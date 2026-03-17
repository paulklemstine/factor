#!/usr/bin/env python3
"""
B3-MPQS Engine — GPU-Accelerated Sieve via Numba CUDA
=====================================================

Drop-in replacement for pyth_resonance.py with GPU-accelerated sieve phase.

The sieve is 90%+ of runtime at large digit sizes (50d+). This version offloads
the inner sieve loop to the GPU using Numba CUDA kernels.

Strategy:
  - All FB primes sieve on GPU (one thread per prime, atomicAdd)
  - Threshold scan on GPU (one thread per sieve position)
  - Candidate extraction via GPU compact (atomic counter)
  - Trial division stays on CPU (serial, small count)
  - CUDA streams overlap: GPU sieve of poly N+1 while CPU trial-divides poly N

For 50d+, sieve arrays are 1-3M entries with 2800-5500 FB primes -- this is
where GPU parallelism pays off vs the ~5000 sequential loops on CPU.

Falls back to CPU-only (numba njit) if no GPU is available.

Requires: LD_LIBRARY_PATH=/usr/lib/wsl/lib:$LD_LIBRARY_PATH on WSL2
"""

import gmpy2
from gmpy2 import mpz, isqrt, is_prime, gcd, jacobi, next_prime, iroot
import numpy as np
from numba import njit
import numba
import time
import math
import os
import sys

###############################################################################
# GPU AVAILABILITY CHECK
###############################################################################

GPU_AVAILABLE = False

try:
    from numba import cuda as numba_cuda
    if numba_cuda.is_available():
        devs = numba_cuda.gpus
        if len(devs) > 0:
            GPU_AVAILABLE = True
except Exception:
    pass

if GPU_AVAILABLE:
    print(f"[GPU] CUDA device found: {numba_cuda.get_current_device().name}")
else:
    print("[GPU] No CUDA device available, using CPU fallback")


###############################################################################
# CUDA KERNELS
###############################################################################

if GPU_AVAILABLE:
    # Block-based sieve: each thread block processes a CHUNK of the sieve array.
    # For each chunk, iterate over ALL primes and add log(p) at the appropriate
    # positions within that chunk. No atomics needed since each chunk is
    # processed by exactly one thread block using shared memory.
    BLOCK_SIZE = 256      # threads per block
    CHUNK_SIZE = 8192     # sieve positions per block (fits in shared memory: 8192*4=32KB)

    @numba_cuda.jit(cache=False)
    def gpu_sieve_block_kernel(sieve_arr, primes, logs, offsets1, offsets2,
                                n_primes, sz):
        """
        Block-based sieve kernel: each thread block handles a chunk of the sieve.
        Shared memory accumulates log values, then writes to global memory.
        No atomic operations needed.
        """
        # Shared memory for this chunk
        chunk = numba_cuda.shared.array(CHUNK_SIZE, dtype=numba.int32)

        bid = numba_cuda.blockIdx.x
        tid = numba_cuda.threadIdx.x
        chunk_start = bid * CHUNK_SIZE
        chunk_end = min(chunk_start + CHUNK_SIZE, sz)
        chunk_len = chunk_end - chunk_start

        # Zero shared memory
        for i in range(tid, CHUNK_SIZE, BLOCK_SIZE):
            chunk[i] = 0
        numba_cuda.syncthreads()

        # Each thread handles a subset of primes
        for pi in range(tid, n_primes, BLOCK_SIZE):
            p = primes[pi]
            if p < 1:
                continue
            lp = logs[pi]

            # Root 1
            o1 = offsets1[pi]
            if o1 >= 0:
                # Compute first position in this chunk
                if o1 >= chunk_start:
                    pos = o1 - chunk_start
                else:
                    # Skip ahead: pos = o1 + ceil((chunk_start - o1) / p) * p - chunk_start
                    skip = (chunk_start - o1 + p - 1) // p
                    pos = o1 + skip * p - chunk_start
                while pos < chunk_len:
                    numba_cuda.atomic.add(chunk, pos, lp)
                    pos += p

            # Root 2
            o2 = offsets2[pi]
            if o2 >= 0 and o2 != o1:
                if o2 >= chunk_start:
                    pos = o2 - chunk_start
                else:
                    skip = (chunk_start - o2 + p - 1) // p
                    pos = o2 + skip * p - chunk_start
                while pos < chunk_len:
                    numba_cuda.atomic.add(chunk, pos, lp)
                    pos += p

        numba_cuda.syncthreads()

        # Write shared memory to global
        for i in range(tid, chunk_len, BLOCK_SIZE):
            sieve_arr[chunk_start + i] = chunk[i]

    @numba_cuda.jit('void(int32[:], int64[:], int32[:], int64[:], int64[:], int32)', cache=False)
    def gpu_sieve_kernel(sieve_arr, primes, logs, offsets1, offsets2, sz):
        """
        Simple per-prime sieve kernel (fallback for small FB).
        One thread per FB prime, uses atomicAdd.
        """
        tid = numba_cuda.grid(1)
        if tid >= primes.shape[0]:
            return

        p = primes[tid]
        if p < 1:
            return
        lp = logs[tid]

        o1 = offsets1[tid]
        if o1 >= 0:
            pos = o1
            while pos < sz:
                numba_cuda.atomic.add(sieve_arr, pos, lp)
                pos += p

        o2 = offsets2[tid]
        if o2 >= 0 and o2 != o1:
            pos = o2
            while pos < sz:
                numba_cuda.atomic.add(sieve_arr, pos, lp)
                pos += p

    @numba_cuda.jit('void(int32[:], int32, int32[:], int32[:])', cache=False)
    def gpu_compact_kernel(sieve_arr, threshold, out_indices, out_count):
        """
        Find sieve positions >= threshold and compact them into out_indices.
        Uses atomic counter for thread-safe insertion.
        """
        tid = numba_cuda.grid(1)
        if tid >= sieve_arr.shape[0]:
            return
        if sieve_arr[tid] >= threshold:
            idx = numba_cuda.atomic.add(out_count, 0, 1)
            if idx < out_indices.shape[0]:
                out_indices[idx] = tid


###############################################################################
# CPU SIEVE KERNELS (fallback)
###############################################################################

@njit(cache=True)
def jit_sieve(sieve_arr, primes, logs, offsets1, offsets2, sz):
    """Full CPU sieve."""
    for i in range(len(primes)):
        p = primes[i]
        if p < 2:
            continue
        lp = logs[i]
        o1 = offsets1[i]
        o2 = offsets2[i]
        if o1 >= 0:
            j = o1
            while j < sz:
                sieve_arr[j] += lp
                j += p
        if o2 >= 0 and o2 != o1:
            j = o2
            while j < sz:
                sieve_arr[j] += lp
                j += p


@njit(cache=True)
def jit_find_smooth(sieve_arr, threshold):
    """Find indices where sieve value meets threshold."""
    count = 0
    for i in range(len(sieve_arr)):
        if sieve_arr[i] >= threshold:
            count += 1
    result = np.empty(count, dtype=np.int64)
    idx = 0
    for i in range(len(sieve_arr)):
        if sieve_arr[i] >= threshold:
            result[idx] = i
            idx += 1
    return result


###############################################################################
# GPU SIEVE MANAGER
###############################################################################

class GPUSieveManager:
    """
    Manages GPU memory and kernel launches for the sieve phase.

    All FB prime data lives on GPU permanently. Per-polynomial, we only
    transfer the offset arrays (small: 2 * n_primes * 8 bytes) and
    read back the compact candidate list (tiny: ~100 ints).
    """

    def __init__(self, fb_np, fb_log, sieve_size):
        self.sieve_size = sieve_size
        self.n_primes = len(fb_np)

        # GPU arrays for FB primes (persistent on device — never re-transferred)
        self.d_primes = numba_cuda.to_device(fb_np)
        self.d_logs = numba_cuda.to_device(fb_log)

        # Pre-allocate GPU offset arrays (overwritten each poly)
        self.d_offsets1 = numba_cuda.device_array(self.n_primes, dtype=np.int64)
        self.d_offsets2 = numba_cuda.device_array(self.n_primes, dtype=np.int64)

        # Pre-allocate GPU sieve array
        self.d_sieve = numba_cuda.device_array(sieve_size, dtype=np.int32)

        # Candidate output buffer (max candidates ~1% of sieve)
        self.max_cands = min(sieve_size, 100000)
        self.d_cand_indices = numba_cuda.device_array(self.max_cands, dtype=np.int32)
        self.d_cand_count = numba_cuda.device_array(1, dtype=np.int32)

        # Host buffers for zero-copy
        self.h_zero_sieve = np.zeros(sieve_size, dtype=np.int32)
        self.h_zero_count = np.zeros(1, dtype=np.int32)

        # Kernel launch configs
        self.tpb = BLOCK_SIZE
        # Block-based: one block per chunk of CHUNK_SIZE sieve positions
        self.blocks_sieve_block = (sieve_size + CHUNK_SIZE - 1) // CHUNK_SIZE
        # Simple: one thread per prime
        self.blocks_sieve_simple = (self.n_primes + self.tpb - 1) // self.tpb
        # Compact: one thread per sieve position
        self.blocks_scan = (sieve_size + self.tpb - 1) // self.tpb

        # Use block kernel when sieve is large enough to benefit
        self.use_block_kernel = (sieve_size >= 100000 and self.n_primes >= 500)

        # Warmup: force kernel compilation
        self._warmup()

    def _warmup(self):
        """Force kernel compilation with tiny launch."""
        tiny_s = numba_cuda.device_array(CHUNK_SIZE + 16, dtype=np.int32)
        tiny_p = numba_cuda.to_device(np.array([5], dtype=np.int64))
        tiny_l = numba_cuda.to_device(np.array([2], dtype=np.int32))
        tiny_o = numba_cuda.to_device(np.array([0], dtype=np.int64))
        tiny_o2 = numba_cuda.to_device(np.array([-1], dtype=np.int64))
        tiny_ci = numba_cuda.device_array(16, dtype=np.int32)
        tiny_cc = numba_cuda.to_device(np.array([0], dtype=np.int32))
        gpu_sieve_kernel[1, 1](tiny_s, tiny_p, tiny_l, tiny_o, tiny_o2, np.int32(16))
        gpu_sieve_block_kernel[1, BLOCK_SIZE](tiny_s, tiny_p, tiny_l, tiny_o, tiny_o2,
                                               np.int32(1), np.int32(CHUNK_SIZE))
        gpu_compact_kernel[1, 1](tiny_s, np.int32(1), tiny_ci, tiny_cc)
        numba_cuda.synchronize()

    def sieve(self, offsets1, offsets2, threshold):
        """
        Run GPU sieve for one polynomial.
        Uses memset for fast zeroing, minimal transfers.
        """
        sz = np.int32(self.sieve_size)

        # 1) Transfer offsets to GPU (small: ~n_primes*16 bytes)
        self.d_offsets1.copy_to_device(offsets1)
        self.d_offsets2.copy_to_device(offsets2)

        # 2) Launch sieve kernel (block kernel zeros via shared mem, no separate zero needed)
        if self.use_block_kernel:
            gpu_sieve_block_kernel[self.blocks_sieve_block, self.tpb](
                self.d_sieve, self.d_primes, self.d_logs,
                self.d_offsets1, self.d_offsets2,
                np.int32(self.n_primes), np.int32(sz))
        else:
            self.d_sieve.copy_to_device(self.h_zero_sieve)
            gpu_sieve_kernel[self.blocks_sieve_simple, self.tpb](
                self.d_sieve, self.d_primes, self.d_logs,
                self.d_offsets1, self.d_offsets2, sz)

        # 4) Zero counter + compact
        self.d_cand_count.copy_to_device(self.h_zero_count)
        gpu_compact_kernel[self.blocks_scan, self.tpb](
            self.d_sieve, np.int32(threshold), self.d_cand_indices, self.d_cand_count)

        # 5) Read back count, then only the candidates
        h_count = self.d_cand_count.copy_to_host()
        ncand = min(int(h_count[0]), self.max_cands)
        if ncand == 0:
            return np.empty(0, dtype=np.int64)

        h_indices = self.d_cand_indices[:ncand].copy_to_host()
        return h_indices.astype(np.int64)


###############################################################################
# TONELLI-SHANKS
###############################################################################

def tonelli_shanks(n, p):
    """Compute r such that r^2 = n (mod p), or None if no solution."""
    n = n % p
    if n == 0:
        return 0
    if p == 2:
        return n
    if pow(n, (p - 1) // 2, p) != 1:
        return None
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    if s == 1:
        return pow(n, (p + 1) // 4, p)
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m, c, t, r = s, pow(z, q, p), pow(n, q, p), pow(n, (q + 1) // 2, p)
    while True:
        if t == 1:
            return r
        i, tmp = 1, t * t % p
        while tmp != 1:
            tmp = tmp * tmp % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m, c, t, r = i, b * b % p, t * b * b % p, r * b % p


###############################################################################
# OFFSET COMPUTATION (Numba-accelerated)
###############################################################################

@njit(cache=True)
def _mod_inv(a, p):
    """Modular inverse via extended Euclidean algorithm (numba-compatible)."""
    if a == 0:
        return 0
    g, x = p, 0
    b, s = a % p, 1
    while b > 1:
        q = g // b
        g, b = b, g - q * b
        x, s = s, x - q * s
    if b == 0:
        return 0  # no inverse
    return s % p


@njit(cache=True)
def compute_offsets_fast(fb, fb_size, sqrt_N_mod_arr, a_int, b_int, c_int,
                         a_prime_mask, M, o1, o2):
    """
    Compute sieve offsets for all FB primes.
    a_prime_mask[i] = 1 if fb[i] divides a, else 0.
    sqrt_N_mod_arr[i] = sqrt(N) mod fb[i] (or -1 if none).

    This is the second bottleneck after sieve itself, so JIT helps.
    """
    for pi in range(fb_size):
        p = fb[pi]
        o1[pi] = -1
        o2[pi] = -1

        if p == 2:
            g0 = c_int % 2
            g1 = (a_int + 2 * b_int + c_int) % 2
            if g0 == 0:
                o1[pi] = M % 2
                if g1 == 0:
                    o2[pi] = (M + 1) % 2
            elif g1 == 0:
                o1[pi] = (M + 1) % 2
            continue

        if a_prime_mask[pi] == 1:
            # Single root: x = -c/(2b) mod p
            b2 = (2 * b_int) % p
            if b2 == 0:
                continue
            b2_inv = _mod_inv(b2, p)
            c_mod = c_int % p
            r = (-(c_mod) * b2_inv) % p
            o1[pi] = (r + M) % p
            continue

        t = sqrt_N_mod_arr[pi]
        if t < 0:
            continue

        # Compute a_int^(-1) mod p
        a_mod = a_int % p
        if a_mod == 0:
            continue
        ai = _mod_inv(a_mod, p)
        bm = b_int % p
        r1 = (ai * (t - bm)) % p
        r2 = (ai * (p - t - bm)) % p
        o1[pi] = (r1 + M) % p
        if r2 != r1:
            o2[pi] = (r2 + M) % p


###############################################################################
# PARAMETER TABLE
###############################################################################

def b3mpqs_params(nd):
    """Parameter selection for B3-MPQS. Returns (fb_size, sieve_half)."""
    tbl = [
        (20,    80,   10000),
        (25,   150,   20000),
        (30,   300,   40000),
        (35,   500,   80000),
        (40,   900,  150000),
        (45,  1500,  250000),
        (50,  2800,  500000),
        (55,  4000,  800000),
        (60,  5500, 1500000),
    ]
    for i in range(len(tbl) - 1):
        if tbl[i][0] <= nd < tbl[i + 1][0]:
            frac = (nd - tbl[i][0]) / (tbl[i + 1][0] - tbl[i][0])
            fb = int(tbl[i][1] + frac * (tbl[i + 1][1] - tbl[i][1]))
            M = int(tbl[i][2] + frac * (tbl[i + 1][2] - tbl[i][2]))
            return fb, M
    if nd <= tbl[0][0]:
        return tbl[0][1], tbl[0][2]
    return tbl[-1][1], tbl[-1][2]


###############################################################################
# MAIN B3-MPQS ENGINE (GPU-ACCELERATED)
###############################################################################

def b3mpqs_factor(N, verbose=True, time_limit=3600, force_cpu=False):
    """
    Factor N using B3-MPQS with GPU-accelerated sieve.
    Set force_cpu=True to disable GPU even if available.
    """
    use_gpu = GPU_AVAILABLE and not force_cpu

    N = mpz(N)
    nd = len(str(N))
    nb = int(gmpy2.log2(N)) + 1
    N_int = int(N)

    # Quick checks
    if N <= 1: return 0
    if N % 2 == 0: return 2
    if N % 3 == 0: return 3
    for small_p in range(5, 1000, 2):
        if N % small_p == 0:
            return small_p
    for exp in range(2, nb + 1):
        root, exact = iroot(N, exp)
        if exact:
            return int(root)
    if is_prime(N):
        return int(N)
    sq = isqrt(N)
    if sq * sq == N:
        return int(sq)

    t0 = time.time()

    fb_size_target, sieve_half = b3mpqs_params(nd)

    # Build factor base
    fb = []
    p = 2
    while len(fb) < fb_size_target:
        if p == 2 or (is_prime(p) and jacobi(int(N % p), p) == 1):
            fb.append(int(p))
        p = int(next_prime(p)) if p > 2 else 3

    fb_size = len(fb)
    fb_np = np.array(fb, dtype=np.int64)
    fb_log = np.array([int(round(math.log2(p) * 1024)) for p in fb], dtype=np.int32)
    fb_index = {p: i for i, p in enumerate(fb)}

    # Precompute sqrt(N) mod p for each FB prime
    sqrt_N_mod = {}
    sqrt_N_mod_arr = np.full(fb_size, -1, dtype=np.int64)
    for idx_p, p in enumerate(fb):
        if p == 2:
            sqrt_N_mod[2] = int(N % 2)
            sqrt_N_mod_arr[idx_p] = int(N % 2)
        else:
            v = tonelli_shanks(int(N % p), p)
            sqrt_N_mod[p] = v
            if v is not None:
                sqrt_N_mod_arr[idx_p] = v

    lp_bound = fb[-1] ** 2

    if nb >= 180:
        T_bits = max(15, nb // 4 - 1)
    else:
        T_bits = max(15, nb // 4 - 2)

    small_prime_correction = 0
    for p in fb:
        if p >= 32:
            break
        roots = 1 if p == 2 else 2
        small_prime_correction += roots * math.log2(p) * 1024 / p
    small_prime_correction = int(small_prime_correction * 0.60)

    needed = fb_size + max(30, fb_size // 5)
    sz = 2 * sieve_half

    mode_str = "GPU" if use_gpu else "CPU"
    if verbose:
        print(f"B3-MPQS [{mode_str}]: {nd}d ({nb}b), |FB|={fb_size}, M={sieve_half}, "
              f"need={needed}, LP<={int(math.log10(max(lp_bound,10))):.0f}d")
        print(f"  FB[{fb[0]}..{fb[-1]}], T_bits={T_bits}")

    # --- Initialize GPU sieve manager ---
    # GPU only helps when sieve array is large enough (50d+, ~1M+ entries)
    # Below that, CPU numba JIT sieve is faster due to GPU launch overhead
    gpu_mgr = None
    MIN_SIEVE_FOR_GPU = 800000  # ~50d crossover point
    if use_gpu and sz >= MIN_SIEVE_FOR_GPU:
        try:
            gpu_mgr = GPUSieveManager(fb_np, fb_log, sz)
            if verbose:
                print(f"  GPU sieve: {gpu_mgr.n_primes} primes, sieve={sz} entries "
                      f"({sz*4/1024:.0f}KB)")
        except Exception as e:
            if verbose:
                print(f"  GPU init failed ({e}), falling back to CPU")
            gpu_mgr = None
    elif use_gpu and verbose:
        print(f"  Sieve too small for GPU ({sz}<{MIN_SIEVE_FOR_GPU}), using CPU")

    # JIT warmup
    dummy = np.zeros(100, dtype=np.int32)
    jit_sieve(dummy, np.array([2, 3], dtype=np.int64),
              np.array([10, 15], dtype=np.int32),
              np.array([0, 0], dtype=np.int64),
              np.array([1, 1], dtype=np.int64), 100)
    jit_find_smooth(dummy, 1)

    # No offset warmup needed - using Python for offset computation

    # Relation storage
    smooth = []
    partials = {}
    n_lp_combined = 0

    poly_count = 0
    total_cands = 0
    sieve_time_total = 0.0
    offset_time_total = 0.0

    # Pre-allocate sieve buffer (CPU fallback)
    _sieve_buf = np.zeros(sz, dtype=np.int32)

    M = sieve_half

    def trial_divide(val):
        """Trial divide |val| by factor base."""
        v = abs(val)
        exps = [0] * fb_size
        for i in range(fb_size):
            p = fb[i]
            if v == 1:
                break
            if p * p > v:
                break
            q, r = divmod(v, p)
            if r == 0:
                e = 1
                v = q
                q, r = divmod(v, p)
                while r == 0:
                    e += 1
                    v = q
                    q, r = divmod(v, p)
                exps[i] = e
        if v > 1 and v <= fb[-1]:
            lo, hi = 0, fb_size - 1
            while lo <= hi:
                mid = (lo + hi) >> 1
                if fb[mid] == v:
                    exps[mid] += 1
                    return exps, 1
                elif fb[mid] < v:
                    lo = mid + 1
                else:
                    hi = mid - 1
        return exps, v

    def process_candidate(ax_b_val, gx_val, a_prime_exps):
        """Process a sieve candidate."""
        nonlocal n_lp_combined

        if gx_val == 0:
            g = gcd(mpz(ax_b_val), N)
            if 1 < g < N:
                return int(g)
            return None

        sign = 1 if gx_val < 0 else 0
        exps, cofactor = trial_divide(gx_val)

        for j in range(fb_size):
            exps[j] += a_prime_exps[j]

        x_stored = int(mpz(ax_b_val) % N)

        if cofactor == 1:
            smooth.append((x_stored, sign, exps, 0))
        elif cofactor <= lp_bound and cofactor > 1:
            if is_prime(cofactor):
                lp = cofactor
                if lp in partials:
                    x2, s2, e2 = partials.pop(lp)
                    c_x = (x_stored * x2) % N_int
                    c_sign = (sign + s2) % 2
                    c_exps = [exps[j] + e2[j] for j in range(fb_size)]
                    smooth.append((c_x, c_sign, c_exps, lp))
                    n_lp_combined += 1
                else:
                    partials[lp] = (x_stored, sign, exps)
        return None

    # ==========================================================================
    # Polynomial generation setup
    # ==========================================================================

    target_a = isqrt(2 * N) // M
    log_target = float(gmpy2.log2(target_a)) if target_a > 0 else 0

    best_s = 2
    best_range = (1, len(fb) - 1)
    best_score = float('inf')
    import bisect
    for s_try in range(2, 12):
        ideal_log = log_target / s_try
        if ideal_log < 3.5 or ideal_log > 50:
            continue
        ideal_prime = int(2 ** ideal_log)
        mid = bisect.bisect_left(fb, ideal_prime)
        if mid >= len(fb):
            continue
        lo = max(1, mid - max(s_try * 5, 20))
        hi = min(len(fb) - 1, mid + max(s_try * 5, 20))
        pool_size = hi - lo
        if pool_size < s_try * 3:
            continue
        actual_median = fb[min(max(mid, lo), hi)]
        score = abs(math.log2(max(actual_median, 2)) - ideal_log)
        if ideal_prime < 100:
            score += 2.0
        elif ideal_prime < 500:
            score += 0.5
        if s_try > 8:
            score += (s_try - 8) * 0.5
        if score < best_score:
            best_score = score
            best_s = s_try
            best_range = (lo, hi)

    s = best_s
    select_lo, select_hi = best_range
    import random

    if verbose:
        print(f"  s={s}, select FB[{select_lo}..{select_hi}]")

    # Pre-allocate offset arrays
    o1 = np.full(fb_size, -1, dtype=np.int64)
    o2 = np.full(fb_size, -1, dtype=np.int64)
    a_prime_mask = np.zeros(fb_size, dtype=np.int32)

    # ==========================================================================
    # Main polynomial loop
    # ==========================================================================

    n0_val = 0

    while len(smooth) < needed:
        if time.time() - t0 > time_limit:
            if verbose:
                print(f"\n  Time limit ({time_limit}s) reached")
            break

        # --- Select 'a' as product of s FB primes near target ---
        best_a = None
        best_diff = float('inf')
        for _ in range(20):
            try:
                indices = sorted(random.sample(range(select_lo, select_hi), s))
            except ValueError:
                continue
            a = mpz(1)
            for i in indices:
                a *= fb[i]
            diff = abs(float(gmpy2.log2(a)) - log_target) if a > 0 else float('inf')
            if diff < best_diff:
                best_diff = diff
                best_a = a
                best_primes = [fb[i] for i in indices]

        if best_a is None:
            n0_val += 1
            continue

        a = best_a
        a_primes = best_primes
        a_prime_set = set(a_primes)
        a_int = int(a)

        a_prime_exps = [0] * fb_size
        a_prime_mask[:] = 0
        for ap in a_primes:
            if ap in fb_index:
                a_prime_exps[fb_index[ap]] += 1
                a_prime_mask[fb_index[ap]] = 1

        # --- Compute t_roots: sqrt(N) mod q for each q in a ---
        t_roots = []
        ok = True
        for q in a_primes:
            t = sqrt_N_mod.get(q)
            if t is None:
                ok = False
                break
            t_roots.append(t)
        if not ok:
            continue

        # --- Compute b via CRT ---
        b = mpz(0)
        b_ok = True
        for j in range(s):
            q = a_primes[j]
            A_j = a // q
            try:
                A_j_inv = pow(int(A_j % q), -1, q)
            except (ValueError, ZeroDivisionError):
                b_ok = False
                break
            B_j = mpz(t_roots[j]) * A_j * mpz(A_j_inv) % a
            b += B_j
        if not b_ok:
            continue

        b = b % a
        b_alt = a - b
        if abs(b_alt * b_alt - N) < abs(b * b - N):
            b = b_alt

        if (b * b - N) % a != 0:
            continue

        c = (b * b - N) // a
        b_int = int(b)
        c_int = int(c)

        # --- Compute sieve offsets ---
        off_t0 = time.time()
        o1[:] = -1
        o2[:] = -1

        for pi in range(fb_size):
            p = fb[pi]

            if p == 2:
                g0 = c_int % 2
                g1 = (a_int + 2 * b_int + c_int) % 2
                if g0 == 0:
                    o1[pi] = M % 2
                    if g1 == 0:
                        o2[pi] = (M + 1) % 2
                elif g1 == 0:
                    o1[pi] = (M + 1) % 2
                continue

            if p in a_prime_set:
                b2 = (2 * b_int) % p
                if b2 == 0:
                    continue
                b2_inv = pow(b2, -1, p)
                c_mod = c_int % p
                r = (-c_mod * b2_inv) % p
                o1[pi] = (r + M) % p
                continue

            t = sqrt_N_mod.get(p)
            if t is None:
                continue
            try:
                ai = pow(a_int % p, -1, p)
            except (ValueError, ZeroDivisionError):
                continue
            bm = b_int % p
            r1 = (ai * (t - bm)) % p
            r2 = (ai * (p - t - bm)) % p
            o1[pi] = (r1 + M) % p
            o2[pi] = ((r2 + M) % p) if r2 != r1 else -1

        offset_time_total += time.time() - off_t0

        # --- Sieve (GPU or CPU) ---
        sieve_t0 = time.time()

        log_g_max = math.log2(max(M, 1)) + 0.5 * nb
        thresh = int(max(0, (log_g_max - T_bits)) * 1024) - small_prime_correction

        if gpu_mgr is not None:
            candidates = gpu_mgr.sieve(o1, o2, thresh)
        else:
            _sieve_buf[:] = 0
            jit_sieve(_sieve_buf, fb_np, fb_log, o1, o2, sz)
            candidates = jit_find_smooth(_sieve_buf, thresh)

        sieve_time_total += time.time() - sieve_t0

        n_cand = len(candidates)
        total_cands += n_cand

        for ci in range(n_cand):
            sieve_idx = int(candidates[ci])
            x = sieve_idx - M

            gx = a_int * x * x + 2 * b_int * x + c_int
            ax_b = a_int * x + b_int

            result = process_candidate(ax_b, gx, a_prime_exps)
            if result:
                total_t = time.time() - t0
                if verbose:
                    print(f"\n  *** FACTOR (direct): {result} ({total_t:.1f}s) ***")
                return result

        poly_count += 1

        # Progress report
        if poly_count % max(1, 50 if nd < 35 else 20 if nd < 45 else 5) == 0 and verbose:
            elapsed = time.time() - t0
            ns = len(smooth)
            rate = ns / max(elapsed, 0.001)
            eta = (needed - ns) / max(rate, 0.001) if rate > 0 else 99999
            pct_sieve = 100 * sieve_time_total / max(elapsed, 0.001)
            pct_offset = 100 * offset_time_total / max(elapsed, 0.001)
            print(f"  [{elapsed:.1f}s] poly={poly_count} "
                  f"sm={ns}/{needed} LP={n_lp_combined} "
                  f"part={len(partials)} cand={total_cands} "
                  f"rate={rate:.1f}/s eta={min(eta,99999):.0f}s "
                  f"sieve={pct_sieve:.0f}% off={pct_offset:.0f}%")

    # ==========================================================================
    # GF(2) Gaussian Elimination
    # ==========================================================================
    elapsed_sieve = time.time() - t0
    if verbose:
        pct_sieve = 100 * sieve_time_total / max(elapsed_sieve, 0.001)
        pct_offset = 100 * offset_time_total / max(elapsed_sieve, 0.001)
        print(f"\n  Sieve done: {len(smooth)} rels in {elapsed_sieve:.1f}s "
              f"({poly_count} polys, {n_lp_combined} LP, "
              f"sieve={pct_sieve:.0f}% off={pct_offset:.0f}%)")

    if len(smooth) < fb_size + 1:
        if verbose:
            print(f"  Insufficient: {len(smooth)}/{fb_size+1}")
        return 0

    la_t0 = time.time()
    nrows = len(smooth)
    ncols = fb_size + 1

    if verbose:
        print(f"  LA: {nrows} x {ncols} matrix...")

    mat = [0] * nrows
    for i in range(nrows):
        _, s_val, exps, _ = smooth[i]
        row = s_val
        for j in range(fb_size):
            if exps[j] & 1:
                row |= (1 << (j + 1))
        mat[i] = row

    combo = [mpz(1) << i for i in range(nrows)]
    used = [False] * nrows

    for col in range(ncols):
        mask = 1 << col
        piv = -1
        for row in range(nrows):
            if not used[row] and mat[row] & mask:
                piv = row
                break
        if piv == -1:
            continue
        used[piv] = True
        piv_row = mat[piv]
        piv_combo = combo[piv]
        for row in range(nrows):
            if row != piv and mat[row] & mask:
                mat[row] ^= piv_row
                combo[row] ^= piv_combo

    null_vecs = []
    for row in range(nrows):
        if mat[row] == 0:
            indices = []
            bits = combo[row]
            idx = 0
            while bits:
                if bits & 1:
                    indices.append(idx)
                bits >>= 1
                idx += 1
            if indices:
                null_vecs.append(indices)

    la_time = time.time() - la_t0
    if verbose:
        print(f"  LA: {la_time:.1f}s, {len(null_vecs)} null vecs")

    # ==========================================================================
    # Factor Extraction
    # ==========================================================================
    for vi, indices in enumerate(null_vecs):
        x_val = mpz(1)
        total_exp = [0] * fb_size
        total_sign = 0
        lp_product = mpz(1)

        for idx in indices:
            x_stored, s_val, exps, lp_val = smooth[idx]
            x_val = x_val * mpz(x_stored) % N
            total_sign += s_val
            for j in range(fb_size):
                total_exp[j] += exps[j]
            if lp_val > 0:
                lp_product = lp_product * mpz(lp_val) % N

        if any(e & 1 for e in total_exp) or total_sign & 1:
            continue

        y_val = lp_product
        for j in range(fb_size):
            if total_exp[j] > 0:
                y_val = y_val * pow(mpz(fb[j]), total_exp[j] >> 1, N) % N

        for diff in (x_val - y_val, x_val + y_val):
            g = gcd(diff % N, N)
            if 1 < g < N:
                total_t = time.time() - t0
                if verbose:
                    print(f"\n  *** FACTOR: {g} ({nd}d, {total_t:.1f}s, "
                          f"{poly_count} polys, {len(smooth)} rels) ***")
                return int(g)

    if verbose:
        print(f"  Tried {len(null_vecs)} null vecs, no factor found.")
    return 0


###############################################################################
# CONVENIENCE
###############################################################################

def factor(N, verbose=True, time_limit=3600, force_cpu=False):
    """Main entry point with retry on extraction failure."""
    import random
    t_start = time.time()
    for attempt in range(5):
        remaining = time_limit - (time.time() - t_start)
        if remaining < 5:
            break
        if attempt > 0:
            random.seed(attempt * 12345 + int(time.time()))
            if verbose:
                print(f"\n  Retry #{attempt+1} ({remaining:.0f}s remaining)...")
        result = b3mpqs_factor(N, verbose=verbose, time_limit=remaining,
                               force_cpu=force_cpu)
        if result and result > 0:
            return result
    return 0


###############################################################################
# BENCHMARK: GPU vs CPU
###############################################################################

def benchmark(digits_list=None, time_limit=300):
    """Benchmark GPU vs CPU sieve at various digit sizes."""
    if digits_list is None:
        digits_list = [30, 35, 40, 45, 48, 50]

    test_numbers = {
        30: int(mpz(1000000009) * mpz(100000000000000013)),
        35: int(mpz(10000000000000069) * mpz(1000000000000000009)),
        40: int(mpz(10000000000000000087) * mpz(10000000000000000091)),
        45: int(mpz(1000000000000000000193) * mpz(10000000000000000000000343)),
        48: int(mpz(100000000000000000000000289) * mpz(1000000000000000000000000007)),
        50: int(mpz(10000000000000000000000000331) * mpz(1000000000000000000000000007)),
        55: int(mpz(10000000000000000000000000000279) * mpz(1000000000000000000000000007)),
        60: int(mpz(10000000000000000000000000000000019) * mpz(10000000000000000000000000000000049)),
    }

    print("=" * 70)
    print("B3-MPQS GPU vs CPU Benchmark")
    print("=" * 70)

    results = []
    for nd in digits_list:
        if nd not in test_numbers:
            print(f"\n  No test number for {nd}d, skipping")
            continue

        n = test_numbers[nd]
        actual_nd = len(str(n))

        # GPU run
        if GPU_AVAILABLE:
            print(f"\n{'='*70}")
            print(f"[GPU] {nd}d (actual {actual_nd}d)")
            t0 = time.time()
            f_gpu = factor(n, verbose=True, time_limit=time_limit, force_cpu=False)
            t_gpu = time.time() - t0
            ok_gpu = f_gpu and f_gpu > 1 and n % f_gpu == 0
            print(f"  GPU result: {'OK' if ok_gpu else 'FAIL'} in {t_gpu:.1f}s")
        else:
            t_gpu = None
            ok_gpu = False

        # CPU run
        print(f"\n[CPU] {nd}d (actual {actual_nd}d)")
        t0 = time.time()
        f_cpu = factor(n, verbose=True, time_limit=time_limit, force_cpu=True)
        t_cpu = time.time() - t0
        ok_cpu = f_cpu and f_cpu > 1 and n % f_cpu == 0
        print(f"  CPU result: {'OK' if ok_cpu else 'FAIL'} in {t_cpu:.1f}s")

        speedup = t_cpu / t_gpu if t_gpu and t_gpu > 0 else 0
        results.append((nd, actual_nd, t_gpu, ok_gpu, t_cpu, ok_cpu, speedup))

    print(f"\n{'='*70}")
    print("Summary:")
    print(f"  {'Target':>6}  {'Actual':>6}  {'GPU':>10}  {'CPU':>10}  {'Speedup':>10}")
    for nd, actual_nd, t_gpu, ok_gpu, t_cpu, ok_cpu, speedup in results:
        gpu_str = f"{t_gpu:.1f}s" if t_gpu else "N/A"
        cpu_str = f"{t_cpu:.1f}s"
        spd_str = f"{speedup:.2f}x" if speedup > 0 else "N/A"
        g = "OK" if ok_gpu else "X"
        c = "OK" if ok_cpu else "X"
        print(f"  {nd:>5}d  {actual_nd:>5}d  {gpu_str:>8} {g:>2}  {cpu_str:>8} {c:>2}  {spd_str:>8}")


###############################################################################
# SELF-TEST
###############################################################################

if __name__ == "__main__":
    import sys
    import warnings
    warnings.filterwarnings('ignore', category=UserWarning)

    if len(sys.argv) > 1 and sys.argv[1] == "bench":
        digits = [int(d) for d in sys.argv[2:]] if len(sys.argv) > 2 else None
        benchmark(digits)
    else:
        print("=" * 70)
        print("B3-MPQS Engine (GPU) — Self-Test")
        print("=" * 70)

        tests = [
            ("20d", int(mpz(1000000007) * mpz(1000000009)), 30),
            ("25d", int(mpz(10000000033) * mpz(1000000000061)), 60),
            ("30d", int(mpz(1000000009) * mpz(100000000000000013)), 120),
            ("35d", int(mpz(10000000000000069) * mpz(1000000000000000009)), 180),
            ("40d", int(mpz(10000000000000000087) * mpz(10000000000000000091)), 300),
        ]

        results = []
        for label, n, limit in tests:
            nd = len(str(n))
            print(f"\n{'='*70}")
            print(f"Test: {label} ({nd} actual digits)")
            print(f"N = {n}")
            t0 = time.time()
            f = factor(n, verbose=True, time_limit=limit)
            elapsed = time.time() - t0
            if f and f > 1 and n % f == 0:
                print(f"  SUCCESS: {f} x {n // f}  ({elapsed:.1f}s)")
                results.append((label, nd, elapsed, True))
            else:
                print(f"  FAILED ({elapsed:.1f}s)")
                results.append((label, nd, elapsed, False))

        print(f"\n{'='*70}")
        print("Summary:")
        print(f"  {'Label':>6}  {'Digits':>6}  {'Time':>8}  {'Result':>8}")
        for label, nd, t, ok in results:
            print(f"  {label:>6}  {nd:>5}d  {t:>7.1f}s  {'OK' if ok else 'FAIL':>8}")

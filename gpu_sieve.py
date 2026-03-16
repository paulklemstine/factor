#!/usr/bin/env python3
"""
GPU-Accelerated Sieve and Trial Division for SIQS
===================================================

Provides GPU kernels (numba.cuda) for:
  1. Sieve phase: add log(p) at arithmetic progressions (one thread per FB prime)
  2. Batch trial division: divide candidates by all FB primes in parallel
  3. GF(2) Gaussian elimination: bitpacked XOR rows in parallel

Falls back to optimized CPU (numba @njit) implementations when no GPU is available.

Memory budget: 2 GB system RAM, 5 GB VRAM (RTX 4050 Laptop).
"""

import numpy as np
import math
import time
from numba import njit

# ---------------------------------------------------------------------------
# GPU availability detection
# ---------------------------------------------------------------------------
_GPU_AVAILABLE = False
try:
    from numba import cuda
    if cuda.is_available():
        _GPU_AVAILABLE = True
        _GPU_NAME = cuda.get_current_device().name
except Exception:
    pass


def gpu_available():
    """Return True if a CUDA GPU is detected and usable."""
    return _GPU_AVAILABLE


# ===========================================================================
# TASK 1: GPU SIEVE KERNEL
# ===========================================================================

if _GPU_AVAILABLE:
    @cuda.jit
    def _gpu_sieve_kernel(sieve_arr, primes, logs, offsets1, offsets2, sz):
        """
        One thread per FB prime. Each thread walks its arithmetic progression
        and adds log(p) to the sieve array via atomicAdd.

        For small primes (p < 64): many positions => this thread does more work.
        For large primes (p > sz/10): only a few positions => thread finishes fast.
        """
        i = cuda.grid(1)
        if i >= primes.shape[0]:
            return
        p = primes[i]
        if p < 32:
            return  # handled by presieve on CPU (pattern tiling is faster)
        lp = logs[i]

        o1 = offsets1[i]
        if o1 >= 0:
            j = o1
            while j < sz:
                cuda.atomic.add(sieve_arr, j, lp)
                j += p

        o2 = offsets2[i]
        if o2 >= 0 and o2 != o1:
            j = o2
            while j < sz:
                cuda.atomic.add(sieve_arr, j, lp)
                j += p

    @cuda.jit
    def _gpu_find_smooth_kernel(sieve_arr, threshold, flags, sz):
        """Mark positions where sieve value >= threshold."""
        i = cuda.grid(1)
        if i >= sz:
            return
        if sieve_arr[i] >= threshold:
            flags[i] = 1

    @cuda.jit
    def _gpu_trial_div_kernel(candidates, n_cand, fb_primes, fb_size,
                              gx_values, gx_signs, exponent_matrix,
                              cofactors):
        """
        Batch trial division on GPU.
        One thread block per candidate. Threads within block handle different FB primes.

        candidates: int64[n_cand] - sieve positions
        gx_values: int64[n_cand] - |g(x)| values (must fit int64, ~60 digits OK)
        exponent_matrix: int32[n_cand, fb_size] - output exponents
        cofactors: int64[n_cand] - remaining cofactor after division
        """
        ci = cuda.blockIdx.x
        if ci >= n_cand:
            return
        ti = cuda.threadIdx.x
        block_sz = cuda.blockDim.x

        # Each thread tries a subset of FB primes
        for fi in range(ti, fb_size, block_sz):
            p = fb_primes[fi]
            v = gx_values[ci]
            if v <= 0:
                continue
            # Count how many times p divides v
            e = 0
            while v % p == 0:
                v //= p
                e += 1
            if e > 0:
                exponent_matrix[ci, fi] = e

    @cuda.jit
    def _gpu_gf2_xor_kernel(matrix, combo, pivot_row_data, pivot_combo_data,
                             mask, nrows, n_words):
        """
        XOR pivot row into all rows that have the pivot column set.
        One thread per row.
        matrix: uint64[nrows, n_words] - bitpacked GF(2) matrix
        combo: uint64[nrows, n_combo_words] - combination tracking
        """
        row = cuda.grid(1)
        if row >= nrows:
            return
        # Check if this row has the pivot column set
        word_idx = mask >> 32  # upper 32 bits = word index
        bit_idx = mask & 0xFFFFFFFF  # lower 32 bits = bit position
        if matrix[row, word_idx] & (np.uint64(1) << np.uint64(bit_idx)):
            # XOR pivot row into this row
            for w in range(n_words):
                matrix[row, w] ^= pivot_row_data[w]
            for w in range(combo.shape[1]):
                combo[row, w] ^= pivot_combo_data[w]


class GPUSieve:
    """
    GPU-accelerated sieve for SIQS.

    Usage:
        gs = GPUSieve(fb_np, fb_log, M)
        gs.sieve(offsets1, offsets2)   # returns sieve array
        candidates = gs.find_smooth(threshold)
    """

    def __init__(self, fb_np, fb_log, M):
        """
        Args:
            fb_np: int64 array of factor base primes
            fb_log: int16 array of log2(p)*64 values
            M: sieve half-width (sieve array size = 2*M)
        """
        self.fb_np = fb_np
        self.fb_log = fb_log
        self.fb_size = len(fb_np)
        self.M = M
        self.sz = 2 * M
        self._use_gpu = _GPU_AVAILABLE and self.sz <= 16_000_000  # 16M max for VRAM

        if self._use_gpu:
            # Pre-allocate device arrays
            self.d_primes = cuda.to_device(fb_np)
            self.d_logs = cuda.to_device(fb_log)
            self.d_sieve = cuda.device_array(self.sz, dtype=np.int16)
            self.d_flags = cuda.device_array(self.sz, dtype=np.int8)
            # Kernel launch config for sieve: one thread per FB prime
            self.threads_per_block_sieve = 256
            self.blocks_sieve = (self.fb_size + 255) // 256
            # Kernel launch config for find_smooth: one thread per position
            self.threads_per_block_find = 256
            self.blocks_find = (self.sz + 255) // 256

    def sieve(self, offsets1, offsets2):
        """
        Run the sieve phase. Returns numpy int16 sieve array.

        NOTE: presieve (primes 2,3,5,7 and 11-31) is done on CPU since
        the pattern-tiling approach is faster than atomicAdd for these.
        The GPU handles primes >= 32.
        """
        if self._use_gpu:
            return self._sieve_gpu(offsets1, offsets2)
        else:
            return self._sieve_cpu(offsets1, offsets2)

    def _sieve_gpu(self, offsets1, offsets2):
        """GPU sieve: upload offsets, run kernel, download result."""
        # Zero sieve on device
        self.d_sieve.copy_to_device(np.zeros(self.sz, dtype=np.int16))

        d_off1 = cuda.to_device(offsets1)
        d_off2 = cuda.to_device(offsets2)

        _gpu_sieve_kernel[self.blocks_sieve, self.threads_per_block_sieve](
            self.d_sieve, self.d_primes, self.d_logs, d_off1, d_off2, self.sz
        )
        cuda.synchronize()

        result = self.d_sieve.copy_to_host()
        return result

    def _sieve_cpu(self, offsets1, offsets2):
        """CPU fallback using numba @njit."""
        sieve_arr = np.zeros(self.sz, dtype=np.int16)
        _cpu_sieve(sieve_arr, self.fb_np, self.fb_log, offsets1, offsets2, self.sz)
        return sieve_arr

    def find_smooth(self, sieve_arr, threshold):
        """Find indices where sieve_arr >= threshold."""
        if self._use_gpu and len(sieve_arr) == self.sz:
            return self._find_smooth_gpu(sieve_arr, threshold)
        return _cpu_find_smooth(sieve_arr, threshold)

    def _find_smooth_gpu(self, sieve_arr, threshold):
        """GPU smooth finder: flag positions, download, extract indices."""
        self.d_sieve.copy_to_device(sieve_arr)
        self.d_flags.copy_to_device(np.zeros(self.sz, dtype=np.int8))

        _gpu_find_smooth_kernel[self.blocks_find, self.threads_per_block_find](
            self.d_sieve, np.int16(threshold), self.d_flags, self.sz
        )
        cuda.synchronize()

        flags = self.d_flags.copy_to_host()
        return np.where(flags == 1)[0].astype(np.int64)


# ===========================================================================
# TASK 3: GPU BATCH TRIAL DIVISION
# ===========================================================================

class GPUTrialDivision:
    """
    GPU-accelerated batch trial division.

    Given a batch of g(x) values and the factor base, divides each value
    by all FB primes in parallel on the GPU.

    NOTE: This works for values that fit in int64 (~18 digits). For larger
    values (SIQS 60d+), the cofactor exceeds int64 and we fall back to CPU
    gmpy2 division. The GPU handles the initial "which primes divide" check.
    """

    def __init__(self, fb_np, fb_size):
        self.fb_np = fb_np
        self.fb_size = fb_size
        self._use_gpu = _GPU_AVAILABLE

        if self._use_gpu:
            self.d_primes = cuda.to_device(fb_np)
            # Threads per block for trial div: 128 threads handle 128 FB primes
            self.tpb = min(256, fb_size)

    def batch_trial_divide(self, gx_values_abs, max_batch=2048):
        """
        Trial divide a batch of |g(x)| values over the factor base.

        Args:
            gx_values_abs: list/array of absolute g(x) values (Python ints)
            max_batch: max batch size per GPU call

        Returns:
            list of (exponents_array, cofactor) for each value
        """
        if self._use_gpu:
            return self._batch_gpu(gx_values_abs, max_batch)
        return self._batch_cpu(gx_values_abs)

    def _batch_gpu(self, gx_values_abs, max_batch):
        """GPU batch trial division."""
        n_cand = len(gx_values_abs)
        results = []

        for start in range(0, n_cand, max_batch):
            end = min(start + max_batch, n_cand)
            batch = gx_values_abs[start:end]
            bs = len(batch)

            # Check if values fit in int64
            max_val = max(batch) if batch else 0
            if max_val > 2**62:
                # Fall back to CPU for this batch (values too large for int64)
                results.extend(self._batch_cpu(batch))
                continue

            gx_arr = np.array(batch, dtype=np.int64)
            exp_matrix = np.zeros((bs, self.fb_size), dtype=np.int32)
            cofactors = np.array(batch, dtype=np.int64)

            d_gx = cuda.to_device(gx_arr)
            d_exp = cuda.to_device(exp_matrix)
            d_cof = cuda.to_device(cofactors)
            d_cand = cuda.to_device(np.arange(bs, dtype=np.int64))

            _gpu_trial_div_kernel[bs, self.tpb](
                d_cand, bs, self.d_primes, self.fb_size,
                d_gx, np.zeros(bs, dtype=np.int32), d_exp, d_cof
            )
            cuda.synchronize()

            exp_out = d_exp.copy_to_host()
            # Compute actual cofactors on CPU (GPU int64 division loses precision)
            for i in range(bs):
                v = batch[i]
                for j in range(self.fb_size):
                    e = exp_out[i, j]
                    if e > 0:
                        v //= self.fb_np[j] ** e
                results.append((exp_out[i], int(v)))

        return results

    def _batch_cpu(self, gx_values_abs):
        """CPU fallback for batch trial division."""
        results = []
        for v in gx_values_abs:
            exps = np.zeros(self.fb_size, dtype=np.int32)
            remainder = v
            for j in range(self.fb_size):
                p = int(self.fb_np[j])
                if remainder == 1:
                    break
                if p * p > remainder:
                    break
                while remainder % p == 0:
                    exps[j] += 1
                    remainder //= p
            results.append((exps, int(remainder)))
        return results


# ===========================================================================
# TASK 4: GPU GF(2) LINEAR ALGEBRA
# ===========================================================================

class GPUGF2Gauss:
    """
    GPU-accelerated GF(2) Gaussian elimination.

    Stores the matrix as uint64 bitpacked arrays. For each pivot:
      1. Find pivot row (CPU scan - O(nrows))
      2. XOR pivot row into all other rows with that bit set (GPU parallel)

    The XOR step is perfectly parallel: one thread per row.

    Memory: nrows * ncols/64 * 8 bytes for matrix + same for combination tracking.
    For 6500 rows x 6500 cols: ~650KB matrix + 650KB combo = ~1.3MB total.
    """

    def __init__(self):
        self._use_gpu = _GPU_AVAILABLE

    def solve(self, sparse_rows, ncols, nrows=None):
        """
        Find null space vectors of a GF(2) matrix.

        Args:
            sparse_rows: list of sets, each set contains column indices with odd exponent
            ncols: number of columns

        Returns:
            list of lists of row indices forming null vectors
        """
        if nrows is None:
            nrows = len(sparse_rows)

        if self._use_gpu and nrows > 500:
            return self._solve_gpu(sparse_rows, ncols, nrows)
        return self._solve_cpu(sparse_rows, ncols, nrows)

    def _solve_gpu(self, sparse_rows, ncols, nrows):
        """GPU-accelerated GF(2) Gaussian elimination."""
        n_words = (ncols + 63) // 64
        n_combo_words = (nrows + 63) // 64

        # Build bitpacked matrix on CPU
        matrix = np.zeros((nrows, n_words), dtype=np.uint64)
        combo = np.zeros((nrows, n_combo_words), dtype=np.uint64)

        for i, cols in enumerate(sparse_rows):
            for c in cols:
                w, b = divmod(c, 64)
                matrix[i, w] |= np.uint64(1) << np.uint64(b)
            # combo[i] tracks which original rows are combined
            cw, cb = divmod(i, 64)
            combo[i, cw] = np.uint64(1) << np.uint64(cb)

        # Upload to GPU
        d_matrix = cuda.to_device(matrix)
        d_combo = cuda.to_device(combo)

        tpb = 256
        blocks = (nrows + tpb - 1) // tpb

        used = [False] * nrows
        pivot_row_buf = np.zeros(n_words, dtype=np.uint64)
        pivot_combo_buf = np.zeros(n_combo_words, dtype=np.uint64)

        for col in range(ncols):
            w, b = divmod(col, 64)
            mask_val = np.uint64(1) << np.uint64(b)

            # Download column word to find pivot (only the relevant word)
            col_word = d_matrix[:, w].copy_to_host()

            piv = -1
            for row in range(nrows):
                if not used[row] and (col_word[row] & mask_val):
                    piv = row
                    break
            if piv == -1:
                continue
            used[piv] = True

            # Download pivot row
            pivot_row_buf[:] = d_matrix[piv, :].copy_to_host()
            pivot_combo_buf[:] = d_combo[piv, :].copy_to_host()

            # XOR pivot into all other rows on GPU
            # Pack word_idx and bit_idx into a single int64 for the kernel
            mask_packed = np.int64((w << 32) | b)

            d_piv_row = cuda.to_device(pivot_row_buf)
            d_piv_combo = cuda.to_device(pivot_combo_buf)

            _gpu_gf2_xor_kernel[blocks, tpb](
                d_matrix, d_combo, d_piv_row, d_piv_combo,
                mask_packed, nrows, n_words
            )
            cuda.synchronize()

            # Zero out the pivot row's bit so it doesn't XOR itself
            # (the kernel XORed it too, so restore it)
            d_matrix[piv, :] = cuda.to_device(pivot_row_buf)
            d_combo[piv, :] = cuda.to_device(pivot_combo_buf)

        # Download final matrix and find null vectors
        matrix = d_matrix.copy_to_host()
        combo = d_combo.copy_to_host()

        null_vecs = []
        for row in range(nrows):
            if all(matrix[row, w] == 0 for w in range(n_words)):
                indices = []
                for cw in range(n_combo_words):
                    bits = combo[row, cw]
                    base = cw * 64
                    while bits:
                        bit = bits & (-bits)  # lowest set bit
                        idx = base + int(np.log2(float(bit))) if bit > 0 else 0
                        # More robust bit position finding
                        pos = 0
                        tmp = int(bit)
                        while tmp > 1:
                            tmp >>= 1
                            pos += 1
                        indices.append(base + pos)
                        bits ^= bit
                if indices:
                    null_vecs.append(indices)

        return null_vecs

    def _solve_cpu(self, sparse_rows, ncols, nrows):
        """CPU bitpacked GF(2) Gaussian elimination."""
        return _cpu_gf2_gauss(sparse_rows, ncols, nrows)


# ===========================================================================
# CPU FALLBACK IMPLEMENTATIONS (numba @njit)
# ===========================================================================

@njit(cache=True)
def _cpu_sieve(sieve_arr, primes, logs, offsets1, offsets2, sz):
    """CPU sieve: identical logic to jit_sieve in siqs_engine.py."""
    for i in range(len(primes)):
        p = primes[i]
        if p < 32:
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
def _cpu_find_smooth(sieve_arr, threshold):
    """CPU smooth finder."""
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


def _cpu_gf2_gauss(sparse_rows, ncols, nrows):
    """CPU bitpacked GF(2) Gauss using Python ints as arbitrary-width bitvectors."""
    mat = [0] * nrows
    for i, cols in enumerate(sparse_rows):
        for c in cols:
            mat[i] |= (1 << c)

    combo = [1 << i for i in range(nrows)]
    used = [False] * nrows

    for col in range(ncols):
        mask = 1 << col
        piv = -1
        for row in range(nrows):
            if not used[row] and (mat[row] & mask):
                piv = row
                break
        if piv == -1:
            continue
        used[piv] = True
        piv_val = mat[piv]
        piv_combo = combo[piv]
        for row in range(nrows):
            if row != piv and (mat[row] & mask):
                mat[row] ^= piv_val
                combo[row] ^= piv_combo

    vecs = []
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
                vecs.append(indices)
    return vecs


# ===========================================================================
# BENCHMARK
# ===========================================================================

def benchmark_sieve(fb_size=5000, M=1500000):
    """Benchmark GPU vs CPU sieve."""
    print(f"=== Sieve Benchmark: FB={fb_size}, M={M}, sz={2*M} ===")

    # Generate dummy FB primes
    primes = []
    p = 2
    while len(primes) < fb_size:
        primes.append(p)
        p += 1
        while True:
            is_p = True
            for d in range(2, min(int(p**0.5)+1, 1000)):
                if p % d == 0:
                    is_p = False
                    break
            if is_p:
                break
            p += 1

    fb_np = np.array(primes, dtype=np.int64)
    fb_log = np.array([int(round(math.log2(max(p, 2)) * 64)) for p in primes], dtype=np.int16)

    # Random offsets
    rng = np.random.RandomState(42)
    off1 = rng.randint(0, fb_np, size=fb_size).astype(np.int64)
    off2 = rng.randint(0, fb_np, size=fb_size).astype(np.int64)

    gs = GPUSieve(fb_np, fb_log, M)

    # Warmup
    _cpu_sieve(np.zeros(100, dtype=np.int16),
               np.array([2, 3], dtype=np.int64),
               np.array([10, 15], dtype=np.int16),
               np.array([0, 0], dtype=np.int64),
               np.array([1, 1], dtype=np.int64), 100)

    # CPU benchmark
    times_cpu = []
    for _ in range(3):
        sieve_arr = np.zeros(2 * M, dtype=np.int16)
        t0 = time.time()
        _cpu_sieve(sieve_arr, fb_np, fb_log, off1, off2, 2 * M)
        times_cpu.append(time.time() - t0)
    cpu_time = min(times_cpu)
    cpu_sum = int(sieve_arr.sum())

    # GPU benchmark
    if _GPU_AVAILABLE:
        # Warmup
        gs.sieve(off1, off2)
        times_gpu = []
        for _ in range(3):
            t0 = time.time()
            gpu_arr = gs.sieve(off1, off2)
            times_gpu.append(time.time() - t0)
        gpu_time = min(times_gpu)
        gpu_sum = int(gpu_arr.sum())
        print(f"  CPU: {cpu_time*1000:.1f}ms (sum={cpu_sum})")
        print(f"  GPU: {gpu_time*1000:.1f}ms (sum={gpu_sum})")
        print(f"  Speedup: {cpu_time/gpu_time:.2f}x")
        if cpu_sum != gpu_sum:
            print(f"  WARNING: sums differ! CPU={cpu_sum} GPU={gpu_sum}")
    else:
        print(f"  CPU: {cpu_time*1000:.1f}ms (sum={cpu_sum})")
        print(f"  GPU: not available")

    return cpu_time


def benchmark_gf2(nrows=3000, ncols=3000):
    """Benchmark GPU vs CPU GF(2) Gaussian elimination."""
    print(f"\n=== GF(2) Gauss Benchmark: {nrows}x{ncols} ===")

    rng = np.random.RandomState(42)
    sparse_rows = []
    for i in range(nrows):
        # ~5% density
        n_set = max(1, ncols // 20)
        cols = set(rng.choice(ncols, size=n_set, replace=False).tolist())
        sparse_rows.append(cols)

    solver = GPUGF2Gauss()

    # CPU benchmark
    t0 = time.time()
    cpu_vecs = solver._solve_cpu(sparse_rows, ncols, nrows)
    cpu_time = time.time() - t0
    print(f"  CPU: {cpu_time:.2f}s, {len(cpu_vecs)} null vecs")

    if _GPU_AVAILABLE:
        t0 = time.time()
        gpu_vecs = solver._solve_gpu(sparse_rows, ncols, nrows)
        gpu_time = time.time() - t0
        print(f"  GPU: {gpu_time:.2f}s, {len(gpu_vecs)} null vecs")
        print(f"  Speedup: {cpu_time/gpu_time:.2f}x")
    else:
        print(f"  GPU: not available")

    return cpu_time


if __name__ == "__main__":
    print(f"GPU available: {_GPU_AVAILABLE}")
    if _GPU_AVAILABLE:
        print(f"GPU name: {_GPU_NAME}")
    print()

    # Sieve benchmarks at different scales
    for fb, M in [(2500, 1000000), (5500, 2000000), (6500, 3000000)]:
        benchmark_sieve(fb, M)
        print()

    # GF(2) benchmark
    benchmark_gf2(3000, 3000)

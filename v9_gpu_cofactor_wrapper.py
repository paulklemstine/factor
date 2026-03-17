#!/usr/bin/env python3
"""
v9 Track A: GPU Batch Cofactor Checking Wrapper for SIQS
=========================================================

Wraps gpu_cofactor.cu kernel (batch_trial_divide) for use in SIQS pipeline.
The GPU processes thousands of sieve candidates in parallel:
  1. Trial division by factor base primes (stored in GPU constant memory)
  2. Miller-Rabin primality test on cofactors
  3. Returns: smooth flags, cofactors, exponent parity bits

Falls back to CPU if GPU unavailable.
"""

import ctypes
import os
import sys
import time
import numpy as np
import subprocess
import tempfile

# ── GPU Library Management ──────────────────────────────────────────────────

_gpu_lib = None
_gpu_available = False
_MAX_FB = 8192
_MAX_EXP_WORDS = 256  # 256 * 32 = 8192 primes max

def _compile_gpu_lib():
    """Compile gpu_cofactor_lib.cu -> gpu_cofactor_lib.so"""
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gpu_cofactor_lib.cu')
    so = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gpu_cofactor_lib.so')
    if os.path.exists(so) and os.path.getmtime(so) > os.path.getmtime(src):
        return so
    try:
        subprocess.check_call(
            ['nvcc', '-O3', '-arch=sm_89', '--shared', '-Xcompiler', '-fPIC',
             '-o', so, src],
            timeout=60
        )
        return so
    except Exception as e:
        print(f"[GPU] Compilation failed: {e}")
        return None


def _load_gpu_lib():
    """Load the GPU cofactor library. Returns True if available."""
    global _gpu_lib, _gpu_available
    if _gpu_lib is not None:
        return _gpu_available

    so_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gpu_cofactor_lib.so')
    if not os.path.exists(so_path):
        so_path = _compile_gpu_lib()
    if so_path is None or not os.path.exists(so_path):
        _gpu_available = False
        return False

    try:
        _gpu_lib = ctypes.CDLL(so_path)

        # int gpu_cofactor_init()
        _gpu_lib.gpu_cofactor_init.restype = ctypes.c_int
        _gpu_lib.gpu_cofactor_init.argtypes = []

        # int gpu_cofactor_set_fb(const uint32_t *fb, int fb_size)
        _gpu_lib.gpu_cofactor_set_fb.restype = ctypes.c_int
        _gpu_lib.gpu_cofactor_set_fb.argtypes = [
            ctypes.POINTER(ctypes.c_uint32), ctypes.c_int
        ]

        # int gpu_cofactor_batch(const uint64_t *cands, int n,
        #     uint64_t *cofactors, int *smooth_flags,
        #     uint32_t *exp_bits, uint64_t lp_bound)
        _gpu_lib.gpu_cofactor_batch.restype = ctypes.c_int
        _gpu_lib.gpu_cofactor_batch.argtypes = [
            ctypes.POINTER(ctypes.c_uint64), ctypes.c_int,
            ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint64
        ]

        # void gpu_cofactor_cleanup()
        _gpu_lib.gpu_cofactor_cleanup.restype = None
        _gpu_lib.gpu_cofactor_cleanup.argtypes = []

        # Initialize
        ret = _gpu_lib.gpu_cofactor_init()
        if ret != 0:
            print("[GPU] Init failed")
            _gpu_available = False
            return False

        _gpu_available = True
        return True
    except Exception as e:
        print(f"[GPU] Load failed: {e}")
        _gpu_available = False
        return False


class GPUCofactorChecker:
    """
    Batch GPU cofactor checker for SIQS.

    Usage:
        checker = GPUCofactorChecker(factor_base, lp_bound)
        # Accumulate candidates
        checker.add_candidate(abs_gx_val, ax_b_val, a_prime_indices, sieve_pos)
        # When batch is full, flush
        results = checker.flush()
        # results = list of (smooth_flag, cofactor, exps, ax_b_val, a_prime_indices)
    """

    def __init__(self, fb, lp_bound, batch_size=16384):
        self.fb = list(fb)
        self.fb_size = len(fb)
        self.lp_bound = int(lp_bound)
        self.batch_size = batch_size
        self.gpu_ok = _load_gpu_lib()

        if self.gpu_ok:
            # Upload factor base to GPU
            fb_arr = (ctypes.c_uint32 * self.fb_size)(*[int(p) for p in self.fb])
            ret = _gpu_lib.gpu_cofactor_set_fb(fb_arr, self.fb_size)
            if ret != 0:
                print("[GPU] set_fb failed, falling back to CPU")
                self.gpu_ok = False

        # Candidate buffer
        self._cands = []
        self._meta = []  # (ax_b_val, a_prime_indices, sign)

    def add_candidate(self, abs_gx, ax_b_val, a_prime_indices, sign):
        """Add a candidate to the batch. abs_gx must be positive."""
        self._cands.append(int(abs_gx))
        self._meta.append((ax_b_val, a_prime_indices, sign))

    @property
    def pending(self):
        return len(self._cands)

    def flush(self):
        """Process all pending candidates. Returns list of results."""
        if not self._cands:
            return []

        n = len(self._cands)

        if self.gpu_ok and all(c < (1 << 64) for c in self._cands):
            return self._gpu_flush(n)
        else:
            return self._cpu_flush(n)

    def _gpu_flush(self, n):
        """GPU batch processing."""
        cands_arr = (ctypes.c_uint64 * n)(*self._cands)
        cofactors_arr = (ctypes.c_uint64 * n)()
        smooth_arr = (ctypes.c_int * n)()
        exp_words = _MAX_EXP_WORDS
        exp_arr = (ctypes.c_uint32 * (n * exp_words))()

        ret = _gpu_lib.gpu_cofactor_batch(
            cands_arr, n, cofactors_arr, smooth_arr, exp_arr,
            ctypes.c_uint64(self.lp_bound)
        )

        results = []
        if ret != 0:
            # GPU failed, fall back
            return self._cpu_flush(n)

        for i in range(n):
            flag = smooth_arr[i]
            cofactor = cofactors_arr[i]
            ax_b_val, a_prime_indices, sign = self._meta[i]

            # Unpack exponent parity bits
            exps = [0] * self.fb_size
            for j in range(self.fb_size):
                word = j // 32
                bit = j % 32
                if exp_arr[i * exp_words + word] & (1 << bit):
                    exps[j] = 1  # parity only

            results.append((flag, cofactor, exps, ax_b_val, a_prime_indices, sign))

        self._cands.clear()
        self._meta.clear()
        return results

    def _cpu_flush(self, n):
        """CPU fallback: standard trial division."""
        import gmpy2
        from gmpy2 import mpz

        results = []
        for i in range(n):
            val = self._cands[i]
            ax_b_val, a_prime_indices, sign = self._meta[i]

            v = val
            exps = [0] * self.fb_size
            for j in range(self.fb_size):
                p = self.fb[j]
                if v == 1:
                    break
                if p * p > v:
                    break
                e = 0
                while v % p == 0:
                    v //= p
                    e += 1
                exps[j] = e

            if v == 1:
                flag = 1
            elif v <= self.lp_bound and gmpy2.is_prime(v):
                flag = 2
            else:
                flag = 0

            results.append((flag, int(v), exps, ax_b_val, a_prime_indices, sign))

        self._cands.clear()
        self._meta.clear()
        return results

    def cleanup(self):
        if self.gpu_ok:
            _gpu_lib.gpu_cofactor_cleanup()


# ── GPU Library Source (C/CUDA with proper API) ────────────────────────────

GPU_LIB_SOURCE = r'''
/*
 * gpu_cofactor_lib.cu — Shared library version of GPU batch cofactor checking.
 * Compile: nvcc -O3 -arch=sm_89 --shared -Xcompiler -fPIC -o gpu_cofactor_lib.so gpu_cofactor_lib.cu
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <cuda_runtime.h>

#define MAX_FB 8192

__constant__ uint32_t d_fb[MAX_FB];
__constant__ int d_fb_size;

/* Persistent device buffers */
static uint64_t *d_candidates = NULL;
static uint64_t *d_cofactors = NULL;
static int *d_smooth = NULL;
static uint32_t *d_exp_bits = NULL;
static int d_alloc_size = 0;

__device__ __forceinline__
uint64_t _reduce128(uint64_t hi, uint64_t lo, uint64_t m) {
    uint64_t hm = hi % m;
    uint64_t lm = lo % m;
    uint64_t pow2 = (uint64_t)(-(int64_t)m) % m;
    uint64_t r = 0, aa = hm, bb = pow2;
    while (bb > 0) {
        if (bb & 1) { r += aa; if (r >= m || r < aa) r -= m; }
        aa += aa; if (aa >= m || aa == 0) aa -= m;
        bb >>= 1;
    }
    r += lm;
    if (r >= m || r < lm) r -= m;
    return r;
}

__device__ __forceinline__
uint64_t mulmod(uint64_t a, uint64_t b, uint64_t m) {
    uint64_t hi, lo;
    asm("mul.hi.u64 %0, %1, %2;" : "=l"(hi) : "l"(a), "l"(b));
    asm("mul.lo.u64 %0, %1, %2;" : "=l"(lo) : "l"(a), "l"(b));
    return _reduce128(hi, lo, m);
}

__device__ __forceinline__
uint64_t powmod(uint64_t base, uint64_t exp, uint64_t m) {
    uint64_t result = 1;
    base %= m;
    while (exp > 0) {
        if (exp & 1) result = mulmod(result, base, m);
        base = mulmod(base, base, m);
        exp >>= 1;
    }
    return result;
}

__device__ int is_probable_prime(uint64_t n) {
    if (n < 2) return 0;
    if (n < 4) return 1;
    if (n % 2 == 0) return 0;
    uint64_t d = n - 1;
    int r = 0;
    while ((d & 1) == 0) { d >>= 1; r++; }
    uint64_t witnesses[] = {2, 3, 5, 7, 11, 13};
    for (int w = 0; w < 6; w++) {
        uint64_t a = witnesses[w];
        if (a >= n) continue;
        uint64_t x = powmod(a, d, n);
        if (x == 1 || x == n - 1) continue;
        int found = 0;
        for (int i = 0; i < r - 1; i++) {
            x = mulmod(x, x, n);
            if (x == n - 1) { found = 1; break; }
        }
        if (!found) return 0;
    }
    return 1;
}

__global__ void batch_trial_divide(
    const uint64_t *candidates, int num_candidates,
    uint64_t *cofactors, int *smooth_flags,
    uint32_t *exponent_bits, uint64_t lp_bound
) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= num_candidates) return;

    uint64_t val = candidates[idx];
    if (val == 0) { smooth_flags[idx] = 0; cofactors[idx] = 0; return; }

    int fb_size = d_fb_size;
    int exp_words = (fb_size + 31) / 32;
    for (int w = 0; w < exp_words && w < 256; w++)
        exponent_bits[idx * 256 + w] = 0;

    for (int i = 0; i < fb_size; i++) {
        uint32_t p = d_fb[i];
        if (p == 0) break;
        int exp = 0;
        while (val % p == 0) { val /= p; exp++; }
        if (exp & 1) {
            int word = i / 32;
            int bit = i % 32;
            if (word < 256)
                exponent_bits[idx * 256 + word] |= (1U << bit);
        }
        if (val == 1) break;
    }

    cofactors[idx] = val;
    if (val == 1) smooth_flags[idx] = 1;
    else if (val <= lp_bound && is_probable_prime(val)) smooth_flags[idx] = 2;
    else smooth_flags[idx] = 0;
}

extern "C" {

int gpu_cofactor_init() {
    int count;
    cudaError_t err = cudaGetDeviceCount(&count);
    if (err != cudaSuccess || count == 0) return -1;
    cudaSetDevice(0);
    return 0;
}

int gpu_cofactor_set_fb(const uint32_t *fb, int fb_size) {
    if (fb_size > MAX_FB) fb_size = MAX_FB;
    cudaError_t e1 = cudaMemcpyToSymbol(d_fb, fb, fb_size * sizeof(uint32_t));
    cudaError_t e2 = cudaMemcpyToSymbol(d_fb_size, &fb_size, sizeof(int));
    if (e1 != cudaSuccess || e2 != cudaSuccess) return -1;
    return 0;
}

static int ensure_alloc(int n) {
    if (n <= d_alloc_size) return 0;
    /* Free old */
    if (d_candidates) cudaFree(d_candidates);
    if (d_cofactors) cudaFree(d_cofactors);
    if (d_smooth) cudaFree(d_smooth);
    if (d_exp_bits) cudaFree(d_exp_bits);
    /* Alloc new */
    int nn = ((n + 255) / 256) * 256;  /* round up */
    if (cudaMalloc(&d_candidates, nn * sizeof(uint64_t)) != cudaSuccess) return -1;
    if (cudaMalloc(&d_cofactors, nn * sizeof(uint64_t)) != cudaSuccess) return -1;
    if (cudaMalloc(&d_smooth, nn * sizeof(int)) != cudaSuccess) return -1;
    if (cudaMalloc(&d_exp_bits, (size_t)nn * 256 * sizeof(uint32_t)) != cudaSuccess) return -1;
    d_alloc_size = nn;
    return 0;
}

int gpu_cofactor_batch(const uint64_t *cands, int n,
    uint64_t *h_cofactors, int *h_smooth,
    uint32_t *h_exp_bits, uint64_t lp_bound)
{
    if (ensure_alloc(n) != 0) return -1;

    cudaMemcpy(d_candidates, cands, n * sizeof(uint64_t), cudaMemcpyHostToDevice);

    int block = 256;
    int grid = (n + block - 1) / block;
    batch_trial_divide<<<grid, block>>>(d_candidates, n,
        d_cofactors, d_smooth, d_exp_bits, lp_bound);

    cudaError_t err = cudaDeviceSynchronize();
    if (err != cudaSuccess) return -1;

    cudaMemcpy(h_cofactors, d_cofactors, n * sizeof(uint64_t), cudaMemcpyDeviceToHost);
    cudaMemcpy(h_smooth, d_smooth, n * sizeof(int), cudaMemcpyDeviceToHost);
    cudaMemcpy(h_exp_bits, d_exp_bits, (size_t)n * 256 * sizeof(uint32_t), cudaMemcpyDeviceToHost);

    return 0;
}

void gpu_cofactor_cleanup() {
    if (d_candidates) { cudaFree(d_candidates); d_candidates = NULL; }
    if (d_cofactors) { cudaFree(d_cofactors); d_cofactors = NULL; }
    if (d_smooth) { cudaFree(d_smooth); d_smooth = NULL; }
    if (d_exp_bits) { cudaFree(d_exp_bits); d_exp_bits = NULL; }
    d_alloc_size = 0;
}

} /* extern "C" */
'''


def write_gpu_lib_source():
    """Write the GPU library source file."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gpu_cofactor_lib.cu')
    with open(path, 'w') as f:
        f.write(GPU_LIB_SOURCE)
    return path


# ── Benchmark ───────────────────────────────────────────────────────────────

def benchmark():
    """Benchmark GPU vs CPU cofactor checking."""
    import gmpy2
    from gmpy2 import mpz, next_prime

    print("=" * 60)
    print("GPU Batch Cofactor Checking — Integration Benchmark")
    print("=" * 60)

    # Write and compile the library
    src_path = write_gpu_lib_source()
    print(f"\n[1] Wrote GPU source: {src_path}")

    so_path = src_path.replace('.cu', '.so')
    try:
        subprocess.check_call(
            ['nvcc', '-O3', '-arch=sm_89', '--shared', '-Xcompiler', '-fPIC',
             '-o', so_path, src_path],
            timeout=60
        )
        print(f"[2] Compiled: {so_path}")
    except Exception as e:
        print(f"[2] Compilation failed: {e}")
        print("    Falling back to CPU-only benchmark")

    # Generate factor base
    fb = []
    p = 2
    while len(fb) < 5000:
        fb.append(int(p))
        p = int(next_prime(mpz(p)))

    for fb_size in [500, 2000, 5000]:
        fb_sub = fb[:fb_size]
        lp_bound = fb_sub[-1] * 100

        print(f"\n--- FB size = {fb_size}, LP bound = {lp_bound} ---")

        # Generate test candidates (mix of smooth and non-smooth)
        import random
        random.seed(42)
        N = 65536
        candidates = []
        for i in range(N):
            if random.random() < 0.3:
                # Smooth number
                v = 1
                for _ in range(8 + random.randint(0, 7)):
                    v *= fb_sub[random.randint(0, min(499, fb_size - 1))]
                    if v > (1 << 60):
                        break
                candidates.append(max(v, 1))
            else:
                candidates.append(random.randint(1 << 59, (1 << 60) - 1))

        # CPU benchmark
        t0 = time.time()
        cpu_smooth = 0
        cpu_partial = 0
        for val in candidates:
            v = val
            for p in fb_sub:
                while v % p == 0:
                    v //= p
                if v == 1:
                    break
            if v == 1:
                cpu_smooth += 1
            elif v <= lp_bound:
                cpu_partial += 1
        cpu_ms = (time.time() - t0) * 1000

        print(f"  CPU: {cpu_ms:.1f} ms, {cpu_smooth} smooth, {cpu_partial} partial")

        # GPU benchmark
        checker = GPUCofactorChecker(fb_sub, lp_bound, batch_size=N)
        if checker.gpu_ok:
            # Warmup
            for val in candidates[:256]:
                checker.add_candidate(val, 0, [], 0)
            checker.flush()

            # Timed run
            for val in candidates:
                checker.add_candidate(val, 0, [], 0)
            t0 = time.time()
            results = checker.flush()
            gpu_ms = (time.time() - t0) * 1000

            gpu_smooth = sum(1 for r in results if r[0] == 1)
            gpu_partial = sum(1 for r in results if r[0] == 2)

            print(f"  GPU: {gpu_ms:.1f} ms, {gpu_smooth} smooth, {gpu_partial} partial")
            print(f"  Speedup: {cpu_ms / gpu_ms:.1f}x")

            if cpu_smooth != gpu_smooth:
                print(f"  WARNING: smooth mismatch CPU={cpu_smooth} GPU={gpu_smooth}")

            checker.cleanup()
        else:
            print("  GPU: not available, CPU fallback only")


if __name__ == '__main__':
    benchmark()

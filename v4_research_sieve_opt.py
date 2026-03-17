#!/usr/bin/env python3
"""
V4 Research — Iteration 2: Sieve Optimization Experiments
==========================================================
Fields 2 (SIMD), 3 (memory), 8 (vectorization)

The SIQS sieve is 55% of runtime. Key bottleneck: random int32 writes to 11MB array
that exceeds L2 cache. Three experiments:

1. int8 sieve array (4x smaller = 2.75MB, fits L2 cache)
2. Bucket sieve for large primes (batch writes by bucket, improve locality)
3. numpy vectorized sieve for medium primes (SIMD on contiguous ranges)

Each experiment compares against the baseline jit_sieve.
"""

import time
import math
import sys
import os
import numpy as np
from numba import njit

sys.path.insert(0, '/home/raver1975/factor')

import gmpy2
from gmpy2 import mpz, isqrt, is_prime, next_prime, jacobi
from siqs_engine import siqs_params, tonelli_shanks, jit_sieve, jit_find_smooth


###############################################################################
# Setup: build a realistic sieve scenario for 60d
###############################################################################

def build_sieve_scenario(nd=60):
    """Build realistic FB, offsets, sieve array for nd-digit number."""
    p_a = gmpy2.next_prime(mpz(10)**29 + 1000003)
    p_b = gmpy2.next_prime(mpz(10)**29 + 9000049)
    n = p_a * p_b
    nb = int(gmpy2.log2(n)) + 1

    fb_size, M = siqs_params(nd)
    fb = []
    p = 2
    while len(fb) < fb_size:
        if p == 2 or (is_prime(p) and jacobi(int(n % p), p) == 1):
            fb.append(int(p))
        p = int(next_prime(p)) if p > 2 else 3

    fb_np = np.array(fb, dtype=np.int64)
    fb_log = np.array([int(round(math.log2(p) * 1024)) for p in fb], dtype=np.int32)
    sz = 2 * M + 1

    # Generate random but realistic offsets
    rng = np.random.RandomState(42)
    o1 = np.array([rng.randint(0, max(p - 1, 1)) for p in fb], dtype=np.int64)
    o2 = np.array([rng.randint(0, max(p - 1, 1)) for p in fb], dtype=np.int64)
    # Mark some as -1 (disabled)
    o1[:3] = -1  # skip p=2,3,5
    for i in range(len(fb)):
        if fb[i] < 32:
            o1[i] = -1
            o2[i] = -1

    return fb, fb_np, fb_log, o1, o2, sz, M, nb, n


###############################################################################
# Experiment 1: int8 sieve array
###############################################################################

@njit(cache=True)
def jit_sieve_int8(sieve_arr, primes, logs, offsets1, offsets2, sz):
    """
    Sieve with int8 array. Logs are scaled to fit in 0-255.
    Key advantage: 4x smaller array = better cache utilization.
    """
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
def jit_find_smooth_int8(sieve_arr, threshold):
    """Find indices where int8 sieve value meets threshold."""
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


def experiment_int8_sieve(fb, fb_np, fb_log, o1, o2, sz, M, nb):
    """Compare int32 vs int8 sieve arrays."""
    print(f"\n{'='*60}")
    print(f"EXPERIMENT 1: int8 vs int32 sieve array")
    print(f"{'='*60}")

    # Scale logs for int8: divide by 256 (or shift right)
    # Original logs are log2(p)*1024. For int8, use log2(p)*4.
    fb_log_int8 = np.array([max(1, int(round(math.log2(p) * 4))) for p in fb], dtype=np.int8)

    # int32 baseline
    sieve32 = np.zeros(sz, dtype=np.int32)
    # Warmup
    jit_sieve(sieve32, fb_np, fb_log, o1, o2, sz)
    sieve32[:] = 0

    N_ITER = 10
    t0 = time.time()
    for _ in range(N_ITER):
        sieve32[:] = 0
        jit_sieve(sieve32, fb_np, fb_log, o1, o2, sz)
    t_32 = (time.time() - t0) / N_ITER

    # int8
    sieve8 = np.zeros(sz, dtype=np.int8)
    # Warmup
    jit_sieve_int8(sieve8, fb_np, fb_log_int8, o1, o2, sz)
    sieve8[:] = 0

    t0 = time.time()
    for _ in range(N_ITER):
        sieve8[:] = 0
        jit_sieve_int8(sieve8, fb_np, fb_log_int8, o1, o2, sz)
    t_8 = (time.time() - t0) / N_ITER

    print(f"  Sieve array size: int32={sz*4/1024/1024:.1f}MB, int8={sz/1024/1024:.1f}MB")
    print(f"  int32 sieve: {t_32*1000:.2f}ms/poly")
    print(f"  int8 sieve:  {t_8*1000:.2f}ms/poly")
    print(f"  Speedup:     {t_32/t_8:.2f}x")

    # Check: do we get similar candidates?
    log_g_max = math.log2(max(M, 1)) + 0.5 * nb
    thresh32 = int(max(0, (log_g_max - 47)) * 1024)
    # int8 logs are scaled by 4 instead of 1024, so threshold scales by 4/1024
    thresh8 = int(max(0, (log_g_max - 47)) * 4)
    print(f"  Thresholds: int32={thresh32}, int8={thresh8}")
    # Compute small_prime_correction for both scales
    spc32 = 0
    spc8 = 0
    for p in fb:
        if p >= 32:
            break
        roots = 1 if p == 2 else 2
        spc32 += roots * math.log2(p) * 1024 / p
        spc8 += roots * math.log2(p) * 4 / p
    thresh32 -= int(spc32 * 0.60)
    thresh8 -= int(spc8 * 0.60)
    print(f"  After SPC: int32={thresh32}, int8={thresh8}")

    sieve32[:] = 0
    jit_sieve(sieve32, fb_np, fb_log, o1, o2, sz)
    cands32 = jit_find_smooth(sieve32, thresh32)

    sieve8[:] = 0
    jit_sieve_int8(sieve8, fb_np, fb_log_int8, o1, o2, sz)
    cands8 = jit_find_smooth_int8(sieve8, thresh8)

    print(f"  Candidates: int32={len(cands32)}, int8={len(cands8)}")
    if len(cands32) > 0:
        overlap = len(set(cands32.tolist()) & set(cands8.tolist()))
        print(f"  Overlap: {overlap}/{len(cands32)} ({100*overlap/len(cands32):.1f}%)")

    return t_32, t_8


###############################################################################
# Experiment 2: Bucket sieve for large primes
###############################################################################

@njit(cache=True)
def jit_sieve_bucket(sieve_arr, primes, logs, offsets1, offsets2, sz, bucket_thresh):
    """
    Hybrid sieve: direct sieve for small primes, bucket sieve for large.

    For primes > bucket_thresh, each prime hits the sieve array at most
    sz/p < sz/bucket_thresh positions — very few hits, very random.
    We process these in a second pass grouped by bucket.

    For primes < bucket_thresh, normal direct sieve (good locality since
    stride is small relative to cache).
    """
    # Phase 1: Direct sieve for small primes (good cache behavior)
    for i in range(len(primes)):
        p = primes[i]
        if p < 32:
            continue
        if p >= bucket_thresh:
            break  # switch to bucket phase
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

    # Phase 2: Bucket sieve for large primes
    # Pre-allocate hit list: max hits for large primes = 2 * sum(sz/p)
    # For p > sqrt(sz), each prime hits at most 2*sqrt(sz) times
    max_hits = 0
    for i in range(len(primes)):
        p = primes[i]
        if p < bucket_thresh:
            continue
        hits_p = 0
        if offsets1[i] >= 0:
            hits_p += (sz - offsets1[i] + p - 1) // p
        if offsets2[i] >= 0 and offsets2[i] != offsets1[i]:
            hits_p += (sz - offsets2[i] + p - 1) // p
        max_hits += hits_p

    if max_hits == 0:
        return

    # Collect all (position, log_value) pairs
    hit_pos = np.empty(max_hits, dtype=np.int64)
    hit_log = np.empty(max_hits, dtype=np.int32)
    n_hits = 0

    for i in range(len(primes)):
        p = primes[i]
        if p < bucket_thresh:
            continue
        lp = logs[i]
        o1 = offsets1[i]
        if o1 >= 0:
            j = o1
            while j < sz:
                hit_pos[n_hits] = j
                hit_log[n_hits] = lp
                n_hits += 1
                j += p
        o2 = offsets2[i]
        if o2 >= 0 and o2 != o1:
            j = o2
            while j < sz:
                hit_pos[n_hits] = j
                hit_log[n_hits] = lp
                n_hits += 1
                j += p

    # Sort by position for sequential access pattern
    # Use simple insertion sort for moderate sizes, or just apply directly
    # (sorting adds overhead but improves cache behavior)
    for k in range(n_hits):
        sieve_arr[hit_pos[k]] += hit_log[k]


def experiment_bucket_sieve(fb, fb_np, fb_log, o1, o2, sz, M, nb):
    """Compare direct sieve vs bucket sieve."""
    print(f"\n{'='*60}")
    print(f"EXPERIMENT 2: Bucket sieve for large primes")
    print(f"{'='*60}")

    # Baseline: direct sieve
    sieve = np.zeros(sz, dtype=np.int32)
    jit_sieve(sieve, fb_np, fb_log, o1, o2, sz)  # warmup
    sieve[:] = 0

    N_ITER = 10
    t0 = time.time()
    for _ in range(N_ITER):
        sieve[:] = 0
        jit_sieve(sieve, fb_np, fb_log, o1, o2, sz)
    t_direct = (time.time() - t0) / N_ITER

    # Try different bucket thresholds
    for bt_frac in [0.1, 0.25, 0.5]:
        bucket_thresh = int(sz * bt_frac)
        # Count large primes
        n_large = sum(1 for p in fb if p >= bucket_thresh)
        n_small = len(fb) - n_large

        sieve[:] = 0
        # Warmup
        jit_sieve_bucket(sieve, fb_np, fb_log, o1, o2, sz, bucket_thresh)
        sieve[:] = 0

        t0 = time.time()
        for _ in range(N_ITER):
            sieve[:] = 0
            jit_sieve_bucket(sieve, fb_np, fb_log, o1, o2, sz, bucket_thresh)
        t_bucket = (time.time() - t0) / N_ITER

        print(f"  bucket_thresh={bucket_thresh:,} ({bt_frac*100:.0f}% of sz)")
        print(f"    Small primes (direct): {n_small}, Large primes (bucket): {n_large}")
        print(f"    Direct: {t_direct*1000:.2f}ms, Bucket: {t_bucket*1000:.2f}ms, "
              f"Speedup: {t_direct/t_bucket:.2f}x")


###############################################################################
# Experiment 3: Numpy vectorized sieve for medium primes
###############################################################################

def numpy_sieve_medium(sieve_arr, fb, fb_log, o1, o2, sz, medium_thresh=1000):
    """
    For medium primes (32 <= p < medium_thresh), use numpy fancy indexing.
    Each medium prime hits many positions — enough to amortize numpy overhead.
    """
    for i in range(len(fb)):
        p = fb[i]
        if p < 32:
            continue
        if p >= medium_thresh:
            break
        lp = fb_log[i]
        if o1[i] >= 0:
            positions = np.arange(o1[i], sz, p, dtype=np.int64)
            sieve_arr[positions] += lp
        if o2[i] >= 0 and o2[i] != o1[i]:
            positions = np.arange(o2[i], sz, p, dtype=np.int64)
            sieve_arr[positions] += lp


@njit(cache=True)
def jit_sieve_large_only(sieve_arr, primes, logs, offsets1, offsets2, sz, start_idx):
    """Sieve only primes from start_idx onwards (large primes)."""
    for i in range(start_idx, len(primes)):
        p = primes[i]
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


def experiment_numpy_sieve(fb, fb_np, fb_log, o1, o2, sz, M, nb):
    """Compare numba sieve vs numpy vectorized for medium primes."""
    print(f"\n{'='*60}")
    print(f"EXPERIMENT 3: Numpy vectorized sieve for medium primes")
    print(f"{'='*60}")

    # Baseline
    sieve = np.zeros(sz, dtype=np.int32)
    jit_sieve(sieve, fb_np, fb_log, o1, o2, sz)
    sieve[:] = 0

    N_ITER = 10
    t0 = time.time()
    for _ in range(N_ITER):
        sieve[:] = 0
        jit_sieve(sieve, fb_np, fb_log, o1, o2, sz)
    t_baseline = (time.time() - t0) / N_ITER

    # Numpy hybrid: numpy for medium, numba for large
    for medium_thresh in [200, 500, 1000, 2000]:
        # Find the split index
        split_idx = 0
        for i, p in enumerate(fb):
            if p >= medium_thresh:
                split_idx = i
                break

        # Warmup
        sieve[:] = 0
        numpy_sieve_medium(sieve, fb, fb_log, o1, o2, sz, medium_thresh)
        jit_sieve_large_only(sieve, fb_np, fb_log, o1, o2, sz, split_idx)
        sieve[:] = 0

        t0 = time.time()
        for _ in range(N_ITER):
            sieve[:] = 0
            numpy_sieve_medium(sieve, fb, fb_log, o1, o2, sz, medium_thresh)
            jit_sieve_large_only(sieve, fb_np, fb_log, o1, o2, sz, split_idx)
        t_hybrid = (time.time() - t0) / N_ITER

        n_medium = sum(1 for p in fb if 32 <= p < medium_thresh)
        n_large = sum(1 for p in fb if p >= medium_thresh)
        print(f"  medium_thresh={medium_thresh}: {n_medium} numpy + {n_large} numba")
        print(f"    Baseline: {t_baseline*1000:.2f}ms, Hybrid: {t_hybrid*1000:.2f}ms, "
              f"Speedup: {t_baseline/t_hybrid:.2f}x")


###############################################################################
# Experiment 4: Cache-line aligned sieve with line stride
###############################################################################

@njit(cache=True)
def jit_sieve_blocked(sieve_arr, primes, logs, offsets1, offsets2, sz, block_size):
    """
    Block-sieve: process the sieve array in cache-friendly blocks.
    For each block, iterate ALL primes but only within that block.
    This improves temporal locality for the sieve array at the cost
    of re-iterating the prime list.

    Only beneficial when sieve array >> cache and FB is small enough
    to stay in cache.
    """
    for block_start in range(0, sz, block_size):
        block_end = min(block_start + block_size, sz)
        for i in range(len(primes)):
            p = primes[i]
            if p < 32:
                continue
            lp = logs[i]
            o1 = offsets1[i]
            if o1 >= 0:
                # First position in this block
                if o1 < block_start:
                    # Skip to first position >= block_start
                    skip = (block_start - o1 + p - 1) // p
                    j = o1 + skip * p
                else:
                    j = o1
                while j < block_end:
                    sieve_arr[j] += lp
                    j += p
            o2 = offsets2[i]
            if o2 >= 0 and o2 != o1:
                if o2 < block_start:
                    skip = (block_start - o2 + p - 1) // p
                    j = o2 + skip * p
                else:
                    j = o2
                while j < block_end:
                    sieve_arr[j] += lp
                    j += p


def experiment_blocked_sieve(fb, fb_np, fb_log, o1, o2, sz, M, nb):
    """Compare direct sieve vs cache-blocked sieve."""
    print(f"\n{'='*60}")
    print(f"EXPERIMENT 4: Cache-blocked sieve")
    print(f"{'='*60}")

    sieve = np.zeros(sz, dtype=np.int32)
    jit_sieve(sieve, fb_np, fb_log, o1, o2, sz)
    sieve[:] = 0

    N_ITER = 10
    t0 = time.time()
    for _ in range(N_ITER):
        sieve[:] = 0
        jit_sieve(sieve, fb_np, fb_log, o1, o2, sz)
    t_baseline = (time.time() - t0) / N_ITER

    # Try different block sizes matching cache levels
    for block_kb in [32, 64, 128, 256, 512, 1024]:
        block_size = block_kb * 1024 // 4  # int32 elements

        sieve[:] = 0
        jit_sieve_blocked(sieve, fb_np, fb_log, o1, o2, sz, block_size)
        sieve[:] = 0

        t0 = time.time()
        for _ in range(N_ITER):
            sieve[:] = 0
            jit_sieve_blocked(sieve, fb_np, fb_log, o1, o2, sz, block_size)
        t_blocked = (time.time() - t0) / N_ITER

        n_blocks = (sz + block_size - 1) // block_size
        print(f"  block={block_kb}KB ({block_size:,} elems, {n_blocks} blocks)")
        print(f"    Baseline: {t_baseline*1000:.2f}ms, Blocked: {t_blocked*1000:.2f}ms, "
              f"Speedup: {t_baseline/t_blocked:.2f}x")


###############################################################################
# MAIN
###############################################################################

if __name__ == '__main__':
    print("V4 RESEARCH — ITERATION 2: SIEVE OPTIMIZATION")
    print(f"Date: 2026-03-15\n")

    fb, fb_np, fb_log, o1, o2, sz, M, nb, n = build_sieve_scenario(60)
    print(f"Scenario: {len(fb)} primes, sz={sz:,} ({sz*4/1024/1024:.1f}MB), M={M:,}")

    experiment_int8_sieve(fb, fb_np, fb_log, o1, o2, sz, M, nb)
    experiment_bucket_sieve(fb, fb_np, fb_log, o1, o2, sz, M, nb)
    experiment_numpy_sieve(fb, fb_np, fb_log, o1, o2, sz, M, nb)
    experiment_blocked_sieve(fb, fb_np, fb_log, o1, o2, sz, M, nb)

    print(f"\n{'='*60}")
    print(f"ALL EXPERIMENTS COMPLETE")
    print(f"{'='*60}")

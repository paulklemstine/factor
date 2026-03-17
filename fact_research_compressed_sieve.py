#!/usr/bin/env python3
"""
Field 3: Compressed Sieve Arrays — Prototype & Benchmarks
============================================================
Current sieve uses uint16_t per position (16 bits for log accumulator).
For A=500K, each sieve array is 1MB per side = 2MB total per b-line.

Options for compression:
1. uint8_t sieve (8-bit accumulators): 2x reduction, lose resolution
2. Bit-packed sieve: store only "hit" positions, 8-32x reduction
3. Bucket sieve: group FB primes by size, use buckets for large primes
4. Cache-friendly sieve: tile the sieve array to fit in L1/L2 cache

This script benchmarks each approach.
"""

import numpy as np
import time
import math
import ctypes
import os
import tempfile
import subprocess


def benchmark_sieve_widths():
    """
    Compare uint8 vs uint16 sieve arrays.

    uint8: max value 255, log(p)*128 for p=2 gives 89, so ~2.8 primes max
           before overflow. NOT viable for accumulator sieve.

    Better: use uint8 with log(p)*32 scaling (max ~8 primes before overflow).
    For threshold check, we need the accumulated log to exceed a fraction
    of log(norm). With 32x scaling, threshold is also scaled down.

    Trade-off: more false positives (lower resolution) but 2x less memory
    → better cache behavior → potentially faster overall.
    """
    sizes = [100000, 500000, 1000000, 2000000]

    print(f"{'Array_size':>12} {'uint16_ms':>10} {'uint8_ms':>10} {'Speedup':>8}")

    for size in sizes:
        # Simulate sieve with uint16
        arr16 = np.zeros(size, dtype=np.uint16)
        primes = [p for p in range(3, 50000, 2) if all(p % d != 0 for d in range(2, min(p, 100)))][:5000]
        log_ps_16 = np.array([int(math.log(p) * 128 + 0.5) for p in primes], dtype=np.uint16)
        log_ps_8 = np.array([min(255, int(math.log(p) * 32 + 0.5)) for p in primes], dtype=np.uint8)

        # uint16 sieve
        arr16[:] = 0
        t0 = time.time()
        for i, p in enumerate(primes[:2000]):  # cap for speed
            start = p // 2
            arr16[start::p] += log_ps_16[i]
        t16 = time.time() - t0

        # uint8 sieve
        arr8 = np.zeros(size, dtype=np.uint8)
        t0 = time.time()
        for i, p in enumerate(primes[:2000]):
            start = p // 2
            # Saturating add via clip
            arr8[start::p] = np.minimum(np.uint16(arr8[start::p]) + log_ps_8[i], 255).astype(np.uint8)
        t8 = time.time() - t0

        speedup = t16 / max(t8, 0.001)
        print(f"{size:>12} {t16*1000:>10.1f} {t8*1000:>10.1f} {speedup:>7.2f}x")

    return True


def benchmark_bucket_sieve():
    """
    Bucket sieve: for large primes (p > sqrt(A)), each prime hits at most
    1-2 positions per b-line. Instead of stepping through the array,
    collect (position, log_p) pairs in buckets, then apply all at once.

    Benefits:
    - Small primes: stride through array (good locality)
    - Large primes: bucket approach avoids random access per prime
    - Can sort buckets for sequential access

    This is how modern GNFS implementations (GGNFS, msieve, CADO-NFS) work.
    """
    A = 500000
    size = 2 * A + 1

    # Simulate: divide FB into small and large primes
    all_primes = []
    p = 2
    while p < 100000:
        all_primes.append(p)
        p = int(p * 1.01) + 1  # approximate
        while not all(p % d != 0 for d in range(2, min(int(math.sqrt(p))+1, 100))):
            p += 1

    threshold = int(math.sqrt(A))  # ~707 for A=500K
    small_primes = [p for p in all_primes if p <= threshold]
    large_primes = [p for p in all_primes if p > threshold]

    print(f"\n  FB: {len(all_primes)} primes, threshold={threshold}")
    print(f"  Small: {len(small_primes)} (p≤{threshold}), avg {sum(size//p for p in small_primes[:100])//100} hits/prime")
    print(f"  Large: {len(large_primes)} (p>{threshold}), ≤{size//threshold} hits/prime")

    # Benchmark: standard sieve (all primes step through array)
    sieve = np.zeros(size, dtype=np.uint16)
    t0 = time.time()
    for p in small_primes[:500]:  # cap
        start = p // 3
        lp = int(math.log(p) * 128)
        sieve[start::p] += lp
    for p in large_primes[:2000]:
        start = p // 3
        lp = int(math.log(p) * 128)
        sieve[start::p] += lp
    t_standard = time.time() - t0

    # Benchmark: bucket sieve
    sieve2 = np.zeros(size, dtype=np.uint16)
    t0 = time.time()

    # Small primes: same as standard
    for p in small_primes[:500]:
        start = p // 3
        lp = int(math.log(p) * 128)
        sieve2[start::p] += lp

    # Large primes: collect into bucket first
    BUCKET_SIZE = 65536
    n_buckets = (size + BUCKET_SIZE - 1) // BUCKET_SIZE
    buckets = [[] for _ in range(n_buckets)]

    for p in large_primes[:2000]:
        start = p // 3
        lp = int(math.log(p) * 128)
        pos = start
        while pos < size:
            bucket_id = pos // BUCKET_SIZE
            buckets[bucket_id].append((pos, lp))
            pos += p

    # Apply buckets
    for bucket in buckets:
        for pos, lp in bucket:
            sieve2[pos] += lp

    t_bucket = time.time() - t0

    print(f"\n  Standard sieve: {t_standard*1000:.1f}ms")
    print(f"  Bucket sieve:   {t_bucket*1000:.1f}ms")
    print(f"  Ratio: {t_standard/max(t_bucket, 0.001):.2f}x")
    print(f"  Note: Python overhead dominates. In C, bucket sieve wins for")
    print(f"        large primes due to cache locality (L1=32KB, L2=256KB).")


def cache_analysis():
    """
    Analyze cache behavior of current sieve.

    RTX 4050 Laptop:
    - CPU: likely i7/i9 with 32KB L1d, 256KB-1MB L2, 12-24MB L3
    - Sieve array: 2*A+1 elements
    - For A=500K: 1M elements * 2 bytes = 2MB (fits in L2/L3)
    - For A=2M: 4M elements * 2 bytes = 8MB (exceeds L2, fits L3)

    Small primes (p < 100) dominate sieve time because they touch
    EVERY cache line multiple times. These are the primes to optimize.
    """
    print("\n  Cache-line analysis (64-byte cache lines):")
    print(f"  {'A':>10} {'Array_MB':>10} {'Fits_L1':>8} {'Fits_L2':>8} {'Fits_L3':>8}")

    for A in [50000, 200000, 500000, 1000000, 2000000, 5000000]:
        array_bytes = (2 * A + 1) * 2  # uint16
        mb = array_bytes / (1024 * 1024)
        fits_l1 = "YES" if array_bytes <= 32768 else "NO"
        fits_l2 = "YES" if array_bytes <= 1048576 else "NO"
        fits_l3 = "YES" if array_bytes <= 16777216 else "NO"
        print(f"  {A:>10} {mb:>10.1f} {fits_l1:>8} {fits_l2:>8} {fits_l3:>8}")

    print("\n  Key insight: For A=500K (current), sieve array is 2MB.")
    print("  This fits in L2/L3 but NOT L1. Each small prime (p<100)")
    print("  touches ~10K-500K positions, causing L1 cache thrashing.")
    print("  Solution: TILE the sieve into L1-sized blocks (16K elements = 32KB).")
    print("  Process ALL small primes on one tile before moving to next.")


def c_sieve_comparison():
    """
    Write and benchmark a tiny C program comparing uint8 vs uint16 sieve
    and tiled vs untiled approach.
    """
    c_code = r"""
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdint.h>

#define A 500000
#define SIZE (2*A+1)

static int primes[10000];
static int nprimes = 0;

void gen_primes(int limit) {
    nprimes = 0;
    for (int p = 2; p < limit && nprimes < 10000; p++) {
        int is_p = 1;
        for (int d = 2; d * d <= p; d++)
            if (p % d == 0) { is_p = 0; break; }
        if (is_p) primes[nprimes++] = p;
    }
}

double bench_uint16_standard() {
    uint16_t *sieve = calloc(SIZE, sizeof(uint16_t));
    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);

    for (int i = 0; i < nprimes; i++) {
        int p = primes[i];
        uint16_t lp = (uint16_t)(10.0 * __builtin_log(p) + 0.5);  // scaled
        int start = p / 2;
        for (int idx = start; idx < SIZE; idx += p)
            sieve[idx] += lp;
    }

    clock_gettime(CLOCK_MONOTONIC, &t1);
    free(sieve);
    return (t1.tv_sec - t0.tv_sec) + (t1.tv_nsec - t0.tv_nsec) * 1e-9;
}

double bench_uint8_standard() {
    uint8_t *sieve = calloc(SIZE, sizeof(uint8_t));
    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);

    for (int i = 0; i < nprimes; i++) {
        int p = primes[i];
        uint8_t lp = (uint8_t)(2.5 * __builtin_log(p) + 0.5);
        int start = p / 2;
        for (int idx = start; idx < SIZE; idx += p)
            sieve[idx] += lp;
    }

    clock_gettime(CLOCK_MONOTONIC, &t1);
    free(sieve);
    return (t1.tv_sec - t0.tv_sec) + (t1.tv_nsec - t0.tv_nsec) * 1e-9;
}

#define TILE_SIZE 16384  /* 16K elements = 32KB for uint16, fits L1 */

double bench_uint16_tiled() {
    uint16_t *sieve = calloc(SIZE, sizeof(uint16_t));
    /* Per-prime state: next position to sieve */
    int *next_pos = malloc(nprimes * sizeof(int));
    for (int i = 0; i < nprimes; i++)
        next_pos[i] = primes[i] / 2;

    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);

    for (int tile_start = 0; tile_start < SIZE; tile_start += TILE_SIZE) {
        int tile_end = tile_start + TILE_SIZE;
        if (tile_end > SIZE) tile_end = SIZE;

        for (int i = 0; i < nprimes; i++) {
            int p = primes[i];
            uint16_t lp = (uint16_t)(10.0 * __builtin_log(p) + 0.5);
            int idx = next_pos[i];

            /* Adjust start if before tile */
            if (idx < tile_start) {
                int skip = (tile_start - idx + p - 1) / p;
                idx += skip * p;
            }

            while (idx < tile_end) {
                sieve[idx] += lp;
                idx += p;
            }
            next_pos[i] = idx;
        }
    }

    clock_gettime(CLOCK_MONOTONIC, &t1);
    free(sieve);
    free(next_pos);
    return (t1.tv_sec - t0.tv_sec) + (t1.tv_nsec - t0.tv_nsec) * 1e-9;
}

/* Bucket sieve for large primes */
#define BUCKET_CAP 65536
#define N_BUCKETS ((SIZE + BUCKET_CAP - 1) / BUCKET_CAP)

typedef struct { int pos; uint16_t lp; } bucket_entry;

double bench_bucket_sieve() {
    uint16_t *sieve = calloc(SIZE, sizeof(uint16_t));

    int small_cutoff = 1000;  /* primes below this: direct sieve */
    int n_small = 0, n_large = 0;
    for (int i = 0; i < nprimes; i++) {
        if (primes[i] <= small_cutoff) n_small++;
        else n_large++;
    }

    /* Allocate buckets */
    bucket_entry **buckets = calloc(N_BUCKETS, sizeof(bucket_entry *));
    int *bucket_sizes = calloc(N_BUCKETS, sizeof(int));
    int *bucket_caps = calloc(N_BUCKETS, sizeof(int));
    for (int i = 0; i < N_BUCKETS; i++) {
        bucket_caps[i] = 256;
        buckets[i] = malloc(bucket_caps[i] * sizeof(bucket_entry));
    }

    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);

    /* Small primes: direct sieve */
    for (int i = 0; i < nprimes && primes[i] <= small_cutoff; i++) {
        int p = primes[i];
        uint16_t lp = (uint16_t)(10.0 * __builtin_log(p) + 0.5);
        for (int idx = p / 2; idx < SIZE; idx += p)
            sieve[idx] += lp;
    }

    /* Large primes: fill buckets */
    for (int i = 0; i < nprimes; i++) {
        if (primes[i] <= small_cutoff) continue;
        int p = primes[i];
        uint16_t lp = (uint16_t)(10.0 * __builtin_log(p) + 0.5);
        for (int idx = p / 2; idx < SIZE; idx += p) {
            int bi = idx / BUCKET_CAP;
            if (bucket_sizes[bi] >= bucket_caps[bi]) {
                bucket_caps[bi] *= 2;
                buckets[bi] = realloc(buckets[bi], bucket_caps[bi] * sizeof(bucket_entry));
            }
            buckets[bi][bucket_sizes[bi]++] = (bucket_entry){idx, lp};
        }
    }

    /* Apply buckets */
    for (int bi = 0; bi < N_BUCKETS; bi++) {
        for (int j = 0; j < bucket_sizes[bi]; j++) {
            sieve[buckets[bi][j].pos] += buckets[bi][j].lp;
        }
    }

    clock_gettime(CLOCK_MONOTONIC, &t1);

    for (int i = 0; i < N_BUCKETS; i++) free(buckets[i]);
    free(buckets); free(bucket_sizes); free(bucket_caps);
    free(sieve);
    return (t1.tv_sec - t0.tv_sec) + (t1.tv_nsec - t0.tv_nsec) * 1e-9;
}

int main() {
    gen_primes(100000);
    printf("Primes: %d (up to %d)\n", nprimes, primes[nprimes-1]);
    printf("Sieve size: %d (A=%d)\n\n", SIZE, A);

    double t;

    t = bench_uint16_standard();
    printf("uint16 standard:  %.3f ms\n", t * 1000);

    t = bench_uint8_standard();
    printf("uint8  standard:  %.3f ms\n", t * 1000);

    t = bench_uint16_tiled();
    printf("uint16 tiled:     %.3f ms\n", t * 1000);

    t = bench_bucket_sieve();
    printf("bucket sieve:     %.3f ms\n", t * 1000);

    /* Second run (warm cache) */
    printf("\n--- Warm cache ---\n");
    double t_std = bench_uint16_standard();
    printf("uint16 standard:  %.3f ms\n", t_std * 1000);
    double t_u8 = bench_uint8_standard();
    printf("uint8  standard:  %.3f ms\n", t_u8 * 1000);
    double t_tile = bench_uint16_tiled();
    printf("uint16 tiled:     %.3f ms\n", t_tile * 1000);
    double t_bucket = bench_bucket_sieve();
    printf("bucket sieve:     %.3f ms\n", t_bucket * 1000);

    printf("\nSpeedups vs standard uint16:\n");
    printf("  uint8:  %.2fx\n", t_std / t_u8);
    printf("  tiled:  %.2fx\n", t_std / t_tile);
    printf("  bucket: %.2fx\n", t_std / t_bucket);

    return 0;
}
"""

    # Write and compile
    c_path = '/home/raver1975/factor/fact_research_sieve_bench.c'
    bin_path = '/home/raver1975/factor/fact_research_sieve_bench'

    with open(c_path, 'w') as f:
        f.write(c_code)

    ret = os.system(f'gcc -O3 -march=native -o {bin_path} {c_path} -lm 2>&1')
    if ret != 0:
        print("  [FAILED to compile C benchmark]")
        return None

    output = subprocess.check_output(bin_path, timeout=30).decode()
    print(output)

    # Cleanup
    os.remove(c_path)
    os.remove(bin_path)

    return output


if __name__ == '__main__':
    print("=" * 72)
    print("FIELD 3: Compressed & Cache-Optimized Sieve Arrays")
    print("=" * 72)

    # Part 1: uint8 vs uint16 in Python/NumPy
    print("\n--- Part 1: uint8 vs uint16 Sieve (Python/NumPy) ---")
    benchmark_sieve_widths()

    # Part 2: Cache analysis
    print("\n--- Part 2: Cache Behavior Analysis ---")
    cache_analysis()

    # Part 3: Bucket sieve concept
    print("\n--- Part 3: Bucket Sieve Concept ---")
    benchmark_bucket_sieve()

    # Part 4: C benchmark (real measurement)
    print("\n--- Part 4: C Sieve Micro-Benchmarks ---")
    c_sieve_comparison()

    # Summary
    print("\n" + "=" * 72)
    print("FIELD 3 CONCLUSION:")
    print("  - uint8 sieve: ~2x memory savings, minor speed gain from cache")
    print("  - Tiled sieve: potentially 1.5-3x from L1 cache residency")
    print("  - Bucket sieve: key for large-FB GNFS (100K+ primes)")
    print("  - PRIORITY: MEDIUM — helps at 50d+, essential at 70d+")
    print("  - NEXT: Integrate tiled + bucket into gnfs_sieve_c.c")
    print("=" * 72)

#!/usr/bin/env python3
"""
V4 Research — Iteration 3: End-to-end benchmark of uint16 sieve
================================================================
Apply the uint16 sieve optimization to SIQS and measure actual factoring speedup.
Also test prime power sieving (p^2, p^3).
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
from siqs_engine import siqs_factor, siqs_params


def generate_semiprime(nd):
    """Generate a semiprime of approximately nd digits."""
    half = nd // 2
    p = gmpy2.next_prime(mpz(10)**(half) + 1000003)
    q = gmpy2.next_prime(mpz(10)**(nd - half) + 9000049)
    n = p * q
    actual_nd = len(str(int(n)))
    return n, actual_nd


def benchmark_siqs(nd_list, n_trials=1):
    """Benchmark current SIQS at multiple digit sizes."""
    print(f"{'='*70}")
    print(f"SIQS END-TO-END BENCHMARK")
    print(f"{'='*70}")

    results = {}
    for nd in nd_list:
        times = []
        for trial in range(n_trials):
            n, actual_nd = generate_semiprime(nd)
            print(f"\n  {actual_nd}d trial {trial+1}/{n_trials}:")
            t0 = time.time()
            factor = siqs_factor(n, verbose=True, time_limit=300)
            elapsed = time.time() - t0
            if factor and factor > 1 and n % factor == 0:
                print(f"    FACTORED in {elapsed:.1f}s: {factor}")
                times.append(elapsed)
            else:
                print(f"    FAILED after {elapsed:.1f}s")
                times.append(None)

        results[nd] = times
        if times and times[0] is not None:
            print(f"\n  Summary {nd}d: {min(t for t in times if t):.1f}s")

    return results


if __name__ == '__main__':
    print("V4 RESEARCH — ITERATION 3: E2E BENCHMARK")
    print(f"Date: 2026-03-15\n")

    # Quick benchmarks at 48d, 54d, 57d to establish baseline
    # (These should match or beat the scoreboard times)
    results = benchmark_siqs([48, 54, 57, 60], n_trials=1)

    print(f"\n{'='*70}")
    print(f"BENCHMARK COMPLETE")
    print(f"{'='*70}")
    print(f"\nResults:")
    for nd, times in results.items():
        if times and times[0] is not None:
            print(f"  {nd}d: {times[0]:.1f}s")
        else:
            print(f"  {nd}d: FAILED")

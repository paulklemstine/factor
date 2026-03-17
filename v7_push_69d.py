#!/usr/bin/env python3
"""
Track 2: Push SIQS to 69d
==========================
Session 7 — Engineering track

Goals:
1. Profile SIQS at 66d to find current bottleneck breakdown
2. Test parameter variations (FB size, M, T_bits)
3. Test K-S multiplier='auto'
4. Test n_workers=2,3
5. Find path to 69d in < 300s
"""

import gmpy2
from gmpy2 import mpz, is_prime, next_prime
import time
import sys
import os
import math

sys.path.insert(0, '/home/raver1975/factor')

# Test semiprimes at various digit levels
def make_semiprime(nd):
    """Generate a balanced semiprime with nd digits."""
    import random
    random.seed(nd * 1000 + 42)  # reproducible
    half = nd // 2
    # Generate primes near 10^(half-1)
    base = mpz(10) ** (half - 1)
    p = gmpy2.next_prime(base + random.randint(1, int(base)))
    q = gmpy2.next_prime(p + random.randint(1, int(base // 10)))
    while p == q:
        q = gmpy2.next_prime(q)
    N = p * q
    # Adjust to exact digit count
    while len(str(N)) < nd:
        q = gmpy2.next_prime(q)
        N = p * q
    while len(str(N)) > nd:
        p = gmpy2.next_prime(base + random.randint(1, int(base // 2)))
        q = gmpy2.next_prime(p + random.randint(1, int(base // 10)))
        N = p * q
    return int(N), int(p), int(q)


# Known hard semiprimes for testing
TEST_NUMBERS = {
    # Balanced semiprimes with known factors for verification
    66: 150000000000000000000000000000017800000000000000000000000000000483,
    # p=300000000000000000000000000000023, q=500000000000000000000000000000021
    69: 150000000000000000000000000000007771000000000000000000000000000015943,
    # p=3000000000000000000000000000000149, q=50000000000000000000000000000000107
}


def profile_66d():
    """Profile SIQS at 66d to find bottleneck."""
    from siqs_engine import siqs_factor, siqs_params

    print("=" * 70)
    print("PROFILE: SIQS at 66d")
    print("=" * 70)

    # Use the known 66d number
    N = TEST_NUMBERS[66]
    nd = len(str(N))
    print(f"N = {N} ({nd}d)")

    fb_size, M = siqs_params(nd)
    print(f"Parameters: FB={fb_size}, M={M}")

    t0 = time.time()
    result = siqs_factor(N, verbose=True, n_workers=1)
    dt = time.time() - t0

    if result:
        print(f"\n  FACTORED in {dt:.1f}s: {result} x {N // result}")
    else:
        print(f"\n  FAILED after {dt:.1f}s")

    return dt


def test_param_variations_66d():
    """Test different parameter combinations at 66d."""
    from siqs_engine import siqs_factor

    print("\n" + "=" * 70)
    print("PARAMETER SWEEP at 66d")
    print("=" * 70)

    N = TEST_NUMBERS[66]

    configs = [
        {"name": "baseline (k=1, w=1)", "multiplier": 1, "n_workers": 1},
        {"name": "k=auto, w=1", "multiplier": 'auto', "n_workers": 1},
        {"name": "k=1, w=2", "multiplier": 1, "n_workers": 2},
        {"name": "k=auto, w=2", "multiplier": 'auto', "n_workers": 2},
    ]

    results = []
    for cfg in configs:
        print(f"\n--- {cfg['name']} ---")
        t0 = time.time()
        try:
            result = siqs_factor(N, verbose=True, time_limit=180,
                               multiplier=cfg['multiplier'],
                               n_workers=cfg['n_workers'])
            dt = time.time() - t0
            ok = result is not None
        except Exception as e:
            dt = time.time() - t0
            ok = False
            print(f"  ERROR: {e}")

        results.append((cfg['name'], dt, ok))
        print(f"  => {dt:.1f}s {'OK' if ok else 'FAIL'}")

    print("\n--- SUMMARY ---")
    for name, dt, ok in results:
        print(f"  {name:25s}: {dt:7.1f}s {'OK' if ok else 'FAIL'}")

    return results


def attempt_69d():
    """Attempt 69d with best configuration."""
    from siqs_engine import siqs_factor

    print("\n" + "=" * 70)
    print("ATTEMPT: 69d")
    print("=" * 70)

    N = TEST_NUMBERS[69]
    nd = len(str(N))
    print(f"N = {N} ({nd}d)")

    # Try with n_workers=2 and auto multiplier
    configs = [
        {"name": "k=1, w=2", "multiplier": 1, "n_workers": 2},
        {"name": "k=auto, w=2", "multiplier": 'auto', "n_workers": 2},
    ]

    for cfg in configs:
        print(f"\n--- {cfg['name']} ---")
        t0 = time.time()
        try:
            result = siqs_factor(N, verbose=True, time_limit=600,
                               multiplier=cfg['multiplier'],
                               n_workers=cfg['n_workers'])
            dt = time.time() - t0
            if result:
                print(f"\n  69d FACTORED in {dt:.1f}s: {result} x {N // result}")
                return dt
            else:
                print(f"\n  FAILED after {dt:.1f}s")
        except Exception as e:
            print(f"  ERROR: {e}")

    return None


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", action="store_true", help="Profile 66d")
    parser.add_argument("--sweep", action="store_true", help="Parameter sweep 66d")
    parser.add_argument("--69d", dest="try69", action="store_true", help="Attempt 69d")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    args = parser.parse_args()

    if args.all or args.profile:
        profile_66d()

    if args.all or args.sweep:
        test_param_variations_66d()

    if args.all or args.try69:
        attempt_69d()

    if not any([args.all, args.profile, args.sweep, args.try69]):
        print("Usage: python v7_push_69d.py --profile|--sweep|--69d|--all")
        print("Starting with profile...")
        profile_66d()

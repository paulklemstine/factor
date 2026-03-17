#!/usr/bin/env python3
"""Comprehensive benchmark: SIQS, GNFS, ECDLP with latest optimizations."""
import time
import signal
import sys
import random
import gmpy2
from gmpy2 import mpz, next_prime

signal.alarm(600)

# Generate deterministic balanced semiprimes at target digit sizes
def make_semiprime(target_digits, seed=42):
    """Generate a balanced semiprime with approximately target_digits digits."""
    rng = random.Random(seed + target_digits)
    half_digits = target_digits // 2
    # Generate two primes of ~half_digits digits
    lo = 10**(half_digits - 1)
    hi = 10**half_digits - 1
    p = int(next_prime(mpz(rng.randint(lo, hi))))
    q = int(next_prime(mpz(rng.randint(lo, hi))))
    while q == p:
        q = int(next_prime(mpz(rng.randint(lo, hi))))
    return p * q, min(p, q), max(p, q)


print("=" * 70)
print("COMPREHENSIVE BENCHMARK — All Solvers")
print("=" * 70)

results = []

# ============================================================
# SIQS Benchmarks: 48d, 54d, 60d, 63d, 66d
# ============================================================
print("\n" + "=" * 70)
print("SIQS ENGINE")
print("=" * 70)

from siqs_engine import siqs_factor

siqs_targets = [48, 54, 60, 63, 66]
for td in siqs_targets:
    n, p, q = make_semiprime(td)
    nd = len(str(n))
    print(f"\n  SIQS {td}d (actual {nd}d): {n}")
    t0 = time.time()
    try:
        result = siqs_factor(n, verbose=False, time_limit=600)
        elapsed = time.time() - t0
        ok = result is not None and result != n and result != 1
        if ok:
            print(f"    SUCCESS: {elapsed:.1f}s (factor={result})")
        else:
            print(f"    FAILED: {elapsed:.1f}s")
        results.append(("SIQS", td, nd, elapsed, ok))
    except Exception as e:
        elapsed = time.time() - t0
        print(f"    ERROR: {elapsed:.1f}s — {e}")
        results.append(("SIQS", td, nd, elapsed, False))

# ============================================================
# GNFS Benchmarks: 34d, 40d, 43d
# ============================================================
print("\n" + "=" * 70)
print("GNFS ENGINE")
print("=" * 70)

from gnfs_engine import gnfs_factor

gnfs_targets = [34, 40, 43]
for td in gnfs_targets:
    n, p, q = make_semiprime(td)
    nd = len(str(n))
    print(f"\n  GNFS {td}d (actual {nd}d): {n}")
    t0 = time.time()
    try:
        result = gnfs_factor(n, verbose=True, time_limit=600)
        elapsed = time.time() - t0
        ok = result is not None and result != n and result != 1
        if ok:
            print(f"    SUCCESS: {elapsed:.1f}s (factor={result})")
        else:
            print(f"    FAILED: {elapsed:.1f}s")
        results.append(("GNFS", td, nd, elapsed, ok))
    except Exception as e:
        elapsed = time.time() - t0
        print(f"    ERROR: {elapsed:.1f}s — {e}")
        results.append(("GNFS", td, nd, elapsed, False))

# ============================================================
# SCOREBOARD
# ============================================================
print("\n" + "=" * 70)
print("UPDATED SCOREBOARD")
print("=" * 70)
print(f"{'Method':<8} {'Target':<8} {'Actual':<8} {'Time':>10} {'Status':<8}")
print("-" * 50)
for method, td, nd, elapsed, ok in results:
    status = "PASS" if ok else "FAIL"
    print(f"{method:<8} {td:<8}d {nd:<8}d {elapsed:>9.1f}s {status:<8}")

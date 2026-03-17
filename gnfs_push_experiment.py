#!/usr/bin/env python3
"""GNFS push experiment: test improvements incrementally on 45d-55d."""
import time
import signal
import sys
import random
import gmpy2
from gmpy2 import mpz, next_prime

sys.stdout.reconfigure(line_buffering=True)

def make_semiprime(target_digits, seed=42):
    rng = random.Random(seed + target_digits)
    half_digits = target_digits // 2
    lo = 10**(half_digits - 1)
    hi = 10**half_digits - 1
    p = int(next_prime(mpz(rng.randint(lo, hi))))
    q = int(next_prime(mpz(rng.randint(lo, hi))))
    while q == p:
        q = int(next_prime(mpz(rng.randint(lo, hi))))
    return p * q, min(p, q), max(p, q)

from gnfs_engine import gnfs_factor

# Iteration 9: push to 50d after 48d success
targets = [50]
time_limit = 2100  # 35 min — 50d will need more sieve time

results = []
for td in targets:
    n, p, q = make_semiprime(td)
    nd = len(str(n))
    print(f"\n{'='*60}")
    print(f"GNFS {td}d (actual {nd}d): n={n}")
    print(f"  p={p}")
    print(f"  q={q}")
    print(f"{'='*60}")
    t0 = time.time()
    try:
        result = gnfs_factor(n, verbose=True, time_limit=time_limit)
        elapsed = time.time() - t0
        ok = result is not None and result != n and result != 1
        if ok:
            print(f"  => FACTORED in {elapsed:.1f}s: {result}")
        else:
            print(f"  => FAILED in {elapsed:.1f}s (result={result})")
    except Exception as e:
        elapsed = time.time() - t0
        print(f"  => ERROR in {elapsed:.1f}s: {e}")
        import traceback; traceback.print_exc()
        ok = False
    results.append((td, nd, elapsed, ok))

print(f"\n{'='*60}")
print("BASELINE SCOREBOARD")
print(f"{'Target':>8} {'Actual':>8} {'Time':>10} {'Status':>8}")
for td, nd, elapsed, ok in results:
    print(f"{td:>8}d {nd:>8}d {elapsed:>9.1f}s {'PASS' if ok else 'FAIL':>8}")

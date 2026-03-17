#!/usr/bin/env python3
"""GNFS benchmark: 34d, 40d, 43d."""
import time
import signal
import sys
import random
import gmpy2
from gmpy2 import mpz, next_prime

sys.stdout.reconfigure(line_buffering=True)
signal.alarm(600)

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

results = []
for td in [24, 31, 34, 40, 43]:
    n, p, q = make_semiprime(td)
    nd = len(str(n))
    print(f"GNFS {td}d (actual {nd}d)...", end=" ", flush=True)
    t0 = time.time()
    try:
        result = gnfs_factor(n, verbose=False, time_limit=600)
        elapsed = time.time() - t0
        ok = result is not None and result != n and result != 1
        status = f"OK {elapsed:.1f}s" if ok else f"FAIL {elapsed:.1f}s"
    except Exception as e:
        elapsed = time.time() - t0
        status = f"ERR {elapsed:.1f}s ({e})"
        ok = False
    print(status, flush=True)
    results.append((td, nd, elapsed, ok))

print("\nGNFS SCOREBOARD")
print(f"{'Target':>8} {'Actual':>8} {'Time':>10} {'Status':>8}")
for td, nd, elapsed, ok in results:
    print(f"{td:>8}d {nd:>8}d {elapsed:>9.1f}s {'PASS' if ok else 'FAIL':>8}")

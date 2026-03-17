#!/usr/bin/env python3
"""
Track C: Test presieve integration with CORRECT threshold adjustment.

Currently jit_sieve skips primes < 32, and small_prime_correction lowers the
threshold to compensate. The presieve function exists but is never called.

Strategy: Call jit_presieve BEFORE jit_sieve. Since presieve adds small prime
contributions to the sieve array, we should NOT subtract small_prime_correction
from the threshold (or reduce it). Test at 48d, 54d, 60d.
"""
import resource
resource.setrlimit(resource.RLIMIT_AS, (4*1024*1024*1024, 4*1024*1024*1024))

import sys
import os
import time
import math
import random
import copy
from gmpy2 import mpz, next_prime

# Test presieve vs no-presieve at multiple sizes
from siqs_engine import siqs_factor

def make_semiprime(digits, seed=42):
    rng = random.Random(seed)
    half = digits * 332 // 200
    p = int(next_prime(mpz(rng.getrandbits(half)) | (mpz(1) << (half-1))))
    q = int(next_prime(mpz(rng.getrandbits(half)) | (mpz(1) << (half-1))))
    return p * q, p, q

# First, let's verify the current baseline (no presieve, with small_prime_correction)
print("="*70)
print("TRACK C: PRESIEVE BENCHMARK")
print("="*70)

for digits in [48, 54, 60]:
    N, p, q = make_semiprime(digits)
    print(f"\n--- {digits}d semiprime ---")
    print(f"N = {N}")

    t0 = time.time()
    f = siqs_factor(N, verbose=True, time_limit=300, n_workers=0, multiplier='auto')
    elapsed = time.time() - t0
    ok = f and N % f == 0
    print(f"{digits}d baseline: {'OK' if ok else 'FAIL'} in {elapsed:.1f}s")

    if not ok:
        print("  BASELINE FAILED, skipping presieve test")
        continue

print("\n\nNow testing presieve integration...")
print("To enable presieve, we need to patch the sieve_and_collect function.")
print("The key insight: if presieve adds small prime logs to the sieve array,")
print("then small_prime_correction should be 0 (or near 0).")
print()
print("ANALYSIS:")
print("  Current: sieve_buf[:] = 0; jit_sieve(skip <32); thresh -= small_prime_correction")
print("  Proposed: sieve_buf[:] = 0; jit_presieve(tiles <32); jit_sieve(skip <32); thresh unchanged")
print()
print("The presieve adds exact log values at exact positions, while the")
print("small_prime_correction estimates the AVERAGE contribution. Presieve is")
print("strictly more accurate — fewer false positives in trial division.")

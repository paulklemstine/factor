#!/usr/bin/env python3
"""Track A: Test 69d factoring with restored small_prime_correction and n_workers=2."""
import resource
resource.setrlimit(resource.RLIMIT_AS, (4*1024*1024*1024, 4*1024*1024*1024))
from siqs_engine import siqs_factor
from gmpy2 import mpz, next_prime
import random, time

rng = random.Random(42)
half = 69 * 332 // 200
p = int(next_prime(mpz(rng.getrandbits(half)) | (mpz(1) << (half-1))))
q = int(next_prime(mpz(rng.getrandbits(half)) | (mpz(1) << (half-1))))
N = p * q
print(f"N = {N}")
print(f"  {len(str(N))}d, p={len(str(p))}d, q={len(str(q))}d")
t0 = time.time()
f = siqs_factor(N, verbose=True, time_limit=600, n_workers=2, multiplier='auto')
elapsed = time.time() - t0
print(f'69d: {"OK" if f and N%f==0 else "FAIL"} in {elapsed:.1f}s')
if f:
    print(f"  factor = {f}")

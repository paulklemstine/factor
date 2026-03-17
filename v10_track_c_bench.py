#!/usr/bin/env python3
"""Track C: Benchmark presieve-enabled SIQS at 48d, 54d, 60d."""
import resource
resource.setrlimit(resource.RLIMIT_AS, (4*1024*1024*1024, 4*1024*1024*1024))

from siqs_engine import siqs_factor
from gmpy2 import mpz, next_prime
import random, time

def make_semiprime(digits, seed=42):
    rng = random.Random(seed)
    half = digits * 332 // 200
    p = int(next_prime(mpz(rng.getrandbits(half)) | (mpz(1) << (half-1))))
    q = int(next_prime(mpz(rng.getrandbits(half)) | (mpz(1) << (half-1))))
    return p * q, p, q

print("="*70)
print("TRACK C: PRESIEVE BENCHMARK (presieve enabled, no small_prime_correction)")
print("="*70)

for digits in [48, 54, 60]:
    N, p, q = make_semiprime(digits)
    print(f"\n--- {digits}d semiprime ---")
    t0 = time.time()
    f = siqs_factor(N, verbose=True, time_limit=300, n_workers=0, multiplier='auto')
    elapsed = time.time() - t0
    ok = f and N % f == 0
    print(f"{digits}d presieve: {'OK' if ok else 'FAIL'} in {elapsed:.1f}s")

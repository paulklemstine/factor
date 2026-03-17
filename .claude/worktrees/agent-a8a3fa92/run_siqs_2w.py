#!/usr/bin/env python3
"""SIQS test: 66d and 69d with 2 workers."""
import sys, time, gmpy2
sys.path.insert(0, '/home/raver1975/factor')
from siqs_engine import siqs_factor

def make_semiprime(digits):
    half = digits // 2
    p = gmpy2.next_prime(gmpy2.mpz(10)**(half-1) + 42)
    q = gmpy2.next_prime(gmpy2.mpz(10)**(digits - half - 1) + 179)
    return p * q, p, q

results = []

for digits in [66, 69]:
    N, p, q = make_semiprime(digits)
    print(f"\n{'='*60}", flush=True)
    print(f"SIQS {digits}d (2 workers): N = {str(N)[:40]}...", flush=True)
    print(f"Known: {p} x {q}", flush=True)

    t0 = time.time()
    result = siqs_factor(N, verbose=True, time_limit=1800, n_workers=2)
    elapsed = time.time() - t0

    if result and result != N and N % result == 0:
        print(f"\nSUCCESS: {digits}d (2w) in {elapsed:.1f}s", flush=True)
        results.append((digits, elapsed, True))
    else:
        print(f"\nFAILED: {digits}d (2w) after {elapsed:.1f}s", flush=True)
        results.append((digits, elapsed, False))

print(f"\n{'='*60}", flush=True)
print("2-WORKER RESULTS:", flush=True)
for d, t, ok in results:
    print(f"  {d}d: {'SUCCESS' if ok else 'FAILED'} in {t:.1f}s", flush=True)

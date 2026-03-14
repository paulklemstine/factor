#!/usr/bin/env python3
"""Benchmark H26 (Kolmogorov pre-filter) and H27 (population kangaroo)."""

import time
import random
from ecdlp_pythagorean import (
    secp256k1_curve, ECPoint,
    ecdlp_kolmogorov_prefilter,
    ecdlp_population_kangaroo,
    ecdlp_pythagorean_kangaroo,
    ecdlp_pythagorean_kangaroo_c,
    ecdlp_smart_solve,
)

curve = secp256k1_curve()
G = curve.G
n = curve.n

print("=" * 70)
print("H26: Kolmogorov Pre-filter Benchmark")
print("=" * 70)

# Test with structured keys (should be found)
structured_keys = [
    ("2^30", 1 << 30),
    ("2^40 - 1", (1 << 40) - 1),
    ("2^25 + 2^15 + 1", (1 << 25) + (1 << 15) + 1),
    ("fib(50)=12586269025", 12586269025),
    ("100!", 93326215443944152681699238856266700490715968264381621468592963895217599993229915608941463976156518286253697920827223758251185210916864000000000000000000000000),
    ("31#=200560490130", 200560490130),  # primorial
    ("palindrome 0b10000000001", 0b10000000001),
    ("random 28-bit", random.randint(1 << 27, 1 << 28)),  # should NOT be found
]

for name, k in structured_keys:
    if k >= 2**48:
        bound = k * 2
    else:
        bound = 1 << 48
    K = curve.scalar_mult(k % n, G)
    t0 = time.time()
    result = ecdlp_kolmogorov_prefilter(curve, G, K, bound)
    elapsed = time.time() - t0
    found = result is not None and result == k % n
    print(f"  {name:30s}: {'FOUND' if found else 'miss':5s} ({elapsed:.3f}s)")

print()
print("=" * 70)
print("H27: Population Kangaroo vs Standard Kangaroo")
print("=" * 70)

TRIALS = 3

for bits in [28, 32, 36]:
    bound = 1 << bits
    print(f"\n  {bits}-bit search space (k < 2^{bits}):")

    # Standard 2-walker Python kangaroo
    times_std = []
    for trial in range(TRIALS):
        k_secret = random.randint(1, bound - 1)
        K = curve.scalar_mult(k_secret, G)
        t0 = time.time()
        result = ecdlp_pythagorean_kangaroo(curve, G, K, bound)
        elapsed = time.time() - t0
        ok = result is not None and result == k_secret
        times_std.append(elapsed)
        if not ok:
            times_std[-1] = float('inf')
    avg_std = sum(t for t in times_std if t != float('inf')) / max(1, sum(1 for t in times_std if t != float('inf')))
    solved_std = sum(1 for t in times_std if t != float('inf'))

    # Population kangaroo (50 walkers)
    times_pop = []
    for trial in range(TRIALS):
        k_secret = random.randint(1, bound - 1)
        K = curve.scalar_mult(k_secret, G)
        t0 = time.time()
        result = ecdlp_population_kangaroo(curve, G, K, bound, num_walkers=50)
        elapsed = time.time() - t0
        ok = result is not None and result == k_secret
        times_pop.append(elapsed)
        if not ok:
            times_pop[-1] = float('inf')
    avg_pop = sum(t for t in times_pop if t != float('inf')) / max(1, sum(1 for t in times_pop if t != float('inf')))
    solved_pop = sum(1 for t in times_pop if t != float('inf'))

    # C kangaroo (with new NK scaling)
    times_c = []
    for trial in range(TRIALS):
        k_secret = random.randint(1, bound - 1)
        K = curve.scalar_mult(k_secret, G)
        t0 = time.time()
        result = ecdlp_pythagorean_kangaroo_c(curve, G, K, bound)
        elapsed = time.time() - t0
        ok = result is not None and result == k_secret
        times_c.append(elapsed)
        if not ok:
            times_c[-1] = float('inf')
    avg_c = sum(t for t in times_c if t != float('inf')) / max(1, sum(1 for t in times_c if t != float('inf')))
    solved_c = sum(1 for t in times_c if t != float('inf'))

    print(f"    Std kangaroo (2-walk):  {avg_std:7.3f}s avg  ({solved_std}/{TRIALS} solved)")
    print(f"    Pop kangaroo (50-walk): {avg_pop:7.3f}s avg  ({solved_pop}/{TRIALS} solved)")
    print(f"    C kangaroo (NK scaled): {avg_c:7.3f}s avg  ({solved_c}/{TRIALS} solved)")
    if avg_std > 0 and avg_pop > 0:
        print(f"    Pop speedup vs std: {avg_std/avg_pop:.2f}x")
    if avg_std > 0 and avg_c > 0:
        print(f"    C speedup vs std:   {avg_std/avg_c:.2f}x")

print()
print("=" * 70)
print("Smart Solve (H26 + C kangaroo pipeline)")
print("=" * 70)

# Test structured key through smart solver
k_struct = (1 << 35) + (1 << 20) + 1
K = curve.scalar_mult(k_struct, G)
t0 = time.time()
result = ecdlp_smart_solve(curve, G, K, 1 << 48, verbose=True)
elapsed = time.time() - t0
print(f"  Structured key: {'FOUND' if result == k_struct else 'FAIL'} in {elapsed:.3f}s")

# Test random key through smart solver
k_rand = random.randint(1 << 27, 1 << 28)
K = curve.scalar_mult(k_rand, G)
t0 = time.time()
result = ecdlp_smart_solve(curve, G, K, 1 << 30, verbose=True)
elapsed = time.time() - t0
print(f"  Random key: {'FOUND' if result == k_rand else 'FAIL'} in {elapsed:.3f}s")

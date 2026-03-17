"""
Pythagorean Tree x Algebraic Geometry Experiment

HYPOTHESIS: The Pythagorean tree generates rational points on the conic x^2 + y^2 = z^2.
The HEIGHT function h(m,n) = max(|m|,|n|) grows exponentially along B1/B2 paths but
LINEARLY along B3 (parabolic).

KEY IDEA: For a composite N = p*q, consider the tree mod N as points on the conic mod p
crossed with the conic mod q. The Neron-Tate height on the product decomposes as h_p + h_q.
If we can detect when h_p is "small" (near a torsion point mod p), we find p.

Specifically: torsion points on x^2+y^2=z^2 mod p are the 4 points where (m,n) = (1,0), (0,1),
(-1,0), (0,-1) mod p. If a tree walk brings us NEAR a torsion point mod p (i.e., m or n is
small mod p), then gcd(m, N) or gcd(n, N) might reveal p.

EXPERIMENT: Walk the tree mod N for various semiprimes. Track gcd(m, N), gcd(n, N),
gcd(m-n, N), gcd(m+n, N) at each node. Measure how often these reveal factors vs random.
Also test: does the "height" h(m,n) = m^2+n^2 mod N have detectable structure?
"""

import random
import math
import time

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

# Berggren matrices acting on (m, n)
def B1(m, n, N): return ((2*m - n) % N, m % N)
def B2(m, n, N): return ((2*m + n) % N, m % N)
def B3(m, n, N): return ((m + 2*n) % N, n % N)

MATRICES = [B1, B2, B3]

def test_height_decomposition(N, p, q, num_walks=200, depth=50):
    """Walk tree mod N, check if height-based quantities reveal factors."""
    factors_found = 0
    total_checks = 0

    # Track which derived quantities find factors
    method_hits = {'m': 0, 'n': 0, 'm-n': 0, 'm+n': 0, 'm^2+n^2': 0, 'm*n': 0}

    for walk in range(num_walks):
        m, n = 2, 1
        for step in range(depth):
            # Apply random matrix
            mat = random.choice(MATRICES)
            m, n = mat(m, n, N)
            total_checks += 1

            # Check various derived quantities
            for name, val in [('m', m), ('n', n), ('m-n', (m-n)%N),
                              ('m+n', (m+n)%N), ('m^2+n^2', (m*m+n*n)%N),
                              ('m*n', (m*n)%N)]:
                g = gcd(val, N)
                if 1 < g < N:
                    method_hits[name] += 1
                    factors_found += 1

    return factors_found, total_checks, method_hits

def test_random_baseline(N, p, q, num_checks):
    """Random values mod N, check gcd."""
    hits = 0
    for _ in range(num_checks):
        val = random.randint(1, N-1)
        g = gcd(val, N)
        if 1 < g < N:
            hits += 1
    return hits

# Test with various semiprime sizes
print("=" * 70)
print("ALGEBRAIC GEOMETRY: Height Decomposition on Pythagorean Conic")
print("=" * 70)

random.seed(42)
results = []

for bits in [20, 30, 40, 50]:
    # Generate semiprime
    from sympy import nextprime, isprime
    p = nextprime(random.randint(2**(bits//2 - 1), 2**(bits//2)))
    q = nextprime(random.randint(2**(bits//2 - 1), 2**(bits//2)))
    N = p * q

    print(f"\n--- N = {N} ({N.bit_length()}b, p={p}, q={q}) ---")

    found, checks, methods = test_height_decomposition(N, p, q, num_walks=500, depth=100)
    baseline = test_random_baseline(N, p, q, checks * 6)  # 6 derived values per check

    factor_rate = found / (checks * 6) if checks > 0 else 0
    baseline_rate = baseline / (checks * 6) if checks > 0 else 0

    print(f"  Tree walk: {found} factor hits in {checks*6} derived values (rate={factor_rate:.6f})")
    print(f"  Random:    {baseline} factor hits in {checks*6} random values (rate={baseline_rate:.6f})")
    print(f"  Ratio:     {factor_rate/baseline_rate:.2f}x" if baseline_rate > 0 else "  Ratio: inf")
    print(f"  Method breakdown: {methods}")
    results.append((bits, factor_rate, baseline_rate, methods))

# NEW: Test projective height filtration
print("\n" + "=" * 70)
print("THEOREM TEST: Projective Height Filtration")
print("If h_p(m,n) = min(v_p(m), v_p(n)) is detectable from h_N(m,n)...")
print("=" * 70)

p = nextprime(1000)
q = nextprime(2000)
N = p * q

# Collect heights along B3 (parabolic) paths vs B1/B2 (hyperbolic)
for matrix_name, matrix_fn in [("B3 (parabolic)", B3), ("B1 (hyperbolic)", B1), ("B2 (hyperbolic)", B2)]:
    m, n = 2, 1
    gcd_hits = 0
    steps = 2000
    for i in range(steps):
        m, n = matrix_fn(m, n, N)
        for val in [m, n, (m-n)%N, (m+n)%N]:
            g = gcd(val, N)
            if 1 < g < N:
                gcd_hits += 1
    print(f"  {matrix_name}: {gcd_hits} factor hits in {steps*4} checks (rate={gcd_hits/(steps*4):.6f})")

print("\n--- CONCLUSION ---")
print("Comparing tree-walk factor detection rate vs random baseline.")
print("If ratio > 1, the tree structure helps; if ~1, no advantage.")

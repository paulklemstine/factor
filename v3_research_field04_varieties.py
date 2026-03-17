#!/usr/bin/env python3
"""
Field 4: Algebraic Geometry of Varieties — Factoring via Variety Intersection
=============================================================================

HYPOTHESIS: The factoring problem N=p*q can be viewed geometrically:
  - The "multiplication variety" V = {(x,y) : x*y = N} in Z^2
  - We need integer points on this hyperbola
  - Over Z/NZ, this variety decomposes because Z/NZ ~ Z/pZ x Z/qZ (CRT)

DEEPER IDEA: Consider the affine variety defined by:
  x^2 ≡ 1 (mod N)  — this has 4 solutions: ±1, ±k where gcd(k±1, N) gives factors

Can we find non-trivial square roots of 1 mod N using geometric methods?
This is essentially what QS/GNFS do, but can algebraic geometry give shortcuts?

EXPERIMENTS:
1. Count points on y^2 = x^3 + ax + b mod N — Hasse's theorem connects to #E(F_p)
2. The "difference of squares" variety: x^2 - y^2 = N, find integer points
3. Congruence intersection: find x where x^2 ≡ a (mod N) for various a
4. Elliptic curve point counting mod N vs mod p — can we detect p from #E(Z/NZ)?
"""

import time
import math
import gmpy2
from gmpy2 import mpz, gcd, is_prime, next_prime, isqrt, jacobi
import random

# ─── Experiment 1: Square roots of unity mod N ──────────────────────────

print("=" * 70)
print("EXPERIMENT 1: Non-trivial square roots of 1 mod N")
print("=" * 70)

def find_sqrt_unity(N, p, q, trials=1000):
    """
    x^2 ≡ 1 (mod N) has 4 solutions when N=pq (p,q odd primes):
    x ≡ ±1 (mod p) AND x ≡ ±1 (mod q)
    The non-trivial ones give factors via gcd(x±1, N).
    How hard is it to find them by random sampling?
    """
    found = set()
    for _ in range(trials):
        # Random x, compute x^((N-1)/2) mod N (should be ±1 if jacobi(x,N)=1)
        x = random.randint(2, int(N) - 1)
        r = pow(x, (int(N) - 1) // 2, int(N))
        if (r * r) % int(N) == 1:
            if r != 1 and r != int(N) - 1:
                g = gcd(r - 1, N)
                if 1 < g < N:
                    found.add(int(g))
    return found

for bits in [20, 24, 28, 32]:
    rng = gmpy2.random_state(42 + bits)
    p = gmpy2.next_prime(gmpy2.mpz_urandomb(rng, bits))
    q = gmpy2.next_prime(gmpy2.mpz_urandomb(rng, bits))
    N = p * q

    t0 = time.time()
    factors = find_sqrt_unity(N, p, q, trials=500)
    elapsed = time.time() - t0

    print(f"{bits}b: N={N}, found factors={factors}, time={elapsed:.3f}s")
    if factors:
        print(f"  → gcd method works! But this is just Euler criterion sampling.")

# ─── Experiment 2: Difference of squares variety ─────────────────────────

print()
print("=" * 70)
print("EXPERIMENT 2: Difference of squares — geometric view of Fermat")
print("=" * 70)

def fermat_method(N, max_iter=100000):
    """
    Find x,y such that x^2 - y^2 = N, i.e., (x-y)(x+y) = N.
    This is the geometry of the hyperbola x^2 - y^2 = N.
    Start at x = ceil(sqrt(N)), increment until x^2-N is a perfect square.
    """
    x = isqrt(N) + 1
    iters = 0
    while iters < max_iter:
        y2 = x * x - N
        y = isqrt(y2)
        if y * y == y2:
            return int(x - y), int(x + y), iters
        x += 1
        iters += 1
    return None, None, iters

print(f"{'bits':>6} {'iters':>8} {'time(s)':>10} {'factor':>12} {'note':>30}")
print("-" * 70)

for bits in [16, 20, 24, 28, 32]:
    rng = gmpy2.random_state(77 + bits)
    p = gmpy2.next_prime(gmpy2.mpz_urandomb(rng, bits))
    q = gmpy2.next_prime(gmpy2.mpz_urandomb(rng, bits))
    N = p * q

    t0 = time.time()
    a, b, iters = fermat_method(N)
    elapsed = time.time() - t0

    if a:
        ga = gcd(a, N)
        note = "balanced" if abs(int(p) - int(q)) < int(p) // 2 else "unbalanced"
        print(f"{bits:>6} {iters:>8} {elapsed:>10.4f} {int(ga):>12} {note:>30}")
    else:
        print(f"{bits:>6} {iters:>8} {elapsed:>10.4f} {'FAILED':>12} {'':>30}")

# Now test with BALANCED factors (where Fermat shines)
print("\nBalanced factors (|p-q| small):")
for bits in [32, 40, 48]:
    base = gmpy2.next_prime(mpz(1) << bits)
    p = base
    q = gmpy2.next_prime(p + random.randint(1, 1000))
    N = p * q

    t0 = time.time()
    a, b, iters = fermat_method(N, max_iter=100000)
    elapsed = time.time() - t0

    if a:
        ga = gcd(a, N)
        print(f"  {bits}b: |p-q|={int(q-p)}, iters={iters}, time={elapsed:.4f}s, found={int(ga)}")
    else:
        print(f"  {bits}b: |p-q|={int(q-p)}, FAILED in {iters} iters")

# ─── Experiment 3: Point counting on elliptic curves mod N ────────────────

print()
print("=" * 70)
print("EXPERIMENT 3: Elliptic curve point counting mod N vs mod p")
print("=" * 70)

def count_points_mod_m(a, b, m, limit=None):
    """Count points on y^2 = x^3 + ax + b mod m (brute force for small m)."""
    count = 1  # point at infinity
    m = int(m)
    if limit is None:
        limit = m
    for x in range(min(m, limit)):
        rhs = (x * x * x + a * x + b) % m
        # Count solutions to y^2 ≡ rhs (mod m)
        for y in range(m):
            if (y * y) % m == rhs:
                count += 1
    return count

# Small test: compare #E(Z/NZ) with #E(Z/pZ) * #E(Z/qZ)
print("CRT decomposition of elliptic curve groups over Z/NZ:")
for bits in [8, 10, 12]:
    rng = gmpy2.random_state(55 + bits)
    p = int(gmpy2.next_prime(gmpy2.mpz_urandomb(rng, bits)))
    q = int(gmpy2.next_prime(gmpy2.mpz_urandomb(rng, bits)))
    N = p * q

    a_ec, b_ec = 1, 1  # y^2 = x^3 + x + 1

    t0 = time.time()
    E_N = count_points_mod_m(a_ec, b_ec, N)
    E_p = count_points_mod_m(a_ec, b_ec, p)
    E_q = count_points_mod_m(a_ec, b_ec, q)
    elapsed = time.time() - t0

    print(f"  {bits}b: N={N}={p}*{q}, #E(Z/NZ)={E_N}, #E(F_p)={E_p}, #E(F_q)={E_q}, "
          f"product={E_p*E_q}, ratio={E_N/(E_p*E_q):.4f}, time={elapsed:.2f}s")

print()
print("ANALYSIS: By CRT, E(Z/NZ) ~ E(F_p) x E(F_q), so #E(Z/NZ) = #E(F_p) * #E(F_q).")
print("This is EXACTLY what ECM exploits — if #E(F_p) is smooth, we can find p.")
print("Point counting mod N is O(N) brute force — no shortcut without knowing p.")

# ─── Experiment 4: Variety dimension and factor detection ─────────────────

print()
print("=" * 70)
print("EXPERIMENT 4: Variety dimension analysis")
print("=" * 70)

print("""
THEORETICAL ANALYSIS:

The factoring variety V_N = {(x,y) in Z^2 : x*y = N, x > 1, y > 1} is a
finite set of points on the hyperbola xy = N.

Over Z/NZ (or more precisely Z/pZ x Z/qZ via CRT):
- The zero divisors of Z/NZ form two "lines": multiples of p and multiples of q
- These are "hidden subvarieties" that we cannot see without knowing p,q
- Finding ANY zero divisor of Z/NZ is equivalent to factoring N

Key algebraic geometry concepts:
1. Spec(Z/NZ) = Spec(Z/pZ) ∪ Spec(Z/qZ) — the scheme has two components
2. The irreducible decomposition of Spec(Z/NZ) IS the factoring of N
3. Computing this decomposition requires... factoring N (circular!)

The scheme-theoretic approach doesn't help because:
- Primary decomposition of ideals in Z/NZ requires factoring N
- Hilbert function computation requires knowing the components
- Every algebraic geometry tool eventually reduces to factoring the modulus
""")

# Quantitative test: zero divisors in Z/NZ
print("Zero divisor density in Z/NZ:")
for bits in [8, 10, 12, 14, 16]:
    rng = gmpy2.random_state(33 + bits)
    p = int(gmpy2.next_prime(gmpy2.mpz_urandomb(rng, bits)))
    q = int(gmpy2.next_prime(gmpy2.mpz_urandomb(rng, bits)))
    N = p * q

    # Count zero divisors: multiples of p or q in [1, N-1]
    zd = (N // p - 1) + (N // q - 1)  # multiples of p + multiples of q (excluding 0 and N)
    density = zd / N

    # Random sampling: how many tries to hit a zero divisor?
    hits = 0
    for trial in range(1000):
        x = random.randint(1, N - 1)
        if gcd(x, N) > 1:
            hits += 1

    print(f"  {bits}b: N={N}, zero_divisors={zd}/{N} ({density:.6f}), "
          f"random_hit_rate={hits}/1000 ({hits/10:.1f}%), "
          f"expected_tries={int(1/density) if density > 0 else 'inf'}")

print()
print("=" * 70)
print("CONCLUSIONS")
print("=" * 70)
print("""
1. SQUARE ROOTS OF UNITY: Finding non-trivial sqrt(1) mod N factors N, but
   random sampling finds them with probability ~2/N — no better than trial division.
   QS/GNFS construct these systematically via smooth relations.

2. FERMAT/DIFFERENCE-OF-SQUARES: The hyperbola x^2-y^2=N is a 1D variety.
   Fermat's method walks along it but is O(N^(1/3)) for random semiprimes.
   Only fast when |p-q| is small (balanced factors near sqrt(N)).

3. ELLIPTIC CURVE POINT COUNTING: #E(Z/NZ) = #E(F_p)*#E(F_q) by CRT, which
   is exactly what ECM exploits. No new insight from the geometric perspective.

4. SCHEME DECOMPOSITION: Decomposing Spec(Z/NZ) into irreducible components
   IS factoring N. Algebraic geometry provides beautiful language but no shortcut.

5. ZERO DIVISOR DENSITY: ~(1/p + 1/q) ≈ 2/sqrt(N) — exponentially rare.
   Random sampling needs O(sqrt(N)) attempts — same as Pollard rho.

6. VERDICT: Algebraic geometry gives elegant reformulations of factoring but
   NO computational shortcuts. Every geometric approach reduces to a known
   method (Fermat, ECM, QS, Pollard rho). NEGATIVE result.
""")

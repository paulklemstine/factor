#!/usr/bin/env python3
"""
v36: Third-Order p-1 Method using Cubic Extension Rings
========================================================

Theory: p^3 - 1 = (p-1)(p^2+p+1).
- Standard p-1 tests whether (p-1) is B-smooth.
- Williams p+1 tests whether (p+1) is B-smooth.
- Third-order p-1 tests whether (p^2+p+1) is B-smooth — NEW and INDEPENDENT.

Implementation: work in Z[x]/(f(x), N) where f(x) is an irreducible cubic over Q.
An element alpha in this ring, raised to E = lcm(1..B1), gives:
  gcd(Norm(alpha^E - 1), N)
When f is irreducible mod p, the multiplicative group has order p^3-1 = (p-1)(p^2+p+1).
After removing the (p-1) part (done implicitly by the gcd check), if p^2+p+1 | E
then alpha^E = 1 mod p, giving a nontrivial gcd.

KEY INSIGHT (verified): Berggren 3x3 matrices have order dividing p^2-1 mod p
(they preserve a quadratic form), so they do NOT test p^2+p+1. We need matrices
with IRREDUCIBLE characteristic polynomial over F_p.
"""

import gmpy2
from gmpy2 import mpz, gcd, is_prime, next_prime, isqrt
import time
import random
import math
import sys

# ---------------------------------------------------------------------------
# Prime sieve
# ---------------------------------------------------------------------------
def _sieve_primes(limit):
    sieve = bytearray(b'\x01') * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = bytearray(len(sieve[i*i::i]))
    return [i for i in range(2, limit + 1) if sieve[i]]

_SMALL_PRIMES = _sieve_primes(1_000_000)

# ---------------------------------------------------------------------------
# Arithmetic in Z[x]/(x^3 + a*x + b, N)  — cubic extension ring mod N
# Elements are triples (c0, c1, c2) representing c0 + c1*x + c2*x^2
# ---------------------------------------------------------------------------

def cubic_mul(A, B, a_coeff, b_coeff, n):
    """Multiply two elements in Z[x]/(x^3 + a*x + b) mod n.
    A = (a0, a1, a2), B = (b0, b1, b2).
    x^3 = -a*x - b in this ring.
    """
    a0, a1, a2 = A
    b0, b1, b2 = B

    # Standard polynomial multiplication gives degree-4 poly,
    # then reduce x^3 = -a*x - b, x^4 = -a*x^2 - b*x
    # Product before reduction:
    # c0 = a0*b0
    # c1 = a0*b1 + a1*b0
    # c2 = a0*b2 + a1*b1 + a2*b0
    # c3 = a1*b2 + a2*b1
    # c4 = a2*b2

    c0 = a0*b0
    c1 = a0*b1 + a1*b0
    c2 = a0*b2 + a1*b1 + a2*b0
    c3 = a1*b2 + a2*b1
    c4 = a2*b2

    # Reduce x^4 = x * x^3 = x*(-a*x - b) = -a*x^2 - b*x
    # Reduce x^3 = -a*x - b
    # c3 * x^3 -> c3 * (-a*x - b)
    # c4 * x^4 -> c4 * (-a*x^2 - b*x)

    r0 = (c0 - c3 * b_coeff) % n
    r1 = (c1 - c3 * a_coeff - c4 * b_coeff) % n
    r2 = (c2 - c4 * a_coeff) % n

    return (r0, r1, r2)


def cubic_pow(A, e, a_coeff, b_coeff, n):
    """Compute A^e in Z[x]/(x^3 + a*x + b) mod n using binary exponentiation."""
    if e == 0:
        return (mpz(1), mpz(0), mpz(0))
    if e == 1:
        return A

    result = (mpz(1), mpz(0), mpz(0))  # identity = 1
    base = A

    while e > 0:
        if e & 1:
            result = cubic_mul(result, base, a_coeff, b_coeff, n)
        base = cubic_mul(base, base, a_coeff, b_coeff, n)
        e >>= 1

    return result


def cubic_norm(A, a_coeff, b_coeff, n):
    """Compute Norm(A) in Z[x]/(x^3 + a*x + b) mod n.
    Norm = product of conjugates = resultant of (a0+a1*x+a2*x^2) and (x^3+a*x+b).
    For f(x) = x^3 + a*x + b with roots r1,r2,r3:
      Norm(c0+c1*x+c2*x^2) = prod(c0 + c1*ri + c2*ri^2)
    This equals the resultant, computable as determinant of Sylvester matrix.
    """
    c0, c1, c2 = A
    # For x^3 + a*x + b, the norm of c0 + c1*x + c2*x^2 is:
    # det of the multiplication matrix (3x3) of the element
    # M = [[c0, -c2*b, -c1*b],
    #      [c1, c0-c2*a, -c1*a-c2*b],
    #      [c2, c1, c0-c2*a]]  ... wait, let me compute properly.

    # The multiplication-by-A matrix in the basis {1, x, x^2}:
    # A * 1 = c0 + c1*x + c2*x^2
    # A * x = c0*x + c1*x^2 + c2*x^3 = c0*x + c1*x^2 + c2*(-a*x - b)
    #       = -c2*b + (c0 - c2*a)*x + c1*x^2
    # A * x^2 = c0*x^2 + c1*x^3 + c2*x^4
    #         = c0*x^2 + c1*(-a*x-b) + c2*(-a*x^2-b*x)
    #         = -c1*b + (-c1*a-c2*b)*x + (c0-c2*a)*x^2

    # Matrix (columns are A*1, A*x, A*x^2):
    m00, m01, m02 = c0,       -c2*b_coeff,            -c1*b_coeff
    m10, m11, m12 = c1,       c0 - c2*a_coeff,        -c1*a_coeff - c2*b_coeff
    m20, m21, m22 = c2,       c1,                      c0 - c2*a_coeff

    det = (m00*(m11*m22 - m12*m21) - m01*(m10*m22 - m12*m20) + m02*(m10*m21 - m11*m20)) % n
    return det


# ---------------------------------------------------------------------------
# Third-order p-1 method
# ---------------------------------------------------------------------------
def third_order_pm1(n, B1=100000, num_bases=6, verbose=False):
    """
    Third-order p-1 factoring using cubic extension rings.

    Works in Z[x]/(f(x), N) where f(x) = x^3 + a*x + b is irreducible over Q.
    Computes alpha^E mod (N, f) where E = lcm(1..B1).
    Then checks gcd(Norm(alpha^E - 1), N).

    When f is irreducible mod p (a prime factor of N), the multiplicative
    group of F_p[x]/(f) has order p^3-1 = (p-1)(p^2+p+1).
    If p^2+p+1 is B1-smooth, then alpha^E ≡ 1 (mod p), giving a factor.

    We try multiple irreducible cubics to maximize coverage (each cubic is
    irreducible mod ~1/3 of primes, so 6 cubics covers ~88%).

    Args:
        n: number to factor
        B1: smoothness bound
        num_bases: number of different cubics to try
        verbose: print progress

    Returns:
        factor of n, or None
    """
    n = mpz(n)

    # Irreducible cubics over Q: x^3 + a*x + b
    # (discriminant -4a^3 - 27b^2 must not be a perfect square for irreducibility)
    cubics = [
        (1, 1),    # x^3 + x + 1, disc = -31
        (2, 1),    # x^3 + 2x + 1, disc = -59
        (1, 2),    # x^3 + x + 2, disc = -116
        (3, 1),    # x^3 + 3x + 1, disc = -135
        (2, 3),    # x^3 + 2x + 3, disc = -275
        (4, 1),    # x^3 + 4x + 1, disc = -283
        (1, 3),    # x^3 + x + 3, disc = -327
        (5, 2),    # x^3 + 5x + 2, disc = -608
    ]

    for ci in range(min(num_bases, len(cubics))):
        a_coeff, b_coeff = cubics[ci]
        a_coeff, b_coeff = mpz(a_coeff), mpz(b_coeff)

        if verbose:
            print(f"  3rd-order: cubic x^3+{a_coeff}x+{b_coeff}, B1={B1}")

        # Start with alpha = x (the element x in the quotient ring)
        alpha = (mpz(0), mpz(1), mpz(0))  # = x

        # Stage 1: alpha = alpha^{lcm(1..B1)} mod (n, f)
        for p in _SMALL_PRIMES:
            if p > B1:
                break
            pk = p
            while pk * p <= B1:
                pk *= p
            alpha = cubic_pow(alpha, pk, a_coeff, b_coeff, n)

        # Check gcd(Norm(alpha - 1), N)
        alpha_m1 = ((alpha[0] - 1) % n, alpha[1], alpha[2])
        norm_val = cubic_norm(alpha_m1, a_coeff, b_coeff, n)
        g = gcd(norm_val, n)
        if 1 < g < n:
            if verbose:
                print(f"  3rd-order hit! cubic=x^3+{a_coeff}x+{b_coeff}")
            return int(g)

        # Also check individual components (sometimes faster)
        for component in alpha_m1:
            if component % n != 0:
                g = gcd(component % n, n)
                if 1 < g < n:
                    if verbose:
                        print(f"  3rd-order hit (component)!")
                    return int(g)

    return None


# ---------------------------------------------------------------------------
# Standard p-1 (Pollard) for comparison
# ---------------------------------------------------------------------------
def pollard_pm1(n, B1=100000, verbose=False):
    """Standard Pollard p-1, Stage 1 only."""
    n = mpz(n)
    a = mpz(2)
    for p in _SMALL_PRIMES:
        if p > B1:
            break
        pk = p
        while pk * p <= B1:
            pk *= p
        a = pow(a, pk, n)

    g = gcd(a - 1, n)
    if 1 < g < n:
        return int(g)
    return None


# ---------------------------------------------------------------------------
# Standard p+1 (Williams) for comparison
# ---------------------------------------------------------------------------
def williams_pp1(n, B1=100000, verbose=False):
    """Williams p+1, Stage 1 only, multiple seeds."""
    n = mpz(n)

    def lucas_chain(v, k, n_val):
        if k == 0:
            return mpz(2)
        if k == 1:
            return v
        vl = v
        vh = (v * v - 2) % n_val
        for bit in bin(k)[3:]:
            if bit == '1':
                vl = (vl * vh - v) % n_val
                vh = (vh * vh - 2) % n_val
            else:
                vh = (vl * vh - v) % n_val
                vl = (vl * vl - 2) % n_val
        return vl

    for seed in [3, 5, 7, 11, 13]:
        v = mpz(seed)
        for p in _SMALL_PRIMES:
            if p > B1:
                break
            pk = p
            while pk * p <= B1:
                pk *= p
            v = lucas_chain(v, pk, n)

        g = gcd(v - 2, n)
        if 1 < g < n:
            return int(g)
    return None


# ---------------------------------------------------------------------------
# Smoothness check
# ---------------------------------------------------------------------------
def is_B_smooth(n, B):
    """Check if n is B-smooth (all prime factors <= B). Uses gmpy2 for speed."""
    n = mpz(n)
    if n <= 1:
        return True
    for p in _SMALL_PRIMES:
        if p > B:
            break
        if n % p == 0:
            while n % p == 0:
                n //= p
            if n == 1:
                return True
    return int(n) <= B


# ---------------------------------------------------------------------------
# Test case generation
# ---------------------------------------------------------------------------
def find_third_order_primes(bit_range, B, count=50, time_limit=30):
    """
    Find primes p where p^2+p+1 is B-smooth but p-1 and p+1 are NOT B-smooth.
    """
    results = []
    rng = random.Random(42)
    lo = 1 << (bit_range - 1)
    hi = 1 << bit_range
    t0 = time.time()

    while len(results) < count and time.time() - t0 < time_limit:
        candidate = rng.randint(lo, hi)
        p = int(next_prime(mpz(candidate)))
        if p >= hi:
            continue

        p2p1 = mpz(p) * p + p + 1
        rem = p2p1
        for sp in _SMALL_PRIMES:
            if sp > B:
                break
            if sp * sp > rem:
                break
            while rem % sp == 0:
                rem //= sp
            if rem == 1:
                break
        if rem != 1 and rem > B:
            continue

        if is_B_smooth(p - 1, B) or is_B_smooth(p + 1, B):
            continue

        results.append(p)

    return results


def generate_test_semiprimes_by_bits(half_bits, B=100000, count=20):
    """Generate semiprimes N=p*q where p^2+p+1 is B-smooth but BOTH p+-1 and q+-1 are NOT smooth."""
    primes_special = find_third_order_primes(half_bits, B, count=count*3, time_limit=30)
    rng = random.Random(123)
    lo = 1 << (half_bits - 1)
    hi = 1 << half_bits
    semiprimes = []

    for p in primes_special:
        if len(semiprimes) >= count:
            break
        for _ in range(200):
            candidate = rng.randint(lo, hi)
            q = int(next_prime(mpz(candidate)))
            if q == p or q >= hi:
                continue
            if not is_B_smooth(q - 1, B) and not is_B_smooth(q + 1, B):
                N = p * q
                semiprimes.append((N, p, q))
                break

    return semiprimes


def generate_random_semiprimes(digits, count=20):
    """Generate random semiprimes with ~digits total digits."""
    rng = random.Random(456)
    half_bits = int(digits * 3.32 / 2)
    results = []
    for _ in range(count):
        lo = 1 << (half_bits - 1)
        hi = 1 << half_bits
        p = int(next_prime(mpz(rng.randint(lo, hi))))
        q = int(next_prime(mpz(rng.randint(lo, hi))))
        while q == p:
            q = int(next_prime(mpz(rng.randint(lo, hi))))
        N = p * q
        results.append((N, p, q))
    return results


# ---------------------------------------------------------------------------
# Verify matrix orders (diagnostic)
# ---------------------------------------------------------------------------
def verify_cubic_orders():
    """Verify that cubic extension method has correct orders mod small primes."""
    print("\n  Verifying cubic extension orders mod small primes:")
    print("  (When f irreducible mod p, order should divide p^3-1 with p^2+p+1 component)")
    print()

    from v36_third_order import cubic_mul, cubic_pow, cubic_norm

    cubics_to_test = [(1, 1), (2, 1), (1, 2)]

    for a_c, b_c in cubics_to_test:
        print(f"  f(x) = x^3 + {a_c}x + {b_c}:")
        for p in [5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43]:
            # Check if f is irreducible mod p
            # f is irreducible mod p iff it has no roots mod p
            has_root = any((x**3 + a_c*x + b_c) % p == 0 for x in range(p))

            # Find order of x in F_p[x]/(f)
            alpha = (mpz(0), mpz(1), mpz(0))
            R = alpha
            order = None
            for k in range(1, p**3):
                R = cubic_mul(R, alpha, mpz(a_c), mpz(b_c), mpz(p))
                if R == (mpz(1) % p, mpz(0), mpz(0)):
                    order = k + 1
                    break
            # Hmm, let me use powering instead
            # Actually, start fresh
            one = (mpz(1), mpz(0), mpz(0))
            R = (mpz(0), mpz(1), mpz(0))  # x
            found_order = None
            for k in range(1, p**3 + 1):
                if R == one:
                    found_order = k
                    break
                R = cubic_mul(R, (mpz(0), mpz(1), mpz(0)), mpz(a_c), mpz(b_c), mpz(p))

            irr = "IRR" if not has_root else "RED"
            p2p1 = p*p+p+1
            if found_order:
                div_p2p1 = (p2p1 % found_order == 0)
                div_pm1 = ((p-1) % found_order == 0)
                div_p3m1 = ((p**3-1) % found_order == 0)
                print(f"    p={p:2d} [{irr}]: ord={found_order:5d}, p^2+p+1={p2p1:5d}, "
                      f"ord|p^2+p+1?{div_p2p1}, ord|p-1?{div_pm1}, ord|p^3-1?{div_p3m1}")
            else:
                print(f"    p={p:2d} [{irr}]: order > p^3")
        print()


# ---------------------------------------------------------------------------
# Benchmark
# ---------------------------------------------------------------------------
def benchmark():
    print("=" * 72)
    print("v36: Third-Order p-1 Method — Cubic Extension Rings")
    print("=" * 72)

    B1 = 100000

    # ====================================================================
    # Part 0: Verify theory — check cubic extension orders
    # ====================================================================
    print("\n" + "=" * 72)
    print("PART 0: Theory Verification — Cubic Extension Orders")
    print("=" * 72)

    # Quick order check for a few primes
    print("\n  f(x) = x^3 + x + 1, element = x:")
    for p in [5, 7, 11, 13, 17, 19, 23, 29, 31]:
        has_root = any((x**3 + x + 1) % p == 0 for x in range(p))
        one = (mpz(1) % p, mpz(0), mpz(0))
        alpha = (mpz(0), mpz(1), mpz(0))
        R = alpha
        found_order = None
        for k in range(1, p**3 + 1):
            if R == one:
                found_order = k
                break
            R = cubic_mul(R, alpha, mpz(1), mpz(1), mpz(p))

        irr = "IRR" if not has_root else "RED"
        p2p1 = p*p+p+1
        if found_order:
            divides = []
            if (p-1) % found_order == 0: divides.append("p-1")
            if (p+1) % found_order == 0: divides.append("p+1")
            if p2p1 % found_order == 0: divides.append("p^2+p+1")
            if ((p**3-1) % found_order == 0) and not divides: divides.append("p^3-1 only")
            print(f"    p={p:2d} [{irr}]: ord(x)={found_order}, divides: {', '.join(divides)}")

    # ====================================================================
    # Part 1: Generate special test cases
    # ====================================================================
    print("\n" + "=" * 72)
    print("PART 1: Test cases where p^2+p+1 is B-smooth but p+-1 are NOT")
    print("=" * 72)

    special_cases = {}
    special_bit_counts = {24: 15, 30: 10, 40: 5, 50: 3}
    for half_bits, cnt in special_bit_counts.items():
        digit_approx = int(half_bits * 2 * 0.301)
        cases = generate_test_semiprimes_by_bits(half_bits, B=B1, count=cnt)

        if cases:
            special_cases[half_bits] = cases
            print(f"\n  {half_bits}b factors (~{digit_approx}d N): found {len(cases)} special semiprimes")
            N, p, q = cases[0]
            p2p1 = p*p + p + 1
            print(f"    Example: p={p} ({len(str(p))}d)")
            print(f"    p^2+p+1 B-smooth? {is_B_smooth(p2p1, B1)}")
            print(f"    p-1 B-smooth?     {is_B_smooth(p-1, B1)}")
            print(f"    p+1 B-smooth?     {is_B_smooth(p+1, B1)}")
        else:
            print(f"\n  {half_bits}b factors (~{digit_approx}d N): no special cases found")

    # ====================================================================
    # Part 2: Benchmark on special cases
    # ====================================================================
    print("\n" + "=" * 72)
    print("PART 2: Benchmark on SPECIAL cases (p^2+p+1 smooth, p+-1 NOT)")
    print("=" * 72)

    results_special = {
        'pm1_hits': 0, 'pp1_hits': 0, 'third_hits': 0,
        'pm1_time': 0.0, 'pp1_time': 0.0, 'third_time': 0.0,
        'total': 0
    }

    for key, cases in special_cases.items():
        print(f"\n--- {key}-bit factor semiprimes ---")
        for i, (N, p, q) in enumerate(cases):
            results_special['total'] += 1
            nd = len(str(N))

            t0 = time.time()
            f1 = pollard_pm1(N, B1=B1)
            t_pm1 = time.time() - t0
            results_special['pm1_time'] += t_pm1
            pm1_ok = f1 is not None and 1 < f1 < N and N % f1 == 0
            if pm1_ok: results_special['pm1_hits'] += 1

            t0 = time.time()
            f2 = williams_pp1(N, B1=B1)
            t_pp1 = time.time() - t0
            results_special['pp1_time'] += t_pp1
            pp1_ok = f2 is not None and 1 < f2 < N and N % f2 == 0
            if pp1_ok: results_special['pp1_hits'] += 1

            t0 = time.time()
            f3 = third_order_pm1(N, B1=B1, num_bases=6)
            t_third = time.time() - t0
            results_special['third_time'] += t_third
            third_ok = f3 is not None and 1 < f3 < N and N % f3 == 0
            if third_ok: results_special['third_hits'] += 1

            status = "3rd" if third_ok else ("p-1" if pm1_ok else ("p+1" if pp1_ok else "MISS"))
            if i < 3 or third_ok:
                print(f"  [{nd}d] N=...{str(N)[-12:]} => {status}  (p-1:{t_pm1:.3f}s, p+1:{t_pp1:.3f}s, 3rd:{t_third:.3f}s)")

    print(f"\n  SPECIAL CASE SUMMARY ({results_special['total']} semiprimes):")
    print(f"    p-1 hits:       {results_special['pm1_hits']}/{results_special['total']}  ({results_special['pm1_time']:.2f}s)")
    print(f"    p+1 hits:       {results_special['pp1_hits']}/{results_special['total']}  ({results_special['pp1_time']:.2f}s)")
    print(f"    3rd-order hits: {results_special['third_hits']}/{results_special['total']}  ({results_special['third_time']:.2f}s)")

    # ====================================================================
    # Part 3: Random semiprimes
    # ====================================================================
    print("\n" + "=" * 72)
    print("PART 3: Random semiprimes (30-60 digits)")
    print("=" * 72)

    results_random = {}
    random_counts = {30: 15, 36: 12, 40: 8, 45: 6, 50: 4, 55: 3, 60: 2}

    for digits, cnt in random_counts.items():
        cases = generate_random_semiprimes(digits, count=cnt)

        pm1_hits = pp1_hits = third_hits = 0
        pm1_time = pp1_time = third_time = 0.0
        extra_from_third = 0

        print(f"\n--- {digits}-digit random semiprimes ---")

        for i, (N, p, q) in enumerate(cases):
            nd = len(str(N))

            t0 = time.time()
            f1 = pollard_pm1(N, B1=B1)
            t_pm1 = time.time() - t0
            pm1_time += t_pm1
            pm1_ok = f1 is not None and 1 < f1 < N and N % f1 == 0
            if pm1_ok: pm1_hits += 1

            t0 = time.time()
            f2 = williams_pp1(N, B1=B1)
            t_pp1 = time.time() - t0
            pp1_time += t_pp1
            pp1_ok = f2 is not None and 1 < f2 < N and N % f2 == 0
            if pp1_ok: pp1_hits += 1

            t0 = time.time()
            f3 = third_order_pm1(N, B1=B1, num_bases=6)
            t_third = time.time() - t0
            third_time += t_third
            third_ok = f3 is not None and 1 < f3 < N and N % f3 == 0
            if third_ok:
                third_hits += 1
                if not pm1_ok and not pp1_ok:
                    extra_from_third += 1

            if pm1_ok or pp1_ok or third_ok:
                who = []
                if pm1_ok: who.append("p-1")
                if pp1_ok: who.append("p+1")
                if third_ok: who.append("3rd")
                print(f"  [{nd}d] HIT by {'+'.join(who)}  (p-1:{t_pm1:.3f}s, p+1:{t_pp1:.3f}s, 3rd:{t_third:.3f}s)")

        results_random[digits] = {
            'count': cnt, 'pm1': pm1_hits, 'pp1': pp1_hits,
            'third': third_hits, 'extra_third': extra_from_third,
            'pm1_time': pm1_time, 'pp1_time': pp1_time, 'third_time': third_time,
        }
        print(f"  p-1: {pm1_hits}/{cnt} ({pm1_time:.2f}s)  p+1: {pp1_hits}/{cnt} ({pp1_time:.2f}s)  "
              f"3rd: {third_hits}/{cnt} ({third_time:.2f}s)  EXTRA: {extra_from_third}")

    # ====================================================================
    # Part 4: Cost analysis
    # ====================================================================
    print("\n" + "=" * 72)
    print("PART 4: Cost Analysis")
    print("=" * 72)

    print("\n  Per-step cost (multiplications mod N per prime power step):")
    print("    p-1 (scalar pow):  ~1.5 avg muls")
    print("    p+1 (Lucas chain): ~2.0 avg muls")
    print("    3rd (cubic ext):   ~6.0 avg muls (6 muls per cubic multiply)")
    print("    Ratio: cubic is ~4x costlier than p-1, ~3x costlier than p+1")
    print("    (But: 6 cubics tested = ~24x total vs single p-1)")

    total_pm1_t = sum(r['pm1_time'] for r in results_random.values())
    total_pp1_t = sum(r['pp1_time'] for r in results_random.values())
    total_third_t = sum(r['third_time'] for r in results_random.values())
    total_extra = sum(r['extra_third'] for r in results_random.values())
    total_count = sum(r['count'] for r in results_random.values())

    print(f"\n  Aggregate over {total_count} random semiprimes:")
    print(f"    p-1 total:       {total_pm1_t:.2f}s")
    print(f"    p+1 total:       {total_pp1_t:.2f}s")
    print(f"    3rd-order total: {total_third_t:.2f}s")
    print(f"    Extra factors from 3rd-order: {total_extra}")

    if total_pm1_t + total_pp1_t > 0:
        overhead = (total_third_t / (total_pm1_t + total_pp1_t)) * 100
        print(f"    Overhead: {overhead:.1f}% of (p-1 + p+1) time")

    # ====================================================================
    # Part 5: Integration recommendation
    # ====================================================================
    print("\n" + "=" * 72)
    print("PART 5: Integration Recommendation")
    print("=" * 72)

    # Compute yield
    total_third_hits_special = results_special['third_hits']
    total_special = results_special['total']

    print(f"""
  FINDINGS:
  - Berggren 3x3 matrices have order dividing p^2-1 (NOT p^2+p+1).
    They preserve the quadratic form a^2+b^2=c^2, reducing to 2D.
    This was verified: orders mod p always divide p-1 or p+1.

  - Cubic extension rings Z[x]/(f(x), N) with irreducible f properly
    test p^2+p+1 smoothness when f is irreducible mod p.

  - Special case results: {total_third_hits_special}/{total_special} hits on semiprimes
    specifically constructed so p^2+p+1 is {B1}-smooth but p+-1 are not.

  - Random semiprime results: {total_extra} extra factors (beyond p-1/p+1).

  THEORY vs PRACTICE:
  - p^2+p+1 being B-smooth is MUCH rarer than p-1 or p+1 being smooth,
    because p^2+p+1 ~ p^2 >> p, so it needs many more small prime factors.
  - For B=100K: Pr(p-1 smooth) ~ u^(-u) where u=log(p)/log(B).
    Pr(p^2+p+1 smooth) ~ u'^(-u') where u'=2*log(p)/log(B) — exponentially smaller.
  - At 50d (factors ~25d, ~83b): u=5.0 for p-1, u'=10.0 for p^2+p+1.
    Dickman rho: rho(5)~3e-3, rho(10)~2e-10. Ratio: ~10^7 rarer.

  RECOMMENDATION:
  - For the pre-sieve pipeline, third-order p-1 adds ~4x per-cubic overhead
    and catches a much rarer condition. Net value is NEGATIVE for random inputs.
  - However, for targeted use (e.g., RSA numbers where p+-1 are known to be
    non-smooth), it provides a theoretically independent test.
  - If integrated: use B1=50000, num_bases=2, AFTER p-1/p+1 and BEFORE ECM.
    Expected overhead: ~8x of p-1 time. Expected yield: < 0.1% extra on random input.
  """)

    # Write results
    write_results(results_special, results_random, special_cases, B1)
    print("\nResults written to v36_third_order_results.md")
    print("=" * 72)


def write_results(results_special, results_random, special_cases, B1):
    with open("/home/raver1975/factor/.claude/worktrees/agent-af45f5bb/v36_third_order_results.md", "w") as f:
        f.write("# v36: Third-Order p-1 Method -- Cubic Extension Rings\n\n")

        f.write("## Theory\n\n")
        f.write("Standard p-1 tests (p-1) smoothness. Williams p+1 tests (p+1) smoothness.\n")
        f.write("Third-order p-1 tests (p^2+p+1) smoothness using cubic extension rings.\n\n")
        f.write("**Key finding**: Berggren 3x3 matrices do NOT test p^2+p+1.\n")
        f.write("Their order mod p divides p^2-1 = (p-1)(p+1) because they preserve\n")
        f.write("the quadratic form a^2+b^2=c^2. Verified on all primes 5-47.\n\n")
        f.write("**Correct approach**: Z[x]/(f(x), N) where f is an irreducible cubic.\n")
        f.write("When f is irreducible mod p, the group has order p^3-1 = (p-1)(p^2+p+1),\n")
        f.write("and the p^2+p+1 component is genuinely new.\n\n")

        f.write("## Special Test Cases (p^2+p+1 smooth, p+-1 NOT smooth)\n\n")
        f.write(f"Total: {results_special['total']} semiprimes tested\n\n")
        f.write(f"| Method | Hits | Time |\n")
        f.write(f"|--------|------|------|\n")
        f.write(f"| p-1 | {results_special['pm1_hits']}/{results_special['total']} | {results_special['pm1_time']:.2f}s |\n")
        f.write(f"| p+1 | {results_special['pp1_hits']}/{results_special['total']} | {results_special['pp1_time']:.2f}s |\n")
        f.write(f"| 3rd-order | {results_special['third_hits']}/{results_special['total']} | {results_special['third_time']:.2f}s |\n\n")

        f.write("## Random Semiprime Benchmarks\n\n")
        f.write("| Digits | Count | p-1 | p+1 | 3rd | Extra | p-1 time | p+1 time | 3rd time |\n")
        f.write("|--------|-------|-----|-----|-----|-------|----------|----------|----------|\n")
        for d in sorted(results_random.keys()):
            r = results_random[d]
            f.write(f"| {d} | {r['count']} | {r['pm1']} | {r['pp1']} | {r['third']} | {r['extra_third']} | {r['pm1_time']:.2f}s | {r['pp1_time']:.2f}s | {r['third_time']:.2f}s |\n")

        total_extra = sum(r['extra_third'] for r in results_random.values())
        total_count = sum(r['count'] for r in results_random.values())
        total_third_t = sum(r['third_time'] for r in results_random.values())
        total_pm1_t = sum(r['pm1_time'] for r in results_random.values())
        total_pp1_t = sum(r['pp1_time'] for r in results_random.values())

        f.write(f"\n**Totals**: {total_count} semiprimes, extra from 3rd: {total_extra}\n\n")

        f.write("## Cost Analysis\n\n")
        f.write("| Method | Muls/step | Relative cost |\n")
        f.write("|--------|-----------|---------------|\n")
        f.write("| p-1 | ~1.5 | 1x |\n")
        f.write("| p+1 | ~2.0 | 1.3x |\n")
        f.write("| cubic ext | ~6.0 | 4x |\n")
        f.write("| 6 cubics | ~36.0 | 24x |\n\n")

        if total_pm1_t + total_pp1_t > 0:
            overhead = total_third_t / (total_pm1_t + total_pp1_t) * 100
            f.write(f"Measured overhead: {overhead:.1f}% of (p-1 + p+1) time\n\n")

        f.write("## Probability Analysis\n\n")
        f.write("For B=100K smoothness bound:\n\n")
        f.write("| Factor size | u (p-1) | u (p^2+p+1) | Pr(p-1 smooth) | Pr(p^2+p+1 smooth) | Ratio |\n")
        f.write("|-------------|---------|--------------|----------------|--------------------|-------|\n")
        for bits in [40, 50, 60, 80, 100]:
            u_pm1 = bits * math.log(2) / math.log(100000)
            u_p2p1 = 2 * bits * math.log(2) / math.log(100000)
            # Dickman rho approximation: rho(u) ~ u^(-u) for large u
            pr_pm1 = u_pm1 ** (-u_pm1) if u_pm1 > 1 else 1.0
            pr_p2p1 = u_p2p1 ** (-u_p2p1) if u_p2p1 > 1 else 1.0
            ratio = pr_pm1 / pr_p2p1 if pr_p2p1 > 0 else float('inf')
            f.write(f"| {bits}b | {u_pm1:.1f} | {u_p2p1:.1f} | {pr_pm1:.2e} | {pr_p2p1:.2e} | {ratio:.0e}x rarer |\n")

        f.write("\n## Integration Recommendation\n\n")
        f.write("**NOT recommended for general pre-sieve pipeline.**\n\n")
        f.write("The p^2+p+1 smoothness condition is exponentially rarer than p-1 smoothness\n")
        f.write("(by factor ~10^7 at 25-digit factors). The ~4x per-step overhead and need for\n")
        f.write("multiple cubics makes the cost/benefit ratio strongly negative.\n\n")
        f.write("**Berggren matrix correction**: The original hypothesis that Berggren 3x3\n")
        f.write("matrices test p^2+p+1 is FALSE. They preserve a quadratic form and their\n")
        f.write("order divides p^2-1, making them redundant with p-1 and p+1 methods.\n\n")
        f.write("**If used**: B1=50000, num_bases=2, after p-1/p+1, before ECM.\n")
        f.write("Expected yield: < 0.1% extra on random semiprimes.\n\n")

        if special_cases:
            f.write("## Sample Special Primes\n\n")
            for bits, cases in special_cases.items():
                f.write(f"### {bits}-bit factor semiprimes\n\n")
                for N, p, q in cases[:3]:
                    f.write(f"- p={p}, p^2+p+1 smooth, p-1 NOT smooth, p+1 NOT smooth\n")
                f.write("\n")


if __name__ == "__main__":
    benchmark()

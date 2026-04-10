#!/usr/bin/env python3
"""
Lattice-Based Factoring Demonstration

This script demonstrates:
1. Building the factoring lattice for a given n and candidate a
2. Simulating LLL-style lattice reduction to find short vectors
3. Testing short vectors for smoothness
4. The continued fraction factoring approach (CFRAC)
5. Sum-of-squares factoring via the Brahmagupta–Fibonacci identity

Usage:
    python lattice_factoring_demo.py
"""

import math
from fractions import Fraction


def simple_lll_2d(b1, b2):
    """
    Simplified LLL reduction for a 2D lattice with basis vectors b1, b2.
    Returns a reduced basis.
    """
    def dot(u, v):
        return u[0]*v[0] + u[1]*v[1]

    def norm2(v):
        return dot(v, v)

    def sub(u, v):
        return (u[0] - v[0], u[1] - v[1])

    def scale(c, v):
        return (c * v[0], c * v[1])

    # Ensure b1 is the shorter vector
    if norm2(b1) > norm2(b2):
        b1, b2 = b2, b1

    max_iter = 100
    for _ in range(max_iter):
        # Gram-Schmidt coefficient
        mu = dot(b2, b1) / norm2(b1) if norm2(b1) > 0 else 0
        mu_round = round(mu)

        # Size-reduce b2
        b2 = sub(b2, scale(mu_round, b1))

        # Check Lovász condition
        if norm2(b2) >= 0.75 * norm2(b1):
            break

        # Swap
        b1, b2 = b2, b1

    return b1, b2


def factoring_lattice(n, a):
    """
    Build the factoring lattice for n with candidate a.
    Basis: (1, a), (0, n)
    """
    b1 = (1, a % n)
    b2 = (0, n)
    return b1, b2


def is_smooth(m, primes):
    """Check if |m| is B-smooth with given factor base."""
    m = abs(m)
    if m <= 1:
        return m == 1, {}
    factors = {}
    for p in primes:
        while m % p == 0:
            factors[p] = factors.get(p, 0) + 1
            m //= p
    return m == 1, factors


def lattice_factoring_demo(n):
    """Demonstrate lattice-based factoring."""
    print(f"\n{'='*60}")
    print(f"  Lattice-Based Factoring for n = {n}")
    print(f"{'='*60}")

    primes = [p for p in range(2, 50) if all(p % i != 0 for i in range(2, p))]
    print(f"\n  Factor base: {primes[:10]}...")

    smooth_relations = []
    for a in range(2, min(n, 200)):
        b1, b2 = factoring_lattice(n, a)
        rb1, rb2 = simple_lll_2d(b1, b2)

        # Test short vectors
        for vec in [rb1, rb2]:
            x, y = vec
            if y != 0 and x != 0:
                residue = (x * x - (a * a % n) * y * y) % n
                if residue > n // 2:
                    residue -= n
                smooth, factors = is_smooth(residue, primes)
                if smooth and abs(residue) > 1:
                    smooth_relations.append((a, x, y, residue, factors))
                    if len(smooth_relations) <= 10:
                        print(f"\n  a={a}: short vector ({x},{y}), residue={residue}")
                        print(f"    Smooth factorization: {factors}")

        if len(smooth_relations) > len(primes) + 5:
            break

    print(f"\n  Total smooth relations found: {len(smooth_relations)}")
    print(f"  Relations needed: {len(primes) + 1}")
    if len(smooth_relations) > len(primes):
        print(f"  ✓ Enough relations for GF(2) linear algebra!")
    else:
        print(f"  ✗ Need more relations.")


def cfrac_factoring(n, max_steps=100):
    """
    Continued fraction factoring (CFRAC) method.
    Expand √n as a continued fraction and test convergent residues for smoothness.
    """
    print(f"\n{'='*60}")
    print(f"  Continued Fraction Factoring for n = {n}")
    print(f"{'='*60}")

    sqrt_n = math.isqrt(n)
    if sqrt_n * sqrt_n == n:
        print(f"\n  n = {sqrt_n}² is a perfect square!")
        return sqrt_n

    primes = [p for p in range(2, 30) if all(p % i != 0 for i in range(2, p))]
    print(f"\n  Factor base: {primes}")
    print(f"  √{n} ≈ {math.sqrt(n):.6f}")

    # Compute continued fraction expansion of √n
    a0 = sqrt_n
    cf_coeffs = [a0]

    m, d, a = 0, 1, a0
    seen = set()

    # Convergents
    p_prev, p_curr = 1, a0
    q_prev, q_curr = 0, 1

    print(f"\n  {'k':<4} {'aₖ':<6} {'pₖ':<10} {'qₖ':<10} {'pₖ²-nqₖ²':<12} {'Smooth?'}")
    print(f"  {'-'*52}")

    smooth_found = []
    residue = p_curr * p_curr - n * q_curr * q_curr
    smooth, factors = is_smooth(residue, primes)
    marker = f"✓ {factors}" if smooth else ""
    print(f"  {0:<4} {a0:<6} {p_curr:<10} {q_curr:<10} {residue:<12} {marker}")
    if smooth and abs(residue) > 0:
        smooth_found.append((p_curr, q_curr, residue))

    for k in range(1, max_steps):
        m = d * a - m
        d = (n - m * m) // d
        if d == 0:
            break
        a = (a0 + m) // d

        state = (m, d)
        if state in seen:
            break
        seen.add(state)

        cf_coeffs.append(a)

        # Update convergents
        p_prev, p_curr = p_curr, a * p_curr + p_prev
        q_prev, q_curr = q_curr, a * q_curr + q_prev

        residue = p_curr * p_curr - n * q_curr * q_curr
        smooth, factors = is_smooth(residue, primes)
        marker = f"✓ {factors}" if smooth else ""
        if k < 20 or smooth:
            print(f"  {k:<4} {a:<6} {p_curr:<10} {q_curr:<10} {residue:<12} {marker}")
        if smooth and abs(residue) > 0:
            smooth_found.append((p_curr, q_curr, residue))

    print(f"\n  CF coefficients: [{', '.join(str(c) for c in cf_coeffs[:15])}{'...' if len(cf_coeffs) > 15 else ''}]")
    print(f"  Period length: {len(cf_coeffs) - 1}")
    print(f"  Smooth convergents found: {len(smooth_found)}")

    # Try to combine smooth relations
    if len(smooth_found) >= 2:
        print(f"\n  Attempting factor extraction from smooth relations...")
        for i in range(len(smooth_found)):
            for j in range(i + 1, len(smooth_found)):
                p1, q1, r1 = smooth_found[i]
                p2, q2, r2 = smooth_found[j]
                product = r1 * r2
                sqrt_product = math.isqrt(abs(product))
                if sqrt_product * sqrt_product == abs(product):
                    x = (p1 * p2) % n
                    y = sqrt_product % n
                    g = math.gcd(abs(x - y), n)
                    if 1 < g < n:
                        print(f"  ✓ Found factor: gcd(|{x} - {y}|, {n}) = {g}")
                        print(f"    {n} = {g} × {n // g}")
                        return g
    return None


def sum_of_squares_factoring():
    """
    Demonstrate factoring via sum-of-two-squares representations.
    """
    print(f"\n{'='*60}")
    print(f"  Sum of Squares Factoring")
    print(f"{'='*60}")

    def find_sum_of_squares(n, max_search=1000):
        """Find all representations n = a² + b² with a ≤ b."""
        reps = []
        for a in range(0, min(int(math.sqrt(n)) + 1, max_search)):
            b2 = n - a * a
            if b2 < 0:
                break
            b = math.isqrt(b2)
            if b * b == b2 and a <= b:
                reps.append((a, b))
        return reps

    test_cases = [5, 13, 25, 50, 65, 85, 125, 325, 650, 5525]

    for n in test_cases:
        reps = find_sum_of_squares(n)
        if len(reps) >= 2:
            print(f"\n  n = {n}:")
            for a, b in reps:
                print(f"    = {a}² + {b}² = {a**2} + {b**2}")

            # Use first two representations to factor
            a1, b1 = reps[0]
            a2, b2 = reps[1]
            g1 = math.gcd(a1 * a2 + b1 * b2, n)
            g2 = math.gcd(abs(a1 * b2 - b1 * a2), n)

            if 1 < g1 < n:
                print(f"    → gcd({a1*a2+b1*b2}, {n}) = {g1}, so {n} = {g1} × {n//g1}")
            elif 1 < g2 < n:
                print(f"    → gcd({abs(a1*b2-b1*a2)}, {n}) = {g2}, so {n} = {g2} × {n//g2}")
            else:
                print(f"    → GCD methods gave trivial factors")
        elif len(reps) == 1:
            a, b = reps[0]
            print(f"\n  n = {n} = {a}² + {b}² (unique representation → likely prime power)")


def main():
    print(f"╔{'═'*58}╗")
    print(f"║  Hybrid Geometric Factoring — Lattice Methods Demo       ║")
    print(f"╚{'═'*58}╝")

    # Demo 1: Lattice factoring
    lattice_factoring_demo(1003)  # 17 × 59

    # Demo 2: CFRAC
    cfrac_factoring(1073)  # 29 × 37

    # Demo 3: Sum of squares
    sum_of_squares_factoring()

    print(f"\n{'='*60}")
    print(f"  Demo complete!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

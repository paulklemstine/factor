#!/usr/bin/env python3
"""
Representation Density Analysis

Computes and visualizes the number of representations r_k(N) for k = 2, 4, 8
using exact formulas, and analyzes how representation density correlates
with factorability.

The formulas:
  r_2(N) = 4 * sum_{d|N} chi(d)          where chi is the non-principal char mod 4
  r_4(N) = 8 * sum_{d|N, 4∤d} d
  r_8(N) = 16 * sum_{d|N} (-1)^{N+d} * d^3
"""

import math
from collections import defaultdict


def divisors(n: int) -> list:
    """Return all positive divisors of n."""
    divs = []
    for d in range(1, int(math.isqrt(n)) + 1):
        if n % d == 0:
            divs.append(d)
            if d != n // d:
                divs.append(n // d)
    return sorted(divs)


def chi_4(d: int) -> int:
    """Non-principal Dirichlet character mod 4: chi(1)=1, chi(3)=-1, chi(0)=chi(2)=0."""
    r = d % 4
    if r == 1:
        return 1
    elif r == 3:
        return -1
    else:
        return 0


def r2(N: int) -> int:
    """Number of representations of N as a sum of 2 squares (counting signs and order)."""
    return 4 * sum(chi_4(d) for d in divisors(N))


def r4(N: int) -> int:
    """Number of representations of N as a sum of 4 squares."""
    return 8 * sum(d for d in divisors(N) if d % 4 != 0)


def r8(N: int) -> int:
    """Number of representations of N as a sum of 8 squares."""
    return 16 * sum((-1)**(N + d) * d**3 for d in divisors(N))


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def factorize(n: int) -> dict:
    """Return prime factorization as {prime: exponent}."""
    factors = defaultdict(int)
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] += 1
            n //= d
        d += 1
    if n > 1:
        factors[n] += 1
    return dict(factors)


def main():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  REPRESENTATION DENSITY ANALYSIS                       ║")
    print("║  r_k(N) for k = 2, 4, 8                                ║")
    print("╚══════════════════════════════════════════════════════════╝")

    # Table of representation counts
    print(f"\n{'N':>6} | {'Type':>12} | {'r₂(N)':>8} | {'r₄(N)':>8} | {'r₈(N)':>12} | {'Factorization':>20}")
    print(f"{'-'*6}-+-{'-'*12}-+-{'-'*8}-+-{'-'*8}-+-{'-'*12}-+-{'-'*20}")

    for N in range(1, 51):
        factors = factorize(N)
        if is_prime(N):
            ntype = f"prime({N%4}mod4)"
        elif len(factors) == 1:
            p, e = list(factors.items())[0]
            ntype = f"p^{e}"
        else:
            ntype = "composite"

        fstr = " × ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(factors.items()))
        r2v = r2(N)
        r4v = r4(N)
        r8v = r8(N)
        print(f"{N:>6} | {ntype:>12} | {r2v:>8} | {r4v:>8} | {r8v:>12} | {fstr:>20}")

    # Analysis: primes mod 4
    print(f"\n{'='*60}")
    print(f"  ANALYSIS: Primes by residue class mod 4")
    print(f"{'='*60}")

    print(f"\n  Primes ≡ 1 (mod 4): representable as sum of 2 squares")
    for p in [5, 13, 17, 29, 37, 41]:
        if is_prime(p):
            print(f"    p = {p}: r₂ = {r2(p)}, r₄ = {r4(p)}, r₈ = {r8(p)}")

    print(f"\n  Primes ≡ 3 (mod 4): NOT representable as sum of 2 squares")
    for p in [3, 7, 11, 19, 23, 31]:
        if is_prime(p):
            print(f"    p = {p}: r₂ = {r2(p)}, r₄ = {r4(p)}, r₈ = {r8(p)}")

    # Collision analysis for composites
    print(f"\n{'='*60}")
    print(f"  COLLISION ANALYSIS: Composites with multiple representations")
    print(f"{'='*60}")

    print(f"\n  Products of two primes ≡ 1 (mod 4):")
    for p, q in [(5, 13), (5, 17), (13, 17), (5, 29), (13, 29)]:
        N = p * q
        r = r2(N)
        essentially_distinct = r // 8 if r > 0 else 0
        print(f"    {p}×{q} = {N}: r₂ = {r}, essentially distinct = {essentially_distinct}")

    print(f"\n  Products of two primes ≡ 3 (mod 4):")
    for p, q in [(3, 7), (3, 11), (7, 11), (3, 19), (7, 19)]:
        N = p * q
        r = r2(N)
        print(f"    {p}×{q} = {N}: r₂ = {r} (product is ≡ 1 mod 4, so representable!)")

    # Modular form connection
    print(f"\n{'='*60}")
    print(f"  MODULAR FORM CONNECTION")
    print(f"{'='*60}")
    print(f"\n  The theta function Θ_k(q) = Σ r_k(n) q^n is a modular form")
    print(f"  of weight k/2 for the group Γ₀(4).")
    print(f"\n  Coefficients encode divisor structure:")
    print(f"    r₂(N) depends on χ₄-twisted divisor sum")
    print(f"    r₄(N) depends on divisors not divisible by 4")
    print(f"    r₈(N) depends on cubed divisor sum")
    print(f"\n  Key insight: knowing r_k(N) reveals divisor information,")
    print(f"  but computing r_k(N) exactly requires the factorization!")


if __name__ == "__main__":
    main()

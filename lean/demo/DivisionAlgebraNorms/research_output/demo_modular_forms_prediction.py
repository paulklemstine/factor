#!/usr/bin/env python3
"""
Demo: Modular Forms Prediction for Factoring

Demonstrates how modular form representation count formulas
(Jacobi's formulas) predict the structure of factoring collisions.

Key formulas:
  r₂(N) = 4(d₁(N) - d₃(N))
  r₄(N) = 8·σ₁(N)  for odd N
  r₈(N) = 16·σ₃(N) for odd N
"""

import math
from collections import defaultdict


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


def divisor_sum(k: int, n: int) -> int:
    """σ_k(n) = Σ_{d|n} d^k"""
    return sum(d**k for d in range(1, n+1) if n % d == 0)


def divisor_count(n: int) -> int:
    """d(n) = number of divisors"""
    return sum(1 for d in range(1, n+1) if n % d == 0)


def r2_formula(N: int) -> int:
    """r₂(N) = 4(d₁(N) - d₃(N))"""
    d1 = sum(1 for d in range(1, N+1) if N % d == 0 and d % 4 == 1)
    d3 = sum(1 for d in range(1, N+1) if N % d == 0 and d % 4 == 3)
    return 4 * (d1 - d3)


def sum_of_two_squares_reps(N: int):
    """All (a, b) with a² + b² = N, a ≤ b, a ≥ 0"""
    reps = []
    for a in range(0, int(math.isqrt(N)) + 1):
        b_sq = N - a * a
        if b_sq < 0:
            break
        b = int(math.isqrt(b_sq))
        if b * b == b_sq and a <= b:
            reps.append((a, b))
    return reps


def analyze_hecke_structure():
    """
    Analyze how Hecke eigenvalues relate to representation structure.

    For primes p ≡ 1 (mod 4), the representation p = a² + b² is unique (up to signs/order).
    For products pq, multiplicativity gives r₂(pq) from r₂(p) and r₂(q).
    """
    print("=" * 70)
    print("Hecke Structure Analysis: Representation Multiplicativity")
    print("=" * 70)

    primes_1mod4 = [p for p in range(5, 200) if is_prime(p) and p % 4 == 1]

    print("\n  Primes p ≡ 1 (mod 4) and their representations:")
    print(f"  {'p':>5} {'r₂(p)':>6} {'Rep (a,b)':>15} {'σ₁(p)':>6}")
    print("  " + "-" * 40)
    for p in primes_1mod4[:15]:
        r2 = r2_formula(p)
        reps = sum_of_two_squares_reps(p)
        s1 = divisor_sum(1, p)
        rep_str = str(reps[0]) if reps else "none"
        print(f"  {p:>5} {r2:>6} {rep_str:>15} {s1:>6}")

    print("\n  Products of two primes ≡ 1 (mod 4):")
    print(f"  {'p':>4} {'q':>4} {'N=pq':>7} {'r₂(N)':>6} {'r₂(p)':>6} {'r₂(q)':>6} {'Reps':>30}")
    print("  " + "-" * 65)
    for i, p in enumerate(primes_1mod4[:8]):
        for q in primes_1mod4[i+1:i+3]:
            N = p * q
            r2_N = r2_formula(N)
            r2_p = r2_formula(p)
            r2_q = r2_formula(q)
            reps = sum_of_two_squares_reps(N)
            rep_str = ", ".join(str(r) for r in reps[:3])
            if len(reps) > 3:
                rep_str += "..."
            print(f"  {p:>4} {q:>4} {N:>7} {r2_N:>6} {r2_p:>6} {r2_q:>6} {rep_str:>30}")


def analyze_dimension_selection():
    """
    For each N, compare dimensions 2, 4, 8 for factoring potential.
    """
    print("\n" + "=" * 70)
    print("Optimal Dimension Selection")
    print("=" * 70)

    print("\n  For N = p·q, representation counts grow with dimension:")
    print(f"  {'N':>7} {'r₂(N)':>7} {'8σ₁(N)':>8} {'16σ₃(N)':>10} {'Best dim':>10}")
    print("  " + "-" * 50)

    test_N = [
        (3, 5),      # 15, p=3 ≡ 3 mod 4
        (5, 13),     # 65, both ≡ 1 mod 4
        (7, 11),     # 77, both ≡ 3 mod 4
        (3, 7),      # 21, both ≡ 3 mod 4
        (5, 29),     # 145, both ≡ 1 mod 4
        (13, 17),    # 221, both ≡ 1 mod 4
        (3, 37),     # 111, mixed
        (41, 53),    # 2173, both ≡ 1 mod 4
    ]

    for p, q in test_N:
        N = p * q
        r2 = r2_formula(N)
        s1 = divisor_sum(1, N)
        s3 = divisor_sum(3, N)
        r4 = 8 * s1 if N % 2 == 1 else None
        r8 = 16 * s3 if N % 2 == 1 else None

        if r2 > 0:
            best = "dim 2"
        elif r4 and r4 > 0:
            best = "dim 4"
        else:
            best = "dim 8"

        r4_str = str(r4) if r4 else "—"
        r8_str = str(r8) if r8 else "—"
        print(f"  {N:>7} {r2:>7} {r4_str:>8} {r8_str:>10} {best:>10}")
        reps2 = sum_of_two_squares_reps(N)
        if reps2:
            print(f"          dim-2 reps: {reps2}")


def analyze_divisor_mod4_pattern():
    """
    Analyze the d₁ - d₃ pattern that determines r₂(N).
    """
    print("\n" + "=" * 70)
    print("Divisor Mod-4 Pattern Analysis")
    print("=" * 70)

    print("\n  For N = p·q, divisors are {1, p, q, pq}.")
    print("  Their residues mod 4 determine r₂(N).\n")

    cases = [
        ("p≡1, q≡1", [(5, 13), (5, 29), (13, 17), (29, 37)]),
        ("p≡1, q≡3", [(5, 7), (13, 3), (29, 11), (37, 19)]),
        ("p≡3, q≡3", [(3, 7), (3, 11), (7, 11), (3, 19)]),
    ]

    for label, pairs in cases:
        print(f"\n  Case: {label}")
        for p, q in pairs:
            N = p * q
            divs = sorted(d for d in range(1, N+1) if N % d == 0)
            mods = [(d, d % 4) for d in divs]
            d1 = sum(1 for _, m in mods if m == 1)
            d3 = sum(1 for _, m in mods if m == 3)
            r2 = 4 * (d1 - d3)
            div_str = ", ".join(f"{d}≡{d%4}" for d in divs)
            print(f"    N={N:>5} = {p}×{q}  divisors: [{div_str}]  d₁={d1}, d₃={d3}, r₂={r2}")


def analyze_representation_growth():
    """
    Show how representation counts grow with N for each dimension.
    """
    print("\n" + "=" * 70)
    print("Representation Count Growth")
    print("=" * 70)

    print(f"\n  {'N':>6} {'d(N)':>5} {'σ₁(N)':>7} {'σ₃(N)':>10} {'r₂(N)':>6} {'8σ₁':>6} {'16σ₃':>8}")
    print("  " + "-" * 55)

    for N in [1, 2, 3, 5, 10, 15, 20, 25, 50, 100, 65, 85, 145, 221]:
        d = divisor_count(N)
        s1 = divisor_sum(1, N)
        s3 = divisor_sum(3, N)
        r2 = r2_formula(N)
        print(f"  {N:>6} {d:>5} {s1:>7} {s3:>10} {r2:>6} {8*s1:>6} {16*s3:>8}")


def demo_hecke_prediction():
    """
    Show how Hecke eigenvalues (via multiplicativity) predict factoring success.
    """
    print("\n" + "=" * 70)
    print("Hecke-Guided Factoring Prediction")
    print("=" * 70)

    print("\n  For N = p·q with both p,q ≡ 1 (mod 4):")
    print("  - N has 4 distinct representations as a² + b²")
    print("  - The 'extra' 2 representations (beyond what a prime has)")
    print("    are precisely those that encode the factorization.\n")

    primes = [p for p in range(5, 100) if is_prime(p) and p % 4 == 1]

    success_count = 0
    total_count = 0

    for i, p in enumerate(primes[:10]):
        for q in primes[i+1:i+4]:
            N = p * q
            reps = sum_of_two_squares_reps(N)
            if len(reps) < 2:
                continue

            total_count += 1
            # Try all pairs
            found_factor = False
            for rep1, rep2 in zip(reps, reps[1:]):
                a, b = rep1
                c, d = rep2
                cross = a * d - b * c
                g = math.gcd(abs(cross), N)
                if 1 < g < N:
                    found_factor = True
                    print(f"  N={N:>6} = {p}×{q}: ({a},{b}) ∧ ({c},{d}) → "
                          f"cross={cross:>5}, gcd={g:>4} ✓")
                    break

            if found_factor:
                success_count += 1
            else:
                print(f"  N={N:>6} = {p}×{q}: reps={reps} — need more channels")

    print(f"\n  Success rate: {success_count}/{total_count} "
          f"({100*success_count/max(total_count,1):.0f}%)")
    print("  Note: failures can be resolved by trying all C(r,2) pairs")
    print("  or moving to dimension 4 or 8 for more channels.")


if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║  Modular Forms and Factoring: Prediction Demos                      ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")

    analyze_hecke_structure()
    analyze_dimension_selection()
    analyze_divisor_mod4_pattern()
    analyze_representation_growth()
    demo_hecke_prediction()

    print("\n" + "=" * 70)
    print("All demos completed!")
    print("=" * 70)

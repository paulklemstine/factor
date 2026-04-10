#!/usr/bin/env python3
"""
The Quadruple-Quintuple Bridge

Explores the "dimension leak" when composing two sums of 3 squares:
- Product of two sums of 3 squares → sum of 4 squares (not necessarily 3)
- This bridges quadruple factoring to quintuple/higher-dimensional structures

Demonstrates:
1. Euler's four-square identity applied to 3-square inputs
2. When the product stays as 3 squares vs. needs 4
3. The factoring cascade: quadruples → quintuples → E₈
"""

from math import isqrt, gcd
from itertools import combinations


def is_sum_of_3_squares(N):
    """Check if N = a² + b² + c² is possible."""
    if N < 0:
        return False
    if N == 0:
        return True
    m = N
    while m % 4 == 0:
        m //= 4
    return m % 8 != 7


def find_3sq_reps(N):
    """Find all representations of N as a sum of 3 non-negative squares."""
    reps = []
    for a in range(0, isqrt(N) + 1):
        for b in range(a, isqrt(N - a**2) + 1):
            rem = N - a**2 - b**2
            if rem < b**2:
                break
            c = isqrt(rem)
            if c >= b and c * c == rem:
                reps.append((a, b, c))
    return reps


def find_4sq_reps(N):
    """Find all representations of N as a sum of 4 non-negative squares."""
    reps = []
    for a in range(0, isqrt(N) + 1):
        for b in range(a, isqrt(N - a**2) + 1):
            for c in range(b, isqrt(N - a**2 - b**2) + 1):
                rem = N - a**2 - b**2 - c**2
                if rem < c**2:
                    break
                d = isqrt(rem)
                if d >= c and d * d == rem:
                    reps.append((a, b, c, d))
    return reps


def euler_compose(a1, a2, a3, b1, b2, b3):
    """
    Compose two sums of 3 squares using Euler's identity (embedding as 4-squares with 4th = 0).
    (a₁²+a₂²+a₃²)(b₁²+b₂²+b₃²) = c₁²+c₂²+c₃²+c₄²
    """
    # Treat as (a1,a2,a3,0) × (b1,b2,b3,0)
    c1 = a1*b1 - a2*b2 - a3*b3
    c2 = a1*b2 + a2*b1
    c3 = a1*b3 + a3*b1
    c4 = a2*b3 - a3*b2
    return (c1, c2, c3, c4)


def demo_dimension_leak():
    """Show when products of 3-square sums stay as 3 squares vs. need 4."""
    print("=" * 60)
    print("THE DIMENSION LEAK: 3-SQUARES → 4-SQUARES")
    print("=" * 60)

    stays_3 = 0
    needs_4 = 0
    examples_needs_4 = []

    for M in range(1, 30):
        if not is_sum_of_3_squares(M):
            continue
        for N in range(M, 30):
            if not is_sum_of_3_squares(N):
                continue

            product = M * N
            is_3sq = is_sum_of_3_squares(product)

            if is_3sq:
                stays_3 += 1
            else:
                needs_4 += 1
                if len(examples_needs_4) < 10:
                    examples_needs_4.append((M, N, product))

    print(f"\n  Products of pairs (M,N) with M,N ≤ 29, both sums of 3 squares:")
    print(f"    Product is sum of 3 squares: {stays_3}")
    print(f"    Product needs 4 squares:     {needs_4}")
    print(f"    Leak rate: {100*needs_4/(stays_3+needs_4):.1f}%")

    if examples_needs_4:
        print(f"\n  Examples where product needs 4 squares:")
        for M, N, P in examples_needs_4:
            reps_M = find_3sq_reps(M)
            reps_N = find_3sq_reps(N)
            reps_P = find_4sq_reps(P)
            print(f"    {M} × {N} = {P}")
            if reps_M:
                print(f"      {M} = {reps_M[0][0]}²+{reps_M[0][1]}²+{reps_M[0][2]}²")
            if reps_N:
                print(f"      {N} = {reps_N[0][0]}²+{reps_N[0][1]}²+{reps_N[0][2]}²")
            if reps_P:
                r = reps_P[0]
                print(f"      {P} = {r[0]}²+{r[1]}²+{r[2]}²+{r[3]}²")
            print(f"      4^a(8b+7) form of {P}: ", end="")
            m = P
            a = 0
            while m % 4 == 0:
                m //= 4
                a += 1
            print(f"4^{a}×{m}, {m} mod 8 = {m%8}")
    print()


def demo_euler_composition():
    """Show Euler's four-square composition of 3-square inputs."""
    print("=" * 60)
    print("EULER COMPOSITION: 3-SQUARES × 3-SQUARES → 4-SQUARES")
    print("=" * 60)

    examples = [
        ((1, 1, 1), (1, 1, 1)),  # 3 × 3 = 9
        ((1, 1, 2), (1, 2, 3)),  # 6 × 14 = 84
        ((1, 2, 3), (2, 3, 4)),  # 14 × 29 = 406
        ((1, 1, 1), (1, 2, 2)),  # 3 × 9 = 27
    ]

    for (a1, a2, a3), (b1, b2, b3) in examples:
        M = a1**2 + a2**2 + a3**2
        N = b1**2 + b2**2 + b3**2
        P = M * N

        c1, c2, c3, c4 = euler_compose(a1, a2, a3, b1, b2, b3)
        verify = c1**2 + c2**2 + c3**2 + c4**2

        print(f"\n  ({a1}²+{a2}²+{a3}²) × ({b1}²+{b2}²+{b3}²) = {M} × {N} = {P}")
        print(f"  Euler composition: {c1}² + {c2}² + {c3}² + {c4}²")
        print(f"  = {c1**2} + {c2**2} + {c3**2} + {c4**2} = {verify}")
        print(f"  Correct: {P == verify} {'✓' if P == verify else '✗'}")
        print(f"  Is {P} a sum of 3 squares? {is_sum_of_3_squares(P)}")
    print()


def demo_factoring_cascade():
    """Demonstrate the factoring cascade: quadruples → quintuples → E₈."""
    print("=" * 60)
    print("FACTORING CASCADE: QUADRUPLES → QUINTUPLES → E₈")
    print("=" * 60)

    print("\n  Level 0: Start with N = 1001 = 7 × 11 × 13")
    N = 1001

    print(f"\n  Level 1 — Quadruple search (sum of 3 squares):")
    if is_sum_of_3_squares(N):
        reps = find_3sq_reps(N)
        print(f"    {N} has {len(reps)} representations as sum of 3 squares")
        for r in reps[:5]:
            print(f"    {r[0]}² + {r[1]}² + {r[2]}² = {r[0]**2+r[1]**2+r[2]**2}")
            # Peel channels
            d = isqrt(N)
            if d * d != N:
                d += 1
    else:
        print(f"    {N} is NOT a sum of 3 squares (form 4^a(8b+7))")
        print(f"    → Must use 4-square representation (quintuple level)")

    print(f"\n  Level 2 — Quintuple (sum of 4 squares, always exists by Lagrange):")
    reps4 = find_4sq_reps(N)
    print(f"    {N} has {len(reps4)} representations as sum of 4 squares")
    for r in reps4[:5]:
        print(f"    {r[0]}² + {r[1]}² + {r[2]}² + {r[3]}² = {sum(x**2 for x in r)}")

    if len(reps4) >= 2:
        print(f"\n    Collision between first two representations:")
        r1, r2 = reps4[0], reps4[1]
        for i in range(4):
            diff = abs(r1[i] - r2[i])
            if diff > 0:
                g = gcd(diff, N)
                if 1 < g < N:
                    print(f"      gcd(|{r1[i]} - {r2[i]}|, {N}) = gcd({diff}, {N}) = {g} ← FACTOR!")
                else:
                    print(f"      gcd(|{r1[i]} - {r2[i]}|, {N}) = gcd({diff}, {N}) = {g}")

    print(f"\n  Level 3 — E₈ (sum of 8 squares):")
    # Simple: duplicate the 4-square representation
    if reps4:
        r = reps4[0]
        print(f"    Embedding: ({r[0]}, {r[1]}, {r[2]}, {r[3]}, 0, 0, 0, 0)")
        print(f"    Norm² = {sum(x**2 for x in r)} = {N}")
        print(f"    240 E₈ neighbours available for collision search")
        print(f"    28 cross-collision channels per neighbour pair")
        print(f"    Total potential channels: {240 * 28}")

    print()

    # Channel count comparison
    print("  CHANNEL COUNT COMPARISON:")
    print("  " + "-" * 50)
    levels = [
        ("Triples (k=2)", 2),
        ("Quadruples (k=3)", 3),
        ("Quintuples (k=4)", 4),
        ("E₈ (k=8)", 8),
    ]
    print(f"  {'Level':<20} | {'Peel':>5} | {'Cross':>5} | {'GCD':>5} | {'Total':>5}")
    print("  " + "-" * 50)
    for name, k in levels:
        peel = k
        cross = k * (k - 1) // 2
        gcd_ch = k
        total = peel + cross + gcd_ch
        print(f"  {name:<20} | {peel:>5} | {cross:>5} | {gcd_ch:>5} | {total:>5}")
    print()


def main():
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  QUADRUPLE-QUINTUPLE BRIDGE — DEMO                     ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()

    demo_dimension_leak()
    demo_euler_composition()
    demo_factoring_cascade()

    print("All demos completed successfully!")


if __name__ == "__main__":
    main()

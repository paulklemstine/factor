#!/usr/bin/env python3
"""
Division Algebra Norm Factoring — Interactive Demo

Demonstrates factoring integers through sum-of-squares representations
in dimensions 2, 4, and 8 (complex, quaternion, octonion norms).

Key algorithms:
  1. Find sum-of-k-squares representations
  2. Detect collisions between representations
  3. Extract factors via GCD cascade
"""

import math
import random
from itertools import combinations
from typing import List, Tuple, Optional


# ============================================================
# SECTION 1: Sum-of-Squares Representations
# ============================================================

def sum_of_2_squares(n: int) -> List[Tuple[int, int]]:
    """Find all representations of n as a² + b² with 0 ≤ a ≤ b."""
    reps = []
    a = 0
    while a * a <= n // 2:
        b_sq = n - a * a
        b = int(math.isqrt(b_sq))
        if b * b == b_sq and a <= b:
            reps.append((a, b))
        a += 1
    return reps


def sum_of_4_squares(n: int) -> List[Tuple[int, int, int, int]]:
    """Find representations of n as a² + b² + c² + d² with a ≤ b ≤ c ≤ d."""
    reps = []
    for a in range(int(math.isqrt(n)) + 1):
        if a * a > n:
            break
        for b in range(a, int(math.isqrt(n - a * a)) + 1):
            if a * a + b * b > n:
                break
            for c in range(b, int(math.isqrt(n - a * a - b * b)) + 1):
                d_sq = n - a * a - b * b - c * c
                if d_sq < c * c:
                    continue
                d = int(math.isqrt(d_sq))
                if d * d == d_sq:
                    reps.append((a, b, c, d))
    return reps


# ============================================================
# SECTION 2: Collision-Based Factoring
# ============================================================

def factor_via_collision_dim2(n: int) -> Optional[int]:
    """
    Factor n using collisions between sum-of-2-squares representations.
    If n = a² + b² = c² + d², compute gcd(ad - bc, n).
    """
    reps = sum_of_2_squares(n)
    if len(reps) < 2:
        return None

    for (a, b), (c, d) in combinations(reps, 2):
        cross = a * d - b * c
        g = math.gcd(abs(cross), n)
        if 1 < g < n:
            return g
        # Also try the other cross-product
        cross2 = a * c + b * d
        g2 = math.gcd(abs(cross2), n)
        if 1 < g2 < n:
            return g2
    return None


def factor_via_collision_dim4(n: int, max_reps: int = 20) -> Optional[int]:
    """
    Factor n using collisions between sum-of-4-squares representations.
    More channels per collision → higher success rate.
    """
    reps = sum_of_4_squares(n)[:max_reps]
    if len(reps) < 2:
        return None

    for r1, r2 in combinations(reps, 2):
        # Try all pairs of components as cross-products
        for i in range(4):
            for j in range(4):
                if i == j:
                    continue
                cross = r1[i] * r2[j] - r1[j] * r2[i]
                if cross == 0:
                    continue
                g = math.gcd(abs(cross), n)
                if 1 < g < n:
                    return g
    return None


def peel_factor(n: int, rep: tuple) -> Optional[int]:
    """
    Try to extract a factor using the peel identity.
    For each component a in the representation,
    compute gcd(n - a, n) and gcd(n + a, n).
    """
    for a in rep:
        if a == 0:
            continue
        for val in [n - a, n + a, n - a * a, n + a * a]:
            g = math.gcd(abs(val), n)
            if 1 < g < n:
                return g
    return None


# ============================================================
# SECTION 3: The Full Hierarchy
# ============================================================

def factor_hierarchy(n: int) -> dict:
    """
    Attempt to factor n using all dimensional levels.
    Returns a report of what each dimension reveals.
    """
    report = {
        'n': n,
        'dim1': {'representation': n, 'factor': None},
        'dim2': {'representations': [], 'collisions': 0, 'factor': None},
        'dim4': {'representations': [], 'collisions': 0, 'factor': None},
    }

    # Dimension 2
    reps2 = sum_of_2_squares(n)
    report['dim2']['representations'] = reps2
    report['dim2']['representation_count'] = len(reps2)
    if len(reps2) >= 2:
        report['dim2']['collisions'] = len(reps2) * (len(reps2) - 1) // 2
        report['dim2']['factor'] = factor_via_collision_dim2(n)

    # Dimension 4
    reps4 = sum_of_4_squares(n)[:10]  # limit for display
    report['dim4']['representations'] = reps4
    report['dim4']['representation_count'] = len(reps4)
    if len(reps4) >= 2:
        report['dim4']['collisions'] = 10 * len(reps4) * (len(reps4) - 1) // 2
        report['dim4']['factor'] = factor_via_collision_dim4(n)

    return report


# ============================================================
# SECTION 4: Brahmagupta-Fibonacci Verification
# ============================================================

def verify_brahmagupta(a, b, c, d):
    """Verify the Brahmagupta-Fibonacci identity."""
    lhs = (a**2 + b**2) * (c**2 + d**2)
    rhs1 = (a*c - b*d)**2 + (a*d + b*c)**2
    rhs2 = (a*c + b*d)**2 + (a*d - b*c)**2
    return lhs == rhs1 == rhs2


def verify_collision_norm(a, b, c, d, n):
    """Verify: if a²+b² = c²+d² = N, then (ad-bc)²+(ac+bd)² = N²."""
    if a**2 + b**2 != n or c**2 + d**2 != n:
        return False
    return (a*d - b*c)**2 + (a*c + b*d)**2 == n**2


# ============================================================
# SECTION 5: Euler Four-Square Identity Verification
# ============================================================

def quaternion_multiply(a, b):
    """Multiply two quaternions (as 4-tuples)."""
    a1, a2, a3, a4 = a
    b1, b2, b3, b4 = b
    return (
        a1*b1 - a2*b2 - a3*b3 - a4*b4,
        a1*b2 + a2*b1 + a3*b4 - a4*b3,
        a1*b3 - a2*b4 + a3*b1 + a4*b2,
        a1*b4 + a2*b3 - a3*b2 + a4*b1,
    )


def qnorm(q):
    """Quaternion norm (sum of squares)."""
    return sum(x**2 for x in q)


def verify_euler_identity(a, b):
    """Verify: N(a)*N(b) = N(a*b) for quaternions."""
    product = quaternion_multiply(a, b)
    return qnorm(a) * qnorm(b) == qnorm(product)


# ============================================================
# MAIN DEMO
# ============================================================

def main():
    print("=" * 70)
    print("DIVISION ALGEBRA NORM FACTORING — INTERACTIVE DEMO")
    print("=" * 70)

    # Demo 1: Brahmagupta-Fibonacci Identity
    print("\n" + "─" * 70)
    print("DEMO 1: Brahmagupta-Fibonacci Identity (Dimension 2)")
    print("─" * 70)
    for a, b, c, d in [(3, 4, 1, 2), (5, 12, 3, 4), (7, 1, 2, 3)]:
        n = (a**2 + b**2) * (c**2 + d**2)
        r1 = (a*c - b*d, a*d + b*c)
        r2 = (a*c + b*d, a*d - b*c)
        ok = verify_brahmagupta(a, b, c, d)
        print(f"  ({a}²+{b}²)·({c}²+{d}²) = {n}")
        print(f"    = {r1[0]}² + {r1[1]}² = {r1[0]**2 + r1[1]**2}")
        print(f"    = {r2[0]}² + {r2[1]}² = {r2[0]**2 + r2[1]**2}")
        print(f"    Identity verified: {ok}")

    # Demo 2: Collision-Based Factoring (Dim 2)
    print("\n" + "─" * 70)
    print("DEMO 2: Collision-Based Factoring (Dimension 2)")
    print("─" * 70)
    test_composites = [65, 85, 145, 221, 325, 377, 1105, 8125]
    for n in test_composites:
        reps = sum_of_2_squares(n)
        if len(reps) >= 2:
            factor = factor_via_collision_dim2(n)
            print(f"\n  N = {n}")
            print(f"    Representations: {reps}")
            if factor:
                print(f"    ✅ Factor found via collision: {factor} × {n // factor} = {n}")
                # Verify collision-norm identity
                a, b = reps[0]
                c, d = reps[1]
                cnv = verify_collision_norm(a, b, c, d, n)
                print(f"    Collision-norm identity (ad-bc)²+(ac+bd)²=N²: {cnv}")
            else:
                print(f"    ❌ No nontrivial GCD found")

    # Demo 3: Quaternion Norm Multiplicativity
    print("\n" + "─" * 70)
    print("DEMO 3: Quaternion Norm Multiplicativity (Dimension 4)")
    print("─" * 70)
    q1 = (1, 2, 3, 4)
    q2 = (5, 6, 7, 8)
    prod = quaternion_multiply(q1, q2)
    print(f"  q₁ = {q1}, N(q₁) = {qnorm(q1)}")
    print(f"  q₂ = {q2}, N(q₂) = {qnorm(q2)}")
    print(f"  q₁·q₂ = {prod}, N(q₁·q₂) = {qnorm(prod)}")
    print(f"  N(q₁)·N(q₂) = {qnorm(q1) * qnorm(q2)}")
    print(f"  Verified: N(q₁·q₂) = N(q₁)·N(q₂)? {verify_euler_identity(q1, q2)}")

    # Demo 4: Dimension-4 Factoring
    print("\n" + "─" * 70)
    print("DEMO 4: Dimension-4 Factoring (Quaternion Collisions)")
    print("─" * 70)
    test_hard = [91, 119, 143, 187, 221, 299, 403, 667, 1001, 1517, 2021]
    for n in test_hard:
        reps4 = sum_of_4_squares(n)[:5]
        factor = factor_via_collision_dim4(n)
        print(f"\n  N = {n}")
        print(f"    Sum-of-4-sq reps (first 5): {reps4}")
        if factor:
            print(f"    ✅ Factor via dim-4 collision: {factor} × {n // factor} = {n}")
        else:
            # Try peel identity
            for rep in reps4:
                pf = peel_factor(n, rep)
                if pf:
                    print(f"    ✅ Factor via peel identity: {pf} × {n // pf} = {n}")
                    break
            else:
                print(f"    ❌ No factor found (try more representations)")

    # Demo 5: The Full Hierarchy
    print("\n" + "─" * 70)
    print("DEMO 5: Full Dimensional Hierarchy Report")
    print("─" * 70)
    for n in [65, 325, 1001, 1105]:
        report = factor_hierarchy(n)
        print(f"\n  N = {n}")
        print(f"    Dim 2: {report['dim2']['representation_count']} reps, "
              f"{report['dim2']['collisions']} collisions → "
              f"factor = {report['dim2']['factor']}")
        print(f"    Dim 4: {report['dim4']['representation_count']} reps, "
              f"{report['dim4']['collisions']} collisions → "
              f"factor = {report['dim4']['factor']}")

    # Demo 6: Channel Count Comparison
    print("\n" + "─" * 70)
    print("DEMO 6: Factoring Channels by Dimension")
    print("─" * 70)
    print(f"  {'Dim':>4} | {'Channels/Rep':>13} | {'Cross-pairs (2 reps)':>20} | {'Cross-pairs (5 reps)':>20}")
    print(f"  {'─'*4}-+-{'─'*13}-+-{'─'*20}-+-{'─'*20}")
    for k in [1, 2, 4, 8]:
        from math import comb
        cross2 = k * comb(2, 2)
        cross5 = k * comb(5, 2)
        print(f"  {k:>4} | {k:>13} | {cross2:>20} | {cross5:>20}")


if __name__ == '__main__':
    main()

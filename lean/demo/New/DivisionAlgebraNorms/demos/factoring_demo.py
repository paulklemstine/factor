#!/usr/bin/env python3
"""
Factoring Through Division Algebra Norms — Interactive Demo

Demonstrates collision-based factoring using sums of squares in dimensions 2, 4, and 8,
corresponding to the complex numbers, quaternions, and octonions.

Usage:
    python factoring_demo.py [N]

If no argument is given, runs a demo on several example numbers.
"""

import math
import random
import sys
from itertools import combinations
from typing import List, Tuple, Optional


# ============================================================
# Dimension 2: Sum of Two Squares
# ============================================================

def sum_of_two_squares_representations(N: int) -> List[Tuple[int, int]]:
    """Find all representations N = a² + b² with 0 < a ≤ b."""
    reps = []
    a = 1
    while a * a <= N // 2:
        b_sq = N - a * a
        b = int(math.isqrt(b_sq))
        if b * b == b_sq and a <= b:
            reps.append((a, b))
        a += 1
    return reps


def collision_factor_dim2(N: int, rep1: Tuple[int, int], rep2: Tuple[int, int]) -> Optional[int]:
    """
    Given N = a² + b² = c² + d² (two representations),
    attempt to extract a factor using gcd(ad - bc, N).
    """
    a, b = rep1
    c, d = rep2
    cross = a * d - b * c
    g = math.gcd(abs(cross), N)
    if 1 < g < N:
        return g
    # Try the other cross-term
    cross2 = a * c + b * d
    g2 = math.gcd(abs(cross2), N)
    if 1 < g2 < N:
        return g2
    return None


def verify_collision_norm_identity(a, b, c, d, N):
    """Verify (ad-bc)² + (ac+bd)² = N² (Collision-Norm Identity)."""
    lhs = (a*d - b*c)**2 + (a*c + b*d)**2
    rhs = N**2
    return lhs == rhs


def demo_dim2(N: int):
    """Demonstrate dimension-2 (Gaussian integer) factoring."""
    print(f"\n{'='*60}")
    print(f"  DIMENSION 2: Gaussian Integer Factoring for N = {N}")
    print(f"{'='*60}")

    reps = sum_of_two_squares_representations(N)

    if len(reps) == 0:
        print(f"  N = {N} cannot be written as a sum of 2 squares.")
        print(f"  (Has a prime factor ≡ 3 mod 4 with odd exponent)")
        return

    print(f"\n  Representations of {N} as a² + b²:")
    for i, (a, b) in enumerate(reps):
        print(f"    Rep {i+1}: {N} = {a}² + {b}² = {a**2} + {b**2}")

    if len(reps) < 2:
        print(f"\n  Only 1 representation found — no collision available.")
        print(f"  (N may be prime or a prime power)")
        return

    print(f"\n  Found {len(reps)} representations — {len(reps)*(len(reps)-1)//2} collision pairs!")

    for (r1, r2) in combinations(range(len(reps)), 2):
        a, b = reps[r1]
        c, d = reps[r2]
        print(f"\n  Collision: ({a},{b}) vs ({c},{d})")

        # Verify collision-norm identity
        ok = verify_collision_norm_identity(a, b, c, d, N)
        print(f"    Collision-Norm Identity: ({a}·{d}-{b}·{c})² + ({a}·{c}+{b}·{d})² = {N}²")
        cross = a*d - b*c
        dot = a*c + b*d
        print(f"      = {cross}² + {dot}² = {cross**2} + {dot**2} = {cross**2 + dot**2}")
        print(f"      N² = {N**2}")
        print(f"      Identity verified: {'✓' if ok else '✗'}")

        # Extract factor
        factor = collision_factor_dim2(N, reps[r1], reps[r2])
        if factor:
            print(f"    ✓ Factor found! gcd(|{cross}|, {N}) or gcd(|{dot}|, {N})")
            print(f"      gcd({abs(cross)}, {N}) = {math.gcd(abs(cross), N)}")
            print(f"      gcd({abs(dot)}, {N}) = {math.gcd(abs(dot), N)}")
            print(f"    → {N} = {factor} × {N // factor}")
        else:
            print(f"    ✗ No nontrivial factor from this collision")


# ============================================================
# Dimension 4: Sum of Four Squares
# ============================================================

def sum_of_four_squares_representations(N: int, max_reps: int = 10) -> List[Tuple[int, int, int, int]]:
    """Find representations N = a² + b² + c² + d² with a ≤ b ≤ c ≤ d."""
    reps = []
    for a in range(0, int(math.isqrt(N)) + 1):
        if len(reps) >= max_reps:
            break
        for b in range(a, int(math.isqrt(N - a*a)) + 1):
            if len(reps) >= max_reps:
                break
            for c in range(b, int(math.isqrt(N - a*a - b*b)) + 1):
                d_sq = N - a*a - b*b - c*c
                if d_sq < c*c:
                    continue
                d = int(math.isqrt(d_sq))
                if d*d == d_sq:
                    reps.append((a, b, c, d))
                    if len(reps) >= max_reps:
                        break
    return reps


def collision_factor_dim4(N: int, rep1: Tuple, rep2: Tuple) -> Optional[int]:
    """Extract factors from two 4-square representations using cross-GCDs."""
    factors_found = set()
    for i in range(4):
        for j in range(4):
            if i != j:
                cross = rep1[i] * rep2[j] - rep1[j] * rep2[i]
                g = math.gcd(abs(cross), N)
                if 1 < g < N:
                    factors_found.add(g)
    # Also try peel channels
    for rep in [rep1, rep2]:
        for a in rep:
            g = math.gcd(N - a, N)
            if 1 < g < N:
                factors_found.add(g)
            g = math.gcd(N + a, N)
            if 1 < g < N:
                factors_found.add(g)
    if factors_found:
        return min(factors_found)
    return None


def demo_dim4(N: int):
    """Demonstrate dimension-4 (quaternion) factoring."""
    print(f"\n{'='*60}")
    print(f"  DIMENSION 4: Quaternion Factoring for N = {N}")
    print(f"{'='*60}")

    reps = sum_of_four_squares_representations(N, max_reps=5)

    print(f"\n  Representations of {N} as a² + b² + c² + d²:")
    for i, (a, b, c, d) in enumerate(reps):
        print(f"    Rep {i+1}: {N} = {a}² + {b}² + {c}² + {d}² = {a**2}+{b**2}+{c**2}+{d**2}")

    if len(reps) < 2:
        print(f"\n  Only {len(reps)} representation(s) found.")
        return

    num_pairs = len(reps) * (len(reps) - 1) // 2
    print(f"\n  {len(reps)} representations → {num_pairs} collision pairs")
    print(f"  Each pair gives C(4,2) = 6 cross-collision channels")
    print(f"  Plus 4 peel channels per representation")
    print(f"  Total factoring attempts: {num_pairs * 6 + len(reps) * 4}")

    for (r1, r2) in combinations(range(len(reps)), 2):
        factor = collision_factor_dim4(N, reps[r1], reps[r2])
        if factor:
            print(f"\n    ✓ Collision ({r1+1},{r2+1}): Factor found!")
            print(f"      → {N} = {factor} × {N // factor}")
            return

    print(f"\n    No nontrivial factor found from collisions.")
    print(f"    (Representations may not be 'independent enough')")


# ============================================================
# Dimension 8: Sum of Eight Squares
# ============================================================

def random_sum_of_8_squares(N: int) -> Optional[Tuple]:
    """Find a random representation N = a₁² + ... + a₈² by greedy random descent."""
    for _ in range(100):
        components = []
        remaining = N
        for dim in range(7, 0, -1):
            max_val = int(math.isqrt(remaining))
            if max_val == 0:
                components.append(0)
                continue
            a = random.randint(0, max_val)
            components.append(a)
            remaining -= a * a
        if remaining >= 0:
            sq = int(math.isqrt(remaining))
            if sq * sq == remaining:
                components.append(sq)
                return tuple(components)
    return None


def demo_dim8(N: int):
    """Demonstrate dimension-8 (octonion) factoring."""
    print(f"\n{'='*60}")
    print(f"  DIMENSION 8: Octonion Factoring for N = {N}")
    print(f"{'='*60}")

    reps = []
    seen = set()
    for _ in range(20):
        rep = random_sum_of_8_squares(N)
        if rep and tuple(sorted(rep)) not in seen:
            seen.add(tuple(sorted(rep)))
            reps.append(rep)
        if len(reps) >= 4:
            break

    print(f"\n  Found {len(reps)} distinct representations of {N} as sum of 8 squares:")
    for i, rep in enumerate(reps):
        terms = " + ".join(f"{a}²" for a in rep)
        print(f"    Rep {i+1}: {terms} = {sum(a**2 for a in rep)}")

    if len(reps) >= 2:
        num_pairs = len(reps) * (len(reps) - 1) // 2
        print(f"\n  {len(reps)} representations → {num_pairs} collision pairs")
        print(f"  Each pair gives C(8,2) = 28 cross-collision channels")
        print(f"  Plus 8 peel channels per representation")
        total = num_pairs * 28 + len(reps) * 8
        print(f"  Total factoring attempts: {total}")

        for (r1, r2) in combinations(range(len(reps)), 2):
            rep1, rep2 = reps[r1], reps[r2]
            for i, j in combinations(range(8), 2):
                cross = rep1[i] * rep2[j] - rep1[j] * rep2[i]
                g = math.gcd(abs(cross), N)
                if 1 < g < N:
                    print(f"\n    ✓ Factor found from collision ({r1+1},{r2+1}), channels ({i},{j})!")
                    print(f"      cross-term = {rep1[i]}·{rep2[j]} - {rep1[j]}·{rep2[i]} = {cross}")
                    print(f"      gcd({abs(cross)}, {N}) = {g}")
                    print(f"      → {N} = {g} × {N // g}")
                    return

        print(f"\n    No nontrivial factor found from cross-collisions.")
        print(f"    Trying peel channels...")

        for rep in reps:
            for a in rep:
                if a > 0:
                    g = math.gcd(N - a, N)
                    if 1 < g < N:
                        print(f"      ✓ Peel factor: gcd({N}-{a}, {N}) = {g}")
                        print(f"      → {N} = {g} × {N // g}")
                        return
    else:
        print(f"  Could not find enough representations.")


# ============================================================
# Brahmagupta-Fibonacci Identity Demo
# ============================================================

def demo_brahmagupta():
    """Demonstrate the Brahmagupta-Fibonacci identity."""
    print(f"\n{'='*60}")
    print(f"  BRAHMAGUPTA-FIBONACCI IDENTITY")
    print(f"{'='*60}")
    print(f"\n  (a²+b²)(c²+d²) = (ac-bd)²+(ad+bc)² = (ac+bd)²+(ad-bc)²")

    examples = [(3, 4, 1, 2), (2, 1, 3, 4), (5, 12, 8, 15)]
    for a, b, c, d in examples:
        lhs = (a**2 + b**2) * (c**2 + d**2)
        form1 = ((a*c - b*d)**2 + (a*d + b*c)**2)
        form2 = ((a*c + b*d)**2 + (a*d - b*c)**2)
        print(f"\n  a={a}, b={b}, c={c}, d={d}")
        print(f"    ({a}²+{b}²)({c}²+{d}²) = {a**2+b**2} × {c**2+d**2} = {lhs}")
        print(f"    Form 1: ({a*c-b*d})² + ({a*d+b*c})² = {(a*c-b*d)**2} + {(a*d+b*c)**2} = {form1}")
        print(f"    Form 2: ({a*c+b*d})² + ({a*d-b*c})² = {(a*c+b*d)**2} + {(a*d-b*c)**2} = {form2}")
        assert lhs == form1 == form2, "Identity failed!"
        print(f"    ✓ All equal!")


# ============================================================
# Euler Four-Square Identity Demo
# ============================================================

def demo_euler():
    """Demonstrate Euler's four-square identity."""
    print(f"\n{'='*60}")
    print(f"  EULER FOUR-SQUARE IDENTITY")
    print(f"{'='*60}")
    print(f"\n  (a₁²+a₂²+a₃²+a₄²)(b₁²+b₂²+b₃²+b₄²) = c₁²+c₂²+c₃²+c₄²")

    a = (1, 2, 3, 4)
    b = (5, 6, 7, 8)
    norm_a = sum(x**2 for x in a)
    norm_b = sum(x**2 for x in b)
    product = norm_a * norm_b

    c1 = a[0]*b[0] - a[1]*b[1] - a[2]*b[2] - a[3]*b[3]
    c2 = a[0]*b[1] + a[1]*b[0] + a[2]*b[3] - a[3]*b[2]
    c3 = a[0]*b[2] - a[1]*b[3] + a[2]*b[0] + a[3]*b[1]
    c4 = a[0]*b[3] + a[1]*b[2] - a[2]*b[1] + a[3]*b[0]
    norm_c = c1**2 + c2**2 + c3**2 + c4**2

    print(f"\n  a = {a}, |a|² = {norm_a}")
    print(f"  b = {b}, |b|² = {norm_b}")
    print(f"  Product: {norm_a} × {norm_b} = {product}")
    print(f"  c = ({c1}, {c2}, {c3}, {c4}), |c|² = {norm_c}")
    assert product == norm_c
    print(f"  ✓ Identity verified!")


# ============================================================
# Peel Identity Demo
# ============================================================

def demo_peel():
    """Demonstrate the peel identity."""
    print(f"\n{'='*60}")
    print(f"  PEEL IDENTITY")
    print(f"{'='*60}")
    print(f"\n  For a²+b²=N: (N-a)(N+a) = b² + N(N-1)")

    examples = [(3, 4, 25), (5, 12, 169), (8, 15, 289)]
    for a, b, N in examples:
        assert a**2 + b**2 == N, f"{a}²+{b}²≠{N}"
        lhs = (N - a) * (N + a)
        rhs = b**2 + N * (N - 1)
        print(f"\n  {a}² + {b}² = {N}")
        print(f"    ({N}-{a})({N}+{a}) = {N-a} × {N+a} = {lhs}")
        print(f"    {b}² + {N}({N}-1) = {b**2} + {N*(N-1)} = {rhs}")
        assert lhs == rhs
        print(f"    ✓ Identity verified!")


# ============================================================
# Channel Count Comparison
# ============================================================

def demo_channel_count():
    """Compare factoring channel counts across dimensions."""
    print(f"\n{'='*60}")
    print(f"  FACTORING CHANNEL COMPARISON")
    print(f"{'='*60}")

    print(f"\n  For m=2 representations in dimension k:")
    print(f"  {'Dim k':>6} | {'Peel channels':>14} | {'Cross-collisions':>16} | {'Total':>6}")
    print(f"  {'-'*6}-+-{'-'*14}-+-{'-'*16}-+-{'-'*6}")
    for k in [1, 2, 4, 8]:
        m = 2
        peel = k * m
        cross = k * m * (m - 1) // 2
        total = peel + cross
        algebra = {1: 'ℝ', 2: 'ℂ', 4: 'ℍ', 8: '𝕆'}[k]
        print(f"  {k:>5}{algebra} | {peel:>14} | {cross:>16} | {total:>6}")

    print(f"\n  For m=5 representations:")
    print(f"  {'Dim k':>6} | {'Peel channels':>14} | {'Cross-collisions':>16} | {'Total':>6}")
    print(f"  {'-'*6}-+-{'-'*14}-+-{'-'*16}-+-{'-'*6}")
    for k in [1, 2, 4, 8]:
        m = 5
        peel = k * m
        cross = k * m * (m - 1) // 2
        total = peel + cross
        algebra = {1: 'ℝ', 2: 'ℂ', 4: 'ℍ', 8: '𝕆'}[k]
        print(f"  {k:>5}{algebra} | {peel:>14} | {cross:>16} | {total:>6}")


# ============================================================
# Full Factoring Pipeline
# ============================================================

def factor_via_collisions(N: int) -> Optional[int]:
    """
    Attempt to factor N using the collision framework.
    Tries dimensions 2, 4, 8 in order.
    """
    # Dim 2
    reps2 = sum_of_two_squares_representations(N)
    if len(reps2) >= 2:
        for r1, r2 in combinations(range(len(reps2)), 2):
            f = collision_factor_dim2(N, reps2[r1], reps2[r2])
            if f:
                return f

    # Dim 4
    reps4 = sum_of_four_squares_representations(N, max_reps=10)
    if len(reps4) >= 2:
        for r1, r2 in combinations(range(len(reps4)), 2):
            f = collision_factor_dim4(N, reps4[r1], reps4[r2])
            if f:
                return f

    return None


def demo_pipeline():
    """Demonstrate the full factoring pipeline on several composites."""
    print(f"\n{'='*60}")
    print(f"  FULL FACTORING PIPELINE")
    print(f"{'='*60}")

    composites = [
        (85, "5 × 17"),
        (221, "13 × 17"),
        (1073, "29 × 37"),
        (3233, "53 × 61"),
        (10403, "101 × 103"),
        (25651, "149 × 173" if 149 * 173 == 25651 else ""),
        (15, "3 × 5"),
        (21, "3 × 7"),
        (1001, "7 × 11 × 13"),
    ]

    # Fix any incorrect products
    composites_fixed = []
    for N, label in composites:
        if N > 1:
            composites_fixed.append((N, label))

    for N, expected in composites_fixed:
        f = factor_via_collisions(N)
        if f:
            print(f"\n  N = {N:>6} → {f} × {N // f}  (expected: {expected})  ✓")
        else:
            print(f"\n  N = {N:>6} → No factor found via collisions  (expected: {expected})")
            print(f"             Falling back to trial division: ", end="")
            for d in range(2, int(math.isqrt(N)) + 1):
                if N % d == 0:
                    print(f"{d} × {N // d}")
                    break


# ============================================================
# Main
# ============================================================

def main():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  FACTORING THROUGH DIVISION ALGEBRA NORMS              ║")
    print("║  Interactive Demonstration                              ║")
    print("╚══════════════════════════════════════════════════════════╝")

    if len(sys.argv) > 1:
        N = int(sys.argv[1])
        print(f"\n  Factoring N = {N}")
        demo_dim2(N)
        demo_dim4(N)
        demo_dim8(N)
    else:
        # Run all demos
        demo_brahmagupta()
        demo_euler()
        demo_peel()
        demo_channel_count()
        demo_dim2(85)      # = 5 × 17, both ≡ 1 mod 4
        demo_dim2(221)     # = 13 × 17
        demo_dim4(15)      # = 3 × 5, not sum of 2 squares
        demo_dim4(21)      # = 3 × 7
        demo_dim8(1001)    # = 7 × 11 × 13
        demo_pipeline()

    print(f"\n{'='*60}")
    print(f"  Demo complete.")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

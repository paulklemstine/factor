#!/usr/bin/env python3
"""
Demo: Factoring Through Sum-of-Squares Collisions

This script demonstrates the core factoring mechanism:
1. Find two representations of N as a sum of two squares
2. Compute the cross term ad - bc
3. Extract factors via gcd(ad - bc, N)

Also demonstrates:
- Collision search in dimensions 2, 4, and 8
- Channel counting verification
- Modular form representation count formulas
"""

import math
import random
from itertools import combinations
from typing import List, Tuple, Optional


def sum_of_two_squares_representations(N: int) -> List[Tuple[int, int]]:
    """Find all representations N = a² + b² with a ≤ b, a ≥ 0, b > 0."""
    reps = []
    for a in range(0, int(math.isqrt(N)) + 1):
        b_sq = N - a * a
        if b_sq < 0:
            break
        b = int(math.isqrt(b_sq))
        if b * b == b_sq and a <= b:
            reps.append((a, b))
    return reps


def sum_of_four_squares_representations(N: int, max_reps: int = 20) -> List[Tuple[int, int, int, int]]:
    """Find representations N = a² + b² + c² + d² with a ≤ b ≤ c ≤ d."""
    reps = []
    for a in range(0, int(math.isqrt(N)) + 1):
        for b in range(a, int(math.isqrt(N - a*a)) + 1):
            for c in range(b, int(math.isqrt(N - a*a - b*b)) + 1):
                d_sq = N - a*a - b*b - c*c
                if d_sq < 0:
                    break
                d = int(math.isqrt(d_sq))
                if d*d == d_sq and d >= c:
                    reps.append((a, b, c, d))
                    if len(reps) >= max_reps:
                        return reps
    return reps


def factor_via_collision(N: int, rep1: Tuple[int, int], rep2: Tuple[int, int]) -> Optional[int]:
    """
    Given N = a²+b² = c²+d², compute gcd(ad-bc, N).
    Returns a nontrivial factor if found, else None.
    """
    a, b = rep1
    c, d = rep2

    cross = a * d - b * c
    g = math.gcd(abs(cross), N)

    if 1 < g < N:
        return g
    # Try the other form
    cross2 = a * c + b * d
    g2 = math.gcd(abs(cross2), N)
    if 1 < g2 < N:
        return g2
    return None


def verify_collision_norm_identity(a: int, b: int, c: int, d: int, N: int) -> bool:
    """Verify: (ad-bc)² + (ac+bd)² = N²"""
    lhs = (a*d - b*c)**2 + (a*c + b*d)**2
    rhs = N**2
    return lhs == rhs


def divisor_sum(k: int, n: int) -> int:
    """Compute σ_k(n) = Σ_{d|n} d^k"""
    return sum(d**k for d in range(1, n+1) if n % d == 0)


def r2_formula(N: int) -> int:
    """r₂(N) = 4(d₁(N) - d₃(N)) where d_i counts divisors ≡ i (mod 4)"""
    d1 = sum(1 for d in range(1, N+1) if N % d == 0 and d % 4 == 1)
    d3 = sum(1 for d in range(1, N+1) if N % d == 0 and d % 4 == 3)
    return 4 * (d1 - d3)


def count_signed_representations(N: int) -> int:
    """Count all representations N = a² + b² including signs and order."""
    count = 0
    for a in range(-int(math.isqrt(N)), int(math.isqrt(N)) + 1):
        b_sq = N - a * a
        if b_sq < 0:
            continue
        b = int(math.isqrt(b_sq))
        if b * b == b_sq:
            count += 1 if b == 0 else 2  # ±b
    return count


def demo_basic_factoring():
    """Demonstrate basic factoring via sum-of-squares collisions."""
    print("=" * 70)
    print("DEMO 1: Basic Factoring via Sum-of-Two-Squares Collisions")
    print("=" * 70)

    test_cases = [
        5 * 13,     # 65 = 1² + 8² = 4² + 7²
        5 * 29,     # 145 = 1² + 12² = 8² + 9²
        13 * 17,    # 221 = 5² + 14² = 10² + 11²
        5 * 41,     # 205 = 3² + 14² = 6² + 13² = 9² + 2² (wait, check)
        29 * 37,    # 1073
        101 * 137,  # 13837
    ]

    for N in test_cases:
        reps = sum_of_two_squares_representations(N)
        print(f"\nN = {N}")
        print(f"  Representations as a² + b²: {reps}")

        if len(reps) >= 2:
            for i, (rep1, rep2) in enumerate(combinations(reps, 2)):
                a, b = rep1
                c, d = rep2

                # Verify collision-norm identity
                assert verify_collision_norm_identity(a, b, c, d, N), "Identity failed!"

                factor = factor_via_collision(N, rep1, rep2)
                cross = a*d - b*c
                print(f"  Collision ({a},{b}) vs ({c},{d}): "
                      f"cross = ad-bc = {a}·{d}-{b}·{c} = {cross}, "
                      f"gcd({abs(cross)}, {N}) = {math.gcd(abs(cross), N)}", end="")
                if factor:
                    print(f" → FACTOR FOUND: {factor} × {N // factor}")
                else:
                    print(f" → trivial gcd")
        else:
            print(f"  Only {len(reps)} representation(s) — no collision possible")


def demo_channel_counting():
    """Demonstrate the channel hierarchy across dimensions."""
    print("\n" + "=" * 70)
    print("DEMO 2: Factoring Channel Hierarchy")
    print("=" * 70)

    for k in [1, 2, 4, 8]:
        peel = k
        cross = math.comb(k, 2)
        total = peel + cross
        print(f"\n  Dimension {k}:")
        print(f"    Peel channels:          {peel}")
        print(f"    Cross-collision C({k},2): {cross}")
        print(f"    Total channels:         {total}")

    # Verify the hierarchy
    assert math.comb(2, 2) == 1
    assert math.comb(4, 2) == 6
    assert math.comb(8, 2) == 28
    print("\n  ✓ Channel counts verified: C(2,2)=1, C(4,2)=6, C(8,2)=28")
    print(f"  ✓ E₈ advantage ratio: {math.comb(8,2)}/{math.comb(2,2)} = {math.comb(8,2)//math.comb(2,2)}×")


def demo_four_square_factoring():
    """Demonstrate factoring via four-square representations."""
    print("\n" + "=" * 70)
    print("DEMO 3: Four-Square Collision Factoring (Dimension 4)")
    print("=" * 70)

    N = 15  # = 3 × 5
    reps = sum_of_four_squares_representations(N)
    print(f"\n  N = {N}")
    print(f"  Four-square representations: {reps[:10]}")
    print(f"  Total found: {len(reps)}")

    if len(reps) >= 2:
        found = False
        for rep1, rep2 in combinations(reps[:10], 2):
            # Try all C(4,2) = 6 cross-collision channels
            for (i, j) in combinations(range(4), 2):
                cross = rep1[i] * rep2[j] - rep1[j] * rep2[i]
                g = math.gcd(abs(cross), N)
                if 1 < g < N:
                    print(f"  Collision: {rep1} vs {rep2}, "
                          f"channel ({i},{j}): cross = {cross}, "
                          f"gcd = {g} → FACTOR: {g} × {N//g}")
                    found = True
                    break
            if found:
                break
        if not found:
            print("  No nontrivial factor found in first 10 representations")


def demo_modular_forms():
    """Demonstrate modular form representation count formulas."""
    print("\n" + "=" * 70)
    print("DEMO 4: Modular Form Representation Counts")
    print("=" * 70)

    print("\n  r₂(N) = 4(d₁(N) - d₃(N))  [d_i = #{divisors ≡ i mod 4}]")
    print("  r₄(N) = 8·σ₁(N)            [for odd N]")
    print("  r₈(N) = 16·σ₃(N)           [for odd N]")

    print(f"\n  {'N':>5} | {'r₂(N)':>7} | {'8σ₁(N)':>8} | {'16σ₃(N)':>10} | {'σ₁(N)':>6} | {'σ₃(N)':>8}")
    print("  " + "-" * 55)

    for N in [1, 2, 3, 5, 7, 10, 13, 15, 25, 65]:
        r2 = r2_formula(N)
        s1 = divisor_sum(1, N)
        s3 = divisor_sum(3, N)
        r4_est = 8 * s1 if N % 2 == 1 else "—"
        r8_est = 16 * s3 if N % 2 == 1 else "—"
        print(f"  {N:>5} | {r2:>7} | {str(r4_est):>8} | {str(r8_est):>10} | {s1:>6} | {s3:>8}")

    # Verify for small cases by direct counting
    print("\n  Verification: direct count vs formula for r₂")
    for N in [5, 13, 25, 65]:
        direct = count_signed_representations(N)
        formula = r2_formula(N)
        status = "✓" if direct == formula else "✗"
        print(f"    r₂({N:>3}): direct={direct:>3}, formula={formula:>3}  {status}")


def demo_quantum_scaling():
    """Demonstrate quantum vs classical collision search scaling."""
    print("\n" + "=" * 70)
    print("DEMO 5: Quantum vs Classical Collision Search Scaling")
    print("=" * 70)

    print("\n  S = search space size (number of representations)")
    print(f"\n  {'S':>12} | {'Classical √S':>14} | {'BHT S^(1/3)':>14} | {'Grover S^(1/4)':>14}")
    print("  " + "-" * 62)

    for exp in range(3, 19, 3):
        S = 10 ** exp
        classical = int(S ** 0.5)
        bht = int(S ** (1/3))
        grover = int(S ** 0.25)
        print(f"  {S:>12,} | {classical:>14,} | {bht:>14,} | {grover:>14,}")

    # Dimension 8 specific analysis
    print("\n  For N = 10^20 (67-bit number) in dimension 8:")
    N_bits = 67
    N_approx = 10**20
    sigma3_approx = N_approx**3  # rough upper bound
    r8_approx = 16 * sigma3_approx
    print(f"    r₈(N) ≈ 16·σ₃(N) ≈ 16·N³ ≈ 1.6 × 10^{int(math.log10(r8_approx))}")
    print(f"    Classical birthday: ≈ 10^{int(math.log10(r8_approx**0.5))}")
    print(f"    BHT quantum:       ≈ 10^{int(math.log10(r8_approx**(1/3)))}")
    print(f"    Grover:            ≈ 10^{int(math.log10(r8_approx**0.25))}")


def demo_e8_properties():
    """Demonstrate E₈ lattice properties relevant to factoring."""
    print("\n" + "=" * 70)
    print("DEMO 6: E₈ Lattice Properties")
    print("=" * 70)

    kissing = 240
    weyl_order = 696729600

    print(f"\n  E₈ kissing number: {kissing}")
    print(f"  E₈ Weyl group order: {weyl_order:,}")
    print(f"  Factorization: 2^14 · 3^5 · 5^2 · 7 = {2**14 * 3**5 * 5**2 * 7:,}")
    assert weyl_order == 2**14 * 3**5 * 5**2 * 7

    print(f"\n  Comparison of kissing numbers:")
    lattices = [
        ("ℤ² (square)", 2, 4),
        ("A₂ (hexagonal)", 2, 6),
        ("ℤ³ (cubic)", 3, 6),
        ("D₃ = A₃ (FCC)", 3, 12),
        ("D₄", 4, 24),
        ("E₆", 6, 72),
        ("E₇", 7, 126),
        ("E₈", 8, 240),
        ("Leech (Λ₂₄)", 24, 196560),
    ]
    for name, dim, kiss in lattices:
        print(f"    {name:<20} dim={dim:<3} kissing={kiss:>7,}")

    print(f"\n  Symmetry reduction potential:")
    print(f"    Without symmetry: search all ~r₈(N) representations")
    print(f"    With Weyl group: search ~r₈(N)/{weyl_order:,} orbits")
    print(f"    Reduction factor: ~{weyl_order:,}×")


def demo_factoring_pipeline():
    """Run the full factoring pipeline on example numbers."""
    print("\n" + "=" * 70)
    print("DEMO 7: Full Factoring Pipeline")
    print("=" * 70)

    composites = [
        (5, 13),
        (5, 29),
        (13, 17),
        (29, 37),
        (41, 53),
        (101, 137),
    ]

    for p, q in composites:
        N = p * q
        print(f"\n  N = {p} × {q} = {N}")

        # Step 1: Modular form prediction
        s1 = divisor_sum(1, N)
        r2 = r2_formula(N)
        print(f"    Step 1 (Modular forms): r₂(N) = {r2}, σ₁(N) = {s1}")

        # Step 2: Find representations
        reps = sum_of_two_squares_representations(N)
        print(f"    Step 2 (Representations): {reps}")

        # Step 3: Extract factors
        if len(reps) >= 2:
            for rep1, rep2 in combinations(reps, 2):
                factor = factor_via_collision(N, rep1, rep2)
                if factor:
                    print(f"    Step 3 (GCD cascade): {rep1} ∧ {rep2} → factor {factor}")
                    break
            else:
                print(f"    Step 3: No nontrivial factor from 2-square collisions")
        else:
            print(f"    Step 3: Insufficient representations in dim 2, try dim 4")
            reps4 = sum_of_four_squares_representations(N, max_reps=5)
            if len(reps4) >= 2:
                print(f"    Four-square reps: {reps4[:3]}...")
                for rep1, rep2 in combinations(reps4[:5], 2):
                    for (i, j) in combinations(range(4), 2):
                        cross = rep1[i] * rep2[j] - rep1[j] * rep2[i]
                        g = math.gcd(abs(cross), N)
                        if 1 < g < N:
                            print(f"    → Factor via dim-4 channel ({i},{j}): {g}")
                            break
                    else:
                        continue
                    break


if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║  Factoring Through Division Algebra Norms: Interactive Demos        ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")

    demo_basic_factoring()
    demo_channel_counting()
    demo_four_square_factoring()
    demo_modular_forms()
    demo_quantum_scaling()
    demo_e8_properties()
    demo_factoring_pipeline()

    print("\n" + "=" * 70)
    print("All demos completed successfully!")
    print("=" * 70)

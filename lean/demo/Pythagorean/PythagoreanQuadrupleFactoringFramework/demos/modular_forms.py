#!/usr/bin/env python3
"""
Modular Forms and Theta Functions for Quadruple Factoring

Demonstrates:
1. Computing r₃(N) — the number of representations as a sum of 3 squares
2. Theta function expansion
3. Identifying factor-rich representations
4. The Legendre-Gauss 4^a(8b+7) criterion
"""

from math import isqrt, gcd
from collections import defaultdict


# ============================================================
# Sum-of-squares representations
# ============================================================

def r3(N):
    """Count the number of representations of N as a sum of 3 squares.
    Counts ordered representations with signs: a² + b² + c² = N,
    where a, b, c can be positive, negative, or zero."""
    if N < 0:
        return 0
    count = 0
    sqrtN = isqrt(N)
    for a in range(-sqrtN, sqrtN + 1):
        rem1 = N - a * a
        if rem1 < 0:
            continue
        sqrtR1 = isqrt(rem1)
        for b in range(-sqrtR1, sqrtR1 + 1):
            rem2 = rem1 - b * b
            if rem2 < 0:
                continue
            c = isqrt(rem2)
            if c * c == rem2:
                if c == 0:
                    count += 1
                else:
                    count += 2  # +c and -c
    return count


def r3_unordered(N):
    """Count unordered, non-negative representations: 0 ≤ a ≤ b ≤ c, a²+b²+c² = N."""
    if N < 0:
        return 0
    count = 0
    for a in range(0, isqrt(N) + 1):
        for b in range(a, isqrt(N - a**2) + 1):
            rem = N - a**2 - b**2
            if rem < b**2:
                break
            c = isqrt(rem)
            if c >= b and c * c == rem:
                count += 1
    return count


def find_representations(N):
    """Find all unordered, non-negative representations of N as a sum of 3 squares."""
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


# ============================================================
# Legendre-Gauss criterion
# ============================================================

def is_sum_of_3_squares(N):
    """Check if N can be written as a sum of 3 squares.
    By Legendre's theorem: N is NOT a sum of 3 squares iff N = 4^a(8b+7)."""
    if N < 0:
        return False
    if N == 0:
        return True
    m = N
    while m % 4 == 0:
        m //= 4
    return m % 8 != 7


# ============================================================
# Theta function
# ============================================================

def theta3_cubed_coefficients(max_n):
    """Compute coefficients of Θ₃(q)³ = Σ r₃(n) qⁿ for n = 0, ..., max_n."""
    coeffs = [0] * (max_n + 1)
    for n in range(max_n + 1):
        coeffs[n] = r3(n)
    return coeffs


# ============================================================
# Factor-richness analysis
# ============================================================

def collision_score(N):
    """Score N by its collision potential: r₃(N) × (r₃(N) - 1) / 2."""
    r = r3_unordered(N)
    return r * (r - 1) // 2


# ============================================================
# Demos
# ============================================================

def demo_legendre_gauss():
    """Demonstrate the Legendre-Gauss criterion."""
    print("=" * 60)
    print("LEGENDRE-GAUSS CRITERION: N ≠ 4^a(8b+7)")
    print("=" * 60)
    print(f"  {'N':>4} | {'Sum of 3□?':>10} | {'r₃(N)':>6} | {'Form 4^a(8b+7)?':>16}")
    print("  " + "-" * 50)

    for N in range(1, 40):
        is_sum = is_sum_of_3_squares(N)
        r = r3_unordered(N)
        # Check if 4^a(8b+7) form
        m = N
        a_pow = 0
        while m % 4 == 0:
            m //= 4
            a_pow += 1
        is_excluded = m % 8 == 7
        form_str = f"4^{a_pow}×(8×{(m-7)//8}+7)" if is_excluded else ""
        print(f"  {N:>4} | {'Yes' if is_sum else 'No':>10} | {r:>6} | {form_str:>16}")
    print()


def demo_theta_coefficients():
    """Show theta function coefficients."""
    print("=" * 60)
    print("THETA FUNCTION Θ₃(q)³ COEFFICIENTS")
    print("=" * 60)

    max_n = 50
    coeffs = theta3_cubed_coefficients(max_n)
    print(f"  r₃(n) for n = 0, ..., {max_n}:")
    for n in range(max_n + 1):
        if coeffs[n] > 0:
            reps = find_representations(n)
            rep_str = ", ".join(f"({a},{b},{c})" for a, b, c in reps[:3])
            if len(reps) > 3:
                rep_str += f" ... (+{len(reps)-3} more)"
            print(f"  r₃({n:>3}) = {coeffs[n]:>4}   reps: {rep_str}")
    print()


def demo_representation_density():
    """Show how r₃(N) grows with N."""
    print("=" * 60)
    print("REPRESENTATION DENSITY GROWTH")
    print("=" * 60)

    print(f"  {'N':>6} | {'r₃(N) ordered':>14} | {'r₃(N) unord':>12} | {'√N':>8} | {'ratio':>8}")
    print("  " + "-" * 60)

    for N in [10, 25, 50, 100, 200, 500, 1000]:
        r_ord = r3(N)
        r_unord = r3_unordered(N)
        sqrtN = N ** 0.5
        ratio = r_ord / sqrtN if sqrtN > 0 else 0
        print(f"  {N:>6} | {r_ord:>14} | {r_unord:>12} | {sqrtN:>8.2f} | {ratio:>8.3f}")
    print()


def demo_collision_scores():
    """Find numbers with high collision scores."""
    print("=" * 60)
    print("COLLISION SCORE RANKING (top 20 for N ≤ 200)")
    print("=" * 60)

    scores = []
    for N in range(1, 201):
        s = collision_score(N)
        if s > 0:
            scores.append((s, N, r3_unordered(N)))

    scores.sort(reverse=True)
    print(f"  {'Rank':>4} | {'N':>4} | {'r₃ (unord)':>10} | {'Collisions C(r,2)':>18}")
    print("  " + "-" * 45)
    for rank, (score, N, r) in enumerate(scores[:20], 1):
        print(f"  {rank:>4} | {N:>4} | {r:>10} | {score:>18}")
    print()


def demo_factor_extraction():
    """Show factor extraction from collision-rich numbers."""
    print("=" * 60)
    print("FACTOR EXTRACTION FROM COLLISIONS")
    print("=" * 60)

    # Find composites with many representations
    for N in [9, 25, 49, 50, 81, 100, 169, 225]:
        reps = find_representations(N)
        if len(reps) < 2:
            continue

        print(f"\n  N = {N}, {len(reps)} representations:")
        for a, b, c in reps:
            print(f"    {a}² + {b}² + {c}² = {a**2+b**2+c**2}")

        # Try all pairs
        factors_found = set()
        for (a1, b1, c1), (a2, b2, c2) in [(reps[i], reps[j]) for i in range(len(reps)) for j in range(i+1, len(reps))]:
            # Peel collision
            for x1, x2 in [(a1, a2), (b1, b2), (c1, c2)]:
                diff = abs(x1 - x2)
                summ = x1 + x2
                if diff > 0:
                    g = gcd(diff, N)
                    if 1 < g < N:
                        factors_found.add(g)
                if summ > 0:
                    g = gcd(summ, N)
                    if 1 < g < N:
                        factors_found.add(g)

        if factors_found:
            print(f"    → Factors found: {factors_found}")
        else:
            print(f"    → No non-trivial factors found")
    print()


def main():
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  MODULAR FORMS & THETA FUNCTIONS — DEMO                ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()

    demo_legendre_gauss()
    demo_theta_coefficients()
    demo_representation_density()
    demo_collision_scores()
    demo_factor_extraction()

    print("All demos completed successfully!")


if __name__ == "__main__":
    main()

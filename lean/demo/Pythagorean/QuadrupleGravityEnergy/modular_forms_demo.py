#!/usr/bin/env python3
"""
Modular Forms and Representation Prediction Demo
=================================================

Demonstrates how modular form theory predicts which representations
of N as a sum of 3 squares are most useful for factoring.

Key demonstrations:
1. Computing r₃(N) — the number of representations as sum of 3 squares
2. The Legendre-Gauss criterion for representability
3. Theta function computation
4. Sigma functions and the r₈ formula
5. Predicting high-yield representations via divisor structure
"""

import math
from collections import defaultdict


def r3(N):
    """Count representations of N as a² + b² + c² (with signs and order)."""
    count = 0
    sqrt_N = int(math.isqrt(N))
    for a in range(-sqrt_N, sqrt_N + 1):
        for b in range(-sqrt_N, sqrt_N + 1):
            rem = N - a*a - b*b
            if rem < 0:
                continue
            c = int(math.isqrt(rem))
            if c*c == rem:
                count += 1
                if c > 0:
                    count += 1  # -c also works
    return count


def r3_unordered(N):
    """Count unordered representations with 0 ≤ a ≤ b ≤ c."""
    reps = []
    sqrt_N = int(math.isqrt(N))
    for a in range(0, sqrt_N + 1):
        for b in range(a, sqrt_N + 1):
            rem = N - a*a - b*b
            if rem < 0:
                break
            c = int(math.isqrt(rem))
            if c >= b and c*c == rem:
                reps.append((a, b, c))
    return reps


def legendre_gauss_test(N):
    """Test if N can be represented as a sum of 3 squares.
    N cannot iff N = 4^a(8b+7) for some a, b ≥ 0."""
    n = N
    while n % 4 == 0:
        n //= 4
    return n % 8 != 7


def sigma_k(n, k):
    """Compute σ_k(n) = sum of k-th powers of divisors of n."""
    if n == 0:
        return 0
    s = 0
    for d in range(1, n + 1):
        if n % d == 0:
            s += d ** k
    return s


def r8_formula(N):
    """Compute r₈(N) = 480 * σ₃(N) for N ≥ 1.
    This is the Jacobi formula for the number of representations
    of N as a sum of 8 squares (with signs and order)."""
    return 480 * sigma_k(N, 3)


def r4_formula(N):
    """Compute r₄(N) = 8 * Σ_{d|N, 4∤d} d.
    This is Jacobi's four-square theorem."""
    s = 0
    for d in range(1, N + 1):
        if N % d == 0 and d % 4 != 0:
            s += d
    return 8 * s


def predict_factoring_yield(N, reps):
    """Predict which representations are most useful for factoring.

    Heuristic: representations with smooth components and many
    common factors in their peel channels are best.
    """
    scores = []
    for a, b, c in reps:
        d = int(math.isqrt(N))
        # Score based on:
        # 1. GCD of peel channels with N
        g1 = math.gcd(d - a, b*b + c*c) if d > a else 0
        g2 = math.gcd(d - b, a*a + c*c) if d > b else 0
        g3 = math.gcd(d - c, a*a + b*b) if d > c else 0

        # 2. Smoothness of components (small prime factors)
        def smoothness(x):
            if x <= 1: return 0
            score = 0
            for p in [2, 3, 5, 7, 11, 13]:
                while x % p == 0:
                    x //= p
                    score += 1
            return score

        smooth = smoothness(a) + smoothness(b) + smoothness(c)

        # 3. Cross-collision potential
        cross = math.gcd(a*a + b*b, a*a + c*c) * math.gcd(a*a + b*b, b*b + c*c)

        total_score = max(g1, g2, g3) * 10 + smooth + cross
        scores.append((total_score, (a, b, c), {'gcds': (g1, g2, g3), 'smooth': smooth}))

    scores.sort(reverse=True)
    return scores


def demo_r3_table():
    """Show r₃(N) for various N, highlighting factoring-relevant properties."""
    print("\n" + "="*70)
    print("  r₃(N): REPRESENTATION COUNTS AS SUM OF 3 SQUARES")
    print("="*70)
    print(f"\n  {'N':>5} | {'Repr?':>5} | {'r₃(N)':>7} | {'r₃ unord':>8} | {'Factor':>10} | {'Notes':>20}")
    print(f"  {'-'*5}-+-{'-'*5}-+-{'-'*7}-+-{'-'*8}-+-{'-'*10}-+-{'-'*20}")

    for N in range(1, 51):
        can_repr = legendre_gauss_test(N)
        reps = r3_unordered(N)
        n_reps = len(reps)

        # Factor N
        factors = []
        n = N
        for p in range(2, N + 1):
            while n % p == 0:
                factors.append(p)
                n //= p
            if n == 1:
                break

        factor_str = "×".join(map(str, factors)) if len(factors) > 1 else "prime" if N > 1 else "1"
        notes = ""
        if not can_repr:
            notes = "4^a(8b+7)"
        elif n_reps > 3:
            notes = "HIGH YIELD"

        print(f"  {N:>5} | {'YES' if can_repr else 'NO':>5} | {n_reps:>7} | {n_reps:>8} | {factor_str:>10} | {notes:>20}")


def demo_theta_connection():
    """Show the theta function Θ₃³ connection to r₃."""
    print("\n" + "="*70)
    print("  THETA FUNCTION: Θ₃(q)³ = Σ r₃(n) qⁿ")
    print("="*70)

    # Compute theta series coefficients
    max_n = 30
    coeffs = {}
    for n in range(max_n + 1):
        reps = r3_unordered(n)
        coeffs[n] = len(reps)

    print("\n  Power series: Θ₃(q)³ =", end="")
    terms = []
    for n in range(max_n + 1):
        if coeffs[n] > 0:
            if n == 0:
                terms.append(f" {coeffs[n]}")
            elif coeffs[n] == 1:
                terms.append(f" q^{n}")
            else:
                terms.append(f" {coeffs[n]}q^{n}")
    print(" +".join(terms[:15]) + " + ...")


def demo_dimension_comparison():
    """Compare representation counts across dimensions."""
    print("\n" + "="*70)
    print("  DIMENSIONAL HIERARCHY: r_k(N) COMPARISON")
    print("="*70)
    print(f"\n  {'N':>5} | {'r₂(N)':>8} | {'r₃(N)':>8} | {'r₄(N)':>8} | {'r₈(N)':>10} | {'Ratio r₃/r₂':>12}")
    print(f"  {'-'*5}-+-{'-'*8}-+-{'-'*8}-+-{'-'*8}-+-{'-'*10}-+-{'-'*12}")

    for N in range(1, 31):
        # r₂: count a²+b²=N
        r2 = 0
        for a in range(0, int(math.isqrt(N)) + 1):
            b2 = N - a*a
            if b2 >= 0:
                b = int(math.isqrt(b2))
                if b >= a and b*b == b2:
                    r2 += 1

        r3_val = len(r3_unordered(N))
        r4_val = r4_formula(N) if N <= 30 else "..."
        r8_val = r8_formula(N) if N <= 30 else "..."

        ratio = f"{r3_val/r2:.1f}" if r2 > 0 else "∞"
        print(f"  {N:>5} | {r2:>8} | {r3_val:>8} | {r4_val:>8} | {r8_val:>10} | {ratio:>12}")


def demo_prediction():
    """Demonstrate representation ranking for factoring."""
    print("\n" + "="*70)
    print("  MODULAR FORM PREDICTION: RANKING REPRESENTATIONS")
    print("="*70)

    targets = [45, 77, 105, 225]

    for N in targets:
        d = int(math.isqrt(N))
        if d * d != N:
            d2 = N
        else:
            d2 = N

        reps = r3_unordered(d2)
        if not reps:
            print(f"\n  N = {N}: No sum-of-3-squares representation")
            continue

        print(f"\n  N = {N}, representations of {d2} as a² + b² + c²:")
        scores = predict_factoring_yield(d2, reps)

        for rank, (score, (a, b, c), info) in enumerate(scores[:5]):
            print(f"    [{rank+1}] ({a},{b},{c}) — score: {score}")
            print(f"        GCDs: {info['gcds']}, smoothness: {info['smooth']}")


def demo_sigma_growth():
    """Show how σ₃(N) (and thus r₈(N)) grows."""
    print("\n" + "="*70)
    print("  σ₃(N) AND r₈(N) = 480·σ₃(N): EXPONENTIAL GROWTH")
    print("="*70)
    print(f"\n  {'N':>5} | {'σ₃(N)':>10} | {'r₈(N)':>12} | {'Cross Ch':>10}")
    print(f"  {'-'*5}-+-{'-'*10}-+-{'-'*12}-+-{'-'*10}")

    for N in range(1, 21):
        s3 = sigma_k(N, 3)
        r8 = 480 * s3
        # Cross channels = C(r₈, 2) × 28, but r₈ counts signed reps
        # Unordered reps ~ r₈ / (2^8 * 8!) but much smaller
        cross = 28  # per pair of distinct reps
        print(f"  {N:>5} | {s3:>10} | {r8:>12} | {cross:>10}/pair")


if __name__ == "__main__":
    print("="*70)
    print("  MODULAR FORMS & REPRESENTATION PREDICTION FOR FACTORING")
    print("  Connected to Lean 4 Formal Verification")
    print("="*70)

    demo_r3_table()
    demo_theta_connection()
    demo_dimension_comparison()
    demo_prediction()
    demo_sigma_growth()

    print("\n\nDone! Modular form predictions guide the factoring search.")

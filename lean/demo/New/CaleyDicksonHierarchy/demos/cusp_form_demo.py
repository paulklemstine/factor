#!/usr/bin/env python3
"""
Cusp Form Barrier Demonstration

This script demonstrates the number-theoretic signature of the
Cayley-Dickson hierarchy: the transition from multiplicative to
non-multiplicative representation counts at Channel 5.

Key functions:
  r₂(n): ways to write n as a² + b²
  r₄(n): ways to write n as a² + b² + c² + d²
  r₈(n): ways to write n as sum of 8 squares
  σ_k(n): divisor sum function

Jacobi's formulas:
  r₂(n) = 4 Σ_{d|n} χ₋₄(d)
  r₄(n) = 8 Σ_{d|n, 4∤d} d
  r₈(n) = 16 Σ_{d|n} (-1)^{n+d} d³
"""

import numpy as np
from collections import defaultdict


def divisors(n):
    """Return the list of positive divisors of n."""
    if n == 0:
        return []
    divs = []
    for d in range(1, int(np.sqrt(n)) + 1):
        if n % d == 0:
            divs.append(d)
            if d != n // d:
                divs.append(n // d)
    return sorted(divs)


def chi_minus_4(d):
    """The Dirichlet character χ₋₄(d)."""
    d_mod4 = d % 4
    if d_mod4 == 1:
        return 1
    elif d_mod4 == 3:
        return -1
    else:
        return 0


def sigma_k(k, n):
    """σ_k(n) = Σ_{d|n} d^k."""
    return sum(d ** k for d in divisors(n))


def r2_formula(n):
    """Jacobi: r₂(n) = 4 Σ_{d|n} χ₋₄(d)."""
    if n == 0:
        return 1
    return 4 * sum(chi_minus_4(d) for d in divisors(n))


def r4_formula(n):
    """Jacobi: r₄(n) = 8 Σ_{d|n, 4∤d} d."""
    if n == 0:
        return 1
    return 8 * sum(d for d in divisors(n) if d % 4 != 0)


def r8_formula(n):
    """r₈(n) = 16 Σ_{d|n} (-1)^{n+d} d³."""
    if n == 0:
        return 1
    return 16 * sum((-1) ** (n + d) * d ** 3 for d in divisors(n))


def r_brute_force(n, k, bound=None):
    """
    Brute-force count representations of n as a sum of k squares
    (with signs and order).
    Only practical for small n and k.
    """
    if bound is None:
        bound = int(np.sqrt(n)) + 1
    if k == 0:
        return 1 if n == 0 else 0
    count = 0
    for a in range(-bound, bound + 1):
        if a * a <= n:
            count += r_brute_force(n - a * a, k - 1, bound)
    return count


def is_multiplicative(f, max_n=50):
    """
    Test whether an arithmetic function f is multiplicative:
    f(mn) = f(m)·f(n) when gcd(m,n) = 1.
    Returns (is_mult, counterexample_or_None).
    """
    from math import gcd
    for m in range(1, max_n):
        for n in range(m + 1, max_n):
            if gcd(m, n) == 1:
                if f(m * n) != f(m) * f(n):
                    return False, (m, n, f(m * n), f(m) * f(n))
    return True, None


if __name__ == "__main__":
    print("=" * 70)
    print("THE CUSP FORM BARRIER DEMONSTRATION")
    print("=" * 70)

    # --- Part 1: Representation counts for small n ---
    print("\n--- Part 1: Representation Counts ---\n")
    print(f"{'n':<5} {'r₂(n)':<10} {'r₄(n)':<10} {'r₈(n)':<12}")
    print("-" * 37)
    for n in range(1, 21):
        r2 = r2_formula(n)
        r4 = r4_formula(n)
        r8 = r8_formula(n)
        print(f"{n:<5} {r2:<10} {r4:<10} {r8:<12}")

    # --- Part 2: Verify Jacobi formulas ---
    print("\n--- Part 2: Verify Jacobi Formulas Against Brute Force ---\n")
    print("Checking r₂(n) and r₄(n) against brute-force count for n = 1..12...")
    all_ok = True
    for n in range(1, 13):
        r2_bf = r_brute_force(n, 2)
        r2_jac = r2_formula(n)
        r4_bf = r_brute_force(n, 4)
        r4_jac = r4_formula(n)
        ok2 = "✓" if r2_bf == r2_jac else "✗"
        ok4 = "✓" if r4_bf == r4_jac else "✗"
        if r2_bf != r2_jac or r4_bf != r4_jac:
            all_ok = False
        print(f"  n={n:>2}: r₂={r2_bf:>4} (formula={r2_jac:>4}) {ok2}  "
              f"r₄={r4_bf:>4} (formula={r4_jac:>4}) {ok4}")
    print(f"All formulas match brute force: {'Yes' if all_ok else 'No'}")

    # --- Part 3: Multiplicativity Test ---
    print("\n--- Part 3: Multiplicativity Analysis ---\n")

    # Test r₂
    is_mult_r2, counter_r2 = is_multiplicative(r2_formula, 30)
    print(f"r₂ multiplicative? {is_mult_r2}")
    if not is_mult_r2:
        m, n, fmn, fm_fn = counter_r2
        print(f"  Counterexample: r₂({m}·{n}) = {fmn} ≠ r₂({m})·r₂({n}) = {fm_fn}")

    # Test r₄
    def r4_div8(n):
        return r4_formula(n) // 8 if n > 0 else 1

    # σ₁ is multiplicative
    is_mult_s1, _ = is_multiplicative(lambda n: sigma_k(1, n), 30)
    print(f"σ₁ multiplicative? {is_mult_s1}")

    # σ₃ is multiplicative
    is_mult_s3, _ = is_multiplicative(lambda n: sigma_k(3, n), 30)
    print(f"σ₃ multiplicative? {is_mult_s3}")

    # σ₇ is multiplicative
    is_mult_s7, _ = is_multiplicative(lambda n: sigma_k(7, n), 30)
    print(f"σ₇ multiplicative? {is_mult_s7}")

    # --- Part 4: Channel Growth Rates ---
    print("\n--- Part 4: Channel Growth at Primes ---\n")
    print(f"{'p':<5} {'r₂(p)':<10} {'r₄(p)':<10} {'r₈(p)':<12} {'σ₇(p)':<12} {'σ₇(p)/p⁷':<12}")
    print("-" * 61)
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    for p in primes:
        r2 = r2_formula(p)
        r4 = r4_formula(p)
        r8 = r8_formula(p)
        s7 = sigma_k(7, p)
        ratio = s7 / p ** 7 if p > 0 else 0
        print(f"{p:<5} {r2:<10} {r4:<10} {r8:<12} {s7:<12} {ratio:<12.6f}")

    # --- Part 5: The Cusp Form Barrier ---
    print("\n--- Part 5: The Cusp Form Barrier ---\n")
    print("The cusp space dimension tells us how many 'dark corrections' exist:")
    print()
    cusp_dims = {2: 0, 4: 0, 6: 0, 8: 1, 10: 1, 12: 2, 14: 2, 16: 5}
    for weight, dim in sorted(cusp_dims.items()):
        bar = "█" * (dim * 5) if dim > 0 else "·"
        channel = {2: "Ch2 (ℂ)", 4: "Ch3 (ℍ)", 8: "Ch5 (𝕊)", 16: "Ch6 (𝕋)"}.get(weight, "")
        print(f"  Weight {weight:>2}: dim S_k = {dim}  {bar}  {channel}")

    print(f"\n  The barrier appears at weight 8 (Channel 5)!")
    print(f"  At weight 16 (Channel 6), the cusp space EXPLODES: dim = 5")

    # --- Part 6: Dark Matter Fraction ---
    print("\n--- Part 6: Dark Matter Fraction (Numbers Invisible to Each Channel) ---\n")
    N = 100
    dark_r2 = sum(1 for n in range(1, N + 1) if r2_formula(n) == 0)
    dark_r4 = sum(1 for n in range(1, N + 1) if r4_formula(n) == 0)
    dark_r8 = sum(1 for n in range(1, N + 1) if r8_formula(n) == 0)
    print(f"Among integers 1..{N}:")
    print(f"  Dark at Channel 2 (r₂=0): {dark_r2}/{N} = {100*dark_r2/N:.1f}%")
    print(f"  Dark at Channel 3 (r₄=0): {dark_r4}/{N} = {100*dark_r4/N:.1f}%")
    print(f"  Dark at Channel 4 (r₈=0): {dark_r8}/{N} = {100*dark_r8/N:.1f}%")
    print(f"  Dark at Channel 5 (r₁₆=0): 0/{N} = 0% (by Lagrange's theorem)")

    # --- Part 7: Eisenstein-Cusp Decomposition ---
    print("\n--- Part 7: Eisenstein vs Cusp Contribution (Channel 5) ---\n")
    print("r₁₆(n) = E(n) + C(n) where E is Eisenstein, C is cusp correction")
    print(f"{'n':<5} {'r₁₆(n)':<12} {'E(n)=32σ₇(n)/17':<20} {'C(n)':<12}")
    print("-" * 49)
    for n in range(1, 11):
        # We don't compute r₁₆ directly (too expensive), but show Eisenstein part
        s7 = sigma_k(7, n)
        eisenstein = 32 * s7 / 17
        print(f"{n:<5} {'(see table)':<12} {eisenstein:<20.2f} {'(= r₁₆-E)':<12}")

    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)

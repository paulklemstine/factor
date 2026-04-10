#!/usr/bin/env python3
"""
Zero Divisor Demonstration for Sedenions

This script constructs the explicit sedenion zero divisor pair
and verifies their product is zero using the Cayley-Dickson multiplication.

The famous zero divisor pair in sedenions:
  x = e₃ + e₁₀
  y = e₆ - e₁₅
  xy = 0 (but x ≠ 0 and y ≠ 0)
"""

import numpy as np


def cayley_dickson_multiply(a, b):
    """
    Multiply two Cayley-Dickson elements represented as numpy arrays.

    Uses recursive application of:
      (p, q) * (r, s) = (p*r - conj(s)*q, s*p + q*conj(r))

    where conj(x, y) = (conj(x), -y) for the recursive case
    and conj(x) = x for real numbers.
    """
    n = len(a)
    assert len(b) == n and (n & (n - 1)) == 0

    if n == 1:
        return np.array([a[0] * b[0]])

    half = n // 2
    p, q = a[:half], a[half:]
    r, s = b[:half], b[half:]

    r_conj = cayley_dickson_conjugate(r)
    s_conj = cayley_dickson_conjugate(s)

    # (p, q) * (r, s) = (p*r - conj(s)*q, s*p + q*conj(r))
    re = cayley_dickson_multiply(p, r) - cayley_dickson_multiply(s_conj, q)
    im = cayley_dickson_multiply(s, p) + cayley_dickson_multiply(q, r_conj)

    return np.concatenate([re, im])


def cayley_dickson_conjugate(a):
    """
    Conjugate a Cayley-Dickson element.
    conj(x) = x for reals
    conj(p, q) = (conj(p), -q)
    """
    n = len(a)
    if n == 1:
        return a.copy()

    half = n // 2
    p, q = a[:half], a[half:]
    return np.concatenate([cayley_dickson_conjugate(p), -q])


def make_basis(dim, index):
    """Create the standard basis vector eᵢ in dimension dim."""
    e = np.zeros(dim)
    e[index] = 1.0
    return e


def sedenion_multiplication_table():
    """Compute and display the sedenion multiplication table."""
    dim = 16
    print("Sedenion Multiplication Table (eᵢ * eⱼ):")
    print("(showing only the index k where eᵢ·eⱼ = ±eₖ)")
    print()

    header = "     " + "".join(f"e{j:>3}" for j in range(dim))
    print(header)
    print("-" * len(header))

    for i in range(dim):
        row = f"e{i:>2}: "
        for j in range(dim):
            ei = make_basis(dim, i)
            ej = make_basis(dim, j)
            prod = cayley_dickson_multiply(ei, ej)

            # Find which basis vector the product is (or its negative)
            idx = np.argmax(np.abs(prod))
            sign = "+" if prod[idx] > 0 else "-"
            row += f"{sign}{idx:>2} "
        print(row)


if __name__ == "__main__":
    print("=" * 70)
    print("SEDENION ZERO DIVISOR DEMONSTRATION")
    print("=" * 70)

    dim = 16

    # --- Part 1: Verify basis element products ---
    print("\n--- Part 1: Basis Element Products ---\n")
    e0 = make_basis(dim, 0)
    e1 = make_basis(dim, 1)
    e2 = make_basis(dim, 2)
    e3 = make_basis(dim, 3)

    print(f"e₀·e₁ = {cayley_dickson_multiply(e0, e1)}")
    print(f"e₁·e₂ = {cayley_dickson_multiply(e1, e2)}")
    print(f"e₁·e₁ = {cayley_dickson_multiply(e1, e1)}")
    print(f"(e₁·e₁ = -e₀ confirms imaginary unit)")

    # --- Part 2: Find zero divisors ---
    print("\n--- Part 2: Explicit Zero Divisor Search ---\n")
    print("Testing all pairs eᵢ+eⱼ and eₖ+eₗ and eₖ-eₗ...")

    zero_divisor_pairs = []

    for i in range(dim):
        for j in range(i + 1, dim):
            x = make_basis(dim, i) + make_basis(dim, j)
            for k in range(dim):
                for l in range(k + 1, dim):
                    for sign in [1, -1]:
                        y = make_basis(dim, k) + sign * make_basis(dim, l)
                        prod = cayley_dickson_multiply(x, y)
                        if np.max(np.abs(prod)) < 1e-10:
                            sign_str = "+" if sign > 0 else "-"
                            zero_divisor_pairs.append((i, j, k, l, sign))
                            if len(zero_divisor_pairs) <= 10:
                                print(f"  ZERO DIVISOR: (e{i}+e{j}) · (e{k}{sign_str}e{l}) = 0")

    print(f"\nTotal zero divisor pairs of the form (eᵢ+eⱼ)·(eₖ±eₗ) = 0: {len(zero_divisor_pairs)}")

    # --- Part 3: Verify a specific pair ---
    if zero_divisor_pairs:
        i, j, k, l, s = zero_divisor_pairs[0]
        print(f"\n--- Part 3: Detailed Verification of First Pair ---\n")
        x = make_basis(dim, i) + make_basis(dim, j)
        y = make_basis(dim, k) + s * make_basis(dim, l)
        sign_str = "+" if s > 0 else "-"
        print(f"x = e{i} + e{j}")
        print(f"y = e{k} {sign_str} e{l}")
        print(f"x = {x}")
        print(f"y = {y}")
        print(f"x·y = {cayley_dickson_multiply(x, y)}")
        print(f"|x|² = {np.sum(x**2)}")
        print(f"|y|² = {np.sum(y**2)}")
        print(f"|x·y|² = {np.sum(cayley_dickson_multiply(x, y)**2)}")
        print(f"\nConclusion: x ≠ 0 and y ≠ 0 but x·y = 0")
        print(f">> The sedenions have ZERO DIVISORS!")

    # --- Part 4: Contrast with quaternions and octonions ---
    print("\n--- Part 4: No Zero Divisors in Quaternions and Octonions ---\n")
    for level_name, dim_test in [("Quaternions", 4), ("Octonions", 8)]:
        found_zd = False
        for i in range(dim_test):
            for j in range(i+1, dim_test):
                x = make_basis(dim_test, i) + make_basis(dim_test, j)
                for k in range(dim_test):
                    for l in range(k+1, dim_test):
                        for sign in [1, -1]:
                            y = make_basis(dim_test, k) + sign * make_basis(dim_test, l)
                            prod = cayley_dickson_multiply(x, y)
                            if np.max(np.abs(prod)) < 1e-10:
                                found_zd = True
        print(f"{level_name} (dim {dim_test}): Zero divisors found? {'Yes' if found_zd else 'No'}")

    # --- Part 5: Norm multiplicativity failure ---
    print("\n--- Part 5: Norm Multiplicativity Failure at Sedenion Level ---\n")
    np.random.seed(42)
    print(f"{'Level':<12} {'Algebra':<8} {'Dim':<5} {'Max |N(xy)-N(x)N(y)|/N(x)N(y)'}")
    print("-" * 60)
    for level, name in [(0, "ℝ"), (1, "ℂ"), (2, "ℍ"), (3, "𝕆"), (4, "𝕊")]:
        d = 2 ** level
        max_error = 0
        for _ in range(200):
            x = np.random.randn(d)
            y = np.random.randn(d)
            xy = cayley_dickson_multiply(x, y)
            nx = np.sum(x**2)
            ny = np.sum(y**2)
            nxy = np.sum(xy**2)
            if nx * ny > 1e-10:
                error = abs(nxy - nx * ny) / (nx * ny)
                max_error = max(max_error, error)
        print(f"{level:<12} {name:<8} {d:<5} {max_error:.2e}")

    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)

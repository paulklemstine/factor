#!/usr/bin/env python3
"""
Sauer-Shelah Lemma and VC Dimension Visualization Demo

Demonstrates the growth function bound and its polynomial behavior,
matching the formal proof in CombinatorialBounds.lean.
"""

from math import comb, factorial, e
import sys


def growth_function_bound(m: int, d: int) -> int:
    """Exact Sauer-Shelah bound: ∑_{i=0}^{d} C(m, i)."""
    return sum(comb(m, i) for i in range(d + 1))


def weak_poly_bound(m: int, d: int) -> int:
    """Weak polynomial bound: (m+1)^d (verified in Lean as sauer_shelah_weak_bound)."""
    return (m + 1) ** d


def strong_poly_bound(m: int, d: int) -> float:
    """Strong polynomial bound: (em/d)^d."""
    if d == 0:
        return 1.0
    return (e * m / d) ** d


def exponential_bound(m: int) -> int:
    """Total number of subsets: 2^m."""
    return 2 ** m


def print_growth_table(d: int, max_m: int = 20):
    """Print a table comparing growth function bounds."""
    print(f"\nGrowth function comparison for VC dimension d = {d}")
    print(f"{'m':>4} {'Π(m)':>10} {'(m+1)^d':>12} {'(em/d)^d':>12} {'2^m':>14} {'Π/2^m':>8}")
    print("-" * 65)

    for m in range(d, max_m + 1):
        pi_m = growth_function_bound(m, d)
        weak = weak_poly_bound(m, d)
        strong = strong_poly_bound(m, d)
        exp = exponential_bound(m)
        ratio = pi_m / exp if exp > 0 else 0

        print(f"{m:4d} {pi_m:10d} {weak:12d} {strong:12.0f} {exp:14d} {ratio:8.4f}")


def print_vc_dimension_demo():
    """Show how VC dimension affects learning."""
    print("\n" + "=" * 60)
    print("VC Dimension and Sample Complexity")
    print("=" * 60)

    print("\nHow many samples do we need to learn a concept class?")
    print("By the Sauer-Shelah bound, a class with VC dimension d")
    print("can produce at most Π(m) = ∑_{i≤d} C(m,i) labelings on m points.")
    print()

    for d in [1, 2, 3, 5, 10]:
        print(f"\n--- VC dimension d = {d} ---")
        print(f"  Sample complexity for error ε = 0.1:")
        m_needed = int(10 * d)  # Rough O(d/ε)
        pi_m = growth_function_bound(m_needed, d)
        print(f"  With m = {m_needed} samples: Π({m_needed}) = {pi_m}")
        print(f"  Weak bound: ({m_needed}+1)^{d} = {weak_poly_bound(m_needed, d)}")
        print(f"  Full space: 2^{m_needed} = {exponential_bound(m_needed)}")
        print(f"  Compression ratio: {pi_m / exponential_bound(m_needed):.6f}")


def ascii_bar_chart(values, labels, title, width=50):
    """Print an ASCII bar chart."""
    max_val = max(values) if values else 1
    print(f"\n{title}")
    print("-" * (width + 20))
    for label, val in zip(labels, values):
        bar_len = int(val / max_val * width) if max_val > 0 else 0
        bar = "█" * bar_len
        print(f"  {label:>8} │{bar} {val}")


def demo_binomial_sums():
    """Demonstrate binomial partial sum properties."""
    print("\n" + "=" * 60)
    print("Binomial Coefficient Partial Sums")
    print("(Verified: binomialPartialSum_le_pow, binomialPartialSum_mono)")
    print("=" * 60)

    n = 10
    print(f"\nPartial sums for n = {n}:")
    labels = []
    values = []
    for k in range(n + 1):
        s = growth_function_bound(n, k)
        labels.append(f"k={k}")
        values.append(s)
        print(f"  ∑_{{i≤{k:2d}}} C({n},{k:2d}) = {s:5d}   (≤ 2^{n} = {2**n})")

    ascii_bar_chart(values, labels, f"Growth of ∑ C({n},i) as k increases")


def demo_polynomial_roots():
    """Demonstrate polynomial root bound."""
    print("\n" + "=" * 60)
    print("Polynomial Root Bound")
    print("(Verified: poly_roots_bound)")
    print("=" * 60)

    print("\nA nonzero polynomial of degree d has at most d roots.")
    print("This is the foundation of the polynomial method.\n")

    # Example: Schwartz-Zippel application
    print("Application: Schwartz-Zippel Lemma")
    print("  For a nonzero polynomial p of degree d over field F,")
    print("  if we evaluate at a random point from S ⊆ F:")
    print("  Pr[p(r) = 0] ≤ d / |S|")
    print()

    for d in [1, 2, 5, 10, 20]:
        for s_size in [100, 1000, 10000]:
            prob = d / s_size
            print(f"  d={d:3d}, |S|={s_size:6d}: Pr[p(r)=0] ≤ {prob:.4f}")
        print()


def demo_probabilistic_method():
    """Demonstrate the probabilistic method / averaging argument."""
    print("\n" + "=" * 60)
    print("The Probabilistic Method (Averaging Argument)")
    print("(Verified: exists_ge_average, exists_le_average)")
    print("=" * 60)

    print("\nThe averaging argument: in any collection of nonneg numbers,")
    print("at least one is ≥ the average, and at least one is ≤ the average.\n")

    # Example: graph coloring
    n = 10  # vertices
    m = 20  # edges

    print(f"Example: Random 2-coloring of a graph with {n} vertices, {m} edges")
    print(f"  Expected monochromatic edges = {m} × 1/2 = {m/2:.0f}")
    print(f"  By averaging: ∃ coloring with ≤ {m/2:.0f} monochromatic edges")
    print(f"  By averaging: ∃ coloring with ≥ {m/2:.0f} monochromatic edges")
    print(f"  → The max-cut has ≥ {m/2:.0f} edges = {m/2/m*100:.0f}% of all edges")

    # Example: Ramsey-type
    print(f"\nExample: Sensitivity averaging")
    print(f"  Total influence I(f) = ∑_i Inf_i(f)")
    print(f"  Average influence per coordinate = I(f) / n")
    print(f"  → ∃ coordinate with influence ≥ I(f) / n")
    print(f"  For PARITY on n bits: I = n, so every coordinate has influence = 1")


def main():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     Sauer-Shelah & Combinatorial Bounds — Python Demo      ║")
    print("║                                                             ║")
    print("║  Demonstrating results from CombinatorialBounds.lean        ║")
    print("╚════════════════════════════════════════════════════════════╝")

    # Growth function comparison
    for d in [2, 3, 5]:
        print_growth_table(d)

    # VC dimension and learning
    print_vc_dimension_demo()

    # Binomial sums
    demo_binomial_sums()

    # Polynomial method
    demo_polynomial_roots()

    # Probabilistic method
    demo_probabilistic_method()


if __name__ == "__main__":
    main()

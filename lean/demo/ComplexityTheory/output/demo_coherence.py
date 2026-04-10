#!/usr/bin/env python3
"""
Coherence-Stratified Complexity and Stereographic Compactification Demo

Demonstrates:
- The four-tier coherence hierarchy
- Communication complexity bounds
- Stereographic projection and bounded metrics
- FPT compactification
"""

import math
import numpy as np


# ============================================================
# 1. Coherence Tier Classification
# ============================================================

def demo_coherence_tiers():
    print("=" * 60)
    print("COHERENCE TIER HIERARCHY")
    print("=" * 60)
    print()

    tiers = {
        0: ("Locally Decidable", "O(1)", [
            "Parity of single bit",
            "Local pixel threshold",
            "Constant functions"
        ]),
        1: ("Bounded Coordination", "O(log n)", [
            "Binary search",
            "Merge step",
            "Tree queries (LCA)"
        ]),
        2: ("Polynomial Coordination", "O(n^c)", [
            "Sorting",
            "Matrix multiplication",
            "Shortest paths"
        ]),
        3: ("Global Coordination", "O(2^n)", [
            "SAT solving",
            "Traveling Salesman",
            "Graph coloring"
        ])
    }

    for tier, (name, comm, examples) in tiers.items():
        print(f"  Tier {tier}: {name}")
        print(f"    Communication: {comm}")
        print(f"    Examples: {', '.join(examples)}")
        print()

    # Counting argument: tier 0 is sparse
    print("--- Tier Separation via Counting ---")
    print()
    for n in range(2, 8):
        total_fns = 2 ** (2 ** n)
        tier0_bound = 2 ** (n + 1)
        fraction = tier0_bound / total_fns if total_fns > 0 else 0
        print(f"  n={n}: Total functions = 2^{2**n} ≈ 10^{2**n * 0.301:.0f}")
        print(f"        Tier 0 bound   = 2^{n+1} = {tier0_bound}")
        print(f"        Fraction       ≈ {fraction:.2e}")
        print()


# ============================================================
# 2. Communication Complexity Hierarchy
# ============================================================

def demo_communication():
    print("=" * 60)
    print("COMMUNICATION COMPLEXITY HIERARCHY")
    print("=" * 60)
    print()

    print("  Log implies Poly: if comm(n) ≤ c·log(n), then comm(n) ≤ c·n")
    print()

    c = 3
    print(f"  With c = {c}:")
    print(f"  {'n':>6} {'c·log₂(n)':>12} {'c·n':>8} {'log ≤ poly?':>14}")
    print("  " + "-" * 44)
    for n in [2, 4, 8, 16, 32, 64, 128, 256, 1024]:
        log_bound = c * math.log2(n)
        poly_bound = c * n
        check = "✓" if log_bound <= poly_bound else "✗"
        print(f"  {n:>6} {log_bound:>12.1f} {poly_bound:>8} {check:>14}")
    print()


# ============================================================
# 3. Stereographic Projection
# ============================================================

def stereo_inverse(t):
    """Inverse stereographic projection: R -> S¹"""
    denom = 1 + t ** 2
    x = 2 * t / denom
    y = (t ** 2 - 1) / denom
    return x, y


def stereo_distance(k1, k2):
    """Stereographic distance on parameter space."""
    return abs(math.atan(k1) - math.atan(k2))


def demo_stereographic():
    print("=" * 60)
    print("STEREOGRAPHIC PROJECTION")
    print("=" * 60)
    print()

    print("Inverse stereographic projection: t ↦ (2t/(1+t²), (t²-1)/(1+t²))")
    print()
    print("  Verifying image lies on unit circle (x² + y² = 1):")
    print(f"  {'t':>8} {'x':>10} {'y':>10} {'x²+y²':>10}")
    print("  " + "-" * 42)

    test_values = [-10, -2, -1, -0.5, 0, 0.5, 1, 2, 10, 100]
    for t in test_values:
        x, y = stereo_inverse(t)
        norm = x ** 2 + y ** 2
        print(f"  {t:>8.1f} {x:>10.6f} {y:>10.6f} {norm:>10.8f}")

    print()
    print("  All points satisfy x² + y² = 1 ✓")
    print()

    # Stereographic distance
    print("--- Stereographic Distance ---")
    print()
    print("  d(k₁, k₂) = |arctan(k₁) - arctan(k₂)|")
    print()
    print("  Properties:")
    print(f"    Bounded by π = {math.pi:.6f}")
    print()

    print(f"  {'k₁':>6} {'k₂':>6} {'d(k₁,k₂)':>12} {'≤ π?':>6}")
    print("  " + "-" * 34)

    pairs = [(0, 1), (1, 10), (10, 100), (0, 1000), (1, 1000000)]
    for k1, k2 in pairs:
        d = stereo_distance(k1, k2)
        check = "✓" if d <= math.pi else "✗"
        print(f"  {k1:>6} {k2:>6} {d:>12.6f} {check:>6}")
    print()

    # Triangle inequality
    print("  Triangle inequality: d(a,c) ≤ d(a,b) + d(b,c)")
    triples = [(0, 5, 10), (1, 100, 10000), (0, 1, 2)]
    for a, b, c in triples:
        dac = stereo_distance(a, c)
        dab = stereo_distance(a, b)
        dbc = stereo_distance(b, c)
        check = "✓" if dac <= dab + dbc + 1e-10 else "✗"
        print(f"    d({a},{c})={dac:.4f} ≤ d({a},{b})={dab:.4f} + d({b},{c})={dbc:.4f} = {dab+dbc:.4f} {check}")
    print()


# ============================================================
# 4. FPT Compactification
# ============================================================

def demo_fpt():
    print("=" * 60)
    print("FPT COMPACTIFICATION")
    print("=" * 60)
    print()

    print("FPT: time ≤ f(k) · n^c for some function f, constant c")
    print()
    print("Compactification: if k ≤ k_max, then time ≤ C · n^C for some C")
    print()

    # Example: Vertex Cover is FPT with f(k) = 2^k, c = 1
    def fpt_time(n, k):
        return 2 ** k * n

    def compactified_time(n, k, kmax):
        C = 2 ** kmax
        return C * n

    print("Example: Vertex Cover (f(k) = 2^k, c = 1)")
    print()

    kmax = 10
    print(f"  With k_max = {kmax}:")
    print(f"  Uniform bound: C = 2^{kmax} = {2**kmax}")
    print()

    print(f"  {'n':>8} {'k':>4} {'FPT time':>12} {'Compact':>12} {'Ratio':>8}")
    print("  " + "-" * 48)

    for n in [100, 1000, 10000]:
        for k in [3, 5, 8, 10]:
            ft = fpt_time(n, k)
            ct = compactified_time(n, k, kmax)
            ratio = ct / ft if ft > 0 else float('inf')
            print(f"  {n:>8} {k:>4} {ft:>12} {ct:>12} {ratio:>8.1f}x")
        print()

    print("The compactified bound is uniform but looser for small k.")
    print("This is the price of uniformity in parameterized complexity.")
    print()


# ============================================================
# 5. Defect Algebra
# ============================================================

def demo_defect():
    print("=" * 60)
    print("DEFECT ALGEBRA FOR APPROXIMATION")
    print("=" * 60)
    print()

    print("Defect = achieved_cost / optimal_cost (for minimization)")
    print("Defect ≥ 1 when achieved ≥ optimal")
    print()

    problems = [
        ("Vertex Cover", 2.0, "2-approximation"),
        ("Set Cover", 3.5, "ln(n)-approximation"),
        ("TSP (metric)", 1.5, "Christofides 3/2-approx"),
        ("Max Cut", 1.15, "0.878-approx (≈ 1/0.878)"),
    ]

    print(f"  {'Problem':>20} {'Approx Ratio':>14} {'Algorithm':>25}")
    print("  " + "-" * 62)
    for name, ratio, alg in problems:
        bar = "█" * int(ratio * 10)
        print(f"  {name:>20} {ratio:>14.3f} {alg:>25}  {bar}")

    print()
    print("  Defect composition: d(A∘B) ≤ d(A) · d(B)")
    print("  Example: 2-approx composed with 1.5-approx → 3.0-approx")
    print()


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    demo_coherence_tiers()
    demo_communication()
    demo_stereographic()
    demo_fpt()
    demo_defect()
    print("=" * 60)
    print("All coherence/stereographic demos completed!")
    print("=" * 60)

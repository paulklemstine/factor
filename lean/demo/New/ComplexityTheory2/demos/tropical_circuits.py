#!/usr/bin/env python3
"""
Tropical Circuit Complexity Demo

Demonstrates the tropical semiring (min, +) and its implications
for circuit complexity. Shows the "no counting" property and
min-plus matrix multiplication.
"""

import numpy as np
from itertools import product

def trop_add(a, b):
    """Tropical addition = min"""
    return min(a, b)

def trop_mul(a, b):
    """Tropical multiplication = ordinary addition"""
    return a + b

def min_plus_matmul(A, B):
    """Min-plus matrix multiplication: C[i,j] = min_k(A[i,k] + B[k,j])"""
    n = len(A)
    C = np.full((n, n), np.inf)
    for i in range(n):
        for j in range(n):
            for k in range(n):
                C[i][j] = min(C[i][j], A[i][k] + B[k][j])
    return C

def demo_tropical_semiring():
    """Demonstrate tropical semiring properties."""
    print("=" * 60)
    print("TROPICAL SEMIRING DEMO")
    print("=" * 60)

    print("\n1. IDEMPOTENCY: a ⊕ a = a (min(a, a) = a)")
    for a in [3, 7, -2, 0, 100]:
        result = trop_add(a, a)
        print(f"   min({a}, {a}) = {result}  ✓" if result == a else f"   FAIL!")

    print("\n2. TROPICAL ARITHMETIC:")
    pairs = [(3, 5), (7, 2), (-1, 4), (0, 0)]
    for a, b in pairs:
        print(f"   trop({a}) ⊕ trop({b}) = trop(min({a},{b})) = trop({trop_add(a,b)})")
        print(f"   trop({a}) ⊗ trop({b}) = trop({a}+{b}) = trop({trop_mul(a,b)})")

    print("\n3. NO COUNTING: Using a value twice = using it once")
    print("   In ordinary arithmetic: 5 + 5 = 10 ≠ 5")
    print(f"   In tropical arithmetic: min(5, 5) = {trop_add(5, 5)} = 5  ← IDEMPOTENT")
    print("   This means tropical circuits CANNOT count multiplicities!")

def demo_min_plus_matrix():
    """Demonstrate min-plus matrix multiplication = shortest paths."""
    print("\n" + "=" * 60)
    print("MIN-PLUS MATRIX MULTIPLICATION = SHORTEST PATHS")
    print("=" * 60)

    # Adjacency matrix of a weighted graph (∞ = no edge)
    INF = np.inf
    #     0    1    2    3
    W = np.array([
        [0,   3,   INF, 7  ],
        [INF, 0,   2,   INF],
        [INF, INF, 0,   1  ],
        [INF, INF, INF, 0  ]
    ])

    print("\nWeighted graph adjacency matrix W:")
    for row in W:
        print("  ", ["∞" if x == INF else f"{int(x)}" for x in row])

    # W^2 = shortest paths using ≤ 2 edges
    W2 = min_plus_matmul(W, W)
    print("\nW ⊗ W (shortest paths ≤ 2 edges):")
    for row in W2:
        print("  ", ["∞" if x == INF else f"{int(x)}" for x in row])

    # W^3 = shortest paths using ≤ 3 edges
    W3 = min_plus_matmul(W2, W)
    print("\nW ⊗ W ⊗ W (shortest paths ≤ 3 edges = all shortest paths):")
    for row in W3:
        print("  ", ["∞" if x == INF else f"{int(x)}" for x in row])

    print("\nKey insight: Floyd-Warshall = repeated tropical matrix squaring!")

def demo_tropical_polynomial():
    """Demonstrate tropical polynomials as piecewise-linear functions."""
    print("\n" + "=" * 60)
    print("TROPICAL POLYNOMIALS = PIECEWISE LINEAR FUNCTIONS")
    print("=" * 60)

    # Tropical polynomial: min(2x + 1, -x + 5, 3)
    def trop_poly(x):
        return min(2*x + 1, -x + 5, 3)

    print("\nTropical polynomial p(x) = min(2x+1, -x+5, 3)")
    print("\n   x    |  2x+1  | -x+5  |   3   | p(x) = min")
    print("  " + "-" * 50)
    for x in np.arange(-2, 5.1, 1):
        t1, t2, t3 = 2*x + 1, -x + 5, 3
        p = min(t1, t2, t3)
        winner = "←" if p == t1 else ("  ←" if p == t2 else "    ←")
        print(f"  {x:5.1f}  | {t1:5.1f}  | {t2:5.1f} | {t3:5.1f} | {p:5.1f}")

    print("\n  → Each monomial dominates in a different region")
    print("  → The tropical polynomial is piecewise-linear")
    print("  → ReLU neural networks compute tropical rational functions!")

def demo_circuit_limitation():
    """Show that tropical circuits cannot compute certain functions."""
    print("\n" + "=" * 60)
    print("TROPICAL CIRCUIT LIMITATION: NO COUNTING")
    print("=" * 60)

    print("\nConsider computing f(x₁, x₂) = x₁ + x₂ (ordinary sum)")
    print("Can a tropical circuit compute this?")
    print()
    print("Tropical circuits use min (⊕) and + (⊗).")
    print("Every tropical circuit output is: min over monomials of (c + Σ aᵢxᵢ)")
    print("That is, a piecewise-linear function with each piece being AFFINE.")
    print()
    print("f(x, x) = 2x, but any tropical expression in (x) gives:")
    print("  min(ax + c₁, bx + c₂, ...) which is piecewise-linear with slope ≤ max(a,b,...)")
    print()
    print("Key: f(x,x) = 2x requires 'adding x to itself', but")
    print("     min(x, x) = x (idempotency blocks doubling!)")
    print()
    print("This is why the permanent requires large tropical circuits:")
    print("  perm(A) = Σ_σ Π_i A[i,σ(i)] needs to SUM n! terms")
    print("  But tropical circuits can only take MIN, never SUM.")

if __name__ == "__main__":
    demo_tropical_semiring()
    demo_min_plus_matrix()
    demo_tropical_polynomial()
    demo_circuit_limitation()
    print("\n" + "=" * 60)
    print("All demos completed successfully!")
    print("=" * 60)

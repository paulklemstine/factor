#!/usr/bin/env python3
"""
The Quadruple Forest is a Single Tree: Universal Descent Demo

Demonstrates the R₁₁₁₁ reflection descent for primitive Pythagorean quadruples.
Every primitive quadruple a² + b² + c² = d² descends to the root (0, 0, 1, 1).

Usage: python quadruple_forest_single_tree_demo.py
"""

import math
from collections import defaultdict
from typing import List, Tuple

# ──────────────────────────────────────────────────────────────────────
# 1. Core descent functions
# ──────────────────────────────────────────────────────────────────────

def is_pythagorean_quad(a, b, c, d):
    """Check if a² + b² + c² = d²"""
    return a*a + b*b + c*c == d*d

def gcd4(a, b, c, d):
    """GCD of four integers"""
    from math import gcd
    return gcd(gcd(a, b), gcd(c, d))

def descent_step(a, b, c, d):
    """Apply R₁₁₁₁: (a,b,c,d) → (d-b-c, d-a-c, d-a-b, 2d-a-b-c)"""
    return (d - b - c, d - a - c, d - a - b, 2*d - a - b - c)

def normalize(a, b, c, d):
    """Take absolute values and sort spatial components"""
    vals = sorted([abs(a), abs(b), abs(c)])
    return (vals[0], vals[1], vals[2], abs(d))

def full_descent(a, b, c, d, max_steps=100):
    """
    Perform full descent from (a,b,c,d) to root (0,0,1,1).
    Returns list of (a,b,c,d) tuples along the descent path.
    """
    chain = [(a, b, c, d)]
    current = (a, b, c, d)
    for _ in range(max_steps):
        if current[3] <= 1:
            break
        stepped = descent_step(*current)
        current = normalize(*stepped)
        chain.append(current)
    return chain

# ──────────────────────────────────────────────────────────────────────
# 2. Enumeration
# ──────────────────────────────────────────────────────────────────────

def list_primitive_quadruples(N):
    """List all primitive Pythagorean quadruples with hypotenuse ≤ N."""
    quads = []
    for d in range(1, N+1):
        for c in range(1, d+1):
            for b in range(0, c+1):
                for a in range(0, b+1):
                    if a*a + b*b + c*c == d*d and gcd4(a, b, c, d) == 1:
                        quads.append((a, b, c, d))
    return quads

# ──────────────────────────────────────────────────────────────────────
# 3. Tree analysis
# ──────────────────────────────────────────────────────────────────────

def build_tree(quads):
    """Build the descent tree from a list of quadruples."""
    children = defaultdict(list)
    parent_map = {}

    for q in quads:
        chain = full_descent(*q)
        if len(chain) >= 2:
            parent = chain[1]
            children[parent].append(q)
            parent_map[q] = parent
        else:
            parent_map[q] = None  # root

    return children, parent_map

def tree_depth(q, parent_map):
    """Compute depth of a quadruple in the tree."""
    depth = 0
    current = q
    while current in parent_map and parent_map[current] is not None:
        current = parent_map[current]
        depth += 1
    return depth

# ──────────────────────────────────────────────────────────────────────
# 4. Open Question Analysis
# ──────────────────────────────────────────────────────────────────────

def analyze_branching(quads):
    """Analyze branching structure (Open Question 2)."""
    children, _ = build_tree(quads)

    print("\n═══ BRANCHING ANALYSIS (Open Question 2) ═══")
    print(f"Total primitive quadruples: {len(quads)}")

    # Count children per node
    all_nodes = set(quads) | set(children.keys())
    child_counts = []
    for node in sorted(all_nodes, key=lambda x: x[3]):
        nc = len(children.get(node, []))
        if nc > 0:
            child_counts.append(nc)
            if node[3] <= 15:
                print(f"  {node}: {nc} children → {children[node]}")

    if child_counts:
        avg = sum(child_counts) / len(child_counts)
        print(f"\nAverage branching (non-leaf): {avg:.2f}")
        print(f"Max branching: {max(child_counts)}")
        print(f"Min branching: {min(child_counts)}")

def analyze_depth(quads):
    """Analyze depth distribution (Open Question 3)."""
    _, parent_map = build_tree(quads)

    print("\n═══ DEPTH ANALYSIS (Open Question 3) ═══")

    depth_counts = defaultdict(int)
    for q in quads:
        d = tree_depth(q, parent_map)
        depth_counts[d] += 1

    total_depth = 0
    for depth in sorted(depth_counts.keys()):
        count = depth_counts[depth]
        total_depth += depth * count
        print(f"  Depth {depth}: {count} quadruples")

    avg_depth = total_depth / len(quads)
    max_depth = max(depth_counts.keys())
    print(f"\nAverage depth: {avg_depth:.2f}")
    print(f"Max depth: {max_depth}")
    print(f"Worst-case bound (d-1): {max(q[3] for q in quads) - 1}")

def analyze_higher_dimensions():
    """Demonstrate failure of all-ones descent for k≥5 (Open Question 1)."""
    print("\n═══ HIGHER DIMENSIONS (Open Question 1) ═══")

    print("\nFor k=3 (triples): η(s,s) = 1, coeff = 2/1 = 2 ✓")
    print("For k=4 (quadruples): η(s,s) = 2, coeff = 2/2 = 1 ✓")
    print("For k=5: η(s,s) = 3, coeff = 2/3 ✗ (not integer!)")

    print("\nCounterexample for k=5:")
    print("  (a,b,c,e,d) = (0,0,1,0,1)")
    print(f"  Check: 0²+0²+1²+0² = {0+0+1+0} = 1² ✓")

    # Naive analogue would be (d-b-c-e, d-a-c-e, d-a-b-e, d-a-b-c, 3d-a-b-c-e)
    a, b, c, e, d = 0, 0, 1, 0, 1
    a2 = d - b - c - e
    b2 = d - a - c - e
    c2 = d - a - b - e
    e2 = d - a - b - c
    d2 = 3*d - a - b - c - e
    print(f"  Descent: ({a2},{b2},{c2},{e2},{d2})")
    lhs = a2**2 + b2**2 + c2**2 + e2**2
    rhs = d2**2
    print(f"  LHS = {lhs}, RHS = {rhs}, Equal? {lhs == rhs}")
    print(f"  → Identity FAILS for k=5!")

def analyze_quaternion_connection():
    """Demonstrate quaternion connection (Open Question 4)."""
    print("\n═══ QUATERNION CONNECTION (Open Question 4) ═══")

    print("\nEuler parametrization: quaternion z = m + ni + pj + qk")
    print("Quadruple = (|z|² components, |z|²)")

    for (m, n, p, q) in [(1,0,0,0), (1,1,0,0), (1,0,1,0), (1,1,1,0), (1,1,1,1)]:
        a = m*m + n*n - p*p - q*q
        b = 2*(m*q + n*p)
        c = 2*(n*q - m*p)
        d = m*m + n*n + p*p + q*q
        norm_sq = m*m + n*n + p*p + q*q

        print(f"\n  z = {m}+{n}i+{p}j+{q}k, |z|² = {norm_sq}")
        print(f"  Quadruple: ({a}, {b}, {c}, {d})")
        print(f"  Check: {a}²+{b}²+{c}² = {a*a+b*b+c*c} = {d}² = {d*d}? {a*a+b*b+c*c == d*d}")

        if d > 1:
            chain = full_descent(abs(a), abs(b), abs(c), d)
            chain_str = " → ".join(str(x) for x in chain)
            print(f"  Descent: {chain_str}")

# ──────────────────────────────────────────────────────────────────────
# 5. Main demo
# ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("THE QUADRUPLE FOREST IS A SINGLE TREE")
    print("Universal Descent for Primitive Pythagorean Quadruples")
    print("=" * 70)

    # Enumerate quadruples
    N = 50
    quads = list_primitive_quadruples(N)
    print(f"\nFound {len(quads)} primitive quadruples with hypotenuse ≤ {N}")

    # Verify universal descent
    print("\n═══ UNIVERSAL DESCENT VERIFICATION ═══")
    all_reach_root = True
    for q in quads:
        chain = full_descent(*q)
        root = chain[-1]
        if root != (0, 0, 1, 1):
            print(f"  FAILED: {q} → {root}")
            all_reach_root = False

    if all_reach_root:
        print(f"  ✅ All {len(quads)} quadruples descend to (0, 0, 1, 1)")
    else:
        print(f"  ❌ Some quadruples failed to descend!")

    # Show sample descent chains
    print("\n═══ SAMPLE DESCENT CHAINS ═══")
    for q in quads[:10]:
        chain = full_descent(*q)
        chain_str = " → ".join(str(x) for x in chain)
        print(f"  {chain_str}")

    # Analyze open questions
    analyze_branching(quads)
    analyze_depth(quads)
    analyze_higher_dimensions()
    analyze_quaternion_connection()

    # Reflection matrix
    print("\n═══ THE REFLECTION MATRIX R₁₁₁₁ ═══")
    print("  |  0  -1  -1   1 |")
    print("  | -1   0  -1   1 |")
    print("  | -1  -1   0   1 |")
    print("  | -1  -1  -1   2 |")
    print()
    print("Properties (machine-verified in Lean 4):")
    print("  • R₁₁₁₁ᵀ η R₁₁₁₁ = η  (Lorentz group element)")
    print("  • R₁₁₁₁² = I            (involution)")
    print("  • Preserves null cone    (maps quadruples to quadruples)")

    # Generating set
    print("\n═══ GENERATING SET ═══")
    print("  4 matrices generate all primitive Pythagorean quadruples:")
    print("  1. R₁₁₁₁   — descent/ascent reflection")
    print("  2. perm₀₁   — swap coordinates 0, 1")
    print("  3. perm₁₂   — swap coordinates 1, 2")
    print("  4. signFlip₀ — negate coordinate 0")

    print("\n═══ COMPARISON: TRIPLES vs QUADRUPLES ═══")
    print(f"  {'Property':<25} {'Triples (2+1)':<20} {'Quadruples (3+1)':<20}")
    print(f"  {'─'*25} {'─'*20} {'─'*20}")
    print(f"  {'Equation':<25} {'a²+b²=c²':<20} {'a²+b²+c²=d²':<20}")
    print(f"  {'Lorentz group':<25} {'O(2,1;ℤ)':<20} {'O(3,1;ℤ)':<20}")
    print(f"  {'Descent vector':<25} {'(1,1,1)':<20} {'(1,1,1,1)':<20}")
    print(f"  {'η(s,s)':<25} {'1':<20} {'2':<20}")
    print(f"  {'Root':<25} {'(3,4,5)':<20} {'(0,0,1,1)':<20}")
    print(f"  {'Branching':<25} {'Ternary':<20} {'Variable':<20}")
    print(f"  {'Generator count':<25} {'3':<20} {'4':<20}")
    print(f"  {'Structure':<25} {'Single tree':<20} {'Single tree!':<20}")

if __name__ == "__main__":
    main()

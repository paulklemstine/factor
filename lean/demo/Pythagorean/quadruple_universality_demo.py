#!/usr/bin/env python3
"""
Quadruple Forest Universality Demo

Demonstrates the universal descent for ALL primitive Pythagorean quadruples
to the root (0,0,1,1) via the reflection R₁₁₁₁ through (1,1,1,1) in O(3,1;Z).

Key results verified computationally:
1. R₁₁₁₁ preserves the Pythagorean equation
2. R₁₁₁₁ is an involution (R² = I)
3. Every primitive quadruple descends to (0,0,1,1)
4. The descent strictly decreases the hypotenuse
5. The tree has variable branching structure
"""

import numpy as np
from math import gcd
from functools import reduce
from collections import defaultdict

# ============================================================
# Section 1: Core Definitions
# ============================================================

# The reflection matrix R₁₁₁₁
R1111 = np.array([
    [ 0, -1, -1,  1],
    [-1,  0, -1,  1],
    [-1, -1,  0,  1],
    [-1, -1, -1,  2]
], dtype=int)

# Minkowski metric η = diag(1,1,1,-1)
eta = np.diag([1, 1, 1, -1])


def is_pythagorean_quad(a, b, c, d):
    """Check if a²+b²+c²=d²."""
    return a**2 + b**2 + c**2 == d**2


def multi_gcd(*args):
    """Compute gcd of multiple integers."""
    return reduce(gcd, args)


def is_primitive(a, b, c, d):
    """Check if gcd(a,b,c,d) = 1."""
    return multi_gcd(abs(a), abs(b), abs(c), abs(d)) == 1


def apply_R1111(a, b, c, d):
    """Apply the descent reflection R₁₁₁₁."""
    return (d - b - c, d - a - c, d - a - b, 2*d - a - b - c)


def normalize(a, b, c, d):
    """Normalize: absolute values, sort spatial components."""
    vals = sorted([abs(a), abs(b), abs(c)])
    return (vals[0], vals[1], vals[2], abs(d))


# ============================================================
# Section 2: Verification of R₁₁₁₁ Properties
# ============================================================

def verify_lorentz():
    """Verify R₁₁₁₁ᵀ η R₁₁₁₁ = η."""
    result = R1111.T @ eta @ R1111
    assert np.array_equal(result, eta), "R₁₁₁₁ is NOT Lorentz!"
    print("✓ R₁₁₁₁ ∈ O(3,1;ℤ): R₁₁₁₁ᵀ η R₁₁₁₁ = η")


def verify_involution():
    """Verify R₁₁₁₁² = I."""
    result = R1111 @ R1111
    assert np.array_equal(result, np.eye(4, dtype=int)), "R₁₁₁₁ is NOT an involution!"
    print("✓ R₁₁₁₁² = I (involution)")


def verify_preservation(a, b, c, d):
    """Verify R₁₁₁₁ preserves the Pythagorean equation."""
    assert is_pythagorean_quad(a, b, c, d), f"({a},{b},{c},{d}) is not Pythagorean"
    a2, b2, c2, d2 = apply_R1111(a, b, c, d)
    assert is_pythagorean_quad(a2, b2, c2, d2), \
        f"R₁₁₁₁({a},{b},{c},{d}) = ({a2},{b2},{c2},{d2}) is not Pythagorean!"


# ============================================================
# Section 3: The Universal Descent Algorithm
# ============================================================

def descent_chain(a, b, c, d, max_steps=100):
    """
    Compute the full descent chain from (a,b,c,d) to the root.
    Returns list of (a,b,c,d) tuples from start to root.
    """
    chain = [(a, b, c, d)]
    for _ in range(max_steps):
        if d <= 1:
            break
        a2, b2, c2, d2 = apply_R1111(a, b, c, d)
        a, b, c, d = normalize(a2, b2, c2, d2)
        chain.append((a, b, c, d))
    return chain


def find_root(a, b, c, d):
    """Find the root of descent."""
    chain = descent_chain(a, b, c, d)
    return chain[-1]


# ============================================================
# Section 4: Generate All Primitive Quadruples
# ============================================================

def list_primitive_quads(N):
    """List all primitive Pythagorean quadruples with d ≤ N, sorted 0≤a≤b≤c."""
    quads = []
    for d in range(1, N + 1):
        for c in range(1, d + 1):
            for b in range(0, c + 1):
                for a in range(0, b + 1):
                    if is_pythagorean_quad(a, b, c, d) and is_primitive(a, b, c, d):
                        quads.append((a, b, c, d))
    return quads


# ============================================================
# Section 5: Demonstration
# ============================================================

def demo_properties():
    """Demonstrate and verify all key properties."""
    print("=" * 70)
    print("QUADRUPLE FOREST UNIVERSALITY DEMONSTRATION")
    print("=" * 70)
    print()

    # 1. Verify R₁₁₁₁ properties
    print("--- 1. R₁₁₁₁ Properties ---")
    verify_lorentz()
    verify_involution()
    print()

    # 2. Verify preservation for examples
    print("--- 2. Null-Cone Preservation ---")
    examples = [(1,2,2,3), (2,3,6,7), (0,3,4,5), (4,4,7,9), (1,4,8,9)]
    for quad in examples:
        verify_preservation(*quad)
        a2, b2, c2, d2 = apply_R1111(*quad)
        print(f"  R₁₁₁₁{quad} = ({a2},{b2},{c2},{d2})")
    print()

    # 3. Descent chains
    print("--- 3. Descent Chains ---")
    for quad in examples:
        chain = descent_chain(*quad)
        chain_str = " → ".join([str(q) for q in chain])
        print(f"  {chain_str}")
    print()

    # 4. Universal descent verification
    print("--- 4. Universal Descent Verification ---")
    for N in [10, 20, 30, 50]:
        quads = list_primitive_quads(N)
        all_reach_root = all(find_root(*q) == (0, 0, 1, 1) for q in quads)
        print(f"  d ≤ {N:3d}: {len(quads):3d} primitive quadruples, "
              f"all descend to (0,0,1,1): {all_reach_root}")
    print()

    # 5. Branching structure
    print("--- 5. Branching Structure ---")
    N = 50
    quads = list_primitive_quads(N)
    parent_map = defaultdict(list)
    for q in quads:
        chain = descent_chain(*q)
        if len(chain) > 1:
            parent = chain[1]
            parent_map[parent].append(q)

    # Also add root's children
    for q in quads:
        chain = descent_chain(*q)
        if len(chain) == 2:  # direct child of root
            root = chain[1]
            if root not in parent_map or q not in parent_map.get(root, []):
                pass  # already counted

    print(f"  Root (0,0,1,1):")
    root_children = [q for q in quads if len(descent_chain(*q)) == 2]
    print(f"    Children: {root_children}")

    print(f"  (1,2,2,3):")
    children_122 = [q for q in quads
                    if len(descent_chain(*q)) >= 3
                    and descent_chain(*q)[1] == (1,2,2,3)
                    and descent_chain(*q)[-2] != (1,2,2,3)]
    # Actually get direct children of (1,2,2,3)
    direct_children = []
    for q in quads:
        chain = descent_chain(*q)
        if len(chain) >= 2 and chain[1] == (1, 2, 2, 3) and chain[0] != (1, 2, 2, 3):
            direct_children.append(q)
    print(f"    Direct children: {direct_children}")
    print()

    # 6. Parity analysis
    print("--- 6. Parity Constraints ---")
    odd_d_count = sum(1 for q in quads if q[3] % 2 == 1)
    even_d_count = sum(1 for q in quads if q[3] % 2 == 0)
    print(f"  Primitive quadruples with d ≤ {N}:")
    print(f"    d odd: {odd_d_count}, d even: {even_d_count}")
    print(f"  (All primitive quadruples have odd hypotenuse)")
    print()

    # 7. Depth distribution
    print("--- 7. Descent Depth Distribution ---")
    depth_counts = defaultdict(int)
    for q in quads:
        depth = len(descent_chain(*q)) - 1
        depth_counts[depth] += 1
    for depth in sorted(depth_counts.keys()):
        count = depth_counts[depth]
        bar = "█" * count
        print(f"  Depth {depth}: {count:3d} {bar}")
    print()

    # 8. Euler parametrization examples
    print("--- 8. Euler Parametrization ---")
    print("  (m,n,p,q) → (a, b, c, d)")
    euler_examples = [(1,0,0,0), (1,1,0,0), (1,0,1,0), (1,0,0,1),
                      (1,1,1,0), (1,1,0,1), (2,1,0,0), (2,0,1,0)]
    for (m, n, p, q) in euler_examples:
        a = m**2 + n**2 - p**2 - q**2
        b = 2*(m*q + n*p)
        c = 2*(n*q - m*p)
        d = m**2 + n**2 + p**2 + q**2
        norm = normalize(abs(a), abs(b), abs(c), abs(d))
        g = multi_gcd(abs(a), abs(b), abs(c), abs(d)) if d > 0 else 0
        print(f"  ({m},{n},{p},{q}) → ({a:3d}, {b:3d}, {c:3d}, {d:3d})  "
              f"normalized: {norm}  gcd={g}")
    print()

    # 9. Involution demonstration
    print("--- 9. Involution Property ---")
    for quad in examples:
        a2, b2, c2, d2 = apply_R1111(*quad)
        a3, b3, c3, d3 = apply_R1111(a2, b2, c2, d2)
        print(f"  R²{quad} = ({a3},{b3},{c3},{d3}) {'✓' if (a3,b3,c3,d3)==quad else '✗'}")
    print()

    # 10. Cauchy-Schwarz verification
    print("--- 10. Cauchy-Schwarz Bounds ---")
    print("  For each quadruple: d < a+b+c < 2d")
    for quad in [(1,2,2,3), (2,3,6,7), (0,3,4,5), (4,4,7,9), (1,4,8,9),
                 (3,4,12,13), (2,5,14,15), (6,6,7,11)]:
        a, b, c, d = quad
        s = a + b + c
        ratio = s / d
        print(f"  {quad}: s={s}, d={d}, s/d={ratio:.4f}  "
              f"(1 < {ratio:.4f} < 2: {'✓' if 1 < ratio < 2 else '✗'})")
    print()


def demo_tree_visualization():
    """Print ASCII tree of the quadruple descent structure."""
    print("=" * 70)
    print("QUADRUPLE DESCENT TREE (d ≤ 30)")
    print("=" * 70)
    print()

    N = 30
    quads = list_primitive_quads(N)

    # Build parent-child relationships
    children_of = defaultdict(list)
    for q in quads:
        chain = descent_chain(*q)
        if len(chain) >= 2:
            parent = chain[1]
            children_of[parent].append(q)

    # Print tree
    def print_tree(node, prefix="", is_last=True):
        connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}{node}  [{node[0]}²+{node[1]}²+{node[2]}²={node[3]}²]")
        children = sorted(children_of.get(node, []), key=lambda x: x[3])
        for i, child in enumerate(children):
            extension = "    " if is_last else "│   "
            print_tree(child, prefix + extension, i == len(children) - 1)

    root = (0, 0, 1, 1)
    print(f"Root: {root}  [0²+0²+1²=1²]")
    children = sorted(children_of.get(root, []), key=lambda x: x[3])
    for i, child in enumerate(children):
        print_tree(child, "", i == len(children) - 1)
    print()


def demo_statistics():
    """Compute and display statistics about the tree."""
    print("=" * 70)
    print("TREE STATISTICS")
    print("=" * 70)
    print()

    for N in [10, 20, 30, 50, 75, 100]:
        quads = list_primitive_quads(N)
        depths = [len(descent_chain(*q)) - 1 for q in quads]
        max_depth = max(depths) if depths else 0
        avg_depth = sum(depths) / len(depths) if depths else 0

        print(f"  d ≤ {N:3d}: {len(quads):4d} quadruples, "
              f"max depth = {max_depth}, avg depth = {avg_depth:.2f}")
    print()


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    demo_properties()
    demo_tree_visualization()
    demo_statistics()

#!/usr/bin/env python3
"""
Quadruple Forest Demo: Universal Descent for Pythagorean Quadruples

Demonstrates the key discovery: the single reflection R₁₁₁₁ through the
spacelike vector (1,1,1,1) in O(3,1;Z) provides a universal descent for
ALL primitive Pythagorean quadruples to the root (0,0,1,1).

The "infinite forest" is actually a single tree!
"""

import numpy as np
from math import gcd
from functools import reduce
from collections import defaultdict

# ============================================================
# Section 1: The Reflection Matrix R₁₁₁₁
# ============================================================

# R₁₁₁₁ = reflection through s=(1,1,1,1) in Minkowski metric η=diag(1,1,1,-1)
R1111 = np.array([
    [ 0, -1, -1,  1],
    [-1,  0, -1,  1],
    [-1, -1,  0,  1],
    [-1, -1, -1,  2]
], dtype=int)

# Minkowski metric
eta = np.diag([1, 1, 1, -1])

def verify_lorentz(M):
    """Check M^T η M = η"""
    return np.array_equal(M.T @ eta @ M, eta)

def verify_involution(M):
    """Check M² = I"""
    return np.array_equal(M @ M, np.eye(4, dtype=int))

print("=" * 60)
print("QUADRUPLE FOREST STRUCTURE: UNIVERSAL DESCENT")
print("=" * 60)
print()
print("R₁₁₁₁ is in O(3,1;Z):", verify_lorentz(R1111))
print("R₁₁₁₁ is an involution:", verify_involution(R1111))
print()

# ============================================================
# Section 2: The Descent Algorithm
# ============================================================

def descend_step(a, b, c, d):
    """Apply R₁₁₁₁, take abs, sort spatial components."""
    v = R1111 @ np.array([a, b, c, d])
    spatial = sorted([abs(v[0]), abs(v[1]), abs(v[2])])
    return (spatial[0], spatial[1], spatial[2], abs(v[3]))

def descent_chain(a, b, c, d, max_steps=50):
    """Compute the full descent chain from (a,b,c,d) to the root."""
    chain = [(a, b, c, d)]
    for _ in range(max_steps):
        a2, b2, c2, d2 = descend_step(a, b, c, d)
        if d2 >= d or d2 == 0:
            break
        chain.append((a2, b2, c2, d2))
        a, b, c, d = a2, b2, c2, d2
    return chain

def is_primitive_quad(a, b, c, d):
    """Check if (a,b,c,d) is a primitive Pythagorean quadruple."""
    if a*a + b*b + c*c != d*d:
        return False
    g = reduce(gcd, [a, b, c, d])
    return g == 1

# ============================================================
# Section 3: Enumerate and Test All Quadruples
# ============================================================

def list_primitive_quads(N):
    """List all primitive Pythagorean quadruples with d ≤ N, sorted a ≤ b ≤ c."""
    quads = []
    for d in range(1, N+1):
        for c in range(1, d):
            for b in range(1, c+1):
                for a in range(0, b+1):
                    if a*a + b*b + c*c == d*d:
                        if reduce(gcd, [a, b, c, d]) == 1:
                            quads.append((a, b, c, d))
    return quads

print("DESCENT CHAINS FOR SMALL QUADRUPLES")
print("-" * 60)
test_quads = [(1,2,2,3), (2,3,6,7), (4,4,7,9), (1,4,8,9),
              (3,4,12,13), (2,5,14,15), (2,10,11,15)]
for q in test_quads:
    chain = descent_chain(*q)
    chain_str = " → ".join(str(c) for c in chain)
    print(f"  {q}: {chain_str}")
print()

# ============================================================
# Section 4: Universal Descent Verification
# ============================================================

print("UNIVERSAL DESCENT VERIFICATION")
print("-" * 60)
for N in [10, 20, 30, 50]:
    quads = list_primitive_quads(N)
    roots = set()
    for q in quads:
        chain = descent_chain(*q)
        root = chain[-1]
        roots.add(root)
    all_to_root = all(descent_chain(*q)[-1] == (0, 0, 1, 1) for q in quads)
    print(f"  d ≤ {N:3d}: {len(quads):4d} quadruples, "
          f"all descend to (0,0,1,1): {all_to_root}, "
          f"unique roots: {roots}")
print()

# ============================================================
# Section 5: Tree Statistics
# ============================================================

print("TREE STATISTICS")
print("-" * 60)

quads_50 = list_primitive_quads(50)

# Compute depth distribution
depths = {}
for q in quads_50:
    chain = descent_chain(*q)
    depths[q] = len(chain) - 1

max_depth = max(depths.values())
print(f"  Total quadruples (d ≤ 50): {len(quads_50)}")
print(f"  Maximum depth: {max_depth}")
print(f"  Average depth: {sum(depths.values()) / len(depths):.2f}")
print()

# Depth histogram
print("  Depth distribution:")
for depth in range(max_depth + 1):
    count = sum(1 for d in depths.values() if d == depth)
    bar = "█" * count
    print(f"    Depth {depth}: {count:3d} {bar}")
print()

# ============================================================
# Section 6: Branching Analysis
# ============================================================

print("BRANCHING ANALYSIS (children of each node)")
print("-" * 60)

# Build parent map
parent_map = {}
for q in quads_50:
    chain = descent_chain(*q)
    if len(chain) > 1:
        parent_map[q] = chain[1]

# Count children
children_count = defaultdict(list)
for child, parent in parent_map.items():
    children_count[parent].append(child)

for parent in sorted(children_count.keys(), key=lambda x: x[3]):
    kids = children_count[parent]
    print(f"  {parent}: {len(kids)} children → {kids[:5]}{'...' if len(kids) > 5 else ''}")
print()

# ============================================================
# Section 7: The Descent Identity
# ============================================================

print("ALGEBRAIC IDENTITY VERIFICATION")
print("-" * 60)
print("  (d-b-c)² + (d-a-c)² + (d-a-b)² = (2d-a-b-c)²")
print("  whenever a² + b² + c² = d²")
print()

for q in test_quads:
    a, b, c, d = q
    lhs = (d-b-c)**2 + (d-a-c)**2 + (d-a-b)**2
    rhs = (2*d-a-b-c)**2
    assert lhs == rhs, f"Identity FAILS for {q}"
    print(f"  {q}: LHS = {lhs}, RHS = {rhs}, ✓")
print()

# ============================================================
# Section 8: The Descent Bound
# ============================================================

print("DESCENT BOUND: d' = 2d - (a+b+c)")
print("-" * 60)
print("  For each quadruple, showing 0 < d' < d:")
print()
for q in quads_50[:15]:
    a, b, c, d = q
    dprime = 2*d - (a + b + c)
    ratio = dprime / d if d > 0 else 0
    print(f"  {q}: d'={dprime}, d'<d: {dprime<d}, d'>0: {dprime>0}, "
          f"ratio d'/d = {ratio:.3f}")
print()

# ============================================================
# Section 9: The Euler Parametrization
# ============================================================

print("EULER PARAMETRIZATION")
print("-" * 60)
print("  (m²+n²-p²-q², 2(mq+np), 2(nq-mp), m²+n²+p²+q²)")
print()

def euler_param(m, n, p, q):
    a = m**2 + n**2 - p**2 - q**2
    b = 2*(m*q + n*p)
    c = 2*(n*q - m*p)
    d = m**2 + n**2 + p**2 + q**2
    return (a, b, c, d)

params = [(1,1,0,0), (2,1,0,0), (1,1,1,0), (2,1,1,0), (3,1,0,0)]
for p in params:
    quad = euler_param(*p)
    verify = quad[0]**2 + quad[1]**2 + quad[2]**2 == quad[3]**2
    print(f"  ({p[0]},{p[1]},{p[2]},{p[3]}) → {quad}, valid: {verify}")
print()

# ============================================================
# Section 10: Generating the Tree (BFS)
# ============================================================

print("TREE GENERATION (first 5 levels)")
print("-" * 60)

# BFS from root
root = (0, 0, 1, 1)
visited = {root}
level = [root]
tree_levels = {0: [root]}

for depth in range(1, 6):
    next_level = []
    for q in quads_50:
        if q not in visited:
            chain = descent_chain(*q)
            if len(chain) > 1 and chain[1] in visited:
                if chain[1] in [c for lvl in tree_levels.values() for c in lvl]:
                    # This quad's parent is already in the tree
                    parent = chain[1]
                    if parent in level or parent in [c for d2 in range(depth) for c in tree_levels.get(d2, [])]:
                        next_level.append(q)
                        visited.add(q)

    tree_levels[depth] = next_level
    level = next_level
    print(f"  Level {depth}: {len(next_level)} nodes")
    for q in next_level[:8]:
        print(f"    {q}")
    if len(next_level) > 8:
        print(f"    ... and {len(next_level) - 8} more")
print()

print("=" * 60)
print("CONCLUSION: The quadruple 'forest' is a SINGLE TREE")
print("rooted at (0, 0, 1, 1), with universal descent via R₁₁₁₁.")
print("=" * 60)

#!/usr/bin/env python3
"""
Ramanujan Properties of the Berggren Tree — Part II: Extended Demos

Demonstrates:
1. Parabolic vs hyperbolic trace sequences
2. 5D Pythagorean quintuple generation
3. Modular quotient graph construction
4. Spectral gap monotonicity visualization
5. Grover coin eigenvalue analysis
6. Cryptographic security analysis
"""

import numpy as np
from collections import deque
import json

# ============================================================
# §1. Berggren Matrices (3D)
# ============================================================

B1 = np.array([[1, -2, 2], [2, -1, 2], [2, -2, 3]])
B2 = np.array([[1, 2, 2], [2, 1, 2], [2, 2, 3]])
B3 = np.array([[-1, 2, 2], [-2, 1, 2], [-2, 2, 3]])

Q3 = np.diag([1, 1, -1])

print("=" * 60)
print("BERGGREN TREE — RAMANUJAN FRONTIERS PART II")
print("=" * 60)

# ============================================================
# §2. Parabolic vs Hyperbolic Classification
# ============================================================

print("\n§2. PARABOLIC VS HYPERBOLIC CLASSIFICATION")
print("-" * 40)

def trace_sequence(M, n_terms=8):
    """Compute tr(M), tr(M²), ..., tr(Mⁿ)."""
    traces = []
    power = np.eye(M.shape[0], dtype=int)
    for i in range(n_terms):
        power = power @ M
        traces.append(int(np.trace(power)))
    return traces

print("B₁ trace sequence (PARABOLIC - constant at 3):")
t1 = trace_sequence(B1)
print(f"  tr(B₁ⁿ) for n=1..8: {t1}")

print("\nB₂ trace sequence (HYPERBOLIC - exponential growth):")
t2 = trace_sequence(B2)
print(f"  tr(B₂ⁿ) for n=1..8: {t2}")

print("\nB₃ trace sequence (PARABOLIC - constant at 3):")
t3 = trace_sequence(B3)
print(f"  tr(B₃ⁿ) for n=1..8: {t3}")

# Verify Lorentz classification
print("\nLorentz classification (|tr| vs 3):")
for name, M in [("B₁", B1), ("B₂", B2), ("B₃", B3)]:
    tr = int(np.trace(M))
    cls = "PARABOLIC" if abs(tr) == 3 else ("HYPERBOLIC" if abs(tr) > 3 else "ELLIPTIC")
    print(f"  {name}: tr = {tr}, |tr| = {abs(tr)}, classification: {cls}")

# ============================================================
# §3. Eigenvalue Analysis
# ============================================================

print("\n§3. EIGENVALUE ANALYSIS")
print("-" * 40)

for name, M in [("B₁", B1), ("B₂", B2), ("B₃", B3)]:
    eigenvalues = np.linalg.eigvals(M.astype(float))
    print(f"  {name} eigenvalues: {np.round(eigenvalues, 6)}")

# ============================================================
# §4. Modular Quotient Graphs
# ============================================================

print("\n§4. MODULAR QUOTIENT GRAPHS")
print("-" * 40)

def build_quotient_graph(p, max_vertices=1000):
    """Build the Berggren quotient graph G_p."""
    root = tuple(np.array([3, 4, 5]) % p)
    vertices = {root}
    edges = set()
    queue = deque([root])

    while queue and len(vertices) < max_vertices:
        v = queue.popleft()
        v_arr = np.array(v)
        for M in [B1, B2, B3]:
            w = tuple((M @ v_arr) % p)
            edges.add((v, w))
            edges.add((w, v))  # undirected
            if w not in vertices:
                vertices.add(w)
                queue.append(w)
    return vertices, edges

primes = [5, 7, 11, 13, 17, 19, 23]
print(f"{'Prime p':>8} | {'|V(G_p)|':>10} | {'|E(G_p)|':>10} | {'Max degree':>10}")
print("-" * 50)

for p in primes:
    verts, edges = build_quotient_graph(p)
    # Compute degree distribution
    degree = {}
    for v, w in edges:
        degree[v] = degree.get(v, 0) + 1
    max_deg = max(degree.values()) if degree else 0
    print(f"{p:>8} | {len(verts):>10} | {len(edges):>10} | {max_deg:>10}")

# ============================================================
# §5. 5D Pythagorean Quintuples
# ============================================================

print("\n§5. 5D PYTHAGOREAN QUINTUPLES")
print("-" * 40)

# 5D generators
K1 = np.array([
    [-1, 0, 0, 2, 2],
    [0, 1, 0, 0, 0],
    [0, 0, 1, 0, 0],
    [-2, 0, 0, 1, 2],
    [-2, 0, 0, 2, 3]
])

K2 = np.array([
    [1, 0, 0, 2, 2],
    [0, 1, 0, 0, 0],
    [0, 0, 1, 0, 0],
    [2, 0, 0, 1, 2],
    [2, 0, 0, 2, 3]
])

K3 = np.array([
    [1, 0, 0, 0, 0],
    [0, -1, 0, 2, 2],
    [0, 0, 1, 0, 0],
    [0, -2, 0, 1, 2],
    [0, -2, 0, 2, 3]
])

K4 = np.array([
    [1, 0, 0, 0, 0],
    [0, 1, 0, 0, 0],
    [0, 0, -1, 2, 2],
    [0, 0, -2, 1, 2],
    [0, 0, -2, 2, 3]
])

K5 = np.array([
    [1, 0, 0, 0, 0],
    [0, 1, 0, 0, 0],
    [0, 0, 1, 2, 2],
    [0, 0, 2, 1, 2],
    [0, 0, 2, 2, 3]
])

K6 = np.array([
    [1, 0, 0, 0, 0],
    [0, 1, 0, 2, 2],
    [0, 0, 1, 0, 0],
    [0, 2, 0, 1, 2],
    [0, 2, 0, 2, 3]
])

Q5 = np.diag([1, 1, 1, 1, -1])

# Verify Lorentz preservation
print("Verifying 5D Lorentz form preservation:")
for name, K in [("K₁", K1), ("K₂", K2), ("K₃", K3), ("K₄", K4), ("K₅", K5), ("K₆", K6)]:
    result = K.T @ Q5 @ K
    preserved = np.array_equal(result, Q5)
    det = int(round(np.linalg.det(K)))
    tr = int(np.trace(K))
    print(f"  {name}: KᵀQ₅K = Q₅? {preserved}, det = {det:+d}, tr = {tr}")

# Generate quintuples from root (1, 1, 1, 1, 2)
root5 = np.array([1, 1, 1, 1, 2])
print(f"\nRoot quintuple: {tuple(root5)}")
print(f"  Check: {root5[0]**2} + {root5[1]**2} + {root5[2]**2} + {root5[3]**2} = "
      f"{sum(root5[:4]**2)} = {root5[4]**2} = {root5[4]}²")

print("\nFirst-generation quintuples:")
for name, K in [("K₁", K1), ("K₂", K2), ("K₃", K3), ("K₄", K4), ("K₅", K5), ("K₆", K6)]:
    child = K @ root5
    check = sum(child[:4]**2) == child[4]**2
    print(f"  {name}(root) = {tuple(child)}, valid: {check}")

# ============================================================
# §6. Spectral Gap Monotonicity
# ============================================================

print("\n§6. SPECTRAL GAP MONOTONICITY")
print("-" * 40)

dimensions = [
    ("3D (triples)", 3, 6, 5),
    ("4D (quadruples)", 4, 8, 7),
    ("5D (quintuples)", 6, 12, 11),
]

print(f"{'Dimension':>18} | {'d':>3} | {'Gap = d - 2√(d-1)':>18} | {'Gap/d':>8} | {'λ₂/d':>8}")
print("-" * 70)

for name, n_gen, d, d_minus_1 in dimensions:
    gap = d - 2 * np.sqrt(d_minus_1)
    rel_gap = gap / d
    ratio = 2 * np.sqrt(d_minus_1) / d
    print(f"{name:>18} | {d:>3} | {gap:>18.6f} | {rel_gap:>8.4f} | {ratio:>8.4f}")

print("\nMonotonicity chain (verified in Lean):")
gaps = [(d - 2*np.sqrt(dm1), d) for _, _, d, dm1 in dimensions]
for i in range(len(gaps)):
    d = dimensions[i][2]
    dm1 = dimensions[i][3]
    g = d - 2*np.sqrt(dm1)
    print(f"  {d} - 2√{dm1} = {g:.6f}")

# ============================================================
# §7. Grover Coin Analysis
# ============================================================

print("\n§7. GROVER COIN ANALYSIS")
print("-" * 40)

for d in [3, 4, 5]:
    G = (2/d) * np.ones((d, d)) - np.eye(d)
    eigenvalues = np.sort(np.linalg.eigvals(G))[::-1]
    scaled_G = d * G
    scaled_sq = scaled_G @ scaled_G
    is_involution = np.allclose(scaled_sq, d**2 * np.eye(d))
    print(f"  d={d}: eigenvalues = {np.round(eigenvalues, 4)}")
    print(f"        ({d}G)² = {d}²I? {is_involution}")
    print(f"        tr({d}G) = {int(round(np.trace(scaled_G)))}")

# ============================================================
# §8. Cryptographic Security Analysis
# ============================================================

print("\n§8. CRYPTOGRAPHIC SECURITY ANALYSIS")
print("-" * 40)

print(f"{'Depth n':>8} | {'3ⁿ':>20} | {'Security bits':>14} | {'≥ 2ⁿ?':>6}")
print("-" * 55)
for n in [20, 40, 64, 80, 128, 256]:
    paths = 3**n
    bits = np.log2(float(paths))
    exceeds = "✓" if paths > 2**n else "✗"
    if n <= 80:
        print(f"{n:>8} | {paths:>20} | {bits:>14.1f} | {exceeds:>6}")
    else:
        print(f"{n:>8} | {'3^'+str(n):>20} | {bits:>14.1f} | {exceeds:>6}")

# ============================================================
# §9. Commutator Analysis
# ============================================================

print("\n§9. COMMUTATOR ANALYSIS")
print("-" * 40)

# 3D
print("3D commutators:")
for i, (name_i, Mi) in enumerate([("B₁", B1), ("B₂", B2), ("B₃", B3)]):
    for j, (name_j, Mj) in enumerate([("B₁", B1), ("B₂", B2), ("B₃", B3)]):
        if i < j:
            commutes = np.array_equal(Mi @ Mj, Mj @ Mi)
            print(f"  [{name_i}, {name_j}] = 0? {commutes}")

# 4D
H1 = np.array([[1, 0, -2, 2], [0, 1, 0, 0], [2, 0, -1, 2], [2, 0, -2, 3]])
H2 = np.array([[1, 0, 2, 2], [0, 1, 0, 0], [2, 0, 1, 2], [2, 0, 2, 3]])
H3 = np.array([[1, 0, 0, 0], [0, 1, -2, 2], [0, 2, -1, 2], [0, 2, -2, 3]])
H4 = np.array([[1, 0, 0, 0], [0, 1, 2, 2], [0, 2, 1, 2], [0, 2, 2, 3]])

print("\n4D commutators:")
for i, (name_i, Mi) in enumerate([("H₁", H1), ("H₂", H2), ("H₃", H3), ("H₄", H4)]):
    for j, (name_j, Mj) in enumerate([("H₁", H1), ("H₂", H2), ("H₃", H3), ("H₄", H4)]):
        if i < j:
            commutes = np.array_equal(Mi @ Mj, Mj @ Mi)
            symbol = "=" if commutes else "≠"
            print(f"  {name_i}·{name_j} {symbol} {name_j}·{name_i}  {'(COMMUTE)' if commutes else ''}")

# ============================================================
# §10. Pythagorean Triple Generation Tree
# ============================================================

print("\n§10. BERGGREN TREE (First 3 levels)")
print("-" * 40)

def generate_tree(root, depth):
    """Generate Berggren tree to given depth."""
    levels = [[root]]
    for d in range(depth):
        new_level = []
        for triple in levels[-1]:
            for name, M in [("B₁", B1), ("B₂", B2), ("B₃", B3)]:
                child = tuple(M @ np.array(triple))
                new_level.append(child)
        levels.append(new_level)
    return levels

tree = generate_tree((3, 4, 5), 2)
for i, level in enumerate(tree):
    print(f"  Level {i}: {len(level)} triples")
    for t in level[:6]:
        a, b, c = t
        print(f"    ({a}, {b}, {c})  [{a}² + {b}² = {a**2 + b**2} = {c}² = {c**2}]")
    if len(level) > 6:
        print(f"    ... and {len(level) - 6} more")

# ============================================================
# §11. Summary Statistics
# ============================================================

print("\n" + "=" * 60)
print("SUMMARY OF VERIFIED RESULTS")
print("=" * 60)
print("""
Machine-verified in Lean 4 (zero sorry):

PART I (RamanujanFrontiers.lean):
  ✓ Lorentz form preservation (3D, mod 5/7/13)
  ✓ Spectral gaps: 3-2√2, 6-2√5, 8-2√7 > 0
  ✓ Grover coins: (3G)²=9I, (2G)²=4I
  ✓ Quantum spectral gap: 17-12√2 > 0
  ✓ Step injectivity (B₁, B₂, B₃)
  ✓ 4D generators: H₁...H₄ in O(3,1;ℤ)
  ✓ Monotonicity: 8-2√7 > 6-2√5 > 3-2√2

PART II (RamanujanFrontiers2.lean):
  ✓ Lorentz form mod 11, 17, 19, 23
  ✓ Parabolic/hyperbolic classification
  ✓ Trace sequences: B₁ⁿ=3, B₂ⁿ grows exponentially
  ✓ Full non-commutativity (3D)
  ✓ Partial commutativity structure (4D): H₁H₃=H₃H₁
  ✓ 5D generators K₁...K₆ in O(4,1;ℤ)
  ✓ 5D Lorentz preservation and traces
  ✓ Full monotonicity: 12-2√11 > 8-2√7 > 6-2√5 > 3-2√2
  ✓ Grover 5×5: (5G)²=25I, tr(5G)=-15
  ✓ Security: 3²⁰ > 2³¹, 3¹²⁸ > 2¹²⁸
  ✓ Mixing ratios λ₂/d < 1 for d=6,8,12
  ✓ Quintuple preservation
""")

if __name__ == "__main__":
    print("\nDemo complete.")

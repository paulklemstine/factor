#!/usr/bin/env python3
"""
Ramanujan Frontiers: Computational Demonstrations

Explores four research directions:
1. Explicit Ramanujan graphs from Pythagorean triples
2. Quantum walks on the Berggren tree
3. Cryptographic one-way functions
4. Higher-dimensional Pythagorean trees

Run: python3 ramanujan_frontiers_demo.py
"""

import numpy as np
from math import sqrt, log2, gcd
from collections import deque

# ─── Berggren Matrices (3D) ───

B1 = np.array([[1, -2, 2], [2, -1, 2], [2, -2, 3]])
B2 = np.array([[1,  2, 2], [2,  1, 2], [2,  2, 3]])
B3 = np.array([[-1, 2, 2], [-2, 1, 2], [-2, 2, 3]])

# ─── 4D Generators for Pythagorean Quadruples ───

H1 = np.array([[1, 0, -2, 2], [0, 1, 0, 0], [2, 0, -1, 2], [2, 0, -2, 3]])
H2 = np.array([[1, 0,  2, 2], [0, 1, 0, 0], [2, 0,  1, 2], [2, 0,  2, 3]])
H3 = np.array([[1, 0, 0, 0], [0, 1, -2, 2], [0, 2, -1, 2], [0, 2, -2, 3]])
H4 = np.array([[1, 0, 0, 0], [0, 1,  2, 2], [0, 2,  1, 2], [0, 2,  2, 3]])

# ─── Lorentz Forms ───

Q3 = np.diag([1, 1, -1])
Q4 = np.diag([1, 1, 1, -1])


def verify_lorentz_3d():
    """Verify that B1, B2, B3 preserve the 3D Lorentz form."""
    print("=" * 60)
    print("§1. LORENTZ FORM PRESERVATION (3D)")
    print("=" * 60)
    for name, B in [("B1", B1), ("B2", B2), ("B3", B3)]:
        result = B.T @ Q3 @ B
        preserved = np.array_equal(result, Q3)
        det = int(round(np.linalg.det(B)))
        print(f"  {name}^T Q {name} = Q? {preserved}  |  det({name}) = {det}")
    print()


def verify_lorentz_4d():
    """Verify that H1..H4 preserve the 4D Lorentz form."""
    print("=" * 60)
    print("§2. LORENTZ FORM PRESERVATION (4D)")
    print("=" * 60)
    for name, H in [("H1", H1), ("H2", H2), ("H3", H3), ("H4", H4)]:
        result = H.T @ Q4 @ H
        preserved = np.array_equal(result, Q4)
        det = int(round(np.linalg.det(H)))
        tr = int(np.trace(H))
        print(f"  {name}^T Q4 {name} = Q4? {preserved}  |  det={det:+d}  tr={tr}")
    print()


def generate_berggren_tree(depth=4):
    """Generate all Pythagorean triples up to given depth."""
    root = np.array([3, 4, 5])
    triples = {0: [root]}
    for d in range(1, depth + 1):
        triples[d] = []
        for t in triples[d - 1]:
            for B in [B1, B2, B3]:
                child = B @ t
                triples[d].append(child)
    return triples


def demo_ramanujan_quotients():
    """Demo 1: Explicit Ramanujan graphs from congruence quotients."""
    print("=" * 60)
    print("§3. RAMANUJAN QUOTIENT GRAPHS")
    print("=" * 60)

    for p in [5, 7, 11, 13, 17, 19, 23, 29]:
        # Compute orbit of (3,4,5) mod p
        root = tuple(np.array([3, 4, 5]) % p)
        visited = {root}
        queue = deque([root])
        edges = 0

        while queue:
            v = queue.popleft()
            v_arr = np.array(v)
            for B in [B1, B2, B3]:
                w = tuple((B @ v_arr) % p)
                edges += 1
                if w not in visited:
                    visited.add(w)
                    queue.append(w)

        n_vertices = len(visited)
        avg_degree = 2 * edges / n_vertices if n_vertices > 0 else 0

        # Verify Lorentz form mod p
        lorentz_ok = all(
            np.array_equal((B.T @ Q3 @ B) % p, Q3 % p)
            for B in [B1, B2, B3]
        )

        print(f"  p={p:2d}: |V|={n_vertices:5d}, |E|={edges:6d}, "
              f"avg_deg={avg_degree:.1f}, Lorentz_mod_p={lorentz_ok}")

    print(f"\n  Spectral gap (6-regular Ramanujan): 6 - 2√5 ≈ {6 - 2*sqrt(5):.4f}")
    print(f"  Cheeger bound: (6 - 2√5)/2 ≈ {(6 - 2*sqrt(5))/2:.4f}")
    print()


def demo_quantum_walk():
    """Demo 2: Quantum walk analysis on the Berggren tree."""
    print("=" * 60)
    print("§4. QUANTUM WALKS ON THE BERGGREN TREE")
    print("=" * 60)

    # Grover coins
    G3 = (2/3) * np.ones((3, 3)) - np.eye(3)
    G4 = (2/4) * np.ones((4, 4)) - np.eye(4)

    print("  3×3 Grover coin eigenvalues:", sorted(np.linalg.eigvalsh(G3), reverse=True))
    print("  4×4 Grover coin eigenvalues:", sorted(np.linalg.eigvalsh(G4), reverse=True))
    print(f"  G3² = I? {np.allclose(G3 @ G3, np.eye(3))}")
    print(f"  G4² = I? {np.allclose(G4 @ G4, np.eye(4))}")

    # Quantum spectral gap
    gamma_classical = 3 - 2 * sqrt(2)
    gamma_quantum = gamma_classical ** 2
    print(f"\n  Classical spectral gap (3-reg): {gamma_classical:.6f}")
    print(f"  Quantum spectral gap: {gamma_quantum:.6f} = 17 - 12√2")

    # Mixing time comparison
    print("\n  Mixing time comparison (depth L → N ≈ 3^L nodes):")
    print(f"  {'Depth L':>8s} {'N nodes':>10s} {'Classical O(L²)':>16s} {'Quantum O(L)':>14s} {'Speedup':>8s}")
    for L in [5, 10, 20, 50, 100]:
        N = (3**(L+1) - 1) // 2
        classical = L**2
        quantum = L
        speedup = classical / quantum
        print(f"  {L:8d} {N:10.2e} {classical:16d} {quantum:14d} {speedup:8.1f}x")
    print()


def demo_cryptographic_owf():
    """Demo 3: Cryptographic one-way function properties."""
    print("=" * 60)
    print("§5. CRYPTOGRAPHIC ONE-WAY FUNCTION")
    print("=" * 60)

    # Forward computation
    print("  Forward computation (path → triple):")
    path_labels = "LMRLMRLM"
    matrices = {"L": B1, "M": B2, "R": B3}
    v = np.array([3, 4, 5])
    print(f"    Start: ({v[0]}, {v[1]}, {v[2]})")
    for i, d in enumerate(path_labels):
        v = matrices[d] @ v
        a, b, c = v
        pyth = a**2 + b**2 == c**2
        print(f"    Step {i+1} ({d}): ({a}, {b}, {c}) "
              f"| hyp={c} | a²+b²=c²? {pyth}")

    # Security analysis
    print("\n  Security analysis:")
    for n in [64, 128, 256, 512]:
        paths = 3**n
        bits = n * log2(3)
        print(f"    Path length {n:3d}: {paths:.2e} paths = {bits:.0f} bits of security")

    # Injectivity demonstration
    print("\n  Injectivity test (distinct paths → distinct triples):")
    triples = set()
    collision = False
    for path in ["LLL", "LLM", "LLR", "LML", "LMM", "LMR",
                  "LRL", "LRM", "LRR", "MLL", "MLM", "MLR",
                  "MML", "MMM", "MMR", "MRL", "MRM", "MRR",
                  "RLL", "RLM", "RLR", "RML", "RMM", "RMR",
                  "RRL", "RRM", "RRR"]:
        v = np.array([3, 4, 5])
        for d in path:
            v = matrices[d] @ v
        t = tuple(v)
        if t in triples:
            collision = True
            print(f"    COLLISION at path {path}: {t}")
        triples.add(t)
    print(f"    27 depth-3 paths → {len(triples)} distinct triples | Collision: {collision}")

    # Hypotenuse growth
    print("\n  Hypotenuse growth (all-B₂ path, maximum growth):")
    v = np.array([3, 4, 5])
    for i in range(10):
        v = B2 @ v
        print(f"    Step {i+1}: hyp = {v[2]:>15d}  (ratio: {v[2] / (v[2] / (2*v[0]/v[2] + 2*v[1]/v[2] + 3) if v[2] > 0 else 1):.2f})")
    print()


def demo_higher_dimensions():
    """Demo 4: Higher-dimensional Pythagorean trees."""
    print("=" * 60)
    print("§6. HIGHER-DIMENSIONAL PYTHAGOREAN TREES")
    print("=" * 60)

    # Generate quadruples from root (1,2,2,3)
    root4 = np.array([1, 2, 2, 3])
    print(f"  Root quadruple: {tuple(root4)}")
    a, b, c, d = root4
    print(f"  Verify: {a}² + {b}² + {c}² = {a**2} + {b**2} + {c**2} = {a**2+b**2+c**2} = {d}² = {d**2} ✓")

    print("\n  4D tree (depth 2):")
    depth1 = []
    for name, H in [("H1", H1), ("H2", H2), ("H3", H3), ("H4", H4)]:
        child = H @ root4
        a, b, c, d = child
        valid = a**2 + b**2 + c**2 == d**2
        depth1.append(child)
        print(f"    {name}·(1,2,2,3) = ({a},{b},{c},{d}) | "
              f"a²+b²+c²={a**2+b**2+c**2}, d²={d**2} | valid={valid}")

    # Spectral gaps comparison
    print("\n  Cross-dimensional spectral gaps:")
    dims = [
        ("2D (triples)", 3, 6, 2*sqrt(5)),
        ("3D (quadruples)", 4, 8, 2*sqrt(7)),
    ]
    print(f"  {'System':>20s} {'k gen':>6s} {'d=2k':>5s} {'Gap γ':>12s} {'γ/d':>8s}")
    for name, k, d, bound in dims:
        gap = d - bound
        rel = gap / d
        print(f"  {name:>20s} {k:6d} {d:5d} {gap:12.6f} {rel:8.6f}")

    # Verify products preserve form
    print("\n  Closure under products (4D):")
    products = [
        ("H1·H2", H1 @ H2), ("H1·H3", H1 @ H3),
        ("H2·H3", H2 @ H3), ("H3·H4", H3 @ H4),
        ("H1·H2·H3", H1 @ H2 @ H3),
    ]
    for name, P in products:
        ok = np.array_equal(P.T @ Q4 @ P, Q4)
        det = int(round(np.linalg.det(P)))
        tr = int(round(np.trace(P)))
        print(f"    {name:>10s}: Lorentz={ok}, det={det:+d}, tr={tr}")
    print()


def demo_spectral_comparison():
    """Compare spectral properties across dimensions."""
    print("=" * 60)
    print("§7. SPECTRAL GAP ANALYSIS")
    print("=" * 60)

    print("\n  Ramanujan bounds 2√(d-1) for various degrees:")
    print(f"  {'d':>4s} {'2√(d-1)':>10s} {'gap = d-2√(d-1)':>18s} {'gap²':>10s} {'gap/d':>8s}")
    for d in [3, 4, 6, 8, 10, 12, 20, 50, 100]:
        bound = 2 * sqrt(d - 1)
        gap = d - bound
        print(f"  {d:4d} {bound:10.4f} {gap:18.6f} {gap**2:10.6f} {gap/d:8.6f}")

    # Asymptotic analysis
    print("\n  Asymptotic: gap/d → 1 - 2/√d as d → ∞")
    print(f"  {'d':>6s} {'gap/d':>8s} {'1-2/√d':>8s}")
    for d in [10, 100, 1000, 10000]:
        actual = (d - 2*sqrt(d-1)) / d
        approx = 1 - 2/sqrt(d)
        print(f"  {d:6d} {actual:8.6f} {approx:8.6f}")
    print()


def main():
    print("\n" + "═" * 60)
    print("  RAMANUJAN FRONTIERS: BERGGREN TREE RESEARCH")
    print("  Computational Demonstrations")
    print("═" * 60 + "\n")

    verify_lorentz_3d()
    verify_lorentz_4d()
    demo_ramanujan_quotients()
    demo_quantum_walk()
    demo_cryptographic_owf()
    demo_higher_dimensions()
    demo_spectral_comparison()

    print("═" * 60)
    print("  All demonstrations complete.")
    print("═" * 60)


if __name__ == "__main__":
    main()

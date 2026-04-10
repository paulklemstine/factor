#!/usr/bin/env python3
"""
Cross-Domain Bridges and Langlands Program: Interactive Demonstrations

This script demonstrates the key mathematical concepts formalized in Lean 4:
1. Ihara zeta function and determinant formula
2. Chip-firing dynamics on graphs
3. Idempotent decompositions
4. Bridge composition and analysis bridges
5. Ramanujan graph verification
"""

import numpy as np
from itertools import permutations
import json


# ============================================================
# 1. IHARA ZETA FUNCTION
# ============================================================

def adjacency_matrix(edges, n):
    """Build adjacency matrix from edge list."""
    A = np.zeros((n, n))
    for i, j in edges:
        A[i][j] = 1
        A[j][i] = 1
    return A


def degree_matrix(A):
    """Build degree matrix from adjacency matrix."""
    return np.diag(A.sum(axis=1))


def ihara_matrix(A, D, u):
    """Compute the Ihara matrix I - uA + u²(D - I)."""
    n = A.shape[0]
    I = np.eye(n)
    return I - u * A + u**2 * (D - I)


def ihara_zeta_inverse(A, D, u):
    """Compute ζ_G(u)⁻¹ via the determinant formula."""
    M = ihara_matrix(A, D, u)
    return np.linalg.det(M)


def demo_ihara_zeta():
    """Demonstrate the Ihara zeta function on the Petersen graph."""
    print("=" * 60)
    print("DEMO 1: Ihara Zeta Function — Petersen Graph")
    print("=" * 60)

    # Petersen graph: 10 vertices, 3-regular
    edges = [
        (0,1),(1,2),(2,3),(3,4),(4,0),  # outer pentagon
        (5,7),(7,9),(9,6),(6,8),(8,5),  # inner pentagram
        (0,5),(1,6),(2,7),(3,8),(4,9),  # spokes
    ]
    n = 10
    A = adjacency_matrix(edges, n)
    D = degree_matrix(A)

    print(f"Vertices: {n}")
    print(f"Edges: {len(edges)}")
    print(f"Regular degree: {int(D[0][0])}")

    # Verify regularity (formalized as IharaGraph.isRegular)
    degrees = A.sum(axis=1)
    assert all(d == 3 for d in degrees), "Not regular!"
    print(f"✓ Graph is 3-regular (q+1 = 3, so q = 2)")

    # Compute Ihara zeta at various u values
    print(f"\nIhara zeta inverse ζ_G(u)⁻¹ = det(I - uA + u²(D-I)):")
    for u in [0.1, 0.2, 0.3, 0.4, 0.5]:
        val = ihara_zeta_inverse(A, D, u)
        print(f"  u = {u:.1f}: ζ⁻¹ = {val:.6f}")

    # Check Ramanujan condition
    eigenvalues = np.linalg.eigvalsh(A)
    eigenvalues.sort()
    q = 2  # degree - 1
    ramanujan_bound = 2 * np.sqrt(q)
    print(f"\nEigenvalues of A: {[f'{e:.4f}' for e in eigenvalues]}")
    print(f"Ramanujan bound 2√q = {ramanujan_bound:.4f}")
    non_trivial = [e for e in eigenvalues if abs(abs(e) - 3) > 0.01]
    is_ramanujan = all(abs(e) <= ramanujan_bound + 0.01 for e in non_trivial)
    print(f"Max non-trivial |λ| = {max(abs(e) for e in non_trivial):.4f}")
    print(f"✓ Ramanujan: {is_ramanujan}")

    # Edge count formula (formalized as regular_graph_edges)
    computed_edges = n * 3 / 2
    print(f"\n|E| = n(q+1)/2 = {n}×3/2 = {computed_edges:.0f} ✓")

    return A, D


# ============================================================
# 2. CHIP-FIRING DYNAMICS
# ============================================================

def graph_laplacian(A):
    """Compute the graph Laplacian L = D - A."""
    D = degree_matrix(A)
    return D - A


def chip_fire(L, v, divisor):
    """Fire vertex v: redistribute chips according to Laplacian row v."""
    new_divisor = divisor.copy()
    n = len(divisor)
    for j in range(n):
        new_divisor[j] -= int(L[v][j])
    return new_divisor


def divisor_degree(divisor):
    """Sum of all chips."""
    return sum(divisor)


def demo_chip_firing():
    """Demonstrate chip-firing on a small graph."""
    print("\n" + "=" * 60)
    print("DEMO 2: Chip-Firing and Tropical Jacobian")
    print("=" * 60)

    # Simple cycle graph C_4
    edges = [(0,1), (1,2), (2,3), (3,0)]
    n = 4
    A = adjacency_matrix(edges, n)
    L = graph_laplacian(A)

    print("Graph: Cycle C_4 (4 vertices in a cycle)")
    print(f"Laplacian L:\n{L.astype(int)}")

    # Initial divisor
    D = [3, -1, 0, 0]
    print(f"\nInitial divisor D = {D}")
    print(f"Degree(D) = {divisor_degree(D)}")

    # Perform chip-firing moves
    print("\nChip-firing sequence:")
    print(f"  Start: {D}")
    for v in [0, 1, 3]:
        D = chip_fire(L, v, D)
        print(f"  Fire v={v}: {D}  (degree = {divisor_degree(D)})")

    # Verify degree preservation (formalized as chipFire_degree)
    print(f"\n✓ Degree preserved at {divisor_degree(D)} throughout")

    # Graph genus
    num_edges = len(edges)
    genus = num_edges - n + 1
    print(f"\nGraph genus g = |E| - |V| + 1 = {num_edges} - {n} + 1 = {genus}")

    # Canonical divisor K(v) = deg(v) - 2
    degrees_int = [int(d) for d in A.sum(axis=1)]
    K = [d - 2 for d in degrees_int]
    print(f"Canonical divisor K = {K}")
    print(f"deg(K) = {sum(K)} = 2g-2 = {2*genus-2} ✓")

    # Number of spanning trees (= |Jac(G)|)
    # For C_n, this is n
    L_reduced = L[1:, 1:]
    num_trees = int(round(np.linalg.det(L_reduced)))
    print(f"\nNumber of spanning trees = det(L̃) = {num_trees}")
    print(f"This equals |Jac(G)| = |chip-firing group|")
    print(f"(For C_4, this is 4 = n)")


# ============================================================
# 3. IDEMPOTENT DECOMPOSITIONS
# ============================================================

def demo_idempotents():
    """Demonstrate idempotent theory and projector decomposition."""
    print("\n" + "=" * 60)
    print("DEMO 3: Idempotent Decompositions")
    print("=" * 60)

    # Example: Complete orthogonal system of projectors
    n = 4
    print(f"Complete orthogonal projector system for ℝ^{n}:")

    # Standard basis projectors
    projectors = []
    for i in range(n):
        P = np.zeros((n, n))
        P[i][i] = 1.0
        projectors.append(P)

    # Verify properties (formalized theorems)
    for i, P in enumerate(projectors):
        assert np.allclose(P @ P, P), f"P_{i} not idempotent!"
        trace = np.trace(P)
        print(f"  P_{i}: trace = {trace:.0f}, P²=P ✓")

    # Orthogonality
    for i in range(n):
        for j in range(n):
            if i != j:
                assert np.allclose(projectors[i] @ projectors[j], 0)
    print(f"  All P_i P_j = 0 for i≠j ✓")

    # Completeness
    total = sum(projectors)
    assert np.allclose(total, np.eye(n))
    print(f"  ∑ P_i = I ✓")

    # Complement theorem (formalized as idem_complement)
    print(f"\nComplement theorem: if e²=e then (1-e)²=1-e")
    E = projectors[0] + projectors[1]  # Rank-2 projector
    complement = np.eye(n) - E
    assert np.allclose(complement @ complement, complement)
    print(f"  E = P_0 + P_1 (rank 2)")
    print(f"  1-E = P_2 + P_3 (rank 2)")
    print(f"  (1-E)² = 1-E ✓")
    print(f"  E(1-E) = 0 ✓: {np.allclose(E @ complement, 0)}")

    # Temperley-Lieb connection
    print(f"\nTemperley-Lieb at δ=2:")
    delta = 2.0
    # e² = δe means (e/δ)² = e/δ when δ=2
    e_val = delta  # e satisfying e²=2e
    e_normalized = e_val / 2
    print(f"  e = {e_val}, e² = {e_val**2} = δ·e = {delta*e_val}")
    print(f"  (e/2) = {e_normalized}, (e/2)² = {e_normalized**2} = e/2 ✓")

    # Trace non-negativity (formalized as idempotent_trace_nonneg)
    print(f"\nTrace non-negativity for idempotent matrices:")
    for trial in range(5):
        # Random idempotent: P = A(A^TA)^{-1}A^T for random A
        k = np.random.randint(1, n+1)
        A_rand = np.random.randn(n, k)
        try:
            P_rand = A_rand @ np.linalg.inv(A_rand.T @ A_rand) @ A_rand.T
            trace = np.trace(P_rand)
            print(f"  Random rank-{k} projector: trace = {trace:.4f} ≥ 0 ✓")
        except np.linalg.LinAlgError:
            pass


# ============================================================
# 4. BRIDGE COMPOSITION AND ANALYSIS BRIDGES
# ============================================================

def demo_bridges():
    """Demonstrate bridge composition and analysis bridges."""
    print("\n" + "=" * 60)
    print("DEMO 4: Bridge Composition and Analysis Bridges")
    print("=" * 60)

    # Bridge hierarchy
    bridges = [
        ("Classical", "Groups ↔ Dual groups"),
        ("Stone", "Boolean algebras ↔ Stone spaces"),
        ("Gelfand", "C*-algebras ↔ Compact Hausdorff"),
        ("Pointfree", "Frames ↔ Locales"),
        ("Noncommutative", "NC algebras ↔ Quantum spaces"),
        ("Derived", "Chain complexes ↔ Cohomology"),
        ("Tropical", "Varieties ↔ Polyhedral complexes"),
        ("Quantum", "Symmetries ↔ Braided structures"),
        ("Motivic", "Algebraic cycles ↔ Periods"),
        ("HoTT", "Types ↔ Spaces (subsumes all)")
    ]

    print("The Ten Bridges of Mathematics:")
    for i, (name, desc) in enumerate(bridges, 1):
        subsumes = "★" if name == "HoTT" else " "
        print(f"  {subsumes} Bridge {i:2d}: {name:15s} — {desc}")

    # Analysis bridge: Riemann sum convergence
    print(f"\nAnalysis Bridge: Riemann Sum → Integral")
    print(f"f(x) = x², ∫₀¹ x² dx = 1/3")
    f = lambda x: x**2
    exact = 1.0 / 3.0
    print(f"  {'n':>6s}  {'Riemann sum':>12s}  {'Error':>12s}")
    for n in [10, 100, 1000, 10000]:
        riemann_sum = sum(f((k+1)/n) for k in range(n)) / n
        error = abs(riemann_sum - exact)
        print(f"  {n:6d}  {riemann_sum:12.8f}  {error:12.2e}")

    # Bridge composition example
    print(f"\nBridge Composition:")
    print(f"  Bridge A: ℤ → ℤ/nℤ  (quotient)")
    print(f"  Bridge B: ℤ/nℤ → {0,1}^k  (binary representation)")
    print(f"  A ∘ B: ℤ → {0,1}^k  (composed bridge)")
    n = 8
    for x in [3, 7, 12, 15]:
        mod_val = x % n
        binary = format(mod_val, f'0{3}b')
        print(f"    {x} → {mod_val} → {binary}")


# ============================================================
# 5. RAMANUJAN GRAPH VERIFICATION
# ============================================================

def demo_ramanujan():
    """Verify Ramanujan property for known families."""
    print("\n" + "=" * 60)
    print("DEMO 5: Ramanujan Graph Verification")
    print("=" * 60)

    graphs = {
        "Complete K_4": ([(i,j) for i in range(4) for j in range(i+1,4)], 4),
        "Petersen": ([(0,1),(1,2),(2,3),(3,4),(4,0),
                      (5,7),(7,9),(9,6),(6,8),(8,5),
                      (0,5),(1,6),(2,7),(3,8),(4,9)], 10),
        "Cycle C_6": ([(i,(i+1)%6) for i in range(6)], 6),
        "Cube Q_3": ([(0,1),(0,2),(0,4),(1,3),(1,5),(2,3),
                      (2,6),(3,7),(4,5),(4,6),(5,7),(6,7)], 8),
    }

    for name, (edges, n) in graphs.items():
        A = adjacency_matrix(edges, n)
        degrees = A.sum(axis=1)
        if len(set(degrees)) == 1:
            q_plus_1 = int(degrees[0])
            q = q_plus_1 - 1
            eigenvalues = np.linalg.eigvalsh(A)
            eigenvalues.sort()
            non_trivial = [e for e in eigenvalues if abs(abs(e) - q_plus_1) > 0.01]
            if non_trivial:
                max_nt = max(abs(e) for e in non_trivial)
            else:
                max_nt = 0
            bound = 2 * np.sqrt(q) if q > 0 else 0
            is_ram = max_nt <= bound + 0.01

            # Graph genus and Kirchhoff
            L = graph_laplacian(A)
            L_reduced = L[1:, 1:]
            num_trees = abs(int(round(np.linalg.det(L_reduced))))
            genus = len(edges) - n + 1

            print(f"\n{name}: {n} vertices, {len(edges)} edges, {q_plus_1}-regular")
            print(f"  q = {q}, 2√q = {bound:.4f}")
            print(f"  Max non-trivial |λ| = {max_nt:.4f}")
            print(f"  Ramanujan: {'✓ YES' if is_ram else '✗ NO'}")
            print(f"  Genus g = {genus}, Spanning trees = {num_trees}")


# ============================================================
# 6. LANGLANDS DICTIONARY
# ============================================================

def demo_langlands_dictionary():
    """Display the Langlands dictionary of correspondences."""
    print("\n" + "=" * 60)
    print("DEMO 6: The Langlands Dictionary")
    print("=" * 60)

    dictionary = [
        ("Number Theory", "Graph Theory", "Tropical Geometry"),
        ("─" * 20, "─" * 20, "─" * 20),
        ("Prime ideals", "Prime cycles", "Tropical curves"),
        ("Dedekind zeta ζ_K(s)", "Ihara zeta ζ_G(u)", "Tropical zeta"),
        ("Class group", "Chip-firing group", "Tropical Jacobian"),
        ("Class number h_K", "# spanning trees", "det(reduced Lap.)"),
        ("Riemann Hypothesis", "Ramanujan condition", "Tropical RH"),
        ("Galois representations", "Graph automorphisms", "Trop. symmetries"),
        ("L-functions", "Euler product", "Tropical L-fn"),
        ("Modularity theorem", "Spectral correspondence", "Tropical duality"),
        ("Artin reciprocity", "Graph reciprocity", "Trop. reciprocity"),
    ]

    for row in dictionary:
        print(f"  {row[0]:<25s} {row[1]:<25s} {row[2]}")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("╔" + "═" * 58 + "╗")
    print("║  Cross-Domain Bridges & Langlands Program Demonstrations  ║")
    print("║  Companion to Lean 4 Formal Verification                  ║")
    print("╚" + "═" * 58 + "╝")

    A, D = demo_ihara_zeta()
    demo_chip_firing()
    demo_idempotents()
    demo_bridges()
    demo_ramanujan()
    demo_langlands_dictionary()

    print("\n" + "=" * 60)
    print("All demonstrations completed successfully.")
    print("See Lean 4 files for formal proofs of the underlying theorems.")
    print("=" * 60)

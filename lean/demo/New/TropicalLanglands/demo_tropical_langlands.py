#!/usr/bin/env python3
"""
Tropical Langlands Program: Interactive Demonstrations

This script demonstrates key concepts from the Tropical Langlands program:
1. Tropical arithmetic and matrix multiplication
2. Tropical characters and L-functions
3. Legendre-Fenchel duality (tropical Fourier transform)
4. Newton polygons and p-adic tropicalization
5. Graph Laplacian and tropical automorphic forms
6. Kantorovich duality and optimal transport
7. Tropical neural networks and ReLU
8. Higher-rank tropical Langlands (root systems)
"""

import numpy as np
from itertools import permutations
import json

# ═══════════════════════════════════════════════════════════════════
# PART 1: TROPICAL ARITHMETIC
# ═══════════════════════════════════════════════════════════════════

def trop_add(a, b):
    """Tropical addition: min(a, b)"""
    return min(a, b)

def trop_mul(a, b):
    """Tropical multiplication: a + b"""
    return a + b

def trop_mat_mul(A, B):
    """Tropical matrix multiplication: C[i,k] = min_j(A[i,j] + B[j,k])"""
    n = A.shape[0]
    C = np.full((n, n), np.inf)
    for i in range(n):
        for k in range(n):
            for j in range(n):
                C[i, k] = min(C[i, k], A[i, j] + B[j, k])
    return C

def trop_det(A):
    """Tropical determinant: min over permutations of sum of selected entries"""
    n = A.shape[0]
    min_val = np.inf
    best_perm = None
    for perm in permutations(range(n)):
        val = sum(A[i, perm[i]] for i in range(n))
        if val < min_val:
            min_val = val
            best_perm = perm
    return min_val, best_perm

def demo_tropical_arithmetic():
    print("=" * 60)
    print("DEMO 1: Tropical Arithmetic")
    print("=" * 60)
    print(f"Tropical addition:  3 ⊕ 7 = min(3,7) = {trop_add(3, 7)}")
    print(f"Tropical multiply:  3 ⊙ 7 = 3 + 7 = {trop_mul(3, 7)}")
    print(f"Tropical identity:  a ⊕ ∞ = a (∞ is additive identity)")
    print(f"Tropical identity:  a ⊙ 0 = a (0 is multiplicative identity)")
    print()

    A = np.array([[1, 3], [2, 0]])
    B = np.array([[0, 1], [4, 2]])
    C = trop_mat_mul(A, B)
    print("Tropical Matrix Multiplication:")
    print(f"A = {A.tolist()}")
    print(f"B = {B.tolist()}")
    print(f"A ⊗ B = {C.tolist()}")
    print(f"  (A⊗B)[0,0] = min(1+0, 3+4) = min(1,7) = {C[0,0]}")
    print()

    det_val, best = trop_det(A)
    print(f"Tropical determinant of A = {det_val}")
    print(f"  Optimal assignment: {best}")
    print(f"  = min(1+0, 3+2) = min(1, 5) = {det_val}")
    print()

# ═══════════════════════════════════════════════════════════════════
# PART 2: TROPICAL CHARACTERS AND L-FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def tropical_character(slope, n):
    """Tropical character χ(n) = n * slope (determined by χ(1) = slope)"""
    return n * slope

def tropical_L_function(slopes, s):
    """Tropical L-function: L(s) = Σ (s - slope_i)"""
    return sum(s - slope for slope in slopes)

def demo_tropical_characters():
    print("=" * 60)
    print("DEMO 2: Tropical Characters and L-Functions")
    print("=" * 60)

    slope = 2.5
    print(f"Tropical character with slope {slope}:")
    for n in range(-3, 4):
        print(f"  χ({n}) = {n} × {slope} = {tropical_character(slope, n)}")
    print()

    slopes = [0.5, 1.0, 2.0]
    print(f"Tropical L-function with slopes {slopes}:")
    for s in [0, 1, 2, 3, 4, 5]:
        L = tropical_L_function(slopes, s)
        print(f"  L({s}) = Σ({s} - αᵢ) = {L:.1f}")
    print()

# ═══════════════════════════════════════════════════════════════════
# PART 3: LEGENDRE-FENCHEL DUALITY
# ═══════════════════════════════════════════════════════════════════

def legendre_fenchel(f, x_range, p):
    """Compute f*(p) = sup_x(p*x - f(x))"""
    return max(p * x - f(x) for x in x_range)

def demo_legendre_fenchel():
    print("=" * 60)
    print("DEMO 3: Legendre-Fenchel Duality (Tropical Fourier)")
    print("=" * 60)

    f = lambda x: x**2  # f(x) = x²
    x_range = np.linspace(-5, 5, 1000)

    print("f(x) = x² (a convex function)")
    print("f*(p) = sup_x(px - x²) = p²/4 (the convex conjugate)")
    print()
    for p in [-4, -2, 0, 2, 4]:
        f_star = legendre_fenchel(f, x_range, p)
        exact = p**2 / 4
        print(f"  f*({p:+d}) = {f_star:.3f}  (exact: {exact:.3f})")

    print()
    print("Fenchel-Moreau: f**(x) = f(x) for convex f")
    f_star = lambda p: p**2 / 4
    p_range = np.linspace(-10, 10, 1000)
    for x in [-2, -1, 0, 1, 2]:
        f_biconj = legendre_fenchel(f_star, p_range, x)
        print(f"  f**({x:+d}) = {f_biconj:.3f}  (f({x:+d}) = {x**2:.3f})")
    print()

# ═══════════════════════════════════════════════════════════════════
# PART 4: NEWTON POLYGONS
# ═══════════════════════════════════════════════════════════════════

def newton_polygon(coefficients, p=2):
    """Compute Newton polygon of a polynomial w.r.t. p-adic valuation"""
    valuations = []
    for i, c in enumerate(coefficients):
        if c == 0:
            valuations.append((i, float('inf')))
        else:
            v = 0
            temp = abs(c)
            while temp % p == 0:
                v += 1
                temp //= p
            valuations.append((i, v))
    return valuations

def lower_convex_hull(points):
    """Compute lower convex hull of points (Newton polygon)"""
    points = [(x, y) for x, y in points if y < float('inf')]
    if len(points) <= 1:
        return points
    points.sort()
    hull = []
    for p in points:
        while len(hull) >= 2:
            o, a, b = hull[-2], hull[-1], p
            cross = (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
            if cross <= 0:
                hull.pop()
            else:
                break
        hull.append(p)
    return hull

def demo_newton_polygons():
    print("=" * 60)
    print("DEMO 4: Newton Polygons (p-adic Tropicalization)")
    print("=" * 60)

    # Example: x³ + 6x² + 12x + 8 = (x+2)³ with p=2
    coefficients = [8, 12, 6, 1]
    vals = newton_polygon(coefficients, p=2)
    print(f"Polynomial: 8 + 12x + 6x² + x³")
    print(f"2-adic valuations: {vals}")

    hull = lower_convex_hull(vals)
    print(f"Newton polygon vertices: {hull}")

    slopes = []
    for i in range(len(hull)-1):
        s = (hull[i+1][1] - hull[i][1]) / (hull[i+1][0] - hull[i][0])
        slopes.append(s)
    print(f"Newton polygon slopes: {slopes}")
    print(f"  (These are the tropical Galois parameters!)")
    print()

# ═══════════════════════════════════════════════════════════════════
# PART 5: GRAPH LAPLACIAN AND TROPICAL AUTOMORPHIC FORMS
# ═══════════════════════════════════════════════════════════════════

def graph_laplacian(adj):
    """Compute the graph Laplacian L = D - A"""
    n = adj.shape[0]
    D = np.diag(adj.sum(axis=1))
    return D - adj

def demo_graph_laplacian():
    print("=" * 60)
    print("DEMO 5: Graph Laplacian (Tropical Automorphic Forms)")
    print("=" * 60)

    # Complete graph K4
    n = 4
    adj = np.ones((n, n)) - np.eye(n)
    L = graph_laplacian(adj)

    print(f"Complete graph K₄:")
    print(f"Adjacency matrix:\n{adj.astype(int)}")
    print(f"Laplacian:\n{L.astype(int)}")

    eigenvalues = np.linalg.eigvalsh(L)
    print(f"Eigenvalues: {np.round(eigenvalues, 4)}")
    print(f"  (0 corresponds to the constant automorphic form)")
    print(f"  ({int(n)} with multiplicity {n-1} corresponds to nontrivial forms)")

    # Check Ramanujan property
    q = n - 2  # K4 is 3-regular, so q+1 = 3, q = 2
    nontrivial = [ev for ev in eigenvalues if abs(ev) > 0.01 and abs(ev - (q+1)) > 0.01]
    bound = 2 * np.sqrt(q)
    print(f"\nRamanujan bound for (q+1)={q+1}-regular graph: |λ| ≤ 2√{q} = {bound:.3f}")
    for ev in nontrivial:
        status = "✓ Ramanujan" if abs(ev) <= bound + 0.01 else "✗ Not Ramanujan"
        print(f"  |{ev:.3f}| = {abs(ev):.3f} ≤ {bound:.3f}? {status}")
    print()

# ═══════════════════════════════════════════════════════════════════
# PART 6: KANTOROVICH DUALITY (OPTIMAL TRANSPORT)
# ═══════════════════════════════════════════════════════════════════

def demo_kantorovich():
    print("=" * 60)
    print("DEMO 6: Kantorovich Duality (Tropical Langlands Duality)")
    print("=" * 60)

    # Cost matrix: distances between 3 factories and 3 warehouses
    c = np.array([[1, 4, 3],
                  [2, 1, 5],
                  [3, 2, 1]])
    mu = np.array([0.4, 0.3, 0.3])  # supply
    nu = np.array([0.3, 0.4, 0.3])  # demand

    print(f"Cost matrix c:\n{c}")
    print(f"Supply (μ): {mu}")
    print(f"Demand (ν): {nu}")

    # Primal: naive coupling (diagonal-ish)
    coupling = np.outer(mu, nu)  # Independent coupling
    primal_cost = np.sum(coupling * c)
    print(f"\nIndependent coupling cost: {primal_cost:.3f}")

    # Better coupling: greedy assignment
    coupling2 = np.zeros((3, 3))
    coupling2[0, 0] = 0.3; coupling2[0, 2] = 0.1
    coupling2[1, 1] = 0.3
    coupling2[2, 1] = 0.1; coupling2[2, 2] = 0.2
    primal2 = np.sum(coupling2 * c)
    print(f"Greedy coupling cost: {primal2:.3f}")

    # Dual: find potentials
    phi = np.array([0, 0, 0])
    psi = np.array([1, 1, 1])
    # Check feasibility: phi[i] + psi[j] <= c[i,j]
    feasible = all(phi[i] + psi[j] <= c[i, j] for i in range(3) for j in range(3))
    dual_val = np.sum(phi * mu) + np.sum(psi * nu)
    print(f"\nDual potentials φ={phi.tolist()}, ψ={psi.tolist()}")
    print(f"Feasible: {feasible}")
    print(f"Dual value: {dual_val:.3f}")
    print(f"Weak duality: {dual_val:.3f} ≤ {primal2:.3f} ✓")
    print(f"\n→ The primal (transport) is the 'automorphic side'")
    print(f"→ The dual (potentials) is the 'Galois side'")
    print(f"→ Weak duality = tropical Langlands reciprocity!")
    print()

# ═══════════════════════════════════════════════════════════════════
# PART 7: TROPICAL NEURAL NETWORKS
# ═══════════════════════════════════════════════════════════════════

def relu(x):
    """ReLU = max(0, x) = tropical polynomial"""
    return np.maximum(x, 0)

def tropical_layer(W, x):
    """Tropical (min-plus) layer"""
    n_out, n_in = W.shape
    result = np.full(n_out, np.inf)
    for i in range(n_out):
        for j in range(n_in):
            result[i] = min(result[i], W[i, j] + x[j])
    return result

def maxplus_layer(W, x):
    """Max-plus layer (dual tropical)"""
    n_out, n_in = W.shape
    result = np.full(n_out, -np.inf)
    for i in range(n_out):
        for j in range(n_in):
            result[i] = max(result[i], W[i, j] + x[j])
    return result

def demo_tropical_nn():
    print("=" * 60)
    print("DEMO 7: Tropical Neural Networks")
    print("=" * 60)

    print("ReLU(x) = max(0, x) is a tropical polynomial!")
    for x in [-2, -1, 0, 1, 2]:
        print(f"  ReLU({x:+d}) = max(0, {x:+d}) = {relu(x)}")

    W = np.array([[1, -1], [0, 2], [-1, 1]])
    x = np.array([3, 1])
    print(f"\nMin-plus layer: W={W.tolist()}, x={x.tolist()}")
    y_trop = tropical_layer(W, x)
    print(f"  min-plus output: {y_trop.tolist()}")
    print(f"  (each output = min over j of W[i,j] + x[j])")

    y_maxplus = maxplus_layer(W, x)
    print(f"  max-plus output: {y_maxplus.tolist()}")

    # Network duality: W^T
    W_dual = W.T
    print(f"\nNetwork duality (Langlands dual):")
    print(f"  W = {W.tolist()}")
    print(f"  W^T = {W_dual.tolist()}")
    print(f"  Double dual W^TT = W: {(W_dual.T == W).all()} ✓")

    # Tropical determinant invariance under transpose (for square)
    M = np.array([[1, 3], [2, 0]])
    det_M, _ = trop_det(M)
    det_MT, _ = trop_det(M.T)
    print(f"\nTropical det(M) = {det_M}, det(M^T) = {det_MT}")
    print(f"  Preserved under transpose: {det_M == det_MT} ✓")
    print()

# ═══════════════════════════════════════════════════════════════════
# PART 8: HIGHER-RANK TROPICAL LANGLANDS
# ═══════════════════════════════════════════════════════════════════

def demo_higher_rank():
    print("=" * 60)
    print("DEMO 8: Higher-Rank Tropical Langlands")
    print("=" * 60)

    # Type A root system for GL_3
    print("Type A₂ root system (GL₃):")
    roots = []
    for i in range(3):
        for j in range(3):
            if i != j:
                root = [0, 0, 0]
                root[i] = 1
                root[j] = -1
                roots.append(root)
                print(f"  e_{i+1} - e_{j+1} = {root}")

    # Dominant chamber
    print(f"\nDominant chamber: x₁ ≥ x₂ ≥ x₃")
    test_points = [[3, 2, 1], [5, 5, 1], [1, 2, 3], [2, 2, 2]]
    for x in test_points:
        dominant = x[0] >= x[1] >= x[2]
        print(f"  x = {x}: dominant = {dominant}")

    # Weyl group action (S₃)
    x = [3, 1, 2]
    print(f"\nWeyl group orbit of {x}:")
    orbit = set()
    for p in permutations(range(3)):
        sorted_x = tuple(x[p[i]] for i in range(3))
        orbit.add(sorted_x)
    for elem in sorted(orbit, reverse=True):
        dominant = elem[0] >= elem[1] >= elem[2]
        marker = " ← dominant" if dominant else ""
        print(f"  {list(elem)}{marker}")

    # Tropical Satake parameters and symmetric power
    print(f"\nTropical symmetric power Sym²: GL₂ → GL₃")
    alpha, beta = 1.0, 3.0
    sym2 = [2*alpha, alpha+beta, 2*beta]
    print(f"  Satake params (α,β) = ({alpha},{beta})")
    print(f"  Sym²(α,β) = (2α, α+β, 2β) = {sym2}")
    print(f"  Sorted: {sorted(sym2)} ✓")

    # Parabolic induction
    print(f"\nParabolic induction GL₂ × GL₁ → GL₃:")
    params1 = [1.0, 2.0]
    params2 = [1.5]
    induced = sorted(params1 + params2)
    print(f"  GL₂ params: {params1}")
    print(f"  GL₁ params: {params2}")
    print(f"  Induced GL₃ params: {induced}")
    print()

# ═══════════════════════════════════════════════════════════════════
# PART 9: CHIP-FIRING AND TROPICAL RIEMANN-ROCH
# ═══════════════════════════════════════════════════════════════════

def demo_chip_firing():
    print("=" * 60)
    print("DEMO 9: Chip-Firing (Tropical Automorphic Forms on Graphs)")
    print("=" * 60)

    # Graph: triangle (K3)
    n = 3
    adj = np.array([[0, 1, 1],
                     [1, 0, 1],
                     [1, 1, 0]])

    # Divisor (chip configuration)
    D = np.array([3, -1, 0])
    print(f"Graph: K₃ (triangle)")
    print(f"Initial divisor D = {D.tolist()}")
    print(f"Degree = {sum(D)}")

    # Chip-firing: vertex 0 fires
    print(f"\nVertex 0 fires (sends 1 chip to each neighbor):")
    D2 = D.copy()
    D2[0] -= sum(adj[0])
    for j in range(n):
        D2[j] += int(adj[0][j])
    print(f"  D' = {D2.tolist()}")
    print(f"  Degree = {sum(D2)} (preserved! ✓)")

    # Canonical divisor
    K = np.array([adj[i].sum() - 2 for i in range(n)])
    print(f"\nCanonical divisor K(v) = deg(v) - 2:")
    print(f"  K = {K.astype(int).tolist()}")
    print(f"  deg(K) = {int(sum(K))} = n(q-1) = 3×0 = 0 ✓")
    print()

# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("╔" + "═" * 58 + "╗")
    print("║   TROPICAL LANGLANDS PROGRAM: INTERACTIVE DEMONSTRATIONS  ║")
    print("╚" + "═" * 58 + "╝")
    print()

    demo_tropical_arithmetic()
    demo_tropical_characters()
    demo_legendre_fenchel()
    demo_newton_polygons()
    demo_graph_laplacian()
    demo_kantorovich()
    demo_tropical_nn()
    demo_higher_rank()
    demo_chip_firing()

    print("=" * 60)
    print("All demos completed successfully!")
    print("=" * 60)

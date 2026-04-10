#!/usr/bin/env python3
"""
Ramanujan Open Problems — Computational Exploration
====================================================
Demonstrates the five open problems in Berggren-Ramanujan theory:
1. Density of Ramanujan primes (orbit/spectrum computation)
2. 5D completeness (tree generation)
3. Quaternion-algebraic connection (Pell equation)
4. Chebyshev for mixed generators (trace formulas)
5. Role of -1 eigenvalue (spectral decomposition)
"""

import numpy as np
from collections import deque

# ============================================================
# Berggren Matrices
# ============================================================

B1 = np.array([[1, -2, 2], [2, -1, 2], [2, -2, 3]])
B2 = np.array([[1,  2, 2], [2,  1, 2], [2,  2, 3]])
B3 = np.array([[-1, 2, 2], [-2, 1, 2], [-2, 2, 3]])
Q  = np.diag([1, 1, -1])

GENERATORS = [B1, B2, B3]
GEN_NAMES = ["B1", "B2", "B3"]

def lorentz_check(M):
    """Check M^T Q M = Q."""
    return np.allclose(M.T @ Q @ M, Q)

# ============================================================
# Problem 1: Ramanujan Primes — Orbit and Spectrum Computation
# ============================================================

def mod_matrix(M, p):
    """Reduce matrix mod p."""
    return M % p

def orbit_mod_p(p):
    """Compute orbit of (3,4,5) mod p under Berggren generators."""
    root = tuple(np.array([3, 4, 5]) % p)
    visited = {root}
    queue = deque([root])
    gens = GENERATORS + [np.linalg.inv(G).astype(int) for G in GENERATORS]

    while queue:
        v = queue.popleft()
        for G in gens:
            w = tuple((G @ np.array(v)) % p)
            if w not in visited:
                visited.add(w)
                queue.append(w)
    return visited

def adjacency_matrix_mod_p(p):
    """Build adjacency matrix of Cayley graph G_p."""
    orbit = list(orbit_mod_p(p))
    idx = {v: i for i, v in enumerate(orbit)}
    n = len(orbit)
    A = np.zeros((n, n))

    inv_gens = [np.round(np.linalg.inv(G)).astype(int) for G in GENERATORS]
    gens = GENERATORS + inv_gens

    for v in orbit:
        i = idx[v]
        for G in gens:
            w = tuple((G @ np.array(v)) % p)
            if w in idx:
                j = idx[w]
                A[i, j] = 1

    return A, orbit

def check_ramanujan(p):
    """Check if G_p is Ramanujan for 6-regular graphs."""
    A, orbit = adjacency_matrix_mod_p(p)
    eigenvalues = np.sort(np.linalg.eigvalsh(A))[::-1]

    # Degree (should be ≤ 6)
    d = int(round(eigenvalues[0]))

    # Non-trivial eigenvalues
    nontrivial = [ev for ev in eigenvalues[1:] if abs(abs(ev) - d) > 0.01]
    if not nontrivial:
        max_nontrivial = 0
    else:
        max_nontrivial = max(abs(ev) for ev in nontrivial)

    bound = 2 * np.sqrt(d - 1)
    is_ramanujan = max_nontrivial <= bound + 0.01

    return {
        'p': p,
        'orbit_size': len(orbit),
        'degree': d,
        'max_nontrivial': max_nontrivial,
        'ramanujan_bound': bound,
        'is_ramanujan': is_ramanujan,
        'eigenvalues': eigenvalues
    }

print("=" * 70)
print("PROBLEM 1: Density of Ramanujan Primes")
print("=" * 70)

for p in [5, 7, 11, 13]:
    result = check_ramanujan(p)
    status = "✓ RAMANUJAN" if result['is_ramanujan'] else "✗ NOT Ramanujan"
    print(f"\np = {p}:")
    print(f"  Orbit size: {result['orbit_size']}")
    print(f"  Degree: {result['degree']}")
    print(f"  Max nontrivial |λ|: {result['max_nontrivial']:.4f}")
    print(f"  Ramanujan bound 2√(d-1): {result['ramanujan_bound']:.4f}")
    print(f"  Status: {status}")

# ============================================================
# Problem 2: 5D Generator Completeness
# ============================================================

print("\n" + "=" * 70)
print("PROBLEM 2: 5D Generator Completeness")
print("=" * 70)

# 5D generators
K1 = np.array([[-1,0,0,2,2],[0,1,0,0,0],[0,0,1,0,0],[-2,0,0,1,2],[-2,0,0,2,3]])
K2 = np.array([[1,0,0,2,2],[0,1,0,0,0],[0,0,1,0,0],[2,0,0,1,2],[2,0,0,2,3]])
K3 = np.array([[1,0,0,0,0],[0,-1,0,2,2],[0,0,1,0,0],[0,-2,0,1,2],[0,-2,0,2,3]])
K4 = np.array([[1,0,0,0,0],[0,1,0,0,0],[0,0,-1,2,2],[0,0,-2,1,2],[0,0,-2,2,3]])
K5 = np.array([[1,0,0,0,0],[0,1,0,0,0],[0,0,1,2,2],[0,0,2,1,2],[0,0,2,2,3]])
K6 = np.array([[1,0,0,0,0],[0,1,0,2,2],[0,0,1,0,0],[0,2,0,1,2],[0,2,0,2,3]])

K_GENS = [K1, K2, K3, K4, K5, K6]
Q5 = np.diag([1, 1, 1, 1, -1])

def check_quintuple(v):
    """Check if v = (a1,a2,a3,a4,d) with a1²+a2²+a3²+a4²=d²."""
    return v[0]**2 + v[1]**2 + v[2]**2 + v[3]**2 == v[4]**2

def generate_quintuples(root, depth):
    """Generate quintuples from root up to given depth."""
    quintuples = {tuple(root)}
    frontier = [tuple(root)]
    for d in range(depth):
        next_frontier = []
        for v in frontier:
            for K in K_GENS:
                w = tuple(K @ np.array(v))
                if w not in quintuples:
                    quintuples.add(w)
                    next_frontier.append(w)
        frontier = next_frontier
    return quintuples

root1 = [1, 1, 1, 1, 2]
root2 = [1, 0, 0, 0, 1]

quints1 = generate_quintuples(root1, 3)
quints2 = generate_quintuples(root2, 3)

print(f"\nFrom root (1,1,1,1,2): {len(quints1)} quintuples at depth 3")
print(f"From root (1,0,0,0,1): {len(quints2)} quintuples at depth 3")

# Check for zero entries
has_zero_1 = sum(1 for q in quints1 if 0 in q[:4])
has_zero_2 = sum(1 for q in quints2 if 0 in q[:4])
print(f"  Root 1 quintuples with zero entry: {has_zero_1}")
print(f"  Root 2 quintuples with zero entry: {has_zero_2}")

overlap = quints1 & quints2
print(f"  Overlap between trees: {len(overlap)}")

# Verify all are valid
all_valid_1 = all(check_quintuple(list(q)) for q in quints1)
all_valid_2 = all(check_quintuple(list(q)) for q in quints2)
print(f"  All valid from root 1: {all_valid_1}")
print(f"  All valid from root 2: {all_valid_2}")

# ============================================================
# Problem 3: Quaternion-Algebraic / Pell Connection
# ============================================================

print("\n" + "=" * 70)
print("PROBLEM 3: Pell Equation Connection")
print("=" * 70)

def chebyshev_T(n, x):
    """Compute T_n(x) via recurrence."""
    if n == 0: return 1
    if n == 1: return x
    t0, t1 = 1, x
    for _ in range(n - 1):
        t0, t1 = t1, 2*x*t1 - t0
    return t1

print("\nChebyshev T_n(3) and Pell equation x²-2y²=1:")
print(f"{'n':>4} {'T_n(3)':>12} {'y_n':>10} {'x²-2y²':>10}")
print("-" * 40)

y_vals = [0, 2, 12, 70, 408, 2378]
for n in range(6):
    tn = chebyshev_T(n, 3)
    y = y_vals[n]
    pell = tn**2 - 2*y**2
    print(f"{n:4d} {tn:12d} {y:10d} {pell:10d}")

print("\nConnection: (3+2√2)^n = T_n(3) + y_n·√2")
print("Eigenvalue growth: (3+2√2)^n ≈", end=" ")
for n in range(1, 6):
    print(f"{(3+2*np.sqrt(2))**n:.1f}", end=" ")
print()

# ============================================================
# Problem 4: Chebyshev for Mixed Generators
# ============================================================

print("\n" + "=" * 70)
print("PROBLEM 4: Chebyshev Connection for Mixed Generators")
print("=" * 70)

products = {
    "B2": B2,
    "B1*B2": B1 @ B2,
    "B2*B3": B2 @ B3,
    "B1*B3": B1 @ B3,
    "B1*B2*B3": B1 @ B2 @ B3,
}

for name, M in products.items():
    det_M = int(round(np.linalg.det(M)))
    eigs = np.linalg.eigvals(M)
    eigs_real = sorted(np.real(eigs))
    tr_M = int(round(np.trace(M)))

    # Find the eigenvalue closest to ±1
    fixed_eig = det_M  # det = ±1
    # Hyperbolic pair
    hyp_eigs = [e for e in eigs_real if abs(e - fixed_eig) > 0.1]

    print(f"\n{name}:")
    print(f"  det = {det_M}")
    print(f"  tr = {tr_M}")
    print(f"  eigenvalues: {[f'{e:.4f}' for e in eigs_real]}")

    if len(hyp_eigs) >= 2:
        alpha = max(hyp_eigs)
        beta = min(hyp_eigs)
        c = (alpha + beta) / 2
        print(f"  Chebyshev parameter c = (α+β)/2 = {c:.4f}")

        # Verify trace formula
        print(f"  Trace formula verification (n=1..5):")
        for n in range(1, 6):
            Mn = np.linalg.matrix_power(M, n)
            tr_actual = int(round(np.trace(Mn)))
            tn = chebyshev_T(n, round(c))
            tr_predicted = det_M**n + 2 * tn
            match = "✓" if tr_actual == tr_predicted else "✗"
            print(f"    n={n}: actual={tr_actual}, predicted={tr_predicted} {match}")

# ============================================================
# Problem 5: Role of -1 Eigenvalue
# ============================================================

print("\n" + "=" * 70)
print("PROBLEM 5: Role of the -1 Eigenvalue of B₂")
print("=" * 70)

eigenvalues, eigenvectors = np.linalg.eig(B2)
print(f"\nEigenvalues of B₂: {[f'{e:.6f}' for e in eigenvalues]}")
print(f"Eigenvectors:")
for i, (ev, vec) in enumerate(zip(eigenvalues, eigenvectors.T)):
    vec_norm = vec / vec[np.argmax(np.abs(vec))]
    qnorm = vec_norm[0]**2 + vec_norm[1]**2 - vec_norm[2]**2
    etype = "spacelike" if qnorm > 0 else ("timelike" if qnorm < 0 else "null")
    print(f"  λ={ev:.4f}: v={[f'{x:.4f}' for x in vec_norm]} (Q-norm={qnorm:.4f}, {etype})")

# Even/odd trace dichotomy
print(f"\nEven/Odd Trace Dichotomy:")
print(f"{'n':>4} {'tr(B₂ⁿ)':>12} {'(-1)ⁿ':>8} {'2Tₙ(3)':>10} {'Match':>6}")
print("-" * 45)
for n in range(1, 8):
    Bn = np.linalg.matrix_power(B2, n)
    tr_actual = int(round(np.trace(Bn)))
    sign_part = (-1)**n
    cheb_part = 2 * chebyshev_T(n, 3)
    predicted = sign_part + cheb_part
    match = "✓" if tr_actual == predicted else "✗"
    print(f"{n:4d} {tr_actual:12d} {sign_part:8d} {cheb_part:10d} {match:>6}")

# ============================================================
# Generator Order Analysis
# ============================================================

print("\n" + "=" * 70)
print("BONUS: Generator Orders Modulo Primes")
print("=" * 70)

def matrix_order_mod_p(M, p, max_order=1000):
    """Find the multiplicative order of M mod p."""
    Mk = np.eye(M.shape[0], dtype=int)
    I = np.eye(M.shape[0], dtype=int)
    for k in range(1, max_order + 1):
        Mk = (Mk @ M) % p
        if np.array_equal(Mk % p, I % p):
            return k
    return None

primes = [5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43]
print(f"\n{'p':>4} {'ord(B₁)':>10} {'ord(B₂)':>10} {'ord(B₃)':>10} {'p mod 8':>8}")
print("-" * 45)
for p in primes:
    o1 = matrix_order_mod_p(B1, p)
    o2 = matrix_order_mod_p(B2, p)
    o3 = matrix_order_mod_p(B3, p)
    print(f"{p:4d} {str(o1):>10} {str(o2):>10} {str(o3):>10} {p%8:>8}")

# ============================================================
# Spectral Gap Analysis
# ============================================================

print("\n" + "=" * 70)
print("BONUS: Spectral Gap Growth")
print("=" * 70)

print(f"\n{'d':>6} {'Gap':>12} {'Rel Gap':>12}")
print("-" * 32)
for d in [3, 6, 8, 12, 20, 50, 100, 1000]:
    gap = d - 2*np.sqrt(d-1)
    rel_gap = gap / d
    print(f"{d:6d} {gap:12.4f} {rel_gap:12.4f}")

print("\n✓ All computations complete.")

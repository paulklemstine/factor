#!/usr/bin/env python3
"""
Tropical Transformers Demo
===========================
Demonstrates the tropical limit of softmax attention and its connection
to hard (tropical) attention mechanisms.

Key concepts visualized:
1. Softmax convergence to one-hot as temperature → 0
2. Hard attention as tropical max-selection
3. Tropical matrix multiplication (max-plus)
4. Tropical determinant as optimal assignment
"""

import numpy as np
from itertools import permutations

# =============================================================================
# 1. SOFTMAX AND THE TROPICAL LIMIT
# =============================================================================

def softmax(x, tau=1.0):
    """Standard softmax with temperature parameter tau."""
    e = np.exp(x / tau)
    return e / e.sum()

def hard_attention(scores):
    """Hard (tropical) attention: one-hot on the argmax."""
    result = np.zeros_like(scores)
    result[np.argmax(scores)] = 1.0
    return result

print("=" * 70)
print("TROPICAL TRANSFORMERS: SOFTMAX → HARD ATTENTION")
print("=" * 70)

scores = np.array([1.0, 3.0, 2.0, 0.5])
print(f"\nAttention scores: {scores}")
print(f"\nSoftmax at various temperatures:")
for tau in [2.0, 1.0, 0.5, 0.1, 0.01]:
    sm = softmax(scores, tau)
    print(f"  τ = {tau:5.2f}: [{', '.join(f'{v:.4f}' for v in sm)}]")

print(f"\n  Hard attention (τ → 0): {hard_attention(scores)}")
print(f"  → Selects position {np.argmax(scores)} (score = {np.max(scores)})")

# Verify softmax properties (matching our Lean theorems)
tau = 1.0
sm = softmax(scores, tau)
print(f"\n--- Verified Properties (τ = {tau}) ---")
print(f"  softmax_nonneg: all ≥ 0? {all(x >= 0 for x in sm)}")
print(f"  softmax_sum_one: sum = {sm.sum():.10f}")
print(f"  max_score_ge_avg: max = {scores.max():.2f} ≥ avg = {scores.mean():.2f}? {scores.max() >= scores.mean()}")

# =============================================================================
# 2. TROPICAL MATRIX MULTIPLICATION (MAX-PLUS)
# =============================================================================

def trop_matmul(A, B):
    """Tropical (max-plus) matrix multiplication."""
    m, n = A.shape
    n2, p = B.shape
    assert n == n2
    C = np.full((m, p), -np.inf)
    for i in range(m):
        for j in range(p):
            for k in range(n):
                C[i, j] = max(C[i, j], A[i, k] + B[k, j])
    return C

print("\n" + "=" * 70)
print("TROPICAL MATRIX MULTIPLICATION (MAX-PLUS)")
print("=" * 70)

A = np.array([[1, 3], [2, 0]], dtype=float)
B = np.array([[4, 1], [2, 5]], dtype=float)
C = trop_matmul(A, B)

print(f"\nA = \n{A}")
print(f"\nB = \n{B}")
print(f"\nA ⊗ B (tropical product) = \n{C}")
print(f"\nVerification: (A⊗B)[0,0] = max(A[0,0]+B[0,0], A[0,1]+B[1,0])")
print(f"  = max({A[0,0]}+{B[0,0]}, {A[0,1]}+{B[1,0]}) = max({A[0,0]+B[0,0]}, {A[0,1]+B[1,0]}) = {C[0,0]}")

# Verify associativity (our Lean theorem tropMatMul_assoc)
D = np.array([[2, 1], [3, 4]], dtype=float)
LHS = trop_matmul(trop_matmul(A, B), D)
RHS = trop_matmul(A, trop_matmul(B, D))
print(f"\n--- Associativity Check ---")
print(f"  (A⊗B)⊗D = \n{LHS}")
print(f"  A⊗(B⊗D) = \n{RHS}")
print(f"  Equal? {np.allclose(LHS, RHS)}")

# =============================================================================
# 3. TROPICAL DETERMINANT AND OPTIMAL ASSIGNMENT
# =============================================================================

def trop_det(A):
    """Tropical determinant = max over permutations of sum of selected entries."""
    n = A.shape[0]
    best = -np.inf
    best_perm = None
    for perm in permutations(range(n)):
        val = sum(A[i, perm[i]] for i in range(n))
        if val > best:
            best = val
            best_perm = perm
    return best, best_perm

print("\n" + "=" * 70)
print("TROPICAL DETERMINANT = OPTIMAL ASSIGNMENT")
print("=" * 70)

# Assignment problem: workers (rows) to jobs (columns), scores in matrix
W = np.array([
    [9, 2, 7, 8],
    [6, 4, 3, 7],
    [5, 8, 1, 8],
    [7, 6, 9, 4]
], dtype=float)

det_val, det_perm = trop_det(W)
diag_sum = sum(W[i, i] for i in range(4))

print(f"\nScore matrix W =\n{W}")
print(f"\nTropical determinant = {det_val}")
print(f"Optimal assignment: {det_perm}")
print(f"  Worker 0 → Job {det_perm[0]} (score {W[0, det_perm[0]]})")
print(f"  Worker 1 → Job {det_perm[1]} (score {W[1, det_perm[1]]})")
print(f"  Worker 2 → Job {det_perm[2]} (score {W[2, det_perm[2]]})")
print(f"  Worker 3 → Job {det_perm[3]} (score {W[3, det_perm[3]]})")

# Verify tropDet_ge_diag
print(f"\n--- tropDet_ge_diag Check ---")
print(f"  tropDet = {det_val} ≥ diag_sum = {diag_sum}? {det_val >= diag_sum}")

# =============================================================================
# 4. TROPICAL MATRIX POWERS AND HEAVIEST PATHS
# =============================================================================

def trop_matpow(A, k):
    """Compute A^k in the tropical (max-plus) semiring."""
    n = A.shape[0]
    if k == 0:
        return np.where(np.eye(n, dtype=bool), 0, -np.inf)
    result = A.copy()
    for _ in range(k - 1):
        result = trop_matmul(result, A)
    return result

print("\n" + "=" * 70)
print("TROPICAL MATRIX POWERS = HEAVIEST PATHS")
print("=" * 70)

# Weighted adjacency matrix (edge weights)
G = np.array([
    [-np.inf, 3, 1],
    [2, -np.inf, 4],
    [5, 1, -np.inf]
], dtype=float)

print(f"\nWeighted graph adjacency matrix:")
print(f"  0 →(3)→ 1,  0 →(1)→ 2")
print(f"  1 →(2)→ 0,  1 →(4)→ 2")
print(f"  2 →(5)→ 0,  2 →(1)→ 1")

for k in range(1, 5):
    Gk = trop_matpow(G, k)
    print(f"\nG^{k} (heaviest {k}-step paths):")
    for i in range(3):
        for j in range(3):
            if Gk[i, j] > -np.inf:
                print(f"  {i} → {j}: weight {Gk[i, j]:.0f}")

# =============================================================================
# 5. TROPICAL-CLASSICAL BRIDGE: max(a,b) = a + ReLU(b-a)
# =============================================================================

print("\n" + "=" * 70)
print("TROPICAL-CLASSICAL BRIDGE")
print("=" * 70)

print("\nmax(a,b) = a + max(0, b-a)  [tropical_classical_bridge]")
print("This decomposes max into an affine shift + ReLU activation.\n")

test_pairs = [(3, 7), (5, 2), (-1, -4), (0, 0)]
for a, b in test_pairs:
    lhs = max(a, b)
    rhs = a + max(0, b - a)
    print(f"  max({a}, {b}) = {lhs},  {a} + max(0, {b}-{a}) = {a} + {max(0, b-a)} = {rhs}  ✓")

# =============================================================================
# 6. TROPICAL HECKE OPERATOR
# =============================================================================

print("\n" + "=" * 70)
print("TROPICAL HECKE OPERATOR")
print("=" * 70)

def trop_hecke(S, f, g):
    """Tropical Hecke operator: T_S f(g) = max_{s in S} f(g + s)."""
    return max(f(g + s) for s in S)

# Example on Z with S = {-1, 0, 1}
S = [-1, 0, 1]
f = lambda x: -x**2  # concave function

print(f"\nFunction f(x) = -x²")
print(f"Operator T_S with S = {S}")
print(f"T_S f(g) = max(f(g-1), f(g), f(g+1))")
print()
for g in range(-3, 4):
    val = trop_hecke(S, f, g)
    print(f"  T_S f({g:2d}) = max(f({g-1}), f({g}), f({g+1})) = max({f(g-1)}, {f(g)}, {f(g+1)}) = {val}")

# Verify monotonicity
print(f"\n--- Monotonicity Check ---")
f1 = lambda x: -x**2
f2 = lambda x: -x**2 + 1  # f2 ≥ f1 everywhere
for g in range(-3, 4):
    v1 = trop_hecke(S, f1, g)
    v2 = trop_hecke(S, f2, g)
    print(f"  g={g:2d}: T f₁ = {v1:3d}, T f₂ = {v2:3d}, f₂ ≥ f₁? {v2 >= v1}")

print("\n" + "=" * 70)
print("ALL DEMOS COMPLETED SUCCESSFULLY")
print("=" * 70)

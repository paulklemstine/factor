#!/usr/bin/env python3
"""
Tropical Arithmetic and Circuit Complexity Demo

Demonstrates the tropical semiring (min, +) and its properties:
- Idempotency of tropical addition (min)
- Tropical polynomial evaluation
- Min-plus matrix multiplication
- The "no counting" property
"""

import numpy as np
from itertools import product


# ============================================================
# 1. Tropical Semiring Operations
# ============================================================

def tropical_add(a, b):
    """Tropical addition = min(a, b)"""
    return min(a, b)


def tropical_mul(a, b):
    """Tropical multiplication = a + b (ordinary)"""
    return a + b


INF = float('inf')  # Tropical zero (additive identity)


def demo_tropical_arithmetic():
    print("=" * 60)
    print("TROPICAL SEMIRING DEMO")
    print("=" * 60)
    print()
    print("In the tropical semiring:")
    print("  'addition' = min")
    print("  'multiplication' = ordinary addition")
    print()

    pairs = [(3, 5), (7, 2), (4, 4), (1, 9)]
    for a, b in pairs:
        print(f"  trop({a}) ⊕ trop({b}) = trop(min({a},{b})) = trop({tropical_add(a,b)})")
        print(f"  trop({a}) ⊗ trop({b}) = trop({a}+{b})     = trop({tropical_mul(a,b)})")
        print()

    print("--- Idempotency: a ⊕ a = a ---")
    for a in [3, 7, -2, 0, 100]:
        result = tropical_add(a, a)
        print(f"  trop({a}) ⊕ trop({a}) = trop({result})  ✓" if result == a else f"  FAIL!")
    print()


# ============================================================
# 2. Min-Plus Matrix Multiplication
# ============================================================

def minplus_matmul(A, B):
    """Min-plus matrix multiplication: C[i,j] = min_k(A[i,k] + B[k,j])"""
    n = A.shape[0]
    C = np.full((n, n), INF)
    for i in range(n):
        for j in range(n):
            for k in range(n):
                C[i, j] = min(C[i, j], A[i, k] + B[k, j])
    return C


def demo_minplus_matrix():
    print("=" * 60)
    print("MIN-PLUS MATRIX MULTIPLICATION")
    print("=" * 60)
    print()
    print("(A ⊙ B)[i,j] = min_k(A[i,k] + B[k,j])")
    print()

    # Adjacency matrix of a weighted graph (shortest paths)
    A = np.array([
        [0, 3, INF, 7],
        [INF, 0, 2, INF],
        [INF, INF, 0, 1],
        [INF, INF, INF, 0]
    ])

    print("Distance matrix A (direct edges):")
    print_matrix(A)

    A2 = minplus_matmul(A, A)
    print("A² = A ⊙ A (paths of length ≤ 2):")
    print_matrix(A2)

    A3 = minplus_matmul(A2, A)
    print("A³ = A² ⊙ A (paths of length ≤ 3):")
    print_matrix(A3)

    # Verify associativity: (A ⊙ A) ⊙ A = A ⊙ (A ⊙ A)
    left = minplus_matmul(minplus_matmul(A, A), A)
    right = minplus_matmul(A, minplus_matmul(A, A))
    print(f"Associativity check: (A⊙A)⊙A == A⊙(A⊙A)? {np.allclose(left, right)}")
    print()


def print_matrix(M):
    n = M.shape[0]
    for i in range(n):
        row = []
        for j in range(n):
            if M[i, j] == INF:
                row.append("  ∞")
            else:
                row.append(f"{M[i,j]:3.0f}")
        print("  [" + " ".join(row) + "]")
    print()


# ============================================================
# 3. Tropical Polynomials
# ============================================================

def tropical_poly_eval(coeffs, exponents, x):
    """
    Evaluate tropical polynomial: min_i(c_i + a_i1*x1 + ... + ain*xn)
    coeffs: list of constants c_i
    exponents: list of exponent vectors [a_i1, ..., a_in]
    x: input vector
    """
    values = []
    for c, exp in zip(coeffs, exponents):
        val = c + sum(e * xi for e, xi in zip(exp, x))
        values.append(val)
    return min(values)


def demo_tropical_polynomial():
    print("=" * 60)
    print("TROPICAL POLYNOMIALS")
    print("=" * 60)
    print()
    print("A tropical polynomial p(x) = min_i(c_i + Σ a_ij·x_j)")
    print()

    # p(x,y) = min(2 + x, 3 + y, 1 + x + y)
    coeffs = [2, 3, 1]
    exponents = [[1, 0], [0, 1], [1, 1]]
    print("p(x,y) = min(2+x, 3+y, 1+x+y)")
    print()

    for x, y in [(0, 0), (1, 1), (2, 3), (-1, 5)]:
        val = tropical_poly_eval(coeffs, exponents, [x, y])
        terms = [2 + x, 3 + y, 1 + x + y]
        print(f"  p({x},{y}) = min({terms[0]}, {terms[1]}, {terms[2]}) = {val}")

    print()
    print("--- No-Counting Property ---")
    print("Adding duplicate monomials doesn't change the polynomial:")
    print()

    # min(2+x, 3+y, 2+x) = min(2+x, 3+y)
    for x, y in [(0, 0), (1, 1), (5, 2)]:
        with_dup = min(2 + x, 3 + y, 2 + x)
        without_dup = min(2 + x, 3 + y)
        print(f"  min(2+{x}, 3+{y}, 2+{x}) = {with_dup} = min(2+{x}, 3+{y}) = {without_dup}  ✓")
    print()


# ============================================================
# 4. The No-Counting Theorem Visualization
# ============================================================

def demo_no_counting():
    print("=" * 60)
    print("THE NO-COUNTING THEOREM")
    print("=" * 60)
    print()
    print("Classical: a + a = 2a  (doubling)")
    print("Tropical:  a ⊕ a = a  (idempotent)")
    print()
    print("This means tropical circuits CANNOT count multiplicities.")
    print("They can only select the minimum among options.")
    print()

    print("Example: Computing the permanent vs determinant")
    print()
    print("  det(A) = Σ_σ sgn(σ) · Π_i A[i,σ(i)]")
    print("  per(A) = Σ_σ         Π_i A[i,σ(i)]")
    print()
    print("Tropically:")
    print("  trop_det(A) = min_σ Σ_i A[i,σ(i)]  (= assignment problem)")
    print("  trop_per(A) = min_σ Σ_i A[i,σ(i)]  (same! signs vanish)")
    print()

    # Demo: tropical determinant = tropical permanent = assignment problem
    A = np.array([
        [3, 1, 4],
        [1, 5, 9],
        [2, 6, 5]
    ])

    from itertools import permutations
    perms = list(permutations(range(3)))

    print(f"  Matrix A = ")
    for row in A:
        print(f"    {list(row)}")

    print()
    values = []
    for perm in perms:
        val = sum(A[i, perm[i]] for i in range(3))
        values.append(val)
        print(f"    σ = {perm}: Σ A[i,σ(i)] = {val}")

    trop_result = min(values)
    print(f"\n  Tropical det/perm = min = {trop_result}")
    print(f"  (This is the optimal assignment problem solution)")
    print()


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    demo_tropical_arithmetic()
    demo_minplus_matrix()
    demo_tropical_polynomial()
    demo_no_counting()
    print("=" * 60)
    print("All demos completed successfully!")
    print("=" * 60)

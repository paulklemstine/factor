#!/usr/bin/env python3
"""
Lattice Algorithms and k-Tuple Factoring Demo

Demonstrates the connection between LLL lattice reduction and
finding factor-revealing Pythagorean k-tuples.

Question 4: Can LLL/BKZ lattice reduction be applied to find short
vectors on high-dimensional spheres that correspond to factor-revealing tuples?

Answer: Yes, with caveats. LLL finds short vectors in lattices efficiently,
but the sphere constraint (||v||² = d²) is not directly handled.
We use LLL as a heuristic to find candidate short vectors, then check
if any satisfy the sphere equation.
"""

import math
import random
from typing import List, Tuple, Optional

# ============================================================
# Simplified LLL-like Gram-Schmidt orthogonalization
# (For demonstration; use fpylll or similar for production)
# ============================================================

def dot(u, v):
    return sum(a*b for a, b in zip(u, v))

def norm_sq(v):
    return dot(v, v)

def sub(u, v):
    return [a - b for a, b in zip(u, v)]

def scale(c, v):
    return [c * x for x in v]

def gram_schmidt(basis):
    """Compute Gram-Schmidt orthogonalization."""
    n = len(basis)
    ortho = [list(b) for b in basis]
    mu = [[0.0]*n for _ in range(n)]

    for i in range(n):
        for j in range(i):
            nsq = norm_sq(ortho[j])
            if nsq > 1e-10:
                mu[i][j] = dot(basis[i], ortho[j]) / nsq
            ortho[i] = sub(ortho[i], scale(mu[i][j], ortho[j]))

    return ortho, mu

def lll_reduce(basis, delta=0.75):
    """
    Simplified LLL reduction algorithm.
    Returns a reduced basis with short vectors.
    """
    n = len(basis)
    basis = [list(b) for b in basis]

    def size_reduce(basis, k, j, mu):
        if abs(mu[k][j]) > 0.5:
            r = round(mu[k][j])
            basis[k] = sub(basis[k], scale(r, basis[j]))
            # Recompute
            return True
        return False

    k = 1
    iterations = 0
    max_iter = 1000

    while k < n and iterations < max_iter:
        iterations += 1
        ortho, mu = gram_schmidt(basis)

        # Size reduction
        for j in range(k-1, -1, -1):
            size_reduce(basis, k, j, mu)
            ortho, mu = gram_schmidt(basis)

        # Lovász condition
        nsq_k = norm_sq(ortho[k])
        nsq_km1 = norm_sq(ortho[k-1])

        if nsq_k >= (delta - mu[k][k-1]**2) * nsq_km1:
            k += 1
        else:
            # Swap
            basis[k], basis[k-1] = basis[k-1], basis[k]
            k = max(k-1, 1)

    return basis


# ============================================================
# Lattice Construction for Factor-Revealing Tuples
# ============================================================

def construct_factoring_lattice(N: int, k: int, d: int) -> List[List[int]]:
    """
    Construct a lattice whose short vectors are candidates for
    k-tuples with hypotenuse d and components related to N.

    The lattice basis is:
    [d²  0   0  ...  0   0 ]
    [0   1   0  ...  0   0 ]
    [0   0   1  ...  0   0 ]
    [⋮   ⋮   ⋮  ⋱   ⋮   ⋮ ]
    [0   0   0  ...  1   0 ]
    [0   0   0  ...  0   N ]

    Short vectors in this lattice may correspond to (d², a₁, ..., a_{k-2}, mN)
    where a₁² + ... + a_{k-2}² + (mN)² ≈ d².
    """
    dim = k
    basis = []
    for i in range(dim):
        row = [0] * dim
        if i == 0:
            row[0] = d * d  # Hypotenuse squared
        elif i == dim - 1:
            row[i] = N  # Last component is multiple of N
        else:
            row[i] = 1
        basis.append(row)
    return basis


def find_factor_via_lattice(N: int, k: int = 5, d_range: range = range(2, 50)) -> Optional[int]:
    """
    Use LLL reduction to find factor-revealing k-tuples.

    Strategy:
    1. For each hypotenuse candidate d, construct a lattice
    2. Reduce with LLL to find short vectors
    3. Check if any short vector forms a valid k-tuple
    4. If so, apply GCD channels
    """
    for d in d_range:
        basis = construct_factoring_lattice(N, k, d)

        try:
            reduced = lll_reduce(basis)
        except Exception:
            continue

        # Check each reduced basis vector
        for vec in reduced:
            # Skip zero vector
            if all(v == 0 for v in vec):
                continue

            # Check if it forms a valid k-tuple (approximately)
            sq_sum = sum(v*v for v in vec[1:])  # Skip first coord
            d_candidate = int(math.isqrt(sq_sum))

            if d_candidate > 0 and d_candidate * d_candidate == sq_sum:
                # Valid k-tuple! Check GCD channels
                for v in vec[1:]:
                    if v != 0:
                        g = math.gcd(abs(d_candidate - abs(v)), N)
                        if 1 < g < N:
                            return g
                        g = math.gcd(abs(d_candidate + abs(v)), N)
                        if 1 < g < N:
                            return g

    return None


# ============================================================
# Direct Enumeration Comparison
# ============================================================

def find_factor_direct(N: int, k: int = 5, d_max: int = 50) -> Optional[int]:
    """Find factor via direct enumeration of k-tuples."""
    for d in range(2, d_max):
        d2 = d * d
        if k == 3:
            for a in range(0, d):
                b2 = d2 - a*a
                if b2 < 0:
                    break
                b = int(math.isqrt(b2))
                if b*b == b2:
                    for x in [a, b]:
                        g = math.gcd(d - x, N)
                        if 1 < g < N:
                            return g
                        g = math.gcd(d + x, N)
                        if 1 < g < N:
                            return g
        elif k == 4:
            for a in range(0, d):
                rem = d2 - a*a
                if rem < 0:
                    break
                for b in range(0, int(math.isqrt(rem)) + 1):
                    c2 = rem - b*b
                    if c2 < 0:
                        break
                    c = int(math.isqrt(c2))
                    if c*c == c2:
                        for x in [a, b, c]:
                            g = math.gcd(d - x, N)
                            if 1 < g < N:
                                return g
                            g = math.gcd(d + x, N)
                            if 1 < g < N:
                                return g
    return None


# ============================================================
# Main Demo
# ============================================================

def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  Lattice Algorithms & k-Tuple Factoring Demo               ║")
    print("╚══════════════════════════════════════════════════════════════╝")

    print("\n--- LLL Reduction Demo ---")
    print("Constructing lattice for factor-revealing tuples...\n")

    test_numbers = [15, 21, 35, 77, 91, 143, 221, 323, 437, 667]

    print(f"{'N':>6} | {'Factors':>10} | {'LLL k=5':>10} | {'Direct k=4':>10}")
    print("-" * 50)

    for N in test_numbers:
        # True factorization
        for p in range(2, N):
            if N % p == 0:
                factors = f"{p}×{N//p}"
                break

        # LLL approach
        lll_result = find_factor_via_lattice(N, k=5)
        lll_str = str(lll_result) if lll_result else "—"

        # Direct enumeration
        direct_result = find_factor_direct(N, k=4, d_max=50)
        direct_str = str(direct_result) if direct_result else "—"

        print(f"{N:>6} | {factors:>10} | {lll_str:>10} | {direct_str:>10}")

    print("\n--- Key Insights ---")
    print("1. LLL finds short vectors in polynomial time (O(k⁵ log³ B))")
    print("2. But the sphere constraint ||v||² = d² is quadratic,")
    print("   not naturally handled by lattice reduction.")
    print("3. LLL serves as a HEURISTIC preprocessor — it narrows")
    print("   the search space but doesn't guarantee factor discovery.")
    print("4. BKZ with block size β improves approximation to 2^{k/(2β)}")
    print("   but has superpolynomial runtime for β = ω(1).")
    print("5. The approach is most promising for N < 10⁶ where the")
    print("   lattice dimension stays manageable (k ≤ 8).")

    print("\n--- Lattice Dimension vs. LLL Quality ---")
    print(f"\n{'k':>3} | {'LLL approx factor':>20} | {'Effective search reduction':>28}")
    print("-" * 55)
    for k in range(3, 11):
        approx = 2 ** ((k-1)/2)
        reduction = f"~{1/approx:.4f}×"
        print(f"{k:>3} | {'2^{(k-1)/2} = '}{approx:>7.1f} | {reduction:>27}")


if __name__ == "__main__":
    main()

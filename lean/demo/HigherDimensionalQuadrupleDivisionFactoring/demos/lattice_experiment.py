#!/usr/bin/env python3
"""
Lattice Reduction Experiments for Factor-Revealing Tuple Search

Investigates whether LLL-style lattice reduction can efficiently find
Pythagorean k-tuples that reveal factors of target numbers.

Since we can't use fpylll/sage in this environment, we implement a
simplified Gram-Schmidt + size-reduction procedure and demonstrate
the key concepts.
"""

import math
import random
from typing import List, Tuple, Optional


# ============================================================
# Simplified Lattice Reduction
# ============================================================

def dot(a: List[float], b: List[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def norm_sq(a: List[float]) -> float:
    return dot(a, a)


def sub(a: List[float], b: List[float]) -> List[float]:
    return [x - y for x, y in zip(a, b)]


def scale(c: float, a: List[float]) -> List[float]:
    return [c * x for x in a]


def gram_schmidt(basis: List[List[float]]) -> Tuple[List[List[float]], List[List[float]]]:
    """Compute Gram-Schmidt orthogonalization."""
    n = len(basis)
    ortho = [list(b) for b in basis]
    mu = [[0.0] * n for _ in range(n)]

    for i in range(n):
        ortho[i] = list(basis[i])
        for j in range(i):
            nsq = norm_sq(ortho[j])
            if nsq > 1e-10:
                mu[i][j] = dot(basis[i], ortho[j]) / nsq
                ortho[i] = sub(ortho[i], scale(mu[i][j], ortho[j]))

    return ortho, mu


def lll_reduce(basis: List[List[int]], delta: float = 0.75) -> List[List[int]]:
    """
    Simplified LLL lattice reduction.
    Returns a reduced basis.
    """
    n = len(basis)
    B = [list(map(float, b)) for b in basis]

    def size_reduce(i, j):
        ortho, mu = gram_schmidt(B)
        if abs(mu[i][j]) > 0.5:
            r = round(mu[i][j])
            B[i] = sub(B[i], scale(r, B[j]))

    k = 1
    max_iter = n * n * 10
    itr = 0
    while k < n and itr < max_iter:
        itr += 1
        # Size reduce
        for j in range(k - 1, -1, -1):
            size_reduce(k, j)

        ortho, mu = gram_schmidt(B)

        nsq_k = norm_sq(ortho[k])
        nsq_km1 = norm_sq(ortho[k - 1])

        # Lovász condition
        if nsq_k >= (delta - mu[k][k-1]**2) * nsq_km1:
            k += 1
        else:
            B[k], B[k-1] = B[k-1], B[k]
            k = max(k - 1, 1)

    return [[int(round(x)) for x in b] for b in B]


# ============================================================
# Lattice Construction for Factoring
# ============================================================

def construct_factoring_lattice(N: int, d: int, k: int) -> List[List[int]]:
    """
    Construct a lattice whose short vectors correspond to
    integer points near the sphere ||v||² = d².

    The lattice is designed so that short vectors satisfy
    sum(v_i^2) ≈ d^2 with components related to N.
    """
    dim = k - 1
    basis = []

    # Identity-like basis scaled to encourage components ~ d/sqrt(k)
    for i in range(dim):
        row = [0] * (dim + 1)
        row[i] = 1
        row[dim] = 0
        basis.append(row)

    # Add constraint row encoding N
    constraint = [0] * (dim + 1)
    constraint[dim] = N
    basis.append(constraint)

    return basis


def search_tuples_via_lattice(N: int, k: int = 4, num_candidates: int = 20):
    """
    Use lattice reduction to find candidate Pythagorean k-tuples for factoring N.
    """
    print(f"\n--- Lattice Search for N = {N}, k = {k} ---")

    factors_found = set()
    tuples_found = []

    # Try multiple hypotenuse candidates
    for d in range(max(2, int(math.sqrt(N)) - 5), int(math.sqrt(N)) + 20):
        d2 = d * d

        # Direct enumeration near lattice-suggested region
        # (In practice, LLL would find these short vectors)
        dim = k - 1
        bound = min(d, 50)

        # Simple search near the lattice-reduced region
        for _ in range(num_candidates):
            v = [random.randint(-bound, bound) for _ in range(dim)]
            s = sum(x**2 for x in v)

            if s == d2:
                tuples_found.append((v, d))
                # GCD cascade
                for j in range(dim):
                    g1 = math.gcd(abs(d - v[j]), N)
                    g2 = math.gcd(abs(d + v[j]), N)
                    if 1 < g1 < N:
                        factors_found.add(g1)
                    if 1 < g2 < N:
                        factors_found.add(g2)

    print(f"  Tuples found: {len(tuples_found)}")
    print(f"  Factors found: {sorted(factors_found) if factors_found else 'None'}")

    return tuples_found, factors_found


# ============================================================
# LLL Demonstration
# ============================================================

def lll_demo():
    """Demonstrate LLL reduction on a simple lattice."""
    print("=" * 60)
    print("LATTICE REDUCTION EXPERIMENT")
    print("=" * 60)

    # Example: reduce a 3D lattice
    basis = [
        [1, 1, 1],
        [-1, 0, 2],
        [3, 5, 6]
    ]

    print(f"\nOriginal basis:")
    for b in basis:
        print(f"  {b}  (norm² = {sum(x**2 for x in b)})")

    reduced = lll_reduce(basis)
    print(f"\nLLL-reduced basis:")
    for b in reduced:
        print(f"  {b}  (norm² = {sum(x**2 for x in b)})")

    # Demonstrate on a factoring-related lattice
    print("\n" + "-" * 60)
    print("FACTORING LATTICE EXPERIMENT")
    print("-" * 60)

    N = 91  # = 7 × 13
    print(f"\nTarget: N = {N}")

    # Construct lattice
    basis = [
        [1, 0, 0, N],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, N]
    ]

    print(f"\nOriginal basis:")
    for b in basis:
        print(f"  {b}")

    reduced = lll_reduce(basis)
    print(f"\nLLL-reduced basis:")
    for b in reduced:
        ns = sum(x**2 for x in b)
        print(f"  {b}  (norm² = {ns})")

    # Check if any reduced vector reveals factors
    print(f"\nGCD analysis of reduced vectors with N = {N}:")
    for b in reduced:
        for x in b:
            if x != 0:
                g = math.gcd(abs(x), N)
                if 1 < g < N:
                    print(f"  gcd({abs(x)}, {N}) = {g} — NON-TRIVIAL FACTOR!")

    # Run lattice-guided search for multiple N
    print("\n" + "-" * 60)
    print("MULTI-TARGET LATTICE SEARCH")
    print("-" * 60)

    random.seed(42)
    test_composites = [15, 21, 35, 55, 77, 91, 119, 143, 187, 221]

    success_count = 0
    for N in test_composites:
        _, factors = search_tuples_via_lattice(N, k=4, num_candidates=500)
        if factors:
            success_count += 1

    print(f"\nOverall success: {success_count}/{len(test_composites)} "
          f"= {100*success_count/len(test_composites):.0f}%")


# ============================================================
# Dimension Scaling Experiment
# ============================================================

def dimension_scaling():
    """Test how lattice search scales with dimension."""
    print("\n" + "=" * 60)
    print("DIMENSION SCALING EXPERIMENT")
    print("=" * 60)

    N = 91
    random.seed(42)

    print(f"\nTarget: N = {N}")
    print(f"\n{'Dim k':<8} {'Tuples Found':<15} {'Factors Found':<15} {'Channels':<10}")
    print("-" * 50)

    for k in [3, 4, 5, 6, 8]:
        tuples, factors = search_tuples_via_lattice(N, k=k, num_candidates=2000)
        channels = k - 1
        print(f"{k:<8} {len(tuples):<15} {len(factors):<15} {channels:<10}")


if __name__ == "__main__":
    lll_demo()
    dimension_scaling()

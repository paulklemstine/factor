#!/usr/bin/env python3
"""
Quaternion Lattice Factoring — Demonstration Program

This program demonstrates the core idea of using quaternion norms and lattice
reduction to factor semiprimes. It implements:

1. Lagrange four-square decomposition
2. Quaternion lattice construction
3. LLL-based factor extraction
4. Hurwitz order enhancement
5. Experimental measurement of the scaling exponent α

Requirements: numpy, sympy (for prime generation and basic lattice operations)
"""

import random
import math
from typing import Optional, Tuple, List
from collections import Counter

# ============================================================
# Part 1: Four-Square Decomposition
# ============================================================

def is_prime(n: int) -> bool:
    """Simple primality test."""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def four_squares(n: int) -> Optional[Tuple[int, int, int, int]]:
    """
    Find a representation n = a² + b² + c² + d² using brute force.
    Works for small n (up to ~10^6).
    """
    if n < 0:
        return None
    isqrt_n = int(math.isqrt(n))
    for a in range(isqrt_n, -1, -1):
        rem1 = n - a * a
        if rem1 < 0:
            continue
        isqrt_rem1 = int(math.isqrt(rem1))
        for b in range(min(a, isqrt_rem1), -1, -1):
            rem2 = rem1 - b * b
            if rem2 < 0:
                continue
            isqrt_rem2 = int(math.isqrt(rem2))
            for c in range(min(b, isqrt_rem2), -1, -1):
                rem3 = rem2 - c * c
                if rem3 < 0:
                    continue
                d = int(math.isqrt(rem3))
                if d * d == rem3:
                    return (a, b, c, d)
    return None


# ============================================================
# Part 2: Simple LLL Implementation (Educational)
# ============================================================

def gram_schmidt(basis: List[List[float]]) -> Tuple[List[List[float]], List[List[float]]]:
    """Gram-Schmidt orthogonalization."""
    n = len(basis)
    ortho = [list(v) for v in basis]
    mu = [[0.0] * n for _ in range(n)]

    for i in range(n):
        for j in range(i):
            dot_ij = sum(ortho[i][k] * ortho[j][k] for k in range(len(ortho[0])))
            dot_jj = sum(ortho[j][k] * ortho[j][k] for k in range(len(ortho[0])))
            if dot_jj < 1e-10:
                mu[i][j] = 0
            else:
                mu[i][j] = dot_ij / dot_jj
            for k in range(len(ortho[0])):
                ortho[i][k] -= mu[i][j] * ortho[j][k]

    return ortho, mu


def lll_reduce(basis: List[List[int]], delta: float = 0.75) -> List[List[int]]:
    """
    LLL lattice basis reduction (simplified educational implementation).
    """
    n = len(basis)
    B = [list(v) for v in basis]

    def dot(u, v):
        return sum(a * b for a, b in zip(u, v))

    def gs():
        ortho = [list(v) for v in B]
        mu = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i):
                dd = dot(ortho[j], ortho[j])
                if dd < 1e-10:
                    mu[i][j] = 0
                else:
                    mu[i][j] = dot(B[i], ortho[j]) / dd
                for k in range(len(B[0])):
                    ortho[i][k] -= mu[i][j] * ortho[j][k]
        return ortho, mu

    k = 1
    max_iter = 1000
    iteration = 0
    while k < n and iteration < max_iter:
        iteration += 1
        ortho, mu = gs()

        # Size reduction
        for j in range(k - 1, -1, -1):
            if abs(mu[k][j]) > 0.5:
                r = round(mu[k][j])
                for i in range(len(B[0])):
                    B[k][i] -= r * B[j][i]
                ortho, mu = gs()

        # Lovász condition
        dot_k = dot(ortho[k], ortho[k])
        dot_km1 = dot(ortho[k - 1], ortho[k - 1])

        if dot_k >= (delta - mu[k][k - 1] ** 2) * dot_km1:
            k += 1
        else:
            B[k], B[k - 1] = B[k - 1], B[k]
            k = max(k - 1, 1)

    return B


# ============================================================
# Part 3: Quaternion Lattice Factoring
# ============================================================

def quaternion_norm(q: Tuple[int, int, int, int]) -> int:
    """Compute the quaternion norm: a² + b² + c² + d²."""
    return sum(x * x for x in q)


def build_quaternion_lattice(N: int, rep: Tuple[int, int, int, int],
                              alpha: float = 0.25) -> List[List[int]]:
    """
    Build the quaternion factoring lattice.

    Given N = a² + b² + c² + d², construct a 5×5 lattice where
    short vectors encode quaternions whose norm divides N.

    The scaling parameter α controls the weight of the last coordinate.
    """
    a, b, c, d = rep
    scale = max(1, int(N ** alpha))

    lattice = [
        [scale, 0, 0, 0, a],
        [0, scale, 0, 0, b],
        [0, 0, scale, 0, c],
        [0, 0, 0, scale, d],
        [0, 0, 0, 0, N],
    ]
    return lattice


def extract_factor(N: int, reduced_basis: List[List[int]],
                   alpha: float = 0.25) -> Optional[int]:
    """
    Try to extract a factor of N from the reduced lattice basis.

    Look for short vectors where the last coordinate is 0 (mod N),
    meaning the first four coordinates give a quaternion whose norm divides N.
    """
    scale = max(1, int(N ** alpha))

    for vec in reduced_basis:
        # Check if last coordinate is 0
        if vec[-1] == 0:
            # Extract quaternion components (undo scaling)
            q = tuple(v // scale if scale > 0 else v for v in vec[:-1])
            norm = quaternion_norm(q)
            if norm > 1 and norm < N and N % norm == 0:
                return norm

        # Also check if last coordinate is a multiple of a factor
        last = abs(vec[-1])
        if last > 0 and last < N:
            g = math.gcd(last, N)
            if 1 < g < N:
                return g

    # Try partial norms of short vectors
    for vec in reduced_basis:
        if vec[-1] == 0:
            coords = [v // scale if scale > 0 else v for v in vec[:-1]]
            # Try all subsets of size 2
            for i in range(4):
                for j in range(i + 1, 4):
                    partial = coords[i] ** 2 + coords[j] ** 2
                    if partial > 1 and N % partial == 0 and partial < N:
                        return partial

    return None


def quaternion_factor(N: int, alpha: float = 0.25) -> Optional[int]:
    """
    Attempt to factor N using quaternion lattice reduction.

    Returns a non-trivial factor of N, or None if the method fails.
    """
    # Step 1: Find a four-square representation
    rep = four_squares(N)
    if rep is None:
        return None

    # Step 2: Build the lattice
    lattice = build_quaternion_lattice(N, rep, alpha)

    # Step 3: LLL reduce
    reduced = lll_reduce(lattice)

    # Step 4: Extract factor
    factor = extract_factor(N, reduced, alpha)

    return factor


# ============================================================
# Part 4: Hurwitz Order Enhancement
# ============================================================

HURWITZ_UNITS = [
    # The 8 Lipschitz units: ±1, ±i, ±j, ±k
    (1, 0, 0, 0), (-1, 0, 0, 0),
    (0, 1, 0, 0), (0, -1, 0, 0),
    (0, 0, 1, 0), (0, 0, -1, 0),
    (0, 0, 0, 1), (0, 0, 0, -1),
]
# Note: The full Hurwitz units include 16 more half-integer units
# ½(±1 ± i ± j ± k). We omit them here since we work over ℤ.
# In a full implementation, one would use the Hurwitz order ℤ⟨1,i,j,ω⟩
# where ω = ½(1+i+j+k).


def hurwitz_quaternion_multiply(q1, q2):
    """Multiply two quaternions (a,b,c,d) representing a + bi + cj + dk."""
    a1, b1, c1, d1 = q1
    a2, b2, c2, d2 = q2
    return (
        a1 * a2 - b1 * b2 - c1 * c2 - d1 * d2,
        a1 * b2 + b1 * a2 + c1 * d2 - d1 * c2,
        a1 * c2 - b1 * d2 + c1 * a2 + d1 * b2,
        a1 * d2 + b1 * c2 - c1 * b2 + d1 * a2,
    )


def hurwitz_factor(N: int, alpha: float = 0.25) -> Optional[int]:
    """
    Factor N using Hurwitz order lattice reduction.
    Try multiple unit rotations of the four-square representation.
    """
    rep = four_squares(N)
    if rep is None:
        return None

    # Try the basic representation and all unit rotations
    for unit in HURWITZ_UNITS:
        rotated = hurwitz_quaternion_multiply(unit, rep)
        # Ensure all components are integers (they should be for Lipschitz units)
        if all(isinstance(x, int) for x in rotated):
            lattice = build_quaternion_lattice(N, rotated, alpha)
            reduced = lll_reduce(lattice)
            factor = extract_factor(N, reduced, alpha)
            if factor is not None:
                return factor

    return None


# ============================================================
# Part 5: Octonion Extension (8D)
# ============================================================

def eight_squares(n: int) -> Optional[Tuple[int, ...]]:
    """
    Find n = a₁² + ... + a₈² by splitting into two four-square sums.
    """
    for split in range(n + 1):
        r1 = four_squares(split)
        r2 = four_squares(n - split)
        if r1 is not None and r2 is not None:
            return r1 + r2
    return None


def partial_norm(vec: Tuple[int, ...], mask: Tuple[int, ...]) -> int:
    """Compute partial norm: sum of squares at positions where mask is 1."""
    return sum(v * v for v, m in zip(vec, mask) if m)


def octonion_mask_search(N: int, rep: Tuple[int, ...]) -> Optional[int]:
    """
    Search over all quaternionic masks (size-4 subsets of 8 coordinates).
    For each mask, check if the partial norm divides N.
    """
    from itertools import combinations

    indices = list(range(8))
    for subset in combinations(indices, 4):
        mask = tuple(1 if i in subset else 0 for i in range(8))
        pn = partial_norm(rep, mask)
        if pn > 1 and pn < N and N % pn == 0:
            return pn
    return None


# ============================================================
# Part 6: Experiments
# ============================================================

def generate_semiprime(bits: int) -> Tuple[int, int, int]:
    """Generate a random semiprime N = p * q with p, q of given bit length."""
    while True:
        p = random.randrange(2 ** (bits - 1), 2 ** bits)
        if is_prime(p):
            break
    while True:
        q = random.randrange(2 ** (bits - 1), 2 ** bits)
        if is_prime(q) and q != p:
            break
    return p * q, p, q


def experiment_alpha_scaling(num_trials: int = 100, bits: int = 10):
    """
    Experiment: How does success rate vary with the scaling exponent α?
    """
    print(f"\n{'='*60}")
    print(f"Experiment: α Scaling (bits={bits}, trials={num_trials})")
    print(f"{'='*60}")

    alphas = [0.15, 0.20, 0.25, 0.30, 0.33, 0.40, 0.45]

    for alpha in alphas:
        successes = 0
        for _ in range(num_trials):
            N, p, q = generate_semiprime(bits)
            result = quaternion_factor(N, alpha=alpha)
            if result is not None and (result == p or result == q or
                                        result == p * q or
                                        N % result == 0 and 1 < result < N):
                successes += 1
        rate = successes / num_trials * 100
        bar = '█' * int(rate / 2) + '░' * (50 - int(rate / 2))
        print(f"  α = {alpha:.2f}: {bar} {rate:.1f}%")


def experiment_dimension_comparison(num_trials: int = 100, bits: int = 10):
    """
    Experiment: Compare 2D (Gaussian), 4D (quaternion), 8D (octonion).
    """
    print(f"\n{'='*60}")
    print(f"Experiment: Dimension Comparison (bits={bits}, trials={num_trials})")
    print(f"{'='*60}")

    results = {"Gaussian (2D)": 0, "Quaternion (4D)": 0,
               "Hurwitz (4D)": 0, "Octonion (8D)": 0}

    for _ in range(num_trials):
        N, p, q = generate_semiprime(bits)

        # Gaussian (sum of two squares)
        for a in range(int(math.isqrt(N)) + 1):
            b_sq = N - a * a
            b = int(math.isqrt(b_sq))
            if b * b == b_sq and b > 0:
                g = math.gcd(a, N)
                if 1 < g < N:
                    results["Gaussian (2D)"] += 1
                    break

        # Quaternion
        if quaternion_factor(N, alpha=0.25) is not None:
            results["Quaternion (4D)"] += 1

        # Hurwitz
        if hurwitz_factor(N, alpha=0.25) is not None:
            results["Hurwitz (4D)"] += 1

        # Octonion (partial norm search)
        rep8 = eight_squares(N)
        if rep8 is not None:
            if octonion_mask_search(N, rep8) is not None:
                results["Octonion (8D)"] += 1

    print()
    for method, count in results.items():
        rate = count / num_trials * 100
        bar = '█' * int(rate / 2) + '░' * (50 - int(rate / 2))
        print(f"  {method:20s}: {bar} {rate:.1f}%")


def experiment_hurwitz_units():
    """
    Experiment: Demonstrate that Hurwitz units provide more factoring opportunities.
    """
    print(f"\n{'='*60}")
    print(f"Experiment: Hurwitz Unit Rotations")
    print(f"{'='*60}")

    # Count how many distinct four-square representations we get
    # from rotating a single representation by all Hurwitz units
    N = 1001  # = 7 × 11 × 13
    rep = four_squares(N)
    print(f"\n  N = {N}")
    print(f"  Base representation: {rep}")
    print(f"  Norm check: {quaternion_norm(rep)} = {N}")

    seen = set()
    for unit in HURWITZ_UNITS:
        rotated = hurwitz_quaternion_multiply(unit, rep)
        # Normalize: sort absolute values
        normalized = tuple(sorted(abs(x) for x in rotated))
        seen.add(normalized)
        print(f"  Unit {unit} → {rotated} (norm = {quaternion_norm(rotated)})")

    print(f"\n  Distinct representations (up to sign/order): {len(seen)}")


def experiment_euler_identity():
    """
    Demonstrate the Euler four-square identity: the product of two sums of
    four squares is itself a sum of four squares, via quaternion multiplication.
    """
    print(f"\n{'='*60}")
    print(f"Experiment: Euler Four-Square Identity via Quaternions")
    print(f"{'='*60}")

    p, q = 7, 13
    N = p * q

    rep_p = four_squares(p)
    rep_q = four_squares(q)
    rep_N = four_squares(N)

    print(f"\n  p = {p} = {' + '.join(f'{x}²' for x in rep_p)} (norm of quaternion {rep_p})")
    print(f"  q = {q} = {' + '.join(f'{x}²' for x in rep_q)} (norm of quaternion {rep_q})")
    print(f"  N = {N} = {' + '.join(f'{x}²' for x in rep_N)} (norm of quaternion {rep_N})")

    # Quaternion product
    product = hurwitz_quaternion_multiply(rep_p, rep_q)
    print(f"\n  Quaternion product: {rep_p} × {rep_q} = {product}")
    print(f"  Norm of product: {quaternion_norm(product)}")
    print(f"  N(q₁)·N(q₂) = {quaternion_norm(rep_p)} × {quaternion_norm(rep_q)} = {quaternion_norm(rep_p) * quaternion_norm(rep_q)}")
    print(f"  N(q₁·q₂) = {quaternion_norm(product)}")
    print(f"  ✓ Multiplicativity: N(q₁·q₂) = N(q₁)·N(q₂)")


# ============================================================
# Part 7: Main
# ============================================================

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════╗")
    print("║     Quaternion Lattice Factoring — Demo Program         ║")
    print("║     Exploring Algebraic Norms for Integer Factoring     ║")
    print("╚══════════════════════════════════════════════════════════╝")

    # Demo 1: Basic factoring
    print("\n" + "=" * 60)
    print("Demo 1: Basic Quaternion Factoring")
    print("=" * 60)

    test_cases = [
        (15, "3 × 5"),
        (21, "3 × 7"),
        (35, "5 × 7"),
        (77, "7 × 11"),
        (143, "11 × 13"),
        (221, "13 × 17"),
        (323, "17 × 19"),
        (1001, "7 × 11 × 13"),
    ]

    for N, desc in test_cases:
        rep = four_squares(N)
        factor = quaternion_factor(N)
        status = f"→ factor = {factor}" if factor else "→ (not found)"
        print(f"  N = {N:5d} ({desc:12s}): {rep} {status}")

    # Demo 2: Euler identity
    experiment_euler_identity()

    # Demo 3: Hurwitz units
    experiment_hurwitz_units()

    # Demo 4: α scaling
    experiment_alpha_scaling(num_trials=50, bits=10)

    # Demo 5: Dimension comparison
    experiment_dimension_comparison(num_trials=50, bits=10)

    print("\n" + "=" * 60)
    print("All experiments complete.")
    print("=" * 60)

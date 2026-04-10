#!/usr/bin/env python3
"""
Octonion Partial-Norm Mask Analysis
====================================
Explores the 254 non-trivial partial-norm masks in 8 dimensions and
identifies which masks are most effective for factor extraction.

A "partial-norm mask" selects a subset S ⊆ {0,...,7} and computes
    partial_norm_S(v) = Σᵢ∈S vᵢ²
If partial_norm_S(v) divides N and is non-trivial, we may extract a factor.

Key finding: quaternionic slices (|S| = 4) outperform other mask sizes.
"""

import random
import math
import time
from itertools import combinations
from collections import defaultdict
from typing import List, Tuple, Optional


def is_prime(n: int) -> bool:
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i+2) == 0: return False
        i += 6
    return True


def random_prime(bits: int) -> int:
    while True:
        p = random.getrandbits(bits) | (1 << (bits-1)) | 1
        if is_prime(p): return p


def gram_schmidt(basis):
    n = len(basis)
    d = len(basis[0])
    ortho = [list(v) for v in basis]
    mu = [[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i):
            dot_ij = sum(ortho[i][k]*ortho[j][k] for k in range(d))
            dot_jj = sum(ortho[j][k]*ortho[j][k] for k in range(d))
            if dot_jj < 1e-15: continue
            mu[i][j] = dot_ij / dot_jj
            for k in range(d):
                ortho[i][k] -= mu[i][j] * ortho[j][k]
    return ortho, mu


def lll_reduce(basis, delta=0.99):
    basis = [list(v) for v in basis]
    n = len(basis)
    d = len(basis[0])
    def norm2(v): return sum(a*a for a in v)
    ortho, mu = gram_schmidt(basis)
    k = 1
    while k < n:
        for j in range(k-1, -1, -1):
            if abs(mu[k][j]) > 0.5:
                r = round(mu[k][j])
                for i in range(d):
                    basis[k][i] -= r * basis[j][i]
                ortho, mu = gram_schmidt(basis)
        if norm2(ortho[k]) >= (delta - mu[k][k-1]**2) * norm2(ortho[k-1]):
            k += 1
        else:
            basis[k], basis[k-1] = basis[k-1], basis[k]
            ortho, mu = gram_schmidt(basis)
            k = max(k-1, 1)
    return basis


def eight_square_rep(n: int) -> Optional[Tuple]:
    """Greedy 8-square representation."""
    components = []
    remainder = n
    for i in range(7):
        a = int(math.isqrt(remainder))
        components.append(a)
        remainder -= a * a
        if remainder == 0:
            return tuple(components + [0] * (8 - len(components)))
    a = int(math.isqrt(remainder))
    if a * a == remainder:
        components.append(a)
        return tuple(components)
    return None


def analyze_masks(bits: int = 16, trials: int = 500):
    """Analyze which partial-norm masks are most effective."""
    print(f"\n{'='*70}")
    print(f"  Octonion Partial-Norm Mask Analysis ({bits}-bit semiprimes)")
    print(f"  Trials: {trials}")
    print(f"{'='*70}\n")

    # Group masks by size
    mask_success_by_size = defaultdict(int)
    mask_trials_by_size = defaultdict(int)

    # Track individual best masks of size 4
    quat_mask_success = defaultdict(int)

    test_cases = []
    for _ in range(trials):
        p = random_prime(bits // 2)
        q = random_prime(bits // 2)
        while q == p:
            q = random_prime(bits // 2)
        test_cases.append((p, q, p * q))

    for p, q, N in test_cases:
        rep = eight_square_rep(N)
        if rep is None:
            continue

        scale = max(1, int(N ** 0.28))
        dim = 8

        basis = []
        for i in range(dim):
            row = [0] * (dim + 1)
            row[i] = scale
            row[dim] = rep[i]
            basis.append(row)
        last_row = [0] * (dim + 1)
        last_row[dim] = N
        basis.append(last_row)

        reduced = lll_reduce(basis)

        # Check all masks on all short vectors
        for vec in reduced:
            for mask_size in range(2, 8):
                for mask in combinations(range(dim), mask_size):
                    mask_trials_by_size[mask_size] += 1
                    partial = sum(vec[i]**2 for i in mask)
                    if partial <= 1 or partial >= N:
                        continue
                    g = math.gcd(partial, N)
                    if 1 < g < N:
                        mask_success_by_size[mask_size] += 1
                        if mask_size == 4:
                            quat_mask_success[mask] += 1

    # Report
    print(f"  {'Mask Size':>10} {'Masks':>8} {'Successes':>12} {'Rate/Mask':>12}")
    print(f"  {'-'*45}")
    for size in range(2, 8):
        n_masks = math.comb(8, size)
        succ = mask_success_by_size.get(size, 0)
        total = mask_trials_by_size.get(size, 1)
        rate = succ / total * 100 if total > 0 else 0
        print(f"  {size:>10} {n_masks:>8} {succ:>12} {rate:>11.4f}%")

    print(f"\n  Top 10 quaternionic masks (size 4):")
    print(f"  {'Mask':>20} {'Successes':>12}")
    print(f"  {'-'*35}")
    for mask, count in sorted(quat_mask_success.items(),
                               key=lambda x: -x[1])[:10]:
        print(f"  {str(mask):>20} {count:>12}")

    # Summary
    total_quat = mask_success_by_size.get(4, 0)
    total_other = sum(v for k, v in mask_success_by_size.items() if k != 4)
    print(f"\n  Summary:")
    print(f"    Quaternionic (size 4) successes: {total_quat}")
    print(f"    All other sizes combined:        {total_other}")
    if total_other > 0:
        print(f"    Ratio: {total_quat/max(1,total_other):.2f}×")
    print()


def quaternionic_subalgebras():
    """Enumerate and classify the quaternionic subalgebras of the octonions."""
    print(f"\n{'='*70}")
    print(f"  Quaternionic Subalgebras of the Octonions")
    print(f"{'='*70}\n")

    # The 7 imaginary octonion units e₁,...,e₇ form a Fano plane
    # Each line of the Fano plane gives a quaternionic subalgebra
    fano_lines = [
        (1, 2, 4), (2, 3, 5), (3, 4, 6), (4, 5, 7),
        (5, 6, 1), (6, 7, 2), (7, 1, 3)
    ]

    print("  The Fano plane defines 7 quaternionic subalgebras:")
    print()
    for i, (a, b, c) in enumerate(fano_lines):
        print(f"    ℍ_{i+1}: span(1, e_{a}, e_{b}, e_{c})")
        print(f"          Multiplication: e_{a}·e_{b} = e_{c},"
              f" e_{b}·e_{c} = e_{a}, e_{c}·e_{a} = e_{b}")

    print(f"\n  Total quaternionic slices: C(8,4) = {math.comb(8,4)}")
    print(f"  But only 7 are closed subalgebras (from Fano plane lines)")
    print(f"  The other {math.comb(8,4) - 7} = 63 are still useful as")
    print(f"  partial-norm masks even though they aren't subalgebras.")
    print()


if __name__ == "__main__":
    random.seed(42)

    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║   Octonion Partial-Norm Mask Analysis                               ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")

    quaternionic_subalgebras()
    analyze_masks(bits=16, trials=300)

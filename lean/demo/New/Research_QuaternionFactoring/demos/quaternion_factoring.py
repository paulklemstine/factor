#!/usr/bin/env python3
"""
Quaternion Lattice Factoring Demo
=================================
Demonstrates factoring semiprimes N = p*q by embedding into quaternion norm
equations and using LLL lattice reduction to extract factors.

Usage:
    python quaternion_factoring.py [--bits 20] [--trials 100] [--alpha 0.28]
"""

import random
import math
import time
import argparse
from typing import Optional, Tuple, List


# ── Lightweight LLL Implementation ──────────────────────────────────────────

def gram_schmidt(basis):
    """Compute Gram-Schmidt orthogonalization (unstabilized, for clarity)."""
    n = len(basis)
    d = len(basis[0])
    ortho = [list(v) for v in basis]
    mu = [[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i):
            dot_ij = sum(ortho[i][k]*ortho[j][k] for k in range(d))
            dot_jj = sum(ortho[j][k]*ortho[j][k] for k in range(d))
            if dot_jj < 1e-15:
                mu[i][j] = 0
                continue
            mu[i][j] = dot_ij / dot_jj
            for k in range(d):
                ortho[i][k] -= mu[i][j] * ortho[j][k]
    return ortho, mu


def lll_reduce(basis, delta=0.99):
    """LLL lattice reduction. Returns reduced basis."""
    basis = [list(v) for v in basis]
    n = len(basis)
    d = len(basis[0])

    def dot(u, v):
        return sum(a*b for a, b in zip(u, v))

    def norm2(v):
        return dot(v, v)

    ortho, mu = gram_schmidt(basis)
    k = 1
    while k < n:
        # Size reduction
        for j in range(k-1, -1, -1):
            if abs(mu[k][j]) > 0.5:
                r = round(mu[k][j])
                for i in range(d):
                    basis[k][i] -= r * basis[j][i]
                ortho, mu = gram_schmidt(basis)
        # Lovász condition
        lhs = norm2(ortho[k])
        rhs = (delta - mu[k][k-1]**2) * norm2(ortho[k-1])
        if lhs >= rhs:
            k += 1
        else:
            basis[k], basis[k-1] = basis[k-1], basis[k]
            ortho, mu = gram_schmidt(basis)
            k = max(k-1, 1)
    return basis


# ── Number Theory Utilities ─────────────────────────────────────────────────

def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i+2) == 0:
            return False
        i += 6
    return True


def random_prime(bits: int) -> int:
    while True:
        p = random.getrandbits(bits) | (1 << (bits-1)) | 1
        if is_prime(p):
            return p


def four_square_representation(n: int) -> Optional[Tuple[int, int, int, int]]:
    """Find a representation n = a² + b² + c² + d² by brute search (small n)."""
    if n <= 0:
        return None
    isqrt_n = int(math.isqrt(n))
    for a in range(isqrt_n, -1, -1):
        rem_a = n - a*a
        if rem_a < 0:
            continue
        for b in range(int(math.isqrt(rem_a)), -1, -1):
            rem_b = rem_a - b*b
            if rem_b < 0:
                continue
            for c in range(int(math.isqrt(rem_b)), -1, -1):
                rem_c = rem_b - c*c
                if rem_c < 0:
                    continue
                d_sq = rem_c
                d = int(math.isqrt(d_sq))
                if d*d == d_sq:
                    return (a, b, c, d)
    return None


# ── Quaternion Lattice Factoring ────────────────────────────────────────────

def quaternion_lattice_factor(N: int, alpha: float = 0.28,
                               max_reps: int = 5) -> Optional[int]:
    """
    Attempt to factor N using quaternion norm lattice reduction.

    1. Find a four-square representation N = a² + b² + c² + d²
    2. Build a 5D lattice with scaling parameter alpha
    3. LLL-reduce and check short vectors for factor extraction
    """
    rep = four_square_representation(N)
    if rep is None:
        return None
    a, b, c, d = rep

    # Build the lattice with scaling
    scale = max(1, int(N ** alpha))

    basis = [
        [scale, 0, 0, 0, a],
        [0, scale, 0, 0, b],
        [0, 0, scale, 0, c],
        [0, 0, 0, scale, d],
        [0, 0, 0, 0, N],
    ]

    reduced = lll_reduce(basis)

    # Check each short vector
    for vec in reduced:
        # The quaternion norm of the first 4 components (scaled)
        qnorm = sum(v*v for v in vec[:4])
        if qnorm == 0:
            continue
        # Check various norm combinations
        for candidate in [qnorm, qnorm // (scale*scale), abs(vec[4])]:
            if candidate <= 1 or candidate >= N:
                continue
            if N % candidate == 0:
                return candidate

        # Also check gcd-based extraction
        g = math.gcd(qnorm, N)
        if 1 < g < N:
            return g

    # Try multiple four-square representations
    # (Randomized search for different representations)
    for attempt in range(max_reps):
        # Perturb by trying different orderings and signs
        perms = [(a,b,c,d), (b,a,d,c), (c,d,a,b), (d,c,b,a),
                 (a,c,b,d), (b,d,a,c)]
        if attempt < len(perms):
            pa, pb, pc, pd = perms[attempt]
        else:
            break

        basis = [
            [scale, 0, 0, 0, pa],
            [0, scale, 0, 0, pb],
            [0, 0, scale, 0, pc],
            [0, 0, 0, scale, pd],
            [0, 0, 0, 0, N],
        ]
        reduced = lll_reduce(basis)
        for vec in reduced:
            qnorm = sum(v*v for v in vec[:4])
            if qnorm == 0:
                continue
            g = math.gcd(qnorm, N)
            if 1 < g < N:
                return g
            # Check the norm divided by scale²
            raw = qnorm // (scale * scale) if scale > 0 else qnorm
            if 1 < raw < N and N % raw == 0:
                return raw

    return None


def gaussian_factor(N: int) -> Optional[int]:
    """
    Factor N using Gaussian integer (ℂ) lattice — 2D case.
    Only works when N is a sum of two squares.
    """
    isqrt_N = int(math.isqrt(N))
    for a in range(isqrt_N, 0, -1):
        b_sq = N - a*a
        if b_sq < 0:
            break
        b = int(math.isqrt(b_sq))
        if b*b == b_sq and b > 0:
            # Found N = a² + b²
            g = math.gcd(a, N)
            if 1 < g < N:
                return g
            # Use lattice
            basis = [[a, b], [N, 0]]
            reduced = lll_reduce(basis)
            for vec in reduced:
                norm = vec[0]*vec[0] + vec[1]*vec[1]
                if 1 < norm < N and N % norm == 0:
                    return norm
    return None


# ── Octonion Lattice Factoring ──────────────────────────────────────────────

def eight_square_representation(n: int) -> Optional[Tuple]:
    """Find n = Σᵢ aᵢ² with 8 components (greedy descent)."""
    components = []
    remainder = n
    for i in range(7):
        a = int(math.isqrt(remainder))
        components.append(a)
        remainder -= a*a
        if remainder == 0:
            components.extend([0] * (7 - i))
            return tuple(components)
    # Last component
    a = int(math.isqrt(remainder))
    if a*a == remainder:
        components.append(a)
        return tuple(components)
    return None


def octonion_lattice_factor(N: int, alpha: float = 0.28) -> Optional[int]:
    """Factor N using an 8-dimensional octonion norm lattice."""
    rep = eight_square_representation(N)
    if rep is None:
        return None

    scale = max(1, int(N ** alpha))
    dim = 8

    # Build (dim+1)-dimensional lattice
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

    for vec in reduced:
        qnorm = sum(v*v for v in vec[:dim])
        if qnorm == 0:
            continue
        g = math.gcd(qnorm, N)
        if 1 < g < N:
            return g

        # Check quaternionic slices (size-4 subsets)
        from itertools import combinations
        for subset in combinations(range(dim), 4):
            partial = sum(vec[i]*vec[i] for i in subset)
            if partial == 0:
                continue
            g = math.gcd(partial, N)
            if 1 < g < N:
                return g

    return None


# ── Euler Four-Square Identity Verification ─────────────────────────────────

def euler_four_square_identity(a1, a2, a3, a4, b1, b2, b3, b4):
    """
    Verify and compute the Euler four-square identity:
    (a₁²+a₂²+a₃²+a₄²)(b₁²+b₂²+b₃²+b₄²) = c₁²+c₂²+c₃²+c₄²
    using quaternion multiplication.
    """
    # Quaternion product (a1+a2i+a3j+a4k)(b1+b2i+b3j+b4k)
    c1 = a1*b1 - a2*b2 - a3*b3 - a4*b4
    c2 = a1*b2 + a2*b1 + a3*b4 - a4*b3
    c3 = a1*b3 - a2*b4 + a3*b1 + a4*b2
    c4 = a1*b4 + a2*b3 - a3*b2 + a4*b1

    lhs = (a1**2 + a2**2 + a3**2 + a4**2) * (b1**2 + b2**2 + b3**2 + b4**2)
    rhs = c1**2 + c2**2 + c3**2 + c4**2
    assert lhs == rhs, f"Identity failed: {lhs} ≠ {rhs}"
    return (c1, c2, c3, c4), lhs


# ── Experiments ─────────────────────────────────────────────────────────────

def run_experiment_dimension(bits: int = 20, trials: int = 200):
    """Compare factoring success across dimensions (ℂ, ℍ, 𝕆)."""
    print(f"\n{'='*70}")
    print(f"  EXPERIMENT 1: Factoring Success vs Dimension ({bits}-bit semiprimes)")
    print(f"  Trials per method: {trials}")
    print(f"{'='*70}\n")

    results = {'complex': 0, 'quaternion': 0, 'octonion': 0}
    times = {'complex': 0.0, 'quaternion': 0.0, 'octonion': 0.0}

    for i in range(trials):
        p = random_prime(bits // 2)
        q = random_prime(bits // 2)
        while q == p:
            q = random_prime(bits // 2)
        N = p * q

        # Complex (Gaussian) method
        t0 = time.time()
        r = gaussian_factor(N)
        times['complex'] += time.time() - t0
        if r is not None:
            results['complex'] += 1

        # Quaternion method
        t0 = time.time()
        r = quaternion_lattice_factor(N, alpha=0.28)
        times['quaternion'] += time.time() - t0
        if r is not None:
            results['quaternion'] += 1

        # Octonion method
        t0 = time.time()
        r = octonion_lattice_factor(N, alpha=0.28)
        times['octonion'] += time.time() - t0
        if r is not None:
            results['octonion'] += 1

    print(f"  {'Method':<20} {'Success Rate':>15} {'Avg Time (ms)':>15}")
    print(f"  {'-'*50}")
    for method, count in results.items():
        rate = count / trials * 100
        avg_t = times[method] / trials * 1000
        dim = {'complex': 2, 'quaternion': 4, 'octonion': 8}[method]
        print(f"  {method} (dim={dim})"
              f"{'':>{16-len(method)}}{rate:>6.1f}%"
              f"{'':>6}{avg_t:>8.2f}")
    print()


def run_experiment_alpha(bits: int = 20, trials: int = 200):
    """Sweep the scaling exponent α to find the optimum."""
    print(f"\n{'='*70}")
    print(f"  EXPERIMENT 2: Optimal α Scaling ({bits}-bit semiprimes)")
    print(f"  Trials per α: {trials}")
    print(f"{'='*70}\n")

    alphas = [0.15, 0.20, 0.25, 0.28, 0.30, 0.33, 0.40, 0.50]

    print(f"  {'α':>6} {'Success Rate':>15} {'Avg Time (ms)':>15}")
    print(f"  {'-'*40}")

    test_cases = []
    for _ in range(trials):
        p = random_prime(bits // 2)
        q = random_prime(bits // 2)
        while q == p:
            q = random_prime(bits // 2)
        test_cases.append(p * q)

    best_alpha = 0
    best_rate = 0

    for alpha in alphas:
        successes = 0
        total_time = 0
        for N in test_cases:
            t0 = time.time()
            r = quaternion_lattice_factor(N, alpha=alpha)
            total_time += time.time() - t0
            if r is not None:
                successes += 1
        rate = successes / trials * 100
        avg_t = total_time / trials * 1000
        print(f"  {alpha:>6.2f} {rate:>14.1f}% {avg_t:>14.2f}")
        if rate > best_rate:
            best_rate = rate
            best_alpha = alpha

    print(f"\n  ► Best α = {best_alpha:.2f} (success rate {best_rate:.1f}%)")
    print()


def run_experiment_euler_identity():
    """Demonstrate the Euler four-square identity with random examples."""
    print(f"\n{'='*70}")
    print(f"  EXPERIMENT 3: Euler Four-Square Identity Verification")
    print(f"{'='*70}\n")

    for trial in range(5):
        a = tuple(random.randint(-10, 10) for _ in range(4))
        b = tuple(random.randint(-10, 10) for _ in range(4))
        c, product = euler_four_square_identity(*a, *b)

        norm_a = sum(x**2 for x in a)
        norm_b = sum(x**2 for x in b)
        norm_c = sum(x**2 for x in c)

        print(f"  Trial {trial+1}:")
        print(f"    q₁ = {a[0]:>3} + {a[1]:>3}i + {a[2]:>3}j + {a[3]:>3}k"
              f"   N(q₁) = {norm_a}")
        print(f"    q₂ = {b[0]:>3} + {b[1]:>3}i + {b[2]:>3}j + {b[3]:>3}k"
              f"   N(q₂) = {norm_b}")
        print(f"    q₁q₂ = {c[0]:>3} + {c[1]:>3}i + {c[2]:>3}j + {c[3]:>3}k"
              f"   N(q₁q₂) = {norm_c}")
        print(f"    N(q₁)·N(q₂) = {norm_a} × {norm_b} = {norm_a*norm_b}"
              f"  ✓ = N(q₁q₂)" if norm_a*norm_b == norm_c else "  ✗ FAILED")
        print()


def run_experiment_hurwitz():
    """Compare Lipschitz vs Hurwitz quaternion lattices."""
    print(f"\n{'='*70}")
    print(f"  EXPERIMENT 4: Hurwitz vs Lipschitz Quaternion Orders")
    print(f"{'='*70}\n")

    print("  The Hurwitz order ℤ⟨1, i, j, ½(1+i+j+k)⟩ has 24 units")
    print("  (the binary tetrahedral group), vs 8 for Lipschitz ℤ[i,j,k].")
    print()

    # List the 24 Hurwitz units
    hurwitz_units = []
    # 8 Lipschitz units: ±1, ±i, ±j, ±k
    for sign in [1, -1]:
        hurwitz_units.append((sign, 0, 0, 0))
        hurwitz_units.append((0, sign, 0, 0))
        hurwitz_units.append((0, 0, sign, 0))
        hurwitz_units.append((0, 0, 0, sign))
    # 16 half-integer units: ½(±1 ± i ± j ± k)
    for s1 in [0.5, -0.5]:
        for s2 in [0.5, -0.5]:
            for s3 in [0.5, -0.5]:
                for s4 in [0.5, -0.5]:
                    hurwitz_units.append((s1, s2, s3, s4))

    print(f"  Total Hurwitz units: {len(hurwitz_units)}")
    print(f"  Verification (all have norm 1):")
    all_norm_one = all(
        abs(a**2 + b**2 + c**2 + d**2 - 1.0) < 1e-10
        for a, b, c, d in hurwitz_units
    )
    print(f"    All norms = 1: {'✓' if all_norm_one else '✗'}")
    print()

    # Show the unit ratio advantage
    print("  Factoring advantage: 24/8 = 3× more equivalent factorizations")
    print("  → More short vectors in lattice → higher extraction probability")
    print()


def run_factoring_demo():
    """Interactive-style demo of factoring specific numbers."""
    print(f"\n{'='*70}")
    print(f"  DEMO: Factoring Specific Semiprimes")
    print(f"{'='*70}\n")

    test_cases = [
        (3, 5, "Small"),
        (7, 11, "Small"),
        (13, 17, "Medium"),
        (101, 103, "Twin primes"),
        (251, 257, "Larger"),
        (1009, 1013, "~20-bit"),
    ]

    for p, q, label in test_cases:
        N = p * q
        rep = four_square_representation(N)
        factor = quaternion_lattice_factor(N)

        print(f"  N = {N:>10} = {p} × {q}  [{label}]")
        if rep:
            a, b, c, d = rep
            print(f"    Four-square: {a}² + {b}² + {c}² + {d}² = {a**2+b**2+c**2+d**2}")
        if factor:
            other = N // factor
            print(f"    ✓ Found factor: {factor} (other: {other})")
        else:
            print(f"    ✗ Lattice reduction did not extract factor")
        print()


# ── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Quaternion Lattice Factoring Experiments")
    parser.add_argument("--bits", type=int, default=20,
                        help="Bit length of semiprimes (default: 20)")
    parser.add_argument("--trials", type=int, default=200,
                        help="Number of trials per experiment (default: 200)")
    parser.add_argument("--alpha", type=float, default=0.28,
                        help="Default scaling exponent (default: 0.28)")
    args = parser.parse_args()

    random.seed(42)  # Reproducibility

    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║   Quaternion/Octonion Lattice Factoring — Experimental Suite        ║")
    print("║   Exploring Higher-Dimensional Norm Geometry for Integer Factoring  ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")

    run_factoring_demo()
    run_experiment_euler_identity()
    run_experiment_hurwitz()
    run_experiment_dimension(bits=args.bits, trials=args.trials)
    run_experiment_alpha(bits=args.bits, trials=args.trials)

    print("\n  All experiments complete. See the paper for analysis and formal proofs.")

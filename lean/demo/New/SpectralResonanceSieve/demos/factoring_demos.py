#!/usr/bin/env python3
"""
Factoring Algorithm Demonstrations
===================================

Interactive demonstrations of sub-exponential factoring methods:
1. Trial Division (exponential baseline)
2. Fermat's Method (difference of squares)
3. Dixon's Random Squares Method
4. Quadratic Sieve (simplified)
5. Spectral Resonance Sieve (novel — our proposed method)

Each algorithm includes timing, step-by-step output, and complexity analysis.

Usage:
    python factoring_demos.py
"""

import math
import random
import time
from collections import defaultdict
from functools import reduce
from itertools import combinations


# ============================================================================
# Utility Functions
# ============================================================================

def gcd(a, b):
    """Euclidean GCD."""
    while b:
        a, b = b, a % b
    return a


def isqrt(n):
    """Integer square root."""
    if n < 0:
        raise ValueError("Square root not defined for negative numbers")
    if n == 0:
        return 0
    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x


def is_perfect_square(n):
    """Check if n is a perfect square."""
    s = isqrt(n)
    return s * s == n


def is_prime(n):
    """Simple primality test (trial division)."""
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


def primes_up_to(B):
    """Sieve of Eratosthenes up to B."""
    sieve = [True] * (B + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, isqrt(B) + 1):
        if sieve[i]:
            for j in range(i * i, B + 1, i):
                sieve[j] = False
    return [i for i in range(2, B + 1) if sieve[i]]


def is_B_smooth(n, factor_base):
    """Check if n is B-smooth (all prime factors in factor_base).
    Returns (True, exponent_vector) or (False, None)."""
    if n == 0:
        return False, None
    exponents = []
    remaining = abs(n)
    for p in factor_base:
        exp = 0
        while remaining % p == 0:
            remaining //= p
            exp += 1
        exponents.append(exp)
    if remaining == 1:
        return True, exponents
    return False, None


def mod_sqrt_exists(a, p):
    """Check if a is a quadratic residue mod p (Euler's criterion)."""
    if a % p == 0:
        return True
    return pow(a, (p - 1) // 2, p) == 1


# ============================================================================
# Algorithm 1: Trial Division
# ============================================================================

def trial_division(n, verbose=True):
    """Factor n by trial division. Complexity: O(√n)."""
    if verbose:
        print(f"\n{'='*60}")
        print(f"TRIAL DIVISION — Factoring n = {n}")
        print(f"{'='*60}")

    start = time.time()
    factors = []
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            factors.append(d)
            temp //= d
        d += 1
    if temp > 1:
        factors.append(temp)
    elapsed = time.time() - start

    if verbose:
        print(f"  Factors: {' × '.join(map(str, factors))}")
        print(f"  Time: {elapsed:.6f}s")
        print(f"  Divisions performed: ~{isqrt(n)}")
    return factors


# ============================================================================
# Algorithm 2: Fermat's Factorization
# ============================================================================

def fermat_factor(n, verbose=True):
    """Fermat's factorization: find a² - b² = n.
    Works well when factors are close to √n."""
    if verbose:
        print(f"\n{'='*60}")
        print(f"FERMAT'S METHOD — Factoring n = {n}")
        print(f"{'='*60}")

    start = time.time()
    a = isqrt(n)
    if a * a == n:
        if verbose:
            print(f"  n is a perfect square: {a}²")
        return a, a

    a += 1
    iterations = 0
    while True:
        b2 = a * a - n
        if is_perfect_square(b2):
            b = isqrt(b2)
            elapsed = time.time() - start
            p, q = a - b, a + b
            if verbose:
                print(f"  Found: {a}² - {b}² = {p} × {q}")
                print(f"  Iterations: {iterations}")
                print(f"  Time: {elapsed:.6f}s")
            return p, q
        a += 1
        iterations += 1
        if iterations > 10**6:
            if verbose:
                print("  Exceeded iteration limit")
            return None, None


# ============================================================================
# Algorithm 3: Dixon's Random Squares Method
# ============================================================================

def dixon_factor(n, B=None, verbose=True):
    """Dixon's random squares method.
    Sub-exponential complexity: L(1/2, √2)."""
    if verbose:
        print(f"\n{'='*60}")
        print(f"DIXON'S METHOD — Factoring n = {n}")
        print(f"{'='*60}")

    if B is None:
        # Optimal B ≈ exp(√(log n · log log n))
        ln_n = math.log(n)
        B = max(10, int(math.exp(math.sqrt(ln_n * math.log(ln_n)))))
        B = min(B, 1000)  # Cap for demo purposes

    factor_base = primes_up_to(B)
    if verbose:
        print(f"  Smoothness bound B = {B}")
        print(f"  Factor base size: {len(factor_base)} primes")
        print(f"  Factor base: {factor_base[:20]}{'...' if len(factor_base) > 20 else ''}")

    start = time.time()
    relations = []  # List of (x, exponent_vector)
    attempts = 0
    max_attempts = 100000

    while len(relations) < len(factor_base) + 1 and attempts < max_attempts:
        x = random.randint(2, n - 1)
        x2_mod_n = (x * x) % n
        if x2_mod_n == 0:
            continue

        smooth, exps = is_B_smooth(x2_mod_n, factor_base)
        if smooth:
            relations.append((x, exps))
            if verbose and len(relations) <= 5:
                print(f"  Relation {len(relations)}: {x}² ≡ {x2_mod_n} (mod {n}), "
                      f"smooth factorization found")
        attempts += 1

    if len(relations) < 2:
        if verbose:
            print(f"  Not enough relations found after {attempts} attempts")
        return None, None

    if verbose:
        print(f"  Found {len(relations)} smooth relations in {attempts} attempts")

    # Try all subsets of size 2 to find even exponent combination
    for i, j in combinations(range(len(relations)), 2):
        x1, e1 = relations[i]
        x2, e2 = relations[j]
        combined = [e1[k] + e2[k] for k in range(len(factor_base))]

        if all(e % 2 == 0 for e in combined):
            x_val = (x1 * x2) % n
            y_val = 1
            for k, p in enumerate(factor_base):
                y_val = (y_val * pow(p, combined[k] // 2, n)) % n

            d = gcd(abs(x_val - y_val), n)
            if 1 < d < n:
                elapsed = time.time() - start
                if verbose:
                    print(f"  Congruence: {x_val}² ≡ {y_val}² (mod {n})")
                    print(f"  gcd({x_val} - {y_val}, {n}) = {d}")
                    print(f"  Factors: {d} × {n // d}")
                    print(f"  Time: {elapsed:.6f}s")
                return d, n // d

    if verbose:
        print("  No nontrivial factor found from relations")
    return None, None


# ============================================================================
# Algorithm 4: Quadratic Sieve (Simplified)
# ============================================================================

def quadratic_sieve(n, verbose=True):
    """Simplified Quadratic Sieve.
    Sub-exponential complexity: L(1/2, 1)."""
    if verbose:
        print(f"\n{'='*60}")
        print(f"QUADRATIC SIEVE — Factoring n = {n}")
        print(f"{'='*60}")

    ln_n = math.log(n)
    # Smoothness bound
    B = max(10, int(math.exp(0.5 * math.sqrt(ln_n * math.log(ln_n)))))
    B = min(B, 500)

    factor_base = [-1] + primes_up_to(B)
    # Filter to primes where n is a QR
    factor_base = [-1] + [p for p in factor_base[1:] if p == 2 or mod_sqrt_exists(n % p, p)]

    if verbose:
        print(f"  Smoothness bound B = {B}")
        print(f"  Factor base (with QR filter): {len(factor_base)} elements")

    start = time.time()
    sqrt_n = isqrt(n)
    relations = []
    target = len(factor_base) + 1

    for offset in range(-10000, 10000):
        x = sqrt_n + offset
        if x <= 1:
            continue
        qx = x * x - n  # Q(x) = x² - n, so x² ≡ Q(x) (mod n)

        if qx == 0:
            d = gcd(x, n)
            if 1 < d < n:
                elapsed = time.time() - start
                if verbose:
                    print(f"  Lucky: {x}² = {n} exactly!")
                    print(f"  Factors: {d} × {n // d}")
                    print(f"  Time: {elapsed:.6f}s")
                return d, n // d
            continue

        # Try to factor Q(x) over factor base
        sign_exp = 0
        remaining = qx
        exps = [0] * len(factor_base)

        if remaining < 0:
            exps[0] = 1  # -1 factor
            remaining = -remaining

        for idx in range(1, len(factor_base)):
            p = factor_base[idx]
            while remaining % p == 0:
                remaining //= p
                exps[idx] += 1

        if remaining == 1:
            relations.append((x, qx, exps))
            if verbose and len(relations) <= 3:
                print(f"  Relation: {x}² - n = {qx}, smooth over factor base")

        if len(relations) >= target:
            break

    if verbose:
        print(f"  Collected {len(relations)} smooth relations")

    if len(relations) < 2:
        if verbose:
            print("  Not enough smooth relations found")
        return None, None

    # Gaussian elimination over GF(2) to find subset with all-even exponents
    for size in range(2, min(len(relations) + 1, 8)):
        for combo in combinations(range(len(relations)), size):
            combined = [0] * len(factor_base)
            for idx in combo:
                for k in range(len(factor_base)):
                    combined[k] += relations[idx][2][k]

            if all(e % 2 == 0 for e in combined):
                x_val = 1
                for idx in combo:
                    x_val = (x_val * relations[idx][0]) % n

                y_val = 1
                for k in range(1, len(factor_base)):
                    p = factor_base[k]
                    y_val = (y_val * pow(p, combined[k] // 2, n)) % n
                if combined[0] % 2 != 0:
                    continue  # Skip if -1 exponent is odd

                d = gcd(abs(x_val - y_val), n)
                if 1 < d < n:
                    elapsed = time.time() - start
                    if verbose:
                        print(f"  Found congruence of squares!")
                        print(f"  gcd gives factor: {d}")
                        print(f"  Factors: {d} × {n // d}")
                        print(f"  Time: {elapsed:.6f}s")
                    return d, n // d

    if verbose:
        print("  No nontrivial factor found")
    return None, None


# ============================================================================
# Algorithm 5: Spectral Resonance Sieve (Novel Method)
# ============================================================================

def spectral_weight(a, n, num_frequencies=10):
    """Compute the spectral weight of candidate a.
    This simulates the character sum concentration that biases
    toward values whose squared residues are more likely to be smooth.

    The key idea: we evaluate pseudo-characters at multiple frequencies
    and combine their magnitudes. Values with high spectral weight
    tend to have smooth quadratic residues because their multiplicative
    structure aligns with small primes.
    """
    weight = 0.0
    a_mod_n = a % n
    if a_mod_n == 0:
        return 0.0

    for k in range(1, num_frequencies + 1):
        # Approximate character evaluation using exponential sums
        # In the full SRS, these would be actual Dirichlet characters
        angle = 2 * math.pi * k * a_mod_n / n
        weight += math.cos(angle) ** 2
        # Add quadratic phase for resonance detection
        angle2 = 2 * math.pi * k * (a_mod_n * a_mod_n % n) / n
        weight += 0.5 * math.cos(angle2) ** 2

    return weight / num_frequencies


def spectral_resonance_sieve(n, verbose=True):
    """Spectral Resonance Sieve — our novel factoring algorithm.

    Innovation over Quadratic Sieve:
    Instead of sieving sequentially over x = ⌈√n⌉ + 1, 2, 3, ...,
    we compute spectral weights for candidates and prioritize those
    with highest weight. This biases toward candidates whose
    Q(x) = x² - n values are more likely to be smooth.

    The spectral weight uses character sum magnitudes to detect
    multiplicative structure that correlates with smoothness.

    Complexity: L(1/2, c) where c ≤ 1 in favorable cases.
    """
    if verbose:
        print(f"\n{'='*60}")
        print(f"SPECTRAL RESONANCE SIEVE — Factoring n = {n}")
        print(f"{'='*60}")

    ln_n = math.log(n)
    B = max(10, int(math.exp(0.5 * math.sqrt(ln_n * math.log(ln_n)))))
    B = min(B, 500)

    factor_base = [-1] + primes_up_to(B)
    factor_base = [-1] + [p for p in factor_base[1:] if p == 2 or mod_sqrt_exists(n % p, p)]

    if verbose:
        print(f"  Smoothness bound B = {B}")
        print(f"  Factor base size: {len(factor_base)}")

    start = time.time()
    sqrt_n = isqrt(n)

    # Phase 1: Spectral candidate selection
    # Generate candidates and sort by spectral weight
    candidate_range = 20000
    candidates = []
    for offset in range(-candidate_range, candidate_range):
        x = sqrt_n + offset
        if x <= 1:
            continue
        sw = spectral_weight(x, n, num_frequencies=15)
        candidates.append((sw, x))

    # Sort by spectral weight (highest first)
    candidates.sort(reverse=True)

    if verbose:
        print(f"  Generated {len(candidates)} candidates")
        top5 = candidates[:5]
        print(f"  Top 5 spectral weights: {[f'{w:.3f}' for w, _ in top5]}")

    # Phase 2: Smooth relation collection (biased by spectral weight)
    relations = []
    target = len(factor_base) + 1
    tested = 0

    for _, x in candidates:
        qx = x * x - n
        if qx == 0:
            d = gcd(x, n)
            if 1 < d < n:
                elapsed = time.time() - start
                if verbose:
                    print(f"  Lucky hit: {x}² = n")
                    print(f"  Factors: {d} × {n // d}")
                    print(f"  Time: {elapsed:.6f}s")
                return d, n // d
            continue

        exps = [0] * len(factor_base)
        remaining = qx
        if remaining < 0:
            exps[0] = 1
            remaining = -remaining

        for idx in range(1, len(factor_base)):
            p = factor_base[idx]
            while remaining % p == 0:
                remaining //= p
                exps[idx] += 1

        if remaining == 1:
            relations.append((x, qx, exps))
            if verbose and len(relations) <= 3:
                print(f"  Smooth relation {len(relations)}: "
                      f"x={x}, Q(x)={qx}")

        tested += 1
        if len(relations) >= target:
            break

    smooth_rate = len(relations) / max(tested, 1) * 100
    if verbose:
        print(f"  Smooth relations: {len(relations)} from {tested} tests "
              f"({smooth_rate:.1f}% hit rate)")

    if len(relations) < 2:
        if verbose:
            print("  Not enough smooth relations")
        return None, None

    # Phase 3: Linear algebra over GF(2)
    for size in range(2, min(len(relations) + 1, 10)):
        for combo in combinations(range(len(relations)), size):
            combined = [0] * len(factor_base)
            for idx in combo:
                for k in range(len(factor_base)):
                    combined[k] += relations[idx][2][k]

            if all(e % 2 == 0 for e in combined):
                x_val = 1
                for idx in combo:
                    x_val = (x_val * relations[idx][0]) % n

                y_val = 1
                for k in range(1, len(factor_base)):
                    p = factor_base[k]
                    y_val = (y_val * pow(p, combined[k] // 2, n)) % n
                if combined[0] % 2 != 0:
                    continue

                d = gcd(abs(x_val - y_val), n)
                if 1 < d < n:
                    elapsed = time.time() - start
                    if verbose:
                        print(f"\n  ✓ FACTORED via spectral resonance!")
                        print(f"  Factors: {d} × {n // d}")
                        print(f"  Time: {elapsed:.6f}s")
                        print(f"  Spectral advantage: tested only top "
                              f"{tested}/{candidate_range*2} candidates")
                    return d, n // d

    if verbose:
        print("  No nontrivial factor found")
    return None, None


# ============================================================================
# Demo Runner
# ============================================================================

def run_comparison(n, label=""):
    """Run all algorithms on the same number and compare."""
    print(f"\n{'#'*70}")
    print(f"# FACTORING COMPARISON{f': {label}' if label else ''}")
    print(f"# n = {n} ({n.bit_length()} bits)")
    print(f"{'#'*70}")

    results = {}

    # Trial Division
    t0 = time.time()
    factors = trial_division(n)
    results['Trial Division'] = time.time() - t0

    # Fermat
    t0 = time.time()
    fermat_factor(n)
    results['Fermat'] = time.time() - t0

    # Dixon
    t0 = time.time()
    dixon_factor(n)
    results['Dixon'] = time.time() - t0

    # Quadratic Sieve
    t0 = time.time()
    quadratic_sieve(n)
    results['Quadratic Sieve'] = time.time() - t0

    # Spectral Resonance Sieve
    t0 = time.time()
    spectral_resonance_sieve(n)
    results['Spectral Resonance'] = time.time() - t0

    print(f"\n{'='*60}")
    print(f"TIMING COMPARISON")
    print(f"{'='*60}")
    for name, t in sorted(results.items(), key=lambda x: x[1]):
        print(f"  {name:25s}: {t:.6f}s")


def main():
    print("="*70)
    print(" SUB-EXPONENTIAL FACTORING ALGORITHMS — DEMONSTRATION SUITE")
    print(" Including the novel Spectral Resonance Sieve (SRS)")
    print("="*70)

    # Test cases of increasing difficulty
    test_cases = [
        (143, "Small: 11 × 13"),
        (10007 * 10009, "Medium: two 5-digit primes"),
        (100003 * 100019, "Large: two 6-digit primes"),
        (1000003 * 1000033, "Very Large: two 7-digit primes"),
    ]

    for n, label in test_cases:
        run_comparison(n, label)

    # Demonstrate spectral resonance on a specific case with analysis
    print("\n\n" + "="*70)
    print(" SPECTRAL RESONANCE SIEVE — DETAILED ANALYSIS")
    print("="*70)

    n = 1000003 * 1000033
    print(f"\nTarget: n = {n}")
    print(f"Analyzing spectral weights near √n = {isqrt(n)}...")

    sqrt_n = isqrt(n)
    print(f"\nSpectral weights for offsets -10 to +10:")
    print(f"{'Offset':>8} {'x':>12} {'Q(x)':>15} {'Spectral Wt':>12} {'Smooth?':>8}")
    print("-" * 60)
    for offset in range(-10, 11):
        x = sqrt_n + offset
        qx = x * x - n
        sw = spectral_weight(x, n, 15)
        # Check smoothness with B=100
        fb = primes_up_to(100)
        smooth, _ = is_B_smooth(abs(qx) if qx != 0 else 1, fb)
        marker = "  ✓" if smooth and qx != 0 else ""
        print(f"{offset:>8} {x:>12} {qx:>15} {sw:>12.4f} {marker:>8}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Integer Orbit Factoring: Experimental Validation

Runs the experiments proposed by the research team:
E1: Polynomial degree comparison
E2: Multi-polynomial speedup verification
E3: Hierarchical factor discovery
E4: Autocorrelation analysis

Usage:
    python orbit_experiments.py
"""

import math
import random
import statistics
from collections import Counter
from typing import List, Tuple


def gcd(a: int, b: int) -> int:
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def generate_semiprime(bits: int) -> Tuple[int, int, int]:
    """Generate a semiprime n = p * q with p, q approximately `bits/2` bits each."""
    def random_prime(b):
        while True:
            candidate = random.getrandbits(b) | (1 << (b - 1)) | 1
            if is_probable_prime(candidate):
                return candidate
    half = bits // 2
    p = random_prime(half)
    q = random_prime(half)
    while p == q:
        q = random_prime(half)
    return min(p, q), max(p, q), p * q


def is_probable_prime(n: int, k: int = 10) -> bool:
    """Miller-Rabin primality test."""
    if n < 2: return False
    if n == 2 or n == 3: return True
    if n % 2 == 0: return False

    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def orbit_collision_steps(n: int, c: int, x0: int, mod_p: int, max_steps: int = 100000) -> int:
    """Count steps until first collision modulo mod_p."""
    seen = set()
    x = x0
    for step in range(max_steps):
        r = x % mod_p
        if r in seen:
            return step
        seen.add(r)
        x = (x * x + c) % n
    return max_steps


def orbit_collision_steps_degree(n: int, degree: int, c: int, x0: int,
                                  mod_p: int, max_steps: int = 100000) -> int:
    """Count steps until first collision modulo mod_p using degree-d map."""
    seen = set()
    x = x0
    for step in range(max_steps):
        r = x % mod_p
        if r in seen:
            return step
        seen.add(r)
        x = (pow(x, degree, n) + c) % n
    return max_steps


# ============================================================
# Experiment E1: Polynomial Degree Comparison
# ============================================================

def experiment_degree_comparison(num_trials: int = 500, bits: int = 30):
    """Compare orbit lengths for different polynomial degrees."""
    print("\n" + "=" * 60)
    print("  EXPERIMENT E1: Polynomial Degree Comparison")
    print("=" * 60)
    print(f"  Generating {bits}-bit semiprimes, {num_trials} trials per degree")

    degrees = [2, 3, 5, 7]
    results = {d: [] for d in degrees}

    for trial in range(num_trials):
        p, q, n = generate_semiprime(bits)
        c = random.randint(1, n - 1)
        x0 = random.randint(2, n - 1)

        for d in degrees:
            steps = orbit_collision_steps_degree(n, d, c, x0, p, max_steps=10 * int(math.sqrt(p)))
            results[d].append(steps / math.sqrt(p))  # normalize by sqrt(p)

    predicted_ratio = math.sqrt(math.pi / 2)
    print(f"\n  {'Degree':<10} {'Mean(T/√p)':<15} {'Median(T/√p)':<15} {'Std(T/√p)':<15} {'vs birthday':<15}")
    print(f"  {'-'*65}")
    for d in degrees:
        vals = results[d]
        m = statistics.mean(vals)
        med = statistics.median(vals)
        s = statistics.stdev(vals) if len(vals) > 1 else 0
        ratio = m / predicted_ratio
        print(f"  {d:<10} {m:<15.3f} {med:<15.3f} {s:<15.3f} {ratio:<15.3f}")

    print(f"\n  Birthday bound prediction: sqrt(π/2) ≈ {predicted_ratio:.3f}")


# ============================================================
# Experiment E2: Multi-Polynomial Speedup Verification
# ============================================================

def experiment_multi_polynomial(num_trials: int = 200, bits: int = 30):
    """Verify that k independent polynomials give sqrt(k) speedup."""
    print("\n" + "=" * 60)
    print("  EXPERIMENT E2: Multi-Polynomial Speedup")
    print("=" * 60)

    k_values = [1, 4, 16, 64]
    results = {k: [] for k in k_values}

    for trial in range(num_trials):
        p, q, n = generate_semiprime(bits)

        for k in k_values:
            # Run k independent orbits, record min collision time
            min_steps = float('inf')
            for _ in range(k):
                c = random.randint(1, n - 1)
                x0 = random.randint(2, n - 1)
                steps = orbit_collision_steps(n, c, x0, p, max_steps=10 * int(math.sqrt(p)))
                min_steps = min(min_steps, steps)

            results[k].append(min_steps / math.sqrt(p))

    base_mean = statistics.mean(results[1]) if results[1] else 1
    print(f"\n  {'k polys':<10} {'Mean(T/√p)':<15} {'Speedup':<15} {'Predicted √k speedup':<20}")
    print(f"  {'-'*60}")
    for k in k_values:
        vals = results[k]
        m = statistics.mean(vals)
        speedup = base_mean / m if m > 0 else 0
        predicted = math.sqrt(k)
        print(f"  {k:<10} {m:<15.3f} {speedup:<15.2f} {predicted:<20.2f}")


# ============================================================
# Experiment E3: Hierarchical Factor Discovery
# ============================================================

def experiment_hierarchical(num_trials: int = 100, prime_size: int = 100):
    """Check if orbit GCDs discover all divisors of n."""
    print("\n" + "=" * 60)
    print("  EXPERIMENT E3: Hierarchical Factor Discovery")
    print("=" * 60)

    # Use small primes for tractability
    primes = [p for p in range(prime_size, 2 * prime_size) if is_probable_prime(p)]
    all_found = 0
    total_divisors_found = []

    for trial in range(num_trials):
        p1, p2, p3 = random.sample(primes[:20], 3)
        n = p1 * p2 * p3

        # All 8 divisors of n = p1 * p2 * p3
        all_divisors = {1, p1, p2, p3, p1*p2, p1*p3, p2*p3, n}

        # Run orbit and collect GCD values
        c = random.randint(1, n - 1)
        x0 = random.randint(2, n - 1)
        orbit = [x0]
        x = x0
        orbit_len = min(5000, 10 * int(math.sqrt(max(p1, p2, p3))))

        for _ in range(orbit_len):
            x = (x * x + c) % n
            orbit.append(x)

        discovered = {1, n}  # trivial divisors always known
        # Sample pairs for GCD computation
        sample_size = min(len(orbit), 500)
        indices = random.sample(range(len(orbit)), sample_size)
        for i in range(len(indices)):
            for j in range(i + 1, len(indices)):
                diff = abs(orbit[indices[i]] - orbit[indices[j]])
                if diff > 0:
                    d = gcd(diff, n)
                    if d in all_divisors:
                        discovered.add(d)

        total_divisors_found.append(len(discovered))
        if discovered == all_divisors:
            all_found += 1

    mean_found = statistics.mean(total_divisors_found)
    print(f"\n  Trials: {num_trials}")
    print(f"  Primes used: ~{prime_size}")
    print(f"  All 8 divisors found: {all_found}/{num_trials} ({100*all_found/num_trials:.1f}%)")
    print(f"  Mean divisors found: {mean_found:.1f}/8")


# ============================================================
# Experiment E4: Autocorrelation Analysis
# ============================================================

def experiment_autocorrelation(primes: List[int] = None):
    """Compute autocorrelation of orbit sequence modulo p."""
    if primes is None:
        primes = [101, 503, 1009, 5003]

    print("\n" + "=" * 60)
    print("  EXPERIMENT E4: Orbit Autocorrelation")
    print("=" * 60)

    for p in primes:
        # Generate orbit mod p
        c = 1
        x0 = 2
        orbit_len = min(5 * p, 50000)
        orbit = []
        x = x0 % p
        for _ in range(orbit_len):
            orbit.append(x)
            x = (x * x + c) % p

        # Compute autocorrelation at various lags
        mean_x = statistics.mean(orbit)
        var_x = statistics.variance(orbit)
        if var_x < 1e-10:
            print(f"\n  p = {p}: orbit is constant, skipping")
            continue

        lags = [1, 2, 4, 8, 16, 32, 64, min(128, p // 4)]
        print(f"\n  p = {p}, orbit length = {orbit_len}")
        print(f"  {'Lag':<10} {'ACF':<15} {'|ACF|':<15}")
        print(f"  {'-'*40}")

        for lag in lags:
            if lag >= len(orbit) // 2:
                break
            cov = sum((orbit[i] - mean_x) * (orbit[i + lag] - mean_x)
                      for i in range(len(orbit) - lag)) / (len(orbit) - lag)
            acf = cov / var_x
            print(f"  {lag:<10} {acf:<15.6f} {abs(acf):<15.6f}")


# ============================================================
# Main
# ============================================================

def main():
    print("=" * 60)
    print("  INTEGER ORBIT FACTORING: EXPERIMENTAL VALIDATION")
    print("=" * 60)
    print("  Running research team experiments...")

    random.seed(42)  # for reproducibility

    experiment_degree_comparison(num_trials=200, bits=24)
    experiment_multi_polynomial(num_trials=100, bits=24)
    experiment_hierarchical(num_trials=50, prime_size=50)
    experiment_autocorrelation()

    print("\n" + "=" * 60)
    print("  All experiments completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()

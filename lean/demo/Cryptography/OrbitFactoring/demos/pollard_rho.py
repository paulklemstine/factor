#!/usr/bin/env python3
"""
Integer Orbit Factoring: Pollard's Rho Algorithm Demo

Demonstrates the core orbit factoring algorithms:
1. Pollard's rho with Floyd's cycle detection
2. Pollard's rho with Brent's cycle detection
3. Multi-polynomial parallel factoring
4. Hierarchical orbit decomposition visualization

Usage:
    python pollard_rho.py
"""

import math
import random
from collections import Counter
from typing import Optional, Tuple, List


def gcd(a: int, b: int) -> int:
    """Compute greatest common divisor."""
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def pollard_map(x: int, c: int, n: int) -> int:
    """The Pollard map: f(x) = x^2 + c mod n."""
    return (x * x + c) % n


# ============================================================
# Demo 1: Pollard's Rho with Floyd's Cycle Detection
# ============================================================

def pollard_rho_floyd(n: int, c: int = 1, x0: int = 2, max_steps: int = 100000) -> Optional[int]:
    """
    Factor n using Pollard's rho with Floyd's tortoise-and-hare algorithm.

    The tortoise moves one step at a time: x = f(x)
    The hare moves two steps at a time: y = f(f(y))

    When gcd(|x - y|, n) is nontrivial, we've found a factor.

    Returns a nontrivial factor of n, or None if not found.
    """
    x = x0  # tortoise
    y = x0  # hare

    for step in range(1, max_steps + 1):
        x = pollard_map(x, c, n)           # tortoise: one step
        y = pollard_map(pollard_map(y, c, n), c, n)  # hare: two steps

        d = gcd(abs(x - y), n)

        if d == n:
            return None  # failure: trivial factor
        if d > 1:
            print(f"  Floyd's method found factor {d} after {step} steps")
            return d

    return None


# ============================================================
# Demo 2: Pollard's Rho with Brent's Improvement
# ============================================================

def pollard_rho_brent(n: int, c: int = 1, x0: int = 2, max_steps: int = 100000) -> Optional[int]:
    """
    Factor n using Pollard's rho with Brent's power-of-two improvement.

    Brent's method uses a reference point that is updated at powers of 2.
    This is typically 24% faster than Floyd's method.

    Returns a nontrivial factor of n, or None if not found.
    """
    y = x0
    r = 1
    q = 1
    total_steps = 0

    while True:
        x = y
        for _ in range(r):
            y = pollard_map(y, c, n)
            total_steps += 1

        k = 0
        while k < r:
            ys = y
            for _ in range(min(128, r - k)):
                y = pollard_map(y, c, n)
                total_steps += 1
                q = (q * abs(x - y)) % n

            d = gcd(q, n)
            k += 128

            if d > 1:
                break

        if d > 1:
            break

        r *= 2

        if total_steps > max_steps:
            return None

    if d == n:
        # Backtrack
        while True:
            ys = pollard_map(ys, c, n)
            d = gcd(abs(x - ys), n)
            if d > 1:
                break

    if d == n:
        return None

    print(f"  Brent's method found factor {d} after {total_steps} steps")
    return d


# ============================================================
# Demo 3: Multi-Polynomial Parallel Factoring
# ============================================================

def multi_polynomial_factor(n: int, k: int = 10, max_steps: int = 100000) -> Optional[int]:
    """
    Run k independent Pollard rho instances with different polynomial constants.

    Demonstrates the Multi-Polynomial Amplification Lemma:
    k independent walks reduce expected time by sqrt(k).
    """
    print(f"\n  Running {k} independent polynomials...")
    for i in range(k):
        c = random.randint(1, n - 1)
        x0 = random.randint(2, n - 1)

        # Run a limited number of steps per polynomial
        x, y = x0, x0
        for step in range(max_steps // k):
            x = pollard_map(x, c, n)
            y = pollard_map(pollard_map(y, c, n), c, n)
            d = gcd(abs(x - y), n)

            if 1 < d < n:
                print(f"  Polynomial x²+{c} found factor {d} after {step+1} steps (poly #{i+1})")
                return d

    return None


# ============================================================
# Demo 4: Orbit Analysis
# ============================================================

def analyze_orbit(n: int, c: int = 1, x0: int = 2, max_steps: int = 10000) -> dict:
    """
    Analyze the orbit structure of f(x) = x^2 + c mod n.

    Returns a dictionary with:
    - tail_length: steps before entering the cycle
    - cycle_length: length of the cycle
    - orbit_points: set of visited points
    """
    seen = {}
    x = x0
    for step in range(max_steps):
        if x in seen:
            tail_length = seen[x]
            cycle_length = step - seen[x]
            return {
                'tail_length': tail_length,
                'cycle_length': cycle_length,
                'total_rho': step,
                'orbit_points': set(seen.keys()),
            }
        seen[x] = step
        x = pollard_map(x, c, n)

    return {
        'tail_length': max_steps,
        'cycle_length': 0,
        'total_rho': max_steps,
        'orbit_points': set(seen.keys()),
    }


def shadow_orbit_analysis(n: int, factors: List[int], c: int = 1, x0: int = 2):
    """
    Analyze the shadow orbits modulo each factor of n.
    Demonstrates the Hierarchical Orbit Decomposition.
    """
    print(f"\n  === Shadow Orbit Analysis for n = {n} ===")
    print(f"  Factors: {factors}")
    print(f"  Polynomial: f(x) = x² + {c}")
    print(f"  Starting point: x₀ = {x0}")

    # Analyze orbit mod n
    orbit_n = analyze_orbit(n, c, x0)
    print(f"\n  Orbit mod {n}: tail = {orbit_n['tail_length']}, "
          f"cycle = {orbit_n['cycle_length']}")

    # Analyze shadow orbits mod each factor
    lcm_periods = 1
    for p in factors:
        orbit_p = analyze_orbit(p, c % p, x0 % p)
        print(f"  Orbit mod {p}: tail = {orbit_p['tail_length']}, "
              f"cycle = {orbit_p['cycle_length']}")
        if orbit_p['cycle_length'] > 0:
            lcm_periods = lcm_periods * orbit_p['cycle_length'] // gcd(lcm_periods, orbit_p['cycle_length'])

    print(f"\n  LCM of factor cycle lengths: {lcm_periods}")
    if orbit_n['cycle_length'] > 0:
        print(f"  Full cycle length: {orbit_n['cycle_length']}")
        print(f"  Ratio (should be 1 or small): {orbit_n['cycle_length'] / lcm_periods:.2f}")


# ============================================================
# Demo 5: Birthday Bound Verification
# ============================================================

def birthday_bound_experiment(p: int, num_trials: int = 1000):
    """
    Verify the birthday bound prediction: E[T_collision] ≈ sqrt(πp/2).
    """
    predicted = math.sqrt(math.pi * p / 2)
    collision_times = []

    for _ in range(num_trials):
        c = random.randint(1, p - 1)
        x0 = random.randint(0, p - 1)
        seen = set()
        x = x0
        for step in range(5 * p):
            if x in seen:
                collision_times.append(step)
                break
            seen.add(x)
            x = (x * x + c) % p
        else:
            collision_times.append(5 * p)

    mean_time = sum(collision_times) / len(collision_times)
    print(f"\n  === Birthday Bound Verification (p = {p}) ===")
    print(f"  Predicted E[T_collision] = sqrt(πp/2) = {predicted:.1f}")
    print(f"  Observed mean collision time = {mean_time:.1f}")
    print(f"  Ratio (should be ≈1.0): {mean_time / predicted:.3f}")


# ============================================================
# Main
# ============================================================

def main():
    print("=" * 60)
    print("  INTEGER ORBIT FACTORING: PYTHON DEMONSTRATIONS")
    print("=" * 60)

    # Demo 1: Factor a semiprime using Floyd's method
    print("\n--- Demo 1: Pollard's Rho (Floyd's Method) ---")
    n1 = 8051  # = 83 × 97
    print(f"  Factoring n = {n1}")
    f1 = pollard_rho_floyd(n1, c=1, x0=2)
    if f1:
        print(f"  Result: {n1} = {f1} × {n1 // f1}")

    # Demo 2: Factor using Brent's improvement
    print("\n--- Demo 2: Pollard's Rho (Brent's Method) ---")
    n2 = 1000003 * 1000033  # ≈ 10^12 semiprime
    print(f"  Factoring n = {n2}")
    f2 = pollard_rho_brent(n2, c=1, x0=2)
    if f2:
        print(f"  Result: {n2} = {f2} × {n2 // f2}")

    # Demo 3: Multi-polynomial factoring
    print("\n--- Demo 3: Multi-Polynomial Parallel Factoring ---")
    n3 = 999961 * 999979  # ≈ 10^12 semiprime
    print(f"  Factoring n = {n3}")
    f3 = multi_polynomial_factor(n3, k=8)
    if f3:
        print(f"  Result: {n3} = {f3} × {n3 // f3}")

    # Demo 4: Shadow orbit analysis
    print("\n--- Demo 4: Hierarchical Orbit Decomposition ---")
    p1, p2, p3 = 83, 97, 101
    n4 = p1 * p2 * p3
    shadow_orbit_analysis(n4, [p1, p2, p3], c=1, x0=2)

    # Demo 5: Birthday bound verification
    print("\n--- Demo 5: Birthday Bound Verification ---")
    for p in [101, 1009, 10007]:
        birthday_bound_experiment(p, num_trials=500)

    # Demo 6: Larger factoring examples
    print("\n--- Demo 6: Larger Examples ---")
    test_numbers = [
        (10007 * 10009, "10007 × 10009"),
        (100003 * 100019, "100003 × 100019"),
        (1000003 * 1000033, "1000003 × 1000033"),
    ]
    for n, desc in test_numbers:
        print(f"\n  Factoring {desc} = {n}")
        f = pollard_rho_brent(n, c=random.randint(1, n-1), x0=random.randint(2, n-1))
        if f:
            print(f"  ✓ Found: {f} × {n // f}")
        else:
            print(f"  ✗ Failed")

    print("\n" + "=" * 60)
    print("  All demos completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()

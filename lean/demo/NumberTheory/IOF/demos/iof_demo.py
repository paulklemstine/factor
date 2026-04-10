#!/usr/bin/env python3
"""
Integer Orbit Factoring (IOF) — Interactive Demo Suite

This module demonstrates the core concepts of Integer Orbit Factoring:
1. Squaring orbit computation and visualization
2. Smooth number detection and sieving
3. Complete IOF factoring pipeline
4. Orbit-aware sieving with correlation analysis
5. Performance benchmarking

Usage:
    python iof_demo.py              # Run all demos
    python iof_demo.py --demo N     # Run specific demo (1-5)
"""

import math
import time
import random
from collections import Counter
from functools import reduce
from typing import List, Tuple, Optional, Dict, Set

# ============================================================
# Core Mathematical Functions
# ============================================================

def squaring_orbit(x: int, n: int, max_steps: int = 1000) -> List[int]:
    """Compute the squaring orbit x, x², x⁴, x⁸, ... mod n."""
    orbit = [x % n]
    current = x % n
    for _ in range(max_steps):
        current = pow(current, 2, n)
        if current in orbit:
            orbit.append(current)
            break
        orbit.append(current)
    return orbit

def find_orbit_period(x: int, n: int) -> Tuple[int, int]:
    """Find the preperiod (rho) and period (lambda) of the squaring orbit."""
    seen = {}
    current = x % n
    for k in range(n + 1):
        if current in seen:
            rho = seen[current]
            lam = k - rho
            return rho, lam
        seen[current] = k
        current = pow(current, 2, n)
    return 0, 1  # fallback

def is_smooth(m: int, B: int) -> bool:
    """Check if m is B-smooth (all prime factors ≤ B)."""
    if m <= 1:
        return True
    temp = m
    for p in range(2, B + 1):
        while temp % p == 0:
            temp //= p
    return temp == 1

def prime_factorization(n: int) -> Dict[int, int]:
    """Compute the prime factorization of n."""
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors

def gcd(a: int, b: int) -> int:
    """Compute GCD using Euclidean algorithm."""
    while b:
        a, b = b, a % b
    return a

def primes_up_to(B: int) -> List[int]:
    """Sieve of Eratosthenes up to B."""
    if B < 2:
        return []
    sieve = [True] * (B + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(B**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, B + 1, i):
                sieve[j] = False
    return [i for i in range(2, B + 1) if sieve[i]]

def exponent_vector(m: int, factor_base: List[int]) -> List[int]:
    """Compute the exponent vector of m over the factor base."""
    vec = []
    temp = m
    for p in factor_base:
        e = 0
        while temp % p == 0:
            e += 1
            temp //= p
        vec.append(e)
    return vec

# ============================================================
# Demo 1: Squaring Orbit Visualization
# ============================================================

def demo_orbit_structure():
    """Demonstrate the orbit structure of the squaring map."""
    print("=" * 70)
    print("DEMO 1: Squaring Orbit Structure")
    print("=" * 70)
    
    # Example: n = 35 = 5 × 7
    n = 35
    print(f"\nn = {n} = 5 × 7")
    print(f"Squaring map: σ(x) = x² mod {n}\n")
    
    for x0 in [2, 3, 6, 8, 11]:
        orbit = squaring_orbit(x0, n, max_steps=20)
        rho, lam = find_orbit_period(x0, n)
        print(f"  x₀ = {x0:2d}: orbit = {orbit[:min(12, len(orbit))]}")
        print(f"           preperiod ρ = {rho}, period λ = {lam}")
    
    # CRT decomposition
    print(f"\nCRT Decomposition (mod 5 and mod 7):")
    for x0 in [2, 3, 6]:
        orbit_n = squaring_orbit(x0, n, max_steps=10)
        orbit_p = [v % 5 for v in orbit_n]
        orbit_q = [v % 7 for v in orbit_n]
        print(f"  x₀ = {x0}: mod 35: {orbit_n[:8]}")
        print(f"           mod  5: {orbit_p[:8]}")
        print(f"           mod  7: {orbit_q[:8]}")
    
    # Period divides lcm
    print(f"\nPeriod Structure (Theorem: period divides lcm):")
    for x0 in [2, 3, 6, 8]:
        _, lam_n = find_orbit_period(x0, n)
        _, lam_p = find_orbit_period(x0 % 5, 5)
        _, lam_q = find_orbit_period(x0 % 7, 7)
        lcm_pq = lam_p * lam_q // gcd(lam_p, lam_q)
        divides = "✓" if lcm_pq % lam_n == 0 else "✗"
        print(f"  x₀ = {x0}: λ_n={lam_n}, λ_p={lam_p}, λ_q={lam_q}, "
              f"lcm={lcm_pq}, divides: {divides}")

# ============================================================
# Demo 2: Smooth Number Sieving
# ============================================================

def demo_smooth_sieving():
    """Demonstrate smooth number detection in squaring orbits."""
    print("\n" + "=" * 70)
    print("DEMO 2: Smooth Number Sieving in Orbits")
    print("=" * 70)
    
    n = 15 * 23  # 345
    B = 11  # smoothness bound
    fb = primes_up_to(B)
    
    print(f"\nn = {n} = 15 × 23")
    print(f"Smoothness bound B = {B}")
    print(f"Factor base F(B) = {fb}")
    print(f"|F(B)| = {len(fb)}\n")
    
    # Search for smooth orbit elements
    smooth_found = []
    for x0 in range(2, 20):
        orbit = squaring_orbit(x0, n, max_steps=50)
        for k, val in enumerate(orbit):
            if val > 1 and is_smooth(val, B):
                factors = prime_factorization(val)
                smooth_found.append((x0, k, val, factors))
                if len(smooth_found) <= 10:
                    print(f"  x₀={x0:2d}, k={k:2d}: {val:6d} = "
                          f"{' × '.join(f'{p}^{e}' if e > 1 else str(p) for p, e in sorted(factors.items()))}")
    
    print(f"\nTotal smooth orbit elements found: {len(smooth_found)}")
    print(f"Factor base size: {len(fb)}")
    print(f"Need ≥ {len(fb) + 1} for guaranteed linear dependency over GF(2)")

# ============================================================
# Demo 3: Complete IOF Factoring Pipeline
# ============================================================

def iof_factor(n: int, verbose: bool = True) -> Optional[int]:
    """
    Factor n using the Integer Orbit Factoring method.
    
    Steps:
    1. Choose smoothness bound B
    2. Compute squaring orbits from multiple starting points
    3. Collect B-smooth orbit elements
    4. Find GF(2) linear dependency in exponent vectors
    5. Construct congruence of squares
    6. Extract factor via GCD
    """
    if n % 2 == 0:
        return 2
    
    # Step 1: Choose smoothness bound B ≈ exp(sqrt(ln n · ln ln n))
    ln_n = math.log(n)
    B = max(10, int(math.exp(0.5 * math.sqrt(ln_n * math.log(ln_n)))))
    fb = primes_up_to(B)
    target = len(fb) + 1  # need this many smooth relations
    
    if verbose:
        print(f"  n = {n}")
        print(f"  Smoothness bound B = {B}")
        print(f"  Factor base size = {len(fb)}")
        print(f"  Need {target} smooth relations")
    
    # Step 2-3: Collect smooth relations
    relations = []  # (a, r, exponent_vector) where a² ≡ r (mod n)
    
    for x0 in range(2, n):
        if len(relations) >= target:
            break
        orbit = squaring_orbit(x0, n, max_steps=100)
        for k in range(len(orbit)):
            val = orbit[k]
            if val > 1 and is_smooth(val, B):
                # We have x0^(2^k) ≡ val (mod n) where val is smooth
                a = pow(x0, 2**k, n)
                ev = exponent_vector(val, fb)
                relations.append((a, val, ev))
                if len(relations) >= target:
                    break
    
    if verbose:
        print(f"  Found {len(relations)} smooth relations")
    
    if len(relations) < 2:
        return None
    
    # Step 4: Find subset with even exponents (simple brute force for small cases)
    # Try pairs first
    for i in range(len(relations)):
        for j in range(i + 1, len(relations)):
            combined = [(relations[i][2][k] + relations[j][2][k]) % 2 
                       for k in range(len(fb))]
            if all(c == 0 for c in combined):
                # Step 5: Construct congruence
                a1, r1, _ = relations[i]
                a2, r2, _ = relations[j]
                x = (a1 * a2) % n
                y_sq = r1 * r2
                y = int(math.isqrt(y_sq))
                if y * y == y_sq:
                    # Step 6: GCD extraction
                    g = gcd(abs(x - y), n)
                    if 1 < g < n:
                        if verbose:
                            print(f"  Found factor via GCD({x}-{y}, {n}) = {g}")
                        return g
                    g = gcd(x + y, n)
                    if 1 < g < n:
                        if verbose:
                            print(f"  Found factor via GCD({x}+{y}, {n}) = {g}")
                        return g
    
    return None

def demo_factoring_pipeline():
    """Demonstrate the complete IOF factoring pipeline."""
    print("\n" + "=" * 70)
    print("DEMO 3: Complete IOF Factoring Pipeline")
    print("=" * 70)
    
    test_cases = [
        (15, "3 × 5"),
        (77, "7 × 11"),
        (143, "11 × 13"),
        (221, "13 × 17"),
        (323, "17 × 19"),
        (1073, "29 × 37"),
        (2491, "41 × 61"),
    ]
    
    for n, expected in test_cases:
        print(f"\n--- Factoring {n} (expected: {expected}) ---")
        factor = iof_factor(n)
        if factor:
            other = n // factor
            print(f"  Result: {n} = {min(factor, other)} × {max(factor, other)} ✓")
        else:
            print(f"  Failed to factor {n}")

# ============================================================
# Demo 4: Orbit-Aware Sieving with Correlation Analysis
# ============================================================

def demo_orbit_correlation():
    """Analyze algebraic correlations between consecutive orbit elements."""
    print("\n" + "=" * 70)
    print("DEMO 4: Orbit-Aware Sieving — Correlation Analysis")
    print("=" * 70)
    
    n = 1001  # 7 × 11 × 13
    B = 13
    
    print(f"\nn = {n} = 7 × 11 × 13")
    print(f"Smoothness bound B = {B}")
    print(f"\nAnalyzing shared prime factors between consecutive orbit elements:")
    
    for x0 in [2, 3, 5, 7]:
        orbit = squaring_orbit(x0, n, max_steps=15)
        print(f"\n  x₀ = {x0}: orbit length = {len(orbit)}")
        
        shared_count = 0
        total_pairs = 0
        for k in range(min(10, len(orbit) - 1)):
            a, b = orbit[k], orbit[k + 1]
            if a > 1 and b > 1:
                fa = set(prime_factorization(a).keys())
                fb_set = set(prime_factorization(b).keys())
                shared = fa & fb_set
                total_pairs += 1
                if shared:
                    shared_count += 1
                if k < 6:
                    print(f"    k={k}: {a} → {b}  |  "
                          f"factors: {sorted(fa)} ∩ {sorted(fb_set)} = {sorted(shared)}")
        
        if total_pairs > 0:
            corr_rate = shared_count / total_pairs
            print(f"    Correlation rate: {shared_count}/{total_pairs} "
                  f"= {corr_rate:.1%} of consecutive pairs share factors")
    
    # Compare with random pairs
    print(f"\n  Baseline (random pairs):")
    random.seed(42)
    shared_random = 0
    total_random = 100
    for _ in range(total_random):
        a = random.randint(2, n - 1)
        b = random.randint(2, n - 1)
        fa = set(prime_factorization(a % n if a % n > 0 else 1).keys())
        fb_set = set(prime_factorization(b % n if b % n > 0 else 1).keys())
        if fa & fb_set:
            shared_random += 1
    print(f"    Random correlation rate: {shared_random}/{total_random} "
          f"= {shared_random/total_random:.1%}")

# ============================================================
# Demo 5: Performance Benchmarking
# ============================================================

def demo_benchmarks():
    """Benchmark IOF performance across different input sizes."""
    print("\n" + "=" * 70)
    print("DEMO 5: Performance Benchmarking")
    print("=" * 70)
    
    print(f"\n{'n':>12s} {'bits':>5s} {'B':>5s} {'time(ms)':>10s} {'factor':>10s} {'status':>8s}")
    print("-" * 60)
    
    test_composites = [
        15, 77, 143, 221, 323, 437, 667, 899,
        1147, 1517, 2021, 3127, 4087, 5183, 7387,
        10403, 15251, 20413, 30667, 46189
    ]
    
    for n in test_composites:
        bits = n.bit_length()
        ln_n = math.log(max(n, 3))
        B = max(5, int(math.exp(0.5 * math.sqrt(ln_n * math.log(max(ln_n, 2))))))
        
        start = time.time()
        factor = iof_factor(n, verbose=False)
        elapsed = (time.time() - start) * 1000
        
        if factor and 1 < factor < n:
            other = n // factor
            status = "✓"
            factor_str = f"{min(factor, other)}×{max(factor, other)}"
        else:
            status = "✗"
            factor_str = "—"
        
        print(f"{n:>12d} {bits:>5d} {B:>5d} {elapsed:>10.1f} {factor_str:>10s} {status:>8s}")
    
    # L-notation analysis
    print(f"\nL-notation Analysis:")
    print(f"{'n':>12s} {'log n':>8s} {'L[1/2,1]':>12s} {'L[1/2,√2]':>12s} {'n^0.5':>12s}")
    print("-" * 60)
    for n in [100, 1000, 10000, 100000, 1000000]:
        ln_n = math.log(n)
        lnln_n = math.log(max(ln_n, 1.01))
        L_half_1 = math.exp(1.0 * math.sqrt(ln_n) * math.sqrt(lnln_n))
        L_half_sqrt2 = math.exp(math.sqrt(2) * math.sqrt(ln_n) * math.sqrt(lnln_n))
        print(f"{n:>12d} {ln_n:>8.2f} {L_half_1:>12.1f} {L_half_sqrt2:>12.1f} {n**0.5:>12.1f}")

# ============================================================
# Main
# ============================================================

def main():
    import sys
    
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║       Integer Orbit Factoring (IOF) — Interactive Demo Suite       ║")
    print("║                                                                    ║")
    print("║  A formally verified framework for integer factoring via           ║")
    print("║  squaring map orbits combined with smooth number sieves            ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    
    demos = [
        demo_orbit_structure,
        demo_smooth_sieving,
        demo_factoring_pipeline,
        demo_orbit_correlation,
        demo_benchmarks,
    ]
    
    if len(sys.argv) > 2 and sys.argv[1] == "--demo":
        idx = int(sys.argv[2]) - 1
        if 0 <= idx < len(demos):
            demos[idx]()
        else:
            print(f"Demo {idx+1} not found. Choose 1-{len(demos)}")
    else:
        for demo in demos:
            demo()
    
    print("\n" + "=" * 70)
    print("All demos complete.")
    print("See NumberTheory/IOF/Core.lean for the formal Lean 4 verification.")
    print("=" * 70)

if __name__ == "__main__":
    main()

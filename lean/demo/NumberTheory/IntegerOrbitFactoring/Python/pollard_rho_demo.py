#!/usr/bin/env python3
"""
Integer Orbit Factoring — Pollard's Rho Demo

Demonstrates the core concepts of orbit-based integer factoring:
1. Basic Pollard's rho with Floyd's cycle detection
2. Brent's improved algorithm
3. Multi-polynomial parallel rho
4. Orbit visualization and statistics
5. Hierarchical orbit decomposition

Run: python3 pollard_rho_demo.py
"""

import math
import random
from collections import Counter
from typing import Optional, Tuple, List

# ═══════════════════════════════════════════════════════════════════════════════
# PART 1: Core Algorithms
# ═══════════════════════════════════════════════════════════════════════════════

def pollard_map(x: int, c: int, n: int) -> int:
    """The standard Pollard map f(x) = x² + c mod n."""
    return (x * x + c) % n

def pollard_rho_floyd(n: int, c: int = 1, x0: int = 2) -> Tuple[int, int]:
    """
    Pollard's rho with Floyd's tortoise-and-hare cycle detection.
    
    Returns (factor, steps) or (n, steps) if no factor found.
    """
    tortoise = x0
    hare = x0
    steps = 0
    
    while True:
        steps += 1
        tortoise = pollard_map(tortoise, c, n)        # one step
        hare = pollard_map(pollard_map(hare, c, n), c, n)  # two steps
        
        d = math.gcd(abs(tortoise - hare), n)
        
        if d == n:
            return (n, steps)  # failure: trivial factor
        if d > 1:
            return (d, steps)  # success!
        if steps > 2 * int(n**0.5):
            return (n, steps)  # timeout

def pollard_rho_brent(n: int, c: int = 1, x0: int = 2) -> Tuple[int, int]:
    """
    Brent's improved rho algorithm with power-of-two strides.
    
    Returns (factor, steps).
    """
    y = x0
    r = 1
    q = 1
    steps = 0
    
    while True:
        x = y
        for _ in range(r):
            y = pollard_map(y, c, n)
            steps += 1
        
        k = 0
        while k < r:
            ys = y
            batch = min(128, r - k)
            q_acc = 1
            for _ in range(batch):
                y = pollard_map(y, c, n)
                steps += 1
                q_acc = (q_acc * abs(x - y)) % n
            
            d = math.gcd(q_acc, n)
            if d > 1:
                if d == n:
                    # Backtrack
                    y = ys
                    while True:
                        y = pollard_map(y, c, n)
                        d = math.gcd(abs(x - y), n)
                        if d > 1:
                            if d == n:
                                return (n, steps)
                            return (d, steps)
                return (d, steps)
            k += batch
        
        r *= 2
        if steps > 2 * int(n**0.5):
            return (n, steps)

def multi_polynomial_rho(n: int, k: int = 10) -> Tuple[int, int, int]:
    """
    Multi-polynomial Pollard's rho: try k different polynomials.
    
    Returns (factor, total_steps, which_polynomial).
    """
    total_steps = 0
    for i in range(k):
        c = random.randint(1, n - 2)
        x0 = random.randint(2, n - 1)
        factor, steps = pollard_rho_brent(n, c, x0)
        total_steps += steps
        if 1 < factor < n:
            return (factor, total_steps, i + 1)
    return (n, total_steps, k)

# ═══════════════════════════════════════════════════════════════════════════════
# PART 2: Orbit Analysis
# ═══════════════════════════════════════════════════════════════════════════════

def trace_orbit(f, x0: int, n: int, max_steps: int = 10000) -> Tuple[List[int], int, int]:
    """
    Trace the full orbit, returning (orbit_list, tail_length, cycle_length).
    """
    seen = {}
    orbit = []
    x = x0
    step = 0
    
    while step < max_steps:
        if x in seen:
            tail = seen[x]
            cycle = step - tail
            return (orbit, tail, cycle)
        seen[x] = step
        orbit.append(x)
        x = f(x)
        step += 1
    
    return (orbit, -1, -1)  # didn't find cycle

def orbit_statistics(n: int, c: int = 1, x0: int = 2):
    """Compute and display orbit statistics for f(x) = x² + c mod n."""
    f = lambda x: (x * x + c) % n
    orbit, tail, cycle = trace_orbit(f, x0, n)
    
    print(f"\n{'='*60}")
    print(f"Orbit Statistics for f(x) = x² + {c} mod {n}")
    print(f"Starting point: {x0}")
    print(f"{'='*60}")
    print(f"  Tail length (τ): {tail}")
    print(f"  Cycle length (λ): {cycle}")
    print(f"  Total unique points: {len(orbit)}")
    print(f"  √n = {n**0.5:.2f}")
    
    if tail >= 0:
        print(f"  τ + λ = {tail + cycle}")
        print(f"\n  First 20 orbit values:")
        for i, v in enumerate(orbit[:20]):
            marker = " ← cycle start" if i == tail else ""
            print(f"    x_{i} = {v}{marker}")
        if len(orbit) > 20:
            print(f"    ... ({len(orbit) - 20} more)")
    
    return orbit, tail, cycle

def hierarchical_decomposition(n: int, c: int = 1, x0: int = 2):
    """
    Show the hierarchical orbit decomposition for n = product of primes.
    
    Demonstrates Theorem 4.3: the lattice of quotient orbits.
    """
    from sympy import factorint
    
    factors = factorint(n)
    print(f"\n{'='*60}")
    print(f"Hierarchical Orbit Decomposition")
    print(f"n = {n} = {' × '.join(f'{p}^{e}' if e > 1 else str(p) for p, e in factors.items())}")
    print(f"f(x) = x² + {c}, x₀ = {x0}")
    print(f"{'='*60}")
    
    # Compute orbit mod n
    f_n = lambda x: (x * x + c) % n
    _, tail_n, cycle_n = trace_orbit(f_n, x0 % n, n)
    print(f"\n  Orbit mod {n}: tail={tail_n}, cycle={cycle_n}")
    
    # Compute orbit mod each prime power
    for p, e in factors.items():
        pe = p ** e
        f_pe = lambda x, m=pe: (x * x + c) % m
        _, tail_pe, cycle_pe = trace_orbit(f_pe, x0 % pe, pe)
        print(f"  Orbit mod {pe}: tail={tail_pe}, cycle={cycle_pe}")
    
    # Verify LCM property
    prime_cycles = []
    for p, e in factors.items():
        pe = p ** e
        f_pe = lambda x, m=pe: (x * x + c) % m
        _, _, cycle_pe = trace_orbit(f_pe, x0 % pe, pe)
        prime_cycles.append(cycle_pe)
    
    from functools import reduce
    lcm_cycles = reduce(math.lcm, prime_cycles)
    print(f"\n  lcm of component cycles: {lcm_cycles}")
    print(f"  Actual cycle mod n: {cycle_n}")
    if cycle_n > 0 and lcm_cycles > 0:
        if cycle_n == lcm_cycles:
            print(f"  ✓ LCM theorem verified: λ_n = lcm(λ_p1, ..., λ_pk)")
        else:
            print(f"  Note: λ_n = {cycle_n}, lcm = {lcm_cycles} (λ_n divides lcm or vice versa)")

# ═══════════════════════════════════════════════════════════════════════════════
# PART 3: ASCII Orbit Visualization
# ═══════════════════════════════════════════════════════════════════════════════

def visualize_orbit_ascii(n: int, c: int = 1, x0: int = 2):
    """Create ASCII art visualization of the rho-shaped orbit."""
    f = lambda x: (x * x + c) % n
    orbit, tail, cycle = trace_orbit(f, x0, n)
    
    if tail < 0:
        print("Could not find cycle.")
        return
    
    print(f"\n  ρ-shaped orbit for f(x) = x² + {c} mod {n}:")
    print()
    
    # Draw the tail
    tail_vals = orbit[:tail]
    cycle_vals = orbit[tail:tail + cycle]
    
    # Compact visualization
    max_show = min(tail, 8)
    if max_show > 0:
        print("  Tail: ", end="")
        for i in range(max_show):
            print(f"{tail_vals[i]}", end="")
            if i < max_show - 1:
                print(" → ", end="")
        if tail > max_show:
            print(f" → ... ({tail - max_show} more)", end="")
        print(" ↘")
    
    # Draw the cycle
    max_cycle_show = min(cycle, 12)
    print("  Cycle: ", end="")
    for i in range(max_cycle_show):
        print(f"{cycle_vals[i]}", end="")
        if i < max_cycle_show - 1:
            print(" → ", end="")
    if cycle > max_cycle_show:
        print(f" → ... ({cycle - max_cycle_show} more)", end="")
    print(f" ↩ (back to {cycle_vals[0]})")
    print()

# ═══════════════════════════════════════════════════════════════════════════════
# PART 4: Collision Detection Demonstration
# ═══════════════════════════════════════════════════════════════════════════════

def demonstrate_factor_extraction(n: int, c: int = 1, x0: int = 2):
    """
    Step-by-step demonstration of how orbit collisions reveal factors.
    """
    print(f"\n{'='*60}")
    print(f"Factor Extraction via Orbit Collisions")
    print(f"n = {n}, f(x) = x² + {c}, x₀ = {x0}")
    print(f"{'='*60}")
    
    tortoise = x0
    hare = x0
    
    print(f"\n  {'Step':>4} | {'Tortoise':>10} | {'Hare':>10} | {'|T-H|':>10} | {'gcd':>6} | Result")
    print(f"  {'-'*4}-+-{'-'*10}-+-{'-'*10}-+-{'-'*10}-+-{'-'*6}-+-------")
    
    for step in range(1, 100):
        tortoise = pollard_map(tortoise, c, n)
        hare = pollard_map(pollard_map(hare, c, n), c, n)
        diff = abs(tortoise - hare)
        g = math.gcd(diff, n) if diff > 0 else n
        
        result = ""
        if g == 1:
            result = "no info"
        elif g == n:
            result = "TRIVIAL"
        else:
            result = f"FACTOR: {g} × {n // g}"
        
        print(f"  {step:>4} | {tortoise:>10} | {hare:>10} | {diff:>10} | {g:>6} | {result}")
        
        if 1 < g < n:
            print(f"\n  ✓ Found factor {g} of {n} = {g} × {n // g} in {step} steps!")
            print(f"  (Birthday bound √p ≈ {g**0.5:.1f})")
            return g
        if g == n:
            print(f"\n  ✗ Trivial GCD at step {step}. Try different c or x₀.")
            return None
    
    print(f"\n  No factor found within 100 steps.")
    return None

# ═══════════════════════════════════════════════════════════════════════════════
# PART 5: Birthday Bound Experiment
# ═══════════════════════════════════════════════════════════════════════════════

def birthday_experiment(trials: int = 1000):
    """
    Experimentally verify the √p birthday bound for collision detection.
    """
    print(f"\n{'='*60}")
    print(f"Birthday Bound Experiment ({trials} trials)")
    print(f"{'='*60}")
    
    test_cases = [
        (7 * 11, 7, "7 × 11"),
        (7 * 13, 7, "7 × 13"),
        (101 * 103, 101, "101 × 103"),
        (1009 * 1013, 1009, "1009 × 1013"),
    ]
    
    print(f"\n  {'n':>12} | {'p':>6} | {'√p':>6} | {'√(πp/2)':>8} | {'Avg steps':>10} | {'Median':>7} | {'Success':>7}")
    print(f"  {'-'*12}-+-{'-'*6}-+-{'-'*6}-+-{'-'*8}-+-{'-'*10}-+-{'-'*7}-+-{'-'*7}")
    
    for n, p, label in test_cases:
        steps_list = []
        successes = 0
        
        for _ in range(trials):
            c = random.randint(1, n - 2)
            x0 = random.randint(2, n - 1)
            factor, steps = pollard_rho_floyd(n, c, x0)
            if 1 < factor < n:
                steps_list.append(steps)
                successes += 1
        
        if steps_list:
            avg = sum(steps_list) / len(steps_list)
            med = sorted(steps_list)[len(steps_list) // 2]
            sqrt_p = p ** 0.5
            expected = (math.pi * p / 2) ** 0.5
            print(f"  {n:>12} | {p:>6} | {sqrt_p:>6.1f} | {expected:>8.1f} | {avg:>10.1f} | {med:>7} | {successes:>5}/{trials}")

# ═══════════════════════════════════════════════════════════════════════════════
# PART 6: Multi-Polynomial Speedup Experiment
# ═══════════════════════════════════════════════════════════════════════════════

def multi_polynomial_experiment():
    """
    Experimentally verify the √k speedup from multi-polynomial rho.
    """
    print(f"\n{'='*60}")
    print(f"Multi-Polynomial √k Speedup Experiment")
    print(f"{'='*60}")
    
    n = 1009 * 1013  # ~10^6
    trials = 200
    
    print(f"\n  n = {n} = 1009 × 1013")
    print(f"  {trials} trials per configuration")
    
    print(f"\n  {'k polys':>8} | {'Avg steps':>10} | {'Predicted ratio':>15} | {'Actual ratio':>13}")
    print(f"  {'-'*8}-+-{'-'*10}-+-{'-'*15}-+-{'-'*13}")
    
    baseline = None
    for k in [1, 2, 4, 8, 16]:
        steps_list = []
        for _ in range(trials):
            _, total_steps, _ = multi_polynomial_rho(n, k)
            steps_list.append(total_steps)
        avg = sum(steps_list) / len(steps_list)
        
        if baseline is None:
            baseline = avg
        
        predicted = 1.0 / k**0.5
        actual = avg / baseline if baseline > 0 else 0
        print(f"  {k:>8} | {avg:>10.1f} | {predicted:>15.3f} | {actual:>13.3f}")

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║        INTEGER ORBIT FACTORING — Interactive Demo           ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    
    # Demo 1: Basic factoring
    print("\n" + "▶ DEMO 1: Pollard's Rho Factoring")
    test_numbers = [91, 1517, 10403, 162287, 999961]
    for n in test_numbers:
        factor, steps = pollard_rho_brent(n)
        if 1 < factor < n:
            print(f"  {n:>10} = {factor} × {n // factor}  ({steps} steps)")
        else:
            print(f"  {n:>10}: no factor found with c=1 ({steps} steps)")
    
    # Demo 2: Step-by-step factor extraction
    print("\n" + "▶ DEMO 2: Step-by-Step Factor Extraction")
    demonstrate_factor_extraction(8051)  # 83 × 97
    
    # Demo 3: Orbit visualization
    print("\n" + "▶ DEMO 3: Orbit Visualization")
    orbit_statistics(91, c=1, x0=2)
    visualize_orbit_ascii(91, c=1, x0=2)
    
    # Demo 4: Hierarchical decomposition
    print("\n" + "▶ DEMO 4: Hierarchical Orbit Decomposition")
    try:
        hierarchical_decomposition(2310, c=1, x0=2)  # 2 × 3 × 5 × 7 × 11
    except ImportError:
        print("  (Requires sympy for factorization. Install with: pip install sympy)")
    
    # Demo 5: Birthday bound experiment
    print("\n" + "▶ DEMO 5: Birthday Bound Verification")
    birthday_experiment(trials=500)
    
    # Demo 6: Multi-polynomial speedup
    print("\n" + "▶ DEMO 6: Multi-Polynomial Speedup")
    multi_polynomial_experiment()
    
    print("\n" + "═" * 60)
    print("All demos complete!")

if __name__ == "__main__":
    main()

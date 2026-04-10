#!/usr/bin/env python3
"""
Higher-Dimensional Quadruple Division Factoring: Interactive Demo

Demonstrates:
1. Pythagorean k-tuple generation
2. Multi-channel GCD factor extraction
3. Cross-difference factoring with shared hypotenuses
4. Division algebra composition chains
5. Optimal dimension experiments
"""

import math
import itertools
import random
import time
from collections import defaultdict
from typing import List, Tuple, Optional, Dict

# ============================================================
# Core: Pythagorean k-Tuple Operations
# ============================================================

def find_pythagorean_5tuples(d_max: int) -> List[Tuple[int, ...]]:
    """Find all Pythagorean 5-tuples with hypotenuse ≤ d_max."""
    tuples = []
    for d in range(1, d_max + 1):
        d2 = d * d
        for a1 in range(0, d):
            r1 = d2 - a1*a1
            if r1 < 0:
                break
            for a2 in range(0, int(math.isqrt(r1)) + 1):
                r2 = r1 - a2*a2
                if r2 < 0:
                    break
                for a3 in range(0, int(math.isqrt(r2)) + 1):
                    r3 = r2 - a3*a3
                    if r3 < 0:
                        break
                    a4 = int(math.isqrt(r3))
                    if a4*a4 == r3:
                        tuples.append((a1, a2, a3, a4, d))
    return tuples

def find_pythagorean_ktuples(k: int, d: int) -> List[Tuple[int, ...]]:
    """Find Pythagorean k-tuples with hypotenuse d, via recursive search."""
    if k == 2:
        # Base: a^2 = d^2, so a = d
        return [(d,)]
    results = []
    d2 = d * d

    def search(remaining_k, remaining_sq, current):
        if remaining_k == 1:
            a = int(math.isqrt(remaining_sq))
            if a * a == remaining_sq:
                results.append(tuple(current + [a]))
            return
        max_a = int(math.isqrt(remaining_sq))
        for a in range(0, max_a + 1):
            search(remaining_k - 1, remaining_sq - a*a, current + [a])

    search(k - 1, d2, [])
    return results


# ============================================================
# Factor Extraction via Multi-Channel GCD
# ============================================================

def gcd_factor_extraction(N: int, tuples: List[Tuple[int, ...]], verbose=False) -> Optional[int]:
    """
    Use k-tuple GCD cascades to find a nontrivial factor of N.

    For each k-tuple (a₁,...,aₖ) with hypotenuse d:
      - Peel identity: (d - aᵢ)(d + aᵢ) = ∑_{j≠i} aⱼ²
      - Compute gcd(d ± aᵢ, N) for each channel i
    """
    for tup in tuples:
        *components, d = tup
        k = len(components)
        for i in range(k):
            ai = components[i]
            for sign in [-1, 1]:
                g = math.gcd(d + sign * ai, N)
                if 1 < g < N:
                    if verbose:
                        print(f"  Found factor {g} of {N} via channel {i}, d={d}, a={ai}, sign={sign}")
                    return g
    return None


def multi_channel_factor(N: int, d_max: int = 100, k_range=(3, 9), verbose=False) -> Dict:
    """
    Try factoring N using k-tuples of various dimensions.
    Returns a dict mapping k -> (factor, time, num_tuples).
    """
    results = {}
    for k in range(k_range[0], k_range[1] + 1):
        t0 = time.time()
        # Find k-tuples with hypotenuse related to N
        tuples = []
        for d in range(1, min(d_max, N)):
            ktuples = find_pythagorean_ktuples(k, d)
            tuples.extend(ktuples)

        factor = gcd_factor_extraction(N, [(t + (d,)) for d in range(1, min(d_max, N))
                                           for t in find_pythagorean_ktuples(k, d)], verbose=verbose)
        elapsed = time.time() - t0
        results[k] = {
            'factor': factor,
            'time': elapsed,
            'num_tuples': len(tuples)
        }
        if verbose:
            status = f"factor={factor}" if factor else "no factor"
            print(f"  k={k}: {status}, {len(tuples)} tuples, {elapsed:.4f}s")
    return results


# ============================================================
# Cross-Difference Factoring
# ============================================================

def cross_difference_factor(N: int, d: int) -> Optional[int]:
    """
    Find factors via cross-differences of 5-tuples sharing hypotenuse d.

    If (a₁,...,a₄,d) and (b₁,...,b₄,d), then:
    a₄² - b₄² = (b₁²-a₁²) + (b₂²-a₂²) + (b₃²-a₃²)
    ⟹ (a₄-b₄)(a₄+b₄) provides GCD opportunities.
    """
    tuples = find_pythagorean_ktuples(5, d)
    if len(tuples) < 2:
        return None

    for t1, t2 in itertools.combinations(tuples[:20], 2):  # limit combinations
        for i in range(4):
            diff = t1[i] - t2[i]
            summ = t1[i] + t2[i]
            if diff != 0:
                g = math.gcd(diff, N)
                if 1 < g < N:
                    return g
                g = math.gcd(summ, N)
                if 1 < g < N:
                    return g
    return None


# ============================================================
# Division Algebra Composition
# ============================================================

def brahmagupta_fibonacci(a, b, c, d):
    """Apply Brahmagupta-Fibonacci: (a²+b²)(c²+d²) = (ac-bd)² + (ad+bc)²"""
    return (a*c - b*d, a*d + b*c)


def euler_four_square(a, b):
    """Compose two 4-tuples via Euler's quaternion identity."""
    a1, a2, a3, a4 = a
    b1, b2, b3, b4 = b
    c1 = a1*b1 - a2*b2 - a3*b3 - a4*b4
    c2 = a1*b2 + a2*b1 + a3*b4 - a4*b3
    c3 = a1*b3 - a2*b4 + a3*b1 + a4*b2
    c4 = a1*b4 + a2*b3 - a3*b2 + a4*b1
    return (c1, c2, c3, c4)


def verify_composition(a, b):
    """Verify that Euler composition preserves sum-of-squares."""
    c = euler_four_square(a, b)
    norm_a = sum(x**2 for x in a)
    norm_b = sum(x**2 for x in b)
    norm_c = sum(x**2 for x in c)
    assert norm_c == norm_a * norm_b, f"Composition failed: {norm_a}*{norm_b} ≠ {norm_c}"
    return c


# ============================================================
# Optimal Dimension Experiment
# ============================================================

def optimal_dimension_experiment(N_values: List[int], k_range=(3, 9), d_max=50):
    """
    Experiment: For each N, try factoring with k-tuples of dimension k.
    Measure factor recovery rate and time per dimension.
    """
    print("\n" + "="*70)
    print("OPTIMAL DIMENSION EXPERIMENT")
    print("="*70)
    print(f"Testing N values: {len(N_values)} composites")
    print(f"Dimension range: k ∈ [{k_range[0]}, {k_range[1]}]")
    print(f"Max hypotenuse: d_max = {d_max}")
    print()

    stats = defaultdict(lambda: {'found': 0, 'total': 0, 'time': 0.0})

    for N in N_values:
        for k in range(k_range[0], k_range[1] + 1):
            t0 = time.time()
            # Simple approach: test a few hypotenuses
            found = False
            for d in range(2, min(d_max, N)):
                tuples = find_pythagorean_ktuples(k, d)
                for tup in tuples[:50]:  # limit per hypotenuse
                    *comps, = tup
                    for i, ai in enumerate(comps):
                        for sign in [-1, 1]:
                            g = math.gcd(d + sign * ai, N)
                            if 1 < g < N:
                                found = True
                                break
                        if found:
                            break
                    if found:
                        break
                if found:
                    break
            elapsed = time.time() - t0
            stats[k]['total'] += 1
            stats[k]['time'] += elapsed
            if found:
                stats[k]['found'] += 1

    print(f"{'k':>3} | {'Recovery %':>10} | {'Avg Time (s)':>12} | {'Efficiency':>10}")
    print("-" * 50)
    for k in range(k_range[0], k_range[1] + 1):
        s = stats[k]
        rate = 100 * s['found'] / max(1, s['total'])
        avg_time = s['time'] / max(1, s['total'])
        efficiency = rate / max(0.001, avg_time)  # recovery per second
        print(f"{k:>3} | {rate:>9.1f}% | {avg_time:>11.4f}s | {efficiency:>9.1f}")


# ============================================================
# Channel Utilization Analysis
# ============================================================

def channel_analysis(N_values: List[int], d_max=30):
    """Analyze which GCD channels most frequently find factors."""
    print("\n" + "="*70)
    print("CHANNEL UTILIZATION ANALYSIS (5-Tuples)")
    print("="*70)

    channel_hits = defaultdict(int)
    total_tests = 0

    for N in N_values:
        for d in range(2, min(d_max, N)):
            tuples = find_pythagorean_ktuples(5, d)
            for tup in tuples[:20]:
                total_tests += 1
                for i in range(4):
                    for sign_idx, sign in enumerate([-1, 1]):
                        g = math.gcd(d + sign * tup[i], N)
                        if 1 < g < N:
                            channel_hits[f"channel_{i}_{'minus' if sign == -1 else 'plus'}"] += 1

    print(f"\nTotal tuple-N pairs tested: {total_tests}")
    print(f"\n{'Channel':>25} | {'Hits':>6} | {'Rate':>8}")
    print("-" * 45)
    for ch, hits in sorted(channel_hits.items(), key=lambda x: -x[1]):
        rate = 100 * hits / max(1, total_tests)
        print(f"{ch:>25} | {hits:>6} | {rate:>6.2f}%")


# ============================================================
# Bridge Projection Demo
# ============================================================

def bridge_projection_demo():
    """Demonstrate the 6 possible 2D projections from a 5-tuple."""
    print("\n" + "="*70)
    print("5-TUPLE BRIDGE PROJECTION DEMO")
    print("="*70)

    # Example 5-tuple: 1² + 2² + 3² + 4² = 30 = not a perfect square
    # Try: 2² + 3² + 6² + 6² = 4+9+36+36 = 85 not square
    # 1² + 2² + 4² + 6² = 1+4+16+36 = 57 not square
    # Let's find a valid one
    tuples = find_pythagorean_5tuples(20)

    if not tuples:
        print("No 5-tuples found in range. Increase d_max.")
        return

    # Pick a nontrivial one
    for tup in tuples:
        if all(x > 0 for x in tup[:4]):
            a1, a2, a3, a4, d = tup
            print(f"\n5-tuple: ({a1}, {a2}, {a3}, {a4}, {d})")
            print(f"Verify: {a1}² + {a2}² + {a3}² + {a4}² = {a1**2 + a2**2 + a3**2 + a4**2} = {d}² = {d**2}")
            print(f"\nAll C(4,2) = 6 projections to pairs:")

            components = [a1, a2, a3, a4]
            names = ['a₁', 'a₂', 'a₃', 'a₄']
            bridge_count = 0

            for i, j in itertools.combinations(range(4), 2):
                ai, aj = components[i], components[j]
                sq_sum = ai**2 + aj**2
                e = int(math.isqrt(sq_sum))
                is_bridge = (e * e == sq_sum)
                status = f"✓ BRIDGE (e={e})" if is_bridge else "✗ no bridge"
                print(f"  ({names[i]}, {names[j]}) = ({ai}, {aj}): "
                      f"{ai}² + {aj}² = {sq_sum} {status}")
                if is_bridge:
                    bridge_count += 1

            print(f"\nBridges found: {bridge_count}/6")
            return

    print("No fully-positive 5-tuple found.")


# ============================================================
# Division Algebra Composition Demo
# ============================================================

def composition_demo():
    """Demonstrate the Brahmagupta-Fibonacci and Euler composition chains."""
    print("\n" + "="*70)
    print("DIVISION ALGEBRA COMPOSITION DEMO")
    print("="*70)

    # Brahmagupta-Fibonacci (ℂ)
    print("\n--- Brahmagupta-Fibonacci Identity (ℂ, dim 2) ---")
    a, b, c, d = 3, 4, 5, 12
    p1, p2 = a*a + b*b, c*c + d*d
    r1, r2 = brahmagupta_fibonacci(a, b, c, d)
    print(f"({a}² + {b}²)({c}² + {d}²) = {p1} × {p2} = {p1*p2}")
    print(f"= ({r1})² + ({r2})² = {r1**2 + r2**2}")
    assert r1**2 + r2**2 == p1 * p2

    # Euler Four-Square (ℍ)
    print("\n--- Euler Four-Square Identity (ℍ, dim 4) ---")
    a_vec = (1, 2, 3, 4)
    b_vec = (5, 6, 7, 8)
    c_vec = verify_composition(a_vec, b_vec)
    na = sum(x**2 for x in a_vec)
    nb = sum(x**2 for x in b_vec)
    nc = sum(x**2 for x in c_vec)
    print(f"a = {a_vec}, |a|² = {na}")
    print(f"b = {b_vec}, |b|² = {nb}")
    print(f"c = a·b = {c_vec}, |c|² = {nc}")
    print(f"Verify: {na} × {nb} = {na*nb} = {nc} ✓")


# ============================================================
# Lattice Connection Sketch
# ============================================================

def lattice_connection_demo():
    """
    Sketch of how LLL might find short vectors on spheres
    corresponding to factor-revealing tuples.
    """
    print("\n" + "="*70)
    print("LATTICE ALGORITHM CONNECTION (Conceptual)")
    print("="*70)

    N = 91  # = 7 × 13
    print(f"\nTarget: N = {N}")
    print(f"True factors: 7 × 13")

    # Construct a lattice whose short vectors encode Pythagorean 5-tuples
    # related to N. The idea: find (a₁,...,a₄,d) with a₁²+...+a₄²=d²
    # such that gcd(d ± aᵢ, N) is nontrivial.

    # Simple enumeration (in practice, LLL would be used for large N)
    print("\nSearching for factor-revealing 5-tuples...")
    for d in range(2, 50):
        tuples = find_pythagorean_ktuples(5, d)
        for tup in tuples:
            for i in range(4):
                for sign in [-1, 1]:
                    g = math.gcd(d + sign * tup[i], N)
                    if 1 < g < N:
                        print(f"  5-tuple {tup}, d={d}: gcd({d}{'+' if sign==1 else '-'}{tup[i]}, {N}) = {g}")
                        print(f"  → Factor found: {N} = {g} × {N//g}")
                        return
    print("  No factor found in range.")


# ============================================================
# Main: Run All Demos
# ============================================================

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║  Higher-Dimensional Quadruple Division Factoring: Experiments   ║")
    print("╚══════════════════════════════════════════════════════════════════╝")

    # 1. Bridge Projection Demo
    bridge_projection_demo()

    # 2. Composition Demo
    composition_demo()

    # 3. Lattice Connection
    lattice_connection_demo()

    # 4. Optimal Dimension Experiment (small scale)
    composites = [n for n in range(6, 200) if not all(n % p != 0 for p in range(2, n))]
    composites = [n for n in composites if n > 1 and not all(
        n % i != 0 for i in range(2, int(math.isqrt(n)) + 1)
    )]
    # Filter to actual composites
    def is_composite(n):
        if n < 4:
            return False
        for i in range(2, int(math.isqrt(n)) + 1):
            if n % i == 0:
                return True
        return False
    composites = [n for n in range(6, 200) if is_composite(n)]

    optimal_dimension_experiment(composites[:30], k_range=(3, 7), d_max=20)

    # 5. Channel Analysis
    channel_analysis(composites[:20], d_max=15)

    print("\n" + "="*70)
    print("ALL DEMOS COMPLETE")
    print("="*70)

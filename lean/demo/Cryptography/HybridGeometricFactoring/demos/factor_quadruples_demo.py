#!/usr/bin/env python3
"""
Factor Quadruples and Geometric Factoring — Interactive Demonstration

This script demonstrates the core ideas of Hybrid Geometric Factoring:
1. Enumerating factor quadruples and computing their GCD structure
2. Building the "quadruple graph" showing shared-factor links
3. The divisor hyperbola visualization
4. Fermat's method as a walk along the hyperbola
5. The cross-ratio decomposition of factor quadruples

Usage:
    python factor_quadruples_demo.py [--n VALUE]
"""

import math
import sys
from collections import defaultdict
from itertools import combinations


def divisors(n):
    """Return sorted list of divisors of n."""
    divs = []
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            divs.append(i)
            if i != n // i:
                divs.append(n // i)
    return sorted(divs)


def factor_pairs(n):
    """Return all ordered factor pairs (a, b) with a * b = n, a <= b."""
    pairs = []
    for d in divisors(n):
        if d <= n // d:
            pairs.append((d, n // d))
    return pairs


def factor_quadruples(n):
    """Return all factor quadruples (a, b, c, d) with ab = cd = n."""
    pairs = factor_pairs(n)
    quads = []
    for p1 in pairs:
        for p2 in pairs:
            quads.append((p1[0], p1[1], p2[0], p2[1]))
    return quads


def gcd_structure(n):
    """Analyze the GCD structure of all factor quadruples."""
    pairs = factor_pairs(n)
    print(f"\n{'='*60}")
    print(f"  GCD Structure of Factor Quadruples for n = {n}")
    print(f"{'='*60}")
    print(f"\nFactor pairs of {n}: {pairs}")
    print(f"Number of pairs: {len(pairs)}")
    print(f"Number of quadruples: {len(pairs)**2}")

    print(f"\n  Nontrivial GCD links:")
    print(f"  {'Pair 1':<15} {'Pair 2':<15} {'gcd(a,c)':<10} {'Factor?'}")
    print(f"  {'-'*55}")

    nontrivial_count = 0
    for p1, p2 in combinations(pairs, 2):
        g = math.gcd(p1[0], p2[0])
        is_factor = 1 < g < n
        if g > 1:
            nontrivial_count += 1
            marker = f"✓ factor = {g}" if is_factor else ""
            print(f"  ({p1[0]:>4},{p1[1]:>4})   ({p2[0]:>4},{p2[1]:>4})   {g:<10} {marker}")

    print(f"\n  Nontrivial GCD links: {nontrivial_count} / {len(list(combinations(pairs, 2)))}")
    return pairs


def cross_ratio_decomposition(n):
    """Show the cross-ratio decomposition for all distinct pair combinations."""
    pairs = factor_pairs(n)
    print(f"\n{'='*60}")
    print(f"  Cross-Ratio Decomposition for n = {n}")
    print(f"{'='*60}")

    for p1, p2 in combinations(pairs, 2):
        a, b = p1
        c, d = p2
        g = math.gcd(a, c)
        alpha = a // g
        gamma = c // g
        assert math.gcd(alpha, gamma) == 1, "Cross-ratio coprimality failed!"
        print(f"\n  ({a},{b}) × ({c},{d}):")
        print(f"    g = gcd({a},{c}) = {g}")
        print(f"    α = {a}/{g} = {alpha},  γ = {c}/{g} = {gamma}")
        print(f"    gcd(α,γ) = gcd({alpha},{gamma}) = {math.gcd(alpha, gamma)} ✓ (coprime)")
        print(f"    n = {g} · {alpha} · {gamma} · {b // gamma if gamma and b % gamma == 0 else '?'}")


def quadruple_graph(n):
    """Build and display the factor quadruple graph."""
    pairs = factor_pairs(n)
    print(f"\n{'='*60}")
    print(f"  Factor Quadruple Graph for n = {n}")
    print(f"{'='*60}")

    # Build adjacency
    adj = defaultdict(set)
    for i, p1 in enumerate(pairs):
        for j, p2 in enumerate(pairs):
            if i < j and math.gcd(p1[0], p2[0]) > 1:
                adj[i].add(j)
                adj[j].add(i)

    # Find connected components
    visited = set()
    components = []
    for i in range(len(pairs)):
        if i not in visited:
            comp = []
            stack = [i]
            while stack:
                node = stack.pop()
                if node not in visited:
                    visited.add(node)
                    comp.append(node)
                    stack.extend(adj[node] - visited)
            components.append(comp)

    print(f"\n  Vertices (factor pairs): {len(pairs)}")
    print(f"  Edges (shared factor links): {sum(len(v) for v in adj.values()) // 2}")
    print(f"  Connected components: {len(components)}")

    for k, comp in enumerate(components):
        comp_pairs = [pairs[i] for i in comp]
        print(f"\n  Component {k+1}: {comp_pairs}")
        # Find which primes link this component
        primes_here = set()
        for i in comp:
            for p in range(2, pairs[i][0] + 1):
                if pairs[i][0] % p == 0 and all(p % q != 0 for q in range(2, p)):
                    primes_here.add(p)
        if primes_here:
            print(f"    Linking primes: {sorted(primes_here)}")


def divisor_hyperbola(n):
    """Display the divisor hyperbola xy = n."""
    divs = divisors(n)
    sqrt_n = math.isqrt(n)
    print(f"\n{'='*60}")
    print(f"  Divisor Hyperbola for n = {n}")
    print(f"{'='*60}")
    print(f"\n  √n ≈ {math.sqrt(n):.2f}")
    print(f"\n  {'d':<8} {'n/d':<8} {'d + n/d':<10} {'|d - n/d|':<10} {'AM-GM gap'}")
    print(f"  {'-'*48}")

    min_sum = float('inf')
    for d in divs:
        nd = n // d
        s = d + nd
        gap = abs(d - nd)
        am_gm_gap = s - 2 * math.sqrt(n)
        if s < min_sum:
            min_sum = s
        marker = " ← closest to √n" if d <= sqrt_n <= nd and d * nd == n else ""
        print(f"  {d:<8} {nd:<8} {s:<10} {gap:<10} {am_gm_gap:.2f}{marker}")

    print(f"\n  Minimum sum: {min_sum} (AM-GM bound: {2*math.sqrt(n):.2f})")


def fermat_method(n, verbose=True):
    """Demonstrate Fermat's factoring method as a walk along the hyperbola."""
    if verbose:
        print(f"\n{'='*60}")
        print(f"  Fermat's Method for n = {n}")
        print(f"{'='*60}")

    x = math.isqrt(n)
    if x * x < n:
        x += 1

    steps = 0
    while True:
        y2 = x * x - n
        y = math.isqrt(y2)
        if y * y == y2:
            a, b = x - y, x + y
            if verbose:
                print(f"\n  Found: {n} = {a} × {b}")
                print(f"  x = {x}, y = {y}")
                print(f"  Steps: {steps}")
                print(f"  n = x² - y² = {x}² - {y}² = {x*x} - {y*y} = {n}")
            return a, b, steps
        steps += 1
        x += 1
        if steps > 10000:
            if verbose:
                print(f"  Exceeded 10000 steps, aborting.")
            return None, None, steps


def smooth_analysis(n, B=20):
    """Analyze smooth numbers among orbit elements."""
    print(f"\n{'='*60}")
    print(f"  Smooth Number Analysis for n = {n}, B = {B}")
    print(f"{'='*60}")

    primes = [p for p in range(2, B + 1) if all(p % i != 0 for i in range(2, p))]
    print(f"\n  Factor base (primes ≤ {B}): {primes}")

    def is_smooth(m, bound):
        if m <= 1:
            return m == 1
        for p in primes:
            while m % p == 0:
                m //= p
        return m == 1

    # Test squaring orbit
    x = 2
    orbit = [x]
    for _ in range(30):
        x = (x * x) % n
        orbit.append(x)

    print(f"\n  Squaring orbit (x₀ = 2):")
    smooth_count = 0
    for k, val in enumerate(orbit[:20]):
        smooth = is_smooth(val, B)
        if smooth:
            smooth_count += 1
        marker = " ← B-smooth!" if smooth else ""
        print(f"    x^(2^{k}) mod {n} = {val}{marker}")

    print(f"\n  Smooth elements: {smooth_count} / {min(len(orbit), 20)}")
    print(f"  Smooth ratio: {smooth_count / min(len(orbit), 20):.2%}")


def brahmagupta_fibonacci_demo():
    """Demonstrate the Brahmagupta–Fibonacci identity for factoring."""
    print(f"\n{'='*60}")
    print(f"  Brahmagupta–Fibonacci Identity and Factoring")
    print(f"{'='*60}")

    # 65 = 1² + 8² = 4² + 7²
    n = 65
    x1, y1 = 1, 8
    x2, y2 = 4, 7

    print(f"\n  {n} = {x1}² + {y1}² = {x1**2} + {y1**2}")
    print(f"  {n} = {x2}² + {y2}² = {x2**2} + {y2**2}")
    print(f"\n  Two representations ⇒ {n} is composite!")

    g1 = math.gcd(x1 * x2 + y1 * y2, n)
    g2 = math.gcd(x1 * y2 - y1 * x2, n)

    print(f"\n  gcd({x1}·{x2} + {y1}·{y2}, {n}) = gcd({x1*x2 + y1*y2}, {n}) = {g1}")
    print(f"  gcd({x1}·{y2} - {y1}·{x2}, {n}) = gcd({x1*y2 - y1*x2}, {n}) = {g2}")
    print(f"\n  Factors: {n} = {g1} × {n // g1}")

    # More examples
    print(f"\n  --- More examples ---")
    test_cases = [
        (325, [(1, 18), (6, 17)]),
        (85, [(2, 9), (6, 7)]),
    ]
    for m, reps in test_cases:
        (a1, b1), (a2, b2) = reps
        assert a1**2 + b1**2 == m and a2**2 + b2**2 == m
        g = math.gcd(a1*a2 + b1*b2, m)
        print(f"\n  {m} = {a1}² + {b1}² = {a2}² + {b2}²")
        print(f"  gcd({a1*a2 + b1*b2}, {m}) = {g},  {m} = {g} × {m // g}")


def main():
    n = 2310  # 2 × 3 × 5 × 7 × 11 — highly composite, many quadruples

    if len(sys.argv) > 1 and sys.argv[1] == "--n":
        n = int(sys.argv[2])

    print(f"╔{'═'*58}╗")
    print(f"║  Hybrid Geometric Factoring — Factor Quadruples Demo     ║")
    print(f"║  n = {n:<52} ║")
    print(f"╚{'═'*58}╝")

    # Part 1: Factor pairs and GCD structure
    gcd_structure(n)

    # Part 2: Cross-ratio decomposition (for smaller n)
    if n <= 200:
        cross_ratio_decomposition(n)

    # Part 3: Quadruple graph
    quadruple_graph(n)

    # Part 4: Divisor hyperbola
    divisor_hyperbola(n)

    # Part 5: Fermat's method
    test_n = 10007 * 10009  # Product of two close primes
    fermat_method(test_n)

    # Part 6: Smooth analysis
    smooth_analysis(n * 7 + 1 if n % 2 == 0 else n)

    # Part 7: Brahmagupta–Fibonacci
    brahmagupta_fibonacci_demo()

    print(f"\n{'='*60}")
    print(f"  Demo complete!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Divisor Hyperbola Explorer: xy = n

Demonstrates the geometric structure of integer factorization through
the rectangular hyperbola xy = n. Lattice points on this curve correspond
exactly to divisor pairs of n.

Usage:
    python demo_divisor_hyperbola.py [n]
    python demo_divisor_hyperbola.py          # defaults to n = 210
"""

import sys
from math import isqrt, gcd
from itertools import product as cartprod
from typing import List, Tuple, Dict

# ─── Core Divisor Hyperbola Functions ────────────────────────────────────────

def divisors(n: int) -> List[int]:
    """Return sorted list of all positive divisors of n."""
    divs = []
    for d in range(1, isqrt(n) + 1):
        if n % d == 0:
            divs.append(d)
            if d != n // d:
                divs.append(n // d)
    return sorted(divs)


def lattice_points(n: int) -> List[Tuple[int, int]]:
    """Return all lattice points (d, n/d) on the hyperbola xy = n."""
    return [(d, n // d) for d in divisors(n)]


def dirichlet_split(n: int) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
    """Split divisor pairs at √n (Dirichlet's hyperbola method).
    Returns (below_sqrt, above_sqrt) where 'below' has d ≤ √n."""
    s = isqrt(n)
    below = [(d, n // d) for d in divisors(n) if d <= s]
    above = [(d, n // d) for d in divisors(n) if d > s]
    return below, above


def tau(n: int) -> int:
    """Divisor counting function τ(n) = number of divisors."""
    return len(divisors(n))


def sigma(n: int, k: int = 1) -> int:
    """Divisor sum function σ_k(n) = sum of d^k over divisors d of n."""
    return sum(d ** k for d in divisors(n))


def factorization(n: int) -> Dict[int, int]:
    """Return prime factorization as {prime: exponent}."""
    factors = {}
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            factors[d] = factors.get(d, 0) + 1
            temp //= d
        d += 1
    if temp > 1:
        factors[temp] = factors.get(temp, 0) + 1
    return factors


def tau_from_factorization(n: int) -> int:
    """Compute τ(n) from prime factorization: τ(n) = ∏(eᵢ + 1)."""
    result = 1
    for e in factorization(n).values():
        result *= (e + 1)
    return result


# ─── Geometric Analysis ─────────────────────────────────────────────────────

def rectangle_areas(n: int) -> List[Tuple[int, int, int]]:
    """For each divisor pair, compute the rectangle area (always n).
    Returns (d, n/d, d*(n/d))."""
    return [(d, n // d, d * (n // d)) for d in divisors(n)]


def aspect_ratios(n: int) -> List[Tuple[int, int, float]]:
    """Compute aspect ratios d/(n/d) for each divisor pair.
    Near-square pairs (ratio ≈ 1) are closest to √n."""
    pts = []
    for d in divisors(n):
        q = n // d
        ratio = d / q if q > 0 else float('inf')
        pts.append((d, q, ratio))
    return pts


def nearest_square_divisor(n: int) -> Tuple[int, int]:
    """Find the divisor pair closest to (√n, √n)."""
    s = isqrt(n)
    best = None
    best_gap = float('inf')
    for d in divisors(n):
        gap = abs(d - n // d)
        if gap < best_gap:
            best_gap = gap
            best = (d, n // d)
    return best


# ─── Coprimality and Multiplicativity ────────────────────────────────────────

def verify_multiplicativity(m: int, n: int) -> bool:
    """Verify τ(mn) = τ(m)·τ(n) when gcd(m,n) = 1."""
    if gcd(m, n) != 1:
        return False  # Only valid for coprime m, n
    return tau(m * n) == tau(m) * tau(n)


def coprime_lattice_bijection(m: int, n: int) -> List[Tuple[Tuple[int,int], Tuple[int,int], Tuple[int,int]]]:
    """When gcd(m,n)=1, show the bijection between divisor pairs of mn
    and pairs of divisor pairs of m and n.

    For each d | mn with gcd(m,n)=1, we can uniquely write d = d_m · d_n
    where d_m | m and d_n | n. Returns triples (d_mn_pair, d_m_pair, d_n_pair)."""
    if gcd(m, n) != 1:
        raise ValueError("m and n must be coprime")

    result = []
    dm = divisors(m)
    dn = divisors(n)
    for d_m in dm:
        for d_n in dn:
            d = d_m * d_n
            mn = m * n
            result.append(((d, mn // d), (d_m, m // d_m), (d_n, n // d_n)))
    return result


# ─── Hyperbolic Geometry Metrics ──────────────────────────────────────────────

def hyperbolic_distance_from_diagonal(d: int, n: int) -> float:
    """Compute the (log-space) distance of point (d, n/d) from the diagonal y=x.
    In log coordinates, the hyperbola becomes a line, and this measures
    |log(d) - log(n/d)| = |2·log(d) - log(n)|."""
    import math
    if d <= 0 or n <= 0:
        return float('inf')
    return abs(2 * math.log(d) - math.log(n))


def log_lattice_points(n: int) -> List[Tuple[float, float]]:
    """Map lattice points to log-log space where the hyperbola becomes linear.
    The hyperbola xy = n becomes log(x) + log(y) = log(n), a line of slope -1."""
    import math
    return [(math.log(d), math.log(n / d)) for d in divisors(n)]


# ─── AI-Exploitable Features ─────────────────────────────────────────────────

def feature_vector(n: int) -> Dict[str, float]:
    """Extract geometric features of the divisor hyperbola for ML models.

    These features capture the 'shape' of the factorization in ways that
    neural networks can learn patterns from."""
    import math

    divs = divisors(n)
    num_divs = len(divs)
    sqrt_n = math.sqrt(n)

    # Gap statistics
    gaps = [divs[i+1] - divs[i] for i in range(len(divs) - 1)]
    log_gaps = [math.log(divs[i+1]) - math.log(divs[i]) for i in range(len(divs) - 1)]

    # Nearest-square gap
    ns = nearest_square_divisor(n)
    square_gap = abs(ns[0] - ns[1]) / sqrt_n if sqrt_n > 0 else 0

    return {
        'n': n,
        'num_divisors': num_divs,
        'log_n': math.log(n),
        'sqrt_n': sqrt_n,
        'max_gap': max(gaps) if gaps else 0,
        'min_gap': min(gaps) if gaps else 0,
        'mean_gap': sum(gaps) / len(gaps) if gaps else 0,
        'max_log_gap': max(log_gaps) if log_gaps else 0,
        'mean_log_gap': sum(log_gaps) / len(log_gaps) if log_gaps else 0,
        'square_gap_normalized': square_gap,
        'smallest_prime_factor': divs[1] if num_divs > 1 else n,
        'largest_proper_divisor': divs[-2] if num_divs > 1 else 1,
        'divisor_density': num_divs / sqrt_n if sqrt_n > 0 else 0,
    }


# ─── Display Functions ──────────────────────────────────────────────────────

def print_hyperbola_analysis(n: int):
    """Complete analysis of the divisor hyperbola xy = n."""
    print(f"\n{'='*70}")
    print(f"  THE DIVISOR HYPERBOLA: xy = {n}")
    print(f"{'='*70}")

    # Factorization
    facts = factorization(n)
    fact_str = " × ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(facts.items()))
    print(f"\n  Prime factorization: {n} = {fact_str}")
    print(f"  τ({n}) = {' × '.join(f'({e}+1)' for e in facts.values())} = {tau(n)}")

    # Lattice points
    pts = lattice_points(n)
    print(f"\n  Lattice points on xy = {n} ({len(pts)} points):")
    print(f"  {'d':>6} {'n/d':>6} {'d × (n/d)':>10} {'aspect':>8}")
    print(f"  {'-'*6} {'-'*6} {'-'*10} {'-'*8}")
    for d, q in pts:
        ratio = d / q if q > 0 else float('inf')
        print(f"  {d:>6} {q:>6} {d*q:>10} {ratio:>8.4f}")

    # Dirichlet split
    below, above = dirichlet_split(n)
    s = isqrt(n)
    print(f"\n  Dirichlet split at √{n} ≈ {s}:")
    print(f"    Below √n: {[(d, q) for d, q in below]}")
    print(f"    Above √n: {[(d, q) for d, q in above]}")
    print(f"    Count check: {len(below)} + {len(above)} = {len(pts)} ✓" if len(below) + len(above) == len(pts) else "")

    # Nearest square
    ns = nearest_square_divisor(n)
    print(f"\n  Nearest-square divisor pair: {ns} (gap = {abs(ns[0]-ns[1])})")

    # Rectangle areas
    print(f"\n  Rectangle area invariant: all d × (n/d) = {n} ✓")

    # Multiplicativity demo
    if len(facts) >= 2:
        primes = sorted(facts.keys())
        m = primes[0] ** facts[primes[0]]
        rest = n // m
        if gcd(m, rest) == 1:
            print(f"\n  Multiplicativity: τ({m} × {rest}) = τ({m}) × τ({rest})")
            print(f"    = {tau(m)} × {tau(rest)} = {tau(m)*tau(rest)} ✓")

    # Feature vector
    fv = feature_vector(n)
    print(f"\n  AI Feature Vector:")
    for k, v in fv.items():
        if k != 'n':
            print(f"    {k:>25}: {v:.4f}" if isinstance(v, float) else f"    {k:>25}: {v}")

    print(f"\n{'='*70}\n")


def print_comparative_analysis(numbers: List[int]):
    """Compare the hyperbola structure across multiple numbers."""
    print(f"\n{'='*70}")
    print(f"  COMPARATIVE HYPERBOLA ANALYSIS")
    print(f"{'='*70}")
    print(f"\n  {'n':>8} {'τ(n)':>5} {'factorization':>20} {'nearest-sq pair':>18} {'density':>8}")
    print(f"  {'-'*8} {'-'*5} {'-'*20} {'-'*18} {'-'*8}")

    import math
    for n in numbers:
        facts = factorization(n)
        fact_str = "×".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(facts.items()))
        ns = nearest_square_divisor(n)
        density = tau(n) / math.sqrt(n)
        print(f"  {n:>8} {tau(n):>5} {fact_str:>20} {str(ns):>18} {density:>8.4f}")


def run_experiments():
    """Run a battery of experiments collecting data about divisor hyperbolas."""
    print(f"\n{'='*70}")
    print(f"  EXPERIMENT: DIVISOR DENSITY VS. FACTORIZATION STRUCTURE")
    print(f"{'='*70}")

    import math

    # Experiment 1: Highly composite numbers
    highly_composite = [1, 2, 4, 6, 12, 24, 36, 48, 60, 120, 180, 240, 360, 720, 840, 1260, 1680, 2520]
    print(f"\n  Highly Composite Numbers:")
    print(f"  {'n':>6} {'τ(n)':>5} {'τ/√n':>8} {'τ/log(n)':>8}")
    for n in highly_composite:
        if n <= 1:
            continue
        t = tau(n)
        print(f"  {n:>6} {t:>5} {t/math.sqrt(n):>8.4f} {t/math.log(n):>8.4f}")

    # Experiment 2: Primorials
    print(f"\n  Primorials (products of first k primes):")
    primorials = [2, 6, 30, 210, 2310, 30030]
    for n in primorials:
        facts = factorization(n)
        k = len(facts)
        t = tau(n)
        print(f"  P({k}) = {n:>6}, τ = {t:>4}, 2^{k} = {2**k:>4}, ratio τ/2^k = {t/(2**k):.2f}")

    # Experiment 3: Gap distribution
    print(f"\n  Divisor Gap Analysis for n = 210:")
    divs = divisors(210)
    gaps = [divs[i+1] - divs[i] for i in range(len(divs)-1)]
    log_ratios = [divs[i+1]/divs[i] for i in range(len(divs)-1)]
    for i in range(len(gaps)):
        print(f"    {divs[i]:>4} → {divs[i+1]:>4}: gap = {gaps[i]:>3}, ratio = {log_ratios[i]:.4f}")

    # Experiment 4: Hyperbola curvature at different points
    print(f"\n  Hyperbola Curvature at Divisor Points (n = 210):")
    print(f"  The curvature κ of xy = n at point (d, n/d) is:")
    print(f"  κ = n / (d² + (n/d)²)^(3/2)")
    for d in divisors(210):
        q = 210 // d
        curvature = 210 / (d**2 + q**2)**1.5
        print(f"    ({d:>3}, {q:>3}): κ = {curvature:.6f}")


# ─── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 210

    print_hyperbola_analysis(n)

    # Comparative analysis
    print_comparative_analysis([30, 60, 105, 210, 420, 840, 1260, 2310])

    # Run experiments
    run_experiments()

    # Special: show coprime bijection for 210 = 6 × 35
    if n == 210:
        print(f"\n{'='*70}")
        print(f"  COPRIME BIJECTION: 210 = 6 × 35, gcd(6,35) = {gcd(6,35)}")
        print(f"{'='*70}")
        bij = coprime_lattice_bijection(6, 35)
        print(f"  τ(6)={tau(6)}, τ(35)={tau(35)}, τ(210)={tau(210)}")
        print(f"  {tau(6)} × {tau(35)} = {tau(6)*tau(35)} = {tau(210)} ✓")
        print(f"\n  {'d|210':>12} {'d_6|6':>10} {'d_35|35':>10}")
        for (d_mn, _), (d_m, _), (d_n, _) in sorted(bij):
            print(f"  ({d_mn:>3}, {210//d_mn:>3})   ({d_m:>2}, {6//d_m:>2})   ({d_n:>2}, {35//d_n:>2})")

    print("\nDone. All experiments complete.")

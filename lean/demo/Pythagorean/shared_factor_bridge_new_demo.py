#!/usr/bin/env python3
"""
The Shared Factor Bridge: Interactive Demos for Pythagorean Quadruples and Integer Factoring

This module demonstrates the key theorems from the Shared Factor Bridge framework:
1. Three-Channel Factoring Framework
2. GCD Cascade across multiple channels and representations
3. Higher-Dimensional Extensions (quintuples)
4. Inner Product Geometry of representations
5. Factor Orbit Reduction
6. Pell Connection
7. Full Channel Product
"""

from math import gcd, isqrt, sqrt
from itertools import combinations
from collections import defaultdict
import json


def find_quadruples(d, max_a=None):
    """Find all Pythagorean quadruples (a,b,c,d) with a² + b² + c² = d²."""
    if max_a is None:
        max_a = d
    quads = []
    d2 = d * d
    for a in range(0, min(d, max_a) + 1):
        a2 = a * a
        for b in range(a, d):
            b2 = b * b
            rem = d2 - a2 - b2
            if rem < 0:
                break
            c = isqrt(rem)
            if c >= b and c * c == rem:
                quads.append((a, b, c, d))
    return quads


def three_channels(a, b, c, d):
    """Compute the three factoring channels for a quadruple."""
    ch1 = a * a + b * b  # = (d-c)(d+c)
    ch2 = a * a + c * c  # = (d-b)(d+b)
    ch3 = b * b + c * c  # = (d-a)(d+a)
    return ch1, ch2, ch3


def channel_factors(a, b, c, d):
    """Return the left and right factors for each channel."""
    return {
        'Channel 1': {'left': d - c, 'right': d + c, 'value': a**2 + b**2},
        'Channel 2': {'left': d - b, 'right': d + b, 'value': a**2 + c**2},
        'Channel 3': {'left': d - a, 'right': d + a, 'value': b**2 + c**2},
    }


def gcd_cascade(quads):
    """Perform GCD cascade across multiple quadruples with the same d."""
    if len(quads) < 2:
        return {}
    d = quads[0][3]
    results = {}
    for i, q1 in enumerate(quads):
        for j, q2 in enumerate(quads):
            if j <= i:
                continue
            a1, b1, c1, _ = q1
            a2, b2, c2, _ = q2
            # Cross-channel GCDs
            g1 = gcd(d - c1, d - c2)
            g2 = gcd(d + c1, d + c2)
            g3 = gcd(d - c1, d + c2)
            g4 = gcd(d + c1, d - c2)
            results[f'Q{i+1}-Q{j+1}'] = {
                'gcd(d-c1, d-c2)': g1,
                'gcd(d+c1, d+c2)': g2,
                'gcd(d-c1, d+c2)': g3,
                'gcd(d+c1, d-c2)': g4,
                'c2-c1': c2 - c1,
                'factors_of_d_found': [g for g in [g1, g2, g3, g4]
                                       if 1 < g < d and d % g == 0]
            }
    return results


def full_channel_product(a, b, c, d):
    """Verify the Full Channel Product theorem."""
    lhs = (d-a)*(d+a) * (d-b)*(d+b) * (d-c)*(d+c)
    rhs = (b**2+c**2) * (a**2+c**2) * (a**2+b**2)
    return lhs, rhs, lhs == rhs


def inner_product_analysis(quads):
    """Analyze inner products between representations."""
    if len(quads) < 2:
        return []
    d = quads[0][3]
    results = []
    for i, q1 in enumerate(quads):
        for j, q2 in enumerate(quads):
            if j <= i:
                continue
            a1, b1, c1, _ = q1
            a2, b2, c2, _ = q2
            ip = a1*a2 + b1*b2 + c1*c2
            diff_norm = (a1-a2)**2 + (b1-b2)**2 + (c1-c2)**2
            results.append({
                'Q1': q1, 'Q2': q2,
                'inner_product': ip,
                'inner_product/d²': ip / (d*d),
                'diff_norm': diff_norm,
                'diff_norm_check': diff_norm == 2*d*d - 2*ip,
                'cauchy_schwarz_check': ip**2 <= d**4
            })
    return results


def find_quintuples(e, max_count=20):
    """Find Pythagorean quintuples (a,b,c,d,e) with a²+b²+c²+d² = e²."""
    quints = []
    e2 = e * e
    for a in range(0, e):
        if len(quints) >= max_count:
            break
        a2 = a * a
        for b in range(a, e):
            b2 = b * b
            if a2 + b2 >= e2:
                break
            for c in range(b, e):
                c2 = c * c
                rem = e2 - a2 - b2 - c2
                if rem < 0:
                    break
                dd = isqrt(rem)
                if dd >= c and dd * dd == rem:
                    quints.append((a, b, c, dd, e))
                    if len(quints) >= max_count:
                        break
    return quints


def six_channels_quintuple(a, b, c, d, e):
    """Compute six pair channels for a quintuple."""
    channels = {
        'Ch(a,b)': c**2 + d**2,   # e² - a² - b²
        'Ch(a,c)': b**2 + d**2,
        'Ch(a,d)': b**2 + c**2,
        'Ch(b,c)': a**2 + d**2,
        'Ch(b,d)': a**2 + c**2,
        'Ch(c,d)': a**2 + b**2,
    }
    ch_sum = sum(channels.values())
    return channels, ch_sum, ch_sum == 3 * e * e


def pell_quadruples(max_n=10):
    """Generate Pythagorean quadruples from Pell equation d²-2a²=1."""
    # Pell solutions: (d,a) via recurrence d_{n+1}=3d_n+4a_n, a_{n+1}=2d_n+3a_n
    d, a = 1, 0
    results = []
    for _ in range(max_n):
        d, a = 3*d + 4*a, 2*d + 3*a
        if d*d - 2*a*a == 1:
            results.append({
                'quadruple': (a, a, 1, d),
                'd': d, 'a': a,
                'verification': a**2 + a**2 + 1 == d**2,
                'pell_check': d**2 - 2*a**2 == 1
            })
    return results


def factor_extraction_demo(d):
    """Demonstrate factor extraction from quadruples of d."""
    quads = find_quadruples(d)
    print(f"\n{'='*70}")
    print(f"FACTOR EXTRACTION DEMO: d = {d}")
    print(f"{'='*70}")

    # Known factorization
    factors = []
    n = d
    for p in range(2, isqrt(d) + 1):
        while n % p == 0:
            factors.append(p)
            n //= p
    if n > 1:
        factors.append(n)
    print(f"True factorization: {d} = {'×'.join(map(str, factors))}")
    print(f"Number of quadruples found: {len(quads)}")

    if not quads:
        print("No quadruples found!")
        return

    # Analyze each quadruple
    factors_found = set()
    for i, (a, b, c, d_val) in enumerate(quads):
        cf = channel_factors(a, b, c, d_val)
        print(f"\nQuadruple {i+1}: ({a}, {b}, {c}, {d_val})")

        for name, info in cf.items():
            L, R, V = info['left'], info['right'], info['value']
            g = gcd(L, R)
            print(f"  {name}: ({L})×({R}) = {V}")
            if g > 1:
                print(f"    → gcd({L}, {R}) = {g}", end="")
                if d_val % g == 0 and g < d_val:
                    print(f" → FACTOR of {d_val} FOUND: {g}!")
                    factors_found.add(g)
                elif d_val % g == 0:
                    print(f" (= d itself)")
                else:
                    print(f" (divides 2d = {2*d_val})")

    # Full Channel Product verification
    a, b, c, _ = quads[0]
    lhs, rhs, ok = full_channel_product(a, b, c, d)
    print(f"\n  Full Channel Product: {lhs} = {rhs} → {'✓' if ok else '✗'}")

    # GCD Cascade
    if len(quads) >= 2:
        print(f"\nGCD CASCADE (across {len(quads)} quadruples):")
        cascade = gcd_cascade(quads)
        for key, info in cascade.items():
            if info['factors_of_d_found']:
                print(f"  {key}: Found factors: {info['factors_of_d_found']}")
                factors_found.update(info['factors_of_d_found'])

    # Inner product analysis
    if len(quads) >= 2:
        print(f"\nINNER PRODUCT ANALYSIS:")
        ip_results = inner_product_analysis(quads[:5])  # Limit to first 5
        for r in ip_results:
            print(f"  ⟨{r['Q1'][:3]}, {r['Q2'][:3]}⟩ = {r['inner_product']}, "
                  f"cos θ = {r['inner_product/d²']:.4f}, "
                  f"‖diff‖² = {r['diff_norm']}")

    if factors_found:
        print(f"\n★ FACTORS DISCOVERED: {sorted(factors_found)}")
    else:
        print(f"\n○ No nontrivial factors found via channels (d may be prime)")

    return quads


def quintuple_demo(e):
    """Demonstrate the six-channel framework for quintuples."""
    print(f"\n{'='*70}")
    print(f"QUINTUPLE SIX-CHANNEL DEMO: e = {e}")
    print(f"{'='*70}")

    quints = find_quintuples(e, max_count=5)
    print(f"Found {len(quints)} quintuples")

    for i, (a, b, c, d, e_val) in enumerate(quints):
        print(f"\nQuintuple {i+1}: ({a}, {b}, {c}, {d}, {e_val})")
        channels, ch_sum, ok = six_channels_quintuple(a, b, c, d, e_val)
        for name, val in channels.items():
            print(f"  {name} = {val}")
        print(f"  Sum = {ch_sum} = 3×{e_val}² = {3*e_val**2} → {'✓' if ok else '✗'}")


def pell_demo():
    """Demonstrate the Pell-Quadruple connection."""
    print(f"\n{'='*70}")
    print(f"PELL EQUATION ↔ PYTHAGOREAN QUADRUPLE CONNECTION")
    print(f"{'='*70}")

    results = pell_quadruples(8)
    print(f"\nSolutions to d² - 2a² = 1 (Pell equation for √2):\n")
    print(f"{'n':>3} {'a':>10} {'d':>10} {'Quadruple':<30} {'Verified':>8}")
    print("-" * 65)
    for i, r in enumerate(results, 1):
        q = r['quadruple']
        print(f"{i:>3} {r['a']:>10} {r['d']:>10} ({q[0]}, {q[1]}, {q[2]}, {q[3]})"
              f"{'':>10} {'✓' if r['verification'] else '✗':>8}")

    # Channel analysis for Pell quadruples
    print(f"\nChannel analysis for Pell quadruples:")
    for r in results[:4]:
        a, _, _, d = r['quadruple']
        print(f"  d={d}: Channel 1 = (d-1)(d+1) = {(d-1)*(d+1)} = 2×{a}² = {2*a**2}")


def balanced_quadruple_test():
    """Verify the No Balanced Quadruple theorem computationally."""
    print(f"\n{'='*70}")
    print(f"NO BALANCED QUADRUPLE THEOREM (computational verification)")
    print(f"{'='*70}")
    print(f"\nChecking: can a² + a² + a² = d² for any integer a, d with a ≠ 0?")
    print(f"This requires 3a² = d², i.e., d/a = √3 ≈ {sqrt(3):.10f}")
    print(f"\nSearch for near-misses (3a² ≈ d²):")
    print(f"{'a':>8} {'d=⌊a√3⌋':>10} {'3a²':>12} {'d²':>12} {'gap':>8}")
    print("-" * 55)
    for a in [1, 2, 3, 5, 10, 100, 1000, 10000]:
        d = round(a * sqrt(3))
        gap = 3 * a * a - d * d
        print(f"{a:>8} {d:>10} {3*a*a:>12} {d*d:>12} {gap:>8}")
    print(f"\nThe gap is never zero — √3 is irrational. ✓")


def modular_fingerprint_demo(d):
    """Demonstrate modular fingerprinting."""
    print(f"\n{'='*70}")
    print(f"MODULAR FINGERPRINTING: d = {d}")
    print(f"{'='*70}")

    quads = find_quadruples(d)
    if not quads:
        print("No quadruples found!")
        return

    # Find prime factors of d
    primes = []
    n = d
    for p in range(2, isqrt(d) + 1):
        if n % p == 0:
            primes.append(p)
            while n % p == 0:
                n //= p
    if n > 1:
        primes.append(n)

    print(f"Prime factors of d: {primes}")
    print(f"\nFor each prime p | d, all quadruples must satisfy a²+b²+c² ≡ 0 (mod p²):")

    for p in primes:
        p2 = p * p
        print(f"\n  p = {p}, p² = {p2}:")
        for i, (a, b, c, _) in enumerate(quads[:5]):
            norm = a*a + b*b + c*c
            residue = norm % p2
            residues_mod_p = (a % p, b % p, c % p)
            print(f"    Q{i+1} = ({a},{b},{c}): "
                  f"a²+b²+c² = {norm}, mod {p2} = {residue}, "
                  f"(a,b,c) mod {p} = {residues_mod_p}")


# ============================================================
# MAIN DEMONSTRATION
# ============================================================

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║  THE SHARED FACTOR BRIDGE: Pythagorean Quadruples & Factoring      ║")
    print("║  New Theorems Demo — Formally Verified in Lean 4                   ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")

    # Demo 1: Factor extraction for various d values
    for d in [9, 15, 21, 35, 45, 105]:
        factor_extraction_demo(d)

    # Demo 2: Pell connection
    pell_demo()

    # Demo 3: No balanced quadruple
    balanced_quadruple_test()

    # Demo 4: Quintuple six-channel framework
    for e in [5, 7, 10]:
        quintuple_demo(e)

    # Demo 5: Modular fingerprinting
    for d in [15, 35]:
        modular_fingerprint_demo(d)

    print(f"\n{'='*70}")
    print("ALL DEMOS COMPLETE")
    print(f"{'='*70}")

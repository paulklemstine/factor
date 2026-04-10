#!/usr/bin/env python3
"""
GCD Cascade and Multi-Representation Factor Extraction Demo

Demonstrates the theorems from Pythagorean__SharedFactorBridge__GCDCascade.lean:
1. Channel decomposition of Pythagorean quadruples
2. GCD Cascade across multiple representations
3. Factor extraction via channel analysis
4. Representation distance and inner product geometry
5. Higher-dimensional channel sums
6. Factor orbit descent
"""

from math import gcd, isqrt, sqrt
from itertools import combinations
from typing import List, Tuple, Optional
import random

# =============================================================================
# §1. Pythagorean Quadruple Finder
# =============================================================================

def find_quadruples(d: int, max_results: int = 20) -> List[Tuple[int, int, int, int]]:
    """Find Pythagorean quadruples (a,b,c,d) with a²+b²+c² = d²."""
    results = []
    d2 = d * d
    for a in range(0, d):
        for b in range(a, d):
            rem = d2 - a*a - b*b
            if rem < 0:
                break
            c = isqrt(rem)
            if c >= b and c*c == rem:
                results.append((a, b, c, d))
                if len(results) >= max_results:
                    return results
    return results

# =============================================================================
# §2. Channel Analysis
# =============================================================================

def channels(a: int, b: int, c: int, d: int) -> dict:
    """Compute all three channel values and their factor pairs."""
    ch_ab = a*a + b*b  # = (d-c)(d+c)
    ch_ac = a*a + c*c  # = (d-b)(d+b)
    ch_bc = b*b + c*c  # = (d-a)(d+a)
    return {
        'ch_ab': ch_ab, 'factors_ab': (d-c, d+c),
        'ch_ac': ch_ac, 'factors_ac': (d-b, d+b),
        'ch_bc': ch_bc, 'factors_bc': (d-a, d+a),
    }

def channel_sum_check(a: int, b: int, c: int, d: int) -> bool:
    """Verify: ch_ab + ch_ac + ch_bc = 2d² (Theorem: channel_sum)."""
    ch = channels(a, b, c, d)
    total = ch['ch_ab'] + ch['ch_ac'] + ch['ch_bc']
    expected = 2 * d * d
    return total == expected

def channel_product_via_d_check(a: int, b: int, c: int, d: int) -> bool:
    """Verify: (a²+b²)(a²+c²) = a²d² + b²c² (Theorem: channel_product_via_d)."""
    lhs = (a*a + b*b) * (a*a + c*c)
    rhs = a*a * d*d + b*b * c*c
    return lhs == rhs

# =============================================================================
# §3. GCD Cascade
# =============================================================================

def gcd_cascade(d: int, quads: List[Tuple[int,int,int,int]]) -> dict:
    """
    Run the GCD Cascade algorithm across multiple representations.
    Returns discovered factors and cascade details.
    """
    factors_found = set()
    cascade_log = []

    for i, (a, b, c, _) in enumerate(quads):
        ch = channels(a, b, c, d)

        # Check each channel for factor revelation
        for name, (f1, f2) in [('ab', ch['factors_ab']),
                                 ('ac', ch['factors_ac']),
                                 ('bc', ch['factors_bc'])]:
            g = gcd(abs(f1), abs(f2))
            if g > 1:
                gd = gcd(g, d)
                if 1 < gd < d:
                    factors_found.add(gd)
                    cascade_log.append(
                        f"Q{i+1} channel({name}): ({f1})×({f2}), "
                        f"gcd={g}, gcd(g,d)={gd} → FACTOR FOUND!"
                    )
                else:
                    cascade_log.append(
                        f"Q{i+1} channel({name}): ({f1})×({f2}), "
                        f"gcd={g}, gcd(g,d)={gd}"
                    )

    # Cross-representation GCD (Theorem: gcd_extraction)
    for i, (a1, b1, c1, _) in enumerate(quads):
        for j, (a2, b2, c2, _) in enumerate(quads):
            if j <= i:
                continue
            # gcd(d-c1, d-c2) divides c2-c1
            g_minus = gcd(abs(d - c1), abs(d - c2))
            g_plus = gcd(abs(d + c1), abs(d + c2))
            g_cross = gcd(abs(d - c1), abs(d + c2))

            for label, g in [('d-c_i', g_minus), ('d+c_i', g_plus), ('cross', g_cross)]:
                gd = gcd(g, d)
                if 1 < gd < d:
                    factors_found.add(gd)
                    cascade_log.append(
                        f"Q{i+1}×Q{j+1} {label}: gcd={g}, gcd(g,d)={gd} → FACTOR FOUND!"
                    )

    return {'factors': factors_found, 'log': cascade_log}

# =============================================================================
# §4. Representation Distance
# =============================================================================

def rep_distance(q1: Tuple[int,int,int,int], q2: Tuple[int,int,int,int]) -> int:
    """Squared distance between two representations (Theorem: repDist_eq)."""
    return sum((q1[i] - q2[i])**2 for i in range(3))

def rep_inner_product(q1: Tuple[int,int,int,int], q2: Tuple[int,int,int,int]) -> int:
    """Inner product of two representations."""
    return sum(q1[i] * q2[i] for i in range(3))

def verify_distance_identity(q1, q2, d):
    """Verify: dist² = 2d² - 2⟨v1,v2⟩ (Theorem: repDist_eq)."""
    dist = rep_distance(q1, q2)
    ip = rep_inner_product(q1, q2)
    return dist == 2*d*d - 2*ip

def verify_cauchy_schwarz(q1, q2, d):
    """Verify: ⟨v1,v2⟩² ≤ d⁴ (Theorem: inner_product_bound)."""
    ip = rep_inner_product(q1, q2)
    return ip**2 <= d**4

# =============================================================================
# §5. Factor Orbit Descent
# =============================================================================

def factor_orbit_descent(a: int, b: int, c: int, d: int) -> Optional[Tuple]:
    """
    If gcd(a,b,c) > 1, descend to a smaller quadruple.
    (Theorem: factor_orbit_descent)
    """
    g = gcd(gcd(abs(a), abs(b)), abs(c))
    if g <= 1:
        return None
    a2, b2, c2 = a // g, b // g, c // g
    # Check: g² * (a'²+b'²+c'²) = d²
    if g*g * (a2*a2 + b2*b2 + c2*c2) != d*d:
        return None
    d2 = d // g
    if d2 * d2 != a2*a2 + b2*b2 + c2*c2:
        # d might not be divisible by g in ℤ, but g² | d²
        return None
    return (a2, b2, c2, d2, g)

# =============================================================================
# §6. Higher-Dimensional Channel Sums
# =============================================================================

def verify_channel_sum_nd(components: List[int], hyp: int, n: int) -> bool:
    """
    Verify: sum of all C(n,2) pair-keep channels = (n-1) * hyp².
    """
    assert sum(x**2 for x in components) == hyp**2
    pair_sum = 0
    for i, j in combinations(range(n), 2):
        pair_sum += components[i]**2 + components[j]**2
    return pair_sum == (n - 1) * hyp**2

# =============================================================================
# §7. Brahmagupta-Fibonacci Identity
# =============================================================================

def brahmagupta(a, b, c, d):
    """Two representations of (a²+b²)(c²+d²) as sum of two squares."""
    r1 = ((a*c - b*d)**2 + (a*d + b*c)**2)
    r2 = ((a*c + b*d)**2 + (a*d - b*c)**2)
    product = (a**2 + b**2) * (c**2 + d**2)
    assert r1 == product == r2
    return {
        'product': product,
        'rep1': (abs(a*c - b*d), abs(a*d + b*c)),
        'rep2': (abs(a*c + b*d), abs(a*d - b*c)),
    }

# =============================================================================
# §8. Main Demo
# =============================================================================

def demo_channel_analysis(d: int):
    """Full channel analysis demo for a given d."""
    print(f"\n{'='*70}")
    print(f"  CHANNEL ANALYSIS FOR d = {d}")
    print(f"{'='*70}")

    quads = find_quadruples(d)
    if not quads:
        print(f"  No quadruples found for d={d}")
        return

    print(f"\n  Found {len(quads)} quadruple(s):")
    for i, (a, b, c, d_) in enumerate(quads):
        print(f"    Q{i+1}: ({a}, {b}, {c}, {d_})  "
              f"[{a}²+{b}²+{c}² = {a**2}+{b**2}+{c**2} = {d_**2}]")

    # Channel analysis
    print(f"\n  Channel Analysis:")
    for i, (a, b, c, d_) in enumerate(quads):
        ch = channels(a, b, c, d)
        print(f"\n    Q{i+1} = ({a}, {b}, {c}, {d_}):")
        print(f"      Ch(a,b) = {a}²+{b}² = {ch['ch_ab']} = "
              f"({ch['factors_ab'][0]})×({ch['factors_ab'][1]})")
        print(f"      Ch(a,c) = {a}²+{c}² = {ch['ch_ac']} = "
              f"({ch['factors_ac'][0]})×({ch['factors_ac'][1]})")
        print(f"      Ch(b,c) = {b}²+{c}² = {ch['ch_bc']} = "
              f"({ch['factors_bc'][0]})×({ch['factors_bc'][1]})")

        # Verify channel sum = 2d²
        assert channel_sum_check(a, b, c, d), "Channel sum check failed!"
        print(f"      Channel sum = {ch['ch_ab']+ch['ch_ac']+ch['ch_bc']} = 2×{d}² ✓")

        # Verify channel product identity
        assert channel_product_via_d_check(a, b, c, d), "Channel product check failed!"
        print(f"      (a²+b²)(a²+c²) = a²d²+b²c² = {a**2*d**2+b**2*c**2} ✓")

    # GCD Cascade
    print(f"\n  GCD Cascade:")
    result = gcd_cascade(d, quads)
    for line in result['log']:
        print(f"    {line}")
    if result['factors']:
        print(f"\n  ★ Factors found: {result['factors']}")
        for f in result['factors']:
            print(f"    {d} = {f} × {d // f}")
    else:
        print(f"\n  No factors extracted (d may be prime or cascade insufficient)")

    # Representation distances
    if len(quads) >= 2:
        print(f"\n  Representation Geometry:")
        for i in range(min(len(quads), 4)):
            for j in range(i+1, min(len(quads), 4)):
                dist = rep_distance(quads[i], quads[j])
                ip = rep_inner_product(quads[i], quads[j])
                assert verify_distance_identity(quads[i], quads[j], d)
                assert verify_cauchy_schwarz(quads[i], quads[j], d)
                cos_theta = ip / (d**2) if d > 0 else 0
                print(f"    Q{i+1}↔Q{j+1}: dist²={dist}, ⟨v₁,v₂⟩={ip}, "
                      f"cos θ={cos_theta:.4f}")

    # Factor orbit descent
    print(f"\n  Factor Orbit Descent:")
    for i, (a, b, c, d_) in enumerate(quads):
        result = factor_orbit_descent(a, b, c, d)
        if result:
            a2, b2, c2, d2, g = result
            print(f"    Q{i+1}: gcd(a,b,c) = {g} → descended to ({a2},{b2},{c2},{d2})")
        else:
            print(f"    Q{i+1}: gcd({a},{b},{c}) = {gcd(gcd(abs(a),abs(b)),abs(c))} (primitive)")

def demo_higher_dimensional():
    """Verify the general channel sum formula for higher dimensions."""
    print(f"\n{'='*70}")
    print(f"  HIGHER-DIMENSIONAL CHANNEL SUMS")
    print(f"{'='*70}")

    # n=3: quadruples
    comps3 = [2, 10, 11]; hyp3 = 15
    assert sum(x**2 for x in comps3) == hyp3**2
    ok3 = verify_channel_sum_nd(comps3, hyp3, 3)
    print(f"  n=3: ({comps3}, {hyp3}): pair sum = {2*hyp3**2} = {2}×{hyp3}² {'✓' if ok3 else '✗'}")

    # n=4: quintuples
    comps4 = [1, 2, 4, 10]; hyp4_sq = sum(x**2 for x in comps4)
    hyp4 = isqrt(hyp4_sq)
    if hyp4*hyp4 == hyp4_sq:
        ok4 = verify_channel_sum_nd(comps4, hyp4, 4)
        print(f"  n=4: ({comps4}, {hyp4}): pair sum = {3*hyp4**2} = {3}×{hyp4}² {'✓' if ok4 else '✗'}")
    else:
        # Find a valid quintuple
        comps4 = [1, 2, 2, 4]; hyp4_sq = sum(x**2 for x in comps4)
        hyp4 = isqrt(hyp4_sq)
        if hyp4*hyp4 == hyp4_sq:
            ok4 = verify_channel_sum_nd(comps4, hyp4, 4)
            print(f"  n=4: ({comps4}, {hyp4}): pair sum = {3*hyp4**2} = {3}×{hyp4}² {'✓' if ok4 else '✗'}")
        else:
            comps4 = [2, 3, 6, 18]; hyp4_sq = sum(x**2 for x in comps4)
            hyp4 = isqrt(hyp4_sq)
            print(f"  n=4: ({comps4}, hyp²={hyp4_sq}): searching...")

    # Verify the pattern: sum = (n-1) * y²
    print(f"\n  General pattern: Σ pair-keep channels = (n-1) × y²")
    print(f"  n=3: 3 channels, sum = 2y² (quadruples)")
    print(f"  n=4: 6 channels, sum = 3y² (quintuples)")
    print(f"  n=5: 10 channels, sum = 4y² (sextuples)")
    print(f"  n=6: 15 channels, sum = 5y² (septuples)")

def demo_brahmagupta():
    """Demonstrate the Brahmagupta-Fibonacci identity for channel products."""
    print(f"\n{'='*70}")
    print(f"  BRAHMAGUPTA-FIBONACCI IDENTITY FOR CHANNELS")
    print(f"{'='*70}")

    # For quadruple (6, 10, 33, 35):
    a, b, c, d = 6, 10, 33, 35
    ch_ab = a**2 + b**2  # 136
    ch_ac = a**2 + c**2  # 1125

    # Brahmagupta: ch_ab × ch_ac = (a²+b²)(a²+c²)
    # Using a,b as first sum-of-squares, a,c as second
    print(f"\n  Quadruple: ({a}, {b}, {c}, {d})")
    print(f"  Ch(a,b) = {ch_ab}, Ch(a,c) = {ch_ac}")
    print(f"  Product = {ch_ab * ch_ac}")
    print(f"  a²d² + b²c² = {a**2*d**2} + {b**2*c**2} = {a**2*d**2 + b**2*c**2}")
    assert ch_ab * ch_ac == a**2 * d**2 + b**2 * c**2, "Channel product identity failed!"
    print(f"  ✓ Verified: (a²+b²)(a²+c²) = a²d² + b²c²")

    # Apply Brahmagupta to the sum-of-squares representations
    # ch_ab = 6² + 10² = 136, ch_ac = 6² + 33² = 1125
    # Product = 136 × 1125 = 153000
    # Rep 1: (6·6 - 10·33)² + (6·33 + 10·6)² = (36-330)² + (198+60)² = 294² + 258²
    # Rep 2: (6·6 + 10·33)² + (6·33 - 10·6)² = (36+330)² + (198-60)² = 366² + 138²
    r = brahmagupta(a, b, a, c)
    print(f"\n  Brahmagupta representations of {r['product']}:")
    print(f"    Rep 1: {r['rep1'][0]}² + {r['rep1'][1]}² = {r['rep1'][0]**2 + r['rep1'][1]**2}")
    print(f"    Rep 2: {r['rep2'][0]}² + {r['rep2'][1]}² = {r['rep2'][0]**2 + r['rep2'][1]**2}")

    # Factoring opportunity from dual representations
    diff = abs(r['rep1'][0]**2 - r['rep2'][0]**2)
    print(f"\n  Difference: {r['rep1'][0]}² - {r['rep2'][0]}² = {diff}")
    print(f"  = -4·{a}·{b}·{a}·{c} = {-4*a*b*a*c} (by brahmagupta_diff theorem)")

def demo_pell_connection():
    """Show the Pell equation connection for near-balanced quadruples."""
    print(f"\n{'='*70}")
    print(f"  PELL EQUATION CONNECTION")
    print(f"{'='*70}")

    print(f"\n  Pell equation: d² - 2a² = 1")
    print(f"  Each solution gives quadruple (a, a, 1, d):")
    print()

    # Generate Pell solutions using recurrence
    pell_solutions = [(1, 0)]
    d_prev, a_prev = 1, 0
    for _ in range(8):
        d_new = 3*d_prev + 4*a_prev
        a_new = 2*d_prev + 3*a_prev
        pell_solutions.append((d_new, a_new))
        d_prev, a_prev = d_new, a_new

    print(f"  {'n':>3} {'d':>10} {'a':>10} {'Quadruple':>30} {'d²-2a²':>10} {'Verify':>8}")
    print(f"  {'─'*3} {'─'*10} {'─'*10} {'─'*30} {'─'*10} {'─'*8}")

    for n, (d, a) in enumerate(pell_solutions):
        if a == 0:
            continue
        quad = f"({a}, {a}, 1, {d})"
        pell_val = d*d - 2*a*a
        verify = a*a + a*a + 1 == d*d
        print(f"  {n:>3} {d:>10} {a:>10} {quad:>30} {pell_val:>10} {'✓' if verify else '✗':>8}")

def demo_no_balanced():
    """Demonstrate the No Balanced Quadruple theorem."""
    print(f"\n{'='*70}")
    print(f"  NO BALANCED QUADRUPLE THEOREM")
    print(f"{'='*70}")

    print(f"\n  Theorem: 3a² = d² has no solution with a ≠ 0.")
    print(f"  Proof: √3 is irrational.")
    print()
    print(f"  Verification (checking small values):")
    for a in range(1, 20):
        d2 = 3 * a * a
        d = isqrt(d2)
        is_square = d * d == d2
        if is_square:
            print(f"    a={a}: 3×{a}² = {d2}, √{d2} = {d} — PERFECT SQUARE (impossible!)")
        else:
            ratio = sqrt(3) * a
            print(f"    a={a}: 3×{a}² = {d2}, √{d2} ≈ {ratio:.4f} (not integer)")
        if a >= 8:
            print(f"    ...")
            break

    print(f"\n  The nearest misses:")
    best_misses = []
    for a in range(1, 1000):
        d2 = 3 * a * a
        d = isqrt(d2)
        gap = d2 - d*d
        if gap == 0:
            gap = 1  # shouldn't happen
        best_misses.append((gap, a, d, d2))
    best_misses.sort()
    for gap, a, d, d2 in best_misses[:5]:
        print(f"    a={a}: 3×{a}² = {d2}, nearest square = {d}² = {d*d}, gap = {gap}")

def main():
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║  GCD CASCADE & MULTI-REPRESENTATION FACTOR EXTRACTION DEMO          ║")
    print("║  Based on formally verified theorems (Lean 4 + Mathlib)             ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")

    # Demo 1: Channel analysis for composite numbers
    for d in [15, 21, 35]:
        demo_channel_analysis(d)

    # Demo 2: Brahmagupta identity
    demo_brahmagupta()

    # Demo 3: Pell connection
    demo_pell_connection()

    # Demo 4: No balanced quadruple
    demo_no_balanced()

    # Demo 5: Higher-dimensional channel sums
    demo_higher_dimensional()

    print(f"\n{'='*70}")
    print(f"  ALL DEMOS COMPLETE")
    print(f"{'='*70}")

if __name__ == '__main__':
    main()

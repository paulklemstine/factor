#!/usr/bin/env python3
"""
GCD Cascade Framework: Advanced Demonstrations
================================================

Demonstrates the GCD Cascade for integer factoring using Pythagorean quadruples.
Explores channel structure, cascade propagation, and higher-dimensional extensions.
"""

import math
from itertools import combinations
from typing import List, Tuple, Optional, Dict

# ============================================================
# Core: Finding Pythagorean Quadruples
# ============================================================

def find_quadruples(d: int, max_results: int = 100) -> List[Tuple[int, int, int, int]]:
    """Find all Pythagorean quadruples (a, b, c, d) with a² + b² + c² = d²."""
    results = []
    d2 = d * d
    for a in range(1, d):
        for b in range(a, d):
            remainder = d2 - a*a - b*b
            if remainder <= 0:
                break
            c = int(math.isqrt(remainder))
            if c >= b and c*c == remainder:
                results.append((a, b, c, d))
                if len(results) >= max_results:
                    return results
    return results

# ============================================================
# Channel Analysis
# ============================================================

def compute_channels(a: int, b: int, c: int, d: int) -> Dict[str, int]:
    """Compute the three channel values for a quadruple."""
    return {
        'ab': a*a + b*b,  # = (d-c)(d+c)
        'ac': a*a + c*c,  # = (d-b)(d+b)
        'bc': b*b + c*c,  # = (d-a)(d+a)
    }

def channel_factors(a: int, b: int, c: int, d: int) -> Dict[str, Tuple[int, int]]:
    """Compute the linear factor pairs for each channel."""
    return {
        'ab': (d - c, d + c),
        'ac': (d - b, d + b),
        'bc': (d - a, d + a),
    }

# ============================================================
# GCD Cascade
# ============================================================

def gcd_cascade(d: int, quadruples: List[Tuple[int, int, int, int]]) -> List[Dict]:
    """Run the GCD Cascade algorithm on a set of quadruples sharing hypotenuse d."""
    results = []
    
    for i, q1 in enumerate(quadruples):
        for j, q2 in enumerate(quadruples):
            if j <= i:
                continue
            a1, b1, c1, _ = q1
            a2, b2, c2, _ = q2
            
            # Compute GCDs for each component
            for comp_name, (v1, v2) in [('c', (c1, c2)), ('b', (b1, b2)), ('a', (a1, a2))]:
                g_minus = math.gcd(d - v1, d - v2)
                g_plus = math.gcd(d + v1, d + v2)
                g_cross = math.gcd(d - v1, d + v2)
                
                factor_minus = math.gcd(g_minus, d)
                factor_plus = math.gcd(g_plus, d)
                factor_cross = math.gcd(g_cross, d)
                
                for label, g, f in [('d-v', g_minus, factor_minus),
                                     ('d+v', g_plus, factor_plus),
                                     ('cross', g_cross, factor_cross)]:
                    if f > 1 and f < d:
                        results.append({
                            'q1': q1, 'q2': q2,
                            'component': comp_name,
                            'type': label,
                            'gcd_value': g,
                            'factor': f,
                            'cofactor': d // f
                        })
    
    return results

# ============================================================
# Channel Product Analysis
# ============================================================

def channel_product_analysis(a: int, b: int, c: int, d: int):
    """Verify channel product identities."""
    ch_ab = a*a + b*b
    ch_ac = a*a + c*c
    ch_bc = b*b + c*c
    
    # Identity: ch_ab * ch_ac = a²d² + b²c²
    lhs = ch_ab * ch_ac
    rhs = a*a*d*d + b*b*c*c
    assert lhs == rhs, f"Channel product identity failed: {lhs} != {rhs}"
    
    # Identity: ch_ab * ch_bc = b²d² + a²c²
    lhs2 = ch_ab * ch_bc
    rhs2 = b*b*d*d + a*a*c*c
    assert lhs2 == rhs2, f"Channel product identity 2 failed: {lhs2} != {rhs2}"
    
    # Identity: ch_ac * ch_bc = c²d² + a²b²
    lhs3 = ch_ac * ch_bc
    rhs3 = c*c*d*d + a*a*b*b
    assert lhs3 == rhs3, f"Channel product identity 3 failed: {lhs3} != {rhs3}"
    
    # Channel product simplified
    triple = ch_ab * ch_ac * ch_bc
    simplified = d*d*(a*a*b*b + a*a*c*c + b*b*c*c) - a*a*b*b*c*c
    assert triple == simplified, f"Triple product identity failed: {triple} != {simplified}"
    
    return {
        'ch_ab': ch_ab, 'ch_ac': ch_ac, 'ch_bc': ch_bc,
        'product_ab_ac': lhs, 'product_ab_bc': lhs2, 'product_ac_bc': lhs3,
        'triple_product': triple,
        'simplified': simplified
    }

# ============================================================
# Representation Distance
# ============================================================

def rep_distance(q1: Tuple[int, int, int, int], q2: Tuple[int, int, int, int]) -> int:
    """Compute squared distance between two representations."""
    return sum((v1 - v2)**2 for v1, v2 in zip(q1[:3], q2[:3]))

def rep_inner_product(q1: Tuple[int, int, int, int], q2: Tuple[int, int, int, int]) -> int:
    """Compute inner product of two representations."""
    return sum(v1 * v2 for v1, v2 in zip(q1[:3], q2[:3]))

# ============================================================
# Higher-Dimensional Cascades
# ============================================================

def find_higher_dim_reps(d: int, n_dim: int, max_results: int = 20) -> List[Tuple]:
    """Find representations of d² as sum of n_dim squares."""
    results = []
    d2 = d * d
    
    def search(remaining: int, dim_left: int, min_val: int, current: List[int]):
        if dim_left == 1:
            c = int(math.isqrt(remaining))
            if c >= min_val and c * c == remaining:
                results.append(tuple(current + [c]))
            return
        max_v = int(math.isqrt(remaining))
        for v in range(min_val, max_v + 1):
            if len(results) >= max_results:
                return
            search(remaining - v*v, dim_left - 1, v, current + [v])
    
    search(d2, n_dim, 1, [])
    return results

def dim_channel_sum(rep: Tuple, d: int) -> int:
    """Compute sum of all pair-channels for a representation."""
    n = len(rep)
    total = 0
    for i in range(n):
        for j in range(i+1, n):
            total += rep[i]**2 + rep[j]**2
    return total

# ============================================================
# Main Demonstrations
# ============================================================

def demo_basic_cascade():
    """Demonstrate the basic GCD Cascade on small composites."""
    print("=" * 70)
    print("DEMO 1: Basic GCD Cascade")
    print("=" * 70)
    
    for d in [15, 21, 35, 45, 63, 77, 105]:
        quads = find_quadruples(d)
        if not quads:
            continue
        
        print(f"\n--- d = {d} = ", end="")
        # Simple factorization display
        factors = []
        n = d
        for p in range(2, int(math.isqrt(n)) + 1):
            while n % p == 0:
                factors.append(p)
                n //= p
        if n > 1:
            factors.append(n)
        print(" × ".join(map(str, factors)), "---")
        
        print(f"  Found {len(quads)} quadruples:")
        for q in quads[:5]:
            a, b, c, _ = q
            channels = compute_channels(a, b, c, d)
            print(f"    ({a}, {b}, {c}, {d})")
            print(f"      Channels: ab={channels['ab']}, ac={channels['ac']}, bc={channels['bc']}")
            
            # Check each channel for factors
            cf = channel_factors(a, b, c, d)
            for name, (lo, hi) in cf.items():
                g = math.gcd(lo, d)
                if g > 1 and g < d:
                    print(f"      ⚡ Channel {name}: ({lo})×({hi}), gcd({lo},{d}) = {g} → factor!")
        
        # Run cascade
        if len(quads) >= 2:
            cascade_results = gcd_cascade(d, quads[:5])
            if cascade_results:
                print(f"  Cascade found {len(cascade_results)} factor(s):")
                seen = set()
                for r in cascade_results:
                    f = r['factor']
                    if f not in seen:
                        print(f"    Factor {f} (cofactor {r['cofactor']}) via {r['type']} on component {r['component']}")
                        seen.add(f)

def demo_channel_products():
    """Demonstrate channel product identities."""
    print("\n" + "=" * 70)
    print("DEMO 2: Channel Product Identities")
    print("=" * 70)
    
    test_quads = [
        (1, 2, 2, 3), (2, 3, 6, 7), (1, 4, 8, 9), (4, 4, 7, 9),
        (6, 10, 33, 35), (15, 10, 30, 35), (6, 9, 18, 21)
    ]
    
    for q in test_quads:
        a, b, c, d = q
        result = channel_product_analysis(a, b, c, d)
        print(f"\n  ({a}, {b}, {c}, {d}):")
        print(f"    Channels: ab={result['ch_ab']}, ac={result['ch_ac']}, bc={result['ch_bc']}")
        print(f"    Product ab×ac = {result['product_ab_ac']} = {a}²×{d}² + {b}²×{c}² = {a*a*d*d} + {b*b*c*c}")
        print(f"    Triple product = {result['triple_product']}")
        print(f"    Simplified = d²(Σa²b²) - a²b²c² = {result['simplified']} ✓")

def demo_representation_geometry():
    """Demonstrate sphere geometry of representations."""
    print("\n" + "=" * 70)
    print("DEMO 3: Representation Distance Geometry")
    print("=" * 70)
    
    for d in [9, 15, 21, 35]:
        quads = find_quadruples(d)
        if len(quads) < 2:
            continue
        
        print(f"\n  d = {d}, {len(quads)} representations:")
        for i, q1 in enumerate(quads):
            for j, q2 in enumerate(quads):
                if j <= i:
                    continue
                dist2 = rep_distance(q1, q2)
                ip = rep_inner_product(q1, q2)
                expected_dist = 2*d*d - 2*ip
                
                print(f"    {q1[:3]} ↔ {q2[:3]}:")
                print(f"      dist² = {dist2}, inner = {ip}, 2d²-2⟨v₁,v₂⟩ = {expected_dist}")
                assert dist2 == expected_dist, "Distance identity violated!"
                print(f"      cos θ = {ip}/{d*d} = {ip/(d*d):.4f}")

def demo_higher_dim():
    """Demonstrate higher-dimensional cascades."""
    print("\n" + "=" * 70)
    print("DEMO 4: Higher-Dimensional Channel Sums")
    print("=" * 70)
    
    for n_dim, label in [(3, "3D"), (4, "4D"), (5, "5D")]:
        print(f"\n  --- {label} ---")
        for d in [7, 9, 15]:
            reps = find_higher_dim_reps(d, n_dim, max_results=3)
            if not reps:
                continue
            for rep in reps[:2]:
                cs = dim_channel_sum(rep, d)
                expected = (n_dim - 1) * d * d
                n_channels = n_dim * (n_dim - 1) // 2
                print(f"    d={d}, rep={rep}")
                print(f"      {n_channels} pair-channels, sum = {cs} = {n_dim-1}×{d}² = {expected} {'✓' if cs == expected else '✗'}")

def demo_cascade_network():
    """Demonstrate cascade network with many representations."""
    print("\n" + "=" * 70)
    print("DEMO 5: Cascade Network Analysis")
    print("=" * 70)
    
    for d in [105, 315, 1155]:
        quads = find_quadruples(d, max_results=20)
        if len(quads) < 3:
            continue
        
        print(f"\n  d = {d}:")
        # Simple factorization
        factors = []
        n = d
        for p in range(2, int(math.isqrt(n)) + 1):
            while n % p == 0:
                factors.append(p)
                n //= p
        if n > 1:
            factors.append(n)
        print(f"    Factorization: {' × '.join(map(str, factors))}")
        print(f"    Found {len(quads)} quadruples")
        
        # Cascade analysis
        n_pairs = len(quads) * (len(quads) - 1) // 2
        cascade_results = gcd_cascade(d, quads)
        
        found_factors = set()
        for r in cascade_results:
            found_factors.add(r['factor'])
        
        print(f"    {n_pairs} pairs analyzed")
        print(f"    Factors found via cascade: {sorted(found_factors) if found_factors else 'none'}")
        print(f"    True prime factors: {sorted(set(factors))}")

def demo_prime_factor_dichotomy():
    """Demonstrate the prime factor channel dichotomy."""
    print("\n" + "=" * 70)
    print("DEMO 6: Prime Factor Channel Dichotomy")
    print("=" * 70)
    
    d = 35
    quads = find_quadruples(d)
    primes = [5, 7]
    
    for q in quads:
        a, b, c, _ = q
        print(f"\n  Quadruple ({a}, {b}, {c}, {d}):")
        for p in primes:
            print(f"    Prime p = {p}:")
            for comp_name, comp_val in [('a', a), ('b', b), ('c', c)]:
                if comp_val % p == 0:
                    dc_minus = d - comp_val
                    dc_plus = d + comp_val
                    print(f"      p | {comp_name}={comp_val}: p | (d-{comp_name})={dc_minus}? {'Yes' if dc_minus % p == 0 else 'No'}, p | (d+{comp_name})={dc_plus}? {'Yes' if dc_plus % p == 0 else 'No'}")
                    if dc_minus % p == 0 and dc_plus % p == 0:
                        print(f"        → BOTH factors divisible (Strengthened Dichotomy)")
                else:
                    print(f"      p ∤ {comp_name}={comp_val}: Euclid's lemma applies to channel")

def demo_no_balanced():
    """Verify the no balanced quadruple theorem computationally."""
    print("\n" + "=" * 70)
    print("DEMO 7: No Balanced Quadruple Theorem")
    print("=" * 70)
    
    print("\n  Checking: Does 3a² = d² have nonzero solutions?")
    for a in range(1, 10000):
        d2 = 3 * a * a
        d = int(math.isqrt(d2))
        if d * d == d2:
            print(f"  Found: a={a}, d={d} (IMPOSSIBLE!)")
            return
    print(f"  No solutions found for a in [1, 9999].")
    print(f"  This is because √3 is irrational (formally proven in Lean).")
    
    print(f"\n  Near misses (|3a² - d²| ≤ 3):")
    for a in range(1, 100):
        d2 = 3 * a * a
        d = int(math.isqrt(d2))
        for dd in [d, d+1]:
            diff = abs(3 * a * a - dd * dd)
            if diff <= 3:
                print(f"    a={a}, d={dd}: 3×{a}² = {3*a*a}, {dd}² = {dd*dd}, diff = {diff}")

# ============================================================
# Run All Demos
# ============================================================

if __name__ == "__main__":
    print("GCD CASCADE FRAMEWORK: ADVANCED DEMONSTRATIONS")
    print("=" * 70)
    print()
    
    demo_basic_cascade()
    demo_channel_products()
    demo_representation_geometry()
    demo_higher_dim()
    demo_cascade_network()
    demo_prime_factor_dichotomy()
    demo_no_balanced()
    
    print("\n" + "=" * 70)
    print("All demonstrations complete.")
    print("=" * 70)

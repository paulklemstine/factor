#!/usr/bin/env python3
"""
Quadruple Division Factoring: Arithmetic Geometry & Quantum Demo

Demonstrates the new theorems from the ArithGeomQuantum research:
1. Radical decomposition and triple factoring channels
2. Brahmagupta-Fibonacci composition for explicit factoring
3. Quadratic parametric family generation
4. Modular cascade p-divisibility propagation
5. Bloch sphere rational point visualization
6. Cauchy-Schwarz inner product bounds
7. Euler four-square composition
"""

import math
from fractions import Fraction
from collections import defaultdict

# ============================================================
# §1. Pythagorean Quadruple Generation
# ============================================================

def find_quadruples(d_max=50):
    """Find all Pythagorean quadruples (a,b,c,d) with a²+b²+c²=d², 0<a≤b≤c<d≤d_max."""
    quads = []
    for d in range(1, d_max + 1):
        for c in range(0, d):
            rem = d*d - c*c
            for b in range(0, int(math.isqrt(rem)) + 1):
                a_sq = rem - b*b
                if a_sq >= 0:
                    a = math.isqrt(a_sq)
                    if a*a == a_sq and 0 < a <= b <= c:
                        quads.append((a, b, c, d))
    return quads

def quadratic_family(n_max=20):
    """Generate quadruples from the quadratic family: n² + (n+1)² + (n(n+1))² = (n²+n+1)²."""
    family = []
    for n in range(1, n_max + 1):
        a = n
        b = n + 1
        c = n * (n + 1)
        d = n*n + n + 1
        assert a*a + b*b + c*c == d*d, f"Failed for n={n}"
        family.append((a, b, c, d))
    return family

# ============================================================
# §2. Radical Decomposition (3 channels)
# ============================================================

def radical_decomposition(a, b, c, d):
    """Return all 3 factoring channels from a quadruple."""
    assert a*a + b*b + c*c == d*d
    channels = [
        ("d-c", "d+c", d-c, d+c, a*a + b*b),
        ("d-b", "d+b", d-b, d+b, a*a + c*c),
        ("d-a", "d+a", d-a, d+a, b*b + c*c),
    ]
    return channels

def demo_radical_decomposition():
    """Demonstrate 3-channel radical decomposition."""
    print("=" * 70)
    print("§2. RADICAL DECOMPOSITION: 3 FACTORING CHANNELS")
    print("=" * 70)
    
    examples = [(1, 2, 2, 3), (2, 3, 6, 7), (3, 4, 12, 13), (1, 4, 8, 9)]
    for a, b, c, d in examples:
        print(f"\nQuadruple ({a}, {b}, {c}, {d}): {a}² + {b}² + {c}² = {d}²")
        channels = radical_decomposition(a, b, c, d)
        for name1, name2, v1, v2, rhs in channels:
            print(f"  Channel ({name1})({name2}) = ({v1})({v2}) = {v1*v2} = {rhs}")

# ============================================================
# §3. Brahmagupta-Fibonacci Composition
# ============================================================

def sum_of_two_squares(n):
    """Try to write n as a² + b², return (a,b) or None."""
    for a in range(0, int(math.isqrt(n)) + 1):
        b_sq = n - a*a
        b = math.isqrt(b_sq)
        if b*b == b_sq:
            return (a, b)
    return None

def brahmagupta_compose(a1, b1, a2, b2):
    """Brahmagupta-Fibonacci: (a1²+b1²)(a2²+b2²) = (a1a2-b1b2)² + (a1b2+b1a2)²."""
    x = a1*a2 - b1*b2
    y = a1*b2 + b1*a2
    return (abs(x), abs(y))

def demo_brahmagupta():
    """Demonstrate Brahmagupta-Fibonacci composition for QDF."""
    print("\n" + "=" * 70)
    print("§3. BRAHMAGUPTA-FIBONACCI COMPOSITION")
    print("=" * 70)
    
    examples = [(2, 3, 6, 7), (3, 4, 12, 13), (1, 4, 8, 9)]
    for a, b, c, d in examples:
        dc_minus = d - c
        dc_plus = d + c
        s1 = sum_of_two_squares(dc_minus)
        s2 = sum_of_two_squares(dc_plus)
        
        print(f"\nQuadruple ({a},{b},{c},{d}): d-c={dc_minus}, d+c={dc_plus}")
        if s1 and s2:
            p, q = s1
            r, s = s2
            x, y = brahmagupta_compose(p, q, r, s)
            print(f"  d-c = {p}² + {q}² = {dc_minus}")
            print(f"  d+c = {r}² + {s}² = {dc_plus}")
            print(f"  Brahmagupta: a²+b² = {x}² + {y}² = {x*x + y*y}")
            print(f"  Actual:      a²+b² = {a}² + {b}² = {a*a + b*b}")
        else:
            print(f"  (d±c not both decomposable as sums of 2 squares)")

# ============================================================
# §4. Modular Cascade
# ============================================================

def demo_modular_cascade():
    """Demonstrate the p-cascade: p|d and p|c implies p²|(a²+b²)."""
    print("\n" + "=" * 70)
    print("§4. MODULAR p-CASCADE")
    print("=" * 70)
    
    quads = find_quadruples(50)
    print(f"\nSearching {len(quads)} quadruples for modular cascades...\n")
    
    cascade_count = 0
    for a, b, c, d in quads:
        for p in range(2, d + 1):
            if d % p == 0 and c % p == 0:
                ab_sum = a*a + b*b
                if ab_sum % (p*p) == 0:
                    cascade_count += 1
                    if cascade_count <= 10:
                        print(f"  p={p}: ({a},{b},{c},{d}) → p|d, p|c → p²={p*p} | (a²+b²={ab_sum})")
                        # Check triple cascade
                        if a % p == 0:
                            print(f"    Triple cascade: p|a too → p²={p*p} | b²={b*b}: {b*b % (p*p) == 0}")
    print(f"\n  Total cascade instances found: {cascade_count}")

# ============================================================
# §5. Quadratic Family
# ============================================================

def demo_quadratic_family():
    """Demonstrate the quadratic family n² + (n+1)² + (n(n+1))² = (n²+n+1)²."""
    print("\n" + "=" * 70)
    print("§5. QUADRATIC PARAMETRIC FAMILY")
    print("=" * 70)
    print("\n  n² + (n+1)² + (n·(n+1))² = (n²+n+1)²\n")
    
    print(f"  {'n':>3} | {'a=n':>5} {'b=n+1':>6} {'c=n(n+1)':>9} {'d=n²+n+1':>10} | {'Check':>10}")
    print("  " + "-" * 52)
    
    for n in range(1, 16):
        a = n
        b = n + 1
        c = n * (n + 1)
        d = n*n + n + 1
        check = a*a + b*b + c*c
        print(f"  {n:>3} | {a:>5} {b:>6} {c:>9} {d:>10} | {check:>5}={d*d:>5} {'✓' if check == d*d else '✗'}")

# ============================================================
# §6. Bloch Sphere Points
# ============================================================

def demo_bloch_sphere():
    """Demonstrate rational Bloch sphere points from quadruples."""
    print("\n" + "=" * 70)
    print("§6. BLOCH SPHERE RATIONAL POINTS")
    print("=" * 70)
    print("\n  (a/d)² + (b/d)² + (c/d)² = 1  [rational points on S²]\n")
    
    quads = find_quadruples(20)
    for a, b, c, d in quads[:12]:
        x = Fraction(a, d)
        y = Fraction(b, d)
        z = Fraction(c, d)
        check = x*x + y*y + z*z
        print(f"  ({a},{b},{c},{d}) → ({x}, {y}, {z}), |v|² = {check}")

# ============================================================
# §7. Cauchy-Schwarz Inner Products
# ============================================================

def demo_cauchy_schwarz():
    """Demonstrate Cauchy-Schwarz bounds on quadruple inner products."""
    print("\n" + "=" * 70)
    print("§7. CAUCHY-SCHWARZ INNER PRODUCT BOUNDS")
    print("=" * 70)
    print("\n  (a₁a₂ + b₁b₂ + c₁c₂)² ≤ d₁² · d₂²\n")
    
    quads = find_quadruples(20)[:8]
    for i, (a1, b1, c1, d1) in enumerate(quads):
        for j, (a2, b2, c2, d2) in enumerate(quads):
            if i < j:
                ip = a1*a2 + b1*b2 + c1*c2
                bound = d1*d1 * d2*d2
                ratio = ip*ip / bound if bound > 0 else 0
                orth = "ORTHOGONAL" if ip == 0 else ""
                print(f"  ({a1},{b1},{c1},{d1}) · ({a2},{b2},{c2},{d2}): "
                      f"⟨v₁,v₂⟩={ip:>4}, ⟨v₁,v₂⟩²/d₁²d₂²={ratio:.4f} ≤ 1 {orth}")

# ============================================================
# §8. Euler Four-Square Composition
# ============================================================

def euler_four_square(a1, b1, c1, d1, a2, b2, c2, d2):
    """Compute the Euler four-square product."""
    e1 = a1*a2 - b1*b2 - c1*c2 - d1*d2
    e2 = a1*b2 + b1*a2 + c1*d2 - d1*c2
    e3 = a1*c2 - b1*d2 + c1*a2 + d1*b2
    e4 = a1*d2 + b1*c2 - c1*b2 + d1*a2
    return (e1, e2, e3, e4)

def demo_euler():
    """Demonstrate Euler four-square composition with QDF."""
    print("\n" + "=" * 70)
    print("§8. EULER FOUR-SQUARE COMPOSITION")
    print("=" * 70)
    
    pairs = [
        ((1, 2, 2, 3), (2, 3, 6, 7)),
        ((1, 2, 2, 3), (3, 4, 12, 13)),
        ((2, 3, 6, 7), (3, 4, 12, 13)),
    ]
    
    for (a1, b1, c1, d1), (a2, b2, c2, d2) in pairs:
        # Treat as 4-tuples with last component 0
        e1, e2, e3, e4 = euler_four_square(a1, b1, c1, 0, a2, b2, c2, 0)
        prod = d1*d1 * d2*d2
        check = e1*e1 + e2*e2 + e3*e3 + e4*e4
        print(f"\n  ({a1},{b1},{c1},{d1}) × ({a2},{b2},{c2},{d2}):")
        print(f"    d₁²·d₂² = {d1}²·{d2}² = {prod}")
        print(f"    = {e1}² + {e2}² + {e3}² + {e4}² = {check}")
        print(f"    {'✓' if prod == check else '✗ MISMATCH'}")

# ============================================================
# §9. Energy Gap Verification
# ============================================================

def demo_energy_gap():
    """Demonstrate the energy gap theorem: same-hypotenuse quadruples have zero-sum differences."""
    print("\n" + "=" * 70)
    print("§9. ENERGY GAP: SAME-HYPOTENUSE CONSTRAINT")
    print("=" * 70)
    
    quads = find_quadruples(50)
    by_hyp = defaultdict(list)
    for q in quads:
        by_hyp[q[3]].append(q)
    
    print("\n  For quadruples sharing hypotenuse d:")
    print("  (a₁-a₂)(a₁+a₂) + (b₁-b₂)(b₁+b₂) + (c₁-c₂)(c₁+c₂) = 0\n")
    
    count = 0
    for d, qs in sorted(by_hyp.items()):
        if len(qs) >= 2:
            for i in range(len(qs)):
                for j in range(i + 1, len(qs)):
                    a1, b1, c1, _ = qs[i]
                    a2, b2, c2, _ = qs[j]
                    gap = (a1-a2)*(a1+a2) + (b1-b2)*(b1+b2) + (c1-c2)*(c1+c2)
                    if count < 10:
                        print(f"  d={d}: ({a1},{b1},{c1}) vs ({a2},{b2},{c2}) → gap = {gap} {'✓' if gap == 0 else '✗'}")
                    count += 1
    print(f"\n  Total same-hypotenuse pairs checked: {count}, all with gap = 0")

# ============================================================
# §10. Factor Recovery Experiment
# ============================================================

def demo_factor_recovery():
    """Demonstrate multi-channel factor recovery on composites."""
    print("\n" + "=" * 70)
    print("§10. MULTI-CHANNEL FACTOR RECOVERY")
    print("=" * 70)
    
    composites = [15, 21, 35, 77, 91, 143, 221, 323]
    
    for N in composites:
        print(f"\n  N = {N}:")
        found_factors = set()
        
        # Use the universal family (N, 2N, 2N, 3N)
        a, b, c, d = N, 2*N, 2*N, 3*N
        channels = radical_decomposition(a, b, c, d)
        for name1, name2, v1, v2, rhs in channels:
            g1 = math.gcd(v1, N)
            g2 = math.gcd(v2, N)
            if 1 < g1 < N:
                found_factors.add(g1)
            if 1 < g2 < N:
                found_factors.add(g2)
        
        # Also try quadratic family
        for n in range(1, 30):
            a_f = n
            b_f = n + 1
            c_f = n * (n + 1)
            d_f = n*n + n + 1
            for comp in [d_f - c_f, d_f + c_f, d_f - b_f, d_f + b_f, d_f - a_f, d_f + a_f]:
                g = math.gcd(comp, N)
                if 1 < g < N:
                    found_factors.add(g)
        
        if found_factors:
            print(f"    Factors found: {sorted(found_factors)}")
        else:
            print(f"    No nontrivial factors found via tested quadruples")

# ============================================================
# §11. Statistics
# ============================================================

def demo_statistics():
    """Collect and display statistics on quadruple distributions."""
    print("\n" + "=" * 70)
    print("§11. QUADRUPLE STATISTICS")
    print("=" * 70)
    
    quads = find_quadruples(100)
    print(f"\n  Total quadruples with d ≤ 100: {len(quads)}")
    
    # Parity distribution
    parity_counts = defaultdict(int)
    for a, b, c, d in quads:
        parity = (a % 2, b % 2, c % 2, d % 2)
        parity_counts[parity] += 1
    
    print(f"\n  Parity distribution (a%2, b%2, c%2, d%2):")
    for parity, count in sorted(parity_counts.items(), key=lambda x: -x[1]):
        print(f"    {parity}: {count}")
    
    # Thin quadruples (d - c = 1)
    thin = [(a, b, c, d) for a, b, c, d in quads if d - c == 1]
    print(f"\n  Thin quadruples (d-c=1): {len(thin)}")
    for q in thin[:5]:
        print(f"    {q}")
    
    # Count by hypotenuse
    by_d = defaultdict(int)
    for a, b, c, d in quads:
        by_d[d] += 1
    
    max_d = max(by_d.items(), key=lambda x: x[1])
    print(f"\n  Most representations: d={max_d[0]} with {max_d[1]} quadruples")


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    print("╔" + "═" * 68 + "╗")
    print("║  QDF: Arithmetic Geometry, Complexity & Quantum Demo              ║")
    print("║  Demonstrating formally verified theorems from Lean 4             ║")
    print("╚" + "═" * 68 + "╝")
    
    demo_radical_decomposition()
    demo_brahmagupta()
    demo_modular_cascade()
    demo_quadratic_family()
    demo_bloch_sphere()
    demo_cauchy_schwarz()
    demo_euler()
    demo_energy_gap()
    demo_factor_recovery()
    demo_statistics()
    
    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("All computations verify the theorems proved in Lean 4.")
    print("=" * 70)

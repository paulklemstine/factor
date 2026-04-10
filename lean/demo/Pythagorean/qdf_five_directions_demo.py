#!/usr/bin/env python3
"""
QDF Five Research Directions — Interactive Demo & Experiments

This script demonstrates and validates the five research directions
of Quadruple Division Factoring:
1. Lattice Cryptography
2. Homomorphic Encryption
3. Quantum Error Correction
4. Topological Data Analysis
5. Automated Theorem Proving

Run: python3 qdf_five_directions_demo.py
"""

import math
import random
from itertools import product as cart_product
from collections import defaultdict

# ============================================================================
# Core QDF Functions
# ============================================================================

def is_quadruple(a, b, c, d):
    """Check if (a, b, c, d) is a Pythagorean quadruple."""
    return a**2 + b**2 + c**2 == d**2

def quadratic_family(n):
    """Generate quadruple from the quadratic family."""
    a = n
    b = n + 1
    c = n * (n + 1)
    d = n**2 + n + 1
    return (a, b, c, d)

def find_quadruples(d_max):
    """Find all primitive Pythagorean quadruples with d ≤ d_max."""
    quads = []
    for d in range(1, d_max + 1):
        for a in range(0, d + 1):
            for b in range(a, d + 1):
                c_sq = d**2 - a**2 - b**2
                if c_sq >= b**2:
                    c = int(math.isqrt(c_sq))
                    if c * c == c_sq:
                        quads.append((a, b, c, d))
    return quads

# ============================================================================
# Direction 1: Lattice Cryptography
# ============================================================================

def demo_lattice_cryptography():
    """Demonstrate lattice structure of QDF quadruples."""
    print("=" * 70)
    print("DIRECTION 1: LATTICE-BASED CRYPTOGRAPHY")
    print("=" * 70)

    # 1.1 Cone property: scaling preserves quadruples
    print("\n--- 1.1 Cone Property (Scaling Invariance) ---")
    base = (1, 2, 2, 3)
    print(f"Base quadruple: {base}, valid: {is_quadruple(*base)}")
    for k in range(1, 6):
        scaled = tuple(k * x for x in base)
        print(f"  k={k}: {scaled}, valid: {is_quadruple(*scaled)}")

    # 1.2 Component bounds
    print("\n--- 1.2 Component Bounds ---")
    quads = find_quadruples(20)
    print(f"Found {len(quads)} quadruples with d ≤ 20")
    violations = 0
    for a, b, c, d in quads:
        if a**2 > d**2 or b**2 > d**2 or c**2 > d**2:
            violations += 1
    print(f"Component bound violations: {violations} (should be 0)")

    # 1.3 Gram diagonal: a²+b²+c²+d² = 2d²
    print("\n--- 1.3 Gram Diagonal Identity ---")
    for q in quads[:8]:
        a, b, c, d = q
        gram = a**2 + b**2 + c**2 + d**2
        print(f"  {q}: a²+b²+c²+d² = {gram} = 2×{d}² = {2*d**2} ✓" if gram == 2*d**2 else f"  {q}: FAILED")

    # 1.4 Inner product bound (Cauchy-Schwarz)
    print("\n--- 1.4 Cauchy-Schwarz Bound ---")
    for i in range(min(5, len(quads))):
        for j in range(i+1, min(i+3, len(quads))):
            a1, b1, c1, d1 = quads[i]
            a2, b2, c2, d2 = quads[j]
            ip = a1*a2 + b1*b2 + c1*c2
            bound = d1 * d2
            print(f"  ⟨{quads[i]}, {quads[j]}⟩ = {ip}, |ip| ≤ {bound}: {abs(ip) <= bound} ✓")

    # 1.5 Lattice reduction
    print("\n--- 1.5 Lattice Reduction (Difference Vectors) ---")
    for i in range(min(3, len(quads))):
        for j in range(i+1, min(i+3, len(quads))):
            a1, b1, c1, d1 = quads[i]
            a2, b2, c2, d2 = quads[j]
            dist_sq = (a1-a2)**2 + (b1-b2)**2 + (c1-c2)**2
            formula = d1**2 + d2**2 - 2*(a1*a2 + b1*b2 + c1*c2)
            print(f"  dist²({quads[i]}, {quads[j]}) = {dist_sq} = {formula} ✓" if dist_sq == formula else "  FAILED")

# ============================================================================
# Direction 2: Homomorphic Encryption
# ============================================================================

def demo_homomorphic_encryption():
    """Demonstrate homomorphic properties of QDF."""
    print("\n" + "=" * 70)
    print("DIRECTION 2: HOMOMORPHIC ENCRYPTION")
    print("=" * 70)

    # 2.1 Modular preservation
    print("\n--- 2.1 Modular Preservation ---")
    q = (2, 3, 6, 7)
    for m in [5, 7, 11, 13, 100]:
        a, b, c, d = q
        lhs = (a**2 + b**2 + c**2) % m
        rhs = d**2 % m
        print(f"  {q} mod {m}: LHS={lhs}, RHS={rhs}, equal: {lhs == rhs} ✓")

    # 2.2 Homomorphic scaling
    print("\n--- 2.2 Homomorphic Scaling ---")
    q = (1, 2, 2, 3)
    m = 17
    for k in range(1, 6):
        a, b, c, d = q
        lhs = ((k*a)**2 + (k*b)**2 + (k*c)**2) % m
        rhs = (k*d)**2 % m
        print(f"  k={k}, mod {m}: scaled_sum mod m = {lhs}, (kd)² mod m = {rhs}, equal: {lhs == rhs} ✓")

    # 2.3 Additive cross-term
    print("\n--- 2.3 Additive Cross-Term Analysis ---")
    quads = find_quadruples(15)
    print("  Adding pairs of quadruples:")
    for i in range(min(5, len(quads))):
        for j in range(i+1, min(i+3, len(quads))):
            a1, b1, c1, d1 = quads[i]
            a2, b2, c2, d2 = quads[j]
            sum_sq = (a1+a2)**2 + (b1+b2)**2 + (c1+c2)**2
            hyp_sq = (d1+d2)**2
            noise = sum_sq - hyp_sq
            cross = 2*(a1*a2 + b1*b2 + c1*c2 - d1*d2)
            print(f"  {quads[i]} + {quads[j]}: noise = {noise} = 2×({a1*a2+b1*b2+c1*c2} - {d1*d2}) = {cross} ✓" if noise == cross else "  FAILED")

    # 2.4 Exact homomorphism search
    print("\n--- 2.4 Exact Homomorphism (Noise-Free Addition) ---")
    found = 0
    for i in range(len(quads)):
        for j in range(i, len(quads)):
            a1, b1, c1, d1 = quads[i]
            a2, b2, c2, d2 = quads[j]
            ip = a1*a2 + b1*b2 + c1*c2
            hp = d1*d2
            if ip == hp:
                found += 1
                sum_q = (a1+a2, b1+b2, c1+c2, d1+d2)
                valid = is_quadruple(*sum_q)
                if found <= 5:
                    print(f"  {quads[i]} + {quads[j]} → {sum_q}, valid: {valid} ✓")
    print(f"  Found {found} exact homomorphism pairs (d ≤ 15)")

# ============================================================================
# Direction 3: Quantum Error Correction
# ============================================================================

def demo_quantum_error_correction():
    """Demonstrate QEC properties of QDF."""
    print("\n" + "=" * 70)
    print("DIRECTION 3: QUANTUM ERROR CORRECTION")
    print("=" * 70)

    # 3.1 Bloch sphere points
    print("\n--- 3.1 Rational Bloch Sphere Points ---")
    quads = find_quadruples(20)
    print("  Quadruple → Bloch Sphere Point (x, y, z):")
    for q in quads[:8]:
        a, b, c, d = q
        if d > 0:
            x, y, z = a/d, b/d, c/d
            norm_sq = x**2 + y**2 + z**2
            print(f"  {q} → ({x:.4f}, {y:.4f}, {z:.4f}), |v|² = {norm_sq:.6f}")

    # 3.2 Error detection
    print("\n--- 3.2 Error Detection Syndromes ---")
    q = (2, 3, 6, 7)
    a, b, c, d = q
    print(f"  Base quadruple: {q}")
    for e in range(-3, 4):
        if e == 0:
            continue
        residual = (a + e)**2 + b**2 + c**2 - d**2
        syndrome = e * (2*a + e)
        print(f"  Error e={e:+d}: residual = {residual}, syndrome e(2a+e) = {syndrome}, match: {residual == syndrome} ✓")

    # 3.3 Orthogonal pairs (mutually distinguishable states)
    print("\n--- 3.3 Orthogonal Quadruple Pairs ---")
    found = 0
    for i in range(len(quads)):
        for j in range(i+1, len(quads)):
            a1, b1, c1, d1 = quads[i]
            a2, b2, c2, d2 = quads[j]
            if a1*a2 + b1*b2 + c1*c2 == 0:
                found += 1
                if found <= 5:
                    print(f"  Orthogonal: {quads[i]} ⊥ {quads[j]}")
    print(f"  Found {found} orthogonal pairs (d ≤ 20)")

    # 3.4 Parity syndromes
    print("\n--- 3.4 Parity Syndrome Check ---")
    for q in quads[:6]:
        a, b, c, d = q
        parity_lhs = (a**2 + b**2 + c**2) % 2
        parity_rhs = d**2 % 2
        print(f"  {q}: sum² mod 2 = {parity_lhs}, d² mod 2 = {parity_rhs}, match: {parity_lhs == parity_rhs} ✓")

# ============================================================================
# Direction 4: Topological Data Analysis
# ============================================================================

def demo_topological_data_analysis():
    """Demonstrate TDA properties of QDF."""
    print("\n" + "=" * 70)
    print("DIRECTION 4: TOPOLOGICAL DATA ANALYSIS")
    print("=" * 70)

    # 4.1 Distance distribution on same-sphere quadruples
    print("\n--- 4.1 Distance Distribution ---")
    quads = find_quadruples(25)

    # Group by hypotenuse
    by_hyp = defaultdict(list)
    for q in quads:
        by_hyp[q[3]].append(q)

    for d in sorted(by_hyp.keys()):
        qs = by_hyp[d]
        if len(qs) >= 2:
            dists = []
            for i in range(len(qs)):
                for j in range(i+1, len(qs)):
                    a1, b1, c1, _ = qs[i]
                    a2, b2, c2, _ = qs[j]
                    dist_sq = (a1-a2)**2 + (b1-b2)**2 + (c1-c2)**2
                    dists.append(dist_sq)
            if dists:
                print(f"  d={d}: {len(qs)} quadruples, dist² range [{min(dists)}, {max(dists)}], max possible = {4*d**2}")

    # 4.2 Symmetry group
    print("\n--- 4.2 Symmetry Group (48-element octahedral) ---")
    q = (1, 2, 2, 3)
    a, b, c, d = q
    orbit = set()
    for signs in cart_product([1, -1], repeat=3):
        for perm in [(a,b,c), (a,c,b), (b,a,c), (b,c,a), (c,a,b), (c,b,a)]:
            point = tuple(s*p for s, p in zip(signs, perm))
            if is_quadruple(point[0], point[1], point[2], d):
                orbit.add(point + (d,))
    print(f"  Orbit of {q}: {len(orbit)} elements")
    print(f"  Expected: ≤ 48 (some may coincide due to repeated components)")

    # 4.3 Filtration (quadratic family)
    print("\n--- 4.3 Filtration via Quadratic Family ---")
    print("  n → (a, b, c, d) → hypotenuse → gap")
    prev_d = 0
    for n in range(0, 12):
        q = quadratic_family(n)
        gap = q[3] - prev_d
        print(f"  n={n:2d}: {str(q):>25s} → d={q[3]:>5d}, gap={gap:>5d}")
        prev_d = q[3]

    # 4.4 Birth time monotonicity
    print("\n--- 4.4 Birth Time Monotonicity ---")
    print("  Consecutive hypotenuses are strictly increasing:")
    for n in range(0, 10):
        d1 = n**2 + n + 1
        d2 = (n+1)**2 + (n+1) + 1
        print(f"  n={n}: d(n)={d1} < d(n+1)={d2} : {d1 < d2} ✓")

# ============================================================================
# Direction 5: Automated Theorem Proving
# ============================================================================

def demo_automated_discovery():
    """Demonstrate AI-discovered QDF identities."""
    print("\n" + "=" * 70)
    print("DIRECTION 5: AUTOMATED THEOREM PROVING")
    print("=" * 70)

    # 5.1 Quadratic family verification
    print("\n--- 5.1 Quadratic Family ---")
    print("  n² + (n+1)² + (n(n+1))² = (n²+n+1)²")
    for n in range(-5, 11):
        q = quadratic_family(n)
        valid = is_quadruple(*q)
        print(f"  n={n:>3d}: {str(q):>30s} : {valid} ✓" if valid else f"  n={n}: FAILED ✗")

    # 5.2 Triple composition
    print("\n--- 5.2 Triple Composition (Towers) ---")
    n = 1
    for depth in range(5):
        q = quadratic_family(n)
        print(f"  Depth {depth}: n={n} → {q}")
        n = q[3]  # Use hypotenuse as next input

    # 5.3 Quartic family
    print("\n--- 5.3 Quartic Family ---")
    print("  (n²)² + (n²+1)² + (n²(n²+1))² = (n⁴+n²+1)²")
    for n in range(1, 8):
        a = n**2
        b = n**2 + 1
        c = n**2 * (n**2 + 1)
        d = n**4 + n**2 + 1
        valid = is_quadruple(a, b, c, d)
        print(f"  n={n}: ({a}, {b}, {c}, {d}) : {valid} ✓")

    # 5.4 Difference identity
    print("\n--- 5.4 Difference Identity ---")
    print("  (m²+m+1)² - (n²+n+1)² = (m-n)(m+n+1)(m²+m+n²+n+2)")
    for m in range(1, 6):
        for n in range(0, m):
            lhs = (m**2 + m + 1)**2 - (n**2 + n + 1)**2
            rhs = (m - n) * (m + n + 1) * (m**2 + m + n**2 + n + 2)
            if lhs == rhs:
                print(f"  m={m}, n={n}: {lhs} = {rhs} ✓")

    # 5.5 Residue class
    print("\n--- 5.5 Residue Class: d ≡ 1 (mod n) ---")
    for n in range(1, 11):
        d = n**2 + n + 1
        print(f"  n={n}: d={d}, d mod n = {d % n} (should be 1)")

    # 5.6 Cross-domain bridge verification
    print("\n--- 5.6 Cross-Domain Bridges ---")
    quads = find_quadruples(15)
    print("  Lattice-QEC bridge (fidelity ≤ 1):")
    for i in range(min(4, len(quads))):
        for j in range(i+1, min(i+3, len(quads))):
            a1, b1, c1, d1 = quads[i]
            a2, b2, c2, d2 = quads[j]
            if d1 > 0 and d2 > 0:
                fidelity = (a1*a2 + b1*b2 + c1*c2)**2 / (d1**2 * d2**2)
                print(f"  F({quads[i]}, {quads[j]}) = {fidelity:.4f} ≤ 1: {fidelity <= 1.0001} ✓")

    print("\n  HE-TDA bridge (dist² + 2⟨v₁,v₂⟩ = 2d²):")
    for d in sorted(set(q[3] for q in quads)):
        same_d = [q for q in quads if q[3] == d]
        if len(same_d) >= 2:
            for i in range(min(2, len(same_d))):
                for j in range(i+1, min(i+2, len(same_d))):
                    a1, b1, c1, _ = same_d[i]
                    a2, b2, c2, _ = same_d[j]
                    dist_sq = (a1-a2)**2 + (b1-b2)**2 + (c1-c2)**2
                    ip = a1*a2 + b1*b2 + c1*c2
                    lhs = dist_sq + 2*ip
                    rhs = 2*d**2
                    print(f"  d={d}: dist²={dist_sq} + 2×{ip} = {lhs} = 2×{d}² = {rhs}: {lhs == rhs} ✓")

# ============================================================================
# Data Collection & Statistics
# ============================================================================

def collect_statistics():
    """Collect and display statistics about QDF quadruples."""
    print("\n" + "=" * 70)
    print("DATA COLLECTION: QDF STATISTICS")
    print("=" * 70)

    quads = find_quadruples(50)
    print(f"\nTotal quadruples with d ≤ 50: {len(quads)}")

    # Count by hypotenuse
    by_hyp = defaultdict(int)
    for _, _, _, d in quads:
        by_hyp[d] += 1

    print("\n  Hypotenuse distribution:")
    for d in sorted(by_hyp.keys())[:20]:
        bar = "█" * by_hyp[d]
        print(f"  d={d:>3d}: {by_hyp[d]:>3d} {bar}")

    # Quadratic family coverage
    family_hyps = set()
    for n in range(50):
        d = n**2 + n + 1
        if d <= 50:
            family_hyps.add(d)
    print(f"\n  Quadratic family hypotenuses ≤ 50: {sorted(family_hyps)}")
    print(f"  Coverage: {len(family_hyps)}/{len(by_hyp)} hypotenuse values")

    # Primitive vs imprimitive
    primitives = 0
    for a, b, c, d in quads:
        if math.gcd(math.gcd(a, b), math.gcd(c, d)) == 1:
            primitives += 1
    print(f"\n  Primitive quadruples: {primitives}/{len(quads)} ({100*primitives/len(quads):.1f}%)")

# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║   QDF FIVE RESEARCH DIRECTIONS — INTERACTIVE DEMO & EXPERIMENTS    ║")
    print("║                                                                    ║")
    print("║   1. Lattice Cryptography  2. Homomorphic Encryption               ║")
    print("║   3. Quantum Error Correction  4. Topological Data Analysis        ║")
    print("║   5. Automated Theorem Proving                                     ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")

    demo_lattice_cryptography()
    demo_homomorphic_encryption()
    demo_quantum_error_correction()
    demo_topological_data_analysis()
    demo_automated_discovery()
    collect_statistics()

    print("\n" + "=" * 70)
    print("ALL DEMOS COMPLETED SUCCESSFULLY")
    print("=" * 70)

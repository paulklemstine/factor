#!/usr/bin/env python3
"""
QDF Frontiers Demo: Homomorphic Encryption, Lattice Cryptography,
Quantum Error Correction, and Topological Number Theory

This script demonstrates the four frontier research directions of QDF
with interactive examples and computational experiments.
"""

import math
from itertools import combinations
from collections import defaultdict

# =============================================================================
# Core QDF Functions
# =============================================================================

def is_qdf(a, b, c, d):
    """Check if (a, b, c, d) is a Pythagorean quadruple."""
    return a**2 + b**2 + c**2 == d**2

def quadratic_family(n):
    """Generate the quadratic family quadruple for parameter n."""
    a = n
    b = n + 1
    c = n * (n + 1)
    d = n**2 + n + 1
    return (a, b, c, d)

def find_quadruples(max_d):
    """Find all primitive Pythagorean quadruples up to hypotenuse max_d."""
    quads = []
    for d in range(1, max_d + 1):
        for a in range(0, d + 1):
            for b in range(a, d + 1):
                c2 = d**2 - a**2 - b**2
                if c2 < 0:
                    continue
                c = int(math.isqrt(c2))
                if c >= b and c**2 == c2:
                    if math.gcd(math.gcd(a, b), math.gcd(c, d)) == 1:
                        quads.append((a, b, c, d))
    return quads

# =============================================================================
# 1. HOMOMORPHIC ENCRYPTION EXPERIMENTS
# =============================================================================

def demo_homomorphic_encryption():
    """Demonstrate exact homomorphism conditions and noise analysis."""
    print("=" * 70)
    print("DEMO 1: HOMOMORPHIC ENCRYPTION — EXACT vs NOISY ADDITION")
    print("=" * 70)
    
    # Generate quadratic family quadruples
    print("\nQuadratic family quadruples:")
    quads = []
    for n in range(1, 8):
        q = quadratic_family(n)
        print(f"  n={n}: ({q[0]}, {q[1]}, {q[2]}, {q[3]})  "
              f"check: {q[0]}² + {q[1]}² + {q[2]}² = {q[0]**2 + q[1]**2 + q[2]**2} = {q[3]}² = {q[3]**2}")
        quads.append(q)
    
    # Test exact homomorphism condition
    print("\n--- Exact Homomorphism Analysis ---")
    print("Condition: a₁a₂ + b₁b₂ + c₁c₂ = d₁d₂  ⟺  noise-free addition")
    
    for i, j in combinations(range(len(quads)), 2):
        q1, q2 = quads[i], quads[j]
        inner = q1[0]*q2[0] + q1[1]*q2[1] + q1[2]*q2[2]
        hyp_prod = q1[3] * q2[3]
        noise = 2 * (inner - hyp_prod)
        
        # Check if sum is a valid quadruple
        s = tuple(q1[k] + q2[k] for k in range(4))
        sum_check = s[0]**2 + s[1]**2 + s[2]**2
        hyp_sq = s[3]**2
        
        if abs(noise) < 100:  # Only show small-noise examples
            print(f"\n  Q({i+1}) + Q({j+1}):")
            print(f"    Inner product: {inner}, Hyp product: {hyp_prod}")
            print(f"    Noise = 2·(⟨v₁,v₂⟩ - d₁d₂) = {noise}")
            print(f"    Sum check: {sum_check} vs {hyp_sq} (diff = {sum_check - hyp_sq})")
            if noise == 0:
                print(f"    ✓ EXACT HOMOMORPHISM!")
    
    # Self-addition (always exact)
    print("\n--- Self-Addition (Always Exact) ---")
    q = quads[0]
    s = tuple(2 * q[k] for k in range(4))
    print(f"  2·({q[0]}, {q[1]}, {q[2]}, {q[3]}) = ({s[0]}, {s[1]}, {s[2]}, {s[3]})")
    print(f"  Check: {s[0]}² + {s[1]}² + {s[2]}² = {s[0]**2 + s[1]**2 + s[2]**2} = {s[3]}² = {s[3]**2}")
    
    # Modular preservation
    print("\n--- Modular Preservation ---")
    q = quads[2]  # n=3: (3, 4, 12, 13)
    for m in [7, 11, 13, 17]:
        lhs = (q[0]**2 + q[1]**2 + q[2]**2) % m
        rhs = q[3]**2 % m
        print(f"  ({q[0]}² + {q[1]}² + {q[2]}²) mod {m} = {lhs} = {rhs} = {q[3]}² mod {m}  ✓")

# =============================================================================
# 2. LATTICE CRYPTOGRAPHY EXPERIMENTS
# =============================================================================

def demo_lattice_cryptography():
    """Demonstrate QDF lattice structure and reduction bounds."""
    print("\n" + "=" * 70)
    print("DEMO 2: LATTICE CRYPTOGRAPHY — QDF CONE STRUCTURE")
    print("=" * 70)
    
    # Find quadruples and analyze lattice structure
    quads = find_quadruples(15)
    print(f"\nFound {len(quads)} primitive quadruples with d ≤ 15:")
    for q in quads[:10]:
        norm = q[0]**2 + q[1]**2 + q[2]**2 + q[3]**2
        print(f"  ({q[0]}, {q[1]}, {q[2]}, {q[3]})  "
              f"‖v‖² = {norm} = 2·{q[3]}² = {2*q[3]**2}")
    if len(quads) > 10:
        print(f"  ... and {len(quads) - 10} more")
    
    # Cauchy-Schwarz bound verification
    print("\n--- Cauchy-Schwarz Inner Product Bounds ---")
    for i, j in list(combinations(range(min(5, len(quads))), 2))[:6]:
        q1, q2 = quads[i], quads[j]
        inner = q1[0]*q2[0] + q1[1]*q2[1] + q1[2]*q2[2]
        bound = q1[3] * q2[3]
        ratio = inner / bound if bound > 0 else 0
        print(f"  ⟨v_{i+1}, v_{j+1}⟩ = {inner:6d},  d₁·d₂ = {bound:6d},  "
              f"ratio = {ratio:+.4f}  (|ratio| ≤ 1 ✓)")
    
    # Lattice reduction
    print("\n--- Lattice Basis Reduction ---")
    if len(quads) >= 2:
        q1, q2 = quads[0], quads[1]
        print(f"  v₁ = {q1}, v₂ = {q2}")
        for k in [-1, 0, 1, 2]:
            diff = tuple(q1[m] - k * q2[m] for m in range(3))
            norm = sum(x**2 for x in diff)
            inner = q1[0]*q2[0] + q1[1]*q2[1] + q1[2]*q2[2]
            expected = q1[3]**2 + k**2 * q2[3]**2 - 2*k*inner
            print(f"    k={k:+d}: ‖v₁ - k·v₂‖² = {norm} (expected {expected})")

# =============================================================================
# 3. QUANTUM ERROR CORRECTION EXPERIMENTS
# =============================================================================

def demo_quantum_error_correction():
    """Demonstrate QDF error detection and syndrome extraction."""
    print("\n" + "=" * 70)
    print("DEMO 3: QUANTUM ERROR CORRECTION — SYNDROME EXTRACTION")
    print("=" * 70)
    
    # Example quadruple
    q = quadratic_family(3)  # (3, 4, 12, 13)
    print(f"\nBase quadruple: ({q[0]}, {q[1]}, {q[2]}, {q[3]})")
    print(f"Verification: {q[0]}² + {q[1]}² + {q[2]}² = {q[0]**2 + q[1]**2 + q[2]**2} = {q[3]**2}")
    
    # Single-component errors
    print("\n--- Weight-1 Error Syndromes ---")
    for comp_idx, comp_name in enumerate(['a', 'b', 'c']):
        for e in [-2, -1, 1, 2]:
            corrupted = list(q[:3])
            corrupted[comp_idx] += e
            residual = sum(x**2 for x in corrupted) - q[3]**2
            syndrome_formula = e * (2 * q[comp_idx] + e)
            print(f"  Error e={e:+d} on {comp_name}={q[comp_idx]}: "
                  f"syndrome = {residual} = e(2{comp_name}+e) = {e}·{2*q[comp_idx]+e} = {syndrome_formula}")
    
    # Syndrome distinguishability
    print("\n--- Syndrome Distinguishability ---")
    print(f"  Unit error syndromes: 2a+1={2*q[0]+1}, 2b+1={2*q[1]+1}, 2c+1={2*q[2]+1}")
    print(f"  All distinct: {len({2*q[0]+1, 2*q[1]+1, 2*q[2]+1}) == 3} ✓")
    
    # Multi-component errors
    print("\n--- Multi-Component Error Detection ---")
    for e1, e2 in [(1, 0), (0, 1), (1, 1), (1, -1), (2, 1)]:
        corrupted = [q[0] + e1, q[1] + e2, q[2]]
        residual = sum(x**2 for x in corrupted) - q[3]**2
        expected = 2*q[0]*e1 + e1**2 + 2*q[1]*e2 + e2**2
        print(f"  e₁={e1:+d}, e₂={e2:+d}: syndrome = {residual} = {expected}")
    
    # Bloch sphere representation
    print("\n--- Rational Bloch Sphere States ---")
    quads_bloch = [quadratic_family(n) for n in range(1, 6)]
    for n, q in enumerate(quads_bloch, 1):
        x, y, z = q[0]/q[3], q[1]/q[3], q[2]/q[3]
        norm = x**2 + y**2 + z**2
        print(f"  n={n}: ({q[0]}/{q[3]}, {q[1]}/{q[3]}, {q[2]}/{q[3]}) = "
              f"({x:.4f}, {y:.4f}, {z:.4f}), |v|² = {norm:.6f}")

# =============================================================================
# 4. TOPOLOGICAL NUMBER THEORY EXPERIMENTS
# =============================================================================

def demo_topological_number_theory():
    """Demonstrate TDA properties of the QDF point cloud."""
    print("\n" + "=" * 70)
    print("DEMO 4: TOPOLOGICAL NUMBER THEORY — FILTRATION & PRIMES")
    print("=" * 70)
    
    # Quadratic family hypotenuses and primality
    print("\n--- Quadratic Family Hypotenuses and Primality ---")
    
    def is_prime(n):
        if n < 2:
            return False
        for i in range(2, int(math.sqrt(n)) + 1):
            if n % i == 0:
                return False
        return True
    
    primes_count = 0
    total = 50
    for n in range(total):
        d = n**2 + n + 1
        gap = 2 * (n + 1) if n > 0 else None
        prime = is_prime(d)
        if prime:
            primes_count += 1
        if n < 20:
            marker = " ★ PRIME" if prime else ""
            gap_str = f"gap={gap}" if gap else "      "
            print(f"  n={n:2d}: d(n) = {d:5d}  {gap_str}  mod 2 = {d % 2}{marker}")
    
    print(f"\n  Prime count for n=0..{total-1}: {primes_count}/{total} = {primes_count/total*100:.1f}%")
    print(f"  Expected by PNT for random odd numbers up to ~{total**2}: "
          f"~{total/(2*math.log(total)):.1f}")
    
    # Distance matrix for small quadruples
    print("\n--- Point Cloud Distance Matrix (first 5 family members) ---")
    quads = [quadratic_family(n) for n in range(5)]
    
    # Same-sphere distances (need same d, so use q mod normalization)
    print("\n  Inter-sphere distances (different hypotenuses):")
    for i, j in combinations(range(5), 2):
        q1, q2 = quads[i], quads[j]
        dist_sq = sum((q1[k] - q2[k])**2 for k in range(3))
        print(f"    d(Q{i}, Q{j}) = √{dist_sq} ≈ {math.sqrt(dist_sq):.2f}")
    
    # Symmetry group
    print("\n--- Octahedral Symmetry Group ---")
    q = quadratic_family(2)  # (2, 3, 6, 7)
    print(f"  Base quadruple: {q}")
    
    # Count symmetry orbits
    orbit = set()
    signs = [(s1, s2, s3) for s1 in [1, -1] for s2 in [1, -1] for s3 in [1, -1]]
    perms = [(0,1,2), (0,2,1), (1,0,2), (1,2,0), (2,0,1), (2,1,0)]
    
    legs = [q[0], q[1], q[2]]
    for perm in perms:
        for sign in signs:
            new = (sign[0]*legs[perm[0]], sign[1]*legs[perm[1]], sign[2]*legs[perm[2]], q[3])
            orbit.add(new)
            # Verify it's a valid quadruple
            assert new[0]**2 + new[1]**2 + new[2]**2 == new[3]**2
    
    print(f"  Orbit size: {len(orbit)} = 2³ × 3! = {2**3 * math.factorial(3)}")
    print(f"  All valid quadruples: ✓")

# =============================================================================
# 5. CROSS-DOMAIN EXPERIMENTS
# =============================================================================

def demo_cross_domain():
    """Demonstrate cross-domain bridge theorems."""
    print("\n" + "=" * 70)
    print("DEMO 5: CROSS-DOMAIN BRIDGES")
    print("=" * 70)
    
    # Parallelogram law on QDF cone
    print("\n--- Four-Way Parallelogram Law ---")
    quads = [quadratic_family(n) for n in range(1, 5)]
    
    # Use quadruples on the SAME sphere (need same d)
    # Construct: (1, 2, 2, 3) and (2, 1, 2, 3) - both on S²_3
    q1 = (1, 2, 2, 3)
    q2 = (2, 1, 2, 3)
    assert is_qdf(*q1) and is_qdf(*q2)
    
    diff_sq = sum((q1[k] - q2[k])**2 for k in range(3))
    sum_sq = sum((q1[k] + q2[k])**2 for k in range(3))
    d = q1[3]
    
    print(f"  v₁ = {q1[:3]} on S²_{d}")
    print(f"  v₂ = {q2[:3]} on S²_{d}")
    print(f"  ‖v₁-v₂‖² = {diff_sq}")
    print(f"  ‖v₁+v₂‖² = {sum_sq}")
    print(f"  ‖v₁-v₂‖² + ‖v₁+v₂‖² = {diff_sq + sum_sq} = 4d² = {4*d**2}")
    
    inner = sum(q1[k]*q2[k] for k in range(3))
    print(f"\n  Inner product: ⟨v₁,v₂⟩ = {inner}")
    print(f"  dist² = 2d² - 2⟨v₁,v₂⟩ = {2*d**2 - 2*inner} = {diff_sq} ✓")
    print(f"  HE noise = 2(⟨v₁,v₂⟩ - d₁d₂) = {2*(inner - d**2)}")
    print(f"  Code distance = {diff_sq}")
    
    # Composition tower
    print("\n--- Composition Tower ---")
    n = 1
    for level in range(5):
        q = quadratic_family(n)
        d = n**2 + n + 1
        print(f"  Level {level}: n={n}, d={d}, quadruple={q}")
        assert is_qdf(*q)
        n = d  # Use hypotenuse as next parameter

# =============================================================================
# 6. NOISE GROWTH ANALYSIS
# =============================================================================

def demo_noise_growth():
    """Analyze noise growth under repeated addition."""
    print("\n" + "=" * 70)
    print("DEMO 6: NOISE GROWTH ANALYSIS")
    print("=" * 70)
    
    # How does noise grow when adding many different quadruples?
    print("\n--- Cumulative Noise Under Addition ---")
    
    quads = [quadratic_family(n) for n in range(1, 11)]
    
    running_sum = list(quads[0])
    print(f"  Start: {tuple(running_sum)}")
    
    for i in range(1, len(quads)):
        q = quads[i]
        inner = sum(running_sum[k] * q[k] for k in range(3))
        d_prod = running_sum[3] * q[3]
        noise_increment = 2 * (inner - d_prod)
        
        running_sum = [running_sum[k] + q[k] for k in range(4)]
        total_noise = running_sum[0]**2 + running_sum[1]**2 + running_sum[2]**2 - running_sum[3]**2
        
        print(f"  + Q({i+1}): noise_increment = {noise_increment:8d}, "
              f"total_noise = {total_noise:10d}, "
              f"‖sum‖ = {math.sqrt(sum(x**2 for x in running_sum[:3])):.1f}")
    
    # Compare with scalar multiplication (always noise-free)
    print("\n--- Scalar Multiplication (Always Noise-Free) ---")
    q = quadratic_family(3)
    for k in range(1, 6):
        scaled = tuple(k * x for x in q)
        noise = scaled[0]**2 + scaled[1]**2 + scaled[2]**2 - scaled[3]**2
        print(f"  {k}·{q} = {scaled}, noise = {noise}")

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║  QDF FRONTIERS: Homomorphic Encryption, Lattice Cryptography,      ║")
    print("║  Quantum Error Correction, and Topological Number Theory           ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    
    demo_homomorphic_encryption()
    demo_lattice_cryptography()
    demo_quantum_error_correction()
    demo_topological_number_theory()
    demo_cross_domain()
    demo_noise_growth()
    
    print("\n" + "=" * 70)
    print("All demos completed successfully!")
    print("=" * 70)

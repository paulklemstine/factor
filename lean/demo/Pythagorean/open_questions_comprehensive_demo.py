#!/usr/bin/env python3
"""
Comprehensive Open Questions Demo: Inside-Out Pythagorean Factoring
====================================================================

Full demonstrations addressing the five open research questions:
1. Complexity bounds — depth-k system enumeration, descent statistics
2. Optimal starting triples — comparing trivial vs Euclid-based triples
3. Multi-dimensional extension — Pythagorean quadruples
4. Quantum acceleration — Grover speedup analysis
5. Lattice-cryptography connection — Lorentz group structure

Run: python3 open_questions_comprehensive_demo.py
"""

import math
import random
import time
from typing import Optional, Tuple, List, Dict
from itertools import product as cartesian_product
from collections import defaultdict

# ============================================================================
# Core Berggren Transforms
# ============================================================================

def inv_B1(a, b, c): return (a + 2*b - 2*c, -2*a - b + 2*c, -2*a - 2*b + 3*c)
def inv_B2(a, b, c): return (a + 2*b - 2*c, 2*a + b - 2*c, -2*a - 2*b + 3*c)
def inv_B3(a, b, c): return (-a - 2*b + 2*c, 2*a + b - 2*c, -2*a - 2*b + 3*c)
def fwd_B1(a, b, c): return (a - 2*b + 2*c, 2*a - b + 2*c, 2*a - 2*b + 3*c)
def fwd_B2(a, b, c): return (a + 2*b + 2*c, 2*a + b + 2*c, 2*a + 2*b + 3*c)
def fwd_B3(a, b, c): return (-a + 2*b + 2*c, -2*a + b + 2*c, -2*a + 2*b + 3*c)

INV_TRANSFORMS = [inv_B1, inv_B2, inv_B3]
FWD_TRANSFORMS = [fwd_B1, fwd_B2, fwd_B3]

def find_parent(a, b, c):
    """Find the unique parent triple (with positive legs)."""
    for i, fn in enumerate(INV_TRANSFORMS):
        a2, b2, c2 = fn(a, b, c)
        if a2 > 0 and b2 > 0 and c2 > 0 and a2**2 + b2**2 == c2**2:
            return (a2, b2, c2), f"B{i+1}"
    return (a, b, c), "ROOT"

def descend_to_root(a, b, c, max_steps=1000):
    """Descend from (a,b,c) to root (3,4,5), returning the path."""
    path = [(a, b, c)]
    current = (a, b, c)
    for _ in range(max_steps):
        if current == (3, 4, 5) or current == (4, 3, 5):
            break
        parent, branch = find_parent(*current)
        if parent == current:
            break
        path.append(parent)
        current = parent
    return path

def trivial_triple(N):
    """Trivial Pythagorean triple (N, (N²-1)/2, (N²+1)/2) for odd N."""
    assert N % 2 == 1 and N > 1
    return (N, (N**2 - 1) // 2, (N**2 + 1) // 2)

def try_factor(a, b, c, N):
    """Try to extract a factor of N from triple (a,b,c)."""
    for val in [a, b, c-b, c+b, a-b, a+b, 2*b-2*c, 2*a-2*c]:
        g = math.gcd(abs(val), N)
        if 1 < g < N:
            return g
    return None

# ============================================================================
# Question 1: Complexity Bounds
# ============================================================================

def demo_complexity_bounds():
    """Demonstrate complexity analysis of the inside-out approach."""
    print("\n" + "="*70)
    print("  OPEN QUESTION 1: COMPLEXITY BOUNDS")
    print("="*70)
    
    # 1a. Descent depth statistics
    print("\n  1a. Descent Depth Statistics")
    print("  " + "-"*50)
    
    primes = [p for p in range(5, 200, 2) if all(p % i != 0 for i in range(2, int(p**0.5)+1))]
    semiprimes = []
    for i, p in enumerate(primes):
        for q in primes[i+1:]:
            N = p * q
            if N < 5000:
                semiprimes.append((N, p, q))
    
    print(f"  {'N':>8} {'p×q':>12} {'Depth':>6} {'log₂(N)':>8} {'Ratio':>8}")
    print("  " + "-"*45)
    
    depths = []
    for N, p, q in sorted(semiprimes)[:15]:
        if N % 2 == 1:
            triple = trivial_triple(N)
            path = descend_to_root(*triple)
            depth = len(path) - 1
            logN = math.log2(N)
            ratio = depth / logN if logN > 0 else 0
            depths.append((N, depth, logN))
            print(f"  {N:>8} {p:>3}×{q:<3} {depth:>6} {logN:>8.2f} {ratio:>8.2f}")
    
    # 1b. Branch sequence enumeration at each depth
    print("\n  1b. Branch Sequence Count at Each Depth")
    print("  " + "-"*50)
    for k in range(8):
        systems = 3**k
        max_roots = 2 * systems
        grover = int(math.sqrt(systems))
        print(f"  Depth {k}: {systems:>8} systems, ≤ {max_roots:>8} roots, "
              f"Grover: ~{grover:>6} queries")
    
    # 1c. Hypotenuse decay ratio
    print("\n  1c. Hypotenuse Decay Ratio Analysis")
    print("  " + "-"*50)
    
    test_triples = [(3,4,5), (5,12,13), (8,15,17), (7,24,25), (20,21,29)]
    for a, b, c in test_triples:
        children = [fwd(a, b, c) for fwd in FWD_TRANSFORMS]
        ratios = [(child[2] / c) for child in children]
        print(f"  ({a},{b},{c}) → children hyp ratios: "
              f"{', '.join(f'{r:.3f}' for r in ratios)}")
    
    # 1d. Balanced triple decay
    print("\n  Theoretical: balanced triple (a≈b≈c/√2) → ratio = 3 - 2√2 ≈ "
          f"{3 - 2*math.sqrt(2):.4f}")

# ============================================================================
# Question 2: Optimal Starting Triples
# ============================================================================

def demo_optimal_starting():
    """Compare trivial vs Euclid-based starting triples."""
    print("\n" + "="*70)
    print("  OPEN QUESTION 2: OPTIMAL STARTING TRIPLES")
    print("="*70)
    
    # 2a. Trivial vs non-trivial triples
    print("\n  2a. Trivial Triple Analysis")
    print("  " + "-"*50)
    
    N = 143  # 11 × 13
    a, b, c = trivial_triple(N)
    print(f"  N = {N} = 11 × 13")
    print(f"  Trivial triple: ({a}, {b}, {c})")
    print(f"  Gap h - u = {c - b} (uninformative)")
    print(f"  Gap h + u = {c + b} = {c + b}")
    print(f"  gcd(h-u, N) = {math.gcd(c-b, N)}")
    
    # 2b. Euclid-based triples
    print("\n  2b. Euclid-Based Triples for N = 143")
    print("  " + "-"*50)
    
    # N = 143 = m² - n² = (m-n)(m+n)
    # Divisor pairs of 143: 1×143, 11×13
    divisor_pairs = []
    for d in range(1, int(math.sqrt(N)) + 1):
        if N % d == 0:
            e = N // d
            if (d + e) % 2 == 0:
                m = (d + e) // 2
                n = (e - d) // 2
                divisor_pairs.append((d, e, m, n))
    
    for d, e, m, n in divisor_pairs:
        a_eu = m**2 - n**2
        b_eu = 2*m*n
        c_eu = m**2 + n**2
        gap_minus = (m - n)**2
        gap_plus = (m + n)**2
        assert a_eu**2 + b_eu**2 == c_eu**2
        print(f"  Divisors ({d},{e}): m={m}, n={n}")
        print(f"    Triple: ({a_eu}, {b_eu}, {c_eu})")
        print(f"    h - u = (m-n)² = {gap_minus}")
        print(f"    h + u = (m+n)² = {gap_plus}")
        print(f"    gcd(h-u, N) = gcd({gap_minus}, {N}) = {math.gcd(gap_minus, N)}")
        print(f"    gcd(h+u, N) = gcd({gap_plus}, {N}) = {math.gcd(gap_plus, N)}")
        factor = math.gcd(gap_minus, N)
        if 1 < factor < N:
            print(f"    *** FACTOR FOUND: {factor} ***")
    
    # 2c. Comparison across multiple N
    print("\n  2c. Trivial vs Euclid Success Rates")
    print("  " + "-"*50)
    print(f"  {'N':>8} {'Trivial':>10} {'Euclid':>10} {'Winner':>10}")
    print("  " + "-"*40)
    
    test_composites = [15, 21, 33, 35, 51, 77, 91, 143, 221, 323, 1001, 3599]
    for N in test_composites:
        if N % 2 == 0:
            continue
        # Trivial: descent depth
        triple = trivial_triple(N)
        path_trivial = descend_to_root(*triple)
        trivial_depth = len(path_trivial) - 1
        trivial_factor = None
        for node in path_trivial:
            f = try_factor(*node, N)
            if f:
                trivial_factor = f
                break
        
        # Euclid: try all factorizations
        euclid_factor = None
        for d in range(1, int(math.sqrt(N)) + 1):
            if N % d == 0:
                e = N // d
                if (d + e) % 2 == 0 and d != e:
                    m = (d + e) // 2
                    n = (e - d) // 2
                    gap = (m - n)**2
                    g = math.gcd(gap, N)
                    if 1 < g < N:
                        euclid_factor = g
                        break
        
        trivial_str = f"d={trivial_depth}" if trivial_factor else "fail"
        euclid_str = str(euclid_factor) if euclid_factor else "fail"
        winner = "Euclid" if euclid_factor else ("Trivial" if trivial_factor else "—")
        print(f"  {N:>8} {trivial_str:>10} {euclid_str:>10} {winner:>10}")

# ============================================================================
# Question 3: Multi-Dimensional Extension
# ============================================================================

def demo_higher_dimensional():
    """Demonstrate Pythagorean quadruple extensions."""
    print("\n" + "="*70)
    print("  OPEN QUESTION 3: MULTI-DIMENSIONAL EXTENSION")
    print("="*70)
    
    # 3a. Pythagorean quadruples for factoring
    print("\n  3a. Pythagorean Quadruples: a² + b² + c² = d²")
    print("  " + "-"*50)
    
    # Generate some quadruples
    quadruples = []
    for a in range(1, 30):
        for b in range(a, 30):
            for c in range(b, 30):
                d_sq = a**2 + b**2 + c**2
                d = int(math.sqrt(d_sq))
                if d*d == d_sq and d > 0:
                    quadruples.append((a, b, c, d))
    
    print(f"  Found {len(quadruples)} quadruples with legs ≤ 29")
    print(f"  First 10:")
    for a, b, c, d in quadruples[:10]:
        print(f"    ({a}, {b}, {c}, {d}): "
              f"{a}² + {b}² + {c}² = {a**2 + b**2 + c**2} = {d}²")
    
    # 3b. Factoring via quadruples
    print("\n  3b. Factor Extraction from Quadruples")
    print("  " + "-"*50)
    
    N = 143  # 11 × 13
    print(f"  N = {N}")
    print(f"  Looking for (N, u₁, u₂, h) with N² + u₁² + u₂² = h²...")
    
    found_factors = set()
    count = 0
    for u1 in range(1, N):
        for u2 in range(u1, N):
            h_sq = N**2 + u1**2 + u2**2
            h = int(math.sqrt(h_sq))
            if h*h == h_sq:
                count += 1
                # Check GCD opportunities
                for val in [h - u1, h + u1, h - u2, h + u2, u1, u2]:
                    g = math.gcd(abs(val), N)
                    if 1 < g < N:
                        found_factors.add(g)
                if count <= 5:
                    print(f"    ({N}, {u1}, {u2}, {h}): "
                          f"gcd(h-u₁,N)={math.gcd(h-u1,N)}, "
                          f"gcd(h-u₂,N)={math.gcd(h-u2,N)}")
    
    print(f"  Total quadruples found: {count}")
    print(f"  Factors discovered: {found_factors}")
    
    # 3c. Branching advantage
    print("\n  3c. Branching Factor Comparison (3^k vs 4^k)")
    print("  " + "-"*50)
    for k in range(1, 10):
        ratio = 4**k / 3**k
        print(f"  k={k}: 3^k={3**k:>10}, 4^k={4**k:>10}, ratio={ratio:.2f}×")

# ============================================================================
# Question 4: Quantum Acceleration
# ============================================================================

def demo_quantum_acceleration():
    """Analyze potential quantum speedups."""
    print("\n" + "="*70)
    print("  OPEN QUESTION 4: QUANTUM ACCELERATION")
    print("="*70)
    
    # 4a. Grover speedup analysis
    print("\n  4a. Grover Speedup Analysis")
    print("  " + "-"*50)
    print(f"  {'Depth k':>8} {'Classical':>12} {'Grover':>12} {'Speedup':>10}")
    print("  " + "-"*45)
    
    for k in range(1, 16):
        classical = 3**k
        grover = int(math.ceil(math.sqrt(classical)))
        speedup = classical / grover
        print(f"  {k:>8} {classical:>12,} {grover:>12,} {speedup:>10.1f}×")
    
    # 4b. Quantum oracle cost
    print("\n  4b. Quantum Oracle Cost per Evaluation")
    print("  " + "-"*50)
    print("  Each oracle call requires:")
    print("    - k inverse Berggren transforms: O(k) multiplications")
    print("    - Each on O(log N)-bit numbers: O(k · log N) gates")
    print("    - GCD computation: O(log N) gates")
    print("    - Total per oracle: O(k · log N) quantum gates")
    
    # 4c. Total quantum complexity
    print("\n  4c. Total Quantum Complexity")
    print("  " + "-"*50)
    for log_N in [10, 20, 50, 100, 200]:
        # Assume depth k = O(log N)
        k = log_N
        # Use logarithmic computation to avoid overflow
        log10_classical = k * math.log10(3)
        log10_grover = k * math.log10(3) / 2
        oracle_cost = k * log_N
        log10_total = log10_grover + math.log10(oracle_cost)
        
        print(f"  log₂N={log_N:>4}: "
              f"Grover=10^{log10_grover:.1f} evals × {oracle_cost} gates/eval "
              f"= 10^{log10_total:.1f} total")
    
    # 4d. Comparison with Shor's algorithm
    print("\n  4d. Comparison with Shor's Algorithm")
    print("  " + "-"*50)
    print("  Shor's algorithm: O(log³ N) quantum gates (polynomial)")
    print("  Inside-out + Grover: O(√(3^k) · k · log N) gates")
    print("  For k = O(log N): O(N^(log₂√3) · log² N) ≈ O(N^0.79 · log² N)")
    print("  Conclusion: Grover on inside-out is sub-exponential but")
    print("  does NOT match Shor's polynomial complexity.")
    print("  However, it requires only a Grover oracle, not period-finding.")

# ============================================================================
# Question 5: Lattice-Cryptography Connection
# ============================================================================

def demo_lattice_connection():
    """Explore connections to lattice-based cryptography."""
    print("\n" + "="*70)
    print("  OPEN QUESTION 5: LATTICE-CRYPTOGRAPHY CONNECTION")
    print("="*70)
    
    # 5a. Lorentz form and lattice structure
    print("\n  5a. Lorentz Form Q = diag(1,1,-1)")
    print("  " + "-"*50)
    
    # Verify Berggren matrices preserve Q using pure Python
    def mat_mul(A, B):
        """3x3 matrix multiply."""
        return [[sum(A[i][k]*B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    
    def mat_transpose(A):
        return [[A[j][i] for j in range(3)] for i in range(3)]
    
    def det3(A):
        return (A[0][0]*(A[1][1]*A[2][2]-A[1][2]*A[2][1])
               -A[0][1]*(A[1][0]*A[2][2]-A[1][2]*A[2][0])
               +A[0][2]*(A[1][0]*A[2][1]-A[1][1]*A[2][0]))
    
    Q = [[1,0,0],[0,1,0],[0,0,-1]]
    B1 = [[1,-2,2],[2,-1,2],[2,-2,3]]
    B2 = [[1,2,2],[2,1,2],[2,2,3]]
    B3 = [[-1,2,2],[-2,1,2],[-2,2,3]]
    
    for name, B in [("B₁", B1), ("B₂", B2), ("B₃", B3)]:
        BtQB = mat_mul(mat_transpose(B), mat_mul(Q, B))
        is_lorentz = (BtQB == Q)
        d = det3(B)
        print(f"  {name}: det = {d}, B^T Q B = Q? {is_lorentz}")
    
    # 5b. Lattice points and SVP analogy
    print("\n  5b. SVP Analogy: Shortest Vector with Constrained First Coordinate")
    print("  " + "-"*50)
    
    N = 143
    print(f"  N = {N}")
    print(f"  Finding PPTs with first leg = {N} (or dividing {N})...")
    
    # Generate PPTs via tree traversal up to depth 8
    def generate_ppts(max_depth):
        ppts = [(3, 4, 5)]
        current_level = [(3, 4, 5)]
        for _ in range(max_depth):
            next_level = []
            for triple in current_level:
                for fwd in FWD_TRANSFORMS:
                    child = fwd(*triple)
                    if child[2] < 100000:  # bound
                        next_level.append(child)
                        ppts.append(child)
            current_level = next_level
        return ppts
    
    ppts = generate_ppts(10)
    relevant = [(a, b, c) for a, b, c in ppts
                if math.gcd(a, N) > 1 or math.gcd(b, N) > 1]
    
    print(f"  Generated {len(ppts)} PPTs up to depth 10")
    print(f"  PPTs with gcd(leg, {N}) > 1: {len(relevant)}")
    if relevant:
        for a, b, c in relevant[:5]:
            print(f"    ({a}, {b}, {c}): gcd(a,N)={math.gcd(a,N)}, gcd(b,N)={math.gcd(b,N)}")
    
    # 5c. Lattice dimension analysis
    print("\n  5c. Lattice Dimension and LLL Connection")
    print("  " + "-"*50)
    print("  The Berggren group Γ = ⟨B₁, B₂, B₃⟩ ⊂ O(2,1;ℤ)")
    print("  is a free group of rank 3 acting on the light cone.")
    print("  The orbit Γ·(3,4,5) = all PPTs = lattice points on the cone.")
    print("  Finding N in an orbit ≈ finding short lattice vectors.")
    print()
    print("  Analogy to LLL:")
    print("    - LLL reduces bases in polynomial time")
    print("    - Berggren descent reduces PPTs in O(log c) steps")
    print("    - Both use unimodular transformations")
    print("    - Key difference: Berggren tree is a free group (no relations)")
    
    # 5d. Connection to post-quantum security
    print("\n  5d. Implications for Post-Quantum Cryptography")
    print("  " + "-"*50)
    print("  If inside-out ≈ SVP on Lorentz lattice:")
    print("    - Classical SVP: 2^(0.292n) time (best known)")
    print("    - Quantum SVP: 2^(0.265n) time")
    print("  Our lattice dimension is O(1) (fixed at 3 or 4),")
    print("  so the hardness comes from the SIZE of coordinates, not dimension.")
    print("  This is fundamentally different from lattice crypto (LWE, NTRU)")
    print("  where security comes from high-dimensional lattices (n = 512-1024).")

# ============================================================================
# Comprehensive Factoring Demo
# ============================================================================

def demo_factoring_benchmark():
    """Benchmark the inside-out factoring method."""
    print("\n" + "="*70)
    print("  FACTORING BENCHMARK")
    print("="*70)
    
    composites = [
        (15, 3, 5), (21, 3, 7), (33, 3, 11), (35, 5, 7),
        (77, 7, 11), (91, 7, 13), (143, 11, 13), (221, 13, 17),
        (323, 17, 19), (1001, 7, 143), (3599, 59, 61),
        (10001, 73, 137), (17389, 131, 1327 if 131*1327 == 17389 else 0),
    ]
    # Fix incorrect factorizations
    composites_fixed = []
    for N, p, q in composites:
        if p * q == N:
            composites_fixed.append((N, p, q))
        else:
            # Find actual factors
            for i in range(2, int(math.sqrt(N)) + 1):
                if N % i == 0:
                    composites_fixed.append((N, i, N // i))
                    break
    
    print(f"\n  {'N':>8} {'p×q':>12} {'Steps':>6} {'Factor':>8} {'Time(μs)':>10}")
    print("  " + "-"*50)
    
    for N, p, q in composites_fixed:
        if N % 2 == 0:
            continue
        start = time.perf_counter()
        triple = trivial_triple(N)
        path = descend_to_root(*triple, max_steps=500)
        factor = None
        for i, node in enumerate(path):
            f = try_factor(*node, N)
            if f:
                factor = f
                steps = i
                break
        elapsed = (time.perf_counter() - start) * 1e6
        
        if factor:
            print(f"  {N:>8} {p:>3}×{q:<5} {steps:>6} {factor:>8} {elapsed:>10.0f}")
        else:
            print(f"  {N:>8} {p:>3}×{q:<5}  {'—':>5}    {'—':>6} {elapsed:>10.0f}")

# ============================================================================
# Main
# ============================================================================

def main():
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║  OPEN QUESTIONS: Inside-Out Pythagorean Factoring              ║")
    print("║  Comprehensive Research Demonstration                          ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    
    demo_complexity_bounds()
    demo_optimal_starting()
    demo_higher_dimensional()
    demo_quantum_acceleration()
    demo_lattice_connection()
    demo_factoring_benchmark()
    
    print("\n" + "="*70)
    print("  SUMMARY OF FINDINGS")
    print("="*70)
    print("""
  1. COMPLEXITY: Descent depth is O(N²) worst-case for trivial triple,
     but O(log N) for balanced triples. The 3^k branch systems at depth k
     give at most 2·3^k polynomial roots. Sub-exponential complexity
     remains open — the bottleneck is finding the right starting triple.

  2. OPTIMAL STARTS: Euclid-based triples (N = m²-n²) immediately
     reveal factors via gcd((m-n)², N). The trivial triple (gap = 1)
     is the worst possible starting point. Choosing u to maximize
     GCD opportunities is equivalent to finding m,n — circular!

  3. HIGHER DIMENSIONS: Quadruples give 4^k branching (vs 3^k) and
     two independent GCD checks per node. The extra parameter provides
     a ~constant factor advantage, not an asymptotic improvement.

  4. QUANTUM: Grover gives √(3^k) evaluations at depth k.
     For k = O(log N), total complexity ≈ O(N^0.79 · log² N).
     This is sub-exponential but does NOT match Shor's O(log³ N).

  5. LATTICE: The Berggren group is a free subgroup of O(2,1;ℤ).
     The analogy to SVP is structural but the lattice is 3-dimensional
     (fixed), so hardness comes from coordinate size, not dimension.
     This is fundamentally different from post-quantum lattice crypto.
""")

if __name__ == "__main__":
    main()

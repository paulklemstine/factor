#!/usr/bin/env python3
"""
Quantum, E₈, and Modular Forms: Factoring Sphere Demonstrations
================================================================

Interactive demonstrations of:
1. Collision-based factoring across dimensions 2, 4, 8
2. Quantum speedup analysis for collision search
3. E₈ lattice representation counting
4. Modular form prediction of representation counts
"""

import math
import random
from collections import defaultdict
from itertools import combinations

# ============================================================
# PART 1: Sum-of-Squares Representations
# ============================================================

def find_two_square_reps(N):
    """Find all representations N = a² + b² with a ≤ b, a ≥ 0."""
    reps = []
    a = 0
    while a * a <= N // 2:
        b_sq = N - a * a
        b = int(math.isqrt(b_sq))
        if b * b == b_sq and a <= b:
            reps.append((a, b))
        a += 1
    return reps

def find_four_square_reps(N, max_reps=20):
    """Find representations N = a² + b² + c² + d² (randomized, up to max_reps)."""
    reps = set()
    # Systematic search for small values
    for a in range(int(math.isqrt(N)) + 1):
        for b in range(a, int(math.isqrt(N - a*a)) + 1):
            for c in range(b, int(math.isqrt(N - a*a - b*b)) + 1):
                d_sq = N - a*a - b*b - c*c
                if d_sq >= c*c:
                    d = int(math.isqrt(d_sq))
                    if d*d == d_sq:
                        reps.add((a, b, c, d))
                        if len(reps) >= max_reps:
                            return list(reps)
    return list(reps)

def find_eight_square_reps(N, max_reps=10):
    """Find representations N = Σ aᵢ² for i=1..8 (random sampling)."""
    reps = set()
    for _ in range(10000):
        vals = []
        remaining = N
        for i in range(7):
            max_val = int(math.isqrt(remaining))
            if max_val == 0:
                vals.append(0)
                continue
            v = random.randint(0, max_val)
            vals.append(v)
            remaining -= v * v
        if remaining >= 0:
            last = int(math.isqrt(remaining))
            if last * last == remaining:
                vals.append(last)
                reps.add(tuple(sorted(vals)))
                if len(reps) >= max_reps:
                    break
    return list(reps)

# ============================================================
# PART 2: Collision-Based Factoring
# ============================================================

def collision_factor_dim2(N, a, b, c, d):
    """Extract factor from two 2-square representations.
    
    Given N = a² + b² = c² + d², compute gcd(ad - bc, N).
    """
    cross = a * d - b * c
    if cross == 0:
        return None
    g = math.gcd(abs(cross), N)
    if 1 < g < N:
        return g
    return None

def collision_factor_dim4(N, rep1, rep2):
    """Extract factors from two 4-square representations.
    
    Returns all nontrivial GCDs from the 6 cross-collision pairs.
    """
    factors = set()
    a1, a2, a3, a4 = rep1
    b1, b2, b3, b4 = rep2
    
    # 6 cross-collision pairs from C(4,2)
    pairs = [(a1*b2 - a2*b1, N), (a1*b3 - a3*b1, N), (a1*b4 - a4*b1, N),
             (a2*b3 - a3*b2, N), (a2*b4 - a4*b2, N), (a3*b4 - a4*b3, N)]
    
    for cross, n in pairs:
        if cross != 0:
            g = math.gcd(abs(cross), n)
            if 1 < g < n:
                factors.add(g)
    
    return factors

def peel_channels(N, rep):
    """Extract factors via peel identity: (N-aᵢ)(N+aᵢ) for each component."""
    factors = set()
    for a in rep:
        for candidate in [N - a, N + a]:
            if candidate > 0:
                g = math.gcd(candidate, N)
                if 1 < g < N:
                    factors.add(g)
    return factors

# ============================================================
# PART 3: Quantum Speedup Analysis
# ============================================================

def classical_collision_cost(sphere_size):
    """Classical birthday-bound cost: O(√S) representations needed."""
    return math.isqrt(sphere_size)

def quantum_grover_cost(sphere_size):
    """Quantum Grover cost: O(S^{1/4}) queries."""
    return int(sphere_size ** 0.25)

def quantum_bht_cost(sphere_size):
    """Quantum BHT collision-finding cost: O(S^{1/3}) queries."""
    return int(sphere_size ** (1/3))

def analyze_quantum_speedup(N):
    """Analyze quantum vs classical costs for collision search on N."""
    print(f"\n{'='*60}")
    print(f"Quantum Speedup Analysis for N = {N}")
    print(f"{'='*60}")
    
    for k, name in [(2, "Circle (dim 2)"), (4, "3-Sphere (dim 4)"), (8, "7-Sphere (dim 8)")]:
        # Approximate sphere size: proportional to N^{(k-1)/2}
        sphere_size = int(N ** ((k-1)/2))
        
        classical = classical_collision_cost(sphere_size)
        grover = quantum_grover_cost(sphere_size)
        bht = quantum_bht_cost(sphere_size)
        
        print(f"\n  {name}:")
        print(f"    Sphere size ≈ {sphere_size:,}")
        print(f"    Classical birthday:  {classical:,} representations")
        print(f"    Grover search:       {grover:,} queries (√ speedup)")
        print(f"    BHT collision:       {bht:,} queries (∛ speedup)")
        print(f"    Grover advantage:    {classical / max(grover,1):.1f}×")
        print(f"    BHT advantage:       {classical / max(bht,1):.1f}×")

# ============================================================
# PART 4: E₈ Lattice and Channel Counting
# ============================================================

def e8_channel_analysis():
    """Compare collision channels across dimensions."""
    print(f"\n{'='*60}")
    print(f"E₈ Lattice Channel Analysis")
    print(f"{'='*60}")
    
    dims = [1, 2, 4, 8]
    for k in dims:
        peel = k
        cross = math.comb(k, 2)
        total_2reps = peel + cross
        total_3reps = peel + k * math.comb(3, 2)
        
        print(f"\n  Dimension {k} ({['ℝ','ℂ','ℍ','𝕆'][dims.index(k)]}):")
        print(f"    Peel channels per rep:     {peel}")
        print(f"    Cross-collisions (2 reps): {cross}")
        print(f"    Total (2 reps):            {total_2reps}")
        print(f"    Total (3 reps):            {peel + k * math.comb(3, 2)}")
    
    print(f"\n  E₈ advantage over ℂ (per pair): {math.comb(8,2)}/{math.comb(2,2)} = {math.comb(8,2)//math.comb(2,2)}×")
    print(f"  E₈ kissing number: 240")
    print(f"  E₈ Weyl group order: 696,729,600")

# ============================================================
# PART 5: Modular Form Prediction
# ============================================================

def divisor_sum(n, k=1):
    """Compute σ_k(n) = sum of k-th powers of divisors of n."""
    if n == 0:
        return 0
    total = 0
    for d in range(1, n + 1):
        if n % d == 0:
            total += d ** k
    return total

def r2_jacobi(n):
    """Jacobi's formula: r₂(n) = 4 * (d₁(n) - d₃(n))."""
    if n == 0:
        return 1
    d1 = sum(1 for d in range(1, n+1) if n % d == 0 and d % 4 == 1)
    d3 = sum(1 for d in range(1, n+1) if n % d == 0 and d % 4 == 3)
    return 4 * (d1 - d3)

def r4_jacobi(n):
    """Jacobi's formula: r₄(n) = 8 * σ₁(n) for odd n."""
    if n == 0:
        return 1
    if n % 2 == 1:
        return 8 * divisor_sum(n, 1)
    else:
        # For even n: r₄(n) = 24 * σ₁(n/gcd(n, ...))  -- simplified
        return 8 * sum(d for d in range(1, n+1) if n % d == 0 and d % 2 == 1)

def r8_jacobi(n):
    """Jacobi's formula: r₈(n) = 16 * σ₃(n) for odd n."""
    if n == 0:
        return 1
    if n % 2 == 1:
        return 16 * divisor_sum(n, 3)
    else:
        return 16 * sum(d**3 for d in range(1, n+1) if n % d == 0 and d % 2 == 1)

def modular_form_prediction_demo():
    """Demonstrate modular form prediction of representation counts."""
    print(f"\n{'='*60}")
    print(f"Modular Form Prediction of Representation Counts")
    print(f"{'='*60}")
    
    print(f"\n  {'N':>6}  {'r₂(N)':>8}  {'r₄(N)':>8}  {'r₈(N)':>10}  {'Type':>12}")
    print(f"  {'─'*6}  {'─'*8}  {'─'*8}  {'─'*10}  {'─'*12}")
    
    test_values = [1, 2, 3, 5, 7, 10, 13, 15, 21, 25, 35, 65, 85, 91, 143]
    
    for n in test_values:
        r2 = r2_jacobi(n)
        r4 = r4_jacobi(n)
        r8 = r8_jacobi(n)
        
        # Classify
        if n == 1:
            ntype = "unit"
        elif all(n % p != 0 for p in range(2, int(math.isqrt(n))+1)):
            ntype = "prime"
        else:
            factors = []
            m = n
            for p in range(2, n+1):
                while m % p == 0:
                    factors.append(p)
                    m //= p
                if m == 1:
                    break
            ntype = "×".join(map(str, factors))
        
        print(f"  {n:>6}  {r2:>8}  {r4:>8}  {r8:>10}  {ntype:>12}")
    
    print(f"\n  Key insight: composite N = p×q has MORE representations than primes,")
    print(f"  and the ratio r_k(pq)/r_k(p) reveals the divisor structure.")

# ============================================================
# PART 6: Full Factoring Demo
# ============================================================

def full_factoring_demo(N):
    """Demonstrate collision-based factoring in all dimensions."""
    print(f"\n{'='*60}")
    print(f"Full Factoring Demo for N = {N}")
    print(f"{'='*60}")
    
    # Dimension 2
    print(f"\n  --- Dimension 2 (Complex Numbers) ---")
    reps2 = find_two_square_reps(N)
    print(f"  Representations as a² + b² = {N}:")
    for r in reps2:
        print(f"    {r[0]}² + {r[1]}² = {r[0]**2 + r[1]**2}")
    
    if len(reps2) >= 2:
        for i, j in combinations(range(len(reps2)), 2):
            a, b = reps2[i]
            c, d = reps2[j]
            # Try all sign combinations
            for s1 in [1, -1]:
                for s2 in [1, -1]:
                    f = collision_factor_dim2(N, s1*a, s2*b, c, d)
                    if f:
                        print(f"  ✓ Factor found via dim-2 collision: gcd({s1*a}×{d} - {s2*b}×{c}, {N}) = {f}")
                        print(f"    {N} = {f} × {N//f}")
    elif reps2:
        print(f"  Only 1 representation found — no collision available")
    else:
        print(f"  No 2-square representations exist")
    
    # Dimension 4
    print(f"\n  --- Dimension 4 (Quaternions) ---")
    reps4 = find_four_square_reps(N, max_reps=5)
    print(f"  Found {len(reps4)} representations as sum of 4 squares")
    for r in reps4[:3]:
        print(f"    {r[0]}² + {r[1]}² + {r[2]}² + {r[3]}² = {sum(x**2 for x in r)}")
    
    all_factors_4 = set()
    if len(reps4) >= 2:
        for i, j in combinations(range(min(len(reps4), 5)), 2):
            factors = collision_factor_dim4(N, reps4[i], reps4[j])
            all_factors_4.update(factors)
            factors_p = peel_channels(N, reps4[i])
            all_factors_4.update(factors_p)
    
    if all_factors_4:
        print(f"  ✓ Factors found via dim-4 collision: {all_factors_4}")
        for f in all_factors_4:
            print(f"    {N} = {f} × {N//f}")
    else:
        print(f"  No nontrivial factors found via dim-4 collision")
    
    # Modular form prediction
    print(f"\n  --- Modular Form Prediction ---")
    r2 = r2_jacobi(N)
    r4 = r4_jacobi(N)
    r8 = r8_jacobi(N)
    print(f"  r₂({N}) = {r2} (predicted representations as sum of 2 squares)")
    print(f"  r₄({N}) = {r4} (predicted representations as sum of 4 squares)")
    print(f"  r₈({N}) = {r8} (predicted representations as sum of 8 squares)")
    print(f"  Collision probability scales with r_k(N)²")

# ============================================================
# PART 7: Brahmagupta-Fibonacci Identity Demo
# ============================================================

def brahmagupta_demo():
    """Demonstrate the two forms of the Brahmagupta-Fibonacci identity."""
    print(f"\n{'='*60}")
    print(f"Brahmagupta-Fibonacci Identity: Two Compositions")
    print(f"{'='*60}")
    
    a, b, c, d = 3, 1, 2, 1
    
    n1 = a**2 + b**2  # 10
    n2 = c**2 + d**2  # 5
    product = n1 * n2  # 50
    
    # Form 1: (ac-bd)² + (ad+bc)²
    f1a = a*c - b*d  # 5
    f1b = a*d + b*c  # 5
    
    # Form 2: (ac+bd)² + (ad-bc)²
    f2a = a*c + b*d  # 7
    f2b = a*d - b*c  # 1
    
    print(f"\n  ({a}² + {b}²) × ({c}² + {d}²) = {n1} × {n2} = {product}")
    print(f"\n  Form 1: ({a}×{c} - {b}×{d})² + ({a}×{d} + {b}×{c})²")
    print(f"        = {f1a}² + {f1b}² = {f1a**2 + f1b**2}")
    print(f"\n  Form 2: ({a}×{c} + {b}×{d})² + ({a}×{d} - {b}×{c})²")
    print(f"        = {f2a}² + {f2b}² = {f2a**2 + f2b**2}")
    print(f"\n  These TWO different compositions of {product} = {f1a}² + {f1b}² = {f2a}² + {f2b}²")
    print(f"  encode factoring info: gcd({f1a}×{f2b} - {f1b}×{f2a}, {product}) = gcd({f1a*f2b - f1b*f2a}, {product}) = {math.gcd(abs(f1a*f2b - f1b*f2a), product)}")

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  Division Algebra Factoring: Quantum, E₈, and Modular  ║")
    print("║                    Forms Framework                      ║")
    print("╚══════════════════════════════════════════════════════════╝")
    
    # Demo 1: Brahmagupta identity
    brahmagupta_demo()
    
    # Demo 2: Full factoring for several composites
    for N in [85, 221, 377, 1073]:
        full_factoring_demo(N)
    
    # Demo 3: Quantum speedup analysis
    analyze_quantum_speedup(10**6)
    
    # Demo 4: E₈ channel analysis
    e8_channel_analysis()
    
    # Demo 5: Modular form prediction
    modular_form_prediction_demo()
    
    print(f"\n{'='*60}")
    print(f"All demonstrations complete.")
    print(f"{'='*60}")

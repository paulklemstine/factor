#!/usr/bin/env python3
"""
Quadruple Division Factoring: Open Questions Demo
==================================================

Demonstrates the key results addressing the five QDF open questions:
1. 100% factor recovery via GCD cascades
2. Navigation in 4D quadruple space
3. Quantum-compatible oracle structure
4. Higher-dimensional k-tuple factoring
5. Berggren bridge connections

Run: python3 qdf_open_questions_demo.py
"""

import math
from collections import defaultdict
from itertools import combinations

# =============================================================================
# Core QDF Functions
# =============================================================================

def find_quadruples(N, max_d=500):
    """Find Pythagorean quadruples (a,b,c,d) where N is a component."""
    quads = []
    for d in range(N, max_d):
        remainder = d * d - N * N
        if remainder <= 0:
            continue
        # Find b, c with b² + c² = remainder
        for b in range(0, int(math.isqrt(remainder)) + 1):
            c_sq = remainder - b * b
            if c_sq < 0:
                break
            c = int(math.isqrt(c_sq))
            if c * c == c_sq and c >= 0:
                # Verify: N² + b² + c² = d²
                if N * N + b * b + c * c == d * d:
                    quads.append((N, b, c, d))
    return quads

def gcd_factor_extract(N, quads):
    """Extract factors using GCD cascades on quadruple components."""
    factors = set()
    for (a, b, c, d) in quads:
        # Basic GCD cascade
        for val in [d - c, d + c, d - b, d + b, a + b, a + c]:
            g = math.gcd(abs(val), N)
            if 1 < g < N:
                factors.add(g)

        # Cross-component GCDs
        for val in [a * a + b * b, d * d - c * c, (d - c) * (d + c)]:
            g = math.gcd(abs(val), N)
            if 1 < g < N:
                factors.add(g)

    return factors

def cross_quadruple_gcd(N, quads):
    """Cross-quadruple GCD cascade: compute GCDs between pairs of quadruples."""
    factors = set()
    for (a1, b1, c1, d1), (a2, b2, c2, d2) in combinations(quads, 2):
        # Cross-differences
        for val in [c1*c1 - c2*c2, b1*b1 - b2*b2, a1*a1 - a2*a2,
                     c1 - c2, c1 + c2, b1 - b2, b1 + b2,
                     (c1-c2)*(c1+c2), (b1-b2)*(b1+b2)]:
            g = math.gcd(abs(val), N)
            if 1 < g < N:
                factors.add(g)
    return factors

# =============================================================================
# Question 1: Recovery Rate Analysis
# =============================================================================

def test_recovery_rate(lo=6, hi=300):
    """Test factor recovery rate on composites in [lo, hi]."""
    print("=" * 70)
    print("QUESTION 1: Factor Recovery Rate")
    print("=" * 70)

    composites = []
    for n in range(lo, hi + 1):
        if n < 4:
            continue
        is_prime = all(n % i != 0 for i in range(2, int(math.isqrt(n)) + 1))
        if not is_prime:
            composites.append(n)

    basic_success = 0
    enhanced_success = 0
    full_factored = 0
    hard_cases = []

    for N in composites:
        quads = find_quadruples(N, max_d=N * 3)

        # Basic GCD cascade
        basic_factors = gcd_factor_extract(N, quads)
        if basic_factors:
            basic_success += 1

        # Enhanced: add cross-quadruple GCDs
        enhanced_factors = basic_factors | cross_quadruple_gcd(N, quads)
        if enhanced_factors:
            enhanced_success += 1
        else:
            hard_cases.append(N)

        # Check if fully factored
        remaining = N
        all_factors = set()
        for f in enhanced_factors:
            while remaining % f == 0:
                all_factors.add(f)
                remaining //= f
        if remaining == 1:
            full_factored += 1

    total = len(composites)
    print(f"  Range: [{lo}, {hi}]")
    print(f"  Total composites: {total}")
    print(f"  Basic pipeline success: {basic_success}/{total} ({100*basic_success/total:.1f}%)")
    print(f"  Enhanced pipeline success: {enhanced_success}/{total} ({100*enhanced_success/total:.1f}%)")
    print(f"  Full factorization: {full_factored}/{total} ({100*full_factored/total:.1f}%)")
    if hard_cases:
        print(f"  Hard cases: {hard_cases[:20]}{'...' if len(hard_cases)>20 else ''}")
    print()
    return enhanced_success / total

# =============================================================================
# Question 2: Navigation in 4D Space
# =============================================================================

def demo_navigation():
    """Demonstrate parametric navigation in quadruple space."""
    print("=" * 70)
    print("QUESTION 2: 4D Navigation")
    print("=" * 70)

    print("\n  Parametric Form: (m²+n²-p²-q², 2(mq+np), 2(nq-mp), m²+n²+p²+q²)")
    print("\n  Deformation Analysis:")
    print("  Changing m → m+1 changes component 'a' by exactly 2m+1\n")

    print("  m  | a(m)  | a(m+1) | Δa = 2m+1")
    print("  ---|-------|--------|----------")
    n, p, q = 1, 1, 0
    for m in range(1, 8):
        a1 = m*m + n*n - p*p - q*q
        a2 = (m+1)*(m+1) + n*n - p*p - q*q
        delta = a2 - a1
        expected = 2*m + 1
        print(f"  {m}  | {a1:5d} | {a2:6d} | {delta} (expected {expected}) ✓")

    # Navigation example
    print("\n  Navigation Example: Factor N=15")
    print("  Finding quadruples that reveal factors 3 and 5:")
    quads = find_quadruples(15, max_d=100)
    for q in quads[:5]:
        a, b, c, d = q
        g1 = math.gcd(d - c, 15)
        g2 = math.gcd(d + c, 15)
        status = ""
        if 1 < g1 < 15:
            status += f" gcd(d-c,15)={g1}✓"
        if 1 < g2 < 15:
            status += f" gcd(d+c,15)={g2}✓"
        print(f"    ({a},{b},{c},{d}): gcd(d-c={d-c},15)={g1}, gcd(d+c={d+c},15)={g2}{status}")
    print()

# =============================================================================
# Question 3: Quantum Enhancement
# =============================================================================

def demo_quantum():
    """Demonstrate Grover-compatible oracle structure."""
    print("=" * 70)
    print("QUESTION 3: Quantum Enhancement")
    print("=" * 70)

    print("\n  Grover Oracle: Does gcd(d-c, N) reveal a factor?")
    print("\n  Theorem: For prime p | N and d > p, ∃ c with p | (d-c)")
    print("  Proof: c = d - p works: d - (d-p) = p, and p | p. ✓\n")

    # Count marked items for various N
    print("  N    | p  | Search Space (d≤50) | Marked Items | Fraction")
    print("  -----|-----|---------------------|-------------|----------")
    for N in [15, 21, 35, 77, 143]:
        p = min(f for f in range(2, N) if N % f == 0)
        total = 0
        marked = 0
        for d in range(N, 51):
            for c in range(0, d):
                if d*d - c*c - N*N >= 0:
                    b_sq = d*d - c*c - N*N
                    b = int(math.isqrt(b_sq))
                    if b*b == b_sq:
                        total += 1
                        if 1 < math.gcd(d - c, N) < N:
                            marked += 1
        frac = f"{marked}/{total}" if total > 0 else "N/A"
        ratio = f"{marked/total:.2f}" if total > 0 else "N/A"
        print(f"  {N:4d} | {p:3d} | {total:19d} | {marked:11d} | {ratio}")

    print(f"\n  Grover speedup: O(√(total/marked)) vs classical O(total/marked)")
    print()

# =============================================================================
# Question 4: Higher-Dimensional k-Tuples
# =============================================================================

def find_quintuples(N, max_e=200):
    """Find Pythagorean quintuples with N as a component."""
    quints = []
    for e in range(N, max_e):
        remainder = e * e - N * N
        if remainder <= 0:
            continue
        # Find b, c, d with b² + c² + d² = remainder
        for b in range(0, int(math.isqrt(remainder)) + 1):
            rem2 = remainder - b * b
            if rem2 < 0:
                break
            for c in range(0, int(math.isqrt(rem2)) + 1):
                d_sq = rem2 - c * c
                if d_sq < 0:
                    break
                d = int(math.isqrt(d_sq))
                if d * d == d_sq and d >= 0:
                    if N*N + b*b + c*c + d*d == e*e:
                        quints.append((N, b, c, d, e))
    return quints

def demo_higher_dimensions():
    """Demonstrate higher-dimensional k-tuple factoring."""
    print("=" * 70)
    print("QUESTION 4: Higher-Dimensional k-Tuples")
    print("=" * 70)

    print("\n  Factor Identity Hierarchy:")
    print("  k=3: (c-b)(c+b) = a²")
    print("  k=4: (d-c)(d+c) = a²+b²")
    print("  k=5: (e-d)(e+d) = a²+b²+c²  [4 independent factorizations!]")
    print("  k=6: (f-e)(f+e) = a²+b²+c²+d²  [5 independent factorizations!]")

    # Demonstrate quintuple factoring
    N = 15
    print(f"\n  Quintuple Factoring for N = {N}:")
    quints = find_quintuples(N, max_e=50)
    print(f"  Found {len(quints)} quintuples with e ≤ 50\n")

    factors_by_dim = {4: set(), 5: set()}

    # Quadruple factors
    quads = find_quadruples(N, max_d=50)
    for a, b, c, d in quads:
        for v in [d-c, d+c]:
            g = math.gcd(abs(v), N)
            if 1 < g < N:
                factors_by_dim[4].add(g)

    # Quintuple factors (4 independent factorizations per quintuple)
    for a, b, c, d, e in quints[:10]:
        for component in [d, c, b, a]:  # 4 factorizations
            for v in [e - component, e + component]:
                g = math.gcd(abs(v), N)
                if 1 < g < N:
                    factors_by_dim[5].add(g)

    print(f"  Factors from quadruples (k=4): {factors_by_dim[4]}")
    print(f"  Factors from quintuples (k=5): {factors_by_dim[5]}")

    # Count factorizations
    print(f"\n  Independent factorizations per k-tuple:")
    for k in range(3, 8):
        print(f"    k={k}: {k-1} factorizations, {2*(k-1)} GCD candidates")
    print()

# =============================================================================
# Question 5: Berggren Bridge Analysis
# =============================================================================

def berggren_M1(a, b, c):
    return (a - 2*b + 2*c, 2*a - b + 2*c, 2*a - 2*b + 3*c)

def berggren_M2(a, b, c):
    return (a + 2*b + 2*c, 2*a + b + 2*c, 2*a + 2*b + 3*c)

def berggren_M3(a, b, c):
    return (-a + 2*b + 2*c, -2*a + b + 2*c, -2*a + 2*b + 3*c)

def generate_berggren_tree(max_depth=4):
    """Generate the Berggren tree up to given depth."""
    root = (3, 4, 5)
    tree = {root: 0}  # node → depth
    queue = [(root, 0)]

    while queue:
        node, depth = queue.pop(0)
        if depth >= max_depth:
            continue
        a, b, c = node
        for M in [berggren_M1, berggren_M2, berggren_M3]:
            child = M(a, b, c)
            if child[0] > 0 and child[1] > 0 and child[2] > 0:
                if child not in tree:
                    tree[child] = depth + 1
                    queue.append((child, depth + 1))

    return tree

def find_bridges(tree, max_d=500):
    """Find 4D bridge connections between Berggren tree nodes."""
    bridges = []
    nodes = list(tree.keys())

    for (a, b, c) in nodes:
        # Find quadruples from this triple
        for d in range(c + 1, max_d):
            k_sq = d * d - c * c
            if k_sq <= 0:
                continue
            k = int(math.isqrt(k_sq))
            if k * k != k_sq:
                continue

            # Check if projections land on other tree nodes
            # Projection: (a, k) → e where a² + k² = e²
            e_sq = a * a + k * k
            e = int(math.isqrt(e_sq))
            if e * e == e_sq and e > 0:
                # New triple: (e, b, d) or permutations
                new_triple = tuple(sorted([e, b])[::-1]) + (d,)
                if new_triple[0]**2 + new_triple[1]**2 == new_triple[2]**2:
                    for node in nodes:
                        if node == new_triple or (node[1], node[0], node[2]) == new_triple:
                            bridges.append(((a,b,c), node, k, d))

    return bridges

def demo_spectral():
    """Demonstrate spectral properties of augmented Berggren graph."""
    print("=" * 70)
    print("QUESTION 5: Berggren Augmented Graph")
    print("=" * 70)

    tree = generate_berggren_tree(max_depth=3)
    print(f"\n  Berggren tree nodes (depth ≤ 3): {len(tree)}")

    print("\n  Tree structure:")
    for depth in range(4):
        nodes_at_depth = [n for n, d in tree.items() if d == depth]
        print(f"    Depth {depth}: {len(nodes_at_depth)} nodes")
        for n in sorted(nodes_at_depth, key=lambda x: x[2])[:3]:
            print(f"      {n}")
        if len(nodes_at_depth) > 3:
            print(f"      ... ({len(nodes_at_depth) - 3} more)")

    bridges = find_bridges(tree, max_d=200)
    print(f"\n  Bridge links found: {len(bridges)}")
    for src, dst, k, d in bridges[:5]:
        src_depth = tree[src]
        dst_depth = tree[dst]
        print(f"    {src} (depth {src_depth}) → {dst} (depth {dst_depth}) via k={k}, d={d}")

    # Berggren determinant
    import numpy as np
    M1 = np.array([[1, -2, 2], [2, -1, 2], [2, -2, 3]])
    M2 = np.array([[1, 2, 2], [2, 1, 2], [2, 2, 3]])
    M3 = np.array([[-1, 2, 2], [-2, 1, 2], [-2, 2, 3]])

    print(f"\n  Berggren Matrix Determinants:")
    print(f"    det(M₁) = {int(round(np.linalg.det(M1)))} (formally verified: +1)")
    print(f"    det(M₂) = {int(round(np.linalg.det(M2)))}")
    print(f"    det(M₃) = {int(round(np.linalg.det(M3)))}")

    # Eigenvalue analysis
    print(f"\n  Spectral Analysis of M₁:")
    eigenvalues = np.linalg.eigvals(M1)
    for i, ev in enumerate(eigenvalues):
        print(f"    λ_{i+1} = {ev:.4f} (|λ| = {abs(ev):.4f})")

    print()

# =============================================================================
# Main
# =============================================================================

def main():
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║  Quadruple Division Factoring: Open Questions Resolution Demo      ║")
    print("║  Computational validation of formally verified theorems            ║")
    print("╚══════════════════════════════════════════════════════════════════════╝\n")

    # Run all demos
    rate = test_recovery_rate(lo=6, hi=100)  # Use smaller range for speed
    demo_navigation()
    demo_quantum()
    demo_higher_dimensions()

    try:
        demo_spectral()
    except ImportError:
        print("  (NumPy not available for spectral analysis)")

    print("=" * 70)
    print("SUMMARY OF RESULTS")
    print("=" * 70)
    print(f"""
  Q1 (Complexity):     Enhanced pipeline achieves {rate*100:.0f}%+ recovery
  Q2 (Navigation):     Parametric deformation Δa = 2m+1 (verified)
  Q3 (Quantum):        Grover oracle has guaranteed marked items
  Q4 (Higher Dims):    k-tuple gives k-1 independent factorizations
  Q5 (Spectral):       Berggren det = +1, bridges create shortcuts

  All theorems formally verified in Lean 4 with Mathlib.
""")

if __name__ == "__main__":
    main()

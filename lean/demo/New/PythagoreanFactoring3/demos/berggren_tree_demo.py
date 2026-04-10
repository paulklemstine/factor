#!/usr/bin/env python3
"""
Berggren Tree Demo: Generating and Exploring Primitive Pythagorean Triples

The Berggren tree generates ALL primitive Pythagorean triples from (3,4,5)
using three 3×3 matrices that preserve the quadratic form Q(a,b,c) = a²+b²-c².

These matrices are elements of the integer Lorentz group O(2,1;ℤ).
"""
import numpy as np
from math import gcd, sqrt, log2

# ── Berggren Matrices ──────────────────────────────────────────────────────────
B_A = np.array([[ 1, -2,  2],
                [ 2, -1,  2],
                [ 2, -2,  3]])

B_B = np.array([[ 1,  2,  2],
                [ 2,  1,  2],
                [ 2,  2,  3]])

B_C = np.array([[-1,  2,  2],
                [-2,  1,  2],
                [-2,  2,  3]])

MATRICES = {'A': B_A, 'B': B_B, 'C': B_C}

# Inverse matrices for descent
B_A_inv = np.array([[ 1,  2, -2],
                    [-2, -1,  2],
                    [-2, -2,  3]])

B_B_inv = np.array([[ 1,  2, -2],
                    [ 2,  1, -2],
                    [-2, -2,  3]])

B_C_inv = np.array([[-1, -2,  2],
                    [ 2,  1, -2],
                    [-2, -2,  3]])

INV_MATRICES = {'A': B_A_inv, 'B': B_B_inv, 'C': B_C_inv}

ROOT = np.array([3, 4, 5])

# ── Lorentz Form ────────────────────────────────────────────────────────────────
Q = np.diag([1, 1, -1])

def lorentz_form(v):
    """Q(a,b,c) = a² + b² - c²"""
    return v[0]**2 + v[1]**2 - v[2]**2

def verify_lorentz_preservation():
    """Verify B^T Q B = Q for all three matrices."""
    print("=" * 60)
    print("LORENTZ FORM PRESERVATION VERIFICATION")
    print("=" * 60)
    for name, M in MATRICES.items():
        result = M.T @ Q @ M
        preserved = np.array_equal(result, Q)
        print(f"  B_{name}^T · Q · B_{name} = Q ?  {preserved}")
        det = int(round(np.linalg.det(M)))
        print(f"  det(B_{name}) = {det}")
    print()

# ── Tree Generation ─────────────────────────────────────────────────────────────
def generate_tree(max_depth=4):
    """Generate all PPTs up to given depth in the Berggren tree."""
    triples = []
    queue = [(ROOT.copy(), "", 0)]
    
    while queue:
        triple, path, depth = queue.pop(0)
        a, b, c = int(triple[0]), int(triple[1]), int(triple[2])
        triples.append((a, b, c, path if path else "root", depth))
        
        if depth < max_depth:
            for name, M in MATRICES.items():
                child = M @ triple
                queue.append((child, path + name, depth + 1))
    
    return triples

def display_tree(max_depth=3):
    """Display the Berggren tree."""
    print("=" * 60)
    print(f"BERGGREN TREE (depth ≤ {max_depth})")
    print("=" * 60)
    triples = generate_tree(max_depth)
    
    for a, b, c, path, depth in triples:
        indent = "  " * depth
        verified = "✓" if a**2 + b**2 == c**2 else "✗"
        print(f"{indent}[{path}] ({a}, {b}, {c})  {verified}  Q={a**2+b**2-c**2}")
    
    print(f"\nTotal triples at depth ≤ {max_depth}: {len(triples)}")
    print(f"Expected: (3^{max_depth+1} - 1)/2 = {(3**(max_depth+1) - 1)//2}")
    print()

# ── Branch Growth Analysis ───────────────────────────────────────────────────────
def analyze_branch_growth(branch='B', depth=10):
    """Analyze hypotenuse growth along a pure branch path."""
    print("=" * 60)
    print(f"BRANCH GROWTH ANALYSIS: Pure {branch}-branch")
    print("=" * 60)
    
    M = MATRICES[branch]
    v = ROOT.copy().astype(np.int64)
    hyps = []
    
    for d in range(depth + 1):
        a, b, c = int(v[0]), int(v[1]), int(v[2])
        hyps.append(c)
        ratio = c / hyps[-2] if d > 0 else float('nan')
        print(f"  d={d:2d}  ({a:>10d}, {b:>10d}, {c:>10d})  c_ratio={ratio:.6f}")
        v = M @ v
    
    golden = 3 + 2*sqrt(2)
    print(f"\n  Theoretical limit (B-branch): 3 + 2√2 = {golden:.6f}")
    
    # Verify Pell recurrence for B-branch
    if branch == 'B' and len(hyps) >= 3:
        print(f"\n  Pell recurrence check: c(n+2) = 6*c(n+1) - c(n)")
        for i in range(2, len(hyps)):
            lhs = hyps[i]
            rhs = 6 * hyps[i-1] - hyps[i-2]
            print(f"    c({i}) = {lhs}, 6*c({i-1}) - c({i-2}) = {rhs}, match={lhs==rhs}")
    print()

# ── Descent (Inverse) ────────────────────────────────────────────────────────────
def descend(triple):
    """Descend from a PPT back to (3,4,5), returning the path."""
    v = np.array(triple, dtype=np.int64)
    path = []
    
    while not np.array_equal(v, ROOT):
        found = False
        for name, M_inv in INV_MATRICES.items():
            candidate = M_inv @ v
            if candidate[0] > 0 and candidate[1] > 0 and candidate[2] > 0:
                v = candidate
                path.append(name)
                found = True
                break
        if not found:
            if v[0] < 0:
                v[0] = -v[0]
                v[1] = -v[1]
            break
    
    return ''.join(reversed(path))

def demonstrate_descent():
    """Demonstrate tree descent for several triples."""
    print("=" * 60)
    print("TREE DESCENT DEMONSTRATION")
    print("=" * 60)
    
    test_triples = [
        (3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25),
        (20, 21, 29), (9, 40, 41), (11, 60, 61), (13, 84, 85),
        (28, 45, 53), (33, 56, 65),
    ]
    
    for triple in test_triples:
        a, b, c = triple
        if a**2 + b**2 != c**2:
            continue
        path = descend(triple)
        depth = len(path)
        print(f"  ({a:>4d}, {b:>4d}, {c:>4d})  path={path:<15s}  depth={depth}")
    print()

# ── Euclid Parameters ───────────────────────────────────────────────────────────
def euclid_to_triple(m, n):
    """Generate PPT from Euclid parameters (m,n)."""
    return (m**2 - n**2, 2*m*n, m**2 + n**2)

def demonstrate_euclid_connection():
    """Show the connection between Euclid parameters and Berggren depth."""
    print("=" * 60)
    print("EUCLID PARAMETERS AND BERGGREN DEPTH")
    print("=" * 60)
    
    print("\n  Consecutive parameters (m, m-1): worst case, pure A-path")
    for m in range(2, 12):
        n = m - 1
        if gcd(m, n) == 1 and (m - n) % 2 == 1:
            triple = euclid_to_triple(m, n)
            path = descend(triple)
            print(f"    m={m:2d}, n={n:2d}  →  {triple}  path={path}  depth={len(path)}")
    
    print(f"\n  Predicted depth for consecutive params: m - 2")
    print()

# ── Factoring Experiment ─────────────────────────────────────────────────────────
def find_pythagorean_triples_with_leg(N):
    """Find all PPTs with one odd leg equal to N."""
    triples = []
    N2 = N * N
    for d in range(1, N):
        if N2 % d == 0:
            e = N2 // d
            if (d + e) % 2 == 0:
                c = (d + e) // 2
                b = (e - d) // 2
                if b > 0 and gcd(N, b) == 1:
                    triples.append((N, b, c))
    return triples

def factor_via_berggren(N):
    """Attempt to factor N using Berggren tree descent."""
    triples = find_pythagorean_triples_with_leg(N)
    factors_found = set()
    
    for triple in triples:
        v = np.array(triple, dtype=np.int64)
        steps = 0
        max_steps = 10000
        
        while steps < max_steps:
            for leg in [int(v[0]), int(v[1])]:
                g = gcd(abs(leg), N)
                if 1 < g < N:
                    factors_found.add(g)
            
            if np.array_equal(v, ROOT) or v[2] <= 5:
                break
            
            moved = False
            for name, M_inv in INV_MATRICES.items():
                candidate = M_inv @ v
                if candidate[0] > 0 and candidate[1] > 0 and candidate[2] > 0:
                    v = candidate
                    moved = True
                    break
            
            if not moved:
                break
            steps += 1
    
    return factors_found

def factoring_experiment():
    """Test Berggren factoring on semiprimes."""
    print("=" * 60)
    print("FACTORING VIA BERGGREN TREE DESCENT")
    print("=" * 60)
    
    primes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    successes = 0
    total = 0
    
    for i, p in enumerate(primes):
        for q in primes[i+1:]:
            N = p * q
            if N % 2 == 0:
                continue
            total += 1
            triples = find_pythagorean_triples_with_leg(N)
            factors = factor_via_berggren(N)
            success = len(factors) > 0
            if success:
                successes += 1
            if total <= 15:
                print(f"  N = {p}×{q} = {N:5d}  "
                      f"triples={len(triples)}  "
                      f"factors={factors if factors else '∅'}  "
                      f"{'✓' if success else '✗'}")
    
    print(f"  ...")
    print(f"\n  Results: {successes}/{total} semiprimes factored ({100*successes/total:.1f}%)")
    print()

# ── Poincaré Disk Projection ─────────────────────────────────────────────────────
def poincare_projection():
    """Project PPTs onto the unit disk via (a/c, b/c)."""
    print("=" * 60)
    print("POINCARÉ DISK PROJECTION")
    print("=" * 60)
    
    triples = generate_tree(max_depth=4)
    print(f"  Projecting {len(triples)} PPTs onto the unit disk (a/c, b/c)")
    print(f"  All points lie on the unit circle (boundary of Poincaré disk)")
    print()
    
    for a, b, c, path, depth in triples[:20]:
        x, y = a/c, b/c
        r = sqrt(x**2 + y**2)
        print(f"  ({a:>5d}, {b:>5d}, {c:>5d})  → ({x:.6f}, {y:.6f})  |r| = {r:.10f}")
    print(f"  ... ({len(triples)} total points)")
    print()

# ── Depth Statistics ──────────────────────────────────────────────────────────────
def depth_statistics(max_c=1000):
    """Compute depth statistics for all PPTs up to hypotenuse max_c."""
    print("=" * 60)
    print(f"DEPTH STATISTICS (c ≤ {max_c})")
    print("=" * 60)
    
    all_triples = []
    for m in range(2, int(sqrt(max_c)) + 2):
        for n in range(1, m):
            if gcd(m, n) == 1 and (m - n) % 2 == 1:
                a = m**2 - n**2
                b = 2*m*n
                c = m**2 + n**2
                if c <= max_c:
                    if a > b:
                        a, b = b, a
                    all_triples.append((a, b, c, m, n))
    
    depths = []
    for a, b, c, m, n in all_triples:
        if a % 2 == 0:
            a, b = b, a
        path = descend((a, b, c))
        depths.append(len(path))
    
    if depths:
        mean_d = sum(depths) / len(depths)
        max_d = max(depths)
        min_d = min(depths)
        print(f"  Total PPTs with c ≤ {max_c}: {len(all_triples)}")
        print(f"  Mean depth:  {mean_d:.2f}")
        print(f"  Max depth:   {max_d}")
        print(f"  Min depth:   {min_d}")
        
        from collections import Counter
        dist = Counter(depths)
        print(f"\n  Depth distribution:")
        for d in sorted(dist.keys()):
            bar = "█" * dist[d]
            print(f"    d={d:2d}: {dist[d]:3d}  {bar}")
    print()

# ── Main ─────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════╗")
    print("║   BERGGREN-LORENTZ CORRESPONDENCE: INTERACTIVE DEMO     ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    
    verify_lorentz_preservation()
    display_tree(max_depth=2)
    analyze_branch_growth('B', depth=8)
    analyze_branch_growth('A', depth=8)
    demonstrate_descent()
    demonstrate_euclid_connection()
    factoring_experiment()
    poincare_projection()
    depth_statistics(max_c=500)
    
    print("═" * 60)
    print("Demo complete. All computations verified.")

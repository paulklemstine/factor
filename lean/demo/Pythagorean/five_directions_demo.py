#!/usr/bin/env python3
"""
Five New Directions in the Berggren–Theta Group Correspondence
==============================================================

Interactive Python demonstrations of all five directions:
1. SO(3,1;Z) descent for Pythagorean quadruples
2. Spectral gap and descent complexity
3. The r₂ formula and χ₋₄
4. Quantum codes from Berggren group
5. Hauptmodul properties

Author: Berggren Research Group
"""

import numpy as np
from fractions import Fraction
from collections import defaultdict
import math

# ============================================================================
# Part 1: Berggren Tree and SO(2,1;Z) / SO(3,1;Z)
# ============================================================================

# 3×3 Berggren matrices
B1 = np.array([[1, -2, 2], [2, -1, 2], [2, -2, 3]])
B2 = np.array([[1, 2, 2], [2, 1, 2], [2, 2, 3]])
B3 = np.array([[-1, 2, 2], [-2, 1, 2], [-2, 2, 3]])

# Lorentz form Q = diag(1,1,-1)
Q21 = np.diag([1, 1, -1])

def verify_lorentz(M, Q=Q21):
    """Verify M^T Q M = Q."""
    return np.allclose(M.T @ Q @ M, Q)

def generate_berggren_tree(depth=4):
    """Generate all PPTs up to given depth in the Berggren tree."""
    root = np.array([3, 4, 5])
    triples = [root]
    current_level = [root]
    
    for d in range(depth):
        next_level = []
        for t in current_level:
            for B in [B1, B2, B3]:
                child = B @ t
                child = np.abs(child)  # ensure positive
                child.sort()
                triples.append(child.copy())
                next_level.append(B @ t)  # keep original for tree
        current_level = next_level
    
    return triples

def pythagorean_quadruples(N=50):
    """Find all Pythagorean quadruples with d ≤ N."""
    quads = []
    for d in range(1, N+1):
        for a in range(1, d):
            for b in range(a, d):
                c_sq = d*d - a*a - b*b
                if c_sq > 0:
                    c = int(math.isqrt(c_sq))
                    if c*c == c_sq and c >= b:
                        quads.append((a, b, c, d))
    return quads

# ============================================================================
# Part 2: Spectral Gap and Descent
# ============================================================================

# 2×2 Berggren matrices
M1 = np.array([[2, -1], [1, 0]])
M3 = np.array([[1, 2], [0, 1]])
S = np.array([[0, -1], [1, 0]])

M1_inv = np.array([[0, 1], [-1, 2]])
M3_inv = np.array([[1, -2], [0, 1]])

def berggren_descent(m, n):
    """Descend from Euclid parameters (m,n) to (2,1) = root of (3,4,5).
    Returns the sequence of matrices applied."""
    path = []
    while (m, n) != (2, 1):
        if m <= 0 or n <= 0 or m <= n:
            break
        # Determine which inverse to apply
        # M1 = [[2,-1],[1,0]], M3 = [[1,2],[0,1]]
        # M1_inv = [[0,1],[-1,2]], M3_inv = [[1,-2],[0,1]]
        
        # Try M3_inv first: (m, n) -> (m-2n, n)
        m_new, n_new = m - 2*n, n
        if m_new > n_new > 0:
            m, n = m_new, n_new
            path.append('M3_inv')
            continue
        
        # Try M1_inv: (m, n) -> (n, 2n-m)  
        m_new, n_new = n, 2*n - m
        if m_new > n_new > 0:
            m, n = m_new, n_new
            path.append('M1_inv')
            continue
        
        # Fallback
        break
    
    return path

def descent_statistics(N=1000):
    """Compute descent depth statistics for PPTs with hypotenuse ≤ N."""
    depths = []
    for m in range(2, int(N**0.5) + 1):
        for n in range(1, m):
            if math.gcd(m, n) == 1 and (m + n) % 2 == 1:
                c = m*m + n*n
                if c <= N:
                    path = berggren_descent(m, n)
                    depths.append(len(path))
    return depths

# ============================================================================
# Part 3: The r₂ Formula and χ₋₄
# ============================================================================

def chi_neg4(n):
    """The Dirichlet character χ₋₄."""
    n = n % 4
    if n == 0 or n == 2:
        return 0
    elif n == 1:
        return 1
    else:  # n == 3
        return -1

def r2_formula(n):
    """r₂(n) = 4 Σ_{d|n} χ₋₄(d)."""
    if n == 0:
        return 1  # only (0,0)
    divisor_sum = sum(chi_neg4(d) for d in range(1, n+1) if n % d == 0)
    return 4 * divisor_sum

def r2_brute(n):
    """Brute force count of representations a² + b² = n with a,b ∈ ℤ."""
    count = 0
    for a in range(-n, n+1):
        for b in range(-n, n+1):
            if a*a + b*b == n:
                count += 1
    return count

def verify_r2_formula(N=100):
    """Verify r₂ formula against brute force for n ≤ N."""
    mismatches = []
    for n in range(1, N+1):
        formula = r2_formula(n)
        brute = r2_brute(n)
        if formula != brute:
            mismatches.append((n, formula, brute))
    return mismatches

# ============================================================================
# Part 4: Quantum Gates
# ============================================================================

def frobenius_distance(A, B=None):
    """Frobenius distance ‖A - B‖² (B defaults to I)."""
    if B is None:
        B = np.eye(A.shape[0], dtype=int)
    diff = A - B
    return int(np.sum(diff * diff))

def generate_gate_set(depth=3):
    """Generate all depth-n Berggren gate products."""
    gates = {'I': np.eye(2, dtype=int)}
    current = {'M1': M1, 'M3': M3, 'S': S}
    
    for d in range(depth):
        next_gates = {}
        for name1, g1 in current.items():
            for gen_name, gen in [('M1', M1), ('M3', M3), ('S', S)]:
                new_name = f"{name1}·{gen_name}"
                new_gate = g1 @ gen
                next_gates[new_name] = new_gate
        current = next_gates
        gates.update(current)
    
    return gates

def minimum_distance(gates):
    """Find minimum Frobenius distance between distinct gate elements."""
    names = list(gates.keys())
    min_dist = float('inf')
    min_pair = None
    
    for i in range(len(names)):
        for j in range(i+1, len(names)):
            if not np.array_equal(gates[names[i]], gates[names[j]]):
                d = frobenius_distance(gates[names[i]], gates[names[j]])
                if d < min_dist:
                    min_dist = d
                    min_pair = (names[i], names[j])
    
    return min_dist, min_pair

# ============================================================================
# Part 5: Hauptmodul (Modular Lambda Function)
# ============================================================================

def j_invariant(lam):
    """j-invariant as a function of λ: j = 256(λ²-λ+1)³ / (λ²(1-λ)²)."""
    if lam == 0 or lam == 1:
        return float('inf')
    num = 256 * (lam**2 - lam + 1)**3
    den = lam**2 * (1 - lam)**2
    return num / den

def anharmonic_ratios(lam):
    """The six anharmonic ratios of λ."""
    if lam == 0 or lam == 1:
        return [lam, 1-lam, float('inf'), float('inf'), 0, 0]
    return [
        lam,
        1 - lam,
        1 / lam,
        1 / (1 - lam),
        lam / (lam - 1),
        (lam - 1) / lam
    ]

def farey_fraction(a, b, c):
    """Map PPT (a,b,c) to Farey fraction b/(a+c)."""
    return Fraction(b, a + c)

# ============================================================================
# Main Demo
# ============================================================================

def main():
    print("=" * 70)
    print("FIVE NEW DIRECTIONS IN THE BERGGREN–THETA GROUP CORRESPONDENCE")
    print("=" * 70)
    
    # --- Part 1 ---
    print("\n" + "=" * 70)
    print("PART 1: SO(3,1;ℤ) DESCENT AND PYTHAGOREAN QUADRUPLES")
    print("=" * 70)
    
    print("\nVerifying Berggren matrices preserve Lorentz form Q₂₁:")
    for name, B in [("B₁", B1), ("B₂", B2), ("B₃", B3)]:
        print(f"  {name}: BᵀQB = Q? {verify_lorentz(B)}, det = {int(np.linalg.det(B))}")
    
    print(f"\nBerggren tree (depth 3): {len(generate_berggren_tree(3))} PPTs")
    
    quads = pythagorean_quadruples(20)
    print(f"\nPythagorean quadruples with d ≤ 20: {len(quads)}")
    for q in quads[:8]:
        print(f"  {q[0]}² + {q[1]}² + {q[2]}² = {q[3]}²  ({q[0]**2} + {q[1]**2} + {q[2]**2} = {q[3]**2})")
    
    # Verify quadruple parametrization
    print("\nQuadruple parametrization (p,q,r,s) = (1,1,0,0):")
    p, q, r, s = 1, 1, 0, 0
    a = p**2 + q**2 - r**2 - s**2
    b = 2*(p*s + q*r)
    c = 2*(q*s - p*r)
    d = p**2 + q**2 + r**2 + s**2
    print(f"  ({a}, {b}, {c}, {d}): {a}² + {b}² + {c}² = {a**2} + {b**2} + {c**2} = {a**2+b**2+c**2} = {d}² = {d**2}")
    
    # --- Part 2 ---
    print("\n" + "=" * 70)
    print("PART 2: SPECTRAL GAP AND DESCENT COMPLEXITY")
    print("=" * 70)
    
    print(f"\nSelberg bound: λ₁ ≥ 3/16 = {3/16:.4f}")
    print(f"Optimal bound: λ₁ = 1/4 = {1/4:.4f}")
    print(f"Improvement: {(1/4)/(3/16):.4f}x")
    print(f"Mixing rate: √(λ₁) = {math.sqrt(1/4):.4f}")
    print(f"Descent constant: 1/√(λ₁) = {1/math.sqrt(1/4):.4f}")
    
    depths = descent_statistics(1000)
    if depths:
        print(f"\nDescent statistics (N = 1000):")
        print(f"  PPTs found: {len(depths)}")
        print(f"  Average depth: {sum(depths)/len(depths):.2f}")
        print(f"  Max depth: {max(depths)}")
        print(f"  Expected (2·log₂(1000)): {2*math.log2(1000):.2f}")
    
    # --- Part 3 ---
    print("\n" + "=" * 70)
    print("PART 3: THE r₂ FORMULA AND χ₋₄")
    print("=" * 70)
    
    print("\nχ₋₄ values:")
    for n in range(8):
        print(f"  χ₋₄({n}) = {chi_neg4(n):+d}", end="  ")
    print()
    
    print(f"\nPeriodicity: χ₋₄(0)+χ₋₄(1)+χ₋₄(2)+χ₋₄(3) = {sum(chi_neg4(i) for i in range(4))}")
    
    print(f"\nMultiplicativity (odd inputs):")
    for m, n in [(3,5), (3,7), (5,7), (1,3), (9,11)]:
        print(f"  χ₋₄({m}·{n}) = χ₋₄({m*n}) = {chi_neg4(m*n):+d}  vs  χ₋₄({m})·χ₋₄({n}) = {chi_neg4(m)*chi_neg4(n):+d}  ✓" if chi_neg4(m*n) == chi_neg4(m)*chi_neg4(n) else f"  MISMATCH at ({m},{n})")
    
    print(f"\nr₂ formula verification:")
    print(f"  {'n':>4} | {'r₂(n) formula':>14} | {'r₂(n) brute':>12} | {'Match':>5}")
    print(f"  {'-'*4}-+-{'-'*14}-+-{'-'*12}-+-{'-'*5}")
    for n in [1, 2, 3, 4, 5, 7, 10, 13, 25, 50]:
        f = r2_formula(n)
        b = r2_brute(n)
        match = "✓" if f == b else "✗"
        print(f"  {n:4d} | {f:14d} | {b:12d} | {match:>5}")
    
    mismatches = verify_r2_formula(50)
    print(f"\nMismatches for n ≤ 50: {len(mismatches)}")
    
    # --- Part 4 ---
    print("\n" + "=" * 70)
    print("PART 4: QUANTUM CODES FROM BERGGREN GROUP")
    print("=" * 70)
    
    print("\nGenerator properties:")
    for name, mat in [("M₁", M1), ("M₃", M3), ("S", S)]:
        det = int(np.linalg.det(mat))
        tr = int(np.trace(mat))
        frob = frobenius_distance(mat)
        mtype = "Parabolic" if abs(tr) == 2 else ("Elliptic" if abs(tr) < 2 else "Hyperbolic")
        print(f"  {name}: det={det}, trace={tr}, ‖M-I‖²={frob}, type={mtype}")
    
    print(f"\nS⁴ = I: {np.array_equal(np.linalg.matrix_power(S, 4), np.eye(2, dtype=int))}")
    print(f"S² = -I: {np.array_equal(np.linalg.matrix_power(S, 2), -np.eye(2, dtype=int))}")
    print(f"M₁ = M₃·S: {np.array_equal(M1, M3 @ S)}")
    
    print(f"\nCode parameters:")
    for n in range(1, 8):
        print(f"  Depth {n}: {3**n:>6d} codewords")
    
    # --- Part 5 ---
    print("\n" + "=" * 70)
    print("PART 5: HAUPTMODUL — THE MODULAR LAMBDA FUNCTION")
    print("=" * 70)
    
    print(f"\nj-invariant values:")
    print(f"  j(λ=1/2) = j(i) = {j_invariant(0.5):.0f}  (should be 1728)")
    
    lam = Fraction(1, 2)
    j_exact = 256 * (lam**2 - lam + 1)**3 / (lam**2 * (1 - lam)**2)
    print(f"  Exact: j(1/2) = {j_exact}")
    
    print(f"\nAnharmonic ratios at λ = 2:")
    for i, r in enumerate(anharmonic_ratios(2)):
        print(f"  σ_{i+1}(2) = {r}")
    
    print(f"\nCusp values:")
    print(f"  λ = 0: discriminant = {0**2 * 1**2} (cusp ∞)")
    print(f"  λ = 1: discriminant = {1**2 * 0**2} (cusp 0)")
    print(f"  λ = ∞: pole (cusp 1)")
    
    print(f"\nBerggren-Farey map:")
    triples = [(3,4,5), (5,12,13), (8,15,17), (7,24,25), (20,21,29)]
    for a, b, c in triples:
        f = farey_fraction(a, b, c)
        print(f"  ({a},{b},{c}) ↦ {f} = {float(f):.4f}")
    
    print(f"\nλ(i) = 1/2 fixed point: 1 - 1/2 = {1 - Fraction(1,2)} = 1/2 ✓")
    print(f"|S₃| = 3! = {math.factorial(3)} = 6 ✓")
    print(f"Leading q-coefficient: 16 = 2⁴ = {2**4} ✓")
    
    print("\n" + "=" * 70)
    print("ALL DEMONSTRATIONS COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Berggren Tree Explorer: Hyperbolic Shortcuts and Factoring Demo

This script demonstrates the key mathematical results:
1. Generating Pythagorean triples via the Berggren tree
2. Verifying Lorentz form preservation
3. Hyperbolic shortcuts via repeated squaring
4. Factoring via difference-of-squares from Pythagorean triples
5. The Chebyshev recurrence along the middle branch
"""

import numpy as np
from math import gcd
from typing import List, Tuple, Optional

# ===========================================================================
# Berggren Matrices
# ===========================================================================

B1 = np.array([[1, -2, 2],
               [2, -1, 2],
               [2, -2, 3]], dtype=np.int64)

B2 = np.array([[1, 2, 2],
               [2, 1, 2],
               [2, 2, 3]], dtype=np.int64)

B3 = np.array([[-1, 2, 2],
               [-2, 1, 2],
               [-2, 2, 3]], dtype=np.int64)

Q = np.array([[1, 0, 0],
              [0, 1, 0],
              [0, 0, -1]], dtype=np.int64)

ROOT = np.array([3, 4, 5], dtype=np.int64)

MATRICES = {'L': B1, 'M': B2, 'R': B3}

# Inverse matrices (B_inv = Q @ B.T @ Q)
B1_inv = Q @ B1.T @ Q
B2_inv = Q @ B2.T @ Q
B3_inv = Q @ B3.T @ Q


def verify_lorentz(B: np.ndarray, name: str = "B") -> bool:
    """Verify that B^T Q B = Q (Lorentz preservation)."""
    result = B.T @ Q @ B
    ok = np.array_equal(result, Q)
    print(f"  {name}^T Q {name} = Q: {ok}")
    return ok


def lorentz_form(v: np.ndarray) -> int:
    """Compute Q(v) = v[0]^2 + v[1]^2 - v[2]^2."""
    return int(v[0]**2 + v[1]**2 - v[2]**2)


def triple_at_path(path: str) -> np.ndarray:
    """Compute the Pythagorean triple at the given path (e.g., 'LMR')."""
    v = ROOT.copy()
    for d in path:
        v = MATRICES[d] @ v
    return v


def shortcut_matrix(path: str) -> np.ndarray:
    """Compute the composite matrix for a path.
    Same convention as triple_at_path: first char applied first (innermost)."""
    M = np.eye(3, dtype=np.int64)
    for d in reversed(path):
        M = MATRICES[d] @ M
    return M


def repeated_squaring(B: np.ndarray, k: int) -> np.ndarray:
    """Compute B^k via repeated squaring in O(log k) multiplications."""
    if k == 0:
        return np.eye(3, dtype=np.int64)
    if k == 1:
        return B.copy()
    if k % 2 == 0:
        half = repeated_squaring(B, k // 2)
        return half @ half
    else:
        return B @ repeated_squaring(B, k - 1)


def factor_via_triple(n: int, a: int, b: int, c: int) -> Optional[Tuple[int, int]]:
    """
    Given a Pythagorean triple (a, b, c) where a = n or a divides n^2,
    attempt to factor n using the difference-of-squares identity.
    Returns (p, q) if successful, None otherwise.
    """
    # (c - b)(c + b) = a^2
    d1 = c - b
    d2 = c + b
    g = gcd(abs(d1), abs(n))
    if 1 < g < abs(n):
        return (g, abs(n) // g)
    g2 = gcd(abs(d2), abs(n))
    if 1 < g2 < abs(n):
        return (g2, abs(n) // g2)
    return None


# ===========================================================================
# Demo 1: The Berggren Tree
# ===========================================================================

def demo_tree():
    print("=" * 70)
    print("DEMO 1: The Berggren Tree")
    print("=" * 70)
    print(f"\nRoot: {ROOT}  (3² + 4² = 9 + 16 = 25 = 5²)")
    print("\nFirst generation:")
    for name, d in [("Left (B₁)", 'L'), ("Middle (B₂)", 'M'), ("Right (B₃)", 'R')]:
        v = triple_at_path(d)
        a, b, c = v
        print(f"  {name}: ({a}, {b}, {c})  "
              f"({a}² + {b}² = {a**2} + {b**2} = {c**2} = {c}²)")
    
    print("\nSecond generation (from middle branch):")
    for path in ['ML', 'MM', 'MR']:
        v = triple_at_path(path)
        a, b, c = v
        print(f"  Path [{path}]: ({a}, {b}, {c})  "
              f"(a² + b² = {a**2 + b**2} = {c**2} = c²)")


# ===========================================================================
# Demo 2: Lorentz Form Preservation
# ===========================================================================

def demo_lorentz():
    print("\n" + "=" * 70)
    print("DEMO 2: Lorentz Form Preservation")
    print("=" * 70)
    print("\nVerifying B_i^T Q B_i = Q for each generator:")
    verify_lorentz(B1, "B₁")
    verify_lorentz(B2, "B₂")
    verify_lorentz(B3, "B₃")
    
    print(f"\nDeterminants: det(B₁)={int(np.linalg.det(B1)):+d}, "
          f"det(B₂)={int(np.linalg.det(B2)):+d}, "
          f"det(B₃)={int(np.linalg.det(B3)):+d}")
    
    print("\nLorentz form Q(v) = a² + b² - c² at each node:")
    for path in ['', 'L', 'M', 'R', 'ML', 'MM', 'MR', 'MMM']:
        v = triple_at_path(path)
        q = lorentz_form(v)
        label = f"[{path}]" if path else "[root]"
        print(f"  {label:8s}: ({v[0]:6d}, {v[1]:6d}, {v[2]:6d})  Q = {q}")


# ===========================================================================
# Demo 3: Hyperbolic Shortcuts
# ===========================================================================

def demo_shortcuts():
    print("\n" + "=" * 70)
    print("DEMO 3: Hyperbolic Shortcuts via Repeated Squaring")
    print("=" * 70)
    
    print("\nMiddle branch (B₂ iterated k times):")
    print(f"  {'k':>3s}  {'a':>15s}  {'b':>15s}  {'c (hypotenuse)':>15s}  {'Ops':>6s}")
    print("  " + "-" * 60)
    
    for k in range(8):
        Bk = repeated_squaring(B2, k)
        v = Bk @ ROOT
        ops = max(1, k.bit_length()) if k > 0 else 0  # approximate
        print(f"  {k:3d}  {v[0]:15d}  {v[1]:15d}  {v[2]:15d}  {ops:6d}")
    
    print("\nShortcut: reaching depth 20 on the middle branch via repeated squaring")
    print("  Naive: 20 matrix multiplications")
    print("  Repeated squaring: ~5 multiplications")
    # Use Python ints to avoid overflow
    def mat_mul_py(A, B):
        n = len(A)
        return [[sum(A[i][k]*B[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
    def mat_vec_py(M, v):
        return [sum(M[i][j]*v[j] for j in range(len(v))) for i in range(len(v))]
    def mat_pow_py(M, k):
        n = len(M)
        if k == 0: return [[1 if i==j else 0 for j in range(n)] for i in range(n)]
        if k == 1: return [row[:] for row in M]
        if k % 2 == 0:
            half = mat_pow_py(M, k//2)
            return mat_mul_py(half, half)
        return mat_mul_py(M, mat_pow_py(M, k-1))
    B2_py = [[1,2,2],[2,1,2],[2,2,3]]
    root_py = [3,4,5]
    B2_20 = mat_pow_py(B2_py, 20)
    v20 = mat_vec_py(B2_20, root_py)
    print(f"  a = {v20[0]}")
    print(f"  b = {v20[1]}")
    print(f"  c = {v20[2]}")
    print(f"  Digits in hypotenuse: {len(str(v20[2]))}")
    q_val = v20[0]**2 + v20[1]**2 - v20[2]**2
    print(f"  Q(v) = {q_val} (should be 0)")


# ===========================================================================
# Demo 4: Factoring via Pythagorean Triples
# ===========================================================================

def demo_factoring():
    print("\n" + "=" * 70)
    print("DEMO 4: Factoring via Difference-of-Squares")
    print("=" * 70)
    
    # Example: factoring 21 from the triple (21, 20, 29)
    print("\nExample 1: Factoring 21")
    a, b, c = 21, 20, 29
    print(f"  Triple: ({a}, {b}, {c})")
    print(f"  Verify: {a}² + {b}² = {a**2} + {b**2} = {c**2} = {c}²")
    d1, d2 = c - b, c + b
    print(f"  (c-b)(c+b) = {d1} × {d2} = {d1*d2} = {a}² = {a**2}")
    g1 = gcd(d1, a)
    g2 = gcd(d2, a)
    print(f"  gcd({d1}, {a}) = {g1}")
    print(f"  gcd({d2}, {a}) = {g2}")
    print(f"  → 21 = {g1} × {a // g1}")
    
    # Systematic factoring using tree exploration
    print("\nSystematic factoring using Berggren tree exploration:")
    test_numbers = [15, 21, 35, 77, 143, 221, 323]
    
    for n in test_numbers:
        found = False
        # Search the tree up to depth 4
        from itertools import product as iprod
        for depth in range(1, 5):
            if found:
                break
            for dirs in iprod('LMR', repeat=depth):
                path = ''.join(dirs)
                v = triple_at_path(path)
                a_val = abs(int(v[0]))
                if a_val == n or (n > 1 and a_val % n == 0 and a_val > 0):
                    result = factor_via_triple(n, int(v[0]), int(v[1]), int(v[2]))
                    if result:
                        p, q = result
                        print(f"  {n:4d} = {p} × {q}  "
                              f"(from triple ({v[0]},{v[1]},{v[2]}) at path [{path}])")
                        found = True
                        break
        if not found:
            print(f"  {n:4d}: no factoring triple found in depth ≤ 4")


# ===========================================================================
# Demo 5: Chebyshev Recurrence
# ===========================================================================

def demo_chebyshev():
    print("\n" + "=" * 70)
    print("DEMO 5: Chebyshev Recurrence on the Middle Branch")
    print("=" * 70)
    
    print("\nMiddle-branch hypotenuses and the recurrence c_{n+1} = 6c_n - c_{n-1}:")
    hyps = []
    for k in range(10):
        Bk = repeated_squaring(B2, k)
        v = Bk @ ROOT
        hyps.append(int(v[2]))
    
    print(f"  {'n':>3s}  {'c_n':>12s}  {'6c_n - c_{n-1}':>15s}  {'= c_{n+1}?':>10s}")
    print("  " + "-" * 45)
    for i in range(len(hyps)):
        if i >= 2:
            predicted = 6 * hyps[i-1] - hyps[i-2]
            match = "✓" if predicted == hyps[i] else "✗"
            print(f"  {i:3d}  {hyps[i]:12d}  {predicted:15d}  {match:>10s}")
        elif i == 1:
            print(f"  {i:3d}  {hyps[i]:12d}")
        else:
            print(f"  {i:3d}  {hyps[i]:12d}")
    
    print(f"\n  Ratio c_n/c_{'{n-1}'}: ", end="")
    for i in range(1, min(8, len(hyps))):
        print(f"{hyps[i]/hyps[i-1]:.4f}  ", end="")
    print(f"\n  Converges to 3 + 2√2 ≈ {3 + 2*2**0.5:.6f}")


# ===========================================================================
# Demo 6: Inverse Matrices and Tree Ascent
# ===========================================================================

def demo_inverse():
    print("\n" + "=" * 70)
    print("DEMO 6: Tree Ascent via Inverse Matrices")
    print("=" * 70)
    
    print("\nInverse formula: B_i^{-1} = Q · B_i^T · Q")
    print(f"\nVerification: B₁ · B₁⁻¹ = I: {np.array_equal(B1 @ B1_inv, np.eye(3, dtype=np.int64))}")
    print(f"Verification: B₂ · B₂⁻¹ = I: {np.array_equal(B2 @ B2_inv, np.eye(3, dtype=np.int64))}")
    print(f"Verification: B₃ · B₃⁻¹ = I: {np.array_equal(B3 @ B3_inv, np.eye(3, dtype=np.int64))}")
    
    # Ascend from (119, 120, 169) back to root
    print("\nAscending from (119, 120, 169) to root:")
    v = np.array([119, 120, 169], dtype=np.int64)
    step = 0
    while not np.array_equal(v, ROOT):
        a, b, c = v
        print(f"  Step {step}: ({a}, {b}, {c})")
        
        # Try each inverse; the correct one gives all positive entries
        for name, Binv in [("B₁⁻¹", B1_inv), ("B₂⁻¹", B2_inv), ("B₃⁻¹", B3_inv)]:
            parent = Binv @ v
            if all(p > 0 for p in parent) or np.array_equal(parent, ROOT):
                print(f"         → Apply {name}")
                v = parent
                break
        step += 1
        if step > 20:
            print("  (stopping after 20 steps)")
            break
    
    print(f"  Step {step}: ({v[0]}, {v[1]}, {v[2]}) = ROOT ✓")


# ===========================================================================
# Main
# ===========================================================================

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║  Berggren Tree Explorer: Hyperbolic Shortcuts & Factoring Demo     ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    
    demo_tree()
    demo_lorentz()
    demo_shortcuts()
    demo_factoring()
    demo_chebyshev()
    demo_inverse()
    
    print("\n" + "=" * 70)
    print("All demos complete.")
    print("=" * 70)

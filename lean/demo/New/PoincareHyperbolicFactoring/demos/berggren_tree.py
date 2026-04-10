"""
Berggren Tree: Interactive Exploration and Factoring Demo

This module implements the Berggren tree for generating all primitive Pythagorean
triples, along with the hyperbolic shortcut factoring algorithm.
"""

import numpy as np
from math import gcd, isqrt
from typing import Optional

# ============================================================================
# Berggren Matrices
# ============================================================================

B1 = np.array([[1, -2, 2], [2, -1, 2], [2, -2, 3]], dtype=np.int64)
B2 = np.array([[1, 2, 2], [2, 1, 2], [2, 2, 3]], dtype=np.int64)
B3 = np.array([[-1, 2, 2], [-2, 1, 2], [-2, 2, 3]], dtype=np.int64)

# Inverse matrices for parent descent
B1_inv = np.array([[1, 2, -2], [-2, -1, 2], [-2, -2, 3]], dtype=np.int64)
B2_inv = np.array([[1, -2, -2], [2, -1, 2], [2, -2, 3]], dtype=np.int64)
B3_inv = np.array([[-1, -2, 2], [2, -1, 2], [2, -2, 3]], dtype=np.int64)

# Lorentz form matrix Q = diag(1, 1, -1)
Q = np.array([[1, 0, 0], [0, 1, 0], [0, 0, -1]], dtype=np.int64)

ROOT = np.array([3, 4, 5], dtype=np.int64)


def verify_lorentz_preservation():
    """Verify that each Berggren matrix preserves the Lorentz form."""
    for name, B in [("B1", B1), ("B2", B2), ("B3", B3)]:
        result = B.T @ Q @ B
        assert np.array_equal(result, Q), f"{name} does not preserve Q!"
        det = int(round(np.linalg.det(B)))
        print(f"{name}: B^T Q B = Q ✓  det = {det}")


# ============================================================================
# Tree Generation
# ============================================================================

def generate_tree(depth: int = 4) -> list:
    """Generate all Pythagorean triples up to a given tree depth."""
    triples = []
    
    def _recurse(triple, d, path):
        triples.append((tuple(triple), path, d))
        if d >= depth:
            return
        _recurse(B1 @ triple, d + 1, path + "L")
        _recurse(B2 @ triple, d + 1, path + "M")
        _recurse(B3 @ triple, d + 1, path + "R")
    
    _recurse(ROOT, 0, "")
    return triples


def print_tree(depth: int = 3):
    """Print the Berggren tree up to a given depth."""
    triples = generate_tree(depth)
    print(f"\nBerggren Tree (depth {depth}):")
    print(f"{'Path':<12} {'Triple':<20} {'a²+b²=c²':<15} {'Depth'}")
    print("-" * 60)
    for triple, path, d in triples:
        a, b, c = triple
        check = "✓" if a*a + b*b == c*c else "✗"
        path_str = path if path else "(root)"
        print(f"{path_str:<12} ({a}, {b}, {c}){'':<{max(0,14-len(str(triple)))}} "
              f"{a}²+{b}²={c}² {check}  {d}")


# ============================================================================
# Hyperbolic Shortcuts
# ============================================================================

def shortcut_matrix(path: str) -> np.ndarray:
    """Compute the shortcut matrix for a given path string (e.g., 'LMR').
    pathMatrix([d1,d2,...,dk]) = B_d1 * B_d2 * ... * B_dk"""
    matrices = {'L': B1, 'M': B2, 'R': B3}
    result = np.eye(3, dtype=np.int64)
    for d in path:
        result = result @ matrices[d]
    return result


def apply_shortcut(path: str) -> np.ndarray:
    """Apply a hyperbolic shortcut to reach a triple directly."""
    M = shortcut_matrix(path)
    return M @ ROOT


def demo_shortcuts():
    """Demonstrate hyperbolic shortcuts."""
    print("\n" + "=" * 60)
    print("HYPERBOLIC SHORTCUTS DEMO")
    print("=" * 60)
    
    paths = ["L", "M", "R", "LM", "LR", "ML", "MR", "RL", "RM",
             "LLL", "LMR", "RML", "MMM"]
    
    print(f"\n{'Path':<8} {'Shortcut Triple':<20} {'det(M)':<8} {'Q preserved?'}")
    print("-" * 55)
    
    for path in paths:
        M = shortcut_matrix(path)
        triple = M @ ROOT
        det = int(round(np.linalg.det(M)))
        q_preserved = np.array_equal(M.T @ Q @ M, Q)
        a, b, c = triple
        pyth = a*a + b*b == c*c
        print(f"{path:<8} ({a}, {b}, {c}){'':<{max(0,14-len(f'({a}, {b}, {c})'))}} "
              f"{det:<8} {'✓' if q_preserved else '✗'}")


# ============================================================================
# Parent Descent (Inverse Navigation)
# ============================================================================

def find_parent(triple: np.ndarray) -> Optional[tuple]:
    """Find the parent of a triple in the Berggren tree.
    Returns (parent_triple, direction) or None if at root."""
    a, b, c = triple
    
    if a == 3 and b == 4 and c == 5:
        return None
    
    # Try each inverse matrix
    for name, inv in [("L", B1_inv), ("M", B2_inv), ("R", B3_inv)]:
        parent = inv @ triple
        pa, pb, pc = parent
        # Parent must be a valid primitive Pythagorean triple with positive entries
        if pa > 0 and pb > 0 and pc > 0 and pa*pa + pb*pb == pc*pc:
            return (parent, name)
    
    # Handle case where a might be negative (from B3)
    triple_abs = np.array([abs(a), abs(b), c], dtype=np.int64)
    for name, inv in [("L", B1_inv), ("M", B2_inv), ("R", B3_inv)]:
        parent = inv @ triple_abs
        pa, pb, pc = parent
        if pa > 0 and pb > 0 and pc > 0 and pa*pa + pb*pb == pc*pc:
            return (parent, name)
    
    return None


def descent_path(triple: np.ndarray) -> str:
    """Find the complete path from root to this triple."""
    path = []
    current = triple.copy()
    
    while True:
        result = find_parent(current)
        if result is None:
            break
        current, direction = result
        path.append(direction)
    
    return "".join(reversed(path))


# ============================================================================
# Factoring via Pythagorean Triples
# ============================================================================

def sum_of_two_squares(n: int) -> Optional[tuple]:
    """Find a, b such that a² + b² = n using Cornacchia-like algorithm.
    Returns (a, b) or None if impossible."""
    if n <= 0:
        return None
    if n == 1:
        return (1, 0)
    if n == 2:
        return (1, 1)
    
    # n must be expressible as a sum of two squares
    # Check: no prime factor ≡ 3 (mod 4) appears to an odd power
    
    # Simple search for small numbers
    for a in range(1, isqrt(n) + 1):
        b_sq = n - a * a
        if b_sq < 0:
            break
        b = isqrt(b_sq)
        if b * b == b_sq:
            return (a, b)
    
    return None


def pythagorean_factor(N: int) -> Optional[int]:
    """Attempt to factor N using Pythagorean triples.
    
    Strategy: Find (a, b, c) with one leg = N, then use
    (c - b)(c + b) = N² to extract a factor.
    """
    if N <= 1 or N % 2 == 0:
        return None
    
    # Method 1: Use N as a leg directly
    # N² + b² = c² => (c-b)(c+b) = N²
    # Let d | N², d < N, d ≡ N² (mod 2)
    # Then b = (N²/d - d)/2, c = (N²/d + d)/2
    
    N_sq = N * N
    factors_found = []
    
    for d in range(1, isqrt(N_sq) + 1):
        if N_sq % d == 0:
            e = N_sq // d
            if d < e and (d % 2 == e % 2):
                b = (e - d) // 2
                c = (e + d) // 2
                # Verify
                if N_sq + b*b == c*c:
                    g = gcd(d, N)
                    if 1 < g < N:
                        factors_found.append(g)
    
    return factors_found[0] if factors_found else None


def demo_factoring():
    """Demonstrate the Pythagorean factoring algorithm."""
    print("\n" + "=" * 60)
    print("PYTHAGOREAN TRIPLE FACTORING DEMO")
    print("=" * 60)
    
    test_numbers = [15, 21, 33, 35, 55, 77, 91, 119, 143, 221, 323, 437, 1001, 10001]
    
    print(f"\n{'N':<8} {'Factor':<8} {'N/Factor':<10} {'Verification'}")
    print("-" * 45)
    
    for N in test_numbers:
        factor = pythagorean_factor(N)
        if factor:
            other = N // factor
            check = "✓" if factor * other == N else "✗"
            print(f"{N:<8} {factor:<8} {other:<10} {check}")
        else:
            print(f"{N:<8} {'—':<8} {'(prime or method N/A)'}")


# ============================================================================
# Lorentz / Hyperbolic Geometry
# ============================================================================

def lorentz_inner(u: np.ndarray, v: np.ndarray) -> int:
    """Compute the Lorentz inner product ⟨u, v⟩_L = u₀v₀ + u₁v₁ - u₂v₂."""
    return int(u[0]*v[0] + u[1]*v[1] - u[2]*v[2])


def hyperbolic_distance_proxy(u: np.ndarray, v: np.ndarray) -> float:
    """A proxy for the 'distance' between two Pythagorean triples in the tree.
    Since triples lie on the light cone (Q=0), not the hyperboloid (Q=-1),
    we use the ratio of hypotenuses as a distance proxy: log(c_v / c_u).
    This measures 'how far apart' two triples are in the tree structure."""
    return abs(np.log(float(v[2]) / float(u[2])))


def demo_hyperbolic_geometry():
    """Demonstrate the hyperbolic geometry of the Berggren tree."""
    print("\n" + "=" * 60)
    print("HYPERBOLIC GEOMETRY OF THE BERGGREN TREE")
    print("=" * 60)
    
    triples = generate_tree(depth=3)
    
    print(f"\n{'Path':<10} {'Triple':<20} {'Q(v)':<8} {'log(c/5)':<10} {'Depth'}")
    print("-" * 60)
    
    for triple, path, depth in triples:
        t = np.array(triple, dtype=np.int64)
        ln = lorentz_inner(t, t)  # Should be 0 (on light cone)
        hd = hyperbolic_distance_proxy(ROOT, t) if path else 0.0
        path_str = path if path else "(root)"
        a, b, c = triple
        print(f"{path_str:<10} ({a},{b},{c}){'':<{max(0,14-len(f'({a},{b},{c})'))}} {ln:<8} {hd:<10.3f} {depth}")


# ============================================================================
# Shortcut Composition Demo
# ============================================================================

def demo_composition():
    """Demonstrate that shortcuts compose via matrix multiplication."""
    print("\n" + "=" * 60)
    print("SHORTCUT COMPOSITION DEMO")
    print("=" * 60)
    
    print("\nVerifying: pathMatrix(p ++ q) = pathMatrix(p) · pathMatrix(q)")
    print()
    
    test_cases = [
        ("L", "M"),
        ("LR", "ML"),
        ("LMR", "RML"),
        ("LLRM", "MRLR"),
    ]
    
    for p, q in test_cases:
        Mp = shortcut_matrix(p)
        Mq = shortcut_matrix(q)
        M_concat = shortcut_matrix(p + q)
        M_product = Mp @ Mq
        
        match = np.array_equal(M_concat, M_product)
        triple_concat = M_concat @ ROOT
        triple_product = M_product @ ROOT
        
        print(f"  path({p}) · path({q}) = path({p+q}): "
              f"{'✓' if match else '✗'}  "
              f"triple = ({triple_concat[0]}, {triple_concat[1]}, {triple_concat[2]})")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  HYPERBOLIC SHORTCUTS THROUGH THE BERGGREN TREE         ║")
    print("║  Interactive Python Demo                                 ║")
    print("╚══════════════════════════════════════════════════════════╝")
    
    # 1. Verify fundamental properties
    print("\n1. FUNDAMENTAL PROPERTIES")
    print("-" * 40)
    verify_lorentz_preservation()
    
    # 2. Print the tree
    print_tree(depth=2)
    
    # 3. Shortcuts
    demo_shortcuts()
    
    # 4. Composition
    demo_composition()
    
    # 5. Hyperbolic geometry
    demo_hyperbolic_geometry()
    
    # 6. Factoring
    demo_factoring()
    
    print("\n" + "=" * 60)
    print("All demos complete!")

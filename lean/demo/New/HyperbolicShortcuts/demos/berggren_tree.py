#!/usr/bin/env python3
"""
Berggren Tree Explorer: Generate, visualize, and factor using Pythagorean triples.

Demonstrates:
1. Berggren tree generation via matrix multiplication
2. Lorentz form preservation verification
3. Shortcut factoring algorithm
4. Parallel branch exploration
5. Higher-dimensional Pythagorean quadruples
"""

import numpy as np
from math import gcd, isqrt
from typing import List, Tuple, Optional
from itertools import product as cartesian_product

# ============================================================
# §1. Berggren Matrices
# ============================================================

B1 = np.array([[1, -2, 2], [2, -1, 2], [2, -2, 3]], dtype=np.int64)
B2 = np.array([[1,  2, 2], [2,  1, 2], [2,  2, 3]], dtype=np.int64)
B3 = np.array([[-1, 2, 2], [-2, 1, 2], [-2, 2, 3]], dtype=np.int64)

Q = np.diag([1, 1, -1]).astype(np.int64)  # Lorentz metric

MATRICES = {'L': B1, 'M': B2, 'R': B3}
ROOT = np.array([3, 4, 5], dtype=np.int64)


def path_matrix(path: str) -> np.ndarray:
    """Compute the path matrix for a given path string (e.g., 'LMR')."""
    M = np.eye(3, dtype=np.int64)
    for d in path:
        M = MATRICES[d] @ M
    return M


def triple_at(path: str) -> np.ndarray:
    """Compute the Pythagorean triple at a given path."""
    return path_matrix(path) @ ROOT


def verify_lorentz(M: np.ndarray) -> bool:
    """Verify that M preserves the Lorentz form: M^T Q M = Q."""
    return np.array_equal(M.T @ Q @ M, Q)


def verify_pythagorean(v: np.ndarray) -> bool:
    """Verify a^2 + b^2 = c^2."""
    return v[0]**2 + v[1]**2 == v[2]**2


# ============================================================
# §2. Tree Generation
# ============================================================

def generate_tree(depth: int) -> List[Tuple[str, np.ndarray]]:
    """Generate all triples in the Berggren tree up to given depth."""
    results = [('', ROOT)]
    frontier = [('', ROOT)]
    
    for d in range(depth):
        new_frontier = []
        for path, triple in frontier:
            for direction, matrix in MATRICES.items():
                new_path = path + direction
                new_triple = matrix @ triple
                results.append((new_path, new_triple))
                new_frontier.append((new_path, new_triple))
        frontier = new_frontier
    
    return results


def print_tree(depth: int):
    """Print the Berggren tree to a given depth."""
    triples = generate_tree(depth)
    print(f"Berggren Tree (depth {depth}): {len(triples)} triples\n")
    print(f"{'Path':<12} {'Triple':<25} {'a²+b²=c²?':<10} {'Q preserved?'}")
    print("-" * 65)
    for path, triple in triples:
        a, b, c = triple
        pyth = verify_pythagorean(triple)
        M = path_matrix(path) if path else np.eye(3, dtype=np.int64)
        lorentz = verify_lorentz(M)
        print(f"{path or '(root)':<12} ({a:>4}, {b:>4}, {c:>4})     {'✓' if pyth else '✗':<10} {'✓' if lorentz else '✗'}")


# ============================================================
# §3. Shortcut Factoring Algorithm
# ============================================================

def find_sum_of_squares(n: int) -> Optional[Tuple[int, int]]:
    """Find a, b such that a^2 + b^2 = n (if possible).
    Uses brute force for simplicity; Cornacchia's algorithm is faster."""
    if n <= 0:
        return None
    for a in range(1, isqrt(n) + 1):
        b_sq = n - a * a
        if b_sq < 0:
            break
        b = isqrt(b_sq)
        if b * b == b_sq and b > 0:
            return (a, b)
    return None


def shortcut_factor(N: int, verbose: bool = True) -> Optional[int]:
    """
    Attempt to factor N using the Berggren tree shortcut algorithm.
    
    1. Find a, b with a^2 + b^2 = N^2 (or a^2 + b^2 = c^2 with N | a)
    2. Use the factoring identity (c-b)(c+b) = a^2
    3. Check if gcd reveals a factor
    """
    if N % 2 == 0:
        return 2
    if N < 4:
        return None
    
    # Try to find a Pythagorean triple with N as a leg
    # Use: if N is odd, try N = a with b = (N^2-1)/2, c = (N^2+1)/2
    if N % 2 == 1:
        a = N
        b = (N * N - 1) // 2
        c = (N * N + 1) // 2
        
        if a * a + b * b == c * c:
            if verbose:
                print(f"Triple: ({a}, {b}, {c})")
                print(f"Identity: (c-b)(c+b) = ({c-b})×({c+b}) = {(c-b)*(c+b)} = {a}²")
            
            # The factoring identity gives us (c-b)(c+b) = a^2 = N^2
            # c - b = 1, c + b = N^2 (trivial for this construction)
            # We need a more sophisticated triple
    
    # Try Euclid parametrization: (m²-n², 2mn, m²+n²)
    # If N = m²-n² = (m-n)(m+n), this gives a factoring
    for m in range(2, isqrt(N) + 2):
        for n in range(1, m):
            a = m * m - n * n
            b = 2 * m * n
            c = m * m + n * n
            
            g = gcd(a, N)
            if 1 < g < N:
                if verbose:
                    print(f"Factor found via triple ({a}, {b}, {c})")
                    print(f"  Euclid params: m={m}, n={n}")
                    print(f"  gcd({a}, {N}) = {g}")
                return g
            
            g = gcd(b, N)
            if 1 < g < N:
                if verbose:
                    print(f"Factor found via triple ({a}, {b}, {c})")
                    print(f"  Euclid params: m={m}, n={n}")
                    print(f"  gcd({b}, {N}) = {g}")
                return g
    
    return None


# ============================================================
# §4. Parallel Branch Exploration
# ============================================================

def parallel_search(N: int, max_depth: int = 5) -> Optional[int]:
    """
    Search for factors of N using parallel tree exploration.
    Each branch is independent (parallel_independence theorem).
    """
    print(f"\nParallel search for factors of {N}:")
    print(f"  Exploring tree to depth {max_depth}")
    
    # Generate all paths at each depth level
    for depth in range(1, max_depth + 1):
        paths = [''.join(p) for p in cartesian_product('LMR', repeat=depth)]
        
        for path in paths:
            triple = triple_at(path)
            a, b, c = triple
            
            # Check gcd with N for each leg
            for leg in [abs(a), abs(b)]:
                g = gcd(int(leg), N)
                if 1 < g < N:
                    print(f"  Factor {g} found at path '{path}', triple ({a}, {b}, {c})")
                    return g
    
    print(f"  No factor found within depth {max_depth}")
    return None


# ============================================================
# §5. Higher-Dimensional: Pythagorean Quadruples
# ============================================================

G4 = np.array([
    [1, 2, 0, 2],
    [2, 1, 0, 2],
    [0, 0, 1, 0],
    [2, 2, 0, 3]
], dtype=np.int64)

G4_prime = np.array([
    [1, 0, 2, 2],
    [0, 1, 0, 0],
    [2, 0, 1, 2],
    [2, 0, 2, 3]
], dtype=np.int64)

eta4 = np.diag([1, 1, 1, -1]).astype(np.int64)

ROOT_QUAD = np.array([1, 2, 2, 3], dtype=np.int64)


def verify_quadruple(v: np.ndarray) -> bool:
    """Verify a^2 + b^2 + c^2 = d^2."""
    return v[0]**2 + v[1]**2 + v[2]**2 == v[3]**2


def generate_quadruples(depth: int) -> List[np.ndarray]:
    """Generate Pythagorean quadruples using 4D generators."""
    results = [ROOT_QUAD]
    frontier = [ROOT_QUAD]
    
    generators = [G4, G4_prime]
    
    for d in range(depth):
        new_frontier = []
        for quad in frontier:
            for gen in generators:
                new_quad = gen @ quad
                if new_quad[3] > 0:  # positive hyper-hypotenuse
                    results.append(new_quad)
                    new_frontier.append(new_quad)
        frontier = new_frontier
    
    return results


def quadruple_factoring_demo():
    """Demonstrate the triple factoring identity from quadruples."""
    print("\n" + "=" * 60)
    print("PYTHAGOREAN QUADRUPLE FACTORING")
    print("=" * 60)
    
    quads = generate_quadruples(2)
    for quad in quads[:8]:
        a, b, c, d = quad
        print(f"\nQuadruple: ({a}, {b}, {c}, {d})")
        print(f"  Check: {a}² + {b}² + {c}² = {a**2} + {b**2} + {c**2} = {a**2+b**2+c**2} = {d}² = {d**2}")
        print(f"  Identity 1: ({d}-{c})({d}+{c}) = {d-c}×{d+c} = {(d-c)*(d+c)} = {a}²+{b}² = {a**2+b**2}")
        print(f"  Identity 2: ({d}-{b})({d}+{b}) = {d-b}×{d+b} = {(d-b)*(d+b)} = {a}²+{c}² = {a**2+c**2}")
        print(f"  Identity 3: ({d}-{a})({d}+{a}) = {d-a}×{d+a} = {(d-a)*(d+a)} = {b}²+{c}² = {b**2+c**2}")


# ============================================================
# §6. Determinant Parity
# ============================================================

def det_parity_demo():
    """Demonstrate the determinant parity theorem."""
    print("\n" + "=" * 60)
    print("DETERMINANT PARITY THEOREM")
    print("=" * 60)
    print("det(pathMatrix(p)) = (-1)^(count of M-steps)\n")
    
    test_paths = ['', 'L', 'M', 'R', 'LR', 'LM', 'MM', 'LMR', 'LLL', 'MMM']
    for path in test_paths:
        M = path_matrix(path) if path else np.eye(3, dtype=np.int64)
        det = int(round(np.linalg.det(M)))
        count_m = path.count('M')
        expected = (-1) ** count_m
        status = "✓" if det == expected else "✗"
        print(f"  Path '{path or '(empty)'}':\tdet = {det:>2},\t(-1)^{count_m} = {expected:>2}  {status}")


# ============================================================
# §7. Lorentz Verification Suite
# ============================================================

def lorentz_verification():
    """Verify all Lorentz preservation properties."""
    print("\n" + "=" * 60)
    print("LORENTZ FORM PRESERVATION VERIFICATION")
    print("=" * 60)
    
    # Individual matrices
    for name, M in [('B₁', B1), ('B₂', B2), ('B₃', B3)]:
        preserved = verify_lorentz(M)
        det = int(round(np.linalg.det(M)))
        print(f"  {name}: Q preserved = {preserved}, det = {det}")
    
    # Random paths
    print("\n  Random path verification:")
    import random
    random.seed(42)
    for _ in range(10):
        length = random.randint(1, 8)
        path = ''.join(random.choice('LMR') for _ in range(length))
        M = path_matrix(path)
        preserved = verify_lorentz(M)
        triple = M @ ROOT
        pyth = verify_pythagorean(triple)
        print(f"    Path '{path}': Q preserved = {preserved}, Pythagorean = {pyth}, triple = ({triple[0]}, {triple[1]}, {triple[2]})")
    
    # 4D verification
    print("\n  4D Lorentz verification:")
    for name, M in [('G₄', G4), ("G₄'", G4_prime)]:
        preserved = np.array_equal(M.T @ eta4 @ M, eta4)
        det = int(round(np.linalg.det(M)))
        print(f"  {name}: η₄ preserved = {preserved}, det = {det}")


# ============================================================
# §8. Factoring Examples
# ============================================================

def factoring_examples():
    """Demonstrate factoring via Pythagorean triples."""
    print("\n" + "=" * 60)
    print("FACTORING VIA PYTHAGOREAN TRIPLES")
    print("=" * 60)
    
    # Classic example: 667 = 23 × 29
    print("\nExample 1: Factor 667")
    print(f"  667² + 156² = {667**2} + {156**2} = {667**2 + 156**2} = 685² = {685**2}")
    print(f"  (685 - 156)(685 + 156) = 529 × 841 = {529 * 841}")
    print(f"  529 = 23², 841 = 29²")
    print(f"  Therefore 667 = 23 × 29")
    
    # Try some composites
    composites = [15, 21, 35, 77, 91, 143, 221, 323, 667]
    print(f"\nSystematic factoring attempts:")
    for N in composites:
        factor = shortcut_factor(N, verbose=False)
        if factor:
            print(f"  {N} = {factor} × {N // factor}")
        else:
            print(f"  {N}: no factor found (may be prime)")


# ============================================================
# Main
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("BERGGREN TREE EXPLORER")
    print("Hyperbolic Shortcuts Through the Pythagorean Triple Tree")
    print("=" * 60)
    
    # 1. Print the tree
    print_tree(2)
    
    # 2. Lorentz verification
    lorentz_verification()
    
    # 3. Determinant parity
    det_parity_demo()
    
    # 4. Factoring examples
    factoring_examples()
    
    # 5. Quadruple factoring
    quadruple_factoring_demo()
    
    # 6. Parallel search example
    parallel_search(77, max_depth=4)
    
    print("\n" + "=" * 60)
    print("All demonstrations complete.")
    print("=" * 60)

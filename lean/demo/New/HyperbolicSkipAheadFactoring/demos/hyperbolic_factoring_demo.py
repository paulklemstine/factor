#!/usr/bin/env python3
"""
Hyperbolic Skip-Ahead Factoring via Pythagorean Triple Trees
=============================================================

Demonstrates the two-phase factoring strategy:
  Phase 1: Construct a trivial Pythagorean triple from N
  Phase 2: Navigate the Berggren tree using matrix exponentiation (skip-ahead)
           to find triples whose legs share a nontrivial GCD with N

Usage:
    python hyperbolic_factoring_demo.py [N]
    python hyperbolic_factoring_demo.py          # runs interactive demo
"""

import numpy as np
from math import gcd, isqrt
from typing import Optional, Tuple, List
import time
import sys

# ============================================================
# §1. Berggren Matrices
# ============================================================

B1 = np.array([[ 1, -2,  2],
               [ 2, -1,  2],
               [ 2, -2,  3]], dtype=object)

B2 = np.array([[ 1,  2,  2],
               [ 2,  1,  2],
               [ 2,  2,  3]], dtype=object)

B3 = np.array([[-1,  2,  2],
               [-2,  1,  2],
               [-2,  2,  3]], dtype=object)

BERGGREN_MATRICES = [B1, B2, B3]
BRANCH_NAMES = ["B₁ (left)", "B₂ (middle)", "B₃ (right)"]

# ============================================================
# §2. Trivial Pythagorean Triple Construction
# ============================================================

def trivial_triple_odd(N: int) -> Tuple[int, int, int]:
    """
    For odd N, construct the triple (N, (N²-1)/2, (N²+1)/2).
    This always satisfies a² + b² = c² with a = N.
    """
    assert N % 2 == 1, "N must be odd"
    a = N
    b = (N * N - 1) // 2
    c = (N * N + 1) // 2
    assert a*a + b*b == c*c, "Triple verification failed"
    return (a, b, c)

def trivial_triple_even(k: int) -> Tuple[int, int, int]:
    """
    For any k > 1, construct the triple (2k, k²-1, k²+1).
    """
    a = 2 * k
    b = k * k - 1
    c = k * k + 1
    assert a*a + b*b == c*c, "Triple verification failed"
    return (a, b, c)

def trivial_triple(N: int) -> Tuple[int, int, int]:
    """Construct a trivial Pythagorean triple involving N."""
    if N % 2 == 1:
        return trivial_triple_odd(N)
    else:
        k = N // 2
        return trivial_triple_even(k)

# ============================================================
# §3. Berggren Tree Navigation
# ============================================================

def apply_berggren(triple: Tuple[int,int,int], matrix: np.ndarray) -> Tuple[int,int,int]:
    """Apply a Berggren matrix to a triple."""
    v = np.array(triple, dtype=object)
    result = matrix @ v
    a, b, c = int(result[0]), int(result[1]), int(result[2])
    # Normalize so that a, b > 0 (take absolute values of legs)
    return (abs(a), abs(b), abs(c))

def matrix_power(M: np.ndarray, k: int) -> np.ndarray:
    """Compute M^k using repeated squaring — O(log k) multiplications."""
    if k == 0:
        return np.eye(3, dtype=object)
    if k == 1:
        return M.copy()
    if k % 2 == 0:
        half = matrix_power(M, k // 2)
        return half @ half
    else:
        return M @ matrix_power(M, k - 1)

def skip_ahead(triple: Tuple[int,int,int], branch: int, depth: int) -> Tuple[int,int,int]:
    """
    Skip ahead `depth` levels along a single branch using matrix exponentiation.
    branch: 0 = B₁, 1 = B₂, 2 = B₃
    This computes B_i^depth · v in O(log depth) matrix multiplications.
    """
    M = matrix_power(BERGGREN_MATRICES[branch], depth)
    v = np.array(triple, dtype=object)
    result = M @ v
    return (abs(int(result[0])), abs(int(result[1])), abs(int(result[2])))

# ============================================================
# §4. Factor Extraction via GCD
# ============================================================

def extract_factor(triple: Tuple[int,int,int], N: int) -> Optional[int]:
    """
    Given a Pythagorean triple (a, b, c), check if gcd(a, N) or gcd(b, N)
    reveals a nontrivial factor of N.
    """
    a, b, c = triple
    for x in [a, b, c - b, c + b, c - a, c + a]:
        g = gcd(abs(x), N)
        if 1 < g < N:
            return g
    return None

# ============================================================
# §5. The Hyperbolic Skip-Ahead Factoring Algorithm
# ============================================================

def hyperbolic_factor(N: int, max_depth: int = 100, verbose: bool = True) -> Optional[int]:
    """
    Factor N using the Hyperbolic Skip-Ahead method.
    
    Algorithm:
    1. Construct trivial Pythagorean triple from N
    2. For each branch (B₁, B₂, B₃):
       a. Use exponentially increasing skip depths: 1, 2, 4, 8, ...
       b. At each depth, check if the resulting triple reveals a factor via GCD
    3. Also try mixed paths (combinations of branches)
    
    Returns a nontrivial factor of N, or None if not found within budget.
    """
    if N <= 1:
        return None
    if N % 2 == 0:
        return 2
    
    # Phase 1: Trivial triple
    seed = trivial_triple(N)
    if verbose:
        print(f"\n{'='*70}")
        print(f"  HYPERBOLIC SKIP-AHEAD FACTORING")
        print(f"{'='*70}")
        print(f"  Target: N = {N}")
        print(f"  Seed triple: ({seed[0]}, {seed[1]}, {seed[2]})")
        print(f"  Verification: {seed[0]}² + {seed[1]}² = {seed[0]**2 + seed[1]**2}")
        print(f"                {seed[2]}² = {seed[2]**2}")
        print(f"  c - b = {seed[2] - seed[1]}  (trivial — no factor info)")
        print(f"{'='*70}\n")
    
    # Phase 2: Navigate the tree
    triples_checked = 0
    
    # Strategy A: Single-branch skip-ahead with exponential depths
    for branch_idx in range(3):
        current = seed
        depth = 1
        while depth <= max_depth:
            jumped = skip_ahead(seed, branch_idx, depth)
            triples_checked += 1
            
            factor = extract_factor(jumped, N)
            if factor is not None:
                if verbose:
                    print(f"  ✓ FACTOR FOUND via {BRANCH_NAMES[branch_idx]} at depth {depth}")
                    print(f"    Triple: ({jumped[0]}, {jumped[1]}, {jumped[2]})")
                    print(f"    Factor: {factor}")
                    print(f"    N = {factor} × {N // factor}")
                    print(f"    Triples checked: {triples_checked}")
                return factor
            
            if verbose and depth <= 8:
                print(f"  Branch {BRANCH_NAMES[branch_idx]}, depth {depth}: "
                      f"a={jumped[0]}, hyp={jumped[2]}, "
                      f"gcd(a,N)={gcd(jumped[0], N)}, gcd(b,N)={gcd(jumped[1], N)}")
            
            depth *= 2  # Exponential skip-ahead
    
    # Strategy B: Mixed paths — try all length-2 and length-3 combinations
    if verbose:
        print(f"\n  Trying mixed paths...")
    
    for i in range(3):
        for j in range(3):
            M = BERGGREN_MATRICES[i] @ BERGGREN_MATRICES[j]
            for power in [1, 2, 4, 8, 16, 32]:
                Mp = matrix_power(M, power)
                v = np.array(seed, dtype=object)
                result = Mp @ v
                triple = (abs(int(result[0])), abs(int(result[1])), abs(int(result[2])))
                triples_checked += 1
                
                factor = extract_factor(triple, N)
                if factor is not None:
                    if verbose:
                        print(f"  ✓ FACTOR FOUND via mixed path B{i+1}·B{j+1} at power {power}")
                        print(f"    Factor: {factor}, N = {factor} × {N // factor}")
                        print(f"    Triples checked: {triples_checked}")
                    return factor
    
    # Strategy C: Start from (3,4,5) and navigate with skip-ahead
    if verbose:
        print(f"\n  Trying from root (3,4,5)...")
    
    root = (3, 4, 5)
    for branch_idx in range(3):
        for depth in [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]:
            jumped = skip_ahead(root, branch_idx, depth)
            triples_checked += 1
            
            factor = extract_factor(jumped, N)
            if factor is not None:
                if verbose:
                    print(f"  ✓ FACTOR FOUND from root via {BRANCH_NAMES[branch_idx]} depth {depth}")
                    print(f"    Factor: {factor}, N = {factor} × {N // factor}")
                    print(f"    Triples checked: {triples_checked}")
                return factor
    
    if verbose:
        print(f"\n  No factor found within budget. Triples checked: {triples_checked}")
    return None


# ============================================================
# §6. Comparison with Trial Division
# ============================================================

def trial_division(N: int) -> Optional[int]:
    """Simple trial division up to √N."""
    if N % 2 == 0:
        return 2
    i = 3
    while i * i <= N:
        if N % i == 0:
            return i
        i += 2
    return None


# ============================================================
# §7. Demonstration
# ============================================================

def demonstrate_trivial_triples():
    """Show trivial triple construction for various N."""
    print("\n" + "="*70)
    print("  PHASE 1: TRIVIAL PYTHAGOREAN TRIPLE CONSTRUCTION")
    print("="*70)
    
    test_values = [15, 21, 35, 77, 91, 143, 221, 323, 1001, 10001]
    
    print(f"\n  {'N':>8}  {'a':>8}  {'b':>15}  {'c':>15}  {'c-b':>5}  {'Verified':>8}")
    print(f"  {'─'*8}  {'─'*8}  {'─'*15}  {'─'*15}  {'─'*5}  {'─'*8}")
    
    for N in test_values:
        if N % 2 == 0:
            continue
        a, b, c = trivial_triple_odd(N)
        verified = a*a + b*b == c*c
        print(f"  {N:>8}  {a:>8}  {b:>15}  {c:>15}  {c-b:>5}  {'✓' if verified else '✗':>8}")

def demonstrate_skip_ahead():
    """Show how skip-ahead produces triples at various depths."""
    print("\n" + "="*70)
    print("  PHASE 2: HYPERBOLIC SKIP-AHEAD DEMONSTRATION")
    print("="*70)
    
    seed = (3, 4, 5)
    print(f"\n  Starting from root: {seed}")
    print(f"\n  Middle branch (B₂) skip-ahead:\n")
    print(f"  {'Depth':>8}  {'a':>20}  {'b':>20}  {'c':>20}  {'log₁₀(c)':>10}")
    print(f"  {'─'*8}  {'─'*20}  {'─'*20}  {'─'*20}  {'─'*10}")
    
    for depth in [1, 2, 4, 8, 16, 32, 64, 128]:
        a, b, c = skip_ahead(seed, 1, depth)
        log_c = len(str(c))
        # Truncate display for huge numbers
        a_str = str(a)[:18] + ".." if len(str(a)) > 20 else str(a)
        b_str = str(b)[:18] + ".." if len(str(b)) > 20 else str(b)
        c_str = str(c)[:18] + ".." if len(str(c)) > 20 else str(c)
        print(f"  {depth:>8}  {a_str:>20}  {b_str:>20}  {c_str:>20}  {log_c:>10}")

def demonstrate_factoring():
    """Demo the full factoring algorithm."""
    print("\n" + "="*70)
    print("  FULL FACTORING DEMONSTRATIONS")
    print("="*70)
    
    test_composites = [
        15, 21, 35, 77, 91, 143, 221, 323, 437, 667,
        1001, 1147, 2021, 3599, 4757, 10403,
        # Larger semiprimes
        104729 * 3,  # ~300K
    ]
    
    print(f"\n  {'N':>10}  {'Factor':>10}  {'Other':>10}  {'Triples':>10}  {'Method':>20}")
    print(f"  {'─'*10}  {'─'*10}  {'─'*10}  {'─'*10}  {'─'*20}")
    
    for N in test_composites:
        factor = hyperbolic_factor(N, max_depth=1000, verbose=False)
        if factor:
            print(f"  {N:>10}  {factor:>10}  {N//factor:>10}  {'':>10}  {'Hyp. Skip-Ahead':>20}")
        else:
            # Fall back to trial division
            factor = trial_division(N)
            if factor:
                print(f"  {N:>10}  {factor:>10}  {N//factor:>10}  {'':>10}  {'Trial Division':>20}")
            else:
                print(f"  {N:>10}  {'PRIME?':>10}  {'':>10}  {'':>10}  {'N/A':>20}")

def demonstrate_tree_structure():
    """Show the first few levels of the Berggren tree."""
    print("\n" + "="*70)
    print("  BERGGREN TREE STRUCTURE (First 3 levels)")
    print("="*70)
    
    def print_tree(triple, depth, max_depth, prefix=""):
        a, b, c = triple
        print(f"  {prefix}({a}, {b}, {c})  [a²+b²={a*a+b*b}, c²={c*c}]")
        if depth < max_depth:
            for i, name in enumerate(["L", "M", "R"]):
                child = apply_berggren(triple, BERGGREN_MATRICES[i])
                child_prefix = prefix + "  "
                print_tree(child, depth + 1, max_depth, child_prefix)
    
    print()
    print_tree((3, 4, 5), 0, 2)

def main():
    if len(sys.argv) > 1:
        N = int(sys.argv[1])
        print(f"\nFactoring N = {N}")
        factor = hyperbolic_factor(N, verbose=True)
        if factor:
            print(f"\nResult: {N} = {factor} × {N // factor}")
        else:
            print(f"\nNo factor found (N may be prime)")
        return
    
    # Full interactive demo
    print("\n" + "▓"*70)
    print("▓" + " "*68 + "▓")
    print("▓  HYPERBOLIC SKIP-AHEAD FACTORING                                  ▓")
    print("▓  via Pythagorean Triple Trees                                      ▓")
    print("▓" + " "*68 + "▓")
    print("▓"*70)
    
    demonstrate_trivial_triples()
    demonstrate_tree_structure()
    demonstrate_skip_ahead()
    demonstrate_factoring()
    
    # Detailed walkthrough for N = 91 = 7 × 13
    print("\n" + "="*70)
    print("  DETAILED WALKTHROUGH: N = 91")
    print("="*70)
    hyperbolic_factor(91, max_depth=100, verbose=True)
    
    # Detailed walkthrough for N = 221 = 13 × 17
    print("\n" + "="*70)
    print("  DETAILED WALKTHROUGH: N = 221")
    print("="*70)
    hyperbolic_factor(221, max_depth=100, verbose=True)
    
    print("\n" + "="*70)
    print("  MATHEMATICAL FOUNDATIONS")
    print("="*70)
    print("""
  Key Identity:
    For any Pythagorean triple (a, b, c) with a² + b² = c²:
      (c - b)(c + b) = a²
    
    If a shares a factor with N, then gcd(a, N) reveals it.
  
  Trivial Triple:
    For odd N: (N, (N²-1)/2, (N²+1)/2) is Pythagorean
    But c - b = 1, giving the trivial factorization.
  
  Berggren Tree Navigation:
    Three matrices B₁, B₂, B₃ generate ALL primitive Pythagorean triples.
    Each preserves a² + b² = c² (Lorentz isometries of the light cone).
  
  Hyperbolic Skip-Ahead:
    Matrix exponentiation: B_i^k computed in O(log k) multiplications.
    This "skips" k levels of the tree, reaching triples with
    hypotenuses ~ 3^k × c₀ in logarithmic time.
  
  Factor Extraction:
    At each visited triple (a', b', c'), compute:
      gcd(a', N),  gcd(b', N),  gcd(c'-b', N),  gcd(c'+b', N)
    Any nontrivial GCD immediately yields a factor of N.
""")

if __name__ == "__main__":
    main()

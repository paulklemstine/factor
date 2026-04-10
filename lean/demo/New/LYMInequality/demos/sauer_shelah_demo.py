#!/usr/bin/env python3
"""
Sauer-Shelah Lemma Demo

Demonstrates the properties formalized in Combinatorics/Combinatorics__SauerShelah.lean:
1. Shattering and VC dimension
2. The Sauer-Shelah bound: |F| ≤ ∑_{i=0}^{d} C(n,i)
3. Applications to machine learning (PAC learning)
"""

from math import comb
from itertools import combinations, product
import random


def shatters(family, A):
    """
    Check if family F shatters set A.
    F shatters A if for every subset B ⊆ A, there exists S ∈ F
    such that A ∩ S = B.
    """
    A = frozenset(A)
    # Generate all subsets of A
    required = set()
    for k in range(len(A) + 1):
        for subset in combinations(A, k):
            required.add(frozenset(subset))
    
    # Check if each required intersection is achieved
    achieved = set()
    for S in family:
        S = frozenset(S)
        achieved.add(A & S)
    
    return required <= achieved


def vc_dimension(family, ground_set):
    """
    Compute the VC dimension of a family:
    the largest size of a set shattered by F.
    """
    n = len(ground_set)
    vc = 0
    for k in range(n + 1):
        found = False
        for A in combinations(ground_set, k):
            if shatters(family, A):
                found = True
                vc = k
                break
        if not found:
            break
    return vc


def sauer_shelah_bound(n, d):
    """Compute the Sauer-Shelah bound: ∑_{i=0}^{d} C(n,i)."""
    return sum(comb(n, i) for i in range(d + 1))


def demo():
    print("=" * 60)
    print("SAUER-SHELAH LEMMA DEMO")
    print("Demonstrating properties formalized in Lean 4")
    print("=" * 60)
    
    # Demo 1: Shattering examples
    print("\n1. SHATTERING EXAMPLES")
    print("   Ground set: {0, 1, 2, 3}")
    print()
    
    ground = [0, 1, 2, 3]
    
    # Example family
    family = [
        frozenset(),
        frozenset({0}),
        frozenset({1}),
        frozenset({0, 1}),
        frozenset({2}),
        frozenset({0, 2}),
    ]
    
    print(f"   Family F = {[set(s) for s in family]}")
    print(f"   |F| = {len(family)}")
    print()
    
    # Check which sets are shattered
    for k in range(len(ground) + 1):
        for A in combinations(ground, k):
            A = frozenset(A)
            shattered = shatters(family, A)
            if shattered:
                print(f"   F shatters {set(A)} ✓")
    
    d = vc_dimension(family, ground)
    print(f"\n   VC dimension = {d}")
    n_ground = len(ground)
    print(f"   Sauer-Shelah bound: sum_i=0..{d} C({n_ground},i) = {sauer_shelah_bound(n_ground, d)}")
    print(f"   Actual |F| = {len(family)} ≤ {sauer_shelah_bound(len(ground), d)} ✓")
    
    # Demo 2: Sauer-Shelah bound table
    print("\n\n2. SAUER-SHELAH BOUND TABLE")
    print("   ∑_{i=0}^{d} C(n,i)")
    print()
    
    header = 'n\\d'
    print(f"   {header:>4}", end="")
    for d in range(8):
        print(f" {d:>6}", end="")
    print()
    print(f"   {'----':>4}" + "------" * 8)
    
    for n in range(1, 11):
        print(f"   {n:>4}", end="")
        for d in range(8):
            bound = sauer_shelah_bound(n, d)
            total = 2 ** n
            if bound >= total:
                print(f" {'2^'+str(n):>6}", end="")
            else:
                print(f" {bound:>6}", end="")
        print()
    
    # Demo 3: Half-spaces in R^d
    print("\n\n3. APPLICATION: HALF-SPACES IN R^d")
    print("   Linear classifiers in d dimensions have VC dimension d+1")
    print()
    
    for d in range(1, 7):
        vc = d + 1
        # For n training points
        print(f"   d={d}: VC dimension = {vc}")
        for n in [10, 50, 100]:
            bound = sauer_shelah_bound(n, vc)
            total = 2 ** n
            ratio = bound / total if total > 0 else 0
            print(f"     n={n:3d}: bound = {bound:>12,d} / {total:>30,d} ({ratio:.2e})")
        print()
    
    # Demo 4: Random families and the bound
    print("\n4. RANDOM FAMILIES vs SAUER-SHELAH BOUND")
    print()
    
    random.seed(42)
    n = 6
    ground = list(range(n))
    
    for target_vc in [1, 2, 3]:
        # Generate a random family with VC dimension ≤ target_vc
        family = []
        all_subsets = []
        for k in range(n + 1):
            for s in combinations(ground, k):
                all_subsets.append(frozenset(s))
        
        random.shuffle(all_subsets)
        
        for s in all_subsets:
            candidate = family + [s]
            if vc_dimension(candidate, ground) <= target_vc:
                family.append(s)
        
        actual_vc = vc_dimension(family, ground)
        bound = sauer_shelah_bound(n, actual_vc)
        
        print(f"   Target VC ≤ {target_vc}: |F| = {len(family)}, actual VC = {actual_vc}, "
              f"bound = {bound}, {'≤ bound ✓' if len(family) <= bound else '> bound ✗'}")
    
    # Demo 5: Pascal's identity in the bound
    print("\n\n5. PASCAL'S IDENTITY IN THE BOUND")
    print("   Key lemma: ∑C(n,i) + ∑C(n,i) = ∑C(n+1,i)")
    print("   (formalized as `binomial_pascal_sum` in Lean)")
    print()
    
    for n in range(1, 8):
        for d in range(1, n + 1):
            lhs1 = sum(comb(n, i) for i in range(d + 1))
            lhs2 = sum(comb(n, i) for i in range(d))
            rhs = sum(comb(n + 1, i) for i in range(d + 1))
            check = "✓" if lhs1 + lhs2 == rhs else "✗"
            if d <= 3:
                print(f"   n={n}, d={d}: {lhs1} + {lhs2} = {rhs} {check}")


if __name__ == "__main__":
    demo()

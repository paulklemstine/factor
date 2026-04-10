#!/usr/bin/env python3
"""
LYM Inequality and Sperner's Theorem Demo

Demonstrates the properties formalized in New/New__LYMInequality.lean:
1. The LYM inequality: ∑ 1/C(n,|A|) ≤ 1 for antichains
2. Sperner's theorem: max antichain size = C(n, ⌊n/2⌋)
3. The permutation-counting proof idea
"""

from math import comb, factorial
from itertools import combinations
import random


def is_antichain(family):
    """Check if a family of sets is an antichain (no set contains another)."""
    sets = [frozenset(s) for s in family]
    for i, A in enumerate(sets):
        for j, B in enumerate(sets):
            if i != j and A <= B:
                return False
    return True


def lym_sum(n, family):
    """Compute ∑_{A ∈ family} 1/C(n, |A|)."""
    return sum(1.0 / comb(n, len(A)) for A in family)


def count_chains_through(n, A):
    """
    Count the number of maximal chains in 2^[n] that pass through A.
    A maximal chain corresponds to a permutation of [n].
    The chains through A are those permutations where A = {σ(1),...,σ(|A|)}.
    Count = |A|! * (n - |A|)!
    """
    k = len(A)
    return factorial(k) * factorial(n - k)


def all_subsets(n):
    """Generate all subsets of {0, 1, ..., n-1}."""
    result = []
    for k in range(n + 1):
        for combo in combinations(range(n), k):
            result.append(frozenset(combo))
    return result


def largest_antichain(n):
    """The largest antichain in 2^[n]: all sets of size ⌊n/2⌋."""
    return [frozenset(c) for c in combinations(range(n), n // 2)]


def random_antichain(n, attempts=100):
    """Generate a random antichain by greedy selection."""
    all_sets = all_subsets(n)
    random.shuffle(all_sets)
    antichain = []
    for s in all_sets:
        candidate = antichain + [s]
        if is_antichain(candidate):
            antichain.append(s)
    return antichain


def demo():
    print("=" * 60)
    print("LYM INEQUALITY & SPERNER'S THEOREM DEMO")
    print("Demonstrating properties formalized in Lean 4")
    print("=" * 60)
    
    # Demo 1: LYM inequality verification
    print("\n1. LYM INEQUALITY VERIFICATION")
    print("   For antichains in 2^[n], ∑ 1/C(n,|A|) ≤ 1")
    print()
    
    for n in range(3, 8):
        # The maximum antichain (middle layer)
        max_ac = largest_antichain(n)
        lym = lym_sum(n, max_ac)
        print(f"   n={n}: Middle layer (size {len(max_ac)}), LYM sum = {lym:.4f} {'≤ 1 ✓' if lym <= 1.0001 else '> 1 ✗'}")
        
        # A random antichain
        random.seed(42 + n)
        rand_ac = random_antichain(n)
        lym_rand = lym_sum(n, rand_ac)
        print(f"         Random antichain (size {len(rand_ac)}), LYM sum = {lym_rand:.4f} {'≤ 1 ✓' if lym_rand <= 1.0001 else '> 1 ✗'}")
    
    # Demo 2: Sperner's theorem
    print("\n\n2. SPERNER'S THEOREM")
    print("   Max antichain size in 2^[n] = C(n, ⌊n/2⌋)")
    print()
    
    print(f"   {'n':>3} | {'C(n,⌊n/2⌋)':>12} | {'Middle layer':>12} | {'All subsets':>10} | {'Ratio':>8}")
    print(f"   {'---':>3}-+-{'---':>12}-+-{'---':>12}-+-{'---':>10}-+-{'---':>8}")
    
    for n in range(1, 11):
        sperner = comb(n, n // 2)
        total = 2 ** n
        ratio = sperner / total
        print(f"   {n:3d} | {sperner:12d} | {sperner:12d} | {total:10d} | {ratio:8.4f}")
    
    # Demo 3: Permutation counting (proof idea)
    print("\n\n3. PERMUTATION COUNTING (PROOF IDEA)")
    print("   For each set A of size k, there are k!(n-k)! chains through A")
    print()
    
    n = 4
    print(f"   Ground set: {{0, 1, 2, 3}} (n={n})")
    print(f"   Total permutations: {n}! = {factorial(n)}")
    print()
    
    # Example antichain: {{0,1}, {2,3}, {0,3}, {1,2}}
    antichain = [frozenset({0, 1}), frozenset({2, 3}), frozenset({0, 3}), frozenset({1, 2})]
    print(f"   Antichain: {[set(s) for s in antichain]}")
    print(f"   Is antichain: {is_antichain(antichain)} ✓")
    print()
    
    total_chains = 0
    for A in antichain:
        k = len(A)
        chains = count_chains_through(n, A)
        total_chains += chains
        print(f"   Set {set(A)}: |A|={k}, chains = {k}!×{n-k}! = {chains}")
    
    print(f"\n   Total chains used: {total_chains} ≤ {factorial(n)} = {n}!")
    print(f"   LYM sum: {total_chains}/{factorial(n)} = {total_chains/factorial(n):.4f} ≤ 1 ✓")
    
    # Demo 4: Why antichains matter
    print("\n\n4. ANTICHAINS IN PRACTICE")
    print("   Non-redundant feature sets for a classifier with 5 features")
    print()
    
    n = 5
    features = ['color', 'size', 'shape', 'texture', 'weight']
    
    # An antichain of feature sets
    feature_sets = [
        frozenset({0, 1}),     # {color, size}
        frozenset({2, 3, 4}),  # {shape, texture, weight}
        frozenset({0, 3}),     # {color, texture}
        frozenset({1, 4}),     # {size, weight}
        frozenset({2}),        # NOT in antichain with {2,3,4}
    ]
    
    # Filter to get a valid antichain
    antichain = []
    for s in feature_sets:
        candidate = antichain + [s]
        if is_antichain(candidate):
            antichain.append(s)
    
    print(f"   Valid antichain of feature sets (from {len(feature_sets)} candidates):")
    for s in antichain:
        names = ', '.join(features[i] for i in sorted(s))
        print(f"     {{{names}}}")
    print(f"\n   Antichain size: {len(antichain)}")
    print(f"   Sperner bound: C({n}, {n//2}) = {comb(n, n//2)}")
    print(f"   LYM sum: {lym_sum(n, antichain):.4f} ≤ 1")
    
    # Demo 5: Exhaustive verification for small n
    print("\n\n5. EXHAUSTIVE VERIFICATION (n=4)")
    print("   Checking LYM inequality for ALL antichains in 2^[4]")
    print()
    
    n = 4
    all_sets_list = all_subsets(n)
    max_lym = 0
    max_ac = None
    count = 0
    
    # Check all antichains up to size 7 (exhaustive is too expensive for large)
    for size in range(1, 8):
        for combo in combinations(all_sets_list, size):
            if is_antichain(combo):
                count += 1
                lym = lym_sum(n, combo)
                if lym > max_lym:
                    max_lym = lym
                    max_ac = combo
    
    print(f"   Checked {count} antichains")
    print(f"   Maximum LYM sum: {max_lym:.6f}")
    print(f"   Achieved by: {[set(s) for s in max_ac]}")
    print(f"   LYM inequality holds for all: {'✓' if max_lym <= 1.0001 else '✗'}")


if __name__ == "__main__":
    demo()

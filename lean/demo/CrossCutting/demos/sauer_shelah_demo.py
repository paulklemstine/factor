#!/usr/bin/env python3
"""
Sauer-Shelah and Idempotent Restriction Demo

Demonstrates:
1. The restriction operator is idempotent
2. The Sauer-Shelah bound on shattered sets
3. Binomial sum bounds
"""
import numpy as np
from itertools import combinations
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from math import comb

def restrict_family(F, S):
    """Restrict a family of sets to a subset S."""
    return frozenset(A.intersection(S) for A in F)

def shatters(F, S):
    """Check if F shatters S."""
    restrictions = {A.intersection(S) for A in F}
    powerset = {frozenset(combo) for r in range(len(S)+1)
                for combo in combinations(S, r)}
    return powerset.issubset(restrictions)

def vc_dimension(F, universe):
    """Compute the VC dimension of a set family."""
    vc = 0
    for d in range(len(universe) + 1):
        found = False
        for S in combinations(universe, d):
            if shatters(F, frozenset(S)):
                found = True
                break
        if found:
            vc = d
        else:
            break
    return vc

def binomial_sum(n, d):
    """Sum of C(n,i) for i = 0 to d."""
    return sum(comb(n, i) for i in range(d + 1))

def main():
    print("=== Sauer-Shelah and Idempotent Restriction ===\n")

    # Demo 1: Restriction is idempotent
    print("--- Demo 1: Restriction Idempotence ---")
    universe = frozenset(range(5))
    F = [frozenset(s) for s in [{0,1,2}, {1,2,3}, {0,3,4}, {2,4}, {0,1,3,4}]]
    S = frozenset({0, 1, 2})

    R1 = restrict_family(F, S)
    R2 = restrict_family(R1, S)
    print(f"Family F: {[set(s) for s in F]}")
    print(f"S = {set(S)}")
    print(f"restrict(F, S) = {[set(s) for s in R1]}")
    print(f"restrict(restrict(F, S), S) = {[set(s) for s in R2]}")
    print(f"Idempotent: R1 == R2: {R1 == R2}")
    print()

    # Demo 2: Shattering examples
    print("--- Demo 2: Shattering ---")
    # A family with VC dimension 2
    F_vc2 = [frozenset(s) for s in [set(), {0}, {1}, {2}, {0,1}, {0,2}, {1,2}]]
    universe_small = frozenset(range(3))
    vc = vc_dimension(F_vc2, universe_small)
    print(f"Family: {[set(s) for s in F_vc2]}")
    print(f"Universe: {set(universe_small)}")
    print(f"VC dimension: {vc}")
    print(f"Shatters {{0,1}}: {shatters(F_vc2, frozenset({0,1}))}")
    print(f"Shatters {{0,1,2}}: {shatters(F_vc2, frozenset({0,1,2}))}")
    print()

    # Demo 3: Binomial sum bounds
    print("--- Demo 3: Binomial Sum Bounds ---")
    for n in [5, 10, 20]:
        for d in [1, 2, 3, n]:
            bs = binomial_sum(n, d)
            bound = 2**n
            print(f"  binomialSum({n}, {d}) = {bs:>8} ≤ 2^{n} = {bound}")
    print()

    # Plot
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # 1. Binomial sum vs 2^n
    ax = axes[0]
    ns = range(1, 21)
    for d in [1, 2, 3, 5, 10]:
        ax.semilogy(list(ns), [binomial_sum(n, d) for n in ns],
                     '-o', markersize=3, label=f'd={d}')
    ax.semilogy(list(ns), [2**n for n in ns], 'k--', linewidth=2, label='2^n')
    ax.set_xlabel('n (universe size)', fontsize=12)
    ax.set_ylabel('Binomial sum Σ C(n,i), i≤d', fontsize=12)
    ax.set_title('Sauer-Shelah Bound', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 2. VC dimension visualization
    ax = axes[1]
    # Generate random families of increasing size and compute VC dim
    np.random.seed(42)
    n_universe = 6
    sizes = range(1, 2**n_universe + 1, 2)
    vc_dims = []
    for size in sizes:
        # Random family of `size` subsets
        all_subsets = [frozenset(s) for k in range(n_universe+1)
                       for s in combinations(range(n_universe), k)]
        idx = np.random.choice(len(all_subsets), min(size, len(all_subsets)), replace=False)
        F_rand = [all_subsets[i] for i in idx]
        vc = vc_dimension(F_rand, frozenset(range(n_universe)))
        vc_dims.append(vc)
    ax.scatter(list(sizes), vc_dims, s=10, alpha=0.7, c='blue')
    ax.set_xlabel('Family size |F|', fontsize=12)
    ax.set_ylabel('VC dimension', fontsize=12)
    ax.set_title(f'VC Dimension vs Family Size (n={n_universe})', fontsize=14)
    ax.grid(True, alpha=0.3)

    # 3. Restriction size (idempotent collapse)
    ax = axes[2]
    n_test = 8
    all_subs = [frozenset(s) for k in range(n_test+1)
                for s in combinations(range(n_test), k)]
    original_sizes = []
    restricted_sizes = []
    for _ in range(200):
        size = np.random.randint(1, len(all_subs)+1)
        idx = np.random.choice(len(all_subs), size, replace=False)
        F_rand = [all_subs[i] for i in idx]
        S_size = np.random.randint(1, n_test+1)
        S = frozenset(np.random.choice(n_test, S_size, replace=False))
        R = restrict_family(F_rand, S)
        original_sizes.append(len(F_rand))
        restricted_sizes.append(len(R))
    ax.scatter(original_sizes, restricted_sizes, s=10, alpha=0.5, c='green')
    ax.plot([0, max(original_sizes)], [0, max(original_sizes)], 'k--', alpha=0.3,
            label='y=x (no collapse)')
    ax.set_xlabel('Original family size |F|', fontsize=12)
    ax.set_ylabel('Restricted family size |F|_S|', fontsize=12)
    ax.set_title('Idempotent Restriction Collapse', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('/workspace/request-project/CrossCutting/demos/sauer_shelah.png',
                dpi=150, bbox_inches='tight')
    print("Saved: sauer_shelah.png")

if __name__ == '__main__':
    main()

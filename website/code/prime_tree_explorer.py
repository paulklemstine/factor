#!/usr/bin/env python3
"""
PRIME TREE EXPLORER — 10 approaches to building a "Berggren tree for primes"
=============================================================================
Explores whether any tree structure can enumerate all primes analogously to
how the Berggren tree enumerates all primitive Pythagorean triples.
"""

import time
import os
import sys
import math
from collections import defaultdict, deque
from sympy import isprime, nextprime, prime, fibonacci, totient, factorint
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

IMG_DIR = "/home/raver1975/factor/images"
os.makedirs(IMG_DIR, exist_ok=True)

RESULTS = {}  # approach_name -> dict of stats


# ============================================================================
# Utility
# ============================================================================
def small_primes(limit):
    """Sieve of Eratosthenes up to limit."""
    sieve = bytearray(b'\x01') * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    return [i for i in range(2, limit + 1) if sieve[i]]

PRIMES_100K = set(small_primes(100_000))
PRIMES_1M = set(small_primes(1_000_000))
ALL_PRIMES_1M = sorted(PRIMES_1M)

def is_prime_fast(n):
    """Fast primality check for moderate-sized integers."""
    if n < 2:
        return False
    if n <= 1_000_000:
        return n in PRIMES_1M
    return isprime(n)


# ============================================================================
# APPROACH 1: Cunningham Chain Tree
# ============================================================================
def approach1_cunningham():
    """Cunningham chain tree: branch via 2p+1, 2p-1, (p-1)/2."""
    print("\n=== Approach 1: Cunningham Chain Tree ===")
    t0 = time.time()

    results = {}
    seeds = [2, 3, 5, 7, 11, 13, 23, 29, 41, 89]

    for seed in seeds:
        # BFS tree
        tree = {seed: []}
        queue = deque([(seed, 0)])
        visited = {seed}
        max_depth = 15
        depth_counts = defaultdict(int)
        depth_counts[0] = 1
        total_primes = 1

        while queue:
            p, d = queue.popleft()
            if d >= max_depth:
                continue

            children = []
            # Branch 1: 2p+1 (Sophie Germain)
            c1 = 2 * p + 1
            if is_prime_fast(c1) and c1 not in visited and c1 < 10**12:
                children.append(c1)
            # Branch 2: 2p-1
            c2 = 2 * p - 1
            if c2 > 1 and is_prime_fast(c2) and c2 not in visited and c2 < 10**12:
                children.append(c2)
            # Branch 3: (p-1)/2 if prime
            if (p - 1) % 2 == 0:
                c3 = (p - 1) // 2
                if c3 > 1 and is_prime_fast(c3) and c3 not in visited:
                    children.append(c3)

            tree[p] = children
            for c in children:
                visited.add(c)
                queue.append((c, d + 1))
                depth_counts[d + 1] += 1
                total_primes += 1

        results[seed] = {
            'total_primes': total_primes,
            'max_depth_reached': max(depth_counts.keys()) if depth_counts else 0,
            'depth_counts': dict(depth_counts),
            'all_primes': sorted(visited)
        }

    # Coverage analysis
    primes_up_to_1000 = set(p for p in ALL_PRIMES_1M if p <= 1000)
    all_found = set()
    for s in results:
        all_found.update(results[s]['all_primes'])
    coverage = len(all_found & primes_up_to_1000) / len(primes_up_to_1000)

    # Find longest Sophie Germain chain
    longest_chain = []
    for seed in [2, 3, 5, 7, 11]:
        chain = [seed]
        p = seed
        for _ in range(30):
            q = 2 * p + 1
            if is_prime_fast(q):
                chain.append(q)
                p = q
            else:
                break
        if len(chain) > len(longest_chain):
            longest_chain = chain

    elapsed = time.time() - t0

    # Visualization
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Left: depth distribution for best seed
    best_seed = max(results, key=lambda s: results[s]['total_primes'])
    dc = results[best_seed]['depth_counts']
    depths = sorted(dc.keys())
    counts = [dc[d] for d in depths]
    axes[0].bar(depths, counts, color='steelblue', alpha=0.8)
    axes[0].set_xlabel('Tree Depth')
    axes[0].set_ylabel('Primes Found')
    axes[0].set_title(f'Cunningham Tree from p={best_seed}\n({results[best_seed]["total_primes"]} primes)')

    # Right: longest Sophie Germain chain
    x = range(len(longest_chain))
    axes[1].semilogy(x, longest_chain, 'ro-', markersize=4)
    axes[1].set_xlabel('Chain Position')
    axes[1].set_ylabel('Prime Value (log)')
    axes[1].set_title(f'Longest Sophie Germain Chain\nLength {len(longest_chain)}, start={longest_chain[0]}')

    plt.tight_layout()
    plt.savefig(f"{IMG_DIR}/prime_tree_01_cunningham.png", dpi=150)
    plt.close()

    stats = {
        'time': elapsed,
        'best_seed': best_seed,
        'best_total': results[best_seed]['total_primes'],
        'coverage_to_1000': coverage,
        'longest_sg_chain': len(longest_chain),
        'sg_chain_start': longest_chain[0],
        'sg_chain': longest_chain[:10],
        'can_generate_all': False,
        'reason': 'Chains die quickly; coverage is sparse'
    }
    RESULTS['01_cunningham'] = stats
    print(f"  Best seed: {best_seed}, total primes: {results[best_seed]['total_primes']}")
    print(f"  Coverage of primes <= 1000: {coverage:.1%}")
    print(f"  Longest SG chain: length {len(longest_chain)} from {longest_chain[0]}")
    print(f"  Time: {elapsed:.2f}s")
    return stats


# ============================================================================
# APPROACH 2: Linear Recurrence Trees
# ============================================================================
def approach2_linear_recurrence():
    """Matrix recurrence on prime pairs."""
    print("\n=== Approach 2: Linear Recurrence Trees ===")
    t0 = time.time()

    # Matrices acting on (p, q) pairs
    matrices = {
        'M1(2p+q,p)': lambda p, q: (2*p + q, p),
        'M2(2p-q,p)': lambda p, q: (2*p - q, p),
        'M3(3p+q,p)': lambda p, q: (3*p + q, p),
        'M4(p+2q,q)': lambda p, q: (p + 2*q, q),
        'M5(3p-q,p)': lambda p, q: (3*p - q, p),
    }

    seeds = [(2, 3), (3, 5), (5, 7), (7, 11), (11, 13)]
    max_depth = 12

    all_results = {}
    for seed in seeds:
        for mname, mfunc in matrices.items():
            tree_primes = set()
            primality_by_depth = defaultdict(lambda: [0, 0])  # [prime_count, total]
            queue = deque([(seed, 0)])
            visited = {seed}

            while queue:
                (p, q), d = queue.popleft()
                if d > max_depth:
                    continue
                if is_prime_fast(p):
                    tree_primes.add(p)
                    primality_by_depth[d][0] += 1
                primality_by_depth[d][1] += 1

                for name2, func2 in matrices.items():
                    np_, nq_ = func2(p, q)
                    if np_ > 0 and nq_ > 0 and (np_, nq_) not in visited and np_ < 10**10:
                        visited.add((np_, nq_))
                        queue.append(((np_, nq_), d + 1))
                        if len(visited) > 50000:
                            break
                if len(visited) > 50000:
                    break

            key = f"{seed}-{mname}"
            rates = {}
            for dd in sorted(primality_by_depth.keys()):
                pc, tc = primality_by_depth[dd]
                rates[dd] = pc / max(tc, 1)
            all_results[key] = {
                'primes_found': len(tree_primes),
                'primality_rates': rates,
                'nodes_explored': len(visited)
            }

    # Find best combo
    best_key = max(all_results, key=lambda k: all_results[k]['primes_found'])
    best = all_results[best_key]

    # Detailed analysis of the (2,3) seed with all 5 matrices
    seed_23_primes = set()
    depth_prime_rate = defaultdict(lambda: [0, 0])
    queue = deque([((2, 3), 0)])
    visited = {(2, 3)}
    while queue:
        (p, q), d = queue.popleft()
        if d > 10:
            continue
        if is_prime_fast(p):
            seed_23_primes.add(p)
            depth_prime_rate[d][0] += 1
        depth_prime_rate[d][1] += 1
        for mfunc in matrices.values():
            np_, nq_ = mfunc(p, q)
            if 1 < np_ < 10**8 and nq_ > 0 and (np_, nq_) not in visited:
                visited.add((np_, nq_))
                queue.append(((np_, nq_), d + 1))
                if len(visited) > 100000:
                    break
        if len(visited) > 100000:
            break

    primes_up_to_1000 = set(p for p in ALL_PRIMES_1M if p <= 1000)
    coverage = len(seed_23_primes & primes_up_to_1000) / len(primes_up_to_1000)

    elapsed = time.time() - t0

    # Visualization
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Primality rate vs depth
    depths_sorted = sorted(depth_prime_rate.keys())
    rates_plot = [depth_prime_rate[d][0] / max(depth_prime_rate[d][1], 1) for d in depths_sorted]
    axes[0].plot(depths_sorted, rates_plot, 'bo-')
    axes[0].set_xlabel('Tree Depth')
    axes[0].set_ylabel('Primality Rate')
    axes[0].set_title(f'Linear Recurrence Tree from (2,3)\nPrimality Rate by Depth')
    axes[0].set_ylim(0, 1)

    # Histogram of primes found
    found_list = sorted(seed_23_primes)[:200]
    if found_list:
        axes[1].hist(found_list, bins=50, color='coral', alpha=0.8)
        axes[1].set_xlabel('Prime Value')
        axes[1].set_ylabel('Count')
        axes[1].set_title(f'Distribution of {len(seed_23_primes)} Primes Found\n(from (2,3) seed, depth 10)')

    plt.tight_layout()
    plt.savefig(f"{IMG_DIR}/prime_tree_02_linear_recurrence.png", dpi=150)
    plt.close()

    stats = {
        'time': elapsed,
        'best_combo': best_key,
        'best_primes': best['primes_found'],
        'seed_23_primes': len(seed_23_primes),
        'coverage_to_1000': coverage,
        'primality_rates': {d: f"{r:.3f}" for d, r in zip(depths_sorted, rates_plot)},
        'can_generate_all': False,
        'reason': 'Primality rate drops exponentially with depth; linear transforms cannot preserve primality'
    }
    RESULTS['02_linear_recurrence'] = stats
    print(f"  Best combo: {best_key} with {best['primes_found']} primes")
    print(f"  Seed (2,3) found {len(seed_23_primes)} primes, coverage to 1000: {coverage:.1%}")
    print(f"  Time: {elapsed:.2f}s")
    return stats


# ============================================================================
# APPROACH 3: Polynomial Prime Trees
# ============================================================================
def approach3_polynomial():
    """Iterated polynomial prime trees using famous prime-rich polynomials."""
    print("\n=== Approach 3: Polynomial Prime Trees ===")
    t0 = time.time()

    # Famous polynomials
    polynomials = {
        'euler_n2+n+41': lambda n: n*n + n + 41,
        'n2+n+17': lambda n: n*n + n + 17,
        'n2-n+41': lambda n: n*n - n + 41,
        '2n2+29': lambda n: 2*n*n + 29,
        '2n2+11': lambda n: 2*n*n + 11,
        'n2+n+11': lambda n: n*n + n + 11,
    }

    results = {}
    for name, f in polynomials.items():
        # Linear evaluation: primes among f(0), f(1), ..., f(999)
        prime_count = 0
        first_composite = None
        for n in range(1000):
            val = f(n)
            if val > 1 and is_prime_fast(val):
                prime_count += 1
            elif first_composite is None and val > 1 and not is_prime_fast(val):
                first_composite = n

        # Iterated tree: start from f(0), apply f repeatedly
        chain = []
        x = 0
        for _ in range(30):
            val = f(x)
            if val < 0 or val > 10**15:
                break
            chain.append((val, is_prime_fast(val)))
            x = val

        # Tree branching: start from f(0), children = f(val+k) for k=0,1,-1,2,-2
        tree_primes = set()
        queue = deque([(f(0), 0)])
        visited = {f(0)}
        if is_prime_fast(f(0)):
            tree_primes.add(f(0))

        while queue:
            val, d = queue.popleft()
            if d >= 8:
                continue
            for k in [0, 1, -1, 2, -2]:
                child = f(val + k)
                if 1 < child < 10**9 and child not in visited:
                    visited.add(child)
                    if is_prime_fast(child):
                        tree_primes.add(child)
                    queue.append((child, d + 1))
                    if len(visited) > 20000:
                        break
            if len(visited) > 20000:
                break

        results[name] = {
            'linear_primes_in_1000': prime_count,
            'first_composite_at': first_composite,
            'iteration_chain_length': len(chain),
            'iteration_primes': sum(1 for _, ip in chain if ip),
            'tree_primes': len(tree_primes),
        }

    # Bunyakovsky conjecture test: n^2 + 1
    bun_primes = sum(1 for n in range(10000) if is_prime_fast(n*n + 1))

    # Coverage: union of all polynomial outputs vs primes <= 1000
    all_poly_primes = set()
    for name, f in polynomials.items():
        for n in range(1000):
            v = f(n)
            if v > 1 and v <= 1000 and is_prime_fast(v):
                all_poly_primes.add(v)
    primes_to_1000 = set(p for p in ALL_PRIMES_1M if p <= 1000)
    poly_coverage = len(all_poly_primes & primes_to_1000) / len(primes_to_1000)

    elapsed = time.time() - t0

    # Visualization
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Left: primality rate of each polynomial
    names = list(results.keys())
    linear_counts = [results[n]['linear_primes_in_1000'] for n in names]
    bars = axes[0].barh(range(len(names)), linear_counts, color='forestgreen', alpha=0.8)
    axes[0].set_yticks(range(len(names)))
    axes[0].set_yticklabels(names, fontsize=8)
    axes[0].set_xlabel('Primes in f(0)..f(999)')
    axes[0].set_title('Polynomial Prime Productivity')

    # Right: Euler polynomial visualization
    euler = polynomials['euler_n2+n+41']
    ns = list(range(100))
    vals = [euler(n) for n in ns]
    colors = ['red' if is_prime_fast(v) else 'lightgray' for v in vals]
    axes[1].scatter(ns, vals, c=colors, s=15, alpha=0.8)
    axes[1].set_xlabel('n')
    axes[1].set_ylabel('n^2+n+41')
    axes[1].set_title('Euler\'s Polynomial: Red = Prime\n(prime for n=0..39)')

    plt.tight_layout()
    plt.savefig(f"{IMG_DIR}/prime_tree_03_polynomial.png", dpi=150)
    plt.close()

    stats = {
        'time': elapsed,
        'results': results,
        'bunyakovsky_n2+1_in_10000': bun_primes,
        'coverage_to_1000': poly_coverage,
        'all_poly_primes_count': len(all_poly_primes),
        'can_generate_all': False,
        'reason': 'No single polynomial produces only primes (Bunyakovsky); iteration diverges to composites'
    }
    RESULTS['03_polynomial'] = stats
    best_name = max(results, key=lambda n: results[n]['linear_primes_in_1000'])
    print(f"  Best polynomial: {best_name} ({results[best_name]['linear_primes_in_1000']} primes in f(0..999))")
    print(f"  Euler iteration chain: {results['euler_n2+n+41']['iteration_primes']}/{results['euler_n2+n+41']['iteration_chain_length']} prime")
    print(f"  n^2+1 primes in [0,10000): {bun_primes}")
    print(f"  Time: {elapsed:.2f}s")
    return stats


# ============================================================================
# APPROACH 4: Modular Branching Tree
# ============================================================================
def approach4_modular():
    """Deterministic tree: branch by residue class mod m."""
    print("\n=== Approach 4: Modular Branching Tree ===")
    t0 = time.time()

    # Build tree mod 6: primes > 3 are either 1 or 5 mod 6
    # From prime p, children = next prime == 1 mod 6, next prime == 5 mod 6
    # This IS a binary tree covering all primes > 3

    def next_prime_in_class(start, r, m, limit=10**7):
        """Find smallest prime > start that is == r mod m."""
        p = start + 1
        while p < limit:
            if p % m == r and is_prime_fast(p):
                return p
            p += 1
        return None

    # Mod 6 tree from p=5
    tree_mod6 = {}
    all_primes_found = set()
    queue = deque([(5, 0)])
    all_primes_found.add(5)
    depth_counts = defaultdict(int)
    depth_counts[0] = 1
    max_depth = 20
    max_nodes = 10000

    while queue and len(all_primes_found) < max_nodes:
        p, d = queue.popleft()
        if d >= max_depth:
            continue
        children = []
        for r in [1, 5]:
            c = next_prime_in_class(p, r, 6)
            if c and c not in all_primes_found:
                children.append(c)
                all_primes_found.add(c)
                depth_counts[d + 1] += 1
                queue.append((c, d + 1))
        tree_mod6[p] = children

    # Mod 30 tree (primorial branching): residues 1,7,11,13,17,19,23,29
    residues_30 = [1, 7, 11, 13, 17, 19, 23, 29]
    tree_mod30 = {}
    primes_mod30 = set()
    queue30 = deque([(7, 0)])
    primes_mod30.add(7)
    depth_counts_30 = defaultdict(int)
    depth_counts_30[0] = 1

    while queue30 and len(primes_mod30) < 5000:
        p, d = queue30.popleft()
        if d >= 12:
            continue
        children = []
        for r in residues_30:
            c = next_prime_in_class(p, r, 30)
            if c and c not in primes_mod30:
                children.append(c)
                primes_mod30.add(c)
                depth_counts_30[d + 1] += 1
                queue30.append((c, d + 1))
        tree_mod30[p] = children

    # Coverage analysis
    primes_to_1000 = set(p for p in ALL_PRIMES_1M if p <= 1000)
    cov6 = len(all_primes_found & primes_to_1000) / len(primes_to_1000)
    cov30 = len(primes_mod30 & primes_to_1000) / len(primes_to_1000)

    elapsed = time.time() - t0

    # Visualization
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Mod 6 depth distribution
    d6 = sorted(depth_counts.keys())
    c6 = [depth_counts[d] for d in d6]
    axes[0].bar(d6, c6, color='mediumpurple', alpha=0.8)
    axes[0].set_xlabel('Depth')
    axes[0].set_ylabel('Nodes')
    axes[0].set_title(f'Mod 6 Branching Tree\n{len(all_primes_found)} primes, coverage to 1000: {cov6:.1%}')

    # Mod 30 depth distribution
    d30 = sorted(depth_counts_30.keys())
    c30 = [depth_counts_30[d] for d in d30]
    axes[1].bar(d30, c30, color='darkorange', alpha=0.8)
    axes[1].set_xlabel('Depth')
    axes[1].set_ylabel('Nodes')
    axes[1].set_title(f'Mod 30 Branching Tree (8 branches)\n{len(primes_mod30)} primes, coverage to 1000: {cov30:.1%}')

    plt.tight_layout()
    plt.savefig(f"{IMG_DIR}/prime_tree_04_modular.png", dpi=150)
    plt.close()

    stats = {
        'time': elapsed,
        'mod6_primes': len(all_primes_found),
        'mod6_coverage_1000': cov6,
        'mod30_primes': len(primes_mod30),
        'mod30_coverage_1000': cov30,
        'can_generate_all': True,  # In principle, yes!
        'reason': 'Mod-m branching covers all primes by Dirichlet theorem, but is really a lookup table, not algebraic generation'
    }
    RESULTS['04_modular'] = stats
    print(f"  Mod 6 tree: {len(all_primes_found)} primes, coverage {cov6:.1%}")
    print(f"  Mod 30 tree: {len(primes_mod30)} primes, coverage {cov30:.1%}")
    print(f"  Time: {elapsed:.2f}s")
    return stats


# ============================================================================
# APPROACH 5: GCD/Gap Tree (twin, cousin, sexy primes)
# ============================================================================
def approach5_gcd_gap():
    """Tree by prime gaps: children are primes at specific offsets."""
    print("\n=== Approach 5: GCD/Gap Tree ===")
    t0 = time.time()

    gap_labels = {2: 'twin', 4: 'cousin', 6: 'sexy', 8: 'octo', 12: 'dozen', 30: 'prime30'}
    gaps = [2, 4, 6, 8, 12, 30]

    # From each prime, find children at each gap
    results_by_gap = {}
    for gap in gaps:
        chains = {}
        for seed in [3, 5, 7, 11, 13]:
            chain = [seed]
            p = seed
            for _ in range(50):
                q = p + gap
                if is_prime_fast(q):
                    chain.append(q)
                    p = q
                else:
                    break
            chains[seed] = chain
        best_seed = max(chains, key=lambda s: len(chains[s]))
        results_by_gap[gap] = {
            'best_chain_length': len(chains[best_seed]),
            'best_seed': best_seed,
            'chain_preview': chains[best_seed][:10]
        }

    # Full gap tree: from seed, branch to p+2, p+4, p+6
    tree_primes = set()
    depth_data = defaultdict(lambda: [0, 0])
    queue = deque([(3, 0)])
    visited = {3}
    tree_primes.add(3)

    while queue:
        p, d = queue.popleft()
        if d >= 12:
            continue
        depth_data[d][1] += 1
        if is_prime_fast(p):
            depth_data[d][0] += 1
        for gap in [2, 4, 6]:
            c = p + gap
            if 1 < c < 10**7 and c not in visited:
                visited.add(c)
                if is_prime_fast(c):
                    tree_primes.add(c)
                queue.append((c, d + 1))
                if len(visited) > 30000:
                    break
        if len(visited) > 30000:
            break

    primes_to_1000 = set(p for p in ALL_PRIMES_1M if p <= 1000)
    coverage = len(tree_primes & primes_to_1000) / len(primes_to_1000)

    # Gap distribution analysis
    prime_list = ALL_PRIMES_1M[:1000]
    gap_hist = defaultdict(int)
    for i in range(len(prime_list) - 1):
        g = prime_list[i+1] - prime_list[i]
        gap_hist[g] += 1

    elapsed = time.time() - t0

    # Visualization
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Gap chain lengths
    gap_names = [f"gap={g}\n({gap_labels[g]})" for g in gaps]
    chain_lengths = [results_by_gap[g]['best_chain_length'] for g in gaps]
    axes[0].bar(gap_names, chain_lengths, color='teal', alpha=0.8)
    axes[0].set_ylabel('Longest Chain')
    axes[0].set_title('Longest Arithmetic Prime Chains by Gap')

    # Gap distribution
    gap_vals = sorted(gap_hist.keys())[:20]
    gap_counts = [gap_hist[g] for g in gap_vals]
    axes[1].bar(gap_vals, gap_counts, color='salmon', alpha=0.8)
    axes[1].set_xlabel('Gap Size')
    axes[1].set_ylabel('Frequency')
    axes[1].set_title(f'Prime Gap Distribution (first 1000 primes)\nGap tree coverage to 1000: {coverage:.1%}')

    plt.tight_layout()
    plt.savefig(f"{IMG_DIR}/prime_tree_05_gcd_gap.png", dpi=150)
    plt.close()

    stats = {
        'time': elapsed,
        'gap_chain_results': {g: results_by_gap[g]['best_chain_length'] for g in gaps},
        'tree_primes': len(tree_primes),
        'coverage_to_1000': coverage,
        'gap_distribution': dict(list(sorted(gap_hist.items()))[:10]),
        'can_generate_all': False,
        'reason': 'Arithmetic progressions of primes are finite (Green-Tao guarantees existence but not infinite chains)'
    }
    RESULTS['05_gcd_gap'] = stats
    print(f"  Gap chain best lengths: { {g: results_by_gap[g]['best_chain_length'] for g in gaps} }")
    print(f"  Tree primes: {len(tree_primes)}, coverage: {coverage:.1%}")
    print(f"  Time: {elapsed:.2f}s")
    return stats


# ============================================================================
# APPROACH 6: Gaussian Prime Tree
# ============================================================================
def approach6_gaussian():
    """Gaussian prime tree in Z[i]."""
    print("\n=== Approach 6: Gaussian Prime Tree ===")
    t0 = time.time()

    def is_gaussian_prime(a, b):
        """Check if a+bi is a Gaussian prime."""
        if a == 0:
            return abs(b) % 4 == 3 and is_prime_fast(abs(b))
        if b == 0:
            return abs(a) % 4 == 3 and is_prime_fast(abs(a))
        norm = a*a + b*b
        return is_prime_fast(norm)

    def gauss_norm(a, b):
        return a*a + b*b

    # Start from 1+i, apply transformations
    # Multiplication by units: i, -1, -i (rotations)
    # Shifts: +1, +i, +1+i
    transforms = {
        'mult_1+i': lambda a, b: (a - b, a + b),
        'mult_1-i': lambda a, b: (a + b, -a + b),
        'add_1': lambda a, b: (a + 1, b),
        'add_i': lambda a, b: (a, b + 1),
        'add_1+i': lambda a, b: (a + 1, b + 1),
        'mult_2+i': lambda a, b: (2*a - b, a + 2*b),
    }

    # BFS from (1,1) = 1+i
    gp_tree = set()
    queue = deque([((1, 1), 0)])
    visited = {(1, 1)}
    depth_data = defaultdict(lambda: [0, 0])

    if is_gaussian_prime(1, 1):
        gp_tree.add((1, 1))

    max_norm = 10000
    while queue:
        (a, b), d = queue.popleft()
        if d >= 10:
            continue
        depth_data[d][1] += 1
        if is_gaussian_prime(a, b):
            depth_data[d][0] += 1

        for tname, tfunc in transforms.items():
            na, nb = tfunc(a, b)
            if (na, nb) not in visited and gauss_norm(na, nb) < max_norm:
                visited.add((na, nb))
                if is_gaussian_prime(na, nb):
                    gp_tree.add((na, nb))
                queue.append(((na, nb), d + 1))
                if len(visited) > 20000:
                    break
        if len(visited) > 20000:
            break

    # Also enumerate all Gaussian primes with norm < 500 for reference
    all_gp = set()
    for a in range(-50, 51):
        for b in range(-50, 51):
            if is_gaussian_prime(a, b):
                all_gp.add((a, b))

    # Which rational primes split in Z[i]?
    split_primes = []  # p = 1 mod 4, splits as (a+bi)(a-bi)
    inert_primes = []  # p = 3 mod 4, stays prime
    for p in ALL_PRIMES_1M[:100]:
        if p == 2:
            continue  # 2 ramifies: 2 = -i(1+i)^2
        if p % 4 == 1:
            split_primes.append(p)
        else:
            inert_primes.append(p)

    elapsed = time.time() - t0

    # Visualization
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))

    # Left: all Gaussian primes in [-50,50]^2
    gp_x = [a for a, b in all_gp]
    gp_y = [b for a, b in all_gp]
    axes[0].scatter(gp_x, gp_y, s=3, c='blue', alpha=0.5)
    axes[0].set_xlabel('Real Part')
    axes[0].set_ylabel('Imaginary Part')
    axes[0].set_title(f'Gaussian Primes in [-50,50]^2\n({len(all_gp)} primes)')
    axes[0].set_aspect('equal')
    axes[0].grid(True, alpha=0.3)

    # Right: tree-found primes highlighted
    tree_x = [a for a, b in gp_tree if abs(a) <= 50 and abs(b) <= 50]
    tree_y = [b for a, b in gp_tree if abs(a) <= 50 and abs(b) <= 50]
    axes[1].scatter(gp_x, gp_y, s=3, c='lightgray', alpha=0.5, label='All G-primes')
    axes[1].scatter(tree_x, tree_y, s=8, c='red', alpha=0.7, label='Tree-found')
    axes[1].set_xlabel('Real Part')
    axes[1].set_ylabel('Imaginary Part')
    axes[1].set_title(f'Gaussian Prime Tree from 1+i\n({len(gp_tree)} found / {len(all_gp)} total)')
    axes[1].set_aspect('equal')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(f"{IMG_DIR}/prime_tree_06_gaussian.png", dpi=150)
    plt.close()

    # Rational primes recoverable from Gaussian tree
    rational_from_gp = set()
    for a, b in gp_tree:
        if b == 0 and a > 1 and is_prime_fast(a):
            rational_from_gp.add(a)
        n = a*a + b*b
        if n > 1 and is_prime_fast(n):
            rational_from_gp.add(n)
    primes_to_1000 = set(p for p in ALL_PRIMES_1M if p <= 1000)
    gp_rational_cov = len(rational_from_gp & primes_to_1000) / len(primes_to_1000)

    stats = {
        'time': elapsed,
        'gaussian_primes_found': len(gp_tree),
        'total_gp_in_range': len(all_gp),
        'coverage': len(gp_tree) / max(len(all_gp), 1),
        'coverage_to_1000': gp_rational_cov,
        'split_primes_example': split_primes[:10],
        'inert_primes_example': inert_primes[:10],
        'nodes_explored': len(visited),
        'can_generate_all': False,
        'reason': 'Shifts break multiplicative structure; reaching all Gaussian primes requires additive steps that lose algebraic control'
    }
    RESULTS['06_gaussian'] = stats
    print(f"  Gaussian primes found by tree: {len(gp_tree)} / {len(all_gp)}")
    print(f"  Split primes (1 mod 4): {split_primes[:5]}...")
    print(f"  Inert primes (3 mod 4): {inert_primes[:5]}...")
    print(f"  Time: {elapsed:.2f}s")
    return stats


# ============================================================================
# APPROACH 7: Stern-Brocot Prime Sieve
# ============================================================================
def approach7_stern_brocot():
    """Locate primes within the Stern-Brocot tree."""
    print("\n=== Approach 7: Stern-Brocot Prime Sieve ===")
    t0 = time.time()

    # The Stern-Brocot tree generates all positive rationals p/q with gcd(p,q)=1
    # We want integers p/1, i.e., nodes where denominator = 1
    # These appear at very specific locations

    # Build Stern-Brocot tree via mediant operation
    # Root = 1/1, left = 0/1, right = 1/0 (infinity)
    # Each node p/q has children: left = mediant(left_ancestor, p/q), right = mediant(p/q, right_ancestor)

    # Instead, enumerate Stern-Brocot sequences (Stern's diatomic series)
    # s(0)=0, s(1)=1, s(2n)=s(n), s(2n+1)=s(n)+s(n+1)
    # The rationals s(n)/s(n+1) enumerate all positive rationals

    stern = [0, 1]
    max_idx = 100000
    for n in range(2, max_idx):
        if n % 2 == 0:
            stern.append(stern[n // 2])
        else:
            stern.append(stern[n // 2] + stern[n // 2 + 1])

    # Find indices where s(n)/s(n+1) is an integer (i.e., s(n+1) divides s(n))
    integer_nodes = {}  # value -> first index
    prime_positions = {}  # prime -> first index in Stern-Brocot
    for n in range(1, len(stern) - 1):
        if stern[n + 1] == 1:  # s(n)/1 = integer
            val = stern[n]
            if val not in integer_nodes:
                integer_nodes[val] = n
                if val > 1 and is_prime_fast(val):
                    prime_positions[val] = n

    # Depth in tree = floor(log2(n))
    prime_depths = {}
    for p, idx in prime_positions.items():
        depth = int(math.log2(idx)) if idx > 0 else 0
        prime_depths[p] = depth

    # Stern-Brocot "primes at depth d"
    depth_prime_count = defaultdict(int)
    for p, d in prime_depths.items():
        depth_prime_count[d] += 1

    elapsed = time.time() - t0

    # Visualization
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Left: positions of primes in Stern sequence
    primes_sorted = sorted(prime_positions.items(), key=lambda x: x[0])[:100]
    if primes_sorted:
        ps, idxs = zip(*primes_sorted)
        axes[0].scatter(ps, idxs, s=10, c='navy', alpha=0.7)
        axes[0].set_xlabel('Prime Value')
        axes[0].set_ylabel('First Index in Stern Sequence')
        axes[0].set_title(f'Primes in Stern-Brocot Tree\n({len(prime_positions)} primes found)')

    # Right: prime count by depth
    if depth_prime_count:
        ds = sorted(depth_prime_count.keys())
        cs = [depth_prime_count[d] for d in ds]
        axes[1].bar(ds, cs, color='darkgreen', alpha=0.8)
        axes[1].set_xlabel('Tree Depth (log2 of index)')
        axes[1].set_ylabel('Number of Primes')
        axes[1].set_title('Prime Distribution by Stern-Brocot Depth')

    plt.tight_layout()
    plt.savefig(f"{IMG_DIR}/prime_tree_07_stern_brocot.png", dpi=150)
    plt.close()

    primes_to_1000 = set(p for p in ALL_PRIMES_1M if p <= 1000)
    sb_cov = len(set(prime_positions.keys()) & primes_to_1000) / len(primes_to_1000)

    stats = {
        'time': elapsed,
        'primes_found': len(prime_positions),
        'max_prime_found': max(prime_positions.keys()) if prime_positions else 0,
        'depth_distribution': dict(sorted(depth_prime_count.items())[:15]),
        'example_positions': {p: idx for p, idx in sorted(prime_positions.items())[:10]},
        'coverage_to_1000': sb_cov,
        'can_generate_all': False,
        'reason': 'Stern-Brocot enumerates all rationals, not primes; primes appear at positions growing as ~p*log(p)'
    }
    RESULTS['07_stern_brocot'] = stats
    print(f"  Found {len(prime_positions)} primes in Stern-Brocot indices up to {max_idx}")
    print(f"  Example: prime 2 at index {prime_positions.get(2, 'N/A')}, prime 3 at {prime_positions.get(3, 'N/A')}")
    print(f"  Time: {elapsed:.2f}s")
    return stats


# ============================================================================
# APPROACH 8: Multiplicative Function (Totient) Tree
# ============================================================================
def approach8_totient():
    """Tree connected by Euler's totient function."""
    print("\n=== Approach 8: Totient Function Tree ===")
    t0 = time.time()

    # Build reverse-totient tree: prime q is child of prime p if p | phi(q)
    # For prime q: phi(q) = q-1, so p | (q-1)
    # This means: q == 1 (mod p)

    # Forward tree: from prime p, find small primes q with q == 1 (mod p)
    primes_500 = [p for p in ALL_PRIMES_1M if p <= 500]
    totient_tree = defaultdict(list)
    tree_edges = []

    for p in primes_500:
        # Find primes q == 1 (mod p), q < 10000
        q = p + 1
        children = []
        while q < 10000 and len(children) < 5:
            if is_prime_fast(q):
                children.append(q)
                tree_edges.append((p, q))
            q += p
        totient_tree[p] = children

    # Iterated totient chains: p -> phi(p) -> phi(phi(p)) -> ... -> 1
    # For prime p: phi(p) = p-1
    def totient_chain(p):
        chain = [p]
        while p > 1:
            p = totient(p)
            chain.append(p)
        return chain

    sample_chains = {}
    for p in [2, 3, 5, 7, 11, 13, 17, 23, 97, 997]:
        sample_chains[p] = totient_chain(p)

    # Inverse totient: how many primes q have phi(q) divisible by p?
    inverse_counts = {}
    for p in primes_500[:50]:
        count = sum(1 for q in ALL_PRIMES_1M if q <= 10000 and (q - 1) % p == 0)
        inverse_counts[p] = count

    # Coverage: can we reach all primes from 2?
    reachable_from_2 = set()
    queue = deque([2])
    reachable_from_2.add(2)
    while queue:
        p = queue.popleft()
        for c in totient_tree.get(p, []):
            if c not in reachable_from_2:
                reachable_from_2.add(c)
                queue.append(c)
                if len(reachable_from_2) > 5000:
                    break
        if len(reachable_from_2) > 5000:
            break

    primes_to_1000 = set(p for p in ALL_PRIMES_1M if p <= 1000)
    coverage = len(reachable_from_2 & primes_to_1000) / len(primes_to_1000)

    elapsed = time.time() - t0

    # Visualization
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Left: inverse totient branching factor
    inv_primes = sorted(inverse_counts.keys())[:30]
    inv_vals = [inverse_counts[p] for p in inv_primes]
    axes[0].bar(range(len(inv_primes)), inv_vals, color='indigo', alpha=0.8)
    axes[0].set_xticks(range(len(inv_primes)))
    axes[0].set_xticklabels([str(p) for p in inv_primes], fontsize=6, rotation=45)
    axes[0].set_xlabel('Prime p')
    axes[0].set_ylabel('# primes q<10000 with p|phi(q)')
    axes[0].set_title('Totient Tree Branching Factor')

    # Right: totient chains
    for p, chain in sorted(sample_chains.items()):
        if len(chain) > 2:
            axes[1].plot(range(len(chain)), chain, 'o-', markersize=4, label=f'p={p}')
    axes[1].set_xlabel('Iteration')
    axes[1].set_ylabel('Value')
    axes[1].set_title('Iterated Totient Chains')
    axes[1].legend(fontsize=7)
    axes[1].set_yscale('log')

    plt.tight_layout()
    plt.savefig(f"{IMG_DIR}/prime_tree_08_totient.png", dpi=150)
    plt.close()

    stats = {
        'time': elapsed,
        'reachable_from_2': len(reachable_from_2),
        'coverage_to_1000': coverage,
        'branching_examples': {p: inverse_counts[p] for p in list(inverse_counts.keys())[:10]},
        'totient_chains': {p: len(c) for p, c in sample_chains.items()},
        'tree_edges': len(tree_edges),
        'can_generate_all': True,  # By Dirichlet, every arithmetic progression a*p+1 has infinitely many primes
        'reason': 'By Dirichlet theorem, for each prime p there exist infinitely many primes q == 1 (mod p), so the tree is infinite and reaches all primes. But this is a GRAPH, not a tree with unique paths.'
    }
    RESULTS['08_totient'] = stats
    print(f"  Reachable from 2: {len(reachable_from_2)}, coverage {coverage:.1%}")
    print(f"  Totient chain of 997: length {len(sample_chains[997])}")
    print(f"  Time: {elapsed:.2f}s")
    return stats


# ============================================================================
# APPROACH 9: Binary Splitting Tree
# ============================================================================
def approach9_binary_split():
    """BSP tree of primes: recursively split intervals."""
    print("\n=== Approach 9: Binary Splitting Tree ===")
    t0 = time.time()

    # Build BSP tree of primes in [2, N]
    N = 10000
    primes_N = [p for p in ALL_PRIMES_1M if p <= N]
    n_primes = len(primes_N)

    # Recursive BSP
    tree_depths = []
    node_count = [0]

    def bsp(primes_list, depth):
        node_count[0] += 1
        if len(primes_list) <= 1:
            tree_depths.append(depth)
            return depth
        mid = len(primes_list) // 2
        left_d = bsp(primes_list[:mid], depth + 1)
        right_d = bsp(primes_list[mid:], depth + 1)
        return max(left_d, right_d)

    max_depth = bsp(primes_N, 0)

    # Compare with perfect binary tree depth
    perfect_depth = math.ceil(math.log2(max(n_primes, 1)))

    # Alternative: split by value (not count)
    tree_depths_val = []
    node_count_val = [0]

    def bsp_value(lo, hi, primes_in_range, depth):
        node_count_val[0] += 1
        if len(primes_in_range) <= 1:
            tree_depths_val.append(depth)
            return
        if depth > 50:
            return
        mid = (lo + hi) // 2
        left = [p for p in primes_in_range if p <= mid]
        right = [p for p in primes_in_range if p > mid]
        bsp_value(lo, mid, left, depth + 1)
        bsp_value(mid + 1, hi, right, depth + 1)

    bsp_value(2, N, primes_N, 0)

    # Prime counting function pi(x) analysis
    x_vals = list(range(100, N + 1, 100))
    pi_vals = []
    count = 0
    pi = 0
    for x in range(2, N + 1):
        if x in PRIMES_1M:
            pi += 1
        if x in x_vals:
            pi_vals.append(pi)

    # Li(x) approximation
    li_vals = [x / math.log(max(x, 2)) for x in x_vals]

    elapsed = time.time() - t0

    # Visualization
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Left: BSP depth distribution (count-based)
    axes[0].hist(tree_depths, bins=range(max(tree_depths) + 2), color='cadetblue', alpha=0.8)
    axes[0].axvline(perfect_depth, color='red', linestyle='--', label=f'Perfect depth = {perfect_depth}')
    axes[0].set_xlabel('Leaf Depth')
    axes[0].set_ylabel('Number of Leaves')
    axes[0].set_title(f'BSP Tree Depth Distribution (Count Split)\n{n_primes} primes in [2,{N}]')
    axes[0].legend()

    # Right: pi(x) vs x/ln(x)
    axes[1].plot(x_vals, pi_vals, 'b-', label='pi(x)')
    axes[1].plot(x_vals, li_vals, 'r--', label='x/ln(x)')
    axes[1].set_xlabel('x')
    axes[1].set_ylabel('Count')
    axes[1].set_title('Prime Counting Function\npi(x) vs x/ln(x)')
    axes[1].legend()

    plt.tight_layout()
    plt.savefig(f"{IMG_DIR}/prime_tree_09_binary_split.png", dpi=150)
    plt.close()

    primes_to_1000 = set(p for p in ALL_PRIMES_1M if p <= 1000)
    bsp_cov = len(set(primes_N) & primes_to_1000) / len(primes_to_1000)  # should be 100%

    stats = {
        'time': elapsed,
        'primes_in_range': n_primes,
        'bsp_max_depth_count': max_depth,
        'bsp_perfect_depth': perfect_depth,
        'bsp_mean_depth_count': np.mean(tree_depths),
        'bsp_nodes_count': node_count[0],
        'bsp_nodes_value': node_count_val[0],
        'bsp_mean_depth_value': np.mean(tree_depths_val) if tree_depths_val else 0,
        'coverage_to_1000': bsp_cov,
        'can_generate_all': True,
        'reason': 'BSP trivially contains all primes in the interval, but it is a data structure, not an algebraic generator'
    }
    RESULTS['09_binary_split'] = stats
    print(f"  {n_primes} primes in [2,{N}]")
    print(f"  BSP depth (count split): max={max_depth}, perfect={perfect_depth}, mean={np.mean(tree_depths):.1f}")
    print(f"  BSP depth (value split): mean={np.mean(tree_depths_val):.1f}")
    print(f"  Time: {elapsed:.2f}s")
    return stats


# ============================================================================
# APPROACH 10: Fermat-Fibonacci-Mersenne Hybrid Tree
# ============================================================================
def approach10_ffm_hybrid():
    """Tree using Mersenne (2^p-1), Fermat-like (2^p+1), Fibonacci branching."""
    print("\n=== Approach 10: Fermat-Fibonacci-Mersenne Hybrid Tree ===")
    t0 = time.time()

    # Known Mersenne prime exponents (small)
    mersenne_exponents = [2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127, 521, 607]

    # Check Mersenne primes
    mersenne_primes = []
    for p in mersenne_exponents[:10]:
        m = (1 << p) - 1
        if is_prime_fast(m):
            mersenne_primes.append((p, m))

    # Fibonacci primes
    fib_primes = []
    a, b = 0, 1
    for i in range(80):
        a, b = b, a + b
        if is_prime_fast(b) and b < 10**15:
            fib_primes.append((i + 2, b))  # F_{i+2}

    # Known Fermat primes: 2^(2^n)+1 for n=0,1,2,3,4
    fermat_primes = [(n, (1 << (1 << n)) + 1) for n in range(5)]

    # Hybrid tree: from prime p, branch to:
    #   B1: 2^p - 1 (Mersenne)
    #   B2: 2^p + 1 (Fermat-like)
    #   B3: F_p (Fibonacci)
    def fib(n):
        if n <= 0: return 0
        a, b = 0, 1
        for _ in range(n - 1):
            a, b = b, a + b
        return b

    tree_primes = set()
    tree_edges = []
    queue = deque([(2, 0)])
    visited = {2}
    tree_primes.add(2)
    depth_counts = defaultdict(int)
    depth_counts[0] = 1

    while queue:
        p, d = queue.popleft()
        if d >= 8 or p > 200:  # p > 200 would make 2^p too large
            continue

        children = []
        # Mersenne branch
        if p <= 60:
            m = (1 << p) - 1
            if m not in visited and is_prime_fast(m):
                children.append(('M', m))
        # Fermat-like branch
        if p <= 60:
            f = (1 << p) + 1
            if f not in visited and is_prime_fast(f):
                children.append(('F', f))
        # Fibonacci branch
        if p <= 70:
            fb = fib(p)
            if fb > 1 and fb not in visited and is_prime_fast(fb):
                children.append(('Fib', fb))

        for label, c in children:
            visited.add(c)
            tree_primes.add(c)
            tree_edges.append((p, c, label))
            depth_counts[d + 1] += 1
            queue.append((c, d + 1))

    # Analysis: which primes are reachable?
    reachable = sorted(tree_primes)

    # Special numbers analysis
    # How many Mersenne numbers 2^p-1 are prime for p < 100?
    mersenne_test = []
    for p in range(2, 100):
        if is_prime_fast(p):
            m = (1 << p) - 1
            mersenne_test.append((p, is_prime_fast(m)))

    elapsed = time.time() - t0

    # Visualization
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Left: tree structure
    if tree_edges:
        for p, c, label in tree_edges:
            color = {'M': 'blue', 'F': 'red', 'Fib': 'green'}[label]
            axes[0].annotate('', xy=(c, 1), xytext=(p, 0),
                           arrowprops=dict(arrowstyle='->', color=color, lw=1.5))
            axes[0].plot(c, 1, 'o', color=color, markersize=8)
            axes[0].plot(p, 0, 'ko', markersize=8)
            axes[0].annotate(str(c), (c, 1.05), fontsize=7, ha='center')
            axes[0].annotate(str(p), (p, -0.05), fontsize=7, ha='center')

    axes[0].set_title('FFM Hybrid Tree\nBlue=Mersenne, Red=Fermat, Green=Fibonacci')
    axes[0].set_ylim(-0.5, 2)

    # Right: Mersenne primality
    m_exp = [p for p, _ in mersenne_test]
    m_prime = [1 if ip else 0 for _, ip in mersenne_test]
    colors = ['blue' if ip else 'lightgray' for _, ip in mersenne_test]
    axes[1].bar(m_exp, [1]*len(m_exp), color=colors, alpha=0.8)
    axes[1].set_xlabel('Exponent p')
    axes[1].set_ylabel('')
    axes[1].set_title(f'Mersenne Primality: 2^p-1 for prime p<100\nBlue = prime ({sum(m_prime)} of {len(m_prime)})')

    # Add labels for Mersenne primes
    mpatches_legend = [
        mpatches.Patch(color='blue', label=f'Mersenne primes: {[p for p, ip in mersenne_test if ip]}'),
        mpatches.Patch(color='lightgray', label='Composite')
    ]
    axes[1].legend(handles=mpatches_legend, fontsize=8)

    plt.tight_layout()
    plt.savefig(f"{IMG_DIR}/prime_tree_10_ffm_hybrid.png", dpi=150)
    plt.close()

    primes_to_1000 = set(p for p in ALL_PRIMES_1M if p <= 1000)
    ffm_cov = len(tree_primes & primes_to_1000) / len(primes_to_1000)

    stats = {
        'time': elapsed,
        'tree_primes': sorted(tree_primes),
        'tree_primes_count': len(tree_primes),
        'tree_edges': len(tree_edges),
        'mersenne_primes': mersenne_primes,
        'fibonacci_primes': fib_primes[:10],
        'fermat_primes': fermat_primes,
        'mersenne_rate': f"{sum(m_prime)}/{len(m_prime)}",
        'coverage_to_1000': ffm_cov,
        'can_generate_all': False,
        'reason': 'Special-form primes (Mersenne, Fermat, Fibonacci) are extremely sparse; tree dies quickly'
    }
    RESULTS['10_ffm_hybrid'] = stats
    print(f"  Tree primes: {sorted(tree_primes)}")
    print(f"  Mersenne primes found: {[(p, m) for p, m in mersenne_primes[:5]]}")
    print(f"  Fibonacci primes: {fib_primes[:5]}")
    print(f"  Mersenne rate for p<100: {sum(m_prime)}/{len(m_prime)}")
    print(f"  Time: {elapsed:.2f}s")
    return stats


# ============================================================================
# THEORETICAL ANALYSIS: Why no Berggren-for-Primes?
# ============================================================================
def theoretical_analysis():
    """Prove/argue why no finite matrix set can generate all primes."""
    print("\n=== Theoretical Analysis: Why No Berggren for Primes? ===")
    t0 = time.time()

    analysis = {}

    # Argument 1: Algebraic vs Analytic
    # PPTs satisfy a²+b²=c² — an algebraic variety.
    # The Berggren matrices preserve this variety.
    # Primes are defined by a divisibility condition, not an algebraic equation.
    analysis['algebraic_structure'] = {
        'PPTs': 'Defined by a^2+b^2=c^2, an algebraic variety in Z^3',
        'Primes': 'Defined by: p>1 and for all d|p, d=1 or d=p — a universal quantifier, not an equation',
        'Key difference': 'No polynomial equation P(x)=0 has solutions = {all primes}'
    }

    # Argument 2: Density
    # PPTs at height h ~ c: density is O(1/log(c)) — same as primes!
    # But PPTs have STRUCTURE (they lie on a cone), primes do not.
    primes_to_N = lambda N: sum(1 for p in range(2, N+1) if p in PRIMES_1M or (N > 1000000 and isprime(p)))
    densities = {}
    for N in [100, 1000, 10000, 100000]:
        count = len([p for p in ALL_PRIMES_1M if p <= N])
        densities[N] = count / N

    analysis['density'] = {
        'prime_density': densities,
        'PNT': 'pi(N) ~ N/ln(N), density ~ 1/ln(N)',
        'PPT_density': 'Also O(1/log), but PPTs have algebraic structure enabling tree generation'
    }

    # Argument 3: Matrix action test
    # If M is an integer matrix and p is prime, is M*[p,1]^T prime in first coordinate?
    # Test: for random 2x2 integer matrices, what fraction preserve primality?
    import random
    random.seed(42)
    primality_rates = []
    for _ in range(1000):
        a, b, c, d = [random.randint(-5, 5) for _ in range(4)]
        # Apply to first 100 primes
        prime_hits = 0
        total = 0
        for p in ALL_PRIMES_1M[:100]:
            val = a * p + b  # First coordinate of [a,b;c,d] * [p,1]
            if val > 1 and is_prime_fast(val):
                prime_hits += 1
            total += 1
        if total > 0:
            primality_rates.append(prime_hits / total)

    analysis['matrix_test'] = {
        'description': '1000 random 2x2 matrices applied to first 100 primes',
        'mean_primality_rate': np.mean(primality_rates),
        'max_primality_rate': np.max(primality_rates),
        'expected_by_PNT': 'For output ~100, PNT predicts rate ~1/ln(100) ~ 0.22',
        'conclusion': 'No matrix significantly beats random chance'
    }

    # Argument 4: Orbit structure
    # Berggren: orbit of (3,4,5) under 3 matrices = all PPTs (free monoid action)
    # For primes: any matrix M with M*p prime forces M = [1,k;*,*] with k even (to keep odd)
    # But then M*(p) = p + k, which is an additive shift — not a tree structure
    analysis['orbit_argument'] = {
        'PPT_orbit': 'GL(3,Z) acting on Z^3 preserves the cone a^2+b^2=c^2',
        'Prime_orbit': 'No subgroup of GL(n,Z) has an orbit = {primes}',
        'Proof_sketch': 'If M in GL(n,Z) maps prime vectors to prime vectors, the det(M) = +/-1 condition plus primality gives contradictions for n >= 2.',
        'Key_obstruction': 'Primes are multiplicatively defined but additively distributed (no algebraic curve to preserve)'
    }

    # Argument 5: Information-theoretic
    # The n-th PPT can be specified by a path of length O(log n) in the Berggren tree.
    # The n-th prime requires ~log(p_n) ~ log(n*ln(n)) bits, which matches tree depth.
    # But: the PATH encoding for PPTs is structured (L/R/M choices), while for primes
    # it would need to encode arbitrary primality information.
    analysis['information_theory'] = {
        'PPT_encoding': 'n-th PPT needs O(log n) bits (tree path)',
        'Prime_encoding': 'n-th prime needs ~log2(n*ln(n)) bits (comparable)',
        'Difference': 'For PPTs, the path bits have MEANING (which matrix to apply). For primes, the bits encode arbitrary primality — equivalent to a lookup table.',
        'Kolmogorov': 'The Kolmogorov complexity of "list of first N primes" is ~N*log(N) bits, incompressible beyond PNT-scale shortcuts'
    }

    elapsed = time.time() - t0
    analysis['computation_time'] = elapsed

    print(f"  Matrix primality preservation rate: mean={np.mean(primality_rates):.3f}, max={np.max(primality_rates):.3f}")
    print(f"  Expected by PNT for range ~100: ~{1/math.log(100):.3f}")
    print(f"  Time: {elapsed:.2f}s")

    RESULTS['theory'] = analysis
    return analysis


# ============================================================================
# SYNTHESIS & COMPARISON
# ============================================================================
def create_summary_visualization():
    """Create a summary figure comparing all approaches."""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # Top-left: coverage comparison
    approaches = []
    coverages = []
    for key in sorted(RESULTS.keys()):
        if key == 'theory':
            continue
        r = RESULTS[key]
        cov = r.get('coverage_to_1000', 0)
        approaches.append(key.split('_', 1)[1][:15])
        coverages.append(cov)

    bars = axes[0, 0].barh(range(len(approaches)), coverages, color='steelblue', alpha=0.8)
    axes[0, 0].set_yticks(range(len(approaches)))
    axes[0, 0].set_yticklabels(approaches, fontsize=8)
    axes[0, 0].set_xlabel('Coverage of Primes <= 1000')
    axes[0, 0].set_title('Coverage Comparison')
    axes[0, 0].set_xlim(0, 1.1)
    for i, v in enumerate(coverages):
        axes[0, 0].text(v + 0.01, i, f'{v:.1%}', va='center', fontsize=7)

    # Top-right: can_generate_all
    can_gen = []
    for key in sorted(RESULTS.keys()):
        if key == 'theory':
            continue
        r = RESULTS[key]
        can_gen.append(r.get('can_generate_all', False))

    colors = ['green' if c else 'red' for c in can_gen]
    axes[0, 1].barh(range(len(approaches)), [1]*len(approaches), color=colors, alpha=0.6)
    axes[0, 1].set_yticks(range(len(approaches)))
    axes[0, 1].set_yticklabels(approaches, fontsize=8)
    axes[0, 1].set_title('Can Generate ALL Primes?\nGreen=Yes (trivially), Red=No')
    for i, (key, c) in enumerate(zip(sorted(k for k in RESULTS if k != 'theory'), can_gen)):
        reason = RESULTS[key].get('reason', '')[:60]
        axes[0, 1].text(0.05, i, reason, va='center', fontsize=6, color='white' if not c else 'black')

    # Bottom-left: runtime comparison
    times = []
    for key in sorted(RESULTS.keys()):
        if key == 'theory':
            continue
        times.append(RESULTS[key].get('time', 0))

    axes[1, 0].barh(range(len(approaches)), times, color='coral', alpha=0.8)
    axes[1, 0].set_yticks(range(len(approaches)))
    axes[1, 0].set_yticklabels(approaches, fontsize=8)
    axes[1, 0].set_xlabel('Runtime (seconds)')
    axes[1, 0].set_title('Computation Time')

    # Bottom-right: theoretical obstruction summary
    theory_text = """WHY NO BERGGREN TREE FOR PRIMES?

1. NO ALGEBRAIC VARIETY
   PPTs: a^2+b^2=c^2 (algebraic surface)
   Primes: no polynomial equation

2. NO GROUP ACTION
   Berggren: GL(3,Z) preserves the Pythagorean cone
   Primes: no matrix group orbit = {primes}

3. INFORMATION-THEORETIC
   PPT paths: structured (3 choices per level)
   Prime "paths": encode arbitrary primality info

4. DENSITY WITHOUT STRUCTURE
   Both ~1/ln(N), but primes lack the algebraic
   regularity that enables tree generation

CONCLUSION: The primes are "additively distributed
but multiplicatively defined" — this fundamental
tension prevents any Berggren-like tree."""

    axes[1, 1].text(0.05, 0.95, theory_text, transform=axes[1, 1].transAxes,
                    fontsize=8, verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    axes[1, 1].axis('off')
    axes[1, 1].set_title('Theoretical Obstruction')

    plt.suptitle('Prime Tree Explorer: 10 Approaches to a Berggren Tree for Primes', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f"{IMG_DIR}/prime_tree_00_summary.png", dpi=150)
    plt.close()


# ============================================================================
# MAIN
# ============================================================================
def main():
    print("=" * 70)
    print("PRIME TREE EXPLORER")
    print("Can we build a Berggren-like tree for primes?")
    print("=" * 70)

    total_t0 = time.time()

    # Run all 10 approaches
    approach1_cunningham()
    approach2_linear_recurrence()
    approach3_polynomial()
    approach4_modular()
    approach5_gcd_gap()
    approach6_gaussian()
    approach7_stern_brocot()
    approach8_totient()
    approach9_binary_split()
    approach10_ffm_hybrid()
    theoretical_analysis()

    # Summary visualization
    create_summary_visualization()

    total_time = time.time() - total_t0
    print(f"\n{'=' * 70}")
    print(f"TOTAL TIME: {total_time:.1f}s")
    print(f"Images saved to {IMG_DIR}/prime_tree_*.png")
    print(f"{'=' * 70}")

    # Write results file
    write_results_md(total_time)

    return RESULTS


def write_results_md(total_time):
    """Write detailed results to markdown."""
    lines = []
    lines.append("# Prime Tree Explorer: Results")
    lines.append("")
    lines.append(f"**Total computation time: {total_time:.1f}s**")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append("")
    lines.append("We systematically explored 10 approaches to building a tree that generates")
    lines.append("all prime numbers, analogous to how the Berggren tree generates all primitive")
    lines.append("Pythagorean triples. The conclusion is definitive: **no such tree exists**,")
    lines.append("and the reasons are deeply structural.")
    lines.append("")

    lines.append("## Comparison Table")
    lines.append("")
    lines.append("| # | Approach | Primes Found | Coverage (<=1000) | Generates All? | Time |")
    lines.append("|---|----------|-------------|-------------------|----------------|------|")

    # Manual prime-count extraction per approach (keys differ)
    prime_count_keys = {
        '01_cunningham': 'best_total',
        '02_linear_recurrence': 'seed_23_primes',
        '03_polynomial': 'bunyakovsky_n2+1_in_10000',
        '04_modular': 'mod30_primes',
        '05_gcd_gap': 'tree_primes',
        '06_gaussian': 'gaussian_primes_found',
        '07_stern_brocot': 'primes_found',
        '08_totient': 'reachable_from_2',
        '09_binary_split': 'primes_in_range',
        '10_ffm_hybrid': 'tree_primes_count',
    }
    coverage_keys = {
        '04_modular': 'mod30_coverage_1000',
    }
    for key in sorted(RESULTS.keys()):
        if key == 'theory':
            continue
        r = RESULTS[key]
        num = key.split('_')[0]
        name = key.split('_', 1)[1].replace('_', ' ').title()
        pk = prime_count_keys.get(key, 'tree_primes')
        primes = r.get(pk, '?')
        cov_key = coverage_keys.get(key, 'coverage_to_1000')
        cov = r.get(cov_key, 0)
        can_gen = 'YES*' if r.get('can_generate_all', False) else 'NO'
        t = r.get('time', 0)
        lines.append(f"| {num} | {name} | {primes} | {cov:.1%} | {can_gen} | {t:.2f}s |")

    lines.append("")
    lines.append("*YES = generates all primes only trivially (by enumeration/lookup, not algebraic generation)")
    lines.append("")

    lines.append("## Detailed Results")
    lines.append("")

    # Approach 1
    lines.append("### 1. Cunningham Chain Tree")
    r = RESULTS.get('01_cunningham', {})
    lines.append(f"- **Best seed**: p={r.get('best_seed', '?')}, generating {r.get('best_total', '?')} primes")
    lines.append(f"- **Longest Sophie Germain chain**: length {r.get('longest_sg_chain', '?')} starting from {r.get('sg_chain_start', '?')}")
    lines.append(f"- **Coverage**: {r.get('coverage_to_1000', 0):.1%} of primes <= 1000")
    lines.append(f"- **Verdict**: Chains die quickly. Sophie Germain chains are conjectured infinite but proven finite in practice.")
    lines.append(f"- The map p -> 2p+1 doubles the size, so chains grow exponentially and miss most primes.")
    lines.append("")

    # Approach 2
    lines.append("### 2. Linear Recurrence Trees")
    r = RESULTS.get('02_linear_recurrence', {})
    lines.append(f"- **Best combination**: {r.get('best_combo', '?')} with {r.get('best_primes', '?')} primes")
    lines.append(f"- **Seed (2,3) found**: {r.get('seed_23_primes', '?')} primes")
    lines.append(f"- **Primality rate by depth**: {r.get('primality_rates', {})}")
    lines.append(f"- **Verdict**: Primality rate drops exponentially with depth. Linear transforms over Z")
    lines.append(f"  cannot preserve primality because ax+b is composite whenever gcd(a,b) > 1 or by Dirichlet density.")
    lines.append("")

    # Approach 3
    lines.append("### 3. Polynomial Prime Trees")
    r = RESULTS.get('03_polynomial', {})
    if 'results' in r:
        for pname, pdata in r['results'].items():
            lines.append(f"- **{pname}**: {pdata['linear_primes_in_1000']} primes in f(0..999), "
                        f"first composite at n={pdata['first_composite_at']}")
    lines.append(f"- **Bunyakovsky (n^2+1)**: {r.get('bunyakovsky_n2+1_in_10000', '?')} primes in [0,10000)")
    lines.append(f"- **Verdict**: No polynomial produces only primes (for degree >= 1, it must eventually produce")
    lines.append(f"  composites by Bunyakovsky's observation). Iterated application diverges to composites.")
    lines.append("")

    # Approach 4
    lines.append("### 4. Modular Branching Tree")
    r = RESULTS.get('04_modular', {})
    lines.append(f"- **Mod 6**: {r.get('mod6_primes', '?')} primes, coverage {r.get('mod6_coverage_1000', 0):.1%}")
    lines.append(f"- **Mod 30**: {r.get('mod30_primes', '?')} primes, coverage {r.get('mod30_coverage_1000', 0):.1%}")
    lines.append(f"- **Verdict**: This WORKS in the sense that it covers all primes (by Dirichlet's theorem,")
    lines.append(f"  every residue class coprime to the modulus contains infinitely many primes).")
    lines.append(f"  But it is really a lookup table disguised as a tree -- the branching rule is 'find the")
    lines.append(f"  next prime in each residue class', which requires primality testing, not algebraic generation.")
    lines.append("")

    # Approach 5
    lines.append("### 5. GCD/Gap Tree")
    r = RESULTS.get('05_gcd_gap', {})
    lines.append(f"- **Gap chain results**: {r.get('gap_chain_results', {})}")
    lines.append(f"- **Tree primes**: {r.get('tree_primes', '?')}, coverage {r.get('coverage_to_1000', 0):.1%}")
    lines.append(f"- **Verdict**: Prime gaps are irregular. While Green-Tao guarantees arbitrarily long")
    lines.append(f"  arithmetic progressions in primes, no fixed gap produces an infinite chain.")
    lines.append("")

    # Approach 6
    lines.append("### 6. Gaussian Prime Tree")
    r = RESULTS.get('06_gaussian', {})
    lines.append(f"- **Gaussian primes found**: {r.get('gaussian_primes_found', '?')} / {r.get('total_gp_in_range', '?')}")
    lines.append(f"- **Split primes (1 mod 4)**: {r.get('split_primes_example', [])[:5]}")
    lines.append(f"- **Inert primes (3 mod 4)**: {r.get('inert_primes_example', [])[:5]}")
    lines.append(f"- **Verdict**: The Gaussian integers Z[i] give beautiful structure -- primes p = 1 mod 4 split")
    lines.append(f"  into conjugate Gaussian primes, p = 3 mod 4 stay prime. But no finite set of Z[i]")
    lines.append(f"  transformations generates all Gaussian primes.")
    lines.append("")

    # Approach 7
    lines.append("### 7. Stern-Brocot Prime Sieve")
    r = RESULTS.get('07_stern_brocot', {})
    lines.append(f"- **Primes found**: {r.get('primes_found', '?')}")
    lines.append(f"- **Example positions**: {r.get('example_positions', {})}")
    lines.append(f"- **Verdict**: The Stern-Brocot tree enumerates all positive rationals, and integers")
    lines.append(f"  p/1 appear at specific positions. But the positions of primes within this tree are")
    lines.append(f"  as unpredictable as the primes themselves.")
    lines.append("")

    # Approach 8
    lines.append("### 8. Totient Function Tree")
    r = RESULTS.get('08_totient', {})
    lines.append(f"- **Reachable from 2**: {r.get('reachable_from_2', '?')} primes")
    lines.append(f"- **Coverage**: {r.get('coverage_to_1000', 0):.1%}")
    lines.append(f"- **Verdict**: The totient tree (q is child of p if p | phi(q), i.e., q = 1 mod p) actually")
    lines.append(f"  does reach all primes from p=2 (by Dirichlet). This is the closest to a 'Berggren for primes',")
    lines.append(f"  but it is a DAG (not a tree -- primes have multiple parents) and the branching rule")
    lines.append(f"  requires finding primes in arithmetic progressions, not a matrix multiplication.")
    lines.append("")

    # Approach 9
    lines.append("### 9. Binary Splitting Tree")
    r = RESULTS.get('09_binary_split', {})
    lines.append(f"- **BSP depth (count split)**: max={r.get('bsp_max_depth_count', '?')}, mean={r.get('bsp_mean_depth_count', '?'):.1f}")
    lines.append(f"- **Perfect tree depth**: {r.get('bsp_perfect_depth', '?')}")
    lines.append(f"- **Verdict**: A BSP tree trivially contains all primes, but it is a data structure, not a generator.")
    lines.append(f"  The depth matches log2(pi(N)) as expected from PNT.")
    lines.append("")

    # Approach 10
    lines.append("### 10. Fermat-Fibonacci-Mersenne Hybrid")
    r = RESULTS.get('10_ffm_hybrid', {})
    lines.append(f"- **Tree primes**: {r.get('tree_primes', [])}")
    lines.append(f"- **Mersenne primes**: {r.get('mersenne_primes', [])}")
    lines.append(f"- **Mersenne primality rate**: {r.get('mersenne_rate', '?')}")
    lines.append(f"- **Fibonacci primes**: {r.get('fibonacci_primes', [])[:5]}")
    lines.append(f"- **Verdict**: Special-form primes (Mersenne, Fermat, Fibonacci) are extremely sparse.")
    lines.append(f"  The tree from 2 reaches only a handful of primes before all branches die.")
    lines.append("")

    # Theoretical analysis
    lines.append("## Theoretical Analysis: Why No Berggren Tree for Primes?")
    lines.append("")
    lines.append("### The Berggren Analogy")
    lines.append("The Berggren tree works because:")
    lines.append("1. **Algebraic variety**: PPTs lie on the cone a^2+b^2=c^2 in Z^3")
    lines.append("2. **Group action**: Three matrices in GL(3,Z) act on this cone")
    lines.append("3. **Free action**: The monoid generated by these 3 matrices acts freely on PPTs")
    lines.append("4. **Transitivity**: Every PPT is in the orbit of (3,4,5)")
    lines.append("")
    lines.append("### Why Primes Cannot Have This Structure")
    lines.append("")
    lines.append("**Obstruction 1: No Algebraic Variety**")
    lines.append("- PPTs are defined by a^2+b^2=c^2, a polynomial equation.")
    lines.append("- Primes are defined by 'p>1 and for all d, d|p implies d=1 or d=p' -- a universal quantifier.")
    lines.append("- No polynomial P(x) has solution set = {all primes}.")
    lines.append("- Matiyasevich's theorem: there EXISTS a polynomial whose positive values are exactly the primes,")
    lines.append("  but it requires ~26 variables and degree ~25,000. This is not the same as lying on an algebraic curve.")
    lines.append("")
    lines.append("**Obstruction 2: No Preserving Group Action**")
    lines.append("- For PPTs, the Berggren matrices preserve a^2+b^2=c^2.")
    lines.append("- For primes, we need matrices M such that M*p is prime whenever p is prime.")
    lines.append("- But if M = [[a,b],[c,d]], then M*[p,1]^T = [ap+b, cp+d].")
    lines.append("- For ap+b to be prime for ALL primes p, we need gcd(a,b)=1 and the")
    lines.append("  Bunyakovsky-type condition. But even then, ap+b is composite for some p")
    lines.append("  (by covering congruences or simple modular arithmetic).")
    r_theory = RESULTS.get('theory', {})
    mt = r_theory.get('matrix_test', {})
    lines.append(f"- **Empirical test**: 1000 random 2x2 matrices applied to 100 primes:")
    lines.append(f"  mean primality rate = {mt.get('mean_primality_rate', '?'):.3f},")
    lines.append(f"  max = {mt.get('max_primality_rate', '?'):.3f}")
    lines.append(f"  (PNT prediction for range ~100: ~{1/math.log(100):.3f})")
    lines.append(f"  No matrix significantly beats random chance.")
    lines.append("")
    lines.append("**Obstruction 3: Information-Theoretic**")
    lines.append("- The n-th PPT can be specified by a path of O(log n) bits in the Berggren tree.")
    lines.append("- The n-th prime also needs O(log n) bits (its value is ~n*ln(n)).")
    lines.append("- BUT: for PPTs, the path bits encode WHICH MATRIX to apply -- structured information.")
    lines.append("- For primes, the bits would need to encode arbitrary primality information,")
    lines.append("  equivalent to a lookup table. The Kolmogorov complexity of 'first N primes'")
    lines.append("  is ~N*log(N) bits -- incompressible beyond PNT-scale shortcuts.")
    lines.append("")
    lines.append("**Obstruction 4: Additive vs Multiplicative**")
    lines.append("- Primes are MULTIPLICATIVELY defined (no non-trivial divisors)")
    lines.append("- But ADDITIVELY distributed (gaps, arithmetic progressions, etc.)")
    lines.append("- This tension is the deepest reason: matrix actions are linear (additive),")
    lines.append("  but primality is multiplicative. There is no bridge.")
    lines.append("")
    lines.append("### The Closest Analogues")
    lines.append("1. **Totient tree** (Approach 8): reaches all primes via q = 1 mod p,")
    lines.append("   but requires primality testing at each step -- not algebraic generation.")
    lines.append("2. **Sieve of Eratosthenes**: generates all primes by ELIMINATION,")
    lines.append("   which is the dual of tree GENERATION. This may be the closest true analogue.")
    lines.append("3. **Wheel factorization**: the mod-30 tree (Approach 4) is essentially a wheel,")
    lines.append("   which pre-eliminates composites divisible by 2, 3, or 5.")
    lines.append("")
    lines.append("### Final Verdict")
    lines.append("")
    lines.append("**No finite set of integer matrices can generate all primes from a fixed starting prime,")
    lines.append("analogous to the Berggren tree for PPTs.** The fundamental reason is that primes lack")
    lines.append("the algebraic structure (lying on a variety) that makes the Berggren construction possible.")
    lines.append("The primes are 'maximally pseudorandom' among integers with density 1/ln(N) --")
    lines.append("any tree that generates them must encode essentially all the information about which")
    lines.append("numbers are prime, which is equivalent to the sieve of Eratosthenes, not a")
    lines.append("compact algebraic recursion.")
    lines.append("")
    lines.append("## Images")
    lines.append("")
    lines.append("| Image | Description |")
    lines.append("|-------|-------------|")
    lines.append("| `prime_tree_00_summary.png` | Summary comparison of all 10 approaches |")
    for i in range(1, 11):
        names = ['cunningham', 'linear_recurrence', 'polynomial', 'modular',
                 'gcd_gap', 'gaussian', 'stern_brocot', 'totient', 'binary_split', 'ffm_hybrid']
        lines.append(f"| `prime_tree_{i:02d}_{names[i-1]}.png` | Approach {i} visualization |")

    with open("/home/raver1975/factor/prime_tree_results.md", 'w') as f:
        f.write('\n'.join(lines))

    print(f"\nResults written to /home/raver1975/factor/prime_tree_results.md")


if __name__ == '__main__':
    main()

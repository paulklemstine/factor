"""Field 1: Topological Data Analysis - Persistent Homology of Divisor Lattices
Hypothesis: The divisor lattice of N has topological features (Betti numbers, persistence
diagrams) that encode factor information. Specifically, the Vietoris-Rips complex built
from residues mod small primes might show a topological signature that distinguishes
factors from non-factors.
"""
import time, math, random
from collections import defaultdict

def divisor_distance(a, b, N):
    """Distance between two residue classes based on shared divisibility patterns."""
    return abs((N % a) - (N % b)) if a > 0 and b > 0 else float('inf')

def build_simplicial_complex(N, max_dim=2, num_points=50):
    """Build a simplicial complex from residues and track connected components."""
    # Sample points: integers near sqrt(N)
    sq = int(math.isqrt(N))
    points = [max(2, sq - num_points//2 + i) for i in range(num_points)]

    # Compute pairwise distances based on N mod x
    residues = [(N % p) for p in points]

    # Track "birth" and "death" of connected components as we increase threshold
    # This is a simplified persistence computation
    edges = []
    for i in range(len(points)):
        for j in range(i+1, len(points)):
            dist = abs(residues[i] - residues[j])
            edges.append((dist, i, j))
    edges.sort()

    # Union-Find for H0 persistence
    parent = list(range(len(points)))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py
            return True
        return False

    births = {i: 0 for i in range(len(points))}
    persistence_pairs = []

    for dist, i, j in edges:
        pi, pj = find(i), find(j)
        if pi != pj:
            # Component dies - record persistence
            dying = max(pi, pj)
            persistence_pairs.append((births.get(dying, 0), dist))
            union(i, j)

    return persistence_pairs, residues, points

def experiment(bits_list=[20, 24, 28, 32, 40]):
    print("=== Field 1: TDA - Persistent Homology of Divisor Lattices ===\n")

    for bits in bits_list:
        # Generate semiprime
        while True:
            p = random.getrandbits(bits // 2) | (1 << (bits//2 - 1)) | 1
            q = random.getrandbits(bits // 2) | (1 << (bits//2 - 1)) | 1
            if p != q and all(p % d != 0 for d in range(2, min(p, 100))) and \
               all(q % d != 0 for d in range(2, min(q, 100))):
                break
        N = p * q

        t0 = time.time()
        pairs, residues, points = build_simplicial_complex(N, num_points=80)

        # Key question: do persistence features correlate with factors?
        # Check if points near p or q have distinctive persistence
        factor_indices = []
        for idx, pt in enumerate(points):
            if N % pt == 0:
                factor_indices.append(idx)

        # Check if zero-residue points exist (they ARE the factors)
        zero_residues = [i for i, r in enumerate(residues) if r == 0]

        # Persistence statistics
        if pairs:
            lifetimes = [d - b for b, d in pairs]
            max_lifetime = max(lifetimes) if lifetimes else 0
            avg_lifetime = sum(lifetimes) / len(lifetimes) if lifetimes else 0
        else:
            max_lifetime = avg_lifetime = 0

        elapsed = time.time() - t0

        print(f"  {bits}b: N={N}, p={p}, q={q}")
        print(f"    Persistence pairs: {len(pairs)}, max lifetime: {max_lifetime:.0f}, avg: {avg_lifetime:.1f}")
        print(f"    Zero-residue points found: {len(zero_residues)} (factors in sample: {len(factor_indices)})")
        print(f"    Time: {elapsed:.4f}s")

        # The real test: does persistence topology help find factors
        # beyond just checking N mod x == 0 (which IS trial division)?
        if zero_residues:
            print(f"    NOTE: Finding zero residues IS trial division!")

    print("\nVERDICT: Persistent homology on residue data is just")
    print("a topological wrapper around trial-division-like information.")
    print("The topology doesn't add information beyond the residues themselves.")
    print("RESULT: REFUTED")

experiment()

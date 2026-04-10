#!/usr/bin/env python3
"""
Berggren Tree Ramanujan Property: Computational Demonstrations

This script explores the spectral properties of the Berggren tree,
which generates all primitive Pythagorean triples.

Demonstrations:
1. Tree generation and visualization
2. Spectral gap computation for finite quotients
3. Random walk mixing analysis
4. Return probability computation
5. Eigenvalue distribution of quotient graphs
"""

import numpy as np
from collections import deque
import math

# ============================================================
# §1. Berggren Matrices
# ============================================================

B1 = np.array([[1, -2, 2], [2, -1, 2], [2, -2, 3]])
B2 = np.array([[1, 2, 2], [2, 1, 2], [2, 2, 3]])
B3 = np.array([[-1, 2, 2], [-2, 1, 2], [-2, 2, 3]])

BERGGREN_MATRICES = [B1, B2, B3]

# Lorentz form Q = diag(1, 1, -1)
Q = np.diag([1, 1, -1])


def verify_lorentz(B, name="B"):
    """Verify that B preserves the Lorentz form."""
    result = B.T @ Q @ B
    is_preserved = np.allclose(result, Q)
    print(f"  {name}^T Q {name} = Q: {is_preserved}")
    return is_preserved


def verify_pythagorean(triple):
    """Check if (a,b,c) is a Pythagorean triple."""
    a, b, c = triple
    return a**2 + b**2 == c**2


# ============================================================
# §2. Tree Generation
# ============================================================

def generate_tree(depth):
    """Generate all Berggren tree nodes up to given depth."""
    root = np.array([3, 4, 5])
    nodes = {(): root}  # path -> triple

    queue = deque([((), root)])
    while queue:
        path, triple = queue.popleft()
        if len(path) >= depth:
            continue
        for i, B in enumerate(BERGGREN_MATRICES):
            child_path = path + (i,)
            child_triple = B @ triple
            nodes[child_path] = child_triple
            queue.append((child_path, child_triple))

    return nodes


def tree_statistics(nodes):
    """Compute statistics about the generated tree."""
    triples = list(nodes.values())
    hypotenuses = [t[2] for t in triples]

    print(f"\n  Nodes: {len(nodes)}")
    print(f"  Min hypotenuse: {min(hypotenuses)}")
    print(f"  Max hypotenuse: {max(hypotenuses)}")
    print(f"  Mean hypotenuse: {np.mean(hypotenuses):.1f}")

    # Verify all are Pythagorean triples
    all_pyth = all(verify_pythagorean(t) for t in triples)
    print(f"  All Pythagorean: {all_pyth}")

    return hypotenuses


# ============================================================
# §3. Adjacency Matrix and Spectrum
# ============================================================

def build_adjacency_matrix(depth):
    """Build the adjacency matrix of the Berggren tree truncated at depth d."""
    nodes = generate_tree(depth)
    paths = sorted(nodes.keys(), key=lambda p: (len(p), p))
    path_to_idx = {p: i for i, p in enumerate(paths)}
    n = len(paths)
    A = np.zeros((n, n))

    for path in paths:
        # Connect to children
        for i in range(3):
            child = path + (i,)
            if child in path_to_idx:
                A[path_to_idx[path], path_to_idx[child]] = 1
                A[path_to_idx[child], path_to_idx[path]] = 1

    return A, paths


def compute_spectrum(depth):
    """Compute the spectrum of the truncated Berggren tree."""
    A, paths = build_adjacency_matrix(depth)
    eigenvalues = np.linalg.eigvalsh(A)
    eigenvalues = np.sort(eigenvalues)[::-1]  # descending
    return eigenvalues


# ============================================================
# §4. Random Walk Mixing
# ============================================================

def random_walk_mixing(depth, num_walks=1000, walk_length=100):
    """Simulate random walks and measure mixing."""
    nodes = generate_tree(depth)
    paths = sorted(nodes.keys(), key=lambda p: (len(p), p))
    n = len(paths)

    # Build adjacency list
    adj = {p: [] for p in paths}
    for path in paths:
        for i in range(3):
            child = path + (i,)
            if child in adj:
                adj[path].append(child)
                adj[child].append(path)
        # Parent
        if path:
            parent = path[:-1]
            if parent in adj and parent not in adj[path]:
                pass  # already added above

    # Random walk from root
    visit_counts = np.zeros(n)
    path_to_idx = {p: i for i, p in enumerate(paths)}

    for _ in range(num_walks):
        current = ()  # root
        for step in range(walk_length):
            neighbors = adj[current]
            if neighbors:
                current = neighbors[np.random.randint(len(neighbors))]
        visit_counts[path_to_idx[current]] += 1

    # Compare to uniform distribution
    uniform = num_walks / n
    total_variation = 0.5 * np.sum(np.abs(visit_counts / num_walks - 1 / n))

    return total_variation, visit_counts


def mixing_time_experiment(depth, target_tv=0.1, num_trials=500):
    """Estimate mixing time by varying walk length."""
    nodes = generate_tree(depth)
    paths = sorted(nodes.keys(), key=lambda p: (len(p), p))
    n = len(paths)
    path_to_idx = {p: i for i, p in enumerate(paths)}

    # Build adjacency list
    adj = {p: [] for p in paths}
    for path in paths:
        for i in range(3):
            child = path + (i,)
            if child in adj:
                adj[path].append(child)
                adj[child].append(path)

    results = []
    for walk_len in range(1, 50):
        visit_counts = np.zeros(n)
        for _ in range(num_trials):
            current = ()
            for _ in range(walk_len):
                neighbors = adj[current]
                if neighbors:
                    current = neighbors[np.random.randint(len(neighbors))]
            visit_counts[path_to_idx[current]] += 1

        tv = 0.5 * np.sum(np.abs(visit_counts / num_trials - 1 / n))
        results.append((walk_len, tv))

        if tv < target_tv:
            break

    return results


# ============================================================
# §5. Return Probabilities
# ============================================================

def return_probability(depth, max_steps=20, num_walks=10000):
    """Estimate return probabilities for random walks from root."""
    nodes = generate_tree(depth)
    paths = sorted(nodes.keys(), key=lambda p: (len(p), p))

    adj = {p: [] for p in paths}
    for path in paths:
        for i in range(3):
            child = path + (i,)
            if child in adj:
                adj[path].append(child)
                adj[child].append(path)

    return_probs = []
    for steps in range(1, max_steps + 1):
        returns = 0
        for _ in range(num_walks):
            current = ()
            for _ in range(steps):
                neighbors = adj[current]
                if neighbors:
                    current = neighbors[np.random.randint(len(neighbors))]
            if current == ():
                returns += 1
        return_probs.append((steps, returns / num_walks))

    return return_probs


# ============================================================
# §6. Ramanujan Bound Check
# ============================================================

def check_ramanujan(eigenvalues, d):
    """Check if eigenvalues satisfy the Ramanujan bound for d-regular graph."""
    bound = 2 * math.sqrt(d - 1)

    # Nontrivial eigenvalues (exclude the largest, which should be ≈ d)
    nontrivial = eigenvalues[1:]  # eigenvalues sorted descending

    max_nontrivial = max(abs(e) for e in nontrivial)

    is_ramanujan = max_nontrivial <= bound + 1e-10  # numerical tolerance

    return is_ramanujan, max_nontrivial, bound


# ============================================================
# §7. Spectral Gap Analysis
# ============================================================

def spectral_gap_by_depth():
    """Compute spectral gap for increasing tree depths."""
    print("\n  Depth | Nodes | λ₁    | λ₂    | Gap   | Ramanujan bound")
    print("  " + "-" * 60)

    for depth in range(1, 7):
        eigenvalues = compute_spectrum(depth)
        n = len(eigenvalues)

        lambda1 = eigenvalues[0]
        lambda2 = eigenvalues[1] if n > 1 else 0

        gap = lambda1 - lambda2

        # The tree is NOT regular, but we can compare to bounds
        # Root has degree 3, others have degree 4 (except leaves which have degree 1)
        bound_3 = 2 * math.sqrt(2)
        bound_4 = 2 * math.sqrt(3)

        print(f"  {depth:5d} | {n:5d} | {lambda1:5.3f} | {lambda2:5.3f} | {gap:5.3f} | "
              f"2√2={bound_3:.3f}, 2√3={bound_4:.3f}")


# ============================================================
# Main Demonstration
# ============================================================

def main():
    print("=" * 70)
    print("BERGGREN TREE RAMANUJAN PROPERTY: COMPUTATIONAL EXPLORATION")
    print("=" * 70)

    # Demo 1: Verify Lorentz preservation
    print("\n§1. Lorentz Form Preservation")
    print("-" * 40)
    for name, B in [("B₁", B1), ("B₂", B2), ("B₃", B3)]:
        verify_lorentz(B, name)

    # Demo 2: Determinants
    print("\n§2. Determinants")
    print("-" * 40)
    for name, B in [("B₁", B1), ("B₂", B2), ("B₃", B3)]:
        print(f"  det({name}) = {int(round(np.linalg.det(B)))}")

    # Demo 3: Involution check
    print("\n§3. Involution Check (B² = I?)")
    print("-" * 40)
    for name, B in [("B₁", B1), ("B₂", B2), ("B₃", B3)]:
        is_involution = np.allclose(B @ B, np.eye(3))
        print(f"  {name}² = I: {is_involution}")

    # Demo 4: Tree generation
    print("\n§4. Berggren Tree Generation")
    print("-" * 40)
    nodes = generate_tree(4)
    tree_statistics(nodes)

    # Demo 5: First few triples
    print("\n§5. First Two Levels of the Tree")
    print("-" * 40)
    for path in sorted(nodes.keys(), key=lambda p: (len(p), p)):
        if len(path) <= 1:
            triple = nodes[path]
            depth_str = "  " * len(path)
            dir_names = {0: "B₁", 1: "B₂", 2: "B₃"}
            path_str = " → ".join(dir_names[d] for d in path) if path else "root"
            print(f"  {depth_str}[{path_str}] ({triple[0]}, {triple[1]}, {triple[2]})")

    # Demo 6: Spectral analysis
    print("\n§6. Spectral Gap Analysis by Depth")
    print("-" * 40)
    spectral_gap_by_depth()

    # Demo 7: Eigenvalue distribution
    print("\n§7. Eigenvalue Distribution (depth 5)")
    print("-" * 40)
    evals = compute_spectrum(5)
    print(f"  Number of eigenvalues: {len(evals)}")
    print(f"  Largest: {evals[0]:.4f}")
    print(f"  Smallest: {evals[-1]:.4f}")
    print(f"  2nd largest: {evals[1]:.4f}")
    print(f"  2nd smallest: {evals[-2]:.4f}")
    print(f"  Spectral gap (λ₁ - λ₂): {evals[0] - evals[1]:.4f}")
    print(f"  Ramanujan bound (2√2): {2*math.sqrt(2):.4f}")
    print(f"  Ramanujan bound (2√3): {2*math.sqrt(3):.4f}")

    # Demo 8: Return probabilities
    print("\n§8. Return Probabilities (depth 4, 10000 walks)")
    print("-" * 40)
    rp = return_probability(4, max_steps=12, num_walks=5000)
    print("  Steps | P(return to root)")
    for steps, prob in rp:
        bar = "█" * int(prob * 100)
        print(f"  {steps:5d} | {prob:.4f} {bar}")

    # Demo 9: Key constants
    print("\n§9. Key Spectral Constants")
    print("-" * 40)
    gamma3 = 3 - 2 * math.sqrt(2)
    gamma4 = 4 - 2 * math.sqrt(3)
    print(f"  Ramanujan bound (d=3): 2√2 = {2*math.sqrt(2):.6f}")
    print(f"  Ramanujan bound (d=4): 2√3 = {2*math.sqrt(3):.6f}")
    print(f"  Spectral gap (d=3): 3 - 2√2 = {gamma3:.6f}")
    print(f"  Spectral gap (d=4): 4 - 2√3 = {gamma4:.6f}")
    print(f"  (3 - 2√2)² = {gamma3**2:.6f} ≈ 17 - 12√2 = {17 - 12*math.sqrt(2):.6f}")
    print(f"  Cheeger bound (d=3): {gamma3/2:.6f}")
    print(f"  Cheeger bound (d=4): {gamma4/2:.6f}")

    # Demo 10: Trace analysis
    print("\n§10. Matrix Trace Analysis")
    print("-" * 40)
    matrices = {"B₁": B1, "B₂": B2, "B₃": B3}
    for name, B in matrices.items():
        print(f"  tr({name}) = {int(np.trace(B))}")
    for n1, B_i in matrices.items():
        for n2, B_j in matrices.items():
            prod = B_i @ B_j
            print(f"  tr({n1}·{n2}) = {int(np.trace(prod))}, det = {int(round(np.linalg.det(prod)))}")

    print("\n" + "=" * 70)
    print("EXPLORATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()

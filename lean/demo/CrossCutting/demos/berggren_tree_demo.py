#!/usr/bin/env python3
"""
Berggren Tree and O(2,1;Z) Demo

Demonstrates the Berggren tree generating all primitive Pythagorean triples,
the quadratic form preservation, and the Lorentz group connection.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Berggren matrices
M1 = np.array([[1, -2, 2], [2, -1, 2], [2, -2, 3]])
M2 = np.array([[1, 2, 2], [2, 1, 2], [2, 2, 3]])
M3 = np.array([[-1, 2, 2], [-2, 1, 2], [-2, 2, 3]])

# Signature matrix
Sigma = np.diag([1, 1, -1])

def verify_O21(M, name):
    """Verify M^T Sigma M = Sigma."""
    result = M.T @ Sigma @ M
    preserved = np.allclose(result, Sigma)
    det = int(round(np.linalg.det(M)))
    print(f"{name}: det = {det:+d}, preserves Σ: {preserved}")
    return preserved

def generate_tree(root, depth):
    """Generate the Berggren tree to given depth."""
    triples = [root]
    current_level = [root]
    for d in range(depth):
        next_level = []
        for t in current_level:
            for M in [M1, M2, M3]:
                child = M @ t
                triples.append(child)
                next_level.append(child)
        current_level = next_level
    return triples

def main():
    # Verify O(2,1;Z) membership
    print("=== O(2,1;ℤ) Verification ===")
    verify_O21(M1, "M₁")
    verify_O21(M2, "M₂")
    verify_O21(M3, "M₃")
    verify_O21(M1 @ M2, "M₁M₂")
    verify_O21(M1 @ M3, "M₁M₃")
    print()

    # Generate tree
    root = np.array([3, 4, 5])
    depth = 5
    triples = generate_tree(root, depth)

    # Verify Pythagorean property
    print(f"=== Tree Generation (depth {depth}) ===")
    print(f"Total triples: {len(triples)}")
    all_pyth = all(t[0]**2 + t[1]**2 == t[2]**2 for t in triples)
    print(f"All Pythagorean: {all_pyth}")
    all_pos = all(all(x > 0 for x in t) for t in triples)
    print(f"All positive: {all_pos}")
    print()

    # Show first few levels
    print("Level 0: (3, 4, 5)")
    print("Level 1:", [(tuple(M @ root)) for M in [M1, M2, M3]])
    print()

    # Plot
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # 1. Tree visualization (hypotenuse vs index)
    ax = axes[0]
    hyps = [t[2] for t in triples]
    colors = []
    idx = 0
    for d in range(depth + 1):
        n = 3**d
        colors.extend([d] * n)
    ax.scatter(range(len(triples)), hyps, c=colors[:len(triples)],
               cmap='viridis', s=10, alpha=0.7)
    ax.set_xlabel('Triple index', fontsize=12)
    ax.set_ylabel('Hypotenuse c', fontsize=12)
    ax.set_title('Berggren Tree: Hypotenuse Growth', fontsize=14)
    ax.set_yscale('log')
    cbar = plt.colorbar(ax.scatter(range(len(triples)), hyps,
                                    c=colors[:len(triples)],
                                    cmap='viridis', s=0), ax=ax)
    cbar.set_label('Tree depth')

    # 2. Triples in (a,b) plane
    ax = axes[1]
    a_vals = [t[0] for t in triples]
    b_vals = [t[1] for t in triples]
    ax.scatter(a_vals, b_vals, c=colors[:len(triples)],
               cmap='viridis', s=15, alpha=0.5)
    ax.set_xlabel('a (leg 1)', fontsize=12)
    ax.set_ylabel('b (leg 2)', fontsize=12)
    ax.set_title('Pythagorean Triples in (a,b) Plane', fontsize=14)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)

    # 3. Quadratic form verification
    ax = axes[2]
    Q_vals = [t[0]**2 + t[1]**2 - t[2]**2 for t in triples]
    ax.plot(range(len(triples)), Q_vals, 'g-', linewidth=0.5)
    ax.scatter(range(len(triples)), Q_vals, c='green', s=5)
    ax.set_xlabel('Triple index', fontsize=12)
    ax.set_ylabel('Q(a,b,c) = a² + b² - c²', fontsize=12)
    ax.set_title('Quadratic Form Invariance (Q = 0)', fontsize=14)
    ax.axhline(y=0, color='red', linestyle='--', alpha=0.5)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('/workspace/request-project/CrossCutting/demos/berggren_tree.png',
                dpi=150, bbox_inches='tight')
    print("Saved: berggren_tree.png")

    # Trace analysis
    print("\n=== Trace Analysis ===")
    print(f"tr(M₁) = {int(np.trace(M1))}")
    print(f"tr(M₂) = {int(np.trace(M2))}")
    print(f"tr(M₃) = {int(np.trace(M3))}")
    print(f"tr(M₁M₂) = {int(np.trace(M1 @ M2))}")
    print(f"tr(M₁M₃) = {int(np.trace(M1 @ M3))}")

if __name__ == '__main__':
    main()

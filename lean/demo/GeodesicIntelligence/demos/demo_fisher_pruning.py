#!/usr/bin/env python3
"""
Demo: Fisher Information Pruning for Neural Networks
=====================================================

Demonstrates how the Fisher Information Matrix identifies redundant
parameters in a neural network. Parameters with small Fisher eigenvalues
carry little information and can be pruned.

Part of the Geodesic Intelligence research program.
"""

import numpy as np
import json
from typing import Tuple, List

def sigmoid(x):
    """Numerically stable sigmoid."""
    return np.where(x >= 0, 1 / (1 + np.exp(-x)), np.exp(x) / (1 + np.exp(x)))

def create_toy_network(input_dim: int, hidden_dim: int, output_dim: int, seed: int = 42):
    """Create a simple 2-layer network with random weights."""
    rng = np.random.RandomState(seed)
    W1 = rng.randn(input_dim, hidden_dim) * 0.5
    b1 = rng.randn(hidden_dim) * 0.1
    W2 = rng.randn(hidden_dim, output_dim) * 0.5
    b2 = rng.randn(output_dim) * 0.1
    return W1, b1, W2, b2

def forward(x, W1, b1, W2, b2):
    """Forward pass through 2-layer network."""
    h = sigmoid(x @ W1 + b1)
    logits = h @ W2 + b2
    probs = sigmoid(logits)
    return probs, h

def compute_fisher_diagonal(X, W1, b1, W2, b2, n_samples=1000):
    """
    Compute the diagonal of the Fisher Information Matrix.
    F_ii = E[(d log p / d theta_i)^2]
    """
    params = np.concatenate([W1.ravel(), b1, W2.ravel(), b2])
    n_params = len(params)
    fisher_diag = np.zeros(n_params)

    for i in range(min(n_samples, len(X))):
        x = X[i:i+1]
        probs, h = forward(x, W1, b1, W2, b2)
        p = probs[0, 0]
        p = np.clip(p, 1e-7, 1 - 1e-7)

        # Gradient of log p(y|x) w.r.t. output
        # For Bernoulli: d log p / d logit = y - p
        # We use the expected Fisher: E_y[(y-p)^2] = p(1-p)
        output_grad_var = p * (1 - p)

        # Backprop to compute gradient variances
        # d logit / d W2 = h^T, d logit / d b2 = 1
        dW2 = np.outer(h[0], np.ones(1))
        db2 = np.ones(1)

        # d logit / d h = W2
        dh = W2  # (hidden, 1)
        # d h / d z = h * (1-h) (sigmoid derivative)
        dz = (h * (1 - h))[0]  # (hidden,)
        # d z / d W1 = x^T, d z / d b1 = 1
        dW1 = np.outer(x[0], dz * dh.ravel())
        db1 = dz * dh.ravel()

        # Fisher diagonal = grad^2 * output_variance
        grad = np.concatenate([dW1.ravel(), db1, dW2.ravel(), db2])
        fisher_diag += output_grad_var * grad**2

    fisher_diag /= n_samples
    return fisher_diag

def prune_by_fisher(fisher_diag, threshold_percentile=75):
    """Identify parameters to prune based on Fisher information."""
    threshold = np.percentile(fisher_diag, threshold_percentile)
    mask = fisher_diag >= threshold
    return mask, threshold

def demo():
    """Run the Fisher pruning demonstration."""
    print("=" * 70)
    print("DEMO: Fisher Information Pruning")
    print("=" * 70)

    # Setup
    input_dim, hidden_dim, output_dim = 10, 50, 1
    n_data = 500

    rng = np.random.RandomState(42)
    X = rng.randn(n_data, input_dim)

    W1, b1, W2, b2 = create_toy_network(input_dim, hidden_dim, output_dim)
    total_params = W1.size + b1.size + W2.size + b2.size

    print(f"\nNetwork: {input_dim} -> {hidden_dim} -> {output_dim}")
    print(f"Total parameters: {total_params}")

    # Compute Fisher diagonal
    print("\nComputing Fisher Information Matrix (diagonal)...")
    fisher_diag = compute_fisher_diagonal(X, W1, b1, W2, b2)

    # Analyze Fisher spectrum
    sorted_fisher = np.sort(fisher_diag)[::-1]
    cumulative = np.cumsum(sorted_fisher) / np.sum(sorted_fisher)

    print(f"\nFisher Information Spectrum:")
    print(f"  Max eigenvalue:  {sorted_fisher[0]:.6f}")
    print(f"  Min eigenvalue:  {sorted_fisher[-1]:.10f}")
    print(f"  Dynamic range:   {sorted_fisher[0] / max(sorted_fisher[-1], 1e-15):.1f}x")
    print(f"  Mean:            {np.mean(fisher_diag):.6f}")
    print(f"  Median:          {np.median(fisher_diag):.6f}")

    # Find effective dimension
    for target in [0.90, 0.95, 0.99]:
        eff_dim = np.searchsorted(cumulative, target) + 1
        print(f"  {target*100:.0f}% info in top: {eff_dim}/{total_params} params "
              f"({100*eff_dim/total_params:.1f}%)")

    # Prune at different levels
    print(f"\nPruning Analysis:")
    print(f"{'Percentile':>12} {'Kept':>8} {'Pruned':>8} {'% Kept':>8} {'Info Retained':>15}")
    print("-" * 55)

    for pct in [50, 75, 90, 95]:
        mask, threshold = prune_by_fisher(fisher_diag, pct)
        kept = mask.sum()
        pruned = total_params - kept
        info_kept = fisher_diag[mask].sum() / fisher_diag.sum()
        print(f"{pct:>10}th {kept:>8} {pruned:>8} {100*kept/total_params:>7.1f}% "
              f"{100*info_kept:>14.2f}%")

    # Demonstrate the Cramér-Rao bound
    print(f"\nCramér-Rao Bound Demonstration:")
    print(f"  For each parameter θᵢ, Var(θ̂ᵢ) ≥ 1/F(θᵢ)")
    top_5 = np.argsort(fisher_diag)[-5:][::-1]
    bot_5 = np.argsort(fisher_diag)[:5]
    print(f"\n  Top 5 most informative parameters:")
    for i, idx in enumerate(top_5):
        print(f"    θ_{idx}: F={fisher_diag[idx]:.6f}, "
              f"min variance={1/max(fisher_diag[idx], 1e-15):.2f}")
    print(f"\n  Bottom 5 least informative parameters:")
    for i, idx in enumerate(bot_5):
        fi = max(fisher_diag[idx], 1e-15)
        print(f"    θ_{idx}: F={fisher_diag[idx]:.10f}, "
              f"min variance={1/fi:.0f}")

    # Save results
    results = {
        "network": {"input": input_dim, "hidden": hidden_dim, "output": output_dim},
        "total_params": total_params,
        "fisher_stats": {
            "max": float(sorted_fisher[0]),
            "min": float(sorted_fisher[-1]),
            "mean": float(np.mean(fisher_diag)),
            "median": float(np.median(fisher_diag)),
        },
        "effective_dimensions": {
            "90pct": int(np.searchsorted(cumulative, 0.90) + 1),
            "95pct": int(np.searchsorted(cumulative, 0.95) + 1),
            "99pct": int(np.searchsorted(cumulative, 0.99) + 1),
        },
        "pruning_results": {}
    }
    for pct in [50, 75, 90, 95]:
        mask, _ = prune_by_fisher(fisher_diag, pct)
        info_kept = fisher_diag[mask].sum() / fisher_diag.sum()
        results["pruning_results"][f"{pct}th_percentile"] = {
            "kept": int(mask.sum()),
            "info_retained": float(info_kept)
        }

    print(f"\n✓ Demo complete. Key finding: {results['effective_dimensions']['95pct']}/{total_params} "
          f"parameters contain 95% of the information.")
    return results

if __name__ == "__main__":
    demo()

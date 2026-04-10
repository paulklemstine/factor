#!/usr/bin/env python3
"""
LogSumExp Tropical-Quantum Bridge Demo

Demonstrates the smooth interpolation between tropical max and classical averaging
via the LogSumExp function with temperature parameter epsilon.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def logsumexp(eps, x, y):
    """LogSumExp with temperature eps."""
    return eps * np.log(np.exp(x/eps) + np.exp(y/eps))

def softmax_fst(eps, x, y):
    """First softmax component."""
    return np.exp(x/eps) / (np.exp(x/eps) + np.exp(y/eps))

def main():
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    # 1. LSE vs max for varying epsilon
    ax = axes[0, 0]
    x_vals = np.linspace(-3, 3, 200)
    y_fixed = 0.0
    epsilons = [0.1, 0.5, 1.0, 2.0, 5.0]
    colors = plt.cm.coolwarm(np.linspace(0, 1, len(epsilons)))

    ax.plot(x_vals, np.maximum(x_vals, y_fixed), 'k-', linewidth=3,
            label='max(x, 0) [tropical]', alpha=0.5)
    for eps, color in zip(epsilons, colors):
        lse = logsumexp(eps, x_vals, y_fixed)
        ax.plot(x_vals, lse, color=color, linewidth=1.5, label=f'ε = {eps}')
    ax.set_xlabel('x', fontsize=12)
    ax.set_ylabel('LSE_ε(x, 0)', fontsize=12)
    ax.set_title('LogSumExp: Tropical → Classical Bridge', fontsize=14)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # 2. Error bound: LSE - max ≤ ε·ln(2)
    ax = axes[0, 1]
    x_test, y_test = 1.0, 2.0
    eps_range = np.linspace(0.01, 5, 200)
    errors = [logsumexp(e, x_test, y_test) - max(x_test, y_test) for e in eps_range]
    bounds = [e * np.log(2) for e in eps_range]

    ax.plot(eps_range, errors, 'b-', linewidth=2, label='LSE_ε(1,2) - max(1,2)')
    ax.plot(eps_range, bounds, 'r--', linewidth=2, label='ε · ln(2) [upper bound]')
    ax.fill_between(eps_range, 0, bounds, alpha=0.1, color='red')
    ax.set_xlabel('ε (temperature)', fontsize=12)
    ax.set_ylabel('Approximation error', fontsize=12)
    ax.set_title('Error Bound: max ≤ LSE ≤ max + ε·ln(2)', fontsize=14)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    # 3. Softmax transition
    ax = axes[1, 0]
    x_vals2 = np.linspace(-5, 5, 200)
    for eps in [0.1, 0.5, 1.0, 2.0, 5.0]:
        probs = softmax_fst(eps, x_vals2, 0)
        ax.plot(x_vals2, probs, linewidth=1.5, label=f'ε = {eps}')
    ax.axhline(y=0.5, color='gray', linestyle=':', alpha=0.5)
    ax.set_xlabel('x', fontsize=12)
    ax.set_ylabel('softmax₁(x, 0)', fontsize=12)
    ax.set_title('Softmax: Sharp → Smooth Selection', fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    # 4. 2D contour of LSE
    ax = axes[1, 1]
    x_grid = np.linspace(-3, 3, 100)
    y_grid = np.linspace(-3, 3, 100)
    X, Y = np.meshgrid(x_grid, y_grid)
    eps_demo = 0.5
    Z = logsumexp(eps_demo, X, Y)
    cs = ax.contourf(X, Y, Z, levels=20, cmap='viridis')
    ax.contour(X, Y, Z, levels=20, colors='white', linewidths=0.3, alpha=0.5)
    plt.colorbar(cs, ax=ax, label=f'LSE_{{ε={eps_demo}}}(x, y)')
    # Add max(x,y) contours for comparison
    Z_max = np.maximum(X, Y)
    ax.contour(X, Y, Z_max, levels=10, colors='red', linewidths=1, linestyles='--',
               alpha=0.5)
    ax.set_xlabel('x', fontsize=12)
    ax.set_ylabel('y', fontsize=12)
    ax.set_title(f'LSE contours (filled) vs max contours (red dashed)', fontsize=13)

    plt.tight_layout()
    plt.savefig('/workspace/request-project/CrossCutting/demos/logsumexp_bridge.png',
                dpi=150, bbox_inches='tight')
    print("Saved: logsumexp_bridge.png")

    # Print key values
    print("\n=== Key Verified Properties ===")
    eps = 1.0
    x, y = 2.0, 2.0
    print(f"LSE_{eps}({x}, {y}) = {logsumexp(eps, x, y):.6f}")
    print(f"Expected: {x} + {eps}*ln(2) = {x + eps*np.log(2):.6f}")
    print(f"Match: {np.isclose(logsumexp(eps, x, y), x + eps*np.log(2))}")

    x, y = 3.0, 1.0
    mx = max(x, y)
    lse = logsumexp(eps, x, y)
    print(f"\nLSE_{eps}({x}, {y}) = {lse:.6f}")
    print(f"max({x}, {y}) = {mx}")
    print(f"max + ε·ln(2) = {mx + eps*np.log(2):.6f}")
    print(f"Sandwich: {mx:.6f} ≤ {lse:.6f} ≤ {mx + eps*np.log(2):.6f}: {mx <= lse <= mx + eps*np.log(2)}")

if __name__ == '__main__':
    main()

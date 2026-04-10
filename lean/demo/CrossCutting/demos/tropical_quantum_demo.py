#!/usr/bin/env python3
"""
Tropical–Quantum Bridge Demo

Demonstrates the ε-interpolation between tropical (max) and classical arithmetic
via the LogSumExp function.

Visualizations:
1. LSE_ε(x, y) for various ε values → convergence to max(x, y)
2. Softmax temperature sweep → from uniform to one-hot
3. The sandwich bound: max ≤ LSE ≤ max + ε·ln2
4. Tropical semiring operations
5. 2D contour comparison: max vs LSE
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from mpl_toolkits.mplot3d import Axes3D

# ──────────────────────────────────────────────────────────
# Core functions
# ──────────────────────────────────────────────────────────

def logsumexp(eps, x, y):
    """LogSumExp with temperature ε."""
    # Numerically stable version
    m = np.maximum(x, y)
    return m + eps * np.log(np.exp((x - m) / eps) + np.exp((y - m) / eps))

def softmax_probs(eps, x, y):
    """Softmax probabilities for two values."""
    m = np.maximum(x, y)
    e1 = np.exp((x - m) / eps)
    e2 = np.exp((y - m) / eps)
    s = e1 + e2
    return e1 / s, e2 / s

# ──────────────────────────────────────────────────────────

fig = plt.figure(figsize=(20, 14))
gs = GridSpec(2, 3, figure=fig, hspace=0.35, wspace=0.3)

# ──────────────────────────────────────────────────────────
# 1. LSE convergence to max as ε → 0
# ──────────────────────────────────────────────────────────

x = np.linspace(-3, 3, 500)
y_fixed = 0.5  # Fixed y value

ax1 = fig.add_subplot(gs[0, 0])
ax1.plot(x, np.maximum(x, y_fixed), 'k-', linewidth=3, label='max(x, 0.5) [tropical]', alpha=0.7)

colors = ['#ff6b6b', '#ffa502', '#2ed573', '#1e90ff', '#a55eea']
epsilons = [2.0, 1.0, 0.5, 0.2, 0.05]
for eps_val, color in zip(epsilons, colors):
    lse = logsumexp(eps_val, x, y_fixed)
    ax1.plot(x, lse, color=color, linewidth=1.5, label=f'LSE (ε={eps_val})')

ax1.set_title('LogSumExp → max as ε → 0', fontsize=14, fontweight='bold')
ax1.set_xlabel('x')
ax1.set_ylabel('LSE_ε(x, 0.5)')
ax1.legend(fontsize=8)
ax1.grid(True, alpha=0.3)

# ──────────────────────────────────────────────────────────
# 2. Softmax temperature sweep
# ──────────────────────────────────────────────────────────

scores = np.array([2.0, 1.0, 0.5, -0.5, -1.0])
eps_range = np.logspace(-1.5, 1.5, 100)

ax2 = fig.add_subplot(gs[0, 1])
for i, score in enumerate(scores):
    probs = []
    for eps_val in eps_range:
        # Softmax for multiple values
        exp_vals = np.exp(scores / eps_val - np.max(scores) / eps_val)
        p = exp_vals / np.sum(exp_vals)
        probs.append(p[i])
    ax2.semilogx(eps_range, probs, linewidth=2, label=f'score={score}')

ax2.axhline(y=0.2, color='gray', linestyle='--', alpha=0.3, label='uniform (1/5)')
ax2.set_title('Softmax: ε → 0 (hard) vs ε → ∞ (uniform)', fontsize=14, fontweight='bold')
ax2.set_xlabel('Temperature ε')
ax2.set_ylabel('Probability')
ax2.legend(fontsize=8)
ax2.grid(True, alpha=0.3)
ax2.annotate('Tropical\n(argmax)', xy=(0.03, 0.95), fontsize=9, color='red',
            xycoords='axes fraction', fontweight='bold')
ax2.annotate('Classical\n(uniform)', xy=(0.85, 0.5), fontsize=9, color='blue',
            xycoords='axes fraction', fontweight='bold')

# ──────────────────────────────────────────────────────────
# 3. Sandwich bounds: max ≤ LSE ≤ max + ε·ln2
# ──────────────────────────────────────────────────────────

eps_val = 0.5
ax3 = fig.add_subplot(gs[0, 2])
max_xy = np.maximum(x, y_fixed)
lse_xy = logsumexp(eps_val, x, y_fixed)
upper = max_xy + eps_val * np.log(2)

ax3.fill_between(x, max_xy, upper, alpha=0.2, color='green', label='Allowed region')
ax3.plot(x, max_xy, 'b-', linewidth=2, label='max(x, 0.5) [lower bound]')
ax3.plot(x, upper, 'r--', linewidth=2, label=f'max + ε·ln2 [upper bound]')
ax3.plot(x, lse_xy, 'k-', linewidth=2.5, label=f'LSE_ε(x, 0.5), ε={eps_val}')
ax3.set_title(f'Sandwich Bound (ε = {eps_val})', fontsize=14, fontweight='bold')
ax3.set_xlabel('x')
ax3.set_ylabel('Value')
ax3.legend(fontsize=8)
ax3.grid(True, alpha=0.3)
ax3.annotate(f'Gap = ε·ln2 ≈ {eps_val*np.log(2):.3f}',
            xy=(0.5, 0.85), fontsize=10, xycoords='axes fraction',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

# ──────────────────────────────────────────────────────────
# 4. Tropical semiring: distributivity
# ──────────────────────────────────────────────────────────

a_val = 1.0
ax4 = fig.add_subplot(gs[1, 0])
y_vals = np.linspace(-2, 2, 500)
x_vals = np.linspace(-2, 2, 500)

# a + max(x, y) = max(a+x, a+y)
for y_val in [-1.0, 0.0, 1.0]:
    lhs = a_val + np.maximum(x_vals, y_val)
    rhs = np.maximum(a_val + x_vals, a_val + y_val)
    ax4.plot(x_vals, lhs, linewidth=2, label=f'{a_val}+max(x,{y_val})')
    ax4.plot(x_vals, rhs, '--', linewidth=2, alpha=0.5)

ax4.set_title('Tropical Distributivity\na + max(x,y) = max(a+x, a+y)', fontsize=14, fontweight='bold')
ax4.set_xlabel('x')
ax4.set_ylabel('Value')
ax4.legend(fontsize=8)
ax4.grid(True, alpha=0.3)

# ──────────────────────────────────────────────────────────
# 5. 2D contour: max vs LSE
# ──────────────────────────────────────────────────────────

xx, yy = np.meshgrid(np.linspace(-2, 2, 200), np.linspace(-2, 2, 200))

ax5 = fig.add_subplot(gs[1, 1])
max_vals = np.maximum(xx, yy)
ax5.contour(xx, yy, max_vals, levels=15, cmap='RdYlBu')
ax5.contourf(xx, yy, max_vals, levels=15, cmap='RdYlBu', alpha=0.3)
ax5.set_title('max(x, y) [Tropical]', fontsize=14, fontweight='bold')
ax5.set_xlabel('x')
ax5.set_ylabel('y')
ax5.set_aspect('equal')

ax6 = fig.add_subplot(gs[1, 2])
lse_vals = logsumexp(0.3, xx, yy)
ax6.contour(xx, yy, lse_vals, levels=15, cmap='RdYlBu')
ax6.contourf(xx, yy, lse_vals, levels=15, cmap='RdYlBu', alpha=0.3)
ax6.set_title('LSE₀.₃(x, y) [Smooth Bridge]', fontsize=14, fontweight='bold')
ax6.set_xlabel('x')
ax6.set_ylabel('y')
ax6.set_aspect('equal')

plt.suptitle('The Tropical–Quantum Bridge via LogSumExp', fontsize=16, fontweight='bold', y=0.98)
plt.savefig('/workspace/request-project/CrossCutting/demos/tropical_quantum_demo.png', dpi=150, bbox_inches='tight')
plt.close()

print("✓ Tropical–quantum bridge demo saved to tropical_quantum_demo.png")

# ──────────────────────────────────────────────────────────
# Numerical verification
# ──────────────────────────────────────────────────────────
print("\n=== Numerical Verification ===")
test_x, test_y = 2.3, -1.7
for eps in [1.0, 0.5, 0.1, 0.01]:
    lse = logsumexp(eps, test_x, test_y)
    mx = max(test_x, test_y)
    print(f"ε={eps:6.3f}: max={mx:.3f}, LSE={lse:.6f}, gap={lse-mx:.6f}, ε·ln2={eps*np.log(2):.6f}, "
          f"within bound: {lse - mx <= eps * np.log(2) + 1e-10}")

# Softmax sums to 1
p1, p2 = softmax_probs(1.0, 3.0, -1.0)
print(f"\nSoftmax({3.0}, {-1.0}): p1={p1:.6f}, p2={p2:.6f}, sum={p1+p2:.10f}")

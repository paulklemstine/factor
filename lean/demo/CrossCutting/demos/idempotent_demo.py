#!/usr/bin/env python3
"""
Idempotent Collapse Principle — Interactive Demo

Demonstrates idempotence across multiple domains:
1. ReLU (neural networks)
2. Projection matrices (linear algebra / quantum mechanics)
3. Lattice operations (max/min)
4. Clamping functions (signal processing)
5. Finite function iteration
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# ──────────────────────────────────────────────────────────
# 1. ReLU Idempotence
# ──────────────────────────────────────────────────────────

def relu(x):
    return np.maximum(x, 0)

x = np.linspace(-3, 3, 500)
relu1 = relu(x)
relu2 = relu(relu1)
relu5 = relu(relu(relu(relu(relu1))))

fig = plt.figure(figsize=(18, 12))
gs = GridSpec(2, 3, figure=fig, hspace=0.35, wspace=0.3)

ax1 = fig.add_subplot(gs[0, 0])
ax1.plot(x, x, '--', color='gray', alpha=0.5, label='identity')
ax1.plot(x, relu1, 'b-', linewidth=2, label='ReLU(x)')
ax1.plot(x, relu2, 'r--', linewidth=2, label='ReLU(ReLU(x))')
ax1.plot(x, relu5, 'g:', linewidth=2, label='ReLU⁵(x)')
ax1.set_title('ReLU is Idempotent', fontsize=14, fontweight='bold')
ax1.set_xlabel('x')
ax1.set_ylabel('f(x)')
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.set_xlim(-3, 3)
ax1.set_ylim(-1, 3)

# ──────────────────────────────────────────────────────────
# 2. Projection Matrix Idempotence
# ──────────────────────────────────────────────────────────

# Projection onto the line y = x (angle π/4)
theta = np.pi / 4
P = np.array([[np.cos(theta)**2, np.cos(theta)*np.sin(theta)],
              [np.cos(theta)*np.sin(theta), np.sin(theta)**2]])

# Generate random 2D points
np.random.seed(42)
points = np.random.randn(50, 2) * 1.5

# Apply projection once and twice
proj1 = (P @ points.T).T
proj2 = (P @ proj1.T).T

ax2 = fig.add_subplot(gs[0, 1])
ax2.scatter(points[:, 0], points[:, 1], c='blue', alpha=0.3, s=30, label='Original')
ax2.scatter(proj1[:, 0], proj1[:, 1], c='red', alpha=0.7, s=30, label='P(x)')
ax2.scatter(proj2[:, 0], proj2[:, 1], c='green', marker='x', s=50, label='P(P(x)) = P(x)')
# Draw projection lines
for i in range(0, 50, 5):
    ax2.annotate('', xy=proj1[i], xytext=points[i],
                arrowprops=dict(arrowstyle='->', color='gray', alpha=0.3))
ax2.plot([-3, 3], [-3, 3], 'k--', alpha=0.3, label='y = x')
ax2.set_title('Projection P² = P', fontsize=14, fontweight='bold')
ax2.set_xlabel('x₁')
ax2.set_ylabel('x₂')
ax2.legend(fontsize=8)
ax2.grid(True, alpha=0.3)
ax2.set_xlim(-4, 4)
ax2.set_ylim(-4, 4)
ax2.set_aspect('equal')

# ──────────────────────────────────────────────────────────
# 3. Lattice Idempotence: max and min
# ──────────────────────────────────────────────────────────

a_val = 1.5  # Fixed lattice element
max_a = np.maximum(x, a_val)
max_a_twice = np.maximum(max_a, a_val)

min_a = np.minimum(x, a_val)
min_a_twice = np.minimum(min_a, a_val)

ax3 = fig.add_subplot(gs[0, 2])
ax3.plot(x, x, '--', color='gray', alpha=0.5, label='identity')
ax3.plot(x, max_a, 'b-', linewidth=2, label=f'max(x, {a_val})')
ax3.plot(x, max_a_twice, 'r--', linewidth=2, label=f'max(max(x,{a_val}),{a_val})')
ax3.plot(x, min_a, 'g-', linewidth=2, label=f'min(x, {a_val})')
ax3.plot(x, min_a_twice, 'm--', linewidth=2, label=f'min(min(x,{a_val}),{a_val})')
ax3.set_title('Lattice Idempotence', fontsize=14, fontweight='bold')
ax3.set_xlabel('x')
ax3.set_ylabel('f(x)')
ax3.legend(fontsize=8)
ax3.grid(True, alpha=0.3)

# ──────────────────────────────────────────────────────────
# 4. Clamping Idempotence
# ──────────────────────────────────────────────────────────

def clamp(x, lo=0, hi=1):
    return np.maximum(lo, np.minimum(hi, x))

x_wide = np.linspace(-1, 2, 500)
clamp1 = clamp(x_wide)
clamp2 = clamp(clamp1)

ax4 = fig.add_subplot(gs[1, 0])
ax4.plot(x_wide, x_wide, '--', color='gray', alpha=0.5, label='identity')
ax4.plot(x_wide, clamp1, 'b-', linewidth=2.5, label='clamp(x)')
ax4.plot(x_wide, clamp2, 'r--', linewidth=2, label='clamp(clamp(x))')
ax4.axhline(y=0, color='k', linewidth=0.5, alpha=0.3)
ax4.axhline(y=1, color='k', linewidth=0.5, alpha=0.3)
ax4.fill_between(x_wide, 0, 1, alpha=0.05, color='green')
ax4.set_title('Clamping is Idempotent', fontsize=14, fontweight='bold')
ax4.set_xlabel('x')
ax4.set_ylabel('clamp(x)')
ax4.legend()
ax4.grid(True, alpha=0.3)

# ──────────────────────────────────────────────────────────
# 5. Image = Fixed Points for Finite Idempotent
# ──────────────────────────────────────────────────────────

# Define an idempotent function on {0,1,2,3,4,5}
# f maps: 0→0, 1→0, 2→2, 3→2, 4→4, 5→4
f_map = {0: 0, 1: 0, 2: 2, 3: 2, 4: 4, 5: 4}
domain = list(range(6))
image = sorted(set(f_map.values()))
fixed = [x for x in domain if f_map[x] == x]
non_fixed = [x for x in domain if f_map[x] != x]

ax5 = fig.add_subplot(gs[1, 1])
# Draw arrows
for x_val in domain:
    color = 'green' if x_val in fixed else 'red'
    ax5.annotate('', xy=(f_map[x_val], -0.5), xytext=(x_val, 0.5),
                arrowprops=dict(arrowstyle='->', color=color, linewidth=1.5, alpha=0.7))

# Draw points
for x_val in domain:
    color = 'green' if x_val in fixed else 'lightblue'
    ax5.scatter(x_val, 0.5, c=color, s=200, zorder=5, edgecolors='black')
    ax5.text(x_val, 0.6, str(x_val), ha='center', va='bottom', fontsize=12, fontweight='bold')

for y_val in domain:
    if y_val in image:
        ax5.scatter(y_val, -0.5, c='green', s=200, zorder=5, edgecolors='black')
    else:
        ax5.scatter(y_val, -0.5, c='lightgray', s=100, zorder=5, edgecolors='gray')
    ax5.text(y_val, -0.65, str(y_val), ha='center', va='top', fontsize=12)

ax5.text(-0.5, 0.5, 'Domain', ha='right', va='center', fontsize=11, style='italic')
ax5.text(-0.5, -0.5, 'Codomain', ha='right', va='center', fontsize=11, style='italic')
ax5.set_title(f'Image = Fixed Points\nImage: {image}, Fixed: {fixed}', fontsize=14, fontweight='bold')
ax5.set_xlim(-1, 6)
ax5.set_ylim(-1, 1)
ax5.axis('off')

# ──────────────────────────────────────────────────────────
# 6. Iteration Collapse
# ──────────────────────────────────────────────────────────

# Show how idempotent iteration collapses: ||f^n(x) - f(x)|| vs n
def random_idempotent_matrix(n, rank):
    """Create a random n×n idempotent matrix of given rank."""
    U = np.linalg.qr(np.random.randn(n, n))[0]
    D = np.diag([1]*rank + [0]*(n-rank))
    return U @ D @ U.T

np.random.seed(123)
P_mat = random_idempotent_matrix(10, 4)
x0 = np.random.randn(10)
fx = P_mat @ x0

errors = []
current = x0.copy()
for i in range(10):
    current = P_mat @ current
    errors.append(np.linalg.norm(current - fx))

ax6 = fig.add_subplot(gs[1, 2])
ax6.semilogy(range(1, 11), [max(e, 1e-16) for e in errors], 'bo-', linewidth=2, markersize=8)
ax6.set_title('Iteration Collapse\n‖P^n(x) − P(x)‖ vs n', fontsize=14, fontweight='bold')
ax6.set_xlabel('Number of applications n')
ax6.set_ylabel('‖Pⁿ(x) − P(x)‖')
ax6.set_ylim(1e-17, 1)
ax6.grid(True, alpha=0.3)
ax6.annotate('Collapses to 0\nafter first application',
            xy=(2, errors[1] if errors[1] > 0 else 1e-16),
            xytext=(4, 1e-5),
            arrowprops=dict(arrowstyle='->', color='red'),
            fontsize=10, color='red')

plt.suptitle('The Idempotent Collapse Principle: f(f(x)) = f(x)', fontsize=16, fontweight='bold', y=0.98)
plt.savefig('/workspace/request-project/CrossCutting/demos/idempotent_demo.png', dpi=150, bbox_inches='tight')
plt.close()

print("✓ Idempotent demo saved to idempotent_demo.png")

# ──────────────────────────────────────────────────────────
# Verification: Check idempotence numerically
# ──────────────────────────────────────────────────────────
print("\n=== Numerical Verification ===")
print(f"ReLU idempotent: max error = {np.max(np.abs(relu2 - relu1)):.2e}")
print(f"Projection idempotent: max error = {np.max(np.abs(proj2 - proj1)):.2e}")
print(f"Clamp idempotent: max error = {np.max(np.abs(clamp2 - clamp1)):.2e}")
print(f"P² = P matrix error: {np.max(np.abs(P @ P - P)):.2e}")
print(f"Image = Fixed points: {set(image) == set(fixed)}")
print(f"Iteration collapse error: {errors[-1]:.2e}")

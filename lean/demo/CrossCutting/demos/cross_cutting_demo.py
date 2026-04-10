#!/usr/bin/env python3
"""
Cross-Cutting Connections Demo

Demonstrates the interconnections between all three themes:
1. Berggren tree visualization with growth properties
2. ReLU as tropical-idempotent bridge
3. Retraction → Idempotent connection
4. Pythagorean-tropical bounds
5. Convergence via idempotent limit
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib.patches as mpatches

# ──────────────────────────────────────────────────────────
# Berggren tree
# ──────────────────────────────────────────────────────────

def berggren_M1(a, b, c):
    return (a - 2*b + 2*c, 2*a - b + 2*c, 2*a - 2*b + 3*c)

def berggren_M2(a, b, c):
    return (a + 2*b + 2*c, 2*a + b + 2*c, 2*a + 2*b + 3*c)

def berggren_M3(a, b, c):
    return (-a + 2*b + 2*c, -2*a + b + 2*c, -2*a + 2*b + 3*c)

def build_berggren_tree(depth=3):
    """Build the Berggren tree to given depth."""
    root = (3, 4, 5)
    tree = {(): root}
    queue = [((), root)]
    
    for _ in range(depth):
        new_queue = []
        for path, triple in queue:
            a, b, c = triple
            for i, transform in enumerate([berggren_M1, berggren_M2, berggren_M3]):
                new_path = path + (i,)
                new_triple = transform(a, b, c)
                tree[new_path] = new_triple
                new_queue.append((new_path, new_triple))
        queue = new_queue
    
    return tree

fig = plt.figure(figsize=(20, 16))
gs = GridSpec(2, 3, figure=fig, hspace=0.35, wspace=0.3)

# ──────────────────────────────────────────────────────────
# 1. Berggren Tree Visualization
# ──────────────────────────────────────────────────────────

tree = build_berggren_tree(3)

ax1 = fig.add_subplot(gs[0, 0])

# Position nodes
positions = {}
positions[()] = (0.5, 1.0)

def get_children_positions(parent_pos, depth, width=0.4):
    x, y = parent_pos
    dy = 0.25
    dx = width / (2 ** depth)
    return [(x - dx, y - dy), (x, y - dy), (x + dx, y - dy)]

for depth in range(3):
    for path, triple in tree.items():
        if len(path) == depth:
            pos = positions[path]
            children = get_children_positions(pos, depth)
            for i, child_pos in enumerate(children):
                child_path = path + (i,)
                if child_path in tree:
                    positions[child_path] = child_pos

# Draw edges and nodes
colors_map = {0: '#ff6b6b', 1: '#2ed573', 2: '#1e90ff'}
labels = {0: 'M₁', 1: 'M₂', 2: 'M₃'}

for path, triple in tree.items():
    if len(path) > 0:
        parent_path = path[:-1]
        px, py = positions[parent_path]
        cx, cy = positions[path]
        ax1.plot([px, cx], [py, cy], '-', color=colors_map[path[-1]], linewidth=1.5, alpha=0.6)

for path, triple in tree.items():
    x, y = positions[path]
    a, b, c = triple
    ax1.scatter(x, y, c='white', s=800, zorder=5, edgecolors='black', linewidth=1.5)
    ax1.text(x, y, f'({a},{b},{c})', ha='center', va='center', fontsize=5.5, fontweight='bold')

# Legend
patches = [mpatches.Patch(color=colors_map[i], label=labels[i]) for i in range(3)]
ax1.legend(handles=patches, loc='lower left', fontsize=8)
ax1.set_title('Berggren Pythagorean Tree', fontsize=14, fontweight='bold')
ax1.set_xlim(-0.1, 1.1)
ax1.set_ylim(-0.1, 1.1)
ax1.axis('off')

# ──────────────────────────────────────────────────────────
# 2. Hypotenuse Growth
# ──────────────────────────────────────────────────────────

ax2 = fig.add_subplot(gs[0, 1])

# Track hypotenuse along several paths
paths_to_trace = [
    [(3,4,5)],
    [(3,4,5)],
    [(3,4,5)],
]
transforms = [berggren_M1, berggren_M2, berggren_M3]
transform_names = ['M₁ path', 'M₂ path', 'M₃ path']
colors_line = ['#ff6b6b', '#2ed573', '#1e90ff']

for idx in range(3):
    hyp_path = [5]
    current = (3, 4, 5)
    for _ in range(6):
        current = transforms[idx](*current)
        hyp_path.append(current[2])
    ax2.semilogy(range(len(hyp_path)), hyp_path, 'o-', color=colors_line[idx],
                linewidth=2, markersize=6, label=transform_names[idx])

ax2.set_title('Hypotenuse Strictly Increases', fontsize=14, fontweight='bold')
ax2.set_xlabel('Tree depth')
ax2.set_ylabel('Hypotenuse c (log scale)')
ax2.legend()
ax2.grid(True, alpha=0.3)

# ──────────────────────────────────────────────────────────
# 3. Quadratic Form Invariance
# ──────────────────────────────────────────────────────────

ax3 = fig.add_subplot(gs[0, 2])

# For every triple in the tree, compute a² + b² - c²
depths = []
quad_forms = []
for path, (a, b, c) in tree.items():
    depths.append(len(path))
    quad_forms.append(a**2 + b**2 - c**2)

ax3.scatter(depths, quad_forms, c='blue', s=50, alpha=0.7)
ax3.axhline(y=0, color='red', linewidth=2, linestyle='--', label='Q = 0 (Pythagorean)')
ax3.set_title('Quadratic Form a² + b² − c² = 0\n(Invariant under all Berggren matrices)', fontsize=14, fontweight='bold')
ax3.set_xlabel('Tree depth')
ax3.set_ylabel('a² + b² − c²')
ax3.legend()
ax3.grid(True, alpha=0.3)
ax3.set_ylim(-1, 1)

# ──────────────────────────────────────────────────────────
# 4. Pythagorean-Tropical Bounds
# ──────────────────────────────────────────────────────────

ax4 = fig.add_subplot(gs[1, 0])

# For each tree triple, show max(a², b²) ≤ c² ≤ 2·max(a², b²)
triples = list(tree.values())
a_sq = [t[0]**2 for t in triples]
b_sq = [t[1]**2 for t in triples]
c_sq = [t[2]**2 for t in triples]
max_ab = [max(a, b) for a, b in zip(a_sq, b_sq)]

sorted_idx = np.argsort(c_sq)
c_sq_sorted = [c_sq[i] for i in sorted_idx]
max_ab_sorted = [max_ab[i] for i in sorted_idx]

x_range = range(len(triples))
ax4.fill_between(x_range, max_ab_sorted, [2*m for m in max_ab_sorted],
                alpha=0.2, color='green', label='Tropical bounds')
ax4.plot(x_range, c_sq_sorted, 'ro', markersize=5, label='c²')
ax4.plot(x_range, max_ab_sorted, 'b-', linewidth=1, alpha=0.5, label='max(a², b²)')
ax4.plot(x_range, [2*m for m in max_ab_sorted], 'g-', linewidth=1, alpha=0.5, label='2·max(a², b²)')
ax4.set_title('Tropical Bound on Pythagorean Triples\nmax(a², b²) ≤ c² ≤ 2·max(a², b²)', fontsize=14, fontweight='bold')
ax4.set_xlabel('Triple index (sorted by c²)')
ax4.set_ylabel('Value')
ax4.legend(fontsize=8)
ax4.grid(True, alpha=0.3)

# ──────────────────────────────────────────────────────────
# 5. Retraction → Idempotent
# ──────────────────────────────────────────────────────────

ax5 = fig.add_subplot(gs[1, 1])

# Visualize retraction: R² → line y=x → R² and the resulting idempotent
theta = np.pi/4
proj_mat = np.array([[np.cos(theta)**2, np.cos(theta)*np.sin(theta)],
                     [np.cos(theta)*np.sin(theta), np.sin(theta)**2]])

# The retraction: project onto line, embed back
np.random.seed(7)
test_points = np.random.randn(30, 2) * 1.5
projected = (proj_mat @ test_points.T).T
proj2 = (proj_mat @ projected.T).T

# Show the cycle
ax5.scatter(test_points[:, 0], test_points[:, 1], c='blue', s=40, alpha=0.3, label='x')
ax5.scatter(projected[:, 0], projected[:, 1], c='red', s=40, alpha=0.7, label='i∘r(x)')
ax5.scatter(proj2[:, 0], proj2[:, 1], c='green', marker='x', s=60, alpha=0.9, label='(i∘r)²(x)')

for i in range(30):
    ax5.annotate('', xy=projected[i], xytext=test_points[i],
                arrowprops=dict(arrowstyle='->', color='gray', alpha=0.2))

ax5.plot([-3, 3], [-3, 3], 'k--', alpha=0.3)
ax5.set_title('Retraction → Idempotent\nr∘i = id ⟹ (i∘r)² = i∘r', fontsize=14, fontweight='bold')
ax5.set_xlabel('x₁')
ax5.set_ylabel('x₂')
ax5.legend(fontsize=8)
ax5.set_aspect('equal')
ax5.grid(True, alpha=0.3)
ax5.set_xlim(-4, 4)
ax5.set_ylim(-4, 4)

# ──────────────────────────────────────────────────────────
# 6. Cross-Cutting Summary Diagram
# ──────────────────────────────────────────────────────────

ax6 = fig.add_subplot(gs[1, 2])
ax6.axis('off')

# Draw the triangle
triangle = plt.Polygon([(0.5, 0.9), (0.1, 0.15), (0.9, 0.15)],
                       fill=False, edgecolor='black', linewidth=2)
ax6.add_patch(triangle)

# Vertices
ax6.text(0.5, 0.93, 'Idempotent\nCollapse', ha='center', va='bottom',
        fontsize=12, fontweight='bold', color='#e74c3c',
        bbox=dict(boxstyle='round', facecolor='#ffebee', edgecolor='#e74c3c'))
ax6.text(0.05, 0.08, 'Tropical\nAlgebra', ha='center', va='top',
        fontsize=12, fontweight='bold', color='#2196f3',
        bbox=dict(boxstyle='round', facecolor='#e3f2fd', edgecolor='#2196f3'))
ax6.text(0.95, 0.08, 'Quantum/\nSmooth', ha='center', va='top',
        fontsize=12, fontweight='bold', color='#4caf50',
        bbox=dict(boxstyle='round', facecolor='#e8f5e9', edgecolor='#4caf50'))

# Edge labels
ax6.text(0.25, 0.55, 'max(x,x)=x\nReLU²=ReLU', ha='center', va='center',
        fontsize=8, style='italic', rotation=55)
ax6.text(0.75, 0.55, 'P²=P\nMeasurement', ha='center', va='center',
        fontsize=8, style='italic', rotation=-55)
ax6.text(0.5, 0.12, 'LSE_ε → max\nas ε → 0', ha='center', va='center',
        fontsize=8, style='italic')

# Center
ax6.text(0.5, 0.45, 'Berggren\nTree', ha='center', va='center',
        fontsize=11, fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='#fff3e0', edgecolor='#ff9800'))

ax6.set_title('Cross-Cutting Connections', fontsize=14, fontweight='bold')
ax6.set_xlim(-0.1, 1.1)
ax6.set_ylim(-0.05, 1.1)

plt.suptitle('Cross-Cutting Themes: Connections and Applications', fontsize=16, fontweight='bold', y=0.98)
plt.savefig('/workspace/request-project/CrossCutting/demos/cross_cutting_demo.png', dpi=150, bbox_inches='tight')
plt.close()

print("✓ Cross-cutting connections demo saved to cross_cutting_demo.png")

# ──────────────────────────────────────────────────────────
# Print Berggren tree data
# ──────────────────────────────────────────────────────────
print("\n=== Berggren Tree (depth 2) ===")
for path, (a, b, c) in sorted(tree.items(), key=lambda x: len(x[0])):
    if len(path) <= 2:
        path_str = ''.join(['M₁M₂M₃'[i*2:i*2+2] for i in path]) if path else 'root'
        verify = a**2 + b**2 == c**2
        print(f"  {path_str:10s} → ({a:4d}, {b:4d}, {c:4d})  a²+b²=c²: {verify}  Q={a**2+b**2-c**2}")

# Verify tropical bounds
print("\n=== Tropical Bounds on Pythagorean Triples ===")
for _, (a, b, c) in list(tree.items())[:5]:
    max_sq = max(a**2, b**2)
    print(f"  ({a},{b},{c}): max(a²,b²)={max_sq} ≤ c²={c**2} ≤ 2·max={2*max_sq}: "
          f"{max_sq <= c**2 <= 2*max_sq}")

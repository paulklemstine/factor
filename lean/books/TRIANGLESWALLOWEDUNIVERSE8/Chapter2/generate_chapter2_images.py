#!/usr/bin/env python3
"""Generate all illustrations for Chapter 2: The Tree That Grew Into a Lattice."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe
import numpy as np
import os
from math import gcd

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
os.makedirs(OUT, exist_ok=True)

# Color palette (matching Chapter 1 style)
SAND = '#F5E6C8'
DARK = '#2C1810'
ACCENT1 = '#C0392B'  # red
ACCENT2 = '#2980B9'  # blue
ACCENT3 = '#27AE60'  # green
ACCENT4 = '#8E44AD'  # purple
ACCENT5 = '#E67E22'  # orange
GOLD = '#D4A017'
LIGHT_BLUE = '#AED6F1'
LIGHT_GREEN = '#ABEBC6'
LIGHT_RED = '#F5B7B1'
CREAM = '#FDF2E9'
SLATE = '#34495E'
GLOW = '#F4D03F'

def save(fig, name, dpi=200):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=dpi, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  Saved {name}")


# ============================================================
# ILLUSTRATION 1: Binary tree of (m,n) pairs — the factory tree
# ============================================================
def fig01_factory_tree():
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    def triple(m, n):
        return (m*m - n*n, 2*m*n, m*m + n*n)

    nodes = {
        (0, 0): (2, 1),
        (1, 0): (3, 2),
        (1, 1): (4, 1),
        (2, 0): (4, 3),
        (2, 1): (7, 2),
        (2, 2): (7, 4),
        (2, 3): (6, 1),
    }

    positions = {
        (0, 0): (8, 9),
        (1, 0): (4, 6),
        (1, 1): (12, 6),
        (2, 0): (2, 3),
        (2, 1): (6, 3),
        (2, 2): (10, 3),
        (2, 3): (14, 3),
    }

    edges = [
        ((0, 0), (1, 0), '$\\mathbf{M}_1$'),
        ((0, 0), (1, 1), '$\\mathbf{M}_3$'),
        ((1, 0), (2, 0), '$\\mathbf{M}_1$'),
        ((1, 0), (2, 1), '$\\mathbf{M}_3$'),
        ((1, 1), (2, 2), '$\\mathbf{M}_1$'),
        ((1, 1), (2, 3), '$\\mathbf{M}_3$'),
    ]

    # Draw edges
    for parent, child, label in edges:
        px, py = positions[parent]
        cx, cy = positions[child]
        ax.annotate('', xy=(cx, cy + 0.6), xytext=(px, py - 0.6),
                    arrowprops=dict(arrowstyle='->', color=SLATE, lw=2))
        mx, my = (px + cx) / 2, (py + cy) / 2
        side = -0.7 if child[1] % 2 == 0 else 0.7
        ax.text(mx + side, my + 0.15, label, fontsize=11, ha='center', va='center',
                color=ACCENT4, fontweight='bold')

    # Draw nodes
    for key, (m, n) in nodes.items():
        x, y = positions[key]
        a, b, c = triple(m, n)
        box = FancyBboxPatch((x - 1.3, y - 0.5), 2.6, 1.0,
                             boxstyle="round,pad=0.15", facecolor=CREAM,
                             edgecolor=DARK, linewidth=2)
        ax.add_patch(box)
        ax.text(x, y + 0.1, f'$({m}, {n})$', fontsize=14, ha='center', va='center',
                color=DARK, fontweight='bold')
        ax.text(x, y - 0.9, f'$({a},\\, {b},\\, {c})$', fontsize=11, ha='center',
                va='center', color=ACCENT2)

    ax.set_xlim(-0.5, 16.5)
    ax.set_ylim(1.0, 10.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('The Pythagorean Triple Factory Tree', fontsize=20,
                 fontweight='bold', color=DARK, pad=20)
    save(fig, "fig01_factory_tree.png")


# ============================================================
# ILLUSTRATION 2: SL(2,Z) lattice shearing
# ============================================================
def fig02_lattice_shear():
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.set_facecolor(SAND)

    for ax in axes:
        ax.set_facecolor(SAND)
        ax.set_aspect('equal')
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.set_xticks([])
        ax.set_yticks([])

    # Left: original unit square on Z^2
    ax = axes[0]
    ax.set_title('Original Lattice', fontsize=16, fontweight='bold', color=DARK, pad=10)
    for i in range(5):
        for j in range(5):
            ax.plot(i, j, 'o', color=DARK, markersize=7, zorder=5)
    sq_x = [0, 1, 1, 0, 0]
    sq_y = [0, 0, 1, 1, 0]
    ax.fill(sq_x, sq_y, alpha=0.3, color=ACCENT2)
    ax.plot(sq_x, sq_y, color=ACCENT2, linewidth=2.5)
    ax.text(0.5, 0.5, 'Area = 1', fontsize=13, ha='center', va='center',
            color=DARK, fontweight='bold')
    ax.annotate('', xy=(1, 0), xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=2.5))
    ax.annotate('', xy=(0, 1), xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', color=ACCENT3, lw=2.5))
    ax.text(0.5, -0.3, '$\\mathbf{e}_1$', fontsize=14, ha='center', color=ACCENT1, fontweight='bold')
    ax.text(-0.35, 0.5, '$\\mathbf{e}_2$', fontsize=14, ha='center', color=ACCENT3, fontweight='bold')
    ax.set_xlim(-0.7, 4.5)
    ax.set_ylim(-0.7, 4.5)

    # Right: sheared by M3 = [[1, 2], [0, 1]]
    ax = axes[1]
    M = np.array([[1, 2], [0, 1]])
    ax.set_title('After $\\mathbf{M}_3$ Shear', fontsize=16, fontweight='bold', color=DARK, pad=10)
    for i in range(5):
        for j in range(5):
            v = M @ np.array([i, j])
            if v[0] <= 10 and v[1] <= 5:
                ax.plot(v[0], v[1], 'o', color=DARK, markersize=7, zorder=5)
    corners = np.array([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]])
    transformed = (M @ corners.T).T
    ax.fill(transformed[:, 0], transformed[:, 1], alpha=0.3, color=ACCENT5)
    ax.plot(transformed[:, 0], transformed[:, 1], color=ACCENT5, linewidth=2.5)
    cx = np.mean(transformed[:4, 0])
    cy = np.mean(transformed[:4, 1])
    ax.text(cx, cy, 'Area = 1', fontsize=13, ha='center', va='center',
            color=DARK, fontweight='bold')
    v1 = M @ np.array([1, 0])
    v2 = M @ np.array([0, 1])
    ax.annotate('', xy=v1, xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=2.5))
    ax.annotate('', xy=v2, xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', color=ACCENT3, lw=2.5))
    ax.text(v1[0]/2, v1[1]/2 - 0.35, "$\\mathbf{M}_3 \\mathbf{e}_1$", fontsize=13,
            ha='center', color=ACCENT1, fontweight='bold')
    ax.text(v2[0]/2 - 0.5, v2[1]/2 + 0.2, "$\\mathbf{M}_3 \\mathbf{e}_2$", fontsize=13,
            ha='center', color=ACCENT3, fontweight='bold')
    ax.set_xlim(-0.7, 10)
    ax.set_ylim(-0.7, 4.5)

    fig.text(0.5, 0.02, 'A transformation in SL(2, ℤ) reshapes but never tears the lattice.',
             fontsize=14, ha='center', color=DARK, fontstyle='italic')
    fig.tight_layout(rect=[0, 0.06, 1, 0.95])
    save(fig, "fig02_lattice_shear.png")


# ============================================================
# ILLUSTRATION 3: Euclidean algorithm descent staircase (17, 5)
# ============================================================
def fig03_euclid_staircase():
    fig, axes = plt.subplots(1, 2, figsize=(16, 9))
    fig.set_facecolor(SAND)

    # Left: rectangle peeling
    ax = axes[0]
    ax.set_facecolor(SAND)
    ax.set_title('Euclidean Algorithm: gcd(17, 5)', fontsize=16, fontweight='bold', color=DARK, pad=10)

    steps = [(17, 5, 3, 2), (5, 2, 2, 1), (2, 1, 2, 0)]
    colors = [ACCENT2, ACCENT3, ACCENT5]

    scale = 0.4
    for i, (a, b, q, r) in enumerate(steps):
        y = 8 - i * 3
        rect_w = a * scale
        rect_h = b * scale
        ax.add_patch(patches.Rectangle((0.5, y - rect_h), rect_w, rect_h,
                                        facecolor=CREAM, edgecolor=DARK, linewidth=1.5))
        for j in range(q):
            ax.add_patch(patches.Rectangle((0.5 + j * b * scale, y - rect_h),
                                           b * scale, rect_h,
                                           facecolor=colors[i], alpha=0.3,
                                           edgecolor=DARK, linewidth=1))
        if r > 0:
            ax.add_patch(patches.Rectangle((0.5 + q * b * scale, y - rect_h),
                                           r * scale, rect_h,
                                           facecolor=LIGHT_RED, alpha=0.5,
                                           edgecolor=ACCENT1, linewidth=1.5, linestyle='--'))
        ax.text(0.5 + rect_w / 2, y + 0.2, f'{a} = {q} × {b} + {r}',
                fontsize=13, ha='center', va='bottom', color=DARK, fontweight='bold')
        ax.text(0.5 + rect_w + 0.3, y - rect_h / 2, f'q = {q}',
                fontsize=12, ha='left', va='center', color=colors[i], fontweight='bold')

    ax.set_xlim(-0.5, 10)
    ax.set_ylim(-1, 10)
    ax.set_aspect('equal')
    ax.axis('off')

    # Right: corresponding matrices
    ax = axes[1]
    ax.set_facecolor(SAND)
    ax.set_title('Quotient Matrices', fontsize=16, fontweight='bold', color=DARK, pad=10)

    matrices = [
        (3, 'Q(3) = [ [0, 1], [1, -3] ]'),
        (2, 'Q(2) = [ [0, 1], [1, -2] ]'),
        (2, 'Q(2) = [ [0, 1], [1, -2] ]'),
    ]

    for i, (q, mat_str) in enumerate(matrices):
        y = 8 - i * 3
        ax.text(1, y, f'Step {i+1}:', fontsize=14, ha='left', va='center',
                color=DARK, fontweight='bold')
        ax.text(1, y - 1.0, mat_str, fontsize=15, ha='left', va='center',
                color=colors[i])
        if i < len(matrices) - 1:
            ax.annotate('', xy=(3, y - 1.8), xytext=(3, y - 1.5),
                        arrowprops=dict(arrowstyle='->', color=SLATE, lw=1.5))

    ax.text(3, 0.5, 'gcd(17, 5) = 1  ✓', fontsize=15, ha='center', va='center',
            color=ACCENT1, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=LIGHT_RED, edgecolor=ACCENT1))

    ax.set_xlim(0, 8)
    ax.set_ylim(-0.5, 10)
    ax.axis('off')

    fig.tight_layout()
    save(fig, "fig03_euclid_staircase.png")


# ============================================================
# ILLUSTRATION 4: Split-screen — tree descent vs Euclidean algorithm
# ============================================================
def fig04_tree_vs_euclid():
    fig, axes = plt.subplots(1, 2, figsize=(16, 10))
    fig.set_facecolor(SAND)

    # Left: tree descent from (7,2) back to (2,1)
    ax = axes[0]
    ax.set_facecolor(SAND)
    ax.set_title('Tree Descent: $(7,2) \\to (2,1)$', fontsize=16, fontweight='bold', color=DARK, pad=10)

    path_nodes = [(7, 2), (3, 2), (2, 1)]
    inv_labels = ['$\\mathbf{M}_3^{-1}$', '$\\mathbf{M}_1^{-1}$']
    path_colors = [ACCENT5, ACCENT2, ACCENT3]

    for i, (m, n) in enumerate(path_nodes):
        y = 8 - i * 3
        x = 4
        box = FancyBboxPatch((x - 1.2, y - 0.5), 2.4, 1.0,
                             boxstyle="round,pad=0.15", facecolor=CREAM,
                             edgecolor=path_colors[i], linewidth=2.5)
        ax.add_patch(box)
        ax.text(x, y, f'$({m}, {n})$', fontsize=16, ha='center', va='center',
                color=DARK, fontweight='bold')
        if i < len(inv_labels):
            ax.annotate('', xy=(x, y - 0.6), xytext=(x, y - 2.3),
                        arrowprops=dict(arrowstyle='<-', color=path_colors[i+1], lw=2.5))
            ax.text(x + 1.5, y - 1.5, inv_labels[i], fontsize=14, ha='left', va='center',
                    color=path_colors[i+1], fontweight='bold')

    ax.text(4, 1.2, 'Root reached!', fontsize=13, ha='center', color=ACCENT3, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=LIGHT_GREEN, edgecolor=ACCENT3))

    ax.set_xlim(0, 8)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Right: Euclidean algorithm on m=7, n=2
    ax = axes[1]
    ax.set_facecolor(SAND)
    ax.set_title('Euclidean Algorithm: $m=7, n=2$', fontsize=16, fontweight='bold', color=DARK, pad=10)

    euclid_steps = [
        ('$7 = 3 \\times 2 + 1$',),
        ('$2 = 2 \\times 1 + 0$',),
    ]
    euclid_colors = [ACCENT5, ACCENT2]

    for i, (text,) in enumerate(euclid_steps):
        y = 8 - i * 3
        x = 4
        box = FancyBboxPatch((x - 2.5, y - 0.5), 5.0, 1.0,
                             boxstyle="round,pad=0.15", facecolor=CREAM,
                             edgecolor=euclid_colors[i], linewidth=2.5)
        ax.add_patch(box)
        ax.text(x, y, text, fontsize=15, ha='center', va='center',
                color=DARK, fontweight='bold')
        if i < len(euclid_steps) - 1:
            ax.annotate('', xy=(x, y - 0.6), xytext=(x, y - 2.3),
                        arrowprops=dict(arrowstyle='->', color=euclid_colors[i+1], lw=2.5))

    ax.text(4, 3.5, 'gcd = 1  ✓', fontsize=13, ha='center', color=ACCENT3, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=LIGHT_GREEN, edgecolor=ACCENT3))

    ax.set_xlim(0, 8)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Banner across the middle
    fig.text(0.5, 0.03, 'Same computation.  Different disguise.',
             fontsize=18, ha='center', va='center', color=DARK, fontweight='bold',
             fontstyle='italic',
             bbox=dict(boxstyle='round,pad=0.4', facecolor=GLOW, edgecolor=GOLD, linewidth=2))

    # Connecting arrows between sides
    for i, color in enumerate(euclid_colors):
        y_norm = 0.78 - i * 0.28
        arrow = FancyArrowPatch(
            (0.45, y_norm), (0.55, y_norm),
            transform=fig.transFigure,
            arrowstyle='<->', color=color, lw=2.5,
            mutation_scale=20
        )
        fig.add_artist(arrow)

    fig.tight_layout(rect=[0, 0.07, 1, 0.95])
    save(fig, "fig04_tree_vs_euclid.png")


# ============================================================
# ILLUSTRATION 5: Complexity comparison graph
# ============================================================
def fig05_complexity_graph():
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    fig.set_facecolor(SAND)
    ax.set_facecolor(CREAM)

    N = np.logspace(1, 12, 500)

    y_linear = N
    y_sqrt = np.sqrt(N)
    c = 1.5
    y_subexp = np.exp(c * np.log(N)**(1/3) * np.log(np.log(N + 1) + 1)**(2/3))

    ax.loglog(N, y_linear, color=ACCENT1, linewidth=3, label='Trying every number: $N$')
    ax.loglog(N, y_sqrt, color=ACCENT5, linewidth=3, label='Trial division / tree descent: $\\sqrt{N}$')
    ax.loglog(N, y_subexp, color=ACCENT3, linewidth=3,
              label='Modern algorithms: $e^{c(\\ln N)^{1/3}(\\ln\\ln N)^{2/3}}$')

    ax.fill_between(N, y_subexp, y_sqrt, alpha=0.15, color=ACCENT4)
    ax.text(1e8, 2e2, 'The Escape Route', fontsize=16, ha='center', va='center',
            color=ACCENT4, fontweight='bold', fontstyle='italic', rotation=5)

    ax.set_xlabel('$N$', fontsize=16, color=DARK)
    ax.set_ylabel('Number of steps', fontsize=16, color=DARK)
    ax.set_title('The Three Regimes of Factoring', fontsize=20,
                 fontweight='bold', color=DARK, pad=15)
    ax.legend(fontsize=13, loc='upper left', framealpha=0.9, facecolor=CREAM)

    ax.grid(True, alpha=0.3)
    ax.tick_params(colors=DARK)
    save(fig, "fig05_complexity_graph.png")


# ============================================================
# ILLUSTRATION 6: Gauss 2D lattice reduction
# ============================================================
def fig06_gauss_reduction():
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    # Start with a skewed basis
    v1_orig = np.array([5.0, 1.0])
    v2_orig = np.array([2.0, 3.0])

    # Gauss reduction steps
    def gauss_reduce(v1, v2):
        steps = [(v1.copy(), v2.copy())]
        for _ in range(20):
            if np.linalg.norm(v1) < np.linalg.norm(v2):
                v1, v2 = v2, v1
            mu = round(np.dot(v1, v2) / np.dot(v2, v2))
            if mu == 0:
                break
            v1 = v1 - mu * v2
            steps.append((v1.copy(), v2.copy()))
        return steps

    steps = gauss_reduce(v1_orig.copy(), v2_orig.copy())

    # Draw lattice points using original basis
    for i in range(-5, 6):
        for j in range(-5, 6):
            pt = i * v1_orig + j * v2_orig
            if abs(pt[0]) < 12 and abs(pt[1]) < 12:
                ax.plot(pt[0], pt[1], 'o', color=SLATE, markersize=5, alpha=0.5, zorder=3)

    # Draw reduction steps with fading colors
    n_steps = len(steps)
    for idx, (v1, v2) in enumerate(steps):
        alpha = 0.15 + 0.85 * (idx / max(n_steps - 1, 1))
        lw = 1.5 if idx < n_steps - 1 else 3.5
        ax.annotate('', xy=v1, xytext=(0, 0),
                    arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=lw, alpha=alpha))
        ax.annotate('', xy=v2, xytext=(0, 0),
                    arrowprops=dict(arrowstyle='->', color=ACCENT2, lw=lw, alpha=alpha))
        if idx < n_steps - 1:
            ax.text(v1[0] + 0.15, v1[1] + 0.15, f'step {idx}', fontsize=9,
                    color=ACCENT1, alpha=alpha * 0.8)

    # Highlight the final shortest vector
    final_v1, final_v2 = steps[-1]
    sv = final_v2 if np.linalg.norm(final_v2) <= np.linalg.norm(final_v1) else final_v1
    ax.text(sv[0] + 0.3, sv[1] + 0.3, 'Shortest\nvector', fontsize=13,
            color=ACCENT1, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=LIGHT_RED, edgecolor=ACCENT1))

    # Original basis labels
    ax.text(v1_orig[0] + 0.2, v1_orig[1] - 0.4, '$\\mathbf{v}_1$', fontsize=15,
            color=ACCENT1, fontweight='bold', alpha=0.4)
    ax.text(v2_orig[0] + 0.2, v2_orig[1] + 0.2, '$\\mathbf{v}_2$', fontsize=15,
            color=ACCENT2, fontweight='bold', alpha=0.4)

    ax.plot(0, 0, 'o', color=DARK, markersize=10, zorder=10)
    ax.set_xlim(-8, 10)
    ax.set_ylim(-6, 8)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.15)
    ax.axis('off')
    ax.set_title('Gauss 2D Lattice Reduction', fontsize=20,
                 fontweight='bold', color=DARK, pad=15)
    save(fig, "fig06_gauss_reduction.png")


# ============================================================
# ILLUSTRATION 7: The 2D barrier — cliff edge
# ============================================================
def fig07_2d_barrier():
    fig, ax = plt.subplots(1, 1, figsize=(14, 9))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    # Flat 2D plane on top
    plane_y = 6.0
    ax.fill_between([0, 14], plane_y, 9, color=CREAM, alpha=0.8)
    ax.plot([0, 14], [plane_y, plane_y], color=DARK, linewidth=3)

    # Grid on the 2D plane
    for x in np.arange(0.5, 14, 0.8):
        ax.plot([x, x], [plane_y, 9], color=SLATE, linewidth=0.5, alpha=0.3)
    for y in np.arange(plane_y + 0.5, 9, 0.5):
        ax.plot([0, 14], [y, y], color=SLATE, linewidth=0.5, alpha=0.3)

    ax.text(3, 8, '2D Lattice World', fontsize=16, ha='center', va='center',
            color=DARK, fontweight='bold')

    # Cliff face
    cliff_x = np.linspace(0, 14, 100)
    ax.fill_between(cliff_x, 0.5, plane_y, color='#8B7355', alpha=0.4)
    for y_line in np.arange(1, plane_y, 0.7):
        rng = np.random.RandomState(int(y_line * 10))
        noise = rng.rand(100) * 0.3
        ax.plot(cliff_x, y_line + noise * 0.2, color=DARK, alpha=0.15, linewidth=0.5)

    # 3D lattice below (glowing dots)
    rng = np.random.RandomState(42)
    for _ in range(80):
        x = rng.uniform(1, 13)
        y = rng.uniform(0.5, plane_y - 0.5)
        size = rng.uniform(3, 8)
        ax.plot(x, y, 'o', color=GLOW, markersize=size, alpha=0.6, zorder=5)
        ax.plot(x, y, 'o', color=ACCENT5, markersize=size * 0.6, alpha=0.8, zorder=6)

    # 3D connections (lattice structure)
    pts_3d = [(2, 3), (4, 2), (6, 4), (8, 1.5), (10, 3.5), (12, 2.5),
              (3, 5), (7, 2.5), (11, 4.5), (5, 1)]
    for i in range(len(pts_3d)):
        for j in range(i + 1, len(pts_3d)):
            d = np.sqrt((pts_3d[i][0] - pts_3d[j][0])**2 + (pts_3d[i][1] - pts_3d[j][1])**2)
            if d < 3.5:
                ax.plot([pts_3d[i][0], pts_3d[j][0]], [pts_3d[i][1], pts_3d[j][1]],
                        color=GLOW, alpha=0.3, linewidth=1)

    ax.text(7, 3, '$d \\geq 3$ Lattice Space', fontsize=16, ha='center', va='center',
            color=GOLD, fontweight='bold',
            path_effects=[pe.withStroke(linewidth=3, foreground=DARK)])

    # Tiny figure at the edge
    fig_x = 10
    fig_y = plane_y
    ax.plot([fig_x, fig_x], [fig_y, fig_y + 0.8], color=DARK, linewidth=2.5)
    ax.plot(fig_x, fig_y + 1.0, 'o', color=DARK, markersize=8)
    ax.plot([fig_x - 0.3, fig_x, fig_x + 0.2], [fig_y + 0.4, fig_y + 0.6, fig_y + 0.3],
            color=DARK, linewidth=2)
    ax.plot([fig_x - 0.2, fig_x], [fig_y, fig_y + 0.3], color=DARK, linewidth=2)
    ax.plot([fig_x + 0.15, fig_x], [fig_y, fig_y + 0.3], color=DARK, linewidth=2)

    ax.text(7, plane_y - 0.3, '$\\Theta(\\sqrt{N})$ barrier', fontsize=14,
            ha='center', va='top', color=ACCENT1, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.2', facecolor=LIGHT_RED, edgecolor=ACCENT1, alpha=0.8))

    ax.text(7, -0.3, 'The view from the two-dimensional barrier.',
            fontsize=14, ha='center', va='center', color=DARK, fontstyle='italic')

    ax.set_xlim(-0.5, 14.5)
    ax.set_ylim(-0.7, 9.5)
    ax.set_aspect('auto')
    ax.axis('off')
    ax.set_title('Beyond Two Dimensions', fontsize=20,
                 fontweight='bold', color=DARK, pad=15)
    save(fig, "fig07_2d_barrier.png")


# ============================================================
# ILLUSTRATION 8: LLL approximation — 3D lattice with SVP
# ============================================================
def fig08_lll_bargain():
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    # Generate a 3D lattice
    basis = np.array([[3, 1, 0], [1, 3, 1], [0, 1, 3]])
    points = []
    for i in range(-3, 4):
        for j in range(-3, 4):
            for k in range(-3, 4):
                pt = i * basis[0] + j * basis[1] + k * basis[2]
                if np.linalg.norm(pt) < 12:
                    points.append(pt)
    points = np.array(points)

    ax.scatter(points[:, 0], points[:, 1], points[:, 2],
               c=SLATE, s=15, alpha=0.4, depthshade=True)

    # True shortest vector
    norms = np.array([np.linalg.norm(p) for p in points])
    nonzero = norms > 0.1
    shortest_idx = np.argmin(norms[nonzero])
    sv = points[nonzero][shortest_idx]
    sv_norm = np.linalg.norm(sv)

    # LLL approximate vector (pick one ~1.8x longer)
    candidates = points[nonzero]
    cand_norms = np.array([np.linalg.norm(c) for c in candidates])
    lll_idx = np.argmin(np.abs(cand_norms - sv_norm * 1.8))
    lll_vec = candidates[lll_idx]
    lll_norm = np.linalg.norm(lll_vec)

    # Draw shortest vector (red)
    ax.plot([0, sv[0]], [0, sv[1]], [0, sv[2]], color=ACCENT1, linewidth=3, zorder=10,
            label=f'True shortest: |v| = {sv_norm:.1f}')
    ax.scatter([sv[0]], [sv[1]], [sv[2]], c=ACCENT1, s=80, zorder=11)

    # Draw LLL vector (blue)
    ax.plot([0, lll_vec[0]], [0, lll_vec[1]], [0, lll_vec[2]], color=ACCENT2, linewidth=3, zorder=10,
            label=f'LLL approx: |v| = {lll_norm:.1f}')
    ax.scatter([lll_vec[0]], [lll_vec[1]], [lll_vec[2]], c=ACCENT2, s=80, zorder=11)

    # Draw spheres (wireframe)
    u = np.linspace(0, 2 * np.pi, 30)
    v = np.linspace(0, np.pi, 20)
    xs = sv_norm * np.outer(np.cos(u), np.sin(v))
    ys = sv_norm * np.outer(np.sin(u), np.sin(v))
    zs = sv_norm * np.outer(np.ones_like(u), np.cos(v))
    ax.plot_wireframe(xs, ys, zs, color=ACCENT1, alpha=0.08, linewidth=0.5)

    xl = lll_norm * np.outer(np.cos(u), np.sin(v))
    yl = lll_norm * np.outer(np.sin(u), np.sin(v))
    zl = lll_norm * np.outer(np.ones_like(u), np.cos(v))
    ax.plot_wireframe(xl, yl, zl, color=ACCENT2, alpha=0.06, linewidth=0.5)

    ax.scatter([0], [0], [0], c=DARK, s=60, zorder=12, marker='*')

    ax.set_xlabel('x', fontsize=12, color=DARK)
    ax.set_ylabel('y', fontsize=12, color=DARK)
    ax.set_zlabel('z', fontsize=12, color=DARK)
    ax.legend(fontsize=12, loc='upper left')
    ax.set_title("LLL's Bargain: a longer vector, found in polynomial time",
                 fontsize=16, fontweight='bold', color=DARK, pad=20)
    ax.view_init(elev=20, azim=35)
    save(fig, "fig08_lll_bargain.png")


# ============================================================
# ILLUSTRATION 9: Quadruple lattice sphere
# ============================================================
def fig09_quadruple_lattice():
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    N = 5
    R = 8

    # Draw sphere wireframe
    u = np.linspace(0, 2 * np.pi, 40)
    v = np.linspace(0, np.pi, 25)
    xs = R * np.outer(np.cos(u), np.sin(v))
    ys = R * np.outer(np.sin(u), np.sin(v))
    zs = R * np.outer(np.ones_like(u), np.cos(v))
    ax.plot_wireframe(xs, ys, zs, color=ACCENT2, alpha=0.05, linewidth=0.3)

    # Interior lattice points satisfying x^2+y^2+z^2 ≡ 0 (mod N)
    sublattice_pts = []
    for i in range(-R, R + 1):
        for j in range(-R, R + 1):
            for k in range(-R, R + 1):
                r2 = i*i + j*j + k*k
                if r2 <= R*R and r2 > 0 and r2 % N == 0:
                    sublattice_pts.append((i, j, k))

    if sublattice_pts:
        sublattice_pts = np.array(sublattice_pts)
        ax.scatter(sublattice_pts[:, 0], sublattice_pts[:, 1], sublattice_pts[:, 2],
                   c=GLOW, s=25, alpha=0.7, edgecolors=ACCENT5, linewidth=0.5, zorder=5)

    # Origin star
    ax.scatter([0], [0], [0], c=ACCENT1, s=200, marker='*', zorder=15,
               edgecolors=DARK, linewidth=1)
    ax.text(0.5, 0.5, 0.5, '$(0,0,0)$', fontsize=11, color=DARK)

    # Mark a few "revealing" points near the surface
    if len(sublattice_pts) > 3:
        norms = np.sum(sublattice_pts**2, axis=1)
        near_surface = np.abs(norms - R*R) < R
        if np.any(near_surface):
            special = sublattice_pts[near_surface][:5]
            for pt in special:
                ax.scatter([pt[0]], [pt[1]], [pt[2]], c=ACCENT1, s=100, zorder=10,
                           edgecolors=DARK, linewidth=1.5, marker='o')

    ax.set_xlabel('$x$', fontsize=14, color=DARK)
    ax.set_ylabel('$y$', fontsize=14, color=DARK)
    ax.set_zlabel('$z$', fontsize=14, color=DARK)
    ax.set_title('The Quadruple Lattice: $x^2 + y^2 + z^2 \\equiv 0\\ (\\mathrm{mod}\\ N)$',
                 fontsize=16, fontweight='bold', color=DARK, pad=20)
    ax.view_init(elev=25, azim=40)

    fig.text(0.5, 0.02, 'Lattice points on the sphere reveal the factors of $N$.',
             fontsize=14, ha='center', color=DARK, fontstyle='italic')
    save(fig, "fig09_quadruple_lattice.png")


# ============================================================
# ILLUSTRATION 10: Chapter concept map (treasure map style)
# ============================================================
def fig10_concept_map():
    fig, ax = plt.subplots(1, 1, figsize=(14, 16))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    # Decorative border
    border = patches.FancyBboxPatch((0.3, 0.3), 13.4, 18.4,
                                     boxstyle="round,pad=0.3",
                                     facecolor='none', edgecolor=DARK,
                                     linewidth=3)
    ax.add_patch(border)
    inner_border = patches.FancyBboxPatch((0.5, 0.5), 13.0, 18.0,
                                           boxstyle="round,pad=0.2",
                                           facecolor='none', edgecolor=GOLD,
                                           linewidth=1.5, linestyle='--')
    ax.add_patch(inner_border)

    # Title
    ax.text(7, 18, 'Chapter 2 — Concept Map', fontsize=22, ha='center',
            va='center', color=DARK, fontweight='bold', fontfamily='serif')

    # === Node: Berggren Tree ===
    box1 = FancyBboxPatch((4.5, 15.5), 5, 1.5, boxstyle="round,pad=0.2",
                           facecolor=CREAM, edgecolor=DARK, linewidth=2)
    ax.add_patch(box1)
    ax.text(7, 16.5, 'Berggren Tree', fontsize=16, ha='center',
            va='center', color=DARK, fontweight='bold')
    ax.text(7, 16.0, 'Binary tree of $(m, n)$ pairs', fontsize=11, ha='center',
            va='center', color=SLATE)

    # Arrow: inverse traversal
    ax.annotate('', xy=(7, 14.0), xytext=(7, 15.4),
                arrowprops=dict(arrowstyle='->', color=ACCENT4, lw=3))
    ax.text(8.5, 14.7, 'inverse\ntraversal', fontsize=12, ha='left',
            va='center', color=ACCENT4, fontweight='bold')

    # === Node: Euclidean Algorithm ===
    box2 = FancyBboxPatch((4.0, 12.5), 6, 1.5, boxstyle="round,pad=0.2",
                           facecolor=CREAM, edgecolor=DARK, linewidth=2)
    ax.add_patch(box2)
    ax.text(7, 13.5, 'Euclidean Algorithm', fontsize=16, ha='center',
            va='center', color=DARK, fontweight='bold')
    ax.text(7, 13.0, 'Descent via quotient matrices', fontsize=11, ha='center',
            va='center', color=SLATE)

    # Arrow: matrix formulation
    ax.annotate('', xy=(7, 10.7), xytext=(7, 12.4),
                arrowprops=dict(arrowstyle='->', color=ACCENT2, lw=3))
    ax.text(8.5, 11.5, 'matrix\nformulation', fontsize=12, ha='left',
            va='center', color=ACCENT2, fontweight='bold')

    # === Node: Gauss 2D Reduction ===
    box3 = FancyBboxPatch((3.5, 9.2), 7, 1.5, boxstyle="round,pad=0.2",
                           facecolor=CREAM, edgecolor=DARK, linewidth=2)
    ax.add_patch(box3)
    ax.text(7, 10.2, 'Gauss 2D Reduction', fontsize=16, ha='center',
            va='center', color=DARK, fontweight='bold')
    ax.text(7, 9.7, 'Shortest vector in 2D lattice', fontsize=11, ha='center',
            va='center', color=SLATE)

    # === RED BARRIER ===
    barrier_y = 7.5
    ax.fill_between([1, 13], barrier_y - 0.4, barrier_y + 0.4,
                    color=ACCENT1, alpha=0.3)
    ax.plot([1, 13], [barrier_y, barrier_y], color=ACCENT1, linewidth=4)
    ax.text(7, barrier_y, '$\\Theta(\\sqrt{N})$ wall', fontsize=18, ha='center',
            va='center', color=ACCENT1, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=LIGHT_RED, edgecolor=ACCENT1))

    # Arrow down through barrier
    ax.annotate('', xy=(7, 5.5), xytext=(7, 7.0),
                arrowprops=dict(arrowstyle='->', color=ACCENT3, lw=3, linestyle='--'))
    ax.text(8.5, 6.3, 'breaking\nthrough!', fontsize=12, ha='left',
            va='center', color=ACCENT3, fontweight='bold')

    # === GLOWING REGION BELOW ===
    glow_box = FancyBboxPatch((2, 2.5), 10, 3.5, boxstyle="round,pad=0.3",
                               facecolor=GLOW, edgecolor=GOLD,
                               linewidth=2, alpha=0.25)
    ax.add_patch(glow_box)

    # Node: LLL in d >= 3
    box4 = FancyBboxPatch((2.5, 4.5), 4.5, 1.2, boxstyle="round,pad=0.2",
                           facecolor=CREAM, edgecolor=ACCENT3, linewidth=2)
    ax.add_patch(box4)
    ax.text(4.75, 5.1, 'LLL in $d \\geq 3$', fontsize=15, ha='center',
            va='center', color=ACCENT3, fontweight='bold')

    # Node: Quadruple Lattice
    box5 = FancyBboxPatch((7.5, 4.5), 4.5, 1.2, boxstyle="round,pad=0.2",
                           facecolor=CREAM, edgecolor=ACCENT5, linewidth=2)
    ax.add_patch(box5)
    ax.text(9.75, 5.1, 'Quadruple Lattice', fontsize=15, ha='center',
            va='center', color=ACCENT5, fontweight='bold')

    # Arrows to Chapter 3
    ax.annotate('', xy=(7, 2.0), xytext=(4.75, 4.4),
                arrowprops=dict(arrowstyle='->', color=ACCENT3, lw=2.5))
    ax.annotate('', xy=(7, 2.0), xytext=(9.75, 4.4),
                arrowprops=dict(arrowstyle='->', color=ACCENT5, lw=2.5))
    ax.text(7, 1.5, 'Chapter 3  →', fontsize=18, ha='center', va='center',
            color=DARK, fontweight='bold', fontstyle='italic',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=CREAM, edgecolor=GOLD, linewidth=2))

    # Compass rose (decorative)
    cx, cy = 12, 16.5
    r = 0.6
    ax.text(cx, cy + r + 0.05, 'N', fontsize=10, ha='center', va='bottom',
            color=DARK, fontweight='bold')
    ax.text(cx, cy - r - 0.05, 'S', fontsize=10, ha='center', va='top',
            color=DARK, fontweight='bold')
    ax.text(cx + r + 0.05, cy, 'E', fontsize=10, ha='left', va='center',
            color=DARK, fontweight='bold')
    ax.text(cx - r - 0.05, cy, 'W', fontsize=10, ha='right', va='center',
            color=DARK, fontweight='bold')
    ax.plot([cx, cx], [cy - r + 0.15, cy + r - 0.15], color=DARK, linewidth=1.5)
    ax.plot([cx - r + 0.15, cx + r - 0.15], [cy, cy], color=DARK, linewidth=1.5)
    circle = plt.Circle((cx, cy), r, fill=False, edgecolor=DARK, linewidth=1.5)
    ax.add_patch(circle)

    ax.set_xlim(0, 14)
    ax.set_ylim(0.5, 19)
    ax.set_aspect('equal')
    ax.axis('off')
    save(fig, "fig10_concept_map.png")


# ============================================================
# Run all
# ============================================================
if __name__ == '__main__':
    print("Generating Chapter 2 illustrations...")
    fig01_factory_tree()
    fig02_lattice_shear()
    fig03_euclid_staircase()
    fig04_tree_vs_euclid()
    fig05_complexity_graph()
    fig06_gauss_reduction()
    fig07_2d_barrier()
    fig08_lll_bargain()
    fig09_quadruple_lattice()
    fig10_concept_map()
    print("Done! All images saved to Chapter2/images/")

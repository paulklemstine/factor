#!/usr/bin/env python3
"""Generate all illustrations for Chapter 7: The One-Way Corridor."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Arc
import matplotlib.patheffects as pe
import numpy as np
import os
from math import gcd

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
os.makedirs(OUT, exist_ok=True)

# Color palette (matching book style)
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
SHADOW = '#BFBFBF'

def save(fig, name, dpi=200):
    fig.savefig(os.path.join(OUT, name), dpi=dpi, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  Saved {name}")


# ============================================================
# FIGURE 1: Ternary labyrinth cross-section
# ============================================================
def fig01_ternary_labyrinth():
    fig, ax = plt.subplots(figsize=(12, 10))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    levels = 5
    # Build tree positions
    positions = {}  # (level, index) -> x
    gold_path = [0, 1, 0, 2, 1]  # which branch at each level (arbitrary)

    for lvl in range(levels + 1):
        n_nodes = 3 ** lvl
        for i in range(n_nodes):
            x = (i + 0.5) / n_nodes * 20 - 10
            y = -lvl * 1.6
            positions[(lvl, i)] = (x, y)

    # Determine gold nodes
    gold_nodes = set()
    idx = 0
    for lvl in range(levels):
        gold_nodes.add((lvl, idx))
        idx = idx * 3 + gold_path[lvl]
    gold_nodes.add((levels, idx))
    treasure_node = (levels, idx)

    # Draw edges
    for lvl in range(levels):
        n_nodes = 3 ** lvl
        for i in range(n_nodes):
            px, py = positions[(lvl, i)]
            for child in range(3):
                ci = i * 3 + child
                cx, cy = positions[(lvl + 1, ci)]
                is_gold = (lvl, i) in gold_nodes and (lvl + 1, ci) in gold_nodes
                color = GOLD if is_gold else SHADOW
                lw = 3.5 if is_gold else 1.0
                alpha = 1.0 if is_gold else 0.35
                ax.plot([px, cx], [py, cy], color=color, linewidth=lw,
                        alpha=alpha, zorder=2 if is_gold else 1)

    # Draw nodes
    for (lvl, i), (x, y) in positions.items():
        if (lvl, i) in gold_nodes:
            ax.plot(x, y, 'o', color=GOLD, markersize=10, markeredgecolor=DARK,
                    markeredgewidth=1.5, zorder=5)
        else:
            ax.plot(x, y, 'o', color=SHADOW, markersize=4, alpha=0.4, zorder=3)

    # Dead-end markers on non-gold leaf nodes
    for i in range(3 ** levels):
        if (levels, i) not in gold_nodes:
            x, y = positions[(levels, i)]
            if np.random.random() < 0.15:
                ax.text(x, y - 0.3, '✗', fontsize=7, ha='center', va='top',
                        color=ACCENT1, alpha=0.6)

    # Treasure at bottom of gold path
    tx, ty = positions[treasure_node]
    ax.plot(tx, ty, '*', color=GOLD, markersize=25, markeredgecolor=DARK,
            markeredgewidth=1, zorder=6)
    ax.text(tx, ty - 0.7, 'Treasure', fontsize=11, ha='center', color=DARK,
            fontweight='bold', fontstyle='italic')

    # Entrance at top
    ex, ey = positions[(0, 0)]
    ax.annotate('Entrance', xy=(ex, ey + 0.3), fontsize=13, ha='center',
                color=DARK, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=DARK, lw=1.5),
                xytext=(ex, ey + 1.5))

    ax.set_title("The Ternary Labyrinth\nOne golden path — all others are dead ends",
                  fontsize=16, color=DARK, fontweight='bold', pad=20)
    ax.set_xlim(-11, 11)
    ax.set_ylim(-levels * 1.6 - 1.5, 3)
    ax.axis('off')
    save(fig, "fig01_ternary_labyrinth.png")


# ============================================================
# FIGURE 2: Pythagorean-triple tree with inverse maps
# ============================================================
def fig02_triple_tree():
    fig, ax = plt.subplots(figsize=(14, 10))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    # Berggren matrices
    B1 = np.array([[1, -2, 2], [2, -1, 2], [2, -2, 3]])
    B2 = np.array([[1, 2, 2], [2, 1, 2], [2, 2, 3]])
    B3 = np.array([[-1, 2, 2], [-2, 1, 2], [-2, 2, 3]])
    matrices = [B1, B2, B3]
    inv_colors = [ACCENT1, ACCENT2, ACCENT3]
    inv_labels = [r'$B_1^{-1}$', r'$B_2^{-1}$', r'$B_3^{-1}$']

    root = np.array([3, 4, 5])

    # Build tree: root + 2 levels
    tree = {}
    tree[(0, 0)] = {'triple': root, 'x': 0, 'y': 0}

    # Level 1
    level1 = []
    for i, M in enumerate(matrices):
        child = M @ root
        child = np.abs(child)
        child.sort()
        level1.append(child)
        tree[(1, i)] = {'triple': child, 'x': -6 + i * 6, 'y': -3}

    # Level 2
    idx = 0
    for pi in range(3):
        parent = level1[pi]
        for ci, M in enumerate(matrices):
            child = M @ parent
            child = np.abs(child)
            child.sort()
            tree[(2, idx)] = {'triple': child, 'x': -8 + idx * 2, 'y': -6}
            idx += 1

    # Draw edges and inverse map annotations
    for lvl in range(2):
        n_parent = 3 ** lvl
        for pi in range(n_parent):
            px, py = tree[(lvl, pi)]['x'], tree[(lvl, pi)]['y']
            for ci in range(3):
                child_idx = pi * 3 + ci
                if (lvl + 1, child_idx) in tree:
                    cx, cy = tree[(lvl + 1, child_idx)]['x'], tree[(lvl + 1, child_idx)]['y']
                    ax.plot([px, cx], [py, cy], color=SLATE, linewidth=1.5, zorder=1)

                    # Upward arrow (inverse map) - only the valid one is solid
                    # For simplicity, show the valid inverse in color, others crossed
                    mid_x = (px + cx) / 2
                    mid_y = (py + cy) / 2

                    # The valid inverse is always ci (child came from branch ci)
                    valid_inv = ci
                    # Draw small colored arrow for valid inverse
                    ax.annotate('', xy=(px, py + 0.2), xytext=(cx, cy - 0.2),
                                arrowprops=dict(arrowstyle='->', color=inv_colors[valid_inv],
                                                lw=2, alpha=0.7))

    # Draw nodes
    for key, info in tree.items():
        x, y = info['x'], info['y']
        t = info['triple']
        label = f"({t[0]},{t[1]},{t[2]})"
        bbox = dict(boxstyle='round,pad=0.3', facecolor=CREAM,
                     edgecolor=DARK, linewidth=1.5)
        fontsize = 11 if key[0] < 2 else 8
        ax.text(x, y, label, fontsize=fontsize, ha='center', va='center',
                bbox=bbox, zorder=5, color=DARK, fontweight='bold')

    # Legend
    for i in range(3):
        ax.plot([], [], color=inv_colors[i], linewidth=2, label=inv_labels[i] + ' (valid)')
    ax.legend(loc='upper right', fontsize=11, framealpha=0.9)

    ax.set_title("Pythagorean Triple Tree with Inverse Maps\n"
                  "Each node has exactly one valid parent",
                  fontsize=15, color=DARK, fontweight='bold', pad=15)
    ax.set_xlim(-10, 10)
    ax.set_ylim(-7.5, 2)
    ax.axis('off')
    save(fig, "fig02_triple_tree.png")


# ============================================================
# FIGURE 3: Number-line seesaw (Sum-to-Zero impossibility)
# ============================================================
def fig03_seesaw():
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.set_facecolor(SAND)

    pair_labels = [
        (r'$B_1^{-1}$  &  $B_2^{-1}$', r'$s_1$', r'$s_2$'),
        (r'$B_1^{-1}$  &  $B_3^{-1}$', r'$s_1$', r'$s_3$'),
        (r'$B_2^{-1}$  &  $B_3^{-1}$', r'$s_2$', r'$s_3$'),
    ]

    for idx, (ax, (title, w1, w2)) in enumerate(zip(axes, pair_labels)):
        ax.set_facecolor(SAND)
        ax.set_xlim(-4, 4)
        ax.set_ylim(-1.5, 3)

        # Fulcrum triangle
        fx, fy = 0, 0
        tri = plt.Polygon([(-0.3, -0.6), (0.3, -0.6), (0, 0)],
                           facecolor=SLATE, edgecolor=DARK, zorder=3)
        ax.add_patch(tri)

        # Beam (tilted/snapping)
        angle = 8 if idx % 2 == 0 else -5
        bx = np.array([-3, 3])
        by = np.array([0, 0])
        # Draw a cracked beam
        ax.plot([-3, -0.1], [0.3, 0.05], color=DARK, linewidth=4, zorder=2)
        ax.plot([0.1, 3], [0.05, 0.3], color=DARK, linewidth=4, zorder=2)

        # Crack mark at center
        for dx, dy in [(-0.05, 0.15), (0.05, -0.1), (0, 0.08)]:
            ax.plot([dx - 0.08, dx + 0.08], [dy + 0.02, dy + 0.12],
                    color=ACCENT1, linewidth=1.5, zorder=4)

        # Weights
        ax.add_patch(FancyBboxPatch((-2.8, 0.3), 1.2, 0.8,
                                     boxstyle='round,pad=0.1',
                                     facecolor=ACCENT2, edgecolor=DARK, zorder=4))
        ax.text(-2.2, 0.7, w1, fontsize=14, ha='center', va='center',
                color='white', fontweight='bold', zorder=5)

        ax.add_patch(FancyBboxPatch((1.6, 0.3), 1.2, 0.8,
                                     boxstyle='round,pad=0.1',
                                     facecolor=ACCENT3, edgecolor=DARK, zorder=4))
        ax.text(2.2, 0.7, w2, fontsize=14, ha='center', va='center',
                color='white', fontweight='bold', zorder=5)

        # Both positive labels
        ax.text(-2.2, 1.4, '> 0', fontsize=11, ha='center', color=ACCENT2, fontweight='bold')
        ax.text(2.2, 1.4, '> 0', fontsize=11, ha='center', color=ACCENT3, fontweight='bold')

        # Sum equation
        ax.text(0, 2.4, f'{w1} + {w2} = 0  ✗', fontsize=13, ha='center',
                color=ACCENT1, fontweight='bold')

        ax.set_title(title, fontsize=12, color=DARK, fontweight='bold')
        ax.axis('off')

    fig.suptitle("The Seesaw Principle: Both positive cannot sum to zero",
                 fontsize=15, color=DARK, fontweight='bold', y=1.02)
    fig.tight_layout()
    save(fig, "fig03_seesaw.png")


# ============================================================
# FIGURE 4: Venn diagram — exclusive branches
# ============================================================
def fig04_venn_exclusive():
    fig, ax = plt.subplots(figsize=(10, 8))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    # Three circles
    centers = [(-1.2, 0.7), (1.2, 0.7), (0, -0.8)]
    labels = [r'$B_1^{-1}$ positive', r'$B_2^{-1}$ positive', r'$B_3^{-1}$ positive']
    colors = [ACCENT1, ACCENT2, ACCENT3]
    radius = 2.0

    for (cx, cy), label, color in zip(centers, labels, colors):
        circle = plt.Circle((cx, cy), radius, facecolor=color, alpha=0.15,
                             edgecolor=color, linewidth=2.5, zorder=2)
        ax.add_patch(circle)
        # Label outside
        lx = cx * 1.8
        ly = cy * 1.8 + (0.3 if cy > 0 else -0.3)
        ax.text(cx, cy + radius + 0.3, label, fontsize=13, ha='center',
                va='bottom', color=color, fontweight='bold')

    # EMPTY stamps at each pairwise intersection
    intersection_pts = [
        (0, 1.2),     # B1 ∩ B2
        (-0.8, -0.3), # B1 ∩ B3
        (0.8, -0.3),  # B2 ∩ B3
    ]
    for (ix, iy) in intersection_pts:
        ax.text(ix, iy, 'EMPTY', fontsize=14, ha='center', va='center',
                color=ACCENT1, fontweight='bold', fontstyle='italic',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                          edgecolor=ACCENT1, linewidth=2, alpha=0.9),
                rotation=15, zorder=10)

    ax.set_title("At most one inverse map yields a valid triple",
                  fontsize=15, color=DARK, fontweight='bold', pad=15)
    ax.set_xlim(-4, 4)
    ax.set_ylim(-3.5, 4)
    ax.set_aspect('equal')
    ax.axis('off')
    save(fig, "fig04_venn_exclusive.png")


# ============================================================
# FIGURE 5: The Circular Library (Grover search)
# ============================================================
def fig05_circular_library():
    fig, ax = plt.subplots(figsize=(10, 10))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    S = 64
    marked_indices = {5, 18, 37, 52}  # 4 marked shelves
    radius = 4.0

    # Draw shelves in a circle
    for i in range(S):
        angle = 2 * np.pi * i / S - np.pi / 2
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)

        if i in marked_indices:
            color = GOLD
            size = 9
            ax.plot(x, y, 's', color=color, markersize=size,
                    markeredgecolor=DARK, markeredgewidth=1.5, zorder=5)
        else:
            color = SLATE
            ax.plot(x, y, 's', color=color, markersize=5, alpha=0.4, zorder=3)

    # Quantum wave from center
    for r_wave in np.linspace(0.5, 3.8, 8):
        circle = plt.Circle((0, 0), r_wave, fill=False,
                             edgecolor=ACCENT4, alpha=0.15 + 0.05 * (r_wave / 4),
                             linewidth=1.5, linestyle='--', zorder=2)
        ax.add_patch(circle)

    # Quantum librarian at center
    ax.plot(0, 0, 'o', color=ACCENT4, markersize=18, markeredgecolor=DARK,
            markeredgewidth=2, zorder=6)
    ax.text(0, -0.5, 'Quantum\nSearcher', fontsize=9, ha='center', va='top',
            color=ACCENT4, fontweight='bold')

    # Classical librarian trudging around
    cl_angle = 2 * np.pi * 12 / S - np.pi / 2
    cl_x = radius * np.cos(cl_angle) + 0.6
    cl_y = radius * np.sin(cl_angle) + 0.3
    ax.plot(cl_x, cl_y, 'o', color=ACCENT5, markersize=14, markeredgecolor=DARK,
            markeredgewidth=2, zorder=6)
    ax.text(cl_x + 0.5, cl_y + 0.3, 'Classical\nSearcher', fontsize=9,
            ha='left', color=ACCENT5, fontweight='bold')

    # Progress bars at bottom
    bar_y = -5.8
    # Classical bar
    ax.add_patch(patches.Rectangle((-4.5, bar_y), 4.0, 0.4,
                                    facecolor=ACCENT5, alpha=0.3, edgecolor=DARK))
    ax.add_patch(patches.Rectangle((-4.5, bar_y), 4.0 * (16/16), 0.4,
                                    facecolor=ACCENT5, alpha=0.6, edgecolor=DARK))
    ax.text(-2.5, bar_y + 0.2, 'Classical: 16 steps', fontsize=10,
            ha='center', va='center', color='white', fontweight='bold')

    # Quantum bar
    ax.add_patch(patches.Rectangle((0.5, bar_y), 4.0, 0.4,
                                    facecolor=ACCENT4, alpha=0.3, edgecolor=DARK))
    ax.add_patch(patches.Rectangle((0.5, bar_y), 4.0 * (4/16), 0.4,
                                    facecolor=ACCENT4, alpha=0.6, edgecolor=DARK))
    ax.text(2.5, bar_y + 0.2, 'Quantum: 4 steps', fontsize=10,
            ha='center', va='center', color='white', fontweight='bold')

    ax.text(0, -6.8, r'$S = 64$ shelves, $M = 4$ marked  ·  '
            r'Classical $= S/M = 16$  ·  Quantum $= \sqrt{S/M} = 4$',
            fontsize=10, ha='center', color=DARK)

    ax.set_title("The Circular Library — Grover's Search",
                  fontsize=16, color=DARK, fontweight='bold', pad=15)
    ax.set_xlim(-5.5, 5.5)
    ax.set_ylim(-7.5, 5.5)
    ax.set_aspect('equal')
    ax.axis('off')
    save(fig, "fig05_circular_library.png")


# ============================================================
# FIGURE 6: Elevator shaft — depth search
# ============================================================
def fig06_elevator_shaft():
    fig, ax = plt.subplots(figsize=(10, 12))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    n_floors = 8
    d_star = 6  # the magic floor

    shaft_left = -2
    shaft_right = 2
    floor_height = 1.3

    # Draw shaft walls
    ax.plot([shaft_left, shaft_left], [0.5, -(n_floors + 0.5) * floor_height],
            color=DARK, linewidth=3)
    ax.plot([shaft_right, shaft_right], [0.5, -(n_floors + 0.5) * floor_height],
            color=DARK, linewidth=3)

    for d in range(1, n_floors + 1):
        y = -d * floor_height
        is_star = (d == d_star)

        # Floor line
        ax.plot([shaft_left, shaft_right], [y, y], color=DARK,
                linewidth=2 if not is_star else 3, zorder=2)

        # Floor label
        label = f'd = {d}' if d <= n_floors else ''
        if d == d_star:
            label = f'd* = {d}'
        ax.text(shaft_left - 0.3, y, label, fontsize=11, ha='right', va='center',
                color=DARK, fontweight='bold' if is_star else 'normal')

        # GCD box
        if is_star:
            gcd_text = r'$\gcd(\mathrm{leg}_{d^*}, N) = p$'
            bbox_color = LIGHT_GREEN
            text_color = ACCENT3
            ax.add_patch(FancyBboxPatch((-1.8, y - 0.25), 3.6, 0.5,
                                         boxstyle='round,pad=0.1',
                                         facecolor=LIGHT_GREEN, edgecolor=ACCENT3,
                                         linewidth=2.5, zorder=4))
            ax.text(0, y, gcd_text, fontsize=11, ha='center', va='center',
                    color=ACCENT3, fontweight='bold', zorder=5)
            # Burst effect
            for angle in np.linspace(0, 2 * np.pi, 12, endpoint=False):
                dx = 2.2 * np.cos(angle)
                dy = 0.4 * np.sin(angle)
                ax.plot([0 + dx * 0.8, 0 + dx], [y + dy * 0.8, y + dy],
                        color=GOLD, linewidth=1.5, alpha=0.6, zorder=3)
        else:
            gcd_text = r'$\gcd(\mathrm{leg}_d, N) = 1$'
            ax.text(0, y, gcd_text, fontsize=9, ha='center', va='center',
                    color=SLATE, alpha=0.7, zorder=5)

    # Classical figure descending step by step (left side)
    for d in range(1, d_star + 1):
        y = -d * floor_height
        ax.plot(shaft_left + 0.5, y + 0.15, 'v', color=ACCENT5, markersize=8,
                alpha=0.3 + 0.1 * d, zorder=6)
    ax.text(shaft_left + 0.5, 0.3, 'Classical\n(step by step)', fontsize=9,
            ha='center', color=ACCENT5, fontweight='bold')

    # Quantum figure leaping (right side)
    t_arc = np.linspace(0, 1, 100)
    arc_x = shaft_right - 0.5 + 0.3 * np.sin(8 * np.pi * t_arc)
    arc_y = -1 * floor_height * (1 - t_arc) + (-d_star * floor_height) * t_arc
    ax.plot(arc_x, arc_y, color=ACCENT4, linewidth=2, alpha=0.6, zorder=6,
            linestyle='--')
    ax.plot(shaft_right - 0.5, -d_star * floor_height + 0.15, '*',
            color=ACCENT4, markersize=15, zorder=7)
    ax.text(shaft_right - 0.5, 0.3, 'Quantum\n(Grover leap)', fontsize=9,
            ha='center', color=ACCENT4, fontweight='bold')

    ax.text(0, 1.2, r'$\sqrt{d^*}$ oscillations', fontsize=11,
            ha='center', color=ACCENT4, fontstyle='italic')

    ax.set_title("The Elevator Shaft — Searching for the Right Depth",
                  fontsize=15, color=DARK, fontweight='bold', pad=15)
    ax.set_xlim(-4, 4)
    ax.set_ylim(-(n_floors + 1) * floor_height, 2)
    ax.axis('off')
    save(fig, "fig06_elevator_shaft.png")


# ============================================================
# FIGURE 7: Log-log complexity comparison
# ============================================================
def fig07_complexity_plot():
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    N = np.logspace(2, 35, 500)

    # Curves
    classical = np.sqrt(N)
    quantum_tree = N ** 0.25
    shor = (np.log2(N)) ** 2

    ax.loglog(N, classical, '--', color=ACCENT1, linewidth=2.5, label=r'Classical tree descent $O(\sqrt{N})$')
    ax.loglog(N, quantum_tree, '-', color=ACCENT4, linewidth=2.5, label=r'Quantum tree descent $O(N^{1/4})$')
    ax.loglog(N, shor, '-', color=ACCENT3, linewidth=2.5, label=r"Shor's algorithm $O((\log N)^2)$")

    # Shade Grover speedup region
    ax.fill_between(N, quantum_tree, classical, alpha=0.12, color=ACCENT4,
                     label="Grover's speedup")

    # Vertical line at N = 10^30
    ax.axvline(x=1e30, color=DARK, linewidth=1.5, linestyle=':', alpha=0.6)
    ax.text(1.5e30, 1e3, r'$N = 10^{30}$' + '\n(RSA scale)', fontsize=10,
            color=DARK, ha='left', fontstyle='italic')

    ax.set_xlabel('N (number to factor)', fontsize=13, color=DARK)
    ax.set_ylabel('Number of queries', fontsize=13, color=DARK)
    ax.set_title("Complexity Comparison: Three Factoring Approaches",
                  fontsize=15, color=DARK, fontweight='bold', pad=15)
    ax.legend(fontsize=11, loc='upper left', framealpha=0.9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(1e2, 1e35)
    ax.set_ylim(1, 1e18)
    save(fig, "fig07_complexity_plot.png")


# ============================================================
# FIGURE 8: Descent ledger for N=15
# ============================================================
def fig08_descent_ledger():
    fig, ax = plt.subplots(figsize=(14, 12))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    # Berggren inverse matrices
    def B1_inv(a, b, c):
        return (a - 2*b + 2*c, 2*a - b - 2*c, 2*a - 2*b + 3*c)

    def B2_inv(a, b, c):
        return (a + 2*b + 2*c, 2*a + b - 2*c, 2*a + 2*b - 3*c)

    def B3_inv(a, b, c):
        return (-a + 2*b + 2*c, 2*a + b - 2*c, 2*a + 2*b - 3*c)

    # For N=15: start with triple from N. Let's use the standard approach.
    # We need to show a descent. Let's pick a starting triple and descend.
    # For N=15=3×5, we can use m=4,n=1 -> (8,15,17) or m=2,n=1 -> (3,4,5)
    # Let's use (7, 24, 25) which has gcd(24,15)=3, or (8,15,17)
    # Actually let's trace a real descent. Start from (8,15,17)
    # B1_inv(8,15,17) = (8-30+34, 16-15-34, 16-30+51) = (12, -33, 37) - invalid
    # B2_inv(8,15,17) = (8+30+34, 16+15-34, 16+30-51) = (72, -3, -5) - invalid
    # B3_inv(8,15,17) = (-8+30+34, 16+15-34, 16+30-51) = (56, -3, -5) - invalid
    # Hmm, (8,15,17) is a root-adjacent triple? Let's check: is (8,15,17) in the tree?
    # Actually (8,15,17) comes from (3,4,5) via B2: B2*(3,4,5) = (3+8+10, 6+4+10, 6+8+15) = (21,20,29)?
    # Let me recalculate. B1*(3,4,5) = (3-8+10, 6-4+10, 6-8+15) = (5,12,13)
    # B2*(3,4,5) = (3+8+10, 6+4+10, 6+8+15) = (21,20,29)
    # B3*(3,4,5) = (-3+8+10, -6+4+10, -6+8+15) = (15,8,17)
    # So (8,15,17) is from B3, parent (3,4,5).

    # Let's trace from a deeper triple. Use (20,21,29) -> has parent, etc.
    # Actually let's just demonstrate the concept with made-up but illustrative data

    # Better approach: start from (5,12,13), which is B1(3,4,5)
    # Then go deeper: B1(5,12,13) = (5-24+26, 10-12+26, 10-24+39) = (7,24,25)
    # gcd(24, 15) = 3! Found a factor.

    # So the descent from (7,24,25):
    # Level 0: (7,24,25)
    # B1_inv(7,24,25) = (7-48+50, 14-24-50, 14-48+75) = (9, -60, 41) INVALID
    # B2_inv(7,24,25) = (7+48+50, 14+24-50, 14+48-75) = (105, -12, -13) INVALID
    # B3_inv(7,24,25) = (-7+48+50, 14+24-50, 14+48-75) = (91, -12, -13) INVALID
    # Wait, that makes all invalid? That can't be right.
    # Let me recalculate B1_inv properly.
    # The standard inverse: B1^{-1} is the matrix inverse of B1.
    # B1 = [[1,-2,2],[2,-1,2],[2,-2,3]]
    # Actually the chapter gives specific formulas. Let me use those.

    # From the chapter:
    # B1^{-1}(a,b,c) = (a-2b+2c, -2a+b+2c, -2a+2b+3c) -- wait different from what I had

    def B1i(a, b, c):
        return (a - 2*b + 2*c, -2*a + b + 2*c, -2*a + 2*b + 3*c)

    def B2i(a, b, c):
        return (a + 2*b + 2*c, 2*a + b - 2*c, 2*a + 2*b - 3*c)

    def B3i(a, b, c):
        return (-a + 2*b + 2*c, 2*a + b - 2*c, 2*a + 2*b - 3*c)

    # Actually let's trace from a deeper node.
    # Start from (3,4,5). Children:
    # B1(3,4,5) = (5,12,13), B2(3,4,5) = (21,20,29), B3(3,4,5) = (15,8,17)
    # From (5,12,13): children B1(5,12,13)=(7,24,25), etc.
    # Let me use a triple relevant to N=15.
    # gcd(8,15)=1, gcd(15,15)=15 (trivial), gcd(24,15)=3 ✓
    # So (7,24,25) works - gcd(24,15) = 3.

    # Descent of (7,24,25):
    # B1i(7,24,25) = (7-48+50, -14+24+50, -14+48+75) = (9, 60, 109)
    #   Check: 9²+60² = 81+3600 = 3681, 109² = 11881 ≠ 3681. Not valid PT
    #   Hmm. Let me check if these inverses really give parent triples.

    # Actually (7,24,25) should have parent (5,12,13) via B1.
    # B1i(7,24,25) should give (5,12,13).
    # B1i: (7-48+50, -14+24+50, -14+48+75) = (9, 60, 109). That's wrong.
    # Something is off with the inverse formulas.

    # Let me verify: if B1*(a,b,c) = (a-2b+2c, 2a-b+2c, 2a-2b+3c)
    # Then B1*(5,12,13) = (5-24+26, 10-12+26, 10-24+39) = (7, 24, 25) ✓
    # Now B1^{-1} should invert this. The matrix B1 = [[1,-2,2],[2,-1,2],[2,-2,3]]
    # inv(B1) = [[1,2,-2],[-2,-1,2],[2,2,-1]] (standard result for Berggren)
    # So B1^{-1}(7,24,25) = (7+48-50, -14-24+50, 14+48-25) = (5, 12, 37)?
    # That's not right either. Let me compute inv(B1) properly.

    # det(B1) = 1*(-1*3-2*(-2)) -(-2)*(2*3-2*2) + 2*(2*(-2)-(-1)*2)
    #         = 1*(-3+4) + 2*(6-4) + 2*(-4+2) = 1 + 4 - 4 = 1

    # Cofactor matrix...this is getting complicated. Let me just use numpy.

    B1m = np.array([[1,-2,2],[2,-1,2],[2,-2,3]])
    B1inv = np.round(np.linalg.inv(B1m)).astype(int)
    # B1inv @ [7,24,25] should give [5,12,13]
    result = B1inv @ np.array([7,24,25])

    # Let me just define a simpler example.
    # I'll create a ledger showing the concept without exact math.

    # Levels of descent showing triples and validity
    ledger_data = [
        # (level, current_triple, [(inv_name, result, valid), ...])
    ]

    # Let's just hard-code a plausible illustration
    # We trace descent of triple (7,24,25) toward (3,4,5)
    # and show gcd(24,15)=3 at the end.

    # Let's compute properly with numpy
    B1m = np.array([[1,-2,2],[2,-1,2],[2,-2,3]])
    B2m = np.array([[1,2,2],[2,1,2],[2,2,3]])
    B3m = np.array([[-1,2,2],[-2,1,2],[-2,2,3]])
    B1inv = np.round(np.linalg.inv(B1m)).astype(int)
    B2inv = np.round(np.linalg.inv(B2m)).astype(int)
    B3inv = np.round(np.linalg.inv(B3m)).astype(int)
    inv_mats = [B1inv, B2inv, B3inv]
    inv_names = [r'$B_1^{-1}$', r'$B_2^{-1}$', r'$B_3^{-1}$']

    # Start with a triple at depth 3 from root, relevant to N=15
    # Path: (3,4,5) -> B1 -> (5,12,13) -> B1 -> (7,24,25) -> B2 -> (45, 28, 53)
    # Let me check: B2*(7,24,25) = (7+48+50, 14+24+50, 14+48+75) = (105, 88, 137)?
    # 105²+88² = 11025+7744 = 18769, 137² = 18769 ✓

    # Start from a deeper node and ascend
    # Let's use (45,28,53): B2*(7,24,25) = ... let me just compute
    test = B2m @ np.array([7,24,25])
    # = [7+48+50, 14+24+50, 14+48+75] = [105, 88, 137]
    # gcd(105,15)=15, gcd(88,15)=1

    # Let me use starting triple that gives interesting descent.
    # Use (105, 88, 137) from above.
    # At each level we show which inverse gives valid parent.

    descent_triples = []
    current = np.array([105, 88, 137])
    for step in range(4):
        inv_results = []
        valid_idx = -1
        for j, Minv in enumerate(inv_mats):
            res = Minv @ current
            valid = all(r > 0 for r in res)
            inv_results.append((res.copy(), valid))
            if valid:
                valid_idx = j
        descent_triples.append((current.copy(), inv_results, valid_idx))
        if valid_idx >= 0:
            current = inv_results[valid_idx][0]
        else:
            break
    # Add root
    descent_triples.append((current.copy(), [], -1))

    # Draw the ledger as a table
    row_height = 2.0
    col_width = 3.5
    n_rows = len(descent_triples) - 1  # Don't draw inverses for the root

    ax.set_xlim(-2, 14)
    ax.set_ylim(-(n_rows + 1) * row_height - 1, 2)

    # Header
    headers = ['Level', 'Current Triple', r'$B_1^{-1}$', r'$B_2^{-1}$', r'$B_3^{-1}$']
    header_x = [0, 3, 6.5, 9.5, 12.5]
    for hx, h in zip(header_x, headers):
        ax.text(hx, 0.5, h, fontsize=12, ha='center', va='center',
                color=DARK, fontweight='bold')

    ax.plot([-1.5, 14], [0, 0], color=DARK, linewidth=2)

    for row_idx in range(n_rows):
        y = -(row_idx + 1) * row_height
        triple, inv_results, valid_idx = descent_triples[row_idx]

        # Level number
        ax.text(0, y, f'd = {row_idx + 1}', fontsize=11, ha='center', va='center',
                color=DARK, fontweight='bold')

        # Current triple
        t = triple
        label = f'({t[0]},{t[1]},{t[2]})'
        ax.text(3, y, label, fontsize=10, ha='center', va='center',
                color=DARK, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor=CREAM,
                          edgecolor=DARK, linewidth=1.5))

        # Three inverse results
        for j, (res, valid) in enumerate(inv_results):
            x = 6.5 + j * 3
            res_label = f'({res[0]},{res[1]},{res[2]})'
            if valid:
                bbox_props = dict(boxstyle='round,pad=0.2', facecolor=LIGHT_GREEN,
                                   edgecolor=ACCENT3, linewidth=2)
                text_color = ACCENT3
            else:
                bbox_props = dict(boxstyle='round,pad=0.2', facecolor=LIGHT_RED,
                                   edgecolor=ACCENT1, linewidth=1.5)
                text_color = ACCENT1
            ax.text(x, y, res_label, fontsize=8, ha='center', va='center',
                    color=text_color, bbox=bbox_props)

        # Arrow to next row (from valid result)
        if valid_idx >= 0 and row_idx < n_rows - 1:
            ax.annotate('', xy=(3, y - row_height + 0.4),
                        xytext=(6.5 + valid_idx * 3, y - 0.4),
                        arrowprops=dict(arrowstyle='->', color=ACCENT3, lw=2))

    # GCD computation at bottom
    last_triple = descent_triples[-1][0]
    gcd_leg = last_triple[1] if last_triple[1] != 15 else last_triple[0]
    g = gcd(int(gcd_leg), 15)
    y_bottom = -(n_rows + 0.5) * row_height
    ax.text(6, y_bottom, f'gcd({gcd_leg}, 15) = {g}',
            fontsize=14, ha='center', va='center', color=ACCENT3,
            fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=LIGHT_GREEN,
                      edgecolor=ACCENT3, linewidth=2.5))

    ax.set_title("Descent Ledger for N = 15\n"
                  "Green = valid parent, Red = invalid (negative entries)",
                  fontsize=14, color=DARK, fontweight='bold', pad=15)
    ax.axis('off')
    save(fig, "fig08_descent_ledger.png")


# ============================================================
# FIGURE 9: Quantum branching vs quantum depth search
# ============================================================
def fig09_maze_solvers():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 9))
    fig.set_facecolor(SAND)

    # LEFT: Quantum Branching (Useless)
    ax1.set_facecolor(SAND)

    # Draw a small tree (3 levels)
    def draw_tree(ax, highlight_branch=1):
        positions = {}
        for lvl in range(4):
            n = 3 ** lvl
            for i in range(n):
                x = (i + 0.5) / n * 8 - 4
                y = -lvl * 2
                positions[(lvl, i)] = (x, y)

        # Draw edges
        for lvl in range(3):
            for i in range(3 ** lvl):
                px, py = positions[(lvl, i)]
                for c in range(3):
                    ci = i * 3 + c
                    cx, cy = positions[(lvl + 1, ci)]
                    ax.plot([px, cx], [py, cy], color=SLATE, linewidth=1, alpha=0.4)

        # Highlight one path
        idx = 0
        path_choices = [1, 0, 2]
        for lvl in range(3):
            px, py = positions[(lvl, idx)]
            idx = idx * 3 + path_choices[lvl]
            cx, cy = positions[(lvl + 1, idx)]
            ax.plot([px, cx], [py, cy], color=GOLD, linewidth=3, zorder=3)

        # Wave function spread (useless)
        for lvl in range(1, 4):
            for i in range(3 ** lvl):
                x, y = positions[(lvl, i)]
                circle = plt.Circle((x, y), 0.15, facecolor=ACCENT4,
                                     alpha=0.15, zorder=2)
                ax.add_patch(circle)

        # Collapse markers
        for lvl in range(1, 4):
            for i in range(3 ** lvl):
                x, y = positions[(lvl, i)]
                ax.plot(x, y, 'o', color=ACCENT4 if np.random.random() > 0.7 else SLATE,
                        markersize=4, alpha=0.5, zorder=3)

        return positions

    draw_tree(ax1)
    ax1.text(0, -7.5, 'Wave spreads across branches...\nbut only ONE is valid anyway!',
             fontsize=11, ha='center', color=ACCENT1, fontstyle='italic')
    ax1.text(0, -8.5, 'NO SPEEDUP', fontsize=16, ha='center',
             color=ACCENT1, fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.3', facecolor=LIGHT_RED,
                       edgecolor=ACCENT1, linewidth=2))
    ax1.set_title("Quantum Branching\n(Useless)", fontsize=14,
                   color=ACCENT1, fontweight='bold')
    ax1.set_xlim(-5, 5)
    ax1.set_ylim(-10, 1.5)
    ax1.axis('off')

    # RIGHT: Quantum Depth Search (Useful)
    ax2.set_facecolor(SAND)

    n_depths = 7
    d_star = 5

    for d in range(1, n_depths + 1):
        y = -d * 1.2
        color = ACCENT3 if d == d_star else SLATE
        alpha = 1.0 if d == d_star else 0.4
        lw = 3 if d == d_star else 1.5

        ax2.add_patch(patches.Rectangle((-2, y - 0.3), 4, 0.6,
                                         facecolor=color if d == d_star else CREAM,
                                         edgecolor=color, linewidth=lw, alpha=alpha))
        ax2.text(0, y, f'd = {d}' + (' = d*' if d == d_star else ''),
                 fontsize=11, ha='center', va='center',
                 color='white' if d == d_star else SLATE,
                 fontweight='bold' if d == d_star else 'normal')

    # Quantum wave oscillating across all depths
    t = np.linspace(0, 1, 200)
    wave_x = 3 + 0.5 * np.sin(12 * np.pi * t)
    wave_y = -1.2 + (-n_depths * 1.2 + 1.2) * t
    ax2.plot(wave_x, wave_y, color=ACCENT4, linewidth=2, alpha=0.7)

    # Concentration at d*
    for r in [0.3, 0.5, 0.7]:
        circle = plt.Circle((0, -d_star * 1.2), r,
                             fill=False, edgecolor=ACCENT4,
                             linewidth=2, alpha=0.4, linestyle='--')
        ax2.add_patch(circle)

    ax2.text(0, -n_depths * 1.2 - 1.5,
             'Quantum wave searches ALL depths\nand concentrates at d*!',
             fontsize=11, ha='center', color=ACCENT3, fontstyle='italic')
    ax2.text(0, -n_depths * 1.2 - 2.5, r'$\sqrt{d^*}$ SPEEDUP', fontsize=16,
             ha='center', color=ACCENT3, fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.3', facecolor=LIGHT_GREEN,
                       edgecolor=ACCENT3, linewidth=2))
    ax2.set_title("Quantum Depth Search\n(Useful)", fontsize=14,
                   color=ACCENT3, fontweight='bold')
    ax2.set_xlim(-4, 5)
    ax2.set_ylim(-n_depths * 1.2 - 3.5, 0.5)
    ax2.axis('off')

    fig.suptitle("Where the Quantum Magic Actually Lives",
                 fontsize=17, color=DARK, fontweight='bold', y=0.98)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    save(fig, "fig09_maze_solvers.png")


# ============================================================
# FIGURE 10: Mirror curves — Sum-to-Zero Principle
# ============================================================
def fig10_mirror_curves():
    fig, ax = plt.subplots(figsize=(10, 7))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    x = np.linspace(-3, 3, 500)
    f = 0.5 * np.sin(2 * x) + 0.3 * np.cos(x) + 0.2 * x
    g = -f  # mirror across x-axis

    ax.plot(x, f, color=ACCENT2, linewidth=2.5, label=r'$y = f(x)$', zorder=3)
    ax.plot(x, g, color=ACCENT1, linewidth=2.5, label=r'$y = g(x)$', zorder=3)

    # Shade where both are above x-axis (should be empty since g=-f)
    both_positive = np.minimum(f, g)
    both_positive_mask = (f > 0) & (g > 0)
    # Since g = -f, this never happens, but let's shade to show emptiness
    ax.fill_between(x, 0, np.where(both_positive_mask, both_positive, 0),
                     alpha=0.3, color=ACCENT5, label='Both > 0 (empty!)')

    ax.axhline(y=0, color=DARK, linewidth=1, zorder=1)

    # Annotations
    ax.annotate('f(x) > 0 here', xy=(1.2, f[int(500 * (1.2 + 3) / 6)]),
                fontsize=11, color=ACCENT2, fontweight='bold',
                xytext=(2, 1.5),
                arrowprops=dict(arrowstyle='->', color=ACCENT2))

    ax.annotate('g(x) < 0 here\n(mirror!)', xy=(1.2, g[int(500 * (1.2 + 3) / 6)]),
                fontsize=11, color=ACCENT1, fontweight='bold',
                xytext=(2.5, -1.5),
                arrowprops=dict(arrowstyle='->', color=ACCENT1))

    # Big annotation: region is empty
    ax.text(0, 1.8, 'Region where both f(x) > 0 and g(x) > 0\nis EMPTY',
            fontsize=13, ha='center', color=ACCENT5, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                      edgecolor=ACCENT5, linewidth=2, alpha=0.9))

    ax.set_xlabel('x', fontsize=13, color=DARK)
    ax.set_ylabel('y', fontsize=13, color=DARK)
    ax.set_title("Mirror Curves: the Sum-to-Zero Principle",
                  fontsize=15, color=DARK, fontweight='bold', pad=15)
    ax.legend(fontsize=11, loc='lower left', framealpha=0.9)
    ax.grid(True, alpha=0.2)
    ax.set_ylim(-2.5, 2.8)
    save(fig, "fig10_mirror_curves.png")


# ============================================================
# FIGURE 11: Complexity ladder
# ============================================================
def fig11_complexity_ladder():
    fig, ax = plt.subplots(figsize=(8, 12))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    rungs = [
        (r"Trial division — $O(\sqrt{N})$", ACCENT1, 4),
        (r"Classical tree descent — $O(\sqrt{N})$", ACCENT5, 3),
        (r"Quantum tree descent — $O(N^{1/4})$", ACCENT4, 2),
        (r"Shor's algorithm — $O((\log N)^2)$", ACCENT3, 1),
    ]

    speedup_labels = [
        (3.5, "Same complexity\n(different approach)", SLATE),
        (2.5, "Grover's speedup\n(quadratic)", ACCENT4),
        (1.5, "Periodicity\n(exponential)", ACCENT3),
    ]

    ladder_x = 0
    rung_width = 6

    # Draw ladder sides
    ax.plot([ladder_x - 0.3, ladder_x - 0.3], [0, 5], color=DARK, linewidth=4)
    ax.plot([ladder_x + rung_width + 0.3, ladder_x + rung_width + 0.3],
            [0, 5], color=DARK, linewidth=4)

    for label, color, y_pos in rungs:
        # Rung
        ax.plot([ladder_x, ladder_x + rung_width], [y_pos, y_pos],
                color=DARK, linewidth=3)

        # Label box
        ax.add_patch(FancyBboxPatch((ladder_x + 0.3, y_pos - 0.25),
                                     rung_width - 0.6, 0.5,
                                     boxstyle='round,pad=0.1',
                                     facecolor=color, edgecolor=DARK,
                                     linewidth=1.5, alpha=0.85))
        ax.text(ladder_x + rung_width / 2, y_pos, label,
                fontsize=11, ha='center', va='center',
                color='white', fontweight='bold')

    # Speedup arrows between rungs
    for y, label, color in speedup_labels:
        ax.annotate('', xy=(rung_width + 1, y - 0.35),
                    xytext=(rung_width + 1, y + 0.35),
                    arrowprops=dict(arrowstyle='<->', color=color, lw=2.5))
        ax.text(rung_width + 1.5, y, label, fontsize=10, va='center',
                color=color, fontweight='bold')

    # Speed labels
    ax.text(ladder_x + rung_width / 2, 4.6, '← SLOWER', fontsize=12,
            ha='center', color=ACCENT1, fontweight='bold')
    ax.text(ladder_x + rung_width / 2, 0.4, '← FASTER', fontsize=12,
            ha='center', color=ACCENT3, fontweight='bold')

    ax.set_title("The Complexity Ladder",
                  fontsize=16, color=DARK, fontweight='bold', pad=20)
    ax.set_xlim(-1.5, 11)
    ax.set_ylim(-0.5, 5.5)
    ax.axis('off')
    save(fig, "fig11_complexity_ladder.png")


# ============================================================
# FIGURE 12: The corridors ahead (open questions)
# ============================================================
def fig12_corridors_ahead():
    fig, ax = plt.subplots(figsize=(12, 9))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    # Stone corridor
    # Perspective lines converging to vanishing point
    vp_x, vp_y = 6, 5  # vanishing point
    floor_left = [(0, 0), (2, 0)]
    floor_right = [(10, 0), (12, 0)]

    # Draw corridor walls
    wall_color = '#8B7355'
    # Left wall
    ax.fill([0, 4.5, 7.5, 0], [0, 3, 7, 9], color=wall_color, alpha=0.3)
    # Right wall
    ax.fill([12, 7.5, 4.5, 12], [0, 3, 7, 9], color=wall_color, alpha=0.3)
    # Floor
    ax.fill([0, 12, 7.5, 4.5], [0, 0, 3, 3], color='#A0926B', alpha=0.3)

    # Doorway
    door_left, door_right = 4.5, 7.5
    door_bottom, door_top = 3, 7
    ax.fill([door_left, door_right, door_right, door_left],
            [door_bottom, door_bottom, door_top, door_top],
            color=GOLD, alpha=0.25)

    # Door frame
    ax.plot([door_left, door_left], [door_bottom, door_top], color=DARK, linewidth=3)
    ax.plot([door_right, door_right], [door_bottom, door_top], color=DARK, linewidth=3)
    ax.plot([door_left, door_right], [door_top, door_top], color=DARK, linewidth=3)

    # Sunlight rays
    for angle in np.linspace(-0.5, 0.5, 8):
        ray_x = vp_x + 3 * np.sin(angle)
        ray_y = 8
        ax.plot([vp_x, ray_x], [5, ray_y], color=GOLD, alpha=0.15, linewidth=3)

    # Branching corridors visible through doorway
    questions = ["Existence?", "Structure?", "Multi-channel?", "Hybrid?", "Physical?"]
    q_positions = [
        (5.0, 6.5), (5.8, 6.0), (6.5, 6.5), (5.3, 5.5), (6.2, 5.0)
    ]

    for (qx, qy), q in zip(q_positions, questions):
        ax.text(qx, qy, q, fontsize=10, ha='center', va='center',
                color=DARK, fontstyle='italic', alpha=0.7,
                bbox=dict(boxstyle='round,pad=0.15', facecolor=GOLD,
                          edgecolor=DARK, alpha=0.3, linewidth=1))
        # Small corridor lines
        ax.plot([qx, qx + 0.3 * (qx - 6)], [qy, qy + 0.5],
                color=DARK, linewidth=1, alpha=0.3)

    # Big question mark on doorway
    ax.text(6, 7.3, '?', fontsize=60, ha='center', va='center',
            color=DARK, fontweight='bold', alpha=0.4,
            fontfamily='serif')

    # Floor stones
    for i in range(5):
        y = i * 0.6
        w = 12 - i * 1.5
        x_start = (12 - w) / 2
        ax.plot([x_start, x_start + w], [y, y], color=DARK, linewidth=0.5, alpha=0.2)

    ax.set_title("The Corridors Ahead",
                  fontsize=18, color=DARK, fontweight='bold', pad=15)
    ax.set_xlim(-0.5, 12.5)
    ax.set_ylim(-0.5, 9.5)
    ax.axis('off')
    save(fig, "fig12_corridors_ahead.png")


# ============================================================
# Run all
# ============================================================
if __name__ == '__main__':
    print("Generating Chapter 7 illustrations...")
    fig01_ternary_labyrinth()
    fig02_triple_tree()
    fig03_seesaw()
    fig04_venn_exclusive()
    fig05_circular_library()
    fig06_elevator_shaft()
    fig07_complexity_plot()
    fig08_descent_ledger()
    fig09_maze_solvers()
    fig10_mirror_curves()
    fig11_complexity_ladder()
    fig12_corridors_ahead()
    print(f"Done! All images saved to {OUT}/")

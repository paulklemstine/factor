#!/usr/bin/env python3
"""Generate all illustrations for Chapter 3: Hyperbolic Shortcuts — How Pythagoras Learned to Factor."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import matplotlib.patheffects as pe
import numpy as np
import os
from math import gcd

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
os.makedirs(OUT, exist_ok=True)

# Color palette (matching Chapters 1 & 2)
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


# Berggren matrices
B1 = np.array([[1, -2, 2],
               [2, -1, 2],
               [2, -2, 3]])
B2 = np.array([[1, 2, 2],
               [2, 1, 2],
               [2, 2, 3]])
B3 = np.array([[-1, 2, 2],
               [-2, 1, 2],
               [-2, 2, 3]])

def berggren_children(triple):
    t = np.array(triple)
    return tuple(B1 @ t), tuple(B2 @ t), tuple(B3 @ t)


# Helper to draw a matrix with bracket lines (no LaTeX pmatrix)
def draw_matrix(ax, cx, cy, rows, fontsize=14, color=DARK):
    """Draw a matrix as individual text elements with bracket lines in axes coords."""
    n = len(rows)
    m = len(rows[0]) if rows else 0
    row_h = 0.065
    col_w = 0.045
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            x = cx + (j - (m - 1) / 2) * col_w
            y = cy + ((n - 1) / 2 - i) * row_h
            ax.text(x, y, f'${val}$', fontsize=fontsize, ha='center', va='center',
                    color=color, transform=ax.transAxes)
    top = cy + (n - 1) / 2 * row_h + 0.035
    bot = cy - (n - 1) / 2 * row_h - 0.035
    left = cx - (m - 1) / 2 * col_w - 0.028
    right = cx + (m - 1) / 2 * col_w + 0.028
    bw = 0.008
    # Left bracket
    ax.plot([left + bw, left, left, left + bw],
            [top, top, bot, bot], color=color, linewidth=2,
            transform=ax.transAxes, clip_on=False)
    # Right bracket
    ax.plot([right - bw, right, right, right - bw],
            [top, top, bot, bot], color=color, linewidth=2,
            transform=ax.transAxes, clip_on=False)


def draw_col_vector(ax, cx, cy, vals, fontsize=14, color=DARK):
    """Draw a column vector."""
    draw_matrix(ax, cx, cy, [[v] for v in vals], fontsize=fontsize, color=color)


# ============================================================
# FIG 1: The Broken Square — right triangle + cracked square
# ============================================================
def fig01_broken_square():
    fig, ax = plt.subplots(1, 1, figsize=(12, 9))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    tri_x = [0, 20, 0, 0]
    tri_y = [0, 0, 21, 0]
    ax.plot(tri_x, tri_y, color=DARK, linewidth=2.5, zorder=5)
    ax.fill(tri_x[:3], tri_y[:3], alpha=0.08, color=ACCENT2)

    sq = 1.2
    ax.plot([sq, sq, 0], [0, sq, sq], color=DARK, linewidth=1.5, zorder=5)

    ax.text(10, -1.8, '20', fontsize=16, ha='center', color=DARK, fontweight='bold')
    ax.text(-2.2, 10.5, '21', fontsize=16, ha='center', color=DARK, fontweight='bold')
    ax.text(12, 13, '29', fontsize=16, ha='center', color=DARK, fontweight='bold', rotation=-46)

    sq_x = [-21, 0, 0, -21, -21]
    sq_y = [0, 0, 21, 21, 0]
    ax.plot(sq_x, sq_y, color=DARK, linewidth=2, zorder=4)
    ax.fill([-21, 0, 0, -21], [0, 0, 21, 21], alpha=0.06, color=ACCENT5)

    crack_y = 9
    crack_xs = np.linspace(-21, 0, 80)
    crack_ys = crack_y + 0.2 * np.sin(crack_xs * 2) + 0.15 * np.cos(crack_xs * 5)
    ax.plot(crack_xs, crack_ys, color=ACCENT1, linewidth=2, zorder=6)

    ax.text(-10.5, 18, 'Area = $21^2 = 441$', fontsize=14, ha='center', color=DARK,
            fontweight='bold', style='italic')

    ax.annotate('$(29-20) \\times (29+20) = 9 \\times 49 = 441$',
                xy=(-10.5, crack_y), xytext=(-10.5, -4.5),
                fontsize=13, ha='center', color=ACCENT1, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=1.5))

    ax.text(-10.5, 4, '$9 = 3^2$', fontsize=13, ha='center', color=ACCENT4, alpha=0.7,
            fontweight='bold')
    ax.text(-10.5, 15, '$49 = 7^2$', fontsize=13, ha='center', color=ACCENT4, alpha=0.7,
            fontweight='bold')

    ax.text(-22.5, crack_y / 2, '9', fontsize=12, ha='center', va='center', color=SLATE,
            fontweight='bold')
    ax.text(-22.5, crack_y + (21 - crack_y) / 2, '12', fontsize=12, ha='center', va='center',
            color=SLATE)

    ax.set_xlim(-26, 24)
    ax.set_ylim(-7, 25)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('The Broken Square', fontsize=18, color=DARK, fontweight='bold', pad=15)

    save(fig, 'fig01_broken_square.png')


# ============================================================
# FIG 2: Factorization table for several Pythagorean triples
# ============================================================
def fig02_factor_table():
    fig, ax = plt.subplots(1, 1, figsize=(14, 7))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.axis('off')

    triples = [
        (3, 4, 5),
        (5, 12, 13),
        (8, 15, 17),
        (7, 24, 25),
        (21, 20, 29),
        (9, 40, 41),
    ]

    headers = ['$a$', '$b$', '$c$', '$c - b$', '$c + b$', 'Revealed factors of $a$']
    col_x = [0.08, 0.18, 0.28, 0.40, 0.54, 0.78]
    row_y_start = 0.88
    row_h = 0.10

    for j, h in enumerate(headers):
        ax.text(col_x[j], row_y_start, h, fontsize=13, ha='center', va='center',
                fontweight='bold', color=DARK, transform=ax.transAxes)

    ax.axhline(y=0.83, xmin=0.02, xmax=0.98, color=DARK, linewidth=1.5)

    for i, (a, b, c) in enumerate(triples):
        y = row_y_start - (i + 1) * row_h
        cmb = c - b
        cpb = c + b
        g = gcd(cmb, a)
        nontrivial = 1 < g < a

        if nontrivial:
            rect = patches.FancyBboxPatch((0.02, y - 0.04), 0.96, 0.08,
                                          transform=ax.transAxes,
                                          boxstyle="round,pad=0.01",
                                          facecolor=GLOW, alpha=0.3,
                                          edgecolor='none', zorder=0)
            ax.add_patch(rect)

        vals = [str(a), str(b), str(c), str(cmb), str(cpb)]
        for j, v in enumerate(vals):
            ax.text(col_x[j], y, f'${v}$', fontsize=13, ha='center', va='center',
                    color=DARK, transform=ax.transAxes)

        if nontrivial:
            factor_str = f'$\\gcd({cmb}, {a}) = {g}$  ->  ${a} = {g} \\times {a // g}$'
            fc = ACCENT1
        else:
            factor_str = f'$\\gcd({cmb}, {a}) = {g}$ (trivial)'
            fc = SLATE
        ax.text(col_x[5], y, factor_str, fontsize=11, ha='center', va='center',
                color=fc, transform=ax.transAxes)

    ax.set_title('Difference-of-Squares Factorization Table', fontsize=16, color=DARK,
                 fontweight='bold', pad=20)

    save(fig, 'fig02_factor_table.png')


# ============================================================
# FIG 3: Berggren ternary tree (3 levels)
# ============================================================
def fig03_berggren_tree():
    fig, ax = plt.subplots(1, 1, figsize=(18, 11))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    root = (3, 4, 5)
    children = berggren_children(root)
    grandchildren = [berggren_children(c) for c in children]

    positions = {root: (9, 9)}
    l1_xs = [3, 9, 15]
    branch_labels_1 = ['$B_1$', '$B_2$', '$B_3$']
    for i, c in enumerate(children):
        positions[c] = (l1_xs[i], 5.5)

    l2_base = [0.5, 3, 5.5, 6.5, 9, 11.5, 12.5, 15, 17.5]
    idx = 0
    for i, gc_set in enumerate(grandchildren):
        for j, gc in enumerate(gc_set):
            positions[gc] = (l2_base[idx], 2)
            idx += 1

    branch_colors = [ACCENT1, ACCENT2, ACCENT3]
    for i, c in enumerate(children):
        px, py = positions[root]
        cx, cy = positions[c]
        ax.annotate('', xy=(cx, cy + 0.6), xytext=(px, py - 0.4),
                    arrowprops=dict(arrowstyle='->', color=branch_colors[i], lw=2.5))
        mx, my = (px + cx) / 2, (py + cy) / 2
        offset = -0.8 if i == 0 else (0.8 if i == 2 else 0)
        ax.text(mx + offset, my + 0.3, branch_labels_1[i], fontsize=12,
                ha='center', color=branch_colors[i], fontweight='bold')

    idx = 0
    for i, gc_set in enumerate(grandchildren):
        for j, gc in enumerate(gc_set):
            px, py = positions[children[i]]
            cx, cy = positions[gc]
            ax.annotate('', xy=(cx, cy + 0.6), xytext=(px, py - 0.4),
                        arrowprops=dict(arrowstyle='->', color=branch_colors[j], lw=1.8, alpha=0.7))
            idx += 1

    all_nodes = [root] + list(children)
    for gc_set in grandchildren:
        all_nodes.extend(gc_set)

    for node in all_nodes:
        x, y = positions[node]
        circ = plt.Circle((x, y), 0.9, facecolor=CREAM, edgecolor=DARK,
                           linewidth=2, zorder=10)
        ax.add_patch(circ)
        label = f'({node[0]},{node[1]},{node[2]})'
        fs = 8 if max(abs(v) for v in node) > 50 else 9
        ax.text(x, y, label, fontsize=fs, ha='center', va='center',
                color=DARK, fontweight='bold', zorder=11)

    for gc_set in grandchildren:
        for gc in gc_set:
            x, y = positions[gc]
            for dy in [0.4, 0.6, 0.8]:
                ax.plot(x, y - 0.9 - dy, '.', color=SLATE, markersize=4)

    ax.set_xlim(-1.5, 19.5)
    ax.set_ylim(0, 10.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('The Berggren Tree of Pythagorean Triples', fontsize=18,
                 color=DARK, fontweight='bold', pad=15)

    save(fig, 'fig03_berggren_tree.png')


# ============================================================
# FIG 4: Matrix-vector multiplication B2 x (3,4,5)
# ============================================================
def fig04_matrix_multiply():
    fig, ax = plt.subplots(1, 1, figsize=(12, 7))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.axis('off')

    ax.text(0.5, 0.95, '$B_2 \\times (3, 4, 5)^T = (21, 20, 29)^T$',
            fontsize=20, ha='center', va='top', color=DARK, fontweight='bold',
            transform=ax.transAxes)

    ax.text(0.05, 0.72, '$B_2 =$', fontsize=16, ha='center', va='center',
            color=DARK, transform=ax.transAxes)
    draw_matrix(ax, 0.18, 0.70, [[1, 2, 2], [2, 1, 2], [2, 2, 3]], fontsize=15)

    ax.text(0.32, 0.70, '$\\times$', fontsize=22, ha='center', va='center',
            color=ACCENT1, transform=ax.transAxes)

    draw_col_vector(ax, 0.39, 0.70, [3, 4, 5], fontsize=15, color=ACCENT2)

    ax.text(0.46, 0.70, '$=$', fontsize=22, ha='center', va='center',
            color=DARK, transform=ax.transAxes)

    draw_col_vector(ax, 0.53, 0.70, [21, 20, 29], fontsize=15, color=ACCENT3)

    steps = [
        ('Row 1:', '$1 \\cdot 3 + 2 \\cdot 4 + 2 \\cdot 5 = 3 + 8 + 10 = 21$', ACCENT1),
        ('Row 2:', '$2 \\cdot 3 + 1 \\cdot 4 + 2 \\cdot 5 = 6 + 4 + 10 = 20$', ACCENT2),
        ('Row 3:', '$2 \\cdot 3 + 2 \\cdot 4 + 3 \\cdot 5 = 6 + 8 + 15 = 29$', ACCENT3),
    ]

    for i, (label, expr, color) in enumerate(steps):
        y = 0.42 - i * 0.12
        ax.text(0.55, y, label, fontsize=13, ha='left', va='center',
                color=color, fontweight='bold', transform=ax.transAxes)
        ax.text(0.66, y, expr, fontsize=13, ha='left', va='center',
                color=DARK, transform=ax.transAxes)

    box = FancyBboxPatch((0.25, 0.02), 0.50, 0.09, transform=ax.transAxes,
                         boxstyle="round,pad=0.015", facecolor=LIGHT_GREEN,
                         edgecolor=ACCENT3, linewidth=2)
    ax.add_patch(box)
    ax.text(0.50, 0.065, 'Check: $21^2 + 20^2 = 441 + 400 = 841 = 29^2$  ✓',
            fontsize=14, ha='center', va='center', color=DARK, fontweight='bold',
            transform=ax.transAxes)

    frame = FancyBboxPatch((0.02, 0.0), 0.96, 0.98, transform=ax.transAxes,
                           boxstyle="round,pad=0.02", facecolor='none',
                           edgecolor=GOLD, linewidth=3)
    ax.add_patch(frame)

    save(fig, 'fig04_matrix_multiply.png')


# ============================================================
# FIG 5: Light cone in 3D with lattice points
# ============================================================
def fig05_light_cone():
    fig = plt.figure(figsize=(12, 10))
    fig.set_facecolor(SAND)
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor(SAND)

    theta = np.linspace(0, 2 * np.pi, 80)
    c_vals = np.linspace(0, 35, 30)
    Theta, C = np.meshgrid(theta, c_vals)
    A = C * np.cos(Theta)
    B = C * np.sin(Theta)

    ax.plot_surface(A, B, C, alpha=0.08, color=ACCENT2, edgecolor='none')
    ax.plot_surface(A, B, -C, alpha=0.04, color=ACCENT2, edgecolor='none')

    triples = [(3, 4, 5), (5, 12, 13), (21, 20, 29), (15, 8, 17),
               (7, 24, 25), (8, 15, 17), (9, 12, 15)]

    for a, b, c in triples:
        ax.scatter([a], [b], [c], color=ACCENT1, s=80, zorder=10, edgecolor=DARK, linewidth=1)
        ax.text(a + 1, b + 1, c + 1, f'({a},{b},{c})', fontsize=8, color=DARK)

    tree_edges = [
        ((3, 4, 5), (5, 12, 13)),
        ((3, 4, 5), (21, 20, 29)),
        ((3, 4, 5), (15, 8, 17)),
    ]
    for (a1, b1, c1), (a2, b2, c2) in tree_edges:
        ax.plot([a1, a2], [b1, b2], [c1, c2], '--', color=GOLD, linewidth=2, alpha=0.8)

    ax.set_xlabel('$a$', fontsize=14, color=DARK)
    ax.set_ylabel('$b$', fontsize=14, color=DARK)
    ax.set_zlabel('$c$', fontsize=14, color=DARK)
    ax.set_title('Pythagorean Triples on the Light Cone $a^2 + b^2 = c^2$',
                 fontsize=15, color=DARK, fontweight='bold', pad=15)
    ax.view_init(elev=20, azim=35)

    save(fig, 'fig05_light_cone.png')


# ============================================================
# FIG 6: Whimsical photon at blackboard
# ============================================================
def fig06_photon_blackboard():
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.axis('off')

    board = FancyBboxPatch((0.15, 0.25), 0.70, 0.55, boxstyle="round,pad=0.02",
                           facecolor='#2D4A3E', edgecolor='#5D3A1A', linewidth=5,
                           transform=ax.transAxes, zorder=1)
    ax.add_patch(board)

    ax.text(0.50, 0.60, '$B_i^T \\, Q \\, B_i = Q$',
            fontsize=28, ha='center', va='center', color='white',
            fontweight='bold', transform=ax.transAxes, zorder=2)

    ax.text(0.50, 0.42, '"This is why I always travel\nat the same speed."',
            fontsize=14, ha='center', va='center', color=GLOW,
            style='italic', transform=ax.transAxes, zorder=2)

    photon_x, photon_y = 0.22, 0.18
    glow_circle = plt.Circle((photon_x, photon_y), 0.06, facecolor=GLOW,
                              alpha=0.3, transform=ax.transAxes, zorder=3)
    ax.add_patch(glow_circle)
    photon = plt.Circle((photon_x, photon_y), 0.035, facecolor=GLOW,
                         edgecolor=ACCENT5, linewidth=2,
                         transform=ax.transAxes, zorder=4)
    ax.add_patch(photon)

    for dx in [-0.012, 0.012]:
        eye_bg = plt.Circle((photon_x + dx, photon_y + 0.01), 0.008,
                             facecolor='white', edgecolor=DARK, linewidth=1,
                             transform=ax.transAxes, zorder=5)
        ax.add_patch(eye_bg)
        pupil = plt.Circle((photon_x + dx + 0.003, photon_y + 0.013), 0.004,
                            facecolor=DARK, transform=ax.transAxes, zorder=6)
        ax.add_patch(pupil)

    cap_x = [photon_x - 0.04, photon_x + 0.04, photon_x + 0.03, photon_x - 0.03]
    cap_y = [photon_y + 0.035, photon_y + 0.035, photon_y + 0.05, photon_y + 0.05]
    cap = plt.Polygon(list(zip(cap_x, cap_y)), facecolor=DARK,
                       transform=ax.transAxes, zorder=6)
    ax.add_patch(cap)
    ax.plot([photon_x + 0.04, photon_x + 0.055, photon_x + 0.05],
            [photon_y + 0.035, photon_y + 0.02, photon_y + 0.005],
            color=GOLD, linewidth=2, transform=ax.transAxes, zorder=6)

    ax.text(0.50, 0.05, '"Even light obeys the Berggren matrices."',
            fontsize=13, ha='center', va='center', color=SLATE,
            style='italic', fontweight='bold', transform=ax.transAxes)

    save(fig, 'fig06_photon_blackboard.png')


# ============================================================
# FIG 7: Q-meter flow diagram
# ============================================================
def fig07_q_meter():
    fig, ax = plt.subplots(1, 1, figsize=(14, 7))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.axis('off')

    ax.text(0.50, 0.95, 'The Lorentz Form Is a Conserved Quantity',
            fontsize=18, ha='center', va='top', color=DARK, fontweight='bold',
            transform=ax.transAxes)

    ax.text(0.08, 0.65, '$(a, b, c)$', fontsize=16, ha='center', va='center',
            color=ACCENT2, fontweight='bold', transform=ax.transAxes)

    ax.annotate('', xy=(0.28, 0.65), xytext=(0.16, 0.65),
                arrowprops=dict(arrowstyle='->', color=DARK, lw=2.5),
                transform=ax.transAxes)

    box = FancyBboxPatch((0.28, 0.55), 0.20, 0.20, transform=ax.transAxes,
                         boxstyle="round,pad=0.02", facecolor=SLATE,
                         edgecolor=DARK, linewidth=2)
    ax.add_patch(box)
    ax.text(0.38, 0.65, '$B_2$', fontsize=22, ha='center', va='center',
            color='white', fontweight='bold', transform=ax.transAxes)

    ax.annotate('', xy=(0.60, 0.65), xytext=(0.50, 0.65),
                arrowprops=dict(arrowstyle='->', color=DARK, lw=2.5),
                transform=ax.transAxes)

    ax.text(0.80, 0.65,
            '$(a{+}2b{+}2c,\\;2a{+}b{+}2c,\\;2a{+}2b{+}3c)$',
            fontsize=12, ha='center', va='center', color=ACCENT3, fontweight='bold',
            transform=ax.transAxes)

    for (gx, gy, label) in [(0.10, 0.82, 'Input $Q$-meter'), (0.80, 0.82, 'Output $Q$-meter')]:
        gauge = plt.Circle((gx, gy), 0.05, facecolor=CREAM, edgecolor=DARK,
                            linewidth=2, transform=ax.transAxes, zorder=3)
        ax.add_patch(gauge)
        ax.plot([gx, gx], [gy, gy + 0.04], color=ACCENT1, linewidth=2.5,
                transform=ax.transAxes, zorder=4)
        ax.text(gx, gy - 0.06, '0', fontsize=12, ha='center', color=ACCENT1,
                fontweight='bold', transform=ax.transAxes)
        ax.text(gx, gy + 0.07, label, fontsize=10, ha='center', color=SLATE,
                transform=ax.transAxes)

    ax.plot([0.05, 0.95], [0.38, 0.38], color=DARK, linewidth=1, alpha=0.3,
            transform=ax.transAxes)
    ax.text(0.50, 0.33, 'Non-null example:', fontsize=13, ha='center',
            color=SLATE, fontweight='bold', transform=ax.transAxes)

    ax.text(0.12, 0.22, '$(1, 1, 0)$\n$Q = 1+1-0 = 2$', fontsize=12,
            ha='center', va='center', color=ACCENT4, transform=ax.transAxes)
    ax.annotate('', xy=(0.35, 0.22), xytext=(0.22, 0.22),
                arrowprops=dict(arrowstyle='->', color=DARK, lw=2),
                transform=ax.transAxes)
    box2 = FancyBboxPatch((0.35, 0.16), 0.14, 0.12, transform=ax.transAxes,
                          boxstyle="round,pad=0.015", facecolor=SLATE,
                          edgecolor=DARK, linewidth=1.5)
    ax.add_patch(box2)
    ax.text(0.42, 0.22, '$B_2$', fontsize=16, ha='center', va='center',
            color='white', fontweight='bold', transform=ax.transAxes)
    ax.annotate('', xy=(0.60, 0.22), xytext=(0.50, 0.22),
                arrowprops=dict(arrowstyle='->', color=DARK, lw=2),
                transform=ax.transAxes)
    result = B2 @ np.array([1, 1, 0])
    q_out = result[0]**2 + result[1]**2 - result[2]**2
    ax.text(0.75, 0.22,
            f'$({result[0]}, {result[1]}, {result[2]})$\n$Q = {result[0]}^2+{result[1]}^2-{result[2]}^2 = {q_out}$',
            fontsize=12, ha='center', va='center', color=ACCENT4, transform=ax.transAxes)

    ax.text(0.90, 0.22, '$Q=2$ ✓', fontsize=14, ha='center', va='center',
            color=ACCENT3, fontweight='bold', transform=ax.transAxes)

    save(fig, 'fig07_q_meter.png')


# ============================================================
# FIG 8: Subway-map style Berggren tree
# ============================================================
def fig08_subway_map():
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    root = (3, 4, 5)
    ch = berggren_children(root)
    gch = [berggren_children(c) for c in ch]

    positions = {root: (8, 9)}
    l1_xs = [3, 8, 13]
    for i, c in enumerate(ch):
        positions[c] = (l1_xs[i], 6)

    l2_xs = [0.5, 3, 5.5, 6.5, 8, 9.5, 10.5, 13, 15.5]
    idx = 0
    for i, gc_set in enumerate(gch):
        for j, gc in enumerate(gc_set):
            positions[gc] = (l2_xs[idx], 3)
            idx += 1

    line_colors = {0: ACCENT1, 1: ACCENT2, 2: ACCENT3}
    line_labels = {0: 'L', 1: 'M', 2: 'R'}

    for i, c in enumerate(ch):
        px, py = positions[root]
        cx, cy = positions[c]
        lw = 5 if i == 1 else 3
        ax.plot([px, cx], [py, cy], color=line_colors[i], linewidth=lw, zorder=2,
                solid_capstyle='round')
        mx, my = (px + cx) / 2, (py + cy) / 2
        ax.text(mx + (0.6 if i != 1 else 0), my + 0.4, line_labels[i],
                fontsize=14, ha='center', color=line_colors[i], fontweight='bold',
                bbox=dict(facecolor=SAND, edgecolor='none', alpha=0.8))

    idx = 0
    for i, gc_set in enumerate(gch):
        for j, gc in enumerate(gc_set):
            px, py = positions[ch[i]]
            cx, cy = positions[gc]
            is_highlight = (i == 1 and j == 1)
            lw = 4 if is_highlight else 2.5
            ax.plot([px, cx], [py, cy], color=line_colors[j], linewidth=lw, zorder=2,
                    solid_capstyle='round')
            idx += 1

    path_nodes = [root, ch[1]]
    b2_child_of_middle = gch[1]
    path_nodes.append(b2_child_of_middle[0])

    for k in range(len(path_nodes) - 1):
        px, py = positions[path_nodes[k]]
        cx, cy = positions[path_nodes[k + 1]]
        ax.plot([px, cx], [py, cy], color=ACCENT1, linewidth=6, alpha=0.3, zorder=1,
                solid_capstyle='round')

    ax.text(5.5, 7.8, 'Route ML', fontsize=13, ha='center', color=ACCENT1,
            fontweight='bold',
            bbox=dict(facecolor=LIGHT_RED, edgecolor=ACCENT1, boxstyle='round,pad=0.3'))

    all_nodes = [root] + list(ch)
    for gc_set in gch:
        all_nodes.extend(gc_set)

    for node in all_nodes:
        x, y = positions[node]
        circ = plt.Circle((x, y), 0.7, facecolor='white', edgecolor=DARK,
                           linewidth=2.5, zorder=5)
        ax.add_patch(circ)
        label = f'({node[0]},{node[1]},{node[2]})'
        fs = 7 if max(abs(v) for v in node) > 60 else 8
        ax.text(x, y, label, fontsize=fs, ha='center', va='center',
                color=DARK, fontweight='bold', zorder=6)

    cx, cy = 14.5, 8.5
    ax.text(cx, cy + 0.6, 'L', fontsize=11, ha='center', color=ACCENT1, fontweight='bold')
    ax.text(cx + 0.6, cy, 'R', fontsize=11, ha='center', color=ACCENT3, fontweight='bold')
    ax.text(cx, cy - 0.6, 'M', fontsize=11, ha='center', color=ACCENT2, fontweight='bold')
    compass = plt.Circle((cx, cy), 0.9, facecolor='none', edgecolor=DARK,
                          linewidth=1.5, zorder=3)
    ax.add_patch(compass)

    ax.set_xlim(-1.5, 17.5)
    ax.set_ylim(1.5, 10.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Berggren Tree — Subway Map', fontsize=18, color=DARK,
                 fontweight='bold', pad=15)

    save(fig, 'fig08_subway_map.png')


# ============================================================
# FIG 9: Wormhole / shortcut — matrix power jump
# ============================================================
def fig09_wormhole():
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.axis('off')

    root = (3, 4, 5)
    ch = berggren_children(root)
    tree_nodes = {root: (2.5, 7)}
    l1 = [(1.5, 5), (2.5, 5), (3.5, 5)]
    for i, c in enumerate(ch):
        tree_nodes[c] = l1[i]
    gch = [berggren_children(c) for c in ch]
    l2_xs = np.linspace(0.5, 4.5, 9)
    idx = 0
    for gc_set in gch:
        for gc in gc_set:
            tree_nodes[gc] = (l2_xs[idx], 3)
            idx += 1

    for i, c in enumerate(ch):
        px, py = tree_nodes[root]
        cx, cy = tree_nodes[c]
        ax.plot([px, cx], [py, cy], color=ACCENT3, linewidth=1.5)
    for i, gc_set in enumerate(gch):
        for gc in gc_set:
            px, py = tree_nodes[ch[i]]
            cx, cy = tree_nodes[gc]
            ax.plot([px, cx], [py, cy], color=ACCENT3, linewidth=1)

    for node, (x, y) in tree_nodes.items():
        circ = plt.Circle((x, y), 0.3, facecolor=CREAM, edgecolor=DARK,
                           linewidth=1.5, zorder=5)
        ax.add_patch(circ)

    ax.text(2.5, 7, '(3,4,5)', fontsize=7, ha='center', va='center', color=DARK,
            fontweight='bold', zorder=6)

    ax.text(2.5, 1.5, 'Full tree\n(3 levels shown)', fontsize=11, ha='center',
            color=SLATE, style='italic')

    dest_x, dest_y = 12, 5
    circ = plt.Circle((dest_x, dest_y), 0.5, facecolor=GLOW, edgecolor=ACCENT5,
                       linewidth=3, zorder=5, alpha=0.8)
    ax.add_patch(circ)
    ax.text(dest_x, dest_y, '?', fontsize=16, ha='center', va='center',
            color=DARK, fontweight='bold', zorder=6)
    ax.text(dest_x, dest_y - 1, 'Node at depth\n1,000,000', fontsize=11,
            ha='center', color=DARK, fontweight='bold')

    for t in np.linspace(0.1, 0.9, 40):
        x = 4 + t * 7
        y = 7 - t * 2 + 0.5 * np.sin(t * 15)
        alpha = 0.1 + 0.2 * (1 - abs(t - 0.5) * 2)
        ax.plot(x, y, 'o', color=ACCENT2, markersize=3, alpha=alpha)

    arrow = FancyArrowPatch((3.5, 7), (11.5, 5.3),
                             connectionstyle="arc3,rad=0.3",
                             arrowstyle='->', mutation_scale=25,
                             color=ACCENT1, linewidth=3, zorder=4)
    ax.add_patch(arrow)
    ax.text(7.5, 7.8, '$B_2^{1{,}000{,}000}$', fontsize=18, ha='center',
            color=ACCENT1, fontweight='bold',
            bbox=dict(facecolor=SAND, edgecolor=ACCENT1, boxstyle='round,pad=0.3'))

    counter_box = FancyBboxPatch((10.5, 1.5), 3, 1.2, boxstyle="round,pad=0.1",
                                  facecolor=CREAM, edgecolor=DARK, linewidth=2)
    ax.add_patch(counter_box)
    ax.text(12, 2.3, 'Only 20 matrix\nmultiplications!', fontsize=11,
            ha='center', va='center', color=ACCENT1, fontweight='bold')

    ax.set_xlim(-0.5, 14.5)
    ax.set_ylim(0.5, 9)
    ax.set_aspect('equal')
    ax.set_title('The Wormhole Shortcut: Repeated Squaring',
                 fontsize=18, color=DARK, fontweight='bold', pad=15)

    save(fig, 'fig09_wormhole.png')


# ============================================================
# FIG 10: Elevator — inverse matrices going up the tree
# ============================================================
def fig10_elevator():
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    root = (3, 4, 5)
    ch = berggren_children(root)
    gch = [berggren_children(c) for c in ch]

    positions = {root: (7, 9)}
    l1_xs = [3, 7, 11]
    for i, c in enumerate(ch):
        positions[c] = (l1_xs[i], 6)

    l2_xs = [1, 3, 5, 5.5, 7, 8.5, 9, 11, 13]
    idx = 0
    for i, gc_set in enumerate(gch):
        for j, gc in enumerate(gc_set):
            positions[gc] = (l2_xs[idx], 3)
            idx += 1

    for i, c in enumerate(ch):
        px, py = positions[root]
        cx, cy = positions[c]
        ax.plot([px, cx], [py, cy], color=ACCENT3, linewidth=2, alpha=0.4)

    for i, gc_set in enumerate(gch):
        for gc in gc_set:
            px, py = positions[ch[i]]
            cx, cy = positions[gc]
            ax.plot([px, cx], [py, cy], color=ACCENT3, linewidth=1.5, alpha=0.4)

    all_nodes = [root] + list(ch)
    for gc_set in gch:
        all_nodes.extend(gc_set)
    for node in all_nodes:
        x, y = positions[node]
        circ = plt.Circle((x, y), 0.65, facecolor=CREAM, edgecolor=DARK,
                           linewidth=1.5, zorder=5)
        ax.add_patch(circ)
        label = f'({node[0]},{node[1]},{node[2]})'
        fs = 7 if max(abs(v) for v in node) > 60 else 8
        ax.text(x, y, label, fontsize=fs, ha='center', va='center',
                color=DARK, fontweight='bold', zorder=6)

    elevator_path = [gch[1][0], ch[1], root]
    inv_labels = ['$B_1^{-1}$', '$B_2^{-1}$']

    for k in range(len(elevator_path) - 1):
        cx, cy = positions[elevator_path[k]]
        px, py = positions[elevator_path[k + 1]]
        offset = 0.8
        arrow = FancyArrowPatch((cx + offset, cy + 0.7), (px + offset, py - 0.7),
                                arrowstyle='->', mutation_scale=20,
                                color=GOLD, linewidth=3, zorder=8)
        ax.add_patch(arrow)

        mx = (cx + px) / 2 + offset + 0.6
        my = (cy + py) / 2
        ax.text(mx, my, inv_labels[k], fontsize=13, ha='left', va='center',
                color=GOLD, fontweight='bold',
                bbox=dict(facecolor=SAND, edgecolor=GOLD, boxstyle='round,pad=0.2'))

    for node in elevator_path:
        x, y = positions[node]
        highlight = plt.Circle((x, y), 0.72, facecolor='none', edgecolor=ACCENT1,
                                linewidth=3, zorder=7)
        ax.add_patch(highlight)

    ax.set_xlim(-1, 15)
    ax.set_ylim(1.5, 10.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('The Elevator: Climbing Up the Tree with Inverse Matrices',
                 fontsize=17, color=DARK, fontweight='bold', pad=15)

    save(fig, 'fig10_elevator.png')


# ============================================================
# FIG 11: Lorentz adjoint — B2 and B2^{-1} side by side
# ============================================================
def fig11_lorentz_adjoint():
    fig, ax = plt.subplots(1, 1, figsize=(14, 6))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.axis('off')

    # B2 matrix using draw_matrix helper
    ax.text(0.07, 0.72, '$B_2 =$', fontsize=16, ha='center', va='center',
            color=DARK, transform=ax.transAxes)
    draw_matrix(ax, 0.19, 0.70, [[1, 2, 2], [2, 1, 2], [2, 2, 3]], fontsize=14)

    # Formula in the middle
    ax.text(0.50, 0.70, '$B_2^{-1} = Q \\, B_2^T \\, Q$',
            fontsize=18, ha='center', va='center', color=ACCENT1, fontweight='bold',
            transform=ax.transAxes,
            bbox=dict(facecolor=LIGHT_RED, edgecolor=ACCENT1, boxstyle='round,pad=0.3',
                      alpha=0.5))

    # B2^{-1} matrix
    Q = np.diag([1, 1, -1])
    B2inv = Q @ B2.T @ Q
    ax.text(0.73, 0.72, '$B_2^{-1} =$', fontsize=16, ha='center', va='center',
            color=DARK, transform=ax.transAxes)
    draw_matrix(ax, 0.87, 0.70,
                [[int(B2inv[i, j]) for j in range(3)] for i in range(3)],
                fontsize=14)

    # Three-step process
    steps_y = 0.28
    step_texts = [
        ('Step 1:', 'Multiply by $Q$\n(flip sign of row 3)', ACCENT2),
        ('Step 2:', 'Transpose', ACCENT3),
        ('Step 3:', 'Multiply by $Q$\n(flip sign of col 3)', ACCENT4),
    ]
    for i, (label, desc, color) in enumerate(step_texts):
        x = 0.20 + i * 0.28
        ax.text(x, steps_y + 0.08, label, fontsize=12, ha='center', color=color,
                fontweight='bold', transform=ax.transAxes)
        ax.text(x, steps_y - 0.05, desc, fontsize=10, ha='center', color=SLATE,
                transform=ax.transAxes)

    for i in range(2):
        x1 = 0.33 + i * 0.28
        ax.annotate('', xy=(x1 + 0.05, steps_y), xytext=(x1 - 0.05, steps_y),
                    arrowprops=dict(arrowstyle='->', color=DARK, lw=2),
                    transform=ax.transAxes)

    ax.text(0.50, 0.05,
            '"The inverse is the original seen from the other side of the looking glass."',
            fontsize=12, ha='center', color=SLATE, style='italic',
            transform=ax.transAxes)

    save(fig, 'fig11_lorentz_adjoint.png')


# ============================================================
# FIG 12: Bar chart — hypotenuse growth by branch
# ============================================================
def fig12_hypotenuse_bars():
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    def follow_branch(matrix, start, levels):
        hyps = [start[2]]
        t = np.array(start)
        for _ in range(levels):
            t = matrix @ t
            hyps.append(t[2])
        return hyps

    left_hyps = follow_branch(B1, np.array([3, 4, 5]), 4)
    mid_hyps = follow_branch(B2, np.array([3, 4, 5]), 4)
    right_hyps = follow_branch(B3, np.array([3, 4, 5]), 4)

    x = np.arange(5)
    width = 0.25

    bars_l = ax.bar(x - width, left_hyps, width, label='Left ($B_1$)', color=ACCENT1,
                    edgecolor=DARK, linewidth=1.2)
    bars_m = ax.bar(x, mid_hyps, width, label='Middle ($B_2$)', color=ACCENT2,
                    edgecolor=DARK, linewidth=1.2)
    bars_r = ax.bar(x + width, right_hyps, width, label='Right ($B_3$)', color=ACCENT3,
                    edgecolor=DARK, linewidth=1.2)

    for bars in [bars_l, bars_m, bars_r]:
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h + 50,
                    f'{int(h)}', ha='center', va='bottom', fontsize=8,
                    color=DARK, fontweight='bold')

    ax.set_xlabel('Level in tree', fontsize=14, color=DARK)
    ax.set_ylabel('Hypotenuse $c$', fontsize=14, color=DARK)
    ax.set_xticks(x)
    ax.set_xticklabels([f'Level {i}' for i in range(5)])
    ax.legend(fontsize=12, loc='upper left')
    ax.set_title('Hypotenuse Growth by Branch — Middle Branch Dominates',
                 fontsize=16, color=DARK, fontweight='bold', pad=15)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    save(fig, 'fig12_hypotenuse_bars.png')


# ============================================================
# FIG 13: Number line — middle-branch recurrence
# ============================================================
def fig13_chebyshev_line():
    fig, ax = plt.subplots(1, 1, figsize=(14, 5))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    hyps = [5, 29, 169, 985, 5741]
    log_pos = [np.log10(h) for h in hyps]
    lo, hi = log_pos[0], log_pos[-1]
    xs = [1 + 12 * (lp - lo) / (hi - lo) for lp in log_pos]

    ax.plot([0, 14], [2, 2], color=DARK, linewidth=2)

    for i, (x, h) in enumerate(zip(xs, hyps)):
        ax.plot([x, x], [1.8, 2.2], color=DARK, linewidth=2)
        ax.plot(x, 2, 'o', color=ACCENT2, markersize=12, zorder=5,
                markeredgecolor=DARK, markeredgewidth=1.5)
        label = f'${h}$'
        if h == 169:
            label = '$169 = 13^2$'
        ax.text(x, 1.3, label, fontsize=12, ha='center', color=DARK, fontweight='bold')
        ax.text(x, 2.5, f'$c_{i}$', fontsize=11, ha='center', color=SLATE)

    for i in range(len(hyps) - 1):
        x1, x2 = xs[i], xs[i + 1]
        mid = (x1 + x2) / 2
        arrow = FancyArrowPatch((x1 + 0.2, 2.3), (x2 - 0.2, 2.3),
                                connectionstyle="arc3,rad=-0.4",
                                arrowstyle='->', mutation_scale=15,
                                color=ACCENT5, linewidth=2, zorder=4)
        ax.add_patch(arrow)

        if i > 0:
            ax.text(mid, 3.8 - i * 0.15, f'$6 \\times {hyps[i]} - {hyps[i-1]}$',
                    fontsize=9, ha='center', color=ACCENT5, alpha=0.9)

    ax.text((xs[1] + xs[2]) / 2, 4.2,
            '$6 \\times 29 - 5 = 169$', fontsize=13, ha='center',
            color=ACCENT1, fontweight='bold',
            bbox=dict(facecolor=LIGHT_RED, edgecolor=ACCENT1, boxstyle='round,pad=0.3'))

    box = FancyBboxPatch((xs[2] - 0.5, 0.8), 1.0, 0.8,
                          boxstyle="round,pad=0.1", facecolor=GLOW,
                          edgecolor=GOLD, linewidth=2, alpha=0.5)
    ax.add_patch(box)

    ax.set_xlim(-0.5, 14.5)
    ax.set_ylim(0.3, 5)
    ax.axis('off')
    ax.set_title('Middle-Branch Chebyshev Recurrence: $c_{n+1} = 6c_n - c_{n-1}$',
                 fontsize=16, color=DARK, fontweight='bold', pad=15)

    save(fig, 'fig13_chebyshev_line.png')


# ============================================================
# FIG 14: Three subtrees — no duplicates
# ============================================================
def fig14_three_subtrees():
    fig, axes = plt.subplots(1, 3, figsize=(16, 7))
    fig.set_facecolor(SAND)

    root = (3, 4, 5)
    branch_names = ['Left ($B_1$)', 'Middle ($B_2$)', 'Right ($B_3$)']
    branch_colors = [ACCENT1, ACCENT2, ACCENT3]
    matrices = [B1, B2, B3]

    for idx, ax in enumerate(axes):
        ax.set_facecolor(SAND)
        ax.axis('off')

        child = tuple((matrices[idx] @ np.array(root)).tolist())
        grandchildren = [tuple((m @ np.array(child)).tolist()) for m in matrices]

        ax.add_patch(plt.Circle((3, 8), 0.6, facecolor='#CCCCCC', edgecolor=DARK,
                                 linewidth=2, zorder=5))
        ax.text(3, 8, f'({root[0]},{root[1]},{root[2]})', fontsize=8, ha='center',
                va='center', color=DARK, fontweight='bold', zorder=6)

        ax.plot([3, 3], [7.4, 6.1], color=branch_colors[idx], linewidth=2.5)
        ax.add_patch(plt.Circle((3, 5.5), 0.6, facecolor=branch_colors[idx],
                                 edgecolor=DARK, linewidth=2, alpha=0.3, zorder=5))
        label = f'({child[0]},{child[1]},{child[2]})'
        ax.text(3, 5.5, label, fontsize=7, ha='center', va='center',
                color=DARK, fontweight='bold', zorder=6)

        gc_xs = [1.5, 3, 4.5]
        for j, gc in enumerate(grandchildren):
            ax.plot([3, gc_xs[j]], [4.9, 3.6], color=branch_colors[idx],
                    linewidth=1.5, alpha=0.7)
            ax.add_patch(plt.Circle((gc_xs[j], 3), 0.6, facecolor=branch_colors[idx],
                                     edgecolor=DARK, linewidth=1.5, alpha=0.2, zorder=5))
            gc_label = f'({gc[0]},{gc[1]},{gc[2]})'
            fs = 6 if max(abs(v) for v in gc) > 60 else 7
            ax.text(gc_xs[j], 3, gc_label, fontsize=fs, ha='center', va='center',
                    color=DARK, fontweight='bold', zorder=6)

        ax.set_xlim(-0.5, 6.5)
        ax.set_ylim(1.5, 9.5)
        ax.set_title(branch_names[idx], fontsize=14, color=branch_colors[idx],
                     fontweight='bold')

    fig.text(0.5, 0.08, 'The three subtrees never share a node',
             fontsize=14, ha='center', color=DARK, fontweight='bold', style='italic')

    fig.suptitle('Three Families That Never Intermarry', fontsize=18,
                 color=DARK, fontweight='bold', y=0.98)

    save(fig, 'fig14_three_subtrees.png')


# ============================================================
# FIG 15: Factoring flowchart
# ============================================================
def fig15_factoring_flowchart():
    fig, ax = plt.subplots(1, 1, figsize=(8, 14))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.axis('off')

    steps = [
        (0.5, 0.92, 'Input: A composite\nnumber N', 'box', LIGHT_BLUE),
        (0.5, 0.76, 'Step 1: Find a Pythagorean\ntriple (a, b, c) with a = N', 'box', CREAM),
        (0.5, 0.60, 'Step 2: Compute\nc - b  and  c + b', 'box', CREAM),
        (0.5, 0.44, 'Step 3: Compute\ngcd(c - b, N)', 'box', CREAM),
        (0.5, 0.28, 'Is 1 < gcd < N ?', 'diamond', LIGHT_RED),
        (0.5, 0.10, 'Nontrivial factor\nfound!', 'box', LIGHT_GREEN),
    ]

    for i, (x, y, text, shape, color) in enumerate(steps):
        if shape == 'box':
            w, h = 0.55, 0.09
            box = FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                  boxstyle="round,pad=0.015",
                                  facecolor=color, edgecolor=DARK, linewidth=2,
                                  transform=ax.transAxes, zorder=3)
            ax.add_patch(box)
        elif shape == 'diamond':
            w, h = 0.32, 0.08
            diamond_x = [x, x + w / 2, x, x - w / 2]
            diamond_y = [y + h, y, y - h, y]
            diamond = plt.Polygon(list(zip(diamond_x, diamond_y)),
                                   facecolor=color, edgecolor=DARK, linewidth=2,
                                   transform=ax.transAxes, zorder=3)
            ax.add_patch(diamond)

        ax.text(x, y, text, fontsize=11, ha='center', va='center',
                color=DARK, fontweight='bold', transform=ax.transAxes, zorder=4)

        if i < len(steps) - 1:
            if shape == 'diamond':
                start_y = y - 0.08
            else:
                start_y = y - 0.045
            next_shape = steps[i + 1][3]
            next_y = steps[i + 1][1]
            if next_shape == 'diamond':
                end_y = next_y + 0.08
            else:
                end_y = next_y + 0.045

            ax.annotate('', xy=(x, end_y), xytext=(x, start_y),
                        arrowprops=dict(arrowstyle='->', color=DARK, lw=2),
                        transform=ax.transAxes)

    ax.text(0.55, 0.19, 'Yes', fontsize=12, color=ACCENT3, fontweight='bold',
            transform=ax.transAxes)

    ax.annotate('', xy=(0.82, 0.76), xytext=(0.82, 0.28),
                arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=2,
                                connectionstyle="arc3,rad=0.3"),
                transform=ax.transAxes)
    ax.text(0.90, 0.52, 'No —\nTry another\ntriple', fontsize=10,
            ha='center', color=ACCENT1, fontweight='bold', transform=ax.transAxes)

    ax.set_title('The Pythagorean Factoring Algorithm', fontsize=16,
                 color=DARK, fontweight='bold', pad=10)

    save(fig, 'fig15_factoring_flowchart.png')


# ============================================================
# FIG 16: Worked example — (21,20,29) → factor 21
# ============================================================
def fig16_worked_example():
    fig, ax = plt.subplots(1, 1, figsize=(10, 12))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.axis('off')

    tri_x = [2, 6, 2, 2]
    tri_y = [6.5, 6.5, 10.7, 6.5]
    ax.plot(tri_x, tri_y, color=DARK, linewidth=2.5, zorder=5)
    ax.fill(tri_x[:3], tri_y[:3], alpha=0.08, color=ACCENT2)

    sq = 0.25
    ax.plot([2 + sq, 2 + sq, 2], [6.5, 6.5 + sq, 6.5 + sq], color=DARK, linewidth=1.5)

    ax.text(4, 6.0, '20', fontsize=14, ha='center', color=DARK, fontweight='bold')
    ax.text(1.3, 8.6, '21', fontsize=14, ha='center', color=DARK, fontweight='bold')
    ax.text(4.5, 9.0, '29', fontsize=14, ha='center', color=DARK, fontweight='bold',
            rotation=-46)

    ax.annotate('$29 - 20 = 9$', xy=(4, 5.3), xytext=(4, 5.3),
                fontsize=16, ha='center', color=ACCENT1, fontweight='bold')

    venn_cx1, venn_cx2 = 3.0, 5.0
    venn_cy = 3.5
    venn_r = 1.3

    circle1 = plt.Circle((venn_cx1, venn_cy), venn_r, facecolor=LIGHT_RED,
                           edgecolor=ACCENT1, linewidth=2, alpha=0.4, zorder=3)
    circle2 = plt.Circle((venn_cx2, venn_cy), venn_r, facecolor=LIGHT_BLUE,
                           edgecolor=ACCENT2, linewidth=2, alpha=0.4, zorder=3)
    ax.add_patch(circle1)
    ax.add_patch(circle2)

    ax.text(venn_cx1 - 0.6, venn_cy + 0.9, 'Divisors of 9', fontsize=10,
            ha='center', color=ACCENT1, fontweight='bold')
    ax.text(venn_cx2 + 0.6, venn_cy + 0.9, 'Divisors of 21', fontsize=10,
            ha='center', color=ACCENT2, fontweight='bold')

    ax.text(venn_cx1 - 0.7, venn_cy - 0.2, '9', fontsize=12, ha='center', color=ACCENT1)
    ax.text(venn_cx2 + 0.7, venn_cy + 0.2, '7', fontsize=12, ha='center', color=ACCENT2)
    ax.text(venn_cx2 + 0.7, venn_cy - 0.3, '21', fontsize=12, ha='center', color=ACCENT2)

    overlap_x = (venn_cx1 + venn_cx2) / 2
    ax.text(overlap_x, venn_cy + 0.2, '3', fontsize=14, ha='center',
            color=DARK, fontweight='bold')
    ax.text(overlap_x, venn_cy - 0.3, '1', fontsize=12, ha='center', color=SLATE)

    gcd_circle = plt.Circle((overlap_x, venn_cy + 0.2), 0.3, facecolor='none',
                              edgecolor=ACCENT1, linewidth=3, zorder=6)
    ax.add_patch(gcd_circle)
    ax.text(overlap_x + 0.5, venn_cy + 0.6, '$\\gcd = 3$', fontsize=13,
            color=ACCENT1, fontweight='bold')

    ax.text(4, 1.3, '$21 = 3 \\times 7$', fontsize=28, ha='center',
            color=DARK, fontweight='bold',
            bbox=dict(facecolor=LIGHT_GREEN, edgecolor=ACCENT3,
                      boxstyle='round,pad=0.3', linewidth=2))

    ax.set_xlim(0, 8)
    ax.set_ylim(0.3, 11.5)
    ax.set_aspect('equal')
    ax.set_title('Worked Example: Factoring 21 via (21, 20, 29)',
                 fontsize=16, color=DARK, fontweight='bold', pad=10)

    save(fig, 'fig16_worked_example.png')


# ============================================================
# FIG 17: Chapter concept map — mappa mundi style
# ============================================================
def fig17_concept_map():
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    regions = [
        (2, 9, 'The Broken\nSquare', LIGHT_RED, 1.3),
        (7, 10, 'Berggren\nForest', LIGHT_GREEN, 1.5),
        (13, 9, 'The Light\nCone', LIGHT_BLUE, 1.4),
        (4, 5.5, 'Shortcut\nWormhole', '#E8DAEF', 1.2),
        (10, 6, 'The\nElevator', '#FAE5D3', 1.2),
        (3, 2.5, 'Chebyshev\nRidge', '#D5F5E3', 1.3),
        (11, 2.5, 'The Factoring\nForge', '#FDEBD0', 1.4),
    ]

    path_order = [0, 1, 2, 3, 4, 5, 6]
    for i in range(len(path_order) - 1):
        x1, y1 = regions[path_order[i]][0], regions[path_order[i]][1]
        x2, y2 = regions[path_order[i + 1]][0], regions[path_order[i + 1]][1]
        ax.plot([x1, x2], [y1, y2], color=GOLD, linewidth=2, linestyle='--',
                alpha=0.6, zorder=1)

    icons = ['S', 'T', 'C', 'W', 'E', 'R', 'F']  # Simple letter icons
    for idx, (x, y, name, color, radius) in enumerate(regions):
        circ = plt.Circle((x, y), radius, facecolor=color, edgecolor=DARK,
                           linewidth=2, alpha=0.6, zorder=3)
        ax.add_patch(circ)
        ax.text(x, y + 0.3, icons[idx], fontsize=22, ha='center', va='center',
                color=DARK, fontweight='bold', zorder=4)
        ax.text(x, y - 0.4, name, fontsize=10, ha='center', va='center',
                color=DARK, fontweight='bold', zorder=4)

    # Compass rose
    cx, cy = 14, 1.5
    ax.text(cx, cy, '+', fontsize=16, ha='center', va='center', color=GOLD, zorder=5)
    directions = [('Algebra', 0, 0.8), ('Geometry', 0.8, 0),
                  ('Analysis', 0, -0.8), ('Number\nTheory', -0.9, 0)]
    for label, dx, dy in directions:
        ax.text(cx + dx, cy + dy, label, fontsize=8, ha='center', va='center',
                color=SLATE, fontweight='bold')
    compass = plt.Circle((cx, cy), 1.1, facecolor='none', edgecolor=DARK,
                          linewidth=1.5, zorder=3)
    ax.add_patch(compass)

    border = FancyBboxPatch((0.3, 0.3), 15.4, 11.4, boxstyle="round,pad=0.3",
                             facecolor='none', edgecolor=DARK, linewidth=3, zorder=0)
    ax.add_patch(border)

    corner_triples = ['(3,4,5)', '(5,12,13)', '(8,15,17)', '(7,24,25)']
    corner_pos = [(1, 11), (15, 11), (1, 0.8), (15, 0.8)]
    for triple, (cx, cy) in zip(corner_triples, corner_pos):
        ax.text(cx, cy, triple, fontsize=7, ha='center', color=SLATE, alpha=0.5,
                style='italic')

    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('A Map of Chapter 3', fontsize=20, color=DARK,
                 fontweight='bold', pad=15)

    save(fig, 'fig17_concept_map.png')


# ============================================================
# Run all
# ============================================================
if __name__ == '__main__':
    print("Generating Chapter 3 illustrations...")
    fig01_broken_square()
    fig02_factor_table()
    fig03_berggren_tree()
    fig04_matrix_multiply()
    fig05_light_cone()
    fig06_photon_blackboard()
    fig07_q_meter()
    fig08_subway_map()
    fig09_wormhole()
    fig10_elevator()
    fig11_lorentz_adjoint()
    fig12_hypotenuse_bars()
    fig13_chebyshev_line()
    fig14_three_subtrees()
    fig15_factoring_flowchart()
    fig16_worked_example()
    fig17_concept_map()
    print("Done! All Chapter 3 images saved.")

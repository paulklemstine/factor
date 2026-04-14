#!/usr/bin/env python3
"""Generate all illustrations for Chapter 1: The Tree That Grew Triangles."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np
import os
from math import gcd

OUT = "images/chapter1"
os.makedirs(OUT, exist_ok=True)

# Color palette
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

def save(fig, name, dpi=200):
    fig.savefig(f"{OUT}/{name}", dpi=dpi, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  Saved {name}")


# ============================================================
# ILLUSTRATION 1: Rope-stretcher's 3-4-5 triangle
# ============================================================
def fig1_rope_triangle():
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    # Draw the main 3-4-5 triangle
    tri_x = [0, 4, 0, 0]
    tri_y = [0, 0, 3, 0]
    ax.plot(tri_x, tri_y, color=DARK, linewidth=3, zorder=5)
    ax.fill(tri_x[:3], tri_y[:3], alpha=0.1, color=ACCENT2)

    # Right angle mark
    sq = 0.3
    ax.plot([sq, sq, 0], [0, sq, sq], color=DARK, linewidth=1.5, zorder=5)

    # Knots on the rope (12 equally spaced along perimeter)
    perimeter_pts = []
    # b side: (0,0) to (4,0) — 4 segments
    for i in range(4):
        perimeter_pts.append((i * 4/4, 0))
    # c side: (4,0) to (0,3) — 5 segments
    for i in range(5):
        t = i / 5
        perimeter_pts.append((4 - 4*t, 3*t))
    # a side: (0,3) to (0,0) — 3 segments
    for i in range(3):
        t = i / 3
        perimeter_pts.append((0, 3 - 3*t))

    knot_colors = [ACCENT1, ACCENT2, ACCENT3, ACCENT5] * 3
    for idx, (kx, ky) in enumerate(perimeter_pts[:12]):
        ax.plot(kx, ky, 'o', color=knot_colors[idx % 4], markersize=10,
                markeredgecolor=DARK, markeredgewidth=1.5, zorder=10)

    # Labels
    ax.text(2, -0.5, '$b = 4$', fontsize=16, ha='center', color=DARK, fontweight='bold')
    ax.text(-0.6, 1.5, '$a = 3$', fontsize=16, ha='center', color=DARK, fontweight='bold')
    ax.text(2.5, 2.0, '$c = 5$', fontsize=16, ha='center', color=DARK, fontweight='bold', rotation=-37)

    # Ghost triangles (larger, faint)
    ghost_triples = [(5, 12, 13, 0.12), (8, 15, 17, 0.07), (7, 24, 25, 0.04)]
    for a, b, c, alph in ghost_triples:
        scale = 0.18
        gx = [0, b*scale, 0, 0]
        gy = [0, 0, a*scale, 0]
        ax.plot(gx, gy, color=ACCENT4, linewidth=1, alpha=alph*5, zorder=2)
        ax.fill(gx[:3], gy[:3], alpha=alph, color=ACCENT4)
        s2 = 0.15
        ax.plot([s2, s2, 0], [0, s2, s2], color=ACCENT4, linewidth=0.8, alpha=alph*5, zorder=2)
        ax.text(b*scale*0.4, a*scale*0.55, f'({a},{b},{c})', fontsize=7,
                alpha=min(alph*8, 1.0), color=ACCENT4, ha='center')

    ax.set_xlim(-1.5, 6)
    ax.set_ylim(-1, 5.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title("The Rope-Stretcher's Triangle", fontsize=18, color=DARK, fontweight='bold', pad=20)
    save(fig, "fig01_rope_triangle.png")


# ============================================================
# ILLUSTRATION 2: The Null Cone with Pythagorean triples
# ============================================================
def fig2_null_cone():
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    fig.set_facecolor('white')

    theta = np.linspace(0, 2*np.pi, 100)
    c_vals = np.linspace(0, 30, 50)
    Theta, C = np.meshgrid(theta, c_vals)
    A = C * np.cos(Theta)
    B = C * np.sin(Theta)
    ax.plot_surface(A, B, C, alpha=0.08, color=ACCENT2)
    ax.plot_surface(A, B, -C, alpha=0.05, color=ACCENT2)

    for t in np.linspace(0, 2*np.pi, 12, endpoint=False):
        r = np.linspace(0, 30, 50)
        ax.plot(r*np.cos(t), r*np.sin(t), r, color=ACCENT2, alpha=0.15, linewidth=0.5)

    triples_on = [(3,4,5), (5,12,13), (8,15,17), (7,24,25), (20,21,29)]
    for a, b, c in triples_on:
        ax.scatter([a], [b], [c], color=ACCENT1, s=80, zorder=10, edgecolors=DARK, linewidths=1)
        ax.text(a+0.5, b+0.5, c+1, f'({a},{b},{c})', fontsize=8, color=ACCENT1, fontweight='bold')

    off_pts = [(2, 3, 4, -3)]
    for a, b, c, q in off_pts:
        ax.scatter([a], [b], [c], color=ACCENT5, s=60, zorder=10, marker='s', edgecolors=DARK)
        ax.text(a+0.5, b+0.5, c+1, f'({a},{b},{c})\nQ={q}', fontsize=8, color=ACCENT5)

    ax.set_xlabel('$a$', fontsize=14, labelpad=10)
    ax.set_ylabel('$b$', fontsize=14, labelpad=10)
    ax.set_zlabel('$c$', fontsize=14, labelpad=10)
    ax.set_title('The Null Cone: $a^2 + b^2 = c^2$', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlim(-5, 25)
    ax.set_ylim(-5, 25)
    ax.set_zlim(0, 30)
    ax.view_init(elev=20, azim=35)
    save(fig, "fig02_null_cone.png")


# ============================================================
# ILLUSTRATION 3: Three Magic Mirrors
# ============================================================
def fig3_magic_mirrors():
    fig, axes = plt.subplots(1, 3, figsize=(15, 7))
    fig.set_facecolor(CREAM)

    mirror_data = [
        ('A', (3,4,5), (5,12,13), ACCENT1),
        ('B', (3,4,5), (21,20,29), ACCENT2),
        ('C', (3,4,5), (15,8,17), ACCENT3),
    ]

    for ax, (label, inp, out, color) in zip(axes, mirror_data):
        ax.set_facecolor(CREAM)

        # Mirror ellipse
        mirror = patches.Ellipse((0.5, 0.55), 0.85, 0.7,
                                  facecolor='#E8E8E8', edgecolor=color, linewidth=4, zorder=2)
        ax.add_patch(mirror)

        # Handle
        ax.plot([0.5, 0.5], [0.15, 0.2], color=color, linewidth=6, zorder=1)
        handle = FancyBboxPatch((0.4, 0.02), 0.2, 0.15,
                                boxstyle="round,pad=0.02", facecolor=color, edgecolor=DARK, linewidth=1.5)
        ax.add_patch(handle)

        # Input triple
        ax.text(0.5, 0.95, f'({inp[0]}, {inp[1]}, {inp[2]})', fontsize=14,
                ha='center', va='center', color=DARK, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=DARK))

        ax.annotate('', xy=(0.5, 0.82), xytext=(0.5, 0.9),
                    arrowprops=dict(arrowstyle='->', color=DARK, lw=2))

        # Output triple in mirror
        ax.text(0.5, 0.58, f'({out[0]}, {out[1]}, {out[2]})', fontsize=14,
                ha='center', va='center', color=color, fontweight='bold', zorder=5)

        # Small triangle in mirror
        a, b, c_val = out
        scale = 0.012
        tx = [0.25, 0.25 + b*scale, 0.25, 0.25]
        ty = [0.38, 0.38, 0.38 + a*scale, 0.38]
        ax.plot(tx, ty, color=color, linewidth=2, zorder=5)

        # Verification
        ax.text(0.5, 0.3, f'${out[0]}^2 + {out[1]}^2 = {out[2]}^2$', fontsize=9,
                ha='center', va='center', color=SLATE, style='italic', zorder=5)

        ax.text(0.5, -0.08, f'Mirror {label}', fontsize=14, ha='center', color=color, fontweight='bold')

        ax.set_xlim(-0.1, 1.1)
        ax.set_ylim(-0.15, 1.05)
        ax.set_aspect('equal')
        ax.axis('off')

    fig.suptitle('Three Magic Mirrors', fontsize=20, fontweight='bold', color=DARK, y=1.02)
    fig.tight_layout()
    save(fig, "fig03_magic_mirrors.png")


# ============================================================
# ILLUSTRATION 4: Matrix-vector multiplication step by step
# ============================================================
def fig4_matrix_vector():
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    fig.set_facecolor('white')
    ax.set_facecolor('white')

    # Title (avoid \begin{pmatrix})
    ax.text(0.5, 0.92, r'$\mathbf{A} \cdot (3,\;4,\;5)^\top = (5,\;12,\;13)^\top$',
            fontsize=22, ha='center', va='center', color=DARK, fontweight='bold',
            transform=ax.transAxes)

    rows = [
        ('Row 1:', r'$1(3) + (-2)(4) + 2(5)$', r'$= 3 - 8 + 10 = \mathbf{5}$', ACCENT1),
        ('Row 2:', r'$2(3) + (-1)(4) + 2(5)$', r'$= 6 - 4 + 10 = \mathbf{12}$', ACCENT2),
        ('Row 3:', r'$2(3) + (-2)(4) + 3(5)$', r'$= 6 - 8 + 15 = \mathbf{13}$', ACCENT3),
    ]

    for i, (label, calc, result, color) in enumerate(rows):
        y = 0.68 - i * 0.22
        rect = FancyBboxPatch((0.05, y - 0.07), 0.9, 0.14,
                               boxstyle="round,pad=0.02", facecolor=color, alpha=0.1,
                               edgecolor=color, linewidth=2, transform=ax.transAxes)
        ax.add_patch(rect)

        ax.text(0.08, y, label, fontsize=14, ha='left', va='center', color=color,
                fontweight='bold', transform=ax.transAxes)
        ax.text(0.22, y, calc, fontsize=14, ha='left', va='center', color=DARK,
                transform=ax.transAxes)
        ax.text(0.72, y, result, fontsize=14, ha='left', va='center', color=color,
                fontweight='bold', transform=ax.transAxes)

    ax.text(0.5, 0.1, r'Check: $5^2 + 12^2 = 25 + 144 = 169 = 13^2$  $\checkmark$',
            fontsize=14, ha='center', va='center', color=ACCENT3,
            fontweight='bold', transform=ax.transAxes,
            bbox=dict(boxstyle='round,pad=0.4', facecolor=LIGHT_GREEN, edgecolor=ACCENT3))

    ax.axis('off')
    save(fig, "fig04_matrix_vector.png")


# ============================================================
# ILLUSTRATION 5: The Berggren Tree (ternary tree)
# ============================================================
def fig5_berggren_tree():
    fig, ax = plt.subplots(1, 1, figsize=(16, 11))
    fig.set_facecolor('white')
    ax.set_facecolor('white')

    rx, ry = 8, 10

    l1 = [
        ((5, 12, 13), 2, 7, 'A'),
        ((21, 20, 29), 8, 7, 'B'),
        ((15, 8, 17), 14, 7, 'C'),
    ]

    l2 = [
        ((7, 24, 25), 0.5, 4, 'A'),
        ((55, 48, 73), 2, 4, 'B'),
        ((45, 28, 53), 3.5, 4, 'C'),
        ((39, 80, 89), 6.5, 4, 'A'),
        ((119, 120, 169), 8, 4, 'B'),
        ((77, 36, 85), 9.5, 4, 'C'),
        ((11, 60, 61), 12.5, 4, 'A'),
        ((65, 72, 97), 14, 4, 'B'),
        ((35, 12, 37), 15.5, 4, 'C'),
    ]

    def draw_node(ax, triple, x, y, sz=0.7, fs=10, color=ACCENT2):
        a, b, c = triple
        scale = sz / max(a, b)
        tx = [x - b*scale/2, x + b*scale/2, x - b*scale/2, x - b*scale/2]
        ty = [y - 0.3, y - 0.3, y - 0.3 + a*scale, y - 0.3]
        ax.fill(tx[:3], ty[:3], alpha=0.15, color=color, zorder=3)
        ax.plot(tx, ty, color=color, linewidth=1.5, zorder=4)
        ax.text(x, y + sz*0.6, f'({triple[0]}, {triple[1]}, {triple[2]})',
                fontsize=fs, ha='center', va='center', color=DARK, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor=color, alpha=0.9),
                zorder=5)

    branch_colors = {'A': ACCENT1, 'B': ACCENT2, 'C': ACCENT3}

    for (triple, x, y, label) in l1:
        color = branch_colors[label]
        ax.plot([rx, x], [ry - 0.5, y + 1], color=color, linewidth=2.5, zorder=1)
        mx, my = (rx + x) / 2, (ry - 0.5 + y + 1) / 2
        ax.text(mx - 0.3, my + 0.3, f'${label}$', fontsize=13,
                color=color, fontweight='bold', zorder=6)

    parent_l1 = {0: (2, 7), 1: (8, 7), 2: (14, 7)}
    for i, (triple, x, y, label) in enumerate(l2):
        px, py = parent_l1[i // 3]
        color = branch_colors[label]
        ax.plot([px, x], [py - 0.5, y + 1], color=color, linewidth=1.5, alpha=0.6, zorder=1)
        mx, my = (px + x) / 2, (py - 0.5 + y + 1) / 2
        ax.text(mx - 0.2, my + 0.15, f'${label}$', fontsize=9,
                color=color, alpha=0.8, zorder=6)

    draw_node(ax, (3, 4, 5), rx, ry, sz=0.8, fs=13, color=GOLD)
    for (triple, x, y, label) in l1:
        draw_node(ax, triple, x, y, sz=0.6, fs=10, color=branch_colors[label])
    for (triple, x, y, label) in l2:
        draw_node(ax, triple, x, y, sz=0.4, fs=7, color=branch_colors[label])

    for (triple, x, y, label) in l2:
        ax.text(x, y - 1.0, '...', fontsize=14, ha='center', color='gray', alpha=0.5)

    ax.set_xlim(-1, 17)
    ax.set_ylim(2.5, 11.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('The Berggren Tree of Pythagorean Triples', fontsize=20, fontweight='bold',
                 color=DARK, pad=20)
    save(fig, "fig05_berggren_tree.png")


# ============================================================
# ILLUSTRATION 6: Descent maze
# ============================================================
def fig6_descent_maze():
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    fig.set_facecolor('white')
    ax.set_facecolor('white')

    nodes = [
        ((119, 120, 169), 5, 9, 'c = 169'),
        ((21, 20, 29), 5, 6, 'c = 29'),
        ((3, 4, 5), 5, 3, 'c = 5'),
    ]

    inv_labels = [r'$B^{-1}$', r'$B^{-1}$']

    for i, ((a, b, c), x, y, clabel) in enumerate(nodes):
        is_root = (i == len(nodes) - 1)
        color = GOLD if is_root else ACCENT2
        circle = plt.Circle((x, y), 0.8, facecolor=color if is_root else 'white',
                            edgecolor=color, linewidth=3, alpha=0.3 if not is_root else 0.4, zorder=3)
        ax.add_patch(circle)

        ax.text(x, y + 0.15, f'({a}, {b}, {c})', fontsize=13, ha='center', va='center',
                color=DARK, fontweight='bold', zorder=5)
        ax.text(x, y - 0.3, clabel, fontsize=10, ha='center', va='center',
                color=SLATE, style='italic', zorder=5)

        if i < len(nodes) - 1:
            ax.annotate('', xy=(x, nodes[i+1][2] + 1.0), xytext=(x, y - 0.9),
                       arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=3))
            ax.text(x + 0.8, (y + nodes[i+1][2]) / 2, inv_labels[i],
                    fontsize=14, ha='left', va='center', color=ACCENT1, fontweight='bold')

    for r in [1.2, 1.4, 1.6]:
        glow = plt.Circle((5, 3), r, facecolor=GOLD, alpha=0.05, zorder=1)
        ax.add_patch(glow)

    ax.annotate('', xy=(8.5, 3), xytext=(8.5, 9),
               arrowprops=dict(arrowstyle='->', color=ACCENT3, lw=2, linestyle='--'))
    ax.text(9.2, 6, 'Hypotenuse\ndecreasing', fontsize=12, ha='center', va='center',
            color=ACCENT3, fontweight='bold', rotation=90)

    ax.text(5, 1.5, 'The unique root: smallest primitive triple',
            fontsize=10, ha='center', color=DARK, style='italic')

    ax.set_xlim(1, 10)
    ax.set_ylim(0.5, 10.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Descent: Every Path Leads to (3, 4, 5)', fontsize=18, fontweight='bold',
                 color=DARK, pad=20)
    save(fig, "fig06_descent_maze.png")


# ============================================================
# ILLUSTRATION 7: Factoring 667 magic trick
# ============================================================
def fig7_factoring_trick():
    fig, ax = plt.subplots(1, 1, figsize=(14, 7))
    fig.set_facecolor('white')
    ax.set_facecolor('white')

    # Card 1: 667
    card1 = FancyBboxPatch((0.5, 2.5), 2, 2.5, boxstyle="round,pad=0.15",
                            facecolor=LIGHT_RED, edgecolor=ACCENT1, linewidth=3)
    ax.add_patch(card1)
    ax.text(1.5, 4.0, '667', fontsize=32, ha='center', va='center', color=ACCENT1, fontweight='bold')
    ax.text(1.5, 3.2, '= ?', fontsize=20, ha='center', va='center', color=DARK)

    ax.annotate('', xy=(3.5, 3.75), xytext=(2.7, 3.75),
               arrowprops=dict(arrowstyle='->', color=DARK, lw=2.5))

    # Triangle
    tri_x = [4, 4, 8.5, 4]
    tri_y = [2, 5.5, 2, 2]
    ax.fill(tri_x[:3], tri_y[:3], alpha=0.1, color=ACCENT2)
    ax.plot(tri_x, tri_y, color=ACCENT2, linewidth=2.5)
    ax.plot([4.3, 4.3, 4], [2, 2.3, 2.3], color=ACCENT2, linewidth=1.5)
    ax.text(3.4, 3.75, '667', fontsize=14, ha='center', va='center', color=ACCENT1, fontweight='bold', rotation=90)
    ax.text(6.25, 1.5, '156', fontsize=14, ha='center', va='center', color=ACCENT2, fontweight='bold')
    ax.text(6.8, 4.2, '685', fontsize=14, ha='center', va='center', color=ACCENT3, fontweight='bold', rotation=-38)

    # Branch: c - b
    ax.annotate('', xy=(9.5, 5.0), xytext=(7.5, 4.5),
               arrowprops=dict(arrowstyle='->', color=ACCENT5, lw=2))
    card2 = FancyBboxPatch((9.3, 4.3), 3.2, 1.2, boxstyle="round,pad=0.1",
                            facecolor=LIGHT_GREEN, edgecolor=ACCENT3, linewidth=2)
    ax.add_patch(card2)
    ax.text(10.9, 4.9, r'$c - b = 529 = 23^2$', fontsize=13, ha='center', va='center',
            color=ACCENT3, fontweight='bold')

    # Branch: c + b
    ax.annotate('', xy=(9.5, 2.5), xytext=(7.5, 3.0),
               arrowprops=dict(arrowstyle='->', color=ACCENT5, lw=2))
    card3 = FancyBboxPatch((9.3, 1.8), 3.2, 1.2, boxstyle="round,pad=0.1",
                            facecolor=LIGHT_BLUE, edgecolor=ACCENT2, linewidth=2)
    ax.add_patch(card3)
    ax.text(10.9, 2.4, r'$c + b = 841 = 29^2$', fontsize=13, ha='center', va='center',
            color=ACCENT2, fontweight='bold')

    # Converge
    ax.annotate('', xy=(13.2, 3.75), xytext=(12.7, 4.5),
               arrowprops=dict(arrowstyle='->', color=DARK, lw=2))
    ax.annotate('', xy=(13.2, 3.75), xytext=(12.7, 2.8),
               arrowprops=dict(arrowstyle='->', color=DARK, lw=2))

    card4 = FancyBboxPatch((13, 2.8), 2.5, 2, boxstyle="round,pad=0.15",
                            facecolor=GOLD, edgecolor=DARK, linewidth=3, alpha=0.3)
    ax.add_patch(card4)
    ax.text(14.25, 4.1, '667', fontsize=20, ha='center', va='center', color=DARK, fontweight='bold')
    ax.text(14.25, 3.5, r'$= 23 \times 29$', fontsize=18, ha='center', va='center',
            color=ACCENT1, fontweight='bold')

    ax.set_xlim(-0.2, 16)
    ax.set_ylim(0.8, 5.8)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Cracking 667 with a Right Triangle', fontsize=18, fontweight='bold', color=DARK, pad=20)
    save(fig, "fig07_factoring_trick.png")


# ============================================================
# ILLUSTRATION 8: Gnomon / difference of squares
# ============================================================
def fig8_gnomon():
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    fig.set_facecolor('white')
    ax.set_facecolor('white')

    c = 8
    b = 5

    outer = patches.Rectangle((0, 0), c, c, facecolor=LIGHT_BLUE, edgecolor=ACCENT2, linewidth=2)
    ax.add_patch(outer)
    inner = patches.Rectangle((0, 0), b, b, facecolor='white', edgecolor=ACCENT2, linewidth=2, zorder=2)
    ax.add_patch(inner)

    rect1 = patches.Rectangle((0, b), c, c - b, facecolor=ACCENT1, alpha=0.25, edgecolor=ACCENT1, linewidth=2, zorder=3)
    ax.add_patch(rect1)
    rect2 = patches.Rectangle((b, 0), c - b, b, facecolor=ACCENT3, alpha=0.25, edgecolor=ACCENT3, linewidth=2, zorder=3)
    ax.add_patch(rect2)

    ax.text(c / 2, -0.5, f'$c = {c}$', fontsize=16, ha='center', color=ACCENT2, fontweight='bold')
    ax.text(-0.6, c / 2, f'$c = {c}$', fontsize=16, ha='center', va='center', color=ACCENT2,
            fontweight='bold', rotation=90)
    ax.text(b / 2, -0.5, f'$b = {b}$', fontsize=12, ha='center', color=SLATE)
    ax.text(-0.6, b / 2, f'$b = {b}$', fontsize=12, ha='center', va='center', color=SLATE, rotation=90)

    ax.text(b / 2, b / 2, f'$b^2 = {b**2}$', fontsize=14, ha='center', va='center', color=SLATE, zorder=4)
    ax.text(c / 2, b + (c - b) / 2, f'$c \\times (c-b) = {c*(c-b)}$',
            fontsize=11, ha='center', va='center', color=ACCENT1, fontweight='bold', zorder=4)
    ax.text(b + (c - b) / 2, b / 2, f'$(c-b) \\times b$\n$= {(c-b)*b}$',
            fontsize=10, ha='center', va='center', color=ACCENT3, fontweight='bold', zorder=4)

    ax.text(c / 2, c + 1.0,
            f'$c^2 - b^2 = (c-b)(c+b) = {c-b} \\times {c+b} = {(c-b)*(c+b)} = a^2$',
            fontsize=15, ha='center', va='center', color=DARK, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=CREAM, edgecolor=DARK))

    ax.annotate('', xy=(c, b), xytext=(c, c),
               arrowprops=dict(arrowstyle='<->', color=DARK, lw=1.5))
    ax.text(c + 0.4, (b + c) / 2, f'$c-b={c-b}$', fontsize=10, va='center', color=DARK)

    ax.set_xlim(-1.5, c + 2)
    ax.set_ylim(-1.5, c + 2)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('The Gnomon: Visualizing $(c-b)(c+b) = a^2$', fontsize=18,
                 fontweight='bold', color=DARK, pad=20)
    save(fig, "fig08_gnomon.png")


# ============================================================
# ILLUSTRATION 9: B-branch hypotenuses on log scale
# ============================================================
def fig9_b_branch():
    fig, ax = plt.subplots(1, 1, figsize=(14, 6))
    fig.set_facecolor('white')
    ax.set_facecolor('white')

    triples = [
        (3, 4, 5),
        (21, 20, 29),
        (119, 120, 169),
        (697, 696, 985),
        (4059, 4060, 5741),
        (23661, 23660, 33461),
    ]
    hyps = [t[2] for t in triples]
    x_pos = list(range(len(hyps)))

    ax.semilogy(x_pos, hyps, 'o-', color=ACCENT2, markersize=12, linewidth=2.5,
                markeredgecolor=DARK, markeredgewidth=1.5, zorder=5)

    for i, (trip, h) in enumerate(zip(triples, hyps)):
        a, b, c = trip
        ax.text(i, h * 1.8, f'$c = {c}$', fontsize=12, ha='center', color=ACCENT1, fontweight='bold')
        ax.text(i, h * 0.45, f'({a}, {b}, {c})', fontsize=7, ha='center', color=SLATE,
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor=SLATE, alpha=0.5))

    # Growth line
    x_fit = np.linspace(-0.5, 5.5, 100)
    growth = 5 * (3 + 2*np.sqrt(2))**x_fit
    ax.semilogy(x_fit, growth, '--', color=ACCENT5, linewidth=1.5, alpha=0.6,
                label=r'$(3+2\sqrt{2})^n \approx 5.83^n$')

    for i in range(len(hyps) - 1):
        ratio = hyps[i+1] / hyps[i]
        ax.text(i + 0.5, np.sqrt(hyps[i] * hyps[i+1]),
                f'x{ratio:.2f}', fontsize=9, ha='center', color=ACCENT3, fontweight='bold')

    ax.set_xlabel('Depth $n$', fontsize=14, color=DARK)
    ax.set_ylabel('Hypotenuse $c_n$ (log scale)', fontsize=14, color=DARK)
    ax.set_xticks(x_pos)
    ax.set_xticklabels([f'$n={i}$' for i in range(len(hyps))])
    ax.legend(fontsize=12, loc='lower right')
    ax.grid(True, alpha=0.3)
    ax.set_title('The B-Branch: Nearly Isosceles Triangles Growing Exponentially',
                 fontsize=16, fontweight='bold', color=DARK, pad=15)

    ax.text(0.5, 0.02, r'Recurrence: $c_{n+2} = 6\,c_{n+1} - c_n$, with $c_0=5$, $c_1=29$',
            fontsize=12, ha='center', transform=ax.transAxes, color=DARK,
            bbox=dict(boxstyle='round,pad=0.3', facecolor=CREAM, edgecolor=DARK))

    save(fig, "fig09_b_branch.png")


# ============================================================
# ILLUSTRATION 10: Euclid parameter grid
# ============================================================
def fig10_euclid_grid():
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    fig.set_facecolor('white')
    ax.set_facecolor('white')

    max_m = 8

    triangle_x = [1, max_m, max_m, 1]
    triangle_y = [0, 0, max_m - 1, 0]
    ax.fill(triangle_x, triangle_y, alpha=0.05, color=ACCENT2)

    for m in range(1, max_m + 1):
        for n in range(1, m):
            if gcd(m, n) == 1 and (m - n) % 2 == 1:
                a = m*m - n*n
                b = 2*m*n
                c = m*m + n*n
                ax.plot(m, n, 'o', color=ACCENT2, markersize=8, markeredgecolor=DARK,
                       markeredgewidth=1, zorder=5)
                if m <= 6:
                    ax.text(m + 0.15, n + 0.15, f'({a},{b},{c})', fontsize=6,
                            color=SLATE, zorder=6)
            else:
                ax.plot(m, n, 'o', color='lightgray', markersize=4, zorder=3)

    stair_m = [2, 3, 4, 5, 6, 7]
    stair_n = [1, 2, 3, 4, 5, 6]
    ax.plot(stair_m, stair_n, 's-', color=ACCENT1, markersize=12, linewidth=3,
            markeredgecolor=DARK, markeredgewidth=1.5, zorder=10, label='$n = m-1$ (A-branch)')

    for m, n in zip(stair_m, stair_n):
        a = m*m - n*n
        b = 2*m*n
        c = m*m + n*n
        ax.text(m - 0.5, n + 0.35, f'({a},{b},{c})', fontsize=8, color=ACCENT1,
                fontweight='bold', zorder=11)

    for i in range(len(stair_m) - 1):
        ax.annotate('', xy=(stair_m[i+1] - 0.15, stair_n[i+1] - 0.15),
                    xytext=(stair_m[i] + 0.15, stair_n[i] + 0.15),
                    arrowprops=dict(arrowstyle='->', color=ACCENT3, lw=2),
                    zorder=8)
        ax.text((stair_m[i] + stair_m[i+1]) / 2 + 0.25,
                (stair_n[i] + stair_n[i+1]) / 2 - 0.25,
                '$A$', fontsize=11, color=ACCENT3, fontweight='bold')

    diag = np.linspace(0, max_m, 50)
    ax.plot(diag, diag, '--', color='gray', linewidth=1, alpha=0.5)
    ax.text(max_m - 0.5, max_m - 0.2, '$n = m$', fontsize=10, color='gray', rotation=45)

    ax.set_xlabel('$m$', fontsize=16, color=DARK)
    ax.set_ylabel('$n$', fontsize=16, color=DARK)
    ax.set_xlim(0.5, max_m + 0.5)
    ax.set_ylim(-0.5, max_m)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.2)
    ax.legend(fontsize=12, loc='upper left')
    ax.set_title("Euclid's Parameter Grid", fontsize=18, fontweight='bold', color=DARK, pad=15)
    save(fig, "fig10_euclid_grid.png")


# ============================================================
# ILLUSTRATION 11: Poincare disk tessellation
# ============================================================
def fig11_poincare_disk():
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    fig.set_facecolor('white')
    ax.set_facecolor('white')

    theta = np.linspace(0, 2*np.pi, 200)
    ax.plot(np.cos(theta), np.sin(theta), color=DARK, linewidth=2)
    ax.fill(np.cos(theta), np.sin(theta), alpha=0.03, color=ACCENT2)

    # Center tile
    center_r = 0.25
    hex_angles = np.linspace(0, 2*np.pi, 7)
    cx = center_r * np.cos(hex_angles)
    cy = center_r * np.sin(hex_angles)
    ax.fill(cx, cy, alpha=0.3, color=GOLD, zorder=3)
    ax.plot(cx, cy, color=DARK, linewidth=1.5, zorder=4)
    ax.text(0, 0, '(3,4,5)', fontsize=9, ha='center', va='center', color=DARK, fontweight='bold', zorder=5)

    ring1_centers = [(0.45, 0.15), (-0.1, 0.47), (-0.35, -0.25)]
    ring1_labels = ['(5,12,13)', '(21,20,29)', '(15,8,17)']
    ring1_colors = [ACCENT1, ACCENT2, ACCENT3]
    branch_labels_str = ['A', 'B', 'C']

    np.random.seed(7)
    for (cx_c, cy_c), label, color, bl in zip(ring1_centers, ring1_labels, ring1_colors, branch_labels_str):
        r = 0.15
        angles = np.linspace(0, 2*np.pi, 7) + np.random.uniform(0, 0.5)
        px = cx_c + r * np.cos(angles)
        py = cy_c + r * np.sin(angles)
        ax.fill(px, py, alpha=0.2, color=color, zorder=3)
        ax.plot(px, py, color=color, linewidth=1, zorder=4)
        ax.text(cx_c, cy_c, label, fontsize=6, ha='center', va='center', color=DARK, zorder=5)

    ring2_data = [
        (0.65, 0.35, '(7,24,25)', ACCENT1),
        (0.7, -0.1, '(55,48,73)', ACCENT1),
        (0.45, -0.3, '(45,28,53)', ACCENT1),
        (-0.3, 0.65, '(39,80,89)', ACCENT2),
        (0.15, 0.7, '(119,120,169)', ACCENT2),
        (-0.55, 0.45, '(77,36,85)', ACCENT2),
        (-0.6, -0.4, '(11,60,61)', ACCENT3),
        (-0.15, -0.55, '(65,72,97)', ACCENT3),
        (-0.55, 0.0, '(35,12,37)', ACCENT3),
    ]

    for cx_c, cy_c, label, color in ring2_data:
        r = 0.08
        angles = np.linspace(0, 2*np.pi, 7) + np.random.uniform(0, 1)
        px = cx_c + r * np.cos(angles)
        py = cy_c + r * np.sin(angles)
        ax.fill(px, py, alpha=0.15, color=color, zorder=3)
        ax.plot(px, py, color=color, linewidth=0.8, zorder=4)
        ax.text(cx_c, cy_c, label, fontsize=4, ha='center', va='center', color=DARK, zorder=5)

    np.random.seed(42)
    for _ in range(50):
        angle = np.random.uniform(0, 2*np.pi)
        dist = 0.75 + np.random.uniform(0, 0.2)
        r = 0.03
        cx_c = dist * np.cos(angle)
        cy_c = dist * np.sin(angle)
        angles = np.linspace(0, 2*np.pi, 5) + np.random.uniform(0, 1)
        px = cx_c + r * np.cos(angles)
        py = cy_c + r * np.sin(angles)
        color = [ACCENT1, ACCENT2, ACCENT3][np.random.randint(0, 3)]
        ax.fill(px, py, alpha=0.1, color=color, zorder=2)
        ax.plot(px, py, color=color, linewidth=0.3, alpha=0.5, zorder=2)

    for _ in range(100):
        angle = np.random.uniform(0, 2*np.pi)
        dist = 0.88 + np.random.uniform(0, 0.09)
        r = 0.012
        cx_c = dist * np.cos(angle)
        cy_c = dist * np.sin(angle)
        angles = np.linspace(0, 2*np.pi, 4) + np.random.uniform(0, 1)
        px = cx_c + r * np.cos(angles)
        py = cy_c + r * np.sin(angles)
        color = [ACCENT1, ACCENT2, ACCENT3][np.random.randint(0, 3)]
        ax.fill(px, py, alpha=0.08, color=color, zorder=1)

    ax.text(0.3, 0.35, '$A$', fontsize=14, color=ACCENT1, fontweight='bold')
    ax.text(-0.25, 0.35, '$B$', fontsize=14, color=ACCENT2, fontweight='bold')
    ax.text(-0.3, -0.1, '$C$', fontsize=14, color=ACCENT3, fontweight='bold')
    ax.text(0, -1.15, 'Circle at Infinity', fontsize=12, ha='center', color=SLATE, style='italic')

    ax.set_xlim(-1.25, 1.25)
    ax.set_ylim(-1.3, 1.25)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('The Poincare Disk: Berggren Tree as Hyperbolic Tessellation',
                 fontsize=16, fontweight='bold', color=DARK, pad=15)
    save(fig, "fig11_poincare_disk.png")


# ============================================================
# ILLUSTRATION 12: Side-by-side light cones
# ============================================================
def fig12_light_cones():
    fig = plt.figure(figsize=(14, 7))
    fig.set_facecolor('white')

    ax1 = fig.add_subplot(121, projection='3d')
    ax2 = fig.add_subplot(122, projection='3d')

    theta = np.linspace(0, 2*np.pi, 80)
    z_vals = np.linspace(0, 1, 30)
    Theta, Z = np.meshgrid(theta, z_vals)
    X = Z * np.cos(Theta)
    Y = Z * np.sin(Theta)

    ax1.plot_surface(X * 15, Y * 15, Z * 15, alpha=0.08, color=ACCENT2)
    ax1.plot_surface(X * 15, Y * 15, -Z * 15, alpha=0.05, color=ACCENT2)
    for t in np.linspace(0, 2*np.pi, 6, endpoint=False):
        r = np.linspace(0, 15, 50)
        ax1.plot(r*np.cos(t), r*np.sin(t), r, color=ACCENT5, linewidth=1.5, alpha=0.6)
    ax1.set_xlabel('$x$', fontsize=12)
    ax1.set_ylabel('$y$', fontsize=12)
    ax1.set_zlabel('$t$', fontsize=12)
    ax1.set_title('Spacetime Light Cone\n$x^2 + y^2 = t^2$', fontsize=13, fontweight='bold', color=DARK)
    ax1.view_init(elev=20, azim=35)

    ax2.plot_surface(X * 30, Y * 30, Z * 30, alpha=0.05, color=ACCENT2)
    triples = [(3,4,5), (5,12,13), (8,15,17), (7,24,25), (20,21,29), (9,40,41)]
    for a, b, c in triples:
        ax2.scatter([a], [b], [c], color=ACCENT1, s=60, zorder=10, edgecolors=DARK, linewidths=1)
        ax2.text(a+1, b+1, c+1, f'({a},{b},{c})', fontsize=7, color=ACCENT1)
    ax2.set_xlabel('$a$', fontsize=12)
    ax2.set_ylabel('$b$', fontsize=12)
    ax2.set_zlabel('$c$', fontsize=12)
    ax2.set_title('Integer Null Cone\n$a^2 + b^2 = c^2$', fontsize=13, fontweight='bold', color=DARK)
    ax2.view_init(elev=20, azim=35)

    fig.suptitle('Same Equation, Different Worlds', fontsize=18, fontweight='bold', color=DARK, y=0.98)
    save(fig, "fig12_light_cones.png")


# ============================================================
# ILLUSTRATION 13: The Five Wonders infographic
# ============================================================
def fig13_wonder_map():
    fig, ax = plt.subplots(1, 1, figsize=(14, 14))
    fig.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    center = (7, 7)
    tree_circle = plt.Circle(center, 1.8, facecolor=LIGHT_GREEN, edgecolor=ACCENT3,
                              linewidth=3, alpha=0.5, zorder=3)
    ax.add_patch(tree_circle)
    ax.text(7, 7.5, 'Berggren', fontsize=16, ha='center', va='center', color=DARK, fontweight='bold', zorder=5)
    ax.text(7, 6.8, 'Tree', fontsize=16, ha='center', va='center', color=DARK, fontweight='bold', zorder=5)
    ax.text(7, 6.1, '(3, 4, 5)', fontsize=12, ha='center', va='center', color=ACCENT3, fontweight='bold', zorder=5)

    wonders = [
        ('1. Preservation', '$a^2 + b^2 = c^2$\npreserved', 10.5, 11, ACCENT1),
        ('2. Completeness', 'Every primitive\ntriple, exactly once', 3.5, 11, ACCENT2),
        ('3. Descent', 'Always back to\n(3, 4, 5)', 1.5, 5, ACCENT3),
        ('4. Factoring', '$(c-b)(c+b) = a^2$', 12.5, 5, ACCENT5),
        ('5. Lorentz\n   Symmetry', '$M^T Q M = Q$', 7, 1.5, ACCENT4),
    ]

    for title, desc, wx, wy, color in wonders:
        box = plt.Circle((wx, wy), 1.5, facecolor='white', edgecolor=color,
                          linewidth=2.5, alpha=0.8, zorder=3)
        ax.add_patch(box)

        dx, dy = wx - center[0], wy - center[1]
        dist = np.sqrt(dx**2 + dy**2)
        sx = center[0] + 1.9 * dx / dist
        sy = center[1] + 1.9 * dy / dist
        ex = wx - 1.6 * dx / dist
        ey = wy - 1.6 * dy / dist
        ax.annotate('', xy=(ex, ey), xytext=(sx, sy),
                    arrowprops=dict(arrowstyle='->', color=color, lw=2.5,
                                   connectionstyle='arc3,rad=0.05'))

        ax.text(wx, wy + 0.4, title, fontsize=11, ha='center', va='center',
                color=color, fontweight='bold', zorder=5)
        ax.text(wx, wy - 0.3, desc, fontsize=9, ha='center', va='center',
                color=DARK, zorder=5)

    border = FancyBboxPatch((0.3, 0.3), 13.4, 13.4, boxstyle="round,pad=0.3",
                            facecolor='none', edgecolor=DARK, linewidth=2, alpha=0.3)
    ax.add_patch(border)

    ax.set_xlim(0, 14)
    ax.set_ylim(0, 14)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('The Five Wonders of the Berggren Tree', fontsize=22,
                 fontweight='bold', color=DARK, pad=20)
    save(fig, "fig13_wonder_map.png")


# ============================================================
# Run all
# ============================================================
if __name__ == '__main__':
    print("Generating Chapter 1 illustrations...")
    fig1_rope_triangle()
    fig2_null_cone()
    fig3_magic_mirrors()
    fig4_matrix_vector()
    fig5_berggren_tree()
    fig6_descent_maze()
    fig7_factoring_trick()
    fig8_gnomon()
    fig9_b_branch()
    fig10_euclid_grid()
    fig11_poincare_disk()
    fig12_light_cones()
    fig13_wonder_map()
    print("Done! All images saved to images/chapter1/")

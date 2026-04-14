#!/usr/bin/env python3
"""Generate all illustrations for Chapter 5: The Tree That Knew It Was a Spacetime."""

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

# Color palette (matching Chapters 1 & 2 style)
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


# ---------- Berggren matrices ----------
BA = np.array([[1, -2, 2], [2, -1, 2], [2, -2, 3]])
BB = np.array([[1,  2, 2], [2,  1, 2], [2,  2, 3]])
BC = np.array([[-1, 2, 2], [-2, 1, 2], [-2, 2, 3]])

def berggren_children(triple):
    v = np.array(triple)
    return tuple(BA @ v), tuple(BB @ v), tuple(BC @ v)


# ============================================================
# FIG 1: Full ternary Berggren tree, 3 levels
# ============================================================
def fig01_berggren_tree():
    fig, ax = plt.subplots(1, 1, figsize=(20, 12))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    root = (3, 4, 5)
    level1 = berggren_children(root)
    level2 = []
    for t in level1:
        level2.extend(berggren_children(t))

    positions = {}
    positions[root] = (10, 10)
    x_starts_l1 = [3, 10, 17]
    for i, t in enumerate(level1):
        positions[t] = (x_starts_l1[i], 7)
    x_l2 = np.linspace(0.5, 19.5, 9)
    for i, t in enumerate(level2):
        positions[t] = (x_l2[i], 4)

    branch_labels = ['$A$', '$B$', '$C$']
    branch_colors = [ACCENT1, ACCENT2, ACCENT3]

    def draw_edge(parent, child, label, color):
        px, py = positions[parent]
        cx, cy = positions[child]
        ax.plot([px, cx], [py - 0.7, cy + 0.7], color=color, lw=2.5, zorder=1)
        mx, my = (px + cx) / 2, (py + cy) / 2
        ax.text(mx + 0.3 * np.sign(cx - px + 0.01), my + 0.15, label,
                fontsize=11, ha='center', va='center', color=color, fontweight='bold')

    for i, child in enumerate(level1):
        draw_edge(root, child, branch_labels[i], branch_colors[i])
    for i, parent in enumerate(level1):
        children_of_p = berggren_children(parent)
        for j, child in enumerate(children_of_p):
            draw_edge(parent, child, branch_labels[j], branch_colors[j])

    def draw_node(triple, pos, size=0.65, fontsize=11):
        x, y = pos
        circle = plt.Circle((x, y), size, facecolor=CREAM, edgecolor=DARK,
                             linewidth=2, zorder=5)
        ax.add_patch(circle)
        a, b, c = [int(x) for x in triple]
        ax.text(x, y, f'$({a},{b},{c})$', fontsize=fontsize,
                ha='center', va='center', color=DARK, fontweight='bold', zorder=6)

    draw_node(root, positions[root], size=0.8, fontsize=13)
    for t in level1:
        draw_node(t, positions[t], size=0.7, fontsize=11)
    for t in level2:
        draw_node(t, positions[t], size=0.65, fontsize=8)

    ax.set_xlim(-1, 21)
    ax.set_ylim(2.5, 11.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title("The Berggren Tree \u2014 Three Levels Deep",
                 fontsize=18, fontweight='bold', color=DARK, pad=15)
    save(fig, "fig01_berggren_tree.png")


# ============================================================
# FIG 2: Three right triangles with matrix arrows
# ============================================================
def fig02_three_triangles():
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.set_facecolor(SAND)

    triples = [(3, 4, 5), (5, 12, 13), (15, 8, 17)]
    labels = ['$(3, 4, 5)$\nParent', '$(5, 12, 13)$\n$B_A$ child', '$(15, 8, 17)$\n$B_C$ child']
    colors = [ACCENT2, ACCENT1, ACCENT3]

    for idx, (ax, (a, b, c), label, col) in enumerate(zip(axes, triples, labels, colors)):
        ax.set_facecolor(SAND)
        scale = 1.0 / max(a, b) * 4
        ax.fill([0, b * scale, 0], [0, 0, a * scale], alpha=0.15, color=col)
        ax.plot([0, b * scale, 0, 0], [0, 0, a * scale, 0], color=DARK, lw=2.5)
        sq = 0.3
        ax.plot([sq, sq, 0], [0, sq, sq], color=DARK, lw=1.5)
        ax.text(b * scale / 2, -0.4, f'$b = {b}$', fontsize=13, ha='center', color=DARK)
        ax.text(-0.6, a * scale / 2, f'$a = {a}$', fontsize=13, ha='center', color=DARK, rotation=90)
        ax.text(b * scale / 2 + 0.3, a * scale / 2 + 0.3, f'$c = {c}$', fontsize=13,
                ha='center', color=DARK, rotation=-np.degrees(np.arctan2(a, b)))
        ax.set_title(label, fontsize=14, fontweight='bold', color=col, pad=10)
        ax.set_xlim(-1.2, b * scale + 1)
        ax.set_ylim(-1, a * scale + 1)
        ax.set_aspect('equal')
        ax.axis('off')

    # Arrows between subplots (use simple arrow text)
    fig.text(0.36, 0.52, r'$B_A$', fontsize=20, ha='center', va='center',
             color=ACCENT1, fontweight='bold')
    fig.text(0.36, 0.44, r'$\longrightarrow$', fontsize=22, ha='center', va='center',
             color=ACCENT1)
    fig.text(0.68, 0.52, r'$B_C$', fontsize=20, ha='center', va='center',
             color=ACCENT3, fontweight='bold')
    fig.text(0.68, 0.44, r'$\longleftarrow$', fontsize=22, ha='center', va='center',
             color=ACCENT3)
    fig.text(0.52, 0.06, '(both from parent $(3,4,5)$)', fontsize=12, ha='center',
             va='center', color=SLATE)

    fig.suptitle("The Berggren Matrices Produce Wildly Different Children",
                 fontsize=16, fontweight='bold', color=DARK, y=0.98)
    save(fig, "fig02_three_triangles.png")


# ============================================================
# FIG 3: 3D null cone with Pythagorean triples
# ============================================================
def fig03_null_cone():
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    theta = np.linspace(0, 2 * np.pi, 100)
    c_vals = np.linspace(0, 30, 50)
    Theta, C = np.meshgrid(theta, c_vals)
    A = C * np.cos(Theta)
    B = C * np.sin(Theta)
    ax.plot_surface(A, B, C, alpha=0.12, color=LIGHT_BLUE, edgecolor='none')

    for t in np.linspace(0, 2 * np.pi, 12, endpoint=False):
        a_line = c_vals * np.cos(t)
        b_line = c_vals * np.sin(t)
        ax.plot(a_line, b_line, c_vals, color=ACCENT2, alpha=0.2, lw=0.5)

    pts = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25), (20, 21, 29), (9, 40, 41)]
    for a, b, c in pts:
        ax.scatter([a], [b], [c], s=120, color=ACCENT1, edgecolors=DARK, linewidths=1.5, zorder=10)
        ax.text(a + 1, b + 1, c + 0.5, f'$({a},{b},{c})$', fontsize=9, color=DARK)

    ax.set_xlabel('$a$', fontsize=14, color=DARK)
    ax.set_ylabel('$b$', fontsize=14, color=DARK)
    ax.set_zlabel('$c$', fontsize=14, color=DARK)
    ax.set_title('The Null Cone of $Q$: Every Pythagorean Triple Lives Here',
                 fontsize=15, fontweight='bold', color=DARK, pad=15)
    ax.view_init(elev=20, azim=35)
    save(fig, "fig03_null_cone.png")


# ============================================================
# FIG 4: Side-by-side spacetime vs Pythagorean cone
# ============================================================
def fig04_spacetime_comparison():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    fig.set_facecolor(SAND)

    for ax, title, xlabel, ylabel, is_physics in [
        (ax1, "Spacetime Light Cone", "$x$", "$t$", True),
        (ax2, "Pythagorean Null Cone", "$a$", "$c$", False)
    ]:
        ax.set_facecolor(SAND)
        x = np.linspace(-10, 10, 200)
        ax.fill_between(x, np.abs(x), 12, alpha=0.10, color=LIGHT_BLUE,
                         label='Timelike ($Q < 0$)')
        ax.fill_between(x, 0, np.abs(x), alpha=0.10, color=GLOW,
                         label='Spacelike ($Q > 0$)')
        ax.plot(x, np.abs(x), color=DARK, lw=2.5, label='Null cone ($Q = 0$)')

        if is_physics:
            t_wl = np.linspace(0, 10, 50)
            ax.plot(t_wl * 0.3, t_wl, '--', color=ACCENT4, lw=2, label='Timelike worldline')
            ax.plot(t_wl * 1.5, t_wl, ':', color=ACCENT5, lw=2, label='Spacelike path')
        else:
            pts_2d = [(3, 5), (5, 13), (8, 17), (7, 25), (-3, 5), (-5, 13)]
            for a, c in pts_2d:
                ax.plot(a, c, 'o', color=ACCENT1, markersize=10,
                        markeredgecolor=DARK, markeredgewidth=1.5, zorder=10)
                label_str = f'$({abs(a)},\\ldots,{c})$'
                ax.annotate(label_str, (a, c),
                           textcoords='offset points', xytext=(8, 5),
                           fontsize=9, color=DARK)

        ax.set_xlabel(xlabel, fontsize=14, color=DARK)
        ax.set_ylabel(ylabel, fontsize=14, color=DARK)
        ax.set_title(title, fontsize=15, fontweight='bold', color=DARK, pad=10)
        ax.set_xlim(-11, 11)
        ax.set_ylim(-0.5, 12)
        ax.legend(fontsize=9, loc='upper left', framealpha=0.8)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color(DARK)
        ax.spines['left'].set_color(DARK)

    fig.suptitle("From Einstein to Euclid \u2014 The Same Cone Governs Both",
                 fontsize=17, fontweight='bold', color=DARK, y=1.02)
    plt.tight_layout()
    save(fig, "fig04_spacetime_comparison.png")


# ============================================================
# FIG 5: Mirror triangle -- orientation / determinant
# ============================================================
def fig05_mirror_triangle():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.set_facecolor(SAND)

    for ax, flip, label, det_label, col in [
        (ax1, False, 'Proper ($\\det = +1$)', '$B_A$ or $B_C$', ACCENT2),
        (ax2, True, 'Improper ($\\det = -1$)', '$B_B$', ACCENT1)
    ]:
        ax.set_facecolor(SAND)
        if flip:
            tri_x = [8, 4, 8, 8]
            tri_y = [0, 0, 3, 0]
        else:
            tri_x = [0, 4, 0, 0]
            tri_y = [0, 0, 3, 0]

        ax.fill(tri_x[:3], tri_y[:3], alpha=0.15, color=col)
        ax.plot(tri_x, tri_y, color=DARK, lw=3)

        if flip:
            ax.plot([8 - 0.3, 8 - 0.3, 8], [0, 0.3, 0.3], color=DARK, lw=1.5)
        else:
            ax.plot([0.3, 0.3, 0], [0, 0.3, 0.3], color=DARK, lw=1.5)

        bx = 6 if flip else 2
        ax.text(bx, -0.5, '$b = 4$', fontsize=14, ha='center', color=DARK, fontweight='bold')
        sx = 8.6 if flip else -0.6
        ax.text(sx, 1.5, '$a = 3$', fontsize=14, ha='center', color=DARK, fontweight='bold')

        ax.set_title(label, fontsize=15, fontweight='bold', color=col, pad=10)
        ax.text(4 if flip else 2, -1.3, det_label, fontsize=12, ha='center',
                color=SLATE, style='italic')
        ax.set_xlim(-1.5, 9.5)
        ax.set_ylim(-2, 4.5)
        ax.set_aspect('equal')
        ax.axis('off')

    # Arrow between
    fig.text(0.50, 0.55, r'$B_B$', fontsize=24, ha='center', va='center',
             color=ACCENT5, fontweight='bold')
    fig.text(0.50, 0.45, r'$\longleftrightarrow$', fontsize=28, ha='center', va='center',
             color=ACCENT5)
    fig.text(0.50, 0.35, 'Mirror reflection', fontsize=12, ha='center', va='center',
             color=SLATE, style='italic')

    fig.suptitle("Orientation: Proper vs. Improper Transformations",
                 fontsize=16, fontweight='bold', color=DARK, y=0.98)
    save(fig, "fig05_mirror_triangle.png")


# ============================================================
# FIG 6: Tree with checkmarks -- Pythagorean verification
# ============================================================
def fig06_pythagorean_check():
    fig, ax = plt.subplots(1, 1, figsize=(18, 12))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    root = (3, 4, 5)
    level1 = berggren_children(root)
    level2 = []
    for t in level1:
        level2.extend(berggren_children(t))

    positions = {}
    positions[root] = (9, 10)
    x_l1 = [3, 9, 15]
    for i, t in enumerate(level1):
        positions[t] = (x_l1[i], 7)
    x_l2 = np.linspace(0.5, 17.5, 9)
    for i, t in enumerate(level2):
        positions[t] = (x_l2[i], 4)

    def draw_edge(p, c):
        px, py = positions[p]
        cx, cy = positions[c]
        ax.plot([px, cx], [py - 0.8, cy + 0.8], color=SLATE, lw=2, zorder=1)

    for child in level1:
        draw_edge(root, child)
    for i, parent in enumerate(level1):
        for child in berggren_children(parent):
            draw_edge(parent, child)

    def draw_verified_node(triple, pos, fontsize=10):
        x, y = pos
        a, b, c = [int(v) for v in triple]
        a2b2 = a**2 + b**2
        c2 = c**2

        box = FancyBboxPatch((x - 1.3, y - 0.6), 2.6, 1.2,
                              boxstyle="round,pad=0.1", facecolor=CREAM,
                              edgecolor=DARK, linewidth=1.5, zorder=5)
        ax.add_patch(box)

        ax.text(x, y + 0.2, f'$({a},{b},{c})$', fontsize=fontsize,
                ha='center', va='center', color=DARK, fontweight='bold', zorder=6)
        ax.text(x, y - 0.25, f'${a}^2+{b}^2={a2b2}={c}^2$', fontsize=fontsize - 2,
                ha='center', va='center', color=SLATE, zorder=6)

        # Checkmark
        ax.text(x + 1.1, y + 0.4, '\u2713', fontsize=fontsize + 4, ha='center', va='center',
                color=ACCENT3, fontweight='bold', zorder=7)

    draw_verified_node(root, positions[root], fontsize=12)
    for t in level1:
        draw_verified_node(t, positions[t], fontsize=10)
    for t in level2:
        draw_verified_node(t, positions[t], fontsize=7)

    ax.set_xlim(-1, 19)
    ax.set_ylim(2.5, 11.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title("Every Node Is Pythagorean \u2014 Verified by Induction",
                 fontsize=17, fontweight='bold', color=DARK, pad=15)
    save(fig, "fig06_pythagorean_check.png")


# ============================================================
# FIG 7: Null cone with timelike/spacelike regions (3D)
# ============================================================
def fig07_null_cone_regions():
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    theta = np.linspace(0, 2 * np.pi, 80)
    c_vals = np.linspace(0, 25, 40)
    Theta, C = np.meshgrid(theta, c_vals)
    A = C * np.cos(Theta)
    B_surf = C * np.sin(Theta)

    ax.plot_surface(A, B_surf, C, alpha=0.15, color='silver', edgecolor='none')

    on_cone = [(3, 4, 5), (5, 12, 13)]
    for a, b, c in on_cone:
        ax.scatter([a], [b], [c], s=150, color=ACCENT1, edgecolors=DARK,
                   linewidths=2, zorder=10)
        ax.text(a + 1, b + 1, c + 0.5, f'$({a},{b},{c})$\n$Q=0$', fontsize=10, color=ACCENT1)

    ax.scatter([1], [1], [1], s=150, color=GOLD, edgecolors=DARK, linewidths=2,
               zorder=10, marker='D')
    ax.text(2, 2, 1, '$(1,1,1)$\n$Q=1$', fontsize=10, color=GOLD)

    ax.scatter([1], [1], [2], s=150, color=ACCENT2, edgecolors=DARK, linewidths=2,
               zorder=10, marker='s')
    ax.text(2, 2, 2.2, '$(1,1,2)$\n$Q=-2$', fontsize=10, color=ACCENT2)

    ax.set_xlabel('$a$', fontsize=13, color=DARK)
    ax.set_ylabel('$b$', fontsize=13, color=DARK)
    ax.set_zlabel('$c$', fontsize=13, color=DARK)
    ax.set_title('Null Cone with Timelike and Spacelike Regions',
                 fontsize=15, fontweight='bold', color=DARK, pad=15)
    ax.view_init(elev=22, azim=40)
    save(fig, "fig07_null_cone_regions.png")


# ============================================================
# FIG 8: Factoring vice diagram
# ============================================================
def fig08_factoring_vice():
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    block = FancyBboxPatch((4, 3.5), 4, 2, boxstyle="round,pad=0.2",
                            facecolor=LIGHT_BLUE, edgecolor=DARK, linewidth=3, zorder=5)
    ax.add_patch(block)
    ax.text(6, 4.5, '$N^2 = a^2$', fontsize=22, ha='center', va='center',
            color=DARK, fontweight='bold', zorder=6)

    left_jaw = FancyBboxPatch((0.5, 3.5), 2.5, 2, boxstyle="round,pad=0.15",
                               facecolor=LIGHT_RED, edgecolor=ACCENT1, linewidth=2.5, zorder=5)
    ax.add_patch(left_jaw)
    ax.text(1.75, 4.5, '$c - b$', fontsize=18, ha='center', va='center',
            color=ACCENT1, fontweight='bold', zorder=6)

    right_jaw = FancyBboxPatch((9, 3.5), 2.5, 2, boxstyle="round,pad=0.15",
                                facecolor=LIGHT_GREEN, edgecolor=ACCENT3, linewidth=2.5, zorder=5)
    ax.add_patch(right_jaw)
    ax.text(10.25, 4.5, '$c + b$', fontsize=18, ha='center', va='center',
            color=ACCENT3, fontweight='bold', zorder=6)

    ax.annotate('', xy=(4, 4.5), xytext=(3, 4.5),
                arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=3))
    ax.annotate('', xy=(8, 4.5), xytext=(9, 4.5),
                arrowprops=dict(arrowstyle='->', color=ACCENT3, lw=3))

    ax.text(6, 7, '$(c - b)(c + b) = c^2 - b^2 = a^2$', fontsize=16, ha='center',
            va='center', color=DARK, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=GLOW, alpha=0.5))

    tri_x = [3.5, 8.5, 3.5, 3.5]
    tri_y = [0.3, 0.3, 2.8, 0.3]
    ax.fill(tri_x[:3], tri_y[:3], alpha=0.1, color=ACCENT2)
    ax.plot(tri_x, tri_y, color=DARK, lw=2)
    ax.plot([3.8, 3.8, 3.5], [0.3, 0.6, 0.6], color=DARK, lw=1.5)

    ax.text(6, -0.1, '$b$', fontsize=14, ha='center', color=DARK, fontweight='bold')
    ax.text(3.0, 1.5, '$a = N$', fontsize=14, ha='center', color=DARK, fontweight='bold', rotation=90)
    ax.text(6.3, 1.9, '$c$', fontsize=14, ha='center', color=DARK, fontweight='bold', rotation=-28)

    ax.set_xlim(-0.5, 12.5)
    ax.set_ylim(-0.8, 8)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title("The Factoring Vice: $(c - b)(c + b) = a^2$",
                 fontsize=17, fontweight='bold', color=DARK, pad=15)
    save(fig, "fig08_factoring_vice.png")


# ============================================================
# FIG 9: Brahmagupta-Fibonacci identity visual proof
# ============================================================
def fig09_brahmagupta_fibonacci():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    fig.set_facecolor(SAND)

    a1, b1, a2, b2 = 2, 1, 3, 2
    lhs1 = a1**2 + b1**2  # 5
    lhs2 = a2**2 + b2**2  # 13
    product = lhs1 * lhs2  # 65
    r1 = a1*a2 - b1*b2  # 4
    r2 = a1*b2 + b1*a2  # 7

    # Left panel: the two factors
    ax1.set_facecolor(SAND)
    ax1.add_patch(patches.Rectangle((0, 0), a1, a1, facecolor=LIGHT_BLUE, edgecolor=DARK, lw=2))
    ax1.text(a1/2, a1/2, f'$a_1^2 = {a1**2}$', fontsize=12, ha='center', va='center', color=DARK)

    ax1.add_patch(patches.Rectangle((0, a1), b1, b1, facecolor=LIGHT_RED, edgecolor=DARK, lw=2))
    ax1.text(b1/2, a1 + b1/2, f'$b_1^2$\n$={b1**2}$', fontsize=9, ha='center', va='center', color=DARK)

    ax1.text(1, -0.7, f'$a_1^2 + b_1^2 = {lhs1}$', fontsize=13, ha='center', color=ACCENT2, fontweight='bold')

    ax1.add_patch(patches.Rectangle((4, 0), a2, a2, facecolor=LIGHT_GREEN, edgecolor=DARK, lw=2))
    ax1.text(4 + a2/2, a2/2, f'$a_2^2 = {a2**2}$', fontsize=12, ha='center', va='center', color=DARK)

    ax1.add_patch(patches.Rectangle((4, a2), b2, b2, facecolor=GLOW, edgecolor=DARK, lw=2, alpha=0.5))
    ax1.text(4 + b2/2, a2 + b2/2, f'$b_2^2 = {b2**2}$', fontsize=10, ha='center', va='center', color=DARK)

    ax1.text(5.5, -0.7, f'$a_2^2 + b_2^2 = {lhs2}$', fontsize=13, ha='center', color=ACCENT3, fontweight='bold')

    ax1.set_title(f'Two sums of squares: ${lhs1} \\times {lhs2} = {product}$',
                  fontsize=14, fontweight='bold', color=DARK, pad=10)
    ax1.set_xlim(-0.5, 8)
    ax1.set_ylim(-1.5, 6)
    ax1.set_aspect('equal')
    ax1.axis('off')

    # Right panel: the rearrangement
    ax2.set_facecolor(SAND)
    ax2.add_patch(patches.Rectangle((0, 0), abs(r1), abs(r1), facecolor=LIGHT_BLUE,
                                     edgecolor=DARK, lw=2))
    ax2.text(abs(r1)/2, abs(r1)/2, f'$(a_1 a_2 - b_1 b_2)^2$\n$= {r1}^2 = {r1**2}$',
             fontsize=10, ha='center', va='center', color=DARK)

    offset = abs(r1) + 0.5
    ax2.add_patch(patches.Rectangle((offset, 0), abs(r2), abs(r2), facecolor=LIGHT_GREEN,
                                     edgecolor=DARK, lw=2))
    ax2.text(offset + abs(r2)/2, abs(r2)/2,
             f'$(a_1 b_2 + b_1 a_2)^2$\n$= {r2}^2 = {r2**2}$',
             fontsize=10, ha='center', va='center', color=DARK)

    ax2.text(6, -0.7, f'${r1**2} + {r2**2} = {product}$', fontsize=14,
             ha='center', color=ACCENT1, fontweight='bold')

    ax2.set_title(f'Rearranged: ${r1**2} + {r2**2} = {product}$',
                  fontsize=14, fontweight='bold', color=DARK, pad=10)
    ax2.set_xlim(-0.5, 13)
    ax2.set_ylim(-1.5, 8)
    ax2.set_aspect('equal')
    ax2.axis('off')

    fig.suptitle("Brahmagupta\u2013Fibonacci: $(a_1^2+b_1^2)(a_2^2+b_2^2) = (a_1 a_2 - b_1 b_2)^2 + (a_1 b_2 + b_1 a_2)^2$",
                 fontsize=14, fontweight='bold', color=DARK, y=1.01)
    plt.tight_layout()
    save(fig, "fig09_brahmagupta_fibonacci.png")


# ============================================================
# FIG 10: Euclid (m,n) parameter grid
# ============================================================
def fig10_euclid_grid():
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    max_m = 10
    for m in range(2, max_m + 1):
        for n in range(1, m):
            valid = (gcd(m, n) == 1) and ((m - n) % 2 == 1)
            if valid:
                a = m*m - n*n
                b = 2*m*n
                c = m*m + n*n
                ax.plot(m, n, 'o', color=ACCENT2, markersize=12,
                        markeredgecolor=DARK, markeredgewidth=1.5, zorder=10)
                ax.text(m + 0.25, n + 0.2, f'$({a},{b},{c})$', fontsize=7,
                        color=DARK, zorder=11)
            else:
                ax.plot(m, n, 'o', color='#CCCCCC', markersize=7,
                        markeredgecolor=SLATE, markeredgewidth=0.8, zorder=5)

    # Highlight consecutive diagonal n = m - 1
    for m in range(2, max_m + 1):
        n = m - 1
        if gcd(m, n) == 1 and (m - n) % 2 == 1:
            ax.plot(m, n, 'o', color=ACCENT1, markersize=14,
                    markeredgecolor=DARK, markeredgewidth=2, zorder=12)

    ax.plot([2, max_m], [1, max_m - 1], '--', color=ACCENT1, lw=2, alpha=0.5,
            label='Consecutive diagonal $n = m-1$')

    ax.set_xlabel('$m$', fontsize=14, color=DARK)
    ax.set_ylabel('$n$', fontsize=14, color=DARK)
    ax.set_title("Euclid's Parameter Grid: Primitive Triples from $(m, n)$",
                 fontsize=16, fontweight='bold', color=DARK, pad=15)
    ax.legend(fontsize=11, loc='upper left', framealpha=0.8)
    ax.set_xlim(1.3, max_m + 1)
    ax.set_ylim(0.3, max_m)
    ax.set_xticks(range(2, max_m + 1))
    ax.set_yticks(range(1, max_m))
    ax.grid(True, alpha=0.2)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    save(fig, "fig10_euclid_grid.png")


# ============================================================
# FIG 11: A-branch staircase descent
# ============================================================
def fig11_a_staircase():
    fig, ax = plt.subplots(1, 1, figsize=(10, 14))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    stairs = []
    for m in range(2, 7):
        n = m - 1
        a = m*m - n*n
        b = 2*m*n
        c = m*m + n*n
        stairs.append((a, b, c, m, n))

    num = len(stairs)
    step_h = 2.2
    step_w = 6

    for i, (a, b, c, m, n) in enumerate(stairs):
        y = i * step_h + 1
        x = 2

        ax.add_patch(patches.Rectangle((x, y), step_w, step_h * 0.75,
                                        facecolor=CREAM, edgecolor=DARK, linewidth=2, zorder=5))

        ax.text(x + step_w / 2, y + step_h * 0.5,
                f'$({a}, {b}, {c})$', fontsize=14,
                ha='center', va='center', color=DARK, fontweight='bold', zorder=6)
        ax.text(x + step_w / 2, y + step_h * 0.2,
                f'$(m, n) = ({m}, {n})$', fontsize=11,
                ha='center', va='center', color=SLATE, zorder=6)

        # Small right triangle
        scale = 0.6 / max(a, b)
        tx, ty = x + step_w + 0.5, y + 0.2
        ax.fill([tx, tx + b * scale, tx], [ty, ty, ty + a * scale],
                alpha=0.15, color=ACCENT2)
        ax.plot([tx, tx + b * scale, tx, tx], [ty, ty, ty + a * scale, ty],
                color=DARK, lw=1.5)

        # Downward arrow (except at bottom)
        if i > 0:
            ax.annotate('', xy=(x + step_w / 2, y + step_h * 0.75 + 0.05),
                        xytext=(x + step_w / 2, y + step_h * 0.75 + step_h * 0.25 - 0.05),
                        arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=2.5))
            ax.text(x + step_w / 2 + 1.8, y + step_h * 0.85,
                    '$B_A^{-1}$', fontsize=12, ha='center', va='center',
                    color=ACCENT1, fontweight='bold')

    ax.set_xlim(0, 12)
    ax.set_ylim(0, num * step_h + 2)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title("The A-Branch Staircase: Descent by $B_A^{-1}$",
                 fontsize=16, fontweight='bold', color=DARK, pad=15)
    ax.text(5, 0.3, 'Bottom: the root $(3, 4, 5)$', fontsize=12,
            ha='center', va='center', color=ACCENT3, style='italic')
    save(fig, "fig11_a_staircase.png")


# ============================================================
# FIG 12: B-branch hypotenuses on log scale
# ============================================================
def fig12_pell_number_line():
    fig, ax = plt.subplots(1, 1, figsize=(16, 6))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    hyps = [5, 29]
    for _ in range(5):
        hyps.append(6 * hyps[-1] - hyps[-2])

    y = 3
    positions_x = []
    for i, h in enumerate(hyps):
        x = np.log10(h)
        positions_x.append(x)
        ax.plot(x, y, 'o', color=ACCENT1, markersize=14,
                markeredgecolor=DARK, markeredgewidth=2, zorder=10)
        ax.text(x, y + 0.5, f'${h}$', fontsize=12, ha='center', va='bottom',
                color=DARK, fontweight='bold')
        ax.text(x, y - 0.5, f'$c_{i}$', fontsize=11, ha='center', va='top', color=SLATE)

    for i in range(len(positions_x) - 1):
        x1, x2 = positions_x[i], positions_x[i + 1]
        mid = (x1 + x2) / 2
        ax.annotate('', xy=(x2 - 0.05, y + 0.1), xytext=(x1 + 0.05, y + 0.1),
                    arrowprops=dict(arrowstyle='->', color=ACCENT2, lw=2,
                                   connectionstyle='arc3,rad=-0.3'))
        ax.text(mid, y + 1.1, r'$\times 6 - \mathrm{prev}$', fontsize=8,
                ha='center', va='center', color=ACCENT2)

    ax.axhline(y=y - 0.1, color=DARK, lw=1, zorder=1)

    ax.text(2.5, 1.2, 'Pell recurrence: $c_{n+2} = 6\\,c_{n+1} - c_n$',
            fontsize=14, ha='center', va='center', color=ACCENT4, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=CREAM, alpha=0.8))

    ax.set_xlim(0.4, 5.5)
    ax.set_ylim(0.5, 5)
    ax.axis('off')
    ax.set_title("B-Branch Hypotenuses: A Pell Sequence in Disguise",
                 fontsize=16, fontweight='bold', color=DARK, pad=15)
    save(fig, "fig12_pell_number_line.png")


# ============================================================
# FIG 13: B-branch vine (vertical path with ratios)
# ============================================================
def fig13_b_branch_vine():
    fig, ax = plt.subplots(1, 1, figsize=(10, 16))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    triple = np.array([3, 4, 5])
    triples = [tuple(triple)]
    for _ in range(5):
        triple = BB @ triple
        triples.append(tuple(triple))

    num = len(triples)
    for i, (a, b, c) in enumerate(triples):
        a, b, c = int(a), int(b), int(c)
        y = i * 2.5 + 1
        x = 5

        # Vine stem
        if i < num - 1:
            ax.plot([x, x], [y + 0.7, y + 2.5 - 0.7], color=ACCENT3, lw=3, zorder=1)
            for dy in np.linspace(y + 1.0, y + 2.0, 3):
                side = 0.3 if int(dy * 10) % 2 == 0 else -0.3
                ax.plot([x, x + side], [dy, dy + 0.15], color=ACCENT3, lw=1.5, alpha=0.5)

        circle = plt.Circle((x, y), 0.65, facecolor=CREAM, edgecolor=DARK,
                             linewidth=2, zorder=5)
        ax.add_patch(circle)

        ax.text(x, y + 0.15, f'$({a},{b},{c})$', fontsize=10,
                ha='center', va='center', color=DARK, fontweight='bold', zorder=6)

        ratio = b / a
        ax.text(x + 2.5, y + 0.15, f'$b/a = {b}/{a}$\n$\\approx {ratio:.6f}$',
                fontsize=9, ha='left', va='center', color=SLATE, zorder=6)

        ax.text(x - 2.5, y, f'$n = {i}$', fontsize=11, ha='center', va='center',
                color=ACCENT2, fontweight='bold')

    ax.text(5, num * 2.5 + 1.5,
            f'$b/a \\to 1 + \\sqrt{{2}} \\approx {1 + np.sqrt(2):.6f}$',
            fontsize=13, ha='center', va='center', color=ACCENT1, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=GLOW, alpha=0.4))

    ax.set_xlim(1, 12)
    ax.set_ylim(-0.5, num * 2.5 + 3)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title("The Pure $B$-Path: A Vine of Converging Ratios",
                 fontsize=15, fontweight='bold', color=DARK, pad=15)
    save(fig, "fig13_b_branch_vine.png")


# ============================================================
# FIG 14: Grand Mosaic -- eight theorems compass rose
# ============================================================
def fig14_grand_mosaic():
    fig, ax = plt.subplots(1, 1, figsize=(16, 16))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    cx, cy = 8, 8
    radius = 5.5

    # Central triangle
    tri = plt.Polygon([(cx - 0.8, cy - 0.6), (cx + 0.8, cy - 0.6), (cx, cy + 0.8)],
                       facecolor=GLOW, edgecolor=DARK, linewidth=3, zorder=10, alpha=0.7)
    ax.add_patch(tri)
    ax.text(cx, cy - 0.1, '$(a, b, c)$', fontsize=14, ha='center', va='center',
            color=DARK, fontweight='bold', zorder=11)

    theorems = [
        ('Lorentz\nPreservation', '$M^T Q M = Q$', ACCENT2),
        ('Pythagorean\nPreservation', '$a^2+b^2=c^2$', ACCENT1),
        ('Tree\nSoundness', 'Every node\nis Pythagorean', ACCENT3),
        ('Factoring\nIdentity', '$(c-b)(c+b)=a^2$', ACCENT5),
        ('Euclid\nParametrization', '$(m^2-n^2, 2mn,$\n$m^2+n^2)$', ACCENT4),
        ('Pell\nRecurrence', '$c_{n+2}=6c_{n+1}-c_n$', GOLD),
        ('A-Branch\nDescent', 'Consecutive\nparams descend', ACCENT2),
        ('Determinants', '$\\det = \\pm 1$\norientation', ACCENT1),
    ]

    for i, (name, formula, color) in enumerate(theorems):
        angle = i * 2 * np.pi / 8 - np.pi / 2
        tx = cx + radius * np.cos(angle)
        ty = cy + radius * np.sin(angle)

        ax.plot([cx, tx], [cy, ty], color=color, lw=2, alpha=0.4, zorder=1)

        box = FancyBboxPatch((tx - 1.5, ty - 0.9), 3, 1.8,
                              boxstyle="round,pad=0.2", facecolor=CREAM,
                              edgecolor=color, linewidth=2.5, zorder=5)
        ax.add_patch(box)

        ax.text(tx, ty + 0.35, name, fontsize=10, ha='center', va='center',
                color=color, fontweight='bold', zorder=6)
        ax.text(tx, ty - 0.35, formula, fontsize=8, ha='center', va='center',
                color=DARK, zorder=6)

        num_circle = plt.Circle((tx - 1.2, ty + 0.6), 0.25, facecolor=color,
                                 edgecolor=DARK, linewidth=1, zorder=7)
        ax.add_patch(num_circle)
        ax.text(tx - 1.2, ty + 0.6, str(i + 1), fontsize=9, ha='center', va='center',
                color='white', fontweight='bold', zorder=8)

    border = plt.Circle((cx, cy), radius + 2, facecolor='none',
                         edgecolor=DARK, linewidth=2, linestyle='--', zorder=0)
    ax.add_patch(border)

    ax.set_xlim(0, 16)
    ax.set_ylim(0, 16)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title("The Grand Mosaic: Eight Theorems, One Pythagorean Triple",
                 fontsize=18, fontweight='bold', color=DARK, pad=20)
    save(fig, "fig14_grand_mosaic.png")


# ============================================================
# FIG 15: Cheat sheet -- all eight theorem statements
# ============================================================
def fig15_cheat_sheet():
    fig, ax = plt.subplots(1, 1, figsize=(14, 18))
    fig.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    theorems = [
        ("Theorem 1: Lorentz Form Preservation",
         "$M^T \\eta\\, M = \\eta$  where  $\\eta = \\mathrm{diag}(1,1,-1)$",
         "Each Berggren matrix preserves the Lorentz quadratic form."),

        ("Theorem 2: Pythagorean Preservation",
         "If $a^2 + b^2 = c^2$, then $(a')^2 + (b')^2 = (c')^2$",
         "The Berggren matrices map Pythagorean triples to Pythagorean triples."),

        ("Theorem 3: Tree Soundness",
         "Every node of the Berggren tree satisfies $a^2 + b^2 = c^2$",
         "By induction from the root (3,4,5)."),

        ("Theorem 4: The Factoring Identity",
         "$(c - b)(c + b) = a^2$",
         "A rearrangement of the Pythagorean equation reveals factors."),

        ("Theorem 5: Euclid's Parametrization",
         "$(m^2 - n^2)^2 + (2mn)^2 = (m^2 + n^2)^2$",
         "A universal formula producing all Pythagorean triples."),

        ("Theorem 6: Pell Recurrence on the B-Branch",
         "$c_{n+2} = 6\\,c_{n+1} - c_n$",
         "The B-branch hypotenuses obey a second-order linear recurrence."),

        ("Theorem 7: A-Branch Consecutive Descent",
         "$B_A^{-1}$ maps $(m, m-1)$ triples to $(m-1, m-2)$ triples",
         "Consecutive Euclid parameters descend to the root via A-steps alone."),

        ("Theorem 8: Determinants and Orientation",
         "$\\det(B_A) = +1, \\quad \\det(B_B) = -1, \\quad \\det(B_C) = +1$",
         "$B_B$ is an improper Lorentz transformation; $B_A$ and $B_C$ are proper."),
    ]

    y = 17
    colors = [ACCENT2, ACCENT1, ACCENT3, ACCENT5, ACCENT4, GOLD, ACCENT2, ACCENT1]

    for i, (title, formula, summary) in enumerate(theorems):
        color = colors[i]
        ax.text(0.5, y, title, fontsize=14, ha='left', va='top',
                color=color, fontweight='bold', transform=ax.transData)
        ax.text(1, y - 0.7, formula, fontsize=12, ha='left', va='top',
                color=DARK, transform=ax.transData)
        ax.text(1, y - 1.5, summary, fontsize=10, ha='left', va='top',
                color=SLATE, style='italic', transform=ax.transData)
        ax.axhline(y=y - 2.0, color=DARK, lw=0.5, alpha=0.3, xmin=0.03, xmax=0.97)
        y -= 2.2

    ax.set_xlim(0, 14)
    ax.set_ylim(-1, 18)
    ax.axis('off')

    ax.text(7, 17.8, "EIGHT THEOREMS", fontsize=20, ha='center', va='center',
            color=DARK, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor=GLOW, alpha=0.3, edgecolor=DARK))
    ax.text(7, 17.0, "The Berggren\u2013Lorentz Correspondence", fontsize=14, ha='center',
            va='center', color=SLATE, style='italic')
    save(fig, "fig15_cheat_sheet.png")


# ============================================================
# Generate all figures
# ============================================================
if __name__ == '__main__':
    print("Generating Chapter 5 illustrations...")
    fig01_berggren_tree()
    fig02_three_triangles()
    fig03_null_cone()
    fig04_spacetime_comparison()
    fig05_mirror_triangle()
    fig06_pythagorean_check()
    fig07_null_cone_regions()
    fig08_factoring_vice()
    fig09_brahmagupta_fibonacci()
    fig10_euclid_grid()
    fig11_a_staircase()
    fig12_pell_number_line()
    fig13_b_branch_vine()
    fig14_grand_mosaic()
    fig15_cheat_sheet()
    print("Done! All Chapter 5 images saved to images/")

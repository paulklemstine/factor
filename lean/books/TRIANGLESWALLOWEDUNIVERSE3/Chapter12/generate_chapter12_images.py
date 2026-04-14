#!/usr/bin/env python3
"""Generate all illustrations for Chapter 12: The Fourth Dimension of Pythagoras."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Arc
import matplotlib.patheffects as pe
import numpy as np
import os
from math import gcd, sqrt
from itertools import combinations

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
os.makedirs(OUT, exist_ok=True)

# Color palette (matching Chapter 1/2 style)
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
# Helper: find primitive Pythagorean quadruples
# ============================================================
def find_primitive_quadruples(max_d=50):
    """Find primitive Pythagorean quadruples (a,b,c,d) with a<=b<=c, gcd=1."""
    quads = []
    for d in range(1, max_d + 1):
        d2 = d * d
        for c in range(0, d):
            rem = d2 - c * c
            for b in range(0, int(sqrt(rem)) + 1):
                a2 = rem - b * b
                if a2 < 0:
                    continue
                a = int(round(sqrt(a2)))
                if a * a != a2:
                    continue
                if a > b:
                    continue
                if b > c:
                    continue
                if a == 0 and b == 0:
                    continue
                g = gcd(gcd(a, b), gcd(c, d))
                if g == 1:
                    quads.append((a, b, c, d))
    return quads


# ============================================================
# ILLUSTRATION 1: Table of primitive quadruples in hypercube wireframe
# ============================================================
def fig01_quadruple_table():
    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(16, 10),
                                             gridspec_kw={'width_ratios': [1, 1.2]})
    fig.set_facecolor(SAND)
    for ax in [ax_left, ax_right]:
        ax.set_facecolor(SAND)

    # Left panel: hypercube wireframe with glowing points
    ax = ax_left
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Points on the Three-Sphere', fontsize=14, color=DARK, fontweight='bold', pad=10)

    # Draw a translucent circle representing the 3-sphere projection
    circle = plt.Circle((0, 0), 1.15, fill=True, facecolor=LIGHT_BLUE, edgecolor=ACCENT2,
                         alpha=0.2, linewidth=2)
    ax.add_patch(circle)

    # Draw hypercube wireframe (projected tesseract)
    s = 1.0
    si = 0.5
    outer = [(-s, -s), (s, -s), (s, s), (-s, s)]
    inner = [(-si, -si), (si, -si), (si, si), (-si, si)]
    for i in range(4):
        j = (i + 1) % 4
        ax.plot([outer[i][0], outer[j][0]], [outer[i][1], outer[j][1]],
                color=SLATE, linewidth=1.5, alpha=0.4)
        ax.plot([inner[i][0], inner[j][0]], [inner[i][1], inner[j][1]],
                color=SLATE, linewidth=1, alpha=0.3)
        ax.plot([outer[i][0], inner[i][0]], [outer[i][1], inner[i][1]],
                color=SLATE, linewidth=1, alpha=0.3)

    # Place glowing points (projections of quadruple directions)
    quads = find_primitive_quadruples(20)[:15]
    np.random.seed(42)
    for i, (a, b, c, d) in enumerate(quads):
        # Project (a,b,c) onto 2D using a simple projection
        angle = 2 * np.pi * i / len(quads) + 0.3
        r = 0.6 + 0.4 * (c / d)
        px, py = r * np.cos(angle), r * np.sin(angle)
        # Dotted line from origin
        ax.plot([0, px], [0, py], '--', color=GOLD, linewidth=0.8, alpha=0.5)
        # Glowing point
        ax.plot(px, py, 'o', color=GLOW, markersize=10, markeredgecolor=ACCENT5,
                markeredgewidth=1.5, zorder=10)

    # Origin
    ax.plot(0, 0, 'o', color=DARK, markersize=6, zorder=11)
    ax.text(0.08, -0.12, 'O', fontsize=10, color=DARK)

    # Right panel: table of quadruples
    ax = ax_right
    ax.axis('off')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 20)
    ax.set_title('First 15 Primitive Pythagorean Quadruples', fontsize=14,
                 color=DARK, fontweight='bold', pad=10)

    headers = ['$a$', '$b$', '$c$', '$d$', 'Check: $a^2+b^2+c^2=d^2$']
    col_x = [1, 2.5, 4, 5.5, 8]
    y_start = 18.5
    row_h = 1.1

    # Header
    for cx, h in zip(col_x, headers):
        ax.text(cx, y_start, h, fontsize=11, ha='center', va='center',
                color=DARK, fontweight='bold')
    ax.plot([0.3, 9.7], [y_start - 0.5, y_start - 0.5], color=DARK, linewidth=1.5)

    for i, (a, b, c, d) in enumerate(quads):
        y = y_start - (i + 1) * row_h
        vals = [str(a), str(b), str(c), str(d),
                f'${a**2}+{b**2}+{c**2}={d**2}$']
        bg_color = CREAM if i % 2 == 0 else SAND
        rect = patches.FancyBboxPatch((0.3, y - 0.4), 9.4, 0.85,
                                       boxstyle="round,pad=0.05",
                                       facecolor=bg_color, edgecolor='none', alpha=0.6)
        ax.add_patch(rect)
        for cx, v in zip(col_x, vals):
            ax.text(cx, y, v, fontsize=10, ha='center', va='center', color=DARK)

    fig.suptitle('Pythagorean Quadruples on the Three-Sphere',
                 fontsize=18, color=DARK, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    save(fig, 'fig01_quadruple_table.png')


# ============================================================
# ILLUSTRATION 2: Triangle vs Sphere — triples vs quadruples
# ============================================================
def fig02_triangle_to_sphere():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
    fig.set_facecolor(SAND)
    for ax in [ax1, ax2]:
        ax.set_facecolor(SAND)

    # Left: right triangle on integer grid
    ax = ax1
    ax.set_xlim(-0.5, 5.5)
    ax.set_ylim(-0.5, 4.5)
    ax.set_aspect('equal')
    ax.set_title('Pythagorean Triple: $a^2 + b^2 = c^2$', fontsize=13,
                 color=DARK, fontweight='bold')

    # Grid
    for i in range(7):
        ax.axhline(i - 0.5, color=SLATE, alpha=0.1, linewidth=0.5)
        ax.axvline(i - 0.5, color=SLATE, alpha=0.1, linewidth=0.5)

    # Grid dots
    for i in range(6):
        for j in range(5):
            ax.plot(i, j, '.', color=SLATE, markersize=3, alpha=0.3)

    # Triangle 3-4-5
    tri_x = [0, 4, 0, 0]
    tri_y = [0, 0, 3, 0]
    ax.fill(tri_x[:3], tri_y[:3], alpha=0.15, color=ACCENT2)
    ax.plot(tri_x, tri_y, color=DARK, linewidth=2.5, zorder=5)

    # Right angle mark
    sq = 0.3
    ax.plot([sq, sq, 0], [0, sq, sq], color=DARK, linewidth=1.5)

    # Labels
    ax.text(2, -0.4, '$b = 4$', fontsize=14, ha='center', color=ACCENT2, fontweight='bold')
    ax.text(-0.5, 1.5, '$a = 3$', fontsize=14, ha='center', color=ACCENT1, fontweight='bold')
    ax.text(2.4, 1.9, '$c = 5$', fontsize=14, ha='center', color=ACCENT4, fontweight='bold',
            rotation=-37)
    ax.text(2.5, 4, '$3^2 + 4^2 = 5^2$', fontsize=13, ha='center', color=DARK,
            fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=CREAM, edgecolor=GOLD, alpha=0.9))
    ax.axis('off')

    # Right: sphere with point and radial line
    ax = ax2
    ax.set_xlim(-1.8, 1.8)
    ax.set_ylim(-1.8, 1.8)
    ax.set_aspect('equal')
    ax.set_title('Pythagorean Quadruple: $a^2 + b^2 + c^2 = d^2$', fontsize=13,
                 color=DARK, fontweight='bold')

    # Translucent sphere
    theta = np.linspace(0, 2 * np.pi, 200)
    ax.fill(1.3 * np.cos(theta), 1.3 * np.sin(theta), alpha=0.12, color=ACCENT2)
    ax.plot(1.3 * np.cos(theta), 1.3 * np.sin(theta), color=ACCENT2, linewidth=2, alpha=0.5)

    # Axes (3D projected)
    ax.annotate('', xy=(1.6, 0), xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=2))
    ax.annotate('', xy=(0, 1.6), xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', color=ACCENT2, lw=2))
    ax.annotate('', xy=(-0.9, -0.9), xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', color=ACCENT3, lw=2))

    ax.text(1.65, -0.15, '$a$', fontsize=14, color=ACCENT1, fontweight='bold')
    ax.text(0.1, 1.65, '$b$', fontsize=14, color=ACCENT2, fontweight='bold')
    ax.text(-1.05, -1.05, '$c$', fontsize=14, color=ACCENT3, fontweight='bold')

    # Point on sphere
    px, py = 0.7, 0.95
    ax.plot(px, py, 'o', color=GLOW, markersize=14, markeredgecolor=ACCENT5,
            markeredgewidth=2, zorder=10)
    ax.text(px + 0.15, py + 0.15, '$(a, b, c)$', fontsize=12, color=DARK, fontweight='bold')

    # Dashed radial line
    ax.plot([0, px], [0, py], '--', color=DARK, linewidth=2, zorder=5)
    ax.text(0.15, 0.55, '$d$', fontsize=14, color=DARK, fontweight='bold', rotation=55)

    # Origin
    ax.plot(0, 0, 'o', color=DARK, markersize=5, zorder=11)

    ax.text(0, -1.6, '$a^2 + b^2 + c^2 = d^2$', fontsize=13, ha='center', color=DARK,
            fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=CREAM, edgecolor=GOLD, alpha=0.9))
    ax.axis('off')

    fig.suptitle('From Triangles to Spheres', fontsize=18, color=DARK, fontweight='bold', y=1.0)
    plt.tight_layout()
    save(fig, 'fig02_triangle_to_sphere.png')


# ============================================================
# ILLUSTRATION 3: The Magician's Bridge
# ============================================================
def fig03_bridge():
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.set_aspect('equal')
    ax.axis('off')

    # River
    river_x = np.linspace(0, 14, 300)
    river_y1 = 2.5 + 0.3 * np.sin(river_x * 0.8)
    river_y2 = 1.5 + 0.3 * np.sin(river_x * 0.8 + 0.5)
    ax.fill_between(river_x, river_y1, river_y2, color=LIGHT_BLUE, alpha=0.5)
    ax.plot(river_x, river_y1, color=ACCENT2, linewidth=1, alpha=0.5)
    ax.plot(river_x, river_y2, color=ACCENT2, linewidth=1, alpha=0.5)

    # River label
    ax.text(7, 1.9, '$a^2 + b^2$', fontsize=16, ha='center', va='center',
            color=ACCENT2, fontweight='bold', fontstyle='italic', alpha=0.8)

    # Bridge arch
    arch_x = np.linspace(3, 11, 200)
    arch_y = 3.0 + 4.0 * np.sin(np.pi * (arch_x - 3) / 8)
    ax.fill_between(arch_x, 2.5, arch_y, color='#C4A882', alpha=0.6)
    ax.plot(arch_x, arch_y, color=DARK, linewidth=3)

    # Stone pattern on arch
    for i in range(4, 11):
        y_base = 3.0 + 4.0 * np.sin(np.pi * (i - 3) / 8)
        ax.plot([i, i], [2.5, y_base - 0.2], color=DARK, linewidth=0.5, alpha=0.3)

    # Keystone = equals sign
    ax.text(7, 6.8, '=', fontsize=40, ha='center', va='center',
            color=GOLD, fontweight='bold', zorder=10,
            bbox=dict(boxstyle='round,pad=0.2', facecolor=CREAM, edgecolor=GOLD, linewidth=2))

    # Left bank: Geometry
    left_box = FancyBboxPatch((0.5, 4), 3.5, 3.5, boxstyle="round,pad=0.3",
                               facecolor=LIGHT_BLUE, edgecolor=ACCENT2, linewidth=2, alpha=0.8)
    ax.add_patch(left_box)
    ax.text(2.25, 6.8, 'GEOMETRY', fontsize=12, ha='center', color=ACCENT2, fontweight='bold')
    # Small sphere icon
    theta = np.linspace(0, 2 * np.pi, 100)
    ax.plot(2.25 + 0.6 * np.cos(theta), 5.5 + 0.6 * np.sin(theta),
            color=ACCENT2, linewidth=2)
    ax.text(2.25, 4.5, '$a^2+b^2+c^2=d^2$', fontsize=10, ha='center', color=DARK,
            fontweight='bold')

    # Right bank: Arithmetic
    right_box = FancyBboxPatch((10, 4), 3.5, 3.5, boxstyle="round,pad=0.3",
                                facecolor=LIGHT_RED, edgecolor=ACCENT1, linewidth=2, alpha=0.8)
    ax.add_patch(right_box)
    ax.text(11.75, 6.8, 'ARITHMETIC', fontsize=12, ha='center', color=ACCENT1, fontweight='bold')
    ax.text(11.75, 5.7, '$(d-c)$', fontsize=16, ha='center', color=DARK, fontweight='bold')
    ax.text(11.75, 5.1, '$\\times$', fontsize=18, ha='center', color=ACCENT1, fontweight='bold')
    ax.text(11.75, 4.5, '$(d+c)$', fontsize=16, ha='center', color=DARK, fontweight='bold')

    # Title
    ax.text(7, 8.5, "The Magician's Bridge", fontsize=20, ha='center',
            color=DARK, fontweight='bold')
    ax.text(7, 0.5, '$(d-c)(d+c) = a^2 + b^2$', fontsize=16, ha='center',
            color=DARK, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=CREAM, edgecolor=GOLD, linewidth=2))

    save(fig, 'fig03_bridge.png')


# ============================================================
# ILLUSTRATION 4: The Parametric Machine
# ============================================================
def fig04_quadruple_machine():
    fig, ax = plt.subplots(1, 1, figsize=(14, 9))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Machine body
    machine = FancyBboxPatch((3, 1.5), 8, 7, boxstyle="round,pad=0.4",
                              facecolor='#D5C4A1', edgecolor=DARK, linewidth=3)
    ax.add_patch(machine)

    # Inner mechanism area
    inner = FancyBboxPatch((5.5, 2.5), 3, 5, boxstyle="round,pad=0.2",
                            facecolor=CREAM, edgecolor=SLATE, linewidth=1.5, alpha=0.8)
    ax.add_patch(inner)

    # Gears (decorative circles)
    for cx, cy, r in [(6.2, 4, 1), (7, 5.5, 1), (7.8, 4, 1)]:
        theta = np.linspace(0, 2 * np.pi, 100)
        ax.plot(cx + r * 0.5 * np.cos(theta), cy + r * 0.5 * np.sin(theta),
                color=SLATE, linewidth=1.5, alpha=0.4)
        # Gear teeth
        for k in range(8):
            a = 2 * np.pi * k / 8
            ax.plot([cx + r * 0.45 * np.cos(a), cx + r * 0.55 * np.cos(a)],
                    [cy + r * 0.45 * np.sin(a), cy + r * 0.55 * np.sin(a)],
                    color=SLATE, linewidth=1.5, alpha=0.4)

    # Input dials (left side)
    params = ['$m$', '$n$', '$p$', '$q$']
    values_label = ['1', '1', '1', '0']
    colors = [ACCENT1, ACCENT2, ACCENT3, ACCENT5]
    for i, (p, v, c) in enumerate(zip(params, values_label, colors)):
        y = 7.5 - i * 1.5
        # Dial circle
        circle = plt.Circle((2, y), 0.55, fill=True, facecolor=CREAM,
                            edgecolor=c, linewidth=2.5)
        ax.add_patch(circle)
        ax.text(2, y, v, fontsize=16, ha='center', va='center', color=DARK, fontweight='bold')
        ax.text(0.8, y, p, fontsize=16, ha='center', va='center', color=c, fontweight='bold')
        # Arrow to machine
        ax.annotate('', xy=(3.2, y), xytext=(2.6, y),
                    arrowprops=dict(arrowstyle='->', color=c, lw=2))

    # Output displays (right side)
    outputs = ['$a$', '$b$', '$c$', '$d$']
    out_vals = ['1', '2', '−2', '3']
    formulas = ['$m^2+n^2-p^2-q^2$', '$2(mq+np)$', '$2(nq-mp)$', '$m^2+n^2+p^2+q^2$']
    for i, (o, v, f) in enumerate(zip(outputs, out_vals, formulas)):
        y = 7.5 - i * 1.5
        # Display box
        disp = FancyBboxPatch((11.5, y - 0.4), 1.2, 0.8, boxstyle="round,pad=0.1",
                               facecolor='#1a1a2e', edgecolor=GOLD, linewidth=2)
        ax.add_patch(disp)
        ax.text(12.1, y, v, fontsize=16, ha='center', va='center', color=GLOW, fontweight='bold')
        ax.text(13.2, y, o, fontsize=14, ha='left', va='center', color=DARK, fontweight='bold')
        # Arrow from machine
        ax.annotate('', xy=(11.4, y), xytext=(10.8, y),
                    arrowprops=dict(arrowstyle='->', color=GOLD, lw=2))
        # Formula placard
        ax.text(7, y, f, fontsize=8, ha='center', va='center', color=SLATE,
                bbox=dict(boxstyle='round,pad=0.15', facecolor='#EDE4D3', edgecolor=SLATE,
                          linewidth=0.8, alpha=0.7))

    # Title
    ax.text(7, 9.5, 'The Quadruple Machine', fontsize=20, ha='center',
            color=DARK, fontweight='bold')

    # Verification
    ax.text(7, 0.7, 'Check: $1^2 + 2^2 + (-2)^2 = 1 + 4 + 4 = 9 = 3^2$  OK',
            fontsize=13, ha='center', color=ACCENT3, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=CREAM, edgecolor=ACCENT3, linewidth=1.5))

    save(fig, 'fig04_quadruple_machine.png')


# ============================================================
# ILLUSTRATION 5: Hypotenuse decomposition number line
# ============================================================
def fig05_hypotenuse_decomposition():
    fig, ax = plt.subplots(1, 1, figsize=(12, 5))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.set_xlim(-0.5, 11)
    ax.set_ylim(-1, 4.5)
    ax.axis('off')

    # Example: m=2, n=1, p=1, q=1
    # d = 4+1+1+1 = 7,  m²+n² = 5, p²+q² = 2
    m, n, p, q = 2, 1, 1, 1
    m2, n2, p2, q2 = m**2, n**2, p**2, q**2
    total = m2 + n2 + p2 + q2  # d = 7
    first_norm = m2 + n2  # 5
    second_norm = p2 + q2  # 2

    # Scale for drawing
    scale = 10.0 / total
    y_main = 3
    bar_h = 0.7

    # Main bar: d
    ax.barh(y_main, total * scale, left=0, height=bar_h, color=SLATE, alpha=0.2,
            edgecolor=DARK, linewidth=2)

    # First norm (blue): m² + n²
    ax.barh(y_main, first_norm * scale, left=0, height=bar_h,
            color=ACCENT2, alpha=0.4, edgecolor=DARK, linewidth=1.5)
    # Second norm (red): p² + q²
    ax.barh(y_main, second_norm * scale, left=first_norm * scale, height=bar_h,
            color=ACCENT1, alpha=0.4, edgecolor=DARK, linewidth=1.5)

    # Sub-decomposition bar (lower)
    y_sub = 1.5
    # m² (dark blue)
    ax.barh(y_sub, m2 * scale, left=0, height=bar_h,
            color=ACCENT2, alpha=0.7, edgecolor=DARK, linewidth=1.5)
    # n² (light blue)
    ax.barh(y_sub, n2 * scale, left=m2 * scale, height=bar_h,
            color=LIGHT_BLUE, alpha=0.8, edgecolor=DARK, linewidth=1.5)
    # p² (dark red)
    ax.barh(y_sub, p2 * scale, left=first_norm * scale, height=bar_h,
            color=ACCENT1, alpha=0.7, edgecolor=DARK, linewidth=1.5)
    # q² (light red)
    ax.barh(y_sub, q2 * scale, left=(first_norm + p2) * scale, height=bar_h,
            color=LIGHT_RED, alpha=0.8, edgecolor=DARK, linewidth=1.5)

    # Labels - main bar
    ax.text(first_norm * scale / 2, y_main + 0.05, f'$m^2+n^2 = {first_norm}$',
            fontsize=12, ha='center', va='center', color='white', fontweight='bold')
    ax.text(first_norm * scale + second_norm * scale / 2, y_main + 0.05,
            f'$p^2+q^2 = {second_norm}$',
            fontsize=12, ha='center', va='center', color='white', fontweight='bold')

    # Labels - sub-bar
    ax.text(m2 * scale / 2, y_sub + 0.05, f'$m^2={m2}$',
            fontsize=10, ha='center', va='center', color='white', fontweight='bold')
    ax.text(m2 * scale + n2 * scale / 2, y_sub + 0.05, f'$n^2={n2}$',
            fontsize=10, ha='center', va='center', color=DARK, fontweight='bold')
    ax.text(first_norm * scale + p2 * scale / 2, y_sub + 0.05, f'$p^2={p2}$',
            fontsize=10, ha='center', va='center', color='white', fontweight='bold')
    ax.text((first_norm + p2) * scale + q2 * scale / 2, y_sub + 0.05, f'$q^2={q2}$',
            fontsize=10, ha='center', va='center', color=DARK, fontweight='bold')

    # Brace for d
    ax.annotate('', xy=(0, y_main + 0.6), xytext=(total * scale, y_main + 0.6),
                arrowprops=dict(arrowstyle='<->', color=DARK, lw=2))
    ax.text(total * scale / 2, y_main + 0.9, f'$d = {total}$',
            fontsize=16, ha='center', color=DARK, fontweight='bold')

    # Connecting arrows
    for x in [0, m2 * scale, first_norm * scale, (first_norm + p2) * scale, total * scale]:
        ax.plot([x, x], [y_sub + bar_h / 2, y_main - bar_h / 2], '--',
                color=SLATE, linewidth=0.8, alpha=0.5)

    # Caption
    ax.text(total * scale / 2, 0.2,
            '"The hypotenuse is a sum of two sums-of-two-squares"',
            fontsize=12, ha='center', va='center', color=DARK, fontstyle='italic',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=CREAM, edgecolor=GOLD, alpha=0.8))

    # Title
    ax.text(total * scale / 2, 4.2, 'Hypotenuse Decomposition',
            fontsize=18, ha='center', color=DARK, fontweight='bold')

    save(fig, 'fig05_hypotenuse_decomposition.png')


# ============================================================
# ILLUSTRATION 6: Collision — two roads to the hilltop
# ============================================================
def fig06_collision_roads():
    fig, ax = plt.subplots(1, 1, figsize=(14, 9))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Hilltop
    hill_x = np.linspace(2, 12, 200)
    hill_y = 4 + 4 * np.exp(-((hill_x - 7) / 2.5) ** 2)
    ax.fill_between(hill_x, 0, hill_y, color=ACCENT3, alpha=0.15)
    ax.plot(hill_x, hill_y, color=ACCENT3, linewidth=2, alpha=0.5)

    # Hilltop label
    ax.text(7, 8.3, '$d^2 = 81$', fontsize=20, ha='center', va='center',
            color=DARK, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=GLOW, edgecolor=GOLD, linewidth=2))

    # Left road (path 1): (1, 4, 8, 9)
    road1_x = np.array([1, 2.5, 3.5, 5, 6, 7])
    road1_y = np.array([1.5, 2.5, 3.5, 5, 6.5, 7.8])
    # Smooth
    t1 = np.linspace(0, 1, 200)
    from numpy import interp
    road1_xs = np.interp(t1, np.linspace(0, 1, len(road1_x)), road1_x)
    road1_ys = np.interp(t1, np.linspace(0, 1, len(road1_y)), road1_y)
    ax.plot(road1_xs, road1_ys, color=ACCENT2, linewidth=3, alpha=0.8)

    # Milestones on road 1
    milestones1 = [(2, 2.2, '1'), (3.2, 3.3, '4'), (5.2, 5.3, '8')]
    for mx, my, label in milestones1:
        ax.plot(mx, my, 's', color=ACCENT2, markersize=15, markeredgecolor=DARK,
                markeredgewidth=1.5, zorder=10)
        ax.text(mx, my, label, fontsize=11, ha='center', va='center', color='white',
                fontweight='bold', zorder=11)

    # Right road (path 2): (4, 4, 7, 9)
    road2_x = np.array([13, 11.5, 10.5, 9, 8, 7])
    road2_y = np.array([1.5, 2.5, 3.5, 5, 6.5, 7.8])
    road2_xs = np.interp(t1, np.linspace(0, 1, len(road2_x)), road2_x)
    road2_ys = np.interp(t1, np.linspace(0, 1, len(road2_y)), road2_y)
    ax.plot(road2_xs, road2_ys, color=ACCENT1, linewidth=3, alpha=0.8)

    # Milestones on road 2
    milestones2 = [(12, 2.2, '4'), (10.8, 3.3, '4'), (8.8, 5.3, '7')]
    for mx, my, label in milestones2:
        ax.plot(mx, 'o' if False else my, 's', color=ACCENT1, markersize=15,
                markeredgecolor=DARK, markeredgewidth=1.5, zorder=10)
        ax.text(mx, my, label, fontsize=11, ha='center', va='center', color='white',
                fontweight='bold', zorder=11)

    # Road labels
    ax.text(1.5, 0.8, 'Path 1: $(1, 4, 8, 9)$', fontsize=12, color=ACCENT2, fontweight='bold')
    ax.text(10.5, 0.8, 'Path 2: $(4, 4, 7, 9)$', fontsize=12, color=ACCENT1, fontweight='bold')

    # Magnifying glass at junction
    mg_x, mg_y = 7, 7.0
    mg_circle = plt.Circle((mg_x, mg_y - 0.5), 1.0, fill=True, facecolor=CREAM,
                            edgecolor=DARK, linewidth=2.5, alpha=0.9, zorder=15)
    ax.add_patch(mg_circle)
    # Handle
    ax.plot([mg_x + 0.7, mg_x + 1.5], [mg_y - 1.2, mg_y - 2.0], color=DARK, linewidth=4, zorder=15)

    # Content inside magnifying glass
    ax.text(mg_x, mg_y - 0.2, '$15$', fontsize=18, ha='center', va='center',
            color=ACCENT5, fontweight='bold', zorder=16)
    ax.text(mg_x, mg_y - 0.9, '$(c_1-c_2)(c_1+c_2)$', fontsize=8, ha='center',
            va='center', color=DARK, zorder=16)

    # Firefly (factor 3)
    ax.plot(9.5, 6.2, '*', color=GLOW, markersize=20, markeredgecolor=ACCENT5,
            markeredgewidth=1, zorder=20)
    ax.text(9.5, 5.5, '$3$', fontsize=14, ha='center', color=ACCENT5, fontweight='bold')
    ax.text(9.5, 5.0, 'factor!', fontsize=9, ha='center', color=DARK, fontstyle='italic')

    # Title
    ax.text(7, 9.7, 'The Collision Detector', fontsize=20, ha='center',
            color=DARK, fontweight='bold')

    save(fig, 'fig06_collision_roads.png')


# ============================================================
# ILLUSTRATION 7: Scaling tetrahedra
# ============================================================
def fig07_scaling_tetrahedra():
    fig, ax = plt.subplots(1, 1, figsize=(12, 7))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.set_xlim(-1, 13)
    ax.set_ylim(-1, 8)
    ax.axis('off')

    def draw_tetrahedron(ax, cx, cy, scale, label, color, values):
        """Draw a simple 2D projection of a tetrahedron."""
        s = scale
        # Vertices of projected tetrahedron
        v = [(cx, cy), (cx + 2 * s, cy), (cx + s, cy + 1.5 * s), (cx + 0.7 * s, cy + 0.8 * s)]

        # Faces (triangles)
        faces = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]
        for face in faces:
            tri_x = [v[face[0]][0], v[face[1]][0], v[face[2]][0]]
            tri_y = [v[face[0]][1], v[face[1]][1], v[face[2]][1]]
            ax.fill(tri_x, tri_y, alpha=0.1, color=color)

        # Edges
        for i in range(4):
            for j in range(i + 1, 4):
                ax.plot([v[i][0], v[j][0]], [v[i][1], v[j][1]],
                        color=color, linewidth=2, alpha=0.7)

        # Vertices
        for i, (vx, vy) in enumerate(v):
            ax.plot(vx, vy, 'o', color=color, markersize=8, markeredgecolor=DARK,
                    markeredgewidth=1.5, zorder=10)

        # Label beneath
        ax.text(cx + s, cy - 0.6, label, fontsize=13, ha='center', color=DARK, fontweight='bold')
        ax.text(cx + s, cy - 1.1, values, fontsize=11, ha='center', color=color)

    # Small tetrahedron
    draw_tetrahedron(ax, 0.5, 1.5, 1.2, '$(1, 2, 2, 3)$', ACCENT2, '$1^2+2^2+2^2=3^2$')

    # Large tetrahedron
    draw_tetrahedron(ax, 5, 0.5, 3.0, '$(3, 6, 6, 9)$', ACCENT1, '$3^2+6^2+6^2=9^2$')

    # Dotted connecting lines
    small_pts = [(0.5, 1.5), (2.9, 1.5), (1.7, 3.3)]
    large_pts = [(5, 0.5), (11, 0.5), (8, 5.0)]
    for sp, lp in zip(small_pts, large_pts):
        ax.plot([sp[0], lp[0]], [sp[1], lp[1]], '--', color=SLATE, linewidth=1.2, alpha=0.5)

    # Scale factor annotation
    ax.text(3.5, 4.5, '$\\times 3$', fontsize=24, ha='center', va='center',
            color=ACCENT5, fontweight='bold', rotation=10,
            bbox=dict(boxstyle='round,pad=0.3', facecolor=CREAM, edgecolor=ACCENT5, linewidth=2))

    # GCD note
    ax.text(8, -0.8, '$\\gcd(3, 6, 6, 9) = 3$: scale factor extracted',
            fontsize=12, ha='center', color=DARK, fontstyle='italic',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=CREAM, edgecolor=GOLD, alpha=0.8))

    ax.text(6, 7.5, 'Stretching the Quadruple', fontsize=20, ha='center',
            color=DARK, fontweight='bold')

    save(fig, 'fig07_scaling_tetrahedra.png')


# ============================================================
# ILLUSTRATION 8: Lattice sphere with two highlighted points
# ============================================================
def fig08_lattice_sphere():
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.set_aspect('equal')
    ax.axis('off')

    # Translucent sphere (circle in 2D projection)
    theta = np.linspace(0, 2 * np.pi, 200)
    R = 1.5
    ax.fill(R * np.cos(theta), R * np.sin(theta), alpha=0.08, color=ACCENT2)
    ax.plot(R * np.cos(theta), R * np.sin(theta), color=ACCENT2, linewidth=2, alpha=0.4)

    # Lattice points (3D grid projected to 2D)
    for i in np.arange(-1.5, 2.0, 0.5):
        for j in np.arange(-1.5, 2.0, 0.5):
            dist = sqrt(i**2 + j**2)
            if dist < 1.9:
                ax.plot(i, j, '.', color=SLATE, markersize=4, alpha=0.3)

    # Origin and axes
    ax.plot(0, 0, 'o', color=DARK, markersize=5, zorder=11)
    ax.annotate('', xy=(1.8, 0), xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', color=SLATE, lw=1.5, alpha=0.5))
    ax.annotate('', xy=(0, 1.8), xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', color=SLATE, lw=1.5, alpha=0.5))
    ax.annotate('', xy=(-1.0, -1.0), xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', color=SLATE, lw=1.5, alpha=0.5))
    ax.text(1.85, -0.1, '$a$', fontsize=12, color=SLATE)
    ax.text(0.1, 1.85, '$b$', fontsize=12, color=SLATE)
    ax.text(-1.15, -1.15, '$c$', fontsize=12, color=SLATE)

    # Point 1 (red): represents (1, 4, 8) projected
    p1 = (0.3, 1.35)
    ax.plot(*p1, 'o', color=ACCENT1, markersize=14, markeredgecolor=DARK,
            markeredgewidth=2, zorder=15)
    ax.text(p1[0] + 0.15, p1[1] + 0.15, '$(1, 4, 8)$', fontsize=11, color=ACCENT1,
            fontweight='bold')

    # Dashed lines to axes from point 1
    ax.plot([p1[0], p1[0]], [0, p1[1]], '--', color=ACCENT1, linewidth=1, alpha=0.5)
    ax.plot([0, p1[0]], [p1[1], p1[1]], '--', color=ACCENT1, linewidth=1, alpha=0.5)

    # Point 2 (blue): represents (4, 4, 7) projected
    p2 = (1.0, 0.9)
    ax.plot(*p2, 'o', color=ACCENT2, markersize=14, markeredgecolor=DARK,
            markeredgewidth=2, zorder=15)
    ax.text(p2[0] + 0.15, p2[1] - 0.2, '$(4, 4, 7)$', fontsize=11, color=ACCENT2,
            fontweight='bold')

    # Dashed lines to axes from point 2
    ax.plot([p2[0], p2[0]], [0, p2[1]], '--', color=ACCENT2, linewidth=1, alpha=0.5)
    ax.plot([0, p2[0]], [p2[1], p2[1]], '--', color=ACCENT2, linewidth=1, alpha=0.5)

    # Arc between points on sphere
    angle1 = np.arctan2(p1[1], p1[0])
    angle2 = np.arctan2(p2[1], p2[0])
    arc_angles = np.linspace(angle2, angle1, 50)
    arc_r = R * 0.95
    ax.plot(arc_r * np.cos(arc_angles), arc_r * np.sin(arc_angles),
            color=GOLD, linewidth=2.5, alpha=0.8)

    # Annotation along arc
    mid_angle = (angle1 + angle2) / 2
    ax.text(1.65 * np.cos(mid_angle), 1.65 * np.sin(mid_angle),
            '$(a_1-a_2)(a_1+a_2) + \\ldots$',
            fontsize=9, ha='center', va='center', color=DARK,
            bbox=dict(boxstyle='round,pad=0.2', facecolor=CREAM, edgecolor=GOLD, alpha=0.8),
            rotation=20)

    # Sphere label
    ax.text(0, -1.8, '$a^2 + b^2 + c^2 = d^2 \\quad (d = 9)$',
            fontsize=13, ha='center', color=DARK, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=CREAM, edgecolor=ACCENT2, alpha=0.8))

    ax.set_title('The Lattice Detective', fontsize=20, color=DARK, fontweight='bold', pad=15)

    save(fig, 'fig08_lattice_sphere.png')


# ============================================================
# ILLUSTRATION 9: Gaussian integer — square vs rectangle
# ============================================================
def fig09_gaussian_plane():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
    fig.set_facecolor(SAND)
    for ax in [ax1, ax2]:
        ax.set_facecolor(SAND)

    # Left panel: Gaussian integer plane with vector and square
    ax = ax1
    ax.set_xlim(-1, 6)
    ax.set_ylim(-1, 6)
    ax.set_aspect('equal')
    ax.set_title('Gaussian Integer $2 + 3i$', fontsize=14, color=DARK, fontweight='bold')

    # Grid
    for i in range(7):
        ax.axhline(i - 0.5, color=SLATE, alpha=0.08, linewidth=0.5)
        ax.axvline(i - 0.5, color=SLATE, alpha=0.08, linewidth=0.5)
    for i in range(6):
        for j in range(6):
            ax.plot(i, j, '.', color=SLATE, markersize=3, alpha=0.3)

    # Axes
    ax.axhline(0, color=DARK, linewidth=1, alpha=0.5)
    ax.axvline(0, color=DARK, linewidth=1, alpha=0.5)
    ax.text(5.5, -0.4, 'Re', fontsize=11, color=DARK)
    ax.text(-0.5, 5.5, 'Im', fontsize=11, color=DARK)

    # Vector from origin to (2, 3)
    ax.annotate('', xy=(2, 3), xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=3))
    ax.text(0.6, 1.8, '$\\sqrt{13}$', fontsize=13, color=ACCENT1, fontweight='bold', rotation=56)

    # Point
    ax.plot(2, 3, 'o', color=ACCENT1, markersize=10, markeredgecolor=DARK,
            markeredgewidth=2, zorder=10)
    ax.text(2.3, 3.2, '$2 + 3i$', fontsize=13, color=DARK, fontweight='bold')

    # Square built on the vector (rotated square with side sqrt(13))
    # Vertices: (0,0), (2,3), (-1,5), (-3,2)  -- but let's use a simpler visual
    sq_verts = np.array([[0, 0], [2, 3], [-1, 5], [-3, 2], [0, 0]])
    ax.fill(sq_verts[:, 0], sq_verts[:, 1], alpha=0.15, color=ACCENT2)
    ax.plot(sq_verts[:, 0], sq_verts[:, 1], color=ACCENT2, linewidth=2)
    ax.text(-0.5, 2.5, 'Area $= 13$', fontsize=12, ha='center', color=ACCENT2, fontweight='bold')

    ax.axis('off')

    # Right panel: Rectangle with same area
    ax = ax2
    ax.set_xlim(-1, 16)
    ax.set_ylim(-2, 5)
    ax.set_aspect('equal')
    ax.set_title('Difference of Squares: $(d-c)(d+c)$', fontsize=14, color=DARK, fontweight='bold')

    # Rectangle 1 × 13
    rect = patches.Rectangle((1, 0.5), 13, 1, linewidth=2,
                               edgecolor=ACCENT1, facecolor=ACCENT1, alpha=0.2)
    ax.add_patch(rect)
    ax.plot([1, 14, 14, 1, 1], [0.5, 0.5, 1.5, 1.5, 0.5], color=ACCENT1, linewidth=2)

    # Dimensions
    ax.text(7.5, 1, 'Area $= 13$', fontsize=14, ha='center', va='center',
            color=ACCENT1, fontweight='bold')
    ax.text(7.5, 0, '$d + c = 13$', fontsize=13, ha='center', color=DARK, fontweight='bold')
    ax.text(0.3, 1, '$d-c$\n$= 1$', fontsize=11, ha='center', va='center', color=DARK)

    # Quadruple reference
    ax.text(7.5, 2.5, 'From quadruple $(2, 3, 6, 7)$:', fontsize=12, ha='center', color=DARK)
    ax.text(7.5, 3.3, '$(7-6)(7+6) = 1 \\times 13 = 13 = 2^2 + 3^2$',
            fontsize=13, ha='center', color=DARK, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=CREAM, edgecolor=GOLD, linewidth=1.5))

    # Equals sign between panels
    ax.text(-0.5, 1, '$=$', fontsize=30, ha='center', va='center', color=GOLD, fontweight='bold')

    ax.axis('off')

    fig.suptitle('Same Area, Different Shapes — The Gaussian Norm Meets the Difference of Squares',
                 fontsize=15, color=DARK, fontweight='bold', y=1.02)
    plt.tight_layout()
    save(fig, 'fig09_gaussian_plane.png')


# ============================================================
# ILLUSTRATION 10: Euclid's Lever (Prime Inquisitor)
# ============================================================
def fig10_euclid_lever():
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.axis('off')

    # Fulcrum (triangle)
    fulcrum_x = [7, 6.3, 7.7, 7]
    fulcrum_y = [3, 2, 2, 3]
    ax.fill(fulcrum_x, fulcrum_y, color=DARK, alpha=0.7)
    ax.text(7, 1.3, "Euclid's Lemma", fontsize=13, ha='center', color=DARK, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=CREAM, edgecolor=GOLD, linewidth=1.5))

    # Beam
    ax.plot([2, 12], [4, 4], color=DARK, linewidth=4)
    ax.plot([2, 2], [3.8, 4.2], color=DARK, linewidth=3)
    ax.plot([12, 12], [3.8, 4.2], color=DARK, linewidth=3)

    # Left weight: product
    left_box = FancyBboxPatch((1, 4.5), 4, 1.5, boxstyle="round,pad=0.2",
                               facecolor=LIGHT_BLUE, edgecolor=ACCENT2, linewidth=2)
    ax.add_patch(left_box)
    ax.text(3, 5.25, '$(d-c)(d+c)$', fontsize=14, ha='center', va='center',
            color=DARK, fontweight='bold')

    # Right weight: prime
    right_circle = plt.Circle((12, 5.5), 0.8, fill=True, facecolor=LIGHT_RED,
                               edgecolor=ACCENT1, linewidth=2.5)
    ax.add_patch(right_circle)
    ax.text(12, 5.5, '$p$', fontsize=20, ha='center', va='center',
            color=DARK, fontweight='bold')
    ax.text(12, 4.3, 'prime', fontsize=10, ha='center', color=ACCENT1, fontstyle='italic')

    # Branching arrows from prime
    # Arrow to (d-c)
    ax.annotate('', xy=(3.5, 7.8), xytext=(10, 6.3),
                arrowprops=dict(arrowstyle='->', color=ACCENT2, lw=2.5,
                                connectionstyle='arc3,rad=0.2'))
    # Arrow to (d+c)
    ax.annotate('', xy=(10.5, 7.8), xytext=(12, 6.3),
                arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=2.5,
                                connectionstyle='arc3,rad=-0.2'))

    # Two outcome boxes
    box1 = FancyBboxPatch((1.5, 7.5), 4, 1, boxstyle="round,pad=0.2",
                           facecolor=LIGHT_BLUE, edgecolor=ACCENT2, linewidth=2)
    ax.add_patch(box1)
    ax.text(3.5, 8, '$p \\mid (d - c)$', fontsize=14, ha='center', va='center',
            color=DARK, fontweight='bold')

    box2 = FancyBboxPatch((8.5, 7.5), 4, 1, boxstyle="round,pad=0.2",
                           facecolor=LIGHT_RED, edgecolor=ACCENT1, linewidth=2)
    ax.add_patch(box2)
    ax.text(10.5, 8, '$p \\mid (d + c)$', fontsize=14, ha='center', va='center',
            color=DARK, fontweight='bold')

    # "or" label
    ax.text(7, 8, 'or', fontsize=16, ha='center', va='center', color=DARK,
            fontweight='bold', fontstyle='italic')

    # Caption
    ax.text(7, 0.5, '$p \\mid (d-c)(d+c) \\;\\Longrightarrow\\; p \\mid (d-c)$ or $p \\mid (d+c)$',
            fontsize=14, ha='center', color=DARK, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=CREAM, edgecolor=GOLD, linewidth=1.5))

    ax.text(7, 9.5, 'The Prime Inquisitor', fontsize=20, ha='center',
            color=DARK, fontweight='bold')

    save(fig, 'fig10_euclid_lever.png')


# ============================================================
# ILLUSTRATION 11: Mod 4 residue grid
# ============================================================
def fig11_mod4_grid():
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.set_xlim(-0.5, 8.5)
    ax.set_ylim(-1, 9)
    ax.set_aspect('equal')
    ax.axis('off')

    # a² mod 4 ∈ {0, 1}, b² mod 4 ∈ {0, 1}, c² mod 4 ∈ {0, 1}
    # sum must be ≡ 0 or 1 (mod 4)
    sq_residues = [0, 1]
    cell_size = 1.8
    gap = 0.15

    x_start = 1
    y_start = 7

    # Header labels
    ax.text(4.5, 8.5, 'Modular Filter: $a^2 + b^2 + c^2 \equiv ?$ (mod 4)',
            fontsize=16, ha='center', color=DARK, fontweight='bold')

    ax.text(x_start + 2 * cell_size, y_start + 0.8,
            '$b^2$ mod 4', fontsize=13, ha='center', color=ACCENT2, fontweight='bold')
    ax.text(x_start - 1.2, y_start - 1.5 * cell_size,
            '$a^2$ mod 4', fontsize=13, ha='center', color=ACCENT1, fontweight='bold',
            rotation=90)

    # Column headers
    for j, b2 in enumerate(sq_residues):
        for k, c2 in enumerate(sq_residues):
            col = j * 2 + k
            x = x_start + col * cell_size + cell_size / 2
            ax.text(x, y_start + 0.3, f'$b^2\\!={b2}$\n$c^2\\!={c2}$',
                    fontsize=9, ha='center', va='bottom', color=DARK)

    for i, a2 in enumerate(sq_residues):
        # Row header
        y = y_start - i * cell_size - cell_size / 2
        ax.text(x_start - 0.3, y, f'$a^2={a2}$', fontsize=11, ha='right', va='center',
                color=DARK, fontweight='bold')

        for j, b2 in enumerate(sq_residues):
            for k, c2 in enumerate(sq_residues):
                col = j * 2 + k
                x = x_start + col * cell_size
                yc = y_start - i * cell_size - cell_size

                total = (a2 + b2 + c2) % 4
                valid = total in [0, 1]

                color = ACCENT3 if valid else ACCENT1
                alpha = 0.3 if valid else 0.25
                label_color = ACCENT3 if valid else ACCENT1

                rect = patches.FancyBboxPatch((x + gap, yc + gap),
                                               cell_size - 2 * gap, cell_size - 2 * gap,
                                               boxstyle="round,pad=0.05",
                                               facecolor=color, edgecolor=DARK,
                                               linewidth=1.5, alpha=alpha)
                ax.add_patch(rect)

                # Sum value
                ax.text(x + cell_size / 2, yc + cell_size / 2 + 0.15,
                        f'$\\sum \\equiv {total}$',
                        fontsize=12, ha='center', va='center', color=DARK, fontweight='bold')

                # Valid/forbidden label
                status = 'OK' if valid else 'X'
                ax.text(x + cell_size / 2, yc + cell_size / 2 - 0.35,
                        status, fontsize=16, ha='center', va='center',
                        color=label_color, fontweight='bold')

    # Legend
    legend_y = y_start - 3 * cell_size
    valid_patch = patches.FancyBboxPatch((1, legend_y), 0.6, 0.5, boxstyle="round,pad=0.05",
                                          facecolor=ACCENT3, alpha=0.3, edgecolor=DARK)
    ax.add_patch(valid_patch)
    ax.text(2, legend_y + 0.25, 'Valid: sum $\equiv 0$ or $1$ (mod 4)',
            fontsize=11, va='center', color=DARK)

    forbid_patch = patches.FancyBboxPatch((1, legend_y - 0.8), 0.6, 0.5, boxstyle="round,pad=0.05",
                                           facecolor=ACCENT1, alpha=0.25, edgecolor=DARK)
    ax.add_patch(forbid_patch)
    ax.text(2, legend_y - 0.55, 'Forbidden: sum $\equiv 2$ or $3$ (mod 4)',
            fontsize=11, va='center', color=DARK)

    # Example annotation
    ax.text(4.5, legend_y - 1.8,
            'Example: $7^2+7^2+7^2 \equiv 1+1+1 = 3$ (mod 4) — forbidden!',
            fontsize=12, ha='center', color=ACCENT1, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=CREAM, edgecolor=ACCENT1, linewidth=1.5))

    save(fig, 'fig11_mod4_grid.png')


# ============================================================
# ILLUSTRATION 12: Workbench scene
# ============================================================
def fig12_workbench():
    fig, ax = plt.subplots(1, 1, figsize=(14, 9))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Desk surface
    desk = patches.FancyBboxPatch((0.5, 0.5), 13, 5, boxstyle="round,pad=0.2",
                                   facecolor='#C4A882', edgecolor=DARK, linewidth=3)
    ax.add_patch(desk)

    # Chalkboard in background
    chalk = patches.FancyBboxPatch((1, 6), 12, 3.5, boxstyle="round,pad=0.2",
                                    facecolor='#2C5F2D', edgecolor=DARK, linewidth=3)
    ax.add_patch(chalk)

    # Chalkboard content — parametric machine formulas
    chalk_text = [
        '$a = m^2 + n^2 - p^2 - q^2$',
        '$b = 2(mq + np)$',
        '$c = 2(nq - mp)$',
        '$d = m^2 + n^2 + p^2 + q^2$',
    ]
    for i, t in enumerate(chalk_text):
        ax.text(7, 9 - i * 0.7, t, fontsize=11, ha='center', color='white',
                fontfamily='serif')

    # Paper 1: quadruples list
    paper1 = patches.FancyBboxPatch((1.5, 1), 3.5, 4, boxstyle="round,pad=0.1",
                                     facecolor='white', edgecolor=SLATE, linewidth=1,
                                     alpha=0.9)
    ax.add_patch(paper1)
    quads_text = [
        '$(1, 2, 2, 3)$  OK',
        '$(2, 3, 6, 7)$  OK',
        '$(1, 4, 8, 9)$  OK',
        '$(4, 4, 7, 9)$  OK',
    ]
    for i, t in enumerate(quads_text):
        ax.text(3.2, 4.3 - i * 0.7, t, fontsize=10, ha='center', color=DARK,
                fontfamily='serif')

    # Paper 2: collision identity
    paper2 = patches.FancyBboxPatch((5.5, 1.5), 4, 2.5, boxstyle="round,pad=0.1",
                                     facecolor='#FFFEF5', edgecolor=SLATE, linewidth=1,
                                     alpha=0.9)
    ax.add_patch(paper2)
    ax.text(7.5, 3.3, 'Collision Check:', fontsize=10, ha='center', color=DARK,
            fontweight='bold', fontfamily='serif')
    ax.text(7.5, 2.7, '$(8-7)(8+7) = 15$', fontsize=10, ha='center', color=DARK,
            fontfamily='serif')
    ax.text(7.5, 2.1, '$\\gcd(15, 81) = 3$  OK', fontsize=11, ha='center', color=ACCENT3,
            fontweight='bold', fontfamily='serif')

    # Magnifying glass
    mg = plt.Circle((5.3, 3.8), 0.5, fill=False, edgecolor=DARK, linewidth=2.5, zorder=15)
    ax.add_patch(mg)
    ax.plot([5.65, 6.1], [3.45, 3.0], color=DARK, linewidth=3, zorder=15)

    # Calculator display
    calc = FancyBboxPatch((10, 1.5), 3, 3.5, boxstyle="round,pad=0.2",
                           facecolor='#3D3D3D', edgecolor=DARK, linewidth=2)
    ax.add_patch(calc)
    calc_screen = patches.FancyBboxPatch((10.3, 3.8), 2.4, 0.8, boxstyle="round,pad=0.1",
                                          facecolor='#C8E6C9', edgecolor=DARK, linewidth=1)
    ax.add_patch(calc_screen)
    ax.text(11.5, 4.2, 'GCD = 3', fontsize=12, ha='center', va='center',
            color=DARK, fontweight='bold', fontfamily='monospace')

    # Calculator buttons (decorative grid)
    for r in range(3):
        for c in range(3):
            btn = patches.FancyBboxPatch((10.5 + c * 0.8, 1.8 + r * 0.6), 0.6, 0.4,
                                          boxstyle="round,pad=0.05",
                                          facecolor='#555', edgecolor=DARK, linewidth=0.8)
            ax.add_patch(btn)

    # Coffee cup (simple)
    cup_x = [0.8, 1.5]
    cup_y = [1.2, 1.2]
    ax.plot(cup_x, cup_y, color=DARK, linewidth=2)
    cup = patches.FancyBboxPatch((0.7, 0.7), 0.9, 0.5, boxstyle="round,pad=0.05",
                                  facecolor='#8B4513', edgecolor=DARK, linewidth=1.5)
    ax.add_patch(cup)
    # Steam
    for dx in [0.9, 1.1, 1.3]:
        steam_y = np.linspace(1.25, 1.8, 30)
        steam_x = dx + 0.05 * np.sin(steam_y * 15)
        ax.plot(steam_x, steam_y, color=SLATE, linewidth=1, alpha=0.4)

    # Title
    ax.text(7, 9.8, "The Number Cruncher's Workbench", fontsize=20, ha='center',
            color=DARK, fontweight='bold')

    save(fig, 'fig12_workbench.png')


# ============================================================
# ILLUSTRATION 13: Histogram of primitive quadruples by d
# ============================================================
def fig13_histogram():
    fig, ax = plt.subplots(1, 1, figsize=(14, 7))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    # Count primitive quadruples for each d from 1 to 50
    quads = find_primitive_quadruples(50)
    counts = {}
    for a, b, c, d in quads:
        counts[d] = counts.get(d, 0) + 1

    def is_prime(n):
        if n < 2:
            return False
        for i in range(2, int(sqrt(n)) + 1):
            if n % i == 0:
                return False
        return True

    d_vals = list(range(1, 51))
    bar_counts = [counts.get(d, 0) for d in d_vals]
    bar_colors = [ACCENT2 if is_prime(d) else ACCENT1 for d in d_vals]

    bars = ax.bar(d_vals, bar_counts, color=bar_colors, edgecolor=DARK, linewidth=0.5, alpha=0.7)

    ax.set_xlabel('$d$ (hypotenuse)', fontsize=14, color=DARK, fontweight='bold')
    ax.set_ylabel('Number of primitive quadruples', fontsize=14, color=DARK, fontweight='bold')
    ax.set_title('Primitive Pythagorean Quadruples by Hypotenuse',
                 fontsize=18, color=DARK, fontweight='bold', pad=15)

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=ACCENT2, edgecolor=DARK, alpha=0.7, label='$d$ prime'),
        Patch(facecolor=ACCENT1, edgecolor=DARK, alpha=0.7, label='$d$ composite'),
    ]
    ax.legend(handles=legend_elements, fontsize=12, loc='upper left',
              framealpha=0.9, facecolor=CREAM, edgecolor=GOLD)

    # Style
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(DARK)
    ax.spines['bottom'].set_color(DARK)
    ax.tick_params(colors=DARK)
    ax.set_xticks(range(0, 51, 5))

    # Caption
    ax.text(25, max(bar_counts) * 0.9,
            'More representations → more collisions → more factors',
            fontsize=13, ha='center', color=DARK, fontstyle='italic',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=CREAM, edgecolor=GOLD, alpha=0.8))

    plt.tight_layout()
    save(fig, 'fig13_histogram.png')


# ============================================================
# Main
# ============================================================
if __name__ == '__main__':
    print("Generating Chapter 12 illustrations...")
    fig01_quadruple_table()
    fig02_triangle_to_sphere()
    fig03_bridge()
    fig04_quadruple_machine()
    fig05_hypotenuse_decomposition()
    fig06_collision_roads()
    fig07_scaling_tetrahedra()
    fig08_lattice_sphere()
    fig09_gaussian_plane()
    fig10_euclid_lever()
    fig11_mod4_grid()
    fig12_workbench()
    fig13_histogram()
    print("Done! All Chapter 12 illustrations generated.")

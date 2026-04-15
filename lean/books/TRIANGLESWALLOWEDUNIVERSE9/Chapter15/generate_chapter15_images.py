#!/usr/bin/env python3
"""Generate all illustrations for Chapter 15: The Algebra Where Two Plus Three Equals Two."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe
import numpy as np
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
os.makedirs(OUT, exist_ok=True)

# Color palette (matching Chapter 1/2 style)
SAND = '#F5E6C8'
DARK = '#2C1810'
ACCENT1 = '#C0392B'  # red
ACCENT2 = '#2980B9'  # blue
ACCENT3 = '#27AE60'  # green
ACCENT4 = '#8E44AD'  # purple
ACCENT5 = '#E67E22'  # orange / tropical
GOLD = '#D4A017'
LIGHT_BLUE = '#AED6F1'
LIGHT_GREEN = '#ABEBC6'
LIGHT_RED = '#F5B7B1'
CREAM = '#FDF2E9'
SLATE = '#34495E'
GLOW = '#F4D03F'
TROPICAL = '#E67E22'  # the signature tropical orange


def save(fig, name, dpi=200):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=dpi, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  Saved {name}")


# ============================================================
# ILLUSTRATION 1: The tropical calculator keypad
# ============================================================
def fig01_tropical_calculator():
    fig, ax = plt.subplots(1, 1, figsize=(12, 9))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    # Draw calculator body
    calc_body = FancyBboxPatch((0.5, 0.5), 5, 7.5, boxstyle="round,pad=0.3",
                                facecolor='#3B3B3B', edgecolor=DARK, linewidth=3)
    ax.add_patch(calc_body)

    # Display screen
    screen = FancyBboxPatch((1.0, 6.5), 4, 1.0, boxstyle="round,pad=0.1",
                             facecolor='#C8E6C9', edgecolor=DARK, linewidth=2)
    ax.add_patch(screen)
    ax.text(3.0, 7.0, '? = min(a, b)', fontsize=14, ha='center', va='center',
            fontfamily='monospace', color=DARK, fontweight='bold')

    # Number keys (3x3 grid: 7-8-9, 4-5-6, 1-2-3, then 0)
    key_labels = [
        ['7', '8', '9'],
        ['4', '5', '6'],
        ['1', '2', '3'],
        ['0', '·', '='],
    ]
    for row_i, row in enumerate(key_labels):
        for col_i, label in enumerate(row):
            kx = 1.2 + col_i * 1.3
            ky = 5.5 - row_i * 1.2
            color = CREAM
            if label == '=':
                color = LIGHT_BLUE
            key = FancyBboxPatch((kx, ky), 1.0, 0.9, boxstyle="round,pad=0.08",
                                  facecolor=color, edgecolor=DARK, linewidth=1.5)
            ax.add_patch(key)
            ax.text(kx + 0.5, ky + 0.45, label, fontsize=16, ha='center', va='center',
                    color=DARK, fontweight='bold')

    # Operation keys on the right side
    ops = [
        ('+', 'min', TROPICAL),
        ('×', '+', TROPICAL),
    ]
    for i, (orig, trop, col) in enumerate(ops):
        kx = 4.7
        ky = 5.5 - i * 1.2
        key = FancyBboxPatch((kx, ky), 1.0, 0.9, boxstyle="round,pad=0.08",
                              facecolor=col, edgecolor=DARK, linewidth=2)
        ax.add_patch(key)
        # Show crossed-out original and tropical replacement
        ax.text(kx + 0.5, ky + 0.62, orig, fontsize=14, ha='center', va='center',
                color='white', fontweight='bold', alpha=0.4)
        ax.plot([kx + 0.25, kx + 0.75], [ky + 0.60, ky + 0.65], color='white', lw=2, alpha=0.6)
        ax.text(kx + 0.5, ky + 0.28, trop, fontsize=13, ha='center', va='center',
                color='white', fontweight='bold')

    # Question mark cloud from = key
    eq_x, eq_y = 3.8 + 0.5, 2.3 + 0.45
    cloud_x, cloud_y = eq_x + 0.8, eq_y - 0.5
    ax.text(cloud_x, cloud_y, '?', fontsize=28, ha='center', va='center',
            color=ACCENT4, fontweight='bold', fontstyle='italic',
            path_effects=[pe.withStroke(linewidth=4, foreground='white')])

    # Example computations table on the right
    table_x = 7.0
    table_y_start = 7.5
    examples = [
        ('5 ⊕ 3', '= 3'),
        ('5 ⊙ 3', '= 8'),
        ('2 ⊕ 2', '= 2'),
        ('2 ⊙ 2', '= 4'),
    ]
    # Table header
    ax.text(table_x + 1.2, table_y_start + 0.3, 'Tropical Arithmetic',
            fontsize=16, ha='center', va='center', color=DARK, fontweight='bold')

    # Table background
    tbl = FancyBboxPatch((table_x - 0.3, table_y_start - 4.2), 3.0, 4.3,
                          boxstyle="round,pad=0.15", facecolor=CREAM,
                          edgecolor=DARK, linewidth=2)
    ax.add_patch(tbl)

    for i, (expr, result) in enumerate(examples):
        y = table_y_start - 0.5 - i * 0.95
        ax.text(table_x, y, expr, fontsize=18, ha='left', va='center',
                color=DARK, fontfamily='monospace')
        ax.text(table_x + 2.0, y, result, fontsize=18, ha='left', va='center',
                color=TROPICAL, fontweight='bold', fontfamily='monospace')

    # Annotation
    ax.text(table_x + 1.2, table_y_start - 4.6,
            '⊕ = min     ⊙ = +',
            fontsize=13, ha='center', va='center', color=SLATE, fontstyle='italic')

    ax.set_xlim(-0.5, 11)
    ax.set_ylim(-0.5, 9)
    ax.set_aspect('equal')
    ax.axis('off')

    ax.text(5.5, -0.2, 'The broken calculator: "+" means min, "×" means +.',
            fontsize=12, ha='center', va='center', color=SLATE, fontstyle='italic')

    save(fig, 'fig01_tropical_calculator.png')


# ============================================================
# ILLUSTRATION 2: Number-line shift — distributive law
# ============================================================
def fig02_distributive_shift():
    fig, axes = plt.subplots(2, 1, figsize=(14, 6), gridspec_kw={'height_ratios': [1, 1]})
    fig.set_facecolor(SAND)

    for ax in axes:
        ax.set_facecolor(SAND)
        ax.set_xlim(-1, 16)
        ax.set_ylim(-0.8, 1.5)
        ax.set_aspect('equal')
        ax.axis('off')

    # TOP: Original number line with b=7, c=2
    ax = axes[0]
    ax.annotate('', xy=(15, 0), xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', color=DARK, lw=2))
    for tick in range(16):
        ax.plot([tick, tick], [-0.1, 0.1], color=DARK, lw=1)
        if tick % 2 == 0:
            ax.text(tick, -0.35, str(tick), fontsize=9, ha='center', color=DARK)

    # Mark b=7 and c=2
    ax.plot(7, 0, 'o', color=ACCENT1, markersize=14, markeredgecolor=DARK, markeredgewidth=2, zorder=10)
    ax.text(7, 0.55, '$b = 7$', fontsize=14, ha='center', color=ACCENT1, fontweight='bold')
    ax.plot(2, 0, 'o', color=ACCENT2, markersize=14, markeredgecolor=DARK, markeredgewidth=2, zorder=10)
    ax.text(2, 0.55, '$c = 2$', fontsize=14, ha='center', color=ACCENT2, fontweight='bold')

    # Arc from both to the minimum
    arc_style = dict(arrowstyle='->', color=TROPICAL, lw=2.5, connectionstyle='arc3,rad=-0.4')
    ax.annotate('', xy=(2, -0.15), xytext=(7, -0.15), arrowprops=arc_style)
    ax.text(4.5, -0.7, '$\\oplus = \\min$', fontsize=13, ha='center', color=TROPICAL, fontweight='bold')

    # Winner indicator
    ax.plot(2, 0, 'o', color=TROPICAL, markersize=20, markeredgecolor=TROPICAL,
            markeredgewidth=2, alpha=0.3, zorder=5)

    ax.text(0, 1.2, 'Before shift:', fontsize=13, ha='left', color=DARK, fontweight='bold')

    # BOTTOM: Shifted line by a=4
    ax = axes[1]
    ax.annotate('', xy=(15, 0), xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', color=DARK, lw=2))
    for tick in range(16):
        ax.plot([tick, tick], [-0.1, 0.1], color=DARK, lw=1)
        if tick % 2 == 0:
            ax.text(tick, -0.35, str(tick), fontsize=9, ha='center', color=DARK)

    # Orange shading for the shift
    shift_rect = patches.Rectangle((0, -0.05), 15, 0.1, alpha=0.08, color=TROPICAL)
    ax.add_patch(shift_rect)

    # Mark a+b=11 and a+c=6
    ax.plot(11, 0, 'o', color=ACCENT1, markersize=14, markeredgecolor=DARK, markeredgewidth=2, zorder=10)
    ax.text(11, 0.55, '$a+b = 11$', fontsize=14, ha='center', color=ACCENT1, fontweight='bold')
    ax.plot(6, 0, 'o', color=ACCENT2, markersize=14, markeredgecolor=DARK, markeredgewidth=2, zorder=10)
    ax.text(6, 0.55, '$a+c = 6$', fontsize=14, ha='center', color=ACCENT2, fontweight='bold')

    # Arc to minimum
    arc_style2 = dict(arrowstyle='->', color=TROPICAL, lw=2.5, connectionstyle='arc3,rad=-0.4')
    ax.annotate('', xy=(6, -0.15), xytext=(11, -0.15), arrowprops=arc_style2)
    ax.text(8.5, -0.7, '$\\oplus = \\min = 6$', fontsize=13, ha='center', color=TROPICAL, fontweight='bold')

    ax.plot(6, 0, 'o', color=TROPICAL, markersize=20, markeredgecolor=TROPICAL,
            markeredgewidth=2, alpha=0.3, zorder=5)

    ax.text(0, 1.2, 'After shift by $a = 4$:', fontsize=13, ha='left', color=DARK, fontweight='bold')

    # Overall caption
    fig.text(0.5, -0.02, 'Shifting preserves the winner: $a + \\min(b,c) = \\min(a+b, a+c)$.',
             fontsize=12, ha='center', color=SLATE, fontstyle='italic')

    plt.tight_layout()
    save(fig, 'fig02_distributive_shift.png')


# ============================================================
# ILLUSTRATION 3: Totem pole of integers with ∞ at top
# ============================================================
def fig03_totem_pole():
    fig, ax = plt.subplots(1, 1, figsize=(8, 12))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    integers = list(range(-3, 6))  # -3 to +5
    pole_x = 4
    y_base = 1
    y_spacing = 1.0

    # Draw the pole (vertical line)
    ax.plot([pole_x, pole_x], [y_base - 0.5, y_base + len(integers) * y_spacing + 2.5],
            color=DARK, lw=3, zorder=1)

    # Draw integer markers
    for i, val in enumerate(integers):
        y = y_base + i * y_spacing
        # Notch
        ax.plot([pole_x - 0.3, pole_x + 0.3], [y, y], color=DARK, lw=2, zorder=2)
        # Circle node
        circle = plt.Circle((pole_x, y), 0.35, facecolor=CREAM, edgecolor=DARK, linewidth=2, zorder=5)
        ax.add_patch(circle)
        ax.text(pole_x, y, str(val), fontsize=14, ha='center', va='center',
                color=DARK, fontweight='bold', zorder=6)

    # Infinity cloud at top
    inf_y = y_base + len(integers) * y_spacing + 1.5
    # Cloud shape
    from matplotlib.patches import Ellipse
    cloud_main = Ellipse((pole_x, inf_y), 2.5, 1.2, facecolor='white',
                          edgecolor=TROPICAL, linewidth=3, zorder=5)
    ax.add_patch(cloud_main)
    cloud_l = Ellipse((pole_x - 0.7, inf_y - 0.2), 1.2, 0.8, facecolor='white',
                       edgecolor='white', linewidth=0, zorder=4)
    ax.add_patch(cloud_l)
    cloud_r = Ellipse((pole_x + 0.7, inf_y - 0.2), 1.2, 0.8, facecolor='white',
                       edgecolor='white', linewidth=0, zorder=4)
    ax.add_patch(cloud_r)

    ax.text(pole_x, inf_y, '∞', fontsize=28, ha='center', va='center',
            color=TROPICAL, fontweight='bold', zorder=6)
    ax.text(pole_x, inf_y - 0.85, '= tropical zero', fontsize=11, ha='center',
            color=TROPICAL, fontstyle='italic', zorder=6)

    # Arrows showing a ⊕ ∞ = a for a couple of values
    demo_vals = [2, -1, 5]
    for val in demo_vals:
        idx = integers.index(val)
        y = y_base + idx * y_spacing
        # Arrow from integer to cloud
        ax.annotate('', xy=(pole_x + 1.4, inf_y - 0.3),
                    xytext=(pole_x + 0.45, y),
                    arrowprops=dict(arrowstyle='->', color=ACCENT2, lw=1.5,
                                    connectionstyle='arc3,rad=0.3'))
        # Arrow back
        ax.annotate('', xy=(pole_x - 0.45, y),
                    xytext=(pole_x - 1.4, inf_y - 0.3),
                    arrowprops=dict(arrowstyle='->', color=ACCENT3, lw=1.5,
                                    connectionstyle='arc3,rad=0.3'))

    # Labels on the right
    ax.text(pole_x + 2.8, inf_y - 0.5, '$a \\oplus \\infty = a$',
            fontsize=16, ha='left', va='center', color=DARK, fontweight='bold')
    ax.text(pole_x + 2.8, inf_y - 1.2, '$\\min(a, \\infty) = a$',
            fontsize=14, ha='left', va='center', color=SLATE)

    # Arrow labels
    ax.text(pole_x + 2.0, 6, '⊕', fontsize=18, ha='center', va='center',
            color=ACCENT2, fontweight='bold')
    ax.text(pole_x - 2.0, 6, '= a', fontsize=14, ha='center', va='center',
            color=ACCENT3, fontweight='bold')

    ax.set_xlim(0, 10)
    ax.set_ylim(-0.5, 14)
    ax.set_aspect('equal')
    ax.axis('off')

    ax.text(5, -0.2, 'The king of all numbers does nothing when added.',
            fontsize=12, ha='center', color=SLATE, fontstyle='italic')

    save(fig, 'fig03_totem_pole.png')


# ============================================================
# ILLUSTRATION 4: Newton polygon of a tropical polynomial
# ============================================================
def fig04_newton_polygon():
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    # Points: (exponent, coefficient) for 2 + 7x + 3x^2
    points = [(0, 2), (1, 7), (2, 3)]

    # Axes
    ax.annotate('', xy=(3.5, 0), xytext=(-0.5, 0),
                arrowprops=dict(arrowstyle='->', color=DARK, lw=2))
    ax.annotate('', xy=(0, 9), xytext=(0, -0.5),
                arrowprops=dict(arrowstyle='->', color=DARK, lw=2))

    ax.text(3.5, -0.6, 'exponent $i$', fontsize=14, ha='center', color=DARK)
    ax.text(-0.6, 9, 'valuation $a_i$', fontsize=14, ha='center', color=DARK, rotation=90)

    # Grid
    for x in range(4):
        ax.plot([x, x], [0, 8.5], color=DARK, lw=0.3, alpha=0.3)
    for y in range(9):
        ax.plot([0, 3.2], [y, y], color=DARK, lw=0.3, alpha=0.3)

    # Plot points
    colors = [ACCENT2, ACCENT1, ACCENT3]
    labels = ['$a_0 = 2$', '$a_1 = 7$', '$a_2 = 3$']
    for (x, y), col, lbl in zip(points, colors, labels):
        ax.plot(x, y, 'o', color=col, markersize=16, markeredgecolor=DARK,
                markeredgewidth=2, zorder=10)
        offset_y = 0.6 if y != 7 else 0.6
        offset_x = 0.3
        ax.text(x + offset_x, y + offset_y, lbl, fontsize=13, ha='left',
                color=col, fontweight='bold')

    # Lower convex hull: (0,2) -> (2,3), skipping (1,7) which is above
    hull_x = [0, 2]
    hull_y = [2, 3]
    ax.plot(hull_x, hull_y, color=TROPICAL, lw=3, zorder=5, linestyle='-')

    # Extend hull lines to edges for visibility
    ax.plot([-0.3, 0], [2 - 0.3 * 0.5, 2], color=TROPICAL, lw=2, linestyle='--', alpha=0.5)
    ax.plot([2, 3.2], [3, 3 + 0.5 * 1.2], color=TROPICAL, lw=2, linestyle='--', alpha=0.5)

    # Shade below hull
    hull_fill_x = [0, 2, 2, 0]
    hull_fill_y = [2, 3, 0, 0]
    ax.fill(hull_fill_x, hull_fill_y, color=TROPICAL, alpha=0.08)

    # Slope label
    mid_x, mid_y = 1, 2.5
    ax.text(mid_x + 0.3, mid_y - 0.5, 'slope = $\\frac{1}{2}$', fontsize=13,
            ha='left', color=TROPICAL, fontweight='bold', rotation=27)

    # Dashed line from (1,7) down to hull
    hull_at_1 = 2 + 0.5 * 1  # y on hull at x=1
    ax.plot([1, 1], [hull_at_1, 7], color=ACCENT1, lw=1.5, linestyle=':', zorder=3)
    ax.text(1.15, 4.5, 'above hull', fontsize=10, color=ACCENT1, fontstyle='italic')

    # Title-like caption
    ax.text(1.5, 8.5, 'Newton Polygon of $2 \\oplus 7x \\oplus 3x^{\\odot 2}$',
            fontsize=15, ha='center', color=DARK, fontweight='bold')

    ax.set_xlim(-1, 4.5)
    ax.set_ylim(-1, 9.5)
    ax.set_aspect('equal')
    ax.axis('off')

    ax.text(1.5, -0.8, 'Roots live at the slope-breaks of the lower convex hull.',
            fontsize=12, ha='center', color=SLATE, fontstyle='italic')

    save(fig, 'fig04_newton_polygon.png')


# ============================================================
# ILLUSTRATION 5: Classical vs tropical convex hulls
# ============================================================
def fig05_convex_hulls():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
    fig.set_facecolor(SAND)

    # Three points
    pts = np.array([[1, 5], [5, 2], [3, 7]])

    for ax, title in [(ax1, 'Classical Convex Hull'), (ax2, 'Tropical Convex Hull')]:
        ax.set_facecolor(SAND)
        ax.set_xlim(-0.5, 8)
        ax.set_ylim(-0.5, 9)
        ax.set_aspect('equal')
        ax.set_title(title, fontsize=16, color=DARK, fontweight='bold', pad=10)

        # Grid
        for x in range(9):
            ax.plot([x, x], [-0.5, 9], color=DARK, lw=0.2, alpha=0.2)
            ax.plot([-0.5, 8], [x, x], color=DARK, lw=0.2, alpha=0.2)

        # Plot points
        labels = ['A', 'B', 'C']
        colors = [ACCENT1, ACCENT2, ACCENT3]
        for i, (pt, lbl, col) in enumerate(zip(pts, labels, colors)):
            ax.plot(pt[0], pt[1], 'o', color=col, markersize=14,
                    markeredgecolor=DARK, markeredgewidth=2, zorder=10)
            ax.text(pt[0] + 0.3, pt[1] + 0.3, f'${lbl}$', fontsize=14,
                    color=col, fontweight='bold')

    # Classical: filled triangle
    tri = plt.Polygon(pts, facecolor=ACCENT2, alpha=0.15, edgecolor=DARK, linewidth=2)
    ax1.add_patch(tri)

    # Tropical: staircase / L-shaped region from componentwise minima
    # The tropical convex hull of points is the set of all componentwise minima
    # For visualization: draw L-shapes from pairs and the overall staircase
    # Tropical hull = all points (min(x_i), min(y_i)) reachable by tropical combinations

    # Draw L-shaped paths between pairs
    pairs = [(0, 1), (1, 2), (0, 2)]
    pair_colors = [ACCENT4, TROPICAL, ACCENT3]
    for (i, j), col in zip(pairs, pair_colors):
        p1, p2 = pts[i], pts[j]
        # L-shape: go to (min_x, max_y_of_pair) then to (max_x, min_y_of_pair)
        # Actually tropical segment = {min(λ⊙a, μ⊙b) : λ⊕μ = 0} which forms L-shape
        min_x, min_y = min(p1[0], p2[0]), min(p1[1], p2[1])
        # The L-shape connects through the corner point
        corner = (min_x, min_y)
        # Draw two segments forming the L
        ax2.plot([p1[0], p1[0], p2[0]], [p1[1], min_y, min_y],
                 color=col, lw=2, alpha=0.5, linestyle='--')
        ax2.plot([p2[0], p2[0]], [p2[1], min_y],
                 color=col, lw=2, alpha=0.5, linestyle='--')

    # Shade the tropical hull region (staircase)
    # For 3 points, the tropical convex hull includes all L-connections
    # Simplified: shade the staircase region
    stair_x = [1, 1, 3, 3, 5, 5, 1]
    stair_y = [5, 2, 2, 2, 2, 7, 7]

    # More accurate: the tropical convex hull boundary
    # is the union of tropical segments
    # Let me draw a nice staircase polygon
    trop_x = [1, 1, 5, 5, 3, 3, 1]
    trop_y = [7, 2, 2, 2, 7, 7, 7]
    ax2.fill(trop_x, trop_y, color=TROPICAL, alpha=0.12)
    ax2.plot(trop_x, trop_y, color=TROPICAL, lw=2.5)

    # Mark the "corner" points where min switches
    ax2.plot(1, 2, 's', color=TROPICAL, markersize=10, markeredgecolor=DARK,
             markeredgewidth=1.5, zorder=10)
    ax2.text(0.3, 1.5, 'min corner', fontsize=10, color=TROPICAL, fontstyle='italic')

    fig.text(0.5, 0.02, 'Classical versus tropical convexity: smooth triangles become staircase polygons.',
             fontsize=12, ha='center', color=SLATE, fontstyle='italic')

    plt.tight_layout()
    save(fig, 'fig05_convex_hulls.png')


# ============================================================
# ILLUSTRATION 6: Road-map triangle inequality
# ============================================================
def fig06_triangle_inequality():
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    # Three cities as points
    cities = {'x': (1, 2), 'y': (6, 6), 'z': (11, 2)}

    # Draw roads (edges)
    # Direct: x -> z, length 5
    ax.annotate('', xy=(10.3, 2), xytext=(1.7, 2),
                arrowprops=dict(arrowstyle='->', color=ACCENT2, lw=3))
    ax.text(6, 1.2, '$d(x, z) = 5$', fontsize=16, ha='center', color=ACCENT2, fontweight='bold')

    # Detour: x -> y, length 3
    ax.annotate('', xy=(5.5, 5.7), xytext=(1.5, 2.5),
                arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=3,
                                connectionstyle='arc3,rad=0.0'))
    ax.text(2.5, 4.8, '$d(x, y) = 3$', fontsize=14, ha='center', color=ACCENT1, fontweight='bold')

    # Detour: y -> z, length 4
    ax.annotate('', xy=(10.5, 2.5), xytext=(6.5, 5.7),
                arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=3,
                                connectionstyle='arc3,rad=0.0'))
    ax.text(9.5, 4.8, '$d(y, z) = 4$', fontsize=14, ha='center', color=ACCENT1, fontweight='bold')

    # Draw city nodes
    for name, (cx, cy) in cities.items():
        circle = plt.Circle((cx, cy), 0.5, facecolor=CREAM, edgecolor=DARK,
                             linewidth=3, zorder=10)
        ax.add_patch(circle)
        ax.text(cx, cy, f'${name}$', fontsize=18, ha='center', va='center',
                color=DARK, fontweight='bold', zorder=11)

    # Inequality display
    box = FancyBboxPatch((3.5, 7), 5, 1.2, boxstyle="round,pad=0.2",
                          facecolor=CREAM, edgecolor=TROPICAL, linewidth=2.5)
    ax.add_patch(box)
    ax.text(6, 7.6, '$5 \\leq 3 + 4 = 7 \\;\\; ✓$', fontsize=18,
            ha='center', va='center', color=DARK, fontweight='bold')

    # "≤" between paths
    ax.text(6, 4.0, '$\\leq$', fontsize=36, ha='center', va='center',
            color=TROPICAL, fontweight='bold', alpha=0.7)

    ax.set_xlim(-1, 13)
    ax.set_ylim(-0.5, 9)
    ax.set_aspect('equal')
    ax.axis('off')

    ax.text(6, -0.3, 'The shortest path never detours — the triangle inequality as a shortest-path principle.',
            fontsize=12, ha='center', color=SLATE, fontstyle='italic')

    save(fig, 'fig06_triangle_inequality.png')


# ============================================================
# ILLUSTRATION 7: Weighted graph and tropical matrix squaring
# ============================================================
def fig07_tropical_matrix():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8),
                                     gridspec_kw={'width_ratios': [1, 1.3]})
    fig.set_facecolor(SAND)

    # --- Left panel: directed graph ---
    ax = ax1
    ax.set_facecolor(SAND)

    node_pos = {'A': (1, 4), 'B': (5, 4), 'C': (5, 1), 'D': (1, 1)}
    nodes = list(node_pos.keys())

    # Edge weights (adjacency): A->B:3, A->D:7, B->C:1, B->D:2, C->A:6, D->C:4
    edges = [
        ('A', 'B', 3), ('A', 'D', 7), ('B', 'C', 1),
        ('B', 'D', 2), ('C', 'A', 6), ('D', 'C', 4),
    ]

    # Draw edges with weights
    for src, dst, w in edges:
        sx, sy = node_pos[src]
        dx, dy = node_pos[dst]
        # Offset slightly for bidirectional
        rad = 0.15
        ax.annotate('', xy=(dx, dy), xytext=(sx, sy),
                    arrowprops=dict(arrowstyle='->', color=SLATE, lw=2,
                                    connectionstyle=f'arc3,rad={rad}',
                                    shrinkA=18, shrinkB=18))
        # Label
        mx = (sx + dx) / 2
        my = (sy + dy) / 2
        # Offset label
        perp_x = -(dy - sy) * 0.12
        perp_y = (dx - sx) * 0.12
        ax.text(mx + perp_x, my + perp_y, str(w), fontsize=16, ha='center', va='center',
                color=TROPICAL, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.15', facecolor=SAND, edgecolor='none'))

    # Draw nodes
    for name, (nx, ny) in node_pos.items():
        circle = plt.Circle((nx, ny), 0.45, facecolor=CREAM, edgecolor=DARK,
                             linewidth=2.5, zorder=10)
        ax.add_patch(circle)
        ax.text(nx, ny, name, fontsize=18, ha='center', va='center',
                color=DARK, fontweight='bold', zorder=11)

    ax.set_xlim(-0.5, 6.5)
    ax.set_ylim(-0.5, 5.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Weighted Directed Graph', fontsize=14, color=DARK, fontweight='bold')

    # --- Right panel: matrices ---
    ax = ax2
    ax.set_facecolor(SAND)
    ax.axis('off')

    INF = '∞'

    # Build adjacency matrix D
    idx = {n: i for i, n in enumerate(nodes)}
    D = [[INF]*4 for _ in range(4)]
    for i in range(4):
        D[i][i] = '0'
    for src, dst, w in edges:
        D[idx[src]][idx[dst]] = str(w)

    # Build D^2 = D ⊙ D  (tropical matrix product)
    def parse(v):
        return float('inf') if v == INF else int(v)

    D_num = [[parse(D[i][j]) for j in range(4)] for i in range(4)]
    D2 = [[None]*4 for _ in range(4)]
    changed = [[False]*4 for _ in range(4)]
    for i in range(4):
        for j in range(4):
            val = min(D_num[i][k] + D_num[k][j] for k in range(4))
            D2[i][j] = INF if val == float('inf') else str(int(val))
            changed[i][j] = (D2[i][j] != D[i][j])

    # Draw matrices as text tables
    def draw_matrix(ax, mat, highlight, x0, y0, title, changed_mat=None):
        ax.text(x0 + 1.2, y0 + 0.6, title, fontsize=13, ha='center',
                color=DARK, fontweight='bold')
        headers = ['A', 'B', 'C', 'D']
        for j, h in enumerate(headers):
            ax.text(x0 + 0.6 + j * 0.6, y0 + 0.15, h, fontsize=11, ha='center',
                    color=SLATE, fontweight='bold')
        for i, h in enumerate(headers):
            ax.text(x0 - 0.15, y0 - 0.15 - i * 0.5, h, fontsize=11, ha='center',
                    va='center', color=SLATE, fontweight='bold')

        for i in range(4):
            for j in range(4):
                val = mat[i][j]
                cx = x0 + 0.6 + j * 0.6
                cy = y0 - 0.15 - i * 0.5
                is_changed = changed_mat[i][j] if changed_mat else False
                color = TROPICAL if is_changed else DARK
                weight = 'bold' if is_changed else 'normal'
                bg = LIGHT_RED if is_changed else 'none'
                ax.text(cx, cy, val, fontsize=13, ha='center', va='center',
                        color=color, fontweight=weight,
                        bbox=dict(boxstyle='round,pad=0.1', facecolor=bg,
                                  edgecolor='none', alpha=0.5 if is_changed else 0))

        # Bracket lines
        bx_l = x0 + 0.3
        bx_r = x0 + 2.7
        by_t = y0 + 0.0
        by_b = y0 - 1.8
        ax.plot([bx_l, bx_l], [by_b, by_t], color=DARK, lw=2)
        ax.plot([bx_l, bx_l + 0.1], [by_t, by_t], color=DARK, lw=2)
        ax.plot([bx_l, bx_l + 0.1], [by_b, by_b], color=DARK, lw=2)
        ax.plot([bx_r, bx_r], [by_b, by_t], color=DARK, lw=2)
        ax.plot([bx_r, bx_r - 0.1], [by_t, by_t], color=DARK, lw=2)
        ax.plot([bx_r, bx_r - 0.1], [by_b, by_b], color=DARK, lw=2)

    draw_matrix(ax, D, False, 0, 4.5, '$D$ (adjacency)')
    draw_matrix(ax, D2, True, 0, 1.8, '$D^{(2)} = D \\odot D$', changed)

    # Arrow between
    ax.annotate('', xy=(1.2, 2.5), xytext=(1.2, 3.3),
                arrowprops=dict(arrowstyle='->', color=TROPICAL, lw=3))
    ax.text(2.0, 2.9, 'tropical\nsquaring', fontsize=11, ha='left',
            color=TROPICAL, fontweight='bold')

    ax.set_xlim(-0.5, 4)
    ax.set_ylim(-0.5, 5.5)

    fig.text(0.5, 0.01, 'One tropical matrix squaring reveals all two-hop shortcuts.',
             fontsize=12, ha='center', color=SLATE, fontstyle='italic')

    plt.tight_layout()
    save(fig, 'fig07_tropical_matrix.png')


# ============================================================
# ILLUSTRATION 8: Bellman-Ford relaxation rounds
# ============================================================
def fig08_bellman_ford():
    fig = plt.figure(figsize=(14, 10))
    fig.set_facecolor(SAND)

    # Top half: graph
    ax_graph = fig.add_axes([0.05, 0.45, 0.9, 0.5])
    ax_graph.set_facecolor(SAND)

    # 5 vertices: 0(source), 1, 2, 3, 4
    pos = {0: (1, 3), 1: (4, 5), 2: (7, 3), 3: (4, 1), 4: (10, 3)}
    edges = [
        (0, 1, 2), (0, 3, 8), (1, 2, 3), (1, 3, 5),
        (2, 4, 1), (3, 2, 1), (3, 4, 4),
    ]

    # Draw edges
    for s, d, w in edges:
        sx, sy = pos[s]
        dx, dy = pos[d]
        ax_graph.annotate('', xy=(dx, dy), xytext=(sx, sy),
                          arrowprops=dict(arrowstyle='->', color=SLATE, lw=2,
                                          shrinkA=20, shrinkB=20))
        mx, my = (sx + dx) / 2, (sy + dy) / 2
        perp_x = -(dy - sy) * 0.08
        perp_y = (dx - sx) * 0.08
        ax_graph.text(mx + perp_x, my + perp_y, str(w), fontsize=15, ha='center',
                      va='center', color=TROPICAL, fontweight='bold',
                      bbox=dict(boxstyle='round,pad=0.12', facecolor=SAND, edgecolor='none'))

    # Draw nodes
    for node, (nx, ny) in pos.items():
        col = TROPICAL if node == 0 else CREAM
        ecol = TROPICAL if node == 0 else DARK
        circle = plt.Circle((nx, ny), 0.5, facecolor=col, edgecolor=ecol,
                             linewidth=2.5, zorder=10)
        ax_graph.add_patch(circle)
        txt_col = 'white' if node == 0 else DARK
        ax_graph.text(nx, ny, str(node), fontsize=18, ha='center', va='center',
                      color=txt_col, fontweight='bold', zorder=11)

    ax_graph.text(1, 5.5, 'Source', fontsize=12, ha='center', color=TROPICAL, fontweight='bold')
    ax_graph.set_xlim(-0.5, 11.5)
    ax_graph.set_ylim(-0.5, 6.5)
    ax_graph.set_aspect('equal')
    ax_graph.axis('off')

    # Bottom half: relaxation table
    ax_tbl = fig.add_axes([0.05, 0.02, 0.9, 0.38])
    ax_tbl.set_facecolor(SAND)
    ax_tbl.axis('off')

    # Simulate Bellman-Ford
    INF = float('inf')
    dist_rounds = []

    d = [INF] * 5
    d[0] = 0
    dist_rounds.append(list(d))

    # Round 1: process edges in order
    for s, dst, w in edges:
        if d[s] + w < d[dst]:
            d[dst] = d[s] + w
    dist_rounds.append(list(d))

    # Round 2
    for s, dst, w in edges:
        if d[s] + w < d[dst]:
            d[dst] = d[s] + w
    dist_rounds.append(list(d))

    # Round 3
    for s, dst, w in edges:
        if d[s] + w < d[dst]:
            d[dst] = d[s] + w
    dist_rounds.append(list(d))

    # Draw table
    col_width = 1.8
    row_height = 0.7
    x0 = 1.5
    y0 = 3.0

    # Headers
    headers = ['Round', '$d(0)$', '$d(1)$', '$d(2)$', '$d(3)$', '$d(4)$']
    for j, h in enumerate(headers):
        ax_tbl.text(x0 + j * col_width, y0, h, fontsize=13, ha='center', va='center',
                    color=DARK, fontweight='bold')

    # Separator line
    ax_tbl.plot([x0 - 0.8, x0 + 5.5 * col_width], [y0 - 0.35, y0 - 0.35],
                color=DARK, lw=1.5)

    round_labels = ['Init', '1', '2', '3']
    for r, (label, dists) in enumerate(zip(round_labels, dist_rounds)):
        y = y0 - (r + 1) * row_height
        ax_tbl.text(x0, y, label, fontsize=14, ha='center', va='center',
                    color=DARK, fontweight='bold')
        for j, val in enumerate(dists):
            prev_val = dist_rounds[r - 1][j] if r > 0 else INF
            is_changed = (r > 0 and val != prev_val) or (r == 0 and val != INF)
            disp = '∞' if val == INF else str(int(val))
            color = TROPICAL if is_changed else DARK
            weight = 'bold' if is_changed else 'normal'
            bg = LIGHT_RED if is_changed else 'none'
            ax_tbl.text(x0 + (j + 1) * col_width, y, disp,
                        fontsize=14, ha='center', va='center',
                        color=color, fontweight=weight,
                        bbox=dict(boxstyle='round,pad=0.15', facecolor=bg,
                                  edgecolor='none', alpha=0.5 if is_changed else 0))

    ax_tbl.set_xlim(0, 13)
    ax_tbl.set_ylim(-0.5, 3.5)

    fig.text(0.5, 0.0, 'Bellman–Ford: each round is a tropical matrix-vector product.',
             fontsize=12, ha='center', color=SLATE, fontstyle='italic')

    save(fig, 'fig08_bellman_ford.png')


# ============================================================
# ILLUSTRATION 9: Map of the book — network diagram
# ============================================================
def fig09_book_map():
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    # Node positions arranged in a rough flow
    positions = {
        1: (2, 10), 2: (5, 10), 3: (8, 10),
        4: (2, 7.5), 5: (5, 7.5), 6: (8, 7.5),
        7: (11, 7.5), 8: (2, 5), 9: (5, 5),
        10: (8, 5), 11: (11, 5),
        12: (2, 2.5), 13: (5, 2.5), 14: (8, 2.5),
        15: (11, 2.5), 16: (14, 2.5),
    }

    # Edges: conceptual dependencies
    all_edges = [
        (1, 2), (1, 3), (2, 3), (1, 4), (2, 5),
        (3, 6), (4, 8), (5, 9), (6, 7), (6, 10),
        (7, 11), (8, 12), (9, 13), (10, 14),
        (11, 14), (13, 14), (14, 15), (15, 16),
        (1, 14), (2, 14), (3, 14), (9, 15), (6, 15),
        (12, 13),
    ]

    # The "tropical highway"
    highway = [(1, 2), (2, 3), (3, 14), (14, 15), (15, 16)]
    highway_nodes = {1, 2, 3, 14, 15, 16}

    # Draw non-highway edges
    for s, d in all_edges:
        if (s, d) not in highway:
            sx, sy = positions[s]
            dx, dy = positions[d]
            ax.annotate('', xy=(dx, dy), xytext=(sx, sy),
                        arrowprops=dict(arrowstyle='->', color=SLATE, lw=1,
                                        alpha=0.3, shrinkA=18, shrinkB=18))

    # Draw highway edges
    for s, d in highway:
        sx, sy = positions[s]
        dx, dy = positions[d]
        ax.annotate('', xy=(dx, dy), xytext=(sx, sy),
                    arrowprops=dict(arrowstyle='->', color=TROPICAL, lw=4,
                                    shrinkA=18, shrinkB=18))

    # Draw nodes
    for ch, (nx, ny) in positions.items():
        is_highway = ch in highway_nodes
        is_ch15 = ch == 15
        if is_ch15:
            col = TROPICAL
            ecol = DARK
            r = 0.7
        elif is_highway:
            col = GLOW
            ecol = TROPICAL
            r = 0.55
        else:
            col = CREAM
            ecol = DARK
            r = 0.5

        circle = plt.Circle((nx, ny), r, facecolor=col, edgecolor=ecol,
                             linewidth=2.5 if is_highway else 1.5, zorder=10)
        ax.add_patch(circle)
        txt_col = 'white' if is_ch15 else DARK
        ax.text(nx, ny, str(ch), fontsize=16 if is_highway else 13,
                ha='center', va='center', color=txt_col,
                fontweight='bold', zorder=11)

    # Label the highway
    ax.text(4.5, 11.2, 'The Tropical Highway', fontsize=18, ha='center',
            color=TROPICAL, fontweight='bold', fontstyle='italic')

    # Arrow showing the highway path
    hw_label_positions = [(3.5, 10.6), (6.5, 10.6), (8.5, 6.2), (9.5, 2.0), (12.5, 2.0)]
    for (lx, ly) in hw_label_positions:
        ax.plot(lx, ly, 's', color=TROPICAL, markersize=4, alpha=0.5)

    # Label Ch 15 specially
    ax.text(11, 1.3, 'Ch 15: Tropical\nCrossroads', fontsize=11, ha='center',
            color=TROPICAL, fontweight='bold')

    ax.set_xlim(-0.5, 16)
    ax.set_ylim(-0.5, 12.5)
    ax.set_aspect('equal')
    ax.axis('off')

    ax.text(8, -0.2, 'The tropical semiring is the hidden algebra connecting every factoring algorithm in this book.',
            fontsize=12, ha='center', color=SLATE, fontstyle='italic')

    save(fig, 'fig09_book_map.png')


# ============================================================
# ILLUSTRATION 10: Piecewise-linear tropical polynomial
# ============================================================
def fig10_tropical_polynomial():
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    # p(x) = min(3, 1+x, 4+2x)
    x = np.linspace(-5, 5, 1000)
    f1 = np.full_like(x, 3.0)       # constant 3
    f2 = 1 + x                       # 1 + x
    f3 = 4 + 2 * x                   # 4 + 2x

    p = np.minimum(np.minimum(f1, f2), f3)

    # Find kink points (roots)
    # 3 = 1+x  =>  x = 2
    # 1+x = 4+2x  =>  x = -3
    # 3 = 4+2x  =>  x = -0.5
    # Active pieces: for x < -3: 4+2x wins; for -3 < x < 2: 1+x wins; for x > 2: 3 wins
    # But let's verify: at x=-4: f1=3, f2=-3, f3=-4 → min=-4 (f3)
    # at x=0: f1=3, f2=1, f3=4 → min=1 (f2)
    # at x=3: f1=3, f2=4, f3=10 → min=3 (f1)
    # Kinks: f3=f2 at x=-3 (both = -2), f2=f1 at x=2 (both = 3)

    # Draw individual lines (extended, faded)
    ax.plot(x, f1, '--', color=ACCENT2, lw=1.5, alpha=0.4, label='$3$ (constant)')
    ax.plot(x, f2, '--', color=TROPICAL, lw=1.5, alpha=0.4, label='$1 + x$')
    ax.plot(x, f3, '--', color=ACCENT3, lw=1.5, alpha=0.4, label='$4 + 2x$')

    # Draw the minimum (the tropical polynomial) in segments with different colors
    # Segment 1: x < -3 → f3 active
    mask1 = x <= -3
    ax.plot(x[mask1], p[mask1], color=ACCENT3, lw=4, solid_capstyle='round')

    # Segment 2: -3 < x < 2 → f2 active
    mask2 = (x >= -3) & (x <= 2)
    ax.plot(x[mask2], p[mask2], color=TROPICAL, lw=4, solid_capstyle='round')

    # Segment 3: x > 2 → f1 active
    mask3 = x >= 2
    ax.plot(x[mask3], p[mask3], color=ACCENT2, lw=4, solid_capstyle='round')

    # Mark kink points (tropical roots)
    kinks = [(-3, -2), (2, 3)]
    for kx, ky in kinks:
        ax.plot(kx, ky, 'o', color=ACCENT1, markersize=14, markeredgecolor=DARK,
                markeredgewidth=2.5, zorder=10)
        # Circle highlight
        circle = plt.Circle((kx, ky), 0.35, facecolor='none', edgecolor=ACCENT1,
                             linewidth=2, linestyle='--', zorder=9)
        ax.add_patch(circle)

    # Label kinks
    ax.text(-3, -3.2, '$x = -3$', fontsize=14, ha='center', color=ACCENT1, fontweight='bold')
    ax.text(2, 4.2, '$x = 2$', fontsize=14, ha='center', color=ACCENT1, fontweight='bold')
    ax.text(-3, -2.5, 'tropical root', fontsize=10, ha='center', color=ACCENT1, fontstyle='italic')
    ax.text(2, 3.7, 'tropical root', fontsize=10, ha='center', color=ACCENT1, fontstyle='italic')

    # Label line segments
    ax.text(-4.3, -3.5, '$4 + 2x$', fontsize=13, color=ACCENT3, fontweight='bold', rotation=55)
    ax.text(0.5, 2.8, '$1 + x$', fontsize=13, color=TROPICAL, fontweight='bold', rotation=35)
    ax.text(3.5, 3.3, '$3$', fontsize=13, color=ACCENT2, fontweight='bold')

    # Axes
    ax.axhline(0, color=DARK, lw=0.8, alpha=0.3)
    ax.axvline(0, color=DARK, lw=0.8, alpha=0.3)
    ax.set_xlabel('$x$', fontsize=16, color=DARK)
    ax.set_ylabel('$p(x) = \\min(3,\\; 1+x,\\; 4+2x)$', fontsize=14, color=DARK)

    # Grid
    ax.grid(True, alpha=0.15, color=DARK)
    ax.set_xlim(-5, 5)
    ax.set_ylim(-6, 6)

    # Legend
    ax.legend(fontsize=11, loc='upper left', framealpha=0.8, facecolor=CREAM)

    # Title
    ax.set_title('A Tropical Polynomial: Three Lines, Two Roots, Zero Curves',
                 fontsize=16, color=DARK, fontweight='bold', pad=15)

    # Spine styling
    for spine in ax.spines.values():
        spine.set_color(DARK)
        spine.set_linewidth(0.5)
    ax.tick_params(colors=DARK, labelsize=10)

    save(fig, 'fig10_tropical_polynomial.png')


# ============================================================
# Main: generate all
# ============================================================
if __name__ == '__main__':
    print("Generating Chapter 15 illustrations...")
    fig01_tropical_calculator()
    fig02_distributive_shift()
    fig03_totem_pole()
    fig04_newton_polygon()
    fig05_convex_hulls()
    fig06_triangle_inequality()
    fig07_tropical_matrix()
    fig08_bellman_ford()
    fig09_book_map()
    fig10_tropical_polynomial()
    print("Done! All images saved to", OUT)

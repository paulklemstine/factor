#!/usr/bin/env python3
"""Generate all illustrations for Chapter 9: The Four-Rung Ladder — A Journey Through the Doubling Algebras."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import matplotlib.patheffects as pe
import numpy as np
import os

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
GLOW = '#F4D03F'

def save(fig, name, dpi=200):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=dpi, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  Saved {name}")


# ============================================================
# ILLUSTRATION 1: The Four-Rung Ladder
# ============================================================
def fig01_four_rung_ladder():
    fig, ax = plt.subplots(1, 1, figsize=(10, 14))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    # Ladder rails
    rail_x_left = 3.5
    rail_x_right = 6.5
    ax.plot([rail_x_left, rail_x_left], [0.5, 12.5], color=DARK, linewidth=6, zorder=1)
    ax.plot([rail_x_right, rail_x_right], [0.5, 12.5], color=DARK, linewidth=6, zorder=1)

    # Rung data: y-position, label, property lost (left), property gained (right)
    rungs = [
        (2,  r'$\mathbb{R}$',   '—',                 '—',               ACCENT2),
        (4.5,r'$\mathbb{C}$',   'Total ordering',    'Algebraic closure', ACCENT3),
        (7,  r'$\mathbb{H}$',   'Commutativity',     '3D Rotations',     ACCENT5),
        (9.5,r'$\mathbb{O}$',   'Associativity',     '$E_8$ Lattice',    ACCENT4),
    ]

    for y, label, lost, gained, color in rungs:
        # Draw rung
        ax.plot([rail_x_left, rail_x_right], [y, y], color=color, linewidth=8, zorder=3,
                solid_capstyle='round')
        # Label on rung
        ax.text(5.0, y + 0.05, label, fontsize=22, ha='center', va='center',
                fontweight='bold', color='white', zorder=5,
                path_effects=[pe.withStroke(linewidth=3, foreground=DARK)])
        # Lost property (left)
        if lost != '—':
            ax.annotate(f'✗ {lost}', xy=(rail_x_left - 0.2, y),
                        fontsize=11, ha='right', va='center', color=ACCENT1, fontweight='bold')
        # Gained property (right)
        if gained != '—':
            ax.annotate(f'✓ {gained}', xy=(rail_x_right + 0.2, y),
                        fontsize=11, ha='left', va='center', color=ACCENT3, fontweight='bold')

    # Broken fifth rung (Sedenions)
    y5 = 11.5
    # Draw cracked rung pieces
    ax.plot([rail_x_left, 4.6], [y5, y5 + 0.15], color='#888888', linewidth=6, zorder=3,
            solid_capstyle='round', linestyle=(0, (3, 1)))
    ax.plot([5.4, rail_x_right], [y5 - 0.15, y5], color='#888888', linewidth=6, zorder=3,
            solid_capstyle='round', linestyle=(0, (3, 1)))
    # Gap in the middle
    ax.text(5.0, y5, r'$\mathbb{S}$', fontsize=20, ha='center', va='center',
            fontweight='bold', color='#888888', zorder=5)
    ax.text(5.0, y5 + 0.7, '☠ Zero Divisors!', fontsize=13, ha='center', va='center',
            color=ACCENT1, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=LIGHT_RED, edgecolor=ACCENT1, linewidth=2))
    ax.annotate('✗ Division', xy=(rail_x_left - 0.2, y5),
                fontsize=11, ha='right', va='center', color=ACCENT1, fontweight='bold')

    # Dimension labels
    dims = [(2, '$2^0 = 1$'), (4.5, '$2^1 = 2$'), (7, '$2^2 = 4$'), (9.5, '$2^3 = 8$'), (y5, '$2^4 = 16$')]
    for y, dim in dims:
        ax.text(1.2, y, dim, fontsize=11, ha='center', va='center', color=SLATE, fontstyle='italic')

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 13)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('The Four-Rung Ladder of Division Algebras', fontsize=18,
                 fontweight='bold', color=DARK, pad=15)
    save(fig, 'fig01_four_rung_ladder.png')


# ============================================================
# ILLUSTRATION 2: Multiplication Tables (1×1, 2×2, 4×4, 8×8)
# ============================================================
def fig02_multiplication_tables():
    fig, axes = plt.subplots(1, 4, figsize=(22, 6),
                             gridspec_kw={'width_ratios': [1, 2, 4, 8]})
    fig.set_facecolor(SAND)

    # --- 1×1 table for R ---
    ax = axes[0]
    ax.set_facecolor(SAND)
    table_data = [['1']]
    headers = ['1']
    ax.axis('off')
    tbl = ax.table(cellText=table_data, colLabels=headers, rowLabels=['1'],
                   loc='center', cellLoc='center')
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(14)
    tbl.scale(1.5, 2.0)
    for cell in tbl.get_celld().values():
        cell.set_facecolor(CREAM)
        cell.set_edgecolor(DARK)
    ax.set_title(r'$\mathbb{R}$: $1 \times 1$', fontsize=14, fontweight='bold', color=DARK)

    # --- 2×2 table for C ---
    ax = axes[1]
    ax.set_facecolor(SAND)
    headers = ['1', 'i']
    row_labels = ['1', 'i']
    data = [['1', 'i'],
            ['i', '−1']]
    ax.axis('off')
    tbl = ax.table(cellText=data, colLabels=headers, rowLabels=row_labels,
                   loc='center', cellLoc='center')
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(13)
    tbl.scale(1.3, 1.8)
    for cell in tbl.get_celld().values():
        cell.set_facecolor(CREAM)
        cell.set_edgecolor(DARK)
    ax.set_title(r'$\mathbb{C}$: $2 \times 2$ (symmetric)', fontsize=14, fontweight='bold', color=DARK)

    # --- 4×4 table for H ---
    ax = axes[2]
    ax.set_facecolor(SAND)
    headers = ['1', 'i', 'j', 'k']
    row_labels = ['1', 'i', 'j', 'k']
    data = [['1',  'i',  'j',  'k'],
            ['i',  '−1', 'k',  '−j'],
            ['j',  '−k', '−1', 'i'],
            ['k',  'j',  '−i', '−1']]
    ax.axis('off')
    tbl = ax.table(cellText=data, colLabels=headers, rowLabels=row_labels,
                   loc='center', cellLoc='center')
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(12)
    tbl.scale(1.2, 1.6)
    for key, cell in tbl.get_celld().items():
        cell.set_facecolor(CREAM)
        cell.set_edgecolor(DARK)
        # Highlight non-commutative pairs: (i,j)→k vs (j,i)→−k
        if key == (2, 2):  # row i (1-indexed after header), col j (index 2)
            cell.set_facecolor(LIGHT_GREEN)
        if key == (3, 1):  # row j, col i
            cell.set_facecolor(LIGHT_RED)
    ax.set_title(r'$\mathbb{H}$: $4 \times 4$ (non-commutative!)', fontsize=14, fontweight='bold', color=DARK)

    # --- 8×8 table for O (simplified) ---
    ax = axes[3]
    ax.set_facecolor(SAND)
    basis = ['1', 'e₁', 'e₂', 'e₃', 'e₄', 'e₅', 'e₆', 'e₇']
    # Octonion multiplication (one standard convention)
    oct_table = [
        ['1',   'e₁',  'e₂',  'e₃',  'e₄',  'e₅',  'e₆',  'e₇'],
        ['e₁',  '−1',  'e₃',  '−e₂', 'e₅',  '−e₄', '−e₇', 'e₆'],
        ['e₂',  '−e₃', '−1',  'e₁',  'e₆',  'e₇',  '−e₄', '−e₅'],
        ['e₃',  'e₂',  '−e₁', '−1',  'e₇',  '−e₆', 'e₅',  '−e₄'],
        ['e₄',  '−e₅', '−e₆', '−e₇', '−1',  'e₁',  'e₂',  'e₃'],
        ['e₅',  'e₄',  '−e₇', 'e₆',  '−e₁', '−1',  '−e₃', 'e₂'],
        ['e₆',  'e₇',  'e₄',  '−e₅', '−e₂', 'e₃',  '−1',  '−e₁'],
        ['e₇',  '−e₆', 'e₅',  'e₄',  '−e₃', '−e₂', 'e₁',  '−1'],
    ]
    ax.axis('off')
    tbl = ax.table(cellText=oct_table, colLabels=basis, rowLabels=basis,
                   loc='center', cellLoc='center')
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8)
    tbl.scale(1.0, 1.4)
    for key, cell in tbl.get_celld().items():
        cell.set_facecolor(CREAM)
        cell.set_edgecolor(DARK)
        row, col = key
        # Shade some non-associative triples
        if row >= 1 and col >= 0 and row <= 8 and col <= 7:
            if (row in [2, 3, 4] and col in [1, 2, 3]):
                cell.set_facecolor('#E8DAEF')  # light purple for non-assoc region
    ax.set_title(r'$\mathbb{O}$: $8 \times 8$ (non-associative!)', fontsize=14, fontweight='bold', color=DARK)

    fig.suptitle('Multiplication Tables of the Four Division Algebras', fontsize=18,
                 fontweight='bold', color=DARK, y=1.02)
    plt.tight_layout()
    save(fig, 'fig02_multiplication_tables.png')


# ============================================================
# ILLUSTRATION 3: Complex Multiplication in the Argand Plane
# ============================================================
def fig03_argand_commutativity():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
    fig.set_facecolor(SAND)

    z = complex(2, 1)   # z = 2 + i
    w = complex(1, 2)   # w = 1 + 2i
    zw = z * w           # = 0 + 5i
    wz = w * z           # same!

    for ax, title, order in [(ax1, r'$z \cdot w$', 'zw'), (ax2, r'$w \cdot z$', 'wz')]:
        ax.set_facecolor(SAND)
        ax.set_xlim(-2, 6)
        ax.set_ylim(-1, 6)
        ax.set_aspect('equal')
        ax.axhline(0, color=DARK, linewidth=0.5, alpha=0.3)
        ax.axvline(0, color=DARK, linewidth=0.5, alpha=0.3)
        ax.grid(True, alpha=0.15, color=DARK)

        # Draw z
        ax.annotate('', xy=(z.real, z.imag), xytext=(0, 0),
                     arrowprops=dict(arrowstyle='->', color=ACCENT2, lw=2.5))
        ax.text(z.real + 0.15, z.imag + 0.2, r'$z = 2 + i$', fontsize=12, color=ACCENT2, fontweight='bold')

        # Draw w
        ax.annotate('', xy=(w.real, w.imag), xytext=(0, 0),
                     arrowprops=dict(arrowstyle='->', color=ACCENT3, lw=2.5))
        ax.text(w.real - 0.9, w.imag + 0.2, r'$w = 1 + 2i$', fontsize=12, color=ACCENT3, fontweight='bold')

        # Draw product
        prod = zw
        ax.annotate('', xy=(prod.real, prod.imag), xytext=(0, 0),
                     arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=3))
        ax.text(prod.real + 0.2, prod.imag + 0.2, f'{title} = {int(prod.real)} + {int(prod.imag)}i',
                fontsize=13, color=ACCENT1, fontweight='bold')

        # Angle arcs
        angle_z = np.degrees(np.arctan2(z.imag, z.real))
        angle_w = np.degrees(np.arctan2(w.imag, w.real))
        angle_p = np.degrees(np.arctan2(prod.imag, prod.real))

        arc_z = patches.Arc((0, 0), 1.5, 1.5, angle=0, theta1=0, theta2=angle_z,
                             color=ACCENT2, linewidth=1.5, linestyle='--')
        arc_w = patches.Arc((0, 0), 2.0, 2.0, angle=0, theta1=0, theta2=angle_w,
                             color=ACCENT3, linewidth=1.5, linestyle='--')
        arc_p = patches.Arc((0, 0), 2.5, 2.5, angle=0, theta1=0, theta2=angle_p,
                             color=ACCENT1, linewidth=1.5, linestyle='--')
        ax.add_patch(arc_z)
        ax.add_patch(arc_w)
        ax.add_patch(arc_p)

        ax.set_xlabel('Real', fontsize=12, color=DARK)
        ax.set_ylabel('Imaginary', fontsize=12, color=DARK)
        ax.set_title(title, fontsize=16, fontweight='bold', color=DARK)

    fig.suptitle('Swap the order, get the same arrow. This is commutativity — and it\'s about to die.',
                 fontsize=14, fontstyle='italic', color=SLATE, y=0.02)
    plt.tight_layout()
    save(fig, 'fig03_argand_commutativity.png')


# ============================================================
# ILLUSTRATION 4: Brahmagupta's Multiplication Machine
# ============================================================
def fig04_brahmagupta_machine():
    fig, ax = plt.subplots(1, 1, figsize=(14, 9))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.axis('off')

    # Input boxes (left)
    box1 = FancyBboxPatch((0.5, 5.5), 3.5, 1.8, boxstyle="round,pad=0.2",
                          facecolor=LIGHT_BLUE, edgecolor=ACCENT2, linewidth=2)
    box2 = FancyBboxPatch((0.5, 2.5), 3.5, 1.8, boxstyle="round,pad=0.2",
                          facecolor=LIGHT_BLUE, edgecolor=ACCENT2, linewidth=2)
    ax.add_patch(box1)
    ax.add_patch(box2)
    ax.text(2.25, 6.4, r'$a^2 + b^2$', fontsize=18, ha='center', va='center', color=DARK, fontweight='bold')
    ax.text(2.25, 3.4, r'$c^2 + d^2$', fontsize=18, ha='center', va='center', color=DARK, fontweight='bold')

    # Gearbox (center)
    gear = FancyBboxPatch((5.0, 3.0), 4, 3.5, boxstyle="round,pad=0.3",
                          facecolor=GOLD, edgecolor=DARK, linewidth=3, alpha=0.8)
    ax.add_patch(gear)
    ax.text(7.0, 5.3, "Brahmagupta's", fontsize=14, ha='center', va='center', color=DARK, fontweight='bold')
    ax.text(7.0, 4.5, 'Identity', fontsize=14, ha='center', va='center', color=DARK, fontweight='bold')
    # Gear teeth (decorative)
    for angle in np.linspace(0, 2*np.pi, 12, endpoint=False):
        gx = 7.0 + 2.3 * np.cos(angle)
        gy = 4.75 + 2.0 * np.sin(angle)
        ax.plot(gx, gy, 's', color=DARK, markersize=6, alpha=0.3)

    # Output box (right)
    box3 = FancyBboxPatch((10.0, 3.5), 3.5, 2.5, boxstyle="round,pad=0.2",
                          facecolor=LIGHT_GREEN, edgecolor=ACCENT3, linewidth=2)
    ax.add_patch(box3)
    ax.text(11.75, 5.1, r'$(ac - bd)^2$', fontsize=15, ha='center', va='center', color=DARK, fontweight='bold')
    ax.text(11.75, 4.3, r'$+ (ad + bc)^2$', fontsize=15, ha='center', va='center', color=DARK, fontweight='bold')

    # Arrows
    ax.annotate('', xy=(5.0, 5.0), xytext=(4.0, 6.4),
                arrowprops=dict(arrowstyle='->', color=ACCENT2, lw=2.5))
    ax.annotate('', xy=(5.0, 4.5), xytext=(4.0, 3.4),
                arrowprops=dict(arrowstyle='->', color=ACCENT2, lw=2.5))
    ax.annotate('', xy=(10.0, 4.75), xytext=(9.0, 4.75),
                arrowprops=dict(arrowstyle='->', color=ACCENT3, lw=2.5))

    # Worked example below
    ax.text(7.0, 1.8, 'Worked Example:', fontsize=14, ha='center', va='center',
            color=DARK, fontweight='bold')
    ax.text(7.0, 1.1,
            r'$1^2 + 2^2 = 5$  and  $2^2 + 3^2 = 13$',
            fontsize=13, ha='center', va='center', color=SLATE)
    ax.text(7.0, 0.4,
            r'$(1{\cdot}2 - 2{\cdot}3)^2 + (1{\cdot}3 + 2{\cdot}2)^2 = (-4)^2 + 7^2 = 16 + 49 = 65\;\checkmark$',
            fontsize=13, ha='center', va='center', color=ACCENT3, fontweight='bold')

    ax.set_title("Brahmagupta's Multiplication Machine", fontsize=18,
                 fontweight='bold', color=DARK, pad=15)
    save(fig, 'fig04_brahmagupta_machine.png')


# ============================================================
# ILLUSTRATION 5: Quaternion Fano Plane Mnemonic
# ============================================================
def fig05_quaternion_fano():
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    # Three vertices of a triangle + center
    r = 3.0
    angles = [np.pi/2, np.pi/2 + 2*np.pi/3, np.pi/2 + 4*np.pi/3]
    pts = {
        'i': (r * np.cos(angles[0]), r * np.sin(angles[0])),
        'j': (r * np.cos(angles[1]), r * np.sin(angles[1])),
        'k': (r * np.cos(angles[2]), r * np.sin(angles[2])),
    }

    # Draw triangle edges
    for (a, b) in [('i', 'j'), ('j', 'k'), ('k', 'i')]:
        ax.plot([pts[a][0], pts[b][0]], [pts[a][1], pts[b][1]],
                color=DARK, linewidth=2, zorder=1)

    # Draw inscribed circle
    circle = plt.Circle((0, 0), r * 0.5, fill=False, color=DARK, linewidth=2, linestyle='--', zorder=1)
    ax.add_patch(circle)

    # Draw directed arrows along edges (cyclic: i→j→k→i)
    arrow_pairs = [('i', 'j', ACCENT3), ('j', 'k', ACCENT3), ('k', 'i', ACCENT3)]
    for a, b, color in arrow_pairs:
        dx = pts[b][0] - pts[a][0]
        dy = pts[b][1] - pts[a][1]
        mid_x = pts[a][0] + 0.45 * dx
        mid_y = pts[a][1] + 0.45 * dy
        ax.annotate('', xy=(pts[a][0] + 0.6 * dx, pts[a][1] + 0.6 * dy),
                     xytext=(pts[a][0] + 0.35 * dx, pts[a][1] + 0.35 * dy),
                     arrowprops=dict(arrowstyle='->', color=color, lw=3))

    # Draw nodes
    for name, (x, y) in pts.items():
        circle_node = plt.Circle((x, y), 0.4, facecolor='white', edgecolor=DARK, linewidth=2.5, zorder=5)
        ax.add_patch(circle_node)
        ax.text(x, y, r'$\mathbf{' + name + '}$', fontsize=22, ha='center', va='center',
                fontweight='bold', color=DARK, zorder=6)

    # Annotations for products
    ax.text(0, 4.2, r'$\mathbf{i} \cdot \mathbf{j} = +\mathbf{k}$', fontsize=16,
            ha='center', color=ACCENT3, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=LIGHT_GREEN, edgecolor=ACCENT3))
    ax.text(0, -4.2, r'$\mathbf{j} \cdot \mathbf{i} = -\mathbf{k}$', fontsize=16,
            ha='center', color=ACCENT1, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=LIGHT_RED, edgecolor=ACCENT1))

    # Arrow legend
    ax.text(-4.5, 0, '→ positive\n(with arrows)', fontsize=12, color=ACCENT3, fontweight='bold',
            ha='center', va='center')
    ax.text(4.5, 0, '← negative\n(against arrows)', fontsize=12, color=ACCENT1, fontweight='bold',
            ha='center', va='center')

    ax.set_xlim(-5.5, 5.5)
    ax.set_ylim(-5.5, 5.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Quaternion Multiplication: The Cyclic Mnemonic', fontsize=18,
                 fontweight='bold', color=DARK, pad=15)
    save(fig, 'fig05_quaternion_fano.png')


# ============================================================
# ILLUSTRATION 6: Non-Commutative Rotation Demonstration
# ============================================================
def fig06_rotation_demo():
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    fig.set_facecolor(SAND)

    def draw_book(ax, corners, color, label, alpha=0.6):
        """Draw a 3D-ish book face from 4 corners."""
        poly = plt.Polygon(corners, facecolor=color, edgecolor=DARK, linewidth=2, alpha=alpha, zorder=3)
        ax.add_patch(poly)
        cx = np.mean([c[0] for c in corners])
        cy = np.mean([c[1] for c in corners])
        ax.text(cx, cy, label, fontsize=10, ha='center', va='center', fontweight='bold', color=DARK, zorder=4)

    sequences = [
        ("Sequence A: X then Y", [
            ("Start", [(1,1),(3,1),(3,3),(1,3)], LIGHT_BLUE),
            (r"Rot 90° about $x$", [(4.5,1),(6.5,1),(6.5,2),(4.5,2)], LIGHT_GREEN),
            (r"Then 90° about $y$", [(8,1.5),(9,1),(9,3),(8,3.5)], ACCENT5),
        ]),
        ("Sequence B: Y then X", [
            ("Start", [(1,1),(3,1),(3,3),(1,3)], LIGHT_BLUE),
            (r"Rot 90° about $y$", [(4.5,1.5),(5.5,1),(5.5,3),(4.5,3.5)], LIGHT_GREEN),
            (r"Then 90° about $x$", [(8,2),(10,2),(10,3),(8,3)], '#FFB3BA'),
        ]),
    ]

    for ax, (title, steps) in zip(axes, sequences):
        ax.set_facecolor(SAND)
        ax.set_xlim(0, 11)
        ax.set_ylim(0, 5)
        ax.set_aspect('equal')
        ax.axis('off')

        for label, corners, color in steps:
            draw_book(ax, corners, color, label)

        # Arrows between stages
        ax.annotate('', xy=(4.3, 2), xytext=(3.2, 2),
                     arrowprops=dict(arrowstyle='->', color=DARK, lw=2))
        ax.annotate('', xy=(7.8, 2), xytext=(6.7, 2),
                     arrowprops=dict(arrowstyle='->', color=DARK, lw=2))

        ax.set_title(title, fontsize=15, fontweight='bold', color=DARK)

    # Final result comparison
    fig.text(0.5, 0.02, 'Final orientations differ! Rotations do not commute.',
             fontsize=14, ha='center', color=ACCENT1, fontweight='bold', fontstyle='italic')
    fig.suptitle('This is why Hamilton needed non-commutative multiplication.',
                 fontsize=16, fontweight='bold', color=DARK, y=0.98)
    plt.tight_layout(rect=[0, 0.05, 1, 0.93])
    save(fig, 'fig06_rotation_demo.png')


# ============================================================
# ILLUSTRATION 7: Euler's Four-Square Super-Gearbox
# ============================================================
def fig07_euler_gearbox():
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Input boxes (left side, 4 squares each)
    input_labels = [r'$x_1^2$', r'$x_2^2$', r'$x_3^2$', r'$x_4^2$']
    for i, lbl in enumerate(input_labels):
        y = 7.5 - i * 1.5
        box = FancyBboxPatch((0.3, y - 0.4), 2.0, 0.8, boxstyle="round,pad=0.15",
                              facecolor=LIGHT_BLUE, edgecolor=ACCENT2, linewidth=1.5)
        ax.add_patch(box)
        ax.text(1.3, y, lbl, fontsize=14, ha='center', va='center', color=DARK, fontweight='bold')

    input_labels2 = [r'$y_1^2$', r'$y_2^2$', r'$y_3^2$', r'$y_4^2$']
    for i, lbl in enumerate(input_labels2):
        y = 7.5 - i * 1.5
        box = FancyBboxPatch((3.0, y - 0.4), 2.0, 0.8, boxstyle="round,pad=0.15",
                              facecolor=LIGHT_BLUE, edgecolor=ACCENT2, linewidth=1.5)
        ax.add_patch(box)
        ax.text(4.0, y, lbl, fontsize=14, ha='center', va='center', color=DARK, fontweight='bold')

    # Plus signs and sums
    ax.text(1.3, 8.5, r'$\sum = x_1^2+x_2^2+x_3^2+x_4^2$', fontsize=11, ha='center', color=SLATE)
    ax.text(4.0, 8.5, r'$\sum = y_1^2+y_2^2+y_3^2+y_4^2$', fontsize=11, ha='center', color=SLATE)

    # Gearbox (center)
    gear = FancyBboxPatch((6.0, 3.0), 4, 4, boxstyle="round,pad=0.3",
                          facecolor=GOLD, edgecolor=DARK, linewidth=3, alpha=0.8)
    ax.add_patch(gear)
    ax.text(8.0, 5.5, "Euler's", fontsize=16, ha='center', va='center', color=DARK, fontweight='bold')
    ax.text(8.0, 4.7, 'Four-Square', fontsize=14, ha='center', va='center', color=DARK, fontweight='bold')
    ax.text(8.0, 4.0, 'Identity', fontsize=14, ha='center', va='center', color=DARK, fontweight='bold')

    # Decorative gears
    for angle in np.linspace(0, 2*np.pi, 16, endpoint=False):
        gx = 8.0 + 2.5 * np.cos(angle)
        gy = 5.0 + 2.3 * np.sin(angle)
        ax.plot(gx, gy, 's', color=DARK, markersize=5, alpha=0.3)

    # Output boxes (right side)
    output_labels = [
        r'$(x_1 y_1 - x_2 y_2 - x_3 y_3 - x_4 y_4)^2$',
        r'$(x_1 y_2 + x_2 y_1 + x_3 y_4 - x_4 y_3)^2$',
        r'$(x_1 y_3 - x_2 y_4 + x_3 y_1 + x_4 y_2)^2$',
        r'$(x_1 y_4 + x_2 y_3 - x_3 y_2 + x_4 y_1)^2$',
    ]
    for i, lbl in enumerate(output_labels):
        y = 7.5 - i * 1.5
        box = FancyBboxPatch((10.8, y - 0.4), 4.8, 0.8, boxstyle="round,pad=0.15",
                              facecolor=LIGHT_GREEN, edgecolor=ACCENT3, linewidth=1.5)
        ax.add_patch(box)
        ax.text(13.2, y, lbl, fontsize=9, ha='center', va='center', color=DARK, fontweight='bold')

    # Arrows
    ax.annotate('', xy=(6.0, 5.5), xytext=(5.2, 6.5),
                arrowprops=dict(arrowstyle='->', color=ACCENT2, lw=2))
    ax.annotate('', xy=(6.0, 4.5), xytext=(5.2, 4.5),
                arrowprops=dict(arrowstyle='->', color=ACCENT2, lw=2))
    ax.annotate('', xy=(10.8, 5.0), xytext=(10.0, 5.0),
                arrowprops=dict(arrowstyle='->', color=ACCENT3, lw=2))

    # Worked example
    ax.text(8.0, 1.5, 'Example: $(1^2+1^2+1^2+1^2)(1^2+2^2+0^2+0^2) = 4 \\times 5 = 20$',
            fontsize=12, ha='center', color=DARK, fontweight='bold')
    ax.text(8.0, 0.7, r'$= (1{\cdot}1-1{\cdot}2-1{\cdot}0-1{\cdot}0)^2 + \ldots = (-1)^2 + 3^2 + 1^2 + 3^2 = 1+9+1+9 = 20\;\checkmark$',
            fontsize=11, ha='center', color=ACCENT3, fontweight='bold')

    ax.set_title("Euler's Four-Square Super-Gearbox", fontsize=18,
                 fontweight='bold', color=DARK, pad=15)
    save(fig, 'fig07_euler_gearbox.png')


# ============================================================
# ILLUSTRATION 8: Brahmagupta vs Euler Comparison
# ============================================================
def fig08_identity_comparison():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    fig.set_facecolor(SAND)

    # Brahmagupta (left)
    ax1.set_facecolor(SAND)
    ax1.axis('off')
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    box = FancyBboxPatch((0.5, 2), 9, 6, boxstyle="round,pad=0.5",
                          facecolor=CREAM, edgecolor=ACCENT2, linewidth=3)
    ax1.add_patch(box)
    ax1.text(5, 7, 'Brahmagupta–Fibonacci', fontsize=16, ha='center', fontweight='bold', color=ACCENT2)
    ax1.text(5, 6, '2 squares × 2 squares = 2 squares', fontsize=12, ha='center', color=SLATE, fontstyle='italic')
    ax1.text(5, 4.5, r'$(a^2 + b^2)(c^2 + d^2)$', fontsize=16, ha='center', color=DARK)
    ax1.text(5, 3.5, r'$= (ac - bd)^2 + (ad + bc)^2$', fontsize=16, ha='center', color=DARK)
    ax1.text(5, 1.2, 'Elegant. Two lines.', fontsize=13, ha='center', color=ACCENT3, fontstyle='italic')

    # Euler (right)
    ax2.set_facecolor(SAND)
    ax2.axis('off')
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    box2 = FancyBboxPatch((0.5, 1), 9, 7.5, boxstyle="round,pad=0.5",
                           facecolor=CREAM, edgecolor=ACCENT5, linewidth=3)
    ax2.add_patch(box2)
    ax2.text(5, 7.8, 'Euler Four-Square', fontsize=16, ha='center', fontweight='bold', color=ACCENT5)
    ax2.text(5, 7, '4 squares × 4 squares = 4 squares', fontsize=12, ha='center', color=SLATE, fontstyle='italic')
    ax2.text(5, 5.8, r'$(x_1^2+x_2^2+x_3^2+x_4^2)(y_1^2+y_2^2+y_3^2+y_4^2)$', fontsize=11, ha='center', color=DARK)
    ax2.text(5, 4.9, r'$=(x_1 y_1 - x_2 y_2 - x_3 y_3 - x_4 y_4)^2$', fontsize=10, ha='center', color=DARK)
    ax2.text(5, 4.2, r'$+(x_1 y_2 + x_2 y_1 + x_3 y_4 - x_4 y_3)^2$', fontsize=10, ha='center', color=DARK)
    ax2.text(5, 3.5, r'$+(x_1 y_3 - x_2 y_4 + x_3 y_1 + x_4 y_2)^2$', fontsize=10, ha='center', color=DARK)
    ax2.text(5, 2.8, r'$+(x_1 y_4 + x_2 y_3 - x_3 y_2 + x_4 y_1)^2$', fontsize=10, ha='center', color=DARK)
    ax2.text(5, 1.2, 'A sprawling quartet. Four lines.', fontsize=13, ha='center', color=ACCENT1, fontstyle='italic')

    fig.suptitle('The Growth in Complexity: From Couplet to Quartet', fontsize=18,
                 fontweight='bold', color=DARK, y=0.98)
    plt.tight_layout()
    save(fig, 'fig08_identity_comparison.png')


# ============================================================
# ILLUSTRATION 9: Staircase of Squares
# ============================================================
def fig09_staircase():
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Steps
    steps = [
        (1, 1, 2.5, 1.8, r'$a^2$', '1 square', [ACCENT2]),
        (4, 2.5, 2.5, 1.8, r'$a^2 + b^2$', '2 squares', [ACCENT2, ACCENT3]),
        (7, 4, 3.5, 1.8, r'$a^2+b^2+c^2+d^2$', '4 squares', [ACCENT2, ACCENT3, ACCENT5, ACCENT4]),
        (11, 5.5, 4.5, 1.8, r'$\sum_{i=0}^{7} f(i)^2$', '8 squares', [ACCENT2, ACCENT3, ACCENT5, ACCENT4, '#ccc', '#ccc', '#ccc', '#ccc']),
    ]

    for x, y, w, h, label, desc, colors in steps:
        # Draw step platform
        step_rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                                            facecolor=CREAM, edgecolor=DARK, linewidth=2)
        ax.add_patch(step_rect)

        # Draw small squares on the step
        sq_size = 0.45
        sq_gap = 0.15
        n_sq = len(colors)
        total_w = n_sq * sq_size + (n_sq - 1) * sq_gap
        start_x = x + (w - total_w) / 2
        for i, c in enumerate(colors):
            sx = start_x + i * (sq_size + sq_gap)
            sq = patches.Rectangle((sx, y + h - sq_size - 0.2), sq_size, sq_size,
                                    facecolor=c, edgecolor=DARK, linewidth=1.5,
                                    alpha=0.4 if c == '#ccc' else 0.8, zorder=3)
            ax.add_patch(sq)

        # Labels
        ax.text(x + w/2, y + 0.3, label, fontsize=12, ha='center', va='center',
                color=DARK, fontweight='bold')
        ax.text(x + w/2, y - 0.3, desc, fontsize=11, ha='center', va='center',
                color=SLATE, fontstyle='italic')

    # Arrows between steps labeled "pad with zeros"
    arrow_positions = [(3.5, 2.0, 4.0, 3.0), (6.5, 3.5, 7.0, 4.5), (10.5, 5.0, 11.0, 6.0)]
    for x1, y1, x2, y2 in arrow_positions:
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                     arrowprops=dict(arrowstyle='->', color=ACCENT3, lw=2.5))
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx + 0.3, my + 0.3, 'pad 0s', fontsize=9, color=ACCENT3,
                fontstyle='italic', rotation=35)

    ax.text(8, 9, 'Every channel nests inside the one above it.',
            fontsize=15, ha='center', color=DARK, fontweight='bold', fontstyle='italic')

    ax.set_title('The Staircase of Squares', fontsize=18,
                 fontweight='bold', color=DARK, pad=15)
    save(fig, 'fig09_staircase.png')


# ============================================================
# ILLUSTRATION 10: Powers of 2 Number Line (Hurwitz Dimensions)
# ============================================================
def fig10_magic_dimensions():
    fig, ax = plt.subplots(1, 1, figsize=(16, 6))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    powers = [1, 2, 4, 8, 16, 32, 64]
    labels = [r'$\mathbb{R}$', r'$\mathbb{C}$', r'$\mathbb{H}$', r'$\mathbb{O}$', '', '', '']
    colors_ring = [ACCENT2, ACCENT3, ACCENT5, ACCENT4, ACCENT1, '#aaa', '#aaa']

    # Draw number line
    ax.plot([0, 70], [3, 3], color=DARK, linewidth=2)

    for i, (p, lbl, col) in enumerate(zip(powers, labels, colors_ring)):
        x = p  # Use log-ish spacing for readability
        x_pos = i * 10 + 2

        # Tick
        ax.plot([x_pos, x_pos], [2.7, 3.3], color=DARK, linewidth=2)

        # Number label
        ax.text(x_pos, 2.2, str(p), fontsize=14, ha='center', va='center', color=DARK, fontweight='bold')

        if i < 4:
            # Circle the first four
            circle = plt.Circle((x_pos, 3), 1.0, fill=False, edgecolor=col, linewidth=3, zorder=5)
            ax.add_patch(circle)
            # Algebra label
            ax.text(x_pos, 4.5, lbl, fontsize=18, ha='center', va='center',
                    fontweight='bold', color=col)
        elif i == 4:
            # Big red X on 16
            ax.text(x_pos, 3, '✗', fontsize=30, ha='center', va='center',
                    color=ACCENT1, fontweight='bold', zorder=5)
            ax.text(x_pos, 4.5, 'Zero\ndivisors!', fontsize=11, ha='center', va='center',
                    color=ACCENT1, fontweight='bold')
        else:
            ax.text(x_pos, 3, '·', fontsize=20, ha='center', va='center', color='#aaa')

    # Dots to indicate continuation
    ax.text(67, 3, '· · ·', fontsize=18, ha='center', va='center', color=SLATE)

    ax.set_xlim(-2, 72)
    ax.set_ylim(0, 6)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('The Magic Dimensions: Only 1, 2, 4, 8 Admit Division Algebras',
                 fontsize=16, fontweight='bold', color=DARK, pad=15)
    save(fig, 'fig10_magic_dimensions.png')


# ============================================================
# ILLUSTRATION 11: Venn Diagram of Algebraic Properties
# ============================================================
def fig11_venn_algebras():
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    # Concentric rounded rectangles, outermost to innermost
    levels = [
        (0.5, 0.5, 11, 9, 'Algebra', ACCENT1, '#F9E8E8', r'$\mathbb{S}$ (Sedenions)'),
        (1.3, 1.3, 9.4, 7.4, 'Alternative Algebra', ACCENT4, '#EDE7F6', r'$\mathbb{O}$ (Octonions)'),
        (2.1, 2.1, 7.8, 5.8, 'Associative Algebra', ACCENT5, '#FFF3E0', r'$\mathbb{H}$ (Quaternions)'),
        (2.9, 2.9, 6.2, 4.2, 'Commutative Algebra', ACCENT3, '#E8F5E9', r'$\mathbb{C}$ (Complex)'),
        (3.7, 3.7, 4.6, 2.6, 'Ordered Field', ACCENT2, '#E3F2FD', r'$\mathbb{R}$ (Reals)'),
    ]

    for x, y, w, h, name, edge_col, fill_col, algebra in levels:
        rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3",
                               facecolor=fill_col, edgecolor=edge_col, linewidth=2.5, zorder=1)
        ax.add_patch(rect)
        # Label at top
        ax.text(x + w/2, y + h - 0.35, name, fontsize=12, ha='center', va='center',
                fontweight='bold', color=edge_col, zorder=5)
        # Algebra name at bottom right
        ax.text(x + w - 0.4, y + 0.4, algebra, fontsize=10, ha='right', va='center',
                color=SLATE, fontstyle='italic', zorder=5)

    # Property loss labels on left boundary
    property_losses = [
        (1.0, 5.5, '↑ loses: Division'),
        (1.8, 4.7, '↑ loses: Associativity'),
        (2.6, 3.9, '↑ loses: Commutativity'),
        (3.4, 3.1, '↑ loses: Total ordering'),
    ]
    for x, y, txt in property_losses:
        ax.text(x - 0.2, y, txt, fontsize=9, ha='left', va='center',
                color=ACCENT1, fontweight='bold', rotation=90, zorder=5)

    ax.set_xlim(-0.5, 12.5)
    ax.set_ylim(-0.5, 11)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Nested Algebraic Structures: Each Step Out Loses a Property',
                 fontsize=16, fontweight='bold', color=DARK, pad=15)
    save(fig, 'fig11_venn_algebras.png')


# ============================================================
# ILLUSTRATION 12: Square Root Solutions on Number Line
# ============================================================
def fig12_square_root_bandwidth():
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 6))
    fig.set_facecolor(SAND)

    for ax, n, solutions, label in [
        (ax1, 25, [5, -5], r'$n = 25$: Two solutions'),
        (ax2, 7, [], r'$n = 7$: No integer solutions'),
    ]:
        ax.set_facecolor(SAND)
        ax.set_xlim(-8, 8)
        ax.set_ylim(-0.5, 2.5)

        # Number line
        ax.plot([-7, 7], [0, 0], color=DARK, linewidth=2)
        for i in range(-6, 7):
            ax.plot([i, i], [-0.1, 0.1], color=DARK, linewidth=1)
            if i % 2 == 0 or abs(i) <= 1:
                ax.text(i, -0.3, str(i), fontsize=9, ha='center', va='top', color=DARK)

        # Highlight solutions
        for s in solutions:
            ax.plot(s, 0, 'o', color=ACCENT1, markersize=15, markeredgecolor=DARK,
                    markeredgewidth=2, zorder=5)
            ax.text(s, 0.5, f'$a = {s}$', fontsize=12, ha='center', va='bottom',
                    color=ACCENT1, fontweight='bold')

        if solutions:
            # Bracket
            ax.annotate('', xy=(solutions[1] - 0.3, 1.8), xytext=(solutions[0] + 0.3, 1.8),
                         arrowprops=dict(arrowstyle='<->', color=ACCENT2, lw=2))
            ax.text(0, 2.1, r'$\leq 2$ solutions, always', fontsize=12, ha='center',
                    color=ACCENT2, fontweight='bold')

        ax.text(-7.5, 1.0, label, fontsize=13, ha='left', va='center',
                color=DARK, fontweight='bold')
        ax.axis('off')

    fig.suptitle('The Simplest Channel Has the Tightest Bandwidth',
                 fontsize=16, fontweight='bold', color=DARK, y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.93])
    save(fig, 'fig12_square_root_bandwidth.png')


# ============================================================
# ILLUSTRATION 13: Jacobi Divisor Diagram for n=12
# ============================================================
def fig13_jacobi_divisors():
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis('off')

    divisors = [1, 2, 3, 4, 6, 12]
    div_by_4 = {4, 12}

    ax.text(7, 7.3, r'Divisors of $n = 12$', fontsize=18, ha='center',
            fontweight='bold', color=DARK)

    # Draw divisor boxes
    x_start = 1.5
    x_gap = 2.0
    y_div = 5.5

    kept_sum = 0
    for i, d in enumerate(divisors):
        x = x_start + i * x_gap
        is_bad = d in div_by_4
        color = LIGHT_RED if is_bad else LIGHT_GREEN
        edge = ACCENT1 if is_bad else ACCENT3

        box = FancyBboxPatch((x - 0.6, y_div - 0.5), 1.2, 1.0, boxstyle="round,pad=0.1",
                              facecolor=color, edgecolor=edge, linewidth=2)
        ax.add_patch(box)
        ax.text(x, y_div, str(d), fontsize=18, ha='center', va='center',
                fontweight='bold', color=DARK)

        if is_bad:
            # Red X
            ax.text(x, y_div, '✗', fontsize=28, ha='center', va='center',
                    color=ACCENT1, alpha=0.5, fontweight='bold', zorder=5)
            ax.text(x, y_div - 0.8, r'$4 \mid d$', fontsize=10, ha='center',
                    color=ACCENT1, fontstyle='italic')
        else:
            kept_sum += d

    # Sum line
    ax.text(7, 3.8, r'Keep: $\{1, 2, 3, 6\}$', fontsize=14, ha='center',
            color=ACCENT3, fontweight='bold')
    ax.text(7, 3.0, f'$J(12) = 1 + 2 + 3 + 6 = {kept_sum}$', fontsize=16, ha='center',
            color=DARK, fontweight='bold')

    # Final result
    result_box = FancyBboxPatch((3, 0.8), 8, 1.5, boxstyle="round,pad=0.3",
                                 facecolor=GOLD, edgecolor=DARK, linewidth=3, alpha=0.7)
    ax.add_patch(result_box)
    ax.text(7, 1.55, f'$r_4(12) = 8 \\times J(12) = 8 \\times {kept_sum} = {8*kept_sum}$',
            fontsize=18, ha='center', va='center', color=DARK, fontweight='bold')

    ax.text(7, 0.3, 'There are 96 ways to write 12 as a sum of four squares!',
            fontsize=13, ha='center', color=SLATE, fontstyle='italic')

    ax.set_title("Jacobi's Four-Square Formula in Action", fontsize=18,
                 fontweight='bold', color=DARK, pad=15)
    save(fig, 'fig13_jacobi_divisors.png')


# ============================================================
# ILLUSTRATION 14: Representations of 1 as Sum of Four Squares
# ============================================================
def fig14_representations_of_one():
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # 8 representations of 1 = a² + b² + c² + d²
    # They are: (±1, 0, 0, 0), (0, ±1, 0, 0), (0, 0, ±1, 0), (0, 0, 0, ±1)
    reps = [
        (1, 0, 0, 0),
        (-1, 0, 0, 0),
        (0, 1, 0, 0),
        (0, -1, 0, 0),
        (0, 0, 1, 0),
        (0, 0, -1, 0),
        (0, 0, 0, 1),
        (0, 0, 0, -1),
    ]

    ax.text(6, 9.3, r'All 8 representations of $1 = a^2 + b^2 + c^2 + d^2$',
            fontsize=16, ha='center', fontweight='bold', color=DARK)

    y_start = 8.0
    y_gap = 0.9
    box_w = 1.5
    box_h = 0.6
    x_start = 2.0
    x_gap = 2.0

    colors = [ACCENT2, ACCENT3, ACCENT5, ACCENT4]

    for row, (a, b, c, d) in enumerate(reps):
        y = y_start - row * y_gap
        vals = [a, b, c, d]
        for col, v in enumerate(vals):
            x = x_start + col * x_gap
            is_nonzero = v != 0
            fc = colors[col] if is_nonzero else CREAM
            alpha = 0.8 if is_nonzero else 0.4
            box = FancyBboxPatch((x - box_w/2, y - box_h/2), box_w, box_h,
                                  boxstyle="round,pad=0.1",
                                  facecolor=fc, edgecolor=DARK, linewidth=1.5, alpha=alpha)
            ax.add_patch(box)
            txt = str(v) if is_nonzero else '0'
            ax.text(x, y, txt, fontsize=14, ha='center', va='center',
                    fontweight='bold' if is_nonzero else 'normal',
                    color='white' if is_nonzero else SLATE)

        # Equals sign
        ax.text(x_start + 4 * x_gap - 0.5, y, '= 1', fontsize=14, ha='center', va='center',
                color=DARK, fontweight='bold')

    # Column headers
    headers = [r'$a$', r'$b$', r'$c$', r'$d$']
    for col, h in enumerate(headers):
        ax.text(x_start + col * x_gap, y_start + 0.6, h, fontsize=14, ha='center',
                va='center', color=DARK, fontweight='bold')

    ax.text(6, 0.5, r'Exactly $r_4(1) = 8 \times J(1) = 8 \times 1 = 8$',
            fontsize=14, ha='center', color=ACCENT3, fontweight='bold')

    ax.set_title('The 8 Representations of 1', fontsize=18,
                 fontweight='bold', color=DARK, pad=15)
    save(fig, 'fig14_representations_of_one.png')


# ============================================================
# ILLUSTRATION 15: Cayley-Dickson Cartographic Map
# ============================================================
def fig15_cayley_dickson_map():
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    fig.set_facecolor('#E8D5B7')  # parchment
    ax.set_facecolor('#E8D5B7')

    # Water background
    water = patches.Rectangle((-1, -1), 18, 12, facecolor='#B3D9FF', alpha=0.3, zorder=0)
    ax.add_patch(water)

    # Islands
    islands = [
        (2, 5, 2.0, r'$\mathbb{R}$', 'Reals', ACCENT2, '#D6EAF8'),
        (6, 5, 2.2, r'$\mathbb{C}$', 'Complex', ACCENT3, '#D5F5E3'),
        (10, 5, 2.4, r'$\mathbb{H}$', 'Quaternions', ACCENT5, '#FDEBD0'),
        (14, 5, 2.6, r'$\mathbb{O}$', 'Octonions', ACCENT4, '#E8DAEF'),
    ]

    for x, y, r, sym, name, col, fill in islands:
        # Island shape (irregular circle)
        angles = np.linspace(0, 2*np.pi, 50)
        np.random.seed(hash(name) % 1000)
        radii = r + 0.15 * np.random.randn(50)
        radii = np.maximum(radii, r * 0.7)
        ix = x + radii * np.cos(angles)
        iy = y + radii * np.sin(angles)
        ax.fill(ix, iy, facecolor=fill, edgecolor=col, linewidth=2, zorder=2)

        ax.text(x, y + 0.3, sym, fontsize=24, ha='center', va='center',
                fontweight='bold', color=col, zorder=5)
        ax.text(x, y - 0.5, name, fontsize=11, ha='center', va='center',
                color=DARK, fontstyle='italic', zorder=5)

    # Bridges with toll labels
    bridges = [
        (2, 6, '—'),
        (6, 10, 'Loses:\nOrdering'),
        (10, 14, 'Loses:\nCommutativity'),
    ]
    # Actually the bridges connect sequentially and the tolls are for crossing TO the next
    bridge_data = [
        ((3.5, 5), (4.5, 5), 'Toll: Ordering'),
        ((7.5, 5), (8.5, 5), 'Toll: Commutativity'),
        ((11.5, 5), (12.5, 5), 'Toll: Associativity'),
    ]

    for (x1, y1), (x2, y2), toll in bridge_data:
        ax.plot([x1, x2], [y1, y2], color=DARK, linewidth=4, zorder=3)
        ax.plot([x1, x2], [y1 + 0.1, y2 + 0.1], color=GOLD, linewidth=2, zorder=4)
        mx = (x1 + x2) / 2
        ax.text(mx, y1 + 0.8, toll, fontsize=8, ha='center', va='center',
                color=ACCENT1, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='#FFF', edgecolor=ACCENT1, alpha=0.9),
                zorder=5)

    # "Here Be Zero Divisors" beyond O
    ax.text(14, 1.5, '~~ Here Be Zero Divisors ~~', fontsize=14, ha='center',
            color=ACCENT1, fontweight='bold', fontstyle='italic',
            path_effects=[pe.withStroke(linewidth=2, foreground='white')])

    # Sea monsters (text-based)
    ax.text(15.5, 2.8, '~~~', fontsize=18, ha='center', color='#666', zorder=3,
            fontfamily='serif', fontstyle='italic')
    ax.text(15.5, 2.2, 'serpens', fontsize=9, ha='center', color='#888',
            fontstyle='italic', fontfamily='serif', zorder=3)
    ax.text(12.5, 1.3, '~~~', fontsize=14, ha='center', color='#666', zorder=3,
            fontfamily='serif', fontstyle='italic')
    ax.text(12.5, 0.8, 'monstrum', fontsize=9, ha='center', color='#888',
            fontstyle='italic', fontfamily='serif', zorder=3)

    # Faint distant islands
    for dx, label in [(2, r'$\mathbb{S}_{32}$'), (3.5, r'$\mathbb{S}_{64}$')]:
        ax.text(14 + dx, 8, label, fontsize=10, ha='center', color='#999', alpha=0.5)
        circle = plt.Circle((14 + dx, 8), 0.5, facecolor='#ddd', edgecolor='#999',
                             linewidth=1, alpha=0.3, zorder=1)
        ax.add_patch(circle)

    ax.set_xlim(-1, 19)
    ax.set_ylim(-0.5, 10.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('The Cayley–Dickson Archipelago', fontsize=20,
                 fontweight='bold', color=DARK, pad=15,
                 fontfamily='serif')
    save(fig, 'fig15_cayley_dickson_map.png')


# ============================================================
# ILLUSTRATION 16: Historical Timeline
# ============================================================
def fig16_timeline():
    fig, ax = plt.subplots(1, 1, figsize=(18, 6))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    events = [
        (628,  "Brahmagupta's\nIdentity", ACCENT2),
        (1225, "Fibonacci's\nLiber Quadratorum", ACCENT3),
        (1748, "Euler's Four-\nSquare Identity", ACCENT5),
        (1834, "Jacobi's\nFormula", GOLD),
        (1843, "Hamilton's\nQuaternions", ACCENT1),
        (1845, "Graves/Cayley's\nOctonions", ACCENT4),
        (1898, "Hurwitz's\nTheorem", SLATE),
        (1959, "Bott\nPeriodicity", '#555'),
        (2000, "String Theory\n& Standard Model", '#888'),
    ]

    # Normalize years to x-axis
    min_yr = 550
    max_yr = 2050
    def yr_to_x(yr):
        return 1 + (yr - min_yr) / (max_yr - min_yr) * 16

    # Timeline
    ax.plot([yr_to_x(min_yr), yr_to_x(max_yr)], [2.5, 2.5], color=DARK, linewidth=3)

    for i, (year, label, color) in enumerate(events):
        x = yr_to_x(year)
        # Alternate above/below
        if i % 2 == 0:
            y_text = 4.0
            y_line_end = 3.0
        else:
            y_text = 1.0
            y_line_end = 2.0

        # Vertical line to timeline
        ax.plot([x, x], [2.5, y_line_end], color=color, linewidth=2)

        # Dot on timeline
        ax.plot(x, 2.5, 'o', color=color, markersize=10, markeredgecolor=DARK,
                markeredgewidth=1.5, zorder=5)

        # Label
        ax.text(x, y_text, f'{label}\n({year})', fontsize=9, ha='center', va='center',
                color=color, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=color,
                          linewidth=1.5, alpha=0.9))

    ax.set_xlim(0, 18)
    ax.set_ylim(-0.5, 5.5)
    ax.axis('off')
    ax.set_title('A Timeline of Composition Algebras', fontsize=18,
                 fontweight='bold', color=DARK, pad=15)
    save(fig, 'fig16_timeline.png')


# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    print("Generating Chapter 9 illustrations...")
    fig01_four_rung_ladder()
    fig02_multiplication_tables()
    fig03_argand_commutativity()
    fig04_brahmagupta_machine()
    fig05_quaternion_fano()
    fig06_rotation_demo()
    fig07_euler_gearbox()
    fig08_identity_comparison()
    fig09_staircase()
    fig10_magic_dimensions()
    fig11_venn_algebras()
    fig12_square_root_bandwidth()
    fig13_jacobi_divisors()
    fig14_representations_of_one()
    fig15_cayley_dickson_map()
    fig16_timeline()
    print("Done! All images saved to", OUT)

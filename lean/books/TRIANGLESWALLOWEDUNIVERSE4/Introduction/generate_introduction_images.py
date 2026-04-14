#!/usr/bin/env python3
"""Generate all illustrations for the Introduction: The Triangle That Swallowed the Universe."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe
import numpy as np
import os
from math import gcd

OUT = "images"
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
SKY_BLUE = '#87CEEB'
WARM_GOLD = '#DAA520'
SOFT_CORAL = '#F08080'
LIGHT_BLUE = '#AED6F1'
LIGHT_GREEN = '#ABEBC6'
LIGHT_RED = '#F5B7B1'
LIGHT_YELLOW = '#FFF9C4'
CREAM = '#FDF2E9'
SLATE = '#34495E'
PALE_YELLOW = '#FFFDE7'
PALE_GREEN = '#E8F5E9'

def save(fig, name, dpi=200):
    fig.savefig(f"{OUT}/{name}", dpi=dpi, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  Saved {name}")


# ============================================================
# ILLUSTRATION 1: Pythagorean theorem visual — 3-4-5 triangle
# with square grids and rearrangement arrows
# ============================================================
def fig01_pythagorean_squares():
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    fig.set_facecolor(SAND)

    # --- Left panel: Triangle with squares on each side ---
    ax = axes[0]
    ax.set_facecolor(SAND)
    ax.set_aspect('equal')

    # Triangle vertices
    A = np.array([0, 0])
    B = np.array([4, 0])
    C = np.array([0, 3])

    # Draw triangle
    tri = plt.Polygon([A, B, C], fill=False, edgecolor=DARK, linewidth=3, zorder=10)
    ax.add_patch(tri)

    # Right angle mark
    sq_size = 0.3
    ax.plot([sq_size, sq_size, 0], [0, sq_size, sq_size], color=DARK, linewidth=1.5, zorder=10)

    # --- Square on leg a=3 (left side, blue) ---
    # Build outward from the leg A-C (vertical, x=0, y from 0 to 3)
    # Outward = to the left (negative x)
    for i in range(3):
        for j in range(3):
            rect = patches.Rectangle((-3 + j, i), 1, 1,
                                     linewidth=0.8, edgecolor=DARK,
                                     facecolor=SKY_BLUE, alpha=0.7, zorder=2)
            ax.add_patch(rect)

    # --- Square on leg b=4 (bottom side, gold) ---
    # Build outward from the leg A-B (horizontal, y=0, x from 0 to 4)
    # Outward = downward (negative y)
    for i in range(4):
        for j in range(4):
            rect = patches.Rectangle((i, -4 + j), 1, 1,
                                     linewidth=0.8, edgecolor=DARK,
                                     facecolor=WARM_GOLD, alpha=0.7, zorder=2)
            ax.add_patch(rect)

    # --- Square on hypotenuse c=5 (coral) ---
    # The hypotenuse goes from B=(4,0) to C=(0,3)
    # Direction along hypotenuse: (-4,3)/5, perpendicular outward: (3,4)/5
    perp = np.array([3, 4]) / 5.0
    along = np.array([-4, 3]) / 5.0

    # Corners of the 5x5 square built outward from hypotenuse
    P1 = B  # (4, 0)
    P2 = C  # (0, 3)
    P3 = C + 5 * perp  # (0+3, 3+4) = (3, 7)
    P4 = B + 5 * perp  # (4+3, 0+4) = (7, 4)

    # Draw the rotated grid
    for i in range(5):
        for j in range(5):
            corner = B + i * along + j * perp
            square_pts = [corner, corner + along, corner + along + perp, corner + perp]
            poly = plt.Polygon(square_pts, linewidth=0.8, edgecolor=DARK,
                               facecolor=SOFT_CORAL, alpha=0.7, zorder=2)
            ax.add_patch(poly)

    # Labels
    ax.text(2, -0.6, '$b = 4$', fontsize=16, ha='center', va='top', color=DARK, fontweight='bold')
    ax.text(-0.6, 1.5, '$a = 3$', fontsize=16, ha='right', va='center', color=DARK, fontweight='bold',
            rotation=90)
    ax.text(2.5, 2.2, '$c = 5$', fontsize=16, ha='center', va='center', color=DARK, fontweight='bold',
            rotation=-36.87)

    # Area labels
    ax.text(-1.5, 1.5, '$9$', fontsize=20, ha='center', va='center', color=DARK, fontweight='bold',
            alpha=0.6)
    ax.text(2, -2, '$16$', fontsize=20, ha='center', va='center', color=DARK, fontweight='bold',
            alpha=0.6)
    ax.text(5.0, 3.5, '$25$', fontsize=22, ha='center', va='center', color=DARK, fontweight='bold',
            alpha=0.6)

    ax.set_xlim(-4.5, 8.5)
    ax.set_ylim(-5.5, 8.5)
    ax.axis('off')
    ax.set_title('$3^2 + 4^2 = 5^2$', fontsize=22, color=DARK, fontweight='bold', pad=15)

    # --- Right panel: Rearrangement / "explosion" diagram ---
    ax2 = axes[1]
    ax2.set_facecolor(SAND)
    ax2.set_aspect('equal')

    # Show the 5x5 target grid
    for i in range(5):
        for j in range(5):
            # Color: first 9 tiles blue, next 16 gold
            idx = i * 5 + j
            if idx < 9:
                color = SKY_BLUE
            else:
                color = WARM_GOLD
            rect = patches.Rectangle((i, j), 1, 1,
                                     linewidth=0.8, edgecolor=DARK,
                                     facecolor=color, alpha=0.7, zorder=2)
            ax2.add_patch(rect)

    # Outline
    outline = patches.Rectangle((0, 0), 5, 5, linewidth=3, edgecolor=SOFT_CORAL,
                                facecolor='none', zorder=5)
    ax2.add_patch(outline)

    # Labels
    ax2.text(2.5, -0.8, '$5 \\times 5 = 25$ tiles', fontsize=16, ha='center',
             color=DARK, fontweight='bold')

    # Blue label
    ax2.text(0.9, 4.2, '9 blue', fontsize=11, ha='center', color=ACCENT2, fontweight='bold',
             zorder=10)
    # Gold label
    ax2.text(3.5, 1.0, '16 gold', fontsize=11, ha='center', color='#8B6914', fontweight='bold',
             zorder=10)

    # Big equation
    ax2.text(2.5, 5.8, '$9 + 16 = 25$', fontsize=24, ha='center', va='center',
             color=DARK, fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.3', facecolor=CREAM, edgecolor=DARK, linewidth=1.5))

    # Arrow from left to right
    fig.text(0.48, 0.5, '⟹', fontsize=40, ha='center', va='center', color=DARK, fontweight='bold')

    ax2.set_xlim(-0.5, 6)
    ax2.set_ylim(-1.5, 7)
    ax2.axis('off')
    ax2.set_title('Tiles rearranged', fontsize=18, color=DARK, pad=15)

    fig.suptitle('The Pythagorean Theorem — Visual Proof with Tiles',
                 fontsize=20, color=DARK, fontweight='bold', y=0.98)

    save(fig, 'fig01_pythagorean_squares.png')


# ============================================================
# ILLUSTRATION 2: Table of first 16 primitive Pythagorean triples
# ============================================================
def fig02_primitive_triples_table():
    fig, ax = plt.subplots(figsize=(14, 10))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.axis('off')

    # Data: (a, b, c, m, n)
    triples = [
        (3, 4, 5, 2, 1),
        (5, 12, 13, 3, 2),
        (8, 15, 17, 4, 1),     # note: a=m²-n²=15, b=2mn=8 → swap so a odd: (15,8,17)→ but list says (8,15,17)
        (7, 24, 25, 4, 3),
        (20, 21, 29, 5, 2),
        (9, 40, 41, 5, 4),     # a=m²-n²=9, b=2mn=40
        (12, 35, 37, 6, 1),
        (11, 60, 61, 6, 5),
        (13, 84, 85, 7, 6),
        (28, 45, 53, 7, 2),
        (33, 56, 65, 7, 4),
        (36, 77, 85, 9, 2),
        (20, 99, 101, 10, 1),
        (48, 55, 73, 8, 3),    # a=m²-n²=55, b=2mn=48
        (39, 80, 89, 8, 5),
        (65, 72, 97, 9, 4),
    ]

    # Recompute m,n properly for each triple where a is odd, b even
    def find_mn(a, b, c):
        """Find m,n such that a=m²-n², b=2mn, c=m²+n² (with a odd, b even)."""
        if a % 2 == 0:
            a, b = b, a  # swap so a is odd
        # c = m²+n², a = m²-n² → m² = (c+a)/2, n² = (c-a)/2
        m2 = (c + a) // 2
        n2 = (c - a) // 2
        m = int(round(m2**0.5))
        n = int(round(n2**0.5))
        return m, n

    # Headers
    col_x = [1.5, 4.5, 7.0, 9.5]
    header_y = 9.5

    headers = ['$(a, b, c)$', '$(m, n)$', '$c - b$', '$c - a$']
    for x, h in zip(col_x, headers):
        ax.text(x, header_y, h, fontsize=15, ha='center', va='center',
                fontweight='bold', color=DARK,
                bbox=dict(boxstyle='round,pad=0.2', facecolor=CREAM, edgecolor=DARK))

    # Draw rows
    for idx, (a, b, c, m, n) in enumerate(triples):
        y = header_y - 0.55 * (idx + 1)

        # Alternate row background
        if idx % 2 == 0:
            rect = patches.FancyBboxPatch((0.2, y - 0.22), 10.6, 0.5,
                                          boxstyle='round,pad=0.05',
                                          facecolor=CREAM, edgecolor='none', alpha=0.5)
            ax.add_patch(rect)

        # Triple
        ax.text(col_x[0], y, f'$({a},\\, {b},\\, {c})$',
                fontsize=12, ha='center', va='center', color=DARK)

        # (m, n) — recompute properly
        m_act, n_act = find_mn(a, b, c)
        ax.text(col_x[1], y, f'$({m_act},\\, {n_act})$',
                fontsize=12, ha='center', va='center', color=DARK)

        # c - b (highlighted yellow)
        cb = c - b
        ax.text(col_x[2], y, f'${cb}$',
                fontsize=12, ha='center', va='center', color=DARK,
                bbox=dict(boxstyle='round,pad=0.15', facecolor=PALE_YELLOW,
                          edgecolor='none', alpha=0.8))

        # c - a (highlighted green)
        ca = c - a
        ax.text(col_x[3], y, f'${ca}$',
                fontsize=12, ha='center', va='center', color=DARK,
                bbox=dict(boxstyle='round,pad=0.15', facecolor=PALE_GREEN,
                          edgecolor='none', alpha=0.8))

    # Bottom note
    bottom_y = header_y - 0.55 * 17
    ax.text(5.5, bottom_y, '"Notice anything about the $c - b$ column?"',
            fontsize=13, ha='center', va='center', color=ACCENT1, style='italic')

    # Title
    ax.set_xlim(0, 11)
    ax.set_ylim(bottom_y - 0.5, header_y + 0.8)
    ax.set_title('The First Sixteen Primitive Pythagorean Triples ($c < 100$)',
                 fontsize=18, color=DARK, fontweight='bold', pad=15)

    save(fig, 'fig02_primitive_triples_table.png')


# ============================================================
# ILLUSTRATION 3: Whimsical bathroom scene with Pythagorean
# tiles and thought bubble containing tree
# ============================================================
def fig03_bathroom_scene():
    fig, ax = plt.subplots(figsize=(14, 10))
    fig.set_facecolor('#E8E8E8')  # light gray bathroom
    ax.set_facecolor('#F0F0F0')
    ax.set_aspect('equal')

    # --- Bathroom floor tiles (white grid) ---
    for i in range(-2, 16):
        for j in range(-2, 10):
            rect = patches.Rectangle((i, j), 1, 1,
                                     linewidth=0.3, edgecolor='#CCCCCC',
                                     facecolor='white', zorder=1)
            ax.add_patch(rect)

    # --- Colored tile regions forming Pythagorean diagram ---
    # 3x3 blue square
    for i in range(3):
        for j in range(3):
            rect = patches.Rectangle((1 + i, 1 + j), 1, 1,
                                     linewidth=1, edgecolor=DARK,
                                     facecolor=SKY_BLUE, alpha=0.8, zorder=3)
            ax.add_patch(rect)

    # 4x4 gold square
    for i in range(4):
        for j in range(4):
            rect = patches.Rectangle((4 + i, 1 + j), 1, 1,
                                     linewidth=1, edgecolor=DARK,
                                     facecolor=WARM_GOLD, alpha=0.8, zorder=3)
            ax.add_patch(rect)

    # 5x5 coral square (above, representing hypotenuse square)
    for i in range(5):
        for j in range(5):
            rect = patches.Rectangle((2 + i, 5 + j), 1, 1,
                                     linewidth=1, edgecolor=DARK,
                                     facecolor=SOFT_CORAL, alpha=0.8, zorder=3)
            ax.add_patch(rect)

    # Labels on squares
    ax.text(2.5, 2.5, '$3^2 = 9$', fontsize=14, ha='center', va='center',
            color=DARK, fontweight='bold', zorder=5)
    ax.text(6, 3, '$4^2 = 16$', fontsize=14, ha='center', va='center',
            color=DARK, fontweight='bold', zorder=5)
    ax.text(4.5, 7.5, '$5^2 = 25$', fontsize=16, ha='center', va='center',
            color=DARK, fontweight='bold', zorder=5)

    # Plus and equals signs
    ax.text(3.7, 2.5, '$+$', fontsize=20, ha='center', va='center',
            color=ACCENT1, fontweight='bold', zorder=5)
    ax.text(4.5, 4.7, '$=$', fontsize=20, ha='center', va='center',
            color=ACCENT1, fontweight='bold', zorder=5)

    # --- Person sitting (simplified stick figure on right side) ---
    # Bathtub outline
    tub_x = [10, 10, 14, 14, 10]
    tub_y = [1, 5, 5, 1, 1]
    ax.plot(tub_x, tub_y, color=ACCENT2, linewidth=3, zorder=6)
    ax.fill_between([10, 14], [1, 1], [3.5, 3.5], color=LIGHT_BLUE, alpha=0.4, zorder=5)

    # Water overflow drips
    for dx in [0.2, 0.5, 0.9]:
        ax.plot([14 + dx, 14 + dx], [1.5 - dx, 1], color=ACCENT2, linewidth=2, alpha=0.5, zorder=5)

    # Stick figure sitting on tub edge
    # Head
    head = plt.Circle((10, 6.5), 0.5, facecolor=SAND, edgecolor=DARK, linewidth=2, zorder=8)
    ax.add_patch(head)
    # Body
    ax.plot([10, 10], [6, 5], color=DARK, linewidth=3, zorder=7)
    # Legs
    ax.plot([10, 10.5], [5, 4], color=DARK, linewidth=3, zorder=7)
    ax.plot([10, 9.5], [5, 4], color=DARK, linewidth=3, zorder=7)
    # Arms
    ax.plot([10, 9, 8.5], [5.5, 5.8, 5.5], color=DARK, linewidth=2, zorder=7)
    ax.plot([10, 11], [5.5, 5], color=DARK, linewidth=2, zorder=7)

    # --- Thought bubble with branching tree ---
    # Bubble
    bubble = patches.FancyBboxPatch((5.5, 10.5), 8, 5,
                                     boxstyle='round,pad=0.5',
                                     facecolor='white', edgecolor=DARK,
                                     linewidth=2, alpha=0.9, zorder=9)
    ax.add_patch(bubble)

    # Small bubbles leading to thought
    for cx, cy, r in [(10.2, 8.5, 0.15), (10.0, 9.2, 0.2), (9.7, 10.0, 0.25)]:
        circ = plt.Circle((cx, cy), r, facecolor='white', edgecolor=DARK,
                          linewidth=1.5, zorder=9)
        ax.add_patch(circ)

    # Tree inside thought bubble
    def draw_tree_node(x, y, label, color, size=8):
        ax.text(x, y, label, fontsize=size, ha='center', va='center',
                color=DARK, fontweight='bold', zorder=12,
                bbox=dict(boxstyle='round,pad=0.2', facecolor=color,
                          edgecolor=DARK, linewidth=1, alpha=0.8))

    def draw_edge(x1, y1, x2, y2):
        ax.plot([x1, x2], [y1, y2], color=DARK, linewidth=1.5, zorder=10)

    # Root
    root_x, root_y = 9.5, 14.5
    draw_tree_node(root_x, root_y, '(3,4,5)', LIGHT_BLUE, 9)

    # Level 1
    children1 = [(7, 13), (9.5, 13), (12, 13)]
    labels1 = ['(5,12,13)', '(21,20,29)', '(15,8,17)']
    colors1 = [LIGHT_BLUE, LIGHT_RED, LIGHT_GREEN]
    for (cx, cy), label, color in zip(children1, labels1, colors1):
        draw_edge(root_x, root_y - 0.3, cx, cy + 0.3)
        draw_tree_node(cx, cy, label, color, 7)

    # Level 2 (just hints fading out)
    level2_positions = [
        (6, 12), (7, 11.5), (8, 12),
        (9, 11.5), (9.5, 12), (10, 11.5),
        (11, 12), (12, 11.5), (13, 12),
    ]
    for i, (px, py) in enumerate(level2_positions):
        parent = children1[i // 3]
        draw_edge(parent[0], parent[1] - 0.3, px, py + 0.15)
        ax.text(px, py, '···', fontsize=8, ha='center', va='center',
                color=SLATE, alpha=0.6, zorder=12)

    # "Fading into infinity" text
    ax.text(9.5, 11, '∞', fontsize=24, ha='center', va='center',
            color=ACCENT4, alpha=0.4, zorder=12)

    # --- Plimpton 322 tablet on windowsill ---
    # Windowsill
    ax.fill_between([0, 3], [9.5, 9.5], [10, 10], color='#8B7355', zorder=6)
    ax.plot([0, 3], [10, 10], color=DARK, linewidth=2, zorder=7)

    # Tablet
    tablet = patches.FancyBboxPatch((0.5, 10.1), 2, 1.5,
                                     boxstyle='round,pad=0.1',
                                     facecolor='#C4A882', edgecolor='#8B6914',
                                     linewidth=2, zorder=8)
    ax.add_patch(tablet)

    # Cuneiform-like marks
    for tx in np.linspace(0.8, 2.2, 5):
        for ty in np.linspace(10.4, 11.3, 4):
            mark = np.random.choice(['▽', '◁', '△', '▷', '|', '<', '∧', '⊏'])
            ax.text(tx, ty, mark, fontsize=6, ha='center', va='center',
                    color='#5C4033', zorder=9, alpha=0.7)

    ax.text(1.5, 9.2, 'Plimpton 322\nc. 1800 BCE', fontsize=8, ha='center',
            va='top', color=DARK, style='italic', zorder=7)

    # --- Rubber duck ---
    duck = plt.Circle((13, 4.5), 0.3, facecolor='#FFD700', edgecolor=DARK,
                       linewidth=1.5, zorder=8)
    ax.add_patch(duck)
    # Duck head
    duck_head = plt.Circle((13.25, 4.9), 0.15, facecolor='#FFD700', edgecolor=DARK,
                            linewidth=1, zorder=8)
    ax.add_patch(duck_head)
    # Beak
    ax.plot([13.35, 13.55, 13.35], [4.95, 4.9, 4.85], color=ACCENT5, linewidth=2, zorder=9)
    # Eye
    ax.plot(13.28, 4.95, 'o', color=DARK, markersize=2, zorder=9)

    ax.set_xlim(-1, 15.5)
    ax.set_ylim(-0.5, 16.5)
    ax.axis('off')

    fig.suptitle('The Puzzle on the Bathroom Tiles',
                 fontsize=22, color=DARK, fontweight='bold', y=0.98)

    save(fig, 'fig03_bathroom_scene.png')


# ============================================================
# Run all figure generators
# ============================================================
if __name__ == '__main__':
    print("Generating Introduction illustrations...")
    print()

    print("[1/3] Pythagorean squares diagram...")
    fig01_pythagorean_squares()

    print("[2/3] Primitive triples table...")
    fig02_primitive_triples_table()

    print("[3/3] Bathroom scene...")
    fig03_bathroom_scene()

    print()
    print("All Introduction illustrations generated successfully!")

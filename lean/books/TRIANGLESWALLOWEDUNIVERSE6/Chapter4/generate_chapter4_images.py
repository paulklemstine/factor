#!/usr/bin/env python3
"""Generate all illustrations for Chapter 4: Three Roads from Pythagoras."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe
import numpy as np
import os
from math import gcd, sqrt

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
os.makedirs(OUT, exist_ok=True)

# Color palette (matching earlier chapters)
SAND = '#F5E6C8'
DARK = '#2C1810'
ACCENT1 = '#C0392B'  # red
ACCENT2 = '#2980B9'  # blue
ACCENT3 = '#27AE60'  # green
ACCENT4 = '#8E44AD'  # purple
ACCENT5 = '#E67E22'  # orange/amber
GOLD = '#D4A017'
LIGHT_BLUE = '#AED6F1'
LIGHT_GREEN = '#ABEBC6'
LIGHT_RED = '#F5B7B1'
CREAM = '#FDF2E9'
SLATE = '#34495E'
GLOW = '#F4D03F'
AMBER = '#D4890A'
COOL_BLUE = '#5DADE2'


def save(fig, name, dpi=200):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=dpi, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  Saved {name}")


# ============================================================
# FIG 1: 13x5 rectangle — two sum-of-squares decompositions of 65
# ============================================================
def fig01_rectangle_dissection():
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.set_facecolor(SAND)

    for idx, ax in enumerate(axes):
        ax.set_facecolor(SAND)
        # Draw the 13x5 grid
        for i in range(14):
            ax.plot([i, i], [0, 5], color=DARK, linewidth=0.3, alpha=0.3)
        for j in range(6):
            ax.plot([0, 13], [j, j], color=DARK, linewidth=0.3, alpha=0.3)
        ax.plot([0, 13, 13, 0, 0], [0, 0, 5, 5, 0], color=DARK, linewidth=2)

        if idx == 0:
            # 1^2 + 8^2 = 65: highlight 1x1 and 8x8 regions
            r1 = patches.Rectangle((0, 0), 1, 1, facecolor=AMBER, alpha=0.4, edgecolor=AMBER, linewidth=2)
            ax.add_patch(r1)
            r2 = patches.Rectangle((0, 0), 8, 8, facecolor=COOL_BLUE, alpha=0.15, edgecolor=COOL_BLUE,
                                   linewidth=2, linestyle='--')
            ax.add_patch(r2)
            ax.text(0.5, 0.5, '$1^2$', fontsize=11, ha='center', va='center', color=DARK, fontweight='bold')
            ax.text(4, 4, '$8^2 = 64$', fontsize=14, ha='center', va='center', color=ACCENT2, fontweight='bold')
            ax.set_title('$65 = 1^2 + 8^2$', fontsize=16, color=DARK, fontweight='bold', pad=10)
            # show squares as side annotations
            ax.annotate('', xy=(8, -0.3), xytext=(0, -0.3),
                        arrowprops=dict(arrowstyle='<->', color=ACCENT2, lw=1.5))
            ax.text(4, -0.7, '8', fontsize=12, ha='center', color=ACCENT2, fontweight='bold')
        else:
            # 4^2 + 7^2 = 65: highlight 4x4 and 7x7 regions
            r1 = patches.Rectangle((0, 0), 4, 4, facecolor=AMBER, alpha=0.4, edgecolor=AMBER, linewidth=2)
            ax.add_patch(r1)
            r2 = patches.Rectangle((0, 0), 7, 7, facecolor=COOL_BLUE, alpha=0.15, edgecolor=COOL_BLUE,
                                   linewidth=2, linestyle='--')
            ax.add_patch(r2)
            ax.text(2, 2, '$4^2 = 16$', fontsize=12, ha='center', va='center', color=DARK, fontweight='bold')
            ax.text(3.5, 5.5, '$7^2 = 49$', fontsize=14, ha='center', va='center', color=ACCENT2, fontweight='bold')
            ax.set_title('$65 = 4^2 + 7^2$', fontsize=16, color=DARK, fontweight='bold', pad=10)
            ax.annotate('', xy=(7, -0.3), xytext=(0, -0.3),
                        arrowprops=dict(arrowstyle='<->', color=ACCENT2, lw=1.5))
            ax.text(3.5, -0.7, '7', fontsize=12, ha='center', color=ACCENT2, fontweight='bold')
            ax.annotate('', xy=(-0.3, 4), xytext=(-0.3, 0),
                        arrowprops=dict(arrowstyle='<->', color=AMBER, lw=1.5))
            ax.text(-0.8, 2, '4', fontsize=12, ha='center', color=AMBER, fontweight='bold')

        ax.set_xlim(-1.5, 14)
        ax.set_ylim(-1.5, 9)
        ax.set_aspect('equal')
        ax.axis('off')

    fig.suptitle('Two Sum-of-Squares Decompositions of 65', fontsize=18, color=DARK,
                 fontweight='bold', y=1.02)
    save(fig, "fig01_rectangle_dissection.png")


# ============================================================
# FIG 2: Gaussian integer lattice
# ============================================================
def fig02_gaussian_lattice():
    fig, ax = plt.subplots(1, 1, figsize=(12, 12))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    # Draw lattice points
    rng = 9
    for x in range(-rng, rng + 1):
        for y in range(-rng, rng + 1):
            ax.plot(x, y, '.', color=SLATE, markersize=2, alpha=0.3)

    # Draw circles for |z|^2 = 5, 13, 65
    for r2, col, lbl in [(5, ACCENT5, '$|z|^2=5$'), (13, ACCENT1, '$|z|^2=13$'), (65, ACCENT4, '$|z|^2=65$')]:
        theta = np.linspace(0, 2 * np.pi, 200)
        r = np.sqrt(r2)
        ax.plot(r * np.cos(theta), r * np.sin(theta), color=col, linewidth=1.5, alpha=0.6, linestyle='--')
        ax.text(r * 0.71 + 0.3, r * 0.71 + 0.3, lbl, fontsize=10, color=col, fontweight='bold')

    # Points on |z|^2 = 5
    pts5 = [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]
    for p in pts5:
        ax.plot(*p, 'o', color=ACCENT5, markersize=7, markeredgecolor=DARK, markeredgewidth=0.5)

    # Points on |z|^2 = 13
    pts13 = [(2, 3), (3, 2), (-2, 3), (-3, 2), (2, -3), (3, -2), (-2, -3), (-3, -2)]
    for p in pts13:
        ax.plot(*p, 'o', color=ACCENT1, markersize=7, markeredgecolor=DARK, markeredgewidth=0.5)

    # Points on |z|^2 = 65
    pts65 = [(1, 8), (8, 1), (4, 7), (7, 4), (-1, 8), (-8, 1), (-4, 7), (-7, 4),
             (1, -8), (8, -1), (4, -7), (7, -4), (-1, -8), (-8, -1), (-4, -7), (-7, -4)]
    for p in pts65:
        ax.plot(*p, '*', color=ACCENT4, markersize=12, markeredgecolor=DARK, markeredgewidth=0.5)

    # Vectors: 1+2i and 2+3i
    ax.annotate('', xy=(1, 2), xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', color=ACCENT5, lw=2.5))
    ax.text(0.3, 2.3, '$1+2i$', fontsize=13, color=ACCENT5, fontweight='bold')

    ax.annotate('', xy=(2, 3), xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=2.5))
    ax.text(2.2, 3.2, '$2+3i$', fontsize=13, color=ACCENT1, fontweight='bold')

    # Product: (1+2i)(2+3i) = (2-6) + (3+4)i = -4 + 7i
    ax.annotate('', xy=(-4, 7), xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', color=ACCENT4, lw=2.5))
    ax.text(-5.5, 7.3, '$-4+7i$', fontsize=13, color=ACCENT4, fontweight='bold')

    ax.axhline(0, color=DARK, linewidth=0.5, alpha=0.3)
    ax.axvline(0, color=DARK, linewidth=0.5, alpha=0.3)
    ax.set_xlim(-9.5, 9.5)
    ax.set_ylim(-9.5, 9.5)
    ax.set_aspect('equal')
    ax.set_xlabel('Real', fontsize=14, color=DARK)
    ax.set_ylabel('Imaginary', fontsize=14, color=DARK)
    ax.set_title('Gaussian Integer Lattice $\\mathbb{Z}[i]$\nNorm Multiplicativity: $|z_1 z_2|^2 = |z_1|^2 \\cdot |z_2|^2$',
                 fontsize=16, color=DARK, fontweight='bold', pad=15)
    ax.axis('off')
    save(fig, "fig02_gaussian_lattice.png")


# ============================================================
# FIG 3: Triple Factory conveyor belt
# ============================================================
def fig03_triple_factory():
    fig, ax = plt.subplots(1, 1, figsize=(16, 8))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    # Conveyor belts (input)
    for yoff, triple, col in [(5, '(3, 4, 5)', ACCENT2), (2, '(5, 12, 13)', ACCENT1)]:
        # belt
        ax.plot([0, 5], [yoff, yoff], color=SLATE, linewidth=4, solid_capstyle='round')
        ax.plot([0, 5], [yoff - 0.3, yoff - 0.3], color=SLATE, linewidth=2, alpha=0.5)
        # rollers
        for xr in [0.5, 2, 3.5]:
            circ = plt.Circle((xr, yoff - 0.15), 0.15, color=SLATE, fill=False, linewidth=1.5)
            ax.add_patch(circ)
        # card
        card = FancyBboxPatch((1.5, yoff + 0.2), 3, 1.5, boxstyle="round,pad=0.1",
                              facecolor=CREAM, edgecolor=col, linewidth=2)
        ax.add_patch(card)
        ax.text(3, yoff + 0.95, triple, fontsize=14, ha='center', va='center',
                color=col, fontweight='bold')
        # small triangle
        if triple == '(3, 4, 5)':
            tx, ty = 3.8, yoff + 0.5
            sc = 0.15
            ax.plot([tx, tx + 4 * sc, tx, tx], [ty, ty, ty + 3 * sc, ty], color=col, linewidth=1.5)
        else:
            tx, ty = 3.8, yoff + 0.5
            sc = 0.06
            ax.plot([tx, tx + 12 * sc, tx, tx], [ty, ty, ty + 5 * sc, ty], color=col, linewidth=1.5)

    # Machine
    machine = FancyBboxPatch((5.5, 0.5), 5, 6.5, boxstyle="round,pad=0.3",
                             facecolor=SLATE, edgecolor=DARK, linewidth=3, alpha=0.85)
    ax.add_patch(machine)
    ax.text(8, 5.5, 'Brahmagupta–\nFibonacci\nComposer', fontsize=13, ha='center', va='center',
            color=GLOW, fontweight='bold')
    # gears
    for gx, gy in [(6.3, 2), (9.5, 2), (7.9, 1.2)]:
        gear = plt.Circle((gx, gy), 0.4, color=GOLD, fill=False, linewidth=2)
        ax.add_patch(gear)
        ax.plot(gx, gy, '+', color=GOLD, markersize=8, markeredgewidth=2)

    ax.text(8, 3.5, '$(ac-bd)^2+(ad+bc)^2$', fontsize=10, ha='center', va='center',
            color=CREAM, fontstyle='italic')

    # Output conveyor belts
    for yoff, triple, col in [(5, '(33, 56, 65)', ACCENT3), (2, '(16, 63, 65)', ACCENT5)]:
        ax.plot([11, 16], [yoff, yoff], color=SLATE, linewidth=4, solid_capstyle='round')
        ax.plot([11, 16], [yoff - 0.3, yoff - 0.3], color=SLATE, linewidth=2, alpha=0.5)
        for xr in [12, 13.5, 15]:
            circ = plt.Circle((xr, yoff - 0.15), 0.15, color=SLATE, fill=False, linewidth=1.5)
            ax.add_patch(circ)
        card = FancyBboxPatch((11.5, yoff + 0.2), 3.5, 1.5, boxstyle="round,pad=0.1",
                              facecolor=CREAM, edgecolor=col, linewidth=2)
        ax.add_patch(card)
        ax.text(13.25, yoff + 0.95, triple, fontsize=14, ha='center', va='center',
                color=col, fontweight='bold')

    # arrows
    for yoff in [5.5, 2.5]:
        ax.annotate('', xy=(5.5, yoff), xytext=(4.8, yoff),
                    arrowprops=dict(arrowstyle='->', color=DARK, lw=2))
        ax.annotate('', xy=(11.5, yoff), xytext=(10.7, yoff),
                    arrowprops=dict(arrowstyle='->', color=DARK, lw=2))

    ax.set_xlim(-0.5, 16.5)
    ax.set_ylim(-0.5, 8)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title("The Triple Factory", fontsize=18, color=DARK, fontweight='bold', pad=15)
    save(fig, "fig03_triple_factory.png")


# ============================================================
# FIG 4: Multiplication table of Pythagorean triples
# ============================================================
def fig04_multiplication_table():
    fig, ax = plt.subplots(1, 1, figsize=(14, 12))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25)]
    labels = ['(3,4,5)', '(5,12,13)', '(8,15,17)', '(7,24,25)']

    def compose(t1, t2):
        a1, b1, c1 = t1
        a2, b2, c2 = t2
        return (abs(a1 * a2 - b1 * b2), abs(a1 * b2 + b1 * a2), c1 * c2)

    n = len(triples)
    cell_w, cell_h = 2.8, 1.2

    # Header row and column
    for i in range(n):
        # Column headers
        hx = (i + 1) * cell_w + cell_w / 2
        hy = (n + 0.5) * cell_h
        ax.text(hx, hy, labels[i], fontsize=10, ha='center', va='center',
                color=DARK, fontweight='bold')
        # Row headers
        rx = cell_w / 2
        ry = (n - i - 0.5) * cell_h
        ax.text(rx, ry, labels[i], fontsize=10, ha='center', va='center',
                color=DARK, fontweight='bold')

    # Table cells
    for i in range(n):
        for j in range(n):
            cx = (j + 1) * cell_w
            cy = (n - i - 1) * cell_h
            is_diag = (i == j)

            bg_color = LIGHT_RED if is_diag else CREAM
            rect = patches.Rectangle((cx, cy), cell_w, cell_h,
                                     facecolor=bg_color, edgecolor=DARK, linewidth=1)
            ax.add_patch(rect)

            result = compose(triples[i], triples[j])
            txt = f'({result[0]},{result[1]},{result[2]})'
            ax.text(cx + cell_w / 2, cy + cell_h / 2, txt, fontsize=8,
                    ha='center', va='center', color=DARK)

    # Grid lines
    for i in range(n + 2):
        ax.plot([cell_w, (n + 1) * cell_w], [i * cell_h, i * cell_h], color=DARK, linewidth=0.5, alpha=0.3)
    for j in range(n + 2):
        ax.plot([j * cell_w, j * cell_w], [0, n * cell_h], color=DARK, linewidth=0.5, alpha=0.3)

    # Operator symbol
    ax.text(cell_w / 2, (n + 0.5) * cell_h, '★', fontsize=18, ha='center', va='center',
            color=ACCENT4, fontweight='bold')

    # Note
    ax.text((n + 1) * cell_w / 2 + cell_w / 2, -0.8,
            'The Pythagorean triples form a monoid — with identity element $(1, 0, 1)$.',
            fontsize=11, ha='center', va='center', color=SLATE, fontstyle='italic')

    ax.set_xlim(-0.2, (n + 1) * cell_w + 0.5)
    ax.set_ylim(-1.5, (n + 1.5) * cell_h)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title("Multiplication Table of Pythagorean Triples", fontsize=18, color=DARK,
                 fontweight='bold', pad=20)
    save(fig, "fig04_multiplication_table.png")


# ============================================================
# FIG 5: Euler's X-Ray Machine for 1105
# ============================================================
def fig05_euler_xray():
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    # Central frame with N = 1105
    frame = FancyBboxPatch((4, 3.5), 6, 3, boxstyle="round,pad=0.3",
                           facecolor=CREAM, edgecolor=GOLD, linewidth=4)
    ax.add_patch(frame)
    ax.text(7, 5, '$N = 1105$', fontsize=28, ha='center', va='center',
            color=DARK, fontweight='bold')

    # Left X-ray screen
    screen_l = FancyBboxPatch((0, 0), 5, 3), 
    rect_l = patches.Rectangle((0.3, 0.3), 4.4, 2.4, facecolor=LIGHT_BLUE,
                               edgecolor=ACCENT2, linewidth=2, alpha=0.7)
    ax.add_patch(rect_l)
    ax.text(2.5, 2.0, '$4^2 + 33^2$', fontsize=16, ha='center', va='center',
            color=ACCENT2, fontweight='bold')
    ax.text(2.5, 1.2, '$= 16 + 1089 = 1105$', fontsize=11, ha='center', va='center',
            color=SLATE)

    # Right X-ray screen
    rect_r = patches.Rectangle((9.3, 0.3), 4.4, 2.4, facecolor=LIGHT_RED,
                               edgecolor=ACCENT1, linewidth=2, alpha=0.7)
    ax.add_patch(rect_r)
    ax.text(11.5, 2.0, '$9^2 + 32^2$', fontsize=16, ha='center', va='center',
            color=ACCENT1, fontweight='bold')
    ax.text(11.5, 1.2, '$= 81 + 1024 = 1105$', fontsize=11, ha='center', va='center',
            color=SLATE)

    # Magnifying glass in center
    mg_x, mg_y = 7, 1.5
    circ = plt.Circle((mg_x, mg_y), 0.8, facecolor=GLOW, edgecolor=DARK,
                      linewidth=2, alpha=0.4)
    ax.add_patch(circ)
    ax.text(mg_x, mg_y, '$13$', fontsize=20, ha='center', va='center',
            color=ACCENT1, fontweight='bold')
    ax.plot([mg_x + 0.56, mg_x + 1.2], [mg_y - 0.56, mg_y - 1.2],
            color=DARK, linewidth=3)

    # Dotted lines connecting screens through magnifying glass
    ax.plot([4.7, mg_x - 0.7], [1.5, 1.5], color=ACCENT4, linewidth=1.5, linestyle=':')
    ax.plot([mg_x + 0.7, 9.3], [1.5, 1.5], color=ACCENT4, linewidth=1.5, linestyle=':')

    # Arithmetic below
    ax.text(7, -0.5, '$\\gcd(33+32,\\, 9+4) = \\gcd(65,\\, 13) = 13$',
            fontsize=13, ha='center', va='center', color=ACCENT3, fontweight='bold')
    ax.text(7, -1.2, '$1105 \\div 13 = 85 = 5 \\times 17$',
            fontsize=13, ha='center', va='center', color=SLATE)

    ax.set_xlim(-0.5, 14.5)
    ax.set_ylim(-2, 7.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title("Euler's X-Ray Machine", fontsize=20, color=DARK, fontweight='bold', pad=15)
    save(fig, "fig05_euler_xray.png")


# ============================================================
# FIG 6: Portrait of Euler at his desk
# ============================================================
def fig06_euler_portrait():
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    # Desk
    desk = patches.Rectangle((1, 0.5), 10, 3, facecolor='#8B6914', edgecolor=DARK,
                              linewidth=2, alpha=0.7)
    ax.add_patch(desk)

    # Paper on desk
    paper = patches.Rectangle((2, 1), 4, 2.2, facecolor='white', edgecolor=SLATE,
                               linewidth=1, alpha=0.9)
    ax.add_patch(paper)
    ax.text(4, 2.7, '$1105 = 4^2 + 33^2$', fontsize=10, ha='center', color=DARK)
    ax.text(4, 2.2, '$1105 = 9^2 + 32^2$', fontsize=10, ha='center', color=DARK)
    ax.text(4, 1.5, '$\\Rightarrow 13$', fontsize=14, ha='center', color=ACCENT1,
            fontweight='bold')
    # circle around 13
    circ = plt.Circle((4, 1.5), 0.35, facecolor='none', edgecolor=ACCENT1,
                      linewidth=2, linestyle='-')
    ax.add_patch(circ)

    # Quill
    ax.plot([6.5, 7.5], [2.5, 4.5], color=DARK, linewidth=2)
    ax.plot([6.5, 6.3], [2.5, 2.2], color=DARK, linewidth=1)
    # feather
    from matplotlib.patches import Polygon
    feather = Polygon([(7.5, 4.5), (7.8, 5.5), (7.2, 5.3), (7.5, 4.5)],
                      facecolor=CREAM, edgecolor=DARK, linewidth=1)
    ax.add_patch(feather)

    # Thought bubble
    bubble = plt.Circle((8, 7.5), 1.8, facecolor=CREAM, edgecolor=SLATE,
                        linewidth=2, alpha=0.9)
    ax.add_patch(bubble)
    # small bubbles leading up
    for bx, by, br in [(7.2, 5.5, 0.15), (7.5, 6.0, 0.2), (7.7, 6.5, 0.25)]:
        b = plt.Circle((bx, by), br, facecolor=CREAM, edgecolor=SLATE, linewidth=1)
        ax.add_patch(b)
    ax.text(8, 7.5, '$(a-c)(a+c)$\n$= (d-b)(d+b)$', fontsize=12,
            ha='center', va='center', color=ACCENT4, fontweight='bold')

    # Simple figure (head)
    head = plt.Circle((7, 5), 0.5, facecolor=SAND, edgecolor=DARK, linewidth=2)
    ax.add_patch(head)
    # body
    ax.plot([7, 7], [4.5, 3.5], color=DARK, linewidth=3)
    ax.plot([7, 6.2], [4, 3.5], color=DARK, linewidth=2)  # left arm
    ax.plot([7, 6.5], [3.5, 2.5], color=DARK, linewidth=2)  # reaching to quill
    # eye (one clouded)
    ax.plot(6.85, 5.1, '.', color=DARK, markersize=5)
    ax.plot(7.15, 5.1, '.', color=SLATE, markersize=5, alpha=0.4)  # clouded eye

    # Window with spires
    win = patches.Rectangle((9.5, 4), 2, 3, facecolor=LIGHT_BLUE, edgecolor=DARK, linewidth=2)
    ax.add_patch(win)
    ax.plot([10.5, 10.5], [4, 7], color=DARK, linewidth=1)
    ax.plot([9.5, 11.5], [5.5, 5.5], color=DARK, linewidth=1)
    # spires
    for sx in [10, 10.5, 11]:
        ax.plot([sx, sx], [6, 6.5 + 0.3 * (sx == 10.5)], color=SLATE, linewidth=1.5)
        ax.plot([sx - 0.1, sx, sx + 0.1], [6.5 + 0.3 * (sx == 10.5)] * 3,
                color=SLATE, linewidth=1)
        ax.plot(sx, 6.5 + 0.3 * (sx == 10.5) + 0.15, '^', color=SLATE, markersize=4)

    ax.set_xlim(0, 12.5)
    ax.set_ylim(0, 10)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title("Euler and the Two Portraits of 1105", fontsize=18, color=DARK,
                 fontweight='bold', pad=15)
    save(fig, "fig06_euler_portrait.png")


# ============================================================
# FIG 7: Pythagorean cone 3D with Berggren arrows
# ============================================================
def fig07_pythagorean_cone():
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    # Cone surface
    theta = np.linspace(0, 2 * np.pi, 100)
    z = np.linspace(0, 35, 50)
    Theta, Z = np.meshgrid(theta, z)
    X = Z * np.cos(Theta)
    Y = Z * np.sin(Theta)
    ax.plot_surface(X, Y, Z, alpha=0.08, color=ACCENT2)

    # Pythagorean triples as points
    pts = [(3, 4, 5), (5, 12, 13), (21, 20, 29), (15, 8, 17)]
    colors_pts = [ACCENT1, ACCENT2, ACCENT1, ACCENT3]
    for (a, b, c), col in zip(pts, colors_pts):
        ax.scatter([a], [b], [c], color=col, s=80, edgecolors=DARK, zorder=10)
        ax.text(a + 0.5, b + 0.5, c + 0.5, f'({a},{b},{c})', fontsize=9, color=DARK)

    # Arrows from (3,4,5) to children
    root = np.array([3, 4, 5])
    children = [(5, 12, 13, ACCENT2, '$B_1$'), (21, 20, 29, ACCENT1, '$B_2$'), (15, 8, 17, ACCENT3, '$B_3$')]
    for (a, b, c, col, lbl) in children:
        child = np.array([a, b, c])
        ax.plot([root[0], child[0]], [root[1], child[1]], [root[2], child[2]],
                color=col, linewidth=2.5, alpha=0.8)
        mid = (root + child) / 2
        ax.text(mid[0] - 1, mid[1], mid[2], lbl, fontsize=11, color=col, fontweight='bold')

    ax.set_xlabel('a', fontsize=12)
    ax.set_ylabel('b', fontsize=12)
    ax.set_zlabel('c', fontsize=12)
    ax.set_title('Pythagorean Cone $a^2 + b^2 = c^2$\nBerggren Transformations', fontsize=16,
                 color=DARK, fontweight='bold')
    ax.view_init(elev=20, azim=35)
    save(fig, "fig07_pythagorean_cone.png")


# ============================================================
# FIG 8: Light cone vs Pythagorean cone side-by-side
# ============================================================
def fig08_light_cones():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    fig.set_facecolor(SAND)

    for ax in (ax1, ax2):
        ax.set_facecolor(SAND)

    # LEFT: Relativistic light cone
    # Draw cone outlines
    t = np.linspace(-5, 5, 100)
    ax1.plot(t, np.abs(t), color=ACCENT1, linewidth=2)
    ax1.plot(t, -np.abs(t), color=ACCENT1, linewidth=2, alpha=0.3)
    ax1.fill_between(t, np.abs(t), 6, alpha=0.1, color=ACCENT1)
    ax1.fill_between(t, -np.abs(t), -6, alpha=0.05, color=ACCENT1)

    ax1.text(0, 4.5, 'Future', fontsize=14, ha='center', color=ACCENT1, fontweight='bold')
    ax1.text(0, -4.5, 'Past', fontsize=14, ha='center', color=ACCENT1, fontweight='bold', alpha=0.5)
    ax1.text(4, 2, 'Elsewhere', fontsize=12, ha='center', color=SLATE, fontstyle='italic')
    ax1.text(-4, 2, 'Elsewhere', fontsize=12, ha='center', color=SLATE, fontstyle='italic')

    # photon worldline
    ax1.plot([0, 4], [0, 4], color=GLOW, linewidth=2, linestyle='--')
    ax1.text(3, 4.3, 'photon', fontsize=10, color=GOLD, fontstyle='italic')

    ax1.axhline(0, color=DARK, linewidth=0.5, alpha=0.3)
    ax1.axvline(0, color=DARK, linewidth=0.5, alpha=0.3)
    ax1.set_xlabel('Space ($x$)', fontsize=12, color=DARK)
    ax1.set_ylabel('Time ($t$)', fontsize=12, color=DARK)
    ax1.set_title('Relativistic Light Cone\n$x^2 + y^2 - t^2 = 0$', fontsize=14,
                  color=DARK, fontweight='bold')
    ax1.set_xlim(-6, 6)
    ax1.set_ylim(-6, 6)
    ax1.set_aspect('equal')

    # RIGHT: Pythagorean cone with integer points
    t2 = np.linspace(-30, 30, 200)
    ax2.plot(t2, np.abs(t2), color=ACCENT2, linewidth=2)
    ax2.fill_between(t2, np.abs(t2), 40, alpha=0.05, color=ACCENT2)

    # Plot Pythagorean triples as points on the cone
    pyth_triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25), (20, 21, 29),
                    (9, 40, 41), (12, 35, 37), (15, 8, 17)]
    for a, b, c in pyth_triples:
        # Plot at (a, c) — using one leg as x-axis, hypotenuse as y
        ax2.plot(a, c, 'o', color=GLOW, markersize=10, markeredgecolor=DARK,
                 markeredgewidth=1, zorder=5)
        ax2.text(a + 0.5, c + 0.5, f'({a},{b},{c})', fontsize=7, color=DARK)
        # mirror
        ax2.plot(-a, c, 'o', color=GLOW, markersize=6, markeredgecolor=DARK,
                 markeredgewidth=0.5, zorder=5, alpha=0.4)

    ax2.axhline(0, color=DARK, linewidth=0.5, alpha=0.3)
    ax2.axvline(0, color=DARK, linewidth=0.5, alpha=0.3)
    ax2.set_xlabel('Leg $a$', fontsize=12, color=DARK)
    ax2.set_ylabel('Hypotenuse $c$', fontsize=12, color=DARK)
    ax2.set_title('Pythagorean Cone\n$a^2 + b^2 = c^2$', fontsize=14,
                  color=DARK, fontweight='bold')
    ax2.set_xlim(-30, 30)
    ax2.set_ylim(-5, 45)

    # Bridge label
    fig.text(0.5, 0.02, '$Q = x^2 + y^2 - z^2 = 0$  —  Same equation, different worlds.',
             fontsize=14, ha='center', color=ACCENT4, fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.5', facecolor=CREAM, edgecolor=ACCENT4, linewidth=2))

    plt.tight_layout()
    save(fig, "fig08_light_cones.png")


# ============================================================
# FIG 9: Berggren tree — 3 levels deep
# ============================================================
def fig09_berggren_tree():
    fig, ax = plt.subplots(1, 1, figsize=(20, 12))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    B1 = np.array([[1, -2, 2], [2, -1, 2], [2, -2, 3]])
    B2 = np.array([[1, 2, 2], [2, 1, 2], [2, 2, 3]])
    B3 = np.array([[-1, 2, 2], [-2, 1, 2], [-2, 2, 3]])

    matrices = [B1, B2, B3]
    branch_colors = [ACCENT2, ACCENT1, ACCENT3]
    branch_labels = ['$B_1$', '$B_2$', '$B_3$']

    root = np.array([3, 4, 5])

    def triple_str(t):
        return f'({t[0]},{t[1]},{t[2]})'

    def draw_triangle(ax, cx, cy, a, b, c, scale=0.008):
        s = scale
        ax.plot([cx - b * s / 2, cx + b * s / 2, cx - b * s / 2, cx - b * s / 2],
                [cy - 0.4, cy - 0.4, cy - 0.4 + a * s, cy - 0.4],
                color=DARK, linewidth=1, alpha=0.5)

    # Level 0 position
    positions = {}
    root_pos = (10, 10)
    positions[(0, 0)] = (root_pos, root)

    ax.text(root_pos[0], root_pos[1], triple_str(root), fontsize=13,
            ha='center', va='center', color=DARK, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=CREAM, edgecolor=DARK, linewidth=2))
    draw_triangle(ax, root_pos[0], root_pos[1], 3, 4, 5, 0.04)

    # Level 1
    l1_y = 7
    l1_xs = [3, 10, 17]
    for i, (M, col, lbl) in enumerate(zip(matrices, branch_colors, branch_labels)):
        child = M @ root
        child = np.abs(child)
        pos = (l1_xs[i], l1_y)
        positions[(1, i)] = (pos, child)

        # branch line
        ax.plot([root_pos[0], pos[0]], [root_pos[1] - 0.5, pos[1] + 0.6],
                color=col, linewidth=2.5, alpha=0.8)
        ax.text((root_pos[0] + pos[0]) / 2 + (-0.8 if i == 0 else 0.8 if i == 2 else 0),
                (root_pos[1] + pos[1]) / 2, lbl, fontsize=11, color=col, fontweight='bold')

        ax.text(pos[0], pos[1], triple_str(child), fontsize=11,
                ha='center', va='center', color=DARK, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor=CREAM, edgecolor=col, linewidth=2))
        draw_triangle(ax, pos[0], pos[1], child[0], child[1], child[2], 0.012)

    # Level 2
    l2_y = 3.5
    l2_positions = []
    spread = 1.8
    for pi in range(3):
        parent_pos, parent_triple = positions[(1, pi)]
        base_x = parent_pos[0]
        for ci, (M, col, lbl) in enumerate(zip(matrices, branch_colors, branch_labels)):
            child = M @ parent_triple
            child = np.abs(child)
            cx = base_x + (ci - 1) * spread
            pos = (cx, l2_y)
            l2_positions.append((pos, child, branch_colors[pi]))

            ax.plot([parent_pos[0], pos[0]], [parent_pos[1] - 0.5, pos[1] + 0.5],
                    color=col, linewidth=1.5, alpha=0.6)

            ax.text(pos[0], pos[1], triple_str(child), fontsize=8,
                    ha='center', va='center', color=DARK,
                    bbox=dict(boxstyle='round,pad=0.2', facecolor=CREAM,
                              edgecolor=branch_colors[pi], linewidth=1.5))

    ax.set_xlim(-1, 21)
    ax.set_ylim(1.5, 11.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('The Berggren Tree of Primitive Pythagorean Triples',
                 fontsize=20, color=DARK, fontweight='bold', pad=15)

    # Legend
    for i, (col, lbl) in enumerate(zip(branch_colors, ['$B_1$ branch', '$B_2$ branch', '$B_3$ branch'])):
        ax.plot([], [], color=col, linewidth=3, label=lbl)
    ax.legend(loc='lower right', fontsize=12, framealpha=0.8,
              facecolor=CREAM, edgecolor=DARK)

    save(fig, "fig09_berggren_tree.png")


# ============================================================
# FIG 10: Tree sieve — stylized tree with glowing fruit
# ============================================================
def fig10_tree_sieve():
    fig, ax = plt.subplots(1, 1, figsize=(12, 14))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    # Trunk
    trunk_x = [4.5, 5.5, 5.8, 4.2, 4.5]
    trunk_y = [0, 0, 4, 4, 0]
    ax.fill(trunk_x, trunk_y, color='#8B6914', alpha=0.8)
    ax.plot(trunk_x, trunk_y, color=DARK, linewidth=2)

    # Banner on trunk
    banner = FancyBboxPatch((3, 1.5), 4, 1.2, boxstyle="round,pad=0.2",
                            facecolor=CREAM, edgecolor=ACCENT1, linewidth=2, alpha=0.9)
    ax.add_patch(banner)
    ax.text(5, 2.1, '$N = 31{,}861$', fontsize=16, ha='center', va='center',
            color=ACCENT1, fontweight='bold')

    # Crown (canopy)
    from matplotlib.patches import Ellipse
    canopy = Ellipse((5, 8), 10, 8, facecolor=ACCENT3, edgecolor=DARK,
                     linewidth=2, alpha=0.3)
    ax.add_patch(canopy)

    # Branches
    branches = [(5, 4, 3, 7), (5, 4, 7, 7), (3, 7, 1, 10), (3, 7, 4, 10.5),
                (7, 7, 6, 10.5), (7, 7, 9, 10)]
    for x1, y1, x2, y2 in branches:
        ax.plot([x1, x2], [y1, y2], color='#6B4914', linewidth=3, alpha=0.7)

    # Glowing fruit (highlighted triples)
    fruits = [(1.5, 10.5, '139', True), (4, 11, '(a,b,c)', False),
              (6.5, 11, '229', True), (9, 10, '(a,b,c)', False),
              (2.5, 8.5, '(a,b,c)', False), (7.5, 8.5, '(a,b,c)', False)]
    for fx, fy, lbl, glow in fruits:
        col = GLOW if glow else ACCENT3
        alph = 0.9 if glow else 0.5
        sz = 0.5 if glow else 0.35
        c = plt.Circle((fx, fy), sz, facecolor=col, edgecolor=DARK,
                        linewidth=2 if glow else 1, alpha=alph, zorder=5)
        ax.add_patch(c)
        ax.text(fx, fy, lbl, fontsize=10 if glow else 8, ha='center', va='center',
                color=DARK, fontweight='bold' if glow else 'normal')

    # Figure at base with basket
    # Head
    head = plt.Circle((2, 1.5), 0.35, facecolor=SAND, edgecolor=DARK, linewidth=2)
    ax.add_patch(head)
    # Body
    ax.plot([2, 2], [1.15, 0.3], color=DARK, linewidth=3)
    # Arms reaching to basket
    ax.plot([2, 2.8], [0.8, 0.5], color=DARK, linewidth=2)
    ax.plot([2, 1.2], [0.8, 0.5], color=DARK, linewidth=2)
    # Legs
    ax.plot([2, 1.5], [0.3, -0.3], color=DARK, linewidth=2)
    ax.plot([2, 2.5], [0.3, -0.3], color=DARK, linewidth=2)
    # Basket
    basket = patches.Arc((2, 0.2), 1.5, 0.8, angle=0, theta1=0, theta2=180,
                         color=DARK, linewidth=2)
    ax.add_patch(basket)
    ax.text(2, 0, 'gcd', fontsize=10, ha='center', va='center', color=ACCENT4,
            fontweight='bold')

    ax.set_xlim(-1, 11)
    ax.set_ylim(-1, 13)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('The Tree Sieve — Shaking for Factors', fontsize=18, color=DARK,
                 fontweight='bold', pad=15)
    save(fig, "fig10_tree_sieve.png")


# ============================================================
# FIG 11: Number line with divisor arcs for N^2
# ============================================================
def fig11_divisor_arcs():
    fig, ax = plt.subplots(1, 1, figsize=(16, 8))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    N = 31861
    N2 = N * N

    # Show a simplified number line (log scale)
    ax.plot([0, 14], [0, 0], color=DARK, linewidth=2)

    # Key divisor pairs of N^2 = 139^2 * 229^2
    # (c-b)(c+b) = N^2
    divisor_pairs = [
        (1, N2, 'trivial'),
        (139, N2 // 139, '$\\gcd = 139$'),
        (229, N2 // 229, '$\\gcd = 229$'),
        (139 * 139, 229 * 229, ''),
    ]

    positions = {
        1: 0.5, 139: 3, 229: 4.5,
        139 * 139: 6.5, 229 * 229: 8,
        N2 // 229: 10, N2 // 139: 11.5, N2: 13.5
    }

    for d1, d2, label in divisor_pairs:
        x1 = positions.get(d1, 7)
        x2 = positions.get(d2, 7)

        ax.plot(x1, 0, '|', color=DARK, markersize=15, markeredgewidth=2)
        ax.plot(x2, 0, '|', color=DARK, markersize=15, markeredgewidth=2)

        ax.text(x1, -0.5, f'{d1}', fontsize=8, ha='center', color=SLATE, rotation=45)
        ax.text(x2, -0.5, f'{d2}', fontsize=8, ha='center', color=SLATE, rotation=45)

        # Arc
        mid = (x1 + x2) / 2
        height = (x2 - x1) * 0.3
        arc_color = ACCENT3 if '139' in label or '229' in label else SLATE
        lw = 2.5 if arc_color == ACCENT3 else 1

        t = np.linspace(x1, x2, 50)
        y = height * np.sin(np.pi * (t - x1) / (x2 - x1))
        ax.plot(t, y, color=arc_color, linewidth=lw, alpha=0.7)

        if label and 'trivial' not in label:
            ax.text(mid, height + 0.3, label, fontsize=12, ha='center',
                    color=ACCENT3, fontweight='bold')
            ax.plot(mid, height, '*', color=GLOW, markersize=15,
                    markeredgecolor=DARK, markeredgewidth=1)

    ax.text(7, -1.5, f'$N^2 = {N}^2 = {N2}$', fontsize=14, ha='center',
            color=DARK, fontweight='bold')
    ax.text(7, -2.2, '$31{,}861 = 139 \\times 229$', fontsize=13, ha='center',
            color=ACCENT1, fontweight='bold')

    ax.set_xlim(-0.5, 14.5)
    ax.set_ylim(-3, 5)
    ax.axis('off')
    ax.set_title('Divisor Pairs and Factor Discovery', fontsize=18, color=DARK,
                 fontweight='bold', pad=15)
    save(fig, "fig11_divisor_arcs.png")


# ============================================================
# FIG 12: Medieval cartographer's map — Three Roads
# ============================================================
def fig12_three_roads_map():
    fig, ax = plt.subplots(1, 1, figsize=(14, 12))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    # Castle at center
    castle_x, castle_y = 7, 7
    castle = FancyBboxPatch((5.5, 5.5), 3, 3, boxstyle="round,pad=0.2",
                            facecolor=SLATE, edgecolor=DARK, linewidth=3, alpha=0.8)
    ax.add_patch(castle)
    # turrets
    for tx in [5.8, 7, 8.2]:
        ax.plot([tx, tx], [8.5, 9.5], color=SLATE, linewidth=4)
        ax.plot([tx - 0.2, tx, tx + 0.2], [9.5, 10, 9.5], color=SLATE, linewidth=2)
    ax.text(7, 7, '$p$ and $q$', fontsize=18, ha='center', va='center',
            color=GLOW, fontweight='bold')

    # Land label
    ax.text(7, 3.8, 'The Land of Semiprimes', fontsize=13, ha='center',
            color=ACCENT4, fontstyle='italic', fontweight='bold')

    # Road 1 — Euler's Two Portraits (from left)
    road1_x = [0, 1.5, 2.5, 3.5, 4.5, 5.5]
    road1_y = [10, 9.5, 8.5, 8, 7.5, 7]
    ax.plot(road1_x, road1_y, color=AMBER, linewidth=4, alpha=0.7)
    # Art gallery
    gallery = FancyBboxPatch((0.5, 9), 2, 1.5, boxstyle="round,pad=0.1",
                             facecolor=CREAM, edgecolor=AMBER, linewidth=2)
    ax.add_patch(gallery)
    ax.text(1.5, 9.75, "Euler's Two\nPortraits", fontsize=9, ha='center',
            va='center', color=DARK, fontweight='bold')
    # small frames
    for fx, fy in [(0.8, 9.3), (1.5, 9.3), (2.2, 9.3)]:
        r = patches.Rectangle((fx - 0.15, fy - 0.1), 0.3, 0.2,
                               facecolor=AMBER, edgecolor=DARK, linewidth=1, alpha=0.5)
        ax.add_patch(r)

    # Road 2 — Gaussian Composition (from bottom)
    road2_x = [7, 7.5, 7, 6.5, 7, 7]
    road2_y = [0, 1.5, 2.5, 3.5, 4.5, 5.5]
    ax.plot(road2_x, road2_y, color=ACCENT2, linewidth=4, alpha=0.7)
    # Factory
    factory = FancyBboxPatch((5.5, 0.5), 3, 1.5, boxstyle="round,pad=0.1",
                             facecolor=CREAM, edgecolor=ACCENT2, linewidth=2)
    ax.add_patch(factory)
    ax.text(7, 1.25, 'Gaussian\nComposition', fontsize=9, ha='center',
            va='center', color=DARK, fontweight='bold')
    # gears
    for gx, gy in [(6, 0.8), (8, 0.8)]:
        g = plt.Circle((gx, gy), 0.2, facecolor='none', edgecolor=ACCENT2,
                        linewidth=1.5)
        ax.add_patch(g)

    # Road 3 — Berggren Tree Sieve (from right)
    road3_x = [14, 12.5, 11.5, 10.5, 9.5, 8.5]
    road3_y = [9, 8.5, 8, 7.5, 7.5, 7]
    ax.plot(road3_x, road3_y, color=ACCENT3, linewidth=4, alpha=0.7)
    # Forest
    for tx, ty in [(12, 8), (13, 9), (11.5, 9.5), (12.8, 7.5), (13.5, 8.5)]:
        tree_shape = plt.Polygon([(tx - 0.3, ty - 0.3), (tx, ty + 0.5), (tx + 0.3, ty - 0.3)],
                                 facecolor=ACCENT3, edgecolor=DARK, linewidth=1, alpha=0.5)
        ax.add_patch(tree_shape)
        ax.plot([tx, tx], [ty - 0.3, ty - 0.7], color='#8B6914', linewidth=2)
    ax.text(12.5, 10.3, 'Berggren\nTree Sieve', fontsize=9, ha='center',
            va='center', color=DARK, fontweight='bold')

    # Compass rose
    cx, cy = 12.5, 2
    ax.annotate('', xy=(cx + 1, cy), xytext=(cx, cy),
                arrowprops=dict(arrowstyle='->', color=DARK, lw=1.5))
    ax.text(cx + 1.2, cy, 'Ch. 5', fontsize=9, color=SLATE, fontstyle='italic')
    ax.annotate('', xy=(cx, cy + 1), xytext=(cx, cy),
                arrowprops=dict(arrowstyle='->', color=DARK, lw=1.5))
    ax.text(cx, cy + 1.3, 'N', fontsize=10, ha='center', color=DARK, fontweight='bold')
    ax.plot(cx, cy, 'o', color=GOLD, markersize=8, markeredgecolor=DARK)

    ax.set_xlim(-0.5, 15)
    ax.set_ylim(-0.5, 11.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Three Roads from Pythagoras', fontsize=20, color=DARK,
                 fontweight='bold', pad=15)
    save(fig, "fig12_three_roads_map.png")


# ============================================================
# FIG 13: Logarithmic scale — Berggren tree growth
# ============================================================
def fig13_exponential_climb():
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    B1 = np.array([[1, -2, 2], [2, -1, 2], [2, -2, 3]])
    B2 = np.array([[1, 2, 2], [2, 1, 2], [2, 2, 3]])
    B3 = np.array([[-1, 2, 2], [-2, 1, 2], [-2, 2, 3]])

    # Build tree up to depth 6
    levels = {0: [np.array([3, 4, 5])]}
    for d in range(1, 7):
        levels[d] = []
        for parent in levels[d - 1]:
            for M in [B1, B2, B3]:
                child = np.abs(M @ parent)
                levels[d].append(child)

    # Plot: x = generation, y = log10(hypotenuse)
    for depth, triples in levels.items():
        hyps = [t[2] for t in triples]
        for i, h in enumerate(hyps):
            jitter = (i / len(hyps) - 0.5) * 0.6
            ax.plot(depth + jitter, np.log10(h), 'o', color=ACCENT2,
                    markersize=max(3, 8 - depth), alpha=0.6, markeredgecolor=DARK,
                    markeredgewidth=0.3)

    # Lower bound line: 3^k * 5
    ks = np.linspace(0, 6, 50)
    ax.plot(ks, np.log10(5 * 3 ** ks), color=ACCENT1, linewidth=2, linestyle='--',
            label='Lower bound: $3^k \\cdot 5$')

    # RSA-size lines
    for bits, log_val, label in [(256, 77, '256-bit ($10^{77}$)'),
                                  (512, 154, '512-bit ($10^{154}$)')]:
        ax.axhline(log_val, color=ACCENT4, linewidth=1, linestyle=':', alpha=0.5)
        ax.text(5.5, log_val + 2, label, fontsize=10, color=ACCENT4, fontstyle='italic')

    # Small figure looking up
    ax.text(0.3, -1.5, '👤', fontsize=14, color=DARK)
    ax.annotate('', xy=(0.8, 5), xytext=(0.8, 0),
                arrowprops=dict(arrowstyle='->', color=SLATE, lw=1, linestyle='--'))

    ax.set_xlabel('Generation $k$', fontsize=14, color=DARK)
    ax.set_ylabel('$\\log_{10}(\\mathrm{hypotenuse})$', fontsize=14, color=DARK)
    ax.set_title('Exponential Growth of the Berggren Tree', fontsize=18,
                 color=DARK, fontweight='bold', pad=15)
    ax.legend(fontsize=12, facecolor=CREAM)

    # Set y range to show RSA lines symbolically
    ax.set_ylim(-3, 170)
    ax.set_xlim(-0.5, 7)

    save(fig, "fig13_exponential_climb.png")


# ============================================================
# FIG 14: Flower diagram — four representations of N^2
# ============================================================
def fig14_flower_diagram():
    fig, ax = plt.subplots(1, 1, figsize=(12, 12))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    # Center circle
    center = plt.Circle((6, 6), 1.2, facecolor=CREAM, edgecolor=DARK, linewidth=3)
    ax.add_patch(center)
    ax.text(6, 6, '$N^2$', fontsize=24, ha='center', va='center', color=DARK, fontweight='bold')

    # Petals
    petals = [
        (6, 10, '$a^2 + b^2$', 'Parent', AMBER, 90),
        (10, 6, '$c^2 + d^2$', 'Parent', AMBER, 0),
        (6, 2, '$(ac-bd)^2+(ad+bc)^2$', 'Child', COOL_BLUE, 270),
        (2, 6, '$(ac+bd)^2+(ad-bc)^2$', 'Child', COOL_BLUE, 180),
    ]

    for px, py, formula, role, col, angle in petals:
        petal = plt.Circle((px, py), 1.5, facecolor=col, edgecolor=DARK,
                           linewidth=2, alpha=0.3)
        ax.add_patch(petal)
        ax.text(px, py + 0.2, formula, fontsize=9, ha='center', va='center',
                color=DARK, fontweight='bold')
        ax.text(px, py - 0.5, role, fontsize=10, ha='center', va='center',
                color=SLATE, fontstyle='italic')

        # Line from center to petal
        dx, dy = px - 6, py - 6
        norm = np.sqrt(dx ** 2 + dy ** 2)
        ax.annotate('', xy=(6 + dx * 0.7, 6 + dy * 0.7),
                    xytext=(6 + dx * 0.25, 6 + dy * 0.25),
                    arrowprops=dict(arrowstyle='->', color=col, lw=2))

    # Curved arrows between parents and children
    for (sx, sy, ex, ey) in [(7.2, 9.2, 9.2, 7.2), (4.8, 9.2, 2.8, 7.2),
                              (9.2, 4.8, 7.2, 2.8), (2.8, 4.8, 4.8, 2.8)]:
        ax.annotate('', xy=(ex, ey), xytext=(sx, sy),
                    arrowprops=dict(arrowstyle='->', color=ACCENT4,
                                   connectionstyle='arc3,rad=0.3', lw=1.5))

    # Pot at bottom
    pot = FancyBboxPatch((2.5, -0.5), 7, 1.2, boxstyle="round,pad=0.2",
                         facecolor='#8B6914', edgecolor=DARK, linewidth=2, alpha=0.6)
    ax.add_patch(pot)
    ax.text(6, 0.1, 'Multiplicativity of $a^2 + b^2$', fontsize=12, ha='center',
            va='center', color=CREAM, fontweight='bold')

    ax.set_xlim(-0.5, 12.5)
    ax.set_ylim(-1.5, 12.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('The Flower of Representations', fontsize=20, color=DARK,
                 fontweight='bold', pad=15)
    save(fig, "fig14_flower_diagram.png")


# ============================================================
# FIG 15: Pythagorean Factoring Toolkit infographic
# ============================================================
def fig15_factoring_toolkit():
    fig, axes = plt.subplots(1, 3, figsize=(18, 10))
    fig.set_facecolor(SAND)

    columns = [
        ("Euler's Two Portraits", AMBER,
         '$(a-c)(a+c) = (d-b)(d+b)$',
         '$1105 = 4^2+33^2 = 9^2+32^2$\n$\\gcd(65, 13) = 13$\n$1105 = 5 \\times 13 \\times 17$'),
        ("Gaussian Composition", ACCENT2,
         '$(a^2+b^2)(c^2+d^2)$\n$= (ac-bd)^2+(ad+bc)^2$',
         '$(3,4,5) \\star (5,12,13)$\n$= (33, 56, 65)$'),
        ("Berggren Tree Sieve", ACCENT3,
         '$(c-b)(c+b) = a^2$',
         'Walk tree, collect\ntriples with $\\gcd(a, N) > 1$'),
    ]

    for idx, (ax, (title, col, identity, example)) in enumerate(zip(axes, columns)):
        ax.set_facecolor(SAND)

        # Title box
        title_box = FancyBboxPatch((0.1, 8), 3.8, 1.5, boxstyle="round,pad=0.2",
                                   facecolor=col, edgecolor=DARK, linewidth=2, alpha=0.4)
        ax.add_patch(title_box)
        ax.text(2, 8.75, title, fontsize=13, ha='center', va='center',
                color=DARK, fontweight='bold')

        # Identity
        ax.text(2, 6.5, identity, fontsize=11, ha='center', va='center',
                color=DARK,
                bbox=dict(boxstyle='round,pad=0.5', facecolor=CREAM, edgecolor=col, linewidth=1.5))

        # Example
        ax.text(2, 4, example, fontsize=10, ha='center', va='center',
                color=SLATE,
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor=SLATE, linewidth=1))

        # Icon at bottom
        if idx == 0:
            # Euler portrait silhouette
            head = plt.Circle((2, 2), 0.4, facecolor=col, edgecolor=DARK, linewidth=1.5, alpha=0.5)
            ax.add_patch(head)
            body = patches.Rectangle((1.5, 1), 1, 0.8, facecolor=col, edgecolor=DARK,
                                     linewidth=1, alpha=0.3)
            ax.add_patch(body)
        elif idx == 1:
            # Gaussian lattice dots
            for x in range(0, 5):
                for y_pt in range(1, 4):
                    ax.plot(x * 0.5 + 1, y_pt * 0.3 + 1.2, '.', color=col, markersize=5, alpha=0.5)
        else:
            # Tree
            ax.plot([2, 1.5], [2.5, 1.5], color=col, linewidth=2)
            ax.plot([2, 2], [2.5, 1.5], color=col, linewidth=2)
            ax.plot([2, 2.5], [2.5, 1.5], color=col, linewidth=2)
            ax.plot([2, 2], [2.5, 3], color='#8B6914', linewidth=3)

        ax.set_xlim(-0.3, 4.3)
        ax.set_ylim(0.5, 10.5)
        ax.set_aspect('equal')
        ax.axis('off')

    # Foundation bar
    fig.text(0.5, 0.02,
             'Multiplicativity of $a^2 + b^2$    |    Lorentz Invariance: $Q = 0$',
             fontsize=14, ha='center', color=DARK, fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.5', facecolor=CREAM, edgecolor=DARK, linewidth=2))

    fig.suptitle('The Pythagorean Factoring Toolkit', fontsize=22, color=DARK,
                 fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0.06, 1, 0.94])
    save(fig, "fig15_factoring_toolkit.png")


# ============================================================
# FIG 16: Winding road to future chapters
# ============================================================
def fig16_road_ahead():
    fig, ax = plt.subplots(1, 1, figsize=(16, 8))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    # Winding road
    t = np.linspace(0, 14, 300)
    road_y = 4 + 1.5 * np.sin(t * 0.5) * np.exp(-t * 0.05)
    road_width = 0.8 * np.exp(-t * 0.03)

    ax.fill_between(t, road_y - road_width, road_y + road_width,
                    color=SLATE, alpha=0.3)
    ax.plot(t, road_y, color=SLATE, linewidth=2, alpha=0.5)

    # dashed center line
    ax.plot(t, road_y, color=GLOW, linewidth=1, linestyle='--', alpha=0.5)

    # Mile markers
    markers = [
        (2, 'Lattice\nReduction', 'Ch. 5', ACCENT2),
        (5, 'Complexity\nBounds', 'Ch. 6', ACCENT1),
        (8, 'Quantum\nSpeedup', 'Ch. 7', ACCENT4),
        (11, '...and\nbeyond', '', GOLD),
    ]

    for mx, label, ch, col in markers:
        my = 4 + 1.5 * np.sin(mx * 0.5) * np.exp(-mx * 0.05)
        # mile marker post
        ax.plot([mx, mx], [my - 1.5, my - 0.5], color=DARK, linewidth=3)
        ax.plot(mx, my - 0.5, 's', color=col, markersize=12, markeredgecolor=DARK, markeredgewidth=1.5)

        ax.text(mx, my - 2, label, fontsize=11, ha='center', va='center',
                color=DARK, fontweight='bold')
        if ch:
            ax.text(mx, my - 2.8, ch, fontsize=9, ha='center', va='center',
                    color=col, fontstyle='italic')

    # Landscape elements
    # Lattice points field (near Ch. 5)
    for lx in np.arange(1, 3.5, 0.4):
        for ly in np.arange(5.5, 7, 0.4):
            ax.plot(lx, ly, '.', color=ACCENT2, markersize=3, alpha=0.4)

    # Hyperbolic tiling (near Ch. 6)
    for cx, cy, r in [(5.5, 6.5, 0.3), (4.8, 7, 0.2), (5.2, 6.2, 0.15),
                       (6, 7, 0.25), (5.8, 6, 0.15)]:
        c = plt.Circle((cx, cy), r, facecolor='none', edgecolor=ACCENT1,
                        linewidth=1, alpha=0.3)
        ax.add_patch(c)

    # Quantum circuit (near Ch. 7)
    for qy in [6.5, 7, 7.5]:
        ax.plot([7.5, 9.5], [qy, qy], color=ACCENT4, linewidth=1, alpha=0.3)
    for qx in [8, 8.5, 9]:
        ax.plot(qx, 7, 's', color=ACCENT4, markersize=6, alpha=0.4)

    # Glow at vanishing point
    glow = plt.Circle((13.5, road_y[-10]), 1, facecolor=GLOW, edgecolor='none', alpha=0.15)
    ax.add_patch(glow)
    glow2 = plt.Circle((13.5, road_y[-10]), 0.5, facecolor=GLOW, edgecolor='none', alpha=0.25)
    ax.add_patch(glow2)

    # Mist
    for mx_m in np.arange(10, 14, 0.5):
        for my_m in np.arange(2, 8, 1):
            c = plt.Circle((mx_m, my_m), 0.6, facecolor=SAND, edgecolor='none', alpha=0.3)
            ax.add_patch(c)

    ax.set_xlim(-0.5, 15)
    ax.set_ylim(0, 8.5)
    ax.axis('off')
    ax.set_title('The Road Ahead', fontsize=20, color=DARK, fontweight='bold', pad=15)
    save(fig, "fig16_road_ahead.png")


# ============================================================
# Run all
# ============================================================
if __name__ == "__main__":
    print("Generating Chapter 4 illustrations...")
    fig01_rectangle_dissection()
    fig02_gaussian_lattice()
    fig03_triple_factory()
    fig04_multiplication_table()
    fig05_euler_xray()
    fig06_euler_portrait()
    fig07_pythagorean_cone()
    fig08_light_cones()
    fig09_berggren_tree()
    fig10_tree_sieve()
    fig11_divisor_arcs()
    fig12_three_roads_map()
    fig13_exponential_climb()
    fig14_flower_diagram()
    fig15_factoring_toolkit()
    fig16_road_ahead()
    print("Done! All images saved to", OUT)

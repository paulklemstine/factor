#!/usr/bin/env python3
"""Generate all illustrations for Chapter 13: The GCD Cascade."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import matplotlib.patheffects as pe
import numpy as np
import os
from math import gcd, sqrt

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
# FIG 1: The Eavesdropper's Puzzle
# ============================================================
def fig01_eavesdropper():
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # Envelope
    env_x = [1.5, 5.5, 5.5, 1.5, 1.5]
    env_y = [2.5, 2.5, 5.5, 5.5, 2.5]
    ax.fill(env_x, env_y, color=CREAM, edgecolor=DARK, linewidth=2, zorder=2)
    # Envelope flap
    flap_x = [1.5, 3.5, 5.5]
    flap_y = [5.5, 4.2, 5.5]
    ax.fill(flap_x, flap_y, color='#E8D5B7', edgecolor=DARK, linewidth=2, zorder=3)
    # Seal
    seal = plt.Circle((3.5, 4.6), 0.35, color=ACCENT1, zorder=4)
    ax.add_patch(seal)
    ax.text(3.5, 4.6, '?', fontsize=14, ha='center', va='center', color='white',
            fontweight='bold', zorder=5)
    # Label on envelope
    ax.text(3.5, 3.5, r'$p \times q = 4{,}579$', fontsize=15, ha='center', va='center',
            color=DARK, fontweight='bold', fontstyle='italic')

    # Four numbered cards
    cards = [
        (6.5, 5.0, r'$a = 390$', LIGHT_RED),
        (8.5, 5.0, r'$b = 1{,}738$', LIGHT_BLUE),
        (6.5, 3.0, r'$c = 4{,}122$', LIGHT_GREEN),
        (8.5, 3.0, r'$d = 4{,}579$', '#F9E79F'),
    ]
    for cx, cy, label, color in cards:
        card = FancyBboxPatch((cx - 0.8, cy - 0.55), 1.6, 1.1,
                              boxstyle="round,pad=0.1", facecolor=color,
                              edgecolor=DARK, linewidth=1.5, zorder=3)
        ax.add_patch(card)
        ax.text(cx, cy, label, fontsize=12, ha='center', va='center',
                color=DARK, fontweight='bold', zorder=4)

    # Magnifying glass
    mg_cx, mg_cy = 10.3, 4.0
    glass = plt.Circle((mg_cx, mg_cy), 0.9, facecolor='#D5F5E3', edgecolor=SLATE,
                       linewidth=3, alpha=0.5, zorder=6)
    ax.add_patch(glass)
    ax.plot([mg_cx + 0.6, mg_cx + 1.5], [mg_cy - 0.6, mg_cy - 1.5],
            color=SLATE, linewidth=4, zorder=6)
    # Primes visible through lens
    ax.text(mg_cx - 0.15, mg_cy + 0.2, r'$p\!=\!43$', fontsize=11, ha='center', va='center',
            color=ACCENT1, fontweight='bold', alpha=0.7, zorder=7)
    ax.text(mg_cx + 0.15, mg_cy - 0.25, r'$q\!=\!107$', fontsize=11, ha='center', va='center',
            color=ACCENT2, fontweight='bold', alpha=0.7, zorder=7)

    # Caption
    ax.text(6, 1.3, "The eavesdropper's puzzle \u2014\ncan four numbers betray two secrets?",
            fontsize=13, ha='center', va='center', color=DARK, fontstyle='italic')

    # Title
    ax.text(6, 7.3, "The Eavesdropper's Puzzle", fontsize=18, ha='center',
            va='center', color=DARK, fontweight='bold')

    save(fig, "fig01_eavesdropper.png")


# ============================================================
# FIG 2: Three Channels Tetrahedron
# ============================================================
def fig02_channel_tetrahedron():
    fig, ax = plt.subplots(1, 1, figsize=(10, 9))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 9)
    ax.axis('off')

    # Tetrahedron vertices
    va = (2, 1.5)
    vb = (8, 1.5)
    vc = (5, 4.5)
    vd = (5, 7.5)

    # Thick colored edges (channels) among a, b, c
    ax.plot([va[0], vb[0]], [va[1], vb[1]], color=ACCENT1, linewidth=5, zorder=3)
    ax.plot([va[0], vc[0]], [va[1], vc[1]], color=ACCENT2, linewidth=5, zorder=3)
    ax.plot([vb[0], vc[0]], [vb[1], vc[1]], color=ACCENT3, linewidth=5, zorder=3)

    # Dashed lines from d to each base vertex
    for v in [va, vb, vc]:
        ax.plot([vd[0], v[0]], [vd[1], v[1]], color=DARK, linewidth=1.5,
                linestyle='--', zorder=2)

    # Edge labels
    ax.text(5, 1.0, r'$\mathrm{Ch}_{ab} = a^2 + b^2$', fontsize=12, ha='center',
            color=ACCENT1, fontweight='bold')
    ax.text(2.8, 3.3, r'$\mathrm{Ch}_{ac}$' + '\n' + r'$= a^2 + c^2$', fontsize=10,
            ha='center', color=ACCENT2, fontweight='bold', rotation=45)
    ax.text(7.2, 3.3, r'$\mathrm{Ch}_{bc}$' + '\n' + r'$= b^2 + c^2$', fontsize=10,
            ha='center', color=ACCENT3, fontweight='bold', rotation=-45)

    # Dashed line labels
    ax.text(3.1, 5.0, r'$d^2\!-\!c^2$', fontsize=9, ha='center', color=SLATE, rotation=63)
    ax.text(6.9, 5.0, r'$d^2\!-\!b^2$', fontsize=9, ha='center', color=SLATE, rotation=-63)
    ax.text(5.35, 6.2, r'$d^2\!-\!a^2$', fontsize=9, ha='left', color=SLATE)

    # Vertex dots and labels
    for v, lbl, offset in [(va, '$a$', (-0.5, -0.3)),
                            (vb, '$b$', (0.5, -0.3)),
                            (vc, '$c$', (0.4, -0.3)),
                            (vd, '$d$', (0, 0.4))]:
        ax.plot(v[0], v[1], 'o', color=GOLD, markersize=16, markeredgecolor=DARK,
                markeredgewidth=2, zorder=5)
        ax.text(v[0] + offset[0], v[1] + offset[1], lbl, fontsize=16, ha='center',
                va='center', color=DARK, fontweight='bold')

    # Banner
    ax.text(5, 0.3, r"Three channels, one hypotenuse \u2014 sum: $2d^2$",
            fontsize=13, ha='center', color=DARK, fontstyle='italic',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=CREAM, edgecolor=DARK, linewidth=1))

    ax.text(5, 8.6, "Three Channels, One Tower", fontsize=18, ha='center',
            color=DARK, fontweight='bold')

    save(fig, "fig02_channel_tetrahedron.png")


# ============================================================
# FIG 3: Venn Diagram — Triangulation Principle
# ============================================================
def fig03_triangulation_venn():
    fig, ax = plt.subplots(1, 1, figsize=(10, 9))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.set_xlim(-4, 4)
    ax.set_ylim(-3.5, 4)
    ax.axis('off')

    r = 2.0
    centers = [(-1.0, -0.3), (1.0, -0.3), (0, 1.4)]
    colors = [ACCENT1, ACCENT2, ACCENT3]
    labels = [r'$\mathrm{Ch}_{ab}$', r'$\mathrm{Ch}_{ac}$', r'$\mathrm{Ch}_{bc}$']
    label_offsets = [(-1.8, -1.8), (1.8, -1.8), (0, 2.8)]

    for c, col, lbl, lo in zip(centers, colors, labels, label_offsets):
        circle = plt.Circle(c, r, facecolor=col, alpha=0.15, edgecolor=col,
                           linewidth=2.5, zorder=2)
        ax.add_patch(circle)
        ax.text(c[0] + lo[0], c[1] + lo[1], lbl, fontsize=14, ha='center',
                va='center', color=col, fontweight='bold')

    ax.text(0, -1.0, r'$b^2 - c^2$', fontsize=11, ha='center', va='center',
            color=DARK, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.15', facecolor=CREAM, alpha=0.8))
    ax.text(-0.9, 0.9, r'$a^2 - c^2$', fontsize=11, ha='center', va='center',
            color=DARK, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.15', facecolor=CREAM, alpha=0.8))
    ax.text(0.9, 0.9, r'$a^2 - b^2$', fontsize=11, ha='center', va='center',
            color=DARK, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.15', facecolor=CREAM, alpha=0.8))

    ax.text(0, 0.15, r'$2a^2$' + '\n' + r'$2b^2$' + '\n' + r'$2c^2$',
            fontsize=10, ha='center', va='center', color=ACCENT4, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.2', facecolor=GLOW, alpha=0.5, edgecolor=ACCENT4))

    ax.text(0, 3.7, "The Triangulation Principle", fontsize=18, ha='center',
            color=DARK, fontweight='bold')

    save(fig, "fig03_triangulation_venn.png")


# ============================================================
# FIG 4: Euclid's Cascade / Waterfall
# ============================================================
def fig04_cascade_waterfall():
    fig, ax = plt.subplots(1, 1, figsize=(11, 9))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 9)
    ax.axis('off')

    for cx, label, col in [(3, r'$\mathrm{Ch}_{ab}$', ACCENT1),
                            (8, r'$\mathrm{Ch}_{ac}$', ACCENT2)]:
        box = FancyBboxPatch((cx - 1.3, 7.2), 2.6, 1.2, boxstyle="round,pad=0.15",
                             facecolor=col, edgecolor=DARK, linewidth=2, alpha=0.3, zorder=3)
        ax.add_patch(box)
        ax.text(cx, 7.8, label, fontsize=16, ha='center', va='center',
                color=DARK, fontweight='bold', zorder=4)

    ax.annotate('', xy=(5.5, 6.3), xytext=(3, 7.2),
                arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=2.5))
    ax.annotate('', xy=(5.5, 6.3), xytext=(8, 7.2),
                arrowprops=dict(arrowstyle='->', color=ACCENT2, lw=2.5))

    sub = plt.Circle((5.5, 5.8), 0.5, facecolor=GLOW, edgecolor=DARK, linewidth=2, zorder=4)
    ax.add_patch(sub)
    ax.text(5.5, 5.8, '\u2212', fontsize=24, ha='center', va='center', color=DARK,
            fontweight='bold', zorder=5)

    ax.annotate('', xy=(5.5, 4.5), xytext=(5.5, 5.3),
                arrowprops=dict(arrowstyle='->', color=SLATE, lw=2.5))
    ax.text(6.6, 4.9, r'$b^2 - c^2$', fontsize=14, ha='left', va='center',
            color=DARK, fontweight='bold')

    rock_x = [4.5, 5.5, 6.5]
    rock_y = [4.0, 4.5, 4.0]
    ax.fill(rock_x, rock_y, color=SLATE, alpha=0.4, zorder=3)
    ax.plot(rock_x + [rock_x[0]], rock_y + [rock_y[0]], color=DARK, linewidth=1.5, zorder=3)

    wl_x = np.array([3.5, 3.8, 3.3, 3.6, 3.1])
    wl_y = np.array([3.8, 3.2, 2.6, 2.0, 1.4])
    ax.plot(wl_x, wl_y, color=ACCENT2, linewidth=4, alpha=0.6, zorder=2)
    ax.text(2.5, 2.6, r'$(b - c)$', fontsize=14, ha='center', va='center',
            color=ACCENT2, fontweight='bold')

    wr_x = np.array([7.5, 7.2, 7.7, 7.4, 7.9])
    wr_y = np.array([3.8, 3.2, 2.6, 2.0, 1.4])
    ax.plot(wr_x, wr_y, color=ACCENT3, linewidth=4, alpha=0.6, zorder=2)
    ax.text(8.5, 2.6, r'$(b + c)$', fontsize=14, ha='center', va='center',
            color=ACCENT3, fontweight='bold')

    boulder = plt.Circle((5.5, 2.0), 0.55, facecolor=GOLD, edgecolor=DARK,
                         linewidth=2.5, zorder=5)
    ax.add_patch(boulder)
    ax.text(5.5, 2.0, '$p$', fontsize=18, ha='center', va='center', color=DARK,
            fontweight='bold', zorder=6)

    ax.annotate('', xy=(7.0, 1.8), xytext=(6.05, 2.0),
                arrowprops=dict(arrowstyle='->', color=GOLD, lw=2, connectionstyle='arc3,rad=-0.2'))
    ax.text(6.5, 1.3, '?', fontsize=16, ha='center', color=GOLD, fontweight='bold')

    ax.text(5.5, 0.5, "Euclid's cascade \u2014 a prime must choose a side",
            fontsize=13, ha='center', color=DARK, fontstyle='italic',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=CREAM, edgecolor=DARK))

    save(fig, "fig04_cascade_waterfall.png")


# ============================================================
# FIG 5: Composite Tower with Spotlights
# ============================================================
def fig05_composite_tower():
    fig, ax = plt.subplots(1, 1, figsize=(10, 9))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 9)
    ax.axis('off')

    tw = 2.0
    th_total = 5.0
    tx = 4.0
    ty = 1.5

    # Bottom layer (5 blue bricks)
    n_blue = 5
    brick_h_blue = th_total * (5.0 / 12.0) / n_blue
    for i in range(n_blue):
        rect = patches.Rectangle((tx, ty + i * brick_h_blue), tw, brick_h_blue * 0.9,
                                  facecolor=LIGHT_BLUE, edgecolor=DARK, linewidth=1, zorder=3)
        ax.add_patch(rect)

    base_top = ty + n_blue * brick_h_blue

    # Top layer (7 red bricks)
    n_red = 7
    remaining = th_total - n_blue * brick_h_blue
    brick_h_red = remaining / n_red
    for i in range(n_red):
        yy = base_top + i * brick_h_red
        rect = patches.Rectangle((tx, yy), tw, brick_h_red * 0.9,
                                  facecolor=LIGHT_RED, edgecolor=DARK, linewidth=1, zorder=3)
        ax.add_patch(rect)

    # Tower outline
    ax.plot([tx, tx, tx + tw, tx + tw], [ty, ty + th_total, ty + th_total, ty],
            color=DARK, linewidth=2.5, zorder=4)

    ax.text(tx + tw / 2, ty + th_total + 0.3, '$d = 35$', fontsize=16, ha='center',
            color=DARK, fontweight='bold')

    ax.plot([tx - 0.1, tx + tw + 0.1], [base_top, base_top], color=DARK,
            linewidth=2, linestyle='--', zorder=4)
    ax.text(tx - 0.4, ty + n_blue * brick_h_blue / 2, '$5$', fontsize=18, ha='center',
            color=ACCENT2, fontweight='bold')
    ax.text(tx - 0.4, base_top + remaining / 2, '$7$', fontsize=18,
            ha='center', color=ACCENT1, fontweight='bold')

    spotlights = [
        (1.5, 1.0, r'$\mathrm{Ch}_{ab}$', ACCENT1, tx + 0.3, ty + th_total * 0.6),
        (2.5, 0.5, r'$\mathrm{Ch}_{ac}$', ACCENT2, tx + 0.5, ty + brick_h_blue * 2),
        (8.5, 0.5, r'$\mathrm{Ch}_{bc}$', ACCENT3, tx + tw - 0.3, ty + th_total * 0.8),
    ]

    for sx, sy, lbl, col, ex, ey in spotlights:
        beam_x = [sx, ex - 0.3, ex + 0.3, sx]
        beam_y = [sy, ey + 0.3, ey - 0.3, sy]
        ax.fill(beam_x, beam_y, color=col, alpha=0.12, zorder=1)
        ax.plot([sx, ex], [sy, ey], color=col, linewidth=1.5, alpha=0.4, zorder=1)
        ax.plot(sx, sy, 'o', color=col, markersize=12, markeredgecolor=DARK,
                markeredgewidth=1.5, zorder=5)
        ax.text(sx, sy - 0.4, lbl, fontsize=11, ha='center', color=col, fontweight='bold')

    glow5 = plt.Circle((tx + tw / 2, ty + brick_h_blue * 2), 0.35, facecolor=GLOW,
                        edgecolor=ACCENT2, linewidth=2, alpha=0.8, zorder=6)
    ax.add_patch(glow5)
    ax.text(tx + tw / 2, ty + brick_h_blue * 2, '$5$', fontsize=14, ha='center', va='center',
            color=DARK, fontweight='bold', zorder=7)

    ax.text(5, 0.3, "A composite tower reveals its secret bricks \u2014\nbut only to the right spotlight",
            fontsize=12, ha='center', color=DARK, fontstyle='italic')

    ax.text(5, 8.5, "The Composite Tower", fontsize=18, ha='center',
            color=DARK, fontweight='bold')

    save(fig, "fig05_composite_tower.png")


# ============================================================
# FIG 6: Parity Chessboard
# ============================================================
def fig06_parity_chessboard():
    fig, ax = plt.subplots(1, 1, figsize=(10, 7))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.set_xlim(-1.5, 9)
    ax.set_ylim(-1.5, 6)
    ax.axis('off')

    col_labels = ['(E,E,E)', '(E,E,O)', '(E,O,O)', '(O,O,O)']
    row_labels = ['$d$ even', '$d$ odd']

    possible = [
        [True, False, False, False],   # d even
        [False, True, False, False],   # d odd
    ]

    cell_w = 2.0
    cell_h = 1.5
    x0 = 1.0
    y0 = 1.0

    for r in range(2):
        for c in range(4):
            x = x0 + c * cell_w
            y = y0 + (1 - r) * cell_h
            if possible[r][c]:
                color = LIGHT_GREEN
                symbol = '\u2713'
                sym_color = ACCENT3
            else:
                color = LIGHT_RED
                symbol = '\u2717'
                sym_color = ACCENT1
            rect = patches.Rectangle((x, y), cell_w - 0.1, cell_h - 0.1,
                                      facecolor=color, edgecolor=DARK, linewidth=1.5, zorder=2)
            ax.add_patch(rect)
            ax.text(x + cell_w / 2 - 0.05, y + cell_h / 2 - 0.05, symbol,
                    fontsize=22, ha='center', va='center', color=sym_color,
                    fontweight='bold', zorder=3)

    for c, lbl in enumerate(col_labels):
        ax.text(x0 + c * cell_w + cell_w / 2 - 0.05, y0 + 2 * cell_h + 0.15, lbl,
                fontsize=12, ha='center', va='bottom', color=DARK, fontweight='bold')
    ax.text(x0 + 2 * cell_w - 0.05, y0 + 2 * cell_h + 0.7, "Parity of $(a, b, c)$",
            fontsize=13, ha='center', color=SLATE, fontweight='bold')

    for r, lbl in enumerate(row_labels):
        ax.text(x0 - 0.2, y0 + (1 - r) * cell_h + cell_h / 2 - 0.05, lbl,
                fontsize=13, ha='right', va='center', color=DARK, fontweight='bold')

    ax.text(4.5, -0.8, "The Parity Chessboard of Pythagorean Quadruples \u2014\n"
            "only certain combinations survive the mod-4 sieve",
            fontsize=12, ha='center', color=DARK, fontstyle='italic')

    ax.text(4.5, 5.3, "The Parity Chessboard", fontsize=18, ha='center',
            color=DARK, fontweight='bold')

    save(fig, "fig06_parity_chessboard.png")


# ============================================================
# FIG 7: Three Trails to One Peak
# ============================================================
def fig07_three_trails():
    fig, ax = plt.subplots(1, 1, figsize=(10, 9))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 9)
    ax.axis('off')

    peak = (5, 7.5)
    ax.plot(peak[0], peak[1], '*', color=GOLD, markersize=25, markeredgecolor=DARK,
            markeredgewidth=1.5, zorder=10)
    ax.text(5, 8.0, '$d$', fontsize=18, ha='center', color=DARK, fontweight='bold')

    trails = [
        (1.5, 1.0, '$c_1$', ACCENT1),
        (5.0, 1.0, '$c_2$', ACCENT2),
        (8.5, 1.0, '$c_3$', ACCENT3),
    ]

    for tx, ty, lbl, col in trails:
        n = 20
        t = np.linspace(0, 1, n)
        px = tx + (peak[0] - tx) * t + 0.3 * np.sin(4 * np.pi * t)
        py = ty + (peak[1] - ty) * t
        ax.plot(px, py, color=col, linewidth=3, alpha=0.7, zorder=3)
        ax.plot(tx, ty, 'o', color=col, markersize=14, markeredgecolor=DARK,
                markeredgewidth=2, zorder=5)
        ax.text(tx, ty - 0.5, lbl, fontsize=14, ha='center', color=col, fontweight='bold')

    pairs = [
        (trails[0], trails[1], r'$c_1 - c_2$'),
        (trails[1], trails[2], r'$c_2 - c_3$'),
        (trails[0], trails[2], r'$c_1 - c_3$'),
    ]
    y_offsets = [0.0, 0.0, -0.8]
    for (t1, t2, lbl), yoff in zip(pairs, y_offsets):
        y = min(t1[1], t2[1]) + yoff
        ax.annotate('', xy=(t2[0] - 0.3, y), xytext=(t1[0] + 0.3, y),
                    arrowprops=dict(arrowstyle='<->', color=SLATE, lw=1.5, linestyle='--'))
        ax.text((t1[0] + t2[0]) / 2, y - 0.35, lbl, fontsize=11, ha='center',
                color=SLATE, fontweight='bold')

    mg_x, mg_y = 3.25, 0.5
    glass = plt.Circle((mg_x, mg_y), 0.4, facecolor='#D5F5E3', edgecolor=SLATE,
                       linewidth=2, alpha=0.5, zorder=6)
    ax.add_patch(glass)
    ax.plot([mg_x + 0.25, mg_x + 0.6], [mg_y - 0.25, mg_y - 0.6],
            color=SLATE, linewidth=3, zorder=6)
    ax.text(mg_x, mg_y, '$p$', fontsize=12, ha='center', va='center',
            color=GOLD, fontweight='bold', zorder=7)

    ax.text(5, -0.0, "Three trails, one peak, one hidden factor",
            fontsize=13, ha='center', color=DARK, fontstyle='italic',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=CREAM, edgecolor=DARK))

    save(fig, "fig07_three_trails.png")


# ============================================================
# FIG 8: Brahmagupta's Two-Square Identity
# ============================================================
def fig08_brahmagupta():
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    fig.set_facecolor(SAND)

    titles = [
        r'$a^2 + b^2$',
        r'$c^2 + d^2$',
        'Two decompositions',
    ]

    for idx, ax in enumerate(axes):
        ax.set_facecolor(SAND)
        ax.set_xlim(0, 4)
        ax.set_ylim(0, 4)
        ax.set_aspect('equal')
        ax.axis('off')

        if idx == 0:
            rect1 = patches.Rectangle((0.5, 2), 1.5, 1.5, facecolor=LIGHT_RED,
                                       edgecolor=DARK, linewidth=2)
            rect2 = patches.Rectangle((2.2, 0.5), 1.2, 1.2, facecolor=LIGHT_BLUE,
                                       edgecolor=DARK, linewidth=2)
            ax.add_patch(rect1)
            ax.add_patch(rect2)
            ax.text(1.25, 2.75, r'$a^2$', fontsize=16, ha='center', va='center',
                    color=ACCENT1, fontweight='bold')
            ax.text(2.8, 1.1, r'$b^2$', fontsize=16, ha='center', va='center',
                    color=ACCENT2, fontweight='bold')
        elif idx == 1:
            rect1 = patches.Rectangle((0.5, 2), 1.5, 1.5, facecolor=LIGHT_GREEN,
                                       edgecolor=DARK, linewidth=2)
            rect2 = patches.Rectangle((2.2, 0.5), 1.2, 1.2, facecolor='#F9E79F',
                                       edgecolor=DARK, linewidth=2)
            ax.add_patch(rect1)
            ax.add_patch(rect2)
            ax.text(1.25, 2.75, r'$c^2$', fontsize=16, ha='center', va='center',
                    color=ACCENT3, fontweight='bold')
            ax.text(2.8, 1.1, r'$d^2$', fontsize=16, ha='center', va='center',
                    color=ACCENT5, fontweight='bold')
        else:
            s = 3.0
            ox, oy = 0.5, 0.5
            sq = patches.Rectangle((ox, oy), s, s, facecolor='white',
                                    edgecolor=DARK, linewidth=2)
            ax.add_patch(sq)
            ax.plot([ox, ox + s], [oy, oy + s], color=DARK, linewidth=2, linestyle='--')
            tri1 = plt.Polygon([(ox, oy), (ox + s, oy + s), (ox, oy + s)],
                               facecolor=ACCENT4, alpha=0.15)
            ax.add_patch(tri1)
            ax.text(ox + s * 0.25, oy + s * 0.72,
                    r'$(ac\!-\!bd)^2$' + '\n' + r'$+\,(ad\!+\!bc)^2$',
                    fontsize=9, ha='center', va='center', color=ACCENT4, fontweight='bold')
            tri2 = plt.Polygon([(ox, oy), (ox + s, oy + s), (ox + s, oy)],
                               facecolor=ACCENT5, alpha=0.15)
            ax.add_patch(tri2)
            ax.text(ox + s * 0.72, oy + s * 0.28,
                    r'$(ac\!+\!bd)^2$' + '\n' + r'$+\,(ad\!-\!bc)^2$',
                    fontsize=9, ha='center', va='center', color=ACCENT5, fontweight='bold')

        ax.set_title(titles[idx], fontsize=12, color=DARK, fontweight='bold', pad=10)

    fig.text(0.355, 0.5, r'$\times$', fontsize=28, ha='center', va='center',
             color=DARK, fontweight='bold')
    fig.text(0.645, 0.5, r'$=$', fontsize=28, ha='center', va='center',
             color=DARK, fontweight='bold')

    fig.suptitle("Brahmagupta's Magic: One Product, Two Decompositions",
                 fontsize=16, color=DARK, fontweight='bold', y=1.02)

    fig.text(0.5, -0.02, "Brahmagupta's magic: one product, two decompositions",
             fontsize=12, ha='center', color=DARK, fontstyle='italic')

    save(fig, "fig08_brahmagupta.png")


# ============================================================
# FIG 9: Asymmetry Is the Key
# ============================================================
def fig09_asymmetry():
    fig, ax = plt.subplots(1, 1, figsize=(12, 7))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)
    ax.axis('off')

    ax.text(6, 6.5, "Asymmetry Is the Key", fontsize=18, ha='center',
            color=DARK, fontweight='bold')

    for i, (cx, quad, ch_val, has_factor) in enumerate([
        (3.0, r'$(6, 10, 33, 35)$', r'$\mathrm{Ch}_{ab} = 136$', False),
        (9.0, r'$(10, 15, 30, 35)$', r'$\mathrm{Ch}_{ab} = 325 = 5^2 \!\times\! 13$', True),
    ]):
        card = FancyBboxPatch((cx - 2.2, 2.5), 4.4, 3.2, boxstyle="round,pad=0.2",
                              facecolor=CREAM, edgecolor=DARK, linewidth=2, zorder=2)
        ax.add_patch(card)

        ax.text(cx, 5.0, f'Quadruple {i+1}', fontsize=12, ha='center',
                color=SLATE, fontweight='bold')
        ax.text(cx, 4.3, quad, fontsize=13, ha='center', color=DARK, fontweight='bold')
        ax.text(cx, 3.5, ch_val, fontsize=11, ha='center', color=DARK)

        mg_x = cx + 1.2
        mg_y = 3.0
        glass = plt.Circle((mg_x, mg_y), 0.35,
                           facecolor='#D5F5E3' if has_factor else '#FADBD8',
                           edgecolor=SLATE, linewidth=2, alpha=0.6, zorder=5)
        ax.add_patch(glass)
        ax.plot([mg_x + 0.2, mg_x + 0.5], [mg_y - 0.2, mg_y - 0.5],
                color=SLATE, linewidth=2.5, zorder=5)

        if has_factor:
            ax.text(mg_x, mg_y, '$5$', fontsize=14, ha='center', va='center',
                    color=GOLD, fontweight='bold', zorder=6)
        else:
            ax.text(mg_x, mg_y, '\u2014', fontsize=14, ha='center', va='center',
                    color=ACCENT1, fontweight='bold', zorder=6)

    ax.text(9.0, 2.8, r'Factor of $5$ visible!', fontsize=11, ha='center',
            color=GOLD, fontweight='bold', fontstyle='italic')

    ax.text(6, 4.0, 'vs', fontsize=20, ha='center', va='center',
            color=SLATE, fontweight='bold', fontstyle='italic')

    ax.text(6, 1.5, "One quadruple hides the factor; the other reveals it.\n"
            r"$136$ has no factor of $5$, but $325 = 5^2 \times 13$ does.",
            fontsize=11, ha='center', color=DARK, fontstyle='italic')

    save(fig, "fig09_asymmetry.png")


# ============================================================
# FIG 10: Descent Through the Spheres
# ============================================================
def fig10_descent_spheres():
    fig, ax = plt.subplots(1, 1, figsize=(10, 9))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    ax.axis('off')

    radii = [4.0, 2.5, 1.2]
    alphas = [0.12, 0.18, 0.25]
    labels_outer = [r"$(a, b, c)$", r"$(a', b', c')$", r"$(a'', b'', c'')$"]
    colors = [ACCENT2, ACCENT3, ACCENT5]

    for r, alpha, lbl, col in zip(radii, alphas, labels_outer, colors):
        ellipse = patches.Ellipse((0, 0), 2 * r, 2 * r * 0.7, facecolor=col,
                                   alpha=alpha, edgecolor=col, linewidth=2, zorder=2)
        ax.add_patch(ellipse)

    angles_outer = [30, 110, 200, 310]
    for ang in angles_outer:
        rad = np.radians(ang)
        x = 4.0 * np.cos(rad)
        y = 4.0 * 0.7 * np.sin(rad)
        ax.plot(x, y, 'o', color=ACCENT2, markersize=6, markeredgecolor=DARK,
                markeredgewidth=1, zorder=5)

    ax.text(3.5, 2.5, r"$(a, b, c)$", fontsize=13, color=ACCENT2, fontweight='bold')
    ax.text(2.0, 1.2, r"$(a', b', c')$", fontsize=12, color=ACCENT3, fontweight='bold')
    ax.text(0.7, 0.3, r"$(a'', b'', c'')$", fontsize=11, color=ACCENT5, fontweight='bold')

    ax.annotate('', xy=(2.3, 0.6), xytext=(3.6, 1.2),
                arrowprops=dict(arrowstyle='->', color=DARK, lw=2))
    ax.text(3.3, 0.5, r'$\div\, p$', fontsize=13, ha='center', color=DARK, fontweight='bold')

    ax.annotate('', xy=(1.0, -0.1), xytext=(2.0, 0.3),
                arrowprops=dict(arrowstyle='->', color=DARK, lw=2))
    ax.text(1.9, -0.3, r'$\div\, p$', fontsize=13, ha='center', color=DARK, fontweight='bold')

    ax.text(0, 4.5, "Descent Through the Spheres", fontsize=18, ha='center',
            color=DARK, fontweight='bold')

    ax.text(0, -4.5, "Peeling off one factor at a time",
            fontsize=13, ha='center', color=DARK, fontstyle='italic',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=CREAM, edgecolor=DARK))

    save(fig, "fig10_descent_spheres.png")


# ============================================================
# FIG 11: Pell's Staircase
# ============================================================
def fig11_pell_staircase():
    fig, ax = plt.subplots(1, 1, figsize=(12, 7))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    pell_data = [
        (2, 3, r'$\frac{3}{2} = 1.500$'),
        (12, 17, r'$\frac{17}{12} \approx 1.417$'),
        (70, 99, r'$\frac{99}{70} \approx 1.4143$'),
        (408, 577, r'$\frac{577}{408} \approx 1.41422$'),
    ]

    ratios = [d / a for a, d, _ in pell_data]
    sqrt2 = np.sqrt(2)

    ax.set_xlim(-0.5, 4.5)
    ax.set_ylim(1.39, 1.55)

    ax.axhline(y=sqrt2, color=ACCENT1, linewidth=2, linestyle='--', alpha=0.6, zorder=1)
    ax.text(4.3, sqrt2 + 0.003, r'$\sqrt{2}$', fontsize=14, color=ACCENT1, fontweight='bold')

    for i, (a, d, lbl) in enumerate(pell_data):
        r = d / a
        ax.plot(i, r, 'o', color=GOLD, markersize=14, markeredgecolor=DARK,
                markeredgewidth=2, zorder=5)
        ax.text(i, r + 0.008, lbl, fontsize=11, ha='center', color=DARK, fontweight='bold')
        quad_str = f'$({a}, {a}, 1, {d})$'
        ax.text(i, r - 0.012, quad_str, fontsize=9, ha='center', color=SLATE)

    for i in range(len(pell_data) - 1):
        ax.plot([i, i + 1], [ratios[i], ratios[i + 1]], color=ACCENT2, linewidth=1.5,
                linestyle=':', alpha=0.5, zorder=2)

    ax.set_xlabel('Pell solution index', fontsize=13, color=DARK)
    ax.set_ylabel(r'Ratio $d/a$', fontsize=13, color=DARK)
    ax.set_xticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(DARK)
    ax.spines['left'].set_color(DARK)

    ax.set_title(r"Pell's Staircase \u2014 quadruples approaching $\sqrt{2}$",
                 fontsize=16, color=DARK, fontweight='bold', pad=15)

    ax.text(2, 1.395, r"Quadruples that almost balance, forever approaching $\sqrt{2}$",
            fontsize=12, ha='center', color=DARK, fontstyle='italic')

    save(fig, "fig11_pell_staircase.png")


# ============================================================
# FIG 12: Channel Graphs — Pentagon and Hexagon
# ============================================================
def fig12_channel_graphs():
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    fig.set_facecolor(SAND)

    for ax_idx, (ax, n) in enumerate(zip(axes, [5, 6])):
        ax.set_facecolor(SAND)
        ax.set_xlim(-1.8, 1.8)
        ax.set_ylim(-1.8, 1.8)
        ax.set_aspect('equal')
        ax.axis('off')

        angles = [np.pi / 2 + 2 * np.pi * k / n for k in range(n)]
        verts = [(1.3 * np.cos(a), 1.3 * np.sin(a)) for a in angles]

        for i in range(n):
            for j in range(i + 1, n):
                ax.plot([verts[i][0], verts[j][0]], [verts[i][1], verts[j][1]],
                        color=ACCENT2, linewidth=1.2, alpha=0.5, zorder=2)

        for k in range(n):
            ax.plot(verts[k][0], verts[k][1], 'o', color=GOLD, markersize=14,
                    markeredgecolor=DARK, markeredgewidth=2, zorder=5)
            lx = 1.55 * np.cos(angles[k])
            ly = 1.55 * np.sin(angles[k])
            ax.text(lx, ly, f'$a_{k + 1}$', fontsize=12, ha='center', va='center',
                    color=DARK, fontweight='bold')

        total_channels = n * (n - 1) // 2
        name = "Pentagon" if n == 5 else "Hexagon"
        suffix = "sextuplet" if n == 5 else "septuplet"
        ax.set_title(f'{name}: {total_channels} channels ({suffix})',
                     fontsize=13, color=DARK, fontweight='bold', pad=10)

    fig.suptitle("The Channel Graph Grows Rich as Dimensions Rise",
                 fontsize=16, color=DARK, fontweight='bold', y=1.0)

    fig.text(0.5, -0.02, "The channel graph grows rich as dimensions rise \u2014 "
             "10 channels for a sextuplet, 15 for a septuplet",
             fontsize=11, ha='center', color=DARK, fontstyle='italic')

    save(fig, "fig12_channel_graphs.png")


# ============================================================
# FIG 13: Modular Fingerprint
# ============================================================
def fig13_modular_fingerprint():
    fig, ax = plt.subplots(1, 1, figsize=(10, 9))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    ax.axis('off')

    np.random.seed(42)
    n_rings = 12
    for i in range(n_rings):
        r = 0.3 + i * 0.35
        theta = np.linspace(0, 2 * np.pi, 200)
        wobble = 0.05 * np.sin(7 * theta + i) + 0.03 * np.cos(11 * theta)
        rx = (r + wobble) * (1.0 + 0.2 * np.sin(theta * 2 + 0.5))
        ry = (r + wobble) * (0.7 + 0.1 * np.cos(theta * 3))
        color_val = plt.cm.copper(i / n_rings)
        ax.plot(rx, ry, color=color_val, linewidth=1.8, alpha=0.6, zorder=2)

    residue_labels = [
        (1.2, 0.5, r'$\equiv 0\;(\mathrm{mod}\;3)$'),
        (2.0, -0.8, r'$\equiv 1\;(\mathrm{mod}\;5)$'),
        (3.0, 1.5, r'$\equiv 4\;(\mathrm{mod}\;7)$'),
        (-1.5, 1.8, r'$\equiv 2\;(\mathrm{mod}\;3)$'),
    ]
    for x, y, lbl in residue_labels:
        ax.text(x, y, lbl, fontsize=10, ha='center', va='center', color=DARK,
                fontweight='bold', alpha=0.7,
                bbox=dict(boxstyle='round,pad=0.15', facecolor=SAND, alpha=0.8, edgecolor='none'))

    for cx, cy, q_lbl in [(-3.5, -3.5, 'Quadruple 1'), (3.5, -3.5, 'Quadruple 2')]:
        card = FancyBboxPatch((cx - 1.0, cy - 0.5), 2.0, 1.0, boxstyle="round,pad=0.1",
                              facecolor=CREAM, edgecolor=DARK, linewidth=1.5, zorder=5)
        ax.add_patch(card)
        ax.text(cx, cy, q_lbl, fontsize=10, ha='center', va='center',
                color=DARK, fontweight='bold', zorder=6)
        ax.annotate('', xy=(0, -1.5), xytext=(cx, cy + 0.5),
                    arrowprops=dict(arrowstyle='->', color=SLATE, lw=1.5,
                                   connectionstyle='arc3,rad=0.2'))

    ax.text(0, -0.2, r'$d^2$', fontsize=20, ha='center', va='center',
            color=GOLD, fontweight='bold', zorder=4,
            bbox=dict(boxstyle='round,pad=0.2', facecolor=GLOW, alpha=0.5, edgecolor=GOLD))

    ax.text(0, 4.5, "The Modular Fingerprint", fontsize=18, ha='center',
            color=DARK, fontweight='bold')

    ax.text(0, -4.7, "Unique to $d^2$, shared by all its quadruples",
            fontsize=13, ha='center', color=DARK, fontstyle='italic',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=CREAM, edgecolor=DARK))

    save(fig, "fig13_modular_fingerprint.png")


# ============================================================
# FIG 14: GCD Cascade Algorithm Flowchart
# ============================================================
def fig14_gcd_flowchart():
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')

    boxes = [
        (3.5, 8.5, "Start: composite $d$", LIGHT_BLUE),
        (3.5, 6.5, "Find quadruple(s):\n$a^2 + b^2 + c^2 = d^2$", LIGHT_GREEN),
        (3.5, 4.2, "Compute:\n$(d\\!-\\!a),\\,(d\\!+\\!a),\\,(d\\!-\\!b),$\n$(d\\!+\\!b),\\,(d\\!-\\!c),\\,(d\\!+\\!c)$", '#F9E79F'),
        (3.5, 1.8, "GCD cascade\n$\\longrightarrow$ factor of $d$", '#D5F5E3'),
    ]

    for cx, cy, text, color in boxes:
        box = FancyBboxPatch((cx - 2.5, cy - 0.7), 5.0, 1.4,
                             boxstyle="round,pad=0.2", facecolor=color,
                             edgecolor=DARK, linewidth=2, zorder=3)
        ax.add_patch(box)
        ax.text(cx, cy, text, fontsize=11, ha='center', va='center',
                color=DARK, fontweight='bold', zorder=4)

    for i in range(len(boxes) - 1):
        y_from = boxes[i][1] - 0.7
        y_to = boxes[i + 1][1] + 0.7
        ax.annotate('', xy=(3.5, y_to), xytext=(3.5, y_from),
                    arrowprops=dict(arrowstyle='->', color=DARK, lw=2.5))

    examples = [
        (10.5, 8.5, "$d = 35$"),
        (10.5, 6.5, "$(6,\\, 10,\\, 33,\\, 35)$"),
        (10.5, 4.2, "$29,\\, 41,\\, 25,$\n$45,\\, 2,\\, 68$"),
        (10.5, 1.8, "$\\gcd(25,\\, 35) = 5$"),
    ]

    for cx, cy, text in examples:
        box = FancyBboxPatch((cx - 2.2, cy - 0.6), 4.4, 1.2,
                             boxstyle="round,pad=0.15", facecolor=CREAM,
                             edgecolor=SLATE, linewidth=1.5, linestyle='--', zorder=3)
        ax.add_patch(box)
        ax.text(cx, cy, text, fontsize=12, ha='center', va='center',
                color=SLATE, fontweight='bold', zorder=4)

    for i in range(len(examples) - 1):
        y_from = examples[i][1] - 0.6
        y_to = examples[i + 1][1] + 0.6
        ax.annotate('', xy=(10.5, y_to), xytext=(10.5, y_from),
                    arrowprops=dict(arrowstyle='->', color=SLATE, lw=1.5, linestyle='--'))

    for i in range(len(boxes)):
        ax.annotate('', xy=(examples[i][0] - 2.2, examples[i][1]),
                    xytext=(boxes[i][0] + 2.5, boxes[i][1]),
                    arrowprops=dict(arrowstyle='->', color=ACCENT5, lw=1.5, alpha=0.5))

    star_x, star_y = 10.5, 1.8
    for angle in np.linspace(0, 2 * np.pi, 16, endpoint=False):
        dx = 2.8 * np.cos(angle)
        dy = 1.0 * np.sin(angle)
        ax.plot([star_x, star_x + dx], [star_y, star_y + dy],
                color=GOLD, linewidth=1.2, alpha=0.3, zorder=1)

    ax.text(10.5, 0.8, r'$\mathbf{5 \times 7}$', fontsize=20, ha='center',
            color=GOLD, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=GLOW, edgecolor=GOLD, linewidth=2))

    ax.text(3.5, 9.5, "Algorithm", fontsize=14, ha='center', color=DARK, fontweight='bold')
    ax.text(10.5, 9.5, "Worked Example", fontsize=14, ha='center', color=SLATE, fontweight='bold')

    ax.text(7, 9.8, "The GCD Cascade Algorithm", fontsize=18, ha='center',
            color=DARK, fontweight='bold')

    ax.text(7, 0.2, "From quadruple to factor in four steps",
            fontsize=13, ha='center', color=DARK, fontstyle='italic')

    save(fig, "fig14_gcd_flowchart.png")


# ============================================================
# Run all
# ============================================================
if __name__ == '__main__':
    print("Generating Chapter 13 images...")
    fig01_eavesdropper()
    fig02_channel_tetrahedron()
    fig03_triangulation_venn()
    fig04_cascade_waterfall()
    fig05_composite_tower()
    fig06_parity_chessboard()
    fig07_three_trails()
    fig08_brahmagupta()
    fig09_asymmetry()
    fig10_descent_spheres()
    fig11_pell_staircase()
    fig12_channel_graphs()
    fig13_modular_fingerprint()
    fig14_gcd_flowchart()
    print("Done! All Chapter 13 images generated.")

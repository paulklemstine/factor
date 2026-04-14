#!/usr/bin/env python3
"""Generate all illustrations for Chapter 14: The Tree That Cracks Numbers."""

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
# Helper: Berggren maps and inverses
# ============================================================
def B1_inv(a, b, c):
    return (a + 2*b - 2*c, -2*a - b + 2*c, -2*a - 2*b + 3*c)

def B2_inv(a, b, c):
    return (a + 2*b - 2*c, 2*a + b - 2*c, -2*a - 2*b + 3*c)

def B3_inv(a, b, c):
    return (-a - 2*b + 2*c, 2*a + b - 2*c, -2*a - 2*b + 3*c)

def B1(a, b, c):
    return (a - 2*b + 2*c, 2*a - b + 2*c, 2*a - 2*b + 3*c)

def B2(a, b, c):
    return (a + 2*b + 2*c, 2*a + b + 2*c, 2*a + 2*b + 3*c)

def B3(a, b, c):
    return (-a + 2*b + 2*c, -2*a + b + 2*c, -2*a + 2*b + 3*c)

def parent_triple(a, b, c):
    """Return the unique parent of (a,b,c) in the Berggren tree, plus which inverse was used."""
    for i, inv in enumerate([B1_inv, B2_inv, B3_inv], 1):
        result = inv(a, b, c)
        if result[0] > 0 and result[1] > 0 and result[2] > 0:
            return result, i
    return None, 0

def trivial_triple(N):
    return (N, (N*N - 1)//2, (N*N + 1)//2)

def descend_to_root(a, b, c):
    """Return list of (triple, inverse_used) from (a,b,c) up to (3,4,5)."""
    path = [((a, b, c), 0)]
    cur = (a, b, c)
    limit = 200
    while cur != (3, 4, 5) and limit > 0:
        par, which = parent_triple(*cur)
        if par is None:
            break
        path.append((par, which))
        cur = par
        limit -= 1
    return path

def factor_via_tree(N):
    """Run the factoring algorithm, return list of (triple, gcd_a, gcd_b, found_factor)."""
    tt = trivial_triple(N)
    g = gcd(tt[0], N)
    steps = [(tt, g, gcd(tt[1], N), 1 < g < N or 1 < gcd(tt[1], N) < N)]
    cur = tt
    limit = 200
    while cur != (3, 4, 5) and limit > 0:
        # Make it primitive for tree climbing
        d = gcd(gcd(cur[0], cur[1]), cur[2])
        prim = (cur[0]//d, cur[1]//d, cur[2]//d)
        par, which = parent_triple(*prim)
        if par is None:
            break
        ga = gcd(par[0], N)
        gb = gcd(par[1], N)
        steps.append((par, ga, gb, 1 < ga < N or 1 < gb < N))
        cur = par
        limit -= 1
    return steps


# ============================================================
# FIG 1: Right triangle with trivial triple + table
# ============================================================
def fig01_trivial_triple():
    fig, axes = plt.subplots(1, 2, figsize=(14, 7), gridspec_kw={'width_ratios': [1.2, 1]})
    fig.set_facecolor(SAND)

    # Left: triangle for N=15
    ax = axes[0]
    ax.set_facecolor(SAND)
    N = 15
    b_val = (N*N - 1)//2
    c_val = (N*N + 1)//2

    scale = 4.0 / b_val
    bx = b_val * scale
    ay = N * scale

    tri_x = [0, bx, 0, 0]
    tri_y = [0, 0, ay, 0]
    ax.plot(tri_x, tri_y, color=DARK, linewidth=3, zorder=5)
    ax.fill(tri_x[:3], tri_y[:3], alpha=0.08, color=ACCENT2)

    sq = 0.15
    ax.plot([sq, sq, 0], [0, sq, sq], color=DARK, linewidth=1.5, zorder=5)

    ax.text(bx/2, -0.25, r'$b = \frac{N^2-1}{2}$', fontsize=13, ha='center',
            color=ACCENT2, fontweight='bold')
    ax.text(-0.5, ay/2, r'$N$', fontsize=16, ha='center', color=ACCENT1, fontweight='bold')
    ax.text(bx/2 + 0.3, ay/2 + 0.15, r'$c = \frac{N^2+1}{2}$', fontsize=13, ha='center',
            color=ACCENT3, fontweight='bold', rotation=-15)

    ax.text(-0.3, ay/2 + 0.25, '?', fontsize=28, ha='center', color=ACCENT1, fontweight='bold',
            alpha=0.6, style='italic')
    ax.text(-0.9, ay * 0.35, r'$3$', fontsize=14, ha='center', color=ACCENT1, alpha=0.5,
            fontweight='bold')
    ax.text(-0.9, ay * 0.65, r'$\times\,5$', fontsize=14, ha='center', color=ACCENT1, alpha=0.5,
            fontweight='bold')

    ax.set_xlim(-1.5, bx + 0.8)
    ax.set_ylim(-0.7, ay + 0.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(r'The Trivial Triple for $N = 15$', fontsize=16, fontweight='bold',
                 color=DARK, pad=10)

    # Right: Table
    ax2 = axes[1]
    ax2.set_facecolor(SAND)
    ax2.axis('off')

    table_data = []
    for nn in [3, 5, 7, 9, 11, 13, 15]:
        bb = (nn*nn - 1)//2
        cc = (nn*nn + 1)//2
        table_data.append([f'${nn}$', f'${bb}$', f'${cc}$'])

    table = ax2.table(cellText=table_data,
                      colLabels=[r'$N$', r'$b$', r'$c$'],
                      cellLoc='center', loc='center',
                      colColours=[LIGHT_BLUE, LIGHT_GREEN, CREAM])
    table.auto_set_font_size(False)
    table.set_fontsize(13)
    table.scale(1.0, 1.8)

    for col in range(3):
        table[7, col].set_facecolor(GLOW)
        table[7, col].set_edgecolor(ACCENT5)
        table[7, col].set_linewidth(2)
    for row in range(8):
        for col in range(3):
            table[row, col].set_edgecolor(SLATE)

    ax2.set_title('Trivial Triples', fontsize=16, fontweight='bold', color=DARK, pad=10)

    plt.tight_layout()
    save(fig, "fig01_trivial_triple.png")


# ============================================================
# FIG 2: Crowbar diagram — difference of squares
# ============================================================
def fig02_crowbar():
    fig, ax = plt.subplots(1, 1, figsize=(14, 9))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.axis('off')

    # Left side: triangle
    tri_cx, tri_cy = 2.5, 5.5
    sc = 0.8
    tri_xs = [tri_cx, tri_cx + 3*sc, tri_cx, tri_cx]
    tri_ys = [tri_cy, tri_cy, tri_cy + 1.5*sc, tri_cy]
    ax.fill(tri_xs[:3], tri_ys[:3], alpha=0.1, color=ACCENT2)
    ax.plot(tri_xs, tri_ys, color=DARK, linewidth=2.5)
    ax.text(tri_cx + 1.5*sc, tri_cy - 0.35, '$b$', fontsize=14, ha='center', color=ACCENT2,
            fontweight='bold')
    ax.text(tri_cx - 0.35, tri_cy + 0.6*sc, '$N$', fontsize=14, ha='center', color=ACCENT1,
            fontweight='bold')
    ax.text(tri_cx + 1.8*sc, tri_cy + 1.0*sc, '$c$', fontsize=14, ha='center', color=ACCENT3,
            fontweight='bold')

    # Arrow to equation
    ax.annotate('', xy=(5.5, 5.8), xytext=(4.5, 5.8),
                arrowprops=dict(arrowstyle='->', lw=2.5, color=ACCENT5))
    ax.text(5.0, 6.2, 'subtract', fontsize=11, ha='center', color=ACCENT5, fontweight='bold')

    # Central equation
    ax.text(8.5, 5.8, r'$(c - b)(c + b) = N^2$', fontsize=20, ha='center', va='center',
            color=DARK, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=CREAM, edgecolor=DARK, linewidth=2))

    # Rectangle on the right
    rect_x, rect_y = 11.0, 4.5
    rw, rh = 2.5, 2.5
    ax.add_patch(patches.Rectangle((rect_x, rect_y), rw, rh, linewidth=2,
                                    edgecolor=DARK, facecolor=LIGHT_BLUE, alpha=0.4))
    ax.text(rect_x + rw/2, rect_y - 0.3, r'$d = c - b$', fontsize=12, ha='center',
            color=ACCENT2, fontweight='bold')
    ax.text(rect_x - 0.6, rect_y + rh/2, r'$e = c + b$', fontsize=12, ha='center',
            color=ACCENT3, fontweight='bold', rotation=90)
    ax.text(rect_x + rw/2, rect_y + rh/2, r'$N^2$', fontsize=18, ha='center', va='center',
            color=DARK, fontweight='bold')

    # Table below
    table_data = [
        [r'$1 \times 225$', r'$(15, 112, 113)$', 'Trivial'],
        [r'$9 \times 25$', r'$(15, 8, 17)$', 'Reveals 3 and 5'],
        [r'$3 \times 75$', r'$(15, 36, 39)$', 'Factor 3 visible'],
    ]

    table = ax.table(cellText=table_data,
                      colLabels=[r'$d \times e$', r'Triple $(N, b, c)$', 'Factors visible?'],
                      cellLoc='center', loc='lower center',
                      bbox=[0.1, 0.02, 0.8, 0.38],
                      colColours=[LIGHT_BLUE, LIGHT_GREEN, CREAM])
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.0, 2.0)
    table[2, 2].set_facecolor(LIGHT_RED)
    table[3, 2].set_facecolor(LIGHT_RED)

    ax.set_xlim(0, 14.5)
    ax.set_ylim(-0.5, 8)
    ax.set_title(r"The Difference-of-Squares Crowbar: $(c - b)(c + b) = N^2$",
                 fontsize=18, fontweight='bold', color=DARK, pad=15)
    save(fig, "fig02_crowbar.png")


# ============================================================
# FIG 3: Berggren ternary tree, 3 levels
# ============================================================
def fig03_berggren_tree():
    fig, ax = plt.subplots(1, 1, figsize=(18, 12))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    root = (3, 4, 5)
    children = [B1(3,4,5), B2(3,4,5), B3(3,4,5)]
    grandchildren = []
    for ch in children:
        grandchildren.append([B1(*ch), B2(*ch), B3(*ch)])

    positions = {}
    positions[root] = (9, 10)
    child_xs = [3, 9, 15]
    for i, ch in enumerate(children):
        positions[ch] = (child_xs[i], 6.5)

    gc_xs = [1, 3, 5, 7, 9, 11, 13, 15, 17]
    idx = 0
    for i, gcgroup in enumerate(grandchildren):
        for j, gc in enumerate(gcgroup):
            positions[gc] = (gc_xs[idx], 3)
            idx += 1

    branch_colors = [ACCENT2, ACCENT3, ACCENT1]
    branch_labels = [r'$B_1$', r'$B_2$', r'$B_3$']

    def draw_edge(parent, child, label, color):
        px, py = positions[parent]
        cx, cy = positions[child]
        ax.annotate('', xy=(cx, cy + 0.7), xytext=(px, py - 0.7),
                    arrowprops=dict(arrowstyle='->', color=color, lw=2.5))
        mx, my = (px + cx) / 2, (py + cy) / 2
        offset = 0.3 if cx < px else (-0.3 if cx > px else 0)
        ax.text(mx + offset, my + 0.2, label, fontsize=10, ha='center', va='center',
                color=color, fontweight='bold')

    for i, ch in enumerate(children):
        draw_edge(root, ch, branch_labels[i], branch_colors[i])
    for i, gcgroup in enumerate(grandchildren):
        for j, gc in enumerate(gcgroup):
            draw_edge(children[i], gc, branch_labels[j], branch_colors[j])

    def draw_node(triple, highlight=False):
        x, y = positions[triple]
        a, b, c = triple
        label = f'$({a},\\,{b},\\,{c})$'
        fc = GLOW if highlight else CREAM
        ec = ACCENT5 if highlight else DARK
        lw = 3 if highlight else 2
        box = FancyBboxPatch((x - 1.35, y - 0.5), 2.7, 1.0,
                             boxstyle="round,pad=0.15", facecolor=fc,
                             edgecolor=ec, linewidth=lw)
        ax.add_patch(box)
        ax.text(x, y, label, fontsize=10, ha='center', va='center',
                color=DARK, fontweight='bold')

    draw_node(root, highlight=True)
    for ch in children:
        draw_node(ch)
    for gcgroup in grandchildren:
        for gc in gcgroup:
            draw_node(gc)

    ax.set_xlim(-0.5, 18.5)
    ax.set_ylim(1.5, 11.5)
    ax.axis('off')
    ax.set_title("Berggren's Ternary Tree of Pythagorean Triples",
                 fontsize=20, fontweight='bold', color=DARK, pad=15)
    save(fig, "fig03_berggren_tree.png")


# ============================================================
# FIG 4: Reverse climb inset
# ============================================================
def fig04_reverse_climb():
    fig, ax = plt.subplots(1, 1, figsize=(8, 10))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    path = descend_to_root(39, 80, 89)
    n = len(path)

    for i, (triple, which) in enumerate(path):
        y = i * 2.5
        a, b, c = triple
        label = f'$({a},\\,{b},\\,{c})$'

        fc = GLOW if triple == (3, 4, 5) else CREAM
        box = FancyBboxPatch((1.5, y - 0.4), 5, 0.8,
                             boxstyle="round,pad=0.15", facecolor=fc,
                             edgecolor=DARK, linewidth=2)
        ax.add_patch(box)
        ax.text(4, y, label, fontsize=14, ha='center', va='center',
                color=DARK, fontweight='bold')

        ax.text(7.2, y, f'$c = {c}$', fontsize=12, ha='left', va='center',
                color=ACCENT2, fontweight='bold')

        if i < n - 1:
            next_which = path[i+1][1]
            ax.annotate('', xy=(4, (i+1)*2.5 - 0.5), xytext=(4, y + 0.5),
                        arrowprops=dict(arrowstyle='->', color=ACCENT4, lw=2.5))
            if next_which > 0:
                ax.text(0.8, y + 1.25, f'$B_{next_which}^{{-1}}$', fontsize=12,
                        ha='center', va='center', color=ACCENT4, fontweight='bold')

    root_y = (n - 1) * 2.5
    ax.text(4, root_y + 0.7, 'Root!', fontsize=14, ha='center', va='center',
            color=GOLD, fontweight='bold')

    ax.set_xlim(0, 9)
    ax.set_ylim(-1, root_y + 1.5)
    ax.axis('off')
    ax.set_title('Climbing the Tree: One Path Back to $(3,4,5)$',
                 fontsize=16, fontweight='bold', color=DARK, pad=15)
    save(fig, "fig04_reverse_climb.png")


# ============================================================
# FIG 5: Worked descent ladder (39,80,89) -> (3,4,5)
# ============================================================
def fig05_descent_ladder():
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    path = descend_to_root(39, 80, 89)
    n = len(path)

    for i, (triple, which) in enumerate(path):
        y = i * 3.0
        a, b, c = triple
        label = f'$({a},\\,{b},\\,{c})$'

        fc = GLOW if triple == (3, 4, 5) else CREAM
        ec = ACCENT5 if triple == (3, 4, 5) else DARK
        box = FancyBboxPatch((2.0, y - 0.45), 5.5, 0.9,
                             boxstyle="round,pad=0.15", facecolor=fc,
                             edgecolor=ec, linewidth=2)
        ax.add_patch(box)
        ax.text(4.75, y, label, fontsize=14, ha='center', va='center',
                color=DARK, fontweight='bold')

        ax.text(8.5, y, f'$c = {c}$', fontsize=13, ha='left', va='center',
                color=ACCENT2, fontweight='bold')

        if i < n - 1:
            next_which = path[i+1][1]
            ax.annotate('', xy=(4.75, (i+1)*3.0 - 0.55), xytext=(4.75, y + 0.55),
                        arrowprops=dict(arrowstyle='->', color=ACCENT4, lw=2.5))
            ax.text(1.5, y + 1.5, f'$B_{next_which}^{{-1}}$', fontsize=13,
                    ha='center', va='center', color=ACCENT4, fontweight='bold')

    ax.text(4.75, (n-1)*3.0 + 0.8, 'Arrived!', fontsize=15, ha='center',
            color=GOLD, fontweight='bold')

    ax.set_xlim(0, 11)
    ax.set_ylim(-1.2, (n-1)*3.0 + 1.5)
    ax.axis('off')
    ax.set_title('Descent Ladder: $(39, 80, 89) \\to (3, 4, 5)$',
                 fontsize=18, fontweight='bold', color=DARK, pad=15)
    save(fig, "fig05_descent_ladder.png")


# ============================================================
# FIG 6: Hypotenuse staircase
# ============================================================
def fig06_hypotenuse_staircase():
    fig, ax = plt.subplots(1, 1, figsize=(10, 7))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    tt = trivial_triple(21)
    d = gcd(gcd(tt[0], tt[1]), tt[2])
    start = (tt[0]//d, tt[1]//d, tt[2]//d)
    path = descend_to_root(*start)

    steps = list(range(len(path)))
    hyps = [p[0][2] for p in path]

    ax.axhspan(-10, 0, color=LIGHT_RED, alpha=0.4, zorder=0)
    ax.text(len(path) * 0.6, -5, 'Forbidden zone $(c < 0)$', fontsize=13,
            ha='center', va='center', color=ACCENT1, fontweight='bold', alpha=0.7)

    ax.step(steps, hyps, where='mid', color=SLATE, linewidth=2, alpha=0.5, zorder=2)
    ax.plot(steps, hyps, 'o', color=ACCENT2, markersize=12, markeredgecolor=DARK,
            markeredgewidth=1.5, zorder=5)

    for i, (s, h) in enumerate(zip(steps, hyps)):
        offset = 12 if i % 2 == 0 else -16
        ax.annotate(f'$c = {h}$', (s, h), textcoords="offset points",
                    xytext=(15, offset), fontsize=10, color=DARK, fontweight='bold')

    ax.annotate('Arrived!', (steps[-1], hyps[-1]),
                textcoords="offset points", xytext=(40, 10),
                fontsize=14, color=GOLD, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=GOLD, lw=2))

    ax.set_xlabel('Descent step', fontsize=14, color=DARK)
    ax.set_ylabel('Hypotenuse $c$', fontsize=14, color=DARK)
    ax.set_ylim(-10, max(hyps) * 1.15)
    ax.set_xlim(-0.5, len(path) - 0.3)
    ax.axhline(y=0, color=ACCENT1, linewidth=1.5, linestyle='--', alpha=0.6)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(DARK)
    ax.spines['bottom'].set_color(DARK)
    ax.tick_params(colors=DARK)
    ax.set_title('The Hypotenuse Always Shrinks', fontsize=18, fontweight='bold',
                 color=DARK, pad=15)
    save(fig, "fig06_hypotenuse_staircase.png")


# ============================================================
# FIG 7: Three doors, one opens
# ============================================================
def fig07_three_doors():
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.axis('off')

    triple = (39, 80, 89)
    cx, cy = 7, 5.5
    box = FancyBboxPatch((cx - 1.8, cy - 0.5), 3.6, 1.0,
                         boxstyle="round,pad=0.2", facecolor=CREAM,
                         edgecolor=DARK, linewidth=2.5)
    ax.add_patch(box)
    ax.text(cx, cy, f'$({triple[0]},\\,{triple[1]},\\,{triple[2]})$',
            fontsize=16, ha='center', va='center', color=DARK, fontweight='bold')

    results = [
        (B1_inv(*triple), r'$B_1^{-1}$'),
        (B2_inv(*triple), r'$B_2^{-1}$'),
        (B3_inv(*triple), r'$B_3^{-1}$'),
    ]

    box_positions = [(2, 1.5), (7, 1.5), (12, 1.5)]

    for i, ((res, label), (bx, by)) in enumerate(zip(results, box_positions)):
        a, b, c = res
        all_pos = a > 0 and b > 0 and c > 0

        fc = LIGHT_GREEN if all_pos else LIGHT_RED
        ec = ACCENT3 if all_pos else ACCENT1
        lw = 3 if all_pos else 2

        box = FancyBboxPatch((bx - 1.8, by - 0.5), 3.6, 1.0,
                             boxstyle="round,pad=0.2", facecolor=fc,
                             edgecolor=ec, linewidth=lw)
        ax.add_patch(box)

        txt_color = ACCENT1 if not all_pos else DARK
        triple_str = f'$({a},\\,{b},\\,{c})$'
        ax.text(bx, by, triple_str, fontsize=13, ha='center', va='center',
                color=txt_color, fontweight='bold')

        symbol = '  +  ' if all_pos else '  X  '
        sym_color = ACCENT3 if all_pos else ACCENT1
        ax.text(bx + 2.0, by, symbol, fontsize=20, ha='center', va='center',
                color=sym_color, fontweight='bold')

        ax.annotate('', xy=(bx, by + 0.6), xytext=(cx + (bx - cx)*0.2, cy - 0.6),
                    arrowprops=dict(arrowstyle='->', color=SLATE, lw=2))
        ax.text(bx, by + 1.1, label, fontsize=13, ha='center', color=ACCENT4,
                fontweight='bold')

    ax.text(7, 0.3, '"Only one door opens."', fontsize=15, ha='center', va='center',
            color=DARK, style='italic',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=GLOW, edgecolor=GOLD, linewidth=1.5))

    ax.set_xlim(-0.5, 14.5)
    ax.set_ylim(-0.3, 7)
    ax.set_title('Uniqueness of the Parent: Three Doors, One Opens',
                 fontsize=18, fontweight='bold', color=DARK, pad=15)
    save(fig, "fig07_three_doors.png")


# ============================================================
# FIG 8: Flowchart of the factoring algorithm
# ============================================================
def fig08_flowchart():
    fig, ax = plt.subplots(1, 1, figsize=(10, 14))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.axis('off')

    def draw_box(x, y, w, h, text, fc=CREAM, fs=12, shape='rect'):
        if shape == 'diamond':
            diamond = plt.Polygon([(x, y + h/2), (x + w/2, y + h),
                                    (x + w, y + h/2), (x + w/2, y)],
                                   facecolor=fc, edgecolor=DARK, linewidth=2)
            ax.add_patch(diamond)
            ax.text(x + w/2, y + h/2, text, fontsize=fs, ha='center', va='center',
                    color=DARK, fontweight='bold')
        elif shape == 'round':
            box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2",
                                 facecolor=fc, edgecolor=DARK, linewidth=2)
            ax.add_patch(box)
            ax.text(x + w/2, y + h/2, text, fontsize=fs, ha='center', va='center',
                    color=DARK, fontweight='bold')
        else:
            box = patches.Rectangle((x, y), w, h, facecolor=fc, edgecolor=DARK, linewidth=2)
            ax.add_patch(box)
            ax.text(x + w/2, y + h/2, text, fontsize=fs, ha='center', va='center',
                    color=DARK, fontweight='bold')

    y_start = 12

    draw_box(3, y_start, 4, 0.8, 'Input odd $N$', fc=LIGHT_BLUE, shape='round')
    ax.annotate('', xy=(5, y_start - 0.1), xytext=(5, y_start),
                arrowprops=dict(arrowstyle='->', color=DARK, lw=2))

    y2 = y_start - 1.6
    draw_box(1.5, y2, 7, 1.0, 'Compute trivial triple\n$(N, (N^2-1)/2, (N^2+1)/2)$',
             fc=CREAM, shape='round', fs=11)
    ax.annotate('', xy=(5, y2 - 0.1), xytext=(5, y2),
                arrowprops=dict(arrowstyle='->', color=DARK, lw=2))

    y3 = y2 - 2.2
    diamond_w, diamond_h = 6, 1.6
    diamond_x = 5 - diamond_w/2
    draw_box(diamond_x, y3, diamond_w, diamond_h,
             'gcd$(a, N)$ or gcd$(b, N)$\nnon-trivial?',
             fc=GLOW, shape='diamond', fs=11)

    y_out = y3 + diamond_h/2
    ax.annotate('', xy=(9.5, y_out), xytext=(5 + diamond_w/2, y_out),
                arrowprops=dict(arrowstyle='->', color=ACCENT3, lw=2.5))
    ax.text(8.3, y_out + 0.25, 'Yes', fontsize=12, color=ACCENT3, fontweight='bold')
    draw_box(9.5, y_out - 0.4, 3.2, 0.8, 'Output\nfactor!', fc=LIGHT_GREEN, shape='round', fs=13)

    y4 = y3 - 1.8
    ax.annotate('', xy=(5, y4 + 1.0), xytext=(5, y3),
                arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=2.5))
    ax.text(5.4, y3 - 0.4, 'No', fontsize=12, color=ACCENT1, fontweight='bold')

    draw_box(2, y4, 6, 0.9, 'Compute parent triple\nvia inverse Berggren',
             fc=CREAM, shape='round', fs=11)

    ax.text(8.5, y4 + 0.45, 'step++', fontsize=10, color=SLATE, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.2', facecolor=LIGHT_BLUE, edgecolor=SLATE))

    loop_x = 1.0
    ax.plot([loop_x, loop_x], [y4 + 0.45, y3 + diamond_h/2], color=DARK, lw=2)
    ax.annotate('', xy=(diamond_x, y3 + diamond_h/2), xytext=(loop_x, y3 + diamond_h/2),
                arrowprops=dict(arrowstyle='->', color=DARK, lw=2))

    y5 = y4 - 1.5
    ax.annotate('', xy=(5, y5 + 0.7), xytext=(5, y4),
                arrowprops=dict(arrowstyle='->', color=SLATE, lw=1.5, linestyle='dashed'))
    draw_box(1.5, y5, 7, 0.7, 'Arrived at root\n(no factor found)', fc=LIGHT_RED, shape='round', fs=10)

    ax.set_xlim(-0.5, 13.5)
    ax.set_ylim(y5 - 0.5, y_start + 1.5)
    ax.set_title('The Pythagorean Tree Factoring Algorithm',
                 fontsize=18, fontweight='bold', color=DARK, pad=15)
    save(fig, "fig08_flowchart.png")


# ============================================================
# FIG 9: Worked example N=77
# ============================================================
def fig09_worked_77():
    fig, ax = plt.subplots(1, 1, figsize=(12, 14))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.axis('off')

    N = 77
    steps = factor_via_tree(N)

    n = min(len(steps), 12)
    found_idx = None
    for i, (triple, ga, gb, found) in enumerate(steps[:n]):
        if found:
            found_idx = i
            break

    if found_idx is None:
        found_idx = n - 1

    display_steps = steps[:found_idx + 1]
    n_display = len(display_steps)

    for i, (triple, ga, gb, found) in enumerate(display_steps):
        y = i * 2.2
        a, b, c = triple

        fc = GLOW if found else CREAM
        ec = GOLD if found else DARK
        lw = 3 if found else 2

        box = FancyBboxPatch((1.5, y - 0.4), 5.5, 0.8,
                             boxstyle="round,pad=0.15", facecolor=fc,
                             edgecolor=ec, linewidth=lw)
        ax.add_patch(box)
        ax.text(4.25, y, f'$({a},\\,{b},\\,{c})$', fontsize=12, ha='center',
                va='center', color=DARK, fontweight='bold')

        ga_color = ACCENT1 if 1 < ga < N else SLATE
        gb_color = ACCENT1 if 1 < gb < N else SLATE
        ga_weight = 'bold' if 1 < ga < N else 'normal'
        gb_weight = 'bold' if 1 < gb < N else 'normal'

        ax.text(8.0, y + 0.15, f'gcd$(a, {N}) = {ga}$', fontsize=10, ha='left',
                color=ga_color, fontweight=ga_weight)
        ax.text(8.0, y - 0.15, f'gcd$(b, {N}) = {gb}$', fontsize=10, ha='left',
                color=gb_color, fontweight=gb_weight)

        if found:
            factor = ga if 1 < ga < N else gb
            ax.text(4.25, y + 0.8, f'${N} = {factor} \\times {N // factor}$, found!',
                    fontsize=14, ha='center', color=GOLD, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor=GLOW, edgecolor=GOLD, lw=2))

        if i < n_display - 1:
            ax.annotate('', xy=(4.25, (i+1)*2.2 - 0.5), xytext=(4.25, y + 0.5),
                        arrowprops=dict(arrowstyle='->', color=ACCENT4, lw=2))

    ax.set_xlim(0, 13)
    ax.set_ylim(-1, n_display * 2.2 + 0.5)
    ax.set_title(f'Factoring $N = {N}$ via Tree Descent',
                 fontsize=18, fontweight='bold', color=DARK, pad=15)
    save(fig, "fig09_worked_77.png")


# ============================================================
# FIG 10: Light cone with Pythagorean triples
# ============================================================
def fig10_light_cone():
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    theta = np.linspace(0, 2*np.pi, 80)
    z = np.linspace(0, 30, 40)
    Theta, Z = np.meshgrid(theta, z)
    X = Z * np.cos(Theta)
    Y = Z * np.sin(Theta)
    ax.plot_surface(X, Y, Z, alpha=0.08, color=ACCENT2, edgecolor='none')

    for t in np.linspace(0, 2*np.pi, 12, endpoint=False):
        ax.plot([0, 30*np.cos(t)], [0, 30*np.sin(t)], [0, 30],
                color=SLATE, alpha=0.15, linewidth=0.5)
    for zz in [5, 13, 17, 25, 29]:
        t_ring = np.linspace(0, 2*np.pi, 60)
        ax.plot(zz*np.cos(t_ring), zz*np.sin(t_ring), [zz]*60,
                color=SLATE, alpha=0.1, linewidth=0.5)

    triples = [(3,4,5), (5,12,13), (8,15,17), (15,8,17), (21,20,29), (7,24,25)]
    colors = [ACCENT1, ACCENT2, ACCENT3, ACCENT5, ACCENT4, GOLD]

    for (a, b, c), col in zip(triples, colors):
        ax.scatter([a], [b], [c], color=col, s=100, edgecolors=DARK, linewidths=1.5, zorder=10)
        ax.text(a + 1, b + 1, c + 0.5, f'$({a},{b},{c})$', fontsize=9, color=col,
                fontweight='bold')

    tree_edges = [
        ((3,4,5), (5,12,13)),
        ((3,4,5), (21,20,29)),
        ((3,4,5), (15,8,17)),
        ((5,12,13), (7,24,25)),
    ]
    for (a1,b1,c1), (a2,b2,c2) in tree_edges:
        ax.plot([a1, a2], [b1, b2], [c1, c2], color=DARK, linewidth=1.5, alpha=0.6)

    ax.set_xlabel('$a$', fontsize=14, color=DARK)
    ax.set_ylabel('$b$', fontsize=14, color=DARK)
    ax.set_zlabel('$c$', fontsize=14, color=DARK)
    ax.set_title('The Light Cone $a^2 + b^2 = c^2$\nwith Pythagorean Triples',
                 fontsize=16, fontweight='bold', color=DARK, pad=15)
    ax.view_init(elev=20, azim=35)
    save(fig, "fig10_light_cone.png")


# ============================================================
# FIG 11: Five descent ladders side by side
# ============================================================
def fig11_five_ladders():
    fig, axes = plt.subplots(1, 5, figsize=(22, 12))
    fig.set_facecolor(SAND)

    test_cases = [
        (15, '3 x 5'),
        (21, '3 x 7'),
        (77, '7 x 11'),
        (143, '11 x 13'),
        (323, '17 x 19'),
    ]

    max_steps = 0
    results = []
    for N, factstr in test_cases:
        steps = factor_via_tree(N)
        found_idx = next((i for i, (_, ga, gb, f) in enumerate(steps) if f), len(steps)-1)
        results.append((steps[:found_idx+1], found_idx+1))
        max_steps = max(max_steps, found_idx + 1)

    for col, ((display, n_disp), (N, factstr)) in enumerate(zip(results, test_cases)):
        ax = axes[col]
        ax.set_facecolor(SAND)
        ax.axis('off')

        for i, (triple, ga, gb, found) in enumerate(display):
            y = i * 2.0
            a, b, c = triple

            fc = GLOW if found else CREAM
            ec = GOLD if found else DARK
            lw = 2.5 if found else 1.5

            box = FancyBboxPatch((-0.3, y - 0.35), 4.6, 0.7,
                                 boxstyle="round,pad=0.1", facecolor=fc,
                                 edgecolor=ec, linewidth=lw)
            ax.add_patch(box)

            label = f'({a},{b},{c})'
            fsize = 6 if max(abs(a), abs(b), abs(c)) > 9999 else (7 if max(abs(a), abs(b), abs(c)) > 999 else 8)
            ax.text(2.0, y, label, fontsize=fsize, ha='center', va='center',
                    color=DARK, fontweight='bold', family='monospace')

            if found:
                ax.text(2.0, y + 0.55, f'{factstr}', fontsize=9, ha='center',
                        color=GOLD, fontweight='bold')

            if i < n_disp - 1:
                ax.annotate('', xy=(2.0, (i+1)*2.0 - 0.45), xytext=(2.0, y + 0.45),
                            arrowprops=dict(arrowstyle='->', color=ACCENT4, lw=1.5))

        ax.set_xlim(-1, 5)
        ax.set_ylim(-1, max_steps * 2.0 + 0.5)
        ax.set_title(f'$N = {N}$', fontsize=14, fontweight='bold', color=DARK)

    fig.suptitle('Five Numbers Fall Apart: Descent Ladders',
                 fontsize=20, fontweight='bold', color=DARK, y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    save(fig, "fig11_five_ladders.png")


# ============================================================
# FIG 12: Bar chart — descent steps vs N
# ============================================================
def fig12_bar_chart():
    fig, ax = plt.subplots(1, 1, figsize=(10, 7))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    test_Ns = [15, 21, 77, 143, 323]
    step_counts = []

    for N in test_Ns:
        steps = factor_via_tree(N)
        found_idx = next((i for i, (_, ga, gb, f) in enumerate(steps) if f), len(steps)-1)
        step_counts.append(found_idx + 1)

    colors_list = [ACCENT2, ACCENT3, ACCENT5, ACCENT4, ACCENT1]
    bars = ax.bar([str(n) for n in test_Ns], step_counts, color=colors_list,
                  edgecolor=DARK, linewidth=1.5, width=0.6)

    for bar, count in zip(bars, step_counts):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.15,
                str(count), ha='center', fontsize=14, fontweight='bold', color=DARK)

    x_smooth = np.linspace(0, 4, 100)
    n_smooth = np.interp(x_smooth, range(5), test_Ns)
    sqrt_curve = np.sqrt(n_smooth) * (max(step_counts) / (np.sqrt(max(test_Ns)) * 1.2))
    ax.plot(x_smooth, sqrt_curve, '--', color=SLATE, alpha=0.5, linewidth=2,
            label=r'$\sim\sqrt{N}$')
    ax.legend(fontsize=12, loc='upper left')

    ax.set_xlabel('$N$', fontsize=14, color=DARK, fontweight='bold')
    ax.set_ylabel('Number of descent steps', fontsize=14, color=DARK, fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(DARK)
    ax.spines['bottom'].set_color(DARK)
    ax.tick_params(colors=DARK, labelsize=12)
    ax.set_title('The Climb Gets Longer \u2014 But Always Ends',
                 fontsize=18, fontweight='bold', color=DARK, pad=15)
    save(fig, "fig12_bar_chart.png")


# ============================================================
# FIG 13: Grand composite image
# ============================================================
def fig13_grand_composite():
    fig, ax = plt.subplots(1, 1, figsize=(16, 16))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.axis('off')

    # Central tree (simplified)
    root = (3, 4, 5)
    ch1, ch2, ch3 = B1(*root), B2(*root), B3(*root)
    gc = []
    for ch in [ch1, ch2, ch3]:
        gc.append([B1(*ch), B2(*ch), B3(*ch)])

    tree_cx, tree_cy = 8, 10
    positions = {
        root: (tree_cx, tree_cy + 3),
        ch1: (tree_cx - 4, tree_cy),
        ch2: (tree_cx, tree_cy),
        ch3: (tree_cx + 4, tree_cy),
    }
    gc_x_offsets = [-5.5, -4, -2.5, -1, 0.5, 2, 3.5, 5, 6.5]
    idx = 0
    for i in range(3):
        for j in range(3):
            positions[gc[i][j]] = (tree_cx + gc_x_offsets[idx], tree_cy - 3)
            idx += 1

    branch_colors = [ACCENT2, ACCENT3, ACCENT1]
    for i, ch in enumerate([ch1, ch2, ch3]):
        px, py = positions[root]
        cx, cy = positions[ch]
        ax.plot([px, cx], [py - 0.3, cy + 0.3], color=branch_colors[i], lw=2, alpha=0.7)
        for j in range(3):
            gx, gy = positions[gc[i][j]]
            ax.plot([cx, gx], [cy - 0.3, gy + 0.3], color=branch_colors[j], lw=1.5, alpha=0.5)

    all_nodes = [root] + [ch1, ch2, ch3]
    for gci in gc:
        all_nodes.extend(gci)

    for triple in all_nodes:
        x, y = positions[triple]
        a, b, c = triple
        fc = GLOW if triple == root else CREAM
        fs = 9 if max(abs(a), abs(b), abs(c)) > 99 else 10
        box = FancyBboxPatch((x - 1.1, y - 0.25), 2.2, 0.5,
                             boxstyle="round,pad=0.08", facecolor=fc,
                             edgecolor=DARK, linewidth=1.2, alpha=0.9)
        ax.add_patch(box)
        ax.text(x, y, f'({a},{b},{c})', fontsize=fs, ha='center', va='center',
                color=DARK, fontweight='bold', family='monospace')

    # Translucent cone rings
    cone_cx, cone_cy = 8, 9.5
    for r in np.linspace(0.5, 7, 8):
        circle = plt.Circle((cone_cx, cone_cy), r, fill=False, color=ACCENT2,
                            alpha=0.04, linewidth=1)
        ax.add_patch(circle)

    # Upper left: right triangle
    tri_x0, tri_y0 = 0.5, 14.5
    tri_sc = 1.8
    ax.plot([tri_x0, tri_x0 + tri_sc, tri_x0, tri_x0],
            [tri_y0, tri_y0, tri_y0 + tri_sc * 0.6, tri_y0],
            color=DARK, linewidth=2.5)
    ax.fill([tri_x0, tri_x0 + tri_sc, tri_x0],
            [tri_y0, tri_y0, tri_y0 + tri_sc * 0.6], alpha=0.1, color=ACCENT2)
    ax.text(tri_x0 + tri_sc/2, tri_y0 - 0.25, r'$(N^2-1)/2$', fontsize=10,
            ha='center', color=ACCENT2, fontweight='bold')
    ax.text(tri_x0 - 0.3, tri_y0 + tri_sc * 0.3, '$N$', fontsize=12,
            ha='center', color=ACCENT1, fontweight='bold')

    # Upper right: mini flowchart
    fc_x, fc_y = 13, 15
    mini_labels = ['Input $N$', 'Trivial triple', 'GCD check', 'Factor!']
    for i, lbl in enumerate(mini_labels):
        yy = fc_y - i * 0.7
        fc_color = LIGHT_GREEN if i == 3 else CREAM
        box = FancyBboxPatch((fc_x - 1.2, yy - 0.2), 2.4, 0.4,
                             boxstyle="round,pad=0.05", facecolor=fc_color,
                             edgecolor=DARK, linewidth=1)
        ax.add_patch(box)
        ax.text(fc_x, yy, lbl, fontsize=8, ha='center', va='center', color=DARK)
        if i < 3:
            ax.annotate('', xy=(fc_x, yy - 0.25), xytext=(fc_x, yy - 0.5),
                        arrowprops=dict(arrowstyle='->', color=DARK, lw=1))

    # Bottom: locked box with 10,403
    box_x, box_y = 6.5, 3.5
    bw, bh = 3, 1.5
    box_patch = FancyBboxPatch((box_x, box_y), bw, bh,
                                boxstyle="round,pad=0.3", facecolor='#8B7355',
                                edgecolor=DARK, linewidth=3)
    ax.add_patch(box_patch)
    ax.text(box_x + bw/2, box_y + bh/2 + 0.2, '$10403$', fontsize=22,
            ha='center', va='center', color=CREAM, fontweight='bold')
    ax.text(box_x + bw/2, box_y + bh/2 - 0.3, 'Can you crack it?', fontsize=11,
            ha='center', va='center', color=GLOW, style='italic')

    # Triangle keyhole
    kx, ky = box_x + bw/2, box_y - 0.1
    ax.plot([kx - 0.15, kx + 0.15, kx, kx - 0.15],
            [ky, ky, ky + 0.25, ky], color=GOLD, linewidth=2)

    ax.set_xlim(-0.5, 16.5)
    ax.set_ylim(2.5, 16.5)
    ax.set_title('The Tree That Cracks Numbers \u2014 A Grand View',
                 fontsize=22, fontweight='bold', color=DARK, pad=20)
    save(fig, "fig13_grand_composite.png")


# ============================================================
# FIG 14: Map of the book — Chapter 14 as hub
# ============================================================
def fig14_book_map():
    fig, ax = plt.subplots(1, 1, figsize=(14, 14))
    fig.set_facecolor('#E8DCC8')
    ax.set_facecolor('#E8DCC8')
    ax.axis('off')

    center = (7, 7)
    island_r = 1.8
    circle = plt.Circle(center, island_r, facecolor=GLOW, edgecolor=DARK,
                        linewidth=3, alpha=0.8)
    ax.add_patch(circle)
    ax.text(center[0], center[1] + 0.3, 'Chapter 14', fontsize=18, ha='center',
            va='center', color=DARK, fontweight='bold')
    ax.text(center[0], center[1] - 0.3, 'The Tree That\nCracks Numbers', fontsize=11,
            ha='center', va='center', color=DARK, style='italic')

    neighbors = [
        (2, 11, 'Ch. 2', 'Lattice\nReduction', LIGHT_BLUE, 'Lattice-Tree\nCorrespondence'),
        (12, 11, 'Ch. 3', 'Hyperbolic\nShortcuts', LIGHT_GREEN, 'Geodesics &\nMatrix Exp.'),
        (1.5, 3.5, 'Ch. 6', '$k$-Tuples', '#D5B8FF', 'Higher\nDimensions'),
        (12.5, 3.5, 'Ch. 7', 'Quantum\nSpeedup', LIGHT_RED, 'Grover\nAcceleration'),
        (7, 13, 'Ch. 8', 'Complexity\nBounds', '#FDEBD0', r'$\Theta(\sqrt{N})$'),
    ]

    for nx, ny, ch_label, desc, color, bridge_label in neighbors:
        r = 1.2
        island = plt.Circle((nx, ny), r, facecolor=color, edgecolor=DARK,
                            linewidth=2, alpha=0.7)
        ax.add_patch(island)
        ax.text(nx, ny + 0.25, ch_label, fontsize=14, ha='center', va='center',
                color=DARK, fontweight='bold')
        ax.text(nx, ny - 0.25, desc, fontsize=9, ha='center', va='center',
                color=DARK, style='italic')

        dx = nx - center[0]
        dy = ny - center[1]
        dist = sqrt(dx**2 + dy**2)
        ux, uy = dx/dist, dy/dist

        start_x = center[0] + ux * island_r
        start_y = center[1] + uy * island_r
        end_x = nx - ux * r
        end_y = ny - uy * r

        ax.plot([start_x, end_x], [start_y, end_y], color=DARK, linewidth=2.5,
                alpha=0.5, linestyle='-')

        mx = (start_x + end_x) / 2
        my = (start_y + end_y) / 2
        angle = np.degrees(np.arctan2(dy, dx))
        ax.text(mx, my, bridge_label, fontsize=8, ha='center', va='center',
                color=ACCENT4, fontweight='bold', rotation=angle if abs(angle) < 80 else 0,
                bbox=dict(boxstyle='round,pad=0.15', facecolor='#E8DCC8',
                          edgecolor='none', alpha=0.9))

    ax.text(10, 8.5, 'Here be\nsemiprimes', fontsize=10, ha='center', color=SLATE,
            style='italic', alpha=0.5)
    ax.text(3.5, 6.5, 'Uncharted\nquadruples', fontsize=10, ha='center', color=SLATE,
            style='italic', alpha=0.5)

    # Compass rose
    comp_x, comp_y = 12.5, 0.8
    ax.text(comp_x, comp_y + 0.7, 'Geometry', fontsize=8, ha='center', color=DARK)
    ax.text(comp_x, comp_y - 0.7, 'Computation', fontsize=8, ha='center', color=DARK)
    ax.text(comp_x - 1.0, comp_y, 'Algebra', fontsize=8, ha='center', color=DARK)
    ax.text(comp_x + 1.0, comp_y, 'Physics', fontsize=8, ha='center', color=DARK)
    ax.plot([comp_x, comp_x], [comp_cy := comp_y - 0.4, comp_y + 0.4], color=DARK, lw=1.5)
    ax.plot([comp_x - 0.5, comp_x + 0.5], [comp_y, comp_y], color=DARK, lw=1.5)
    compass = plt.Circle((comp_x, comp_y), 0.1, facecolor=ACCENT1, edgecolor=DARK, lw=1)
    ax.add_patch(compass)

    ax.set_xlim(-0.5, 14.5)
    ax.set_ylim(-0.5, 14.5)
    ax.set_title('A Map of the Book: Chapter 14 and Its Neighbors',
                 fontsize=20, fontweight='bold', color=DARK, pad=20)
    save(fig, "fig14_book_map.png")


# ============================================================
# Run all
# ============================================================
if __name__ == '__main__':
    print("Generating Chapter 14 illustrations...")
    fig01_trivial_triple()
    fig02_crowbar()
    fig03_berggren_tree()
    fig04_reverse_climb()
    fig05_descent_ladder()
    fig06_hypotenuse_staircase()
    fig07_three_doors()
    fig08_flowchart()
    fig09_worked_77()
    fig10_light_cone()
    fig11_five_ladders()
    fig12_bar_chart()
    fig13_grand_composite()
    fig14_book_map()
    print("Done! All images saved to Chapter14/images/")

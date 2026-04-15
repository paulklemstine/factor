#!/usr/bin/env python3
"""Generate all illustrations for Chapter 16: The Relativistic Secret of Right Triangles."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe
import numpy as np
import os
from math import gcd
from collections import deque

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

BRANCH_COLORS = [ACCENT2, ACCENT1, GOLD]  # A=blue, B=red, C=gold

def save(fig, name, dpi=200):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=dpi, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  Saved {name}")


# Berggren matrices
A_mat = np.array([[1, -2, 2], [2, -1, 2], [2, -2, 3]])
B_mat = np.array([[1, 2, 2], [2, 1, 2], [2, 2, 3]])
C_mat = np.array([[-1, 2, 2], [-2, 1, 2], [-2, 2, 3]])
MATS = [A_mat, B_mat, C_mat]

def berggren_children(triple):
    v = np.array(triple)
    return tuple(A_mat @ v), tuple(B_mat @ v), tuple(C_mat @ v)

def Q(a, b, c):
    return a*a + b*b - c*c

def triple_to_disk(t):
    a, b, c = t
    scale = 1 - 1.0 / (1 + 0.02 * c)
    angle = np.arctan2(b, a)
    return scale * np.cos(angle), scale * np.sin(angle)


# ============================================================
# FIG 1: Magic-box Q-invariance diagram
# ============================================================
def fig01_magic_box():
    fig, ax = plt.subplots(1, 1, figsize=(14, 7))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    labels = ['$A$', '$B$', '$C$']
    colors = [ACCENT2, ACCENT1, GOLD]
    example = (2, 3, 4)
    q_val = Q(*example)

    for i, (lab, mat, col) in enumerate(zip(labels, MATS, colors)):
        cx = 2 + i * 4.5
        cy = 3.5

        # Machine box
        box = FancyBboxPatch((cx - 1.2, cy - 1.5), 2.4, 3.0,
                             boxstyle="round,pad=0.15", facecolor=CREAM,
                             edgecolor=DARK, linewidth=2.5)
        ax.add_patch(box)
        ax.text(cx, cy + 1.8, lab, fontsize=22, ha='center', va='center',
                fontweight='bold', color=col)

        # Input
        ax.annotate('', xy=(cx, cy + 1.2), xytext=(cx, cy + 2.8),
                    arrowprops=dict(arrowstyle='->', color=DARK, lw=2))
        ax.text(cx, cy + 3.1, f'$({example[0]}, {example[1]}, {example[2]})$',
                fontsize=13, ha='center', va='center', color=DARK)

        # Output
        out = tuple((mat @ np.array(example)).astype(int))
        ax.annotate('', xy=(cx, cy - 2.5), xytext=(cx, cy - 1.7),
                    arrowprops=dict(arrowstyle='->', color=DARK, lw=2))
        ax.text(cx, cy - 2.9, f'$({out[0]}, {out[1]}, {out[2]})$',
                fontsize=13, ha='center', va='center', color=DARK)

        # Gear decorations
        for gx, gy, r in [(cx-0.6, cy+0.3, 0.25), (cx+0.5, cy-0.2, 0.2), (cx-0.2, cy-0.7, 0.15)]:
            ax.add_patch(plt.Circle((gx, gy), r, fill=False, edgecolor=col, linewidth=1.5, linestyle='--'))

        # Q meter
        mx, my = cx + 1.6, cy
        ax.add_patch(plt.Circle((mx, my), 0.45, facecolor=GLOW, edgecolor=DARK, linewidth=2, alpha=0.9))
        ax.text(mx, my + 0.15, '$Q$', fontsize=10, ha='center', va='center', fontweight='bold', color=DARK)
        ax.text(mx, my - 0.18, f'${q_val}$', fontsize=12, ha='center', va='center', fontweight='bold', color=ACCENT1)

    ax.set_xlim(-0.5, 14.5)
    ax.set_ylim(-0.5, 7.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('The Form That Remembers: $Q = a^2 + b^2 - c^2$ is invariant',
                 fontsize=16, color=DARK, pad=15)
    save(fig, 'fig01_magic_box.png')


# ============================================================
# FIG 2: Table of 5 numerical examples
# ============================================================
def fig02_q_table():
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    examples = [(1,0,0), (3,4,5), (2,3,4), (0,0,7), (-1,5,3)]
    col_labels = ['Original $(a,b,c)$', '$Q$', 'Transformed $(a\',b\',c\')$', "$Q'$"]
    rows = []
    for ex in examples:
        q = Q(*ex)
        out = tuple((A_mat @ np.array(ex)).astype(int))
        q2 = Q(*out)
        rows.append([f'$({ex[0]},\\;{ex[1]},\\;{ex[2]})$', f'${q}$',
                      f'$({out[0]},\\;{out[1]},\\;{out[2]})$', f'${q2}$'])

    table = ax.table(cellText=rows, colLabels=col_labels, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(13)
    table.scale(1.0, 2.2)
    for (r, c), cell in table.get_celld().items():
        cell.set_edgecolor(DARK)
        if r == 0:
            cell.set_facecolor(SLATE)
            cell.set_text_props(color='white', fontweight='bold')
        else:
            cell.set_facecolor(CREAM if r % 2 == 1 else '#FFF8EE')
            cell.set_text_props(color=DARK)
    ax.axis('off')
    ax.set_title('Five examples confirming $Q(a,b,c) = Q(a\',b\',c\')$ under matrix $A$',
                 fontsize=15, color=DARK, pad=20)
    save(fig, 'fig02_q_table.png')


# ============================================================
# FIG 3: 3D null cone
# ============================================================
def fig03_null_cone():
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    theta = np.linspace(0, 2*np.pi, 80)
    c_vals = np.linspace(0, 30, 40)
    Theta, C = np.meshgrid(theta, c_vals)
    ax.plot_surface(C*np.cos(Theta), C*np.sin(Theta), C, alpha=0.15, color=ACCENT2, edgecolor='none')

    triples = [(3,4,5),(5,12,13),(8,15,17),(7,24,25),(20,21,29),(9,40,41),(12,35,37)]
    for a,b,c in triples:
        ax.scatter([a],[b],[c], color=GOLD, s=80, edgecolors=DARK, linewidths=1, zorder=10, depthshade=False)
    for a,b,c in [(3,4,5),(5,12,13),(8,15,17),(7,24,25)]:
        ax.text(a+1, b+1, c+0.5, f'({a},{b},{c})', fontsize=8, color=DARK)

    ax.set_xlabel('$a$', fontsize=14, color=DARK)
    ax.set_ylabel('$b$', fontsize=14, color=DARK)
    ax.set_zlabel('$c$', fontsize=14, color=DARK)
    ax.set_title('The Null Cone $a^2 + b^2 = c^2$\nwith Pythagorean lattice points',
                 fontsize=14, color=DARK, pad=15)
    ax.view_init(elev=25, azim=35)
    ax.set_xlim(-5, 30); ax.set_ylim(-5, 45); ax.set_zlim(0, 45)
    save(fig, 'fig03_null_cone.png')


# ============================================================
# FIG 4: Berggren tree — first 4 levels
# ============================================================
def fig04_berggren_tree():
    fig, ax = plt.subplots(1, 1, figsize=(18, 12))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    root = (3, 4, 5)
    levels = 4
    level_nodes = {0: [root]}
    children_map = {}
    for lev in range(levels - 1):
        level_nodes[lev + 1] = []
        for parent in level_nodes[lev]:
            kids = berggren_children(parent)
            children_map[parent] = kids
            for k in kids:
                level_nodes[lev + 1].append(k)

    positions = {}
    y_positions = {0: 10, 1: 7, 2: 4, 3: 1}
    for lev in range(levels):
        nn = len(level_nodes[lev])
        for i, node in enumerate(level_nodes[lev]):
            x = 1 + (i + 0.5) * 16 / nn
            positions[node] = (x, y_positions[lev])

    for parent, kids in children_map.items():
        px, py = positions[parent]
        for i, kid in enumerate(kids):
            kx, ky = positions[kid]
            ax.plot([px, kx], [py, ky], color=BRANCH_COLORS[i], linewidth=1.5, alpha=0.7, zorder=1)
            if parent == root:
                mx, my = (px+kx)/2, (py+ky)/2
                ax.text(mx-0.1, my+0.3, ['$A$','$B$','$C$'][i], fontsize=11,
                        color=BRANCH_COLORS[i], fontweight='bold', ha='center')

    for node in positions:
        x, y = positions[node]
        lev = next(l for l in range(levels) if node in level_nodes[l])
        r = 0.7 if lev < 2 else 0.5 if lev < 3 else 0.35
        ax.add_patch(plt.Circle((x, y), r, facecolor=CREAM, edgecolor=DARK, linewidth=1.5, zorder=5))
        a, b, c = node
        fs = 9 if lev < 2 else 7 if lev < 3 else 5.5
        ax.text(x, y, f'({a},{b},{c})', fontsize=fs, ha='center', va='center', color=DARK, zorder=6)

    ax.set_xlim(-0.5, 18.5); ax.set_ylim(-0.5, 12)
    ax.set_aspect('equal'); ax.axis('off')
    ax.set_title('The Berggren Tree: Every Primitive Pythagorean Triple Appears Exactly Once',
                 fontsize=15, color=DARK, pad=15)
    for i, (lab, col) in enumerate(zip(['$A$-branch','$B$-branch','$C$-branch'], BRANCH_COLORS)):
        ax.plot([], [], color=col, linewidth=3, label=lab)
    ax.legend(loc='upper right', fontsize=12, framealpha=0.8)
    save(fig, 'fig04_berggren_tree.png')


# ============================================================
# FIG 5: Side-by-side Minkowski + Poincaré disk
# ============================================================
def fig05_minkowski_poincare():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    fig.set_facecolor(SAND)

    # LEFT: Minkowski
    ax1.set_facecolor(SAND)
    t = np.linspace(-4, 4, 100)
    ax1.plot(t, t, '--', color=GOLD, linewidth=2.5)
    ax1.plot(t, -t, '--', color=GOLD, linewidth=2.5)
    ax1.fill_between(t, np.abs(t), 4, color=ACCENT2, alpha=0.12)
    ax1.fill_between(t, -4, -np.abs(t), color=ACCENT2, alpha=0.12)
    ax1.text(0, 3, 'Timelike\n($Q < 0$)', fontsize=11, ha='center', color=ACCENT2, fontweight='bold')
    ax1.fill_between(t, -np.abs(t), np.abs(t), color=ACCENT1, alpha=0.08)
    ax1.text(2.5, 0.3, 'Spacelike\n($Q > 0$)', fontsize=10, ha='center', color=ACCENT1, fontweight='bold')
    s = np.linspace(-3, 3, 200)
    ax1.plot(np.sinh(s), np.cosh(s), color=ACCENT4, linewidth=1.5, alpha=0.6)
    ax1.plot(0.5, 2, 'o', color=ACCENT1, markersize=10, zorder=10)
    ax1.plot(1.5, 2.8, 'o', color=ACCENT1, markersize=10, zorder=10)
    ax1.annotate('', xy=(1.5, 2.8), xytext=(0.5, 2),
                 arrowprops=dict(arrowstyle='->', color=ACCENT3, lw=2.5))
    ax1.text(1.3, 2.1, 'Lorentz\nboost', fontsize=10, color=ACCENT3, fontweight='bold')
    ax1.set_xlim(-4, 4); ax1.set_ylim(-4, 4)
    ax1.set_xlabel('$x$', fontsize=14); ax1.set_ylabel('$t$', fontsize=14)
    ax1.axhline(0, color=DARK, linewidth=0.5, alpha=0.3)
    ax1.axvline(0, color=DARK, linewidth=0.5, alpha=0.3)
    ax1.set_title('Minkowski Spacetime', fontsize=14, color=DARK)
    ax1.set_aspect('equal')

    # RIGHT: Poincaré disk
    ax2.set_facecolor(SAND)
    ax2.add_patch(plt.Circle((0, 0), 1, facecolor='white', edgecolor=DARK, linewidth=2))

    # Build tree triples
    all_triples = [(3,4,5)]
    level_t = [(3,4,5)]
    parent_map = {}
    for _ in range(3):
        new_level = []
        for t_node in level_t:
            kids = berggren_children(t_node)
            for i, kid in enumerate(kids):
                parent_map[kid] = (t_node, i)
            new_level.extend(kids)
        all_triples.extend(new_level)
        level_t = new_level

    for t_node in all_triples:
        px, py = triple_to_disk(t_node)
        ms = max(3, 12 - 0.1 * t_node[2])
        ax2.plot(px, py, 'o', color=ACCENT2, markersize=ms, markeredgecolor=DARK, markeredgewidth=0.5, zorder=5)
        if t_node[2] <= 29:
            ax2.text(px + 0.03, py + 0.03, f'({t_node[0]},{t_node[1]},{t_node[2]})', fontsize=6, color=DARK)

    for child, (parent, bi) in parent_map.items():
        p1 = triple_to_disk(parent)
        p2 = triple_to_disk(child)
        ax2.plot([p1[0], p2[0]], [p1[1], p2[1]], color=BRANCH_COLORS[bi], linewidth=0.8, alpha=0.5, zorder=2)

    ax2.set_xlim(-1.3, 1.3); ax2.set_ylim(-1.3, 1.3)
    ax2.set_aspect('equal'); ax2.axis('off')
    ax2.set_title('Berggren Tree on the Poincaré Disk', fontsize=14, color=DARK)

    fig.suptitle('"The same group acts on both pictures"', fontsize=16, color=DARK, style='italic', y=0.02)
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    save(fig, 'fig05_minkowski_poincare.png')


# ============================================================
# FIG 6: Elevator descent diagram
# ============================================================
def fig06_elevator_descent():
    fig, ax = plt.subplots(1, 1, figsize=(8, 14))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    # Compute inverses properly
    inv_mats = [(f'$A^{{-1}}$', np.round(np.linalg.inv(A_mat)).astype(int)),
                (f'$B^{{-1}}$', np.round(np.linalg.inv(B_mat)).astype(int)),
                (f'$C^{{-1}}$', np.round(np.linalg.inv(C_mat)).astype(int))]

    def descend(triple):
        v = np.array(triple, dtype=int)
        for name, inv in inv_mats:
            result = inv @ v
            if all(r > 0 for r in result) and result[2] < v[2]:
                return tuple(result), name
        return None, None

    path = [(697, 696, 985)]
    labels = []
    current = (697, 696, 985)
    for _ in range(20):
        if current == (3, 4, 5):
            break
        nxt, op = descend(current)
        if nxt is None:
            break
        labels.append(op)
        path.append(nxt)
        current = nxt

    n = len(path)
    for i, triple in enumerate(path):
        y = (n - 1 - i) * 2
        x = 3
        box = FancyBboxPatch((x-2, y-0.6), 4, 1.2, boxstyle="round,pad=0.1",
                             facecolor=CREAM if i < n-1 else LIGHT_GREEN,
                             edgecolor=DARK, linewidth=2)
        ax.add_patch(box)
        a, b, c = triple
        ax.text(x, y+0.15, f'$({a},\\;{b},\\;{c})$', fontsize=12,
                ha='center', va='center', color=DARK, fontweight='bold')
        ax.text(x, y-0.25, f'hyp $= {c}$', fontsize=9, ha='center', va='center', color=SLATE)
        if i < n - 1:
            ax.annotate('', xy=(x, y-0.7), xytext=(x, y-1.3),
                        arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=2))
            if i < len(labels):
                ax.text(x+2.3, y-1.0, labels[i], fontsize=10, ha='center', va='center',
                        color=ACCENT1, fontweight='bold')

    ax.text(3, -0.8, '\u2691', fontsize=24, ha='center', va='center')
    ax.set_xlim(-1, 7); ax.set_ylim(-1.5, n*2+0.5)
    ax.set_aspect('equal'); ax.axis('off')
    ax.set_title('Descent to the Root: Tracing the Berggren Address',
                 fontsize=14, color=DARK, pad=15)
    save(fig, 'fig06_elevator_descent.png')


# ============================================================
# FIG 7: A-highway — leftmost branch
# ============================================================
def fig07_a_highway():
    fig, ax = plt.subplots(1, 1, figsize=(16, 6))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    current = np.array([3, 4, 5])
    nodes = [tuple(current)]
    mn_params = [(2, 1)]
    for i in range(7):
        current = A_mat @ current
        nodes.append(tuple(current))
        mn_params.append((i+3, i+2))

    n = len(nodes)
    for i in range(n):
        x = i * 2
        y = 3
        scale = 1.0 / (1 + 0.08 * i)
        post_h = 2.5 * scale
        ax.plot([x, x], [y - 0.5*scale, y + post_h], color=DARK, linewidth=2*scale+0.5)

        sign_w, sign_h = 1.8*scale, 1.2*scale
        ax.add_patch(FancyBboxPatch((x-sign_w/2, y+post_h-sign_h/2), sign_w, sign_h,
                                     boxstyle="round,pad=0.05", facecolor='white',
                                     edgecolor=DARK, linewidth=1.5*scale+0.3))
        a, b, c = [int(v) for v in nodes[i]]
        fs = max(5, int(10*scale))
        ax.text(x, y+post_h+0.05, f'({a},{b},{c})', fontsize=fs,
                ha='center', va='center', color=DARK, fontweight='bold')
        m, nn = mn_params[i]
        ax.text(x, y+post_h-0.35*scale, f'$(m,n)=({m},{nn})$', fontsize=max(4, int(7*scale)),
                ha='center', va='center', color=ACCENT4)

        if i < n-1:
            ax.plot([x+0.3, (i+1)*2-0.3], [y-0.3, y-0.3],
                    color=SLATE, linewidth=3*scale, solid_capstyle='round')
        if i < n-1 and i < 4:
            ax.annotate('', xy=(x+0.8, y+0.5), xytext=(x+0.2, y),
                        arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=1, alpha=0.4))
            ax.text(x+1.0, y+0.7, '$B$', fontsize=7, color=ACCENT1, alpha=0.5)
            ax.annotate('', xy=(x+0.8, y-1.0), xytext=(x+0.2, y-0.5),
                        arrowprops=dict(arrowstyle='->', color=GOLD, lw=1, alpha=0.4))
            ax.text(x+1.0, y-1.2, '$C$', fontsize=7, color=GOLD, alpha=0.5)

    ax.text(n*2-0.5, 3, r'$\cdots$', fontsize=20, ha='center', va='center', color=DARK)
    ax.set_xlim(-1, n*2+1); ax.set_ylim(0.5, 7)
    ax.set_aspect('equal'); ax.axis('off')
    ax.set_title('The $A$-Highway: The Leftmost Branch at Every Generation',
                 fontsize=15, color=DARK, pad=10)
    save(fig, 'fig07_a_highway.png')


# ============================================================
# FIG 8: Prime depth staircase
# ============================================================
def fig08_prime_depth():
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    primes_1mod4 = [5, 13, 17, 29, 37, 41, 53, 61, 73, 89, 97]

    def find_depth(target_c):
        queue = deque([((3,4,5), 1)])
        visited = set()
        while queue:
            triple, depth = queue.popleft()
            a, b, c = triple
            if c == target_c:
                return depth
            if c > target_c * 2 or depth > 30:
                continue
            if triple in visited:
                continue
            visited.add(triple)
            for kid in berggren_children(triple):
                if all(k > 0 for k in kid):
                    queue.append((kid, depth + 1))
        return None

    depths, valid_primes = [], []
    for p in primes_1mod4:
        d = find_depth(p)
        if d is not None:
            depths.append(d)
            valid_primes.append(p)

    for i, (p, d) in enumerate(zip(valid_primes, depths)):
        ax.plot([0, d], [p, p], color=ACCENT2, linewidth=2, alpha=0.7)
        ax.plot(0, p, 's', color=ACCENT1, markersize=8, zorder=5)
        ax.plot(d, p, 'o', color=ACCENT3, markersize=8, zorder=5)
        ax.text(-1.5, p, f'${p}$', fontsize=11, ha='center', va='center', color=DARK, fontweight='bold')
        ax.text(d+0.5, p, f'{d}', fontsize=10, ha='left', va='center', color=ACCENT3)

    if len(valid_primes) > 2:
        coeffs = np.polyfit(valid_primes, depths, 1)
        p_range = np.linspace(min(valid_primes)-2, max(valid_primes)+5, 100)
        ax.plot(np.polyval(coeffs, p_range), p_range, '--', color=ACCENT4, linewidth=2,
                label=f'Linear fit: slope \u2248 {coeffs[0]:.2f}', alpha=0.7)

    ax.set_xlabel('Berggren Tree Depth', fontsize=13, color=DARK)
    ax.set_ylabel('Prime Hypotenuse $p$', fontsize=13, color=DARK)
    ax.set_title('Prime Hypotenuses and Their Berggren Tree Depth', fontsize=15, color=DARK, pad=15)
    ax.legend(fontsize=11, framealpha=0.8)
    ax.grid(True, alpha=0.2)
    save(fig, 'fig08_prime_depth.png')


# ============================================================
# FIG 9: Factor-pair table for leg = 15 (225 = d × e)
# ============================================================
def fig09_factor_table():
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    factor_pairs = [(1, 225), (3, 75), (5, 45), (9, 25)]
    triples_data = []
    for d, e in factor_pairs:
        a = (e - d) // 2
        c = (e + d) // 2
        b = 15
        g = gcd(gcd(a, b), c)
        triples_data.append(((b, a, c), g == 1, g))

    col_labels = ['$d$', '$e = 225/d$', 'Triple $(a, b, c)$', 'Type']
    rows = []
    for (d, e), ((b, a, c), is_prim, g) in zip(factor_pairs, triples_data):
        prim_label = 'Primitive' if is_prim else f'$\\times {g}$'
        rows.append([f'${d}$', f'${e}$', f'$({b},\\;{a},\\;{c})$', prim_label])

    table = ax.table(cellText=rows, colLabels=col_labels, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(14)
    table.scale(1.0, 2.5)
    for (r, ci), cell in table.get_celld().items():
        cell.set_edgecolor(DARK)
        if r == 0:
            cell.set_facecolor(SLATE)
            cell.set_text_props(color='white', fontweight='bold')
        else:
            is_prim = triples_data[r-1][1]
            cell.set_facecolor(CREAM if is_prim else '#F0E0D0')
            cell.set_text_props(color=DARK, fontweight='bold' if is_prim else 'normal')
    ax.axis('off')
    ax.set_title('Factoring $225 = d \\times e$: Four Pythagorean Triples with Leg $15$',
                 fontsize=15, color=DARK, pad=20)
    save(fig, 'fig09_factor_table.png')


# ============================================================
# FIG 10: Bar chart |T(N)| for k distinct odd prime factors
# ============================================================
def fig10_triple_count():
    fig, ax = plt.subplots(1, 1, figsize=(10, 7))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    ks = [1, 2, 3, 4, 5]
    counts = [(3**k - 1) // 2 for k in ks]
    bar_colors = [ACCENT2, ACCENT1, ACCENT3, ACCENT4, ACCENT5]
    bars = ax.bar(ks, counts, color=bar_colors, edgecolor=DARK, linewidth=1.5, width=0.6, zorder=3)

    for bar, count in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height()+2,
                f'{count}', fontsize=14, ha='center', va='bottom', color=DARK, fontweight='bold')

    k_smooth = np.linspace(0.5, 5.5, 100)
    ax.plot(k_smooth, (3**k_smooth - 1)/2, '--', color=ACCENT4, linewidth=2, alpha=0.7,
            label='$y = (3^k - 1)/2$')

    for bar, count in zip(bars, counts):
        n_tri = min(count, 8)
        bx, bw, bh = bar.get_x(), bar.get_width(), bar.get_height()
        for j in range(n_tri):
            ty = bh * (j + 0.5) / n_tri
            tx = bx + bw / 2
            s = 0.06
            ax.plot([tx-s, tx+s, tx, tx-s], [ty-s, ty-s, ty+s, ty-s],
                    color='white', linewidth=0.8, alpha=0.4)

    ax.set_xlabel('$k$ = number of distinct odd prime factors', fontsize=13, color=DARK)
    ax.set_ylabel('$|T(N)|$ = number of Pythagorean triples', fontsize=13, color=DARK)
    ax.set_title('Exponential Growth of Pythagorean Triple Count', fontsize=15, color=DARK, pad=15)
    ax.set_xticks(ks)
    ax.legend(fontsize=12, framealpha=0.8)
    ax.grid(True, alpha=0.2, axis='y')
    save(fig, 'fig10_triple_count.png')


# ============================================================
# FIG 11: Poincaré disk tessellation (Escher-style)
# ============================================================
def fig11_poincare_tessellation():
    fig, ax = plt.subplots(1, 1, figsize=(12, 12))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.add_patch(plt.Circle((0, 0), 1, facecolor='#FFFEF5', edgecolor=DARK, linewidth=3))

    def draw_subtree(triple, depth, angle_offset, angle_span, max_depth, parent_pos=None, branch_idx=0):
        if depth > max_depth:
            return
        r = 1 - 1.0 / (1 + 0.6 * depth)
        angle = angle_offset + angle_span / 2
        x, y = r * np.cos(angle), r * np.sin(angle)
        r_size = max(0.03, 0.15 / (1 + 0.5 * depth))
        tile_color = BRANCH_COLORS[branch_idx % 3] if depth > 0 else ACCENT3
        ax.add_patch(plt.Circle((x, y), r_size, facecolor=tile_color, edgecolor=DARK,
                                 linewidth=max(0.3, 1.5-0.2*depth), alpha=0.7))
        a, b, c = triple
        fs = max(3, 9 - depth * 1.2)
        if depth <= 3:
            ax.text(x, y, f'({a},{b},{c})', fontsize=fs, ha='center', va='center',
                    color='white' if depth > 0 else DARK, fontweight='bold', zorder=10)
        if parent_pos is not None:
            ax.plot([parent_pos[0], x], [parent_pos[1], y],
                    color=tile_color, linewidth=max(0.3, 1.5-0.15*depth), alpha=0.5, zorder=1)
        children = berggren_children(triple)
        child_span = angle_span / 3
        for i, child in enumerate(children):
            draw_subtree(child, depth+1, angle_offset + i*child_span, child_span,
                         max_depth, parent_pos=(x, y), branch_idx=i)

    draw_subtree((3,4,5), 0, 0, 2*np.pi, 5)

    ax.set_xlim(-1.15, 1.15); ax.set_ylim(-1.15, 1.15)
    ax.set_aspect('equal'); ax.axis('off')
    ax.set_title('Berggren Tree Tessellation of the Poincaré Disk', fontsize=16, color=DARK, pad=15)
    for lab, col in zip(['$A$-branch (blue)','$B$-branch (red)','$C$-branch (gold)'], BRANCH_COLORS):
        ax.plot([], [], 'o', color=col, markersize=10, label=lab)
    ax.legend(loc='lower right', fontsize=11, framealpha=0.8)
    save(fig, 'fig11_poincare_tessellation.png')


# ============================================================
# FIG 12: Grand Diagram — four-quadrant overview
# ============================================================
def fig12_grand_diagram():
    fig, axes = plt.subplots(2, 2, figsize=(16, 16))
    fig.set_facecolor(SAND)
    fig.suptitle('One Equation, Four Worlds', fontsize=20, color=DARK, fontweight='bold', y=0.98)

    fig.text(0.5, 0.5, '$a^2 + b^2 = c^2$', fontsize=28, ha='center', va='center',
             color=DARK, fontweight='bold', style='italic',
             bbox=dict(boxstyle='round,pad=0.3', facecolor=GLOW, edgecolor=DARK, linewidth=2),
             zorder=100, transform=fig.transFigure)

    # NORTH: Berggren tree
    ax = axes[0, 0]
    ax.set_facecolor(SAND)
    def draw_mini_tree(ax, triple, depth, x, y, x_spread, max_d):
        if depth > max_d:
            return
        r = max(0.15, 0.4 - 0.08 * depth)
        ax.add_patch(plt.Circle((x, y), r, facecolor=CREAM, edgecolor=DARK, linewidth=1, zorder=5))
        a, b, c = triple
        ax.text(x, y, f'{a},{b},{c}', fontsize=max(4, 8-depth), ha='center', va='center', color=DARK, zorder=6)
        if depth < max_d:
            for i, child in enumerate(berggren_children(triple)):
                cx_pos = x + (i-1) * x_spread
                cy_pos = y - 1.5
                ax.plot([x, cx_pos], [y-r, cy_pos+r], color=BRANCH_COLORS[i], linewidth=1, alpha=0.7)
                draw_mini_tree(ax, child, depth+1, cx_pos, cy_pos, x_spread/3, max_d)
    draw_mini_tree(ax, (3,4,5), 0, 3, 5, 2.5, 2)
    ax.set_xlim(-2, 8); ax.set_ylim(-1, 7); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title('NORTH: The Berggren Tree', fontsize=13, color=DARK, fontweight='bold')

    # EAST: Minkowski light cone
    ax = axes[0, 1]
    ax.set_facecolor(SAND)
    t = np.linspace(-3, 3, 100)
    ax.plot(t, t, '--', color=GOLD, linewidth=2)
    ax.plot(t, -t, '--', color=GOLD, linewidth=2)
    ax.fill_between(t, np.abs(t), 3.5, color=ACCENT2, alpha=0.1)
    ax.text(0, 2.5, 'Timelike', fontsize=11, ha='center', color=ACCENT2)
    ax.text(2, 0.5, 'Spacelike', fontsize=10, ha='center', color=ACCENT1)
    s = np.linspace(-2.5, 2.5, 100)
    ax.plot(np.sinh(s), np.cosh(s), color=ACCENT4, linewidth=1.5, alpha=0.5)
    ax.set_xlim(-3.5, 3.5); ax.set_ylim(-3.5, 3.5); ax.set_aspect('equal')
    ax.set_xlabel('$x$', fontsize=12); ax.set_ylabel('$t$', fontsize=12)
    ax.axhline(0, color=DARK, linewidth=0.3, alpha=0.3)
    ax.axvline(0, color=DARK, linewidth=0.3, alpha=0.3)
    ax.set_title('EAST: Minkowski Light Cone', fontsize=13, color=DARK, fontweight='bold')
    ax.text(0, -3, '$M^\\top J M = J$', fontsize=12, ha='center', color=ACCENT4, style='italic')

    # SOUTH: Factorization lattice
    ax = axes[1, 0]
    ax.set_facecolor(SAND)
    divs = [(1, 225), (3, 75), (5, 45), (9, 25), (15, 15)]
    for i, (d, e) in enumerate(divs):
        x = i * 1.5
        ax.plot(x, 3, 'o', color=ACCENT1, markersize=12, zorder=5)
        ax.text(x, 3.4, f'${d}$', fontsize=10, ha='center', color=DARK)
        ax.plot(x, 1, 'o', color=ACCENT2, markersize=12, zorder=5)
        ax.text(x, 0.6, f'${e}$', fontsize=10, ha='center', color=DARK)
        ax.plot([x, x], [1.2, 2.8], color=SLATE, linewidth=1, linestyle=':', alpha=0.5)
        ax.text(x, 2, r'$\times$', fontsize=12, ha='center', color=SLATE)
    ax.text(3, 4.2, '$d \\times e = 225$', fontsize=13, ha='center', color=DARK, fontweight='bold')
    ax.set_xlim(-1, 7.5); ax.set_ylim(-0.5, 5); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title('SOUTH: Factorization Lattice', fontsize=13, color=DARK, fontweight='bold')

    # WEST: Poincaré disk mini
    ax = axes[1, 1]
    ax.set_facecolor(SAND)
    ax.add_patch(plt.Circle((0, 0), 1, facecolor='#FFFEF5', edgecolor=DARK, linewidth=2))
    pts = [(3,4,5),(5,12,13),(21,20,29),(15,8,17),(7,24,25),(55,48,73),(45,28,53)]
    for tr in pts:
        a,b,c = tr
        px, py = triple_to_disk(tr)
        ms = max(4, 10 - 0.05*c)
        ax.plot(px, py, 'o', color=ACCENT3, markersize=ms, markeredgecolor=DARK, markeredgewidth=0.5, zorder=5)
        if c <= 29:
            ax.text(px+0.05, py+0.05, f'({a},{b},{c})', fontsize=6, color=DARK)
    ax.set_xlim(-1.3, 1.3); ax.set_ylim(-1.3, 1.3); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title('WEST: Poincaré Disk', fontsize=13, color=DARK, fontweight='bold')
    ax.text(0, -1.15, 'Hyperbolic isometry', fontsize=10, ha='center', color=ACCENT4, style='italic')

    fig.tight_layout(rect=[0, 0, 1, 0.95], h_pad=3, w_pad=3)
    save(fig, 'fig12_grand_diagram.png')


# ============================================================
if __name__ == '__main__':
    print("Generating Chapter 16 illustrations...")
    fig01_magic_box()
    fig02_q_table()
    fig03_null_cone()
    fig04_berggren_tree()
    fig05_minkowski_poincare()
    fig06_elevator_descent()
    fig07_a_highway()
    fig08_prime_depth()
    fig09_factor_table()
    fig10_triple_count()
    fig11_poincare_tessellation()
    fig12_grand_diagram()
    print("Done! All Chapter 16 illustrations generated.")

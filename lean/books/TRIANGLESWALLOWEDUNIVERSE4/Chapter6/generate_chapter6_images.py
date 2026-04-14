#!/usr/bin/env python3
"""Generate all illustrations for Chapter 6: The Lock with Seven Keyholes."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Wedge
import matplotlib.patheffects as pe
import numpy as np
import os
from math import gcd, sqrt

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
BRASS = '#B5A642'
BRONZE = '#CD7F32'
PARCHMENT = '#F5E6C8'

def save(fig, name, dpi=200):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=dpi, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  Saved {name}")


# ============================================================
# ILLUSTRATION 1: Vault door with seven keyholes
# ============================================================
def fig01_vault_door():
    fig, ax = plt.subplots(1, 1, figsize=(10, 11))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    # Draw vault door as large circle
    vault = plt.Circle((5, 5.5), 4, fill=True, facecolor='#8B8682',
                        edgecolor=DARK, linewidth=4, zorder=2)
    ax.add_patch(vault)
    # Inner ring
    inner = plt.Circle((5, 5.5), 3.5, fill=False,
                        edgecolor=BRONZE, linewidth=2, linestyle='--', zorder=3)
    ax.add_patch(inner)

    # Rivets around the edge
    for angle in np.linspace(0, 2*np.pi, 24, endpoint=False):
        rx = 5 + 3.8 * np.cos(angle)
        ry = 5.5 + 3.8 * np.sin(angle)
        rivet = plt.Circle((rx, ry), 0.08, color=BRASS, zorder=4)
        ax.add_patch(rivet)

    # Seven keyholes arranged in a circle
    labels = ['$a_1$', '$a_2$', '$a_3$', '$a_4$', '$a_5$', '$a_6$', '$a_7$']
    for i in range(7):
        angle = np.pi/2 + i * 2 * np.pi / 7
        kx = 5 + 2.4 * np.cos(angle)
        ky = 5.5 + 2.4 * np.sin(angle)

        # Keyhole shape: circle + rectangle
        kh_circle = plt.Circle((kx, ky), 0.22, color=DARK, zorder=5)
        ax.add_patch(kh_circle)
        # Slot below circle
        slot_dx = 0.08
        slot_dy = 0.35
        rect = patches.Rectangle((kx - slot_dx, ky - slot_dy), 2*slot_dx, slot_dy,
                                  color=DARK, zorder=5)
        ax.add_patch(rect)

        # Label
        lx = 5 + 3.0 * np.cos(angle)
        ly = 5.5 + 3.0 * np.sin(angle)
        ax.text(lx, ly, labels[i], fontsize=14, ha='center', va='center',
                color=DARK, fontweight='bold', zorder=10)

        # Radiating line from keyhole to center
        ax.plot([kx, 5], [ky, 5.5], color=GOLD, linewidth=1, alpha=0.6,
                linestyle=':', zorder=3)

    # Center N
    ax.text(5, 5.5, '$N$', fontsize=28, ha='center', va='center',
            color=CREAM, fontweight='bold', zorder=6,
            path_effects=[pe.withStroke(linewidth=3, foreground=DARK)])

    # Equation below
    ax.text(5, 0.6, r'$a_1^2 + a_2^2 + \cdots + a_7^2 = N^2$',
            fontsize=16, ha='center', va='center', color=DARK,
            fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=CREAM, edgecolor=BRONZE, linewidth=2))

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title("The Lock with Seven Keyholes", fontsize=18, color=DARK,
                 fontweight='bold', pad=15)
    save(fig, "fig01_vault_seven_keyholes.png")


# ============================================================
# ILLUSTRATION 2: Phylogenetic tree of Pythagorean creatures
# ============================================================
def fig02_phylogenetic_tree():
    fig, ax = plt.subplots(1, 1, figsize=(12, 14))
    fig.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    # Levels: triple (bottom), quadruple, quintuplet, sextuplet, octuplet (top)
    levels = [
        (1.0, "(3, 4, 5)\nTriple", "The Ancestor", 3, ACCENT1),
        (3.0, "(2, 3, 6, 7)\nQuadruple", "Four-legged", 4, ACCENT2),
        (5.0, "(1, 2, 2, 4, 5)\nQuintuplet", "Starfish", 5, ACCENT3),
        (7.0, "(1, 1, 1, 2, 3, 4)\nSextuplet", "Hexapod", 6, ACCENT5),
        (9.0, "(1, 2, 3, 4, 5, 6, 3, 10)\nOctuplet", "Octopus", 8, ACCENT4),
    ]

    cx = 6.0

    for i, (y, label, name, n_limbs, color) in enumerate(levels):
        # Body
        body = plt.Circle((cx, y), 0.6, facecolor=color, edgecolor=DARK,
                          linewidth=2, alpha=0.8, zorder=5)
        ax.add_patch(body)

        # Limbs radiating outward
        for j in range(n_limbs):
            angle = np.pi/2 + j * 2 * np.pi / n_limbs
            lx = cx + 1.1 * np.cos(angle)
            ly = y + 1.1 * np.sin(angle)
            ax.plot([cx + 0.6*np.cos(angle), lx],
                    [y + 0.6*np.sin(angle), ly],
                    color=color, linewidth=2.5, zorder=4)
            # Small circle at end (foot/tip)
            tip = plt.Circle((lx, ly), 0.06, color=DARK, zorder=6)
            ax.add_patch(tip)

        # Eyes on body
        ax.plot(cx - 0.15, y + 0.15, 'o', color='white', markersize=5, zorder=7)
        ax.plot(cx + 0.15, y + 0.15, 'o', color='white', markersize=5, zorder=7)
        ax.plot(cx - 0.15, y + 0.15, 'o', color=DARK, markersize=2, zorder=8)
        ax.plot(cx + 0.15, y + 0.15, 'o', color=DARK, markersize=2, zorder=8)

        # Label to the right
        ax.text(cx + 2.0, y + 0.2, name, fontsize=13, color=DARK,
                fontweight='bold', fontstyle='italic', va='center')
        ax.text(cx + 2.0, y - 0.25, label, fontsize=9, color=SLATE,
                va='center', family='monospace')

        # Vine-like branch connecting to next level
        if i < len(levels) - 1:
            next_y = levels[i+1][0]
            # Organic curve
            ts = np.linspace(0, 1, 30)
            bx = cx + 0.3 * np.sin(ts * 4 * np.pi)
            by = y + 0.6 + ts * (next_y - y - 1.2)
            ax.plot(bx, by, color='#6B4226', linewidth=2, alpha=0.7, zorder=2)
            # Small leaves
            for t in [0.3, 0.7]:
                lf_x = cx + 0.3 * np.sin(t * 4 * np.pi)
                lf_y = y + 0.6 + t * (next_y - y - 1.2)
                leaf = plt.Circle((lf_x + 0.15, lf_y), 0.06, color=ACCENT3, alpha=0.5, zorder=3)
                ax.add_patch(leaf)

    ax.set_xlim(2, 11)
    ax.set_ylim(-0.5, 11)
    ax.axis('off')
    ax.set_title("A Naturalist's Guide to Pythagorean Creatures",
                 fontsize=17, color=DARK, fontweight='bold', fontstyle='italic', pad=15)
    save(fig, "fig02_phylogenetic_tree.png")


# ============================================================
# ILLUSTRATION 3: Specimen catalog table
# ============================================================
def fig03_specimen_catalog():
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    fig.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    specimens = [
        ("Quintuplet", (1,1,1,1,2), "1+1+1+1=4=2²"),
        ("Quintuplet", (1,2,2,4,5), "1+4+4+16=25=5²"),
        ("Quintuplet", (1,4,4,4,7), "1+16+16+16=49=7²"),
        ("Sextuplet",  (1,1,1,2,3,4), "1+1+1+4+9=16=4²"),
        ("Sextuplet",  (1,1,3,3,4,6), "1+1+9+9+16=36=6²"),
        ("Octuplet",   (1,2,3,4,5,6,3,10), "1+4+9+16+25+36+9=100=10²"),
    ]

    col_widths = [2.5, 4.5, 5.0]
    row_height = 0.9
    x0, y0 = 0.5, 6.5

    # Header
    headers = ["Type", "Tuple", "Verification"]
    for j, (hdr, w) in enumerate(zip(headers, col_widths)):
        x = x0 + sum(col_widths[:j])
        rect = patches.FancyBboxPatch((x, y0), w, row_height,
                                       boxstyle="round,pad=0.05",
                                       facecolor=BRONZE, edgecolor=DARK, linewidth=2)
        ax.add_patch(rect)
        ax.text(x + w/2, y0 + row_height/2, hdr, fontsize=13, ha='center', va='center',
                color=CREAM, fontweight='bold')

    # Rows
    for i, (typ, tup, verif) in enumerate(specimens):
        y = y0 - (i + 1) * row_height
        bg = SAND if i % 2 == 0 else CREAM
        for j, w in enumerate(col_widths):
            x = x0 + sum(col_widths[:j])
            rect = patches.FancyBboxPatch((x, y), w, row_height,
                                           boxstyle="round,pad=0.05",
                                           facecolor=bg, edgecolor=DARK, linewidth=1)
            ax.add_patch(rect)

        # Type
        x_t = x0 + col_widths[0] / 2
        ax.text(x_t, y + row_height/2, typ, fontsize=11, ha='center', va='center',
                color=DARK, fontstyle='italic')

        # Tuple
        x_t = x0 + col_widths[0] + col_widths[1] / 2
        tup_str = str(tup)
        ax.text(x_t, y + row_height/2, tup_str, fontsize=11, ha='center', va='center',
                color=DARK, family='monospace')

        # Verification + checkmark
        x_t = x0 + col_widths[0] + col_widths[1] + col_widths[2] / 2
        ax.text(x_t - 0.3, y + row_height/2, verif, fontsize=10, ha='center', va='center',
                color=SLATE)
        ax.text(x_t + 2.0, y + row_height/2, '✓', fontsize=14, ha='center', va='center',
                color=ACCENT3, fontweight='bold')

    # Ornamental border
    total_w = sum(col_widths)
    total_h = (len(specimens) + 1) * row_height
    border = patches.FancyBboxPatch((x0 - 0.1, y0 - len(specimens) * row_height - 0.1),
                                     total_w + 0.2, total_h + 0.2,
                                     boxstyle="round,pad=0.1",
                                     facecolor='none', edgecolor=BRONZE, linewidth=3)
    ax.add_patch(border)

    ax.set_xlim(-0.5, 13.5)
    ax.set_ylim(-0.5, 8.5)
    ax.axis('off')
    ax.set_title("Specimen Catalog: Higher Pythagorean $k$-tuples",
                 fontsize=16, color=DARK, fontweight='bold', fontstyle='italic', pad=15)
    save(fig, "fig03_specimen_catalog.png")


# ============================================================
# ILLUSTRATION 4: Combination lock diagram for N=15
# ============================================================
def fig04_lock_N15():
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    cx, cy = 5, 5
    R = 3.5

    # Outer ring (antique pocket watch)
    outer = plt.Circle((cx, cy), R + 0.5, fill=False, edgecolor=BRONZE, linewidth=4, zorder=2)
    ax.add_patch(outer)
    outer2 = plt.Circle((cx, cy), R + 0.3, fill=False, edgecolor=GOLD, linewidth=1, zorder=2)
    ax.add_patch(outer2)
    inner_fill = plt.Circle((cx, cy), R, fill=True, facecolor=CREAM, edgecolor=DARK,
                             linewidth=2, zorder=1)
    ax.add_patch(inner_fill)

    # Quadruple (5, 10, 10, 15) — spatial components at three points
    spatial = [5, 10, 10]
    N = 15
    channels = [
        (f"gcd({N}-{spatial[0]}, {N}) = gcd(10,15) = 5", True),
        (f"gcd({N}-{spatial[1]}, {N}) = gcd(5,15) = 5", True),
        (f"gcd({N}-{spatial[2]}, {N}) = gcd(5,15) = 5", True),
    ]

    for i in range(3):
        angle = np.pi/2 + i * 2 * np.pi / 3
        sx = cx + R * np.cos(angle)
        sy = cy + R * np.sin(angle)

        # Point
        pt = plt.Circle((sx, sy), 0.25, facecolor=ACCENT3, edgecolor=DARK,
                         linewidth=2, zorder=5)
        ax.add_patch(pt)
        ax.text(sx, sy, str(spatial[i]), fontsize=12, ha='center', va='center',
                color='white', fontweight='bold', zorder=6)

        # Arrow to center
        ax.annotate('', xy=(cx + 0.3*np.cos(angle), cy + 0.3*np.sin(angle)),
                    xytext=(sx - 0.3*np.cos(angle), sy - 0.3*np.sin(angle)),
                    arrowprops=dict(arrowstyle='->', color=ACCENT3, lw=2), zorder=4)

        # Channel label
        lx = cx + (R + 1.5) * np.cos(angle)
        ly = cy + (R + 1.5) * np.sin(angle)
        text = channels[i][0]
        color = ACCENT3 if channels[i][1] else ACCENT1
        ax.text(lx, ly, text, fontsize=8, ha='center', va='center',
                color=color, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor=color, alpha=0.9))

    # Center: N
    ax.text(cx, cy, '$N = 15$', fontsize=20, ha='center', va='center',
            color=DARK, fontweight='bold', zorder=6)

    # Factor annotation
    ax.text(cx, cy - 1.2, 'Factor found: $\\mathbf{5}$ ✓', fontsize=14, ha='center',
            color=ACCENT3, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=LIGHT_GREEN, edgecolor=ACCENT3))

    # Title
    ax.text(cx, cy - R - 2.0, 'Quadruple: $(5, 10, 10, 15)$', fontsize=13,
            ha='center', color=DARK, fontstyle='italic')

    ax.set_xlim(-1, 11)
    ax.set_ylim(-1, 11)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title("Combination Lock — $N = 15$", fontsize=17, color=DARK,
                 fontweight='bold', pad=15)
    save(fig, "fig04_lock_N15.png")


# ============================================================
# ILLUSTRATION 5: Combination lock diagram for N=21
# ============================================================
def fig05_lock_N21():
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    cx, cy = 5, 5
    R = 3.5

    # Ornate outer ring
    outer = plt.Circle((cx, cy), R + 0.6, fill=False, edgecolor=BRONZE, linewidth=5, zorder=2)
    ax.add_patch(outer)
    outer2 = plt.Circle((cx, cy), R + 0.4, fill=False, edgecolor=GOLD, linewidth=2, zorder=2)
    ax.add_patch(outer2)
    outer3 = plt.Circle((cx, cy), R + 0.2, fill=False, edgecolor=BRONZE, linewidth=1, zorder=2)
    ax.add_patch(outer3)
    inner_fill = plt.Circle((cx, cy), R, fill=True, facecolor=CREAM, edgecolor=DARK,
                             linewidth=2, zorder=1)
    ax.add_patch(inner_fill)

    # Quadruple (6, 9, 18, 21) — spatial: 6, 9, 18; hyp: 21
    spatial = [6, 9, 18]
    N = 21
    gcd_vals = [gcd(N - s, N) for s in spatial]
    channels = [
        (f"gcd({N-s}, {N}) = {gcd(N-s, N)}", gcd(N-s, N) not in [1, N])
        for s in spatial
    ]

    for i in range(3):
        angle = np.pi/2 + i * 2 * np.pi / 3
        sx = cx + R * np.cos(angle)
        sy = cy + R * np.sin(angle)

        pt = plt.Circle((sx, sy), 0.28, facecolor=ACCENT2, edgecolor=DARK,
                         linewidth=2, zorder=5)
        ax.add_patch(pt)
        ax.text(sx, sy, str(spatial[i]), fontsize=12, ha='center', va='center',
                color='white', fontweight='bold', zorder=6)

        ax.annotate('', xy=(cx + 0.3*np.cos(angle), cy + 0.3*np.sin(angle)),
                    xytext=(sx - 0.3*np.cos(angle), sy - 0.3*np.sin(angle)),
                    arrowprops=dict(arrowstyle='->', color=ACCENT2, lw=2), zorder=4)

        lx = cx + (R + 1.5) * np.cos(angle)
        ly = cy + (R + 1.5) * np.sin(angle)
        text = channels[i][0]
        ax.text(lx, ly, text, fontsize=9, ha='center', va='center',
                color=ACCENT2, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor=ACCENT2, alpha=0.9))

    # Center
    ax.text(cx, cy + 0.3, '$N = 21$', fontsize=20, ha='center', va='center',
            color=DARK, fontweight='bold', zorder=6)
    ax.text(cx, cy - 0.4, '$= 3 \\times 7$', fontsize=12, ha='center',
            color=SLATE, zorder=6)

    # Factor annotation
    ax.text(cx, cy - 1.5, 'Factor: $\\mathbf{3}$  ·  Complement: $\\mathbf{7}$',
            fontsize=13, ha='center', color=ACCENT2, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=LIGHT_BLUE, edgecolor=ACCENT2))

    ax.text(cx, cy - R - 2.0, 'Quadruple: $(6, 9, 18, 21)$', fontsize=13,
            ha='center', color=DARK, fontstyle='italic')

    ax.set_xlim(-1, 11)
    ax.set_ylim(-1, 11)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title("Combination Lock — $N = 21$", fontsize=17, color=DARK,
                 fontweight='bold', pad=15)
    save(fig, "fig05_lock_N21.png")


# ============================================================
# ILLUSTRATION 6: Complete graph K7 — channel network
# ============================================================
def fig06_K7_channels():
    fig, ax = plt.subplots(1, 1, figsize=(11, 11))
    fig.set_facecolor(PARCHMENT)
    ax.set_facecolor(PARCHMENT)

    cx, cy = 5.5, 5.5
    R = 3.8
    n = 7

    # Vertices of heptagon
    verts = []
    for i in range(n):
        angle = np.pi/2 + i * 2 * np.pi / n
        verts.append((cx + R * np.cos(angle), cy + R * np.sin(angle)))

    # Draw all 21 edges
    for i in range(n):
        for j in range(i+1, n):
            ax.plot([verts[i][0], verts[j][0]], [verts[i][1], verts[j][1]],
                    color=ACCENT2, linewidth=1, alpha=0.4, zorder=2)
            # Small gcd label at midpoint (only a few to avoid clutter)
            mx = (verts[i][0] + verts[j][0]) / 2
            my = (verts[i][1] + verts[j][1]) / 2

    # Draw vertices as keyholes
    labels = ['$a_1$', '$a_2$', '$a_3$', '$a_4$', '$a_5$', '$a_6$', '$a_7$']
    for i, (vx, vy) in enumerate(verts):
        # Keyhole circle
        kh = plt.Circle((vx, vy), 0.35, facecolor=ACCENT2, edgecolor=DARK,
                         linewidth=2, zorder=5)
        ax.add_patch(kh)
        # Keyhole slot
        rect = patches.Rectangle((vx - 0.06, vy - 0.45), 0.12, 0.3,
                                  color=DARK, zorder=5)
        ax.add_patch(rect)
        # Label
        lx = cx + (R + 0.8) * np.cos(np.pi/2 + i * 2*np.pi/n)
        ly = cy + (R + 0.8) * np.sin(np.pi/2 + i * 2*np.pi/n)
        ax.text(lx, ly, labels[i], fontsize=14, ha='center', va='center',
                color=DARK, fontweight='bold', zorder=10)

    # Center N
    ax.text(cx, cy, '$N$', fontsize=32, ha='center', va='center',
            color=DARK, fontweight='bold', zorder=6, family='serif')

    # Legend box
    legend_text = ("7 vertices = 7 primary channels\n"
                   "21 edges = 21 pairwise channels\n"
                   "Total = 28 keys")
    ax.text(9.5, 1.0, legend_text, fontsize=10, ha='center', va='center',
            color=DARK,
            bbox=dict(boxstyle='round,pad=0.4', facecolor=CREAM, edgecolor=BRONZE, linewidth=2))

    ax.set_xlim(0, 11)
    ax.set_ylim(0, 11)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title("$K_7$: The Complete Channel Network",
                 fontsize=17, color=DARK, fontweight='bold', pad=15)
    save(fig, "fig06_K7_channels.png")


# ============================================================
# ILLUSTRATION 7: Three-panel inside-out factoring
# ============================================================
def fig07_inside_out():
    fig, axes = plt.subplots(1, 3, figsize=(16, 6))
    fig.set_facecolor(SAND)

    titles = ["Triple (2D)", "Quadruple (3D)", "Octuplet (high-D)"]
    channels = ["1 channel", "2 channels", "6 channels"]
    colors = [ACCENT1, ACCENT2, ACCENT4]

    for idx, ax in enumerate(axes):
        ax.set_facecolor(SAND)
        ax.set_aspect('equal')

        if idx == 0:
            # 2D cone cross-section: V shape
            ax.plot([0, 3, 6], [0, 4, 0], color=DARK, linewidth=2, zorder=3)
            ax.plot(3, 4, 'o', color=ACCENT1, markersize=12, zorder=5)
            ax.text(3, 4.4, '$N$', fontsize=14, ha='center', color=DARK, fontweight='bold')
            # Arc for parameter u
            theta = np.linspace(-0.5, 0.5, 30)
            arc_x = 3 + 2 * np.sin(theta)
            arc_y = 2 + 0.5 * np.cos(theta)
            ax.plot(arc_x, arc_y, color=ACCENT1, linewidth=2.5, zorder=4)
            ax.text(5.3, 2, '$u$', fontsize=12, color=ACCENT1, fontweight='bold')
            ax.annotate('', xy=(1, -0.5), xytext=(3, 2),
                        arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=2))
            ax.text(1, -1, '1 channel', fontsize=11, ha='center', color=ACCENT1, fontweight='bold')

        elif idx == 1:
            # 3D cone: ellipse base + lines to apex
            theta = np.linspace(0, 2*np.pi, 60)
            ex = 3 + 2 * np.cos(theta)
            ey = 1 + 0.6 * np.sin(theta)
            ax.fill(ex, ey, alpha=0.15, color=ACCENT2)
            ax.plot(ex, ey, color=ACCENT2, linewidth=2, zorder=3)
            ax.plot([1, 3], [1, 5], color=DARK, linewidth=1.5, zorder=2)
            ax.plot([5, 3], [1, 5], color=DARK, linewidth=1.5, zorder=2)
            ax.plot(3, 5, 'o', color=ACCENT2, markersize=12, zorder=5)
            ax.text(3, 5.4, '$N$', fontsize=14, ha='center', color=DARK, fontweight='bold')
            ax.text(4.5, 0.5, '$u, v$', fontsize=12, color=ACCENT2, fontweight='bold')
            for ang in [0.3, -0.4]:
                ax.annotate('', xy=(3 + 3*np.cos(ang), -0.5 + np.sin(ang)),
                            xytext=(3 + 1.8*np.cos(ang), 1 + 0.5*np.sin(ang)),
                            arrowprops=dict(arrowstyle='->', color=ACCENT2, lw=2))
            ax.text(3, -1, '2 channels', fontsize=11, ha='center', color=ACCENT2, fontweight='bold')

        else:
            # Starburst
            ax.plot(3, 3, 'o', color=ACCENT4, markersize=16, zorder=5)
            ax.text(3, 3.6, '$N$', fontsize=14, ha='center', color=DARK, fontweight='bold')
            u_labels = ['$u_1$', '$u_2$', '$u_3$', '$u_4$', '$u_5$', '$u_6$']
            for i in range(6):
                angle = i * np.pi / 3
                dx = 2.5 * np.cos(angle)
                dy = 2.5 * np.sin(angle)
                ax.plot([3, 3+dx], [3, 3+dy], color=ACCENT4, linewidth=2, alpha=0.7, zorder=3)
                ax.annotate('', xy=(3 + dx*1.1, 3 + dy*1.1),
                            xytext=(3 + dx*0.7, 3 + dy*0.7),
                            arrowprops=dict(arrowstyle='->', color=ACCENT4, lw=2))
                ax.text(3 + dx*1.25, 3 + dy*1.25, u_labels[i], fontsize=10,
                        ha='center', va='center', color=ACCENT4, fontweight='bold')
            ax.text(3, -0.5, '6 channels', fontsize=11, ha='center', color=ACCENT4, fontweight='bold')

        ax.set_title(titles[idx], fontsize=13, color=DARK, fontweight='bold')
        ax.set_xlim(-0.5, 6.5)
        ax.set_ylim(-1.5, 6.5)
        ax.axis('off')

    fig.suptitle("More dimensions, more freedom, more chances",
                 fontsize=16, color=DARK, fontweight='bold', y=0.02, fontstyle='italic')
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    save(fig, "fig07_inside_out.png")


# ============================================================
# ILLUSTRATION 8: Maze — inside-out method
# ============================================================
def fig08_maze():
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    fig.set_facecolor(SAND)

    for idx, ax in enumerate(axes):
        ax.set_facecolor(SAND)
        np.random.seed(42)

        # Simple maze: create walls
        n = 8
        # Draw grid walls
        for i in range(n + 1):
            ax.plot([0, n], [i, i], color='#DDD', linewidth=0.5, zorder=1)
            ax.plot([i, i], [0, n], color='#DDD', linewidth=0.5, zorder=1)

        # Border walls
        ax.plot([0, n, n, 0, 0], [0, 0, n, n, 0], color=DARK, linewidth=3, zorder=5)

        # Create a winding path
        path = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 3), (3, 3),
                (3, 4), (3, 5), (4, 5), (5, 5), (5, 6), (5, 7), (6, 7),
                (7, 7)]
        path_x = [p[0] + 0.5 for p in path]
        path_y = [p[1] + 0.5 for p in path]

        # Draw some maze walls (interior)
        walls = [
            ([1, 1], [0, 2]), ([2, 2], [0, 1]), ([3, 3], [0, 2]),
            ([1, 3], [3, 3]), ([4, 4], [0, 4]), ([5, 7], [4, 4]),
            ([5, 5], [1, 4]), ([6, 6], [0, 3]), ([7, 7], [1, 6]),
            ([6, 8], [6, 6]), ([1, 1], [4, 7]), ([2, 4], [6, 6]),
            ([3, 3], [6, 8]), ([6, 6], [5, 7]),
        ]
        for wx, wy in walls:
            ax.plot(wx, wy, color=DARK, linewidth=2, zorder=3)

        if idx == 0:
            # Forward view — frustration path
            ax.plot(path_x, path_y, color=ACCENT1, linewidth=3, alpha=0.6, zorder=4,
                    linestyle='--')
            ax.text(0.5, -0.5, 'START\n"Search for tuples"', fontsize=10,
                    ha='center', color=ACCENT1, fontweight='bold')
            ax.text(7.5, 8.3, 'FINISH', fontsize=10, ha='center', color=SLATE)
            ax.set_title("Forward: Hard", fontsize=14, color=ACCENT1, fontweight='bold')
        else:
            # Backward view — solution highlighted
            ax.plot(path_x, path_y, color=ACCENT3, linewidth=4, alpha=0.8, zorder=4)
            ax.text(7.5, 8.3, 'START\n"Fix $N$, work backwards"', fontsize=10,
                    ha='center', color=ACCENT3, fontweight='bold')
            ax.text(0.5, -0.5, 'FINISH', fontsize=10, ha='center', color=SLATE)
            ax.set_title("Inside-Out: Easy", fontsize=14, color=ACCENT3, fontweight='bold')

        ax.set_xlim(-0.5, 8.5)
        ax.set_ylim(-1.5, 9)
        ax.set_aspect('equal')
        ax.axis('off')

    fig.suptitle("The inside-out method: start with $N$, choose free parameters, "
                 "check for integer solutions",
                 fontsize=12, color=DARK, fontstyle='italic', y=0.02)
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    save(fig, "fig08_maze.png")


# ============================================================
# ILLUSTRATION 9: Berggren tree with descent path
# ============================================================
def fig09_berggren_descent():
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    fig.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    # Build a small Berggren tree
    # Matrices for generating Pythagorean triples from (m, n) -> children
    def children_triples(a, b, c):
        """Return three children via Berggren matrices."""
        c1 = (a - 2*b + 2*c, 2*a - b + 2*c, 2*a - 2*b + 3*c)
        c2 = (a + 2*b + 2*c, 2*a + b + 2*c, 2*a + 2*b + 3*c)
        c3 = (-a + 2*b + 2*c, -2*a + b + 2*c, -2*a + 2*b + 3*c)
        return [c1, c2, c3]

    root = (3, 4, 5)
    # Build tree: level 0 = root, levels 1-3
    tree = {0: [root]}
    positions = {}
    # Position root
    positions[root] = (8, 1)

    for level in range(3):
        tree[level + 1] = []
        parents = tree[level]
        n_parents = len(parents)
        for pi, parent in enumerate(parents):
            kids = children_triples(*parent)
            tree[level + 1].extend(kids)

    # Assign positions
    level_ys = [1, 3.5, 6, 8.5]
    for level in range(4):
        nodes = tree[level]
        n = len(nodes)
        for i, node in enumerate(nodes):
            x = 1 + (15) * (i + 0.5) / n
            positions[node] = (x, level_ys[level])

    # Draw edges
    for level in range(3):
        parents = tree[level]
        children = tree[level + 1]
        for pi, parent in enumerate(parents):
            kids = children_triples(*parent)
            for kid in kids:
                if kid in positions and parent in positions:
                    px, py = positions[parent]
                    kx, ky = positions[kid]
                    ax.plot([px, kx], [py, ky], color='#8B7355', linewidth=1.5,
                            alpha=0.5, zorder=2)

    # Draw nodes
    for level in range(4):
        for node in tree[level]:
            if node in positions:
                x, y = positions[node]
                ax.plot(x, y, 'o', color=ACCENT2, markersize=8, zorder=5,
                        markeredgecolor=DARK, markeredgewidth=1)
                label = f"({node[0]},{node[1]},{node[2]})"
                fontsize = 7 if level >= 2 else 9
                ax.text(x, y - 0.4, label, fontsize=fontsize, ha='center',
                        color=DARK, zorder=6)

    # Ascent label
    ax.annotate('', xy=(14.5, 8), xytext=(14.5, 2),
                arrowprops=dict(arrowstyle='->', color=ACCENT2, lw=3))
    ax.text(15.2, 5, 'ASCENT\n(easy)', fontsize=12, color=ACCENT2,
            fontweight='bold', ha='center', rotation=90)

    # Descent path: highlight a path from a leaf back to root
    # Find a descent path
    descent_path = [root]
    node = root
    for level in range(3):
        kids = children_triples(*node)
        node = kids[1]  # Take middle child
        descent_path.append(node)
    descent_path.reverse()

    # Draw thick descent arrow
    for i in range(len(descent_path) - 1):
        p1 = positions[descent_path[i]]
        p2 = positions[descent_path[i+1]]
        ax.annotate('', xy=(p2[0], p2[1] + 0.3), xytext=(p1[0], p1[1] - 0.3),
                    arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=3), zorder=10)

    # Descent label
    ax.text(0.5, 5, 'DESCENT\n(factoring)', fontsize=12, color=ACCENT1,
            fontweight='bold', ha='center', rotation=90)

    # Hypotenuse values along descent
    for i, node in enumerate(descent_path):
        x, y = positions[node]
        ax.text(x, y + 0.5, f'$c = {node[2]}$', fontsize=9, ha='center',
                color=ACCENT1, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.15', facecolor=LIGHT_RED, edgecolor=ACCENT1, alpha=0.8))

    ax.set_xlim(-0.5, 16.5)
    ax.set_ylim(-0.5, 10)
    ax.axis('off')
    ax.set_title("The Berggren Tree: Ascent Builds Tuples, Descent Factors",
                 fontsize=16, color=DARK, fontweight='bold', pad=15)
    save(fig, "fig09_berggren_descent.png")


# ============================================================
# ILLUSTRATION 10: Reflection map — before/after tetrahedra
# ============================================================
def fig10_reflection_tetrahedra():
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    fig.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    def draw_tetrahedron(ax, cx, cy, labels_base, label_apex, color, title):
        """Draw a stylized tetrahedron: triangle base + apex above."""
        # Base triangle
        bw = 2.5
        bh = 0.8
        base_pts = [
            (cx - bw/2, cy),
            (cx + bw/2, cy),
            (cx, cy + bh),
        ]
        tri = plt.Polygon(base_pts, fill=True, facecolor=color, alpha=0.2,
                           edgecolor=color, linewidth=2, zorder=3)
        ax.add_patch(tri)

        # Apex
        apex = (cx, cy + 3.0)
        for bpt in base_pts:
            ax.plot([bpt[0], apex[0]], [bpt[1], apex[1]], color=color,
                    linewidth=1.5, linestyle='--', alpha=0.5, zorder=2)

        # Apex point
        ax.plot(*apex, 'o', color=color, markersize=14, zorder=5,
                markeredgecolor=DARK, markeredgewidth=2)
        ax.text(apex[0], apex[1] + 0.4, label_apex, fontsize=12, ha='center',
                color=DARK, fontweight='bold')

        # Base points and labels
        for i, (bpt, lbl) in enumerate(zip(base_pts, labels_base)):
            ax.plot(*bpt, 'o', color=color, markersize=10, zorder=5,
                    markeredgecolor=DARK, markeredgewidth=1.5)
            offset_y = -0.5 if i < 2 else 0.4
            ax.text(bpt[0], bpt[1] + offset_y, lbl, fontsize=11, ha='center',
                    color=DARK)

        ax.text(cx, cy - 0.8, title, fontsize=11, ha='center', color=color,
                fontweight='bold', fontstyle='italic')

    # Left tetrahedron: original
    draw_tetrahedron(ax, 3, 2,
                     ['$a$', '$b$', '$c$'],
                     '$d$ (hyp.)', ACCENT2, "Original")

    # Right tetrahedron: reflected
    draw_tetrahedron(ax, 11, 2,
                     ['$d{-}b{-}c$', '$d{-}a{-}c$', '$d{-}a{-}b$'],
                     '$2d{-}a{-}b{-}c$', ACCENT1, "Reflected")

    # Curved arrow between them
    ax.annotate('', xy=(8.5, 4.5), xytext=(5.5, 4.5),
                arrowprops=dict(arrowstyle='->', color=GOLD, lw=3,
                                connectionstyle='arc3,rad=0.3'))
    ax.text(7, 5.8, '$R_{1111}$', fontsize=16, ha='center', color=GOLD,
            fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=CREAM, edgecolor=GOLD, linewidth=2))

    # Note about descent
    ax.text(11, 5.5, '← smaller apex\n   (descent!)', fontsize=10,
            color=ACCENT1, fontstyle='italic')

    # GCD arrows from reflected base
    for i, (x, y, expr) in enumerate([
        (9.5, 1.5, 'gcd(d−b−c, N)?'),
        (12.5, 1.5, 'gcd(d−a−c, N)?'),
        (11, 2.8, 'gcd(d−a−b, N)?'),
    ]):
        ax.annotate('Factor of $N$?', xy=(x, y - 1.0), xytext=(x, y),
                    fontsize=8, ha='center', color=ACCENT3,
                    arrowprops=dict(arrowstyle='->', color=ACCENT3, lw=1.5),
                    bbox=dict(boxstyle='round,pad=0.2', facecolor=LIGHT_GREEN, edgecolor=ACCENT3))

    ax.set_xlim(0, 14)
    ax.set_ylim(-0.5, 7)
    ax.axis('off')
    ax.set_title("The Reflection Map: From Quadruple to Factor",
                 fontsize=16, color=DARK, fontweight='bold', pad=15)
    save(fig, "fig10_reflection_tetrahedra.png")


# ============================================================
# ILLUSTRATION 11: Dimensional elevator
# ============================================================
def fig11_dimensional_elevator():
    fig, ax = plt.subplots(1, 1, figsize=(12, 14))
    fig.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    floors = [
        (3, "Floor 3: Triples", "(3, 4, 5)", ACCENT1, "△"),
        (4, "Floor 4: Quadruples", "(3, 4, 0, 5)", ACCENT2, "◇"),
        (5, "Floor 5: Quintuplets", "(1, 2, 2, 4, 5)", ACCENT3, "☆"),
        (6, "Floor 6: Sextuplets", "(1, 1, 1, 2, 3, 4)", ACCENT5, "⬡"),
        (7, "Floor 7: Septuplets", "(1, 1, 2, 2, 3, 3, 6)", ACCENT4, "●"),
        (8, "Floor 8: Octuplets", "(1, 2, 3, 4, 5, 6, 3, 10)", SLATE, "8"),
    ]

    floor_h = 1.8
    floor_w = 9
    x0 = 1.5
    shaft_x = 1.0  # elevator shaft position

    for i, (k, label, example, color, symbol) in enumerate(floors):
        y = i * floor_h + 0.5

        # Floor rectangle
        rect = patches.FancyBboxPatch((x0, y), floor_w, floor_h * 0.8,
                                       boxstyle="round,pad=0.1",
                                       facecolor='white', edgecolor=color,
                                       linewidth=2, alpha=0.8)
        ax.add_patch(rect)

        # Floor label
        ax.text(x0 + 0.5, y + floor_h * 0.6, label, fontsize=12, color=DARK,
                fontweight='bold', va='center')
        ax.text(x0 + 0.5, y + floor_h * 0.25, example, fontsize=10, color=SLATE,
                va='center', family='monospace')

        # Symbol decoration
        ax.text(x0 + floor_w - 0.5, y + floor_h * 0.4, symbol, fontsize=20,
                ha='center', va='center', color=color)

    # Elevator shaft
    shaft_left = shaft_x - 0.3
    shaft_right = shaft_x + 0.3
    ax.plot([shaft_left, shaft_left], [0.5, len(floors) * floor_h],
            color=DARK, linewidth=2, zorder=3)
    ax.plot([shaft_right, shaft_right], [0.5, len(floors) * floor_h],
            color=DARK, linewidth=2, zorder=3)

    # Upward arrow: "Trivial Lift"
    y1 = 0.5 + floor_h * 0.4
    y2 = floor_h + 0.5 + floor_h * 0.4
    ax.annotate('', xy=(shaft_x, y2), xytext=(shaft_x, y1),
                arrowprops=dict(arrowstyle='->', color=ACCENT3, lw=3))
    ax.text(shaft_x - 1.0, (y1 + y2) / 2, 'Trivial\nLift\n(insert 0)',
            fontsize=8, ha='center', color=ACCENT3, fontweight='bold', rotation=0)

    # Chain Lift arrow (skipping)
    y1 = 0.5 + floor_h * 0.4
    y3 = 2 * floor_h + 0.5 + floor_h * 0.4
    ax.annotate('', xy=(shaft_x + 0.5, y3), xytext=(shaft_x + 0.5, y1),
                arrowprops=dict(arrowstyle='->', color=ACCENT2, lw=2,
                                connectionstyle='arc3,rad=0.5'))
    ax.text(shaft_x + 1.8, (y1 + y3) / 2, 'Chain\nLift', fontsize=8,
            ha='center', color=ACCENT2, fontweight='bold')

    # Downward arrow: "Peel"
    y4 = 2 * floor_h + 0.5 + floor_h * 0.4
    y5 = floor_h + 0.5 + floor_h * 0.4
    ax.annotate('', xy=(shaft_x - 0.2, y5 + 0.3), xytext=(shaft_x - 0.2, y4 - 0.1),
                arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=2))
    ax.text(shaft_x - 1.0, (y4 + y5) / 2 + 0.5, 'Peel ↓', fontsize=8,
            ha='center', color=ACCENT1, fontweight='bold')

    ax.set_xlim(-1, 12)
    ax.set_ylim(-0.5, len(floors) * floor_h + 1)
    ax.axis('off')
    ax.set_title("The Dimensional Elevator: ride up to gain channels, "
                 "ride down to simplify",
                 fontsize=14, color=DARK, fontweight='bold', fontstyle='italic', pad=15)
    save(fig, "fig11_dimensional_elevator.png")


# ============================================================
# ILLUSTRATION 12: Brahmagupta–Fibonacci gear machine
# ============================================================
def fig12_gear_machine():
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    def draw_gear(ax, cx, cy, r, n_teeth, color, labels):
        """Draw a stylized gear."""
        theta = np.linspace(0, 2*np.pi, 200)
        # Gear profile: circle with bumps
        r_vals = r + 0.15 * np.sign(np.sin(n_teeth * theta))
        gx = cx + r_vals * np.cos(theta)
        gy = cy + r_vals * np.sin(theta)
        ax.fill(gx, gy, color=color, alpha=0.3, zorder=3)
        ax.plot(gx, gy, color=DARK, linewidth=2, zorder=4)
        # Center
        center = plt.Circle((cx, cy), 0.15, color=DARK, zorder=5)
        ax.add_patch(center)
        # Labels on teeth
        for i, lbl in enumerate(labels):
            angle = i * 2 * np.pi / len(labels) + np.pi/len(labels)
            tx = cx + (r * 0.6) * np.cos(angle)
            ty = cy + (r * 0.6) * np.sin(angle)
            ax.text(tx, ty, lbl, fontsize=11, ha='center', va='center',
                    color=DARK, fontweight='bold', zorder=6)

    # Left gear
    draw_gear(ax, 3.5, 4.5, 2, 8, ACCENT2, ['$a$', '$b$', '$a^2$', '$b^2$'])
    ax.text(3.5, 7.2, 'First sum:\n$a^2 + b^2 = N_1$', fontsize=11,
            ha='center', color=ACCENT2, fontweight='bold')

    # Right gear
    draw_gear(ax, 8.5, 4.5, 2, 8, ACCENT1, ['$c$', '$d$', '$c^2$', '$d^2$'])
    ax.text(8.5, 7.2, 'Second sum:\n$c^2 + d^2 = N_2$', fontsize=11,
            ha='center', color=ACCENT1, fontweight='bold')

    # Output shaft below
    ax.plot([6, 6], [2, 0.5], color=DARK, linewidth=4, zorder=3)
    ax.plot(6, 0.2, 'v', color=DARK, markersize=12, zorder=5)

    # Output label
    ax.text(6, -0.5, r'$(ac - bd)^2 + (ad + bc)^2 = N_1 N_2$',
            fontsize=13, ha='center', color=DARK, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=GLOW, edgecolor=GOLD, linewidth=2))

    # Connection between gears
    ax.plot([5.5, 6.5], [4.5, 4.5], color=DARK, linewidth=2, linestyle=':', zorder=2)

    ax.set_xlim(0, 12)
    ax.set_ylim(-1.5, 8)
    ax.axis('off')
    ax.set_title("The Brahmagupta–Fibonacci Identity: A Multiplication Machine",
                 fontsize=16, color=DARK, fontweight='bold', pad=15)
    save(fig, "fig12_gear_machine.png")


# ============================================================
# ILLUSTRATION 13: Euler four-square table
# ============================================================
def fig13_euler_table():
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    fig.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    # Euler's four-square identity:
    # (a1² + a2² + a3² + a4²)(b1² + b2² + b3² + b4²) = c1² + c2² + c3² + c4²
    # c1 = a1b1 - a2b2 - a3b3 - a4b4
    # c2 = a1b2 + a2b1 + a3b4 - a4b3
    # c3 = a1b3 - a2b4 + a3b1 + a4b2
    # c4 = a1b4 + a2b3 - a3b2 + a4b1

    table = [
        ['+a₁b₁', '-a₂b₂', '-a₃b₃', '-a₄b₄'],
        ['+a₁b₂', '+a₂b₁', '+a₃b₄', '-a₄b₃'],
        ['+a₁b₃', '-a₂b₄', '+a₃b₁', '+a₄b₂'],
        ['+a₁b₄', '+a₂b₃', '-a₃b₂', '+a₄b₁'],
    ]
    row_labels = ['$c_1$', '$c_2$', '$c_3$', '$c_4$']
    col_labels = ['$b_1$', '$b_2$', '$b_3$', '$b_4$']

    cell_w = 2.0
    cell_h = 1.2
    x0, y0 = 2.5, 6.5

    # Cartouche title
    ax.text(6, y0 + 2.0, "Euler's Quaternionic Table (1748)",
            fontsize=16, ha='center', color=DARK, fontweight='bold',
            fontstyle='italic',
            bbox=dict(boxstyle='round,pad=0.5', facecolor=GOLD, edgecolor=BRONZE,
                      linewidth=3, alpha=0.3))

    # Column headers
    for j, lbl in enumerate(col_labels):
        x = x0 + (j + 1) * cell_w
        rect = patches.FancyBboxPatch((x, y0), cell_w, cell_h,
                                       boxstyle="round,pad=0.05",
                                       facecolor=ACCENT2, edgecolor=DARK,
                                       linewidth=2, alpha=0.3)
        ax.add_patch(rect)
        ax.text(x + cell_w/2, y0 + cell_h/2, lbl, fontsize=14, ha='center',
                va='center', color=DARK, fontweight='bold')

    # Row headers + cells
    for i in range(4):
        y = y0 - (i + 1) * cell_h
        # Row header
        rect = patches.FancyBboxPatch((x0, y), cell_w, cell_h,
                                       boxstyle="round,pad=0.05",
                                       facecolor=ACCENT1, edgecolor=DARK,
                                       linewidth=2, alpha=0.3)
        ax.add_patch(rect)
        ax.text(x0 + cell_w/2, y + cell_h/2, row_labels[i], fontsize=14,
                ha='center', va='center', color=DARK, fontweight='bold')

        for j in range(4):
            x = x0 + (j + 1) * cell_w
            entry = table[i][j]
            bg = CREAM if entry.startswith('+') else LIGHT_RED
            rect = patches.FancyBboxPatch((x, y), cell_w, cell_h,
                                           boxstyle="round,pad=0.05",
                                           facecolor=bg, edgecolor=DARK,
                                           linewidth=1)
            ax.add_patch(rect)
            color = ACCENT3 if entry.startswith('+') else ACCENT1
            ax.text(x + cell_w/2, y + cell_h/2, entry, fontsize=11,
                    ha='center', va='center', color=color, fontweight='bold')

    # Ornamental border
    total_w = 5 * cell_w
    total_h = 5 * cell_h
    border = patches.FancyBboxPatch((x0 - 0.1, y0 - 4*cell_h - 0.1),
                                     total_w + 0.2, total_h + 0.2,
                                     boxstyle="round,pad=0.15",
                                     facecolor='none', edgecolor=BRONZE, linewidth=3)
    ax.add_patch(border)

    # Note
    ax.text(6, y0 - 4*cell_h - 0.8,
            "The quaternion multiplication rule, disguised as a sum-of-squares identity.",
            fontsize=10, ha='center', color=SLATE, fontstyle='italic')

    ax.set_xlim(1, 13)
    ax.set_ylim(0.5, 10)
    ax.axis('off')
    save(fig, "fig13_euler_table.png")


# ============================================================
# ILLUSTRATION 14: Venn diagram — k-tuples, congruences, modern factoring
# ============================================================
def fig14_venn_diagram():
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    fig.set_facecolor(PARCHMENT)
    ax.set_facecolor(PARCHMENT)

    cx, cy = 6, 5
    r = 3.0
    offset = 1.5

    # Three circles
    circles_data = [
        (cx - offset, cy + 0.8, "Pythagorean\n$k$-tuples", ACCENT2, LIGHT_BLUE),
        (cx + offset, cy + 0.8, "Modern factoring\n(QS, NFS)", ACCENT1, LIGHT_RED),
        (cx, cy - 1.0, "Congruences\nof squares", ACCENT3, LIGHT_GREEN),
    ]

    for ccx, ccy, label, edge_color, fill_color in circles_data:
        circle = plt.Circle((ccx, ccy), r, facecolor=fill_color, edgecolor=edge_color,
                             linewidth=3, alpha=0.3, zorder=2)
        ax.add_patch(circle)
        ax.text(ccx, ccy + 1.5, label, fontsize=13, ha='center', va='center',
                color=edge_color, fontweight='bold', zorder=5)

    # Center: golden glow
    center_x, center_y = cx, cy + 0.2
    glow_circle = plt.Circle((center_x, center_y), 0.8, facecolor=GLOW,
                              edgecolor=GOLD, linewidth=3, alpha=0.6, zorder=6)
    ax.add_patch(glow_circle)
    ax.text(center_x, center_y, "The factoring\nsweet spot", fontsize=10,
            ha='center', va='center', color=DARK, fontweight='bold', zorder=7)

    # Flow arrows
    # k-tuples -> congruences
    ax.annotate('', xy=(cx - 0.5, cy - 0.8), xytext=(cx - 1.5, cy + 0.3),
                arrowprops=dict(arrowstyle='->', color=SLATE, lw=1.5,
                                connectionstyle='arc3,rad=0.3'), zorder=3)
    ax.text(cx - 2.5, cy - 0.5, 'generate', fontsize=9, color=SLATE, fontstyle='italic')

    # congruences -> algorithms
    ax.annotate('', xy=(cx + 1.0, cy + 0.3), xytext=(cx + 0.2, cy - 0.8),
                arrowprops=dict(arrowstyle='->', color=SLATE, lw=1.5,
                                connectionstyle='arc3,rad=0.3'), zorder=3)
    ax.text(cx + 1.5, cy - 0.8, 'exploit', fontsize=9, color=SLATE, fontstyle='italic')

    # algorithms -> k-tuples
    ax.annotate('', xy=(cx - 1.0, cy + 1.2), xytext=(cx + 1.0, cy + 1.2),
                arrowprops=dict(arrowstyle='->', color=SLATE, lw=1.5,
                                connectionstyle='arc3,rad=0.3'), zorder=3)
    ax.text(cx, cy + 2.3, 'factor & generate', fontsize=9, ha='center',
            color=SLATE, fontstyle='italic')

    ax.set_xlim(0, 12)
    ax.set_ylim(-1, 10)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title("Three Roads to Factoring", fontsize=17, color=DARK,
                 fontweight='bold', pad=15)
    save(fig, "fig14_venn_diagram.png")


# ============================================================
# ILLUSTRATION 15: Pollard's rho — squaring map orbit
# ============================================================
def fig15_rho_orbit():
    fig, ax = plt.subplots(1, 1, figsize=(14, 7))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    # Simulate a rho-shaped orbit mod N
    # Use N = 35 as example
    N = 35
    x0_val = 2
    orbit = [x0_val]
    x = x0_val
    for _ in range(12):
        x = (x * x) % N
        orbit.append(x)
        if x in orbit[:-1]:
            break

    # For illustration, use a crafted orbit that shows the rho shape
    # tail + cycle
    tail = [2, 4, 16, 11]
    cycle = [16, 11, 16]  # cycle detected
    full_orbit = [2, 4, 16, 11, 16]  # rho shape: 2->4->16->11->16(cycle)

    # Layout: tail goes left to right, cycle goes in a loop
    tail_pts = [(1 + 2*i, 3) for i in range(4)]
    # cycle point wraps back
    cycle_pt = tail_pts[2]  # 16 is the meeting point

    # Draw tail
    for i, (x, y) in enumerate(tail_pts):
        ax.plot(x, y, 'o', color=ACCENT2, markersize=14, zorder=5,
                markeredgecolor=DARK, markeredgewidth=2)
        ax.text(x, y + 0.5, f'${full_orbit[i]}$', fontsize=12, ha='center',
                color=DARK, fontweight='bold')
        if i < 3:
            ax.annotate('', xy=(tail_pts[i+1][0] - 0.4, tail_pts[i+1][1]),
                        xytext=(x + 0.4, y),
                        arrowprops=dict(arrowstyle='->', color=DARK, lw=2))

    # Cycle: arrow from last point back to cycle entry
    # 11 -> 16 (loopback)
    ax.annotate('', xy=(tail_pts[2][0] + 0.1, tail_pts[2][1] - 0.4),
                xytext=(tail_pts[3][0], tail_pts[3][1] - 0.4),
                arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=2.5,
                                connectionstyle='arc3,rad=-0.5'))
    ax.text(5.5, 1.5, 'cycle!', fontsize=11, color=ACCENT1, fontweight='bold',
            fontstyle='italic')

    # Highlight collision
    collision_x = (tail_pts[2][0] + tail_pts[3][0]) / 2
    ax.text(collision_x, 4.5, 'Collision: $16 \\equiv 16$ (mod $N$)',
            fontsize=11, ha='center', color=ACCENT1, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=LIGHT_RED, edgecolor=ACCENT1))

    # GCD arrow
    ax.text(10, 3, r'$\gcd(x_i - x_j,\, N)$' + '\n= nontrivial factor',
            fontsize=13, ha='center', color=ACCENT3, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=LIGHT_GREEN, edgecolor=ACCENT3, linewidth=2))
    ax.annotate('', xy=(8.5, 3), xytext=(7.5, 3),
                arrowprops=dict(arrowstyle='->', color=ACCENT3, lw=2.5))

    # Number line at bottom
    ax.plot([0, 13], [0.5, 0.5], color=DARK, linewidth=1, zorder=1)
    for i in range(N):
        if i <= 12:
            ax.plot(0.5 + i, 0.5, '|', color=SLATE, markersize=3)
    ax.text(0, 0, '$0$', fontsize=8, ha='center', color=SLATE)
    ax.text(12, 0, '$N{-}1$', fontsize=8, ha='center', color=SLATE)

    # Squaring map label
    ax.text(3, 5.5, 'Squaring map orbit: $x \mapsto x^2$ mod $N$',
            fontsize=13, color=DARK, fontweight='bold')
    ax.text(3, 5.0, 'The rho shape: tail + cycle = collision reveals factors',
            fontsize=10, color=SLATE, fontstyle='italic')

    ax.set_xlim(-0.5, 13.5)
    ax.set_ylim(-0.5, 6.5)
    ax.axis('off')
    ax.set_title("Pollard's Rho: Collisions in the Squaring Map",
                 fontsize=16, color=DARK, fontweight='bold', pad=15)
    save(fig, "fig15_rho_orbit.png")


# ============================================================
# ILLUSTRATION 16: Octopus's garden — closing illustration
# ============================================================
def fig16_octopus_garden():
    fig, ax = plt.subplots(1, 1, figsize=(12, 12))
    fig.set_facecolor('#E8F5E9')  # Garden green
    ax.set_facecolor('#E8F5E9')

    cx, cy = 6, 6

    # Ground vault
    vault = patches.FancyBboxPatch((4, 0.5), 4, 3,
                                    boxstyle="round,pad=0.2",
                                    facecolor='#8B8682', edgecolor=DARK,
                                    linewidth=3, zorder=3)
    ax.add_patch(vault)
    ax.text(6, 2, '$N$', fontsize=36, ha='center', va='center',
            color=CREAM, fontweight='bold', zorder=5,
            path_effects=[pe.withStroke(linewidth=4, foreground=DARK)])

    # Keyholes in vault
    for i in range(7):
        kx = 4.5 + i * 0.45
        ky = 1.2
        kh = plt.Circle((kx, ky), 0.12, color=DARK, zorder=6)
        ax.add_patch(kh)
        rect = patches.Rectangle((kx - 0.04, ky - 0.25), 0.08, 0.2,
                                  color=DARK, zorder=6)
        ax.add_patch(rect)

    # Octopus body
    body = plt.Circle((cx, cy + 2), 1.2, facecolor=ACCENT4, edgecolor=DARK,
                       linewidth=2, alpha=0.8, zorder=7)
    ax.add_patch(body)

    # Eyes
    ax.plot(cx - 0.3, cy + 2.3, 'o', color='white', markersize=10, zorder=8)
    ax.plot(cx + 0.3, cy + 2.3, 'o', color='white', markersize=10, zorder=8)
    ax.plot(cx - 0.3, cy + 2.3, 'o', color=DARK, markersize=4, zorder=9)
    ax.plot(cx + 0.3, cy + 2.3, 'o', color=DARK, markersize=4, zorder=9)
    # Smile
    smile_t = np.linspace(-0.5, 0.5, 20)
    ax.plot(cx + smile_t * 0.6, cy + 1.7 + 0.15 * np.cos(smile_t * np.pi),
            color=DARK, linewidth=2, zorder=9)

    # Tentacles reaching to keyholes
    for i in range(7):
        kx = 4.5 + i * 0.45
        ky = 1.2
        # Curvy tentacle
        t = np.linspace(0, 1, 30)
        tx = cx + (kx - cx) * t + 0.3 * np.sin(t * 3 * np.pi)
        ty = cy + 0.8 + (ky - cy - 0.8) * t + 0.2 * np.cos(t * 2 * np.pi)
        ax.plot(tx, ty, color=ACCENT4, linewidth=2.5, alpha=0.7, zorder=4)

    # 8th tentacle waving
    t = np.linspace(0, 1, 30)
    tx = cx + 2 * t + 0.3 * np.sin(t * 3 * np.pi)
    ty = cy + 2 + 1.5 * t + 0.3 * np.cos(t * 2 * np.pi)
    ax.plot(tx, ty, color=ACCENT4, linewidth=2.5, alpha=0.7, zorder=4)

    # Thought bubble with equation
    ax.text(cx, cy + 5, r'$a_1^2 + a_2^2 + \cdots + a_7^2 = N^2$',
            fontsize=14, ha='center', color=DARK, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                      edgecolor=ACCENT4, linewidth=2, alpha=0.9), zorder=10)
    # Bubble connectors
    for r_val, offset in [(0.15, 0.5), (0.1, 1.0)]:
        b = plt.Circle((cx - 0.5, cy + 3.2 + offset), r_val, facecolor='white',
                        edgecolor=ACCENT4, linewidth=1, zorder=9)
        ax.add_patch(b)

    # Flowers shaped like prime numbers
    primes = [3, 5, 7, 11, 13]
    flower_positions = [(1.5, 1.5), (2, 4), (10, 2), (10.5, 5), (1, 7)]
    for (fx, fy), p in zip(flower_positions, primes):
        # Stem
        ax.plot([fx, fx], [fy - 0.8, fy], color=ACCENT3, linewidth=2, zorder=2)
        # Flower head
        flower = plt.Circle((fx, fy), 0.4, facecolor=GLOW, edgecolor=ACCENT5,
                             linewidth=2, zorder=3)
        ax.add_patch(flower)
        ax.text(fx, fy, str(p), fontsize=12, ha='center', va='center',
                color=DARK, fontweight='bold', zorder=4)
        # Petals
        for j in range(5):
            angle = j * 2 * np.pi / 5
            px = fx + 0.35 * np.cos(angle)
            py = fy + 0.35 * np.sin(angle)
            petal = plt.Circle((px, py), 0.12, facecolor=ACCENT5, alpha=0.3, zorder=2)
            ax.add_patch(petal)

    # Lattice points in background
    for ix in range(0, 13, 1):
        for iy in range(0, 13, 1):
            ax.plot(ix, iy, '.', color=ACCENT3, alpha=0.1, markersize=2, zorder=1)

    # Caption
    ax.text(6, -0.5, "The octopus's garden: seven tentacles, "
            "twenty-eight channels, one happy factorer.",
            fontsize=11, ha='center', color=DARK, fontstyle='italic')

    ax.set_xlim(-0.5, 12.5)
    ax.set_ylim(-1.5, 12.5)
    ax.set_aspect('equal')
    ax.axis('off')
    save(fig, "fig16_octopus_garden.png")


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("Generating Chapter 6 illustrations...")
    fig01_vault_door()
    fig02_phylogenetic_tree()
    fig03_specimen_catalog()
    fig04_lock_N15()
    fig05_lock_N21()
    fig06_K7_channels()
    fig07_inside_out()
    fig08_maze()
    fig09_berggren_descent()
    fig10_reflection_tetrahedra()
    fig11_dimensional_elevator()
    fig12_gear_machine()
    fig13_euler_table()
    fig14_venn_diagram()
    fig15_rho_orbit()
    fig16_octopus_garden()
    print("Done! All images saved to", OUT)

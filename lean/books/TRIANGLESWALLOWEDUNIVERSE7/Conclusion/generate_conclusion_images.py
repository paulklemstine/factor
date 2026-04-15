#!/usr/bin/env python3
"""Generate all illustrations for the Conclusion: The Rosetta Stone."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Arc, Wedge
import matplotlib.patheffects as pe
import numpy as np
import os
from math import gcd, pi, sin, cos

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
NIGHT = '#0C1445'
DEEP_BLUE = '#1A2980'
STAR_GOLD = '#FFD700'

def save(fig, name, dpi=200):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=dpi, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  Saved {name}")


# ============================================================
# ILLUSTRATION 1: The Rope-Stretcher's Return — Night Sky
# ============================================================
def fig01_rope_stretcher_return():
    """An aged rope-stretcher beside the Nile at dusk.
    The sky shows mathematical structures radiating from a 3-4-5 constellation."""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    fig.set_facecolor(NIGHT)
    ax.set_facecolor(NIGHT)

    # --- Sky gradient (dark blue to purple at horizon) ---
    for i in range(100):
        y_lo = 2.5 + i * 0.075
        y_hi = y_lo + 0.08
        t = i / 100.0
        r = int(12 + t * 30)
        g = int(20 + t * 20)
        b = int(69 + t * 60)
        ax.axhspan(y_lo, y_hi, color=f'#{r:02x}{g:02x}{b:02x}', alpha=0.8, zorder=0)

    # --- Random background stars ---
    np.random.seed(42)
    n_stars = 200
    sx = np.random.uniform(-1, 15, n_stars)
    sy = np.random.uniform(3.5, 10, n_stars)
    ss = np.random.uniform(0.3, 2.5, n_stars)
    sa = np.random.uniform(0.3, 1.0, n_stars)
    for i in range(n_stars):
        ax.plot(sx[i], sy[i], '*', color='white', markersize=ss[i], alpha=sa[i], zorder=1)

    # --- The 3-4-5 constellation (three bright stars) ---
    # Triangle vertices in sky coordinates
    cx, cy = 7, 7  # center of the constellation
    s = 1.2  # scale
    star_A = (cx, cy)           # right angle vertex
    star_B = (cx + 4*s, cy)     # along base
    star_C = (cx, cy + 3*s)     # along height

    for (stx, sty) in [star_A, star_B, star_C]:
        ax.plot(stx, sty, '*', color=STAR_GOLD, markersize=18, zorder=10,
                markeredgecolor='white', markeredgewidth=0.3)
        # glow
        circle = plt.Circle((stx, sty), 0.25, color=STAR_GOLD, alpha=0.15, zorder=9)
        ax.add_patch(circle)

    # Connect stars to form triangle
    tri_x = [star_A[0], star_B[0], star_C[0], star_A[0]]
    tri_y = [star_A[1], star_B[1], star_C[1], star_A[1]]
    ax.plot(tri_x, tri_y, color=STAR_GOLD, linewidth=1.5, alpha=0.7, zorder=8)

    # Labels on the constellation
    ax.text(cx + 2*s, cy - 0.35, '4', fontsize=11, color=STAR_GOLD, ha='center', fontstyle='italic', zorder=11)
    ax.text(cx - 0.4, cy + 1.5*s, '3', fontsize=11, color=STAR_GOLD, ha='center', fontstyle='italic', zorder=11)
    ax.text(cx + 2.2*s, cy + 1.8*s, '5', fontsize=11, color=STAR_GOLD, ha='center', fontstyle='italic',
            rotation=-37, zorder=11)

    # --- Radiating structures from the constellation ---
    # Mini ternary tree (upper right)
    def draw_mini_tree(cx, cy, scale, depth, ax):
        if depth == 0:
            return
        ax.plot(cx, cy, 'o', color=STAR_GOLD, markersize=3*scale, alpha=0.6, zorder=7)
        for angle_off in [-30, 0, 30]:
            angle = 90 + angle_off
            dx = scale * 0.8 * cos(np.radians(angle))
            dy = scale * 0.8 * sin(np.radians(angle))
            nx, ny = cx + dx, cy + dy
            ax.plot([cx, nx], [cy, ny], color=STAR_GOLD, linewidth=0.5, alpha=0.4, zorder=6)
            draw_mini_tree(nx, ny, scale * 0.5, depth - 1, ax)

    draw_mini_tree(10, 9, 1.0, 4, ax)

    # Mini light cone (upper left)
    lc_cx, lc_cy = 3.5, 8.5
    lc_h = 1.5
    # Two diagonal lines forming a cone
    ax.plot([lc_cx, lc_cx - 0.8], [lc_cy, lc_cy + lc_h], color=LIGHT_BLUE, linewidth=1.2, alpha=0.5, zorder=6)
    ax.plot([lc_cx, lc_cx + 0.8], [lc_cy, lc_cy + lc_h], color=LIGHT_BLUE, linewidth=1.2, alpha=0.5, zorder=6)
    ax.plot([lc_cx, lc_cx - 0.8], [lc_cy, lc_cy - lc_h], color=LIGHT_BLUE, linewidth=1.2, alpha=0.5, zorder=6)
    ax.plot([lc_cx, lc_cx + 0.8], [lc_cy, lc_cy - lc_h], color=LIGHT_BLUE, linewidth=1.2, alpha=0.5, zorder=6)
    # Ellipse at cone cross-section
    ell = patches.Ellipse((lc_cx, lc_cy + lc_h), 1.6, 0.3, color=LIGHT_BLUE, fill=False,
                           linewidth=0.8, alpha=0.5, zorder=6)
    ax.add_patch(ell)
    ell2 = patches.Ellipse((lc_cx, lc_cy - lc_h), 1.6, 0.3, color=LIGHT_BLUE, fill=False,
                            linewidth=0.8, alpha=0.5, zorder=6)
    ax.add_patch(ell2)

    # Mini lattice grid (left)
    lg_cx, lg_cy = 2, 6
    for i in range(5):
        for j in range(4):
            ax.plot(lg_cx + i * 0.35, lg_cy + j * 0.35, '.', color=LIGHT_GREEN,
                    markersize=2, alpha=0.5, zorder=6)

    # Mini algebra tower (right)
    tw_x, tw_y = 12, 6.5
    for i, label in enumerate(['ℝ', 'ℂ', 'ℍ', '𝕆']):
        y = tw_y + i * 0.6
        rect = patches.FancyBboxPatch((tw_x - 0.3, y - 0.15), 0.6, 0.3,
                                       boxstyle="round,pad=0.05",
                                       facecolor=ACCENT4, alpha=0.3 + i * 0.15,
                                       edgecolor=STAR_GOLD, linewidth=0.5, zorder=7)
        ax.add_patch(rect)
        ax.text(tw_x, y, label, fontsize=7, color='white', ha='center', va='center',
                fontweight='bold', zorder=8)

    # Mini quantum circuit (far right)
    qc_x, qc_y = 13, 8.5
    for i in range(3):
        ax.plot([qc_x, qc_x + 1.2], [qc_y + i * 0.3, qc_y + i * 0.3],
                color=LIGHT_BLUE, linewidth=0.7, alpha=0.5, zorder=6)
    # Gate boxes
    for (gx, gy) in [(qc_x + 0.3, qc_y), (qc_x + 0.6, qc_y + 0.3), (qc_x + 0.9, qc_y + 0.6)]:
        rect = patches.Rectangle((gx - 0.1, gy - 0.08), 0.2, 0.16,
                                  facecolor=ACCENT2, alpha=0.5, edgecolor='white',
                                  linewidth=0.5, zorder=7)
        ax.add_patch(rect)

    # --- Nile water (bottom portion) ---
    # Water
    for i in range(30):
        y = 0 + i * 0.083
        alpha = 0.4 + 0.3 * (1 - i / 30.0)
        ax.axhspan(y, y + 0.09, color='#0A2472', alpha=alpha, zorder=2)

    # Reflection ripples
    for i in range(8):
        rx = np.random.uniform(1, 13)
        ry = np.random.uniform(0.3, 2.2)
        rw = np.random.uniform(0.5, 2.0)
        ax.plot([rx, rx + rw], [ry, ry], color=STAR_GOLD, linewidth=0.4, alpha=0.2, zorder=3)

    # Faint reflection of the triangle in the water
    for (x1, y1), (x2, y2) in [(star_A, star_B), (star_B, star_C), (star_C, star_A)]:
        ry1 = 2.5 - (y1 - 2.5) * 0.25
        ry2 = 2.5 - (y2 - 2.5) * 0.25
        ax.plot([x1, x2], [ry1, ry2], color=STAR_GOLD, linewidth=0.8, alpha=0.15, zorder=3)

    # --- Ground / riverbank ---
    bank_x = np.linspace(-1, 15, 200)
    bank_y = 2.5 + 0.15 * np.sin(bank_x * 0.8) + 0.1 * np.sin(bank_x * 2.1)
    ax.fill_between(bank_x, 2.0, bank_y, color='#3D2B1F', zorder=4)

    # --- Rope-stretcher figure (silhouette on limestone block) ---
    # Limestone block
    block = patches.FancyBboxPatch((1.5, 2.3), 1.2, 0.8, boxstyle="round,pad=0.05",
                                    facecolor='#8B7D6B', edgecolor='#5C4A3A',
                                    linewidth=1, zorder=5)
    ax.add_patch(block)

    # Seated figure (simplified silhouette)
    # Body
    body_x = [2.0, 1.9, 2.0, 2.3, 2.4, 2.3]
    body_y = [3.1, 3.5, 4.0, 4.0, 3.5, 3.1]
    ax.fill(body_x, body_y, color=DARK, zorder=6)
    # Head
    head = plt.Circle((2.15, 4.2), 0.22, color=DARK, zorder=6)
    ax.add_patch(head)

    # --- Apprentice figure (standing, gesturing at sky) ---
    # Standing figure
    app_x = [3.2, 3.1, 3.15, 3.35, 3.4, 3.3]
    app_y = [2.8, 3.3, 4.2, 4.2, 3.3, 2.8]
    ax.fill(app_x, app_y, color=DARK, zorder=6)
    app_head = plt.Circle((3.25, 4.42), 0.2, color=DARK, zorder=6)
    ax.add_patch(app_head)

    # Raised arm pointing at sky
    ax.plot([3.35, 4.0, 5.0], [4.0, 4.8, 5.5], color=DARK, linewidth=2.5, zorder=6)

    # Dotted line from hand to constellation
    ax.plot([5.0, star_A[0]], [5.5, star_A[1]], ':', color=STAR_GOLD, linewidth=0.8,
            alpha=0.4, zorder=5)

    # --- Title text ---
    ax.text(7, 0.8, 'The Constellation of Pythagoras',
            fontsize=16, color=STAR_GOLD, ha='center', fontstyle='italic',
            fontweight='bold', alpha=0.7, zorder=10,
            path_effects=[pe.withStroke(linewidth=2, foreground=NIGHT)])

    ax.set_xlim(-0.5, 14.5)
    ax.set_ylim(-0.2, 10.5)
    ax.set_aspect('equal')
    ax.axis('off')
    save(fig, 'fig01_rope_stretcher_return.png')


# ============================================================
# ILLUSTRATION 2: The Rosetta Stone Mandala
# ============================================================
def fig02_rosetta_mandala():
    """Nine spokes radiating from the central equation to domain vignettes."""
    fig, ax = plt.subplots(1, 1, figsize=(14, 14))
    fig.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    center = (0, 0)
    outer_r = 5.0
    inner_r = 1.2
    mid_r = 3.2

    # --- Central stone tablet ---
    tablet = patches.FancyBboxPatch((-1.5, -0.8), 3.0, 1.6,
                                     boxstyle="round,pad=0.15",
                                     facecolor='#C4A882', edgecolor='#6B5B3E',
                                     linewidth=3, zorder=10)
    ax.add_patch(tablet)

    # Stone texture lines
    for i in range(8):
        y = -0.6 + i * 0.2
        ax.plot([-1.3, 1.3], [y, y + 0.02], color='#A89070', linewidth=0.3, alpha=0.4, zorder=11)

    ax.text(0, 0, r'$a^2 + b^2 = c^2$', fontsize=22, ha='center', va='center',
            color=DARK, fontweight='bold', zorder=12,
            fontfamily='serif')

    # --- Nine spokes with labels and vignettes ---
    spoke_labels = [
        'Berggren\nTree',
        'Light\nCone',
        'Euclid\'s\nAlgorithm',
        'Lattice\nReduction',
        'Integer\nFactoring',
        'Cayley–Dickson\nAlgebras',
        'Quantum\nSearch',
        'Tropical\nGeometry',
        'Fermat\'s\nLast Theorem',
    ]
    spoke_colors = [
        ACCENT3,   # green - tree
        ACCENT2,   # blue - light cone
        ACCENT5,   # orange - Euclid
        ACCENT1,   # red - lattice
        GOLD,      # gold - factoring
        ACCENT4,   # purple - Cayley-Dickson
        LIGHT_BLUE,  # light blue - quantum
        ACCENT3,   # green - tropical
        ACCENT1,   # red - Fermat
    ]

    for i in range(9):
        angle = 90 + i * 40  # 360/9 = 40 degrees apart
        rad = np.radians(angle)

        # Spoke line
        x1 = inner_r * cos(rad)
        y1 = inner_r * sin(rad)
        x2 = mid_r * cos(rad)
        y2 = mid_r * sin(rad)
        x3 = outer_r * cos(rad)
        y3 = outer_r * sin(rad)

        ax.plot([x1, x3], [y1, y3], color=spoke_colors[i], linewidth=2.5,
                alpha=0.6, zorder=5)

        # Label
        lx = (mid_r + 0.3) * cos(rad)
        ly = (mid_r + 0.3) * sin(rad)
        ax.text(lx, ly, spoke_labels[i], fontsize=8, ha='center', va='center',
                color=DARK, fontweight='bold', zorder=8,
                bbox=dict(boxstyle='round,pad=0.2', facecolor=CREAM, alpha=0.8, edgecolor='none'))

        # Vignette circle at the end
        vign = plt.Circle((x3, y3), 0.6, facecolor='white', edgecolor=spoke_colors[i],
                           linewidth=2, alpha=0.9, zorder=7)
        ax.add_patch(vign)

        # Draw vignette icons
        _draw_vignette(ax, i, x3, y3, spoke_colors[i])

    # --- Outer rim with text ---
    rim = plt.Circle((0, 0), outer_r + 1.0, facecolor='none', edgecolor='#8B7D6B',
                      linewidth=2.5, linestyle='--', alpha=0.5, zorder=3)
    ax.add_patch(rim)

    # Rim text (curved approximation using placed text)
    rim_text = "Every theorem in this book is a consequence of this single line"
    n_chars = len(rim_text)
    rim_r = outer_r + 1.15
    start_angle = 160
    for idx, ch in enumerate(rim_text):
        a = np.radians(start_angle - idx * 4.5)
        tx = rim_r * cos(a)
        ty = rim_r * sin(a)
        rot = start_angle - idx * 4.5 - 90
        ax.text(tx, ty, ch, fontsize=6.5, ha='center', va='center',
                color='#6B5B3E', rotation=rot, fontstyle='italic', zorder=4)

    # Decorative inner ring
    inner_ring = plt.Circle((0, 0), inner_r, facecolor='none', edgecolor='#C4A882',
                             linewidth=2, zorder=9)
    ax.add_patch(inner_ring)

    ax.set_xlim(-7, 7)
    ax.set_ylim(-7, 7)
    ax.set_aspect('equal')
    ax.axis('off')
    save(fig, 'fig02_rosetta_mandala.png')


def _draw_vignette(ax, idx, cx, cy, color):
    """Draw a tiny iconic image for each spoke."""
    s = 0.35  # scale

    if idx == 0:  # Ternary tree
        # Simple tree structure
        ax.plot(cx, cy + s * 0.4, 'o', color=GOLD, markersize=5, zorder=20)
        for dx in [-s * 0.6, 0, s * 0.6]:
            ax.plot([cx, cx + dx], [cy + s * 0.4, cy - s * 0.3],
                    color=color, linewidth=1.2, zorder=19)
            ax.plot(cx + dx, cy - s * 0.3, 'o', color=GOLD, markersize=3, zorder=20)

    elif idx == 1:  # Light cone
        ax.plot([cx, cx - s * 0.5], [cy, cy + s * 0.7], color=color, linewidth=1.5, zorder=19)
        ax.plot([cx, cx + s * 0.5], [cy, cy + s * 0.7], color=color, linewidth=1.5, zorder=19)
        ax.plot([cx, cx - s * 0.5], [cy, cy - s * 0.7], color=color, linewidth=1.5, zorder=19)
        ax.plot([cx, cx + s * 0.5], [cy, cy - s * 0.7], color=color, linewidth=1.5, zorder=19)
        # Photon
        ax.plot(cx + s * 0.25, cy + s * 0.35, '*', color=STAR_GOLD, markersize=6, zorder=20)

    elif idx == 2:  # Euclid staircase
        pts = [(cx - s * 0.5, cy - s * 0.5)]
        for i in range(4):
            x0, y0 = pts[-1]
            pts.append((x0 + s * 0.25, y0))
            pts.append((x0 + s * 0.25, y0 + s * 0.25))
        xs, ys = zip(*pts)
        ax.plot(xs, ys, color=color, linewidth=1.5, zorder=19)

    elif idx == 3:  # 3D lattice points
        for i in range(3):
            for j in range(3):
                ax.plot(cx - s * 0.4 + i * s * 0.4, cy - s * 0.4 + j * s * 0.4,
                        'o', color=color, markersize=2.5, zorder=19)
        # Highlight short vector
        ax.annotate('', xy=(cx + s * 0.4, cy), xytext=(cx - s * 0.4, cy - s * 0.4),
                     arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=1.5), zorder=20)

    elif idx == 4:  # Padlock with GCD key
        # Lock body
        lock = patches.FancyBboxPatch((cx - s * 0.3, cy - s * 0.4), s * 0.6, s * 0.5,
                                       boxstyle="round,pad=0.02",
                                       facecolor=GOLD, edgecolor=DARK, linewidth=1, zorder=19)
        ax.add_patch(lock)
        # Shackle
        shackle = Arc((cx, cy + s * 0.1), s * 0.4, s * 0.5, angle=0,
                       theta1=0, theta2=180, color=DARK, linewidth=1.5, zorder=19)
        ax.add_patch(shackle)
        # Keyhole
        ax.plot(cx, cy - s * 0.15, 'o', color=DARK, markersize=2, zorder=20)

    elif idx == 5:  # Algebra tower
        floors = ['ℂ', 'ℍ', '𝕆']
        for i, label in enumerate(floors):
            y = cy - s * 0.5 + i * s * 0.35
            rect = patches.Rectangle((cx - s * 0.25, y), s * 0.5, s * 0.3,
                                      facecolor=ACCENT4, alpha=0.4 + i * 0.2,
                                      edgecolor=color, linewidth=0.8, zorder=19)
            ax.add_patch(rect)
            ax.text(cx, y + s * 0.15, label, fontsize=5, ha='center', va='center',
                    color='white', fontweight='bold', zorder=20)

    elif idx == 6:  # Quantum circuit / magnifying glass
        # Magnifying glass
        lens = plt.Circle((cx, cy + s * 0.1), s * 0.3, facecolor='none',
                           edgecolor=color, linewidth=1.5, zorder=19)
        ax.add_patch(lens)
        ax.plot([cx + s * 0.2, cx + s * 0.5], [cy - s * 0.15, cy - s * 0.45],
                color=color, linewidth=2, zorder=19)
        # Wave inside
        wx = np.linspace(cx - s * 0.2, cx + s * 0.2, 20)
        wy = cy + s * 0.1 + 0.05 * np.sin((wx - cx) * 30)
        ax.plot(wx, wy, color=ACCENT2, linewidth=0.8, zorder=20)

    elif idx == 7:  # Tropical curve (piecewise-linear)
        # Simple PL curve
        pts_x = [cx - s * 0.5, cx - s * 0.1, cx + s * 0.1, cx + s * 0.5]
        pts_y = [cy + s * 0.2, cy - s * 0.3, cy + s * 0.4, cy - s * 0.1]
        ax.plot(pts_x, pts_y, color=color, linewidth=1.5, zorder=19)
        # Palm tree hint
        ax.plot(cx + s * 0.3, cy + s * 0.1, '*', color=ACCENT3, markersize=5, zorder=20)

    elif idx == 8:  # Torn parchment / Fermat's margin
        # Parchment rectangle
        parch = patches.FancyBboxPatch((cx - s * 0.35, cy - s * 0.45), s * 0.7, s * 0.9,
                                        boxstyle="round,pad=0.03",
                                        facecolor='#F5E6C8', edgecolor='#8B7D6B',
                                        linewidth=1, zorder=19)
        ax.add_patch(parch)
        # Torn edge
        tear_x = [cx + s * 0.35, cx + s * 0.3, cx + s * 0.35, cx + s * 0.28, cx + s * 0.35]
        tear_y = [cy - s * 0.45, cy - s * 0.2, cy, cy + s * 0.2, cy + s * 0.45]
        ax.plot(tear_x, tear_y, color='#8B7D6B', linewidth=1, zorder=20)
        # Text lines
        for i in range(4):
            y = cy + s * 0.25 - i * s * 0.15
            ax.plot([cx - s * 0.25, cx + s * 0.15], [y, y],
                    color='#8B7D6B', linewidth=0.5, alpha=0.5, zorder=20)


# ============================================================
# ILLUSTRATION 3: The Final Triangle — Door of Light
# ============================================================
def fig03_final_triangle():
    """A clean 3-4-5 triangle with a tiny door at the right-angle vertex,
    golden light spilling through revealing mathematical structures."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 9))
    fig.set_facecolor('white')
    ax.set_facecolor('white')

    # Main triangle coordinates (scaled for visual clarity)
    scale = 1.8
    A = np.array([0, 0])         # right-angle vertex
    B = np.array([4 * scale, 0])  # base
    C = np.array([0, 3 * scale])  # height

    # Draw the main triangle in clean black ink
    tri_x = [A[0], B[0], C[0], A[0]]
    tri_y = [A[1], B[1], C[1], A[1]]
    ax.plot(tri_x, tri_y, color='black', linewidth=2.5, zorder=10)

    # Right-angle square
    sq = 0.4
    ax.plot([sq, sq, 0], [0, sq, sq], color='black', linewidth=1.5, zorder=10)

    # Side labels
    ax.text(scale * 2, -0.5, '$b = 4$', fontsize=14, ha='center', color='black',
            fontfamily='serif', zorder=11)
    ax.text(-0.7, scale * 1.5, '$a = 3$', fontsize=14, ha='center', color='black',
            fontfamily='serif', zorder=11)
    ax.text(scale * 2.3, scale * 1.8, '$c = 5$', fontsize=14, ha='center', color='black',
            fontfamily='serif', rotation=-37, zorder=11)

    # --- Tiny door at right-angle vertex ---
    door_w = 0.35
    door_h = 0.6
    door_x = A[0] + 0.15
    door_y = A[1] + 0.15

    # Door frame
    door = patches.FancyBboxPatch((door_x, door_y), door_w, door_h,
                                   boxstyle="round,pad=0.02",
                                   facecolor='#2C1810', edgecolor='#2C1810',
                                   linewidth=1.5, zorder=12)
    ax.add_patch(door)

    # Door opening (slightly ajar — a sliver of golden light)
    opening = patches.FancyBboxPatch((door_x + door_w * 0.3, door_y + 0.02),
                                      door_w * 0.65, door_h - 0.04,
                                      boxstyle="round,pad=0.01",
                                      facecolor=GOLD, edgecolor='none',
                                      linewidth=0, zorder=13, alpha=0.9)
    ax.add_patch(opening)

    # Door knob
    ax.plot(door_x + door_w * 0.25, door_y + door_h * 0.45, 'o',
            color=GOLD, markersize=3, zorder=14)

    # --- Golden light spilling from the door ---
    # Light rays spreading inward into the triangle
    light_origin = np.array([door_x + door_w * 0.6, door_y + door_h * 0.5])
    n_rays = 15
    for i in range(n_rays):
        angle = np.radians(10 + i * (70 / n_rays))
        length = 1.5 + np.random.uniform(0, 2.5)
        dx = length * cos(angle)
        dy = length * sin(angle)
        endpoint = light_origin + np.array([dx, dy])
        # Check if endpoint is inside triangle (roughly)
        alpha = 0.08 + 0.04 * np.random.random()
        ax.plot([light_origin[0], endpoint[0]], [light_origin[1], endpoint[1]],
                color=GOLD, linewidth=0.8, alpha=alpha, zorder=8)

    # Light glow around door
    for r, a in [(0.5, 0.15), (0.8, 0.08), (1.2, 0.04)]:
        glow = plt.Circle(light_origin, r, facecolor=GOLD, alpha=a, edgecolor='none', zorder=7)
        ax.add_patch(glow)

    # --- Faint mathematical structures visible in the light ---
    # These are drawn with low alpha inside the triangle

    # Mini tree
    tx, ty = 2.5, 2.0
    ax.plot(tx, ty, 'o', color=GOLD, markersize=3, alpha=0.2, zorder=8)
    for dx in [-0.6, 0, 0.6]:
        ax.plot([tx, tx + dx], [ty, ty - 0.5], color=GOLD, linewidth=0.6, alpha=0.15, zorder=8)
        ax.plot(tx + dx, ty - 0.5, 'o', color=GOLD, markersize=2, alpha=0.15, zorder=8)

    # Mini lattice
    for i in range(4):
        for j in range(3):
            ax.plot(1.0 + i * 0.3, 1.0 + j * 0.3, '.', color=GOLD,
                    markersize=1.5, alpha=0.15, zorder=8)

    # Mini cone
    ccx, ccy = 4.5, 1.5
    ax.plot([ccx, ccx - 0.4], [ccy, ccy + 0.6], color=GOLD, linewidth=0.5, alpha=0.12, zorder=8)
    ax.plot([ccx, ccx + 0.4], [ccy, ccy + 0.6], color=GOLD, linewidth=0.5, alpha=0.12, zorder=8)
    ax.plot([ccx, ccx - 0.4], [ccy, ccy - 0.6], color=GOLD, linewidth=0.5, alpha=0.12, zorder=8)
    ax.plot([ccx, ccx + 0.4], [ccy, ccy - 0.6], color=GOLD, linewidth=0.5, alpha=0.12, zorder=8)

    # Mini tower
    for i in range(3):
        y = 3.2 + i * 0.25
        rect = patches.Rectangle((1.8, y), 0.4, 0.2,
                                  facecolor=GOLD, alpha=0.1, edgecolor=GOLD,
                                  linewidth=0.3, zorder=8)
        ax.add_patch(rect)

    # Mini staircase
    pts = [(3.5, 0.8)]
    for i in range(5):
        x0, y0 = pts[-1]
        pts.append((x0 + 0.2, y0))
        pts.append((x0 + 0.2, y0 + 0.15))
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=GOLD, linewidth=0.5, alpha=0.12, zorder=8)

    # --- Caption below ---
    ax.text(scale * 2, -1.5,
            '"The simplest objects in mathematics hide the deepest structures."',
            fontsize=11, ha='center', color='#555555', fontstyle='italic',
            fontfamily='serif', zorder=11)

    ax.set_xlim(-1.5, scale * 4 + 1.5)
    ax.set_ylim(-2.2, scale * 3 + 1)
    ax.set_aspect('equal')
    ax.axis('off')
    save(fig, 'fig03_final_triangle.png')


# ============================================================
# RUN ALL
# ============================================================
if __name__ == '__main__':
    print("Generating Conclusion illustrations...")
    fig01_rope_stretcher_return()
    fig02_rosetta_mandala()
    fig03_final_triangle()
    print("Done! All images saved to", OUT)

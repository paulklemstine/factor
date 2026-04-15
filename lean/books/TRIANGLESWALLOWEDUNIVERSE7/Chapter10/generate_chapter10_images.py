#!/usr/bin/env python3
"""Generate all illustrations for Chapter 10: The Margin That Shook the World."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Arc
import matplotlib.patheffects as pe
import numpy as np
import os
from math import gcd

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
# FIG 1: Near-miss meter
# ============================================================
def fig01_near_miss_meter():
    fig, axes = plt.subplots(2, 1, figsize=(14, 8), gridspec_kw={'height_ratios': [1, 1]})
    fig.set_facecolor(SAND)
    for ax in axes:
        ax.set_facecolor(SAND)

    # --- Row 1: 6^3 + 8^3 = 728 vs 9^3 = 729 ---
    ax = axes[0]
    ax.set_xlim(720, 740)
    ax.set_ylim(-1, 3)
    ax.axhline(y=0, color=DARK, linewidth=2)

    for x in range(720, 741):
        h = 0.15 if x % 5 != 0 else 0.25
        ax.plot([x, x], [0, h], color=DARK, linewidth=1)
        if x % 5 == 0:
            ax.text(x, -0.2, str(x), ha='center', va='top', fontsize=9, color=DARK)

    ax.plot(728, 0, 'o', color=ACCENT1, markersize=14, zorder=10)
    ax.plot(729, 0, 'o', color=ACCENT2, markersize=14, zorder=10)
    ax.text(728, 0.6, r'$6^3 + 8^3 = 728$', ha='center', fontsize=13, color=ACCENT1, fontweight='bold')
    ax.text(729, 0.6, r'$9^3 = 729$', ha='center', fontsize=13, color=ACCENT2, fontweight='bold')

    mag_cx, mag_cy = 728.5, 1.8
    circle = plt.Circle((mag_cx, mag_cy), 0.8, fill=False, edgecolor=DARK, linewidth=3, zorder=15)
    ax.add_patch(circle)
    ax.plot([mag_cx + 0.56, mag_cx + 1.5], [mag_cy - 0.56, mag_cy - 1.5],
            color=DARK, linewidth=3, zorder=15)
    ax.text(mag_cx, mag_cy + 0.1, r'GAP = 1', ha='center', va='center', fontsize=11,
            color=ACCENT1, fontweight='bold', zorder=20)
    ax.text(mag_cx, mag_cy - 0.25, r'A yawning chasm!', ha='center', va='center', fontsize=8,
            color=ACCENT4, style='italic', zorder=20)

    ax.set_title(r'Near-Miss Meter: Cubes', fontsize=15, color=DARK, fontweight='bold', pad=10)
    ax.axis('off')

    # --- Row 2: Simpsons equation ---
    ax = axes[1]
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.5, 3.5)

    ax.text(5, 2.5, r'$1782^{12} + 1841^{12}$', ha='center', fontsize=16, color=ACCENT1, fontweight='bold')
    ax.text(5, 1.7, r'vs.', ha='center', fontsize=14, color=DARK)
    ax.text(5, 0.9, r'$1922^{12}$', ha='center', fontsize=16, color=ACCENT2, fontweight='bold')

    ax.text(1, 1.7, r'Calculator says: $=$', ha='center', fontsize=12, color=ACCENT3, fontweight='bold')
    ax.text(9, 1.7, r'Reality: $\neq$', ha='center', fontsize=12, color=ACCENT1, fontweight='bold')

    calc_x, calc_y = 1, 0
    calc = FancyBboxPatch((calc_x - 0.5, calc_y - 0.3), 1.0, 0.8, boxstyle="round,pad=0.05",
                          facecolor='#E8E8E8', edgecolor=DARK, linewidth=2)
    ax.add_patch(calc)
    ax.text(calc_x, calc_y + 0.25, r'= ?!', ha='center', va='center', fontsize=10, color=ACCENT1, fontweight='bold')
    # Sweat drops as simple markers
    ax.plot(calc_x + 0.55, calc_y + 0.5, 'v', color=ACCENT2, markersize=6)
    ax.plot(calc_x - 0.55, calc_y + 0.45, 'v', color=ACCENT2, markersize=6)

    ax.text(5, -0.3, r'"Close only counts in horseshoes."', ha='center', fontsize=14,
            color=DARK, style='italic', fontweight='bold')

    ax.axis('off')

    fig.suptitle('The Near-Miss Meter', fontsize=18, color=DARK, fontweight='bold', y=0.98)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    save(fig, 'fig01_near_miss_meter.png')


# ============================================================
# FIG 2: Fermat's margin note (facsimile style)
# ============================================================
def fig02_fermat_margin():
    fig, ax = plt.subplots(1, 1, figsize=(12, 9))
    fig.set_facecolor('#F0E4CC')
    ax.set_facecolor('#F5EDDA')

    ax.set_xlim(0, 12)
    ax.set_ylim(0, 9)

    page = FancyBboxPatch((0.3, 0.3), 11.4, 8.4, boxstyle="round,pad=0.1",
                          facecolor='#FAF3E3', edgecolor='#8B7355', linewidth=3)
    ax.add_patch(page)

    main_area = FancyBboxPatch((0.8, 0.8), 7.0, 7.4, boxstyle="round,pad=0.05",
                               facecolor='#FBF6EC', edgecolor='#C4A87C', linewidth=1, linestyle='--')
    ax.add_patch(main_area)

    latin_lines = [
        "QVAESTIO VIII.",
        "",
        "Propositum quadratum in duos",
        "quadratos dividere.",
        "",
        "Ut 16 in duos quadratos.",
        "",
        "Pono primum quadratum esse 1Q,",
        "ergo alterum erit 16 - 1Q.",
        "Oportet igitur ut 16 - 1Q sit",
        "quadratus. Fingo latus eius 1N - 4,",
        "igitur quadratus est 1Q + 16 - 8N,",
        "atque hic aequalis erit 16 - 1Q.",
        "",
        "Addatur utrique deficiens,",
        "& ex parte similia de similibus.",
        "Fit 2Q aequalis 8N,",
        "& 1N erit 4. Ergo unus quadratus",
        "erit 256/25, alter 144/25,",
        "& summa utriusque est 16."
    ]

    y_start = 7.8
    for i, line in enumerate(latin_lines):
        y = y_start - i * 0.34
        if y < 1.0:
            break
        style = 'italic'
        size = 9
        weight = 'normal'
        if 'QVAESTIO' in line:
            size = 11
            weight = 'bold'
            style = 'normal'
        ax.text(1.2, y, line, fontsize=size, color='#3C2415', style=style,
                fontweight=weight, fontfamily='serif')

    margin_area = FancyBboxPatch((8.2, 0.8), 3.0, 7.4, boxstyle="round,pad=0.05",
                                 facecolor='#FDF8EE', edgecolor='#C4A87C', linewidth=1, linestyle=':')
    ax.add_patch(margin_area)

    ax.annotate('', xy=(8.3, 8.5), xytext=(7.5, 8.5),
                arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=2))
    ax.text(7.8, 8.7, 'The margin', ha='center', fontsize=9, color=ACCENT1, style='italic')

    margin_text = [
        "Cubum autem in duos",
        "cubos, aut quadrato-",
        "quadratum in duos",
        "quadrato-quadratos,",
        "& generaliter nullam",
        "in infinitum ultra",
        "quadratum potestatem",
        "in duos eiusdem",
        "nominis fas est",
        "dividere.",
        "",
        "Cuius rei demonstra-",
        "tionem mirabilem",
        "sane detexi. Hanc",
        "marginis exiguitas",
        "non caperet.",
    ]

    y_start_margin = 7.0
    for i, line in enumerate(margin_text):
        y = y_start_margin - i * 0.32
        if y < 1.0:
            break
        ax.text(8.5, y, line, fontsize=7.5, color='#5C3D1A', style='italic',
                fontfamily='serif', fontweight='normal')

    ax.text(10.2, 1.5, '~', fontsize=20, color='#5C3D1A', fontfamily='serif', rotation=30)

    ink_x, ink_y = 10.5, 0.5
    ink_body = FancyBboxPatch((ink_x - 0.25, ink_y - 0.15), 0.5, 0.4,
                               boxstyle="round,pad=0.03", facecolor='#1A1A2E', edgecolor=DARK, linewidth=1.5)
    ax.add_patch(ink_body)
    ink_neck = FancyBboxPatch((ink_x - 0.12, ink_y + 0.25), 0.24, 0.15,
                               boxstyle="round,pad=0.02", facecolor='#1A1A2E', edgecolor=DARK, linewidth=1)
    ax.add_patch(ink_neck)
    ax.text(ink_x, ink_y + 0.1, 'INK', fontsize=5, color='white', ha='center', va='center')

    ax.text(6, 8.9, "Diophantus's Arithmetica  -  Bachet edition, 1621",
            ha='center', fontsize=13, color=DARK, fontweight='bold', fontfamily='serif')

    ax.axis('off')
    save(fig, 'fig02_fermat_margin.png')


# ============================================================
# FIG 3: Factor tree / Hasse diagram
# ============================================================
def fig03_factor_tree():
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    essential = {3, 4, 5, 7, 11, 13, 17, 19}
    composites = {6: [3], 8: [4], 9: [3], 10: [5], 12: [3, 4], 14: [7], 15: [3, 5],
                  16: [4], 18: [3], 20: [4, 5]}

    essential_list = sorted(essential)
    composite_list = sorted(composites.keys())

    top_y = 5
    bot_y = 1.5
    top_positions = {}
    for i, n in enumerate(essential_list):
        x = 1.5 + i * 1.6
        top_positions[n] = (x, top_y)

    bot_positions = {}
    for i, n in enumerate(composite_list):
        x = 1.0 + i * 1.4
        bot_positions[n] = (x, bot_y)

    for comp, divisors in composites.items():
        cx, cy = bot_positions[comp]
        for d in divisors:
            dx, dy = top_positions[d]
            ax.annotate('', xy=(dx, dy - 0.35), xytext=(cx, cy + 0.35),
                        arrowprops=dict(arrowstyle='->', color=SLATE, lw=1.5, alpha=0.6))

    for n, (x, y) in top_positions.items():
        circle = plt.Circle((x, y), 0.35, facecolor=GOLD, edgecolor=DARK, linewidth=2, zorder=10)
        ax.add_patch(circle)
        ax.text(x, y, str(n), ha='center', va='center', fontsize=13, fontweight='bold', color=DARK, zorder=11)

    for n, (x, y) in bot_positions.items():
        circle = plt.Circle((x, y), 0.32, facecolor=LIGHT_RED, edgecolor=DARK, linewidth=1.5, zorder=10)
        ax.add_patch(circle)
        ax.text(x, y, str(n), ha='center', va='center', fontsize=12, color=DARK, zorder=11)

    ax.text(7.5, 6.5, r"Knock down the primes (and 4), and every composite falls.",
            ha='center', fontsize=14, color=DARK, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=GLOW, edgecolor=DARK, linewidth=2))

    ax.text(7.5, top_y + 0.7, 'Essential Exponents (gold)', ha='center', fontsize=11, color=GOLD, fontweight='bold')
    ax.text(7.5, bot_y - 0.8, 'Composite Exponents (toppled)', ha='center', fontsize=11, color=ACCENT1, fontweight='bold')

    ax.set_xlim(0, 15)
    ax.set_ylim(0, 7.5)
    ax.set_title("The Domino Principle for Fermat's Last Theorem", fontsize=16, color=DARK, fontweight='bold', pad=15)
    ax.axis('off')
    save(fig, 'fig03_factor_tree.png')


# ============================================================
# FIG 4: Infinite descent staircase
# ============================================================
def fig04_descent_staircase():
    fig, ax = plt.subplots(1, 1, figsize=(12, 9))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    steps = [
        (r'$(a_1, b_1, c_1)$', r'$c_1 = 481$'),
        (r'$(a_2, b_2, c_2)$', r'$c_2 = 137$'),
        (r'$(a_3, b_3, c_3)$', r'$c_3 = 29$'),
        (r'$(a_4, b_4, c_4)$', r'$c_4 = \;?$'),
    ]

    n_steps = len(steps)
    step_w = 2.5
    step_h = 1.5

    for i, (label, c_label) in enumerate(steps):
        x = 1 + i * step_w
        y = 7 - i * step_h

        ax.plot([x, x + step_w], [y, y], color=DARK, linewidth=3)
        if i < n_steps - 1:
            ax.plot([x + step_w, x + step_w], [y, y - step_h], color=DARK, linewidth=3)

        ax.text(x + step_w / 2, y + 0.15, label, ha='center', va='bottom', fontsize=13,
                color=ACCENT4, fontweight='bold')
        ax.text(x + step_w / 2, y + 0.65, c_label, ha='center', va='bottom', fontsize=11,
                color=ACCENT2)

        if i < n_steps - 1:
            ax.annotate('', xy=(x + step_w, y - step_h + 0.1), xytext=(x + step_w, y - 0.1),
                        arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=2.5))

    wall_x = 1
    wall_y = 0.5
    wall_w = 10
    for row in range(3):
        for col in range(int(wall_w / 0.8)):
            bx = wall_x + col * 0.8 + (0.4 if row % 2 else 0)
            by = wall_y + row * 0.4
            brick = patches.Rectangle((bx, by), 0.75, 0.35,
                                       facecolor='#C0392B', edgecolor='#8B2500', linewidth=0.8, alpha=0.8)
            ax.add_patch(brick)

    ax.text(6, 1.1, r'$c > 0$', ha='center', va='center', fontsize=20, fontweight='bold',
            color='white', zorder=20,
            bbox=dict(boxstyle='round,pad=0.3', facecolor=ACCENT1, edgecolor='white', linewidth=2))

    ax.text(6, 2.2, 'IMPOSSIBLE', ha='center', va='center', fontsize=28, fontweight='bold',
            color=ACCENT1, rotation=15, alpha=0.7,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=ACCENT1, linewidth=3))

    ax.set_xlim(0, 12)
    ax.set_ylim(0, 9)
    ax.set_title("Fermat's Infinite Descent", fontsize=18, color=DARK, fontweight='bold', pad=10)
    ax.axis('off')
    save(fig, 'fig04_descent_staircase.png')


# ============================================================
# FIG 5: Descent flowchart for n=4
# ============================================================
def fig05_descent_flowchart():
    fig, ax = plt.subplots(1, 1, figsize=(10, 12))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    boxes = [
        (5, 10, 'Assume (a, b, c) is a minimal\npositive-integer solution to ' + r'$a^4 + b^4 = c^4$',
         LIGHT_BLUE),
        (5, 8, 'Rewrite as Pythagorean triple\n' + r'$(a^2, b^2, c^2)$',
         LIGHT_GREEN),
        (5, 6, 'Apply parametrization; factor',
         '#FCE4EC'),
        (5, 4, "Extract new triple (a', b', c')\nwith c' < c",
         '#FFF3E0'),
    ]

    box_w = 3.5
    box_h = 1.2

    for x, y, text, color in boxes:
        box = FancyBboxPatch((x - box_w / 2, y - box_h / 2), box_w, box_h,
                              boxstyle="round,pad=0.15", facecolor=color, edgecolor=DARK, linewidth=2)
        ax.add_patch(box)
        ax.text(x, y, text, ha='center', va='center', fontsize=10, color=DARK, fontweight='bold')

    for i in range(len(boxes) - 1):
        x1, y1 = boxes[i][0], boxes[i][1] - box_h / 2
        x2, y2 = boxes[i + 1][0], boxes[i + 1][1] + box_h / 2
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color=DARK, lw=2.5))

    ax.annotate('', xy=(1.0, 10), xytext=(1.0, 4),
                arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=3,
                                connectionstyle='arc3,rad=-0.3'))
    ax.text(0.2, 7, 'CONTRADICTION', ha='center', va='center', fontsize=13,
            color=ACCENT1, fontweight='bold', rotation=90,
            bbox=dict(boxstyle='round,pad=0.2', facecolor=LIGHT_RED, edgecolor=ACCENT1, linewidth=2))

    ax.set_xlim(-1, 10)
    ax.set_ylim(2.5, 11.5)
    ax.set_title(r"Fermat's Descent for $n = 4$", fontsize=16, color=DARK, fontweight='bold', pad=15)
    ax.axis('off')
    save(fig, 'fig05_descent_flowchart.png')


# ============================================================
# FIG 6: Venn diagram
# ============================================================
def fig06_venn_diagram():
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    outer = plt.Circle((5, 4.5), 3.0, facecolor=LIGHT_BLUE, edgecolor=ACCENT2, linewidth=3, alpha=0.4)
    ax.add_patch(outer)
    ax.text(3.5, 6.5, r'All perfect squares $c^2$', fontsize=13, color=ACCENT2, fontweight='bold')

    inner = plt.Circle((5, 4.0), 1.2, facecolor=LIGHT_GREEN, edgecolor=ACCENT3, linewidth=3, alpha=0.5)
    ax.add_patch(inner)
    ax.text(5, 4.0, r'$c^4 = (c^2)^2$', ha='center', fontsize=11, color=ACCENT3, fontweight='bold')

    ax.annotate(r'$a^4 + b^4 = c^2$', xy=(8.5, 5.5), xytext=(7.0, 6.0),
                fontsize=13, color=ACCENT1, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=2))
    ax.text(9.2, 5.5, r'$\times$', fontsize=30, color=ACCENT1, fontweight='bold')
    ax.text(8.5, 4.8, 'Fermat proved the\nbigger impossibility', fontsize=9,
            ha='center', color=DARK, style='italic')

    ax.annotate(r'$a^4 + b^4 = c^4$', xy=(8.5, 2.5), xytext=(6.2, 3.5),
                fontsize=13, color=ACCENT1, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=2))
    ax.text(9.2, 2.5, r'$\times$', fontsize=30, color=ACCENT1, fontweight='bold')
    ax.text(8.5, 1.8, '...and the smaller\none comes free', fontsize=9,
            ha='center', color=DARK, style='italic')

    ax.set_xlim(0, 11)
    ax.set_ylim(0.5, 8.5)
    ax.set_title('The Logical Containment', fontsize=16, color=DARK, fontweight='bold', pad=10)
    ax.axis('off')
    save(fig, 'fig06_venn_diagram.png')


# ============================================================
# FIG 7: Eisenstein integers lattice
# ============================================================
def fig07_eisenstein_lattice():
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    omega = np.exp(2j * np.pi / 3)

    for a in range(-4, 5):
        for b in range(-4, 5):
            z = a + b * omega
            ax.plot(z.real, z.imag, 'o', color=SLATE, markersize=5, zorder=5)

    for a in range(-4, 5):
        for b in range(-4, 5):
            z = a + b * omega
            for da, db in [(1, 0), (0, 1), (-1, 1)]:
                w = (a + da) + (b + db) * omega
                if -4 <= a + da <= 4 and -4 <= b + db <= 4:
                    ax.plot([z.real, w.real], [z.imag, w.imag], color=SLATE, linewidth=0.5, alpha=0.3)

    theta = np.linspace(0, 2 * np.pi, 100)
    ax.plot(np.cos(theta), np.sin(theta), '--', color=DARK, linewidth=1.5, alpha=0.5)

    units = [1, -1, omega, -omega, omega**2, -omega**2]
    unit_colors = [ACCENT1, ACCENT1, ACCENT2, ACCENT2, ACCENT3, ACCENT3]
    unit_labels = [r'$1$', r'$-1$', r'$\omega$', r'$-\omega$', r'$\omega^2$', r'$-\omega^2$']
    for u, c, lbl in zip(units, unit_colors, unit_labels):
        ax.plot(u.real, u.imag, 'o', color=c, markersize=12, zorder=15, markeredgecolor=DARK, markeredgewidth=1.5)
        offset_x = 0.2 if u.real >= 0 else -0.35
        offset_y = 0.2 if u.imag >= 0 else -0.25
        ax.text(u.real + offset_x, u.imag + offset_y, lbl, fontsize=11, color=c, fontweight='bold', zorder=16)

    ax.axhline(y=0, color=DARK, linewidth=0.8, alpha=0.5)
    ax.axvline(x=0, color=DARK, linewidth=0.8, alpha=0.5)

    ax.set_xlim(-4.5, 4.5)
    ax.set_ylim(-4.5, 4.5)
    ax.set_aspect('equal')
    ax.set_title(r'$\mathbb{Z}[\omega]$: the Eisenstein Integers', fontsize=16, color=DARK, fontweight='bold', pad=15)
    ax.axis('off')
    save(fig, 'fig07_eisenstein_lattice.png')


# ============================================================
# FIG 8: Euler portrait (stylized placeholder)
# ============================================================
def fig08_euler_portrait():
    fig, ax = plt.subplots(1, 1, figsize=(8, 10))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    frame_outer = FancyBboxPatch((1, 1.5), 6, 7, boxstyle="round,pad=0.3",
                                  facecolor='#FDF8EE', edgecolor=GOLD, linewidth=4)
    ax.add_patch(frame_outer)
    frame_inner = FancyBboxPatch((1.3, 1.8), 5.4, 6.4, boxstyle="round,pad=0.2",
                                  facecolor=CREAM, edgecolor='#8B7355', linewidth=2)
    ax.add_patch(frame_inner)

    ax.text(4, 5.5, 'L. E.', ha='center', va='center', fontsize=72,
            color=DARK, fontweight='bold', fontfamily='serif', alpha=0.15)

    ax.text(4, 6.8, 'LEONHARD EULER', ha='center', fontsize=16,
            color=DARK, fontweight='bold', fontfamily='serif')
    ax.text(4, 6.2, '(1707 - 1783)', ha='center', fontsize=13,
            color=SLATE, fontfamily='serif')

    ax.text(4, 4.5, r'$a^3 + b^3 \neq c^3$', ha='center', fontsize=22,
            color=ACCENT4, fontweight='bold')
    ax.text(4, 3.8, r'Proved: no integer cubes', ha='center', fontsize=11,
            color=DARK, fontfamily='serif')

    ax.text(4, 0.8, 'He proved the cube case -\nand made his only lucky\nfactorization assumption.',
            ha='center', fontsize=11, color=DARK, style='italic', fontfamily='serif',
            linespacing=1.5)

    # Symbolic eyes (one clear, one clouded)
    ax.plot(3.3, 5.0, 'o', color=DARK, markersize=8)
    ax.plot(4.7, 5.0, 'o', color='#AAAAAA', markersize=8, alpha=0.5)

    ax.set_xlim(0, 8)
    ax.set_ylim(0, 9.5)
    ax.axis('off')
    save(fig, 'fig08_euler_portrait.png')


# ============================================================
# FIG 9: Factorization in Z vs Z[sqrt(-5)]
# ============================================================
def fig09_factorization_comparison():
    fig, axes = plt.subplots(1, 2, figsize=(14, 8))
    fig.set_facecolor(SAND)

    # Left: Z
    ax = axes[0]
    ax.set_facecolor(SAND)

    nodes = {
        '60': (3, 7), '4': (1.5, 5), '15': (4.5, 5),
        '2a': (0.75, 3), '2b': (2.25, 3), '3': (3.75, 3), '5': (5.25, 3)
    }
    labels = {'60': '60', '4': '4', '15': '15', '2a': '2', '2b': '2', '3': '3', '5': '5'}
    edges = [('60', '4'), ('60', '15'), ('4', '2a'), ('4', '2b'), ('15', '3'), ('15', '5')]

    for parent, child in edges:
        px, py = nodes[parent]
        cx, cy = nodes[child]
        ax.plot([px, cx], [py, cy], color=DARK, linewidth=2)

    for key, (x, y) in nodes.items():
        is_prime = key in ['2a', '2b', '3', '5']
        color = GOLD if is_prime else LIGHT_BLUE
        circle = plt.Circle((x, y), 0.4, facecolor=color, edgecolor=DARK, linewidth=2, zorder=10)
        ax.add_patch(circle)
        ax.text(x, y, labels[key], ha='center', va='center', fontsize=14, fontweight='bold', color=DARK, zorder=11)

    ax.text(3, 1.5, r'$60 = 2^2 \times 3 \times 5$', ha='center', fontsize=14, color=ACCENT3, fontweight='bold')
    ax.text(3, 0.8, 'Unique!', ha='center', fontsize=13, color=ACCENT3, fontweight='bold')
    ax.set_title(r'Factorization in $\mathbb{Z}$', fontsize=15, color=DARK, fontweight='bold', pad=10)
    ax.set_xlim(-0.5, 6.5)
    ax.set_ylim(0, 8.5)
    ax.axis('off')

    # Right: Z[sqrt(-5)]
    ax = axes[1]
    ax.set_facecolor('#FFF0F0')

    ax.plot([2, 1], [7, 5], color=DARK, linewidth=2)
    ax.plot([2, 3], [7, 5], color=DARK, linewidth=2)
    ax.plot([5, 4], [7, 5], color=ACCENT4, linewidth=2)
    ax.plot([5, 6], [7, 5], color=ACCENT4, linewidth=2)

    for x, y, label in [(2, 7, '6'), (1, 5, '2'), (3, 5, '3')]:
        circle = plt.Circle((x, y), 0.4, facecolor=LIGHT_BLUE, edgecolor=DARK, linewidth=2, zorder=10)
        ax.add_patch(circle)
        ax.text(x, y, label, ha='center', va='center', fontsize=14, fontweight='bold', color=DARK, zorder=11)

    for x, y, label in [(5, 7, '6')]:
        circle = plt.Circle((x, y), 0.4, facecolor=LIGHT_BLUE, edgecolor=DARK, linewidth=2, zorder=10)
        ax.add_patch(circle)
        ax.text(x, y, label, ha='center', va='center', fontsize=14, fontweight='bold', color=DARK, zorder=11)

    for x, y, label in [(4, 5, r'$1+\sqrt{-5}$'), (6, 5, r'$1-\sqrt{-5}$')]:
        box = FancyBboxPatch((x - 0.8, y - 0.3), 1.6, 0.6, boxstyle="round,pad=0.1",
                              facecolor='#E8D5F5', edgecolor=ACCENT4, linewidth=2, zorder=10)
        ax.add_patch(box)
        ax.text(x, y, label, ha='center', va='center', fontsize=10, fontweight='bold', color=ACCENT4, zorder=11)

    ax.text(3.5, 6, r'$\neq$', ha='center', va='center', fontsize=40, color=ACCENT1, fontweight='bold')

    ax.text(3.5, 3.5, r'$6 = 2 \times 3$', ha='center', fontsize=13, color=DARK, fontweight='bold')
    ax.text(3.5, 2.8, r'$= (1+\sqrt{-5})(1-\sqrt{-5})$', ha='center', fontsize=13, color=ACCENT4, fontweight='bold')
    ax.text(3.5, 1.8, 'Two different factorizations!', ha='center', fontsize=13, color=ACCENT1, fontweight='bold')

    ax.set_title(r'Factorization in $\mathbb{Z}[\sqrt{-5}]$', fontsize=15, color=DARK, fontweight='bold', pad=10)
    ax.set_xlim(-0.5, 7.5)
    ax.set_ylim(0, 8.5)
    ax.axis('off')

    fig.suptitle('When Unique Factorization Fails', fontsize=18, color=DARK, fontweight='bold', y=0.98)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    save(fig, 'fig09_factorization_comparison.png')


# ============================================================
# FIG 10: The unique factorization trap (rope bridge)
# ============================================================
def fig10_uf_trap():
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    fig.set_facecolor('#E8DCC8')
    ax.set_facecolor('#D6EAF8')

    for i in range(100):
        y = i / 100 * 8
        alpha = 0.3 * (1 - i / 100)
        ax.axhspan(y, y + 0.08, color=LIGHT_BLUE, alpha=alpha)

    cliff_l = patches.Polygon([(0, 0), (0, 5), (2.5, 5), (3, 3), (2, 0)],
                               facecolor='#8B7355', edgecolor=DARK, linewidth=2)
    ax.add_patch(cliff_l)

    cliff_r = patches.Polygon([(11, 0), (11, 5), (13, 5), (14, 3), (14, 0)],
                               facecolor='#8B7355', edgecolor=DARK, linewidth=2)
    ax.add_patch(cliff_r)

    bridge_x = np.linspace(2.5, 11, 50)
    bridge_y = 5 - 1.5 * np.sin(np.pi * (bridge_x - 2.5) / 8.5)
    ax.plot(bridge_x, bridge_y, color=DARK, linewidth=3)
    ax.plot(bridge_x, bridge_y + 0.5, color='#8B6914', linewidth=2, alpha=0.6)

    for x in np.linspace(3, 10.5, 15):
        y_deck = 5 - 1.5 * np.sin(np.pi * (x - 2.5) / 8.5)
        ax.plot([x, x], [y_deck, y_deck + 0.5], color='#8B6914', linewidth=1, alpha=0.6)

    gaps = [(5.5, 37), (7, 59), (8.5, 67)]
    for gx, n in gaps:
        gy = 5 - 1.5 * np.sin(np.pi * (gx - 2.5) / 8.5)
        ax.plot([gx - 0.3, gx + 0.3], [gy, gy], color='#D6EAF8', linewidth=6, zorder=5)
        ax.text(gx, gy - 0.8, f'n = {n}', ha='center', fontsize=9, color=ACCENT1, fontweight='bold')

    # Fermat figure on left cliff (simple stick figure)
    ax.plot(1.5, 5.7, 'o', color=DARK, markersize=12)
    ax.plot([1.5, 1.5], [5.2, 5.5], color=DARK, linewidth=2)
    ax.plot([1.3, 1.7], [5.1, 5.1], color=DARK, linewidth=2)
    ax.plot([1.5, 1.3], [5.2, 4.8], color=DARK, linewidth=2)
    ax.plot([1.5, 1.7], [5.2, 4.8], color=DARK, linewidth=2)
    ax.text(1.5, 6.3, 'Fermat', ha='center', fontsize=10, color=DARK, fontweight='bold')

    ax.text(12, 5.5, r'$a^n + b^n \neq c^n$', ha='center', fontsize=13, color=ACCENT3,
            fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=GLOW, edgecolor=DARK, linewidth=2))

    ax.text(6.75, 5.8, 'Unique Factorization', ha='center', fontsize=12,
            color=DARK, fontweight='bold', rotation=-5)

    ax.text(7, 0.5, '"Kummer was here, 1847"', ha='center', fontsize=9,
            color='#5C3D1A', style='italic',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='#C4A87C', edgecolor=DARK, linewidth=1))

    ax.set_xlim(0, 14)
    ax.set_ylim(0, 7.5)
    ax.set_title('The Unique Factorization Trap', fontsize=16, color=DARK, fontweight='bold', pad=10)
    ax.axis('off')
    save(fig, 'fig10_uf_trap.png')


# ============================================================
# FIG 11: Bar chart of proof lengths
# ============================================================
def fig11_proof_lengths():
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    exponents = [r'$n=4$', r'$n=3$', r'$n=5$', r'$n=7$', r'$n=?$', r'$n=\mathrm{all}$']
    pages = [3, 15, 40, 80, None, 120]
    colors = [ACCENT2, ACCENT3, ACCENT5, ACCENT4, '#CCCCCC', GOLD]

    for i, (exp, pg, col) in enumerate(zip(exponents, pages, colors)):
        if pg is not None:
            n_pages = max(1, pg // 5)
            for j in range(min(n_pages, 25)):
                y = j * 0.35
                rect = patches.Rectangle((i - 0.35, y), 0.7, 0.3,
                                          facecolor=col, edgecolor=DARK, linewidth=0.5, alpha=0.8)
                ax.add_patch(rect)
            ax.text(i, n_pages * 0.35 + 0.3, f'{pg} pp.', ha='center', fontsize=10,
                    color=DARK, fontweight='bold')
        else:
            ax.text(i, 4, '?', ha='center', va='center', fontsize=60,
                    color=SLATE, fontweight='bold', alpha=0.5)

        ax.text(i, -0.5, exp, ha='center', fontsize=13, color=DARK, fontweight='bold')

    ax.annotate('', xy=(5, 5), xytext=(4, 5),
                arrowprops=dict(arrowstyle='->', color=DARK, lw=2, linestyle='dashed'))

    margin_rect = patches.Rectangle((0.5, -2.5), 0.3, 0.5, facecolor=CREAM,
                                     edgecolor=DARK, linewidth=1)
    ax.add_patch(margin_rect)
    ax.text(1.5, -2.3, r"Fermat's margin", ha='right', fontsize=9, color=DARK, style='italic')

    ax.text(5, 9.5, r'Wiles, 1995', ha='center', fontsize=10, color=GOLD, fontweight='bold')

    ax.set_xlim(-1, 6.5)
    ax.set_ylim(-3, 11)
    ax.set_title('Growth of Proof Complexity', fontsize=16, color=DARK, fontweight='bold', pad=15)
    ax.axis('off')
    save(fig, 'fig11_proof_lengths.png')


# ============================================================
# FIG 12: Sophie Germain portrait (stylized)
# ============================================================
def fig12_germain_portrait():
    fig, ax = plt.subplots(1, 1, figsize=(8, 10))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    frame_outer = FancyBboxPatch((1, 1.5), 6, 7, boxstyle="round,pad=0.3",
                                  facecolor='#FDF8EE', edgecolor=ACCENT4, linewidth=4)
    ax.add_patch(frame_outer)
    frame_inner = FancyBboxPatch((1.3, 1.8), 5.4, 6.4, boxstyle="round,pad=0.2",
                                  facecolor=CREAM, edgecolor='#8B7355', linewidth=2)
    ax.add_patch(frame_inner)

    ax.text(4, 5.5, 'S. G.', ha='center', va='center', fontsize=72,
            color=ACCENT4, fontweight='bold', fontfamily='serif', alpha=0.12)

    ax.text(4, 7.0, 'SOPHIE GERMAIN', ha='center', fontsize=16,
            color=DARK, fontweight='bold', fontfamily='serif')
    ax.text(4, 6.4, '(1776 - 1831)', ha='center', fontsize=13,
            color=SLATE, fontfamily='serif')

    ax.text(4, 4.8, r"Germain's Theorem", ha='center', fontsize=16,
            color=ACCENT4, fontweight='bold')
    ax.text(4, 4.1, r'If $p$ is a Germain prime,', ha='center', fontsize=11,
            color=DARK, fontfamily='serif')
    ax.text(4, 3.5, r'then $a^p + b^p = c^p$ has', ha='center', fontsize=11,
            color=DARK, fontfamily='serif')
    ax.text(4, 2.9, r'no solutions with $p \nmid abc$', ha='center', fontsize=11,
            color=DARK, fontfamily='serif')

    ax.text(4, 0.7, "She wrote to Gauss under a man's name -\nand proved more than most of\nher male contemporaries.",
            ha='center', fontsize=11, color=DARK, style='italic', fontfamily='serif',
            linespacing=1.5)

    ax.set_xlim(0, 8)
    ax.set_ylim(0, 9.5)
    ax.axis('off')
    save(fig, 'fig12_germain_portrait.png')


# ============================================================
# FIG 13: Elliptic curve group law
# ============================================================
def fig13_elliptic_curve():
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    # y^2 = x^3 - x
    x1 = np.linspace(-1, -0.01, 300)
    x2 = np.linspace(1, 2.5, 300)

    for xvals in [x1, x2]:
        y2 = xvals**3 - xvals
        mask = y2 >= 0
        xv = xvals[mask]
        yv = np.sqrt(y2[mask])
        ax.plot(xv, yv, color=ACCENT2, linewidth=3, zorder=5)
        ax.plot(xv, -yv, color=ACCENT2, linewidth=3, zorder=5)

    Px, Py = -1, 0
    Qx = 2.0
    Qy = np.sqrt(Qx**3 - Qx)

    if Qx != Px:
        slope = (Qy - Py) / (Qx - Px)
        intercept = Py - slope * Px

    line_x = np.linspace(-1.5, 2.5, 200)
    line_y = slope * line_x + intercept
    ax.plot(line_x, line_y, '--', color=ACCENT5, linewidth=2, alpha=0.8)

    Rx = slope**2 - Px - Qx
    Ry = slope * Rx + intercept
    PQx, PQy = Rx, -Ry

    for px, py, label, color in [(Px, Py, 'P', ACCENT1), (Qx, Qy, 'Q', ACCENT3),
                                  (Rx, Ry, 'R', ACCENT5), (PQx, PQy, 'P + Q', ACCENT4)]:
        ax.plot(px, py, 'o', color=color, markersize=12, zorder=15, markeredgecolor=DARK, markeredgewidth=1.5)
        offset = 0.2
        ax.text(px + offset, py + offset, label, fontsize=13, color=color, fontweight='bold', zorder=16)

    ax.plot([Rx, PQx], [Ry, PQy], ':', color=ACCENT4, linewidth=2, alpha=0.8)

    ax.axhline(y=0, color=DARK, linewidth=0.8, alpha=0.5)
    ax.axvline(x=0, color=DARK, linewidth=0.8, alpha=0.5)

    ax.set_xlim(-1.8, 2.8)
    ax.set_ylim(-3, 3)
    ax.set_aspect('equal')
    ax.set_title(r'The Group Law on $y^2 = x^3 - x$', fontsize=16, color=DARK, fontweight='bold', pad=15)
    ax.text(0.5, -2.6, 'Draw line through P and Q; intersects at R; reflect to get P + Q',
            ha='center', fontsize=10, color=DARK, style='italic')
    ax.axis('off')
    save(fig, 'fig13_elliptic_curve.png')


# ============================================================
# FIG 14: Bridge diagram (Frey curve / modularity)
# ============================================================
def fig14_bridge_diagram():
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    fig.set_facecolor('#E8DCC8')
    ax.set_facecolor('#D5E8F0')

    river_x = np.linspace(0, 14, 200)
    river_y1 = 2.0 + 0.3 * np.sin(river_x * 2)
    river_y2 = 3.5 + 0.3 * np.sin(river_x * 2 + 0.5)
    ax.fill_between(river_x, river_y1, river_y2, color='#85C1E9', alpha=0.6)

    ax.fill_between([0, 3.5], [0, 0], [2.0, 2.0], color='#7D6B4F', alpha=0.8)
    ax.fill_between([0, 3.5], [2.0, 2.0], [2.5, 2.3], color='#27AE60', alpha=0.5)

    ax.fill_between([10.5, 14], [0, 0], [3.5, 3.5], color='#7D6B4F', alpha=0.8)
    ax.fill_between([10.5, 14], [3.5, 3.5], [4.0, 3.8], color='#27AE60', alpha=0.5)

    # Left signpost
    ax.plot([1.5, 1.5], [2.5, 4.0], color=DARK, linewidth=3)
    sign_l = FancyBboxPatch((0.2, 4.0), 2.6, 1.2, boxstyle="round,pad=0.1",
                             facecolor=CREAM, edgecolor=DARK, linewidth=2)
    ax.add_patch(sign_l)
    ax.text(1.5, 4.6, "Fermat's Equation:\n" + r"$a^p + b^p = c^p$",
            ha='center', va='center', fontsize=10, color=DARK, fontweight='bold')

    # Right signpost
    ax.plot([12, 12], [4.0, 5.5], color=DARK, linewidth=3)
    sign_r = FancyBboxPatch((10.5, 5.5), 3.0, 1.2, boxstyle="round,pad=0.1",
                             facecolor=CREAM, edgecolor=DARK, linewidth=2)
    ax.add_patch(sign_r)
    ax.text(12, 6.1, "Modular Forms:\n" + r"$\sum a_n q^n$",
            ha='center', va='center', fontsize=10, color=DARK, fontweight='bold')

    # Bridge arch
    bridge_x = np.linspace(3.5, 10.5, 100)
    bridge_y = 3.5 + 3.5 * np.sin(np.pi * (bridge_x - 3.5) / 7)
    ax.plot(bridge_x, bridge_y, color='#8B7355', linewidth=5)
    ax.fill_between(bridge_x, bridge_y, bridge_y - 0.3, color='#A89070', alpha=0.8)

    ax.text(7, 6.8, 'Taniyama-Shimura-Weil\nConjecture', ha='center', fontsize=12,
            color=DARK, fontweight='bold', style='italic')

    # Barricade
    bar_x = 7
    bar_y = 3.5 + 3.5 * np.sin(np.pi * (bar_x - 3.5) / 7)
    barricade = FancyBboxPatch((bar_x - 1.2, bar_y - 0.8), 2.4, 0.8,
                                boxstyle="round,pad=0.1", facecolor=LIGHT_RED, edgecolor=ACCENT1, linewidth=2)
    ax.add_patch(barricade)
    ax.text(bar_x, bar_y - 0.4, "Ribet's Theorem:\nThe Frey curve\ncannot cross!",
            ha='center', va='center', fontsize=8, color=ACCENT1, fontweight='bold')

    ax.text(7, 2.5, '~Frey Curve~', ha='center', fontsize=10, color=ACCENT4, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='#E8D5F5', edgecolor=ACCENT4, linewidth=1.5))

    ax.text(7, 1.0, 'CONTRADICTION -\nno Fermat solution exists',
            ha='center', fontsize=10, color=ACCENT1, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor=ACCENT1, linewidth=2, alpha=0.8))

    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.set_title("The Bridge to Fermat's Last Theorem", fontsize=16, color=DARK, fontweight='bold', pad=10)
    ax.axis('off')
    save(fig, 'fig14_bridge_diagram.png')


# ============================================================
# FIG 15: Timeline 1637-1995
# ============================================================
def fig15_timeline():
    fig, ax = plt.subplots(1, 1, figsize=(16, 8))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    milestones = [
        (1637, "Fermat's\nmarginal note", ACCENT1),
        (1640, "Fermat proves\nn=4", ACCENT2),
        (1770, "Euler proves\nn=3", ACCENT3),
        (1825, "Dirichlet &\nLegendre: n=5", ACCENT5),
        (1839, "Lame:\nn=7", ACCENT4),
        (1847, "Kummer's\nideal numbers", GOLD),
        (1955, "Taniyama-\nShimura conj.", ACCENT2),
        (1985, "Frey\ncurve", ACCENT5),
        (1986, "Ribet's\ntheorem", ACCENT3),
        (1993, "Wiles's\nannouncement", ACCENT1),
        (1994, "Gap repaired\nwith Taylor", ACCENT4),
        (1995, "Published\nproof!", GOLD),
    ]

    year_min, year_max = 1620, 2010
    def year_to_x(y):
        return 1 + 13 * (y - year_min) / (year_max - year_min)

    road_years = np.linspace(year_min, year_max, 300)
    road_x = [year_to_x(y) for y in road_years]
    road_y = [4 + 0.5 * np.sin(0.05 * (y - year_min)) for y in road_years]
    ax.plot(road_x, road_y, color='#8B7355', linewidth=6, alpha=0.6, zorder=1)
    ax.plot(road_x, road_y, color=CREAM, linewidth=3, alpha=0.8, zorder=2)

    for i, (year, label, color) in enumerate(milestones):
        x = year_to_x(year)
        base_y = 4 + 0.5 * np.sin(0.05 * (year - year_min))
        if i % 2 == 0:
            y_text = base_y + 1.5
            va = 'bottom'
            y_line_end = base_y + 0.3
        else:
            y_text = base_y - 1.5
            va = 'top'
            y_line_end = base_y - 0.3

        ax.plot([x, x], [base_y, y_line_end + (0.5 if i % 2 == 0 else -0.5)],
                color=color, linewidth=2, zorder=5)
        ax.plot(x, base_y, 'o', color=color, markersize=8, zorder=10,
                markeredgecolor=DARK, markeredgewidth=1)
        ax.text(x, y_text, f'{year}\n{label}', ha='center', va=va, fontsize=7,
                color=DARK, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor=color,
                          linewidth=1.5, alpha=0.9))

    ax.annotate('', xy=(year_to_x(1995), 7.2), xytext=(year_to_x(1637), 7.2),
                arrowprops=dict(arrowstyle='<->', color=DARK, lw=2))
    ax.text(year_to_x(1816), 7.5, '358 years', ha='center', fontsize=14,
            color=DARK, fontweight='bold')

    ax.set_xlim(0, 15)
    ax.set_ylim(0.5, 8)
    ax.set_title("The Road to Fermat's Last Theorem", fontsize=16, color=DARK, fontweight='bold', pad=10)
    ax.axis('off')
    save(fig, 'fig15_timeline.png')


# ============================================================
# FIG 16: Blackboard
# ============================================================
def fig16_blackboard():
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    fig.set_facecolor('#1A1A2E')
    ax.set_facecolor('#1B4D3E')

    board = FancyBboxPatch((0.5, 0.5), 11, 7, boxstyle="round,pad=0.2",
                            facecolor='#1B4D3E', edgecolor='#8B6914', linewidth=6)
    ax.add_patch(board)

    chalk_props = dict(color='#F5F5DC', fontfamily='serif')

    equations = [
        (1.5, 7.0, r'$\rho_{E,p} : \mathrm{Gal}(\bar{\mathbb{Q}}/\mathbb{Q}) \to \mathrm{GL}_2(\mathbb{F}_p)$', 10),
        (1.5, 6.3, r'$f = \sum_{n=1}^{\infty} a_n q^n \in S_2(\Gamma_0(N))$', 11),
        (1.5, 5.6, r'$|E(\mathbb{F}_p)| = p + 1 - a_p$', 11),
        (1.5, 4.9, r'$R = \mathbb{T}$  (Hecke algebra)', 10),
        (1.5, 4.2, r'$\mathrm{Sel}(\mathbb{Q}, \mathrm{ad}^0 \rho) \hookrightarrow H^1(\mathbb{Q}_p, \mathrm{ad}^0 \rho)$', 9),
        (6, 3.2, r'$\Rightarrow$  every semistable elliptic curve is modular', 11),
        (6, 2.3, r'$\Rightarrow$  Frey curve cannot exist', 11),
    ]

    for x, y, eq, size in equations:
        ax.text(x, y, eq, fontsize=size, **chalk_props, alpha=0.85)

    ax.text(6, 1.2, r'$\therefore$ QED', fontsize=28, ha='center',
            color='#F5F5DC', fontweight='bold', fontfamily='serif')

    # Chalk piece
    ax.plot([9, 9.3], [0.6, 0.6], color='#F5F5DC', linewidth=4, alpha=0.7, solid_capstyle='round')

    ax.text(6, -0.3, "Cambridge, June 23, 1993.  \"I think I'll stop here.\"",
            ha='center', fontsize=12, color=SAND, style='italic', fontweight='bold')

    ax.set_xlim(0, 12)
    ax.set_ylim(-0.7, 8)
    ax.axis('off')
    save(fig, 'fig16_blackboard.png')


# ============================================================
# FIG 17: Landscape Beyond Fermat
# ============================================================
def fig17_landscape_beyond():
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    fig.set_facecolor(SAND)
    ax.set_facecolor('#E8F4E8')

    def draw_mountain(ax, cx, cy, width, height, color, label, sublabel='', flag=False, clouds=False, rubble=False):
        x = [cx - width / 2, cx, cx + width / 2]
        y = [cy, cy + height, cy]
        ax.fill(x, y, color=color, alpha=0.7, zorder=3)
        ax.plot(x, y, color=DARK, linewidth=1.5, zorder=4)

        snow_x = [cx - width * 0.1, cx, cx + width * 0.1]
        snow_y = [cy + height * 0.85, cy + height, cy + height * 0.85]
        ax.fill(snow_x, snow_y, color='white', alpha=0.7, zorder=5)

        if flag:
            ax.plot([cx, cx], [cy + height, cy + height + 0.5], color=DARK, linewidth=2, zorder=10)
            flag_poly = patches.Polygon([(cx, cy + height + 0.5), (cx + 0.4, cy + height + 0.35),
                                          (cx, cy + height + 0.2)],
                                         facecolor=ACCENT1, edgecolor=DARK, linewidth=1, zorder=10)
            ax.add_patch(flag_poly)

        if clouds:
            for dx, dy in [(-0.3, 0.1), (0.2, 0.3), (0.5, 0)]:
                cloud = plt.Circle((cx + dx * width, cy + height * 0.7 + dy), 0.3,
                                    facecolor='white', edgecolor='#CCCCCC', alpha=0.7, zorder=6)
                ax.add_patch(cloud)

        if rubble:
            for dx in np.linspace(-width * 0.3, width * 0.3, 8):
                ax.plot(cx + dx, cy + 0.1, 's', color='#8B7355', markersize=4, alpha=0.6, zorder=4)

        ax.text(cx, cy + height + (0.9 if flag else 0.3), label, ha='center', fontsize=9,
                color=DARK, fontweight='bold', zorder=15,
                bbox=dict(boxstyle='round,pad=0.15', facecolor='white', edgecolor=DARK, linewidth=1, alpha=0.85))
        if sublabel:
            ax.text(cx, cy - 0.5, sublabel, ha='center', fontsize=7, color=SLATE, style='italic', zorder=15)

    draw_mountain(ax, 7, 1, 4, 5, '#8B7355', 'FLT\n(conquered, 1995)', flag=True)
    draw_mountain(ax, 7, 5.5, 3.5, 4, '#6C8EBF', 'Beal Conjecture\n(\\$1,000,000 prize)', sublabel='Unclimbed')
    draw_mountain(ax, 11.5, 3, 3, 3.5, '#B0A090', 'abc Conjecture\n(contested, 2012)', clouds=True, sublabel='Shrouded in clouds')
    draw_mountain(ax, 4, 0, 3, 2, '#A0522D', "Euler's Conjecture\n(collapsed 1966/88)", rubble=True, sublabel='Summit collapsed')
    draw_mountain(ax, 2, 3, 2.5, 2.5, '#7CB342', "Catalan's Conjecture\n(Mihailescu, 2002)", flag=True)

    for cx, cy in [(13, 6), (1, 7), (12, 7.5)]:
        draw_mountain(ax, cx, cy, 1.5, 1.5, '#CCCCCC', '?', sublabel='')

    # Compass rose
    cx, cy = 1, 1
    ax.text(cx, cy + 0.7, 'N', ha='center', fontsize=9, color=DARK, fontweight='bold')
    ax.text(cx, cy - 0.7, 'S', ha='center', fontsize=9, color=DARK, fontweight='bold')
    ax.text(cx + 0.7, cy, 'E', ha='center', fontsize=9, color=DARK, fontweight='bold')
    ax.text(cx - 0.7, cy, 'W', ha='center', fontsize=9, color=DARK, fontweight='bold')
    ax.plot([cx, cx], [cy - 0.5, cy + 0.5], color=DARK, linewidth=1.5)
    ax.plot([cx - 0.5, cx + 0.5], [cy, cy], color=DARK, linewidth=1.5)

    ax.text(7, 9.5, 'The Landscape Beyond Fermat', ha='center', fontsize=18,
            color=DARK, fontweight='bold', fontfamily='serif',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=CREAM, edgecolor=GOLD, linewidth=3))

    ax.set_xlim(-0.5, 14.5)
    ax.set_ylim(-1, 10.5)
    ax.axis('off')
    save(fig, 'fig17_landscape_beyond.png')


# ============================================================
# RUN ALL
# ============================================================
if __name__ == '__main__':
    print("Generating Chapter 10 illustrations...")
    fig01_near_miss_meter()
    fig02_fermat_margin()
    fig03_factor_tree()
    fig04_descent_staircase()
    fig05_descent_flowchart()
    fig06_venn_diagram()
    fig07_eisenstein_lattice()
    fig08_euler_portrait()
    fig09_factorization_comparison()
    fig10_uf_trap()
    fig11_proof_lengths()
    fig12_germain_portrait()
    fig13_elliptic_curve()
    fig14_bridge_diagram()
    fig15_timeline()
    fig16_blackboard()
    fig17_landscape_beyond()
    print("Done! All 17 illustrations generated.")

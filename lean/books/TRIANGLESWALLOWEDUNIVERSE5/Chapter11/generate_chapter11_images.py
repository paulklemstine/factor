#!/usr/bin/env python3
"""Generate all illustrations for Chapter 11: The Magnificent Sieve."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe
import numpy as np
import os
from math import gcd, isqrt

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
# FIGURE 1: Treasure chest -- congruence of squares metaphor
# ============================================================
def fig01_treasure_chest():
    fig, ax = plt.subplots(1, 1, figsize=(14, 9))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    # Central chest
    chest = FancyBboxPatch((4, 2.5), 6, 3.5, boxstyle="round,pad=0.3",
                           facecolor='#8B4513', edgecolor=DARK, linewidth=3)
    ax.add_patch(chest)
    # Iron bands
    for y_off in [0.8, 1.8, 2.8]:
        ax.plot([4.2, 9.8], [2.5 + y_off, 2.5 + y_off], color='#555555', linewidth=4, alpha=0.6)
    # Lock
    lock = plt.Circle((7, 3.5), 0.35, color='#555555', ec=DARK, linewidth=2, zorder=10)
    ax.add_patch(lock)

    # n = 8051 on chest
    ax.text(7, 5.2, '$n = 8051$', fontsize=22, ha='center', va='center',
            color=GOLD, fontweight='bold', zorder=10,
            path_effects=[pe.withStroke(linewidth=3, foreground=DARK)])

    # Equation on lid
    ax.text(7, 6.5, r'$x^2 - y^2 = (x-y)(x+y)$', fontsize=16, ha='center',
            va='center', color=DARK, fontstyle='italic',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=GLOW, alpha=0.5))

    # Left key
    ax.annotate('', xy=(4.5, 3.5), xytext=(1.5, 5),
                arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=2.5))
    key_box_l = FancyBboxPatch((0.2, 4.5), 2.6, 1.5, boxstyle="round,pad=0.2",
                               facecolor=LIGHT_RED, edgecolor=ACCENT1, linewidth=2)
    ax.add_patch(key_box_l)
    ax.text(1.5, 5.25, '$(x - y) = 83$', fontsize=14, ha='center', va='center',
            color=ACCENT1, fontweight='bold')

    # Right key
    ax.annotate('', xy=(9.5, 3.5), xytext=(12.5, 5),
                arrowprops=dict(arrowstyle='->', color=ACCENT2, lw=2.5))
    key_box_r = FancyBboxPatch((11.2, 4.5), 2.6, 1.5, boxstyle="round,pad=0.2",
                               facecolor=LIGHT_BLUE, edgecolor=ACCENT2, linewidth=2)
    ax.add_patch(key_box_r)
    ax.text(12.5, 5.25, '$(x + y) = 97$', fontsize=14, ha='center', va='center',
            color=ACCENT2, fontweight='bold')

    # GCD operation
    gcd_box = FancyBboxPatch((5.5, 0.5), 3, 1.3, boxstyle="round,pad=0.2",
                             facecolor=GLOW, edgecolor=GOLD, linewidth=3, zorder=10)
    ax.add_patch(gcd_box)
    ax.text(7, 1.15, r'$\gcd(83, 8051) = 83$', fontsize=14, ha='center', va='center',
            color=DARK, fontweight='bold', zorder=11)
    ax.annotate('', xy=(7, 2.5), xytext=(7, 1.8),
                arrowprops=dict(arrowstyle='->', color=GOLD, lw=3))

    # Result boxes
    res_l = FancyBboxPatch((3, -0.8), 2.5, 1, boxstyle="round,pad=0.2",
                           facecolor=LIGHT_GREEN, edgecolor=ACCENT3, linewidth=2)
    ax.add_patch(res_l)
    ax.text(4.25, -0.3, '$83$', fontsize=18, ha='center', va='center',
            color=ACCENT3, fontweight='bold')

    res_r = FancyBboxPatch((8.5, -0.8), 2.5, 1, boxstyle="round,pad=0.2",
                           facecolor=LIGHT_GREEN, edgecolor=ACCENT3, linewidth=2)
    ax.add_patch(res_r)
    ax.text(9.75, -0.3, '$97$', fontsize=18, ha='center', va='center',
            color=ACCENT3, fontweight='bold')

    ax.annotate('', xy=(4.25, 0.2), xytext=(5.8, 0.5),
                arrowprops=dict(arrowstyle='->', color=ACCENT3, lw=2))
    ax.annotate('', xy=(9.75, 0.2), xytext=(8.2, 0.5),
                arrowprops=dict(arrowstyle='->', color=ACCENT3, lw=2))

    ax.set_xlim(-0.5, 14.5)
    ax.set_ylim(-1.5, 7.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('The Congruence of Squares: Cracking $n$ Open',
                 fontsize=18, color=DARK, fontweight='bold', pad=15)
    save(fig, 'fig01_treasure_chest.png')


# ============================================================
# FIGURE 2: Factor-o-gram table
# ============================================================
def fig02_factorgram_table():
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.axis('off')

    n = 8051
    rows = [
        (201, 150, False, None),
        (126, 41, False, None),
        (90, 1, False, None),
        (255, 248, False, None),
        (90, 7, True, 83),
        (127, 44, True, 1),
    ]

    headers = ['$x$', '$y$', '$x^2 - y^2$', 'Div by $n$?', r'$\gcd(x-y,\,n)$', '']
    col_x = [1, 2.5, 4.5, 7, 9.5, 11.5]
    y_start = 7

    for j, h in enumerate(headers):
        ax.text(col_x[j], y_start, h, fontsize=13, ha='center', va='center',
                fontweight='bold', color=DARK)
    ax.plot([0.2, 12.5], [y_start - 0.35, y_start - 0.35], color=DARK, linewidth=2)

    for i, (x, y, div, g) in enumerate(rows):
        yi = y_start - 0.9 * (i + 1)
        diff = x*x - y*y
        is_winner = (div and g not in (1, n))
        if is_winner:
            rect = FancyBboxPatch((0.2, yi - 0.35), 12.3, 0.7, boxstyle="round,pad=0.05",
                                  facecolor=GLOW, alpha=0.4, edgecolor=GOLD, linewidth=2)
            ax.add_patch(rect)

        color = DARK
        ax.text(col_x[0], yi, f'${x}$', fontsize=13, ha='center', va='center', color=color)
        ax.text(col_x[1], yi, f'${y}$', fontsize=13, ha='center', va='center', color=color)
        ax.text(col_x[2], yi, f'${diff}$', fontsize=12, ha='center', va='center', color=color)

        if div:
            ax.text(col_x[3], yi, 'Yes', fontsize=13, ha='center', va='center', color=ACCENT3, fontweight='bold')
        else:
            ax.text(col_x[3], yi, 'No', fontsize=13, ha='center', va='center', color=ACCENT1)

        if div:
            gval = gcd(x - y, n)
            ax.text(col_x[4], yi, f'${gval}$', fontsize=13, ha='center', va='center', color=color)
        else:
            ax.text(col_x[4], yi, '---', fontsize=13, ha='center', va='center', color='#888888')

        if is_winner:
            ax.text(col_x[5], yi, 'YES', fontsize=14, ha='center', va='center', color=ACCENT3, fontweight='bold')
        else:
            ax.text(col_x[5], yi, 'X', fontsize=14, ha='center', va='center', color=ACCENT1, fontweight='bold')

    ax.text(7, y_start - 0.9 * 7 - 0.2,
            'The factors are $83$ and $97 = 8051 / 83$.',
            fontsize=13, ha='center', va='center', color=DARK, fontstyle='italic',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=LIGHT_GREEN, alpha=0.5))

    ax.set_xlim(0, 13)
    ax.set_ylim(y_start - 8, y_start + 0.8)
    ax.set_title('Factor-o-Gram: Hunting for Congruent Squares',
                 fontsize=18, color=DARK, fontweight='bold', pad=15)
    save(fig, 'fig02_factorgram_table.png')


# ============================================================
# FIGURE 3: Venn diagram of prime factors
# ============================================================
def fig03_venn_diagram():
    fig, ax = plt.subplots(1, 1, figsize=(12, 9))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    c1 = plt.Circle((4, 5), 2.8, facecolor=LIGHT_RED, edgecolor=ACCENT1,
                     linewidth=2.5, alpha=0.5)
    c2 = plt.Circle((8, 5), 2.8, facecolor=LIGHT_BLUE, edgecolor=ACCENT2,
                     linewidth=2.5, alpha=0.5)
    ax.add_patch(c1)
    ax.add_patch(c2)

    ax.text(2.8, 7.5, 'Prime factors of $(x - y)$', fontsize=12, ha='center',
            color=ACCENT1, fontweight='bold')
    ax.text(9.2, 7.5, 'Prime factors of $(x + y)$', fontsize=12, ha='center',
            color=ACCENT2, fontweight='bold')

    dot83 = plt.Circle((3.5, 5), 0.4, facecolor=ACCENT1, edgecolor=DARK, linewidth=2, zorder=10)
    ax.add_patch(dot83)
    ax.text(3.5, 5, '$83$', fontsize=14, ha='center', va='center', color='white',
            fontweight='bold', zorder=11)

    dot97 = plt.Circle((8.5, 5), 0.4, facecolor=ACCENT2, edgecolor=DARK, linewidth=2, zorder=10)
    ax.add_patch(dot97)
    ax.text(8.5, 5, '$97$', fontsize=14, ha='center', va='center', color='white',
            fontweight='bold', zorder=11)

    ax.text(6, 5, '(empty)', fontsize=11, ha='center', va='center', color='#888888',
            fontstyle='italic')

    annotations = [
        (6, 2.5, r'$n \mid (x-y)(x+y)$: every prime of $n$ appears in at least one circle'),
        (6, 1.7, r'$n \nmid (x-y)$: NOT all primes of $n$ are in the left circle'),
        (6, 0.9, r'$\gcd(x-y, n)$ harvests exactly the primes in the left circle'),
    ]
    for x, y, txt in annotations:
        ax.text(x, y, txt, fontsize=11, ha='center', va='center', color=DARK,
                bbox=dict(boxstyle='round,pad=0.3', facecolor=CREAM, alpha=0.8))

    ax.set_xlim(0, 12)
    ax.set_ylim(0, 9)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('How $\\gcd$ Harvests a Factor',
                 fontsize=18, color=DARK, fontweight='bold', pad=15)
    save(fig, 'fig03_venn_diagram.png')


# ============================================================
# FIGURE 4: Fermat's method -- margin computations
# ============================================================
def fig04_fermat_margin():
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    fig.set_facecolor('#F0E4C8')
    ax.set_facecolor('#F0E4C8')
    ax.axis('off')

    ax.text(5, 9.3, "Fermat's Method of Factoring", fontsize=20,
            ha='center', va='center', color=DARK, fontweight='bold',
            fontstyle='italic')
    ax.text(5, 8.7, '$n = 1009$', fontsize=16, ha='center', va='center', color=DARK)

    margin = FancyBboxPatch((1, 1), 8, 7, boxstyle="round,pad=0.3",
                            facecolor='#FDF5E6', edgecolor='#8B7355', linewidth=2)
    ax.add_patch(margin)

    trials = [
        (32, 32**2 - 1009),
        (33, 33**2 - 1009),
        (34, 34**2 - 1009),
        (35, 35**2 - 1009),
        (36, 36**2 - 1009),
        (37, 37**2 - 1009),
        (38, 38**2 - 1009),
    ]

    ax.text(2, 7.3, 'Trial:', fontsize=12, color=DARK, fontstyle='italic')
    ax.text(5, 7.3, '$x^2 - n$', fontsize=12, ha='center', color=DARK, fontstyle='italic')
    ax.text(7.5, 7.3, 'Perfect sq?', fontsize=11, ha='center', color=DARK, fontstyle='italic')

    for i, (x, diff) in enumerate(trials):
        yi = 6.5 - i * 0.7
        sq = isqrt(max(0, diff))
        is_sq = (sq * sq == diff and diff >= 0)

        ax.text(2, yi, f'$x = {x}$:', fontsize=13, color=DARK)
        ax.text(5, yi, f'${x}^2 - 1009 = {diff}$', fontsize=12, ha='center', color=DARK)
        if is_sq:
            ax.text(7.5, yi, f'Yes! $= {sq}^2$', fontsize=12, ha='center',
                    color=ACCENT3, fontweight='bold')
        else:
            ax.text(7.5, yi, 'No', fontsize=12, ha='center', color=ACCENT1)

    ax.text(5, 1.7, r'Seek $x$ such that $x^2 - n$ is a perfect square $y^2$',
            fontsize=12, ha='center', color=DARK, fontstyle='italic')
    ax.text(5, 1.2, r'Then $n = x^2 - y^2 = (x-y)(x+y)$',
            fontsize=13, ha='center', color=ACCENT1, fontweight='bold')

    ax.set_xlim(0, 10)
    ax.set_ylim(0.5, 10)
    save(fig, 'fig04_fermat_margin.png')


# ============================================================
# FIGURE 5: Balanced vs. unbalanced factors on number line
# ============================================================
def fig05_balanced_factors():
    fig, axes = plt.subplots(2, 1, figsize=(14, 7), gridspec_kw={'hspace': 0.5})
    fig.set_facecolor(SAND)

    for idx, ax in enumerate(axes):
        ax.set_facecolor(SAND)
        ax.set_xlim(0, 100)
        ax.set_ylim(-0.5, 3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.set_yticks([])

        ax.axhline(y=0, color=DARK, linewidth=2)

        if idx == 0:
            sqn = 50
            p, q = 42, 58
            ax.plot(sqn, 0, 'D', color=GOLD, markersize=12, zorder=10)
            ax.text(sqn, -0.35, r'$\sqrt{n}$', fontsize=14, ha='center', color=GOLD, fontweight='bold')

            ax.plot(p, 0, 'o', color=ACCENT1, markersize=14, zorder=10)
            ax.text(p, 0.4, '$p$', fontsize=16, ha='center', color=ACCENT1, fontweight='bold')
            ax.plot(q, 0, 'o', color=ACCENT2, markersize=14, zorder=10)
            ax.text(q, 0.4, '$q$', fontsize=16, ha='center', color=ACCENT2, fontweight='bold')

            arc = patches.Arc((50, 0.8), q - p, 1.5, angle=0, theta1=0, theta2=180,
                              color=ACCENT3, linewidth=2.5)
            ax.add_patch(arc)
            ax.text(50, 2.2, 'Fast convergence', fontsize=13, ha='center',
                    color=ACCENT3, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor=LIGHT_GREEN, alpha=0.6))
            ax.set_title('Scenario A: Balanced Factors',
                         fontsize=14, color=DARK, fontweight='bold')
        else:
            sqn = 50
            p, q = 5, 95
            ax.plot(sqn, 0, 'D', color=GOLD, markersize=12, zorder=10)
            ax.text(sqn, -0.35, r'$\sqrt{n}$', fontsize=14, ha='center', color=GOLD, fontweight='bold')

            ax.plot(p, 0, 'o', color=ACCENT1, markersize=14, zorder=10)
            ax.text(p, 0.4, '$p$', fontsize=16, ha='center', color=ACCENT1, fontweight='bold')
            ax.plot(q, 0, 'o', color=ACCENT2, markersize=14, zorder=10)
            ax.text(q, 0.4, '$q$', fontsize=16, ha='center', color=ACCENT2, fontweight='bold')

            arc = patches.Arc((50, 0.8), q - p, 2.5, angle=0, theta1=0, theta2=180,
                              color=ACCENT1, linewidth=2.5, linestyle='--')
            ax.add_patch(arc)
            ax.text(50, 2.5, 'Slow convergence -- as bad as trial division',
                    fontsize=13, ha='center', color=ACCENT1, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor=LIGHT_RED, alpha=0.6))
            ax.set_title('Scenario B: Unbalanced Factors',
                         fontsize=14, color=DARK, fontweight='bold')

    save(fig, 'fig05_balanced_factors.png')


# ============================================================
# FIGURE 6: Smoothness spectrum chart
# ============================================================
def fig06_smoothness_spectrum():
    fig, ax = plt.subplots(1, 1, figsize=(16, 7))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    def largest_prime_factor(n):
        if n <= 1:
            return 0
        factor = 2
        lpf = 1
        temp = n
        while factor * factor <= temp:
            while temp % factor == 0:
                lpf = factor
                temp //= factor
            factor += 1
        if temp > 1:
            lpf = temp
        return lpf

    xs = list(range(2, 101))
    lpfs = [largest_prime_factor(x) for x in xs]

    for x, lpf in zip(xs, lpfs):
        if lpf <= 7:
            color = ACCENT3
        elif lpf <= 11:
            color = ACCENT2
        elif lpf <= 13:
            color = GOLD
        else:
            color = ACCENT1
        ax.bar(x, lpf, color=color, edgecolor=color, width=0.8, alpha=0.85)

    ax.axhline(y=7, color=DARK, linewidth=1.5, linestyle='--', alpha=0.7)
    ax.text(102, 7, '$B = 7$', fontsize=12, va='center', color=DARK, fontweight='bold')

    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=ACCENT3, label='7-smooth'),
        Patch(facecolor=ACCENT2, label='11-smooth'),
        Patch(facecolor=GOLD, label='13-smooth'),
        Patch(facecolor=ACCENT1, label='Rough (lpf > 13)'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=11, framealpha=0.9)

    ax.annotate('$64 = 2^6$\nlpf $= 2$', xy=(64, 2), xytext=(64, 20),
                fontsize=10, ha='center', color=ACCENT3, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=ACCENT3))
    ax.annotate('$97$ (prime)\nlpf $= 97$', xy=(97, 97), xytext=(85, 85),
                fontsize=10, ha='center', color=ACCENT1, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=ACCENT1))
    ax.annotate('$96 = 2^5 \\cdot 3$\nlpf $= 3$', xy=(96, 3), xytext=(80, 30),
                fontsize=10, ha='center', color=ACCENT3, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=ACCENT3))

    ax.set_xlabel('Integer $n$', fontsize=14, color=DARK)
    ax.set_ylabel('Largest prime factor', fontsize=14, color=DARK)
    ax.set_title('The Smoothness Spectrum: Integers 2--100',
                 fontsize=18, color=DARK, fontweight='bold', pad=15)
    ax.set_xlim(0, 105)
    ax.set_ylim(0, 100)
    save(fig, 'fig06_smoothness_spectrum.png')


# ============================================================
# FIGURE 7: Smooth vs rough boulders
# ============================================================
def fig07_smooth_vs_rough():
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.axis('off')

    # Hill / slope
    slope_x = np.linspace(0, 14, 200)
    slope_y = 2 + 3 * np.exp(-0.15 * slope_x)
    ax.fill_between(slope_x, 0, slope_y, color='#8FBC8F', alpha=0.3)
    ax.plot(slope_x, slope_y, color=ACCENT3, linewidth=2)

    # Sieve at bottom
    for sx in np.linspace(10.5, 13.5, 8):
        ax.plot([sx, sx], [1.5, 2.1], color='#888888', linewidth=2)
    ax.plot([10, 14], [2.1, 2.1], color=DARK, linewidth=3)
    ax.plot([10, 14], [1.5, 1.5], color=DARK, linewidth=3)
    ax.text(12, 1.2, 'SIEVE', fontsize=14, ha='center', va='center',
            color=DARK, fontweight='bold')

    # Smooth boulder (rolling down)
    idx_8 = int(8/14*200)
    smooth = plt.Circle((8, slope_y[idx_8] + 0.8), 0.8,
                        facecolor=ACCENT3, edgecolor=DARK, linewidth=2, zorder=10)
    ax.add_patch(smooth)
    ax.text(8, slope_y[idx_8] + 0.8, 'S', fontsize=20, ha='center', va='center',
            zorder=11, color='white', fontweight='bold')
    ax.text(8, slope_y[idx_8] + 2.2, '$120 = 2^3 \\times 3 \\times 5$',
            fontsize=12, ha='center', color=ACCENT3, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=LIGHT_GREEN, alpha=0.7))
    # Track
    for tx in np.linspace(3, 7.5, 15):
        ty = 2 + 3 * np.exp(-0.15 * tx)
        ax.plot(tx, ty + 0.1, '.', color=ACCENT3, markersize=4, alpha=0.5)

    # Rough rock (stuck higher up)
    rough_x = 4
    rough_y = 2 + 3 * np.exp(-0.15 * 4) + 0.5
    angles = np.linspace(0, 2*np.pi, 12, endpoint=False)
    radii = [0.7 + 0.3 * ((i % 2) * 2 - 1) * 0.5 for i in range(12)]
    jx = rough_x + np.array([r * np.cos(a) for r, a in zip(radii, angles)])
    jy = rough_y + np.array([r * np.sin(a) for r, a in zip(radii, angles)])
    ax.fill(jx, jy, color=ACCENT1, alpha=0.8, zorder=10)
    ax.plot(np.append(jx, jx[0]), np.append(jy, jy[0]), color=DARK, linewidth=2, zorder=10)
    ax.text(rough_x, rough_y, 'R', fontsize=16, ha='center', va='center',
            zorder=11, color='white', fontweight='bold')
    ax.text(rough_x, rough_y + 1.5, '$127$ (prime)', fontsize=12, ha='center',
            color=ACCENT1, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=LIGHT_RED, alpha=0.7))

    ax.text(7, 0.3, '"Smooth numbers roll through the sieve; rough ones get stuck."',
            fontsize=13, ha='center', va='center', color=DARK, fontstyle='italic',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=CREAM, alpha=0.8))

    ax.set_xlim(0, 14)
    ax.set_ylim(-0.2, 8)
    ax.set_title("Smooth vs. Rough: The Sieve's Verdict",
                 fontsize=18, color=DARK, fontweight='bold', pad=15)
    save(fig, 'fig07_smooth_vs_rough.png')


# ============================================================
# FIGURE 8: Arsenal rack / factor base compartments
# ============================================================
def fig08_arsenal_rack():
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.axis('off')

    primes = [2, 3, 5, 7, 11, 13]
    n_primes = len(primes)
    slot_w = 1.5
    slot_h = 3
    gap = 0.3
    start_x = (14 - n_primes * (slot_w + gap)) / 2

    rack = FancyBboxPatch((start_x - 0.3, 5), n_primes * (slot_w + gap) + 0.3, slot_h + 1,
                          boxstyle="round,pad=0.2", facecolor='#D2B48C',
                          edgecolor='#8B4513', linewidth=3)
    ax.add_patch(rack)

    for i, p in enumerate(primes):
        x = start_x + i * (slot_w + gap)
        slot = patches.Rectangle((x, 5.3), slot_w, slot_h, facecolor=CREAM,
                                 edgecolor=DARK, linewidth=1.5)
        ax.add_patch(slot)
        ax.text(x + slot_w/2, 5.3 + slot_h + 0.3, f'${p}$', fontsize=16,
                ha='center', va='center', color=DARK, fontweight='bold')

    ax.text(7, 4.3, '$360 = 2^3 \\times 3^2 \\times 5$', fontsize=14,
            ha='center', color=ACCENT2, fontweight='bold')
    balls_360 = {0: 3, 1: 2, 2: 1, 3: 0, 4: 0, 5: 0}
    ball_colors = {0: ACCENT1, 1: ACCENT2, 2: ACCENT3, 3: ACCENT5, 4: ACCENT4, 5: GOLD}
    for i, count in balls_360.items():
        x = start_x + i * (slot_w + gap) + slot_w / 2
        for j in range(count):
            ball = plt.Circle((x, 5.8 + j * 0.7), 0.25, facecolor=ball_colors[i],
                              edgecolor=DARK, linewidth=1.5, zorder=10)
            ax.add_patch(ball)

    ax.text(7, 3.5, 'Vector: $(3, 2, 1, 0, 0, 0)$', fontsize=12,
            ha='center', color=DARK, fontstyle='italic')

    ax.text(7, 2.5, '$1001 = 7 \\times 11 \\times 13$', fontsize=14,
            ha='center', color=ACCENT4, fontweight='bold')

    balls_1001 = {0: 0, 1: 0, 2: 0, 3: 1, 4: 1, 5: 1}
    for i, count in balls_1001.items():
        x = start_x + i * (slot_w + gap) + slot_w / 2
        for j in range(count):
            ball = plt.Circle((x, 1.5 + j * 0.7), 0.25, facecolor=ball_colors[i],
                              edgecolor=DARK, linewidth=1.5, zorder=10)
            ax.add_patch(ball)

    ax.text(7, 0.7, 'Vector: $(0, 0, 0, 1, 1, 1)$', fontsize=12,
            ha='center', color=DARK, fontstyle='italic')

    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10.5)
    ax.set_title('The Factor Base Arsenal: $\\mathcal{F}(13)$',
                 fontsize=18, color=DARK, fontweight='bold', pad=15)
    save(fig, 'fig08_arsenal_rack.png')


# ============================================================
# FIGURE 9: Exponent matrix tableau (blackboard style)
# ============================================================
def fig09_matrix_tableau():
    fig, axes = plt.subplots(1, 2, figsize=(16, 8), gridspec_kw={'wspace': 0.3})
    fig.set_facecolor('#2C3E50')

    primes = [2, 3, 5, 7, 11]
    numbers = [
        ('$a_1 = 600$',  [3, 1, 2, 0, 0]),
        ('$a_2 = 252$',  [2, 2, 0, 1, 0]),
        ('$a_3 = 1050$', [1, 1, 2, 1, 0]),
        ('$a_4 = 462$',  [1, 1, 0, 1, 1]),
        ('$a_5 = 660$',  [2, 1, 1, 0, 1]),
        ('$a_6 = 180$',  [2, 2, 1, 0, 0]),
    ]
    highlight_rows = [1, 3, 4]

    for panel, (ax, title, mod2) in enumerate(zip(axes,
                                                  ['Exponent Matrix', 'Matrix mod 2'],
                                                  [False, True])):
        ax.set_facecolor('#2C3E50')
        ax.axis('off')
        ax.set_title(title, fontsize=16, color='white', fontweight='bold', pad=10)

        for j, p in enumerate(primes):
            ax.text(2.5 + j * 1.5, 6.5, f'${p}$', fontsize=14, ha='center', va='center',
                    color=GLOW, fontweight='bold')

        for i, (label, exps) in enumerate(numbers):
            yi = 5.5 - i * 0.9
            is_hl = i in highlight_rows

            if is_hl:
                rect = patches.Rectangle((0.5, yi - 0.35), 9, 0.7,
                                         facecolor=GLOW, alpha=0.15)
                ax.add_patch(rect)

            ax.text(1.2, yi, label, fontsize=11, ha='center', va='center',
                    color=GLOW if is_hl else 'white')

            for j, e in enumerate(exps):
                val = e % 2 if mod2 else e
                ax.text(2.5 + j * 1.5, yi, f'${val}$', fontsize=13, ha='center', va='center',
                        color='white', fontweight='bold' if is_hl else 'normal')

        if mod2:
            col_sums = [sum(numbers[r][1][j] for r in highlight_rows) % 2 for j in range(5)]
            yi_sum = 5.5 - 6 * 0.9 - 0.3
            ax.plot([1.5, 9], [yi_sum + 0.45, yi_sum + 0.45], color=GLOW, linewidth=1.5)
            ax.text(1.2, yi_sum, '$\\Sigma$', fontsize=13, ha='center', va='center', color=GLOW)
            for j, s in enumerate(col_sums):
                ax.text(2.5 + j * 1.5, yi_sum, f'${s}$', fontsize=13, ha='center', va='center',
                        color=ACCENT3 if s == 0 else ACCENT1, fontweight='bold')

            ax.text(5, yi_sum - 0.8, '$a_2 \\times a_4 \\times a_5 = $ perfect square!',
                    fontsize=13, ha='center', color=GLOW, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor=ACCENT3, alpha=0.3))

        ax.set_xlim(0, 10)
        ax.set_ylim(-1, 7.5)

    save(fig, 'fig09_matrix_tableau.png')


# ============================================================
# FIGURE 10: Pigeonhole / F_2^3 cube
# ============================================================
def fig10_pigeonhole_cube():
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    vertices = [(i, j, k) for i in [0, 1] for j in [0, 1] for k in [0, 1]]

    for v1 in vertices:
        for v2 in vertices:
            if sum(abs(a - b) for a, b in zip(v1, v2)) == 1:
                ax.plot3D(*zip(v1, v2), color='#AAAAAA', linewidth=1, alpha=0.5)

    for v in vertices:
        label = f'$({v[0]},{v[1]},{v[2]})$'
        ax.text(v[0], v[1], v[2], label, fontsize=9, ha='center', va='bottom')
        ax.scatter(*v, color=SLATE, s=40, zorder=5)

    vectors = {
        '$\\mathbf{r}_0$': (1, 0, 0),
        '$\\mathbf{r}_1$': (0, 1, 0),
        '$\\mathbf{r}_2$': (1, 1, 0),
        '$\\mathbf{r}_3$': (0, 0, 1),
    }
    colors_v = [ACCENT1, ACCENT2, ACCENT3, ACCENT4]

    for (name, vec), col in zip(vectors.items(), colors_v):
        ax.quiver(0, 0, 0, vec[0], vec[1], vec[2], color=col, linewidth=3,
                  arrow_length_ratio=0.15, zorder=10)
        ax.text(vec[0] * 1.15, vec[1] * 1.15, vec[2] * 1.15, name,
                fontsize=12, color=col, fontweight='bold')

    dep_pts = [(1, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)]
    dep_x, dep_y, dep_z = zip(*dep_pts)
    ax.plot3D(dep_x, dep_y, dep_z, color=GLOW, linewidth=3, linestyle='--', zorder=8)

    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_zticks([0, 1])
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_zlabel('')
    ax.view_init(elev=25, azim=45)

    ax.set_title('$\\mathbb{F}_2^3$: 4 vectors in 3 dimensions\n-- a dependency must exist!',
                 fontsize=16, color=DARK, fontweight='bold', pad=20)
    save(fig, 'fig10_pigeonhole_cube.png')


# ============================================================
# FIGURE 11: Gaussian elimination over F_2
# ============================================================
def fig11_gaussian_elimination():
    fig, axes = plt.subplots(3, 1, figsize=(12, 14), gridspec_kw={'hspace': 0.4})
    fig.set_facecolor(SAND)

    M_orig = np.array([
        [1, 1, 0, 0, 0],
        [0, 0, 1, 1, 0],
        [1, 1, 1, 1, 0],
        [1, 0, 0, 1, 1],
        [0, 1, 1, 0, 1],
        [0, 0, 1, 0, 0],
    ])

    M_step1 = M_orig.copy()
    M_step1[2] = (M_step1[2] + M_step1[0]) % 2

    M_rref = np.array([
        [1, 0, 0, 1, 1],
        [0, 1, 0, 1, 1],
        [0, 0, 1, 1, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ])

    matrices = [
        (M_orig, 'Original Matrix', None),
        (M_step1, 'After Row 3 = Row 3 + Row 1 (XOR)', 'Row 3 = Row 3 XOR Row 1'),
        (M_rref, 'Reduced Row-Echelon Form', None),
    ]

    for ax, (M, title, note) in zip(axes, matrices):
        ax.set_facecolor(SAND)
        ax.axis('off')
        ax.set_title(title, fontsize=14, color=DARK, fontweight='bold')

        rows, cols = M.shape
        for i in range(rows):
            for j in range(cols):
                val = int(M[i, j])
                is_zero_row = (M[i].sum() == 0)
                bg = LIGHT_RED if is_zero_row else CREAM
                cell = patches.Rectangle((2 + j * 1.2, 4 - i * 0.8), 1, 0.6,
                                         facecolor=bg, edgecolor=DARK, linewidth=1)
                ax.add_patch(cell)
                ax.text(2.5 + j * 1.2, 4.3 - i * 0.8, f'${val}$', fontsize=14,
                        ha='center', va='center', color=DARK, fontweight='bold')

        for i in range(rows):
            ax.text(1.5, 4.3 - i * 0.8, f'$R_{i+1}$', fontsize=12,
                    ha='center', va='center', color=SLATE)

        for j, p in enumerate([2, 3, 5, 7, 11]):
            ax.text(2.5 + j * 1.2, 4.9, f'${p}$', fontsize=12,
                    ha='center', va='center', color=ACCENT2, fontweight='bold')

        if note:
            ax.text(9, 2.5, note, fontsize=12, color=ACCENT4, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor=CREAM, alpha=0.8))

        ax.set_xlim(0, 12)
        ax.set_ylim(-1.5, 5.5)

    axes[2].text(9, 1, 'Zero rows reveal\nlinear dependencies!',
                 fontsize=13, color=ACCENT1, fontweight='bold', ha='center',
                 bbox=dict(boxstyle='round,pad=0.4', facecolor=LIGHT_RED, alpha=0.6))

    save(fig, 'fig11_gaussian_elimination.png')


# ============================================================
# FIGURE 12: Flowchart of the sieve algorithm
# ============================================================
def fig12_sieve_flowchart():
    fig, ax = plt.subplots(1, 1, figsize=(10, 16))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.axis('off')

    steps = [
        ('Step 1', 'Choose smoothness\nbound $B$', ACCENT2),
        ('Step 2', 'Build factor base\n$\\mathcal{F}(B)$, size $k$', ACCENT2),
        ('Step 3', 'Sieve: find $k+1$ values\nof $x$ with $x^2$ mod $n$\nbeing $B$-smooth', ACCENT3),
        ('Step 4', 'Build exponent\nmatrix mod 2', ACCENT4),
        ('Step 5', 'Gaussian elimination\nfind subset $S$', ACCENT4),
        ('Step 6', 'Compute\n$X = \\prod x_i$,  $Y = \\sqrt{\\prod a_i}$', ACCENT5),
        ('Step 7', 'Compute $\\gcd(X-Y, n)$\nNontrivial? Done!', ACCENT1),
    ]

    box_h = 1.4
    gap = 0.6
    x_center = 5
    y_start = 15

    for i, (label, text, color) in enumerate(steps):
        y = y_start - i * (box_h + gap)
        box = FancyBboxPatch((x_center - 3, y - box_h/2), 6, box_h,
                             boxstyle="round,pad=0.3", facecolor='white',
                             edgecolor=color, linewidth=2.5)
        ax.add_patch(box)

        circle = plt.Circle((x_center - 2.5, y), 0.35, facecolor=color,
                            edgecolor=DARK, linewidth=1.5, zorder=10)
        ax.add_patch(circle)
        ax.text(x_center - 2.5, y, str(i+1), fontsize=12, ha='center', va='center',
                color='white', fontweight='bold', zorder=11)

        ax.text(x_center + 0.3, y, text, fontsize=11, ha='center', va='center',
                color=DARK, fontweight='bold')

        if i < len(steps) - 1:
            y_next = y_start - (i+1) * (box_h + gap)
            ax.annotate('', xy=(x_center, y_next + box_h/2),
                        xytext=(x_center, y - box_h/2),
                        arrowprops=dict(arrowstyle='->', color=DARK, lw=2))

    y7 = y_start - 6 * (box_h + gap)
    y5 = y_start - 4 * (box_h + gap)
    ax.annotate('', xy=(x_center + 3.5, y5),
                xytext=(x_center + 3.5, y7),
                arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=2,
                               connectionstyle='arc3,rad=0.3'))
    ax.text(x_center + 4.5, (y5 + y7) / 2, 'Try next\ndependency',
            fontsize=10, color=ACCENT1, ha='center', fontstyle='italic',
            bbox=dict(boxstyle='round,pad=0.2', facecolor=LIGHT_RED, alpha=0.5))

    ax.set_xlim(0, 10)
    ax.set_ylim(y_start - 7 * (box_h + gap) - 1, y_start + 1.5)
    ax.set_title('The Quadratic Sieve: Complete Algorithm',
                 fontsize=18, color=DARK, fontweight='bold', pad=20)
    save(fig, 'fig12_sieve_flowchart.png')


# ============================================================
# FIGURE 13: Sieving table (worked example)
# ============================================================
def fig13_sieving_table():
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.axis('off')

    n = 15347
    sqn = isqrt(n) + 1  # 124

    headers = ['$x$', '$x^2$', '$x^2$ mod $n$', 'Factorization', 'Smooth?']
    col_x = [1, 3, 5.5, 9, 12.5]
    y_start = 9

    for j, h in enumerate(headers):
        ax.text(col_x[j], y_start, h, fontsize=12, ha='center', va='center',
                fontweight='bold', color=DARK)
    ax.plot([0.2, 14.5], [y_start - 0.35, y_start - 0.35], color=DARK, linewidth=2)

    def factorize_small(val, bound=13):
        if val == 0:
            return '0', True
        if val == 1:
            return '1', True
        factors = {}
        temp = val
        for p in [2, 3, 5, 7, 11, 13]:
            while temp % p == 0:
                factors[p] = factors.get(p, 0) + 1
                temp //= p
        if temp > 1:
            return f'... (rem {temp})', False
        parts = []
        for p in sorted(factors):
            if factors[p] == 1:
                parts.append(f'{p}')
            else:
                parts.append(f'{p}^{{{factors[p]}}}')
        return '$' + ' \\cdot '.join(parts) + '$', True

    rows_data = []
    for dx in range(12):
        x = sqn + dx
        xsq = x * x
        residue = xsq - n
        if residue < 0:
            continue
        fact_str, is_smooth = factorize_small(residue)
        rows_data.append((x, xsq, residue, fact_str, is_smooth))

    for i, (x, xsq, res, fact, smooth) in enumerate(rows_data):
        if i >= 8:
            break
        yi = y_start - 0.75 * (i + 1)

        if smooth:
            rect = FancyBboxPatch((0.2, yi - 0.3), 14.3, 0.6, boxstyle="round,pad=0.05",
                                  facecolor=GLOW, alpha=0.25, edgecolor=GOLD, linewidth=1)
            ax.add_patch(rect)

        ax.text(col_x[0], yi, f'${x}$', fontsize=11, ha='center', va='center', color=DARK)
        ax.text(col_x[1], yi, f'${xsq}$', fontsize=10, ha='center', va='center', color=DARK)
        ax.text(col_x[2], yi, f'${res}$', fontsize=11, ha='center', va='center', color=DARK)
        ax.text(col_x[3], yi, fact, fontsize=10, ha='center', va='center', color=DARK)

        if smooth:
            ax.text(col_x[4], yi, 'YES', fontsize=12, ha='center', va='center',
                    color=ACCENT3, fontweight='bold')
        else:
            ax.text(col_x[4], yi, 'no', fontsize=12, ha='center', va='center', color=ACCENT1)

    ax.text(7.5, y_start - 8,
            'Collect smooth relations, then combine for congruence of squares.',
            fontsize=12, ha='center', color=DARK, fontstyle='italic',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=CREAM, alpha=0.8))

    ax.set_xlim(0, 15)
    ax.set_ylim(y_start - 9, y_start + 0.8)
    ax.set_title('Sieving Table for $n = 15{,}347$',
                 fontsize=18, color=DARK, fontweight='bold', pad=15)
    save(fig, 'fig13_sieving_table.png')


# ============================================================
# FIGURE 14: GCD gate -- the moment of triumph
# ============================================================
def fig14_gcd_gate():
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.axis('off')

    # Two pillars
    pillar_l = patches.Rectangle((3, 1), 1, 6, facecolor='#D2B48C',
                                 edgecolor=DARK, linewidth=2)
    pillar_r = patches.Rectangle((8, 1), 1, 6, facecolor='#D2B48C',
                                 edgecolor=DARK, linewidth=2)
    ax.add_patch(pillar_l)
    ax.add_patch(pillar_r)

    # Arch top
    arch = patches.Arc((6, 7), 6, 3, angle=0, theta1=0, theta2=180,
                       color=DARK, linewidth=3)
    ax.add_patch(arch)
    theta = np.linspace(0, np.pi, 100)
    arch_x = 6 + 3 * np.cos(theta)
    arch_y = 7 + 1.5 * np.sin(theta)
    ax.fill_between(arch_x, 7, arch_y, color='#D2B48C', alpha=0.5)

    # GCD label
    ax.text(6, 8, 'gcd', fontsize=36, ha='center', va='center',
            color=GOLD, fontweight='bold',
            path_effects=[pe.withStroke(linewidth=4, foreground=DARK)])

    # Input banners
    ax.annotate('', xy=(3.5, 5), xytext=(0.5, 5),
                arrowprops=dict(arrowstyle='->', color=ACCENT2, lw=3))
    ax.text(0.5, 5.5, '$X - Y$', fontsize=16, ha='center', color=ACCENT2, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=LIGHT_BLUE, alpha=0.7))

    ax.annotate('', xy=(8.5, 5), xytext=(11.5, 5),
                arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=3))
    ax.text(11.5, 5.5, '$n = 15{,}347$', fontsize=14, ha='center', color=ACCENT1, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=LIGHT_RED, alpha=0.7))

    # Output
    ax.annotate('', xy=(6, -0.5), xytext=(6, 1),
                arrowprops=dict(arrowstyle='->', color=GOLD, lw=4))

    spotlight = plt.Circle((6, -1.2), 1.2, facecolor=GLOW, alpha=0.3, edgecolor='none')
    ax.add_patch(spotlight)

    ax.text(5, -1.5, '$p$', fontsize=30, ha='center', va='center',
            color=ACCENT3, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=LIGHT_GREEN, alpha=0.8))

    ax.text(7.5, -1.5, '$q = n/p$', fontsize=18, ha='center', va='center',
            color=ACCENT4,
            bbox=dict(boxstyle='round,pad=0.3', facecolor=CREAM, alpha=0.8))

    # Confetti
    np.random.seed(42)
    for _ in range(30):
        cx = np.random.uniform(1, 11)
        cy = np.random.uniform(-2, 9)
        color = np.random.choice([ACCENT1, ACCENT2, ACCENT3, ACCENT4, ACCENT5, GOLD])
        ax.plot(cx, cy, '*', color=color, markersize=np.random.uniform(4, 10), alpha=0.5)

    ax.set_xlim(-0.5, 12.5)
    ax.set_ylim(-3, 10)
    ax.set_title('The Moment of Triumph: $\\gcd$ Reveals the Factors',
                 fontsize=18, color=DARK, fontweight='bold', pad=15)
    save(fig, 'fig14_gcd_gate.png')


# ============================================================
# FIGURE 15: Historical timeline of factoring methods
# ============================================================
def fig15_timeline():
    fig, ax = plt.subplots(1, 1, figsize=(18, 7))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.axis('off')

    milestones = [
        (1643, "Fermat's\nmethod", ACCENT1),
        (1798, "Legendre's\nimprovements", ACCENT5),
        (1975, "Morrison-\nBrillhart\n(CFRAC)", ACCENT2),
        (1981, "Dixon's\nrandom\nsquares", ACCENT4),
        (1982, "Pomerance's\nQuadratic\nSieve", ACCENT3),
        (1987, "Lenstra's\nECM", GOLD),
        (1993, "Number\nField\nSieve", SLATE),
        (2009, "RSA-768\nfactored", ACCENT1),
    ]

    x_min, x_max = 1620, 2030
    ax.plot([x_min, x_max], [3, 3], color=DARK, linewidth=4, zorder=1)

    # Gradient background
    for i, x in enumerate(np.linspace(x_min, x_max, 200)):
        frac = i / 200
        r = 0.96 * (1 - frac) + 0.16 * frac
        g = 0.90 * (1 - frac) + 0.50 * frac
        b = 0.78 * (1 - frac) + 0.73 * frac
        ax.axvline(x, ymin=0.3, ymax=0.7, color=(r, g, b), alpha=0.3, linewidth=2)

    for i, (year, label, color) in enumerate(milestones):
        above = (i % 2 == 0)
        y_dot = 3
        y_text = 5 if above else 1

        ax.plot(year, y_dot, 'o', color=color, markersize=14, zorder=10,
                markeredgecolor=DARK, markeredgewidth=1.5)

        ax.plot([year, year], [y_dot, y_text + (0.5 if above else -0.5)],
                color=color, linewidth=1.5, linestyle='--', alpha=0.7)

        ax.text(year, y_text, label, fontsize=9, ha='center',
                va='bottom' if above else 'top', color=DARK, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7,
                          edgecolor=color))

        ax.text(year, y_dot - 0.5 if above else y_dot + 0.5, str(year),
                fontsize=9, ha='center', va='top' if above else 'bottom', color=color,
                fontweight='bold')

    ax.set_xlim(x_min - 10, x_max + 10)
    ax.set_ylim(-0.5, 7)
    ax.set_title('A Brief History of Integer Factoring',
                 fontsize=18, color=DARK, fontweight='bold', pad=15)
    save(fig, 'fig15_timeline.png')


# ============================================================
# FIGURE 16: Triptych -- three disciplines converge
# ============================================================
def fig16_triptych():
    fig, axes = plt.subplots(1, 3, figsize=(18, 8), gridspec_kw={'wspace': 0.1})
    fig.set_facecolor(SAND)

    panels = [
        ('Number Theory', ACCENT1, LIGHT_RED,
         ['$x^2 \\equiv y^2$ (mod $n$)',
          '$\\gcd(x - y, n)$',
          'Congruences',
          'Quadratic residues']),
        ('Combinatorics', ACCENT3, LIGHT_GREEN,
         ['$B$-smooth numbers',
          'Birthday paradox',
          'Factor base $\\mathcal{F}(B)$',
          'Pigeonhole principle']),
        ('Linear Algebra', ACCENT2, LIGHT_BLUE,
         ['Exponent vectors mod 2',
          '$\\mathbb{F}_2$ row reduction',
          'Null space',
          'Linear dependencies']),
    ]

    for ax, (title, color, bg, items) in zip(axes, panels):
        ax.set_facecolor(bg)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')

        # Panel border (arch-like top)
        theta = np.linspace(0, np.pi, 100)
        arch_x = 5 + 4.5 * np.cos(theta)
        arch_y = 8.5 + 1 * np.sin(theta)
        ax.plot(arch_x, arch_y, color=color, linewidth=3)
        ax.plot([0.5, 0.5], [0, 8.5], color=color, linewidth=3)
        ax.plot([9.5, 9.5], [0, 8.5], color=color, linewidth=3)
        ax.plot([0.5, 9.5], [0, 0], color=color, linewidth=3)

        ax.text(5, 9, title, fontsize=16, ha='center', va='center',
                color=color, fontweight='bold')

        for i, item in enumerate(items):
            yi = 7 - i * 1.3
            ax.text(5, yi, item, fontsize=12, ha='center', va='center',
                    color=DARK,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))

        ax.annotate('', xy=(5, 0.3), xytext=(5, 1.5),
                    arrowprops=dict(arrowstyle='->', color=color, lw=3))

    fig.text(0.5, 0.02, 'Factors $p$ and $q$ of $n$',
             fontsize=20, ha='center', va='center', color=GOLD, fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='white',
                       edgecolor=GOLD, linewidth=3))

    fig.suptitle('Three Disciplines Unite to Factor $n$',
                 fontsize=20, color=DARK, fontweight='bold', y=0.98)
    save(fig, 'fig16_triptych.png')


# ============================================================
# Run all
# ============================================================
if __name__ == '__main__':
    print("Generating Chapter 11 illustrations...")
    fig01_treasure_chest()
    fig02_factorgram_table()
    fig03_venn_diagram()
    fig04_fermat_margin()
    fig05_balanced_factors()
    fig06_smoothness_spectrum()
    fig07_smooth_vs_rough()
    fig08_arsenal_rack()
    fig09_matrix_tableau()
    fig10_pigeonhole_cube()
    fig11_gaussian_elimination()
    fig12_sieve_flowchart()
    fig13_sieving_table()
    fig14_gcd_gate()
    fig15_timeline()
    fig16_triptych()
    print("Done! All images saved to", OUT)

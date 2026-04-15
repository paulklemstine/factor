#!/usr/bin/env python3
"""Generate all illustrations for Chapter 8: The Price of Descent."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe
import numpy as np
import os
from math import gcd, log2, sqrt, log

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
# FIGURE 1: The Locksmith's Tree
# ============================================================
def fig01_locksmith_tree():
    fig, ax = plt.subplots(1, 1, figsize=(10, 14))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    # Trunk
    trunk_x = [4.5, 4.5, 5.5, 5.5]
    trunk_y = [0, 10, 10, 0]
    ax.fill(trunk_x, trunk_y, color='#8B6914', alpha=0.5, zorder=1)

    # Canopy levels
    levels = 8
    for lv in range(levels):
        y = 1.2 + lv * 1.1
        width = 0.5 + lv * 0.55
        cx = 5.0
        ell = patches.Ellipse((cx, y), width * 2, 0.9, color=ACCENT3,
                               alpha=0.15 + 0.05 * lv, zorder=2)
        ax.add_patch(ell)
        n_nodes = min(2 * lv + 1, 7)
        for ni in range(n_nodes):
            nx = cx - width + 2 * width * ni / max(n_nodes - 1, 1)
            ax.plot(nx, y, 'o', color=ACCENT2, markersize=5, zorder=5, alpha=0.7)

    # Red descent path
    path_y = np.linspace(9.8, 0.3, 50)
    path_x = 5.0 + 0.4 * np.sin(path_y * 2.5)
    ax.plot(path_x, path_y, color=ACCENT1, linewidth=3, zorder=6, alpha=0.85)
    ax.annotate('The Descent', xy=(path_x[25], path_y[25]),
                xytext=(7.5, path_y[25]), fontsize=13, color=ACCENT1,
                fontweight='bold', ha='left',
                arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=1.5))

    # sqrt(N) dashed line
    sqN_y = 4.5
    ax.axhline(sqN_y, color=DARK, linestyle='--', linewidth=2, zorder=4)
    ax.text(8.5, sqN_y + 0.2, r'$\sqrt{N}$', fontsize=16, color=DARK,
            fontweight='bold', ha='center')
    ax.text(8.5, sqN_y - 0.5, '"You must pass\n through here"', fontsize=10,
            color=SLATE, ha='center', fontstyle='italic')

    # Locksmith at the top
    lx, ly = 5.0, 10.5
    ax.plot(lx, ly + 0.3, 'o', color=ACCENT5, markersize=14, zorder=8)
    ax.plot([lx, lx], [ly - 0.3, ly + 0.15], color=DARK, linewidth=2, zorder=8)
    ax.plot([lx - 0.3, lx, lx + 0.3], [ly - 0.1, ly + 0.0, ly - 0.1],
            color=DARK, linewidth=2, zorder=8)
    circle_mg = plt.Circle((lx + 0.55, ly + 0.15), 0.18, fill=False,
                            edgecolor=DARK, linewidth=2, zorder=8)
    ax.add_patch(circle_mg)
    ax.plot([lx + 0.4, lx + 0.3], [ly + 0.0, ly - 0.15], color=DARK, linewidth=2, zorder=8)
    ax.text(lx + 0.55, ly + 0.15, r'$N$', fontsize=8, ha='center', va='center',
            color=DARK, fontweight='bold', zorder=9)

    # Roots labeled with primes
    primes = [2, 3, 5, 7, 11]
    for i, p in enumerate(primes):
        rx = 3.5 + i * 0.8
        ry = -0.3 - 0.2 * abs(i - 2)
        ax.plot([rx, 4.5 + (rx - 3.5) * 0.3], [ry, 0.3], color='#8B6914',
                linewidth=1.5, alpha=0.6, zorder=1)
        ax.text(rx, ry - 0.3, str(p), fontsize=11, ha='center', color=DARK, fontweight='bold')

    ax.set_xlim(1, 10)
    ax.set_ylim(-1.5, 11.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title("The Locksmith's Tree", fontsize=18, color=DARK, fontweight='bold', pad=10)
    save(fig, 'fig01_locksmith_tree.png')


# ============================================================
# FIGURE 2: Euclid's Staircase / Nautilus for (377, 233)
# ============================================================
def fig02_euclid_staircase():
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    steps_a = [377, 233, 144, 89, 55, 34, 21, 13, 8, 5, 3, 2, 1]
    n = len(steps_a)
    colors = [ACCENT1, ACCENT2, ACCENT3, ACCENT5, ACCENT4, GOLD,
              ACCENT1, ACCENT2, ACCENT3, ACCENT5, ACCENT4, GOLD, ACCENT1]
    y_positions = list(range(n - 1, -1, -1))

    ax.barh(y_positions, steps_a, height=0.7,
            color=[colors[i % len(colors)] for i in range(n)],
            edgecolor=DARK, linewidth=1, alpha=0.5, zorder=3)

    for i, (yp, val) in enumerate(zip(y_positions, steps_a)):
        ax.text(val + 5, yp, str(val), fontsize=10, va='center', color=DARK, fontweight='bold')
        if i < n - 1:
            q = steps_a[i] // steps_a[i + 1]
            ax.text(-15, yp, f'q={q}', fontsize=9, va='center', ha='right', color=SLATE)

    ax.text(1, y_positions[-1] - 0.8, r'$\gcd = 1$', fontsize=13, color=ACCENT1,
            fontweight='bold', ha='left')

    ax.text(200, n - 0.5, r'$\frac{377}{233} = [1; 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2]$',
            fontsize=12, color=DARK, ha='center', fontweight='bold')
    ax.text(200, n - 1.5, '(Fibonacci connection: all quotients are 1)',
            fontsize=10, color=SLATE, ha='center', fontstyle='italic')

    ax.set_xlabel('Remainder size', fontsize=12, color=DARK)
    ax.set_ylabel('Step number (descending)', fontsize=12, color=DARK)
    ax.set_title("Euclid's Staircase: (377, 233)", fontsize=16, color=DARK, fontweight='bold')
    ax.set_xlim(-30, 420)
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    save(fig, 'fig02_euclid_staircase.png')


# ============================================================
# FIGURE 3: Euclidean algorithm step count plot
# ============================================================
def fig03_step_count_plot():
    fig, ax = plt.subplots(1, 1, figsize=(10, 7))
    fig.set_facecolor(SAND)
    ax.set_facecolor(CREAM)

    np.random.seed(42)

    def euclid_steps(a, b):
        steps = 0
        while b > 0:
            a, b = b, a % b
            steps += 1
        return steps

    max_val = 2000
    n_pts = 1500
    xs, ys = [], []
    for _ in range(n_pts):
        a = np.random.randint(2, max_val)
        b = np.random.randint(2, max_val)
        m = min(a, b)
        xs.append(m)
        ys.append(euclid_steps(a, b))

    ax.scatter(xs, ys, s=8, color=ACCENT2, alpha=0.3, zorder=3, label='Random pairs')

    fibs = [1, 1]
    while fibs[-1] < max_val:
        fibs.append(fibs[-1] + fibs[-2])

    fib_x, fib_y = [], []
    for i in range(2, len(fibs) - 1):
        fib_x.append(fibs[i])
        fib_y.append(euclid_steps(fibs[i + 1], fibs[i]))

    ax.plot(fib_x, fib_y, 'o-', color=ACCENT1, markersize=6, linewidth=2,
            zorder=5, label='Fibonacci worst case')

    t = np.linspace(2, max_val, 200)
    theory = 2.078 * np.log(t)
    ax.plot(t, theory, '--', color=ACCENT5, linewidth=2, zorder=4,
            label=r'$\sim 2.078 \ln(\min(a,b))$')

    ax.set_xlabel(r'$\min(a, b)$', fontsize=13, color=DARK)
    ax.set_ylabel('Number of Euclidean steps', fontsize=13, color=DARK)
    ax.set_title('Euclidean Algorithm: Step Count vs. Input Size',
                 fontsize=15, color=DARK, fontweight='bold')
    ax.legend(fontsize=11, framealpha=0.9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    save(fig, 'fig03_step_count_plot.png')


# ============================================================
# FIGURE 4: The Danger Zone — number line with p, q, sqrt(N)
# ============================================================
def fig04_danger_zone():
    fig, axes = plt.subplots(2, 1, figsize=(12, 7), gridspec_kw={'hspace': 0.6})
    fig.set_facecolor(SAND)

    for idx, ax in enumerate(axes):
        ax.set_facecolor(SAND)
        ax.set_xlim(-0.05, 1.05)
        ax.set_ylim(-0.5, 1.2)

        ax.plot([0, 1], [0, 0], color=DARK, linewidth=3, zorder=3)
        ax.plot(0, 0, '|', color=DARK, markersize=15, zorder=4)
        ax.plot(1, 0, '|', color=DARK, markersize=15, zorder=4)
        ax.text(0, -0.25, '1', fontsize=11, ha='center', color=DARK)
        ax.text(1, -0.25, r'$N$', fontsize=13, ha='center', color=DARK, fontweight='bold')

        sq = 0.5
        ax.plot(sq, 0, '|', color=GOLD, markersize=20, zorder=5)
        ax.text(sq, -0.25, r'$\sqrt{N}$', fontsize=12, ha='center', color=GOLD, fontweight='bold')

        if idx == 0:
            p_pos, q_pos = 0.1, 0.9
            ax.plot(p_pos, 0, 'o', color=ACCENT3, markersize=14, zorder=6)
            ax.plot(q_pos, 0, 'o', color=ACCENT3, markersize=14, zorder=6)
            ax.text(p_pos, 0.15, r'$p$', fontsize=14, ha='center', color=ACCENT3, fontweight='bold')
            ax.text(q_pos, 0.15, r'$q$', fontsize=14, ha='center', color=ACCENT3, fontweight='bold')
            ax.annotate('', xy=(p_pos, 0.6), xytext=(0.0, 0.6),
                        arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=2.5))
            ax.text(p_pos / 2, 0.75, 'Short descent', fontsize=10, ha='center',
                    color=ACCENT1, fontweight='bold')
            ax.set_title('(a) Easy: $p$ and $q$ far apart \u2014 shallow tree',
                         fontsize=13, color=DARK, fontweight='bold')
        else:
            p_pos, q_pos = 0.47, 0.53
            ax.plot(p_pos, 0, 'o', color=ACCENT1, markersize=14, zorder=6)
            ax.plot(q_pos, 0, 'o', color=ACCENT1, markersize=14, zorder=6)
            ax.text(p_pos - 0.03, 0.15, r'$p$', fontsize=14, ha='center',
                    color=ACCENT1, fontweight='bold')
            ax.text(q_pos + 0.03, 0.15, r'$q$', fontsize=14, ha='center',
                    color=ACCENT1, fontweight='bold')
            ax.axvspan(0.35, 0.65, alpha=0.2, color=ACCENT1, zorder=1)
            ax.text(0.5, 1.0, 'The Danger Zone', fontsize=13, ha='center',
                    color=ACCENT1, fontweight='bold', fontstyle='italic')
            ax.annotate('', xy=(p_pos, 0.6), xytext=(0.0, 0.6),
                        arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=2.5))
            ax.text(p_pos / 2, 0.75, 'Long descent', fontsize=10, ha='center',
                    color=ACCENT1, fontweight='bold')
            ax.set_title(r'(b) Hard: $p \approx q$ near $\sqrt{N}$ \u2014 deep tree',
                         fontsize=13, color=DARK, fontweight='bold')
        ax.axis('off')

    save(fig, 'fig04_danger_zone.png')


# ============================================================
# FIGURE 5: The Nearly-Square Rectangle
# ============================================================
def fig05_nearly_square():
    fig, ax = plt.subplots(1, 1, figsize=(9, 8))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    p, q = 101, 103
    N = p * q

    rect_full = patches.Rectangle((0, 0), q, p, linewidth=2.5, edgecolor=DARK,
                                   facecolor=LIGHT_BLUE, alpha=0.3, zorder=2)
    ax.add_patch(rect_full)

    rect_sq = patches.Rectangle((0, 0), p, p, linewidth=2, edgecolor=ACCENT2,
                                 facecolor=ACCENT2, alpha=0.15, zorder=3, linestyle='--')
    ax.add_patch(rect_sq)

    rect_strip = patches.Rectangle((p, 0), q - p, p, linewidth=2, edgecolor=ACCENT1,
                                    facecolor=ACCENT1, alpha=0.2, zorder=3)
    ax.add_patch(rect_strip)

    ax.text(q / 2, -5, f'$q = {q}$', fontsize=15, ha='center', color=DARK, fontweight='bold')
    ax.text(-5, p / 2, f'$p = {p}$', fontsize=15, ha='center', va='center', color=DARK,
            fontweight='bold', rotation=90)
    ax.text(p / 2, p / 2, f'$p \\times p$\n$= {p}^2 = {p*p}$',
            fontsize=13, ha='center', va='center', color=ACCENT2, fontweight='bold')
    ax.text(p + (q - p) / 2, p / 2,
            f'surplus\n$p(q-p)$\n$= {p}\\times{q-p}$\n$= {p*(q-p)}$',
            fontsize=10, ha='center', va='center', color=ACCENT1, fontweight='bold')

    ax.text(q / 2, p + 8, f'$N = p \\times q = {p} \\times {q} = {N}$',
            fontsize=14, ha='center', color=DARK, fontweight='bold')
    ax.text(q / 2, -15, '"A balanced semiprime is almost a perfect square."',
            fontsize=11, ha='center', color=SLATE, fontstyle='italic')

    ax.set_xlim(-12, q + 10)
    ax.set_ylim(-22, p + 15)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('The Nearly-Square Rectangle', fontsize=16, color=DARK, fontweight='bold')
    save(fig, 'fig05_nearly_square.png')


# ============================================================
# FIGURE 6: GCD Decision Node
# ============================================================
def fig06_gcd_node():
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    node = plt.Circle((5, 6), 1.2, color=LIGHT_BLUE, ec=DARK, linewidth=2.5, zorder=5)
    ax.add_patch(node)
    ax.text(5, 6, r'$(a,\, b,\, c)$', fontsize=16, ha='center', va='center',
            color=DARK, fontweight='bold', zorder=6)

    ax.annotate('', xy=(5, 3.8), xytext=(5, 4.8),
                arrowprops=dict(arrowstyle='->', color=DARK, lw=2.5))

    gcd_box = FancyBboxPatch((3.3, 3.0), 3.4, 1.0, boxstyle="round,pad=0.15",
                              facecolor=GLOW, edgecolor=DARK, linewidth=2, zorder=5)
    ax.add_patch(gcd_box)
    ax.text(5, 3.5, r'$\gcd(a,\, N)$', fontsize=14, ha='center', va='center',
            color=DARK, fontweight='bold', zorder=6)

    # Green: factor found
    ax.annotate('', xy=(1.5, 1.5), xytext=(3.5, 3.0),
                arrowprops=dict(arrowstyle='->', color=ACCENT3, lw=3))
    ax.text(1.5, 1.8, r'$\gcd > 1$', fontsize=13, ha='center', color=ACCENT3, fontweight='bold')
    ax.text(1.5, 1.2, 'Factor found!', fontsize=12, ha='center', color=ACCENT3, fontstyle='italic')
    lock_x, lock_y = 1.5, 0.3
    ax.plot([lock_x - 0.3, lock_x - 0.3, lock_x + 0.3, lock_x + 0.3],
            [lock_y, lock_y + 0.5, lock_y + 0.5, lock_y], color=ACCENT3, linewidth=2.5, zorder=5)
    theta = np.linspace(0, np.pi, 30)
    shackle_r = 0.25
    ax.plot(lock_x + shackle_r * np.cos(theta) + 0.1,
            lock_y + 0.5 + shackle_r * np.sin(theta),
            color=ACCENT3, linewidth=2.5, zorder=5)

    # Red: continue descent
    ax.annotate('', xy=(8.5, 1.5), xytext=(6.5, 3.0),
                arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=3))
    ax.text(8.5, 1.8, r'$\gcd = 1$', fontsize=13, ha='center', color=ACCENT1, fontweight='bold')
    ax.text(8.5, 1.2, 'Continue descent', fontsize=12, ha='center', color=ACCENT1, fontstyle='italic')
    ax.annotate('', xy=(8.5, 0.2), xytext=(8.5, 0.8),
                arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=2))

    ax.set_xlim(-0.5, 10.5)
    ax.set_ylim(-0.5, 8)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('GCD Decision at Each Node', fontsize=16, color=DARK, fontweight='bold')
    save(fig, 'fig06_gcd_node.png')


# ============================================================
# FIGURE 7: The Descent with Clocks
# ============================================================
def fig07_descent_clocks():
    fig, ax = plt.subplots(1, 1, figsize=(10, 13))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    n_levels = 10
    total_h = 12.0
    level_h = total_h / (n_levels + 1)

    for i in range(n_levels):
        y = total_h - (i + 1) * level_h
        node = plt.Circle((4, y), 0.35, color=ACCENT2, ec=DARK, linewidth=1.5,
                           alpha=0.6, zorder=5)
        ax.add_patch(node)
        ax.text(4, y, str(i + 1), fontsize=9, ha='center', va='center',
                color='white', fontweight='bold', zorder=6)

        if i < n_levels - 1:
            y_next = total_h - (i + 2) * level_h
            ax.plot([4, 4], [y - 0.35, y_next + 0.35], color=ACCENT1,
                    linewidth=2, zorder=3)

        cx, cy = 6.5, y
        clock = plt.Circle((cx, cy), 0.28, color=CREAM, ec=DARK, linewidth=1.2, zorder=5)
        ax.add_patch(clock)
        ax.plot([cx, cx], [cy, cy + 0.18], color=DARK, linewidth=1.5, zorder=6)
        ax.plot([cx, cx + 0.14], [cy, cy + 0.07], color=DARK, linewidth=1.5, zorder=6)
        ax.text(7.3, cy, r'$\log N$', fontsize=10, va='center', color=SLATE)

        ax.text(1.5, cy, f'{i + 1}' + r'$\times \log N$', fontsize=9, va='center',
                ha='center', color=DARK, alpha=0.7)

    ax.text(4, total_h + 0.3, r'$N$ (start)', fontsize=13, ha='center',
            color=DARK, fontweight='bold')
    ax.annotate('', xy=(4, total_h - 0.5), xytext=(4, total_h),
                arrowprops=dict(arrowstyle='->', color=DARK, lw=2))

    y_bot = total_h - (n_levels + 0.5) * level_h
    ax.text(4, y_bot, r'$\sqrt{N} \times \log N$ total', fontsize=14,
            ha='center', color=ACCENT1, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=GLOW, edgecolor=DARK, alpha=0.8))

    ax.text(0.3, total_h / 2, 'Running\nsum', fontsize=11, ha='center', va='center',
            color=DARK, fontweight='bold', rotation=90)
    ax.text(6.5, total_h + 0.3, 'Cost per node', fontsize=11, ha='center',
            color=DARK, fontweight='bold')

    ax.annotate('', xy=(9, total_h - level_h - 0.35),
                xytext=(9, total_h - n_levels * level_h + 0.35),
                arrowprops=dict(arrowstyle='<->', color=DARK, lw=1.5))
    ax.text(9.4, total_h / 2, r'Depth $= O(\sqrt{N})$', fontsize=11, color=DARK,
            rotation=90, va='center', ha='left', fontweight='bold')

    ax.text(4, total_h - 0.8 * level_h, 'Width = 1\n(deterministic)', fontsize=9,
            ha='center', va='top', color=SLATE, fontstyle='italic')

    ax.set_xlim(-0.5, 10.5)
    ax.set_ylim(y_bot - 1, total_h + 1)
    ax.axis('off')
    ax.set_title('The Descent with Clocks', fontsize=16, color=DARK, fontweight='bold')
    save(fig, 'fig07_descent_clocks.png')


# ============================================================
# FIGURE 8: The Multiplication Rectangle
# ============================================================
def fig08_multiplication_rect():
    fig, ax = plt.subplots(1, 1, figsize=(10, 7))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    rect_w, rect_h = 6, 8

    rect = patches.Rectangle((2, 1), rect_w, rect_h, linewidth=3, edgecolor=DARK,
                               facecolor=ACCENT2, alpha=0.2, zorder=2)
    ax.add_patch(rect)

    for i in range(rect_h * 3):
        y = 1 + i / 3.0
        if y < 1 + rect_h:
            ax.plot([2, 2 + rect_w], [y, y], color=ACCENT2, linewidth=0.3, alpha=0.3, zorder=3)

    ax.text(2 + rect_w / 2, 0.2, r'Cost per node: $O(\log N)$', fontsize=14,
            ha='center', color=DARK, fontweight='bold')
    ax.annotate('', xy=(2, 0.6), xytext=(2 + rect_w, 0.6),
                arrowprops=dict(arrowstyle='<->', color=DARK, lw=2))

    ax.text(0.5, 1 + rect_h / 2, r'Nodes: $O(\sqrt{N})$', fontsize=14,
            ha='center', va='center', color=DARK, fontweight='bold', rotation=90)
    ax.annotate('', xy=(1.3, 1), xytext=(1.3, 1 + rect_h),
                arrowprops=dict(arrowstyle='<->', color=DARK, lw=2))

    ax.text(2 + rect_w / 2, 1 + rect_h / 2,
            r'$O(\sqrt{N} \cdot \log N)$' + '\ntotal bit operations',
            fontsize=16, ha='center', va='center', color=DARK, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=GLOW, edgecolor=DARK, alpha=0.85))

    ax.set_xlim(-0.5, 10)
    ax.set_ylim(-0.5, 10.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Total Cost = Nodes x Cost per Node', fontsize=16, color=DARK, fontweight='bold')
    save(fig, 'fig08_multiplication_rect.png')


# ============================================================
# FIGURE 9: The Complexity Vise
# ============================================================
def fig09_complexity_vise():
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    jaw_upper = FancyBboxPatch((2, 5.5), 6, 1.5, boxstyle="round,pad=0.1",
                                facecolor=SLATE, edgecolor=DARK, linewidth=2, zorder=5)
    ax.add_patch(jaw_upper)
    ax.text(5, 6.25, r'Upper bound: $O(\sqrt{N})$', fontsize=15, ha='center',
            va='center', color='white', fontweight='bold', zorder=6)

    jaw_lower = FancyBboxPatch((2, 2.0), 6, 1.5, boxstyle="round,pad=0.1",
                                facecolor=SLATE, edgecolor=DARK, linewidth=2, zorder=5)
    ax.add_patch(jaw_lower)
    ax.text(5, 2.75, r'Lower bound: $\Omega(\sqrt{N})$', fontsize=15, ha='center',
            va='center', color='white', fontweight='bold', zorder=6)

    ax.annotate('', xy=(5, 5.5), xytext=(5, 6.0),
                arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=3))
    ax.annotate('', xy=(5, 3.5), xytext=(5, 3.0),
                arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=3))

    squeezed = FancyBboxPatch((3, 4.0), 4, 1.2, boxstyle="round,pad=0.2",
                               facecolor=GLOW, edgecolor=ACCENT1, linewidth=3, zorder=7)
    ax.add_patch(squeezed)
    ax.text(5, 4.6, r'$\Theta(\sqrt{N})$', fontsize=22, ha='center', va='center',
            color=DARK, fontweight='bold', zorder=8)

    # Vise screw decoration
    screw_x = 1.0
    ax.plot([screw_x, screw_x], [2.5, 6.5], color=DARK, linewidth=3, zorder=4)
    ax.plot([screw_x, 2], [6.5, 6.25], color=DARK, linewidth=2, zorder=4)
    ax.plot([screw_x, 2], [2.5, 2.75], color=DARK, linewidth=2, zorder=4)
    ax.plot([screw_x - 0.5, screw_x + 0.5], [7.0, 7.0], color=DARK, linewidth=3, zorder=4)
    ax.plot([screw_x], [7.0], 'o', color=DARK, markersize=8, zorder=5)

    ax.text(5, 1.2, '"The complexity is pinched."', fontsize=13, ha='center',
            color=SLATE, fontstyle='italic')

    ax.set_xlim(-0.5, 10)
    ax.set_ylim(0.5, 8)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('The Complexity Vise', fontsize=18, color=DARK, fontweight='bold')
    save(fig, 'fig09_complexity_vise.png')


# ============================================================
# FIGURE 10: The Three-Way Race
# ============================================================
def fig10_three_way_race():
    fig, ax = plt.subplots(1, 1, figsize=(13, 7))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    track_y = 3.0
    ax.plot([0.5, 12.5], [track_y, track_y], color=DARK, linewidth=4, zorder=2)
    ax.plot(0.5, track_y, '|', color=DARK, markersize=20, zorder=3)
    ax.plot(12.5, track_y, '|', color=DARK, markersize=20, zorder=3)
    ax.text(0.5, track_y - 0.7, '2', fontsize=13, ha='center', color=DARK, fontweight='bold')
    ax.text(12.5, track_y - 0.7, r'$\sqrt{N}$', fontsize=14, ha='center',
            color=DARK, fontweight='bold')

    p_x = 11.5
    ax.axvline(p_x, color=GOLD, linewidth=3, linestyle=':', zorder=2)
    ax.text(p_x, track_y + 2.5, r'$p$', fontsize=16, ha='center', color=GOLD, fontweight='bold')
    ax.text(p_x, track_y + 2.0, '(finish)', fontsize=10, ha='center', color=GOLD)

    # Runner A
    ax.plot(2.0, track_y + 0.5, 's', color=ACCENT2, markersize=18, zorder=6)
    ax.text(2.0, track_y + 1.2, 'A: Trial\nDivision', fontsize=10, ha='center',
            color=ACCENT2, fontweight='bold')
    ax.annotate('', xy=(p_x - 0.5, track_y + 0.5), xytext=(2.5, track_y + 0.5),
                arrowprops=dict(arrowstyle='->', color=ACCENT2, lw=2, linestyle='--'))

    # Runner B
    ax.plot(12.0, track_y, 'D', color=ACCENT4, markersize=18, zorder=6)
    ax.text(12.0, track_y + 1.2, 'B: Fermat', fontsize=10, ha='center',
            color=ACCENT4, fontweight='bold')
    ax.annotate('', xy=(p_x + 0.3, track_y), xytext=(12.3, track_y),
                arrowprops=dict(arrowstyle='->', color=ACCENT4, lw=2, linestyle='--'))

    # Runner C
    ax.plot(6.5, track_y + 3.5, '^', color=ACCENT1, markersize=18, zorder=6)
    ax.text(6.5, track_y + 4.2, 'C: Pythagorean\nTree', fontsize=10, ha='center',
            color=ACCENT1, fontweight='bold')
    ax.annotate('', xy=(p_x - 0.5, track_y + 0.3), xytext=(6.5, track_y + 3.2),
                arrowprops=dict(arrowstyle='->', color=ACCENT1, lw=2, linestyle='--'))

    # Scoreboard
    sb_x, sb_y = 6.5, -0.2
    sb = FancyBboxPatch((sb_x - 3.5, sb_y - 0.3), 7, 1.6,
                         boxstyle="round,pad=0.2",
                         facecolor=CREAM, edgecolor=DARK, linewidth=2, zorder=5)
    ax.add_patch(sb)
    ax.text(sb_x, sb_y + 1.0, 'SCOREBOARD', fontsize=12, ha='center',
            color=DARK, fontweight='bold', zorder=6)
    ax.text(sb_x, sb_y + 0.3,
            r'Balanced case ($p \approx q$):  THREE-WAY TIE  \u2014  all $\Theta(\sqrt{N})$',
            fontsize=11, ha='center', color=ACCENT1, fontweight='bold', zorder=6)

    ax.set_xlim(-0.5, 14)
    ax.set_ylim(-1.5, track_y + 5.5)
    ax.axis('off')
    ax.set_title('The Three-Way Factoring Race', fontsize=17, color=DARK, fontweight='bold')
    save(fig, 'fig10_three_way_race.png')


# ============================================================
# FIGURE 11: Method Comparison Table
# ============================================================
def fig11_comparison_table():
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)
    ax.axis('off')

    columns = ['Scenario', 'Trial Division', "Fermat's Method", 'Pythagorean Tree']
    rows = [
        ['$p$ small, $q$ large',
         '$O(p)$ \u2014 FAST',
         '$O(q - p)$ \u2014 slow',
         r'$O(\sqrt{N})$ \u2014 moderate'],
        [r'$p \approx q$ (balanced)',
         r'$O(\sqrt{N})$ \u2014 slow',
         '$O(q-p)$ \u2014 FAST',
         r'$O(\sqrt{N})$ \u2014 moderate'],
        ['General balanced\nsemiprime',
         r'$O(\sqrt{N})$',
         r'$O(\sqrt{N})$',
         r'$\Theta(\sqrt{N})$'],
    ]

    table = ax.table(cellText=rows, colLabels=columns, loc='center',
                     cellLoc='center', colColours=[LIGHT_BLUE] * 4)

    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.2)

    for j in range(4):
        cell = table[0, j]
        cell.set_text_props(fontweight='bold', color='white')
        cell.set_facecolor(SLATE)

    row_colors = [CREAM, LIGHT_RED, LIGHT_GREEN]
    for i in range(3):
        for j in range(4):
            table[i + 1, j].set_facecolor(row_colors[i])
            table[i + 1, j].set_edgecolor(DARK)
            table[i + 1, j].set_text_props(fontsize=10)

    for j in range(4):
        table[3, j].set_text_props(fontweight='bold')

    ax.set_title('Factoring Method Comparison', fontsize=16, color=DARK,
                 fontweight='bold', pad=20)
    save(fig, 'fig11_comparison_table.png')


# ============================================================
# FIGURE 12: The Dimensional Escape (2D vs 3D)
# ============================================================
def fig12_dimensional_escape():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
    fig.set_facecolor(SAND)

    # Left panel: 2D maze
    ax1.set_facecolor(CREAM)
    np.random.seed(17)
    n_walls = 8
    for i in range(n_walls):
        x = 1 + i * 1.0
        gap_y = np.random.uniform(1, 7)
        ax1.plot([x, x], [0, gap_y - 0.4], color=SLATE, linewidth=4, zorder=3)
        ax1.plot([x, x], [gap_y + 0.4, 8], color=SLATE, linewidth=4, zorder=3)

    sf_x, sf_y = 0.5, 4
    ax1.plot(sf_x, sf_y + 0.3, 'o', color=ACCENT1, markersize=10, zorder=5)
    ax1.plot([sf_x, sf_x], [sf_y - 0.3, sf_y + 0.15], color=ACCENT1, linewidth=2, zorder=5)
    ax1.plot([sf_x - 0.2, sf_x + 0.2], [sf_y, sf_y], color=ACCENT1, linewidth=2, zorder=5)
    ax1.plot([sf_x - 0.15, sf_x, sf_x + 0.15], [sf_y - 0.5, sf_y - 0.3, sf_y - 0.5],
             color=ACCENT1, linewidth=2, zorder=5)

    ax1.set_xlim(-0.5, 9.5)
    ax1.set_ylim(-0.5, 9)
    ax1.set_title(r'2D: $\Theta(\sqrt{N})$ steps', fontsize=14, color=DARK, fontweight='bold')
    ax1.text(4.5, -1.0, 'Trapped in the flat maze', fontsize=11, ha='center',
             color=SLATE, fontstyle='italic')
    ax1.axis('off')

    # Right panel: 3D escape
    ax2.set_facecolor(LIGHT_GREEN)
    for i in range(n_walls):
        x = 1 + i * 1.0
        ax2.plot([x, x], [0, 8], color=SLATE, linewidth=2, alpha=0.3, zorder=2)

    path_x = np.linspace(0.5, 9.0, 50)
    path_y = 4 + 2.5 * np.sin(np.linspace(0, np.pi, 50))
    ax2.plot(path_x, path_y, color=ACCENT3, linewidth=3, zorder=5)
    ax2.plot(path_x[::5], path_y[::5], 'o', color=ACCENT3, markersize=6, zorder=6)

    sf2_x, sf2_y = path_x[25], path_y[25]
    ax2.plot(sf2_x, sf2_y + 0.3, 'o', color=ACCENT3, markersize=10, zorder=7)
    ax2.plot([sf2_x, sf2_x], [sf2_y - 0.3, sf2_y + 0.15], color=ACCENT3,
             linewidth=2, zorder=7)

    ax2.set_xlim(-0.5, 9.5)
    ax2.set_ylim(-0.5, 9)
    ax2.set_title('3D+: sub-exponential steps', fontsize=14, color=DARK, fontweight='bold')
    ax2.text(4.5, -1.0, 'Stepping over walls in higher dimensions', fontsize=11,
             ha='center', color=SLATE, fontstyle='italic')
    ax2.axis('off')

    fig.text(0.5, 0.5, '==>', fontsize=30, ha='center', va='center', color=ACCENT1,
             fontweight='bold', transform=fig.transFigure)
    fig.text(0.5, 0.42, 'The Dimensional\nEscape', fontsize=12, ha='center',
             va='center', color=ACCENT1, fontweight='bold', transform=fig.transFigure)

    fig.suptitle('Breaking the Barrier: 2D vs. Higher Dimensions',
                 fontsize=16, color=DARK, fontweight='bold', y=0.98)
    save(fig, 'fig12_dimensional_escape.png')


# ============================================================
# FIGURE 13: Factoring Time Curves
# ============================================================
def fig13_factoring_curves():
    fig, ax = plt.subplots(1, 1, figsize=(11, 7))
    fig.set_facecolor(SAND)
    ax.set_facecolor(CREAM)

    n_digits = np.linspace(10, 200, 300)

    trial_div = 0.5 * n_digits
    c_nfs = 1.5
    nfs = c_nfs * n_digits**(1.0/3.0) * (np.log(n_digits + 1))**(2.0/3.0)
    poly = 2.5 * np.log(n_digits + 1)
    grover = 0.25 * n_digits

    ax.plot(n_digits, trial_div, color=ACCENT1, linewidth=3,
            label=r'Trial division / Tree: $\sqrt{N}$', zorder=4)
    ax.plot(n_digits, nfs, color=ACCENT2, linewidth=3,
            label='Quadratic Sieve / NFS: sub-exponential', zorder=4)
    ax.plot(n_digits, poly, color=ACCENT3, linewidth=3, linestyle='--',
            label='Polynomial? (hypothetical)', zorder=4)
    ax.plot(n_digits, grover, color=ACCENT5, linewidth=2.5, linestyle='-.',
            label=r"Grover's algorithm: $N^{1/4}$", zorder=4)

    ax.fill_between(n_digits, nfs, trial_div, alpha=0.1, color=ACCENT4, zorder=2)
    ax.text(120, 40, 'Where do quantum\ncomputers land?', fontsize=12,
            ha='center', color=ACCENT4, fontstyle='italic', fontweight='bold')

    ax.set_xlabel(r'$\log N$ (number of digits)', fontsize=13, color=DARK)
    ax.set_ylabel(r'$\log(\mathrm{factoring\ time})$', fontsize=13, color=DARK)
    ax.set_title('Factoring Time: Classical vs. Quantum vs. Sub-exponential',
                 fontsize=14, color=DARK, fontweight='bold')
    ax.legend(fontsize=10, loc='upper left', framealpha=0.9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    save(fig, 'fig13_factoring_curves.png')


# ============================================================
# FIGURE 14: Classical vs. Quantum Descent
# ============================================================
def fig14_quantum_descent():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 10),
                                    gridspec_kw={'wspace': 0.3})
    fig.set_facecolor(SAND)

    total_depth = 12

    # Left: Classical
    ax1.set_facecolor(SAND)
    ax1.set_xlim(-1, 5)
    ax1.set_ylim(-1, total_depth + 1)
    ax1.plot([2, 2], [0, total_depth], color=DARK, linewidth=1, linestyle=':', zorder=1)
    ax1.text(2, total_depth + 0.5, 'Depth 0', fontsize=10, ha='center', color=DARK)
    ax1.text(2, -0.7, r'Depth $\sqrt{N}$', fontsize=10, ha='center', color=DARK)

    for i in range(total_depth):
        y = total_depth - i - 0.5
        offset = 0.15 if i % 2 == 0 else -0.15
        ax1.plot(2 + offset, y, 'v', color=ACCENT2, markersize=10, zorder=5)
        ax1.text(3.5, y, f'step {i+1}', fontsize=8, va='center', color=SLATE, alpha=0.6)

    ax1.set_title(r'Classical: $O(\sqrt{N})$ steps', fontsize=14,
                  color=DARK, fontweight='bold')
    ax1.axis('off')

    # Right: Quantum
    ax2.set_facecolor(SAND)
    ax2.set_xlim(-1, 5)
    ax2.set_ylim(-1, total_depth + 1)
    ax2.plot([2, 2], [0, total_depth], color=DARK, linewidth=1, linestyle=':', zorder=1)
    ax2.text(2, total_depth + 0.5, 'Depth 0', fontsize=10, ha='center', color=DARK)
    ax2.text(2, -0.7, r'Depth $\sqrt{N}$', fontsize=10, ha='center', color=DARK)

    np.random.seed(7)
    n_ghosts = 40
    ghost_y = np.random.uniform(0.5, total_depth - 0.5, n_ghosts)
    ghost_x = 2 + np.random.normal(0, 0.3, n_ghosts)
    ax2.scatter(ghost_x, ghost_y, s=80, color=ACCENT4, alpha=0.15, zorder=3, marker='v')

    key_depths = np.linspace(total_depth, 1, int(np.sqrt(total_depth)) + 1)
    for d in key_depths:
        ax2.plot(2, d, 'v', color=ACCENT4, markersize=12, zorder=5, alpha=0.7)

    critical_y = 4.0
    ax2.plot(2, critical_y, '*', color=GLOW, markersize=20, zorder=7,
             markeredgecolor=DARK, markeredgewidth=1.5)
    ax2.text(3.2, critical_y, 'Factor found!', fontsize=11, va='center',
             color=ACCENT3, fontweight='bold')

    ell = patches.Ellipse((2, total_depth / 2), 1.5, total_depth - 1,
                           fill=False, edgecolor=ACCENT4, linewidth=2,
                           linestyle='--', alpha=0.4, zorder=2)
    ax2.add_patch(ell)
    ax2.text(3.8, total_depth / 2, 'Quantum\nsuperposition', fontsize=10,
             ha='center', va='center', color=ACCENT4, fontstyle='italic', alpha=0.7)

    ax2.set_title(r'Quantum (Grover): $O(N^{1/4})$ queries', fontsize=14,
                  color=DARK, fontweight='bold')
    ax2.axis('off')

    fig.suptitle('Classical vs. Quantum Descent',
                 fontsize=17, color=DARK, fontweight='bold', y=0.97)
    save(fig, 'fig14_quantum_descent.png')


# ============================================================
# FIGURE 15: Full-Page Tree Recapitulation
# ============================================================
def fig15_full_recap():
    fig, ax = plt.subplots(1, 1, figsize=(12, 16))
    fig.set_facecolor(SAND)
    ax.set_facecolor(SAND)

    # Trunk
    trunk_x = [5.5, 5.5, 6.5, 6.5]
    trunk_y = [0, 12, 12, 0]
    ax.fill(trunk_x, trunk_y, color='#8B6914', alpha=0.4, zorder=1)

    # Canopy
    for lv in range(10):
        y = 1 + lv * 1.1
        width = 0.4 + lv * 0.45
        cx = 6.0
        ell = patches.Ellipse((cx, y), width * 2, 0.8, color=ACCENT3,
                               alpha=0.1 + 0.04 * lv, zorder=2)
        ax.add_patch(ell)

    # Glowing orb N
    orb = plt.Circle((6.0, 13.0), 0.6, color=GLOW, ec=ACCENT5, linewidth=3,
                      zorder=8, alpha=0.9)
    ax.add_patch(orb)
    ax.text(6.0, 13.0, r'$N$', fontsize=20, ha='center', va='center',
            color=DARK, fontweight='bold', zorder=9)

    # Red descent path
    path_y = np.linspace(12.4, 0.5, 60)
    path_x = 6.0 + 0.5 * np.sin(path_y * 2)
    ax.plot(path_x, path_y, color=ACCENT1, linewidth=3.5, zorder=6, alpha=0.8)

    # sqrt(N) line
    sqN_y = 6.0
    ax.plot([1, 11], [sqN_y, sqN_y], color=DARK, linewidth=2, linestyle='--', zorder=4)
    ax.text(11.2, sqN_y, r'$\sqrt{N}$', fontsize=14, color=DARK, fontweight='bold')

    # Roots
    primes = [2, 3, 5, 7, 11, 13]
    for i, p in enumerate(primes):
        rx = 4.5 + i * 0.6
        ry = -0.5
        ax.plot([rx, 5.5 + (rx - 4.5) * 0.4], [ry, 0.5], color='#8B6914',
                linewidth=1.5, alpha=0.5)
        ax.text(rx, ry - 0.4, str(p), fontsize=10, ha='center', color=DARK, fontweight='bold')

    # Left: 2D prison
    prison_x, prison_y = 1.5, 5.0
    prison = patches.Rectangle((prison_x - 1.2, prison_y - 1.5), 2.4, 3,
                                 linewidth=2.5, edgecolor=DARK,
                                 facecolor=LIGHT_RED, alpha=0.5, zorder=3)
    ax.add_patch(prison)
    for bx in np.linspace(prison_x - 1.0, prison_x + 1.0, 6):
        ax.plot([bx, bx], [prison_y - 1.5, prison_y + 1.5], color=DARK,
                linewidth=1.5, zorder=4)
    ax.text(prison_x, prison_y + 2.0, 'The Hyperbolic\nPlane', fontsize=10,
            ha='center', color=DARK, fontweight='bold')
    ax.text(prison_x, prison_y - 2.2, '(2D prison)', fontsize=9, ha='center',
            color=SLATE, fontstyle='italic')

    # Right: 3D lattice
    lat_x, lat_y = 10.5, 5.0
    for ix in range(4):
        for iy in range(4):
            lx = lat_x - 1.0 + ix * 0.6 + iy * 0.15
            ly = lat_y - 1.0 + iy * 0.6 + ix * 0.1
            ax.plot(lx, ly, 'o', color=ACCENT2, markersize=5, zorder=5, alpha=0.6)
            if ix < 3:
                lx2 = lat_x - 1.0 + (ix+1) * 0.6 + iy * 0.15
                ly2 = lat_y - 1.0 + iy * 0.6 + (ix+1) * 0.1
                ax.plot([lx, lx2], [ly, ly2], color=ACCENT2, linewidth=0.8, alpha=0.4)
            if iy < 3:
                lx2 = lat_x - 1.0 + ix * 0.6 + (iy+1) * 0.15
                ly2 = lat_y - 1.0 + (iy+1) * 0.6 + ix * 0.1
                ax.plot([lx, lx2], [ly, ly2], color=ACCENT2, linewidth=0.8, alpha=0.4)

    ax.text(lat_x, lat_y + 2.0, 'Higher Dimensions:\nThe Way Out', fontsize=10,
            ha='center', color=ACCENT2, fontweight='bold')

    # Bottom: stone with Theta(sqrt(N))
    stone = FancyBboxPatch((3.5, -2.8), 5, 1.5,
                            boxstyle="round,pad=0.3",
                            facecolor='#D5C4A1', edgecolor=DARK,
                            linewidth=2.5, zorder=5)
    ax.add_patch(stone)
    ax.text(6.0, -2.05, r'$\Theta(\sqrt{N})$', fontsize=22, ha='center', va='center',
            color=DARK, fontweight='bold', zorder=6)

    # Pondering figure
    fig_x, fig_y = 6.0, -3.8
    ax.plot(fig_x, fig_y + 0.3, 'o', color=ACCENT5, markersize=10, zorder=7)
    ax.plot([fig_x, fig_x], [fig_y - 0.4, fig_y + 0.15], color=DARK, linewidth=2, zorder=7)
    ax.plot([fig_x - 0.2, fig_x + 0.2], [fig_y, fig_y], color=DARK, linewidth=2, zorder=7)
    ax.plot([fig_x - 0.15, fig_x, fig_x + 0.15], [fig_y - 0.7, fig_y - 0.4, fig_y - 0.7],
             color=DARK, linewidth=2, zorder=7)

    ax.set_xlim(-1, 13)
    ax.set_ylim(-5, 14.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('The Price of Descent \u2014 Chapter Recapitulation',
                 fontsize=18, color=DARK, fontweight='bold', pad=15)
    save(fig, 'fig15_full_recap.png')


# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    print("Generating Chapter 8 illustrations...")
    fig01_locksmith_tree()
    fig02_euclid_staircase()
    fig03_step_count_plot()
    fig04_danger_zone()
    fig05_nearly_square()
    fig06_gcd_node()
    fig07_descent_clocks()
    fig08_multiplication_rect()
    fig09_complexity_vise()
    fig10_three_way_race()
    fig11_comparison_table()
    fig12_dimensional_escape()
    fig13_factoring_curves()
    fig14_quantum_descent()
    fig15_full_recap()
    print("Done! All Chapter 8 images saved to images/")

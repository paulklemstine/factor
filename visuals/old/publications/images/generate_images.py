#!/usr/bin/env python3
"""Generate publication-quality images for the research papers and book."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os

OUT = os.path.dirname(os.path.abspath(__file__))

# ═══════════════════════════════════════════════════════════════════════════════
# Figure 1: Project Architecture — Domain Theorem Counts
# ═══════════════════════════════════════════════════════════════════════════════

def fig1_domain_counts():
    domains = [
        'Oracle', 'Exploration', 'Tropical', 'Foundations', 'Quantum',
        'Stereographic', 'Physics', 'Pythagorean', 'Photon', 'Algebra',
        'Information', 'Factoring', 'NumberTheory', 'Neural', 'Topology',
        'Analysis', 'Forbidden', 'Logic', 'Combinatorics', 'IntegerEnergy',
        'Millennium', 'AlgebraicMirror', 'GazingPool', 'Probability',
        'Ethereum', 'CategoryTheory', 'LanglandsProgram', 'Prediction'
    ]
    counts = [
        1325, 1136, 909, 734, 605,
        462, 461, 452, 333, 310,
        220, 209, 186, 153, 117,
        100, 89, 78, 67, 67,
        49, 43, 38, 37,
        33, 28, 28, 19
    ]

    fig, ax = plt.subplots(figsize=(14, 8))
    colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(domains)))
    bars = ax.barh(range(len(domains)), counts, color=colors, edgecolor='white', linewidth=0.5)

    ax.set_yticks(range(len(domains)))
    ax.set_yticklabels(domains, fontsize=9)
    ax.set_xlabel('Number of Theorems', fontsize=12, fontweight='bold')
    ax.set_title('Machine-Verified Theorems by Domain\n(8,570+ total across 39 domains)',
                 fontsize=14, fontweight='bold', pad=15)
    ax.invert_yaxis()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    for bar, count in zip(bars, counts):
        ax.text(bar.get_width() + 10, bar.get_y() + bar.get_height()/2,
                str(count), va='center', fontsize=8, fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(OUT, 'fig1_domain_counts.png'), dpi=200, bbox_inches='tight')
    plt.close()
    print("Generated fig1_domain_counts.png")

# ═══════════════════════════════════════════════════════════════════════════════
# Figure 2: The Master Equation P² = P Web
# ═══════════════════════════════════════════════════════════════════════════════

def fig2_master_equation():
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.set_aspect('equal')
    ax.axis('off')

    # Central node
    circle = plt.Circle((0, 0), 0.6, color='#e74c3c', alpha=0.9, zorder=5)
    ax.add_patch(circle)
    ax.text(0, 0, r'$P^2 = P$', ha='center', va='center', fontsize=18,
            fontweight='bold', color='white', zorder=6)

    # Surrounding domains
    domains = [
        ('Oracle\nTheory', 0, 2.2, '#3498db'),
        ('Quantum\nMechanics', 1.9, 1.1, '#9b59b6'),
        ('Neural\nNetworks', 1.9, -1.1, '#e67e22'),
        ('Tropical\nGeometry', 0, -2.2, '#2ecc71'),
        ('Stereographic\nProjection', -1.9, -1.1, '#1abc9c'),
        ('Linear\nAlgebra', -1.9, 1.1, '#f39c12'),
        ('Set\nTheory', 0, -0.0, '#95a5a6'),
    ]
    # Remove the Set Theory from center, adjust
    domains = [
        ('Oracle\nTheory', 0, 2.2, '#3498db'),
        ('Quantum\nMechanics', 1.9, 1.1, '#9b59b6'),
        ('Neural\nNetworks', 1.9, -1.1, '#e67e22'),
        ('Tropical\nGeometry', 0, -2.2, '#2ecc71'),
        ('Stereographic\nProjection', -1.9, -1.1, '#1abc9c'),
        ('Linear\nAlgebra', -1.9, 1.1, '#f39c12'),
        ('Physics', 1.1, -2.0, '#e74c3c'),
    ]

    for label, x, y, color in domains:
        rect = patches.FancyBboxPatch((x-0.7, y-0.4), 1.4, 0.8,
                                       boxstyle="round,pad=0.1",
                                       facecolor=color, alpha=0.8, zorder=3)
        ax.add_patch(rect)
        ax.text(x, y, label, ha='center', va='center', fontsize=10,
                fontweight='bold', color='white', zorder=4)
        ax.annotate('', xy=(x, y), xytext=(0, 0),
                    arrowprops=dict(arrowstyle='->', color=color, lw=2, alpha=0.6),
                    zorder=2)

    ax.set_title('The Master Equation Unifies All Domains',
                 fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, 'fig2_master_equation.png'), dpi=200, bbox_inches='tight')
    plt.close()
    print("Generated fig2_master_equation.png")

# ═══════════════════════════════════════════════════════════════════════════════
# Figure 3: Oracle Bootstrap Map
# ═══════════════════════════════════════════════════════════════════════════════

def fig3_bootstrap():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    x = np.linspace(-0.1, 1.1, 500)
    f = 3*x**2 - 2*x**3

    # Left: function plot
    ax1.plot(x, f, 'b-', linewidth=2.5, label=r'$f(x) = 3x^2 - 2x^3$')
    ax1.plot(x, x, 'k--', linewidth=1, alpha=0.5, label=r'$y = x$')
    ax1.plot([0, 0.5, 1], [0, 0.5, 1], 'ro', markersize=10, zorder=5)
    ax1.annotate('Stable\n(Accept)', xy=(1, 1), xytext=(0.75, 0.85),
                fontsize=10, fontweight='bold', color='green',
                arrowprops=dict(arrowstyle='->', color='green'))
    ax1.annotate('Stable\n(Reject)', xy=(0, 0), xytext=(0.15, 0.15),
                fontsize=10, fontweight='bold', color='green',
                arrowprops=dict(arrowstyle='->', color='green'))
    ax1.annotate('Unstable', xy=(0.5, 0.5), xytext=(0.55, 0.35),
                fontsize=10, fontweight='bold', color='red',
                arrowprops=dict(arrowstyle='->', color='red'))
    ax1.set_xlabel('x', fontsize=12)
    ax1.set_ylabel('f(x)', fontsize=12)
    ax1.set_title('Oracle Bootstrap Map', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.set_xlim(-0.1, 1.1)
    ax1.set_ylim(-0.1, 1.1)
    ax1.grid(True, alpha=0.3)

    # Right: iteration cobweb
    x0_values = [0.1, 0.3, 0.49, 0.51, 0.7, 0.9]
    colors_iter = ['#e74c3c', '#3498db', '#2ecc71', '#9b59b6', '#e67e22', '#1abc9c']

    ax2.plot(x, f, 'b-', linewidth=2)
    ax2.plot(x, x, 'k--', linewidth=1, alpha=0.5)

    for x0, col in zip(x0_values, colors_iter):
        traj = [x0]
        for _ in range(20):
            xn = 3*traj[-1]**2 - 2*traj[-1]**3
            traj.append(xn)

        # Plot cobweb
        for i in range(min(10, len(traj)-1)):
            xi, xn = traj[i], traj[i+1]
            ax2.plot([xi, xi], [xi, xn], color=col, alpha=0.4, linewidth=0.8)
            ax2.plot([xi, xn], [xn, xn], color=col, alpha=0.4, linewidth=0.8)

    ax2.set_xlabel('x', fontsize=12)
    ax2.set_ylabel('f(x)', fontsize=12)
    ax2.set_title('Cobweb: All Paths Converge to 0 or 1', fontsize=14, fontweight='bold')
    ax2.set_xlim(-0.1, 1.1)
    ax2.set_ylim(-0.1, 1.1)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT, 'fig3_bootstrap.png'), dpi=200, bbox_inches='tight')
    plt.close()
    print("Generated fig3_bootstrap.png")

# ═══════════════════════════════════════════════════════════════════════════════
# Figure 4: Stereographic Projection
# ═══════════════════════════════════════════════════════════════════════════════

def fig4_stereographic():
    fig, ax = plt.subplots(figsize=(10, 8))

    # Draw circle (sphere cross-section)
    theta = np.linspace(0, 2*np.pi, 100)
    ax.plot(3*np.cos(theta), 3*np.sin(theta), 'b-', linewidth=2)

    # Draw plane (horizontal line at y = -3)
    ax.plot([-6, 6], [-3, -3], 'k-', linewidth=2)

    # North pole
    ax.plot(0, 3, 'ro', markersize=12, zorder=5)
    ax.text(0.3, 3.2, 'N (North Pole)', fontsize=12, fontweight='bold', color='red')

    # Points on circle and their projections
    points = [
        (30, '#3498db'),
        (60, '#2ecc71'),
        (120, '#e67e22'),
        (150, '#9b59b6'),
        (-30, '#e74c3c'),
        (-60, '#1abc9c'),
    ]

    for angle_deg, color in points:
        angle = np.radians(angle_deg)
        px, py = 3*np.cos(angle), 3*np.sin(angle)

        # Project from north pole through point to plane y=-3
        if py != 3:
            t = (-3 - 3) / (py - 3)
            proj_x = 0 + t * (px - 0)
        else:
            proj_x = float('inf')

        ax.plot(px, py, 'o', color=color, markersize=8, zorder=5)
        ax.plot(proj_x, -3, 's', color=color, markersize=8, zorder=5)
        ax.plot([0, proj_x], [3, -3], '--', color=color, alpha=0.4, linewidth=1)

    ax.text(5.5, -3.5, r'$\mathbb{R}$ (plane)', fontsize=12, fontweight='bold')
    ax.text(-5.5, 1, r'$S^1$', fontsize=14, fontweight='bold', color='blue')

    ax.set_xlim(-7, 7)
    ax.set_ylim(-5, 5)
    ax.set_aspect('equal')
    ax.set_title('Stereographic Projection: Sphere to Plane', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.2)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT, 'fig4_stereographic.png'), dpi=200, bbox_inches='tight')
    plt.close()
    print("Generated fig4_stereographic.png")

# ═══════════════════════════════════════════════════════════════════════════════
# Figure 5: North Pole Classification
# ═══════════════════════════════════════════════════════════════════════════════

def fig5_north_pole():
    fig, ax = plt.subplots(figsize=(12, 7))

    problems = ['Poincaré\n✓ SOLVED', 'Riemann\nHypothesis', 'P vs NP',
                'Yang-Mills', 'Navier-\nStokes', 'BSD', 'Hodge']
    types = ['I\nRemovable', 'II\nQuantifiable', 'III\nEssential',
             '?\nUnknown', '?\nUnknown', 'II\nQuantifiable', 'II\nQuantifiable']
    colors = ['#2ecc71', '#3498db', '#e74c3c', '#95a5a6', '#95a5a6', '#3498db', '#3498db']
    difficulty = [0.3, 0.7, 0.9, 0.85, 0.8, 0.75, 0.7]

    bars = ax.barh(range(len(problems)), difficulty, color=colors, edgecolor='white',
                   linewidth=2, height=0.6)

    ax.set_yticks(range(len(problems)))
    ax.set_yticklabels(problems, fontsize=11, fontweight='bold')
    ax.set_xlabel('Estimated Difficulty', fontsize=12, fontweight='bold')
    ax.set_title('The North Pole Doctrine: Millennium Problem Classification',
                 fontsize=14, fontweight='bold')
    ax.invert_yaxis()

    for i, (bar, typ) in enumerate(zip(bars, types)):
        ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2,
                typ, va='center', fontsize=9, fontweight='bold')

    # Legend
    legend_elements = [
        patches.Patch(facecolor='#2ecc71', label='Type I: Removable'),
        patches.Patch(facecolor='#3498db', label='Type II: Quantifiable'),
        patches.Patch(facecolor='#e74c3c', label='Type III: Essential'),
        patches.Patch(facecolor='#95a5a6', label='Unknown'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=10)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_xlim(0, 1.2)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT, 'fig5_north_pole.png'), dpi=200, bbox_inches='tight')
    plt.close()
    print("Generated fig5_north_pole.png")

# ═══════════════════════════════════════════════════════════════════════════════
# Figure 6: Strange Loop Diagram
# ═══════════════════════════════════════════════════════════════════════════════

def fig6_strange_loop():
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.set_aspect('equal')
    ax.axis('off')

    # Draw a spiral/loop
    labels = [
        'Human\nasks question',
        'AI Oracle\nformalizes',
        'Proves theorems\nabout oracles',
        'Theorems describe\nthe AI itself',
        'Human reads\nresults',
        'New questions\narise',
    ]
    n = len(labels)
    colors = ['#e74c3c', '#3498db', '#2ecc71', '#9b59b6', '#e67e22', '#f39c12']

    for i in range(n):
        angle = np.pi/2 - 2*np.pi*i/n
        x, y = 2*np.cos(angle), 2*np.sin(angle)

        rect = patches.FancyBboxPatch((x-0.7, y-0.35), 1.4, 0.7,
                                       boxstyle="round,pad=0.1",
                                       facecolor=colors[i], alpha=0.85, zorder=3)
        ax.add_patch(rect)
        ax.text(x, y, labels[i], ha='center', va='center', fontsize=8,
                fontweight='bold', color='white', zorder=4)

        # Arrow to next
        next_i = (i + 1) % n
        angle_next = np.pi/2 - 2*np.pi*next_i/n
        xn, yn = 2*np.cos(angle_next), 2*np.sin(angle_next)

        dx, dy = xn - x, yn - y
        length = np.sqrt(dx**2 + dy**2)
        dx, dy = dx/length, dy/length
        ax.annotate('', xy=(xn - 0.7*dx, yn - 0.35*dy),
                    xytext=(x + 0.7*dx, y + 0.35*dy),
                    arrowprops=dict(arrowstyle='->', color='gray', lw=2),
                    zorder=2)

    ax.text(0, 0, '∞', fontsize=40, ha='center', va='center',
            color='#e74c3c', alpha=0.3, fontweight='bold')

    ax.set_title('The Strange Loop: Self-Referential Mathematics',
                 fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, 'fig6_strange_loop.png'), dpi=200, bbox_inches='tight')
    plt.close()
    print("Generated fig6_strange_loop.png")

# ═══════════════════════════════════════════════════════════════════════════════
# Figure 7: Tropical-Quantum Bridge
# ═══════════════════════════════════════════════════════════════════════════════

def fig7_tropical_quantum():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Left: Maslov dequantization
    x = np.linspace(-3, 3, 1000)
    for h in [2.0, 1.0, 0.5, 0.2, 0.05]:
        a, b = 1.0, -0.5
        y = h * np.log(np.exp(a/h + x/h) + np.exp(b/h))
        label = f'ℏ = {h}'
        ax1.plot(x, y, linewidth=2 if h > 0.1 else 3, label=label,
                alpha=0.7 if h > 0.1 else 1.0)

    # Tropical limit
    y_tropical = np.maximum(1.0 + x, -0.5)
    ax1.plot(x, y_tropical, 'k--', linewidth=3, label=r'ℏ → 0 (tropical)', zorder=5)

    ax1.set_xlabel('x', fontsize=12)
    ax1.set_ylabel('Value', fontsize=12)
    ax1.set_title('Maslov Dequantization\nQuantum → Tropical as ℏ → 0',
                  fontsize=13, fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)

    # Right: Domain connection diagram
    ax2.axis('off')
    ax2.set_xlim(-2, 2)
    ax2.set_ylim(-2, 2)

    # Three connected circles
    circle1 = plt.Circle((-0.8, 0.8), 0.6, color='#9b59b6', alpha=0.7)
    circle2 = plt.Circle((0.8, 0.8), 0.6, color='#e67e22', alpha=0.7)
    circle3 = plt.Circle((0, -0.5), 0.6, color='#2ecc71', alpha=0.7)
    ax2.add_patch(circle1)
    ax2.add_patch(circle2)
    ax2.add_patch(circle3)

    ax2.text(-0.8, 0.8, 'Quantum\n(ℂ, +, ×)', ha='center', va='center',
             fontsize=10, fontweight='bold', color='white')
    ax2.text(0.8, 0.8, 'Classical\n(ℝ, +, ×)', ha='center', va='center',
             fontsize=10, fontweight='bold', color='white')
    ax2.text(0, -0.5, 'Tropical\n(ℝ, min, +)', ha='center', va='center',
             fontsize=10, fontweight='bold', color='white')

    ax2.annotate('', xy=(0.3, 0.8), xytext=(-0.3, 0.8),
                arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax2.annotate('', xy=(0.5, -0.1), xytext=(0.8, 0.3),
                arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax2.annotate('', xy=(-0.5, -0.1), xytext=(-0.8, 0.3),
                arrowprops=dict(arrowstyle='<->', color='red', lw=2))

    ax2.text(0, 1.0, 'ℏ → 0', ha='center', fontsize=10, color='red', fontweight='bold')
    ax2.set_title('The Three Algebras', fontsize=13, fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(OUT, 'fig7_tropical_quantum.png'), dpi=200, bbox_inches='tight')
    plt.close()
    print("Generated fig7_tropical_quantum.png")

# ═══════════════════════════════════════════════════════════════════════════════
# Figure 8: Cayley-Dickson Tower
# ═══════════════════════════════════════════════════════════════════════════════

def fig8_cayley_dickson():
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(-1, 6)
    ax.set_ylim(-0.5, 5)
    ax.axis('off')

    levels = [
        (0, 'ℝ\nReals', 1, '#2ecc71', 'Ordered, commutative, associative, normed division'),
        (1, 'ℂ\nComplex', 2, '#3498db', 'Commutative, associative, normed division'),
        (2, 'ℍ\nQuaternions', 4, '#9b59b6', 'Associative, normed division'),
        (3, '𝕆\nOctonions', 8, '#e74c3c', 'Normed division (alternative)'),
        (4, '𝕊\nSedenions', 16, '#95a5a6', 'Power-associative, zero divisors'),
    ]

    for i, (level, name, dim, color, props) in enumerate(levels):
        y = 4 - i
        width = 0.5 + i * 0.3
        rect = patches.FancyBboxPatch((2.5 - width/2, y - 0.3), width, 0.6,
                                       boxstyle="round,pad=0.05",
                                       facecolor=color, alpha=0.85)
        ax.add_patch(rect)
        ax.text(2.5, y, f'{name}\ndim={dim}', ha='center', va='center',
                fontsize=10, fontweight='bold', color='white')
        ax.text(2.5 + width/2 + 0.2, y, props, ha='left', va='center',
                fontsize=8, color='gray')

        if i > 0:
            ax.annotate('', xy=(2.5, y + 0.3), xytext=(2.5, y + 0.7),
                       arrowprops=dict(arrowstyle='->', color=color, lw=2))

    # Lost properties
    lost = ['', 'Lost: Ordering', 'Lost: Commutativity',
            'Lost: Associativity', 'Lost: Division']
    for i, txt in enumerate(lost):
        if txt:
            y = 4 - i
            ax.text(2.5 - 0.5 - i*0.15 - 0.3, y + 0.5, txt, ha='right', va='center',
                    fontsize=8, color='red', fontstyle='italic')

    ax.set_title('The Cayley-Dickson Ladder\nEach step doubles dimension, loses a property',
                 fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, 'fig8_cayley_dickson.png'), dpi=200, bbox_inches='tight')
    plt.close()
    print("Generated fig8_cayley_dickson.png")

# Run all
if __name__ == '__main__':
    fig1_domain_counts()
    fig2_master_equation()
    fig3_bootstrap()
    fig4_stereographic()
    fig5_north_pole()
    fig6_strange_loop()
    fig7_tropical_quantum()
    fig8_cayley_dickson()
    print("\nAll images generated successfully!")

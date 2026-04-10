"""
Tropical Algebra Visualization Demo

Generates visualizations of:
1. Tropical polynomial curves (piecewise linear)
2. ReLU network linear regions
3. LogSumExp temperature convergence
4. Tropical convexity

Requires: numpy, matplotlib
Run: python demo_tropical_visualization.py
"""

import numpy as np

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    HAS_MPL = True
except ImportError:
    HAS_MPL = False
    print("matplotlib not available; generating text-based visualizations")


def tropical_polynomial(coeffs, x):
    """Evaluate tropical polynomial: max_i(a_i + i*x)"""
    terms = [a + i * x for i, a in enumerate(coeffs)]
    return max(terms)


def relu(x):
    return max(x, 0.0)


def logsumexp_temp(beta, values):
    c = max(values)
    return c + np.log(sum(np.exp(beta * (v - c)) for v in values)) / beta


def plot_tropical_polynomial():
    """Plot a tropical polynomial showing piecewise linearity"""
    coeffs = [2, -1, 0.5, -2]  # Tropical polynomial of degree 3
    xs = np.linspace(-5, 5, 1000)
    ys = [tropical_polynomial(coeffs, x) for x in xs]

    if HAS_MPL:
        fig, ax = plt.subplots(1, 1, figsize=(10, 6))
        ax.plot(xs, ys, 'b-', linewidth=2, label='Tropical poly: max(2, -1+x, 0.5+2x, -2+3x)')

        # Plot individual terms
        colors = ['r', 'g', 'orange', 'purple']
        for i, a in enumerate(coeffs):
            term_ys = [a + i * x for x in xs]
            ax.plot(xs, term_ys, '--', color=colors[i], alpha=0.5,
                    label=f'Term {i}: {a} + {i}x')

        ax.set_xlabel('x', fontsize=12)
        ax.set_ylabel('Tropical value', fontsize=12)
        ax.set_title('Tropical Polynomial = Max of Affine Functions', fontsize=14)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_ylim(-10, 15)
        fig.savefig('/workspace/request-project/Tropical/NewResearch/tropical_polynomial.png',
                    dpi=150, bbox_inches='tight')
        plt.close()
        print("Saved: tropical_polynomial.png")
    else:
        print("\nTropical Polynomial (text):")
        for x in range(-5, 6):
            y = tropical_polynomial(coeffs, x)
            bar = '#' * max(0, int(y + 10))
            print(f"  x={x:3d}: {bar} ({y:.1f})")


def plot_relu_regions():
    """Plot ReLU network linear regions"""
    # 3 neurons with different weights and biases
    neurons = [
        (1.0, -1.0),   # w=1, b=-1: breakpoint at x=1
        (-2.0, 3.0),   # w=-2, b=3: breakpoint at x=1.5
        (0.5, -0.5),   # w=0.5, b=-0.5: breakpoint at x=1
    ]

    xs = np.linspace(-3, 5, 1000)

    def network_output(x):
        hidden = [relu(w * x + b) for w, b in neurons]
        return sum(hidden)

    ys = [network_output(x) for x in xs]

    if HAS_MPL:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

        # Individual neuron activations
        for i, (w, b) in enumerate(neurons):
            neuron_ys = [relu(w * x + b) for x in xs]
            ax1.plot(xs, neuron_ys, linewidth=2,
                     label=f'Neuron {i}: ReLU({w}x + {b})')
            # Mark breakpoint
            bp = -b / w if abs(w) > 1e-10 else None
            if bp is not None and -3 <= bp <= 5:
                ax1.axvline(x=bp, color='gray', linestyle=':', alpha=0.5)

        ax1.set_ylabel('Activation', fontsize=12)
        ax1.set_title('Individual ReLU Neuron Activations', fontsize=14)
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)

        # Network output with linear region highlighting
        ax2.plot(xs, ys, 'b-', linewidth=2, label='Network output')

        # Find and highlight linear regions
        breakpoints = sorted([-b / w for w, b in neurons if abs(w) > 1e-10])
        breakpoints = [bp for bp in breakpoints if -3 <= bp <= 5]
        regions = [-3] + breakpoints + [5]
        colors_bg = ['#FFE0E0', '#E0FFE0', '#E0E0FF', '#FFFFE0', '#FFE0FF']
        for i in range(len(regions) - 1):
            ax2.axvspan(regions[i], regions[i+1], alpha=0.3,
                       color=colors_bg[i % len(colors_bg)])

        for bp in breakpoints:
            ax2.axvline(x=bp, color='red', linestyle='--', alpha=0.7)

        ax2.set_xlabel('x', fontsize=12)
        ax2.set_ylabel('Output', fontsize=12)
        ax2.set_title(f'ReLU Network Output ({len(breakpoints)+1} Linear Regions)', fontsize=14)
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        fig.savefig('/workspace/request-project/Tropical/NewResearch/relu_regions.png',
                    dpi=150, bbox_inches='tight')
        plt.close()
        print("Saved: relu_regions.png")
    else:
        print("\nReLU Network Linear Regions (text):")
        for x_int in range(-3, 6):
            y = network_output(float(x_int))
            bar = '#' * max(0, int(y * 2))
            print(f"  x={x_int:3d}: {bar} ({y:.2f})")


def plot_logsumexp_convergence():
    """Plot LogSumExp convergence to max as temperature → ∞"""
    values = [3.0, 7.0, 5.0, 1.0]
    true_max = max(values)

    betas = np.logspace(-1, 2, 100)
    lse_values = [logsumexp_temp(beta, values) for beta in betas]

    if HAS_MPL:
        fig, ax = plt.subplots(1, 1, figsize=(10, 6))
        ax.semilogx(betas, lse_values, 'b-', linewidth=2, label='LSE_β(v)')
        ax.axhline(y=true_max, color='r', linestyle='--', linewidth=1.5,
                   label=f'max(v) = {true_max}')
        ax.axhline(y=true_max + np.log(len(values)), color='g', linestyle='--',
                   linewidth=1.5, label=f'max(v) + log(n) = {true_max + np.log(len(values)):.2f}')

        ax.fill_between(betas, true_max, [true_max + np.log(len(values))] * len(betas),
                        alpha=0.1, color='green')

        ax.set_xlabel('Temperature β', fontsize=12)
        ax.set_ylabel('LSE_β(v)', fontsize=12)
        ax.set_title('LogSumExp Converges to Max (Maslov Dequantization)', fontsize=14)
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)

        fig.savefig('/workspace/request-project/Tropical/NewResearch/logsumexp_convergence.png',
                    dpi=150, bbox_inches='tight')
        plt.close()
        print("Saved: logsumexp_convergence.png")
    else:
        print("\nLogSumExp Convergence (text):")
        for beta in [0.1, 0.5, 1, 2, 5, 10, 50, 100]:
            lse = logsumexp_temp(beta, values)
            print(f"  β={beta:6.1f}: LSE_β = {lse:.4f} (max = {true_max})")


def plot_tropical_convexity():
    """Plot tropical convex set (halfspace intersection)"""
    if HAS_MPL:
        fig, ax = plt.subplots(1, 1, figsize=(8, 8))

        # 2D tropical halfspaces: {(x,y) | x ≥ c1}, {(x,y) | y ≥ c2}
        c1, c2 = -1, 0.5

        # Fill the tropical polyhedron
        ax.fill([c1, 5, 5, c1], [c2, c2, 5, 5], alpha=0.3, color='blue',
                label=f'Tropical polyhedron: x ≥ {c1}, y ≥ {c2}')
        ax.axvline(x=c1, color='blue', linewidth=2)
        ax.axhline(y=c2, color='blue', linewidth=2)

        # Show tropical convex combination
        p1 = np.array([1, 3])
        p2 = np.array([3, 1])
        ax.plot(*p1, 'ro', markersize=10, label=f'p₁ = {tuple(p1)}')
        ax.plot(*p2, 'go', markersize=10, label=f'p₂ = {tuple(p2)}')

        # Tropical convex hull: max(c + p1, d + p2) for all c, d
        # This traces out a path from p1 to max(p1,p2) to p2
        ts = np.linspace(0, 1, 100)
        hull_x = [max(p1[0] + t, p2[0] + (1-t)) for t in np.linspace(-5, 5, 200)]
        hull_y = [max(p1[1] + t, p2[1] + (1-t)) for t in np.linspace(-5, 5, 200)]

        # Simple tropical segment
        segment_x = [max(p1[0] - t, p2[0] + t - 2) for t in np.linspace(0, 2, 100)]
        segment_y = [max(p1[1] - t, p2[1] + t - 2) for t in np.linspace(0, 2, 100)]

        corner = np.maximum(p1, p2)
        ax.plot([p1[0], corner[0], p2[0]], [p1[1], corner[1], p2[1]],
                'm-', linewidth=2, label='Tropical segment')
        ax.plot(*corner, 'ms', markersize=8)

        ax.set_xlabel('x', fontsize=12)
        ax.set_ylabel('y', fontsize=12)
        ax.set_title('Tropical Convexity', fontsize=14)
        ax.legend(fontsize=10, loc='upper left')
        ax.set_xlim(-2, 5)
        ax.set_ylim(-1, 5)
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')

        fig.savefig('/workspace/request-project/Tropical/NewResearch/tropical_convexity.png',
                    dpi=150, bbox_inches='tight')
        plt.close()
        print("Saved: tropical_convexity.png")
    else:
        print("\nTropical Convexity: See SVG files for visualization")


if __name__ == "__main__":
    print("Generating Tropical Algebra Visualizations...")
    print()
    plot_tropical_polynomial()
    plot_relu_regions()
    plot_logsumexp_convergence()
    plot_tropical_convexity()
    print("\nAll visualizations generated!")

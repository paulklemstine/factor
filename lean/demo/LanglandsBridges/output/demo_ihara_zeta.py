#!/usr/bin/env python3
"""
Demo: Ihara Zeta Function and Ramanujan Graphs

Computes and visualizes the Ihara zeta function for regular graphs,
demonstrates the Ramanujan spectral gap, and shows the connection
between graph spectra and number-theoretic zeta functions.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from itertools import product


def adjacency_matrix_complete(n):
    """Complete graph K_n: every vertex connects to every other."""
    return np.ones((n, n)) - np.eye(n)


def adjacency_matrix_cycle(n):
    """Cycle graph C_n."""
    A = np.zeros((n, n))
    for i in range(n):
        A[i][(i+1) % n] = 1
        A[i][(i-1) % n] = 1
    return A


def adjacency_matrix_petersen():
    """The Petersen graph: 3-regular, 10 vertices."""
    A = np.zeros((10, 10))
    # Outer cycle
    for i in range(5):
        A[i][(i+1) % 5] = 1
        A[(i+1) % 5][i] = 1
    # Inner pentagram
    for i in range(5):
        A[5+i][5+(i+2) % 5] = 1
        A[5+(i+2) % 5][5+i] = 1
    # Spokes
    for i in range(5):
        A[i][5+i] = 1
        A[5+i][i] = 1
    return A


def ihara_matrix(A, u):
    """Compute the Ihara matrix I(G,u) = I - uA + u²(D-I)."""
    n = A.shape[0]
    D = np.diag(A.sum(axis=1))
    I = np.eye(n)
    return I - u * A + u**2 * (D - I)


def ihara_zeta_inv(A, u):
    """Compute ζ_G(u)⁻¹ = det(I(G,u))."""
    return np.linalg.det(ihara_matrix(A, u))


def check_ramanujan(A, q):
    """Check if a (q+1)-regular graph is Ramanujan."""
    eigenvalues = np.linalg.eigvalsh(A)
    eigenvalues.sort()
    # Non-trivial eigenvalues: exclude q+1 and -(q+1)
    nontrivial = [ev for ev in eigenvalues
                  if abs(abs(ev) - (q+1)) > 1e-10]
    bound = 2 * np.sqrt(q)
    max_nontrivial = max(abs(ev) for ev in nontrivial) if nontrivial else 0
    return max_nontrivial <= bound + 1e-10, max_nontrivial, bound


def plot_ihara_zeta():
    """Plot |ζ_G(u)⁻¹| for various graphs."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    graphs = [
        ("Complete K₅ (4-regular)", adjacency_matrix_complete(5), 3),
        ("Cycle C₈ (2-regular)", adjacency_matrix_cycle(8), 1),
        ("Petersen (3-regular)", adjacency_matrix_petersen(), 2),
        ("Complete K₇ (6-regular)", adjacency_matrix_complete(7), 5),
    ]

    u_values = np.linspace(0.01, 0.99, 500)

    for ax, (name, A, q) in zip(axes.flat, graphs):
        zeta_inv = [abs(ihara_zeta_inv(A, u)) for u in u_values]
        ax.semilogy(u_values, zeta_inv, 'b-', linewidth=2)
        ax.set_title(f'{name}', fontsize=12)
        ax.set_xlabel('u')
        ax.set_ylabel('|ζ_G(u)⁻¹|')
        ax.grid(True, alpha=0.3)

        # Mark zeros
        for i in range(1, len(zeta_inv)):
            if zeta_inv[i-1] * zeta_inv[i] < 0 or zeta_inv[i] < 1e-10:
                ax.axvline(u_values[i], color='r', alpha=0.3, linestyle='--')

        # Check Ramanujan
        is_ram, max_ev, bound = check_ramanujan(A, q)
        status = "✓ Ramanujan" if is_ram else "✗ Not Ramanujan"
        ax.text(0.05, 0.95, f'{status}\nmax|λ|={max_ev:.3f}, 2√q={bound:.3f}',
                transform=ax.transAxes, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightgreen' if is_ram else 'lightyellow'))

    plt.suptitle('Ihara Zeta Function |ζ_G(u)⁻¹| for Regular Graphs', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('/workspace/request-project/LanglandsBridges/output/ihara_zeta_plot.png', dpi=150)
    plt.close()
    print("Saved: ihara_zeta_plot.png")


def plot_spectral_gap():
    """Plot the Ramanujan spectral gap (q+1) - 2√q."""
    q_values = np.linspace(1, 50, 500)
    gap = q_values + 1 - 2 * np.sqrt(q_values)
    lower_bound = (np.sqrt(q_values) - 1)**2

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(q_values, gap, 'b-', linewidth=2, label='(q+1) - 2√q')
    ax.plot(q_values, lower_bound, 'r--', linewidth=2, label='(√q - 1)²')
    ax.fill_between(q_values, lower_bound, gap, alpha=0.1, color='blue')
    ax.set_xlabel('q (regularity parameter)', fontsize=12)
    ax.set_ylabel('Spectral Gap', fontsize=12)
    ax.set_title('Ramanujan Spectral Gap: (q+1) - 2√q ≥ (√q - 1)²', fontsize=14)
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(1, 50)

    plt.tight_layout()
    plt.savefig('/workspace/request-project/LanglandsBridges/output/spectral_gap_plot.png', dpi=150)
    plt.close()
    print("Saved: spectral_gap_plot.png")


def plot_eigenvalue_distribution():
    """Plot eigenvalue distribution of random regular graphs approaching Kesten-McKay."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    q_values = [2, 5, 10]

    for ax, q in zip(axes, q_values):
        k = q + 1  # degree

        # Kesten-McKay distribution (limit for Ramanujan graphs)
        x = np.linspace(-2*np.sqrt(q), 2*np.sqrt(q), 1000)
        density = k * np.sqrt(4*q - x**2) / (2 * np.pi * (k**2 - x**2))
        density = np.where(np.isfinite(density) & (density > 0), density, 0)

        ax.plot(x, density, 'r-', linewidth=2, label='Kesten-McKay limit')
        ax.fill_between(x, density, alpha=0.2, color='red')
        ax.axvline(-2*np.sqrt(q), color='green', linestyle='--', alpha=0.5, label=f'±2√q = ±{2*np.sqrt(q):.2f}')
        ax.axvline(2*np.sqrt(q), color='green', linestyle='--', alpha=0.5)
        ax.set_title(f'q={q}, (q+1)={k}-regular', fontsize=12)
        ax.set_xlabel('Eigenvalue')
        ax.set_ylabel('Density')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)

    plt.suptitle('Spectral Distribution: Kesten-McKay Law (Ramanujan Limit)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('/workspace/request-project/LanglandsBridges/output/eigenvalue_distribution.png', dpi=150)
    plt.close()
    print("Saved: eigenvalue_distribution.png")


def demo_chip_firing():
    """Demonstrate chip-firing dynamics on a small graph."""
    print("\n=== Chip-Firing Demo ===")
    # Path graph P₄: 0-1-2-3
    n = 4
    A = np.array([[0,1,0,0],[1,0,1,0],[0,1,0,1],[0,0,1,0]], dtype=float)
    L = np.diag(A.sum(axis=1)) - A

    print(f"Graph: Path P₄")
    print(f"Adjacency matrix:\n{A.astype(int)}")
    print(f"Laplacian:\n{L.astype(int)}")

    # Initial divisor
    D = np.array([3, 0, 0, 0])
    print(f"\nInitial divisor: {D}")
    print(f"Degree: {D.sum()}")

    # Chip-fire vertex 0
    print(f"\nChip-fire at vertex 0 (degree 1):")
    D_new = D.copy()
    D_new -= L[0].astype(int)
    print(f"New divisor: {D_new}")
    print(f"Degree: {D_new.sum()} (preserved!)")

    # Chip-fire vertex 1
    print(f"\nChip-fire at vertex 1 (degree 2):")
    D_new2 = D_new.copy()
    D_new2 -= L[1].astype(int)
    print(f"New divisor: {D_new2}")
    print(f"Degree: {D_new2.sum()} (preserved!)")

    # Number of spanning trees
    # Remove row 0, col 0 from L
    L_reduced = L[1:, 1:]
    num_trees = abs(round(np.linalg.det(L_reduced)))
    print(f"\nNumber of spanning trees: {num_trees}")
    print(f"(= |Tropical Jacobian| by Kirchhoff's theorem)")

    # Graph genus
    num_edges = int(A.sum() / 2)
    genus = num_edges - n + 1
    print(f"\nGraph genus: g = |E| - |V| + 1 = {num_edges} - {n} + 1 = {genus}")
    print(f"Canonical divisor degree: 2g-2 = {2*genus - 2}")


def demo_idempotent():
    """Demonstrate idempotent decomposition."""
    print("\n=== Idempotent Decomposition Demo ===")

    # Projection onto first coordinate
    e = np.array([[1, 0, 0],
                   [0, 0, 0],
                   [0, 0, 0]], dtype=float)
    complement = np.eye(3) - e

    print("Idempotent e (project onto x-axis):")
    print(e)
    print(f"\ne² = e: {np.allclose(e @ e, e)}")
    print(f"(1-e)² = (1-e): {np.allclose(complement @ complement, complement)}")
    print(f"e(1-e) = 0: {np.allclose(e @ complement, 0)}")
    print(f"(1-e)e = 0: {np.allclose(complement @ e, 0)}")
    print(f"e + (1-e) = I: {np.allclose(e + complement, np.eye(3))}")
    print(f"tr(e) = {np.trace(e):.0f} (rank of projection)")
    print(f"tr(1-e) = {np.trace(complement):.0f} (rank of complement)")

    # Temperley-Lieb at delta=2
    print("\n--- Temperley-Lieb at δ=2 ---")
    delta = 2
    ei = np.array([[1, 1], [1, 1]], dtype=float)  # ei² = 2·ei
    print(f"TL generator e = [[1,1],[1,1]]")
    print(f"e² = {(ei @ ei).tolist()}")
    print(f"δ·e = {(delta * ei).tolist()}")
    print(f"e²=δ·e: {np.allclose(ei @ ei, delta * ei)}")
    rescaled = ei / delta
    print(f"(e/δ)² = e/δ: {np.allclose(rescaled @ rescaled, rescaled)}")


def main():
    print("=" * 60)
    print("Cross-Domain Bridges: Langlands Program Demos")
    print("=" * 60)

    # Generate plots
    plot_ihara_zeta()
    plot_spectral_gap()
    plot_eigenvalue_distribution()

    # Run text demos
    demo_chip_firing()
    demo_idempotent()

    print("\n" + "=" * 60)
    print("All demos complete. Plots saved to output/")
    print("=" * 60)


if __name__ == "__main__":
    main()

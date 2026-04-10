#!/usr/bin/env python3
"""
Idempotent Neural Convergence Demo

Demonstrates that idempotent layers converge in exactly 1 step,
while general linear layers may require many iterations.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def make_projection_matrix(n, rank):
    """Create a random rank-r projection matrix (idempotent: P^2 = P)."""
    Q = np.linalg.qr(np.random.randn(n, n))[0]
    D = np.diag([1]*rank + [0]*(n - rank))
    return Q @ D @ Q.T

def make_general_matrix(n, spectral_radius=0.9):
    """Create a general contraction matrix."""
    A = np.random.randn(n, n)
    A = A / np.max(np.abs(np.linalg.eigvals(A))) * spectral_radius
    return A

def iterate_and_track(A, x0, n_iters):
    """Track ||A^k x - A^{k-1} x|| over iterations."""
    x = x0.copy()
    diffs = []
    for _ in range(n_iters):
        x_new = A @ x
        diffs.append(np.linalg.norm(x_new - x))
        x = x_new
    return diffs

def main():
    np.random.seed(42)
    n = 50
    n_iters = 30
    x0 = np.random.randn(n)

    # Idempotent (projection) matrix
    P = make_projection_matrix(n, rank=10)
    # General contraction
    A = make_general_matrix(n, spectral_radius=0.95)

    # Verify idempotence
    print(f"||P^2 - P|| = {np.linalg.norm(P @ P - P):.2e} (should be ~0)")
    print(f"Spectral radius of A: {np.max(np.abs(np.linalg.eigvals(A))):.4f}")

    diffs_idem = iterate_and_track(P, x0, n_iters)
    diffs_general = iterate_and_track(A, x0, n_iters)

    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Left: convergence comparison
    ax = axes[0]
    ax.semilogy(range(1, n_iters + 1), diffs_idem, 'b-o', markersize=4,
                label='Idempotent (P² = P)', linewidth=2)
    ax.semilogy(range(1, n_iters + 1), diffs_general, 'r-s', markersize=4,
                label='General contraction (ρ=0.95)', linewidth=2)
    ax.set_xlabel('Iteration k', fontsize=12)
    ax.set_ylabel('||f^k(x) - f^{k-1}(x)||', fontsize=12)
    ax.set_title('Convergence: Idempotent vs General', fontsize=14)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(bottom=1e-17)

    # Right: eigenvalue spectrum
    ax = axes[1]
    eigs_P = np.linalg.eigvals(P)
    eigs_A = np.linalg.eigvals(A)
    ax.scatter(eigs_P.real, eigs_P.imag, c='blue', s=30, alpha=0.7,
               label='Idempotent (eigs ∈ {0,1})')
    ax.scatter(eigs_A.real, eigs_A.imag, c='red', s=30, alpha=0.7,
               label='General contraction')
    theta = np.linspace(0, 2*np.pi, 100)
    ax.plot(np.cos(theta), np.sin(theta), 'k--', alpha=0.3)
    ax.set_xlabel('Re(λ)', fontsize=12)
    ax.set_ylabel('Im(λ)', fontsize=12)
    ax.set_title('Eigenvalue Spectra', fontsize=14)
    ax.legend(fontsize=11)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('/workspace/request-project/CrossCutting/demos/idempotent_convergence.png',
                dpi=150, bbox_inches='tight')
    print("Saved: idempotent_convergence.png")

    # Print convergence data
    print(f"\nIdempotent: converges to 0 at step 2 (diff = {diffs_idem[1]:.2e})")
    print(f"General: still converging at step {n_iters} (diff = {diffs_general[-1]:.2e})")

if __name__ == '__main__':
    main()

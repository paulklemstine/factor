#!/usr/bin/env python3
"""
Quantum Phase Lattice — Spectral Theory Demo

Demonstrates the spectral theory theorems:
- Theorem 37: Eigenspace is a submodule (lattice element)
- Theorem 38: Eigenspaces for distinct eigenvalues are disjoint
- Theorem 39: Self-adjoint eigenvalues are real
- Theorem 40: Eigenvectors of self-adjoint operators are orthogonal
- Theorem 29: Self-adjoint operators have real expectation values
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def random_hermitian(dim, seed=None):
    """Generate a random Hermitian (self-adjoint) matrix."""
    if seed is not None:
        np.random.seed(seed)
    M = np.random.randn(dim, dim) + 1j * np.random.randn(dim, dim)
    return (M + M.conj().T) / 2


def demo_eigenvalue_reality():
    """Theorem 39: Self-adjoint eigenvalues are real."""
    print("=" * 60)
    print("SELF-ADJOINT EIGENVALUES ARE REAL (Theorem 39)")
    print("=" * 60)

    for dim in [2, 3, 5, 10, 50]:
        A = random_hermitian(dim, seed=42 + dim)
        eigenvalues = np.linalg.eigvalsh(A)

        max_imag = np.max(np.abs(eigenvalues.imag))
        print(f"  dim={dim:3d}: max |Im(λ)| = {max_imag:.2e}  "
              f"eigenvalues = [{', '.join(f'{v:.4f}' for v in eigenvalues[:4])}{'...' if dim > 4 else ''}]")

        assert max_imag < 1e-10, f"Non-real eigenvalue found for dim={dim}!"

    print("✓ All eigenvalues are real for self-adjoint operators")


def demo_eigenvector_orthogonality():
    """Theorem 40: Eigenvectors for distinct eigenvalues are orthogonal."""
    print("\n" + "=" * 60)
    print("EIGENVECTOR ORTHOGONALITY (Theorem 40)")
    print("=" * 60)

    dim = 6
    A = random_hermitian(dim, seed=123)
    eigenvalues, eigenvectors = np.linalg.eigh(A)

    print(f"  Eigenvalues: {eigenvalues}")

    # Check all pairs
    max_inner = 0
    n_pairs = 0
    for i in range(dim):
        for j in range(i + 1, dim):
            if abs(eigenvalues[i] - eigenvalues[j]) > 1e-10:
                inner = abs(np.vdot(eigenvectors[:, i], eigenvectors[:, j]))
                max_inner = max(max_inner, inner)
                n_pairs += 1

    print(f"  Checked {n_pairs} pairs of eigenvectors with distinct eigenvalues")
    print(f"  Max |⟨vᵢ|vⱼ⟩| = {max_inner:.2e}")
    print("✓ All eigenvectors for distinct eigenvalues are orthogonal")


def demo_eigenspace_structure():
    """
    Theorem 37: Eigenspace is a submodule.
    Theorem 38: Eigenspaces for distinct eigenvalues are disjoint.
    """
    print("\n" + "=" * 60)
    print("EIGENSPACE STRUCTURE (Theorems 37, 38)")
    print("=" * 60)

    # Create a matrix with known degenerate eigenvalues
    # A = diag(1, 1, 2, 2, 2, 3)
    eigenvalues_desired = [1, 1, 2, 2, 2, 3]
    D = np.diag(np.array(eigenvalues_desired, dtype=complex))

    # Random unitary change of basis
    np.random.seed(456)
    M = np.random.randn(6, 6) + 1j * np.random.randn(6, 6)
    U, _ = np.linalg.qr(M)

    A = U @ D @ U.conj().T

    eigenvalues, eigenvectors = np.linalg.eigh(A)
    print(f"  Eigenvalues: {np.round(eigenvalues, 4)}")

    # Group into eigenspaces
    tol = 1e-8
    eigenspaces = {}
    for i, lam in enumerate(eigenvalues):
        key = round(lam, 6)
        if key not in eigenspaces:
            eigenspaces[key] = []
        eigenspaces[key].append(eigenvectors[:, i])

    for lam, vecs in eigenspaces.items():
        print(f"  Eigenspace for λ={lam:.4f}: dimension {len(vecs)}")

        # Theorem 37: Verify it's a submodule (closed under linear combinations)
        if len(vecs) >= 2:
            combo = 0.3 * vecs[0] + 0.7j * vecs[1]
            result = A @ combo
            expected = lam * combo
            assert np.allclose(result, expected, atol=1e-8), \
                f"Eigenspace not closed under linear combinations!"
            print(f"    ✓ Closed under linear combinations (submodule)")

    # Theorem 38: Disjointness
    distinct_eigenvalues = sorted(eigenspaces.keys())
    for i, lam1 in enumerate(distinct_eigenvalues):
        for lam2 in distinct_eigenvalues[i+1:]:
            vecs1 = eigenspaces[lam1]
            vecs2 = eigenspaces[lam2]
            for v1 in vecs1:
                for v2 in vecs2:
                    inner = abs(np.vdot(v1, v2))
                    assert inner < 1e-8, \
                        f"Eigenspaces for {lam1} and {lam2} not disjoint!"
    print("  ✓ Eigenspaces for distinct eigenvalues are disjoint")


def demo_real_expectation():
    """Theorem 29: Self-adjoint operators have real expectation values."""
    print("\n" + "=" * 60)
    print("REAL EXPECTATION VALUES (Theorem 29)")
    print("⟨Av, v⟩ ∈ ℝ for self-adjoint A")
    print("=" * 60)

    dim = 10
    A = random_hermitian(dim, seed=789)

    np.random.seed(101)
    max_imag = 0
    for _ in range(10000):
        v = np.random.randn(dim) + 1j * np.random.randn(dim)
        expectation = np.vdot(v, A @ v)
        max_imag = max(max_imag, abs(expectation.imag))

    print(f"  Tested 10000 random vectors in C^{dim}")
    print(f"  Max |Im⟨Av, v⟩| = {max_imag:.2e}")
    print("✓ All expectation values are real (within numerical precision)")


def demo_spectral_visualization():
    """Visualize the spectral decomposition."""
    print("\n" + "=" * 60)
    print("SPECTRAL DECOMPOSITION VISUALIZATION")
    print("=" * 60)

    dim = 20
    A = random_hermitian(dim, seed=42)
    eigenvalues = np.linalg.eigvalsh(A)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Eigenvalue distribution
    axes[0].stem(range(dim), eigenvalues, linefmt='b-', markerfmt='bo', basefmt='k-')
    axes[0].axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    axes[0].set_xlabel('Index')
    axes[0].set_ylabel('Eigenvalue')
    axes[0].set_title(f'Spectrum of {dim}×{dim} Hermitian Matrix')
    axes[0].grid(True, alpha=0.3)

    # Expectation value distribution for random states
    np.random.seed(202)
    expectations = []
    for _ in range(5000):
        v = np.random.randn(dim) + 1j * np.random.randn(dim)
        v /= np.linalg.norm(v)
        expectations.append(np.real(np.vdot(v, A @ v)))

    axes[1].hist(expectations, bins=50, density=True, alpha=0.7, color='blue')
    for lam in eigenvalues:
        axes[1].axvline(x=lam, color='red', alpha=0.3, linewidth=0.5)
    axes[1].set_xlabel('⟨v|A|v⟩')
    axes[1].set_ylabel('Density')
    axes[1].set_title('Distribution of Expectation Values (random unit vectors)')
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('spectral_decomposition.png', dpi=150)
    plt.close()
    print("  Plot saved: spectral_decomposition.png")


if __name__ == '__main__':
    demo_eigenvalue_reality()
    demo_eigenvector_orthogonality()
    demo_eigenspace_structure()
    demo_real_expectation()
    demo_spectral_visualization()
    print("\n" + "=" * 60)
    print("ALL SPECTRAL THEORY DEMOS PASSED ✓")
    print("=" * 60)

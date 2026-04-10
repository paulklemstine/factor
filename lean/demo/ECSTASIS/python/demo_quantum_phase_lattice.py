#!/usr/bin/env python3
"""
Quantum Phase Lattice — Core Demo

Demonstrates the key theorems from the formally verified quantum phase lattice:
1. Quantum interference formula
2. Phase invariance of norm and inner product
3. Superposition norm bounds
4. Born rule and Cauchy-Schwarz
5. Parallelogram law
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def demo_interference_formula():
    """
    Theorem 10: ‖ψ + φ‖² = ‖ψ‖² + ‖φ‖² + 2·Re⟨ψ|φ⟩
    
    Demonstrates constructive and destructive interference
    as the relative phase between two states varies.
    """
    print("=" * 60)
    print("QUANTUM INTERFERENCE FORMULA")
    print("‖ψ + φ‖² = ‖ψ‖² + ‖φ‖² + 2·Re⟨ψ|φ⟩")
    print("=" * 60)

    psi = np.array([1, 0], dtype=complex)
    phi_base = np.array([0, 1], dtype=complex)

    phases = np.linspace(0, 2 * np.pi, 100)
    norms_sq = []
    interference_terms = []

    for theta in phases:
        phi = np.exp(1j * theta) * phi_base
        superposition = psi + phi

        norm_sq = np.linalg.norm(superposition) ** 2
        individual = np.linalg.norm(psi) ** 2 + np.linalg.norm(phi) ** 2
        interference = 2 * np.real(np.vdot(psi, phi))

        norms_sq.append(norm_sq)
        interference_terms.append(interference)

        # Verify the formula
        assert abs(norm_sq - (individual + interference)) < 1e-10, \
            f"Interference formula violated! {norm_sq} != {individual} + {interference}"

    print("✓ Interference formula verified for 100 phase angles")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

    ax1.plot(np.degrees(phases), norms_sq, 'b-', linewidth=2)
    ax1.axhline(y=2, color='gray', linestyle='--', label='Classical (no interference)')
    ax1.set_xlabel('Relative phase (degrees)')
    ax1.set_ylabel('‖ψ + φ‖²')
    ax1.set_title('Quantum Interference: Superposition Norm²')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2.plot(np.degrees(phases), interference_terms, 'r-', linewidth=2)
    ax2.axhline(y=0, color='gray', linestyle='--')
    ax2.fill_between(np.degrees(phases), interference_terms, alpha=0.3, color='red')
    ax2.set_xlabel('Relative phase (degrees)')
    ax2.set_ylabel('2·Re⟨ψ|φ⟩')
    ax2.set_title('Interference Term')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('quantum_interference_demo.png', dpi=150)
    plt.close()
    print("  Plot saved: quantum_interference_demo.png")


def demo_phase_invariance():
    """
    Theorem 7: ‖e^{iθ}·ψ‖ = ‖ψ‖
    Theorem 8: |⟨ψ|e^{iθ}φ⟩| = |⟨ψ|φ⟩|
    """
    print("\n" + "=" * 60)
    print("PHASE INVARIANCE")
    print("‖e^{iθ}·ψ‖ = ‖ψ‖  and  |⟨ψ|e^{iθ}φ⟩| = |⟨ψ|φ⟩|")
    print("=" * 60)

    psi = np.array([1, 1j, -0.5], dtype=complex) / np.sqrt(2.25)
    phi = np.array([0.5, -1j, 1], dtype=complex) / np.sqrt(2.25)

    original_norm = np.linalg.norm(psi)
    original_inner = abs(np.vdot(psi, phi))

    for theta in np.linspace(0, 2 * np.pi, 1000):
        phase = np.exp(1j * theta)

        # Theorem 7: Norm invariance
        rotated_norm = np.linalg.norm(phase * psi)
        assert abs(rotated_norm - original_norm) < 1e-10, \
            f"Norm invariance violated at θ={theta:.3f}"

        # Theorem 8: Inner product magnitude invariance
        rotated_inner = abs(np.vdot(psi, phase * phi))
        assert abs(rotated_inner - original_inner) < 1e-10, \
            f"Inner product invariance violated at θ={theta:.3f}"

    print("✓ Phase invariance of norm verified for 1000 angles")
    print("✓ Phase invariance of |⟨ψ|φ⟩| verified for 1000 angles")
    print(f"  ‖ψ‖ = {original_norm:.6f} (constant)")
    print(f"  |⟨ψ|φ⟩| = {original_inner:.6f} (constant)")


def demo_born_rule():
    """
    Theorem 4: |⟨ψ|φ⟩|² ≥ 0
    Theorem 5: |⟨ψ|φ⟩| ≤ ‖ψ‖·‖φ‖
    Theorem 6: For unit vectors, |⟨ψ|φ⟩| ≤ 1
    """
    print("\n" + "=" * 60)
    print("BORN RULE AND CAUCHY-SCHWARZ")
    print("|⟨ψ|φ⟩|² ≥ 0,  |⟨ψ|φ⟩| ≤ ‖ψ‖·‖φ‖")
    print("=" * 60)

    np.random.seed(42)
    n_tests = 10000
    violations = 0

    for _ in range(n_tests):
        dim = np.random.randint(2, 10)
        psi = np.random.randn(dim) + 1j * np.random.randn(dim)
        phi = np.random.randn(dim) + 1j * np.random.randn(dim)

        inner = np.vdot(psi, phi)

        # Theorem 4: Non-negativity
        assert abs(inner) ** 2 >= -1e-15

        # Theorem 5: Cauchy-Schwarz
        cs_bound = np.linalg.norm(psi) * np.linalg.norm(phi)
        assert abs(inner) <= cs_bound + 1e-10

        # Theorem 6: Unit vectors
        psi_unit = psi / np.linalg.norm(psi)
        phi_unit = phi / np.linalg.norm(phi)
        assert abs(np.vdot(psi_unit, phi_unit)) <= 1 + 1e-10

    print(f"✓ Born rule non-negativity verified for {n_tests} random pairs")
    print(f"✓ Cauchy-Schwarz bound verified for {n_tests} random pairs")
    print(f"✓ Unit vector bound verified for {n_tests} random pairs")


def demo_parallelogram_law():
    """
    Theorem 18: ‖ψ+φ‖² + ‖ψ-φ‖² = 2(‖ψ‖² + ‖φ‖²)
    """
    print("\n" + "=" * 60)
    print("PARALLELOGRAM LAW")
    print("‖ψ+φ‖² + ‖ψ-φ‖² = 2(‖ψ‖² + ‖φ‖²)")
    print("=" * 60)

    np.random.seed(123)

    for i in range(1000):
        dim = np.random.randint(2, 20)
        psi = np.random.randn(dim) + 1j * np.random.randn(dim)
        phi = np.random.randn(dim) + 1j * np.random.randn(dim)

        lhs = np.linalg.norm(psi + phi) ** 2 + np.linalg.norm(psi - phi) ** 2
        rhs = 2 * (np.linalg.norm(psi) ** 2 + np.linalg.norm(phi) ** 2)

        assert abs(lhs - rhs) < 1e-8, \
            f"Parallelogram law violated! {lhs} != {rhs}"

    print("✓ Parallelogram law verified for 1000 random pairs")


def demo_projection_norm():
    """
    Theorem 11: ‖P_K ψ‖ ≤ ‖ψ‖
    """
    print("\n" + "=" * 60)
    print("PROJECTION NORM DECREASE")
    print("‖P_K ψ‖ ≤ ‖ψ‖")
    print("=" * 60)

    dim = 5
    np.random.seed(456)

    for _ in range(1000):
        # Random subspace of dimension k
        k = np.random.randint(1, dim)
        basis = np.random.randn(dim, k) + 1j * np.random.randn(dim, k)
        Q, _ = np.linalg.qr(basis)  # Orthonormal basis for K

        # Projection matrix
        P = Q @ Q.conj().T

        # Random state
        psi = np.random.randn(dim) + 1j * np.random.randn(dim)

        projected = P @ psi
        assert np.linalg.norm(projected) <= np.linalg.norm(psi) + 1e-10, \
            "Projection norm increase!"

    print("✓ Projection norm decrease verified for 1000 random (subspace, state) pairs")


if __name__ == '__main__':
    demo_interference_formula()
    demo_phase_invariance()
    demo_born_rule()
    demo_parallelogram_law()
    demo_projection_norm()
    print("\n" + "=" * 60)
    print("ALL DEMOS PASSED ✓")
    print("=" * 60)

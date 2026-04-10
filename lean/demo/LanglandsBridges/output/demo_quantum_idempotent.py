"""
Quantum Idempotent Framework Demo

Demonstrates connections between idempotent theory and quantum mechanics:
1. Density matrices and purity bounds
2. Spectral decomposition and von Neumann entropy
3. Marchenko-Pastur eigenvalue distribution
4. Quantum channel trace preservation
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def random_density_matrix(n):
    """Generate a random n×n density matrix."""
    # Method: generate a random Ginibre matrix, then form ρ = AA†/tr(AA†)
    A = np.random.randn(n, n) + 1j * np.random.randn(n, n)
    rho = A @ A.conj().T
    rho /= np.trace(rho)
    return rho

def pure_state_dm(n, state_idx=0):
    """Generate a pure state density matrix |ψ⟩⟨ψ|."""
    psi = np.zeros(n, dtype=complex)
    psi[state_idx] = 1.0
    return np.outer(psi, psi.conj())

def von_neumann_entropy(rho):
    """Compute S(ρ) = -Σ pᵢ log(pᵢ)."""
    eigenvalues = np.linalg.eigvalsh(rho)
    eigenvalues = eigenvalues[eigenvalues > 1e-12]
    return -np.sum(eigenvalues * np.log(eigenvalues))

def purity(rho):
    """Compute tr(ρ²)."""
    return np.real(np.trace(rho @ rho))

def demo_purity_bounds():
    """Demonstrate the Cauchy-Schwarz purity bound: tr(ρ²) ≥ 1/n."""
    print("=" * 70)
    print("PURITY BOUNDS: tr(ρ²) ∈ [1/n, 1]")
    print("=" * 70)
    
    dimensions = [2, 4, 8, 16, 32]
    num_samples = 500
    
    fig, axes = plt.subplots(1, len(dimensions), figsize=(20, 4))
    
    for idx, n in enumerate(dimensions):
        purities = []
        for _ in range(num_samples):
            rho = random_density_matrix(n)
            purities.append(purity(rho))
        
        ax = axes[idx]
        ax.hist(purities, bins=30, density=True, alpha=0.7, color='steelblue')
        ax.axvline(x=1/n, color='red', linestyle='--', linewidth=2, 
                   label=f'1/n = {1/n:.4f}')
        ax.axvline(x=1, color='green', linestyle='--', linewidth=2,
                   label='Pure state')
        ax.set_xlabel('Purity tr(ρ²)')
        ax.set_ylabel('Density')
        ax.set_title(f'n = {n}')
        ax.legend(fontsize=7)
        
        print(f"\nn = {n}:")
        print(f"  Lower bound 1/n = {1/n:.6f}")
        print(f"  Min purity observed: {min(purities):.6f}")
        print(f"  Mean purity: {np.mean(purities):.6f}")
        print(f"  Bound satisfied: {all(p >= 1/n - 1e-10 for p in purities)}")
    
    plt.tight_layout()
    plt.savefig('/workspace/request-project/LanglandsBridges/output/purity_bounds.png',
                dpi=150, bbox_inches='tight')
    print("\n[Saved: purity_bounds.png]")

def demo_entropy():
    """Demonstrate von Neumann entropy properties."""
    print("\n" + "=" * 70)
    print("VON NEUMANN ENTROPY")
    print("=" * 70)
    
    for n in [2, 4, 8]:
        # Pure state
        rho_pure = pure_state_dm(n)
        S_pure = von_neumann_entropy(rho_pure)
        
        # Maximally mixed state
        rho_mixed = np.eye(n) / n
        S_mixed = von_neumann_entropy(rho_mixed)
        
        # Random state
        rho_random = random_density_matrix(n)
        S_random = von_neumann_entropy(rho_random)
        
        print(f"\nn = {n}:")
        print(f"  Pure state:   S = {S_pure:.6f} (expected: 0)")
        print(f"  Max mixed:    S = {S_mixed:.6f} (expected: log({n}) = {np.log(n):.6f})")
        print(f"  Random state: S = {S_random:.6f}")
        print(f"  0 ≤ S_random ≤ log(n): {0 <= S_random <= np.log(n) + 1e-10}")

def demo_marchenko_pastur():
    """Demonstrate Marchenko-Pastur eigenvalue distribution."""
    print("\n" + "=" * 70)
    print("MARCHENKO-PASTUR DISTRIBUTION")
    print("=" * 70)
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    for idx, (n, m) in enumerate([(50, 200), (100, 400), (200, 800)]):
        gamma = n / m
        all_eigenvalues = []
        
        for _ in range(100):
            X = np.random.randn(n, m) / np.sqrt(m)
            W = X @ X.T  # Wishart matrix
            eigenvalues = np.linalg.eigvalsh(W)
            all_eigenvalues.extend(eigenvalues)
        
        # Marchenko-Pastur theoretical bounds
        lambda_minus = (1 - np.sqrt(gamma))**2
        lambda_plus = (1 + np.sqrt(gamma))**2
        width = 4 * np.sqrt(gamma)
        
        # Theoretical density
        x = np.linspace(lambda_minus + 0.001, lambda_plus - 0.001, 200)
        mp_density = np.sqrt((lambda_plus - x) * (x - lambda_minus)) / (2 * np.pi * gamma * x)
        
        ax = axes[idx]
        ax.hist(all_eigenvalues, bins=80, density=True, alpha=0.5, 
                color='steelblue', label='Empirical')
        ax.plot(x, mp_density, 'r-', linewidth=2, label='MP density')
        ax.axvline(x=lambda_minus, color='green', linestyle='--', alpha=0.7)
        ax.axvline(x=lambda_plus, color='green', linestyle='--', alpha=0.7)
        ax.set_xlabel('λ')
        ax.set_ylabel('Density')
        ax.set_title(f'γ = n/m = {gamma:.2f}, width = 4√γ = {width:.3f}')
        ax.legend()
        
        print(f"\nγ = {gamma:.2f} (n={n}, m={m}):")
        print(f"  MP support: [{lambda_minus:.4f}, {lambda_plus:.4f}]")
        print(f"  Predicted width: 4√γ = {width:.4f}")
        print(f"  Empirical range: [{min(all_eigenvalues):.4f}, {max(all_eigenvalues):.4f}]")
    
    plt.tight_layout()
    plt.savefig('/workspace/request-project/LanglandsBridges/output/marchenko_pastur.png',
                dpi=150, bbox_inches='tight')
    print("\n[Saved: marchenko_pastur.png]")

def demo_idempotent_projectors():
    """Demonstrate idempotent projector properties in quantum mechanics."""
    print("\n" + "=" * 70)
    print("IDEMPOTENT PROJECTORS IN QUANTUM MECHANICS")
    print("=" * 70)
    
    n = 4
    # Create orthogonal projectors
    # P₁ projects onto |0⟩, P₂ onto |1⟩, etc.
    projectors = [np.zeros((n, n)) for _ in range(n)]
    for i in range(n):
        projectors[i][i, i] = 1.0
    
    # Verify idempotent property
    print(f"\nDimension n = {n}")
    for i, P in enumerate(projectors):
        is_idem = np.allclose(P @ P, P)
        print(f"  P_{i}² = P_{i}: {is_idem}")
    
    # Verify orthogonality
    for i in range(n):
        for j in range(i+1, n):
            is_orth = np.allclose(projectors[i] @ projectors[j], 0)
            print(f"  P_{i} · P_{j} = 0: {is_orth}")
    
    # Verify completeness
    total = sum(projectors)
    is_complete = np.allclose(total, np.eye(n))
    print(f"  Σ Pᵢ = I: {is_complete}")
    
    # Complement property
    e = projectors[0]
    complement = np.eye(n) - e
    is_idem_comp = np.allclose(complement @ complement, complement)
    is_orth = np.allclose(e @ complement, 0)
    print(f"\n  e = P₀, (1-e)² = (1-e): {is_idem_comp}")
    print(f"  e·(1-e) = 0: {is_orth}")
    
    # Spectral decomposition of a density matrix
    eigenvalues = np.array([0.5, 0.3, 0.15, 0.05])
    rho = sum(p * P for p, P in zip(eigenvalues, projectors))
    
    print(f"\nDensity matrix ρ = Σ pᵢPᵢ with p = {eigenvalues}")
    print(f"  tr(ρ) = {np.trace(rho):.6f} (expected: 1)")
    print(f"  tr(ρ²) = {np.trace(rho @ rho):.6f}")
    print(f"  Σ pᵢ² = {sum(p**2 for p in eigenvalues):.6f}")
    print(f"  Match: {np.isclose(np.trace(rho @ rho), sum(p**2 for p in eigenvalues))}")
    print(f"  Purity ≥ 1/n = {1/n}: {np.trace(rho @ rho) >= 1/n - 1e-10}")

if __name__ == "__main__":
    demo_purity_bounds()
    demo_entropy()
    demo_marchenko_pastur()
    demo_idempotent_projectors()
    print("\nAll demos completed!")

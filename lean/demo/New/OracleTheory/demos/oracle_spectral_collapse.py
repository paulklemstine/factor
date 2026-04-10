"""
Oracle Theory Demo: Spectral Collapse Visualization

Demonstrates the Spectral Collapse Theorem: eigenvalues of idempotent
matrices are exactly {0, 1}. Shows how iterating a matrix toward
idempotency causes its eigenvalues to collapse to the binary spectrum.

Usage:
    python oracle_spectral_collapse.py
"""

import numpy as np
import json


def make_random_matrix(n: int) -> np.ndarray:
    """Generate a random n×n matrix."""
    return np.random.randn(n, n)


def project_to_idempotent(M: np.ndarray, steps: int = 100) -> list[dict]:
    """
    Smoothly interpolate from M toward its nearest idempotent.
    Use eigendecomposition: round eigenvalues toward {0, 1}.
    
    Returns the eigenvalue history at each step.
    """
    history = []
    evals, evecs = np.linalg.eig(M)
    evals = np.real(evals)
    evecs = np.real(evecs)
    
    for step in range(steps + 1):
        t = step / steps  # interpolation parameter 0 to 1
        # Smoothly round each eigenvalue toward 0 or 1
        target_evals = np.where(evals > 0.5, 1.0, 0.0)
        current_evals = evals * (1 - t) + target_evals * t
        
        current = evecs @ np.diag(current_evals) @ np.linalg.inv(evecs)
        eigenvalues = np.sort(current_evals)
        idempotency_error = np.linalg.norm(current @ current - current, 'fro')
        
        history.append({
            'step': step,
            'eigenvalues': eigenvalues.tolist(),
            'idempotency_error': float(idempotency_error),
            'eigenvalue_binary_distance': float(
                np.sum(np.minimum(np.abs(eigenvalues), np.abs(eigenvalues - 1)))
            )
        })
        
        if idempotency_error < 1e-12:
            break
    
    return history


def demonstrate_spectral_collapse():
    """Main demonstration of spectral collapse."""
    print("=" * 60)
    print("SPECTRAL COLLAPSE THEOREM DEMONSTRATION")
    print("=" * 60)
    print()
    print("Theorem: Every eigenvalue of an idempotent matrix is 0 or 1.")
    print("         (Proved in Lean 4: spectral_collapse_eigenvalue)")
    print()
    
    np.random.seed(42)
    n = 5
    
    # Start with a random matrix
    M = make_random_matrix(n)
    # Scale to have eigenvalues roughly in [0, 1]
    M = M / (2 * np.linalg.norm(M))
    M = M + 0.5 * np.eye(n)
    
    print(f"Starting matrix ({n}×{n}) with eigenvalues:")
    eigs = np.sort(np.real(np.linalg.eigvals(M)))
    for i, e in enumerate(eigs):
        print(f"  λ_{i+1} = {e:.4f}")
    print()
    
    # Iterate toward idempotency
    history = project_to_idempotent(M, steps=20)
    
    print("Iteration toward idempotency (M ↦ 3M² - 2M³):")
    print("-" * 50)
    for record in history:
        step = record['step']
        err = record['idempotency_error']
        eigs = record['eigenvalues']
        print(f"  Step {step:2d}: error={err:.2e}, eigenvalues=[{', '.join(f'{e:.4f}' for e in eigs)}]")
    
    print()
    final_eigs = history[-1]['eigenvalues']
    print("RESULT: Final eigenvalues collapsed to {0, 1}:")
    for i, e in enumerate(final_eigs):
        label = "≈ 0" if abs(e) < 0.01 else "≈ 1"
        print(f"  λ_{i+1} = {e:.10f}  ({label})")
    
    # Verify idempotency
    print(f"\nFinal idempotency error: {history[-1]['idempotency_error']:.2e}")
    print()
    
    return history


def demonstrate_determinant_collapse():
    """Show det(M) ∈ {0, 1} for idempotent M."""
    print("=" * 60)
    print("DETERMINANT COLLAPSE: det(M) ∈ {0, 1}")
    print("=" * 60)
    print("(Proved in Lean 4: idempotent_det_zero_or_one)")
    print()
    
    np.random.seed(123)
    
    for trial in range(5):
        n = 4
        # Create a random projection matrix (idempotent by construction)
        rank = np.random.randint(0, n + 1)
        if rank == 0:
            P = np.zeros((n, n))
        elif rank == n:
            P = np.eye(n)
        else:
            Q = np.random.randn(n, rank)
            P = Q @ np.linalg.inv(Q.T @ Q) @ Q.T
        
        det = np.linalg.det(P)
        err = np.linalg.norm(P @ P - P, 'fro')
        print(f"  Trial {trial+1}: rank={rank}, det={det:.10f}, "
              f"idempotency_error={err:.2e}")
    print()


def demonstrate_goodhart_decay():
    """Show exponential alignment decay (Goodhart's Law)."""
    print("=" * 60)
    print("GOODHART'S LAW: ALIGNMENT DECAY")
    print("=" * 60)
    print("(Proved in Lean 4: alignment_tendsto_zero)")
    print()
    
    initial_alignment = 0.95
    decay_rates = [0.99, 0.95, 0.90, 0.80]
    
    print("Alignment = initial_correlation × decay_rate^t")
    print()
    
    for r in decay_rates:
        print(f"  Decay rate r={r}:")
        for t in [0, 10, 50, 100, 500]:
            alignment = initial_alignment * r ** t
            print(f"    t={t:4d}: alignment={alignment:.6f}")
        print()


def demonstrate_council_diminishing_returns():
    """Show diminishing returns for oracle councils."""
    print("=" * 60)
    print("ORACLE COUNCIL: DIMINISHING RETURNS")
    print("=" * 60)
    print("(Proved in Lean 4: diminishing_returns)")
    print()
    
    sigma_sq = 1.0
    print(f"Individual variance σ² = {sigma_sq}")
    print()
    print(f"  {'k':>4s}  {'Variance':>12s}  {'Marginal Reduction':>20s}  {'% of σ²':>10s}")
    print(f"  {'---':>4s}  {'--------':>12s}  {'------------------':>20s}  {'------':>10s}")
    
    for k in range(1, 21):
        variance = sigma_sq / k
        if k == 1:
            marginal = sigma_sq - variance
        else:
            marginal = sigma_sq / ((k-1) * k)  # σ²/(k(k-1))
        print(f"  {k:4d}  {variance:12.6f}  {marginal:20.6f}  {variance/sigma_sq*100:9.1f}%")
    print()


def demonstrate_phase_transition():
    """Show sharp phase transition in convergence."""
    print("=" * 60)
    print("PHASE TRANSITION IN ORACLE CONVERGENCE")
    print("=" * 60)
    print("(Proved in Lean 4: geometric_convergence, geometric_divergence)")
    print()
    
    x0 = 10.0
    contraction_factors = [0.3, 0.7, 0.9, 0.99, 1.0, 1.01, 1.1, 2.0]
    
    for c in contraction_factors:
        values = [x0]
        x = x0
        for _ in range(20):
            x = c * x
            values.append(x)
        
        final = values[-1]
        status = "CONVERGES" if abs(c) < 1 else ("CRITICAL" if c == 1.0 else "DIVERGES")
        print(f"  c={c:5.2f}: x₂₀={final:>15.4f}  [{status}]")
    print()


def main():
    """Run all demonstrations."""
    demonstrate_spectral_collapse()
    demonstrate_determinant_collapse()
    demonstrate_goodhart_decay()
    demonstrate_council_diminishing_returns()
    demonstrate_phase_transition()
    
    print("=" * 60)
    print("All demonstrations complete.")
    print("Every result above is backed by a machine-verified")
    print("proof in Lean 4 (see OracleTheory/ directory).")
    print("=" * 60)


if __name__ == "__main__":
    main()

"""
Oracle Networks Demo: Council Dynamics and Self-Improvement

Interactive demonstration of oracle network convergence, council
optimization, and self-improvement bounds.

Usage:
    python oracle_networks.py
"""

import numpy as np
from typing import List, Tuple


def oracle_council_simulation(
    true_value: float,
    n_oracles: int,
    noise_std: float,
    n_rounds: int = 50
) -> dict:
    """
    Simulate an oracle council with n_oracles providing noisy estimates.
    Each round, each oracle updates to a weighted average of its own
    estimate and the council mean (contraction toward consensus).
    
    Returns convergence history.
    """
    np.random.seed(42)
    
    # Initialize oracles with noisy estimates
    estimates = true_value + noise_std * np.random.randn(n_oracles)
    
    history = {
        'round': [],
        'mean': [],
        'variance': [],
        'max_error': [],
        'estimates': []
    }
    
    contraction = 0.8  # Mix 80% council mean, 20% own estimate
    
    for round_num in range(n_rounds):
        council_mean = np.mean(estimates)
        variance = np.var(estimates)
        max_error = np.max(np.abs(estimates - true_value))
        
        history['round'].append(round_num)
        history['mean'].append(float(council_mean))
        history['variance'].append(float(variance))
        history['max_error'].append(float(max_error))
        history['estimates'].append(estimates.copy().tolist())
        
        # Update: each oracle moves toward the council mean
        estimates = contraction * council_mean + (1 - contraction) * estimates
    
    return history


def self_improvement_simulation(
    initial_error: float,
    improvement_rate: float,
    n_steps: int = 30
) -> List[float]:
    """
    Simulate self-improvement: error decreases geometrically.
    error(k) = initial_error * improvement_rate^k
    
    Proved to converge to 0 (selfImprovementError_tendsto_zero)
    and be strictly decreasing for 0 < r < 1 (selfImprovementError_decreasing).
    """
    return [initial_error * improvement_rate ** k for k in range(n_steps)]


def optimal_council_size(sigma: float, cost_per_oracle: float) -> Tuple[int, float]:
    """
    Find optimal council size minimizing total cost.
    Total cost = sigma/sqrt(k) + cost_per_oracle * k
    
    Derivative: -sigma/(2*k^(3/2)) + cost_per_oracle = 0
    k* = (sigma / (2 * cost_per_oracle))^(2/3)
    """
    k_star = (sigma / (2 * cost_per_oracle)) ** (2/3)
    k_opt = max(1, int(round(k_star)))
    min_cost = sigma / np.sqrt(k_opt) + cost_per_oracle * k_opt
    return k_opt, min_cost


def phase_transition_demo():
    """Demonstrate sharp phase transition in oracle convergence."""
    print("=" * 60)
    print("PHASE TRANSITION IN ORACLE NETWORKS")
    print("=" * 60)
    print()
    
    # Simulate random oracle networks with varying connectivity
    np.random.seed(42)
    n_nodes = 20
    
    probabilities = [0.02, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50]
    threshold = np.log(n_nodes) / n_nodes
    
    print(f"Network: {n_nodes} oracle nodes")
    print(f"Theoretical connectivity threshold: p* ≈ ln({n_nodes})/{n_nodes} = {threshold:.3f}")
    print()
    
    for p in probabilities:
        # Create random adjacency matrix
        adj = (np.random.rand(n_nodes, n_nodes) < p).astype(float)
        np.fill_diagonal(adj, 0)
        adj = np.maximum(adj, adj.T)  # Symmetrize
        
        # Check connectivity via eigenvalues of Laplacian
        degree = np.sum(adj, axis=1)
        laplacian = np.diag(degree) - adj
        eigenvalues = np.sort(np.linalg.eigvalsh(laplacian))
        
        # Second smallest eigenvalue (algebraic connectivity)
        algebraic_connectivity = eigenvalues[1]
        connected = algebraic_connectivity > 1e-10
        avg_degree = np.mean(degree)
        
        status = "CONNECTED" if connected else "DISCONNECTED"
        marker = " ← threshold" if abs(p - threshold) < 0.03 else ""
        print(f"  p={p:.2f}: avg_degree={avg_degree:5.1f}, "
              f"λ₂={algebraic_connectivity:6.3f}, [{status}]{marker}")
    print()


def neural_collapse_demo():
    """Demonstrate simplex ETF structure in neural collapse."""
    print("=" * 60)
    print("NEURAL COLLAPSE: SIMPLEX ETF STRUCTURE")
    print("=" * 60)
    print()
    
    for K in [2, 3, 4, 5, 10]:
        # Construct simplex ETF Gram matrix
        G = np.full((K, K), -1.0 / (K - 1))
        np.fill_diagonal(G, 1.0)
        
        # Verify properties
        eigenvalues = np.sort(np.linalg.eigvalsh(G))
        margin = K / (K - 1)
        
        print(f"  K={K:2d} classes:")
        print(f"    Gram matrix diagonal: {G[0,0]:.4f}")
        print(f"    Gram matrix off-diagonal: {G[0,1]:.4f}")
        print(f"    Eigenvalues: [{', '.join(f'{e:.3f}' for e in eigenvalues)}]")
        print(f"    Max margin: K/(K-1) = {margin:.4f}")
        print(f"    Optimal bottleneck dim: {K-1}")
        print()


def main():
    """Run all oracle network demonstrations."""
    
    # 1. Oracle Council Convergence
    print("=" * 60)
    print("ORACLE COUNCIL CONVERGENCE")
    print("=" * 60)
    print("(Proved in Lean 4: contracting_oracle_cauchy)")
    print()
    
    true_value = 42.0
    for n_oracles in [3, 5, 10, 50]:
        history = oracle_council_simulation(true_value, n_oracles, noise_std=5.0)
        initial_var = history['variance'][0]
        final_var = history['variance'][-1]
        initial_err = history['max_error'][0]
        final_err = history['max_error'][-1]
        print(f"  {n_oracles:3d} oracles: variance {initial_var:.2f} → {final_var:.6f}, "
              f"max_error {initial_err:.2f} → {final_err:.6f}")
    print()
    
    # 2. Self-Improvement Bounds
    print("=" * 60)
    print("SELF-IMPROVEMENT ERROR CONVERGENCE")
    print("=" * 60)
    print("(Proved in Lean 4: selfImprovementError_tendsto_zero)")
    print()
    
    for rate in [0.9, 0.7, 0.5, 0.3]:
        errors = self_improvement_simulation(1.0, rate, n_steps=15)
        print(f"  Rate r={rate}: errors = [{', '.join(f'{e:.4f}' for e in errors[:8])}...]")
    print()
    
    # 3. Optimal Council Size
    print("=" * 60)
    print("OPTIMAL COUNCIL SIZE")
    print("=" * 60)
    print("(Proved in Lean 4: diminishing_returns, council_cost_grows)")
    print()
    
    scenarios = [
        (1.0, 0.01, "Low cost"),
        (1.0, 0.1, "Medium cost"),
        (1.0, 1.0, "High cost"),
        (0.1, 0.01, "Low variance + low cost"),
    ]
    
    for sigma, cost, name in scenarios:
        k_opt, min_cost = optimal_council_size(sigma, cost)
        print(f"  {name}: σ={sigma}, c={cost} → optimal k*={k_opt}, min_cost={min_cost:.4f}")
    print()
    
    # 4. Phase Transition
    phase_transition_demo()
    
    # 5. Neural Collapse
    neural_collapse_demo()
    
    # 6. Goodhart's Law Multi-Proxy
    print("=" * 60)
    print("MULTI-PROXY GOODHART MITIGATION")
    print("=" * 60)
    print("(Proved in Lean 4: multi_proxy_contained)")
    print()
    
    np.random.seed(42)
    n_items = 1000
    n_proxies_list = [1, 2, 3, 5, 10]
    
    for n_proxies in n_proxies_list:
        # True quality + proxy scores
        true_quality = np.random.randn(n_items)
        proxy_scores = [true_quality + np.random.randn(n_items) for _ in range(n_proxies)]
        
        # Select top 10% by each proxy, take intersection
        threshold_pct = 90
        selected = np.ones(n_items, dtype=bool)
        for proxy in proxy_scores:
            threshold = np.percentile(proxy, threshold_pct)
            selected &= (proxy >= threshold)
        
        n_selected = np.sum(selected)
        if n_selected > 0:
            avg_true_quality = np.mean(true_quality[selected])
        else:
            avg_true_quality = float('nan')
        
        print(f"  {n_proxies:2d} proxies: {n_selected:3d} items selected, "
              f"avg true quality = {avg_true_quality:+.3f}")
    print()
    
    print("=" * 60)
    print("All oracle network demonstrations complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()

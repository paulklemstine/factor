"""
Demonstration: Diminishing Returns Theorem for Oracle Councils

This demo visualizes the key results from the formally verified
Diminishing Returns Theorem:
1. Ensemble variance decreasing with n
2. Marginal improvement O(1/n²)
3. Optimal ensemble size via AM-GM
4. Effect of correlation on the irreducible floor

All mathematical results are formally verified in Lean 4.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec


def ensemble_variance(sigma_sq, rho, n):
    """Ensemble variance: σ²/n + ρ·σ²·(n-1)/n"""
    return sigma_sq / n + rho * sigma_sq * (n - 1) / n


def marginal_improvement(sigma_sq, n):
    """Marginal improvement: σ²/(n·(n+1))"""
    return sigma_sq / (n * (n + 1))


def total_cost(sigma_sq, cost_per_oracle, n):
    """Total cost: σ²/n + c·n"""
    return sigma_sq / n + cost_per_oracle * n


def optimal_n(sigma_sq, cost):
    """Optimal ensemble size: √(σ²/c)"""
    return np.sqrt(sigma_sq / cost)


def main():
    fig = plt.figure(figsize=(16, 12))
    gs = GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.3)
    
    # =========================================
    # Plot 1: Ensemble Variance vs. n
    # =========================================
    ax1 = fig.add_subplot(gs[0, 0])
    sigma_sq = 1.0
    ns = np.arange(1, 51)
    
    for rho, color, label in [(0.0, '#2196F3', 'ρ = 0 (independent)'),
                               (0.3, '#4CAF50', 'ρ = 0.3'),
                               (0.5, '#FF9800', 'ρ = 0.5'),
                               (0.8, '#F44336', 'ρ = 0.8 (correlated)')]:
        vs = [ensemble_variance(sigma_sq, rho, n) for n in ns]
        ax1.plot(ns, vs, color=color, linewidth=2, label=label)
        ax1.axhline(y=rho * sigma_sq, color=color, linestyle='--', alpha=0.4)
    
    ax1.set_xlabel('Number of Oracles (n)', fontsize=12)
    ax1.set_ylabel('Ensemble Variance', fontsize=12)
    ax1.set_title('Ensemble Variance: Diminishing Returns', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.set_ylim(0, 1.05)
    ax1.grid(True, alpha=0.3)
    
    # =========================================
    # Plot 2: Marginal Improvement
    # =========================================
    ax2 = fig.add_subplot(gs[0, 1])
    
    improvements = [marginal_improvement(sigma_sq, n) for n in ns]
    ax2.bar(ns, improvements, color='#673AB7', alpha=0.7, width=0.8)
    
    # Overlay 1/n² bound
    bound = [sigma_sq / n**2 for n in ns]
    ax2.plot(ns, bound, 'r--', linewidth=2, label='O(1/n²) bound')
    
    ax2.set_xlabel('Oracle Number (n)', fontsize=12)
    ax2.set_ylabel('Marginal Improvement', fontsize=12)
    ax2.set_title('Marginal Improvement: O(1/n²)', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=11)
    ax2.set_xlim(0, 20)
    ax2.grid(True, alpha=0.3)
    
    # =========================================
    # Plot 3: Optimal Ensemble Size
    # =========================================
    ax3 = fig.add_subplot(gs[1, 0])
    
    costs = [0.01, 0.05, 0.1, 0.5]
    colors = ['#2196F3', '#4CAF50', '#FF9800', '#F44336']
    n_range = np.linspace(1, 50, 200)
    
    for c, color in zip(costs, colors):
        tc = [total_cost(sigma_sq, c, n) for n in n_range]
        n_opt = optimal_n(sigma_sq, c)
        tc_min = 2 * np.sqrt(sigma_sq * c)
        ax3.plot(n_range, tc, color=color, linewidth=2,
                label=f'c = {c} (n* = {n_opt:.1f})')
        ax3.plot(n_opt, tc_min, 'o', color=color, markersize=8)
    
    ax3.set_xlabel('Number of Oracles (n)', fontsize=12)
    ax3.set_ylabel('Total Cost', fontsize=12)
    ax3.set_title('Optimal Ensemble Size (AM-GM Bound)', fontsize=14, fontweight='bold')
    ax3.legend(fontsize=9)
    ax3.set_ylim(0, 2)
    ax3.grid(True, alpha=0.3)
    
    # =========================================
    # Plot 4: Cumulative Improvement
    # =========================================
    ax4 = fig.add_subplot(gs[1, 1])
    
    cumulative = np.cumsum([marginal_improvement(sigma_sq, n) for n in ns])
    max_improvement = sigma_sq  # theoretical maximum
    
    ax4.fill_between(ns, cumulative, alpha=0.3, color='#2196F3')
    ax4.plot(ns, cumulative, color='#2196F3', linewidth=2, label='Cumulative improvement')
    ax4.axhline(y=max_improvement, color='red', linestyle='--', linewidth=2,
               label=f'Theoretical max = σ² = {max_improvement}')
    
    # Mark 80%, 90%, 95% thresholds
    for pct, ls in [(0.8, ':'), (0.9, '-.'), (0.95, '--')]:
        target = pct * max_improvement
        n_needed = next((n for n in ns if cumulative[n-1] >= target), ns[-1])
        ax4.axhline(y=target, color='gray', linestyle=ls, alpha=0.5)
        ax4.annotate(f'{int(pct*100)}% at n={n_needed}', xy=(n_needed, target),
                    fontsize=9, color='gray')
    
    ax4.set_xlabel('Number of Oracles (n)', fontsize=12)
    ax4.set_ylabel('Cumulative Improvement', fontsize=12)
    ax4.set_title('Diminishing Cumulative Returns', fontsize=14, fontweight='bold')
    ax4.legend(fontsize=10)
    ax4.grid(True, alpha=0.3)
    
    fig.suptitle('Formally Verified: Diminishing Returns Theorem for Oracle Councils',
                fontsize=16, fontweight='bold', y=0.98)
    
    plt.savefig('/workspace/request-project/PredictionTheory/demos/ensemble_diminishing_returns.png',
               dpi=150, bbox_inches='tight')
    plt.close()
    print("✓ Saved ensemble_diminishing_returns.png")


if __name__ == '__main__':
    main()

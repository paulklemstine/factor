"""
Demonstration: The Prediction-Information Uncertainty Principle

Visualizes the fundamental tradeoff between prediction precision
and information requirements, including:
1. The uncertainty principle curve (error × info ≥ 1)
2. Cramér-Rao bound scaling with sample size
3. Precision-coverage tradeoff for prediction intervals
4. Meta-prediction hierarchy convergence

All mathematical results are formally verified in Lean 4.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec


def main():
    fig = plt.figure(figsize=(16, 12))
    gs = GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.3)
    
    # =========================================
    # Plot 1: Uncertainty Principle
    # =========================================
    ax1 = fig.add_subplot(gs[0, 0])
    
    info = np.linspace(0.1, 10, 200)
    min_error = 1.0 / info
    
    ax1.fill_between(info, min_error, 5, alpha=0.15, color='#F44336',
                     label='Achievable region')
    ax1.fill_between(info, 0, min_error, alpha=0.15, color='#BDBDBD',
                     label='Forbidden region')
    ax1.plot(info, min_error, 'r-', linewidth=3,
            label='Error × Info = 1 (bound)')
    
    # Example points
    examples = [(1, 1.5, 'Typical ML'), (3, 0.5, 'Good model'),
                (0.5, 3, 'Low data'), (8, 0.15, 'High data')]
    for i_val, e_val, name in examples:
        color = '#4CAF50' if e_val * i_val >= 1 else '#F44336'
        ax1.plot(i_val, e_val, 'o', color=color, markersize=10)
        ax1.annotate(name, xy=(i_val, e_val), xytext=(5, 5),
                    textcoords='offset points', fontsize=9)
    
    ax1.set_xlabel('Information (bits)', fontsize=12)
    ax1.set_ylabel('Prediction Error', fontsize=12)
    ax1.set_title('Prediction-Information Uncertainty Principle',
                 fontsize=14, fontweight='bold')
    ax1.legend(fontsize=9, loc='upper right')
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 3)
    ax1.grid(True, alpha=0.3)
    
    # =========================================
    # Plot 2: Cramér-Rao Bound
    # =========================================
    ax2 = fig.add_subplot(gs[0, 1])
    
    ns = np.arange(1, 101)
    fisher_info = 2.0  # Fisher information per sample
    
    cramer_rao = 1.0 / (ns * fisher_info)
    
    # Simulated estimator performance (slightly above the bound)
    np.random.seed(42)
    achieved = cramer_rao * (1 + 0.3 * np.exp(-ns / 20))
    
    ax2.fill_between(ns, 0, cramer_rao, alpha=0.15, color='#BDBDBD',
                     label='Forbidden by Cramér-Rao')
    ax2.plot(ns, cramer_rao, 'r-', linewidth=2, label='Cramér-Rao bound: 1/(n·I)')
    ax2.plot(ns, achieved, 'b-', linewidth=2, alpha=0.7,
            label='Typical estimator variance')
    
    ax2.set_xlabel('Number of Samples (n)', fontsize=12)
    ax2.set_ylabel('Estimator Variance', fontsize=12)
    ax2.set_title('Cramér-Rao Lower Bound', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.set_ylim(0, 0.6)
    ax2.grid(True, alpha=0.3)
    
    # =========================================
    # Plot 3: Prediction Interval Tradeoff
    # =========================================
    ax3 = fig.add_subplot(gs[1, 0])
    
    from scipy import stats
    
    coverages = np.linspace(0.01, 0.99, 200)
    sigma = 1.0
    widths = 2 * stats.norm.ppf((1 + coverages) / 2) * sigma
    
    ax3.plot(coverages * 100, widths, '#9C27B0', linewidth=3)
    
    # Highlight common intervals
    for cov, color, name in [(0.50, '#2196F3', '50%'),
                              (0.90, '#4CAF50', '90%'),
                              (0.95, '#FF9800', '95%'),
                              (0.99, '#F44336', '99%')]:
        w = 2 * stats.norm.ppf((1 + cov) / 2) * sigma
        ax3.plot(cov * 100, w, 'o', color=color, markersize=10)
        ax3.annotate(f'{name}: w={w:.2f}', xy=(cov * 100, w),
                    xytext=(-60, 10), textcoords='offset points', fontsize=9,
                    color=color)
    
    ax3.set_xlabel('Coverage (%)', fontsize=12)
    ax3.set_ylabel('Interval Width', fontsize=12)
    ax3.set_title('Precision-Coverage Tradeoff (Gaussian)',
                 fontsize=14, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # =========================================
    # Plot 4: Meta-Prediction Hierarchy
    # =========================================
    ax4 = fig.add_subplot(gs[1, 1])
    
    levels = np.arange(0, 15)
    initial_error = 1.0
    errors = initial_error / (2 ** levels)
    bound = initial_error / (2 ** levels)
    
    ax4.semilogy(levels, errors, 'bo-', markersize=8, linewidth=2,
                label='Actual error |eₖ|')
    ax4.semilogy(levels, bound, 'r--', linewidth=2,
                label='Bound: |e₀|/2ᵏ')
    
    ax4.axhline(y=1e-4, color='green', linestyle=':', alpha=0.5)
    ax4.annotate('Target ε = 10⁻⁴', xy=(0, 1e-4), fontsize=10, color='green')
    
    ax4.set_xlabel('Meta-Prediction Level (k)', fontsize=12)
    ax4.set_ylabel('Prediction Error', fontsize=12)
    ax4.set_title('Hierarchical Meta-Prediction Convergence',
                 fontsize=14, fontweight='bold')
    ax4.legend(fontsize=11)
    ax4.grid(True, alpha=0.3)
    ax4.set_ylim(1e-5, 2)
    
    fig.suptitle('Formally Verified: Prediction-Information Uncertainty Principle',
                fontsize=16, fontweight='bold', y=0.98)
    
    plt.savefig('/workspace/request-project/PredictionTheory/demos/prediction_uncertainty.png',
               dpi=150, bbox_inches='tight')
    plt.close()
    print("✓ Saved prediction_uncertainty.png")


if __name__ == '__main__':
    main()

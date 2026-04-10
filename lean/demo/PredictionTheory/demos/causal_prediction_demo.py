"""
Demonstration: Causal vs. Observational Prediction

Visualizes the difference between E[Y|X] and E[Y|do(X)],
showing how confounding bias leads to incorrect causal conclusions.

All bounds are formally verified in Lean 4.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec


def main():
    np.random.seed(42)
    fig = plt.figure(figsize=(16, 12))
    gs = GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.3)
    
    # =========================================
    # Plot 1: Confounding Creates Spurious Association
    # =========================================
    ax1 = fig.add_subplot(gs[0, 0])
    
    n = 500
    # Z (confounder) affects both X and Y
    Z = np.random.randn(n)
    X = 0.5 * Z + 0.3 * np.random.randn(n)  # X depends on Z
    Y_causal = 0.0 * X + np.random.randn(n)  # Y does NOT causally depend on X
    Y_obs = Y_causal + 0.8 * Z               # But Z creates association
    
    ax1.scatter(X, Y_obs, alpha=0.3, s=10, color='#2196F3')
    
    # Fit observational regression
    coeffs = np.polyfit(X, Y_obs, 1)
    x_line = np.linspace(-3, 3, 100)
    ax1.plot(x_line, coeffs[0] * x_line + coeffs[1], 'r-', linewidth=2,
            label=f'Observational: slope = {coeffs[0]:.2f}')
    ax1.axhline(y=0, color='green', linestyle='--', linewidth=2,
               label='Causal effect: slope = 0.0')
    
    ax1.set_xlabel('X (Treatment)', fontsize=12)
    ax1.set_ylabel('Y (Outcome)', fontsize=12)
    ax1.set_title('Confounding Bias: E[Y|X] ≠ E[Y|do(X)]',
                 fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # =========================================
    # Plot 2: Back-Door Adjustment
    # =========================================
    ax2 = fig.add_subplot(gs[0, 1])
    
    # After adjusting for Z, the effect disappears
    # E[Y|do(X)] = Σ_z E[Y|X,Z=z] P(Z=z)
    z_bins = np.linspace(-3, 3, 6)
    adjusted_slopes = []
    for i in range(len(z_bins) - 1):
        mask = (Z >= z_bins[i]) & (Z < z_bins[i + 1])
        if mask.sum() > 10:
            c = np.polyfit(X[mask], Y_obs[mask], 1)
            adjusted_slopes.append(c[0])
            ax2.scatter(X[mask], Y_obs[mask], alpha=0.3, s=10,
                       label=f'Z ∈ [{z_bins[i]:.1f}, {z_bins[i+1]:.1f})')
    
    avg_adjusted = np.mean(adjusted_slopes)
    ax2.axhline(y=0, color='green', linestyle='--', linewidth=2)
    ax2.set_xlabel('X (Treatment)', fontsize=12)
    ax2.set_ylabel('Y (Outcome)', fontsize=12)
    ax2.set_title(f'Back-Door Adjustment (avg slope: {avg_adjusted:.2f})',
                 fontsize=14, fontweight='bold')
    ax2.legend(fontsize=8, loc='upper left')
    ax2.grid(True, alpha=0.3)
    
    # =========================================
    # Plot 3: Manski Bounds
    # =========================================
    ax3 = fig.add_subplot(gs[1, 0])
    
    p_treated_range = np.linspace(0.1, 0.9, 50)
    E_Y1_treated = 0.7
    E_Y0_control = 0.3
    
    lower = p_treated_range * E_Y1_treated - (p_treated_range * 1 + (1 - p_treated_range) * E_Y0_control)
    upper = p_treated_range * E_Y1_treated + (1 - p_treated_range) - (1 - p_treated_range) * E_Y0_control
    
    ax3.fill_between(p_treated_range * 100, lower, upper, alpha=0.3, color='#FF9800',
                     label='Identification region')
    ax3.plot(p_treated_range * 100, lower, '#FF9800', linewidth=2)
    ax3.plot(p_treated_range * 100, upper, '#FF9800', linewidth=2)
    ax3.axhline(y=E_Y1_treated - E_Y0_control, color='green', linestyle='--',
               linewidth=2, label=f'True ATE = {E_Y1_treated - E_Y0_control:.1f}')
    
    ax3.set_xlabel('Proportion Treated (%)', fontsize=12)
    ax3.set_ylabel('Average Treatment Effect', fontsize=12)
    ax3.set_title('Manski Bounds: Partial Identification',
                 fontsize=14, fontweight='bold')
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3)
    
    # =========================================
    # Plot 4: Weak vs Strong Instruments
    # =========================================
    ax4 = fig.add_subplot(gs[1, 1])
    
    cov_ZX_values = np.linspace(0.05, 2.0, 100)
    sigma = 1.0
    iv_variance = sigma**2 / cov_ZX_values**2
    
    ax4.semilogy(cov_ZX_values, iv_variance, '#9C27B0', linewidth=3)
    ax4.axvline(x=0.3, color='red', linestyle='--', alpha=0.5)
    ax4.annotate('Weak instrument\nzone', xy=(0.15, 50), fontsize=10, color='red')
    ax4.axvline(x=1.0, color='green', linestyle='--', alpha=0.5)
    ax4.annotate('Strong\ninstrument', xy=(1.2, 0.5), fontsize=10, color='green')
    
    ax4.set_xlabel('Instrument Strength |Cov(Z,X)|', fontsize=12)
    ax4.set_ylabel('IV Estimator Variance', fontsize=12)
    ax4.set_title('Weak Instrument Problem', fontsize=14, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    fig.suptitle('Formally Verified: Causal Prediction Theory',
                fontsize=16, fontweight='bold', y=0.98)
    
    plt.savefig('/workspace/request-project/PredictionTheory/demos/causal_prediction.png',
               dpi=150, bbox_inches='tight')
    plt.close()
    print("✓ Saved causal_prediction.png")


if __name__ == '__main__':
    main()

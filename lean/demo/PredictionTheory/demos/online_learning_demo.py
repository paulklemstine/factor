"""
Demonstration: Online Learning and Adversarial Prediction

Simulates the multiplicative weights algorithm and visualizes:
1. Expert weight evolution over time
2. Regret growth vs. theoretical bound
3. Online-to-batch conversion
4. Adversarial robustness landscape

All bounds are formally verified in Lean 4.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec


def multiplicative_weights(n_experts, T, losses, eta):
    """Run multiplicative weights algorithm."""
    weights = np.ones(n_experts) / n_experts
    predictions = []
    cumulative_losses = np.zeros(n_experts)
    weight_history = [weights.copy()]
    regrets = []
    
    for t in range(T):
        # Predict: weighted average
        prediction = np.dot(weights, losses[t])
        predictions.append(prediction)
        
        # Update weights
        cumulative_losses += losses[t]
        weights = np.exp(-eta * cumulative_losses)
        weights /= weights.sum()
        weight_history.append(weights.copy())
        
        # Compute regret
        best_expert_loss = cumulative_losses.min()
        total_loss = sum(predictions)
        regrets.append(total_loss - best_expert_loss)
    
    return predictions, np.array(weight_history), regrets


def main():
    fig = plt.figure(figsize=(16, 12))
    gs = GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.3)
    
    np.random.seed(42)
    
    # Setup
    n_experts = 5
    T = 200
    
    # Generate losses: expert 0 is best, but others are sometimes better
    losses = np.random.rand(T, n_experts) * 0.8 + 0.1
    # Expert 0 has lower average loss
    losses[:, 0] *= 0.6
    # Expert 1 is good in the second half
    losses[T//2:, 1] *= 0.5
    
    eta_opt = np.sqrt(8 * np.log(n_experts) / T)
    
    predictions, weight_history, regrets = multiplicative_weights(
        n_experts, T, losses, eta_opt)
    
    # =========================================
    # Plot 1: Expert Weights Over Time
    # =========================================
    ax1 = fig.add_subplot(gs[0, 0])
    
    colors = ['#2196F3', '#4CAF50', '#FF9800', '#F44336', '#9C27B0']
    for i in range(n_experts):
        ax1.plot(weight_history[:, i], color=colors[i], linewidth=2,
                label=f'Expert {i+1}', alpha=0.8)
    
    ax1.set_xlabel('Round (t)', fontsize=12)
    ax1.set_ylabel('Weight', fontsize=12)
    ax1.set_title('Expert Weights: Multiplicative Weights Update',
                 fontsize=14, fontweight='bold')
    ax1.legend(fontsize=9, loc='upper right')
    ax1.grid(True, alpha=0.3)
    
    # =========================================
    # Plot 2: Regret vs. Theoretical Bound
    # =========================================
    ax2 = fig.add_subplot(gs[0, 1])
    
    ts = np.arange(1, T + 1)
    theoretical_bound = np.sqrt(ts * np.log(n_experts) / 2)
    
    ax2.plot(ts, regrets, color='#2196F3', linewidth=2, label='Actual regret')
    ax2.plot(ts, theoretical_bound, 'r--', linewidth=2,
            label=r'Bound: $\sqrt{T \log(n)/2}$')
    
    ax2.set_xlabel('Round (T)', fontsize=12)
    ax2.set_ylabel('Cumulative Regret', fontsize=12)
    ax2.set_title('Regret Growth (Verified Bound)', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3)
    
    # =========================================
    # Plot 3: Online-to-Batch Conversion
    # =========================================
    ax3 = fig.add_subplot(gs[1, 0])
    
    avg_regrets = np.array(regrets) / ts
    avg_bound = np.sqrt(np.log(n_experts) / (2 * ts))
    
    ax3.plot(ts, avg_regrets, color='#4CAF50', linewidth=2,
            label='Average regret')
    ax3.plot(ts, avg_bound, 'r--', linewidth=2,
            label=r'Bound: $\sqrt{\log(n)/(2T)}$')
    ax3.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
    
    ax3.set_xlabel('Round (T)', fontsize=12)
    ax3.set_ylabel('Average Regret', fontsize=12)
    ax3.set_title('Online-to-Batch: Average Regret → 0',
                 fontsize=14, fontweight='bold')
    ax3.legend(fontsize=11)
    ax3.grid(True, alpha=0.3)
    ax3.set_ylim(-0.5, 2)
    
    # =========================================
    # Plot 4: Optimal Learning Rate
    # =========================================
    ax4 = fig.add_subplot(gs[1, 1])
    
    etas = np.linspace(0.01, 2.0, 100)
    Ts = [50, 100, 200, 500]
    colors_T = ['#2196F3', '#4CAF50', '#FF9800', '#F44336']
    
    for T_val, color in zip(Ts, colors_T):
        regret_bound = np.log(n_experts) / etas + etas * T_val / 8
        eta_star = np.sqrt(8 * np.log(n_experts) / T_val)
        min_regret = np.sqrt(T_val * np.log(n_experts) / 2)
        
        ax4.plot(etas, regret_bound, color=color, linewidth=2,
                label=f'T={T_val}')
        ax4.plot(eta_star, min_regret, 'o', color=color, markersize=8)
    
    ax4.set_xlabel('Learning Rate (η)', fontsize=12)
    ax4.set_ylabel('Regret Bound', fontsize=12)
    ax4.set_title('Optimal Learning Rate η* = √(8 log n / T)',
                 fontsize=14, fontweight='bold')
    ax4.legend(fontsize=10)
    ax4.set_ylim(0, 50)
    ax4.grid(True, alpha=0.3)
    
    fig.suptitle('Formally Verified: Online Learning Prediction Framework',
                fontsize=16, fontweight='bold', y=0.98)
    
    plt.savefig('/workspace/request-project/PredictionTheory/demos/online_learning.png',
               dpi=150, bbox_inches='tight')
    plt.close()
    print("✓ Saved online_learning.png")


if __name__ == '__main__':
    main()

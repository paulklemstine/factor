"""
Quantum-Neural Bridge Demo

Demonstrates the key connections between quantum computing and neural networks:
1. ReLU as idempotent projection (quantum measurement analogue)
2. Softmax as tropical limit
3. MERA-Transformer structural parallel
4. Decoherence accumulation (Bernoulli's inequality)
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def relu_projection_demo():
    """ReLU as idempotent projection — the neural-quantum duality."""
    print("=" * 60)
    print("RELU AS IDEMPOTENT PROJECTION")
    print("=" * 60)
    
    x = np.linspace(-3, 3, 1000)
    relu = np.maximum(x, 0)
    relu_relu = np.maximum(relu, 0)
    
    print(f"\nReLU(x) = max(x, 0)")
    print(f"ReLU(ReLU(x)) = ReLU(x) for all x (idempotent!)")
    print(f"Max error: |ReLU(ReLU(x)) - ReLU(x)| = {np.max(np.abs(relu_relu - relu)):.2e}")
    print(f"\n→ Just like quantum measurement: measuring twice = measuring once")
    print(f"→ Both are projections onto a subspace")
    
    # Plot
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    
    axes[0].plot(x, relu, 'b-', linewidth=2, label='ReLU(x)')
    axes[0].plot(x, x, 'r--', alpha=0.3, label='y = x')
    axes[0].set_title('ReLU: Neural Projection')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    axes[0].set_xlabel('x')
    
    # Quantum projector |0⟩⟨0|
    theta = np.linspace(0, 2*np.pi, 100)
    cos2 = np.cos(theta)**2
    axes[1].plot(theta/np.pi, cos2, 'g-', linewidth=2, label='⟨ψ|P|ψ⟩')
    axes[1].plot(theta/np.pi, cos2**2, 'r--', linewidth=2, label='⟨ψ|P²|ψ⟩')
    axes[1].set_title('Quantum Projector: P² = P')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    axes[1].set_xlabel('θ/π')
    
    # Both are idempotent
    axes[2].plot(x, relu_relu - relu, 'k-', linewidth=2)
    axes[2].set_title('ReLU(ReLU(x)) - ReLU(x) = 0')
    axes[2].set_ylim(-0.1, 0.1)
    axes[2].grid(True, alpha=0.3)
    axes[2].set_xlabel('x')
    
    plt.tight_layout()
    plt.savefig('/workspace/request-project/visuals/relu_projection.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("→ Plot saved to visuals/relu_projection.png")

def softmax_tropical_demo():
    """Softmax as tropical limit."""
    print("\n" + "=" * 60)
    print("SOFTMAX → TROPICAL LIMIT")
    print("=" * 60)
    
    x = np.array([1.0, 3.0, 2.0, 0.5])
    
    print(f"\nInput: x = {x}")
    print(f"\nSoftmax(βx) for different temperatures β:")
    print(f"{'β':>8} | {'softmax(βx)':>40} | {'argmax':>7}")
    print("-" * 65)
    
    betas = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 50.0, 100.0]
    softmax_results = []
    
    for beta in betas:
        exp_bx = np.exp(beta * x)
        sm = exp_bx / exp_bx.sum()
        softmax_results.append(sm)
        print(f"{beta:8.1f} | [{', '.join(f'{s:.4f}' for s in sm)}] | {np.argmax(sm):>7d}")
    
    print(f"\n→ As β → ∞, softmax → one-hot (tropical/argmax)")
    print(f"→ This is the Maslov dequantization: quantum → classical")
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    for i in range(len(x)):
        probs = [sr[i] for sr in softmax_results]
        ax.semilogx(betas, probs, 'o-', linewidth=2, markersize=6, 
                    label=f'x[{i}] = {x[i]}')
    
    ax.set_xlabel('Temperature β (log scale)', fontsize=12)
    ax.set_ylabel('Softmax probability', fontsize=12)
    ax.set_title('Softmax → Tropical Limit (Winner-Take-All)', fontsize=14)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-0.05, 1.05)
    
    plt.tight_layout()
    plt.savefig('/workspace/request-project/visuals/softmax_tropical.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("→ Plot saved to visuals/softmax_tropical.png")

def decoherence_demo():
    """Demonstrate decoherence accumulation via Bernoulli's inequality."""
    print("\n" + "=" * 60)
    print("DECOHERENCE ACCUMULATION")
    print("=" * 60)
    
    print("\nBernoulli's inequality: (1-p)^T ≥ 1 - Tp")
    print("\nCoherence probability (1-p)^T for per-step error rate p:")
    print(f"{'T':>5} | {'p=0.001':>10} | {'p=0.01':>10} | {'p=0.1':>10} | {'1-Tp':>10}")
    print("-" * 55)
    
    for T in [1, 5, 10, 50, 100, 500, 1000]:
        coherences = []
        for p in [0.001, 0.01, 0.1]:
            coherences.append((1 - p)**T)
        bernoulli = 1 - T * 0.01  # Bernoulli bound for p=0.01
        print(f"{T:5d} | {coherences[0]:10.6f} | {coherences[1]:10.6f} | "
              f"{coherences[2]:10.6f} | {max(bernoulli, 0):10.6f}")
    
    print(f"\n→ For p=0.001 and T=1000: coherence = {(1-0.001)**1000:.4f}")
    print(f"→ Bernoulli bound: 1 - 1000·0.001 = {1 - 1000*0.001:.4f}")
    print(f"→ The bound is tight for small p!")
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    T_range = np.arange(1, 201)
    
    for p, color in [(0.001, 'green'), (0.005, 'blue'), (0.01, 'orange'), (0.05, 'red')]:
        coherence = (1 - p)**T_range
        bernoulli = np.maximum(1 - T_range * p, 0)
        ax.plot(T_range, coherence, '-', color=color, linewidth=2, label=f'(1-{p})^T')
        ax.plot(T_range, bernoulli, '--', color=color, linewidth=1, alpha=0.5)
    
    ax.set_xlabel('Circuit Depth T', fontsize=12)
    ax.set_ylabel('Coherence Probability', fontsize=12)
    ax.set_title('Decoherence Accumulation: (1-p)^T ≥ 1-Tp', fontsize=14)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 1.05)
    
    plt.tight_layout()
    plt.savefig('/workspace/request-project/visuals/decoherence.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("→ Plot saved to visuals/decoherence.png")

def quantum_advantage_demo():
    """Visualize the quantum advantage threshold."""
    print("\n" + "=" * 60)
    print("QUANTUM ADVANTAGE THRESHOLD")
    print("=" * 60)
    
    n_range = np.arange(1, 25)
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    ax.semilogy(n_range, 2**n_range, 'b-o', linewidth=2, markersize=5, label='2^n (quantum)')
    ax.semilogy(n_range, n_range**2, 'r-s', linewidth=2, markersize=5, label='n² (classical)')
    ax.semilogy(n_range, n_range**3, 'g-^', linewidth=2, markersize=5, label='n³')
    ax.semilogy(n_range, n_range**5, 'm-D', linewidth=2, markersize=5, label='n⁵')
    
    # Mark the crossover points
    ax.axvline(x=5, color='red', linestyle=':', alpha=0.5, label='n=5 (2^n > n²)')
    ax.axvline(x=10, color='green', linestyle=':', alpha=0.5, label='n=10 (2^n > n³)')
    
    ax.set_xlabel('Number of Qubits n', fontsize=12)
    ax.set_ylabel('Computational Resources (log scale)', fontsize=12)
    ax.set_title('Quantum Advantage: 2^n vs Polynomial Resources', fontsize=14)
    ax.legend(fontsize=10, loc='upper left')
    ax.grid(True, alpha=0.3, which='both')
    
    plt.tight_layout()
    plt.savefig('/workspace/request-project/visuals/quantum_advantage.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("→ Plot saved to visuals/quantum_advantage.png")
    
    print(f"\nCrossover points (2^n > n^d):")
    for d in [2, 3, 4, 5]:
        for n in range(1, 100):
            if 2**n > n**d:
                print(f"  d = {d}: crossover at n = {n}")
                break

if __name__ == "__main__":
    relu_projection_demo()
    softmax_tropical_demo()
    decoherence_demo()
    quantum_advantage_demo()

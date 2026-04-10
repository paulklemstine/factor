"""
Hilbert-Pólya Operator Demo: Discrete Model of the Riemann Hypothesis

This demo constructs the normalized adjacency operator A/√q for various
graphs and demonstrates:
1. The Ihara zeta function zeros from graph eigenvalues
2. The Ramanujan bound |λ/√q| ≤ 2
3. The "critical line" for graph zeta zeros
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from itertools import product

def petersen_graph():
    """The Petersen graph: a 3-regular graph on 10 vertices."""
    adj = np.zeros((10, 10))
    # Outer cycle
    for i in range(5):
        adj[i][(i+1) % 5] = 1
        adj[(i+1) % 5][i] = 1
    # Inner pentagram
    for i in range(5):
        adj[5+i][5+(i+2) % 5] = 1
        adj[5+(i+2) % 5][5+i] = 1
    # Spokes
    for i in range(5):
        adj[i][5+i] = 1
        adj[5+i][i] = 1
    return adj, 2  # q = 2 (since regularity = q+1 = 3)

def complete_bipartite(m, n):
    """Complete bipartite graph K_{m,n}."""
    N = m + n
    adj = np.zeros((N, N))
    for i in range(m):
        for j in range(m, N):
            adj[i][j] = 1
            adj[j][i] = 1
    return adj, None  # Not regular in general

def cycle_graph(n):
    """Cycle graph C_n: 2-regular."""
    adj = np.zeros((n, n))
    for i in range(n):
        adj[i][(i+1) % n] = 1
        adj[(i+1) % n][i] = 1
    return adj, 1  # q = 1 (regularity = 2)

def random_regular_graph(n, d):
    """Generate a random d-regular graph on n vertices (approximately)."""
    adj = np.zeros((n, n))
    stubs = list(range(n)) * d
    np.random.shuffle(stubs)
    for i in range(0, len(stubs), 2):
        if i + 1 < len(stubs):
            u, v = stubs[i], stubs[i+1]
            if u != v:
                adj[u][v] = 1
                adj[v][u] = 1
    return adj, d - 1

def ihara_zeros(eigenvalues, q):
    """
    Compute Ihara zeta zeros from eigenvalues.
    For each eigenvalue λ, the zeros satisfy: q*u² - λ*u + 1 = 0
    u = (λ ± √(λ² - 4q)) / (2q)
    """
    zeros = []
    for lam in eigenvalues:
        discriminant = lam**2 - 4*q
        if discriminant >= 0:
            u1 = (lam + np.sqrt(discriminant)) / (2*q)
            u2 = (lam - np.sqrt(discriminant)) / (2*q)
            zeros.append(complex(u1, 0))
            zeros.append(complex(u2, 0))
        else:
            real_part = lam / (2*q)
            imag_part = np.sqrt(-discriminant) / (2*q)
            zeros.append(complex(real_part, imag_part))
            zeros.append(complex(real_part, -imag_part))
    return zeros

def hilbert_polya_operator(adj, q):
    """Construct the Hilbert-Pólya operator A/√q."""
    return adj / np.sqrt(q)

def demo_spectral_analysis():
    """Analyze spectra and Ihara zeros for several graphs."""
    print("=" * 70)
    print("HILBERT-PÓLYA OPERATOR: DISCRETE MODEL OF RIEMANN HYPOTHESIS")
    print("=" * 70)
    
    graphs = {
        "Petersen Graph (3-regular)": petersen_graph(),
        "Cycle C₁₂ (2-regular)": cycle_graph(12),
        "Cycle C₇ (2-regular)": cycle_graph(7),
    }
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    for idx, (name, (adj, q)) in enumerate(graphs.items()):
        eigenvalues = np.linalg.eigvalsh(adj)
        reg = int(q + 1)
        ramanujan_bound = 2 * np.sqrt(q)
        
        print(f"\n{name}")
        print(f"  Regularity: {reg}, q = {q}")
        print(f"  Eigenvalues: {np.sort(eigenvalues)[::-1]}")
        print(f"  Ramanujan bound: |λ| ≤ 2√q = {ramanujan_bound:.4f}")
        
        # Check Ramanujan property
        nontrivial = [ev for ev in eigenvalues 
                      if abs(abs(ev) - (q+1)) > 0.01]
        is_ramanujan = all(abs(ev) <= ramanujan_bound + 0.01 
                          for ev in nontrivial)
        print(f"  Is Ramanujan: {is_ramanujan}")
        
        # Hilbert-Pólya spectrum
        hp_eigenvalues = eigenvalues / np.sqrt(q)
        print(f"  HP spectrum (A/√q): {np.sort(hp_eigenvalues)[::-1]}")
        print(f"  HP bound: |λ/√q| ≤ 2: {all(abs(ev) <= 2.01 for ev in hp_eigenvalues if abs(abs(ev*np.sqrt(q)) - (q+1)) > 0.01)}")
        
        # Ihara zeros
        zeros = ihara_zeros(eigenvalues, q)
        
        # Plot Ihara zeros in complex plane
        ax = axes[idx]
        real_parts = [z.real for z in zeros]
        imag_parts = [z.imag for z in zeros]
        ax.scatter(real_parts, imag_parts, c='blue', s=50, zorder=5)
        
        # Draw critical line Re(u) = 1/(2q)... actually for the graph case
        # the "critical strip" is centered differently
        critical_x = 1/(2*q) if q > 0 else 0
        ax.axvline(x=critical_x, color='red', linestyle='--', alpha=0.5,
                   label=f'Re(u)=1/(2q)={critical_x:.3f}')
        
        ax.set_xlabel('Re(u)')
        ax.set_ylabel('Im(u)')
        ax.set_title(name)
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
    
    plt.tight_layout()
    plt.savefig('/workspace/request-project/LanglandsBridges/output/hilbert_polya_zeros.png', 
                dpi=150, bbox_inches='tight')
    print("\n[Saved: hilbert_polya_zeros.png]")

def demo_psd_laplacian():
    """Demonstrate the Laplacian PSD property v^T L v ≥ 0."""
    print("\n" + "=" * 70)
    print("LAPLACIAN POSITIVE SEMI-DEFINITENESS")
    print("=" * 70)
    
    adj, _ = petersen_graph()
    n = adj.shape[0]
    D = np.diag(adj.sum(axis=1))
    L = D - adj
    
    print(f"\nPetersen Graph Laplacian eigenvalues: {np.sort(np.linalg.eigvalsh(L))}")
    
    # Test PSD with random vectors
    num_tests = 1000
    min_quadratic = float('inf')
    for _ in range(num_tests):
        v = np.random.randn(n)
        qform = v @ L @ v
        min_quadratic = min(min_quadratic, qform)
    
    print(f"Minimum v^T L v over {num_tests} random vectors: {min_quadratic:.6f}")
    print(f"PSD verified: {min_quadratic >= -1e-10}")
    
    # Verify the identity: v^T L v = (1/2) Σ A_ij (v_i - v_j)²
    v = np.random.randn(n)
    lhs = v @ L @ v
    rhs = 0.5 * sum(adj[i,j] * (v[i] - v[j])**2 
                     for i in range(n) for j in range(n))
    print(f"\nIdentity check: v^T L v = (1/2)Σ A_ij(v_i-v_j)²")
    print(f"  LHS = {lhs:.10f}")
    print(f"  RHS = {rhs:.10f}")
    print(f"  Match: {abs(lhs - rhs) < 1e-10}")

if __name__ == "__main__":
    demo_spectral_analysis()
    demo_psd_laplacian()
    print("\nDone!")

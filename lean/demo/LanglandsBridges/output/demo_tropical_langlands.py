"""
Tropical Langlands Demo: Tropicalization of Curves

Demonstrates:
1. Tropical arithmetic (min, +)
2. Tropicalization of algebraic curves
3. Baker-Norine chip-firing
4. Tropical Jacobians and divisor theory
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import defaultdict

# --- Tropical Arithmetic ---

class TropicalNumber:
    """A number in the tropical semiring (ℝ ∪ {∞}, min, +)."""
    def __init__(self, val):
        self.val = val  # float or float('inf')
    
    def __add__(self, other):
        """Tropical addition = min."""
        return TropicalNumber(min(self.val, other.val))
    
    def __mul__(self, other):
        """Tropical multiplication = ordinary addition."""
        if self.val == float('inf') or other.val == float('inf'):
            return TropicalNumber(float('inf'))
        return TropicalNumber(self.val + other.val)
    
    def __repr__(self):
        if self.val == float('inf'):
            return "∞"
        return f"{self.val}"
    
    def __eq__(self, other):
        return self.val == other.val

def demo_tropical_arithmetic():
    """Demonstrate tropical arithmetic operations."""
    print("=" * 70)
    print("TROPICAL ARITHMETIC: (ℝ ∪ {∞}, min, +)")
    print("=" * 70)
    
    a = TropicalNumber(3)
    b = TropicalNumber(5)
    c = TropicalNumber(2)
    inf = TropicalNumber(float('inf'))
    zero = TropicalNumber(0)
    
    print(f"\nTropical addition (min):")
    print(f"  {a} ⊕ {b} = {a + b}  (min(3,5) = 3)")
    print(f"  {a} ⊕ {c} = {a + c}  (min(3,2) = 2)")
    print(f"  {a} ⊕ ∞ = {a + inf}  (min(3,∞) = 3) [∞ is additive identity]")
    
    print(f"\nTropical multiplication (addition):")
    print(f"  {a} ⊙ {b} = {a * b}  (3+5 = 8)")
    print(f"  {a} ⊙ {c} = {a * c}  (3+2 = 5)")
    print(f"  {a} ⊙ 0 = {a * zero}  (3+0 = 3) [0 is multiplicative identity]")
    print(f"  {a} ⊙ ∞ = {a * inf}  (3+∞ = ∞)")
    
    # Verify commutativity and associativity
    print(f"\nCommutativity: {a} ⊕ {b} = {a+b}, {b} ⊕ {a} = {b+a}: {a+b == b+a}")
    print(f"Associativity: ({a} ⊕ {b}) ⊕ {c} = {(a+b)+c}, {a} ⊕ ({b} ⊕ {c}) = {a+(b+c)}: {(a+b)+c == a+(b+c)}")

# --- Metric Graphs ---

class MetricGraph:
    """A metric graph (1-dimensional polyhedral complex)."""
    def __init__(self, num_vertices, edges, edge_lengths):
        self.num_vertices = num_vertices
        self.edges = edges  # list of (u, v) pairs
        self.edge_lengths = edge_lengths
        self.num_edges = len(edges)
        
        # Build adjacency
        self.adj = defaultdict(list)
        for i, (u, v) in enumerate(edges):
            self.adj[u].append((v, i))
            self.adj[v].append((u, i))
    
    def genus(self):
        """g = |E| - |V| + 1"""
        return self.num_edges - self.num_vertices + 1
    
    def valence(self, v):
        """Degree of vertex v."""
        return len(self.adj[v])
    
    def laplacian(self):
        """Compute the graph Laplacian."""
        n = self.num_vertices
        L = np.zeros((n, n), dtype=int)
        for u, v in self.edges:
            L[u][v] -= 1
            L[v][u] -= 1
            L[u][u] += 1
            L[v][v] += 1
        return L
    
    def canonical_divisor(self):
        """K(v) = val(v) - 2."""
        return {v: self.valence(v) - 2 for v in range(self.num_vertices)}
    
    def divisor_degree(self, D):
        """deg(D) = Σ D(v)."""
        return sum(D.values())

def demo_chip_firing():
    """Demonstrate chip-firing on a graph."""
    print("\n" + "=" * 70)
    print("CHIP-FIRING AND TROPICAL JACOBIANS")
    print("=" * 70)
    
    # Complete graph K4
    edges = [(0,1), (0,2), (0,3), (1,2), (1,3), (2,3)]
    lengths = [1.0] * 6
    G = MetricGraph(4, edges, lengths)
    
    print(f"\nGraph: K₄ (complete graph on 4 vertices)")
    print(f"  Vertices: {G.num_vertices}, Edges: {G.num_edges}")
    print(f"  Genus g = |E| - |V| + 1 = {G.genus()}")
    print(f"  Valences: {[G.valence(v) for v in range(G.num_vertices)]}")
    
    # Canonical divisor
    K = G.canonical_divisor()
    print(f"\nCanonical divisor K(v) = val(v) - 2:")
    print(f"  K = {dict(K)}")
    print(f"  deg(K) = {G.divisor_degree(K)} (expected: 2g-2 = {2*G.genus()-2})")
    
    # Laplacian
    L = G.laplacian()
    print(f"\nLaplacian:\n{L}")
    print(f"  Row sums: {L.sum(axis=1)} (should be 0)")
    
    eigenvalues = np.sort(np.linalg.eigvalsh(L.astype(float)))
    print(f"  Eigenvalues: {eigenvalues}")
    print(f"  Smallest eigenvalue: {eigenvalues[0]:.6f} (should be 0)")
    
    # Chip-firing simulation
    D = {0: 3, 1: 0, 2: 0, 3: 0}  # All chips on vertex 0
    print(f"\nChip-firing simulation:")
    print(f"  Initial divisor: {D}, degree = {sum(D.values())}")
    
    for step in range(4):
        # Fire vertex with most chips
        v = max(D, key=D.get)
        if D[v] < G.valence(v):
            print(f"  No vertex can fire (need val(v) chips)")
            break
        
        # Fire v: send 1 chip along each edge
        new_D = dict(D)
        new_D[v] -= G.valence(v)
        for u, _ in G.adj[v]:
            new_D[u] = new_D.get(u, 0) + 1
        
        print(f"  Fire vertex {v}: {D} → {new_D}, degree = {sum(new_D.values())}")
        D = new_D

def demo_tropical_curve():
    """Visualize tropicalization of a curve."""
    print("\n" + "=" * 70)
    print("TROPICAL CURVE VISUALIZATION")
    print("=" * 70)
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # Example 1: Tropical line (max(x, y, 0))
    ax = axes[0]
    x = np.linspace(-3, 3, 300)
    y = np.linspace(-3, 3, 300)
    X, Y = np.meshgrid(x, y)
    
    # Tropical line: corner locus of max(x, y, 0)
    # Segments: x=y≥0, x=0≥y, y=0≥x
    ax.plot([0, 3], [0, 3], 'b-', linewidth=3, label='x = y ≥ 0')
    ax.plot([0, -3], [0, 0], 'b-', linewidth=3, label='y = 0 ≥ x')
    ax.plot([0, 0], [0, -3], 'b-', linewidth=3, label='x = 0 ≥ y')
    ax.plot(0, 0, 'ro', markersize=10, zorder=5)
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title('Tropical Line\n(genus 0)')
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')
    
    # Example 2: Tropical elliptic curve (genus 1)
    ax = axes[1]
    # A genus-1 tropical curve looks like a cycle with rays
    theta = np.linspace(0, 2*np.pi, 100)
    cx, cy = np.cos(theta), np.sin(theta)
    ax.plot(cx, cy, 'b-', linewidth=3)
    # Add rays
    for angle in [0, 2*np.pi/3, 4*np.pi/3]:
        x0, y0 = np.cos(angle), np.sin(angle)
        dx, dy = np.cos(angle), np.sin(angle)
        ax.plot([x0, x0+2*dx], [y0, y0+2*dy], 'b-', linewidth=3)
        ax.plot(x0, y0, 'ro', markersize=8, zorder=5)
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title('Tropical Elliptic Curve\n(genus 1, Jac ≅ S¹)')
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')
    
    # Example 3: Tropical genus-2 curve
    ax = axes[2]
    # Two cycles connected by an edge
    t = np.linspace(0, 2*np.pi, 100)
    ax.plot(np.cos(t) - 1.5, np.sin(t), 'b-', linewidth=3)
    ax.plot(np.cos(t) + 1.5, np.sin(t), 'b-', linewidth=3)
    ax.plot([-0.5, 0.5], [0, 0], 'b-', linewidth=3)
    # Add rays
    for cx_offset in [-1.5, 1.5]:
        for angle in [np.pi/2, -np.pi/2]:
            x0 = cx_offset + np.cos(angle)
            y0 = np.sin(angle)
            ax.plot([x0, x0], [y0, y0 + np.sign(y0)*1.5], 'b-', linewidth=3)
            ax.plot(x0, y0, 'ro', markersize=8, zorder=5)
    
    ax.plot(-0.5, 0, 'ro', markersize=8, zorder=5)
    ax.plot(0.5, 0, 'ro', markersize=8, zorder=5)
    ax.set_xlim(-4, 4)
    ax.set_ylim(-3, 3)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title('Tropical Genus-2 Curve\n(genus 2, Jac ≅ T²)')
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')
    
    plt.tight_layout()
    plt.savefig('/workspace/request-project/LanglandsBridges/output/tropical_curves.png',
                dpi=150, bbox_inches='tight')
    print("[Saved: tropical_curves.png]")

if __name__ == "__main__":
    demo_tropical_arithmetic()
    demo_chip_firing()
    demo_tropical_curve()
    print("\nAll tropical demos completed!")

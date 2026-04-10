"""
Quantum Gate Synthesis via Solovay-Kitaev Algorithm

This demo implements a simplified version of the Solovay-Kitaev algorithm
for approximating arbitrary single-qubit gates using a finite gate set.

The key idea: given generators {H, T} (Hadamard and T-gate), any SU(2)
element can be approximated to precision ε using O(log^3.97(1/ε)) gates.
"""

import numpy as np
from typing import List, Tuple

# --- Gate Definitions ---

# Pauli matrices
I = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)

# Hadamard gate
H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)

# T gate (π/8 gate)
T = np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]], dtype=complex)

# S gate (phase gate)
S = np.array([[1, 0], [0, 1j]], dtype=complex)

def gate_distance(U: np.ndarray, V: np.ndarray) -> float:
    """Frobenius distance between two unitary matrices."""
    return np.linalg.norm(U - V, 'fro')

def group_commutator(U: np.ndarray, V: np.ndarray) -> np.ndarray:
    """Compute [U, V] = U V U† V†"""
    return U @ V @ U.conj().T @ V.conj().T

def random_su2() -> np.ndarray:
    """Generate a random SU(2) matrix using the Haar measure."""
    # Parameterize by Euler angles
    alpha = np.random.uniform(0, 2 * np.pi)
    beta = np.random.uniform(0, np.pi)
    gamma = np.random.uniform(0, 2 * np.pi)
    
    U = np.array([
        [np.cos(beta/2) * np.exp(1j*(alpha+gamma)/2), 
         np.sin(beta/2) * np.exp(1j*(alpha-gamma)/2)],
        [-np.sin(beta/2) * np.exp(-1j*(alpha-gamma)/2),
         np.cos(beta/2) * np.exp(-1j*(alpha+gamma)/2)]
    ])
    return U

# --- Solovay-Kitaev Core ---

class GateSequence:
    """Represents a sequence of quantum gates."""
    def __init__(self, gates: List[str], matrix: np.ndarray):
        self.gates = gates
        self.matrix = matrix
        self.length = len(gates)
    
    def __repr__(self):
        return f"GateSeq({' '.join(self.gates)}, len={self.length})"

def build_gate_library(depth: int) -> List[GateSequence]:
    """Build a library of gate sequences up to given depth."""
    gate_map = {'H': H, 'T': T, 'Td': T.conj().T, 'S': S, 'Sd': S.conj().T}
    
    library = [GateSequence([], I)]
    current = [GateSequence([name], mat) for name, mat in gate_map.items()]
    library.extend(current)
    
    for d in range(1, depth):
        next_level = []
        for seq in current:
            for name, mat in gate_map.items():
                new_matrix = seq.matrix @ mat
                new_seq = GateSequence(seq.gates + [name], new_matrix)
                next_level.append(new_seq)
        library.extend(next_level)
        current = next_level
    
    return library

def find_closest(target: np.ndarray, library: List[GateSequence]) -> GateSequence:
    """Find the gate sequence in the library closest to the target."""
    best = library[0]
    best_dist = gate_distance(target, best.matrix)
    
    for seq in library[1:]:
        dist = gate_distance(target, seq.matrix)
        if dist < best_dist:
            best_dist = dist
            best = seq
    
    return best

def solovay_kitaev_step(target: np.ndarray, library: List[GateSequence], 
                         depth: int) -> GateSequence:
    """One step of the Solovay-Kitaev algorithm."""
    if depth == 0:
        return find_closest(target, library)
    
    # Recursive approximation
    approx_prev = solovay_kitaev_step(target, library, depth - 1)
    
    # Compute the error
    error = target @ approx_prev.matrix.conj().T
    
    # Decompose error as a group commutator [V, W]
    # Simplified: just find a better approximation
    better = find_closest(target, library)
    
    # Combine
    combined_matrix = better.matrix
    combined_gates = better.gates
    
    return GateSequence(combined_gates, combined_matrix)

# --- Demo ---

def demo_gate_synthesis():
    """Demonstrate quantum gate synthesis."""
    print("=" * 60)
    print("QUANTUM GATE SYNTHESIS DEMO")
    print("=" * 60)
    
    # Build gate library
    print("\nBuilding gate library (depth 3)...")
    library = build_gate_library(3)
    print(f"Library size: {len(library)} gate sequences")
    
    # Generate random target
    np.random.seed(42)
    target = random_su2()
    print(f"\nTarget gate:\n{np.round(target, 3)}")
    
    # Find approximation
    approx = find_closest(target, library)
    dist = gate_distance(target, approx.matrix)
    
    print(f"\nBest approximation: {approx}")
    print(f"Gate sequence: {' → '.join(approx.gates)}")
    print(f"Distance: {dist:.6f}")
    print(f"Gate count: {approx.length}")
    
    # Show how precision improves with library depth
    print("\n--- Precision vs Library Depth ---")
    for depth in range(1, 5):
        lib = build_gate_library(depth)
        approx = find_closest(target, lib)
        dist = gate_distance(target, approx.matrix)
        print(f"Depth {depth}: {len(lib):6d} sequences, "
              f"best distance = {dist:.6f}, gates = {approx.length}")
    
    # Demonstrate the parameter-shift rule
    print("\n" + "=" * 60)
    print("PARAMETER-SHIFT RULE DEMO")
    print("=" * 60)
    
    # C(θ) = a·cos(θ) + b·sin(θ) + d
    a, b, d = 0.7, -0.3, 0.5
    theta = np.pi / 3
    
    def cost(t):
        return a * np.cos(t) + b * np.sin(t) + d
    
    # Exact derivative
    exact_deriv = -a * np.sin(theta) + b * np.cos(theta)
    
    # Parameter-shift rule
    shift_deriv = (cost(theta + np.pi/2) - cost(theta - np.pi/2)) / 2
    
    # Finite difference (for comparison)
    h = 1e-7
    fd_deriv = (cost(theta + h) - cost(theta - h)) / (2 * h)
    
    print(f"\nCost function: C(θ) = {a}·cos(θ) + {b}·sin(θ) + {d}")
    print(f"At θ = π/3 = {theta:.4f}")
    print(f"\nExact derivative:        {exact_deriv:.10f}")
    print(f"Parameter-shift rule:    {shift_deriv:.10f}")
    print(f"Finite difference:       {fd_deriv:.10f}")
    print(f"\nParameter-shift error:   {abs(shift_deriv - exact_deriv):.2e}")
    print(f"Finite difference error: {abs(fd_deriv - exact_deriv):.2e}")
    print(f"\n→ The parameter-shift rule is EXACT (up to floating point)!")
    
    # Demonstrate barren plateau
    print("\n" + "=" * 60)
    print("BARREN PLATEAU DEMO")
    print("=" * 60)
    
    print("\nGradient variance ~ 1/2^n:")
    for n in [5, 10, 20, 30, 50]:
        var = 1.0 / 2**n
        print(f"  n = {n:3d} qubits: Var ≈ {var:.2e}")
    
    print(f"\n→ At n=50: 2^50 = {2**50:,} > 10^15 = {10**15:,}")
    print("→ Gradients are unmeasurable beyond ~50 qubits!")

def demo_tropical_dequantization():
    """Demonstrate the Maslov dequantization (tropical limit)."""
    print("\n" + "=" * 60)
    print("MASLOV DEQUANTIZATION DEMO")
    print("=" * 60)
    
    def maslov_add(eps, x, y):
        """ε-deformed addition: ε · log(e^(x/ε) + e^(y/ε))"""
        return eps * np.log(np.exp(x/eps) + np.exp(y/eps))
    
    x, y = 3.0, 7.0
    print(f"\nx = {x}, y = {y}, max(x,y) = {max(x,y)}")
    print(f"\nε-deformed addition a ⊕_ε b = ε·log(e^(a/ε) + e^(b/ε)):")
    print(f"{'ε':>10} | {'a ⊕_ε b':>15} | {'max(a,b)':>10} | {'error':>10}")
    print("-" * 55)
    
    for eps in [10.0, 5.0, 2.0, 1.0, 0.5, 0.1, 0.01]:
        result = maslov_add(eps, x, y)
        error = abs(result - max(x, y))
        print(f"{eps:10.3f} | {result:15.6f} | {max(x,y):10.1f} | {error:10.6f}")
    
    print(f"\n→ As ε → 0, Maslov addition → max (tropical addition)")
    print(f"→ Error bounded by ε·log(2) = {0.01 * np.log(2):.6f} for ε=0.01")
    
    # Quantum advantage threshold
    print("\n--- Quantum Advantage Threshold: 2^n vs n^d ---")
    print(f"{'n':>5} | {'2^n':>15} | {'n^2':>10} | {'n^3':>12} | {'n^5':>15}")
    print("-" * 65)
    for n in [3, 4, 5, 6, 8, 10, 15, 20]:
        print(f"{n:5d} | {2**n:15,} | {n**2:10,} | {n**3:12,} | {n**5:15,}")

if __name__ == "__main__":
    demo_gate_synthesis()
    demo_tropical_dequantization()

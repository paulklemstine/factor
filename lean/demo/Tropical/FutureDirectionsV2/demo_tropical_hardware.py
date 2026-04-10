#!/usr/bin/env python3
"""
Tropical Hardware & Complexity Demo
=====================================
Demonstrates tropical circuits, gate complexity, and the connection
between tropical matrix algebra and hardware design.

Key concepts:
1. Tropical circuit simulation
2. Gate count analysis (max vs add gates)
3. Tropical vs classical circuit cost comparison
4. Tropical L-function computation
"""

import numpy as np
from itertools import permutations
import time

# =============================================================================
# 1. TROPICAL CIRCUIT SIMULATOR
# =============================================================================

class TropicalCircuit:
    """
    A tropical circuit with max-gates and add-gates.
    
    In the tropical semiring:
    - "multiplication" = addition of reals
    - "addition" = max of reals
    
    So a tropical circuit uses only max and + gates,
    eliminating classical multiplier units entirely.
    """
    
    def __init__(self, num_inputs):
        self.num_inputs = num_inputs
        self.gates = []  # (type, left_idx, right_idx)
        self.values = [0.0] * num_inputs
    
    def add_max_gate(self, left, right):
        """Add a max gate: output = max(left, right)."""
        idx = self.num_inputs + len(self.gates)
        self.gates.append(('max', left, right))
        return idx
    
    def add_add_gate(self, left, right):
        """Add an add gate: output = left + right."""
        idx = self.num_inputs + len(self.gates)
        self.gates.append(('add', left, right))
        return idx
    
    def evaluate(self, inputs):
        """Evaluate the circuit on given inputs."""
        values = list(inputs)
        for gate_type, left, right in self.gates:
            if gate_type == 'max':
                values.append(max(values[left], values[right]))
            else:  # add
                values.append(values[left] + values[right])
        return values
    
    @property
    def num_gates(self):
        return len(self.gates)
    
    @property
    def max_gate_count(self):
        return sum(1 for g in self.gates if g[0] == 'max')
    
    @property
    def add_gate_count(self):
        return sum(1 for g in self.gates if g[0] == 'add')

print("=" * 70)
print("TROPICAL CIRCUIT SIMULATOR")
print("=" * 70)

# Build a circuit computing max(x0, x1, x2, x3) using 3 max-gates
circuit = TropicalCircuit(4)
m01 = circuit.add_max_gate(0, 1)  # max(x0, x1)
m23 = circuit.add_max_gate(2, 3)  # max(x2, x3)
m_all = circuit.add_max_gate(m01, m23)  # max of all 4

inputs = [3.0, 7.0, 1.0, 5.0]
values = circuit.evaluate(inputs)

print(f"\nCircuit: max(x0, x1, x2, x3)")
print(f"Inputs: {inputs}")
print(f"Output: {values[-1]}")
print(f"Expected: {max(inputs)}")
print(f"\nGate decomposition (gate_count_decomp theorem):")
print(f"  Max gates: {circuit.max_gate_count}")
print(f"  Add gates: {circuit.add_gate_count}")
print(f"  Total:     {circuit.num_gates}")
print(f"  max + add = total? {circuit.max_gate_count + circuit.add_gate_count == circuit.num_gates}")

# =============================================================================
# 2. TROPICAL INNER PRODUCT CIRCUIT
# =============================================================================

print("\n" + "=" * 70)
print("TROPICAL INNER PRODUCT CIRCUIT")
print("=" * 70)

# Classical inner product: sum_i x_i * y_i  (needs n multiplies + n-1 adds)
# Tropical inner product: max_i (x_i + y_i)  (needs n adds + n-1 maxes)

def build_tropical_inner_product(n):
    """Build a circuit for tropical inner product of two n-vectors."""
    circuit = TropicalCircuit(2 * n)  # x0..x_{n-1}, y0..y_{n-1}
    
    # First: compute x_i + y_i for each i (n add-gates)
    sums = []
    for i in range(n):
        s = circuit.add_add_gate(i, n + i)  # x_i + y_i
        sums.append(s)
    
    # Then: compute max of all sums (n-1 max-gates)
    current = sums[0]
    for i in range(1, n):
        current = circuit.add_max_gate(current, sums[i])
    
    return circuit

n = 4
circuit = build_tropical_inner_product(n)
x = [1.0, 3.0, 2.0, 5.0]
y = [4.0, 1.0, 6.0, 2.0]
inputs = x + y
values = circuit.evaluate(inputs)

print(f"\nTropical inner product of x and y:")
print(f"  x = {x}")
print(f"  y = {y}")
print(f"  ⟨x, y⟩_trop = max_i(x_i + y_i) = {values[-1]}")
print(f"  Components: {[x[i]+y[i] for i in range(n)]}")
print(f"  Max: {max(x[i]+y[i] for i in range(n))}")
print(f"\nGate counts:")
print(f"  Add gates (= n = {n}): {circuit.add_gate_count}")
print(f"  Max gates (= n-1 = {n-1}): {circuit.max_gate_count}")
print(f"  Total: {circuit.num_gates}")

# =============================================================================
# 3. HARDWARE COST COMPARISON
# =============================================================================

print("\n" + "=" * 70)
print("HARDWARE COST: TROPICAL vs CLASSICAL")
print("=" * 70)

print(f"\nFor n-bit operands:")
print(f"{'Operation':<25} {'Classical Gates':<20} {'Tropical Gates':<20} {'Savings'}")
print(f"{'-'*85}")

for bits in [8, 16, 32, 64]:
    # Classical multiply: O(n^2) gates (schoolbook), O(n log n) (Karatsuba)
    classical_mul = bits * bits  # schoolbook
    tropical_add = bits  # ripple-carry adder
    savings = (1 - tropical_add / classical_mul) * 100
    
    print(f"{'Multiply→Add':<25} {classical_mul:<20} {tropical_add:<20} {savings:.1f}%")

print()
for bits in [8, 16, 32, 64]:
    # Classical add: O(n) gates
    classical_add = bits  # ripple-carry
    tropical_max = bits  # comparator
    
    print(f"{'Add→Max':<25} {classical_add:<20} {tropical_max:<20} {'~same'}")

print(f"\nKey insight: The big win is replacing multipliers (O(n²)) with adders (O(n)).")
print(f"Max (comparator) and add have similar cost, so the savings come from")
print(f"eliminating the most expensive component in classical arithmetic.")

# =============================================================================
# 4. TROPICAL L-FUNCTION COMPUTATION
# =============================================================================

print("\n" + "=" * 70)
print("TROPICAL L-FUNCTION")
print("=" * 70)

def trop_L_function(local_factors, N):
    """Tropical L-function: sum of first N local factors."""
    return sum(local_factors[:N])

# Example: local factors as log of prime reciprocals
primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
local_factors = [np.log(p) for p in primes]

print(f"\nLocal factors = log(p) for primes p:")
for i, (p, f) in enumerate(zip(primes, local_factors)):
    print(f"  f({i}) = log({p}) = {f:.4f}")

print(f"\nTropical L-function values:")
for N in range(1, len(primes) + 1):
    L = trop_L_function(local_factors, N)
    print(f"  L_trop(f, {N:2d}) = {L:.4f}")

# Verify monotonicity (tropLFunction_mono)
print(f"\n--- Monotonicity Check (tropLFunction_mono) ---")
for M in range(len(primes)):
    for N in range(M, len(primes) + 1):
        LM = trop_L_function(local_factors, M)
        LN = trop_L_function(local_factors, N)
        if LM > LN:
            print(f"  VIOLATION: L({M}) = {LM} > L({N}) = {LN}")
            break
else:
    print(f"  All M ≤ N satisfy L(M) ≤ L(N) ✓")

# Verify Euler product (tropLFunction_euler)
print(f"\n--- Euler Product Check (tropLFunction_euler) ---")
for N in range(len(primes)):
    L_N = trop_L_function(local_factors, N)
    L_N1 = trop_L_function(local_factors, N + 1)
    diff = L_N1 - L_N
    print(f"  L({N+1}) - L({N}) = {diff:.4f}, f({N}) = {local_factors[N]:.4f}, match? {abs(diff - local_factors[N]) < 1e-10}")

# =============================================================================
# 5. BENCHMARKING TROPICAL VS CLASSICAL MATMUL
# =============================================================================

print("\n" + "=" * 70)
print("PERFORMANCE: TROPICAL vs CLASSICAL MATRIX MULTIPLY")
print("=" * 70)

def trop_matmul_np(A, B):
    """Tropical matrix multiply using numpy broadcasting."""
    m, n = A.shape
    _, p = B.shape
    # A[:, :, None] + B[None, :, :] gives all A_ik + B_kj
    return np.max(A[:, :, np.newaxis] + B[np.newaxis, :, :], axis=1)

sizes = [10, 50, 100, 200]
print(f"\n{'Size':<10} {'Classical (ms)':<18} {'Tropical (ms)':<18} {'Ratio'}")
print(f"{'-'*60}")

for n in sizes:
    A = np.random.randn(n, n)
    B = np.random.randn(n, n)
    
    # Classical
    t0 = time.perf_counter()
    for _ in range(10):
        _ = A @ B
    t_classical = (time.perf_counter() - t0) / 10 * 1000
    
    # Tropical
    t0 = time.perf_counter()
    for _ in range(10):
        _ = trop_matmul_np(A, B)
    t_tropical = (time.perf_counter() - t0) / 10 * 1000
    
    ratio = t_tropical / t_classical if t_classical > 0 else float('inf')
    print(f"{n:<10} {t_classical:<18.3f} {t_tropical:<18.3f} {ratio:.2f}x")

print(f"\nNote: In software, tropical matmul is slower due to the max operation")
print(f"not benefiting from BLAS optimization. In dedicated hardware (FPGA/ASIC),")
print(f"tropical matmul would be faster since max is cheaper than multiply.")

print("\n" + "=" * 70)
print("ALL HARDWARE & COMPLEXITY DEMOS COMPLETED")
print("=" * 70)

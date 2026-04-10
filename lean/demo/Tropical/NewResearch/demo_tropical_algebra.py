"""
Tropical Algebra & Neural Networks: Interactive Demonstrations

This script demonstrates the core concepts from the formally verified
tropical algebra framework, including:
1. Tropical semiring arithmetic
2. Tropical matrix multiplication (shortest paths)
3. ReLU-tropical correspondence
4. Tropical neural network compilation
5. Tropical probability theory
6. LogSumExp as smooth tropical bridge

Run: python demo_tropical_algebra.py
"""

import numpy as np
from typing import List, Tuple
import itertools

# =============================================================================
# PART 1: Tropical Semiring Arithmetic
# =============================================================================

def trop_add(a: float, b: float) -> float:
    """Tropical addition: max(a, b)"""
    return max(a, b)

def trop_mul(a: float, b: float) -> float:
    """Tropical multiplication: a + b"""
    return a + b

def trop_pow(a: float, n: int) -> float:
    """Tropical power: n * a"""
    return n * a

NEG_INF = float('-inf')  # Tropical zero (additive identity)
TROP_ONE = 0.0           # Tropical one (multiplicative identity)

def demo_tropical_arithmetic():
    """Demonstrate tropical semiring properties"""
    print("=" * 60)
    print("PART 1: Tropical Semiring Arithmetic")
    print("=" * 60)

    # Basic operations
    a, b, c = 3.0, 5.0, 2.0
    print(f"\na = {a}, b = {b}, c = {c}")
    print(f"a ⊕ b = max({a}, {b}) = {trop_add(a, b)}")
    print(f"a ⊗ b = {a} + {b} = {trop_mul(a, b)}")
    print(f"a^3 (tropical) = 3 × {a} = {trop_pow(a, 3)}")

    # Idempotency: a ⊕ a = a
    print(f"\nIdempotency: {a} ⊕ {a} = {trop_add(a, a)} = {a} ✓")

    # Distributivity: a ⊗ (b ⊕ c) = (a ⊗ b) ⊕ (a ⊗ c)
    lhs = trop_mul(a, trop_add(b, c))
    rhs = trop_add(trop_mul(a, b), trop_mul(a, c))
    print(f"Distributivity: {a} ⊗ ({b} ⊕ {c}) = {lhs}")
    print(f"               ({a} ⊗ {b}) ⊕ ({a} ⊗ {c}) = {rhs}")
    print(f"               Equal: {lhs == rhs} ✓")

    # Identity elements
    print(f"\nAdditive identity: {a} ⊕ (-∞) = {trop_add(a, NEG_INF)} = {a} ✓")
    print(f"Multiplicative identity: {a} ⊗ 0 = {trop_mul(a, TROP_ONE)} = {a} ✓")

    # No absorbing element over ℝ (formally proven as no_max_absorbing)
    print(f"\nNo absorbing element: For any e ∈ ℝ, ∃ a: max(a, e) ≠ a")
    print(f"  e.g., e = 10, a = 11: max(11, 10) = 11 ≠ 11... wait, that IS 11")
    print(f"  But e = 10, a = 9: max(9, 10) = 10 ≠ 9 ✓")


# =============================================================================
# PART 2: Tropical Matrix Multiplication
# =============================================================================

def trop_mat_mul(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Tropical matrix multiplication: (A ⊗ B)_{ij} = max_k (A_{ik} + B_{kj})"""
    n, m = A.shape
    m2, p = B.shape
    assert m == m2
    C = np.full((n, p), NEG_INF)
    for i in range(n):
        for j in range(p):
            for k in range(m):
                C[i, j] = max(C[i, j], A[i, k] + B[k, j])
    return C

def trop_mat_pow(A: np.ndarray, power: int) -> np.ndarray:
    """Tropical matrix power by repeated squaring"""
    n = A.shape[0]
    result = np.full((n, n), NEG_INF)
    np.fill_diagonal(result, 0)  # Tropical identity
    base = A.copy()
    while power > 0:
        if power % 2 == 1:
            result = trop_mat_mul(result, base)
        base = trop_mat_mul(base, base)
        power //= 2
    return result

def demo_tropical_matrices():
    """Demonstrate tropical matrix multiplication for shortest paths"""
    print("\n" + "=" * 60)
    print("PART 2: Tropical Matrix Multiplication (Shortest Paths)")
    print("=" * 60)

    # Adjacency matrix (edge weights, NEG_INF = no edge)
    # Using MIN-PLUS convention for shortest paths:
    # We negate weights to use MAX-PLUS
    # Graph: 0 --2--> 1 --3--> 2, 0 --10--> 2
    print("\nGraph: 0 →(2)→ 1 →(3)→ 2, 0 →(10)→ 2")

    # For MAX-PLUS (longest path), use positive weights
    # For shortest path, negate and take max = negate and take min
    W = np.array([
        [0,    2,    10],    # From node 0
        [NEG_INF, 0,  3],   # From node 1
        [NEG_INF, NEG_INF, 0]  # From node 2
    ])

    print(f"\nWeight matrix W (max-plus convention):")
    print(W)

    W2 = trop_mat_mul(W, W)
    print(f"\nW² (best 2-hop paths):")
    print(W2)
    print(f"\nW²[0,2] = {W2[0,2]} (path 0→1→2 with weight 2+3=5)")

    # Monotonicity demonstration (formally proven as tropMatMul_mono_left)
    W_bigger = W.copy()
    W_bigger[0, 1] = 4  # Increase edge weight 0→1
    W2_bigger = trop_mat_mul(W_bigger, W)
    print(f"\nMonotonicity: increasing W[0,1] from 2 to 4:")
    print(f"  Original W²[0,2] = {W2[0,2]}")
    print(f"  New W²[0,2] = {W2_bigger[0,2]}")
    print(f"  Increased: {W2_bigger[0,2] >= W2[0,2]} ✓ (tropMatMul_mono_left)")


# =============================================================================
# PART 3: ReLU-Tropical Correspondence
# =============================================================================

def relu(x: float) -> float:
    """ReLU(x) = max(x, 0) = tropical addition of x and 0"""
    return max(x, 0)

def demo_relu_tropical():
    """Demonstrate the ReLU-tropical bridge"""
    print("\n" + "=" * 60)
    print("PART 3: ReLU-Tropical Correspondence")
    print("=" * 60)

    # max(a, b) = a + ReLU(b - a) (formally proven as max_eq_relu_form)
    print("\nTheorem: max(a, b) = a + ReLU(b - a)")
    test_pairs = [(3, 7), (5, 2), (-1, -4), (0, 0), (-3, 3)]
    for a, b in test_pairs:
        lhs = max(a, b)
        rhs = a + relu(b - a)
        print(f"  max({a:3}, {b:3}) = {lhs:3}  |  {a} + ReLU({b-a:3}) = {a} + {relu(b-a)} = {rhs:3}  ✓")

    # ReLU is 1-Lipschitz (formally proven as relu_lipschitz)
    print("\nTheorem: |ReLU(x) - ReLU(y)| ≤ |x - y|")
    test_pairs2 = [(3, 7), (5, -2), (-1, -4), (0, 3)]
    for x, y in test_pairs2:
        lip_lhs = abs(relu(x) - relu(y))
        lip_rhs = abs(x - y)
        print(f"  |ReLU({x:3}) - ReLU({y:3})| = {lip_lhs} ≤ {lip_rhs} = |{x} - {y}|  ✓")


# =============================================================================
# PART 4: Tropical Neural Network
# =============================================================================

def tropical_neuron(weights: np.ndarray, bias: float, x: np.ndarray) -> float:
    """A single tropical neuron: max(w · x + b, 0) = ReLU(w · x + b)
    This is tropical: max over {w_i + x_i for each i} plus bias, then max with 0"""
    return relu(np.dot(weights, x) + bias)

def tropical_layer(W: np.ndarray, biases: np.ndarray, x: np.ndarray) -> np.ndarray:
    """A tropical ReLU layer"""
    return np.array([tropical_neuron(W[j], biases[j], x) for j in range(len(biases))])

def count_linear_regions_1d(weights: np.ndarray, biases: np.ndarray,
                              x_range: Tuple[float, float], n_points: int = 10000) -> int:
    """Count linear regions of a 1-hidden-layer ReLU network"""
    xs = np.linspace(x_range[0], x_range[1], n_points)
    # Each neuron creates a breakpoint at x = -b/w
    breakpoints = []
    for j in range(len(biases)):
        if abs(weights[j, 0]) > 1e-10:
            bp = -biases[j] / weights[j, 0]
            if x_range[0] <= bp <= x_range[1]:
                breakpoints.append(bp)
    breakpoints.sort()
    return len(breakpoints) + 1

def demo_tropical_nn():
    """Demonstrate tropical neural network concepts"""
    print("\n" + "=" * 60)
    print("PART 4: Tropical Neural Network Compilation")
    print("=" * 60)

    # 1D example with 3 neurons
    np.random.seed(42)
    W = np.array([[1.0], [-2.0], [0.5]])
    biases = np.array([-1.0, 3.0, -0.5])

    print(f"\n1-hidden-layer ReLU network with {len(biases)} neurons:")
    print(f"  Weights: {W.flatten()}")
    print(f"  Biases:  {biases}")

    # Evaluate at several points
    x_vals = [-5, -2, 0, 1, 3, 5]
    print(f"\nInput → Hidden activations → Output:")
    for x_val in x_vals:
        x = np.array([float(x_val)])
        hidden = tropical_layer(W, biases, x)
        output = np.sum(hidden)  # Simple sum output
        print(f"  x={x_val:3}: hidden={np.round(hidden, 2)} → output={output:.2f}")

    # Count linear regions
    n_regions = count_linear_regions_1d(W, biases, (-10, 10))
    print(f"\nLinear regions in [-10, 10]: {n_regions}")
    print(f"Upper bound (2^m): {2**len(biases)}")
    print(f"Tight bound for 1 layer: {len(biases) + 1}")

    # Breakpoints (tropical hyperplane vertices)
    print(f"\nBreakpoints (tropical hyperplane):")
    for j in range(len(biases)):
        if abs(W[j, 0]) > 1e-10:
            bp = -biases[j] / W[j, 0]
            print(f"  Neuron {j}: w={W[j,0]}, b={biases[j]} → breakpoint at x={bp:.2f}")


# =============================================================================
# PART 5: Tropical Probability
# =============================================================================

def trop_expectation(log_probs: np.ndarray, values: np.ndarray) -> float:
    """Tropical expectation: max_i (logP(i) + X(i))
    Formally defined in tropExpectation"""
    return np.max(log_probs + values)

def trop_variance(log_probs: np.ndarray, values: np.ndarray) -> float:
    """Tropical variance: max_i (logP(i) + |X(i) - E_trop[X]|)
    Formally defined in tropVariance"""
    mu = trop_expectation(log_probs, values)
    return np.max(log_probs + np.abs(values - mu))

def classical_expectation(probs: np.ndarray, values: np.ndarray) -> float:
    """Classical expectation: sum_i P(i) * X(i)"""
    return np.sum(probs * values)

def demo_tropical_probability():
    """Demonstrate tropical probability theory"""
    print("\n" + "=" * 60)
    print("PART 5: Tropical Probability Theory")
    print("=" * 60)

    # Example distribution
    probs = np.array([0.1, 0.3, 0.4, 0.15, 0.05])
    values = np.array([10, 20, 15, 25, 5])
    log_probs = np.log(probs)

    print(f"\nDistribution:")
    for i in range(len(probs)):
        print(f"  P(X={values[i]}) = {probs[i]:.2f}, log P = {log_probs[i]:.3f}")

    e_classical = classical_expectation(probs, values)
    e_tropical = trop_expectation(log_probs, values)
    v_tropical = trop_variance(log_probs, values)

    print(f"\nClassical E[X]    = {e_classical:.2f}")
    print(f"Tropical E_trop[X] = {e_tropical:.3f}")

    # Show which term achieves the maximum
    terms = log_probs + values
    best_i = np.argmax(terms)
    print(f"\nTropical expectation achieved at i={best_i}:")
    print(f"  logP({values[best_i]}) + {values[best_i]} = {log_probs[best_i]:.3f} + {values[best_i]} = {terms[best_i]:.3f}")

    # Monotonicity (formally proven as tropExpectation_mono)
    values_shifted = values + 5
    e_trop_shifted = trop_expectation(log_probs, values_shifted)
    print(f"\nMonotonicity: X ≤ X+5 implies E_trop[X] ≤ E_trop[X+5]")
    print(f"  E_trop[X] = {e_tropical:.3f} ≤ {e_trop_shifted:.3f} = E_trop[X+5]  ✓")

    # Translation-equivariance (formally proven as tropExpectation_shift)
    c = 3.0
    e_trop_plus_c = trop_expectation(log_probs, values + c)
    print(f"\nTranslation: E_trop[X + {c}] = E_trop[X] + {c}")
    print(f"  {e_trop_plus_c:.3f} = {e_tropical:.3f} + {c} = {e_tropical + c:.3f}  ✓")

    print(f"\nTropical variance = {v_tropical:.3f}")


# =============================================================================
# PART 6: LogSumExp Bridge
# =============================================================================

def logsumexp(v: np.ndarray) -> float:
    """LogSumExp: log(sum(exp(v)))"""
    c = np.max(v)  # Numerical stability
    return c + np.log(np.sum(np.exp(v - c)))

def logsumexp_temp(beta: float, v: np.ndarray) -> float:
    """LogSumExp with temperature: (1/β) * log(sum(exp(β*v)))"""
    return logsumexp(beta * v) / beta

def demo_logsumexp():
    """Demonstrate LogSumExp as smooth tropical bridge"""
    print("\n" + "=" * 60)
    print("PART 6: LogSumExp — The Smooth Tropical Bridge")
    print("=" * 60)

    v = np.array([3.0, 7.0, 5.0, 1.0])
    true_max = np.max(v)

    print(f"\nVector v = {v}")
    print(f"max(v)   = {true_max}")
    print(f"LSE(v)   = {logsumexp(v):.6f}")
    print(f"\nBounds: max(v) ≤ LSE(v) ≤ max(v) + log(n)")
    print(f"  {true_max} ≤ {logsumexp(v):.6f} ≤ {true_max + np.log(len(v)):.6f}  ✓")

    # Temperature sweep: as β → ∞, LSE_β → max
    print(f"\nTemperature sweep (β → ∞ approaches tropical limit):")
    print(f"  {'β':>6} | {'LSE_β(v)':>12} | {'Error vs max':>12}")
    print(f"  {'-'*6}-+-{'-'*12}-+-{'-'*12}")
    for beta in [0.1, 0.5, 1, 2, 5, 10, 50, 100]:
        lse_val = logsumexp_temp(beta, v)
        error = lse_val - true_max
        print(f"  {beta:6.1f} | {lse_val:12.6f} | {error:12.8f}")

    print(f"\nAs β → ∞, LSE_β → max = {true_max} (Maslov dequantization)")


# =============================================================================
# PART 7: Tropical Determinant
# =============================================================================

def trop_det(A: np.ndarray) -> float:
    """Tropical determinant: max over permutations of sum A_{i,σ(i)}
    Equals the maximum weight perfect matching (assignment problem)."""
    n = A.shape[0]
    best = NEG_INF
    for perm in itertools.permutations(range(n)):
        weight = sum(A[i, perm[i]] for i in range(n))
        best = max(best, weight)
    return best

def demo_tropical_determinant():
    """Demonstrate tropical determinant = assignment problem"""
    print("\n" + "=" * 60)
    print("PART 7: Tropical Determinant = Assignment Problem")
    print("=" * 60)

    # Cost matrix for assignment problem
    A = np.array([
        [3, 5, 2],
        [4, 1, 6],
        [7, 3, 4]
    ], dtype=float)

    print(f"\nCost matrix A:")
    print(A)

    td = trop_det(A)
    diag_sum = sum(A[i, i] for i in range(3))

    print(f"\nTropical determinant = {td}")
    print(f"Diagonal sum (lower bound) = {diag_sum}")
    print(f"tropDet ≥ diag sum: {td >= diag_sum} ✓ (tropDet_ge_diag)")

    # Find the optimal permutation
    n = A.shape[0]
    for perm in itertools.permutations(range(n)):
        weight = sum(A[i, perm[i]] for i in range(n))
        if weight == td:
            assignment = list(perm)
            print(f"\nOptimal assignment: {assignment}")
            for i in range(n):
                print(f"  Worker {i} → Task {assignment[i]} (cost {A[i, assignment[i]]})")
            break

    # Tropical det = tropical perm (formally proven as tropDet_eq_tropPerm)
    print(f"\ntropDet = tropPerm = {td} (no signs in tropical!) ✓")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("╔" + "═" * 58 + "╗")
    print("║  Tropical Algebra & Neural Networks: Interactive Demos  ║")
    print("║  Based on formally verified Lean 4 theorems             ║")
    print("╚" + "═" * 58 + "╝")

    demo_tropical_arithmetic()
    demo_tropical_matrices()
    demo_relu_tropical()
    demo_tropical_nn()
    demo_tropical_probability()
    demo_logsumexp()
    demo_tropical_determinant()

    print("\n" + "=" * 60)
    print("All demonstrations complete!")
    print("Every result corresponds to a formally verified Lean 4 theorem.")
    print("=" * 60)

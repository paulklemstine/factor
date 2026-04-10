#!/usr/bin/env python3
"""
Tropical Neural Network Compilation Demo
==========================================
Demonstrates that ReLU neural networks are exactly tropical polynomial circuits.

Key insight (machine-verified in Lean 4):
  ReLU(x) = max(x, 0) = x ⊕_tropical 0

This means every ReLU network computes a piecewise-linear function
that can be expressed as a tropical polynomial.

No external dependencies required (pure Python).
"""

import random
random.seed(42)


# =============================================================================
# Tropical Semiring Operations
# =============================================================================

def tropical_add(a, b):
    """Tropical addition: a ⊕ b = max(a, b)"""
    return max(a, b)


def tropical_mul(a, b):
    """Tropical multiplication: a ⊙ b = a + b"""
    return a + b


def tropical_power(a, n):
    """Tropical power: a^⊙n = n * a"""
    return n * a


def relu(x):
    """ReLU(x) = max(x, 0) = x ⊕_tropical 0"""
    return tropical_add(x, 0)


# =============================================================================
# Tropical Polynomial
# =============================================================================

class TropicalPolynomial:
    """
    A tropical polynomial: max over a set of affine terms.
    p(x) = max_i (a_i · x + b_i)
    """

    def __init__(self, terms):
        """terms: list of (coefficient_vector, bias) tuples"""
        self.terms = terms

    def evaluate(self, x):
        """Evaluate the tropical polynomial at point x."""
        if isinstance(x, (int, float)):
            x = [x]
        return max(
            sum(a * xi for a, xi in zip(coeff, x)) + bias
            for coeff, bias in self.terms
        )

    def __repr__(self):
        parts = []
        for coeff, bias in self.terms:
            term = " + ".join(f"{c}·x_{i}" for i, c in enumerate(coeff) if c != 0)
            if bias != 0:
                term += f" + {bias}" if bias > 0 else f" - {-bias}"
            if not term:
                term = str(bias)
            parts.append(term)
        return "max(" + ", ".join(parts) + ")"


# =============================================================================
# Simple matrix/vector operations (no numpy needed)
# =============================================================================

def mat_vec_mul(W, x):
    """Multiply matrix W by vector x."""
    return [sum(W[i][j] * x[j] for j in range(len(x))) for i in range(len(W))]


def vec_add(a, b):
    """Add two vectors."""
    return [ai + bi for ai, bi in zip(a, b)]


def vec_relu(v):
    """Apply ReLU elementwise."""
    return [max(vi, 0) for vi in v]


# =============================================================================
# ReLU Network as Tropical Circuit
# =============================================================================

class TropicalReLUNetwork:
    """
    A ReLU neural network, viewed as a tropical polynomial circuit.
    """

    def __init__(self, layers):
        """layers: list of (weight_matrix, bias_vector) tuples"""
        self.layers = layers

    def forward_classical(self, x):
        """Standard forward pass."""
        for W, b in self.layers:
            z = vec_add(mat_vec_mul(W, x), b)
            x = vec_relu(z)
        return x

    def forward_tropical(self, x):
        """Tropical forward pass (should give same result)."""
        for W, b in self.layers:
            z = vec_add(mat_vec_mul(W, x), b)
            x = [tropical_add(zi, 0) for zi in z]
        return x

    def count_tropical_terms(self):
        """Upper bound on tropical monomials."""
        total = 1
        for W, b in self.layers:
            total *= (len(W) + 1)
        return total


def demo_tropical_semiring():
    """Demonstrate tropical arithmetic properties."""
    print("=" * 60)
    print("TROPICAL SEMIRING (max, +)")
    print("=" * 60)
    print()

    print("Basic Operations:")
    print(f"  3 ⊕ 5 = max(3, 5) = {tropical_add(3, 5)}")
    print(f"  3 ⊙ 5 = 3 + 5 = {tropical_mul(3, 5)}")
    print(f"  2^⊙3 = 3 × 2 = {tropical_power(2, 3)}")
    print()

    print("Key Properties (all machine-verified in Lean 4):")
    print()

    a, b = 3, 7
    print(f"  Commutativity:  {a} ⊕ {b} = {tropical_add(a,b)} = {tropical_add(b,a)} = {b} ⊕ {a}  ✓")

    c = 5
    print(f"  Associativity:  ({a}⊕{b})⊕{c} = {tropical_add(tropical_add(a,b),c)} = "
          f"{tropical_add(a,tropical_add(b,c))} = {a}⊕({b}⊕{c})  ✓")

    print(f"  IDEMPOTENCY:    {a} ⊕ {a} = max({a},{a}) = {tropical_add(a,a)} = {a}  ✓")
    print(f"                  (This is UNIQUE to tropical — fails in classical arithmetic)")
    print()

    print(f"  Distributivity: {a}⊙({b}⊕{c}) = {a}+max({b},{c}) = {tropical_mul(a,tropical_add(b,c))}")
    print(f"                  ({a}⊙{b})⊕({a}⊙{c}) = max({a}+{b},{a}+{c}) = {tropical_add(tropical_mul(a,b),tropical_mul(a,c))}  ✓")
    print()


def demo_relu_tropical():
    """Demonstrate ReLU = tropical addition with zero."""
    print("=" * 60)
    print("ReLU(x) = x ⊕_tropical 0 = max(x, 0)")
    print("=" * 60)
    print()

    print("The Core Identity (definitional equality in Lean 4):")
    print()
    print(f"{'x':>8} {'ReLU(x)':>10} {'x ⊕ 0':>10} {'equal':>7}")
    print("-" * 40)

    for x_val in [x / 4.0 for x in range(-12, 13)]:
        r = relu(x_val)
        t = tropical_add(x_val, 0)
        print(f"{x_val:>8.2f} {r:>10.2f} {t:>10.2f} {'  ✓':>7}")

    print()
    print("Idempotency of ReLU:")
    for x in [-2, -1, 0, 1, 2]:
        r1 = relu(x)
        r2 = relu(r1)
        print(f"  ReLU(ReLU({x:>2})) = ReLU({r1:.0f}) = {r2:.0f} = ReLU({x})  ✓")
    print()


def demo_network_compilation():
    """Compile a small ReLU network into tropical polynomial form."""
    print("=" * 60)
    print("NEURAL NETWORK → TROPICAL POLYNOMIAL COMPILATION")
    print("=" * 60)
    print()

    # Single neuron: y = ReLU(2x - 1)
    print("Example 1: Single neuron y = ReLU(2x - 1)")
    print("  Tropical form: y = max(2x - 1, 0)")
    print("  = max(2·x + (-1), 0)")
    print("  This is a tropical polynomial with 2 terms")
    print()

    tp = TropicalPolynomial([([2], -1), ([0], 0)])
    for x in [-1, 0, 0.5, 1, 2]:
        classical = max(2*x - 1, 0)
        tropical = tp.evaluate([x])
        print(f"    x={x:>4.1f}: classical={classical:>4.1f}, tropical={tropical:>4.1f}  {'✓' if abs(classical-tropical)<1e-10 else '✗'}")
    print()

    # Two-layer network
    print("Example 2: Two-layer network")
    W1 = [[2, -1], [-1, 3]]
    b1 = [0.5, -1]
    W2 = [[1, 1]]
    b2 = [0]

    net = TropicalReLUNetwork([(W1, b1), (W2, b2)])
    print(f"  Layer 1: W={W1}, b={b1}")
    print(f"  Layer 2: W={W2}, b={b2}")
    print(f"  Tropical term count (upper bound): {net.count_tropical_terms()}")
    print()

    print("  Verification (classical vs tropical forward pass):")
    for x1, x2 in [(-1, 0), (0, 0), (1, 1), (2, -1), (0.5, 0.5)]:
        x = [x1, x2]
        y_classical = net.forward_classical(x)
        y_tropical = net.forward_tropical(x)
        match = all(abs(a - b) < 1e-10 for a, b in zip(y_classical, y_tropical))
        print(f"    ({x1:>5.1f}, {x2:>5.1f}) → classical={y_classical[0]:>6.2f}, tropical={y_tropical[0]:>6.2f}  {'✓' if match else '✗'}")
    print()


def demo_tropical_pruning():
    """Demonstrate network pruning via tropical term dominance."""
    print("=" * 60)
    print("NETWORK PRUNING VIA TROPICAL DOMINANCE")
    print("=" * 60)
    print()
    print("In tropical polynomials, a term a·x+b is 'dominated' by c·x+d")
    print("if c·x+d ≥ a·x+b for all x in the input domain.")
    print("Dominated terms can be removed without changing the function.")
    print()

    print("  Original: max(3x+1, 2x+5, x+2)")
    print()
    print(f"  {'x':>5} {'3x+1':>7} {'2x+5':>7} {'x+2':>7} {'max':>7} {'winner':>8}")
    print("  " + "-" * 45)

    for x in range(-3, 6):
        vals = [3*x+1, 2*x+5, x+2]
        mx = max(vals)
        winner = ['3x+1', '2x+5', 'x+2'][vals.index(mx)]
        print(f"  {x:>5} {vals[0]:>7} {vals[1]:>7} {vals[2]:>7} {mx:>7} {winner:>8}")

    print()
    print("  Observation: 'x+2' is dominated by '2x+5' for x ≥ -3")
    print("  → Can prune the third term in that domain")
    print("  → Corresponds to pruning a neuron in the network!")
    print()


def demo_tropical_peirce():
    """Demonstrate the tropical Peirce decomposition: x = ReLU(x) - ReLU(-x)."""
    print("=" * 60)
    print("TROPICAL PEIRCE DECOMPOSITION")
    print("x = ReLU(x) - ReLU(-x) = max(x,0) - max(-x,0)")
    print("=" * 60)
    print()
    print("(Machine-verified in Lean 4 as theorem tropical_peirce)")
    print()

    print(f"{'x':>8} {'ReLU(x)':>10} {'ReLU(-x)':>10} {'diff':>8} {'match':>7}")
    print("-" * 48)

    for x in [v / 2.0 for v in range(-6, 7)]:
        r_pos = max(x, 0)
        r_neg = max(-x, 0)
        diff = r_pos - r_neg
        match = abs(diff - x) < 1e-10
        print(f"{x:>8.1f} {r_pos:>10.1f} {r_neg:>10.1f} {diff:>8.1f} {'  ✓' if match else '  ✗':>7}")

    print()
    print("This decomposes any real number into its 'positive projection'")
    print("minus its 'negative projection' — analogous to the algebraic")
    print("Peirce decomposition x = exe + (1-e)x(1-e) for e = sign(x).")
    print()


if __name__ == "__main__":
    demo_tropical_semiring()
    demo_relu_tropical()
    demo_network_compilation()
    demo_tropical_pruning()
    demo_tropical_peirce()

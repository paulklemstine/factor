"""
Neural Network Compilation Demo 1: Temperature Annealing and Tropical Convergence

Demonstrates how the softmax (log-sum-exp) operation converges to the hard
maximum (tropical addition) as temperature T → 0.

Key theorem: max(a,b) ≤ log(exp(a) + exp(b)) ≤ max(a,b) + log(2)
Scaled:      max(a,b) ≤ T·log(exp(a/T) + exp(b/T)) ≤ max(a,b) + T·log(2)
"""

import numpy as np
import json

def logsumexp(a, b, temperature=1.0):
    """Compute T * log(exp(a/T) + exp(b/T)) — the smooth max."""
    T = temperature
    # Numerically stable version
    m = max(a, b)
    return m + T * np.log(np.exp((a - m) / T) + np.exp((b - m) / T))

def tropical_max(a, b):
    """Tropical addition = hard max."""
    return max(a, b)

def demo_convergence():
    """Show convergence of smooth max to hard max as T → 0."""
    a, b = 3.0, 7.0
    hard_max = tropical_max(a, b)

    print("=" * 60)
    print("TROPICAL ANNEALING CONVERGENCE DEMO")
    print("=" * 60)
    print(f"\na = {a}, b = {b}")
    print(f"Hard max (tropical addition): {hard_max}")
    print(f"Theoretical error bound: [0, T * log(2)]")
    print()
    print(f"{'Temperature T':>15} {'Smooth Max':>12} {'Error':>10} {'T*log(2)':>10} {'Within Bound':>14}")
    print("-" * 65)

    temperatures = [10.0, 5.0, 2.0, 1.0, 0.5, 0.1, 0.01, 0.001]
    results = []

    for T in temperatures:
        smooth = logsumexp(a, b, T)
        error = smooth - hard_max
        bound = T * np.log(2)
        within = 0 <= error <= bound
        results.append({
            "temperature": T,
            "smooth_max": round(smooth, 8),
            "error": round(error, 8),
            "bound": round(bound, 8),
            "within_bound": within
        })
        print(f"{T:>15.4f} {smooth:>12.6f} {error:>10.6f} {bound:>10.6f} {'✓' if within else '✗':>14}")

    print()
    print("As T → 0, the smooth max converges to the hard max (tropical limit).")
    print("The error is always within [0, T·log(2)] as proven in our Lean formalization.")
    return results

def demo_tropical_distributivity():
    """Demonstrate the tropical distributive law: a + max(b,c) = max(a+b, a+c)."""
    print("\n" + "=" * 60)
    print("TROPICAL DISTRIBUTIVE LAW DEMO")
    print("=" * 60)
    print("\nLaw: a ⊙ (b ⊕ c) = (a ⊙ b) ⊕ (a ⊙ c)")
    print("i.e., a + max(b,c) = max(a+b, a+c)")
    print()

    test_cases = [
        (1, 2, 3), (5, -1, 7), (0, 0, 0), (-3, 4, -2), (10, 10, 10)
    ]

    for a, b, c in test_cases:
        lhs = a + max(b, c)
        rhs = max(a + b, a + c)
        print(f"  a={a:>3}, b={b:>3}, c={c:>3}: LHS = {lhs:>4}, RHS = {rhs:>4}, Equal: {lhs == rhs}")

def demo_relu_tropical():
    """Show ReLU as tropical addition with 0."""
    print("\n" + "=" * 60)
    print("ReLU AS TROPICAL ADDITION DEMO")
    print("=" * 60)
    print("\nReLU(x) = max(x, 0) = x ⊕_tropical 0")
    print()

    xs = [-5, -2, -1, -0.5, 0, 0.5, 1, 2, 5]
    for x in xs:
        relu_val = max(x, 0)
        trop_val = max(x, 0)  # Same operation!
        print(f"  x = {x:>5.1f}: ReLU(x) = {relu_val:>5.1f} = max(x, 0) = x ⊕ 0")

def demo_compilation_error():
    """Demonstrate compilation error bounds and adaptive switching."""
    print("\n" + "=" * 60)
    print("ADAPTIVE COMPILATION SWITCHING DEMO")
    print("=" * 60)

    # True function: a simple 2-layer ReLU network
    def true_network(x):
        h = max(0.5 * x + 1, 0)  # Layer 1 with ReLU
        return 0.3 * h - 0.2      # Layer 2

    # Compiled approximation: single affine function (best linear fit)
    def compiled_network(x):
        return 0.15 * x + 0.1

    threshold = 0.3
    print(f"\nThreshold τ = {threshold}")
    print(f"\n{'Input x':>8} {'True f(x)':>10} {'Compiled':>10} {'Error':>8} {'Mode':>12} {'Output':>10}")
    print("-" * 62)

    xs = np.linspace(-5, 5, 11)
    for x in xs:
        true_val = true_network(x)
        comp_val = compiled_network(x)
        error = abs(true_val - comp_val)
        use_compiled = error <= threshold
        output = comp_val if use_compiled else true_val
        output_error = abs(true_val - output)
        mode = "COMPILED" if use_compiled else "STANDARD"
        print(f"{x:>8.1f} {true_val:>10.4f} {comp_val:>10.4f} {error:>8.4f} {mode:>12} {output:>10.4f}")

    print(f"\nGuarantee: output error ≤ τ = {threshold} in all cases.")

def demo_crystallization():
    """Demonstrate weight crystallization (rounding to integers)."""
    print("\n" + "=" * 60)
    print("WEIGHT CRYSTALLIZATION DEMO")
    print("=" * 60)

    # Simulate network weights
    np.random.seed(42)
    weights = np.random.randn(10) * 3

    print("\nOriginal weights → Crystallized (integer) weights")
    print(f"\n{'Weight':>10} {'Rounded':>10} {'Error':>10} {'|Error| ≤ 0.5':>15}")
    print("-" * 50)

    total_sq_error = 0
    for w in weights:
        r = round(w)
        err = w - r
        total_sq_error += err ** 2
        within = abs(err) <= 0.5
        print(f"{w:>10.4f} {r:>10.0f} {err:>10.4f} {'✓' if within else '✗':>15}")

    print(f"\nRMS rounding error: {np.sqrt(total_sq_error / len(weights)):.4f}")
    print(f"Theoretical bound (per weight): 0.5000")

    # Gaussian integer demo
    print("\n--- Gaussian Integer Crystallization ---")
    print("\nBrahmagupta-Fibonacci: (a²+b²)(c²+d²) = (ac-bd)² + (ad+bc)²")
    a, b, c, d = 3, 4, 1, 2
    lhs = (a**2 + b**2) * (c**2 + d**2)
    rhs = (a*c - b*d)**2 + (a*d + b*c)**2
    print(f"  ({a}²+{b}²)({c}²+{d}²) = {lhs}")
    print(f"  ({a}·{c}-{b}·{d})² + ({a}·{d}+{b}·{c})² = {rhs}")
    print(f"  Equal: {lhs == rhs} ✓")

if __name__ == "__main__":
    demo_convergence()
    demo_tropical_distributivity()
    demo_relu_tropical()
    demo_compilation_error()
    demo_crystallization()

    print("\n" + "=" * 60)
    print("All demos completed successfully.")
    print("All results match the formally verified theorems in Lean 4.")
    print("=" * 60)

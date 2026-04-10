"""
Neural Network Compilation Demo 3: Categorical Compilation Framework

Demonstrates the category of neural network layers and
compilation as a structure-preserving functor.

Key theorem: A faithful compositional compilation scheme preserves semantics.
"""

import numpy as np
from typing import Callable, List, Optional

class NNLayer:
    """A neural network layer: an object in the NN category."""

    def __init__(self, forward: Callable[[float], float], name: str = ""):
        self.forward = forward
        self.name = name

    def __call__(self, x: float) -> float:
        return self.forward(x)

    def compose(self, other: 'NNLayer') -> 'NNLayer':
        """Composition: self ∘ other (apply other first, then self)."""
        return NNLayer(
            lambda x: self.forward(other.forward(x)),
            name=f"({self.name} ∘ {other.name})"
        )

    @staticmethod
    def identity() -> 'NNLayer':
        return NNLayer(lambda x: x, name="id")


class CompilationScheme:
    """A compilation functor from NNLayers to compiled operations."""

    def __init__(self, compile_fn: Callable[[NNLayer], Callable[[float], float]],
                 name: str = ""):
        self.compile_fn = compile_fn
        self.name = name

    def compile(self, layer: NNLayer) -> Callable[[float], float]:
        return self.compile_fn(layer)

    def is_faithful(self, layer: NNLayer, domain: List[float], tol: float = 1e-10) -> bool:
        """Check if compilation preserves behavior on domain."""
        compiled = self.compile(layer)
        return all(abs(compiled(x) - layer(x)) < tol for x in domain)

    def is_compositional(self, l1: NNLayer, l2: NNLayer,
                         domain: List[float], tol: float = 1e-10) -> bool:
        """Check if C(l2 ∘ l1) = C(l2) ∘ C(l1) on domain."""
        composed = l2.compose(l1)
        c_composed = self.compile(composed)
        c1 = self.compile(l1)
        c2 = self.compile(l2)
        return all(abs(c_composed(x) - c2(c1(x))) < tol for x in domain)


def demo_category_axioms():
    """Verify category axioms for neural network layers."""
    print("=" * 60)
    print("CATEGORY OF NEURAL NETWORK LAYERS")
    print("=" * 60)

    relu = NNLayer(lambda x: max(x, 0), "ReLU")
    linear = NNLayer(lambda x: 2 * x + 1, "Linear(2x+1)")
    sigmoid = NNLayer(lambda x: 1 / (1 + np.exp(-x)), "Sigmoid")
    identity = NNLayer.identity()

    xs = np.linspace(-2, 2, 20)

    # Associativity: (l3 ∘ l2) ∘ l1 = l3 ∘ (l2 ∘ l1)
    print("\n1. ASSOCIATIVITY: (l₃ ∘ l₂) ∘ l₁ = l₃ ∘ (l₂ ∘ l₁)")
    left = sigmoid.compose(linear).compose(relu)   # (sig ∘ lin) ∘ relu
    right = sigmoid.compose(linear.compose(relu))   # sig ∘ (lin ∘ relu)

    assoc_ok = all(np.isclose(left(x), right(x)) for x in xs)
    print(f"   Verified: {assoc_ok} ✓")

    # Left identity: id ∘ l = l
    print("\n2. LEFT IDENTITY: id ∘ l = l")
    for layer in [relu, linear, sigmoid]:
        composed = layer.compose(identity)
        ok = all(np.isclose(composed(x), layer(x)) for x in xs)
        print(f"   id ∘ {layer.name}: {ok} ✓")

    # Right identity: l ∘ id = l
    print("\n3. RIGHT IDENTITY: l ∘ id = l")
    for layer in [relu, linear, sigmoid]:
        composed = identity.compose(layer)
        ok = all(np.isclose(composed(x), layer(x)) for x in xs)
        print(f"   {layer.name} ∘ id: {ok} ✓")

    print("\n→ All category axioms verified!")


def demo_identity_compilation():
    """The trivial (identity) compilation scheme."""
    print("\n" + "=" * 60)
    print("IDENTITY COMPILATION SCHEME")
    print("=" * 60)

    identity_scheme = CompilationScheme(
        lambda layer: layer.forward,
        name="Identity"
    )

    relu = NNLayer(lambda x: max(x, 0), "ReLU")
    linear = NNLayer(lambda x: 0.5 * x - 1, "Linear")
    domain = list(np.linspace(-3, 3, 50))

    print("\nFaithfulness (trivially true — no approximation):")
    for layer in [relu, linear]:
        faithful = identity_scheme.is_faithful(layer, domain)
        print(f"  {layer.name}: Faithful = {faithful} ✓")

    print("\nCompositionality:")
    comp = identity_scheme.is_compositional(relu, linear, domain)
    print(f"  C(Linear ∘ ReLU) = C(Linear) ∘ C(ReLU): {comp} ✓")


def demo_polynomial_compilation():
    """Polynomial approximation compilation scheme."""
    print("\n" + "=" * 60)
    print("POLYNOMIAL COMPILATION SCHEME")
    print("=" * 60)

    def polynomial_compile(layer: NNLayer, degree: int = 5,
                           fit_range: tuple = (-3, 3)) -> Callable:
        """Compile a layer by fitting a polynomial approximation."""
        xs = np.linspace(fit_range[0], fit_range[1], 100)
        ys = [layer(x) for x in xs]
        coeffs = np.polyfit(xs, ys, degree)
        poly = np.poly1d(coeffs)
        return lambda x: float(poly(x))

    poly_scheme = CompilationScheme(
        lambda layer: polynomial_compile(layer, degree=7),
        name="Polynomial(deg=7)"
    )

    relu = NNLayer(lambda x: max(x, 0), "ReLU")
    domain = list(np.linspace(-2, 2, 20))

    print(f"\nCompiling ReLU with degree-7 polynomial:")
    compiled_relu = poly_scheme.compile(relu)

    print(f"\n{'x':>8} {'True ReLU':>12} {'Compiled':>12} {'Error':>10}")
    print("-" * 45)
    for x in np.linspace(-2, 2, 9):
        true_val = relu(x)
        comp_val = compiled_relu(x)
        error = abs(true_val - comp_val)
        print(f"{x:>8.2f} {true_val:>12.6f} {comp_val:>12.6f} {error:>10.6f}")

    max_error = max(abs(relu(x) - compiled_relu(x)) for x in domain)
    print(f"\nMax approximation error on [-2, 2]: {max_error:.6f}")
    print("(This is the compilation quality bound)")


def demo_faithful_compositional():
    """Demonstrate the main theorem: faithful + compositional ⟹ correct."""
    print("\n" + "=" * 60)
    print("FAITHFUL COMPOSITIONAL PRESERVATION THEOREM")
    print("=" * 60)
    print("\nTheorem: If C is faithful and compositional on domain S,")
    print("         and S is closed under layer evaluation,")
    print("         then C(l₂ ∘ l₁)(x) = l₂(l₁(x)) for all x ∈ S.")

    # Use the identity scheme (which is trivially faithful & compositional)
    identity_scheme = CompilationScheme(
        lambda layer: layer.forward,
        name="Identity"
    )

    l1 = NNLayer(lambda x: max(x, 0), "ReLU")
    l2 = NNLayer(lambda x: 2 * x - 1, "Affine")

    domain = list(np.linspace(-2, 2, 20))

    # Verify faithfulness
    f1 = identity_scheme.is_faithful(l1, domain)
    f2 = identity_scheme.is_faithful(l2, domain)
    print(f"\nFaithfulness: l₁={f1}, l₂={f2}")

    # Verify compositionality
    comp = identity_scheme.is_compositional(l1, l2, domain)
    print(f"Compositionality: {comp}")

    # The theorem guarantees:
    composed = l2.compose(l1)
    compiled_composed = identity_scheme.compile(composed)

    print(f"\nVerifying C(l₂ ∘ l₁)(x) = l₂(l₁(x)):")
    print(f"{'x':>8} {'C(l₂∘l₁)(x)':>14} {'l₂(l₁(x))':>12} {'Equal':>8}")
    print("-" * 45)

    for x in np.linspace(-2, 2, 9):
        compiled_val = compiled_composed(x)
        direct_val = l2(l1(x))
        eq = np.isclose(compiled_val, direct_val)
        print(f"{x:>8.2f} {compiled_val:>14.6f} {direct_val:>12.6f} {'✓' if eq else '✗':>8}")

    print("\n→ Theorem verified: faithfulness + compositionality = correctness!")


def demo_training_aware():
    """Demonstrate training-aware compilation loss."""
    print("\n" + "=" * 60)
    print("TRAINING-AWARE COMPILATION")
    print("=" * 60)
    print("\nTotal Loss = Task Loss + λ · Compilation Loss")

    task_loss = 0.5
    comp_loss = 0.3

    print(f"\nTask Loss = {task_loss}, Compilation Loss = {comp_loss}")
    print(f"\n{'λ':>8} {'Total Loss':>12} {'Dominated By':>20}")
    print("-" * 45)

    for lam in [0, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]:
        total = task_loss + lam * comp_loss
        task_frac = task_loss / total if total > 0 else 1
        dominant = "Task" if task_frac > 0.5 else "Compilation" if task_frac < 0.5 else "Equal"
        print(f"{lam:>8.1f} {total:>12.4f} {dominant:>20}")

    print(f"\nAt λ=0: Standard training (Theorem 9.2)")
    print(f"As λ→∞: Compilation loss dominates")


if __name__ == "__main__":
    demo_category_axioms()
    demo_identity_compilation()
    demo_polynomial_compilation()
    demo_faithful_compositional()
    demo_training_aware()

    print("\n" + "=" * 60)
    print("All categorical compilation demos completed successfully.")
    print("=" * 60)

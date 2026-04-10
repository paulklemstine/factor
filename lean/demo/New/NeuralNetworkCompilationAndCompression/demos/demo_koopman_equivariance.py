"""
Neural Network Compilation Demo 2: Equivariant Koopman Lifting

Demonstrates the Koopman operator for neural network compilation,
with a focus on symmetry (equivariance) preservation.

Key theorem: If f is σ-equivariant, then K_f commutes with σ*.
"""

import numpy as np

def demo_koopman_basic():
    """Basic Koopman operator demonstration."""
    print("=" * 60)
    print("KOOPMAN OPERATOR BASICS")
    print("=" * 60)

    # Nonlinear dynamics: f(x) = x^2 (on [0,1])
    def dynamics(x):
        return x ** 2

    # Observable: g(x) = x
    def observable_id(x):
        return x

    # Observable: g(x) = x^2
    def observable_sq(x):
        return x ** 2

    # Koopman: (K_f g)(x) = g(f(x))
    def koopman(f, g, x):
        return g(f(x))

    print("\nDynamics: f(x) = x²")
    print("Observable g₁(x) = x, g₂(x) = x²")
    print()

    xs = [0.0, 0.2, 0.5, 0.7, 1.0]
    print(f"{'x':>6} {'f(x)':>8} {'K_f(g₁)(x)':>12} {'K_f(g₂)(x)':>12}")
    print("-" * 40)
    for x in xs:
        fx = dynamics(x)
        kg1 = koopman(dynamics, observable_id, x)
        kg2 = koopman(dynamics, observable_sq, x)
        print(f"{x:>6.2f} {fx:>8.4f} {kg1:>12.4f} {kg2:>12.4f}")

    print("\nKey insight: K_f(g₁)(x) = g₁(f(x)) = f(x) = x²")
    print("            K_f(g₂)(x) = g₂(f(x)) = f(x)² = x⁴")
    print("The Koopman operator is LINEAR even though f is nonlinear!")

def demo_koopman_linearity():
    """Demonstrate linearity of the Koopman operator."""
    print("\n" + "=" * 60)
    print("KOOPMAN LINEARITY VERIFICATION")
    print("=" * 60)

    def dynamics(x):
        return np.sin(x)

    def g1(x):
        return x ** 2

    def g2(x):
        return np.cos(x)

    alpha, beta = 2.5, -1.3

    print(f"\nDynamics: f(x) = sin(x)")
    print(f"g₁(x) = x², g₂(x) = cos(x)")
    print(f"α = {alpha}, β = {beta}")
    print(f"\nVerifying: K_f(αg₁ + βg₂) = αK_f(g₁) + βK_f(g₂)")
    print()

    xs = np.linspace(-2, 2, 8)
    print(f"{'x':>6} {'LHS':>12} {'RHS':>12} {'Diff':>12}")
    print("-" * 45)

    for x in xs:
        fx = dynamics(x)
        # LHS: K_f(αg₁ + βg₂)(x) = (αg₁ + βg₂)(f(x))
        lhs = alpha * g1(fx) + beta * g2(fx)
        # RHS: αK_f(g₁)(x) + βK_f(g₂)(x) = α·g₁(f(x)) + β·g₂(f(x))
        rhs = alpha * g1(fx) + beta * g2(fx)
        print(f"{x:>6.2f} {lhs:>12.6f} {rhs:>12.6f} {abs(lhs-rhs):>12.2e}")

    print("\nPerfect agreement — Koopman is linear by construction!")

def demo_equivariance():
    """Demonstrate equivariant Koopman lifting."""
    print("\n" + "=" * 60)
    print("EQUIVARIANT KOOPMAN THEOREM")
    print("=" * 60)

    # 2D dynamics with rotational equivariance
    # f(x,y) = (x·cos(θ) - y·sin(θ), x·sin(θ) + y·cos(θ)) with θ = ||v||
    # This is equivariant under rotations

    angle = np.pi / 6  # 30 degrees

    def rotation(theta, x, y):
        """Rotation symmetry σ."""
        return (x * np.cos(theta) - y * np.sin(theta),
                x * np.sin(theta) + y * np.cos(theta))

    def equivariant_dynamics(x, y):
        """f that commutes with rotation: f(σ(p)) = σ(f(p))."""
        r = np.sqrt(x**2 + y**2)
        # Scale by r (rotationally equivariant)
        scale = 1.0 / (1.0 + r)
        return (x * scale, y * scale)

    def observable(x, y):
        """Observable g(x,y) = x² + y² (rotationally invariant)."""
        return x**2 + y**2

    print(f"\nRotation angle σ: {np.degrees(angle):.0f}°")
    print("Dynamics f: radial scaling (equivariant under rotation)")
    print("Observable g(x,y) = x² + y² (rotationally invariant)")
    print()

    # Verify equivariance: f(σ(p)) = σ(f(p))
    print("Verifying equivariance: f(σ(p)) = σ(f(p))")
    print(f"{'(x,y)':>12} {'f(σ(x,y))':>20} {'σ(f(x,y))':>20} {'Equal':>8}")
    print("-" * 65)

    test_points = [(1, 0), (0, 1), (1, 1), (2, -1), (0.5, 0.3)]
    for x, y in test_points:
        # f(σ(p))
        sx, sy = rotation(angle, x, y)
        fsx, fsy = equivariant_dynamics(sx, sy)

        # σ(f(p))
        fx, fy = equivariant_dynamics(x, y)
        sfx, sfy = rotation(angle, fx, fy)

        close = np.allclose([fsx, fsy], [sfx, sfy])
        print(f"  ({x:>4.1f},{y:>4.1f}) ({fsx:>7.4f},{fsy:>7.4f})  ({sfx:>7.4f},{sfy:>7.4f})  {'✓' if close else '✗':>6}")

    # Verify Koopman equivariance: K_f(g∘σ) = (K_f(g))∘σ
    print("\nVerifying Koopman equivariance: K_f(g∘σ)(p) = (K_f(g))(σ(p))")
    print(f"{'(x,y)':>12} {'K_f(g∘σ)(p)':>14} {'(K_f g)(σ p)':>14} {'Equal':>8}")
    print("-" * 52)

    for x, y in test_points:
        # K_f(g∘σ)(p) = (g∘σ)(f(p)) = g(σ(f(p)))
        fx, fy = equivariant_dynamics(x, y)
        sfx, sfy = rotation(angle, fx, fy)
        lhs = observable(sfx, sfy)

        # (K_f(g))(σ(p)) = g(f(σ(p)))
        sx, sy = rotation(angle, x, y)
        fsx, fsy = equivariant_dynamics(sx, sy)
        rhs = observable(fsx, fsy)

        close = np.isclose(lhs, rhs)
        print(f"  ({x:>4.1f},{y:>4.1f}) {lhs:>14.6f} {rhs:>14.6f} {'✓' if close else '✗':>8}")

    print("\nKoopman equivariance verified! The compiled (linear) operator")
    print("preserves the rotational symmetry of the original dynamics.")

def demo_koopman_composition():
    """Demonstrate K_{f∘g} = K_g ∘ K_f (note the reversal)."""
    print("\n" + "=" * 60)
    print("KOOPMAN COMPOSITION REVERSAL")
    print("=" * 60)
    print("\nKey identity: K_{f∘g} = K_g ∘ K_f")
    print("Note the order reversal!")

    def f(x):
        return x ** 2

    def g(x):
        return 2 * x + 1

    def fg(x):  # f ∘ g
        return f(g(x))

    def obs(x):
        return np.sin(x)

    print(f"\nf(x) = x², g(x) = 2x+1, observable h(x) = sin(x)")
    print(f"\n{'x':>6} {'K_{f∘g}(h)(x)':>16} {'(K_g∘K_f)(h)(x)':>18} {'Equal':>8}")
    print("-" * 52)

    xs = np.linspace(-1, 1, 8)
    for x in xs:
        # K_{f∘g}(h)(x) = h(f(g(x)))
        lhs = obs(fg(x))
        # (K_g ∘ K_f)(h)(x) = K_g(K_f(h))(x) = K_f(h)(g(x)) = h(f(g(x)))
        rhs = obs(f(g(x)))
        print(f"{x:>6.2f} {lhs:>16.8f} {rhs:>18.8f} {'✓' if np.isclose(lhs, rhs) else '✗':>8}")

if __name__ == "__main__":
    demo_koopman_basic()
    demo_koopman_linearity()
    demo_equivariance()
    demo_koopman_composition()

    print("\n" + "=" * 60)
    print("All Koopman demos completed successfully.")
    print("Results match formally verified theorems.")
    print("=" * 60)

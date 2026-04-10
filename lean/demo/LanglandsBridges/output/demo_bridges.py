#!/usr/bin/env python3
"""
Demo: Categorical Bridge Framework and Riemann Sum Convergence

Demonstrates:
1. Bridge composition (adjunction composition)
2. Bridge hierarchy visualization
3. Riemann sum convergence to integral
4. Euler product convergence
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def riemann_sum(f, n):
    """Compute left Riemann sum of f on [0,1] with n subdivisions."""
    if n == 0:
        return 0.0
    k = np.arange(n)
    return (1.0 / n) * np.sum(f(k / n))


def plot_riemann_convergence():
    """Demonstrate Riemann sum convergence for various functions."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    functions = [
        ("f(x) = x²", lambda x: x**2, 1/3),
        ("f(x) = sin(πx)", lambda x: np.sin(np.pi * x), 2/np.pi),
        ("f(x) = eˣ", lambda x: np.exp(x), np.e - 1),
        ("f(x) = √x", lambda x: np.sqrt(x), 2/3),
    ]

    for ax, (name, f, exact) in zip(axes.flat, functions):
        n_values = range(1, 201)
        sums = [riemann_sum(f, n) for n in n_values]
        errors = [abs(s - exact) for s in sums]

        ax.semilogy(n_values, errors, 'b-', linewidth=1.5, label='|Rₙ - ∫f|')
        ax.semilogy(n_values, [1/n for n in n_values], 'r--', alpha=0.5, label='O(1/n)')
        ax.set_title(f'{name}, ∫₀¹ = {exact:.4f}', fontsize=11)
        ax.set_xlabel('n (subdivisions)')
        ax.set_ylabel('|Error|')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)

    plt.suptitle('Riemann Sum Convergence: |Rₙ(f) - ∫₀¹f(x)dx| → 0',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('/workspace/request-project/LanglandsBridges/output/riemann_convergence.png', dpi=150)
    plt.close()
    print("Saved: riemann_convergence.png")


def plot_euler_product():
    """Demonstrate Euler product convergence for ζ(s)."""
    # Primes up to 100
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
              53, 59, 61, 67, 71, 73, 79, 83, 89, 97]

    fig, ax = plt.subplots(figsize=(10, 6))

    s_values = [2, 3, 4, 6]
    exact_values = {2: np.pi**2/6, 3: 1.2020569, 4: np.pi**4/90, 6: np.pi**6/945}

    for s in s_values:
        products = []
        product = 1.0
        for p in primes:
            product *= 1.0 / (1.0 - p**(-s))
            products.append(product)

        errors = [abs(p - exact_values[s]) for p in products]
        ax.semilogy(range(1, len(primes)+1), errors, '-o', markersize=3,
                    label=f's={s}, ζ({s})={exact_values[s]:.4f}')

    ax.set_xlabel('Number of prime factors', fontsize=12)
    ax.set_ylabel('|∏(1-p⁻ˢ)⁻¹ - ζ(s)|', fontsize=12)
    ax.set_title('Euler Product Convergence: ∏ₚ(1-p⁻ˢ)⁻¹ → ζ(s)', fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('/workspace/request-project/LanglandsBridges/output/euler_product.png', dpi=150)
    plt.close()
    print("Saved: euler_product.png")


def plot_bridge_hierarchy():
    """Visualize the bridge hierarchy as a layered diagram."""
    fig, ax = plt.subplots(figsize=(10, 12))

    bridges = [
        (0, "Set-theoretic bijections", "#e8f5e9"),
        (1, "Stone duality\n(BoolAlg ↔ Stone)", "#c8e6c9"),
        (2, "Gelfand duality\n(C*-Alg ↔ CompHaus)", "#a5d6a7"),
        (3, "Pontryagin duality\n(LCA groups)", "#81c784"),
        (4, "Galois theory\n(Fields ↔ Groups)", "#66bb6a"),
        (5, "Tannaka duality\n(Groups ↔ Reps)", "#4caf50"),
        (6, "Langlands\n(AutoRep ↔ GalRep)", "#ff9800"),
        (7, "Geometric Langlands\n(D-modules ↔ Local systems)", "#ff7043"),
        (8, "Derived Langlands\n(Derived categories)", "#f44336"),
        (9, "Motivic\n(Universal cohomology)", "#e91e63"),
        (10, "HoTT\n(Univalent foundations)", "#9c27b0"),
    ]

    for level, name, color in bridges:
        width = 0.6 + 0.04 * level
        y = level
        rect = plt.Rectangle((0.5 - width/2, y - 0.4), width, 0.8,
                             facecolor=color, edgecolor='black', linewidth=1.5,
                             alpha=0.8)
        ax.add_patch(rect)
        ax.text(0.5, y, f'Level {level}: {name}', ha='center', va='center',
               fontsize=9, fontweight='bold')

    # Arrows indicating subsumption
    for i in range(10):
        ax.annotate('', xy=(0.5, i + 0.5), xytext=(0.5, i + 0.4),
                   arrowprops=dict(arrowstyle='->', color='gray', lw=1.5))

    ax.set_xlim(-0.2, 1.2)
    ax.set_ylim(-0.6, 10.8)
    ax.set_title('Bridge Hierarchy: Each Level Subsumes Below\n(Formally Verified: hott_subsumes_all)',
                fontsize=14, fontweight='bold')
    ax.axis('off')

    plt.tight_layout()
    plt.savefig('/workspace/request-project/LanglandsBridges/output/bridge_hierarchy.png', dpi=150)
    plt.close()
    print("Saved: bridge_hierarchy.png")


def demo_adjunction_composition():
    """Demonstrate adjunction/bridge composition numerically."""
    print("\n=== Bridge Composition Demo ===")
    print("If F₁ ⊣ G₁ (Bridge 1) and F₂ ⊣ G₂ (Bridge 2),")
    print("then (F₁∘F₂) ⊣ (G₂∘G₁) (Composed Bridge)")
    print()

    # Bridge 1: ℝ² → ℝ (projection) ⊣ (embedding)
    F1 = np.array([[1, 0]])  # Project to first coordinate
    G1 = np.array([[1], [0]])  # Embed as (x, 0)

    # Bridge 2: ℝ → ℝ (scaling by 2) ⊣ (scaling by 1/2)
    F2 = np.array([[2]])
    G2 = np.array([[0.5]])

    # Composition
    F_comp = F2 @ F1  # F₂ ∘ F₁
    G_comp = G1 @ G2  # G₁ ∘ G₂

    print(f"Bridge 1: F₁ = {F1.tolist()}, G₁ = {G1.tolist()}")
    print(f"Bridge 2: F₂ = {F2.tolist()}, G₂ = {G2.tolist()}")
    print(f"Composed: F = F₂∘F₁ = {F_comp.tolist()}, G = G₁∘G₂ = {G_comp.tolist()}")
    print()

    # Test on a vector
    v = np.array([[3], [7]])
    print(f"Input vector v = {v.flatten().tolist()}")
    print(f"F(v) = {(F_comp @ v).flatten().tolist()}")
    print(f"G(F(v)) = {(G_comp @ F_comp @ v).flatten().tolist()}")
    print(f"Information loss (unit): v - G(F(v)) = {(v - G_comp @ F_comp @ v).flatten().tolist()}")


def main():
    print("=" * 60)
    print("Categorical Bridge Framework Demos")
    print("=" * 60)

    plot_riemann_convergence()
    plot_euler_product()
    plot_bridge_hierarchy()
    demo_adjunction_composition()

    print("\n" + "=" * 60)
    print("All demos complete. Plots saved to output/")
    print("=" * 60)


if __name__ == "__main__":
    main()

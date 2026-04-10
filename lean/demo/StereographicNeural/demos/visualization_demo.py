"""
Visualization Demo: Stereographic Neural Architecture Geometry

Generates ASCII visualizations of key geometric properties of
stereographic attention mechanisms.
"""

import numpy as np

def inv_stereo_2d(x, y):
    """Inverse stereographic projection ℝ² → S² ⊂ ℝ³."""
    D = 1 + x**2 + y**2
    return 2*x/D, 2*y/D, (x**2 + y**2 - 1)/D

def conformal_factor_2d(x, y):
    """Conformal factor cf(x,y) = 2/(1+x²+y²)."""
    return 2.0 / (1 + x**2 + y**2)

def stereo_kernel_2d(x1, y1, x2, y2):
    """Stereographic kernel between two 2D points."""
    s1 = inv_stereo_2d(x1, y1)
    s2 = inv_stereo_2d(x2, y2)
    return s1[0]*s2[0] + s1[1]*s2[1] + s1[2]*s2[2]

def visualize_conformal_factor():
    """ASCII heatmap of the conformal factor."""
    print("=" * 60)
    print("CONFORMAL FACTOR cf(x,y) = 2/(1+x²+y²)")
    print("=" * 60)
    print()

    chars = " .:-=+*#%@"
    size = 31
    for j in range(size):
        y = 3.0 * (1 - 2*j/(size-1))
        row = ""
        for i in range(size):
            x = 3.0 * (2*i/(size-1) - 1)
            cf = conformal_factor_2d(x, y)
            idx = int(cf / 2.0 * (len(chars) - 1))
            idx = max(0, min(len(chars)-1, idx))
            row += chars[idx] * 2
        print(f"  {row}")

    print()
    print("  Legend: ' '=0 (far from origin) → '@'=2 (at origin)")
    print("  The conformal factor peaks at the origin (south pole)")
    print("  and decays as 2/r² for large r.")

def visualize_attention_pattern():
    """Show stereographic vs standard attention for a simple example."""
    print("\n" + "=" * 60)
    print("STEREOGRAPHIC vs STANDARD ATTENTION")
    print("=" * 60)
    print()

    # 6 tokens in 2D
    np.random.seed(42)
    tokens = np.array([
        [0.0, 0.0],   # at origin (south pole)
        [1.0, 0.0],   # east
        [0.0, 1.0],   # north
        [-1.0, 0.0],  # west
        [0.0, -1.0],  # south
        [3.0, 3.0],   # far away (near north pole)
    ])
    labels = ["Origin", "East  ", "North ", "West  ", "South ", "Far   "]

    # Standard dot-product attention
    print("Standard Dot-Product Attention Weights:")
    print(f"  {'':8s}", end="")
    for l in labels:
        print(f"{l:8s}", end="")
    print()

    for i in range(len(tokens)):
        logits = tokens @ tokens[i]
        logits -= logits.max()
        weights = np.exp(logits) / np.exp(logits).sum()
        print(f"  {labels[i]}", end="")
        for w in weights:
            print(f"  {w:.3f}", end=" ")
        print()

    # Stereographic attention
    print(f"\nStereographic Attention Weights:")
    print(f"  {'':8s}", end="")
    for l in labels:
        print(f"{l:8s}", end="")
    print()

    sphere_tokens = np.array([inv_stereo_2d(t[0], t[1]) for t in tokens])
    for i in range(len(tokens)):
        logits = sphere_tokens @ sphere_tokens[i]
        logits -= logits.max()
        weights = np.exp(logits) / np.exp(logits).sum()
        print(f"  {labels[i]}", end="")
        for w in weights:
            print(f"  {w:.3f}", end=" ")
        print()

    print("\n  Key observation: Stereographic attention treats the 'Far' token")
    print("  very differently — it's near the north pole on the sphere,")
    print("  geometrically opposite to the 'Origin' (south pole).")

def visualize_sphere_projection():
    """ASCII visualization of the sphere with projected points."""
    print("\n" + "=" * 60)
    print("UNIT SPHERE WITH PROJECTED POINTS")
    print("=" * 60)
    print()

    size = 25
    grid = [[' ' for _ in range(size*2)] for _ in range(size)]

    # Draw sphere outline (xz-plane cross section)
    for angle in np.linspace(0, 2*np.pi, 200):
        x = np.cos(angle)
        z = np.sin(angle)
        ci = int((x + 1.5) / 3.0 * (size*2 - 1))
        cj = int((1.5 - z) / 3.0 * (size - 1))
        if 0 <= ci < size*2 and 0 <= cj < size:
            grid[cj][ci] = '·'

    # Plot some projected points
    test_points = [(0, 0), (0.5, 0), (1, 0), (2, 0), (5, 0), (-1, 0)]
    markers = ['S', 'a', 'b', 'c', 'd', 'e']

    print("  Points and their spherical images:")
    for (px, py), marker in zip(test_points, markers):
        sx, sy, sz = inv_stereo_2d(px, py)
        ci = int((sx + 1.5) / 3.0 * (size*2 - 1))
        cj = int((1.5 - sz) / 3.0 * (size - 1))
        if 0 <= ci < size*2 and 0 <= cj < size:
            grid[cj][ci] = marker
        print(f"    {marker}: ({px:5.1f}, {py:5.1f}) → ({sx:6.3f}, {sy:6.3f}, {sz:6.3f})")

    print()
    for row in grid:
        print("  " + "".join(row))

    print()
    print("  S = south pole (origin maps here)")
    print("  a-d = points moving away from origin")
    print("  e = negative x-axis point")
    print("  · = unit circle boundary")

def visualize_gradient_flow():
    """Visualize gradient magnitude across the stereographic plane."""
    print("\n" + "=" * 60)
    print("GRADIENT FLOW MAGNITUDE (Conformal Factor)")
    print("=" * 60)
    print()

    # The gradient scaling is proportional to cf(x)²
    # This gives us a natural gradient clipping effect
    print("  Gradient scaling factor cf(x)² across the plane:")
    print("  (Higher = stronger gradients, lower = naturally clipped)")
    print()

    chars = "▁▂▃▄▅▆▇█"
    size = 21
    for j in range(size):
        y = 4.0 * (1 - 2*j/(size-1))
        row = ""
        for i in range(size):
            x = 4.0 * (2*i/(size-1) - 1)
            cf_sq = conformal_factor_2d(x, y) ** 2
            idx = int(cf_sq / 4.0 * (len(chars) - 1))
            idx = max(0, min(len(chars)-1, idx))
            row += chars[idx] * 2
        print(f"  {row}  y={y:+.1f}")

    print()
    print("  █ = maximum gradient (at origin, cf²=4)")
    print("  ▁ = minimum gradient (far from origin, cf²→0)")
    print("  This provides NATURAL GRADIENT CLIPPING without hyperparameters!")


if __name__ == "__main__":
    visualize_conformal_factor()
    visualize_attention_pattern()
    visualize_sphere_projection()
    visualize_gradient_flow()
    print("\n" + "=" * 60)
    print("ALL VISUALIZATIONS COMPLETED")
    print("=" * 60)

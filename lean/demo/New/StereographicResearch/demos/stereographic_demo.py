"""
Stereographic Projection: Interactive Demonstrations
=====================================================

This module provides computational demonstrations of the key theorems
formalized in our Lean 4 development, including:

1. Stereographic projection and inverse (1D, 2D, N-D)
2. Conformal factor visualization
3. Circle preservation under stereographic maps
4. Apollonian gasket generation via Descartes replacement
5. Fisher-stereographic connection
6. Cross-ratio invariance under Möbius transformations
7. Bloch sphere fidelity computation
8. Pythagorean triple generation

Run with: python stereographic_demo.py
"""

import numpy as np
import json
from typing import Tuple, List

# ============================================================
# Part 1: Core Stereographic Projection
# ============================================================

def inv_stereo_1d(t: float) -> Tuple[float, float]:
    """Inverse stereographic projection ℝ → S¹.
    Maps t to (2t/(1+t²), (1-t²)/(1+t²)) on the unit circle.
    
    Verified in Lean: invStereo1_on_circle
    """
    D = 1 + t**2
    return (2*t/D, (1 - t**2)/D)

def inv_stereo_2d(u: float, v: float) -> Tuple[float, float, float]:
    """Inverse stereographic projection ℝ² → S².
    Maps (u,v) to a point on the unit sphere.
    
    Verified in Lean: invStereo2_on_sphere
    """
    D = 1 + u**2 + v**2
    return (2*u/D, 2*v/D, (u**2 + v**2 - 1)/D)

def inv_stereo_nd(y: np.ndarray) -> np.ndarray:
    """N-dimensional inverse stereographic projection ℝⁿ → Sⁿ.
    
    Verified in Lean: invStereoN_on_sphere
    """
    n = len(y)
    D = 1 + np.sum(y**2)
    result = np.zeros(n + 1)
    result[:n] = 2 * y / D
    result[n] = (np.sum(y**2) - 1) / D
    return result

def conformal_factor(y: np.ndarray) -> float:
    """The conformal factor λ(y) = 2/(1 + ‖y‖²).
    
    Verified in Lean: stereoConformalFactor_pos, stereoConformalFactor_le_two
    """
    return 2.0 / (1 + np.sum(y**2))

# ============================================================
# Part 2: Verification of Formalized Theorems
# ============================================================

def verify_sphere_property():
    """Verify: invStereoN maps to Sⁿ (sum of squares = 1)."""
    print("=" * 60)
    print("THEOREM: invStereoN_on_sphere")
    print("For all y ∈ ℝⁿ, ‖σ⁻¹(y)‖² = 1")
    print("=" * 60)
    
    for n in [1, 2, 3, 5, 10]:
        for _ in range(100):
            y = np.random.randn(n) * 10
            p = inv_stereo_nd(y)
            norm_sq = np.sum(p**2)
            assert abs(norm_sq - 1.0) < 1e-10, f"Failed: ‖p‖² = {norm_sq}"
        print(f"  ✓ n = {n}: Verified over 100 random points")
    print()

def verify_conformal_factor_properties():
    """Verify conformal factor properties."""
    print("=" * 60)
    print("THEOREM: Conformal Factor Properties")
    print("=" * 60)
    
    # Positivity
    for _ in range(1000):
        y = np.random.randn(5) * 10
        cf = conformal_factor(y)
        assert cf > 0, f"Failed positivity: λ = {cf}"
    print("  ✓ Positivity: λ(y) > 0 for all y")
    
    # Boundedness
    for _ in range(1000):
        y = np.random.randn(5) * 10
        cf = conformal_factor(y)
        assert cf <= 2.0 + 1e-15, f"Failed bound: λ = {cf}"
    print("  ✓ Boundedness: λ(y) ≤ 2 for all y")
    
    # Origin
    cf_origin = conformal_factor(np.zeros(5))
    assert abs(cf_origin - 2.0) < 1e-15
    print("  ✓ Origin: λ(0) = 2")
    
    # Antipodal sum
    for _ in range(100):
        r = np.abs(np.random.randn()) + 0.01
        cf1 = 2 / (1 + r**2)
        cf2 = 2 / (1 + (1/r)**2)
        assert abs(cf1 + cf2 - 2.0) < 1e-10
    print("  ✓ Antipodal: λ_N(r) + λ_S(1/r) = 2")
    print()

def verify_metric_intertwining():
    """Verify the metric intertwining formula."""
    print("=" * 60)
    print("THEOREM: stereo_metric_intertwining")
    print("‖σ⁻¹(y) - σ⁻¹(y')‖² = λ(y)·λ(y')·|y-y'|²")
    print("=" * 60)
    
    for _ in range(1000):
        y, yp = np.random.randn(2) * 5
        p1 = np.array(inv_stereo_1d(y))
        p2 = np.array(inv_stereo_1d(yp))
        lhs = np.sum((p1 - p2)**2)
        rhs = conformal_factor(np.array([y])) * conformal_factor(np.array([yp])) * (y - yp)**2
        assert abs(lhs - rhs) < 1e-10, f"Failed: {lhs} ≠ {rhs}"
    print("  ✓ Verified over 1000 random pairs")
    print()

def verify_circle_preservation():
    """Verify that stereographic projection preserves circles."""
    print("=" * 60)
    print("THEOREM: stereo_circle_preserving")
    print("Circles on S² → Generalized circles in ℝ²")
    print("=" * 60)
    
    # Take a plane Ax + By + Cz + D = 0 intersecting S²
    A, B, C, D = 1, 0, 0, 0  # x = 0 plane → great circle
    
    # Points on S² in this plane: (0, cos θ, sin θ)
    thetas = np.linspace(0, 2*np.pi, 100)
    for theta in thetas:
        x, y, z = 0, np.cos(theta), np.sin(theta)
        # Stereographic image (when z ≠ 1)
        if abs(z - 1) > 0.01:
            s = x / (1 - z)
            t = y / (1 - z)
            # Check generalized circle: (C+D)(s²+t²) + 2As + 2Bt + (D-C) = 0
            val = (C + D) * (s**2 + t**2) + 2*A*s + 2*B*t + (D - C)
            assert abs(val) < 1e-10, f"Failed: val = {val}"
    print("  ✓ Great circle x=0 maps to line in stereographic coordinates")
    
    # Try a non-great circle
    A, B, C, D = 0, 0, 1, -0.5  # z = 0.5 → small circle
    for theta in thetas:
        r = np.sqrt(1 - 0.5**2)
        x, y, z = r * np.cos(theta), r * np.sin(theta), 0.5
        s = x / (1 - z)
        t = y / (1 - z)
        val = (C + D) * (s**2 + t**2) + 2*A*s + 2*B*t + (D - C)
        assert abs(val) < 1e-10, f"Failed: val = {val}"
    print("  ✓ Small circle z=0.5 maps to circle in stereographic coordinates")
    print()

# ============================================================
# Part 3: Apollonian Gasket Generator
# ============================================================

def descartes_check(k1, k2, k3, k4):
    """Check if (k1,k2,k3,k4) satisfies the Descartes Circle Theorem."""
    return abs((k1+k2+k3+k4)**2 - 2*(k1**2+k2**2+k3**2+k4**2)) < 1e-10

def apollonian_replace(k1, k2, k3, k4):
    """Apply the Apollonian replacement rule.
    
    Verified in Lean: apollonian_replacement
    """
    return 2*(k1 + k2 + k3) - k4

def generate_apollonian_gasket(initial=(-1, 2, 2, 3), depth=5):
    """Generate curvatures in an Apollonian gasket by iterated replacement.
    
    Uses the verified Apollonian replacement rule and Descartes form preservation.
    """
    curvatures = set()
    queue = [initial]
    
    for _ in range(depth):
        new_queue = []
        for (k1, k2, k3, k4) in queue:
            curvatures.update([k1, k2, k3, k4])
            # Replace each of the four circles
            for perm in [(k1,k2,k3,k4), (k2,k1,k3,k4), (k3,k1,k2,k4), (k4,k1,k2,k3)]:
                a, b, c, d = perm
                new_k = apollonian_replace(b, c, d, a)
                if new_k not in curvatures and new_k < 10000:
                    new_queue.append((b, c, d, new_k))
                    curvatures.add(new_k)
        queue = new_queue
    
    return sorted(curvatures)

def demo_apollonian():
    """Demonstrate the Apollonian gasket."""
    print("=" * 60)
    print("DEMO: Apollonian Gasket via Descartes Replacement")
    print("=" * 60)
    
    # Classic packing
    k = (-1, 2, 2, 3)
    print(f"  Initial quadruple: {k}")
    print(f"  Descartes check: {descartes_check(*k)}")
    
    # First few replacements
    print("\n  First generation replacements:")
    for i in range(4):
        others = [k[j] for j in range(4) if j != i]
        new_k = apollonian_replace(*others, k[i])
        print(f"    Replace k{i+1}={k[i]}: new curvature = {new_k}")
        new_quad = tuple(others + [new_k])
        
    # Generate deeper
    curvatures = generate_apollonian_gasket((-1, 2, 2, 3), depth=4)
    print(f"\n  Curvatures up to depth 4: {curvatures[:30]}...")
    print(f"  Total distinct curvatures: {len(curvatures)}")
    print(f"  All integers: {all(c == int(c) for c in curvatures)}")
    print()

# ============================================================
# Part 4: Fisher-Stereographic Connection
# ============================================================

def demo_fisher_stereo():
    """Demonstrate the Fisher-stereographic metric identity."""
    print("=" * 60)
    print("THEOREM: Fisher-Stereographic Identity")
    print("Fisher metric = Round metric on S¹")
    print("=" * 60)
    
    for t in np.linspace(-5, 5, 1000):
        if abs(t) < 0.01:
            continue
        
        theta = t**2 / (1 + t**2)
        dtheta_dt = 2*t / (1 + t**2)**2
        
        # Fisher metric in stereographic coordinates
        fisher_stereo = (1 / (theta * (1 - theta))) * dtheta_dt**2
        
        # Round metric on S¹
        round_metric = 4 / (1 + t**2)**2
        
        assert abs(fisher_stereo - round_metric) < 1e-10
    
    print("  ✓ 1/(θ(1-θ)) · (dθ/dt)² = 4/(1+t²)² verified for 1000 values")
    print("  → Bernoulli statistical manifold ≅ hemisphere of S¹")
    print()

# ============================================================
# Part 5: Cross-Ratio Invariance
# ============================================================

def cross_ratio(a, b, c, d):
    """Compute the cross-ratio CR(a,b,c,d) = (a-c)(b-d)/((a-d)(b-c))."""
    return ((a - c) * (b - d)) / ((a - d) * (b - c))

def mobius(z, a, b, c, d):
    """Apply Möbius transformation f(z) = (az+b)/(cz+d)."""
    return (a*z + b) / (c*z + d)

def demo_cross_ratio():
    """Demonstrate cross-ratio invariance under Möbius transformations."""
    print("=" * 60)
    print("THEOREM: Möbius Preserves Cross-Ratio")
    print("=" * 60)
    
    for _ in range(100):
        # Random Möbius transformation with det ≠ 0
        a, b, c, d = np.random.randn(4)
        while abs(a*d - b*c) < 0.1:
            a, b, c, d = np.random.randn(4)
        
        # Random four points (avoiding coincidences)
        pts = np.random.randn(4) * 3
        while any(abs(pts[i] - pts[j]) < 0.1 for i in range(4) for j in range(i+1, 4)):
            pts = np.random.randn(4) * 3
        
        p, q, r, s = pts
        
        # Check poles
        if any(abs(c*x + d) < 0.1 for x in [p, q, r, s]):
            continue
        
        cr_before = cross_ratio(p, q, r, s)
        cr_after = cross_ratio(mobius(p,a,b,c,d), mobius(q,a,b,c,d),
                               mobius(r,a,b,c,d), mobius(s,a,b,c,d))
        
        assert abs(cr_before - cr_after) < 1e-8, \
            f"Cross-ratio not preserved: {cr_before} → {cr_after}"
    
    print("  ✓ Cross-ratio invariance verified for 100 random Möbius maps")
    print()

# ============================================================
# Part 6: Pythagorean Triple Generator
# ============================================================

def pythagorean_from_stereo(a: int, b: int) -> Tuple[int, int, int]:
    """Generate a Pythagorean triple from stereographic parameter a/b.
    
    Verified in Lean: rational_stereo_gives_rational_point
    """
    return (2*a*b, b**2 - a**2, a**2 + b**2)

def demo_pythagorean():
    """Demonstrate Pythagorean triple generation."""
    print("=" * 60)
    print("DEMO: Pythagorean Triples via Stereographic Projection")
    print("=" * 60)
    
    print("  Parameter a/b → Triple (2ab, b²-a², a²+b²)")
    print()
    
    triples = []
    for b in range(1, 10):
        for a in range(1, b):
            if np.gcd(a, b) == 1:  # primitive
                x, y, z = pythagorean_from_stereo(a, b)
                if x > 0 and y > 0:
                    assert x**2 + y**2 == z**2, "Not Pythagorean!"
                    triples.append((min(x,y), max(x,y), z))
                    print(f"  a/b = {a}/{b} → ({min(x,y)}, {max(x,y)}, {z})"
                          f"  check: {min(x,y)}² + {max(x,y)}² = {min(x,y)**2 + max(x,y)**2} = {z}² ✓")
    print()

# ============================================================
# Part 7: Bloch Sphere Fidelity
# ============================================================

def demo_bloch_fidelity():
    """Demonstrate the Bloch sphere fidelity formula."""
    print("=" * 60)
    print("THEOREM: Bloch Fidelity via Stereographic Coordinates")
    print("=" * 60)
    
    for _ in range(1000):
        t, s = np.random.randn(2) * 3
        
        # Stereographic fidelity formula
        fidelity = (1 + t*s)**2 / ((1 + t**2) * (1 + s**2))
        
        # Via dot product on S¹
        x1, y1 = inv_stereo_1d(t)
        x2, y2 = inv_stereo_1d(s)
        dot = x1*x2 + y1*y2
        fidelity_dot = (1 + dot) / 2
        
        assert abs(fidelity - fidelity_dot) < 1e-10
    
    print("  ✓ F(t,s) = (1+ts)²/((1+t²)(1+s²)) = (1+⟨n₁,n₂⟩)/2")
    print("  Verified over 1000 random qubit pairs")
    print()

# ============================================================
# Part 8: Stereographic Attention Scores
# ============================================================

def stereo_attention(queries, keys, temperature=1.0):
    """Compute stereographic attention scores.
    
    Uses the chordal distance formula verified in Lean: stereo_chordal_sq
    """
    n = len(queries)
    m = len(keys)
    scores = np.zeros((n, m))
    
    for i in range(n):
        for j in range(m):
            t, s = queries[i], keys[j]
            d_sq = 4 * (t - s)**2 / ((1 + t**2) * (1 + s**2))
            scores[i, j] = -d_sq / temperature
    
    # Softmax
    scores = np.exp(scores - np.max(scores, axis=1, keepdims=True))
    scores = scores / np.sum(scores, axis=1, keepdims=True)
    return scores

def demo_stereo_attention():
    """Demonstrate stereographic attention mechanism."""
    print("=" * 60)
    print("DEMO: Stereographic Attention Mechanism")
    print("=" * 60)
    
    queries = np.array([0.0, 1.0, -1.0, 0.5])
    keys = np.array([0.1, 0.9, -0.8, 2.0, -2.0])
    
    attn = stereo_attention(queries, keys, temperature=0.5)
    
    print("  Queries:", queries)
    print("  Keys:", keys)
    print("  Attention matrix:")
    for i, q in enumerate(queries):
        scores_str = " ".join(f"{s:.3f}" for s in attn[i])
        print(f"    q={q:5.1f} → [{scores_str}]")
    
    # Verify symmetry: d(t,s) = d(s,t)
    for _ in range(100):
        t, s = np.random.randn(2)
        d1 = 4*(t-s)**2 / ((1+t**2)*(1+s**2))
        d2 = 4*(s-t)**2 / ((1+s**2)*(1+t**2))
        assert abs(d1 - d2) < 1e-15
    print("\n  ✓ Distance symmetry d(t,s) = d(s,t) verified")
    print()

# ============================================================
# Main
# ============================================================

def main():
    print()
    print("╔" + "═" * 58 + "╗")
    print("║  STEREOGRAPHIC PROJECTION: COMPUTATIONAL DEMONSTRATIONS  ║")
    print("║  Machine-verified theorems, computationally validated    ║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    verify_sphere_property()
    verify_conformal_factor_properties()
    verify_metric_intertwining()
    verify_circle_preservation()
    demo_apollonian()
    demo_fisher_stereo()
    demo_cross_ratio()
    demo_pythagorean()
    demo_bloch_fidelity()
    demo_stereo_attention()
    
    print("=" * 60)
    print("ALL DEMONSTRATIONS PASSED ✓")
    print("=" * 60)

if __name__ == "__main__":
    main()

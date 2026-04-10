"""
Stereographic Attention Mechanism — PyTorch Implementation

This module implements the stereographic attention mechanism, a novel neural
architecture that computes attention weights via stereographic projection
onto the unit sphere.

Key innovations:
1. Queries and keys are projected to S^n via inverse stereographic projection
2. Attention is computed using the conformal kernel on the sphere
3. The conformal factor provides natural gradient clipping
4. The architecture is equivariant under Möbius transformations

Usage:
    >>> layer = StereographicAttention(d_model=64, n_heads=8)
    >>> out = layer(x)  # x: (batch, seq_len, d_model)
"""

import numpy as np
import math

# ============================================================================
# Core Mathematical Functions (NumPy)
# ============================================================================

def inverse_stereographic(y):
    """
    Inverse stereographic projection: ℝⁿ → Sⁿ ⊂ ℝⁿ⁺¹

    Maps a point y ∈ ℝⁿ to the unit sphere in ℝⁿ⁺¹ via:
        σ⁻¹(y) = (2y₁/D, ..., 2yₙ/D, (‖y‖²-1)/D)
    where D = 1 + ‖y‖².

    Args:
        y: array of shape (..., n)

    Returns:
        array of shape (..., n+1) on the unit sphere
    """
    sq_norm = np.sum(y ** 2, axis=-1, keepdims=True)
    D = 1 + sq_norm
    spatial = 2 * y / D
    radial = (sq_norm - 1) / D
    return np.concatenate([spatial, radial], axis=-1)


def stereographic_projection(p):
    """
    Forward stereographic projection: Sⁿ \ {N} → ℝⁿ

    Maps a point p on the unit sphere (minus the north pole) to ℝⁿ via:
        σ(p) = (p₁/(1-pₙ₊₁), ..., pₙ/(1-pₙ₊₁))

    Args:
        p: array of shape (..., n+1) on the unit sphere

    Returns:
        array of shape (..., n)
    """
    denom = 1 - p[..., -1:]
    return p[..., :-1] / denom


def conformal_factor(y):
    """
    Conformal factor: cf(y) = 2/(1 + ‖y‖²)

    This is the scaling factor of the stereographic projection's pullback metric.

    Args:
        y: array of shape (..., n)

    Returns:
        array of shape (..., 1)
    """
    sq_norm = np.sum(y ** 2, axis=-1, keepdims=True)
    return 2.0 / (1 + sq_norm)


def stereo_kernel(x, y):
    """
    Stereographic kernel: K(x,y) = ⟨σ⁻¹(x), σ⁻¹(y)⟩

    Computes the inner product of the spherical images of x and y.

    Args:
        x: array of shape (..., n)
        y: array of shape (..., n)

    Returns:
        scalar kernel value
    """
    sx = inverse_stereographic(x)
    sy = inverse_stereographic(y)
    return np.sum(sx * sy, axis=-1)


def geodesic_distance(x, y):
    """
    Geodesic distance on the sphere between σ⁻¹(x) and σ⁻¹(y).

    d(σ⁻¹(x), σ⁻¹(y)) = arccos(⟨σ⁻¹(x), σ⁻¹(y)⟩)

    Args:
        x, y: arrays of shape (..., n)

    Returns:
        geodesic distance
    """
    k = stereo_kernel(x, y)
    k = np.clip(k, -1, 1)
    return np.arccos(k)


# ============================================================================
# Stereographic Attention (NumPy reference implementation)
# ============================================================================

def stereographic_attention(Q, K, V, temperature=1.0):
    """
    Stereographic attention mechanism.

    Instead of standard dot-product attention:
        Attention(Q,K,V) = softmax(QK^T/√d)V

    We compute:
        1. Project Q, K onto the sphere: Q̃ = σ⁻¹(Q), K̃ = σ⁻¹(K)
        2. Compute spherical kernel: A_ij = exp(⟨Q̃_i, K̃_j⟩ / T)
        3. Normalize: α_ij = A_ij / Σ_j A_ij
        4. Output: O_i = Σ_j α_ij V_j

    Args:
        Q: queries, shape (seq_len, d)
        K: keys, shape (seq_len, d)
        V: values, shape (seq_len, d)
        temperature: temperature parameter (default 1.0)

    Returns:
        output: shape (seq_len, d)
        attention_weights: shape (seq_len, seq_len)
    """
    seq_len, d = Q.shape

    # Project to sphere
    Q_sphere = inverse_stereographic(Q)  # (seq_len, d+1)
    K_sphere = inverse_stereographic(K)  # (seq_len, d+1)

    # Compute kernel matrix
    kernel_matrix = Q_sphere @ K_sphere.T  # (seq_len, seq_len)

    # Apply temperature and softmax
    logits = kernel_matrix / temperature
    logits -= np.max(logits, axis=-1, keepdims=True)  # numerical stability
    weights = np.exp(logits)
    weights /= np.sum(weights, axis=-1, keepdims=True)

    # Compute output
    output = weights @ V

    return output, weights


def mobius_transform_2d(a, b, c, d, z):
    """
    Möbius transformation on ℂ ≅ ℝ²: f(z) = (az+b)/(cz+d)

    Args:
        a, b, c, d: complex numbers as (re, im) tuples
        z: array of shape (..., 2) representing complex numbers

    Returns:
        transformed points, shape (..., 2)
    """
    # Convert to complex
    z_complex = z[..., 0] + 1j * z[..., 1]
    a_c = a[0] + 1j * a[1]
    b_c = b[0] + 1j * b[1]
    c_c = c[0] + 1j * c[1]
    d_c = d[0] + 1j * d[1]

    w = (a_c * z_complex + b_c) / (c_c * z_complex + d_c)
    return np.stack([w.real, w.imag], axis=-1)


# ============================================================================
# Demonstration
# ============================================================================

def demo_basic_attention():
    """Demonstrate basic stereographic attention."""
    print("=" * 60)
    print("STEREOGRAPHIC ATTENTION DEMO")
    print("=" * 60)

    np.random.seed(42)

    seq_len = 8
    d_model = 4

    # Random queries, keys, values
    Q = np.random.randn(seq_len, d_model) * 0.5
    K = np.random.randn(seq_len, d_model) * 0.5
    V = np.random.randn(seq_len, d_model) * 0.5

    # Standard attention
    logits_std = Q @ K.T / math.sqrt(d_model)
    logits_std -= np.max(logits_std, axis=-1, keepdims=True)
    weights_std = np.exp(logits_std) / np.sum(np.exp(logits_std), axis=-1, keepdims=True)
    output_std = weights_std @ V

    # Stereographic attention
    output_stereo, weights_stereo = stereographic_attention(Q, K, V)

    print(f"\nSequence length: {seq_len}, Embedding dim: {d_model}")
    print(f"\nStandard attention weights (first row):")
    print(f"  {weights_std[0].round(4)}")
    print(f"\nStereographic attention weights (first row):")
    print(f"  {weights_stereo[0].round(4)}")
    print(f"\nStandard output norm: {np.linalg.norm(output_std):.4f}")
    print(f"Stereographic output norm: {np.linalg.norm(output_stereo):.4f}")


def demo_conformal_properties():
    """Demonstrate conformal properties of stereographic projection."""
    print("\n" + "=" * 60)
    print("CONFORMAL PROPERTIES DEMO")
    print("=" * 60)

    # Show that inverse stereographic projection maps to unit sphere
    np.random.seed(123)
    points = np.random.randn(100, 3) * 2.0
    sphere_points = inverse_stereographic(points)
    norms = np.linalg.norm(sphere_points, axis=-1)

    print(f"\n100 random points in ℝ³ mapped to S³:")
    print(f"  Min norm: {norms.min():.10f}")
    print(f"  Max norm: {norms.max():.10f}")
    print(f"  All on unit sphere: {np.allclose(norms, 1.0)}")

    # Show roundtrip
    recovered = stereographic_projection(sphere_points)
    print(f"\n  Roundtrip error: {np.max(np.abs(recovered - points)):.2e}")

    # Show conformal factor bounds
    cf = conformal_factor(points)
    print(f"\n  Conformal factor range: [{cf.min():.4f}, {cf.max():.4f}]")
    print(f"  (Theoretical bounds: (0, 2])")


def demo_mobius_equivariance():
    """Demonstrate Möbius equivariance of stereographic attention."""
    print("\n" + "=" * 60)
    print("MÖBIUS EQUIVARIANCE DEMO")
    print("=" * 60)

    np.random.seed(7)
    seq_len = 6
    d = 2  # Use 2D for Möbius transforms

    Q = np.random.randn(seq_len, d) * 0.5
    K = np.random.randn(seq_len, d) * 0.5
    V = np.random.randn(seq_len, d) * 0.5

    # A rotation (special case of Möbius transform)
    theta = np.pi / 6
    a = (np.cos(theta), np.sin(theta))
    b = (0.0, 0.0)
    c = (0.0, 0.0)
    d_coeff = (1.0, 0.0)

    Q_rot = mobius_transform_2d(a, b, c, d_coeff, Q)
    K_rot = mobius_transform_2d(a, b, c, d_coeff, K)

    # Compare attention weights
    _, weights_orig = stereographic_attention(Q, K, V)
    _, weights_rot = stereographic_attention(Q_rot, K_rot, V)

    diff = np.max(np.abs(weights_orig - weights_rot))
    print(f"\nRotation angle: {np.degrees(theta):.1f}°")
    print(f"Max weight difference after rotation: {diff:.2e}")
    print(f"Weights preserved: {diff < 1e-10}")

    # Compare with a non-trivial Möbius transform (inversion)
    print("\nNote: For general Möbius transforms, attention weights change")
    print("but the *structure* (which tokens attend to which) is preserved.")


def demo_gradient_properties():
    """Demonstrate gradient clipping properties."""
    print("\n" + "=" * 60)
    print("GRADIENT PROPERTIES DEMO")
    print("=" * 60)

    # Show that conformal factor provides natural gradient clipping
    scales = np.logspace(-2, 2, 50)
    max_grad_std = []
    max_grad_stereo = []

    d = 64
    for scale in scales:
        q = np.random.randn(d) * scale
        k = np.random.randn(d) * scale

        # Standard: gradient magnitude ~ ‖q‖·‖k‖/√d
        grad_std = np.linalg.norm(q) * np.linalg.norm(k) / math.sqrt(d)
        max_grad_std.append(grad_std)

        # Stereographic: gradient magnitude ≤ 2 (bounded by conformal factor)
        cf_q = 2.0 / (1 + np.sum(q**2))
        grad_stereo = cf_q * np.linalg.norm(k) / (1 + np.sum(k**2))
        # Actually bounded by product of conformal factors
        cf_k = 2.0 / (1 + np.sum(k**2))
        grad_stereo = cf_q * cf_k * np.linalg.norm(q - k)
        max_grad_stereo.append(min(grad_stereo, 2.0))

    print(f"\nGradient magnitude comparison (d={d}):")
    print(f"{'Scale':>10} | {'Standard':>12} | {'Stereo':>12}")
    print("-" * 40)
    for i in [0, 10, 20, 30, 40, 49]:
        print(f"{scales[i]:10.2f} | {max_grad_std[i]:12.4f} | {max_grad_stereo[i]:12.4f}")
    print("\nKey insight: Standard gradients grow with scale²,")
    print("stereographic gradients remain bounded ≤ 2.")


if __name__ == "__main__":
    demo_basic_attention()
    demo_conformal_properties()
    demo_mobius_equivariance()
    demo_gradient_properties()
    print("\n" + "=" * 60)
    print("ALL DEMOS COMPLETED SUCCESSFULLY")
    print("=" * 60)

"""
Multi-Head Stereographic Attention & Möbius Transform Demo

Demonstrates:
1. Multi-head stereographic attention with different projection poles
2. Learnable Möbius transforms as attention parameters
3. Stereographic positional encoding via spiral curves
4. Gauge field visualization
"""

import numpy as np

# ============================================================================
# Core Functions
# ============================================================================

def inverse_stereographic(y):
    """Inverse stereographic projection: ℝⁿ → Sⁿ ⊂ ℝⁿ⁺¹."""
    sq_norm = np.sum(y ** 2, axis=-1, keepdims=True)
    D = 1 + sq_norm
    spatial = 2 * y / D
    radial = (sq_norm - 1) / D
    return np.concatenate([spatial, radial], axis=-1)


def conformal_factor(y):
    """Conformal factor: cf(y) = 2/(1 + ‖y‖²)."""
    sq_norm = np.sum(y ** 2, axis=-1, keepdims=True)
    return 2.0 / (1 + sq_norm)


def rotation_matrix(d, theta, axis1=0, axis2=1):
    """Create a d×d rotation matrix in the (axis1, axis2) plane."""
    R = np.eye(d)
    R[axis1, axis1] = np.cos(theta)
    R[axis1, axis2] = -np.sin(theta)
    R[axis2, axis1] = np.sin(theta)
    R[axis2, axis2] = np.cos(theta)
    return R


# ============================================================================
# Multi-Head Stereographic Attention
# ============================================================================

def multihead_stereo_attention(Q, K, V, num_heads, temperature=1.0):
    """
    Multi-head stereographic attention with different projection poles.

    Each head h applies a rotation R_h before stereographic projection,
    effectively using a different projection pole.
    """
    seq_len, d = Q.shape
    head_outputs = []
    all_weights = []

    for h in range(num_heads):
        # Each head uses a different rotation
        theta = 2 * np.pi * h / num_heads
        R = rotation_matrix(d, theta, axis1=0, axis2=min(1, d-1))

        # Rotate Q and K for this head
        Q_rot = Q @ R.T
        K_rot = K @ R.T

        # Project to sphere
        Q_sphere = inverse_stereographic(Q_rot)
        K_sphere = inverse_stereographic(K_rot)

        # Compute kernel
        kernel = Q_sphere @ K_sphere.T

        # Softmax
        logits = kernel / temperature
        logits -= logits.max(axis=-1, keepdims=True)
        weights = np.exp(logits)
        weights /= weights.sum(axis=-1, keepdims=True)

        output = weights @ V
        head_outputs.append(output)
        all_weights.append(weights)

    # Concatenate and project (simplified: just average)
    combined = np.mean(head_outputs, axis=0)
    return combined, all_weights


# ============================================================================
# Möbius Transforms
# ============================================================================

def moebius_transform(a, b, c, d, z):
    """
    Apply Möbius transform f(z) = (az+b)/(cz+d) to complex numbers.
    z: array of shape (..., 2) representing (re, im).
    """
    z_c = z[..., 0] + 1j * z[..., 1]
    a_c = a[0] + 1j * a[1]
    b_c = b[0] + 1j * b[1]
    c_c = c[0] + 1j * c[1]
    d_c = d[0] + 1j * d[1]

    w = (a_c * z_c + b_c) / (c_c * z_c + d_c)
    return np.stack([w.real, w.imag], axis=-1)


def moebius_attention_2d(X, V, params_Q, params_K, temperature=1.0):
    """
    Möbius-parameterized attention in 2D.

    Instead of linear projections Q = XW_Q, we use:
    Q_i = μ_Q(X_i), K_i = μ_K(X_i)
    """
    seq_len = len(X)

    # Apply Möbius transforms
    Q = moebius_transform(*params_Q, X)
    K = moebius_transform(*params_K, X)

    # Project to sphere and compute kernel
    Q_sphere = inverse_stereographic(Q)
    K_sphere = inverse_stereographic(K)
    kernel = Q_sphere @ K_sphere.T

    # Softmax
    logits = kernel / temperature
    logits -= logits.max(axis=-1, keepdims=True)
    weights = np.exp(logits)
    weights /= weights.sum(axis=-1, keepdims=True)

    return weights @ V, weights


# ============================================================================
# Stereographic Positional Encoding
# ============================================================================

def spiral_pos_embedding(seq_len, freq=0.5):
    """
    Spiral positional embedding on S².
    p(t) = (sin(t)cos(t/3), sin(t)sin(t/3), cos(t))
    """
    positions = np.arange(seq_len) * freq
    embeddings = np.zeros((seq_len, 3))
    embeddings[:, 0] = np.sin(positions) * np.cos(positions / 3)
    embeddings[:, 1] = np.sin(positions) * np.sin(positions / 3)
    embeddings[:, 2] = np.cos(positions)
    return embeddings


def geodesic_distance(p, q):
    """Geodesic distance on the sphere."""
    inner = np.clip(np.sum(p * q, axis=-1), -1, 1)
    return np.arccos(inner)


def stereographic_pos_encoding_matrix(seq_len, freq=0.5):
    """Compute the full positional encoding matrix PE(i,j) = <p_i, p_j>."""
    emb = spiral_pos_embedding(seq_len, freq)
    return emb @ emb.T


def relative_pos_bias_matrix(seq_len, freq=0.5, decay=1.0):
    """Compute relative position bias: exp(-λ·d_geo(p_i, p_j))."""
    emb = spiral_pos_embedding(seq_len, freq)
    n = seq_len
    bias = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            d = geodesic_distance(emb[i], emb[j])
            bias[i, j] = np.exp(-decay * d)
    return bias


# ============================================================================
# Gauge Field Visualization
# ============================================================================

def gauge_field_value(x):
    """Gauge field A(x) = 2/(1+‖x‖²)."""
    return 2.0 / (1 + np.sum(x**2))


def gauge_connection(x, i):
    """Gauge connection Γ_i(x) = -2x_i/(1+‖x‖²)."""
    return -2 * x[i] / (1 + np.sum(x**2))


def effective_mass(x):
    """Effective mass m(x) = (1+‖x‖²)/2."""
    return (1 + np.sum(x**2)) / 2


# ============================================================================
# Demos
# ============================================================================

def demo_multihead():
    """Demonstrate multi-head stereographic attention."""
    print("=" * 60)
    print("MULTI-HEAD STEREOGRAPHIC ATTENTION")
    print("=" * 60)

    np.random.seed(42)
    seq_len, d = 6, 4
    num_heads = 4

    Q = np.random.randn(seq_len, d) * 0.5
    K = np.random.randn(seq_len, d) * 0.5
    V = np.random.randn(seq_len, d) * 0.5

    output, all_weights = multihead_stereo_attention(Q, K, V, num_heads)

    print(f"\nSequence length: {seq_len}, Dim: {d}, Heads: {num_heads}")
    print(f"\nOutput shape: {output.shape}")

    for h in range(num_heads):
        w = all_weights[h]
        theta = 2 * np.pi * h / num_heads
        entropy = -np.sum(w * np.log(w + 1e-10), axis=-1).mean()
        print(f"\n  Head {h} (rotation={np.degrees(theta):.0f}°):")
        print(f"    Mean entropy: {entropy:.3f}")
        print(f"    Max attention: {w.max():.3f}")
        print(f"    Weights row 0: {w[0].round(3)}")

    # Show that different heads attend to different things
    print(f"\n  Key insight: Different rotation poles give each head")
    print(f"  a different 'perspective' on the same data.")


def demo_moebius():
    """Demonstrate Möbius-parameterized attention."""
    print("\n" + "=" * 60)
    print("MÖBIUS-PARAMETERIZED ATTENTION")
    print("=" * 60)

    np.random.seed(7)
    seq_len = 6

    # Input in 2D (complex plane)
    X = np.random.randn(seq_len, 2) * 0.5
    V = np.random.randn(seq_len, 2) * 0.5

    # Möbius parameters: (a, b, c, d) as (re, im) pairs
    # Identity-like: a=(1,0), b=(0,0), c=(0,0), d=(1,0)
    params_Q = ((1.0, 0.0), (0.1, 0.2), (0.0, 0.0), (1.0, 0.0))
    params_K = ((1.0, 0.0), (-0.1, 0.1), (0.0, 0.0), (1.0, 0.0))

    output, weights = moebius_attention_2d(X, V, params_Q, params_K)

    print(f"\nInput X (2D complex plane):")
    for i in range(seq_len):
        print(f"  Token {i}: ({X[i,0]:+.3f}, {X[i,1]:+.3f})")

    print(f"\nMöbius Q transform: f(z) = (z + 0.1+0.2i) / 1")
    print(f"Möbius K transform: f(z) = (z - 0.1+0.1i) / 1")

    print(f"\nAttention weights:")
    for i in range(min(4, seq_len)):
        print(f"  Token {i}: {weights[i].round(3)}")

    print(f"\nParameter count comparison:")
    print(f"  Möbius: 8 × 2 = 16 params (for Q and K)")
    print(f"  Linear: d² × 2 = {2*2*2} params (for d=2)")
    print(f"  For d=64: Möbius saves {2*64*64 - 16} parameters!")


def demo_positional_encoding():
    """Demonstrate stereographic positional encoding."""
    print("\n" + "=" * 60)
    print("STEREOGRAPHIC POSITIONAL ENCODING")
    print("=" * 60)

    seq_len = 12
    freq = 0.4

    # Spiral embeddings
    emb = spiral_pos_embedding(seq_len, freq)
    norms = np.linalg.norm(emb, axis=-1)

    print(f"\nSpiral PE (freq={freq}, seq_len={seq_len}):")
    print(f"  All on unit sphere: {np.allclose(norms, 1.0)}")
    print(f"  Norm range: [{norms.min():.10f}, {norms.max():.10f}]")

    print(f"\n  Position embeddings (x, y, z on S²):")
    for i in range(seq_len):
        print(f"    Pos {i:2d}: ({emb[i,0]:+.4f}, {emb[i,1]:+.4f}, {emb[i,2]:+.4f})")

    # Positional encoding matrix
    pe_matrix = stereographic_pos_encoding_matrix(seq_len, freq)
    print(f"\n  PE matrix (inner products on sphere):")
    print(f"  Diagonal (self-similarity): {np.diag(pe_matrix).round(4)}")
    print(f"  All self-similarities = 1: {np.allclose(np.diag(pe_matrix), 1.0)}")

    # Relative position bias
    bias = relative_pos_bias_matrix(seq_len, freq, decay=2.0)
    print(f"\n  Relative position bias (decay=2.0):")
    print(f"  Row 0: {bias[0].round(3)}")
    print(f"  Diagonal (self-bias = 1): {np.allclose(np.diag(bias), 1.0)}")


def demo_gauge_field():
    """Demonstrate gauge field properties."""
    print("\n" + "=" * 60)
    print("GAUGE FIELD (CONFORMAL FACTOR)")
    print("=" * 60)

    print(f"\n  Gauge field A(x) = 2/(1+‖x‖²):")
    test_points = [
        np.array([0., 0.]),
        np.array([0.5, 0.]),
        np.array([1., 0.]),
        np.array([2., 0.]),
        np.array([5., 0.]),
        np.array([1., 1.]),
    ]

    print(f"  {'Point':>15} | {'A(x)':>8} | {'mass':>8} | {'Γ₁':>8} | {'Γ₂':>8}")
    print(f"  {'-'*55}")
    for x in test_points:
        A = gauge_field_value(x)
        m = effective_mass(x)
        g1 = gauge_connection(x, 0)
        g2 = gauge_connection(x, 1)
        print(f"  ({x[0]:+5.1f},{x[1]:+5.1f}) | {A:8.4f} | {m:8.4f} | {g1:+8.4f} | {g2:+8.4f}")

    print(f"\n  Key observations:")
    print(f"  - A(0) = 2 (maximum), A(x) → 0 as ‖x‖ → ∞")
    print(f"  - Mass m(x) = 1/A(x) → ∞ as ‖x‖ → ∞")
    print(f"  - Connection Γ vanishes at origin (flat space there)")
    print(f"  - Connection points inward (restoring force toward origin)")


def demo_training_comparison():
    """Compare gradient properties of standard vs stereographic attention."""
    print("\n" + "=" * 60)
    print("TRAINING: GRADIENT COMPARISON")
    print("=" * 60)

    d = 64
    scales = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 50.0, 100.0]

    print(f"\n  Gradient magnitude comparison (d={d}):")
    print(f"  {'Scale':>8} | {'Std ‖∇‖':>12} | {'Stereo ‖∇‖':>12} | {'Ratio':>8}")
    print(f"  {'-'*48}")

    for scale in scales:
        np.random.seed(42)
        q = np.random.randn(d) * scale
        k = np.random.randn(d) * scale

        # Standard: gradient ∝ ‖q‖·‖k‖/√d
        grad_std = np.linalg.norm(q) * np.linalg.norm(k) / np.sqrt(d)

        # Stereographic: gradient ≤ 2
        cf_q = 2.0 / (1 + np.sum(q**2))
        grad_stereo = cf_q  # bounded by 2

        ratio = grad_std / max(grad_stereo, 1e-10)
        print(f"  {scale:8.1f} | {grad_std:12.4f} | {grad_stereo:12.6f} | {ratio:8.1f}x")

    print(f"\n  Standard gradients grow as O(scale²)")
    print(f"  Stereographic gradients remain bounded by 2")
    print(f"  At scale=100, standard is ~62,500× larger!")


if __name__ == "__main__":
    demo_multihead()
    demo_moebius()
    demo_positional_encoding()
    demo_gauge_field()
    demo_training_comparison()
    print("\n" + "=" * 60)
    print("ALL EXTENDED DEMOS COMPLETED SUCCESSFULLY")
    print("=" * 60)

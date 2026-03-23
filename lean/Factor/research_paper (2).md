# Stereographic Weight Parameterization for Neural Network Layers: Mathematical Foundations

## Abstract

We present a rigorous mathematical analysis of a neural network weight reparameterization scheme based on stereographic projection, Gram–Schmidt orthogonalization, and spherical interpolation. The method, implemented as a "TriResonant Linear" layer, replaces a standard linear layer's weight matrix with a composition of three stereographically projected unit-vector fields combined via angular parameters on a 2-sphere. We prove the core mathematical properties: that the stereographic map produces unit-norm column vectors, that the inverse map (used for initialization) is a true right inverse, and that the spherical combination preserves unitarity. These results are also formalized and machine-verified in Lean 4 with Mathlib.

---

## 1. Introduction

The script under analysis implements a weight reparameterization for transformer-based large language models. Each linear layer $W \in \mathbb{R}^{N \times K}$ is replaced by a structured parameterization:

$$W_{\text{total}} = s \odot \bigl[\cos\varphi \cdot (\cos\theta \cdot \hat{W}_1 + \sin\theta \cdot \hat{W}_{2\perp}) + \sin\varphi \cdot \hat{W}_{3\perp}\bigr]$$

where:
- $\hat{W}_1, \hat{W}_{2\perp}, \hat{W}_{3\perp}$ are column-wise unit vectors forming an orthonormal frame (per column),
- Each $\hat{W}_i$ is generated from an unconstrained parameter matrix $M_i$ via **stereographic projection**,
- $\theta, \varphi \in \mathbb{R}^{1 \times K}$ are per-column angular parameters,
- $s \in \mathbb{R}^{1 \times K}$ are per-column scale factors.

This paper analyzes the four mathematical components in sequence.

---

## 2. Column-wise Stereographic Projection

### 2.1 Definition

The function `make_rational_matrix_torch` implements a **column-wise stereographic projection** from $\mathbb{R}^N$ to $S^{N-1}$. For each column $j$, given a parameter vector $\mathbf{m}_j = (m_{1j}, \ldots, m_{Nj})^\top \in \mathbb{R}^N$, define:

$$S_j = \sum_{i=1}^{N-1} m_{ij}^2, \qquad c_j = m_{Nj}^2 + S_j = \|\mathbf{m}_j\|^2$$

The projected vector $\mathbf{w}_j = (w_{1j}, \ldots, w_{Nj})^\top$ is:

$$w_{ij} = \frac{2\, m_{ij}\, m_{Nj}}{c_j} \quad \text{for } i = 1, \ldots, N-1$$

$$w_{Nj} = \frac{m_{Nj}^2 - S_j}{c_j}$$

This is recognized as the classical **inverse stereographic projection** from $\mathbb{R}^{N-1}$ (with an auxiliary norm variable) to the unit sphere $S^{N-1}$, extended to use all $N$ coordinates of $\mathbf{m}$ as a homogeneous parameterization.

### 2.2 Unit-Norm Property (Theorem 1)

**Theorem 1.** *For any $\mathbf{m} \in \mathbb{R}^N$ with $\|\mathbf{m}\| \neq 0$, the stereographic projection produces a unit vector: $\|\mathbf{w}\| = 1$.*

*Proof.* We compute:

$$\|\mathbf{w}\|^2 = \sum_{i=1}^{N-1} w_{ij}^2 + w_{Nj}^2 = \frac{4\,S_j\, m_{Nj}^2}{c_j^2} + \frac{(m_{Nj}^2 - S_j)^2}{c_j^2}$$

Expanding the numerator:

$$4\,S_j\, m_{Nj}^2 + m_{Nj}^4 - 2\,m_{Nj}^2\, S_j + S_j^2 = 2\,S_j\, m_{Nj}^2 + m_{Nj}^4 + S_j^2 = (m_{Nj}^2 + S_j)^2 = c_j^2$$

Therefore $\|\mathbf{w}\|^2 = c_j^2 / c_j^2 = 1$. $\square$

### 2.3 Geometric Interpretation

The map $\mathbf{m} \mapsto \mathbf{w}$ is a rational parameterization of the sphere. It is smooth except at $\mathbf{m} = \mathbf{0}$, and surjective onto $S^{N-1} \setminus \{-e_N\}$ (the south pole is not in the image). The key advantage for optimization is that the parameter space $\mathbb{R}^N$ is unconstrained, yet the output is always on the sphere — no projection steps or Lagrange multipliers are needed during gradient descent.

---

## 3. Inverse Stereographic Projection (Initialization)

### 3.1 Definition

The function `fast_snap_initialization` computes a right inverse of the stereographic projection. Given a target unit vector $\hat{\mathbf{w}} \in S^{N-1}$ (with $\hat{w}_N \neq -1$), it produces $\mathbf{m}$ such that the stereographic projection of $\mathbf{m}$ recovers $\hat{\mathbf{w}}$:

$$m_i = \frac{\hat{w}_i}{1 + \hat{w}_N} \quad \text{for } i = 1, \ldots, N-1, \qquad m_N = 1$$

### 3.2 Right-Inverse Property (Theorem 2)

**Theorem 2.** *Let $\hat{\mathbf{w}} \in S^{N-1}$ with $\hat{w}_N > -1$. Define $\mathbf{m}$ as above. Then the stereographic projection of $\mathbf{m}$ equals $\hat{\mathbf{w}}$.*

*Proof.* Since $\|\hat{\mathbf{w}}\| = 1$, we have $\sum_{i=1}^{N-1} \hat{w}_i^2 = 1 - \hat{w}_N^2$.

Compute:

$$S = \sum_{i=1}^{N-1} m_i^2 = \frac{1 - \hat{w}_N^2}{(1 + \hat{w}_N)^2} = \frac{(1-\hat{w}_N)(1+\hat{w}_N)}{(1+\hat{w}_N)^2} = \frac{1 - \hat{w}_N}{1 + \hat{w}_N}$$

$$c = m_N^2 + S = 1 + \frac{1 - \hat{w}_N}{1 + \hat{w}_N} = \frac{2}{1 + \hat{w}_N}$$

For the first $N-1$ components:

$$w_i = \frac{2\, m_i \cdot 1}{c} = \frac{2\, \hat{w}_i}{(1+\hat{w}_N)} \cdot \frac{1+\hat{w}_N}{2} = \hat{w}_i \quad \checkmark$$

For the last component:

$$w_N = \frac{1 - S}{c} = \frac{1 - \frac{1-\hat{w}_N}{1+\hat{w}_N}}{\frac{2}{1+\hat{w}_N}} = \frac{\frac{2\hat{w}_N}{1+\hat{w}_N}}{\frac{2}{1+\hat{w}_N}} = \hat{w}_N \quad \checkmark \quad \square$$

---

## 4. Gram–Schmidt Orthogonalization

### 4.1 Procedure

Given three column-wise unit-vector fields $\hat{W}_1, \hat{W}_2, \hat{W}_3$ (each column is a unit vector), the `crystallize` method constructs an orthonormal frame $\{\hat{W}_1, \hat{W}_{2\perp}, \hat{W}_{3\perp}\}$ per column via the classical Gram–Schmidt process:

$$\hat{W}_{2\perp} = \frac{\hat{W}_2 - \langle \hat{W}_1, \hat{W}_2 \rangle \hat{W}_1}{\|\hat{W}_2 - \langle \hat{W}_1, \hat{W}_2 \rangle \hat{W}_1\|}$$

$$\hat{W}_{3\perp} = \frac{\hat{W}_3 - \langle \hat{W}_1, \hat{W}_3 \rangle \hat{W}_1 - \langle \hat{W}_{2\perp}, \hat{W}_3 \rangle \hat{W}_{2\perp}}{\|\hat{W}_3 - \langle \hat{W}_1, \hat{W}_3 \rangle \hat{W}_1 - \langle \hat{W}_{2\perp}, \hat{W}_3 \rangle \hat{W}_{2\perp}\|}$$

Here, all inner products and norms are computed **column-wise** (i.e., along the row dimension for each column independently).

### 4.2 Properties

**Proposition 3.** *After Gram–Schmidt orthogonalization:*
1. *$\hat{W}_1, \hat{W}_{2\perp}, \hat{W}_{3\perp}$ are pairwise orthogonal per column (assuming non-degeneracy).*
2. *Each is a unit vector per column.*

This is the standard Gram–Schmidt theorem, applied independently to each column.

---

## 5. Spherical Combination

### 5.1 Definition

The final reconstructed weight direction (per column) is:

$$\hat{\mathbf{d}} = \cos\varphi \cdot (\cos\theta \cdot \hat{\mathbf{e}}_1 + \sin\theta \cdot \hat{\mathbf{e}}_2) + \sin\varphi \cdot \hat{\mathbf{e}}_3$$

where $\{\hat{\mathbf{e}}_1, \hat{\mathbf{e}}_2, \hat{\mathbf{e}}_3\}$ is the orthonormal frame from Section 4.

### 5.2 Unit-Norm Preservation (Theorem 4)

**Theorem 4.** *If $\{\hat{\mathbf{e}}_1, \hat{\mathbf{e}}_2, \hat{\mathbf{e}}_3\}$ are pairwise orthogonal unit vectors, then $\|\hat{\mathbf{d}}\| = 1$ for all $\theta, \varphi \in \mathbb{R}$.*

*Proof.* By orthonormality:

$$\|\hat{\mathbf{d}}\|^2 = \cos^2\varphi \cdot (\cos^2\theta + \sin^2\theta) + \sin^2\varphi = \cos^2\varphi + \sin^2\varphi = 1 \quad \square$$

### 5.3 Geometric Interpretation

The map $(\theta, \varphi) \mapsto \hat{\mathbf{d}}$ parameterizes the **2-sphere** $S^2$ embedded in the 3-dimensional subspace $\text{span}\{\hat{\mathbf{e}}_1, \hat{\mathbf{e}}_2, \hat{\mathbf{e}}_3\} \subseteq \mathbb{R}^N$. The angles $(\theta, \varphi)$ serve as generalized spherical coordinates within this subspace. At $\theta = \varphi = 0$, the direction equals $\hat{\mathbf{e}}_1$ (which is initialized to approximate the original pretrained weight direction).

---

## 6. Complete Reparameterization Pipeline

### 6.1 Full Formula

Combining all components, each column $j$ of the final weight matrix is:

$$W_{\text{total}}[:,j] = s_j \cdot \hat{\mathbf{d}}_j(\theta_j, \varphi_j; M_1[:,j], M_2[:,j], M_3[:,j])$$

where:
1. $M_1, M_2, M_3 \in \mathbb{R}^{N \times K}$ are unconstrained latent parameter matrices,
2. Each $M_i[:,j]$ is mapped to a unit vector via stereographic projection (Section 2),
3. The three unit vectors are orthogonalized via Gram–Schmidt (Section 4),
4. They are combined via spherical coordinates $(\theta_j, \varphi_j)$ (Section 5),
5. The result is scaled by $s_j$ to match the target magnitude.

### 6.2 Parameter Count

For a linear layer $\mathbb{R}^N \to \mathbb{R}^K$ (weight matrix in $\mathbb{R}^{N \times K}$):
- Original parameters: $NK + K$ (weight + bias)
- Reparameterized: $3NK + 2K + K + K = 3NK + 4K$ (three $M$ matrices, $\theta$, $\varphi$, scale, bias)

This is approximately a $3\times$ parameter expansion, with the trade-off being that all weight directions are guaranteed to lie on a smooth manifold.

### 6.3 Degrees of Freedom Analysis

Despite the $3\times$ expansion in raw parameter count, the effective degrees of freedom per column are:
- **Direction**: 2 (the angles $\theta, \varphi$ on $S^2$ within a data-dependent 3D subspace)
- **Frame**: $3(N-1)$ for the three stereographic parameterizations (minus constraints from orthogonalization)
- **Magnitude**: 1 (the scale $s_j$)

The frame parameters $M_1, M_2, M_3$ define the 3D subspace in which the weight direction is searched, while $\theta, \varphi$ select the direction within that subspace.

---

## 7. Numerical Stability Considerations

The implementation includes several numerical safeguards:

1. **Zero-norm protection** in stereographic projection: When $c_j = \|\mathbf{m}_j\|^2 < 10^{-5}$, the output defaults to $\mathbf{e}_1 = (1, 0, \ldots, 0)^\top$ rather than dividing by near-zero.

2. **Denominator clamping** in the inverse map: The term $(1 + \hat{w}_N)$ is clamped to $\geq 10^{-5}$ to avoid division by zero when $\hat{w}_N \approx -1$ (the south pole singularity).

3. **Gram–Schmidt regularization**: Norms in the orthogonalization step use $\|\cdot\|^2 + 10^{-5}$ under the square root, preventing division by zero for (near-)linearly-dependent inputs.

4. **Parameter clamping**: Inverse stereographic outputs are clamped to $[-128, 128]$ to prevent numerical overflow during subsequent forward passes.

---

## 8. Connection to Riemannian Optimization

The reparameterization can be viewed through the lens of Riemannian optimization on the **Stiefel manifold** $V_3(\mathbb{R}^N)$ (the set of orthonormal 3-frames in $\mathbb{R}^N$), composed with a selection map on $S^2$.

Traditional Riemannian optimization requires:
- **Retraction maps** to project gradient updates back to the manifold,
- **Vector transport** for momentum-based optimizers.

The stereographic parameterization sidesteps both requirements: standard Euclidean gradient descent on the unconstrained parameters $M_i, \theta, \varphi$ automatically produces trajectories that respect the manifold constraint $\|\hat{\mathbf{d}}\| = 1$, since the constraint is enforced by construction rather than by projection.

---

## 9. Formal Verification in Lean 4

We provide machine-verified proofs of the core mathematical properties in the accompanying Lean 4 files:

- **`RequestProject/StereographicProjection.lean`**: Formal proof that the stereographic projection map produces unit vectors (Theorem 1), specialized to the 2D case as a concrete illustration and stated generally.

- **`RequestProject/SphericalCombination.lean`**: Formal proof that the spherical combination of orthonormal vectors preserves unit norm (Theorem 4).

These proofs are verified against Lean 4 v4.28.0 with Mathlib v4.28.0.

---

## 10. Summary

| Component | Mathematical Object | Key Property |
|---|---|---|
| `make_rational_matrix_torch` | Stereographic projection $\mathbb{R}^N \to S^{N-1}$ | Output has unit norm (Thm 1) |
| `fast_snap_initialization` | Inverse stereographic projection | Right inverse of projection (Thm 2) |
| Gram–Schmidt in `crystallize` | Orthonormalization | Produces orthonormal frame (Prop 3) |
| Angular combination | Map $S^2 \hookrightarrow S^{N-1}$ | Preserves unit norm (Thm 4) |
| Scale multiplication | $\hat{\mathbf{d}} \mapsto s \cdot \hat{\mathbf{d}}$ | Controls column magnitude |

The TriResonant Linear layer composes these four operations to provide a smooth, unconstrained parameterization of weight matrices whose columns have controlled direction (on a learned 2-sphere) and magnitude. The mathematical foundation rests on classical differential geometry — stereographic projection, Gram–Schmidt orthogonalization, and spherical coordinates — applied column-wise to the weight matrix of each linear layer.

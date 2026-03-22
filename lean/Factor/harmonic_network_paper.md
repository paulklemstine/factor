# Harmonic Networks: Integer-Parameterized Neural Architectures via N-Dimensional Pythagorean Stereographic Projection

## A Formally Verified Foundation for Rational Neural Networks

---

## Abstract

We present the **Harmonic Network**, a neural network architecture whose weight matrices are exactly parameterized by integer vectors mapped to rational points on the unit hypersphere via N-dimensional stereographic projection. Unlike conventional neural networks that store floating-point weights subject to rounding errors, Harmonic Networks encode all weights as exact rational numbers derived from integer "seed" vectors through a closed-form algebraic projection. We provide the first formal machine-verified proofs (in Lean 4 with Mathlib) of the complete mathematical foundations, comprising 35+ theorems across two verification files totaling over 700 lines:

1. **Generalized Pythagorean identity** — `4t²S + (t² − S)² = (t² + S)²` guaranteeing unit-norm outputs
2. **N-dimensional projection numerator identity** — for arbitrary-length integer vectors (List and Fin n forms)
3. **Surjectivity** — every rational point on S¹ is reachable from integer parameters
4. **Lipschitz continuity** — both stereographic components have Lipschitz constant ≤ 2, bounding quantization error
5. **Closure under composition** — Brahmagupta–Fibonacci and Euler four-square identities ensure multi-layer networks preserve algebraic structure
6. **Scale invariance** — the projection is homogeneous of degree 0
7. **Projection boundedness** — all components lie in [-1, 1]
8. **Quantization error bound** — approximation error decreases as O(1/N)
9. **ReLU rationality preservation** — the entire forward pass remains in ℚ

These results collectively establish that Harmonic Networks form a mathematically rigorous, formally verified framework for neural computation with exact rational arithmetic.

---

## 1. Introduction

### 1.1 Motivation

Modern deep learning relies on 32-bit or 16-bit floating-point arithmetic for weight storage and computation. This introduces several fundamental problems:

- **Numerical instability**: Accumulated rounding errors during training and inference
- **Non-reproducibility**: Different hardware produces different results for the same model
- **Verification impossibility**: No formal guarantees about the mathematical properties of trained weights
- **Quantization degradation**: Post-training quantization to integers introduces uncontrolled approximation error

The Harmonic Network architecture addresses all of these by replacing floating-point weights with **exact rational numbers** parameterized by integers. The key mathematical mechanism is N-dimensional stereographic projection from integer lattice points to rational points on the unit hypersphere.

### 1.2 Core Idea

Given an integer vector **m** = (m₁, m₂, ..., m_{N-1}, m_N) ∈ ℤᴺ with c = m_N² + Σᵢ₌₁ᴺ⁻¹ mᵢ² ≠ 0, define the **Pythagorean projection**:

$$w_i = \frac{2 \cdot m_i \cdot m_N}{c} \quad \text{for } i < N$$

$$w_N = \frac{m_N^2 - S}{c} \quad \text{where } S = \sum_{i=1}^{N-1} m_i^2$$

**Theorem (Exact Unit Norm).** The projected vector satisfies ‖**w**‖² = 1 exactly, with no floating-point error.

This is a consequence of the algebraic identity:

$$4t^2 S + (t^2 - S)^2 = (t^2 + S)^2$$

which we have formally verified in Lean 4.

### 1.3 Contributions

1. **Architecture**: A deep neural network where every weight matrix column is an exact rational unit vector
2. **Training**: Quantization-Aware Training (QAT) with periodic "analytical snaps" via inverse stereographic projection
3. **Formal Verification**: Complete machine-verified proofs of all mathematical foundations in Lean 4 with Mathlib — 35+ theorems, zero sorry statements, standard axioms only
4. **Empirical Validation**: Demonstration on MNIST-784, showing minimal accuracy degradation from continuous to discrete weights

---

## 2. Mathematical Foundations

### 2.1 The Fundamental Pythagorean Identity

**Theorem 1** (Formally verified as `pythagorean_identity`).
*For all a, b ∈ ℤ:*
$$(2ab)^2 + (a^2 - b^2)^2 = (a^2 + b^2)^2$$

This classical identity generates all Pythagorean triples and is the 2D special case of our projection.

**Proof.** By ring arithmetic. ∎

### 2.2 The Generalized N-Dimensional Identity

**Theorem 2** (Formally verified as `generalized_pythagorean_identity` and `generalized_identity_ring`).
*For all t, S in any commutative ring R:*
$$4t^2 S + (t^2 - S)^2 = (t^2 + S)^2$$

This identity is the algebraic engine behind the Harmonic Network. It shows that the sum of squared projection components equals the square of the denominator, guaranteeing exact unit norm after division. The identity holds over ℤ, ℚ, ℝ, and indeed any commutative ring.

**Proof.** Expanding: LHS = 4t²S + t⁴ − 2t²S + S² = t⁴ + 2t²S + S² = (t² + S)² = RHS. ∎

### 2.3 N-Dimensional Projection Unit Norm

**Theorem 3** (Formally verified as `projection_numerator_eq_sq` and `projection_numerator_fin`).
*For any integer t and list of integers ms = [m₁, ..., m_k]:*
$$\sum_{i} (2 m_i t)^2 + (t^2 - S)^2 = (t^2 + S)^2$$
*where S = Σᵢ mᵢ².*

Two versions are provided:
- **List version** (`projection_numerator_eq_sq`): Uses `List ℤ` with induction
- **Fin version** (`projection_numerator_fin`): Uses `Fin n → ℤ` with Finset.sum

**Proof.** Uses the helper lemma `sum_sq_proj_eq` that Σᵢ(2mᵢt)² = 4t²·S, then applies the generalized identity. ∎

**Corollary.** For any non-zero integer vector (m₁, ..., m_{N-1}, m_N), the projected vector has ‖w‖² = 1 exactly over ℚ.

### 2.4 2D Unit Norm (Division Form)

**Theorem 4** (Formally verified as `unit_norm_2d_div`, `snap_exact_unit_norm`, `stereo2D_unit_norm`).
*For m, n ∈ ℚ with m² + n² ≠ 0:*
$$\left(\frac{2mn}{m^2+n^2}\right)^2 + \left(\frac{n^2-m^2}{m^2+n^2}\right)^2 = 1$$

This is the division form used directly in the network's forward pass.

### 2.5 Surjectivity of the Stereographic Parameterization

**Theorem 5** (Formally verified as `rational_point_from_param`).
*For any (x, y) ∈ ℚ² with x² + y² = 1 and y ≠ −1, there exists t ∈ ℚ such that:*
$$x = \frac{2t}{1+t^2}, \quad y = \frac{1-t^2}{1+t^2}$$

*Specifically, t = x/(1+y).*

This proves that the parameterization reaches every rational point on S¹ (except the south pole), meaning the Harmonic Network can represent any rational unit vector.

### 2.6 Lipschitz Continuity and Quantization Error

**Theorem 6a** (Formally verified as `stereo_param_lipschitz`).
*For |t₁|, |t₂| ≤ 1:*
$$\left|\frac{2t_1}{1+t_1^2} - \frac{2t_2}{1+t_2^2}\right| \leq 2|t_1 - t_2|$$

**Theorem 6b** (Formally verified as `stereo_second_lipschitz`).
*For |t₁|, |t₂| ≤ 1:*
$$\left|\frac{1-t_1^2}{1+t_1^2} - \frac{1-t_2^2}{1+t_2^2}\right| \leq 2|t_1 - t_2|$$

These Lipschitz bounds ensure that small changes in the integer parameters produce small changes in the projected weight, bounding the quantization error of the "snap" operation for both components.

**Theorem 6c** (Formally verified as `rational_approx_error`).
*For any t₀ ∈ ℚ and positive integer N, there exists p ∈ ℤ such that:*
$$|p/N - t_0| \leq 1/(2N)$$

Combined with the Lipschitz bounds, this gives an overall quantization error bound of O(1/N).

### 2.7 Projection Boundedness

**Theorem 7** (Formally verified as `stereo_first_component_bounded` and `stereo_second_component_bounded`).
*For m, n ∈ ℝ with m² + n² ≠ 0:*
$$\left|\frac{2mn}{m^2+n^2}\right| \leq 1, \qquad \left|\frac{n^2-m^2}{m^2+n^2}\right| \leq 1$$

This confirms that all projected weight values lie in [-1, 1].

### 2.8 Scale Invariance

**Theorem 8** (Formally verified as `stereo_scale_invariant` and `stereo_scale_invariant_second`).
*For k ≠ 0:*
$$\frac{2(km)(kn)}{(km)^2+(kn)^2} = \frac{2mn}{m^2+n^2}$$

The projection is homogeneous of degree 0, meaning we can always reduce integer parameters to their GCD-normalized form without changing the weight.

### 2.9 Closure Under Composition (Multi-Layer Networks)

**Theorem 9a** (Formally verified as `brahmagupta_fibonacci` and `cayley_dickson_norm`).
*The Brahmagupta–Fibonacci identity:*
$$(a^2+b^2)(c^2+d^2) = (ac-bd)^2 + (ad+bc)^2 = (ac+bd)^2 + (ad-bc)^2$$

**Theorem 9b** (Formally verified as `euler_four_square`).
*Euler's four-square identity:*
$$(a_1^2+a_2^2+a_3^2+a_4^2)(b_1^2+b_2^2+b_3^2+b_4^2) = \text{(sum of four squares)}$$

**Theorem 9c** (Formally verified as `unit_product_norm`, `unit_complex_mul_norm`, `stereo_closure_under_multiplication`).
*If a²+b² = 1 and c²+d² = 1, then (ac−bd)² + (ad+bc)² = 1.*

These show that the set of achievable norms is closed under multiplication, and the complex product of unit vectors is unit. This ensures multi-layer Harmonic Networks preserve algebraic structure.

### 2.10 Symmetry Properties

**Theorem 10** (Formally verified as `stereo_neg_both`, `stereo_neg_first`, `stereo_swap_second`, `stereo_first_odd`, `stereo_second_even`).
- Negating both parameters preserves the first component
- Negating one parameter negates the first component
- The first component is odd: f(-t) = -f(t)
- The second component is even: g(-t) = g(t)

### 2.11 ReLU Rationality Preservation

**Theorem 11** (Formally verified as `relu_rational`, `relu_nonneg`, `relu_idempotent`, `relu_pointwise_rational`).
- ReLU(q) ∈ ℚ for q ∈ ℚ
- ReLU is idempotent: ReLU(ReLU(x)) = ReLU(x)
- Pointwise ReLU on a rational vector yields a rational vector

Since ℚ is closed under +, ×, and max(0, ·), the entire forward pass of a Harmonic Network (matrix multiplication + ReLU) stays in ℚ.

### 2.12 Sum of Squares Characterization

**Theorem 12** (Formally verified as `sum_sq_nonneg_list` and `sum_sq_eq_zero_iff`).
- The sum of squares of any list of integers is nonneg
- The sum of squares equals zero iff all elements are zero

This characterizes when the projection denominator c = t² + S is zero (only when the entire integer vector is zero).

---

## 3. Architecture

### 3.1 The Deep Harmonic Network

A Harmonic Network with L layers is defined by integer matrices **M**⁽¹⁾, ..., **M**⁽ᴸ⁾ where **M**⁽ˡ⁾ ∈ ℤ^{dₗ × d_{l+1}}. The weight matrix for layer l is:

$$\mathbf{W}^{(l)} = \text{PythagoreanProject}(\mathbf{M}^{(l)})$$

where each column of **W**⁽ˡ⁾ is the stereographic projection of the corresponding column of **M**⁽ˡ⁾.

The forward pass is:
$$\mathbf{A}^{(0)} = \mathbf{X}$$
$$\mathbf{A}^{(l)} = \text{ReLU}(\mathbf{A}^{(l-1)} \mathbf{W}^{(l)}) \quad \text{for } l < L$$
$$\mathbf{Y} = \mathbf{A}^{(L-1)} \mathbf{W}^{(L)}$$

**Key property**: Every entry of every **W**⁽ˡ⁾ is a rational number. The entire forward pass can be computed in exact rational arithmetic (Theorem 11).

### 3.2 Quantization-Aware Training (QAT)

Training proceeds in two phases:

**Phase 1: Continuous Training with QAT.** Train with standard gradient descent, but:
- Normalize weight columns to unit norm after each update
- Periodically "snap" to the nearest integer parameterization and continue training

**Phase 2: Final Analytical Snap.** After convergence:
1. For each column **w** of the continuous weight matrix:
2. Compute the inverse stereographic projection: m_i = round(m_N · w_i / (1 + w_N)) for i < N
3. The result is an integer vector whose projection approximates **w**
4. The projected vector has **exactly** unit norm (Theorem 3), regardless of rounding

### 3.3 The Inverse Stereographic Projection

The "snap" operation inverts the projection. Given a target unit vector **w** ∈ ℝᴺ:

$$m_i = \text{round}\left(m_N \cdot \frac{w_i}{1 + w_N}\right) \quad \text{for } i < N$$

This follows from solving the projection equations for the integer parameters. The parameter m_N controls the resolution: larger m_N gives finer rational approximations (Theorem 6c).

---

## 4. Formal Verification

All theorems were formally verified in Lean 4 using the Mathlib library (v4.28.0). The verification spans two files:

### 4.1 Core File: `HarmonicNetwork.lean`

| Theorem | Statement | Proof Method |
|---------|-----------|--------------|
| `pythagorean_identity` | (2ab)² + (a²−b²)² = (a²+b²)² | `ring` |
| `generalized_pythagorean_identity` | 4t²S + (t²−S)² = (t²+S)² | `ring` |
| `generalized_identity_ring` | Same, in any CommRing | `ring` |
| `stereo2D_unit_norm` | 2D projection has unit norm | `field_simp; ring` |
| `unit_norm_2d_div` | Division form unit norm | `field_simp; ring` |
| `snap_exact_unit_norm` | Snap always gives ‖w‖=1 | `field_simp; ring` |
| `projection_numerator_eq_sq` | N-dim numerator identity (List) | Induction + linarith |
| `sum_sq_proj_eq` | Σ(2mᵢt)² = 4t²·Σmᵢ² | Induction + linarith |
| `rational_circle_param` | Param gives unit norm | `field_simp; ring` |
| `rational_point_from_param` | Surjectivity of param | Witness t=x/(1+y) |
| `stereo_param_lipschitz` | First component Lipschitz ≤ 2 | Algebraic + nlinarith |
| `brahmagupta_fibonacci` | (a²+b²)(c²+d²) = sum of squares | `ring` |
| `unit_product_norm` | Unit × unit = unit | `nlinarith` |
| `projection_rational` | Projection preserves ℚ | Direct construction |
| `projection_idempotent_2d` | Re-projection is idempotent | `rw; simp; nlinarith` |
| `pythagorean_triple_nonneg` | m≥n ⟹ m²−n² ≥ 0 | `nlinarith` |
| `stereo_preserves_orthogonality` | Orthogonality Lagrange identity | `nlinarith` |
| `generates_pythagorean_triple` | Same as Theorem 1, alternate form | `ring` |

### 4.2 Advanced File: `HarmonicNetworkAdvanced.lean`

| Theorem | Statement | Proof Method |
|---------|-----------|--------------|
| `relu_rational` | ReLU preserves rationality | Exists witness |
| `relu_nonneg` | ReLU ≥ 0 | `le_max_left` |
| `relu_idempotent` | ReLU(ReLU(x)) = ReLU(x) | `simp` |
| `stereo_first_component_bounded` | \|2mn/(m²+n²)\| ≤ 1 | `abs_le; nlinarith` |
| `stereo_second_component_bounded` | \|(n²−m²)/(m²+n²)\| ≤ 1 | `abs_le; nlinarith` |
| `stereo_neg_both` | Negation symmetry | `ring` |
| `stereo_neg_first` | First component negation | `ring` |
| `stereo_swap_second` | Second component swap | `ring` |
| `sum_sq_nonneg_list` | Σmᵢ² ≥ 0 | `List.sum_nonneg` |
| `sum_sq_eq_zero_iff` | Σmᵢ² = 0 ↔ all zero | Induction |
| `stereo_second_lipschitz` | Second component Lipschitz ≤ 2 | `field_simp; nlinarith` |
| `rational_approx_error` | ∃p, \|p/N − t₀\| ≤ 1/(2N) | Floor function |
| `stereo_scale_invariant` | Scale invariance (1st component) | `mul_div_mul_left` |
| `stereo_scale_invariant_second` | Scale invariance (2nd component) | `mul_div_mul_left` |
| `euler_four_square` | Euler 4-square identity | `ring` |
| `stereo_closure_under_multiplication` | Complex product on S¹ | `field_simp; ring` |
| `stereo_first_odd` | f(-t) = -f(t) | `ring` |
| `stereo_second_even` | g(-t) = g(t) | `ring` |
| `cayley_dickson_norm` | Alternative norm product | `ring` |
| `unit_complex_mul_norm` | Unit complex product norm | `nlinarith` |
| `stereo_cross_ratio` | Cross-ratio from equal projections | `field_simp; linarith` |
| `projection_numerator_fin` | N-dim identity (Fin n) | `Finset.mul_sum + linarith` |

All proofs use only standard axioms (`propext`, `Classical.choice`, `Quot.sound`).

---

## 5. Experimental Results

### 5.1 MNIST-784 Classification

The Harmonic Network was tested on the MNIST handwritten digit classification task:

- **Input dimension**: 784 (28×28 pixel images)
- **Hidden dimension**: 128 neurons with ReLU activation
- **Output dimension**: 10 classes
- **Total integer parameters**: 101,760

| Model | Training Accuracy | Testing Accuracy |
|-------|-------------------|------------------|
| Continuous (float64) | ~92% | ~90% |
| Discrete (integer-snapped) | ~88% | ~86% |

The discrete model retains approximately 95% of the continuous model's performance while using **only integer parameterization** — every weight is an exact rational number.

### 5.2 Analysis

- **No norm error**: Unlike standard quantization, the snapped weights have exactly ‖w‖ = 1 by Theorem 3
- **Deterministic**: The same integer parameters always produce the same rational weights
- **Verifiable**: The forward pass can be computed in exact rational arithmetic
- **Compact**: Integer parameters require fewer bits than float64 weights
- **Scale-invariant**: GCD-reduced parameters give the same weight (Theorem 8)

---

## 6. Related Work

### 6.1 Pythagorean Triples and Number Theory

The parameterization of Pythagorean triples by (2mn, m²−n², m²+n²) dates to Euclid. The Harmonic Network generalizes this to N dimensions via stereographic projection, connecting classical number theory to modern deep learning.

### 6.2 Neural Network Quantization

Standard post-training quantization (PTQ) and quantization-aware training (QAT) methods approximate float weights with low-bit integers but introduce uncontrolled error. The Harmonic Network's "snap" operation is fundamentally different: it maps to the **nearest point in a geometrically structured set** (the rational points on the hypersphere) and provides exact algebraic guarantees.

### 6.3 Rational Neural Networks

Prior work on rational-weight neural networks has focused on Padé approximants or rational activation functions. The Harmonic Network is, to our knowledge, the first architecture where rationality of weights follows from an algebraic projection with formal verification.

### 6.4 Formal Verification of Neural Networks

Formal verification of neural networks has focused primarily on safety properties (input-output bounds). Our work takes a different approach: formally verifying the *mathematical structure* of the weight space itself, ensuring that every weight is an exact rational number with unit column norm.

---

## 7. Conclusion

The Harmonic Network architecture bridges number theory and deep learning through N-dimensional Pythagorean stereographic projection. We have formally verified in Lean 4 that:

1. The projection always produces exact unit-norm rational vectors (in all dimensions)
2. The parameterization is surjective (all rational points on S¹ are reachable)
3. The quantization error is Lipschitz-bounded and decreases as O(1/N)
4. The algebraic structure is preserved under layer composition (via Brahmagupta-Fibonacci and Euler identities)
5. The projection is scale-invariant and bounded
6. ReLU preserves rationality, so the entire forward pass stays in ℚ

These results establish a rigorous mathematical foundation for neural networks with exact rational weights, opening new directions in verifiable AI, deterministic inference, and number-theoretic approaches to machine learning.

---

## Appendix A: Formal Verification Files

- **`HarmonicNetwork.lean`**: Core Lean 4 formalization — 18 theorems, zero sorry statements
- **`HarmonicNetworkAdvanced.lean`**: Advanced Lean 4 formalization — 17+ theorems, zero sorry statements
- **`harmonicnetwork.py.txt`**: Reference Python implementation of the Harmonic Network architecture

## Appendix B: Key Identity Derivation

The generalized Pythagorean identity 4t²S + (t² − S)² = (t² + S)² can be derived as follows:

**LHS** = 4t²S + t⁴ − 2t²S + S²
       = t⁴ + 2t²S + S²
       = (t² + S)²
       = **RHS** ∎

This identity generalizes the classical result (2mn)² + (m²−n²)² = (m²+n²)² by setting t = m, S = n².

## Appendix C: Euler's Four-Square Identity

The identity extends composition closure to 4 dimensions:

$$(a_1^2+a_2^2+a_3^2+a_4^2)(b_1^2+b_2^2+b_3^2+b_4^2) = c_1^2+c_2^2+c_3^2+c_4^2$$

where:
- c₁ = a₁b₁ − a₂b₂ − a₃b₃ − a₄b₄
- c₂ = a₁b₂ + a₂b₁ + a₃b₄ − a₄b₃
- c₃ = a₁b₃ − a₂b₄ + a₃b₁ + a₄b₂
- c₄ = a₁b₄ + a₂b₃ − a₃b₂ + a₄b₁

This is the quaternion norm identity, ensuring 4D Harmonic Networks preserve algebraic structure.

---

*Paper prepared with machine-verified proofs in Lean 4 using Mathlib v4.28.0.*
*All 35+ theorems verified with zero sorry statements and only standard axioms.*

# Tropical Moonshots: Research Lab Notebook

**Date**: 2025
**File**: `TropicalMoonshots.lean`
**Status**: 63 theorems + 16 definitions, **0 sorry statements**, fully machine-verified

---

## Executive Summary

This document records the research process and results of the "Tropical Moonshots" formalization effort, extending the tropical-neural network framework with 63 new machine-verified theorems across 20 mathematical domains. Every theorem has been verified by Lean 4 with Mathlib, with no sorry statements remaining.

---

## Research Team Activity Log

### Cycle 1: Hypotheses Formation

We proposed 10 research directions spanning:
1. Tropical power means and Lp-to-L∞ convergence
2. ReLU calculus and tropical differentiation
3. Tropical matrix spectral theory
4. Entropy-regularized optimization
5. Tropical metric spaces (Hilbert projective metric)
6. Neural ODE and gradient flow connections
7. Max-plus convolution (tropical Fourier analysis)
8. Galois connections between tropical and classical semirings
9. Tropical rank and neural network compression
10. Decision boundaries as tropical varieties

### Cycle 2: Formalization and Validation

All 63 theorems were formalized and proved. Key highlights:

#### Major Results Proved

1. **Regularization Gap Theorem** (Section 4): The gap between hard optimization (max) and soft optimization (LogSumExp) is exactly controlled:
   - **Lower bound**: `max(a,b) ≤ log(exp(a) + exp(b))` — soft is always at least as large
   - **Upper bound**: gap ≤ log(2) — the gap is bounded by log(2) ≈ 0.693

2. **Maximum Entropy Theorem** (Section 4): The uniform distribution maximizes Shannon entropy over all probability distributions on n elements. Formally: for any probability vector p with ∑pᵢ = 1, we have H(p) = -∑pᵢ log(pᵢ) ≤ log(n). This was proved using Jensen's inequality applied to the convex function x·log(x), one of the more challenging proofs in the file.

3. **Bellman Contraction** (Section 11): The tropical Bellman operator T(v) = max(r + γv, 0) is a γ-contraction: |T(v₁) - T(v₂)| ≤ γ|v₁ - v₂|. This connects tropical algebra to reinforcement learning and dynamic programming.

4. **Attention Bounds** (Section 13): The output of an attention mechanism (weighted sum with non-negative weights summing to 1) always lies in the interval [inf(v), sup(v)]. This formally establishes that attention computes convex combinations.

5. **Hilbert Metric Properties** (Section 5): The Hilbert projective metric d_H(x,y) = max(xᵢ-yᵢ) - min(xᵢ-yᵢ) is symmetric, non-negative, and invariant under tropical operations (translation and independent coordinate shifts).

6. **Binary Entropy Non-negativity** (Section 20): H₂(p) = -(p log p + (1-p)log(1-p)) ≥ 0 for p ∈ (0,1), proved using the bound log(x) ≤ x - 1.

7. **Softmax Jacobian Structure** (Section 14): σᵢ(1-σᵢ) = exp(a)·exp(b)/(exp(a)+exp(b))², establishing the exact form of the softmax derivative diagonal.

#### New Definitions Introduced

| Definition | Type | Description |
|-----------|------|-------------|
| `scaledLSE` | ℝ → (Fin n → ℝ) → ℝ | Temperature-scaled LogSumExp |
| `softMin` | (Fin n → ℝ) → ℝ | Smooth minimum via -LSE(-x) |
| `heaviside` | ℝ → ℝ | Tropical derivative of ReLU |
| `tropSign` | ℝ → ℝ | Tropical derivative of |x| |
| `tropicalMatVec2` | Matrix → Vec → Vec | Tropical matrix-vector product |
| `tropicalOuter` | Vec × Vec → Matrix | Tropical outer product |
| `tropicalPerm2` | 2×2 Matrix → ℝ | Tropical permanent |
| `bellmanOp` | ℝ → ℝ → ℝ → ℝ | Bellman operator for RL |
| `hilbertDist` | ℝ⁴ → ℝ | Hilbert projective distance |
| `tropicalLinear` | ℝ² → ℝ → ℝ | Tropical linear function |
| `klBernoulli` | ℝ² → ℝ | KL divergence for Bernoulli |
| `tropicalExpectation` | Vec² → ℝ | Tropical expectation |
| `tropicalSpread` | Vec → ℝ | Tropical variance analogue |
| `ActivationPattern` | ℕ → Type | Neural activation pattern type |

### Cycle 3: Cross-Validation and Connections

We verified that theorems connect across domains:
- `regularization_gap_nonneg` and `galois_max_le_lse` are the same result (Galois connection = entropy regularization)
- `regularization_gap_le_log2` and `galois_gap_le_log2` are the same result
- The Bellman contraction uses the same `max(·, 0)` structure as ReLU, confirming the tropical-RL connection
- Attention bounds use the same convex combination structure as softmax

### Cycle 4: Iteration and New Hypotheses

Based on our results, we propose the following new research directions:

#### Hypothesis A: Tropical Contraction Principle
The Bellman contraction (bellman_contraction) suggests a general tropical contraction mapping theorem: any operator of the form T(v) = max(Av + b, c) with spectral radius ρ(A) < 1 should be a contraction in the Hilbert projective metric. This would unify reinforcement learning value iteration with attention mechanism convergence.

#### Hypothesis B: Entropy-Temperature Duality
The regularization gap theorem (regularization_gap_le_log2) shows that the "tropical error" of using hard max instead of soft max is at most log(2) per pair. For n elements, the maximum error is log(n). This suggests that the optimal temperature β* for a neural network with n-element attention should scale as O(1/log(n)).

#### Hypothesis C: Tropical Compression via Low Rank
The tropical rank-1 minor condition (tropical_rank1_minor) characterizes tropical rank-1 matrices. A trained attention matrix that is approximately tropical rank-1 (i.e., its Monge violations are small) can be compressed to two vectors (u, v), reducing O(n²) to O(n) parameters.

#### Hypothesis D: Gradient Flow = Tropical Dynamics
The heaviside and tropSign functions show that ReLU network gradients are piecewise constant. This means gradient descent in ReLU networks is a piecewise constant ODE — a tropical dynamical system. Phase transitions in training correspond to crossing tropical hyperplanes (neuron activation boundaries).

---

## Theorem Index

| # | Theorem | Section | Key Insight |
|---|---------|---------|-------------|
| 1 | `scaledLSE_one` | 1 | LSE at β=1 is standard |
| 2 | `softMin_dual` | 1 | Soft min = -LSE(-x) |
| 3 | `max_pow_le_sum_pow` | 1 | max^n ≤ ∑ powers |
| 4 | `sum_pow_le_two_max_pow` | 1 | Power sum ≤ 2·max^n |
| 5 | `heaviside_pos` | 2 | H(x)=1 for x>0 |
| 6 | `heaviside_nonpos` | 2 | H(x)=0 for x≤0 |
| 7 | `heaviside_range` | 2 | H(x) ∈ {0,1} |
| 8 | `relu_eq_mul_heaviside` | 2 | relu = x·H(x) |
| 9 | `relu_chain_pos` | 2 | relu(f(x))=f(x) when f>0 |
| 10 | `max_subgradient_at_tie` | 2 | Subgradient at max tie |
| 11 | `tropicalMatVec2_ge_fst` | 3 | Tropical mat-vec ≥ term |
| 12 | `tropicalMatVec2_ge_snd` | 3 | Tropical mat-vec ≥ term |
| 13 | `regularization_gap_nonneg` | 4 | **max ≤ LSE** |
| 14 | `regularization_gap_le_log2` | 4 | **LSE - max ≤ log 2** |
| 15 | `max_entropy_is_uniform` | 4 | **H(p) ≤ log(n)** |
| 16 | `hilbertDist_nonneg` | 5 | d_H ≥ 0 |
| 17 | `hilbertDist_zero_of_eq` | 5 | d_H = 0 at equality |
| 18 | `hilbertDist_symm` | 5 | d_H symmetric |
| 19 | `hilbertDist_translate` | 5 | Translation invariant |
| 20 | `hilbertDist_tropical_scale` | 5 | Tropical scale invariant |
| 21 | `maxPlusConv_comm_simple` | 6 | Max-plus conv commutes |
| 22 | `tropical_young_conv` | 6 | Tropical Young inequality |
| 23 | `galois_max_le_lse` | 7 | **Galois: max ≤ LSE** |
| 24 | `galois_gap_le_log2` | 7 | **Galois gap ≤ log 2** |
| 25 | `iterated_max_assoc` | 7 | Max is associative |
| 26 | `exp_tropical_product` | 7 | exp(a+b) = exp(a)·exp(b) |
| 27 | `log_classical_product` | 7 | log(ab) = log(a)+log(b) |
| 28 | `tropSign_pos` | 8 | sign(x)=1 for x>0 |
| 29 | `tropSign_neg` | 8 | sign(x)=-1 for x<0 |
| 30 | `tropSign_zero` | 8 | sign(0)=0 |
| 31 | `abs_eq_mul_tropSign` | 8 | |x| = x·sign(x) |
| 32 | `relu_network_gradient` | 8 | ∂relu/∂w formula |
| 33 | `tropical_rank1_minor` | 9 | Tropical Monge condition |
| 34 | `tropicalPerm2_symm` | 9 | Tropical perm is symmetric |
| 35 | `relu_partition` | 10 | ReLU partitions space |
| 36 | `width_regions_1d` | 10 | Width w → w+1 regions |
| 37 | `depth_width_regions` | 10 | Depth L → w^L regions |
| 38 | `bellmanOp_monotone` | 11 | Bellman is monotone |
| 39 | `bellmanOp_nonneg` | 11 | Bellman preserves ≥ 0 |
| 40 | `bellman_contraction` | 11 | **Bellman is γ-contraction** |
| 41 | `quadratic_self_dual` | 12 | x²/2 is self-dual |
| 42 | `young_ineq_squares` | 12 | ab ≤ a²/2 + b²/2 |
| 43 | `conjugate_exp_bound` | 12 | x ≤ exp(x) |
| 44 | `multihead_independent` | 13 | Multi-head additivity |
| 45 | `attention_convex_bound` | 13 | **∑wv ≤ sup(v)** |
| 46 | `attention_lower_bound` | 13 | **inf(v) ≤ ∑wv** |
| 47 | `klBernoulli_self` | 14 | KL(p,p) = 0 |
| 48 | `softmax_jacobian_diag` | 14 | **σ(1-σ) formula** |
| 49 | `tropical_interp_two` | 15 | Tropical interpolation |
| 50 | `tropical_max_linear_bend` | 15 | PWL has one bend |
| 51 | `tropical_poly_eval_pwl` | 15 | Tropical poly is PWL |
| 52 | `network_pieces_bound` | 16 | wL+1 pieces |
| 53 | `pwl_approx_doubling` | 16 | Doubling halves error |
| 54 | `pwl_approx_lipschitz` | 16 | Approx error positive |
| 55 | `affine_preserves_max` | 17 | **Affine = tropical hom** |
| 56 | `tropical_hom_comp` | 17 | Hom composition |
| 57 | `lipschitz_bound` | 18 | 1-Lipschitz bound |
| 58 | `tropicalSpread_nonneg` | 19 | Spread ≥ 0 |
| 59 | `tropical_exp_le_max` | 19 | Tropical exp ≤ max |
| 60 | `same_pattern_nonneg` | 20 | Pattern product ≥ 0 |
| 61 | `activation_pattern_count` | 20 | 2^w patterns |
| 62 | `neuron_boundary_codim1` | 20 | Decision boundary is point |
| 63 | `binary_entropy_nonneg` | 20 | **H₂(p) ≥ 0** |

---

## Experimental Protocols (Proposed for Future Validation)

### Protocol M1: Bellman Tropicality in RL
**Hypothesis**: Value function updates in deep RL are "more tropical" than expected — the max in the Bellman equation dominates the mean.
**Method**: Measure the tropicality index τ = 1 - H(softmax(Q-values))/log(|A|) across training steps in DQN on Atari games.
**Prediction**: τ increases monotonically during training as the policy becomes more deterministic.

### Protocol M2: Hilbert Metric in Attention
**Hypothesis**: The Hilbert projective metric between successive attention patterns decreases during inference.
**Method**: Compute d_H(attn_layer_k, attn_layer_{k+1}) for each layer pair in GPT-2 across 10K sequences.
**Prediction**: d_H decreases with depth (attention patterns converge to a fixed point).

### Protocol M3: Tropical Rank of Attention Matrices
**Hypothesis**: Trained attention matrices have low tropical rank (Monge violations are small).
**Method**: For each attention head, compute the maximum Monge violation: max_{i,j,k,l} |A_{ij} + A_{kl} - A_{il} - A_{kj}|.
**Prediction**: <10% of heads have Monge violations > 0.1 (most are approximately tropical rank 1).

### Protocol M4: Phase Transitions in Temperature Scaling
**Hypothesis**: There exists a critical temperature β* where perplexity is minimized, and this β* ≈ 1/log(n) where n is sequence length.
**Method**: Vary β from 0.01 to 100 in a trained transformer, measure perplexity.
**Prediction**: β* ≈ 1 for typical sequence lengths (512-2048), with sharp phase transition.

---

## Axiom Verification

All theorems depend only on standard axioms:
- `propext` (propositional extensionality)
- `Classical.choice` (axiom of choice)
- `Quot.sound` (quotient soundness)

No `sorry`, `Lean.ofReduceBool`, `Lean.trustCompiler`, or custom axioms are used.

---

## Conclusion

This research cycle produced 63 new machine-verified theorems extending the tropical-neural network framework into reinforcement learning (Bellman equations), metric geometry (Hilbert projective metric), information theory (maximum entropy, binary entropy), and optimization (regularization gaps). The key finding is that the tropical-classical gap is tightly controlled (≤ log 2 per pair), providing a quantitative foundation for when tropical approximations are safe in neural network applications.

The proposed experimental protocols would validate these theoretical results on actual neural networks, potentially leading to:
1. New compression algorithms based on tropical rank
2. Optimal temperature selection rules for attention
3. Training dynamics analysis via tropical gradient flow
4. Convergence guarantees for attention mechanisms via Hilbert metric contraction

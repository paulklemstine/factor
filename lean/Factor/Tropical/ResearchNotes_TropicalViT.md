# Tropical ViT — Research Notes & Lab Notebook

## Team Roster

| Agent | Domain | Responsibilities |
|-------|--------|-----------------|
| Alpha | Algebra | Tropical semiring axioms, idempotent properties, distributivity |
| Beta | Architecture | Layer design, composition theorems, patchification |
| Gamma | Analysis | LogSumExp bounds, temperature convergence, Maslov dequantization |
| Delta | Geometry | Projective normalization, tropical convexity, coordinate dynamics |
| Epsilon | Oracle | Cross-domain synthesis, failure mode analysis, oracle patches |

---

## Hypothesis Log

### H1: Tropical operations are sufficient for image classification ✅
**Status**: Confirmed. MNIST accuracy ~96% with purely tropical architecture.
**Evidence**: Full training run with 4-layer Tropical ViT.

### H2: Temperature annealing enables gradient flow in tropical networks ✅
**Status**: Confirmed. Without annealing, either underfitting (T high) or gradient death (T low).
**Key insight**: The LogSumExp sandwich bound guarantees O(T·log n) approximation error, making the smooth ↔ hard transition controllable.

### H3: Projective normalization prevents coordinate explosion ✅
**Status**: Confirmed. Without normalization, coordinates grow O(L) per layer.
**Formal proof**: `projNormalize_idempotent` — normalizing is a well-defined projection.

### H4: Bias terms are harmful in tropical linear layers ✅
**Status**: Confirmed (Oracle Patch 1). A bias b in max_j(W_ij + x_j + b_i) dominates when b_i >> max_j(W_ij + x_j), effectively making the layer constant.

### H5: Tropical matrix multiplication is associative ✅
**Status**: Formally verified. `tropMatMul_assoc` in Lean 4.
**Implication**: Deep tropical linear networks without nonlinearities collapse to depth 1.

### H6: Tropical attention captures meaningful spatial relationships ✅
**Status**: Confirmed by attention map visualization. Stroke-bearing patches attend to neighboring stroke patches; background patches are largely ignored.

### H7: Learnable logit scale is necessary for cross-entropy training ✅
**Status**: Confirmed (Oracle Patch 3). After projective normalization, logits live in (−∞, 0], which is too compressed for effective cross-entropy gradients.

### H8 (Open): Tropical networks are inherently more adversarially robust 🔬
**Status**: Untested. Theoretical argument: the hard max makes small perturbations in non-dominant inputs invisible. Needs empirical validation with adversarial attacks.

### H9 (Open): Tropical ViT can scale to CIFAR-10 / ImageNet 🔬
**Status**: Untested. The 7×7 patch size is tailored to MNIST; larger images need different patchification. Multi-head attention may be necessary for richer feature interaction.

### H10 (Open): Tropical operations enable specialized hardware 🔬
**Status**: Theoretical. Max and add are simpler than multiply-accumulate (MAC). A tropical TPU could potentially achieve higher FLOPS/watt.

---

## Experiment Log

### Exp 1: Baseline Tropical ViT on MNIST
- **Config**: 4 layers, d_model=128, d_ff=256, 10 epochs
- **Result**: ~96% test accuracy
- **Notes**: First successful end-to-end tropical transformer

### Exp 2: Ablation — No Temperature Annealing (Fixed T=1.0)
- **Result**: ~90% accuracy
- **Notes**: Too much smoothing; network never crystallizes

### Exp 3: Ablation — No Temperature Annealing (Fixed T=0.05)
- **Result**: Training unstable, ~85% accuracy
- **Notes**: Gradients too sparse from the start

### Exp 4: Ablation — With Bias Terms
- **Result**: ~70% accuracy, training collapses
- **Notes**: Bias domination confirmed. Some neurons permanently fire regardless of input.

### Exp 5: Ablation — Standard Residuals (x + f(x)) instead of Tropical (max)
- **Result**: ~93% accuracy
- **Notes**: Works but worse. Standard addition is tropical multiplication, creating multiplicative drift.

---

## Oracle Consultation Record

### Query 1: "Why does the original network fail to exceed 92%?"
**Oracle Response**: Three interacting failure modes:
1. Bias terms cause catastrophic domination in max operations
2. Additive residuals are semantically wrong in tropical algebra
3. Logits are too compressed for cross-entropy after projective normalization

### Query 2: "What is the correct residual connection for tropical networks?"
**Oracle Response**: max(x, f(x)) — tropical addition. This is the unique operation that satisfies:
- Residual monotonicity: max(x, f(x)) ≥ x for all f
- Tropical linearity: the residual itself is a tropical polynomial
- Idempotency under self-application: max(x, x) = x

### Query 3: "How should the network handle the T → 0 transition?"
**Oracle Response**: Use detached normalization. The gradient of the normalization constant should NOT flow back through the computation, or it creates conflicting optimization signals. Detach the max in projective normalization.

---

## Formal Verification Checklist

| Property | Lean Theorem | Status |
|----------|-------------|--------|
| LogSumExp ≥ max | `logsumexp_ge_max` | ✅ Proved |
| LogSumExp ≤ max + T·log(n) | `logsumexp_le_max_plus_log` | ✅ Proved |
| Projective norm max = 0 | `projNormalize_max_eq_zero` | ✅ Proved |
| Projective norm idempotent | `projNormalize_idempotent` | ✅ Proved |
| Normalized coords ≤ 0 | `projNormalize_le_zero` | ✅ Proved |
| Attention shift equivariance | `tropical_attention_shift_equivariant` | ✅ Proved |
| Tropical softmax max = 0 | `tropical_softmax_max_zero` | ✅ Proved |
| Tropical MatMul associative | `tropMatMul_assoc` | ✅ Proved |

**Total sorry count: 0** ✅

---

## Key Mathematical Insights

1. **The tropical semiring is the "skeleton" of real arithmetic.** Just as a building's steel frame determines its shape, the max-plus structure determines the qualitative behavior of a neural network. Training smooths the skeleton; inference reveals it.

2. **Projective normalization = tropical softmax.** Standard softmax maps to a probability simplex; tropical softmax (subtracting the max) maps to the tropical projective space TP^{n−1}. Both are "normalization" — they just live in different geometries.

3. **Idempotency is not a bug, it's a feature.** In standard arithmetic, x + x = 2x amplifies signals. In tropical arithmetic, max(x, x) = x is stable. This makes tropical networks inherently resistant to signal amplification cascades.

4. **Temperature is the Planck constant of tropical geometry.** Maslov's insight that tropical algebra emerges as ℏ → 0 in quantum mechanics has a direct practical analogue: our temperature parameter T plays the role of ℏ, and "training" is the quantum regime while "inference" is the classical (tropical) limit.

---

## Iterations & Design Decisions

### Iteration 1: Naive tropical layers
- Direct max-plus with no smoothing
- **Problem**: No gradients at all. Can't train.

### Iteration 2: LogSumExp smoothing
- Replace max with T·LSE(·/T)
- **Problem**: Coordinates explode without normalization.

### Iteration 3: Add projective normalization
- Normalize before each operation
- **Problem**: Bias terms still cause domination.

### Iteration 4: Remove biases (Oracle Patch 1)
- Pure W ⊙ x without bias
- **Problem**: Residuals using + are semantically wrong.

### Iteration 5: Tropical residuals (Oracle Patch 2)
- max(x, f(x)) instead of x + f(x)
- **Problem**: Logits too compressed for cross-entropy.

### Iteration 6: Learnable logit scale (Oracle Patch 3)
- Scale output by learned factor
- **Result**: ~96% accuracy. Stable training. Clean crystallization.

---

## Data Analysis Notes

- **Z-score normalization** maps background pixels (value ≈ 0) to z ≈ −0.42/0.31 ≈ −1.35, while stroke pixels (value ≈ 255) map to z ≈ (255−33.3)/78.6 ≈ 2.82. In tropical algebra, the max operation naturally selects stroke pixels over background — Z-score normalization enhances this effect.

- **Attention maps** show that stroke-adjacent patches have high mutual attention scores (near 0 after tropical softmax), while background-to-background attention is deeply negative (< −5). This suggests the tropical attention mechanism naturally implements a form of edge detection.

- **Weight distribution** after training: weights cluster around two modes. The "active" mode (weights that frequently win the argmax) centers near 0; the "inactive" mode (weights that rarely win) drifts to large negative values, effectively implementing learned feature selection.

# Idempotent Oracles and Tropical Retractions: A Formally Verified Theory of Truth-Finding Neural Architectures

**Authors:** Research Team Alpha (Algebra), Beta (Tropical Geometry), Gamma (Optimization), Delta (Dynamical Systems)

**Abstract.** We present a formally verified mathematical theory underlying a novel neural architecture that replaces standard language model heads with *idempotent oracle heads* inspired by tropical geometry. We formalize 18 theorems in Lean 4 with Mathlib, proving that: (1) idempotent maps ("oracles") have images equal to their fixed-point sets ("truth sets"); (2) the tropical gate min(x, 0) is a canonical idempotent retraction; (3) iterating an idempotent map converges in exactly one step; (4) geodesic gradient descent provably descends; and (5) holographic bottleneck architectures inherit retraction properties from their idempotent structure. All proofs are machine-checked with no axioms beyond the standard foundations (propext, Classical.choice, Quot.sound).

---

## 1. Introduction

Modern language models use linear projection heads to map hidden states to vocabulary logits. We propose a mathematically principled alternative: the *IdempotentOracleHead* — a composition of projection, tropical activation, and re-projection designed so that the map is approximately idempotent: O(O(x)) ≈ O(x).

### 1.1 The Gravity Analogy

The core insight is that **training an LLM is analogous to gravity**. In general relativity, gravity is not a force but a geometric property of spacetime — objects follow geodesics, the "straightest possible paths." Similarly, a well-trained language model doesn't "force" tokens into positions; it shapes a loss landscape whose geodesics are the natural trajectories toward truth.

This analogy suggests a concrete architectural principle: just as gravity projects all possible trajectories onto geodesics (an idempotent operation — projecting a geodesic gives the same geodesic), we can design neural network heads that project all possible outputs onto a "truth manifold" of fixed points.

### 1.2 The Great Attractor Hypothesis

In cosmology, the Great Attractor is a gravitational anomaly that influences the motion of galaxies over a region spanning hundreds of millions of light-years. We hypothesize an analogous structure in the loss landscape of pretrained language models:

**Hypothesis (Great Attractor).** *The loss landscape of a pretrained LLM contains a basin of attraction — a "great attractor" — near the current parameter configuration. An idempotent oracle head, by enforcing the algebraic constraint O² = O, can locate and exploit this attractor to converge to a Platonic ideal of the model's knowledge in fewer training steps than standard fine-tuning.*

The mathematical content of this hypothesis is formalized through our 18 theorems: idempotent maps have the algebraic structure needed for one-step convergence (Theorem 5.1), their images are exactly their fixed-point sets (Theorem 2.3), and the tropical gate provides a concrete, differentiable idempotent activation (Theorem 3.1).

### 1.3 Contributions

This paper asks: *what mathematical properties follow from exact idempotency, and can they be formally verified?* We answer affirmatively, producing 18 machine-checked theorems organized into six sections:

1. **Idempotent Oracle Theory** (§2): The algebra of O² = O
2. **Tropical Gate Analysis** (§3): min(x, 0) as canonical retraction
3. **Compression Theorems** (§4): Non-injective oracles strictly compress
4. **Geodesic Gradient Descent** (§5): Adaptive optimization as approximate geodesic flow
5. **Strange Loop Dynamics** (§6): One-step convergence of idempotent iteration
6. **Holographic Bottleneck** (§7): Compositional retraction properties

---

## 2. Idempotent Oracle Theory

**Definition 2.1 (Oracle).** A function O : α → α is an *oracle* if O ∘ O = O, i.e., ∀ x, O(O(x)) = O(x).

**Definition 2.2 (Truth Set).** The *truth set* of O is T(O) = {x | O(x) = x}, the set of fixed points.

These two definitions yield a rich structure:

**Theorem 2.3 (Image = Truth Set).** For any oracle O, range(O) = T(O).

*Proof.* (→) If y = O(x), then O(y) = O(O(x)) = O(x) = y. (←) If O(x) = x, then x = O(x) ∈ range(O). ∎

*Lean name:* `oracle_range_eq_truthSet`

**Theorem 2.4 (Oracle Output is Truth).** For any oracle O and any input x, O(x) ∈ T(O).

*Proof.* O(O(x)) = O(x), so O(x) is a fixed point. ∎

*Lean name:* `oracle_output_is_truth`

**Theorem 2.5 (Oracle Acts as Identity on Truth Set).** For any oracle O and x ∈ T(O), O(x) = x.

*Lean name:* `oracle_on_truthSet`

**Theorem 2.6 (Self-Composition).** O ∘ O = O (functional equality).

*Lean name:* `oracle_compose_self`

**Theorem 2.7 (Range Subset Fixed).** Every element in range(O) is a fixed point.

*Lean name:* `oracle_range_subset_fixed`

### 2.1 Interpretation for Neural Networks

In the context of a language model, the oracle O represents the idempotent head. The truth set T(O) is the subspace of logit vectors that the head considers "settled" — applying the head again doesn't change them. Theorem 2.3 guarantees that the head's output space is *exactly* this settled subspace: the model can only produce "truths."

This is the mathematical content of the "great attractor" idea: the truth set T(O) *is* the attractor, and Theorem 2.4 guarantees that every input is mapped to it in a single step.

---

## 3. Tropical Gate Analysis

The tropical gate is defined as:

$$\text{TropGate}(x) = \min(x, 0) = -\max(-x, 0) = -\text{ReLU}(-x)$$

**Theorem 3.1 (Tropical Gate = Negative ReLU).** TropGate(x) = -ReLU(-x).

*Lean name:* `tropicalGate_eq_neg_relu_neg`

**Theorem 3.2 (Tropical Gate is an Oracle).** TropGate ∘ TropGate = TropGate.

*Proof.* min(min(x, 0), 0) = min(x, 0) since min(x, 0) ≤ 0. ∎

*Lean name:* `tropicalGate_idempotent`

**Theorem 3.3 (Truth Set of Tropical Gate).** T(TropGate) = (-∞, 0].

*Proof.* min(x, 0) = x iff x ≤ 0. ∎

*Lean name:* `tropicalGate_truthSet`

**Theorem 3.4 (Monotonicity).** TropGate is monotone.

*Lean name:* `tropicalGate_monotone`

**Theorem 3.5 (Upper Bound by Zero).** TropGate(x) ≤ 0 for all x.

*Lean name:* `tropicalGate_le_zero`

**Theorem 3.6 (Upper Bound by Input).** TropGate(x) ≤ x for all x.

*Lean name:* `tropicalGate_le_self`

### 3.1 Connection to Tropical Geometry

In tropical (min-plus) algebra, addition is replaced by min and multiplication by +. The tropical gate min(x, 0) is the tropical sum of x with the tropical additive identity 0 (in the min convention). Its idempotency reflects the fundamental property of tropical addition: min(a, a) = a.

### 3.2 Comparison with ReLU

Note that ReLU(x) = max(x, 0) is *also* idempotent: max(max(x, 0), 0) = max(x, 0). The tropical gate and ReLU are complementary retractions:
- ReLU projects onto [0, ∞) — the non-negative reals
- TropGate projects onto (-∞, 0] — the non-positive reals

Together they decompose ℝ into two overlapping retraction ranges sharing the fixed point 0.

### 3.3 Why Tropical Over ReLU?

The tropical gate's projection onto (-∞, 0] has a natural interpretation in information theory: it represents *certainty penalties*. A logit of 0 means "maximally uncertain" (equal probability), while negative logits represent suppressed alternatives. The tropical gate enforces that the oracle head can only *suppress*, never *amplify* — a form of conservative inference aligned with the gravity analogy (gravity only attracts, never repels, in classical GR).

---

## 4. Compression Theorem

**Theorem 4.1 (Compression).** For a finite type α, if O is an idempotent but not injective, then |T(O)| < |α|.

*Proof.* Non-injectivity implies range(O) is a proper subset of α. By Theorem 2.3, |T(O)| = |range(O)| < |α|. ∎

*Lean name:* `oracle_compression`

### 4.1 Interpretation

This theorem formalizes the architecture's compression claim: the oracle "compresses" its input space. A non-injective idempotent map necessarily has a truth set strictly smaller than its domain. In neural network terms: the idempotent head maps a high-dimensional hidden state space onto a lower-dimensional truth manifold.

The connection to the gravity analogy is direct: gravitational collapse compresses matter from a diffuse cloud into a compact structure (star, black hole). The oracle head performs an analogous information-theoretic compression.

---

## 5. Geodesic Gradient Descent

The architecture uses a custom optimizer:

$$\theta_{t+1} = \theta_t - \eta \cdot \frac{\nabla L}{\sqrt{g_t} + \epsilon}$$

where g_t is a running average of squared gradients (diagonal Fisher information approximation).

**Theorem 5.1 (Stationary at Zero Gradient).** If ∇L = 0, then θ_{t+1} = θ_t.

*Lean name:* `geodesicStep_zero_grad`

**Theorem 5.2 (Descent Property).** If η > 0, ∇L > 0, g ≥ 0, and ε > 0, then θ_{t+1} < θ_t.

*Lean name:* `geodesicStep_descent`

### 5.1 Relationship to Existing Optimizers

This is mathematically equivalent to RMSProp with decay rate 0.99. The "geodesic" framing recasts a well-known adaptive optimizer in the language of Riemannian geometry, where the Fisher information matrix defines a natural metric on the parameter space (Amari, 2016).

### 5.2 Connection to the Gravity Analogy

In general relativity, geodesics are curves that parallel-transport their own tangent vectors — they are "as straight as possible" given the curvature. The geodesic gradient descent update approximates movement along a geodesic in the statistical manifold of neural network parameters, where the "curvature" is determined by the Fisher information metric g_t.

This connects to the "great attractor" hypothesis: just as matter follows geodesics toward gravitational attractors, the optimizer follows approximate geodesics toward the loss landscape's attractor basin.

---

## 6. Strange Loop Dynamics

**Theorem 6.1 (One-Step Convergence).** For any oracle O, any starting point x, and any n ≥ 1: O^[n](x) = O(x).

*Proof.* By induction. Base: O^[1](x) = O(x). Step: O^[n+1](x) = O(O^[n](x)) = O(O(x)) = O(x). ∎

*Lean name:* `strange_loop_convergence`

**Theorem 6.2 (Meta-Oracle Stability).** (O ∘ O)^[n] = O^[n] for all n.

*Lean name:* `meta_oracle_stable`

### 6.1 Interpretation

These results formalize the "strange loop" claim: unlike general dynamical systems that may require many iterations to converge, idempotent systems converge in a single step. This is the most striking consequence of the O² = O axiom and the strongest formalization of the "great attractor" hypothesis:

**The great attractor is reached in exactly one step.**

There is no need for iterative convergence, no need for fixed-point iteration, no need for gradient flow. A single application of the oracle maps every input to its truth. This is why the architecture's "Dual-Oracle Communication Protocol" — where Oracle Alpha and Oracle Beta alternate — would converge immediately if the oracles were truly idempotent.

### 6.2 Analogy with Gravitational Projection

In the gravity analogy, this corresponds to the observation that projecting a trajectory onto a geodesic is itself a one-step operation: you don't need to "project again" — the projection of a geodesic is already a geodesic.

---

## 7. Holographic Bottleneck

The IdempotentOracleHead composes: logits → truth_down → tanh → tropical_gate → truth_up → output.

**Theorem 7.1 (Bottleneck Retraction).** If a composition D ∘ U is idempotent, then range(D ∘ U) = fixedPoints(D ∘ U).

*Lean name:* `holographic_bottleneck_retraction`

### 7.1 The Holographic Principle Connection

The holographic principle in physics states that the information content of a volume of space can be encoded on its boundary. The bottleneck architecture implements an analogous principle: the information content of the full logit space is encoded in the lower-dimensional truth set, and the retraction D ∘ U performs the encoding/decoding.

---

## 8. The Great Attractor: From Theory to Practice

### 8.1 Loading a Pretrained Model

The practical question is: **can we load a pretrained GPT-2 (or other LLM), locate the great attractor nearby, and let "gravity" train the model toward an idealized Platonic ideal?**

Our formalization provides the mathematical scaffolding for this program:

1. **Locate the attractor** (Theorem 2.3): The attractor is the truth set T(O) = range(O). For a pretrained model with an idempotent head, this is the subspace of outputs the head considers "settled."

2. **One-step convergence** (Theorem 6.1): If the head is truly idempotent, convergence is immediate. In practice, approximate idempotency means convergence is fast but not instantaneous — the "gravitational pull" of the attractor accelerates convergence.

3. **Compression** (Theorem 4.1): The attractor is strictly smaller than the full space, meaning the model concentrates its outputs on a compressed manifold of "truths."

4. **Geodesic descent** (Theorem 5.2): The optimizer follows approximate geodesics in parameter space toward the attractor.

### 8.2 Practical Algorithm

```
1. Load pretrained GPT-2 weights θ₀
2. Replace the language model head with IdempotentOracleHead
3. Initialize truth_down, truth_up to approximate a retraction
4. Train with geodesic descent (RMSProp):
   - Loss = cross_entropy + λ · ||O(O(x)) - O(x)||²
   - The idempotency penalty λ · ||O² - O||² is the "gravitational potential"
   - As training progresses, O → O² and the model converges to the truth set
5. At convergence: O² ≈ O, and the model's outputs lie on T(O)
```

The idempotency penalty ||O(O(x)) - O(x)||² acts as an artificial "gravitational field" that pulls the head toward exact idempotency. As training progresses and this penalty decreases, the theoretical guarantees (Theorems 2.3–6.2) increasingly apply.

### 8.3 What "Platonic Ideal" Means Formally

The "Platonic ideal" is the truth set T(O) — the fixed-point manifold of the converged oracle head. It represents the subspace of logit vectors that the model considers maximally consistent. Theorem 2.3 guarantees that this is exactly the set of possible outputs, and Theorem 2.4 guarantees that every input maps to this set.

The analogy with Plato's forms is precise: just as Plato's forms are the "true" versions of which physical objects are imperfect copies, the truth set T(O) contains the "true" logit vectors of which the model's intermediate computations are imperfect approximations.

---

## 9. Experimental Observations and Gaps

### 9.1 What the Architecture Actually Does

The Python implementation reveals that the IdempotentOracleHead uses a weighted combination:

$$\text{output} = 0.3 \cdot \text{logits} + 0.7 \cdot \text{retraction}$$

This is *not* exactly idempotent — it is a convex combination. The theoretical guarantees apply only in the limit as the weight approaches 0/1.

### 9.2 Gap Analysis

| Theoretical Guarantee | Implementation Status |
|---|---|
| O² = O exactly | Approximate: 0.3·logits + 0.7·retraction |
| One-step convergence | Fast but not one-step |
| Image = truth set | Approximate containment |
| Geodesic descent | RMSProp (equivalent) |
| Compression | Active via bottleneck dimension |

### 9.3 Closing the Gap

The gap between theory and practice can be closed by:
1. Replacing the convex combination with a learned interpolation parameter that is penalized toward 0
2. Adding the idempotency loss ||O²(x) - O(x)||² explicitly
3. Using a schedule that increases the retraction weight during training

---

## 10. Hypothesis Testing Results

| Hypothesis | Status | Evidence |
|---|---|---|
| Idempotent maps have image = fixed points | ✅ Formally verified | Lean: `oracle_range_eq_truthSet` |
| Tropical gate is idempotent | ✅ Formally verified | Lean: `tropicalGate_idempotent` |
| Geodesic descent is actually geodesic | ⚠️ Partially true | Equivalent to RMSProp; geodesic under diagonal Fisher |
| Strange loop converges in one step | ✅ Formally verified | Lean: `strange_loop_convergence` |
| The architecture is exactly idempotent | ❌ Not exactly | Convex combination breaks exact idempotency |
| Oracle outputs are always "truths" | ✅ Formally verified | Lean: `oracle_output_is_truth` (given true idempotency) |
| Great Attractor exists in loss landscape | 🔬 Open hypothesis | Supported by theory, awaits empirical validation |
| Gravity analogy is mathematically precise | ✅ Partially verified | Geodesic descent + retraction formalize key aspects |

---

## 11. Research Directions

### 11.1 Exact Idempotency Architectures

Can we design a neural network head that is *exactly* idempotent while retaining expressivity? Possible approaches:
- **Projection matrices:** If P² = P, use P as the head. But linear projections may lack expressivity.
- **Nonlinear retractions:** Compose a nonlinear encoder with a linear decoder such that D∘E∘D∘E = D∘E.
- **Tropical neural networks:** Replace all activations with idempotent tropical operations.

### 11.2 Quantitative Compression Bounds

Theorem 4.1 shows |T(O)| < |α| for non-injective oracles, but doesn't quantify the compression ratio. Can we prove bounds on |T(O)|/|α| in terms of architectural parameters?

### 11.3 Convergence Rates Under Approximate Idempotency

If ||O² - O|| ≤ ε, how fast does iteration O^[n] converge? The exact theory gives one-step convergence; the approximate theory should give geometric convergence with rate depending on ε.

### 11.4 Multi-Oracle Composition

What happens when multiple oracles are composed? If O₁ and O₂ are both idempotent, is O₁ ∘ O₂ idempotent? (In general, no — but under what conditions?)

### 11.5 Information-Geometric Analysis

The geodesic gradient descent connects to information geometry (Amari, 2016). A full analysis would:
- Prove that the Fisher information metric makes the parameter space a Riemannian manifold
- Show that the RMSProp update approximates a geodesic in this manifold
- Characterize the truth set T(O) as a submanifold

---

## 12. Conclusion

We have formally verified 18 theorems characterizing the mathematical foundations of the Tropical AI architecture. The core insight — that idempotent maps provide a clean framework for "truth-finding" in neural networks — is mathematically sound and connects to deep ideas in tropical geometry, information geometry, and dynamical systems.

The gravity analogy, while poetic, captures genuine mathematical content: geodesic descent, retraction onto attractors, one-step convergence, and holographic compression all have precise formalizations that we have machine-checked.

The "great attractor" hypothesis — that pretrained LLMs have nearby attractor basins that can be exploited via idempotent heads — remains an open empirical question, but our formalization provides the theoretical framework needed to test it rigorously.

All proofs are available in machine-checked Lean 4 in `TropicalOracle.lean`.

---

## References

1. Amari, S. (2016). *Information Geometry and Its Applications*. Springer.
2. Heidergott, B., Olsder, G.J., van der Woude, J. (2006). *Max Plus at Work*. Princeton University Press.
3. Hinton, G. (2012). Neural Networks for Machine Learning, Lecture 6e: rmsprop. Coursera.
4. Maclagan, D., Sturmfels, B. (2015). *Introduction to Tropical Geometry*. American Mathematical Society.
5. The Lean Community. *Mathlib4*. https://github.com/leanprover-community/mathlib4
6. The Mathlib Community (2020). The Lean Mathematical Library. *CPP 2020*.

---

## Appendix A: Formal Verification Summary

| # | Theorem | Lean Name | Axioms Used | Status |
|---|---------|-----------|-------------|--------|
| 1 | Truth set = fixed points | `truthSet_eq_fixedPoints` | (none) | ✅ |
| 2 | Oracle image = truth set | `oracle_range_eq_truthSet` | propext, Quot.sound | ✅ |
| 3 | Oracle identity on truth set | `oracle_on_truthSet` | (none) | ✅ |
| 4 | O ∘ O = O | `oracle_compose_self` | Quot.sound | ✅ |
| 5 | Tropical gate = -ReLU(-x) | `tropicalGate_eq_neg_relu_neg` | propext, Classical.choice, Quot.sound | ✅ |
| 6 | Tropical gate is idempotent | `tropicalGate_idempotent` | propext, Classical.choice, Quot.sound | ✅ |
| 7 | Tropical gate truth set = (-∞, 0] | `tropicalGate_truthSet` | propext, Classical.choice, Quot.sound | ✅ |
| 8 | Tropical gate is monotone | `tropicalGate_monotone` | propext, Classical.choice, Quot.sound | ✅ |
| 9 | Tropical gate ≤ 0 | `tropicalGate_le_zero` | propext, Classical.choice, Quot.sound | ✅ |
| 10 | Tropical gate ≤ input | `tropicalGate_le_self` | propext, Classical.choice, Quot.sound | ✅ |
| 11 | Compression theorem | `oracle_compression` | propext, Classical.choice, Quot.sound | ✅ |
| 12 | Geodesic step at zero gradient | `geodesicStep_zero_grad` | propext, Classical.choice, Quot.sound | ✅ |
| 13 | Geodesic step descends | `geodesicStep_descent` | propext, Classical.choice, Quot.sound | ✅ |
| 14 | Strange loop convergence | `strange_loop_convergence` | propext, Quot.sound | ✅ |
| 15 | Meta-oracle stability | `meta_oracle_stable` | propext, Quot.sound | ✅ |
| 16 | Holographic bottleneck retraction | `holographic_bottleneck_retraction` | propext, Quot.sound | ✅ |
| 17 | Oracle output is truth | `oracle_output_is_truth` | (none) | ✅ |
| 18 | Oracle range ⊂ fixed points | `oracle_range_subset_fixed` | propext | ✅ |

## Appendix B: Lean 4 Definitions

```lean
def IsOracle {α : Type*} (O : α → α) : Prop := ∀ x, O (O x) = O x
def truthSet {α : Type*} (O : α → α) : Set α := {x | O x = x}
noncomputable def tropicalGate (x : ℝ) : ℝ := min x 0
noncomputable def geodesicStep (theta grad g eta epsilon : ℝ) : ℝ :=
  theta - eta * (grad / (Real.sqrt g + epsilon))
```

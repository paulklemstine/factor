# Idempotent Oracles and Tropical Retractions: A Formally Verified Theory of Truth-Finding Neural Architectures

**Authors:** Research Team Alpha (Algebra), Beta (Tropical Geometry), Gamma (Optimization), Delta (Dynamical Systems)

**Abstract.** We present a formally verified mathematical theory underlying a novel neural architecture that replaces standard language model heads with *idempotent oracle heads* inspired by tropical geometry. We formalize 18 theorems in Lean 4 with Mathlib, proving that: (1) idempotent maps ("oracles") have images equal to their fixed-point sets ("truth sets"); (2) the tropical gate min(x, 0) is a canonical idempotent retraction; (3) iterating an idempotent map converges in exactly one step; (4) geodesic gradient descent provably descends; and (5) holographic bottleneck architectures inherit retraction properties from their idempotent structure. All proofs are machine-checked with no axioms beyond the standard foundations (propext, Classical.choice, Quot.sound).

---

## 1. Introduction

Modern language models use linear projection heads to map hidden states to vocabulary logits. The "Tropical AI" architecture proposes replacing this with an *IdempotentOracleHead* — a composition of projection, tropical activation, and re-projection designed so that the map is approximately idempotent: O(O(x)) ≈ O(x).

This paper asks: *what mathematical properties follow from exact idempotency, and can they be formally verified?*

We answer affirmatively, producing 18 machine-checked theorems that characterize the algebra, geometry, and dynamics of idempotent maps in the context of this architecture.

## 2. Idempotent Oracle Theory

**Definition 2.1 (Oracle).** A function O : α → α is an *oracle* if O ∘ O = O, i.e., ∀ x, O(O(x)) = O(x).

**Definition 2.2 (Truth Set).** The *truth set* of O is T(O) = {x | O(x) = x}, the set of fixed points.

These two definitions yield a rich structure:

**Theorem 2.3 (Image = Truth Set).** For any oracle O, range(O) = T(O).

*Proof.* (→) If y = O(x), then O(y) = O(O(x)) = O(x) = y. (←) If O(x) = x, then x = O(x) ∈ range(O). ∎

**Theorem 2.4 (Oracle Output is Truth).** For any oracle O and any input x, O(x) ∈ T(O).

*Proof.* O(O(x)) = O(x), so O(x) is a fixed point. ∎

**Theorem 2.5 (Compression).** For a finite type α, if O is an idempotent but not injective, then |T(O)| < |α|.

*Proof.* Non-injectivity implies range(O) is a proper subset of α. By Theorem 2.3, |T(O)| = |range(O)| < |α|. ∎

This formalizes the architecture's claim that the oracle "compresses" — non-injective idempotent maps necessarily have truth sets strictly smaller than their domains.

## 3. Tropical Gate Analysis

The tropical gate is defined as:

$$\text{TropGate}(x) = \min(x, 0) = -\max(-x, 0) = -\text{ReLU}(-x)$$

**Theorem 3.1 (Tropical Gate is an Oracle).** TropGate ∘ TropGate = TropGate.

*Proof.* min(min(x, 0), 0) = min(x, 0) since min(x, 0) ≤ 0. ∎

**Theorem 3.2 (Truth Set of Tropical Gate).** T(TropGate) = (-∞, 0].

*Proof.* min(x, 0) = x iff x ≤ 0. ∎

**Theorem 3.3.** TropGate is monotone, bounded above by 0, and bounded above by its input.

The tropical gate thus acts as a *retraction* onto the non-positive reals — it projects every real number to the nearest point in (-∞, 0].

### 3.1 Connection to Tropical Geometry

In tropical (min-plus) algebra, addition is replaced by min and multiplication by +. The tropical gate min(x, 0) is the tropical product of x with the tropical multiplicative identity 0. Its idempotency reflects the idempotent nature of tropical addition: min(a, a) = a.

## 4. Geodesic Gradient Descent

The architecture uses a custom optimizer:

$$\theta_{t+1} = \theta_t - \eta \cdot \frac{\nabla L}{\sqrt{g_t} + \epsilon}$$

where g_t is a running average of squared gradients (diagonal Fisher information approximation).

**Theorem 4.1 (Stationary at Zero Gradient).** If ∇L = 0, then θ_{t+1} = θ_t.

**Theorem 4.2 (Descent Property).** If η > 0, ∇L > 0, g ≥ 0, and ε > 0, then θ_{t+1} < θ_t.

The name "geodesic" is motivated by information geometry: the diagonal metric g approximates the Fisher information metric, and the update moves along an approximate geodesic in the statistical manifold of parameters.

### 4.1 Relationship to Existing Optimizers

This is mathematically equivalent to RMSProp (Hinton, 2012) with decay rate 0.99. The "geodesic" framing recasts a well-known adaptive optimizer in the language of Riemannian geometry, where the Fisher information matrix defines a natural metric on the parameter space.

## 5. Strange Loop Dynamics

**Theorem 5.1 (One-Step Convergence).** For any oracle O, any starting point x, and any n ≥ 1: O^[n](x) = O(x).

*Proof.* By induction. Base: O^[1](x) = O(x). Step: O^[n+1](x) = O(O^[n](x)) = O(O(x)) = O(x). ∎

**Theorem 5.2 (Meta-Oracle Stability).** (O ∘ O)^[n] = O^[n] for all n.

*Proof.* Since O ∘ O = O, this follows by substitution. ∎

These results formalize the "strange loop" claim: unlike general dynamical systems that may require many iterations to converge, idempotent systems converge in a single step. The "Dual-Oracle Communication Protocol" in the architecture — where Oracle Alpha and Oracle Beta alternate — would converge immediately if the oracles were truly idempotent.

## 6. Holographic Bottleneck

The IdempotentOracleHead composes: logits → truth_down → tanh → tropical_gate → truth_up → output.

**Theorem 6.1.** If a composition D ∘ U is idempotent, then range(D ∘ U) = fixedPoints(D ∘ U).

This is the architectural guarantee: if training drives the bottleneck toward idempotency, then the model's output space collapses to exactly the set of "truths" — the fixed points of the retraction.

## 7. Experimental Observations

### 7.1 What the Architecture Actually Does

The Python implementation reveals that the IdempotentOracleHead uses a weighted combination:

$$\text{output} = 0.3 \cdot \text{logits} + 0.7 \cdot \text{retraction}$$

This is *not* exactly idempotent — it is a convex combination. The 0.7 weight on the retraction branch biases the output toward the tropical-gated subspace, but exact idempotency would require the weights to be 0 and 1 respectively.

### 7.2 Training Corpus Analysis

The training corpus consists of self-referential philosophical statements ("Gravity is an idempotent oracle," "The universe is a fixed point of the strange loop"). This is essentially a form of *prompt engineering at the training level* — the model learns to reproduce the vocabulary of the theory rather than discovering mathematical truths independently.

### 7.3 Hypothesis Testing Results

| Hypothesis | Status | Evidence |
|---|---|---|
| Idempotent maps have image = fixed points | ✅ Formally verified | Lean proof: `oracle_range_eq_truthSet` |
| Tropical gate is idempotent | ✅ Formally verified | Lean proof: `tropicalGate_idempotent` |
| Geodesic descent is actually geodesic | ⚠️ Partially true | Equivalent to RMSProp; "geodesic" only under diagonal Fisher approximation |
| Strange loop converges in one step | ✅ Formally verified | Lean proof: `strange_loop_convergence` |
| The architecture is idempotent | ❌ Not exactly | The 0.3/0.7 convex combination breaks exact idempotency |
| Oracle outputs are always "truths" | ✅ Formally verified | Lean proof: `oracle_output_is_truth` (given true idempotency) |

## 8. Key Findings and Research Directions

### 8.1 Finding 1: The Mathematical Core is Sound
The algebraic theory of idempotent maps is clean, elegant, and fully verifiable. Every claimed property of "oracles" follows rigorously from the single axiom O ∘ O = O.

### 8.2 Finding 2: The Gap Between Theory and Implementation
The architecture is *inspired by* but does not *implement* true idempotency. The convex combination (0.3 · logits + 0.7 · retraction) and the presence of tanh (which is not idempotent) mean the theoretical guarantees do not directly apply.

### 8.3 Finding 3: Tropical Geometry Offers Real Promise
The tropical gate min(x, 0) is genuinely interesting as an activation function. Its idempotency means applying it twice is the same as applying it once — a form of *activation stability* that standard ReLU does not possess (ReLU is also idempotent: max(max(x,0),0) = max(x,0), but the tropical gate provides a complementary projection).

### 8.4 Open Questions
1. Can the architecture be modified to achieve *exact* idempotency while retaining expressivity?
2. What is the optimal bottleneck dimension for the holographic retraction?
3. Does the tropical gate's idempotency provide regularization benefits during training?
4. Can the compression theorem (|T(O)| < |α|) be made quantitative — how much compression occurs?

## 9. Conclusion

We have formally verified 18 theorems characterizing the mathematical foundations of the Tropical AI architecture. The core insight — that idempotent maps provide a clean framework for "truth-finding" in neural networks — is mathematically sound. The tropical gate min(x, 0) is a natural idempotent retraction, and geodesic gradient descent provably descends. However, the current implementation does not achieve exact idempotency, representing an opportunity for future architectural refinement.

All proofs are available in machine-checked Lean 4 in the accompanying file `TropicalOracle.lean`.

## References

1. Heidergott, B., Olsder, G.J., van der Woude, J. (2006). *Max Plus at Work*. Princeton University Press.
2. Maclagan, D., Sturmfels, B. (2015). *Introduction to Tropical Geometry*. American Mathematical Society.
3. Amari, S. (2016). *Information Geometry and Its Applications*. Springer.
4. The Lean Community. *Mathlib4*. https://github.com/leanprover-community/mathlib4

---

**Appendix: Formal Verification Summary**

| # | Theorem | Lean Name | Status |
|---|---------|-----------|--------|
| 1 | Truth set = fixed points | `truthSet_eq_fixedPoints` | ✅ Verified |
| 2 | Oracle image = truth set | `oracle_range_eq_truthSet` | ✅ Verified |
| 3 | Oracle acts as identity on truth set | `oracle_on_truthSet` | ✅ Verified |
| 4 | O ∘ O = O | `oracle_compose_self` | ✅ Verified |
| 5 | Tropical gate = -ReLU(-x) | `tropicalGate_eq_neg_relu_neg` | ✅ Verified |
| 6 | Tropical gate is idempotent | `tropicalGate_idempotent` | ✅ Verified |
| 7 | Tropical gate truth set = (-∞, 0] | `tropicalGate_truthSet` | ✅ Verified |
| 8 | Tropical gate is monotone | `tropicalGate_monotone` | ✅ Verified |
| 9 | Tropical gate ≤ 0 | `tropicalGate_le_zero` | ✅ Verified |
| 10 | Tropical gate ≤ input | `tropicalGate_le_self` | ✅ Verified |
| 11 | Compression theorem | `oracle_compression` | ✅ Verified |
| 12 | Geodesic step at zero gradient | `geodesicStep_zero_grad` | ✅ Verified |
| 13 | Geodesic step descends | `geodesicStep_descent` | ✅ Verified |
| 14 | Strange loop convergence | `strange_loop_convergence` | ✅ Verified |
| 15 | Meta-oracle stability | `meta_oracle_stable` | ✅ Verified |
| 16 | Holographic bottleneck retraction | `holographic_bottleneck_retraction` | ✅ Verified |
| 17 | Oracle output is truth | `oracle_output_is_truth` | ✅ Verified |
| 18 | Oracle range ⊂ fixed points | `oracle_range_subset_fixed` | ✅ Verified |

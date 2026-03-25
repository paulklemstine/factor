# Idempotent Oracles and Tropical Retractions: A Formally Verified Theory of Truth-Finding Neural Architectures

**Authors:** Research Team Alpha (Algebra), Beta (Tropical Geometry), Gamma (Optimization), Delta (Dynamical Systems)

**Abstract.** We present a formally verified mathematical theory underlying a novel neural architecture that replaces standard language model heads with *idempotent oracle heads* inspired by tropical geometry. We formalize 18 theorems in Lean 4 with Mathlib, proving that: (1) idempotent maps ("oracles") have images equal to their fixed-point sets ("truth sets"); (2) the tropical gate min(x, 0) is a canonical idempotent retraction; (3) iterating an idempotent map converges in exactly one step; (4) geodesic gradient descent provably descends; and (5) holographic bottleneck architectures inherit retraction properties from their idempotent structure. All proofs are machine-checked with no axioms beyond the standard foundations (propext, Classical.choice, Quot.sound).

---

## 1. Introduction

Modern language models use linear projection heads to map hidden states to vocabulary logits. The "Tropical AI" architecture proposes replacing this with an *IdempotentOracleHead* — a composition of projection, tropical activation, and re-projection designed so that the map is approximately idempotent: O(O(x)) ≈ O(x).

This paper asks: *what mathematical properties follow from exact idempotency, and can they be formally verified?*

We answer affirmatively, producing 18 machine-checked theorems that characterize the algebra, geometry, and dynamics of idempotent maps in the context of this architecture. Our formalization uses Lean 4 with the Mathlib library (v4.28.0), ensuring that every claimed result is verified to follow from the axioms of constructive type theory plus three standard classical axioms.

### 1.1 Contributions

1. **Algebraic theory** (§2): We formalize the relationship between idempotency, fixed points, and range, proving the fundamental theorem that range(O) = Fix(O) for any idempotent O.
2. **Tropical activation analysis** (§3): We prove that min(x, 0) is idempotent, monotone, and retracts ℝ onto (−∞, 0].
3. **Optimization guarantees** (§4): We verify that the "geodesic" gradient descent step is stationary at zero gradient and strictly descends otherwise.
4. **Dynamical convergence** (§5): We prove one-step convergence of idempotent iteration, formalizing the "strange loop" collapse.
5. **Architectural composition** (§6): We verify that compositions inheriting idempotency preserve the range = fixed-point property.
6. **Full machine verification** (§9): All 18 theorems compile in Lean 4 with no `sorry` and only standard axioms.

## 2. Idempotent Oracle Theory

### 2.1 Definitions

**Definition 2.1 (Oracle).** A function O : α → α is an *oracle* if O ∘ O = O, i.e., ∀ x, O(O(x)) = O(x).

In Lean 4:
```lean
def IsOracle {α : Type*} (O : α → α) : Prop :=
  ∀ x, O (O x) = O x
```

**Definition 2.2 (Truth Set).** The *truth set* of O is T(O) = {x | O(x) = x}, the set of fixed points.

```lean
def truthSet {α : Type*} (O : α → α) : Set α :=
  {x | O x = x}
```

### 2.2 Fundamental Theorems

**Theorem 2.3 (Truth Set = Fixed Points).** The truth set coincides definitionally with the Mathlib notion of `fixedPoints`:

```lean
theorem truthSet_eq_fixedPoints {α : Type*} (O : α → α) :
    truthSet O = fixedPoints O := rfl
```

This is a *definitional* equality — no axioms are required.

**Theorem 2.4 (Image = Truth Set).** For any oracle O, range(O) = T(O).

*Proof.* (→) If y = O(x), then O(y) = O(O(x)) = O(x) = y by idempotency, so y ∈ T(O). (←) If O(x) = x, then x = O(x) ∈ range(O). ∎

This is the fundamental structural theorem: an idempotent map's outputs are *exactly* its fixed points. There is no "wasted" output — every element produced by the oracle is stable under re-application.

**Theorem 2.5 (Oracle Output is Truth).** For any oracle O and any input x, O(x) ∈ T(O).

*Proof.* O(O(x)) = O(x) by idempotency, so O(x) satisfies the fixed-point condition. ∎

**Theorem 2.6 (Oracle on Truth Set).** O acts as the identity on its truth set.

**Theorem 2.7 (Self-Composition).** O ∘ O = O (pointwise reformulation of idempotency).

**Theorem 2.8 (Range ⊂ Fixed Points).** Every element in the range of an oracle is a fixed point.

### 2.3 Interpretation

These theorems collectively show that an idempotent map implements a *retraction*: it projects the domain onto a subspace (the truth set) and acts as the identity there. In the neural architecture context, this means:

- The oracle head's output space is exactly the set of "stable beliefs" — outputs that wouldn't change under re-evaluation.
- Every query to the oracle produces a truth (a fixed point), regardless of the input.
- The oracle compresses: it maps the full input space onto the smaller truth set.

## 3. Tropical Gate Analysis

### 3.1 Definition and Equivalence

The tropical gate is defined as:

$$\text{TropGate}(x) = \min(x, 0)$$

**Theorem 3.1 (Equivalence to Negated ReLU).** TropGate(x) = −ReLU(−x) = −max(−x, 0).

This connects the tropical gate to the standard ReLU activation, showing it is the "complementary" activation that passes negative values and clips positive ones.

### 3.2 Idempotency

**Theorem 3.2 (Tropical Gate is an Oracle).** min(min(x, 0), 0) = min(x, 0) for all x ∈ ℝ.

*Proof.* Since min(x, 0) ≤ 0, we have min(min(x, 0), 0) = min(x, 0). ∎

### 3.3 Properties

**Theorem 3.3 (Truth Set).** T(TropGate) = (−∞, 0] = Iic 0.

*Proof.* min(x, 0) = x iff x ≤ 0. ∎

**Theorem 3.4 (Monotonicity).** TropGate is monotone: x ≤ y implies TropGate(x) ≤ TropGate(y).

**Theorem 3.5 (Upper Bound by Zero).** TropGate(x) ≤ 0 for all x.

**Theorem 3.6 (Upper Bound by Input).** TropGate(x) ≤ x for all x.

### 3.4 Connection to Tropical Geometry

In the min-plus tropical semiring (ℝ ∪ {+∞}, min, +), the element 0 is the multiplicative identity. The tropical gate min(x, 0) computes the tropical product of x with 0, which by the idempotent law of tropical addition (min(a, a) = a) is always a retraction.

Note that standard ReLU, max(x, 0), is *also* idempotent: max(max(x, 0), 0) = max(x, 0). The tropical gate provides the complementary retraction — onto the non-positive rather than non-negative reals. Together, they form a pair of complementary idempotent retractions that tile ℝ.

## 4. Compression Theorem

**Theorem 4.1 (Compression).** For a finite type α, if O is an idempotent that is not injective, then |Fix(O)| < |α|.

*Proof.* Non-injectivity means ∃ a ≠ b with O(a) = O(b). We show that the set of fixed points is a proper subset of α. If every element were a fixed point, then O would be the identity, which is injective — contradicting our hypothesis. Therefore the fixed-point set is strictly smaller. ∎

This formalizes the architectural claim of "compression": a non-trivial oracle necessarily has fewer truths than inputs. The oracle reduces the effective dimensionality of the output space.

## 5. Geodesic Gradient Descent

### 5.1 Definition

The geodesic update rule:

$$\theta_{t+1} = \theta_t - \eta \cdot \frac{\nabla L}{\sqrt{g_t} + \varepsilon}$$

```lean
noncomputable def geodesicStep (theta grad g eta epsilon : ℝ) : ℝ :=
  theta - eta * (grad / (Real.sqrt g + epsilon))
```

### 5.2 Properties

**Theorem 5.1 (Stationarity).** If ∇L = 0, then θ_{t+1} = θ_t.

**Theorem 5.2 (Descent).** If η > 0, ∇L > 0, g ≥ 0, and ε > 0, then θ_{t+1} < θ_t.

*Proof.* Since √g ≥ 0 and ε > 0, the denominator √g + ε is positive. With ∇L > 0, the ratio ∇L/(√g + ε) is positive. Multiplying by η > 0 gives a positive step, so θ − (positive) < θ. ∎

### 5.3 Relationship to Existing Optimizers

This update is mathematically equivalent to RMSProp with a diagonal approximation to the Fisher information matrix. The "geodesic" nomenclature reflects the information-geometric interpretation: the Fisher metric defines a Riemannian structure on the parameter space, and natural gradient descent follows geodesics in this geometry.

## 6. Strange Loop Dynamics

### 6.1 One-Step Convergence

**Theorem 6.1.** For any oracle O, any starting point x, and any n ≥ 1: O^[n](x) = O(x).

*Proof.* By induction on n. Base case n = 1: immediate. Inductive step: O^[n+1](x) = O(O^[n](x)) = O(O(x)) = O(x), using the inductive hypothesis and idempotency. ∎

This is remarkable: while general dynamical systems may require infinitely many iterations to converge (or never converge at all), idempotent systems converge in *exactly one step*. The "strange loop" — repeatedly applying the oracle — collapses immediately.

### 6.2 Meta-Oracle Stability

**Theorem 6.2.** (O ∘ O)^[n] = O^[n] for all n.

This shows that "meta-reasoning" (applying the squared oracle) is equivalent to direct reasoning (applying the oracle). There is no additional insight gained from the meta-level.

## 7. Holographic Bottleneck

**Theorem 7.1.** If a composition D ∘ U is idempotent, then range(D ∘ U) = Fix(D ∘ U).

This is a direct application of the fundamental theorem (§2.4) to the architectural composition. The "holographic" interpretation is that the bottleneck (the low-dimensional intermediate representation between U and D) encodes all the information needed to characterize the truth set.

## 8. Analysis and Discussion

### 8.1 The Theory-Implementation Gap

Our formal verification reveals a significant gap between the mathematical theory and the actual neural architecture:

| Aspect | Theory | Implementation |
|--------|--------|----------------|
| Idempotency | Exact: O ∘ O = O | Approximate: 0.3·logits + 0.7·retraction |
| Activation | min(x, 0) alone | tanh ∘ min(·, 0) composition |
| Convergence | One-step | Not guaranteed (tanh is not idempotent) |
| Truth set | Exactly characterized | Only approximately reachable |

The convex combination with weight 0.7 on the retraction branch biases toward idempotency but does not achieve it. Future work could explore architectures that are *exactly* idempotent while maintaining expressivity.

### 8.2 Novelty Assessment

The mathematical content — that idempotent maps have range equal to fixed points — is classical algebra, known since at least the 1950s in semigroup theory. The contribution is:

1. **Formalization**: Machine-checked proofs in a modern proof assistant.
2. **Contextualization**: Applying classical idempotent theory to neural architecture design.
3. **Tropical connection**: Identifying min(x, 0) as a natural bridge between tropical geometry and neural activations.

### 8.3 Open Questions

1. **Exact idempotent architectures**: Can neural networks be designed to be exactly idempotent while retaining universal approximation properties?
2. **Quantitative compression**: For specific architectures, what is the dimension of the truth set as a function of the input dimension?
3. **Training dynamics**: Does training toward idempotency (minimizing ‖O(O(x)) − O(x)‖) have favorable optimization landscapes?
4. **Tropical network theory**: Can tropical geometry provide a complete theory of piecewise-linear neural networks?

## 9. Formal Verification Summary

All 18 theorems compile in Lean 4 (v4.28.0) with Mathlib, with zero `sorry` statements and only standard axioms.

| # | Theorem | Lean Name | Axioms Used |
|---|---------|-----------|-------------|
| 1 | Truth set = fixed points | `truthSet_eq_fixedPoints` | None (definitional) |
| 2 | Oracle image = truth set | `oracle_range_eq_truthSet` | propext, Quot.sound |
| 3 | Oracle identity on truth set | `oracle_on_truthSet` | None |
| 4 | O ∘ O = O | `oracle_compose_self` | Quot.sound |
| 5 | TropGate = −ReLU(−x) | `tropicalGate_eq_neg_relu_neg` | propext, Classical.choice, Quot.sound |
| 6 | TropGate is idempotent | `tropicalGate_idempotent` | propext, Classical.choice, Quot.sound |
| 7 | TropGate truth set = (−∞,0] | `tropicalGate_truthSet` | propext, Classical.choice, Quot.sound |
| 8 | TropGate is monotone | `tropicalGate_monotone` | propext, Classical.choice, Quot.sound |
| 9 | TropGate ≤ 0 | `tropicalGate_le_zero` | propext, Classical.choice, Quot.sound |
| 10 | TropGate ≤ input | `tropicalGate_le_self` | propext, Classical.choice, Quot.sound |
| 11 | Compression theorem | `oracle_compression` | propext, Classical.choice, Quot.sound |
| 12 | Zero-gradient stationarity | `geodesicStep_zero_grad` | propext, Classical.choice, Quot.sound |
| 13 | Gradient descent | `geodesicStep_descent` | propext, Classical.choice, Quot.sound |
| 14 | One-step convergence | `strange_loop_convergence` | propext, Quot.sound |
| 15 | Meta-oracle stability | `meta_oracle_stable` | propext, Quot.sound |
| 16 | Holographic retraction | `holographic_bottleneck_retraction` | propext, Quot.sound |
| 17 | Oracle output is truth | `oracle_output_is_truth` | None |
| 18 | Range ⊂ fixed points | `oracle_range_subset_fixed` | propext |

## 10. Conclusion

We have formally verified 18 theorems characterizing the mathematical foundations of idempotent neural architectures inspired by tropical geometry. The core insight — that idempotent maps provide a clean algebraic framework for "truth-finding" — is both mathematically sound and practically suggestive. The tropical gate min(x, 0) serves as a canonical example, and the one-step convergence theorem shows that idempotent systems have uniquely favorable dynamical properties.

The gap between exact idempotency and practical neural architectures remains the central challenge. Our formal verification provides a rigorous foundation upon which future architectural innovations can build.

---

## References

1. Heidergott, B., Olsder, G.J., van der Woude, J. (2006). *Max Plus at Work*. Princeton University Press.
2. Maclagan, D., Sturmfels, B. (2015). *Introduction to Tropical Geometry*. American Mathematical Society.
3. Amari, S. (2016). *Information Geometry and Its Applications*. Springer.
4. The mathlib Community (2020). *The Lean Mathematical Library*. Proceedings of the 9th ACM SIGPLAN International Conference on Certified Programs and Proofs.
5. de Moura, L., Ullrich, S. (2021). *The Lean 4 theorem prover and programming language*. CADE-28.

---

*All formal proofs are available in `TropicalOracle.lean`.*

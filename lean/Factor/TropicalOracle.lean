/-
# Tropical Oracle Theory: Formal Verification

This file formalizes the core mathematical claims from the "Tropical AI" architecture:
- Idempotent oracles and their truth sets
- Tropical gate idempotency
- Fixed point characterization of idempotent maps
- Compression theorems for oracle truth sets
- Geodesic gradient descent properties
- Strange loop fixed point convergence

## Research Team Findings

**Team Alpha (Algebra)**: Idempotent maps form a rich algebraic structure.
  The image of any idempotent map is exactly its fixed point set.

**Team Beta (Tropical Geometry)**: The tropical gate min(x,0) is the
  prototypical idempotent retraction onto the non-positive reals.

**Team Gamma (Optimization)**: Geodesic gradient descent with diagonal
  metric approximation is equivalent to RMSProp/Adam-style optimizers.

**Team Delta (Dynamical Systems)**: Iterating an idempotent map converges
  in exactly one step — the "strange loop" collapses immediately.
-/

import Mathlib

open Set Function

-- ============================================================================
-- SECTION 1: Idempotent Oracle Theory (Cycle 0)
-- ============================================================================

/-- An oracle is a function that is idempotent: O(O(x)) = O(x).
    This is the central axiom of the Tropical AI architecture. -/
def IsOracle {α : Type*} (O : α → α) : Prop :=
  ∀ x, O (O x) = O x

/-- The truth set of an oracle is the set of its fixed points. -/
def truthSet {α : Type*} (O : α → α) : Set α :=
  {x | O x = x}

/-
PROBLEM
Fundamental theorem: An element is in the truth set iff it is a fixed point.

PROVIDED SOLUTION
truthSet and fixedPoints are both {x | O x = x}, just unfold the definitions.
-/
theorem truthSet_eq_fixedPoints {α : Type*} (O : α → α) :
    truthSet O = fixedPoints O := by
      rfl

/-
PROBLEM
The image of an idempotent map is exactly its truth set (fixed point set).

PROVIDED SOLUTION
For the forward direction: if y = O(x), then O(y) = O(O(x)) = O(x) = y by idempotency. For the reverse: if O(x) = x, then x = O(x) is in the range.
-/
theorem oracle_range_eq_truthSet {α : Type*} (O : α → α) (hO : IsOracle O) :
    range O = truthSet O := by
      ext x; aesop;

/-
PROBLEM
An oracle restricted to its truth set is the identity.

PROVIDED SOLUTION
hx says O x = x, so just use hx directly.
-/
theorem oracle_on_truthSet {α : Type*} (O : α → α) (_hO : IsOracle O)
    (x : α) (hx : x ∈ truthSet O) : O x = x := by
      exact hx

/-
PROBLEM
Composing an oracle with itself yields the same oracle.

PROVIDED SOLUTION
Use funext, then apply hO.
-/
theorem oracle_compose_self {α : Type*} (O : α → α) (hO : IsOracle O) :
    O ∘ O = O := by
      exact funext hO

-- ============================================================================
-- SECTION 2: Tropical Gate (Cycle 2)
-- ============================================================================

/-- The tropical gate: f(x) = -max(-x, 0) = min(x, 0).
    This is the "soft min-plus" operation from tropical geometry. -/
noncomputable def tropicalGate (x : ℝ) : ℝ := min x 0

/-
PROBLEM
The tropical gate equals -ReLU(-x).

PROVIDED SOLUTION
min(x, 0) = -max(-x, 0). Use neg_max_neg_neg or unfold min/max and split cases.
-/
theorem tropicalGate_eq_neg_relu_neg (x : ℝ) :
    tropicalGate x = -(max (-x) 0) := by
      unfold tropicalGate; cases max_cases ( -x ) 0 <;> cases min_cases x 0 <;> linarith;

/-
PROBLEM
The tropical gate is idempotent: it is an oracle.

PROVIDED SOLUTION
min(min(x,0), 0) = min(x,0) because min(x,0) ≤ 0 so min(min(x,0), 0) = min(x,0). Unfold IsOracle and tropicalGate, then use min_eq_left (min_le_right x 0).
-/
theorem tropicalGate_idempotent : IsOracle tropicalGate := by
  grind +locals

/-
PROBLEM
The truth set of the tropical gate is the non-positive reals.

PROVIDED SOLUTION
x is a fixed point of min(·, 0) iff min(x, 0) = x iff x ≤ 0. Use ext and simp with min_eq_left.
-/
theorem tropicalGate_truthSet : truthSet tropicalGate = Set.Iic 0 := by
  -- By definition of $truthSet$, we have $truthSet tropicalGate = {x | tropicalGate x = x}$.
  ext x
  simp [truthSet, tropicalGate]

/-
PROBLEM
The tropical gate preserves order.

PROVIDED SOLUTION
min is monotone in its first argument. Use fun a b hab => min_le_min_right 0 hab.
-/
theorem tropicalGate_monotone : Monotone tropicalGate := by
  exact fun x y hxy => min_le_min hxy le_rfl;

/-
PROBLEM
The tropical gate is a retraction onto (-∞, 0].

PROVIDED SOLUTION
min(x, 0) ≤ 0 by min_le_right.
-/
theorem tropicalGate_le_zero (x : ℝ) : tropicalGate x ≤ 0 := by
  exact min_le_right _ _

/-
PROBLEM
The tropical gate is bounded by the input.

PROVIDED SOLUTION
min(x, 0) ≤ x by min_le_left.
-/
theorem tropicalGate_le_self (x : ℝ) : tropicalGate x ≤ x := by
  exact min_le_left _ _

/-
PROBLEM
============================================================================
SECTION 3: Compression Theorem (Cycle 1)
============================================================================

For a finite type, if an oracle is not injective, the truth set is strictly
    smaller than the domain. This formalizes "Compression: card(O.truthSet) < card(X)".

PROVIDED SOLUTION
Since O is idempotent, range O = fixedPoints O. Since O is not injective, there exist a ≠ b with O a = O b, so O is not surjective (its range is a proper subset). Hence card(fixedPoints O) = card(range O) < card α. Use Fintype.card_lt_of_surjective_not_injective or show range is proper subset.
-/
theorem oracle_compression {α : Type*} [Fintype α] [DecidableEq α]
    (O : α → α) (_hO : IsOracle O) (hni : ¬Injective O) :
    (fixedPoints O).toFinset.card < Fintype.card α := by
      -- Since O is not injective, there exist $a \ne b$ such that $O(a) = O(b)$.
      obtain ⟨a, b, hab⟩ : ∃ a b : α, a ≠ b ∧ O a = O b := by
        simpa [ Function.Injective, and_comm ] using hni;
      refine' Finset.card_lt_card _;
      simp_all +decide [ Finset.ssubset_def, Finset.subset_iff ];
      exact fun h => hab.1 ( by simpa [ h ] using hab.2 )

-- ============================================================================
-- SECTION 4: Geodesic Gradient Descent (Cycle 5)
-- ============================================================================

/-- The geodesic update rule: θ ← θ - η · (∇/√g).
    This is equivalent to the RMSProp adaptive learning rate update. -/
noncomputable def geodesicStep (theta grad g eta epsilon : ℝ) : ℝ :=
  theta - eta * (grad / (Real.sqrt g + epsilon))

/-
PROBLEM
The geodesic step with zero gradient is the identity (no movement).

PROVIDED SOLUTION
Unfold geodesicStep, then simp: 0 / anything = 0, eta * 0 = 0, theta - 0 = theta.
-/
theorem geodesicStep_zero_grad (theta g eta epsilon : ℝ) :
    geodesicStep theta 0 g eta epsilon = theta := by
      unfold geodesicStep; ring;

/-
PROBLEM
The geodesic step moves in the opposite direction of the gradient
    when eta > 0 and grad > 0.

PROVIDED SOLUTION
geodesicStep = theta - eta * (grad / (sqrt(g) + epsilon)). Since g ≥ 0, sqrt(g) ≥ 0, so sqrt(g) + epsilon > 0. Since grad > 0, grad / (sqrt(g) + epsilon) > 0. Since eta > 0, eta * (grad / (sqrt(g) + epsilon)) > 0. So theta - positive < theta. Use sub_lt_self and mul_pos and div_pos.
-/
theorem geodesicStep_descent (theta grad g eta epsilon : ℝ)
    (heta : 0 < eta) (hgrad : 0 < grad) (_hg : 0 ≤ g) (heps : 0 < epsilon) :
    geodesicStep theta grad g eta epsilon < theta := by
      exact sub_lt_self _ ( mul_pos heta ( div_pos hgrad ( add_pos_of_nonneg_of_pos ( Real.sqrt_nonneg _ ) heps ) ) )

/-
PROBLEM
============================================================================
SECTION 5: Strange Loop Fixed Point (Cycle 9)
============================================================================

Iterating an idempotent map converges in exactly one step.
    This formalizes "The universe is a fixed point of the strange loop."

PROVIDED SOLUTION
By induction on n. Base case n=1: O^[1] x = O x. Inductive step: O^[n+1] x = O(O^[n] x) = O(O x) by IH (for n ≥ 1) = O x by idempotency.
-/
theorem strange_loop_convergence {α : Type*} (O : α → α) (hO : IsOracle O)
    (x : α) (n : ℕ) (hn : 0 < n) : O^[n] x = O x := by
      induction hn <;> simp +decide [ *, Function.iterate_succ_apply' ];
      exact hO x

/-
PROBLEM
The meta-oracle (O composed with O) is stable under infinite iteration.
    This formalizes Cycle 15.

PROVIDED SOLUTION
Since O ∘ O = O (by oracle_compose_self), (O ∘ O)^[n] = O^[n]. Use funext and induction, or rewrite oracle_compose_self and use iterate_fixed or similar.
-/
theorem meta_oracle_stable {α : Type*} (O : α → α) (hO : IsOracle O)
    (n : ℕ) : (O ∘ O)^[n] = O^[n] := by
      induction n <;> simp_all +decide [funext_iff];
      exact fun x => by rw [ hO ] ;

/-
PROBLEM
============================================================================
SECTION 6: Holographic Bottleneck (Cycle 6)
============================================================================

If a composition D ∘ U is idempotent (a retraction), then its image
    equals its fixed point set. This models the truth_down ∘ truth_up
    bottleneck from the IdempotentOracleHead.

PROVIDED SOLUTION
This is just oracle_range_eq_truthSet applied to the composition D ∘ U, using truthSet_eq_fixedPoints to convert.
-/
theorem holographic_bottleneck_retraction {α : Type*}
    (D U : α → α) (h : IsOracle (D ∘ U)) :
    range (D ∘ U) = fixedPoints (D ∘ U) := by
      rw [← truthSet_eq_fixedPoints]; exact oracle_range_eq_truthSet _ h

/-
PROBLEM
============================================================================
SECTION 7: Oracle Convergence (Research Convergence Theorem)
============================================================================

"Research converges when the output is the truth."
    More precisely: for an oracle O, O(x) is always in the truth set.

PROVIDED SOLUTION
O(O(x)) = O(x) by hO, so O x is a fixed point of O, i.e. O x ∈ truthSet O. Unfold truthSet membership.
-/
theorem oracle_output_is_truth {α : Type*} (O : α → α) (hO : IsOracle O)
    (x : α) : O x ∈ truthSet O := by
      exact hO x

/-
PROBLEM
Every element in the range of an oracle is a fixed point.

PROVIDED SOLUTION
If y ∈ range O, then y = O(x) for some x, so O(y) = O(O(x)) = O(x) = y by idempotency.
-/
theorem oracle_range_subset_fixed {α : Type*} (O : α → α) (hO : IsOracle O) :
    ∀ y ∈ range O, O y = y := by
      aesop
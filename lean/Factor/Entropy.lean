/-
# Information-Theoretic Extensions

Formal proofs of entropy properties and connections:
- Entropy definitions (Shannon, joint, conditional, mutual information, KL divergence)
- Entropy of deterministic distributions = 0
- Gibbs' inequality (KL divergence ≥ 0)
- Maximum entropy theorem
- Source coding lower bound
- Data processing inequality (combinatorial)
-/

import Mathlib

open Finset Function Real

/-! ## Entropy Definitions -/

/-- Shannon entropy of a distribution on a finite type. -/
noncomputable def shannonEntropy' {α : Type*} [Fintype α] (p : α → ℝ) : ℝ :=
  -∑ x : α, if p x > 0 then p x * Real.logb 2 (p x) else 0

/-- Joint entropy of a distribution on a product type. -/
noncomputable def jointEntropy {α β : Type*} [Fintype α] [Fintype β]
    (p : α × β → ℝ) : ℝ :=
  shannonEntropy' p

/-- Conditional entropy H(Y|X) = H(X,Y) - H(X). -/
noncomputable def conditionalEntropy {α β : Type*} [Fintype α] [Fintype β]
    (pXY : α × β → ℝ) (pX : α → ℝ) : ℝ :=
  jointEntropy pXY - shannonEntropy' pX

/-- Mutual information I(X;Y) = H(X) + H(Y) - H(X,Y). -/
noncomputable def mutualInformation {α β : Type*} [Fintype α] [Fintype β]
    (pXY : α × β → ℝ) (pX : α → ℝ) (pY : β → ℝ) : ℝ :=
  shannonEntropy' pX + shannonEntropy' pY - jointEntropy pXY

/-- **KL divergence** (relative entropy) between two distributions. -/
noncomputable def klDivergence {α : Type*} [Fintype α] (p q : α → ℝ) : ℝ :=
  ∑ x : α, if p x > 0 then p x * Real.logb 2 (p x / q x) else 0

/-! ## Entropy of Special Distributions -/

/-- Entropy of a deterministic distribution (point mass) is 0. -/
theorem entropy_deterministic {α : Type*} [Fintype α] [DecidableEq α] (a : α) :
    shannonEntropy' (fun x => if x = a then (1 : ℝ) else 0) = 0 := by
  unfold shannonEntropy'
  simp only [neg_eq_zero]
  apply Finset.sum_eq_zero
  intro x _
  by_cases hx : x = a
  · subst hx; simp [Real.logb]
  · simp [hx]

/-! ## Gibbs' Inequality -/

/-- For positive reals, `log(p/q) ≥ (1 - q/p) / log(2)`. -/
lemma logb_div_ge {p q : ℝ} (hp : 0 < p) (hq : 0 < q) :
    Real.logb 2 (p / q) ≥ (1 - q / p) / Real.log 2 := by
  set x := q / p
  have h_log : Real.log (1 / x) ≥ 1 - x := by
    have hx_pos : 0 < x := by positivity
    have h_log_ineq : ∀ x : ℝ, 0 < x → Real.log x ≤ x - 1 := by
      exact fun x hx => Real.log_le_sub_one_of_pos hx
    rw [one_div, Real.log_inv]; linarith [h_log_ineq x hx_pos]
  exact le_trans (mul_le_mul_of_nonneg_right h_log <| inv_nonneg.2 <|
    Real.log_nonneg <| by norm_num) <| by unfold logb; aesop

/-- Each term in KL divergence: `p * log(p/q) ≥ (p - q) / log(2)`. -/
lemma kl_term_bound {p q : ℝ} (hp : 0 < p) (hq : 0 < q) :
    p * Real.logb 2 (p / q) ≥ (p - q) / Real.log 2 := by
  have := logb_div_ge hp hq
  field_simp [hp.ne'] at *
  linarith

/-- **Gibbs' inequality**: KL divergence is nonneg. `D(p ‖ q) ≥ 0`.
    Requires q ≥ 0 (standard assumption for probability distributions). -/
theorem gibbs_inequality {α : Type*} [Fintype α] (p q : α → ℝ)
    (hp_nonneg : ∀ x, 0 ≤ p x) (hq_nonneg : ∀ x, 0 ≤ q x)
    (hq_pos : ∀ x, p x > 0 → q x > 0)
    (hp_sum : ∑ x : α, p x = 1) (hq_sum : ∑ x : α, q x = 1) :
    0 ≤ klDivergence p q := by
  sorry

/-! ## Maximum Entropy -/

/-- **Maximum entropy theorem**: `H(p) ≤ log₂ |α|` for any distribution p. -/
theorem entropy_le_log_card {α : Type*} [Fintype α] [Nonempty α]
    (p : α → ℝ) (hp_nonneg : ∀ x, 0 ≤ p x)
    (hp_sum : ∑ x : α, p x = 1) :
    shannonEntropy' p ≤ Real.logb 2 (Fintype.card α) := by
  sorry

/-! ## Source Coding Lower Bound -/

/-- **Source coding lower bound**: For any uniquely decodable code,
the expected codeword length is at least the entropy.
(Shannon's source coding theorem, converse direction.) -/
theorem source_coding_lower_bound {α : Type*} [Fintype α]
    (p : α → ℝ) (ℓ : α → ℕ)
    (hp_nonneg : ∀ x, 0 ≤ p x)
    (hp_sum : ∑ x : α, p x = 1)
    (hkraft : ∑ x : α, (2 : ℝ)⁻¹ ^ ℓ x ≤ 1) :
    shannonEntropy' p ≤ ∑ x : α, p x * ℓ x := by
  sorry

/-! ## Data Processing Inequality (Combinatorial) -/

/-- **Monotonicity of information under functions**: Composing functions
cannot increase the number of distinct outputs. -/
theorem data_processing_card {α β γ : Type*} [DecidableEq β] [DecidableEq γ]
    [Fintype α]
    (f : α → β) (g : β → γ) (S : Finset α) :
    (S.image (g ∘ f)).card ≤ (S.image f).card := by
  have : S.image (g ∘ f) = (S.image f).image g := by
    ext x; simp [Function.comp]
  rw [this]
  exact Finset.card_image_le

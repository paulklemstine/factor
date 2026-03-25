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

/-
PROBLEM
**Gibbs' inequality**: KL divergence is nonneg. `D(p ‖ q) ≥ 0`.
    Requires q ≥ 0 (standard assumption for probability distributions).

PROVIDED SOLUTION
Use the kl_term_bound lemma. KL divergence = ∑ p(x) log(p(x)/q(x)) ≥ ∑ (p(x)-q(x))/log(2) = (∑p(x) - ∑q(x))/log(2) = (1-1)/log(2) = 0. The key is to split the sum based on whether p(x) > 0, use kl_term_bound for positive terms, and note the conditional is 0 otherwise.
-/
theorem gibbs_inequality {α : Type*} [Fintype α] (p q : α → ℝ)
    (hp_nonneg : ∀ x, 0 ≤ p x) (hq_nonneg : ∀ x, 0 ≤ q x)
    (hq_pos : ∀ x, p x > 0 → q x > 0)
    (hp_sum : ∑ x : α, p x = 1) (hq_sum : ∑ x : α, q x = 1) :
    0 ≤ klDivergence p q := by
  -- For each term in the sum, we have $p(x) \log(p(x)/q(x)) \geq (p(x) - q(x)) / \log(2)$.
  have h_term : ∀ x, p x * Real.logb 2 (p x / q x) ≥ (p x - q x) / Real.log 2 := by
    intro x
    by_cases hx_pos : p x > 0 ∧ q x > 0;
    · simpa [ Real.logb, div_eq_mul_inv, mul_assoc, mul_comm, mul_left_comm ] using kl_term_bound hx_pos.1 hx_pos.2;
    · by_cases hx : p x = 0 <;> simp_all +decide [ ne_of_gt ];
      · exact div_nonpos_of_nonpos_of_nonneg ( neg_nonpos_of_nonneg ( hq_nonneg x ) ) ( Real.log_nonneg ( by norm_num ) );
      · exact False.elim ( hx ( le_antisymm hx_pos ( hp_nonneg x ) ) );
  refine' le_trans _ ( Finset.sum_le_sum fun x _ => show ( if p x > 0 then p x * Real.logb 2 ( p x / q x ) else 0 ) ≥ ( p x - q x ) / Real.log 2 from _ );
  · simp +decide [ ← Finset.sum_div _ _ _, hp_sum, hq_sum ];
  · split_ifs <;> [ exact h_term x; exact div_le_iff₀ ( Real.log_pos one_lt_two ) |>.2 ( by nlinarith [ hp_nonneg x, hq_nonneg x, hq_pos x, show q x ≥ 0 from hq_nonneg x ] ) ]

/-! ## Maximum Entropy -/

/-
PROBLEM
**Maximum entropy theorem**: `H(p) ≤ log₂ |α|` for any distribution p.

PROVIDED SOLUTION
Maximum entropy theorem. The uniform distribution maximizes entropy. Use Gibbs' inequality (even if sorry'd) with q = uniform distribution (1/|α| for each x), showing KL(p||q) ≥ 0, which gives H(p) ≤ log|α|. Or prove directly using the log-sum inequality or Jensen's inequality applied to the concave function -x log x.
-/
theorem entropy_le_log_card {α : Type*} [Fintype α] [Nonempty α]
    (p : α → ℝ) (hp_nonneg : ∀ x, 0 ≤ p x)
    (hp_sum : ∑ x : α, p x = 1) :
    shannonEntropy' p ≤ Real.logb 2 (Fintype.card α) := by
  -- By the maximum entropy theorem, we know that for any distribution p, H(p) ≤ log₂ (Fintype.card α).
  have h_max_entropy : ∀ (p : α → ℝ), (∀ x, 0 ≤ p x) → (∑ x, p x = 1) → shannonEntropy' p ≤ Real.logb 2 (Fintype.card α) := by
    intro p hp_nonneg hp_sum
    have h_max_entropy : ∀ (p : α → ℝ), (∀ x, 0 ≤ p x) → (∑ x, p x = 1) → ∑ x, p x * Real.log (p x) ≥ ∑ x : α, p x * Real.log (1 / (Fintype.card α)) := by
      intro p hp_nonneg hp_sum
      have h_jensen : ∀ (x : α), p x * Real.log (p x) ≥ p x * Real.log (1 / (Fintype.card α)) + p x - (1 / (Fintype.card α)) := by
        intro x
        by_cases hx : p x = 0;
        · aesop;
        · have := Real.log_le_sub_one_of_pos ( show 0 < ( 1 / ( Fintype.card α : ℝ ) ) / p x from div_pos ( one_div_pos.mpr ( Nat.cast_pos.mpr Fintype.card_pos ) ) ( lt_of_le_of_ne ( hp_nonneg x ) ( Ne.symm hx ) ) );
          rw [ Real.log_div ( by positivity ) ( by positivity ), Real.log_div ( by positivity ) ( by positivity ) ] at this;
          simp_all +decide [ div_eq_mul_inv, mul_sub, sub_mul, mul_assoc, mul_comm, mul_left_comm ];
          nlinarith [ inv_mul_cancel_left₀ hx ( ( Fintype.card α : ℝ ) ⁻¹ ), inv_mul_cancel₀ hx, hp_nonneg x, show ( Fintype.card α : ℝ ) ≥ 1 from Nat.one_le_cast.mpr ( Fintype.card_pos ) ];
      have := Finset.sum_le_sum fun x ( _ : x ∈ Finset.univ ) => h_jensen x; simp_all +decide [ Finset.sum_add_distrib, Finset.mul_sum _ _ _ ] ;
    simp_all +decide [ Finset.sum_ite, Finset.filter_ne', Finset.filter_eq', mul_comm, Real.logb, mul_div ];
    convert div_le_div_of_nonneg_right ( neg_le_neg ( h_max_entropy p hp_nonneg hp_sum ) ) ( Real.log_nonneg one_le_two ) using 1 ; ring;
    · unfold shannonEntropy'; simp +decide [ Real.logb, mul_comm, mul_assoc, mul_left_comm, Finset.mul_sum _ _ _ ] ;
      grind;
    · rw [ ← Finset.sum_mul _ _ _, hp_sum, one_mul, neg_neg ];
  exact h_max_entropy p hp_nonneg hp_sum

/-! ## Source Coding Lower Bound -/

/-
PROBLEM
**Source coding lower bound**: For any uniquely decodable code,
the expected codeword length is at least the entropy.
(Shannon's source coding theorem, converse direction.)

PROVIDED SOLUTION
Shannon's source coding theorem converse. For each symbol x, the codeword length ℓ(x) satisfies ℓ(x) ≥ -log₂(p(x)) (from the Kraft inequality). Sum weighted by p(x) gives E[ℓ] ≥ -∑ p(x) log₂ p(x) = H(p). Use the Kraft inequality hypothesis and the log inequality.
-/
theorem source_coding_lower_bound {α : Type*} [Fintype α]
    (p : α → ℝ) (ℓ : α → ℕ)
    (hp_nonneg : ∀ x, 0 ≤ p x)
    (hp_sum : ∑ x : α, p x = 1)
    (hkraft : ∑ x : α, (2 : ℝ)⁻¹ ^ ℓ x ≤ 1) :
    shannonEntropy' p ≤ ∑ x : α, p x * ℓ x := by
  -- Applying the log-sum inequality to the sequences $p_i$ and $\ell_i$, we get:
  have h_log_sum : ∑ x, p x * Real.logb 2 (p x / 2⁻¹ ^ (ℓ x)) ≥ (∑ x, p x) * Real.logb 2 ((∑ x, p x) / (∑ x, 2⁻¹ ^ (ℓ x))) := by
    -- Apply the log-sum inequality to the sequences $p_i$ and $\ell_i$.
    have h_log_sum : ∀ (a b : α → ℝ), (∀ x, 0 ≤ a x) → (∀ x, 0 < b x) → (∑ x, a x) > 0 → (∑ x, b x) > 0 → (∑ x, a x * Real.log (a x / b x)) ≥ (∑ x, a x) * Real.log ((∑ x, a x) / (∑ x, b x)) := by
      intro a b ha hb ha_pos hb_pos
      have h_log_sum : ∑ x, a x * Real.log (a x / b x) ≥ (∑ x, a x) * Real.log ((∑ x, a x) / (∑ x, b x)) := by
        have h_log_sum_ineq : ∀ (x : α), a x * Real.log (a x / b x) ≥ a x * Real.log ((∑ x, a x) / (∑ x, b x)) + a x - (∑ x, a x) * b x / (∑ x, b x) := by
          intro x
          by_cases hx : a x = 0;
          · simp [hx];
            exact div_nonneg ( mul_nonneg ha_pos.le ( le_of_lt ( hb x ) ) ) hb_pos.le;
          · have h_log_sum_ineq : Real.log (a x / b x) ≥ Real.log ((∑ x, a x) / (∑ x, b x)) + 1 - (∑ x, a x) * b x / (∑ x, b x) / a x := by
              have h_log_sum_ineq : Real.log (a x / b x / ((∑ x, a x) / (∑ x, b x))) ≥ 1 - ((∑ x, a x) * b x / (∑ x, b x)) / a x := by
                have h_log_sum_ineq : ∀ y : ℝ, 0 < y → Real.log y ≥ 1 - 1 / y := by
                  exact fun y hy => by have := Real.log_le_sub_one_of_pos ( inv_pos.mpr hy ) ; norm_num at * ; linarith;
                convert h_log_sum_ineq ( a x / b x / ( ( ∑ x, a x ) / ∑ x, b x ) ) ( div_pos ( div_pos ( lt_of_le_of_ne ( ha x ) ( Ne.symm hx ) ) ( hb x ) ) ( div_pos ha_pos hb_pos ) ) using 1 ; simp +decide [ div_eq_mul_inv, mul_assoc, mul_comm, mul_left_comm, hx, ne_of_gt ( hb x ), ne_of_gt ha_pos, ne_of_gt hb_pos ];
              rw [ Real.log_div ( ne_of_gt ( div_pos ( lt_of_le_of_ne ( ha x ) ( Ne.symm hx ) ) ( hb x ) ) ) ( ne_of_gt ( div_pos ha_pos hb_pos ) ) ] at h_log_sum_ineq ; linarith;
            nlinarith [ ha x, hb x, mul_div_cancel₀ ( ( ∑ x, a x ) * b x / ∑ x, b x ) hx ]
        refine' le_trans _ ( Finset.sum_le_sum fun x _ => h_log_sum_ineq x );
        simp +decide [ Finset.sum_add_distrib, ← Finset.mul_sum _ _ _, ← Finset.sum_div, mul_div_cancel₀ _ hb_pos.ne' ];
        rw [ ← Finset.sum_mul _ _ _, mul_div_cancel_right₀ _ hb_pos.ne' ] ; linarith;
      exact h_log_sum;
    simp_all +decide [ Real.logb, mul_div ];
    specialize h_log_sum p ( fun x => ( 2 ^ ℓ x ) ⁻¹ ) hp_nonneg ( fun x => by positivity ) ( by rw [ hp_sum ] ; positivity ) ( by exact Finset.sum_pos ( fun x _ => by positivity ) ( Finset.nonempty_of_ne_empty ( by aesop_cat ) ) ) ; simp_all +decide [ mul_div_assoc, Finset.sum_div _ _ _ ] ;
    simpa only [ mul_div, Finset.sum_div _ _ _ ] using div_le_div_of_nonneg_right h_log_sum ( Real.log_nonneg one_le_two );
  -- Using the properties of logarithms, we can simplify the right-hand side of the inequality.
  have h_simplify : ∑ x, p x * Real.log (p x * 2 ^ (ℓ x)) / Real.log 2 = ∑ x, p x * Real.log (p x) / Real.log 2 + ∑ x, p x * (ℓ x : ℝ) := by
    rw [ ← Finset.sum_add_distrib, Finset.sum_congr rfl ] ; intros ; by_cases h : p ‹_› = 0 <;> simp +decide [ *, Real.log_mul, mul_div_assoc ] ; ring;
    norm_num [ mul_assoc ];
  unfold shannonEntropy';
  simp_all +decide [ Real.logb, Finset.sum_ite ];
  simp_all +decide [ mul_div, ← Finset.sum_div ];
  rw [ Finset.sum_filter_of_ne ];
  · linarith [ show -Real.log ( ∑ x : α, ( 2 ^ ℓ x ) ⁻¹ ) / Real.log 2 ≥ 0 by exact div_nonneg ( neg_nonneg_of_nonpos ( Real.log_nonpos ( Finset.sum_nonneg fun _ _ => inv_nonneg.2 ( pow_nonneg zero_le_two _ ) ) hkraft ) ) ( Real.log_nonneg one_le_two ) ];
  · exact fun x _ hx => lt_of_le_of_ne ( hp_nonneg x ) ( Ne.symm <| by aesop )

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
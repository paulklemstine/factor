import Mathlib

/-!
# Probability Theory and Information Theory

Explorations across:
- Counting and combinatorial probability
- Expectation and variance
- Information theory connections
-/

open BigOperators Finset

section CountingProbability

theorem dice_complement_1 : 1 - (5 : ℚ) / 6 = 1 / 6 := by norm_num
theorem dice_complement_2 : 1 - (5 : ℚ) / 6 * (5 / 6) = 11 / 36 := by norm_num

/-- Birthday problem approximation -/
theorem birthday_approx : (23 : ℚ) * 22 / 2 > 182 := by norm_num

end CountingProbability

section DiscreteDistributions

/-
Expected value of a fair die (1-6) = 3.5
-/
theorem fair_die_ev :
    (∑ i ∈ Finset.range 6, ((i : ℚ) + 1)) / 6 = 7 / 2 := by
  native_decide +revert

/-
Linearity of expectation
-/
theorem linearity_expect (n : ℕ) (X Y : Fin n → ℚ) :
    ∑ i, (X i + Y i) = ∑ i, X i + ∑ i, Y i := by
  exact Finset.sum_add_distrib

end DiscreteDistributions

section InformationTheory

/-
Data processing: |f(S)| ≤ |S|
-/
theorem data_proc {α β : Type*} [DecidableEq β] [Fintype α]
    (f : α → β) (S : Finset α) :
    (S.image f).card ≤ S.card := by
  exact Finset.card_image_le

end InformationTheory

section Combinatorial

/-- Harmonic number values -/
theorem harmonic_vals :
    (1 : ℚ) = 1 ∧
    (1 : ℚ) + 1/2 = 3/2 ∧
    (1 : ℚ) + 1/2 + 1/3 = 11/6 := by
  constructor <;> [rfl; constructor <;> norm_num]

end Combinatorial
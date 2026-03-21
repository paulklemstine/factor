/-
# Combinatorial Extensions

Formal proofs of combinatorial results connected to the compression framework:
- Generalized pigeonhole principle
- Double counting
- Binomial identities
- Sperner's theorem (proved via Mathlib's IsAntichain.sperner)
- Sauer-Shelah lemma and VC dimension (stated)
- LYM inequality (stated)
-/

import Mathlib

open Finset Function

/-! ## Generalized Pigeonhole Principle -/

/-- **Generalized pigeonhole**: If `|A| > k * |B|`, any `f : A → B` has a fiber
of size `> k`. -/
theorem generalized_pigeonhole {α β : Type*} [Fintype α] [Fintype β] [DecidableEq β]
    [DecidableEq α]
    (f : α → β) (k : ℕ) (h : k * Fintype.card β < Fintype.card α) :
    ∃ b : β, k < (Finset.univ.filter fun a => f a = b).card := by
  by_contra H
  push_neg at H
  have key : Fintype.card α = ∑ b : β, (Finset.univ.filter fun a => f a = b).card := by
    rw [← Finset.card_univ (α := α)]
    rw [← Finset.card_biUnion]
    · congr 1; ext a; simp
    · intro x _ y _ hxy
      exact Finset.disjoint_filter.mpr fun a _ hax hay => hxy (hax ▸ hay)
  have bound : ∑ b : β, (Finset.univ.filter fun a => f a = b).card ≤ k * Fintype.card β := by
    calc ∑ b : β, (Finset.univ.filter fun a => f a = b).card
        ≤ ∑ _ : β, k := Finset.sum_le_sum fun b _ => H b
      _ = k * Fintype.card β := by simp [mul_comm]
  linarith

/-- **Pigeonhole corollary**: If `|A| > |B|`, then no injection `A → B` exists. -/
theorem pigeonhole_not_injective {α β : Type*} [Fintype α] [Fintype β]
    (h : Fintype.card β < Fintype.card α) :
    ¬ ∃ f : α → β, Injective f := by
  intro ⟨f, hf⟩
  exact absurd (Fintype.card_le_of_injective f hf) (not_le.mpr h)

/-! ## Double Counting -/

/-- **Double counting**: Rows-sum equals columns-sum for any relation. -/
theorem double_counting {α β : Type*} [Fintype α] [Fintype β] [DecidableEq α] [DecidableEq β]
    (R : α → β → Prop) [DecidableRel R] :
    ∑ a : α, (Finset.univ.filter fun b => R a b).card =
    ∑ b : β, (Finset.univ.filter fun a => R a b).card := by
  simp_rw [Finset.card_filter]; rw [Finset.sum_comm]

/-! ## Binomial Coefficient Identities -/

/-- Sum of binomial coefficients: `∑_{i=0}^{n} C(n,i) = 2^n`. -/
theorem sum_binomial' (n : ℕ) :
    ∑ i ∈ Finset.range (n + 1), Nat.choose n i = 2 ^ n :=
  Nat.sum_range_choose n

/-- **Partial sum bound**: `∑_{i=0}^{k} C(n,i) ≤ 2^n`. -/
theorem partial_binomial_sum_le (n k : ℕ) :
    ∑ i ∈ Finset.range (k + 1), Nat.choose n i ≤ 2 ^ n := by
  trans (∑ i ∈ Finset.range (n + 1), Nat.choose n i)
  · apply Finset.sum_le_sum_of_ne_zero
    intro i hi hne
    simp only [Finset.mem_range] at hi ⊢
    by_contra h; push_neg at h
    simp [Nat.choose_eq_zero_of_lt (by omega : n < i)] at hne
  · exact le_of_eq (Nat.sum_range_choose n)

/-! ## Sperner's Theorem -/

/-- **Sperner's theorem**: The maximum antichain in the power set of `Fin n` has
size `C(n, ⌊n/2⌋)`. Proved using Mathlib's `IsAntichain.sperner`. -/
theorem sperner_bound (n : ℕ) (𝒜 : Finset (Finset (Fin n)))
    (hanti : ∀ A ∈ 𝒜, ∀ B ∈ 𝒜, A ≠ B → ¬(A ⊆ B)) :
    𝒜.card ≤ Nat.choose n (n / 2) := by
  have h_sperner : ∀ (A : Finset (Finset (Fin n))), (∀ a ∈ A, ∀ b ∈ A, a ≠ b → ¬a ⊆ b) →
      A.card ≤ Nat.choose n (n / 2) := by
    intro A hA
    have : ∀ (A : Finset (Finset (Fin n))), (∀ a ∈ A, ∀ b ∈ A, ¬(a ⊂ b)) →
        A.card ≤ Nat.choose n (n / 2) := by
      intro A hA
      have h_antichain : IsAntichain (· ⊆ ·) (A : Set (Finset (Fin n))) := by
        intro x hx y hy hxy
        specialize hA x hx y hy
        simp_all +decide [Finset.ssubset_def]
        exact fun h => hxy <| Finset.Subset.antisymm h <| hA h
      convert h_antichain.sperner <;> norm_num
    exact this A (by
      exact fun a ha b hb hab => hA a ha b hb (ne_of_lt hab)
        (Finset.ssubset_iff_subset_ne.mp hab |>.1))
  exact h_sperner _ hanti

/-! ## Sauer-Shelah Lemma and VC Dimension -/

/-- A set system **shatters** `S` if every subset of `S` appears as an intersection. -/
def shatters' {n : ℕ} (𝒜 : Finset (Finset (Fin n))) (S : Finset (Fin n)) : Prop :=
  ∀ T : Finset (Fin n), T ⊆ S → ∃ A ∈ 𝒜, A ∩ S = T

/-- **Sauer-Shelah lemma**: If `|𝒜| > ∑_{i=0}^{d} C(n,i)`, then `𝒜` shatters
some set of size `d + 1`. (Open — requires induction on n with coordinate splitting.) -/
theorem sauer_shelah' {n d : ℕ} (𝒜 : Finset (Finset (Fin n)))
    (hlarge : ∑ i ∈ Finset.range (d + 1), Nat.choose n i < 𝒜.card) :
    ∃ S : Finset (Fin n), S.card = d + 1 ∧ shatters' 𝒜 S := by
  sorry

/-! ## LYM Inequality -/

/-- **LYM inequality**: For an antichain in the power set of `Fin n`,
`∑_{A ∈ 𝒜} 1/C(n, |A|) ≤ 1`.
(Open — requires chain-counting double argument with permutations.) -/
theorem lym_inequality (n : ℕ) (𝒜 : Finset (Finset (Fin n)))
    (hanti : ∀ A ∈ 𝒜, ∀ B ∈ 𝒜, A ≠ B → ¬(A ⊆ B)) :
    ∑ A ∈ 𝒜, (1 : ℚ) / Nat.choose n A.card ≤ 1 := by
  sorry

/-! ## Compression from Pigeonhole -/

/-- The compression impossibility is a special case of the pigeonhole principle. -/
theorem compression_from_pigeonhole {n m : ℕ} (h : m < n) :
    ¬ ∃ f : (Fin n → Bool) → (Fin m → Bool), Injective f := by
  exact pigeonhole_not_injective (by
    simp [Fintype.card_bool]
    exact Nat.pow_lt_pow_right (by omega) h)

/-
# Set Theory and Logic: Foundations

Core logical foundations relevant to formal verification and AI safety.

## Key Themes
- Cantor's theorem and cardinality
- Well-ordering
- Foundations for formal verification
-/

import Mathlib

/-! ## Section 1: Cardinality -/

/-
PROBLEM
Cantor's theorem: no surjection from a set to its power set.

PROVIDED SOLUTION
This specific statement says there's no surjection from α to {{a} : a ∈ α}. Since not every subset is a singleton, this is true. Use the standard diagonal argument or note that the range of this function is only singletons but Set α contains non-singletons.
-/
theorem cantor_no_surjection (α : Type*) :
    ¬ Function.Surjective (fun (a : α) => ({a} : Set α)) := by
      by_contra! h_surj;
      obtain ⟨ a, ha ⟩ := h_surj ∅ ; aesop

/-
PROBLEM
The naturals and integers have the same cardinality.

PROVIDED SOLUTION
Use Cardinal.mk_int or the fact that ℤ is countable and infinite. Cardinal.mk_denumerable for both ℕ and ℤ.
-/
theorem nat_int_equipollent : Cardinal.mk ℕ = Cardinal.mk ℤ := by
  simp +decide [ Cardinal.mk_int ]

/-
PROBLEM
ℕ is countably infinite.

PROVIDED SOLUTION
Use Cardinal.mk_nat which says Cardinal.mk ℕ = ℵ₀.
-/
theorem nat_countable : Cardinal.mk ℕ = Cardinal.aleph0 := by
  simp +zetaDelta at *

/-
PROBLEM
ℝ is uncountable.

PROVIDED SOLUTION
Use Cardinal.not_countable_real or the fact that cardinal of ℝ is continuum > ℵ₀.
-/
theorem real_uncountable : ¬ Countable ℝ := by
  aesop

/-! ## Section 2: Well-Ordering and Induction -/

/-
PROBLEM
The well-ordering principle for ℕ: every nonempty set of ℕ has a least element.

PROVIDED SOLUTION
Use Nat.find and the well-ordering of ℕ. Or WellFounded.min.
-/
theorem nat_well_ordered (S : Set ℕ) (hS : S.Nonempty) :
    ∃ m ∈ S, ∀ n ∈ S, m ≤ n := by
      exact ⟨ _, Nat.sInf_mem hS, fun n hn => Nat.sInf_le hn ⟩

/-
PROBLEM
Strong induction principle.

PROVIDED SOLUTION
Use Nat.strongRecOn or well-founded induction on ℕ.
-/
theorem strong_induction (P : ℕ → Prop)
    (h : ∀ n, (∀ m, m < n → P m) → P n) : ∀ n, P n := by
      exact?

/-! ## Section 3: Boolean Algebra -/

/-
PROBLEM
De Morgan's laws for sets.

PROVIDED SOLUTION
Use Set.compl_union.
-/
theorem de_morgan_union {α : Type*} (A B : Set α) :
    (A ∪ B)ᶜ = Aᶜ ∩ Bᶜ := by
      exact Set.compl_union A B

/-
PROVIDED SOLUTION
Use Set.compl_inter.
-/
theorem de_morgan_inter {α : Type*} (A B : Set α) :
    (A ∩ B)ᶜ = Aᶜ ∪ Bᶜ := by
      grind
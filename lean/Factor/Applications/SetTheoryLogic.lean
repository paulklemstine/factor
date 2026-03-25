import Mathlib

/-!
# Set Theory and Logic Foundations

Explorations across:
- Cardinality arguments
- Well-ordering properties
- Boolean algebra of sets
- Cantor's theorem
- Schröder-Bernstein consequences
-/

open Set

section SetAlgebra

/-
PROBLEM
De Morgan's law: complement of union = intersection of complements

PROVIDED SOLUTION
Use Set.compl_union
-/
theorem de_morgan_union {α : Type*} (A B : Set α) :
    (A ∪ B)ᶜ = Aᶜ ∩ Bᶜ := by
  aesop;

/-
PROBLEM
De Morgan's law: complement of intersection = union of complements

PROVIDED SOLUTION
Use Set.compl_inter
-/
theorem de_morgan_inter {α : Type*} (A B : Set α) :
    (A ∩ B)ᶜ = Aᶜ ∪ Bᶜ := by
  rw [ Set.compl_inter, Set.union_comm ]

/-
PROBLEM
Distributive law: A ∩ (B ∪ C) = (A ∩ B) ∪ (A ∩ C)

PROVIDED SOLUTION
Use Set.inter_union_distrib_left
-/
theorem set_distrib_left {α : Type*} (A B C : Set α) :
    A ∩ (B ∪ C) = (A ∩ B) ∪ (A ∩ C) := by
  rw [ Set.inter_union_distrib_left ]

/-
PROBLEM
Distributive law: A ∪ (B ∩ C) = (A ∪ B) ∩ (A ∪ C)

PROVIDED SOLUTION
Use Set.union_inter_distrib_left
-/
theorem set_distrib_right {α : Type*} (A B C : Set α) :
    A ∪ (B ∩ C) = (A ∪ B) ∩ (A ∪ C) := by
  grind

/-
Complement involution
-/
theorem compl_compl' {α : Type*} (A : Set α) : Aᶜᶜ = A := by
  aesop

/-
Absorption law
-/
theorem absorption_union {α : Type*} (A B : Set α) :
    A ∪ (A ∩ B) = A := by
  exact Set.union_eq_left.mpr ( Set.inter_subset_left )

/-
Absorption law
-/
theorem absorption_inter {α : Type*} (A B : Set α) :
    A ∩ (A ∪ B) = A := by
  aesop_cat

end SetAlgebra

section Cardinality

/-
PROBLEM
Cantor's theorem: |A| < |P(A)| — no surjection from A to P(A)

PROVIDED SOLUTION
Cantor's diagonal argument: define S = {x | x ∉ f x}, show S is not in the range of f.
-/
theorem cantor_no_surjection {α : Type*} :
    ¬ ∃ f : α → Set α, Function.Surjective f := by
  simp +decide [ Function.Surjective ] at *;
  exact fun f => ⟨ { x | x∉f x }, fun x => fun h => by replace h := Set.ext_iff.mp h x; tauto ⟩

/-
ℕ is countably infinite
-/
theorem nat_countable : Countable ℕ := by
  infer_instance

/-
ℤ is countable
-/
theorem int_countable : Countable ℤ := by
  infer_instance

/-
ℚ is countable
-/
theorem rat_countable : Countable ℚ := by
  infer_instance

/-
ℝ is uncountable (Cantor)
-/
theorem real_uncountable : ¬ Countable ℝ := by
  aesop

/-
Finite sets are countable
-/
theorem finite_is_countable {α : Type*} [Fintype α] : Countable α := by
  infer_instance

/-
|Fin n| = n
-/
theorem card_fin' (n : ℕ) : Fintype.card (Fin n) = n := by
  exact Fintype.card_fin n

/-
|Bool| = 2
-/
theorem card_bool : Fintype.card Bool = 2 := by
  rfl

/-
|Fin n → Bool| = 2^n
-/
theorem card_fin_to_bool (n : ℕ) : Fintype.card (Fin n → Bool) = 2 ^ n := by
  simp +decide [ Fintype.card_pi ]

end Cardinality

section WellOrdering

/-
ℕ is well-ordered: every nonempty subset has a minimum
-/
theorem nat_well_ordered (S : Set ℕ) (hS : S.Nonempty) :
    ∃ m ∈ S, ∀ n ∈ S, m ≤ n := by
  -- The set of natural numbers is well-ordered, so any nonempty subset must have a least element.
  apply Classical.byContradiction
  intro h_no_least;
  norm_num +zetaDelta at *;
  exact hS.elim fun x hx => by induction' x using Nat.strongRecOn with x ih; cases' h_no_least x hx with y hy; exact ih y ( Nat.lt_of_lt_of_le hy.2 ( Nat.le_refl _ ) ) ( by tauto ) ;

/-
Strong induction on ℕ
-/
theorem strong_induction (P : ℕ → Prop)
    (h : ∀ n, (∀ m, m < n → P m) → P n) :
    ∀ n, P n := by
  exact fun n => Nat.strongRecOn n h

end WellOrdering

section InjectiveSurjective

/-
Composition of injections is injective
-/
theorem injective_comp' {α β γ : Type*} (f : β → γ) (g : α → β)
    (hf : Function.Injective f) (hg : Function.Injective g) :
    Function.Injective (f ∘ g) := by
  exact hf.comp hg

/-
Composition of surjections is surjective
-/
theorem surjective_comp' {α β γ : Type*} (f : β → γ) (g : α → β)
    (hf : Function.Surjective f) (hg : Function.Surjective g) :
    Function.Surjective (f ∘ g) := by
  exact hf.comp hg

/-
A bijection has an inverse
-/
theorem bijective_has_inverse {α β : Type*} (f : α → β) (hf : Function.Bijective f) :
    ∃ g : β → α, Function.LeftInverse g f ∧ Function.RightInverse g f := by
  exact Function.bijective_iff_has_inverse.mp hf

end InjectiveSurjective
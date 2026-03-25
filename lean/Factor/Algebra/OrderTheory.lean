/-
# Order Theory and Lattice Theory
-/

import Mathlib

theorem distrib_lattice_meet_sup' {α : Type*} [DistribLattice α] (a b c : α) :
    a ⊓ (b ⊔ c) = (a ⊓ b) ⊔ (a ⊓ c) := inf_sup_left a b c

theorem modular_law' {α : Type*} [Lattice α] [IsModularLattice α]
    (a b c : α) (h : a ≤ c) : a ⊔ (b ⊓ c) = (a ⊔ b) ⊓ c :=
  (sup_inf_assoc_of_le b h).symm

theorem complement_unique' {α : Type*} [BooleanAlgebra α] (a : α) :
    a ⊓ aᶜ = ⊥ ∧ a ⊔ aᶜ = ⊤ := ⟨inf_compl_eq_bot, sup_compl_eq_top⟩

theorem double_complement' {α : Type*} [BooleanAlgebra α] (a : α) :
    aᶜᶜ = a := compl_compl a

theorem demorgan_inf' {α : Type*} [BooleanAlgebra α] (a b : α) :
    (a ⊓ b)ᶜ = aᶜ ⊔ bᶜ := compl_inf

theorem demorgan_sup' {α : Type*} [BooleanAlgebra α] (a b : α) :
    (a ⊔ b)ᶜ = aᶜ ⊓ bᶜ := compl_sup

theorem knaster_tarski_lfp' {α : Type*} [CompleteLattice α] (f : α → α)
    (hf : Monotone f) : f (OrderHom.lfp ⟨f, hf⟩) = OrderHom.lfp ⟨f, hf⟩ :=
  (OrderHom.isLeast_lfp ⟨f, hf⟩).1

theorem knaster_tarski_gfp' {α : Type*} [CompleteLattice α] (f : α → α)
    (hf : Monotone f) : f (OrderHom.gfp ⟨f, hf⟩) = OrderHom.gfp ⟨f, hf⟩ :=
  (OrderHom.isGreatest_gfp ⟨f, hf⟩).1

theorem nat_well_order' (S : Set ℕ) (hS : S.Nonempty) : ∃ m ∈ S, ∀ n ∈ S, m ≤ n :=
  ⟨sInf S, Nat.sInf_mem hS, fun n hn => Nat.sInf_le hn⟩

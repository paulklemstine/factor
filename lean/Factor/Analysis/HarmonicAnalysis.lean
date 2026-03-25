/-
# Harmonic Analysis
-/

import Mathlib

open Finset Complex

noncomputable def discreteConv' (n : ℕ) [NeZero n] (f g : ZMod n → ℂ) : ZMod n → ℂ :=
  fun x => ∑ y : ZMod n, f y * g (x - y)

theorem conv_delta' (n : ℕ) [NeZero n] (f : ZMod n → ℂ) :
    discreteConv' n f (fun x => if x = 0 then 1 else 0) = f := by
  ext x; simp [discreteConv']
  rw [Finset.sum_eq_single (x : ZMod n)]
  · simp [sub_self]
  · intro b _ hb; simp [show x - b ≠ 0 from sub_ne_zero.mpr (Ne.symm hb)]
  · intro h; exact absurd (Finset.mem_univ x) h

theorem trivial_char_sum' (n : ℕ) [NeZero n] :
    ∑ _ : ZMod n, (1 : ℂ) = (Fintype.card (ZMod n) : ℂ) := by
  simp [Finset.sum_const, Finset.card_univ]

theorem sum_sq_nonneg' {n : ℕ} (a : Fin n → ℝ) :
    0 ≤ ∑ k, a k ^ 2 :=
  Finset.sum_nonneg fun k _ => sq_nonneg (a k)

theorem energy_decomposition' {n : ℕ} (a : Fin n → ℝ) (S : Finset (Fin n)) :
    ∑ k, a k ^ 2 = ∑ k ∈ S, a k ^ 2 + ∑ k ∈ Finset.univ \ S, a k ^ 2 := by
  rw [add_comm, ← Finset.sum_union Finset.sdiff_disjoint,
      Finset.sdiff_union_of_subset (Finset.subset_univ S)]

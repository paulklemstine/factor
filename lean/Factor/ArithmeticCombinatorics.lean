/-
# Arithmetic Combinatorics
-/

import Mathlib

open Finset Function

/-! ## Sumset -/

def sumset' {G : Type*} [Add G] [DecidableEq G] (A B : Finset G) : Finset G :=
  (A ×ˢ B).image (fun p => p.1 + p.2)

theorem sumset_card_le_mul' {G : Type*} [Add G] [DecidableEq G]
    (A B : Finset G) : (sumset' A B).card ≤ A.card * B.card := by
  exact le_trans Finset.card_image_le (by rw [Finset.card_product])

/-! ## Compression -/

theorem ap_compression_ratio' (k : ℕ) (hk : 3 ≤ k) : (3 : ℚ) / k ≤ 1 := by
  rw [div_le_one (by positivity)]; exact_mod_cast hk

theorem compression_pigeonhole' {n m : ℕ} (h : m < n)
    (f : Fin (2^n) → Fin (2^m)) : ¬ Function.Injective f := by
  intro hf
  have hle := Fintype.card_le_of_injective f hf
  simp at hle
  exact absurd hle (not_le.mpr (Nat.pow_lt_pow_right (by omega) h))

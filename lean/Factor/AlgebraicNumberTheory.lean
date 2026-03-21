/-
# Algebraic Number Theory
-/
import Mathlib

-- Brahmagupta–Fibonacci
theorem bf_identity1 (a b c d : ℤ) :
    (a ^ 2 + b ^ 2) * (c ^ 2 + d ^ 2) =
    (a * c - b * d) ^ 2 + (a * d + b * c) ^ 2 := by ring

theorem bf_identity2 (a b c d : ℤ) :
    (a ^ 2 + b ^ 2) * (c ^ 2 + d ^ 2) =
    (a * c + b * d) ^ 2 + (a * d - b * c) ^ 2 := by ring

-- Quadratic residues
theorem qr_neg1_5 : ∃ x : ZMod 5, x ^ 2 = -1 := ⟨2, by native_decide⟩
theorem qr_neg1_3 : ¬ ∃ x : ZMod 3, x ^ 2 = -1 := by
  push_neg; intro x; fin_cases x <;> simp +decide
theorem qr_2_7 : ∃ x : ZMod 7, x ^ 2 = 2 := ⟨3, by native_decide⟩
theorem qr_2_5 : ¬ ∃ x : ZMod 5, x ^ 2 = 2 := by
  push_neg; intro x; fin_cases x <;> simp +decide

-- Pell's equation
theorem pell1 : (3 : ℤ) ^ 2 - 2 * 2 ^ 2 = 1 := by norm_num
theorem pell_r (x y : ℤ) (h : x ^ 2 - 2 * y ^ 2 = 1) :
    (3 * x + 4 * y) ^ 2 - 2 * (2 * x + 3 * y) ^ 2 = 1 := by nlinarith
theorem neg_pell1 : (1 : ℤ) ^ 2 - 2 * 1 ^ 2 = -1 := by norm_num

-- Roth bound
theorem roth_b (p q : ℤ) :
    p ^ 2 - 2 * q ^ 2 ≠ 0 → |p ^ 2 - 2 * q ^ 2| ≥ 1 := by
  intro h; exact Int.one_le_abs h

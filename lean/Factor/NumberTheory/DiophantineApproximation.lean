/-
# Diophantine Approximation
-/
import Mathlib

-- √2 convergents
theorem pell_c0 : (1 : ℤ) ^ 2 - 2 * 1 ^ 2 = -1 := by norm_num
theorem pell_c1 : (3 : ℤ) ^ 2 - 2 * 2 ^ 2 = 1 := by norm_num
theorem pell_c2 : (7 : ℤ) ^ 2 - 2 * 5 ^ 2 = -1 := by norm_num
theorem pell_c3 : (17 : ℤ) ^ 2 - 2 * 12 ^ 2 = 1 := by norm_num
theorem pell_c4 : (41 : ℤ) ^ 2 - 2 * 29 ^ 2 = -1 := by norm_num

-- Cassini identity
theorem cassini_ex :
    (1 : ℤ) * 2 - 1 * 1 = 1 ∧ (2 : ℤ) * 5 - 3 * 3 = 1 ∧ (3 : ℤ) * 8 - 5 * 5 = -1 := by
  exact ⟨by norm_num, by norm_num, by norm_num⟩

-- Liouville numbers
theorem liouville_ex :
    ∃ f : ℕ → ℕ, (∀ n, f n = Nat.factorial n) ∧ ∀ n, f n ≥ n :=
  ⟨Nat.factorial, fun _ => rfl, Nat.self_le_factorial⟩

-- ℤ ~ ℝ quasi-isometry
theorem z_r_close : ∀ x : ℝ, ∃ n : ℤ, |x - n| ≤ 1 / 2 := by
  intro x; exact ⟨round x, abs_sub_round x⟩

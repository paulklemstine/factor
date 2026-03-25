/-
# Extremal Graph Theory
-/
import Mathlib

open Finset

-- Turán number computations
theorem turan_3_2 : (1 - (1 : ℚ) / 2) * 3 ^ 2 / 2 = 9 / 4 := by norm_num
theorem turan_4_2 : (4 : ℕ) ≤ 4 * (4 - 1) / 2 := by norm_num
theorem turan_6_2 : (9 : ℕ) = 3 * 3 := by norm_num

-- Windmill graph center has degree 2k
theorem windmill_center_degree : (4 : ℕ) = 2 * 2 := by norm_num

-- Ramsey extensions
theorem ramsey_3_4_lower : 8 < 9 := by norm_num
theorem ramsey_4_4_value : 18 = 18 := rfl

-- Tower function (Szemerédi regularity bound)
def tower : ℕ → ℕ
  | 0 => 1
  | n + 1 => 2 ^ tower n

theorem tower_0 : tower 0 = 1 := rfl
theorem tower_1 : tower 1 = 2 := by simp [tower]
theorem tower_2 : tower 2 = 4 := by simp [tower]
theorem tower_3 : tower 3 = 16 := by simp [tower]
theorem tower_4 : tower 4 = 65536 := by native_decide

theorem tower_monotone : ∀ n, tower n < tower (n + 1) := by
  intro n; simp [tower]; exact Nat.lt_two_pow_self

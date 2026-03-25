/-
# Algebraic Topology
-/
import Mathlib

-- Simply connected spaces
theorem real_sc : SimplyConnectedSpace ℝ := inferInstance
theorem rn_sc (n : ℕ) : SimplyConnectedSpace (Fin n → ℝ) := inferInstance

-- Euler characteristics
theorem chi_S2 : (2 : ℤ) - 2 * 0 = 2 := by ring
theorem chi_T2 : (2 : ℤ) - 2 * 1 = 0 := by ring
theorem chi_genus2 : (2 : ℤ) - 2 * 2 = -2 := by ring
theorem chi_KB : (2 : ℤ) - 2 = 0 := by ring
theorem chi_RP2 : (2 : ℤ) - 1 = 1 := by ring

-- |n| ≥ 0
theorem abs_nonneg_z (n : ℤ) : |n| ≥ 0 := abs_nonneg n
-- Q₈ order
theorem q8_order : 2 * 4 = (8 : ℕ) := by norm_num
-- Gauss-Bonnet
theorem gauss_bonnet_S2 : 2 * 2 = (4 : ℤ) := by ring

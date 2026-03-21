/-
# Spectral Graph Theory
-/
import Mathlib

-- Petersen graph eigenvalues
theorem petersen_eig : (3 : ℤ) + 5 * 1 + 4 * (-2) = 0 := by norm_num

-- Path algebraic connectivity
theorem path_ac : 2 * (1 - (1 : ℚ) / 2) = 1 := by norm_num

-- Binary tree nodes
theorem bin_tree (d : ℕ) : 2 ^ (d + 1) ≥ d + 2 := by
  induction d with
  | zero => simp
  | succ n ih => calc 2 ^ (n + 2) = 2 * 2 ^ (n + 1) := by ring_nf
                   _ ≥ 2 * (n + 2) := by omega
                   _ ≥ n + 3 := by omega

-- Ternary tree (Berggren) nodes
theorem tern_tree (d : ℕ) : 3 ^ (d + 1) ≥ 2 * d + 1 := by
  induction d with
  | zero => simp
  | succ n ih => calc 3 ^ (n + 2) = 3 * 3 ^ (n + 1) := by ring
                   _ ≥ 3 * (2 * n + 1) := by omega
                   _ = 6 * n + 3 := by ring
                   _ ≥ 2 * (n + 1) + 1 := by omega

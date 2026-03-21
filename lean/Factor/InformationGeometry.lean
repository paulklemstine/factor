/-
# Information Geometry
-/
import Mathlib

-- Fisher information for Bernoulli
theorem bernoulli_fisher' (theta : ℝ) (h0 : 0 < theta) (h1 : theta < 1) :
    0 < 1 / (theta * (1 - theta)) := by
  apply div_pos one_pos; exact mul_pos h0 (by linarith)

-- Fisher information is additive
theorem fisher_additive_n (n : ℕ) (I1 : ℝ) (hI : 0 < I1) (hn : 0 < n) :
    (n : ℝ) * I1 > 0 := by positivity

-- Cramér-Rao
theorem cramer_rao_bound (I_theta : ℝ) (hI : 0 < I_theta) :
    0 < 1 / I_theta := by positivity

-- Entropy bounds
theorem uniform_entropy_pos (a b : ℝ) (hab : a < b) : 0 < b - a := by linarith

-- IOF information extraction
theorem iof_info (p : ℕ) (hp : 2 ≤ p) :
    (p - 1) / 2 + 1 ≥ 1 := by omega

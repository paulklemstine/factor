/-
# Numerical Analysis
-/
import Mathlib

-- Newton quadratic convergence
theorem newton_qc (e : ℕ → ℝ) (C : ℝ) (h : ∀ n, e (n + 1) ≤ C * e n ^ 2) :
    e 1 ≤ C * e 0 ^ 2 := h 0

-- Simpson exact for cubics
theorem simpson_cubic :
    (0 + 4 * ((1 : ℚ) / 2) ^ 3 + 1) / 6 = 1 / 4 := by norm_num

-- Euler stability
theorem euler_stab (h_s : ℝ) (lam : ℝ) (hlam : lam < 0)
    (hh : 0 < h_s) (hstab : h_s * (-lam) < 2) :
    |1 + h_s * lam| < 1 := by
  rw [abs_lt]; constructor <;> nlinarith

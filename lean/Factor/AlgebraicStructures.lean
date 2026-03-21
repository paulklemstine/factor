/-
# Algebraic Structures Exploration

Rings, fields, modules, and algebraic structures
with connections to quantum computing and number theory.
-/
import Mathlib

open Polynomial BigOperators

/-! ## §1: Ring Properties -/

/-- Gaussian integer norm is multiplicative (Brahmagupta-Fibonacci). -/
theorem gaussian_norm_mul' (a b c d : ℤ) :
    (a^2 + b^2) * (c^2 + d^2) = (a*c - b*d)^2 + (a*d + b*c)^2 := by ring

/-- ℤ[√-5] norms: showing non-unique factorization of 6. -/
theorem zsqrt_neg5_norms :
    2^2 + 0^2 * 5 = (4 : ℤ) ∧
    3^2 + 0^2 * 5 = (9 : ℤ) ∧
    1^2 + 1^2 * 5 = (6 : ℤ) ∧
    1^2 + 1^2 * 5 = (6 : ℤ) :=
  ⟨by ring, by ring, by ring, by ring⟩

/-! ## §2: Polynomial Ring Properties -/

/-- x² - 1 = (x-1)(x+1) over ℤ. -/
theorem factor_diff_squares :
    (X : ℤ[X])^2 - 1 = (X - 1) * (X + 1) := by ring

/-- x³ - 1 = (x-1)(x²+x+1) over ℤ. -/
theorem factor_cube_minus_one :
    (X : ℤ[X])^3 - 1 = (X - 1) * (X^2 + X + 1) := by ring

/-- x⁴ - 1 = (x-1)(x+1)(x²+1) over ℤ. -/
theorem factor_fourth_power :
    (X : ℤ[X])^4 - 1 = (X - 1) * (X + 1) * (X^2 + 1) := by ring

/-- Cyclotomic factorization of x⁶ - 1. -/
theorem cyclotomic_6_divides :
    (X : ℤ[X])^6 - 1 = (X - 1) * (X + 1) * (X^2 + X + 1) * (X^2 - X + 1) := by ring

/-! ## §3: Field Extensions -/

/-- √2 is irrational. -/
theorem sqrt2_irrational' : Irrational (Real.sqrt 2) :=
  irrational_sqrt_two

/-
PROBLEM
√3 is irrational.

PROVIDED SOLUTION
Use Nat.Prime.irrational_sqrt (by norm_num : Nat.Prime 3) from Mathlib.
-/
theorem sqrt3_irrational : Irrational (Real.sqrt 3) := by
  exact Nat.prime_three.irrational_sqrt

/-! ## §4: Quaternion Algebra -/

/-- The quaternion norm is multiplicative (Euler four-square identity). -/
theorem quaternion_norm_mul' (a b c d e f g h : ℤ) :
    (a^2 + b^2 + c^2 + d^2) * (e^2 + f^2 + g^2 + h^2) =
    (a*e - b*f - c*g - d*h)^2 + (a*f + b*e + c*h - d*g)^2 +
    (a*g - b*h + c*e + d*f)^2 + (a*h + b*g - c*f + d*e)^2 := by ring

/-! ## §5: Lie Algebra of sl(2) -/

def sl2_e' : Matrix (Fin 2) (Fin 2) ℤ := !![0, 1; 0, 0]
def sl2_f' : Matrix (Fin 2) (Fin 2) ℤ := !![0, 0; 1, 0]
def sl2_h' : Matrix (Fin 2) (Fin 2) ℤ := !![1, 0; 0, -1]

/-- [e, f] = h -/
theorem sl2_bracket_ef' : sl2_e' * sl2_f' - sl2_f' * sl2_e' = sl2_h' := by
  ext i j; fin_cases i <;> fin_cases j <;>
    simp [sl2_e', sl2_f', sl2_h', Matrix.mul_apply, Fin.sum_univ_two]

/-- [h, e] = 2e -/
theorem sl2_bracket_he' : sl2_h' * sl2_e' - sl2_e' * sl2_h' = 2 • sl2_e' := by
  ext i j; fin_cases i <;> fin_cases j <;>
    simp [sl2_e', sl2_h', Matrix.mul_apply, Matrix.smul_apply, Fin.sum_univ_two]

/-- [h, f] = -2f -/
theorem sl2_bracket_hf' : sl2_h' * sl2_f' - sl2_f' * sl2_h' = -(2 • sl2_f') := by
  ext i j; fin_cases i <;> fin_cases j <;>
    simp [sl2_f', sl2_h', Matrix.mul_apply, Matrix.smul_apply, Matrix.neg_apply,
          Fin.sum_univ_two]

/-- Trace of sl(2) elements is 0. -/
theorem sl2_trace_e' : Matrix.trace sl2_e' = 0 := by
  simp [sl2_e', Matrix.trace, Matrix.diag, Fin.sum_univ_two]

theorem sl2_trace_f' : Matrix.trace sl2_f' = 0 := by
  simp [sl2_f', Matrix.trace, Matrix.diag, Fin.sum_univ_two]

theorem sl2_trace_h' : Matrix.trace sl2_h' = 0 := by
  simp [sl2_h', Matrix.trace, Matrix.diag, Fin.sum_univ_two]
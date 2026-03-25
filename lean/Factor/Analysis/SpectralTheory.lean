/-
# Spectral Theory of Berggren Cayley Graphs

The Cayley graph of ⟨M₁, M₃⟩ in SL(2,𝔽_p) is a candidate family
of Ramanujan graphs.
-/
import Mathlib

open Matrix

/-! ## Generators in SL(2,𝔽_p) -/

/-- M₁ mod p has determinant 1. -/
theorem M₁_det_mod (p : ℕ) :
    Matrix.det (!![((2 : ℤ) : ZMod p), ((-1 : ℤ) : ZMod p);
                    ((1 : ℤ) : ZMod p), ((0 : ℤ) : ZMod p)]) = 1 := by
  simp [Matrix.det_fin_two]

/-- M₃ mod p has determinant 1. -/
theorem M₃_det_mod (p : ℕ) :
    Matrix.det (!![((1 : ℤ) : ZMod p), ((2 : ℤ) : ZMod p);
                    ((0 : ℤ) : ZMod p), ((1 : ℤ) : ZMod p)]) = 1 := by
  simp [Matrix.det_fin_two]

/-! ## Graph Regularity -/

theorem M₁_ne_inv : !![( 2 : ℤ), -1; 1, 0] ≠ !![( 0 : ℤ), 1; -1, 2] := by
  intro h; have := congr_fun (congr_fun h 0) 0; simp at this

theorem M₃_ne_inv : !![( 1 : ℤ), 2; 0, 1] ≠ !![( 1 : ℤ), -2; 0, 1] := by
  intro h; have := congr_fun (congr_fun h 0) 1; simp at this

/-! ## Ramanujan Bound -/

/-
PROBLEM
The Ramanujan bound for 4-regular graphs: 2√3 < 4.

PROVIDED SOLUTION
We need 2*sqrt(3) < 4, i.e., sqrt(3) < 2. Since 3 < 4 = 2², and sqrt is monotone, sqrt(3) < sqrt(4) = 2. Use Real.sqrt_lt_sqrt or show (2*sqrt(3))^2 = 12 < 16 = 4^2 and both sides positive.
-/
theorem ramanujan_bound_lt_degree : 2 * Real.sqrt 3 < 4 := by
  nlinarith [ Real.sq_sqrt ( show 0 ≤ 3 by norm_num ) ]

/-- The Ramanujan spectral gap for 4-regular graphs is positive. -/
theorem ramanujan_gap_pos : (4 : ℝ) - 2 * Real.sqrt 3 > 0 := by
  linarith [ramanujan_bound_lt_degree]

/-! ## Matrix Computations -/

theorem M₃_squared :
    !![( 1 : ℤ), 2; 0, 1] * !![( 1 : ℤ), 2; 0, 1] = !![( 1 : ℤ), 4; 0, 1] := by
  ext i j; fin_cases i <;> fin_cases j <;>
    simp [Matrix.mul_apply, Fin.sum_univ_two]

theorem M₁_squared :
    !![( 2 : ℤ), -1; 1, 0] * !![( 2 : ℤ), -1; 1, 0] = !![( 3 : ℤ), -2; 2, -1] := by
  ext i j; fin_cases i <;> fin_cases j <;>
    simp [Matrix.mul_apply, Fin.sum_univ_two]
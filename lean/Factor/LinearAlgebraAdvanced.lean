/-
# Advanced Linear Algebra
-/
import Mathlib

open Matrix BigOperators Finset

/-! ## §1: Determinant Properties -/

theorem det_mul_2x2 (A B : Matrix (Fin 2) (Fin 2) ℤ) :
    Matrix.det (A * B) = Matrix.det A * Matrix.det B :=
  Matrix.det_mul A B

theorem det_transpose_2x2 (A : Matrix (Fin 2) (Fin 2) ℤ) :
    Matrix.det A.transpose = Matrix.det A :=
  Matrix.det_transpose A

/-! ## §2: Trace Properties -/

theorem trace_add_2x2 (A B : Matrix (Fin 2) (Fin 2) ℤ) :
    Matrix.trace (A + B) = Matrix.trace A + Matrix.trace B :=
  Matrix.trace_add A B

/-! ## §3: Special Matrices -/

theorem rotation_det_345 :
    Matrix.det !![( 3 : ℚ)/5, -(4 : ℚ)/5; (4 : ℚ)/5, (3 : ℚ)/5] = 1 := by
  simp [Matrix.det_fin_two]; ring

theorem rotation_preserves_norm_345 (x y : ℚ) :
    ((3 * x - 4 * y) / 5) ^ 2 + ((4 * x + 3 * y) / 5) ^ 2 = x ^ 2 + y ^ 2 := by ring

/-! ## §4: Nilpotent and Idempotent -/

def nilpotent_2x2 : Matrix (Fin 2) (Fin 2) ℤ := !![0, 1; 0, 0]

theorem nilpotent_squared : nilpotent_2x2 * nilpotent_2x2 = 0 := by
  ext i j; fin_cases i <;> fin_cases j <;>
    simp [nilpotent_2x2, Matrix.mul_apply, Fin.sum_univ_two]

def proj_2x2 : Matrix (Fin 2) (Fin 2) ℤ := !![1, 0; 0, 0]

theorem proj_idempotent : proj_2x2 * proj_2x2 = proj_2x2 := by
  ext i j; fin_cases i <;> fin_cases j <;>
    simp [proj_2x2, Matrix.mul_apply, Fin.sum_univ_two]

/-! ## §5: Eigenvalues -/

theorem berggren_M1_eigenvalue' : (1 : ℤ) ^ 2 - 2 * 1 + 1 = 0 := by ring
theorem rotation_char_poly_eval : (0 : ℤ) ^ 2 + 1 ≠ 0 := by norm_num

/-! ## §6: Self-inverse -/

theorem pauli_x_self_inverse :
    !![( 0 : ℤ), 1; 1, 0] * !![( 0 : ℤ), 1; 1, 0] = 1 := by
  ext i j; fin_cases i <;> fin_cases j <;>
    simp [Matrix.mul_apply, Fin.sum_univ_two, Matrix.one_apply] <;> rfl

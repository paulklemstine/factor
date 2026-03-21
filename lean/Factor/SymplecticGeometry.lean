/-
# Symplectic Geometry
-/
import Mathlib

open Matrix

def symp_J : Matrix (Fin 2) (Fin 2) ℤ := !![0, 1; -1, 0]

theorem symp_J_sq : symp_J * symp_J = -1 := by
  ext i j; fin_cases i <;> fin_cases j <;> simp [symp_J, mul_apply, Fin.sum_univ_two]

theorem symp_J_det : symp_J.det = 1 := by simp [symp_J, det_fin_two]

theorem symp_product (A B : Matrix (Fin 2) (Fin 2) ℤ)
    (hA : A.det = 1) (hB : B.det = 1) :
    (A * B).det = 1 := by rw [det_mul, hA, hB, mul_one]

def mod_S : Matrix (Fin 2) (Fin 2) ℤ := !![0, -1; 1, 0]
def mod_T : Matrix (Fin 2) (Fin 2) ℤ := !![1, 1; 0, 1]

theorem mod_S_det : mod_S.det = 1 := by simp [mod_S, det_fin_two]
theorem mod_T_det : mod_T.det = 1 := by simp [mod_T, det_fin_two]

theorem mod_S_sq : mod_S * mod_S = -1 := by
  ext i j; fin_cases i <;> fin_cases j <;> simp [mod_S, mul_apply, Fin.sum_univ_two]

theorem mod_S_ord4 : mod_S * mod_S * mod_S * mod_S = 1 := by
  ext i j; fin_cases i <;> fin_cases j <;>
    simp [mod_S, mul_apply, Fin.sum_univ_two]

theorem mod_ST_cubed :
    let ST := mod_S * mod_T
    ST * ST * ST = -1 := by
  simp only []
  ext i j; fin_cases i <;> fin_cases j <;>
    simp [mod_S, mod_T, mul_apply, Fin.sum_univ_two]

theorem liouville_2d_thm (A : Matrix (Fin 2) (Fin 2) ℝ) (hA : A.det = 1) :
    |A.det| = 1 := by rw [hA]; simp

-- Berggren B₁ has det 1, B₂ has det -1, B₃ has det 1
theorem berg_B1 :
    (!![1, -2, 2; 2, -1, 2; 2, -2, 3] : Matrix (Fin 3) (Fin 3) ℤ).det = 1 := by
  native_decide

theorem berg_B2 :
    (!![1, 2, 2; 2, 1, 2; 2, 2, 3] : Matrix (Fin 3) (Fin 3) ℤ).det = -1 := by
  native_decide

theorem berg_B3 :
    (!![-1, 2, 2; -2, 1, 2; -2, 2, 3] : Matrix (Fin 3) (Fin 3) ℤ).det = 1 := by
  native_decide

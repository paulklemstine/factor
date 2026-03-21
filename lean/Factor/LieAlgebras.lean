/-
# Lie Algebras
-/

import Mathlib

open Matrix

def lieBracket2 {R : Type*} [CommRing R]
    (A B : Matrix (Fin 2) (Fin 2) R) : Matrix (Fin 2) (Fin 2) R :=
  A * B - B * A

theorem lie_antisymm' {R : Type*} [CommRing R]
    (A B : Matrix (Fin 2) (Fin 2) R) :
    lieBracket2 A B = -lieBracket2 B A := by
  ext i j; simp [lieBracket2, Matrix.sub_apply, Matrix.neg_apply, Matrix.mul_apply]

theorem lie_self_zero' {R : Type*} [CommRing R]
    (A : Matrix (Fin 2) (Fin 2) R) :
    lieBracket2 A A = 0 := by
  ext i j; simp [lieBracket2, Matrix.sub_apply, Matrix.zero_apply, Matrix.mul_apply]

theorem jacobi_identity' {R : Type*} [CommRing R]
    (A B C : Matrix (Fin 2) (Fin 2) R) :
    lieBracket2 A (lieBracket2 B C) + lieBracket2 B (lieBracket2 C A) +
    lieBracket2 C (lieBracket2 A B) = 0 := by
  ext i j; simp [lieBracket2, Matrix.sub_apply, Matrix.add_apply,
    Matrix.zero_apply, Matrix.mul_apply, Fin.sum_univ_two]; ring

theorem trace_lie_zero' {R : Type*} [CommRing R]
    (A B : Matrix (Fin 2) (Fin 2) R) :
    Matrix.trace (lieBracket2 A B) = 0 := by
  unfold lieBracket2; rw [Matrix.trace_sub, Matrix.trace_mul_comm]; ring

def sl2_e' : Matrix (Fin 2) (Fin 2) ℤ := !![0, 1; 0, 0]
def sl2_f' : Matrix (Fin 2) (Fin 2) ℤ := !![0, 0; 1, 0]
def sl2_h' : Matrix (Fin 2) (Fin 2) ℤ := !![1, 0; 0, -1]

theorem sl2_ef' : lieBracket2 sl2_e' sl2_f' = sl2_h' := by
  ext i j; fin_cases i <;> fin_cases j <;>
    simp [lieBracket2, sl2_e', sl2_f', sl2_h', Matrix.mul_apply, Fin.sum_univ_two]

theorem sl2_he' : lieBracket2 sl2_h' sl2_e' = 2 • sl2_e' := by
  ext i j; fin_cases i <;> fin_cases j <;>
    simp [lieBracket2, sl2_h', sl2_e', Matrix.mul_apply, Fin.sum_univ_two, Matrix.smul_apply]

theorem sl2_traceless' : Matrix.trace sl2_e' = 0 ∧ Matrix.trace sl2_f' = 0 ∧
    Matrix.trace sl2_h' = 0 := by
  refine ⟨?_, ?_, ?_⟩ <;> simp [sl2_e', sl2_f', sl2_h', Matrix.trace, Fin.sum_univ_two]

theorem upper_triangular_nilpotent' : sl2_e' * sl2_e' = 0 := by
  ext i j; fin_cases i <;> fin_cases j <;>
    simp [sl2_e', Matrix.mul_apply, Fin.sum_univ_two]

theorem sl2_not_abelian' : lieBracket2 sl2_e' sl2_f' ≠ 0 := by
  rw [sl2_ef']; intro h
  have := congr_fun (congr_fun h 0) 0
  simp [sl2_h'] at this

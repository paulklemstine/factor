import Mathlib

/-!
# Linear Algebra Exploration

Deep explorations including:
- Determinant properties and identities
- Eigenvalue theory
- Matrix decompositions
- Trace identities
- Rank-nullity connections
- Special matrices (orthogonal, symmetric, nilpotent)
-/

open Matrix Finset BigOperators

section DeterminantProperties

/-
det(AB) = det(A) * det(B)
-/
theorem det_mul_comm (n : ℕ) (A B : Matrix (Fin n) (Fin n) ℤ) :
    Matrix.det (A * B) = Matrix.det A * Matrix.det B := by
  exact Matrix.det_mul A B

/-
det(A^T) = det(A)
-/
theorem det_transpose' (n : ℕ) (A : Matrix (Fin n) (Fin n) ℤ) :
    Matrix.det Aᵀ = Matrix.det A := by
  rw [ Matrix.det_transpose ]

/-
det(cA) = c^n * det(A) for n×n matrix
-/
theorem det_smul' (n : ℕ) (c : ℤ) (A : Matrix (Fin n) (Fin n) ℤ) :
    Matrix.det (c • A) = c ^ Fintype.card (Fin n) * Matrix.det A := by
  rw [ Matrix.det_smul, mul_comm ]

/-
det(I) = 1
-/
theorem det_one' (n : ℕ) : Matrix.det (1 : Matrix (Fin n) (Fin n) ℤ) = 1 := by
  convert Matrix.det_one

/-
Determinant of a 2x2 matrix
-/
theorem det_2x2 (a b c d : ℤ) :
    Matrix.det !![a, b; c, d] = a * d - b * c := by
  bound

/-
Determinant of a diagonal 2x2 matrix
-/
theorem det_diag_2x2 (a d : ℤ) :
    Matrix.det !![a, 0; 0, d] = a * d := by
  simp +decide [ Matrix.det_fin_two ]

end DeterminantProperties

section TraceProperties

/-
tr(A + B) = tr(A) + tr(B)
-/
theorem trace_add' (n : ℕ) (A B : Matrix (Fin n) (Fin n) ℤ) :
    Matrix.trace (A + B) = Matrix.trace A + Matrix.trace B := by
  exact Matrix.trace_add A B

/-
tr(cA) = c * tr(A)
-/
theorem trace_smul' (n : ℕ) (c : ℤ) (A : Matrix (Fin n) (Fin n) ℤ) :
    Matrix.trace (c • A) = c * Matrix.trace A := by
  simp +decide [ Matrix.trace, Finset.mul_sum _ _ _, Matrix.smul_eq_diagonal_mul ]

/-
tr(AB) = tr(BA) (trace cyclicity)
-/
theorem trace_mul_comm' (n : ℕ) (A B : Matrix (Fin n) (Fin n) ℤ) :
    Matrix.trace (A * B) = Matrix.trace (B * A) := by
  rw [ Matrix.trace_mul_comm ]

/-
tr(I_n) = n
-/
theorem trace_one' (n : ℕ) :
    Matrix.trace (1 : Matrix (Fin n) (Fin n) ℤ) = (n : ℤ) := by
  simp +decide [ Matrix.trace ]

end TraceProperties

section SpecialMatrices

/-- A nilpotent 2x2 matrix: [[0,1],[0,0]]^2 = 0 -/
def nilpotent_2x2 : Matrix (Fin 2) (Fin 2) ℤ := !![0, 1; 0, 0]

theorem nilpotent_2x2_sq : nilpotent_2x2 * nilpotent_2x2 = 0 := by
  -- By definition of matrix multiplication, we can compute each element of the product.
  ext i j; fin_cases i <;> fin_cases j <;> norm_num [ nilpotent_2x2 ]

theorem nilpotent_2x2_trace : Matrix.trace nilpotent_2x2 = 0 := by
  -- The trace of a matrix is the sum of its diagonal elements.
  simp [nilpotent_2x2, Matrix.trace]

theorem nilpotent_2x2_det : Matrix.det nilpotent_2x2 = 0 := by
  -- The determinant of the nilpotent matrix is calculated as follows:
  simp [nilpotent_2x2, Matrix.det_fin_two]

/-- The rotation matrix R(90°) over ℤ: [[0,-1],[1,0]] -/
def rotation_90 : Matrix (Fin 2) (Fin 2) ℤ := !![0, -1; 1, 0]

theorem rotation_90_det : Matrix.det rotation_90 = 1 := by
  -- Calculate the determinant using the formula for a 2x2 matrix.
  simp [rotation_90, Matrix.det_fin_two]

theorem rotation_90_sq : rotation_90 * rotation_90 = -1 := by
  -- Let's compute the product of the rotation matrix with itself.
  ext i j; fin_cases i <;> fin_cases j <;> norm_num [rotation_90]

theorem rotation_90_fourth : rotation_90 * rotation_90 * rotation_90 * rotation_90 = 1 := by
  -- Let's compute the product of the rotation matrix with itself four times.
  simp +decide [rotation_90]

/-- Projection matrix: P² = P for P = [[1,0],[0,0]] -/
def proj_2x2 : Matrix (Fin 2) (Fin 2) ℤ := !![1, 0; 0, 0]

theorem proj_idempotent : proj_2x2 * proj_2x2 = proj_2x2 := by
  -- By definition of matrix multiplication, we can compute each element of the product.
  ext i j; fin_cases i <;> fin_cases j <;> norm_num [proj_2x2]

theorem proj_trace : Matrix.trace proj_2x2 = 1 := by
  -- The trace of a matrix is the sum of its diagonal elements. For the projection matrix proj_2x2, the diagonal elements are 1 and 0.
  simp [proj_2x2, Matrix.trace]

theorem proj_det : Matrix.det proj_2x2 = 0 := by
  native_decide +revert

end SpecialMatrices

section MatrixEquations

/-
Cayley-Hamilton for 2x2 over ℤ (general form)
-/
theorem cayley_hamilton_2x2' (A : Matrix (Fin 2) (Fin 2) ℤ) :
    A * A - Matrix.trace A • A + Matrix.det A • (1 : Matrix (Fin 2) (Fin 2) ℤ) = 0 := by
  rw [ Matrix.det_fin_two, Matrix.trace_fin_two ];
  ext i j ; fin_cases i <;> fin_cases j <;> simpa [ Matrix.mul_apply, Matrix.smul_eq_diagonal_mul ] using by ring;

/-
For an involution (A² = I), the eigenvalues are ±1, hence det = ±1
-/
theorem involution_det (A : Matrix (Fin 2) (Fin 2) ℤ) (hA : A * A = 1) :
    Matrix.det A = 1 ∨ Matrix.det A = -1 := by
  exact Int.eq_one_or_neg_one_of_mul_eq_one <| by simpa using congr_arg Matrix.det hA;

/-
If A² = -I (complex structure), then det A = 1
-/
theorem complex_structure_det (A : Matrix (Fin 2) (Fin 2) ℤ) (hA : A * A = -1) :
    Matrix.det A = 1 := by
  rw [ ← Matrix.ext_iff ] at hA;
  norm_num [ Fin.forall_fin_two, Matrix.mul_apply ] at hA;
  cases le_or_gt 0 ( A 0 1 ) <;> cases le_or_gt 0 ( A 1 0 ) <;> nlinarith [ Matrix.det_fin_two A ]

end MatrixEquations

section Kronecker

/-
Kronecker delta: δ_{ii} = 1
-/
theorem kronecker_diag {n : ℕ} (i : Fin n) :
    (1 : Matrix (Fin n) (Fin n) ℤ) i i = 1 := by
  exact?

/-
Kronecker off-diagonal: δ_{ij} = 0 for i ≠ j
-/
theorem kronecker_off_diag {n : ℕ} (i j : Fin n) (hij : i ≠ j) :
    (1 : Matrix (Fin n) (Fin n) ℤ) i j = 0 := by
  -- Since $i \neq j$, the entry at $(i, j)$ in the identity matrix is $0$.
  simp [Matrix.one_apply, hij]

end Kronecker
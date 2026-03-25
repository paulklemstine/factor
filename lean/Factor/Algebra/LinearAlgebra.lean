/-
# Linear Algebra: Matrices, Determinants, and Quantum Gates

Foundations for Berggren matrices, quantum gate decomposition, and IMU systems.
-/

import Mathlib

/-! ## Section 1: Determinant Properties -/

/-
PROBLEM
The determinant of a product is the product of determinants.

PROVIDED SOLUTION
Use Matrix.det_mul.
-/
theorem det_mul_eq {n : Type*} [DecidableEq n] [Fintype n]
    (A B : Matrix n n ℝ) :
    (A * B).det = A.det * B.det := by
      exact Matrix.det_mul A B

/-
PROBLEM
The determinant of the identity is 1.

PROVIDED SOLUTION
Use Matrix.det_one.
-/
theorem det_one_pf {n : Type*} [DecidableEq n] [Fintype n] :
    (1 : Matrix n n ℝ).det = 1 := by
      convert Matrix.det_one

/-
PROBLEM
The determinant of the transpose equals the determinant.

PROVIDED SOLUTION
Use Matrix.det_transpose.
-/
theorem det_transpose_pf {n : Type*} [DecidableEq n] [Fintype n]
    (A : Matrix n n ℝ) :
    A.transpose.det = A.det := by
      exact?

/-! ## Section 2: Trace and Skew-Symmetry -/

/-
PROBLEM
The trace of a skew-symmetric matrix is 0.

PROVIDED SOLUTION
Since Aᵀ = -A, we have A i i = -A i i for all i. So 2 * A i i = 0, hence A i i = 0. The trace is the sum of diagonal entries, all zero.
-/
theorem skew_symmetric_trace_zero {n : Type*} [DecidableEq n] [Fintype n]
    (A : Matrix n n ℝ) (hA : A.transpose = -A) :
    A.trace = 0 := by
      rw [ ← Matrix.ext_iff ] at hA;
      exact Finset.sum_eq_zero fun i _ => by have := hA i i; norm_num at *; linarith;

/-
PROBLEM
Orthogonal matrices have determinant ±1.

PROVIDED SOLUTION
From A * Aᵀ = I, det(A) * det(Aᵀ) = 1, so det(A)² = 1, hence det(A) = ±1. Use det_mul, det_transpose, sq_eq_one_iff_of_ne_neg_one or mul_self_eq_one.
-/
theorem orthogonal_det {n : Type*} [DecidableEq n] [Fintype n]
    (A : Matrix n n ℝ) (hA : A * A.transpose = 1) :
    A.det = 1 ∨ A.det = -1 := by
      exact mul_self_eq_one_iff.mp ( by simpa [ Matrix.det_transpose ] using congr_arg Matrix.det hA )
/-
# Quantum Computing Foundations: Hilbert Spaces and Unitaries

Mathematical foundations for quantum gate synthesis.
-/

import Mathlib

/-! ## Section 1: Norm Properties -/

/-
PROBLEM
The triangle inequality for norms.

PROVIDED SOLUTION
Use norm_add_le.
-/
theorem norm_triangle_pf {V : Type*} [SeminormedAddCommGroup V] (x y : V) :
    ‖x + y‖ ≤ ‖x‖ + ‖y‖ := by
      exact norm_add_le x y

/-
PROBLEM
Cauchy-Schwarz for inner product spaces (real case).

PROVIDED SOLUTION
Use real_inner_le_norm.
-/
theorem inner_mul_le_norm_pf {V : Type*} [SeminormedAddCommGroup V] [InnerProductSpace ℝ V] (x y : V) :
    @inner ℝ V _ x y ≤ ‖x‖ * ‖y‖ := by
      exact?

/-! ## Section 2: Unitary Matrix Properties -/

/-
PROBLEM
The product of unitary matrices is unitary.

PROVIDED SOLUTION
star(U*V) = star V * star U. So (UV)(UV)* = UV(star V)(star U) = U(V star V)(star U) = U*1*star U = U star U = 1. Use star_mul, mul_assoc, hV, hU.
-/
theorem unitary_mul_unitary {n : Type*} [DecidableEq n] [Fintype n]
    (U V : Matrix n n ℂ) (hU : U * star U = 1) (hV : V * star V = 1) :
    (U * V) * star (U * V) = 1 := by
      simp +decide [ ← mul_assoc, hU, hV ];
      simp +decide [ mul_assoc, hU, hV ]

/-
PROBLEM
The inverse of a unitary matrix is its conjugate transpose.

PROVIDED SOLUTION
From U * star U = 1, U is invertible with inverse star U. Then star U * U = 1 by the uniqueness of inverses. Use mul_right_eq_of_eq_mul or Matrix.nonsing_inv properties.
-/
theorem unitary_inv_eq_star {n : Type*} [DecidableEq n] [Fintype n]
    (U : Matrix n n ℂ) (hU : U * star U = 1) :
    star U * U = 1 := by
      rw [ ← mul_eq_one_comm, hU ]

/-! ## Section 3: Quantum State Properties -/

/-
PROBLEM
The tensor product of normalized states is normalized.

PROVIDED SOLUTION
normSq is multiplicative: normSq(xy) = normSq(x)*normSq(y). So the sum is normSq(a)*(normSq(c)+normSq(d)) + normSq(b)*(normSq(c)+normSq(d)) = (normSq(a)+normSq(b))*(normSq(c)+normSq(d)) = 1*1 = 1. Use map_mul and h1, h2.
-/
theorem tensor_normalized (a b c d : ℂ)
    (h1 : Complex.normSq a + Complex.normSq b = 1)
    (h2 : Complex.normSq c + Complex.normSq d = 1) :
    Complex.normSq (a * c) + Complex.normSq (a * d) +
    Complex.normSq (b * c) + Complex.normSq (b * d) = 1 := by
      simpa [ Complex.normSq_mul ] using by linear_combination' h1 * h2;

/-
PROBLEM
The Pauli X gate is its own inverse.

PROVIDED SOLUTION
Direct matrix computation: X² = I. Use ext, fin_cases, simp.
-/
theorem pauli_x_squared :
    (!![(0:ℂ), 1; 1, 0] : Matrix (Fin 2) (Fin 2) ℂ) *
    (!![(0:ℂ), 1; 1, 0] : Matrix (Fin 2) (Fin 2) ℂ) = 1 := by
      ext i j ; fin_cases i <;> fin_cases j <;> norm_num
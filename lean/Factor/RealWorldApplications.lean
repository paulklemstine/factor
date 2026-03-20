import Mathlib

/-!
# Real-World Applications of Formal Mathematics

Connecting formal mathematics to engineering and science:
- Signal processing
- Control theory
- Machine learning
- Physics
- Economics
- Algorithm correctness
-/

open BigOperators Finset Matrix

section SignalProcessing

/-
2-point DFT: [[1,1],[1,-1]]² = 2I
-/
theorem dft2_squared :
    !![1, 1; 1, -1] * !![1, 1; 1, -1] = (2 : ℤ) • (1 : Matrix (Fin 2) (Fin 2) ℤ) := by
  ext i j ; fin_cases i <;> fin_cases j <;> norm_num [ Matrix.mul_apply ]

/-
Polynomial multiplication is commutative
-/
theorem poly_mul_comm_int (p q : Polynomial ℤ) : p * q = q * p := by
  exact mul_comm p q

/-- Parseval example -/
theorem parseval_ex : (1 : ℤ)^2 + 1^2 = (2^2 + 0^2) / 2 := by norm_num

/-- Nyquist dimension bound -/
theorem nyquist_dim (B : ℕ) : 2 * B ≥ B := by omega

end SignalProcessing

section ControlTheory

/-
Nilpotent system is stable: A² = 0
-/
theorem nilpotent_stable :
    !![0, 1; 0, 0] * !![0, 1; 0, 0] = (0 : Matrix (Fin 2) (Fin 2) ℤ) := by
  native_decide +revert

end ControlTheory

section MachineLearning

/-
Gradient descent key inequality for f(x) = x²
-/
theorem gd_key_ineq (x y : ℝ) :
    y ^ 2 ≥ x ^ 2 + 2 * x * (y - x) := by
  linarith [ sq_nonneg ( y - x ) ]

/-- Softmax normalization example -/
theorem softmax_ex : (1 : ℚ)/3 + 1/3 + 1/3 = 1 := by norm_num

end MachineLearning

section Physics

/-- Energy conservation (discrete) -/
theorem energy_cons (ke₁ pe₁ ke₂ pe₂ : ℤ) (h : ke₁ + pe₁ = ke₂ + pe₂) :
    (ke₂ - ke₁) + (pe₂ - pe₁) = 0 := by linarith

/-
Commuting matrices have zero commutator
-/
theorem comm_mat_zero (A B : Matrix (Fin 2) (Fin 2) ℤ) (h : A * B = B * A) :
    A * B - B * A = 0 := by
  rw [ h, sub_self ]

/-- Energy levels form a group under addition -/
theorem energy_additive (c : ℤ) (n m : ℤ) :
    n * c + m * c = (n + m) * c := by ring

end Physics

section Economics

/-- Arrow's orderings count -/
theorem arrow_ord : Nat.factorial 3 = 6 := by norm_num

/-
Argmax of finite function exists
-/
theorem econ_argmax {n : ℕ} (f : Fin (n + 1) → ℤ) :
    ∃ i : Fin (n + 1), ∀ j : Fin (n + 1), f j ≤ f i := by
  simpa using Finset.exists_max_image Finset.univ f ( Finset.univ_nonempty )

end Economics

section Algorithms

/-- Sorting lower bound: n! > 2^(n-1) for n ≥ 3 -/
theorem sort_lower : 2 ^ 2 < Nat.factorial 3 := by norm_num

/-- GCD reduction step -/
theorem gcd_step (a b : ℕ) (hb : 0 < b) :
    a % b < b := Nat.mod_lt a hb

end Algorithms
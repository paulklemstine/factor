/-
# Optimization Theory

Convexity, linear programming duality, and connections
to quantum circuit optimization.
-/
import Mathlib

open BigOperators Finset

/-! ## §1: Convexity -/

/-
PROBLEM
x² is convex: t*a² + (1-t)*b² ≥ (t*a + (1-t)*b)².

PROVIDED SOLUTION
nlinarith with sq_nonneg (a - b) and sq_nonneg t and sq_nonneg (1 - t). The key identity is t*a² + (1-t)*b² - (t*a + (1-t)*b)² = t*(1-t)*(a-b)² ≥ 0.
-/
theorem sq_convex (a b : ℝ) (t : ℝ) (ht0 : 0 ≤ t) (ht1 : t ≤ 1) :
    (t * a + (1 - t) * b) ^ 2 ≤ t * a ^ 2 + (1 - t) * b ^ 2 := by
  nlinarith [ sq_nonneg ( a - b ), mul_nonneg ht0 ( sub_nonneg_of_le ht1 ) ] ;

/-
PROBLEM
Jensen's inequality for x² (finite version): (E[X])² ≤ E[X²].

PROVIDED SOLUTION
Use Finset.inner_mul_le_norm_mul_sq or Cauchy-Schwarz. Alternatively, for the finite version: ∑ xᵢ² / n ≥ (∑ xᵢ / n)² is equivalent to n * ∑ xᵢ² ≥ (∑ xᵢ)² which is Cauchy-Schwarz with b = 1.
-/
theorem jensen_sq (n : ℕ) (hn : 0 < n) (x : Fin n → ℝ) :
    ((∑ i, x i) / n) ^ 2 ≤ (∑ i, (x i) ^ 2) / n := by
  -- Applying the Cauchy-Schwarz inequality in its generalized form for sequences in Euclidean space.
  have h_cauchy_schwarz : ∀ (u v : Fin n → ℝ), (∑ i, u i * v i) ^ 2 ≤ (∑ i, u i ^ 2) * (∑ i, v i ^ 2) := by
    exact?;
  have := h_cauchy_schwarz ( fun _ => 1 ) x; simp_all +decide [ div_pow, mul_comm, mul_assoc, mul_left_comm, hn.ne' ] ;
  rw [ div_le_div_iff₀ ] <;> first | positivity | nlinarith;

/-! ## §2: Gate Count Lower Bound -/

/-- 2^n ≤ 4^n (gate count lower bound for n qubits). -/
theorem gate_count_lower_bound (n : ℕ) : 2 ^ n ≤ 4 ^ n :=
  Nat.pow_le_pow_left (by norm_num : 2 ≤ 4) n

/-! ## §3: Trace Linearity -/

/-- The trace is linear on matrices. -/
theorem trace_linear_2x2 (A B : Matrix (Fin 2) (Fin 2) ℝ) (c : ℝ) :
    Matrix.trace (c • A + B) = c * Matrix.trace A + Matrix.trace B := by
  simp [Matrix.trace_add, Matrix.trace_smul, smul_eq_mul]

/-! ## §4: Gradient Descent -/

/-- For f(x) = x²/2, one step of GD with step size 1 from x gives 0. -/
theorem gd_quadratic_one_step (x : ℝ) :
    x - 1 * x = (0 : ℝ) := by ring
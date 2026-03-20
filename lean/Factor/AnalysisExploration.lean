/-
# Analysis Exploration

Real analysis, inequalities, sequences, and series.
Connections to the project's compression theory and spectral bounds.
-/
import Mathlib

open BigOperators Finset Real

/-! ## §1: Classical Inequalities -/

/-
PROBLEM
AM-GM inequality for two non-negative reals.

PROVIDED SOLUTION
Use Real.add_sq_le_sq_add_sq or show (√a - √b)² ≥ 0 implies √(ab) ≤ (a+b)/2. Mathlib might have this directly.
-/
theorem am_gm_two (a b : ℝ) (ha : 0 ≤ a) (hb : 0 ≤ b) :
    Real.sqrt (a * b) ≤ (a + b) / 2 := by
  rw [ Real.sqrt_le_left ] <;> linarith [ sq_nonneg ( a - b ) ]

/-
PROBLEM
Cauchy-Schwarz for finite sums.

PROVIDED SOLUTION
Use Finset.inner_mul_le_norm_mul_sq from Mathlib, or inner_mul_le_norm_mul_sq applied to the EuclideanDomain structure on Fin n → ℝ.
-/
theorem cauchy_schwarz_finset' {n : ℕ} (a b : Fin n → ℝ) :
    (∑ i, a i * b i) ^ 2 ≤ (∑ i, a i ^ 2) * (∑ i, b i ^ 2) := by
  exact?

/-
PROBLEM
Power mean inequality: geometric ≤ arithmetic for two terms.

PROVIDED SOLUTION
nlinarith with sq_nonneg (x - y).
-/
theorem power_mean_two (x y : ℝ) (hx : 0 < x) (hy : 0 < y) :
    x * y ≤ ((x + y) / 2) ^ 2 := by
  linarith [ sq_nonneg ( x - y ) ]

/-! ## §2: Sequences and Convergence -/

/-
PROBLEM
The sequence 1/n → 0.

PROVIDED SOLUTION
Use tendsto_one_div_add_atTop_nhds_zero_nat or similar from Mathlib.
-/
theorem inv_n_tendsto : Filter.Tendsto (fun n : ℕ => (1 : ℝ) / (n + 1)) Filter.atTop (nhds 0) := by
  exact tendsto_one_div_add_atTop_nhds_zero_nat

/-
PROBLEM
Geometric series sum for r ≠ 1.

PROVIDED SOLUTION
Use geom_sum_eq from Mathlib.
-/
theorem geometric_sum_formula (r : ℝ) (hr : r ≠ 1) (n : ℕ) :
    ∑ k ∈ Finset.range n, r ^ k = (1 - r ^ n) / (1 - r) := by
  rw [ ← neg_div_neg_eq, geom_sum_eq ] <;> aesop

/-! ## §3: Series -/

/-
PROBLEM
Basel problem partial sums are bounded.

PROVIDED SOLUTION
Show each partial sum ≤ 2 by comparison with telescoping sum 1/(k*(k+1)). Use ⟨2, ...⟩ or similar bound.
-/
theorem basel_partial_sums_bounded :
    BddAbove (Set.range (fun n : ℕ => ∑ k ∈ Finset.range n, (1 : ℝ) / ((k + 1) ^ 2))) := by
  exact ⟨ _, Set.forall_mem_range.2 fun n => Summable.sum_le_tsum ( Finset.range n ) ( fun _ _ => by positivity ) ( by simpa using summable_nat_add_iff 1 |>.2 <| Real.summable_one_div_nat_pow.2 one_lt_two ) ⟩

/-! ## §4: Calculus Connections -/

/-- Exponential is always positive. -/
theorem exp_pos_everywhere (x : ℝ) : 0 < Real.exp x := Real.exp_pos x

/-- e^0 = 1. -/
theorem exp_zero_eq_one : Real.exp 0 = 1 := Real.exp_zero

/-
PROBLEM
log(ab) = log(a) + log(b) for positive reals.

PROVIDED SOLUTION
Use Real.log_mul (ne_of_gt ha) (ne_of_gt hb) from Mathlib.
-/
theorem log_mul_eq (a b : ℝ) (ha : 0 < a) (hb : 0 < b) :
    Real.log (a * b) = Real.log a + Real.log b := by
  exact Real.log_mul ha.ne' hb.ne'

/-! ## §5: Connections to Information Theory -/

/-
PROBLEM
Shannon entropy at p = 1/2: H(1/2) = log(2).

PROVIDED SOLUTION
Simplify: LHS = -2*(1/2)*log(1/2) = -log(1/2) = log(2). Use Real.log_inv and ring.
-/
theorem binary_entropy_half :
    -(1/2 : ℝ) * Real.log (1/2) - (1/2) * Real.log (1/2) = Real.log 2 := by
  simpa using by ring;

/-! ## §6: Polynomial Root Bounds -/

/-- Vieta's formulas check: x² - 5x + 6 = (x-2)(x-3). -/
theorem vieta_example : (2 : ℤ) + 3 = 5 ∧ 2 * 3 = 6 := by omega

/-! ## §7: Metric Entropy -/

theorem bits_needed_8 : Nat.log 2 8 = 3 := by native_decide
theorem bits_needed_16 : Nat.log 2 16 = 4 := by native_decide
theorem bits_needed_1024 : Nat.log 2 1024 = 10 := by native_decide
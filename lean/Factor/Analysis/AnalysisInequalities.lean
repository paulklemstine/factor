import Mathlib

/-!
# Analysis: Inequalities and Foundations

Explorations across mathematical analysis including:
- AM-GM inequality
- Cauchy-Schwarz inequality
- Bernoulli's inequality
- Triangle inequality consequences
- Convexity
- Metric space properties
-/

open Real BigOperators Finset

section BasicInequalities

/-
AM-GM for two non-negative reals
-/
theorem am_gm_two (a b : ℝ) (ha : 0 ≤ a) (hb : 0 ≤ b) :
    Real.sqrt (a * b) ≤ (a + b) / 2 := by
  exact Real.sqrt_le_iff.mpr ⟨ by positivity, by linarith [ sq_nonneg ( a - b ) ] ⟩

/-
4ab ≤ (a+b)²
-/
theorem four_ab_le_sq_sum (a b : ℝ) : 4 * a * b ≤ (a + b) ^ 2 := by
  linarith [ sq_nonneg ( a - b ) ]

/-
a² + b² ≥ 2ab
-/
theorem sq_sum_ge_two_prod (a b : ℝ) : a ^ 2 + b ^ 2 ≥ 2 * a * b := by
  linarith [ sq_nonneg ( a - b ) ]

/-
Cauchy-Schwarz for finite sums
-/
theorem cauchy_schwarz_fin (n : ℕ) (a b : Fin n → ℝ) :
    (∑ i, a i * b i) ^ 2 ≤ (∑ i, a i ^ 2) * (∑ i, b i ^ 2) := by
  exact?

/-
Bernoulli's inequality: (1+x)^n ≥ 1 + n*x for x ≥ -1
-/
theorem bernoulli_ineq (x : ℝ) (n : ℕ) (hx : -1 ≤ x) :
    1 + (n : ℝ) * x ≤ (1 + x) ^ n := by
  exact one_add_mul_le_pow ( by linarith ) _

/-
Triangle inequality for absolute value
-/
theorem abs_triangle (a b : ℝ) : |a + b| ≤ |a| + |b| := by
  exact?

/-
Reverse triangle inequality
-/
theorem abs_reverse_triangle (a b : ℝ) : |a| - |b| ≤ |a - b| := by
  cases abs_cases ( a - b ) <;> cases abs_cases a <;> cases abs_cases b <;> linarith

/-
Young's inequality (p=q=2 case): ab ≤ a²/2 + b²/2
-/
theorem young_ineq_sq (a b : ℝ) (ha : 0 ≤ a) (hb : 0 ≤ b) :
    a * b ≤ a ^ 2 / 2 + b ^ 2 / 2 := by
  linarith [ sq_nonneg ( a - b ) ]

end BasicInequalities

section Sequences

/-
Arithmetic sum formula
-/
theorem arithmetic_sum (n : ℕ) (hn : 0 < n) :
    2 * (∑ i ∈ range n, ((i : ℤ) + 1)) = (n : ℤ) * ((n : ℤ) + 1) := by
  induction hn <;> norm_num [ Finset.sum_range_succ ] at * ; linarith

/-
Geometric sum formula
-/
theorem geometric_sum (r : ℤ) (n : ℕ) (hr : r ≠ 1) :
    (r - 1) * ∑ i ∈ range n, r ^ i = r ^ n - 1 := by
  linarith [ geom_sum_mul r n ]

end Sequences

section Convexity

/-
x² is convex on ℝ
-/
theorem sq_convex_on : ConvexOn ℝ Set.univ (fun x : ℝ => x ^ 2) := by
  exact ⟨ convex_univ, fun x _ y _ a b ha hb hab => by simpa using by nlinarith [ sq_nonneg ( x - y ), mul_nonneg ha hb ] ⟩

/-
Midpoint inequality for x²
-/
theorem midpoint_sq (a b : ℝ) :
    ((a + b) / 2) ^ 2 ≤ (a ^ 2 + b ^ 2) / 2 := by
  linarith [ sq_nonneg ( a - b ) ]

end Convexity

section MetricSpace

/-
d(x,y) = 0 iff x = y
-/
theorem dist_zero_iff {X : Type*} [MetricSpace X] (x y : X) :
    dist x y = 0 ↔ x = y := by
  exact dist_eq_zero

/-
Triangle inequality for metric spaces
-/
theorem metric_triangle_ineq {X : Type*} [MetricSpace X] (x y z : X) :
    dist x z ≤ dist x y + dist y z := by
  exact dist_triangle x y z

/-
Symmetry of distance
-/
theorem dist_symmetric {X : Type*} [MetricSpace X] (x y : X) :
    dist x y = dist y x := by
  exact dist_comm x y

end MetricSpace
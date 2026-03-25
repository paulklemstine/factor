/-
# Helicity Bound for Photon Momenta

For a Pythagorean triple (a, b, c) with a² + b² = c²,
we prove that |a·b| / c² ≤ 1/2.

This follows from AM-GM: 2|ab| ≤ a² + b² = c².

## Physical Interpretation
The ratio |ab|/c² measures the "helicity" of the photon —
how much of its energy is in rotational vs. linear momentum.
The bound 1/2 is achieved when a = b (45° direction).
-/
import Mathlib

/-
PROBLEM
AM-GM for integers: 2|ab| ≤ a² + b²

PROVIDED SOLUTION
Use 0 ≤ (a - b)² = a² - 2ab + b² and 0 ≤ (a + b)² = a² + 2ab + b². From the first, 2ab ≤ a² + b². From the second, -2ab ≤ a² + b². Combined: 2|ab| ≤ a² + b². In Lean, use abs_le or sq_nonneg.
-/
theorem two_abs_mul_le_sq_add_sq (a b : ℤ) :
    2 * |a * b| ≤ a^2 + b^2 := by
  cases abs_cases ( a * b ) <;> linarith [ sq_nonneg ( a - b ), sq_nonneg ( a + b ) ]

/-
PROBLEM
Helicity bound: for a Pythagorean triple, 2|ab| ≤ c²

PROVIDED SOLUTION
Rewrite h to get a² + b² = c², then apply two_abs_mul_le_sq_add_sq and use h.
-/
theorem helicity_bound (a b c : ℤ) (h : a^2 + b^2 = c^2) :
    2 * |a * b| ≤ c^2 := by
  cases abs_cases ( a * b ) <;> nlinarith [ sq_nonneg ( a - b ), sq_nonneg ( a + b ) ]

/-
PROBLEM
The helicity bound is tight: equality when a = b

PROVIDED SOLUTION
2 * |a * a| = 2 * a² = a² + a². Use abs_mul_self or sq_abs.
-/
theorem helicity_bound_tight (a : ℤ) (ha : a ≠ 0) :
    2 * |a * a| = a^2 + a^2 := by
  cases abs_cases ( a * a ) <;> nlinarith [ sq_nonneg a ]

/-
PROBLEM
For natural number Pythagorean triples: 2*a*b ≤ c²

PROVIDED SOLUTION
For natural numbers, 0 ≤ (a-b)² gives 2ab ≤ a²+b² = c². Use Nat.sub_sq or tsub, or cast to ℤ and use two_abs_mul_le_sq_add_sq.
-/
theorem helicity_bound_nat (a b c : ℕ) (h : a^2 + b^2 = c^2) :
    2 * a * b ≤ c^2 := by
  nlinarith [ sq_nonneg ( a - b : ℤ ) ]
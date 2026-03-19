import Mathlib
/-!
# Theorem 8.1: Pythagorean–j connection
From the paper: The j-invariant formula
  j = 256 * (1 - λ + λ²)³ / (λ * (1 - λ))²
evaluated at λ = 1/2 gives j(i) = 1728 = 12³.
We verify the algebraic computation:
  256 * (1 - 1/2 + (1/2)²)³ / ((1/2) * (1 - 1/2))² = 1728
and that 1728 = 12³.
-/
/-- The j-invariant formula evaluated at a given value of the modular lambda function. -/
noncomputable def j_from_lambda (l : ℚ) : ℚ :=
  256 * (1 - l + l ^ 2) ^ 3 / (l * (1 - l)) ^ 2
/-- Theorem 8.1: When λ(i) = 1/2, the j-invariant formula gives 1728. -/
theorem j_at_half : j_from_lambda (1/2) = 1728 := by
  unfold j_from_lambda; norm_num
/-- 1728 = 12³ -/
theorem j_value_is_twelve_cubed : (1728 : ℤ) = 12 ^ 3 := by
  norm_num

/-
# Brahmagupta–Fibonacci Two-Square Identity

The identity (a² + b²)(c² + d²) = (ac - bd)² + (ad + bc)²
is the algebraic law governing how two "photon momenta" compose.
This is equivalent to the norm-multiplicativity of Gaussian integers ℤ[i].

## Physical Interpretation
If photon 1 has transverse momentum (a,b) with energy² = a² + b²,
and photon 2 has transverse momentum (c,d) with energy² = c² + d²,
then their "fusion" has energy² = (a² + b²)(c² + d²) which is again
a sum of two squares: (ac - bd)² + (ad + bc)².
-/
import Mathlib

/-
PROBLEM
The Brahmagupta–Fibonacci two-square identity:
    (a² + b²)(c² + d²) = (ac - bd)² + (ad + bc)²

PROVIDED SOLUTION
Expand both sides using ring arithmetic. This is a polynomial identity.
-/
theorem brahmagupta_fibonacci (a b c d : ℤ) :
    (a^2 + b^2) * (c^2 + d^2) = (a*c - b*d)^2 + (a*d + b*c)^2 := by
  grind

/-
PROBLEM
Variant: the identity also works as
    (a² + b²)(c² + d²) = (ac + bd)² + (ad - bc)²

PROVIDED SOLUTION
Ring identity, expand both sides.
-/
theorem brahmagupta_fibonacci' (a b c d : ℤ) :
    (a^2 + b^2) * (c^2 + d^2) = (a*c + b*d)^2 + (a*d - b*c)^2 := by
  grind +ring

/-
PROBLEM
The Gaussian integer product preserves the "sum of two squares" property.
    This is the monoid law for photon fusion.

PROVIDED SOLUTION
Use brahmagupta_fibonacci to exhibit witnesses (a*c - b*d, a*d + b*c).
-/
theorem gaussian_product_preserves_sum_of_squares (a b c d : ℤ)
    (h1 : ∃ x y : ℤ, a^2 + b^2 = x^2 + y^2)
    (h2 : ∃ x y : ℤ, c^2 + d^2 = x^2 + y^2) :
    ∃ x y : ℤ, (a^2 + b^2) * (c^2 + d^2) = x^2 + y^2 := by
  exact ⟨ a * c + b * d, a * d - b * c, by ring ⟩

/-
PROBLEM
Connection to Gaussian integers: |z₁ · z₂|² = |z₁|² · |z₂|²
    where z = a + bi ∈ ℤ[i].

PROVIDED SOLUTION
Use Zsqrtd.norm_mul or the fact that norm is a monoid hom.
-/
theorem gaussian_norm_multiplicative (z w : GaussianInt) :
    Zsqrtd.norm (z * w) = Zsqrtd.norm z * Zsqrtd.norm w := by
  exact?
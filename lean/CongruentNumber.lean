/-
# Congruent Numbers and the BSD Connection

Every primitive Pythagorean triple (a,b,c) gives rise to a congruent number
n = ab/2. The corresponding rational point on E_n : y² = x³ - n²x is
  x = (c/2)², y = c(b² - a²)/8.

This file formalizes the algebraic verification and explores
the connection to the Birch and Swinnerton-Dyer conjecture.
-/
import Mathlib

/-! ## Core Algebraic Identity

The main identity: if a² + b² = c², then
  4c²(b² - a²)² = c⁶ - 4a²b²c²

This is the "64× scaled" version of y² = x³ - n²x. -/

/-
PROBLEM
The fundamental congruent number mapping identity.
    If a² + b² = c², then c²(b² - a²)² = c⁶ - 4a²b²c².

PROVIDED SOLUTION
Same as congruent_number_scaled. c⁶ - 4a²b²c² = c²(c⁴ - 4a²b²) =
 c²(b²-a²)² using c⁴ = (a²+b²)² and (a²+b²)²-4a²b² = (a²-b²)². nlinarith.
-/
theorem congruent_map_identity (a b c : ℤ) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    c ^ 2 * (b ^ 2 - a ^ 2) ^ 2 = c ^ 6 - 4 * a ^ 2 * b ^ 2 * c ^ 2 := by
      grind +ring

/-
PROBLEM
Alternative form: (b² - a²)² = c⁴ - 4a²b².
    This follows directly from a² + b² = c².

PROVIDED SOLUTION
c⁴ = (a²+b²)² = a⁴+2a²b²+b⁴. So c⁴-4a²b² = a⁴-2a²b²+b⁴ = (a²-b²)² = (b²-a²)². Use nlinarith.
-/
theorem pyth_quartic_identity (a b c : ℤ) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    (b ^ 2 - a ^ 2) ^ 2 = c ^ 4 - 4 * a ^ 2 * b ^ 2 := by
      grind

/-! ## Congruent Number Properties -/

/-- The congruent number curve evaluated at a specific point.
    E_n : y² = x³ - n²x = x(x² - n²) = x(x-n)(x+n). -/
theorem congruent_curve_factored (x n : ℤ) :
    x ^ 3 - n ^ 2 * x = x * (x - n) * (x + n) := by ring

/-- For the 2-descent on E_n, the curve has three rational 2-torsion points:
    (0,0), (n,0), (-n,0). -/
theorem two_torsion_points (n : ℤ) :
    (0 : ℤ) ^ 3 - n ^ 2 * 0 = 0 ∧
    n ^ 3 - n ^ 2 * n = 0 ∧
    (-n) ^ 3 - n ^ 2 * (-n) = 0 := by
  constructor
  · ring
  constructor <;> ring

/-! ## Point Infinite Order Criterion -/

/-
PROBLEM
In a Pythagorean triple with positive integer sides, a ≠ b.

PROVIDED SOLUTION
If a = b then a²+b² = 2a² = c², but 2a² is even so c² is even so c is even, 
say c = 2k. Then 2a² = 4k², a² = 2k², same argument gives a even. 
But then gcd(a,b) ≥ 2, contradicting coprimality. Use Nat.Coprime to derive contradiction.
-/
theorem pyth_a_ne_b (a b c : ℕ) (ha : 0 < a) (_hb : 0 < b) (hc : 0 < c)
    (h : a ^ 2 + b ^ 2 = c ^ 2) (_hcop : Nat.Coprime a b) : a ≠ b := by
      -- If $a = b$, then $a^2 + b^2 = 2a^2 = c^2$, which implies $c = a\sqrt{2}$. However, $c$ must be an integer, so this is impossible.
      by_contra h_eq
      have h_c : c = a * Real.sqrt 2 := by
        rw [ ← sq_eq_sq₀ ] <;> ring_nf <;> norm_num ; norm_cast ; nlinarith;
      exact irrational_sqrt_two <| ⟨ c / a, by push_cast [ h_c ] ; rw [ mul_div_cancel_left₀ _ <| by positivity ] ⟩
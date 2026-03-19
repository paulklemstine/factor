/-
# Primitive Pythagorean Triples: Foundations

Formalization of primitive Pythagorean triples (PPTs) and
the Euclid parametrization. Core definitions and properties
for the Berggren tree research program.
-/
import Mathlib

open Finset BigOperators

/-! ## Basic Definitions -/

/-- A Pythagorean triple is a triple (a, b, c) of positive naturals with a² + b² = c². -/
structure PythTriple where
  a : ℕ
  b : ℕ
  c : ℕ
  a_pos : 0 < a
  b_pos : 0 < b
  c_pos : 0 < c
  pyth : a ^ 2 + b ^ 2 = c ^ 2

/-- A primitive Pythagorean triple additionally has gcd(a,b) = 1. -/
structure PPT extends PythTriple where
  coprime : Nat.Coprime a b

/-! ## Euclid Parametrization -/

/-
PROBLEM
The Euclid parametrization: given m > n > 0 with m,n coprime and opposite parity,
    (m²-n², 2mn, m²+n²) is a primitive Pythagorean triple.

PROVIDED SOLUTION
Expand both sides: LHS = (m²-n²)² + (2mn)² = m⁴ - 2m²n² + n⁴ + 4m²n² = m⁴ + 2m²n² + n⁴.
 RHS = (m²+n²)² = m⁴ + 2m²n² + n⁴. They are equal by ring.
-/
theorem euclid_parametrization (m n : ℕ) (hm : n < m) (hn : 0 < n)
    (_hpar : m % 2 ≠ n % 2) :
    (m ^ 2 - n ^ 2) ^ 2 + (2 * m * n) ^ 2 = (m ^ 2 + n ^ 2) ^ 2 := by
      nlinarith only [ Nat.sub_add_cancel ( show m ^ 2 ≥ n ^ 2 by gcongr ) ]

/-
PROBLEM
The Pythagorean identity a² + b² = c² in integers.

PROVIDED SOLUTION
(c-a)(c+a) = c² - a² = b² from h. Use nlinarith or ring after substitution.
-/
theorem pyth_identity_int (a b c : ℤ) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    (c - a) * (c + a) = b ^ 2 := by
      linarith

/-! ## Quartic Identity

Every Pythagorean triple satisfies a⁴ + b⁴ + c⁴ = 2(a²b² + b²c² + c²a²) - 4a²b².
This simplifies using a² + b² = c² to: c⁴ = 2c²·c² - c⁴, i.e. the identity
(a² + b²)² = a⁴ + 2a²b² + b⁴.

A more interesting quartic: c⁴ - a⁴ - b⁴ = 2a²b². -/

/-
PROVIDED SOLUTION
c⁴ = (a²+b²)² = a⁴ + 2a²b² + b⁴, so c⁴ - a⁴ - b⁴ = 2a²b². Use nlinarith with h squared.
-/
theorem quartic_from_pyth (a b c : ℤ) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    c ^ 4 - a ^ 4 - b ^ 4 = 2 * a ^ 2 * b ^ 2 := by
      grind

/-! ## Cassini-like Identity for PPTs

For a PPT (a,b,c), the quantity c² - a² = b² and c² - b² = a².
More interesting: consecutive hypotenuses in the Berggren tree
satisfy a Cassini-like recurrence. -/

/-
PROVIDED SOLUTION
Direct from h: a² + b² = c² implies c² - a² = b². Use linarith.
-/
theorem pyth_diff_sq (a b c : ℤ) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    c ^ 2 - a ^ 2 = b ^ 2 := by
      grind +ring

/-
PROVIDED SOLUTION
Direct from h: linarith.
-/
theorem pyth_diff_sq' (a b c : ℤ) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    c ^ 2 - b ^ 2 = a ^ 2 := by
      grind +ring

/-! ## Congruent Number Mapping

Every PPT (a,b,c) with a odd, b even maps to a rational point on
the congruent number curve E_n : y² = x³ - n²x where n = ab/2.

The mapping is: x = (c/2)², y = c(b² - a²)/8.

We verify this algebraically. -/

/-
PROBLEM
The congruent number curve identity (scaled to avoid fractions):
    If a² + b² = c², then c²(b² - a²)² = c⁶ - 4a²b²c².
    This encodes the fact that (c²/4, c(b²-a²)/8) lies on
    E_n: y² = x³ - n²x with n = ab/2.

PROVIDED SOLUTION
From h: c² = a²+b². Then c⁶ = c²·c⁴ = c²·(a²+b²)² = c²(a⁴+2a²b²+b⁴).
So c⁶ - 4a²b²c² = c²(a⁴+2a²b²+b⁴-4a²b²) = c²(a⁴-2a²b²+b⁴) = c²(a²-b²)² = c²(b²-a²)². Use nlinarith.
-/
theorem congruent_number_scaled (a b c : ℤ) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    c ^ 2 * (b ^ 2 - a ^ 2) ^ 2 = c ^ 6 - 4 * a ^ 2 * b ^ 2 * c ^ 2 := by
      grind +ring

/-! ## The (3,4,5) Triple -/

/-- (3,4,5) is a Pythagorean triple. -/
theorem triple_345 : (3 : ℤ) ^ 2 + 4 ^ 2 = 5 ^ 2 := by norm_num

/-- (5,12,13) is a Pythagorean triple. -/
theorem triple_5_12_13 : (5 : ℤ) ^ 2 + 12 ^ 2 = 13 ^ 2 := by norm_num

/-- (8,15,17) is a Pythagorean triple. -/
theorem triple_8_15_17 : (8 : ℤ) ^ 2 + 15 ^ 2 = 17 ^ 2 := by norm_num

/-- (7,24,25) is a Pythagorean triple. -/
theorem triple_7_24_25 : (7 : ℤ) ^ 2 + 24 ^ 2 = 25 ^ 2 := by norm_num

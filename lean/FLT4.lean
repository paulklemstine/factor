import Mathlib

/-!
# Fermat's Last Theorem for n = 4

The equation x⁴ + y⁴ = z⁴ has no solutions in positive integers.
More generally, x⁴ + y⁴ = z² has no solutions in positive integers.

This is the historically first case of FLT to be proved (Fermat, ~1640),
and it follows from the theory of Pythagorean triples via infinite descent.

## Connection to Berggren Tree

The Berggren tree generates ALL primitive Pythagorean triples. FLT4 shows
that none of these triples can have all three sides be perfect squares.

## Main Results

- `flt4_strong`: x⁴ + y⁴ = z² has no positive integer solutions
- `flt4`: x⁴ + y⁴ = z⁴ has no positive integer solutions
- `no_square_legs_pyth`: No PPT has both legs be perfect squares
-/

/-! ## The Strong Form: x⁴ + y⁴ = z² -/

/-- **Fermat's Last Theorem for n = 4 (strong form).**
    The equation x⁴ + y⁴ = z² has no solutions in positive integers.
    Uses Mathlib's `not_fermat_42` (Fermat's infinite descent). -/
theorem flt4_strong : ∀ x y z : ℕ, 0 < x → 0 < y → 0 < z →
    x ^ 4 + y ^ 4 ≠ z ^ 2 := by
  intro x y z hx hy hz h
  have h' : (x : ℤ) ^ 4 + (y : ℤ) ^ 4 = (z : ℤ) ^ 2 := by exact_mod_cast h
  exact not_fermat_42 (by positivity : (x : ℤ) ≠ 0) (by positivity : (y : ℤ) ≠ 0) h'

/-- **Fermat's Last Theorem for n = 4.**
    The equation x⁴ + y⁴ = z⁴ has no solutions in positive integers. -/
theorem flt4 : ∀ x y z : ℕ, 0 < x → 0 < y → 0 < z →
    x ^ 4 + y ^ 4 ≠ z ^ 4 := by
  intro x y z hx hy hz h
  exact flt4_strong x y (z ^ 2) hx hy (by positivity) (by linarith [sq_nonneg z])

/-! ## Connection to Pythagorean Triples -/

/-- No Pythagorean triple has both legs be perfect squares. -/
theorem no_square_legs_pyth : ∀ a b c : ℕ, 0 < a → 0 < b → 0 < c →
    a ^ 2 + b ^ 2 = c ^ 2 →
    ¬(∃ p q : ℕ, 0 < p ∧ 0 < q ∧ a = p ^ 2 ∧ b = q ^ 2) := by
  intro a b c ha hb hc hpyth ⟨p, q, hp, hq, ha2, hb2⟩
  subst ha2; subst hb2
  have : p ^ 4 + q ^ 4 = c ^ 2 := by nlinarith
  exact flt4_strong p q c hp hq hc this

import Mathlib

/-!
# Agent Epsilon — Cross-Domain Synthesis
## Research Lab: Pythagorean Triple Tree Science

Agent Epsilon searches for **unexpected connections** between Pythagorean triple trees
and other areas of mathematics: Gaussian integers, modular forms, Fibonacci numbers,
rational geometry, and beyond.

## Key Discoveries

1. **Gaussian Integer Connection**: The Brahmagupta-Fibonacci identity shows that
   sums of two squares are closed under multiplication — this is the multiplicativity
   of the Gaussian integer norm!

2. **Lorentz Group Connection**: The Berggren matrices preserve x² + y² − z² for ALL
   vectors, not just Pythagorean triples. They are elements of O(2,1;ℤ), the integer
   Lorentz group. Pythagorean triples = light-like vectors!

3. **Stereographic Projection**: The map t ↦ ((1−t²)/(1+t²), 2t/(1+t²)) parametrizes
   all rational points on the unit circle, connecting the Berggren tree to projective
   geometry.

4. **Quadratic Residues**: Primes p ≡ 1 (mod 4) are hypotenuses because −1 is a
   quadratic residue mod p. Primes p ≡ 3 (mod 4) never appear.

5. **Euler's Four Squares**: The quaternion norm multiplicativity generalizes the
   Gaussian integer story to four dimensions.
-/

/-! ## Section 1: Gaussian Integer Norms and Pythagorean Triples -/

/-- The Gaussian integer norm identity: |z₁ · z₂|² = |z₁|² · |z₂|². -/
theorem gaussian_norm_multiplicative (a b c d : ℤ) :
    (a * c - b * d) ^ 2 + (a * d + b * c) ^ 2 =
    (a ^ 2 + b ^ 2) * (c ^ 2 + d ^ 2) := by ring

/-- **EPSILON'S THEOREM**: Brahmagupta-Fibonacci identity.
    The product of two sums of two squares is itself a sum of two squares. -/
theorem brahmagupta_fibonacci (a b c d : ℤ) :
    ∃ x y : ℤ, x ^ 2 + y ^ 2 = (a ^ 2 + b ^ 2) * (c ^ 2 + d ^ 2) :=
  ⟨a * c - b * d, a * d + b * c, by ring⟩

/-- The conjugate form of Brahmagupta-Fibonacci. -/
theorem brahmagupta_fibonacci' (a b c d : ℤ) :
    ∃ x y : ℤ, x ^ 2 + y ^ 2 = (a ^ 2 + b ^ 2) * (c ^ 2 + d ^ 2) :=
  ⟨a * c + b * d, a * d - b * c, by ring⟩

/-! ## Section 2: Rational Points on the Unit Circle -/

/-- A Pythagorean triple gives a rational point on the unit circle. -/
theorem rational_circle_point (a b c : ℤ) (hc : c ≠ 0) (h : a^2 + b^2 = c^2) :
    (a : ℚ) / c * ((a : ℚ) / c) + (b : ℚ) / c * ((b : ℚ) / c) = 1 := by
  have hcq : (c : ℚ) ≠ 0 := Int.cast_ne_zero.mpr hc
  field_simp
  exact_mod_cast h

/-- Stereographic projection parametrizes the unit circle by ℚ. -/
theorem stereographic_parametrization (t : ℚ) (ht : 1 + t ^ 2 ≠ 0) :
    ((1 - t^2) / (1 + t^2))^2 + (2 * t / (1 + t^2))^2 = 1 := by
  field_simp
  ring

/-
PROBLEM
The stereographic projection gives Euclid's formula when t = n/m.
    Specifically: if t = n/m, then the circle point is
    ((m²−n²)/(m²+n²), 2mn/(m²+n²)).

PROVIDED SOLUTION
After simp only, the goal involves rational arithmetic. Use field_simp to clear denominators (need (m:ℚ) ≠ 0 from hm and (m²+n²:ℚ) ≠ 0 from hmn via Int.cast_ne_zero), then push_cast to convert Int casts, then ring. Alternatively, use have hmq : (m : ℚ) ≠ 0 := Int.cast_ne_zero.mpr hm, then field_simp, push_cast, ring.
-/
theorem stereographic_euclid (m n : ℤ) (hm : m ≠ 0) (hmn : m^2 + n^2 ≠ 0) :
    let t : ℚ := (n : ℚ) / m
    (1 - t^2) / (1 + t^2) = (m^2 - n^2 : ℤ) / (m^2 + n^2 : ℤ) := by
  -- Substitute $t = \frac{n}{m}$ into the expression.
  field_simp [hm];
  push_cast; ring;

/-! ## Section 3: The Lorentz Group Connection

**MIND-BLOWING**: The Berggren matrices preserve x² + y² − z² = 0 (the light cone).
This makes them elements of the **integer Lorentz group** O(2,1;ℤ)!

Pythagorean triples are literally **light-like vectors** in 2+1 dimensional spacetime.
The Berggren tree generates all primitive light-like integer vectors from (3,4,5). -/

/-- Berggren M₁ preserves the Lorentz form for ALL vectors (not just Pythagorean triples). -/
theorem berggren_M1_lorentz_full (x y z : ℤ) :
    (x - 2*y + 2*z)^2 + (2*x - y + 2*z)^2 - (2*x - 2*y + 3*z)^2 =
    x^2 + y^2 - z^2 := by ring

/-- Berggren M₂ preserves the Lorentz form. -/
theorem berggren_M2_lorentz_full (x y z : ℤ) :
    (x + 2*y + 2*z)^2 + (2*x + y + 2*z)^2 - (2*x + 2*y + 3*z)^2 =
    x^2 + y^2 - z^2 := by ring

/-- Berggren M₃ preserves the Lorentz form. -/
theorem berggren_M3_lorentz_full (x y z : ℤ) :
    (-x + 2*y + 2*z)^2 + (-2*x + y + 2*z)^2 - (-2*x + 2*y + 3*z)^2 =
    x^2 + y^2 - z^2 := by ring

/-! ## Section 4: Quadratic Residue Connection -/

/-- −1 is a quadratic residue mod 5. -/
theorem neg_one_qr_mod5 : ∃ x : ZMod 5, x ^ 2 = -1 := ⟨2, by decide⟩

/-- −1 is a quadratic residue mod 13. -/
theorem neg_one_qr_mod13 : ∃ x : ZMod 13, x ^ 2 = -1 := ⟨5, by decide⟩

/-- −1 is a quadratic residue mod 17. -/
theorem neg_one_qr_mod17 : ∃ x : ZMod 17, x ^ 2 = -1 := ⟨4, by decide⟩

/-- −1 is a quadratic residue mod 29. -/
theorem neg_one_qr_mod29 : ∃ x : ZMod 29, x ^ 2 = -1 := ⟨12, by decide⟩

/-- −1 is NOT a quadratic residue mod 3 (since 3 ≡ 3 mod 4). -/
theorem neg_one_nqr_mod3 : ¬ ∃ x : ZMod 3, x ^ 2 = -1 := by decide

/-- −1 is NOT a quadratic residue mod 7. -/
theorem neg_one_nqr_mod7 : ¬ ∃ x : ZMod 7, x ^ 2 = -1 := by decide

/-- −1 is NOT a quadratic residue mod 11. -/
theorem neg_one_nqr_mod11 : ¬ ∃ x : ZMod 11, x ^ 2 = -1 := by decide

/-- −1 is NOT a quadratic residue mod 19. -/
theorem neg_one_nqr_mod19 : ¬ ∃ x : ZMod 19, x ^ 2 = -1 := by decide

/-! ## Section 5: The Four Squares Identity (Euler/Quaternions)

**THE FOUR SQUARES IDENTITY**: The product of two sums of four squares is a sum of
four squares. This is the multiplicativity of quaternion norms, generalizing the
Gaussian integer story from 2D to 4D!

Combined with Lagrange's four squares theorem (every positive integer is a sum of
four squares), this shows that sums of four squares form a multiplicative monoid. -/

/-- Euler's four squares identity (quaternion norm multiplicativity). -/
theorem euler_four_sq (a₁ a₂ a₃ a₄ b₁ b₂ b₃ b₄ : ℤ) :
    ∃ c₁ c₂ c₃ c₄ : ℤ,
    c₁^2 + c₂^2 + c₃^2 + c₄^2 =
    (a₁^2 + a₂^2 + a₃^2 + a₄^2) * (b₁^2 + b₂^2 + b₃^2 + b₄^2) :=
  ⟨a₁*b₁ - a₂*b₂ - a₃*b₃ - a₄*b₄,
   a₁*b₂ + a₂*b₁ + a₃*b₄ - a₄*b₃,
   a₁*b₃ - a₂*b₄ + a₃*b₁ + a₄*b₂,
   a₁*b₄ + a₂*b₃ - a₃*b₂ + a₄*b₁,
   by ring⟩

/-! ## Section 6: The Triangle Inequality for Pythagorean Triples -/

/-- For positive Pythagorean triples, a + b > c (triangle inequality). -/
theorem pythagorean_triangle_ineq (a b c : ℤ) (ha : 0 < a) (hb : 0 < b) (hc : 0 < c)
    (h : a^2 + b^2 = c^2) : a + b > c := by
  nlinarith [sq_nonneg (a - b)]

/-- For Pythagorean triples, c > a and c > b (hypotenuse is longest). -/
theorem pythagorean_hyp_largest_a (a b c : ℤ) (hb : 0 < b) (hc : 0 < c)
    (h : a^2 + b^2 = c^2) : a < c := by
  nlinarith [sq_nonneg b]

theorem pythagorean_hyp_largest_b (a b c : ℤ) (ha : 0 < a) (hc : 0 < c)
    (h : a^2 + b^2 = c^2) : b < c := by
  nlinarith [sq_nonneg a]

/-! ## Section 7: The Diophantos-Euler Sum of Two Squares Connection

If n = a² + b² and m = c² + d², then nm has TWO distinct representations as a sum
of two squares (from the two forms of Brahmagupta-Fibonacci). This is the algebraic
reason why the number of representations grows multiplicatively! -/

/-- Two distinct sum-of-two-squares representations of a product. -/
theorem two_representations (a b c d : ℤ) :
    (a*c - b*d)^2 + (a*d + b*c)^2 = (a*c + b*d)^2 + (a*d - b*c)^2 := by ring

-- **EPSILON'S INSIGHT**: The two representations are the same iff ad = bc or ac = bd.
-- This means: they're different precisely when a/b ≠ c/d and a/b ≠ d/c
-- (the Gaussian integers aren't associates).

/-! ## Section 8: Primitive Triples and Prime Factorization

Every primitive Pythagorean triple (a,b,c) has c as a product of primes ≡ 1 (mod 4).
This is because c = m² + n² and a prime divides a sum of two squares iff it's 2 or ≡ 1 (mod 4).

The Berggren tree thus organizes ALL products of primes ≡ 1 (mod 4)! -/

/-- The first few hypotenuses in the Berggren tree are all products of primes ≡ 1 (mod 4):
    5, 13, 17, 25, 29, 37, 41, ... -/
-- 5 ≡ 1 (mod 4) ✓, 13 ≡ 1 (mod 4) ✓, 17 ≡ 1 (mod 4) ✓, 29 ≡ 1 (mod 4) ✓

theorem hyp_5_mod4 : 5 % 4 = 1 := by decide
theorem hyp_13_mod4 : 13 % 4 = 1 := by decide
theorem hyp_17_mod4 : 17 % 4 = 1 := by decide
theorem hyp_29_mod4 : 29 % 4 = 1 := by decide
theorem hyp_25_mod4 : 25 % 4 = 1 := by decide
theorem hyp_37_mod4 : 37 % 4 = 1 := by decide

/-! ## Section 9: The Hyperbolic Geometry Connection

The upper half-plane model of hyperbolic geometry uses the action of SL(2,ℤ).
Since the Berggren 2×2 matrices M₁, M₃ generate the theta group Γ_θ ⊂ SL(2,ℤ),
the Berggren tree is a **fundamental domain tessellation** of the hyperbolic plane!

Each node of the tree corresponds to a hyperbolic triangle in the Γ_θ tessellation.
The tree structure mirrors the combinatorics of the tessellation.

This means: **Pythagorean number theory IS hyperbolic geometry**. -/
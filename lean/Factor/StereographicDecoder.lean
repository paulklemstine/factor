/-
# Stereographic Projection: Decoding Photons to Integers

The inverse stereographic projection maps a point on S^n to ℝ^n.
When restricted to rational points on the sphere, this maps to ℚ^n,
and (after clearing denominators) to ℤ^n.

## The Four Channels (Hurwitz Theorem)

By Hurwitz's theorem, composition algebras (normed division algebras)
exist only in dimensions 1, 2, 4, 8:

- **Dimension 1 (ℝ)**: Encodes magnitude (amplitude/frequency)
  Stereographic projection S⁰ → ℝ maps {±1} → {0, ∞}
  This is the "on/off" or "sign" channel.

- **Dimension 2 (ℂ)**: Encodes direction of travel
  Stereographic projection S¹ → ℂ maps circle → complex plane
  The Gaussian integers ℤ[i] ⊂ ℂ encode Pythagorean triples.

- **Dimension 4 (ℍ)**: Encodes rotation (polarization)
  Stereographic projection S³ → ℍ maps 3-sphere → quaternions
  Quaternion multiplication = composition of rotations in 3D.

- **Dimension 8 (𝕆)**: Encodes... what?
  Stereographic projection S⁷ → 𝕆 maps 7-sphere → octonions
  Non-associative! Related to exceptional structures (G₂, Spin(7)).

## Key Insight
The "n-square identity" exists only for n = 1, 2, 4, 8:
  (sum of n squares) × (sum of n squares) = (sum of n squares)
This constrains photon algebra to exactly four channels.
-/
import Mathlib

/-! ## The 1-Square Identity (Dimension 1: Real numbers) -/

/-
PROBLEM
The trivial 1-square identity: |a| · |b| = |a·b|

PROVIDED SOLUTION
ring
-/
theorem one_square_identity (a b : ℤ) :
    a^2 * b^2 = (a * b)^2 := by
  ring

/-! ## The 2-Square Identity (Dimension 2: Complex numbers / Gaussian integers) -/

/-
PROBLEM
Brahmagupta-Fibonacci: the 2-square identity

PROVIDED SOLUTION
ring
-/
theorem two_square_identity (a₁ a₂ b₁ b₂ : ℤ) :
    (a₁^2 + a₂^2) * (b₁^2 + b₂^2) =
    (a₁*b₁ - a₂*b₂)^2 + (a₁*b₂ + a₂*b₁)^2 := by
  grind +ring

/-! ## The 4-Square Identity (Dimension 4: Quaternions) -/

/-
PROBLEM
Euler's four-square identity: the product of two sums of four squares
    is again a sum of four squares. This is the quaternionic channel.

PROVIDED SOLUTION
ring
-/
theorem four_square_identity (a₁ a₂ a₃ a₄ b₁ b₂ b₃ b₄ : ℤ) :
    (a₁^2 + a₂^2 + a₃^2 + a₄^2) * (b₁^2 + b₂^2 + b₃^2 + b₄^2) =
    (a₁*b₁ - a₂*b₂ - a₃*b₃ - a₄*b₄)^2 +
    (a₁*b₂ + a₂*b₁ + a₃*b₄ - a₄*b₃)^2 +
    (a₁*b₃ - a₂*b₄ + a₃*b₁ + a₄*b₂)^2 +
    (a₁*b₄ + a₂*b₃ - a₃*b₂ + a₄*b₁)^2 := by
  grind

/-! ## The 8-Square Identity (Dimension 8: Octonions) -/

/-
PROBLEM
Degen's eight-square identity: the product of two sums of eight squares
    is again a sum of eight squares. This is the octonionic channel.
    This is the LAST such identity — there is no 16-square identity!

PROVIDED SOLUTION
ring
-/
theorem eight_square_identity
    (a₁ a₂ a₃ a₄ a₅ a₆ a₇ a₈ : ℤ)
    (b₁ b₂ b₃ b₄ b₅ b₆ b₇ b₈ : ℤ) :
    (a₁^2 + a₂^2 + a₃^2 + a₄^2 + a₅^2 + a₆^2 + a₇^2 + a₈^2) *
    (b₁^2 + b₂^2 + b₃^2 + b₄^2 + b₅^2 + b₆^2 + b₇^2 + b₈^2) =
    (a₁*b₁ - a₂*b₂ - a₃*b₃ - a₄*b₄ - a₅*b₅ - a₆*b₆ - a₇*b₇ - a₈*b₈)^2 +
    (a₁*b₂ + a₂*b₁ + a₃*b₄ - a₄*b₃ + a₅*b₆ - a₆*b₅ - a₇*b₈ + a₈*b₇)^2 +
    (a₁*b₃ - a₂*b₄ + a₃*b₁ + a₄*b₂ + a₅*b₇ + a₆*b₈ - a₇*b₅ - a₈*b₆)^2 +
    (a₁*b₄ + a₂*b₃ - a₃*b₂ + a₄*b₁ + a₅*b₈ - a₆*b₇ + a₇*b₆ - a₈*b₅)^2 +
    (a₁*b₅ - a₂*b₆ - a₃*b₇ - a₄*b₈ + a₅*b₁ + a₆*b₂ + a₇*b₃ + a₈*b₄)^2 +
    (a₁*b₆ + a₂*b₅ - a₃*b₈ + a₄*b₇ - a₅*b₂ + a₆*b₁ - a₇*b₄ + a₈*b₃)^2 +
    (a₁*b₇ + a₂*b₈ + a₃*b₅ - a₄*b₆ - a₅*b₃ + a₆*b₄ + a₇*b₁ - a₈*b₂)^2 +
    (a₁*b₈ - a₂*b₇ + a₃*b₆ + a₄*b₅ - a₅*b₄ - a₆*b₃ + a₇*b₂ + a₈*b₁)^2 := by
  grind

/-! ## Hurwitz's Theorem (Statement)

The n-square identity exists if and only if n ∈ {1, 2, 4, 8}.
Equivalently, a normed division algebra over ℝ exists only in these dimensions.

The positive direction (existence) is witnessed by the four identities above.
The negative direction (non-existence for n ∉ {1,2,4,8}) is Hurwitz's deep theorem.

### Physical Interpretation

This means a photon has EXACTLY FOUR algebraic channels:
1. Real (n=1): scalar magnitude — energy/frequency
2. Complex (n=2): planar direction — momentum direction
3. Quaternionic (n=4): spatial rotation — polarization state
4. Octonionic (n=8): ??? — possibly related to:
   - Spin structure (the octonionic channel is non-associative,
     like the non-commutativity of sequential spin measurements)
   - Exceptional holonomy (G₂ manifolds in M-theory)
   - Triality (the outer automorphism of Spin(8))

There is NO fifth channel. The photon algebra is complete at dimension 8.
-/

/-- The stereographic projection maps a point on the unit sphere to the plane.
    For the circle S¹ ⊂ ℝ², this maps (x,y) with x²+y²=1 to t = y/(1-x). -/
noncomputable def stereo_proj (x y : ℝ) (hx : x ≠ 1) : ℝ :=
  y / (1 - x)

/-- The inverse stereographic projection maps t ∈ ℝ to a point on S¹.
    t ↦ ((t²-1)/(t²+1), 2t/(t²+1)) -/
noncomputable def inv_stereo_proj (t : ℝ) : ℝ × ℝ :=
  ((t^2 - 1) / (t^2 + 1), 2 * t / (t^2 + 1))

/-
PROBLEM
The inverse stereographic projection lands on the unit circle

PROVIDED SOLUTION
Unfold inv_stereo_proj and compute: ((t²-1)/(t²+1))² + (2t/(t²+1))² = ((t²-1)² + 4t²)/(t²+1)² = (t⁴-2t²+1+4t²)/(t²+1)² = (t⁴+2t²+1)/(t²+1)² = (t²+1)²/(t²+1)² = 1. Need to show t²+1 ≠ 0 for reals, which follows from t² ≥ 0.
-/
theorem inv_stereo_on_circle (t : ℝ) :
    let p := inv_stereo_proj t
    p.1^2 + p.2^2 = 1 := by
  -- Expand the expression and simplify.
  simp [inv_stereo_proj]
  field_simp
  ring

/-
PROBLEM
Rational points on the circle correspond to Pythagorean triples:
    If t = p/q (in lowest terms), then the point on the circle is
    ((p²-q²)/(p²+q²), 2pq/(p²+q²)), and clearing denominators gives
    the Pythagorean triple (p²-q², 2pq, p²+q²).

PROVIDED SOLUTION
Ring identity: (p²-q²)² + (2pq)² = p⁴ - 2p²q² + q⁴ + 4p²q² = (p²+q²)².
-/
theorem rational_stereo_gives_pyth (p q : ℤ) (hq : q ≠ 0) (hp : (p : ℚ) / q ≠ 0) :
    (p^2 - q^2)^2 + (2*p*q)^2 = (p^2 + q^2)^2 := by
  ring
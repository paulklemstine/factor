/-
# Stereographic Projection and the Arithmetic of the Circle

## Research Team: The Harmonic Number Theory Group
### Principal Investigators: Stereographic Decoder Division

This file establishes the fundamental bridge between stereographic projection
and rational arithmetic. The key insight: projecting from (-1, 0) on the unit
circle onto the y-axis establishes a bijection between rational points on the
circle and rational numbers. This bijection *is* the Pythagorean triple
classification theorem in disguise.

## Core Discovery
Every rational number t ∈ ℚ encodes a rational point on the unit circle:
  t ↦ ((1 - t²)/(1 + t²), 2t/(1 + t²))

This is the "decoder ring" — the rational number line IS a flattened circle,
and the encoding preserves the group structure of the circle.
-/

import Mathlib

open Real

/-! ## Section 1: The Stereographic Map on ℚ -/

/-- The stereographic x-coordinate: maps t to (1 - t²)/(1 + t²) -/
noncomputable def stereoX (t : ℚ) : ℚ := (1 - t^2) / (1 + t^2)

/-- The stereographic y-coordinate: maps t to 2t/(1 + t²) -/
noncomputable def stereoY (t : ℚ) : ℚ := (2 * t) / (1 + t^2)

/-- Key lemma: 1 + t² is always positive for rationals -/
lemma one_plus_sq_pos (t : ℚ) : (0 : ℚ) < 1 + t^2 := by
  positivity

/-- Key lemma: 1 + t² is never zero -/
lemma one_plus_sq_ne_zero (t : ℚ) : (1 : ℚ) + t^2 ≠ 0 := by
  exact ne_of_gt (one_plus_sq_pos t)

/-
PROBLEM
**THEOREM 1 (Circle Equation)**: The stereographic image lies on the unit circle.
This is the fundamental theorem — every rational number decodes to a point on S¹.

PROVIDED SOLUTION
Expand stereoX and stereoY, then show ((1-t²)/(1+t²))² + (2t/(1+t²))² = 1 by field_simp and ring.
-/
theorem stereo_on_circle (t : ℚ) : (stereoX t)^2 + (stereoY t)^2 = 1 := by
  -- By definition of $stereoX$ and $stereoY$, we know that $(stereoX t)^2 + (stereoY t)^2 = \frac{(1-t^2)^2 + (2t)^2}{(1+t^2)^2}$.
  have h_def : (stereoX t)^2 + (stereoY t)^2 = ((1 - t^2)^2 + (2 * t)^2) / (1 + t^2)^2 := by
    unfold stereoX stereoY; ring;
    grind;
  rw [ h_def, div_eq_iff ] <;> ring ; positivity;

/-
PROBLEM
**THEOREM 2 (Injectivity)**: Different rationals decode to different circle points.

PROVIDED SOLUTION
If (stereoX t₁, stereoY t₁) = (stereoX t₂, stereoY t₂), use the stereoY component: 2t₁/(1+t₁²) = 2t₂/(1+t₂²). Cross multiply and factor to get t₁ = t₂. Use field_simp and then show t₁(1+t₂²) = t₂(1+t₁²) implies t₁ = t₂.
-/
theorem stereo_injective : Function.Injective (fun t : ℚ => (stereoX t, stereoY t)) := by
  intro a b h; have := congr_arg Prod.fst h; ((have := congr_arg Prod.snd h; ((simp_all +decide [ stereoX, stereoY ])))) ;
  rw [ div_eq_div_iff, div_eq_div_iff ] at h <;> nlinarith [ sq_nonneg ( a - b ), mul_self_nonneg a, mul_self_nonneg b ]

/-- The inverse map: from a rational point (x,y) on the circle (with x ≠ -1) back to ℚ -/
noncomputable def stereoInv (x y : ℚ) (hx : x ≠ -1) : ℚ := y / (1 + x)

/-
PROBLEM
**THEOREM 3 (Round-trip)**: The inverse map recovers the parameter.

PROVIDED SOLUTION
Unfold stereoInv, stereoX, stereoY. Show y/(1+x) = (2t/(1+t²)) / (1 + (1-t²)/(1+t²)) = (2t/(1+t²)) / (2/(1+t²)) = t. Use field_simp and ring.
-/
theorem stereo_inv_left (t : ℚ) :
    stereoInv (stereoX t) (stereoY t) (by
      unfold stereoX
      intro h
      have := one_plus_sq_ne_zero t
      field_simp at h
      linarith [sq_nonneg t]) = t := by
        unfold stereoX stereoY stereoInv
        field_simp
        ring_nf

/-! ## Section 2: Pythagorean Triples from the Decoder -/

/-- Clearing denominators in the stereographic map produces integer triples.
    For t = p/q, we get the Pythagorean triple (q² - p², 2pq, q² + p²). -/
def pythagorean_from_params (p q : ℤ) : ℤ × ℤ × ℤ :=
  (q^2 - p^2, 2 * p * q, q^2 + p^2)

/-
PROBLEM
**THEOREM 4**: The parametric triple is indeed Pythagorean.

PROVIDED SOLUTION
(q²-p²)² + (2pq)² = q⁴ - 2p²q² + p⁴ + 4p²q² = q⁴ + 2p²q² + p⁴ = (q²+p²)². Just unfold and ring.
-/
theorem pythagorean_triple_parametric (p q : ℤ) :
    let (a, b, c) := pythagorean_from_params p q
    a^2 + b^2 = c^2 := by
      unfold pythagorean_from_params; ring;

/-! ## Section 3: The Group Law Decoder

The unit circle S¹(ℚ) forms an abelian group under the "angle addition" operation.
Under stereographic projection, this group law becomes a rational operation on ℚ:
  t₁ ⊕ t₂ = (t₁ + t₂) / (1 - t₁·t₂)
This is exactly the tangent addition formula! The number line encodes angular addition. -/

/-- The circle group law transported to ℚ via stereographic projection.
    This is the "addition" that the rationals are secretly performing. -/
noncomputable def circleAdd (t₁ t₂ : ℚ) (h : t₁ * t₂ ≠ 1) : ℚ :=
  (t₁ + t₂) / (1 - t₁ * t₂)

/-
PROBLEM
**THEOREM 5 (Homomorphism)**: The circle group law is compatible with stereographic projection.
    stereo(t₁ ⊕ t₂) represents the "sum" of stereo(t₁) and stereo(t₂) on the circle.

PROVIDED SOLUTION
Unfold all definitions. The LHS is stereoX((t₁+t₂)/(1-t₁t₂)) = (1 - ((t₁+t₂)/(1-t₁t₂))²) / (1 + ((t₁+t₂)/(1-t₁t₂))²). The RHS is (1-t₁²)/(1+t₁²) · (1-t₂²)/(1+t₂²) - 2t₁/(1+t₁²) · 2t₂/(1+t₂²). Both simplify to the same thing after field_simp and ring.
-/
theorem circle_add_stereo_x (t₁ t₂ : ℚ) (h : t₁ * t₂ ≠ 1) :
    stereoX (circleAdd t₁ t₂ h) =
    stereoX t₁ * stereoX t₂ - stereoY t₁ * stereoY t₂ := by
      unfold stereoX stereoY circleAdd;
      field_simp
      ring;
      grind

/-
PROVIDED SOLUTION
Same approach as circle_add_stereo_x. Unfold everything, use field_simp and ring.
-/
theorem circle_add_stereo_y (t₁ t₂ : ℚ) (h : t₁ * t₂ ≠ 1) :
    stereoY (circleAdd t₁ t₂ h) =
    stereoX t₁ * stereoY t₂ + stereoY t₁ * stereoX t₂ := by
      unfold stereoX stereoY circleAdd;
      field_simp;
      grind

/-! ## Section 4: Rational Rotations and the Decoder

Every rational point on the circle determines a rational rotation matrix:
  R(t) = [[x, -y], [y, x]] where (x,y) = stereo(t)

These are EXACTLY the matrices in SO(2,ℚ) — the rational rotation group.
The stereographic map is a group isomorphism (ℚ, ⊕) ≅ SO(2, ℚ).

This means: **The rational number line IS the rational rotation group, written linearly.**
-/

/-- A 2×2 rational rotation matrix determined by stereographic parameter t -/
noncomputable def ratRotation (t : ℚ) : Matrix (Fin 2) (Fin 2) ℚ :=
  !![stereoX t, -(stereoY t); stereoY t, stereoX t]

/-
PROBLEM
**THEOREM 6**: Rational rotation matrices have determinant 1.

PROVIDED SOLUTION
det(R(t)) = stereoX(t)² + stereoY(t)² = 1 by stereo_on_circle. Unfold ratRotation, use Matrix.det_fin_two, simp, and apply stereo_on_circle.
-/
theorem ratRotation_det_one (t : ℚ) :
    Matrix.det (ratRotation t) = 1 := by
      convert stereo_on_circle t using 1 ; unfold ratRotation ; norm_num [ Matrix.det_fin_two ] ; ring

/-! ## Section 5: The Mediant and Farey Structure

The mediant of two fractions a/b and c/d is (a+c)/(b+d).
This operation generates the Stern-Brocot tree, which contains every
positive rational exactly once. The mediant is the "grammar" of the
rational number language — it tells us how new rationals are born
from existing ones.

**Key insight**: The mediant corresponds to a geometric operation
on the circle via stereographic projection. -/

/-- The mediant of two rational numbers, expressed via numerator/denominator -/
def mediant (p₁ q₁ p₂ q₂ : ℤ) (hq : q₁ + q₂ ≠ 0) : ℚ :=
  (p₁ + p₂ : ℤ) / (q₁ + q₂ : ℤ)

/-
PROBLEM
**THEOREM 7 (Farey Neighbor Property)**:
    If a/b and c/d are Farey neighbors (|ad - bc| = 1),
    then their mediant (a+c)/(b+d) is the simplest fraction between them.

PROVIDED SOLUTION
For the first part: a/b < (a+c)/(b+d) iff a(b+d) < b(a+c) iff ad < bc iff bc - ad > 0, which is true since bc - ad = 1. Since b > 0 and b+d > 0, use div_lt_div_iff. For the second part: (a+c)/(b+d) < c/d iff d(a+c) < c(b+d) iff da < cb iff bc - ad > 0. Use push_cast, field_simp, and nlinarith.
-/
theorem farey_neighbor_det (a b c d : ℤ) (hab : 0 < b) (hcd : 0 < d)
    (hneighbor : b * c - a * d = 1) :
    (a : ℚ) / b < (a + c : ℚ) / (b + d) ∧
    (a + c : ℚ) / (b + d) < (c : ℚ) / d := by
      exact ⟨ by rw [ div_lt_div_iff₀ ] <;> norm_cast <;> nlinarith, by rw [ div_lt_div_iff₀ ] <;> norm_cast <;> nlinarith ⟩

/-! ## Section 6: Gaussian Integers — The 2D Decoder Ring

If ℚ decodes the circle S¹, then ℚ[i] (Gaussian rationals) decode the
entire plane. Every Gaussian integer a + bi determines:
- A lattice point (a, b) ∈ ℤ²
- A norm a² + b² (sum of two squares!)
- A Pythagorean triple via (a² - b², 2ab, a² + b²)

**The Gaussian integers are the 2D version of the decoder.** -/

/-- The norm of a Gaussian integer pair -/
def gaussNorm (a b : ℤ) : ℤ := a^2 + b^2

/-
PROBLEM
**THEOREM 8 (Multiplicativity of Norms = Brahmagupta-Fibonacci Identity)**:
    The product of two sums of squares is a sum of squares.
    This is the algebraic heart of the decoder — norms are multiplicative.

PROVIDED SOLUTION
Unfold gaussNorm and use ring.
-/
theorem brahmagupta_fibonacci (a₁ b₁ a₂ b₂ : ℤ) :
    gaussNorm a₁ b₁ * gaussNorm a₂ b₂ =
    gaussNorm (a₁ * a₂ - b₁ * b₂) (a₁ * b₂ + b₁ * a₂) := by
      unfold gaussNorm; ring;

/-
PROBLEM
**THEOREM 9 (Norm Multiplicativity, alternate form)**:
    Same identity, other sign choice — corresponding to conjugation.

PROVIDED SOLUTION
Unfold gaussNorm and use ring.
-/
theorem brahmagupta_fibonacci' (a₁ b₁ a₂ b₂ : ℤ) :
    gaussNorm a₁ b₁ * gaussNorm a₂ b₂ =
    gaussNorm (a₁ * a₂ + b₁ * b₂) (a₁ * b₂ - b₁ * a₂) := by
      unfold gaussNorm; ring;
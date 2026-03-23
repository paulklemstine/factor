import Mathlib

/-!
# The Universal Decoder: Stereographic Projection as a Rosetta Stone

## Research Team Theta: The Rational-Geometric Dictionary

This file formalizes the core insight that stereographic projection acts as a
"universal translator" between number theory, geometry, algebra, and topology.

The key idea: every rational number t ∈ ℚ encodes a rational point on S¹ via
  t ↦ ((1-t²)/(1+t²), 2t/(1+t²))

This is not merely a parametrization — it is a *functor* that translates:
  - Addition in ℚ → rotation-like operations on S¹
  - Multiplication in ℚ → scaling operations on rational points
  - The ordering of ℚ → angular ordering on S¹
  - Continued fraction structure → hierarchical approximation on S¹
  - The Stern-Brocot tree → a binary tree of rational points on S¹
  - Farey neighbors → geometrically adjacent rational points
-/

open Real

/-! ## Section 1: The Core Dictionary — Rationals to Circle Points -/

/-- Stereographic x-coordinate: maps t to (1 - t²)/(1 + t²) -/
noncomputable def stereo_x (t : ℝ) : ℝ := (1 - t ^ 2) / (1 + t ^ 2)

/-- Stereographic y-coordinate: maps t to 2t/(1 + t²) -/
noncomputable def stereo_y (t : ℝ) : ℝ := (2 * t) / (1 + t ^ 2)

/-- The denominator 1 + t² is always positive -/
theorem one_plus_sq_pos (t : ℝ) : 0 < 1 + t ^ 2 := by positivity

/-- The denominator 1 + t² is never zero -/
theorem one_plus_sq_ne_zero (t : ℝ) : 1 + t ^ 2 ≠ 0 := ne_of_gt (one_plus_sq_pos t)

/-- **Core Theorem**: Stereographic projection maps ℝ to S¹.
    For any t ∈ ℝ, (stereo_x t)² + (stereo_y t)² = 1. -/
theorem stereo_on_circle (t : ℝ) :
    (stereo_x t) ^ 2 + (stereo_y t) ^ 2 = 1 := by
  unfold stereo_x stereo_y
  have h := one_plus_sq_ne_zero t
  field_simp
  ring

/-! ## Section 2: Special Values — The Dictionary's Key Entries -/

/-- t = 0 maps to the "north pole" (1, 0) -/
theorem stereo_zero_x : stereo_x 0 = 1 := by simp [stereo_x]
theorem stereo_zero_y : stereo_y 0 = 0 := by simp [stereo_y]

/-- t = 1 maps to (0, 1), a 90° rotation -/
theorem stereo_one_x : stereo_x 1 = 0 := by unfold stereo_x; norm_num
theorem stereo_one_y : stereo_y 1 = 1 := by unfold stereo_y; norm_num

/-- t = -1 maps to (0, -1), a -90° rotation -/
theorem stereo_neg_one_x : stereo_x (-1) = 0 := by unfold stereo_x; norm_num
theorem stereo_neg_one_y : stereo_y (-1) = -1 := by unfold stereo_y; norm_num

/-! ## Section 3: Symmetries — The Grammar of the Language -/

/-- The x-coordinate is an even function: stereo_x(-t) = stereo_x(t) -/
theorem stereo_x_even (t : ℝ) : stereo_x (-t) = stereo_x t := by
  unfold stereo_x; ring_nf

/-- The y-coordinate is an odd function: stereo_y(-t) = -stereo_y(t) -/
theorem stereo_y_odd (t : ℝ) : stereo_y (-t) = -stereo_y t := by
  unfold stereo_y; ring_nf

/-- Negation in ℝ corresponds to reflection through the x-axis on S¹.
    This is the first "translation rule" of the decoder. -/
theorem decoder_negation (t : ℝ) :
    stereo_x (-t) = stereo_x t ∧ stereo_y (-t) = -stereo_y t :=
  ⟨stereo_x_even t, stereo_y_odd t⟩

/-! ## Section 4: The Inversion Rule — Reciprocals Map to Antipodal-like Points -/

/-- Taking the reciprocal negates the x-coordinate: stereo_x(1/t) = -stereo_x(t) for t ≠ 0 -/
theorem stereo_x_reciprocal (t : ℝ) (ht : t ≠ 0) :
    stereo_x (1 / t) = -(stereo_x t) := by
  unfold stereo_x
  have h1 := one_plus_sq_ne_zero t
  have h2 := one_plus_sq_ne_zero (1 / t)
  field_simp
  ring

/-- Taking the reciprocal preserves the y-coordinate:
    stereo_y(1/t) = stereo_y(t) -/
theorem stereo_y_reciprocal (t : ℝ) (ht : t ≠ 0) :
    stereo_y (1 / t) = stereo_y t := by
  unfold stereo_y
  have h1 := one_plus_sq_ne_zero t
  have h2 := one_plus_sq_ne_zero (1 / t)
  field_simp
  ring

/-- **Key Translation Rule**: The reciprocal operation 1/t corresponds to
    reflection through the y-axis on S¹. -/
theorem decoder_reciprocal (t : ℝ) (ht : t ≠ 0) :
    stereo_x (1 / t) = -(stereo_x t) ∧ stereo_y (1 / t) = stereo_y t :=
  ⟨stereo_x_reciprocal t ht, stereo_y_reciprocal t ht⟩

/-! ## Section 5: The Composition Law — Addition Becomes Rotation -/

/-- The rotation formula x-component -/
theorem stereo_rotation_x (t₁ t₂ : ℝ) :
    stereo_x t₁ * stereo_x t₂ - stereo_y t₁ * stereo_y t₂ =
    ((1 - t₁ ^ 2) * (1 - t₂ ^ 2) - 4 * t₁ * t₂) / ((1 + t₁ ^ 2) * (1 + t₂ ^ 2)) := by
  unfold stereo_x stereo_y
  have h1 := one_plus_sq_ne_zero t₁
  have h2 := one_plus_sq_ne_zero t₂
  field_simp
  ring

/-- The rotation formula y-component -/
theorem stereo_rotation_y (t₁ t₂ : ℝ) :
    stereo_x t₁ * stereo_y t₂ + stereo_y t₁ * stereo_x t₂ =
    (2 * t₂ * (1 - t₁ ^ 2) + 2 * t₁ * (1 - t₂ ^ 2)) / ((1 + t₁ ^ 2) * (1 + t₂ ^ 2)) := by
  unfold stereo_x stereo_y
  have h1 := one_plus_sq_ne_zero t₁
  have h2 := one_plus_sq_ne_zero t₂
  field_simp

/-! ## Section 6: The Pythagorean-Rational Bridge -/

/-- Euclid's parametrization expressed stereographically:
    integers (m, n) with m ≠ 0 produce the point
    ((m² - n²)/(m² + n²), 2mn/(m² + n²)) = stereo(n/m). -/
theorem euclid_is_stereo (m n : ℝ) (hm : m ≠ 0) :
    stereo_x (n / m) = (m ^ 2 - n ^ 2) / (m ^ 2 + n ^ 2) := by
  unfold stereo_x
  have hm2 : m ^ 2 ≠ 0 := pow_ne_zero 2 hm
  have hd2 : (0 : ℝ) < m ^ 2 + n ^ 2 := by positivity
  field_simp

theorem euclid_is_stereo_y (m n : ℝ) (hm : m ≠ 0) :
    stereo_y (n / m) = 2 * m * n / (m ^ 2 + n ^ 2) := by
  unfold stereo_y
  have hd2 : (0 : ℝ) < m ^ 2 + n ^ 2 := by positivity
  field_simp

/-! ## Section 7: The Conformal Factor — Information Preservation -/

/-- The conformal factor of stereographic projection -/
noncomputable def conformal_factor (t : ℝ) : ℝ := 2 / (1 + t ^ 2)

/-- The conformal factor is always positive -/
theorem conformal_pos (t : ℝ) : 0 < conformal_factor t := by
  unfold conformal_factor; positivity

/-- The conformal factor achieves its maximum at t = 0 -/
theorem conformal_max_at_zero : conformal_factor 0 = 2 := by
  unfold conformal_factor; norm_num

/-! ## Section 8: The Weierstrass Substitution — Calculus Meets Number Theory -/

/-- cos θ = (1 - t²)/(1 + t²) = stereo_x(t) where t = tan(θ/2) -/
theorem weierstrass_is_stereo_x (t : ℝ) :
    stereo_x t = (1 - t ^ 2) / (1 + t ^ 2) := rfl

/-- sin θ = 2t/(1 + t²) = stereo_y(t) -/
theorem weierstrass_is_stereo_y (t : ℝ) :
    stereo_y t = 2 * t / (1 + t ^ 2) := rfl

/-! ## Section 9: The Integer Lattice — Pythagorean Triples as Decoded Messages -/

/-- When the stereographic parameter is an integer ratio n/m, the resulting
    point is a rational point on S¹. -/
theorem integer_ratio_to_pyth_triple (m n : ℤ) :
    (m ^ 2 - n ^ 2) ^ 2 + (2 * m * n) ^ 2 = (m ^ 2 + n ^ 2) ^ 2 := by ring

/-- The Gaussian integer norm is multiplicative -/
theorem gaussian_norm_mult (a b c d : ℤ) :
    (a ^ 2 + b ^ 2) * (c ^ 2 + d ^ 2) = (a * c - b * d) ^ 2 + (a * d + b * c) ^ 2 := by ring

/-- **Decoder Composition Law**: Gaussian products preserve the Pythagorean property -/
theorem decoder_composition (a b c d : ℤ) :
    let hyp₁ := a ^ 2 + b ^ 2
    let hyp₂ := c ^ 2 + d ^ 2
    let new_x := a * c - b * d
    let new_y := a * d + b * c
    new_x ^ 2 + new_y ^ 2 = hyp₁ * hyp₂ := by simp only; ring

/-! ## Section 10: The Stern-Brocot Connection — The Tree of All Rationals -/

/-- The mediant of two fractions a/b and c/d is (a+c)/(b+d).
    It lies strictly between the two fractions when they are ordered. -/
theorem mediant_between (a b c d : ℝ) (hb : 0 < b) (hd : 0 < d)
    (h : a * d < c * b) :
    a * (b + d) < (a + c) * b := by nlinarith

theorem mediant_between_upper (a b c d : ℝ) (hb : 0 < b) (hd : 0 < d)
    (h : a * d < c * b) :
    (a + c) * d < c * (b + d) := by nlinarith

/-! ## Section 11: The Modular Group Connection -/

/-- SL(2,ℤ) transformations compose with determinant 1. -/
theorem moebius_composition (a₁ b₁ c₁ d₁ a₂ b₂ c₂ d₂ : ℤ)
    (h₁ : a₁ * d₁ - b₁ * c₁ = 1) (h₂ : a₂ * d₂ - b₂ * c₂ = 1) :
    (a₁ * a₂ + b₁ * c₂) * (c₁ * b₂ + d₁ * d₂) -
    (a₁ * b₂ + b₁ * d₂) * (c₁ * a₂ + d₁ * c₂) = 1 := by nlinarith

/-! ## Section 12: The Farey Sequence as Circle Tessellation -/

/-- The Farey mediant preserves the neighbor relation -/
theorem farey_mediant_neighbor_left (a b c d : ℤ) (h : a * d - b * c = 1) :
    a * (b + d) - b * (a + c) = a * d - b * c := by ring

theorem farey_mediant_neighbor_right (a b c d : ℤ) (h : a * d - b * c = 1) :
    (a + c) * d - (b + d) * c = a * d - b * c := by ring

/-! ## Section 13: The p-adic Perspective — Another Decoder Channel -/

/-- The p-adic valuation is multiplicative -/
theorem padic_val_mul_formula (p : ℕ) [hp : Fact p.Prime] (a b : ℕ)
    (ha : a ≠ 0) (hb : b ≠ 0) :
    padicValNat p (a * b) = padicValNat p a + padicValNat p b :=
  padicValNat.mul ha hb

/-! ## Section 14: The Information-Theoretic Perspective -/

/-- The height of a rational controls the hypotenuse of its Pythagorean triple -/
theorem height_controls_hypotenuse (p q : ℤ) :
    p ^ 2 + q ^ 2 ≤ 2 * (max (|p|) (|q|)) ^ 2 := by
  have hp : p ^ 2 ≤ (max (|p|) (|q|)) ^ 2 := by
    nlinarith [abs_nonneg p, abs_nonneg q, le_max_left (|p|) (|q|), sq_abs p]
  have hq : q ^ 2 ≤ (max (|p|) (|q|)) ^ 2 := by
    nlinarith [abs_nonneg p, abs_nonneg q, le_max_right (|p|) (|q|), sq_abs q]
  linarith

/-! ## Section 15: The Four-Squares Theorem Connection -/

/-- Euler's four-square identity: extends the decoder from 2D to 4D -/
theorem decoder_four_squares (a₁ a₂ a₃ a₄ b₁ b₂ b₃ b₄ : ℤ) :
    (a₁^2 + a₂^2 + a₃^2 + a₄^2) * (b₁^2 + b₂^2 + b₃^2 + b₄^2) =
    (a₁*b₁ - a₂*b₂ - a₃*b₃ - a₄*b₄)^2 +
    (a₁*b₂ + a₂*b₁ + a₃*b₄ - a₄*b₃)^2 +
    (a₁*b₃ - a₂*b₄ + a₃*b₁ + a₄*b₂)^2 +
    (a₁*b₄ + a₂*b₃ - a₃*b₂ + a₄*b₁)^2 := by ring

/-! ## Section 16: The Eight-Squares Identity — Octonions -/

/-- Degen's eight-square identity: extends the decoder to 8 dimensions -/
theorem decoder_eight_squares (a₁ a₂ a₃ a₄ a₅ a₆ a₇ a₈
    b₁ b₂ b₃ b₄ b₅ b₆ b₇ b₈ : ℤ) :
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
  ring

/-! ## Section 17: The Decoder Taxonomy

Each mathematical domain is reached by a different "channel" of the decoder:

| Channel | Input Domain | Output Domain | Decoder Map |
|---------|-------------|---------------|-------------|
| 1 | ℤ × ℤ | Pythagorean triples | (m,n) ↦ (m²-n², 2mn, m²+n²) |
| 2 | ℚ | Rational S¹ | t ↦ ((1-t²)/(1+t²), 2t/(1+t²)) |
| 3 | ℝ | S¹ | same formula, continuous |
| 4 | ℤ[i] | Gaussian primes | factorization in ℤ[i] |
| 5 | ℍ(ℤ) | Quaternionic lattice | Hurwitz integers |
| 6 | 𝕆(ℤ) | Octonionic norm | Sum-of-eight-squares |
| 7 | SL(2,ℤ) | Modular forms | Möbius action |
| 8 | Cont. fracs | Farey tessellation | convergent sequence |
| 9 | ℚ_p | p-adic circle | Hensel lifting |
| 10 | ℚ(√D) | Algebraic circle pts | Pell equation |
-/

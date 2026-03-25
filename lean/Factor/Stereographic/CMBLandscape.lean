import Mathlib

/-!
# CMB Landscape: Pythagorean Energy, Stereographic Projection, and Spherical Distributions

This file formalizes the key mathematical results from our exploration of:
1. Energy density of Pythagorean triples
2. The stereographic-Pythagorean correspondence
3. Properties of the inverse stereographic projection of integer lattices

## Main Results

* `pythagorean_energy_density_bound` — For any Pythagorean triple, the energy density
  ab/(2c²) is bounded above by 1/4.
* `stereo_pyth_correspondence` — The Pythagorean rational point equals the inverse
  stereographic image of n/m.
* `inverse_stereo_on_sphere` — The inverse stereographic projection maps to the unit sphere.
* `energy_density_345` — The energy density of (3,4,5) is 6/25.
* `most_energy_rich_in_range` — (696, 697, 985) has higher energy density than (3,4,5).
-/

open Real

/-! ## Section 1: Pythagorean Energy Density -/

/-- The energy density of a Pythagorean triple (a, b, c) is ab/(2c²). -/
noncomputable def pythagorean_energy_density (a b c : ℝ) : ℝ := a * b / (2 * c ^ 2)

/-
PROBLEM
For any Pythagorean triple with c > 0, the energy density ab/(2c²) ≤ 1/4.

This follows from AM-GM: a² + b² = c² implies ab ≤ (a² + b²)/2 = c²/2,
hence ab/(2c²) ≤ 1/4.

PROVIDED SOLUTION
Unfold pythagorean_energy_density. By AM-GM, 2ab ≤ a² + b² = c², so ab ≤ c²/2, hence ab/(2c²) ≤ 1/4. Use nlinarith with the AM-GM fact (a-b)² ≥ 0, which gives a²+b² ≥ 2ab.
-/
theorem pythagorean_energy_density_bound (a b c : ℝ) (hc : c ≠ 0)
    (hpyth : a ^ 2 + b ^ 2 = c ^ 2) :
    pythagorean_energy_density a b c ≤ 1 / 4 := by
  rw [ pythagorean_energy_density ] ; rw [ div_le_iff₀ ] <;> nlinarith [ sq_nonneg ( a - b ), mul_self_pos.2 hc ] ;

/-
PROBLEM
The energy density of (3, 4, 5) is 6/25.

PROVIDED SOLUTION
Unfold pythagorean_energy_density and compute: 3*4/(2*5²) = 12/50 = 6/25. Use norm_num.
-/
theorem energy_density_345 :
    pythagorean_energy_density 3 4 5 = 6 / 25 := by
  unfold pythagorean_energy_density; norm_num;

/-
PROBLEM
(696, 697, 985) is a Pythagorean triple.

PROVIDED SOLUTION
Compute: 696² + 697² = 484416 + 485809 = 970225 = 985². Use norm_num or decide.
-/
theorem pythagorean_696_697_985 : (696 : ℤ) ^ 2 + 697 ^ 2 = 985 ^ 2 := by
  decide +kernel

/-
PROBLEM
The energy density of (696, 697, 985) exceeds that of (3, 4, 5),
    making it "more energy-rich".

PROVIDED SOLUTION
Unfold pythagorean_energy_density. Need 3*4/(2*25) < 696*697/(2*985²). That is 12/50 < 485112/1940450. Compute: 12/50 = 0.24 and 485112/1940450 ≈ 0.24999.... Use norm_num.
-/
theorem most_energy_rich_comparison :
    pythagorean_energy_density 3 4 5 < pythagorean_energy_density 696 697 985 := by
  unfold pythagorean_energy_density; norm_num;

/-! ## Section 2: Inverse Stereographic Projection -/

/-- The inverse stereographic projection from ℝ² to S² (projecting from the north pole).
    Maps (x, y) to (2x/(1+x²+y²), 2y/(1+x²+y²), (x²+y²-1)/(1+x²+y²)). -/
noncomputable def inverse_stereo (x y : ℝ) : ℝ × ℝ × ℝ :=
  let r2 := x ^ 2 + y ^ 2
  let denom := 1 + r2
  (2 * x / denom, 2 * y / denom, (r2 - 1) / denom)

/-
PROBLEM
The inverse stereographic projection maps to the unit sphere:
    X² + Y² + Z² = 1.

PROVIDED SOLUTION
Unfold inverse_stereo. Need to show (2x/d)² + (2y/d)² + ((r²-1)/d)² = 1 where d = 1+r², r² = x²+y². Numerator: 4x² + 4y² + (r²-1)² = 4r² + r⁴ - 2r² + 1 = r⁴ + 2r² + 1 = (r²+1)² = d². So ratio is d²/d² = 1. Use field_simp then ring or nlinarith.
-/
theorem inverse_stereo_on_sphere (x y : ℝ) :
    let p := inverse_stereo x y
    p.1 ^ 2 + p.2.1 ^ 2 + p.2.2 ^ 2 = 1 := by
  -- Let's unfold the definition of `inverse_stereo`.
  unfold inverse_stereo;
  field_simp
  ring

/-
PROBLEM
The origin maps to the south pole under inverse stereographic projection.

PROVIDED SOLUTION
Unfold inverse_stereo and compute with simp/norm_num.
-/
theorem inverse_stereo_origin : inverse_stereo 0 0 = (0, 0, -1) := by
  unfold inverse_stereo; norm_num;

/-! ## Section 3: The Stereographic-Pythagorean Correspondence -/

/-- The 1D inverse stereographic projection from ℝ to S¹:
    t ↦ ((1-t²)/(1+t²), 2t/(1+t²)). -/
noncomputable def inverse_stereo_1d (t : ℝ) : ℝ × ℝ :=
  ((1 - t ^ 2) / (1 + t ^ 2), 2 * t / (1 + t ^ 2))

/-- The Pythagorean rational point from Euclid parameters (m, n):
    ((m²-n²)/(m²+n²), 2mn/(m²+n²)). -/
noncomputable def pythagorean_rational_point (m n : ℝ) : ℝ × ℝ :=
  ((m ^ 2 - n ^ 2) / (m ^ 2 + n ^ 2), 2 * m * n / (m ^ 2 + n ^ 2))

/-
PROBLEM
**The Stereographic-Pythagorean Correspondence**:
    The Pythagorean rational point from parameters (m, n) with m ≠ 0 equals
    the inverse stereographic projection of t = n/m.

    This means: every primitive Pythagorean triple corresponds to a rational
    point on S¹ obtained by inverse stereographic projection of a rational number.

PROVIDED SOLUTION
Unfold both definitions. pythagorean_rational_point gives ((m²-n²)/(m²+n²), 2mn/(m²+n²)). inverse_stereo_1d(n/m) gives ((1-(n/m)²)/(1+(n/m)²), 2(n/m)/(1+(n/m)²)). Multiply numerator and denominator by m²: ((m²-n²)/(m²+n²), 2mn/(m²+n²)). Use field_simp then ring.
-/
theorem stereo_pyth_correspondence (m n : ℝ) (hm : m ≠ 0) (hsum : m ^ 2 + n ^ 2 ≠ 0) :
    pythagorean_rational_point m n = inverse_stereo_1d (n / m) := by
  unfold pythagorean_rational_point inverse_stereo_1d;
  grind

/-! ## Section 4: Energy Density Analysis -/

/-- The energy density in Euclid parameters: E(m,n) = mn(m²-n²)/(m²+n²)².
    This is the fundamental formula connecting Pythagorean energetics to
    the Euclid parametrization. -/
noncomputable def energy_euclid (m n : ℝ) : ℝ :=
  m * n * (m ^ 2 - n ^ 2) / (m ^ 2 + n ^ 2) ^ 2

/-- The energy density in terms of the ratio t = n/m is E(t) = t(1-t²)/(1+t²)²,
    which reaches its maximum at t = √2 - 1 (equivalently m/n = 1 + √2, the silver ratio). -/
noncomputable def energy_ratio (t : ℝ) : ℝ :=
  t * (1 - t ^ 2) / (1 + t ^ 2) ^ 2

/-
PROBLEM
The energy function in Euclid parameters equals the ratio form when t = n/m.

PROVIDED SOLUTION
Unfold energy_euclid and energy_ratio. This is an algebraic identity. Use field_simp then ring.
-/
theorem energy_euclid_eq_ratio (m n : ℝ) (hm : m ≠ 0) (hsum : m ^ 2 + n ^ 2 ≠ 0) :
    energy_euclid m n = m ^ 4 * energy_ratio (n / m) / (m ^ 2 + n ^ 2) ^ 2 *
      (m ^ 2 + n ^ 2) ^ 2 / m ^ 4 := by
  unfold energy_euclid energy_ratio; ring;
  -- Combine and simplify the terms in the equation.
  field_simp
  ring

/-
PROBLEM
AM-GM gives us that for non-negative reals, 2ab ≤ a² + b².

PROVIDED SOLUTION
This is equivalent to 0 ≤ (a-b)². Use nlinarith [sq_nonneg (a - b)].
-/
theorem two_mul_le_sq_add_sq (a b : ℝ) : 2 * a * b ≤ a ^ 2 + b ^ 2 := by
  linarith [ sq_nonneg ( a - b ) ]

/-! ## Section 5: The Silver Ratio Connection -/

/-- The silver ratio σ = 1 + √2 ≈ 2.414... -/
noncomputable def silver_ratio : ℝ := 1 + Real.sqrt 2

/-- The optimal ratio for maximum energy density is t* = √2 - 1 = 1/σ. -/
noncomputable def optimal_ratio : ℝ := Real.sqrt 2 - 1

/-
PROBLEM
The optimal ratio is the reciprocal of the silver ratio.

PROVIDED SOLUTION
Unfold optimal_ratio and silver_ratio. Need (√2 - 1)(1 + √2) = 1. This is a difference of squares: (√2)² - 1² = 2 - 1 = 1. Use ring-like reasoning with Real.sq_sqrt (by norm_num : (2:ℝ) ≥ 0) and nlinarith.
-/
theorem optimal_ratio_eq_inv_silver :
    optimal_ratio * silver_ratio = 1 := by
  exact show ( Real.sqrt 2 - 1 ) * ( 1 + Real.sqrt 2 ) = 1 from by ring_nf; norm_num;
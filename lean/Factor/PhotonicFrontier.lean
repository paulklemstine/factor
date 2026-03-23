import Mathlib

/-!
# Photonic Frontier: Beyond the Light Cone

## Machine-Verified Theorems from the Photonic Frontier Research Collective

Building on the 42 theorems of `LightConeTheory.lean`, this file explores
**new mathematical territory** at the intersection of Minkowski geometry,
hyperbolic geometry, Möbius transformations, and the arithmetic of light.

## Research Teams

- **Team Φ (Hyperbolic Geometry)**: The hyperboloid model of hyperbolic space
  lives *inside* the light cone. We prove that the unit hyperboloid is preserved
  by Lorentz boosts and establish the hyperbolic distance formula.

- **Team Ψ (Möbius-Lorentz Correspondence)**: Lorentz boosts act as Möbius
  transformations on the celestial circle. We formalize this correspondence
  and prove cross-ratio invariance.

- **Team Ω (Spatial Symmetry & Duality)**: Spatial rotations in the (a,b) plane
  form the compact part of the Lorentz group. Combined with boosts, they generate
  the full connected component SO⁺(2,1).

- **Team Σ (Arithmetic of Light)**: The Gaussian integer norm equals spatial
  momentum squared. Norm multiplicativity gives photon momentum composition.

- **Team Λ (Conformal Structure)**: Inversions, dilations, and special conformal
  transformations extend the Lorentz group to the conformal group.

- **Team Ξ (Light Cone Quantization)**: Discrete structure of integer null vectors,
  primitive photons, and counting functions.

## Summary

53 new machine-verified theorems. 0 sorry.
-/

open Real Finset BigOperators

noncomputable section

/-! ═══════════════════════════════════════════════════════════════════════
    DEFINITIONS (shared across all teams)
    ═══════════════════════════════════════════════════════════════════════ -/

/-- The Minkowski quadratic form Q(a,b,c) = a² + b² - c² in (2+1)d. -/
def Q (a b c : ℝ) : ℝ := a ^ 2 + b ^ 2 - c ^ 2

/-- The Minkowski bilinear form ⟨u,v⟩_η = a₁a₂ + b₁b₂ - c₁c₂. -/
def eta (a₁ b₁ c₁ a₂ b₂ c₂ : ℝ) : ℝ := a₁ * a₂ + b₁ * b₂ - c₁ * c₂

/-- A vector is null (light-like) if Q = 0. -/
def IsNull (a b c : ℝ) : Prop := Q a b c = 0

/-- A vector is timelike if Q < 0. -/
def IsTimelike (a b c : ℝ) : Prop := Q a b c < 0

/-- A vector is spacelike if Q > 0. -/
def IsSpacelike (a b c : ℝ) : Prop := Q a b c > 0

/-- Spatial rotation in the (a,b) plane by angle θ. -/
def spatialRotation (a b c θ : ℝ) : ℝ × ℝ × ℝ :=
  (a * cos θ - b * sin θ, a * sin θ + b * cos θ, c)

/-- Lorentz boost in the a-c plane with rapidity φ. -/
def boost (a b c φ : ℝ) : ℝ × ℝ × ℝ :=
  (a * cosh φ + c * sinh φ, b, a * sinh φ + c * cosh φ)

/-! ═══════════════════════════════════════════════════════════════════════
    TEAM Φ: HYPERBOLIC GEOMETRY INSIDE THE LIGHT CONE
    ═══════════════════════════════════════════════════════════════════════

    The unit hyperboloid H² = {(a,b,c) : Q(a,b,c) = -1, c > 0} is the
    **hyperboloid model** of the hyperbolic plane. It sits inside the
    future light cone. Light rays are the "points at infinity" of
    hyperbolic space.
-/

/-- The unit hyperboloid: Q = -1, c > 0. This is the hyperboloid model
    of the hyperbolic plane H². -/
def OnHyperboloid (a b c : ℝ) : Prop := Q a b c = -1 ∧ 0 < c

/-- **Theorem Φ.1**: The point (0, 0, 1) lies on the unit hyperboloid —
    it is the "origin" of hyperbolic space. -/
theorem hyperboloid_origin : OnHyperboloid 0 0 1 := by
  simp [OnHyperboloid, Q]

/-- **Theorem Φ.2**: Lorentz boosts preserve the quadratic form Q. -/
theorem boost_preserves_Q (a b c φ : ℝ) :
    Q (boost a b c φ).1 (boost a b c φ).2.1 (boost a b c φ).2.2 = Q a b c := by
  simp [boost, Q]
  have h := Real.cosh_sq_sub_sinh_sq φ
  nlinarith [sq_nonneg (a * cosh φ + c * sinh φ),
             sq_nonneg (a * sinh φ + c * cosh φ)]

/-- **Theorem Φ.3**: Lorentz boosts preserve the hyperboloid Q = -1. -/
theorem boost_preserves_hyperboloid_Q (a b c φ : ℝ)
    (h : Q a b c = -1) :
    Q (boost a b c φ).1 (boost a b c φ).2.1 (boost a b c φ).2.2 = -1 := by
  rw [boost_preserves_Q]; exact h

/-- **Theorem Φ.4**: The boosted origin lies on the hyperboloid. -/
theorem boosted_origin_on_hyperboloid (φ : ℝ) :
    OnHyperboloid (sinh φ) 0 (cosh φ) := by
  refine ⟨?_, Real.cosh_pos φ⟩
  simp [Q]
  have h := Real.cosh_sq_sub_sinh_sq φ
  linarith

/-- **Theorem Φ.5**: The hyperboloid is "inside" the future light cone:
    if (a,b,c) is on H², then c² = a² + b² + 1. -/
theorem hyperboloid_inside_light_cone (a b c : ℝ) (h : OnHyperboloid a b c) :
    c ^ 2 = a ^ 2 + b ^ 2 + 1 := by
  obtain ⟨hQ, _⟩ := h
  simp [Q] at hQ; linarith

/-- **Theorem Φ.6**: The hyperbolic distance from the origin to boost(origin,φ):
    -eta((0,0,1), (sinh φ, 0, cosh φ)) = cosh φ. -/
theorem hyperbolic_distance_base (φ : ℝ) :
    -(eta 0 0 1 (sinh φ) 0 (cosh φ)) = cosh φ := by
  simp [eta]

/-- **Theorem Φ.7**: The Minkowski inner product of a hyperboloid point
    with itself equals -1. -/
theorem hyperboloid_self_inner (a b c : ℝ) (h : OnHyperboloid a b c) :
    eta a b c a b c = -1 := by
  obtain ⟨hQ, _⟩ := h
  simp [eta, Q] at *; nlinarith

theorem hyperboloid_c_ge_one (a b c : ℝ) (h : OnHyperboloid a b c) :
    1 ≤ c := by
  -- By definition of $OnHyperboloid$, we know that $Q a b c = -1$ and $0 < c$.
  obtain ⟨hQ, hc⟩ := h
  have hc_sq : c ^ 2 = a ^ 2 + b ^ 2 + 1 := by
    unfold Q at hQ; linarith;
  have hc_ge_one : 1 ≤ c := by
    nlinarith [ sq_nonneg a, sq_nonneg b ]
  exact hc_ge_one

/-! ═══════════════════════════════════════════════════════════════════════
    TEAM Ψ: MÖBIUS-LORENTZ CORRESPONDENCE
    ═══════════════════════════════════════════════════════════════════════
-/

/-- A Möbius transformation (αt + β)/(γt + δ). -/
def mobius (α β γ δ t : ℝ) : ℝ := (α * t + β) / (γ * t + δ)

theorem mobius_composition (a₁ b₁ c₁ d₁ a₂ b₂ c₂ d₂ t : ℝ)
    (h1 : c₁ * mobius a₂ b₂ c₂ d₂ t + d₁ ≠ 0)
    (h2 : c₂ * t + d₂ ≠ 0) :
    mobius a₁ b₁ c₁ d₁ (mobius a₂ b₂ c₂ d₂ t) =
      mobius (a₁ * a₂ + b₁ * c₂) (a₁ * b₂ + b₁ * d₂)
             (c₁ * a₂ + d₁ * c₂) (c₁ * b₂ + d₁ * d₂) t := by
  unfold mobius; ring;
  grind

/-- **Theorem Ψ.2**: A Lorentz boost acts on the stereographic parameter
    as t ↦ e^φ · t (pure dilation). -/
theorem boost_is_dilation_on_celestial (φ t : ℝ) :
    (cosh φ + sinh φ) * t = exp φ * t := by
  congr 1; rw [cosh_eq, sinh_eq]; ring

/-- **Theorem Ψ.3**: The cross-ratio of four real numbers. -/
def crossRatio (a b c d : ℝ) : ℝ :=
  ((a - c) * (b - d)) / ((a - d) * (b - c))

theorem cross_ratio_dilation_invariant (a b c d k : ℝ)
    (h1 : (a - d) * (b - c) ≠ 0)
    (hk : k ≠ 0) :
    crossRatio (k * a) (k * b) (k * c) (k * d) = crossRatio a b c d := by
  unfold crossRatio; ring;
  grind

/-- **Theorem Ψ.5**: The identity Möbius transformation. -/
theorem mobius_identity (t : ℝ) : mobius 1 0 0 1 t = t := by
  simp [mobius]

/-- **Theorem Ψ.6**: Translation is a Möbius transformation. -/
theorem mobius_translation (s t : ℝ) : mobius 1 s 0 1 t = t + s := by
  simp [mobius]

/-! ═══════════════════════════════════════════════════════════════════════
    TEAM Ω: SPATIAL ROTATIONS & ELECTROMAGNETIC DUALITY
    ═══════════════════════════════════════════════════════════════════════
-/

/-- **Theorem Ω.1**: Spatial rotation preserves the Minkowski form. -/
theorem rotation_preserves_Q (a b c θ : ℝ) :
    Q (spatialRotation a b c θ).1 (spatialRotation a b c θ).2.1
      (spatialRotation a b c θ).2.2 = Q a b c := by
  simp [spatialRotation, Q]
  have h := Real.sin_sq_add_cos_sq θ
  nlinarith [sq_nonneg (a * cos θ - b * sin θ),
             sq_nonneg (a * sin θ + b * cos θ)]

/-- **Theorem Ω.2**: Spatial rotation preserves null vectors. -/
theorem rotation_preserves_null (a b c θ : ℝ) (h : IsNull a b c) :
    IsNull (spatialRotation a b c θ).1 (spatialRotation a b c θ).2.1
      (spatialRotation a b c θ).2.2 := by
  simp [IsNull] at *; rw [rotation_preserves_Q]; exact h

/-- **Theorem Ω.3**: Spatial rotation preserves the "energy" component c. -/
theorem rotation_preserves_energy (a b c θ : ℝ) :
    (spatialRotation a b c θ).2.2 = c := by
  simp [spatialRotation]

/-- **Theorem Ω.4**: Spatial rotation preserves the spatial momentum magnitude. -/
theorem rotation_preserves_spatial_momentum (a b c θ : ℝ) :
    (spatialRotation a b c θ).1 ^ 2 + (spatialRotation a b c θ).2.1 ^ 2 =
      a ^ 2 + b ^ 2 := by
  simp [spatialRotation]
  have h := Real.sin_sq_add_cos_sq θ
  nlinarith [sq_nonneg (a * cos θ - b * sin θ),
             sq_nonneg (a * sin θ + b * cos θ)]

/-- **Theorem Ω.5**: A full rotation by 2π is the identity. -/
theorem rotation_full_circle (a b c : ℝ) :
    spatialRotation a b c (2 * π) = (a, b, c) := by
  simp [spatialRotation, cos_two_pi, sin_two_pi]

/-- **Theorem Ω.6**: Rotation by 0 is the identity. -/
theorem rotation_zero (a b c : ℝ) :
    spatialRotation a b c 0 = (a, b, c) := by
  simp [spatialRotation]

/-- **Theorem Ω.7**: Rotation composition = angle addition. -/
theorem rotation_composition (a b c θ₁ θ₂ : ℝ) :
    let v₁ := spatialRotation a b c θ₁
    spatialRotation v₁.1 v₁.2.1 v₁.2.2 θ₂ = spatialRotation a b c (θ₁ + θ₂) := by
  simp [spatialRotation, cos_add, sin_add]
  constructor <;> ring

/-- **Theorem Ω.8**: Boost followed by rotation preserves Q. -/
theorem boost_rotation_preserves_Q (a b c φ θ : ℝ) :
    let v := boost a b c φ
    let w := spatialRotation v.1 v.2.1 v.2.2 θ
    Q w.1 w.2.1 w.2.2 = Q a b c := by
  simp only; rw [rotation_preserves_Q, boost_preserves_Q]

/-! ═══════════════════════════════════════════════════════════════════════
    TEAM Σ: ARITHMETIC OF LIGHT
    ═══════════════════════════════════════════════════════════════════════
-/

theorem gaussian_norm_multiplicative (a b c d : ℤ) :
    ((a : ℝ) ^ 2 + (b : ℝ) ^ 2) * ((c : ℝ) ^ 2 + (d : ℝ) ^ 2) =
      ((a * c - b * d : ℤ) : ℝ) ^ 2 + ((a * d + b * c : ℤ) : ℝ) ^ 2 := by
  push_cast; ring;

/-- **Theorem Σ.2**: Photon composition via Gaussian multiplication. -/
theorem photon_gaussian_composition (m n p q : ℤ) :
    let m' := m * p - n * q
    let n' := m * q + n * p
    m' ^ 2 + n' ^ 2 = (m ^ 2 + n ^ 2) * (p ^ 2 + q ^ 2) := by
  simp only; ring

/-- **Theorem Σ.3**: Euclid's formula gives null vectors. -/
theorem euclid_spatial_momentum (m n : ℤ) :
    (2 * m * n : ℤ) ^ 2 + (n ^ 2 - m ^ 2) ^ 2 = (m ^ 2 + n ^ 2) ^ 2 := by
  ring

/-- **Theorem Σ.4**: 5 = 1² + 2². -/
theorem five_is_sum_of_squares : (1 : ℤ) ^ 2 + 2 ^ 2 = 5 := by norm_num

/-- **Theorem Σ.5**: 13 = 2² + 3². -/
theorem thirteen_is_sum_of_squares : (2 : ℤ) ^ 2 + 3 ^ 2 = 13 := by norm_num

/-- **Theorem Σ.6**: Gaussian product (1+2i)(2+3i) = -4+7i, energy 65. -/
theorem gaussian_product_example :
    (1 * 2 - 2 * 3 : ℤ) ^ 2 + (1 * 3 + 2 * 2) ^ 2 = 5 * 13 := by norm_num

/-- **Theorem Σ.7**: The photon (56, 33, 65) from Gaussian composition. -/
theorem composed_photon_is_null :
    (56 : ℤ) ^ 2 + 33 ^ 2 = 65 ^ 2 := by norm_num

/-! ═══════════════════════════════════════════════════════════════════════
    TEAM Λ: CONFORMAL STRUCTURE & INVERSIONS
    ═══════════════════════════════════════════════════════════════════════
-/

/-- **Theorem Λ.1**: Dilation scales Q quadratically: Q(kv) = k²Q(v). -/
theorem dilation_scales_Q (a b c k : ℝ) :
    Q (k * a) (k * b) (k * c) = k ^ 2 * Q a b c := by
  simp [Q]; ring

/-- **Theorem Λ.2**: Dilation preserves null vectors. -/
theorem dilation_preserves_null (a b c k : ℝ) (h : IsNull a b c) :
    IsNull (k * a) (k * b) (k * c) := by
  simp [IsNull] at *; rw [dilation_scales_Q]; simp [h]

/-- **Theorem Λ.3**: Dilation by k > 0 preserves timelike character. -/
theorem dilation_preserves_timelike (a b c k : ℝ) (h : IsTimelike a b c) (hk : 0 < k) :
    IsTimelike (k * a) (k * b) (k * c) := by
  simp [IsTimelike] at *; rw [dilation_scales_Q]
  exact mul_neg_of_pos_of_neg (sq_pos_of_pos hk) h

/-- **Theorem Λ.4**: Kelvin inversion: Q(v/Q(v)) = 1/Q(v). -/
theorem kelvin_inversion_form (a b c : ℝ) (hQ : Q a b c ≠ 0) :
    Q (a / Q a b c) (b / Q a b c) (c / Q a b c) = 1 / Q a b c := by
  simp [Q] at *
  field_simp

theorem translation_Q (a₁ b₁ c₁ a₂ b₂ c₂ : ℝ) (t : ℝ) :
    Q (a₁ + t * a₂) (b₁ + t * b₂) (c₁ + t * c₂) =
      Q a₁ b₁ c₁ + 2 * t * eta a₁ b₁ c₁ a₂ b₂ c₂ + t ^ 2 * Q a₂ b₂ c₂ := by
  unfold Q eta; ring;

theorem null_translation_simplified (a₁ b₁ c₁ a₂ b₂ c₂ : ℝ) (t : ℝ)
    (hNull : IsNull a₂ b₂ c₂) :
    Q (a₁ + t * a₂) (b₁ + t * b₂) (c₁ + t * c₂) =
      Q a₁ b₁ c₁ + 2 * t * eta a₁ b₁ c₁ a₂ b₂ c₂ := by
  -- Substitute hNull into the translation_Q theorem to eliminate the t² term.
  rw [translation_Q]
  simp
  exact Or.inr hNull

/-! ═══════════════════════════════════════════════════════════════════════
    TEAM Ξ: LIGHT CONE QUANTIZATION & DISCRETE STRUCTURE
    ═══════════════════════════════════════════════════════════════════════
-/

/-- **Theorem Ξ.1**: Coprimality of (3,4,5). -/
theorem primitive_345 : Nat.Coprime 3 5 ∧ Nat.Coprime 4 5 := by
  constructor <;> decide

theorem energy_dominates_momentum (a b c : ℕ) (hpyth : a ^ 2 + b ^ 2 = c ^ 2)
    (_ha : 0 < a) (_hb : 0 < b) : a ≤ c ∧ b ≤ c := by
  exact ⟨ by nlinarith only [ hpyth ], by nlinarith only [ hpyth ] ⟩

/-- **Theorem Ξ.3**: 3² + 4² = 5². -/
theorem smallest_primitive_energy :
    (3 : ℕ) ^ 2 + 4 ^ 2 = 5 ^ 2 := by norm_num

theorem photon_energy_sum_bound (a₁ b₁ c₁ a₂ b₂ c₂ : ℝ)
    (h1 : IsNull a₁ b₁ c₁) (h2 : IsNull a₂ b₂ c₂)
    (hc1 : 0 < c₁) (hc2 : 0 < c₂) :
    (a₁ + a₂) ^ 2 + (b₁ + b₂) ^ 2 ≤ (c₁ + c₂) ^ 2 := by
  -- Since $a₁^2 + b₁^2 = c₁^2$ and $a₂^2 + b₂^2 = c₂^2$, we can substitute these into the inequality.
  have h_sub : a₁^2 + b₁^2 = c₁^2 ∧ a₂^2 + b₂^2 = c₂^2 := by
    exact ⟨ eq_of_sub_eq_zero h1, eq_of_sub_eq_zero h2 ⟩;
  -- By Cauchy-Schwarz inequality, we have $a₁a₂ + b₁b₂ \leq \sqrt{a₁^2 + b₁^2} \cdot \sqrt{a₂^2 + b₂^2}$.
  have h_cauchy_schwarz : a₁ * a₂ + b₁ * b₂ ≤ Real.sqrt (a₁^2 + b₁^2) * Real.sqrt (a₂^2 + b₂^2) := by
    rw [ ← Real.sqrt_mul <| by positivity ] ; exact Real.le_sqrt_of_sq_le <| by linarith [ sq_nonneg ( a₁ * b₂ - a₂ * b₁ ) ] ;
  rw [ h_sub.1, h_sub.2, Real.sqrt_sq hc1.le, Real.sqrt_sq hc2.le ] at h_cauchy_schwarz ; linarith

/-! ═══════════════════════════════════════════════════════════════════════
    SYNTHESIS: DEEP CONNECTIONS
    ═══════════════════════════════════════════════════════════════════════
-/

/-- **Synthesis 1**: Rotation-boost decomposition preserves Q. -/
theorem iwasawa_preserves_Q (a b c θ φ : ℝ) :
    let v := spatialRotation a b c θ
    let w := boost v.1 v.2.1 v.2.2 φ
    Q w.1 w.2.1 w.2.2 = Q a b c := by
  simp only; rw [boost_preserves_Q, rotation_preserves_Q]

/-- **Synthesis 2**: The boosted energy in a general direction. -/
theorem general_lorentz_transform (a b c θ φ : ℝ) :
    let v := spatialRotation a b c θ
    let w := boost v.1 v.2.1 v.2.2 φ
    w.2.2 = (a * cos θ - b * sin θ) * sinh φ + c * cosh φ := by
  simp [spatialRotation, boost]

/-- **Synthesis 3**: eta on the diagonal equals Q. -/
theorem eta_self_eq_Q (a b c : ℝ) :
    eta a b c a b c = Q a b c := by
  simp [eta, Q, sq]

/-- **Synthesis 4**: Every point on the celestial circle is null. -/
theorem celestial_angle_null (θ : ℝ) : IsNull (cos θ) (sin θ) 1 := by
  unfold IsNull Q; nlinarith [sin_sq_add_cos_sq θ]

/-- **Synthesis 5**: The photon orbit at radius r is null. -/
theorem photon_orbit_radius (r θ : ℝ) :
    IsNull (r * cos θ) (r * sin θ) r := by
  unfold IsNull Q; nlinarith [sin_sq_add_cos_sq θ, sq_nonneg r]

/-- **Synthesis 6**: Aberration formula — boosted photon energy. -/
theorem aberration_energy (θ φ : ℝ) :
    (boost (cos θ) (sin θ) 1 φ).2.2 = cos θ * sinh φ + cosh φ := by
  simp [boost]

/-- **Synthesis 7**: Forward blueshift: E' = e^φ. -/
theorem forward_blueshift (φ : ℝ) :
    cos 0 * sinh φ + cosh φ = exp φ := by
  simp [cos_zero, cosh_eq, sinh_eq]; ring

theorem backward_redshift (φ : ℝ) :
    cos π * sinh φ + cosh φ = exp (-φ) := by
  norm_num [ Real.sinh_eq, Real.cosh_eq ] ; ring;

theorem two_photon_invariant_mass (θ₁ θ₂ : ℝ) :
    -Q (cos θ₁ + cos θ₂) (sin θ₁ + sin θ₂) 2 = 2 * (1 - cos (θ₁ - θ₂)) := by
  unfold Q; rw [ Real.cos_sub ] ; nlinarith [ Real.sin_sq_add_cos_sq θ₁, Real.sin_sq_add_cos_sq θ₂ ] ;

/-- **Synthesis 10**: Head-on collision mass M² = 4. -/
theorem head_on_collision_mass :
    -Q (cos 0 + cos π) (sin 0 + sin π) 2 = 4 := by
  simp [Q, cos_zero, sin_zero, cos_pi, sin_pi]; ring

/-- **Synthesis 11**: Euclid(m,n) gives null vector with energy m² + n². -/
theorem crystallizer_gaussian_photon (m n : ℤ) :
    (2 * m * n) ^ 2 + (n ^ 2 - m ^ 2) ^ 2 = (m ^ 2 + n ^ 2) ^ 2 := by ring

/-- **Synthesis 12**: Right-moving null direction. -/
theorem null_direction_right : IsNull 1 0 1 := by
  simp [IsNull, Q]

/-- **Synthesis 13**: Left-moving null direction. -/
theorem null_direction_left : IsNull 1 0 (-1) := by
  simp [IsNull, Q]

theorem null_b_zero_classification (a c : ℝ) (h : IsNull a 0 c) :
    (∃ k : ℝ, a = k ∧ c = k) ∨ (∃ k : ℝ, a = k ∧ c = -k) := by
  cases eq_or_eq_neg_of_sq_eq_sq a c ( by unfold IsNull at h; norm_num [ Q ] at h; linarith ) <;> aesop

/-- **Synthesis 15**: Wigner rotation preserves Q. -/
theorem wigner_rotation_structure (a b c φ₁ θ φ₂ : ℝ) :
    let v := boost a b c φ₁
    let w := spatialRotation v.1 v.2.1 v.2.2 θ
    let u := boost w.1 w.2.1 w.2.2 φ₂
    Q u.1 u.2.1 u.2.2 = Q a b c := by
  simp only; rw [boost_preserves_Q, rotation_preserves_Q, boost_preserves_Q]

end
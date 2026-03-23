import Mathlib

/-!
# Light Cone Theory: New Properties and Theorems of Light

## From Pythagorean Triples to Null Vectors in Minkowski Space

This file formalizes a suite of new theorems discovered by our research team,
connecting the Intelligence Crystallizer's stereographic projection framework
to the physics of light through Minkowski geometry.

## Core Insight

The Pythagorean equation a² + b² = c² is *exactly* the light-like (null) condition
in (2+1)-dimensional Minkowski space with signature (+,+,-). A Pythagorean triple
is an integer point on the **light cone**. The Berggren matrices are **discrete
Lorentz transformations**. Stereographic projection is the **conformal map of the
celestial sphere** — the space of light ray directions.

## Main Results

### Part I: Light Cone Fundamentals
- `light_like_iff_pythagorean`: Light-like = Pythagorean condition
- `light_cone_is_cone`: The light cone is closed under scaling
- `light_like_self_orthogonal`: Null vectors are Minkowski-self-orthogonal
- `pyth_triple_is_light_like`: Every Pythagorean triple is a light-like vector
- `causal_classification`: Trichotomy of causal vectors

### Part II: Lorentz Invariance
- `lorentz_boost_preserves_form`: 2D Lorentz boost preserves Minkowski form
- `lorentz_boost_preserves_light_like`: Boosts map null → null
- `berggren_A/B/C_maps_light_to_light`: Berggren matrices map null → null
- `rapidity_composition`: Rapidities add under boost composition

### Part III: Celestial Sphere & Stereographic Projection
- `celestial_sphere_is_circle`: Cross-section of light cone at z=1 is S¹
- `inv_celestial_stereo_is_light_like`: Inverse stereo produces light-like vectors
- `conformal_factor_positive`: The conformal factor is positive

### Part IV: Photonic Crystallizer
- `crystallized_weight_on_light_cone`: Integer latent params → weight on light cone
- `photon_energy_momentum`: E² = p² for massless particles
- `doppler_factor_positive`: Doppler shift factor is always positive
- `doppler_is_exponential`: cosh φ + sinh φ = exp φ

### Part V: Algebraic Light
- `minkowski_polarization`: Polarization identity for the Minkowski form
- `sum_light_like_iff_orthogonal`: Sum of null vectors is null iff orthogonal
- `null_coordinates`: Light-cone coordinate change
- `photon_pair_to_timelike`: Two back-to-back photons form a massive particle

### Part VI: Crystallizer-Photon Dictionary
- `crystallizer_to_celestial`: Stereo map lands on the celestial sphere
- `crystallizer_loss_measures_photon_deviation`: Loss = 0 iff on integer light cone
- `finite_photons_bounded_energy`: Finitely many photons with bounded energy
-/

open Real Finset BigOperators Matrix

noncomputable section

/-! ## Part I: Light Cone Fundamentals -/

/-- The Minkowski quadratic form in (2+1) dimensions with signature (+,+,-).
    Q(a,b,c) = a² + b² - c². The light cone is Q = 0. -/
def minkowskiForm (a b c : ℝ) : ℝ := a ^ 2 + b ^ 2 - c ^ 2

/-- A vector is light-like (null) if it lies on the light cone: Q = 0. -/
def isLightLike (a b c : ℝ) : Prop := minkowskiForm a b c = 0

/-- A vector is timelike if Q < 0 (inside the light cone). -/
def isTimeLike (a b c : ℝ) : Prop := minkowskiForm a b c < 0

/-- A vector is spacelike if Q > 0 (outside the light cone). -/
def isSpaceLike (a b c : ℝ) : Prop := 0 < minkowskiForm a b c

/-- Light-like is equivalent to the Pythagorean condition a² + b² = c². -/
theorem light_like_iff_pythagorean (a b c : ℝ) :
    isLightLike a b c ↔ a ^ 2 + b ^ 2 = c ^ 2 := by
  simp [isLightLike, minkowskiForm]; constructor <;> intro h <;> linarith

/-- The light cone is a cone: if v is light-like, then kv is light-like. -/
theorem light_cone_is_cone (a b c k : ℝ) (h : isLightLike a b c) :
    isLightLike (k * a) (k * b) (k * c) := by
  simp [isLightLike, minkowskiForm] at *; nlinarith [sq_nonneg k]

/-- A light-like vector is Minkowski-self-orthogonal: ⟨v, v⟩_η = 0. -/
theorem light_like_self_orthogonal (a b c : ℝ) (h : isLightLike a b c) :
    a * a + b * b - c * c = 0 := by
  simp [isLightLike, minkowskiForm] at h; nlinarith

/-- Every Pythagorean triple defines a light-like vector. -/
theorem pyth_triple_is_light_like (a b c : ℤ) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    isLightLike (a : ℝ) (b : ℝ) (c : ℝ) := by
  rw [light_like_iff_pythagorean]; exact_mod_cast h

/-- The origin is (trivially) light-like. -/
theorem origin_is_light_like : isLightLike 0 0 0 := by
  simp [isLightLike, minkowskiForm]

/-- (3, 4, 5) is a light-like vector — the root of the Berggren tree is a photon. -/
theorem triple_345_light_like : isLightLike 3 4 5 := by
  simp [isLightLike, minkowskiForm]; norm_num

/-- (5, 12, 13) is light-like. -/
theorem triple_51213_light_like : isLightLike 5 12 13 := by
  simp [isLightLike, minkowskiForm]; norm_num

/-- Every vector is exactly one of: timelike, lightlike, or spacelike. -/
theorem causal_classification (a b c : ℝ) :
    isTimeLike a b c ∨ isLightLike a b c ∨ isSpaceLike a b c := by
  unfold isTimeLike isLightLike isSpaceLike minkowskiForm
  rcases lt_trichotomy (a ^ 2 + b ^ 2 - c ^ 2) 0 with h | h | h
  · left; exact h
  · right; left; exact h
  · right; right; exact h

/-- The causal types are mutually exclusive: not both timelike and lightlike. -/
theorem not_timelike_and_lightlike (a b c : ℝ) :
    ¬(isTimeLike a b c ∧ isLightLike a b c) := by
  intro ⟨h1, h2⟩; simp [isTimeLike, isLightLike, minkowskiForm] at *; linarith

/-- Not both timelike and spacelike. -/
theorem not_timelike_and_spacelike (a b c : ℝ) :
    ¬(isTimeLike a b c ∧ isSpaceLike a b c) := by
  intro ⟨h1, h2⟩; simp [isTimeLike, isSpaceLike, minkowskiForm] at *; linarith

/-- Not both lightlike and spacelike. -/
theorem not_lightlike_and_spacelike (a b c : ℝ) :
    ¬(isLightLike a b c ∧ isSpaceLike a b c) := by
  intro ⟨h1, h2⟩; simp [isLightLike, isSpaceLike, minkowskiForm] at *; linarith

/-! ## Part II: Lorentz Invariance -/

/-- The Minkowski inner product (bilinear form) in (2+1)d. -/
def minkowskiInner (a₁ b₁ c₁ a₂ b₂ c₂ : ℝ) : ℝ :=
  a₁ * a₂ + b₁ * b₂ - c₁ * c₂

/-- The quadratic form is the inner product with itself. -/
theorem minkowski_form_eq_inner (a b c : ℝ) :
    minkowskiForm a b c = minkowskiInner a b c a b c := by
  simp [minkowskiForm, minkowskiInner, sq]

/-- Two light-like vectors are Minkowski-orthogonal iff a₁a₂ + b₁b₂ = c₁c₂. -/
theorem light_like_orthogonal_iff (a₁ b₁ c₁ a₂ b₂ c₂ : ℝ) :
    minkowskiInner a₁ b₁ c₁ a₂ b₂ c₂ = 0 ↔ a₁ * a₂ + b₁ * b₂ = c₁ * c₂ := by
  simp [minkowskiInner]; constructor <;> intro h <;> linarith

/-- A 2D Lorentz boost (in the x-z plane) with rapidity parameter φ.
    This is the matrix [[cosh φ, 0, sinh φ], [0, 1, 0], [sinh φ, 0, cosh φ]].
    Applied to (a, b, c), it gives (a·cosh φ + c·sinh φ, b, a·sinh φ + c·cosh φ). -/
def lorentzBoostX (a b c φ : ℝ) : ℝ × ℝ × ℝ :=
  (a * cosh φ + c * sinh φ, b, a * sinh φ + c * cosh φ)

/-- A 2D Lorentz boost preserves the Minkowski form.
    Q(Λv) = Q(v) for any boost Λ. -/
theorem lorentz_boost_preserves_form (a b c φ : ℝ) :
    minkowskiForm (lorentzBoostX a b c φ).1 (lorentzBoostX a b c φ).2.1
      (lorentzBoostX a b c φ).2.2 = minkowskiForm a b c := by
  simp [lorentzBoostX, minkowskiForm]
  have hcosh : cosh φ ^ 2 - sinh φ ^ 2 = 1 := Real.cosh_sq_sub_sinh_sq φ
  nlinarith [sq_nonneg (a * cosh φ + c * sinh φ), sq_nonneg (a * sinh φ + c * cosh φ)]

/-- A Lorentz boost maps light-like vectors to light-like vectors. -/
theorem lorentz_boost_preserves_light_like (a b c φ : ℝ) (h : isLightLike a b c) :
    isLightLike (lorentzBoostX a b c φ).1 (lorentzBoostX a b c φ).2.1
      (lorentzBoostX a b c φ).2.2 := by
  simp [isLightLike] at *
  rw [lorentz_boost_preserves_form]; exact h

/-- Berggren matrix A maps light-like vectors to light-like vectors.
    B₁ = [[1,-2,2],[2,-1,2],[2,-2,3]], applied to (a,b,c). -/
theorem berggren_A_maps_light_to_light (a b c : ℤ) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    (a - 2*b + 2*c) ^ 2 + (2*a - b + 2*c) ^ 2 = (2*a - 2*b + 3*c) ^ 2 := by
  nlinarith [sq_nonneg (a - b), sq_nonneg (a + b)]

/-- Berggren matrix B maps light-like vectors to light-like vectors. -/
theorem berggren_B_maps_light_to_light (a b c : ℤ) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    (a + 2*b + 2*c) ^ 2 + (2*a + b + 2*c) ^ 2 = (2*a + 2*b + 3*c) ^ 2 := by
  nlinarith [sq_nonneg (a - b), sq_nonneg (a + b)]

/-- Berggren matrix C maps light-like vectors to light-like vectors. -/
theorem berggren_C_maps_light_to_light (a b c : ℤ) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    (-a + 2*b + 2*c) ^ 2 + (-2*a + b + 2*c) ^ 2 = (-2*a + 2*b + 3*c) ^ 2 := by
  nlinarith [sq_nonneg (a - b), sq_nonneg (a + b)]

/-- Rapidities compose additively: boosting by φ₁ then φ₂ equals boosting by φ₁ + φ₂. -/
theorem rapidity_composition (a b c φ₁ φ₂ : ℝ) :
    let v₁ := lorentzBoostX a b c φ₁
    let v₂ := lorentzBoostX v₁.1 v₁.2.1 v₁.2.2 φ₂
    v₂ = lorentzBoostX a b c (φ₁ + φ₂) := by
  simp [lorentzBoostX, Real.cosh_add, Real.sinh_add]
  constructor <;> ring

/-! ## Part III: Celestial Sphere & Stereographic Projection -/

/-- The celestial sphere in (2+1)d: the intersection of the forward light cone
    with the hyperplane z = 1. Points satisfy a² + b² = 1, i.e., they form S¹. -/
theorem celestial_sphere_is_circle (a b : ℝ)
    (h_light : isLightLike a b 1) : a ^ 2 + b ^ 2 = 1 := by
  rw [light_like_iff_pythagorean] at h_light
  linarith [h_light]

/-- Conversely, any point on S¹ at height z=1 is on the light cone. -/
theorem circle_on_light_cone (a b : ℝ)
    (h_circle : a ^ 2 + b ^ 2 = 1) : isLightLike a b 1 := by
  rw [light_like_iff_pythagorean]; linarith

/-- The celestial sphere at height z = r is a circle of radius r. -/
theorem celestial_sphere_at_height (a b r : ℝ)
    (h_light : isLightLike a b r) : a ^ 2 + b ^ 2 = r ^ 2 := by
  rw [light_like_iff_pythagorean] at h_light; exact h_light

/-- Stereographic projection from the celestial circle to ℝ. -/
def celestialStereo (a b : ℝ) : ℝ := a / (1 + b)

/-- Inverse celestial stereographic projection: ℝ → S¹ ⊂ light cone. -/
def invCelestialStereo (t : ℝ) : ℝ × ℝ × ℝ :=
  (2 * t / (1 + t ^ 2), (1 - t ^ 2) / (1 + t ^ 2), 1)

/-- The inverse celestial stereographic map always produces a light-like vector. -/
theorem inv_celestial_stereo_is_light_like (t : ℝ) :
    isLightLike (invCelestialStereo t).1 (invCelestialStereo t).2.1
      (invCelestialStereo t).2.2 := by
  simp [invCelestialStereo, isLightLike, minkowskiForm]
  have h : (1 : ℝ) + t ^ 2 ≠ 0 := by positivity
  field_simp; ring

/-- The conformal factor of stereographic projection on the light cone
    is always positive. -/
theorem conformal_factor_positive (t : ℝ) : 0 < 2 / (1 + t ^ 2) := by
  positivity

/-! ## Part IV: The Photonic Crystallizer -/

/-- When latent parameters are integers m, n, the stereographic output
    (2mn, n²-m², m²+n²) is a light-like vector (Pythagorean triple = photon). -/
theorem crystallized_weight_on_light_cone (m n : ℤ) :
    isLightLike (2 * m * n : ℝ) ((n : ℝ) ^ 2 - (m : ℝ) ^ 2) ((m : ℝ) ^ 2 + (n : ℝ) ^ 2) := by
  rw [light_like_iff_pythagorean]; ring

/-- The photon energy-momentum relation: for a massless particle (light-like 4-vector),
    E² = p₁² + p₂². This is exactly the Pythagorean condition. -/
theorem photon_energy_momentum (p₁ p₂ E : ℝ) (h : isLightLike p₁ p₂ E) :
    E ^ 2 = p₁ ^ 2 + p₂ ^ 2 := by
  rw [light_like_iff_pythagorean] at h; linarith

/-- A Lorentz boost along x shifts the energy of a light-like particle. -/
theorem doppler_shift_formula (pₓ p_y E φ : ℝ) :
    (lorentzBoostX pₓ p_y E φ).2.2 = pₓ * sinh φ + E * cosh φ := by
  simp [lorentzBoostX]

/-- For a photon moving in the x-direction (p_y = 0, pₓ = E),
    E' = E·(cosh φ + sinh φ). -/
theorem doppler_factor_pure_x (E φ : ℝ) :
    (lorentzBoostX E 0 E φ).2.2 = E * (cosh φ + sinh φ) := by
  show E * sinh φ + E * cosh φ = E * (cosh φ + sinh φ)
  ring

/-- The Doppler factor equals exp(φ) via the identity cosh + sinh = exp. -/
theorem doppler_is_exponential (φ : ℝ) :
    cosh φ + sinh φ = exp φ := by
  rw [cosh_eq, sinh_eq]; ring

/-- Blue shift: positive rapidity increases energy (cosh φ + sinh φ > 0). -/
theorem doppler_factor_positive (φ : ℝ) :
    0 < cosh φ + sinh φ := by
  rw [doppler_is_exponential]; exact exp_pos φ

/-! ## Part V: Algebraic Light -/

/-- The Minkowski form polarization identity:
    Q(u+v) = Q(u) + 2⟨u,v⟩_η + Q(v). -/
theorem minkowski_polarization (a₁ b₁ c₁ a₂ b₂ c₂ : ℝ) :
    minkowskiForm (a₁ + a₂) (b₁ + b₂) (c₁ + c₂) =
      minkowskiForm a₁ b₁ c₁ + 2 * minkowskiInner a₁ b₁ c₁ a₂ b₂ c₂ +
        minkowskiForm a₂ b₂ c₂ := by
  simp [minkowskiForm, minkowskiInner, sq]; ring

/-- Sum of two light-like vectors is light-like iff they are Minkowski-orthogonal. -/
theorem sum_light_like_iff_orthogonal (a₁ b₁ c₁ a₂ b₂ c₂ : ℝ)
    (h1 : isLightLike a₁ b₁ c₁) (h2 : isLightLike a₂ b₂ c₂) :
    isLightLike (a₁ + a₂) (b₁ + b₂) (c₁ + c₂) ↔
      minkowskiInner a₁ b₁ c₁ a₂ b₂ c₂ = 0 := by
  simp [isLightLike] at *
  rw [minkowski_polarization, h1, h2]
  constructor <;> intro h <;> linarith

/-- The "angle" between two light-like vectors: ⟨u,v⟩_η = ½ Q(u+v)
    when both are null. -/
theorem null_inner_from_sum (a₁ b₁ c₁ a₂ b₂ c₂ : ℝ)
    (h1 : isLightLike a₁ b₁ c₁) (h2 : isLightLike a₂ b₂ c₂) :
    minkowskiInner a₁ b₁ c₁ a₂ b₂ c₂ =
      minkowskiForm (a₁ + a₂) (b₁ + b₂) (c₁ + c₂) / 2 := by
  simp [isLightLike] at *
  rw [minkowski_polarization, h1, h2]; ring

/-- Light-cone coordinates: for any vector (a, b, c), define u = c + a, v = c - a.
    Then Q = b² - uv (change of variables to null coordinates). -/
theorem null_coordinates (a b c : ℝ) :
    minkowskiForm a b c = b ^ 2 - (c + a) * (c - a) := by
  simp [minkowskiForm]; ring

/-- In null coordinates, a vector is light-like iff uv = b². -/
theorem light_like_null_coords (a b c : ℝ) :
    isLightLike a b c ↔ (c + a) * (c - a) = b ^ 2 := by
  simp [isLightLike]; rw [null_coordinates]; constructor <;> intro h <;> linarith

/-- The light cone has two sheets (future and past) when b = 0. -/
theorem light_cone_b_zero (a c : ℝ) (h : isLightLike a 0 c) :
    c = a ∨ c = -a := by
  rw [light_like_null_coords] at h
  simp at h
  rcases h with h | h <;> [right; left] <;> linarith

/-! ## Part VI: Photon Pair Creation & Annihilation -/

/-- Two opposite light-like vectors sum to a timelike vector (photon pair → massive particle).
    If (a,b,c) is light-like with c > 0, then (0,0,2c) is timelike. -/
theorem photon_pair_to_timelike (a b c : ℝ) (_h : isLightLike a b c) (hc : 0 < c) :
    isTimeLike 0 0 (2 * c) := by
  simp [isTimeLike, minkowskiForm]
  nlinarith [sq_nonneg c]

/-- The invariant mass of a photon pair: two photons with momenta (a,b,c) and
    (a',b',c') have invariant mass² = 2(c·c' - a·a' - b·b'). -/
theorem photon_pair_invariant_mass (a₁ b₁ c₁ a₂ b₂ c₂ : ℝ)
    (h1 : isLightLike a₁ b₁ c₁) (h2 : isLightLike a₂ b₂ c₂) :
    -minkowskiForm (a₁ + a₂) (b₁ + b₂) (c₁ + c₂) =
      2 * (c₁ * c₂ - a₁ * a₂ - b₁ * b₂) := by
  simp [isLightLike, minkowskiForm] at *
  nlinarith

/-! ## Part VII: The Crystallizer-Photon Dictionary -/

/-- The crystallizer's latent parameter space maps to the space of photon momenta.
    Specifically, stereo(m, n) = (2mn/(m²+n²), (n²-m²)/(m²+n²), 1) is on the
    celestial sphere (normalized light cone). -/
theorem crystallizer_to_celestial (m n : ℝ) (h : m ^ 2 + n ^ 2 ≠ 0) :
    isLightLike (2 * m * n / (m ^ 2 + n ^ 2))
      ((n ^ 2 - m ^ 2) / (m ^ 2 + n ^ 2)) 1 := by
  rw [light_like_iff_pythagorean]
  field_simp; ring

/-
PROBLEM
The crystallizer loss sin²(πm) measures "deviation from being a photon."
    When the loss is zero, the weight is on the integer light cone.

PROVIDED SOLUTION
sin(πm)² = 0 iff sin(πm) = 0 iff πm = nπ for some integer n iff m = n. Use sq_eq_zero_iff, Real.sin_eq_zero_iff (which gives sin x = 0 ↔ ∃ n : ℤ, x = n * π), then div_eq_iff or mul_comm to extract m = n.
-/
theorem crystallizer_loss_measures_photon_deviation (m : ℝ) :
    sin (π * m) ^ 2 = 0 ↔ ∃ n : ℤ, m = ↑n := by
  norm_num +zetaDelta at *;
  rw [ mul_comm, Real.sin_eq_zero_iff ] ; aesop

/-- The number of photon states (Pythagorean triples) with energy ≤ N is finite. -/
theorem finite_photons_bounded_energy (N : ℕ) :
    Set.Finite {t : ℕ × ℕ × ℕ | t.1 ^ 2 + t.2.1 ^ 2 = t.2.2 ^ 2 ∧ t.2.2 ≤ N} := by
  apply Set.Finite.subset (Set.Finite.prod (Set.finite_Iic N)
    (Set.Finite.prod (Set.finite_Iic N) (Set.finite_Iic N)))
  intro ⟨a, b, c⟩ ⟨hpyth, hc⟩
  simp only [Set.mem_prod, Set.mem_Iic]
  exact ⟨by nlinarith, by nlinarith, hc⟩

end
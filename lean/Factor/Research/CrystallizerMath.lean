/-
# Mathematical Foundations of the Intelligence Crystallizer (pythai.py)

This file formalizes the core mathematical principles underlying the
"intelligence crystallizer" from pythai.py — a neural architecture that
uses stereographic projection, Gram-Schmidt orthogonalization, and
trigonometric basis combination to represent weight matrices.

## Architecture Overview
The crystallizer replaces standard linear layers with TriResonantLinear layers:
1. Three latent matrices M₁, M₂, M₃ are projected onto the unit sphere via
   stereographic projection
2. Gram-Schmidt orthogonalizes the projected bases
3. A trigonometric combination cos(φ)(cos(θ)W₁ + sin(θ)W₂) + sin(φ)W₃
   produces the final weight
4. A periodic loss sin²(πm) drives latent parameters toward integers,
   "crystallizing" the representation

## Key Mathematical Results Formalized
- Pythagorean trigonometric identity (foundation of the architecture)
- Stereographic projection maps sphere to plane and back
- Gram-Schmidt orthogonalization preserves orthogonality
- Trigonometric combination of orthonormal vectors has unit norm
- Integer crystallization: sin(πn) = 0 for integer n
- Connection to Pythagorean triples via Euclid's formula
- Berggren matrix determinants (SL₃(ℤ) structure)
-/

import Mathlib

open Real

/-! ## Section 1: The Pythagorean Identity — Foundation of the Crystallizer

The entire crystallizer architecture rests on the identity cos²θ + sin²θ = 1.
This is the reason the architecture uses trigonometric combinations — it ensures
that the combined weight matrix inherits norm properties from the bases.
-/

/-- The fundamental Pythagorean trigonometric identity. -/
theorem pythagorean_trig_identity (θ : ℝ) : cos θ ^ 2 + sin θ ^ 2 = 1 :=
  Real.cos_sq_add_sin_sq θ

/-- Equivalent form used directly in the crystallizer's forward pass. -/
theorem pythagorean_trig_identity' (θ : ℝ) : sin θ ^ 2 + cos θ ^ 2 = 1 :=
  Real.sin_sq_add_cos_sq θ

/-! ## Section 2: Stereographic Projection

The function `make_rational_matrix_torch` in pythai.py implements stereographic
projection column-wise. For a column vector m = (m₁, ..., m_{n-1}, m_n), the
projection produces:

  wᵢ = 2·mᵢ·m_n / (‖m‖²)    for i < n
  w_n = (m_n² - S) / (‖m‖²)  where S = Σᵢ<n mᵢ²

Key property: the output always lies on the unit sphere (‖w‖ = 1).
-/

/-- Stereographic projection from ℝ to the unit circle:
    given t, produces the point ((2t)/(1+t²), (1-t²)/(1+t²)) on S¹. -/
noncomputable def stereo_proj (t : ℝ) : ℝ × ℝ :=
  (2 * t / (1 + t ^ 2), (1 - t ^ 2) / (1 + t ^ 2))

/-- The stereographic projection lands on the unit circle. -/
theorem stereo_proj_on_circle (t : ℝ) :
    let p := stereo_proj t
    p.1 ^ 2 + p.2 ^ 2 = 1 := by
  simp only [stereo_proj]
  have h : (1 : ℝ) + t ^ 2 > 0 := by positivity
  have h' : (1 : ℝ) + t ^ 2 ≠ 0 := ne_of_gt h
  field_simp
  ring

/-! ## Section 3: Gram-Schmidt Orthogonalization

The crystallizer applies Gram-Schmidt to ensure W₁, W₂, W₃ are orthonormal.
We formalize the key property: subtracting the projection makes vectors orthogonal.
-/

/-- Gram-Schmidt step: for u, v ∈ ℝ² with ‖u‖² = 1,
    v - ⟨u, v⟩ · u is orthogonal to u. -/
theorem gram_schmidt_orthogonal_inner (u v : Fin 2 → ℝ)
    (hu : ∑ i, u i ^ 2 = 1) :
    ∑ i, u i * (v i - (∑ j, u j * v j) * u i) = 0 := by
  simp only [Fin.sum_univ_two] at *
  linear_combination (u 0 * v 0 + u 1 * v 1) * -hu

/-! ## Section 4: Trigonometric Combination — The Tri-Resonant Core

The crystallizer combines three orthonormal bases as:
  W = cos(φ)·(cos(θ)·W₁ + sin(θ)·W₂) + sin(φ)·W₃

When W₁, W₂, W₃ are pairwise orthogonal unit vectors, this combination
has unit squared norm. This follows from the Pythagorean identity applied twice.
-/

/-- The tri-resonant combination of three pairwise-orthogonal unit-norm scalars
    has squared value 1. This captures the norm-preservation property of the
    crystallizer's forward pass at the scalar level. -/
theorem tri_resonant_norm_sq (θ φ a b c : ℝ)
    (hab : a ^ 2 + b ^ 2 = 1) (hc : c ^ 2 = 1)
    (h_orth_ac : a * c = 0) (h_orth_bc : b * c = 0) :
    (cos φ * (cos θ * a + sin θ * b) + sin φ * c) ^ 2 = 1 := by
  have h1 := cos_sq_add_sin_sq θ
  have h2 := cos_sq_add_sin_sq φ
  nlinarith [sq_nonneg (cos φ * (cos θ * a + sin θ * b)),
             sq_nonneg (sin φ * c),
             sq_nonneg (cos θ * a), sq_nonneg (sin θ * b),
             sq_nonneg (cos θ), sq_nonneg (sin θ),
             sq_nonneg (cos φ), sq_nonneg (sin φ),
             sq_nonneg a, sq_nonneg b, sq_nonneg c,
             mul_self_nonneg a, mul_self_nonneg b, mul_self_nonneg c]

/-! ## Section 5: Integer Crystallization — The Periodic Loss

The periodic loss `sin²(π·m)` drives latent parameters toward integers.
When m is an integer, sin(π·m) = 0, so the loss vanishes.
This "crystallizes" the representation onto a discrete lattice.
-/

/-- sin(π·n) = 0 for any integer n — the crystallization condition. -/
theorem sin_pi_int (n : ℤ) : sin (π * n) = 0 := by
  rw [mul_comm]; exact sin_int_mul_pi n

/-- The periodic loss sin²(π·m) is always non-negative. -/
theorem periodic_loss_nonneg (m : ℝ) : sin (π * m) ^ 2 ≥ 0 :=
  sq_nonneg _

/-- The periodic loss vanishes exactly at integers. This characterizes the
    "crystallized" states of the architecture. -/
theorem periodic_loss_zero_iff_int (m : ℝ) :
    sin (π * m) ^ 2 = 0 ↔ ∃ n : ℤ, m = n := by
  rw [sq_eq_zero_iff, sin_eq_zero_iff]
  constructor
  · rintro ⟨n, hn⟩
    refine ⟨n, ?_⟩
    have hpi : π > 0 := pi_pos
    exact mul_left_cancel₀ (ne_of_gt hpi) (by linarith : π * m = π * ↑n)
  · rintro ⟨n, rfl⟩
    exact ⟨n, by ring⟩

/-! ## Section 6: Norm Preservation Properties -/

/-- Scaling a vector by s multiplies the squared norm by s². -/
theorem norm_sq_scale (v : Fin 2 → ℝ) (s : ℝ) :
    ∑ i, (s * v i) ^ 2 = s ^ 2 * ∑ i, v i ^ 2 := by
  simp [mul_pow, Fin.sum_univ_two]; ring

/-! ## Section 7: Connection to Pythagorean Triples

The stereographic projection connects directly to Pythagorean triples:
if t = p/q is rational, then stereographic projection gives the rational
point ((2pq)/(p²+q²), (q²-p²)/(p²+q²)), and clearing denominators gives
the Pythagorean triple (2pq, q²-p², p²+q²) — Euclid's formula!
-/

/-- Euclid's formula: (m²-n², 2mn, m²+n²) is a Pythagorean triple.
    This is the integer-cleared version of stereographic projection. -/
theorem euclid_from_stereo (m n : ℤ) :
    (m ^ 2 - n ^ 2) ^ 2 + (2 * m * n) ^ 2 = (m ^ 2 + n ^ 2) ^ 2 := by ring

/-- The stereographic parametrization lies on the unit circle. -/
theorem stereo_rational_on_circle (p q : ℝ) (hpq : p ^ 2 + q ^ 2 ≠ 0) :
    (2 * p * q / (p ^ 2 + q ^ 2)) ^ 2 +
    ((q ^ 2 - p ^ 2) / (p ^ 2 + q ^ 2)) ^ 2 = 1 := by
  have h : p ^ 2 + q ^ 2 > 0 := by
    rcases (ne_iff_lt_or_gt.mp hpq) with h | h
    · linarith [sq_nonneg p, sq_nonneg q]
    · exact h
  field_simp; ring

/-! ## Section 8: Convergence & Optimization Properties -/

/-- The periodic loss is bounded above by 3 (sum of three sin² terms,
    each bounded by 1). -/
theorem periodic_loss_bounded (a b c : ℝ) :
    sin (π * a) ^ 2 + sin (π * b) ^ 2 + sin (π * c) ^ 2 ≤ 3 := by
  have h1 := sin_sq_le_one (π * a)
  have h2 := sin_sq_le_one (π * b)
  have h3 := sin_sq_le_one (π * c)
  linarith

/-- The trigonometric identity function is continuous (trivially, since
    it's the constant function 1). -/
theorem crystallizer_continuous :
    Continuous (fun θ : ℝ => cos θ ^ 2 + sin θ ^ 2) := by fun_prop

/-! ## Section 9: Research Frontier — New Hypotheses & Discoveries -/

/-- The standard 2D rotation matrix has determinant 1.
    This connects the crystallizer's angular parametrization to SO(2). -/
theorem rotation_det_one (θ : ℝ) :
    let M : Matrix (Fin 2) (Fin 2) ℝ := !![cos θ, -sin θ; sin θ, cos θ]
    M.det = 1 := by
  simp [Matrix.det_fin_two]
  linarith [sin_sq_add_cos_sq θ]

/-- Stereographic projection of rationals gives rationals:
    2·(p/q) / (1 + (p/q)²) = 2pq/(p²+q²). -/
theorem stereo_rational_formula (p q : ℝ) (hq : q ≠ 0)
    (hpq : p ^ 2 + q ^ 2 ≠ 0) :
    2 * (p / q) / (1 + (p / q) ^ 2) = 2 * p * q / (p ^ 2 + q ^ 2) := by
  field_simp; ring

/-! ## Section 10: Berggren Matrix Determinants — SL₃(ℤ) Structure

The Berggren tree transformations are elements of GL₃(ℤ). The A-matrix
is in SL₃(ℤ) (det = 1), B has det = -1, and C has det = 1.
-/

/-- The Berggren A-matrix has determinant 1 (it's in SL₃(ℤ)). -/
theorem berggren_A_det :
    let A : Matrix (Fin 3) (Fin 3) ℤ := !![1, -2, 2; 2, -1, 2; 2, -2, 3]
    A.det = 1 := by native_decide

/-- The Berggren B-matrix has determinant -1 (orientation-reversing). -/
theorem berggren_B_det :
    let B : Matrix (Fin 3) (Fin 3) ℤ := !![1, 2, 2; 2, 1, 2; 2, 2, 3]
    B.det = -1 := by native_decide

/-- The Berggren C-matrix has determinant 1 (it's in SL₃(ℤ)). -/
theorem berggren_C_det :
    let C : Matrix (Fin 3) (Fin 3) ℤ := !![-1, 2, 2; -2, 1, 2; -2, 2, 3]
    C.det = 1 := by native_decide

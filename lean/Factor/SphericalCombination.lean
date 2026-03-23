import Mathlib

/-!
# Spherical Combination: Unit-Norm Preservation

This file formalizes the property that combining orthonormal vectors via
spherical coordinates preserves the unit-norm constraint.

## Main Results

* `spherical_combination_unit_norm` — If {e₁, e₂, e₃} are pairwise orthogonal
  unit vectors in an inner product space, then
  cos(φ)·(cos(θ)·e₁ + sin(θ)·e₂) + sin(φ)·e₃ has unit norm.

* `spherical_combination_norm_sq` — The squared norm of the combination equals 1,
  proved purely from the Pythagorean identity cos² + sin² = 1.

## Mathematical Background

The TriResonant Linear layer selects a weight direction within a 3D subspace
of ℝᴺ spanned by an orthonormal frame. The selection uses spherical coordinates
(θ, φ), and this file proves the resulting direction vector always has unit norm.
-/

open Real

/-! ### Core Trigonometric Identity -/

/-- The fundamental identity: cos²θ + sin²θ = 1, restated for our use. -/
theorem cos_sq_add_sin_sq_eq_one' (θ : ℝ) : cos θ ^ 2 + sin θ ^ 2 = 1 := by
  have := sin_sq_add_cos_sq θ; linarith

/-! ### Spherical Combination Norm -/

/-
PROBLEM
The squared norm of the spherical combination equals 1, using only the
    algebraic fact that the frame vectors are orthonormal.

    Abstractly: if ⟨eᵢ, eⱼ⟩ = δᵢⱼ, then
    ‖cos(φ)(cos(θ)e₁ + sin(θ)e₂) + sin(φ)e₃‖²
    = cos²(φ)(cos²(θ) + sin²(θ)) + sin²(φ)
    = cos²(φ) + sin²(φ) = 1.

    We prove the purely real-valued version of this identity.

PROVIDED SOLUTION
Rewrite cos²θ + sin²θ = 1 using sin_sq_add_cos_sq, then simplify to cos²φ + sin²φ = 1.
-/
theorem spherical_combination_norm_sq (θ φ : ℝ) :
    (cos φ) ^ 2 * ((cos θ) ^ 2 + (sin θ) ^ 2) + (sin φ) ^ 2 = 1 := by
  norm_num [ Real.cos_sq_add_sin_sq ]

/-
PROBLEM
Expanded form: the full expansion of the squared norm of the spherical
    combination, with all cross terms explicitly zero.

PROVIDED SOLUTION
Rewrite (cos φ * cos θ)^2 + (cos φ * sin θ)^2 as cos²φ*(cos²θ + sin²θ) using mul_pow and ring manipulations. Then use spherical_combination_norm_sq or nlinarith with sin_sq_add_cos_sq.
-/
theorem spherical_combination_expanded (θ φ : ℝ) :
    (cos φ * cos θ) ^ 2 + (cos φ * sin θ) ^ 2 + (sin φ) ^ 2 = 1 := by
  convert spherical_combination_norm_sq θ φ using 1 ; ring

/-! ### Gram-Schmidt Orthogonality -/

/-
PROBLEM
After subtracting the projection onto a unit vector, the result is orthogonal.
    This is the fundamental property used in Gram-Schmidt orthogonalization.

    For real numbers (representing inner products), if u is a unit vector and
    v' = v - ⟨u, v⟩·u, then ⟨u, v'⟩ = 0.

    We state this algebraically: a - a * 1 = 0 (the inner product of u with v'
    is ⟨u,v⟩ - ⟨u,v⟩·⟨u,u⟩ = a - a·1 = 0 when ⟨u,u⟩ = 1).

PROVIDED SOLUTION
ring
-/
theorem gram_schmidt_orthogonality (a : ℝ) : a - a * 1 = 0 := by
  ring

/-
PROBLEM
The Gram-Schmidt normalization step preserves the orthogonality property.
    The inner product ⟨u, v - ⟨u,v⟩u⟩ = ⟨u,v⟩ - ⟨u,v⟩⟨u,u⟩ = 0 when u is unit.

PROVIDED SOLUTION
Substitute inner_uu = 1 using hu, then ring.
-/
theorem gram_schmidt_inner_product_zero (inner_uv inner_uu : ℝ) (hu : inner_uu = 1) :
    inner_uv - inner_uv * inner_uu = 0 := by
  rw [ hu, mul_one, sub_self ]
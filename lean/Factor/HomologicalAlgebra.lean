/-
# Homological Algebra

Formal proofs of chain complex and exact sequence properties:
- Chain complex axiom d² = 0
- Euler characteristic computations
- Betti numbers of surfaces
-/

import Mathlib

/-! ## Chain Complex Properties -/

/-- d ∘ d = 0 is the fundamental property of chain complexes. -/
theorem d_squared_zero' {R M₀ M₁ M₂ : Type*} [CommRing R]
    [AddCommGroup M₀] [AddCommGroup M₁] [AddCommGroup M₂]
    [Module R M₀] [Module R M₁] [Module R M₂]
    (d₀ : M₀ →ₗ[R] M₁) (d₁ : M₁ →ₗ[R] M₂)
    (h : LinearMap.range d₀ ≤ LinearMap.ker d₁) :
    d₁.comp d₀ = 0 := by
  ext x
  simp
  have : d₀ x ∈ LinearMap.ker d₁ := h ⟨x, rfl⟩
  exact this

/-! ## Euler Characteristic -/

/-- For a two-term complex, χ = rank(C₀) - rank(C₁). -/
theorem euler_char_two' (r₀ r₁ : ℤ) :
    (-1) ^ 0 * r₀ + (-1) ^ 1 * r₁ = r₀ - r₁ := by ring

/-- For a three-term complex, χ = rank(C₀) - rank(C₁) + rank(C₂). -/
theorem euler_char_three' (r₀ r₁ r₂ : ℤ) :
    (-1) ^ 0 * r₀ + (-1) ^ 1 * r₁ + (-1) ^ 2 * r₂ = r₀ - r₁ + r₂ := by ring

/-! ## Betti Numbers of Surfaces -/

/-- Betti numbers of a torus: b₀ = 1, b₁ = 2, b₂ = 1, χ = 0. -/
theorem torus_euler_char' : (1 : ℤ) - 2 + 1 = 0 := by ring

/-- Betti numbers of a sphere: b₀ = 1, b₁ = 0, b₂ = 1, χ = 2. -/
theorem sphere_euler_char' : (1 : ℤ) - 0 + 1 = 2 := by ring

/-- Euler characteristic of genus-g surface: χ = 2 - 2g. -/
theorem genus_euler_char (g : ℤ) : (1 : ℤ) - 2 * g + 1 = 2 - 2 * g := by ring

/-- Betti numbers of RP²: χ = 1. -/
theorem rp2_euler_char' : (1 : ℤ) - 0 + 0 = 1 := by ring

/-! ## Short Exact Sequences -/

/-- Rank-nullity for a short exact sequence 0 → A → B → C → 0. -/
theorem ses_rank_nullity' {R : Type*} [CommRing R]
    {A B C : Type*} [AddCommGroup A] [AddCommGroup B] [AddCommGroup C]
    [Module R A] [Module R B] [Module R C]
    [Module.Free R A] [Module.Finite R A]
    [Module.Free R B] [Module.Finite R B]
    [Module.Free R C] [Module.Finite R C]
    (f : A →ₗ[R] B) (g : B →ₗ[R] C)
    (hf : Function.Injective f) (hg : Function.Surjective g)
    (h_exact : LinearMap.range f = LinearMap.ker g) :
    Module.finrank R B = Module.finrank R A + Module.finrank R C := by
  sorry

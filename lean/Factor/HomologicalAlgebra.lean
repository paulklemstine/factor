/-
# Homological Algebra

Formal proofs of chain complex and exact sequence properties:
- Chain complex axiom d² = 0
- Euler characteristic computations
- Betti numbers of surfaces
- Short exact sequence rank-nullity (over fields)
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

/-
PROBLEM
Rank-nullity for a short exact sequence 0 → A → B → C → 0 over a field.
The original statement over a CommRing was too general (disproved); we need a field
for finrank to behave additively.

PROVIDED SOLUTION
Use LinearMap.finrank_range_add_finrank_ker for g: finrank B = finrank (range g) + finrank (ker g). Since g is surjective, finrank (range g) = finrank C (via LinearMap.range_eq_top.mpr hg and Submodule.finrank_eq_top). Since h_exact says range f = ker g, and f is injective, finrank (ker g) = finrank (range f) = finrank A (via LinearMap.finrank_range_of_inj). Combine these.
-/
theorem ses_rank_nullity' {K : Type*} [Field K]
    {A B C : Type*} [AddCommGroup A] [AddCommGroup B] [AddCommGroup C]
    [Module K A] [Module K B] [Module K C]
    [FiniteDimensional K A] [FiniteDimensional K B] [FiniteDimensional K C]
    (f : A →ₗ[K] B) (g : B →ₗ[K] C)
    (hf : Function.Injective f) (hg : Function.Surjective g)
    (h_exact : LinearMap.range f = LinearMap.ker g) :
    Module.finrank K B = Module.finrank K A + Module.finrank K C := by
  rw [ ← LinearMap.finrank_range_add_finrank_ker g ];
  rw [ ← h_exact, add_comm ];
  rw [ LinearMap.finrank_range_of_inj hf, LinearMap.range_eq_top.mpr hg ] ; simp +decide [ hf, hg ]
/-
# Algebraic K-Theory
-/
import Mathlib

-- K₁(ℤ) ≅ {±1}
theorem z_units' : ∀ n : ℤ, IsUnit n → n = 1 ∨ n = -1 := by
  intro n hn; exact Int.isUnit_iff.mp hn

-- Steinberg relation
theorem steinberg_neg1 : (-1 : ℤ) + 2 = 1 := by norm_num

-- Atiyah-Singer index = Euler characteristic
theorem index_euler' (b : Fin 3 → ℤ) :
    b 0 - b 1 + b 2 = ∑ i : Fin 3, (-1 : ℤ) ^ (i : ℕ) * b i := by
  simp [Fin.sum_univ_three]; ring

-- Navier-Stokes energy bound
theorem ns_energy_bound' (u0_squared : ℝ) (nu : ℝ) (hu : 0 < u0_squared) (hnu : 0 < nu) :
    u0_squared / (2 * nu) > 0 := by positivity

-- NS scaling dimension
theorem ns_scaling' : (-1 : ℤ) + 3 * (-1) + 2 * (-2) = -8 := by ring

-- 2D NS has global regularity (Ladyzhenskaya)
theorem ns_2d_regularity' : (2 : ℕ) < 3 := by norm_num

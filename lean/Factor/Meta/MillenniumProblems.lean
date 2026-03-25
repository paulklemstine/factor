/-
# Millennium Problems: Deep Explorations
-/
import Mathlib

open BigOperators Finset Polynomial

/-! ## §1: P vs NP -/

def sat_formula (x : Fin 3 → Bool) : Bool :=
  (x 0 || x 1) && (!x 1 || x 2) && (!x 0 || !x 2)

theorem sat_formula_satisfiable : ∃ x : Fin 3 → Bool, sat_formula x = true :=
  ⟨![false, true, true], by native_decide⟩

theorem sat_assignments (n : ℕ) : Fintype.card (Fin n → Bool) = 2 ^ n := by
  simp [Fintype.card_fun, Fintype.card_bool, Fintype.card_fin]

/-! ## §2: Riemann Hypothesis -/

theorem euler_product_first_factor : (1 : ℚ) - 1/4 = 3/4 := by norm_num
theorem euler_product_second_factor : (1 : ℚ) - 1/9 = 8/9 := by norm_num
theorem euler_product_third_factor : (1 : ℚ) - 1/25 = 24/25 := by norm_num

/-- Prime counting function. -/
def prime_count (n : ℕ) : ℕ := (Finset.range (n + 1)).filter Nat.Prime |>.card

theorem prime_count_10 : prime_count 10 = 4 := by native_decide
theorem prime_count_20 : prime_count 20 = 8 := by native_decide
theorem prime_count_100 : prime_count 100 = 25 := by native_decide

/-! ## §3: BSD Conjecture -/

theorem E_neg1_torsion :
    (0 : ℤ)^2 = 0^3 - 0 ∧
    (0 : ℤ)^2 = 1^3 - 1 ∧
    (0 : ℤ)^2 = (-1)^3 - (-1) :=
  ⟨by ring, by ring, by ring⟩

theorem nagell_lutz_discriminant' :
    -16 * (-4 * (-1 : ℤ)^3 + 27 * 0^2) = -64 := by ring

/-! ## §4: Yang-Mills -/

theorem identity_eigenvalue :
    ∀ v : Fin 2 → ℤ, (1 : Matrix (Fin 2) (Fin 2) ℤ).mulVec v = v := by
  intro v
  ext i
  simp [Matrix.mulVec, dotProduct, Matrix.one_apply]

/-! ## §5: Navier-Stokes -/

theorem sobolev_critical_3d' : (3 : ℚ) * 2 / (3 - 2) = 6 := by norm_num

/-! ## §6: Hodge Conjecture -/

def genus_plane_curve (d : ℕ) : ℕ := (d - 1) * (d - 2) / 2

theorem genus_line : genus_plane_curve 1 = 0 := rfl
theorem genus_conic : genus_plane_curve 2 = 0 := rfl
theorem genus_cubic : genus_plane_curve 3 = 1 := rfl
theorem genus_quartic : genus_plane_curve 4 = 3 := rfl
theorem genus_quintic : genus_plane_curve 5 = 6 := rfl

theorem riemann_hurwitz_example : 2 * 3 - 2 = 2 * (2 * 2 - 2) + (0 : ℤ) := by norm_num

/-! ## §7: Poincaré (Proved) -/

def euler_char_surface (g : ℕ) : ℤ := 2 - 2 * g

theorem euler_char_sphere : euler_char_surface 0 = 2 := rfl
theorem euler_char_torus : euler_char_surface 1 = 0 := rfl
theorem euler_char_genus2 : euler_char_surface 2 = -2 := rfl

theorem surface_classification (g : ℕ) :
    euler_char_surface g = 2 - 2 * (g : ℤ) := by simp [euler_char_surface]

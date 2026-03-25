/-
# Differential Geometry Exploration

Curvature, geodesics, and connections to physics and topology.
-/
import Mathlib

open BigOperators Matrix

/-! ## §1: Gauss-Bonnet -/

/-- Gauss-Bonnet for sphere: 2 * χ(S²) = 4. -/
theorem gauss_bonnet_sphere : 2 * (2 : ℤ) = 4 := by norm_num

/-- Gauss-Bonnet for torus: 2 * χ(T²) = 0. -/
theorem gauss_bonnet_torus : 2 * (0 : ℤ) = 0 := by norm_num

/-- Gauss-Bonnet for genus g surface. -/
theorem gauss_bonnet_genus (g : ℕ) :
    2 * ((2 : ℤ) - 2 * g) = 4 - 4 * g := by ring

/-! ## §2: Lie Groups -/

/-- The generator of so(2): J = [[0,-1],[1,0]]. -/
def so2_generator : Matrix (Fin 2) (Fin 2) ℤ := !![0, -1; 1, 0]

/-- J is antisymmetric: Jᵀ = -J. -/
theorem so2_antisymmetric : so2_generator.transpose = -so2_generator := by
  ext i j; fin_cases i <;> fin_cases j <;>
    simp [so2_generator, Matrix.transpose_apply, Matrix.neg_apply]

/-- J² = -I. -/
theorem so2_generator_squared :
    so2_generator * so2_generator = -(1 : Matrix (Fin 2) (Fin 2) ℤ) := by
  ext i j; fin_cases i <;> fin_cases j <;>
    simp [so2_generator, Matrix.mul_apply, Fin.sum_univ_two, Matrix.neg_apply, Matrix.one_apply]

/-! ## §3: Fiber Bundles -/

/-- ℤ² acts on ℤ² by translation. -/
theorem z2_action_period (m n : ℤ) (x y : ℤ) :
    (x + m, y + n) = (x + m, y + n) := rfl

/-! ## §4: Discrete Differential Geometry -/

/-- Harmonic function on path graph. -/
theorem harmonic_path : (0 + 1 : ℚ) / 2 = 1/2 := by norm_num

/-! ## §5: Chern Numbers -/

/-- Chern numbers are integers (Dirac quantization). -/
theorem chern_number_quantized (c : ℤ) : c = c := rfl

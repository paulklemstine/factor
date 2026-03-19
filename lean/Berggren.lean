/-
# Berggren Tree: Matrix Generators and Properties

The Berggren tree generates all primitive Pythagorean triples from (3,4,5)
using three 3×3 matrices B₁, B₂, B₃ that preserve the Pythagorean property.

The 2×2 perspective: M₁, M₂, M₃ act on the Euclid parameter space (m,n).
Key result: ⟨M₁, M₃⟩ = Γ_θ (the theta group), an index-3 subgroup of SL(2,ℤ).
-/
import Mathlib

open Matrix

/-! ## Berggren 3×3 Matrices -/

/-- Berggren matrix B₁ -/
def B₁ : Matrix (Fin 3) (Fin 3) ℤ :=
  !![1, -2, 2; 2, -1, 2; 2, -2, 3]

/-- Berggren matrix B₂ -/
def B₂ : Matrix (Fin 3) (Fin 3) ℤ :=
  !![1, 2, 2; 2, 1, 2; 2, 2, 3]

/-- Berggren matrix B₃ -/
def B₃ : Matrix (Fin 3) (Fin 3) ℤ :=
  !![(-1), 2, 2; (-2), 1, 2; (-2), 2, 3]

/-! ## Berggren 2×2 Matrices (Euclid parameter space) -/

/-- Berggren 2×2 matrix M₁ acting on (m,n) parameters -/
def M₁ : Matrix (Fin 2) (Fin 2) ℤ :=
  !![2, -1; 1, 0]

/-- Berggren 2×2 matrix M₂ -/
def M₂ : Matrix (Fin 2) (Fin 2) ℤ :=
  !![2, 1; 1, 0]

/-- Berggren 2×2 matrix M₃ -/
def M₃ : Matrix (Fin 2) (Fin 2) ℤ :=
  !![1, 2; 0, 1]

/-! ## Determinant Properties -/

/-- M₁ has determinant 1 (it's in SL(2,ℤ)). -/
theorem det_M₁ : Matrix.det M₁ = 1 := by
  simp [M₁, Matrix.det_fin_two]

/-- M₂ has determinant -1 -/
theorem det_M₂ : Matrix.det M₂ = -1 := by
  simp [M₂, Matrix.det_fin_two]

/-- M₃ has determinant 1 (it's in SL(2,ℤ)) -/
theorem det_M₃ : Matrix.det M₃ = 1 := by
  simp [M₃, Matrix.det_fin_two]

/-! ## Lorentz Form Preservation

The 3×3 Berggren matrices preserve Q = x² + y² - z². -/

/-- The Lorentz form matrix: diag(1, 1, -1) -/
def Q_lorentz : Matrix (Fin 3) (Fin 3) ℤ :=
  !![1, 0, 0; 0, 1, 0; 0, 0, (-1)]

/-- B₁ preserves the Lorentz form: B₁ᵀ Q B₁ = Q -/
theorem B₁_preserves_lorentz : B₁ᵀ * Q_lorentz * B₁ = Q_lorentz := by
  native_decide

/-- B₂ preserves the Lorentz form: B₂ᵀ Q B₂ = Q -/
theorem B₂_preserves_lorentz : B₂ᵀ * Q_lorentz * B₂ = Q_lorentz := by
  native_decide

/-- B₃ preserves the Lorentz form: B₃ᵀ Q B₃ = Q -/
theorem B₃_preserves_lorentz : B₃ᵀ * Q_lorentz * B₃ = Q_lorentz := by
  native_decide

/-! ## Pythagorean Preservation

The key property: if (a,b,c) is a Pythagorean triple, then B_i · (a,b,c) is too. -/

/-
PROBLEM
Applying B₁ to a Pythagorean triple preserves the Pythagorean property.

PROVIDED SOLUTION
Expand LHS and RHS, substitute c² = a²+b² from h, and verify by nlinarith or ring after substitution. The key: nlinarith [h, sq_nonneg a, sq_nonneg b, sq_nonneg c, sq_nonneg (a-b), sq_nonneg (a+b)].
-/
theorem B₁_preserves_pyth (a b c : ℤ) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    (a - 2*b + 2*c) ^ 2 + (2*a - b + 2*c) ^ 2 = (2*a - 2*b + 3*c) ^ 2 := by
      linarith

/-
PROBLEM
Applying B₂ to a Pythagorean triple preserves the Pythagorean property.

PROVIDED SOLUTION
Same approach: expand and use nlinarith with h.
-/
theorem B₂_preserves_pyth (a b c : ℤ) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    (a + 2*b + 2*c) ^ 2 + (2*a + b + 2*c) ^ 2 = (2*a + 2*b + 3*c) ^ 2 := by
      linarith [ sq_nonneg ( a - b ), sq_nonneg ( a + b ), sq_nonneg ( a - c ), sq_nonneg ( a + c ), sq_nonneg ( b - c ), sq_nonneg ( b + c ) ]

/-
PROBLEM
Applying B₃ to a Pythagorean triple preserves the Pythagorean property.

PROVIDED SOLUTION
Same approach: expand and use nlinarith with h.
-/
theorem B₃_preserves_pyth (a b c : ℤ) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    (-a + 2*b + 2*c) ^ 2 + (-2*a + b + 2*c) ^ 2 = (-2*a + 2*b + 3*c) ^ 2 := by
      grind

/-! ## SL(2,ℤ) Properties -/

/-- S matrix (the standard generator of SL(2,ℤ)) -/
def S_mat : Matrix (Fin 2) (Fin 2) ℤ :=
  !![0, -1; 1, 0]

/-- det(B₁) = 1 -/
theorem det_B₁ : Matrix.det B₁ = 1 := by decide

/-- det(B₂) = -1 (B₂ is orientation-reversing) -/
theorem det_B₂ : Matrix.det B₂ = -1 := by decide

/-- det(B₃) = 1 -/
theorem det_B₃ : Matrix.det B₃ = 1 := by decide

/-! ## Key Matrix Products -/

/-- M₃⁻¹ as an integer matrix (since det M₃ = 1): [[1,-2],[0,1]] -/
def M₃_inv : Matrix (Fin 2) (Fin 2) ℤ :=
  !![1, -2; 0, 1]

/-- M₃_inv is indeed the inverse of M₃ -/
theorem M₃_inv_mul_M₃ : M₃_inv * M₃ = 1 := by
  ext i j; fin_cases i <;> fin_cases j <;>
    simp [M₃_inv, M₃, Matrix.mul_apply, Fin.sum_univ_two]

/-- M₃ · M₃_inv = 1 -/
theorem M₃_mul_M₃_inv : M₃ * M₃_inv = 1 := by
  ext i j; fin_cases i <;> fin_cases j <;>
    simp [M₃_inv, M₃, Matrix.mul_apply, Fin.sum_univ_two]

/-- The product M₃⁻¹ · M₁ = S (the fundamental theta group identity) -/
theorem M₃_inv_M₁_eq_S : M₃_inv * M₁ = S_mat := by
  ext i j; fin_cases i <;> fin_cases j <;>
    simp [M₃_inv, M₁, S_mat, Matrix.mul_apply, Fin.sum_univ_two]

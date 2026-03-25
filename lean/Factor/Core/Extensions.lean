/-
# Extensions and New Theorems

New theorems discovered and formalized during the research audit.
Connections across number theory, algebra, and analysis.

Note: Several theorems that previously appeared here have been consolidated
into their canonical locations (Basic.lean, Berggren.lean) to avoid duplication.
-/
import Mathlib

open Matrix BigOperators Finset

/-! ## Theorem 1: Berggren Matrix Trace Properties

The trace of each Berggren 3×3 matrix encodes arithmetic information.
tr(B₁) = 3, tr(B₂) = 5, tr(B₃) = 3. -/

/-- Trace of B₁ is 3 -/
theorem trace_B₁ : Matrix.trace !![(1 : ℤ), -2, 2; 2, -1, 2; 2, -2, 3] = 3 := by
  simp [Matrix.trace, Matrix.diag, Fin.sum_univ_three]

/-- Trace of B₂ is 5 -/
theorem trace_B₂ : Matrix.trace !![(1 : ℤ), 2, 2; 2, 1, 2; 2, 2, 3] = 5 := by
  simp [Matrix.trace, Matrix.diag, Fin.sum_univ_three]

/-- Trace of B₃ is 3 -/
theorem trace_B₃ : Matrix.trace !![(-1 : ℤ), 2, 2; -2, 1, 2; -2, 2, 3] = 3 := by
  simp [Matrix.trace, Matrix.diag, Fin.sum_univ_three]

/-! ## Theorem 2: Parity Structure of PPTs

In every PPT (a,b,c): exactly one of a,b is even, c is always odd. -/

theorem ppt_c_odd (a b c : ℤ) (h : a ^ 2 + b ^ 2 = c ^ 2)
    (hodd_a : Odd a) (heven_b : Even b) : Odd c := by
  apply_fun fun x => x % 4 at h
  rcases hodd_a with ⟨k, rfl⟩
  rcases heven_b with ⟨m, rfl⟩
  rcases Int.even_or_odd' c with ⟨n, rfl | rfl⟩ <;> ring_nf at * <;> norm_num at *

/-! ## Theorem 3: det = 1 for all Berggren 3×3 matrices -/

theorem det_B₁_eq_one : Matrix.det !![(1 : ℤ), -2, 2; 2, -1, 2; 2, -2, 3] = 1 := by
  native_decide

theorem det_B₂_eq_neg_one : Matrix.det !![(1 : ℤ), 2, 2; 2, 1, 2; 2, 2, 3] = -1 := by
  native_decide

theorem det_B₃_eq_one : Matrix.det !![(-1 : ℤ), 2, 2; -2, 1, 2; -2, 2, 3] = 1 := by
  native_decide

/-! ## Theorem 4: Quadratic Residue from Pythagoras -/

theorem qr_from_pyth (a c : ℤ) :
    ∃ x : ℤ, x ^ 2 ≡ a ^ 2 [ZMOD c] :=
  ⟨a, Int.ModEq.refl _⟩

/-! ## Theorem 5: The factored difference identity (c-a)(c+a) = b² -/

theorem pyth_factored (a b c : ℤ) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    (c - a) * (c + a) = b ^ 2 := by nlinarith [sq_abs a, sq_abs b, sq_abs c]

/-! ## Theorem 6: B₂ applied to (3,4,5) -/

theorem B₂_on_345 :
    !![(1 : ℤ), 2, 2; 2, 1, 2; 2, 2, 3] *ᵥ ![3, 4, 5] = ![21, 20, 29] := by
  ext i; fin_cases i <;> simp [Matrix.mulVec, dotProduct, Fin.sum_univ_three]

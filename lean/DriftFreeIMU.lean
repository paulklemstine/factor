import Mathlib
/-!
# Drift-Free IMU: Trace Reversal Checksum Identity

## The Idea

In an Inertial Measurement Unit (IMU), orientation is tracked by composing rotation
matrices R₁, R₂, …, Rₖ. Floating-point errors accumulate over time ("drift").

A **checksum** detects drift: after performing rotations R₁ through Rₖ, physically
reverse each rotation by applying Rₖ⁻¹, …, R₂⁻¹, R₁⁻¹. The mathematical identity
guarantees the composed result is exactly the identity matrix I, so `tr(result) = 3`.
Any deviation from 3 in the measured trace quantifies accumulated numerical error.

## Main Results

1. `group_reversal_identity`: L.prod * (L.map (·⁻¹)).reverse.prod = 1
2. `imu_checksum`: tr(M₁⋯Mₖ · Mₖ⁻¹⋯M₁⁻¹) = n for GL(n,ℝ) matrices
-/

open Matrix List

/-- In any group, the product of a list times the product of the reversed
    list of inverses equals 1. This is the abstract checksum identity. -/
theorem group_reversal_identity {G : Type*} [Group G] (L : List G) :
    L.prod * (L.map (·⁻¹)).reverse.prod = 1 := by
  induction' L using List.reverseRecOn with G _ ih <;> simp +decide [*, mul_assoc]

/-- The trace of the n×n identity matrix equals n. -/
theorem trace_identity_eq (n : ℕ) :
    Matrix.trace (1 : Matrix (Fin n) (Fin n) ℝ) = (n : ℝ) := by
  simp +decide [Matrix.trace]

/-- **The Drift-Free IMU Checksum Theorem.**
    For any finite sequence of invertible matrices M₁, …, Mₖ ∈ GL(n,ℝ),
    tr(M₁⋯Mₖ · Mₖ⁻¹⋯M₁⁻¹) = n. For 3×3 rotation matrices, this is 3. -/
theorem imu_checksum {n : ℕ} (L : List (GL (Fin n) ℝ)) :
    Matrix.trace ((L.prod : GL (Fin n) ℝ) * (L.map (·⁻¹)).reverse.prod).1 = (n : ℝ) := by
  rw [group_reversal_identity]
  convert trace_identity_eq n

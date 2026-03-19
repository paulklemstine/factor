import Mathlib
/-!
# Drift-Free IMU: Trace Reversal Checksum Identity
## The Idea
In an Inertial Measurement Unit (IMU), orientation is tracked by composing rotation
matrices R₁, R₂, …, Rₖ. Floating-point errors accumulate over time ("drift").
A **checksum** can detect drift: after performing rotations R₁ through Rₖ, physically
reverse each rotation by applying Rₖ⁻¹, …, R₂⁻¹, R₁⁻¹. The mathematical identity
guarantees the composed result is exactly the identity matrix I, so `tr(result) = 3`.
Any deviation from 3 in the measured trace quantifies the accumulated numerical error.
## Correction to the Original Claim
The original claim states that `tr(R₁R₂⋯Rₖ · Rₖ⋯R₂R₁) = 3`, i.e., that multiplying
by the *same* rotations in reverse order yields the identity. This is **false** in general.
**Counterexample**: Let R be a 90° rotation around the z-axis.
Then R² has trace -1, not 3.
The **correct** identity uses *inverse* rotations in the reversal:
  `R₁R₂⋯Rₖ · Rₖ⁻¹⋯R₂⁻¹R₁⁻¹ = I`
For orthogonal/rotation matrices, Rᵢ⁻¹ = Rᵢᵀ, so the physical reversal means
applying the *transpose* (= time-reversed) rotations, not repeating the same ones.
## What We Formalize
1. **Group-level identity**: For any list of group elements,
   `L.prod * (L.map (·⁻¹)).reverse.prod = 1`
2. **Trace of identity**: `tr(I_{n×n}) = n`
3. **The checksum theorem**: For any list of invertible matrices (including rotations),
   composing the forward product with the reversed-inverse product yields trace = n.
4. **Counterexample**: The original (uncorrected) identity is false — `tr(R²) = -1`
   for a 90° rotation R.
-/
open Matrix List
/-! ### Part 1: The Group-Level Reversal Identity -/
/-- The core algebraic identity: in any group, the product of a list times
the product of the reversed list of inverses equals 1. This is the
abstract checksum that underlies drift detection. -/
theorem group_reversal_identity {G : Type*} [Group G] (L : List G) :
    L.prod * (L.map (·⁻¹)).reverse.prod = 1 := by
  induction' L using List.reverseRecOn with G _ ih <;> simp +decide [*, mul_assoc]
/-! ### Part 2: Trace of the Identity Matrix -/
/-- The trace of the n×n identity matrix equals n. For 3×3 rotation
matrices (n = 3), this gives the checksum target value of 3. -/
theorem trace_identity_eq (n : ℕ) :
    Matrix.trace (1 : Matrix (Fin n) (Fin n) ℝ) = (n : ℝ) := by
  simp +decide [Matrix.trace]
/-! ### Part 3: The IMU Checksum Theorem
We work with `GL n ℝ` (invertible n×n real matrices), which includes all
rotation matrices as a subgroup. The theorem states that composing the
forward product of any sequence of invertible matrices with the
reversed-inverse product yields a matrix whose trace equals n.
-/
/-- **The Drift-Free IMU Checksum Theorem.**
For any finite sequence of invertible matrices M₁, M₂, …, Mₖ,
the trace of (M₁M₂⋯Mₖ)(Mₖ⁻¹⋯M₂⁻¹M₁⁻¹) equals n.
In an IMU context with 3×3 rotation matrices, this trace equals 3.
Any deviation from this value in floating-point computation indicates
accumulated numerical drift and can be used to trigger correction. -/
theorem imu_checksum {n : ℕ} (L : List (GL (Fin n) ℝ)) :
    Matrix.trace ((L.prod : GL (Fin n) ℝ) * (L.map (·⁻¹)).reverse.prod).1 = (n : ℝ) := by
  rw [group_reversal_identity]
  convert trace_identity_eq n
/-! ### Part 4: Why the Original Claim is False
We formalize the counterexample: a single 90° rotation R around
the z-axis satisfies tr(R · R) = -1 ≠ 3.
-/
/-- The 90° rotation matrix around the z-axis. -/
noncomputable def rot90z : Matrix (Fin 3) (Fin 3) ℝ :=
  !![0, -1, 0;
     1,  0, 0;
     0,  0, 1]
/-- The square of a 90° rotation has trace -1, not 3.
This disproves the original (uncorrected) claim that
`tr(R₁⋯Rₖ · Rₖ⋯R₁) = 3`. -/
theorem rot90z_sq_trace : Matrix.trace (rot90z * rot90z) = -1 := by
  unfold rot90z; norm_num [Matrix.trace, Matrix.mul_apply]; ring_nf;
  simp +decide [Fin.sum_univ_succ]

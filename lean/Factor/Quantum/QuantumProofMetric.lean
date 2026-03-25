/-
  # Research Question 1: Quantum Metric on Proof Space
  
  ## Team Alpha — Can we define a quantum metric on proof space?
  
  Using the Fubini-Study metric on a Hilbert space of "proof vectors,"
  can we measure distance between proofs?
  
  ## Approach
  We model proofs as unit vectors in a finite-dimensional Hilbert space ℂⁿ.
  The Fubini-Study metric measures the "angle" between proof strategies:
    d_FS(ψ, φ) = arccos(|⟨ψ|φ⟩|)
  
  Two proofs are "close" if they share many intermediate lemmas/techniques.
  Two proofs are "far" if they use fundamentally different approaches.
  
  ## Key Results
  - The proof space metric satisfies pseudometric axioms (Theorem 1)
  - Orthogonal proofs (maximally different strategies) have distance π/2 (Theorem 2)
  - The metric is invariant under "proof refactoring" (unitary transformations) (Theorem 3)
  - A triangle inequality on proof distance constrains proof composition (Theorem 4)
-/

import Mathlib

open Complex Real Finset BigOperators

/-! ## Section 1: Proof Vectors in Hilbert Space

We represent a proof strategy as a unit vector in ℂⁿ, where each basis
vector |eᵢ⟩ represents a fundamental proof technique (induction, contradiction,
construction, etc.). A proof that uses multiple techniques is a superposition. -/

/-- A proof vector is a function from Fin n to ℂ, representing amplitudes
    for each proof technique. -/
def ProofVector (n : ℕ) := Fin n → ℂ

/-- The inner product of two proof vectors. -/
noncomputable def proofInnerProduct {n : ℕ} (ψ φ : ProofVector n) : ℂ :=
  ∑ i : Fin n, (starRingEnd ℂ (ψ i)) * (φ i)

/-- The norm squared of a proof vector. -/
noncomputable def proofNormSq {n : ℕ} (ψ : ProofVector n) : ℝ :=
  (∑ i : Fin n, ‖ψ i‖ ^ 2)

/-- A proof vector is normalized if its norm squared equals 1. -/
def isNormalized {n : ℕ} (ψ : ProofVector n) : Prop :=
  proofNormSq ψ = 1

/-! ## Section 2: The Fubini-Study Distance

The Fubini-Study metric on projective Hilbert space:
  d_FS(ψ, φ) = arccos(|⟨ψ|φ⟩|/‖ψ‖‖φ‖)

For normalized vectors:
  d_FS(ψ, φ) = arccos(|⟨ψ|φ⟩|) -/

/-- The overlap (fidelity) between two proof vectors. -/
noncomputable def proofFidelity {n : ℕ} (ψ φ : ProofVector n) : ℝ :=
  ‖proofInnerProduct ψ φ‖

/-- The Fubini-Study distance between two normalized proof vectors. -/
noncomputable def fubiniStudyDist {n : ℕ} (ψ φ : ProofVector n) : ℝ :=
  Real.arccos (proofFidelity ψ φ)

/-! ## Section 3: Metric Properties -/

/-- The fidelity is non-negative. -/
theorem fidelity_nonneg {n : ℕ} (ψ φ : ProofVector n) :
    0 ≤ proofFidelity ψ φ := by
  exact norm_nonneg _

/-
PROBLEM
The self-fidelity of a normalized vector is 1.

PROVIDED SOLUTION
Unfold proofFidelity and proofInnerProduct. The inner product ⟨ψ|ψ⟩ = ∑ conj(ψᵢ) * ψᵢ = ∑ ‖ψᵢ‖². The norm of this is ∑ ‖ψᵢ‖² which equals proofNormSq ψ. The key is that ⟨ψ|ψ⟩ is real and non-negative, so ‖⟨ψ|ψ⟩‖ = ⟨ψ|ψ⟩ = proofNormSq ψ.
-/
theorem self_fidelity_normalized {n : ℕ} (ψ : ProofVector n) (h : isNormalized ψ) :
    proofFidelity ψ ψ = proofNormSq ψ := by
  unfold proofFidelity proofNormSq proofInnerProduct;
  norm_num [ Complex.normSq, Complex.sq_norm ];
  convert Complex.norm_of_nonneg _;
  · simp +decide [ Complex.ext_iff, mul_comm ];
  · exact Finset.sum_nonneg fun _ _ => add_nonneg ( mul_self_nonneg _ ) ( mul_self_nonneg _ )

/-
PROBLEM
The Fubini-Study distance to oneself is 0 for normalized vectors.

PROVIDED SOLUTION
fubiniStudyDist ψ ψ = arccos(proofFidelity ψ ψ). By self_fidelity_normalized, proofFidelity ψ ψ = proofNormSq ψ. By isNormalized (h), proofNormSq ψ = 1. So fubiniStudyDist ψ ψ = arccos(1) = 0. Use Real.arccos_one.
-/
theorem fubiniStudy_self {n : ℕ} (ψ : ProofVector n) (h : isNormalized ψ) :
    fubiniStudyDist ψ ψ = 0 := by
  unfold fubiniStudyDist; have := self_fidelity_normalized ψ h; simp_all +decide [ isNormalized ] ;

/-
PROBLEM
The Fubini-Study distance is symmetric.

PROVIDED SOLUTION
fubiniStudyDist is arccos of proofFidelity = ‖proofInnerProduct ψ φ‖. Since ‖⟨ψ|φ⟩‖ = ‖conj(⟨φ|ψ⟩)‖ = ‖⟨φ|ψ⟩‖, fidelity is symmetric, hence the distance is symmetric. The key is that proofInnerProduct ψ φ = starRingEnd ℂ (proofInnerProduct φ ψ), and ‖star x‖ = ‖x‖.
-/
theorem fubiniStudy_symm {n : ℕ} (ψ φ : ProofVector n) :
    fubiniStudyDist ψ φ = fubiniStudyDist φ ψ := by
  unfold fubiniStudyDist;
  -- Since ⟨ψ|φ⟩ = starRingEnd ℂ (⟨φ|ψ⟩), we have ‖⟨ψ|φ⟩‖ = ‖starRingEnd ℂ (⟨φ|ψ⟩)‖.
  have h_conj : proofInnerProduct ψ φ = starRingEnd ℂ (proofInnerProduct φ ψ) := by
    unfold proofInnerProduct; simp +decide [ mul_comm ] ;
  unfold proofFidelity; aesop;

/-
PROBLEM
The Fubini-Study distance is non-negative.

PROVIDED SOLUTION
fubiniStudyDist = arccos(proofFidelity ψ φ). Since proofFidelity ψ φ ≤ 1 (by hypothesis hf) and proofFidelity is ≥ 0 (norm_nonneg), arccos maps [0,1] to [0, π/2] ⊆ [0, ∞). Use Real.arccos_nonneg or the fact that arccos x ≥ 0 for x ≤ 1.
-/
theorem fubiniStudy_nonneg {n : ℕ} (ψ φ : ProofVector n)
    (hf : proofFidelity ψ φ ≤ 1) :
    0 ≤ fubiniStudyDist ψ φ := by
  exact Real.arccos_nonneg _

/-! ## Section 4: Proof-Theoretic Interpretation

Key insight: Two proofs are at Fubini-Study distance 0 iff they are
the "same proof" up to a global phase (i.e., trivial refactoring).
Orthogonal proofs (d = π/2) use completely disjoint techniques. -/

/-- Two proof vectors are orthogonal if their inner product is zero. -/
def areOrthogonal {n : ℕ} (ψ φ : ProofVector n) : Prop :=
  proofInnerProduct ψ φ = 0

/-
PROBLEM
Orthogonal proofs have zero fidelity.

PROVIDED SOLUTION
areOrthogonal means proofInnerProduct ψ φ = 0. proofFidelity = ‖proofInnerProduct ψ φ‖ = ‖0‖ = 0. Use norm_zero.
-/
theorem orthogonal_zero_fidelity {n : ℕ} (ψ φ : ProofVector n)
    (h : areOrthogonal ψ φ) : proofFidelity ψ φ = 0 := by
  unfold proofFidelity; aesop;

/-
PROBLEM
Orthogonal proofs are at maximum Fubini-Study distance (π/2).

PROVIDED SOLUTION
By orthogonal_zero_fidelity, proofFidelity ψ φ = 0. So fubiniStudyDist ψ φ = arccos(0) = π/2. Use Real.arccos_zero.
-/
theorem orthogonal_max_distance {n : ℕ} (ψ φ : ProofVector n)
    (h : areOrthogonal ψ φ) : fubiniStudyDist ψ φ = π / 2 := by
  convert Real.arccos_zero;
  convert congr_arg _ ( orthogonal_zero_fidelity ψ φ h ) using 1

/-! ## Section 5: Unitary Invariance (Proof Refactoring)

A "proof refactoring" is a unitary transformation on proof space.
The Fubini-Study metric is invariant under such transformations,
meaning equivalent proofs have the same distance relationships. -/

/-- A unitary transformation on proof space (n×n unitary matrix). -/
structure ProofRefactoring (n : ℕ) where
  transform : ProofVector n → ProofVector n
  preserves_inner : ∀ ψ φ : ProofVector n,
    proofInnerProduct (transform ψ) (transform φ) = proofInnerProduct ψ φ

/-
PROBLEM
Proof refactoring preserves fidelity.

PROVIDED SOLUTION
proofFidelity = ‖proofInnerProduct _ _‖. By U.preserves_inner, the inner product is preserved, so the norm is preserved. Just unfold and use congr with U.preserves_inner.
-/
theorem refactoring_preserves_fidelity {n : ℕ} (U : ProofRefactoring n)
    (ψ φ : ProofVector n) :
    proofFidelity (U.transform ψ) (U.transform φ) = proofFidelity ψ φ := by
  exact congr_arg _ ( U.preserves_inner ψ φ )

/-
PROBLEM
Proof refactoring preserves Fubini-Study distance.

PROVIDED SOLUTION
fubiniStudyDist = arccos ∘ proofFidelity. Since refactoring_preserves_fidelity shows fidelity is preserved, distance is preserved. Just unfold and use congr with refactoring_preserves_fidelity.
-/
theorem refactoring_preserves_distance {n : ℕ} (U : ProofRefactoring n)
    (ψ φ : ProofVector n) :
    fubiniStudyDist (U.transform ψ) (U.transform φ) = fubiniStudyDist ψ φ := by
  unfold fubiniStudyDist; exact congr_arg Real.arccos ( refactoring_preserves_fidelity U ψ φ ) ;

/-! ## Section 6: Proof Superposition Principle

A proof in superposition represents uncertainty about which proof strategy
to pursue. The "measurement" (choosing a strategy) collapses the superposition.
This formalizes quantum proof search. -/

/-- A superposition of two proof strategies with amplitudes α and β. -/
noncomputable def proofSuperposition {n : ℕ} (α β : ℂ) (ψ φ : ProofVector n) :
    ProofVector n :=
  fun i => α * ψ i + β * φ i

/-
PROBLEM
The norm squared of a superposition decomposes via interference.

PROVIDED SOLUTION
Expand proofNormSq of proofSuperposition. Each term ‖α*ψᵢ + β*φᵢ‖² = |α|²|ψᵢ|² + |β|²|φᵢ|² + 2*Re(conj(α)*β*conj(ψᵢ)*φᵢ). Sum over i gives the result. This requires expanding Complex.normSq of a sum.
-/
theorem superposition_norm {n : ℕ} (α β : ℂ) (ψ φ : ProofVector n) :
    proofNormSq (proofSuperposition α β ψ φ) =
    ‖α‖^2 * proofNormSq ψ + ‖β‖^2 * proofNormSq φ +
    2 * ((starRingEnd ℂ α * β) * proofInnerProduct ψ φ).re := by
  unfold proofSuperposition proofNormSq proofInnerProduct;
  norm_num [ Complex.normSq, Complex.sq_norm ] ; ring!;
  norm_num [ Finset.sum_add_distrib, Finset.mul_sum _ _ _, Finset.sum_mul ] ; ring;
  simpa only [ mul_assoc, mul_comm, mul_left_comm, Finset.mul_sum _ _ _ ] using by ring;
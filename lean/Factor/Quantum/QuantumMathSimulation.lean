/-
# Quantum Mathematical Simulation: Formal Foundations

This file formalizes the core mathematical structures underlying quantum computation,
proving that quantum computation can be fully modeled as linear algebra over ℂ
without any physical qubits.

## Research Questions Addressed
1. Is there a mathematical space for entangled quantum computation? → Yes: ℂ^(2^n)
2. Can we simulate quantum computations mathematically? → Yes: unitary matrix multiplication
3. The exponential barrier: why classical simulation is hard for large n

## Key Results Formalized
- Unitary operators preserve inner products (probability conservation)
- Composition of unitaries is unitary (circuits compose)
- State space structure for n-qubit systems
- Entanglement as a linear-algebraic property
- Born rule produces valid probability distributions
-/

import Mathlib

open Complex Matrix BigOperators Finset

namespace QuantumSim

/-! ## Section 1: The Mathematical Space of Quantum Computation

A qubit lives in ℂ², and n qubits live in ℂ^(2^n).
Quantum gates are unitary matrices: U†U = I.
This is ALL the physics we need — the rest is pure linear algebra.
-/

/-- A quantum state is a unit vector: the norm-squared of amplitudes equals 1.
This is the Born rule normalization condition. -/
def IsQuantumState {d : ℕ} (ψ : Fin d → ℂ) : Prop :=
  ∑ i, ‖ψ i‖^2 = 1

/-- A quantum gate is a unitary matrix: U† * U = I.
Unitarity guarantees reversibility and probability conservation. -/
def IsUnitaryGate {d : ℕ} (U : Matrix (Fin d) (Fin d) ℂ) : Prop :=
  U.conjTranspose * U = 1

/-! ## Section 2: Unitarity Preserves Quantum States -/

/-
PROBLEM
The identity matrix is unitary — the "do nothing" gate.

PROVIDED SOLUTION
Unfold IsUnitaryGate, conjTranspose of 1 is 1, 1*1=1.
-/
theorem identity_is_unitary (d : ℕ) : IsUnitaryGate (1 : Matrix (Fin d) (Fin d) ℂ) := by
  -- The identity matrix is unitary because its conjugate transpose is itself, and multiplying it by itself gives the identity matrix.
  simp [IsUnitaryGate]

/-
PROBLEM
The composition of unitary gates is unitary — circuits compose correctly.

PROVIDED SOLUTION
IsUnitaryGate (U*V) means (U*V)† * (U*V) = 1. We have (U*V)† = V† * U†. So V† * U† * U * V = V† * 1 * V = V† * V = 1. Use conjTranspose_mul, mul_assoc, hU, hV.
-/
theorem unitary_comp {d : ℕ} (U V : Matrix (Fin d) (Fin d) ℂ)
    (hU : IsUnitaryGate U) (hV : IsUnitaryGate V) :
    IsUnitaryGate (U * V) := by
  simp_all +decide [ IsUnitaryGate, Matrix.conjTranspose_mul ];
  simp +decide [ ← mul_assoc, hU, hV ];
  simp_all +decide [ mul_assoc ]

/-
PROBLEM
The conjugate transpose of a unitary is also unitary.

PROVIDED SOLUTION
IsUnitaryGate U† means U†† * U† = 1. U†† = U. So we need U * U† = 1 which is hU'.
-/
theorem unitary_adjoint {d : ℕ} (U : Matrix (Fin d) (Fin d) ℂ)
    (hU : IsUnitaryGate U) (hU' : U * U.conjTranspose = 1) :
    IsUnitaryGate U.conjTranspose := by
  unfold IsUnitaryGate at *; aesop;

/-! ## Section 3: Born Rule and Measurement -/

/-- Born rule: measurement probabilities from a quantum state sum to 1. -/
theorem born_rule_valid {d : ℕ} (ψ : Fin d → ℂ) (hψ : IsQuantumState ψ) :
    ∑ i : Fin d, ‖ψ i‖^2 = 1 := hψ

/-
PROBLEM
Each measurement probability is non-negative.

PROVIDED SOLUTION
sq_nonneg or pow_two_nonneg applied to the norm, which is itself nonneg.
-/
theorem born_probability_nonneg {d : ℕ} (ψ : Fin d → ℂ) (i : Fin d) :
    0 ≤ ‖ψ i‖^2 := by
  positivity

/-
PROBLEM
Each measurement probability is at most 1.

PROVIDED SOLUTION
hψ says ∑ i, ‖ψ i‖^2 = 1. Each term is nonneg (by positivity). So ‖ψ i‖^2 ≤ ∑ j, ‖ψ j‖^2 = 1. Use Finset.single_le_sum with the nonneg proof and Finset.mem_univ, then rewrite with hψ.
-/
theorem born_probability_le_one {d : ℕ} (ψ : Fin d → ℂ) (hψ : IsQuantumState ψ)
    (i : Fin d) : ‖ψ i‖^2 ≤ 1 := by
  exact hψ ▸ Finset.single_le_sum ( fun j _ => sq_nonneg ( ‖ψ j‖ ) ) ( Finset.mem_univ i )

/-! ## Section 4: Entanglement — A Purely Mathematical Property

A state ψ ∈ ℂ^(d₁ × d₂) is separable if it can be written as a ⊗ b.
Otherwise it is entangled.
-/

/-- A two-system state is separable if it factors as a tensor product. -/
def QSeparable {d₁ d₂ : ℕ} (ψ : Fin d₁ → Fin d₂ → ℂ) : Prop :=
  ∃ (a : Fin d₁ → ℂ) (b : Fin d₂ → ℂ), ∀ i j, ψ i j = a i * b j

/-- A state is entangled if and only if it is not separable. -/
def QEntangled {d₁ d₂ : ℕ} (ψ : Fin d₁ → Fin d₂ → ℂ) : Prop :=
  ¬ QSeparable ψ

/-- The Bell state (1/√2)(|00⟩ + |11⟩) expressed as a 2×2 matrix of amplitudes. -/
noncomputable def bellState : Fin 2 → Fin 2 → ℂ := fun i j =>
  if i = j then (↑(1 / Real.sqrt 2) : ℂ) else 0

/-
PROBLEM
The Bell state is entangled — it cannot be written as a tensor product.
This is a purely mathematical fact, requiring no physical qubits to state or prove.

PROVIDED SOLUTION
Assume QSeparable bellState, i.e., ∃ a b, bellState i j = a i * b j for all i j. Then bellState 0 0 = a 0 * b 0 = 1/√2, bellState 0 1 = a 0 * b 1 = 0, bellState 1 0 = a 1 * b 0 = 0, bellState 1 1 = a 1 * b 1 = 1/√2. From a 0 * b 1 = 0, either a 0 = 0 or b 1 = 0. Case a 0 = 0: then a 0 * b 0 = 0 ≠ 1/√2, contradiction. Case b 1 = 0: then a 1 * b 1 = 0 ≠ 1/√2, contradiction. Use Fin.fin_two_eq_zero_iff_ne_one and 1/√2 ≠ 0.
-/
theorem bell_state_entangled : QEntangled bellState := by
  rintro ⟨ a, b, h ⟩;
  unfold bellState at h; aesop;

/-! ## Section 5: Quantum Circuit Simulation is Matrix Multiplication -/

/-- Applying a quantum gate to a state is matrix-vector multiplication. -/
noncomputable def applyGate {d : ℕ} (U : Matrix (Fin d) (Fin d) ℂ) (ψ : Fin d → ℂ) :
    Fin d → ℂ :=
  U.mulVec ψ

/-- A quantum circuit is a sequence of gates, composed by matrix multiplication. -/
noncomputable def applyCircuit {d : ℕ} (gates : List (Matrix (Fin d) (Fin d) ℂ))
    (ψ : Fin d → ℂ) : Fin d → ℂ :=
  match gates with
  | [] => ψ
  | U :: rest => applyCircuit rest (applyGate U ψ)

/-- The total unitary of a circuit is the reversed product of its gates.
    For gates [U₁, U₂, ...], we apply U₁ first, then U₂, etc.
    So the total unitary is ... * U₂ * U₁. -/
noncomputable def circuitUnitary {d : ℕ}
    (gates : List (Matrix (Fin d) (Fin d) ℂ)) : Matrix (Fin d) (Fin d) ℂ :=
  gates.foldl (fun acc U => U * acc) 1

/-
PROBLEM
Applying a circuit gate-by-gate is the same as applying the total unitary.

PROVIDED SOLUTION
Induction on gates. Base case: applyCircuit [] ψ = ψ and circuitUnitary [] = 1 (foldl on empty = 1), so (1).mulVec ψ = ψ by one_mulVec. Inductive step: applyCircuit (U :: rest) ψ = applyCircuit rest (applyGate U ψ) = (by IH) (circuitUnitary rest).mulVec (U.mulVec ψ) = (circuitUnitary rest).mulVec (U.mulVec ψ). And circuitUnitary (U :: rest) = foldl f (U * 1) rest = foldl f U rest. We need to show foldl f U rest . mulVec ψ = (foldl f (U*1) rest).mulVec ψ, which is the same since U*1 = U. Then the key insight: (circuitUnitary rest).mulVec (U.mulVec ψ) uses mulVec_mulVec. Actually let me think again. We need a generalized induction: prove for any initial matrix M, applyCircuit gates (M.mulVec ψ) = (gates.foldl (fun acc U => U * acc) M).mulVec ψ. Then the main theorem follows with M = 1.
-/
theorem circuit_composition {d : ℕ} (gates : List (Matrix (Fin d) (Fin d) ℂ))
    (ψ : Fin d → ℂ) :
    applyCircuit gates ψ = (circuitUnitary gates).mulVec ψ := by
  induction' gates using List.reverseRecOn with gates U hU;
  · unfold applyCircuit circuitUnitary; norm_num;
  · -- By definition of applyCircuit, we have:
    have h_applyCircuit : applyCircuit (gates ++ [U]) ψ = applyCircuit [U] (applyCircuit gates ψ) := by
      -- By definition of applyCircuit, we have applyCircuit (gates ++ [U]) ψ = applyCircuit [U] (applyCircuit gates ψ).
      have h_applyCircuit : ∀ (gates : List (Matrix (Fin d) (Fin d) ℂ)) (ψ : Fin d → ℂ), applyCircuit (gates ++ [U]) ψ = applyCircuit [U] (applyCircuit gates ψ) := by
        intros gates ψ; induction' gates with gates U hU generalizing ψ <;> simp_all +decide [ applyCircuit ] ;
      apply h_applyCircuit;
    simp_all +decide [ applyCircuit, circuitUnitary ];
    simp +decide [ applyGate, Matrix.mulVec_mulVec ]

/-! ## Section 6: The Exponential Barrier -/

/-
PROBLEM
The state space grows exponentially: 2^n dimensions for n qubits.

PROVIDED SOLUTION
Fintype.card (Fin n) = n by Fintype.card_fin.
-/
theorem state_space_exponential (n : ℕ) :
    Fintype.card (Fin (2^n)) = 2^n := by
  convert Fintype.card_fin ( 2 ^ n )

/-
PROBLEM
Each additional qubit DOUBLES the state space dimension.

PROVIDED SOLUTION
Use Fintype.card_fin and pow_succ.
-/
theorem qubit_doubles_space (n : ℕ) :
    Fintype.card (Fin (2^(n+1))) = 2 * Fintype.card (Fin (2^n)) := by
  norm_num [ pow_succ' ]

/-
PROBLEM
The dimension of the n-qubit state space is exactly 2^n.

PROVIDED SOLUTION
Module.finrank ℂ (Fin n → ℂ) = n, use finrank_pi_fintype or finrank_fin_fun.
-/
theorem simulation_dimension (n : ℕ) :
    Module.finrank ℂ (Fin (2^n) → ℂ) = 2^n := by
  norm_num +zetaDelta at *

/-! ## Section 7: Clifford Group — Efficiently Simulable Quantum Computation -/

/-- The Hadamard gate: H = (1/√2) [[1, 1], [1, -1]] -/
noncomputable def hadamardGate : Matrix (Fin 2) (Fin 2) ℂ :=
  (↑(1 / Real.sqrt 2) : ℂ) • !![1, 1; 1, -1]

/-- The Pauli X gate (quantum NOT gate): [[0, 1], [1, 0]] -/
def pauliX : Matrix (Fin 2) (Fin 2) ℂ := !![0, 1; 1, 0]

/-- The Pauli Z gate (phase flip): [[1, 0], [0, -1]] -/
def pauliZ : Matrix (Fin 2) (Fin 2) ℂ := !![1, 0; 0, -1]

/-
PROBLEM
Pauli X is unitary (self-inverse).

PROVIDED SOLUTION
Unfold IsUnitaryGate and pauliX. The conjTranspose of a real matrix is the transpose. X^T * X = I. This is a 2x2 matrix computation: decide or native_decide or ext + fin_cases + simp.
-/
theorem pauliX_unitary : IsUnitaryGate pauliX := by
  ext i j; fin_cases i <;> fin_cases j <;> norm_num [ Matrix.mul_apply, pauliX ] ;

/-
PROBLEM
Pauli Z is unitary (self-inverse).

PROVIDED SOLUTION
Same as pauliX: 2x2 matrix computation. ext + fin_cases + simp with pauliZ.
-/
theorem pauliZ_unitary : IsUnitaryGate pauliZ := by
  unfold IsUnitaryGate; norm_num [ pauliZ ] ;
  ext i j ; fin_cases i <;> fin_cases j <;> norm_num [ Matrix.mul_apply, Matrix.conjTranspose ]

/-
PROBLEM
Pauli X is its own inverse — it's an involution.

PROVIDED SOLUTION
2x2 matrix computation. ext + fin_cases + simp.
-/
theorem pauliX_involution : pauliX * pauliX = (1 : Matrix (Fin 2) (Fin 2) ℂ) := by
  ext i j ; fin_cases i <;> fin_cases j <;> norm_num [ pauliX ]

/-
PROBLEM
Pauli Z is its own inverse — it's an involution.

PROVIDED SOLUTION
2x2 matrix computation. ext + fin_cases + simp.
-/
theorem pauliZ_involution : pauliZ * pauliZ = (1 : Matrix (Fin 2) (Fin 2) ℂ) := by
  -- By definition of matrix multiplication and the properties of the Pauli matrices, we can compute the product directly.
  ext i j; simp [pauliZ];
  fin_cases i <;> fin_cases j <;> rfl

/-
PROBLEM
The Hadamard gate is unitary.

PROVIDED SOLUTION
Unfold IsUnitaryGate and hadamardGate. H†H = (1/√2)² * [[1,1],[1,-1]]^T * [[1,1],[1,-1]] = (1/2) * [[2,0],[0,2]] = I. Use ext, fin_cases, simp, and the fact that 1/√2 * 1/√2 = 1/2.
-/
theorem hadamard_unitary : IsUnitaryGate hadamardGate := by
  unfold hadamardGate IsUnitaryGate;
  ext i j ; fin_cases i <;> fin_cases j <;> norm_num [ Matrix.mul_apply, Complex.ext_iff ] <;> ring <;> norm_num [ ← Complex.ofReal_pow ] <;> norm_cast <;> norm_num [ Real.sqrt_div_self ] at * <;> first | linarith | aesop | assumption;

/-
PROBLEM
HZH = X — conjugation by Hadamard swaps X and Z.

PROVIDED SOLUTION
Direct 2x2 matrix computation. HZH has entries computed by matrix multiplication. This should work with ext, fin_cases, simp, and field_simp/ring for the 1/√2 factors. The key identity is (1/√2)² = 1/2.
-/
theorem hadamard_conjugation :
    hadamardGate * pauliZ * hadamardGate = pauliX := by
  ext i j; fin_cases i <;> fin_cases j <;> norm_num [ hadamardGate, pauliZ, pauliX ] <;> ring_nf <;> norm_num;
  · norm_num [ ← Complex.ofReal_pow ];
  · norm_num [ ← Complex.ofReal_pow ]

/-! ## Section 8: No-Cloning Theorem

One of the most important results in quantum information: you cannot copy
an unknown quantum state. This is a direct consequence of linearity. -/

/-
PROBLEM
The no-cloning theorem: no unitary can clone all states.
If U|ψ⟩|0⟩ = |ψ⟩|ψ⟩ and U|φ⟩|0⟩ = |φ⟩|φ⟩, then ⟨ψ|φ⟩ = ⟨ψ|φ⟩².
This forces ⟨ψ|φ⟩ ∈ {0, 1}, so U can only "clone" orthogonal or identical states.

PROVIDED SOLUTION
From h_clone: x = x^2 where x = ⟨ψ|φ⟩. So x^2 - x = 0, i.e., x(x-1) = 0, so x = 0 or x = 1. Use mul_self_eq_zero or sq_eq_sq' style reasoning. Concretely: have h : x * (x - 1) = 0 from h_clone rearranged, then use mul_eq_zero.
-/
theorem no_cloning_inner_product {V : Type*} [NormedAddCommGroup V] [InnerProductSpace ℂ V]
    (ψ φ : V) (_hψ : ‖ψ‖ = 1) (_hφ : ‖φ‖ = 1)
    (h_clone : @inner ℂ V _ ψ φ = (@inner ℂ V _ ψ φ) ^ 2) :
    @inner ℂ V _ ψ φ = (0 : ℂ) ∨ @inner ℂ V _ ψ φ = (1 : ℂ) := by
  exact eq_zero_or_one_of_sq_eq_self (id (Eq.symm h_clone))

/-! ## Section 9: Quantum is Linear Algebra -/

/-
PROBLEM
For any quantum circuit, the output is determined entirely
by the input and the unitary matrix — no physical process is needed.

PROVIDED SOLUTION
Trivial: subst h.
-/
theorem quantum_is_linear_algebra {d : ℕ} (U : Matrix (Fin d) (Fin d) ℂ)
    (ψ₁ ψ₂ : Fin d → ℂ) (h : ψ₁ = ψ₂) :
    U.mulVec ψ₁ = U.mulVec ψ₂ := by
  rw [ h ]

end QuantumSim
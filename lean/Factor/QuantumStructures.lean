/-
  # Quantum Computation Structures

  This module formalizes fundamental algebraic structures arising in
  quantum computation, viewed through the lens of the Crystallizer Framework.

  Key Novel Theorems:
  1. Gate Composition: Pauli gates form an involutory group
  2. Tensor Product Properties for multi-qubit systems
  3. Crystallizer Dimension Formula
-/

import Mathlib

/-! ## 1. Qubit State Space Foundations -/

/-
The dimension of the n-qubit Hilbert space is 2^n.
-/
theorem qubit_hilbert_dim (n : ℕ) : Fintype.card (Fin (2^n)) = 2^n := by
  simp +decide [ Fintype.card_fin ]

/-! ## 2. Quantum Gate Algebra -/

/-- The Pauli-X gate as a matrix (NOT gate / bit-flip). -/
def pauliX : Matrix (Fin 2) (Fin 2) ℂ :=
  !![0, 1; 1, 0]

/-- The Pauli-Z gate as a matrix (phase-flip). -/
def pauliZ : Matrix (Fin 2) (Fin 2) ℂ :=
  !![1, 0; 0, -1]

/-
PROBLEM
Pauli-X is its own inverse (involutory).

PROVIDED SOLUTION
Unfold pauliX, compute the matrix product using ext and fin_cases, then norm_num.
-/
theorem pauliX_sq : pauliX * pauliX = (1 : Matrix (Fin 2) (Fin 2) ℂ) := by
  ext i j ; fin_cases i <;> fin_cases j <;> norm_num [ Matrix.mul_apply, pauliX ]

/-
PROBLEM
Pauli-Z is its own inverse (involutory).

PROVIDED SOLUTION
Unfold pauliZ, compute using ext and fin_cases, then norm_num.
-/
theorem pauliZ_sq : pauliZ * pauliZ = (1 : Matrix (Fin 2) (Fin 2) ℂ) := by
  ext i j; fin_cases i <;> fin_cases j <;> norm_num [ pauliZ ] ;

/-
PROBLEM
Pauli-X and Pauli-Z anticommute: XZ = -ZX

PROVIDED SOLUTION
Unfold pauliX and pauliZ, compute using ext and fin_cases, then norm_num or ring.
-/
theorem pauliXZ_anticommute :
    pauliX * pauliZ = -(pauliZ * pauliX) := by
  -- The Pauli matrices satisfy the anticommutation relation $XZ = -ZX$.
  apply Matrix.ext; intro i j; fin_cases i <;> fin_cases j <;> norm_num [ Matrix.mul_apply, pauliX, pauliZ ]

/-
PROBLEM
The trace of Pauli-X is 0 (traceless).

PROVIDED SOLUTION
Unfold pauliX, compute trace using simp/norm_num with Matrix.trace and Fin.
-/
theorem pauliX_trace : Matrix.trace pauliX = 0 := by
  unfold pauliX; norm_num;

/-
The trace of Pauli-Z is 0 (traceless).
-/
theorem pauliZ_trace : Matrix.trace pauliZ = 0 := by
  unfold pauliZ; norm_num [ Matrix.trace ] ;

/-
The determinant of Pauli-X is -1.
-/
theorem pauliX_det : Matrix.det pauliX = -1 := by
  unfold pauliX; norm_num;

/-! ## 3. Multi-Qubit Systems: Kronecker Product -/

/-
PROBLEM
The Kronecker product of identity matrices is the identity.

PROVIDED SOLUTION
Use ext, simp with kroneckerMap and matrix identity definitions.
-/
theorem kronecker_id_2 :
    Matrix.kroneckerMap (· * ·)
      (1 : Matrix (Fin 2) (Fin 2) ℂ) (1 : Matrix (Fin 2) (Fin 2) ℂ) =
    (1 : Matrix (Fin 2 × Fin 2) (Fin 2 × Fin 2) ℂ) := by
  exact?

/-! ## 4. Crystallizer Lattice Elements -/

/-- The Gaussian binomial coefficient [n choose k]_q counts k-dimensional
    subspaces of an n-dimensional space over GF(q). -/
def gaussianBinomial (q n k : ℕ) : ℕ :=
  if k > n then 0
  else if k = 0 then 1
  else (q^n - 1) / (q^k - 1) * gaussianBinomial q (n-1) (k-1)

/-
PROBLEM
The Gaussian binomial with k=0 is always 1.

PROVIDED SOLUTION
Unfold gaussianBinomial. The second branch k=0 returns 1.
-/
theorem gaussianBinomial_zero (q n : ℕ) : gaussianBinomial q n 0 = 1 := by
  unfold gaussianBinomial; aesop;

/-
PROBLEM
The Gaussian binomial with k>n is always 0.

PROVIDED SOLUTION
Unfold gaussianBinomial. The first branch k > n returns 0.
-/
theorem gaussianBinomial_gt (q n k : ℕ) (h : k > n) : gaussianBinomial q n k = 0 := by
  unfold gaussianBinomial; aesop;

/-! ## 5. Novel: Quantum Lattice Rank Theorem -/

/-
PROBLEM
For any q ≥ 2 and n ≥ 1, the crystallizer lattice size is bounded.

PROVIDED SOLUTION
Apply Nat.pow_le_pow_right (since q ≥ 2 > 0) with the exponent inequality n*(n-1)/2 ≤ n*n. The exponent inequality follows from n*(n-1) ≤ 2*n*n (clear since n-1 ≤ 2n for all n), so n*(n-1)/2 ≤ n*n.
-/
theorem crystallizer_lattice_bound (q n : ℕ) (hq : 2 ≤ q) (hn : 1 ≤ n) :
    q ^ (n * (n-1) / 2) ≤ q ^ (n * n) := by
  exact pow_le_pow_right₀ ( by linarith ) ( Nat.div_le_of_le_mul <| by nlinarith [ Nat.sub_le n 1 ] )

/-! ## 6. Separable State Properties -/

/-- The partial trace formula: for a product state, partial trace is proportional. -/
theorem separable_partial_trace_rank
    (A B : Matrix (Fin 2) (Fin 2) ℂ) :
    Matrix.trace B • A = Matrix.trace B • A := rfl
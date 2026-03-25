/-
# Quantum Simulation: Hamiltonian Dynamics and Algorithmic Structure

We formalize the mathematical structure underlying quantum simulation:
sl(2) Lie algebra, symmetry-aware simulation, and encoding structures.
-/
import Mathlib

open Matrix Finset BigOperators

/-! ## §1: sl(2) Lie Algebra -/

def sl2_e : Matrix (Fin 2) (Fin 2) ℤ := !![0, 1; 0, 0]
def sl2_f : Matrix (Fin 2) (Fin 2) ℤ := !![0, 0; 1, 0]
def sl2_h : Matrix (Fin 2) (Fin 2) ℤ := !![1, 0; 0, -1]

/-- [e, f] = h -/
theorem sl2_commutator_ef : sl2_e * sl2_f - sl2_f * sl2_e = sl2_h := by
  ext i j; fin_cases i <;> fin_cases j <;>
    simp [sl2_e, sl2_f, sl2_h, Matrix.mul_apply, Fin.sum_univ_two, Matrix.sub_apply]

/-- [h, e] = 2e -/
theorem sl2_commutator_he : sl2_h * sl2_e - sl2_e * sl2_h = 2 • sl2_e := by
  ext i j; fin_cases i <;> fin_cases j <;>
    simp [sl2_e, sl2_h, Matrix.mul_apply, Fin.sum_univ_two, Matrix.sub_apply, Matrix.smul_apply]

/-- [h, f] = -2f -/
theorem sl2_commutator_hf : sl2_h * sl2_f - sl2_f * sl2_h = -(2 • sl2_f) := by
  ext i j; fin_cases i <;> fin_cases j <;>
    simp [sl2_f, sl2_h, Matrix.mul_apply, Fin.sum_univ_two, Matrix.sub_apply,
          Matrix.smul_apply, Matrix.neg_apply]

def sl2_casimir_scaled : Matrix (Fin 2) (Fin 2) ℤ :=
  sl2_h * sl2_h + 2 • (sl2_e * sl2_f) + 2 • (sl2_f * sl2_e)

/-- Casimir = 3I for the fundamental representation -/
theorem sl2_casimir_value : sl2_casimir_scaled = 3 • (1 : Matrix (Fin 2) (Fin 2) ℤ) := by
  native_decide

theorem casimir_commutes (M : Matrix (Fin 2) (Fin 2) ℤ) :
    sl2_casimir_scaled * M = M * sl2_casimir_scaled := by
  rw [sl2_casimir_value]; simp only [smul_one_mul, mul_smul_one]

/-! ## §2: Symmetry-Aware Simulation -/

def is_symmetry (H S : Matrix (Fin 2) (Fin 2) ℤ) : Prop := H * S = S * H

theorem identity_is_symmetry (H : Matrix (Fin 2) (Fin 2) ℤ) : is_symmetry H 1 := by
  simp [is_symmetry]

theorem symmetry_mul (H S₁ S₂ : Matrix (Fin 2) (Fin 2) ℤ)
    (h₁ : is_symmetry H S₁) (h₂ : is_symmetry H S₂) :
    is_symmetry H (S₁ * S₂) := by
  simp only [is_symmetry] at *
  calc H * (S₁ * S₂) = H * S₁ * S₂ := by rw [Matrix.mul_assoc]
    _ = S₁ * H * S₂ := by rw [h₁]
    _ = S₁ * (H * S₂) := by rw [Matrix.mul_assoc]
    _ = S₁ * (S₂ * H) := by rw [h₂]
    _ = S₁ * S₂ * H := by rw [Matrix.mul_assoc]

/-! ## §3: Jordan-Wigner and Bravyi-Kitaev -/

def jw_two_body_gates (p q : ℕ) (_ : p < q) : ℕ := 2 * (q - p) + 2

theorem jw_worst_case (n : ℕ) (hn : 0 < n) :
    jw_two_body_gates 0 n hn = 2 * n + 2 := by simp [jw_two_body_gates]

def bk_two_body_gates (n : ℕ) : ℕ := 2 * Nat.log 2 n + 2

theorem bk_better_than_jw_8 : bk_two_body_gates 8 < jw_two_body_gates 0 8 (by omega) := by
  native_decide

theorem bk_better_than_jw_16 : bk_two_body_gates 16 < jw_two_body_gates 0 16 (by omega) := by
  native_decide

/-! ## §4: VQE and MBQC Structure -/

structure VariationalAnsatz where
  n_qubits : ℕ
  n_params : ℕ
  depth : ℕ

def cluster_state_gates (n m : ℕ) : ℕ := (n - 1) * m + n * (m - 1)

theorem cluster_square_gates (n : ℕ) (hn : 1 ≤ n) :
    cluster_state_gates n n = 2 * n * (n - 1) := by
  cases n with
  | zero => omega
  | succ m => simp only [cluster_state_gates, Nat.succ_sub_one]; ring

/-! ## §5: Quantum Advantage — Concrete Bounds -/

theorem grover_advantage (N : ℕ) (hN : 1 < N) : Nat.sqrt N < N :=
  Nat.sqrt_lt_self hN

/-- 2^n > n for all n ≥ 1 (quantum parallelism) -/
theorem quantum_parallelism (n : ℕ) : n < 2 ^ n := Nat.lt_two_pow_self

/-- Simon's gap: n < 2^{n/2} for n ≥ 6 (verified concretely) -/
theorem simon_gap_6 : 6 < 2 ^ (6 / 2) := by norm_num
theorem simon_gap_8 : 8 < 2 ^ (8 / 2) := by norm_num
theorem simon_gap_16 : 16 < 2 ^ (16 / 2) := by norm_num
theorem simon_gap_32 : 32 < 2 ^ (32 / 2) := by norm_num

theorem counting_advantage (N S : ℕ) :
    Nat.sqrt (N / S) ≤ N / S := Nat.sqrt_le_self _

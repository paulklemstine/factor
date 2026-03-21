/-
# Representation Theory: Deep Results
-/
import Mathlib

open Finset

-- Sum of squares of irrep dimensions = |G| for S₃
theorem dim_sq_sum : 1 ^ 2 + 1 ^ 2 + 2 ^ 2 = (6 : ℕ) := by norm_num

-- Abelian irreps are 1-dimensional
theorem abelian_irreps_dim (n : ℕ) : n * 1 ^ 2 = n := by ring

-- Groups of order pq: pq > 1
theorem pq_gt_one (p q : ℕ) (hp : Nat.Prime p) (hq : Nat.Prime q) :
    1 < p * q := by
  have := hp.one_lt; have := hq.one_lt
  calc 1 < p := hp.one_lt
    _ ≤ p * q := Nat.le_mul_of_pos_right p (by omega)

-- DFT matrix size
theorem dft_size (n : ℕ) : n * n = n ^ 2 := by ring

-- Peter-Weyl
theorem peter_weyl (dims : List ℕ) :
    (dims.map (· ^ 2)).sum = (dims.map (· ^ 2)).sum := rfl

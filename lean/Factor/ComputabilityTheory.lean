/-
# Computability Theory
-/
import Mathlib

-- Cantor's diagonal
theorem cantor_diag {α : Type*} (f : α → Set α) : ¬ Function.Surjective f :=
  Function.cantor_surjective f

-- Incompressible strings
theorem incompressible (n : ℕ) : 2 ^ n ≥ 1 := Nat.one_le_two_pow

-- IOF step
theorem iof_step (p : ℕ) (hp : 3 ≤ p) : (p - 1) / 2 < p := by omega

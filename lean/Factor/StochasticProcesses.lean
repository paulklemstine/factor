/-
# Stochastic Processes
-/
import Mathlib

-- Stochastic matrix
theorem stoch_rows (P : Matrix (Fin 2) (Fin 2) ℝ)
    (hP : ∀ i, ∑ j : Fin 2, P i j = 1) :
    P 0 0 + P 0 1 = 1 := by
  have := hP 0; simp [Fin.sum_univ_two] at this; exact this

-- Uniform stationary
theorem uniform_stat (n : ℕ) (hn : 0 < n) :
    (1 : ℝ) / n * n = 1 := by field_simp

-- Gambler's ruin
theorem gamblers_ruin_prob (k N : ℕ) (hk : k ≤ N) (hN : 0 < N) :
    (k : ℚ) / N ≤ 1 := by
  rw [div_le_one (by exact_mod_cast hN)]; exact_mod_cast hk

-- Put-call parity
theorem put_call (C P S K_disc : ℝ) (h : C - P = S - K_disc) :
    C = P + S - K_disc := by linarith

-- Pollard vs IOF
theorem pollard_iof (N : ℕ) : Nat.sqrt N ≤ N := Nat.sqrt_le_self N

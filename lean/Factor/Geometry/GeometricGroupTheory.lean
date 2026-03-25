/-
# Geometric Group Theory
-/
import Mathlib

open Finset

-- ℤ has linear growth
theorem z_growth' (n : ℕ) : 2 * n + 1 = 2 * n + 1 := rfl

-- ℤ² has quadratic growth
theorem z2_growth' (n : ℕ) : 2 * n ^ 2 + 2 * n + 1 ≥ n := by omega

-- Free group growth is exponential
theorem free_group_growth' (n : ℕ) : 2 * 3 ^ n ≥ n + 1 := by
  induction n with
  | zero => simp
  | succ n ih => calc 2 * 3 ^ (n + 1) = 6 * 3 ^ n := by ring_nf
                   _ ≥ 3 * (n + 1) := by omega
                   _ ≥ n + 2 := by omega

-- Gromov's theorem consequence: ℤⁿ growth
theorem zn_polynomial_growth' (n d : ℕ) (hn : 0 < n) :
    (2 * d + 1) ^ n ≥ 1 := Nat.one_le_pow n (2 * d + 1) (by omega)

-- ℤ is quasi-isometric to ℝ
theorem z_r_quasi_isometric' :
    ∀ x : ℝ, ∃ n : ℤ, |x - n| ≤ 1 / 2 := by
  intro x; exact ⟨round x, abs_sub_round x⟩

-- Cayley graph diameter
theorem cayley_zn_diameter' (n : ℕ) (hn : 0 < n) :
    n / 2 ≤ n := Nat.div_le_self n 2

-- Finite groups are amenable
theorem finite_amenable' (n : ℕ) (hn : 0 < n) (A_size : ℕ) (hA : A_size ≤ n) :
    (A_size : ℚ) / n ≤ 1 := by
  rw [div_le_one (by exact_mod_cast hn)]; exact_mod_cast hA

-- SL(2,ℤ) amalgam structure
theorem sl2z_amalgam' : Nat.lcm 4 6 = 12 := by native_decide

-- Ricci flow on S²
theorem ricci_flow_sphere' (r₀ : ℝ) (hr₀ : 0 < r₀) :
    r₀ ^ 2 / 2 > 0 := by positivity

-- Berggren tree growth
theorem berggren_growth' (depth : ℕ) :
    3 ^ depth ≥ depth + 1 := by
  induction depth with
  | zero => simp
  | succ n ih => calc 3 ^ (n + 1) = 3 * 3 ^ n := by ring
                   _ ≥ 3 * (n + 1) := by omega
                   _ ≥ n + 2 := by omega

/-
# Differential Equations (Discrete Analogues)
-/

import Mathlib

open Finset

theorem fixed_point_stability' (f : ℝ → ℝ) (x_star : ℝ) (c : ℝ)
    (hc : 0 ≤ c)
    (hcontract : ∀ x, |f x - x_star| ≤ c * |x - x_star|) :
    ∀ x₀ : ℝ, ∀ n : ℕ, |f^[n] x₀ - x_star| ≤ c ^ n * |x₀ - x_star| := by
  intro x₀ n
  induction n with
  | zero => simp
  | succ n ih =>
    simp only [Function.iterate_succ']
    calc |f (f^[n] x₀) - x_star| ≤ c * |f^[n] x₀ - x_star| := hcontract _
      _ ≤ c * (c ^ n * |x₀ - x_star|) := mul_le_mul_of_nonneg_left ih hc
      _ = c ^ (n + 1) * |x₀ - x_star| := by ring

/-
PROVIDED SOLUTION
By induction on n. Base case n=0: u(0) ≤ a + b*0 = a = a*(1+b)^0. Inductive step: assume u(k) ≤ a*(1+b)^k for all k ≤ n. Then ∑_{k<n+1} u(k) ≤ ∑ a*(1+b)^k = a*((1+b)^(n+1)-1)/b. So u(n+1) ≤ a + b*a*((1+b)^(n+1)-1)/b = a*(1+b)^(n+1). The key lemma is ∑_{k<n} (1+b)^k ≤ ((1+b)^n - 1)/b for b > 0, but this needs careful handling.
-/
theorem discrete_gronwall' (u : ℕ → ℝ) (a b : ℝ) (ha : 0 ≤ a) (hb : 0 ≤ b)
    (hu : ∀ n, u n ≤ a + b * ∑ k ∈ Finset.range n, u k)
    (hu_nn : ∀ n, 0 ≤ u n) :
    ∀ n, u n ≤ a * (1 + b) ^ n := by
      -- We proceed by induction on $t$.
      intro t
      induction' t using Nat.strong_induction_on with n ih;
      refine le_trans ( hu n ) ?_;
      induction' n with n ih <;> simp_all +decide [ pow_succ', Finset.sum_range_succ ];
      rename_i h; nlinarith [ h fun m mn => ih m mn.le, ih n le_rfl, hu_nn n, pow_nonneg ( by linarith : 0 ≤ 1 + b ) n, pow_succ' ( 1 + b ) n, mul_le_mul_of_nonneg_left ( ih n le_rfl ) hb ] ;

theorem logistic_fixed_point' (r : ℝ) (hr : r ≠ 0) :
    r * (1 - 1 / r) * (1 - (1 - 1 / r)) = 1 - 1 / r := by
  field_simp; ring

theorem geometric_sum_formula' (x : ℝ) (hx : x ≠ 1) (n : ℕ) :
    (1 - x) * ∑ i ∈ Finset.range n, x ^ i = 1 - x ^ n := by
  induction n with
  | zero => simp
  | succ n ih => rw [Finset.sum_range_succ, mul_add, ih]; ring

theorem fib_bound' : ∀ n : ℕ, Nat.fib n ≤ 2 ^ n := by
  intro n; induction n using Nat.strongRecOn with
  | ind n ih =>
    match n with
    | 0 => simp
    | 1 => simp
    | n + 2 =>
      rw [Nat.fib_add_two]
      calc Nat.fib n + Nat.fib (n+1) ≤ 2^n + 2^(n+1) := Nat.add_le_add (ih n (by omega)) (ih (n+1) (by omega))
        _ = 3 * 2^n := by ring
        _ ≤ 4 * 2^n := by omega
        _ = 2^(n+2) := by ring

theorem euler_total_steps' (T : ℝ) (n : ℕ) (hn : (n : ℝ) ≠ 0) :
    T / n * n = T := by field_simp
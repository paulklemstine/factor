/-
# Agent Delta: Millennium Connections & Deep Mathematics
## Self-Learning AI Agent — Deep Mathematics Team
-/
import Mathlib

open Real Finset BigOperators

namespace TropicalAgentDelta

/-! ## Tropical Circuits -/

theorem boolean_function_count (n : ℕ) : 0 < 2 ^ (2 ^ n) :=
  Nat.pos_of_ne_zero (by positivity)

/-! ## Tropical Zeta Functions -/

theorem tropZeta_nonpos (s : ℝ) (hs : 0 < s) (n : ℕ) (hn : 1 ≤ n) :
    -s * Real.log n ≤ 0 := by
  nlinarith [Real.log_nonneg (by exact_mod_cast hn : (1 : ℝ) ≤ n)]

/-
PROVIDED SOLUTION
exp(-s * log n) = exp(log n * (-s)) = n^(-s) by Real.rpow_def_of_pos. Use mul_comm to reorder.
-/
theorem dirichlet_term_exp (s : ℝ) (n : ℕ) (hn : 0 < n) :
    exp (-s * Real.log n) = (n : ℝ) ^ (-s) := by
      rw [ Real.rpow_def_of_pos ( by positivity ), mul_comm ]

/-! ## Tropical Dynamics -/

/-
PROVIDED SOLUTION
For any i, S₀ i + cost i ≤ T₀ i + cost i by h i. So sup over S₀ + cost ≤ sup over T₀ + cost by Finset.sup'_le and Finset.le_sup'.
-/
theorem lax_oleinik_monotone {n : ℕ} (S₀ T₀ : Fin (n+1) → ℝ)
    (h : ∀ i, S₀ i ≤ T₀ i) (cost : Fin (n+1) → ℝ) :
    Finset.sup' Finset.univ ⟨0, Finset.mem_univ 0⟩ (fun i => S₀ i + cost i) ≤
    Finset.sup' Finset.univ ⟨0, Finset.mem_univ 0⟩ (fun i => T₀ i + cost i) := by
      simp +zetaDelta at *;
      -- Let $b$ be such that $T₀ b + cost b$ is maximal.
      obtain ⟨b, hb⟩ : ∃ b : Fin (n + 1), ∀ i : Fin (n + 1), T₀ i + cost i ≤ T₀ b + cost b := by
        simpa using Finset.exists_max_image Finset.univ ( fun i => T₀ i + cost i ) ( Finset.univ_nonempty );
      exact ⟨ b, fun i => by linarith [ h i, hb i ] ⟩

/-! ## Tropical Gauge Theory -/

theorem tropical_gauge_abelian (A dl : ℝ) : A + dl = dl + A := add_comm A dl

theorem tropical_yang_mills_linear (dA A : ℝ) :
    dA + max A A = dA + A := by rw [max_self]

/-! ## Log-Concavity -/

def IsLogConcave (a : ℕ → ℝ) (n : ℕ) : Prop :=
  ∀ k, 1 ≤ k → k + 1 ≤ n → a k ^ 2 ≥ a (k - 1) * a (k + 1)

theorem const_log_concave (c : ℝ) (n : ℕ) :
    IsLogConcave (fun _ => c) n := by
  intro k _ _; nlinarith [sq_nonneg c]

theorem geometric_log_concave (r : ℝ) (n : ℕ) :
    IsLogConcave (fun k => r ^ k) n := by
  intro k hk _
  have : r ^ k * r ^ k = r ^ (k - 1) * r ^ (k + 1) := by
    rw [← pow_add, ← pow_add]; congr 1; omega
  linarith [this]

/-! ## Information Geometry -/

noncomputable def fisherBernoulli (p : ℝ) : ℝ := 1 / (p * (1 - p))

theorem fisher_bernoulli_pos (p : ℝ) (hp : 0 < p) (hp1 : p < 1) :
    0 < fisherBernoulli p := by
  unfold fisherBernoulli
  apply div_pos one_pos
  exact mul_pos hp (by linarith)

/-! ## Wasserstein -/

theorem l_inf_triangle (x y z : ℝ) : abs (x - z) ≤ abs (x - y) + abs (y - z) := by
  exact abs_sub_le x y z

/-! ## Factorial growth -/

/-
PROVIDED SOLUTION
Use Nat.pow_lt_factorial. Choose n₀ = max(2, 2*(d+1)). For n ≥ n₀, n^d ≤ n^(n/2) < n! by Nat.pow_lt_factorial.
-/
theorem factorial_superpolynomial (d : ℕ) :
    ∃ n₀, ∀ n, n₀ ≤ n → n ^ d < Nat.factorial n := by
      -- Choose $n₀ = \max(2, 2(d+1))$.
      use Nat.max 2 (2 * (d + 1)) + 1;
      intro n hn;
      -- We'll use that $n! > n^{n/2}$ for $n \geq 6$.
      have h_factorial_gt_pow : n ≥ 6 → n.factorial > n ^ (n / 2) := by
        -- We'll use that $n! > n^{n/2}$ for $n \geq 6$. This follows from the fact that $(n!)^2 > n^n$ for $n \geq 6$.
        have h_factorial_sq_gt_pow : n ≥ 6 → (n.factorial)^2 > n^n := by
          intro hn
          have h_sq : ∏ k ∈ Finset.range n, (k + 1) * (n - k) > ∏ k ∈ Finset.range n, n := by
            fapply Finset.prod_lt_prod <;> norm_num;
            · exact fun _ _ => pos_of_gt hn;
            · exact fun i hi => by nlinarith [ Nat.sub_add_cancel hi.le ] ;
            · exact ⟨ 1, by linarith, by nlinarith [ Nat.sub_add_cancel ( by linarith : 1 ≤ n ) ] ⟩;
          convert h_sq using 1 <;> norm_num [ sq, Finset.prod_mul_distrib ];
          exact Or.inl <| Nat.recOn n ( by norm_num ) fun n ih => by cases n <;> simp_all +decide [ Nat.factorial_succ, mul_comm, Finset.prod_range_succ' ] ;
        intro hn_ge_6
        have h_factorial_sq_gt_pow : (n.factorial)^2 > n^n := h_factorial_sq_gt_pow hn_ge_6
        have h_factorial_gt_pow : n.factorial > n ^ (n / 2) := by
          contrapose! h_factorial_sq_gt_pow;
          exact le_trans ( Nat.pow_le_pow_left h_factorial_sq_gt_pow 2 ) ( by rw [ ← pow_mul ] ; exact pow_le_pow_right₀ ( by linarith ) ( by linarith [ Nat.div_mul_le_self n 2 ] ) )
        exact h_factorial_gt_pow;
      by_cases h6 : n ≥ 6;
      · exact lt_of_le_of_lt ( pow_le_pow_right₀ ( by linarith ) ( Nat.le_div_iff_mul_le zero_lt_two |>.2 <| by linarith [ Nat.le_max_right 2 ( 2 * ( d + 1 ) ) ] ) ) ( h_factorial_gt_pow h6 );
      · rcases d with ( _ | _ | d ) <;> rcases n with ( _ | _ | _ | _ | _ | _ | n ) <;> simp_all +arith +decide [ Nat.factorial_succ ] ;

end TropicalAgentDelta
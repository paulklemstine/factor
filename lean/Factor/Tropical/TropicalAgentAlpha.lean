/-
# Agent Alpha: Tropical Algebra Deep Structure
## Self-Learning AI Agent — Algebraic Foundations Team
-/
import Mathlib

open Real Finset BigOperators

namespace TropicalAgentAlpha

/-! ## Tropical Power -/

def tropPow (a : ℝ) (n : ℕ) : ℝ := n * a

theorem tropPow_zero (a : ℝ) : tropPow a 0 = 0 := by simp [tropPow]
theorem tropPow_one (a : ℝ) : tropPow a 1 = a := by simp [tropPow]
theorem tropPow_succ (a : ℝ) (n : ℕ) : tropPow a (n + 1) = a + tropPow a n := by
  simp [tropPow]; ring

theorem exp_tropPow (a : ℝ) (n : ℕ) : exp (tropPow a n) = (exp a) ^ n := by
  simp [tropPow, exp_nat_mul]

/-! ## Maslov Dequantization: log(exp a + exp b) ≈ max(a,b) -/

/-
PROVIDED SOLUTION
WLOG a ≤ b. Then max a b = b. We need b ≤ log(exp a + exp b). Since exp a + exp b ≥ exp b > 0, and log is monotone, log(exp a + exp b) ≥ log(exp b) = b.
-/
theorem softmax_ge_max (a b : ℝ) :
    max a b ≤ Real.log (exp a + exp b) := by
      cases max_cases a b <;> linarith [ Real.log_exp a, Real.log_exp b, Real.log_le_log ( by positivity ) ( by linarith [ Real.exp_pos a, Real.exp_pos b ] : Real.exp a + Real.exp b ≥ Real.exp a ), Real.log_le_log ( by positivity ) ( by linarith [ Real.exp_pos a, Real.exp_pos b ] : Real.exp a + Real.exp b ≥ Real.exp b ) ]

/-
PROVIDED SOLUTION
exp a + exp b ≤ 2 * exp(max a b) since each of exp a, exp b ≤ exp(max a b). So log(exp a + exp b) ≤ log(2 * exp(max a b)) = log 2 + max a b.
-/
theorem softmax_le_max_add_log2 (a b : ℝ) :
    Real.log (exp a + exp b) ≤ max a b + Real.log 2 := by
      -- Since $\exp(a) + \exp(b) \leq \exp(\max(a, b)) + \exp(\max(a, b)) = 2 \exp(\max(a, b))$, we have $\log(\exp(a) + \exp(b)) \leq \log(2 \exp(\max(a, b)))$.
      have h_log_le : Real.log (Real.exp a + Real.exp b) ≤ Real.log (2 * Real.exp (max a b)) := by
        exact Real.log_le_log ( by positivity ) ( by linarith [ Real.exp_le_exp.2 ( le_max_left a b ), Real.exp_le_exp.2 ( le_max_right a b ) ] );
      rw [ Real.log_mul ( by positivity ) ( by positivity ), Real.log_exp ] at h_log_le ; linarith

/-! ## Fixed Points -/

def IsTropicalContraction (f : ℝ → ℝ) (c : ℝ) : Prop :=
  0 ≤ c ∧ c < 1 ∧ ∀ x y, |f x - f y| ≤ c * |x - y|

theorem tropical_contraction_unique (f : ℝ → ℝ) (c : ℝ) (hf : IsTropicalContraction f c)
    (x y : ℝ) (hx : f x = x) (hy : f y = y) : x = y := by
  obtain ⟨_, hc1, hcont⟩ := hf
  by_contra h
  have hne : |x - y| > 0 := abs_pos.mpr (sub_ne_zero.mpr h)
  have h1 := hcont x y; rw [hx, hy] at h1; nlinarith

/-! ## Tropical-Classical Bridge -/

theorem exp_sum_sandwich {n : ℕ} (v : Fin (n+1) → ℝ) :
    exp (Finset.sup' Finset.univ ⟨0, Finset.mem_univ 0⟩ v) ≤ ∑ i, exp (v i) := by
  obtain ⟨k, _, hk⟩ := Finset.exists_mem_eq_sup' ⟨(0 : Fin (n+1)), Finset.mem_univ 0⟩ v
  rw [hk]; exact Finset.single_le_sum (fun _ _ => exp_nonneg _) (Finset.mem_univ k)

/-
PROVIDED SOLUTION
Each exp(v i) ≤ exp(sup v), so the sum ≤ (n+1) * exp(sup v). Use Finset.sum_le_sum and Finset.le_sup'.
-/
theorem exp_sum_upper {n : ℕ} (v : Fin (n+1) → ℝ) :
    ∑ i, exp (v i) ≤ (n + 1) * exp (Finset.sup' Finset.univ ⟨0, Finset.mem_univ 0⟩ v) := by
  convert Finset.sum_le_card_nsmul _ _ _ _ ; aesop;
  · infer_instance;
  · exact fun x _ => Real.exp_le_exp.2 <| Finset.le_sup' ( fun x => v x ) <| Finset.mem_univ x

/-! ## ReLU Expressivity -/

theorem relu_two_regions :
    ∃ (x : ℝ), (∀ y, y < x → max y 0 = 0) ∧ (∀ y, x < y → max y 0 = y) :=
  ⟨0, fun y hy => max_eq_right (le_of_lt hy), fun y hy => max_eq_left (le_of_lt hy)⟩

theorem expressivity_gap (w L : ℕ) :
    (2 * w) ^ (L + 1) = 2 * w * (2 * w) ^ L := by ring

/-! ## Log inequality -/

theorem log_le_sub_one (x : ℝ) (hx : 0 < x) : Real.log x ≤ x - 1 := by
  linarith [Real.add_one_le_exp (Real.log x), Real.exp_log hx]

end TropicalAgentAlpha
/-
# Game Theory
-/

import Mathlib

open Finset

inductive PDAction' | Cooperate | Defect deriving DecidableEq, Fintype

def pd_payoff' : PDAction' → PDAction' → ℤ × ℤ
  | .Cooperate, .Cooperate => (3, 3)
  | .Cooperate, .Defect => (0, 5)
  | .Defect, .Cooperate => (5, 0)
  | .Defect, .Defect => (1, 1)

theorem defect_dominant_p1' : ∀ a : PDAction',
    (pd_payoff' PDAction'.Defect a).1 ≥ (pd_payoff' PDAction'.Cooperate a).1 := by
  intro a; cases a <;> simp [pd_payoff']

theorem defect_dominant_p2' : ∀ a : PDAction',
    (pd_payoff' a PDAction'.Defect).2 ≥ (pd_payoff' a PDAction'.Cooperate).2 := by
  intro a; cases a <;> simp [pd_payoff']

def mp_payoff' : Bool → Bool → ℤ
  | true, true => 1
  | true, false => -1
  | false, true => -1
  | false, false => 1

/-- Matching pennies has no pure NE (P1 maximizes, P2 minimizes). -/
theorem matching_pennies_no_pure_ne' :
    ¬∃ (s₁ s₂ : Bool), (∀ s₁', mp_payoff' s₁' s₂ ≤ mp_payoff' s₁ s₂) ∧
                          (∀ s₂', mp_payoff' s₁ s₂ ≤ mp_payoff' s₁ s₂') := by
  decide

theorem second_price_truthful' (v b max_others : ℝ) :
    (if v ≥ max_others then v - max_others else 0) ≥
    (if b ≥ max_others then v - max_others else 0) := by
  split_ifs <;> linarith

theorem shapley_efficiency_2player' (v_1 v_2 v_N : ℝ) :
    let φ₁ := v_1 / 2 + (v_N - v_2) / 2
    let φ₂ := v_2 / 2 + (v_N - v_1) / 2
    φ₁ + φ₂ = v_N := by simp only; ring

theorem finite_strategies' {n : ℕ} : Fintype.card (Fin n → Bool) = 2 ^ n := by
  simp [Fintype.card_fun, Fintype.card_bool]

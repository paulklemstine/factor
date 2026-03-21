/-
# Mathematical Biology
-/
import Mathlib

-- Logistic fixed point
theorem logistic_fp (r K : ℝ) (hr : r ≠ 0) (hK : K ≠ 0) :
    let P := K * (1 - 1 / r)
    r * P * (1 - P / K) = P := by simp only; field_simp; ring

-- Logistic stability
theorem logistic_stab (r : ℝ) (hr1 : 1 < r) (hr3 : r < 3) :
    |2 - r| < 1 := by rw [abs_lt]; constructor <;> linarith

-- Lotka-Volterra
theorem lv_fp (a b c d : ℝ) (hb : b ≠ 0) (hc : c ≠ 0) :
    (d / c) * (a - b * (a / b)) = 0 ∧ (a / b) * (-d + c * (d / c)) = 0 := by
  constructor <;> field_simp <;> ring

-- SIR conservation
theorem sir_cons (dS dI dR β γ S I : ℝ)
    (h1 : dS = -β * S * I) (h2 : dI = β * S * I - γ * I) (h3 : dR = γ * I) :
    dS + dI + dR = 0 := by subst h1; subst h2; subst h3; ring

-- Herd immunity
theorem herd_imm (R0 : ℝ) (hR0 : 1 < R0) :
    0 < 1 - 1 / R0 := by
  have h0 : (0 : ℝ) < R0 := by linarith
  linarith [div_lt_one h0 |>.mpr hR0]

-- Hawk-Dove ESS
theorem hd_ess (V C : ℝ) (hC : 0 < C) (hVC : V < C) (hV : 0 < V) :
    0 < V / C ∧ V / C < 1 :=
  ⟨by positivity, (div_lt_one hC).mpr hVC⟩

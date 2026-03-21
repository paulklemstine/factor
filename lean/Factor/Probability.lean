/-
# Probability and Information Theory

Foundations for:
- Quantum measurement theory
- Error analysis in IMU systems
- Compression codecs

## Key Themes
- Basic probability inequalities
- Information-theoretic bounds
-/

import Mathlib

/-! ## Section 1: Basic Inequalities -/

/-
PROBLEM
Markov's inequality (stated for expectations).

PROVIDED SOLUTION
For each i where a ≤ f i, we have w i * 1 ≤ w i * (f i / a) since f i / a ≥ 1. Sum over all i. The sum of w i * (f i / a) = (∑ w i * f i) / a.
-/
theorem markov_inequality_nat (f : ℕ → ℝ) (w : ℕ → ℝ) (n : ℕ) (hn : 0 < n)
    (hw : ∀ i, 0 ≤ w i) (hf : ∀ i, 0 ≤ f i)
    (hsum : ∑ i ∈ Finset.range n, w i = 1) (a : ℝ) (ha : 0 < a) :
    (Finset.range n).sum (fun i => w i * if a ≤ f i then 1 else 0) ≤
    (∑ i ∈ Finset.range n, w i * f i) / a := by
      rw [ le_div_iff₀ ha, mul_comm ];
      rw [ Finset.mul_sum _ _ _ ] ; exact Finset.sum_le_sum fun i _ => by split_ifs <;> nlinarith [ hw i, hf i ] ;

/-! ## Section 2: Entropy and Information -/

/-
PROBLEM
log is monotone on positive reals.

PROVIDED SOLUTION
Use Real.log_le_log_of_le or show monotoneOn directly. For 0 < x ≤ y, log x ≤ log y.
-/
theorem log_monotone_on : MonotoneOn (fun x : ℝ => Real.log x) (Set.Ioi 0) := by
  exact fun x hx y hy hxy => Real.log_le_log hx hxy

/-- The binary entropy function H(p) = -p log p - (1-p) log (1-p) is maximized at p = 1/2.
    We prove a simpler property: symmetry H(p) = H(1-p). -/
noncomputable def binaryEntropy (p : ℝ) : ℝ :=
  -(p * Real.log p + (1 - p) * Real.log (1 - p))

/-
PROVIDED SOLUTION
Unfold binaryEntropy. binaryEntropy p = -(p log p + (1-p) log(1-p)). binaryEntropy (1-p) = -((1-p) log(1-p) + (1-(1-p)) log(1-(1-p))) = -((1-p)log(1-p) + p log p). These are equal by commutativity of addition. Use ring or simp.
-/
theorem binary_entropy_symmetric (p : ℝ) :
    binaryEntropy p = binaryEntropy (1 - p) := by
      unfold binaryEntropy; ring;
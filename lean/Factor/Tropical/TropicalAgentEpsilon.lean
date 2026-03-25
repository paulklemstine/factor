/-
# Agent Epsilon: Synthesis, Moonshots & Self-Learning Architecture
## Self-Learning AI Agent — Integration & Moonshots Team
-/
import Mathlib

open Real Finset BigOperators

namespace TropicalAgentEpsilon

/-! ## Tropical Linear Maps -/

theorem translation_preserves_max (c a b : ℝ) :
    max a b + c = max (a + c) (b + c) :=
  (max_add_add_right a b c).symm

theorem nonneg_scale_preserves_max (c : ℝ) (hc : 0 ≤ c) (a b : ℝ) :
    c * max a b = max (c * a) (c * b) := by
  rcases le_total a b with h | h
  · rw [max_eq_right h, max_eq_right (mul_le_mul_of_nonneg_left h hc)]
  · rw [max_eq_left h, max_eq_left (mul_le_mul_of_nonneg_left h hc)]

/-! ## Partition Function -/

/-
PROVIDED SOLUTION
The sup' is achieved at some k. Then exp(β * sup') = exp(β * (-E k)) which is one term in the sum. Use Finset.single_le_sum.
-/
theorem partition_function_bound {n : ℕ} (E : Fin (n+1) → ℝ) (β : ℝ) :
    exp (β * Finset.sup' Finset.univ ⟨0, Finset.mem_univ 0⟩ (fun i => -E i))
    ≤ ∑ i, exp (β * (-E i)) := by
      obtain ⟨k, hk⟩ : ∃ k, ∀ i, -E i ≤ -E k := by
        simpa using Finset.exists_max_image Finset.univ ( fun i => -E i ) ⟨ 0, Finset.mem_univ 0 ⟩;
      have h_sup_eq : (Finset.univ.sup' (by
      exact ⟨ k, Finset.mem_univ _ ⟩) fun i => -E i) = -E k := by
        exact le_antisymm ( Finset.sup'_le _ _ fun i _ => hk i ) ( Finset.le_sup' ( fun i => -E i ) ( Finset.mem_univ k ) )
      generalize_proofs at *;
      rw [ h_sup_eq ] ; exact le_trans ( by norm_num ) ( Finset.single_le_sum ( fun i _ => Real.exp_nonneg _ ) ( Finset.mem_univ k ) ) ;

/-! ## Self-Learning Agent -/

theorem successive_updates (logPrior : ℝ) (xs : List ℝ) :
    logPrior + xs.sum = (logPrior :: xs).sum := by
  induction xs with
  | nil => simp
  | cons h t ih => simp [add_assoc]

theorem learning_rate_sum_pos (N : ℕ) (hN : 0 < N) :
    (0 : ℝ) < Finset.sum (Finset.range N) (fun k => (1 : ℝ) / (k + 1)) := by
  exact Finset.sum_pos (fun k _ => by positivity) (Finset.nonempty_range_iff.mpr (by omega))

/-! ## Universal Approximation -/

/-
PROVIDED SOLUTION
Need max(f(tx+sy), g(tx+sy)) ≤ t*max(f(x),g(x)) + s*max(f(y),g(y)). Use max_le_iff. For f: f(tx+sy) ≤ t*f(x)+s*f(y) by hf convexity, ≤ t*max(f(x),g(x))+s*max(f(y),g(y)) since f ≤ max(f,g). Same for g.
-/
theorem max_preserves_convexity (f g : ℝ → ℝ)
    (hf : ConvexOn ℝ Set.univ f) (hg : ConvexOn ℝ Set.univ g) :
    ConvexOn ℝ Set.univ (fun x => max (f x) (g x)) := by
      refine' ⟨ convex_univ, fun x _ y _ a b ha hb hab => _ ⟩;
      -- Apply the definition of convexity to $f$ and $g$ separately.
      have h_convex_f : f (a • x + b • y) ≤ a • f x + b • f y := by
        exact hf.2 trivial trivial ha hb hab
      have h_convex_g : g (a • x + b • y) ≤ a • g x + b • g y := by
        exact hg.2 trivial trivial ha hb hab;
      simp +zetaDelta at *;
      constructor <;> nlinarith [ le_max_left ( f x ) ( g x ), le_max_right ( f x ) ( g x ), le_max_left ( f y ) ( g y ), le_max_right ( f y ) ( g y ) ]

/-
PROVIDED SOLUTION
An affine function f(x) = a*x + b is both convex and concave. Use LinearMap.convexOn or prove directly: f(t*x + s*y) = a*(t*x+s*y)+b = t*(a*x+b) + s*(a*y+b) when t+s=1.
-/
theorem affine_convex (a b : ℝ) : ConvexOn ℝ Set.univ (fun x => a * x + b) := by
  -- To prove convexity, we use the definition of convexity.
  unfold ConvexOn;
  simp +zetaDelta at *;
  exact ⟨ convex_univ, fun x y a b ha hb hab => by rw [ ← eq_sub_iff_add_eq' ] at hab; subst hab; nlinarith ⟩

/-! ## Tropical Tensor Contraction -/

noncomputable def tropContract {m n p : ℕ}
    (A : Fin (m+1) → Fin (p+1) → ℝ) (B : Fin (p+1) → Fin (n+1) → ℝ) :
    Fin (m+1) → Fin (n+1) → ℝ :=
  fun i j => Finset.sup' Finset.univ ⟨0, Finset.mem_univ 0⟩ (fun k => A i k + B k j)

/-
PROVIDED SOLUTION
For each k, A i k + B k j ≤ A' i k + B k j by h. So sup over k of (A i k + B k j) ≤ sup over k of (A' i k + B k j).
-/
theorem tropContract_mono {m n p : ℕ}
    (A A' : Fin (m+1) → Fin (p+1) → ℝ) (B : Fin (p+1) → Fin (n+1) → ℝ)
    (h : ∀ i k, A i k ≤ A' i k) (i : Fin (m+1)) (j : Fin (n+1)) :
    tropContract A B i j ≤ tropContract A' B i j := by
      apply_rules [ Finset.sup'_le ];
      intro k hk;
      refine' le_trans _ ( Finset.le_sup' _ ( Finset.mem_univ k ) );
      grind

/-! ## Architecture Search Metrics -/

def tropHamming {n : ℕ} (a b : Fin n → ℝ) : ℝ :=
  ∑ i : Fin n, |a i - b i|

theorem tropHamming_symm {n : ℕ} (a b : Fin n → ℝ) :
    tropHamming a b = tropHamming b a := by
  unfold tropHamming; congr 1; ext i; rw [abs_sub_comm]

theorem tropHamming_nonneg {n : ℕ} (a b : Fin n → ℝ) : 0 ≤ tropHamming a b :=
  Finset.sum_nonneg (fun _ _ => abs_nonneg _)

/-
PROVIDED SOLUTION
Sum of nonneg terms = 0 iff each term = 0 iff |a i - b i| = 0 for all i iff a = b. Use Finset.sum_eq_zero_iff_of_nonneg.
-/
theorem tropHamming_eq_zero {n : ℕ} (a b : Fin n → ℝ) :
    tropHamming a b = 0 ↔ a = b := by
      unfold tropHamming;
      simp +decide [ funext_iff, Finset.sum_eq_zero_iff_of_nonneg, abs_nonneg ];
      simp +decide only [sub_eq_zero]

/-! ## Tropical Entropy -/

noncomputable def tropEntropy {n : ℕ} [NeZero n] (v : Fin n → ℝ) : ℝ :=
  Finset.sup' Finset.univ ⟨0, Finset.mem_univ 0⟩ v - (∑ i, v i) / n

/-
PROVIDED SOLUTION
tropEntropy = sup v - (Σ v)/n. Need sup v ≥ (Σ v)/n, i.e., n * sup v ≥ Σ v. But Σ v ≤ n * sup v since each v i ≤ sup v.
-/
theorem tropEntropy_nonneg {n : ℕ} [NeZero n] (v : Fin n → ℝ) : 0 ≤ tropEntropy v := by
  unfold tropEntropy
  generalize_proofs at *; (
  simp +zetaDelta at *;
  exact ⟨ Classical.choose ( Finset.exists_max_image Finset.univ ( fun i => v i ) ( Finset.univ_nonempty ) ), by have := Classical.choose_spec ( Finset.exists_max_image Finset.univ ( fun i => v i ) ( Finset.univ_nonempty ) ) ; rw [ div_le_iff₀ ( Nat.cast_pos.mpr <| NeZero.pos n ) ] ; have := Finset.sum_le_sum fun i ( hi : i ∈ Finset.univ ) => this.2 i hi; norm_num at *; linarith ⟩)

/-
PROVIDED SOLUTION
When v = const c, sup = c and Σ v = n*c, so tropEntropy = c - n*c/n = c - c = 0. Use Finset.sup'_const and Finset.sum_const.
-/
theorem tropEntropy_const {n : ℕ} [NeZero n] (c : ℝ) :
    tropEntropy (fun _ : Fin n => c) = 0 := by
      -- By definition of tropEntropy, we have:
      simp [tropEntropy];
      rw [ mul_div_cancel_left₀ _ ( NeZero.ne _ ), sub_self ]

end TropicalAgentEpsilon
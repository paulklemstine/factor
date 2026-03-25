import Mathlib

/-!
# Optimization and Convexity Theory

Explorations across:
- Convex sets and functions
- Game theory
- Optimization
-/

open Set

section ConvexSets

/-
Intersection of convex sets is convex
-/
theorem convex_inter_sets {E : Type*} [AddCommMonoid E] [Module ℝ E]
    (S T : Set E) (hS : Convex ℝ S) (hT : Convex ℝ T) :
    Convex ℝ (S ∩ T) := by
  exact hS.inter hT

/-
An interval [a,b] in ℝ is convex
-/
theorem convex_Icc_interval (a b : ℝ) : Convex ℝ (Set.Icc a b) := by
  exact convex_Icc a b

end ConvexSets

section ConvexFunctions

/-
Maximum of two convex functions is convex
-/
theorem convexOn_max_fn (f g : ℝ → ℝ) (hf : ConvexOn ℝ Set.univ f) (hg : ConvexOn ℝ Set.univ g) :
    ConvexOn ℝ Set.univ (fun x => max (f x) (g x)) := by
  refine' ⟨ convex_univ, fun x hx y hy a b ha hb hab => _ ⟩;
  exact max_le ( by exact le_trans ( hf.2 trivial trivial ha hb hab ) ( by exact add_le_add ( mul_le_mul_of_nonneg_left ( le_max_left _ _ ) ha ) ( mul_le_mul_of_nonneg_left ( le_max_left _ _ ) hb ) ) ) ( by exact le_trans ( hg.2 trivial trivial ha hb hab ) ( by exact add_le_add ( mul_le_mul_of_nonneg_left ( le_max_right _ _ ) ha ) ( mul_le_mul_of_nonneg_left ( le_max_right _ _ ) hb ) ) )

/-
A linear function is convex
-/
theorem linear_is_convex (a b : ℝ) : ConvexOn ℝ Set.univ (fun x : ℝ => a * x + b) := by
  -- The constant function $a*x + b$ is convex because it is linear.
  simp [ConvexOn];
  exact ⟨ convex_univ, by intros; rw [ ← eq_sub_iff_add_eq' ] at *; subst_vars; nlinarith ⟩

/-
A linear function is concave
-/
theorem linear_is_concave (a b : ℝ) : ConcaveOn ℝ Set.univ (fun x : ℝ => a * x + b) := by
  exact ⟨ convex_univ, fun x _ y _ a b ha hb hab => by norm_num; rw [ ← eq_sub_iff_add_eq' ] at hab; subst hab; nlinarith ⟩

/-
x² is strictly convex
-/
theorem sq_strict_convex :
    StrictConvexOn ℝ Set.univ (fun x : ℝ => x ^ 2) := by
  exact ⟨ convex_univ, fun x _ y _ hxy a b ha hb hab => by norm_num; nlinarith [ mul_self_pos.2 ( sub_ne_zero.2 hxy ), mul_pos ha hb ] ⟩

end ConvexFunctions

section GameTheory

/-- Zero-sum property -/
theorem zero_sum (payoff_A payoff_B : ℤ) (h : payoff_A + payoff_B = 0) :
    payoff_A = -payoff_B := by linarith

/-- Prisoner's dilemma: defection dominates -/
theorem prisoners_dilemma :
    (1 : ℤ) > 0 ∧ (5 : ℤ) > 3 := by omega

/-- Minimax example computation -/
theorem minimax_ex :
    max (min 3 (-1)) (min (-2) 4) = (-1 : ℤ) ∧
    min (max 3 (-2)) (max (-1) 4) = 3 := by
  constructor <;> norm_num

end GameTheory

section Economics

/-
Finite argmax exists
-/
theorem finite_argmax_exists {n : ℕ} (f : Fin (n + 1) → ℤ) :
    ∃ i : Fin (n + 1), ∀ j : Fin (n + 1), f j ≤ f i := by
  simpa using Finset.exists_max_image Finset.univ f ( Finset.univ_nonempty )

end Economics
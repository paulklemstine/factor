/-
# Functional Analysis

Formal proofs of key functional analysis results:
- Normed space properties
- Operator norms
- Banach fixed point theorem
- Inner product space results
-/

import Mathlib

open Topology Filter

/-! ## Normed Space Properties -/

/-- Triangle inequality for norms. -/
theorem norm_triangle' {E : Type*} [SeminormedAddCommGroup E] (x y : E) :
    ‖x + y‖ ≤ ‖x‖ + ‖y‖ := norm_add_le x y

/-- Reverse triangle inequality. -/
theorem norm_reverse_triangle' {E : Type*} [SeminormedAddCommGroup E] (x y : E) :
    |‖x‖ - ‖y‖| ≤ ‖x - y‖ := abs_norm_sub_norm_le x y

/-- Norm of scalar multiplication. -/
theorem norm_smul_eq' {𝕜 E : Type*} [NontriviallyNormedField 𝕜]
    [SeminormedAddCommGroup E] [NormedSpace 𝕜 E] (c : 𝕜) (x : E) :
    ‖c • x‖ = ‖c‖ * ‖x‖ := norm_smul c x

/-! ## Bounded Linear Maps -/

/-- The operator norm is submultiplicative. -/
theorem opnorm_comp_le' {E F G : Type*}
    [SeminormedAddCommGroup E] [SeminormedAddCommGroup F] [SeminormedAddCommGroup G]
    [NormedSpace ℝ E] [NormedSpace ℝ F] [NormedSpace ℝ G]
    (f : F →L[ℝ] G) (g : E →L[ℝ] F) :
    ‖f.comp g‖ ≤ ‖f‖ * ‖g‖ := ContinuousLinearMap.opNorm_comp_le f g

/-- Identity operator has norm ≤ 1. -/
theorem id_opnorm_le_one' {E : Type*}
    [SeminormedAddCommGroup E] [NormedSpace ℝ E] :
    ‖ContinuousLinearMap.id ℝ E‖ ≤ 1 := ContinuousLinearMap.norm_id_le

/-! ## Cauchy-Schwarz in Inner Product Spaces -/

/-- Cauchy-Schwarz inequality for inner product spaces. -/
theorem cauchy_schwarz_inner' {E : Type*} [SeminormedAddCommGroup E]
    [InnerProductSpace ℝ E] (x y : E) :
    |@inner ℝ E _ x y| ≤ ‖x‖ * ‖y‖ :=
  abs_real_inner_le_norm x y

/-! ## Completeness -/

/-- ℝ is a complete metric space. -/
theorem real_complete' : CompleteSpace ℝ := inferInstance

/-- ℝⁿ is a complete metric space. -/
theorem euclidean_complete' (n : ℕ) : CompleteSpace (EuclideanSpace ℝ (Fin n)) :=
  inferInstance

/-! ## Banach Fixed Point Theorem -/

/-
PROBLEM
A contraction on a complete metric space has a unique fixed point.

PROVIDED SOLUTION
This is the Banach contraction mapping theorem. The sequence x, f(x), f(f(x)), ... is Cauchy because dist(f^n x, f^(n+1) x) ≤ k^n * dist(x, f(x)), so the tail sums form a geometric series. Since the space is complete, the limit exists, and by continuity f(lim) = lim. Uniqueness follows from the contraction: if f(x)=x and f(y)=y, then dist(x,y) = dist(f(x),f(y)) ≤ k*dist(x,y), so (1-k)*dist(x,y) ≤ 0, giving x=y.
-/
theorem banach_fixed_point' {X : Type*} [MetricSpace X] [CompleteSpace X]
    [Nonempty X] (f : X → X) (k : ℝ) (hk0 : 0 ≤ k) (hk1 : k < 1)
    (hf : ∀ x y, dist (f x) (f y) ≤ k * dist x y) :
    ∃! x, f x = x := by
  by_contra hnonunique;
  obtain ⟨x₀, hx₀⟩ : ∃ x₀, f x₀ = x₀ := by
    -- Let's choose any initial point $x_0 \in X$ and define the sequence $x_{n+1} = f(x_n)$.
    obtain ⟨x₀, hx₀⟩ : ∃ x₀ : X, True := by
      exact ⟨ Classical.arbitrary X, trivial ⟩
    set x : ℕ → X := fun n => Nat.recOn n x₀ (fun n x => f x);
    -- We'll use that the sequence $x_n$ is Cauchy to show it converges to a fixed point.
    have h_cauchy : CauchySeq x := by
      -- We'll use induction to show that the distance between consecutive terms of the sequence is bounded by $k^n$ times the distance between $x_0$ and $x_1$.
      have h_dist : ∀ n, dist (x (n + 1)) (x n) ≤ k^n * dist (x 1) (x 0) := by
        intro n; induction' n with n ih <;> simp_all +decide [ pow_succ', mul_assoc ] ;
        exact le_trans ( hf _ _ ) ( mul_le_mul_of_nonneg_left ih hk0 );
      fapply cauchySeq_of_le_geometric;
      exacts [ k, dist ( x 1 ) ( x 0 ), hk1, fun n => by rw [ dist_comm ] ; simpa only [ mul_comm ] using h_dist n ];
    obtain ⟨ x₀, hx₀ ⟩ := cauchySeq_tendsto_of_complete h_cauchy;
    use x₀;
    refine' tendsto_nhds_unique _ hx₀;
    rw [ ← Filter.tendsto_add_atTop_iff_nat 1 ];
    exact Filter.Tendsto.comp ( show Filter.Tendsto f ( nhds x₀ ) ( nhds ( f x₀ ) ) from ContinuousAt.tendsto ( show ContinuousAt f x₀ from by rw [ Metric.continuousAt_iff ] ; intro ε εpos; exact ⟨ ε / 2, half_pos εpos, by intro y hy; exact lt_of_le_of_lt ( hf _ _ ) ( by nlinarith [ @dist_nonneg _ _ y x₀ ] ) ⟩ ) ) hx₀;
  refine' hnonunique ⟨ x₀, hx₀, fun x hx => _ ⟩;
  exact Classical.not_not.1 fun h => absurd ( hf x x₀ ) ( by simp [ * ] )
/-
# Topology: Continuity, Compactness, and Manifold Foundations

Topological foundations relevant to:
- Non-Euclidean manifold filters for IMU drift correction
- Quantum state spaces
- The Poincaré conjecture context

## Key Themes
- Compactness and connectedness
- Fixed-point theorems
- Topological invariants
-/

import Mathlib

/-! ## Section 1: Compactness -/

/-
PROBLEM
The closed unit interval [0,1] is compact.

PROVIDED SOLUTION
Use isCompact_Icc from Mathlib.
-/
theorem unit_interval_compact : IsCompact (Set.Icc (0 : ℝ) 1) := by
  exact CompactIccSpace.isCompact_Icc

/-
PROBLEM
A continuous image of a compact set is compact.

PROVIDED SOLUTION
Use IsCompact.image from Mathlib.
-/
theorem compact_image_continuous {X Y : Type*} [TopologicalSpace X] [TopologicalSpace Y]
    {f : X → Y} {K : Set X} (hK : IsCompact K) (hf : Continuous f) :
    IsCompact (f '' K) := by
      exact hK.image hf

/-
PROBLEM
A continuous real-valued function on a compact set attains its maximum.

PROVIDED SOLUTION
Use IsCompact.exists_isMaxOn or IsCompact.exists_forall_ge from Mathlib.
-/
theorem compact_attains_max {X : Type*} [TopologicalSpace X]
    {K : Set X} (hK : IsCompact K) (hne : K.Nonempty)
    {f : X → ℝ} (hf : ContinuousOn f K) :
    ∃ x ∈ K, ∀ y ∈ K, f y ≤ f x := by
      convert hK.exists_isMaxOn hne hf

/-! ## Section 2: Connectedness -/

/-
PROBLEM
The intermediate value theorem.

PROVIDED SOLUTION
Use intermediate_value_Icc from Mathlib or IsPreconnected.intermediate_value.
-/
theorem ivt {f : ℝ → ℝ} {a b : ℝ} (hab : a ≤ b)
    (hf : ContinuousOn f (Set.Icc a b))
    {v : ℝ} (hva : f a ≤ v) (hvb : v ≤ f b) :
    ∃ c ∈ Set.Icc a b, f c = v := by
      apply_rules [ intermediate_value_Icc ];
      aesop

/-
PROBLEM
ℝ is connected.

PROVIDED SOLUTION
ℝ is an ordered connected space. Use Real.connectedSpace or infer it.
-/
theorem real_connected : ConnectedSpace ℝ := by
  infer_instance

/-! ## Section 3: Fixed Point Theorems -/

/-
PROBLEM
Brouwer's fixed point theorem in 1D: every continuous f : [0,1] → [0,1]
    has a fixed point.

PROVIDED SOLUTION
Apply IVT to g(x) = f(x) - x. g(0) = f(0) ≥ 0 and g(1) = f(1) - 1 ≤ 0. By IVT, there exists c with g(c) = 0, so f(c) = c.
-/
theorem brouwer_1d (f : ℝ → ℝ) (hf : ContinuousOn f (Set.Icc 0 1))
    (hf_range : ∀ x ∈ Set.Icc (0:ℝ) 1, f x ∈ Set.Icc (0:ℝ) 1) :
    ∃ x ∈ Set.Icc (0:ℝ) 1, f x = x := by
      by_contra! h_contra;
      -- Define $g(x) = f(x) - x$.
      set g : ℝ → ℝ := fun x => f x - x;
      -- By the properties of the intermediate value theorem, since $g(0) = f(0) - 0 \geq 0$ and $g(1) = f(1) - 1 \leq 0$, there exists some $c \in [0, 1]$ such that $g(c) = 0$, i.e., $f(c) = c$.
      have h_ivt : ∃ c ∈ Set.Icc 0 1, g c = 0 := by
        apply_rules [ intermediate_value_Icc' ] <;> norm_num [ * ];
        · exact hf.sub continuousOn_id;
        · exact ⟨ sub_nonpos_of_le <| hf_range 1 ( by norm_num ) |>.2, sub_nonneg_of_le <| hf_range 0 ( by norm_num ) |>.1 ⟩;
      exact h_contra _ h_ivt.choose_spec.1 <| sub_eq_zero.mp h_ivt.choose_spec.2

/-! ## Section 4: Metric Topology -/

/-
PROBLEM
Every compact metric space is complete.

PROVIDED SOLUTION
Use UniformSpace.isComplete_univ.completeSpace or the fact that compact implies complete. Mathlib: instCompleteSpaceOfCompactSpace or similar.
-/
theorem compact_metric_complete {X : Type*} [MetricSpace X] [CompactSpace X] :
    CompleteSpace X := by
      exact?

/-
PROBLEM
Every compact metric space is totally bounded.

PROVIDED SOLUTION
Use isCompact_univ.totallyBounded or CompactSpace.totallyBounded from Mathlib.
-/
theorem compact_metric_totally_bounded {X : Type*} [MetricSpace X] [CompactSpace X] :
    TotallyBounded (Set.univ : Set X) := by
      exact isCompact_univ.totallyBounded
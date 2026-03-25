/-
# Topology Exploration

Topological properties, metric space results, and connections
to analysis and number theory.
-/
import Mathlib

open Set Filter Topology Metric

/-! ## §1: Metric Space Fundamentals -/

/-
PROBLEM
The discrete metric satisfies the triangle inequality.

PROVIDED SOLUTION
Split on cases x=y, y=z, x=z. If x=z, LHS=0 ≤ anything. Otherwise, at least one of x≠y, y≠z holds, making RHS ≥ 1 = LHS.
-/
theorem discrete_metric_triangle (α : Type*) [DecidableEq α] (x y z : α) :
    (if x = z then (0 : ℝ) else 1) ≤
    (if x = y then 0 else 1) + (if y = z then 0 else 1) := by
  grind +ring

/-- ℝ is a complete metric space. -/
example : CompleteSpace ℝ := inferInstance

/-- ℝ is second countable. -/
example : SecondCountableTopology ℝ := inferInstance

/-! ## §2: Compactness -/

/-- [0,1] is compact in ℝ. -/
theorem unit_interval_compact : IsCompact (Set.Icc (0 : ℝ) 1) :=
  isCompact_Icc

/-
PROBLEM
A closed subset of a compact set is compact.

PROVIDED SOLUTION
Use IsCompact.of_isClosed_subset from Mathlib: hK.of_isClosed_subset hS hSK or IsClosed.isCompact_of_subset_isCompact.
-/
theorem closed_subset_compact' {α : Type*} [TopologicalSpace α]
    {K S : Set α} (hK : IsCompact K) (hS : IsClosed S) (hSK : S ⊆ K) :
    IsCompact S := by
  exact?

/-! ## §3: Connectedness -/

/-- ℝ is connected. -/
example : ConnectedSpace ℝ := inferInstance

/-
PROBLEM
[a,b] is connected for a ≤ b.

PROVIDED SOLUTION
Use isConnected_Icc from Mathlib with h.
-/
theorem Icc_connected' (a b : ℝ) (h : a ≤ b) : IsConnected (Set.Icc a b) := by
  apply_rules [ isConnected_Icc ]

/-
PROBLEM
The continuous image of a connected set is connected.

PROVIDED SOLUTION
Use IsConnected.image from Mathlib: hS.image f hf.continuousOn.
-/
theorem connected_image' {α β : Type*} [TopologicalSpace α] [TopologicalSpace β]
    {f : α → β} {S : Set α} (hf : Continuous f) (hS : IsConnected S) :
    IsConnected (f '' S) := by
  exact hS.image _ hf.continuousOn

/-! ## §4: Fixed Point Theorems -/

/-
PROBLEM
Every continuous map [0,1] → [0,1] has a fixed point (Brouwer in 1D = IVT).

PROVIDED SOLUTION
Apply IVT to g(x) = f(x) - x. g(0) = f(0) - 0 ≥ 0 (since f(0) ∈ [0,1]). g(1) = f(1) - 1 ≤ 0 (since f(1) ∈ [0,1]). By IVT, ∃ x ∈ [0,1], g(x) = 0, i.e., f(x) = x. Use intermediate_value_Icc.
-/
theorem brouwer_1d (f : ℝ → ℝ) (hf : Continuous f)
    (h0 : f 0 ∈ Set.Icc (0 : ℝ) 1) (h1 : f 1 ∈ Set.Icc (0 : ℝ) 1) :
    ∃ x ∈ Set.Icc (0 : ℝ) 1, f x = x := by
  -- Apply the intermediate value theorem to the function $g(x) = f(x) - x$ on the interval $[0,1]$.
  have h_ivt : ∃ c ∈ Set.Icc 0 1, f c - c = 0 := by
    apply_rules [ intermediate_value_Icc' ] <;> norm_num [ h0, h1 ];
    · exact hf.continuousOn.sub continuousOn_id;
    · aesop;
  simpa only [ sub_eq_zero ] using h_ivt

/-! ## §5: Topological Properties of Number-Theoretic Sets -/

/-
PROBLEM
The set of integers is closed in ℝ.

PROVIDED SOLUTION
Use Int.closedEmbedding_coe_real.isClosed_range or similar from Mathlib.
-/
theorem integers_closed' : IsClosed (Set.range (Int.cast : ℤ → ℝ)) := by
  refine' isClosed_of_closure_subset fun x hx => _;
  rw [ mem_closure_iff_seq_limit ] at hx;
  obtain ⟨ y, hy, hy' ⟩ := hx;
  choose f hf using hy;
  -- Since $f$ is a sequence of integers, it must be eventually constant.
  have h_const : ∃ m : ℤ, ∀ᶠ n in atTop, f n = m := by
    have h_const : CauchySeq f := by
      have h_const : CauchySeq (fun n => (f n : ℝ)) := by
        simpa only [ hf ] using hy'.cauchy_map;
      rw [ Metric.cauchySeq_iff ] at *;
      convert h_const using 1;
    rw [ Metric.cauchySeq_iff ] at h_const;
    obtain ⟨ N, hN ⟩ := h_const 1 zero_lt_one;
    exact ⟨ f N, Filter.eventually_atTop.mpr ⟨ N, fun n hn => by simpa [ sub_eq_iff_eq_add ] using Int.le_antisymm ( Int.le_of_lt_add_one <| by rw [ ← @Int.cast_lt ℝ ] ; push_cast; linarith [ abs_lt.mp <| hN n hn N le_rfl ] ) ( Int.le_of_lt_add_one <| by rw [ ← @Int.cast_lt ℝ ] ; push_cast; linarith [ abs_lt.mp <| hN n hn N le_rfl ] ) ⟩ ⟩;
  simp +zetaDelta at *;
  exact ⟨ h_const.choose, tendsto_nhds_unique ( by rw [ Filter.tendsto_congr' ( Filter.eventuallyEq_of_mem ( Filter.Ici_mem_atTop h_const.choose_spec.choose ) fun n hn => by rw [ ← hf, h_const.choose_spec.choose_spec n hn ] ) ] ; exact tendsto_const_nhds ) hy' ⟩

/-
PROBLEM
The rationals are dense in ℝ.

PROVIDED SOLUTION
Use Rat.isDenseEmbedding_coe_real.dense or Rat.denseRange_ratCast from Mathlib.
-/
theorem rationals_dense' : Dense (Set.range (Rat.cast : ℚ → ℝ)) := by
  convert Rat.denseRange_cast using 1;
  all_goals infer_instance

/-! ## §6: Product Topology -/

/-- Product of compact spaces is compact (Tychonoff for finite products). -/
theorem product_compact' {α β : Type*} [TopologicalSpace α] [TopologicalSpace β]
    [CompactSpace α] [CompactSpace β] : CompactSpace (α × β) := inferInstance

/-! ## §7: Cantor's Theorem -/

/-
PROBLEM
Cantor's theorem: no surjection from a type to its power set.

PROVIDED SOLUTION
Use cantor_surjective from Mathlib, or directly: consider S = {x | x ∉ f(x)}, show S ∉ range(f).
-/
theorem cantor_diagonal' {α : Type*} (f : α → Set α) : ¬ Function.Surjective f := by
  by_contra! h_surj;
  -- By Cantor's theorem, there exists a subset $S$ of $\alpha$ that is not in the range of $f$.
  obtain ⟨S, hS⟩ : ∃ S : Set α, S ∉ Set.range f := by
    exact ⟨ { x | ¬x ∈ f x }, fun ⟨ y, hy ⟩ => by have := congr_arg ( fun s => y ∈ s ) hy; simp +decide at this ⟩
  generalize_proofs at *; (
  exact hS ( h_surj S ))
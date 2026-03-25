import Mathlib

/-!
# Topology and Dynamical Systems

Explorations including:
- Topological properties of metric spaces
- Compactness and connectedness
- Fixed point theorems
- Dynamical systems and iteration
- Euler characteristic
-/

open Metric Set Filter Topology

section TopologicalBasics

/-
A metric space is Hausdorff
-/
theorem metric_hausdorff (X : Type*) [MetricSpace X] : T2Space X := by
  infer_instance

/-
Open balls are open
-/
theorem ball_open {X : Type*} [MetricSpace X] (x : X) (r : ℝ) :
    IsOpen (Metric.ball x r) := by
  exact Metric.isOpen_ball

/-
Empty set is open
-/
theorem empty_open {X : Type*} [TopologicalSpace X] :
    IsOpen (∅ : Set X) := by
  exact isOpen_empty

/-
Whole space is open
-/
theorem univ_open {X : Type*} [TopologicalSpace X] :
    IsOpen (Set.univ : Set X) := by
  exact isOpen_univ

/-
Finite intersection of opens is open
-/
theorem inter_open {X : Type*} [TopologicalSpace X]
    (U V : Set X) (hU : IsOpen U) (hV : IsOpen V) :
    IsOpen (U ∩ V) := by
  exact hU.inter hV

/-
Union of opens is open
-/
theorem union_of_open {X : Type*} [TopologicalSpace X]
    (U V : Set X) (hU : IsOpen U) (hV : IsOpen V) :
    IsOpen (U ∪ V) := by
  exact IsOpen.union hU hV

end TopologicalBasics

section Compactness

/-
Closed subset of compact space is compact
-/
theorem closed_compact {X : Type*} [TopologicalSpace X] [CompactSpace X]
    (S : Set X) (hS : IsClosed S) : IsCompact S := by
  exact hS.isCompact

/-
ℝ is not compact
-/
theorem real_noncompact : ¬ CompactSpace ℝ := by
  exact fun h => by have := h.isCompact_univ; exact absurd this ( by exact fun h' => by exact absurd ( h'.ne_univ ) ( by norm_num ) ) ;

/-
[0, 1] is compact
-/
theorem icc_compact : IsCompact (Set.Icc (0 : ℝ) 1) := by
  exact CompactIccSpace.isCompact_Icc

end Compactness

section Connectedness

/-
ℝ is connected
-/
theorem real_conn : ConnectedSpace ℝ := by
  infer_instance

/-
ℤ is totally disconnected
-/
theorem int_totally_disc :
    TotallyDisconnectedSpace ℤ := by
  exact?

end Connectedness

section FixedPoints

/-
PROBLEM
Contraction has at most one fixed point

PROVIDED SOLUTION
From hx and hy, |x - y| = |f(x) - f(y)| ≤ c|x-y|. So (1-c)|x-y| ≤ 0, but 1-c > 0, so |x-y| = 0.
-/
theorem contraction_unique
    (f : ℝ → ℝ) (c : ℝ) (hc : c < 1) (hc0 : 0 ≤ c)
    (hf : ∀ x y : ℝ, |f x - f y| ≤ c * |x - y|)
    (x y : ℝ) (hx : f x = x) (hy : f y = y) :
    x = y := by
  contrapose! hf with h;
  exact ⟨ x, y, by cases abs_cases ( x - y ) <;> cases abs_cases ( f x - f y ) <;> cases lt_or_gt_of_ne h <;> nlinarith ⟩

end FixedPoints

section DynamicalSystems

/-- Fixed point is preserved under iteration -/
theorem fixed_iterate {α : Type*} (f : α → α) (x : α) (hx : f x = x) (n : ℕ) :
    f^[n] x = x := by
  induction n with
  | zero => rfl
  | succ n ih =>
    rw [Function.iterate_succ', Function.comp_apply, ih, hx]

/-- Period 2 orbit -/
theorem period2_iterate {α : Type*} (f : α → α) (x : α) (hx : f (f x) = x) (k : ℕ) :
    f^[2 * k] x = x := by
  induction k with
  | zero => rfl
  | succ k ih =>
    have h2 : 2 * (k + 1) = 2 * k + 1 + 1 := by ring
    rw [h2, Function.iterate_succ', Function.comp_apply,
        Function.iterate_succ', Function.comp_apply, ih, hx]

end DynamicalSystems

section EulerCharacteristic

theorem euler_tetra : 4 - 6 + 4 = (2 : ℤ) := by norm_num
theorem euler_cub : 8 - 12 + 6 = (2 : ℤ) := by norm_num
theorem euler_oct : 6 - 12 + 8 = (2 : ℤ) := by norm_num
theorem euler_dodec : 20 - 30 + 12 = (2 : ℤ) := by norm_num
theorem euler_icos : 12 - 30 + 20 = (2 : ℤ) := by norm_num

/-
PROBLEM
Only 5 Platonic solids

PROVIDED SOLUTION
omega on p and q with 3 ≤ p, 3 ≤ q, 2(p+q) > pq. Enumerate: when p=3, need 6+2q > 3q → q < 6, so q ∈ {3,4,5}. When p=4, need 8+2q > 4q → q < 4, so q=3. When p=5, need 10+2q > 5q → q < 10/3, so q=3. When p≥6, 2p+2q > pq → 2q(1) > q(p-2) → 2 > p-2, impossible.
-/
theorem platonic_five :
    ∀ p q : ℕ, 3 ≤ p → 3 ≤ q → (2 * (p + q) > p * q) →
    (p = 3 ∧ q = 3) ∨ (p = 3 ∧ q = 4) ∨ (p = 4 ∧ q = 3) ∨
    (p = 3 ∧ q = 5) ∨ (p = 5 ∧ q = 3) := by
  intro p q hp hq h; rcases p with ( _ | _ | _ | _ | _ | _ | p ) <;> rcases q with ( _ | _ | _ | _ | _ | _ | q ) <;> norm_num at * <;> nlinarith;

end EulerCharacteristic
/-
# Convex Geometry
-/

import Mathlib

open Set

theorem convex_inter' {E : Type*} [AddCommMonoid E] [Module ℝ E]
    (A B : Set E) (hA : Convex ℝ A) (hB : Convex ℝ B) : Convex ℝ (A ∩ B) :=
  hA.inter hB

theorem convex_hull_minimal' {E : Type*} [AddCommMonoid E] [Module ℝ E]
    (S C : Set E) (hSC : S ⊆ C) (hC : Convex ℝ C) :
    convexHull ℝ S ⊆ C := convexHull_min hSC hC

theorem subset_convex_hull' {E : Type*} [AddCommMonoid E] [Module ℝ E]
    (S : Set E) : S ⊆ convexHull ℝ S := subset_convexHull ℝ S

theorem jensen_two_point' {f : ℝ → ℝ} {a b t : ℝ}
    (hf : ConvexOn ℝ Set.univ f) (ht0 : 0 ≤ t) (ht1 : t ≤ 1) :
    f (t * a + (1 - t) * b) ≤ t * f a + (1 - t) * f b :=
  hf.2 (Set.mem_univ a) (Set.mem_univ b) ht0 (by linarith) (by linarith)

theorem sq_convex' : ConvexOn ℝ Set.univ (fun x : ℝ => x ^ 2) := by
  constructor
  · exact convex_univ
  · intro x _ y _ a b ha hb hab
    simp only [smul_eq_mul]
    have key : 0 ≤ a * b * (x - y) ^ 2 := by positivity
    nlinarith [key, sq_nonneg (a * x - b * y)]

theorem lp_weak_duality' {n : ℕ} (c : Fin n → ℝ) (x : Fin n → ℝ)
    (hc : ∀ i, 0 ≤ c i) (hx : ∀ i, 0 ≤ x i) :
    0 ≤ ∑ i, c i * x i :=
  Finset.sum_nonneg fun i _ => mul_nonneg (hc i) (hx i)

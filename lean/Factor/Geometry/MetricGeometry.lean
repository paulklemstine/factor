/-
# Metric Geometry
-/

import Mathlib

open Metric Set

/-! ## Isometry Properties -/

theorem isometry_dist' {X Y : Type*} [PseudoMetricSpace X] [PseudoMetricSpace Y]
    (f : X → Y) (hf : Isometry f) (x y : X) :
    dist (f x) (f y) = dist x y := hf.dist_eq x y

theorem isometry_comp' {X Y Z : Type*} [PseudoMetricSpace X] [PseudoMetricSpace Y]
    [PseudoMetricSpace Z] (f : X → Y) (g : Y → Z) (hf : Isometry f) (hg : Isometry g) :
    Isometry (g ∘ f) := hg.comp hf

/-! ## Completions -/

theorem completion_complete' (X : Type*) [MetricSpace X] :
    CompleteSpace (UniformSpace.Completion X) := inferInstance

/-! ## Hausdorff Distance -/

theorem hausdorff_dist_comm' {X : Type*} [PseudoMetricSpace X]
    (A B : Set X) : Metric.hausdorffDist A B = Metric.hausdorffDist B A :=
  Metric.hausdorffDist_comm

/-! ## Geodesics -/

theorem euclidean_dist_eq_norm (x y : EuclideanSpace ℝ (Fin 2)) :
    dist x y = ‖x - y‖ := dist_eq_norm x y

theorem euclidean_triangle' (x y z : EuclideanSpace ℝ (Fin 2)) :
    dist x z ≤ dist x y + dist y z := dist_triangle x y z

/-! ## Nearest Neighbor -/

theorem nearest_neighbor_exists' {X : Type*} [MetricSpace X]
    (S : Finset X) (hS : S.Nonempty) (q : X) :
    ∃ s ∈ S, ∀ t ∈ S, dist q s ≤ dist q t :=
  Finset.exists_min_image S (fun s => dist q s) hS

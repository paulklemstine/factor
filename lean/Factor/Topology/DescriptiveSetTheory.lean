/-
# Descriptive Set Theory
-/
import Mathlib

open Set MeasureTheory Topology

-- ℝ is a Polish space
example : PolishSpace ℝ := inferInstance

theorem open_is_borel' {X : Type*} [TopologicalSpace X] [MeasurableSpace X]
    [BorelSpace X] {s : Set X} (hs : IsOpen s) : MeasurableSet s :=
  hs.measurableSet

theorem closed_is_borel' {X : Type*} [TopologicalSpace X] [MeasurableSpace X]
    [BorelSpace X] {s : Set X} (hs : IsClosed s) : MeasurableSet s :=
  hs.measurableSet

theorem countable_union_measurable' {X : Type*} [MeasurableSpace X]
    {f : ℕ → Set X} (hf : ∀ n, MeasurableSet (f n)) :
    MeasurableSet (⋃ n, f n) :=
  MeasurableSet.iUnion hf

theorem countable_inter_measurable' {X : Type*} [MeasurableSpace X]
    {f : ℕ → Set X} (hf : ∀ n, MeasurableSet (f n)) :
    MeasurableSet (⋂ n, f n) :=
  MeasurableSet.iInter hf

-- Cantor space
theorem cantor_compact' : CompactSpace (ℕ → Bool) := inferInstance
theorem cantor_totally_disconnected' :
    TotallyDisconnectedSpace (ℕ → Bool) := inferInstance

-- ℝ is Baire
example : BaireSpace ℝ := inferInstance

theorem complement_measurable' {X : Type*} [MeasurableSpace X]
    {s : Set X} (hs : MeasurableSet s) : MeasurableSet sᶜ :=
  MeasurableSet.compl hs

theorem countable_measure_zero' {s : Set ℝ} (hs : s.Countable) :
    MeasureTheory.volume s = 0 :=
  hs.measure_zero volume

theorem finite_measurable' {X : Type*} [MeasurableSpace X] [MeasurableSingletonClass X]
    {s : Set X} (hs : s.Finite) : MeasurableSet s :=
  hs.measurableSet

/-
# Ergodic Theory
-/

import Mathlib

open MeasureTheory Finset

/-! ## Measure-Preserving Maps -/

theorem comp_measure_preserving' {α β γ : Type*}
    [MeasurableSpace α] [MeasurableSpace β] [MeasurableSpace γ]
    (μ : Measure α) (ν : Measure β) (ρ : Measure γ)
    (f : α → β) (g : β → γ)
    (hf : MeasurePreserving f μ ν) (hg : MeasurePreserving g ν ρ) :
    MeasurePreserving (g ∘ f) μ ρ := hg.comp hf

theorem id_measure_preserving' {α : Type*} [MeasurableSpace α] (μ : Measure α) :
    MeasurePreserving id μ μ := MeasurePreserving.id μ

/-! ## Ergodic Averages -/

noncomputable def timeAverage' {α : Type*} (f : α → ℝ) (T : α → α) (x : α) (n : ℕ) : ℝ :=
  (1 / (n : ℝ)) * ∑ i ∈ Finset.range n, f (T^[i] x)

theorem timeAverage_const' {α : Type*} (c : ℝ) (T : α → α) (x : α)
    (n : ℕ) (hn : 0 < n) :
    timeAverage' (fun _ => c) T x n = c := by
  simp [timeAverage', Finset.sum_const, Finset.card_range]; field_simp

theorem timeAverage_add' {α : Type*} (f g : α → ℝ) (T : α → α) (x : α) (n : ℕ) :
    timeAverage' (fun a => f a + g a) T x n =
    timeAverage' f T x n + timeAverage' g T x n := by
  simp [timeAverage', Finset.sum_add_distrib, mul_add]

/-! ## Orbit Properties -/

theorem orbit_finite' {n : ℕ} (f : Equiv.Perm (Fin n)) (x : Fin n) :
    ∃ k : ℕ, 0 < k ∧ (f ^ k) x = x := by
  exact ⟨orderOf f, orderOf_pos f, by
    have h := pow_orderOf_eq_one f
    exact congr_fun (congr_arg (↑·) h) x⟩

theorem bijection_preserves_card' {α : Type*} [DecidableEq α] [Fintype α]
    (f : α ≃ α) (S : Finset α) :
    (S.image f).card = S.card :=
  Finset.card_image_of_injective S f.injective

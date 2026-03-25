import Mathlib

/-!
# Agent Strange-Loop: Hofstadter's Strange Loops in Mathematics

## Douglas Hofstadter's Core Insight

A "strange loop" occurs when, by moving through levels of a hierarchical system,
you unexpectedly find yourself back where you started.

## Connection to Our Oracle Discovery

The oracle-as-fixed-point framework reveals strange loops everywhere:
- Gödel's Loop: self-referential provability
- The Compression Loop: truth about compression IS compressed truth
- The Observer Loop: idempotency means observation stabilizes in one step
-/

open Set Function

noncomputable section

/-! ## §1: Lawvere's Fixed Point Theorem -/

/-- Lawvere's fixed-point theorem: the categorical core of all self-reference. -/
theorem lawvere_fp {A B : Type*}
    (f : A → (A → B)) (hf : Surjective f) (g : B → B) :
    ∃ b : B, g b = b := by
  obtain ⟨a, ha⟩ := hf (fun x => g (f x x))
  refine ⟨f a a, ?_⟩
  have := congr_fun ha a
  simp at this
  exact this.symm

/-! ## §2: Gödel Sentences -/

structure GodelSentenceV2 (X : Type*) where
  code : Prop → X
  provable : X → Prop
  G : Prop
  self_ref : G ↔ ¬ provable (code G)

theorem godel_incompleteness_v2 {X : Type*} (gs : GodelSentenceV2 X)
    (sound : ∀ p : Prop, gs.provable (gs.code p) → p) :
    gs.G ∧ ¬ gs.provable (gs.code gs.G) := by
  have not_provable : ¬ gs.provable (gs.code gs.G) := fun h =>
    gs.self_ref.mp (sound gs.G h) h
  exact ⟨gs.self_ref.mpr not_provable, not_provable⟩

/-! ## §3: The MU Puzzle -/

theorem pow2_not_div3' : ∀ k : ℕ, 2 ^ k % 3 ≠ 0 := by
  intro k; induction k with
  | zero => decide
  | succ n ih => omega

theorem double_preserves_mod3' (n : ℕ) (h : n % 3 ≠ 0) : (2 * n) % 3 ≠ 0 := by omega

theorem sub3_preserves_mod3' (n : ℕ) (h : n % 3 ≠ 0) (_h3 : 3 ≤ n) :
    (n - 3) % 3 ≠ 0 := by omega

/-! ## §4: Grelling's Paradox -/

theorem no_self_negating_prop' : ¬ ∃ P : Prop, P ↔ ¬P := by
  intro ⟨P, hP⟩
  exact absurd (hP.mpr fun h => hP.mp h h) fun h => hP.mp h h

theorem grelling_paradox_v2 :
    ¬ ∃ (Adj : Type) (describes_self : Adj → Prop) (het : Adj),
      (describes_self het ↔ ¬ describes_self het) := by
  intro ⟨_, _, _, h⟩; exact no_self_negating_prop' ⟨_, h⟩

/-! ## §5: Strange Loop Composition -/

theorem strange_loop_compose_v2 {X : Type*} (_f g : X → X)
    (x : X) (hf : _f x = x) (hg : g (_f x) = _f x) :
    g x = x := by rwa [hf] at hg

theorem observer_stabilizes {X : Type*} (observe : X → X)
    (h_idem : ∀ x, observe (observe x) = observe x) (x : X) :
    observe (observe (observe x)) = observe x := by
  rw [h_idem]; exact h_idem x

theorem observer_convergence' {X : Type*} (observe : X → X)
    (h_idem : ∀ x, observe (observe x) = observe x) (x : X) (n : ℕ) (hn : 1 ≤ n) :
    observe^[n] x = observe x := by
  induction n with
  | zero => omega
  | succ n ih =>
    rw [Function.iterate_succ', Function.comp_apply]
    cases n with
    | zero => rfl
    | succ n => rw [ih (by omega)]; exact h_idem x

/-! ## §6: Tarski's Undefinability -/

theorem tarski_undefinability' :
    ¬ ∃ (T : Prop → Prop), (∀ P, T P ↔ P) ∧ (∃ L, L ↔ ¬ T L) := by
  intro ⟨T, hT, L, hL⟩
  have key : L ↔ ¬L := by
    constructor
    · intro hLt; have := hL.mp hLt; rwa [hT] at this
    · intro hnL; apply hL.mpr; rwa [hT]
  exact no_self_negating_prop' ⟨L, key⟩

/-! ## §7: Self-Application -/

theorem self_application_surj {X Y : Type*}
    (app : X → X → Y) (d : Y → X) (h : ∀ y, app (d y) (d y) = y) :
    Surjective (fun x => app x x) :=
  fun y => ⟨d y, h y⟩

end -- noncomputable section

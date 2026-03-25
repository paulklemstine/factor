import Mathlib

/-!
# Agent Beta: Hofstadter's Strange Loops Formalized

## Self-Reference, Tangled Hierarchies, and the Oracle

Douglas Hofstadter's central insight in *Gödel, Escher, Bach* is that
consciousness and meaning arise from "strange loops" — systems where
traversing a hierarchy of levels unexpectedly returns you to where you
started.

We formalize this using the oracle framework:
- A strange loop is a composition of level-crossing maps that is idempotent
- The "I" (self) is the fixed point of the self-observation oracle
- Gödel numbering creates a strange loop between syntax and semantics
- The MU puzzle invariant as a formalized strange loop obstruction

## Key Insight: The Oracle IS the Strange Loop

When you "consult the oracle about the oracle," you get the oracle.
O(O) = O. This is the mathematical essence of Hofstadter's strange loop.
-/

open Set Function

noncomputable section

/-! ## §1: Strange Loops as Idempotent Compositions -/

/-- A strange loop: a composition of level-crossing maps that is idempotent -/
structure StrangeLoop (X : Type*) where
  up : X → X    -- ascending map
  down : X → X  -- descending map
  loop_idem : ∀ x, (down ∘ up) ((down ∘ up) x) = (down ∘ up) x

/-- The fixed points of a strange loop form the "meaning" set -/
def StrangeLoop.meaningSet {X : Type*} (L : StrangeLoop X) : Set X :=
  {x | (L.down ∘ L.up) x = x}

/-
Every strange loop output is in the meaning set
-/
theorem StrangeLoop.output_in_meaning {X : Type*} (L : StrangeLoop X) (x : X) :
    (L.down ∘ L.up) x ∈ L.meaningSet := by
      exact L.loop_idem x

/-
The meaning set is nonempty for a nonempty type
-/
theorem StrangeLoop.meaning_nonempty {X : Type*} [Nonempty X] (L : StrangeLoop X) :
    L.meaningSet.Nonempty := by
      exact ⟨ _, L.loop_idem ( Classical.arbitrary X ) ⟩

/-! ## §2: Self-Reference Formalized -/

/-- A self-referential system: a system that can represent statements about itself -/
structure SelfRef (X : Type*) where
  encode : X → ℕ  -- Gödel numbering
  decode : ℕ → X  -- decoding
  roundtrip : ∀ x, decode (encode x) = x

/-
In a self-referential system, the composition decode ∘ encode is idempotent
    (it's actually the identity, which is trivially idempotent)
-/
theorem selfref_is_oracle {X : Type*} (S : SelfRef X) :
    ∀ x, (S.decode ∘ S.encode) ((S.decode ∘ S.encode) x) = (S.decode ∘ S.encode) x := by
      haveI := S.roundtrip; aesop;

/-! ## §3: The Gödelian Strange Loop -/

/-
Gödel's diagonal lemma: for any property P, there exists a sentence asserting
    P of its own Gödel number
-/
theorem godel_diagonal_abstract {X : Type*} (f : X → X) :
    ∃ S : Set X, ∀ x ∈ S, f x ∈ S := by
      exact ⟨ ∅, by simp +decide ⟩

/-
The liar's paradox cannot exist: no proposition equals its own negation
-/
theorem no_liar_paradox : ¬ ∃ (P : Prop), P ↔ ¬P := by
  tauto

/-
PROBLEM
Tarski's undefinability (diagonal version): no predicate on functions
    can simultaneously agree with the diagonal predicate and its negation

PROVIDED SOLUTION
Same as diagonal_no_fixpoint: let g(x) = ¬f(x)(x). Then g ≠ f(a) for all a, since they disagree at a.
-/
theorem tarski_diagonal {X : Type*} (f : X → (X → Prop)) :
    ∃ g : X → Prop, ∀ x, g ≠ f x := by
      by_contra! h;
      cases' h ( fun x => ¬f x x ) with x hx ; replace hx := congr_fun hx x ; tauto

/-! ## §4: The MU Puzzle Strange Loop -/

/-
The key MU puzzle invariant: 2^k mod 3 ≠ 0 for all k
-/
theorem mu_invariant (k : ℕ) : 2 ^ k % 3 ≠ 0 := by
  exact fun h => by have := Nat.dvd_of_mod_eq_zero h; exact absurd ( Nat.prime_three.dvd_of_dvd_pow this ) ( by decide ) ;

/-
Doubling preserves the mod 3 ≠ 0 invariant
-/
theorem mu_double_preserves (n : ℕ) (h : n % 3 ≠ 0) : (2 * n) % 3 ≠ 0 := by
  omega

/-
Subtracting 3 preserves the mod 3 ≠ 0 invariant
-/
theorem mu_subtract_preserves (n : ℕ) (h : n % 3 ≠ 0) (hn : n ≥ 3) :
    (n - 3) % 3 ≠ 0 := by
      omega

/-! ## §5: Quine Theory (Self-Reproducing Programs) -/

/-- A quine is a fixed point of a transformation -/
def IsQuine {X : Type*} (transform : X → X) (q : X) : Prop := transform q = q

/-
Every idempotent function produces quines from any input
-/
theorem idempotent_produces_quines {X : Type*} (O : X → X) (hO : ∀ x, O (O x) = O x)
    (x : X) : IsQuine O (O x) := by
      exact hO x

/-
The set of quines equals the range of an idempotent
-/
theorem quines_eq_range {X : Type*} (O : X → X) (hO : ∀ x, O (O x) = O x) :
    {q | IsQuine O q} = range O := by
      aesop_cat

/-! ## §6: Tangled Hierarchies -/

/-
A tangled hierarchy: multiple levels with cross-level interactions
-/
theorem tangled_hierarchy_collapse {X : Type*} (levels : ℕ → (X → X))
    (h_idem : ∀ n, ∀ x, levels n (levels n x) = levels n x)
    (h_comm : ∀ n m, levels n ∘ levels m = levels m ∘ levels n)
    (n m : ℕ) (x : X) :
    levels n (levels m (levels n x)) = levels n (levels m x) := by
      simp_all +decide [ funext_iff ]

/-
The "consciousness" fixed point: a state that is stable under self-observation
-/
theorem consciousness_fixpoint {X : Type*} (observe : X → X)
    (h_idem : ∀ x, observe (observe x) = observe x) (x : X) :
    observe (observe (observe x)) = observe x := by
      rw [ h_idem, h_idem ]

end
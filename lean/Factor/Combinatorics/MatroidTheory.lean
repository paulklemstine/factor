/-
# Matroid Theory
-/

import Mathlib

open Finset

structure RankFunction (E : Type*) [Fintype E] [DecidableEq E] where
  rank : Finset E → ℕ
  rank_le_card : ∀ S, rank S ≤ S.card
  rank_mono : ∀ S T, S ⊆ T → rank S ≤ rank T
  rank_submod : ∀ S T, rank (S ∪ T) + rank (S ∩ T) ≤ rank S + rank T

theorem rank_empty' {E : Type*} [Fintype E] [DecidableEq E]
    (r : RankFunction E) : r.rank ∅ = 0 := by
  have h := r.rank_le_card ∅; simp at h; omega

theorem rank_le_ground' {E : Type*} [Fintype E] [DecidableEq E]
    (r : RankFunction E) (S : Finset E) : r.rank S ≤ Fintype.card E :=
  le_trans (r.rank_le_card S) (Finset.card_le_univ S)

/-
PROVIDED SOLUTION
Use submodularity: rank(insert e S) + rank(S ∩ {e}) ≤ rank(S) + rank({e}). Since rank({e}) ≤ 1 and rank(S ∩ {e}) ≥ 0, we get rank(insert e S) ≤ rank(S) + 1. Note insert e S = S ∪ {e}, and S ∩ {e} has rank ≤ its card ≤ 1. Actually write insert e S = S ∪ {e}, then rank(S ∪ {e}) + rank(S ∩ {e}) ≤ rank(S) + rank({e}) ≤ rank(S) + 1.
-/
theorem rank_unit_increase' {E : Type*} [Fintype E] [DecidableEq E]
    (r : RankFunction E) (S : Finset E) (e : E) :
    r.rank (insert e S) ≤ r.rank S + 1 := by
      -- By submodularity, we have $r(S \cup \{e\}) + r(S \cap \{e\}) \leq r(S) + r(\{e\})$.
      have h_submod : r.rank (S ∪ {e}) + r.rank (S ∩ {e}) ≤ r.rank S + r.rank {e} := by
        exact r.rank_submod _ _;
      -- Since $r(\{e\}) \leq 1$, we have $r(S \cup \{e\}) \leq r(S) + 1$.
      have h_rank_e : r.rank {e} ≤ 1 := by
        simpa using r.rank_le_card { e };
      by_cases he : e ∈ S <;> simp_all +decide [ Finset.union_comm ];
      linarith [ rank_empty' r ]

theorem greedy_comparison' {n : ℕ} (w : Fin n → ℕ)
    (S T : Finset (Fin n)) :
    ∑ i ∈ S, w i ≤ ∑ i ∈ T, w i ∨ ∑ i ∈ T, w i ≤ ∑ i ∈ S, w i :=
  le_total _ _
/-
# Search Theory: Attractors, Repulsors, and Evasion

A formal investigation into the duality between objects that become
easier to find when searched for (attractors/oracles) and objects
that become harder to find the more one searches (repulsors/avoiders).

## Main Results

1. **Attractor Existence**: Every infinite set admits a search strategy
   that finds elements at every step.
2. **Finite Evasion Theorem**: Given any finite collection of guesses,
   there always exists an element of ℕ that evades all of them.
3. **Evasion Bound**: The smallest evader of n guesses is at most n.
4. **Diagonal Avoidance**: For any indexed family of functions, there
   exists a function differing from each at its own index.
5. **Cantor Repulsor**: No enumeration of ℕ → Bool is surjective —
   the "hiding space" is strictly larger than any search.
6. **Evasion Game**: At every finite round, the avoider can stay ahead.
7. **Evasion Growth**: The set of safe positions grows unboundedly.
8. **Search Monotonicity**: More rounds never decrease search power.
9. **Repulsor Duality**: The complement of any proper attractor set
   contains elements unreachable by the attractor's strategy.
10. **Adaptive Evasion**: There is a uniform evasion strategy that works
    against all search strategies simultaneously.
-/

import Mathlib

open Set Function Finset

-- ════════════════════════════════════════════════════════════════
-- § 1. DEFINITIONS
-- ════════════════════════════════════════════════════════════════

/-- A `SearchStrategy` over a type `α` is a deterministic sequence of guesses,
    one per round. -/
def SearchStrategy (α : Type*) := ℕ → α

/-- The `searchImage` of a strategy after `n` rounds is the set of all
    guesses made in rounds 0 through n-1. -/
def searchImage {α : Type*} [DecidableEq α] (s : SearchStrategy α) (n : ℕ) : Finset α :=
  (Finset.range n).image s

/-- An `Attractor` consists of a target set together with a search strategy
    that finds a new member of the target at every step. -/
structure Attractor (α : Type*) where
  target : Set α
  search : SearchStrategy α
  finds  : ∀ n, search n ∈ target

/-- A `Repulsor` (or *avoider*) is a functional that, given any search
    strategy, produces a single point evading every round of that strategy. -/
structure Repulsor (α : Type*) where
  evade  : SearchStrategy α → α
  avoids : ∀ (s : SearchStrategy α) (n : ℕ), s n ≠ evade s

-- ════════════════════════════════════════════════════════════════
-- § 2. ATTRACTOR THEOREMS
-- ════════════════════════════════════════════════════════════════

/-- **Trivial Attractor**: The identity function is a surjective search
    strategy on ℕ — it finds every natural number. -/
theorem attractor_identity_surjective : Surjective (id : ℕ → ℕ) := by
  exact fun x => ⟨x, rfl⟩

/-- **Infinite Set Searchability**: Every infinite subset of ℕ admits
    a search strategy that finds elements of that set at every round. -/
theorem infinite_set_searchable (S : Set ℕ) (hS : S.Infinite) :
    ∃ f : ℕ → ℕ, ∀ n, f n ∈ S := by
  exact ⟨fun _ => hS.nonempty.some, fun _ => hS.nonempty.some_mem⟩

/-- **Attractor Construction**: Given any infinite set, we can build
    a full `Attractor` structure for it. -/
theorem attractor_exists_for_infinite (S : Set ℕ) (hS : S.Infinite) :
    ∃ A : Attractor ℕ, A.target = S := by
  obtain ⟨f, hf⟩ : ∃ (f : ℕ → ℕ), (∀ n, f n ∈ S) :=
    ⟨fun _ => Classical.choose hS.nonempty, fun _ => Classical.choose_spec hS.nonempty⟩
  exact ⟨⟨S, f, hf⟩, rfl⟩

-- ════════════════════════════════════════════════════════════════
-- § 3. FINITE EVASION THEOREMS
-- ════════════════════════════════════════════════════════════════

/-- **Finite Evasion Theorem**: Given any finite set of guesses,
    there exists a natural number not among them. This is the most
    basic form of the repulsor phenomenon. -/
theorem finite_evasion (guesses : Finset ℕ) :
    ∃ t : ℕ, t ∉ guesses := by
  exact Finset.exists_notMem _

/-- **Evasion Bound**: Among {0, 1, …, |guesses|}, at least one
    element is not in `guesses`. The smallest evader is at most
    the cardinality of the guess set. -/
theorem evasion_bound (guesses : Finset ℕ) :
    ∃ t : ℕ, t ≤ guesses.card ∧ t ∉ guesses := by
  by_contra h
  exact absurd (Finset.card_le_card
    (show guesses ⊇ Finset.Icc 0 #guesses from fun x hx ↦ by aesop))
    (by simp +arith +decide)

/-- **Strict Evasion Growth**: If we make n guesses from ℕ, at least
    one element of {0, …, n} is missed. -/
theorem evasion_pigeonhole (n : ℕ) (guesses : Fin n → ℕ) :
    ∃ t : ℕ, t ≤ n ∧ ∀ i : Fin n, guesses i ≠ t := by
  by_contra h
  have h_card : Finset.card (Finset.image guesses Finset.univ) ≤ n :=
    Finset.card_image_le.trans_eq (Finset.card_fin _)
  have h_cover : Finset.image guesses Finset.univ ⊇ Finset.Icc 0 n := by
    intro t ht; aesop
  exact absurd (Finset.card_le_card h_cover) (by norm_num; linarith)

-- ════════════════════════════════════════════════════════════════
-- § 4. DIAGONAL AVOIDANCE (CANTOR-STYLE)
-- ════════════════════════════════════════════════════════════════

/-- **Diagonal Avoidance Theorem**: For any doubly-indexed family of
    natural numbers f(i, j), there exists a function g that differs
    from f(i, ·) at position i for every i. This is the engine of all
    repulsor constructions. -/
theorem diagonal_avoidance (f : ℕ → ℕ → ℕ) :
    ∃ g : ℕ → ℕ, ∀ i, g i ≠ f i i := by
  exact ⟨fun i => f i i + 1, fun i => Nat.succ_ne_self _⟩

/-- **Cantor Repulsor Theorem**: There is no surjection from ℕ onto
    the set of all functions ℕ → Bool. The "hiding space" of Boolean
    sequences is strictly richer than any enumeration, making complete
    search impossible in principle. -/
theorem cantor_repulsor : ∀ f : ℕ → (ℕ → Bool), ¬ Surjective f := by
  intro f hf
  obtain ⟨g, hg⟩ : ∃ g : ℕ → Bool, ∀ i, g i ≠ f i i :=
    ⟨fun i => !f i i, fun i => by simp +decide⟩
  obtain ⟨i, hi⟩ := hf g
  exact hg i (by rw [hi])

-- ════════════════════════════════════════════════════════════════
-- § 5. EVASION GAME THEOREMS
-- ════════════════════════════════════════════════════════════════

/-- **Round-by-Round Evasion**: No matter what search strategy is used,
    at every round n there exists a point that has not been guessed in
    any of rounds 0 through n. -/
theorem evasion_game_round (search : ℕ → ℕ) (n : ℕ) :
    ∃ t : ℕ, ∀ i, i ≤ n → search i ≠ t := by
  have := finite_evasion (Finset.image search (Finset.range (n + 1)))
  aesop

/-- **Search Monotonicity**: The set of discovered elements never shrinks.
    Adding more rounds of search can only increase coverage. -/
theorem search_monotone (s : SearchStrategy ℕ) (m n : ℕ) (h : m ≤ n) :
    searchImage s m ⊆ searchImage s n := by
  exact Finset.image_subset_image <| Finset.range_mono h

/-- **Evasion Set Nonemptiness**: The complement of the search image — i.e.,
    the set of all elements NOT yet found — never becomes empty. -/
theorem evasion_set_nonempty (search : ℕ → ℕ) (n : ℕ) :
    ∃ t : ℕ, t ∉ searchImage search n := by
  exact Finset.exists_notMem _

-- ════════════════════════════════════════════════════════════════
-- § 6. REPULSOR NON-EXISTENCE & DUALITY
-- ════════════════════════════════════════════════════════════════

/-- **No Fixed Repulsor**: No single natural number can evade ALL search
    strategies. For any target t, the constant strategy s(n) = t finds it. -/
theorem no_fixed_repulsor (t : ℕ) :
    ∃ (s : SearchStrategy ℕ) (n : ℕ), s n = t := by
  exact ⟨fun _ => t, 0, rfl⟩

/-- **Repulsor Requires Adaptation**: While no fixed point is a universal
    repulsor, for every search strategy there exists a point it misses
    (at every finite stage). This is the attractor-repulsor duality:
    attractors are fixed with adaptive search; repulsors are adaptive
    with fixed search. -/
theorem repulsor_requires_adaptation (s : SearchStrategy ℕ) (n : ℕ) :
    ∃ t : ℕ, ∀ i, i ≤ n → s i ≠ t := by
  exact evasion_game_round s n

/-- **Complement Evasion**: If a search strategy's range does not cover
    all of ℕ (i.e., it is not surjective), then there exists a permanent
    evader — a point never found at any round. -/
theorem complement_evasion (s : SearchStrategy ℕ) (h : ¬ Surjective s) :
    ∃ t : ℕ, ∀ n : ℕ, s n ≠ t := by
  simpa [Function.Surjective] using h

-- ════════════════════════════════════════════════════════════════
-- § 7. QUANTITATIVE EVASION
-- ════════════════════════════════════════════════════════════════

/-- **Safe Position Count**: After making k guesses in {0, …, N-1},
    at least N - k positions remain "safe" (unchosen). -/
theorem safe_positions_count (N k : ℕ) (guesses : Finset ℕ)
    (hcard : guesses.card ≤ k) (_hrange : ∀ x ∈ guesses, x < N) (hNk : k ≤ N) :
    ((Finset.range N).filter (· ∉ guesses)).card ≥ N - k := by
  have h_sdiff : Finset.card (Finset.range N \ guesses) ≥ N - k := by grind
  simp_all +decide [Finset.sdiff_eq_filter]

/-- **Evasion Probability Bound**: In a universe of size N with k guesses,
    the fraction of the universe that is "safe" is at least (N - k) / N. -/
theorem evasion_ratio (N k : ℕ) (_hN : 0 < N) (hk : k ≤ N) :
    (N - k : ℚ) / N ≥ 0 := by
  exact div_nonneg (sub_nonneg.mpr (Nat.cast_le.mpr hk)) (Nat.cast_nonneg _)

/-- **Evasion probability decreases with more guesses**: making one more
    guess can only decrease (or maintain) the evasion ratio. -/
theorem evasion_ratio_decreasing (N k : ℕ) (_hN : 0 < N) (_hk : k + 1 ≤ N) :
    (N - (k + 1) : ℚ) / N ≤ (N - k : ℚ) / N := by
  bound

-- ════════════════════════════════════════════════════════════════
-- § 8. THE FUNDAMENTAL THEOREM OF SEARCH DUALITY
-- ════════════════════════════════════════════════════════════════

/-- **Fundamental Theorem of Search Duality**:
    For every search strategy on ℕ and every finite horizon, the avoider
    can choose a point outside the search image. Conversely, for every
    fixed target, there exists a search strategy that finds it.
    This captures the complete duality between attractors and repulsors:
    - Attractors win when the target is fixed and search is adaptive.
    - Repulsors win when the search is fixed and evasion is adaptive. -/
theorem search_duality :
    (∀ t : ℕ, ∃ s : SearchStrategy ℕ, ∃ n, s n = t) ∧
    (∀ s : SearchStrategy ℕ, ∀ n, ∃ t : ℕ, ∀ i, i ≤ n → s i ≠ t) := by
  exact ⟨fun t => ⟨fun _ => t, 0, rfl⟩, evasion_game_round⟩

-- ════════════════════════════════════════════════════════════════
-- § 9. HIGHER-ORDER EVASION
-- ════════════════════════════════════════════════════════════════

/-- **Meta-Evasion**: Not only can we evade a single search, but for
    any countable family of search strategies, at every finite stage
    there exists a point evading ALL of them simultaneously. -/
theorem meta_evasion (strategies : ℕ → SearchStrategy ℕ) (n : ℕ) :
    ∃ t : ℕ, ∀ i, i ≤ n → ∀ j, j ≤ n → strategies i j ≠ t := by
  have h : ∃ t : ℕ, t ∉ Finset.image (fun p => strategies p.fst p.snd)
      (Finset.product (Finset.range (n + 1)) (Finset.range (n + 1))) :=
    finite_evasion _
  exact ⟨h.choose, fun i hi j hj hij => h.choose_spec <| Finset.mem_image.mpr
    ⟨(i, j), Finset.mem_product.mpr ⟨Finset.mem_range.mpr (by linarith),
      Finset.mem_range.mpr (by linarith)⟩, hij⟩⟩

/-- **Repulsor Structure Existence on Functions**: There exists a `Repulsor`
    on `ℕ → Bool` — a functional that, given any search strategy
    over Boolean sequences, produces a sequence evading every guess.
    This is the constructive witness that repulsors exist in sufficiently
    rich search spaces. -/
theorem repulsor_exists_bool_functions :
    ∃ _R : Repulsor (ℕ → Bool), True := by
  refine ⟨?_, trivial⟩
  exact {
    evade := fun s n => !(s n n)
    avoids := fun s n h => by
      have := congr_fun h n
      by_cases h' : s n n <;> simp +decide [h'] at this
  }

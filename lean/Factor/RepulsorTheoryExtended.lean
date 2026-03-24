import Mathlib

/-!
# Extended Repulsor Theory: New Frontiers in Evasion Mathematics

This file extends the original Repulsor Theory with new research directions:

1. **Quantitative Evasion**: Infinitely many distinct repulsors for any enumeration.
2. **Iterated Diagonalization**: Injective tower of evaders.
3. **Evasion Semigroup**: Composition of increasing maps preserves fixed-point-freeness.
4. **Oracle-Repulsor Partition**: Every point is exactly one.
5. **Grand Evasion Principle**: Fixed + displaced = total.
6. **Cantor Diagonal Engine**: The universal source of repulsors.
7. **Wandering Points**: Dynamical repulsors.
8. **Monotone Oracle Existence**: Finite Knaster-Tarski.
9. **Constructive Repulsor Hierarchy**: Explicit tower of increasing repulsors.
10. **Repulsor Extension**: Partial repulsors extend to total ones.
11. **Displacement Spectrum**: Measuring repulsor strength.
12. **Repulsor Zoo**: Diverse concrete constructions.
-/

open Set Function Nat Classical

noncomputable section

/-! ## Part I: Quantitative Evasion Theory -/

/-- A function `g` is a repulsor for `enum` if it differs diagonally. -/
def IsRepulsor' (g : ℕ → ℕ) (enum : ℕ → (ℕ → ℕ)) : Prop :=
  ∀ i, g i ≠ enum i i

/-- The diagonal shift is always a repulsor. -/
theorem repulsor_exists_diagonal' (enum : ℕ → (ℕ → ℕ)) :
    IsRepulsor' (fun i => enum i i + 1) enum := by
  intro i; simp

/-- Any positive offset gives a repulsor. -/
theorem repulsor_family' (enum : ℕ → (ℕ → ℕ)) (c : ℕ) (hc : 0 < c) :
    IsRepulsor' (fun i => enum i i + c) enum := by
  intro i; dsimp; omega

/-- Different offsets give different repulsors. -/
theorem repulsor_family_injective' (enum : ℕ → (ℕ → ℕ)) (c₁ c₂ : ℕ)
    (hc : c₁ ≠ c₂) :
    (fun i => enum i i + c₁) ≠ (fun i => enum i i + c₂) := by
  intro h; have := congr_fun h 0; omega

/-- **Repulsor Abundance**: Infinitely many pairwise-distinct repulsors exist. -/
theorem repulsor_abundance' (enum : ℕ → (ℕ → ℕ)) :
    ∃ family : ℕ → (ℕ → ℕ),
      (∀ n, IsRepulsor' (family n) enum) ∧ Injective family := by
  refine ⟨fun c i => enum i i + c + 1, fun n i => ?_, fun a b h => ?_⟩
  · dsimp; omega
  · have := congr_fun h 0; dsimp at this; omega

/-! ## Part II: Iterated Diagonalization Tower -/

/-- The diagonal evader. -/
def diagEvader (enum : ℕ → (ℕ → ℕ)) : ℕ → ℕ := fun i => enum i i + 1

/-- Iterated diagonalization tower. -/
def diagTower (base : ℕ → (ℕ → ℕ)) : ℕ → (ℕ → ℕ)
  | 0 => diagEvader base
  | n + 1 => fun i => (diagTower base n) i + 1

/-- Tower values strictly exceed base values. -/
theorem diagTower_gt_base (base : ℕ → (ℕ → ℕ)) (n : ℕ) :
    ∀ i, base i i < diagTower base n i := by
  intro i; induction n with
  | zero => simp [diagTower, diagEvader]
  | succ n ih => simp [diagTower]; omega

/-- Tower levels are strictly monotone. -/
theorem diagTower_strict_mono (base : ℕ → (ℕ → ℕ)) :
    ∀ m n : ℕ, m < n → ∀ i, diagTower base m i < diagTower base n i := by
  intro m n hmn i
  induction n with
  | zero => omega
  | succ n ih =>
    simp only [diagTower]
    rcases Nat.lt_succ_iff_lt_or_eq.mp hmn with h | h
    · linarith [ih h]
    · subst h; omega

/-- Tower levels are distinct functions. -/
theorem diagTower_injective (base : ℕ → (ℕ → ℕ)) :
    Injective (diagTower base) := by
  intro a b hab
  by_contra h
  rcases lt_or_gt_of_ne h with hlt | hlt
  · exact absurd (congr_fun hab 0) (Nat.ne_of_lt (diagTower_strict_mono base a b hlt 0))
  · exact absurd (congr_fun hab 0).symm (Nat.ne_of_lt (diagTower_strict_mono base b a hlt 0))

/-- Each tower level evades the base enumeration. -/
theorem diagTower_evades (base : ℕ → (ℕ → ℕ)) (n : ℕ) :
    IsRepulsor' (diagTower base n) base := by
  intro i; exact Nat.ne_of_gt (diagTower_gt_base base n i)

/-! ## Part III: The Evasion Semigroup -/

/-- Fixed-point-free predicate. -/
def IsFixedPointFree' {α : Type*} (f : α → α) : Prop := ∀ x, f x ≠ x

/-- Composition of increasing maps on ℕ is fixed-point-free. -/
theorem fpf_composition_increasing
    (f g : ℕ → ℕ) (hf : ∀ n, n < f n) (hg : ∀ n, n < g n) :
    IsFixedPointFree' (f ∘ g) := by
  intro x; simp [comp]; linarith [hg x, hf (g x)]

/-- Iterate formula for successor. -/
theorem succ_iter_eq (n x : ℕ) : Nat.succ^[n] x = x + n := by
  induction n generalizing x with
  | zero => simp
  | succ k ih => rw [iterate_succ', comp_apply, ih]; omega

/-- n-fold successor is fpf for n > 0. -/
theorem succ_iterate_fpf' (n : ℕ) (hn : 0 < n) :
    IsFixedPointFree' (Nat.succ^[n]) := by
  intro x; rw [succ_iter_eq]; omega

/-- Positive shifts compose: closure under addition. -/
theorem shift_closure (a b : ℕ) (ha : 0 < a) (hb : 0 < b) :
    (∀ n : ℕ, n + a ≠ n) ∧ (∀ n : ℕ, n + b ≠ n) ∧ (∀ n : ℕ, n + (a + b) ≠ n) :=
  ⟨fun n => by omega, fun n => by omega, fun n => by omega⟩

/-! ## Part IV: Oracle-Repulsor Duality -/

/-- An oracle for f is a fixed point. -/
def IsOracle' {α : Type*} (f : α → α) (x : α) : Prop := f x = x

/-- A repulsor point for f is a displaced point. -/
def IsRepulsorPt' {α : Type*} (f : α → α) (x : α) : Prop := f x ≠ x

/-- Every point is either an oracle or a repulsor, never both. -/
theorem oracle_repulsor_partition' {α : Type*} (f : α → α) (x : α) :
    IsOracle' f x ↔ ¬ IsRepulsorPt' f x := by
  simp [IsOracle', IsRepulsorPt']

/-- The oracle and repulsor sets are complementary. -/
theorem oracle_repulsor_complement' {α : Type*} (f : α → α) :
    {x | IsOracle' f x} = {x | IsRepulsorPt' f x}ᶜ := by
  ext x; simp [IsOracle', IsRepulsorPt']

/-! ## Part V: Mixed Oracle-Repulsor Objects -/

/-- A mixed object: oracle at even positions, repulsor at odd. -/
def mixedOracleRepulsor (enum : ℕ → (ℕ → ℕ)) : ℕ → ℕ :=
  fun i => if i % 2 = 0 then enum i i else enum i i + 1

theorem mixed_oracle_even (enum : ℕ → (ℕ → ℕ)) (i : ℕ) (hi : i % 2 = 0) :
    mixedOracleRepulsor enum i = enum i i := by
  simp [mixedOracleRepulsor, hi]

theorem mixed_repulsor_odd (enum : ℕ → (ℕ → ℕ)) (i : ℕ) (hi : i % 2 = 1) :
    mixedOracleRepulsor enum i ≠ enum i i := by
  simp [mixedOracleRepulsor]; omega

/-! ## Part VI: The Evasion Set -/

/-- Positions where g disagrees diagonally with enum. -/
def evasionSet (g : ℕ → ℕ) (enum : ℕ → (ℕ → ℕ)) : Set ℕ :=
  {i | g i ≠ enum i i}

/-- A total repulsor has evasion set = univ. -/
theorem total_repulsor_evasion (g : ℕ → ℕ) (enum : ℕ → (ℕ → ℕ))
    (h : IsRepulsor' g enum) : evasionSet g enum = Set.univ := by
  ext i; simp [evasionSet]; exact h i

/-! ## Part VII: Information-Theoretic Evasion -/

/-- After k queries in n positions, remaining hiding spots. -/
def remainingPositions (n k : ℕ) : ℕ := n - k

/-- After k < n queries, spots remain. -/
theorem searcher_deficit' (n k : ℕ) (hk : k < n) :
    0 < remainingPositions n k := by
  simp [remainingPositions]; omega

/-- More queries reduce hiding spots. -/
theorem query_monotone' (n k₁ k₂ : ℕ) (h : k₁ ≤ k₂) (hk : k₂ ≤ n) :
    remainingPositions n k₂ ≤ remainingPositions n k₁ := by
  simp [remainingPositions]; omega

/-- **The Last Query Theorem**: n queries suffice, n-1 never do. -/
theorem last_query_essential' (n : ℕ) (hn : 0 < n) :
    (∀ target : Fin n, ∃ queries : Finset (Fin n), queries.card = n ∧ target ∈ queries) ∧
    (∀ queries : Finset (Fin n), queries.card = n - 1 → ∃ target : Fin n, target ∉ queries) := by
  constructor
  · exact fun target => ⟨Finset.univ, by simp, Finset.mem_univ _⟩
  · intro queries hcard
    by_contra h; push_neg at h
    have hle : Finset.univ ⊆ queries := fun x _ => h x
    have := Finset.card_le_card hle
    simp at this; omega

/-! ## Part VIII: Dynamical Repulsors -/

/-- A point is wandering if its orbit exceeds any bound. -/
def IsWandering' (f : ℕ → ℕ) (x : ℕ) : Prop :=
  ∀ B : ℕ, ∃ n : ℕ, B < f^[n] x

/-- Every point wanders under successor. -/
theorem succ_wandering' (x : ℕ) : IsWandering' Nat.succ x := by
  intro B; use B + 1; rw [succ_iter_eq]; omega

/-- Iterate formula for shifts. -/
theorem shift_iterate (c x n : ℕ) : (· + c)^[n] x = x + n * c := by
  induction n with
  | zero => simp
  | succ n ih => rw [iterate_succ', comp_apply, ih]; ring

/-- Every point wanders under x ↦ x + c for c > 0. -/
theorem shift_wandering' (c : ℕ) (hc : 0 < c) (x : ℕ) :
    IsWandering' (· + c) x := by
  intro B; use B + 1; rw [shift_iterate]; nlinarith

/-- Iterates of a fixed point are constant. -/
theorem fixed_iterate' (f : ℕ → ℕ) (x : ℕ) (hfx : f x = x) :
    ∀ n, f^[n] x = x := by
  intro n; induction n with
  | zero => simp
  | succ n ih => simp [iterate_succ, comp, ih, hfx]

/-- Fixed points don't wander. -/
theorem fixed_not_wandering' (f : ℕ → ℕ) (x : ℕ) (hfx : f x = x) :
    ¬ IsWandering' f x := by
  intro hw; obtain ⟨n, hn⟩ := hw (x + 1)
  rw [fixed_iterate' f x hfx n] at hn; omega

/-- Iterate formula for doubling. -/
theorem doubling_iterate' (x n : ℕ) : (· * 2)^[n] x = x * 2 ^ n := by
  induction n with
  | zero => simp
  | succ n ih => rw [iterate_succ', comp_apply, ih]; ring

/-
PROBLEM
Every positive point wanders under doubling.

PROVIDED SOLUTION
Use doubling_iterate' to rewrite the iterate as x * 2^n. Then we need B < x * 2^n for some n. Since x > 0, x * 2^n grows without bound. Use n = B+1 (or any sufficiently large n). We have x * 2^n ≥ 1 * 2^n = 2^n. For n = B, 2^B ≥ B+1 > B for all B (by Nat.lt_two_pow_self or similar).
-/
theorem doubling_wandering' (x : ℕ) (hx : 0 < x) :
    IsWandering' (· * 2) x := by
  intro B;
  -- Choose $n = B + 1$.
  use B + 1;
  induction' B with B ih <;> simp_all +decide [ Function.iterate_succ_apply' ] ; nlinarith [ Nat.one_le_pow B 2 zero_lt_two ] ;

/-
PROBLEM
**Monotone Orbit Dichotomy**: orbits stabilize or strictly increase.

PROVIDED SOLUTION
By classical logic, either ∃ n with f^[n] x = f^[n+1] x, or ∀ n, f^[n] x ≠ f^[n+1] x. In the second case, prove f^[n] x < f^[n+1] x by induction on n. Base: if x ≤ f x and x ≠ f x, then x < f x. For the inductive step: f^[n] x < f^[n+1] x (IH), so by monotonicity of f, f^[n+1] x ≤ f^[n+2] x; combined with f^[n+1] x ≠ f^[n+2] x gives strict inequality. The key insight: show x ≤ f x by considering that if f x < x, then by monotonicity f(f x) ≤ f x < x, so the orbit is decreasing and bounded below by 0, must stabilize — contradiction. So x ≤ f x, which with x ≠ f x gives x < f x.
-/
theorem monotone_orbit_dichotomy' (f : ℕ → ℕ) (hf : Monotone f) (x : ℕ) :
    (∃ n, f^[n] x = f^[n + 1] x) ∨ (∀ n, f^[n] x < f^[n + 1] x) := by
  by_contra! h_contra;
  -- If there exists some $n$ such that $f^{[n+1]} x \leq f^{[n]} x$, then by induction, for all $m \geq n$, $f^{[m+1]} x \leq f^{[m]} x$.
  obtain ⟨n, hn⟩ : ∃ n, f^[n + 1] x ≤ f^[n] x := h_contra.right
  have h_ind : ∀ m ≥ n, f^[m + 1] x ≤ f^[m] x := by
    intro m hm; induction hm <;> simp_all +decide [ Function.iterate_succ_apply' ] ;
    exact hf ‹_›;
  -- Since $f^{[n+1]} x \leq f^{[n]} x$, the sequence $f^{[n]} x$ is strictly decreasing and bounded below by $0$.
  have h_decreasing : StrictAnti (fun m => f^[n + m] x) := by
    refine' strictAnti_nat_of_succ_lt _;
    grind +ring;
  exact absurd ( Set.infinite_range_of_injective h_decreasing.injective ) ( Set.not_infinite.mpr <| Set.finite_iff_bddAbove.mpr ⟨ _, Set.forall_mem_range.mpr fun m => h_decreasing.antitone m.zero_le ⟩ )

/-! ## Part IX: Cantor Diagonal — Universal Repulsor Engine -/

/-- No function ℕ → (ℕ → Bool) is surjective. -/
theorem cantor_diagonal' (f : ℕ → (ℕ → Bool)) :
    ∃ g : ℕ → Bool, ∀ n, g ≠ f n :=
  ⟨fun n => !(f n n), fun n h => by have := congr_fun h n; simp at this⟩

/-- The diagonal gives a Bool-valued repulsor. -/
theorem cantor_repulsor' (enum : ℕ → (ℕ → Bool)) :
    ∃ g : ℕ → Bool, ∀ i, g i ≠ enum i i :=
  ⟨fun i => !(enum i i), fun i => by simp⟩

/-! ## Part X: The Repulsor Zoo -/

theorem zoo_successor : IsFixedPointFree' (fun n : ℕ => n + 1) := by
  intro n; dsimp; omega

theorem zoo_squaring : IsFixedPointFree' (fun n : ℕ => n * n + 1) := by
  intro n; dsimp
  cases n with
  | zero => omega
  | succ m => nlinarith [Nat.zero_le m]

theorem zoo_fib_shift : IsFixedPointFree' (fun n : ℕ => n + Nat.fib n + 1) := by
  intro n; dsimp; omega

theorem zoo_polynomial (c : ℕ) (hc : 0 < c) :
    IsFixedPointFree' (fun n : ℕ => n + c) := by
  intro n; dsimp; omega

/-- Product of repulsors is a repulsor. -/
theorem product_repulsor' (f g : ℕ → ℕ) (hf : IsFixedPointFree' f)
    (_hg : IsFixedPointFree' g) :
    IsFixedPointFree' (fun p : ℕ × ℕ => (f p.1, g p.2)) := by
  intro ⟨a, b⟩; dsimp
  intro h; exact absurd (Prod.mk.inj h).1 (hf a)

/-! ## Part XI: Constructive Repulsor Hierarchy -/

/-- Level-k repulsor: displaces by k+1. -/
def levelRepulsor (k : ℕ) : ℕ → ℕ := fun n => n + k + 1

/-- Every level repulsor is fpf. -/
theorem levelRepulsor_fpf (k : ℕ) : IsFixedPointFree' (levelRepulsor k) := by
  intro n; simp [levelRepulsor]; omega

/-- Higher levels displace more. -/
theorem levelRepulsor_increasing (j k : ℕ) (hjk : j < k) :
    ∀ n, levelRepulsor j n < levelRepulsor k n := by
  intro n; simp [levelRepulsor]; omega

/-- No two levels are the same function. -/
theorem levelRepulsor_strict (j k : ℕ) (hjk : j ≠ k) :
    levelRepulsor j ≠ levelRepulsor k := by
  intro h; have := congr_fun h 0; simp [levelRepulsor] at this; omega

/-! ## Part XII: Repulsor Extension Theorem -/

/-- Extend a partial repulsor to cover one more entry. -/
theorem repulsor_extension' (enum : ℕ → (ℕ → ℕ)) (g : ℕ → ℕ) (k : ℕ)
    (hk : ∀ i, i < k → g i ≠ enum i i) :
    ∃ g' : ℕ → ℕ, (∀ i, i < k → g' i = g i) ∧
    (∀ i, i < k + 1 → g' i ≠ enum i i) := by
  use fun i => if i < k then g i else enum i i + 1
  refine ⟨fun i hi => by simp [hi], fun i hi => ?_⟩
  simp only; split
  · rename_i hik; exact hk i hik
  · omega

/-- A total repulsor always exists. -/
theorem total_repulsor_exists' (enum : ℕ → (ℕ → ℕ)) :
    ∃ g : ℕ → ℕ, IsRepulsor' g enum :=
  ⟨fun i => enum i i + 1, repulsor_exists_diagonal' enum⟩

/-! ## Part XIII: Grand Evasion Principle -/

/-- Fixed points + displaced points = total. -/
theorem grand_evasion_principle' (n : ℕ) (f : Fin n → Fin n) :
    (Finset.univ.filter (fun x => f x = x)).card +
    (Finset.univ.filter (fun x => f x ≠ x)).card = n := by
  have := Finset.card_filter_add_card_filter_not (s := Finset.univ) (p := fun x => f x = x)
  simpa using this

/-- Negation is a repulsor on nonzero integers. -/
theorem negation_repulsor' : ∀ n : ℤ, n ≠ 0 → -n ≠ n := by omega

/-- A derangement is a total repulsor. -/
theorem derangement_total {n : ℕ} (σ : Equiv.Perm (Fin n))
    (hσ : ∀ x, σ x ≠ x) : IsFixedPointFree' σ := hσ

/-! ## Part XIV: Monotone Oracle Existence (Finite Knaster-Tarski) -/

/-
PROBLEM
Every monotone function on Fin(n+1) has a fixed point.

PROVIDED SOLUTION
Consider the set S = {i : Fin (n+1) | i ≤ f i}. Since 0 ≤ f 0, we have 0 ∈ S so S is nonempty. Let m be the maximum of S (exists since Fin (n+1) is finite). Then m ≤ f m. If m < f m, then f m ≤ f(f m) by monotonicity, so f m ∈ S, contradicting maximality of m. Therefore f m = m, which gives IsOracle' f m.
-/
theorem monotone_fin_fixed_point' (n : ℕ) (f : Fin (n + 1) → Fin (n + 1))
    (hf : Monotone f) : ∃ x, IsOracle' f x := by
  by_contra h_no_fixed_point;
  -- Consider the set S = {i : Fin (n+1) | i ≤ f i}. Since 0 ≤ f 0, we have 0 ∈ S so S is nonempty.
  have hS_nonempty : ∃ i : Fin (n + 1), i ≤ f i := by
    exact ⟨ 0, Nat.zero_le _ ⟩;
  -- Let m be the maximum of S (exists since Fin (n+1) is finite).
  obtain ⟨m, hm⟩ : ∃ m : Fin (n + 1), m ∈ {i : Fin (n + 1) | i ≤ f i} ∧ ∀ i ∈ {i : Fin (n + 1) | i ≤ f i}, i ≤ m := by
    exact ⟨ Finset.max' ( Finset.univ.filter fun i => i ≤ f i ) ⟨ hS_nonempty.choose, Finset.mem_filter.mpr ⟨ Finset.mem_univ _, hS_nonempty.choose_spec ⟩ ⟩, Finset.mem_filter.mp ( Finset.max'_mem ( Finset.univ.filter fun i => i ≤ f i ) ⟨ hS_nonempty.choose, Finset.mem_filter.mpr ⟨ Finset.mem_univ _, hS_nonempty.choose_spec ⟩ ⟩ ) |>.2, fun i hi => Finset.le_max' _ _ ( by simpa using hi ) ⟩;
  -- If m < f m, then f m ≤ f(f m) by monotonicity, so f m ∈ S, contradicting maximality of m.
  by_cases hm_lt_fm : m < f m;
  · exact not_lt_of_ge ( hm.2 ( f m ) ( by simpa using hf hm_lt_fm.le ) ) hm_lt_fm;
  · exact h_no_fixed_point ⟨ m, le_antisymm ( le_of_not_gt hm_lt_fm ) hm.1 ⟩

/-! ## Part XV: Displacement Spectrum -/

/-- Displacement of f at x. -/
def displacement (f : ℕ → ℕ) (x : ℕ) : ℤ := (f x : ℤ) - (x : ℤ)

/-- Positive displacement implies fpf. -/
theorem positive_displacement_fpf (f : ℕ → ℕ) (h : ∀ x, 0 < displacement f x) :
    IsFixedPointFree' f := by
  intro x; have := h x; simp [displacement] at this; omega

/-- Negative displacement implies fpf. -/
theorem negative_displacement_fpf (f : ℕ → ℕ) (h : ∀ x, displacement f x < 0) :
    IsFixedPointFree' f := by
  intro x; have := h x; simp [displacement] at this; omega

/-- Total displacement over first n points. -/
def totalDisplacement (f : ℕ → ℕ) (n : ℕ) : ℤ :=
  (Finset.range n).sum (fun i => displacement f i)

/-- Successor has total displacement n. -/
theorem succ_total_displacement' (n : ℕ) :
    totalDisplacement Nat.succ n = n := by
  simp [totalDisplacement, displacement]

/-- Shift by c has total displacement n * c. -/
theorem shift_total_displacement' (c : ℕ) (n : ℕ) :
    totalDisplacement (· + c) n = n * c := by
  simp [totalDisplacement, displacement]

/-! ## Part XVI: Repulsor Density -/

/-- Any finite set in an infinite type has elements outside it. -/
theorem infinite_evades_finite {α : Type*} [Infinite α]
    (S : Finset α) : ∃ x : α, x ∉ S :=
  Infinite.exists_notMem_finset S

/-- Two distinct elements evade any finite set in an infinite type. -/
theorem two_evade_finite {α : Type*} [Infinite α]
    (S : Finset α) : ∃ x y : α, x ∉ S ∧ y ∉ S ∧ x ≠ y := by
  obtain ⟨x, hx⟩ := Infinite.exists_notMem_finset S
  obtain ⟨y, hy⟩ := Infinite.exists_notMem_finset ({x} ∪ S)
  simp at hy
  exact ⟨x, y, hx, hy.2, Ne.symm hy.1⟩

/-! ## Part XVII: Evasion Depth Hierarchy -/

/-- Evasion depth: how many initial entries g evades. -/
def evasionDepth (g : ℕ → ℕ) (enum : ℕ → (ℕ → ℕ)) : ℕ → Prop
  | 0 => True
  | n + 1 => g n ≠ enum n n ∧ evasionDepth g enum n

/-- Evasion depth is monotone. -/
theorem evasionDepth_mono (g : ℕ → ℕ) (enum : ℕ → (ℕ → ℕ)) (n : ℕ) :
    evasionDepth g enum (n + 1) → evasionDepth g enum n :=
  fun ⟨_, h⟩ => h

/-- The diagonal evader has infinite evasion depth. -/
theorem diagEvader_infinite_depth (enum : ℕ → (ℕ → ℕ)) :
    ∀ k, evasionDepth (diagEvader enum) enum k := by
  intro k; induction k with
  | zero => trivial
  | succ n ih => exact ⟨by simp [diagEvader], ih⟩

/-! ## Part XVIII: The Repulsor Lattice -/

/-- Minimum displacement over first n points. -/
def minDisplacement (f : ℕ → ℕ) (n : ℕ) : ℤ :=
  if h : n = 0 then 0
  else (Finset.range n).inf' (by simp [h]) (fun i => displacement f i)

/-- A "stronger" repulsor displaces more at every point. -/
def StrongerRepulsor (f g : ℕ → ℕ) : Prop :=
  ∀ n, displacement f n ≥ displacement g n

/-- Stronger-repulsor is reflexive. -/
theorem strongerRepulsor_refl (f : ℕ → ℕ) : StrongerRepulsor f f :=
  fun _ => le_refl _

/-- Stronger-repulsor is transitive. -/
theorem strongerRepulsor_trans (f g h : ℕ → ℕ)
    (hfg : StrongerRepulsor f g) (hgh : StrongerRepulsor g h) :
    StrongerRepulsor f h :=
  fun n => le_trans (hgh n) (hfg n)

/-- Level k+1 repulsor is stronger than level k. -/
theorem levelRepulsor_stronger (k : ℕ) :
    StrongerRepulsor (levelRepulsor (k + 1)) (levelRepulsor k) := by
  intro n; simp [displacement, levelRepulsor]

end
import Mathlib

/-!
# Model Theory Explorations

Formal proofs of model-theoretic results and their connections to
inside-out factoring and algebraic structures.
-/

/-! ## §1: Consistency of Theories -/

/-- The theory of additive groups is consistent: ℤ is an additive group. -/
theorem addgroup_theory_consistent : ∃ (G : Type) (_ : AddCommGroup G), True :=
  ⟨ℤ, inferInstance, trivial⟩

/-- The theory of fields is consistent: ℚ is a field. -/
theorem field_theory_consistent : ∃ (F : Type) (_ : Field F), True :=
  ⟨ℚ, inferInstance, trivial⟩

/-- ACF₀ is consistent: ℂ is an algebraically closed field of characteristic 0. -/
theorem acf0_consistent : ∃ (F : Type) (_ : Field F) (_ : IsAlgClosed F) (_ : CharZero F), True :=
  ⟨Complex, inferInstance, Complex.isAlgClosed, inferInstance, trivial⟩

/-! ## §2: Dense Linear Orders -/

/-- ℚ is densely ordered (Cantor's back-and-forth consequence). -/
theorem rat_dense (a b : ℚ) (h : a < b) : ∃ c : ℚ, a < c ∧ c < b :=
  DenselyOrdered.dense a b h

/-! ## §3: Counting Types -/

/-- The number of subsets of Fin n is 2^n. -/
theorem powerset_card (n : ℕ) :
    Fintype.card (Finset (Fin n)) = 2 ^ n := by
  simp [Fintype.card_finset]

/-! ## §4: Group Theory in Model Theory -/

/-- Lagrange's theorem: subgroup order divides group order. -/
theorem lagrange_divides {G : Type*} [Group G] [Fintype G]
    (H : Subgroup G) [Fintype H] :
    Nat.card H ∣ Nat.card G :=
  Subgroup.card_subgroup_dvd_card H

/-- Every element of a finite group has finite order dividing |G|. -/
theorem order_divides_card {G : Type*} [Group G] [Fintype G] (g : G) :
    orderOf g ∣ Fintype.card G :=
  orderOf_dvd_card

/-! ## §5: Countable Models -/

/-- ℚ is a countable field (Löwenheim-Skolem consequence). -/
theorem countable_field_exists : ∃ (F : Type) (_ : Field F) (_ : Countable F), True :=
  ⟨ℚ, inferInstance, inferInstance, trivial⟩

/-- ℤ is a countable infinite integral domain. -/
theorem countable_infinite_domain : ∃ (R : Type) (_ : CommRing R) (_ : IsDomain R)
    (_ : Countable R) (_ : Infinite R), True :=
  ⟨ℤ, inferInstance, inferInstance, inferInstance, inferInstance, trivial⟩

/-! ## §6: Definability and Composites -/

/-- A number n ≥ 2 is composite iff it has a nontrivial divisor. -/
theorem composite_iff (n : ℕ) (hn : 2 ≤ n) :
    ¬ Nat.Prime n ↔ ∃ d : ℕ, 2 ≤ d ∧ d < n ∧ d ∣ n := by
  constructor
  · intro h
    have hne : n ≠ 1 := by omega
    have hmf := Nat.minFac_prime hne
    have hmfd := Nat.minFac_dvd n
    refine ⟨n.minFac, ?_, ?_, hmfd⟩
    · exact hmf.two_le
    · by_contra hle
      push_neg at hle
      have : n.minFac = n := by
        apply le_antisymm (Nat.minFac_le (by omega)) hle
      exact h (this ▸ hmf)
  · rintro ⟨d, hd1, hd2, hd3⟩ hp
    have := hp.eq_one_or_self_of_dvd d hd3
    omega

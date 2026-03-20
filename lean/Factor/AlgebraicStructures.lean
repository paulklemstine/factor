import Mathlib

/-!
# Algebraic Structures: Rings, Fields, and Beyond

Explorations across:
- Ring homomorphisms
- Ideal theory
- Noetherian rings
- Unique factorization
-/

section RingHomomorphisms

/-
Ring hom preserves 0
-/
theorem ring_hom_zero_map {R S : Type*} [Semiring R] [Semiring S] (f : R →+* S) :
    f 0 = 0 := by
      exact map_zero f

/-
Ring hom preserves 1
-/
theorem ring_hom_one_map {R S : Type*} [Semiring R] [Semiring S] (f : R →+* S) :
    f 1 = 1 := by
      exact?

/-
Ring hom preserves addition
-/
theorem ring_hom_add_map {R S : Type*} [Semiring R] [Semiring S] (f : R →+* S) (a b : R) :
    f (a + b) = f a + f b := by
      exact f.map_add a b

/-
Ring hom preserves multiplication
-/
theorem ring_hom_mul_map {R S : Type*} [Semiring R] [Semiring S] (f : R →+* S) (a b : R) :
    f (a * b) = f a * f b := by
      exact f.map_mul a b

end RingHomomorphisms

section Ideals

/-
Zero ideal contains only zero
-/
theorem bot_ideal_iff {R : Type*} [CommRing R] (x : R) :
    x ∈ (⊥ : Ideal R) ↔ x = 0 := by
      exact?

/-
The whole ring is an ideal
-/
theorem top_ideal_univ {R : Type*} [CommRing R] (x : R) :
    x ∈ (⊤ : Ideal R) := by
      trivial

/-
Product of ideals ≤ intersection
-/
theorem ideal_mul_le_meet {R : Type*} [CommRing R] (I J : Ideal R) :
    I * J ≤ I ⊓ J := by
      exact?

end Ideals

section UFD

/-- ℤ is a UFD -/
theorem int_ufd : UniqueFactorizationMonoid ℤ := inferInstance

/-
A PID is a UFD
-/
theorem pid_ufd {R : Type*} [CommRing R] [IsDomain R] [IsPrincipalIdealRing R] :
    UniqueFactorizationMonoid R := by
      exact?

end UFD

section QuotientRings

/-
ℤ/nℤ has n elements
-/
theorem zmod_card_n (n : ℕ) [NeZero n] : Fintype.card (ZMod n) = n := by
  convert ZMod.card n

/-
ℤ/2ℤ is a field
-/
theorem zmod_2_is_field : IsField (ZMod 2) := by
  exact @Field.toIsField ( ZMod 2 ) _

end QuotientRings

section Noetherian

/-- ℤ is Noetherian -/
theorem int_noetherian : IsNoetherianRing ℤ := inferInstance

/-
A field is Noetherian
-/
theorem field_noetherian_ring {F : Type*} [Field F] : IsNoetherianRing F := by
  infer_instance

end Noetherian
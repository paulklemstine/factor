/-
# Commutative Algebra
-/

import Mathlib

open Ideal Polynomial

/-! ## Ideal Properties -/

theorem ideal_mul_le_inf' {R : Type*} [CommRing R] (I J : Ideal R) :
    I * J ≤ I ⊓ J := Ideal.mul_le_inf

theorem maximal_is_prime' {R : Type*} [CommRing R] (I : Ideal R)
    [hI : I.IsMaximal] : I.IsPrime := Ideal.IsMaximal.isPrime hI

/-! ## Noetherian Rings -/

theorem int_noetherian' : IsNoetherianRing ℤ := inferInstance

theorem quotient_noetherian' {R : Type*} [CommRing R] [IsNoetherianRing R]
    (I : Ideal R) : IsNoetherianRing (R ⧸ I) := inferInstance

theorem polynomial_noetherian' {R : Type*} [CommRing R] [IsNoetherianRing R] :
    IsNoetherianRing R[X] := inferInstance

/-! ## Chinese Remainder Theorem -/

theorem crt_coprime' {R : Type*} [CommRing R] (I J : Ideal R) (h : I ⊔ J = ⊤) :
    I ⊓ J = I * J :=
  Ideal.inf_eq_mul_of_isCoprime (Ideal.isCoprime_iff_sup_eq.mpr h)

/-! ## Finite Domains -/

theorem finite_domain_is_field' (R : Type*) [CommRing R] [IsDomain R]
    [Finite R] : IsField R :=
  Finite.isField_of_domain R

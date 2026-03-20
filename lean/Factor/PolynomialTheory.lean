import Mathlib

/-!
# Polynomial Theory and Algebraic Structures

Explorations across:
- Polynomial identities and factorizations
- Irreducibility criteria
- Finite field polynomial theory
- Ring theory connections
-/

open Polynomial BigOperators

section PolynomialBasics

/-
X^2 - 1 = (X - 1)(X + 1) over ℤ
-/
theorem diff_of_squares_poly :
    (X ^ 2 - 1 : Polynomial ℤ) = (X - 1) * (X + 1) := by
  ring

/-
X^2 + 1 has no integer root
-/
theorem x2_plus_1_no_root : ∀ a : ℤ, a ^ 2 + 1 ≠ 0 := by
  exact fun a => by positivity;

/-
Geometric series polynomial identity
-/
theorem geom_series_poly (n : ℕ) :
    (X - 1 : Polynomial ℤ) * ∑ i ∈ Finset.range n, X ^ i = X ^ n - 1 := by
  rw [ mul_comm, geom_sum_mul ]

end PolynomialBasics

section RingTheory

/-- ℤ is an integral domain -/
theorem int_domain : IsDomain ℤ := inferInstance

/-- ℤ is a PID -/
theorem int_pid : IsPrincipalIdealRing ℤ := inferInstance

/-
Every nonzero element of a field is a unit
-/
theorem field_unit {F : Type*} [Field F] (a : F) (ha : a ≠ 0) :
    IsUnit a := by
  exact isUnit_iff_ne_zero.mpr ha

/-
ℤ/pℤ is a field for prime p
-/
theorem zmod_field (p : ℕ) (hp : Nat.Prime p) :
    IsField (ZMod p) := by
  haveI := Fact.mk hp; exact @Field.toIsField ( ZMod p ) _;

/-
Every finite integral domain is a field
-/
theorem finite_domain_field (R : Type*) [CommRing R] [IsDomain R] [Fintype R] [Nontrivial R] :
    IsField R := by
  exact?

end RingTheory

section FiniteFields

/-
GF(p) has exactly p elements
-/
theorem gf_card_eq (p : ℕ) [Fact (Nat.Prime p)] : Fintype.card (ZMod p) = p := by
  convert ZMod.card p

/-
Every element of GF(p) satisfies x^p = x
-/
theorem fermat_gf_p (p : ℕ) [Fact (Nat.Prime p)] (a : ZMod p) :
    a ^ p = a := by
  rw [ ZMod.pow_card ]

/-
The multiplicative group of GF(p) is cyclic
-/
theorem gf_mult_cyclic (p : ℕ) [Fact (Nat.Prime p)] :
    IsCyclic (ZMod p)ˣ := by
  infer_instance

end FiniteFields

section Irreducibility

/-
X² - 2 is irreducible over ℚ
-/
theorem x2_minus_2_irred : Irreducible (X ^ 2 - 2 : Polynomial ℚ) := by
  -- We'll use that $X^2 - 2$ is irreducible over $\mathbb{Q}$ because it has no rational roots and its degree is 2.
  have h_no_rational_roots : ¬∃ (q : ℚ), q^2 = 2 := by
    exact fun ⟨ q, hq ⟩ => by apply_fun fun x => x.num at hq; norm_num [ sq, Rat.mul_self_num ] at hq; nlinarith [ show q.num ≤ 1 by nlinarith, show q.num ≥ -1 by nlinarith ] ;
  -- Apply the fact that a polynomial of degree 2 is irreducible if it has no roots in the field.
  have h_irred : ∀ p q : Polynomial ℚ, p.degree > 0 → q.degree > 0 → ¬(p * q = Polynomial.X ^ 2 - 2) := by
    intros p q hp hq h_eq
    have h_deg : p.degree = 1 ∧ q.degree = 1 := by
      have h_deg : p.degree + q.degree = 2 := by
        erw [ ← Polynomial.degree_mul, h_eq, Polynomial.degree_X_pow_sub_C ] <;> norm_num;
      rw [ Polynomial.degree_eq_natDegree ( Polynomial.ne_zero_of_degree_gt hp ), Polynomial.degree_eq_natDegree ( Polynomial.ne_zero_of_degree_gt hq ) ] at * ; norm_cast at * ; exact ⟨ by linarith, by linarith ⟩;
    -- Let $r$ be a root of $p$. Then $r^2 = 2$, which contradicts $h_no_rational_roots$.
    obtain ⟨r, hr⟩ : ∃ r : ℚ, p.eval r = 0 := by
      exact Polynomial.exists_root_of_degree_eq_one h_deg.1;
    exact h_no_rational_roots ⟨ r, by replace h_eq := congr_arg ( Polynomial.eval r ) h_eq; norm_num [ hr ] at h_eq; linarith ⟩;
  constructor <;> contrapose! h_irred;
  · exact absurd ( Polynomial.degree_eq_zero_of_isUnit h_irred ) ( by erw [ Polynomial.degree_X_pow_sub_C ] <;> norm_num );
  · obtain ⟨ a, b, h₁, h₂, h₃ ⟩ := h_irred; exact ⟨ a, b, not_le.mp fun h => h₂ <| Polynomial.isUnit_iff_degree_eq_zero.mpr <| le_antisymm h <| le_of_not_gt fun h' => by { apply_fun Polynomial.eval 0 at h₁; aesop }, not_le.mp fun h => h₃ <| Polynomial.isUnit_iff_degree_eq_zero.mpr <| le_antisymm h <| le_of_not_gt fun h' => by { apply_fun Polynomial.eval 0 at h₁; aesop }, h₁.symm ⟩ ;

/-
√2 is irrational
-/
theorem sqrt2_irrat : Irrational (Real.sqrt 2) := by
  decide +kernel

end Irreducibility
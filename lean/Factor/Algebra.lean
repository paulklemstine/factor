/-
# Abstract Algebra: Groups, Rings, and Symmetry

Exploration of algebraic structures relevant to the Moonshine conjecture,
quantum computing gate groups, and symmetry-breaking in factoring.
-/

import Mathlib

/-! ## Section 1: Group Theory Fundamentals -/

/-
PROBLEM
Lagrange's theorem: the order of a subgroup divides the order of the group.

PROVIDED SOLUTION
Use Subgroup.card_subgroup_dvd_card or similar Mathlib lemma.
-/
theorem lagrange_theorem {G : Type*} [Group G] [Fintype G]
    (H : Subgroup G) [Fintype H] :
    Fintype.card H ∣ Fintype.card G := by
      convert Subgroup.card_subgroup_dvd_card H using 1 ; aesop;
      rw [ Nat.card_eq_fintype_card ]

/-
PROBLEM
Every group of prime order is cyclic.

PROVIDED SOLUTION
Use isCyclic_of_prime_card from Mathlib.
-/
theorem prime_order_cyclic {G : Type*} [Group G] [Fintype G]
    (hp : (Fintype.card G).Prime) : IsCyclic G := by
      haveI := Fact.mk hp; exact isCyclic_of_prime_card ( by aesop ) ;

/-! ## Section 2: Ring Theory and Factoring -/

/-
PROBLEM
In a principal ideal domain, every irreducible element is prime.

PROVIDED SOLUTION
Use Irreducible.prime from Mathlib (available for PIDs).
-/
theorem irreducible_is_prime_in_pid {R : Type*} [CommRing R] [IsDomain R]
    [IsPrincipalIdealRing R] {p : R} (hp : Irreducible p) : Prime p := by
      convert hp.prime

/-
PROBLEM
The Chinese Remainder Theorem for coprime moduli.

PROVIDED SOLUTION
Use Nat.chineseRemainder or construct the solution directly. Since gcd(m,n)=1, there exist u,v with um+vn=1. The solution x = a*v*n + b*u*m works.
-/
theorem crt_coprime (m n : ℕ) (hm : 0 < m) (hn : 0 < n) (hcoprime : Nat.Coprime m n)
    (a b : ℕ) : ∃ x : ℕ, x % m = a % m ∧ x % n = b % n := by
      have := Nat.chineseRemainder hcoprime a b; aesop;

/-! ## Section 3: Polynomial Rings -/

/-
PROBLEM
x² + 1 is irreducible over ℚ.

PROVIDED SOLUTION
Use Polynomial.irreducible_X_pow_add_C or show it has no rational roots. Alternatively use the fact that x²+1 has no real roots.
-/
theorem x_sq_plus_one_irreducible :
    Irreducible (Polynomial.X ^ 2 + 1 : Polynomial ℚ) := by
      -- We'll use that $x^2 + 1$ is the cyclotomic polynomial $\Phi_4(x)$.
      have h_cyclotomic : Polynomial.X ^ 2 + 1 = Polynomial.cyclotomic 4 ℚ := by
        rw [ show ( 4 : ℕ ) = 2 ^ 2 by norm_num, Polynomial.cyclotomic_prime_pow_eq_geom_sum ] ; norm_num;
        norm_num +zetaDelta at *
      rw [h_cyclotomic] ; exact Polynomial.cyclotomic.irreducible_rat (by decide)
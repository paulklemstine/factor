/-
# Congruence of Squares Factoring -- Formal Foundations

This file formalizes the core mathematical theorem underlying all modern
sub-exponential factoring algorithms: the **congruence of squares** method.

Every major factoring algorithm -- Dixon's method, the Quadratic Sieve (QS),
the Number Field Sieve (NFS), and the proposed Spectral Resonance Sieve --
reduces to finding x, y such that x2 === y2 (mod n) with x ? ?y (mod n),
from which gcd(x - y, n) yields a nontrivial factor.

We formalize:
1. The fundamental factoring theorem (congruence of squares)
2. Properties of smooth numbers relevant to sieve methods
3. The structure of the factor base linear algebra step
-/

import Mathlib

open Nat

/-! ## Part 1: The Congruence of Squares Factoring Theorem -/

/-
If `n` divides `x2 - y2` but does not divide `x - y` or `x + y`,
    then `gcd(x - y, n)` is a nontrivial divisor of `n`.
-/
theorem congruence_of_squares_factoring
    {n x y : Int} (hn : 1 < n)
    (hcong : (n : Int) | x ^ 2 - y ^ 2)
    (hne_sub : ! (n : Int) | x - y)
    (hne_add : ! (n : Int) | x + y) :
    1 < Int.gcd (x - y) n /\ Int.gcd (x - y) n < n.natAbs := by
  refine' < Nat.lt_of_le_of_ne ( Nat.pos_of_dvd_of_pos ( Int.natAbs_dvd_natAbs.mpr ( Int.gcd_dvd_right _ _ ) ) ( Int.natAbs_pos.mpr ( by linarith ) ) ) ( Ne.symm _ ), _ >;
  . contrapose! hne_add;
    exact Int.dvd_of_dvd_mul_right_of_gcd_one ( by convert hcong using 1; ring ) ( Int.gcd_comm _ _ > hne_add );
  . refine' lt_of_le_of_ne ( Nat.le_of_dvd ( Int.natAbs_pos.mpr ( by linarith ) ) ( Int.natCast_dvd.mp ( Int.gcd_dvd_right _ _ ) ) ) fun con => hne_sub _;
    exact Int.dvd_trans ( by norm_num ) ( con > Int.gcd_dvd_left _ _ )

/-
The product of gcd(x-y, n) and gcd(x+y, n) is divisible by n
    when n divides x2 - y2. This is essential: after finding one factor
    via gcd(x-y, n), the cofactor n / gcd(x-y, n) divides gcd(x+y, n).
-/
theorem congruence_of_squares_cofactor
    {n x y : Int} (hn : 1 < n)
    (hcong : (n : Int) | x ^ 2 - y ^ 2) :
    (n : Int) | ?(Int.gcd (x - y) n) * ?(Int.gcd (x + y) n) := by
  grind +suggestions

/-! ## Part 2: GCD yields a divisor -/

/-
gcd(x - y, n) always divides n.
-/
theorem gcd_sub_dvd_n (x y n : Int) : ?(Int.gcd (x - y) n) | n := by
  exact Int.gcd_dvd_right _ _

/-
If n divides x2 - y2, then gcd(x - y, n) * gcd(x + y, n) is a
    multiple of n that is bounded by n2.
-/
theorem gcd_product_bound
    {n x y : Int} (hn : 0 < n)
    (hcong : (n : Int) | x ^ 2 - y ^ 2) :
    (Int.gcd (x - y) n : Int) * (Int.gcd (x + y) n : Int) <= n ^ 2 := by
  nlinarith [ Int.le_of_dvd ( by positivity ) ( Int.gcd_dvd_right ( x - y ) n ), Int.le_of_dvd ( by positivity ) ( Int.gcd_dvd_right ( x + y ) n ) ]

/-! ## Part 3: Smooth Numbers -/

/-- A natural number is B-smooth if all its prime factors are <= B. -/
def isSmooth (B : Nat) (n : Nat) : Prop :=
  forall p : Nat, p.Prime -> p | n -> p <= B

/-
1 is B-smooth for any B.
-/
theorem isSmooth_one (B : Nat) : isSmooth B 1 := by
  exact fun p pp dp => pp.not_dvd_one.elim dp

/-
If m and n are B-smooth, so is m * n.
-/
theorem isSmooth_mul {B m n : Nat} (hm : isSmooth B m) (hn : isSmooth B n) :
    isSmooth B (m * n) := by
  intro p pp dp; rw [ Nat.Prime.dvd_mul pp ] at dp; aesop;

/-
If n is B-smooth and B <= B', then n is B'-smooth.
-/
theorem isSmooth_mono {B B' n : Nat} (h : B <= B') (hn : isSmooth B n) :
    isSmooth B' n := by
  exact fun p pp dp => le_trans ( hn p pp dp ) h

/-
A prime p is B-smooth iff p <= B.
-/
theorem isSmooth_prime_iff {B p : Nat} (hp : p.Prime) :
    isSmooth B p <-> p <= B := by
  exact < fun h => h p hp dvd_rfl, fun h q hq hqp => by rw [ Nat.prime_dvd_prime_iff_eq ] at hqp <;> aesop >

/-! ## Part 4: Factor Base Properties -/

/-- The factor base: the set of primes up to bound B. -/
def factorBase (B : Nat) : Finset Nat :=
  (Finset.range (B + 1)).filter Nat.Prime

/-
Every element of the factor base is prime.
-/
theorem factorBase_prime {B p : Nat} (hp : p in factorBase B) : p.Prime := by
  exact Finset.mem_filter.mp hp |>.2

/-
Every element of the factor base is <= B.
-/
theorem factorBase_le {B p : Nat} (hp : p in factorBase B) : p <= B := by
  exact Finset.mem_range_succ_iff.mp ( Finset.mem_filter.mp hp |>.1 )

/-
A B-smooth number > 0 has all prime factors in the factor base.
-/
theorem smooth_factors_in_base {B n : Nat} (hn : 0 < n) (hs : isSmooth B n) :
    forall p : Nat, p.Prime -> p | n -> p in factorBase B := by
  exact fun p pp dp => Finset.mem_filter.mpr < Finset.mem_range.mpr ( Nat.lt_succ_of_le ( hs p pp dp ) ), pp >

/-! ## Part 5: The Birthday Bound -- why we need ?(#factor_base) + 1 relations -/

/-
If we have more relations than the size of the factor base,
    then the exponent vectors (mod 2) are linearly dependent over GF(2).
    This is the key combinatorial fact: with k primes in the base,
    we need at most k + 1 smooth relations to guarantee a
    congruence of squares via linear algebra over GF(2).

    We state this as a pigeonhole/linear algebra fact over ZMod 2 vectors.
-/
theorem relations_exceed_base_gives_dependency
    {k : Nat} (relations : Fin (k + 1) -> Fin k -> ZMod 2) :
    exists S : Finset (Fin (k + 1)), S.Nonempty /\
      forall j : Fin k, sum i in S, relations i j = 0 := by
  by_contra h;
  -- By the pigeonhole principle, since there are $k+1$ vectors in a $k$-dimensional space, there must be a nontrivial linear combination that sums to zero.
  have h_pigeonhole : exists (s : Fin (k + 1) -> ZMod 2), s != 0 /\ sum i, s i ? relations i = 0 := by
    have h_pigeonhole : exists (s : Fin (k + 1) -> ZMod 2), s != 0 /\ sum i, s i ? relations i = 0 := by
      have h_rank : Module.rank (ZMod 2) (Fin k -> ZMod 2) < k + 1 := by
        erw [ rank_fun' ] ; norm_cast ; norm_num
      have h_linear_dep : !LinearIndependent (ZMod 2) relations := by
        intro h_lin_ind
        have h_card : Module.rank (ZMod 2) (Fin k -> ZMod 2) >= k + 1 := by
          have := h_lin_ind;
          have := this.cardinal_lift_le_rank;
          aesop;
        exact not_lt_of_ge h_card h_rank;
      rw [ Fintype.not_linearIndependent_iff ] at h_linear_dep ; tauto;
    exact h_pigeonhole;
  obtain < s, hs_ne_zero, hs_sum_zero > := h_pigeonhole;
  refine' h < Finset.univ.filter fun i => s i != 0, _, _ > <;> simp_all +decide [ funext_iff, Finset.sum_filter ];
  . exact < hs_ne_zero.choose, Finset.mem_filter.mpr < Finset.mem_univ _, hs_ne_zero.choose_spec > >;
  . intro j; specialize hs_sum_zero j; rw [ Finset.sum_congr rfl fun i hi => by rw [ show s i * relations i j = if s i = 0 then 0 else relations i j by cases Fin.exists_fin_two.mp < s i, rfl > <;> aesop ] ] at hs_sum_zero; aesop;
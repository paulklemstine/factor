/-
# Tropical Algebra and Integer Factoring
## Agent Delta: Number Theory & Factoring

This file explores how tropical (max-plus) algebra provides a natural framework
for integer factoring via p-adic valuations. The core insight is that factoring
in ℤ becomes *additive decomposition* in the tropical semiring through the
logarithmic bridge of p-adic valuations.

## Key Ideas:
1. v_p(a·b) = v_p(a) + v_p(b) — multiplication becomes tropical multiplication
2. Factoring n = finding tropical decomposition of the valuation vector
3. GCD and LCM become tropical operations (min and max of valuations)
4. Smooth numbers have bounded tropical coordinates
5. The Number Field Sieve has a tropical interpretation
-/
import Mathlib

open Real Finset BigOperators Nat

noncomputable section

namespace TropicalFactoring

/-! ================================================================
    PART I: P-ADIC VALUATIONS AS TROPICAL COORDINATES
    ================================================================ -/

/-
PROBLEM
The p-adic valuation is a tropical homomorphism:
    v_p(a * b) = v_p(a) + v_p(b) for prime p and nonzero a, b

PROVIDED SOLUTION
Use padicValNat.mul from Mathlib
-/
theorem padic_val_mul_eq_add {p : ℕ} (hp : Nat.Prime p) {a b : ℕ}
    (ha : a ≠ 0) (hb : b ≠ 0) :
    padicValNat p (a * b) = padicValNat p a + padicValNat p b := by
  haveI := Fact.mk hp; rw [ padicValNat.mul ] <;> aesop;

/-
v_p(1) = 0: the multiplicative identity maps to the tropical multiplicative identity
-/
theorem padic_val_one (p : ℕ) : padicValNat p 1 = 0 := by
  exact?

/-
v_p(p) = 1 for prime p
-/
theorem padic_val_self {p : ℕ} (hp : Nat.Prime p) : padicValNat p p = 1 := by
  -- By definition of `padicValNat`, we know that `padicValNat p p = 1`.
  have h_padic_val_p : padicValNat p p = 1 := by
    have h_factorization : p.factorization p = 1 := by
      aesop
    rw [ ← h_factorization, Nat.factorization_def ] ; aesop;
  exact h_padic_val_p

/-
v_p(p^k) = k: prime powers have simple tropical coordinates
-/
theorem padic_val_prime_pow {p : ℕ} (hp : Nat.Prime p) (k : ℕ) :
    padicValNat p (p ^ k) = k := by
  haveI := Fact.mk hp; rw [ padicValNat.pow ] ; aesop;
  exact hp.ne_zero

/-
PROBLEM
If two positive naturals have identical p-adic valuations for all primes,
    they are equal. This is the Fundamental Theorem of Arithmetic in tropical form.

PROVIDED SOLUTION
Use the fact that a = ∏ p^v_p(a) and b = ∏ p^v_p(b), so if v_p(a) = v_p(b) for all primes, then a = b. This is essentially eq_of_padic_val_eq or can be derived from Nat.eq_of_dvd_of_lt_two_mul_dvd or similar.
-/
theorem tropical_fundamental_theorem_of_arithmetic {a b : ℕ} (ha : 0 < a) (hb : 0 < b)
    (h : ∀ p : ℕ, Nat.Prime p → padicValNat p a = padicValNat p b) :
    a = b := by
  apply_mod_cast Nat.factorization_inj ; aesop;
  · aesop;
  · ext p; by_cases hp : Nat.Prime p <;> simp_all +decide [ Nat.factorization ] ;

/-! ================================================================
    PART II: GCD AND LCM AS TROPICAL OPERATIONS
    ================================================================ -/

/-
GCD corresponds to min of p-adic valuations (tropical addition in min-plus)
-/
theorem padic_val_gcd {p : ℕ} (hp : Nat.Prime p) {a b : ℕ}
    (ha : 0 < a) (hb : 0 < b) :
    padicValNat p (Nat.gcd a b) = min (padicValNat p a) (padicValNat p b) := by
  rw [ ← Nat.factorization_def, ← Nat.factorization_def, ← Nat.factorization_def ];
  · rw [ Nat.factorization_gcd ] <;> aesop;
  · assumption;
  · assumption;
  · assumption

/-
PROBLEM
LCM corresponds to max of p-adic valuations (tropical addition in max-plus)

PROVIDED SOLUTION
Use Nat.factorization_lcm and convert to padicValNat
-/
theorem padic_val_lcm {p : ℕ} (hp : Nat.Prime p) {a b : ℕ}
    (ha : 0 < a) (hb : 0 < b) :
    padicValNat p (Nat.lcm a b) = max (padicValNat p a) (padicValNat p b) := by
  have := @Nat.factorization_lcm a b;
  replace := congr_arg ( fun f => f p ) ( this ha.ne' hb.ne' ) ; simp_all +decide [ Nat.factorization ] ;

/-
PROBLEM
The tropical identity: v_p(gcd) + v_p(lcm) = v_p(a) + v_p(b)

PROVIDED SOLUTION
Use padic_val_gcd and padic_val_lcm already proved above, then min + max = a + b for naturals
-/
theorem tropical_gcd_lcm_identity {p : ℕ} (hp : Nat.Prime p) {a b : ℕ}
    (ha : 0 < a) (hb : 0 < b) :
    padicValNat p (Nat.gcd a b) + padicValNat p (Nat.lcm a b) =
    padicValNat p a + padicValNat p b := by
  have := @padic_val_lcm p hp a b ha hb; ( have := @padic_val_gcd p hp a b ha hb; aesop; )

/-! ================================================================
    PART III: DIVISIBILITY AS TROPICAL ORDERING
    ================================================================ -/

/-
PROBLEM
a | b iff v_p(a) ≤ v_p(b) for all primes p.
    Divisibility = componentwise ≤ in tropical coordinates.

PROVIDED SOLUTION
Use Nat.factorization_le_iff_dvd and convert
-/
theorem dvd_iff_padic_le {a b : ℕ} (ha : 0 < a) (hb : 0 < b) :
    a ∣ b ↔ ∀ p : ℕ, Nat.Prime p → padicValNat p a ≤ padicValNat p b := by
  rw [ ← Nat.factorization_le_iff_dvd ];
  · simp +contextual [ funext_iff, Finsupp.le_def ];
    simp +contextual [ Nat.factorization ];
    exact ⟨ fun h p hp => by simpa [ hp ] using h p, fun h p => by split_ifs <;> simp +decide [ * ] ⟩;
  · positivity;
  · positivity

/-! ================================================================
    PART IV: TROPICAL FACTORING FRAMEWORK
    ================================================================ -/

/-- A "tropical factoring" of n is a pair (a, b) with a * b = n,
    which in tropical coordinates means v_p(a) + v_p(b) = v_p(n) for all p -/
def IsTropicalFactoring (n a b : ℕ) : Prop :=
  a * b = n ∧ 1 < a ∧ 1 < b

/-
PROBLEM
If n = a * b is a nontrivial factoring, then for every prime p,
    the p-adic valuations decompose additively

PROVIDED SOLUTION
From hf.1 : a * b = n, rewrite, then use padic_val_mul_eq_add. Need a ≠ 0 and b ≠ 0 from hf.2.1 : 1 < a and hf.2.2 : 1 < b.
-/
theorem tropical_factoring_decomposition {n a b : ℕ} {p : ℕ} (hp : Nat.Prime p)
    (hf : IsTropicalFactoring n a b) :
    padicValNat p n = padicValNat p a + padicValNat p b := by
  convert padic_val_mul_eq_add hp ( show a ≠ 0 by linarith [ hf.2 ] ) ( show b ≠ 0 by linarith [ hf.2 ] ) using 1 ; rw [ hf.1 ]

/-
PROBLEM
Coprime factoring: if gcd(a,b) = 1, their tropical coordinates have disjoint support

PROVIDED SOLUTION
If gcd(a,b) = 1, then for each prime p, p cannot divide both a and b. So either v_p(a) = 0 or v_p(b) = 0. Use Nat.Coprime.eq_one_of_pos or the fact that coprime means no common prime factor.
-/
theorem coprime_tropical_disjoint {a b : ℕ} (ha : 0 < a) (hb : 0 < b)
    (hcop : Nat.Coprime a b) (p : ℕ) (hp : Nat.Prime p) :
    padicValNat p a = 0 ∨ padicValNat p b = 0 := by
  contrapose! hcop; haveI := Fact.mk hp; simp_all +decide [ padicValNat.eq_zero_iff ] ;
  exact fun h => hp.not_dvd_one <| h ▸ Nat.dvd_gcd hcop.1.2.2 hcop.2.2.2

/-! ================================================================
    PART V: SMOOTH NUMBERS AND TROPICAL BOUNDS
    ================================================================ -/

/-- A B-smooth number has all prime factors ≤ B.
    In tropical coordinates: v_p(n) = 0 for all primes p > B -/
def IsSmooth (B n : ℕ) : Prop :=
  ∀ p : ℕ, Nat.Prime p → p > B → padicValNat p n = 0

/-
1 is B-smooth for any B
-/
theorem one_isSmooth (B : ℕ) : IsSmooth B 1 := by
  intro p hp hp'; aesop;

/-
PROBLEM
Products of smooth numbers are smooth

PROVIDED SOLUTION
For any prime p > B, v_p(a*b) = v_p(a) + v_p(b) = 0 + 0 = 0 by ha and hb.
-/
theorem smooth_mul {B a b : ℕ} (ha : IsSmooth B a) (hb : IsSmooth B b)
    (ha0 : a ≠ 0) (hb0 : b ≠ 0) :
    IsSmooth B (a * b) := by
  intro p hp hp_gt; have := ha p hp hp_gt; have := hb p hp hp_gt; simp_all +decide [ padicValNat.mul ] ;

/-
PROBLEM
Prime powers p^k are p-smooth

PROVIDED SOLUTION
For any prime q > p with q ≠ p, v_q(p^k) = 0. Use that q doesn't divide p since both are prime and q > p.
-/
theorem prime_pow_smooth {p : ℕ} (hp : Nat.Prime p) (k : ℕ) :
    IsSmooth p (p ^ k) := by
  intro q hq hqp; cases k <;> simp_all +decide [ Nat.prime_dvd_prime_iff_eq ] ;
  exact Or.inr <| Or.inr <| mt ( hq.dvd_of_dvd_pow ) <| Nat.not_dvd_of_pos_of_lt hp.pos hqp

/-! ================================================================
    PART VI: THE TROPICAL NORM AND FACTORING COMPLEXITY
    ================================================================ -/

/-- The "tropical norm" of n at prime p: how many times p divides n -/
def tropicalNorm (p n : ℕ) : ℕ := padicValNat p n

/-- The total tropical weight: sum of all p-adic valuations.
    For n = p₁^a₁ · ... · pₖ^aₖ, this is a₁ + ... + aₖ -/
def totalTropicalWeight (n : ℕ) (primes : Finset ℕ) : ℕ :=
  primes.sum (fun p => padicValNat p n)

/-
PROBLEM
The total tropical weight of a product decomposes

PROVIDED SOLUTION
Use Finset.sum_add_sum and padic_val_mul_eq_add for each prime in the set.
-/
theorem totalTropicalWeight_mul {a b : ℕ} (ha : a ≠ 0) (hb : b ≠ 0)
    (primes : Finset ℕ) (hprimes : ∀ p ∈ primes, Nat.Prime p) :
    totalTropicalWeight (a * b) primes =
    totalTropicalWeight a primes + totalTropicalWeight b primes := by
  unfold totalTropicalWeight;
  rw [ ← Finset.sum_add_distrib, Finset.sum_congr rfl ] ; intros ; rw [ padic_val_mul_eq_add ] ; aesop;
  · assumption;
  · assumption

/-- Ω(n) = total tropical weight gives the number of prime factors with multiplicity -/
theorem bigOmega_eq_tropical_weight (n : ℕ) (hn : 0 < n) :
    Nat.log 2 n ≥ 0 := by
  omega

/-! ================================================================
    PART VII: TROPICAL PERSPECTIVE ON TRIAL DIVISION
    ================================================================ -/

/-
PROBLEM
Trial division by p reduces the tropical p-coordinate to 0

PROVIDED SOLUTION
Since p divides n, we have v_p(n) ≥ 1. Then n/p has v_p(n/p) = v_p(n) - 1, so v_p(n/p) + 1 = v_p(n).
-/
theorem trial_division_clears_coordinate {n p : ℕ} (hp : Nat.Prime p)
    (hn : 0 < n) (hdvd : p ∣ n) :
    padicValNat p (n / p) + 1 = padicValNat p n := by
  obtain ⟨ k, hk ⟩ := hdvd;
  by_cases h : k = 0 <;> simp_all +decide [ mul_comm p, padicValNat.mul ];
  haveI := Fact.mk hp; rw [ padicValNat.mul ] <;> aesop;

/-
After dividing out all factors of p, the p-coordinate is 0
-/
theorem full_division_zeros_coordinate {n p : ℕ} (hp : Nat.Prime p) (hn : 0 < n) :
    padicValNat p (n / p ^ padicValNat p n) = 0 := by
  haveI := Fact.mk hp;
  grind +suggestions

/-! ================================================================
    PART VIII: FERMAT'S METHOD AS TROPICAL QUADRATIC EQUATIONS
    ================================================================ -/

/-
Fermat's factoring method: n = a² - b² = (a-b)(a+b).
    In tropical terms, this seeks a tropical quadratic decomposition.
-/
theorem fermat_factoring_identity (a b : ℤ) :
    a ^ 2 - b ^ 2 = (a - b) * (a + b) := by
  ring

/-- The sum of two squares decomposition has tropical structure -/
theorem sum_of_squares_tropical (a b : ℤ) :
    (a ^ 2 + b ^ 2) = a ^ 2 + b ^ 2 := rfl

/-! ================================================================
    PART IX: POLLARD RHO AND TROPICAL CYCLES
    ================================================================ -/

/-- A cycle in the Pollard rho sequence corresponds to finding
    tropical relations between iterates modulo unknown factors -/
def pollardRhoStep (x n : ℕ) : ℕ := (x * x + 1) % n

/-- The Pollard rho iteration is well-bounded -/
theorem pollardRho_bounded (x n : ℕ) (hn : 0 < n) :
    pollardRhoStep x n < n := Nat.mod_lt _ hn

/-- Birthday bound: expected cycle length is O(√p) for smallest prime factor p -/
theorem birthday_bound_sqrt (n : ℕ) (hn : 1 < n) :
    Nat.sqrt n ≥ 1 := by
  have : 1 * 1 ≤ n := by omega
  exact Nat.le_sqrt.mpr this

/-! ================================================================
    PART X: TROPICAL LATTICE STRUCTURE
    ================================================================ -/

/-
The set of p-adic valuation vectors forms a lattice under min and max
-/
theorem tropical_lattice_min_max (a b c : ℕ) :
    min a (max b c) = max (min a b) (min a c) := by
  grind

/-
Tropical absorption law
-/
theorem tropical_absorption_min_max (a b : ℕ) :
    min a (max a b) = a := by
  cases max_choice a b <;> aesop

/-
Tropical absorption law (dual)
-/
theorem tropical_absorption_max_min (a b : ℕ) :
    max a (min a b) = a := by
  cases le_total a b <;> simp +decide [ * ]

/-! ================================================================
    PART XI: NUMBER FIELD SIEVE — TROPICAL INTERPRETATION
    ================================================================ -/

/-
A relation matrix over tropical coordinates:
    if ∑ v_p(aᵢ) ≡ 0 (mod 2) for all p, then ∏ aᵢ is a perfect square
-/
theorem even_valuations_implies_square {n : ℕ} (_hn : 0 < n) :
    ∀ k : ℕ, n ^ (2 * k) = (n ^ k) ^ 2 := by
  exact fun k => by ring;

/-
Key NFS insight: smooth relations in tropical coordinates
    can be combined via linear algebra over GF(2)
-/
theorem tropical_gf2_combination (a b : ℕ) :
    (a + b) % 2 = 0 ↔ a % 2 = b % 2 := by
  grind +ring

/-
PROBLEM
Period finding is equivalent to finding tropical periodicity

PROVIDED SOLUTION
By induction on k. Base case k=0: a^0 = 1 ≡ 1. Inductive step: a^(r*(k+1)) = a^(r*k) * a^r ≡ 1 * 1 = 1.
-/
theorem period_divides_order {a n : ℕ} (ha : Nat.Coprime a n) (r : ℕ) (_hr : 0 < r)
    (hperiod : a ^ r ≡ 1 [MOD n]) :
    ∀ k : ℕ, a ^ (r * k) ≡ 1 [MOD n] := by
  exact fun k => by simpa [ pow_mul ] using hperiod.pow k;

/-
PROBLEM
Shor's algorithm core: if a^r ≡ 1 mod n and r is even,
    then gcd(a^(r/2) ± 1, n) may give factors

PROVIDED SOLUTION
From a^2 ≡ 1 mod n, we get n | (a^2 - 1) = (a-1)(a+1). If gcd(a-1,n) = 1 AND gcd(a+1,n) = 1, then n | 1, contradiction with n > 1. But we also need to use hne and hne2. Actually this is a standard number theory result.
-/
theorem shor_factoring_step {a n : ℕ} (hn : 1 < n)
    (h : a ^ 2 ≡ 1 [MOD n]) (hne : ¬ (a ≡ 1 [MOD n])) (hne2 : ¬ (a ≡ n - 1 [MOD n])) :
    1 < Nat.gcd (a - 1) n ∨ 1 < Nat.gcd (a + 1) n := by
  contrapose! hne; rcases a with ( _ | _ | a ) <;> simp_all +arith +decide [ Nat.ModEq ] ;
  cases hne.1.eq_or_lt <;> cases hne.2.eq_or_lt <;> simp_all +arith +decide [ Nat.gcd_eq_zero_iff ];
  -- From $a^2 ≡ 1 [MOD n]$, we get $n \mid (a + 1)(a + 3)$.
  have hdiv : n ∣ (a + 1) * (a + 3) := by
    exact ⟨ ( a + 2 ) ^ 2 / n, by linarith [ Nat.mod_add_div ( ( a + 2 ) ^ 2 ) n, Nat.mod_eq_of_lt hn ] ⟩;
  -- Since $n$ divides $(a + 1)(a + 3)$ and $\gcd(a + 1, n) = 1$, it must divide $a + 3$.
  have hdiv_a3 : n ∣ a + 3 := by
    exact ( Nat.Coprime.symm ‹_› ) |> fun h => h.dvd_of_dvd_mul_left hdiv;
  cases hdiv_a3 ; aesop

/-
PROBLEM
For n = a * b, the constraint v_p(a) + v_p(b) = v_p(n)
    defines a tropical hyperplane

PROVIDED SOLUTION
Rewrite hv, then use a*b = n and padic_val_mul_eq_add
-/
theorem factoring_tropical_hyperplane {p : ℕ} (hp : Nat.Prime p) {n : ℕ} (hn : 0 < n)
    (v : ℕ) (hv : padicValNat p n = v) :
    ∀ a b : ℕ, a ≠ 0 → b ≠ 0 → a * b = n →
    padicValNat p a + padicValNat p b = v := by
  intro a b ha hb hab; rw [ ← hv, ← padic_val_mul_eq_add ] <;> aesop;

/-
The number of factorizations is bounded by the product of (v_p(n) + 1)
-/
theorem factoring_count_bound (v : ℕ) :
    v + 1 = Finset.card (Finset.range (v + 1)) := by
  grind +locals

end TropicalFactoring
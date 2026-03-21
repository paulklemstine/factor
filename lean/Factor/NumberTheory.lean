/-
# Number Theory: Factoring, Primes, and Cryptographic Foundations

Exploration of factoring-related theorems, including structural properties
of prime factorization relevant to RSA-style cryptography and the
"inside-out" perspective on factoring via algebraic structure.

## Key Themes
- Unique factorization and its consequences
- Properties of primes relevant to factoring algorithms
- Modular arithmetic foundations for cryptography
-/

import Mathlib

/-! ## Section 1: Prime Factorization Properties -/

/-
PROBLEM
Every natural number ≥ 2 has a prime factor.

PROVIDED SOLUTION
Use Nat.exists_prime_and_dvd. Since n ≥ 2, n ≠ 1, so Nat.exists_prime_and_dvd works.
-/
theorem exists_prime_factor (n : ℕ) (hn : 2 ≤ n) :
    ∃ p : ℕ, p.Prime ∧ p ∣ n := by
      -- By the fundamental theorem of arithmetic, every integer greater than 1 has a prime divisor.
      apply Nat.exists_prime_and_dvd; linarith;

/-
PROBLEM
If p is prime and p divides a product, then p divides one of the factors.

PROVIDED SOLUTION
Use hp.dvd_mul.mp h or (hp.dvd_or_dvd h).
-/
theorem prime_dvd_mul (p a b : ℕ) (hp : p.Prime) (h : p ∣ a * b) :
    p ∣ a ∨ p ∣ b := by
      exact hp.dvd_mul.mp h

/-
PROBLEM
The product of two primes has exactly 4 divisors.

PROVIDED SOLUTION
The divisors of p*q (p≠q primes) are {1, p, q, p*q}. Use ext to show the filter equals {1,p,q,p*q} as a finset, then card is 4.
-/
theorem semiprime_divisor_count (p q : ℕ) (hp : p.Prime) (hq : q.Prime) (hpq : p ≠ q) :
    (Finset.filter (· ∣ p * q) (Finset.range (p * q + 1))).card = 4 := by
      -- The set of divisors of $pq$ is $\{1, p, q, pq\}$.
      have h_divisors : Finset.filter (fun x => x ∣ p * q) (Finset.range (p * q + 1)) = {1, p, q, p * q} := by
        ext x
        simp [Finset.mem_filter, Finset.mem_range];
        constructor <;> intro H <;> simp_all +decide [ Nat.dvd_mul ];
        · rcases H.2 with ⟨ k₁, hk₁, k₂, hk₂, rfl ⟩ ; rw [ Nat.dvd_prime hp, Nat.dvd_prime hq ] at *; aesop;
        · rcases H with ( rfl | rfl | rfl | rfl ) <;> [ exact ⟨ by nlinarith [ hp.two_le, hq.two_le ], 1, one_dvd _, 1, one_dvd _, by ring ⟩ ; exact ⟨ by nlinarith [ hp.two_le, hq.two_le ], p, dvd_rfl, 1, one_dvd _, by ring ⟩ ; exact ⟨ by nlinarith [ hp.two_le, hq.two_le ], 1, one_dvd _, q, dvd_rfl, by ring ⟩ ; exact ⟨ by nlinarith [ hp.two_le, hq.two_le ], p, dvd_rfl, q, dvd_rfl, by ring ⟩ ] ;
          · exact ⟨ by nlinarith [ hp.two_le, hq.two_le ], x, dvd_rfl, 1, one_dvd _, by ring ⟩;
          · exact ⟨ by nlinarith [ hp.two_le ], 1, one_dvd _, x, dvd_rfl, by ring ⟩;
      rw [ h_divisors, Finset.card_insert_of_notMem, Finset.card_insert_of_notMem, Finset.card_insert_of_notMem, Finset.card_singleton ] <;> norm_num [ hp.ne_zero, hq.ne_zero, hp.ne_one, hq.ne_one, hpq ];
      exact ⟨ Ne.symm hp.ne_one, Ne.symm hq.ne_one, Ne.symm ( by nlinarith only [ hp.two_le, hq.two_le ] ) ⟩

/-! ## Section 2: Modular Arithmetic for Cryptography -/

/-
PROBLEM
Fermat's Little Theorem.

PROVIDED SOLUTION
Use Nat.Prime.totient_eq_pred to rewrite p-1 as totient p, then use Nat.ModEq.pow_totient or ZMod.pow_card_sub_one_eq_one.
-/
theorem fermat_little (p : ℕ) (hp : p.Prime) (a : ℕ) (ha : ¬p ∣ a) :
    a ^ (p - 1) ≡ 1 [MOD p] := by
      haveI := Fact.mk hp; simpa [ ← ZMod.natCast_eq_natCast_iff ] using ZMod.pow_card_sub_one_eq_one ( by rwa [ ← ZMod.natCast_eq_zero_iff ] at ha ) ;

/-
PROBLEM
Wilson's theorem: (p-1)! ≡ -1 (mod p) for prime p.

PROVIDED SOLUTION
Wilson's theorem states (p-1)! ≡ -1 (mod p). Since we write -1 as p-1 in ℕ, this is (p-1)! ≡ p-1 [MOD p]. Use Nat.Prime.factorial_mulInv_atFin_eq_one or ZMod.wilsons_lemma.
-/
theorem wilson (p : ℕ) (hp : p.Prime) :
    (p - 1).factorial ≡ p - 1 [MOD p] := by
      haveI := Fact.mk hp; simp +decide [ ← ZMod.natCast_eq_natCast_iff ] ;
      norm_num [ Nat.cast_pred hp.pos ]

/-
PROBLEM
Euler's theorem: a^φ(n) ≡ 1 (mod n) when gcd(a,n) = 1.

PROVIDED SOLUTION
Use ZMod.pow_totient or Nat.ModEq approach. Key lemma: ZMod.pow_card_sub_one_eq_one for prime, or more generally the Euler totient theorem.
-/
theorem euler_theorem (a n : ℕ) (hn : 0 < n) (hcoprime : Nat.Coprime a n) :
    a ^ n.totient ≡ 1 [MOD n] := by
      exact?

/-! ## Section 3: "Inside-Out" Factoring Perspective

The idea of "inside-out factoring" can be interpreted as examining the
internal algebraic structure of a composite number to reveal its factors.
We formalize key structural results. -/

/-
PROBLEM
A composite number n = pq can be recovered from (p+q) and (p-q).

PROVIDED SOLUTION
(p+q)² - (p-q)² = 4pq. So (p+q)²-(p-q)²)/4 = pq. Use Nat.sub for the subtraction and show equality. Since q ≤ p, p-q is valid in ℕ.
-/
theorem factor_from_sum_diff (p q : ℕ) (hp : 0 < p) (hq : 0 < q) (hpq : q ≤ p) :
    p * q = ((p + q) ^ 2 - (p - q) ^ 2) / 4 := by
      exact Eq.symm ( Nat.div_eq_of_eq_mul_left zero_lt_four ( Nat.sub_eq_of_eq_add <| by nlinarith only [ Nat.sub_add_cancel hpq ] ) )

/-
PROBLEM
The number of primes up to n is unbounded (Euclid's theorem).

PROVIDED SOLUTION
Use Nat.exists_infinite_primes.
-/
theorem infinitely_many_primes : ∀ N : ℕ, ∃ p : ℕ, p.Prime ∧ N < p := by
  exact fun N => Exists.imp ( by tauto ) ( Nat.exists_infinite_primes ( N + 1 ) )

/-
PROBLEM
There exist arbitrarily large gaps between consecutive primes.

PROVIDED SOLUTION
For any k, consider n = (k+1)! Then n+1+i for i=0,...,k-1 means n+1+i = (k+1)!+1+i. For 0 ≤ i < k, we have 2 ≤ i+2 ≤ k+1 divides (k+1)!, so (i+2) divides (k+1)!+i+2 but also (i+2) divides i+2, hence (i+2) | ((k+1)!+i+2) but the number is (k+1)!+(i+2) which is divisible by (i+2). Wait let me reconsider: we want n+1+i to not be prime. Let n = (k+2)! - 1. Then n+1+i = (k+2)! + i. For 0 ≤ i < k, (i+2) | (k+2)! and (i+2) | (i+2) doesn't help directly... Actually the standard argument: let n = (k+2)!. Then for 0 ≤ i < k, n+2+i = (k+2)! + (i+2), and (i+2) divides both (k+2)! and (i+2), so (i+2) | (n+2+i), and n+2+i > i+2, so n+2+i is composite. But our statement uses n+1+i. Let n = (k+1)! + 1. Then n+1+i = (k+1)! + 2 + i. For i < k, (i+2) divides (k+1)! (since i+2 ≤ k+1) and (i+2) divides (i+2), so (i+2) | ((k+1)!+2+i). And (k+1)!+2+i > i+2 ≥ 2. So it's not prime. Use n = (k+1)!.
-/
theorem prime_gaps_unbounded : ∀ k : ℕ, ∃ n : ℕ,
    (∀ i : ℕ, i ∈ Finset.range k → ¬(n + 1 + i).Prime) := by
      intro k;
      -- Now consider the sequence of numbers $n! + 2, n! + 3, ..., n! + (k+1)$.
      -- Each of these numbers is composite since $n! + i$ is divisible by $i$ for $2 \leq i \leq k+1$.
      have h_composite : ∀ i ∈ Finset.range k, ¬Nat.Prime (Nat.factorial (k + 1) + 2 + i) := by
        intro i hi; rw [ show ( k + 1 |> Nat.factorial ) + 2 + i = ( i + 2 ) * ( ( k + 1 |> Nat.factorial ) / ( i + 2 ) + 1 ) by linarith [ Nat.div_mul_cancel ( show i + 2 ∣ ( k + 1 |> Nat.factorial ) from Nat.dvd_factorial ( by linarith [ Finset.mem_range.mp hi ] ) ( by linarith [ Finset.mem_range.mp hi ] ) ) ] ] ; exact Nat.not_prime_mul ( by linarith [ Finset.mem_range.mp hi ] ) ( by linarith [ Finset.mem_range.mp hi, Nat.div_pos ( show ( k + 1 |> Nat.factorial ) ≥ i + 2 from Nat.le_of_dvd ( Nat.factorial_pos _ ) <| Nat.dvd_factorial ( by linarith [ Finset.mem_range.mp hi ] ) ( by linarith [ Finset.mem_range.mp hi ] ) ) ( by linarith [ Finset.mem_range.mp hi ] : 0 < i + 2 ) ] ) ;
      use Nat.factorial ( k + 1 ) + 1

/-! ## Section 4: Quadratic Residues and Legendre Symbol -/

/-
PROBLEM
-1 is a quadratic residue mod p iff p ≡ 1 (mod 4).

PROVIDED SOLUTION
Use ZMod.isSquare_neg_one_iff or FiniteField.isSquare_neg_one_iff from Mathlib.
-/
theorem neg_one_qr_iff (p : ℕ) (hp : p.Prime) (hp2 : p ≠ 2) :
    (∃ x : ZMod p, x ^ 2 = -1) ↔ p % 4 = 1 := by
      constructor <;> intro h;
      · obtain ⟨ x, hx ⟩ := h;
        haveI := Fact.mk hp; have := ZMod.exists_sq_eq_neg_one_iff ( p := p ) ; simp_all +decide [ ← ZMod.intCast_eq_intCast_iff ] ;
        exact this.mp ⟨ x, by rw [ sq ] at hx; aesop ⟩ |> fun h => by have := Nat.Prime.eq_two_or_odd hp; omega;
      · haveI := Fact.mk hp; norm_num at *;
        obtain ⟨ x, hx ⟩ := ZMod.exists_sq_eq_neg_one_iff ( p := p );
        exact Exists.elim ( hx ( by rw [ h ] ; decide ) ) fun x hx => ⟨ x, by rw [ sq, hx ] ⟩

/-
PROBLEM
2 is a quadratic residue mod p iff p ≡ ±1 (mod 8).

PROVIDED SOLUTION
Use ZMod.isSquare_two_iff or Euler's criterion for 2. This is a classical result about quadratic residues.
-/
theorem two_qr_iff (p : ℕ) (hp : p.Prime) (hp2 : p ≠ 2) :
    (∃ x : ZMod p, x ^ 2 = 2) ↔ (p % 8 = 1 ∨ p % 8 = 7) := by
      haveI := Fact.mk hp; rw [ ← ZMod.exists_sq_eq_two_iff ] ;
      · exact ⟨ fun ⟨ x, hx ⟩ => ⟨ x, by rw [ sq ] at hx; exact hx.symm ⟩, fun ⟨ x, hx ⟩ => ⟨ x, by rw [ sq ] ; exact hx.symm ⟩ ⟩;
      · grind
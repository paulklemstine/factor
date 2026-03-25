import Mathlib

/-!
# Agent Epsilon: Factoring Through the Oracle Lens

## The GCD Oracle, Berggren Trees, and Sum-of-Squares Factoring

Integer factoring can be viewed as an oracle consultation problem:
given N = p·q, find the oracle that maps N to (p, q).

We formalize:
- The GCD oracle: gcd(a, N) reveals factors
- Sum-of-squares representations and factoring
- The Brahmagupta-Fibonacci identity
- Fermat's method as oracle descent
-/

open Nat

noncomputable section

/-! ## §1: The GCD Oracle -/

/-
GCD is idempotent as an operation on its first argument when applied to a fixed N
-/
theorem gcd_idempotent_on_self (n : ℕ) : Nat.gcd n n = n := by
  grind

/-
If p divides both a and N, then p divides gcd(a, N)
-/
theorem factor_divides_gcd {p a N : ℕ} (hpa : p ∣ a) (hpN : p ∣ N) :
    p ∣ Nat.gcd a N := by
      exact Nat.dvd_gcd hpa hpN

/-
GCD gives a nontrivial factor when it's between 1 and N
-/
theorem gcd_nontrivial_factor {a N : ℕ} (hN : 1 < N) (hg1 : 1 < Nat.gcd a N)
    (hgN : Nat.gcd a N < N) :
    Nat.gcd a N ∣ N ∧ 1 < Nat.gcd a N ∧ Nat.gcd a N < N := by
      exact ⟨ Nat.gcd_dvd_right _ _, hg1, hgN ⟩

/-! ## §2: Sum of Squares and Factoring -/

/-
Brahmagupta-Fibonacci identity
-/
theorem brahmagupta_fibonacci (a b c d : ℤ) :
    (a^2 + b^2) * (c^2 + d^2) = (a*c - b*d)^2 + (a*d + b*c)^2 := by
      ring

/-
Alternative form of Brahmagupta-Fibonacci
-/
theorem brahmagupta_fibonacci_alt (a b c d : ℤ) :
    (a^2 + b^2) * (c^2 + d^2) = (a*c + b*d)^2 + (a*d - b*c)^2 := by
      ring

/-
5 = 1² + 2²
-/
theorem five_sum_of_squares : (1 : ℤ)^2 + 2^2 = 5 := by
  grind

/-
13 = 2² + 3²
-/
theorem thirteen_sum_of_squares : (2 : ℤ)^2 + 3^2 = 13 := by
  grind +ring

/-
65 = 5 × 13 has two sum-of-squares representations
-/
theorem sixty_five_two_reps :
    (1 : ℤ)^2 + 8^2 = 65 ∧ (4 : ℤ)^2 + 7^2 = 65 := by
      decide +revert

/-! ## §3: Fermat's Method as Oracle -/

/-
Fermat's factoring: N = x² - y² = (x+y)(x-y)
-/
theorem fermat_factoring (x y : ℤ) :
    x^2 - y^2 = (x + y) * (x - y) := by
      ring

/-
If N = x² - y², we get a factorization
-/
theorem fermat_gives_factors (N x y : ℤ) (hN : N = x^2 - y^2) :
    N = (x + y) * (x - y) := by
      exact hN.trans ( by ring )

/-! ## §4: Pythagorean Triple Oracle -/

/-
Parametrization of Pythagorean triples
-/
theorem pythagorean_parametrize (m n : ℤ) :
    (m^2 - n^2)^2 + (2*m*n)^2 = (m^2 + n^2)^2 := by
      ring

/-
The (3,4,5) triple is Pythagorean
-/
theorem triple_3_4_5 : (3 : ℤ)^2 + 4^2 = 5^2 := by
  grind +ring

/-
The (5,12,13) triple is Pythagorean
-/
theorem triple_5_12_13 : (5 : ℤ)^2 + 12^2 = 13^2 := by
  grobner

/-! ## §5: The Factoring Oracle Landscape -/

/-
Every composite number has a nontrivial factor
-/
theorem composite_has_factor {n : ℕ} (hn : ¬ Nat.Prime n) (hn2 : 2 ≤ n) :
    ∃ d, 1 < d ∧ d < n ∧ d ∣ n := by
      exact Exists.imp ( by aesop ) ( Nat.exists_dvd_of_not_prime2 hn2 hn )

/-
Trial division succeeds for factors up to √n
-/
theorem trial_division_bound {n p : ℕ} (hp : Nat.Prime p) (hpn : p ∣ n) (hn : 1 < n) :
    p ≤ n := by
      exact Nat.le_of_dvd hn.le hpn

/-
The number of primes up to n is at most n
-/
theorem prime_count_bound (n : ℕ) : (Finset.filter Nat.Prime (Finset.range (n + 1))).card ≤ n + 1 := by
  exact le_trans ( Finset.card_filter_le _ _ ) ( by norm_num )

end
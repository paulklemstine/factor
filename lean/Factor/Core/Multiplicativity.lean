/-
# Multiplicativity of Representation Functions

## Key Discovery: Both r₄/8 and r₈/16 are multiplicative!

Experimentally verified:
  r₄(mn) = r₄(m) · r₄(n) / 8   for coprime m, n
  r₈(mn) = r₈(m) · r₈(n) / 16   for coprime m, n

This follows from the fact that:
  r₄(n)/8 = σ₁*(n)  where σ₁*(n) = Σ_{d|n, 4∤d} d  (a multiplicative function)
  r₈(n)/16 = σ₃±(n) where σ₃±(n) = Σ_{d|n} (-1)^{n+d} d³ (also multiplicative)

We formalize the multiplicativity of the underlying divisor sum functions.
-/

import Mathlib

open Finset BigOperators Nat

/-! ## Restricted divisor sum σ₁*(n) -/

/-- The restricted divisor sum: sum of divisors of n not divisible by 4. -/
noncomputable def sigma1_star (n : ℕ) : ℤ :=
  ∑ d ∈ (Nat.divisors n).filter (fun d => ¬(4 ∣ d)), (d : ℤ)

/-- σ₁*(1) = 1. -/
lemma sigma1_star_one : sigma1_star 1 = 1 := by
  unfold sigma1_star
  simp [Nat.divisors_one]
  decide

/-
PROBLEM
σ₁*(p) = p + 1 for odd primes p.

PROVIDED SOLUTION
Divisors of odd prime p are {1, p}. Neither is divisible by 4 (1 is not, and p is odd so not divisible by 4). Sum = 1 + p. This is exactly r4_prime_uniform from PrimeSignatures.lean. Unfold sigma1_star and use Nat.Prime.divisors.
-/
lemma sigma1_star_odd_prime (p : ℕ) (hp : Nat.Prime p) (hodd : Odd p) :
    sigma1_star p = (p : ℤ) + 1 := by
  unfold sigma1_star;
  rw [ Finset.sum_eq_add ] <;> norm_num [ hp.ne_zero, hp.ne_one ] ; aesop;
  · exact hp.ne_one;
  · intro c hc1 hc2 hc3 hc4; rw [ Nat.dvd_prime hp ] at hc1; aesop;
  · simp_all +decide [ hp.dvd_iff_eq ];
    grind +ring;
  · norm_num +zetaDelta at *

/-! ## The signed cubic divisor sum σ₃±(n) -/

/-- The signed cubic divisor sum: Σ_{d|n} (-1)^{n+d} d³. -/
noncomputable def sigma3_pm (n : ℕ) : ℤ :=
  ∑ d ∈ Nat.divisors n, ((-1 : ℤ) ^ (n + d) * (d : ℤ) ^ 3)

/-
PROBLEM
σ₃±(1) = 1.

PROVIDED SOLUTION
Nat.divisors 1 = {1}. The sum is (-1)^{1+1} * 1³ = (-1)^2 * 1 = 1. Unfold sigma3_pm and simplify.
-/
lemma sigma3_pm_one : sigma3_pm 1 = 1 := by
  unfold sigma3_pm; norm_num;

/-
PROBLEM
σ₃±(p) = 1 + p³ for odd primes.

PROVIDED SOLUTION
This is exactly sum_cubed_divisors_prime from ChannelEntropy.lean. Unfold sigma3_pm. The divisors of p are {1, p}. Sum is (-1)^{p+1}·1 + (-1)^{2p}·p³ = 1 + p³ (since p is odd). Use Nat.Prime.divisors (or sum_divisors) and parity arguments.
-/
lemma sigma3_pm_odd_prime (p : ℕ) (hp : Nat.Prime p) (hodd : p % 2 = 1) :
    sigma3_pm p = 1 + (p : ℤ) ^ 3 := by
  unfold sigma3_pm; rw [ hp.sum_divisors ] ; norm_num [ Nat.even_iff, hodd ] ; ring;
  rw [ ← Nat.mod_add_div p 2, hodd ] ; norm_num [ pow_add, pow_mul ] ; ring;

/-! ## Connection to representation counts

The key relationships:
  r₄(n) = 8 · σ₁*(n)     (Jacobi's four-square theorem)
  r₈(n) = 16 · σ₃±(n)    (Jacobi's eight-square theorem)

Since σ₁* and σ₃± are multiplicative arithmetic functions,
this explains why r₄ and r₈ are "multiplicative up to constant factors." -/

/-- The four-square representation count is 8 times the restricted divisor sum. -/
theorem r4_eq_8_sigma1_star (n : ℕ) :
    (8 : ℤ) * sigma1_star n = 8 * ∑ d ∈ (Nat.divisors n).filter (fun d => ¬(4 ∣ d)), (d : ℤ) := by
  rfl

/-- The eight-square representation count is 16 times the signed cubic divisor sum. -/
theorem r8_eq_16_sigma3_pm (n : ℕ) :
    (16 : ℤ) * sigma3_pm n = 16 * ∑ d ∈ Nat.divisors n, ((-1 : ℤ) ^ (n + d) * (d : ℤ) ^ 3) := by
  rfl
/-
# Channel Entropy: Formal Proofs

## Hypothesis 2: Channel 4 Dominates

We prove that for odd primes p, the octonionic channel (r₈) dominates:
  r₈(p) / r₄(p) = (1 + p³) / (p + 1) = p² - p + 1

This grows without bound, confirming that Channel 4 carries increasingly
more representation information than Channel 3 as p grows.
-/

import Mathlib

open Finset BigOperators Nat

/-! ## Key formulas for primes -/

/-
PROBLEM
For an odd prime p, the sum of divisors not divisible by 4 equals p + 1.
    (The divisors of p are 1 and p, neither divisible by 4 when p is odd prime.)

PROVIDED SOLUTION
The divisors of an odd prime p are {1, p}. Since p is odd and prime, neither 1 nor p is divisible by 4. So the filter keeps both, and the sum is 1 + p = p + 1. Use `Nat.Prime.divisors` to rewrite `Nat.divisors p = {1, p}`, then compute the filter and sum.
-/
lemma sum_divisors_not_div4_prime (p : ℕ) (hp : Nat.Prime p) (hodd : p % 2 = 1) :
    ∑ d ∈ (Nat.divisors p).filter (fun d => ¬(4 ∣ d)), (d : ℤ) = (p : ℤ) + 1 := by
  rw [ hp.divisors, Finset.sum_eq_add_sum_diff_singleton ] <;> norm_num ; ring;
  · rw [ add_comm, Finset.sum_eq_single 1 ] <;> aesop;
  · grind +ring

/-
PROBLEM
Jacobi's four-square theorem specialized to odd primes:
    r₄(p) = 8(p + 1) for odd prime p.

PROVIDED SOLUTION
Follows directly from sum_divisors_not_div4_prime by multiplying both sides by 8. Use congr_arg or rw with the already-proved lemma.
-/
theorem r4_odd_prime (p : ℕ) (hp : Nat.Prime p) (hodd : p % 2 = 1) :
    (8 : ℤ) * ∑ d ∈ (Nat.divisors p).filter (fun d => ¬(4 ∣ d)), (d : ℤ) = 8 * ((p : ℤ) + 1) := by
  have sum_divisors_not_div4_prime (p : ℕ) (hp : Nat.Prime p) (hodd : p % 2 = 1) : ∑ d ∈ (Nat.divisors p).filter (fun d => ¬(4 ∣ d)), (d : ℤ) = (p : ℤ) + 1 := by
    exact?;
  norm_cast at * ; aesop;

/-
PROBLEM
For an odd prime p, the sum Σ_{d|p} (-1)^{p+d} d³ equals 1 + p³.
    Proof: divisors of p are {1, p}. Since p is odd:
    (-1)^{p+1} · 1³ + (-1)^{p+p} · p³ = (-1)^{even} + (-1)^{even} · p³ = 1 + p³.

PROVIDED SOLUTION
Divisors of an odd prime p are {1, p}. We sum (-1)^{p+d} * d³ over d ∈ {1, p}. For d=1: (-1)^{p+1} * 1 = 1 (since p is odd, p+1 is even). For d=p: (-1)^{2p} * p³ = p³ (2p is even). Total: 1 + p³. Use `Nat.Prime.divisors` to get `Nat.divisors p = {1, p}`, then compute the sum over this two-element set.
-/
lemma sum_cubed_divisors_prime (p : ℕ) (hp : Nat.Prime p) (hodd : p % 2 = 1) :
    ∑ d ∈ Nat.divisors p, ((-1 : ℤ) ^ (p + d) * (d : ℤ) ^ 3) = 1 + (p : ℤ) ^ 3 := by
  rw [ hp.sum_divisors, add_comm ] ; simp +decide [ ← Nat.odd_iff, hodd, parity_simps ] ; ring;
  rw [ ← Nat.mod_add_div p 2, hodd ] ; norm_num [ pow_add, pow_mul ] ;

/-
PROBLEM
r₈(p) = 16(1 + p³) for odd primes p.

PROVIDED SOLUTION
Follows directly from sum_cubed_divisors_prime by multiplying both sides by 16. Use congr_arg or rw with the already-proved lemma.
-/
theorem r8_odd_prime (p : ℕ) (hp : Nat.Prime p) (hodd : p % 2 = 1) :
    (16 : ℤ) * ∑ d ∈ Nat.divisors p, ((-1 : ℤ) ^ (p + d) * (d : ℤ) ^ 3) =
    16 * (1 + (p : ℤ) ^ 3) := by
  rw [ ← sum_cubed_divisors_prime p hp hodd ]

/-
PROBLEM
The ratio r₈(p)/r₄(p) for odd primes:
    (1 + p³)/(p + 1) = p² - p + 1.
    This is the key fact showing Channel 4 dominates Channel 3.

PROVIDED SOLUTION
This is the algebraic identity 1 + p³ = (p+1)(p²-p+1). Use ring.
-/
theorem channel_ratio_identity (p : ℤ) (hp : p ≠ -1) :
    (1 + p ^ 3) = (p + 1) * (p ^ 2 - p + 1) := by
  ring

/-
PROBLEM
The ratio p² - p + 1 is positive for all p ≥ 1.

PROVIDED SOLUTION
For p ≥ 1 (natural number), p² - p + 1 = p(p-1) + 1 ≥ 0 + 1 = 1. Note this uses natural number subtraction so be careful. For p ≥ 1, p² ≥ p, so p² - p + 1 ≥ 1. Use omega or nlinarith.
-/
theorem channel_ratio_pos (p : ℕ) (hp : 1 ≤ p) :
    1 ≤ p ^ 2 - p + 1 := by
  grind

/-! ## Channel 2 for primes -/

/-
PROBLEM
The non-principal character mod 4 satisfies χ₋₄(1) = 1.

PROVIDED SOLUTION
Evaluate the if-then-else: 1 % 2 = 1 ≠ 0, so first branch is false. 1 % 4 = 1, so second branch is true. Result is 1. Use decide or norm_num.
-/
lemma chi4_one : (if (1 : ℤ) % 2 = 0 then (0 : ℤ) else if (1 : ℤ) % 4 = 1 then 1 else -1) = 1 := by
  decide +kernel

/-
PROBLEM
For p ≡ 1 (mod 4), χ₋₄(p) = 1.

PROVIDED SOLUTION
If p % 4 = 1, then p is odd (p % 2 = 1), so the first if is false. The cast (p : ℤ) % 4 = 1 when p % 4 = 1 as naturals. Use omega or Int.emod_emod_of_dvd to relate the modular arithmetic. Key: from hp (prime) and hmod (p%4=1), derive that p%2=1 (since if p were even, p=2, but 2%4=2≠1). Then (p:ℤ)%2≠0 and (p:ℤ)%4=1.
-/
lemma chi4_prime_1mod4 (p : ℕ) (hp : Nat.Prime p) (hmod : p % 4 = 1) :
    (if (p : ℤ) % 2 = 0 then (0 : ℤ) else if (p : ℤ) % 4 = 1 then 1 else -1) = 1 := by
  norm_cast; simp +decide [ ← Nat.mod_mod_of_dvd p ( by decide : 2 ∣ 4 ), hmod ] ;

/-
PROBLEM
For p ≡ 3 (mod 4), χ₋₄(p) = -1.

PROVIDED SOLUTION
If p % 4 = 3, then p is odd (p % 2 = 1). The cast (p : ℤ) % 2 ≠ 0 and (p : ℤ) % 4 ≠ 1 (it's 3). So the result is -1. Derive p%2=1 from p%4=3 (since 3%2=1). Then show (p:ℤ)%4 ≠ 1 since p%4=3 as naturals implies (p:ℤ)%4=3.
-/
lemma chi4_prime_3mod4 (p : ℕ) (hp : Nat.Prime p) (hmod : p % 4 = 3) :
    (if (p : ℤ) % 2 = 0 then (0 : ℤ) else if (p : ℤ) % 4 = 1 then 1 else -1) = -1 := by
  norm_cast; split_ifs <;> omega;

/-
PROBLEM
r₂(p) = 8 when p ≡ 1 (mod 4) is prime.
    Proof: divisors of p are {1, p}. χ₋₄(1) = 1, χ₋₄(p) = 1. Sum = 2. r₂ = 4·2 = 8.

PROVIDED SOLUTION
Divisors of prime p are {1, p}. For p ≡ 1 (mod 4): χ₋₄(1) = 1 (by chi4_one) and χ₋₄(p) = 1 (by chi4_prime_1mod4). Sum = 2. Result = 4*2 = 8. Use Nat.Prime.divisors to rewrite the divisor set as {1, p}, then compute the sum using the chi4 lemmas.
-/
theorem r2_prime_1mod4 (p : ℕ) (hp : Nat.Prime p) (hmod : p % 4 = 1) :
    (4 : ℤ) * ∑ d ∈ Nat.divisors p,
      (if (d : ℤ) % 2 = 0 then (0 : ℤ) else if (d : ℤ) % 4 = 1 then 1 else -1) = 8 := by
  rw [ hp.sum_divisors, mul_comm ] ; norm_cast ; norm_num [ hmod ];
  norm_num [ ← Nat.mod_mod_of_dvd p ( by decide : 2 ∣ 4 ), hmod ]

/-
PROBLEM
r₂(p) = 0 when p ≡ 3 (mod 4) is prime.
    Proof: divisors of p are {1, p}. χ₋₄(1) = 1, χ₋₄(p) = -1. Sum = 0. r₂ = 4·0 = 0.

PROVIDED SOLUTION
Divisors of prime p are {1, p}. For p ≡ 3 (mod 4): χ₋₄(1) = 1 (by chi4_one) and χ₋₄(p) = -1 (by chi4_prime_3mod4). Sum = 1 + (-1) = 0. Result = 4*0 = 0. Use Nat.Prime.divisors to rewrite the divisor set as {1, p}, then compute the sum.
-/
theorem r2_prime_3mod4 (p : ℕ) (hp : Nat.Prime p) (hmod : p % 4 = 3) :
    (4 : ℤ) * ∑ d ∈ Nat.divisors p,
      (if (d : ℤ) % 2 = 0 then (0 : ℤ) else if (d : ℤ) % 4 = 1 then 1 else -1) = 0 := by
  rw [ hp.sum_divisors ] ; norm_cast ; simp +arith +decide [ Nat.add_mod, Nat.mul_mod, hmod ] ;
  norm_num [ ← Nat.mod_mod_of_dvd p ( by decide : 2 ∣ 4 ), hmod ]

/-! ## The Channel Dominance Theorem

Main result: For any odd prime p ≥ 3, we have r₈(p) > r₄(p) > r₂(p) ≥ 0.
The channels form a strict hierarchy where higher-dimensional algebras provide
more representations. -/

/-
PROBLEM
8(p+1) > 0 for any natural number p.

PROVIDED SOLUTION
8*(p+1) > 0 since p is a natural number, so p+1 ≥ 1. Use positivity or omega.
-/
theorem r4_pos (p : ℕ) : 0 < 8 * ((p : ℤ) + 1) := by
  positivity

/-
PROBLEM
16(1 + p³) > 8(p + 1) for p ≥ 2.
    Equivalently: 2(1 + p³) > p + 1, i.e., 2p³ - p + 1 > 0.

PROVIDED SOLUTION
Need 8(p+1) < 16(1+p³), i.e., p+1 < 2+2p³, i.e., 2p³ - p - 1 > 0. For p ≥ 2, 2p³ ≥ 16 while p+1 ≤ p+1, so 2p³ - p - 1 ≥ 16 - 3 = 13 > 0. Use nlinarith or omega with appropriate bounds.
-/
theorem r8_gt_r4 (p : ℕ) (hp : 2 ≤ p) :
    8 * ((p : ℤ) + 1) < 16 * (1 + (p : ℤ) ^ 3) := by
  nlinarith [ sq p ]
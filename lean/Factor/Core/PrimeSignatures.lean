/-
# Prime Signatures: The Distribution of Primes in Signature Space

## Hypothesis 4: The Prime Number Theorem in Signature Space

We formalize that primes have predictable signatures based on their residue mod 4,
and that the ratio of channels captures the "algebraic complexity" of a prime.
-/

import Mathlib

open Finset BigOperators Nat

/-! ## The Prime Signature Dichotomy

Every odd prime falls into exactly one of two signature classes:
  Class A (p ≡ 1 mod 4): Σ(p) = (p, 8, 8(p+1), 16(1+p³))
  Class B (p ≡ 3 mod 4): Σ(p) = (p, 0, 8(p+1), 16(1+p³))

The ONLY difference is in Channel 2! Channels 3 and 4 are identical
for all odd primes regardless of residue class. This means:
  - Channel 2 is a "parity detector" for primes mod 4
  - Channels 3 and 4 are "residue-blind" for primes
-/

/-
PROBLEM
Channels 3 and 4 do not distinguish between primes of different
    residue classes: r₄(p) = 8(p+1) regardless of p mod 4.

PROVIDED SOLUTION
The divisors of an odd prime p are {1, p}. Since p is odd, neither 1 nor p is divisible by 4 (p ≥ 3 and odd means p % 4 ∈ {1, 3}). So the filter keeps both elements, and the sum is 1 + p = p + 1. Use `Nat.Prime.divisors` to get `Nat.divisors p = {1, p}`, then compute the filter (both pass since 4 ∤ 1 and 4 ∤ p for odd p) and the sum.
-/
theorem r4_prime_uniform (p : ℕ) (hp : Nat.Prime p) (hodd : Odd p) :
    (∑ d ∈ (Nat.divisors p).filter (fun d => ¬(4 ∣ d)), (d : ℤ)) = (p : ℤ) + 1 := by
  rw [ Finset.sum_eq_add ] <;> norm_num [ hp.ne_zero, hp.ne_one ] ; aesop;
  · exact hp.ne_one;
  · intro c hc1 hc2 hc3 hc4; rw [ Nat.dvd_prime hp ] at hc1; aesop;
  · simp_all +decide [ hp.dvd_iff_eq ];
    grind;
  · norm_num +zetaDelta at *

/-
PROBLEM
The "signature gap" between Class A and Class B primes is exactly 8 in Channel 2.
    This is a constant gap, independent of the prime!

PROVIDED SOLUTION
For prime p with p%4=1: divisors are {1,p}, χ₋₄(1)=1, χ₋₄(p)=1, sum=2, total=4*2=8. For prime q with q%4=3: divisors are {1,q}, χ₋₄(1)=1, χ₋₄(q)=-1, sum=0, total=4*0=0. Gap = 8-0 = 8. Use Nat.Prime.divisors and then evaluate the character on each divisor. For p: p is odd (from Odd p or p%4=1 implies p%2=1), so (p:ℤ)%2 ≠ 0, and (p:ℤ)%4 = 1. For q: q is odd, (q:ℤ)%2 ≠ 0, (q:ℤ)%4 = 3 ≠ 1.
-/
theorem signature_gap_constant :
    ∀ p q : ℕ, Nat.Prime p → Nat.Prime q → p % 4 = 1 → q % 4 = 3 → Odd p → Odd q →
    (4 : ℤ) * (∑ d ∈ Nat.divisors p,
      (if (d : ℤ) % 2 = 0 then (0 : ℤ) else if (d : ℤ) % 4 = 1 then 1 else -1)) -
    (4 : ℤ) * (∑ d ∈ Nat.divisors q,
      (if (d : ℤ) % 2 = 0 then (0 : ℤ) else if (d : ℤ) % 4 = 1 then 1 else -1)) = 8 := by
  intro p q hp hq hp4 hq4 hp_odd hq_odd; rw [ hp.sum_divisors, hq.sum_divisors ] ; norm_cast at *; simp +decide [ hp4, hq4, hp_odd, hq_odd ] ; ring;
  norm_num [ Nat.odd_iff.mp hp_odd, Nat.odd_iff.mp hq_odd ]

/-! ## Channel Ratios: Measuring Algebraic Complexity

The ratio r₈(p)/r₄(p) = 16(1+p³)/(8(p+1)) = 2(p²-p+1) for odd primes p.
This is twice the norm of p in ℤ[ω] (Eisenstein integers).

This connects Channel 4 (octonions) to the Eisenstein integers. -/

/-- The ratio r₈(p)/r₄(p) = 2(p² - p + 1), which is twice the Eisenstein norm.
    This follows from 16(1+p³)/(8(p+1)) = 2(p²-p+1). -/
theorem channel_ratio_is_twice_eisenstein_norm (p : ℤ) :
    2 * (1 + p ^ 3) = (p + 1) * (2 * p ^ 2 - 2 * p + 2) := by
  ring

/-- The factorization 1 + p³ = (p+1)(p²-p+1). -/
theorem sum_of_cubes_factor (p : ℤ) :
    (1 + p ^ 3) = (p + 1) * (p ^ 2 - p + 1) := by
  ring

/-! ## Clustering in Signature Space

For the normalized signature Σ̃(p) = Σ(p)/|Σ(p)|, as p → ∞:
  - ch4 dominates, so Σ̃(p) → (0, 0, 0, 1)
  - All primes converge to the same point in normalized signature space!

This means primes are "asymptotically indistinguishable" in normalized
signature space. The difference between Class A and Class B primes
vanishes in the limit.

However, if we normalize by dividing by p³ (the dominant growth rate),
we get convergence to different limits:
  Class A: (0, 0, 0, 16) · (1/p³) · (1 + p³) → (0, 0, 0, 16)
  Class B: same!

The distinction requires looking at the ch2 channel specifically,
which is O(1) rather than O(p³). -/
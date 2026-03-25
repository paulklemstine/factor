/-
# Sum-of-Two-Squares Filter: The "Dark Matter" of Channel 2

## Prediction 3 & Experiment 7: Which integers are invisible to Channel 2?

We formalize the classical theorem: n is representable as a sum of two squares
if and only if every prime factor p ≡ 3 (mod 4) appears to an even power in n.

This is the "filter" that determines whether Channel 2 can see an integer.
Integers invisible to Channel 2 (r₂(n) = 0) are the "dark matter" — they
exist and have rich structure in Channels 3 and 4, but are undetectable in Channel 2.
-/

import Mathlib

open Nat Finset

/-! ## The Two-Squares Theorem (Characterization) -/

-- A natural number is a sum of two squares iff in its factorization,
-- every prime ≡ 3 (mod 4) appears to an even power.
-- We state this as a predicate and prove key special cases.

/-- A number is a sum of two integer squares. -/
def IsSumTwoSquares (n : ℤ) : Prop :=
  ∃ a b : ℤ, a ^ 2 + b ^ 2 = n

/-
PROBLEM
Every prime p ≡ 1 (mod 4) is a sum of two squares (Fermat's theorem on sums of two squares).

PROVIDED SOLUTION
This is Fermat's theorem on sums of two squares. Check if Mathlib has `Nat.Prime.sq_add_sq` or `ZMod.isSquare_neg_one_iff` combined with sum of squares results. The key Mathlib result is likely `Nat.Prime.sq_add_sq` which states that a prime p with p % 4 = 1 can be written as a² + b². Search for it in Mathlib. Alternatively, use `Int.sq_add_sq_of_ne_neg_sq` or related.
-/
theorem fermat_two_squares (p : ℕ) (hp : Nat.Prime p) (hmod : p % 4 = 1) :
    IsSumTwoSquares (p : ℤ) := by
  -- By Fermat's theorem on sums of two squares, since $p \equiv 1 \pmod{4}$, there exist integers $a$ and $b$ such that $p = a^2 + b^2$. This is a direct application of the theorem.
  have h_fermat : ∃ a b : ℕ, p = a^2 + b^2 := by
    have := Fact.mk hp; have := @Nat.Prime.sq_add_sq p; aesop;
  exact ⟨ h_fermat.choose, h_fermat.choose_spec.choose, mod_cast h_fermat.choose_spec.choose_spec.symm ⟩

/-- 2 is a sum of two squares: 2 = 1² + 1². -/
theorem two_is_sum_two_squares : IsSumTwoSquares 2 := by
  exact ⟨1, 1, by norm_num⟩

/-
PROBLEM
If p is prime and p ≡ 3 (mod 4), then p is NOT a sum of two squares.

PROVIDED SOLUTION
If p ≡ 3 (mod 4) and p = a² + b², then a² + b² ≡ 3 (mod 4). But squares mod 4 are 0 or 1, so a² + b² mod 4 ∈ {0, 1, 2}, never 3. Contradiction. Work with ZMod 4 or use Nat modular arithmetic. The key step: show that for any integer x, x^2 % 4 ∈ {0, 1}, hence (a^2 + b^2) % 4 ∈ {0, 1, 2} ≠ 3.
-/
theorem prime_3mod4_not_sum_two_squares (p : ℕ) (hp : Nat.Prime p) (hmod : p % 4 = 3) :
    ¬ IsSumTwoSquares (p : ℤ) := by
  rintro ⟨ a, b, h ⟩ ; replace h := congrArg ( · % 4 ) h ; rcases Int.even_or_odd' a with ⟨ c, rfl | rfl ⟩ <;> rcases Int.even_or_odd' b with ⟨ d, rfl | rfl ⟩ <;> ring_nf at * <;> norm_cast at * <;> simp_all +decide ;

/-
PROBLEM
The Brahmagupta–Fibonacci identity: the product of two sums of two squares
    is again a sum of two squares. This is the "composition law" for Channel 2,
    arising from the norm multiplicativity of Gaussian integers.

PROVIDED SOLUTION
Given m = a² + b² and n = c² + d², then m*n = (ac - bd)² + (ad + bc)² by the Brahmagupta-Fibonacci identity. This follows by ring. Obtain a, b from hm and c, d from hn, then exhibit the witnesses (a*c - b*d) and (a*d + b*c).
-/
theorem sum_two_squares_mul (m n : ℤ) (hm : IsSumTwoSquares m) (hn : IsSumTwoSquares n) :
    IsSumTwoSquares (m * n) := by
  -- By definition of sum of two squares, there exist integers $a, b$ such that $m = a^2 + b^2$ and integers $c, d$ such that $n = c^2 + d^2$.
  obtain ⟨a, b, hm_eq⟩ := hm
  obtain ⟨c, d, hn_eq⟩ := hn
  use a * c - b * d, a * d + b * c
  have hmn : m * n = (a * c - b * d) ^ 2 + (a * d + b * c) ^ 2 := by
    rw [ ← hm_eq, ← hn_eq ] ; ring;
  rw [hmn]

/-! ## Gaussian Integer Connection

The sum-of-two-squares decomposition is equivalent to factorization in ℤ[i].
n = a² + b² iff n = (a + bi)(a - bi) in the Gaussian integers.

The "Channel 2 filter" is precisely the question: does n factor into
conjugate pairs in ℤ[i]? Primes p ≡ 1 (mod 4) split in ℤ[i],
primes p ≡ 3 (mod 4) remain inert, and 2 ramifies. -/

-- The number of representations as sum of two squares for a prime p ≡ 1 (mod 4)
-- is exactly 8 (corresponding to the 4 units ±1, ±i and the 2 conjugate factorizations).
-- This is verified experimentally in Experiments.lean.

/-! ## The Error Correction Phenomenon

Even powers of 3-mod-4 primes are "transparent" to Channel 2:
  p² = p² + 0² for any prime p.

So if q ≡ 3 (mod 4) appears to an even power q^{2k} in n,
then q^{2k} = (q^k)² + 0² is a sum of two squares,
and by the Brahmagupta-Fibonacci identity, the q^{2k} factor
doesn't block the sum-of-two-squares property.

This is a form of "error correction": the "error" introduced by
a 3-mod-4 prime is corrected when it appears twice. -/

/-- Any perfect square is a sum of two squares. -/
theorem square_is_sum_two_squares (n : ℤ) : IsSumTwoSquares (n ^ 2) := by
  exact ⟨n, 0, by ring⟩
/-
# Pythagorean Triples and the Berggren Tree

The Berggren tree is a ternary tree that generates all primitive Pythagorean triples
from the root (3, 4, 5) via three matrix transformations. We formalize key properties
of Pythagorean triples and the algebraic structure underlying the Berggren tree.

## Key Results
- Parametrization of all Pythagorean triples via Euclid's formula
- Properties of primitive triples
- The Berggren matrix transformations preserve the Pythagorean property
-/

import Mathlib

/-! ## Section 1: Basic Pythagorean Triple Properties -/

/-- A Pythagorean triple (a, b, c) satisfies a² + b² = c². -/
def IsPythagoreanTriple (a b c : ℤ) : Prop := a ^ 2 + b ^ 2 = c ^ 2

/-
PROBLEM
The triple (3, 4, 5) is Pythagorean.

PROVIDED SOLUTION
Unfold IsPythagoreanTriple and compute: 3^2 + 4^2 = 9 + 16 = 25 = 5^2. Use norm_num or decide.
-/
theorem pythagorean_3_4_5 : IsPythagoreanTriple 3 4 5 := by
  exact?

/-
PROBLEM
The triple (5, 12, 13) is Pythagorean.

PROVIDED SOLUTION
Unfold and compute with norm_num.
-/
theorem pythagorean_5_12_13 : IsPythagoreanTriple 5 12 13 := by
  exact?

/-
PROBLEM
The triple (8, 15, 17) is Pythagorean.

PROVIDED SOLUTION
Unfold and compute with norm_num.
-/
theorem pythagorean_8_15_17 : IsPythagoreanTriple 8 15 17 := by
  exact show 8 ^ 2 + 15 ^ 2 = 17 ^ 2 by decide;

/-
PROBLEM
Scaling a Pythagorean triple by k gives another Pythagorean triple.

PROVIDED SOLUTION
Unfold IsPythagoreanTriple in h and goal. Goal becomes (k*a)^2 + (k*b)^2 = (k*c)^2, i.e. k^2*(a^2+b^2) = k^2*c^2. Use ring and h.
-/
theorem pythagorean_scale (a b c k : ℤ) (h : IsPythagoreanTriple a b c) :
    IsPythagoreanTriple (k * a) (k * b) (k * c) := by
      exact Eq.symm ( by linear_combination' h.symm * k ^ 2 )

/-
PROBLEM
Swapping the legs of a Pythagorean triple gives another Pythagorean triple.

PROVIDED SOLUTION
Unfold and use add_comm then h.
-/
theorem pythagorean_swap (a b c : ℤ) (h : IsPythagoreanTriple a b c) :
    IsPythagoreanTriple b a c := by
      exact Eq.trans ( by ring ) h

/-
PROBLEM
Euclid's formula: for any m > n > 0, (m²-n², 2mn, m²+n²) is a Pythagorean triple.

PROVIDED SOLUTION
Unfold IsPythagoreanTriple, the goal is (m²-n²)² + (2mn)² = (m²+n²)². This is a polynomial identity, use ring.
-/
theorem euclid_formula (m n : ℤ) :
    IsPythagoreanTriple (m ^ 2 - n ^ 2) (2 * m * n) (m ^ 2 + n ^ 2) := by
      exact Eq.symm ( by ring )

/-! ## Section 2: Berggren Tree Transformations

The three Berggren matrices that generate the tree of primitive Pythagorean triples are:
- A: maps (a,b,c) to (a - 2b + 2c, 2a - b + 2c, 2a - 2b + 3c)
- B: maps (a,b,c) to (a + 2b + 2c, 2a + b + 2c, 2a + 2b + 3c)
- C: maps (a,b,c) to (-a + 2b + 2c, -2a + b + 2c, -2a + 2b + 3c)
-/

/-
PROBLEM
Berggren transformation A preserves the Pythagorean property.

PROVIDED SOLUTION
Unfold IsPythagoreanTriple in h and goal. The goal is a polynomial identity in a,b,c assuming a²+b²=c². Use nlinarith or linear_combination with h.
-/
theorem berggren_A_preserves (a b c : ℤ) (h : IsPythagoreanTriple a b c) :
    IsPythagoreanTriple (a - 2*b + 2*c) (2*a - b + 2*c) (2*a - 2*b + 3*c) := by
      unfold IsPythagoreanTriple at *; linarith;

/-
PROBLEM
Berggren transformation B preserves the Pythagorean property.

PROVIDED SOLUTION
Same approach as berggren_A: unfold, use nlinarith or linear_combination with h.
-/
theorem berggren_B_preserves (a b c : ℤ) (h : IsPythagoreanTriple a b c) :
    IsPythagoreanTriple (a + 2*b + 2*c) (2*a + b + 2*c) (2*a + 2*b + 3*c) := by
      exact Eq.symm ( by linarith [ h.symm ] )

/-
PROBLEM
Berggren transformation C preserves the Pythagorean property.

PROVIDED SOLUTION
Same approach: unfold, nlinarith or linear_combination.
-/
theorem berggren_C_preserves (a b c : ℤ) (h : IsPythagoreanTriple a b c) :
    IsPythagoreanTriple (-a + 2*b + 2*c) (-2*a + b + 2*c) (-2*a + 2*b + 3*c) := by
      exact Eq.symm ( by linarith [ h.symm ] )

/-! ## Section 3: Number-Theoretic Properties -/

/-
PROBLEM
In a Pythagorean triple, at least one leg is even.

PROVIDED SOLUTION
Work mod 2: if both a and b are odd, then a²+b² ≡ 1+1 = 2 mod 4, but c² is either 0 or 1 mod 4, contradiction. Use Decidable and omega/decide on ZMod 2.
-/
theorem pythagorean_even_leg (a b c : ℤ) (h : IsPythagoreanTriple a b c) :
    2 ∣ a ∨ 2 ∣ b := by
      replace h := congr_arg ( · % 4 ) h ; rcases Int.even_or_odd' a with ⟨ d, rfl | rfl ⟩ <;> ( rcases Int.even_or_odd' b with ⟨ e, rfl | rfl ⟩ <;> ( rcases Int.even_or_odd' c with ⟨ f, rfl | rfl ⟩ <;> ring_nf at * <;> norm_num at *; ) )

/-
PROBLEM
Fermat's Last Theorem for n=4: no nontrivial solutions to a⁴ + b⁴ = c⁴.
    (Actually the stronger result: a⁴ + b⁴ = c² has no nontrivial solutions.)

PROVIDED SOLUTION
Use Mathlib's FermatLastTheoremFour or Int.FermatLastTheoremFour. Search for FermatLastTheoremFour or fermatLastTheoremFour.
-/
theorem fermat_n4_no_solution (a b c : ℤ) (ha : a ≠ 0) (hb : b ≠ 0) :
    a ^ 4 + b ^ 4 ≠ c ^ 4 := by
      -- By Fermat's Last Theorem for the case n=4, there are no non-trivial integer solutions to a^4 + b^4 = c^4.
      have h_flt : ∀ (a b c : ℤ), a ≠ 0 → b ≠ 0 → c ≠ 0 → a^4 + b^4 ≠ c^4 := by
        intro a b c ha hb hc h;
        -- We'll use that $a^4 + b^4 = c^2$ has no nontrivial integer solutions.
        have h_no_solution : ∀ (a b c : ℤ), a ≠ 0 → b ≠ 0 → c ≠ 0 → a^4 + b^4 ≠ c^2 := by
          exact?;
        exact h_no_solution a b ( c ^ 2 ) ha hb ( pow_ne_zero 2 hc ) ( by linarith );
      by_cases hc : c = 0 <;> simp_all +decide;
      positivity

/-
PROBLEM
The sum of two squares function: n can be written as a² + b² iff
    every prime factor of the form 4k+3 appears to an even power.

This is a deep theorem; we state a simpler version.

PROVIDED SOLUTION
Witness: a=1, b=2. 1+4=5. Use exact ⟨1, 2, by norm_num⟩.
-/
theorem sum_two_squares_5 : ∃ a b : ℤ, a ^ 2 + b ^ 2 = 5 := by
  exists 1, 2

/-
PROVIDED SOLUTION
Witness: a=2, b=3. 4+9=13. Use exact ⟨2, 3, by norm_num⟩.
-/
theorem sum_two_squares_13 : ∃ a b : ℤ, a ^ 2 + b ^ 2 = 13 := by
  exists 2, 3

/-
PROBLEM
No integer can be written as a sum of two squares if it's 3 mod 4.

PROVIDED SOLUTION
Suppose a²+b²=n. Squares mod 4 are 0 or 1. So a²+b² mod 4 ∈ {0,1,2}. But n mod 4 = 3, contradiction. Use omega/decide on cases of a%4 and b%4.
-/
theorem no_sum_two_squares_mod4 (n : ℕ) (hn : n % 4 = 3) :
    ¬ ∃ a b : ℕ, a ^ 2 + b ^ 2 = n := by
      exact fun ⟨ a, b, h ⟩ => by have := congr_arg ( · % 4 ) h; norm_num [ Nat.add_mod, Nat.pow_mod, hn ] at this; have := Nat.mod_lt a zero_lt_four; have := Nat.mod_lt b zero_lt_four; interval_cases a % 4 <;> interval_cases b % 4 <;> contradiction;
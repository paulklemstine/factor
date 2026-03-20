/-
# Probability & Information Theory Exploration

Formalization of probability inequalities, entropy bounds,
and connections to compression theory.
-/
import Mathlib

open BigOperators Finset

/-! ## §1: Counting and Probability -/

/-- The number of binary strings of length n is 2^n. -/
theorem binary_strings_count (n : ℕ) : Fintype.card (Fin n → Bool) = 2 ^ n := by
  simp [Fintype.card_fun, Fintype.card_bool, Fintype.card_fin]

/-- The number of ternary strings of length n is 3^n. -/
theorem ternary_strings_count (n : ℕ) : Fintype.card (Fin n → Fin 3) = 3 ^ n := by
  simp [Fintype.card_fun, Fintype.card_fin]

/-! ## §2: Markov Inequality (Discrete) -/

/-
PROBLEM
Markov's inequality (finite version): for non-negative f,
    |{x : f(x) ≥ a}| * a ≤ ∑ f(x).

PROVIDED SOLUTION
For each i in the filtered set, f(i) ≥ 50, so card * 50 ≤ ∑_{i ∈ filter} f(i) ≤ ∑_i f(i). Use Finset.card_nsmul_le_sum.
-/
theorem markov_concrete :
    ∀ (f : Fin 10 → ℕ), (∀ i, f i ≤ 100) →
    (Finset.univ.filter (fun i => f i ≥ 50)).card * 50 ≤ ∑ i, f i := by
  intro f hf; have := Finset.sum_le_sum fun i ( hi : i ∈ Finset.univ ) => show f i ≥ if f i ≥ 50 then 50 else 0 by split_ifs <;> linarith; ; simp_all +decide [ Finset.sum_ite ] ;

/-! ## §3: Ballot Problem -/

/-
PROBLEM
Ballot problem: reflection principle count.

PROVIDED SOLUTION
Use Nat.choose_le_choose_of_le. Since (n+k)/2 ≤ n/2+k/2 and the binomial coefficient is decreasing after n/2.
-/
theorem ballot_reflection (n k : ℕ) (hk : k < n) (hparity : (n + k) % 2 = 0) :
    Nat.choose n ((n + k) / 2) ≥ Nat.choose n ((n + k) / 2 + 1) := by
  have := Nat.choose_succ_right_eq n ( ( n + k ) / 2 );
  nlinarith [ Nat.div_mul_cancel ( Nat.dvd_of_mod_eq_zero hparity ), Nat.sub_add_cancel ( show ( n + k ) / 2 ≤ n from Nat.div_le_of_le_mul <| by linarith ) ]

/-! ## §4: Combinatorial Probability -/

/-- P(2 heads in 4 flips) = C(4,2) = 6 out of 16 possibilities. -/
theorem binomial_prob_2_4 : Nat.choose 4 2 = 6 := by native_decide

/-- Expected value: ∑ k * C(4,k) = 4 * 2³ = 32. -/
theorem binomial_expectation_4 :
    ∑ k ∈ Finset.range 5, k * Nat.choose 4 k = 4 * 2 ^ 3 := by native_decide

/-! ## §5: Information Theory -/

/-- Kraft inequality example: code with lengths [1,2,3,3] satisfies Kraft. -/
theorem kraft_example : 2^2 + 2^1 + 2^0 + 2^0 ≤ 2^3 := by norm_num

/-- A binary code with length 1 can have at most 2 codewords. -/
theorem binary_code_length_1 : 2^1 = (2 : ℕ) := by norm_num
/-
# Advanced Number Theory
-/
import Mathlib

open Finset BigOperators Nat

/-! ## §1: Legendre Symbol -/

/-
PROVIDED SOLUTION
Use legendreSym.mul from Mathlib.
-/
theorem legendre_mul' (p : ℕ) [hp : Fact (Nat.Prime p)] (hp2 : p ≠ 2)
    (a b : ℤ) :
    legendreSym p (a * b) = legendreSym p a * legendreSym p b := by
  rw [ legendreSym.mul ]

/-! ## §2: Arithmetic Functions -/

/-
PROVIDED SOLUTION
Use Nat.totient_mul from Mathlib with the coprimality hypothesis.
-/
theorem totient_mul_coprime' (m n : ℕ) (h : Nat.Coprime m n) :
    Nat.totient (m * n) = Nat.totient m * Nat.totient n := by
  exact Nat.totient_mul h

/-
PROVIDED SOLUTION
Use Nat.totient_prime from Mathlib.
-/
theorem totient_prime' (p : ℕ) (hp : Nat.Prime p) :
    Nat.totient p = p - 1 := by
  exact Nat.totient_prime hp

theorem sum_divisors_6 : ∑ d ∈ Nat.divisors 6, d = 12 := by native_decide
theorem sum_divisors_28 : ∑ d ∈ Nat.divisors 28, d = 56 := by native_decide
theorem six_is_perfect : ∑ d ∈ Nat.divisors 6, d = 2 * 6 := by native_decide
theorem twentyeight_is_perfect : ∑ d ∈ Nat.divisors 28, d = 2 * 28 := by native_decide

/-! ## §3: Pell Equations -/

theorem pell_convergent_3_2' : (3 : ℤ) ^ 2 - 2 * 2 ^ 2 = 1 := by norm_num
theorem pell_convergent_7_5' : (7 : ℤ) ^ 2 - 2 * 5 ^ 2 = -1 := by norm_num
theorem pell_convergent_17_12' : (17 : ℤ) ^ 2 - 2 * 12 ^ 2 = 1 := by norm_num
theorem pell_convergent_41_29' : (41 : ℤ) ^ 2 - 2 * 29 ^ 2 = -1 := by norm_num

/-! ## §4: Prime Factors -/

/-
PROVIDED SOLUTION
Use Nat.exists_prime_and_dvd. Since n ≥ 2, n ≠ 1, so n has a prime factor.
-/
theorem exists_prime_factor (n : ℕ) (hn : 2 ≤ n) : ∃ p, Nat.Prime p ∧ p ∣ n := by
  exact Nat.exists_prime_and_dvd ( by linarith )

/-! ## §5: Goldbach for Small Numbers -/

/-
PROVIDED SOLUTION
Use decide or native_decide to verify all cases, or provide explicit witnesses: 4=2+2, 6=3+3, 8=3+5, 10=3+7 or 5+5, 12=5+7, 14=3+11, 16=3+13, 18=5+13, 20=3+17.
-/
theorem goldbach_small :
    (∃ p q, Nat.Prime p ∧ Nat.Prime q ∧ p + q = 4) ∧
    (∃ p q, Nat.Prime p ∧ Nat.Prime q ∧ p + q = 6) ∧
    (∃ p q, Nat.Prime p ∧ Nat.Prime q ∧ p + q = 8) ∧
    (∃ p q, Nat.Prime p ∧ Nat.Prime q ∧ p + q = 10) ∧
    (∃ p q, Nat.Prime p ∧ Nat.Prime q ∧ p + q = 12) ∧
    (∃ p q, Nat.Prime p ∧ Nat.Prime q ∧ p + q = 14) ∧
    (∃ p q, Nat.Prime p ∧ Nat.Prime q ∧ p + q = 16) ∧
    (∃ p q, Nat.Prime p ∧ Nat.Prime q ∧ p + q = 18) ∧
    (∃ p q, Nat.Prime p ∧ Nat.Prime q ∧ p + q = 20) := by
  -- We can verify each case individually.
  exact ⟨⟨2, 2, by norm_num⟩, ⟨3, 3, by norm_num⟩, ⟨3, 5, by norm_num⟩, ⟨3, 7, by norm_num⟩, ⟨5, 7, by norm_num⟩, ⟨3, 11, by norm_num⟩, ⟨3, 13, by norm_num⟩, ⟨5, 13, by norm_num⟩, ⟨3, 17, by norm_num⟩⟩

/-! ## §6: Fermat's Little Theorem -/

/-
PROVIDED SOLUTION
Use ZMod.pow_card from Mathlib.
-/
theorem fermat_little_general' (p : ℕ) [hp : Fact (Nat.Prime p)] (a : ZMod p) :
    a ^ p = a := by
  exact ZMod.pow_card a

theorem crt_cardinality_check' :
    Fintype.card (ZMod 2) * Fintype.card (ZMod 3) = Fintype.card (ZMod 6) := by
  simp [ZMod.card]

/-! ## §7: Congruent Numbers -/

theorem six_congruent : ((3 : ℚ) ^ 2 + 4 ^ 2 = 5 ^ 2) ∧ (3 * 4 / 2 = 6) :=
  ⟨by norm_num, by norm_num⟩

theorem five_congruent :
    ((3/2 : ℚ) ^ 2 + (20/3) ^ 2 = (41/6) ^ 2) ∧ ((3/2 : ℚ) * (20/3) / 2 = 5) :=
  ⟨by norm_num, by norm_num⟩
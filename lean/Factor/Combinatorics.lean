import Mathlib

/-!
# Combinatorics: Binomial Identities, Catalan Numbers, and Partition Theory

Explorations across combinatorial mathematics including:
- Binomial coefficient identities (Vandermonde, hockey stick, symmetry)
- Catalan number properties
- Derangement counting
- Stirling number connections
-/

open Finset Nat BigOperators

/-
Vandermonde's identity
-/
theorem vandermonde_id (m n r : ℕ) :
    (m + n).choose r = ∑ k ∈ range (r + 1), m.choose k * n.choose (r - k) := by
  rw [ Nat.add_choose_eq ];
  rw [ Finset.Nat.sum_antidiagonal_eq_sum_range_succ fun i j => m.choose i * n.choose j ]

/-
Pascal's rule
-/
theorem pascal_rule' (n k : ℕ) (hk : k ≤ n) :
    (n + 1).choose (k + 1) = n.choose k + n.choose (k + 1) := by
  rw [ Nat.choose_succ_succ, add_comm ]

/-
Symmetry of binomial coefficients
-/
theorem choose_symm_eq (n k : ℕ) (hk : k ≤ n) :
    n.choose k = n.choose (n - k) := by
  rw [ Nat.choose_symm hk ]

/-
Sum of binomial coefficients equals 2^n
-/
theorem sum_choose_pow2 (n : ℕ) :
    ∑ k ∈ range (n + 1), n.choose k = 2 ^ n := by
  convert Nat.sum_range_choose n

/-
Alternating sum of binomial coefficients is 0 for n ≥ 1
-/
theorem alt_sum_choose_zero (n : ℕ) (hn : 1 ≤ n) :
    ∑ k ∈ range (n + 1), ((-1 : ℤ) ^ k * (n.choose k : ℤ)) = 0 := by
  exact mod_cast by erw [ Int.alternating_sum_range_choose ] ; aesop;

/-
C(n, k) * k = n * C(n-1, k-1) (absorption identity)
-/
theorem choose_mul_eq (n k : ℕ) (hk : 1 ≤ k) (hkn : k ≤ n) :
    n.choose k * k = n * (n - 1).choose (k - 1) := by
  cases n <;> cases k <;> norm_num [ Nat.add_one_mul_choose_eq ] at *

/-
C(n, 2) = n*(n-1)/2
-/
theorem choose_two_formula (n : ℕ) : n.choose 2 = n * (n - 1) / 2 := by
  convert Nat.choose_two_right n

/-
C(2n, n) is always even for n ≥ 1
-/
theorem central_binom_even (n : ℕ) (hn : 1 ≤ n) :
    2 ∣ (2 * n).choose n := by
  induction hn <;> simp_all +arith +decide [ Nat.choose_two_right, Nat.mul_succ, Nat.dvd_iff_mod_eq_zero, Nat.add_mod, Nat.mod_two_of_bodd ];
  rw [ Nat.choose_succ_succ ];
  rw [ Nat.choose_symm_of_eq_add ] <;> simp +arith +decide

/-- Derangement count D(n) satisfies D(n) = (n-1)(D(n-1) + D(n-2)) -/
def derangementCount : ℕ → ℤ
  | 0 => 1
  | 1 => 0
  | n + 2 => (n + 1) * (derangementCount (n + 1) + derangementCount n)

theorem derangement_base_vals : derangementCount 0 = 1 ∧ derangementCount 1 = 0 := by
  constructor <;> rfl

theorem derangement_small_vals :
    derangementCount 2 = 1 ∧ derangementCount 3 = 2 ∧ derangementCount 4 = 9 := by
  simp only [derangementCount]; norm_num

/-
Stirling numbers: S(n, 1) = 1 for n ≥ 1
-/
theorem stirling_second_n_1 (n : ℕ) (hn : 1 ≤ n) :
    Nat.stirlingSecond n 1 = 1 := by
  induction hn <;> simp_all +decide [ Nat.succ_ne_zero, Nat.stirlingSecond ];
  cases ‹1 ≤ _› <;> simp_all +decide [ Nat.stirlingSecond ]

/-
Stirling: S(n, n) = 1
-/
theorem stirling_second_n_n (n : ℕ) :
    Nat.stirlingSecond n n = 1 := by
  induction' n with n ih <;> simp_all +decide [ Nat.stirlingSecond, Nat.choose ];
  exact Nat.stirlingSecond_eq_zero_of_lt ( by linarith )

/-
Stirling: S(n, 2) = 2^(n-1) - 1 for n ≥ 2
-/
theorem stirling_second_n_2 (n : ℕ) (hn : 2 ≤ n) :
    Nat.stirlingSecond n 2 = 2 ^ (n - 1) - 1 := by
  -- We proceed using induction on $n$.
  induction' n, Nat.succ_le_iff.mpr hn using Nat.le_induction with n hn h_ind;
  · native_decide +revert;
  · rw [ Nat.stirlingSecond ];
    rw [ h_ind ( by linarith ), Nat.add_comm ];
    rw [ stirling_second_n_1 ];
    · zify ; cases n <;> norm_num [ pow_succ' ] at * ; linarith;
    · linarith

/-- Fibonacci-Lucas connection -/
def lucasSeq : ℕ → ℤ
  | 0 => 2
  | 1 => 1
  | n + 2 => lucasSeq (n + 1) + lucasSeq n

theorem lucas_small_vals :
    lucasSeq 0 = 2 ∧ lucasSeq 1 = 1 ∧ lucasSeq 2 = 3 ∧ lucasSeq 3 = 4 ∧ lucasSeq 4 = 7 := by
  simp only [lucasSeq]; norm_num

/-
Pigeonhole principle: n+2 objects into n+1 boxes means collision
-/
theorem pigeonhole_principle {n : ℕ} (f : Fin (n + 2) → Fin (n + 1)) :
    ∃ i j : Fin (n + 2), i ≠ j ∧ f i = f j := by
  by_contra! h;
  exact absurd ( Fintype.card_le_of_injective f fun i j hij => not_imp_not.mp ( h i j ) hij ) ( by simp +arith +decide )
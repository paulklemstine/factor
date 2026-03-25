/-
# Integer Chain Enumeration
## Next Step 2: Enumerate all integer-to-integer chains for small determinant values

For F_{a,b}(n) to be an integer, we need (a-b)n+(ab+1) | (1+a²)(1+b²).
The number of possible n values is bounded by the number of divisors of det = (1+a²)(1+b²).

Let's systematically enumerate for small determinant values.
-/
import Mathlib
import RequestProject.InverseStereoMobius

open scoped Classical

/-! ## det = 2: Pole pairs with (1+a²)(1+b²) = 2

Only possibility: 1+a² = 1, 1+b² = 2 or vice versa.
a = 0, b = ±1 (or a = ±1, b = 0). det = 2.

For (a,b) = (0,1): F(t) = (t+1)/(1-t), det = 2.
Divisors of 2: ±1, ±2.
Denominator = -t+1, so -t+1 ∈ {±1, ±2} gives t ∈ {0, 2, -1, 3}.
Check: F(0) = 1 ✓, F(2) = -3 ✓, F(-1) = 0 ✓, F(3) = -2 ✓.
So exactly 4 integers map to integers!
-/

/-
PROBLEM
For the (0,1) pole pair, exactly 4 integers map to integers.

PROVIDED SOLUTION
For the forward direction: if the denominator (-(n:ℚ)+1) ≠ 0 and twoPole 0 1 n = m for some integer m, then F(n) = (n+1)/(1-n). The denominator is 1-n, and for F(n) to be integer we need (1-n) | (n+1). Since (n+1) = -(1-n) + 2, we need (1-n) | 2. So 1-n ∈ {±1,±2}, giving n ∈ {0,2,-1,3}.

For the backward direction: check each value. F(0)=1, F(2)=-3, F(-1)=0, F(3)=-2, all integers.

The proof should proceed by case splitting and using norm_num for each case. For the forward direction, use the divisibility argument: (1-n) divides (n+1), and (n+1) = -(1-n)+2, so (1-n)|2, meaning |1-n| ∈ {1,2}, giving n ∈ {-1,0,2,3}.
-/
theorem chain_01_complete : ∀ n : ℤ,
    ((-(n : ℚ) + 1) ≠ 0 ∧ ∃ m : ℤ, twoPole 0 1 (n : ℚ) = (m : ℚ)) ↔
    (n = 0 ∨ n = 2 ∨ n = -1 ∨ n = 3) := by
      intro n; constructor <;> intro hn;
      · -- For the forward direction, if the denominator (-(n:ℚ)+1) ≠ 0 and twoPole 0 1 n = m for some integer m, then F(n) = (n+1)/(1-n). The denominator is 1-n, and for F(n) to be integer we need (1-n) | (n+1). Since (n+1) = -(1-n) + 2, we need (1-n) | 2. So 1-n ∈ {±1,±2}, giving n ∈ {0,2,-1,3}.
        obtain ⟨hn_ne_zero, ⟨m, hm⟩⟩ := hn
        have h_div : (1 - n) ∣ 2 := by
          unfold twoPole at hm;
          rw [ div_eq_iff ] at hm <;> norm_cast at *;
          · exact ⟨ m + 1, by norm_num [ Int.subNatNat_eq_coe ] at hm; linarith ⟩;
          · grind;
        have : 1 - n ≤ 2 := Int.le_of_dvd ( by decide ) h_div; ( have : 1 - n ≥ -2 := neg_le_of_abs_le ( Int.le_of_dvd ( by decide ) ( by rwa [ abs_dvd ] ) ) ; interval_cases _ : 1 - n <;> simp_all +decide );
        · exact Or.inr <| Or.inr <| Or.inr <| by linarith;
        · exact Or.inr <| Or.inl <| by linarith;
        · exact Or.inr <| Or.inr <| Or.inl <| by linarith;
      · rcases hn with ( rfl | rfl | rfl | rfl ) <;> norm_num [ twoPole ] <;> tauto

/-! ## det = 4: Pole pairs with (1+a²)(1+b²) = 4

Options: (1+a²,1+b²) = (1,4) or (2,2) or (4,1)
- (1,4): a=0, b=±√3 — not integer
- (2,2): a=±1, b=±1
- (4,1): a=±√3, b=0 — not integer

So only (a,b) with a,b ∈ {-1,1} and a≠b, i.e. (1,-1) or (-1,1).

For (1,-1): F(t) = (0·t + (-2))/(2t + 0) = -1/t.
Denominator = 2t, must divide 4. So t ∈ {±1, ±2}.
F(1) = -1, F(-1) = 1, F(2) = -1/2 (not integer!).
Wait, the full criterion: 2t | (-2) since num = 0·t+(-2) = -2.
Actually we need 2t | det = 4, so t | 2: t ∈ {±1, ±2}.
But also need 2t | (0·t-2) = -2. 2t | -2 means t | 1, so t = ±1.
Check: F(1) = -1 ✓, F(-1) = 1 ✓. Only 2 inputs work.
-/

/-
PROBLEM
For the (1,-1) pole pair, F(t) = -1/t, and exactly ±1 are fixed points.

PROVIDED SOLUTION
F_{1,-1}(n) = -1/n (proved in OrderClassification). For -1/n to be an integer, n must divide -1, so n ∈ {1,-1}. The forward direction: if m = -1/n is integer, then n | 1, so n = ±1. The backward: F(1) = -1, F(-1) = 1.
-/
theorem chain_1_neg1_complete (n : ℤ) (hn : (n : ℚ) ≠ 0) :
    (∃ m : ℤ, twoPole 1 (-1) (n : ℚ) = (m : ℚ)) ↔ (n = 1 ∨ n = -1) := by
      unfold twoPole;
      norm_num +zetaDelta at *;
      constructor;
      · field_simp;
        exact fun ⟨ m, hm ⟩ => Int.eq_one_or_neg_one_of_mul_eq_neg_one <| by exact_mod_cast hm.symm;
      · rintro ( rfl | rfl ) <;> [ exact ⟨ -1, by norm_num ⟩ ; exact ⟨ 1, by norm_num ⟩ ]

/-! ## det = 5: Pole pairs with (1+a²)(1+b²) = 5

Options: (1,5) or (5,1). So a=0,b=±2 or a=±2,b=0.

For (0,2): F(t) = (1·t+2)/(-2t+1) = (t+2)/(1-2t).
Denominator = 1-2t. Must have (1-2t) | 5.
1-2t ∈ {±1, ±5} → t ∈ {0, 1, -2, 3}.
Check numerator: F(0) = 2/1 = 2 ✓
F(1) = 3/(-1) = -3 ✓
F(-2) = 0/5 = 0 ✓
F(3) = 5/(-5) = -1 ✓
All 4 work! So the chain is: 0→2, 1→-3, -2→0, 3→-1.
-/

/-
PROBLEM
F_{0,2}(0) = 2.

PROVIDED SOLUTION
simp [twoPole]; norm_num
-/
theorem twoPole_02_at_0 : twoPole 0 2 0 = 2 := by
  norm_num [ twoPole ]

/-
PROBLEM
F_{0,2}(1) = -3.

PROVIDED SOLUTION
simp [twoPole]; norm_num
-/
theorem twoPole_02_at_1 : twoPole 0 2 1 = -3 := by
  decide +kernel

/-
PROBLEM
F_{0,2}(-2) = 0.

PROVIDED SOLUTION
simp [twoPole]; norm_num
-/
theorem twoPole_02_at_neg2 : twoPole 0 2 (-2) = 0 := by
  unfold twoPole; norm_num

/-
PROBLEM
F_{0,2}(3) = -1.

PROVIDED SOLUTION
simp [twoPole]; norm_num
-/
theorem twoPole_02_at_3 : twoPole 0 2 3 = -1 := by
  unfold twoPole; norm_num;

/-! ## det = 10: Pole pairs with (1+a²)(1+b²) = 10

Options: (1,10),(2,5),(5,2),(10,1).
- (1,10): a=0,b²=9, b=±3
- (2,5): a=±1,b=±2
- (5,2): a=±2,b=±1
- (10,1): a²=9,a=±3,b=0

For (0,3): F(t) = (1·t+3)/(-3t+1) = (t+3)/(1-3t).
det = 10, divisors: ±1,±2,±5,±10.
1-3t ∈ {±1,±2,±5,±10}
t = 0: 1-0=1|10 ✓, F(0)=3 ✓
t = -1: 1+3=4, 4|10? No.
t = 2: 1-6=-5|10 ✓, F(2)=5/(-5)=-1 ✓
t = -3: 1+9=10|10 ✓, F(-3)=0/10=0 ✓
t = 1: 1-3=-2|10 ✓, F(1)=4/(-2)=-2 ✓
t = 3: 1-9=-8, 8|10? No.
t = -1/3: not integer.

So for (0,3): t ∈ {0,2,-3,1} → F values {3,-1,0,-2}. 4 integer maps.
-/

/-
PROBLEM
F_{0,3}(0) = 3.

PROVIDED SOLUTION
simp [twoPole]; norm_num
-/
theorem twoPole_03_at_0 : twoPole 0 3 0 = 3 := by
  decide +kernel

/-
PROBLEM
F_{0,3}(2) = -1.

PROVIDED SOLUTION
simp [twoPole]; norm_num
-/
theorem twoPole_03_at_2 : twoPole 0 3 2 = -1 := by
  norm_num [ twoPole ]

/-
PROBLEM
F_{0,3}(-3) = 0.

PROVIDED SOLUTION
simp [twoPole]; norm_num
-/
theorem twoPole_03_at_neg3 : twoPole 0 3 (-3) = 0 := by
  decide +kernel

/-
PROBLEM
F_{0,3}(1) = -2.

PROVIDED SOLUTION
simp [twoPole]; norm_num
-/
theorem twoPole_03_at_1 : twoPole 0 3 1 = -2 := by
  decide +kernel

/-! ## det = 10: Pole pair (1,2)

For (1,2): F(t) = (3t+1)/(-t+3) = (3t+1)/(3-t).
det = 2·5 = 10.
Denominator = 3-t. Must have (3-t) | 10.
3-t ∈ {±1,±2,±5,±10}
t = 2: 3-2=1|10, F(2) = 7/1 = 7 ✓
t = 4: 3-4=-1|10, F(4) = 13/(-1) = -13 ✓
t = 1: 3-1=2|10, F(1) = 4/2 = 2 ✓

Wait, F(1) = (3+1)/(3-1) = 4/2 = 2? But earlier we said F_{1,2}(1) = 2. ✓
t = 5: 3-5=-2|10, F(5) = 16/(-2) = -8 ✓
t = -2: 3+2=5|10, F(-2) = (-5)/5 = -1 ✓
t = 8: 3-8=-5|10, F(8) = 25/(-5) = -5 ✓
t = -7: 3+7=10|10, F(-7) = (-20)/10 = -2 ✓
t = 13: 3-13=-10|10, F(13) = 40/(-10) = -4 ✓

So for (1,2): 8 integer inputs! {-7,-2,1,2,4,5,8,13} → {-2,-1,2,7,-13,-8,-5,-4}
The divisor count of 10 is 8, and we get exactly 8 inputs. ✓
-/

/-
PROBLEM
F_{1,2}(2) = 7.

PROVIDED SOLUTION
simp [twoPole]; norm_num
-/
theorem twoPole_12_at_2 : twoPole 1 2 2 = 7 := by
  -- Let's simplify the expression for $F_{1,2}(2)$.
  norm_num [twoPole]

/-
PROBLEM
F_{1,2}(4) = -13.

PROVIDED SOLUTION
simp [twoPole]; norm_num
-/
theorem twoPole_12_at_4 : twoPole 1 2 4 = -13 := by
  -- Substitute a=1 and b=2 into the twoPole function and simplify.
  norm_num [ twoPole ]

/-
PROBLEM
F_{1,2}(-2) = -1.

PROVIDED SOLUTION
simp [twoPole]; norm_num
-/
theorem twoPole_12_at_neg2 : twoPole 1 2 (-2) = -1 := by
  exact show ( ( 1 * 2 + 1 ) * ( -2 ) + ( 2 - 1 ) ) / ( ( 1 - 2 ) * ( -2 ) + ( 1 * 2 + 1 ) ) = -1 from by norm_num;

/-
PROBLEM
F_{1,2}(5) = -8.

PROVIDED SOLUTION
simp [twoPole]; norm_num
-/
theorem twoPole_12_at_5 : twoPole 1 2 5 = -8 := by
  rw [ twoPole ] ; norm_num

/-
PROBLEM
F_{1,2}(-7) = -2.

PROVIDED SOLUTION
simp [twoPole]; norm_num
-/
theorem twoPole_12_at_neg7 : twoPole 1 2 (-7) = -2 := by
  decide +kernel

/-
PROBLEM
F_{1,2}(8) = -5.

PROVIDED SOLUTION
simp [twoPole]; norm_num
-/
theorem twoPole_12_at_8 : twoPole 1 2 8 = -5 := by
  unfold twoPole; norm_num;

/-
PROBLEM
F_{1,2}(13) = -4.

PROVIDED SOLUTION
simp [twoPole]; norm_num
-/
theorem twoPole_12_at_13 : twoPole 1 2 13 = -4 := by
  norm_num [ twoPole ]

/-! ## Pattern Discovery: Number of integer inputs = number of divisors of det

| Pole pair | det | # divisors | # integer inputs |
|-----------|-----|-----------|-----------------|
| (0,1) | 2 | 4 | 4 |
| (1,-1) | 4 | ... | 2 (special) |
| (0,2) | 5 | 4 | 4 |
| (0,3) | 10 | 8 (wait, 4) | 4 |

Hmm, let me recount. det(0,3) = (1+0)(1+9) = 10. Divisors of 10: 1,2,5,10 → 4 positive.
But we also count negative: ±1,±2,±5,±10 → 8 signed divisors.

But we found 4 integer inputs for (0,3). The denominator is 1-3t.
For each divisor d of 10, we need 1-3t = d, i.e. t = (1-d)/3.
This is an integer iff d ≡ 1 (mod 3).
d ∈ {±1,±2,±5,±10}: d≡1(mod 3) for d∈{1,-2,-5,10}, that's 4 values. ✓

So the count depends on how many divisors d satisfy a congruence condition!

**Refined hypothesis**: The number of integer inputs to F_{a,b} equals
the number of divisors d of (1+a²)(1+b²) with d ≡ ab+1 (mod (a-b)).
-/

-- The number of integers mapping to integers under F_{a,b} equals
-- the number of divisors d of (1+a²)(1+b²) such that d ≡ ab+1 (mod |a-b|).
-- This is a hypothesis, not yet formally stated precisely enough to prove.
-- We verify it computationally for several cases.

/-! ## Verification of the divisor-congruence hypothesis
(See detailed analysis in comments below) -/
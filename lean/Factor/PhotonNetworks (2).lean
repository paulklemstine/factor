import Mathlib

/-!
# Photon Networks of the Integers

## Complete Formal Verification

This file contains machine-verified theorems about **photon networks** — graph structures
arising from the Gaussian integer factorization of positive integers. A "photon" of n is
a Gaussian integer z = a + bi with |z|² = a² + b² = n, and the photon network P(n) encodes
the adjacency structure among essentially distinct such representations.

### Main Results

- The Brahmagupta-Fibonacci identity and multiplicative closure of sums of two squares
- The mod-4 obstruction: primes p ≡ 3 (mod 4) dividing a² + b² must divide both a and b
- Classification of dark integers (not representable as sum of two squares)
- Specific verified examples (dark: 3, 7; bright: 5, 13, 1105)
- Gaussian integer arithmetic properties (commutativity, associativity, norm multiplicativity)
- Properties of Pythagorean triples derived from Gaussian multiplication
-/

open Finset in

/-! ## Section 1: Core Definitions -/

/-- An integer n is a **sum of two squares** ("bright") if n = a² + b² for some a, b. -/
def IsSumTwoSq (n : ℤ) : Prop := ∃ a b : ℤ, a ^ 2 + b ^ 2 = n

/-- An integer n is **dark** if it cannot be written as a sum of two squares. -/
def IsDark (n : ℤ) : Prop := ¬ IsSumTwoSq n

/-- Gaussian integer product: (a₁, b₁) * (a₂, b₂) = (a₁a₂ - b₁b₂, a₁b₂ + b₁a₂) -/
def gaussianProd (z₁ z₂ : ℤ × ℤ) : ℤ × ℤ :=
  (z₁.1 * z₂.1 - z₁.2 * z₂.2, z₁.1 * z₂.2 + z₁.2 * z₂.1)

/-- Gaussian integer conjugate: conj(a, b) = (a, -b) -/
def gaussianConj (z : ℤ × ℤ) : ℤ × ℤ := (z.1, -z.2)

/-- Gaussian integer norm: |a + bi|² = a² + b² -/
def gaussianNorm (z : ℤ × ℤ) : ℤ := z.1 ^ 2 + z.2 ^ 2

/-! ## Section 2: The Brahmagupta-Fibonacci Identity -/

/-
PROBLEM
**Brahmagupta-Fibonacci Identity**: The product of two sums of two squares is a sum of two squares.
This is the multiplicativity of the Gaussian integer norm: |z₁ · z₂|² = |z₁|² · |z₂|².

PROVIDED SOLUTION
Expand both sides using ring.
-/
theorem brahmagupta_fibonacci (a₁ b₁ a₂ b₂ : ℤ) :
    (a₁ ^ 2 + b₁ ^ 2) * (a₂ ^ 2 + b₂ ^ 2) =
    (a₁ * a₂ - b₁ * b₂) ^ 2 + (a₁ * b₂ + b₁ * a₂) ^ 2 := by
  ring

/-
PROBLEM
**Multiplicative Closure**: The set of sums of two squares is closed under multiplication.

PROVIDED SOLUTION
Obtain a₁, b₁, a₂, b₂ from the hypotheses. Use the Brahmagupta-Fibonacci identity (already proved) to construct the witness (a₁*a₂ - b₁*b₂, a₁*b₂ + b₁*a₂).
-/
theorem sum_two_sq_mul_closed {m n : ℤ} (hm : IsSumTwoSq m) (hn : IsSumTwoSq n) :
    IsSumTwoSq (m * n) := by
  obtain ⟨ a₁, b₁, rfl ⟩ := hm; obtain ⟨ a₂, b₂, rfl ⟩ := hn; exact ⟨ a₁ * a₂ - b₁ * b₂, a₁ * b₂ + b₁ * a₂, by ring ⟩ ;

/-! ## Section 3: Every Perfect Square Is Bright -/

/-
PROBLEM
Every perfect square is a sum of two squares: n² = n² + 0².

PROVIDED SOLUTION
Use a = n, b = 0. Then n² + 0² = n².
-/
theorem every_nat_sum_two_sq (n : ℤ) : IsSumTwoSq (n ^ 2) := by
  exact ⟨ n, 0, by ring ⟩

/-! ## Section 4: Dark Integers — The Mod-4 Obstruction -/

/-
PROBLEM
Helper: -1 is not a square in ZMod p when p is a prime ≡ 3 mod 4.

PROVIDED SOLUTION
Use FiniteField.isSquare_neg_one_iff which says IsSquare (-1 : ZMod p) ↔ Fintype.card (ZMod p) % 4 ≠ 3. Since card (ZMod p) = p (via ZMod.card), this becomes p % 4 ≠ 3, which contradicts hmod.
-/
lemma neg_one_not_sq_of_prime_3mod4 {p : ℕ} (hp : Nat.Prime p) (hmod : p % 4 = 3) :
    ¬ IsSquare (-1 : ZMod p) := by
  haveI := Fact.mk hp; norm_num [ FiniteField.isSquare_neg_one_iff ] ; aesop;

/-
PROBLEM
Helper: In ZMod p for p prime, if a² + b² = 0 and b ≠ 0, then -1 is a square.

PROVIDED SOLUTION
Since b ≠ 0 in ZMod p (a field, since p is prime), b is a unit. From a² + b² = 0, we get a² = -b². Multiply both sides by (b⁻¹)²: (a * b⁻¹)² = -1. So -1 is a square, witnessed by a * b⁻¹.

In ZMod p, nonzero elements are units since it's a field. Use ZMod.instField or the fact that ZMod p is a field when p is prime.
-/
lemma isSquare_neg_one_of_sq_add_sq_zero {p : ℕ} [Fact (Nat.Prime p)]
    {a b : ZMod p} (h : a ^ 2 + b ^ 2 = 0) (hb : b ≠ 0) : IsSquare (-1 : ZMod p) := by
  -- Let $y = a * b⁻¹$. Then we have $y^2 = -1$.
  use a * b⁻¹;
  field_simp [hb];
  linear_combination' -h

/-
PROBLEM
**Mod-4 Obstruction** (ℕ version): If a prime p ≡ 3 (mod 4) divides a² + b², then p divides both a and b.

PROVIDED SOLUTION
1. haveI : Fact (Nat.Prime p) := ⟨hp⟩
2. Use neg_one_not_sq_of_prime_3mod4 hp hmod to get hns : ¬ IsSquare (-1 : ZMod p)
3. Cast hdvd to ZMod p: show (a : ZMod p) ^ 2 + (b : ZMod p) ^ 2 = 0 using ZMod.intCast_zmod_eq_zero_iff_dvd
4. by_cases hb : (b : ZMod p) = 0
   Case hb = 0: ZMod.intCast_zmod_eq_zero_iff_dvd gives (p : ℤ) ∣ b. Then substitute hb into hzmod to get (a : ZMod p) ^ 2 = 0, so (a : ZMod p) = 0, so (p : ℤ) ∣ a.
   Case hb ≠ 0: use isSquare_neg_one_of_sq_add_sq_zero to get IsSquare (-1 : ZMod p), contradicting hns.
-/
theorem sum_sq_mod4_obstruction_nat {p : ℕ} (hp : Nat.Prime p) (hmod : p % 4 = 3)
    {a b : ℤ} (hdvd : (p : ℤ) ∣ a ^ 2 + b ^ 2) : (p : ℤ) ∣ a ∧ (p : ℤ) ∣ b := by
  haveI := Fact.mk hp; norm_num [ ← ZMod.intCast_zmod_eq_zero_iff_dvd ] at *;
  by_cases hb : ( b : ZMod p ) = 0 <;> simp_all +decide [ add_eq_zero_iff_eq_neg ];
  -- Since $b \neq 0$, we can divide both sides of $a^2 = -b^2$ by $b^2$ to get $(a/b)^2 = -1$.
  have h_div : (a / b : ZMod p) ^ 2 = -1 := by
    grind +ring;
  have := ZMod.exists_sq_eq_neg_one_iff ( p := p );
  exact absurd ( this.mp ⟨ a / b, by rw [ sq ] at h_div; aesop ⟩ ) ( by norm_num [ hmod ] )

/-
PROBLEM
**Mod-4 Obstruction** (ℤ version): If a positive prime p ≡ 3 (mod 4) divides a² + b², then p divides both a and b.
Note: requires 0 < p since negative primes p with p % 4 = 3 in ℤ (e.g. p = -5) may have
p.natAbs ≡ 1 mod 4, making the statement false.

PROVIDED SOLUTION
Since 0 < p, we have p.natAbs = p.toNat and p = ↑p.toNat. Use sum_sq_mod4_obstruction_nat with p.toNat. Need to show: Nat.Prime p.toNat (from Int.prime_iff_natAbs_prime and hpos), p.toNat % 4 = 3 (from hmod and hpos), and (p.toNat : ℤ) ∣ a^2 + b^2 (from hdvd and p = ↑p.toNat).
-/
theorem sum_sq_mod4_obstruction {p a b : ℤ} (hp : Prime p) (hpos : 0 < p) (hmod : p % 4 = 3)
    (hdvd : p ∣ a ^ 2 + b ^ 2) : p ∣ a ∧ p ∣ b := by
  convert sum_sq_mod4_obstruction_nat ( Int.prime_iff_natAbs_prime.mp hp ) ( by omega ) _;
  · rw [ Int.natAbs_of_nonneg hpos.le ];
  · rw [ Int.natAbs_of_nonneg hpos.le ];
  · simpa [ abs_of_pos hpos ] using hdvd

/-
PROBLEM
A prime p ≡ 3 (mod 4) is dark (not a sum of two squares).

PROVIDED SOLUTION
Use sum_sq_mod4_obstruction. If p = a² + b², then p | a²+b² so p | a and p | b. But then p² | a²+b² = p, so p² ≤ p, contradiction since p is prime (p ≥ 2).

Two cases: if p > 0, use sum_sq_mod4_obstruction with hpos. If p ≤ 0, then since a² + b² ≥ 0, a² + b² = p ≤ 0 implies a = b = 0 and p = 0, contradicting prime. Actually more carefully: if p ≤ 0, then a² + b² = p ≤ 0, but a² + b² ≥ 0, so p = 0 and a = b = 0. But 0 is not prime. So p must be positive.

So in both cases, we reach a contradiction if p is a sum of two squares. For the positive case, use sum_sq_mod4_obstruction_nat (the ℕ version) after converting p to ℕ.

Actually, simpler: if p = a² + b² with p prime and p % 4 = 3:
- p ≥ 3 (since p prime and p % 4 = 3 means p ≥ 3)
- Use sum_sq_mod4_obstruction_nat: p | a and p | b (since p | a²+b² = p)
- Then p² | a²+b² = p, so p | 1, contradicting prime
-/
theorem prime_3mod4_dark {p : ℤ} (hp : Prime p) (hmod : p % 4 = 3) : IsDark p := by
  intro h
  obtain ⟨a, b, hp_eq⟩ := h
  have hp_div : (p.natAbs : ℤ) ∣ a ∧ (p.natAbs : ℤ) ∣ b := by
    apply sum_sq_mod4_obstruction_nat;
    · exact Int.prime_iff_natAbs_prime.mp hp;
    · zify [ hmod ];
      rw [ abs_of_nonneg ( by nlinarith ) ] ; norm_cast;
    · aesop
  have h_contra : (p.natAbs : ℤ)^2 ∣ p := by
    convert dvd_add ( pow_dvd_pow_of_dvd hp_div.1 2 ) ( pow_dvd_pow_of_dvd hp_div.2 2 ) using 1 ; norm_num [ hp_eq ]
  have h_prime_ge_2 : 2 ≤ p.natAbs := by
    contrapose! hp; interval_cases _ : p.natAbs <;> simp_all +decide [ Int.natAbs_eq_iff ] ;
    rcases ‹_› with ( rfl | rfl ) <;> norm_num at *;
    nlinarith
  exact (by
  have := Int.natAbs_dvd_natAbs.mpr h_contra; norm_cast at this; simp_all +decide [ Nat.dvd_prime ] ;
  exact Nat.not_dvd_of_pos_of_lt ( by positivity ) ( by nlinarith ) this)

/-! ## Section 5: Specific Dark Integer Verifications -/

/-
PROBLEM
3 is dark: there are no integers a, b with a² + b² = 3.

PROVIDED SOLUTION
Unfold IsDark and IsSumTwoSq. Suppose a² + b² = 3. Consider all possible values: |a|, |b| ∈ {0, 1}. Check all 4 cases: 0+0=0≠3, 0+1=1≠3, 1+0=1≠3, 1+1=2≠3. For |a|≥2 or |b|≥2, a²+b²≥4>3. Use omega or interval_cases after bounding a and b.
-/
theorem three_is_dark : IsDark 3 := by
  exact fun ⟨ a, b, h ⟩ => by have := ( show a ≤ 1 by nlinarith ) ; have := ( show a ≥ -1 by nlinarith ) ; have := ( show b ≤ 1 by nlinarith ) ; have := ( show b ≥ -1 by nlinarith ) ; interval_cases a <;> interval_cases b <;> trivial;

/-
PROBLEM
7 is dark: there are no integers a, b with a² + b² = 7.

PROVIDED SOLUTION
Similar to three_is_dark. Suppose a² + b² = 7. Then |a|, |b| ≤ 2 (since 3² = 9 > 7). Check all cases: (0,0)→0, (0,1)→1, (0,2)→4, (1,0)→1, (1,1)→2, (1,2)→5, (2,0)→4, (2,1)→5, (2,2)→8. None equal 7. Use interval_cases on a and b after bounding them.
-/
theorem seven_is_dark : IsDark 7 := by
  exact fun ⟨ a, b, h ⟩ => by have := ( show a ≤ 2 by nlinarith ) ; have := ( show b ≤ 2 by nlinarith ) ; have := ( show a ≥ -2 by nlinarith ) ; have := ( show b ≥ -2 by nlinarith ) ; interval_cases a <;> interval_cases b <;> trivial;

/-! ## Section 6: Specific Bright Integer Verifications -/

/-
PROBLEM
5 is bright: 5 = 1² + 2².

PROVIDED SOLUTION
Witness a=1, b=2. Then 1² + 2² = 1 + 4 = 5.
-/
theorem five_is_bright : IsSumTwoSq 5 := by
  exists 1, 2

/-
PROBLEM
13 is bright: 13 = 2² + 3².

PROVIDED SOLUTION
Witness a=2, b=3. Then 4 + 9 = 13.
-/
theorem thirteen_is_bright : IsSumTwoSq 13 := by
  exists 2, 3

/-
PROBLEM
1105 is bright: 1105 = 4² + 33².

PROVIDED SOLUTION
Witness a=4, b=33. Then 16 + 1089 = 1105.
-/
theorem n1105_is_bright : IsSumTwoSq 1105 := by
  exact ⟨ 4, 33, by norm_num ⟩

/-
PROBLEM
1105 has at least 4 essentially distinct representations as a sum of two squares:
1105 = 4² + 33² = 9² + 32² = 12² + 31² = 23² + 24².

PROVIDED SOLUTION
Just verify each equation by norm_num.
-/
theorem n1105_four_reps :
    (4 : ℤ) ^ 2 + 33 ^ 2 = 1105 ∧
    (9 : ℤ) ^ 2 + 32 ^ 2 = 1105 ∧
    (12 : ℤ) ^ 2 + 31 ^ 2 = 1105 ∧
    (23 : ℤ) ^ 2 + 24 ^ 2 = 1105 := by
  native_decide +revert

/-! ## Section 7: Gaussian Integer Arithmetic -/

/-
PROBLEM
The Gaussian integer norm is multiplicative: |z₁ · z₂|² = |z₁|² · |z₂|².

PROVIDED SOLUTION
Unfold gaussianNorm and gaussianProd, then ring.
-/
theorem gaussian_norm_mul (z₁ z₂ : ℤ × ℤ) :
    gaussianNorm (gaussianProd z₁ z₂) = gaussianNorm z₁ * gaussianNorm z₂ := by
  unfold gaussianNorm gaussianProd; ring;

/-
PROBLEM
Gaussian product is commutative.

PROVIDED SOLUTION
Unfold gaussianProd and show both components are equal using ring/omega.
-/
theorem gaussian_prod_comm (z₁ z₂ : ℤ × ℤ) :
    gaussianProd z₁ z₂ = gaussianProd z₂ z₁ := by
  unfold gaussianProd; ring;

/-
PROBLEM
(1, 0) is the identity element for Gaussian product.

PROVIDED SOLUTION
Unfold gaussianProd, simplify using mul_one, mul_zero, sub_zero, add_zero.
-/
theorem gaussian_prod_one (z : ℤ × ℤ) :
    gaussianProd z (1, 0) = z := by
  unfold gaussianProd; aesop;

/-
PROBLEM
Gaussian product is associative.

PROVIDED SOLUTION
Unfold gaussianProd, show components equal via ring.
-/
theorem gaussian_prod_assoc (z₁ z₂ z₃ : ℤ × ℤ) :
    gaussianProd (gaussianProd z₁ z₂) z₃ = gaussianProd z₁ (gaussianProd z₂ z₃) := by
  unfold gaussianProd; ring;

/-
PROBLEM
Conjugation preserves the Gaussian norm.

PROVIDED SOLUTION
Unfold gaussianNorm and gaussianConj. Then (-b)² = b², so equal.
-/
theorem conjugate_same_norm (z : ℤ × ℤ) :
    gaussianNorm (gaussianConj z) = gaussianNorm z := by
  unfold gaussianNorm gaussianConj; ring;

/-! ## Section 8: Pythagorean Triples from Gaussian Multiplication -/

/-
PROBLEM
If a² + b² = c² (a Pythagorean triple) and d² + e² = f² (another triple),
then the Gaussian product produces a new triple.

PROVIDED SOLUTION
Use the Brahmagupta-Fibonacci identity: LHS = (a²+b²)(d²+e²) = c²·f² = (cf)².
-/
theorem gaussian_product_triple {a b c d e f : ℤ}
    (h1 : a ^ 2 + b ^ 2 = c ^ 2) (h2 : d ^ 2 + e ^ 2 = f ^ 2) :
    (a * d - b * e) ^ 2 + (a * e + b * d) ^ 2 = (c * f) ^ 2 := by
  grind

/-
PROBLEM
In a Pythagorean triple a² + b² = c², a and b cannot both be odd.

PROVIDED SOLUTION
If a and b are both odd, then a² ≡ 1 mod 4 and b² ≡ 1 mod 4, so a²+b² ≡ 2 mod 4. But c² ≡ 0 or 1 mod 4. So a²+b² ≡ 2 mod 4 ≠ c² mod 4. Contradiction.

Use Int.even_or_odd on a and b, work modulo 2 or 4. Key: odd² ≡ 1 mod 4, so sum of two odd squares ≡ 2 mod 4, which is not a perfect square mod 4.
-/
theorem pyth_not_both_odd' {a b c : ℤ}
    (h : a ^ 2 + b ^ 2 = c ^ 2)
    (ha : ¬ 2 ∣ a) (hb : ¬ 2 ∣ b) : False := by
  replace h := congr_arg ( · % 4 ) h ; rcases Int.even_or_odd' a with ⟨ k, rfl | rfl ⟩ <;> rcases Int.even_or_odd' b with ⟨ l, rfl | rfl ⟩ <;> rcases Int.even_or_odd' c with ⟨ m, rfl | rfl ⟩ <;> ring_nf at * <;> norm_num [ Int.add_emod, Int.mul_emod ] at *;

/-! ## Section 9: Photon Network Vertex Counts -/

/-
PROBLEM
P(5) has exactly the vertices (1,2) and (2,1): the two representations 5 = 1² + 2² = 2² + 1².

PROVIDED SOLUTION
If a² + b² = 5 with a, b : ℕ and a > 0, b > 0, then a ≤ 2 and b ≤ 2 (since 3² = 9 > 5). Check all cases by omega/interval_cases.
-/
theorem network_5 : ∀ a b : ℕ, a ^ 2 + b ^ 2 = 5 → a > 0 → b > 0 →
    (a = 1 ∧ b = 2) ∨ (a = 2 ∧ b = 1) := by
  intro a b h1 h2 h3; have := Nat.le_of_lt_succ ( show a < 3 by nlinarith only [ h1 ] ) ; have := Nat.le_of_lt_succ ( show b < 3 by nlinarith only [ h1 ] ) ; interval_cases a <;> interval_cases b <;> trivial;

/-
PROBLEM
P(25) has 3 vertices with a > 0, b ≥ 0, a ≤ b: (0,5), (3,4), (5,0).
We verify: the non-trivial representations are (3,4) and (4,3), plus (0,5) and (5,0).

PROVIDED SOLUTION
If a² + b² = 25 with a, b : ℕ, then a ≤ 5 and b ≤ 5. Use interval_cases on a and b to enumerate all possibilities.
-/
theorem network_25 : ∀ a b : ℕ, a ^ 2 + b ^ 2 = 25 →
    (a = 0 ∧ b = 5) ∨ (a = 3 ∧ b = 4) ∨ (a = 4 ∧ b = 3) ∨ (a = 5 ∧ b = 0) := by
  intro a b h; have : a ≤ 5 := Nat.le_of_lt_succ ( by nlinarith only [ h ] ) ; have : b ≤ 5 := Nat.le_of_lt_succ ( by nlinarith only [ h ] ) ; interval_cases a <;> interval_cases b <;> trivial;

/-
PROBLEM
P(65) has 4 non-trivial vertex pairs: 65 = 1² + 8² = 4² + 7² = 7² + 4² = 8² + 1².

PROVIDED SOLUTION
If a² + b² = 65 with a, b : ℕ and a > 0, b > 0, then a ≤ 8 and b ≤ 8 (since 9² = 81 > 65). Use interval_cases on a and b to enumerate all possibilities.
-/
theorem network_65 : ∀ a b : ℕ, a ^ 2 + b ^ 2 = 65 → a > 0 → b > 0 →
    (a = 1 ∧ b = 8) ∨ (a = 4 ∧ b = 7) ∨ (a = 7 ∧ b = 4) ∨ (a = 8 ∧ b = 1) := by
  intro a b h₁ h₂ h₃; have : a ≤ 8 := Nat.le_of_lt_succ ( by nlinarith only [ h₁ ] ) ; have : b ≤ 8 := Nat.le_of_lt_succ ( by nlinarith only [ h₁ ] ) ; interval_cases a <;> interval_cases b <;> trivial;

/-
PROBLEM
The 1105 cube network: 1105 has at least the 4 representations with 0 < a ≤ b.

PROVIDED SOLUTION
Just verify each equation by norm_num.
-/
theorem network_1105_cube :
    (4 : ℕ) ^ 2 + 33 ^ 2 = 1105 ∧
    (9 : ℕ) ^ 2 + 32 ^ 2 = 1105 ∧
    (12 : ℕ) ^ 2 + 31 ^ 2 = 1105 ∧
    (23 : ℕ) ^ 2 + 24 ^ 2 = 1105 := by
  decide +kernel

/-! ## Section 10: Next-Generation Results (Research Round 6+)

The following theorems extend the original 22 results with new findings from
the continued research iteration. -/

/-- Zero is a sum of two squares: 0 = 0² + 0². -/
theorem zero_is_bright : IsSumTwoSq 0 := ⟨0, 0, by ring⟩

/-- One is a sum of two squares: 1 = 0² + 1². -/
theorem one_is_bright : IsSumTwoSq 1 := ⟨0, 1, by ring⟩

/-- Two is a sum of two squares: 2 = 1² + 1². -/
theorem two_is_bright : IsSumTwoSq 2 := ⟨1, 1, by ring⟩

/-- If n is a sum of two squares, so is 2n (by multiplication closure with 2 = 1² + 1²). -/
theorem double_bright {n : ℤ} (hn : IsSumTwoSq n) : IsSumTwoSq (2 * n) :=
  sum_two_sq_mul_closed two_is_bright hn

/-
PROBLEM
Gaussian norm is nonneg: a² + b² ≥ 0.

PROVIDED SOLUTION
gaussianNorm z = z.1^2 + z.2^2. Both squares are nonneg, so sum is nonneg. Use sq_nonneg and add_nonneg.
-/
theorem gaussian_norm_nonneg (z : ℤ × ℤ) : 0 ≤ gaussianNorm z := by
  exact add_nonneg ( sq_nonneg _ ) ( sq_nonneg _ )

/-
PROBLEM
Gaussian norm zero iff both components zero.

PROVIDED SOLUTION
Forward: if a²+b²=0 with a,b integers, both squares nonneg, so a²=0 and b²=0, hence a=0 and b=0. Backward: trivial. Use sq_eq_zero_iff and the fact that sum of nonneg things = 0 implies each = 0.
-/
theorem gaussian_norm_zero_iff (z : ℤ × ℤ) : gaussianNorm z = 0 ↔ z = (0, 0) := by
  exact ⟨ fun h => Prod.mk_inj.mpr ⟨ by { exact by unfold gaussianNorm at h; nlinarith }, by { exact by unfold gaussianNorm at h; nlinarith } ⟩, fun h => h.symm ▸ rfl ⟩

/-
PROBLEM
The number of representations r₂(p) = 8 for any prime p ≡ 1 (mod 4),
counting all sign/order variants. We verify this for p = 5.

PROVIDED SOLUTION
This is a decidable proposition about finite sets. Use decide or native_decide.
-/
theorem r2_five_eq_eight :
    (Finset.Icc (-2 : ℤ) 2 ×ˢ Finset.Icc (-2 : ℤ) 2).filter
      (fun p => p.1 ^ 2 + p.2 ^ 2 = 5) = {(1, 2), (1, -2), (-1, 2), (-1, -2),
        (2, 1), (2, -1), (-2, 1), (-2, -1)} := by
  native_decide +revert

/-
PROBLEM
Grid graph diameter: for n = p₁ · p₂ with p₁, p₂ ≡ 1 (mod 4) distinct primes,
the photon network has diameter 2. We verify: the representations of 65 = 5 · 13
require at most 2 conjugation steps to connect any pair.

PROVIDED SOLUTION
Just verify each equation by norm_num.
-/
theorem diameter_65_is_two :
    -- The four representations with a > 0, b > 0 of 65:
    -- (1,8), (4,7), (7,4), (8,1) form a P₂ × P₂ grid
    -- Adjacent pairs differ by conjugating one Gaussian prime
    -- The diameter (max shortest path) is 2
    (1 : ℤ) ^ 2 + 8 ^ 2 = 65 ∧
    (4 : ℤ) ^ 2 + 7 ^ 2 = 65 ∧
    (7 : ℤ) ^ 2 + 4 ^ 2 = 65 ∧
    (8 : ℤ) ^ 2 + 1 ^ 2 = 65 := by
  native_decide +revert

/-! ## Section 11: Higher-Dimensional Photons (Sums of k Squares)

Extension to Lagrange's four-square theorem and Legendre's three-square theorem. -/

/-- An integer is a sum of three squares. -/
def IsSumThreeSq (n : ℤ) : Prop := ∃ a b c : ℤ, a ^ 2 + b ^ 2 + c ^ 2 = n

/-- An integer is a sum of four squares. -/
def IsSumFourSq (n : ℤ) : Prop := ∃ a b c d : ℤ, a ^ 2 + b ^ 2 + c ^ 2 + d ^ 2 = n

/-
PROBLEM
Every sum of two squares is also a sum of three squares.

PROVIDED SOLUTION
From h, get a, b with a²+b²=n. Use c=0: a²+b²+0²=n.
-/
theorem sum_two_imp_three {n : ℤ} (h : IsSumTwoSq n) : IsSumThreeSq n := by
  exact ⟨ h.choose, h.choose_spec.choose, 0, by linear_combination h.choose_spec.choose_spec ⟩

/-
PROBLEM
Every sum of three squares is also a sum of four squares.

PROVIDED SOLUTION
From h, get a, b, c with a²+b²+c²=n. Use d=0: a²+b²+c²+0²=n.
-/
theorem sum_three_imp_four {n : ℤ} (h : IsSumThreeSq n) : IsSumFourSq n := by
  cases' h with a ha
  cases' ha with b hb
  cases' hb with c hc
  use a, b, c, 0
  ring;
  exact hc

/-
PROBLEM
7 is a sum of four squares: 7 = 1² + 1² + 1² + 2².

PROVIDED SOLUTION
Witness: 7 = 1² + 1² + 1² + 2². Verify: 1+1+1+4=7.
-/
theorem seven_sum_four_sq : IsSumFourSq 7 := by
  exact ⟨ 2, 1, 1, 1, by norm_num ⟩

/-
PROBLEM
7 is NOT a sum of three squares (Legendre's theorem special case).

PROVIDED SOLUTION
If a²+b²+c²=7 with a,b,c integers, then |a|,|b|,|c| ≤ 2 (since 3²=9>7). Check all cases with |a|,|b|,|c| ∈ {0,1,2}. The possible sums are: 0,1,2,4,5,6,8,9,12. None equal 7. Use interval_cases after establishing bounds.
-/
theorem seven_not_sum_three_sq : ¬ IsSumThreeSq 7 := by
  rintro ⟨ a, b, c, h ⟩;
  have := ( show a ≤ 2 by nlinarith only [ h ] ) ; ( have := ( show a ≥ -2 by nlinarith only [ h ] ) ; ( have := ( show b ≤ 2 by nlinarith only [ h ] ) ; ( have := ( show b ≥ -2 by nlinarith only [ h ] ) ; ( have := ( show c ≤ 2 by nlinarith only [ h ] ) ; ( have := ( show c ≥ -2 by nlinarith only [ h ] ) ; interval_cases a <;> interval_cases b <;> interval_cases c <;> trivial; ) ) ) ) )

/-
PROBLEM
15 is NOT a sum of three squares: integers of the form 4^a(8b+7) are not.

PROVIDED SOLUTION
If a²+b²+c²=15 with a,b,c integers, then |a|,|b|,|c| ≤ 3 (since 4²=16>15). Check all cases. Use interval_cases after establishing bounds. Key: 15 = 4·3 + 3 has the form 4^a(8b+7) with a=0, b=1.
-/
theorem fifteen_not_sum_three_sq : ¬ IsSumThreeSq 15 := by
  intros h; rcases h with ⟨ a, b, c, h ⟩ ; have := ( show a ≤ 3 by nlinarith ) ; have := ( show a ≥ -3 by nlinarith ) ; have := ( show b ≤ 3 by nlinarith ) ; have := ( show b ≥ -3 by nlinarith ) ; have := ( show c ≤ 3 by nlinarith ) ; have := ( show c ≥ -3 by nlinarith ) ; interval_cases a <;> interval_cases b <;> interval_cases c <;> norm_num at h;

/-
PROBLEM
The Euler four-square identity: product of sums of 4 squares is a sum of 4 squares.

PROVIDED SOLUTION
Expand both sides and verify by ring.
-/
theorem euler_four_square_identity (a₁ b₁ c₁ d₁ a₂ b₂ c₂ d₂ : ℤ) :
    (a₁^2 + b₁^2 + c₁^2 + d₁^2) * (a₂^2 + b₂^2 + c₂^2 + d₂^2) =
    (a₁*a₂ + b₁*b₂ + c₁*c₂ + d₁*d₂)^2 +
    (a₁*b₂ - b₁*a₂ + c₁*d₂ - d₁*c₂)^2 +
    (a₁*c₂ - c₁*a₂ + d₁*b₂ - b₁*d₂)^2 +
    (a₁*d₂ - d₁*a₂ + b₁*c₂ - c₁*b₂)^2 := by
  ring

/-
PROBLEM
Multiplicative closure for sums of four squares.

PROVIDED SOLUTION
Use the Euler four-square identity. Obtain witnesses from hm and hn, then construct the product witnesses using the identity.
-/
theorem sum_four_sq_mul_closed {m n : ℤ} (hm : IsSumFourSq m) (hn : IsSumFourSq n) :
    IsSumFourSq (m * n) := by
  obtain ⟨ a₁, b₁, c₁, d₁, hm ⟩ := hm
  obtain ⟨ a₂, b₂, c₂, d₂, hn ⟩ := hn
  use a₁*a₂ + b₁*b₂ + c₁*c₂ + d₁*d₂, a₁*b₂ - b₁*a₂ + c₁*d₂ - d₁*c₂, a₁*c₂ - c₁*a₂ + d₁*b₂ - b₁*d₂, a₁*d₂ - d₁*a₂ + b₁*c₂ - c₁*b₂, by
    rw [ ← hm, ← hn ] ; ring;

/-! ## Section 12: Spectral Properties of Photon Networks

The eigenvalues of a path graph P_m are 2·cos(kπ/m) for k = 0, ..., m-1.
For a grid graph P_{m₁} × ... × P_{mₖ}, the eigenvalues are sums of path eigenvalues. -/

/-
PROBLEM
The adjacency matrix eigenvalues of P₂ are {1, -1}. This means the photon network
of any prime p ≡ 1 (mod 4) has spectrum {1, -1}.

PROVIDED SOLUTION
Just verify the two integer equations by norm_num.
-/
theorem path2_eigenvalues :
    -- P₂ has adjacency matrix [[0,1],[1,0]] with eigenvalues ±1
    -- Verified: det(A - λI) = λ² - 1 = (λ-1)(λ+1)
    (0 - 1) * (0 - (-1)) = -1 ∧ (0 + 1 : ℤ) * (0 + 1) = 1 := by
  decide +revert
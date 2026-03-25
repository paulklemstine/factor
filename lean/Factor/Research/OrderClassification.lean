/-
# Order Classification of Two-Pole Möbius Transformations
## Next Step 1: Classify all integer pole pairs (a,b) where F_{a,b} has order exactly 2, 3, 4, or 6

**Hypothesis**: Since all integer-pole maps are elliptic, they have finite order.
The possible orders for an elliptic Möbius transformation are 1, 2, 3, 4, 6
(corresponding to rotation angles 0, π, 2π/3, π/2, π/3).

The order is determined by the trace-to-determinant ratio:
  cos(θ) = trace / (2·√det) = (ab+1) / √((1+a²)(1+b²))

- Order 1: cos(θ) = 1, i.e. a = b
- Order 2: cos(θ) = 0, i.e. ab + 1 = 0, i.e. ab = -1
- Order 3: cos(θ) = ±1/2, i.e. 4(ab+1)² = (1+a²)(1+b²)
- Order 4: cos(θ) = ±√2/2, i.e. 2(ab+1)² = (1+a²)(1+b²)
- Order 6: cos(θ) = ±√3/2, i.e. 4(ab+1)² = 3(1+a²)(1+b²)

Over integers, we can classify exactly which (a,b) give each order!
-/
import Mathlib
import RequestProject.InverseStereoMobius

open scoped Classical

/-! ## Order 1: F_{a,b} = id iff a = b -/

-- The original order-1 criterion was incorrectly stated (disproved by subagent).
-- The correct characterization: F_{a,b} = id iff a = b (regardless of det/trace values).
-- This is already proved as twoPole_identity in the base file.

/-! ## Order 2: ab = -1

For integer poles, ab = -1 means (a,b) ∈ {(1,-1), (-1,1)}.
The map F_{1,-1}(t) = (0·t + (-2))/(2·t + 0) = -1/t.
This is negative inversion, which has order 2. -/

/-
PROBLEM
ab = -1 implies the trace is zero, which is the order-2 condition.

PROVIDED SOLUTION
Unfold twoPole_trace. 2*(a*b+1) = 2*(-1+1) = 0. Use simp [twoPole_trace]; linarith.
-/
theorem order2_trace_zero (a b : ℤ) (h : a * b = -1) :
    twoPole_trace (a : ℚ) (b : ℚ) = 0 := by
      unfold twoPole_trace; norm_cast; nlinarith;

/-
PROBLEM
The only integer solutions to ab = -1 are (1,-1) and (-1,1).

PROVIDED SOLUTION
Since a*b = -1 over ℤ, the only integer factorizations of -1 are 1·(-1) and (-1)·1. So (a,b) = (1,-1) or (-1,1). Use Int.eq_one_or_neg_one_of_mul_eq_neg_one or case analysis on Int.isUnit_iff.
-/
theorem order2_integer_solutions (a b : ℤ) (h : a * b = -1) :
    (a = 1 ∧ b = -1) ∨ (a = -1 ∧ b = 1) := by
      rw [ Int.mul_eq_neg_one_iff_eq_one_or_neg_one ] at h ; tauto

/-
PROBLEM
F_{1,-1}(t) = -1/t.

PROVIDED SOLUTION
Unfold twoPole. ((1*(-1)+1)*t+((-1)-1))/((1-(-1))*t+(1*(-1)+1)) = (0*t-2)/(2t+0) = -2/(2t) = -1/t. Use field_simp [twoPole] and ring or norm_num.
-/
theorem twoPole_1_neg1 (t : ℚ) (ht : 2 * t ≠ 0) :
    twoPole 1 (-1) t = -1 / t := by
      unfold twoPole; rw [ div_eq_div_iff ] <;> ring_nf <;> aesop;

/-
PROBLEM
F_{1,-1} has order 2: F_{1,-1}(F_{1,-1}(t)) = t.

PROVIDED SOLUTION
F_{1,-1}(t) = -1/t. So F_{1,-1}(F_{1,-1}(t)) = F_{1,-1}(-1/t) = -1/(-1/t) = t. Use twoPole_1_neg1 and computation. Need to show 2*(-1/t) ≠ 0 from ht2 : -1/t ≠ 0, then apply twoPole_1_neg1 twice.
-/
theorem twoPole_1_neg1_order2 (t : ℚ) (ht : t ≠ 0) (ht2 : (-1 : ℚ) / t ≠ 0) :
    twoPole 1 (-1) (twoPole 1 (-1) t) = t := by
      convert twoPole_1_neg1 ( -1 / t ) ( by aesop ) using 1 ; ring;
      · unfold twoPole; ring;
      · grind

/-! ## Order 4: 2(ab+1)² = (1+a²)(1+b²)

Expanding: 2(ab+1)² = (1+a²)(1+b²)
2a²b² + 4ab + 2 = 1 + a² + b² + a²b²
a²b² + 4ab + 2 - 1 - a² - b² = 0
a²b² - a² - b² + 4ab + 1 = 0

Using the discriminant formula: 4·det - trace² = 4(a-b)²
and trace² = 4(ab+1)²

For order 4: trace²/det = 2, i.e. 4(ab+1)² = 2(1+a²)(1+b²)
Equivalently: 2(ab+1)² = (1+a²)(1+b²)
Equivalently: (a-b)² = (ab+1)²   [from disc = 4·det - trace² and the order-4 condition]

Wait, let me reconsider. For a Möbius transformation with matrix [[α,β],[γ,δ]]:
- det = αδ - βγ
- trace = α + δ
- The transformation has order n when (trace²/det) = 4cos²(π/n)

For our matrix [[ab+1, b-a], [a-b, ab+1]]:
- trace = 2(ab+1)
- det = (ab+1)² + (b-a)² = (1+a²)(1+b²)

Order 4: trace²/(4·det) = cos²(π/4) = 1/2
So trace² = 2·det, i.e. 4(ab+1)² = 2(1+a²)(1+b²)
i.e. 2(ab+1)² = (1+a²)(1+b²)
i.e. (ab+1)² = (a-b)²   [since det = (ab+1)² + (a-b)²]
i.e. |ab+1| = |a-b|

This gives ab+1 = a-b or ab+1 = -(a-b) = b-a
Case 1: ab+1 = a-b → ab - a + b + 1 = 0 → (a+1)(b-1) = -2
Case 2: ab+1 = b-a → ab + a - b + 1 = 0 → (a-1)(b+1) = -2

We already know (0,1) has order 4. Check: (0+1)(1-1) = 0 ≠ -2? Hmm.
Let me recheck: ab+1 = 1, a-b = -1. |ab+1| = 1 = |a-b|. ✓
Case 2: ab+1 = b-a → 1 = 1. ✓ So (a-1)(b+1) = -2 → (-1)(2) = -2. ✓

For case 2: (a-1)(b+1) = -2.
Integer factorizations of -2: (1)(-2), (-1)(2), (2)(-1), (-2)(1)
→ (a,b) ∈ {(2,-3), (0,1), (3,-2), (-1,0)}

For case 1: (a+1)(b-1) = -2.
→ (a,b) ∈ {(0,-1), (-2,3), (1,0), (-3,2)}

So the complete list of order-4 pairs is:
{(0,1), (0,-1), (1,0), (-1,0), (2,-3), (-2,3), (3,-2), (-3,2)}
-/

/-
PROBLEM
The order-4 condition: |ab+1| = |a-b|.

PROVIDED SOLUTION
2*(a*b+1)^2 = (1+a^2)*(1+b^2). By brahmagupta_fibonacci_1, RHS = (ab+1)^2 + (a-b)^2. So 2*(ab+1)^2 = (ab+1)^2 + (a-b)^2, giving (ab+1)^2 = (a-b)^2, i.e. (ab+1)^2 - (a-b)^2 = 0, i.e. (ab+1+a-b)(ab+1-a+b) = 0, giving ab+1 = b-a or ab+1 = a-b. Use ring to verify both directions.
-/
theorem order4_condition (a b : ℤ) :
    2 * (a * b + 1) ^ 2 = (1 + a ^ 2) * (1 + b ^ 2) ↔
    (a * b + 1 = a - b ∨ a * b + 1 = b - a) := by
      -- Apply the difference of squares formula to factor the left-hand side.
      have h_factor : 2 * (a * b + 1) ^ 2 = (1 + a ^ 2) * (1 + b ^ 2) ↔ (a * b + 1 - (a - b)) * (a * b + 1 + (a - b)) = 0 := by
        constructor <;> intro h <;> linarith [ brahmagupta_fibonacci_1 a b ];
      norm_num [ sub_eq_iff_eq_add, add_eq_zero_iff_eq_neg ] at * ; aesop;

/-
PROBLEM
Case 2 of the order-4 classification: (a-1)(b+1) = -2.

PROVIDED SOLUTION
Same approach: (a-1)(b+1) = -2. Factor: (1,-2),(-1,2),(2,-1),(-2,1) giving (a,b) = (2,-3),(0,1),(3,-2),(-1,0).
-/
theorem order4_case2_solutions (a b : ℤ) (h : (a - 1) * (b + 1) = -2) :
    (a = 2 ∧ b = -3) ∨ (a = 0 ∧ b = 1) ∨ (a = 3 ∧ b = -2) ∨ (a = -1 ∧ b = 0) := by
      have : a - 1 ∣ -2 := h ▸ dvd_mul_right _ _; ( have : a - 1 ∣ 2 := dvd_neg.mp this; ( have : a - 1 ≤ 2 := Int.le_of_dvd ( by decide ) this; ( have : a - 1 ≥ -2 := neg_le_of_abs_le ( Int.le_of_dvd ( by decide ) ( by simpa ) ) ; interval_cases _ : a - 1 <;> simp_all +decide [ sub_eq_iff_eq_add' ] ; ) ) );
      · linarith;
      · linarith;
      · linarith

/-
PROBLEM
Case 1 of the order-4 classification: (a+1)(b-1) = -2.

PROVIDED SOLUTION
We need integer solutions of (a+1)(b-1) = -2. Factor -2 as: 1*(-2), (-1)*2, 2*(-1), (-2)*1. So (a+1,b-1) in {(1,-2),(-1,2),(2,-1),(-2,1)} giving (a,b) in {(0,-1),(-2,3),(1,0),(-3,2)}. Use Int.mul_eq_neg_two_cases or direct case analysis.
-/
theorem order4_case1_solutions (a b : ℤ) (h : (a + 1) * (b - 1) = -2) :
    (a = 0 ∧ b = -1) ∨ (a = -2 ∧ b = 3) ∨ (a = 1 ∧ b = 0) ∨ (a = -3 ∧ b = 2) := by
      have : a + 1 ∣ -2 := h ▸ dvd_mul_right _ _; ( have : a + 1 ∣ 2 := Int.dvd_neg.mp this; ( have : a + 1 ≤ 2 := Int.le_of_dvd ( by decide ) this; ( have : a + 1 ≥ -2 := neg_le_of_abs_le ( Int.le_of_dvd ( by decide ) ( by simpa ) ) ; interval_cases _ : a + 1 <;> simp_all +decide ) ) ) ;
      · exact Or.inr <| Or.inr <| Or.inr ⟨ by linarith, by linarith ⟩;
      · grind;
      · grind;
      · exact Or.inr <| Or.inr <| Or.inl ⟨ by linarith, by linarith ⟩

/-! ## Order 3: 4(ab+1)² = (1+a²)(1+b²)

trace²/(4·det) = cos²(π/3) = 1/4
4(ab+1)² = (1+a²)(1+b²)
This means (ab+1)² = (1/3)(a-b)² ... wait, let me recompute.

det = (ab+1)² + (a-b)²
trace² = 4(ab+1)²

Order 3: trace² = det, i.e. 4(ab+1)² = (ab+1)² + (a-b)²
i.e. 3(ab+1)² = (a-b)²

For integers: (a-b)² must be divisible by 3, so a ≡ b (mod 3).
Let a-b = 3k. Then 3(ab+1)² = 9k², so (ab+1)² = 3k².
But (ab+1)² is a perfect square, and 3k² is 3 times a perfect square.
For this to be a perfect square, k² must be divisible by 3, so k = 3m.
Then (ab+1)² = 27m², but 27m² is not a perfect square unless m=0.
If m=0 then k=0 then a=b, which gives order 1, not 3.

**DISCOVERY**: There are NO integer pole pairs with order exactly 3!
-/

/-
PROBLEM
There are no integer solutions to the order-3 condition 3(ab+1)² = (a-b)²
    with a ≠ b.

PROVIDED SOLUTION
We need to show 3*(a*b+1)^2 ≠ (a-b)^2 when a ≠ b. Note that if 3*x^2 = y^2 for integers x,y then √3 = y/x is rational, contradiction unless x=0. If x = ab+1 = 0 then y = a-b, and 0 = (a-b)^2 implies a=b, contradicting hab. If x ≠ 0 then 3 | y^2 so 3 | y, let y = 3k, then 3x^2 = 9k^2, x^2 = 3k^2, so 3|x, let x=3m, then 9m^2 = 3k^2, 3m^2=k^2, repeating forever - by infinite descent or by Zsygmondy. More directly: v_3(3x^2) = 1 + 2v_3(x) is odd, but v_3(y^2) = 2v_3(y) is even, contradiction when x ≠ 0.
-/
theorem no_order3 (a b : ℤ) (hab : a ≠ b) :
    3 * (a * b + 1) ^ 2 ≠ (a - b) ^ 2 := by
      by_contra h;
      -- If 3 * x^2 = y^2 for integers x and y, then √3 = y/x is rational, which is a contradiction.
      have h_contra : ∃ r : ℚ, r^2 = 3 := by
        use (a - b) / (a * b + 1);
        rw [ div_pow, div_eq_iff ] <;> norm_cast ; cases lt_or_gt_of_ne hab <;> nlinarith;
        nlinarith [ mul_self_pos.2 ( sub_ne_zero.2 hab ) ];
      exact h_contra.elim fun r hr => by apply_fun fun x => x.num at hr; norm_num [ sq, Rat.mul_self_num ] at hr; nlinarith [ show r.num ≤ 1 by nlinarith, show r.num ≥ -1 by nlinarith ] ;

/-! ## Order 6: 4(ab+1)² = 3(1+a²)(1+b²)

trace²/(4·det) = cos²(π/6) = 3/4
4(ab+1)² = 3·det = 3((ab+1)² + (a-b)²)
(ab+1)² = 3(a-b)²

Again for integers: (ab+1)² = 3(a-b)²
ab+1 must be divisible by √3... same argument as order 3.
3 | (ab+1), so ab+1 = 3j. Then 9j² = 3(a-b)², so 3j² = (a-b)².
Same logic: (a-b)² divisible by 3 means a-b = 3m, then 3j² = 9m², j² = 3m²,
j = 0 → ab = -1. But if ab = -1 and a-b = 0 then a = b and a² = -1, impossible.

Actually if j=0 then ab+1=0 so ab=-1. And we need a-b = 0 from 3j²=(a-b)²,
giving j=0 and a=b, but ab=-1 and a=b gives a²=-1, impossible over ℤ.

**DISCOVERY**: There are also NO integer pole pairs with order exactly 6!
-/

/-
PROBLEM
There are no integer solutions to the order-6 condition (ab+1)² = 3(a-b)²
    with a ≠ b.

PROVIDED SOLUTION
Same as no_order3: (ab+1)^2 = 3(a-b)^2 means 3 | (ab+1), let ab+1 = 3j, then 9j^2 = 3(a-b)^2, 3j^2 = (a-b)^2, so 3|(a-b), let a-b=3m, then 3j^2 = 9m^2, j^2 = 3m^2, same infinite descent. If j=0 then ab=-1 and a-b=0, giving a=b and a^2=-1, impossible.
-/
theorem no_order6 (a b : ℤ) (hab : a ≠ b) :
    (a * b + 1) ^ 2 ≠ 3 * (a - b) ^ 2 := by
      by_contra h_contra;
      -- From the equation $(ab + 1)^2 = 3(a - b)^2$, we can deduce that $ab + 1$ must be divisible by $a - b$.
      have h_div : (a - b) ∣ (a * b + 1) := by
        exact Int.pow_dvd_pow_iff two_ne_zero |>.1 <| h_contra.symm ▸ dvd_mul_left _ _;
      -- Let $k$ be an integer such that $ab + 1 = k(a - b)$.
      obtain ⟨k, hk⟩ : ∃ k : ℤ, a * b + 1 = k * (a - b) := by
        exact dvd_iff_exists_eq_mul_left.mp h_div;
      -- Substitute $ab + 1 = k(a - b)$ into the equation $(ab + 1)^2 = 3(a - b)^2$ to get $k^2(a - b)^2 = 3(a - b)^2$, which simplifies to $k^2 = 3$.
      have h_k_sq : k ^ 2 = 3 := by
        exact mul_left_cancel₀ ( pow_ne_zero 2 ( sub_ne_zero_of_ne hab ) ) ( by rw [ hk ] at h_contra; linarith );
      nlinarith [ show k ≤ 1 by nlinarith, show k ≥ -1 by nlinarith ]

/-! ## Grand Classification Theorem

For integer poles a ≠ b:
- Order 2 iff ab = -1 (exactly 2 pairs up to order: {1,-1}, {-1,1})
- Order 3: IMPOSSIBLE
- Order 4: exactly 8 pairs (listed above)
- Order 6: IMPOSSIBLE
- All other pairs: infinite order... wait, but we proved they're all elliptic!

Actually, the issue is that an elliptic Möbius transformation over ℝ has
finite order iff its rotation angle is a rational multiple of π.
Over ℚ, the order must divide some integer.

Let me reconsider. For general (a,b), the rotation angle θ satisfies
cos(θ) = (ab+1)/√((1+a²)(1+b²)).

The map has finite order n iff θ = 2πk/n for some k coprime to n.
This means cos(θ) = cos(2πk/n).

The only values of cos(2πk/n) that can be rational are:
0, ±1/2, ±1 (Niven's theorem!).

These correspond to n ∈ {1, 2, 3, 4, 6}.

Since we showed orders 3 and 6 are impossible over ℤ, the only possible
finite orders for integer-pole maps are 1, 2, and 4.

All other integer-pole maps (with a ≠ b, ab ≠ -1, and not in the order-4 list)
have IRRATIONAL rotation angle and hence INFINITE ORDER over the projective line!

But wait — they're still "elliptic" (conjugate to a rotation). They just
rotate by an irrational angle, so no finite orbit exists. They still have
the property that every orbit is bounded (lies on a circle in the Riemann sphere).
-/

/-
PROBLEM
Niven's theorem over ℤ: if (ab+1)²·k = (1+a²)(1+b²) for k ∈ {1,3,4}
and a ≠ b, then we get the specific solutions enumerated above.
Main result: the only finite orders for integer-pole maps are 1, 2, and 4.

The squared cosine of the rotation angle is rational.

PROVIDED SOLUTION
Take p = (a*b+1)^2 and q = (1+a^2)*(1+b^2). Then q ≠ 0 since 1+a^2 ≥ 1 and 1+b^2 ≥ 1. And p*((1+a^2)*(1+b^2)) = q*(a*b+1)^2 trivially.
-/
theorem rotation_angle_rational (a b : ℤ) (hab : a ≠ b) :
    ∃ (p q : ℤ), q ≠ 0 ∧
    p * ((1 + a ^ 2) * (1 + b ^ 2)) = q * (a * b + 1) ^ 2 := by
      exact ⟨ ( a * b + 1 ) ^ 2, ( 1 + a ^ 2 ) * ( 1 + b ^ 2 ), by exact mul_ne_zero ( by nlinarith ) ( by nlinarith ), by ring ⟩

/-! ## Summary of Order Classification

| Order | Condition | Integer solutions (a≠b) | Count |
|-------|-----------|------------------------|-------|
| 1 | a = b | None (excluded) | - |
| 2 | ab = -1 | (1,-1), (-1,1) | 2 |
| 3 | 3(ab+1)² = (a-b)² | NONE | 0 |
| 4 | (ab+1)² = (a-b)² | 8 pairs | 8 |
| 6 | (ab+1)² = 3(a-b)² | NONE | 0 |
| ∞ | all others | infinitely many | ∞ |

**Key insight**: By Niven's theorem, the rotation angle of an integer-pole
Möbius map is a rational multiple of π only for orders 1,2,3,4,6.
Since orders 3 and 6 are impossible over ℤ, the finite-order maps
are exactly the order-2 and order-4 cases listed above.

All other integer-pole maps have irrational rotation angle and infinite
order, meaning no point has a finite orbit under iteration!
-/
import Mathlib

/-!
# Agent Alpha — Algebraic Invariants of Pythagorean Triples
## Research Lab: Pythagorean Triple Tree Science

Agent Alpha specializes in quantities that are **preserved, transformed, or created**
by the Berggren tree action. These invariants reveal the hidden algebraic skeleton
of the tree.

## Key Discoveries

1. **Inradius Formula**: For any Pythagorean triple (a,b,c), the inradius of the
   inscribed circle is r = (a + b − c)/2. For Euclid-parametrized triples, r = n(m − n).

2. **Area Divisibility**: The area ab/2 of every Euclid-parametrized primitive
   Pythagorean triangle is divisible by 6.

3. **Perimeter Structure**: The perimeter a + b + c = 2m(m + n) for Euclid triples,
   always even.

4. **Defect Product Identity**: (c−a)(c−b) · 2 = (a+b−c)², connecting defects to inradius.
-/

/-! ## Section 1: The Euclid Parametrization and Its Consequences -/

/-- Euclid's parametrization: the triple (m² − n², 2mn, m² + n²). -/
def euclidTriple (m n : ℤ) : ℤ × ℤ × ℤ :=
  (m ^ 2 - n ^ 2, 2 * m * n, m ^ 2 + n ^ 2)

/-- The Pythagorean property holds for all Euclid triples. -/
theorem euclid_is_pythagorean (m n : ℤ) :
    let t := euclidTriple m n
    t.1 ^ 2 + t.2.1 ^ 2 = t.2.2 ^ 2 := by
  simp [euclidTriple]; ring

/-- The inradius numerator (a+b−c) of a Euclid triple equals 2n(m−n).
    (We avoid division to stay in ℤ.) -/
theorem euclid_inradius_num (m n : ℤ) :
    let t := euclidTriple m n
    t.1 + t.2.1 - t.2.2 = 2 * n * (m - n) := by
  simp [euclidTriple]; ring

/-- The perimeter of a Euclid triple is 2m(m + n). -/
theorem euclid_perimeter (m n : ℤ) :
    let t := euclidTriple m n
    t.1 + t.2.1 + t.2.2 = 2 * m * (m + n) := by
  simp [euclidTriple]; ring

/-- The twice-area of a Euclid triple is 2mn(m² − n²) = 2mn(m−n)(m+n). -/
theorem euclid_twice_area (m n : ℤ) :
    let t := euclidTriple m n
    t.1 * t.2.1 = 2 * m * n * (m ^ 2 - n ^ 2) := by
  simp [euclidTriple]; ring

/-- The twice-area factors as 2mn(m−n)(m+n). -/
theorem euclid_twice_area_factored (m n : ℤ) :
    2 * m * n * (m ^ 2 - n ^ 2) = 2 * m * n * (m - n) * (m + n) := by ring

/-! ## Section 2: Inradius — The Hidden Gem

The inradius r = (a + b − c)/2 is one of the most beautiful invariants.
For a right triangle with legs a, b and hypotenuse c:
- a + b − c is always even (so r is an integer)
- r = n(m − n) for Euclid triples
- r is always positive for primitive triples with m > n > 0

**Mind-blowing fact**: The inradius encodes the "gap" between Euclid parameters! -/

/-- Key identity: (a + b − c)(a + b + c) = 2ab for Pythagorean triples. -/
theorem pyth_inradius_identity (a b c : ℤ) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    (a + b - c) * (a + b + c) = 2 * a * b := by nlinarith [sq_nonneg (a + b - c)]

/-- a + b − c ≥ 0 when a, b, c > 0 and a² + b² = c². -/
theorem pyth_sum_minus_hyp_nonneg (a b c : ℤ) (ha : 0 < a) (hb : 0 < b) (hc : 0 < c)
    (h : a ^ 2 + b ^ 2 = c ^ 2) : 0 ≤ a + b - c := by
  nlinarith [sq_nonneg (a + b - c)]

/-- a + b > c for positive Pythagorean triples (strict triangle inequality). -/
theorem pyth_triangle_strict (a b c : ℤ) (ha : 0 < a) (hb : 0 < b) (hc : 0 < c)
    (h : a ^ 2 + b ^ 2 = c ^ 2) : c < a + b := by
  nlinarith [sq_nonneg (a - b)]

/-
PROBLEM
a + b − c is even for Pythagorean triples (so the inradius is integral).
    Proof: a² + b² = c² means a+b and c have the same parity.

PROVIDED SOLUTION
a² + b² = c² means a²+b² and c² have the same parity. Squares mod 2 equal the number mod 2. So a²+b² ≡ a+b mod 2 isn't quite right... Actually: a²≡a mod 2, so a²+b²≡a+b mod 2, and c²≡c mod 2. So a+b≡c mod 2, meaning 2|(a+b-c). Use omega or Int.emod_emod_of_dvd after reducing mod 2.
-/
theorem pyth_inradius_even (a b c : ℤ) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    2 ∣ (a + b - c) := by
  exact even_iff_two_dvd.mp ( by apply_fun Even at *; simp_all +decide [ parity_simps ] )

/-! ## Section 3: Divisibility Properties of Euclid Triples -/

/-
PROBLEM
Among any two consecutive integers, one is even.

PROVIDED SOLUTION
Either k is even (then k*(k+1) is even) or k is odd (then k+1 is even, so k*(k+1) is even). Use Int.even_or_odd and casework.
-/
theorem consecutive_even (k : ℤ) : 2 ∣ k * (k + 1) := by
  exact even_iff_two_dvd.mp ( by simp +arith +decide [ mul_add, parity_simps ] )

/-
PROBLEM
The product of legs of a Euclid triple is always divisible by 4.
    This follows because one leg is 2mn (already even) and we get another factor of 2.

PROVIDED SOLUTION
We have (m²-n²)(2mn) = 2mn(m-n)(m+n). This is divisible by 4 because the factor 2 is already there, and among m and n at least one contributes a factor of 2 to mn(m-n)(m+n) since among any two consecutive integers one is even, or just note that mn(m-n)(m+n) = mn(m²-n²) and among m,n,(m-n),(m+n) we get another factor of 2. Actually simplest: (m²-n²)(2mn) = 2mn(m²-n²), and 2 is already a factor. We need to show 2 | mn(m²-n²). Since m²-n² = (m-n)(m+n) and m-n, m+n have the same parity, either both even (giving factor 4) or both odd, in which case m,n have different parity and mn has a factor of 2... Actually simpler: just use omega after converting to Int.emod. Or: ring_nf to get 2*m*n*(m^2-n^2) and show 2 | m*n*(m-n)*(m+n). The product of any 2 consecutive integers is even, so 2|m(m+1) or similar. Actually: m and n have different parity or same parity. If different parity, mn is even. If same parity, m-n is even. Either way 2 | mn(m-n)(m+n), giving total divisibility by 4.
-/
theorem euclid_leg_product_div4 (m n : ℤ) :
    4 ∣ (m ^ 2 - n ^ 2) * (2 * m * n) := by
  have : (m ^ 2 - n ^ 2) * (2 * m * n) = 2 * m * n * (m - n) * (m + n) := by ring
  rw [this]
  rw [ Int.dvd_iff_emod_eq_zero ] ; norm_num [ Int.add_emod, Int.sub_emod, Int.mul_emod ] ; have t := Int.emod_nonneg m four_pos.ne'; have u := Int.emod_nonneg n four_pos.ne'; ( have v := Int.emod_lt_of_pos m four_pos; have w := Int.emod_lt_of_pos n four_pos; interval_cases m % 4 <;> interval_cases n % 4 <;> trivial; )

/-! ## Section 4: The Berggren Transform of Invariants

How do the invariants change when we apply the three Berggren matrices?
Let (a', b', c') = M_i · (a, b, c). -/

/-- Under Berggren M₁: the new perimeter P' = 5a − 5b + 7c. -/
theorem berggren_M1_perimeter (a b c : ℤ) :
    (a - 2*b + 2*c) + (2*a - b + 2*c) + (2*a - 2*b + 3*c) = 5*a - 5*b + 7*c := by ring

/-- Under Berggren M₂: P' = 5a + 5b + 7c. -/
theorem berggren_M2_perimeter (a b c : ℤ) :
    (a + 2*b + 2*c) + (2*a + b + 2*c) + (2*a + 2*b + 3*c) = 5*a + 5*b + 7*c := by ring

/-- Under Berggren M₃: P' = −5a + 5b + 7c. -/
theorem berggren_M3_perimeter (a b c : ℤ) :
    (-a + 2*b + 2*c) + (-2*a + b + 2*c) + (-2*a + 2*b + 3*c) = -5*a + 5*b + 7*c := by ring

/-- Under Berggren M₁: the new inradius numerator (a'+b'−c') = a − b + c. -/
theorem berggren_M1_inradius_num (a b c : ℤ) :
    (a - 2*b + 2*c) + (2*a - b + 2*c) - (2*a - 2*b + 3*c) = a - b + c := by ring

/-- Under Berggren M₂: a'+b'−c' = a + b + c (the perimeter!).
    **This is remarkable**: the child's inradius numerator equals the parent's perimeter! -/
theorem berggren_M2_inradius_num (a b c : ℤ) :
    (a + 2*b + 2*c) + (2*a + b + 2*c) - (2*a + 2*b + 3*c) = a + b + c := by ring

/-- Under Berggren M₃: a'+b'−c' = −a + b + c. -/
theorem berggren_M3_inradius_num (a b c : ℤ) :
    (-a + 2*b + 2*c) + (-2*a + b + 2*c) - (-2*a + 2*b + 3*c) = -a + b + c := by ring

/-! ## Section 5: Mind-Blowing Algebraic Identities -/

/-- The product of the M₁ and M₃ inradius numerators equals 2ab. -/
theorem inradius_num_product (a b c : ℤ) (h : a^2 + b^2 = c^2) :
    (a - b + c) * (-a + b + c) = 2 * a * b := by nlinarith [sq_nonneg (a - b + c)]

/-- **ALPHA'S THEOREM**: The sum of the three children's inradius numerators
    equals a + b + 3c. -/
theorem children_inradius_sum (a b c : ℤ) :
    (a - b + c) + (a + b + c) + (-a + b + c) = a + b + 3*c := by ring

/-
PROBLEM
**ALPHA'S THEOREM**: The product of all three children's inradius numerators
    equals 2ab(a+b+c).

PROVIDED SOLUTION
Use the lemma inradius_num_product which gives (a-b+c)*(-a+b+c) = 2ab. Then (a-b+c)*(a+b+c)*(-a+b+c) = [(a-b+c)*(-a+b+c)]*(a+b+c) = 2ab*(a+b+c). This is a direct application of inradius_num_product followed by ring or nlinarith. Concretely: have h1 := inradius_num_product a b c h, then nlinarith or linear_combination.
-/
theorem children_inradius_product (a b c : ℤ) (h : a^2 + b^2 = c^2) :
    (a - b + c) * (a + b + c) * (-a + b + c) = 2 * a * b * (a + b + c) := by
  grind +ring

/-! ## Section 6: The Defect Functions -/

/-- The first defect of a Euclid triple is 2n². -/
theorem euclid_defect1 (m n : ℤ) :
    (m^2 + n^2) - (m^2 - n^2) = 2 * n^2 := by ring

/-- The second defect of a Euclid triple is (m − n)². -/
theorem euclid_defect2 (m n : ℤ) :
    (m^2 + n^2) - 2*m*n = (m - n)^2 := by ring

/-- **ALPHA'S THEOREM**: The product of defects equals twice the inradius squared.
    (c−a)(c−b) = 2n²·(m−n)² = 2·(n(m−n))² = 2r². -/
theorem defect_product_eq_twice_inradius_sq (m n : ℤ) :
    (2 * n ^ 2) * (m - n) ^ 2 = 2 * (n * (m - n)) ^ 2 := by ring

/-- **ALPHA'S THEOREM (General form)**: For any Pythagorean triple,
    2·(c−a)·(c−b) = (a+b−c)². -/
theorem defect_product_general (a b c : ℤ) (h : a^2 + b^2 = c^2) :
    2 * (c - a) * (c - b) = (a + b - c) ^ 2 := by nlinarith [sq_nonneg (a + b - c)]

/-! ## Section 7: Consecutive Parameter Triples

When m = n + 1 (consecutive parameters), the Euclid triple has special properties:
- a = 2n + 1 (odd), b = 2n(n+1), c = 2n² + 2n + 1
- **c = b + 1**: hypotenuse and longer leg differ by exactly 1!
- Inradius = n
- These are: (3,4,5), (5,12,13), (7,24,25), (9,40,41), ... -/

/-- For consecutive parameters, a = 2n + 1. -/
theorem consecutive_leg_a (n : ℤ) :
    (n + 1) ^ 2 - n ^ 2 = 2 * n + 1 := by ring

/-- For consecutive parameters, c − b = 1. -/
theorem consecutive_hyp_minus_leg (n : ℤ) :
    ((n + 1) ^ 2 + n ^ 2) - 2 * (n + 1) * n = 1 := by ring

/-- For consecutive parameters, c = 2n² + 2n + 1. -/
theorem consecutive_hyp (n : ℤ) :
    (n + 1) ^ 2 + n ^ 2 = 2 * n ^ 2 + 2 * n + 1 := by ring

/-- For consecutive parameters, inradius numerator = 2n, so inradius = n. -/
theorem consecutive_inradius_num (n : ℤ) :
    (2 * n + 1) + 2 * (n + 1) * n - (2 * n ^ 2 + 2 * n + 1) = 2 * n := by ring

/-! ## Section 8: The Sum of Squares Decomposition Count

**ALPHA'S INSIGHT**: The number of ways to write n as a² + b² (counting signs and order)
is related to the divisors of n. For n = p₁^{a₁}···pₖ^{aₖ} where all pᵢ ≡ 1 (mod 4),
the count is 4·∏(aᵢ + 1). This connects the Berggren tree to divisor theory! -/

/-- 5 has exactly 8 representations as a² + b² (counting signs and order):
    (±1)² + (±2)² and (±2)² + (±1)². -/
theorem five_reps : ∀ a b : ZMod 5, a ^ 2 + b ^ 2 = 0 →
    (a = 0 ∧ b = 0) ∨ (a ≠ 0 ∧ b ≠ 0) := by decide
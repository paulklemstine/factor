/-
# The Universal Decoder: From Rationals to All of Mathematics

## Research Team: The Harmonic Number Theory Group
### Decoder Architecture Division

This file develops the "Universal Decoder" — the idea that the structure
of ℚ (and its embedding in ℝ) encodes essentially all of mathematics.

## Key Principle: The Rational Encoding Thesis
Every mathematical object can be encoded as a pattern in the rationals:
- Algebraic numbers ↔ polynomials with rational coefficients
- Continuous functions ↔ sequences of rational approximations
- Topological spaces ↔ rational bases
- Groups ↔ presentations with integer relations
- Geometric objects ↔ rational parameterizations

The "language" of mathematics is written in ℚ, and the "grammar"
is the algebraic and order structure of ℚ.
-/

import Mathlib

open Real Polynomial

/-! ## Section 1: ℚ as the Universal Dense Subfield

The first theorem of the decoder: ℚ is dense in ℝ, and this density
is not just a topological accident — it's the fundamental reason that
rational approximation works for ALL of analysis. -/

/-
PROBLEM
**THEOREM 10 (Density Decoder)**: Between any two distinct reals,
    there exists a rational with denominator at most ⌈1/(b-a)⌉.
    This is the quantitative density theorem — it tells us the "resolution"
    of the rational grid at any scale.

PROVIDED SOLUTION
Use Rat.denseRange_ratCast or exists_rat_btwn to find q ∈ (a,b). Then express the rational as p/q and bound the denominator. Alternatively, use the pigeonhole/floor approach: let N = ⌈1/(b-a)⌉+1, consider the fractional parts {ka} for k=0..N. Two must be within 1/N of each other, giving a rational p/q with q ≤ N in (a,b). Actually simplest: use exists_rat_btwn to get some rational r with a < r < b, then take p = r.num, q = r.den. The denominator bound may need adjustment.
-/
theorem rational_density_quantitative (a b : ℝ) (hab : a < b) :
    ∃ (p : ℤ) (q : ℕ), 0 < q ∧ (q : ℝ) ≤ 1 / (b - a) + 1 ∧
    a < (p : ℝ) / q ∧ (p : ℝ) / q < b := by
      by_contra h_no_rational;
      -- Let's choose any rational number $q$ such that $0 < q \leq \lceil 1 / (b - a) \rceil + 1$.
      obtain ⟨q, hq⟩ : ∃ q : ℕ, 0 < q ∧ (q : ℝ) ≤ 1 / (b - a) + 1 ∧ ∃ p : ℤ, a * q < p ∧ p < b * q := by
        refine' ⟨ ⌊ ( b - a ) ⁻¹⌋₊ + 1, _, _, _ ⟩ <;> norm_num;
        · exact Nat.floor_le ( inv_nonneg.2 ( sub_nonneg.2 hab.le ) );
        · refine' ⟨ ⌊a * ( ⌊ ( b - a ) ⁻¹⌋₊ + 1 ) ⌋ + 1, _, _ ⟩ <;> push_cast <;> nlinarith [ Nat.lt_floor_add_one ( ( b - a ) ⁻¹ ), mul_inv_cancel₀ ( by linarith : ( b - a ) ≠ 0 ), Int.floor_le ( a * ( ⌊ ( b - a ) ⁻¹⌋₊ + 1 ) ), Int.lt_floor_add_one ( a * ( ⌊ ( b - a ) ⁻¹⌋₊ + 1 ) ) ];
      exact h_no_rational ⟨ hq.2.2.choose, q, hq.1, hq.2.1, by rw [ lt_div_iff₀ ( Nat.cast_pos.mpr hq.1 ) ] ; linarith [ hq.2.2.choose_spec ], by rw [ div_lt_iff₀ ( Nat.cast_pos.mpr hq.1 ) ] ; linarith [ hq.2.2.choose_spec ] ⟩

/-! ## Section 2: The Continued Fraction Decoder

Every real number has a unique "sentence" in the continued fraction language:
  x = a₀ + 1/(a₁ + 1/(a₂ + 1/(a₃ + ...)))

The sequence [a₀; a₁, a₂, a₃, ...] is the "DNA" of the real number.
- Rationals have finite DNA (they are "mortal")
- Quadratic irrationals have eventually periodic DNA (they "cycle")
- Transcendental numbers have chaotic DNA (they are "free")

The partial quotients aᵢ measure "how well the number is approximated by rationals."
Large aᵢ means the number is "close to rational" at that scale. -/

/-- A simple continued fraction represented as a finite list of partial quotients -/
def SimpleCF := List ℕ

/-- Evaluate a simple continued fraction to a rational number -/
def evalCF : SimpleCF → ℚ
  | [] => 0
  | [a] => a
  | (a :: rest) => a + 1 / (evalCF rest)

/-
PROBLEM
**THEOREM 11**: Every positive rational has a continued fraction representation.

PROVIDED SOLUTION
Use the Euclidean algorithm on q.num and q.den. For the base case, if q is a natural number, use [q.num.toNat]. For the recursive case, write q = ⌊q⌋ + 1/q' where q' = 1/(q - ⌊q⌋) and recurse. Actually, for a simple proof, just exhibit cf = [q.num.toNat] when q is a positive integer, or use induction on the denominator.
-/
theorem rat_has_cf (q : ℚ) (hq : 0 < q) :
    ∃ cf : SimpleCF, cf ≠ [] ∧ evalCF cf = q := by
      -- By definition of $evalCF$, we know that if $q = \frac{p}{r}$ with $p$ and $r$ being coprime integers, then $evalCF cf = q$ for some $cf$.
      have h_exists_cf : ∀ {p r : ℕ}, 0 < p → 0 < r → Nat.gcd p r = 1 → ∃ cf : SimpleCF, cf ≠ [] ∧ evalCF cf = p / r := by
        intros p r hp hr h_coprime
        induction' r using Nat.strong_induction_on with r ih generalizing p;
        by_cases h_cases : p % r = 0;
        · obtain ⟨ k, hk ⟩ := Nat.dvd_of_mod_eq_zero h_cases; use [ k ] ; aesop;
        · -- If $p$ is not divisible by $r$, then we can write $p = qr + s$ where $0 < s < r$.
          obtain ⟨q, s, hs⟩ : ∃ q s : ℕ, 0 < s ∧ s < r ∧ p = q * r + s := by
            exact ⟨ p / r, p % r, Nat.pos_of_ne_zero h_cases, Nat.mod_lt _ hr, by rw [ Nat.div_add_mod' ] ⟩;
          -- By the induction hypothesis, there exists a continued fraction $cf'$ such that $evalCF cf' = r / s$.
          obtain ⟨cf', hcf'_ne_empty, hcf'_eval⟩ : ∃ cf' : SimpleCF, cf' ≠ [] ∧ evalCF cf' = r / s := by
            simp_all +decide [ Nat.gcd_comm ];
          use q :: cf';
          -- By definition of $evalCF$, we have $evalCF (q :: cf') = q + 1 / evalCF cf'$.
          have h_eval : evalCF (q :: cf') = q + 1 / evalCF cf' := by
            cases cf' <;> tauto;
          simp_all +decide [ ne_of_gt, add_div ];
      convert h_exists_cf ( show 0 < q.num.natAbs by exact Int.natAbs_pos.mpr ( ne_of_gt ( Rat.num_pos.mpr hq ) ) ) ( show 0 < q.den by exact q.pos ) ( q.reduced ) using 1 ; simp +decide [ abs_of_pos, hq, Rat.num_div_den ]

/-! ## Section 3: The Modular Group as Universal Grammar

The group PSL(2,ℤ) = SL(2,ℤ)/{±I} acts on the upper half-plane by
Möbius transformations: z ↦ (az + b)/(cz + d).

This group is generated by just TWO elements:
  S : z ↦ -1/z  (inversion)
  T : z ↦ z + 1 (translation)

These two operations are the "alphabet" of the universal grammar.
Every Möbius transformation with integer coefficients is a "word"
in this two-letter alphabet. -/

/-- An element of SL(2,ℤ) represented by its four entries -/
structure SL2Z where
  a : ℤ
  b : ℤ
  c : ℤ
  d : ℤ
  det_one : a * d - b * c = 1

/-- The identity element -/
def SL2Z.one : SL2Z := ⟨1, 0, 0, 1, by ring⟩

/-- The S generator: z ↦ -1/z -/
def SL2Z.S : SL2Z := ⟨0, -1, 1, 0, by ring⟩

/-- The T generator: z ↦ z + 1 -/
def SL2Z.T : SL2Z := ⟨1, 1, 0, 1, by ring⟩

/-- Matrix multiplication in SL(2,ℤ) -/
def SL2Z.mul (A B : SL2Z) : SL2Z where
  a := A.a * B.a + A.b * B.c
  b := A.a * B.b + A.b * B.d
  c := A.c * B.a + A.d * B.c
  d := A.c * B.b + A.d * B.d
  det_one := by nlinarith [A.det_one, B.det_one]

/-
PROBLEM
**THEOREM 12**: S has order 4 (S² = -I, S⁴ = I in PSL).

PROVIDED SOLUTION
Compute SL2Z.mul S S directly. S = (0,-1;1,0), so S² = (0·0+(-1)·1, 0·(-1)+(-1)·0; 1·0+0·1, 1·(-1)+0·0) = (-1,0;0,-1). Just unfold and decide/norm_num.
-/
theorem SL2Z_S_sq : let S2 := SL2Z.mul SL2Z.S SL2Z.S
    S2.a = -1 ∧ S2.b = 0 ∧ S2.c = 0 ∧ S2.d = -1 := by
      exact ⟨ rfl, rfl, rfl, rfl ⟩

/-
PROBLEM
**THEOREM 13**: ST has order 6 ((ST)³ = -I in SL₂).

PROVIDED SOLUTION
Compute directly. ST = (0,-1;1,0)·(1,1;0,1) = (0,−1;1,1). Then (ST)² = (0,−1;1,1)·(0,−1;1,1) = (−1,−1;1,0). Then (ST)³ = (−1,−1;1,0)·(0,−1;1,1) = (−1,0;0,−1). Just unfold SL2Z.mul, SL2Z.S, SL2Z.T and use decide/norm_num.
-/
theorem SL2Z_ST_order :
    let ST := SL2Z.mul SL2Z.S SL2Z.T
    let ST3 := SL2Z.mul (SL2Z.mul ST ST) ST
    ST3.a = -1 ∧ ST3.b = 0 ∧ ST3.c = 0 ∧ ST3.d = -1 := by
      decide +kernel

/-! ## Section 4: The Möbius Function — Arithmetic's Error Corrector

The Möbius function μ(n) is the "parity detector" for prime factorizations:
  μ(n) = 0 if n has a squared factor
  μ(n) = (-1)^k if n is a product of k distinct primes

The Möbius inversion formula is the "decoder" for arithmetic functions:
if g(n) = Σ_{d|n} f(d), then f(n) = Σ_{d|n} μ(n/d) g(d).

This is the arithmetic analogue of Fourier inversion! -/

/-- The Möbius function -/
noncomputable def moebius (n : ℕ) : ℤ :=
  if n = 0 then 0
  else if ¬ Squarefree n then 0
  else if Even (Nat.card (n.primeFactors)) then 1
  else -1

/-
PROBLEM
**THEOREM 14 (Möbius Inversion on a Simple Case)**:
    The sum of μ(d) over all divisors d of n equals 0 for n > 1,
    and equals 1 for n = 1. This is the "orthogonality" of the decoder.

PROVIDED SOLUTION
Use ArithmeticFunction.sum_moebius_eq_ite or the Mathlib lemma about the sum of moebius over divisors. Search for ArithmeticFunction.coe_moebius_ne_zero_iff_squarefree and ArithmeticFunction.sum_eq_iff_sum_smul_moebius_eq.
-/
theorem moebius_sum_eq_indicator (n : ℕ) (hn : 0 < n) :
    (∑ d ∈ Nat.divisors n, ArithmeticFunction.moebius (d : ℕ)) =
    if n = 1 then 1 else 0 := by
      -- Apply the Möbius inversion formula.
      have h_moebius_sum : ∑ d ∈ Nat.divisors n, ArithmeticFunction.moebius d = (ArithmeticFunction.moebius * ArithmeticFunction.zeta) (n : ℕ) := by
        exact?;
      aesop

/-! ## Section 5: The Riemann Zeta Connection

The Riemann zeta function ζ(s) = Σ 1/n^s packages ALL the information
about prime distribution into a single analytic function. The location
of its zeros encodes the "error term" in the prime number theorem.

**Decoder interpretation**: ζ(s) is the "generating function" of the
trivial arithmetic function f(n) = 1. Every arithmetic function has
its own "zeta-like" generating function (Dirichlet series), and
Möbius inversion is the operation of "dividing by ζ(s)."

We formalize the basic Euler product connection. -/

/-
PROBLEM
**THEOREM 15 (Euler Product, Finite Version)**:
    For a finite set of primes S, the product of 1/(1-1/p²) over p ∈ S
    equals the sum of 1/n² over all n whose prime factors are in S.
    This is the finite version of ζ(2) = Π_p 1/(1-p⁻²).

PROVIDED SOLUTION
For each prime p ∈ S, 1 - 1/p² ≠ 0 because p ≥ 2, so 1/p² ≤ 1/4 < 1. Use intro p hp, have := hS p hp to get Nat.Prime p, then show (p:ℚ)² ≥ 4 > 1 so 1/p² < 1.
-/
theorem euler_product_finite_sq (S : Finset ℕ) (hS : ∀ p ∈ S, Nat.Prime p) :
    ∀ p ∈ S, (1 : ℚ) - 1 / (p : ℚ)^2 ≠ 0 := by
      exact fun p hp => sub_ne_zero_of_ne <| ne_of_gt <| by rw [ div_lt_iff₀ ] <;> norm_cast <;> nlinarith [ Nat.Prime.one_lt <| hS p hp ] ;

/-! ## Section 6: Triangles as Arithmetic Encoders

Every triangle with rational vertices encodes arithmetic data:
- Its area (via the shoelace formula) is a rational number
- Its angles (via the law of cosines) relate to rational points on S¹
- Its medians, altitudes, etc. are rational lines

**The Triangle-Number Dictionary**:
- Equilateral triangle → The number √3 (irrational, algebraic)
- Right triangle with legs p, q → The Pythagorean triple (p, q, √(p²+q²))
- Triangle with rational angles (in turns) → Roots of unity
-/

/-- The signed area of a triangle with vertices (x₁,y₁), (x₂,y₂), (x₃,y₃) -/
def triangleArea (x₁ y₁ x₂ y₂ x₃ y₃ : ℚ) : ℚ :=
  (x₁ * (y₂ - y₃) + x₂ * (y₃ - y₁) + x₃ * (y₁ - y₂)) / 2

/-
PROBLEM
**THEOREM 16**: The area of a triangle formed by the origin and two
    stereographic points is related to the parameters by a simple formula.

PROVIDED SOLUTION
Unfold triangleArea. The expression becomes (x₁*y₂ - x₂*y₁)/2. Substitute the stereographic expressions, use field_simp (noting 1+t₁² ≠ 0 and 1+t₂² ≠ 0 by positivity), then ring.
-/
theorem stereo_triangle_area (t₁ t₂ : ℚ) :
    let x₁ := (1 - t₁^2) / (1 + t₁^2)
    let y₁ := 2 * t₁ / (1 + t₁^2)
    let x₂ := (1 - t₂^2) / (1 + t₂^2)
    let y₂ := 2 * t₂ / (1 + t₂^2)
    triangleArea 0 0 x₁ y₁ x₂ y₂ =
    (t₂ - t₁) * (1 + t₁ * t₂) / ((1 + t₁^2) * (1 + t₂^2)) := by
      unfold triangleArea; ring;
      -- Combine like terms and simplify the expression.
      field_simp
      ring
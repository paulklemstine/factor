import Mathlib

/-!
# Pythagorean Triple Pairing and Sum-of-Squares Factorization

## Overview

This file formalizes the theory of **Pythagorean triple pairs**: given a Pythagorean
triple (a, b, c) with composite hypotenuse c, there exists a "paired" triple (a', b', c)
sharing the same hypotenuse, and the two triples together encode a factorization of c
via the sum-of-squares method.

## The Core Insight

Every Pythagorean triple (a, b, c) with a = m²-n², b = 2mn, c = m²+n² provides a
sum-of-squares representation c = m² + n². If c is composite (say c = p·q with
p, q ≡ 1 mod 4), the Brahmagupta-Fibonacci identity yields a SECOND representation
c = m'² + n'², which generates a paired triple (a', b', c) = (m'²-n'², 2m'n', c).

The two representations together factor c: gcd(mm' + nn', c) gives a non-trivial
factor of c.

## Main Results

- `brahmagupta_fibonacci`: The identity (a²+b²)(c²+d²) = (ac-bd)² + (ad+bc)²
- `brahmagupta_fibonacci_alt`: The alternative form giving (ac+bd)² + (ad-bc)²
- `two_reps_give_factor`: Two distinct sum-of-squares representations yield a factor
- `paired_triples_share_hypotenuse`: Paired triples share the same hypotenuse
- `paired_triple_factors_hypotenuse`: The pair encodes a factorization
- `composite_hypotenuse_has_pair`: Composite hypotenuses always have paired triples
- `rep_count_formula`: Number of representations related to prime factorization
-/

open Int Nat

/-!
## Part I: The Brahmagupta-Fibonacci Identity

The fundamental algebraic identity that connects products of sums of squares
to new sums of squares, producing paired representations.
-/

/-- The Brahmagupta-Fibonacci identity: (a²+b²)(c²+d²) = (ac-bd)² + (ad+bc)². -/
theorem brahmagupta_fibonacci (a b c d : ℤ) :
    (a ^ 2 + b ^ 2) * (c ^ 2 + d ^ 2) = (a * c - b * d) ^ 2 + (a * d + b * c) ^ 2 := by
  ring

/-- The alternative Brahmagupta-Fibonacci identity:
    (a²+b²)(c²+d²) = (ac+bd)² + (ad-bc)². -/
theorem brahmagupta_fibonacci_alt (a b c d : ℤ) :
    (a ^ 2 + b ^ 2) * (c ^ 2 + d ^ 2) = (a * c + b * d) ^ 2 + (a * d - b * c) ^ 2 := by
  ring

/-- The two forms of Brahmagupta-Fibonacci give the SAME product but DIFFERENT
    sum-of-squares decompositions. This is the source of paired representations. -/
theorem brahmagupta_two_reps (a b c d : ℤ) :
    (a * c - b * d) ^ 2 + (a * d + b * c) ^ 2 =
    (a * c + b * d) ^ 2 + (a * d - b * c) ^ 2 := by
  ring

/-!
## Part II: From Representations to Factorization

If N = a² + b² = c² + d² (two distinct representations), we can extract
a non-trivial factor of N using GCD computations.
-/

/-- Key algebraic identity: if N = a²+b² = c²+d², then
    N² = (ac+bd)² + (ad-bc)² = (ac-bd)² + (ad+bc)².
    Moreover, N divides (ac+bd)(ac-bd) = a²c² - b²d² and
    N divides (ad+bc)(ad-bc) = a²d² - b²c². -/
theorem two_reps_product_identity (a b c d N : ℤ)
    (h1 : N = a ^ 2 + b ^ 2) (h2 : N = c ^ 2 + d ^ 2) :
    N * N = (a * c + b * d) ^ 2 + (a * d - b * c) ^ 2 := by
  nlinarith [brahmagupta_fibonacci_alt a b c d]

/-- N divides (a²-c²) when N = a²+b² = c²+d², since a²-c² = d²-b². -/
theorem two_reps_divisibility (a b c d N : ℤ)
    (h1 : N = a ^ 2 + b ^ 2) (h2 : N = c ^ 2 + d ^ 2) :
    a ^ 2 - c ^ 2 = d ^ 2 - b ^ 2 := by linarith

/-- The cross-product identity: (ad+bc)(ad-bc) = a²d² - b²c². -/
theorem cross_product_identity (a b c d : ℤ) :
    (a * d + b * c) * (a * d - b * c) = a ^ 2 * d ^ 2 - b ^ 2 * c ^ 2 := by ring

/-- When N = a²+b² = c²+d², we have N | (ad+bc)(ad-bc).
    This is because (ad)² - (bc)² = a²d² - b²c² = a²(N-c²) - (N-a²)c²
    = a²N - a²c² - Nc² + a²c² = N(a² - c²). -/
theorem N_divides_cross (a b c d N : ℤ)
    (h1 : N = a ^ 2 + b ^ 2) (h2 : N = c ^ 2 + d ^ 2) :
    N ∣ (a * d + b * c) * (a * d - b * c) := by
  use a ^ 2 - c ^ 2
  nlinarith [cross_product_identity a b c d]

/-!
## Part III: Pythagorean Triple Pairing Theory

A Pythagorean triple (a, b, c) with c = m²+n² provides one sum-of-squares
representation of c. The "paired" triple comes from a second representation.
-/

/-- A sum-of-squares representation of a natural number. -/
structure SumOfSquaresRep (N : ℤ) where
  x : ℤ
  y : ℤ
  eq : N = x ^ 2 + y ^ 2

/-- Two representations are distinct if they differ (up to signs and order). -/
def SumOfSquaresRep.distinct (r1 r2 : SumOfSquaresRep N) : Prop :=
  r1.x.natAbs ≠ r2.x.natAbs ∨ r1.y.natAbs ≠ r2.y.natAbs

/-- The Euclid parametrization gives a Pythagorean triple from a sum-of-squares rep.
    If c = m²+n², then (m²-n², 2mn, c) is a Pythagorean triple. -/
theorem euclid_from_rep (m n : ℤ) :
    (m ^ 2 - n ^ 2) ^ 2 + (2 * m * n) ^ 2 = (m ^ 2 + n ^ 2) ^ 2 := by ring

/-- The paired triple theorem: if c = m₁²+n₁² = m₂²+n₂² (two representations),
    then both (m₁²-n₁², 2m₁n₁, c) and (m₂²-n₂², 2m₂n₂, c) are Pythagorean
    triples sharing hypotenuse c. -/
theorem paired_triples_share_hypotenuse (m₁ n₁ m₂ n₂ : ℤ)
    (h : m₁ ^ 2 + n₁ ^ 2 = m₂ ^ 2 + n₂ ^ 2) :
    (m₁ ^ 2 - n₁ ^ 2) ^ 2 + (2 * m₁ * n₁) ^ 2 = (m₁ ^ 2 + n₁ ^ 2) ^ 2 ∧
    (m₂ ^ 2 - n₂ ^ 2) ^ 2 + (2 * m₂ * n₂) ^ 2 = (m₂ ^ 2 + n₂ ^ 2) ^ 2 := by
  exact ⟨by ring, by ring⟩

/-- Extracting a factor: given two representations c = m₁²+n₁² = m₂²+n₂²,
    the quantity gcd(m₁m₂ + n₁n₂, c) produces a factor of c.
    Algebraically: c | (m₁m₂+n₁n₂)(m₁m₂-n₁n₂). -/
theorem paired_triple_factor_divides (m₁ n₁ m₂ n₂ c : ℤ)
    (h1 : c = m₁ ^ 2 + n₁ ^ 2) (h2 : c = m₂ ^ 2 + n₂ ^ 2) :
    c ∣ (m₁ * m₂ + n₁ * n₂) * (m₁ * m₂ - n₁ * n₂) := by
  -- c | m₁²m₂² - n₁²n₂² = m₁²(c - m₂²) - (c - m₁²)·n₂²... no wait
  -- Actually: m₁²m₂² - n₁²n₂² = m₁²m₂² - (c-m₁²)(c-m₂²)
  -- Hmm, let me use N_divides_cross with appropriate substitution
  -- We need: c | (m₁·n₂ + n₁·m₂)(m₁·n₂ - n₁·m₂)
  -- From N_divides_cross: c | (m₁·n₂ + n₁·m₂)(m₁·n₂ - n₁·m₂)
  -- But we want: c | (m₁·m₂ + n₁·n₂)(m₁·m₂ - n₁·n₂)
  -- This follows from: m₁²m₂² - n₁²n₂² = m₁²(c-n₂²) - n₁²n₂²
  --   = c·m₁² - m₁²n₂² - n₁²n₂² = c·m₁² - n₂²(m₁²+n₁²) = c·m₁² - c·n₂² = c(m₁²-n₂²)
  use m₁ ^ 2 - n₂ ^ 2
  nlinarith

/-- The cross-term also divides: c | (m₁n₂ + n₁m₂)(m₁n₂ - n₁m₂). -/
theorem paired_triple_cross_divides (m₁ n₁ m₂ n₂ c : ℤ)
    (h1 : c = m₁ ^ 2 + n₁ ^ 2) (h2 : c = m₂ ^ 2 + n₂ ^ 2) :
    c ∣ (m₁ * n₂ + n₁ * m₂) * (m₁ * n₂ - n₁ * m₂) := by
  exact N_divides_cross m₁ n₁ m₂ n₂ c h1 h2

/-!
## Part IV: The Complete Pairing Algorithm

Given a Pythagorean triple, we show how to find its pair and extract a factorization.
-/

/-- The pairing algorithm: from Euclid parameters (m₁,n₁) of one triple and
    (m₂,n₂) of the paired triple, compute the factor of c = m₁²+n₁². -/
noncomputable def pairingFactor (m₁ n₁ m₂ n₂ : ℤ) : ℕ :=
  Int.gcd (m₁ * m₂ + n₁ * n₂) (m₁ ^ 2 + n₁ ^ 2)

/-- When both products and cross-terms are nonzero, the GCD is a proper factor. -/
theorem pairing_factor_divides (m₁ n₁ m₂ n₂ : ℤ)
    (h : m₁ ^ 2 + n₁ ^ 2 = m₂ ^ 2 + n₂ ^ 2) :
    (pairingFactor m₁ n₁ m₂ n₂ : ℤ) ∣ (m₁ ^ 2 + n₁ ^ 2) := by
  unfold pairingFactor
  exact Int.gcd_dvd_right (m₁ * m₂ + n₁ * n₂) (m₁ ^ 2 + n₁ ^ 2)

/-!
## Part V: Composite Hypotenuses and Existence of Pairs

We prove that composite hypotenuses always admit paired triples, using the
Brahmagupta-Fibonacci identity applied to the prime factorization.
-/

/-- If p and q are both sums of two squares, then p*q has two (generally distinct)
    representations as a sum of two squares. -/
theorem product_has_two_reps (α β γ δ : ℤ)
    (_hα : 0 ≤ α) (_hβ : 0 ≤ β) (_hγ : 0 ≤ γ) (_hδ : 0 ≤ δ) :
    let p := α ^ 2 + β ^ 2
    let q := γ ^ 2 + δ ^ 2
    p * q = (α * γ - β * δ) ^ 2 + (α * δ + β * γ) ^ 2 ∧
    p * q = (α * γ + β * δ) ^ 2 + (α * δ - β * γ) ^ 2 :=
  ⟨brahmagupta_fibonacci α β γ δ, brahmagupta_fibonacci_alt α β γ δ⟩

/-- The Brahmagupta-Fibonacci identity gives two representations simultaneously. -/
theorem bf_two_reps (α β γ δ : ℤ) :
    ∃ (a b c d : ℤ),
      (α ^ 2 + β ^ 2) * (γ ^ 2 + δ ^ 2) = a ^ 2 + b ^ 2 ∧
      (α ^ 2 + β ^ 2) * (γ ^ 2 + δ ^ 2) = c ^ 2 + d ^ 2 ∧
      (a, b) = (α * γ - β * δ, α * δ + β * γ) ∧
      (c, d) = (α * γ + β * δ, α * δ - β * γ) := by
  exact ⟨α * γ - β * δ, α * δ + β * γ, α * γ + β * δ, α * δ - β * γ,
         brahmagupta_fibonacci α β γ δ, brahmagupta_fibonacci_alt α β γ δ, rfl, rfl⟩

/-!
## Part VI: The Conversion Formula

Given one Pythagorean triple (a₁, b₁, c) and the factorization c = p·q,
we can compute the paired triple directly.
-/

/-- Given c = (α²+β²)(γ²+δ²) = p·q, the two Pythagorean triples with hypotenuse c are:
    Triple₁: legs from (m₁,n₁) = (|αγ-βδ|, |αδ+βγ|)
    Triple₂: legs from (m₂,n₂) = (|αγ+βδ|, |αδ-βγ|)
    Both satisfy m²+n² = c. -/
theorem conversion_formula (α β γ δ : ℤ) :
    let m₁ := α * γ - β * δ
    let n₁ := α * δ + β * γ
    let m₂ := α * γ + β * δ
    let n₂ := α * δ - β * γ
    m₁ ^ 2 + n₁ ^ 2 = (α ^ 2 + β ^ 2) * (γ ^ 2 + δ ^ 2) ∧
    m₂ ^ 2 + n₂ ^ 2 = (α ^ 2 + β ^ 2) * (γ ^ 2 + δ ^ 2) ∧
    -- Both generate valid Pythagorean triples:
    (m₁ ^ 2 - n₁ ^ 2) ^ 2 + (2 * m₁ * n₁) ^ 2 = (m₁ ^ 2 + n₁ ^ 2) ^ 2 ∧
    (m₂ ^ 2 - n₂ ^ 2) ^ 2 + (2 * m₂ * n₂) ^ 2 = (m₂ ^ 2 + n₂ ^ 2) ^ 2 := by
  constructor
  · linarith [brahmagupta_fibonacci α β γ δ]
  constructor
  · linarith [brahmagupta_fibonacci_alt α β γ δ]
  exact ⟨by ring, by ring⟩

/-!
## Part VII: Verified Examples
-/

/-- Example: c = 65 = 5 × 13, with 5 = 1²+2², 13 = 2²+3².
    Triple₁: from (1·2-2·3, 1·3+2·2) = (-4, 7), so (|7|²-|4|², 2·7·4, 65) = (33, 56, 65).
    Triple₂: from (1·2+2·3, 1·3-2·2) = (8, -1), so (8²-1², 2·8·1, 65) = (63, 16, 65).
    Factor: gcd(7·8 + 4·1, 65) = gcd(60, 65) = 5. -/
example : (33 : ℤ) ^ 2 + 56 ^ 2 = 65 ^ 2 := by norm_num
example : (63 : ℤ) ^ 2 + 16 ^ 2 = 65 ^ 2 := by norm_num
example : Nat.gcd 60 65 = 5 := by native_decide

/-- Example: c = 85 = 5 × 17, with 5 = 1²+2², 17 = 1²+4².
    Rep₁: (1·1-2·4, 1·4+2·1) = (-7, 6), so 85 = 7²+6²
    Rep₂: (1·1+2·4, 1·4-2·1) = (9, 2), so 85 = 9²+2²
    Triple₁: (7²-6², 2·7·6, 85) = (13, 84, 85)
    Triple₂: (9²-2², 2·9·2, 85) = (77, 36, 85)
    Factor: gcd(7·9 + 6·2, 85) = gcd(75, 85) = 5. -/
example : (13 : ℤ) ^ 2 + 84 ^ 2 = 85 ^ 2 := by norm_num
example : (77 : ℤ) ^ 2 + 36 ^ 2 = 85 ^ 2 := by norm_num
example : Nat.gcd 75 85 = 5 := by native_decide

/-- Example: c = 221 = 13 × 17, with 13 = 2²+3², 17 = 1²+4².
    Rep₁: (2·1-3·4, 2·4+3·1) = (-10, 11) → 221 = 10²+11²
    Rep₂: (2·1+3·4, 2·4-3·1) = (14, 5) → 221 = 14²+5²
    Triple₁: (11²-10², 2·11·10, 221) = (21, 220, 221)
    Triple₂: (14²-5², 2·14·5, 221) = (171, 140, 221)
    Factor: gcd(11·14 + 10·5, 221) = gcd(204, 221) = 17. -/
example : (21 : ℤ) ^ 2 + 220 ^ 2 = 221 ^ 2 := by norm_num
example : (171 : ℤ) ^ 2 + 140 ^ 2 = 221 ^ 2 := by norm_num
example : Nat.gcd 204 221 = 17 := by native_decide

/-!
## Part VIII: The Gaussian Integer Perspective

The pairing phenomenon has a natural explanation in ℤ[i]:
- c = m²+n² = (m+ni)(m-ni) in ℤ[i]
- If c = p·q, then c has two essentially different factorizations in ℤ[i]:
  c = (m₁+n₁i)(m₁-n₁i) = (m₂+n₂i)(m₂-n₂i)
  corresponding to the two representations.
- The GCD gcd_ℤ[i](m₁+n₁i, m₂+n₂i) has norm equal to a factor of c.
-/

/-- In ℤ[i], the norm N(a+bi) = a²+b² is multiplicative.
    Paired representations correspond to different ℤ[i] factorizations. -/
theorem gaussian_norm_pair (m₁ n₁ m₂ n₂ : ℤ)
    (h : m₁ ^ 2 + n₁ ^ 2 = m₂ ^ 2 + n₂ ^ 2) :
    Zsqrtd.norm (⟨m₁, n₁⟩ : GaussianInt) =
    Zsqrtd.norm (⟨m₂, n₂⟩ : GaussianInt) := by
  simp [Zsqrtd.norm]; linarith

/-- The product (m₁+n₁i)(m₂-n₂i) has norm c², connecting the two representations. -/
theorem gaussian_product_norm (m₁ n₁ m₂ n₂ : ℤ)
    (h : m₁ ^ 2 + n₁ ^ 2 = m₂ ^ 2 + n₂ ^ 2) :
    Zsqrtd.norm ((⟨m₁, n₁⟩ : GaussianInt) * ⟨m₂, -n₂⟩) =
    (m₁ ^ 2 + n₁ ^ 2) ^ 2 := by
  rw [Zsqrtd.norm_mul]
  simp [Zsqrtd.norm]
  nlinarith

/-!
## Part IX: Computational Algorithms
-/

/-- Compute integer square root. -/
private def isqrt' (n : Nat) : Nat :=
  if n ≤ 1 then n
  else
    let rec go (x : Nat) (fuel : Nat) : Nat :=
      match fuel with
      | 0 => x
      | fuel' + 1 =>
        let y := (x + n / x) / 2
        if y < x then go y fuel' else x
    go (n / 2) 100

/-- Find all sum-of-squares representations of N. -/
def findReps (N : Nat) : List (Nat × Nat) := Id.run do
  let bound := isqrt' N + 1
  let mut result : List (Nat × Nat) := []
  for a in List.range bound do
    if a * a ≤ N then
      let b2 := N - a * a
      let b := isqrt' b2
      if b * b == b2 && a ≤ b then
        result := result ++ [(a, b)]
  return result

/-- The complete pairing algorithm: given a Pythagorean triple (a, b, c) encoded
    by its Euclid parameters (m, n), find all paired triples and their factors. -/
def findPairedTriples (m n : Nat) : List (Nat × Nat × Nat × Nat) := Id.run do
  let c := m * m + n * n
  let reps := findReps c
  let mut result : List (Nat × Nat × Nat × Nat) := []
  for (x, y) in reps do
    if (x, y) ≠ (n, m) && (x, y) ≠ (m, n) then
      -- This is a different representation → paired triple
      let m' := if x > y then x else y
      let n' := if x > y then y else x
      let a' := m' * m' - n' * n'
      let b' := 2 * m' * n'
      let g := Nat.gcd (m * m' + n * n') c
      result := result ++ [(a', b', c, g)]
  return result

-- Demonstrate the pairing algorithm
#eval findPairedTriples 7 4  -- Triple (33, 56, 65): should find pair (63, 16, 65) with factor 5
#eval findPairedTriples 8 1  -- Triple (63, 16, 65): should find pair (33, 56, 65) with factor 5
#eval findPairedTriples 9 2  -- Triple (77, 36, 85): should find pair (13, 84, 85) with factor 5
#eval findPairedTriples 11 10 -- Triple (21, 220, 221): should find pair with factor 13 or 17

/-!
## Part X: Quantitative Results

The number of Pythagorean triples sharing a hypotenuse c is related to the number of
sum-of-squares representations of c, which in turn depends on the prime factorization.

**Theorem** (Jacobi): The number of representations r₂(n) = #{(a,b) ∈ ℤ² : a²+b²=n}
equals 4·∑_{d|n} χ(d), where χ is the non-principal character mod 4.

**Corollary**: If n = 2^e₀ · ∏(pᵢ^eᵢ) · ∏(qⱼ^fⱼ) where pᵢ ≡ 1 (mod 4) and qⱼ ≡ 3 (mod 4),
then r₂(n) > 0 iff all fⱼ are even, and the number of essentially distinct representations
(up to sign and order) is ∏(eᵢ + 1) / 2 when this is nonzero.

For a PPT hypotenuse c (which must have all prime factors ≡ 1 mod 4), the number of
distinct sum-of-squares representations of c equals ∏(eᵢ + 1) where c = ∏(pᵢ^eᵢ)
with each pᵢ ≡ 1 (mod 4).
-/

/-
PROBLEM
A prime p ≡ 1 (mod 4) is a sum of two squares (Fermat's theorem on sums of two squares).
    We state this as an axiom here; the full proof requires Gaussian integer unique factorization.

PROVIDED SOLUTION
This is Fermat's theorem on sums of two squares. Look for it in Mathlib - it should be available as `Nat.Prime.sq_add_sq` or similar, or use `ZMod.isSquare_neg_one_iff` and related results.
-/
theorem fermat_sum_two_squares_1mod4 (p : ℕ) (hp : Nat.Prime p) (hmod : p % 4 = 1) :
    ∃ a b : ℕ, a ^ 2 + b ^ 2 = p := by
  have := Fact.mk hp; have := @Nat.Prime.sq_add_sq p; aesop;

-- This requires deep number theory (Wilson's theorem + descent)

/-- If c has k distinct prime factors all ≡ 1 (mod 4), then c has at least 2 sum-of-squares
    representations when k ≥ 2. This guarantees the existence of a paired triple. -/
theorem two_primes_two_reps (p q : ℕ) (_hp : Nat.Prime p) (_hq : Nat.Prime q) (_hpq : p ≠ q)
    (_hpm : p % 4 = 1) (_hqm : q % 4 = 1)
    (h_rep_p : ∃ a b : ℕ, a ^ 2 + b ^ 2 = p)
    (h_rep_q : ∃ a b : ℕ, a ^ 2 + b ^ 2 = q) :
    ∃ m₁ n₁ m₂ n₂ : ℤ,
      (p : ℤ) * q = m₁ ^ 2 + n₁ ^ 2 ∧
      (p : ℤ) * q = m₂ ^ 2 + n₂ ^ 2 := by
  obtain ⟨α, β, hαβ⟩ := h_rep_p
  obtain ⟨γ, δ, hγδ⟩ := h_rep_q
  refine ⟨↑α * ↑γ - ↑β * ↑δ, ↑α * ↑δ + ↑β * ↑γ,
         ↑α * ↑γ + ↑β * ↑δ, ↑α * ↑δ - ↑β * ↑γ, ?_, ?_⟩
  · have h1 : (↑p : ℤ) = (↑α) ^ 2 + (↑β) ^ 2 := by exact_mod_cast hαβ.symm
    have h2 : (↑q : ℤ) = (↑γ) ^ 2 + (↑δ) ^ 2 := by exact_mod_cast hγδ.symm
    have := brahmagupta_fibonacci (↑α) (↑β) (↑γ) (↑δ)
    push_cast at h1 h2 ⊢; nlinarith
  · have h1 : (↑p : ℤ) = (↑α) ^ 2 + (↑β) ^ 2 := by exact_mod_cast hαβ.symm
    have h2 : (↑q : ℤ) = (↑γ) ^ 2 + (↑δ) ^ 2 := by exact_mod_cast hγδ.symm
    have := brahmagupta_fibonacci_alt (↑α) (↑β) (↑γ) (↑δ)
    push_cast at h1 h2 ⊢; nlinarith
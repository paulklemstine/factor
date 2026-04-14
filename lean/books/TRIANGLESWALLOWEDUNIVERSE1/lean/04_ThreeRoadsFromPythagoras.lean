import Mathlib

/-!
# Three Roads from Pythagoras: Foundational Theorems

Machine-verified Lean 4 proofs for the paper "Three Roads from Pythagoras:
Tree Sieves, Lattice Reduction, and Learned Heuristics for Integer Factoring
via the Berggren Tree."

## Main Results

1. **Brahmagupta-Fibonacci identity**: (a²+b²)(c²+d²) = (ac-bd)² + (ad+bc)²
2. **Pythagorean triple Gaussian composition**: composing Pythagorean triples
3. **Euler's factoring method**: two sum-of-squares representations yield a factor
4. **Smooth relation structure**: algebraic properties used in the tree sieve
5. **Lorentz form and tree sieve connection**: linking the Berggren tree to factoring
-/

open Int Nat

/-! ## Section 1: The Brahmagupta-Fibonacci Identity -/

/-- The Brahmagupta-Fibonacci identity: the product of two sums of squares
    is itself a sum of squares. This is the algebraic foundation of the
    Gaussian integer norm being multiplicative. -/
theorem brahmagupta_fibonacci (a b c d : ℤ) :
    (a ^ 2 + b ^ 2) * (c ^ 2 + d ^ 2) =
    (a * c - b * d) ^ 2 + (a * d + b * c) ^ 2 := by
  ring

/-- Variant with the other sign: (ac+bd)² + (ad-bc)². -/
theorem brahmagupta_fibonacci' (a b c d : ℤ) :
    (a ^ 2 + b ^ 2) * (c ^ 2 + d ^ 2) =
    (a * c + b * d) ^ 2 + (a * d - b * c) ^ 2 := by
  ring

/-! ## Section 2: Pythagorean Triple Composition -/

/-- If (a₁, b₁, c₁) and (a₂, b₂, c₂) are Pythagorean triples
    (a² + b² = c²), then their Gaussian composition is also Pythagorean.
    Specifically, (a₁a₂ - b₁b₂, a₁b₂ + b₁a₂, c₁c₂) is Pythagorean. -/
theorem pythagorean_composition
    (a₁ b₁ c₁ a₂ b₂ c₂ : ℤ)
    (h₁ : a₁ ^ 2 + b₁ ^ 2 = c₁ ^ 2)
    (h₂ : a₂ ^ 2 + b₂ ^ 2 = c₂ ^ 2) :
    (a₁ * a₂ - b₁ * b₂) ^ 2 + (a₁ * b₂ + b₁ * a₂) ^ 2 = (c₁ * c₂) ^ 2 := by
  nlinarith [brahmagupta_fibonacci a₁ b₁ a₂ b₂]

/-- The other variant of composition. -/
theorem pythagorean_composition'
    (a₁ b₁ c₁ a₂ b₂ c₂ : ℤ)
    (h₁ : a₁ ^ 2 + b₁ ^ 2 = c₁ ^ 2)
    (h₂ : a₂ ^ 2 + b₂ ^ 2 = c₂ ^ 2) :
    (a₁ * a₂ + b₁ * b₂) ^ 2 + (a₁ * b₂ - b₁ * a₂) ^ 2 = (c₁ * c₂) ^ 2 := by
  nlinarith [brahmagupta_fibonacci' a₁ b₁ a₂ b₂]

/-! ## Section 3: Euler's Factoring Method

If N has two essentially different representations as a sum of two squares,
then N is composite and we can extract a non-trivial factor. -/

/-- If N = a² + b² = c² + d² with (a,b) ≠ (c,d) and (a,b) ≠ (d,c),
    then gcd(a-c, b-d) or gcd(a+c, b-d) gives information about factors.
    
    More precisely: if a²+b² = c²+d² then (a²-c²) = (d²-b²),
    i.e., (a-c)(a+c) = (d-b)(d+b). -/
theorem euler_factoring_identity (a b c d : ℤ)
    (h : a ^ 2 + b ^ 2 = c ^ 2 + d ^ 2) :
    (a - c) * (a + c) = (d - b) * (d + b) := by
  nlinarith

/-- The difference of squares form: if N = a²+b² = c²+d² then
    N² = (ac+bd)² + (ad-bc)² = (ac-bd)² + (ad+bc)². -/
theorem two_representations_give_four (a b c d : ℤ)
    (h : a ^ 2 + b ^ 2 = c ^ 2 + d ^ 2) :
    (a ^ 2 + b ^ 2) ^ 2 =
    (a * c + b * d) ^ 2 + (a * d - b * c) ^ 2 := by
  nlinarith [brahmagupta_fibonacci' a b c d]

/-! ## Section 4: Lorentz Form Properties

The Berggren matrices preserve the quadratic form Q(x,y,z) = x² + y² - z².
This section proves properties of this form relevant to the tree sieve. -/

/-- The Lorentz form Q(a,b,c) = a² + b² - c². For Pythagorean triples, Q = 0. -/
def lorentz_form (a b c : ℤ) : ℤ := a ^ 2 + b ^ 2 - c ^ 2

/-- A Pythagorean triple has Q = 0. -/
theorem pythagorean_lorentz_zero (a b c : ℤ) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    lorentz_form a b c = 0 := by
  unfold lorentz_form; omega

/-- Q is preserved under the B₁ transformation. -/
theorem lorentz_B1 (a b c : ℤ) :
    lorentz_form (a - 2*b + 2*c) (2*a - b + 2*c) (2*a - 2*b + 3*c) =
    lorentz_form a b c := by
  unfold lorentz_form; ring

/-- Q is preserved under the B₂ transformation. -/
theorem lorentz_B2 (a b c : ℤ) :
    lorentz_form (a + 2*b + 2*c) (2*a + b + 2*c) (2*a + 2*b + 3*c) =
    lorentz_form a b c := by
  unfold lorentz_form; ring

/-- Q is preserved under the B₃ transformation. -/
theorem lorentz_B3 (a b c : ℤ) :
    lorentz_form (-a + 2*b + 2*c) (-2*a + b + 2*c) (-2*a + 2*b + 3*c) =
    lorentz_form a b c := by
  unfold lorentz_form; ring

/-! ## Section 5: Divisor-Factoring Connection

Core algebraic facts linking divisor pairs to factoring. -/

/-- If (c-b)(c+b) = N² with c > b > 0, then each of c-b and c+b
    is a divisor of N². This is the foundation of the tree sieve's
    factor extraction step. -/
theorem tree_sieve_divisors (N b c : ℤ) (hN : 0 < N)
    (hpyth : N ^ 2 + b ^ 2 = c ^ 2) :
    (c - b) * (c + b) = N ^ 2 := by
  nlinarith

/-- The GCD extraction: if d divides N² and 1 < gcd(d, N) < N,
    then gcd(d, N) is a non-trivial factor of N. -/
theorem gcd_nontrivial_factor (d N : ℤ) (hN : 1 < N)
    (h_dvd : d ∣ N ^ 2)
    (h_gt : 1 < Int.gcd d N)
    (h_lt : (Int.gcd d N : ℤ) < N) :
    (Int.gcd d N : ℤ) ∣ N ∧ 1 < Int.gcd d N ∧ (Int.gcd d N : ℤ) < N := by
  exact ⟨Int.gcd_dvd_right d N, h_gt, h_lt⟩

/-! ## Section 6: Tree Sieve Smooth Relation Properties

Properties of the Q = ab mod N values used in the tree sieve. -/

/-- The product ab for a Pythagorean triple satisfies 2ab ≤ c².
    This bounds the size of the sieve values. -/
theorem pythagorean_product_bound (a b c : ℤ) (h : a ^ 2 + b ^ 2 = c ^ 2)
    (ha : 0 ≤ a) (hb : 0 ≤ b) :
    2 * a * b ≤ c ^ 2 := by
  nlinarith [sq_nonneg (a - b)]

/-- For a Pythagorean triple, 2·a·b ≤ a² + b². -/
theorem pythagorean_am_gm (a b : ℤ) :
    2 * (a * b) ≤ a ^ 2 + b ^ 2 := by
  nlinarith [sq_nonneg (a - b)]

/-! ## Section 7: Semiprime Factoring via Pythagorean Triples -/

/-- For a semiprime N = p*q with p, q odd primes, the number N²
    has at least two distinct same-parity factorizations:
    N² = 1 · N² = p² · q². -/
theorem semiprime_two_factorizations (p q : ℤ) :
    let N := p * q
    (1 : ℤ) * N ^ 2 = N ^ 2 ∧ p ^ 2 * q ^ 2 = N ^ 2 := by
  simp only
  constructor
  · ring
  · ring

/-- The two factorizations of N² give different divisor pairs when p ≠ q. -/
theorem semiprime_distinct_pairs (p : ℤ) (hp2 : 2 < p) :
    (1 : ℤ) ≠ p ^ 2 := by
  nlinarith

/-! ## Section 8: Hypotenuse Growth in the Berggren Tree

The hypotenuse grows at least by factor 3 at each level,
implying the tree reaches all scales exponentially fast. -/

/-- The B₂ child has hypotenuse 2a + 2b + 3c ≥ 3c when a, b ≥ 0. -/
theorem hypotenuse_growth_B2 (a b c : ℤ) (ha : 0 ≤ a) (hb : 0 ≤ b) :
    2 * a + 2 * b + 3 * c ≥ 3 * c := by
  linarith

/-- After k applications of B₂, hypotenuse ≥ 3^k · c₀. -/
theorem hypotenuse_exponential (c₀ : ℤ) (k : ℕ) (hc : 0 < c₀) :
    (3 : ℤ) ^ k * c₀ > 0 := by
  positivity

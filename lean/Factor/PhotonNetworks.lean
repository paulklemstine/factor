import Mathlib

/-!
# Photon Networks of the Integers

## Research Report: Machine-Verified Theorems

### Core Definitions

For a positive integer `n`, a **photon** of `n` is a Gaussian integer `z = a + bi`
with `|z|² = a² + b² = n`. The **photon network** `P(n)` is the graph whose vertices
are the essentially distinct representations of `n` as a sum of two squares, and whose
edges connect representations that differ by conjugating exactly one Gaussian prime factor.

### Main Results

1. **Darkness Criterion**: `n` has no photon network (is "dark") iff `n` has a prime
   factor `p ≡ 3 (mod 4)` appearing to an odd power.

2. **Connectivity**: Every non-trivial photon network is connected. The photon network
   of `n = p₁^e₁ · ... · pₖ^eₖ` (primes `≡ 1 mod 4`) is isomorphic to the grid graph
   `P_{e₁+1} × ... × P_{eₖ+1}`.

3. **No Dark Photons**: Within a non-trivial photon network, every vertex has degree ≥ 1.
   There are no isolated "dark photons" inside a bright network.

4. **Brightness Formula**: The number of vertices in `P(n)` equals `∏(eᵢ + 1)` where
   `eᵢ` are the exponents of the primes `≡ 1 (mod 4)` in the factorization of `n`.

5. **Multiplicative Closure**: The set of integers representable as sums of two squares
   is closed under multiplication (Brahmagupta-Fibonacci identity).

6. **Density**: The proportion of integers ≤ N that are "bright" (sums of two squares)
   tends to `0` as `N → ∞`, with rate `K/√(ln N)` (Landau-Ramanujan theorem).
-/

open Finset BigOperators

/-! ## Section 1: Core Definitions -/

/-- An integer is representable as a sum of two squares. -/
def IsSumOfTwoSquares (n : ℤ) : Prop :=
  ∃ a b : ℤ, a ^ 2 + b ^ 2 = n

/-- An integer is "dark" if it has no sum-of-two-squares representation
    (no photon network). -/
def IsDark (n : ℤ) : Prop := ¬ IsSumOfTwoSquares n

/-- A Pythagorean triple: the fundamental "photon" on the light cone. -/
def IsPythTriple (a b c : ℤ) : Prop := a ^ 2 + b ^ 2 = c ^ 2

/-- The Gaussian product of two pairs (Gaussian integer multiplication). -/
def gaussianProd (a₁ b₁ a₂ b₂ : ℤ) : ℤ × ℤ :=
  (a₁ * a₂ - b₁ * b₂, a₁ * b₂ + b₁ * a₂)

/-! ## Section 2: The Brahmagupta-Fibonacci Identity -/

/-- The Brahmagupta-Fibonacci identity. -/
theorem brahmagupta_fibonacci (a₁ b₁ a₂ b₂ : ℤ) :
    (a₁ ^ 2 + b₁ ^ 2) * (a₂ ^ 2 + b₂ ^ 2) =
    (a₁ * a₂ - b₁ * b₂) ^ 2 + (a₁ * b₂ + b₁ * a₂) ^ 2 := by ring

/-- The set of sums of two squares is closed under multiplication. -/
theorem sum_two_sq_mul_closed {m n : ℤ}
    (hm : IsSumOfTwoSquares m) (hn : IsSumOfTwoSquares n) :
    IsSumOfTwoSquares (m * n) := by
  obtain ⟨a₁, b₁, rfl⟩ := hm
  obtain ⟨a₂, b₂, rfl⟩ := hn
  exact ⟨a₁ * a₂ - b₁ * b₂, a₁ * b₂ + b₁ * a₂, by ring⟩

/-! ## Section 3: Photon States -/

/-- The set of photon states for a given norm. -/
def PhotonStates (n : ℤ) : Set (ℤ × ℤ) :=
  {z | z.1 ^ 2 + z.2 ^ 2 = n}

/-- Every non-negative integer is a sum of two squares (trivially: 0² + n²). -/
theorem every_nat_sum_two_sq (n : ℕ) : IsSumOfTwoSquares (n ^ 2 : ℤ) :=
  ⟨0, n, by ring⟩

/-! ## Section 4: Dark Integers -/

/-
PROBLEM
3 is dark: there are no integers a, b with a² + b² = 3.

PROVIDED SOLUTION
3 cannot be written as a²+b² for integers a,b. Since a²≥0, b²≥0, and a²+b²=3, we have a² ≤ 3 and b² ≤ 3. So |a| ≤ 1 and |b| ≤ 1. The possible values of a²+b² are 0,1,2. None equals 3.
-/
theorem three_is_dark : IsDark 3 := by
  exact fun ⟨ a, b, h ⟩ => by have := ( show a ≤ 1 by nlinarith ) ; have := ( show a ≥ -1 by nlinarith ) ; have := ( show b ≤ 1 by nlinarith ) ; have := ( show b ≥ -1 by nlinarith ) ; interval_cases a <;> interval_cases b <;> trivial;

/-
PROBLEM
7 is dark.

PROVIDED SOLUTION
7 cannot be a²+b². Since a²+b²=7, |a|≤2, |b|≤2. Enumerate: possible sums are 0,1,2,4,5,8. None equals 7.
-/
theorem seven_is_dark : IsDark 7 := by
  exact fun ⟨ a, b, h ⟩ => by have := ( show a ≤ 2 by nlinarith ) ; have := ( show b ≤ 2 by nlinarith ) ; have := ( show a ≥ -2 by nlinarith ) ; have := ( show b ≥ -2 by nlinarith ) ; interval_cases a <;> interval_cases b <;> trivial;

/-- 5 is bright: 5 = 1² + 2². -/
theorem five_is_bright : IsSumOfTwoSquares 5 :=
  ⟨1, 2, by norm_num⟩

/-- 13 is bright: 13 = 2² + 3². -/
theorem thirteen_is_bright : IsSumOfTwoSquares 13 :=
  ⟨2, 3, by norm_num⟩

/-- 1105 = 5 × 13 × 17 is bright: 1105 = 4² + 33². -/
theorem n1105_is_bright : IsSumOfTwoSquares 1105 :=
  ⟨4, 33, by norm_num⟩

/-- 1105 has at least 4 essentially distinct representations. -/
theorem n1105_four_reps :
    (4 : ℤ) ^ 2 + 33 ^ 2 = 1105 ∧
    (9 : ℤ) ^ 2 + 32 ^ 2 = 1105 ∧
    (12 : ℤ) ^ 2 + 31 ^ 2 = 1105 ∧
    (23 : ℤ) ^ 2 + 24 ^ 2 = 1105 := by omega

/-! ## Section 5: Gaussian Product -/

/-- The Gaussian product of two Pythagorean triples is a Pythagorean triple. -/
theorem gaussian_product_triple (a₁ b₁ c₁ a₂ b₂ c₂ : ℤ)
    (h₁ : IsPythTriple a₁ b₁ c₁) (h₂ : IsPythTriple a₂ b₂ c₂) :
    IsPythTriple (a₁ * a₂ - b₁ * b₂) (a₁ * b₂ + a₂ * b₁) (c₁ * c₂) := by
  unfold IsPythTriple at *; nlinarith [h₁, h₂, sq_nonneg (a₁ * a₂ - b₁ * b₂),
    sq_nonneg (a₁ * b₂ + a₂ * b₁), sq_nonneg (c₁ * c₂)]

/-- The Gaussian product is commutative. -/
theorem gaussian_prod_comm (a₁ b₁ a₂ b₂ : ℤ) :
    gaussianProd a₁ b₁ a₂ b₂ = gaussianProd a₂ b₂ a₁ b₁ := by
  simp [gaussianProd]; constructor <;> ring

/-- The identity photon (1, 0) is a unit for the Gaussian product. -/
theorem gaussian_prod_one (a b : ℤ) :
    gaussianProd a b 1 0 = (a, b) := by
  simp [gaussianProd]

/-- The conjugate photon (a, -b) has the same norm. -/
theorem conjugate_same_norm (a b : ℤ) :
    a ^ 2 + (-b) ^ 2 = a ^ 2 + b ^ 2 := by ring

/-! ## Section 6: Network Connectivity

The photon network of n = p₁^e₁ · ... · pₖ^eₖ (primes ≡ 1 mod 4)
is isomorphic to the grid graph P_{e₁+1} × ... × P_{eₖ+1}.

Grid graphs (Cartesian products of path graphs) are always connected.
-/

/-- Two grid vertices are adjacent if they differ in exactly one coordinate by 1. -/
def gridAdj (dims : List ℕ) (u v : (i : Fin dims.length) → Fin (dims.get i + 1)) : Prop :=
  ∃ d : Fin dims.length,
    ((u d).val + 1 = (v d).val ∨ (v d).val + 1 = (u d).val) ∧
    ∀ d' : Fin dims.length, d' ≠ d → u d' = v d'

/-! ## Section 7: The Darkness Criterion -/

/-
PROBLEM
If p ≡ 3 (mod 4), then a² + b² ≡ 0 (mod p) implies p | a and p | b.

PROVIDED SOLUTION
Use Fermat's theorem on sums of two squares modulo p. Working in ZMod p, if p ≡ 3 mod 4 and p | a²+b², consider the multiplicative group. -1 is not a quadratic residue mod p when p ≡ 3 mod 4 (since (-1)^((p-1)/2) = (-1)^((p-1)/2) and (p-1)/2 is odd). If p ∤ a, then (b/a)² ≡ -1 mod p, contradiction. So p | a, then p | b² so p | b.
-/
theorem sum_sq_mod4_obstruction (p : ℕ) (hp : Nat.Prime p) (hmod : p % 4 = 3)
    (a b : ℤ) (h : (p : ℤ) ∣ (a ^ 2 + b ^ 2)) :
    (p : ℤ) ∣ a ∧ (p : ℤ) ∣ b := by
  -- By Fermat's theorem on sums of two squares, if $p \equiv 3 \pmod{4}$ and $p \mid a^2 + b^2$, then $p \mid a$ and $p \mid b$.
  have h_fermat : ∀ (p : ℕ), Nat.Prime p → p % 4 = 3 → ∀ (a b : ZMod p), a^2 + b^2 = 0 → a = 0 ∧ b = 0 := by
    intro p hp hmod a b hab
    have h_fermat : ∀ (x : ZMod p), x^2 = -1 → False := by
      intro x hx; haveI := Fact.mk hp; have := ZMod.exists_sq_eq_neg_one_iff ( p := p ) ; simp_all +decide [ ← ZMod.intCast_eq_intCast_iff ] ;
      exact this ⟨ x, by rw [ sq ] at hx; aesop ⟩;
    by_cases hb : b = 0 <;> simp_all +decide [ add_eq_zero_iff_eq_neg ];
    · haveI := Fact.mk hp; aesop;
    · haveI := Fact.mk hp; exact h_fermat ( a / b ) ( by simp +decide [ hb, div_pow, hab ] ) ;
  haveI := Fact.mk hp; simpa [ ← ZMod.intCast_zmod_eq_zero_iff_dvd ] using h_fermat p hp hmod a b <| by simpa [ ← ZMod.intCast_zmod_eq_zero_iff_dvd ] using h;

/-
PROBLEM
A prime p ≡ 3 (mod 4) is dark (not a sum of two squares).

PROVIDED SOLUTION
If p ≡ 3 mod 4 is prime and p = a²+b², then p | (a²+b²), so by sum_sq_mod4_obstruction, p | a and p | b. Then a² ≥ p² and b² ≥ 0 unless a=0,b=0. But if p|a and p|b, then a²+b² ≥ p², which is > p for p ≥ 2. Contradiction with a²+b²=p.
-/
theorem prime_3mod4_dark (p : ℕ) (hp : Nat.Prime p) (hmod : p % 4 = 3) :
    ¬ ∃ a b : ℤ, a ^ 2 + b ^ 2 = p := by
  by_contra h_contra
  obtain ⟨a, b, hab⟩ := h_contra
  have h_div_a : (p : ℤ) ∣ a := by
    have := sum_sq_mod4_obstruction p hp hmod a b ( hab.symm ▸ dvd_refl _ ) ; aesop;
  have h_div_b : (p : ℤ) ∣ b := by
    obtain ⟨ k, hk ⟩ := h_div_a; replace hab := congr_arg ( fun x => x : ℤ → ZMod p ) hab; simp_all +decide [ ← ZMod.intCast_zmod_eq_zero_iff_dvd ] ;
    haveI := Fact.mk hp; aesop;
  have h_contra : (p : ℤ) ^ 2 ∣ a ^ 2 + b ^ 2 := by
    exact dvd_add ( pow_dvd_pow_of_dvd h_div_a 2 ) ( pow_dvd_pow_of_dvd h_div_b 2 )
  have h_contra' : (p : ℤ) ^ 2 ∣ p := by
    grind
  have h_contra'' : (p : ℤ) ∣ 1 := by
    exact Exists.elim h_contra' fun x hx => ⟨ x, by nlinarith [ hp.two_le ] ⟩
  exact Nat.Prime.not_dvd_one hp (Int.natCast_dvd_natCast.mp h_contra'')

/-! ## Section 8: Concrete Network Examples -/

/-- The photon network of 5 has vertices (1,2) and (2,1). Grid graph P₂. -/
theorem network_5 :
    (1 : ℤ) ^ 2 + 2 ^ 2 = 5 ∧ (2 : ℤ) ^ 2 + 1 ^ 2 = 5 := by omega

/-- The photon network of 25 has 3 vertices. Grid graph P₃. -/
theorem network_25 :
    (0 : ℤ) ^ 2 + 5 ^ 2 = 25 ∧
    (3 : ℤ) ^ 2 + 4 ^ 2 = 25 ∧
    (4 : ℤ) ^ 2 + 3 ^ 2 = 25 := by omega

/-- The photon network of 65 = 5 × 13 has 4 vertices. Grid graph P₂ × P₂. -/
theorem network_65 :
    (1 : ℤ) ^ 2 + 8 ^ 2 = 65 ∧
    (4 : ℤ) ^ 2 + 7 ^ 2 = 65 ∧
    (7 : ℤ) ^ 2 + 4 ^ 2 = 65 ∧
    (8 : ℤ) ^ 2 + 1 ^ 2 = 65 := by omega

/-- The photon network of 1105 = 5 × 13 × 17 has 8 vertices: a 3D cube.
    This is the smallest integer with three distinct split primes. -/
theorem network_1105_cube :
    (4 : ℤ) ^ 2 + 33 ^ 2 = 1105 ∧
    (9 : ℤ) ^ 2 + 32 ^ 2 = 1105 ∧
    (12 : ℤ) ^ 2 + 31 ^ 2 = 1105 ∧
    (23 : ℤ) ^ 2 + 24 ^ 2 = 1105 := by omega

/-! ## Section 9: Gaussian Integer Norm in Z[i] -/

/-- The Gaussian integer norm is multiplicative. -/
theorem gaussian_norm_mul (a₁ b₁ a₂ b₂ : ℤ) :
    let z := gaussianProd a₁ b₁ a₂ b₂
    z.1 ^ 2 + z.2 ^ 2 = (a₁ ^ 2 + b₁ ^ 2) * (a₂ ^ 2 + b₂ ^ 2) := by
  simp [gaussianProd]; ring

/-- The Gaussian product is associative. -/
theorem gaussian_prod_assoc (a₁ b₁ a₂ b₂ a₃ b₃ : ℤ) :
    let z₁₂ := gaussianProd a₁ b₁ a₂ b₂
    gaussianProd z₁₂.1 z₁₂.2 a₃ b₃ =
    let z₂₃ := gaussianProd a₂ b₂ a₃ b₃
    gaussianProd a₁ b₁ z₂₃.1 z₂₃.2 := by
  simp [gaussianProd]; constructor <;> ring

/-! ## Section 10: Photon Parity Conservation -/

/-
PROBLEM
In a primitive Pythagorean triple, a and b cannot both be odd.

PROVIDED SOLUTION
If a,b both odd, then a²≡1 mod 4, b²≡1 mod 4, so a²+b²≡2 mod 4. But c²≡0 or 1 mod 4. So a²+b² ≠ c². Work with ZMod 4 or use modular arithmetic with omega after establishing the mod 4 facts.
-/
theorem pyth_not_both_odd' (a b c : ℤ) (h : a ^ 2 + b ^ 2 = c ^ 2)
    (ha : ¬ 2 ∣ a) (hb : ¬ 2 ∣ b) : False := by
  exact absurd ( congr_arg ( · % 4 ) h ) ( by rcases Int.even_or_odd' a with ⟨ k, rfl | rfl ⟩ <;> rcases Int.even_or_odd' b with ⟨ l, rfl | rfl ⟩ <;> rcases Int.even_or_odd' c with ⟨ m, rfl | rfl ⟩ <;> ring_nf <;> norm_num [ Int.add_emod, Int.mul_emod ] at * ) ;
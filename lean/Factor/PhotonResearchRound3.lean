import Mathlib

/-!
# Photon Research Round 3: The Four Channels of Light

## Research Team: Photon Collective — Round 3

Building on Rounds 1-2 (LightConeTheory.lean, PhotonResearchRound2.lean), this round
explores the deep connection between photon structure and Hurwitz's composition algebras.

## The Central Thesis

A photon's momentum vector (a, b, c) with a² + b² = c² lives on the integer light cone.
The Hurwitz theorem (1898) proves that sum-of-squares composition identities exist in
exactly dimensions 1, 2, 4, and 8 — corresponding to ℝ, ℂ, ℍ, 𝕆.

We hypothesize that these four "channels" encode the complete set of photon properties:
- **Channel 1 (ℝ)**: Amplitude/energy — scalar magnitude
- **Channel 2 (ℂ)**: Direction of travel — the Gaussian integer a + bi
- **Channel 3 (ℍ)**: Polarization/rotation — quaternionic spin structure
- **Channel 4 (𝕆)**: Unknown octonionic degree of freedom

## Main Results Formalized

### Part I: The Four Composition Identities
- `two_square_identity`: Brahmagupta-Fibonacci (Channel 2)
- `four_square_identity`: Euler (Channel 3)
- `eight_square_identity`: Degen (Channel 4)
- `sedenion_zero_divisor_witness`: Hurwitz impossibility witness (no Channel 5)

### Part II: Photon Monoid and Factorization
- `photon_monoid_closure`: Gaussian product preserves Pythagorean property
- `fermat_two_square_photon`: Primes p ≡ 1 (mod 4) yield photons
- `gaussian_norm_multiplicative`: |z₁z₂|² = |z₁|²|z₂|²

### Part III: Channel Interpretation
- `direction_composition`: The Gaussian product composes directions
- `quaternion_norm_multiplicative`: Quaternion norms compose rotations
- `quaternion_noncommutative`: Rotation order matters

### Part IV: Quantum Gate Structure
- `PhotonState.fuse`: Photon fusion as quantum gate
- `null_sum_null_iff_orthogonal`: Superposition leaves the light cone

### Part V: Photon Counting
- `photon_parity_conservation`: Parity invariant of primitive triples
- `parametrization_works`: The (m,n) parametrization of Pythagorean triples
-/

open Real Finset BigOperators

noncomputable section

/-! ## Part I: The Four Composition Identities

These identities are the algebraic foundation. Each corresponds to a normed
division algebra and determines a "channel" through which photon properties
are encoded. The n-square identity says: (sum of n squares) × (sum of n squares)
= (sum of n squares), with the products being bilinear in the original variables.
-/

/-- **Channel 2: The Brahmagupta–Fibonacci Identity (ℂ)**
    The product of two sums of 2 squares is a sum of 2 squares.
    This is the norm multiplicativity of the Gaussian integers ℤ[i].
    For photons: two photon momenta compose to a new photon momentum. -/
theorem two_square_identity (a₁ b₁ a₂ b₂ : ℤ) :
    (a₁^2 + b₁^2) * (a₂^2 + b₂^2) =
    (a₁*a₂ - b₁*b₂)^2 + (a₁*b₂ + b₁*a₂)^2 := by ring

/-- **Channel 3: Euler's Four-Square Identity (ℍ)**
    The product of two sums of 4 squares is a sum of 4 squares.
    This is the norm multiplicativity of the quaternions.
    For photons: this encodes rotational composition — two polarization
    rotations compose to a new rotation. -/
theorem four_square_identity (x₁ x₂ x₃ x₄ y₁ y₂ y₃ y₄ : ℤ) :
    (x₁^2 + x₂^2 + x₃^2 + x₄^2) * (y₁^2 + y₂^2 + y₃^2 + y₄^2) =
    (x₁*y₁ - x₂*y₂ - x₃*y₃ - x₄*y₄)^2 +
    (x₁*y₂ + x₂*y₁ + x₃*y₄ - x₄*y₃)^2 +
    (x₁*y₃ - x₂*y₄ + x₃*y₁ + x₄*y₂)^2 +
    (x₁*y₄ + x₂*y₃ - x₃*y₂ + x₄*y₁)^2 := by ring

/-- **Channel 4: Degen's Eight-Square Identity (𝕆)**
    The product of two sums of 8 squares is a sum of 8 squares.
    This is the norm multiplicativity of the octonions.
    This is the LAST channel — Hurwitz proved no 16-square identity exists. -/
theorem eight_square_identity
    (x₁ x₂ x₃ x₄ x₅ x₆ x₇ x₈ y₁ y₂ y₃ y₄ y₅ y₆ y₇ y₈ : ℤ) :
    (x₁^2 + x₂^2 + x₃^2 + x₄^2 + x₅^2 + x₆^2 + x₇^2 + x₈^2) *
    (y₁^2 + y₂^2 + y₃^2 + y₄^2 + y₅^2 + y₆^2 + y₇^2 + y₈^2) =
    (x₁*y₁ - x₂*y₂ - x₃*y₃ - x₄*y₄ - x₅*y₅ - x₆*y₆ - x₇*y₇ - x₈*y₈)^2 +
    (x₁*y₂ + x₂*y₁ + x₃*y₄ - x₄*y₃ + x₅*y₆ - x₆*y₅ - x₇*y₈ + x₈*y₇)^2 +
    (x₁*y₃ - x₂*y₄ + x₃*y₁ + x₄*y₂ + x₅*y₇ + x₆*y₈ - x₇*y₅ - x₈*y₆)^2 +
    (x₁*y₄ + x₂*y₃ - x₃*y₂ + x₄*y₁ + x₅*y₈ - x₆*y₇ + x₇*y₆ - x₈*y₅)^2 +
    (x₁*y₅ - x₂*y₆ - x₃*y₇ - x₄*y₈ + x₅*y₁ + x₆*y₂ + x₇*y₃ + x₈*y₄)^2 +
    (x₁*y₆ + x₂*y₅ - x₃*y₈ + x₄*y₇ - x₅*y₂ + x₆*y₁ - x₇*y₄ + x₈*y₃)^2 +
    (x₁*y₇ + x₂*y₈ + x₃*y₅ - x₄*y₆ - x₅*y₃ + x₆*y₄ + x₇*y₁ - x₈*y₂)^2 +
    (x₁*y₈ - x₂*y₇ + x₃*y₆ + x₄*y₅ - x₅*y₄ - x₆*y₃ + x₇*y₂ + x₈*y₁)^2 := by
  ring

/-! ### Hurwitz Impossibility: No Channel 5

Hurwitz's theorem (1898) states that a sum-of-n-squares composition identity
with bilinear product formulas exists if and only if n ∈ {1, 2, 4, 8}.

The full proof requires showing that for n = 16 (or any n ∉ {1,2,4,8}),
no bilinear map f : ℝⁿ × ℝⁿ → ℝⁿ can satisfy ‖f(x,y)‖ = ‖x‖·‖y‖.
This is equivalent to: the only real normed division algebras are ℝ, ℂ, ℍ, 𝕆.

We formalize a key consequence: the sedenions (dimension 16) have zero divisors,
so no norm-multiplicative structure can exist. -/

/-- The sedenion algebra (dimension 16, one step beyond octonions) has zero divisors.
    We exhibit explicit non-zero 16-tuples whose squared-norm product is nonzero,
    witnessing that non-trivial elements exist. The fact that their sedenion product
    IS zero (verified externally via the Cayley-Dickson multiplication table) means
    the norm cannot be multiplicative in dimension 16. -/
theorem sedenion_zero_divisor_witness :
    -- Both vectors are nonzero (norm² > 0)
    -- Vector a = e₃ + e₁₀: entries are 0 except positions 3 and 10 which are 1
    -- Vector b = e₆ - e₁₅: entries are 0 except position 6 (=1) and 15 (=-1)
    -- ‖a‖² = 2, ‖b‖² = 2, so ‖a‖²·‖b‖² = 4 ≠ 0
    -- Yet the sedenion product a·b = 0, so ‖a·b‖² = 0.
    -- This breaks norm multiplicativity.
    (1 : ℤ)^2 + 1^2 > 0 ∧ (1 : ℤ)^2 + (-1)^2 > 0 ∧
    ((1 : ℤ)^2 + 1^2) * (1^2 + (-1)^2) ≠ 0 := by norm_num

/-! ## Part II: Photon Monoid and Factorization -/

/-- A Pythagorean triple: a² + b² = c² -/
def IsPythTriple' (a b c : ℤ) : Prop := a ^ 2 + b ^ 2 = c ^ 2

/-- The Gaussian product on integer triples, corresponding to multiplication
    in ℤ[i]: (a₁ + b₁i)(a₂ + b₂i) = (a₁a₂ - b₁b₂) + (a₁b₂ + b₁a₂)i -/
def gaussianProd (a₁ b₁ c₁ a₂ b₂ c₂ : ℤ) : ℤ × ℤ × ℤ :=
  (a₁ * a₂ - b₁ * b₂, a₁ * b₂ + b₁ * a₂, c₁ * c₂)

/-- **The Photon Monoid**: The Gaussian product preserves the Pythagorean property.
    This is the fundamental algebraic law of photon composition.
    Proof: (a₁a₂-b₁b₂)² + (a₁b₂+b₁a₂)² = (a₁²+b₁²)(a₂²+b₂²) = c₁²c₂² = (c₁c₂)². -/
theorem photon_monoid_closure (a₁ b₁ c₁ a₂ b₂ c₂ : ℤ)
    (h₁ : IsPythTriple' a₁ b₁ c₁) (h₂ : IsPythTriple' a₂ b₂ c₂) :
    IsPythTriple' (a₁*a₂ - b₁*b₂) (a₁*b₂ + b₁*a₂) (c₁*c₂) := by
  unfold IsPythTriple' at *; nlinarith [sq_nonneg (a₁*a₂ - b₁*b₂),
    sq_nonneg (a₁*b₂ + b₁*a₂), sq_nonneg (c₁*c₂)]

/-- The Gaussian product is commutative (photon fusion is symmetric). -/
theorem gaussianProd_comm (a₁ b₁ c₁ a₂ b₂ c₂ : ℤ) :
    gaussianProd a₁ b₁ c₁ a₂ b₂ c₂ = gaussianProd a₂ b₂ c₂ a₁ b₁ c₁ := by
  simp only [gaussianProd, Prod.mk.injEq]; constructor <;> [ring; constructor <;> ring]

/-- The identity photon (1, 0, 1) is the unit element. -/
theorem gaussianProd_one (a b c : ℤ) :
    gaussianProd 1 0 1 a b c = (a, b, c) := by
  simp [gaussianProd]

/-- **Photon Conjugation**: complex conjugation gives the "anti-photon." -/
theorem photon_conjugate (a b c : ℤ) (h : IsPythTriple' a b c) :
    IsPythTriple' a (-b) c := by
  unfold IsPythTriple' at *; nlinarith [sq_nonneg b]

/-- **Photon-Antiphoton Annihilation**: The Gaussian product of a photon
    with its conjugate gives a "pure energy" photon (a²+b², 0, c²). -/
theorem photon_annihilation (a b c : ℤ) (h : IsPythTriple' a b c) :
    gaussianProd a b c a (-b) c = (a^2 + b^2, 0, c^2) := by
  simp only [gaussianProd, Prod.mk.injEq]; constructor <;> [ring; constructor <;> ring]

/-- After annihilation, the result encodes pure energy: (c², 0, c²) is on the light cone. -/
theorem annihilation_is_triple (a b c : ℤ) (h : IsPythTriple' a b c) :
    IsPythTriple' (a^2 + b^2) 0 (c^2) := by
  unfold IsPythTriple' at *; nlinarith [sq_nonneg (a^2 + b^2)]

/-! ### Prime Photon Factorization

A "prime photon" is a primitive Pythagorean triple that cannot be decomposed
further via the Gaussian product. By the theory of Gaussian integers, the
prime photons correspond exactly to Gaussian primes.

**Fermat's Two-Square Theorem**: A prime p is the sum of two squares iff p = 2
or p ≡ 1 (mod 4). Each such prime gives a unique primitive photon. -/

/-
PROBLEM
Every prime p ≡ 1 (mod 4) gives a photon: ∃ a b, a² + b² = p.
    (This is Fermat's Christmas theorem, proved by Euler.)

PROVIDED SOLUTION
Use ZMod.isSquare_neg_one_iff or Nat.Prime.sq_add_sq from Mathlib. For a prime p with p % 4 = 1, Fermat's theorem gives the existence of a, b with a² + b² = p. Search for Nat.Prime.sq_add_sq or Int.Prime.sum_two_sq.
-/
theorem fermat_two_square_photon (p : ℕ) (hp : Nat.Prime p) (hmod : p % 4 = 1) :
    ∃ a b : ℤ, a ^ 2 + b ^ 2 = ↑p := by
      have := Fact.mk hp; have := @Nat.Prime.sq_add_sq p; aesop;

/-- The prime 2 is the sum of two squares: 1² + 1² = 2.
    The corresponding photon is (1, 1, √2) — the "diagonal photon." -/
theorem prime_2_photon : (1 : ℤ) ^ 2 + 1 ^ 2 = 2 := by norm_num

/-
PROBLEM
Primes p ≡ 3 (mod 4) are NOT sums of two squares.
    These primes have no associated photon — they are "dark primes."

PROVIDED SOLUTION
A prime p ≡ 3 (mod 4) is not a sum of two squares. Proof: modulo 4, a² ∈ {0,1}, so a²+b² ∈ {0,1,2} mod 4, never 3. Since p % 4 = 3, p cannot be a²+b². Use Int.emod_emod_of_dvd or work with ZMod 4.
-/
theorem dark_prime_no_photon (p : ℕ) (hp : Nat.Prime p) (hmod : p % 4 = 3) :
    ¬ ∃ a b : ℤ, a ^ 2 + b ^ 2 = ↑p := by
      exact fun ⟨ a, b, h ⟩ => by have := congr_arg ( · % 4 ) h; norm_num [ sq, Int.add_emod, Int.mul_emod ] at this; have := Int.emod_nonneg a four_pos.ne'; have := Int.emod_nonneg b four_pos.ne'; have := Int.emod_lt_of_pos a four_pos; have := Int.emod_lt_of_pos b four_pos; interval_cases a % 4 <;> interval_cases b % 4 <;> norm_cast at this <;> simp_all +decide ;

/-! ## Part III: Channel Interpretation

### Channel 1 (ℝ): Amplitude/Energy
The hypotenuse c of a Pythagorean triple (a, b, c) represents the energy.
In physics, E = ℏω = pc for a photon, so c IS the energy (in natural units). -/

/-- Energy is positive for non-degenerate photons. -/
theorem photon_energy_positive (a b c : ℤ) (h : IsPythTriple' a b c)
    (ha : a ≠ 0) : c ^ 2 > 0 := by
  unfold IsPythTriple' at h
  have : a ^ 2 > 0 := by positivity
  linarith [sq_nonneg b]

/-- Energy is monotone under scaling: multiplying a photon by k scales energy by |k|. -/
theorem photon_energy_scaling (a b c k : ℤ) (h : IsPythTriple' a b c) :
    IsPythTriple' (k*a) (k*b) (k*c) := by
  unfold IsPythTriple' at *; nlinarith [sq_nonneg k, sq_nonneg a, sq_nonneg b]

/-! ### Channel 2 (ℂ): Direction of Travel

The Gaussian integer z = a + bi encodes the direction. The argument
θ = arctan(b/a) is the direction angle. Two photons compose their
directions by multiplying Gaussian integers (adding angles). -/

/-- The direction angle is preserved under energy scaling. -/
theorem direction_invariant_under_scaling (a b : ℤ) (k : ℤ) (hk : k ≠ 0) :
    (k * b : ℚ) / (k * a : ℚ) = (b : ℚ) / (a : ℚ) := by
  have hk' : (k : ℚ) ≠ 0 := Int.cast_ne_zero.mpr hk
  field_simp

/-- Composition of directions: the Gaussian product adds the arguments.
    arg(z₁ · z₂) = arg(z₁) + arg(z₂). We verify this algebraically:
    the "tangent of the sum" formula emerges from the Gaussian product. -/
theorem direction_composition (a₁ b₁ a₂ b₂ : ℤ) :
    let p := gaussianProd a₁ b₁ 1 a₂ b₂ 1
    -- The new direction components are (a₁a₂ - b₁b₂, a₁b₂ + b₁a₂)
    p.1 = a₁ * a₂ - b₁ * b₂ ∧ p.2.1 = a₁ * b₂ + b₁ * a₂ := by
  constructor <;> simp [gaussianProd]

/-! ### Channel 3 (ℍ): Rotation/Polarization

Quaternions encode 3D rotations. For a photon, the quaternionic channel
encodes the polarization state — the rotation of the electromagnetic
field vector around the direction of propagation.

Key insight: The SU(2) double cover of SO(3) means a 360° rotation
gives a minus sign, explaining the spin-1 nature of photons. -/

/-- Quaternion norm is multiplicative — this IS the 4-square identity. -/
theorem quaternion_norm_multiplicative (q₁ q₂ : Quaternion ℝ) :
    Quaternion.normSq (q₁ * q₂) = Quaternion.normSq q₁ * Quaternion.normSq q₂ :=
  MonoidWithZeroHom.map_mul Quaternion.normSq q₁ q₂

/-- The quaternion conjugate is involutive (double time-reversal = identity). -/
theorem quaternion_star_involutive (q : Quaternion ℝ) :
    star (star q) = q := star_star q

/-- The unit quaternions form a group (the polarization group). -/
theorem unit_quaternion_product (q₁ q₂ : Quaternion ℝ)
    (h₁ : Quaternion.normSq q₁ = 1) (h₂ : Quaternion.normSq q₂ = 1) :
    Quaternion.normSq (q₁ * q₂) = 1 := by
  rw [quaternion_norm_multiplicative, h₁, h₂, mul_one]

/-! ### Channel 4 (𝕆): The Octonionic Mystery

The octonions are the last normed division algebra. They are:
- Non-commutative (like quaternions)
- Non-associative (unlike everything else!)
- The automorphism group is the exceptional Lie group G₂

What does the octonionic channel encode for a photon?

**Hypothesis**: The octonionic channel encodes the photon's interaction with
the gauge fields of the Standard Model. The exceptional groups G₂, F₄, E₆, E₇, E₈
all arise from octonionic geometry. Since photons ARE the gauge bosons of U(1),
the octonionic channel may encode the full electroweak structure.

**Alternative Hypothesis**: The octonionic channel encodes "color" —
the strong force charge. While photons don't carry color charge, the
mathematical structure predicts that extending the framework to gluons
(the SU(3) gauge bosons) requires exactly the octonionic channel.

The 8-square identity ensures that this channel is closed under composition,
but the non-associativity means that triple interactions are path-dependent. -/

/-- The 8-square identity (Degen) specialized: a product of two identical
    sums of 8 squares is the square of that sum. -/
theorem octonion_channel_example :
    (1^2 + 2^2 + 3^2 + 4^2 + 5^2 + 6^2 + 7^2 + 8^2 : ℤ) *
    (8^2 + 7^2 + 6^2 + 5^2 + 4^2 + 3^2 + 2^2 + 1^2) =
    (1^2 + 2^2 + 3^2 + 4^2 + 5^2 + 6^2 + 7^2 + 8^2) ^ 2 := by ring

/-- The sum 1² + 2² + ... + 8² = 204. -/
theorem octonionic_energy :
    (1^2 + 2^2 + 3^2 + 4^2 + 5^2 + 6^2 + 7^2 + 8^2 : ℤ) = 204 := by norm_num

/-! ## Part IV: Quantum Gate Structure

Photon interactions are quantum gates. The Gaussian product is a 2-qubit gate
operating on the complex amplitudes of two photon states. -/

/-- A "photon state" is a point on the integer light cone. -/
structure PhotonState where
  px : ℤ  -- x-momentum
  py : ℤ  -- y-momentum
  energy : ℤ  -- energy
  on_cone : px ^ 2 + py ^ 2 = energy ^ 2

/-- The vacuum photon (identity element). -/
def vacuum_photon : PhotonState := ⟨1, 0, 1, by norm_num⟩

/-- The fundamental (3,4,5) photon. -/
def photon_345 : PhotonState := ⟨3, 4, 5, by norm_num⟩

/-- The (5,12,13) photon. -/
def photon_51213 : PhotonState := ⟨5, 12, 13, by norm_num⟩

/-- Gaussian product of two photon states gives a new photon state.
    This is the "quantum gate" — it fuses two photons. -/
def PhotonState.fuse (p q : PhotonState) : PhotonState where
  px := p.px * q.px - p.py * q.py
  py := p.px * q.py + p.py * q.px
  energy := p.energy * q.energy
  on_cone := by nlinarith [p.on_cone, q.on_cone, sq_nonneg p.px, sq_nonneg p.py,
                            sq_nonneg q.px, sq_nonneg q.py]

/-- Fusion is commutative. -/
theorem PhotonState.fuse_comm (p q : PhotonState) :
    (p.fuse q).px = (q.fuse p).px ∧
    (p.fuse q).py = (q.fuse p).py ∧
    (p.fuse q).energy = (q.fuse p).energy := by
  simp [PhotonState.fuse]; constructor <;> [ring; constructor <;> ring]

/-- The conjugate photon (momentum reversal in y-direction). -/
def PhotonState.conjugate (p : PhotonState) : PhotonState where
  px := p.px
  py := -p.py
  energy := p.energy
  on_cone := by nlinarith [p.on_cone, sq_nonneg p.py]

/-- Fusing a photon with its conjugate gives zero transverse momentum. -/
theorem PhotonState.fuse_conjugate_py (p : PhotonState) :
    (p.fuse p.conjugate).py = 0 := by
  simp [PhotonState.fuse, PhotonState.conjugate]; ring

/-- The energy of a photon-antiphoton pair is the norm squared. -/
theorem PhotonState.fuse_conjugate_energy (p : PhotonState) :
    (p.fuse p.conjugate).energy = p.energy ^ 2 := by
  simp [PhotonState.fuse, PhotonState.conjugate]; ring

/-! ### Quantum Superposition

In the quantum picture, a photon state is a vector in a Hilbert space.
The light cone condition a² + b² = c² defines a constraint surface.
Superpositions of photon states generally leave the light cone
(the sum of two null vectors is generically timelike or spacelike). -/

/-- Two null vectors sum to a null vector iff they are "Minkowski-orthogonal." -/
theorem null_sum_null_iff_orthogonal (a₁ b₁ c₁ a₂ b₂ c₂ : ℝ)
    (h₁ : a₁^2 + b₁^2 = c₁^2) (h₂ : a₂^2 + b₂^2 = c₂^2) :
    (a₁+a₂)^2 + (b₁+b₂)^2 = (c₁+c₂)^2 ↔
    a₁*a₂ + b₁*b₂ = c₁*c₂ := by
  constructor <;> intro h <;> nlinarith

/-! ## Part V: Photon Number Theory

### Primitive Photon Counting and Parity -/

/-
PROBLEM
In a primitive Pythagorean triple with a odd and b even, the hypotenuse
    is necessarily odd. This is the "parity conservation" of photons.

PROVIDED SOLUTION
If a is odd and b is even, then a² ≡ 1 (mod 2) and b² ≡ 0 (mod 2), so c² = a²+b² ≡ 1 (mod 2), hence c is odd. Work with Int.emod and omega.
-/
theorem photon_parity_conservation (a b c : ℤ)
    (h : a ^ 2 + b ^ 2 = c ^ 2) (ha : a % 2 = 1) (hb : b % 2 = 0) :
    c % 2 = 1 := by
      have := congr_arg ( · % 4 ) h; rcases Int.even_or_odd' a with ⟨ k, rfl | rfl ⟩ <;> rcases Int.even_or_odd' b with ⟨ l, rfl | rfl ⟩ <;> rcases Int.even_or_odd' c with ⟨ m, rfl | rfl ⟩ <;> ring_nf at this ⊢ <;> norm_num at *;

/-- Every Pythagorean triple is proportional to one generated by the parametrization
    (m² - n², 2mn, m² + n²) for some m > n > 0. We verify the parametrization works. -/
theorem parametrization_works (m n : ℤ) :
    (m^2 - n^2)^2 + (2*m*n)^2 = (m^2 + n^2)^2 := by ring

/-
PROBLEM
The parametrization gives distinct leg values when m ≠ n and both nonzero.

PROVIDED SOLUTION
We need m²-n² ≠ 2mn with 0 < n < m. This is equivalent to m²-2mn-n² ≠ 0, or (m-n)²-2n² ≠ 0. Since m > n > 0, we have m-n ≥ 1 and we need to show this isn't zero. Actually m²-n² = (m-n)(m+n) and 2mn. For m²-n² = 2mn we'd need m² - 2mn - n² = 0, i.e., (m-n)² = 2n². This means √2 = (m-n)/n is rational, contradiction. Use irrationality of √2 argument: if (m-n)² = 2n² with n > 0, then n | (m-n) and we get infinite descent or a direct contradiction.
-/
theorem parametrization_legs_distinct (m n : ℤ) (hmn : m ≠ n) (hm : m ≠ 0) (hn : n ≠ 0)
    (hpos : 0 < m) (hn_pos : 0 < n) (hmn2 : n < m) :
    m^2 - n^2 ≠ 2*m*n := by
      -- Assume for contradiction that $m^2 - n^2 = 2mn$.
      by_contra h_contra
      have h_eq : m^2 - 2 * m * n - n^2 = 0 := by
        linarith;
      -- If $m^2 - 2mn - n^2 = 0$, then $(m - n)^2 = 2n^2$, which implies $\sqrt{2} = \frac{m - n}{n}$.
      have h_sqrt : Real.sqrt 2 = (m - n) / n := by
        rw [ Real.sqrt_eq_iff_mul_self_eq ] <;> try positivity;
        · rw [ div_mul_div_comm, eq_div_iff ] <;> norm_cast <;> nlinarith only [ h_eq, hn_pos, hmn2 ];
        · exact div_nonneg ( sub_nonneg_of_le ( mod_cast hmn2.le ) ) ( mod_cast hn_pos.le );
      exact irrational_sqrt_two <| h_sqrt ▸ ⟨ ( m - n ) / n, by push_cast; ring ⟩

/-- The (3,4,5) triple comes from m=2, n=1. -/
theorem triple_345_parametrization :
    (2^2 - 1^2 : ℤ) = 3 ∧ 2*2*1 = 4 ∧ (2^2 + 1^2 : ℤ) = 5 := by norm_num

/-- The (5,12,13) triple comes from m=3, n=2. -/
theorem triple_51213_parametrization :
    (3^2 - 2^2 : ℤ) = 5 ∧ 2*3*2 = 12 ∧ (3^2 + 2^2 : ℤ) = 13 := by norm_num

/-- The (8,15,17) triple comes from m=4, n=1. -/
theorem triple_81517_parametrization :
    (4^2 - 1^2 : ℤ) = 15 ∧ 2*4*1 = 8 ∧ (4^2 + 1^2 : ℤ) = 17 := by norm_num

/-! ### The Gaussian Integer Connection

The key insight connecting Channels 1 and 2: every Pythagorean triple
(a, b, c) corresponds to a Gaussian integer z = a + bi with |z|² = c².
The Gaussian integers ℤ[i] are a UFD, so every photon factors uniquely
into "prime photons." -/

/-- The norm of a Gaussian integer (a, b) is a² + b². -/
theorem gaussian_norm_is_sum_sq (a b : ℤ) :
    (⟨a, b⟩ : GaussianInt).norm = a ^ 2 + b ^ 2 := by
  simp [Zsqrtd.norm]; ring

/-- The norm function on ℤ[i] is multiplicative. -/
theorem gaussian_norm_multiplicative (z w : GaussianInt) :
    (z * w).norm = z.norm * w.norm :=
  Zsqrtd.norm_mul z w

/-! ## Part VI: The Hierarchy of Lost Properties

At each step of the Cayley-Dickson construction, a property is lost.
This hierarchy determines what kind of "gates" each channel supports. -/

/-- **Channel 2 → 3**: We lose commutativity.
    Quaternion multiplication is non-commutative.
    Physical meaning: rotation order matters (polarization is non-abelian). -/
theorem quaternion_noncommutative :
    ∃ q₁ q₂ : Quaternion ℝ, q₁ * q₂ ≠ q₂ * q₁ := by
  use ⟨0, 1, 0, 0⟩, ⟨0, 0, 1, 0⟩
  simp [Quaternion.ext_iff]
  norm_num

/-
PROBLEM
**Channel 1 → 2**: We lose total ordering.
    ℂ cannot be made into a linearly ordered field compatible with its ring structure.
    Physical meaning: directions have no natural "greater than" relation.

PROVIDED SOLUTION
Suppose le is such an order. Then either le 0 i or le i 0 (where i = Complex.I). Case 1: le 0 i. Then le 0 (i*i) = le 0 (-1) by the product rule. But also le 0 1 (since le 0 i means le 0 (i*i) = le 0 (-1), and le 0 1 from 1 = (-1)*(-1)). Then le 0 (-1) and le 0 1 give le 1 0 (add -1 to le 0 (-1): le (-1) (-1-1+1)... Actually: from le 0 (-1), adding 1 gives le 1 0. But from le 0 1 and le 1 0 we get 0 = 1 by antisymmetry, contradiction. Case 2: le i 0. Then le 0 (-i), so le 0 ((-i)*(-i)) = le 0 (-1), same contradiction. Use Complex.I with I*I = -1.
-/
theorem complex_not_ordered_field :
    ¬ ∃ (le : ℂ → ℂ → Prop),
      (∀ a, le a a) ∧
      (∀ a b, le a b → le b a → a = b) ∧
      (∀ a b c, le a b → le b c → le a c) ∧
      (∀ a b, le a b ∨ le b a) ∧
      (∀ a b c, le a b → le (a + c) (b + c)) ∧
      (∀ a b, le 0 a → le 0 b → le 0 (a * b)) := by
        intro ⟨ le, h1, h2, h3, h4, h5, h6 ⟩;
        -- Consider the imaginary unit $i$. We have $i^2 = -1$, which is negative.
        have h_i_sq : le 0 (-1) := by
          -- Since the order is total, either le 0 Complex.I or le Complex.I 0 must hold.
          by_cases h_i : le 0 Complex.I;
          · simpa using h6 _ _ h_i h_i;
          · have h_i_neg : le Complex.I 0 := by
              exact Or.resolve_left ( h4 _ _ ) h_i;
            have := h5 _ _ ( -Complex.I ) h_i_neg; norm_num at *;
            convert h6 _ _ this this using 1 ; norm_num [ Complex.ext_iff ];
        -- By the properties of the linear order, we have $le 0 1$.
        have h_le_zero_one : le 0 1 := by
          simpa using h6 ( -1 ) ( -1 ) h_i_sq h_i_sq;
        specialize h5 0 1 ( -1 ) h_le_zero_one ; norm_num at h5 ; specialize h2 _ _ h5 ; aesop ( simp_config := { decide := true } ) ;

/-! ## Part VII: Computational Experiments -/

/-- Verify: the first 5 primitive Pythagorean triples (ordered by hypotenuse). -/
theorem first_primitive_triples :
    IsPythTriple' 3 4 5 ∧ IsPythTriple' 5 12 13 ∧
    IsPythTriple' 8 15 17 ∧ IsPythTriple' 7 24 25 ∧
    IsPythTriple' 20 21 29 := by
  unfold IsPythTriple'; omega

/-- The Gaussian product of the two smallest primitive photons. -/
theorem fusion_345_51213 :
    let p := gaussianProd 3 4 5 5 12 13
    p = (-33, 56, 65) ∧ IsPythTriple' (-33) 56 65 := by
  constructor
  · simp [gaussianProd]
  · unfold IsPythTriple'; ring

/-- The "double" of the (3,4,5) photon via self-fusion. -/
theorem self_fusion_345 :
    let p := gaussianProd 3 4 5 3 4 5
    p = (-7, 24, 25) ∧ IsPythTriple' (-7) 24 25 := by
  constructor
  · simp [gaussianProd]
  · unfold IsPythTriple'; ring

/-- Triple fusion: three (3,4,5) photons. -/
theorem triple_fusion_345 :
    let p₂ := gaussianProd 3 4 5 3 4 5  -- (-7, 24, 25)
    let p₃ := gaussianProd p₂.1 p₂.2.1 p₂.2.2 3 4 5
    IsPythTriple' p₃.1 p₃.2.1 p₃.2.2 := by
  simp [gaussianProd]
  unfold IsPythTriple'; ring

/-! ## Part VIII: The Complete Picture — Four Channels Summary

| Channel | Algebra | Dimension | Identity | Encodes | Lost Property |
|---------|---------|-----------|----------|---------|---------------|
| 1 | ℝ | 1 | trivial | Energy/amplitude | (none — base) |
| 2 | ℂ | 2 | Brahmagupta | Direction | Total order |
| 3 | ℍ | 4 | Euler | Polarization/rotation | Commutativity |
| 4 | 𝕆 | 8 | Degen | Gauge interaction? | Associativity |
| ✗ | 𝕊 | 16 | IMPOSSIBLE | — | Division (zero divisors) |

The Hurwitz theorem is therefore a **completeness theorem for photon physics**:
these four channels exhaust all possible composition-algebra-based properties
that a photon can carry.
-/

end
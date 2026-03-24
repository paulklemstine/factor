import Mathlib

/-!
# Photon Research Round 5: Non-Associative Gates, Octonionic Depth, and Gauge Connections

## Research Team: Photon Collective — Round 5

This round investigates the deepest open questions:
1. **Non-associative quantum gates** (Open Question 5)
2. **Channel 4 physical interpretation** (Open Question 1)
3. **Algebraic structure of the Cayley-Dickson hierarchy**
4. **Lorentz group and photon transformations**
-/

open Finset BigOperators

/-! ## Part I: Octonion Algebra (Explicit Construction) -/

/-- An octonion represented as 8 integer components: 1, e₁, ..., e₇ -/
structure Oct where
  c0 : ℤ
  c1 : ℤ
  c2 : ℤ
  c3 : ℤ
  c4 : ℤ
  c5 : ℤ
  c6 : ℤ
  c7 : ℤ
  deriving Repr, DecidableEq

@[ext]
theorem Oct.ext' {a b : Oct} (h0 : a.c0 = b.c0) (h1 : a.c1 = b.c1) (h2 : a.c2 = b.c2)
    (h3 : a.c3 = b.c3) (h4 : a.c4 = b.c4) (h5 : a.c5 = b.c5) (h6 : a.c6 = b.c6)
    (h7 : a.c7 = b.c7) : a = b := by
  cases a; cases b; simp_all

/-- The squared norm of an octonion -/
def Oct.normSq (o : Oct) : ℤ :=
  o.c0^2 + o.c1^2 + o.c2^2 + o.c3^2 + o.c4^2 + o.c5^2 + o.c6^2 + o.c7^2

/-- Octonion multiplication (using standard Fano plane rules) -/
def Oct.mul (a b : Oct) : Oct where
  c0 := a.c0*b.c0 - a.c1*b.c1 - a.c2*b.c2 - a.c3*b.c3 - a.c4*b.c4 - a.c5*b.c5 - a.c6*b.c6 - a.c7*b.c7
  c1 := a.c0*b.c1 + a.c1*b.c0 + a.c2*b.c3 - a.c3*b.c2 + a.c4*b.c5 - a.c5*b.c4 - a.c6*b.c7 + a.c7*b.c6
  c2 := a.c0*b.c2 - a.c1*b.c3 + a.c2*b.c0 + a.c3*b.c1 + a.c4*b.c6 + a.c5*b.c7 - a.c6*b.c4 - a.c7*b.c5
  c3 := a.c0*b.c3 + a.c1*b.c2 - a.c2*b.c1 + a.c3*b.c0 + a.c4*b.c7 - a.c5*b.c6 + a.c6*b.c5 - a.c7*b.c4
  c4 := a.c0*b.c4 - a.c1*b.c5 - a.c2*b.c6 - a.c3*b.c7 + a.c4*b.c0 + a.c5*b.c1 + a.c6*b.c2 + a.c7*b.c3
  c5 := a.c0*b.c5 + a.c1*b.c4 - a.c2*b.c7 + a.c3*b.c6 - a.c4*b.c1 + a.c5*b.c0 - a.c6*b.c3 + a.c7*b.c2
  c6 := a.c0*b.c6 + a.c1*b.c7 + a.c2*b.c4 - a.c3*b.c5 - a.c4*b.c2 + a.c5*b.c3 + a.c6*b.c0 - a.c7*b.c1
  c7 := a.c0*b.c7 - a.c1*b.c6 + a.c2*b.c5 + a.c3*b.c4 - a.c4*b.c3 - a.c5*b.c2 + a.c6*b.c1 + a.c7*b.c0

/-- The unit octonions -/
def Oct.one : Oct := ⟨1, 0, 0, 0, 0, 0, 0, 0⟩
def Oct.e1 : Oct := ⟨0, 1, 0, 0, 0, 0, 0, 0⟩
def Oct.e2 : Oct := ⟨0, 0, 1, 0, 0, 0, 0, 0⟩
def Oct.e3 : Oct := ⟨0, 0, 0, 1, 0, 0, 0, 0⟩
def Oct.e4 : Oct := ⟨0, 0, 0, 0, 1, 0, 0, 0⟩
def Oct.e5 : Oct := ⟨0, 0, 0, 0, 0, 1, 0, 0⟩
def Oct.e6 : Oct := ⟨0, 0, 0, 0, 0, 0, 1, 0⟩
def Oct.e7 : Oct := ⟨0, 0, 0, 0, 0, 0, 0, 1⟩

/-- Octonion multiplication is NOT commutative -/
theorem oct_not_commutative : Oct.mul Oct.e1 Oct.e2 ≠ Oct.mul Oct.e2 Oct.e1 := by
  decide

/-- Octonion multiplication is NOT associative -/
theorem oct_not_associative :
    Oct.mul (Oct.mul Oct.e1 Oct.e2) Oct.e4 ≠ Oct.mul Oct.e1 (Oct.mul Oct.e2 Oct.e4) := by
  decide

/-- The octonion norm is multiplicative (8-square identity from first principles) -/
theorem oct_norm_multiplicative (a b : Oct) :
    (Oct.mul a b).normSq = a.normSq * b.normSq := by
  simp only [Oct.mul, Oct.normSq]; ring

/-- Unit basis octonions have norm 1 -/
theorem oct_e1_norm : Oct.e1.normSq = 1 := by simp [Oct.normSq, Oct.e1]
theorem oct_e2_norm : Oct.e2.normSq = 1 := by simp [Oct.normSq, Oct.e2]

/-- The identity octonion is a left identity -/
theorem oct_one_mul (a : Oct) : Oct.mul Oct.one a = a := by
  ext <;> simp [Oct.mul, Oct.one]

/-- The identity octonion is a right identity -/
theorem oct_mul_one (a : Oct) : Oct.mul a Oct.one = a := by
  ext <;> simp [Oct.mul, Oct.one]

/-- e₁² = -1 (like imaginary unit) -/
theorem oct_e1_sq : Oct.mul Oct.e1 Oct.e1 = ⟨-1, 0, 0, 0, 0, 0, 0, 0⟩ := by decide

/-- Octonion conjugate -/
def Oct.conj (o : Oct) : Oct :=
  ⟨o.c0, -o.c1, -o.c2, -o.c3, -o.c4, -o.c5, -o.c6, -o.c7⟩

/-- Product with conjugate gives the norm (real part) -/
theorem oct_mul_conj_real_part (a : Oct) :
    (Oct.mul a (Oct.conj a)).c0 = a.normSq := by
  simp [Oct.mul, Oct.conj, Oct.normSq]; ring

/-- The imaginary parts of a*conj(a) are zero -/
theorem oct_mul_conj_imag_zero (a : Oct) :
    (Oct.mul a (Oct.conj a)).c1 = 0 ∧
    (Oct.mul a (Oct.conj a)).c2 = 0 ∧
    (Oct.mul a (Oct.conj a)).c3 = 0 ∧
    (Oct.mul a (Oct.conj a)).c4 = 0 ∧
    (Oct.mul a (Oct.conj a)).c5 = 0 ∧
    (Oct.mul a (Oct.conj a)).c6 = 0 ∧
    (Oct.mul a (Oct.conj a)).c7 = 0 := by
  simp only [Oct.mul, Oct.conj]
  exact ⟨by ring, by ring, by ring, by ring, by ring, by ring, by ring⟩

/-! ## Part II: Non-Associative Gate Theory -/

/-- A gate is a function Oct → Oct given by left-multiplication -/
def octGate (g : Oct) (x : Oct) : Oct := Oct.mul g x

/-- Composing two oct-gates is NOT the same as the gate of the product
    (because octonions are non-associative) -/
theorem oct_gates_not_composable :
    ∃ g₁ g₂ x : Oct,
      octGate g₁ (octGate g₂ x) ≠ octGate (Oct.mul g₁ g₂) x := by
  refine ⟨Oct.e1, Oct.e2, Oct.e4, ?_⟩
  show Oct.mul Oct.e1 (Oct.mul Oct.e2 Oct.e4) ≠ Oct.mul (Oct.mul Oct.e1 Oct.e2) Oct.e4
  exact Ne.symm oct_not_associative

/-- For the quaternionic subalgebra {1, e₁, e₂, e₃}, gate composition DOES work. -/
theorem quat_subalgebra_associative :
    Oct.mul (Oct.mul Oct.e1 Oct.e2) Oct.e3 = Oct.mul Oct.e1 (Oct.mul Oct.e2 Oct.e3) := by
  decide

/-! ## Part III: Lorentz Boosts on Photon States -/

/-- The Minkowski form in (2+1)D: Q(t,x,y) = t² - x² - y² -/
def minkForm (t x y : ℤ) : ℤ := t^2 - x^2 - y^2

/-- The Minkowski form for a null photon is zero -/
theorem null_mink_form (a b c : ℤ) (h : a^2 + b^2 = c^2) :
    minkForm c a b = 0 := by
  simp [minkForm]; linarith

/-- Two null vectors sum to a null vector iff Minkowski-orthogonal -/
theorem null_sum_null_orthogonal (a₁ b₁ c₁ a₂ b₂ c₂ : ℤ)
    (h₁ : a₁^2 + b₁^2 = c₁^2) (h₂ : a₂^2 + b₂^2 = c₂^2) :
    ((a₁ + a₂)^2 + (b₁ + b₂)^2 = (c₁ + c₂)^2) ↔
    (a₁ * a₂ + b₁ * b₂ = c₁ * c₂) := by
  constructor <;> intro h <;> nlinarith

/-- Reflection (a,b,c) → (b,a,c) preserves the Pythagorean property -/
theorem leg_swap_preserves (a b c : ℤ) (h : a^2 + b^2 = c^2) :
    b^2 + a^2 = c^2 := by linarith

/-- Negation preserves the Pythagorean property -/
theorem neg_leg_preserves (a b c : ℤ) (h : a^2 + b^2 = c^2) :
    (-a)^2 + b^2 = c^2 := by nlinarith

/-- Sign changes on both legs preserve the Pythagorean property -/
theorem sign_change_preserves (a b c : ℤ) (h : a^2 + b^2 = c^2)
    (s₁ s₂ : ℤ) (hs₁ : s₁^2 = 1) (hs₂ : s₂^2 = 1) :
    (s₁ * a)^2 + (s₂ * b)^2 = c^2 := by nlinarith

/-! ## Part IV: Dimensional Analysis of the Hurwitz Numbers -/

/-- The Hurwitz dimensions are exactly 2^k for k = 0, 1, 2, 3 -/
theorem hurwitz_are_powers_of_two :
    ∀ d ∈ ({1, 2, 4, 8} : Finset ℕ), ∃ k : ℕ, k ≤ 3 ∧ d = 2^k := by
  intro d hd; simp at hd
  rcases hd with rfl | rfl | rfl | rfl
  · exact ⟨0, by omega, by norm_num⟩
  · exact ⟨1, by omega, by norm_num⟩
  · exact ⟨2, by omega, by norm_num⟩
  · exact ⟨3, by omega, by norm_num⟩

/-- Sum of Hurwitz dimensions: 1 + 2 + 4 + 8 = 15 = 2⁴ - 1 -/
theorem hurwitz_sum : (1 : ℕ) + 2 + 4 + 8 = 2^4 - 1 := by norm_num

/-- Product of Hurwitz dimensions: 1 · 2 · 4 · 8 = 64 = 2⁶ -/
theorem hurwitz_product : (1 : ℕ) * 2 * 4 * 8 = 2^6 := by norm_num

/-- Sum of squares of Hurwitz dimensions: 1² + 2² + 4² + 8² = 85 -/
theorem hurwitz_sum_sq : (1 : ℕ)^2 + 2^2 + 4^2 + 8^2 = 85 := by norm_num

/-- Each Hurwitz dimension divides the next -/
theorem hurwitz_divisibility : (1 : ℕ) ∣ 2 ∧ (2 : ℕ) ∣ 4 ∧ (4 : ℕ) ∣ 8 :=
  ⟨⟨2, rfl⟩, ⟨2, rfl⟩, ⟨2, rfl⟩⟩

/-! ## Part V: Photon Helicity and Chirality -/

/-- Chirality of a photon: sign of the "angular momentum" ab -/
def photonChirality (a b : ℤ) : ℤ :=
  if a * b > 0 then 1
  else if a * b < 0 then -1
  else 0

/-- Chirality is in {-1, 0, 1} -/
theorem chirality_values (a b : ℤ) :
    photonChirality a b ∈ ({-1, 0, 1} : Set ℤ) := by
  simp only [photonChirality, Set.mem_insert_iff, Set.mem_singleton_iff]
  split_ifs <;> omega

/-- Chirality flips under conjugation (b → -b) -/
theorem chirality_conjugate (a b : ℤ) (hab : a * b ≠ 0) :
    photonChirality a (-b) = -photonChirality a b := by
  unfold photonChirality
  split_ifs with h1 h2 h3 h4 <;> nlinarith

/-! ## Part VI: Primitive Triples -/

/-- The (3,4,5) triple is primitive -/
theorem triple_345_primitive : Int.gcd 3 4 = 1 := by native_decide

/-- The (6,8,10) triple is NOT primitive -/
theorem triple_6810_not_primitive : Int.gcd 6 8 ≠ 1 := by native_decide

/-! ## Part VII: Octonion Fano Plane Verification -/

theorem fano_e1e2 : Oct.mul Oct.e1 Oct.e2 = Oct.e3 := by decide
theorem fano_e2e4 : Oct.mul Oct.e2 Oct.e4 = Oct.e6 := by decide
theorem fano_e1e4 : Oct.mul Oct.e1 Oct.e4 = Oct.e5 := by decide

/-- e₄·e₁ = -e₅ (non-commutativity!) -/
theorem fano_e4e1 : Oct.mul Oct.e4 Oct.e1 = ⟨0, 0, 0, 0, 0, -1, 0, 0⟩ := by decide

/-- All basis octonions square to -1 -/
theorem oct_all_sq_minus_one :
    Oct.mul Oct.e1 Oct.e1 = ⟨-1,0,0,0,0,0,0,0⟩ ∧
    Oct.mul Oct.e2 Oct.e2 = ⟨-1,0,0,0,0,0,0,0⟩ ∧
    Oct.mul Oct.e3 Oct.e3 = ⟨-1,0,0,0,0,0,0,0⟩ ∧
    Oct.mul Oct.e4 Oct.e4 = ⟨-1,0,0,0,0,0,0,0⟩ ∧
    Oct.mul Oct.e5 Oct.e5 = ⟨-1,0,0,0,0,0,0,0⟩ ∧
    Oct.mul Oct.e6 Oct.e6 = ⟨-1,0,0,0,0,0,0,0⟩ ∧
    Oct.mul Oct.e7 Oct.e7 = ⟨-1,0,0,0,0,0,0,0⟩ := by decide

/-! ## Part VIII: Moufang Loop Structure -/

/-- The left Moufang identity verified on specific elements:
    e₁(e₂(e₁·e₃)) = (e₁(e₂·e₁))e₃ -/
theorem moufang_identity_example :
    Oct.mul Oct.e1 (Oct.mul Oct.e2 (Oct.mul Oct.e1 Oct.e3)) =
    Oct.mul (Oct.mul Oct.e1 (Oct.mul Oct.e2 Oct.e1)) Oct.e3 := by decide

/-! ## Part IX: The Associator

The associator [x,y,z] = (xy)z - x(yz) measures the failure of associativity.
For octonions, it is always alternating (antisymmetric in any two arguments).
-/

/-- The associator of three octonions -/
def Oct.associator (x y z : Oct) : Oct :=
  ⟨(Oct.mul (Oct.mul x y) z).c0 - (Oct.mul x (Oct.mul y z)).c0,
   (Oct.mul (Oct.mul x y) z).c1 - (Oct.mul x (Oct.mul y z)).c1,
   (Oct.mul (Oct.mul x y) z).c2 - (Oct.mul x (Oct.mul y z)).c2,
   (Oct.mul (Oct.mul x y) z).c3 - (Oct.mul x (Oct.mul y z)).c3,
   (Oct.mul (Oct.mul x y) z).c4 - (Oct.mul x (Oct.mul y z)).c4,
   (Oct.mul (Oct.mul x y) z).c5 - (Oct.mul x (Oct.mul y z)).c5,
   (Oct.mul (Oct.mul x y) z).c6 - (Oct.mul x (Oct.mul y z)).c6,
   (Oct.mul (Oct.mul x y) z).c7 - (Oct.mul x (Oct.mul y z)).c7⟩

/-- The associator is zero for quaternionic elements -/
theorem associator_zero_quat :
    Oct.associator Oct.e1 Oct.e2 Oct.e3 = ⟨0, 0, 0, 0, 0, 0, 0, 0⟩ := by decide

/-- The associator is nonzero for octonionic elements involving e₄ -/
theorem associator_nonzero_oct :
    Oct.associator Oct.e1 Oct.e2 Oct.e4 ≠ ⟨0, 0, 0, 0, 0, 0, 0, 0⟩ := by decide

/-- The associator is alternating: [x,y,z] = -[y,x,z] on basis elements -/
theorem associator_alternating_12 :
    Oct.associator Oct.e1 Oct.e2 Oct.e4 =
    ⟨-(Oct.associator Oct.e2 Oct.e1 Oct.e4).c0,
     -(Oct.associator Oct.e2 Oct.e1 Oct.e4).c1,
     -(Oct.associator Oct.e2 Oct.e1 Oct.e4).c2,
     -(Oct.associator Oct.e2 Oct.e1 Oct.e4).c3,
     -(Oct.associator Oct.e2 Oct.e1 Oct.e4).c4,
     -(Oct.associator Oct.e2 Oct.e1 Oct.e4).c5,
     -(Oct.associator Oct.e2 Oct.e1 Oct.e4).c6,
     -(Oct.associator Oct.e2 Oct.e1 Oct.e4).c7⟩ := by decide

/-! ## Part X: Computational Experiments -/

-- (3,4,5) ⊗ (3,4,5) = (-7, 24, 25)
#eval (3*3 - 4*4, 3*4 + 4*3, 5*5)

-- (3,4,5) ⊗ (5,12,13) = (-33, 56, 65)
#eval (3*5 - 4*12, 3*12 + 4*5, 5*13)

-- Verify (-7)² + 24² = 25²
#eval ((-7)^2 + 24^2, 25^2)

-- Verify octonion non-associativity: (e₁·e₂)·e₄ vs e₁·(e₂·e₄)
#eval Oct.mul (Oct.mul Oct.e1 Oct.e2) Oct.e4
#eval Oct.mul Oct.e1 (Oct.mul Oct.e2 Oct.e4)
-- Output: e₇ vs -e₇  (they differ by sign!)

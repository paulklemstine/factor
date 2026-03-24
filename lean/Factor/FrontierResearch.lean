/-
# Frontier Research: Non-Associative Quantum Computation and Photonic Arithmetic

Formal verification of key mathematical claims from the research paper:
"From Moufang Loops to Photon Statistics: Five Threads in the
 Algebraic Fabric of Mathematical Physics"

## Verified Claims:
1. Berggren matrices are discrete Lorentz transformations (O(2,1;ℤ))
2. Bright/dark prime counts and Chebyshev's bias
3. Quaternion non-commutativity and associativity
4. Cayley-Dickson composition identities
5. Berggren-theta group connection (M₁ = T²S, M₃ = T²)
-/
import Mathlib

open Matrix Finset

/-! ## §1: Berggren Matrices as Discrete Lorentz Transformations -/

/-- The Minkowski metric η = diag(-1, -1, 1) for the (2,1) signature. -/
def η : Matrix (Fin 3) (Fin 3) ℤ := !![-1, 0, 0; 0, -1, 0; 0, 0, 1]

/-- Berggren matrix B₁. -/
def B₁' : Matrix (Fin 3) (Fin 3) ℤ := !![1, -2, 2; 2, -1, 2; 2, -2, 3]

/-- Berggren matrix B₂. -/
def B₂' : Matrix (Fin 3) (Fin 3) ℤ := !![1, 2, 2; 2, 1, 2; 2, 2, 3]

/-- Berggren matrix B₃. -/
def B₃' : Matrix (Fin 3) (Fin 3) ℤ := !![-1, 2, 2; -2, 1, 2; -2, 2, 3]

/-- B₁ preserves the Lorentz form: B₁ᵀ η B₁ = η. -/
theorem B1_lorentz : B₁'ᵀ * η * B₁' = η := by native_decide

/-- B₂ preserves the Lorentz form: B₂ᵀ η B₂ = η. -/
theorem B2_lorentz : B₂'ᵀ * η * B₂' = η := by native_decide

/-- B₃ preserves the Lorentz form: B₃ᵀ η B₃ = η. -/
theorem B3_lorentz : B₃'ᵀ * η * B₃' = η := by native_decide

/-- B₁ has determinant 1 (proper Lorentz transformation). -/
theorem B1_det : B₁'.det = 1 := by native_decide

/-- B₂ has determinant -1 (improper Lorentz transformation / reflection). -/
theorem B2_det : B₂'.det = -1 := by native_decide

/-- B₃ has determinant 1 (proper Lorentz transformation). -/
theorem B3_det : B₃'.det = 1 := by native_decide

/-! ## §2: Photon Statistics — Bright and Dark Primes -/

/-- A prime is "bright" if it is ≡ 1 (mod 4). -/
def isBrightPrime (p : ℕ) : Prop := Nat.Prime p ∧ p % 4 = 1

/-- A prime is "dark" if it is ≡ 3 (mod 4). -/
def isDarkPrime (p : ℕ) : Prop := Nat.Prime p ∧ p % 4 = 3

/-- Every odd prime is either bright or dark. -/
theorem prime_bright_or_dark (p : ℕ) (hp : Nat.Prime p) (hodd : p ≠ 2) :
    isBrightPrime p ∨ isDarkPrime p := by
  unfold isBrightPrime isDarkPrime
  have h2 : 2 ≤ p := hp.two_le
  have hmod : p % 4 = 1 ∨ p % 4 = 3 := by
    have : p % 2 = 1 := by
      have := hp.odd_of_ne_two hodd
      rw [Nat.odd_iff] at this
      exact this
    omega
  tauto

/-- The number 2 is the unique prime that is neither bright nor dark. -/
theorem two_neither_bright_nor_dark : ¬ isBrightPrime 2 ∧ ¬ isDarkPrime 2 := by
  constructor <;> intro ⟨_, h⟩ <;> omega

/-- Bright primes up to 100. Verified count = 11. -/
theorem bright_count_100 :
    (Finset.filter (fun p => Nat.Prime p ∧ p % 4 = 1) (Finset.range 101)).card = 11 := by
  native_decide

/-- Dark primes up to 100. Verified count = 13. -/
theorem dark_count_100 :
    (Finset.filter (fun p => Nat.Prime p ∧ p % 4 = 3) (Finset.range 101)).card = 13 := by
  native_decide

/-- Chebyshev's bias: dark primes outnumber bright primes up to 100. -/
theorem chebyshev_bias_100 :
    (Finset.filter (fun p => Nat.Prime p ∧ p % 4 = 3) (Finset.range 101)).card >
    (Finset.filter (fun p => Nat.Prime p ∧ p % 4 = 1) (Finset.range 101)).card := by
  native_decide

/-- Chebyshev's bias persists up to 1000. -/
theorem chebyshev_bias_1000 :
    (Finset.filter (fun p => Nat.Prime p ∧ p % 4 = 3) (Finset.range 1001)).card >
    (Finset.filter (fun p => Nat.Prime p ∧ p % 4 = 1) (Finset.range 1001)).card := by
  native_decide

/-! ## §3: Quaternion Properties -/

/-- Quaternions are NOT commutative. -/
theorem quaternion_noncommutative :
    ∃ (a b : Quaternion ℝ), a * b ≠ b * a := by
  exact ⟨⟨0, 1, 0, 0⟩, ⟨0, 0, 1, 0⟩, by
    simp [Quaternion.ext_iff]
    norm_num⟩

/-- Quaternions ARE associative. -/
theorem quaternion_associative (a b c : Quaternion ℝ) :
    a * b * c = a * (b * c) := mul_assoc a b c

/-! ## §4: Composition Algebra Identities -/

/-- Brahmagupta–Fibonacci (2-square) identity — Channel 2. -/
theorem two_square_identity (a b c d : ℤ) :
    (a^2 + b^2) * (c^2 + d^2) = (a*c - b*d)^2 + (a*d + b*c)^2 := by ring

/-- Euler four-square identity — Channel 3. -/
theorem four_square_identity (x₁ x₂ x₃ x₄ y₁ y₂ y₃ y₄ : ℤ) :
    (x₁^2 + x₂^2 + x₃^2 + x₄^2) * (y₁^2 + y₂^2 + y₃^2 + y₄^2) =
    (x₁*y₁ - x₂*y₂ - x₃*y₃ - x₄*y₄)^2 +
    (x₁*y₂ + x₂*y₁ + x₃*y₄ - x₄*y₃)^2 +
    (x₁*y₃ - x₂*y₄ + x₃*y₁ + x₄*y₂)^2 +
    (x₁*y₄ + x₂*y₃ - x₃*y₂ + x₄*y₁)^2 := by ring

/-- The Pythagorean parametrization identity. -/
theorem pythagorean_parametrization (m n : ℤ) :
    (m^2 - n^2)^2 + (2*m*n)^2 = (m^2 + n^2)^2 := by ring

/-! ## §5: Berggren–Theta Group Connection -/

/-- The modular matrices T and S. -/
def modT : Matrix (Fin 2) (Fin 2) ℤ := !![1, 1; 0, 1]
def modS : Matrix (Fin 2) (Fin 2) ℤ := !![0, -1; 1, 0]

/-- The 2×2 Berggren matrices. -/
def M₁' : Matrix (Fin 2) (Fin 2) ℤ := !![2, -1; 1, 0]
def M₃' : Matrix (Fin 2) (Fin 2) ℤ := !![1, 2; 0, 1]

/-- M₁ = T²S: the first Berggren generator is a word in the modular group. -/
theorem M1_eq_T2S : M₁' = modT * modT * modS := by native_decide

/-- M₃ = T²: the third Berggren generator is a power of T. -/
theorem M3_eq_T2 : M₃' = modT * modT := by native_decide

/-- M₁ has determinant 1 (in SL(2,ℤ)). -/
theorem M1_det_one : M₁'.det = 1 := by native_decide

/-- M₃ has determinant 1 (in SL(2,ℤ)). -/
theorem M3_det_one : M₃'.det = 1 := by native_decide

/-- S has order 4 in SL(2,ℤ). -/
theorem S_order_4 : modS ^ 4 = 1 := by native_decide

/-- (ST)³ = S² (the modular relation). -/
theorem modular_relation : (modS * modT) ^ 3 = modS ^ 2 := by native_decide

/-! ## §6: Pythagorean Rotation Gates -/

/-- A Pythagorean rotation matrix. -/
def PythRot (a b : ℤ) : Matrix (Fin 2) (Fin 2) ℤ := !![a, -b; b, a]

/-- Pythagorean rotations are closed under multiplication (= Gaussian integer multiplication). -/
theorem PythRot_mul (a b c d : ℤ) :
    PythRot a b * PythRot c d = PythRot (a*c - b*d) (a*d + b*c) := by
  ext i j; fin_cases i <;> fin_cases j <;>
    simp [PythRot, mul_apply, Fin.sum_univ_two] <;> ring

/-- The determinant of a Pythagorean rotation is the Gaussian norm. -/
theorem PythRot_det (a b : ℤ) : (PythRot a b).det = a^2 + b^2 := by
  simp [PythRot, det_fin_two]; ring

/-- Pythagorean rotations commute (abelian gate set). -/
theorem PythRot_comm (a b c d : ℤ) :
    PythRot a b * PythRot c d = PythRot c d * PythRot a b := by
  rw [PythRot_mul, PythRot_mul]; congr 1 <;> ring

/-! ## §7: Lorentz Form Preservation by Pythagorean Triples -/

/-- The Minkowski form Q(a,b,c) = c² - a² - b². -/
def minkowski_form (v : Fin 3 → ℤ) : ℤ :=
  (v 2)^2 - (v 0)^2 - (v 1)^2

/-- Pythagorean triples are null vectors of the Minkowski form. -/
theorem pyth_triple_null (a b c : ℤ) (h : a^2 + b^2 = c^2) :
    minkowski_form ![a, b, c] = 0 := by
  simp [minkowski_form]; linarith

/-- The Berggren tree preserves nullity (if parent is Pythagorean, so is child). -/
theorem B1_preserves_pyth (a b c : ℤ) (h : a^2 + b^2 = c^2) :
    let v := B₁'.mulVec ![a, b, c]
    (v 0)^2 + (v 1)^2 = (v 2)^2 := by
  simp [B₁', mulVec, dotProduct, Fin.sum_univ_three]
  nlinarith [sq_nonneg a, sq_nonneg b, sq_nonneg c, sq_nonneg (a-b), sq_nonneg (a+b)]

/-! ## §8: Non-Associativity Measures -/

/-- The associator of three elements in a ring. -/
def associator_ring {R : Type*} [Ring R] (x y z : R) : R :=
  (x * y) * z - x * (y * z)

/-- In any associative ring, the associator vanishes. -/
theorem associator_zero_of_assoc {R : Type*} [Ring R] (x y z : R) :
    associator_ring x y z = 0 := by
  simp [associator_ring, mul_assoc]

/-- For quaternions, the associator is always zero (they are associative). -/
theorem quaternion_associator_zero (x y z : Quaternion ℝ) :
    associator_ring x y z = 0 := associator_zero_of_assoc x y z

/-! ## §9: Cayley-Dickson Property Hierarchy -/

/-- The complex numbers are commutative. -/
theorem complex_commutative (z w : ℂ) : z * w = w * z := mul_comm z w

/-- The complex norm is multiplicative. -/
theorem complex_norm_multiplicative (z w : ℂ) :
    Complex.normSq (z * w) = Complex.normSq z * Complex.normSq w :=
  map_mul Complex.normSq z w

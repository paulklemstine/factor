import Mathlib

/-!
# Decoder Applications: Moonshot and Sci-Fi Applications

## Research Team Sigma: Applied Decoding

This file formalizes theorems underlying futuristic applications of the
universal stereographic decoder, from error-correcting codes to
quantum gate synthesis to music theory.
-/

open Real

/-! ## Section 1: Error-Correcting Codes from Number Theory -/

/-- The Gaussian integer norm satisfies a triangle-like inequality -/
theorem gaussian_norm_submult (a₁ b₁ a₂ b₂ : ℤ) :
    (a₁ + a₂) ^ 2 + (b₁ + b₂) ^ 2 ≤
    2 * ((a₁ ^ 2 + b₁ ^ 2) + (a₂ ^ 2 + b₂ ^ 2)) := by
  nlinarith [sq_nonneg (a₁ - a₂), sq_nonneg (b₁ - b₂)]

/-- The unit Gaussian integers: exactly 4 elements of norm 1 (kissing number = 4) -/
theorem gaussian_lattice_neighbors (a b : ℤ) :
    a ^ 2 + b ^ 2 = 1 ↔ (a = 1 ∧ b = 0) ∨ (a = -1 ∧ b = 0) ∨
                          (a = 0 ∧ b = 1) ∨ (a = 0 ∧ b = -1) := by
  constructor
  · intro h
    have ha2 : a ^ 2 ≤ 1 := by nlinarith [sq_nonneg b]
    have hb2 : b ^ 2 ≤ 1 := by nlinarith [sq_nonneg a]
    have ha : a * a ≤ 1 := by nlinarith
    have hb : b * b ≤ 1 := by nlinarith
    have ha_bound : -1 ≤ a ∧ a ≤ 1 := by
      constructor <;> nlinarith [sq_nonneg (a + 1), sq_nonneg (a - 1)]
    have hb_bound : -1 ≤ b ∧ b ≤ 1 := by
      constructor <;> nlinarith [sq_nonneg (b + 1), sq_nonneg (b - 1)]
    rcases ha_bound with ⟨ha_lo, ha_hi⟩
    rcases hb_bound with ⟨hb_lo, hb_hi⟩
    interval_cases a <;> interval_cases b <;> simp_all <;> omega
  · rintro (⟨rfl, rfl⟩ | ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩) <;> norm_num

/-! ## Section 2: Hexagonal lattice (Eisenstein integers) -/

/-
PROBLEM
The hexagonal lattice has kissing number 6

PROVIDED SOLUTION
For the forward direction: Note that a² + ab + b² = (2a+b)² / 4 + 3b²/4 (completing the square). Alternatively, use 4(a² + ab + b²) = (2a+b)² + 3b² = 4, so (2a+b)² + 3b² = 4. Since 3b² ≤ 4, we need b ∈ {-1, 0, 1}. If b=0, then a²=1 so a=±1. If b=±1, then (2a+b)² = 1, so 2a+b = ±1, giving the remaining solutions. For the backward direction, just check each case by norm_num.
-/
theorem hex_lattice_neighbors (a b : ℤ) :
    a ^ 2 + a * b + b ^ 2 = 1 ↔
    (a = 1 ∧ b = 0) ∨ (a = -1 ∧ b = 0) ∨
    (a = 0 ∧ b = 1) ∨ (a = 0 ∧ b = -1) ∨
    (a = 1 ∧ b = -1) ∨ (a = -1 ∧ b = 1) := by
  exact ⟨ fun h => by have : a ≤ 1 := Int.le_of_lt_add_one ( by nlinarith [ sq_nonneg ( a + b ) ] ) ; have : a ≥ -1 := Int.le_of_lt_add_one ( by nlinarith [ sq_nonneg ( a + b ) ] ) ; interval_cases a <;> ( have : b ≤ 1 := Int.le_of_lt_add_one ( by nlinarith ) ; have : b ≥ -1 := Int.le_of_lt_add_one ( by nlinarith ) ; interval_cases b <;> trivial ), by rintro ( ⟨ rfl, rfl ⟩ | ⟨ rfl, rfl ⟩ | ⟨ rfl, rfl ⟩ | ⟨ rfl, rfl ⟩ | ⟨ rfl, rfl ⟩ | ⟨ rfl, rfl ⟩ ) <;> trivial ⟩

/-! ## Section 3: Quantum Gate Synthesis -/

/-- Powers of 2 are sums of four squares — codewords for quantum gates -/
theorem two_pow_sum_four_sq : ∀ n : ℕ,
    ∃ a b c d : ℤ, a ^ 2 + b ^ 2 + c ^ 2 + d ^ 2 = 2 ^ n := by
  intro n
  induction n with
  | zero => exact ⟨1, 0, 0, 0, by norm_num⟩
  | succ n ih =>
    obtain ⟨a, b, c, d, h⟩ := ih
    refine ⟨a + b, a - b, c + d, c - d, ?_⟩
    have key : (a + b) ^ 2 + (a - b) ^ 2 + (c + d) ^ 2 + (c - d) ^ 2 =
               2 * (a ^ 2 + b ^ 2 + c ^ 2 + d ^ 2) := by ring
    rw [key, h]; ring

/-! ## Section 4: Signal Processing — Roots of Unity -/

/-- If ω is a primitive 5th root of unity, then ω⁵ = 1 -/
theorem root_of_unity_sum (ω : ℂ) (h : ω ^ 4 + ω ^ 3 + ω ^ 2 + ω + 1 = 0) :
    ω ^ 5 = 1 := by
  have key : ω ^ 5 - 1 = (ω - 1) * (ω ^ 4 + ω ^ 3 + ω ^ 2 + ω + 1) := by ring
  have h2 : ω ^ 5 - 1 = 0 := by rw [key, h, mul_zero]
  linear_combination h2

/-! ## Section 5: Torus Parametrization (Protein Folding) -/

/-- The torus T² = S¹ × S¹ parametrized by two stereographic coordinates -/
theorem torus_parametrization (s t : ℝ) :
    ((1 - s ^ 2) / (1 + s ^ 2)) ^ 2 + (2 * s / (1 + s ^ 2)) ^ 2 = 1 ∧
    ((1 - t ^ 2) / (1 + t ^ 2)) ^ 2 + (2 * t / (1 + t ^ 2)) ^ 2 = 1 := by
  have hs : (0 : ℝ) < 1 + s ^ 2 := by positivity
  have ht : (0 : ℝ) < 1 + t ^ 2 := by positivity
  constructor <;> (field_simp; ring)

/-! ## Section 6: Music Theory — The Harmonic Decoder -/

/-- The Pythagorean comma: 12 perfect fifths ≈ 7 octaves -/
theorem pythagorean_comma :
    (3 : ℚ) ^ 12 / 2 ^ 19 = 531441 / 524288 := by norm_num

/-- The syntonic comma: 4 fifths vs 2 octaves + major third -/
theorem syntonic_comma :
    (3 : ℚ) ^ 4 / (2 ^ 4 * 5) = 81 / 80 := by norm_num

/-! ## Section 7: Timelike / Lightlike Classification -/

theorem timelike_positive (a b c : ℤ) (h : a ^ 2 + b ^ 2 < c ^ 2) :
    c ^ 2 - a ^ 2 - b ^ 2 > 0 := by omega

theorem lightlike_zero (a b c : ℤ) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    c ^ 2 - a ^ 2 - b ^ 2 = 0 := by omega

/-! ## Section 8: Quantum Dimension Recursion -/

theorem quantum_dim_recursion (d : ℝ) (hd : d ^ 2 = d + 1) :
    d ^ 3 = 2 * d + 1 := by nlinarith

/-! ## Section 9: AdS/CFT Conformal Factor -/

theorem ads_conformal_factor (L z : ℝ) (hz : z ≠ 0) :
    (L / z) ^ 2 * z ^ 2 = L ^ 2 := by field_simp

/-! ## Section 10: Legendre Polynomial Identity -/

theorem legendre_P1_identity (x : ℝ) :
    x ^ 2 + (1 - x ^ 2) = 1 := by ring
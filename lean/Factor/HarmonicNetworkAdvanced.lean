/-
# Harmonic Network: Advanced Formal Verification

This file extends the core formalization in `HarmonicNetwork.lean` with deeper results:

* `relu_preserves_rational` — ReLU activation preserves rationality of vectors
* `stereo_proj_bounded` — Projection components lie in [-1, 1]
* `stereo_proj_neg_symm` — Negation symmetry of the projection
* `stereo_scale_invariant` — Scale invariance of the projection
* `euler_four_square` — Euler's four-square identity for 4D networks
* `stereo_closure_under_multiplication` — Closure under complex multiplication
* `stereo_second_lipschitz` — Lipschitz bound for the second stereographic component
* `rational_approx_error` — Quantization error decreases as 1/(2N)
-/

import Mathlib
import HarmonicNetwork

-- =====================================================================
-- SECTION 1: ReLU PRESERVES RATIONALITY
-- =====================================================================

/-- ReLU applied to a rational number yields a rational number. -/
theorem relu_rational (q : ℚ) : ∃ r : ℚ, r = max 0 q := ⟨max 0 q, rfl⟩

/-- ReLU is nonnegative. -/
theorem relu_nonneg (q : ℚ) : (0 : ℚ) ≤ max 0 q := le_max_left 0 q

/-- ReLU is idempotent: ReLU(ReLU(x)) = ReLU(x). -/
theorem relu_idempotent (q : ℚ) : max 0 (max 0 q) = max 0 q := by
  simp [max_comm, max_assoc, max_self]

/-
PROBLEM
=====================================================================
SECTION 2: PROJECTION BOUNDEDNESS
=====================================================================

The first component of 2D stereographic projection is bounded in [-1, 1].

PROVIDED SOLUTION
We need |2mn/(m²+n²)| ≤ 1. By AM-GM, 2|m||n| ≤ m²+n². So |2mn| = 2|m||n| ≤ m²+n². Since m²+n² > 0, dividing gives the result. Use abs_div, div_le_one, and nlinarith with sq_nonneg (|m| - |n|).
-/
theorem stereo_first_component_bounded (m n : ℝ) (h : m ^ 2 + n ^ 2 ≠ 0) :
    |2 * m * n / (m ^ 2 + n ^ 2)| ≤ 1 := by
  exact abs_le.mpr ⟨ by rw [ le_div_iff₀ ( by positivity ) ] ; nlinarith [ sq_nonneg ( m - n ), sq_nonneg ( m + n ) ], by rw [ div_le_iff₀ ( by positivity ) ] ; nlinarith [ sq_nonneg ( m - n ), sq_nonneg ( m + n ) ] ⟩

/-
PROBLEM
The second component of 2D stereographic projection is bounded in [-1, 1].

PROVIDED SOLUTION
We need |(n²-m²)/(m²+n²)| ≤ 1. Since |n²-m²| ≤ n²+m² = m²+n² (because both m²,n² ≥ 0), dividing by m²+n² > 0 gives the result. Use abs_div, div_le_one, abs_le, and nlinarith with sq_nonneg.
-/
theorem stereo_second_component_bounded (m n : ℝ) (h : m ^ 2 + n ^ 2 ≠ 0) :
    |(n ^ 2 - m ^ 2) / (m ^ 2 + n ^ 2)| ≤ 1 := by
  exact abs_le.mpr ⟨ by rw [ le_div_iff₀ <| by positivity ] ; nlinarith, by rw [ div_le_iff₀ <| by positivity ] ; nlinarith ⟩

-- =====================================================================
-- SECTION 3: NEGATION SYMMETRY
-- =====================================================================

/-- Negating both parameters preserves the first component. -/
theorem stereo_neg_both (m n : ℚ) :
    2 * (-m) * (-n) / ((-m) ^ 2 + (-n) ^ 2) = 2 * m * n / (m ^ 2 + n ^ 2) := by
  ring

/-- Negating only the first parameter negates the first component. -/
theorem stereo_neg_first (m n : ℚ) :
    2 * (-m) * n / ((-m) ^ 2 + n ^ 2) = -(2 * m * n / (m ^ 2 + n ^ 2)) := by
  ring

/-- Swapping parameters swaps the sign of the second component. -/
theorem stereo_swap_second (m n : ℚ) :
    (m ^ 2 - n ^ 2) / (m ^ 2 + n ^ 2) = -((n ^ 2 - m ^ 2) / (m ^ 2 + n ^ 2)) := by
  ring

-- =====================================================================
-- SECTION 4: SUM OF SQUARES PROPERTIES
-- =====================================================================

/-- Sum of squares of a list of integers is nonnegative. -/
theorem sum_sq_nonneg_list (ms : List ℤ) : 0 ≤ (ms.map (· ^ 2)).sum := by
  apply List.sum_nonneg
  intro x hx
  simp only [List.mem_map] at hx
  obtain ⟨a, _, rfl⟩ := hx
  positivity

/-
PROBLEM
Sum of squares is zero iff all elements are zero.

PROVIDED SOLUTION
By induction on ms. Nil case: trivial. Cons case: sum of nonneg terms is 0 iff each is 0. Use List.sum_cons, sq_eq_zero_iff, and the inductive hypothesis.
-/
theorem sum_sq_eq_zero_iff (ms : List ℤ) :
    (ms.map (· ^ 2)).sum = 0 ↔ ∀ m ∈ ms, m = 0 := by
  induction ms <;> simp +contextual [ *, List.sum_cons ];
  constructor <;> intro h;
  · rename_i k l ih;
    exact ⟨ by nlinarith [ List.sum_nonneg ( show ∀ x ∈ List.map ( fun x => x ^ 2 ) l, 0 ≤ x from by intros x hx; rw [ List.mem_map ] at hx; rcases hx with ⟨ y, hy, rfl ⟩ ; positivity ) ], ih.mp <| by nlinarith [ List.sum_nonneg ( show ∀ x ∈ List.map ( fun x => x ^ 2 ) l, 0 ≤ x from by intros x hx; rw [ List.mem_map ] at hx; rcases hx with ⟨ y, hy, rfl ⟩ ; positivity ) ] ⟩;
  · aesop

-- =====================================================================
-- SECTION 5: RATIONAL DOT PRODUCT
-- =====================================================================

/-- The dot product of two rational vectors is rational (closure of ℚ). -/
theorem rational_dot_product (v w : Fin n → ℚ) :
    ∃ r : ℚ, r = ∑ i, v i * w i := ⟨∑ i, v i * w i, rfl⟩

/-- ReLU applied pointwise to a rational vector yields a rational vector. -/
theorem relu_pointwise_rational (v : Fin n → ℚ) :
    ∃ w : Fin n → ℚ, ∀ i, w i = max 0 (v i) :=
  ⟨fun i => max 0 (v i), fun _ => rfl⟩

/-
PROBLEM
=====================================================================
SECTION 6: SECOND COMPONENT LIPSCHITZ BOUND
=====================================================================

The second component of stereographic projection, g(t) = (1-t²)/(1+t²),
    also satisfies a Lipschitz bound for |t| ≤ 1.

PROVIDED SOLUTION
Write g(t) = (1-t²)/(1+t²). Then g(t₁) - g(t₂) = [(1-t₁²)(1+t₂²) - (1-t₂²)(1+t₁²)] / [(1+t₁²)(1+t₂²)] = [1+t₂²-t₁²-t₁²t₂² - 1 - t₁² + t₂² + t₁²t₂²] / [(1+t₁²)(1+t₂²)] = [2t₂²-2t₁²]/[(1+t₁²)(1+t₂²)] = 2(t₂-t₁)(t₂+t₁)/[(1+t₁²)(1+t₂²)]. So |g(t₁)-g(t₂)| = 2|t₁-t₂|·|t₁+t₂|/[(1+t₁²)(1+t₂²)]. We need |t₁+t₂| ≤ (1+t₁²)(1+t₂²). Since |t₁|,|t₂| ≤ 1, |t₁+t₂| ≤ 2 and (1+t₁²)(1+t₂²) ≥ 1+t₁²+t₂² ≥ 1+|t₁+t₂|-1 = |t₁+t₂| when |t₁+t₂| ≤ 2. Actually simpler: (1+t₁²)(1+t₂²) ≥ 2|t₁|·2|t₂| ≥ ... Try: factor algebraically using div_sub_div, then bound the ratio. Use nlinarith with sq_nonneg hints.
-/
theorem stereo_second_lipschitz (t₁ t₂ : ℝ) (ht₁ : |t₁| ≤ 1) (ht₂ : |t₂| ≤ 1) :
    |(1 - t₁ ^ 2) / (1 + t₁ ^ 2) - (1 - t₂ ^ 2) / (1 + t₂ ^ 2)| ≤ 2 * |t₁ - t₂| := by
  field_simp;
  -- We'll use the fact that |t₁ + t₂| ≤ 2 and (1 + t₁^2)(1 + t₂^2) ≥ 1 to bound the expression.
  have h_bound : |(t₂ - t₁) * (t₂ + t₁)| ≤ 2 * |t₁ - t₂| * ((1 + t₁^2) * (1 + t₂^2)) / 2 := by
    rw [ abs_mul, abs_sub_comm ] ; ring_nf ; (
    -- We can divide both sides by $|t₁ - t₂|$ (which is positive since $t₁ \neq t₂$).
    suffices h_div : |t₁ + t₂| ≤ t₁ ^ 2 * t₂ ^ 2 + t₁ ^ 2 + t₂ ^ 2 + 1 by
      nlinarith [ abs_nonneg ( t₁ - t₂ ) ];
    exact abs_le.mpr ⟨ by nlinarith only [ sq_nonneg ( t₁ - t₂ ), sq_nonneg ( t₁ + t₂ ), abs_le.mp ht₁, abs_le.mp ht₂ ], by nlinarith only [ sq_nonneg ( t₁ - t₂ ), sq_nonneg ( t₁ + t₂ ), abs_le.mp ht₁, abs_le.mp ht₂ ] ⟩);
  rw [ abs_le ] at *;
  exact ⟨ by rw [ le_div_iff₀ <| by positivity ] ; nlinarith, by rw [ div_le_iff₀ <| by positivity ] ; nlinarith ⟩

/-
PROBLEM
=====================================================================
SECTION 7: QUANTIZATION ERROR BOUND
=====================================================================

If we approximate a target rational t₀ by p/N for the nearest integer p,
    then |p/N - t₀| ≤ 1/(2N).

PROVIDED SOLUTION
Let p = round(t₀ * N) = ⌊t₀ * N + 1/2⌋. Then |p - t₀*N| ≤ 1/2, so |p/N - t₀| ≤ 1/(2N). Use Int.floor or round. Actually simplest: use p = ⌈t₀ * N - 1/2⌉ or just p = ⌊t₀ * N⌋ and get |p/N - t₀| ≤ 1/N which is ≤ 1/(2N) only if N ≥ 2... Actually |⌊t₀*N⌋/N - t₀| ≤ 1/N, not 1/(2N). For 1/(2N), use p = round(t₀*N). Try using Int.floor: let p = ⌊t₀ * ↑N + 1/2⌋, then ⌊x⌋ ≤ x < ⌊x⌋+1 implies |⌊x⌋ - x| ≤ 1, hence |p - t₀*N - 1/2| ≤ 1, so |p - t₀*N| ≤ 1/2 + ... Hmm, more carefully: ⌊x⌋ ≤ x and x < ⌊x⌋+1, so 0 ≤ x - ⌊x⌋ < 1. Let x = t₀*N + 1/2, p = ⌊x⌋. Then 0 ≤ t₀*N + 1/2 - p < 1, so -1/2 ≤ t₀*N - p < 1/2, so |p - t₀*N| ≤ 1/2, so |p/N - t₀| ≤ 1/(2N).
-/
theorem rational_approx_error (t₀ : ℚ) (N : ℕ) (hN : 0 < N) :
    ∃ p : ℤ, |p / (N : ℚ) - t₀| ≤ 1 / (2 * N) := by
  refine' ⟨ ⌊t₀ * N + 1 / 2⌋, _ ⟩ ; rw [ abs_le ] ; constructor <;> norm_num [ mul_assoc, mul_comm, mul_left_comm ] at * <;> ring_nf at * <;> norm_num [ hN.ne' ] at *;
  · field_simp;
    linarith [ Int.lt_floor_add_one ( ( 1 + t₀ * 2 * N ) / 2 ) ];
  · field_simp;
    linarith [ Int.floor_le ( ( 1 + 2 * t₀ * N ) / 2 ) ]

-- =====================================================================
-- SECTION 8: SCALE INVARIANCE
-- =====================================================================

/-- Scaling the integer vector by a nonzero constant does not change the
    projected rational point. The projection is scale-invariant. -/
theorem stereo_scale_invariant (m n k : ℚ) (hk : k ≠ 0) (_h : m ^ 2 + n ^ 2 ≠ 0) :
    2 * (k * m) * (k * n) / ((k * m) ^ 2 + (k * n) ^ 2) =
    2 * m * n / (m ^ 2 + n ^ 2) := by
  have hk2 : k ^ 2 ≠ 0 := pow_ne_zero 2 hk
  have hc : (k * m) ^ 2 + (k * n) ^ 2 = k ^ 2 * (m ^ 2 + n ^ 2) := by ring
  rw [hc, show 2 * (k * m) * (k * n) = k ^ 2 * (2 * m * n) from by ring]
  exact mul_div_mul_left _ (m ^ 2 + n ^ 2) hk2

/-- The second component is also scale-invariant. -/
theorem stereo_scale_invariant_second (m n k : ℚ) (hk : k ≠ 0) (_h : m ^ 2 + n ^ 2 ≠ 0) :
    ((k * n) ^ 2 - (k * m) ^ 2) / ((k * m) ^ 2 + (k * n) ^ 2) =
    (n ^ 2 - m ^ 2) / (m ^ 2 + n ^ 2) := by
  have hk2 : k ^ 2 ≠ 0 := pow_ne_zero 2 hk
  have hc : (k * m) ^ 2 + (k * n) ^ 2 = k ^ 2 * (m ^ 2 + n ^ 2) := by ring
  rw [hc, show (k * n) ^ 2 - (k * m) ^ 2 = k ^ 2 * (n ^ 2 - m ^ 2) from by ring]
  exact mul_div_mul_left _ (m ^ 2 + n ^ 2) hk2

-- =====================================================================
-- SECTION 9: EULER'S FOUR-SQUARE IDENTITY
-- =====================================================================

/-- Euler's four-square identity: the product of two sums of four squares
    is again a sum of four squares. This extends the Brahmagupta-Fibonacci
    identity to higher dimensions, relevant for 4D Harmonic Networks. -/
theorem euler_four_square (a₁ a₂ a₃ a₄ b₁ b₂ b₃ b₄ : ℤ) :
    (a₁^2 + a₂^2 + a₃^2 + a₄^2) * (b₁^2 + b₂^2 + b₃^2 + b₄^2) =
    (a₁*b₁ - a₂*b₂ - a₃*b₃ - a₄*b₄)^2 +
    (a₁*b₂ + a₂*b₁ + a₃*b₄ - a₄*b₃)^2 +
    (a₁*b₃ - a₂*b₄ + a₃*b₁ + a₄*b₂)^2 +
    (a₁*b₄ + a₂*b₃ - a₃*b₂ + a₄*b₁)^2 := by
  ring

-- =====================================================================
-- SECTION 10: CLOSURE UNDER MULTIPLICATION
-- =====================================================================

/-- The complex product of two stereographically-projected points
    remains on the unit circle. -/
theorem stereo_closure_under_multiplication (m₁ n₁ m₂ n₂ : ℤ)
    (h1 : (m₁ : ℚ) ^ 2 + (n₁ : ℚ) ^ 2 ≠ 0)
    (h2 : (m₂ : ℚ) ^ 2 + (n₂ : ℚ) ^ 2 ≠ 0) :
    let x₁ := 2 * (m₁ : ℚ) * n₁ / ((m₁ : ℚ) ^ 2 + (n₁ : ℚ) ^ 2)
    let y₁ := ((n₁ : ℚ) ^ 2 - (m₁ : ℚ) ^ 2) / ((m₁ : ℚ) ^ 2 + (n₁ : ℚ) ^ 2)
    let x₂ := 2 * (m₂ : ℚ) * n₂ / ((m₂ : ℚ) ^ 2 + (n₂ : ℚ) ^ 2)
    let y₂ := ((n₂ : ℚ) ^ 2 - (m₂ : ℚ) ^ 2) / ((m₂ : ℚ) ^ 2 + (n₂ : ℚ) ^ 2)
    (x₁ * x₂ - y₁ * y₂) ^ 2 + (x₁ * y₂ + y₁ * x₂) ^ 2 = 1 := by
  simp only
  field_simp
  ring

-- =====================================================================
-- SECTION 11: CALIBRATION POINTS
-- =====================================================================

/-- The stereographic map t ↦ 2t/(1+t²) maps 0 to 0. -/
theorem stereo_calibration_zero : (2 : ℚ) * 0 / (1 + 0 ^ 2) = 0 := by norm_num

/-- The stereographic map t ↦ 2t/(1+t²) maps 1 to 1. -/
theorem stereo_calibration_one : (2 : ℚ) * 1 / (1 + 1 ^ 2) = 1 := by norm_num

/-- The first component is an odd function. -/
theorem stereo_first_odd (t : ℚ) :
    2 * (-t) / (1 + (-t) ^ 2) = -(2 * t / (1 + t ^ 2)) := by ring

/-- The second component is an even function. -/
theorem stereo_second_even (t : ℚ) :
    (1 - (-t) ^ 2) / (1 + (-t) ^ 2) = (1 - t ^ 2) / (1 + t ^ 2) := by ring

-- =====================================================================
-- SECTION 12: ALTERNATIVE NORM PRODUCT
-- =====================================================================

/-- The product of norms equals the norm of the product (Gaussian integer view):
    |z₁|²·|z₂|² = |z₁·z₂|² where z = a + bi. -/
theorem cayley_dickson_norm (a b c d : ℤ) :
    (a ^ 2 + b ^ 2) * (c ^ 2 + d ^ 2) =
    (a * c + b * d) ^ 2 + (a * d - b * c) ^ 2 := by
  ring

-- =====================================================================
-- SECTION 13: NETWORK DEPTH — UNIT NORM CHAIN
-- =====================================================================

/-- Composing two unit vectors via complex multiplication preserves unit norm.
    This is the key lemma for network depth composition. -/
theorem unit_complex_mul_norm (a b c d : ℚ)
    (h1 : a ^ 2 + b ^ 2 = 1) (h2 : c ^ 2 + d ^ 2 = 1) :
    (a * c - b * d) ^ 2 + (a * d + b * c) ^ 2 = 1 := by
  nlinarith [sq_nonneg (a * c - b * d), sq_nonneg (a * d + b * c),
             sq_nonneg a, sq_nonneg b, sq_nonneg c, sq_nonneg d]

-- =====================================================================
-- SECTION 14: PROJECTION CROSS-RATIO
-- =====================================================================

/-- If two parameter pairs produce the same first projected component,
    the cross-ratio condition holds. -/
theorem stereo_cross_ratio (m₁ n₁ m₂ n₂ : ℚ)
    (h1 : m₁ ^ 2 + n₁ ^ 2 ≠ 0) (h2 : m₂ ^ 2 + n₂ ^ 2 ≠ 0)
    (hx : 2 * m₁ * n₁ / (m₁ ^ 2 + n₁ ^ 2) = 2 * m₂ * n₂ / (m₂ ^ 2 + n₂ ^ 2)) :
    m₁ * n₁ * (m₂ ^ 2 + n₂ ^ 2) = m₂ * n₂ * (m₁ ^ 2 + n₁ ^ 2) := by
  field_simp at hx
  linarith

-- =====================================================================
-- SECTION 15: FINSET SUM NUMERATOR IDENTITY
-- =====================================================================

/-- The N-dimensional projection numerator identity using Finset.sum.
    This is the type-safe version of `projection_numerator_eq_sq`. -/
theorem projection_numerator_fin (n : ℕ) (t : ℤ) (m : Fin n → ℤ) :
    (∑ i : Fin n, (2 * m i * t) ^ 2) + (t ^ 2 - ∑ i : Fin n, (m i) ^ 2) ^ 2 =
    (t ^ 2 + ∑ i : Fin n, (m i) ^ 2) ^ 2 := by
  have key : ∑ i : Fin n, (2 * m i * t) ^ 2 =
      4 * t ^ 2 * ∑ i : Fin n, (m i) ^ 2 := by
    simp only [mul_pow]
    rw [Finset.mul_sum]
    congr 1; ext i; ring
  linarith [generalized_pythagorean_identity t (∑ i : Fin n, (m i) ^ 2)]
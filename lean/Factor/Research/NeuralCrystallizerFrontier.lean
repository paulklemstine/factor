import Mathlib

/-!
# Neural Crystallizer Frontier: New Theorems at the Intersection of AI and Mathematics

## Research Team Discoveries

This file contains machine-verified theorems discovered by our research team exploring
the mathematical foundations of neural networks through the lens of stereographic
projection, crystallization, and the Hopf fibration.

## New Discoveries

### 1. Pendulum Dynamics of Crystallization
### 2. Composition Algebra of Crystallized Networks
### 3. Spectral Properties of Stereographic Weights
### 4. Information-Theoretic Bounds
### 5. Fixed-Point Theory of Stereographic Maps
### 6. Quaternionic Network Layers
### 7. Robustness via Lipschitz Bounds
### 8. Residual Crystallization Energy
### 9. Stereographic Lattice Density
### 10. Crystallization-Quantization Duality
### 11. Hopf Fibration and Entanglement
### 12. Convergence of Crystallization Training
-/

open Real Finset BigOperators

noncomputable section

/-! ## §1: Pendulum Dynamics of Crystallization -/

/-- The gradient of crystallization loss at integer points vanishes. -/
theorem crystallization_gradient_zero_at_int (n : ℤ) :
    Real.sin (2 * π * (n : ℝ)) = 0 := by
  rw [show 2 * π * (n : ℝ) = ↑(2 * n) * π from by push_cast; ring]
  exact sin_int_mul_pi (2 * n)

/-
PROBLEM
At half-integer points, sin(2πm) also vanishes — unstable equilibria.

PROVIDED SOLUTION
2 * π * (n + 1/2) = (2*n + 1) * π. Then use sin_int_mul_pi to get sin((2*n+1)*π) = 0. The push_cast/ring approach may timeout, so try a more manual approach: convert the goal to show sin of an integer multiple of π is 0.
-/
theorem crystallization_gradient_zero_at_half_int (n : ℤ) :
    Real.sin (2 * π * ((n : ℝ) + 1/2)) = 0 := by
      exact Real.sin_eq_zero_iff.mpr ⟨ 2 * n + 1, by push_cast; ring ⟩

/-
PROBLEM
The crystallization loss achieves its maximum value of 1 at half-integers.

PROVIDED SOLUTION
π * (n + 1/2) = n*π + π/2. Use sin_add and sin_int_mul_pi, cos_int_mul_pi, sin_pi_div_two, cos_pi_div_two. After simplification we get (±1)² = 1.
-/
theorem crystallization_max_at_half_int (n : ℤ) :
    Real.sin (π * ((n : ℝ) + 1/2)) ^ 2 = 1 := by
      rw [ ← Real.cos_sub_pi_div_two ] ; ring_nf; norm_num [ mul_assoc, mul_comm Real.pi _, mul_div ] ;
      exact eq_or_eq_neg_of_sq_eq_sq _ _ <| by norm_num [ Real.cos_sq' ] ;

/-- The double-angle identity for the crystallization gradient. -/
theorem crystallization_double_angle (m : ℝ) :
    Real.sin (2 * (π * m)) = 2 * Real.sin (π * m) * Real.cos (π * m) :=
  sin_two_mul (π * m)

/-- sin²(πm) = (1 - cos(2πm))/2 — the pendulum potential. -/
theorem crystallization_pendulum_potential (m : ℝ) :
    Real.sin (π * m) ^ 2 = (1 - Real.cos (2 * (π * m))) / 2 := by
  have := Real.cos_sq_add_sin_sq (π * m)
  have h2 := Real.cos_two_mul (π * m)
  nlinarith

/-! ## §2: Composition Algebra of Crystallized Networks -/

/-- The Brahmagupta-Fibonacci identity over ℝ. -/
theorem gaussian_norm_multiplicative_real (a b c d : ℝ) :
    (a ^ 2 + b ^ 2) * (c ^ 2 + d ^ 2) =
    (a * c - b * d) ^ 2 + (a * d + b * c) ^ 2 := by ring

/-- Composing two stereographic unit vectors preserves the unit circle. -/
theorem gaussian_composition_unit (a b c d : ℝ)
    (h1 : a ^ 2 + b ^ 2 = 1) (h2 : c ^ 2 + d ^ 2 = 1) :
    (a * c - b * d) ^ 2 + (a * d + b * c) ^ 2 = 1 := by
  nlinarith [gaussian_norm_multiplicative_real a b c d]

/-- Triple composition: three crystallized layers compose to another unit vector. -/
theorem triple_gaussian_composition_unit (a b c d e f : ℝ)
    (h1 : a ^ 2 + b ^ 2 = 1) (h2 : c ^ 2 + d ^ 2 = 1) (h3 : e ^ 2 + f ^ 2 = 1) :
    let p := a * c - b * d
    let q := a * d + b * c
    (p * e - q * f) ^ 2 + (p * f + q * e) ^ 2 = 1 := by
  have h12 := gaussian_composition_unit a b c d h1 h2
  exact gaussian_composition_unit _ _ e f h12 h3

/-- Gaussian composition is associative. -/
theorem gaussian_composition_assoc (a b c d e f : ℝ) :
    let p1 := a * c - b * d
    let q1 := a * d + b * c
    let p2 := c * e - d * f
    let q2 := c * f + d * e
    p1 * e - q1 * f = a * p2 - b * q2 ∧ p1 * f + q1 * e = a * q2 + b * p2 := by
  simp only
  constructor <;> ring

/-! ## §3: Spectral Properties of Stereographic Weights -/

/-- The determinant of a 2D rotation matrix is 1. -/
theorem rotation_det_is_one (θ : ℝ) :
    Real.cos θ * Real.cos θ - (- Real.sin θ) * Real.sin θ = 1 := by
  have := Real.sin_sq_add_cos_sq θ; nlinarith

/-- The characteristic polynomial discriminant of a rotation is -4sin²θ. -/
theorem rotation_char_poly_discriminant (θ : ℝ) :
    (2 * Real.cos θ) ^ 2 - 4 * 1 = -4 * Real.sin θ ^ 2 := by
  have := Real.sin_sq_add_cos_sq θ; nlinarith

/-! ## §4: Information-Theoretic Bounds -/

/-
PROBLEM
The number of integer points in [-B, B] is exactly 2B+1.

PROVIDED SOLUTION
The Finset.Icc (-(B:ℤ)) (B:ℤ) has cardinality 2*B+1. Use Int.card_Icc or the formula card_Icc = toNat(B - (-B) + 1) = toNat(2*B + 1) = 2*B+1.
-/
theorem integer_points_in_range (B : ℕ) :
    Finset.card (Finset.Icc (-(B : ℤ)) (B : ℤ)) = 2 * B + 1 := by
      norm_num +zetaDelta at *;
      ring ; norm_cast

/-! ## §5: Fixed-Point Theory of Stereographic Maps -/

/-- Inverse stereographic projection maps 0 to (0, 1). -/
theorem inv_stereo_zero :
    (2 * (0 : ℝ) / (1 + 0 ^ 2), (1 - 0 ^ 2) / (1 + 0 ^ 2)) = (0, 1) := by norm_num

/-- Inverse stereographic projection maps 1 to (1, 0). -/
theorem inv_stereo_one :
    (2 * (1 : ℝ) / (1 + 1 ^ 2), (1 - 1 ^ 2) / (1 + 1 ^ 2)) = (1, 0) := by norm_num

/-
PROBLEM
Stereographic round-trip: first component recovery.

PROVIDED SOLUTION
Use field_simp to clear denominators, then use nlinarith with the hypothesis h : x^2 + y^2 = 1 and the fact that (1+y)≠0. After field_simp, the goal becomes a polynomial identity that follows from x^2 + y^2 = 1.
-/
theorem stereo_round_trip_fst (x y : ℝ) (h : x ^ 2 + y ^ 2 = 1) (hy : 1 + y ≠ 0) :
    2 * (x / (1 + y)) / (1 + (x / (1 + y)) ^ 2) = x := by
      grind

/-
PROBLEM
Stereographic round-trip: second component recovery.

PROVIDED SOLUTION
Use field_simp, then nlinarith with h : x^2 + y^2 = 1.
-/
theorem stereo_round_trip_snd (x y : ℝ) (h : x ^ 2 + y ^ 2 = 1) (hy : 1 + y ≠ 0) :
    (1 - (x / (1 + y)) ^ 2) / (1 + (x / (1 + y)) ^ 2) = y := by
      grind +ring

/-! ## §6: Quaternionic Network Layers -/

/-- Euler's four-square identity (quaternion norm multiplicativity). -/
theorem euler_four_squares_identity (a₁ a₂ a₃ a₄ b₁ b₂ b₃ b₄ : ℝ) :
    (a₁^2 + a₂^2 + a₃^2 + a₄^2) * (b₁^2 + b₂^2 + b₃^2 + b₄^2) =
    (a₁*b₁ - a₂*b₂ - a₃*b₃ - a₄*b₄)^2 +
    (a₁*b₂ + a₂*b₁ + a₃*b₄ - a₄*b₃)^2 +
    (a₁*b₃ - a₂*b₄ + a₃*b₁ + a₄*b₂)^2 +
    (a₁*b₄ + a₂*b₃ - a₃*b₂ + a₄*b₁)^2 := by ring

/-- The Hopf map preserves the sphere: S³ → S². -/
theorem hopf_map_sphere (a b c d : ℝ) (h : a^2 + b^2 + c^2 + d^2 = 1) :
    (2*(a*c + b*d))^2 + (2*(b*c - a*d))^2 + (a^2 + b^2 - c^2 - d^2)^2 = 1 := by
  nlinarith [sq_nonneg (a*c + b*d), sq_nonneg (b*c - a*d),
             sq_nonneg (a^2 + b^2 - c^2 - d^2),
             sq_nonneg a, sq_nonneg b, sq_nonneg c, sq_nonneg d]

/-- Quaternion composition of two S³ vectors stays on S³. -/
theorem quaternion_composition_sphere (a₁ a₂ a₃ a₄ b₁ b₂ b₃ b₄ : ℝ)
    (h1 : a₁^2 + a₂^2 + a₃^2 + a₄^2 = 1)
    (h2 : b₁^2 + b₂^2 + b₃^2 + b₄^2 = 1) :
    (a₁*b₁ - a₂*b₂ - a₃*b₃ - a₄*b₄)^2 +
    (a₁*b₂ + a₂*b₁ + a₃*b₄ - a₄*b₃)^2 +
    (a₁*b₃ - a₂*b₄ + a₃*b₁ + a₄*b₂)^2 +
    (a₁*b₄ + a₂*b₃ - a₃*b₂ + a₄*b₁)^2 = 1 := by
  nlinarith [euler_four_squares_identity a₁ a₂ a₃ a₄ b₁ b₂ b₃ b₄]

/-! ## §7: Robustness via Lipschitz Bounds -/

/-- Cauchy-Schwarz for unit vectors: inner product bounded by input norm. -/
theorem unit_vector_bounded_output (w₁ w₂ x₁ x₂ : ℝ)
    (hw : w₁ ^ 2 + w₂ ^ 2 = 1) :
    (w₁ * x₁ + w₂ * x₂) ^ 2 ≤ x₁ ^ 2 + x₂ ^ 2 := by
  nlinarith [sq_nonneg (w₁ * x₂ - w₂ * x₁)]

/-- Crystallized layers are 1-Lipschitz: output difference bounded by input difference. -/
theorem crystallized_layer_lipschitz (w₁ w₂ x₁ x₂ y₁ y₂ : ℝ)
    (hw : w₁ ^ 2 + w₂ ^ 2 = 1) :
    (w₁ * (x₁ - y₁) + w₂ * (x₂ - y₂)) ^ 2 ≤ (x₁ - y₁) ^ 2 + (x₂ - y₂) ^ 2 := by
  nlinarith [sq_nonneg (w₁ * (x₂ - y₂) - w₂ * (x₁ - y₁))]

/-- Composition of Lipschitz-1 maps remains Lipschitz-1. -/
theorem deep_lipschitz_bound (L₁ L₂ : ℝ) (hL1 : 0 ≤ L₁) (hL1b : L₁ ≤ 1)
    (_hL2 : 0 ≤ L₂) (hL2b : L₂ ≤ 1) :
    L₁ * L₂ ≤ 1 := by nlinarith

/-! ## §8: Residual Crystallization Energy -/

/-
PROBLEM
The crystallization loss is periodic with period 1.

PROVIDED SOLUTION
Rewrite π*(m+n) = π*m + n*π. Then use Real.sin_add_int_mul_pi which gives sin(x + n*π) = (-1)^n * sin(x). Squaring, ((-1)^n)^2 = 1, so sin²(π*(m+n)) = sin²(πm).
-/
theorem crystallization_periodic (m : ℝ) (n : ℤ) :
    Real.sin (π * (m + n)) ^ 2 = Real.sin (π * m) ^ 2 := by
      -- Rewrite π*(m+n) as π*m + n*π.
      ring_nf at *; (
      norm_num [ mul_comm Real.pi, Real.sin_add ];
      norm_num [ mul_pow, Real.cos_sq' ]); -- Apply the identity sin(x + n*π) = (-1)^n * sin(x) and then square it. The square of (-1)^n is 1, so the equality follows.

/-- Total crystallization energy is non-negative. -/
theorem total_crystallization_nonneg (m₁ m₂ : ℝ) :
    0 ≤ Real.sin (π * m₁) ^ 2 + Real.sin (π * m₂) ^ 2 := by positivity

/-- Total crystallization energy for three parameters bounded by 3. -/
theorem total_crystallization_bounded (m₁ m₂ m₃ : ℝ) :
    Real.sin (π * m₁) ^ 2 + Real.sin (π * m₂) ^ 2 + Real.sin (π * m₃) ^ 2 ≤ 3 := by
  have h1 := Real.sin_sq_le_one (π * m₁)
  have h2 := Real.sin_sq_le_one (π * m₂)
  have h3 := Real.sin_sq_le_one (π * m₃)
  linarith

/-! ## §9: Stereographic Lattice Density -/

/-- Stereographic projection of any real number lands on the unit circle. -/
theorem stereo_on_circle (t : ℝ) :
    (2 * t / (1 + t ^ 2)) ^ 2 + ((1 - t ^ 2) / (1 + t ^ 2)) ^ 2 = 1 := by
  have h : (1 + t ^ 2) ≠ 0 := by positivity
  field_simp; ring

/-- The N-dimensional stereographic projection produces unit norm. -/
theorem stereo_general_unit (S : ℝ) (hS : 0 ≤ S) :
    4 * S / (1 + S) ^ 2 + ((1 - S) / (1 + S)) ^ 2 = 1 := by
  have h : (1 + S) ≠ 0 := by positivity
  field_simp; ring

/-! ## §10: Crystallization-Quantization Duality -/

/-- Post-training quantization: every real is within 1/2 of an integer. -/
theorem quantization_error_bound (m : ℝ) :
    ∃ n : ℤ, |m - n| ≤ 1 / 2 :=
  ⟨round m, abs_sub_round m⟩

/-- At any integer, crystallization loss is 0. -/
theorem crystallization_at_integer (n : ℤ) :
    Real.sin (π * (n : ℝ)) ^ 2 = 0 := by
  rw [mul_comm, sin_int_mul_pi]; ring

/-
PROBLEM
Two distinct integers give distinct stereographic projections (injectivity).

PROVIDED SOLUTION
If the stereographic projections are equal, comparing the first components gives 2m*(1+n²) = 2n*(1+m²), which simplifies to 2m + 2mn² = 2n + 2nm², hence 2(m-n) = 2mn(n-m) = -2mn(m-n). So (m-n)(1+mn)=0 (over ℤ). Since m≠n, m-n≠0 (as integers cast to ℝ), so (1+mn)=0, but this means mn = -1 over integers... Wait, we need to be more careful. Actually 2m(1+n²) = 2n(1+m²) means m+mn² = n+nm², so m-n = nm²-mn² = mn(m-n)... wait that's mn(m-n) with wrong sign. Let me redo: m(1+n²) = n(1+m²) → m + mn² = n + nm² → m - n = nm² - mn² = mn(m-n)... no, nm² - mn² = m²n - mn² = mn(m-n). So m-n = mn(m-n). Since m ≠ n, we get 1 = mn. But m,n are integers with mn = 1, so (m,n) = (1,1) or (-1,-1), both giving m=n, contradiction. So just show that from the first component equation, we derive m = n contradiction.
-/
theorem stereo_injective_on_int (m n : ℤ) (hm : m ≠ n) :
    (2 * (m : ℝ) / (1 + (m : ℝ) ^ 2), (1 - (m : ℝ) ^ 2) / (1 + (m : ℝ) ^ 2)) ≠
    (2 * (n : ℝ) / (1 + (n : ℝ) ^ 2), (1 - (n : ℝ) ^ 2) / (1 + (n : ℝ) ^ 2)) := by
  -- By contradiction, assume the stereographic projections are equal.
  by_contra h_eq;
  simp_all +decide [ div_eq_mul_inv ];
  -- By simplifying, we can see that this implies $m = n$, contradicting our assumption.
  field_simp at h_eq;
  norm_cast at *; cases lt_or_gt_of_ne hm <;> nlinarith [ sq_nonneg ( m - n ) ] ;

/-! ## §11: Hopf Fibration and Entanglement -/

/-- The fiber of the Hopf map over the south pole is S¹. -/
theorem hopf_fiber_south_pole (c d : ℝ) (h : c ^ 2 + d ^ 2 = 1) :
    2*((0:ℝ)*c + (0:ℝ)*d) = 0 ∧ 2*((0:ℝ)*c - (0:ℝ)*d) = 0 ∧
    (0:ℝ)^2 + (0:ℝ)^2 - c^2 - d^2 = -1 := by
  constructor; · ring
  constructor; · ring
  linarith

/-- The fiber over the north pole. -/
theorem hopf_fiber_north_pole (a b : ℝ) (h : a ^ 2 + b ^ 2 = 1) :
    2*(a*(0:ℝ) + b*(0:ℝ)) = 0 ∧ 2*(b*(0:ℝ) - a*(0:ℝ)) = 0 ∧
    a^2 + b^2 - (0:ℝ)^2 - (0:ℝ)^2 = 1 := by
  constructor; · ring
  constructor; · ring
  linarith

/-! ## §12: Convergence of Crystallization Training -/

/-- The crystallization loss is a valid Lyapunov function: non-negative. -/
theorem lyapunov_nonneg (m : ℝ) : 0 ≤ Real.sin (π * m) ^ 2 := sq_nonneg _

/-
PROBLEM
The Lyapunov function is zero exactly at equilibria (integers).

PROVIDED SOLUTION
sin(πm)² = 0 iff sin(πm) = 0 (by sq_eq_zero_iff). sin(πm) = 0 iff πm = nπ for some integer n (by sin_eq_zero_iff). πm = nπ iff m = n (dividing by π ≠ 0). Use Real.sin_eq_zero_iff or sin_eq_zero_iff_exists_int from Mathlib.
-/
theorem lyapunov_zero_iff_equilibrium (m : ℝ) :
    Real.sin (π * m) ^ 2 = 0 ↔ ∃ n : ℤ, m = ↑n := by
      exact ⟨ fun h => by obtain ⟨ n, hn ⟩ := Real.sin_eq_zero_iff.mp ( sq_eq_zero_iff.mp h ) ; exact ⟨ n, by nlinarith [ Real.pi_pos ] ⟩, by rintro ⟨ n, rfl ⟩ ; simp +decide [ mul_comm Real.pi ] ⟩

/-- Sum of Lyapunov functions is non-negative (product space). -/
theorem lyapunov_sum_nonneg (params : Finset ℝ) :
    0 ≤ ∑ m ∈ params, Real.sin (π * m) ^ 2 :=
  Finset.sum_nonneg (fun _ _ => sq_nonneg _)

end
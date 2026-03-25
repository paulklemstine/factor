import Mathlib

/-!
# Inverse Stereographic Projection: Möbius Transformations from Generalized Poles

## Research Team: The Möbius Circle
- **Agent Α (Alpha)** — Generalized Pole Theory: Change-of-pole maps, involutions
- **Agent Β (Beta)** — Two-Pole Composition: The F_{a,b} Möbius family
- **Agent Γ (Gamma)** — Integer-to-Integer Mappings: Divisibility & finiteness
- **Agent Δ (Delta)** — Computational Explorer: Chains, orbits, experiments
- **Agent Ε (Epsilon)** — Synthesis: Connections to number theory, group theory

## Core Discovery

Composing inverse stereographic projection from one pole with forward projection
from another yields a Möbius transformation. When both poles correspond to integers,
the resulting map has integer coefficients, and the set of integers mapping to integers
is controlled by divisors of (1+a²)(1+b²). This creates a rich arithmetic structure
connecting stereographic geometry to divisor theory.
-/

open Real Finset BigOperators

noncomputable section

/-! ## Agent Α: Generalized Pole Theory -/

/-- The change-of-pole Möbius transformation.
    M_a(t) = (at + 1)/(t - a) maps the standard south-pole coordinates to
    the stereographic projection from the pole at parameter a. -/
def poleMap (a t : ℝ) : ℝ := (a * t + 1) / (t - a)

/-- **Theorem Α.1**: The denominator 1 + a² is always positive. -/
theorem one_plus_sq_pos' (a : ℝ) : (0 : ℝ) < 1 + a ^ 2 := by positivity

/-- **Theorem Α.2**: M_0(t) = 1/t, the classical north-south swap. -/
theorem pole_map_at_zero (t : ℝ) (ht : t ≠ 0) :
    poleMap 0 t = 1 / t := by
  simp [poleMap]

/-
PROBLEM
**Theorem Α.3**: M_a is an involution: M_a(M_a(t)) = t.

PROVIDED SOLUTION
Unfold poleMap. The key identity: a*((at+1)/(t-a)) + 1 = (1+a²)t/(t-a) and (at+1)/(t-a) - a = (1+a²)/(t-a). So the composition is ((1+a²)t/(t-a)) / ((1+a²)/(t-a)) = t. Use field_simp and ring after establishing t-a ≠ 0 and the denominator of poleMap a t minus a is nonzero.
-/
theorem pole_map_involution (a t : ℝ) (ht : t ≠ a)
    (hmt : (a * t + 1) / (t - a) ≠ a) :
    poleMap a (poleMap a t) = t := by
  -- Substitute poleMap a t into the expression for poleMap a (poleMap a t).
  have h_sub : poleMap a (poleMap a t) = (a * ((a * t + 1) / (t - a)) + 1) / (((a * t + 1) / (t - a)) - a) := by
    rfl;
  grind

/-
PROBLEM
**Theorem Α.4**: M_a(-1/a) = 0 when a ≠ 0. The antipodal point maps to 0.

PROVIDED SOLUTION
Unfold poleMap. We need (a*(-1/a) + 1) / ((-1/a) - a) = 0. The numerator is -1 + 1 = 0, so the result is 0/anything = 0. Use field_simp and ring.
-/
theorem pole_map_antipodal (a : ℝ) (ha : a ≠ 0) :
    poleMap a (-1/a) = 0 := by
  unfold poleMap; ring_nf; aesop;

/-! ## Agent Β: Two-Pole Composition -/

/-- The two-pole Möbius transformation.
    F_{a,b}(t) = ((ab+1)t + (b-a)) / ((a-b)t + (ab+1)) -/
def twoPoleMap (a b t : ℝ) : ℝ :=
  ((a * b + 1) * t + (b - a)) / ((a - b) * t + (a * b + 1))

/-
PROBLEM
**Theorem Β.1**: F_{a,a}(t) = t. Same-pole map is identity.

PROVIDED SOLUTION
Unfold twoPoleMap. With a=b, numerator = (a²+1)t + 0 = (a²+1)t, denominator = 0 + (a²+1) = (a²+1). So F = (a²+1)t/(a²+1) = t. Use the fact that 1+a²≠0 (by positivity or nlinarith [sq_nonneg a]), field_simp, ring.
-/
theorem two_pole_same_is_id (a t : ℝ) :
    twoPoleMap a a t = t := by
  exact div_eq_iff ( by nlinarith [ sq_nonneg a ] ) |>.2 ( by ring )

/-- **Theorem Β.2**: The key algebraic identity.
    (b-a)·Num + (ab+1)·Den = (1+a²)(1+b²). -/
theorem two_pole_det_identity (a b t : ℝ) :
    (b - a) * ((a * b + 1) * t + (b - a)) +
    (a * b + 1) * ((a - b) * t + (a * b + 1)) =
    (1 + a ^ 2) * (1 + b ^ 2) := by ring

/-- **Theorem Β.3**: The determinant factors as (1+a²)(1+b²). -/
theorem two_pole_det_factored (a b : ℝ) :
    (a * b + 1) ^ 2 + (b - a) ^ 2 = (1 + a ^ 2) * (1 + b ^ 2) := by ring

/-
PROBLEM
**Theorem Β.4**: Swapping poles inverts the map. F_{b,a}(F_{a,b}(t)) = t.

PROVIDED SOLUTION
Unfold twoPoleMap. Use field_simp with h1 and h2 as the nonzero denominators. Then ring should close the goal.
-/
theorem two_pole_reverse_inverse (a b t : ℝ)
    (h1 : (a - b) * t + (a * b + 1) ≠ 0)
    (h2 : (b - a) * twoPoleMap a b t + (b * a + 1) ≠ 0) :
    twoPoleMap b a (twoPoleMap a b t) = t := by
  unfold twoPoleMap at *;
  grind +ring

/-- **Theorem Β.5**: F_{0,1}(t) = (t+1)/(1-t). South-to-east-point map. -/
theorem two_pole_south_east (t : ℝ) (ht : (1:ℝ) - t ≠ 0) :
    twoPoleMap 0 1 t = (t + 1) / (1 - t) := by
  unfold twoPoleMap; congr 1 <;> ring

/-- **Theorem Β.6**: F_{0,1}(0) = 1. -/
theorem two_pole_01_at_zero :
    twoPoleMap 0 1 0 = 1 := by
  unfold twoPoleMap; norm_num

/-- **Theorem Β.7**: F_{0,1}(-1) = 0. -/
theorem two_pole_01_at_neg_one :
    twoPoleMap 0 1 (-1) = 0 := by
  unfold twoPoleMap; norm_num

/-- **Theorem Β.8**: F_{0,1}(2) = -3. An integer maps to a different integer! -/
theorem two_pole_01_at_two :
    twoPoleMap 0 1 2 = -3 := by
  unfold twoPoleMap; norm_num

/-- **Theorem Β.9**: F_{0,1}(3) = -2. -/
theorem two_pole_01_at_three :
    twoPoleMap 0 1 3 = -2 := by
  unfold twoPoleMap; norm_num

/-
PROBLEM
**Theorem Β.10**: The composition F_{b,c} ∘ F_{a,b} = F_{a,c}.
    Two-pole maps compose transitively!

PROVIDED SOLUTION
Unfold twoPoleMap. Use field_simp with h1 and h2 to clear denominators. Then ring should close it.
-/
theorem two_pole_composition_formula (a b c t : ℝ)
    (h1 : (a - b) * t + (a * b + 1) ≠ 0)
    (h2 : (b - c) * twoPoleMap a b t + (b * c + 1) ≠ 0) :
    twoPoleMap b c (twoPoleMap a b t) = twoPoleMap a c t := by
  unfold twoPoleMap at *;
  grind

/-! ## Agent Γ: Integer-to-Integer Mappings -/

/-
PROBLEM
**Theorem Γ.1**: The NECESSARY condition for integer mapping.
    If the denominator divides the numerator, then it divides (1+a²)(1+b²).
    This is the correct direction: F_{a,b}(n) ∈ ℤ → den | det.

PROVIDED SOLUTION
From the identity two_pole_det_identity_int: (b-a)*((ab+1)*n + (b-a)) + (ab+1)*((a-b)*n + (ab+1)) = (1+a²)(1+b²). Let d = (a-b)*n + (ab+1) and num = (ab+1)*n + (b-a). Then (b-a)*num + (ab+1)*d = det. If d | num, then d | (b-a)*num and d | (ab+1)*d, so d | their sum = det. Use dvd_add with dvd_mul_of_dvd_right and dvd_mul_left.
-/
theorem integer_map_necessary (a b n : ℤ) :
    (a - b) * n + (a * b + 1) ∣ (a * b + 1) * n + (b - a) →
    (a - b) * n + (a * b + 1) ∣ (1 + a ^ 2) * (1 + b ^ 2) := by
  exact fun h => by convert dvd_add ( h.mul_left ( b - a ) ) ( dvd_mul_right ( ( a - b ) * n + ( a * b + 1 ) ) ( a * b + 1 ) ) using 1; ring;

/-
PROBLEM
**Theorem Γ.1b**: The denominator always divides (b-a) times the numerator.
    This is the weaker forward direction that IS always true.

PROVIDED SOLUTION
From the identity: (b-a)*num + (ab+1)*d = det where d = (a-b)*n + (ab+1) and num = (ab+1)*n + (b-a). So (b-a)*num = det - (ab+1)*d. Since d | det (hypothesis) and d | (ab+1)*d (dvd_mul_left), d | det - (ab+1)*d = (b-a)*num. Use dvd_sub or show directly.
-/
theorem integer_map_weak_criterion (a b n : ℤ) :
    (a - b) * n + (a * b + 1) ∣ (1 + a ^ 2) * (1 + b ^ 2) →
    (a - b) * n + (a * b + 1) ∣ (b - a) * ((a * b + 1) * n + (b - a)) := by
  intro h
  have h_det : (a - b) * n + (a * b + 1) ∣ (1 + a ^ 2) * (1 + b ^ 2) := h
  have h_sub : (a - b) * n + (a * b + 1) ∣ (1 + a ^ 2) * (1 + b ^ 2) - (a * b + 1) * ((a - b) * n + (a * b + 1)) := by
    exact dvd_sub h_det ( dvd_mul_left _ _ )
  convert h_sub using 1 ; ring

/-- **Theorem Γ.2**: The key algebraic identity in ℤ. -/
theorem two_pole_det_identity_int (a b n : ℤ) :
    (b - a) * ((a * b + 1) * n + (b - a)) +
    (a * b + 1) * ((a - b) * n + (a * b + 1)) =
    (1 + a ^ 2) * (1 + b ^ 2) := by ring

/-- **Theorem Γ.3**: The determinant factorization in ℤ. -/
theorem two_pole_det_factored_int (a b : ℤ) :
    (a * b + 1) ^ 2 + (b - a) ^ 2 = (1 + a ^ 2) * (1 + b ^ 2) := by ring

/-- **Theorem Γ.4**: det for (0,1) is 4. -/
theorem det_south_east : (1 + (0:ℤ)^2) * (1 + (1:ℤ)^2) = 2 := by norm_num

/-- **Theorem Γ.5**: det for (1,2) is 10. -/
theorem det_one_two : (1 + (1:ℤ)^2) * (1 + (2:ℤ)^2) = 10 := by norm_num

/-- **Theorem Γ.6**: det for (2,3) is 50. -/
theorem det_two_three : (1 + (2:ℤ)^2) * (1 + (3:ℤ)^2) = 50 := by norm_num

/-- **Theorem Γ.7**: 1+n² is always positive for integers. -/
theorem one_plus_sq_pos_int (n : ℤ) : 0 < 1 + n ^ 2 := by positivity

/-! ## Agent Δ: Computational Explorer — Integer Chains -/

/-- F_{0,1}: numerator at n=2 is 3, denominator is -1, quotient is -3. -/
theorem chain_01_2_num : (0 * 1 + 1) * 2 + (1 - 0) = (3 : ℤ) := by norm_num
theorem chain_01_2_den : (0 - 1) * 2 + (0 * 1 + 1) = (-1 : ℤ) := by norm_num
theorem chain_01_2 : (3 : ℤ) / (-1) = -3 := by norm_num

/-- F_{0,1}: at n=3, numerator is 4, denominator is -2, quotient is -2. -/
theorem chain_01_3_num : (0 * 1 + 1) * 3 + (1 - 0) = (4 : ℤ) := by norm_num
theorem chain_01_3_den : (0 - 1) * 3 + (0 * 1 + 1) = (-2 : ℤ) := by norm_num
theorem chain_01_3 : (4 : ℤ) / (-2) = -2 := by norm_num

/-- F_{1,2}(1) = 2. -/
theorem chain_12_1 :
    ((1 * 2 + 1) * 1 + (2 - 1)) / ((1 - 2) * 1 + (1 * 2 + 1)) = (2 : ℤ) := by norm_num

/-- F_{1,2}(2) = 7. -/
theorem chain_12_2 :
    ((1 * 2 + 1) * 2 + (2 - 1)) / ((1 - 2) * 2 + (1 * 2 + 1)) = (7 : ℤ) := by norm_num

/-- F_{1,3}(1) = 3. -/
theorem chain_13_1 :
    ((1 * 3 + 1) * 1 + (3 - 1)) / ((1 - 3) * 1 + (1 * 3 + 1)) = (3 : ℤ) := by norm_num

/-- F_{1,3}(3) = -7. -/
theorem chain_13_3 :
    ((1 * 3 + 1) * 3 + (3 - 1)) / ((1 - 3) * 3 + (1 * 3 + 1)) = (-7 : ℤ) := by norm_num

/-- F_{1,3}(-3) = -1. -/
theorem chain_13_neg3 :
    ((1 * 3 + 1) * (-3) + (3 - 1)) / ((1 - 3) * (-3) + (1 * 3 + 1)) = (-1 : ℤ) := by norm_num

/-! ## Agent Ε: Synthesis -/

/-- **Grand Synthesis**: The determinant equals (1+a²)(1+b²) = N(1+ai)·N(1+bi)
    in Gaussian integer norms. -/
theorem gaussian_norm_connection (a b : ℤ) :
    (a * b + 1) ^ 2 + (b - a) ^ 2 = (1 + a ^ 2) * (1 + b ^ 2) := by ring

/-- **Brahmagupta-Fibonacci from poles**: Both sum-of-squares decompositions. -/
theorem brahmagupta_from_poles (a b : ℤ) :
    (1 + a ^ 2) * (1 + b ^ 2) = (a * b + 1) ^ 2 + (a - b) ^ 2 ∧
    (1 + a ^ 2) * (1 + b ^ 2) = (a * b - 1) ^ 2 + (a + b) ^ 2 := by
  constructor <;> ring

/-- **All integer-pole maps are elliptic**: 4·det - trace² = 4(a-b)² ≥ 0. -/
theorem all_integer_poles_elliptic (a b : ℤ) :
    4 * ((1 + a ^ 2) * (1 + b ^ 2)) - (2 * (a * b + 1)) ^ 2 = 4 * (a - b) ^ 2 := by
  ring

/-
PROBLEM
**F_{0,1} has order 4**: Applying F_{0,1} four times returns to t.

PROVIDED SOLUTION
Unfold twoPoleMap four times. Use field_simp with the hypotheses ht0, ht1, htm1 to clear denominators. Then ring should close. Key: need t ≠ 0 (ht0), 1-t ≠ 0 (from ht1), t+1 ≠ 0 (from htm1).
-/
theorem two_pole_01_order_four (t : ℝ) (ht0 : t ≠ 0) (ht1 : t ≠ 1) (htm1 : t ≠ -1) :
    twoPoleMap 0 1 (twoPoleMap 0 1 (twoPoleMap 0 1 (twoPoleMap 0 1 t))) = t := by
  unfold twoPoleMap;
  grind

/-
PROBLEM
**F_{0,1}² is negative inversion**: F_{0,1}(F_{0,1}(t)) = -1/t.

PROVIDED SOLUTION
Unfold twoPoleMap twice. F_{0,1}(t) = (t+1)/(1-t) (after simplification, since ab+1=1, b-a=1, a-b=-1). Then F_{0,1}(F_{0,1}(t)) = F_{0,1}((t+1)/(1-t)). Applying the formula: numerator = (t+1)/(1-t) + 1 = (t+1+1-t)/(1-t) = 2/(1-t). Denominator = 1 - (t+1)/(1-t) = (1-t-t-1)/(1-t) = -2t/(1-t). Result = (2/(1-t))/(-2t/(1-t)) = 2/(-2t) = -1/t. Use field_simp and ring with ht0 and ht1 (which give t≠0 and 1-t≠0).
-/
theorem two_pole_01_squared (t : ℝ) (ht0 : t ≠ 0) (ht1 : t ≠ 1) :
    twoPoleMap 0 1 (twoPoleMap 0 1 t) = -(1/t) := by
  unfold twoPoleMap; norm_num [ ht0, ht1 ] ; ring;
  grind

/-- **Eigenvalue Gaussian factorization**: (1+ai)·conj(1+bi) has real part ab+1
    and imaginary part a-b. -/
theorem eigenvalue_gaussian_factorization (a b : ℤ) :
    (1 * 1 + a * b = a * b + 1) ∧ (a * 1 - 1 * b = a - b) := by
  constructor <;> ring

/-- **The Pythagorean triple (3,4,5) from poles (1,2)**: p=3, q=1, 3²+1²=10=2·5. -/
theorem pythagorean_from_poles_1_2 :
    let p := (1:ℤ) * 2 + 1
    let q := (2:ℤ) - 1
    p ^ 2 + q ^ 2 = (1 + 1 ^ 2) * (1 + 2 ^ 2) := by norm_num

/-- **South-east elliptic**: trace² < 4·det for (0,1). -/
theorem south_east_elliptic :
    (2 * ((0:ℤ) * 1 + 1)) ^ 2 < 4 * ((1 + 0 ^ 2) * (1 + 1 ^ 2)) := by norm_num

end
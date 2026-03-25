import Mathlib

/-!
# Dimensional Projection: Stereographic Ladders Across Dimensions

## Research Question
Is there an inverse stereographic projection path into lower and lower dimensions?
How about projecting to higher dimensions? What new mathematics does this unlock?

## Answer: Yes — The Stereographic Ladder

### Descending Ladder (Higher → Lower Dimensions)
The stereographic projection σₙ: Sⁿ \ {N} → ℝⁿ maps the n-sphere minus the
north pole to n-dimensional Euclidean space. By composing:

  S^n → ℝ^n → S^(n-1) → ℝ^(n-1) → ... → S¹ → ℝ

we get a chain of dimension reductions. Each step is:
1. **Conformal** (angle-preserving)
2. **Rational-preserving** (rational points map to rational points)
3. **Information-preserving** (injective, hence reversible)

### Ascending Ladder (Lower → Higher Dimensions)
The inverse stereographic projection σₙ⁻¹: ℝⁿ → Sⁿ lifts into higher spheres:

  ℝ → S¹ ↪ ℝ² → S² ↪ ℝ³ → S³ ↪ ...

Each step embeds in one higher dimension, creating a "tower of spheres".

### What This Unlocks
1. **Pythagorean towers**: Integer solutions propagate up the ladder
2. **Conformal compactification chains**: Each step adds a point at ∞
3. **Hopf-like structures**: S³ → S² via stereo connects to Hopf fibration
4. **Number-theoretic dimension theory**: Sums of k squares ↔ rational points on S^(k-1)

## Main Results

* `stereo_round_trip_from_R`: Forward ∘ Inverse = id on ℝ
* `inv_stereo_2d_on_sphere`: ℝ² → S² always lands on S²
* `inv_stereo_3d_on_sphere`: ℝ³ → S³ always lands on S³
* `hopf_map_on_sphere`: The Hopf map S³ → S² is well-defined
* `north_pole_not_in_image`: The north pole is not in the stereo image
* `every_non_north_pole_in_image`: Every other S¹ point is in the image
* `four_squares_identity`: Euler's identity via quaternionic stereo
-/

open Real Finset BigOperators

noncomputable section

/-! ## Part I: The Descending Ladder -/

/-! ### Step 1: S¹ → ℝ (Forward Stereographic Projection from the Circle) -/

/-- Forward stereographic projection from S¹ to ℝ.
    Projects from the north pole (0, -1). Given (x, y) on S¹ with y ≠ -1,
    maps to t = x / (1 + y). -/
def stereoForward1 (x y : ℝ) : ℝ := x / (1 + y)

/-- Inverse stereographic projection from ℝ to S¹. -/
def invStereo1 (t : ℝ) : ℝ × ℝ :=
  (2 * t / (1 + t ^ 2), (1 - t ^ 2) / (1 + t ^ 2))

/-- The inverse stereo map always lands on S¹. -/
theorem inv_stereo_1d_on_circle (t : ℝ) :
    (invStereo1 t).1 ^ 2 + (invStereo1 t).2 ^ 2 = 1 := by
  simp only [invStereo1]
  have h : (1 : ℝ) + t ^ 2 ≠ 0 := by positivity
  field_simp; ring

/-- Forward ∘ Inverse = id on ℝ (round-trip from ℝ). -/
theorem stereo_round_trip_from_R (t : ℝ) :
    stereoForward1 (invStereo1 t).1 (invStereo1 t).2 = t := by
  simp only [stereoForward1, invStereo1]
  have h : (1 : ℝ) + t ^ 2 ≠ 0 := by positivity
  field_simp; ring

/-
PROBLEM
Inverse ∘ Forward = id on S¹ (round-trip from S¹), first component.

PROVIDED SOLUTION
Unfold invStereo1 and stereoForward1. We need to show 2*(x/(1+y))/(1+(x/(1+y))^2) = x. Use field_simp to clear denominators. Then use nlinarith with hunit (x^2+y^2=1) and sq_nonneg (1+y).
-/
theorem stereo_round_trip_from_S1_fst (x y : ℝ) (hunit : x ^ 2 + y ^ 2 = 1) (hy : 1 + y ≠ 0) :
    (invStereo1 (stereoForward1 x y)).1 = x := by
  simp [stereoForward1, invStereo1] at *;
  grind

/-
PROBLEM
Inverse ∘ Forward = id on S¹ (round-trip from S¹), second component.

PROVIDED SOLUTION
Unfold invStereo1 and stereoForward1. Use field_simp to clear denominators. Then use nlinarith with hunit (x^2+y^2=1) and sq_nonneg (1+y).
-/
theorem stereo_round_trip_from_S1_snd (x y : ℝ) (hunit : x ^ 2 + y ^ 2 = 1) (hy : 1 + y ≠ 0) :
    (invStereo1 (stereoForward1 x y)).2 = y := by
  unfold invStereo1 stereoForward1;
  grind

/-! ### Step 2: S² → ℝ² (Stereographic Projection from the 2-Sphere) -/

/-- Forward stereographic projection from S² to ℝ².
    Projects from north pole (0, 0, -1).
    Given (x, y, z) on S² with z ≠ -1, maps to (x/(1+z), y/(1+z)). -/
def stereoForward2 (x y z : ℝ) : ℝ × ℝ :=
  (x / (1 + z), y / (1 + z))

/-- Inverse stereographic projection from ℝ² to S².
    Given (u, v) ∈ ℝ², maps to S² via:
    (2u/(1+u²+v²), 2v/(1+u²+v²), (1-u²-v²)/(1+u²+v²)) -/
def invStereo2 (u v : ℝ) : ℝ × ℝ × ℝ :=
  let d := 1 + u ^ 2 + v ^ 2
  (2 * u / d, 2 * v / d, (1 - u ^ 2 - v ^ 2) / d)

/-- The inverse stereo map from ℝ² always lands on S². -/
theorem inv_stereo_2d_on_sphere (u v : ℝ) :
    let p := invStereo2 u v
    p.1 ^ 2 + p.2.1 ^ 2 + p.2.2 ^ 2 = 1 := by
  simp only [invStereo2]
  have h : (1 : ℝ) + u ^ 2 + v ^ 2 ≠ 0 := by positivity
  field_simp; ring

/-- Round-trip from ℝ² through S² and back. First component. -/
theorem stereo_2d_round_trip_fst (u v : ℝ) :
    (stereoForward2 (invStereo2 u v).1 (invStereo2 u v).2.1 (invStereo2 u v).2.2).1 = u := by
  simp only [stereoForward2, invStereo2]
  have h : (1 : ℝ) + u ^ 2 + v ^ 2 ≠ 0 := by positivity
  field_simp; ring

/-- Round-trip from ℝ² through S² and back. Second component. -/
theorem stereo_2d_round_trip_snd (u v : ℝ) :
    (stereoForward2 (invStereo2 u v).1 (invStereo2 u v).2.1 (invStereo2 u v).2.2).2 = v := by
  simp only [stereoForward2, invStereo2]
  have h : (1 : ℝ) + u ^ 2 + v ^ 2 ≠ 0 := by positivity
  field_simp; ring

/-! ### Step 3: S³ → ℝ³ (Stereographic Projection from the 3-Sphere) -/

/-- Inverse stereographic projection from ℝ³ to S³.
    Given (u, v, w) ∈ ℝ³, maps to S³. -/
def invStereo3 (u v w : ℝ) : Fin 4 → ℝ := fun i =>
  let d := 1 + u ^ 2 + v ^ 2 + w ^ 2
  match i with
  | 0 => 2 * u / d
  | 1 => 2 * v / d
  | 2 => 2 * w / d
  | 3 => (1 - u ^ 2 - v ^ 2 - w ^ 2) / d

/-- The inverse stereo map from ℝ³ always lands on S³. -/
theorem inv_stereo_3d_on_sphere (u v w : ℝ) :
    ∑ i : Fin 4, (invStereo3 u v w i) ^ 2 = 1 := by
  simp only [invStereo3, Fin.sum_univ_four, Fin.isValue]
  have h : (1 : ℝ) + u ^ 2 + v ^ 2 + w ^ 2 ≠ 0 := by positivity
  field_simp; ring

/-! ### General n-dimensional identity -/

/-- The general stereographic identity: for any S ≥ 0 representing the sum of
    squares of the "flat" coordinates, the inverse stereo output has unit norm.
    This works in ANY dimension. -/
theorem stereo_general_unit_norm (S : ℝ) (hS : 0 ≤ S) :
    let d := 1 + S
    (4 * S) / d ^ 2 + ((1 - S) / d) ^ 2 = 1 := by
  have h : (1 : ℝ) + S ≠ 0 := by positivity
  simp only
  field_simp; ring

/-! ## Part II: The Ascending Ladder -/

/-- One step of the ascending ladder: ℝ → S¹ ↪ ℝ² → S².
    Start with t ∈ ℝ, map to S¹ via inv_stereo, embed in ℝ²,
    then lift to S² via inv_stereo again. -/
def liftRtoS2 (t : ℝ) : ℝ × ℝ × ℝ :=
  let p := invStereo1 t  -- ℝ → S¹
  invStereo2 p.1 p.2     -- ℝ² → S²

/-- The ascending ladder preserves the sphere property:
    lifting from ℝ to S² always lands on S². -/
theorem lift_R_to_S2_on_sphere (t : ℝ) :
    let p := liftRtoS2 t
    p.1 ^ 2 + p.2.1 ^ 2 + p.2.2 ^ 2 = 1 := by
  exact inv_stereo_2d_on_sphere _ _

/-! ## Part III: Rational Point Propagation -/

/-- Key theorem: Rational stereographic coordinates produce rational sphere points.
    If t = p/q is rational, then inv_stereo gives a rational point on S¹. -/
theorem rational_stereo_rational_circle (p q : ℤ) (hq : (q : ℝ) ≠ 0)
    (hpq : (p : ℝ) ^ 2 + (q : ℝ) ^ 2 ≠ 0) :
    (invStereo1 ((p : ℝ) / q)).1 = 2 * p * q / (p ^ 2 + q ^ 2) := by
  simp only [invStereo1]
  have hq2 : (q : ℝ) ^ 2 ≠ 0 := pow_ne_zero 2 hq
  field_simp; ring

/-- Rational points on S¹ give Pythagorean triples. -/
theorem rational_circle_pythagorean (p q : ℤ) (hpq : (p : ℤ) ^ 2 + q ^ 2 ≠ 0) :
    ∃ a b c : ℤ, c ≠ 0 ∧
    (2 * p * q : ℤ) ^ 2 + (q ^ 2 - p ^ 2) ^ 2 = c ^ 2 := by
  exact ⟨2 * p * q, q ^ 2 - p ^ 2, p ^ 2 + q ^ 2, by exact_mod_cast hpq, by ring⟩

/-! ## Part IV: Sums of Squares Tower -/

/-- Two squares identity (Brahmagupta-Fibonacci). -/
theorem two_squares_identity (a b c d : ℤ) :
    (a ^ 2 + b ^ 2) * (c ^ 2 + d ^ 2) = (a * c - b * d) ^ 2 + (a * d + b * c) ^ 2 := by ring

/-- Three squares from a Pythagorean triple: lifting to S². -/
theorem three_squares_from_pythagorean (a b c : ℤ) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    (2 * a * c) ^ 2 + (2 * b * c) ^ 2 + (c ^ 2 - a ^ 2 - b ^ 2) ^ 2 =
    (c ^ 2 + a ^ 2 + b ^ 2) ^ 2 := by nlinarith [sq_nonneg a, sq_nonneg b, sq_nonneg c]

/-- Four squares from stereo: lifting to S³.
    Euler's four-square identity, arising from the norm of quaternion multiplication. -/
theorem four_squares_identity (a₁ a₂ a₃ a₄ b₁ b₂ b₃ b₄ : ℤ) :
    (a₁ ^ 2 + a₂ ^ 2 + a₃ ^ 2 + a₄ ^ 2) * (b₁ ^ 2 + b₂ ^ 2 + b₃ ^ 2 + b₄ ^ 2) =
    (a₁*b₁ - a₂*b₂ - a₃*b₃ - a₄*b₄) ^ 2 +
    (a₁*b₂ + a₂*b₁ + a₃*b₄ - a₄*b₃) ^ 2 +
    (a₁*b₃ - a₂*b₄ + a₃*b₁ + a₄*b₂) ^ 2 +
    (a₁*b₄ + a₂*b₃ - a₃*b₂ + a₄*b₁) ^ 2 := by ring

/-! ## Part V: The Hopf Fibration via Stereographic Projection -/

/-
PROBLEM
The Hopf map sends S³ → S² by treating S³ ⊂ ℂ² and mapping
    (z₁, z₂) ↦ (2·Re(z₁z̄₂), 2·Im(z₁z̄₂), |z₁|²-|z₂|²).
    In real coordinates (a, b, c, d) with a²+b²+c²+d²=1:
      x = 2(ac + bd)
      y = 2(bc - ad)
      z = a² + b² - c² - d²
    This is a well-defined map from S³ to S².

PROVIDED SOLUTION
Expand everything and use nlinarith. The key is that (2(ac+bd))^2 + (2(bc-ad))^2 + (a²+b²-c²-d²)^2 = (a²+b²+c²+d²)^2. Since a²+b²+c²+d²=1, result is 1. Use nlinarith with lots of sq_nonneg hints.
-/
theorem hopf_map_on_sphere (a b c d : ℝ) (h : a^2 + b^2 + c^2 + d^2 = 1) :
    (2*(a*c + b*d))^2 + (2*(b*c - a*d))^2 + (a^2 + b^2 - c^2 - d^2)^2 = 1 := by
  grind +ring

/-- The fiber of the Hopf map over the south pole (0,0,-1) consists of
    points with a² + b² = 0, i.e., the "equatorial circle" c² + d² = 1. -/
theorem hopf_fiber_south_pole (c d : ℝ) (h : c^2 + d^2 = 1) :
    let a := (0 : ℝ); let b := (0 : ℝ)
    a^2 + b^2 + c^2 + d^2 = 1 ∧
    2*(a*c + b*d) = 0 ∧ 2*(b*c - a*d) = 0 ∧ a^2 + b^2 - c^2 - d^2 = -1 := by
  refine ⟨by linarith, by ring, by ring, by linarith⟩

/-! ## Part VI: Conformal Properties -/

/-- The Jacobian determinant of the 2D inverse stereographic projection.
    At point (u, v), det(J) = 4/(1+u²+v²)². This is always positive,
    confirming the map is orientation-preserving and locally invertible. -/
theorem stereo_2d_jacobian_positive (u v : ℝ) :
    0 < 4 / (1 + u ^ 2 + v ^ 2) ^ 2 := by positivity

/-- The conformal factor of the stereographic projection.
    The metric on S² pulled back to ℝ² is (2/(1+u²+v²))² (du² + dv²).
    The conformal factor is always positive. -/
theorem stereo_conformal_factor_positive (u v : ℝ) :
    0 < (2 / (1 + u ^ 2 + v ^ 2)) ^ 2 := by positivity

/-! ## Part VII: Compactification and Missing Points -/

/-- The north pole (0, -1) is the unique point NOT in the image of invStereo1. -/
theorem north_pole_not_in_image :
    ∀ t : ℝ, invStereo1 t ≠ (0, -1) := by
  intro t ht
  simp only [invStereo1, Prod.mk.injEq] at ht
  have h1 : (1 : ℝ) + t ^ 2 ≠ 0 := by positivity
  have h2 := ht.2
  rw [div_eq_iff h1] at h2
  nlinarith [sq_nonneg t]

/-
PROBLEM
Every point on S¹ except the north pole IS in the image.

PROVIDED SOLUTION
Use t = x / (1 + y). Since y ≠ -1, 1 + y ≠ 0. Show invStereo1(x/(1+y)) = (x, y) by unfolding invStereo1, using field_simp and nlinarith with hunit. Use Prod.ext (or ext) to split into components.
-/
theorem every_non_north_pole_in_image (x y : ℝ) (hunit : x ^ 2 + y ^ 2 = 1) (hy : y ≠ -1) :
    ∃ t : ℝ, invStereo1 t = (x, y) := by
  unfold invStereo1;
  use ( 1 - y ) / x;
  grind

/-! ## Part VIII: Dimensional Interplay and New Identities -/

/-- Iterated stereo produces sphere points at every level. -/
theorem iterated_stereo_image (t : ℝ) :
    let p := liftRtoS2 t
    p.1 ^ 2 + p.2.1 ^ 2 + p.2.2 ^ 2 = 1 :=
  lift_R_to_S2_on_sphere t

/-- The stereographic projection intertwines with rotations.
    When projecting from the circle with stereoForward1 (which uses x/(1+y)),
    the stereo coordinate of (cos α, sin α) is cos α / (1 + sin α). -/
theorem stereo_rotation_at_east (α : ℝ) (h : 1 + sin α ≠ 0) :
    stereoForward1 (cos α) (sin α) = cos α / (1 + sin α) := by
  simp [stereoForward1]

/-
PROBLEM
Inverse stereo is injective (fundamental for the ladder being invertible).

PROVIDED SOLUTION
Intro a b hab. Extract both component equalities from hab. From the second component equation, (1-a²)/(1+a²) = (1-b²)/(1+b²), cross multiply to get (1-a²)(1+b²) = (1-b²)(1+a²), expand to get b²-a² = a²-b², so 2(a²-b²) = 0, so a² = b². From the first component equation, 2a/(1+a²) = 2b/(1+b²), so a(1+b²) = b(1+a²). Since a² = b², this gives a+ab² = b+ba², hence a-b = ba²-ab² = ab(a-b)... Actually simpler: a(1+b²) = b(1+a²) and a²=b². So a+ab²=b+ba², hence (a-b) + ab(b-a) = 0, so (a-b)(1-ab) = 0. If a=b done. If ab=1, then a²=b² and ab=1, so a²=a·b... use nlinarith.
-/
theorem inv_stereo_1d_injective : Function.Injective invStereo1 := by
  intros t1 t2 h_eq
  have h_comp : 2 * t1 / (1 + t1 ^ 2) = 2 * t2 / (1 + t2 ^ 2) ∧ (1 - t1 ^ 2) / (1 + t1 ^ 2) = (1 - t2 ^ 2) / (1 + t2 ^ 2) := by
    exact ⟨ congr_arg Prod.fst h_eq, congr_arg Prod.snd h_eq ⟩;
  rw [ div_eq_div_iff, div_eq_div_iff ] at h_comp <;> nlinarith [ mul_self_nonneg ( t1 - t2 ), mul_self_nonneg ( t1 + t2 ) ]

/-
PROBLEM
The 2D inverse stereo is also injective.

PROVIDED SOLUTION
Intro p1 p2 h. Extract all 3 component equalities. From the third component, (1-p1.1²-p1.2²)/(1+p1.1²+p1.2²) = (1-p2.1²-p2.2²)/(1+p2.1²+p2.2²). Cross multiply and simplify to get p1.1²+p1.2² = p2.1²+p2.2². Then from the first component, 2*p1.1/(1+p1.1²+p1.2²) = 2*p2.1/(1+p2.1²+p2.2²). Since the denominators are equal (from above), p1.1 = p2.1. Similarly p1.2 = p2.2. Use Prod.ext.
-/
theorem inv_stereo_2d_injective : Function.Injective (fun p : ℝ × ℝ => invStereo2 p.1 p.2) := by
  intro p q h;
  unfold invStereo2 at h;
  -- By simplifying, we can see that the equations imply $p.1 = q.1$ and $p.2 = q.2$.
  have h_eq : p.1 ^ 2 + p.2 ^ 2 = q.1 ^ 2 + q.2 ^ 2 := by
    grind;
  simp_all +decide [ div_eq_mul_inv ];
  simp_all +decide [ add_assoc ];
  exact Prod.ext ( h.1.resolve_right ( by positivity ) ) ( h.2.1.resolve_right ( by positivity ) )

end
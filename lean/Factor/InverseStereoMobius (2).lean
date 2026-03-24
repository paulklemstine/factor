/-
# Inverse Stereographic Möbius Research
## Machine-Verified Integer-to-Integer Mappings via Generalized Poles

Core definitions and foundational theorems for two-pole stereographic projection.
-/
import Mathlib

open scoped Classical

/-! ## Core Definitions -/

/-- The change-of-pole map M_a(t) = (at + 1)/(t - a).
    This maps the stereographic coordinate from the standard south pole
    to the coordinate from the pole at invStereo(a). -/
noncomputable def polemap (a : ℚ) (t : ℚ) : ℚ := (a * t + 1) / (t - a)

/-- The two-pole Möbius transformation F_{a,b}(t) = ((ab+1)t + (b-a)) / ((a-b)t + (ab+1)).
    This is the composition of inverse stereographic from pole a with forward
    stereographic from pole b. -/
noncomputable def twoPole (a b : ℚ) (t : ℚ) : ℚ :=
  ((a * b + 1) * t + (b - a)) / ((a - b) * t + (a * b + 1))

/-- The determinant of the two-pole Möbius matrix. -/
def twoPole_det (a b : ℚ) : ℚ := (1 + a ^ 2) * (1 + b ^ 2)

/-- The trace of the two-pole Möbius matrix. -/
def twoPole_trace (a b : ℚ) : ℚ := 2 * (a * b + 1)

/-- The discriminant 4·det - trace² which controls the type of Möbius transformation. -/
def twoPole_disc (a b : ℚ) : ℚ := 4 * twoPole_det a b - (twoPole_trace a b) ^ 2

/-! ## Agent Alpha: Generalized Pole Theory -/

/-
PROBLEM
The north pole case: M_0(t) = 1/t.

PROVIDED SOLUTION
Unfold polemap. Simplify: (0*t+1)/(t-0) = 1/t.
-/
theorem polemap_zero (t : ℚ) (ht : t ≠ 0) : polemap 0 t = 1 / t := by
  -- By definition of polemap, we have polemap 0 t = (0 * t + 1) / (t - 0).
  simp [polemap]

/-
PROBLEM
The polemap is an involution: M_a(M_a(t)) = t when t ≠ a and M_a(t) ≠ a.

PROVIDED SOLUTION
Unfold polemap. M_a(M_a(t)) = (a * ((at+1)/(t-a)) + 1) / (((at+1)/(t-a)) - a). Simplify numerator: a(at+1)/(t-a) + 1 = (a²t+a+t-a)/(t-a) = (a²t+t)/(t-a) = t(a²+1)/(t-a). Simplify denominator: (at+1)/(t-a) - a = (at+1-a(t-a))/(t-a) = (at+1-at+a²)/(t-a) = (1+a²)/(t-a). So the result is t(a²+1)/(1+a²) = t. Use field_simp and ring.
-/
theorem polemap_involution (a t : ℚ) (ht : t ≠ a) (hM : polemap a t ≠ a) :
    polemap a (polemap a t) = t := by
      unfold polemap at *;
      grind

/-
PROBLEM
The determinant of the polemap is -(1 + a²), which is always negative (nonzero).

PROVIDED SOLUTION
a^2 >= 0 so a^2 + 1 >= 1 > 0 hence nonzero.
-/
theorem polemap_det_nonzero (a : ℚ) : a ^ 2 + 1 ≠ 0 := by
  positivity

/-! ## Agent Beta: Two-Pole Composition -/

/-
PROBLEM
Same-pole composition is the identity.

PROVIDED SOLUTION
Unfold twoPole. When a=b, numerator = (a²+1)t + 0 and denominator = 0·t + (a²+1). So the result is t. Use field_simp and ring.
-/
theorem twoPole_identity (a t : ℚ) (ht : (a - a) * t + (a * a + 1) ≠ 0) :
    twoPole a a t = t := by
      unfold twoPole; rw [ div_eq_iff ht ] ; ring;

/-
PROBLEM
The determinant of the two-pole matrix equals (1+a²)(1+b²).

PROVIDED SOLUTION
Ring identity.
-/
theorem twoPole_det_eq (a b : ℚ) :
    (a * b + 1) ^ 2 + (b - a) ^ 2 = (1 + a ^ 2) * (1 + b ^ 2) := by
      ring

/-
PROBLEM
Swapping poles gives the inverse transformation.

PROVIDED SOLUTION
Unfold twoPole twice and simplify. The key is that the composition gives ((ba+1)((ab+1)t+(b-a)) + (a-b)((a-b)t+(ab+1))) / ((b-a)((ab+1)t+(b-a)) + (ba+1)((a-b)t+(ab+1))). The numerator simplifies to (1+a²)(1+b²)·t and the denominator to (1+a²)(1+b²). Use field_simp and ring.
-/
theorem twoPole_inverse (a b t : ℚ)
    (h1 : (a - b) * t + (a * b + 1) ≠ 0)
    (h2 : (b - a) * (twoPole a b t) + (b * a + 1) ≠ 0) :
    twoPole b a (twoPole a b t) = t := by
      unfold twoPole;
      rw [ div_eq_iff ];
      · grind +ring;
      · convert h2 using 1

/-
PROBLEM
The discriminant equals 4(a-b)², showing all integer-pole maps are elliptic.

PROVIDED SOLUTION
Unfold twoPole_disc, twoPole_det, twoPole_trace. Ring.
-/
theorem twoPole_disc_eq (a b : ℚ) : twoPole_disc a b = 4 * (a - b) ^ 2 := by
  unfold twoPole_disc twoPole_det twoPole_trace; ring;

/-! ## Agent Gamma: Integer-to-Integer Mappings -/

/-
PROBLEM
If F_{a,b}(n) is an integer, the denominator divides the determinant.

PROVIDED SOLUTION
Let d = (a-b)n + (ab+1). We know d | (ab+1)n + (b-a). Then d | (a-b)·((ab+1)n+(b-a)) - (ab+1)·((a-b)n+(ab+1)) since d divides both d·(ab+1) and (ab+1)·d. Actually compute: (a-b)·num - (ab+1)·den = (a-b)((ab+1)n+(b-a)) - (ab+1)((a-b)n+(ab+1)) = -(a-b)² - (ab+1)² = -(1+a²)(1+b²). So d | (1+a²)(1+b²). Use dvd_sub and ring.
-/
theorem twoPole_int_necessary (a b n : ℤ) (h : (a - b) * n + (a * b + 1) ≠ 0)
    (hint : ((a - b) * n + (a * b + 1)) ∣ ((a * b + 1) * n + (b - a))) :
    ((a - b) * n + (a * b + 1)) ∣ ((1 + a ^ 2) * (1 + b ^ 2)) := by
      obtain ⟨ k, hk ⟩ := ‹_›;
      exact ⟨ -k * ( a - b ) + ( a * b + 1 ), by linear_combination -hk * ( a - b ) ⟩

/-! ## Agent Delta: Computational Explorer -/

/-
PROBLEM
F_{0,1}(0) = 1.

PROVIDED SOLUTION
Unfold twoPole, compute: ((0*1+1)*0 + (1-0))/((0-1)*0 + (0*1+1)) = 1/1 = 1. Use norm_num and simp [twoPole].
-/
theorem twoPole_01_at_0 : twoPole 0 1 0 = 1 := by
  unfold twoPole; norm_num;

/-
PROBLEM
F_{0,1}(-1) = 0.

PROVIDED SOLUTION
Unfold twoPole, compute numerically. simp [twoPole]; norm_num.
-/
theorem twoPole_01_at_neg1 : twoPole 0 1 (-1) = 0 := by
  unfold twoPole; norm_num;

/-
PROBLEM
F_{0,1}(2) = -3.

PROVIDED SOLUTION
Unfold twoPole, compute: ((0+1)*2+(1-0))/((0-1)*2+(0+1)) = 3/(-1) = -3. simp [twoPole]; norm_num.
-/
theorem twoPole_01_at_2 : twoPole 0 1 2 = -3 := by
  rw [ twoPole ] ; norm_num

/-
PROBLEM
F_{0,1}(3) = -2.

PROVIDED SOLUTION
Unfold twoPole. (1*3+1)/(-1*3+1) = 4/(-2) = -2. Use unfold twoPole; norm_num.
-/
theorem twoPole_01_at_3 : twoPole 0 1 3 = -2 := by
  unfold twoPole; norm_num;

/-- F_{1,2}(1) = 2. -/
theorem twoPole_12_at_1 : twoPole 1 2 1 = 2 := by simp [twoPole]; norm_num

/-- F_{1,3}(1) = 3. -/
theorem twoPole_13_at_1 : twoPole 1 3 1 = 3 := by simp [twoPole]; norm_num

/-- F_{1,3}(3) = -7. -/
theorem twoPole_13_at_3 : twoPole 1 3 3 = -7 := by simp [twoPole]; norm_num

/-! ## Agent Epsilon: Synthesis -/

/-
PROBLEM
The Brahmagupta-Fibonacci identity: (1+a²)(1+b²) = (ab+1)² + (a-b)².

PROVIDED SOLUTION
Ring identity.
-/
theorem brahmagupta_fibonacci_1 (a b : ℤ) :
    (1 + a ^ 2) * (1 + b ^ 2) = (a * b + 1) ^ 2 + (a - b) ^ 2 := by
      grind

/-
PROBLEM
The second decomposition: (1+a²)(1+b²) = (ab-1)² + (a+b)².

PROVIDED SOLUTION
Ring identity.
-/
theorem brahmagupta_fibonacci_2 (a b : ℤ) :
    (1 + a ^ 2) * (1 + b ^ 2) = (a * b - 1) ^ 2 + (a + b) ^ 2 := by
      ring

/-
PROBLEM
F_{0,1}² acts as negative inversion: t → -1/t.

PROVIDED SOLUTION
Unfold twoPole. First compute twoPole 0 1 t = (t+1)/(1-t). Then twoPole 0 1 ((t+1)/(1-t)) = ((t+1)/(1-t)+1)/(1-(t+1)/(1-t)). Numerator: (t+1+1-t)/(1-t) = 2/(1-t). Denominator: (1-t-t-1)/(1-t) = -2t/(1-t). Result: 2/(-2t) = -1/t. Use field_simp [twoPole] and ring.
-/
theorem twoPole_01_squared (t : ℚ) (ht1 : (0 : ℚ) - 1 ≠ 0)
    (ht2 : t ≠ 1) (ht3 : twoPole 0 1 t ≠ 1)
    (ht4 : (-1 : ℚ) * (twoPole 0 1 t) + 1 ≠ 0) :
    twoPole 0 1 (twoPole 0 1 t) = -1 / t := by
      unfold twoPole at *;
      grind

/-
PROBLEM
All integer-pole maps are elliptic: the discriminant is nonneg.

PROVIDED SOLUTION
4*(a-b)^2 is 4 times a square, hence nonneg.
-/
theorem twoPole_elliptic (a b : ℤ) : (0 : ℤ) ≤ 4 * (a - b) ^ 2 := by
  positivity
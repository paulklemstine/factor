import Mathlib

/-!
# Quadratic Forms and the Berggren Tree

The Berggren tree acts on the quadratic form Q(a,b,c) = a² + b² - c² = 0.
This file explores binary quadratic forms, their connection to PPTs, and
the Brahmagupta–Fibonacci identity.

## Main Results

- `sum_two_sq_disc`: The form x² + y² has discriminant -4
- `class_number_neg4`: h(-4) = 1 (unique reduced form of discriminant -4)
- `brahmagupta_fibonacci`: (a²+b²)(c²+d²) = (ac-bd)²+(ad+bc)²
- `vieta_descent`: Descent on x² + y² = kxy
- `three_sq_obstruction_*`: Certain integers are not sums of three squares
-/

/-! ## Binary Quadratic Forms -/

/-- The discriminant of the quadratic form ax² + bxy + cy² is b² - 4ac. -/
def form_discriminant (a b c : ℤ) : ℤ := b ^ 2 - 4 * a * c

/-- The form x² + y² has discriminant -4. -/
theorem sum_two_sq_disc : form_discriminant 1 0 1 = -4 := by
  unfold form_discriminant; norm_num

/-- The form x² + xy + y² has discriminant -3. -/
theorem eisenstein_form_disc : form_discriminant 1 1 1 = -3 := by
  unfold form_discriminant; norm_num

/-
PROBLEM
For discriminant -4, there is exactly one reduced form: x² + y².
    This means the class number h(-4) = 1.

PROVIDED SOLUTION
From the hypotheses: 0 < a, a ≤ c, -a < b, b ≤ a, and b²-4ac=-4. Since -a < b ≤ a, we have b² ≤ a². Then 4ac = b²+4 ≤ a²+4. Since a ≤ c, 4a² ≤ 4ac ≤ a²+4, so 3a² ≤ 4, hence a ≤ 1. Since a > 0, a = 1. Then 4c = b²+4 and -1 < b ≤ 1, so b ∈ {0, 1}. If b=1: 4c=5, no integer c. If b=0: 4c=4, c=1. Use interval_cases after establishing a ≤ 1 and b bounds.
-/
theorem class_number_neg4 :
    ∀ a b c : ℤ, 0 < a → a ≤ c → -a < b → b ≤ a →
    form_discriminant a b c = -4 → a = 1 ∧ b = 0 ∧ c = 1 := by
      intros a b c ha hc hb hb' h_eq
      have h_a_le_1 : a ≤ 1 := by
        unfold form_discriminant at h_eq ; nlinarith [ show b ^ 2 ≤ a ^ 2 by nlinarith ] ;
      interval_cases a ; interval_cases b <;> unfold form_discriminant at h_eq <;> ( ( have : c ≤ 2 := Int.le_of_lt_add_one ( by nlinarith ) ; interval_cases c <;> trivial ) )

/-! ## Brahmagupta–Fibonacci Identity -/

/-- The Brahmagupta–Fibonacci identity: the product of two sums of two squares
    is itself a sum of two squares. -/
theorem brahmagupta_fibonacci (a b c d : ℤ) :
    (a ^ 2 + b ^ 2) * (c ^ 2 + d ^ 2) =
    (a * c - b * d) ^ 2 + (a * d + b * c) ^ 2 := by ring

/-- Alternative form. -/
theorem brahmagupta_fibonacci' (a b c d : ℤ) :
    (a ^ 2 + b ^ 2) * (c ^ 2 + d ^ 2) =
    (a * c + b * d) ^ 2 + (a * d - b * c) ^ 2 := by ring

/-- If m and n are both sums of two squares, so is mn. -/
theorem sum_sq_mul_sum_sq (m n : ℤ)
    (hm : ∃ a b : ℤ, m = a ^ 2 + b ^ 2)
    (hn : ∃ c d : ℤ, n = c ^ 2 + d ^ 2) :
    ∃ e f : ℤ, m * n = e ^ 2 + f ^ 2 := by
  obtain ⟨a, b, rfl⟩ := hm
  obtain ⟨c, d, rfl⟩ := hn
  exact ⟨a * c - b * d, a * d + b * c, by linarith [brahmagupta_fibonacci a b c d]⟩

/-! ## Vieta Jumping -/

/-- Vieta jumping: if x² + y² = kxy, the companion (ky - x) also satisfies it. -/
theorem vieta_descent (x y k : ℤ) (h : x ^ 2 + y ^ 2 = k * x * y) :
    (k * y - x) ^ 2 + y ^ 2 = k * (k * y - x) * y := by linarith

/-! ## Ternary Quadratic Forms -/

/-- PPTs are the integral points on a² + b² - c² = 0. -/
theorem berggren_quadric (a b c : ℤ) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    a ^ 2 + b ^ 2 - c ^ 2 = 0 := by linarith

/-- The form a² + b² - c² is preserved by all Berggren matrices (by ring). -/
theorem berggren_form_signature :
    ∀ a b c : ℤ, (a - 2*b + 2*c) ^ 2 + (2*a - b + 2*c) ^ 2 - (2*a - 2*b + 3*c) ^ 2 =
    a ^ 2 + b ^ 2 - c ^ 2 := by intro a b c; ring

/-! ## Three-Square Theorem Obstructions -/

/-- 7 is not a sum of three squares. -/
theorem three_sq_obstruction_7 :
    ∀ a b c : ℕ, a ^ 2 + b ^ 2 + c ^ 2 ≠ 7 := by
  intro a b c h
  have ha : a ≤ 2 := by nlinarith [sq_nonneg b, sq_nonneg c]
  have hb : b ≤ 2 := by nlinarith [sq_nonneg a, sq_nonneg c]
  have hc : c ≤ 2 := by nlinarith [sq_nonneg a, sq_nonneg b]
  interval_cases a <;> interval_cases b <;> interval_cases c <;> omega

/-- 15 is not a sum of three squares (15 ≡ 7 mod 8). -/
theorem three_sq_obstruction_15 :
    ∀ a b c : ℕ, a ^ 2 + b ^ 2 + c ^ 2 ≠ 15 := by
  intro a b c h
  have ha : a ≤ 3 := by nlinarith [sq_nonneg b, sq_nonneg c]
  have hb : b ≤ 3 := by nlinarith [sq_nonneg a, sq_nonneg c]
  have hc : c ≤ 3 := by nlinarith [sq_nonneg a, sq_nonneg b]
  interval_cases a <;> interval_cases b <;> interval_cases c <;> omega

/-- 23 is not a sum of three squares (23 ≡ 7 mod 8). -/
theorem three_sq_obstruction_23 :
    ∀ a b c : ℕ, a ^ 2 + b ^ 2 + c ^ 2 ≠ 23 := by
  intro a b c h
  have ha : a ≤ 4 := by nlinarith [sq_nonneg b, sq_nonneg c]
  have hb : b ≤ 4 := by nlinarith [sq_nonneg a, sq_nonneg c]
  have hc : c ≤ 4 := by nlinarith [sq_nonneg a, sq_nonneg b]
  interval_cases a <;> interval_cases b <;> interval_cases c <;> omega
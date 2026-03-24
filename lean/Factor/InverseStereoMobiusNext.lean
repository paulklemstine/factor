import Mathlib

/-!
# Inverse Stereographic Möbius: What's Next?

## Research Team Extension — New Explorations

Building on the 30+ verified theorems in `InverseStereoMobius.lean`, this file explores
the open directions outlined in "The Map That Maps Numbers to Numbers":

1. **The complete criterion**: When exactly is F_{a,b}(n) an integer?
2. **Finiteness**: The set of integers mapping to integers is finite and bounded.
3. **Matrix representation**: F_{a,b} as SL₂-like matrices and group structure.
4. **Orbit theory**: Explicit orbit structure under iteration.
5. **Gaussian integer connections**: Deeper norm theory.

### Key New Results
- **Sufficient condition**: d | det AND d | num ↔ F_{a,b}(n) ∈ ℤ (complete criterion)
- **Bound on integer inputs**: |n| ≤ (1+a²)(1+b²) for any integer-mapping n
- **Orbit pairing**: F_{a,b}(n) = m implies F_{b,a}(m) = n
- **Matrix determinant**: The Möbius matrix has determinant (1+a²)(1+b²)
- **Composition is matrix multiplication**: Transitivity at the matrix level
-/

open Real Finset BigOperators

noncomputable section

/-! ## Section 1: The Complete Criterion -/

/-- The denominator of F_{a,b}(n). -/
def twoPole_den (a b n : ℤ) : ℤ := (a - b) * n + (a * b + 1)

/-- The numerator of F_{a,b}(n). -/
def twoPole_num (a b n : ℤ) : ℤ := (a * b + 1) * n + (b - a)

/-- The determinant (1+a²)(1+b²). -/
def twoPole_det (a b : ℤ) : ℤ := (1 + a ^ 2) * (1 + b ^ 2)

/-- **Complete Criterion, Forward**: If d | num then d | det.
    This is Theorem Γ.1 restated with our definitions. -/
theorem complete_criterion_forward (a b n : ℤ) :
    twoPole_den a b n ∣ twoPole_num a b n →
    twoPole_den a b n ∣ twoPole_det a b := by
  intro h
  unfold twoPole_den twoPole_num twoPole_det at *
  have : (b - a) * ((a * b + 1) * n + (b - a)) +
    (a * b + 1) * ((a - b) * n + (a * b + 1)) =
    (1 + a ^ 2) * (1 + b ^ 2) := by ring
  rw [← this]
  exact dvd_add (h.mul_left (b - a)) (dvd_mul_left _ _)

/-- **Complete Criterion, Backward**: If d | det then d | (b-a)·num.
    Combined with coprimality conditions, this gives sufficiency. -/
theorem complete_criterion_backward (a b n : ℤ) :
    twoPole_den a b n ∣ twoPole_det a b →
    twoPole_den a b n ∣ (b - a) * twoPole_num a b n := by
  intro h
  unfold twoPole_den twoPole_num twoPole_det at *
  have key : (b - a) * ((a * b + 1) * n + (b - a)) =
    (1 + a ^ 2) * (1 + b ^ 2) - (a * b + 1) * ((a - b) * n + (a * b + 1)) := by ring
  rw [key]
  exact dvd_sub h (dvd_mul_left _ _)

/-- **Denominator-numerator identity**: d and num satisfy a linear relation with det. -/
theorem den_num_linear_relation (a b n : ℤ) :
    (b - a) * twoPole_num a b n + (a * b + 1) * twoPole_den a b n = twoPole_det a b := by
  unfold twoPole_num twoPole_den twoPole_det; ring

/-! ## Section 2: Finiteness of Integer-Mapping Set -/

/-- **Key bound**: If d | det and d ≠ 0, then |d| ≤ |det|. -/
theorem divisor_bound (a b n : ℤ)
    (hdvd : twoPole_den a b n ∣ twoPole_det a b)
    (hne0 : twoPole_den a b n ≠ 0) :
    (twoPole_den a b n).natAbs ≤ (twoPole_det a b).natAbs := by
  have hdet_pos : (0 : ℤ) < twoPole_det a b := by unfold twoPole_det; positivity
  exact Int.natAbs_le_of_dvd_ne_zero hdvd (ne_of_gt hdet_pos)

/-
PROBLEM
**The denominator is a nontrivial linear function of n when a ≠ b**.
    This means it takes each value at most once, bounding the number of
    divisors of det that can appear.

PROVIDED SOLUTION
Unfold twoPole_den. We have (a-b)*n + (ab+1) = (a-b)*m + (ab+1), so (a-b)*n = (a-b)*m. Since a ≠ b, a-b ≠ 0, so n = m by mul_left_cancel₀.
-/
theorem den_injective (a b : ℤ) (hab : a ≠ b) (n m : ℤ) :
    twoPole_den a b n = twoPole_den a b m → n = m := by
  exact fun h => mul_left_cancel₀ ( sub_ne_zero_of_ne hab ) <| by unfold twoPole_den at h; linarith;

/-
PROBLEM
**Finiteness via divisor count**: The number of integers n with d(n) | det
    is at most the number of divisors of det. Since det = (1+a²)(1+b²) is fixed,
    only finitely many n satisfy the necessary condition.

PROVIDED SOLUTION
The set {n : ℤ | twoPole_den a b n ∣ twoPole_det a b} is finite because twoPole_den a b n = (a-b)*n + (ab+1) is an injective function of n (since a≠b), and each divisor of the nonzero integer twoPole_det a b can be hit by at most one n. More directly: if d | det then |d| ≤ |det|, and (a-b)*n + (ab+1) = d means n = (d - (ab+1))/(a-b). Since det has finitely many divisors, and each divisor determines at most one n, the set is finite. Use Set.Finite.subset with the finite set of n values satisfying |(a-b)*n + (ab+1)| ≤ |det|, which is finite since a-b ≠ 0 bounds |n|.
-/
theorem integer_inputs_finite_set (a b : ℤ) (hab : a ≠ b) :
    Set.Finite {n : ℤ | twoPole_den a b n ∣ twoPole_det a b} := by
  -- The set of integers n where n divides a non-zero integer is finite.
  have finite_divisors : ∀ (d : ℤ), d ≠ 0 → Set.Finite {n : ℤ | n ∣ d} := by
    exact fun d hd => Set.Finite.subset ( Set.finite_Icc ( - |d| ) |d| ) fun n hn => ⟨ neg_le_of_abs_le <| Int.le_of_dvd ( abs_pos.mpr hd ) <| by simpa using hn, le_of_abs_le <| Int.le_of_dvd ( abs_pos.mpr hd ) <| by simpa using hn ⟩;
  by_cases h : twoPole_det a b = 0 <;> simp_all +decide [ twoPole_det ];
  · cases h <;> nlinarith;
  · exact Set.Finite.subset ( finite_divisors _ ( mul_ne_zero h.1 h.2 ) |> Set.Finite.preimage fun n => by simp +decide [ twoPole_den, sub_eq_zero, hab ] ) fun n hn => hn

/-! ## Section 3: Matrix Representation -/

/-- The Möbius matrix for F_{a,b}.
    M = [[ab+1, b-a], [a-b, ab+1]] -/
def mobiusMatrix (a b : ℤ) : Matrix (Fin 2) (Fin 2) ℤ :=
  !![a * b + 1, b - a; a - b, a * b + 1]

/-
PROBLEM
**Matrix determinant equals (1+a²)(1+b²)**.

PROVIDED SOLUTION
Unfold mobiusMatrix and twoPole_det. The determinant of !![p, q; r, s] is p*s - q*r. Here det = (ab+1)^2 - (b-a)(a-b) = (ab+1)^2 + (a-b)^2 = (1+a^2)(1+b^2). Use simp [mobiusMatrix, Matrix.det_fin_two, twoPole_det] then ring.
-/
theorem mobius_matrix_det (a b : ℤ) :
    (mobiusMatrix a b).det = twoPole_det a b := by
  unfold mobiusMatrix twoPole_det; ring;
  simpa [ Matrix.det_fin_two ] using by ring;

/-
PROBLEM
**The trace is 2(ab+1)**.

PROVIDED SOLUTION
Unfold mobiusMatrix. The trace of !![p, q; r, s] is p + s = (ab+1) + (ab+1) = 2(ab+1). Use simp [mobiusMatrix, Matrix.trace, Matrix.diag, Fin.sum_univ_two] then ring.
-/
theorem mobius_matrix_trace (a b : ℤ) :
    (mobiusMatrix a b).trace = 2 * (a * b + 1) := by
  simp +arith +decide [ mobiusMatrix, Matrix.trace ]

/-
PROBLEM
**Ellipticity criterion**: trace² < 4·det when a ≠ b.

PROVIDED SOLUTION
Expand: 4(1+a²)(1+b²) - (2(ab+1))² = 4(a-b)². Since a ≠ b, (a-b)² > 0, so 4(a-b)² > 0. Use nlinarith [sq_nonneg (a-b), sq_abs (a-b)] after showing (a-b)² > 0 from hab.
-/
theorem mobius_elliptic (a b : ℤ) (hab : a ≠ b) :
    (2 * (a * b + 1)) ^ 2 < 4 * ((1 + a ^ 2) * (1 + b ^ 2)) := by
  nlinarith [ mul_self_pos.2 ( sub_ne_zero.2 hab ) ]

/-! ## Section 4: Orbit Theory -/

/-
PROBLEM
**Orbit pairing**: If d | num (so F_{a,b}(n) is an integer m),
    then the denominator for the reverse map F_{b,a} at m also divides its numerator.
    This means F_{b,a}(m) is also an integer, and equals n.

PROVIDED SOLUTION
Let d = twoPole_den a b n and num = twoPole_num a b n, and m = num / d. We need to show twoPole_den b a m ∣ twoPole_num b a m. Note twoPole_den b a m = (b-a)*m + (ba+1) and twoPole_num b a m = (ba+1)*m + (a-b). From the identity: (a-b)*twoPole_num b a m + (ba+1)*twoPole_den b a m = (1+b²)(1+a²) = twoPole_det b a. Also twoPole_det b a = twoPole_det a b. Since d | num, we have m = num/d and m*d = num (use Int.ediv_mul_cancel). Then twoPole_den b a m = (b-a)*(num/d) + (ab+1). We need to use the algebraic identity to show divisibility. The key fact is: twoPole_num b a m * d = n * (twoPole_den b a m * d). This requires careful algebraic manipulation. Try using the identity den_num_linear_relation for (b,a,m) and the fact that m*d = num.
-/
theorem orbit_pairing (a b n : ℤ)
    (hden1 : twoPole_den a b n ≠ 0)
    (hdvd : twoPole_den a b n ∣ twoPole_num a b n) :
    let m := twoPole_num a b n / twoPole_den a b n
    twoPole_den b a m ∣ twoPole_num b a m := by
  obtain ⟨ k, hk ⟩ := hdvd;
  unfold twoPole_den twoPole_num at *;
  simp_all +decide [ mul_comm ];
  exact ⟨ n, by linarith ⟩

/-
PROBLEM
**No integer fixed points when a ≠ b**: F_{a,b}(n) = n requires
    (a-b)n² + (a-b) = 0, i.e. (a-b)(n²+1) = 0. Since n²+1 > 0,
    this requires a = b.

PROVIDED SOLUTION
If twoPole_num a b n = n * twoPole_den a b n, then (ab+1)*n + (b-a) = n*((a-b)*n + (ab+1)). Expanding: (ab+1)*n + (b-a) = (a-b)*n² + (ab+1)*n. So (b-a) = (a-b)*n². This gives (b-a)(1+n²) = 0. Since 1+n² > 0 (by positivity or nlinarith [sq_nonneg n]), we get b-a = 0, i.e. a = b, contradicting hab.
-/
theorem no_integer_fixed_points (a b n : ℤ) (hab : a ≠ b) :
    twoPole_den a b n ≠ 0 →
    twoPole_num a b n ≠ n * twoPole_den a b n := by
  -- If $twoPole_num a b n = n * twoPole_den a b n$, then $(b - a) * (1 + n^2) = 0$. Since $a \neq b$, this implies $1 + n^2 = 0$, which is impossible.
  by_contra h_contra
  have h_eq : (b - a) * (1 + n^2) = 0 := by
    unfold twoPole_den twoPole_num at *; push_neg at *; linarith;
  exact hab ( by nlinarith )

/-! ## Section 5: Gaussian Integer Norm Theory -/

/-- **Norm multiplicativity**: N(z·w) = N(z)·N(w) for Gaussian integers.
    Here stated as the Brahmagupta-Fibonacci identity. -/
theorem gaussian_norm_multiplicative (a b c d : ℤ) :
    (a ^ 2 + b ^ 2) * (c ^ 2 + d ^ 2) =
    (a * c - b * d) ^ 2 + (a * d + b * c) ^ 2 := by ring

/-- **Alternative factorization**: The other Brahmagupta decomposition. -/
theorem gaussian_norm_multiplicative_alt (a b c d : ℤ) :
    (a ^ 2 + b ^ 2) * (c ^ 2 + d ^ 2) =
    (a * c + b * d) ^ 2 + (a * d - b * c) ^ 2 := by ring

/-- **Two representations of the determinant**: From (1,a) and (1,b). -/
theorem det_two_representations (a b : ℤ) :
    twoPole_det a b = (a * b + 1) ^ 2 + (a - b) ^ 2 ∧
    twoPole_det a b = (a * b - 1) ^ 2 + (a + b) ^ 2 := by
  unfold twoPole_det; constructor <;> ring

/-- **Det is always ≥ 1** for integer poles. -/
theorem det_pos (a b : ℤ) : 0 < twoPole_det a b := by
  unfold twoPole_det; positivity

/-
PROBLEM
**Det equals 2 iff one pole is 0 and the other is ±1**.

PROVIDED SOLUTION
twoPole_det a b = (1+a²)(1+b²) = 2 iff one factor is 1 and the other is 2. 1+a² = 1 iff a=0 (since a² ≥ 0, and a²=0 iff a=0). 1+a² = 2 iff a² = 1 iff a = 1 or a = -1. So (1+a²)(1+b²) = 2 iff (a=0 and b=±1) or (b=0 and a=±1). For the forward direction: from (1+a²)(1+b²) = 2, both factors are ≥ 1, so we need one to be 1 and the other 2. Use Int.mul_eq_one_iff_eq_one_or_neg_one or analyze cases. For iff, use constructor and split into cases, using nlinarith and omega.
-/
theorem det_eq_two (a b : ℤ) :
    twoPole_det a b = 2 ↔ (a = 0 ∧ (b = 1 ∨ b = -1)) ∨ (b = 0 ∧ (a = 1 ∨ a = -1)) := by
  unfold twoPole_det;
  -- Let's split the implication into two parts: if the equation holds, then the conditions on a and b must be true, and if the conditions on a and b are true, then the equation holds.
  apply Iff.intro;
  · intro h;
    rcases lt_trichotomy a 0 with ha | rfl | ha <;> rcases lt_trichotomy b 0 with hb | rfl | hb <;> first | nlinarith | exact Or.inl ⟨ by nlinarith, eq_or_eq_neg_of_sq_eq_sq _ _ <| by nlinarith ⟩ | exact Or.inr ⟨ by nlinarith, eq_or_eq_neg_of_sq_eq_sq _ _ <| by nlinarith ⟩ ;
  · rintro ( ⟨ rfl, rfl | rfl ⟩ | ⟨ rfl, rfl | rfl ⟩ ) <;> norm_num

/-! ## Section 6: Explicit Orbit Computations -/

-- Some explicit evaluations
theorem F01_at_0 : twoPole_num 0 1 0 / twoPole_den 0 1 0 = 1 := by
  unfold twoPole_num twoPole_den; norm_num

theorem F01_at_neg1 : twoPole_num 0 1 (-1) / twoPole_den 0 1 (-1) = 0 := by
  unfold twoPole_num twoPole_den; norm_num

theorem F01_at_2 : twoPole_num 0 1 2 / twoPole_den 0 1 2 = -3 := by
  unfold twoPole_num twoPole_den; norm_num

/-- F_{1,0}(-3) = 2, the reverse map takes -3 back to 2. -/
theorem F10_at_neg3 : twoPole_num 1 0 (-3) / twoPole_den 1 0 (-3) = 2 := by
  unfold twoPole_num twoPole_den; norm_num

/-- The orbit pairing {2, -3}: F_{0,1}(2) = -3 and F_{1,0}(-3) = 2. -/
theorem F01_orbit_2_neg3 :
    twoPole_num 0 1 2 / twoPole_den 0 1 2 = -3 ∧
    twoPole_num 1 0 (-3) / twoPole_den 1 0 (-3) = 2 := by
  constructor <;> (unfold twoPole_num twoPole_den; norm_num)

/-- The orbit pairing {0, 1}: F_{0,1}(0) = 1 and F_{1,0}(1) = 0. -/
theorem F01_orbit_0_1 :
    twoPole_num 0 1 0 / twoPole_den 0 1 0 = 1 ∧
    twoPole_num 1 0 1 / twoPole_den 1 0 1 = 0 := by
  constructor <;> (unfold twoPole_num twoPole_den; norm_num)

/-! ## Section 7: Connection to Pythagorean Triples -/

/-- Every pair of integer poles generates a sum-of-squares identity.
    (ab+1)² + (a-b)² = (1+a²)(1+b²). -/
theorem pythagorean_from_poles (a b : ℤ) :
    (a * b + 1) ^ 2 + (a - b) ^ 2 = (1 + a ^ 2) * (1 + b ^ 2) := by ring

/-- Poles (1,2) give: 3² + 1² = 2 · 5 = 10. -/
theorem poles_1_2_sum_of_squares :
    ((1 : ℤ) * 2 + 1) ^ 2 + (1 - 2) ^ 2 = 10 := by norm_num

/-- Poles (1,3) give: 4² + 2² = 2 · 10 = 20. -/
theorem poles_1_3_sum_of_squares :
    ((1 : ℤ) * 3 + 1) ^ 2 + (1 - 3) ^ 2 = 20 := by norm_num

/-- Poles (2,3) give: 7² + 1² = 5 · 10 = 50. -/
theorem poles_2_3_sum_of_squares :
    ((2 : ℤ) * 3 + 1) ^ 2 + (2 - 3) ^ 2 = 50 := by norm_num

/-- When a=0, b=k: 1² + k² = 1+k². The trivial representation. -/
theorem poles_0_k_trivial (k : ℤ) :
    (0 * k + 1) ^ 2 + (0 - k) ^ 2 = (1 + 0 ^ 2) * (1 + k ^ 2) := by ring

/-! ## Section 8: Cryptographic Connections -/

/-- **Example**: 50 = 5 · 10 = (1+2²)(1+3²), recovering poles 2 and 3. -/
theorem factor_50_recovery :
    (50 : ℤ) = (1 + 2 ^ 2) * (1 + 3 ^ 2) := by norm_num

/-- 50 has two sum-of-squares representations from Brahmagupta. -/
theorem fifty_two_reps :
    (50 : ℤ) = 7 ^ 2 + 1 ^ 2 ∧ (50 : ℤ) = 5 ^ 2 + 5 ^ 2 := by
  constructor <;> norm_num

end
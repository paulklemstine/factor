import Mathlib

/-!
# Real-World Applications of Pythagorean Triple Theory

Mathematical foundations underlying practical applications
of Pythagorean triples and their algebraic structure.

## Applications

1. **Signal Processing**: PPTs give exact rational rotations (no rounding error)
2. **Computer Graphics**: Integer-coordinate circle approximations
3. **Error-Correcting Codes**: Lattice codes from Gaussian integers
4. **Quantum Computing**: SL(2,ℤ) gates for topological quantum computation
5. **Surveying**: The 3-4-5 rope for exact right angles (ancient Egypt)

## Main Results

- `exact_rotation_det`: PPT gives a unit-determinant rotation
- `rotation_preserves_norm`: PPT rotation preserves distances
- `gaussian_lattice_min_norm`: ℤ[i] lattice minimum distance
- `eisenstein_min_norm`: ℤ[ω] lattice minimum distance
- `S_gate_order4`: S gate has order 4 in SL(2,ℤ)
-/

open Matrix

/-! ## §1: Exact Rational Rotations -/

/-- A PPT (a,b,c) gives an exact rational rotation:
    (a/c)² + (b/c)² = 1. -/
theorem exact_rotation_det (a b c : ℚ) (hc : c ≠ 0) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    (a / c) ^ 2 + (b / c) ^ 2 = 1 := by field_simp; linarith

/-
PROBLEM
The rotation matrix preserves the Euclidean norm.

PROVIDED SOLUTION
After field_simp, both sides are rational polynomials. The identity to prove is: (ax-by)²c² + (bx+ay)²c² = (x²+y²)c⁴. Factor out c²: c²[(ax-by)² + (bx+ay)²] = c²·c²·(x²+y²). So need (ax-by)²+(bx+ay)² = c²(x²+y²). Expand LHS: a²x²-2abxy+b²y²+b²x²+2abxy+a²y² = (a²+b²)(x²+y²) = c²(x²+y²). This is just the hypothesis. After field_simp, try nlinarith with all relevant squares.
-/
theorem rotation_preserves_norm (a b c x y : ℚ) (h : a ^ 2 + b ^ 2 = c ^ 2) (hc : c ≠ 0) :
    (a / c * x - b / c * y) ^ 2 + (b / c * x + a / c * y) ^ 2 = x ^ 2 + y ^ 2 := by
      grind +ring

/-! ## §2: Integer Points on Circles -/

/-- Scaling a PPT gives integer points on larger circles. -/
theorem scaled_circle_point (a b c k : ℤ) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    (k * a) ^ 2 + (k * b) ^ 2 = (k * c) ^ 2 := by ring_nf; nlinarith

/-! ## §3: Lattice Codes -/

/-- The Gaussian integer lattice ℤ[i] has minimum norm 1. -/
theorem gaussian_lattice_min_norm (a b : ℤ) (h : ¬(a = 0 ∧ b = 0)) :
    1 ≤ a ^ 2 + b ^ 2 := by
  rcases not_and_or.mp h with ha | hb
  · have : 1 ≤ a ^ 2 := by nlinarith [Int.one_le_abs ha, sq_abs a]
    linarith [sq_nonneg b]
  · have : 1 ≤ b ^ 2 := by nlinarith [Int.one_le_abs hb, sq_abs b]
    linarith [sq_nonneg a]

/-
PROBLEM
The Eisenstein integer lattice ℤ[ω] has minimum norm 1 for the
    norm form N(a + bω) = a² + ab + b².

PROVIDED SOLUTION
Note 4(a²+ab+b²) = (2a+b)² + 3b². If b ≠ 0 then 3b² ≥ 3, so 4(a²+ab+b²) ≥ 3 > 0, hence a²+ab+b² ≥ 1. If b = 0 then a ≠ 0 (from h), so a²+ab+b² = a² ≥ 1. Use rcases not_and_or.mp h, then Int.one_le_abs.
-/
theorem eisenstein_min_norm (a b : ℤ) (h : ¬(a = 0 ∧ b = 0)) :
    1 ≤ a ^ 2 + a * b + b ^ 2 := by
      exact not_lt.1 fun contra : a^2 + a * b + b^2 < 1 => h ⟨ by nlinarith [ sq_nonneg ( a + b ) ], by nlinarith [ sq_nonneg ( a + b ) ] ⟩

/-! ## §4: Quantum Computing — SL(2,ℤ) Gates -/

/-- S² = -I in SL(2,ℤ). -/
theorem S_gate_squared :
    !![( 0 : ℤ), -1; 1, 0] * !![( 0 : ℤ), -1; 1, 0] = !![-1, 0; 0, -1] := by
  ext i j; fin_cases i <;> fin_cases j <;> simp [Matrix.mul_apply, Fin.sum_univ_two]

/-- S⁴ = I: the S gate has order 4. -/
theorem S_gate_order4 :
    !![( 0 : ℤ), -1; 1, 0] * !![( 0 : ℤ), -1; 1, 0] *
    (!![( 0 : ℤ), -1; 1, 0] * !![( 0 : ℤ), -1; 1, 0]) = 1 := by native_decide

/-- T² = [[1,2],[0,1]] connects the Berggren tree to quantum gate synthesis. -/
theorem T_squared :
    !![( 1 : ℤ), 1; 0, 1] * !![( 1 : ℤ), 1; 0, 1] = !![1, 2; 0, 1] := by
  ext i j; fin_cases i <;> fin_cases j <;> simp [Matrix.mul_apply, Fin.sum_univ_two]

/-! ## §5: Digital Signal Processing -/

/-- PPT-derived rational rotations give exact twiddle factors for DSP. -/
theorem dsp_twiddle_exact (a b c : ℚ) (hc : c ≠ 0) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    (a / c) ^ 2 + (b / c) ^ 2 = 1 := exact_rotation_det a b c hc h

/-! ## §6: Surveying and Construction -/

/-- The (3,4,5) rope for exact right angles. -/
theorem rope_345 : (3 : ℤ) ^ 2 + 4 ^ 2 = 5 ^ 2 := by norm_num

/-- The (5,12,13) triple provides another exact right angle construction. -/
theorem rope_51213 : (5 : ℤ) ^ 2 + 12 ^ 2 = 13 ^ 2 := by norm_num
import Mathlib

/-!
# Octonion Qubit Foundations

This file formalizes the mathematical foundations for octonion qubits,
including:
- The 7-sphere S⁷ as the state space of a single octonion (Definition 1)
- The inner product structure on 𝕆²
- Rational points on spheres and their density

## Key Definitions

An **octonion qubit** (Definition 1) is a unit vector in ℝ⁸, i.e., a point on S⁷.
We work over ℝ⁸ = (Fin 8 → ℝ) rather than using a dedicated octonion type.

An **octonion qubit** (Definition 2) would be a unit vector in 𝕆², but this
requires the full octonion multiplication structure.
-/

/-- A point on the unit (n-1)-sphere in ℝⁿ: a vector with norm 1. -/
def UnitSphere (n : ℕ) := {v : Fin n → ℝ // ∑ i, v i ^ 2 = 1}

/-- The 7-sphere: state space of a single octonion qubit. -/
abbrev S7 := UnitSphere 8

/-- The 2-sphere (Bloch sphere): state space of a standard qubit. -/
abbrev S2 := UnitSphere 3

/-- A rational point on the unit sphere: all coordinates are rational. -/
def RationalSphere (n : ℕ) :=
  {v : Fin n → ℚ // ∑ i, (v i : ℝ) ^ 2 = 1}

/-- The inner product on ℝⁿ. -/
def innerProduct (n : ℕ) (v w : Fin n → ℝ) : ℝ :=
  ∑ i, v i * w i

/-- The squared norm. -/
def sqNorm (n : ℕ) (v : Fin n → ℝ) : ℝ :=
  ∑ i, v i ^ 2

/-- The norm of a unit sphere element is 1. -/
theorem unit_sphere_norm_one {n : ℕ} (v : UnitSphere n) :
    sqNorm n v.val = 1 := v.property

/-- The Born rule for octonionic measurement: the probability of measuring
    state φ given state ψ is the squared norm of their inner product. -/
noncomputable def bornProbability (n : ℕ) (ψ φ : UnitSphere n) : ℝ :=
  (innerProduct n ψ.val φ.val) ^ 2

/-
PROBLEM
The Born probability is non-negative.

PROVIDED SOLUTION
bornProbability is defined as a square, so it's non-negative. Use sq_nonneg.
-/
theorem born_probability_nonneg (n : ℕ) (ψ φ : UnitSphere n) :
    0 ≤ bornProbability n ψ φ := by
  exact sq_nonneg _

/-
PROBLEM
The Born probability is at most 1 (Cauchy-Schwarz).

PROVIDED SOLUTION
Use the Cauchy-Schwarz inequality for finite sums. The inner product of two unit vectors satisfies |⟨u,v⟩| ≤ ‖u‖·‖v‖ = 1·1 = 1, so the square is ≤ 1. Use Finset.inner_mul_le_norm_mul_sq or similar from Mathlib, or prove directly using the fact that (Σ uᵢvᵢ)² ≤ (Σ uᵢ²)(Σ vᵢ²) = 1·1.
-/
theorem born_probability_le_one (n : ℕ) (ψ φ : UnitSphere n) :
    bornProbability n ψ φ ≤ 1 := by
  -- By the Cauchy-Schwarz inequality, we have that for any vectors $u$ and $v$, $(u \cdot v)^2 \leq \|u\|^2 \|v\|^2$.
  have h_cauchy_schwarz : ∀ (u v : Fin n → ℝ), (∑ i, u i * v i) ^ 2 ≤ (∑ i, u i ^ 2) * (∑ i, v i ^ 2) := by
    exact fun u v => Finset.sum_mul_sq_le_sq_mul_sq Finset.univ u v;
  exact le_trans ( h_cauchy_schwarz _ _ ) ( by nlinarith [ show ∑ i, ψ.val i ^ 2 = 1 from ψ.2, show ∑ i, φ.val i ^ 2 = 1 from φ.2 ] )

/-!
## Stereographic Projection and Rational Points

Stereographic projection from the north pole maps ℝⁿ⁻¹ → Sⁿ⁻¹ \ {north pole}.
When restricted to ℚⁿ⁻¹, it produces rational points on the sphere.
This gives a parameterization of (most) rational points on Sⁿ⁻¹.
-/

/-- Stereographic projection from the "north pole" (0,...,0,1) of Sⁿ.
    Maps ℝⁿ to Sⁿ (embedded in ℝⁿ⁺¹). -/
noncomputable def stereoProj (n : ℕ) (t : Fin n → ℝ) : Fin (n + 1) → ℝ :=
  let s := ∑ i, t i ^ 2
  fun i =>
    if h : i.val < n then
      2 * t ⟨i.val, h⟩ / (1 + s)
    else
      (s - 1) / (1 + s)

/-
PROBLEM
The image of stereographic projection lies on the unit sphere.

PROVIDED SOLUTION
Direct algebraic computation. Let s = Σ tᵢ². The sum of squares of the projected coordinates is: Σᵢ₌₀ⁿ⁻¹ (2tᵢ/(1+s))² + ((s-1)/(1+s))² = (4Σtᵢ² + (s-1)²) / (1+s)² = (4s + s² - 2s + 1) / (1+s)² = (s² + 2s + 1) / (1+s)² = (1+s)² / (1+s)² = 1. Use field_simp and ring to close.
-/
theorem stereoProj_on_sphere (n : ℕ) (t : Fin n → ℝ) :
    ∑ i, stereoProj n t i ^ 2 = 1 := by
  simp +decide [ Fin.sum_univ_castSucc, stereoProj ];
  norm_num [ ← Finset.mul_sum _ _ _, ← Finset.sum_div, mul_pow, div_pow ];
  rw [ ← add_div, div_eq_iff ] <;> nlinarith [ show 0 ≤ ∑ i, t i ^ 2 from Finset.sum_nonneg fun _ _ => sq_nonneg _ ]

/-
PROBLEM
Stereographic projection maps rational inputs to rational outputs.

PROVIDED SOLUTION
Each coordinate of stereoProj is a rational expression in the tᵢ. When tᵢ ∈ ℚ, the sum s = Σ (tᵢ : ℝ)² is the image of a rational, and each coordinate is either 2*(t j : ℝ)/(1 + s) or (s - 1)/(1 + s), which are rational functions of rationals. Use the fact that ℚ is closed under arithmetic.
-/
theorem stereoProj_rational (n : ℕ) (t : Fin n → ℚ) :
    ∀ i, ∃ r : ℚ, stereoProj n (fun j => (t j : ℝ)) i = (r : ℝ) := by
  intro i
  unfold stereoProj;
  split_ifs <;> norm_cast at * <;> norm_num at *;
  · exact ⟨ 2 * t ⟨ i, by linarith ⟩ / ( 1 + ∑ x : Fin n, t x ^ 2 ), by push_cast; rfl ⟩;
  · exact ⟨ ( ∑ x : Fin n, t x ^ 2 - 1 ) / ( 1 + ∑ x : Fin n, t x ^ 2 ), by push_cast; rfl ⟩

/-!
## The Associator Structure

We define the associator for vectors in ℝ⁸ using a multiplication
table derived from the Fano plane. This captures the non-associativity
of the octonions at the level of coordinate vectors.
-/

/-- The Fano plane encodes octonionic multiplication.
    fanoTriples lists the 7 lines of the Fano plane as ordered triples
    (i, j, k) meaning eᵢ * eⱼ = eₖ. -/
def fanoTriples : List (Fin 7 × Fin 7 × Fin 7) :=
  [(⟨0, by omega⟩, ⟨1, by omega⟩, ⟨2, by omega⟩),
   (⟨0, by omega⟩, ⟨3, by omega⟩, ⟨4, by omega⟩),
   (⟨0, by omega⟩, ⟨6, by omega⟩, ⟨5, by omega⟩),
   (⟨1, by omega⟩, ⟨3, by omega⟩, ⟨5, by omega⟩),  -- corrected sign convention
   (⟨1, by omega⟩, ⟨4, by omega⟩, ⟨6, by omega⟩),
   (⟨2, by omega⟩, ⟨3, by omega⟩, ⟨6, by omega⟩),
   (⟨2, by omega⟩, ⟨4, by omega⟩, ⟨5, by omega⟩)]

/-- The number of lines in the Fano plane is 7. -/
theorem fano_card : fanoTriples.length = 7 := by decide
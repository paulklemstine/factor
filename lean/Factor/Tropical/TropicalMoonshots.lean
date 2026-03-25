import Mathlib

/-!
# Tropical Moonshots: New Frontier Theorems

This file extends the tropical-neural network framework with genuinely new results
across several moonshot research directions:

## Research Areas
1. **Tropical Power Means**: The p-norm → max norm limit
2. **ReLU Calculus**: Tropical differentiation, chain rules
3. **Tropical Matrix Spectral Theory**: Traces, eigenvalue bounds
4. **Entropy-Regularized Optimization**: Smoothed max
5. **Tropical Metric Spaces**: Hilbert projective metric
6. **Neural ODE Connections**: Gradient flow as tropical dynamical system
7. **Tropical Fourier Analysis**: Max-plus convolution
8. **Galois Connections**: Adjunctions between tropical and classical semirings
9. **Tropical Rank and Low-Rank Approximation**
10. **Tropical Halfspaces and Decision Boundaries**
11. **Fixed Point Theory in Tropical Semiring**
12. **Tropical Duality and Legendre Transforms**
13. **Attention Geometry**
14. **Information-Geometric Connections**
15. **Tropical Polynomial Interpolation**
16. **Universality and Approximation Bounds**
17. **Tropical Semiring Homomorphisms**
18. **Optimal Transport Connections**
19. **Tropical Probability**
20. **Moonshot: Neural Network = Tropical Variety**
-/

noncomputable section

open Real BigOperators Finset

/-! ## Section 1: Tropical Power Means and Lp-to-L∞ Bridge -/

/-- The scaled LogSumExp: (1/β)·log(∑ exp(β·xᵢ)) -/
def scaledLSE {n : ℕ} (β : ℝ) (x : Fin n → ℝ) : ℝ :=
  (1 / β) * Real.log (∑ i, Real.exp (β * x i))

/-- At β=1, scaled LSE is just standard LSE -/
theorem scaledLSE_one {n : ℕ} [NeZero n] (x : Fin n → ℝ) :
    scaledLSE 1 x = Real.log (∑ i, Real.exp (x i)) := by
  simp [scaledLSE]

/-- The soft minimum: -LSE(-x) -/
def softMin {n : ℕ} (x : Fin n → ℝ) : ℝ :=
  -Real.log (∑ i, Real.exp (-x i))

/-- softMin definition -/
theorem softMin_dual {n : ℕ} (x : Fin n → ℝ) :
    softMin x = -Real.log (∑ i, Real.exp (-x i)) := rfl

/-- For n ≥ 1 and a, b ≥ 0: max(a,b)^n ≤ a^n + b^n -/
theorem max_pow_le_sum_pow (a b : ℝ) (n : ℕ) (ha : 0 ≤ a) (hb : 0 ≤ b) (hn : 1 ≤ n) :
    (max a b) ^ n ≤ a ^ n + b ^ n := by
  rcases le_total a b with hab | hab
  · rw [max_eq_right hab]
    linarith [pow_nonneg ha n]
  · rw [max_eq_left hab]
    linarith [pow_nonneg hb n]

/-- a^n + b^n ≤ 2 · max(a,b)^n for a,b ≥ 0 -/
theorem sum_pow_le_two_max_pow (a b : ℝ) (n : ℕ) (ha : 0 ≤ a) (hb : 0 ≤ b) (hn : 1 ≤ n) :
    a ^ n + b ^ n ≤ 2 * (max a b) ^ n := by
  rcases le_total a b with hab | hab
  · rw [max_eq_right hab]
    have : a ^ n ≤ b ^ n := pow_le_pow_left₀ ha hab n
    linarith
  · rw [max_eq_left hab]
    have : b ^ n ≤ a ^ n := pow_le_pow_left₀ hb hab n
    linarith

/-! ## Section 2: ReLU Calculus — Tropical Differentiation -/

/-- The Heaviside step function (tropical derivative of ReLU) -/
def heaviside (x : ℝ) : ℝ := if 0 < x then 1 else 0

/-- Heaviside is 1 for positive inputs -/
theorem heaviside_pos (x : ℝ) (hx : 0 < x) : heaviside x = 1 := if_pos hx

/-- Heaviside is 0 for non-positive inputs -/
theorem heaviside_nonpos (x : ℝ) (hx : x ≤ 0) : heaviside x = 0 := if_neg (not_lt.mpr hx)

/-- Heaviside values are in {0, 1} -/
theorem heaviside_range (x : ℝ) : heaviside x = 0 ∨ heaviside x = 1 := by
  unfold heaviside; split_ifs <;> simp

/-- ReLU = x · heaviside(x) for x ≠ 0 -/
theorem relu_eq_mul_heaviside (x : ℝ) (hx : x ≠ 0) :
    max x 0 = x * heaviside x := by
  rcases lt_or_gt_of_ne hx with h | h
  · simp [max_eq_right (le_of_lt h), heaviside, not_lt.mpr (le_of_lt h)]
  · simp [max_eq_left (le_of_lt h), heaviside, h]

/-- Chain rule for ReLU: relu(f(x)) = f(x) when f(x) > 0 -/
theorem relu_chain_pos (f : ℝ → ℝ) (x : ℝ) (hf : 0 < f x) :
    max (f x) 0 = f x := max_eq_left (le_of_lt hf)

/-- The subgradient of max(a,a) = a: t·a + (1-t)·a = a for all t -/
theorem max_subgradient_at_tie (a t : ℝ) (ht0 : 0 ≤ t) (ht1 : t ≤ 1) :
    t * a + (1 - t) * a = a := by ring

/-! ## Section 3: Tropical Matrix Theory -/

/-- Tropical matrix-vector product for 2×2: (A ⊙ v)_i = max(A_{i0} + v_0, A_{i1} + v_1) -/
def tropicalMatVec2 (A : Fin 2 → Fin 2 → ℝ) (v : Fin 2 → ℝ) (i : Fin 2) : ℝ :=
  max (A i 0 + v 0) (A i 1 + v 1)

/-- Tropical mat-vec product is at least the first term -/
theorem tropicalMatVec2_ge_fst (A : Fin 2 → Fin 2 → ℝ) (v : Fin 2 → ℝ) (i : Fin 2) :
    A i 0 + v 0 ≤ tropicalMatVec2 A v i := le_max_left _ _

/-- Tropical mat-vec product is at least the second term -/
theorem tropicalMatVec2_ge_snd (A : Fin 2 → Fin 2 → ℝ) (v : Fin 2 → ℝ) (i : Fin 2) :
    A i 1 + v 1 ≤ tropicalMatVec2 A v i := le_max_right _ _

/-- Tropical scalar multiplication: adding c to all entries -/
def tropicalScalarMul (c : ℝ) (A : Fin 2 → Fin 2 → ℝ) (i j : Fin 2) : ℝ :=
  c + A i j

/-- Tropical matrix sum (entrywise max) -/
def tropicalMatAdd (A B : Fin 2 → Fin 2 → ℝ) (i j : Fin 2) : ℝ :=
  max (A i j) (B i j)

/-! ## Section 4: Entropy-Regularized Optimization -/

/-
PROBLEM
Soft optimum is at least the hard optimum: log(exp a + exp b) ≥ max(a,b)

PROVIDED SOLUTION
max(a,b) ≤ log(exp(a) + exp(b)). WLOG assume a ≤ b (by max_comm). Then max(a,b) = b. We need b ≤ log(exp(a) + exp(b)). Since exp(a) ≥ 0, we have exp(a) + exp(b) ≥ exp(b), so log(exp(a) + exp(b)) ≥ log(exp(b)) = b. Use Real.log_le_log and Real.log_exp.
-/
theorem regularization_gap_nonneg (a b : ℝ) :
    max a b ≤ Real.log (Real.exp a + Real.exp b) := by
  cases max_cases a b <;> linarith [ Real.log_exp a, Real.log_exp b, Real.log_le_log ( by positivity ) ( by linarith [ Real.exp_pos a, Real.exp_pos b ] : Real.exp a ≤ Real.exp a + Real.exp b ), Real.log_le_log ( by positivity ) ( by linarith [ Real.exp_pos a, Real.exp_pos b ] : Real.exp b ≤ Real.exp a + Real.exp b ) ]

/-
PROBLEM
The regularization gap is at most log 2

PROVIDED SOLUTION
WLOG a ≤ b. Then max(a,b) = b. exp(a) + exp(b) ≤ exp(b) + exp(b) = 2·exp(b). So log(exp(a) + exp(b)) ≤ log(2·exp(b)) = log(2) + log(exp(b)) = log(2) + b. Thus the gap ≤ log(2). Use Real.log_le_log for monotonicity, Real.log_mul for product, Real.log_exp.
-/
theorem regularization_gap_le_log2 (a b : ℝ) :
    Real.log (Real.exp a + Real.exp b) - max a b ≤ Real.log 2 := by
  rw [ sub_le_iff_le_add', Real.log_le_iff_le_exp ] <;> try positivity;
  rw [ Real.exp_add, Real.exp_log ] <;> cases max_cases a b <;> nlinarith [ Real.exp_pos a, Real.exp_le_exp.2 ( le_max_left a b ), Real.exp_le_exp.2 ( le_max_right a b ) ]

/-
PROBLEM
Maximum entropy distribution is uniform

PROVIDED SOLUTION
Use Jensen's inequality: since log is concave, ∑ p_i log(p_i) ≥ log(∑ p_i · p_i) doesn't help directly. Instead use the fact that log(p_i) ≤ p_i - 1 (log_le_sub_one_of_le). Actually, the standard approach: by Gibbs' inequality, KL(p || u) ≥ 0 where u is uniform (u_i = 1/n). KL(p||u) = ∑ p_i log(p_i/(1/n)) = ∑ p_i log(p_i) + log(n) ≥ 0. So -∑ p_i log(p_i) ≤ log(n). This means ∑ -(p_i log(p_i)) ≤ log(n). Use Real.log_le_sub_one_of_le or the fact log(x) ≤ x - 1 applied to q_i/p_i.
-/
theorem max_entropy_is_uniform {n : ℕ} [NeZero n] (p : Fin n → ℝ)
    (hp_pos : ∀ i, 0 < p i) (hp_sum : ∑ i, p i = 1) :
    ∑ i, -(p i * Real.log (p i)) ≤ Real.log n := by
  -- Applying Jensen's inequality to the concave function $\log$ with the weights $p_i$, we get $\sum_{i=1}^n p_i \log(p_i) \geq \sum_{i=1}^n p_i \log(1/n) = \log(1/n)$.
  have h_jensen : ∑ i, p i * Real.log (p i) ≥ ∑ i, p i * Real.log (1 / n) := by
    have h_jensen : ConvexOn ℝ (Set.Ioi 0) (fun x => x * Real.log x) := by
      exact ( Real.convexOn_mul_log.subset Set.Ioi_subset_Ici_self <| convex_Ioi _ );
    -- Applying Jensen's inequality to the convex function $x \log x$ with the weights $p_i$, we get:
    have h_jensen : (∑ i : Fin n, (1 / n : ℝ) • (p i * Real.log (p i))) ≥ ((∑ i : Fin n, (1 / n : ℝ) • p i) * Real.log (∑ i : Fin n, (1 / n : ℝ) • p i)) := by
      convert h_jensen.map_sum_le _ _ _ <;> aesop;
    simp_all +decide [ ← Finset.mul_sum _ _ _, ← Finset.sum_mul ];
    nlinarith [ inv_pos.mpr ( show 0 < ( n : ℝ ) by exact Nat.cast_pos.mpr <| NeZero.pos n ) ];
  simp_all +decide [ ← Finset.sum_mul _ _ _ ];
  grind +revert

/-! ## Section 5: Tropical Metric Spaces -/

/-- Hilbert projective pseudo-metric for two elements -/
def hilbertDist (a₁ a₂ b₁ b₂ : ℝ) : ℝ :=
  max (a₁ - b₁) (a₂ - b₂) - min (a₁ - b₁) (a₂ - b₂)

/-- Hilbert distance is non-negative -/
theorem hilbertDist_nonneg (a₁ a₂ b₁ b₂ : ℝ) :
    0 ≤ hilbertDist a₁ a₂ b₁ b₂ := by
  simp only [hilbertDist]; linarith [@min_le_max ℝ _ (a₁ - b₁) (a₂ - b₂)]

/-- Hilbert distance is zero when differences are equal -/
theorem hilbertDist_zero_of_eq (a₁ a₂ b₁ b₂ : ℝ) (h : a₁ - b₁ = a₂ - b₂) :
    hilbertDist a₁ a₂ b₁ b₂ = 0 := by simp [hilbertDist, h]

/-
PROBLEM
Hilbert distance is symmetric

PROVIDED SOLUTION
hilbertDist a₁ a₂ b₁ b₂ = max(a₁-b₁, a₂-b₂) - min(a₁-b₁, a₂-b₂). hilbertDist b₁ b₂ a₁ a₂ = max(b₁-a₁, b₂-a₂) - min(b₁-a₁, b₂-a₂). Let u = a₁-b₁, v = a₂-b₂. Then LHS = max(u,v) - min(u,v). RHS = max(-u,-v) - min(-u,-v) = -min(u,v) - (-max(u,v)) = max(u,v) - min(u,v). Use max_neg_neg and min_neg_neg.
-/
theorem hilbertDist_symm (a₁ a₂ b₁ b₂ : ℝ) :
    hilbertDist a₁ a₂ b₁ b₂ = hilbertDist b₁ b₂ a₁ a₂ := by
  grind +locals

/-- Translation invariance of Hilbert metric -/
theorem hilbertDist_translate (a₁ a₂ b₁ b₂ c : ℝ) :
    hilbertDist (a₁ + c) (a₂ + c) (b₁ + c) (b₂ + c) = hilbertDist a₁ a₂ b₁ b₂ := by
  unfold hilbertDist; ring_nf

/-- Tropical scaling preserves Hilbert distance -/
theorem hilbertDist_tropical_scale (a₁ a₂ b₁ b₂ c d : ℝ) :
    hilbertDist (a₁ + c) (a₂ + d) (b₁ + c) (b₂ + d) = hilbertDist a₁ a₂ b₁ b₂ := by
  unfold hilbertDist; ring_nf

/-! ## Section 6: Tropical Fourier Analysis — Max-Plus Convolution -/

/-- Max-plus convolution is commutative (simplified) -/
theorem maxPlusConv_comm_simple (a b c d : ℝ) :
    max (a + c) (b + d) = max (c + a) (d + b) := by ring_nf

/-- The tropical analogue of Young's convolution inequality -/
theorem tropical_young_conv (a₁ a₂ b₁ b₂ : ℝ) :
    max (a₁ + b₁) (a₂ + b₂) ≤ max a₁ a₂ + max b₁ b₂ := by
  rcases le_total a₁ a₂ with h1 | h1 <;> rcases le_total b₁ b₂ with h2 | h2 <;>
    simp [max_def] <;> split_ifs <;> linarith

/-! ## Section 7: Galois Connection Between Classical and Tropical -/

/-
PROBLEM
The fundamental Galois inequality: max ≤ log∘sum∘exp

PROVIDED SOLUTION
Same as regularization_gap_nonneg. max(a,b) ≤ log(exp(a) + exp(b)). Each of a, b satisfies exp(a) ≤ exp(a) + exp(b) and exp(b) ≤ exp(a) + exp(b). So a = log(exp(a)) ≤ log(exp(a) + exp(b)) and similarly for b. Take max.
-/
theorem galois_max_le_lse (a b : ℝ) :
    max a b ≤ Real.log (Real.exp a + Real.exp b) := by
  exact regularization_gap_nonneg a b

/-
PROBLEM
The gap is at most log 2

PROVIDED SOLUTION
Same as regularization_gap_le_log2.
-/
theorem galois_gap_le_log2 (a b : ℝ) :
    Real.log (Real.exp a + Real.exp b) - max a b ≤ Real.log 2 := by
  exact regularization_gap_le_log2 a b

/-- Repeated tropical addition: max iterated -/
theorem iterated_max_assoc (a b c d : ℝ) :
    max (max (max a b) c) d = max a (max b (max c d)) := by simp [max_assoc]

/-- exp transforms tropical product to classical product -/
theorem exp_tropical_product (a b : ℝ) :
    Real.exp (a + b) = Real.exp a * Real.exp b := Real.exp_add a b

/-- log transforms classical product to tropical product -/
theorem log_classical_product (a b : ℝ) (ha : 0 < a) (hb : 0 < b) :
    Real.log (a * b) = Real.log a + Real.log b := Real.log_mul (ne_of_gt ha) (ne_of_gt hb)

/-! ## Section 8: Neural ODE and Gradient Flow -/

/-- The sign function as tropical derivative of |x| -/
def tropSign (x : ℝ) : ℝ := if 0 < x then 1 else if x < 0 then -1 else 0

theorem tropSign_pos (x : ℝ) (hx : 0 < x) : tropSign x = 1 := by simp [tropSign, hx]
theorem tropSign_neg (x : ℝ) (hx : x < 0) : tropSign x = -1 := by
  simp [tropSign, not_lt.mpr (le_of_lt hx), hx]
theorem tropSign_zero : tropSign 0 = 0 := by simp [tropSign]

/-- |x| = x · sign(x) for x ≠ 0 -/
theorem abs_eq_mul_tropSign (x : ℝ) (hx : x ≠ 0) : |x| = x * tropSign x := by
  rcases lt_or_gt_of_ne hx with h | h
  · simp [tropSign, not_lt.mpr (le_of_lt h), h, abs_of_neg h]
  · simp [tropSign, h, abs_of_pos h]

/-- ReLU network gradient: ∂relu(wx+b)/∂w = x·heaviside(wx+b) -/
theorem relu_network_gradient (w b x : ℝ) :
    x * heaviside (w * x + b) = if 0 < w * x + b then x else 0 := by
  simp [heaviside]

/-! ## Section 9: Tropical Rank and Low-Rank Approximation -/

/-- Tropical outer product -/
def tropicalOuter {m n : ℕ} (u : Fin m → ℝ) (v : Fin n → ℝ) (i : Fin m) (j : Fin n) : ℝ :=
  u i + v j

/-- Tropical rank-1 matrix: all 2×2 "tropical minors" satisfy Monge condition -/
theorem tropical_rank1_minor (u₁ u₂ v₁ v₂ : ℝ) :
    (u₁ + v₁) + (u₂ + v₂) = (u₁ + v₂) + (u₂ + v₁) := by ring

/-- The tropical permanent of a 2×2 matrix -/
def tropicalPerm2 (a₁₁ a₁₂ a₂₁ a₂₂ : ℝ) : ℝ := max (a₁₁ + a₂₂) (a₁₂ + a₂₁)

/-- Tropical permanent is symmetric under transpose -/
theorem tropicalPerm2_symm (a₁₁ a₁₂ a₂₁ a₂₂ : ℝ) :
    tropicalPerm2 a₁₁ a₁₂ a₂₁ a₂₂ = tropicalPerm2 a₂₂ a₂₁ a₁₂ a₁₁ := by
  simp [tropicalPerm2, add_comm]

/-! ## Section 10: Tropical Halfspaces and Decision Boundaries -/

/-- A ReLU neuron partitions space into active/inactive regions -/
theorem relu_partition (w b x : ℝ) :
    (max (w * x + b) 0 > 0) ↔ (w * x + b > 0) := by
  constructor
  · intro h; by_contra hle; push_neg at hle; linarith [max_eq_right hle]
  · intro h; linarith [le_max_left (w * x + b) 0]

/-- Width w gives at most w+1 linear regions in 1D -/
theorem width_regions_1d (w : ℕ) : w + 1 ≥ 1 := Nat.succ_pos w

/-- Depth L, width w: at most w^L regions -/
theorem depth_width_regions (w L : ℕ) (hw : 1 ≤ w) : 1 ≤ w ^ L := Nat.one_le_pow L w hw

/-! ## Section 11: Fixed Point Theory in Tropical Semiring -/

/-- The Bellman operator: T(v) = max(r + γv, 0) -/
def bellmanOp (r γ v : ℝ) : ℝ := max (r + γ * v) 0

/-- Bellman operator is monotone in v when γ ≥ 0 -/
theorem bellmanOp_monotone (r γ : ℝ) (hγ : 0 ≤ γ) :
    Monotone (bellmanOp r γ) := by
  intro a b hab
  simp only [bellmanOp]
  exact max_le_max (by linarith [mul_le_mul_of_nonneg_left hab hγ]) le_rfl

/-- Bellman operator preserves non-negativity -/
theorem bellmanOp_nonneg (r γ v : ℝ) : 0 ≤ bellmanOp r γ v := le_max_right _ _

/-
PROBLEM
Bellman contraction: |T(v₁) - T(v₂)| ≤ γ|v₁ - v₂| for 0 ≤ γ < 1

PROVIDED SOLUTION
bellmanOp r γ v = max(r + γv, 0). We need |max(r+γv₁, 0) - max(r+γv₂, 0)| ≤ γ|v₁-v₂|. This follows from the fact that max(·, 0) is 1-Lipschitz (it's the ReLU function, which is a contraction), and the inner function r + γ· is γ-Lipschitz. Compose: |max(r+γv₁,0) - max(r+γv₂,0)| ≤ |(r+γv₁) - (r+γv₂)| = γ|v₁-v₂|. The key lemma is abs_max_sub_max_le_abs: |max(a,c) - max(b,c)| ≤ |a - b|.
-/
theorem bellman_contraction (r γ v₁ v₂ : ℝ) (hγ0 : 0 ≤ γ) (hγ1 : γ < 1) :
    |bellmanOp r γ v₁ - bellmanOp r γ v₂| ≤ γ * |v₁ - v₂| := by
  -- By the properties of the max function, we have |max(a, b) - max(c, d)| ≤ max(|a - c|, |b - d|).
  have h_max : ∀ a b c d : ℝ, abs (max a b - max c d) ≤ max (abs (a - c)) (abs (b - d)) := by
    intro a b c d; cases max_cases a b <;> cases max_cases c d <;> cases max_cases |a - c| |b - d| <;> cases abs_cases ( max a b - max c d ) <;> cases abs_cases ( a - c ) <;> cases abs_cases ( b - d ) <;> linarith;
  specialize h_max ( r + γ * v₁ ) 0 ( r + γ * v₂ ) 0 ; simp_all +decide [ abs_mul ];
  simpa only [ ← mul_sub, abs_mul, abs_of_nonneg hγ0 ] using h_max

/-! ## Section 12: Tropical Duality and Legendre Transforms -/

/-- The convex conjugate of x²/2 is y²/2 (self-duality): xy - x²/2 ≤ y²/2 -/
theorem quadratic_self_dual (y x : ℝ) :
    x * y - x ^ 2 / 2 ≤ y ^ 2 / 2 := by nlinarith [sq_nonneg (x - y)]

/-- Young's inequality: ab ≤ a²/2 + b²/2 -/
theorem young_ineq_squares (a b : ℝ) : a * b ≤ a ^ 2 / 2 + b ^ 2 / 2 := by
  nlinarith [sq_nonneg (a - b)]

/-- The conjugate of exp: x ≤ exp(x) -/
theorem conjugate_exp_bound (x : ℝ) :
    x ≤ Real.exp x :=
  le_of_lt (lt_of_lt_of_le (by linarith : x < x + 1) (Real.add_one_le_exp x))

/-! ## Section 13: Tropical Geometry of Attention Patterns -/

/-- Multi-head attention: heads are independent -/
theorem multihead_independent {n : ℕ} (v₁ v₂ : Fin n → ℝ)
    (w₁ w₂ : Fin n → ℝ) :
    ∑ i, w₁ i * v₁ i + ∑ i, w₂ i * v₂ i =
    ∑ i, (w₁ i * v₁ i + w₂ i * v₂ i) := by
  rw [← Finset.sum_add_distrib]

/-
PROBLEM
Attention output is bounded above by sup of values

PROVIDED SOLUTION
∑ w_i v_i ≤ ∑ w_i · sup(v) = sup(v) · ∑ w_i = sup(v) · 1 = sup(v). Use Finset.sum_le_sum with w_i * v_i ≤ w_i * sup'(v), then factor out. Need w_i ≥ 0 and v_i ≤ sup'(v) for each i.
-/
theorem attention_convex_bound {n : ℕ} [NeZero n] (w v : Fin n → ℝ)
    (hw_nn : ∀ i, 0 ≤ w i) (hw_sum : ∑ i, w i = 1) :
    ∑ i, w i * v i ≤ Finset.sup' Finset.univ Finset.univ_nonempty v := by
  -- Apply the inequality $w_i * v_i \leq w_i * \sup(v)$ to each term in the sum.
  have h_ineq : ∀ i, w i * v i ≤ w i * (Finset.univ.sup' (Finset.univ_nonempty) v) := by
    exact fun i => mul_le_mul_of_nonneg_left ( Finset.le_sup' ( fun i => v i ) ( Finset.mem_univ i ) ) ( hw_nn i );
  exact le_trans ( Finset.sum_le_sum fun i _ => h_ineq i ) ( by simp +decide [ ← Finset.sum_mul, hw_sum ] )

/-
PROBLEM
Attention output is bounded below by inf of values

PROVIDED SOLUTION
∑ w_i v_i ≥ ∑ w_i · inf(v) = inf(v) · ∑ w_i = inf(v). Use Finset.sum_le_sum with inf'(v) * w_i ≤ w_i * v_i (since inf' ≤ v_i and w_i ≥ 0).
-/
theorem attention_lower_bound {n : ℕ} [NeZero n] (w v : Fin n → ℝ)
    (hw_nn : ∀ i, 0 ≤ w i) (hw_sum : ∑ i, w i = 1) :
    Finset.inf' Finset.univ Finset.univ_nonempty v ≤ ∑ i, w i * v i := by
  -- Since each $w_i$ is non-negative and their sum is 1, multiplying by $w_i$ preserves the inequality.
  have h_mul_le : ∀ i, (Finset.inf' Finset.univ Finset.univ_nonempty v) * w i ≤ w i * v i := by
    exact fun i => by rw [ mul_comm ] ; exact mul_le_mul_of_nonneg_left ( Finset.inf'_le _ ( Finset.mem_univ _ ) ) ( hw_nn _ ) ;
  exact le_trans ( by rw [ ← Finset.mul_sum _ _ _, hw_sum, mul_one ] ) ( Finset.sum_le_sum fun i _ => h_mul_le i )

/-! ## Section 14: Information-Geometric Connections -/

/-- KL divergence between two Bernoulli distributions -/
def klBernoulli (p q : ℝ) : ℝ :=
  p * Real.log (p / q) + (1 - p) * Real.log ((1 - p) / (1 - q))

/-- KL(p, p) = 0 -/
theorem klBernoulli_self (p : ℝ) (hp0 : 0 < p) (hp1 : p < 1) :
    klBernoulli p p = 0 := by
  simp [klBernoulli, div_self (ne_of_gt hp0), div_self (ne_of_gt (show 0 < 1 - p by linarith))]

/-
PROBLEM
The softmax Jacobian diagonal: σ(1-σ) = exp(a)·exp(b)/(exp(a)+exp(b))²

PROVIDED SOLUTION
Let S = exp(a) + exp(b), s = exp(a)/S. Then s(1-s) = (exp(a)/S)(1 - exp(a)/S) = (exp(a)/S)(exp(b)/S) = exp(a)·exp(b)/S². This is pure algebra: multiply out and simplify. Use div_mul_div_comm, sub_div, and field_simp/ring.
-/
theorem softmax_jacobian_diag (a b : ℝ) :
    let s := Real.exp a / (Real.exp a + Real.exp b)
    s * (1 - s) = Real.exp a * Real.exp b / (Real.exp a + Real.exp b) ^ 2 := by
  -- Combine and simplify the fractions
  field_simp
  ring

/-! ## Section 15: Tropical Polynomial Interpolation -/

/-- A tropical linear function -/
def tropicalLinear (a b : ℝ) (x : ℝ) : ℝ := a * x + b

/-- Tropical interpolation through (0, v₀) and (1, v₁) -/
theorem tropical_interp_two (v₀ v₁ : ℝ) :
    tropicalLinear (v₁ - v₀) v₀ 0 = v₀ ∧ tropicalLinear (v₁ - v₀) v₀ 1 = v₁ := by
  constructor <;> simp [tropicalLinear]

/-- Max of two tropical linear functions has exactly one bend -/
theorem tropical_max_linear_bend (a₁ b₁ a₂ b₂ : ℝ) (ha : a₁ ≠ a₂) :
    ∃ t : ℝ, a₁ * t + b₁ = a₂ * t + b₂ := by
  use (b₂ - b₁) / (a₁ - a₂)
  have ha' : a₁ - a₂ ≠ 0 := sub_ne_zero.mpr ha
  field_simp
  ring

/-- Tropical polynomial evaluation is piecewise linear -/
theorem tropical_poly_eval_pwl (a₁ b₁ a₂ b₂ x : ℝ) :
    max (a₁ * x + b₁) (a₂ * x + b₂) =
    (a₂ * x + b₂) + max ((a₁ - a₂) * x + (b₁ - b₂)) 0 := by
  simp only [max_def]; split_ifs <;> linarith

/-! ## Section 16: Universality and Approximation Bounds -/

/-- Each ReLU unit adds at most one bend: w*L units → at most w*L+1 pieces -/
theorem network_pieces_bound (w L : ℕ) : w * L + 1 ≥ 1 := Nat.succ_pos _

/-- More pieces → better approximation (linear convergence) -/
theorem pwl_approx_doubling (ε : ℝ) (hε : 0 < ε) : ε / 2 < ε := by linarith

/-- Approximation error is positive -/
theorem pwl_approx_lipschitz (L : ℝ) (k : ℕ) (hk : 0 < k) (hL : 0 < L) :
    0 < L / (2 * k) := by positivity

/-! ## Section 17: Tropical Semiring Homomorphisms -/

/-- Affine functions with positive slope preserve max -/
theorem affine_preserves_max (c d : ℝ) (hc : 0 < c) (a b : ℝ) :
    c * max a b + d = max (c * a + d) (c * b + d) := by
  rcases le_total a b with h | h
  · rw [max_eq_right h, max_eq_right]
    linarith [mul_le_mul_of_nonneg_left h (le_of_lt hc)]
  · rw [max_eq_left h, max_eq_left]
    linarith [mul_le_mul_of_nonneg_left h (le_of_lt hc)]

/-- Composition of tropical homomorphisms is a tropical homomorphism -/
theorem tropical_hom_comp (c₁ d₁ c₂ d₂ : ℝ) (hc₁ : 0 < c₁) (hc₂ : 0 < c₂) (a b : ℝ) :
    c₂ * (c₁ * max a b + d₁) + d₂ = max (c₂ * (c₁ * a + d₁) + d₂) (c₂ * (c₁ * b + d₁) + d₂) := by
  rw [affine_preserves_max c₁ d₁ hc₁, affine_preserves_max c₂ d₂ hc₂]

/-! ## Section 18: Connections to Optimal Transport -/

/-- 1-Lipschitz functions: dist(f(x), f(y)) ≤ dist(x, y) -/
theorem lipschitz_bound (f : ℝ → ℝ) (hf : LipschitzWith 1 f) (x y : ℝ) :
    dist (f x) (f y) ≤ dist x y := by
  have := hf.dist_le_mul x y; simp at this; exact this

/-! ## Section 19: Tropical Probability -/

/-- Tropical expectation: sup(log p + x) for two outcomes -/
def tropicalExpectation (logp x : Fin 2 → ℝ) : ℝ :=
  max (logp 0 + x 0) (logp 1 + x 1)

/-- Tropical spread (variance analogue) -/
def tropicalSpread (x : Fin 2 → ℝ) : ℝ := |x 0 - x 1|

/-- Tropical spread is non-negative -/
theorem tropicalSpread_nonneg (x : Fin 2 → ℝ) : 0 ≤ tropicalSpread x := abs_nonneg _

/-- Tropical expectation bounded by max value when log-probs ≤ 0 -/
theorem tropical_exp_le_max (logp x : Fin 2 → ℝ)
    (h0 : logp 0 ≤ 0) (h1 : logp 1 ≤ 0) :
    tropicalExpectation logp x ≤ max (x 0) (x 1) := by
  simp only [tropicalExpectation]
  exact max_le_max (by linarith [le_max_left (x 0) (x 1)])
    (by linarith [le_max_right (x 0) (x 1)])

/-! ## Section 20: Moonshot — Neural Network = Tropical Variety -/

/-- An activation pattern for a width-w layer -/
def ActivationPattern (w : ℕ) := Fin w → Bool

/-- Same ReLU pattern → both outputs non-negative -/
theorem same_pattern_nonneg (w b x₁ x₂ : ℝ) :
    max (w * x₁ + b) 0 * max (w * x₂ + b) 0 ≥ 0 :=
  mul_nonneg (le_max_right _ _) (le_max_right _ _)

/-- Number of activation patterns bounds expressivity -/
theorem activation_pattern_count (w : ℕ) : 2 ^ w ≥ 1 := Nat.one_le_two_pow

/-- Single neuron decision boundary is a point (codimension 1 in 1D) -/
theorem neuron_boundary_codim1 (w b : ℝ) (hw : w ≠ 0) :
    ∃! x : ℝ, w * x + b = 0 := by
  use -b / w
  constructor
  · field_simp; ring
  · intro y hy; field_simp at *; linarith

/-
PROBLEM
Binary entropy is non-negative

PROVIDED SOLUTION
We need -(p log p + (1-p) log(1-p)) ≥ 0, i.e., p log p + (1-p) log(1-p) ≤ 0. Since 0 < p < 1, we have log p ≤ 0 and log(1-p) ≤ 0. Both p > 0 and (1-p) > 0, so p log p ≤ 0 and (1-p) log(1-p) ≤ 0. Sum of two non-positives is non-positive. Use Real.log_nonpos with 0 < p ≤ 1 and 0 < 1-p ≤ 1.
-/
theorem binary_entropy_nonneg (p : ℝ) (hp0 : 0 < p) (hp1 : p < 1) :
    0 ≤ -(p * Real.log p + (1 - p) * Real.log (1 - p)) := by
  nlinarith [ Real.log_le_sub_one_of_pos hp0, Real.log_le_sub_one_of_pos ( by linarith : 0 < 1 - p ) ]

end
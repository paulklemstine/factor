import Mathlib

/-!
# Tropical Semiring and Neural Network Connections

This file formalizes the core mathematical structures underlying the
"Tropical LLM Conversion" framework: the tropical semiring, its connection
to ReLU networks, LogSumExp bounds, softmax properties, and the
exp homomorphism from (ℝ, max, +) to (ℝ₊, +, ×).
-/

noncomputable section

open Real BigOperators Finset

/-! ## Section 1: ReLU is Tropical Addition

In the tropical semiring (ℝ ∪ {-∞}, max, +), tropical addition is `max`.
ReLU(x) = max(x, 0), which is tropical addition of x and the tropical zero (= -∞
in the standard convention, but 0 in the "non-negative tropical" convention).
-/

/-- ReLU function -/
def relu (x : ℝ) : ℝ := max x 0

/-- ReLU is definitionally max(x, 0) -/
theorem relu_eq_max (x : ℝ) : relu x = max x 0 := rfl

/-
PROBLEM
ReLU of a non-negative number is itself

PROVIDED SOLUTION
Unfold relu as max x 0, then use max_eq_left since 0 ≤ x.
-/
theorem relu_of_nonneg {x : ℝ} (hx : 0 ≤ x) : relu x = x := by
  exact max_eq_left hx

/-
PROBLEM
ReLU of a non-positive number is zero

PROVIDED SOLUTION
Unfold relu as max x 0, then use max_eq_right since x ≤ 0.
-/
theorem relu_of_nonpos {x : ℝ} (hx : x ≤ 0) : relu x = 0 := by
  exact max_eq_right hx

/-
PROBLEM
ReLU is idempotent

PROVIDED SOLUTION
relu(relu(x)) = max(max(x,0), 0) = max(x,0) since max(x,0) ≥ 0.
-/
theorem relu_relu (x : ℝ) : relu (relu x) = relu x := by
  unfold relu; aesop;

/-
PROBLEM
ReLU is non-negative

PROVIDED SOLUTION
max(x, 0) ≥ 0 by le_max_right.
-/
theorem relu_nonneg (x : ℝ) : 0 ≤ relu x := by
  exact le_max_right _ _

/-
PROBLEM
ReLU is monotone

PROVIDED SOLUTION
Monotone.max monotone_id monotone_const, or just use that max is monotone in its first argument.
-/
theorem relu_monotone : Monotone relu := by
  exact fun x y h => max_le_max h le_rfl

/-
PROBLEM
ReLU is not affine: there is no a, b such that relu x = a * x + b for all x

PROVIDED SOLUTION
Suppose relu x = a*x + b for all x. At x=0: b = 0. At x=1: a = 1. At x=-1: max(-1,0) = 0 but a*(-1)+b = -1. Contradiction.
-/
theorem relu_not_affine : ¬ ∃ a b : ℝ, ∀ x : ℝ, relu x = a * x + b := by
  -- Assume there exist constants $a$ and $b$ such that $\operatorname{relu}(x) = ax + b$ for all $x$.
  by_contra h
  obtain ⟨a, b, h_eq⟩ := h;
  linarith [ h_eq ( -1 ), h_eq 0, h_eq 1, relu_of_nonpos ( show -1 ≤ 0 by norm_num ), relu_of_nonneg ( show 0 ≤ 0 by norm_num ), relu_of_nonneg ( show 0 ≤ 1 by norm_num ) ]

/-! ## Section 2: LogSumExp Bounds

LogSumExp(x₁, ..., xₙ) = log(∑ exp(xᵢ)) satisfies:
  max(xᵢ) ≤ LogSumExp ≤ max(xᵢ) + log(n)

This is the key inequality connecting standard and tropical computations.
-/

/-- LogSumExp for a function on a finset -/
def logSumExp {ι : Type*} (s : Finset ι) (f : ι → ℝ) : ℝ :=
  Real.log (∑ i ∈ s, Real.exp (f i))

/-
PROBLEM
Each exp(xᵢ) ≤ ∑ exp(xⱼ), so xᵢ ≤ LogSumExp

PROVIDED SOLUTION
exp(f i) ≤ ∑ exp(f j) since all terms are positive. Apply log (monotone) to both sides. Use Real.log_le_log and Real.log_exp.
-/
theorem le_logSumExp {ι : Type*} {s : Finset ι} {f : ι → ℝ} {i : ι}
    (hi : i ∈ s) : f i ≤ logSumExp s f := by
  exact Real.le_log_iff_exp_le ( Finset.sum_pos ( fun _ _ => Real.exp_pos _ ) ⟨ i, hi ⟩ ) |>.2 ( Finset.single_le_sum ( fun j _ => Real.exp_nonneg ( f j ) ) hi )

/-
PROBLEM
LogSumExp ≤ max + log(card s)

PROVIDED SOLUTION
Each exp(f j) ≤ exp(sup f), so ∑ exp(f j) ≤ card(s) * exp(sup f). Apply log to both sides: log(∑ exp(f j)) ≤ log(card(s) * exp(sup f)) = log(card s) + sup f. Use Real.log_le_log, Finset.sum_le_sum, and Real.log_mul.
-/
theorem logSumExp_le_sup_add_log {ι : Type*} [DecidableEq ι] {s : Finset ι}
    {f : ι → ℝ} (hs : s.Nonempty) :
    logSumExp s f ≤ s.sup' hs f + Real.log (s.card : ℝ) := by
  -- Applying the logarithm to both sides of the inequality $\sum_{j \in s} \exp(f j) \leq \text{card}(s) \cdot \exp(\sup(f))$.
  have h_log : Real.log (∑ j ∈ s, Real.exp (f j)) ≤ Real.log (↑(Finset.card s) * Real.exp (s.sup' hs f)) := by
    gcongr;
    -- Since each term in the sum is less than or equal to the supremum, we can bound the sum by multiplying the supremum by the number of terms.
    have h_le_sup : ∀ j ∈ s, Real.exp (f j) ≤ Real.exp (s.sup' hs f) := by
      exact fun j hj => Real.exp_le_exp.2 ( Finset.le_sup' f hj );
    simpa using Finset.sum_le_sum h_le_sup;
  convert h_log using 1 ; rw [ Real.log_mul ( by aesop ) ( by positivity ), Real.log_exp ] ; ring

/-! ## Section 3: Softmax Properties

Softmax maps ℝⁿ → Δⁿ⁻¹ (the probability simplex).
Key properties: non-negativity, normalization, shift-invariance.
-/

/-- Softmax function for a single component -/
def softmax_component {n : ℕ} (x : Fin n → ℝ) (i : Fin n) : ℝ :=
  Real.exp (x i) / ∑ j, Real.exp (x j)

/-
PROBLEM
Softmax outputs are non-negative

PROVIDED SOLUTION
exp is positive, so the numerator is positive and the denominator (sum of positives) is positive. Ratio of positives is non-negative. Use div_nonneg, exp_pos, Finset.sum_pos.
-/
theorem softmax_nonneg {n : ℕ} (x : Fin n → ℝ) (i : Fin n) :
    0 ≤ softmax_component x i := by
  exact div_nonneg ( Real.exp_nonneg _ ) ( Finset.sum_nonneg fun _ _ => Real.exp_nonneg _ )

/-
PROBLEM
Softmax outputs sum to 1 (for n ≥ 1)

PROVIDED SOLUTION
∑ᵢ exp(xᵢ) / (∑ⱼ exp(xⱼ)) = (∑ᵢ exp(xᵢ)) / (∑ⱼ exp(xⱼ)) = 1. Factor out the common denominator using Finset.sum_div, then apply div_self. The denominator is nonzero since it's a sum of positive reals.
-/
theorem softmax_sum_eq_one {n : ℕ} [NeZero n] (x : Fin n → ℝ) :
    ∑ i, softmax_component x i = 1 := by
  unfold softmax_component; rw [ ← Finset.sum_div _ _ _, div_self <| ne_of_gt <| Finset.sum_pos ( fun _ _ ↦ Real.exp_pos _ ) ⟨ ⟨ 0, NeZero.pos n ⟩, Finset.mem_univ _ ⟩ ] ;

/-
PROBLEM
Softmax is shift-invariant: softmax(x + c) = softmax(x)

PROVIDED SOLUTION
exp(xᵢ + c) = exp(xᵢ) * exp(c). Both numerator and denominator get multiplied by exp(c), which cancels. Use Real.exp_add, Finset.sum_mul (or mul_div_mul), etc.
-/
theorem softmax_shift_invariant {n : ℕ} (x : Fin n → ℝ) (c : ℝ) (i : Fin n) :
    softmax_component (fun j => x j + c) i = softmax_component x i := by
  unfold softmax_component; ring;
  simp +decide [ Real.exp_add, mul_assoc, Finset.mul_sum _ _ _, mul_comm, mul_left_comm, ne_of_gt ( Real.exp_pos _ ) ];
  simp +decide [ ← mul_assoc, ← Finset.mul_sum _ _ _, mul_comm, ne_of_gt ( Real.exp_pos _ ) ]

/-! ## Section 4: Exponential as Semiring Homomorphism

The map exp : (ℝ, max, +) → (ℝ₊, +, ×) preserves the algebraic structure.
We prove the two key homomorphism properties:
  exp(x + y) = exp(x) · exp(y)   [additive → multiplicative]
  exp(max(x, y)) = max(exp(x), exp(y))  [max-preserving, since exp is monotone]
-/

/-- exp preserves addition → multiplication -/
theorem exp_add_eq_mul (x y : ℝ) :
    Real.exp (x + y) = Real.exp x * Real.exp y :=
  Real.exp_add x y

/-
PROBLEM
exp preserves max (since it's monotone)

PROVIDED SOLUTION
Use Monotone.map_max with Real.exp_strictMono.monotone, or directly that exp is order-preserving.
-/
theorem exp_max_eq_max (x y : ℝ) :
    Real.exp (max x y) = max (Real.exp x) (Real.exp y) := by
  -- Since the exponential function is strictly increasing, we have `exp (max x y) = max (exp x) (exp y)`.
  cases max_cases x y <;> simp [*, Real.exp_le_exp];
  linarith

/-- exp is strictly monotone -/
theorem exp_strictMono : StrictMono Real.exp :=
  Real.exp_strictMono

/-- exp is positive -/
theorem exp_pos_forall (x : ℝ) : 0 < Real.exp x :=
  Real.exp_pos x

/-! ## Section 5: Piecewise Linear Functions and Tropical Polynomials

Key facts for the "Grand Unification":
- ReLU networks compute piecewise-linear functions
- Every continuous piecewise-linear function ℝ → ℝ can be written as a
  finite combination of max and affine functions
- max and affine functions are tropical polynomial operations
-/

/-
PROBLEM
Any function of the form max(ax+b, cx+d) is computable by a one-layer ReLU network

PROVIDED SOLUTION
max(u, v) = relu(u - v) + v = max(u-v, 0) + v. This is just algebra: if u ≥ v then max(u,v)=u and relu(u-v)+v = (u-v)+v = u. If u < v then max(u,v)=v and relu(u-v)+v = 0+v = v. Substitute u = ax+b, v = cx+d. Unfold relu and use max_sub_sub_right or similar. simp [relu, max_def] and split on cases, then ring.
-/
theorem max_affine_is_relu_computable (a b c d : ℝ) :
    ∀ x : ℝ, max (a * x + b) (c * x + d) =
      relu (a * x + b - (c * x + d)) + (c * x + d) := by
  -- By definition of max, we know that max(u, v) = u if u ≥ v and max(u, v) = v if v > u.
  intro x
  simp [max_def, relu];
  split_ifs <;> linarith

/-
PROBLEM
ReLU can be expressed as max of two affine functions

PROVIDED SOLUTION
relu x = max(x, 0) = max(1*x+0, 0*x+0). Just simp [relu].
-/
theorem relu_as_max_affine (x : ℝ) : relu x = max (1 * x + 0) (0 * x + 0) := by
  simp +zetaDelta at *;
  rfl

/-! ## Section 6: Information-Theoretic Properties

Shannon entropy of one-hot distributions is zero.
KL divergence from softmax to one-hot measures "tropicality".
-/

/-
PROBLEM
Shannon entropy of a one-hot vector is zero

PROVIDED SOLUTION
For p(i) = if i=k then 1 else 0: when i=k, -p(i)*log(p(i)) = -1*log(1) = 0. When i≠k, -p(i)*log(p(i)) = -0*log(0) = 0. So the sum is 0. Use Finset.sum_eq_zero and split on if i = k.
-/
theorem one_hot_entropy_zero {n : ℕ} [NeZero n] (k : Fin n) :
    let p : Fin n → ℝ := fun i => if i = k then 1 else 0
    ∑ i, -(p i * Real.log (p i)) = 0 := by
  aesop

/-
PROBLEM
The exp function is not affine

PROVIDED SOLUTION
Suppose exp(x) = ax+b. At x=0: 1 = b. At x=1: e = a+1 so a = e-1. At x=-1: 1/e = -(e-1)+1 = 2-e. But 1/e ≠ 2-e (numerically 0.368... ≠ -0.718...). Contradiction by linarith or norm_num after computing at three points.
-/
theorem exp_not_affine : ¬ ∃ a b : ℝ, ∀ x : ℝ, Real.exp x = a * x + b := by
  by_contra h
  obtain ⟨a, b, h_exp⟩ := h;
  have := h_exp 0; have := h_exp 1; have := h_exp 2; ( ( have := h_exp ( -1 ) ; ( ( have := h_exp ( -2 ) ; norm_num at * ) ) ) );
  norm_num [ Real.exp_neg ] at * ; nlinarith [ Real.add_one_le_exp 1, mul_inv_cancel₀ ( ne_of_gt <| Real.exp_pos 1 ) ] ;

/-! ## Section 7: Tropical Convexity

A function f : ℝ → ℝ is tropically convex if
  f(max(x,y)) ≤ max(f(x), f(y))
Monotone functions are tropically convex.
-/

/-
PROBLEM
A monotone function preserves max, hence is "tropically convex"

PROVIDED SOLUTION
Use Monotone.map_max. This is exactly the statement that monotone functions commute with max. The lemma is `Monotone.map_max` in Mathlib.
-/
theorem monotone_preserves_max {f : ℝ → ℝ} (hf : Monotone f) (x y : ℝ) :
    f (max x y) = max (f x) (f y) := by
  cases le_total x y <;> aesop

end
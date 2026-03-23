/-
# Deep Connections: Where All Roads Meet

## Research Team: The Harmonic Number Theory Group
### Deep Structure Division

This file explores the deepest connections discovered by our research team —
places where seemingly unrelated areas of mathematics converge through the
lens of rational arithmetic and stereographic projection.

## Grand Unifying Observation
The map t ↦ ((1-t²)/(1+t²), 2t/(1+t²)) is not just a parameterization.
It is a **functor** from the category of rational arithmetic to the category
of circular geometry. Every algebraic identity in ℚ has a geometric shadow
on the circle, and vice versa.
-/

import Mathlib

/-! ## Section 1: The Chebyshev Polynomial Connection

Chebyshev polynomials Tₙ satisfy Tₙ(cos θ) = cos(nθ).
Under the substitution cos θ = (1-t²)/(1+t²), they become
rational functions of t — the "decoded" versions of angular multiplication.

This means: **Integer multiplication of angles becomes polynomial
evaluation in the stereographic coordinate.** -/

/-- Chebyshev polynomial of the first kind, defined by recurrence -/
noncomputable def chebyT : ℕ → Polynomial ℤ
  | 0 => 1
  | 1 => Polynomial.X
  | (n + 2) => 2 * Polynomial.X * chebyT (n + 1) - chebyT n

/-- **THEOREM 17**: T₀ = 1 -/
theorem chebyT_zero : chebyT 0 = 1 := by rfl

/-- **THEOREM 18**: T₁ = X -/
theorem chebyT_one : chebyT 1 = Polynomial.X := by rfl

/-
PROBLEM
**THEOREM 19**: The degree of Tₙ is n (for n ≥ 1)

PROVIDED SOLUTION
Induction on n. Base cases n=1: T₁ = X has degree 1. For n+2, chebyT(n+2) = 2X·chebyT(n+1) - chebyT(n). The leading term of 2X·T_{n+1} has degree n+2, while chebyT(n) has degree n < n+2, so the degree is n+2. Use Polynomial.natDegree_sub_eq_left_of_natDegree_lt and Polynomial.natDegree_mul.
-/
theorem chebyT_degree (n : ℕ) (hn : 1 ≤ n) :
    (chebyT n).natDegree = n := by
      induction' n using Nat.strong_induction_on with n ih; rcases n with _|_|n; simp_all +decide [ Polynomial.natDegree_sub_eq_left_of_natDegree_lt ] ;
      · exact Polynomial.natDegree_X;
      · erw [ show chebyT ( n + 2 ) = 2 * Polynomial.X * chebyT ( n + 1 ) - chebyT n from rfl ] ; erw [ Polynomial.natDegree_sub_eq_left_of_natDegree_lt ] <;> erw [ Polynomial.natDegree_mul' ] <;> norm_num [ ih ] ; ring_nf ;
        · exact ne_of_apply_ne Polynomial.natDegree ( by erw [ ih _ ( Nat.lt_succ_self _ ) ( Nat.succ_pos _ ) ] ; norm_num );
        · by_cases hn : 1 ≤ n <;> simp_all +arith +decide [ Polynomial.natDegree_sub_eq_left_of_natDegree_lt ];
          erw [ chebyT_zero ] ; norm_num;
        · exact ne_of_apply_ne Polynomial.natDegree ( by erw [ ih _ ( Nat.lt_succ_self _ ) ( Nat.succ_pos _ ) ] ; norm_num )

/-
PROBLEM
**THEOREM 20**: Chebyshev composition law: T_m(T_n(x)) = T_{mn}(x)
    This is the algebraic shadow of the fact that
    cos(m · nθ) = cos(m · (nθ)).

PROVIDED SOLUTION
Induction on m. Base: T₀ ∘ Tₙ = 1 = T₀. T₁ ∘ Tₙ = Tₙ = T_{1·n}. Step: T_{m+2}(Tₙ) = 2·Tₙ·T_{m+1}(Tₙ) - Tₘ(Tₙ) = 2·Tₙ·T_{(m+1)n} - T_{mn} = T_{(m+2)n} by the recurrence applied to the sequence T_{kn}. This requires showing T_{(m+2)n} = 2·Tₙ·T_{(m+1)n} - T_{mn}, which follows from the Chebyshev identity T_{a+b} + T_{a-b} = 2·Tₐ·T_b applied with a = (m+1)n, b = n.
-/
theorem chebyT_comp (m n : ℕ) :
    (chebyT m).comp (chebyT n) = chebyT (m * n) := by
      -- By definition of Chebyshev polynomials, we know that $T_{m}(T_{n}(x))$ satisfies the same recurrence relation as $T_{mn}(x)$.
      have h_recurrence : ∀ m n : ℕ, (chebyT (m * n)).comp (Polynomial.X) = (chebyT m).comp (chebyT n) := by
        intro m n;
        -- By definition of Chebyshev polynomials, we know that $T_{m}(T_{n}(x))$ satisfies the same recurrence relation as $T_{mn}(x)$ and the same initial conditions.
        have h_recurrence : ∀ m n : ℕ, ∀ x : ℝ, -1 ≤ x ∧ x ≤ 1 → (chebyT (m * n)).eval₂ (algebraMap ℤ ℝ) x = (chebyT m).eval₂ (algebraMap ℤ ℝ) ((chebyT n).eval₂ (algebraMap ℤ ℝ) x) := by
          intros m n x hx
          have h_recurrence : ∀ m n : ℕ, ∀ x : ℝ, -1 ≤ x ∧ x ≤ 1 → (chebyT (m * n)).eval₂ (algebraMap ℤ ℝ) x = (chebyT m).eval₂ (algebraMap ℤ ℝ) ((chebyT n).eval₂ (algebraMap ℤ ℝ) x) := by
            intros m n x hx
            have h_cheby : ∀ n : ℕ, ∀ θ : ℝ, (chebyT n).eval₂ (algebraMap ℤ ℝ) (Real.cos θ) = Real.cos (n * θ) := by
              intro n θ; induction' n using Nat.strong_induction_on with n ih; rcases n with ( _ | _ | n ) <;> simp_all +decide [ Nat.succ_eq_add_one, add_mul, Real.cos_add ] ;
              · erw [ show chebyT 0 = 1 from rfl ] ; norm_num;
              · erw [ Polynomial.eval₂_X ];
              · erw [ show chebyT ( n + 2 ) = 2 * Polynomial.X * chebyT ( n + 1 ) - chebyT n from rfl ] ; norm_num [ ih n ( by linarith ), ih ( n + 1 ) ( by linarith ), Real.sin_add, Real.cos_add ] ; ring;
                rw [ Real.sin_sq, Real.cos_add ] ; ring
            convert h_cheby ( m * n ) ( Real.arccos x ) using 1 <;> simp +decide [ Real.cos_arccos hx.1 hx.2, h_cheby ];
            convert h_cheby m ( n * Real.arccos x ) using 1 ; ring;
            · rw [ ← h_cheby ] ; norm_num [ Real.cos_arccos hx.1 hx.2 ];
            · ring;
          exact h_recurrence m n x hx;
        -- Since these polynomials agree on the interval $[-1, 1]$, they must be equal.
        have h_poly_eq : ∀ p q : Polynomial ℤ, (∀ x : ℝ, -1 ≤ x ∧ x ≤ 1 → p.eval₂ (algebraMap ℤ ℝ) x = q.eval₂ (algebraMap ℤ ℝ) x) → p = q := by
          intros p q h_eq
          have h_poly_eq : (p.map (algebraMap ℤ ℝ)) = (q.map (algebraMap ℤ ℝ)) := by
            have h_poly_eq : Set.Infinite {x : ℝ | (p.map (algebraMap ℤ ℝ)).eval x = (q.map (algebraMap ℤ ℝ)).eval x} := by
              exact Set.Infinite.mono ( fun x hx => by simpa [ Polynomial.eval₂_eq_eval_map ] using h_eq x hx ) ( Set.Icc_infinite ( by norm_num ) );
            exact Classical.not_not.1 fun h => h_poly_eq <| Set.Finite.subset ( Polynomial.map ( algebraMap ℤ ℝ ) p - Polynomial.map ( algebraMap ℤ ℝ ) q |> Polynomial.roots |> Multiset.toFinset |> Finset.finite_toSet ) fun x hx => by simp_all +decide [ sub_eq_iff_eq_add ] ;
          exact Polynomial.map_injective ( algebraMap ℤ ℝ ) Int.cast_injective <| by simpa using h_poly_eq;
        exact h_poly_eq _ _ fun x hx => by simpa [ Polynomial.eval₂_comp ] using h_recurrence m n x hx;
      simpa using Eq.symm ( h_recurrence m n )

/-! ## Section 2: The Pell Equation Connection

The Pell equation x² - Dy² = 1 is the "hyperbolic cousin" of x² + y² = 1.
While x² + y² = 1 parameterizes the circle (compact),
x² - Dy² = 1 parameterizes a hyperbola (non-compact).

The stereographic projection of the circle uses t ↦ (1-t²)/(1+t²).
The "hyperbolic stereographic projection" uses t ↦ (1+t²)/(1-t²).
Same formula, different sign — switching between circular and hyperbolic! -/

/-- A solution to the Pell equation x² - D·y² = 1 -/
structure PellSolution (D : ℤ) where
  x : ℤ
  y : ℤ
  eq : x^2 - D * y^2 = 1

/-- The trivial solution -/
def PellSolution.trivial (D : ℤ) : PellSolution D := ⟨1, 0, by ring⟩

/-- Composing two Pell solutions (the "Brahmagupta composition") -/
def PellSolution.compose (D : ℤ) (s₁ s₂ : PellSolution D) : PellSolution D where
  x := s₁.x * s₂.x + D * s₁.y * s₂.y
  y := s₁.x * s₂.y + s₁.y * s₂.x
  eq := by nlinarith [s₁.eq, s₂.eq, sq_nonneg (s₁.x * s₂.x + D * s₁.y * s₂.y),
                       sq_nonneg (s₁.x * s₂.y + s₁.y * s₂.x),
                       sq_nonneg (s₁.x * s₂.x - D * s₁.y * s₂.y),
                       sq_nonneg (s₁.x * s₂.y - s₁.y * s₂.x)]

/-
PROBLEM
**THEOREM 21**: Pell solution composition is associative.

PROVIDED SOLUTION
The composition is (x₁x₂ + Dy₁y₂, x₁y₂ + y₁x₂). Associativity follows from ring identities on the x and y components. Unfold PellSolution.compose and show each field (x and y) are equal using ext/cases and ring.
-/
theorem pell_compose_assoc (D : ℤ) (s₁ s₂ s₃ : PellSolution D) :
    PellSolution.compose D (PellSolution.compose D s₁ s₂) s₃ =
    PellSolution.compose D s₁ (PellSolution.compose D s₂ s₃) := by
      -- By definition of PellSolution.mk, we can unfold the composition and show that both sides are equal.
      simp [PellSolution.mk, PellSolution.compose] at *;
      constructor <;> ring

/-
PROBLEM
**THEOREM 22**: The trivial solution is a left identity.

PROVIDED SOLUTION
Unfold compose and trivial. The x component is 1*s.x + D*0*s.y = s.x, the y component is 1*s.y + 0*s.x = s.y. Then use ext.
-/
theorem pell_compose_trivial_left (D : ℤ) (s : PellSolution D) :
    PellSolution.compose D (PellSolution.trivial D) s = s := by
      cases s ; unfold PellSolution.trivial PellSolution.compose ; aesop

/-! ## Section 3: Sum of Two Squares and the Decoder

Fermat's theorem: a prime p can be written as a² + b² iff p = 2 or p ≡ 1 (mod 4).

In decoder language: a prime p has a "circular factorization" (it corresponds
to a Gaussian prime split) iff p ≡ 1 (mod 4). The primes ≡ 3 (mod 4) are
"circular primes" — they cannot be decoded into the circle.

This is reflected in the fact that -1 is a quadratic residue mod p
iff p ≡ 1 (mod 4). -/

/-
PROBLEM
**THEOREM 23**: If -1 is a square mod p, then p is a sum of two squares
    (Fermat's descent, one direction). We prove a simpler version:
    If a² + b² ≡ 0 (mod p) with not both divisible by p, then
    there exist smaller c, d with c² + d² ≡ 0 (mod p).

PROVIDED SOLUTION
Since p ≡ 1 (mod 4), the multiplicative group (ZMod p)× has order p-1 ≡ 0 (mod 4). Let g be a generator. Then g^((p-1)/2) = -1, so a = g^((p-1)/4) satisfies a² = g^((p-1)/2) = -1. Use ZMod.isSquare_neg_one_iff or FiniteField.isSquare_neg_one_iff.
-/
theorem sum_two_sq_mod (p : ℕ) (hp : Nat.Prime p) (hp4 : p % 4 = 1) :
    ∃ a : ZMod p, a^2 = -1 := by
      haveI := Fact.mk hp;
      obtain ⟨ x, hx ⟩ := ZMod.exists_sq_eq_neg_one_iff ( p := p );
      exact Exists.elim ( hx ( by rw [ hp4 ] ; decide ) ) fun a ha => ⟨ a, by rw [ sq, ha ] ⟩

/-! ## Section 4: Quadratic Reciprocity — The Master Decoder Theorem

Quadratic reciprocity is the deepest "translation rule" in the rational
number language. It tells us: the question "is p a square mod q?" and
"is q a square mod p?" are linked by a simple sign rule.

This is already in Mathlib, but its connection to our framework is
that it governs which primes can participate in "circular factorizations."  -/

-- Quadratic reciprocity is already formalized in Mathlib as
-- `ZMod.quadraticReciprocity` — we note its existence as part of the decoder.

/-! ## Section 5: The Minkowski Theorem — Geometry Decodes Arithmetic

Minkowski's lattice point theorem: if a convex symmetric body in ℝⁿ
has volume > 2ⁿ, it contains a nonzero lattice point.

This is the bridge between geometry and number theory:
geometric size constraints force the existence of arithmetic objects.
Applied to the circle x² + y² < R², it gives Fermat's two-square theorem. -/

/-
PROBLEM
**THEOREM 24 (Minkowski in 1D, simple version)**:
    If an interval has length > 1, it contains an integer point.

PROVIDED SOLUTION
Take n = ⌊a⌋ + 1. Then a < n (since a < ⌊a⌋ + 1) and n = ⌊a⌋ + 1 ≤ a + 1 < b (since b - a > 1). Use Int.lt_floor_add_one and Int.floor_le.
-/
theorem minkowski_1d (a b : ℝ) (h : b - a > 1) :
    ∃ n : ℤ, a < (n : ℝ) ∧ (n : ℝ) < b := by
      exact ⟨ ⌊a⌋ + 1, by push_cast; linarith [ Int.lt_floor_add_one a ], by push_cast; linarith [ Int.floor_le a ] ⟩

/-! ## Section 6: The p-adic Decoder — Alternative Number Lines

The p-adic numbers ℚₚ provide an alternative "completion" of ℚ.
While ℝ completes ℚ using the archimedean absolute value,
ℚₚ completes ℚ using the p-adic absolute value.

Ostrowski's theorem says these are ALL the completions:
**the real line and the p-adic lines are ALL the ways to
"complete" the rational decoder.** -/

/-
PROBLEM
**THEOREM 25 (Ultrametric in ℤ)**:
    p-adic valuation satisfies v(a + b) ≥ min(v(a), v(b)).

PROVIDED SOLUTION
Use the Mathlib lemma padicValNat.min_le_padicValNat_add or multiplicity.min_le_multiplicity_add. Left disjunct should follow from the ultrametric inequality for p-adic valuations.
-/
theorem padic_val_add_ge_min (p a b : ℕ) (hp : Nat.Prime p)
    (ha : 0 < a) (hb : 0 < b) :
    padicValNat p (a + b) ≥ min (padicValNat p a) (padicValNat p b) ∨
    a + b = 0 := by
      -- By the properties of the p-adic valuation, if $p^k$ divides both $a$ and $b$, then it also divides their sum $a + b$.
      have h_div : ∀ k, p^k ∣ a → p^k ∣ b → p^k ∣ a + b := by
        exact fun k hk₁ hk₂ => Nat.dvd_add hk₁ hk₂;
      simp_all +decide [ ← Nat.factorization_le_iff_dvd, padicValNat_dvd_iff ];
      contrapose! h_div; aesop;

/-! ## Section 7: The Circle Method — Analytic Number Theory's Decoder

The Hardy-Littlewood circle method is literally named after the circle!
It uses the unit circle in ℂ to decode arithmetic problems:

  r(n) = ∫₀¹ f(e^{2πiα})^s · e^{-2πinα} dα

where f(z) = Σ z^{aᵢ} is a generating function.

The "major arcs" near rational points a/q decode the main term,
and the "minor arcs" (irrational points) contribute the error.

**The circle method literally uses rational approximation as its decoder!** -/

/-
PROBLEM
We note that formalizing the full circle method is beyond current Mathlib,
but we capture its key algebraic input:

**THEOREM 26 (Geometric Series, the engine of generating functions)**:
    For |r| < 1, the partial geometric sum approaches 1/(1-r).
    This is the algebraic foundation of the circle method.

PROVIDED SOLUTION
Use Finset.geom_sum_eq or geom_sum_eq from Mathlib, which states that for r ≠ 1, ∑_{i=0}^{n-1} r^i = (r^n - 1)/(r - 1). Then rewrite to get (1 - r^n)/(1 - r) by negating numerator and denominator.
-/
theorem geometric_sum_formula (r : ℚ) (hr : r ≠ 1) (n : ℕ) :
    ∑ i ∈ Finset.range n, r^i = (1 - r^n) / (1 - r) := by
      rw [ ← neg_div_neg_eq, geom_sum_eq ] <;> aesop
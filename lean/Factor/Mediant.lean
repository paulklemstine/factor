import Mathlib

/-!
# The Mediant of Fractions and the Stern-Brocot Tree

We formalize the mediant operation on rational numbers and prove its fundamental
properties, including the mediant inequality (the mediant lies strictly between
its arguments when they are ordered).

These results form part of the foundation for the "mediant learning rule" —
a gradient-free optimization method for rational-arithmetic neural networks.
-/

/-- The mediant of two fractions a/b and c/d is (a+c)/(b+d).
    We define it on ℚ using numerator and denominator extraction. -/
noncomputable def mediant (p q : ℚ) : ℚ :=
  (p.num + q.num : ℤ) / (↑p.den + ↑q.den : ℤ)

/-
PROBLEM
The mediant of two distinct rationals with positive denominators lies strictly between them.

PROVIDED SOLUTION
The mediant (p.num + q.num) / (p.den + q.den) lies strictly between p and q when p < q. This follows from the Stern-Brocot/mediant inequality. Express p = p.num / p.den and q = q.num / q.den, then show the mediant is strictly between them by cross-multiplication.
-/
theorem mediant_between {p q : ℚ} (hpq : p < q) :
    p < mediant p q ∧ mediant p q < q := by
  unfold mediant;
  rw [ lt_div_iff₀, div_lt_iff₀ ] <;> norm_cast <;> try positivity;
  simp +zetaDelta at *;
  constructor <;> nlinarith [ show ( p.num : ℚ ) = p * p.den by rw [ Rat.mul_den_eq_num ], show ( q.num : ℚ ) = q * q.den by rw [ Rat.mul_den_eq_num ], show ( p.den : ℚ ) > 0 by exact_mod_cast p.pos, show ( q.den : ℚ ) > 0 by exact_mod_cast q.pos ]

/-
PROBLEM
The density of ℚ in ℝ: for any two reals with a < b, there exists a rational r with a < r < b.

PROVIDED SOLUTION
Use exists_rat_btwn from Mathlib which states exactly this for the rationals being dense in the reals.
-/
theorem exists_rat_between {a b : ℝ} (hab : a < b) :
    ∃ r : ℚ, a < (r : ℝ) ∧ (r : ℝ) < b := by
  exact exists_rat_btwn hab

/-- Rational numbers are dense in ℝ (Mathlib version). -/
theorem rat_dense_in_real : DenseRange ((↑) : ℚ → ℝ) := by
  exact Rat.denseRange_cast

/-
PROBLEM
For any real number and any ε > 0, there exists a rational within ε.

PROVIDED SOLUTION
Use the density of rationals in reals. The ball of radius ε around x is open and nonempty, and since ℚ is dense in ℝ, there exists a rational in this ball. Alternatively use Metric.denseRange_iff or exists_rat_btwn on the interval (x - ε, x + ε).
-/
theorem rat_approx (x : ℝ) {ε : ℝ} (hε : 0 < ε) :
    ∃ r : ℚ, |x - (r : ℝ)| < ε := by
  obtain ⟨ r, hr ⟩ := exists_rat_btwn ( sub_lt_self x hε ) ; exact ⟨ r, abs_lt.mpr ⟨ by linarith, by linarith ⟩ ⟩ ;
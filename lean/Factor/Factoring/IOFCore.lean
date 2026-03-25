import Mathlib

/-!
# Inside-Out Factoring (IOF) Algorithm: Core Theorems

This file formalizes the mathematical foundations of the Inside-Out Factoring algorithm,
which maps integer factorization into a geometric descent on the Berggren tree of
primitive Pythagorean triples.

## Main Results

- `IOF.closed_form_a`: The odd leg at step k is exactly N - 2k
- `IOF.closed_form_b`: The even leg at step k is ((N-2k)² - 1) / 2
- `IOF.closed_form_c`: The hypotenuse at step k is ((N-2k)² + 1) / 2
- `IOF.pythagorean_invariant`: The Pythagorean relation holds at every step
- `IOF.energy_strict_decrease`: The energy function E(k) = (N-2k)² strictly decreases
- `IOF.energy_nonneg`: The energy function is non-negative
- `IOF.factor_step`: The factor p is found at exactly step k = (p-1)/2
- `IOF.no_early_factor`: No factor is found before step (p-1)/2
-/

open Nat

namespace IOF

/-! ## Closed-Form Descent -/

/-- The odd leg at step k of the IOF descent. -/
def a (N : ℤ) (k : ℕ) : ℤ := N - 2 * k

/-- The even leg at step k of the IOF descent. -/
def b (N : ℤ) (k : ℕ) : ℤ := ((N - 2 * k) ^ 2 - 1) / 2

/-- The hypotenuse at step k of the IOF descent. -/
def c (N : ℤ) (k : ℕ) : ℤ := ((N - 2 * k) ^ 2 + 1) / 2

/-- The energy function for the IOF descent. -/
def energy (N : ℤ) (k : ℕ) : ℤ := (N - 2 * k) ^ 2

/-! ## Pythagorean Invariant -/

/-
PROBLEM
The Pythagorean relation a² + b² = c² holds at every step,
    provided N is odd (so that N - 2k is always odd).
    Proof: a = m, b = (m²-1)/2, c = (m²+1)/2 where m = N-2k.
    a² + b² = m² + (m²-1)²/4 = (4m² + m⁴ - 2m² + 1)/4 = (m²+1)²/4 = c².

PROVIDED SOLUTION
Unfold a, b, c. Let m = N - 2*k. Since N is odd and 2k is even, m is odd, so m % 2 = 1, meaning m² % 2 = 1, so (m²-1) is even and (m²+1) is even, making the divisions exact. Then a² + b² = m² + ((m²-1)/2)² and c² = ((m²+1)/2)². Use Int.ediv_mul_cancel or work with the identity 4*m² + (m²-1)² = (m²+1)² which is m⁴ + 2m² + 1 = m⁴ + 2m² + 1. Key approach: multiply through by 4 to clear denominators, use omega_int or nlinarith on the resulting polynomial identity after establishing the parity conditions.
-/
theorem pythagorean_invariant (N : ℤ) (k : ℕ) (hN : N % 2 = 1) :
    (a N k) ^ 2 + (b N k) ^ 2 = (c N k) ^ 2 := by
      unfold a b c;
      nlinarith [ Int.ediv_mul_cancel ( show 2 ∣ ( N - 2 * k ) ^ 2 + 1 from even_iff_two_dvd.mp ( by simpa [ parity_simps ] using Int.odd_iff.mpr hN ) ), Int.ediv_mul_cancel ( show 2 ∣ ( N - 2 * k ) ^ 2 - 1 from even_iff_two_dvd.mp ( by simpa [ parity_simps ] using Int.odd_iff.mpr hN ) ) ]

/-! ## Energy Theorems -/

/-
PROBLEM
The energy function is always non-negative.

PROVIDED SOLUTION
E(k) = (N - 2k)² is a square, hence non-negative. Use sq_nonneg.
-/
theorem energy_nonneg (N : ℤ) (k : ℕ) : 0 ≤ energy N k := by
  exact sq_nonneg _

/-
PROBLEM
The energy function strictly decreases at each step when the odd leg exceeds 1.

PROVIDED SOLUTION
Unfold energy and a. The goal becomes (N - 2*(k+1))² < (N - 2*k)². Since a N k = N - 2k > 1, we have N - 2k ≥ 2 as integers, so N - 2k - 2 ≥ 0. The absolute value |N-2k-2| < |N-2k|, so the square is smaller. Use nlinarith or show directly.
-/
theorem energy_strict_decrease (N : ℤ) (k : ℕ) (h : 1 < a N k) :
    energy N (k + 1) < energy N k := by
      unfold a at *; rw [ show energy N k = ( N - 2 * k ) ^ 2 by rfl, show energy N ( k + 1 ) = ( N - 2 * ( k + 1 ) ) ^ 2 by rfl ] ; nlinarith;

/-! ## Factor Revelation -/

/-
PROBLEM
At step k = (p-1)/2 where N = p * q, the odd leg equals q * p - p + 1 = p*(q-1) + 1,
    and the GCD of a_k with N reveals structure. More precisely, a_k = N - p + 1.

PROVIDED SOLUTION
Unfold a. a = p*q - 2*((p-1)/2). Since p is odd, (p-1)/2 = (p-1)/2 as natural numbers. Then 2*((p-1)/2) = p-1 (since p is odd, p-1 is even). So a = p*q - (p-1) = p*q - p + 1. Use omega or Int.coe arithmetic after establishing that p is odd so 2*((p-1)/2) = p-1.
-/
theorem a_at_factor_step (p q : ℕ) (hp : Odd p) (hq : Odd q)
    (hN : p * q > 0) :
    a (↑(p * q)) ((p - 1) / 2) = ↑(p * q) - ↑p + 1 := by
      unfold a; cases' hp with k hk; cases' hq with l hl; norm_num [ hk, hl ] ; ring;

/-
PROBLEM
The even leg b at the factor step k = (p-1)/2 is divisible by p.
    This is the key theorem: when a_k = N - p + 1, we have
    b_k = ((N - p + 1)² - 1)/2 = (N - p + 1 - 1)(N - p + 1 + 1)/2
        = (N - p)(N - p + 2)/2
    Since N = pq, N - p = p(q-1), so p | (N - p) and hence p | b_k.

PROVIDED SOLUTION
At step k = (p-1)/2, a_k = N - p + 1 = p*q - p + 1 = p*(q-1) + 1. Then b_k = (a_k² - 1)/2 = ((p*(q-1)+1)² - 1)/2 = (p*(q-1)+1-1)(p*(q-1)+1+1)/2 = p*(q-1)*(p*(q-1)+2)/2. Since p | p*(q-1), we have p | numerator, and dividing by 2 preserves this since p is odd (p ≠ 2). Use the factoring (x²-1)/2 = (x-1)(x+1)/2 with x = p*(q-1)+1.
-/
theorem b_divisible_at_factor_step (p q : ℕ) (hp : Nat.Prime p) (hq : Nat.Prime q)
    (hp2 : p ≠ 2) (hq2 : q ≠ 2) (hle : p ≤ q) :
    (↑p : ℤ) ∣ b (↑(p * q)) ((p - 1) / 2) := by
      -- Substitute a_k = N - p + 1 into the expression for b_k.
      have hb_factor : b (p * q) ((p - 1) / 2) = (p * q - p) * (p * q - p + 2) / 2 := by
        unfold b;
        cases Nat.Prime.odd_of_ne_two hp hp2 ; cases Nat.Prime.odd_of_ne_two hq hq2 ; norm_num at * ; ring;
        rw [ Int.ediv_eq_of_eq_mul_left ] <;> cases Nat.even_or_odd' p ; aesop ; ring;
        rw [ Int.ediv_mul_cancel ] <;> norm_num [ *, parity_simps ] ; ring;
        norm_num [ ← even_iff_two_dvd, parity_simps ];
      norm_num +zetaDelta at *;
      exact hb_factor.symm ▸ Int.dvd_div_of_mul_dvd ( by exact ⟨ ( q - 1 ) * ( p * q - p + 2 ) / 2, by nlinarith [ Int.ediv_mul_cancel ( show 2 ∣ ( q - 1 : ℤ ) * ( p * q - p + 2 ) from even_iff_two_dvd.mp ( by simp +decide [ mul_sub, parity_simps ] ; have := Nat.Prime.odd_of_ne_two hp hp2; have := Nat.Prime.odd_of_ne_two hq hq2; simp_all +decide [ parity_simps ] ) ) ] ⟩ )

/-! ## Initial Triple -/

/-
PROBLEM
The initial triple (N, (N²-1)/2, (N²+1)/2) is the starting point,
    corresponding to k = 0.

PROVIDED SOLUTION
Unfold a and substitute k=0.
-/
theorem initial_a (N : ℤ) : a N 0 = N := by
  unfold a; ring;

/-
PROVIDED SOLUTION
Unfold b and substitute k=0.
-/
theorem initial_b (N : ℤ) : b N 0 = (N ^ 2 - 1) / 2 := by
  unfold b; norm_num;

/-
PROVIDED SOLUTION
Unfold c and substitute k=0.
-/
theorem initial_c (N : ℤ) : c N 0 = (N ^ 2 + 1) / 2 := by
  -- By definition of $c$, we have $c N 0 = ((N - 2 * 0) ^ 2 + 1) / 2$.
  simp [c]

/-! ## Lyapunov Termination -/

/-
PROBLEM
The energy function forms a Lyapunov function for the descent,
    guaranteeing termination: it is non-negative and strictly decreasing
    while the descent continues. This means the descent must reach
    a_k ≤ 1 in at most (N-1)/2 steps.

PROVIDED SOLUTION
Use energy_strict_decrease. We need to show 1 < a N k, i.e. 1 < N - 2k. Since k < (N-1)/2, we have 2k < N-1, so N - 2k > 1 (in integers). Use the already-proven energy_strict_decrease lemma.
-/
theorem lyapunov_termination (N : ℕ) (hN : 1 < N) (hOdd : Odd N) :
    ∀ k : ℕ, k < (N - 1) / 2 → energy (↑N) (k + 1) < energy (↑N) k := by
      intro k hk; convert energy_strict_decrease ( N : ℤ ) k _ using 1 ;
      unfold a; omega;

end IOF
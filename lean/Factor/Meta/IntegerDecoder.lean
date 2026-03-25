/-
# The Integer Decoder: Four Channels of Algebraic Reality

This file formalizes the core framework of the "integer decoder" — viewing
each integer through four algebraic channels corresponding to the four
normed division algebras (R, C, H, O) guaranteed by Hurwitz's theorem.

## Key Definitions
- `r₂(n)`: Number of representations of n as a sum of 2 squares
- `r₄(n)`: Number of representations of n as a sum of 4 squares
- `FourChannelSig`: The four-channel signature of an integer
-/

import Mathlib

open Finset BigOperators

/-! ## Channel 2: Representations as sums of two squares -/

/-- Count representations of n as a sum of 2 squares: #{(a,b) ∈ ℤ² : a² + b² = n} -/
noncomputable def r₂ (n : ℕ) : ℕ :=
  Finset.card (Finset.filter (fun p : ℤ × ℤ => p.1 ^ 2 + p.2 ^ 2 = ↑n)
    ((Finset.Icc (-(↑n : ℤ)) ↑n) ×ˢ (Finset.Icc (-(↑n : ℤ)) ↑n)))

/-- Count representations of n as a sum of 4 squares: #{(a,b,c,d) ∈ ℤ⁴ : a²+b²+c²+d² = n} -/
noncomputable def r₄ (n : ℕ) : ℕ :=
  Finset.card (Finset.filter
    (fun p : ℤ × ℤ × ℤ × ℤ => p.1 ^ 2 + p.2.1 ^ 2 + p.2.2.1 ^ 2 + p.2.2.2 ^ 2 = ↑n)
    ((Finset.Icc (-(↑n : ℤ)) ↑n) ×ˢ (Finset.Icc (-(↑n : ℤ)) ↑n) ×ˢ
     (Finset.Icc (-(↑n : ℤ)) ↑n) ×ˢ (Finset.Icc (-(↑n : ℤ)) ↑n)))

/-! ## Divisor-based formulas

The representation counts can be computed from divisor sums, which is the
"decoding" of the integer's divisor structure through each channel. -/

/-- Count divisors of n that are ≡ 1 (mod 4) -/
def d₁ (n : ℕ) : ℕ :=
  ((Nat.divisors n).filter (fun d => d % 4 = 1)).card

/-- Count divisors of n that are ≡ 3 (mod 4) -/
def d₃ (n : ℕ) : ℕ :=
  ((Nat.divisors n).filter (fun d => d % 4 = 3)).card

/-- Jacobi's formula helper: sum of divisors of n not divisible by 4 -/
def jacobi_sum (n : ℕ) : ℕ :=
  ((Nat.divisors n).filter (fun d => ¬(4 ∣ d))).sum id

/-- The four-channel signature of a positive integer.
    Components: (is_square, channel_2_signal, channel_3_signal, channel_4_info) -/
structure FourChannelSig where
  /-- Channel 1: Is n a perfect square? -/
  is_square : Bool
  /-- Channel 2: d₁(n) - d₃(n), the imbalance of divisors mod 4 -/
  complex_signal : ℤ
  /-- Channel 3: Jacobi sum = Σ_{d|n, 4∤d} d -/
  quaternionic_signal : ℕ
  /-- Channel 4: Σ_{d|n} (-1)^{n+d} d³ (for the octonionic channel) -/
  octonionic_signal : ℤ
  deriving Repr

/-- Compute the four-channel signature of n -/
def fourChannelSig (n : ℕ) : FourChannelSig where
  is_square := Nat.sqrt n ^ 2 == n
  complex_signal := ↑(d₁ n) - ↑(d₃ n)
  quaternionic_signal := jacobi_sum n
  octonionic_signal :=
    ((Nat.divisors n).sum fun d =>
      if (n + d) % 2 == 0 then (↑d : ℤ) ^ 3 else -(↑d : ℤ) ^ 3)

/-! ## Key Theorems -/

/-
PROBLEM
Every positive integer is a sum of four squares (Lagrange's theorem).
    In our framework: Channel 3 always has nonzero output.

PROVIDED SOLUTION
Use Int.sum_four_squares from Mathlib which states exactly this.
-/
theorem lagrange_four_squares (n : ℕ) :
    ∃ a b c d : ℤ, a ^ 2 + b ^ 2 + c ^ 2 + d ^ 2 = ↑n := by
  have := Nat.sum_four_squares n; aesop;

/-
PROBLEM
The Gaussian integer norm is multiplicative: N(zw) = N(z)N(w).
    This is the "composition law" that makes Channel 2 work.

PROVIDED SOLUTION
Expand both sides and verify by ring.
-/
theorem gaussian_norm_multiplicative (a b c d : ℤ) :
    (a ^ 2 + b ^ 2) * (c ^ 2 + d ^ 2) =
    (a * c - b * d) ^ 2 + (a * d + b * c) ^ 2 := by
  ring

/-
PROBLEM
The two-square identity (Brahmagupta-Fibonacci).
    If m and n are sums of two squares, so is mn.

PROVIDED SOLUTION
Use the Brahmagupta-Fibonacci identity: given m = a² + b² and n = c² + d², we have mn = (ac-bd)² + (ad+bc)². Apply gaussian_norm_multiplicative.
-/
theorem sum_two_squares_mul {m n : ℕ}
    (hm : ∃ a b : ℤ, a ^ 2 + b ^ 2 = ↑m)
    (hn : ∃ c d : ℤ, c ^ 2 + d ^ 2 = ↑n) :
    ∃ e f : ℤ, e ^ 2 + f ^ 2 = ↑(m * n) := by
  obtain ⟨ a, b, h ⟩ := hm; obtain ⟨ c, d, j ⟩ := hn; use a * c - b * d, a * d + b * c; push_cast; rw [ ← h, ← j ] ; ring;

/-
PROBLEM
Channel monotonicity: if n is a sum of 2 squares, it's also a sum of 4 squares.
    (Use zeros for the extra two components.)

PROVIDED SOLUTION
Given a² + b² = n, use c = 0, d = 0 to get a² + b² + 0² + 0² = n.
-/
theorem channel_2_implies_4 {n : ℕ}
    (h : ∃ a b : ℤ, a ^ 2 + b ^ 2 = ↑n) :
    ∃ a b c d : ℤ, a ^ 2 + b ^ 2 + c ^ 2 + d ^ 2 = ↑n := by
  exact ⟨ h.choose, h.choose_spec.choose, 0, 0, by linear_combination h.choose_spec.choose_spec ⟩

/-
PROBLEM
A prime p ≡ 1 (mod 4) is a sum of two squares (Fermat's theorem on sums of two squares).
    Channel 2 "hears" these primes.

PROVIDED SOLUTION
Use Nat.Prime.sq_add_sq from Mathlib which gives the result for primes p % 4 = 1.
-/
theorem fermat_sum_two_squares {p : ℕ} (hp : Nat.Prime p) (hmod : p % 4 = 1) :
    ∃ a b : ℤ, a ^ 2 + b ^ 2 = ↑p := by
  have := Fact.mk hp; have := @Nat.Prime.sq_add_sq p; aesop;

/-
PROBLEM
The Hurwitz composition identity for quaternions (4 squares).
    Product of two sums of 4 squares is a sum of 4 squares.

PROVIDED SOLUTION
Expand both sides and verify by ring.
-/
theorem euler_four_square_identity (a₁ a₂ a₃ a₄ b₁ b₂ b₃ b₄ : ℤ) :
    (a₁^2 + a₂^2 + a₃^2 + a₄^2) * (b₁^2 + b₂^2 + b₃^2 + b₄^2) =
    (a₁*b₁ - a₂*b₂ - a₃*b₃ - a₄*b₄)^2 +
    (a₁*b₂ + a₂*b₁ + a₃*b₄ - a₄*b₃)^2 +
    (a₁*b₃ - a₂*b₄ + a₃*b₁ + a₄*b₂)^2 +
    (a₁*b₄ + a₂*b₃ - a₃*b₂ + a₄*b₁)^2 := by
  ring

/-
PROBLEM
Degen's eight-square identity: product of two sums of 8 squares is a sum of 8 squares.
    This is the composition law for Channel 4 (octonions).

PROVIDED SOLUTION
Construct z explicitly using the octonion multiplication formula (Degen's identity). Define each z i as the appropriate bilinear combination of x and y. This is a finite computation - just define the 8 output coordinates and verify by ring. Alternatively, use the fact that this follows from the existence of the octonions as a composition algebra - just use Finset.sum and construct the witness.
-/
theorem eight_square_identity_exists (x y : Fin 8 → ℤ) :
    ∃ z : Fin 8 → ℤ,
    (∑ i, x i ^ 2) * (∑ i, y i ^ 2) = ∑ i, z i ^ 2 := by
  -- Let's denote the elements of $x$ and $y$ as $x_1, x_2, \ldots, x_8$ and $y_1, y_2, \ldots, y_8$ respectively.
  set x1 := x 0
  set x2 := x 1
  set x3 := x 2
  set x4 := x 3
  set x5 := x 4
  set x6 := x 5
  set x7 := x 6
  set x8 := x 7
  set y1 := y 0
  set y2 := y 1
  set y3 := y 2
  set y4 := y 3
  set y5 := y 4
  set y6 := y 5
  set y7 := y 6
  set y8 := y 7;
  use ![x1 * y1 - x2 * y2 - x3 * y3 - x4 * y4 - x5 * y5 - x6 * y6 - x7 * y7 - x8 * y8, x1 * y2 + x2 * y1 + x3 * y4 - x4 * y3 + x5 * y6 - x6 * y5 - x7 * y8 + x8 * y7, x1 * y3 - x2 * y4 + x3 * y1 + x4 * y2 + x5 * y7 + x6 * y8 - x7 * y5 - x8 * y6, x1 * y4 + x2 * y3 - x3 * y2 + x4 * y1 + x5 * y8 - x6 * y7 + x7 * y6 - x8 * y5, x1 * y5 - x2 * y6 - x3 * y7 - x4 * y8 + x5 * y1 + x6 * y2 + x7 * y3 + x8 * y4, x1 * y6 + x2 * y5 - x3 * y8 + x4 * y7 - x5 * y2 + x6 * y1 - x7 * y4 + x8 * y3, x1 * y7 + x2 * y8 + x3 * y5 - x4 * y6 - x5 * y3 + x6 * y4 + x7 * y1 - x8 * y2, x1 * y8 - x2 * y7 + x3 * y6 + x4 * y5 - x5 * y4 - x6 * y3 + x7 * y2 + x8 * y1];
  simpa [ Fin.sum_univ_succ ] using by ring!;

/-
PROBLEM
The Jacobi sum is always positive for n ≥ 1, confirming Channel 3 always has output

PROVIDED SOLUTION
n itself is a divisor of n (for n ≥ 1), and if n is not divisible by 4 then n contributes to the sum. If n is divisible by 4, then 1 is a divisor and 1 is not divisible by 4, so 1 contributes. Either way the filtered set is nonempty and contains a positive element.
-/
theorem jacobi_sum_pos {n : ℕ} (hn : n ≥ 1) : jacobi_sum n ≥ 1 := by
  exact Finset.sum_pos ( fun x hx => Nat.pos_of_mem_divisors <| Finset.mem_filter.mp hx |>.1 ) ⟨ 1, Finset.mem_filter.mpr ⟨ Nat.mem_divisors.mpr ⟨ by norm_num, by linarith ⟩, by norm_num ⟩ ⟩

/-
PROBLEM
For coprime m, n: d₁(mn) can be expressed in terms of d₁ and d₃ of m and n.
    This is the "multiplicativity" of Channel 2 decoding.

PROVIDED SOLUTION
When gcd(m,n)=1, the divisors of mn are in bijection with pairs (d₁, d₂) where d₁|m and d₂|n via d = d₁d₂. Use Nat.Coprime.divisors_mul. A divisor d₁d₂ has d₁d₂ mod 4 determined by (d₁ mod 4)(d₂ mod 4) mod 4. Divisor d₁d₂ ≡ 1 (mod 4) iff both d₁,d₂ ≡ 1 (mod 4) or both ≡ 3 (mod 4). So the count of divisors ≡ 1 (mod 4) of mn equals d₁(m)·d₁(n) + d₃(m)·d₃(n).
-/
theorem d₁_multiplicative {m n : ℕ} (hcop : Nat.Coprime m n) :
    d₁ (m * n) = d₁ m * d₁ n + d₃ m * d₃ n := by
  -- By definition of $d₁$ and $d₃$, we can write
  have h_def : d₁ (m * n) = Finset.card (Finset.filter (fun d => d % 4 = 1) (Nat.divisors (m * n))) ∧ d₃ (m * n) = Finset.card (Finset.filter (fun d => d % 4 = 3) (Nat.divisors (m * n))) := by
    exact ⟨ rfl, rfl ⟩;
  -- Let's rewrite the divisors of $mn$ in terms of the divisors of $m$ and $n$.
  have h_divisors : Nat.divisors (m * n) = Finset.image (fun (p : ℕ × ℕ) => p.1 * p.2) (Nat.divisors m ×ˢ Nat.divisors n) := by
    exact Nat.divisors_mul _ _;
  -- Let's simplify the expression using the fact that multiplication is commutative and associative.
  have h_simplify : Finset.card (Finset.filter (fun d => d % 4 = 1) (Finset.image (fun (p : ℕ × ℕ) => p.1 * p.2) (Nat.divisors m ×ˢ Nat.divisors n))) = Finset.card (Finset.filter (fun p => p.1 * p.2 % 4 = 1) (Nat.divisors m ×ˢ Nat.divisors n)) := by
    rw [ Finset.card_filter, Finset.card_filter, Finset.sum_image ];
    intros p hp q hq h_eq; simp_all +decide [ Nat.coprime_iff_gcd_eq_one ] ;
    -- Since $p.1 \mid m$ and $q.1 \mid m$, and $\gcd(m, n) = 1$, it follows that $p.1 = q.1$.
    have hp1_eq_q1 : p.1 = q.1 := by
      exact Nat.dvd_antisymm ( by exact ( Nat.Coprime.dvd_of_dvd_mul_right ( show Nat.Coprime ( p.1 ) ( q.2 ) from Nat.Coprime.coprime_dvd_left ( by aesop ) <| Nat.Coprime.coprime_dvd_right ( by aesop ) hcop ) <| h_eq.symm ▸ dvd_mul_right _ _ ) ) ( by exact ( Nat.Coprime.dvd_of_dvd_mul_right ( show Nat.Coprime ( q.1 ) ( p.2 ) from Nat.Coprime.coprime_dvd_left ( by aesop ) <| Nat.Coprime.coprime_dvd_right ( by aesop ) hcop ) <| h_eq.symm ▸ dvd_mul_right _ _ ) );
    aesop;
  simp_all +decide [ Finset.sum_filter, Finset.sum_product ];
  simp +decide only [card_filter, d₁, d₃];
  rw [ Finset.sum_product, Finset.sum_mul, Finset.sum_mul ];
  simp +decide only [Finset.mul_sum _ _ _];
  simpa only [ ← Finset.sum_add_distrib ] using Finset.sum_congr rfl fun i hi => Finset.sum_congr rfl fun j hj => by norm_num [ Nat.mul_mod ] ; have := Nat.mod_lt i zero_lt_four; have := Nat.mod_lt j zero_lt_four; interval_cases i % 4 <;> interval_cases j % 4 <;> trivial;
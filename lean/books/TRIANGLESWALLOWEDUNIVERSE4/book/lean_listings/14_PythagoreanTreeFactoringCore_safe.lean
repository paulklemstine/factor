import Mathlib

/-!
# Pythagorean Tree Factoring ? Core Formalization

This file contains the machine-verified mathematical foundations for
factoring integers via descent in the Berggren Pythagorean triple tree.

## Main Results

1. **`trivial_triple_is_pyth`**: For any odd N, (N, (N?-1)/2, (N?+1)/2) is Pythagorean
2. **`diff_of_squares`**: N? + b? = c?  ?  (c-b)(c+b) = N?
3. **`parent_hyp_decrease`**: Inverse Berggren reduces hypotenuse: 0 < c' < c
4. **`inv_B*_preserves`**: Inverse matrices preserve the Pythagorean property
5. **`factor_from_gcd`**: Non-trivial gcd of leg with N yields factor of N
-/

open Nat

/-! ## Section 1: The Trivial Triple -/

/-- For any odd N, the triple (N, (N?-1)/2, (N?+1)/2) satisfies the Pythagorean equation. -/
theorem trivial_triple_is_pyth (N : Int) (hN : N % 2 = 1) :
    N ^ 2 + ((N ^ 2 - 1) / 2) ^ 2 = ((N ^ 2 + 1) / 2) ^ 2 := by
  have h1 : (2 : Int) ? (N ^ 2 - 1) := by
    have : N % 2 = 1 := hN
    obtain <k, hk> : exists  k, N = 2 * k + 1 := <(N - 1) / 2, by omega>
    subst hk; ring_nf; omega
  have h2 : (2 : Int) ? (N ^ 2 + 1) := by
    have := h1; omega
  nlinarith [Int.ediv_mul_cancel h1, Int.ediv_mul_cancel h2]

/-! ## Section 2: Difference of Squares -/

/-- The core algebraic identity: if N? + b? = c? then (c-b)(c+b) = N?. -/
theorem diff_of_squares (N b c : Int) (h : N ^ 2 + b ^ 2 = c ^ 2) :
    (c - b) * (c + b) = N ^ 2 := by ring_nf; linarith

/-
Converse: a same-parity divisor pair gives a Pythagorean triple.
-/
theorem divisor_pair_to_triple (N d e : Int) (hprod : d * e = N ^ 2)
    (hparity : (2 : Int) ? (e - d)) :
    N ^ 2 + ((e - d) / 2) ^ 2 = ((e + d) / 2) ^ 2 := by
      cases abs_cases e <;> cases abs_cases d <;> nlinarith [ Int.ediv_mul_cancel hparity, Int.ediv_mul_cancel ( show 2 ? e + d from even_iff_two_dvd.mp ( by simpa [ <- parity_simps ] using hparity.even ) ) ]

/-! ## Section 3: Inverse Berggren Matrices Preserve Pythagorean Property -/

/-- B1^(-1) preserves the Pythagorean property. -/
theorem inv_B1_preserves (a b c : Int) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    (a + 2*b - 2*c) ^ 2 + (-2*a - b + 2*c) ^ 2 = (-2*a - 2*b + 3*c) ^ 2 := by nlinarith

/-- B2^(-1) preserves the Pythagorean property. -/
theorem inv_B2_preserves (a b c : Int) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    (a + 2*b - 2*c) ^ 2 + (2*a + b - 2*c) ^ 2 = (-2*a - 2*b + 3*c) ^ 2 := by nlinarith

/-- B3^(-1) preserves the Pythagorean property. -/
theorem inv_B3_preserves (a b c : Int) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    (-a - 2*b + 2*c) ^ 2 + (2*a + b - 2*c) ^ 2 = (-2*a - 2*b + 3*c) ^ 2 := by nlinarith

/-! ## Section 4: Descent Termination -/

/-- The parent hypotenuse is strictly less than the child's. -/
theorem parent_hyp_lt (a b c : Int) (ha : 0 < a) (hb : 0 < b)
    (h : a ^ 2 + b ^ 2 = c ^ 2) :
    -2*a - 2*b + 3*c < c := by nlinarith [sq_nonneg (a + b - c)]

/-- The parent hypotenuse is strictly positive. -/
theorem parent_hyp_pos (a b c : Int) (ha : 0 < a) (hb : 0 < b) (hc : 0 < c)
    (h : a ^ 2 + b ^ 2 = c ^ 2) :
    0 < -2*a - 2*b + 3*c := by nlinarith [sq_nonneg (a - b), sq_nonneg (3*c - 2*(a + b))]

/-- Combined descent bound: 0 < c' < c. -/
theorem parent_hyp_decrease (a b c : Int) (ha : 0 < a) (hb : 0 < b) (hc : 0 < c)
    (h : a ^ 2 + b ^ 2 = c ^ 2) :
    0 < -2*a - 2*b + 3*c /\ -2*a - 2*b + 3*c < c :=
  <parent_hyp_pos a b c ha hb hc h, parent_hyp_lt a b c ha hb h>

/-! ## Section 5: Forward-Inverse Round-Trip -/

/-- B1^(-1) ? B1 = Id (component-wise) -/
theorem inv_B1_comp_B1 (a b c : Int) :
    let a' := a - 2*b + 2*c
    let b' := 2*a - b + 2*c
    let c' := 2*a - 2*b + 3*c
    a' + 2*b' - 2*c' = a /\ -2*a' - b' + 2*c' = b /\ -2*a' - 2*b' + 3*c' = c :=
  <by ring, by ring, by ring>

/-- B2^(-1) ? B2 = Id (component-wise) -/
theorem inv_B2_comp_B2 (a b c : Int) :
    let a' := a + 2*b + 2*c
    let b' := 2*a + b + 2*c
    let c' := 2*a + 2*b + 3*c
    a' + 2*b' - 2*c' = a /\ 2*a' + b' - 2*c' = b /\ -2*a' - 2*b' + 3*c' = c :=
  <by ring, by ring, by ring>

/-- B3^(-1) ? B3 = Id (component-wise) -/
theorem inv_B3_comp_B3 (a b c : Int) :
    let a' := -a + 2*b + 2*c
    let b' := -2*a + b + 2*c
    let c' := -2*a + 2*b + 3*c
    (0 - a') - 2*b' + 2*c' = a /\ 2*a' + b' - 2*c' = b /\ (0 - 2*a') - 2*b' + 3*c' = c :=
  <by ring, by ring, by ring>

/-! ## Section 6: Factor Extraction via GCD -/

/-- If gcd(d, N) is non-trivial, it's a factor of N. -/
theorem factor_from_gcd (N d : Nat) (_hN : 1 < N)
    (hg_gt : 1 < Nat.gcd d N) (hg_lt : Nat.gcd d N < N) :
    Nat.gcd d N ? N /\ 1 < Nat.gcd d N /\ Nat.gcd d N < N :=
  <Nat.gcd_dvd_right d N, hg_gt, hg_lt>

/-- For a semiprime N = p*q, the divisor d = p gives gcd(d, N) = p. -/
theorem semiprime_gcd (p q : Nat) (_hp : Nat.Prime p) :
    Nat.gcd p (p * q) = p :=
  Nat.gcd_eq_left (dvd_mul_right p q)

/-! ## Section 7: Parent Uniqueness -/

/-- At most one inverse Berggren map produces positive first and second components. -/
theorem inv_B1_B2_exclusive (a b c : Int)
    (h1 : 0 < -2*a - b + 2*c) (h2 : 0 < 2*a + b - 2*c) : False := by linarith

/-! ## Section 8: Lorentz Form Preservation -/

theorem inv_B1_lorentz (a b c : Int) :
    (a + 2*b - 2*c)^2 + (-2*a - b + 2*c)^2 - (-2*a - 2*b + 3*c)^2 =
    a^2 + b^2 - c^2 := by ring

theorem inv_B2_lorentz (a b c : Int) :
    (a + 2*b - 2*c)^2 + (2*a + b - 2*c)^2 - (-2*a - 2*b + 3*c)^2 =
    a^2 + b^2 - c^2 := by ring

theorem inv_B3_lorentz (a b c : Int) :
    (-a - 2*b + 2*c)^2 + (2*a + b - 2*c)^2 - (-2*a - 2*b + 3*c)^2 =
    a^2 + b^2 - c^2 := by ring

/-! ## Section 9: Computational Algorithm -/

/-- The parent-finding function: returns which branch and the parent triple. -/
def findParent' (a b c : Int) : Nat x Int x Int x Int :=
  let (a1, b1, c1) := (a + 2*b - 2*c, -2*a - b + 2*c, -2*a - 2*b + 3*c)
  let (a2, b2, c2) := (a + 2*b - 2*c, 2*a + b - 2*c, -2*a - 2*b + 3*c)
  if 0 < a1 && 0 < b1 then (1, a1, b1, c1)
  else if 0 < a2 && 0 < b2 then (2, a2, b2, c2)
  else
    let (a3, b3, c3) := (-a - 2*b + 2*c, 2*a + b - 2*c, -2*a - 2*b + 3*c)
    (3, a3, b3, c3)

/-- Factor N by tree descent with fuel. -/

-- [... 29 more lines omitted for brevity ...]
-- See the full source in lean/14_PythagoreanTreeFactoringCore.lean
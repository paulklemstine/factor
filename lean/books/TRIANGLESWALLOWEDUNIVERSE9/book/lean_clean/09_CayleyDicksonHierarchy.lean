/-
# The Cayley-Dickson Construction and Channel Boundaries

This file formalizes the Cayley-Dickson doubling construction and explores
what properties are lost at each step -- the "cost" of opening each new channel.

## The Four Channels
- Real -> Complex: Lose total ordering (gain: algebraic closure over Real)
- Complex -> Quaternion: Lose commutativity (gain: 3D rotations)
- Quaternion -> ?: Lose associativity (gain: E_8 lattice)
- ? -> Sedenions: Lose division (CHANNEL BREAKS -- zero divisors appear)
-/

import Mathlib

/-! ## Properties of the complex numbers -/

/-- Complex multiplication is commutative -- a property lost in the quaternions. -/
example (z w : Complex) : z * w = w * z := mul_comm z w

/-
PROBLEM
The complex norm squared is multiplicative: normSq(zw) = normSq(z) . normSq(w).
    This is the composition algebra property for Channel 2.

PROVIDED SOLUTION
Use map_mul from Mathlib - Complex.normSq is a MonoidHom.
-/
theorem complex_norm_sq_mul (z w : Complex) :
    Complex.normSq (z * w) = Complex.normSq z * Complex.normSq w := by
  rw [ Complex.normSq_mul ]

/-! ## Properties of the quaternions (Quaternion) -/

/-
PROBLEM
Quaternion multiplication is NOT commutative in general.
    We demonstrate this with i.j != j.i (in fact i.j = k but j.i = -k).

PROVIDED SOLUTION
Use i = <0,1,0,0> and j = <0,0,1,0>. Then extract the imK component: ij has imK = 1 but ji has imK = -1. Use congr_arg QuaternionAlgebra.imK and simp, then linarith.
-/
theorem quaternion_not_commutative :
    exists (a b : Quaternion Real), a * b != b * a := by
  -- By definition of quaternion multiplication, we can compute the products $a * b$ and $b * a$ and show they are not equal.
  use <0, 1, 0, 0>, <0, 0, 1, 0>
  simp [Quaternion.ext_iff];
  norm_num [ Complex.ext_iff ] at * <;> first | linarith | aesop | assumption;

/-! ## The composition algebra structure -/

/-- The Brahmagupta-Fibonacci identity: Channel 2 composition law.
    This identity is equivalent to the multiplicativity of the norm on Complex. -/
theorem brahmagupta_fibonacci (a b c d : Int) :
    (a^2 + b^2) * (c^2 + d^2) = (a*c - b*d)^2 + (a*d + b*c)^2 := by
  ring

/-- Euler's four-square identity: Channel 3 composition law.
    This identity is equivalent to the multiplicativity of the norm on Quaternion. -/
theorem euler_four_square (x_1 x_2 x_3 x_4 y_1 y_2 y_3 y_4 : Int) :
    (x_1^2 + x_2^2 + x_3^2 + x_4^2) * (y_1^2 + y_2^2 + y_3^2 + y_4^2) =
    (x_1*y_1 - x_2*y_2 - x_3*y_3 - x_4*y_4)^2 +
    (x_1*y_2 + x_2*y_1 + x_3*y_4 - x_4*y_3)^2 +
    (x_1*y_3 - x_2*y_4 + x_3*y_1 + x_4*y_2)^2 +
    (x_1*y_4 + x_2*y_3 - x_3*y_2 + x_4*y_1)^2 := by
  ring

/-! ## The "channel hierarchy" -- embeddings between channels -/

/-
PROBLEM
Channel 1 embeds in Channel 2: a sum of 1 square is a sum of 2 squares

PROVIDED SOLUTION
Given a2 = n, use (a, 0) since a2 + 02 = n.
-/
theorem channel_1_to_2 (n : Nat) (h : exists a : Int, a ^ 2 = ?n) :
    exists a b : Int, a ^ 2 + b ^ 2 = ?n := by
  exact < h.choose, 0, by simpa using h.choose_spec >

/-
PROBLEM
Channel 2 embeds in Channel 3: a sum of 2 squares is a sum of 4 squares

PROVIDED SOLUTION
Given a2 + b2 = n, use (a, b, 0, 0) since a2 + b2 + 02 + 02 = n.
-/
theorem channel_2_to_3 (n : Nat) (h : exists a b : Int, a ^ 2 + b ^ 2 = ?n) :
    exists a b c d : Int, a ^ 2 + b ^ 2 + c ^ 2 + d ^ 2 = ?n := by
  exact < h.choose, h.choose_spec.choose, 0, 0, by linear_combination h.choose_spec.choose_spec >

/-
PROBLEM
Channel 3 embeds in Channel 4: a sum of 4 squares is a sum of 8 squares

PROVIDED SOLUTION
Given a2 + b2 + c2 + d2 = n, define f : Fin 8 -> Int by f(0)=a, f(1)=b, f(2)=c, f(3)=d, f(4..7)=0. Then sum f(i)2 = a2 + b2 + c2 + d2 + 0 + 0 + 0 + 0 = n. Use Fin.sum_univ_eight or Fin.cons.
-/
theorem channel_3_to_4 (n : Nat) (h : exists a b c d : Int, a ^ 2 + b ^ 2 + c ^ 2 + d ^ 2 = ?n) :
    exists f : Fin 8 -> Int, sum i, f i ^ 2 = ?n := by
  -- By definition of Fin 8, we can construct such an f by setting the first four elements to a, b, c, d and the rest to zero.
  obtain <a, b, c, d, h_sum> := h;
  use fun i => if i.val < 4 then if i.val = 0 then a else if i.val = 1 then b else if i.val = 2 then c else d else 0;
  simp [Fin.sum_univ_eight, h_sum];

/-! ## Dimension constraints: why 1, 2, 4, 8 are special -/

/-
PROBLEM
The dimensions 1, 2, 4, 8 are exactly the powers of 2 up to 8

PROVIDED SOLUTION
Just decide or norm_num -- both sides are concrete finite sets of naturals.
-/
theorem hurwitz_dimensions : ({1, 2, 4, 8} : Finset Nat) = {2^0, 2^1, 2^2, 2^3} := by
  grind

/-- Sum of all Hurwitz dimensions equals 15, which is 2? - 1 -/
theorem sum_hurwitz_dims : 1 + 2 + 4 + 8 = 15 := by norm_num

/-- Product of all Hurwitz dimensions equals 64 = 2? -/
theorem prod_hurwitz_dims : 1 * 2 * 4 * 8 = 64 := by norm_num

/-! ## Information-theoretic properties -/

/-
PROBLEM
For any n >= 1, the Channel 1 "decoder" outputs at most 2 representations.
    (n is either a perfect square or not)

PROVIDED SOLUTION
The solutions to a2 = n in [-n, n] are at most {?n, -?n}, so the cardinality is at most 2. Show the filter is a subset of {Nat.sqrt n, -(Nat.sqrt n)} and use Finset.card_le_card.
-/
theorem channel_1_bounded (n : Nat) (hn : n >= 1) :
    (Finset.filter (fun a : Int => a ^ 2 = ?n) (Finset.Icc (-(?n : Int)) ?n)).card <= 2 := by
  refine' le_trans ( Finset.card_le_card _ ) _;
  exact { ? ( Nat.sqrt n ), -? ( Nat.sqrt n ) };
  . intro x hx; rw [ Finset.mem_filter ] at hx; rw [ Finset.mem_insert, Finset.mem_singleton ] ; cases le_or_gt 0 x <;> [ left; right ] <;> nlinarith [ Nat.sqrt_le n, Nat.lt_succ_sqrt n ] ;
  . exact Finset.card_insert_le _ _

/-! ## Computational verification of the Jacobi four-square formula -/

/-- Jacobi sum: Sigma_{d|n, 4?d} d -/
def jacobi' (n : Nat) : Nat := ((Nat.divisors n).filter (fun d => !(4 | d))).sum id

-- Verify Jacobi's formula for small n
#eval jacobi' 1      -- 1
#eval 8 * jacobi' 1  -- 8 (= r_4(1))

#eval jacobi' 5      -- 6 (1 + 5)
#eval 8 * jacobi' 5  -- 48 (= r_4(5))

#eval jacobi' 12     -- 12
#eval 8 * jacobi' 12
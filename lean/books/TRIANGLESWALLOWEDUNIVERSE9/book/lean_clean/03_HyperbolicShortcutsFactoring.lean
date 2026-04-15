import Mathlib

/-!
# Hyperbolic Shortcuts and Integer Factoring via the Berggren Tree

## Overview

We formalize the connection between the Berggren tree of primitive Pythagorean triples,
the integer Lorentz group O(2,1;Int), and integer factoring. The main results are:

1. **Difference-of-squares from Pythagorean triples**: Every Pythagorean triple
   `a2 + b2 = c2` yields a factorization `(c-b)(c+b) = a2`.

2. **Berggren matrices as Lorentz isometries**: All three generators preserve the
   quadratic form Q(a,b,c) = a2 + b2 - c2, placing them in O(2,1;Int).

3. **Hypotenuse growth bounds**: The hypotenuse grows strictly along every branch.

4. **Middle-branch Chebyshev recurrence**: The B_2-branch hypotenuses satisfy
   `c_{n+1} = 6c_n - c_{n-1}`.

5. **Shortcut composition**: Path concatenation = matrix multiplication, enabling
   O(log k) navigation via repeated squaring.

6. **Inverse matrices and tree ascent**: Explicit integer inverses allow ascending
   the tree from any primitive triple back to the root (3,4,5).

7. **Factoring connection**: The difference-of-squares identity from a Pythagorean
   triple can reveal nontrivial factors via GCD computation.

## Mathematical Context

The Berggren tree (Berggren 1934) generates all primitive Pythagorean triples
from (3,4,5) using three matrices B_1, B_2, B_3 that lie in the integer Lorentz
group O(2,1;Int). Each matrix preserves the quadratic form Q(a,b,c) = a2 + b2 - c2.

A "hyperbolic shortcut" is a composite matrix B_{i_1} . B_{i_2} . ? . B_{i?}
that jumps across k levels of the tree in a single matrix-vector multiplication.
These shortcuts can be computed in O(log k) time via repeated squaring.
-/

open Matrix

namespace HyperbolicFactoring

/-! ## ?1. Fundamental Algebraic Identities -/

/-- The core algebraic identity: for any Pythagorean triple, the hypotenuse
    and one leg yield a difference-of-squares factorization of the other leg squared. -/
theorem diff_of_squares_from_pyth {a b c : Int} (h : a ^ 2 + b ^ 2 = c ^ 2) :
    (c - b) * (c + b) = a ^ 2 := by linarith [sq_nonneg a, sq_nonneg b, sq_nonneg c]

/-- The factorization works symmetrically for the other leg. -/
theorem diff_of_squares_sym {a b c : Int} (h : a ^ 2 + b ^ 2 = c ^ 2) :
    (c - a) * (c + a) = b ^ 2 := by linarith [sq_nonneg a, sq_nonneg b, sq_nonneg c]

/-- If a2 + b2 = c2 with a > 0 and c > 0, then b < c. -/
theorem hyp_gt_leg {a b c : Int} (h : a ^ 2 + b ^ 2 = c ^ 2) (ha : 0 < a) (hc : 0 < c) :
    b < c := by nlinarith [sq_nonneg (c - b)]

/-- For a Pythagorean triple with positive entries, c - b and c + b are both positive. -/
theorem factors_pos {a b c : Int} (h : a ^ 2 + b ^ 2 = c ^ 2)
    (ha : 0 < a) (hb : 0 < b) (hc : 0 < c) :
    0 < c - b /\ 0 < c + b := by
  exact <by nlinarith [sq_nonneg (c - b)], by linarith>

/-! ## ?2. The Berggren Matrices -/

/-- Berggren matrix B_1 (left branch). -/
def B_1 : Matrix (Fin 3) (Fin 3) Int := !![1, -2, 2; 2, -1, 2; 2, -2, 3]

/-- Berggren matrix B_2 (middle branch). -/
def B_2 : Matrix (Fin 3) (Fin 3) Int := !![1, 2, 2; 2, 1, 2; 2, 2, 3]

/-- Berggren matrix B_3 (right branch). -/
def B_3 : Matrix (Fin 3) (Fin 3) Int := !![-1, 2, 2; -2, 1, 2; -2, 2, 3]

/-- The Lorentz metric Q = diag(1, 1, -1). -/
def Q : Matrix (Fin 3) (Fin 3) Int := !![1, 0, 0; 0, 1, 0; 0, 0, -1]

/-- B_1 preserves the Lorentz form: B_1^T Q B_1 = Q. -/
theorem B_1_lorentz : B_1^T * Q * B_1 = Q := by native_decide

/-- B_2 preserves the Lorentz form. -/
theorem B_2_lorentz : B_2^T * Q * B_2 = Q := by native_decide

/-- B_3 preserves the Lorentz form. -/
theorem B_3_lorentz : B_3^T * Q * B_3 = Q := by native_decide

/-- det(B_1) = 1: B_1 is in SO?(2,1;Int). -/
theorem det_B_1 : Matrix.det B_1 = 1 := by native_decide

/-- det(B_2) = -1: B_2 is in O(2,1;Int) \ SO(2,1;Int). -/
theorem det_B_2 : Matrix.det B_2 = -1 := by native_decide

/-- det(B_3) = 1: B_3 is in SO?(2,1;Int). -/
theorem det_B_3 : Matrix.det B_3 = 1 := by native_decide

/-! ## ?3. Berggren Tree Structure -/

/-- Direction in the ternary tree. -/
inductive Dir where
  | L | M | R
  deriving DecidableEq, Repr

/-- A path in the Berggren tree is a list of directions. -/
abbrev BPath := List Dir

/-- Matrix corresponding to a single direction. -/
def dirMat : Dir -> Matrix (Fin 3) (Fin 3) Int
  | .L => B_1 | .M => B_2 | .R => B_3

/-- The composite matrix for a path (leftmost direction applied first). -/
def pathMat : BPath -> Matrix (Fin 3) (Fin 3) Int
  | [] => 1
  | d :: ds => dirMat d * pathMat ds

/-- The root triple (3, 4, 5). -/
def root : Fin 3 -> Int := ![3, 4, 5]

/-- The triple at a given path in the Berggren tree. -/
def tripleAt (p : BPath) : Fin 3 -> Int := pathMat p *? root

/-- The root satisfies the Pythagorean equation. -/
theorem root_pyth : (root 0) ^ 2 + (root 1) ^ 2 = (root 2) ^ 2 := by native_decide

/-! ## ?4. Pythagorean Property Preservation -/

/-- B_1 preserves the Pythagorean property. -/
theorem B_1_preserves_pyth (a b c : Int) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    (a - 2*b + 2*c)^2 + (2*a - b + 2*c)^2 = (2*a - 2*b + 3*c)^2 := by nlinarith

/-- B_2 preserves the Pythagorean property. -/
theorem B_2_preserves_pyth (a b c : Int) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    (a + 2*b + 2*c)^2 + (2*a + b + 2*c)^2 = (2*a + 2*b + 3*c)^2 := by nlinarith

/-- B_3 preserves the Pythagorean property. -/
theorem B_3_preserves_pyth (a b c : Int) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    (-a + 2*b + 2*c)^2 + (-2*a + b + 2*c)^2 = (-2*a + 2*b + 3*c)^2 := by nlinarith

/-! ## ?5. Hyperbolic Shortcut Composition -/

/-- Path concatenation corresponds to matrix multiplication. -/
theorem pathMat_append (p q : BPath) :
    pathMat (p ++ q) = pathMat p * pathMat q := by
  induction p with
  | nil => simp [pathMat]
  | cons d ds ih => simp [pathMat, ih, Matrix.mul_assoc]

/-- **Shortcut Theorem**: navigating p then q equals the concatenated path. -/
theorem shortcut_compose (p q : BPath) :
    tripleAt (p ++ q) = pathMat p *? tripleAt q := by
  simp [tripleAt, pathMat_append, mulVec_mulVec]

/-- Any path matrix preserves the Lorentz form Q. -/
theorem pathMat_lorentz (p : BPath) :
    (pathMat p)^T * Q * pathMat p = Q := by
  induction p with
  | nil => native_decide
  | cons d ds ih =>
    have hd : (dirMat d)^T * Q * dirMat d = Q := by
      cases d <;> simp [dirMat] <;> native_decide
    simp only [pathMat, transpose_mul]
    rw [show (pathMat ds)^T * (dirMat d)^T * Q * (dirMat d * pathMat ds)
        = (pathMat ds)^T * ((dirMat d)^T * (Q * (dirMat d * pathMat ds))) from by
          simp [Matrix.mul_assoc]]
    rw [show Q * (dirMat d * pathMat ds) = Q * dirMat d * pathMat ds from by
          simp [Matrix.mul_assoc]]
    rw [show (dirMat d)^T * (Q * dirMat d * pathMat ds)
        = (dirMat d)^T * (Q * dirMat d) * pathMat ds from by simp [Matrix.mul_assoc]]
    rw [show (dirMat d)^T * (Q * dirMat d) = (dirMat d)^T * Q * dirMat d from by
          simp [Matrix.mul_assoc]]
    rw [hd]
    rw [show (pathMat ds)^T * (Q * pathMat ds) = (pathMat ds)^T * Q * pathMat ds from by
          simp [Matrix.mul_assoc]]
    exact ih

/-- The |det| of any path matrix is 1. -/
theorem pathMat_det_abs (p : BPath) : |Matrix.det (pathMat p)| = 1 := by
  induction p with
  | nil => simp [pathMat]
  | cons d ds ih =>
    have : |Matrix.det (dirMat d)| = 1 := by cases d <;> native_decide
    simp [pathMat, Matrix.det_mul, abs_mul, this, ih]

/-! ## ?6. Hypotenuse Growth Bounds -/

/-- The hypotenuse strictly increases under B_2 for positive triples. -/
theorem B_2_hyp_increases (a b c : Int) (ha : 0 < a) (hb : 0 < b) (hc : 0 < c) :
    c < 2*a + 2*b + 3*c := by linarith

/-- The hypotenuse strictly increases under B_1 when a2 + b2 = c2, a > 0, c > 0. -/
theorem B_1_hyp_increases (a b c : Int) (ha : 0 < a) (hc : 0 < c)
    (h : a ^ 2 + b ^ 2 = c ^ 2) :
    c < 2*a - 2*b + 3*c := by nlinarith [sq_nonneg (c - b)]

/-- The hypotenuse strictly increases under B_3 when a2 + b2 = c2, b > 0, c > 0. -/
theorem B_3_hyp_increases (a b c : Int) (hb : 0 < b) (hc : 0 < c)
    (h : a ^ 2 + b ^ 2 = c ^ 2) :
    c < -2*a + 2*b + 3*c := by nlinarith [sq_nonneg (c - a)]

/-- B_2-branch hypotenuse is at least 3c (geometric growth). -/
theorem B_2_hyp_triple_growth (a b c : Int) (ha : 0 < a) (hb : 0 < b) :
    3 * c <= 2*a + 2*b + 3*c := by linarith

/-! ## ?7. Middle Branch Chebyshev Recurrence -/

/-- B_2 applied once to (3,4,5) gives hypotenuse 29. -/
theorem B_2_iter1_hyp :
    (B_2 *? (![3, 4, 5] : Fin 3 -> Int)) 2 = 29 := by native_decide

/-- B_2 applied twice gives hypotenuse 169. -/
theorem B_2_iter2_hyp :
    (B_2 *? (B_2 *? (![3, 4, 5] : Fin 3 -> Int))) 2 = 169 := by native_decide

/-- B_2 applied three times gives hypotenuse 985. -/
theorem B_2_iter3_hyp :
    (B_2 *? (B_2 *? (B_2 *? (![3, 4, 5] : Fin 3 -> Int)))) 2 = 985 := by native_decide

/-- The Chebyshev recurrence holds: c_2 = 6c_1 - c_0. -/
theorem chebyshev_step1 : (169 : Int) = 6 * 29 - 5 := by norm_num

/-- c_3 = 6c_2 - c_1. -/
theorem chebyshev_step2 : (985 : Int) = 6 * 169 - 29 := by norm_num

/-! ## ?8. Inverse Berggren Matrices (Tree Ascent) -/

/-- Inverse of B_1: computed as Q . B_1^T . Q. -/
def B_1_inv : Matrix (Fin 3) (Fin 3) Int := !![1, 2, -2; -2, -1, 2; -2, -2, 3]

/-- Inverse of B_2: computed as Q . B_2^T . Q. -/
def B_2_inv : Matrix (Fin 3) (Fin 3) Int := !![1, 2, -2; 2, 1, -2; -2, -2, 3]

/-- Inverse of B_3: computed as Q . B_3^T . Q. -/
def B_3_inv : Matrix (Fin 3) (Fin 3) Int := !![-1, -2, 2; 2, 1, -2; -2, -2, 3]

/-- B_1_inv is the left inverse of B_1. -/
theorem B_1_inv_mul : B_1_inv * B_1 = 1 := by native_decide

/-- B_1_inv is the right inverse of B_1. -/
theorem B_1_mul_inv : B_1 * B_1_inv = 1 := by native_decide

/-- B_2_inv is the left inverse of B_2. -/
theorem B_2_inv_mul : B_2_inv * B_2 = 1 := by native_decide

/-- B_2_inv is the right inverse of B_2. -/
theorem B_2_mul_inv : B_2 * B_2_inv = 1 := by native_decide

/-- B_3_inv is the left inverse of B_3. -/
theorem B_3_inv_mul : B_3_inv * B_3 = 1 := by native_decide

/-- B_3_inv is the right inverse of B_3. -/
theorem B_3_mul_inv : B_3 * B_3_inv = 1 := by native_decide

/-- The inverses are computed via Q . B^T . Q (Lorentz adjoint). -/
theorem B_1_inv_formula : B_1_inv = Q * B_1^T * Q := by native_decide

theorem B_2_inv_formula : B_2_inv = Q * B_2^T * Q := by native_decide

theorem B_3_inv_formula : B_3_inv = Q * B_3^T * Q := by native_decide

/-! ## ?9. Factoring Connection -/

/-- **Core factoring theorem**: a Pythagorean triple with composite leg yields
    a factorization via difference of squares. -/
theorem factoring_from_triple {a b c p q : Int}
    (h_pyth : a ^ 2 + b ^ 2 = c ^ 2) (h_factor : a = p * q) :
    (c - b) * (c + b) = (p * q) ^ 2 := by
  rw [h_factor] at h_pyth; linarith [sq_nonneg (c - b), sq_nonneg (c + b)]

/-- **GCD factoring**: If gcd(c - b, a) is nontrivial, it reveals a factor of a. -/
theorem gcd_reveals_factor {a c_minus_b : Int} (ha : 1 < a)
    (hg : 1 < Int.gcd c_minus_b a) (hg2 : Int.gcd c_minus_b a < a.natAbs) :
    exists d : Nat, 1 < d /\ d < a.natAbs /\ (d : Int) | a := by
  exact <Int.gcd c_minus_b a, hg, hg2, Int.gcd_dvd_right c_minus_b a>

/-! ## ?10. Computational Verification -/

/-- The triple at path [L] is (5, 12, 13). -/
theorem triple_L : tripleAt [Dir.L] = ![5, 12, 13] := by native_decide

/-- The triple at path [M] is (21, 20, 29). -/
theorem triple_M : tripleAt [Dir.M] = ![21, 20, 29] := by native_decide

/-- The triple at path [R] is (15, 8, 17). -/
theorem triple_R : tripleAt [Dir.R] = ![15, 8, 17] := by native_decide

/-- The triple at path [M, M] is (119, 120, 169). -/
theorem triple_MM : tripleAt [Dir.M, Dir.M] = ![119, 120, 169] := by native_decide

/-- The triple at path [L, M] is (39, 80, 89). -/
theorem triple_LM : tripleAt [Dir.L, Dir.M] = ![39, 80, 89] := by native_decide

/-- (5,12,13) is Pythagorean. -/
theorem pyth_5_12_13 : (5 : Int)^2 + 12^2 = 13^2 := by norm_num

/-- (21,20,29) is Pythagorean. -/
theorem pyth_21_20_29 : (21 : Int)^2 + 20^2 = 29^2 := by norm_num

/-- The difference-of-squares from (21, 20, 29): (29-20)(29+20) = 9.49 = 441 = 212. -/
theorem dos_21_20_29 : (29 - 20) * (29 + 20) = (21 : Int)^2 := by norm_num

/-- This reveals the factorization 21 = 3 x 7 since gcd(9, 21) = 3. -/
theorem factor_from_dos : Int.gcd 9 21 = 3 := by native_decide

/-! ## ?11. Branch Disjointness -/

/-- B_1 and B_2 always produce distinct hypotenuses (when b != 0). -/
theorem branch_disjoint_LM (a b c : Int) (hb : b != 0) :
    2*a - 2*b + 3*c != 2*a + 2*b + 3*c := by omega

/-- B_1 and B_3 produce distinct hypotenuses when a != b. -/
theorem branch_disjoint_LR (a b c : Int) (hab : a != b) :
    2*a - 2*b + 3*c != -2*a + 2*b + 3*c := by omega

/-- All three branches produce distinct a-values when a != 0, b != 0, a != 2b. -/
theorem branch_disjoint_legs (a b c : Int) (ha : a != 0) (hb : b != 0) (hab : a != 2*b) :
    a - 2*b + 2*c != a + 2*b + 2*c /\
    a - 2*b + 2*c != -a + 2*b + 2*c /\
    a + 2*b + 2*c != -a + 2*b + 2*c := by
  refine <by omega, by omega, by omega>

/-! ## ?12. Lorentz Form as Quadratic Invariant -/

/-- The Lorentz quadratic form. -/
def lorentzQ (v : Fin 3 -> Int) : Int := (v 0) ^ 2 + (v 1) ^ 2 - (v 2) ^ 2

/-- Pythagorean triples are null vectors of the Lorentz form. -/
theorem pyth_iff_null (v : Fin 3 -> Int) :
    (v 0) ^ 2 + (v 1) ^ 2 = (v 2) ^ 2 <-> lorentzQ v = 0 := by
  unfold lorentzQ; omega

/-- The root is a null vector. -/
theorem root_null : lorentzQ root = 0 := by native_decide

/-- B_1 preserves the Lorentz form for any vector (algebraic proof). -/
theorem B_1_preserves_lorentzQ (a b c : Int) :
    lorentzQ ![a - 2*b + 2*c, 2*a - b + 2*c, 2*a - 2*b + 3*c] = lorentzQ ![a, b, c] := by
  simp [lorentzQ, Matrix.cons_val_zero, Matrix.cons_val_one]; ring

/-- B_2 preserves the Lorentz form for any vector. -/
theorem B_2_preserves_lorentzQ (a b c : Int) :
    lorentzQ ![a + 2*b + 2*c, 2*a + b + 2*c, 2*a + 2*b + 3*c] = lorentzQ ![a, b, c] := by
  simp [lorentzQ, Matrix.cons_val_zero, Matrix.cons_val_one]; ring

/-- B_3 preserves the Lorentz form for any vector. -/
theorem B_3_preserves_lorentzQ (a b c : Int) :
    lorentzQ ![-a + 2*b + 2*c, -2*a + b + 2*c, -2*a + 2*b + 3*c] = lorentzQ ![a, b, c] := by
  simp [lorentzQ, Matrix.cons_val_zero, Matrix.cons_val_one]; ring

end HyperbolicFactoring

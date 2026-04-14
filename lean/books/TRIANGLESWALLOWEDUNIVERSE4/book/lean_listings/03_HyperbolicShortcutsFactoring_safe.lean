import Mathlib

/-!
# Hyperbolic Shortcuts and Integer Factoring via the Berggren Tree

## Overview

We formalize the connection between the Berggren tree of primitive Pythagorean triples,
the integer Lorentz group O(2,1;Int), and integer factoring. The main results are:

1. **Difference-of-squares from Pythagorean triples**: Every Pythagorean triple
   `a? + b? = c?` yields a factorization `(c-b)(c+b) = a?`.

2. **Berggren matrices as Lorentz isometries**: All three generators preserve the
   quadratic form Q(a,b,c) = a? + b? - c?, placing them in O(2,1;Int).

3. **Hypotenuse growth bounds**: The hypotenuse grows strictly along every branch.

4. **Middle-branch Chebyshev recurrence**: The B2-branch hypotenuses satisfy
   `c_{n+1} = 6c_n - c_{n-1}`.

5. **Shortcut composition**: Path concatenation = matrix multiplication, enabling
   O(log k) navigation via repeated squaring.

6. **Inverse matrices and tree ascent**: Explicit integer inverses allow ascending
   the tree from any primitive triple back to the root (3,4,5).

7. **Factoring connection**: The difference-of-squares identity from a Pythagorean
   triple can reveal nontrivial factors via GCD computation.

## Mathematical Context

The Berggren tree (Berggren 1934) generates all primitive Pythagorean triples
from (3,4,5) using three matrices B1, B2, B3 that lie in the integer Lorentz
group O(2,1;Int). Each matrix preserves the quadratic form Q(a,b,c) = a? + b? - c?.

A "hyperbolic shortcut" is a composite matrix B_{i1} . B_{i2} . ? . B_{i?}
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

/-- If a? + b? = c? with a > 0 and c > 0, then b < c. -/
theorem hyp_gt_leg {a b c : Int} (h : a ^ 2 + b ^ 2 = c ^ 2) (ha : 0 < a) (hc : 0 < c) :
    b < c := by nlinarith [sq_nonneg (c - b)]

/-- For a Pythagorean triple with positive entries, c - b and c + b are both positive. -/
theorem factors_pos {a b c : Int} (h : a ^ 2 + b ^ 2 = c ^ 2)
    (ha : 0 < a) (hb : 0 < b) (hc : 0 < c) :
    0 < c - b /\ 0 < c + b := by
  exact <by nlinarith [sq_nonneg (c - b)], by linarith>

/-! ## ?2. The Berggren Matrices -/

/-- Berggren matrix B1 (left branch). -/
def B1 : Matrix (Fin 3) (Fin 3) Int := !![1, -2, 2; 2, -1, 2; 2, -2, 3]

/-- Berggren matrix B2 (middle branch). -/
def B2 : Matrix (Fin 3) (Fin 3) Int := !![1, 2, 2; 2, 1, 2; 2, 2, 3]

/-- Berggren matrix B3 (right branch). -/
def B3 : Matrix (Fin 3) (Fin 3) Int := !![-1, 2, 2; -2, 1, 2; -2, 2, 3]

/-- The Lorentz metric Q = diag(1, 1, -1). -/
def Q : Matrix (Fin 3) (Fin 3) Int := !![1, 0, 0; 0, 1, 0; 0, 0, -1]

/-- B1 preserves the Lorentz form: B1? Q B1 = Q. -/
theorem B1_lorentz : B1? * Q * B1 = Q := by native_decide

/-- B2 preserves the Lorentz form. -/
theorem B2_lorentz : B2? * Q * B2 = Q := by native_decide

/-- B3 preserves the Lorentz form. -/
theorem B3_lorentz : B3? * Q * B3 = Q := by native_decide

/-- det(B1) = 1: B1 is in SO?(2,1;Int). -/
theorem det_B1 : Matrix.det B1 = 1 := by native_decide

/-- det(B2) = -1: B2 is in O(2,1;Int) \ SO(2,1;Int). -/
theorem det_B2 : Matrix.det B2 = -1 := by native_decide

/-- det(B3) = 1: B3 is in SO?(2,1;Int). -/
theorem det_B3 : Matrix.det B3 = 1 := by native_decide

/-! ## ?3. Berggren Tree Structure -/

/-- Direction in the ternary tree. -/
inductive Dir where
  | L | M | R
  deriving DecidableEq, Repr

/-- A path in the Berggren tree is a list of directions. -/
abbrev BPath := List Dir

/-- Matrix corresponding to a single direction. -/
def dirMat : Dir -> Matrix (Fin 3) (Fin 3) Int
  | .L => B1 | .M => B2 | .R => B3

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

/-- B1 preserves the Pythagorean property. -/
theorem B1_preserves_pyth (a b c : Int) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    (a - 2*b + 2*c)^2 + (2*a - b + 2*c)^2 = (2*a - 2*b + 3*c)^2 := by nlinarith

/-- B2 preserves the Pythagorean property. -/
theorem B2_preserves_pyth (a b c : Int) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    (a + 2*b + 2*c)^2 + (2*a + b + 2*c)^2 = (2*a + 2*b + 3*c)^2 := by nlinarith

/-- B3 preserves the Pythagorean property. -/
theorem B3_preserves_pyth (a b c : Int) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    (-a + 2*b + 2*c)^2 + (-2*a + b + 2*c)^2 = (-2*a + 2*b + 3*c)^2 := by nlinarith

/-! ## ?5. Hyperbolic Shortcut Composition -/

/-- Path concatenation corresponds to matrix multiplication. -/
theorem pathMat_append (p q : BPath) :
    pathMat (p ++ q) = pathMat p * pathMat q := by
  induction p with
  | nil => simp [pathMat]
  | cons d ds ih => simp [pathMat, ih, Matrix.mul_assoc]

/-- **Shortcut Theorem**: navigating p then q equals the concatenated path. -/

-- [... 202 more lines omitted for brevity ...]
-- See the full source in lean/03_HyperbolicShortcutsFactoring.lean
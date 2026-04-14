import Mathlib

/-!
# The Berggren-Lorentz Correspondence: Core Formalization

## Overview

We formalize the key mathematical results connecting the Berggren tree of
Pythagorean triples to the Lorentz group and integer factoring:

1. **Berggren matrices preserve the Lorentz form** Q(a,b,c) = a? + b? - c?
2. **Every node in the Berggren tree is a Pythagorean triple**
3. **Hypotenuse strictly decreases during descent** (guaranteeing termination)
4. **The difference-of-squares identity** connecting triples to factoring
5. **The B-branch Pell recurrence** c_{n+1} = 6c_n - c_{n-1}
6. **Descent preserves coprimality structure**

These results establish the Berggren tree as a discrete subgroup of the
integer Lorentz group O(2,1;Int), tiling the hyperbolic plane.
-/

open Matrix

/-! ## ?1. The Lorentz Quadratic Form -/

/-- The Lorentz quadratic form Q(a,b,c) = a? + b? - c?.
    Pythagorean triples are exactly the integer null vectors of this form. -/
def lorentzQ (a b c : Int) : Int := a ^ 2 + b ^ 2 - c ^ 2

/-- Pythagorean triples lie on the null cone of the Lorentz form. -/
theorem pyth_null_cone {a b c : Int} (h : a ^ 2 + b ^ 2 = c ^ 2) :
    lorentzQ a b c = 0 := by
  unfold lorentzQ; omega

/-! ## ?2. Berggren Matrices and Lorentz Preservation -/

/-- Berggren matrix A (also called B1): generates the "slow lane" branch. -/
def berggrenA_matrix : Matrix (Fin 3) (Fin 3) Int :=
  !![1, -2, 2; 2, -1, 2; 2, -2, 3]

/-- Berggren matrix B (also called B2): generates the "fast lane" branch. -/
def berggrenB_matrix : Matrix (Fin 3) (Fin 3) Int :=
  !![1, 2, 2; 2, 1, 2; 2, 2, 3]

/-- Berggren matrix C (also called B3): mirror of A. -/
def berggrenC_matrix : Matrix (Fin 3) (Fin 3) Int :=
  !![(-1), 2, 2; (-2), 1, 2; (-2), 2, 3]

/-- The Lorentz metric matrix Q = diag(1, 1, -1). -/
def lorentzMetric : Matrix (Fin 3) (Fin 3) Int :=
  !![1, 0, 0; 0, 1, 0; 0, 0, (-1)]

/-- **Theorem (Lorentz preservation for A):** B?_A . Q . B_A = Q.
    This means B_A in O(2,1;Int), the integer Lorentz group. -/
theorem berggrenA_lorentz : berggrenA_matrix ? * lorentzMetric * berggrenA_matrix = lorentzMetric := by
  native_decide

/-- **Theorem (Lorentz preservation for B):** B?_B . Q . B_B = Q. -/
theorem berggrenB_lorentz : berggrenB_matrix ? * lorentzMetric * berggrenB_matrix = lorentzMetric := by
  native_decide

/-- **Theorem (Lorentz preservation for C):** B?_C . Q . B_C = Q. -/
theorem berggrenC_lorentz : berggrenC_matrix ? * lorentzMetric * berggrenC_matrix = lorentzMetric := by
  native_decide

/-- The full Lorentz form is preserved by A for *any* integer vector, not just triples.
    Q(Av) = Q(v) for all v in Int?. -/
theorem berggrenA_preserves_form (a b c : Int) :
    lorentzQ (a - 2*b + 2*c) (2*a - b + 2*c) (2*a - 2*b + 3*c) = lorentzQ a b c := by
  unfold lorentzQ; ring

/-- The full Lorentz form is preserved by B for any integer vector. -/
theorem berggrenB_preserves_form (a b c : Int) :
    lorentzQ (a + 2*b + 2*c) (2*a + b + 2*c) (2*a + 2*b + 3*c) = lorentzQ a b c := by
  unfold lorentzQ; ring

/-- The full Lorentz form is preserved by C for any integer vector. -/
theorem berggrenC_preserves_form (a b c : Int) :
    lorentzQ (-a + 2*b + 2*c) (-2*a + b + 2*c) (-2*a + 2*b + 3*c) = lorentzQ a b c := by
  unfold lorentzQ; ring

/-! ## ?3. Pythagorean Preservation -/

/-- **Core theorem:** Berggren A maps Pythagorean triples to Pythagorean triples. -/
theorem berggrenA_pyth {a b c : Int} (h : a ^ 2 + b ^ 2 = c ^ 2) :
    (a - 2*b + 2*c) ^ 2 + (2*a - b + 2*c) ^ 2 = (2*a - 2*b + 3*c) ^ 2 := by
  have := berggrenA_preserves_form a b c
  unfold lorentzQ at this
  linarith

/-- **Core theorem:** Berggren B maps Pythagorean triples to Pythagorean triples. -/
theorem berggrenB_pyth {a b c : Int} (h : a ^ 2 + b ^ 2 = c ^ 2) :
    (a + 2*b + 2*c) ^ 2 + (2*a + b + 2*c) ^ 2 = (2*a + 2*b + 3*c) ^ 2 := by
  have := berggrenB_preserves_form a b c
  unfold lorentzQ at this
  linarith

/-- **Core theorem:** Berggren C maps Pythagorean triples to Pythagorean triples. -/
theorem berggrenC_pyth {a b c : Int} (h : a ^ 2 + b ^ 2 = c ^ 2) :
    (-a + 2*b + 2*c) ^ 2 + (-2*a + b + 2*c) ^ 2 = (-2*a + 2*b + 3*c) ^ 2 := by
  have := berggrenC_preserves_form a b c
  unfold lorentzQ at this
  linarith

/-! ## ?4. Tree Structure and Descent -/

/-- A path in the Berggren ternary tree. -/
inductive BPath where
  | root : BPath
  | brA : BPath -> BPath
  | brB : BPath -> BPath
  | brC : BPath -> BPath

/-- Depth of a tree path. -/
def BPath.depth : BPath -> Nat
  | .root  => 0
  | .brA p => p.depth + 1
  | .brB p => p.depth + 1
  | .brC p => p.depth + 1

/-- Compute the triple at a given tree path. -/
def tripleAt : BPath -> Int x Int x Int
  | .root  => (3, 4, 5)
  | .brA p => let (a, b, c) := tripleAt p
              (a - 2*b + 2*c, 2*a - b + 2*c, 2*a - 2*b + 3*c)
  | .brB p => let (a, b, c) := tripleAt p
              (a + 2*b + 2*c, 2*a + b + 2*c, 2*a + 2*b + 3*c)
  | .brC p => let (a, b, c) := tripleAt p
              (-a + 2*b + 2*c, -2*a + b + 2*c, -2*a + 2*b + 3*c)

/-- The hypotenuse at a given tree path. -/
def hypAt (p : BPath) : Int := (tripleAt p).2.2

/-- Helper lemma: the triple components satisfy the auxiliary equation. -/
private theorem tripleAt_pyth_aux (p : BPath) :
    (tripleAt p).1 ^ 2 + (tripleAt p).2.1 ^ 2 = (tripleAt p).2.2 ^ 2 := by
  induction p with
  | root => native_decide
  | brA p ih =>
    simp only [tripleAt]
    set a := (tripleAt p).1
    set b := (tripleAt p).2.1
    set c := (tripleAt p).2.2
    nlinarith [ih]
  | brB p ih =>
    simp only [tripleAt]
    set a := (tripleAt p).1
    set b := (tripleAt p).2.1
    set c := (tripleAt p).2.2
    nlinarith [ih]

-- [... 128 more lines omitted for brevity ...]
-- See the full source in lean/01_BerggrenLorentzCorrespondence.lean
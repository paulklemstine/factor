import Mathlib

/-!
# Berggren Pythagorean Triple Tree

The Berggren tree (Berggren 1934, Hall 1970, Barning 1963) generates **all** primitive
Pythagorean triples from the root triple (3, 4, 5) by applying three linear transformations.

Each node (a, b, c) with a² + b² = c² produces three children via matrices:
- **M₁**: (a - 2b + 2c, 2a - b + 2c, 2a - 2b + 3c)
- **M₂**: (a + 2b + 2c, 2a + b + 2c, 2a + 2b + 3c)
- **M₃**: (-a + 2b + 2c, -2a + b + 2c, -2a + 2b + 3c)

## Main results

- `berggren_A_pyth`, `berggren_B_pyth`, `berggren_C_pyth`: Each transformation preserves
  the Pythagorean property a² + b² = c².
- `BerggrenTree`: The inductive ternary tree of all reachable triples.
- `berggrenTripleAux_pyth`: Every triple in the tree satisfies the Pythagorean equation.
-/

/-- A Pythagorean triple (a, b, c) over ℤ satisfying a² + b² = c². -/
structure PythTriple where
  a : ℤ
  b : ℤ
  c : ℤ
  pyth : a ^ 2 + b ^ 2 = c ^ 2

instance : Repr PythTriple where
  reprPrec t _ := s!"({t.a}, {t.b}, {t.c})"

/-- Berggren matrix M₁ preserves the Pythagorean property. -/
theorem berggren_A_pyth_eq (a b c : ℤ) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    (a - 2 * b + 2 * c) ^ 2 + (2 * a - b + 2 * c) ^ 2 =
    (2 * a - 2 * b + 3 * c) ^ 2 := by
  nlinarith

/-- Berggren matrix M₂ preserves the Pythagorean property. -/
theorem berggren_B_pyth_eq (a b c : ℤ) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    (a + 2 * b + 2 * c) ^ 2 + (2 * a + b + 2 * c) ^ 2 =
    (2 * a + 2 * b + 3 * c) ^ 2 := by
  nlinarith

/-- Berggren matrix M₃ preserves the Pythagorean property. -/
theorem berggren_C_pyth_eq (a b c : ℤ) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    (-a + 2 * b + 2 * c) ^ 2 + (-2 * a + b + 2 * c) ^ 2 =
    (-2 * a + 2 * b + 3 * c) ^ 2 := by
  nlinarith

/-- The root of the Berggren tree: the triple (3, 4, 5). -/
def rootTriple : PythTriple where
  a := 3
  b := 4
  c := 5
  pyth := by norm_num

/-- A path in the ternary Berggren tree. -/
inductive TreePath where
  | root : TreePath
  | left  : TreePath → TreePath   -- apply M₁
  | mid   : TreePath → TreePath   -- apply M₂
  | right : TreePath → TreePath   -- apply M₃
  deriving Repr

/-- The depth of a tree path. -/
def TreePath.depth : TreePath → ℕ
  | .root    => 0
  | .left p  => p.depth + 1
  | .mid p   => p.depth + 1
  | .right p => p.depth + 1

/-- Computable version of the Berggren triple at a given tree path.
    Returns (a, b, c) where a² + b² = c². -/
def berggrenTripleAux : TreePath → ℤ × ℤ × ℤ
  | .root    => (3, 4, 5)
  | .left p  =>
    let (a, b, c) := berggrenTripleAux p
    (a - 2 * b + 2 * c, 2 * a - b + 2 * c, 2 * a - 2 * b + 3 * c)
  | .mid p   =>
    let (a, b, c) := berggrenTripleAux p
    (a + 2 * b + 2 * c, 2 * a + b + 2 * c, 2 * a + 2 * b + 3 * c)
  | .right p =>
    let (a, b, c) := berggrenTripleAux p
    (-a + 2 * b + 2 * c, -2 * a + b + 2 * c, -2 * a + 2 * b + 3 * c)

/-- Extract the first component. -/
def berggrenA (p : TreePath) : ℤ := (berggrenTripleAux p).1

/-- Extract the second component. -/
def berggrenB (p : TreePath) : ℤ := (berggrenTripleAux p).2.1

/-- Extract the third component (hypotenuse). -/
def berggrenC (p : TreePath) : ℤ := (berggrenTripleAux p).2.2

/-
PROBLEM
Every triple produced by `berggrenTripleAux` satisfies a² + b² = c².

PROVIDED SOLUTION
Induction on the tree path. Base case: (3,4,5) satisfies 9+16=25 by norm_num.
For each recursive case (left/mid/right), unfold berggrenA/berggrenB/berggrenC
 and berggrenTripleAux, then use the inductive hypothesis and nlinarith
 (or ring_nf; nlinarith) to verify the algebraic identity.
-/
theorem berggrenTripleAux_pyth (p : TreePath) :
    (berggrenA p) ^ 2 + (berggrenB p) ^ 2 = (berggrenC p) ^ 2 := by
  -- We can prove this by induction on the tree path.
  induction p with
  | root => rfl
  | left p ih =>
  convert berggren_A_pyth_eq ( berggrenA p ) ( berggrenB p ) ( berggrenC p ) ih using 1
  | mid p hp =>
  convert berggren_B_pyth_eq ( berggrenA p ) ( berggrenB p ) ( berggrenC p ) hp using 1
  | right p hp => convert
  berggren_C_pyth_eq ( berggrenA p ) ( berggrenB p ) ( berggrenC p ) hp using 1

/-- The set of all triples reachable at depth ≤ d. -/
def treeTriplesAtDepth (d : ℕ) : Set (ℤ × ℤ × ℤ) :=
  { t | ∃ p : TreePath, p.depth ≤ d ∧ berggrenTripleAux p = t }

/-!
## Key algebraic properties of the Berggren transformations

The Berggren matrices preserve:
1. The Pythagorean property (proved above)
2. Primitivity (gcd(a,b,c) = 1)
3. Positivity of all components (when starting from positive triples)

The tree is **complete**: every primitive Pythagorean triple with a odd, b even
appears exactly once.
-/

/-
PROBLEM
The Berggren M₁ transformation preserves the Pythagorean property (iff version).

PROVIDED SOLUTION
Both directions follow from expanding the squares and algebraic manipulation.
Use constructor, then nlinarith for each direction.
-/
theorem berggren_A_iff (a b c : ℤ) :
    (a - 2 * b + 2 * c) ^ 2 + (2 * a - b + 2 * c) ^ 2 =
    (2 * a - 2 * b + 3 * c) ^ 2 ↔ a ^ 2 + b ^ 2 = c ^ 2 := by
  grind

/-
PROBLEM
The Berggren M₂ transformation preserves the Pythagorean property (iff version).

PROVIDED SOLUTION
Both directions follow from expanding the squares and algebraic manipulation.
Use constructor, then nlinarith for each direction.
-/
theorem berggren_B_iff (a b c : ℤ) :
    (a + 2 * b + 2 * c) ^ 2 + (2 * a + b + 2 * c) ^ 2 =
    (2 * a + 2 * b + 3 * c) ^ 2 ↔ a ^ 2 + b ^ 2 = c ^ 2 := by
  constructor <;> intro h <;> linarith [ berggren_B_pyth_eq a b c ( by linarith ) ]

/-
PROBLEM
The Berggren M₃ transformation preserves the Pythagorean property (iff version).

PROVIDED SOLUTION
Both directions follow from expanding the squares and algebraic manipulation.
Use constructor, then nlinarith for each direction.
-/
theorem berggren_C_iff (a b c : ℤ) :
    (-a + 2 * b + 2 * c) ^ 2 + (-2 * a + b + 2 * c) ^ 2 =
    (-2 * a + 2 * b + 3 * c) ^ 2 ↔ a ^ 2 + b ^ 2 = c ^ 2 := by
  constructor <;> intro h <;> linarith [ berggren_C_pyth_eq a b c ( by linarith ) ]

/-!
## Computational examples

We can evaluate the tree to verify it generates known triples.
-/

#eval berggrenTripleAux .root                           -- (3, 4, 5)
#eval berggrenTripleAux (.left .root)                   -- (5, 12, 13)
#eval berggrenTripleAux (.mid .root)                    -- (21, 20, 29)
#eval berggrenTripleAux (.right .root)                  -- (15, 8, 17)
#eval berggrenTripleAux (.left (.left .root))           -- (7, 24, 25)
#eval berggrenTripleAux (.mid (.left .root))            -- (55, 48, 73)
#eval berggrenTripleAux (.right (.left .root))          -- (45, 28, 53)

/-- At depth d, the hypotenuse c of the M₂ child satisfies c' = 2a + 2b + 3c ≥ 3c
    when a, b > 0. This implies exponential growth: max hypotenuse at depth d ≥ 3^d · 5. -/
theorem hypotenuse_growth (a b c : ℤ) (ha : 0 < a) (hb : 0 < b) :
    2 * a + 2 * b + 3 * c ≥ 3 * c := by
  linarith

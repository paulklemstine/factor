import Mathlib

/-!
# The Berggren-Lorentz Correspondence: Machine-Verified Proofs

This file contains the formally verified core theorems for the paper
"The Berggren-Lorentz Correspondence: Machine-Verified Connections
Between Pythagorean Trees, Hyperbolic Geometry, and Integer Factoring"

## Main Results

1. **Lorentz Form Preservation** (Theorem 3.1): The Berggren matrices preserve Q(a,b,c) = a?+b?-c?
2. **Pythagorean Preservation** (Theorem 3.2): Tree nodes satisfy a?+b?=c?
3. **Tree Soundness** (Theorem 3.3): Every reachable triple is Pythagorean
4. **Factoring Identity** (Theorem 3.4): (c-b)(c+b) = a?
5. **Euclid Parametrization** (Theorem 3.5): (m?-n?)?+(2mn)?=(m?+n?)?
6. **Pell Recurrence** (Theorem 4.1): B-branch satisfies c_{n+2} = 6c_{n+1} - c_n
7. **A-branch Descent** (Theorem 4.4): Consecutive parameters descend by pure A-steps
8. **Determinants**: det(B_A)=1, det(B_B)=-1, det(B_C)=1

All proofs are machine-checked with clean axiom audit (no sorry, no custom axioms).
-/

open Matrix

/-! ## Section 1: Matrix Definitions -/

/-- Berggren matrix B_A (first generator) -/
def BA : Matrix (Fin 3) (Fin 3) Int :=
  !![1, -2, 2; 2, -1, 2; 2, -2, 3]

/-- Berggren matrix B_B (second generator) -/
def BB : Matrix (Fin 3) (Fin 3) Int :=
  !![1, 2, 2; 2, 1, 2; 2, 2, 3]

/-- Berggren matrix B_C (third generator) -/
def BC : Matrix (Fin 3) (Fin 3) Int :=
  !![(-1), 2, 2; (-2), 1, 2; (-2), 2, 3]

/-- The Lorentz metric matrix: diag(1, 1, -1) -/
def QLorentz : Matrix (Fin 3) (Fin 3) Int :=
  !![1, 0, 0; 0, 1, 0; 0, 0, (-1)]

/-! ## Section 2: Lorentz Form Preservation (Theorem 3.1)

The three Berggren matrices are elements of O(2,1;Int), the integer Lorentz group.
This means they preserve the quadratic form Q(a,b,c) = a? + b? - c?. -/

/-- **Theorem 3.1a**: B_A preserves the Lorentz form: B_A? Q B_A = Q -/
theorem BA_preserves_lorentz : BA? * QLorentz * BA = QLorentz := by
  native_decide

/-- **Theorem 3.1b**: B_B preserves the Lorentz form: B_B? Q B_B = Q -/
theorem BB_preserves_lorentz : BB? * QLorentz * BB = QLorentz := by
  native_decide

/-- **Theorem 3.1c**: B_C preserves the Lorentz form: B_C? Q B_C = Q -/
theorem BC_preserves_lorentz : BC? * QLorentz * BC = QLorentz := by
  native_decide

/-! ## Section 3: Determinants -/

/-- det(B_A) = 1: B_A is in SO(2,1;Int) -/
theorem det_BA : Matrix.det BA = 1 := by decide

/-- det(B_B) = -1: B_B reverses orientation -/
theorem det_BB : Matrix.det BB = -1 := by decide

/-- det(B_C) = 1: B_C is in SO(2,1;Int) -/
theorem det_BC : Matrix.det BC = 1 := by decide

/-! ## Section 4: Pythagorean Preservation (Theorem 3.2)

If (a,b,c) satisfies a? + b? = c?, then the image under each Berggren
matrix also satisfies the Pythagorean equation. -/

/-- **Theorem 3.2a**: B_A preserves the Pythagorean equation -/
theorem BA_preserves_pyth (a b c : Int) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    (a - 2*b + 2*c) ^ 2 + (2*a - b + 2*c) ^ 2 = (2*a - 2*b + 3*c) ^ 2 := by
  nlinarith [sq_nonneg (a - b), sq_nonneg (a + b)]

/-- **Theorem 3.2b**: B_B preserves the Pythagorean equation -/
theorem BB_preserves_pyth (a b c : Int) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    (a + 2*b + 2*c) ^ 2 + (2*a + b + 2*c) ^ 2 = (2*a + 2*b + 3*c) ^ 2 := by
  nlinarith [sq_nonneg (a - b), sq_nonneg (a + b)]

/-- **Theorem 3.2c**: B_C preserves the Pythagorean equation -/
theorem BC_preserves_pyth (a b c : Int) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    (-a + 2*b + 2*c) ^ 2 + (-2*a + b + 2*c) ^ 2 = (-2*a + 2*b + 3*c) ^ 2 := by
  nlinarith [sq_nonneg (a - b), sq_nonneg (a + b)]

/-! ## Section 5: Tree Soundness (Theorem 3.3) -/

/-- A path in the ternary Berggren tree. -/
inductive BerggrenPath where
  | root : BerggrenPath
  | stepA : BerggrenPath -> BerggrenPath
  | stepB : BerggrenPath -> BerggrenPath
  | stepC : BerggrenPath -> BerggrenPath

/-- The triple at a given Berggren tree path. -/
def tripleAt : BerggrenPath -> Int x Int x Int
  | .root => (3, 4, 5)
  | .stepA p =>
    let (a, b, c) := tripleAt p
    (a - 2*b + 2*c, 2*a - b + 2*c, 2*a - 2*b + 3*c)
  | .stepB p =>
    let (a, b, c) := tripleAt p
    (a + 2*b + 2*c, 2*a + b + 2*c, 2*a + 2*b + 3*c)
  | .stepC p =>
    let (a, b, c) := tripleAt p
    (-a + 2*b + 2*c, -2*a + b + 2*c, -2*a + 2*b + 3*c)

/-
**Theorem 3.3**: Every triple produced by the Berggren tree satisfies a?+b?=c?.
-/
theorem tripleAt_is_pythagorean (p : BerggrenPath) :
    let (a, b, c) := tripleAt p
    a ^ 2 + b ^ 2 = c ^ 2 := by
      induction' p with p hp;
      . exact Int.neg_inj.mp rfl;
      . convert BA_preserves_pyth _ _ _ hp using 1;
      . rename_i p ih;
        convert BB_preserves_pyth _ _ _ ih using 1;
      . rename_i p ih;
        convert BC_preserves_pyth _ _ _ ih using 1

/-! ## Section 6: Factoring Identity (Theorem 3.4) -/

/-- **Theorem 3.4**: The factoring identity (c-b)(c+b) = a? -/
theorem factoring_identity (a b c : Int) (h : a ^ 2 + b ^ 2 = c ^ 2) :
    (c - b) * (c + b) = a ^ 2 := by
  nlinarith

/-! ## Section 7: Euclid Parametrization (Theorem 3.5) -/

/-- **Theorem 3.5**: Euclid's parametrization always produces Pythagorean triples -/
theorem euclid_parametrization (m n : Int) :
    (m ^ 2 - n ^ 2) ^ 2 + (2 * m * n) ^ 2 = (m ^ 2 + n ^ 2) ^ 2 := by
  ring

/-! ## Section 8: Pell Recurrence (Theorem 4.1)

The B-branch hypotenuse sequence satisfies c_{n+2} = 6c_{n+1} - c_n. -/

/-- The hypotenuse along the pure B-branch path. -/
def pellHyp : Nat -> Int
  | 0 => 5
  | 1 => 29
  | (n + 2) => 6 * pellHyp (n + 1) - pellHyp n

-- [... 86 more lines omitted for brevity ...]
-- See the full source in lean/05_BerggrenLorentzPaperProofs.lean
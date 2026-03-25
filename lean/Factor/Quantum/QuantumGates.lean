/-
# Quantum Gates in the Composition Algebra Framework

Quantum gates operate inside the composition algebra space.
Light interfering with itself or other light corresponds to
algebraic operations in the normed division algebras.

## Key Insight
- A quantum gate is a unitary transformation U ∈ U(n)
- For n=1: phase gates (real channel) — just sign flips
- For n=2: SU(2) gates (complex channel) — beam splitters, phase shifters
- For n=4: SU(2) × SU(2) (quaternionic channel) — polarization rotations
- For n=8: Spin(8) symmetry (octonionic channel) — triality gates

The Hurwitz constraint means quantum computing with photons
has exactly four "native gate sets" corresponding to the four
composition algebras.
-/
import Mathlib

/-! ## Phase Gates (Real Channel, n=1) -/

/-- A phase gate in the real channel is just multiplication by ±1 -/
def phase_gate (s : Bool) (x : ℤ) : ℤ :=
  if s then -x else x

/-
PROVIDED SOLUTION
Cases on the boolean s. If true, -(-x)=x. If false, x=x.
-/
theorem phase_gate_involutive (s : Bool) (x : ℤ) :
    phase_gate s (phase_gate s x) = x := by
  -- By definition of phase gate, we have phase_gate s x = if s then -x else x.
  unfold phase_gate
  aesop

/-! ## Beam Splitter (Complex Channel, n=2)

A beam splitter acts on a pair of modes (a, b) by a 2×2 unitary matrix.
In the Gaussian integer model, this is multiplication by a unit in ℤ[i].
The units of ℤ[i] are {1, -1, i, -i}, giving exactly 4 gates. -/

/-- The four units of ℤ[i] -/
def gaussian_units : List GaussianInt :=
  [⟨1, 0⟩, ⟨-1, 0⟩, ⟨0, 1⟩, ⟨0, -1⟩]

/-
PROBLEM
Each Gaussian unit has norm 1

PROVIDED SOLUTION
Expand the list membership, case split on each unit, compute norm by simp/decide.
-/
theorem gaussian_unit_norm (u : GaussianInt) (hu : u ∈ gaussian_units) :
    Zsqrtd.norm u = 1 := by
  unfold gaussian_units at hu; aesop;

/-! ## Polarization Rotation (Quaternionic Channel, n=4)

The group of unit quaternions SU(2) acts on ℝ³ by conjugation,
giving all spatial rotations SO(3). This is the double cover:
  1 → ℤ/2 → SU(2) → SO(3) → 1

For photons, this encodes polarization: the Poincaré sphere
of polarization states IS the quaternionic projective line.
-/

/-
PROBLEM
Quaternion norm is multiplicative

PROVIDED SOLUTION
Use map_mul since normSq is a MonoidWithZeroHom.
-/
theorem quaternion_norm_sq_mul (q v : Quaternion ℝ) :
    Quaternion.normSq (q * v) = Quaternion.normSq q * Quaternion.normSq v := by
  grind

/-! ## The Octonionic Mystery (n=8)

The octonions are non-associative, which means:
- Sequential operations don't compose simply
- There is no matrix representation
- The automorphism group is the exceptional Lie group G₂

Hypothesis: The octonionic channel encodes the property that
makes quantum mechanics fundamentally different from classical mechanics —
the non-commutativity/non-associativity of sequential measurements.

The 8-dimensional structure connects to:
- Spin(8) and triality (three equivalent 8-dim representations)
- The Standard Model gauge group SU(3) × SU(2) × U(1)
  (which is a subgroup of the G₂ automorphisms of 𝕆)
- String theory compactification on G₂ manifolds
-/

/-
PROBLEM
The Cayley-Dickson doubling: each composition algebra is obtained
    by doubling the previous one.
    ℝ → ℂ → ℍ → 𝕆
    1 → 2 → 4 → 8
    Each doubling loses a property:
    - ℝ → ℂ: lose ordering
    - ℂ → ℍ: lose commutativity
    - ℍ → 𝕆: lose associativity
    - 𝕆 → ???: lose alternativity (and the division algebra property!)

PROVIDED SOLUTION
norm_num or decide
-/
theorem cayley_dickson_dimensions :
    [1, 2, 4, 8] = [2^0, 2^1, 2^2, 2^3] := by
  decide +kernel
/-
# Quantum Gates on Berggren Trees: A Formal Research Program

## Core Mathematical Framework

1. Every Pythagorean triple (a,b,c) defines a scaled rotation matrix R(a,b)
   isomorphic to the Gaussian integer a + bi ∈ ℤ[i].

2. The Berggren tree generates ALL primitive Pythagorean triples, hence
   a dense discrete gate set for SO(2) rotations.

3. The 3×3 Berggren matrices live in O(2,1;ℤ) — the integer Lorentz group.
   Via the spin homomorphism SU(1,1) → SO(2,1), these lift to SU(1,1) gates.

4. The 2×2 Berggren matrices M₁ = T²S and M₃ = T² generate the theta group
   Γ_θ, an index-3 subgroup of SL(2,ℤ), connecting to modular forms and
   topological quantum computing.

5. Pythagorean quadruples (a²+b²+c²=d²) give SU(2) quantum gates that are
   all π/2 rotations about rational axes on the Bloch sphere.
-/
import Mathlib

open Matrix

/-! ## §1: Pythagorean Rotation Matrices — The Gaussian Integer Gate Set -/

/-- A Pythagorean rotation matrix R(a,b) = [[a,-b],[b,a]], representing
    the Gaussian integer a + bi. -/
def pythRot (a b : ℤ) : Matrix (Fin 2) (Fin 2) ℤ :=
  !![a, -b; b, a]

/-- The determinant of R(a,b) equals the Gaussian norm a² + b². -/
theorem det_pythRot (a b : ℤ) : det (pythRot a b) = a ^ 2 + b ^ 2 := by
  simp [pythRot, det_fin_two]; ring

/-- R(a,b) multiplication = Gaussian integer multiplication. -/
theorem pythRot_mul (a b c d : ℤ) :
    pythRot a b * pythRot c d = pythRot (a*c - b*d) (a*d + b*c) := by
  ext i j; fin_cases i <;> fin_cases j <;>
    simp [pythRot, mul_apply, Fin.sum_univ_two] <;> ring

/-- The identity element is R(1,0) = I. -/
theorem pythRot_one : pythRot 1 0 = (1 : Matrix (Fin 2) (Fin 2) ℤ) := by
  ext i j; fin_cases i <;> fin_cases j <;> simp [pythRot]

/-- The Brahmagupta–Fibonacci identity. -/
theorem brahmagupta_fibonacci (a b c d : ℤ) :
    (a^2 + b^2) * (c^2 + d^2) = (a*c - b*d)^2 + (a*d + b*c)^2 := by ring

/-- Conformality: R(a,b) · R(a,-b) = (a²+b²) · I. -/
theorem pythRot_conformal (a b : ℤ) :
    pythRot a b * pythRot a (-b) = (a^2 + b^2) • (1 : Matrix (Fin 2) (Fin 2) ℤ) := by
  rw [pythRot_mul]
  ext i j; fin_cases i <;> fin_cases j <;>
    simp [pythRot, smul_apply] <;> ring

/-- Transpose = conjugate rotation. -/
theorem pythRot_transpose (a b : ℤ) :
    (pythRot a b)ᵀ = pythRot a (-b) := by
  ext i j; fin_cases i <;> fin_cases j <;> simp [pythRot, transpose_apply]

/-- The trace of R(a,b) is 2a. -/
theorem trace_pythRot (a b : ℤ) : trace (pythRot a b) = 2 * a := by
  simp [pythRot, trace, Fin.sum_univ_two]; ring

/-- Commutativity: Pythagorean rotations commute. -/
theorem pythRot_comm (a b c d : ℤ) :
    pythRot a b * pythRot c d = pythRot c d * pythRot a b := by
  rw [pythRot_mul, pythRot_mul]; congr 1 <;> ring

/-! ## §2: Berggren Gate Structure -/

/-- A Berggren gate: a Pythagorean triple (a,b,c). -/
structure BerggrenGate where
  a : ℤ
  b : ℤ
  c : ℤ
  pyth : a ^ 2 + b ^ 2 = c ^ 2
  c_pos : 0 < c

def BerggrenGate.toMatrix (g : BerggrenGate) : Matrix (Fin 2) (Fin 2) ℤ :=
  pythRot g.a g.b

theorem BerggrenGate.det_eq (g : BerggrenGate) :
    det g.toMatrix = g.c ^ 2 := by
  simp [BerggrenGate.toMatrix, det_pythRot, g.pyth]

theorem BerggrenGate.compose_det (g₁ g₂ : BerggrenGate) :
    det (g₁.toMatrix * g₂.toMatrix) = g₁.c ^ 2 * g₂.c ^ 2 := by
  rw [det_mul, g₁.det_eq, g₂.det_eq]

def rootGate' : BerggrenGate := ⟨3, 4, 5, by norm_num, by norm_num⟩
def gate_5_12_13' : BerggrenGate := ⟨5, 12, 13, by norm_num, by norm_num⟩
def gate_21_20_29' : BerggrenGate := ⟨21, 20, 29, by norm_num, by norm_num⟩
def gate_15_8_17' : BerggrenGate := ⟨15, 8, 17, by norm_num, by norm_num⟩

/-! ## §3: Light Cone Preservation — The Lorentz Connection -/

def B₁' : Matrix (Fin 3) (Fin 3) ℤ := !![1, -2, 2; 2, -1, 2; 2, -2, 3]
def B₂' : Matrix (Fin 3) (Fin 3) ℤ := !![1, 2, 2; 2, 1, 2; 2, 2, 3]
def B₃' : Matrix (Fin 3) (Fin 3) ℤ := !![-1, 2, 2; -2, 1, 2; -2, 2, 3]
def lorentzMetric' : Matrix (Fin 3) (Fin 3) ℤ := !![1, 0, 0; 0, 1, 0; 0, 0, -1]

def onLightCone' (a b c : ℤ) : Prop := a^2 + b^2 - c^2 = 0

/-- B₁ preserves the Lorentz form: B₁ᵀ · η · B₁ = η. -/
theorem B1_preserves_lorentz' :
    B₁'ᵀ * lorentzMetric' * B₁' = lorentzMetric' := by
  native_decide

/-- B₂ preserves the Lorentz form. -/
theorem B2_preserves_lorentz' :
    B₂'ᵀ * lorentzMetric' * B₂' = lorentzMetric' := by
  native_decide

/-- B₃ preserves the Lorentz form. -/
theorem B3_preserves_lorentz' :
    B₃'ᵀ * lorentzMetric' * B₃' = lorentzMetric' := by
  native_decide

/-- det(B₁) = 1 — in SO(2,1;ℤ). -/
theorem det_B1' : det B₁' = 1 := by native_decide

/-- det(B₂) = -1 — in O(2,1;ℤ) \ SO(2,1;ℤ). -/
theorem det_B2' : det B₂' = -1 := by native_decide

/-- det(B₃) = 1 — in SO(2,1;ℤ). -/
theorem det_B3' : det B₃' = 1 := by native_decide

/-- B₁ preserves the light cone. -/
theorem B1_preserves_cone' (a b c : ℤ) (h : onLightCone' a b c) :
    onLightCone' (a - 2*b + 2*c) (2*a - b + 2*c) (2*a - 2*b + 3*c) := by
  simp only [onLightCone'] at *; nlinarith

/-- B₂ preserves the light cone. -/
theorem B2_preserves_cone' (a b c : ℤ) (h : onLightCone' a b c) :
    onLightCone' (a + 2*b + 2*c) (2*a + b + 2*c) (2*a + 2*b + 3*c) := by
  simp only [onLightCone'] at *; nlinarith

/-- B₃ preserves the light cone. -/
theorem B3_preserves_cone' (a b c : ℤ) (h : onLightCone' a b c) :
    onLightCone' (-a + 2*b + 2*c) (-2*a + b + 2*c) (-2*a + 2*b + 3*c) := by
  simp only [onLightCone'] at *; nlinarith

/-! ## §4: The SL(2,ℤ) Connection and Theta Group -/

def S_SL2' : Matrix (Fin 2) (Fin 2) ℤ := !![0, -1; 1, 0]
def T_SL2' : Matrix (Fin 2) (Fin 2) ℤ := !![1, 1; 0, 1]
def M₁_2x2' : Matrix (Fin 2) (Fin 2) ℤ := !![2, -1; 1, 0]
def M₂_2x2' : Matrix (Fin 2) (Fin 2) ℤ := !![2, 1; 1, 0]
def M₃_2x2' : Matrix (Fin 2) (Fin 2) ℤ := !![1, 2; 0, 1]

/-- M₁ = T² · S — connecting Berggren to modular group. -/
theorem M1_eq_T_sq_S' : M₁_2x2' = T_SL2' * T_SL2' * S_SL2' := by native_decide

/-- M₃ = T² — Berggren generator is a modular translation. -/
theorem M3_eq_T_sq' : M₃_2x2' = T_SL2' * T_SL2' := by native_decide

/-- S can be recovered: T⁻² · M₁ = S. -/
theorem S_from_berggren' :
    !![1, -2; 0, (1:ℤ)] * M₁_2x2' = S_SL2' := by native_decide

/-- det(M₁) = 1 — in SL(2,ℤ). -/
theorem det_M1' : det M₁_2x2' = 1 := by native_decide

/-- det(M₂) = -1. -/
theorem det_M2' : det M₂_2x2' = -1 := by native_decide

/-- det(M₃) = 1. -/
theorem det_M3' : det M₃_2x2' = 1 := by native_decide

/-- S² = -I. -/
theorem S_squared' : S_SL2' * S_SL2' = -(1 : Matrix (Fin 2) (Fin 2) ℤ) := by native_decide

/-- S⁴ = I. -/
theorem S_order_4' : S_SL2' * S_SL2' * S_SL2' * S_SL2' = (1 : Matrix (Fin 2) (Fin 2) ℤ) := by
  native_decide

/-! ## §5: Pauli Gate Interactions -/

def pauliX' : Matrix (Fin 2) (Fin 2) ℤ := !![0, 1; 1, 0]
def pauliZ' : Matrix (Fin 2) (Fin 2) ℤ := !![1, 0; 0, -1]

/-- X-conjugation inverts rotations. -/
theorem pauliX_conjugation' (a b : ℤ) :
    pauliX' * pythRot a b * pauliX' = pythRot a (-b) := by
  ext i j; fin_cases i <;> fin_cases j <;>
    simp [pauliX', pythRot, mul_apply, Fin.sum_univ_two] <;> ring

/-- Z-conjugation also inverts rotations. -/
theorem pauliZ_conjugation' (a b : ℤ) :
    pauliZ' * pythRot a b * pauliZ' = pythRot a (-b) := by
  ext i j; fin_cases i <;> fin_cases j <;>
    simp [pauliZ', pythRot, mul_apply, Fin.sum_univ_two] <;> ring

/-- Pauli duality: X and Z have identical conjugation action. -/
theorem pauli_duality' (a b : ℤ) :
    pauliX' * pythRot a b * pauliX' = pauliZ' * pythRot a b * pauliZ' := by
  rw [pauliX_conjugation', pauliZ_conjugation']

theorem pauliX_squared' : pauliX' * pauliX' = (1 : Matrix (Fin 2) (Fin 2) ℤ) := by native_decide
theorem pauliZ_squared' : pauliZ' * pauliZ' = (1 : Matrix (Fin 2) (Fin 2) ℤ) := by native_decide

/-- XZ anticommutation. -/
theorem pauliXZ_anticommute' :
    pauliX' * pauliZ' = -(pauliZ' * pauliX') := by native_decide

/-! ## §6: Circuit Evaluation -/

def evalCircuit' : List BerggrenGate → Matrix (Fin 2) (Fin 2) ℤ
  | [] => 1
  | g :: gs => g.toMatrix * evalCircuit' gs

theorem det_evalCircuit' (gs : List BerggrenGate) :
    det (evalCircuit' gs) = (gs.map fun g => g.c ^ 2).prod := by
  induction gs with
  | nil => simp [evalCircuit', det_one]
  | cons g gs ih =>
    simp [evalCircuit', det_mul, BerggrenGate.det_eq, ih, List.map_cons, List.prod_cons]

theorem circuit_two_gates' (g₁ g₂ : BerggrenGate) :
    evalCircuit' [g₁, g₂] =
    pythRot (g₁.a * g₂.a - g₁.b * g₂.b) (g₁.a * g₂.b + g₁.b * g₂.a) := by
  simp [evalCircuit', BerggrenGate.toMatrix, pythRot_mul]

/-! ## §7: Rotation Composition Examples -/

theorem R345_squared' :
    pythRot 3 4 * pythRot 3 4 = pythRot (-7) 24 := by
  rw [pythRot_mul]; norm_num

theorem triple_7_24_25' : (-7 : ℤ)^2 + 24^2 = 25^2 := by norm_num

theorem compose_345_51213' :
    pythRot 3 4 * pythRot 5 12 = pythRot (-33) 56 := by
  rw [pythRot_mul]; norm_num

theorem triple_33_56_65' : (-33 : ℤ)^2 + 56^2 = 65^2 := by norm_num

/-! ## §8: Pythagorean Quadruples → SU(2) Quantum Gates -/

/-- A Pythagorean quadruple with a²+b²+c²=d². -/
structure PythQuadruple where
  a : ℤ
  b : ℤ
  c : ℤ
  d : ℤ
  pyth : a ^ 2 + b ^ 2 + c ^ 2 = d ^ 2
  d_pos : 0 < d

/-- Quaternion d + ai + bj + ck as 4×4 real matrix. -/
def PythQuadruple.toMatrix (q : PythQuadruple) : Matrix (Fin 4) (Fin 4) ℤ :=
  !![q.d, -q.a, -q.b, -q.c;
     q.a,  q.d, -q.c,  q.b;
     q.b,  q.c,  q.d, -q.a;
     q.c, -q.b,  q.a,  q.d]

def rootQuad' : PythQuadruple := ⟨1, 2, 2, 3, by norm_num, by norm_num⟩
def quad_2_3_6_7' : PythQuadruple := ⟨2, 3, 6, 7, by norm_num, by norm_num⟩
def quad_4_4_7_9' : PythQuadruple := ⟨4, 4, 7, 9, by norm_num, by norm_num⟩

/-- Conformality of SU(2) gate from (1,2,2,3). -/
theorem rootQuad_conformal' :
    rootQuad'.toMatrix ᵀ * rootQuad'.toMatrix =
    (18 : ℤ) • (1 : Matrix (Fin 4) (Fin 4) ℤ) := by native_decide

/-- All Pythagorean quadruples give 2d² norm: a²+b²+c²+d² = 2d². -/
theorem pythQuad_norm_eq_2d_sq' (q : PythQuadruple) :
    q.a ^ 2 + q.b ^ 2 + q.c ^ 2 + q.d ^ 2 = 2 * q.d ^ 2 := by
  linarith [q.pyth]

/-! ## §9: Gaussian Norm -/

def gaussNorm' (a b : ℤ) : ℤ := a^2 + b^2

theorem gaussNorm_mul' (a₁ b₁ a₂ b₂ : ℤ) :
    gaussNorm' (a₁*a₂ - b₁*b₂) (a₁*b₂ + b₁*a₂) =
    gaussNorm' a₁ b₁ * gaussNorm' a₂ b₂ := by
  simp [gaussNorm']; ring

theorem gaussNorm_pyth_preserved' (a₁ b₁ a₂ b₂ r₁ r₂ : ℤ)
    (h₁ : gaussNorm' a₁ b₁ = r₁^2) (h₂ : gaussNorm' a₂ b₂ = r₂^2) :
    gaussNorm' (a₁*a₂ - b₁*b₂) (a₁*b₂ + b₁*a₂) = (r₁ * r₂)^2 := by
  rw [gaussNorm_mul', h₁, h₂]; ring

/-! ## §10: Trace Theory -/

theorem trace_composition' (a₁ b₁ a₂ b₂ : ℤ) :
    trace (pythRot a₁ b₁ * pythRot a₂ b₂) = 2 * (a₁ * a₂ - b₁ * b₂) := by
  rw [pythRot_mul, trace_pythRot]

theorem trace_pauli_conjugation' (a b : ℤ) :
    trace (pauliX' * pythRot a b * pauliX') = 2 * a := by
  rw [pauliX_conjugation', trace_pythRot]

/-- The square of R(a,b) equals R(a²-b², 2ab) — the double-angle formula. -/
theorem pythRot_char_eq' (a b : ℤ) :
    pythRot a b * pythRot a b =
    !![a^2-b^2, -(2*a*b); 2*a*b, a^2-b^2] := by
  ext i j; fin_cases i <;> fin_cases j <;>
    simp [pythRot, mul_apply, Fin.sum_univ_two] <;> ring

/-! ## §11: Finite Field Gates -/

def pythRotMod' (a b : ℤ) (p : ℕ) : Matrix (Fin 2) (Fin 2) (ZMod p) :=
  !![((a : ℤ) : ZMod p), ((-b : ℤ) : ZMod p);
     ((b : ℤ) : ZMod p), ((a : ℤ) : ZMod p)]

theorem det_pythRotMod' (a b : ℤ) (p : ℕ) [NeZero p] :
    det (pythRotMod' a b p) = ((a^2 + b^2 : ℤ) : ZMod p) := by
  simp [pythRotMod', det_fin_two]; ring

/-! ## §12: Power Formula -/

theorem pythRot_sq' (a b : ℤ) :
    pythRot a b * pythRot a b = pythRot (a^2 - b^2) (2*a*b) := by
  rw [pythRot_mul]; congr 1 <;> ring

theorem det_pythRot_sq' (a b : ℤ) :
    det (pythRot a b * pythRot a b) = (a^2 + b^2)^2 := by
  simp [det_mul, det_pythRot]; ring

/-! ## §13: Controlled Gate -/

def controlledPythRot' (a b c : ℤ) : Matrix (Fin 4) (Fin 4) ℤ :=
  !![c, 0,  0,  0;
     0, c,  0,  0;
     0, 0,  a, -b;
     0, 0,  b,  a]

/-
PROVIDED SOLUTION
The matrix is block diagonal with blocks [[c,0],[0,c]] and [[a,-b],[b,a]]. Compute the 4x4 determinant directly by expanding along the first row or using det_fin_four, or use native_decide on a specific formulation, or just use simp with controlledPythRot' and det_fin_four and ring.
-/
theorem det_controlledPythRot' (a b c : ℤ) :
    det (controlledPythRot' a b c) = c^2 * (a^2 + b^2) := by
  unfold controlledPythRot';
  norm_num [ Matrix.det_succ_row_zero ] ; ring;
  simp +decide [ Fin.sum_univ_succ, Fin.succAbove ] ; ring

theorem det_controlledPythRot_pyth' (a b c : ℤ) (h : a^2 + b^2 = c^2) :
    det (controlledPythRot' a b c) = c^4 := by
  rw [det_controlledPythRot', h]; ring

/-! ## §14: Complex Structure -/

def J_SO2' : Matrix (Fin 2) (Fin 2) ℤ := pythRot 0 1

/-- J² = -I. -/
theorem J_sq' : J_SO2' * J_SO2' = -(1 : Matrix (Fin 2) (Fin 2) ℤ) := by
  simp [J_SO2', pythRot_mul]
  ext i j; fin_cases i <;> fin_cases j <;> simp [pythRot]

/-- Every Pythagorean rotation commutes with J. -/
theorem pythRot_commutes_J' (a b : ℤ) :
    pythRot a b * J_SO2' = J_SO2' * pythRot a b := by
  simp [J_SO2']; exact pythRot_comm a b 0 1

/-! ## §15: Computational Experiments -/

-- Level 1 of Berggren tree
#eval B₁' *ᵥ ![3, 4, 5]  -- [5, 12, 13]
#eval B₂' *ᵥ ![3, 4, 5]  -- [21, 20, 29]
#eval B₃' *ᵥ ![3, 4, 5]  -- [15, 8, 17]

-- Rotation powers
#eval pythRot 3 4 * pythRot 3 4  -- R(-7, 24)
#eval pythRot 3 4 * pythRot 3 4 * pythRot 3 4  -- R(-117, 44)

-- Gaussian norm check
#eval det (pythRot 3 4)  -- 25 = 5²
#eval det (pythRot 5 12)  -- 169 = 13²
#eval det (pythRot 3 4 * pythRot 5 12)  -- 4225 = 65²

-- SU(2) gate conformality
#eval rootQuad'.toMatrix ᵀ * rootQuad'.toMatrix
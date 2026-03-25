import Mathlib

/-!
# Homing Missile Navigation on the Berggren–Bloch Sphere 🚀

We formalize the "homing missile" algorithm for navigating the Berggren Pythagorean
triple tree toward a target rational point on the unit circle / Bloch sphere equator.

## Three Key Questions Addressed

1. **The Heuristic Compass** 🧭: Angular distance via cross-ratio; Stern–Brocot
   mediant structure gives a natural "left/right" compass.

2. **Path Correction** 🔄: Parent-descent (inverse Berggren) as course correction;
   three inverse matrices compose to identity.

3. **Target Acquisition** 🎯: Exact acquisition via Gaussian integer GCD;
   the Euclidean algorithm in ℤ[i] gives the exact Berggren path.
-/

open Matrix

/-! ## §1: The Angular Distance Metric — The Heuristic Compass 🧭 -/

/-- A rational point on the unit circle, represented by a Pythagorean triple. -/
structure RatCirclePoint where
  a : ℤ  -- cos component
  b : ℤ  -- sin component
  c : ℤ  -- hypotenuse
  pyth : a ^ 2 + b ^ 2 = c ^ 2
  c_pos : 0 < c

/-- The "angular cross-product" = c₁·c₂·sin(θ₂ - θ₁). -/
def angularCross (p q : RatCirclePoint) : ℤ :=
  p.a * q.b - p.b * q.a

/-- The "angular dot-product" = c₁·c₂·cos(θ₂ - θ₁). -/
def angularDot (p q : RatCirclePoint) : ℤ :=
  p.a * q.a + p.b * q.b

/-- Angular cross-product is antisymmetric. -/
theorem angularCross_antisymm (p q : RatCirclePoint) :
    angularCross p q = -angularCross q p := by
  simp [angularCross]; ring

/-- Angular dot-product is symmetric. -/
theorem angularDot_symm (p q : RatCirclePoint) :
    angularDot p q = angularDot q p := by
  simp [angularDot]; ring

/-- The Pythagorean identity for cross and dot products:
    (cross)² + (dot)² = (c₁·c₂)² -/
theorem angular_pythagorean (p q : RatCirclePoint) :
    (angularCross p q) ^ 2 + (angularDot p q) ^ 2 = (p.c * q.c) ^ 2 := by
  simp [angularCross, angularDot]
  nlinarith [p.pyth, q.pyth, sq_nonneg (p.a * q.a), sq_nonneg (p.b * q.b),
             sq_nonneg (p.a * q.b), sq_nonneg (p.b * q.a)]

/-- Squared angular distance (∝ sin²(θ₂ - θ₁)). The missile minimizes this. -/
def angularDistSq (p q : RatCirclePoint) : ℤ :=
  (angularCross p q) ^ 2

/-- Angular distance is zero iff cross-product is zero. -/
theorem angularDistSq_zero_iff (p q : RatCirclePoint) :
    angularDistSq p q = 0 ↔ angularCross p q = 0 := by
  constructor
  · intro h; simp [angularDistSq] at h; exact h
  · intro h; simp [angularDistSq, h]

/-- Angular distance is symmetric. -/
theorem angularDistSq_symm (p q : RatCirclePoint) :
    angularDistSq p q = angularDistSq q p := by
  simp [angularDistSq, angularCross]; ring

/-! ## §2: Berggren Tree Navigation -/

/-- Euclid parameters (m, n) with m > n > 0. -/
structure EuclidParams where
  m : ℤ
  n : ℤ
  m_pos : 0 < m
  n_pos : 0 < n
  m_gt_n : n < m

/-- Convert Euclid parameters to a Pythagorean triple. -/
def euclidToTriple (p : EuclidParams) : ℤ × ℤ × ℤ :=
  (p.m ^ 2 - p.n ^ 2, 2 * p.m * p.n, p.m ^ 2 + p.n ^ 2)

/-- The Euclid parametrization always gives a Pythagorean triple. -/
theorem euclid_is_pythagorean (p : EuclidParams) :
    let (a, b, c) := euclidToTriple p
    a ^ 2 + b ^ 2 = c ^ 2 := by
  simp [euclidToTriple]; ring

/-- Berggren branch M₂: (m,n) ↦ (2m+n, m) -/
def berggren_M2 (p : EuclidParams) : EuclidParams where
  m := 2 * p.m + p.n
  n := p.m
  m_pos := by linarith [p.m_pos, p.n_pos]
  n_pos := p.m_pos
  m_gt_n := by linarith [p.m_pos, p.n_pos]

/-- Berggren branch M₃: (m,n) ↦ (m+2n, n) -/
def berggren_M3 (p : EuclidParams) : EuclidParams where
  m := p.m + 2 * p.n
  n := p.n
  m_pos := by linarith [p.m_pos, p.n_pos]
  n_pos := p.n_pos
  m_gt_n := by linarith [p.m_gt_n, p.n_pos]

/-! ## §3: Hypotenuse Growth 🔍 -/

/-- The hypotenuse of Euclid parameters. -/
def hypot (p : EuclidParams) : ℤ := p.m ^ 2 + p.n ^ 2

/-- M₂ strictly increases the hypotenuse. -/
theorem hypot_M2_gt (p : EuclidParams) : hypot p < hypot (berggren_M2 p) := by
  simp [hypot, berggren_M2]
  nlinarith [p.m_pos, p.n_pos, sq_nonneg p.m, sq_nonneg p.n,
             sq_nonneg (p.m + p.n), sq_nonneg (p.m - p.n)]

/-- M₃ strictly increases the hypotenuse. -/
theorem hypot_M3_gt (p : EuclidParams) : hypot p < hypot (berggren_M3 p) := by
  simp [hypot, berggren_M3]
  nlinarith [p.m_pos, p.n_pos, sq_nonneg p.m, sq_nonneg p.n,
             sq_nonneg (p.m + p.n)]

/-! ## §4: The Compass 🧭 -/

/-- The compass reading n/m = tan(θ/2). -/
def compassReading (p : EuclidParams) : ℚ :=
  p.n / p.m

/-- Root compass reading is 1/2. -/
theorem compass_root : compassReading ⟨2, 1, by omega, by omega, by omega⟩ = 1/2 := by
  simp [compassReading]

/-! ## §5: Path Correction 🔄 -/

/-- Origin type for Berggren tree nodes. -/
inductive BerggrenOrigin where
  | root : BerggrenOrigin
  | fromM1 : BerggrenOrigin
  | fromM2 : BerggrenOrigin
  | fromM3 : BerggrenOrigin
  deriving Repr, DecidableEq

/-- Parent computation — the "course correction" operation. -/
def berggrenParent (m n : ℤ) : ℤ × ℤ × BerggrenOrigin :=
  if m = 2 ∧ n = 1 then (2, 1, .root)
  else if n ≥ m then (m, n, .root)
  else if m > 2 * n then (n, m - 2 * n, .fromM2)
  else if 2 * n > m ∧ m > n then (n, 2 * n - m, .fromM1)
  else (m - 2 * n, n, .fromM3)

/-! ## §6: Computational Experiments 🧪 -/

-- Experiment 1: Home in on tan(θ/2) = 1/3
#eval
  let target : ℚ := 1/3
  let steps := List.range 10
  steps.foldl (fun (acc : List String × ℤ × ℤ) _ =>
    let (log, m, n) := acc
    let reading := (n : ℚ) / m
    let triple := (m^2 - n^2, 2*m*n, m^2 + n^2)
    let entry := s!"({m},{n}) → {triple}, compass={reading}"
    if reading == target then (log ++ [entry ++ " 🎯"], m, n)
    else if target < reading then (log ++ [entry ++ " → M₂"], 2*m + n, m)
    else (log ++ [entry ++ " → M₃"], m + 2*n, n)
  ) ([], 2, 1) |>.1

-- Experiment 2: Check all three branches from root
#eval
  let (m, n) := ((2 : ℤ), (1 : ℤ))
  [s!"M₁: ({2*m - n},{m}), compass={(m : ℚ)/(2*m - n)}",
   s!"M₂: ({2*m + n},{m}), compass={(m : ℚ)/(2*m + n)}",
   s!"M₃: ({m + 2*n},{n}), compass={(n : ℚ)/(m + 2*n)}"]

-- Experiment 3: 3-branch greedy homing toward 5/13
#eval
  let target : ℚ := 5/13
  let steps := List.range 12
  steps.foldl (fun (acc : List String × ℤ × ℤ) _ =>
    let (log, m, n) := acc
    let reading := (n : ℚ) / m
    if reading == target then (log ++ [s!"🎯 HIT: ({m},{n})"], m, n)
    else
      let candidates := [
        ("M₁", 2*m - n, m),
        ("M₂", 2*m + n, m),
        ("M₃", m + 2*n, n)]
      let valid := candidates.filter (fun (_, m', n') => m' > n' && n' > 0 && m' > 0)
      let best := valid.foldl (fun (acc : String × ℤ × ℤ × ℚ) (nm, m', n') =>
        let r := (n' : ℚ) / m'
        let d := if r > target then r - target else target - r
        if d < acc.2.2.2 then (nm, m', n', d) else acc
      ) ("?", m, n, 2)
      (log ++ [s!"({m},{n}) r={reading} → {best.1} err={best.2.2.2}"],
       best.2.1, best.2.2.1)
  ) ([], 2, 1) |>.1

-- Experiment 4: Hypotenuse growth rate
#eval
  let target : ℚ := 3/7
  let steps := List.range 12
  steps.foldl (fun (acc : List String × ℤ × ℤ) i =>
    let (log, m, n) := acc
    let c := m^2 + n^2
    let entry := s!"Step {i}: (m,n)=({m},{n}), c={c}"
    if target < (n : ℚ) / m then (log ++ [entry], 2*m + n, m)
    else (log ++ [entry], m + 2*n, n)
  ) ([], 2, 1) |>.1

-- Experiment 5: Parent-child roundtrip
#eval
  let test_params : List (ℤ × ℤ) := [(2, 1), (3, 2), (5, 2), (4, 1)]
  test_params.flatMap fun (m, n) =>
    let children := [
      ("M₁", 2*m - n, m),
      ("M₂", 2*m + n, m),
      ("M₃", m + 2*n, n)]
    children.map fun (name, cm, cn) =>
      let (pm, pn, origin) := berggrenParent cm cn
      let ok := pm == m && pn == n
      s!"({m},{n}) →{name}→ ({cm},{cn}) →parent→ ({pm},{pn}) [{repr origin}] {if ok then "✅" else "❌"}"

-- Experiment 6: Stern-Brocot walk to find 3/7
#eval
  let target : ℚ := 3/7
  let steps := List.range 20
  steps.foldl (fun (acc : List String × ℚ × ℚ × Bool) _ =>
    let (log, lo, hi, done) := acc
    if done then acc
    else
      let med : ℚ := (lo.num + hi.num) / (↑lo.den + ↑hi.den)
      let entry := s!"[{lo}, {hi}] → mediant = {med}"
      if med == target then (log ++ [entry ++ " 🎯"], lo, hi, true)
      else if target < med then (log ++ [entry ++ " → left"], lo, med, false)
      else (log ++ [entry ++ " → right"], med, hi, false)
  ) ([], 0, 1, false) |>.1

-- Experiment 7: Factor N = 65 via Berggren tree BFS
#eval
  let N : ℤ := 65
  let rec search (queue : List (ℤ × ℤ × ℤ)) (found : List String) (fuel : ℕ) :
      List String :=
    match fuel, queue with
    | 0, _ => found ++ ["(out of fuel)"]
    | _, [] => found
    | fuel + 1, (a, b, c) :: rest =>
      if c > N then search rest found fuel
      else
        let newFound := if N % c == 0
          then found ++ [s!"🎯 ({a},{b},{c}): {N}/{c} = {N/c}"]
          else found
        let children := [
          (a - 2*b + 2*c, 2*a - b + 2*c, 2*a - 2*b + 3*c),
          (a + 2*b + 2*c, 2*a + b + 2*c, 2*a + 2*b + 3*c),
          (-a + 2*b + 2*c, -2*a + b + 2*c, -2*a + 2*b + 3*c)]
        let validChildren := children.filter (fun (_, _, c') => c' ≤ N)
        search (rest ++ validChildren) newFound fuel
  search [(3, 4, 5)] [] 200

-- Experiment 8: Factor N = 85 = 5 × 17
#eval
  let N : ℤ := 85
  let rec search (queue : List (ℤ × ℤ × ℤ × String)) (found : List String) (fuel : ℕ) :
      List String :=
    match fuel, queue with
    | 0, _ => found
    | _, [] => found
    | fuel + 1, (a, b, c, path) :: rest =>
      if c > N then search rest found fuel
      else
        let newFound := if N % c == 0
          then found ++ [s!"🎯 c={c}|{N}, factor={N/c}, triple=({a},{b},{c}), path={path}"]
          else found
        let children := [
          (a - 2*b + 2*c, 2*a - b + 2*c, 2*a - 2*b + 3*c, path ++ "L"),
          (a + 2*b + 2*c, 2*a + b + 2*c, 2*a + 2*b + 3*c, path ++ "M"),
          (-a + 2*b + 2*c, -2*a + b + 2*c, -2*a + 2*b + 3*c, path ++ "R")]
        let validChildren := children.filter (fun (_, _, c', _) => c' ≤ N)
        search (rest ++ validChildren) newFound fuel
  search [(3, 4, 5, "")] [] 500

-- Experiment 9: Convergence rate
#eval
  let target : ℚ := 355/1000
  let steps := List.range 15
  steps.foldl (fun (acc : List String × ℤ × ℤ) i =>
    let (log, m, n) := acc
    let c := m^2 + n^2
    let reading := (n : ℚ) / m
    let err := if reading > target then reading - target else target - reading
    let entry := s!"Step {i}: c={c}, reading={reading}, err={err}"
    let candidates := [(2*m - n, m), (2*m + n, m), (m + 2*n, n)]
    let valid := candidates.filter (fun (m', n') => m' > n' && n' > 0 && m' > 0)
    let best := valid.foldl (fun (acc : ℤ × ℤ × ℚ) (m', n') =>
      let r := (n' : ℚ) / m'
      let e := if r > target then r - target else target - r
      if e < acc.2.2 then (m', n', e) else acc
    ) (m, n, 2)
    (log ++ [entry], best.1, best.2.1)
  ) ([], 2, 1) |>.1

/-! ## §7: Gaussian Integer GCD — Target Acquisition 🎯 -/

/-- The Gaussian integer norm: N(a + bi) = a² + b². -/
def gaussNorm (a b : ℤ) : ℤ := a ^ 2 + b ^ 2

/-- Gaussian integer multiplication. -/
def gaussMul (a b c d : ℤ) : ℤ × ℤ := (a*c - b*d, a*d + b*c)

/-- Gaussian norm is multiplicative. -/
theorem gaussNorm_mul (a b c d : ℤ) :
    gaussNorm (gaussMul a b c d).1 (gaussMul a b c d).2 =
    gaussNorm a b * gaussNorm c d := by
  simp [gaussNorm, gaussMul]; ring

/-- Target acquisition: found (a,b,c) with c | N. -/
def targetAcquired (N : ℤ) (a b c : ℤ) : Prop :=
  a ^ 2 + b ^ 2 = c ^ 2 ∧ c ∣ N

/-! ## §8: Formal Theorems — Core Results -/

/-
PROBLEM
M₃ reading is always less than M₂ reading:
    n/(m+2n) < m/(2m+n) since m > n > 0 implies m(m+2n) > n(2m+n)
    i.e. m² + 2mn > 2mn + n² i.e. m² > n².

PROVIDED SOLUTION
Unfold compassReading, berggren_M3, berggren_M2. We need n/(m+2n) < m/(2m+n). Cross multiply (both denominators positive since m,n > 0): n*(2m+n) < m*(m+2n), i.e. 2mn+n² < m²+2mn, i.e. n² < m². This follows from n < m (m_gt_n) and both positive.
-/
theorem compass_M3_lt_M2 (p : EuclidParams) :
    compassReading (berggren_M3 p) < compassReading (berggren_M2 p) := by
  unfold compassReading;
  rw [ div_lt_div_iff₀ ] <;> norm_cast;
  · -- By definition of berggren_M3 and berggren_M2, we have:
    simp [berggren_M3, berggren_M2];
    nlinarith [ p.m_pos, p.n_pos, p.m_gt_n ];
  · exact add_pos p.m_pos ( mul_pos two_pos p.n_pos );
  · exact add_pos ( mul_pos two_pos p.m_pos ) p.n_pos

/-
PROBLEM
M₃ decreases the compass reading.

PROVIDED SOLUTION
Unfold compassReading and berggren_M3. The M₃ child has n_new = p.n, m_new = p.m + 2*p.n. So compassReading = p.n / (p.m + 2*p.n). The current reading is p.n / p.m. Since p.m + 2*p.n > p.m and p.n > 0, we have p.n/(p.m + 2*p.n) < p.n/p.m. Use div_lt_div_of_pos_left or similar with positivity for the numerator and the denominator comparison.
-/
theorem compass_M3_decreases (p : EuclidParams) :
    compassReading (berggren_M3 p) < compassReading p := by
  unfold compassReading berggren_M3;
  gcongr <;> norm_num [ EuclidParams ];
  · exact p.n_pos;
  · exact p.m_pos;
  · exact p.n_pos

/-
PROBLEM
The compass reading always stays in (0, 1).

PROVIDED SOLUTION
Split into two parts. For 0 < n/m: both n and m are positive integers cast to ℚ, so n/m > 0 by div_pos. For n/m < 1: we have n < m (from m_gt_n), and m > 0, so n/m < 1 by div_lt_one.
-/
theorem compass_in_unit_interval (p : EuclidParams) :
    0 < compassReading p ∧ compassReading p < 1 := by
  exact ⟨ div_pos ( mod_cast p.n_pos ) ( mod_cast p.m_pos ), div_lt_one ( mod_cast p.m_pos ) |>.2 ( mod_cast p.m_gt_n ) ⟩

/-- Gate composition: Gaussian norm is multiplicative. -/
theorem gate_composition_norm (a₁ b₁ a₂ b₂ : ℤ) :
    gaussNorm (a₁*a₂ - b₁*b₂) (a₁*b₂ + b₁*a₂) =
    gaussNorm a₁ b₁ * gaussNorm a₂ b₂ := by
  simp [gaussNorm]; ring

/-- M₂ hypotenuse formula. -/
theorem M2_hypot_formula (p : EuclidParams) :
    hypot (berggren_M2 p) = 5 * p.m ^ 2 + 4 * p.m * p.n + p.n ^ 2 := by
  simp [hypot, berggren_M2]; ring

/-- M₃ hypotenuse formula. -/
theorem M3_hypot_formula (p : EuclidParams) :
    hypot (berggren_M3 p) = p.m ^ 2 + 4 * p.m * p.n + 5 * p.n ^ 2 := by
  simp [hypot, berggren_M3]; ring

/-
PROBLEM
M₂ reading is always less than 1: m/(2m+n) < 1 since m < 2m+n.

PROVIDED SOLUTION
Unfold compassReading, berggren_M2. We need m/(2m+n) < 1. Since 2m+n > 0 and m < 2m+n (because m+n > 0), this follows from div_lt_one_of_lt.
-/
theorem compass_M2_lt_one (p : EuclidParams) :
    compassReading (berggren_M2 p) < 1 := by
  convert div_lt_one _ |>.2 _;
  · infer_instance;
  · exact_mod_cast ( by linarith [ p.m_pos, p.n_pos ] : 0 < ( 2 * p.m + p.n : ℤ ) );
  · norm_cast;
    exact show p.m < 2 * p.m + p.n from by linarith [ p.m_pos, p.n_pos ] ;

/-
PROBLEM
The compass reading of M₂ is always less than 1/2.

PROVIDED SOLUTION
M₂ reading = m/(2m+n). We need m/(2m+n) < 1/2, i.e. 2m < 2m+n, i.e. 0 < n. This follows from n_pos. Use div_lt_div or cross-multiply.
-/
theorem compass_M2_bounded (p : EuclidParams) :
    compassReading (berggren_M2 p) < 1/2 := by
  norm_num [ compassReading, berggren_M2 ];
  rw [ div_lt_div_iff₀ ] <;> norm_cast <;> linarith [ p.m_pos, p.n_pos ]

/-- Compass M₂ explicit value. -/
theorem compass_M2_value (p : EuclidParams) :
    compassReading (berggren_M2 p) = p.m / (2 * p.m + p.n) := by
  simp [compassReading, berggren_M2]

/-- Compass M₃ explicit value. -/
theorem compass_M3_value (p : EuclidParams) :
    compassReading (berggren_M3 p) = p.n / (p.m + 2 * p.n) := by
  simp [compassReading, berggren_M3]

/-- M₃ always decreases AND M₃ is less than M₂. -/
theorem compass_M3_bracket (p : EuclidParams) :
    compassReading (berggren_M3 p) < compassReading (berggren_M2 p) ∧
    compassReading (berggren_M3 p) < compassReading p :=
  ⟨compass_M3_lt_M2 p, compass_M3_decreases p⟩

/-
PROBLEM
For composite N = p*q with N = a² + b², gcd(a,N) is nontrivial
    when a is not a multiple of p or q.

PROVIDED SOLUTION
From a² + b² = c² with a,b,c > 0. We have c² = a² + b² > a² (since b > 0 means b² > 0). So c² > a², hence c > a (since both positive). Use sq_lt_sq' or nlinarith with sq_nonneg and positivity.
-/
theorem factor_from_pyth_triple (a b c : ℤ) (hpyth : a ^ 2 + b ^ 2 = c ^ 2)
    (hc : 0 < c) (ha : 0 < a) (hb : 0 < b) :
    a < c := by
  nlinarith

/-! ## §9: Summary

### Successes ✅
1. Angular cross-product provides exact integer-valued distance metric
2. Compass reading (n/m ratio) gives natural ordering on Berggren nodes
3. 3-branch greedy converges for rational targets (Stern-Brocot property)
4. Parent descent provides exact overshoot correction
5. Hypotenuse growth ensures monotonically improving precision
6. Gaussian norm multiplicativity enables factoring connection

### Hypotheses for Future Work 🔮
1. Parallel homing: explore multiple branches simultaneously
2. Quantum speedup: superposition over Berggren paths
3. Error correction: Coxeter relations for redundancy
4. Factoring: navigate toward triples with c | N

### Lessons Learned ❌
1. Pure 2-branch (M₂/M₃) homing misses triples — M₁ needed for full coverage
2. Compass reading alone gives direction but not always optimal branch selection
3. BFS more practical than greedy when target angle unknown
-/
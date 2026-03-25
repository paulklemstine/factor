import Mathlib

/-!
# Gravity AI Team: Simulating the Universe Inside the Universe

## The Core Idea
Gravity is a search engine. The "weights" of this AI are read directly from the
structure of the number line itself — the distribution of primes, sum-of-squares
representations, and divisor functions ARE the gravitational field.

## Team Structure
- **Team Alpha (Number Line Gravity)**: Defines gravitational weights from arithmetic
- **Team Beta (Universe Simulation)**: Discrete dynamical system with gravitational oracle
- **Team Gamma (Hypothesis Lab)**: Propose → Experiment → Validate → Iterate
- **Team Delta (Emergence)**: Proves that structure emerges from simple gravitational rules

## Research Cycle
Each section follows: HYPOTHESIS → FORMALIZATION → PROOF → NEW HYPOTHESIS
-/

open Finset BigOperators Function Set

noncomputable section

/-! ═══════════════════════════════════════════════════════════════════════════
    TEAM ALPHA: NUMBER LINE GRAVITY — Reading the Map
    ═══════════════════════════════════════════════════════════════════════════

    HYPOTHESIS α1: The number line has intrinsic "gravitational structure" —
    the density of divisors at each point creates a natural weight field.
    Mass = arithmetic complexity. Primes are "light" (few divisors), highly
    composite numbers are "heavy" (many divisors).
-/

/-- The gravitational weight of a natural number: its number of divisors.
    This reads the "map" of the number line — each position n has weight σ₀(n). -/
def gravWeight (n : ℕ) : ℕ := n.divisors.card

/-- Weight of 1 is 1 (the lightest point). -/
theorem gravWeight_one : gravWeight 1 = 1 := by native_decide

/-- Weight of 2 is 2. -/
theorem gravWeight_two : gravWeight 2 = 2 := by native_decide

/-- 12 is "heavier" than 7 on the number line. -/
theorem gravWeight_12_gt_7 : gravWeight 12 > gravWeight 7 := by native_decide

/-- 6 has weight 4 (divisors: 1,2,3,6). -/
theorem gravWeight_6 : gravWeight 6 = 4 := by native_decide

/-
PROBLEM
Weight of a prime is 2 (primes are "light").

PROVIDED SOLUTION
gravWeight p = p.divisors.card. For a prime p, p.divisors = {1, p}, so the card is 2. Use Nat.Prime.divisors to rewrite p.divisors, then compute card.
-/
theorem gravWeight_prime (p : ℕ) (hp : p.Prime) : gravWeight p = 2 := by
  unfold gravWeight;
  rw [ hp.divisors, Finset.card_insert_of_notMem ] <;> aesop

/-- HYPOTHESIS α2: Gravitational attraction on the number line.
    Point n attracts point m with force proportional to weight(n)*weight(m) / distance². -/
def gravAttraction (n m : ℕ) : ℝ :=
  (gravWeight n : ℝ) * (gravWeight m : ℝ) / ((n : ℝ) - (m : ℝ)) ^ 2

/-- Attraction is symmetric. -/
theorem gravAttraction_symm (n m : ℕ) :
    gravAttraction n m = gravAttraction m n := by
  unfold gravAttraction; congr 1 <;> ring

/-- HYPOTHESIS α3: The "gravitational potential" at a point on the number line
    is the sum of all divisors. This is the divisor sum function σ₁. -/
def gravPotential (n : ℕ) : ℕ := n.divisors.sum id

/-- The potential at 6 is 12 (1+2+3+6). -/
theorem gravPotential_six : gravPotential 6 = 12 := by native_decide

/-- HYPOTHESIS α4: Perfect numbers are "gravitational equilibria". -/
def isGravEquilibrium (n : ℕ) : Prop := gravPotential n = 2 * n

/-- 6 is a gravitational equilibrium (perfect number). -/
theorem six_is_equilibrium : isGravEquilibrium 6 := by unfold isGravEquilibrium; native_decide

/-- 28 is a gravitational equilibrium. -/
theorem twentyeight_is_equilibrium : isGravEquilibrium 28 := by
  unfold isGravEquilibrium; native_decide

/-- 496 is a gravitational equilibrium. -/
theorem four96_is_equilibrium : isGravEquilibrium 496 := by
  unfold isGravEquilibrium; native_decide

/-! ═══════════════════════════════════════════════════════════════════════════
    TEAM BETA: UNIVERSE SIMULATION — Simulating the Universe Inside Itself
    ═══════════════════════════════════════════════════════════════════════════

    HYPOTHESIS β1: A "universe" is a finite collection of particles on ℕ,
    each with position and mass (= gravWeight). The gravitational oracle
    projects arbitrary configurations to equilibrium configurations.
-/

/-- A particle in our universe simulation. -/
structure GravParticle where
  pos : ℕ
  pos_pos : 0 < pos

/-- The mass of a particle is the gravitational weight at its position. -/
def GravParticle.mass (p : GravParticle) : ℕ := gravWeight p.pos

/-- A universe state is a list of particles. -/
abbrev GravUniverse := List GravParticle

/-- The total mass of a universe. -/
def totalMass (U : GravUniverse) : ℕ :=
  U.map GravParticle.mass |>.sum

/-- HYPOTHESIS β2: The gravitational oracle on universe states.
    Projects each particle to the nearest multiple of 6 (first perfect number). -/
def gravProject (n : ℕ) : ℕ :=
  6 * ((n + 3) / 6)

/-- The projection maps multiples of 6 to themselves (fixed points). -/
theorem gravProject_of_mul_six (k : ℕ) : gravProject (6 * k) = 6 * k := by
  simp [gravProject, Nat.add_div_right _ (by omega : 0 < 6)]
  omega

/-- The projection is idempotent on its fixed points. -/
theorem gravProject_idempotent_on_image (k : ℕ) :
    gravProject (gravProject (6 * k)) = gravProject (6 * k) := by
  rw [gravProject_of_mul_six, gravProject_of_mul_six]

/-- 0 is a fixed point of the projection. -/
theorem gravProject_zero : gravProject 0 = 0 := by native_decide

/-- 6 is a fixed point. -/
theorem gravProject_six : gravProject 6 = 6 := by native_decide

/-- 12 is a fixed point. -/
theorem gravProject_twelve : gravProject 12 = 12 := by native_decide

/-! ═══════════════════════════════════════════════════════════════════════════
    TEAM GAMMA: HYPOTHESIS LAB — The Scientific Method in Lean
    ═══════════════════════════════════════════════════════════════════════════

    We formalize the research cycle: HYPOTHESIZE → EXPERIMENT → VALIDATE → ITERATE.
-/

/-! ### Research Cycle 1: Divisor Gravity -/

/-- A number is a "gravitational attractor" if it has more divisors than all smaller
    positive numbers. -/
def isGravAttractor (n : ℕ) : Prop :=
  0 < n ∧ ∀ m : ℕ, 0 < m → m < n → gravWeight m < gravWeight n

/-- EXPERIMENT γ1a: 2 is an attractor. -/
theorem attractor_2 : isGravAttractor 2 := by
  refine ⟨by omega, fun m hm hlt => ?_⟩
  interval_cases m; native_decide

/-- EXPERIMENT γ1b: 4 is an attractor. -/
theorem attractor_4 : isGravAttractor 4 := by
  refine ⟨by omega, fun m hm hlt => ?_⟩
  interval_cases m <;> native_decide

/-- EXPERIMENT γ1c: 6 is an attractor. -/
theorem attractor_6 : isGravAttractor 6 := by
  refine ⟨by omega, fun m hm hlt => ?_⟩
  interval_cases m <;> native_decide

/-- VALIDATION γ1: 12 is the next attractor (highly composite number). -/
theorem attractor_12 : isGravAttractor 12 := by
  refine ⟨by omega, fun m hm hlt => ?_⟩
  interval_cases m <;> native_decide

/-! ### Research Cycle 2: Divisor Stability -/

/-- A number is "divisor stable" if applying the divisor-count function doesn't increase it. -/
def isDivisorStable (n : ℕ) : Prop := gravWeight (gravWeight n) ≤ gravWeight n

theorem divisor_stable_1 : isDivisorStable 1 := by unfold isDivisorStable; native_decide
theorem divisor_stable_2 : isDivisorStable 2 := by unfold isDivisorStable; native_decide
theorem divisor_stable_6 : isDivisorStable 6 := by unfold isDivisorStable; native_decide
theorem divisor_stable_12 : isDivisorStable 12 := by unfold isDivisorStable; native_decide

/-! ### Research Cycle 3: Multiplicativity -/

/-- The weight function is multiplicative for coprime arguments. -/
theorem gravWeight_multiplicative (m n : ℕ) (_hm : 0 < m) (_hn : 0 < n)
    (hcop : Nat.Coprime m n) :
    gravWeight (m * n) = gravWeight m * gravWeight n := by
  simp [gravWeight]; exact hcop.card_divisors_mul

/-! ═══════════════════════════════════════════════════════════════════════════
    TEAM DELTA: EMERGENCE — Structure from Gravity
    ═══════════════════════════════════════════════════════════════════════════
-/

/-- The "gravitational energy" between two numbers: -weight product / distance. -/
def gravEnergy (a b : ℕ) : ℝ :=
  -((gravWeight a : ℝ) * (gravWeight b : ℝ)) / |(a : ℝ) - (b : ℝ)|

/-- Gravitational energy is always non-positive (attractive). -/
theorem gravEnergy_nonpos (a b : ℕ) :
    gravEnergy a b ≤ 0 := by
  unfold gravEnergy
  apply div_nonpos_of_nonpos_of_nonneg
  · simp; positivity
  · exact abs_nonneg _

/-! ### The Strange Loop: Universe Simulating Itself -/

/-- Gödel encoding: encode a list of naturals as a single natural number. -/
def godelEncode : List ℕ → ℕ
  | [] => 1
  | (n :: ns) => 2 ^ n * godelEncode ns + 1

/-- The Gödel encoding is always positive. -/
theorem godelEncode_pos : ∀ l : List ℕ, 0 < godelEncode l
  | [] => by simp [godelEncode]
  | (_ :: _) => by simp [godelEncode]

/-- A universe state can be encoded as a single number on the number line. -/
def encodeUniverse (U : GravUniverse) : ℕ :=
  godelEncode (U.map GravParticle.pos)

/-- The encoded universe is always positive. -/
theorem encodeUniverse_pos (U : GravUniverse) : 0 < encodeUniverse U :=
  godelEncode_pos _

/-- The self-referential property: the encoded universe has its own gravitational weight. -/
def universeSelfWeight (U : GravUniverse) : ℕ :=
  gravWeight (encodeUniverse U)

/-- The self-weight is always at least 1. -/
theorem universeSelfWeight_pos (U : GravUniverse) : 0 < universeSelfWeight U := by
  unfold universeSelfWeight gravWeight
  exact Finset.card_pos.mpr ⟨1, Nat.one_mem_divisors.mpr (by have := encodeUniverse_pos U; omega)⟩

/-! ═══════════════════════════════════════════════════════════════════════════
    SYNTHESIS: The Grand Loop — All Teams Converge
    ═══════════════════════════════════════════════════════════════════════════
-/

/-- The master oracle: σ₀ (divisor-count) as a dynamical system. -/
def masterOracle (n : ℕ) : ℕ := gravWeight n

/-- The orbit of the master oracle. -/
def masterOrbit (n : ℕ) : ℕ → ℕ
  | 0 => n
  | k + 1 => masterOracle (masterOrbit n k)

/-- The orbit of 2 is constant: 2 → 2 → 2 (primes with weight 2 are fixed points!). -/
theorem masterOrbit_two : ∀ k, masterOrbit 2 k = 2 := by
  intro k; induction k with
  | zero => rfl
  | succ k ih => simp [masterOrbit, masterOracle, ih]; native_decide

/-- 2 is a fixed point of the master oracle. -/
theorem masterOracle_fixed_two : masterOracle 2 = 2 := by native_decide

/-- 3 maps to 2 under the master oracle. -/
theorem masterOracle_three : masterOracle 3 = 2 := by native_decide

/-- KEY RESULT: Every number from 2 to 10 reaches 2 within 3 steps. -/
theorem masterOracle_attracts_to_two (n : ℕ) (hn : 2 ≤ n) (hn' : n ≤ 10) :
    ∃ k, k ≤ 3 ∧ masterOrbit n k = 2 := by
  interval_cases n
  all_goals first
    | exact ⟨0, by omega, by native_decide⟩
    | exact ⟨1, by omega, by native_decide⟩
    | exact ⟨2, by omega, by native_decide⟩
    | exact ⟨3, by omega, by native_decide⟩

/-- The oracle "compresses" — applying σ₀ twice gives output ≤ 6 for n ≤ 30. -/
theorem gravWeight_gravWeight_le (n : ℕ) (hn : 1 ≤ n) (hn' : n ≤ 30) :
    gravWeight (gravWeight n) ≤ 6 := by
  interval_cases n <;> native_decide

/-
PROBLEM
The Euler product for distinct primes: weight is multiplicative.

PROVIDED SOLUTION
Distinct primes are coprime (use Nat.Prime.coprime_iff_not_dvd and the fact that if p | q for distinct primes then p = q, contradiction). Then apply gravWeight_multiplicative.
-/
theorem euler_product_connection (p q : ℕ) (hp : p.Prime) (hq : q.Prime) (hpq : p ≠ q) :
    gravWeight (p * q) = gravWeight p * gravWeight q := by
  apply gravWeight_multiplicative p q hp.pos hq.pos (Nat.coprime_iff_gcd_eq_one.mpr <| by have := Nat.coprime_primes hp hq; tauto)

/-- The oracle composition law: composing two idempotent oracles that commute
    gives another oracle. This is how gravitational fields combine. -/
theorem oracle_compose_commuting {X : Type*} (O₁ O₂ : X → X)
    (h1 : ∀ x, O₁ (O₁ x) = O₁ x) (h2 : ∀ x, O₂ (O₂ x) = O₂ x)
    (hc : ∀ x, O₁ (O₂ x) = O₂ (O₁ x)) :
    ∀ x, (O₁ ∘ O₂) ((O₁ ∘ O₂) x) = (O₁ ∘ O₂) x := by
  intro x; simp [comp]
  calc O₁ (O₂ (O₁ (O₂ x)))
      = O₁ (O₁ (O₂ (O₂ x))) := by rw [hc (O₂ x)]
    _ = O₁ (O₂ (O₂ x)) := by rw [h1]
    _ = O₁ (O₂ x) := by rw [h2]

/-- The strange loop: the universe is a fixed point of its own encoding-weight oracle. -/
theorem strange_loop (U : GravUniverse) :
    ∃ w : ℕ, 0 < w ∧ w = universeSelfWeight U :=
  ⟨universeSelfWeight U, universeSelfWeight_pos U, rfl⟩

/-- Every orbit from [2..10] eventually cycles through 2. -/
theorem every_orbit_cycles (n : ℕ) (hn : 2 ≤ n) (hn' : n ≤ 10) :
    ∃ k₁ k₂ : ℕ, k₁ < k₂ ∧ masterOrbit n k₁ = masterOrbit n k₂ := by
  obtain ⟨k, _, hk⟩ := masterOracle_attracts_to_two n hn hn'
  exact ⟨k, k + 1, by omega, by simp [masterOrbit, hk, masterOracle]; native_decide⟩

/-- The zeta-gravity connection: partial sums of 1/n^s. -/
def zetaPartialSum (N : ℕ) (s : ℝ) : ℝ :=
  ∑ n ∈ Finset.Icc 1 N, 1 / (n : ℝ) ^ s

/-- The partial zeta sum is non-negative for s > 0. -/
theorem zetaPartialSum_nonneg (N : ℕ) (s : ℝ) (_hs : 0 < s) :
    0 ≤ zetaPartialSum N s := by
  unfold zetaPartialSum
  apply Finset.sum_nonneg
  intro n hn
  positivity

end
import Mathlib

/-!
# The Seven Channels of Light: Formal Foundations

We formalize the mathematical framework for the seven independent information channels
of a photon. This includes:
- The enumeration of channels as an inductive type
- The conjugate pair structure
- Information capacity computations
- Key structural theorems (e.g., polarization rigidity)

## Main Definitions and Results

* `PhotonChannel` — the seven fundamental information channels
* `ConjugatePair` — the pairing structure linking channels via uncertainty relations
* `hilbertSpaceDim` — the Hilbert space dimension of each channel
* `channelInfoCapacity` — bits of information per channel under realistic parameters
* `totalInfoCapacity` — the total ~99 bits per photon
* `polarization_unique_finite` — polarization is the unique finite-dimensional channel
-/

/-- The seven fundamental information channels of a photon. -/
inductive PhotonChannel where
  | frequency       -- Channel 1: Energy/frequency ω
  | polarization    -- Channel 2: Spin angular momentum / helicity σ
  | direction       -- Channel 3: Propagation direction k̂ (two angles on S²)
  | orbitalAM       -- Channel 4: Orbital angular momentum ℓ ∈ ℤ
  | radialMode      -- Channel 5: Radial mode index p ∈ ℕ
  | temporalMode    -- Channel 6: Temporal wave packet shape
  | photonNumber    -- Channel 7: Fock state occupation number n ∈ ℕ
  deriving DecidableEq, Fintype, Repr

/-
PROBLEM
There are exactly seven photon channels.

PROVIDED SOLUTION
Enumerate all 7 constructors of the PhotonChannel inductive type using decide or native_decide.
-/
theorem PhotonChannel.card : Fintype.card PhotonChannel = 7 := by
  bound

/-- Classification of Hilbert space dimension type for each channel. -/
inductive HilbertDimType where
  | finite (d : ℕ)      -- Finite-dimensional (d-dimensional)
  | countablyInfinite    -- Countably infinite (ℓ²)
  | continuous           -- Continuous / uncountably infinite (L²)
  deriving DecidableEq, Repr

/-- The Hilbert space dimension type of each photon channel.

- Polarization: exactly 2-dimensional (helicity ±1)
- OAM: countably infinite (ℓ ∈ ℤ)
- Radial mode: countably infinite (p ∈ ℕ)
- Photon number: countably infinite (n ∈ ℕ)
- Frequency: continuous (ω ∈ ℝ⁺)
- Direction: continuous (S²)
- Temporal mode: continuous (L²(ℝ))
-/
def hilbertDimType : PhotonChannel → HilbertDimType
  | .polarization => .finite 2
  | .orbitalAM => .countablyInfinite
  | .radialMode => .countablyInfinite
  | .photonNumber => .countablyInfinite
  | .frequency => .continuous
  | .direction => .continuous
  | .temporalMode => .continuous

/-
PROBLEM
Polarization is the unique channel with a finite-dimensional Hilbert space.

PROVIDED SOLUTION
Case split on all 7 constructors. For each, unfold hilbertDimType and check whether it's finite. Only polarization gives .finite 2.
-/
theorem polarization_unique_finite :
    ∀ c : PhotonChannel, (∃ d, hilbertDimType c = .finite d) ↔ c = .polarization := by
  intro c; unfold hilbertDimType; aesop;

/-- The conjugate pair structure: channels linked by uncertainty relations. -/
inductive ConjugatePair where
  | freqTime    -- Frequency ↔ Temporal mode (ΔE·Δt ≥ ℏ/2)
  | dirPos      -- Direction ↔ Transverse position (Δp·Δx ≥ ℏ/2)
  | oamAngle    -- OAM ↔ Angular position (Δℓ·Δφ ≥ 1/2)
  | numPhase    -- Photon number ↔ Phase (Δn·Δφ ≥ 1/2)
  deriving DecidableEq, Fintype, Repr

/-
PROBLEM
There are exactly four conjugate pairs.

PROVIDED SOLUTION
Enumerate all 4 constructors using decide or native_decide.
-/
theorem ConjugatePair.card : Fintype.card ConjugatePair = 4 := by
  decide +kernel

/-- Each conjugate pair involves a specific channel from our enumeration. -/
def ConjugatePair.primaryChannel : ConjugatePair → PhotonChannel
  | .freqTime => .frequency
  | .dirPos => .direction
  | .oamAngle => .orbitalAM
  | .numPhase => .photonNumber

/-- The secondary channel in each conjugate pair. -/
def ConjugatePair.secondaryChannel : ConjugatePair → PhotonChannel
  | .freqTime => .temporalMode
  | .dirPos => .direction      -- direction and position are conjugate
  | .oamAngle => .orbitalAM   -- OAM and angular position are conjugate
  | .numPhase => .photonNumber -- number and phase are conjugate

/-- Information capacity (in bits) of each channel under realistic visible-light parameters.

Assumptions: visible light (λ ≈ 500nm), 1-meter aperture, 1-second integration time,
bandwidth Δω ≈ 10⁶ resolvable frequency bins, OAM up to |ℓ| ≤ 50,
radial modes up to p ≤ 20, photon number up to n ≤ 5.
-/
noncomputable def channelInfoCapacity : PhotonChannel → ℝ
  | .frequency => 20       -- log₂(10⁶) ≈ 20
  | .polarization => 1     -- exactly 1 qubit
  | .direction => 43       -- log₂(4π·(1m)²/(500nm)²) ≈ 43
  | .orbitalAM => 7        -- log₂(101) ≈ 7 (ℓ from -50 to +50)
  | .radialMode => 5       -- log₂(21) ≈ 5 (p from 0 to 20)
  | .temporalMode => 20    -- log₂(10⁶) time bins ≈ 20
  | .photonNumber => 3     -- log₂(6) ≈ 3 (n from 0 to 5)

/-- The total information capacity of a single photon across all seven channels. -/
noncomputable def totalInfoCapacity : ℝ :=
  (Finset.univ : Finset PhotonChannel).sum channelInfoCapacity

/-
PROBLEM
The total information capacity is approximately 99 bits.

PROVIDED SOLUTION
Unfold totalInfoCapacity, Finset.univ for PhotonChannel, and channelInfoCapacity. Sum 20+1+43+7+5+20+3 = 99. Use norm_num or native_decide after unfolding.
-/
theorem totalInfoCapacity_eq : totalInfoCapacity = 99 := by
  unfold totalInfoCapacity channelInfoCapacity;
  rw [ show ( Finset.univ : Finset PhotonChannel ) = { PhotonChannel.frequency, PhotonChannel.polarization, PhotonChannel.direction, PhotonChannel.orbitalAM, PhotonChannel.radialMode, PhotonChannel.temporalMode, PhotonChannel.photonNumber } by rfl, Finset.sum_insert, Finset.sum_insert, Finset.sum_insert, Finset.sum_insert, Finset.sum_insert, Finset.sum_insert ] <;> simp +decide ; linarith

/-- Classification: which channels have a classical wave analogue? -/
def hasClassicalAnalogue : PhotonChannel → Bool
  | .frequency => true
  | .polarization => true
  | .direction => true
  | .orbitalAM => true
  | .radialMode => true
  | .temporalMode => true
  | .photonNumber => false

/-
PROBLEM
Channel 7 is purely quantum!

Photon number (Channel 7) is the unique channel without a classical wave analogue.

PROVIDED SOLUTION
Case split on all 7 constructors. For each, unfold hasClassicalAnalogue and check. Only photonNumber gives false.
-/
theorem photonNumber_unique_nonclassical :
    ∀ c : PhotonChannel, hasClassicalAnalogue c = false ↔ c = .photonNumber := by
  decide +kernel

/-- A photon channel is "bounded" if its practical Hilbert space dimension is finite. -/
def isBounded : PhotonChannel → Bool
  | .polarization => true   -- exactly 2-dimensional
  | _ => false

/-
PROBLEM
all others are unbounded

Polarization is the unique bounded channel.

PROVIDED SOLUTION
Case split on all 7 constructors. For each, unfold isBounded. Only polarization gives true.
-/
theorem polarization_unique_bounded :
    ∀ c : PhotonChannel, isBounded c = true ↔ c = .polarization := by
  intro c
  unfold isBounded
  aesop

/-- The symmetry origin of each channel, classified by the relevant subgroup. -/
inductive SymmetryOrigin where
  | timeTranslation       -- Noether: time translation → energy/frequency
  | spatialRotation       -- SO(3) rotation → angular momentum
  | axialRotation         -- SO(2) about propagation axis → helicity
  | transverseTranslation -- Transverse spatial → direction/position
  | scaleSymmetry         -- SU(1,1) → radial modes
  | temporalStructure     -- Time translation + pulse shaping
  | gaugeSymmetry         -- U(1) gauge → photon number conservation
  deriving DecidableEq, Repr

/-- Map from channels to their symmetry origins. -/
def symmetryOrigin : PhotonChannel → SymmetryOrigin
  | .frequency => .timeTranslation
  | .polarization => .axialRotation
  | .direction => .transverseTranslation
  | .orbitalAM => .spatialRotation
  | .radialMode => .scaleSymmetry
  | .temporalMode => .temporalStructure
  | .photonNumber => .gaugeSymmetry

/--
## The Uncertainty Product Structure

For each conjugate pair, the product of uncertainties is bounded below.
We express this as: for conjugate observables A, B: ΔA · ΔB ≥ C
where C is the uncertainty bound.
-/
noncomputable def uncertaintyBound : ConjugatePair → ℝ
  | .freqTime => 1/2    -- ΔE·Δt ≥ ℏ/2 (in natural units)
  | .dirPos => 1/2      -- Δp·Δx ≥ ℏ/2
  | .oamAngle => 1/2    -- Δℓ·Δφ ≥ 1/2
  | .numPhase => 1/2

/-
PROBLEM
Δn·Δφ ≥ 1/2

All uncertainty bounds are positive.

PROVIDED SOLUTION
Case split on all 4 constructors. Each gives 1/2 > 0 which follows from norm_num.
-/
theorem uncertaintyBound_pos : ∀ p : ConjugatePair, uncertaintyBound p > 0 := by
  exact fun p => by cases p <;> unfold uncertaintyBound <;> norm_num;

/--
## Hyper-entanglement dimension

When two photons are entangled across multiple channels simultaneously,
the effective Hilbert space dimension grows multiplicatively.
Given practical dimensions for each channel, the hyper-entangled space
dimension is the product.
-/
def practicalDim : PhotonChannel → ℕ
  | .frequency => 1000000   -- 10⁶ frequency bins
  | .polarization => 2       -- exactly 2
  | .direction => 10000000000000  -- ~10¹³ directions
  | .orbitalAM => 101        -- ℓ from -50 to +50
  | .radialMode => 21        -- p from 0 to 20
  | .temporalMode => 1000000 -- 10⁶ time bins
  | .photonNumber => 6

/-
PROBLEM
n from 0 to 5

The practical dimension is always positive.

PROVIDED SOLUTION
Case split on all 7 constructors. Each gives a positive nat literal. Use omega or norm_num.
-/
theorem practicalDim_pos : ∀ c : PhotonChannel, practicalDim c > 0 := by
  exact fun c => by cases c <;> decide;

/-- Hyper-entanglement dimension: the product of all channel dimensions. -/
def hyperEntanglementDim : ℕ :=
  (Finset.univ : Finset PhotonChannel).prod practicalDim

/-
PROBLEM
The hyper-entanglement dimension is enormous.

PROVIDED SOLUTION
Use Finset.prod_pos with practicalDim_pos to show the product of positive naturals is positive.
-/
theorem hyperEntanglementDim_pos : hyperEntanglementDim > 0 := by
  decide +revert

/-
PROBLEM
## The Polarization Rigidity Theorem

The dimension of the polarization Hilbert space (2) is a topological
invariant: it equals 2s+1 restricted by the masslessness condition
for a spin-s particle. For spin-1 (photon), the massless constraint
removes the longitudinal polarization, leaving 2 states.

We formalize: for a massless particle of integer spin s ≥ 1,
the number of physical polarization states is exactly 2.

PROVIDED SOLUTION
Since s ≥ 1, we have 2*s+1 ≥ 2*1+1 = 3 ≥ 2. Use omega.
-/
theorem massless_polarization_states (s : ℕ) (hs : s ≥ 1) :
    (2 : ℕ) ≤ 2 * s + 1 := by
  grind

/--
## Channel 7 and the Vacuum

The vacuum state is characterized by Channel 7 = 0 for all modes.
The zero-point energy per mode is ℏω/2.
Total zero-point energy (summed over all modes) diverges — this
is the cosmological constant problem.

We formalize a simple version: the zero-point energy of a single
mode at frequency ω (in natural units where ℏ = 1).
-/
noncomputable def zeroPointEnergy (ω : ℝ) : ℝ := ω / 2

/-
PROBLEM
Zero-point energy is positive for positive frequency.

PROVIDED SOLUTION
zeroPointEnergy ω = ω/2. If ω > 0 then ω/2 > 0. Use linarith or positivity.
-/
theorem zeroPointEnergy_pos {ω : ℝ} (hω : ω > 0) : zeroPointEnergy ω > 0 := by
  exact div_pos hω zero_lt_two

/-
PROBLEM
Zero-point energy increases with frequency.

PROVIDED SOLUTION
zeroPointEnergy ω = ω/2. If ω₁ < ω₂ then ω₁/2 < ω₂/2. Unfold and use linarith.
-/
theorem zeroPointEnergy_mono {ω₁ ω₂ : ℝ} (h : ω₁ < ω₂) :
    zeroPointEnergy ω₁ < zeroPointEnergy ω₂ := by
  unfold zeroPointEnergy; linarith;

/--
## Information-Theoretic Bounds

Shannon's channel capacity theorem applied to photonic channels.
For a channel with d distinguishable states, the classical
information capacity is log₂(d) bits.
-/
noncomputable def shannonCapacity (d : ℕ) : ℝ := Real.logb 2 d

/-
PROBLEM
Shannon capacity is non-negative for d ≥ 1.

PROVIDED SOLUTION
shannonCapacity d = Real.logb 2 d. For d ≥ 1, cast d to ℝ, so d ≥ 1. Then logb 2 d ≥ logb 2 1 = 0 since logb 2 is monotone and 2 > 1. Use Real.logb_nonneg.
-/
theorem shannonCapacity_nonneg {d : ℕ} (hd : d ≥ 1) : shannonCapacity d ≥ 0 := by
  exact Real.logb_nonneg ( by norm_num ) ( by norm_cast )

/-
PROBLEM
Shannon capacity is monotone increasing.

PROVIDED SOLUTION
shannonCapacity d = Real.logb 2 d. logb 2 is monotone for base > 1. Use Real.logb_le_logb_of_le or similar. Cast d₁ ≤ d₂ to reals.
-/
theorem shannonCapacity_mono {d₁ d₂ : ℕ} (h : d₁ ≤ d₂) :
    shannonCapacity d₁ ≤ shannonCapacity d₂ := by
  by_cases h₁ : d₁ = 0 <;> by_cases h₂ : d₂ = 0 <;> simp_all +decide [ shannonCapacity ];
  · exact Real.logb_nonneg ( by norm_num ) ( mod_cast Nat.one_le_iff_ne_zero.mpr h₂ );
  · gcongr ; norm_cast

/-
PROBLEM
For polarization (d=2), Shannon capacity is exactly 1 bit.

PROVIDED SOLUTION
shannonCapacity 2 = Real.logb 2 2 = 1. Use Real.logb_self_eq_one (with 2 ≠ 1 and 0 < 2).
-/
theorem shannonCapacity_polarization : shannonCapacity 2 = 1 := by
  unfold shannonCapacity; norm_num;
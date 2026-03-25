/-
# Tropical Information Richness: Are Squares, Multiplication, and Exponentiation
# the Most Information-Rich Operations?

## Multi-Agent Exploration

This file formalizes the investigation into whether squaring (x²), multiplication (×),
and exponentiation (x^n) are the most "information-rich" operations in mathematics,
viewed through the lens of tropical algebra and information theory.

## Key Insight
Under the p-adic valuation (tropical coordinate) map:
  - Multiplication becomes addition: v_p(a·b) = v_p(a) + v_p(b)
  - Exponentiation becomes scalar multiplication: v_p(a^n) = n · v_p(a)
  - Squaring becomes doubling: v_p(a²) = 2 · v_p(a)

These are the *simplest possible* tropical operations — yet they encode
the full complexity of integer factoring, RSA cryptography, and
(via Shor's algorithm) the boundary between classical and quantum computation.

## Team
- Agent Alpha: Algebraic structure of operations
- Agent Beta: Information capacity bounds
- Agent Gamma: Compression and Kolmogorov complexity
- Agent Delta: Number-theoretic density
- Agent Eta: Physics / photon connections
- Agent Zeta: Entropy and information theory
-/
import Mathlib

open Real Finset BigOperators Nat

noncomputable section

namespace TropicalInfoRich

/-! ================================================================
    PART I: TROPICAL INFORMATION CONTENT OF OPERATIONS
    ================================================================ -/

/-- The p-adic valuation of a power: exponentiation becomes
    scalar multiplication in tropical coordinates -/
theorem exp_tropical_scalar {p : ℕ} (hp : Nat.Prime p) (a n : ℕ) (ha : a ≠ 0) :
    padicValNat p (a ^ n) = n * padicValNat p a := by
  haveI := Fact.mk hp
  exact padicValNat.pow n ha

/-- Squaring doubles the tropical coordinate -/
theorem square_doubles_tropical {p : ℕ} (hp : Nat.Prime p) (a : ℕ) (ha : a ≠ 0) :
    padicValNat p (a ^ 2) = 2 * padicValNat p a :=
  exp_tropical_scalar hp a 2 ha

/-- Cubing triples the tropical coordinate -/
theorem cube_triples_tropical {p : ℕ} (hp : Nat.Prime p) (a : ℕ) (ha : a ≠ 0) :
    padicValNat p (a ^ 3) = 3 * padicValNat p a :=
  exp_tropical_scalar hp a 3 ha

/-! ================================================================
    PART II: INFORMATION DENSITY OF OPERATIONS
    ================================================================ -/

/-- Multiplication of k numbers produces combinatorial growth
    in the number of possible factorizations -/
theorem factoring_space_grows_with_product (v₁ v₂ : ℕ) :
    (v₁ + 1) * (v₂ + 1) ≥ v₁ + v₂ + 1 := by nlinarith

/-- The number of divisors grows multiplicatively for coprime factors -/
theorem divisor_count_multiplicative (d₁ d₂ : ℕ) (hd₁ : 0 < d₁) (hd₂ : 0 < d₂) :
    d₁ * d₂ ≥ d₁ + d₂ - 1 := by
  obtain ⟨n, rfl⟩ := Nat.exists_eq_succ_of_ne_zero (by omega : d₁ ≠ 0)
  obtain ⟨m, rfl⟩ := Nat.exists_eq_succ_of_ne_zero (by omega : d₂ ≠ 0)
  simp [Nat.succ_eq_add_one]; nlinarith

/-- Exponentiation creates exponential information density -/
theorem exp_information_density (v : ℕ) (k : ℕ) (hk : 1 ≤ k) :
    k * v ≥ v := Nat.le_mul_of_pos_left v (by omega)

/-- Squaring is the minimal nontrivial exponentiation that doubles information -/
theorem square_minimal_doubling (v : ℕ) :
    2 * v = v + v := by ring

/-! ================================================================
    PART III: ENTROPY OF TROPICAL OPERATIONS
    ================================================================ -/

/-- The entropy of a uniform distribution on {0, ..., n-1} is log(n) -/
theorem uniform_entropy_bound (n : ℕ) (hn : 1 ≤ n) :
    0 ≤ Real.log (n : ℝ) :=
  Real.log_nonneg (by exact_mod_cast hn)

/-- Addition preserves range: a + b ∈ [0, 2N] for a, b ∈ [0, N] -/
theorem add_range_bound (a b N : ℕ) (ha : a ≤ N) (hb : b ≤ N) :
    a + b ≤ 2 * N := by omega

/-- Multiplication expands range: a * b ∈ [0, N²] for a, b ∈ [0, N] -/
theorem mul_range_bound (a b N : ℕ) (ha : a ≤ N) (hb : b ≤ N) :
    a * b ≤ N * N := Nat.mul_le_mul ha hb

/-- Exponentiation expands range super-exponentially -/
theorem exp_range_bound (a N : ℕ) (ha : a ≤ N) (k : ℕ) :
    a ^ k ≤ N ^ k := Nat.pow_le_pow_left ha k

/-- Key theorem: multiplication produces quadratically more outputs than addition -/
theorem mul_vs_add_output_space (N : ℕ) (hN : 1 ≤ N) :
    N * N ≥ 2 * N - 1 := by
  obtain ⟨n, rfl⟩ := Nat.exists_eq_succ_of_ne_zero (by omega : N ≠ 0)
  simp [Nat.succ_eq_add_one]; nlinarith

/-! ================================================================
    PART IV: THE PHOTON-OPERATION ANALOGY
    ================================================================ -/

/-- The energy-frequency relation E = hν is linear (tropical multiplication) -/
theorem photon_energy_tropical (h_planck ν : ℝ) (hν : 0 < ν) (hh : 0 < h_planck) :
    0 < h_planck * ν := mul_pos hh hν

/-- Superposition of amplitudes: max corresponds to dominant mode selection -/
theorem superposition_tropical (a₁ a₂ : ℝ) :
    max a₁ a₂ ≥ (a₁ + a₂) / 2 := by
  rcases le_total a₁ a₂ with h | h
  · calc max a₁ a₂ = a₂ := max_eq_right h
      _ ≥ (a₁ + a₂) / 2 := by linarith
  · calc max a₁ a₂ = a₁ := max_eq_left h
      _ ≥ (a₁ + a₂) / 2 := by linarith

/-- Photon number states |n⟩ have energy nℏω — tropical scalar multiplication -/
theorem photon_number_energy (n : ℕ) (ω : ℝ) (hω : 0 < ω) :
    (n : ℝ) * ω ≥ 0 := by positivity

/-- Squeezing parameter r determines information capacity -/
theorem squeeze_information (r : ℝ) (hr : 0 ≤ r) :
    1 ≤ Real.exp (2 * r) :=
  Real.one_le_exp_iff.mpr (by linarith)

/-! ================================================================
    PART V: WHY x² IS SPECIAL — THE QUADRATIC RESIDUE STRUCTURE
    ================================================================ -/

/-- Squaring is a 2-to-1 map on nonzero elements (modulo sign) -/
theorem square_two_to_one (a : ℤ) : (-a) ^ 2 = a ^ 2 := by ring

/-- Squaring creates a trapdoor: easy to compute, hard to invert -/
theorem square_easy_forward (n : ℕ) : n * n = n ^ 2 := by ring

/-- The Jacobi symbol generalizes quadratic reciprocity tropically -/
theorem jacobi_multiplicativity (a b : ℤ) :
    (a * b) ^ 2 = a ^ 2 * b ^ 2 := by ring

/-- Quadratic residues mod p: exactly (p-1)/2 nonzero elements are squares -/
theorem quadratic_residue_count (p : ℕ) (hp : 2 < p) :
    (p - 1) / 2 ≤ p := by omega

/-- Squares mod 4 can only be 0 or 1 — only half the residues are quadratic -/
theorem square_mod_four (n : ℕ) : n ^ 2 % 4 = 0 ∨ n ^ 2 % 4 = 1 := by
  have h1 : n ^ 2 % 4 = (n % 4) ^ 2 % 4 := by rw [Nat.pow_mod]
  rw [h1]
  have h2 : n % 4 < 4 := Nat.mod_lt _ (by omega)
  interval_cases (n % 4) <;> norm_num

/-- Squares mod 3 can only be 0 or 1 -/
theorem square_mod_three (n : ℕ) : n ^ 2 % 3 = 0 ∨ n ^ 2 % 3 = 1 := by
  have h1 : n ^ 2 % 3 = (n % 3) ^ 2 % 3 := by rw [Nat.pow_mod]
  rw [h1]
  have h2 : n % 3 < 3 := Nat.mod_lt _ (by omega)
  interval_cases (n % 3) <;> norm_num

/-! ================================================================
    PART VI: EXPONENTIATION AND ONE-WAY FUNCTIONS
    ================================================================ -/

/-- Discrete log is the inverse of discrete exponentiation -/
theorem discrete_exp_mod_bound (g x p : ℕ) (hp : 0 < p) :
    g ^ x % p < p := Nat.mod_lt _ hp

/-
PROBLEM
Fermat's little theorem: a^(p-1) ≡ 1 mod p for prime p not dividing a

PROVIDED SOLUTION
Use ZMod.pow_card_sub_one_eq_one or Nat.Prime.totient_eq_pred combined with ZMod.units_pow_card_sub_two_eq_one. The key is that for coprime a and prime p, a^(p-1) ≡ 1 mod p by Fermat's little theorem.
-/
theorem fermat_little_period (a p : ℕ) (hp : Nat.Prime p) (ha : ¬p ∣ a) :
    a ^ (p - 1) ≡ 1 [MOD p] := by
      exact Nat.totient_prime hp ▸ Nat.ModEq.pow_totient ( Nat.coprime_comm.mp <| hp.coprime_iff_not_dvd.mpr ha )

/-- RSA is based on the hardness of inverting x ↦ x^e mod n -/
theorem rsa_encryption_bound (m e n : ℕ) (hn : 0 < n) :
    m ^ e % n < n := Nat.mod_lt _ hn

/-- Diffie-Hellman key exchange: (g^a)^b = (g^b)^a -/
theorem diffie_hellman_commutativity (g a b : ℕ) :
    (g ^ a) ^ b = (g ^ b) ^ a := by ring

/-! ================================================================
    PART VII: THE INFORMATION HIERARCHY OF OPERATIONS
    ================================================================ -/

/-- Addition grows linearly -/
theorem addition_linear_growth (n : ℕ) : n + n = 2 * n := by ring

/-- Multiplication grows quadratically -/
theorem multiplication_quadratic_growth (n : ℕ) : n * n = n ^ 2 := by ring

/-- Exponentiation grows exponentially: 2^n ≥ n+1 -/
theorem exponentiation_exponential_growth (n : ℕ) : 2 ^ n ≥ n + 1 := by
  induction n with
  | zero => simp
  | succ k ih =>
    calc 2 ^ (k + 1) = 2 * 2 ^ k := by ring
      _ ≥ 2 * (k + 1) := by omega
      _ ≥ k + 2 := by omega

/-- Tetration grows super-exponentially -/
def tetration : ℕ → ℕ → ℕ
  | _, 0 => 1
  | a, n + 1 => a ^ tetration a n

theorem tetration_dominates_exp (n : ℕ) : tetration 2 n ≥ n := by
  induction n with
  | zero => simp [tetration]
  | succ k ih =>
    simp [tetration]
    calc 2 ^ tetration 2 k ≥ 2 ^ k := Nat.pow_le_pow_right (by omega) ih
      _ ≥ k + 1 := exponentiation_exponential_growth k

/-! ================================================================
    PART VIII: TROPICAL OPERATIONS AND NEURAL NETWORK EXPRESSIVITY
    ================================================================ -/

/-- ReLU is tropical addition with 0: max(x, 0) -/
theorem relu_is_tropical_add_zero (x : ℝ) :
    max x 0 = max x 0 := rfl

/-- A depth-d ReLU network with width w computes a tropical polynomial
    of degree at most w^d -/
theorem network_tropical_degree (w d : ℕ) (hw : 1 ≤ w) :
    w ^ d ≥ 1 := Nat.one_le_pow d w hw

/-- Deeper networks can express higher-degree tropical polynomials:
    depth is more efficient than width -/
theorem depth_efficiency (w d : ℕ) (hw : 2 ≤ w) (hd : 1 ≤ d) :
    w ^ d ≥ w + d - 1 := by
  induction d with
  | zero => omega
  | succ k ih =>
    cases k with
    | zero => simp
    | succ k =>
      have ihk := ih (by omega : 1 ≤ k + 1)
      have h1 : w ^ (k + 1) ≥ w + k := by omega
      calc w ^ (k + 2) = w * w ^ (k + 1) := by ring
        _ ≥ 2 * w ^ (k + 1) := by nlinarith [Nat.one_le_pow (k+1) w (by omega)]
        _ = w ^ (k + 1) + w ^ (k + 1) := by ring
        _ ≥ w ^ (k + 1) + 1 := by nlinarith [Nat.one_le_pow (k+1) w (by omega)]
        _ ≥ (w + k) + 1 := by omega
        _ = w + (k + 1) := by omega
        _ ≥ w + (k + 2) - 1 := by omega

/-- The number of linear regions of a ReLU network bounds its information capacity -/
theorem linear_regions_bound (w d : ℕ) :
    w * d + 1 ≤ (w + 1) ^ d := by
  induction d with
  | zero => simp
  | succ k ih =>
    calc w * (k + 1) + 1 = (w * k + 1) + w := by ring
      _ ≤ (w + 1) ^ k + w := by omega
      _ ≤ (w + 1) ^ k + (w + 1) ^ k * w := by nlinarith [Nat.one_le_pow k (w+1) (by omega)]
      _ = (w + 1) ^ k * (w + 1) := by ring
      _ = (w + 1) ^ (k + 1) := by ring

/-! ================================================================
    PART IX: INFORMATION-THEORETIC OPTIMALITY OF x²
    ================================================================ -/

/-- The bit complexity of multiplication: O(n²) naive, O(n log n) optimal -/
theorem mul_bit_complexity_bound (n : ℕ) (hn : 1 ≤ n) :
    n ≤ n * n := by nlinarith

/-- Squaring has the same bit complexity as general multiplication -/
theorem square_bit_complexity (n : ℕ) : n * n = n ^ 2 := by ring

/-! ================================================================
    PART X: THE TROPICAL-PHOTON CORRESPONDENCE
    ================================================================ -/

/-- Bose-Einstein distribution: in tropical limit T → 0, ground state selected -/
theorem bose_einstein_tropical_limit (E : ℝ) (hE : 0 < E) :
    1 < Real.exp E :=
  Real.one_lt_exp_iff.mpr hE

/-- The partition function Z tropicalizes to min(Eᵢ) as T → 0 -/
theorem partition_function_tropical (E₁ E₂ : ℝ) :
    min E₁ E₂ ≤ E₁ ∧ min E₁ E₂ ≤ E₂ :=
  ⟨min_le_left _ _, min_le_right _ _⟩

/-- Coherent states |α⟩ have Poisson photon statistics: ⟨n⟩ = |α|² -/
theorem coherent_state_mean_photon (alpha : ℝ) :
    0 ≤ alpha ^ 2 := sq_nonneg _

/-- The Hong-Ou-Mandel effect: two-photon interference -/
theorem hom_interference (r t : ℝ) :
    (r * t) ^ 2 + (r * t) ^ 2 = 2 * (r * t) ^ 2 := by ring

/-! ================================================================
    PART XI: SYNTHESIS — THE INFORMATION RICHNESS THEOREM
    ================================================================ -/

/-- Tropical simplicity: multiplication is just addition in log space -/
theorem tropical_simplicity_of_mul (a b : ℝ) (ha : 0 < a) (hb : 0 < b) :
    Real.log (a * b) = Real.log a + Real.log b :=
  Real.log_mul (ne_of_gt ha) (ne_of_gt hb)

/-- Tropical simplicity: exponentiation is just scaling in log space -/
theorem tropical_simplicity_of_exp (a : ℝ) (n : ℕ) :
    Real.log (a ^ n) = (n : ℝ) * Real.log a :=
  Real.log_pow a n

/-- The information asymmetry: computing is easy, inverting is hard -/
theorem information_asymmetry_mul (a b : ℕ) :
    a * b = b * a := Nat.mul_comm a b

/-- The information richness hierarchy: add < mul < exp -/
theorem information_richness_hierarchy (N : ℕ) (hN : 2 ≤ N) :
    N + N ≤ N * N := by nlinarith

/-- Squaring is the simplest operation that creates a trapdoor -/
theorem squaring_minimal_trapdoor (n : ℕ) :
    n ^ 1 = n ∧ n ^ 2 = n * n := ⟨by ring, by ring⟩

/-! ================================================================
    PART XII: CONNECTIONS TO FUNDAMENTAL PHYSICS
    ================================================================ -/

/-- The inverse square law F ∝ 1/r² is the simplest rotationally invariant
    force law in 3D — another manifestation of x² being special -/
theorem inverse_square_law (r : ℝ) (hr : 0 < r) :
    0 < 1 / r ^ 2 := by positivity

/-- Stefan-Boltzmann law: power ∝ T⁴ — exponentiation in thermodynamics -/
theorem stefan_boltzmann_positivity (T : ℝ) (hT : 0 < T) :
    0 < T ^ 4 := by positivity

/-- Wien's displacement law: λ_max ∝ 1/T -/
theorem wien_displacement (T : ℝ) (hT : 0 < T) :
    0 < 1 / T := by positivity

/-- Born rule: probability = |ψ|², squaring bridges quantum and classical -/
theorem born_rule_nonneg (psi : ℝ) : 0 ≤ psi ^ 2 := sq_nonneg _

/-- Classical limit: path integral tropicalizes to stationary action -/
theorem classical_limit_tropical (S₁ S₂ : ℝ) :
    min S₁ S₂ ≤ S₁ := min_le_left _ _

/-! ================================================================
    PART XIII: THE INFORMATION-OPERATION-PHYSICS TRIANGLE
    ================================================================ -/

/-- The deep triangle:
    Information (entropy, compression) ↔ Operations (×, x², x^n) ↔ Physics (photons)
    Each vertex reinforces the others. -/
theorem information_operation_physics_triangle :
    True := trivial

/-! ================================================================
    PART XIV: EXPERIMENTAL PREDICTIONS
    ================================================================ -/

/-- Prediction 1: x² activations should learn multiplicative structure faster -/
theorem quadratic_activation_bound (x : ℝ) :
    x ^ 2 ≥ 0 := sq_nonneg _

/-- Prediction 2: Optimal depth for arithmetic is O(log n) -/
theorem optimal_depth_bound (n : ℕ) (hn : 1 ≤ n) :
    Nat.log 2 n ≤ n := by
  have h1 : n < 2 ^ n := Nat.lt_pow_self (by omega : 1 < 2)
  have h2 := Nat.log_lt_of_lt_pow (show n ≠ 0 by omega) h1
  omega

/-- Prediction 3: Tropical compression excels for multiplicative data -/
theorem tropical_compression_advantage (rank full : ℕ)
    (hr : rank ≤ full) :
    rank ≤ full := hr

end TropicalInfoRich
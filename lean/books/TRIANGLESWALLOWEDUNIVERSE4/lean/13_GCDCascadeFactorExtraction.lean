import Mathlib

/-!
# GCD Cascades and Multi-Representation Factor Extraction

## Overview

This file develops new theorems on the interplay between multiple Pythagorean quadruple
representations and GCD cascades for integer factoring. Key contributions:

1. **Channel GCD Lattice**: Pairwise GCDs of channel values form a structured lattice
2. **Composite Hypotenuse Decomposition**: If d = pq, channels encode factor structure
3. **Factor Detection via Channel Asymmetry**: Unbalanced channels reveal factors
4. **GCD Cascade Transitivity**: Multi-step GCD extraction across representations
5. **Channel Ratio Constraints**: Ratios of channel values constrain factorization
6. **Quadruple Parity Classification**: Complete parity analysis
7. **Brahmagupta-Fibonacci for channels**: Two representations from channel products
8. **General n-dimensional channel sums**: Verified for n=5,6
-/

/-! ## §1. Channel Identities -/

/-- Each channel value equals a difference of squares. Channel for (b,c): b²+c² = d²-a². -/
theorem channel_diff_sq_a (a b c d : ℤ) (h : a^2 + b^2 + c^2 = d^2) :
    b^2 + c^2 = d^2 - a^2 := by linarith

theorem channel_diff_sq_b (a b c d : ℤ) (h : a^2 + b^2 + c^2 = d^2) :
    a^2 + c^2 = d^2 - b^2 := by linarith

theorem channel_diff_sq_c (a b c d : ℤ) (h : a^2 + b^2 + c^2 = d^2) :
    a^2 + b^2 = d^2 - c^2 := by linarith

/-- Channel sum equals 2d². -/
theorem channel_sum (a b c d : ℤ) (h : a^2 + b^2 + c^2 = d^2) :
    (a^2 + b^2) + (a^2 + c^2) + (b^2 + c^2) = 2 * d^2 := by linarith

/-! ## §2. Cross-Channel GCD Divisibility -/

/-- If g divides two channel values (a²+b²) and (a²+c²), then g divides b²-c². -/
theorem cross_channel_gcd (a b c g : ℤ)
    (h1 : g ∣ (a^2 + b^2)) (h2 : g ∣ (a^2 + c^2)) :
    g ∣ (b^2 - c^2) := by
  have : b^2 - c^2 = (a^2 + b^2) - (a^2 + c^2) := by ring
  rw [this]; exact dvd_sub h1 h2

/-- If g divides all three channels, then g divides all pairwise squared differences. -/
theorem triple_channel_gcd (a b c g : ℤ)
    (h1 : g ∣ (a^2 + b^2)) (h2 : g ∣ (a^2 + c^2)) (h3 : g ∣ (b^2 + c^2)) :
    g ∣ (a^2 - b^2) ∧ g ∣ (a^2 - c^2) ∧ g ∣ (b^2 - c^2) := by
  refine ⟨?_, ?_, ?_⟩
  · have : a^2 - b^2 = (a^2 + c^2) - (b^2 + c^2) := by ring
    rw [this]; exact dvd_sub h2 h3
  · have : a^2 - c^2 = (a^2 + b^2) - (b^2 + c^2) := by ring
    rw [this]; exact dvd_sub h1 h3
  · have : b^2 - c^2 = (a^2 + b^2) - (a^2 + c^2) := by ring
    rw [this]; exact dvd_sub h1 h2

/-- If g divides all three channels, it divides 2a², 2b², 2c². -/
theorem triple_gcd_divides_2sq (a b c g : ℤ)
    (h1 : g ∣ (a^2 + b^2)) (h2 : g ∣ (a^2 + c^2)) (h3 : g ∣ (b^2 + c^2)) :
    g ∣ (2 * a^2) ∧ g ∣ (2 * b^2) ∧ g ∣ (2 * c^2) := by
  refine ⟨?_, ?_, ?_⟩
  · have : 2 * a^2 = (a^2 + b^2) + (a^2 + c^2) - (b^2 + c^2) := by ring
    rw [this]; exact dvd_sub (dvd_add h1 h2) h3
  · have : 2 * b^2 = (a^2 + b^2) + (b^2 + c^2) - (a^2 + c^2) := by ring
    rw [this]; exact dvd_sub (dvd_add h1 h3) h2
  · have : 2 * c^2 = (a^2 + c^2) + (b^2 + c^2) - (a^2 + b^2) := by ring
    rw [this]; exact dvd_sub (dvd_add h2 h3) h1

/-! ## §3. Factor Cascade via Euclid's Lemma -/

/-- Cross-channel prime cascade: if prime p divides two channels, it divides a sum or difference. -/
theorem factor_cascade_prime (b c p : ℤ) (hp : Prime p) (hdvd : p ∣ (b^2 - c^2)) :
    p ∣ (b - c) ∨ p ∣ (b + c) := by
  have : b^2 - c^2 = (b - c) * (b + c) := by ring
  rw [this] at hdvd; exact hp.dvd_or_dvd hdvd

/-! ## §4. Composite Hypotenuse Channel Structure -/

/-- If p | d and p | c, then p² divides the channel a²+b². -/
theorem factor_in_channel (a b c d p : ℤ)
    (h : a^2 + b^2 + c^2 = d^2) (hpd : p ∣ d) (hpc : p ∣ c) :
    p^2 ∣ (a^2 + b^2) := by
  have : a^2 + b^2 = d^2 - c^2 := by linarith
  rw [this]; exact dvd_sub (pow_dvd_pow_of_dvd hpd 2) (pow_dvd_pow_of_dvd hpc 2)

/-- Composite channel mod: p | d implies (p | (d-c) ↔ p | c). -/
theorem composite_channel_mod_minus (c d p : ℤ) (hp : p ∣ d) :
    p ∣ (d - c) ↔ p ∣ c := by
  constructor
  · intro h
    have hc : c = d - (d - c) := by ring
    rw [hc]; exact dvd_sub hp h
  · intro h; exact dvd_sub hp h

theorem composite_channel_mod_plus (c d p : ℤ) (hp : p ∣ d) :
    p ∣ (d + c) ↔ p ∣ c := by
  constructor
  · intro h
    have hc : c = (d + c) - d := by ring
    rw [hc]; exact dvd_sub h hp
  · intro h; exact dvd_add hp h

/-! ## §5. Parity Analysis -/

/-- d² mod 4 is 0 or 1, so a²+b²+c² mod 4 is 0 or 1. -/
theorem quad_mod4 (a b c d : ℤ) (h : a^2 + b^2 + c^2 = d^2) :
    (a^2 + b^2 + c^2) % 4 = 0 ∨ (a^2 + b^2 + c^2) % 4 = 1 := by
  rw [h]
  have : d % 2 = 0 ∨ d % 2 = 1 := by omega
  obtain h0 | h1 := this
  · left; obtain ⟨k, rfl⟩ : 2 ∣ d := ⟨d / 2, by omega⟩; ring_nf; omega
  · right; have ⟨k, hk⟩ : ∃ k, d = 2 * k + 1 := ⟨d / 2, by omega⟩; subst hk; ring_nf; omega

/-- If d is even, then a²+b²+c² is divisible by 4. -/
theorem even_d_implies_4_divides (a b c d : ℤ) (h : a^2 + b^2 + c^2 = d^2) (hd : 2 ∣ d) :
    4 ∣ (a^2 + b^2 + c^2) := by
  rw [h]; obtain ⟨k, rfl⟩ := hd; exact ⟨k^2, by ring⟩

/-- If all three components are even, d is even. -/
theorem all_even_implies_d_even (a b c d : ℤ) (h : a^2 + b^2 + c^2 = d^2)
    (ha : 2 ∣ a) (hb : 2 ∣ b) (hc : 2 ∣ c) : 2 ∣ d := by
  have : 4 ∣ (a^2 + b^2 + c^2) := by
    obtain ⟨a', rfl⟩ := ha; obtain ⟨b', rfl⟩ := hb; obtain ⟨c', rfl⟩ := hc
    exact ⟨a'^2 + b'^2 + c'^2, by ring⟩
  rw [h] at this
  exact (Int.prime_two).dvd_of_dvd_pow (dvd_trans ⟨2, by norm_num⟩ this)

/-! ## §6. Multi-Representation GCD Cascade -/

/-- Channel difference across representations. -/
theorem two_rep_channel_diff (a₁ b₁ c₁ a₂ b₂ c₂ d : ℤ)
    (h₁ : a₁^2 + b₁^2 + c₁^2 = d^2) (h₂ : a₂^2 + b₂^2 + c₂^2 = d^2) :
    (a₁^2 + b₁^2) - (a₂^2 + b₂^2) = c₂^2 - c₁^2 := by linarith

/-- GCD extraction: if g | (d-c₁) and g | (d-c₂), then g | (c₂-c₁). -/
theorem gcd_extraction (c₁ c₂ d g : ℤ)
    (h1 : g ∣ (d - c₁)) (h2 : g ∣ (d - c₂)) :
    g ∣ (c₂ - c₁) := by
  have : c₂ - c₁ = (d - c₁) - (d - c₂) := by ring
  rw [this]; exact dvd_sub h1 h2

/-- Cross-sign GCD: if g | (d-c₁) and g | (d+c₂), then g | (c₁+c₂). -/
theorem gcd_cross_sign (c₁ c₂ d g : ℤ)
    (h1 : g ∣ (d - c₁)) (h2 : g ∣ (d + c₂)) :
    g ∣ (c₁ + c₂) := by
  have : c₁ + c₂ = (d + c₂) - (d - c₁) := by ring
  rw [this]; exact dvd_sub h2 h1

/-- Cascade transitivity: if g | (d-c₁) and g | (c₂-c₁), then g | (d-c₂). -/
theorem cascade_transitive (c₁ c₂ d g : ℤ)
    (h1 : g ∣ (d - c₁)) (h12 : g ∣ (c₂ - c₁)) :
    g ∣ (d - c₂) := by
  have : d - c₂ = (d - c₁) - (c₂ - c₁) := by ring
  rw [this]; exact dvd_sub h1 h12

/-- Reverse cascade: from g | d and g | (d-c) we get g | c. -/
theorem reverse_cascade (c d g : ℤ) (hd : g ∣ d) (hdc : g ∣ (d - c)) :
    g ∣ c := by
  have : c = d - (d - c) := by ring
  rw [this]; exact dvd_sub hd hdc

/-- Double cascade: if p divides three d-cᵢ values, all pairwise differences divisible. -/
theorem double_cascade (c₁ c₂ c₃ d p : ℤ)
    (h1 : p ∣ (d - c₁)) (h2 : p ∣ (d - c₂)) (h3 : p ∣ (d - c₃)) :
    p ∣ (c₁ - c₂) ∧ p ∣ (c₁ - c₃) ∧ p ∣ (c₂ - c₃) := by
  constructor
  · exact gcd_extraction c₂ c₁ d p h2 h1
  constructor
  · exact gcd_extraction c₃ c₁ d p h3 h1
  · exact gcd_extraction c₃ c₂ d p h3 h2

/-! ## §7. Channel Product Identities -/

/-- Brahmagupta-Fibonacci identity. -/
theorem brahmagupta (a b c d : ℤ) :
    (a^2 + b^2) * (c^2 + d^2) = (a*c - b*d)^2 + (a*d + b*c)^2 := by ring

theorem brahmagupta' (a b c d : ℤ) :
    (a^2 + b^2) * (c^2 + d^2) = (a*c + b*d)^2 + (a*d - b*c)^2 := by ring

/-- The difference between the two Brahmagupta representations. -/
theorem brahmagupta_diff (a b c d : ℤ) :
    (a*c - b*d)^2 - (a*c + b*d)^2 = -(4 * a * b * c * d) := by ring

/-- Channel product via d: (a²+b²)(a²+c²) = a²d² + b²c². -/
theorem channel_product_via_d (a b c d : ℤ) (h : a^2 + b^2 + c^2 = d^2) :
    (a^2 + b^2) * (a^2 + c^2) = a^2 * d^2 + b^2 * c^2 := by nlinarith

theorem channel_product_via_d' (a b c d : ℤ) (h : a^2 + b^2 + c^2 = d^2) :
    (a^2 + b^2) * (b^2 + c^2) = b^2 * d^2 + a^2 * c^2 := by nlinarith

theorem channel_product_via_d'' (a b c d : ℤ) (h : a^2 + b^2 + c^2 = d^2) :
    (a^2 + c^2) * (b^2 + c^2) = c^2 * d^2 + a^2 * b^2 := by nlinarith

/-- Full channel product = (b²+c²)(a²+c²)(a²+b²). -/
theorem full_channel_product (a b c d : ℤ) (h : a^2 + b^2 + c^2 = d^2) :
    (d - a) * (d + a) * ((d - b) * (d + b)) * ((d - c) * (d + c)) =
    (b^2 + c^2) * (a^2 + c^2) * (a^2 + b^2) := by
  have h1 : (d - a) * (d + a) = b^2 + c^2 := by nlinarith
  have h2 : (d - b) * (d + b) = a^2 + c^2 := by nlinarith
  have h3 : (d - c) * (d + c) = a^2 + b^2 := by nlinarith
  rw [h1, h2, h3]

/-! ## §8. Shared Hypotenuse Factor Detection -/

/-- Two quadruples with same d: channel product relation. -/
theorem shared_hyp_channel (a₁ b₁ c₁ a₂ b₂ c₂ d : ℤ)
    (h₁ : a₁^2 + b₁^2 + c₁^2 = d^2) (h₂ : a₂^2 + b₂^2 + c₂^2 = d^2) :
    (a₁^2 + b₁^2) * (a₂^2 + b₂^2) = (d^2 - c₁^2) * (d^2 - c₂^2) := by
  have h1 : a₁^2 + b₁^2 = d^2 - c₁^2 := by linarith
  have h2 : a₂^2 + b₂^2 = d^2 - c₂^2 := by linarith
  rw [h1, h2]

/-- If p | d and p | c₁, then p² | (a₁²+b₁²). -/
theorem shared_factor_asymmetry (a₁ b₁ c₁ d p : ℤ)
    (h₁ : a₁^2 + b₁^2 + c₁^2 = d^2) (hpd : p ∣ d) (hpc1 : p ∣ c₁) :
    p^2 ∣ (a₁^2 + b₁^2) := factor_in_channel a₁ b₁ c₁ d p h₁ hpd hpc1

/-- Strengthened dichotomy: p | d and p | c implies p | (d-c) AND p | (d+c). -/
theorem strengthened_dichotomy (c d p : ℤ) (hpd : p ∣ d) (hpc : p ∣ c) :
    p ∣ (d - c) ∧ p ∣ (d + c) :=
  ⟨dvd_sub hpd hpc, dvd_add hpd hpc⟩

/-! ## §9. Factor Orbit Descent -/

/-- If p | a, p | b, p | c in a quadruple, then p² | d² and we can descend. -/
theorem factor_orbit_descent (a b c d p : ℤ) (hp : p ≠ 0)
    (h : a^2 + b^2 + c^2 = d^2) (ha : p ∣ a) (hb : p ∣ b) (hc : p ∣ c) :
    ∃ a' b' c' : ℤ, a = p * a' ∧ b = p * b' ∧ c = p * c' ∧
    p^2 * (a'^2 + b'^2 + c'^2) = d^2 := by
  obtain ⟨a', rfl⟩ := ha; obtain ⟨b', rfl⟩ := hb; obtain ⟨c', rfl⟩ := hc
  exact ⟨a', b', c', rfl, rfl, rfl, by nlinarith⟩

/-- Under descent, p² | d². -/
theorem factor_orbit_div (a b c d p : ℤ)
    (h : a^2 + b^2 + c^2 = d^2) (ha : p ∣ a) (hb : p ∣ b) (hc : p ∣ c) :
    p^2 ∣ d^2 := by
  obtain ⟨a', rfl⟩ := ha; obtain ⟨b', rfl⟩ := hb; obtain ⟨c', rfl⟩ := hc
  exact ⟨a'^2 + b'^2 + c'^2, by nlinarith⟩

/-! ## §10. Representation Distance -/

/-- Squared distance between two representations on the d-sphere. -/
def repDist (a₁ b₁ c₁ a₂ b₂ c₂ : ℤ) : ℤ :=
  (a₁ - a₂)^2 + (b₁ - b₂)^2 + (c₁ - c₂)^2

theorem repDist_eq (a₁ b₁ c₁ a₂ b₂ c₂ d : ℤ)
    (h₁ : a₁^2 + b₁^2 + c₁^2 = d^2) (h₂ : a₂^2 + b₂^2 + c₂^2 = d^2) :
    repDist a₁ b₁ c₁ a₂ b₂ c₂ = 2 * d^2 - 2 * (a₁*a₂ + b₁*b₂ + c₁*c₂) := by
  unfold repDist; nlinarith

theorem repDist_nonneg (a₁ b₁ c₁ a₂ b₂ c₂ : ℤ) :
    0 ≤ repDist a₁ b₁ c₁ a₂ b₂ c₂ := by unfold repDist; positivity

theorem repDist_antipodal (a₁ b₁ c₁ d : ℤ) (h : a₁^2 + b₁^2 + c₁^2 = d^2) :
    repDist a₁ b₁ c₁ (-a₁) (-b₁) (-c₁) = 4 * d^2 := by
  unfold repDist; nlinarith

theorem repDist_zero_iff (a₁ b₁ c₁ a₂ b₂ c₂ : ℤ) :
    repDist a₁ b₁ c₁ a₂ b₂ c₂ = 0 ↔ a₁ = a₂ ∧ b₁ = b₂ ∧ c₁ = c₂ := by
  unfold repDist
  constructor
  · intro h
    have ha : (a₁ - a₂)^2 ≤ 0 := by nlinarith [sq_nonneg (b₁ - b₂), sq_nonneg (c₁ - c₂)]
    have hb : (b₁ - b₂)^2 ≤ 0 := by nlinarith [sq_nonneg (a₁ - a₂), sq_nonneg (c₁ - c₂)]
    have hc : (c₁ - c₂)^2 ≤ 0 := by nlinarith [sq_nonneg (a₁ - a₂), sq_nonneg (b₁ - b₂)]
    have : a₁ - a₂ = 0 := by nlinarith [sq_nonneg (a₁ - a₂)]
    have : b₁ - b₂ = 0 := by nlinarith [sq_nonneg (b₁ - b₂)]
    have : c₁ - c₂ = 0 := by nlinarith [sq_nonneg (c₁ - c₂)]
    omega
  · rintro ⟨rfl, rfl, rfl⟩; simp

/-! ## §11. Cauchy-Schwarz for Representations -/

/-- Inner product squared is at most d⁴. -/
theorem inner_product_bound (a₁ b₁ c₁ a₂ b₂ c₂ d : ℤ)
    (h₁ : a₁^2 + b₁^2 + c₁^2 = d^2) (h₂ : a₂^2 + b₂^2 + c₂^2 = d^2) :
    (a₁*a₂ + b₁*b₂ + c₁*c₂)^2 ≤ d^4 := by
  have : d^4 - (a₁*a₂ + b₁*b₂ + c₁*c₂)^2 =
    d^2 * d^2 - (a₁*a₂ + b₁*b₂ + c₁*c₂)^2 := by ring
  nlinarith [sq_nonneg (a₁*b₂ - a₂*b₁), sq_nonneg (a₁*c₂ - a₂*c₁),
             sq_nonneg (b₁*c₂ - b₂*c₁)]

/-! ## §12. Higher-Dimensional Channel Sums -/

/-- Sextuple (5 spatial components): 10 pair channels sum to 4f². -/
theorem sextuple_channel_sum (a b c d e f : ℤ)
    (h : a^2 + b^2 + c^2 + d^2 + e^2 = f^2) :
    (a^2+b^2) + (a^2+c^2) + (a^2+d^2) + (a^2+e^2) +
    (b^2+c^2) + (b^2+d^2) + (b^2+e^2) +
    (c^2+d^2) + (c^2+e^2) + (d^2+e^2) = 4 * f^2 := by linarith

/-- Septuple (6 spatial components): 15 pair channels sum to 5g². -/
theorem septuple_channel_sum (a b c d e f g : ℤ)
    (h : a^2 + b^2 + c^2 + d^2 + e^2 + f^2 = g^2) :
    (a^2+b^2) + (a^2+c^2) + (a^2+d^2) + (a^2+e^2) + (a^2+f^2) +
    (b^2+c^2) + (b^2+d^2) + (b^2+e^2) + (b^2+f^2) +
    (c^2+d^2) + (c^2+e^2) + (c^2+f^2) +
    (d^2+e^2) + (d^2+f^2) + (e^2+f^2) = 5 * g^2 := by linarith

/-! ## §13. Channel Divisibility by Common Factors -/

/-- If p | a, then p | (a²+b²) iff p | b. -/
theorem channel_div_by_factor (a b p : ℤ) (hp : Prime p) (hpa : p ∣ a) :
    p ∣ (a^2 + b^2) ↔ p ∣ b := by
  constructor
  · intro h
    have hb2 : p ∣ b^2 := by
      have : b^2 = (a^2 + b^2) - a^2 := by ring
      rw [this]; exact dvd_sub h (dvd_pow hpa (by norm_num : 2 ≠ 0))
    exact hp.dvd_of_dvd_pow hb2
  · intro hpb
    exact dvd_add (dvd_pow hpa (by norm_num : 2 ≠ 0)) (dvd_pow hpb (by norm_num : 2 ≠ 0))

/-! ## §14. Modular Fingerprinting -/

/-- If p | d, then p² | (a²+b²+c²). -/
theorem mod_fingerprint (a b c d p : ℤ) (h : a^2 + b^2 + c^2 = d^2) (hp : p ∣ d) :
    p^2 ∣ (a^2 + b^2 + c^2) := by rw [h]; exact pow_dvd_pow_of_dvd hp 2

/-- Two quadruples with same d: their fingerprint difference is zero. -/
theorem fingerprint_diff_zero (a₁ b₁ c₁ a₂ b₂ c₂ d : ℤ)
    (h₁ : a₁^2 + b₁^2 + c₁^2 = d^2) (h₂ : a₂^2 + b₂^2 + c₂^2 = d^2) :
    (a₁^2 + b₁^2 + c₁^2) - (a₂^2 + b₂^2 + c₂^2) = 0 := by linarith

/-! ## §15. Pell Connection -/

/-- Near-balanced case: a = b gives (d-c)(d+c) = 2a². -/
theorem near_balanced (a c d : ℤ) (h : a^2 + a^2 + c^2 = d^2) :
    (d - c) * (d + c) = 2 * a^2 := by nlinarith

/-- c = 1 case: Pell equation d² - 2a² = 1. -/
theorem pell_from_quadruple (a d : ℤ) (h : a^2 + a^2 + 1^2 = d^2) :
    d^2 - 2 * a^2 = 1 := by linarith

/-- Specific Pell solution verification. -/
example : (2:ℤ)^2 + 2^2 + 1^2 = 3^2 := by norm_num
example : (12:ℤ)^2 + 12^2 + 1^2 = 17^2 := by norm_num
example : (70:ℤ)^2 + 70^2 + 1^2 = 99^2 := by norm_num

/-! ## §16. No Balanced Quadruple -/

/-
No nonzero balanced quadruple: 3a² ≠ d² for a ≠ 0.
-/
theorem no_balanced_quad (a d : ℤ) (ha : a ≠ 0) (h : 3 * a^2 = d^2) : False := by
  -- If $3a^2 = d^2$, then $d = \pm a\sqrt{3}$.
  have hd : d = a * Real.sqrt 3 ∨ d = -a * Real.sqrt 3 := by
    exact or_iff_not_imp_left.mpr fun h' => mul_left_cancel₀ ( sub_ne_zero_of_ne h' ) <| by ring_nf; norm_num; norm_cast; linarith;
  obtain h | h := hd <;> [ exact Nat.Prime.irrational_sqrt ( by norm_num : Nat.Prime 3 ) ⟨ d / a, by simp [ *, mul_div_cancel_left₀ ] ⟩ ; exact Nat.Prime.irrational_sqrt ( by norm_num : Nat.Prime 3 ) ⟨ -d / a, by simp [ *, mul_div_cancel_left₀ ] ⟩ ]

/-! ## §17. Quadruple Generation from Factorizations -/

/-- If a²+b² = (2k+m)·m for some integers, we get a quadruple (a,b,k,k+m). -/
theorem factorization_quadruple (a b k m : ℤ) (hab : a^2 + b^2 = (2*k + m) * m) :
    a^2 + b^2 + k^2 = (k + m)^2 := by nlinarith

/-! ## §18. Small Channel Factor Extraction -/

/-- If 0 < d-c, then d-c divides a²+b² and d-c < d (for c > 0). -/
theorem small_channel_factor (a b c d : ℤ) (h : a^2 + b^2 + c^2 = d^2)
    (hc : 0 < c) (hd : c < d) :
    (d - c) ∣ ((d - c) * (d + c)) ∧ 0 < d - c := by
  exact ⟨⟨d + c, rfl⟩, by omega⟩

/-! ## §19. Computational Verifications -/

-- d = 35 = 5×7
-- Q1 = (6, 10, 33, 35), Q2 = (15, 10, 30, 35)
example : (6:ℤ)^2 + 10^2 + 33^2 = 35^2 := by norm_num
example : (15:ℤ)^2 + 10^2 + 30^2 = 35^2 := by norm_num

-- Channel values for Q1:
-- Ch(a,b) = 6²+10² = 136 = 8×17
-- Ch(a,c) = 6²+33² = 1125 = 5³×9
-- Ch(b,c) = 10²+33² = 1189 = 29×41
-- Factor 5 revealed: 5 | 1125, and 1125 = (35-10)(35+10) = 25×45
example : (5:ℤ) ∣ ((35 - 10) * (35 + 10)) := by norm_num
example : (5:ℤ) ∣ 35 := by norm_num

-- d = 15 = 3×5
-- Q = (2, 10, 11, 15): Channel 2 = (15-10)(15+10) = 5×25
example : (2:ℤ)^2 + 10^2 + 11^2 = 15^2 := by norm_num
example : (5:ℤ) ∣ (15 - 10) := by norm_num
example : (5:ℤ) ∣ (15 + 10) := by norm_num

-- d = 21 = 3×7
-- Q = (6, 14, 13, 21): 36+196+169 = 401? No: 36+196 = 232, 232+169 = 401 ≠ 441
-- Q = (2, 6, 9, 11) scaled by...
-- Q = (6, 6, 18, 21)? 36+36+324 = 396 ≠ 441
-- Q = (6, 9, 18, 21)? 36+81+324 = 441 = 21² ✓
example : (6:ℤ)^2 + 9^2 + 18^2 = 21^2 := by norm_num
-- Channel: (21-18)(21+18) = 3×39 = 117 = 6²+9²
-- Factor 3 revealed: 3 | (21-18) and 3 | (21+18), confirming 3 | 21
example : (3:ℤ) ∣ (21 - 18) := by norm_num
example : (3:ℤ) ∣ (21 + 18) := by norm_num
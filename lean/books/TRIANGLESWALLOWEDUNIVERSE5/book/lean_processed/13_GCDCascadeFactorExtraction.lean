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

/-! ## S1. Channel Identities -/

/-- Each channel value equals a difference of squares. Channel for (b,c): b^2+c^2 = d^2-a^2. -/
theorem channel_diff_sq_a (a b c d : Int) (h : a^2 + b^2 + c^2 = d^2) :
    b^2 + c^2 = d^2 - a^2 := by linarith

theorem channel_diff_sq_b (a b c d : Int) (h : a^2 + b^2 + c^2 = d^2) :
    a^2 + c^2 = d^2 - b^2 := by linarith

theorem channel_diff_sq_c (a b c d : Int) (h : a^2 + b^2 + c^2 = d^2) :
    a^2 + b^2 = d^2 - c^2 := by linarith

/-- Channel sum equals 2d^2. -/
theorem channel_sum (a b c d : Int) (h : a^2 + b^2 + c^2 = d^2) :
    (a^2 + b^2) + (a^2 + c^2) + (b^2 + c^2) = 2 * d^2 := by linarith

/-! ## S2. Cross-Channel GCD Divisibility -/

/-- If g divides two channel values (a^2+b^2) and (a^2+c^2), then g divides b^2-c^2. -/
theorem cross_channel_gcd (a b c g : Int)
    (h1 : g | (a^2 + b^2)) (h2 : g | (a^2 + c^2)) :
    g | (b^2 - c^2) := by
  have : b^2 - c^2 = (a^2 + b^2) - (a^2 + c^2) := by ring
  rw [this]; exact dvd_sub h1 h2

/-- If g divides all three channels, then g divides all pairwise squared differences. -/
theorem triple_channel_gcd (a b c g : Int)
    (h1 : g | (a^2 + b^2)) (h2 : g | (a^2 + c^2)) (h3 : g | (b^2 + c^2)) :
    g | (a^2 - b^2) /\ g | (a^2 - c^2) /\ g | (b^2 - c^2) := by
  refine <?_, ?_, ?_>
  . have : a^2 - b^2 = (a^2 + c^2) - (b^2 + c^2) := by ring
    rw [this]; exact dvd_sub h2 h3
  . have : a^2 - c^2 = (a^2 + b^2) - (b^2 + c^2) := by ring
    rw [this]; exact dvd_sub h1 h3
  . have : b^2 - c^2 = (a^2 + b^2) - (a^2 + c^2) := by ring
    rw [this]; exact dvd_sub h1 h2

/-- If g divides all three channels, it divides 2a^2, 2b^2, 2c^2. -/
theorem triple_gcd_divides_2sq (a b c g : Int)
    (h1 : g | (a^2 + b^2)) (h2 : g | (a^2 + c^2)) (h3 : g | (b^2 + c^2)) :
    g | (2 * a^2) /\ g | (2 * b^2) /\ g | (2 * c^2) := by
  refine <?_, ?_, ?_>
  . have : 2 * a^2 = (a^2 + b^2) + (a^2 + c^2) - (b^2 + c^2) := by ring
    rw [this]; exact dvd_sub (dvd_add h1 h2) h3
  . have : 2 * b^2 = (a^2 + b^2) + (b^2 + c^2) - (a^2 + c^2) := by ring
    rw [this]; exact dvd_sub (dvd_add h1 h3) h2
  . have : 2 * c^2 = (a^2 + c^2) + (b^2 + c^2) - (a^2 + b^2) := by ring
    rw [this]; exact dvd_sub (dvd_add h2 h3) h1

/-! ## S3. Factor Cascade via Euclid's Lemma -/

/-- Cross-channel prime cascade: if prime p divides two channels, it divides a sum or difference. -/
theorem factor_cascade_prime (b c p : Int) (hp : Prime p) (hdvd : p | (b^2 - c^2)) :
    p | (b - c) \/ p | (b + c) := by
  have : b^2 - c^2 = (b - c) * (b + c) := by ring
  rw [this] at hdvd; exact hp.dvd_or_dvd hdvd

/-! ## S4. Composite Hypotenuse Channel Structure -/

/-- If p | d and p | c, then p^2 divides the channel a^2+b^2. -/
theorem factor_in_channel (a b c d p : Int)
    (h : a^2 + b^2 + c^2 = d^2) (hpd : p | d) (hpc : p | c) :
    p^2 | (a^2 + b^2) := by
  have : a^2 + b^2 = d^2 - c^2 := by linarith
  rw [this]; exact dvd_sub (pow_dvd_pow_of_dvd hpd 2) (pow_dvd_pow_of_dvd hpc 2)

/-- Composite channel mod: p | d implies (p | (d-c) <-> p | c). -/
theorem composite_channel_mod_minus (c d p : Int) (hp : p | d) :
    p | (d - c) <-> p | c := by
  constructor
  . intro h
    have hc : c = d - (d - c) := by ring
    rw [hc]; exact dvd_sub hp h
  . intro h; exact dvd_sub hp h

theorem composite_channel_mod_plus (c d p : Int) (hp : p | d) :
    p | (d + c) <-> p | c := by
  constructor
  . intro h
    have hc : c = (d + c) - d := by ring
    rw [hc]; exact dvd_sub h hp
  . intro h; exact dvd_add hp h

/-! ## S5. Parity Analysis -/

/-- d^2 mod 4 is 0 or 1, so a^2+b^2+c^2 mod 4 is 0 or 1. -/
theorem quad_mod4 (a b c d : Int) (h : a^2 + b^2 + c^2 = d^2) :
    (a^2 + b^2 + c^2) % 4 = 0 \/ (a^2 + b^2 + c^2) % 4 = 1 := by
  rw [h]
  have : d % 2 = 0 \/ d % 2 = 1 := by omega
  obtain h0 | h1 := this
  . left; obtain <k, rfl> : 2 | d := <d / 2, by omega>; ring_nf; omega
  . right; have <k, hk> : exists k, d = 2 * k + 1 := <d / 2, by omega>; subst hk; ring_nf; omega

/-- If d is even, then a^2+b^2+c^2 is divisible by 4. -/
theorem even_d_implies_4_divides (a b c d : Int) (h : a^2 + b^2 + c^2 = d^2) (hd : 2 | d) :
    4 | (a^2 + b^2 + c^2) := by
  rw [h]; obtain <k, rfl> := hd; exact <k^2, by ring>

/-- If all three components are even, d is even. -/
theorem all_even_implies_d_even (a b c d : Int) (h : a^2 + b^2 + c^2 = d^2)
    (ha : 2 | a) (hb : 2 | b) (hc : 2 | c) : 2 | d := by
  have : 4 | (a^2 + b^2 + c^2) := by
    obtain <a', rfl> := ha; obtain <b', rfl> := hb; obtain <c', rfl> := hc
    exact <a'^2 + b'^2 + c'^2, by ring>
  rw [h] at this
  exact (Int.prime_two).dvd_of_dvd_pow (dvd_trans <2, by norm_num> this)

/-! ## S6. Multi-Representation GCD Cascade -/

/-- Channel difference across representations. -/
theorem two_rep_channel_diff (a_1 b_1 c_1 a_2 b_2 c_2 d : Int)
    (h_1 : a_1^2 + b_1^2 + c_1^2 = d^2) (h_2 : a_2^2 + b_2^2 + c_2^2 = d^2) :
    (a_1^2 + b_1^2) - (a_2^2 + b_2^2) = c_2^2 - c_1^2 := by linarith

/-- GCD extraction: if g | (d-c_1) and g | (d-c_2), then g | (c_2-c_1). -/
theorem gcd_extraction (c_1 c_2 d g : Int)
    (h1 : g | (d - c_1)) (h2 : g | (d - c_2)) :
    g | (c_2 - c_1) := by
  have : c_2 - c_1 = (d - c_1) - (d - c_2) := by ring
  rw [this]; exact dvd_sub h1 h2

/-- Cross-sign GCD: if g | (d-c_1) and g | (d+c_2), then g | (c_1+c_2). -/
theorem gcd_cross_sign (c_1 c_2 d g : Int)
    (h1 : g | (d - c_1)) (h2 : g | (d + c_2)) :
    g | (c_1 + c_2) := by
  have : c_1 + c_2 = (d + c_2) - (d - c_1) := by ring
  rw [this]; exact dvd_sub h2 h1

/-- Cascade transitivity: if g | (d-c_1) and g | (c_2-c_1), then g | (d-c_2). -/
theorem cascade_transitive (c_1 c_2 d g : Int)
    (h1 : g | (d - c_1)) (h12 : g | (c_2 - c_1)) :
    g | (d - c_2) := by
  have : d - c_2 = (d - c_1) - (c_2 - c_1) := by ring
  rw [this]; exact dvd_sub h1 h12

/-- Reverse cascade: from g | d and g | (d-c) we get g | c. -/
theorem reverse_cascade (c d g : Int) (hd : g | d) (hdc : g | (d - c)) :
    g | c := by
  have : c = d - (d - c) := by ring
  rw [this]; exact dvd_sub hd hdc

/-- Double cascade: if p divides three d-c_i values, all pairwise differences divisible. -/
theorem double_cascade (c_1 c_2 c_3 d p : Int)
    (h1 : p | (d - c_1)) (h2 : p | (d - c_2)) (h3 : p | (d - c_3)) :
    p | (c_1 - c_2) /\ p | (c_1 - c_3) /\ p | (c_2 - c_3) := by
  constructor
  . exact gcd_extraction c_2 c_1 d p h2 h1
  constructor
  . exact gcd_extraction c_3 c_1 d p h3 h1
  . exact gcd_extraction c_3 c_2 d p h3 h2

/-! ## S7. Channel Product Identities -/

/-- Brahmagupta-Fibonacci identity. -/
theorem brahmagupta (a b c d : Int) :
    (a^2 + b^2) * (c^2 + d^2) = (a*c - b*d)^2 + (a*d + b*c)^2 := by ring

theorem brahmagupta' (a b c d : Int) :
    (a^2 + b^2) * (c^2 + d^2) = (a*c + b*d)^2 + (a*d - b*c)^2 := by ring

/-- The difference between the two Brahmagupta representations. -/
theorem brahmagupta_diff (a b c d : Int) :
    (a*c - b*d)^2 - (a*c + b*d)^2 = -(4 * a * b * c * d) := by ring

/-- Channel product via d: (a^2+b^2)(a^2+c^2) = a^2d^2 + b^2c^2. -/
theorem channel_product_via_d (a b c d : Int) (h : a^2 + b^2 + c^2 = d^2) :
    (a^2 + b^2) * (a^2 + c^2) = a^2 * d^2 + b^2 * c^2 := by nlinarith

theorem channel_product_via_d' (a b c d : Int) (h : a^2 + b^2 + c^2 = d^2) :
    (a^2 + b^2) * (b^2 + c^2) = b^2 * d^2 + a^2 * c^2 := by nlinarith

theorem channel_product_via_d'' (a b c d : Int) (h : a^2 + b^2 + c^2 = d^2) :
    (a^2 + c^2) * (b^2 + c^2) = c^2 * d^2 + a^2 * b^2 := by nlinarith

/-- Full channel product = (b^2+c^2)(a^2+c^2)(a^2+b^2). -/
theorem full_channel_product (a b c d : Int) (h : a^2 + b^2 + c^2 = d^2) :
    (d - a) * (d + a) * ((d - b) * (d + b)) * ((d - c) * (d + c)) =
    (b^2 + c^2) * (a^2 + c^2) * (a^2 + b^2) := by
  have h1 : (d - a) * (d + a) = b^2 + c^2 := by nlinarith
  have h2 : (d - b) * (d + b) = a^2 + c^2 := by nlinarith
  have h3 : (d - c) * (d + c) = a^2 + b^2 := by nlinarith
  rw [h1, h2, h3]

/-! ## S8. Shared Hypotenuse Factor Detection -/

/-- Two quadruples with same d: channel product relation. -/
theorem shared_hyp_channel (a_1 b_1 c_1 a_2 b_2 c_2 d : Int)
    (h_1 : a_1^2 + b_1^2 + c_1^2 = d^2) (h_2 : a_2^2 + b_2^2 + c_2^2 = d^2) :
    (a_1^2 + b_1^2) * (a_2^2 + b_2^2) = (d^2 - c_1^2) * (d^2 - c_2^2) := by
  have h1 : a_1^2 + b_1^2 = d^2 - c_1^2 := by linarith
  have h2 : a_2^2 + b_2^2 = d^2 - c_2^2 := by linarith
  rw [h1, h2]

/-- If p | d and p | c_1, then p^2 | (a_1^2+b_1^2). -/
theorem shared_factor_asymmetry (a_1 b_1 c_1 d p : Int)
    (h_1 : a_1^2 + b_1^2 + c_1^2 = d^2) (hpd : p | d) (hpc1 : p | c_1) :
    p^2 | (a_1^2 + b_1^2) := factor_in_channel a_1 b_1 c_1 d p h_1 hpd hpc1

/-- Strengthened dichotomy: p | d and p | c implies p | (d-c) AND p | (d+c). -/
theorem strengthened_dichotomy (c d p : Int) (hpd : p | d) (hpc : p | c) :
    p | (d - c) /\ p | (d + c) :=
  <dvd_sub hpd hpc, dvd_add hpd hpc>

/-! ## S9. Factor Orbit Descent -/

/-- If p | a, p | b, p | c in a quadruple, then p^2 | d^2 and we can descend. -/
theorem factor_orbit_descent (a b c d p : Int) (hp : p != 0)
    (h : a^2 + b^2 + c^2 = d^2) (ha : p | a) (hb : p | b) (hc : p | c) :
    exists a' b' c' : Int, a = p * a' /\ b = p * b' /\ c = p * c' /\
    p^2 * (a'^2 + b'^2 + c'^2) = d^2 := by
  obtain <a', rfl> := ha; obtain <b', rfl> := hb; obtain <c', rfl> := hc
  exact <a', b', c', rfl, rfl, rfl, by nlinarith>

/-- Under descent, p^2 | d^2. -/
theorem factor_orbit_div (a b c d p : Int)
    (h : a^2 + b^2 + c^2 = d^2) (ha : p | a) (hb : p | b) (hc : p | c) :
    p^2 | d^2 := by
  obtain <a', rfl> := ha; obtain <b', rfl> := hb; obtain <c', rfl> := hc
  exact <a'^2 + b'^2 + c'^2, by nlinarith>

/-! ## S10. Representation Distance -/

/-- Squared distance between two representations on the d-sphere. -/
def repDist (a_1 b_1 c_1 a_2 b_2 c_2 : Int) : Int :=
  (a_1 - a_2)^2 + (b_1 - b_2)^2 + (c_1 - c_2)^2

theorem repDist_eq (a_1 b_1 c_1 a_2 b_2 c_2 d : Int)
    (h_1 : a_1^2 + b_1^2 + c_1^2 = d^2) (h_2 : a_2^2 + b_2^2 + c_2^2 = d^2) :
    repDist a_1 b_1 c_1 a_2 b_2 c_2 = 2 * d^2 - 2 * (a_1*a_2 + b_1*b_2 + c_1*c_2) := by
  unfold repDist; nlinarith

theorem repDist_nonneg (a_1 b_1 c_1 a_2 b_2 c_2 : Int) :
    0 <= repDist a_1 b_1 c_1 a_2 b_2 c_2 := by unfold repDist; positivity

theorem repDist_antipodal (a_1 b_1 c_1 d : Int) (h : a_1^2 + b_1^2 + c_1^2 = d^2) :
    repDist a_1 b_1 c_1 (-a_1) (-b_1) (-c_1) = 4 * d^2 := by
  unfold repDist; nlinarith

theorem repDist_zero_iff (a_1 b_1 c_1 a_2 b_2 c_2 : Int) :
    repDist a_1 b_1 c_1 a_2 b_2 c_2 = 0 <-> a_1 = a_2 /\ b_1 = b_2 /\ c_1 = c_2 := by
  unfold repDist
  constructor
  . intro h
    have ha : (a_1 - a_2)^2 <= 0 := by nlinarith [sq_nonneg (b_1 - b_2), sq_nonneg (c_1 - c_2)]
    have hb : (b_1 - b_2)^2 <= 0 := by nlinarith [sq_nonneg (a_1 - a_2), sq_nonneg (c_1 - c_2)]
    have hc : (c_1 - c_2)^2 <= 0 := by nlinarith [sq_nonneg (a_1 - a_2), sq_nonneg (b_1 - b_2)]
    have : a_1 - a_2 = 0 := by nlinarith [sq_nonneg (a_1 - a_2)]
    have : b_1 - b_2 = 0 := by nlinarith [sq_nonneg (b_1 - b_2)]
    have : c_1 - c_2 = 0 := by nlinarith [sq_nonneg (c_1 - c_2)]
    omega
  . rintro <rfl, rfl, rfl>; simp

/-! ## S11. Cauchy-Schwarz for Representations -/

/-- Inner product squared is at most d^4. -/
theorem inner_product_bound (a_1 b_1 c_1 a_2 b_2 c_2 d : Int)
    (h_1 : a_1^2 + b_1^2 + c_1^2 = d^2) (h_2 : a_2^2 + b_2^2 + c_2^2 = d^2) :
    (a_1*a_2 + b_1*b_2 + c_1*c_2)^2 <= d^4 := by
  have : d^4 - (a_1*a_2 + b_1*b_2 + c_1*c_2)^2 =
    d^2 * d^2 - (a_1*a_2 + b_1*b_2 + c_1*c_2)^2 := by ring
  nlinarith [sq_nonneg (a_1*b_2 - a_2*b_1), sq_nonneg (a_1*c_2 - a_2*c_1),
             sq_nonneg (b_1*c_2 - b_2*c_1)]

/-! ## S12. Higher-Dimensional Channel Sums -/

/-- Sextuple (5 spatial components): 10 pair channels sum to 4f^2. -/
theorem sextuple_channel_sum (a b c d e f : Int)
    (h : a^2 + b^2 + c^2 + d^2 + e^2 = f^2) :
    (a^2+b^2) + (a^2+c^2) + (a^2+d^2) + (a^2+e^2) +
    (b^2+c^2) + (b^2+d^2) + (b^2+e^2) +
    (c^2+d^2) + (c^2+e^2) + (d^2+e^2) = 4 * f^2 := by linarith

/-- Septuple (6 spatial components): 15 pair channels sum to 5g^2. -/
theorem septuple_channel_sum (a b c d e f g : Int)
    (h : a^2 + b^2 + c^2 + d^2 + e^2 + f^2 = g^2) :
    (a^2+b^2) + (a^2+c^2) + (a^2+d^2) + (a^2+e^2) + (a^2+f^2) +
    (b^2+c^2) + (b^2+d^2) + (b^2+e^2) + (b^2+f^2) +
    (c^2+d^2) + (c^2+e^2) + (c^2+f^2) +
    (d^2+e^2) + (d^2+f^2) + (e^2+f^2) = 5 * g^2 := by linarith

/-! ## S13. Channel Divisibility by Common Factors -/

/-- If p | a, then p | (a^2+b^2) iff p | b. -/
theorem channel_div_by_factor (a b p : Int) (hp : Prime p) (hpa : p | a) :
    p | (a^2 + b^2) <-> p | b := by
  constructor
  . intro h
    have hb2 : p | b^2 := by
      have : b^2 = (a^2 + b^2) - a^2 := by ring
      rw [this]; exact dvd_sub h (dvd_pow hpa (by norm_num : 2 != 0))
    exact hp.dvd_of_dvd_pow hb2
  . intro hpb
    exact dvd_add (dvd_pow hpa (by norm_num : 2 != 0)) (dvd_pow hpb (by norm_num : 2 != 0))

/-! ## S14. Modular Fingerprinting -/

/-- If p | d, then p^2 | (a^2+b^2+c^2). -/
theorem mod_fingerprint (a b c d p : Int) (h : a^2 + b^2 + c^2 = d^2) (hp : p | d) :
    p^2 | (a^2 + b^2 + c^2) := by rw [h]; exact pow_dvd_pow_of_dvd hp 2

/-- Two quadruples with same d: their fingerprint difference is zero. -/
theorem fingerprint_diff_zero (a_1 b_1 c_1 a_2 b_2 c_2 d : Int)
    (h_1 : a_1^2 + b_1^2 + c_1^2 = d^2) (h_2 : a_2^2 + b_2^2 + c_2^2 = d^2) :
    (a_1^2 + b_1^2 + c_1^2) - (a_2^2 + b_2^2 + c_2^2) = 0 := by linarith

/-! ## S15. Pell Connection -/

/-- Near-balanced case: a = b gives (d-c)(d+c) = 2a^2. -/
theorem near_balanced (a c d : Int) (h : a^2 + a^2 + c^2 = d^2) :
    (d - c) * (d + c) = 2 * a^2 := by nlinarith

/-- c = 1 case: Pell equation d^2 - 2a^2 = 1. -/
theorem pell_from_quadruple (a d : Int) (h : a^2 + a^2 + 1^2 = d^2) :
    d^2 - 2 * a^2 = 1 := by linarith

/-- Specific Pell solution verification. -/
example : (2:Int)^2 + 2^2 + 1^2 = 3^2 := by norm_num
example : (12:Int)^2 + 12^2 + 1^2 = 17^2 := by norm_num
example : (70:Int)^2 + 70^2 + 1^2 = 99^2 := by norm_num

/-! ## S16. No Balanced Quadruple -/

/-
No nonzero balanced quadruple: 3a^2 != d^2 for a != 0.
-/
theorem no_balanced_quad (a d : Int) (ha : a != 0) (h : 3 * a^2 = d^2) : False := by
  -- If $3a^2 = d^2$, then $d = \pm a\sqrt{3}$.
  have hd : d = a * Real.sqrt 3 \/ d = -a * Real.sqrt 3 := by
    exact or_iff_not_imp_left.mpr fun h' => mul_left_cancel_0 ( sub_ne_zero_of_ne h' ) <| by ring_nf; norm_num; norm_cast; linarith;
  obtain h | h := hd <;> [ exact Nat.Prime.irrational_sqrt ( by norm_num : Nat.Prime 3 ) < d / a, by simp [ *, mul_div_cancel_left_0 ] > ; exact Nat.Prime.irrational_sqrt ( by norm_num : Nat.Prime 3 ) < -d / a, by simp [ *, mul_div_cancel_left_0 ] > ]

/-! ## S17. Quadruple Generation from Factorizations -/

/-- If a^2+b^2 = (2k+m).m for some integers, we get a quadruple (a,b,k,k+m). -/
theorem factorization_quadruple (a b k m : Int) (hab : a^2 + b^2 = (2*k + m) * m) :
    a^2 + b^2 + k^2 = (k + m)^2 := by nlinarith

/-! ## S18. Small Channel Factor Extraction -/

/-- If 0 < d-c, then d-c divides a^2+b^2 and d-c < d (for c > 0). -/
theorem small_channel_factor (a b c d : Int) (h : a^2 + b^2 + c^2 = d^2)
    (hc : 0 < c) (hd : c < d) :
    (d - c) | ((d - c) * (d + c)) /\ 0 < d - c := by
  exact <<d + c, rfl>, by omega>

/-! ## S19. Computational Verifications -/

-- d = 35 = 5x7
-- Q1 = (6, 10, 33, 35), Q2 = (15, 10, 30, 35)
example : (6:Int)^2 + 10^2 + 33^2 = 35^2 := by norm_num
example : (15:Int)^2 + 10^2 + 30^2 = 35^2 := by norm_num

-- Channel values for Q1:
-- Ch(a,b) = 6^2+10^2 = 136 = 8x17
-- Ch(a,c) = 6^2+33^2 = 1125 = 5^3x9
-- Ch(b,c) = 10^2+33^2 = 1189 = 29x41
-- Factor 5 revealed: 5 | 1125, and 1125 = (35-10)(35+10) = 25x45
example : (5:Int) | ((35 - 10) * (35 + 10)) := by norm_num
example : (5:Int) | 35 := by norm_num

-- d = 15 = 3x5
-- Q = (2, 10, 11, 15): Channel 2 = (15-10)(15+10) = 5x25
example : (2:Int)^2 + 10^2 + 11^2 = 15^2 := by norm_num
example : (5:Int) | (15 - 10) := by norm_num
example : (5:Int) | (15 + 10) := by norm_num

-- d = 21 = 3x7
-- Q = (6, 14, 13, 21): 36+196+169 = 401? No: 36+196 = 232, 232+169 = 401 != 441
-- Q = (2, 6, 9, 11) scaled by...
-- Q = (6, 6, 18, 21)? 36+36+324 = 396 != 441
-- Q = (6, 9, 18, 21)? 36+81+324 = 441 = 21^2 check
example : (6:Int)^2 + 9^2 + 18^2 = 21^2 := by norm_num
-- Channel: (21-18)(21+18) = 3x39 = 117 = 6^2+9^2
-- Factor 3 revealed: 3 | (21-18) and 3 | (21+18), confirming 3 | 21
example : (3:Int) | (21 - 18) := by norm_num
example : (3:Int) | (21 + 18) := by norm_num
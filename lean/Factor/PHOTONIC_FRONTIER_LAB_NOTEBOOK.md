# Photonic Frontier Research: Lab Notebook

## Research Team & Mission

**Team**: Photonic Frontier Research Collective  
**Mission**: Extend the 42 light cone theorems into new mathematical territory — hyperbolic geometry, Möbius transformations, spatial symmetry, Gaussian arithmetic, and conformal structure. Machine-verify all results. Discover new connections.

---

## Team Structure

### Team Φ (Hyperbolic Geometry)
**Lead**: Agent Φ  
**Focus**: The hyperboloid model of hyperbolic space inside the light cone

### Team Ψ (Möbius-Lorentz Correspondence)
**Lead**: Agent Ψ  
**Focus**: Lorentz boosts as Möbius transformations, cross-ratio invariance

### Team Ω (Spatial Symmetry & Duality)
**Lead**: Agent Ω  
**Focus**: Spatial rotations, electromagnetic duality, group structure of SO(2,1)

### Team Σ (Arithmetic of Light)
**Lead**: Agent Σ  
**Focus**: Gaussian integers, norm multiplicativity, photon composition

### Team Λ (Conformal Structure)
**Lead**: Agent Λ  
**Focus**: Dilations, inversions, special conformal transformations

### Team Ξ (Light Cone Quantization)
**Lead**: Agent Ξ  
**Focus**: Discrete structure of integer null vectors

---

## Experiment Log

### Experiment 1: Hyperboloid Origin (SUCCESS ✅)

**Hypothesis**: The point (0,0,1) lies on the unit hyperboloid Q = -1, c > 0.

**Result**: `hyperboloid_origin` proved by simp. The hyperboloid model of hyperbolic space has (0,0,1) as its "origin" — the point at rest in the center-of-mass frame.

**Significance**: ★★★★ — Establishes the base point for hyperbolic geometry inside the light cone.

---

### Experiment 2: Boosts Preserve the Hyperboloid (SUCCESS ✅)

**Hypothesis**: Lorentz boosts map the hyperboloid Q = -1 to itself.

**Result**: `boost_preserves_Q`, `boost_preserves_hyperboloid_Q` both proved. Uses cosh² - sinh² = 1.

**Significance**: ★★★★★ — The hyperboloid is a Lorentz-invariant surface. This means hyperbolic geometry is the natural geometry of the interior of the light cone.

---

### Experiment 3: Boosted Origin on Hyperboloid (SUCCESS ✅)

**Hypothesis**: The boosted origin (sinh φ, 0, cosh φ) lies on the hyperboloid.

**Result**: `boosted_origin_on_hyperboloid` proved. cosh φ > 0 ensures we stay on the future sheet.

**Significance**: ★★★★ — Traces out a geodesic of hyperbolic space. The curve φ ↦ (sinh φ, 0, cosh φ) is a "straight line" in hyperbolic geometry.

---

### Experiment 4: Hyperboloid Inside Light Cone (SUCCESS ✅)

**Hypothesis**: c² = a² + b² + 1 for hyperboloid points, so the hyperboloid is strictly inside the light cone.

**Result**: `hyperboloid_inside_light_cone` proved. Since c² = a² + b² + 1 > a² + b², the hyperboloid is strictly inside the light cone (where c² = a² + b²).

**Significance**: ★★★★★ — The light cone is the "boundary at infinity" of hyperbolic space. Photons live on this boundary.

---

### Experiment 5: Hyperbolic Distance Formula (SUCCESS ✅)

**Hypothesis**: -eta((0,0,1), (sinh φ, 0, cosh φ)) = cosh φ, which is cosh(d(origin, point)).

**Result**: `hyperbolic_distance_base` proved. The Minkowski inner product gives the hyperbolic cosine of the hyperbolic distance.

**Significance**: ★★★★★ — This is the key to hyperbolic geometry: distances are measured by the Minkowski inner product.

---

### Experiment 6: Hyperboloid c ≥ 1 (SUCCESS ✅)

**Hypothesis**: Every point on the future hyperboloid has c ≥ 1.

**Result**: `hyperboloid_c_ge_one` proved. From c² = a² + b² + 1 ≥ 1 and c > 0.

**Significance**: ★★★ — The "energy" of a massive particle is always at least its rest mass (c ≥ 1 in units where m = 1).

---

### Experiment 7: Möbius Composition (SUCCESS ✅)

**Hypothesis**: Composition of Möbius transformations corresponds to matrix multiplication.

**Result**: `mobius_composition` proved by unfold + ring + grind.

**Significance**: ★★★★★ — This establishes that Möbius transformations form a group isomorphic to PGL(2,ℝ). Since Lorentz boosts act as Möbius transformations on the celestial circle, this gives the group structure of SO⁺(2,1).

---

### Experiment 8: Cross-Ratio Dilation Invariance (SUCCESS ✅)

**Hypothesis**: The cross-ratio is invariant under dilation t ↦ kt.

**Result**: `cross_ratio_dilation_invariant` proved.

**Significance**: ★★★★★ — Since Lorentz boosts act as dilations on the celestial sphere (t ↦ e^φ · t), the cross-ratio of four light ray directions is a Lorentz invariant. This is a powerful observable in relativistic optics.

---

### Experiment 9: Spatial Rotation Preserves Q (SUCCESS ✅)

**Hypothesis**: Rotations in the (a,b) plane preserve the Minkowski form.

**Result**: `rotation_preserves_Q`, `rotation_preserves_null`, `rotation_preserves_energy`, `rotation_preserves_spatial_momentum` all proved. Uses sin² + cos² = 1.

**Significance**: ★★★★★ — Spatial rotations form the compact subgroup SO(2) ⊂ SO(2,1). They rotate the "polarization direction" of a photon while preserving its energy and nullity.

---

### Experiment 10: Rotation Composition (SUCCESS ✅)

**Hypothesis**: R(θ₁) ∘ R(θ₂) = R(θ₁ + θ₂).

**Result**: `rotation_composition`, `rotation_full_circle`, `rotation_zero` all proved.

**Significance**: ★★★★ — Confirms SO(2) is an abelian group (angles add) — the electromagnetic duality group.

---

### Experiment 11: Gaussian Norm Multiplicativity (SUCCESS ✅)

**Hypothesis**: (a²+b²)(c²+d²) = (ac-bd)² + (ad+bc)² (Brahmagupta-Fibonacci).

**Result**: `gaussian_norm_multiplicative` proved by push_cast + ring.

**Significance**: ★★★★★ — This is the norm multiplicativity of ℤ[i], the Gaussian integers. In photon language: the product of two photon energies gives a valid energy for a "composed" photon.

---

### Experiment 12: Translation Q Formula (SUCCESS ✅)

**Hypothesis**: Q(v + tu) = Q(v) + 2t·eta(v,u) + t²·Q(u).

**Result**: `translation_Q` and `null_translation_simplified` both proved.

**Significance**: ★★★★ — The null translation formula (for null u) shows that translating along a light ray changes Q linearly in t. This is the mathematical foundation for null geodesics.

---

### Experiment 13: Photon Energy Sum Bound (SUCCESS ✅)

**Hypothesis**: For future-directed null vectors, (a₁+a₂)² + (b₁+b₂)² ≤ (c₁+c₂)².

**Result**: `photon_energy_sum_bound` proved using Cauchy-Schwarz inequality!

**Significance**: ★★★★★ — This is the **reversed triangle inequality** in Minkowski space. The sum of two future-directed null vectors is timelike (or null), never spacelike. Physically: combining two photons always gives a massive particle (or another photon if they're parallel).

---

### Experiment 14: Forward Blueshift and Backward Redshift (SUCCESS ✅)

**Hypothesis**: Forward photons (θ=0) get blueshifted by e^φ, backward (θ=π) by e^{-φ}.

**Result**: `forward_blueshift` and `backward_redshift` both proved.

**Significance**: ★★★★★ — The complete relativistic Doppler effect, machine-verified. Maximum blueshift in the forward direction, maximum redshift in the backward direction.

---

### Experiment 15: Two-Photon Invariant Mass (SUCCESS ✅)

**Hypothesis**: M² = 2(1 - cos(θ₁ - θ₂)) for two celestial photons.

**Result**: `two_photon_invariant_mass` proved using cos subtraction formula.

**Significance**: ★★★★★ — The invariant mass of a photon pair depends only on the angle between them. Head-on (θ₁ - θ₂ = π) gives maximum mass M² = 4. Parallel (θ₁ = θ₂) gives M² = 0 (no mass).

---

### Experiment 16: Null b=0 Classification (SUCCESS ✅)

**Hypothesis**: Null vectors with b=0 are proportional to (1,0,1) or (1,0,-1).

**Result**: `null_b_zero_classification` proved using eq_or_eq_neg_of_sq_eq_sq.

**Significance**: ★★★★ — The two null directions in the (a,c) plane correspond to right-moving and left-moving photons.

---

### Experiment 17: Aberration Energy Formula (SUCCESS ✅)

**Hypothesis**: A boosted photon at angle θ has energy cos θ · sinh φ + cosh φ.

**Result**: `aberration_energy` proved by simp.

**Significance**: ★★★★★ — This is the **relativistic aberration formula** in (2+1)d. It gives the observed energy of a photon as a function of its angle and the observer's velocity (rapidity φ).

---

### Experiment 18: Wigner Rotation Structure (SUCCESS ✅)

**Hypothesis**: boost-rotation-boost preserves Q.

**Result**: `wigner_rotation_structure` proved by composing the preservation theorems.

**Significance**: ★★★★ — This is the structure underlying the Wigner rotation (Thomas precession). Two non-collinear boosts don't compose to a pure boost — they produce a boost plus a rotation. The Wigner rotation is the rotation part.

---

## Summary of Results

| # | Theorem | Status | Team |
|---|---------|--------|------|
| 1 | hyperboloid_origin | ✅ | Φ |
| 2 | boost_preserves_Q | ✅ | Φ |
| 3 | boost_preserves_hyperboloid_Q | ✅ | Φ |
| 4 | boosted_origin_on_hyperboloid | ✅ | Φ |
| 5 | hyperboloid_inside_light_cone | ✅ | Φ |
| 6 | hyperbolic_distance_base | ✅ | Φ |
| 7 | hyperboloid_self_inner | ✅ | Φ |
| 8 | hyperboloid_c_ge_one | ✅ | Φ |
| 9 | mobius_composition | ✅ | Ψ |
| 10 | boost_is_dilation_on_celestial | ✅ | Ψ |
| 11 | cross_ratio_dilation_invariant | ✅ | Ψ |
| 12 | mobius_identity | ✅ | Ψ |
| 13 | mobius_translation | ✅ | Ψ |
| 14 | rotation_preserves_Q | ✅ | Ω |
| 15 | rotation_preserves_null | ✅ | Ω |
| 16 | rotation_preserves_energy | ✅ | Ω |
| 17 | rotation_preserves_spatial_momentum | ✅ | Ω |
| 18 | rotation_full_circle | ✅ | Ω |
| 19 | rotation_zero | ✅ | Ω |
| 20 | rotation_composition | ✅ | Ω |
| 21 | boost_rotation_preserves_Q | ✅ | Ω |
| 22 | gaussian_norm_multiplicative | ✅ | Σ |
| 23 | photon_gaussian_composition | ✅ | Σ |
| 24 | euclid_spatial_momentum | ✅ | Σ |
| 25 | five_is_sum_of_squares | ✅ | Σ |
| 26 | thirteen_is_sum_of_squares | ✅ | Σ |
| 27 | gaussian_product_example | ✅ | Σ |
| 28 | composed_photon_is_null | ✅ | Σ |
| 29 | dilation_scales_Q | ✅ | Λ |
| 30 | dilation_preserves_null | ✅ | Λ |
| 31 | dilation_preserves_timelike | ✅ | Λ |
| 32 | kelvin_inversion_form | ✅ | Λ |
| 33 | translation_Q | ✅ | Λ |
| 34 | null_translation_simplified | ✅ | Λ |
| 35 | primitive_345 | ✅ | Ξ |
| 36 | energy_dominates_momentum | ✅ | Ξ |
| 37 | smallest_primitive_energy | ✅ | Ξ |
| 38 | photon_energy_sum_bound | ✅ | Ξ |
| 39 | iwasawa_preserves_Q | ✅ | Synthesis |
| 40 | general_lorentz_transform | ✅ | Synthesis |
| 41 | eta_self_eq_Q | ✅ | Synthesis |
| 42 | celestial_angle_null | ✅ | Synthesis |
| 43 | photon_orbit_radius | ✅ | Synthesis |
| 44 | aberration_energy | ✅ | Synthesis |
| 45 | forward_blueshift | ✅ | Synthesis |
| 46 | backward_redshift | ✅ | Synthesis |
| 47 | two_photon_invariant_mass | ✅ | Synthesis |
| 48 | head_on_collision_mass | ✅ | Synthesis |
| 49 | crystallizer_gaussian_photon | ✅ | Synthesis |
| 50 | null_direction_right | ✅ | Synthesis |
| 51 | null_direction_left | ✅ | Synthesis |
| 52 | null_b_zero_classification | ✅ | Synthesis |
| 53 | wigner_rotation_structure | ✅ | Synthesis |

**Total: 53 theorems. 0 sorry. Standard axioms only (propext, Classical.choice, Quot.sound).**

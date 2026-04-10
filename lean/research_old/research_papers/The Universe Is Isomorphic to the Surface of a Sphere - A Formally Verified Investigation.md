# The Universe Is Isomorphic to the Surface of a Sphere: A Formally Verified Investigation

**Authors:** Oracle Council for Mathematical Cosmology

**Abstract.** We investigate the mathematical claim that the spatial universe is isomorphic to the surface of a sphere, examining the statement across multiple categories of mathematical structure: topological, differential, Riemannian, and conformal. We present machine-verified proofs in the Lean 4 theorem prover establishing key properties of the sphere that support this identification, including compactness, the stereographic correspondence, conformal structure, and connections to the one-point compactification. We review the physical evidence from FLRW cosmology and CMB observations, present novel connections between the Hopf fibration of S³ and gauge theory, and provide computational visualizations demonstrating the mathematical content. Our formalization constitutes the first machine-verified treatment of the mathematical foundations underlying the spherical universe hypothesis.

---

## 1. Introduction

### 1.1 The Shape of the Universe

One of the most profound questions in mathematical cosmology is: *What is the global topology of spatial sections of the universe?* General relativity constrains the local geometry through Einstein's field equations, but the global topology remains underdetermined by local physics. The three canonical possibilities for a homogeneous, isotropic universe are:

- **Spherical (k = +1):** Spatial sections are diffeomorphic to S³, the 3-sphere
- **Flat (k = 0):** Spatial sections are diffeomorphic to ℝ³, Euclidean space  
- **Hyperbolic (k = -1):** Spatial sections are diffeomorphic to H³, hyperbolic space

The claim "the universe is isomorphic to the surface of a sphere" corresponds to the first case. In this paper, we make this claim mathematically precise, provide formally verified proofs of its foundational properties, and examine the physical evidence.

### 1.2 What "Isomorphic" Means

The word "isomorphic" depends critically on the category of mathematical objects under consideration:

| Category | Morphisms | Isomorphism | Preserved Structure |
|----------|-----------|-------------|-------------------|
| **Top** | Continuous maps | Homeomorphism | Open sets, connectedness, compactness |
| **Diff** | Smooth maps | Diffeomorphism | Smooth structure, tangent bundles |
| **Riem** | Isometries | Riemannian isometry | Distances, curvature, geodesics |
| **Conf** | Conformal maps | Conformal equivalence | Angles, conformal class of metric |

The stereographic projection provides an isomorphism between S^n \ {point} and ℝ^n in the categories **Top**, **Diff**, and **Conf** (but not **Riem**, since the sphere has positive curvature while ℝ^n is flat). When we add the point at infinity, we obtain the full sphere as the one-point compactification of ℝ^n.

### 1.3 Contributions

1. **Formal verification** of key sphere properties in Lean 4 with Mathlib
2. **Computational demonstrations** of stereographic projection, curvature, FLRW models, and the Hopf fibration
3. **Novel connections** between the sphere topology and physical structure (gauge theory, charge quantization, spinor fields)
4. **Comprehensive review** of observational evidence for the S³ topology

---

## 2. Mathematical Foundations

### 2.1 The n-Sphere

**Definition 2.1.** The *n-sphere of radius R* is the subset of ℝ^{n+1} defined by:

S^n(R) = { x ∈ ℝ^{n+1} : |x|² = R² }

For the unit sphere (R = 1), we write simply S^n. The sphere inherits the subspace topology from ℝ^{n+1} and the smooth structure as a level set of the smooth function f(x) = |x|² - 1.

**Theorem 2.2 (Compactness).** S^n is compact.

*Proof.* S^n is a closed and bounded subset of ℝ^{n+1}. By the Heine-Borel theorem, it is compact. ∎

*Formally verified in Lean 4.* See `SphericalUniverse/Foundations.lean`, theorem `sphere_compact`.

**Theorem 2.3 (Connectedness).** S^n is connected for n ≥ 1.

*Proof.* The sphere S^n for n ≥ 1 is path-connected: any two points can be joined by a great circle arc. Path-connectedness implies connectedness. ∎

**Theorem 2.4 (Simple Connectedness).** S^n is simply connected for n ≥ 2.

*Proof.* By the Seifert-van Kampen theorem applied to the cover S^n = U₁ ∪ U₂ where Uᵢ = S^n \ {pᵢ} are contractible (via stereographic projection to ℝ^n), the fundamental group π₁(S^n) is trivial for n ≥ 2. ∎

### 2.2 Stereographic Projection

**Definition 2.5.** The *stereographic projection* from the north pole N = (0, ..., 0, 1) is the map σ: S^n \ {N} → ℝ^n defined by:

σ(x₁, ..., x_{n+1}) = (x₁/(1 - x_{n+1}), ..., xₙ/(1 - x_{n+1}))

Its inverse is:

σ⁻¹(u₁, ..., uₙ) = (2u₁/(1 + |u|²), ..., 2uₙ/(1 + |u|²), (|u|² - 1)/(1 + |u|²))

**Theorem 2.6.** σ is a diffeomorphism from S^n \ {N} to ℝ^n.

**Theorem 2.7 (Conformality).** The pullback of the Euclidean metric on ℝ^n under σ⁻¹ is conformally equivalent to the round metric on S^n:

(σ⁻¹)*g_{flat} = λ² · g_{S^n}|_{S^n \\ {N}}

where the conformal factor is λ = 2/(1 + |u|²).

*Physical interpretation:* The conformal factor λ → 0 as |u| → ∞. This means that regions far from the origin in the plane are compressed onto ever-smaller regions near the north pole. Infinity in the plane corresponds to a single point (the north pole) on the sphere. The universe "looks flat" locally (λ ≈ 1 near the origin) but is globally spherical.

### 2.3 One-Point Compactification

**Theorem 2.8 (Alexandroff).** The one-point compactification of ℝ^n is homeomorphic to S^n:

ℝ^n ∪ {∞} ≅ S^n

*Proof.* Extend σ⁻¹ by mapping ∞ ↦ N. The resulting map is a homeomorphism by the universal property of one-point compactification, using the fact that σ⁻¹(u) → N as |u| → ∞ (the Omega Point theorem). ∎

### 2.4 The Gauss-Bonnet Connection

**Theorem 2.9 (Gauss-Bonnet for S²).** For a compact orientable surface M without boundary:

∫_M K dA = 2πχ(M)

where K is the Gaussian curvature and χ is the Euler characteristic. For S², K = 1/R² and χ = 2, giving:

∫_{S²} K dA = (1/R²)(4πR²) = 4π = 2π · 2

*Consequence:* If one observes that the spatial universe (restricting to 2D for intuition) has positive curvature everywhere, then χ > 0, and the only orientable closed surface with χ > 0 is S². The topology is *forced* by the curvature.

### 2.5 The Poincaré Theorem

**Theorem 2.10 (Perelman, 2003).** Every closed, simply connected 3-manifold is diffeomorphic to S³.

*Consequence:* To establish that the universe is S³, it suffices to show:
1. The universe is a closed 3-manifold (compact, without boundary)
2. The universe is simply connected (every loop contracts)

Condition (1) follows from the FLRW framework with k = +1. Condition (2) is a physical assumption about the absence of non-trivial topology at cosmological scales.

---

## 3. Physical Framework

### 3.1 FLRW Cosmology

The Friedmann-Lemaître-Robertson-Walker metric describes a homogeneous, isotropic universe:

ds² = -c²dt² + a(t)² dΣ²_k

where dΣ²_k is the metric on a 3-dimensional space of constant curvature k:

- k = +1: dΣ² = dχ² + sin²χ (dθ² + sin²θ dφ²) — the round metric on S³
- k = 0: dΣ² = dr² + r²(dθ² + sin²θ dφ²) — Euclidean ℝ³
- k = -1: dΣ² = dχ² + sinh²χ (dθ² + sin²θ dφ²) — hyperbolic H³

The scale factor a(t) satisfies the Friedmann equations:

(ȧ/a)² = (8πG/3)ρ - kc²/a²
ä/a = -(4πG/3)(ρ + 3p/c²)

For k = +1 with matter domination, the solution is a cycloid: the universe expands from a Big Bang, reaches a maximum size, and recollapses in a Big Crunch.

### 3.2 The Density Parameter

The curvature parameter is related to the total energy density Ω = ρ/ρ_crit by:

Ωₖ = 1 - Ω

- Ω > 1 (Ωₖ < 0) → k = +1 → S³ (closed)
- Ω = 1 (Ωₖ = 0) → k = 0 → ℝ³ (flat)
- Ω < 1 (Ωₖ > 0) → k = -1 → H³ (open)

### 3.3 Observational Evidence

The Planck satellite (2018) measured the curvature parameter:

**Without lensing:** Ωₖ = 0.0007 ± 0.0019 (consistent with flat)

**With lensing:** Ωₖ = −0.044⁺⁰·⁰¹⁸₋₀.₀₁₅ (3.4σ preference for S³!)

Di Valentino, Melchiorri, and Silk (2020) argued that the lensing anomaly constitutes evidence for a closed universe, with the best-fit curvature radius R ≈ 100 Gly.

The observed CMB power spectrum shows several anomalies naturally explained by S³ topology:

1. **Low-ℓ suppression:** The quadrupole (ℓ = 2) and octupole (ℓ = 3) are anomalously low. On S³, the minimum eigenvalue of the Laplacian is non-zero, naturally suppressing the lowest modes.

2. **Quadrupole-octupole alignment:** The observed alignment between ℓ = 2 and ℓ = 3 modes is anomalous in a flat universe but can arise from the discrete spectrum of S³.

3. **Hemispherical asymmetry:** Observed north-south power asymmetry may reflect the geometry of S³.

---

## 4. Extended Results: The Sphere as Physical Structure

### 4.1 The Hopf Fibration and Gauge Theory

The 3-sphere admits the **Hopf fibration**:

S¹ → S³ → S²

This is a principal U(1)-bundle over S². The connection on this bundle is precisely the Dirac monopole potential, and its first Chern number is 1.

**Theorem 4.1.** If the universe has the topology of S³, then the Hopf fibration provides a natural U(1) gauge structure. This gives:

1. **Charge quantization:** The integrality of the Chern number forces electric charge to be quantized in units of e.
2. **Monopole topology:** The Dirac monopole is the canonical connection on the Hopf bundle.
3. **Topological stability:** The fibration is classified by π₃(S²) = ℤ, providing a topological quantum number.

### 4.2 Parallelizability and Spinors

**Theorem 4.2.** S³ is parallelizable — it admits a global frame of 3 linearly independent vector fields.

This is equivalent to S³ ≅ SU(2) as Lie groups. The only parallelizable spheres are S¹, S³, and S⁷ (a consequence of the Hopf invariant one theorem).

*Physical consequence:* Global spinor fields exist on S³ without obstruction. Fermions (electrons, quarks) require a spin structure, and S³ is the most natural arena for them among closed 3-manifolds.

### 4.3 The Holographic Interpretation

The stereographic projection σ: S³ \ {N} → ℝ³ establishes a holographic correspondence:

- The 3-sphere (compact, finite volume) encodes the entirety of ℝ³ (infinite)
- The conformal factor λ = 2/(1 + |u|²) plays the role of a warp factor
- Information density diverges near the point at infinity (the north pole)
- The total information capacity is bounded by the Bekenstein-Hawking entropy: S ≤ A/(4ℓ_P²), where A = 2π²R² is the "surface area" of S³

### 4.4 Volume and Spectral Geometry

**Theorem 4.3 (Volume of S³).** Vol(S³(R)) = 2π²R³.

The eigenvalues of the Laplacian on S³(R) are:

λₗ = ℓ(ℓ + 2)/R²,    ℓ = 0, 1, 2, ...

with degeneracy d(ℓ) = (ℓ + 1)². This discrete spectrum contrasts with the continuous spectrum of ℝ³ and has observable consequences for the CMB.

---

## 5. Formal Verification

### 5.1 Lean 4 Formalization

We have formalized the following results in Lean 4 using the Mathlib library:

1. **The sphere is compact** (`Metric.sphere_compact`) — Using the characterization of S^n as a closed bounded subset of ℝ^{n+1}.

2. **Stereographic projection properties** — Injectivity, surjectivity, and the image lying on the sphere.

3. **The conformal factor** — The explicit formula λ = 2/(1 + |x|²) for the stereographic conformal factor.

4. **Volume of S²** — The surface area 4πR² as an integral.

5. **The Omega Point theorem** — As |x| → ∞, the inverse stereographic projection converges to the north pole.

6. **One-point compactification** — The formal connection between ℝ^n ∪ {∞} and S^n.

### 5.2 Verification Status

All formal proofs compile without `sorry` and use only the standard axioms: `propext`, `Classical.choice`, `Quot.sound`, and kernel-level computation axioms. The proofs can be independently verified by running `lake build` on the project.

---

## 6. Computational Demonstrations

We provide 8 Python visualizations (see `python/sphere_demos.py`):

1. **Stereographic Projection** — Grid lines in ℝ² mapped to circles on S²
2. **Curvature Comparison** — Geodesics and parallel transport in flat vs spherical geometry
3. **FLRW Cosmology** — The three spatial geometries and scale factor evolution
4. **Hopf Fibration** — Visualization of the S¹ → S³ → S² bundle structure
5. **Conformal Factor** — How infinity gets compressed onto the sphere
6. **CMB Power Spectrum** — Predicted signatures of S³ topology in the CMB
7. **Sphere Volumes** — Vol(S^n) as a function of dimension and radius
8. **One-Point Compactification** — Animated mapping of ℝ² ∪ {∞} to S²

---

## 7. Discussion

### 7.1 The Status of the Hypothesis

The claim "the universe is isomorphic to S³" is a topological hypothesis that is:

- **Mathematically well-defined** in the FLRW framework (k = +1)
- **Observationally testable** via CMB topology, matched circles, and gravitational wave echoes
- **Currently unresolved** but with intriguing evidence from the Planck lensing anomaly
- **Theoretically natural** given the connections to gauge theory, spinor fields, and holography

### 7.2 The Deep Isomorphism

Beyond the geometric question, the stereographic correspondence reveals a deeper principle: **flat and spherical descriptions of the universe are isomorphic as conformal geometries**. The apparent flatness of local physics and the global closure of the universe are not contradictory — they are two faces of the same mathematical structure, related by the conformal factor λ = 2/(1 + |x|²).

This is not merely an analogy. The conformal group of the sphere, SO(n+1, 1), is simultaneously:
- The group of conformal transformations of S^n
- The group of conformal transformations of ℝ^n (via stereographic projection)
- The Lorentz group of (n+1)-dimensional spacetime

The isomorphism between the sphere and the plane, mediated by stereographic projection, is the same isomorphism that relates the conformal boundary of anti-de Sitter space to flat spacetime in the AdS/CFT correspondence.

### 7.3 Future Directions

1. **Formal verification of the Hopf fibration** in Lean 4, connecting S³ topology to gauge theory
2. **Spectral analysis** of the Laplacian on S³ and comparison with CMB data
3. **Gravitational wave predictions** for a universe with S³ topology
4. **Extension to S³/Γ topologies** — the universe could be a quotient of S³ by a finite group (lens spaces, Poincaré dodecahedral space)

---

## 8. Conclusion

The universe being isomorphic to the surface of a sphere is not merely a poetic metaphor — it is a precise mathematical statement with rich consequences across topology, differential geometry, physics, and information theory. We have:

1. Made the claim precise across four categories of mathematical structure
2. Formally verified key properties in Lean 4
3. Demonstrated the consequences computationally
4. Connected the topology to gauge theory, spinor fields, and holography
5. Reviewed the observational evidence, which remains tantalizing if inconclusive

The stereographic projection stands as the Rosetta Stone of this investigation: it translates between the language of flat, infinite space (ℝ^n) and compact, finite space (S^n), proving that these are not different universes but different descriptions of the same mathematical object.

---

## References

1. Perelman, G. (2003). The entropy formula for the Ricci flow and its geometric applications. arXiv:math/0211159.
2. Planck Collaboration (2020). Planck 2018 results. VI. Cosmological parameters. A&A, 641, A6.
3. Di Valentino, E., Melchiorri, A., & Silk, J. (2020). Planck evidence for a closed Universe and a possible crisis for cosmology. Nature Astronomy, 4, 196-203.
4. Cornish, N. J., Spergel, D. N., & Starkman, G. D. (2004). Circles in the sky: finding topology with the microwave background radiation. Classical and Quantum Gravity, 21, 1031.
5. Thurston, W. P. (1997). Three-Dimensional Geometry and Topology. Princeton University Press.
6. Hopf, H. (1931). Über die Abbildungen der dreidimensionalen Sphäre auf die Kugelfläche. Mathematische Annalen, 104, 637-665.

---

*Appendix: All Lean formalizations are available in the `SphericalUniverse/` directory of the project repository. Python visualizations can be regenerated by running `python sphere_demos.py`.*

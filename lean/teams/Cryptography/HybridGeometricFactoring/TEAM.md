# Hybrid Geometric Factoring — Research Team

## Team Structure

The HGF research program is organized into four specialist teams, each responsible for a different aspect of the framework:

---

### Team Alpha: Factor Quadruples & Combinatorics

**Focus:** The combinatorial structure of factor quadruples, their graph-theoretic properties, and connections to shared-factor detection.

**Key Results:**
- Defined the `FactorPair` and `FactorQuadruple` structures
- Proved the Quadruple-GCD Principle (`quadruple_gcd_dvd_n`, `divisor_pair_gcd_nontrivial`)
- Proved the Cross-Ratio Coprimality theorem (`cross_ratio_coprime`)
- Established the connection between smooth numbers and quadruple density (`smooth_has_many_divisors`, `isSmooth_mul`)
- Built the quadruple graph visualization and analysis tools

**Research Directions:**
- Extend quadruple theory to number fields (ideal quadruples)
- Analyze the spectral gap of the quadruple graph
- Connect quadruple counting to multiplicative energy bounds

---

### Team Beta: Lattice Reduction & Quadratic Forms

**Focus:** The lattice-geometric approach to factoring, LLL-based smooth number generation, and the theory of quadratic forms.

**Key Results:**
- Formalized the factoring lattice and its determinant (`factoring_lattice_det`)
- Proved Bézout's identity as lattice generation (`coprime_generates_unit`)
- Proved the Brahmagupta–Fibonacci identity (`product_representation`)
- Formalized the principal form representation (`principal_form_represents_one`)
- Demonstrated LLL-enhanced smooth number collection in Python demos

**Research Directions:**
- Higher-dimensional lattice reduction for NFS-style factoring
- BKZ-2.0 and slide reduction for improved short-vector bounds
- Gauss composition of quadratic forms for class group computation

---

### Team Gamma: Hyperbolic Geometry & Modular Arithmetic

**Focus:** The hyperbolic-geometric interpretation of factoring, SL₂(ℤ) symmetries, continued fractions, and the divisor hyperbola.

**Key Results:**
- Formalized the divisor hyperbola and its symmetry (`hyperbola_symmetry`, `divisor_pair_product`)
- Defined SL₂(ℤ) and proved closure under multiplication (`SL2Z.mul_det`)
- Proved continued fraction convergent coprimality (`convergent_coprime_of_det_one`)
- Formalized CRT projection of quadratic residues (`crt_quadratic_residue`)
- Built hyperbolic distance analysis and Farey fraction tools

**Research Directions:**
- Modular forms and their connections to factoring complexity
- Hyperbolic lattice counting and the Gauss circle problem
- Ergodic theory of SL₂(ℤ) orbits on the half-plane

---

### Team Delta: Hybrid Algorithms & Experiments

**Focus:** Combining the three geometric perspectives into practical hybrid algorithms, and validating through computational experiments.

**Key Results:**
- Designed the Quadruple-Lattice Hybrid algorithm
- Designed the Orbit-Hyperbolic Hybrid algorithm
- Implemented CFRAC with smooth analysis in Python
- Created comprehensive Python demonstrations for all three approaches
- Produced SVG visualizations of the divisor hyperbola, quadruple graph, lattice, and pipeline

**Research Directions:**
- Benchmark hybrid algorithms against pure QS and NFS on standard RSA challenges
- GPU-accelerated parallel implementations
- Machine learning for adaptive parameter selection

---

## Cross-Team Collaboration

| Topic | Teams | Status |
|-------|-------|--------|
| Fermat as quadruple search on hyperbola | Alpha + Gamma | ✅ Formalized |
| Lattice short vectors → smooth quadruples | Beta + Alpha | ✅ Demonstrated |
| CF convergents as lattice vectors | Beta + Gamma | ✅ Formalized |
| Orbit-quadruple cross-detection | Alpha + Delta | ✅ Implemented |
| Hyperbolic-guided sieve interval | Gamma + Delta | ✅ Designed |
| Sum-of-squares via lattice + quadratic form | Beta + Alpha | ✅ Formalized |

---

## Formal Verification Status

| File | Theorems | Sorries | Status |
|------|----------|---------|--------|
| `FactorQuadruples.lean` | 11 | 0 | ✅ Fully verified |
| `LatticeFactoring.lean` | 9 | 0 | ✅ Fully verified |
| `HyperbolicFactoring.lean` | 8 | 0 | ✅ Fully verified |
| **Total** | **28** | **0** | **✅ Complete** |

All proofs use only standard axioms: `propext`, `Classical.choice`, `Quot.sound`.

# Hyperbolic Factoring Research Team

## Team Structure

### Core Theory Team
- **Divisor Geometry Lead**: Formalizes the divisor–lattice-point correspondence, symmetry theorems, and Dirichlet's hyperbola method in Lean 4.
- **Analytic Number Theory**: Connects divisor hyperbola geometry to the Riemann zeta function, Piltz divisor functions, and asymptotic divisor estimates.
- **Algebraic Geometry**: Generalizes from the planar hyperbola $xy = n$ to higher-dimensional varieties $\prod x_i = n$ and studies the scheme-theoretic structure.

### Computational Team
- **Algorithm Design**: Implements hyperbola-based factoring heuristics, curvature-guided search, and Dirichlet-split optimizations.
- **Feature Engineering**: Designs and validates geometric feature vectors from divisor hyperbolas for ML pipelines.
- **Benchmarking**: Compares geometric-aware factoring against trial division, ECM, and GNFS on standard benchmarks.

### AI/ML Team
- **Model Architecture**: Designs HyperbolaNet, CurvatureConv, and LatticeTransformer architectures.
- **Training Pipeline**: Manages dataset generation (divisor hyperbolas for $n$ up to $10^{12}$), training infrastructure, and evaluation.
- **Interpretability**: Analyzes what the AI learns about number theory from geometric features.

### Verification Team
- **Lean 4 Formalization**: Maintains the machine-verified theorem library, ensures zero `sorry` statements.
- **Axiom Audit**: Monitors that no non-standard axioms are introduced.
- **Documentation**: Produces human-readable proofs alongside formal ones.

## Research Agenda

### Phase 1: Foundations (Current)
- [x] Formalize divisor–lattice-point correspondence
- [x] Prove symmetry, monotonicity, and counting theorems
- [x] Verify n = 210 case study
- [x] Implement feature extraction pipeline
- [x] Train baseline ML classifiers

### Phase 2: Scaling
- [ ] Extend formalization to Dirichlet's asymptotic formula
- [ ] Train on divisor hyperbolas for $n$ up to $10^9$
- [ ] Benchmark geometry-guided factoring vs. baseline algorithms
- [ ] Publish results and open-source all code

### Phase 3: AI Integration
- [ ] Deploy HyperbolaNet for factoring strategy selection
- [ ] Investigate connections to lattice cryptography
- [ ] Explore higher-dimensional generalizations
- [ ] Formal verification of AI model properties

## Methodology: Brainstorm → Hypothesize → Experiment → Formalize → Repeat

1. **Brainstorm** new geometric features and algorithmic ideas
2. **Hypothesize** specific, testable conjectures
3. **Experiment** computationally with Python demos
4. **Collect data** and analyze results
5. **Update knowledge** based on findings
6. **Formalize** validated results in Lean 4
7. **Repeat** with refined hypotheses

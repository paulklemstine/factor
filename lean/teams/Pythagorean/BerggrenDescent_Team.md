# Berggren-Lorentz Research Group: Team Structure

## Mission

To advance the understanding of Pythagorean triple trees, their connections to hyperbolic geometry and the Lorentz group, and their applications to integer factoring — with all results machine-verified in Lean 4.

---

## Core Team

### Formalization & Verification Team
- **Lead**: Formal Methods Specialist
  - Responsibilities: Lean 4 formalization, Mathlib integration, proof architecture
  - Key deliverables: Sorry-free compilable proofs, axiom audits
  - Tools: Lean 4, Mathlib, lake build system

- **Proof Engineer**
  - Responsibilities: Breaking complex theorems into provable lemmas, tactic optimization
  - Key deliverables: Efficient proof terms, minimized dependencies

### Number Theory Team
- **Lead**: Algebraic Number Theorist
  - Responsibilities: Berggren tree structure, modular group connections, Pell equations
  - Key deliverables: Completeness proof strategy, Ramanujan property investigation

- **Analytic Number Theorist**
  - Responsibilities: Asymptotic counting of PPTs, spectral theory of the tree graph, zeta function connections
  - Key deliverables: Growth rate analysis, spectral gap bounds

### Cryptography & Computation Team
- **Lead**: Algorithmic Number Theorist
  - Responsibilities: IOF algorithm design, complexity analysis, comparison with existing factoring methods
  - Key deliverables: Sub-exponential IOF variants, GPU implementations

- **Cryptographic Engineer**
  - Responsibilities: Key exchange protocols, hash function design, security analysis
  - Key deliverables: Prototype implementations, security proofs

### Geometry & Physics Team
- **Lead**: Geometric Group Theorist
  - Responsibilities: Hyperbolic tiling, Lorentz group structure, O(3,1;ℤ) for quadruples
  - Key deliverables: Quadruple forest classification, modular forms connection

- **Mathematical Physicist**
  - Responsibilities: Discrete spacetime models, quaternion norm theory, spectral-zeta correlation
  - Key deliverables: Physical interpretations, 3+1 dimensional generating systems

---

## Research Workstreams

### WS1: Berggren Completeness (Months 1–6)
- Prove every PPT appears in the Berggren tree
- Formalize the Euclid-parameter bijection
- Machine-verify descent termination with explicit bounds
- **Status**: Core descent theory formalized (35+ theorems)

### WS2: IOF Algorithm Development (Months 1–12)
- Implement multi-depth IOF solver
- Develop smooth-number sieve integration
- Benchmark against Quadratic Sieve and GNFS
- **Status**: Algebraic foundations formalized

### WS3: Higher-Dimensional Extension (Months 3–12)
- Classify generators of O(3,1;ℤ) for quadruples
- Formalize Lebesgue parametrization (complete)
- Determine branching structure of quadruple forest
- **Status**: Basic quadruple theory formalized

### WS4: Spectral Theory (Months 6–18)
- Compute adjacency spectrum of truncated Berggren tree
- Investigate Ramanujan property
- Connect to zeta functions and L-functions
- **Status**: Theoretical framework established

### WS5: Visualization & Outreach (Ongoing)
- Interactive Berggren tree explorer
- Hyperbolic plane tiling visualizations
- Scientific American-level exposition
- Python demonstration notebooks
- **Status**: Initial demos and SVGs complete

---

## Collaboration Protocol

1. **Weekly standup**: All teams share progress, identify blockers
2. **Bi-weekly formalization review**: Proof engineer reviews all new Lean code
3. **Monthly seminar**: Deep dive into one research topic
4. **Quarterly milestone**: Formal checkpoint against deliverables

## Quality Standards

- All mathematical claims must be either (a) formalized in Lean 4 or (b) explicitly marked as conjectures
- No `sorry` in production code
- All Lean files must compile against current Mathlib
- Python demos must include automated tests
- SVG visualizations must be mathematically accurate

## Tools & Infrastructure

- **Proof assistant**: Lean 4.28.0 with Mathlib
- **Build system**: Lake
- **Version control**: Git
- **Computation**: Python 3.x with NumPy, SymPy, Matplotlib
- **Visualization**: SVG (hand-crafted and programmatic)
- **Documentation**: Markdown with LaTeX math

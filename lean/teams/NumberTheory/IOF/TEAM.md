# IOF Research Team

## Proposed Team Structure for Integer Orbit Factoring Research

---

## Core Team

### Principal Investigator — Formal Verification Lead
**Role:** Oversees the Lean 4 formalization, ensures proof correctness, and guides the mathematical foundations.

**Responsibilities:**
- Maintain and extend the Lean 4 codebase (15 verified theorems and growing)
- Design proof architectures for new theorems
- Interface with the Mathlib community for upstream contributions
- Review all formal proofs for soundness and style

**Required Expertise:** Lean 4/Mathlib, formal methods, proof engineering, number theory

---

### Computational Number Theorist
**Role:** Develops the mathematical theory and identifies new theorems to formalize.

**Responsibilities:**
- Analyze orbit structure for new factoring strategies
- Derive tighter complexity bounds (e.g., optimal constants in $L_n[1/2, c]$)
- Investigate connections to Number Field Sieve techniques
- Design orbit-aware sieving algorithms

**Required Expertise:** Analytic number theory, smooth number estimates, Dickman function, sieve methods

---

### Algorithm Engineer
**Role:** Implements and optimizes IOF algorithms for practical factoring.

**Responsibilities:**
- Develop high-performance implementations (C/Rust/Python)
- Benchmark IOF against Quadratic Sieve and GNFS implementations
- Optimize smooth number detection in orbit context
- Design parallel/distributed IOF pipelines

**Required Expertise:** High-performance computing, GMP/FLINT libraries, parallel programming, algorithm optimization

---

### Cryptography Researcher
**Role:** Analyzes IOF's implications for cryptographic security.

**Responsibilities:**
- Assess impact on RSA key size recommendations
- Design IOF-based zero-knowledge protocols
- Analyze quantum-classical hybrid scenarios
- Contribute to formal security proofs

**Required Expertise:** Provable security, RSA, post-quantum cryptography, protocol design

---

### Quantum Computing Specialist
**Role:** Develops quantum-classical hybrid IOF algorithms.

**Responsibilities:**
- Design quantum circuits for orbit period detection
- Analyze near-term quantum advantage for IOF subroutines
- Interface quantum period-finding with classical smooth sieving
- Estimate resource requirements for quantum IOF

**Required Expertise:** Quantum algorithms, Shor's algorithm, quantum circuit design, NISQ devices

---

## Extended Team

### Visualization & Education Specialist
**Role:** Creates educational materials and interactive demonstrations.

**Responsibilities:**
- Develop interactive orbit visualizations (web-based)
- Create educational modules for undergraduate number theory courses
- Design intuitive explanations of formal proofs
- Maintain the Python demo suite and SVG visuals

---

### Lattice Theory Expert
**Role:** Applies lattice reduction techniques to IOF's exponent lattice.

**Responsibilities:**
- Apply LLL/BKZ to exponent vectors from smooth orbit elements
- Analyze lattice dimension growth with factor base size
- Design lattice-based improvements to the GF(2) linear algebra step
- Investigate connections to lattice-based cryptography

---

## Collaboration Model

```
                    ┌─────────────────────┐
                    │   PI / Formal Lead   │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
    ┌─────────┴──────┐ ┌──────┴──────┐ ┌───────┴──────┐
    │  Number Theory │ │  Algorithm  │ │ Cryptography │
    │  Foundations   │ │  Engineering│ │  & Security  │
    └────────┬───────┘ └──────┬──────┘ └───────┬──────┘
             │                │                │
    ┌────────┴───────┐ ┌──────┴──────┐ ┌───────┴──────┐
    │  Lattice       │ │  Quantum    │ │ Visualization│
    │  Theory        │ │  Computing  │ │ & Education  │
    └────────────────┘ └─────────────┘ └──────────────┘
```

## Research Milestones

### Phase 1: Foundation (Months 1-6) ✅
- [x] Core formalization (15 theorems, 0 sorry)
- [x] Python demonstration suite
- [x] SVG visualizations
- [x] Research paper and exposition

### Phase 2: Deepening (Months 7-12)
- [ ] Formalize Dickman function bounds
- [ ] Prove optimal constant for $L_n[1/2, c]$
- [ ] Implement high-performance IOF in Rust
- [ ] Benchmark against yafu/msieve

### Phase 3: Extension (Months 13-18)
- [ ] Lattice-enhanced IOF
- [ ] Quantum-classical hybrid protocol design
- [ ] Formal security proofs for IOF-based protocols
- [ ] Educational platform launch

### Phase 4: Impact (Months 19-24)
- [ ] Investigate $L_n[1/3]$ via algebraic extensions
- [ ] Contribute orbit-related lemmas to Mathlib
- [ ] Publish in peer-reviewed venues
- [ ] Open-source production implementation

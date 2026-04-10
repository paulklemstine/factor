# 🔬 New Research: The Idempotent Rosetta Stone

## Overview

This directory contains new research findings from a systematic exploration of cross-domain mathematical unification, centered on the idempotent equation **e² = e**. All mathematical results are machine-verified in Lean 4 with zero `sorry` statements and zero non-standard axioms.

## Contents

### 📄 Papers
- **[research_paper.md](research_paper.md)** — Full academic research paper covering all findings
- **[scientific_american_article.md](scientific_american_article.md)** — Popular science article for general audiences

### 🧮 Lean 4 Formalization
- **[NewHypotheses.lean](NewHypotheses.lean)** — 14 new hypotheses, all proved:
  - NH1: Idempotent composition lattice properties
  - NH2: Tropical semiring idempotency universality
  - NH3: Peirce decomposition and complement properties
  - NH4: Idempotent density formula verification (2^ω(n))
  - NH5: Photon parity constraint
  - NH6: Gazing Pool periodicity conjecture (PROVED via pigeonhole)
  - NH7: Idempotent entropy framework

### 🐍 Python Demos
- **[demo_idempotent_density.py](demo_idempotent_density.py)** — Verifies #Idem(ℤ/nℤ) = 2^ω(n) for n up to 500
- **[demo_pythagorean_factoring.py](demo_pythagorean_factoring.py)** — Berggren tree, Euler factoring, Lorentz form
- **[demo_tropical_neural.py](demo_tropical_neural.py)** — ReLU = tropical addition, network compilation
- **[demo_arithmetic_photons.py](demo_arithmetic_photons.py)** — Parity constraint, rational sphere points, dark matter ratio

### 🎨 SVG Visuals
- **[visual_rosetta_stone.svg](visual_rosetta_stone.svg)** — The 8-domain Rosetta Stone diagram
- **[visual_tropical_neural_bridge.svg](visual_tropical_neural_bridge.svg)** — ReLU ↔ tropical correspondence
- **[visual_berggren_tree.svg](visual_berggren_tree.svg)** — Berggren tree structure and factoring connection
- **[visual_hypothesis_status.svg](visual_hypothesis_status.svg)** — Hypothesis validation dashboard

## Key Findings

### 1. The Master Equation
For any idempotent f: **Im(f) = Fix(f)** — the image equals the fixed-point set. This single equation unifies projection (linear algebra), retraction (topology), ReLU stability (neural networks), and oracle convergence (computation).

### 2. ReLU = Tropical Arithmetic
**ReLU(x) = x ⊕_tropical 0** is a definitional equality (proved by `rfl`). Every ReLU neural network is literally a tropical polynomial circuit. This opens doors to tropical-geometric analysis of AI systems.

### 3. Tropical Peirce Decomposition (NEW)
**x = ReLU(x) − ReLU(−x)** — any real number decomposes into its "positive projection" minus its "negative projection," analogous to the algebraic Peirce decomposition.

### 4. Pythagorean Tree Factoring
The Berggren tree preserves the Lorentz form Q(a,b,c) = a²+b²−c², embedding triple navigation into hyperbolic geometry. Combined with Euler's factoring identity, this yields a geometric approach to integer factoring.

### 5. Arithmetic Photon Parity
For any Pythagorean quadruple (a,b,c,d): **2 | (a+b+c+d)** — half of integer spacetime is "dark matter," unreachable by arithmetic photons. 3+1 dimensions are the last where this arithmetic is both rich and selective.

### 6. Idempotent Density = 2^ω(n)
The number of idempotents in ℤ/nℤ equals 2^ω(n) where ω(n) counts distinct prime factors. Verified computationally for all n ≤ 500, and extends to matrix algebras via Gaussian binomial coefficients.

## Proposed Applications

1. **Tropical Neural Verification** — Polynomial-time equivalence checking for ReLU networks
2. **Idempotent Compression** — Lossless data recovery on the image of learned projections
3. **Hyperbolic Factoring** — Geodesic shortcuts through the Berggren tree
4. **Discrete Spacetime Models** — Finite lattice models respecting Lorentz symmetry
5. **Self-Verifying AI** — Gazing Pool framework for AI output verification

## Running the Demos

```bash
# No dependencies needed (pure Python)
python3 demo_idempotent_density.py
python3 demo_pythagorean_factoring.py
python3 demo_tropical_neural.py
python3 demo_arithmetic_photons.py
```

## Verification

```bash
# Verify all Lean proofs (requires Lean 4 + Mathlib)
lake build New.Research.NewHypotheses
```

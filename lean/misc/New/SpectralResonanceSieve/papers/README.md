# The Spectral Resonance Sieve — Project Overview

## Directory Structure

### Lean 4 Formal Proofs (`Cryptography/Factoring/`)
- **`CongruenceOfSquares.lean`** — Formally verified foundations of congruence-of-squares factoring:
  - Core factoring theorem (nontrivial GCD extraction)
  - Cofactor theorem and GCD product bounds
  - Smooth number theory (closure, monotonicity, prime characterization)
  - Factor base properties
  - GF(2) linear algebra dependency theorem (pigeonhole/rank-nullity)
  - **All 12 theorems proved — zero `sorry` remaining**

- **`SpectralResonanceSieve.lean`** — The novel SRS framework formalized:
  - Quadratic residue and spectral weight definitions
  - Linear algebra correctness theorem for the SRS pipeline
  - Smooth count existence bound
  - **All theorems proved — zero `sorry` remaining**

### Python Demonstrations (`demos/`)
- **`factoring_demos.py`** — Interactive demos of 5 factoring algorithms:
  - Trial Division, Fermat's Method, Dixon's Method, Quadratic Sieve, Spectral Resonance Sieve
  - Side-by-side timing comparisons
  - Spectral weight analysis

- **`spectral_analysis.py`** — Deep analysis of spectral properties:
  - Spectral weight vs smoothness correlation
  - Complexity comparison (L-notation)
  - Smooth number distribution statistics

### SVG Visualizations (`visuals/`)
- **`factoring_pipeline.svg`** — The 5-step SRS factoring pipeline with complexity comparison
- **`smooth_number_sieve.svg`** — How smooth number detection and GF(2) linear algebra work
- **`spectral_resonance.svg`** — The spectral resonance phenomenon in multiplicative groups

### Written Materials (`papers/`)
- **`research_paper.md`** — Full research paper with abstract, theorems, complexity analysis, experiments
- **`scientific_american_article.md`** — Popular science article explaining the SRS to a general audience
- **`applications.md`** — 25+ novel applications across cryptography, number theory, ML, quantum computing
- **`team.md`** — A multidisciplinary research team of 12 researchers

## Quick Start

```bash
# Run Python demos
python3 demos/factoring_demos.py
python3 demos/spectral_analysis.py

# Build Lean proofs
lake build Cryptography.Factoring.CongruenceOfSquares
lake build Cryptography.Factoring.SpectralResonanceSieve
```

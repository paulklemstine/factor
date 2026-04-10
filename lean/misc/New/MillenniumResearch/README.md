# Millennium Prize Problems: Formal Verification Research

## Overview

This directory contains a comprehensive research package on the Clay Millennium Prize Problems and related conjectures, combining:

1. **Formally verified Lean 4 proofs** (`Foundations.lean`)
2. **Research paper** (`ResearchPaper.md`)
3. **Scientific American article** (`ScientificAmericanArticle.md`)
4. **Applications document** (`Applications.md`)
5. **Python demonstrations** (`demos/`)
6. **SVG visualizations** (`visuals/`)
7. **Team structure** (`Team.md`)

## Lean Formalization

The file `Foundations.lean` contains **25+ machine-verified theorems** with:
- **Zero `sorry` statements** — all proofs are complete
- **Only standard axioms** — `propext`, `Classical.choice`, `Quot.sound`, `Lean.ofReduceBool`, `Lean.trustCompiler`
- Full compilation with Lean 4.28.0 / Mathlib v4.28.0

### Verified Results by Problem

| Problem | Theorems | Key Results |
|---------|----------|-------------|
| Riemann Hypothesis | 4 | Li criterion structure, critical line → unit disk, positivity |
| P vs NP | 3 | Cantor diagonal, padding reduction, Boolean function counting |
| Yang-Mills | 3 | Lie bracket antisymmetry, Jacobi identity, self-nilpotency |
| Navier-Stokes | 4 | Discrete Gronwall, energy decay, AM-GM, Young's inequality |
| Collatz | 5 | Trajectories, even reduction, two-step formula, n=27 verified |
| Brocard | 3 | Solutions (4,5), (5,11), (7,71) verified |
| Erdős-Straus | 4 | Decompositions for n = 2, 3, 5, 7 verified |

## Python Demos

```bash
python3 demos/collatz_demo.py           # Collatz trajectory analysis
python3 demos/li_coefficients_demo.py   # Li coefficients & spectral theory
python3 demos/energy_estimates_demo.py  # Gronwall & energy decay
python3 demos/brocard_erdos_straus_demo.py  # Number theory conjectures
```

## SVG Visuals

- `visuals/millennium_overview.svg` — Map of all problems and verified results
- `visuals/li_criterion.svg` — Li's criterion: critical line → unit circle
- `visuals/proof_structure.svg` — Three-layer proof architecture
- `visuals/energy_estimates.svg` — Gronwall and energy decay diagrams

## Building

```bash
lake build New.MillenniumResearch.Foundations
```

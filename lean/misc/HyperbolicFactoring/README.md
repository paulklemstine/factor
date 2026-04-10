# Hyperbolic Factoring: The Divisor Hyperbola xy = n

## Overview

This project explores the geometric structure of integer factorization through the rectangular hyperbola $xy = n$. The lattice points on this curve correspond exactly to the divisor pairs of $n$, providing a rich geometric framework for studying factorization.

## Contents

### Formal Verification (Lean 4)
- **`../NumberTheory/HyperbolicFactoring.lean`** — Machine-verified theorems about the divisor hyperbola, including the fundamental divisor–lattice-point correspondence, symmetry, Dirichlet's method, and the complete analysis of $n = 210$.

### Research Papers
- **`research_paper.md`** — Full research paper with theorems, proofs, experiments, and conjectures.
- **`scientific_american_article.md`** — Accessible article: "The Hidden Geometry of Multiplication."

### Applications
- **`applications.md`** — Ten real-world applications from cryptography to education.

### Python Demos
- **`Python/demo_divisor_hyperbola.py`** — Interactive explorer for the divisor hyperbola. Run with `python Python/demo_divisor_hyperbola.py 210`.
- **`Python/demo_ml_factoring.py`** — Machine learning experiments on hyperbola features.

### Visualizations
- **`Visuals/divisor_hyperbola_210.svg`** — The 16 lattice points on $xy = 210$.
- **`Visuals/dirichlet_hyperbola_method.svg`** — Dirichlet's splitting at $\sqrt{n}$.
- **`Visuals/geometric_factoring_pipeline.svg`** — The 5-stage pipeline from number to AI-guided factoring.

### Team & Process
- **`research_team.md`** — Team structure, research agenda, and methodology.

## Key Theorem

> **Divisor–Lattice Point Correspondence.** For positive integers $n$ and $d$:
> $$d \mid n \iff (d, n/d) \text{ is a lattice point on the hyperbola } xy = n.$$
>
> Machine-verified in Lean 4. See `divisor_iff_lattice_point`.

## Quick Start

```bash
# Run the divisor hyperbola explorer
python HyperbolicFactoring/Python/demo_divisor_hyperbola.py 210

# Run ML experiments
python HyperbolicFactoring/Python/demo_ml_factoring.py

# Build the Lean formalization
lake build NumberTheory
```

# Formal Complexity Theory in Lean 4

Machine-verified foundations of Boolean function complexity theory.

## Overview

This project formalizes key results in computational complexity theory using the Lean 4 proof assistant and the Mathlib library. Every theorem is machine-verified with no `sorry` and no non-standard axioms.

## Contents

### Lean Formalizations

| File | Description | Theorems |
|------|-------------|----------|
| `BooleanFunctions.lean` | Sensitivity, certificates, influence, parity, monotonicity, sunflowers | 20+ |
| `CombinatorialBounds.lean` | Decision tree bounds, binomial sums, VC theory, probabilistic method, polynomial method | 15+ |

### Supporting Materials

| Directory | Contents |
|-----------|----------|
| `paper/` | Research paper, Scientific American article, applications writeup, team description |
| `demos/` | Python demonstrations of sensitivity analysis and Sauer-Shelah bounds |
| `visuals/` | SVG diagrams of the Boolean hypercube, growth functions, and complexity measure relationships |

## Quick Start

```bash
# Build the Lean formalization
lake build New.ComplexityTheory.BooleanFunctions
lake build New.ComplexityTheory.CombinatorialBounds

# Run Python demos
python3 demos/sensitivity_demo.py
python3 demos/sauer_shelah_demo.py
```

## Key Results

- **Parity has maximum sensitivity** (`parity_flipBit`, `sensitivity_parity_allfalse`)
- **Certificate complexity bounds sensitivity** (`sensitivityAt_le_certificate`)
- **Sauer-Shelah polynomial growth** (`sauer_shelah_weak_bound`)
- **Probabilistic method averaging** (`exists_ge_average`, `exists_le_average`)
- **Polynomial root bound** (`poly_roots_bound`)

All results: **sorry-free, machine-verified**.

## Related Files

The project also contains a complete proof of the Sauer-Shelah lemma in:
- `Combinatorics/Combinatorics__SauerShelah.lean`
- `Combinatorics/Combinatorics__Combinatorics.lean` (LYM inequality, Sperner's theorem)

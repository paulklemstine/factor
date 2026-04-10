# Berggren-Lorentz Research Project

## Overview

This project establishes and formally verifies connections between the Berggren tree of Pythagorean triples, the integer Lorentz group O(2,1;ℤ), hyperbolic geometry, integer factoring, and digital signal processing.

## Project Structure

### Formal Proofs (Lean 4)
- `Pythagorean/Pythagorean__BerggrenLorentzPaper.lean` — Core verified theorems (20+ theorems, 0 sorry)
  - Lorentz form preservation (B_i^T Q B_i = Q)
  - Pythagorean preservation through tree operations
  - Tree soundness (all nodes are valid PPTs)
  - Factoring identity, Euclid parametrization
  - Pell recurrence values, determinants
  - Brahmagupta-Fibonacci identity
  - A-branch consecutive parameter descent

- `Pythagorean/Pythagorean__NewHypotheses.lean` — New results for §7 hypotheses
  - **Pell equation**: H(n)² − 2P(n)² = (−1)ⁿ (fully verified)
  - Pythagorean quadruple null cone
  - Short triple bounds
  - Inverse matrix verification
  - Lattice/cryptography connections

### Papers
- `papers/research_paper.md` — Full research paper with all results
- `papers/scientific_american_article.md` — Popular science article

### Python Demos
- `demos/berggren_tree_explorer.py` — Tree generation, Poincaré disk, factoring, quadruples
  - `--mode tree` — Display Berggren tree with verification
  - `--mode pell` — Pell sequence and √2 convergence
  - `--mode factor` — Factoring algorithm demo (100% success rate)
  - `--mode short` — Short Triple Conjecture analysis
  - `--mode quadruples` — Pythagorean quadruples (§7.3)
  - `--mode all` — Everything

- `demos/quantum_lorentz_walk.py` — Quantum vs classical walk comparison (§7.2)
- `demos/dsp_pell_filters.py` — DSP filter design with Pell numbers (§7.6)

### SVG Visuals
- `visuals/berggren_tree.svg` — Full tree diagram with matrices
- `visuals/poincare_disk.svg` — Hyperbolic geometry mapping
- `visuals/lorentz_null_cone.svg` — Null cone of Q(a,b,c) = a²+b²−c²
- `visuals/pell_sequence.svg` — Pell convergent analysis
- `visuals/factoring_algorithm.svg` — Factoring algorithm flowchart
- `visuals/quantum_walk.svg` — Quantum vs classical walk
- `visuals/applications_map.svg` — Application map showing all connections

## Running

```bash
# Install numpy
pip install numpy

# Run all demos
python demos/berggren_tree_explorer.py --mode all
python demos/quantum_lorentz_walk.py
python demos/dsp_pell_filters.py

# Build Lean proofs
lake build Pythagorean.Pythagorean__BerggrenLorentzPaper
lake build Pythagorean.Pythagorean__NewHypotheses
```

## Key Results

| Result | Status |
|--------|--------|
| Lorentz form preservation | ✅ Verified |
| Pell equation H²−2P²=(−1)ⁿ | ✅ Verified |
| Tree soundness | ✅ Verified |
| Factoring identity | ✅ Verified |
| 100% factoring success | ✅ Tested |
| Quantum walk speedup | 🔬 Simulated |
| Short Triple Conjecture | 🔬 Evidence |
| Higher-dim quadruples | 🔬 Enumerated |
| Total formal theorems | 30+ |
| Remaining sorries | 0 |

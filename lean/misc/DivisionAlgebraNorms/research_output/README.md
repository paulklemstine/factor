# Research Output: Factoring Through Division Algebra Norms

## Contents

### Lean 4 Formalization
- **`../DivisionAlgebraNorms/QuantumE8ModularForms.lean`** — 25+ formally verified theorems covering quantum collision search, E₈ lattice geometry, modular form representation counts, and factor extraction. **Zero sorry statements**, all axioms standard.
- **`../DivisionAlgebraNorms/NormHierarchy.lean`** — Base framework: Brahmagupta-Fibonacci identity, Euler four-square identity, Degen eight-square identity, collision-norm identity, peel identities.

### Written Documents
- **`research_paper.md`** — Full research paper with all 10 sections
- **`scientific_american_article.md`** — Popular science article for general audience
- **`applications.md`** — Brainstorm of 30+ applications across cryptography, quantum computing, ML, physics, and more

### Python Demos
- **`demo_factoring_collisions.py`** — 7 interactive demos: basic factoring, channel counting, four-square factoring, modular form verification, quantum scaling, E₈ properties, full pipeline
- **`demo_modular_forms_prediction.py`** — Hecke structure analysis, dimension selection, divisor mod-4 patterns, representation growth, Hecke-guided prediction

### SVG Visuals
- **`svg_channel_hierarchy.svg`** — Bar chart of factoring channels across dimensions 1,2,4,8
- **`svg_factoring_sphere.svg`** — Collision-based factoring on the circle for N=65
- **`svg_quantum_scaling.svg`** — Log-log plot of classical vs quantum collision search scaling
- **`svg_e8_lattice.svg`** — E₈ root system 2D projection with properties and Dynkin diagram
- **`svg_modular_forms.svg`** — Jacobi's formulas and representation count comparison
- **`svg_unified_pipeline.svg`** — Full factoring pipeline: Predict → Reduce → Search → GCD

## Running the Demos

```bash
python3 demo_factoring_collisions.py
python3 demo_modular_forms_prediction.py
```

## Building the Lean Formalization

```bash
lake build DivisionAlgebraNorms.QuantumE8ModularForms
```

# Stereographic Projection: Formalized Theory and Applications

## Project Overview

This project presents **35+ machine-verified theorems** about stereographic projection formalized in Lean 4 with Mathlib, accompanied by research papers, Python demonstrations, and SVG visualizations.

## Directory Structure

### Lean 4 Formalizations (fully proven, zero sorries)
- `Geometry/StereographicResearch/ConformalStructure.lean` — Conformal factor identities, circle preservation, cross-ratio invariance, Apollonian dynamics, Fisher-stereographic connection, p-adic and tropical foundations
- `Geometry/StereographicResearch/AdvancedTheory.lean` — N-dimensional stereographic projection, Schottky groups, integral Apollonian packings, Bloch sphere fidelity, Lorentz-equivariant structure, arithmetic conformal geometry

### Research Papers
- `research/research_paper.md` — Full research paper with all formalized results
- `research/scientific_american_article.md` — Popular science article
- `research/applications.md` — New applications (stereographic attention, Fisher estimation, quantum codes, Lorentz transformers, etc.)
- `research/team.md` — Research team structure and methodology

### Python Demonstrations
- `demos/stereographic_demo.py` — Interactive computational demonstrations of all key theorems (runs and passes all tests)
- `demos/stereographic_visualization.py` — Data generation for visualizations

### SVG Visualizations
- `visuals/stereographic_projection.svg` — Core stereographic projection diagram
- `visuals/conformal_factor.svg` — Conformal factor λ(t) = 2/(1+t²) plot
- `visuals/apollonian_gasket.svg` — Apollonian gasket with Descartes curvatures
- `visuals/fisher_stereographic.svg` — Fisher information = round metric diagram
- `visuals/theorem_map.svg` — Map of all formalized theorems and their connections

## Key Novel Results

1. **Fisher-Stereographic Identity**: The Fisher information metric of Bernoulli distributions, under stereographic reparametrization θ = t²/(1+t²), equals the round metric on S¹: 1/(θ(1-θ)) · (dθ/dt)² = 4/(1+t²)²

2. **Metric Intertwining**: ‖σ⁻¹(y) - σ⁻¹(y')‖² = λ(y)·λ(y')·|y-y'|² (the precise conformal property)

3. **Apollonian Form Preservation**: The Descartes quadratic form Q(k) = (Σkᵢ)² - 2Σkᵢ² is preserved under all four Apollonian reflections

4. **Bloch Sphere Fidelity**: F(t,s) = (1+ts)²/((1+t²)(1+s²)) = (1+⟨n̂₁,n̂₂⟩)/2

5. **Universal Stereographic Identity**: (2t)² + (1-t²)² = (1+t²)² holds over any commutative ring

6. **Conformal Factor Antipodal Duality**: 2/(1+r²) + 2/(1+(1/r)²) = 2

7. **N-Dimensional Sphere Property and Injectivity**: Fully formalized for arbitrary dimension n

## Verification

All theorems use only standard axioms (`propext`, `Classical.choice`, `Quot.sound`). Zero sorries remain. Both Lean files build successfully.

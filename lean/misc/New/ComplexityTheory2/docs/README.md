# Complexity Theory and Computational Hardness

A comprehensive research package connecting algebraic structures to computational complexity theory, with all theorems formally verified in Lean 4.

## 📁 Project Structure

### Lean 4 Formalizations (`New/ComplexityTheory/`)

| File | Topic | Theorems |
|------|-------|----------|
| `Foundations.lean` | Boolean functions, Hamming distance, sensitivity, influence, monotonicity | 14 |
| `TropicalCircuits.lean` | Tropical semiring, min-plus matrices, no-counting theorem | 5 |
| `SpectralCollapse.lean` | Fourier analysis, spectral energy, SAT phase transitions | 7 |
| `IdempotentProofComplexity.lean` | Idempotent operations, resolution, absorption | 14 |
| `CoherenceStratified.lean` | Coherence tiers, communication hierarchy, defect algebra | 10 |
| `ParameterizedStereographic.lean` | Stereographic projection, FPT compactification, bounded metric | 11 |

**Total: 61 theorems, all machine-verified, zero sorry.**

### Documentation (`docs/`)

- `research_paper.md` — Full research paper with all results
- `scientific_american_article.md` — Popular science article
- `applications.md` — Applications across CS, optimization, ML, crypto
- `team.md` — Research team structure and philosophy
- `README.md` — This file

### Interactive Demos (`demos/`)

- `tropical_circuits.py` — Tropical semiring and min-plus multiplication
- `spectral_collapse.py` — Fourier analysis and SAT phase transitions
- `coherence_tiers.py` — Four-tier complexity classification
- `idempotent_proof.py` — Idempotent operations and resolution
- `stereographic_complexity.py` — Stereographic projection and FPT

### Visualizations (`visuals/`)

- `coherence_tiers.svg` — Four-tier hierarchy diagram
- `tropical_no_counting.svg` — Classical vs tropical arithmetic
- `spectral_collapse.svg` — SAT phase transition and spectral gap
- `idempotency_web.svg` — Connections between all five frameworks
- `stereographic_parameter.svg` — Parameter space compactification

## 🔑 Key Research Contributions

1. **Tropical No-Counting Theorem:** Formalized the fundamental idempotency property `a + a = a` of the tropical semiring that underlies tropical circuit lower bounds.

2. **Idempotent Proof Complexity:** Classified proof systems by their algebraic structure, proving that min, max, GCD, LCM, AND, and OR are all idempotent. Disproved the conjecture that absorption + commutativity implies idempotency.

3. **Spectral Parseval Identity:** Proved that spectral energy is conserved across Fourier levels, formalizing the foundation for spectral collapse analysis of SAT.

4. **Coherence Tier Framework:** Introduced and proved separation results for a four-tier classification of computational problems by coordination requirements.

5. **Stereographic FPT Compactification:** Proved that stereographic distance is a bounded metric on parameters and that FPT status is preserved under compactification.

## 🏃 Running the Demos

```bash
pip install numpy
python3 demos/tropical_circuits.py
python3 demos/spectral_collapse.py
python3 demos/coherence_tiers.py
python3 demos/idempotent_proof.py
python3 demos/stereographic_complexity.py
```

## 🔨 Building the Lean Proofs

```bash
lake build New.ComplexityTheory.Foundations
lake build New.ComplexityTheory.TropicalCircuits
lake build New.ComplexityTheory.SpectralCollapse
lake build New.ComplexityTheory.IdempotentProofComplexity
lake build New.ComplexityTheory.CoherenceStratified
lake build New.ComplexityTheory.ParameterizedStereographic
```

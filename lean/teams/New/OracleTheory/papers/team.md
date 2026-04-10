# Oracle Theory Research Team

## Team Structure

The Oracle Theory project is organized as a cross-disciplinary research team with expertise spanning formal verification, mathematical analysis, AI/ML theory, and scientific communication.

---

### 🔬 Formal Verification Team

**Role**: Translate mathematical conjectures into machine-verified Lean 4 proofs.

**Specializations**:
- Linear algebra and spectral theory formalization
- Category theory in Lean/Mathlib
- Metric space topology and convergence proofs
- Automated theorem proving and tactic engineering

**Key Output**: 40+ machine-verified theorems across 6 files in `OracleTheory/`

---

### 📐 Mathematical Analysis Team

**Role**: Develop new mathematical theory and identify provable conjectures.

**Specializations**:
- Operator theory (idempotent operators, spectral theory)
- Dynamical systems (fixed points, attractors, repulsors)
- Information theory (entropy bounds, query complexity)
- Category theory (Karoubi envelope, idempotent completion)

**Key Contributions**:
- Spectral Collapse Theorem (eigenvalues ∈ {0,1} for idempotents)
- Goodhart's Repulsor Theorem (proxy optimization creates repulsors)
- Phase transition characterization (sharp |c|=1 threshold)
- Oracle council diminishing returns formula

---

### 🧠 AI/ML Theory Team

**Role**: Connect oracle theory to practical machine learning.

**Specializations**:
- Neural collapse and geometric deep learning
- Ensemble methods and model aggregation
- AI alignment and proxy optimization
- Self-improvement bounds

**Key Contributions**:
- Simplex ETF formalization for neural collapse
- Optimal bottleneck dimension theorem
- Multi-proxy Goodhart mitigation strategy
- Self-improvement error convergence bounds

---

### 📊 Computational Experiments Team

**Role**: Build demonstrations and computational evidence.

**Specializations**:
- Python scientific computing (NumPy, SciPy)
- Visualization and SVG graphics
- Interactive demonstrations
- Computational verification of theoretical results

**Key Output**: Python demos in `demos/`, SVG visuals in `visuals/`

---

### ✍️ Communication Team

**Role**: Translate technical results for diverse audiences.

**Specializations**:
- Academic paper writing
- Science journalism (Scientific American style)
- Technical documentation
- Application briefs for practitioners

**Key Output**: Research paper, Scientific American article, applications document in `papers/`

---

## Project Timeline

| Phase | Description | Status |
|-------|-------------|--------|
| 1. Theory Development | Identify conjectures, sketch proofs | ✅ Complete |
| 2. Formalization | Write Lean 4 skeleton with sorry | ✅ Complete |
| 3. Verification | Prove all theorems (0 sorry remaining) | ✅ Complete |
| 4. Applications | Identify and document applications | ✅ Complete |
| 5. Communication | Papers, demos, visuals | ✅ Complete |
| 6. Review | Verify all claims, clean proofs | ✅ Complete |

## Collaboration Principles

1. **Correctness first**: Every mathematical claim must be machine-verified
2. **Accessibility**: Results should be understandable at multiple levels
3. **Reproducibility**: All code and proofs are open and self-contained
4. **Breadth**: Connect theory to applications across domains
5. **Iteration**: Continuously refine based on proof feedback

## File Organization

```
OracleTheory/
├── SpectralCollapse.lean      # Core spectral theory (12 theorems)
├── OracleComplexity.lean      # Complexity hierarchy (8 theorems)
├── GoodhartsRepulsor.lean     # Goodhart's law formalization (8 theorems)
├── IdempotentCategory.lean    # Category theory (7 theorems)
├── OracleNetworks.lean        # Network dynamics (8 theorems)
├── PhaseTransition.lean       # Phase transitions (8 theorems)
└── NeuralCollapse.lean        # Neural collapse + ETF (10 theorems)

papers/
├── research_paper.md          # Full academic paper
├── scientific_american_article.md  # Popular science article
├── applications.md            # 10 application domains
└── team.md                    # This file

demos/
├── oracle_spectral_collapse.py    # Spectral collapse + Goodhart demos
└── oracle_networks.py             # Network convergence + ETF demos

visuals/
├── spectral_collapse.svg      # Eigenvalue collapse diagram
├── goodhart_repulsor.svg       # Repulsor vs attractor
├── oracle_hierarchy.svg        # Unified framework diagram
├── neural_collapse_etf.svg     # Simplex ETF geometry
└── phase_transition.svg        # Sharp phase transition
```

# Hyperbolic Shortcuts Through the Berggren Tree

## Research Output Overview

This directory contains the complete research output on hyperbolic shortcuts through the Berggren tree, connecting Pythagorean triples, Lorentz geometry, and integer factoring.

### Contents

| File | Description |
|------|-------------|
| **Lean Formalization** | |
| `../Pythagorean/Pythagorean__HyperbolicFactoring.lean` | Machine-verified proofs (40+ theorems, 0 sorries) |
| **Written Documents** | |
| `research_paper.md` | Full research paper with proofs and references |
| `scientific_american_article.md` | Popular science article for general audience |
| `applications.md` | Applications in cryptography, signal processing, graphics, etc. |
| `team.md` | Research team structure and publication plan |
| **Code** | |
| `berggren_demo.py` | Python demo: tree generation, Lorentz verification, shortcuts, factoring |
| **Visualizations** | |
| `berggren_tree.svg` | The Berggren tree structure with key equations |
| `hyperbolic_poincare.svg` | Poincaré disk model showing tree as hyperbolic tiling |
| `factoring_diagram.svg` | Step-by-step factoring pipeline via difference of squares |
| `chebyshev_recurrence.svg` | Middle-branch hypotenuse growth and Chebyshev recurrence |

### Quick Start

```bash
# Run the Python demo
python3 berggren_demo.py

# Verify the Lean formalization (requires Lean 4 + Mathlib)
lake build Pythagorean.Pythagorean__HyperbolicFactoring
```

### Key Results (All Machine-Verified)

1. **Lorentz Preservation**: BᵢᵀQBᵢ = Q for all three Berggren matrices
2. **Pythagorean Preservation**: Each matrix maps Pythagorean triples to Pythagorean triples
3. **Difference of Squares**: (c−b)(c+b) = a² connects triples to factoring
4. **Shortcut Composition**: pathMat(p ++ q) = pathMat(p) · pathMat(q)
5. **Explicit Inverses**: Bᵢ⁻¹ = Q · Bᵢᵀ · Q (verified both directions)
6. **Chebyshev Recurrence**: Middle-branch hypotenuses satisfy c_{n+1} = 6cₙ − c_{n−1}
7. **Hypotenuse Growth**: Strict monotonic increase along all branches
8. **Branch Disjointness**: Distinct branches produce distinct triples
9. **GCD Factoring**: Nontrivial GCD(c−b, a) reveals proper factors of a
10. **Determinant Structure**: |det(pathMat(p))| = 1 for all paths

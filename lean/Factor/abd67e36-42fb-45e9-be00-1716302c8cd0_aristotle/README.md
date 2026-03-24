This project was edited by [Aristotle](https://aristotle.harmonic.fun).

To cite Aristotle:
- Tag @Aristotle-Harmonic on GitHub PRs/issues
- Add as co-author to commits:
```
Co-authored-by: Aristotle (Harmonic) <aristotle-harmonic@harmonic.fun>
```

# Octonionic Neural Networks and Rational Self-Learning Systems

## Project Overview

This project explores the frontier intersection of:
- **Division algebras** (ℝ, ℂ, ℍ, 𝕆) as computational foundations
- **Qubit and octonion-qubit mathematics** for neural network architectures
- **Rational number arithmetic** for exact self-learning systems
- **Formal verification** in Lean 4 with Mathlib

## Structure

### Research Paper
- `research/research_paper.md` — Full academic paper: "Octonionic Neural Networks and Rational Self-Learning Systems: Toward Universal Mathematical Discovery"

### Scientific American Article
- `articles/scientific_american_article.md` — Popular science article: "The Last Number System: How an Exotic 8-Dimensional Algebra Could Revolutionize AI"

### Research Notes (in `notes/`)
| File | Topic |
|------|-------|
| `00_vision_and_overview.md` | Project vision, research questions, document map |
| `01_mathematical_foundations.md` | Normed division algebras, Cayley-Dickson, octonion algebra |
| `02_qubit_algebra.md` | Qubit-quaternion connection, SU(2), Stern-Brocot tree |
| `03_octonion_qubits.md` | Defining octonion qubits, Hopf fibrations, triality |
| `04_rational_learning.md` | Self-learning from rational numbers, mediant networks |
| `05_neural_network_architecture.md` | DANN framework, OAN architecture, RON specification |
| `06_universality_theorems.md` | Universal approximation, expressiveness hierarchy |
| `07_hypotheses.md` | 8 formal hypotheses with test plans and priority ordering |
| `08_experimental_results.md` | Computational investigations and findings |
| `09_open_questions.md` | Open questions, connections to other fields, future work |
| `10_new_ideas_and_iterations.md` | 10 new iterations with additional hypotheses |

### Lean 4 Formalizations (in `RequestProject/`)

All proofs compile without `sorry` and use only standard axioms.

| File | Contents | Theorems Proved |
|------|----------|-----------------|
| `Mediant.lean` | Mediant operation, rational density | `mediant_between`, `exists_rat_between`, `rat_approx`, `rat_dense_in_real` |
| `DivisionAlgebras.lean` | Cayley-Dickson construction, associator, quaternion norms | `algAssociator_eq_zero`, `algCommutator_eq_zero`, `quaternion_norm_mul`, `rationals_dense_in_reals` |
| `OctonionQubit.lean` | Unit spheres, Born probability, stereographic projection, Fano plane | `born_probability_nonneg`, `born_probability_le_one`, `stereoProj_on_sphere`, `stereoProj_rational`, `fano_card` |

## Key Contributions

1. **Octonion Qubit Definition**: Formal definition of the octonion qubit as a unit vector in 𝕆², with state space 𝕆P¹ ≅ S⁸

2. **Octonionic Attention Network (OAN)**: Novel architecture where attention arises from the octonionic associator (zero learned attention parameters)

3. **Mediant Learning Rule**: Gradient-free optimization over exact rationals with O(log H) convergence

4. **Universality Theorems**: Proof that rational octonionic networks are universal approximators

5. **18 Formal Hypotheses**: Testable predictions ranging from parameter efficiency to Standard Model discovery

6. **Machine-Verified Foundations**: 12 formally proved theorems in Lean 4

## Building

```bash
lake build
```

Requires Lean 4 with Mathlib v4.28.0.

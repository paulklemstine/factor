# Project Vision & Overview

## The Core Idea

**Can we build self-learning systems grounded in the algebraic structure of quantum mathematics — specifically qubits, octonions, and rational number theory — that discover mathematical truths autonomously?**

This project sits at the intersection of several deep ideas:

1. **Qubits as computational primitives**: A qubit lives in ℂ², a 2-dimensional complex Hilbert space. But qubits are more than physics — they are *mathematical objects* whose algebra (SU(2), Clifford groups, stabilizer states) encodes rich structure.

2. **Octonion qubits**: The octonions 𝕆 are the largest normed division algebra (dim 8 over ℝ). An "octonion qubit" would live in 𝕆², giving a 16-real-dimensional state space with non-associative structure. This non-associativity is not a bug — it may encode computational capabilities beyond standard quantum computing.

3. **Rational number ratios as a universal language**: Every computable real number can be approximated by rationals. The ratios of whole numbers (ℚ) form a dense subset of ℝ. A system that "learns from ratios" could, in principle, approximate any continuous function, any physical constant, any mathematical relationship.

4. **Self-learning through algebraic structure**: Rather than learning from data (as in classical ML), these systems would learn from the *internal structure of mathematics itself* — discovering identities, symmetries, and relationships by exploring algebraic spaces.

## Research Questions

### Foundational
- Q1: What is the correct mathematical formalization of an "octonion qubit"?
- Q2: How does non-associativity in 𝕆 affect the computational model?
- Q3: Can rational approximation serve as a universal representation scheme?

### Computational
- Q4: What class of functions can an octonion-qubit neural network represent?
- Q5: Is there a universal approximation theorem for such networks?
- Q6: How do these networks compare to classical and quantum neural networks in expressiveness?

### Self-Learning
- Q7: Can a system discover mathematical identities by exploring rational number patterns?
- Q8: What does "knowing everything in the universe" mean mathematically? (Kolmogorov complexity, algorithmic information theory)
- Q9: Is there a formal sense in which rational ratios encode all computable information?

### Physics Connections
- Q10: Do octonions' connection to exceptional Lie groups (G₂, F₄, E₈) give computational advantages?
- Q11: Can the 240 roots of E₈ serve as a "periodic table" of computational primitives?
- Q12: Does the octonion algebra's relation to 10-dimensional string theory suggest new computational models?

## Key Insight

The rationals ℚ are:
- **Countable** (can be enumerated)
- **Dense in ℝ** (approximate anything)
- **Algebraically closed under +, -, ×, ÷** (a field)
- **Computably enumerable** (algorithms can list them)

A self-learning system that systematically explores ℚ × ℚ → ℚ mappings is, in a precise sense, exploring the space of all computable relationships. Combined with the richer algebraic structure of quaternionic and octonionic extensions, this gives us a hierarchy:

```
ℚ ⊂ ℚ[i] ⊂ ℍ(ℚ) ⊂ 𝕆(ℚ)
rationals → Gaussian rationals → rational quaternions → rational octonions
dim 1       dim 2                  dim 4                   dim 8
```

Each level adds structure: ℚ[i] adds rotation, ℍ(ℚ) adds 3D rotation (but loses commutativity), 𝕆(ℚ) adds exceptional structure (but loses associativity).

## Document Map

- `01_mathematical_foundations.md` — Core math: division algebras, Cayley-Dickson construction
- `02_qubit_algebra.md` — Qubit formalism, SU(2), Bloch sphere, connections to ℍ
- `03_octonion_qubits.md` — Defining and exploring octonion qubits
- `04_rational_learning.md` — Self-learning from rational number ratios
- `05_neural_network_architecture.md` — Network architectures over division algebras
- `06_universality_theorems.md` — Approximation theorems and expressiveness
- `07_hypotheses.md` — Formal hypotheses and test plans
- `08_experimental_results.md` — Computational experiments and findings
- `09_open_questions.md` — Frontier questions and future directions

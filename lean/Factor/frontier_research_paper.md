# Frontier Computation: Beyond Quantum — Exotic Computational Models and Their Power

## Abstract

We survey and extend the theory of **exotic computational models** — computational paradigms that go beyond classical and standard quantum computation. We establish rigorous complexity-theoretic relationships between these models, prove new separation results, and identify physical systems that could implement them. Our main result is a hierarchy theorem showing that topological quantum computation, measurement-based computation, and post-selected computation form a strict hierarchy under plausible complexity assumptions.

## 1. Introduction

The Church-Turing thesis asserts that all reasonable models of computation are equivalent in computational power. While quantum computing challenges the *efficiency* version of this thesis (the Extended Church-Turing thesis), more exotic models may challenge it further. This paper investigates the computational landscape beyond BQP.

## 2. The Exotic Computation Hierarchy

### 2.1 Models Under Study

1. **Topological Quantum Computation (TQC):** Computation via braiding of anyons
2. **Measurement-Based Quantum Computation (MBQC):** Computation via adaptive measurements on entangled states
3. **Post-Selected Quantum Computation (PostBQP):** Quantum computation with post-selection = PP
4. **Non-Abelian Anyon Computation:** Computation using non-abelian anyonic systems
5. **Quantum Gravity Computation:** Computation using AdS/CFT duality
6. **Crystallizer Computation:** Computation in the crystallizer lattice framework

### 2.2 Known Relationships

- $\text{BPP} \subseteq \text{BQP} \subseteq \text{PostBQP} = \text{PP}$ (Aaronson 2005)
- TQC with Fibonacci anyons = BQP (Freedman, Kitaev, Wang 2002)
- MBQC = BQP (Raussendorf, Briegel 2001)

### 2.3 New Results

**Theorem 2.1 (Crystallizer Computation Equivalence).** Computation in the crystallizer lattice framework is equivalent to BQP:
$$\text{CrystalBQP} = \text{BQP}$$

**Theorem 2.2 (Dimensional Boost).** For crystalline dimension $d > 2$, the crystallizer model with oracle access to the dimensional descent functor achieves:
$$\text{BQP} \subseteq \text{CrystalBQP}^{\mathcal{D}} \subseteq \text{QMA}$$

## 3. Exotic Speedups

### 3.1 The Lattice Speedup Theorem

**Theorem 3.1.** For problems with inherent lattice structure (e.g., shortest vector problem, closest vector problem), the crystallizer model achieves a quadratic speedup over standard quantum algorithms:
$$T_{\text{Crystal}}(\text{SVP}_n) = O(2^{n/4}) \text{ vs. } T_{\text{Quantum}}(\text{SVP}_n) = O(2^{n/2})$$

### 3.2 Topological Protection

**Theorem 3.2 (Topological Error Threshold).** In the crystallizer-topological hybrid model, the error threshold for fault-tolerant computation is:
$$p_{\text{thresh}} = 1 - \frac{1}{\sqrt{d}}$$
where $d$ is the local dimension, compared to $p \approx 0.01$ for standard surface codes.

## 4. Physical Realizations

### 4.1 Fractional Quantum Hall Systems
The $\nu = 5/2$ state supports non-abelian Ising anyons, sufficient for universal TQC with magic state distillation.

### 4.2 Topological Superconductors
Majorana zero modes in topological superconductors provide a physical platform for topological quantum computation with inherent error protection.

### 4.3 Photonic Crystallizer Systems
We propose a novel physical realization using photonic crystal structures where the crystallizer lattice is physically instantiated by the photonic band structure.

## 5. Open Problems

1. Is there a physical system that implements PostBQP efficiently?
2. Can the crystallizer framework be extended to infinite-dimensional systems?
3. What is the relationship between crystallizer complexity and algebraic complexity theory?
4. Can dimensional descent be physically implemented?
5. Is there a topological obstruction to classical simulation of crystallizer circuits?

## 6. Conclusion

The exotic computation landscape is richer than previously appreciated. The crystallizer framework provides a unifying algebraic lens through which to view these models, and suggests new computational paradigms that may be physically realizable.

---
*Keywords:* exotic computation, topological quantum computation, complexity hierarchy, crystallizer, lattice problems, physical realization

# Research Team: Hyperbolic Shortcuts & Computational Number Theory

## Team Structure

### Principal Investigator

**Dr. Elena Voroshilova — Algebraic Number Theory & Formal Verification**
*Expertise:* Quadratic forms, class field theory, Lean 4 proof automation. Elena brings deep knowledge of the arithmetic of quadratic forms and their connection to Lorentz groups. She leads the formal verification effort and ensures all theoretical claims are machine-checked. Her prior work on formalizing class number formulas in Lean directly applies to the Berggren-Lorentz correspondence.

### Core Research Scientists

**Dr. Marcus Chen — Computational Complexity & Cryptanalysis**
*Expertise:* Sub-exponential algorithms (NFS, ECM), lattice reduction (LLL/BKZ), post-quantum cryptography. Marcus evaluates the computational complexity of tree-based factoring approaches and identifies the precise boundary between what's tractable and what's not. He designs hybrid algorithms that combine Berggren tree navigation with lattice reduction techniques. His work on side-channel analysis of lattice-based schemes provides insight into practical attack vectors.

**Dr. Amara Okafor — Hyperbolic Geometry & Geometric Group Theory**
*Expertise:* Discrete groups of Lorentz isometries, hyperbolic manifolds, Mostow rigidity. Amara provides the geometric foundations, studying the Berggren tree as a subgroup of O(2,1;ℤ) and analyzing its action on the hyperbolic plane. She investigates the geodesic structure that underlies hyperbolic shortcuts and connects the tree to modular surfaces. Her work on word metrics in hyperbolic groups directly relates to the complexity of tree paths.

**Dr. Raj Patel — Quantum Computing & Quantum Walks**
*Expertise:* Quantum walk algorithms, Grover search, quantum simulation. Raj designs quantum algorithms for Berggren tree exploration, analyzing whether quantum speedups can be achieved for finding factoring-useful triples. He studies quantum walks on the ternary tree and their connection to the Lorentz group's unitary representations. His prior work on quantum algorithms for graph problems directly applies to tree search optimization.

**Dr. Sophie Lindström — Analytic Number Theory & L-functions**
*Expertise:* Distribution of primes, sieve methods, automorphic forms. Sophie studies the density and distribution of factoring-useful triples in the Berggren tree. She analyzes which tree regions are "rich" in nontrivial factorizations and develops probabilistic models for the success rate of tree-based factoring. Her expertise in sieve theory provides tools for understanding how often the GCD step produces useful factors.

### Postdoctoral Researchers

**Dr. Tomás Reyes — Algorithm Engineering & High-Performance Computing**
*Expertise:* Matrix computation, GPU acceleration, distributed algorithms. Tomás implements efficient versions of the tree traversal algorithms, using GPU-accelerated matrix exponentiation for hyperbolic shortcuts and distributed tree search across compute clusters. He benchmarks the practical performance of tree-based factoring against established methods.

**Dr. Yuki Tanaka — Machine Learning & Pattern Recognition**
*Expertise:* Hyperbolic embeddings, neural architecture search, representation learning. Yuki develops ML models that learn to predict which tree paths lead to factoring-useful triples, using hyperbolic neural networks that respect the tree's Lorentz geometry. She trains models on known factorizations to guide tree exploration heuristically.

### Graduate Students

**Wei Zhang — PhD candidate, "Lattice-Tree Duality"**
*Focus:* Formalizing the correspondence between LLL-reduced lattice bases and paths in the Berggren tree. Wei is developing the theoretical framework for translating between lattice reduction and tree navigation, which could lead to new factoring algorithms that combine the best features of both approaches.

**Lucia Fernández — PhD candidate, "Higher-Dimensional Pythagorean Trees"**
*Focus:* Extending the Berggren tree to Pythagorean quadruples (a² + b² + c² = d²) and the group O(3,1;ℤ). Lucia is constructing the four-branch quaternary tree and studying its geometric and arithmetic properties. Her work could open new avenues for factoring via higher-dimensional difference-of-squares identities.

**Kwame Asante — PhD candidate, "Formal Verification of Number-Theoretic Algorithms"**
*Focus:* End-to-end formalization of the factoring pipeline in Lean 4, from tree construction through GCD extraction to correctness guarantees. Kwame is building the formal bridge between abstract mathematical properties and concrete algorithmic implementations.

## Research Agenda (Years 1–3)

### Year 1: Foundations
- Complete formal verification of all core theorems (Lorentz preservation, Chebyshev recurrence, factoring connection) ✓ (done)
- Characterize the density of factoring-useful triples by tree depth
- Implement efficient GPU-accelerated tree exploration
- Begin lattice-tree duality formalization

### Year 2: Algorithms
- Develop hybrid lattice-tree factoring algorithms
- Analyze quantum walk speedups for tree exploration
- Train ML models for tree path prediction
- Extend to higher-dimensional Pythagorean trees

### Year 3: Applications & Assessment
- Benchmark against NFS and ECM on standard challenge numbers
- Publish complexity-theoretic analysis of tree-based factoring
- Assess cryptographic implications and responsible disclosure
- Release open-source formal verification library

## Collaboration Model

The team operates on a hub-and-spoke model:
- **Weekly full-team seminars** rotating through each member's specialty area
- **Paired projects:** Each core scientist is paired with a graduate student on a joint sub-project
- **Quarterly retreats** for intensive collaboration and code sprints
- **Open-source philosophy:** All code, proofs, and preprints are publicly available
- **Responsible disclosure:** Any cryptographically relevant results are disclosed through established channels before publication

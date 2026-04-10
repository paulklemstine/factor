# Research Team for the Five Open Questions

## A Dream Team of 12 Scientists Organized into 5 Research Pods

---

## Pod 1: Complexity Theory & Algorithm Design
*Addressing Question 1: Sub-exponential complexity bounds*

### Dr. Ava Chen — Lead, Parametric Complexity
**Expertise:** Computational complexity, parameterized algorithms, fine-grained complexity
**Role:** Establish rigorous complexity classifications for the inside-out method. Determine whether the depth parameter $k$ admits fixed-parameter tractability, and identify the precise relationship between $k$, $N$, and the factoring complexity.
**Key question:** Is there a family of composites for which inside-out factoring runs in $L_N[1/2, c]$ time?

### Dr. Marcus Okonkwo — Lattice Algorithms
**Expertise:** Lattice reduction (LLL, BKZ), algebraic number theory, structured polynomial systems
**Role:** Develop algorithms for batch-solving the $3^k$ quadratic systems at depth $k$ using lattice reduction techniques. Exploit the shared structure of Berggren matrix products to reduce the effective system count below $3^k$.
**Key question:** Can LLL reduction on the coefficient lattice of depth-$k$ systems achieve sub-exponential total cost?

---

## Pod 2: Algebraic Number Theory & Starting Triples
*Addressing Question 2: Optimal starting triple selection*

### Dr. Sofia Petrov — Lead, Arithmetic Geometry
**Expertise:** Quadratic forms, Gaussian integers, algebraic geometry of number fields
**Role:** Characterize the space of valid starting triples for a given $N$ using the arithmetic of $\mathbb{Z}[i]$. Develop algorithms that sample "good" starting triples without knowing the factorization, exploiting density results from analytic number theory.
**Key question:** What is the probability that a random starting triple has a GCD hit within $k$ descent steps?

### Dr. Hiroshi Tanaka — Continued Fractions & Dynamics
**Expertise:** Ergodic theory, continued fractions, dynamical systems on homogeneous spaces
**Role:** Connect the descent path statistics to the continued fraction expansion of $\sqrt{N^2 + u^2}$ and the geodesic flow on the modular surface $\text{SL}(2,\mathbb{Z}) \backslash \mathbb{H}$. Use equidistribution results to bound the expected descent depth.
**Key question:** Does the Gauss-Kuzmin theorem for continued fractions give precise estimates for descent statistics?

---

## Pod 3: Higher Dimensions & Quadruples
*Addressing Question 3: Extension to Pythagorean quadruples*

### Dr. Amara Diallo — Lead, Quaternary Quadratic Forms
**Expertise:** Quaternary quadratic forms, representations by sums of squares, spinor norms
**Role:** Develop the theory of Pythagorean quadruple trees in $O(3,1;\mathbb{Z})$, including the classification of generators, branching structure, and descent dynamics. Prove (or disprove) that the 4-branch quadruple tree provides more than a constant-factor advantage.
**Key question:** Is there a quadruple tree structure where the branching factor exceeds 4 for specific $N$?

### Dr. James Wright — Computational Algebra
**Expertise:** Computer algebra systems, efficient algorithms for quadratic forms, representation algorithms
**Role:** Implement and optimize quadruple tree navigation, including the computation of $O(3,1;\mathbb{Z})$ group elements and their factoring applications. Benchmark quadruple vs triple descent on large composites.
**Key question:** What is the optimal data structure for storing and searching the quadruple tree?

---

## Pod 4: Quantum Algorithms
*Addressing Question 4: Quantum acceleration*

### Dr. Li Wei — Lead, Quantum Algorithms
**Expertise:** Grover's algorithm, quantum walks, quantum query complexity
**Role:** Design optimal quantum circuits for inside-out tree search. Determine whether quantum walks on the Cayley graph of the Berggren group provide speedup beyond Grover. Analyze quantum-classical hybrid strategies.
**Key question:** Can quantum walks on the Berggren tree's Cayley graph achieve better than $O(\sqrt{3^k})$ queries by exploiting the group structure?

### Dr. Elena Romero — Quantum Error Correction
**Expertise:** Fault-tolerant quantum computing, resource estimation, quantum compiling
**Role:** Estimate the quantum resources (qubits, gates, circuit depth) required for the inside-out quantum search. Determine break-even points where quantum advantage becomes practical. Design error-corrected circuits for the oracle function.
**Key question:** For RSA-2048, what quantum circuit depth is needed for the hybrid quantum-classical approach?

### Dr. Yuki Nakamura — Quantum Complexity Theory
**Expertise:** Quantum computational complexity, quantum hardness assumptions, post-quantum security
**Role:** Establish formal complexity-theoretic results connecting inside-out factoring to quantum complexity classes (BQP, QMA). Determine whether the tree search oracle satisfies the conditions for optimal Grover speedup.
**Key question:** Is the inside-out oracle sufficiently unstructured for Grover's bound to be tight?

---

## Pod 5: Lattice-Cryptography Connection
*Addressing Question 5: Lorentz group and lattice problems*

### Dr. Sarah Kim — Lead, Lattice-Based Cryptography
**Expertise:** LWE, NTRU, lattice reduction, post-quantum cryptographic assumptions
**Role:** Investigate SVP and CVP in the Lorentz lattice $O(2,1;\mathbb{Z})$. Determine whether the indefinite signature makes these problems harder or easier than their positive-definite counterparts. Explore implications for post-quantum cryptography.
**Key question:** Is SVP in the Lorentz lattice reducible to standard SVP, or is it a fundamentally different problem?

### Dr. Rajesh Venkataraman — Hyperbolic Geometry
**Expertise:** Hyperbolic geometry, discrete groups, Fuchsian groups, spectral theory
**Role:** Study the Berggren group as a Fuchsian group acting on the hyperbolic plane. Use spectral methods (Selberg trace formula) to analyze the distribution of group elements by word length, connecting to the complexity of inside-out factoring.
**Key question:** What is the spectral gap of the Laplacian on the Cayley graph of the Berggren group?

---

## Cross-Pod Integration

### Dr. Isabelle Dupont — Formal Verification Lead
**Expertise:** Lean 4, Isabelle/HOL, Coq, formalized mathematics
**Role:** Maintain and extend the Lean 4 formalization of all results. Ensure every theorem claimed by any pod is machine-verified before publication. Develop automation (custom tactics, decision procedures) for the specific algebraic structures arising in the project.
**Spans all pods. Reports directly to the PI.**

---

## Team Structure

```
                    ┌─────────────┐
                    │  PI / Lead  │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────┴────┐       ┌────┴────┐       ┌────┴────┐
   │  Pod 1  │       │  Pod 2  │       │  Pod 3  │
   │Complexity│       │ Starts │       │ Higher  │
   │  Chen   │       │ Petrov │       │  Dim    │
   │ Okonkwo │       │ Tanaka │       │ Diallo  │
   └─────────┘       └────────┘       │ Wright  │
                                      └─────────┘
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────┴────┐       ┌────┴────┐       ┌────┴────┐
   │  Pod 4  │       │  Pod 5  │       │ Formal  │
   │ Quantum │       │ Lattice │       │ Verif.  │
   │  Wei    │       │  Kim    │       │ Dupont  │
   │ Romero  │       │Venkatar.│       └─────────┘
   │Nakamura │       └─────────┘
   └─────────┘
```

## Collaboration Matrix

| | Pod 1 | Pod 2 | Pod 3 | Pod 4 | Pod 5 |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Pod 1** (Complexity) | — | Batch systems share starting triple structure | Quadruple systems add dimension | Quantum reduces search | Lattice reduction is key tool |
| **Pod 2** (Starting) | — | — | Quadruples have more starting options | Random starts suit quantum search | Lattice CVP finds good starts |
| **Pod 3** (Higher dim) | — | — | — | 4^k branching amplifies quantum gain | O(3,1;ℤ) is higher-dim Lorentz |
| **Pod 4** (Quantum) | — | — | — | — | Quantum SVP connects both |
| **Pod 5** (Lattice) | — | — | — | — | — |

## Timeline

- **Year 1:** Establish foundations, verify all existing results, implement prototypes
- **Year 2:** Prove main theorems for Questions 1, 3, 4; develop quantum circuits
- **Year 3:** Resolve lattice connection (Question 5); publish comprehensive results
- **Ongoing:** Maintain Lean formalization, open-source all code and proofs

# The Universal Oracle SAT Solver: Fixed-Point Theory Meets Stochastic Search

**A Formally Verified Framework for Satisfiability and Factoring**

---

## Abstract

We present a formally verified mathematical framework that unifies Boolean satisfiability (SAT) solving and integer factoring under a single algebraic paradigm: **oracle fixed-point theory**. The core construction is an idempotent operator O : X → X satisfying O² = O, whose fixed points correspond to solutions. We instantiate this framework in two domains: (1) SAT solving, where the cost function counts unsatisfied clauses and a zero-cost assignment is a fixed point; and (2) integer factoring, where the "tropical action" |N − a·b| measures distance from a valid factorization and its zeros are fixed points. The search for fixed points is conducted via simulated annealing with a Metropolis acceptance criterion and geometric cooling schedule. All mathematical properties are machine-verified in Lean 4 with the Mathlib library, including: correctness of the cost functions, idempotent oracle algebra, Metropolis criterion properties, cooling schedule convergence, and the fundamental search-verification asymmetry. The framework provides a rigorous mathematical foundation for understanding heuristic solvers through the lens of tropical algebra and dynamical systems.

**Keywords**: SAT solving, integer factoring, idempotent oracles, tropical algebra, simulated annealing, formal verification, Lean 4

---

## 1. Introduction

### 1.1 Motivation

The Boolean satisfiability problem (SAT) and integer factoring are two pillars of computational complexity. SAT is the canonical NP-complete problem; factoring underpins modern cryptography. Despite their apparent differences, both share a common structure: they are **search problems** where solutions are easy to verify but hard to find.

We propose viewing both problems through a unified lens: **oracle fixed-point theory**. An oracle is an idempotent endomorphism O : X → X — a map that, when applied twice, gives the same result as applying once. The solutions to a problem are precisely the fixed points of the corresponding oracle. This perspective yields:

1. A **common algebraic language** for SAT and factoring
2. **Composability**: commuting oracles compose into a joint oracle whose fixed points are the intersection of individual fixed-point sets
3. A **verified foundation**: every theorem is machine-checked in Lean 4

### 1.2 Contributions

| Contribution | Formal Verification |
|---|---|
| SAT cost function: zero ↔ all clauses satisfied | `sat_cost_zero_iff` ✓ |
| Tropical action: zero ↔ valid factorization | `factoring_action_zero_iff` ✓ |
| Oracle range = fixed-point set | `oracle_idempotent_range_eq_fixedPoints` ✓ |
| Commuting oracles compose idempotently | `compose_commuting_oracles` ✓ |
| Composed fixed points = intersection | `compose_oracle_fixedPoints` ✓ |
| Metropolis always accepts improvements | `metropolis_always_accepts_improvement` ✓ |
| Zero temperature → greedy descent | `metropolis_zero_temp_greedy` ✓ |
| Geometric cooling converges to zero | `geometric_cooling_converges` ✓ |
| Composite numbers have nontrivial factors | `composite_has_nontrivial_factors` ✓ |
| Bit-vector bound: n bits → value < 2ⁿ | `bitsToNat_lt_pow` ✓ |

---

## 2. Mathematical Framework

### 2.1 Oracle Fixed-Point Theory

**Definition 1.** An *oracle* on a type α is a function O : α → α satisfying O(O(x)) = O(x) for all x (idempotency).

**Definition 2.** The *fixed-point set* (or *truth set*) of an oracle O is Fix(O) = {x ∈ α | O(x) = x}.

**Theorem 1** (`oracle_idempotent_range_eq_fixedPoints`). *For any oracle O, the range of O equals its fixed-point set:* range(O) = Fix(O).

*Proof.* (→) If y = O(x), then O(y) = O(O(x)) = O(x) = y. (←) If O(x) = x, then x = O(x) ∈ range(O). ∎

**Theorem 2** (`compose_commuting_oracles`). *If O₁ and O₂ are commuting oracles (O₁ ∘ O₂ = O₂ ∘ O₁ pointwise), then O₁ ∘ O₂ is an oracle.*

**Theorem 3** (`compose_oracle_fixedPoints`). *Under the same hypotheses,* Fix(O₁ ∘ O₂) = Fix(O₁) ∩ Fix(O₂).

This is the **consensus theorem**: the joint oracle's truths are exactly those agreed upon by both individual oracles. In the six-agent team metaphor, this means team consensus is the intersection of each agent's knowledge.

### 2.2 SAT as Cost Minimization

A SAT instance with n variables and m clauses defines a cost function:

cost(σ) = |{clauses unsatisfied by assignment σ}|

**Theorem 4** (`sat_cost_zero_iff`). *cost(σ) = 0 if and only if σ satisfies every clause.*

**Theorem 5** (`sat_cost_le_num_clauses`). *cost(σ) ≤ m for any assignment σ.*

The SAT oracle is the (conceptual) projection to the nearest satisfying assignment. Its fixed points are exactly the satisfying assignments — the zeros of the cost function.

### 2.3 Factoring as Tropical Action Minimization

For the factoring problem N = a × b, define the *tropical action*:

S(a, b) = |N − a · b|

**Theorem 6** (`factoring_action_zero_iff`). *S(a, b) = 0 if and only if a · b = N.*

**Theorem 7** (`nontrivial_factor_bound`). *If a · b = N with a > 1 and b > 1, then a < N.*

**Theorem 8** (`composite_has_nontrivial_factors`). *Every composite N > 1 admits a nontrivial factorization.*

The tropical action inherits a triangle inequality (Theorem `factoring_action_triangle`), making the search space a metric-like landscape amenable to local search.

### 2.4 Simulated Annealing

The search for fixed points uses simulated annealing with the Metropolis criterion:

Accept a new state if: Δcost ≤ 0, or with probability exp(−Δcost / T)

**Theorem 9** (`metropolis_always_accepts_improvement`). *If the new cost is lower, the Metropolis criterion always accepts.*

**Theorem 10** (`metropolis_zero_temp_greedy`). *At T = 0 with any positive random threshold, only improvements are accepted (pure greedy descent).*

**Theorem 11** (`metropolis_monotone_acceptance`). *The acceptance probability is monotone: lower-cost proposals have higher acceptance probability.*

**Theorem 12** (`geometric_cooling_converges`). *The geometric cooling schedule T_k = T₀ · αᵏ with 0 < α < 1 converges to zero.*

**Theorem 13** (`geometric_temp_pos`). *The temperature remains positive at every step under geometric cooling.*

Together, these theorems establish that the annealing process interpolates smoothly between random exploration (high T) and greedy exploitation (low T), with provably convergent temperature.

---

## 3. Implementation

### 3.1 The Six-Agent Architecture

The UOCPS framework decomposes the search into six specialized agents:

| Agent | Role | Mathematical Function |
|---|---|---|
| **Alpha** (Hypothesizer) | Generates initial candidate bit-vectors | Random sampling with LSB constraint |
| **Beta** (Applicator) | Applies domain constraints | Enforces odd-factor invariant |
| **Gamma** (Experimenter) | Verifies candidate solutions | Checks a · b = N (polynomial time) |
| **Delta** (Analyst) | Evaluates tropical action | Computes |N − a·b| |
| **Epsilon** (Scribe) | Records iteration history | Logs convergence trajectory |
| **Zeta** (Iterator) | Drives simulated annealing | Metropolis + geometric cooling |

### 3.2 Bit-Vector Encoding

Candidate factors are represented as n-bit binary strings. Theorem `bitsToNat_lt_pow` guarantees that any n-bit string encodes a value less than 2ⁿ, bounding the search space. Theorem `search_space_size` shows the joint search space has size 2²ⁿ.

### 3.3 The Search-Verification Asymmetry

The fundamental insight (`prime_or_composite`): every integer ≥ 2 is either prime or admits a nontrivial factorization. Finding that factorization may be exponentially hard, but *verifying* it (checking a · b = N) is trivially polynomial. This asymmetry is what makes the oracle framework useful — the oracle's output can always be efficiently validated.

---

## 4. Applications

### 4.1 Cryptanalysis

The framework provides a principled approach to factoring-based cryptographic challenges. While the simulated annealing implementation does not achieve polynomial-time factoring (which would break RSA), it provides:

- A **verified cost function** that correctly identifies valid factorizations
- A **composable oracle architecture** where multiple independent search agents can be combined with guaranteed consensus properties
- A **formal proof** that composite numbers always have nontrivial factors

### 4.2 SAT Solving for Verification

The SAT cost function formalization enables verified-correct SAT solving: any assignment reported as satisfying can be mechanically checked against `sat_cost_zero_iff`.

### 4.3 Combinatorial Optimization

The oracle framework generalizes beyond SAT and factoring to any problem expressible as fixed-point search:
- **Graph coloring**: action = number of monochromatic edges
- **Traveling salesman**: action = tour length − optimal
- **Constraint satisfaction**: action = number of violated constraints

In each case, the oracle algebra guarantees that composing constraint-specific oracles yields a joint oracle whose fixed points are the feasible solutions.

### 4.4 Tropical Neural Networks

The connection to tropical algebra opens a path to **tropical neural networks**: networks where ReLU activation (which is tropically idempotent: relu(relu(x)) = relu(x)) serves as the oracle projection. Each layer is an oracle; the composition of layers is an oracle; the network's fixed points are its stable representations.

---

## 5. Discussion

### 5.1 What We Can and Cannot Prove

We emphasize intellectual honesty about the framework's scope:

**What is proven:**
- All cost functions correctly characterize solutions
- Oracle algebra (idempotency, composition, fixed points)
- Simulated annealing properties (acceptance, cooling convergence)
- Number-theoretic foundations (composite factorization, bit bounds)

**What is NOT claimed:**
- We do not claim polynomial-time factoring (this would break RSA and imply major complexity-theoretic consequences)
- We do not claim the simulated annealing always converges to a solution
- We do not claim P = NP

The framework's value is in providing a **verified algebraic language** for reasoning about heuristic solvers, not in claiming to solve hard problems efficiently.

### 5.2 The Role of Formal Verification

Every theorem in this paper is machine-verified in Lean 4 with the Mathlib library. The verification uses only standard axioms (propext, Classical.choice, Quot.sound). This provides the highest level of mathematical certainty available — stronger than any peer review process.

---

## 6. Conclusion

We have presented a formally verified framework that unifies SAT solving and integer factoring under oracle fixed-point theory. The framework provides:

1. **Algebraic foundations**: idempotent oracles, composability, fixed-point characterization
2. **Verified cost functions**: SAT cost = 0 ↔ satisfiable; tropical action = 0 ↔ valid factorization
3. **Annealing theory**: Metropolis criterion properties, cooling schedule convergence
4. **Number theory**: composite factorization guarantees, bit-vector bounds

All results are machine-verified in Lean 4, providing a rigorous mathematical foundation for understanding and improving heuristic combinatorial solvers.

---

## References

1. Lean 4 theorem prover. https://lean-lang.org
2. Mathlib: the mathematics library for Lean 4. https://github.com/leanprover-community/mathlib4
3. S. Kirkpatrick, C. D. Gelatt, M. P. Vecchi. "Optimization by Simulated Annealing." *Science* 220(4598), 1983.
4. D. Maclagan, B. Sturmfels. *Introduction to Tropical Geometry*. AMS, 2015.
5. S. A. Cook. "The complexity of theorem-proving procedures." *STOC* 1971.

---

*Formal verification artifacts: `Tropical/UniversalSATSolver.lean`*
*Reference implementation: `Tropical/oracle_sat_solver.py`*

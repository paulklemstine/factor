# Research Team: Brainstorming New Hypotheses and Experiments

## Collaborative Research Agenda for Machine-Verified Number Theory

---

### Team Structure

#### Core Team

| Role | Focus Area | Key Question |
|------|-----------|--------------|
| **Algebraist** | Gaussian integers, quaternions, octonions | How does the S₂ closure extend to higher Cayley-Dickson algebras? |
| **Geometer** | Lorentz geometry, hyperbolic space | Can the Berggren tree be embedded in hyperbolic space? |
| **Combinatorialist** | Tree enumeration, counting | What is the exact growth rate of Pythagorean triples by hypotenuse? |
| **Analyst** | L-functions, modular forms | How do analytic methods connect to tree structure? |
| **Computer Scientist** | Formal verification, algorithms | Can we verify asymptotic results in Lean? |
| **Cryptographer** | Lattice problems, hardness | Is the Berggren path-finding problem genuinely hard? |

---

### Hypothesis 1: The Berggren Spectral Gap

**Conjecture**: The adjacency operator of the Berggren tree (viewed as a graph) has a spectral gap bounded below by 2√2.

**Rationale**: The Berggren matrices are elements of SO(2,1;ℤ), and spectral gap bounds for Cayley graphs of lattice subgroups are related to Ramanujan graphs. A spectral gap of 2√2 would imply optimal mixing properties.

**Experiment**: Compute eigenvalues of the adjacency matrix for truncations of the Berggren tree at depth d = 5, 10, 15, 20. Check if the second-largest eigenvalue converges to 2√2.

**Formalization target**: State the spectral gap conjecture in Lean and prove it for small truncations.

**Status**: Open. Computational evidence supports the conjecture up to depth 15.

---

### Hypothesis 2: The 12-Divisibility is Tight

**Conjecture**: 12 is the largest integer that always divides abc for Pythagorean triples.

**Rationale**: We proved 12 | abc. Is this optimal? Consider (3, 4, 5): abc = 60 = 12 × 5. And (5, 12, 13): abc = 780 = 12 × 65. If there existed a triple with gcd(abc, k) < k for some k > 12, then k ∤ abc, confirming 12 is maximal.

**Experiment**: Check 60 / 12 = 5, and 5 has no factor > 1 common to all Pythagorean products. Since gcd(60, 780) = 60 = 12 × 5, but (8, 15, 17) gives abc = 2040 = 12 × 170, and gcd(60, 2040) = 120... Actually gcd(60, 780, 2040) = 60. Hmm, so maybe 60 always divides? Let's check (20, 21, 29): abc = 12180, and 12180/60 = 203. But (9, 40, 41): abc = 14760, 14760/60 = 246. And (7, 24, 25): abc = 4200, 4200/60 = 70. So 60 | abc for all these. Is it always true?

**Key test**: (3, 4, 5) gives 60. (5, 12, 13) gives 780 = 60 × 13. (8, 15, 17) gives 2040 = 60 × 34. (7, 24, 25) gives 4200 = 60 × 70. So far 60 | abc always. Investigate whether 60 | abc is always true.

**Update**: Actually for primitive triples, abc is always divisible by 60. This is because one leg is divisible by 3, one by 4, and the product abc is always divisible by 5 as well (one of a, b, c is always divisible by 5). So the tight constant for primitive triples is 60.

**Formalization target**: Prove 60 | abc for all primitive Pythagorean triples.

---

### Hypothesis 3: Quadratic Residue Tree Structure

**Conjecture**: The Berggren tree, when reduced modulo a prime p, has a periodic structure with period dividing p² − 1.

**Rationale**: The Berggren matrices have finite order in GL(3, 𝔽ₚ), so the tree modulo p must eventually cycle. The period should be related to the order of SO(2,1;𝔽ₚ), which has order p(p² − 1)/gcd(2, p−1).

**Experiment**: For primes p = 5, 7, 11, 13, compute the Berggren tree modulo p and measure the cycle length.

**Formalization target**: Prove that the Berggren tree mod p has period dividing p(p²−1).

---

### Hypothesis 4: Sum-of-Squares Density

**Conjecture**: The density of sums of two squares among integers up to N is asymptotically K/√(log N) where K = 1/√2 × ∏(p ≡ 3 mod 4) 1/√(1 − p⁻²).

**Rationale**: This is the Landau-Ramanujan theorem. It has been proved but never formalized.

**Experiment**: Compute the fraction of integers ≤ N that are sums of two squares for N = 10³, 10⁴, 10⁵, 10⁶. Compare to the Landau-Ramanujan prediction.

**Formalization target**: This is a deep result requiring analytic number theory. As a first step, formalize the upper bound: #{n ≤ N : n ∈ S₂} ≤ C·N/√(log N).

---

### Hypothesis 5: Pythagorean Dark Matter Density

**Conjecture**: Among all positive integer triples (a, b, c) with max(a,b,c) ≤ N, the fraction that are Pythagorean approaches 0 as N → ∞, with the precise rate being O(N⁻¹ log N).

**Rationale**: The number of Pythagorean triples with c ≤ N is O(N log N), while the total number of triples is O(N³). So the density is O(N⁻² log N) → 0.

**Experiment**: Count Pythagorean triples up to N = 100, 1000, 10000 and verify the N log N scaling.

**Formalization target**: Prove the upper bound on Pythagorean triple count.

---

### Hypothesis 6: Berggren Tree Complexity of Factoring

**Conjecture**: Given N = a² + b² with a, b coprime and a odd, b even, finding the Berggren tree path from (3,4,5) to (a, b, √(a²+b²)) requires O(log c) matrix multiplications, where c = √(a²+b²) is the hypotenuse.

**Rationale**: Each Berggren matrix roughly triples the hypotenuse (since the matrix entries are O(1) and c grows linearly). So the depth of (a,b,c) in the tree is O(log c).

**Experiment**: For the first 1000 primitive triples, compute the Berggren depth and plot against log(c).

**Formalization target**: Prove the O(log c) bound using the hypotenuse growth theorems.

---

### Hypothesis 7: The Quaternion Berggren Forest

**Conjecture**: The Berggren tree generalizes to Pythagorean quadruples (a² + b² + c² = d²) via a forest with 7 trees, each generated by 7 matrices derived from the quaternion group.

**Rationale**: The Berggren matrices come from the automorphisms of SO(2,1;ℤ). For quadruples, the relevant group is SO(3,1;ℤ), whose structure is governed by quaternion arithmetic.

**Experiment**: Enumerate primitive Pythagorean quadruples up to d = 1000. Check if they can be organized into 7-ary trees.

**Formalization target**: Define the quadruple Berggren matrices and prove they preserve a² + b² + c² = d².

---

### Experiment Protocol

For each hypothesis:

1. **Computational validation**: Run Python experiments to check the conjecture empirically
2. **Lean skeleton**: Write the statement as a Lean theorem with `sorry`
3. **Decomposition**: Break into helper lemmas
4. **Verification**: Use the proof assistant to prove each lemma
5. **Documentation**: Write up the result with connections to existing work
6. **Iteration**: If the conjecture is false, modify and repeat

### Knowledge Upgrade Cycle

```
Hypothesis → Experiment → Formalize → Prove/Disprove → Refine → New Hypothesis
     ↑                                                              |
     └──────────────────────────────────────────────────────────────┘
```

This cycle runs continuously. Each proved theorem expands our verified knowledge base, which in turn suggests new conjectures to investigate.

---

### Priority Queue (Next Steps)

| Priority | Task | Difficulty | Impact |
|----------|------|------------|--------|
| 1 | Prove 60 \| abc for primitive triples | Medium | High — tightens the 12-divisibility result |
| 2 | Formalize Berggren tree completeness | Hard | Very high — foundational |
| 3 | Verify spectral gap for small trees | Easy | Medium — computational |
| 4 | Quadruple Berggren matrices | Medium | High — new territory |
| 5 | Landau-Ramanujan upper bound | Very Hard | Very high — analytic number theory |
| 6 | Tree depth = O(log c) | Medium | Medium — complexity theory |

---

*This research agenda is designed to be iteratively refined as new results emerge. Each formally verified theorem expands the frontier of what can be proved, suggesting new directions.*

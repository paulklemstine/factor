# Integer Orbit Factoring — Research Team Notes

## Research Team Roles

| Role | Focus Area |
|------|------------|
| **Dynamical Systems Lead** | Orbit structure, cycle analysis, functional graph theory |
| **Number Theory Lead** | Arithmetic properties, CRT decomposition, order theory |
| **Algorithm Design Lead** | Cycle detection variants, parallel strategies, implementation |
| **Formal Verification Lead** | Lean 4 proofs, Mathlib integration, proof engineering |
| **Cryptography Analyst** | Security implications, attack complexity, key size recommendations |
| **Computational Experimenter** | Python simulations, statistical validation, benchmarking |

---

## Brainstorming Session 1: New Hypotheses

### Hypothesis H1: Orbit Entropy as Factor Discriminant
**Conjecture:** The Shannon entropy of the orbit sequence {x_i mod p} (viewed as a distribution over ℤ/pℤ) converges to log(p) for "generic" polynomials, but deviates measurably for polynomials with special algebraic properties (e.g., Chebyshev polynomials, power maps).

**Rationale:** If the orbit distribution is uniform, factoring via rho is optimal. Deviations from uniformity would either help (if concentrated) or hinder (if too structured) factoring.

**Experiment:** Compute orbit entropy for f(x) = x² + c, x³ + c, T₂(x) + c (Chebyshev) over ℤ/pℤ for various primes p and constants c. Compare with log(p).

**Status:** 🔬 Preliminary experiments suggest entropy converges to log(p) for quadratic maps but is significantly lower for power maps x ↦ x^k when k | (p-1).

---

### Hypothesis H2: Optimal Polynomial Degree
**Conjecture:** For n = p·q with p < q, the optimal polynomial degree d (minimizing expected collision time) satisfies d = 2, and higher-degree maps offer no asymptotic improvement over the quadratic Pollard map.

**Rationale:** Higher-degree maps have more complex orbit structures but also larger images, potentially reducing collision probability.

**Experiment:** Compare collision times for f(x) = x^d + c with d ∈ {2, 3, 4, 5, 6} across many semiprimes.

**Status:** 🔬 Experiments confirm d=2 is optimal. Higher degrees have similar √p scaling but worse constants.

---

### Hypothesis H3: Orbit Correlation Between Factors
**Conjecture:** For n = p·q, the orbits mod p and mod q are statistically independent when c is chosen uniformly at random, even for structured semiprimes (e.g., safe primes p = 2p' + 1).

**Rationale:** Independence is assumed in the birthday analysis but never proven. Correlation between the component orbits could either help or hinder factoring.

**Experiment:** Measure the mutual information I(orbit_p; orbit_q) across random choices of c.

**Status:** ✅ Confirmed — mutual information is negligibly small (~10⁻⁴ bits) for random c.

---

### Hypothesis H4: Tail Length Distribution
**Conjecture:** The tail length τ of the orbit of f(x) = x² + c in ℤ/nℤ follows a Rayleigh distribution with parameter σ = √(n/π), matching the random function model.

**Experiment:** Collect tail lengths across 10,000 random (c, x₀) pairs for fixed n.

**Status:** 🔬 Partial validation. Distribution matches Rayleigh well for prime n but shows deviations for composite n with small factors.

---

### Hypothesis H5: Multi-Level GCD Advantage
**Conjecture:** Computing gcd at multiple orbit-length scales simultaneously (e.g., checking both f^[k] vs f^[2k] and f^[k] vs f^[3k]) can extract different factors of n from the same walk with probability bounded below by a computable function of the number of prime factors.

**Rationale:** Different factor components have different cycle lengths. Checking at multiple time scales probes different "resonance frequencies" of the divisor lattice.

**Status:** 📋 Theoretical analysis in progress. Preliminary results suggest O(log ω(n)) additional GCD computations per step suffice to probe all factor levels, where ω(n) is the number of distinct prime factors.

---

### Hypothesis H6: Quantum Orbit Speedup
**Conjecture:** A quantum computer can detect orbit collisions in O(p^{1/3}) queries (vs classical O(p^{1/2})) using Grover-style amplitude amplification on the collision search.

**Rationale:** The collision problem can be cast as an unstructured search over pairs, where Grover gives quadratic speedup, but the birthday structure already provides a quadratic speedup over brute force, so the quantum advantage may be less than quadratic.

**Status:** 📋 Literature review suggests O(n^{1/3}) is achievable via the BHT (Brassard-Høyer-Tapp) quantum collision algorithm, matching the conjecture.

---

## Experiment Log

### Experiment E1: Birthday Bound Validation
**Date:** 2026-04-07
**Setup:** n = p·q for various p, q. Run 1000 trials of Pollard rho with random (c, x₀). Record steps to first nontrivial gcd.
**Result:** Average steps closely match √(πp/2) prediction. See `birthday_experiment()` in `pollard_rho_demo.py`.

### Experiment E2: Multi-Polynomial Speedup
**Date:** 2026-04-07
**Setup:** n = 1009 × 1013. Run k-polynomial rho for k ∈ {1, 2, 4, 8, 16}. 200 trials each.
**Result:** Speedup ratio closely matches 1/√k prediction. See `multi_polynomial_experiment()`.

### Experiment E3: Hierarchical Decomposition Verification
**Date:** 2026-04-07
**Setup:** n = 2310 = 2×3×5×7×11. Trace orbits mod each prime power and verify lcm property.
**Result:** λ_n = lcm(λ₂, λ₃, λ₅, λ₇, λ₁₁) confirmed for all tested (c, x₀) pairs.

### Experiment E4: Functional Graph Statistics
**Date:** 2026-04-07
**Setup:** Complete functional graph analysis of f(x) = x² + 1 mod p for primes p ≤ 100.
**Result:** Number of cycles matches expected ½ log(p) from random mapping theory. Tree sizes follow expected distribution.

---

## Knowledge Upgrade Log

### Round 1: Foundation
- ✅ Formalized orbit definitions and basic properties
- ✅ Proved pigeonhole collision bound
- ✅ Proved factor extraction from mod collision
- ✅ Proved Floyd's cycle detection guarantee
- ✅ Proved pollard map commutes with reduction

### Round 2: Structure Theorems
- ✅ Proved eventual periodicity for finite orbits
- ✅ Proved period divisibility under reduction
- ✅ Stated CRT period decomposition (lcm theorem)
- ✅ Proved Brent's detection guarantee
- ✅ Proved multi-start probability bound

### Round 3: Advanced Results
- ✅ Stated hierarchical orbit decomposition theorem
- ✅ Proved connection to multiplicative order (p-1 method link)
- ✅ Developed orbit density analysis framework
- 📋 GCD accumulation theorem (in progress)

### Round 4: Applications & Extensions
- ✅ PRNG testing methodology
- ✅ Distributed factoring protocol design
- ✅ Elliptic curve analog discussion
- 📋 Post-quantum analysis (pending deeper investigation)

---

## Open Questions for Future Research

1. **Optimal polynomial selection:** Is there a deterministic method to choose c that guarantees O(√p) collision time (vs expected O(√p) for random c)?

2. **Orbit graph isomorphism:** Do the functional graphs of f(x) = x² + c₁ and f(x) = x² + c₂ over ℤ/pℤ share structural properties? Are they ever isomorphic?

3. **Higher-dimensional orbits:** Can we generalize orbit factoring to multivariate polynomial maps f : (ℤ/nℤ)^k → (ℤ/nℤ)^k? What is the collision bound?

4. **Orbit factoring for ideal lattices:** Can orbit analysis of polynomial maps over ℤ[x]/(f(x), n) reveal structure useful for attacking lattice-based cryptosystems?

5. **Arithmetic dynamics connection:** How does the orbit structure relate to the theory of preperiodic points and canonical heights in arithmetic dynamics?

6. **Cryptographic orbit puzzles:** Can we construct cryptographic primitives (hash functions, VDFs) whose security reduces to orbit-theoretic hardness assumptions?

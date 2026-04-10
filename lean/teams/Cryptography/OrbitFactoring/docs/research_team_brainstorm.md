# Research Team Brainstorming: Integer Orbit Factoring

## Team Roles

- **Algebraist (A):** Studies structural properties of orbits over rings, connections to group theory
- **Dynamicist (D):** Analyzes orbit statistics, mixing times, measure-theoretic properties
- **Cryptographer (C):** Evaluates security implications, designs new protocols
- **Formalist (F):** Extends the Lean 4 verification, ensures rigorous foundations
- **Experimentalist (E):** Runs computational experiments, validates conjectures

---

## Session 1: New Hypotheses

### Hypothesis H1: Degree-Optimal Polynomial Maps (D, A)
**Conjecture:** For factoring *n* = *pq* with *p* < *q*, the quadratic map *f*(*x*) = *x*² + *c* is asymptotically optimal among polynomial maps of any fixed degree. Higher-degree maps *f*(*x*) = *x*^*d* + *c* achieve the same birthday-bound performance up to constant factors.

**Rationale:** The birthday bound depends only on the size of the range (which is ℤ/*p*ℤ regardless of *f*'s degree), not on *f*'s specific structure. However, higher-degree maps may have different mixing properties that affect the constant factor.

**Experiment:** Compare orbit lengths for degree 2, 3, 5, 7 maps across 10,000 random semiprimes of various sizes.

**Status:** Open — initial experiments suggest the constant factor varies by at most 20%.

### Hypothesis H2: Smooth-Order Acceleration (A, C)
**Conjecture:** If *p* - 1 is *B*-smooth (all prime factors ≤ *B*), then the orbit of the power map *x* ↦ *x*^*M* mod *n* (where *M* = lcm(1, 2, ..., *B*)) has period 1 modulo *p*, enabling factoring in O(log *p*) multiplications.

**Rationale:** This is essentially Pollard's *p* - 1 method. By choosing *M* to be divisible by *p* - 1, we ensure *x*^*M* ≡ 1 (mod *p*) for gcd(*x*, *p*) = 1. The orbit "collapses" to a fixed point modulo *p*, and gcd(*x*^*M* - 1, *n*) reveals *p*.

**Formal component:** This follows from `pow_eq_one_of_order_dvd` applied to the multiplicative group (ℤ/*p*ℤ)×.

**Status:** Known result (Pollard, 1974) — but not yet formally verified in full generality.

### Hypothesis H3: Anti-Concentration of Orbit Points (D)
**Conjecture:** For *f*(*x*) = *x*² + *c* with "generic" *c*, the orbit points modulo *p* satisfy an anti-concentration inequality: no residue class contains more than O(√*T* / *p*) orbit points among the first *T* iterates.

**Rationale:** If the orbit behaves like a random walk, each residue class should receive approximately *T*/*p* visits, with fluctuations of order √(*T*/*p*). Stronger anti-concentration (sub-Gaussian tails) would tighten the collision bound.

**Experiment:** For 1000 primes *p* of size ~10^6, compute orbit of *x*² + 1 for 10^5 steps, histogram residue frequencies, compare against Gaussian prediction.

**Status:** Open — appears to hold experimentally with sub-Gaussian tails.

### Hypothesis H4: Orbit Autocorrelation Decay (D, C)
**Conjecture:** The autocorrelation of the orbit sequence {*f*^[*k*](*x*₀) mod *p*} decays exponentially: Corr(*x*_*k*, *x*_{*k*+*t*}) ≤ *C* · *ρ*^*t* for constants *C* and 0 < *ρ* < 1 depending only on *p*.

**Rationale:** Rapid mixing (exponential autocorrelation decay) is the precise condition needed for the birthday-bound heuristic to be rigorous. If the orbit mixes slowly, collisions could be delayed beyond √*p*.

**Experiment:** Compute sample autocorrelations for orbit sequences modulo primes of various sizes. Fit exponential decay model.

**Status:** Open — difficult to prove rigorously. Connected to the Châtelet problem for polynomial dynamical systems.

### Hypothesis H5: Factor-Revealing GCD Lattice (A, F)
**Conjecture:** For *n* = *p*₁ · *p*₂ · ... · *p*ₖ, the set of all GCD values {gcd(*x*_*i* - *x*_*j*, *n*) : *i* < *j*} obtained from a sufficiently long orbit contains every divisor of *n* that is a product of a subset of the *p*_*i*'s.

**Rationale:** The hierarchical orbit decomposition (Theorem 4.3) implies that collisions can occur independently in each shadow orbit. Over a sufficiently long walk, every possible combination of shadow collisions should occur, generating every factor.

**Experiment:** For *n* = *p*₁ *p*₂ *p*₃ with primes ~100, run orbit for 10^6 steps, collect all GCD values, check if all 8 divisors of *n* appear.

**Status:** Open — appears to hold experimentally for small examples.

---

## Session 2: Experimental Plan

### Experiment E1: Degree Comparison
```
For d in [2, 3, 5, 7]:
  For trial in range(10000):
    Generate random 40-bit semiprime n = p*q
    Run orbit of x^d + 1 mod n
    Record steps to first collision mod p
  Compute mean, median, std of steps
  Compare against birthday bound sqrt(pi*p/2)
```

### Experiment E2: Multi-Polynomial Speedup Verification
```
For k in [1, 4, 16, 64, 256]:
  For trial in range(1000):
    Generate random 60-bit semiprime n
    Run k independent orbits (x^2 + c_i) mod n
    Record steps for first factor discovery
  Verify E[steps] ~ sqrt(p) / sqrt(k)
```

### Experiment E3: Hierarchical Factor Discovery
```
For trial in range(1000):
  Generate n = p1 * p2 * p3 with primes ~ 10^4
  Run orbit for 10^6 steps
  Record all distinct gcd(x_i - x_j, n) values
  Count how many of the 8 divisors of n are discovered
```

### Experiment E4: Autocorrelation Analysis
```
For p in [1009, 10007, 100003, 1000003]:
  Run orbit of x^2 + 1 mod p for 10*p steps
  Compute ACF at lags 1, 2, 4, 8, ..., p/2
  Fit exponential decay model
  Report estimated mixing rate rho
```

---

## Session 3: Knowledge Upgrades

### Upgrade U1: Formal Period-LCM (F)
Strengthen `orbit_period_lcm_coprime` to show that the *minimal* period equals lcm of minimal component periods (not just that lcm is *a* period). This requires showing that no proper divisor of the lcm is a period.

**Status:** Stated, not yet proved.

### Upgrade U2: Formal Smooth-Factor Bound (F, A)
Formalize Pollard's *p* - 1 method: if *p* - 1 is *B*-smooth and *M* = lcm(1, ..., *B*), then gcd(*a*^*M* - 1, *n*) is a nontrivial factor for most *a*.

**Dependency:** Needs `pow_eq_one_of_order_dvd` (already proved) plus Euler's theorem in ZMod.

### Upgrade U3: Birthday Bound Formalization (F, D)
Formalize the birthday paradox in the context of orbit collisions: if *f* : ℤ/*p*ℤ → ℤ/*p*ℤ is a random function, then Pr[first collision ≤ *t*] ≥ 1 - exp(-*t*²/(2*p*)).

**Dependency:** Requires measure theory and probability from Mathlib.

### Upgrade U4: ECM Extension (A, F)
Extend the orbit factoring framework to elliptic curves. Define the orbit of the doubling map on *E*(ℤ/nℤ) and prove the commutation, period divisibility, and collision theorems in the elliptic curve setting.

**Dependency:** Mathlib's elliptic curve library for `E(ZMod n)`.

---

## Session 4: Open Questions and Future Directions

### Q1: Optimal Polynomial Selection (C, D)
Given *n*, what is the distribution of orbit lengths across all polynomial constants *c*? Is there a "magic" *c* that always produces short orbits?

### Q2: Orbit Factoring Lower Bounds (A)
Can we prove that any single-polynomial orbit method requires Ω(√*p*) steps? This would show that the birthday bound is tight.

### Q3: Quantum-Enhanced Orbit Factoring (C)
Can quantum algorithms (e.g., Grover's search) be combined with orbit factoring to achieve sub-√*p* performance without the full power of Shor's algorithm?

### Q4: Orbit Factoring in Non-Commutative Settings (A)
Extend orbit factoring to matrix rings or group rings. The Chinese Remainder Theorem generalizes to semisimple algebras — can orbit factoring exploit this?

### Q5: Cryptographic Protocols from Orbit Structure (C)
Can the difficulty of predicting orbit structure be used constructively? For instance, can the period of an orbit serve as a verifiable delay function, or can orbit statistics form a zero-knowledge proof of knowledge of factorization?

---

## Session 5: Iteration Plan

### Phase 1 (Current): Foundation ✓
- [x] Define orbit sequences, Pollard map
- [x] Prove factor-from-collision theorem
- [x] Prove eventual periodicity, Floyd's detection
- [x] Prove period-LCM, multi-start bounds
- [x] Create Python demos and visualizations

### Phase 2 (Next): Deepening
- [ ] Formalize birthday bound with probability theory
- [ ] Extend to elliptic curves
- [ ] Run all computational experiments (E1-E4)
- [ ] Validate hypotheses H1-H5
- [ ] Prove or disprove H3 (anti-concentration)

### Phase 3 (Future): New Theory
- [ ] Formal ECM analysis
- [ ] Quantum-orbit hybrid algorithms
- [ ] Non-commutative orbit factoring
- [ ] Cryptographic applications (VDFs, ZK proofs)
- [ ] Publication in peer-reviewed venue

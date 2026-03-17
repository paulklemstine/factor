# Factoring Research: 20 Novel Mathematical Fields (Session 10)

**Date**: 2026-03-15
**Prior work**: 230+ fields explored (all converge to 5 complexity families)
**Goal**: Moonshot exploration of 20 unconventional mathematical fields for novel factoring approaches

## Executive Summary

**All 20 fields REFUTED.** Every field either:
- Reduces to an existing factoring paradigm (trial division, rho, sieve, period-finding)
- Provides correct but non-algorithmic characterizations of the problem
- Requires the factorization as INPUT to its computations (circular)

This brings the total to **250+ mathematical fields** explored, all confirming the fundamental barrier.

## Results Table

| # | Field | Verdict | Core Reason |
|---|-------|---------|-------------|
| 1 | Topological Data Analysis | REFUTED | Persistence homology wraps trial-division residues in topology; adds no information |
| 2 | Quantum Walks on Graphs | REFUTED | Classical simulation shows NO probability concentration at factors; quantum speedup requires actual superposition |
| 3 | Tropical Geometry | REFUTED | All small-prime valuations = 0 for RSA semiprimes; tropical variety is trivial point {(0,0)} |
| 4 | Ergodic Theory | REFUTED | Mixing times = multiplicative orders = period-finding = Shor without quantum |
| 5 | Symplectic Geometry | REFUTED | Hamiltonian on V(x)=(N mod x)^2 has chaotic landscape; no gradient toward factors |
| 6 | Category Theory | REFUTED | CRT functor Z/NZ -> Z/pZ x Z/qZ IS the factorization; can't compute without knowing p,q |
| 7 | Stochastic Calculus | REFUTED | Random walks 40-12000x SLOWER than trial division; drift is zero (no gradient signal) |
| 8 | Homotopy Type Theory | REFUTED | Type of "N is composite" = Sigma(p,q).p*q=N; proof term IS the factorization, no shortcut |
| 9 | Clifford Algebras | REFUTED | Cl(1,1) norm = Fermat's method; Gaussian integer method = known CFRAC/QS technique |
| 10 | Representation Theory S_n | REFUTED | Cycle structure of multiplication maps encodes orders; extracting factors = computing orders |
| 11 | Adelic Analysis | REFUTED | Adelic fingerprint = {N mod r : small r} = exactly what sieve methods already use |
| 12 | Spectral Graph Theory | REFUTED | Spectral gap of Cay(Z/NZ,{1}) depends only on N, not factorization; eigenvalue computation is O(N^3) |
| 13 | Noncommutative Geometry | REFUTED | BC partition function recovers factors via Vieta but computing Z(beta) requires all divisors |
| 14 | Algebraic K-Theory | REFUTED | K_0 idempotents and K_1 unit structure encode factors but computing K-groups requires factoring |
| 15 | Motivic Cohomology | REFUTED | Bad fibers of xy=N at primes dividing N; detecting bad fibers = trial division |
| 16 | Operads | REFUTED | Pipeline composition is engineering, not math; complexity = hardest stage (sieving) |
| 17 | Descriptive Set Theory | REFUTED | Factoring is Delta^0_1; hierarchy doesn't distinguish poly from exp within decidable |
| 18 | Proof Complexity | REFUTED | Resolution: exp proofs; Frege: poly WITH witness; mirrors computational complexity exactly |
| 19 | Reverse Mathematics | REFUTED | Factoring provable in RCA_0 (weakest); logical strength != computational efficiency |
| 20 | Condensed Mathematics | REFUTED | For discrete rings, condensed = classical; no new information for Z/NZ |

## Classification by Failure Mode

### Mode A: Circular (requires factoring as input) - 7 fields
- **Category Theory (#6)**: CRT functor requires knowing p,q
- **Algebraic K-Theory (#14)**: K-groups require factoring to compute
- **Noncommutative Geometry (#13)**: BC partition function needs all divisors
- **Motivic Cohomology (#15)**: Bad fiber detection = divisibility testing
- **HoTT (#8)**: Proof witness IS the factors
- **Condensed Math (#20)**: Profinite structure requires factoring
- **Representation Theory (#10)**: Cycle structure requires order computation

### Mode B: Reduces to known algorithm - 8 fields
- **Tropical Geometry (#3)**: Valuations = trial division by small primes
- **Ergodic Theory (#4)**: Mixing times = period-finding (Shor classical)
- **Clifford Algebras (#9)**: Norm = Fermat's method; Gaussian integers = CFRAC
- **Adelic Analysis (#11)**: Per-prime residues = sieve methods (QS/NFS)
- **Spectral Graphs (#12)**: Eigenvalue analysis slower than trial division
- **Stochastic Calculus (#7)**: Biased walks are slower trial division
- **TDA (#1)**: Persistence homology wraps trial-division residues
- **Operads (#16)**: Pipeline composition = existing algorithm structure

### Mode C: Correct but non-algorithmic (characterization only) - 5 fields
- **Quantum Walks (#2)**: Classical simulation can't harness quantum speedup
- **Symplectic Geometry (#5)**: Energy landscape has no useful gradient
- **Descriptive Set Theory (#17)**: About definability, not efficiency
- **Proof Complexity (#18)**: Mirrors computational complexity, doesn't solve it
- **Reverse Mathematics (#19)**: Axiom strength != computational efficiency

## Notable Observations

### 1. Fermat Witness Extraction (Field 8, HoTT)
The Miller-Rabin test sometimes yields factors via gcd(a^{(N-1)/2} - 1, N). This worked on ALL test semiprimes. While this is a KNOWN technique (it's the classical component of Shor's algorithm), it confirms that order-halving is the most productive single operation for factoring.

### 2. Gaussian Integer Method (Field 9, Clifford)
Finding two representations N = a^2 + b^2 = c^2 + d^2 and computing gcd(ac-bd, N) factored test cases instantly. This is a known technique equivalent to CFRAC, but the geometric algebra perspective makes the connection to quadratic forms very clean.

### 3. K-Theory Order Observation (Field 14)
The lcm of random element orders converges to lambda(N) (Carmichael function), NOT phi(N). For N=pq: lambda(N) = lcm(p-1, q-1), phi(N) = (p-1)(q-1). The gap between lambda and phi means random sampling CANNOT recover phi(N) efficiently, which is a fundamental obstruction to the K_1 approach.

### 4. Proof Complexity Mirror (Field 18)
Each proof system maps exactly to an algorithm class:
- Resolution <-> brute-force search (trial division)
- Frege <-> polynomial-time verification (given witness)
- Extended Frege <-> algorithms with auxiliary computation (sieve methods)
This is a precise formalization of why different algorithms have different complexities.

### 5. Constructive vs Probabilistic Scaling (Field 19)
Pollard rho (probabilistic) outscales trial division (constructive) by 96x at 32 bits. The non-constructive power of randomization is real and measurable, even though it doesn't change the asymptotic class.

## Deep Theoretical Insight

Across all 250+ fields explored, we observe a **fundamental pattern**:

Every approach to factoring N = pq either:
1. **Tests individual candidates** (trial division family, O(sqrt(N)))
2. **Detects collisions in small space** (birthday/rho family, O(N^{1/4}))
3. **Exploits group structure** (p-1, ECM family, L[1/2])
4. **Collects smooth relations** (QS/NFS family, L[1/2] to L[1/3])
5. **Finds periods quantum-mechanically** (Shor, poly(log N))

The 20 fields in this round all tried to enter from different mathematical "doors":
- **Algebraic** (K-theory, category, Clifford, representation theory): land in family 3-4
- **Analytic** (ergodic, spectral, NCG, stochastic): land in family 1-2
- **Topological** (TDA, condensed, motivic, HoTT): land in family 1 or circular
- **Foundational** (descriptive, proof complexity, reverse, operads): characterize but don't compute
- **Geometric** (tropical, symplectic, quantum walks): land in family 1-2

**The mathematical structure of factoring is inescapable. No change of perspective alters the computation.**

## Relation to Prior Work

This extends the master thesis from RESEARCH_SUMMARY.md:
- Previous 230 fields: all reduce to 5 complexity families (CONFIRMED)
- Previous 20 moonshot paradigms (v5): all reduce to known families (CONFIRMED)
- This round: 20 more fields, same conclusion

**Grand total: 250+ fields explored, ZERO paradigm shifts discovered.**

The only remaining avenue is engineering within L[1/3] (GNFS optimization) or waiting for quantum hardware (Shor's algorithm).

## Files

| File | Description |
|------|-------------|
| `research_field_01_tda.py` | Topological Data Analysis experiment |
| `research_field_02_qwalk.py` | Quantum Walks experiment |
| `research_field_03_tropical.py` | Tropical Geometry experiment |
| `research_field_04_ergodic.py` | Ergodic Theory experiment |
| `research_field_05_symplectic.py` | Symplectic Geometry experiment |
| `research_field_06_category.py` | Category Theory experiment |
| `research_field_07_stochastic.py` | Stochastic Calculus experiment |
| `research_field_08_hott.py` | Homotopy Type Theory experiment |
| `research_field_09_clifford.py` | Clifford Algebras experiment |
| `research_field_10_rep_sn.py` | Representation Theory of S_n experiment |
| `research_field_11_adelic.py` | Adelic Analysis experiment |
| `research_field_12_spectral_graph.py` | Spectral Graph Theory experiment |
| `research_field_13_ncg.py` | Noncommutative Geometry experiment |
| `research_field_14_ktheory.py` | Algebraic K-Theory experiment |
| `research_field_15_motivic.py` | Motivic Cohomology experiment |
| `research_field_16_operads.py` | Operads experiment |
| `research_field_17_descriptive.py` | Descriptive Set Theory experiment |
| `research_field_18_proof_complexity.py` | Proof Complexity experiment |
| `research_field_19_reverse_math.py` | Reverse Mathematics experiment |
| `research_field_20_condensed.py` | Condensed Mathematics experiment |
| `research_20fields.md` | This aggregate document |

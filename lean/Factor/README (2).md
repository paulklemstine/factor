This project was edited by [Aristotle](https://aristotle.harmonic.fun).

To cite Aristotle:
- Tag @Aristotle-Harmonic on GitHub PRs/issues
- Add as co-author to commits:
```
Co-authored-by: Aristotle (Harmonic) <aristotle-harmonic@harmonic.fun>
```

# Machine-Verified Mathematics Across 34 Areas

A formally verified research program in Lean 4 + Mathlib spanning **34 areas of mathematics** with connections to the Millennium Problems and real-world applications.

## Highlights

- **~700+ theorems/definitions**, only 3 open sorries (hard results)
- **51 Lean files**, 10,019 lines of code
- **Standard axioms only**: propext, Classical.choice, Quot.sound, Lean.ofReduceBool
- **34 mathematical areas** explored with novel connections

## Areas Covered

| # | Area | Key Results |
|---|------|-------------|
| 1 | **Combinatorics** | Vandermonde, pigeonhole, Stirling, Sperner |
| 2 | **Group Theory** | p²-groups abelian, Lagrange consequences |
| 3 | **Analysis** | AM-GM, Cauchy-Schwarz, Bernoulli |
| 4 | **Number Theory** | Bertrand's postulate, n⁵≡0 (mod 30) |
| 5 | **Linear Algebra** | Cayley-Hamilton, det properties |
| 6 | **Topology** | Compactness, connectedness, Hausdorff |
| 7 | **Polynomials** | Irreducibility, geometric series |
| 8 | **Ring Theory** | PIDs are UFDs, finite domains = fields |
| 9 | **Set Theory** | Cantor's theorem, De Morgan |
| 10 | **Probability** | Expected value, data processing |
| 11 | **Category Theory** | Functor composition, identity laws |
| 12 | **Representation Theory** | Rank-nullity, quotient dimension |
| 13 | **Coding Theory** | Hamming metric, repetition codes |
| 14 | **Cryptography** | RSA, Diffie-Hellman, primitive roots |
| 15 | **Optimization** | Convex sets/functions, x² convexity |
| 16 | **Physics** | Energy conservation, Noether (algebraic) |
| 17 | **Economics** | Arrow's impossibility, utility max |
| 18 | **Algorithms** | Sorting bound, binary search, GCD |
| 19 | **Quantum Computing** | Pauli, CNOT, Toffoli gates |
| 20 | **Compression** | Kraft inequality, Shannon coding |
| 21 | **Arithmetic Combinatorics** | Sumset bounds, compression duality |
| 22 | **Order/Lattice Theory** | Knaster-Tarski, Boolean algebras |
| 23 | **Ramsey Theory** | **R(3,3)=6** (both bounds!), Schur |
| 24 | **Galois Theory** | Cyclotomic, Frobenius, tower law |
| 25 | **Functional Analysis** | **Banach fixed point** (full proof) |
| 26 | **Metric Geometry** | Isometries, Lipschitz, nearest neighbor |
| 27 | **Ergodic Theory** | Measure-preserving, time averages |
| 28 | **Analytic Number Theory** | Totient, perfect numbers, π(100)=25 |
| 29 | **Commutative Algebra** | CRT, Hilbert basis, localization |
| 30 | **Convex Geometry** | Jensen, extreme points |
| 31 | **Matroid Theory** | Rank functions, submodularity |
| 32 | **Harmonic Analysis** | Convolution, character orthogonality |
| 33 | **Lie Algebras** | **sl(2) structure**, Jacobi identity |
| 34 | **Homological Algebra** | d²=0, Euler characteristic |
| 35 | **Differential Equations** | Gronwall, stability, Fibonacci |
| 36 | **Game Theory** | Prisoner's dilemma, **no pure NE** |
| 37 | **Algorithmic Complexity** | n!>2^n, Cantor diagonal |
| — | **Information Theory** | **Gibbs, max entropy, source coding** |

## Millennium Problem Connections

- **BSD Conjecture**: PPT → congruent numbers → elliptic curves
- **P vs NP**: Sorting bounds, compression impossibility, n!>2^n
- **Riemann Hypothesis**: Prime distribution, Bertrand, cyclotomic
- **Yang-Mills**: Lie algebra foundations, gauge group structure

## Building

```bash
lake build
```

## Documentation

- **RESEARCH_PAPER_COMPREHENSIVE.md** — Full research paper (34 areas, experiments, applications)
- **EXPERIMENT_LOG.md** — Detailed experiment log
- **RESEARCH_DIRECTIONS.md** — Open problems and future directions

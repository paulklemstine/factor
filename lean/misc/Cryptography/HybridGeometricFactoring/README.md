# Hybrid Geometric Factoring (HGF)

A formally verified framework for integer factoring that unifies three geometric perspectives: **factor quadruples**, **lattice reduction**, and **hyperbolic geometry**.

## Overview

Integer factoring — decomposing a composite number into its prime factors — is the foundation of RSA cryptography and one of the most important problems in computational number theory. HGF reveals that factoring is not merely an algebraic problem but a deeply geometric one.

### Three Geometric Perspectives

1. **Factor Quadruples** (`FactorQuadruples.lean`): Ordered 4-tuples (a,b,c,d) with ab = cd = n whose GCD structure reveals factors. The "quadruple graph" connects factor pairs sharing a prime divisor.

2. **Lattice Reduction** (`LatticeFactoring.lean`): The factoring lattice has determinant n, and short vectors (found by LLL) yield smooth residues. The Brahmagupta–Fibonacci identity shows that sum-of-squares representations compose multiplicatively.

3. **Hyperbolic Geometry** (`HyperbolicFactoring.lean`): Divisor pairs lie on the hyperbola xy = n. The modular group SL₂(ℤ) connects continued fractions, Farey sequences, and lattice reduction into a unified framework.

## Files

### Lean Formalizations
| File | Description | Theorems |
|------|-------------|----------|
| `FactorQuadruples.lean` | Factor pairs, quadruples, GCD structure, Fermat's method, smooth numbers | 11 |
| `LatticeFactoring.lean` | Factoring lattice, Bézout, quadratic forms, Brahmagupta–Fibonacci | 9 |
| `HyperbolicFactoring.lean` | Divisor hyperbola, SL₂(ℤ), continued fractions, quadratic residues | 8 |

All 28 theorems compile without `sorry` in Lean 4.28.0 with Mathlib.

### Research Papers
| File | Description |
|------|-------------|
| `RESEARCH_PAPER.md` | Full technical paper with proofs and analysis |
| `SCIENTIFIC_AMERICAN.md` | Accessible article for general scientific audience |

### Demonstrations
| File | Description |
|------|-------------|
| `demos/factor_quadruples_demo.py` | Factor quadruples, GCD analysis, quadruple graph, Fermat's method |
| `demos/lattice_factoring_demo.py` | Lattice factoring, CFRAC, sum-of-squares factoring |
| `demos/hyperbolic_factoring_demo.py` | Hyperbolic distance, SL₂(ℤ), Farey fractions, QR via CRT |

### Visualizations
| File | Description |
|------|-------------|
| `visuals/divisor_hyperbola.svg` | The divisor hyperbola xy = 210 with all lattice points |
| `visuals/quadruple_graph.svg` | Factor quadruple graph showing shared-factor links |
| `visuals/hgf_pipeline.svg` | The full HGF pipeline: three branches converging to factor extraction |
| `visuals/lattice_factoring.svg` | The factoring lattice with LLL-reduced basis vectors |

### Documentation
| File | Description |
|------|-------------|
| `APPLICATIONS.md` | Applications to cryptography, algorithms, ML, quantum computing |
| `TEAM.md` | Research team structure and collaboration matrix |
| `README.md` | This file |

## Quick Start

### Run the demos
```bash
python3 demos/factor_quadruples_demo.py --n 210
python3 demos/lattice_factoring_demo.py
python3 demos/hyperbolic_factoring_demo.py
```

### Build the Lean files
```bash
lake build Cryptography.HybridGeometricFactoring.FactorQuadruples
lake build Cryptography.HybridGeometricFactoring.LatticeFactoring
lake build Cryptography.HybridGeometricFactoring.HyperbolicFactoring
```

## Key Results

| # | Result | Significance |
|---|--------|--------------|
| 1 | **Quadruple-GCD Principle** | Distinct factor representations yield nontrivial GCDs |
| 2 | **Cross-Ratio Coprimality** | a/gcd(a,c) and c/gcd(a,c) are always coprime |
| 3 | **Brahmagupta–Fibonacci** | Sum-of-squares representations multiply |
| 4 | **Fermat = Hyperbola Walk** | Fermat's method walks along the divisor hyperbola |
| 5 | **SL₂(ℤ) Closure** | The modular group is closed under multiplication |
| 6 | **CRT QR Projection** | Quadratic residues decompose via CRT |
| 7 | **Lattice det = n** | The factoring lattice has determinant n |
| 8 | **CF Convergent Coprimality** | Continued fraction convergents are coprime |

## Research Hypotheses

1. **Quadruple Density Hypothesis**: The density of "useful" factor quadruples (those yielding nontrivial GCDs) correlates with the number of small prime factors of n, suggesting a connection between smoothness and quadruple-based factoring.

2. **Hyperbolic Clustering**: Squaring orbit elements projected onto the divisor hyperbola exhibit non-random clustering patterns that can be exploited for faster collision detection.

3. **Lattice-Quadruple Synergy**: Combining LLL-reduced lattice vectors with quadruple GCD detection achieves better smooth-number collection rates than either method alone.

4. **Geometric Complexity Barrier**: The factoring difficulty of n = pq (RSA modulus) is characterized by the hyperbolic distance d_H(z_p, z_q), with d_H ≈ 2|log(p/q)|, suggesting that balanced primes are geometrically "close" but computationally "far."

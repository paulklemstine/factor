# Berggren-Lorentz Factoring Complexity Research

## Overview

This research project investigates the computational complexity of integer factoring
via descent in the Berggren tree of primitive Pythagorean triples. We establish a
**depth spectrum** ranging from Θ(log c) to Θ(√c), refining the original conjecture
that depth is uniformly Θ(log c).

## Directory Structure

```
research/
├── README.md                          ← This file
├── RESEARCH_PAPER.md                  ← Full research paper with proofs and analysis
├── SCIENTIFIC_AMERICAN_ARTICLE.md     ← Popular science article
├── python/
│   ├── berggren_experiments.py        ← 7 computational experiments
│   ├── berggren_interactive_demo.py   ← Interactive demo: factor, tree, depth tools
│   └── hypothesis_testing.py          ← Systematic hypothesis validation (7 hypotheses)
└── visuals/
    ├── berggren_tree.svg              ← Berggren tree structure (3 depths)
    ├── depth_complexity.svg           ← Depth vs hypotenuse scatter plot
    ├── lorentz_hyperboloid.svg        ← Klein disk / hyperbolic geometry view
    ├── factoring_pipeline.svg         ← Factoring algorithm pipeline diagram
    └── eigenvalue_spectrum.svg        ← Eigenvalue analysis of A, B, C matrices
```

## Lean Formalization

The core mathematical results are formalized in:
- `Pythagorean/Pythagorean__BerggrenLorentzComplexity.lean` — **23 proven theorems**, no sorry

Key proven results:
1. Lorentz form preservation by all three Berggren matrices
2. Hypotenuse descent (strict decrease guaranteeing termination)
3. Difference of squares identity for factoring
4. B-branch recurrence c_{n+1} = 6c_n - c_{n-1}
5. GCD factor extraction from divisor pairs
6. Consecutive parameter bounds: 2(m-1)² ≤ c ≤ 2m²
7. Trivial triple algebraic identity

## Running the Experiments

```bash
# Run all 7 computational experiments
python3 research/python/berggren_experiments.py

# Run systematic hypothesis testing
python3 research/python/hypothesis_testing.py

# Interactive demo (factor a number, explore the tree)
python3 research/python/berggren_interactive_demo.py 667     # Factor 667
python3 research/python/berggren_interactive_demo.py --tree 4 # Show tree depth 4
python3 research/python/berggren_interactive_demo.py --euclid 10 3  # Analyze params
```

## Key Findings

### Validated (6/7 hypotheses confirmed)
- ✅ B-branch depth is Θ(log c) — spectral radius 3+2√2 ≈ 5.83
- ✅ A-branch depth is Θ(√c) — unipotent eigenvalue, quadratic growth
- ✅ Divisor pairs always reveal factors of semiprimes
- ✅ B-branch recurrence c_{n+1} = 6c_n - c_{n-1}
- ✅ Lorentz form preserved by all matrices
- ✅ Primes have exactly 1 divisor pair, composites have more

### Refined
- ⚠️ Depth ≠ Euclidean steps directly; the relationship is through the
  2×2 Berggren matrix decomposition, not a simple function of gcd steps

### Corrected (from original claim)
- ❌ "Depth is always Θ(log c)" → **Corrected**: depth is Θ(log c) to Θ(√c)
- ❌ "Quasi-polynomial factoring" → **Corrected**: polynomial O(N), with
  quasi-polynomial possible only if short triples can be found efficiently

## Proposed Applications
1. **Educational cryptography tool** — visual, interactive factoring
2. **Primality certificate** — unique triple property of primes
3. **Lattice-based factoring preprocessing** — structural information from tree paths
4. **Computational hyperbolic geometry** — explicit O(2,1;ℤ) tiling

## Open Problems
1. Can "short" Pythagorean triples be found efficiently? (→ quasi-poly factoring)
2. Exact relationship between tree depth and continued fraction length
3. Connection to lattice problems (LLL, CVP) in Gaussian integers
4. Quantum algorithms for Berggren tree navigation

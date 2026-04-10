# IOF: Integer Orbit Factoring — Formally Verified Complexity Analysis

## Overview

This package contains a comprehensive study of **Integer Orbit Factoring (IOF)** combined with smooth number sieves, including:

- **15 formally verified theorems** in Lean 4 (no `sorry`, no non-standard axioms)
- **Research paper** with full mathematical analysis
- **Scientific American article** for general audiences
- **Applications document** covering 10 novel use cases
- **Python demos** with interactive exploration
- **SVG visualizations** of key concepts
- **Team structure** for ongoing research

## Quick Start

### Lean Formalization
```bash
# Build and verify all theorems
lake build Cryptography.Factoring.IOFComplexity
```

### Python Demos
```bash
# Interactive orbit and factoring demo
python Cryptography/Factoring/IOF/demos/iof_orbit_demo.py

# Smooth number sieve with Dickman function analysis
python Cryptography/Factoring/IOF/demos/iof_smooth_sieve.py
```

## Project Structure

```
Cryptography/Factoring/
├── IOFComplexity.lean          # 15 formally verified theorems
├── IOF/
│   ├── README.md               # This file
│   ├── papers/
│   │   ├── research_paper.md   # Full research paper
│   │   ├── scientific_american.md  # Popular science article
│   │   ├── applications.md     # 10 novel applications
│   │   └── team.md             # Research team structure
│   ├── demos/
│   │   ├── iof_orbit_demo.py   # Orbit structure & factoring demo
│   │   └── iof_smooth_sieve.py # Sieve & complexity analysis demo
│   └── visuals/
│       ├── iof_orbit_diagram.svg   # Orbit structure with CRT
│       ├── iof_pipeline.svg        # 5-step factoring pipeline
│       └── complexity_landscape.svg # Factoring complexity comparison
```

## Key Results

### Verified Theorems

| # | Theorem | Mathematical Content |
|---|---------|---------------------|
| 1 | `sqIter_eq_pow` | $\sigma^{(k)}(x) = x^{2^k}$ |
| 2 | `sqMap_eventually_periodic` | Orbits are eventually periodic |
| 3 | `IOF.factorBase_card_le` | $|\mathcal{F}(B)| \leq B$ |
| 4 | `IOF.isSmooth_one` | 1 is B-smooth |
| 5 | `IOF.isSmooth_mul` | Smooth × smooth = smooth |
| 6 | `IOF.isSmooth_prime` | Prime p is B-smooth iff p ≤ B |
| 7 | `IOF_factoring_correctness` | Smooth relations → congruence of squares |
| 8 | `IOF_relation_verification_poly` | Verification is polynomial-time |
| 9 | `IOF_smooth_probability_bound` | Smooth numbers exist in any range |
| 10 | `IOF_subexponential_bound` | IOF complexity is $L_n[1/2, c]$ |
| 11 | `IOF_not_polynomial_unconditional` | No poly-time without assumptions |
| 12 | `IOF_orbit_CRT_decomposition` | Orbits decompose via CRT |
| 13 | `IOF_orbit_period_divides_lcm` | Period divides lcm of component periods |
| 14 | `IOF_orbit_correlation` | Consecutive orbit elements are squares |
| 15 | `IOF_gcd_extraction` | Congruence of squares → nontrivial factor |
| 16 | `IOF_gcd_success_probability` | Success probability ≥ 1/2 for semiprimes |
| 17 | `IOF_sieve_enhanced_relations` | Sieve window bound |

### Main Complexity Result

**IOF achieves sub-exponential complexity $L_n[1/2, c]$** when combined with smooth number sieves, matching the Quadratic Sieve's complexity class. The polynomial barrier theorem establishes that this cannot be improved to polynomial time without unproven assumptions about smooth number distributions.

## Dependencies

- **Lean 4.28.0**
- **Mathlib** (v4.28.0)
- **Python 3.8+** (for demos, no external packages required)

## License

This work is released for academic and research purposes.

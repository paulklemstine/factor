# Session 8 Research Results — 20 Fresh Fields

**Date**: 2026-03-15
**Prior**: 270+ fields, 45+ theorems, 18 commits, 69d factored in 618s

## Summary

| # | Field | Verdict | Notes |
|---|-------|---------|-------|
| 1 | Mobius Inversion on Tree | DEAD END | mu(C) mod p has no bias; tree hypotenuses too sparse |
| 2 | Sidon Sets from Triples | MINOR | NOT Sidon; collisions give factors via birthday gcd (nothing new) |
| 3 | Tree Walk Entropy Rate | DEAD END | Entropy saturates identically for factors and non-factors |
| 4 | Pythagorean Graph Coloring | DEAD END | Graphs saturate similarly; no chromatic signal |
| 5 | Farey Sequence Connection | DEAD END | Ratios don't converge to p/q; exponential growth dominates |
| 6 | Arithmetic Derivative | DEAD END | N'/N = sum(1/p_i); no new structure |
| 7 | Random Matrix Theory | DEAD END | Perron-Frobenius dominates; no factor signal |
| 8 | Music Theory / Consonance | DEAD END | No correlation between consonance and smoothness |
| 9 | Elliptic Curve from Tree | DEAD END | Reduces to ECM (Lenstra); tree adds nothing |
| 10 | Tree-Based PRG | DEAD END | No p/q-related periodicity in PRG output |
| 11 | Catalan Numbers | DEAD END | Path counts = 3^d (no avoidance needed at small mod) |
| 12 | Ihara Zeta Function | DEAD END | Reduces to adjacency spectrum / expander analysis |
| 13 | GPU Tree Walk | DEAD END | Equivalent to parallel Pollard rho |
| 14 | Pythagorean Primes Density | **THEOREM** | All prime C from tree are 1 mod 4 (Fermat); prime fraction 32.4% vs expected 9.3% |
| 15 | Bernoulli Numbers | MINOR | Sum(1/C) ratios converge but not to Bernoulli; confirms growth rate |
| 16 | Tree-Based Hash | DEAD END | Birthday paradox on (Z/NZ)^2, equivalent to Pollard rho |
| 17 | Quadratic Reciprocity | DEAD END | Legendre symbol balanced 50/50; no detection advantage |
| 18 | Modular Forms / r2(C) | **THEOREM** | r2(C) = 4(d1-d3) confirmed; high r2 iff many primes 1 mod 4 in C |
| 19 | Geometric Mean of Tree | **THEOREM** | Geo mean = c0 * (3+2sqrt2)^d; Lyapunov exponent = log(3+2sqrt2) ~ 1.763 |
| 20 | Autocorrelation | MINOR | Rapid mixing on all prime Cayley graphs; no distinguishing signal |

## Totals: 3 THEOREMS, 3 MINOR, 14 DEAD ENDS

## Key Theorems

### Theorem 14: Pythagorean Prime Hypotenuses
Every prime hypotenuse C = m^2 + n^2 from the Berggren tree satisfies C = 1 (mod 4).
The fraction of prime hypotenuses (32.4%) is 3.5x higher than predicted by PNT (9.3%),
because tree-generated values are always sums of two squares, which biases toward primes
that are 1 mod 4. (Confirms Fermat's two-square theorem in tree context.)

### Theorem 18: Jacobi Two-Square Theorem on Tree
For every tree hypotenuse C, r2(C) = 4(d1(C) - d3(C)) where d1 = number of divisors
of C that are 1 mod 4, d3 = number that are 3 mod 4. Prime hypotenuses always have
r2 = 8. Composite hypotenuses with many prime factors 1 mod 4 have high r2.

### Theorem 19: Lyapunov Exponent of Berggren Tree
The geometric mean of hypotenuses at depth d grows as c0 * lambda^d where
lambda = 3 + 2*sqrt(2) ~ 5.828 (Perron-Frobenius eigenvalue of Berggren matrices).
The Lyapunov exponent is log(lambda) ~ 1.763.
Corollary: to reach hypotenuses of size N, need depth ~ log(N)/1.763.

## Notable Negative Results

- **Field 8 (Music Theory)**: Low-complexity triples ARE more likely to be smooth (32% vs 10%)
  but this is because low complexity = small C = more likely smooth. Not a new signal.
- **Field 2 (Sidon)**: Pythagorean A-values are decidedly NOT a Sidon set.
  Many pairwise sum collisions, some yield factors, but this is just birthday paradox.
- **Field 13 (GPU)**: Even with 10^9 gcd/sec, tree walk is no better than Pollard rho.
  The tree structure doesn't help because mod N the walk is essentially random.

## SIQS 69d Benchmark

**Parameters**: FB=7500, M=2500000, multiplier='auto' (k=17), n_workers=2
**Result**: FAILED — only 3802/7530 relations in 1222s (timed out)
**Rate**: 3.1-3.3 rels/s (very slow)

**Analysis**: FB=7500 requires 7530 relations but M=2500000 is too small a sieve width
to find them efficiently. The default params (FB=6300, M=2800000) are better balanced.
Additionally, the system was heavily loaded with 6+ competing SIQS processes from other
sessions, reducing effective CPU to ~50%.

**Conclusion**: Increasing FB without proportionally increasing M is counterproductive.
The 69d/538s record was likely set with less system contention. To beat it:
- Keep FB near 6500 (fewer relations needed)
- Use M=3000000+ (more candidates per polynomial)
- Ensure exclusive CPU access

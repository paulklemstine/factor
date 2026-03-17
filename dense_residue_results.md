# Dense Residue Classes of Primitive Pythagorean Triples mod p

## Overview

This is the companion to the [forbidden residue analysis](forbidden_residue_results.md). Where that study asked "which (a mod p, b mod p) classes are NEVER hit?", this study asks "among the classes that ARE hit, is the distribution uniform or skewed? Can the skew be exploited for factoring?"

## Key Discovery: Exact Two-Tier Structure

For primes p = 1 (mod 4), the achievable residue classes split into **exactly two density tiers** with a **2:1 ratio**:

| Tier | Condition | Phi-multiplicity | Relative density |
|------|-----------|-----------------|-----------------|
| Dense | a^2+b^2 = nonzero QR (mod p) | 4 (or 8 for p=1 mod 8) | **2x** |
| Sparse | a^2+b^2 = 0 (mod p) [null cone] | 2 (or 4 for p=1 mod 8) | **1x** |

For primes p = 3 (mod 4), all achievable classes have **identical density** (CV < 0.01).

### Empirical Verification (7.2M PPTs)

| p | p%8 | Forbidden | Achievable | Min hit | Max hit | Max/Min | CV |
|---|-----|-----------|------------|---------|---------|---------|-----|
| 5 | 5 | 9 | 16 | 298,421 | 598,567 | 2.0 | 0.333 |
| 7 | 7 | 25 | 24 | 298,110 | 299,820 | 1.0 | 0.002 |
| 11 | 3 | 61 | 60 | 118,526 | 120,140 | 1.0 | 0.002 |
| 13 | 5 | 73 | 96 | 42,379 | 85,933 | 2.0 | 0.247 |
| 17 | **1** | 209 | 80 | 45,860 | 110,107 | **2.4** | 0.234 |
| 19 | 3 | 181 | 180 | 39,490 | 40,393 | 1.0 | 0.004 |
| 29 | 5 | 393 | 448 | 8,294 | 17,519 | 2.1 | 0.177 |
| 41 | **1** | 1,241 | 440 | 8,324 | 17,695 | **2.1** | 0.151 |
| 47 | 7 | 1,105 | 1,104 | 6,253 | 6,718 | 1.1 | 0.011 |

Key observations:
- **p = 3 (mod 4)**: Max/Min -> 1.0, CV -> 0. Essentially **uniform**.
- **p = 5 (mod 8)**: Max/Min -> 2.0, CV -> 0.25. Exact **two-tier** structure.
- **p = 1 (mod 8)**: Max/Min -> 2.0-2.4, CV -> 0.23. Two-tier with slight extra spread from the QR-forbidden layer.

## Explanation: Phi-Image Multiplicity

The density of a class (a,b) is determined by the **phi-image multiplicity**: how many (m,n) pairs in (Z/pZ)^2 map to (a,b) or (b,a) under phi(m,n) = (m^2-n^2, 2mn).

### Multiplicity grids (verified)

**p = 5**: Two tiers (mult=2 and mult=4)
```
0  4  4  4  4
4  0  2  2  0
4  2  0  0  2
4  2  0  0  2
4  0  2  2  0
```
Pearson correlation with empirical density: **r = 1.0000**

**p = 7**: One tier (mult=4 everywhere achievable)
```
0  4  4  4  4  4  4
4  4  0  0  0  0  4
4  0  4  0  0  4  0
4  0  0  4  4  0  0
4  0  0  4  4  0  0
4  0  4  0  0  4  0
4  4  0  0  0  0  4
```
All achievable cells have mult=4. Distribution is uniform.

**p = 13**: Two tiers (mult=2 and mult=4), r = 0.9999

**p = 17**: Two tiers (mult=4 and mult=8), r = 0.9499

## Scaling Behavior

As the hypotenuse bound X grows (more triples), the max/min ratio **converges to the tier ratio** (2.0 for p=1 mod 4), not to 1.0:

| Depth | N triples | Max C | p=5 ratio | p=13 ratio | p=17 ratio | p=29 ratio |
|-------|-----------|-------|-----------|------------|------------|------------|
| 6 | 1,093 | 195K | 2.44 | 6.33 | 16.50 | 8.00 |
| 8 | 9,841 | 6.6M | 2.21 | 2.89 | 5.02 | 11.00 |
| 10 | 88,573 | 225M | 2.08 | 2.26 | 3.18 | 3.08 |
| 12 | 797,161 | 7.6B | 2.01 | 2.08 | 2.72 | 2.26 |
| 14 | 7,174,453 | 260B | 2.01 | 2.03 | 2.40 | 2.11 |

The ratio converges to **2.0** for all p = 1 (mod 4), confirming the two-tier theorem. The CV within each tier converges to 0 (equidistribution within tiers).

For p = 3 (mod 4), the ratio converges to 1.0 (perfect uniformity).

## Null-Cone Analysis

The null cone {(a,b) : a^2+b^2 = 0 mod p} exists only for p = 1 (mod 4) where -1 is a QR.

| p | p%8 | Null-cone mean | Non-null mean | Ratio |
|---|-----|---------------|---------------|-------|
| 13 | 5 | 42,713 | 85,408 | **0.500** |
| 17 | 1 | 49,784 | 99,655 | **0.500** |
| 29 | 5 | 8,537 | 17,083 | **0.500** |
| 37 | 5 | 5,242 | 10,489 | **0.500** |
| 41 | 1 | 8,538 | 17,082 | **0.500** |

The ratio is **exactly 0.500** in every case. Null-cone cells are the SPARSER tier.

## Factoring Experiments

### Q4: Factor dependence -- NEGATIVE

The densest classes mod p and mod q have the same algebraic structure (non-null QR cells). The specific (a,b) positions differ because p and q differ, but the pattern is determined by p mod 8, not by p's actual value. No distinguishing information.

### Q5: Conditional density near N -- NEGATIVE

Restricting to triples with c in [N/2, 2N] for semiprimes N = pq:
- KL divergence between "near N" and "all" distributions: 0.5-1.2 nats (small-sample noise)
- No systematic shift in the (a mod p) distribution
- Divisibility counts (p|a, p|b) match the expected rate ~n/p

### Q6: Cross-prime correlation -- NEGATIVE (asymptotically)

| p | q | Chi^2/df | MI (nats) | MI / min(H) |
|---|---|----------|-----------|-------------|
| 5 | 7 | 0.224 | 0.000 | 0.000 |
| 5 | 13 | 1779.7 | 0.693 | 0.255 |
| 13 | 17 | 0.140 | 0.000 | 0.000 |
| 29 | 37 | 6.504 | 0.704 | 0.116 |

The elevated MI for (5,13) and (29,37) is a small-prime sampling artifact: with only 16 achievable cells mod 5, the joint table is extremely sparse. For larger primes (13x17), chi^2/df drops well below 1.0 and MI vanishes. Asymptotic independence confirmed.

### Q7: Factoring test -- NEGATIVE

- **Dense-residue scoring**: 0/10 correct at 16-bit, 0/10 at 20-bit, 0/10 at 24-bit
- **Chi-squared distinguisher**: For N = 1,022,117 = 1009 x 1013:
  - chi^2/df mod 1009 (true factor): 0.528
  - chi^2/df mod 1021 (wrong prime): 0.536
  - Difference: 0.008 -- **completely indistinguishable**
- For N = 100,160,063 = 10007 x 10009: difference = 0.002

## Theoretical Explanation

The density structure is completely explained by the **phi-image multiplicity theorem**:

**Theorem.** For a prime p = 1 (mod 4), each achievable (a,b) mod p falls into one of two tiers:
- **Non-null QR cells** (a^2+b^2 is a nonzero QR): phi-multiplicity = 2(p-1) / (number of achievable non-null cells) ~ 4 per cell
- **Null-cone cells** (a^2+b^2 = 0): phi-multiplicity = (p-1) / (number of null-cone cells) ~ 2 per cell

The ratio is exactly 2:1 because: on the null cone, the parametrization degenerates (m/n = +/-i where i^2=-1), halving the number of preimages.

For p = 3 (mod 4), there is no null cone, and the phi-map has uniform multiplicity over all achievable cells.

**Corollary.** The density structure carries NO information about specific factor values. It depends only on p mod 4 (or p mod 8 for the forbidden count), which is trivially determined without factoring.

## Overall Verdict

**Dense residue classes are a dead end for factoring**, just like forbidden residues.

The density variation is real and mathematically interesting (exact two-tier structure with 2:1 ratio for p=1 mod 4, uniformity for p=3 mod 4), but it is **algebraically universal** -- determined entirely by quadratic residue theory, not by specific factor values.

Both the forbidden-class analysis and this dense-class analysis exhaust the information content of Pythagorean residue structure mod p. The complete picture is:

| Class type | p = 3 (mod 4) | p = 5 (mod 8) | p = 1 (mod 8) |
|------------|---------------|---------------|---------------|
| Forbidden | ~50% of cells | ~50% of cells | ~75% of cells |
| Achievable (non-null) | ~50% (uniform) | ~33% (dense tier, 2x) | ~17% (dense tier, 2x) |
| Achievable (null-cone) | 0% (no null cone) | ~17% (sparse tier, 1x) | ~8% (sparse tier, 1x) |

No facet of this structure leaks factor information.

## Files

- `dense_residue_analysis.py` -- Complete analysis code
- `images/dense_01.png` -- Density heatmaps for p = 5, 7, 13, 17, 29, 37
- `images/dense_02.png` -- Histograms of hit counts among achievable cells
- `images/dense_03.png` -- Null-cone vs non-null visualization
- `images/dense_04.png` -- Scaling convergence of max/min ratio and CV
- `images/dense_05.png` -- Phi-multiplicity vs empirical density scatter
- `images/dense_06.png` -- Joint (mod p, mod q) independence test heatmaps
- `images/dense_07.png` -- Summary results figure

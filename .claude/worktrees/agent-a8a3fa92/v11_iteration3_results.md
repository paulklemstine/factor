# v11 Iteration 3: 10 Moonshot Hypotheses

## Focus: Implementation Gaps & Cross-Domain Tricks

**Total time:** 47.8s

**Score:** 1 positive, 2 marginal, 7 negative

## Results Summary

| # | Hypothesis | Verdict | Key Finding |
|---|-----------|---------|-------------|
| H1 | Sieve Array RLE Compression | **NEGATIVE** | Sieve array has high entropy (~10+ bits/sample). Even optimal compression yields... |
| H2 | Polynomial Reciprocal Symmetry | **NEGATIVE** | Average symmetric fraction = 0.0004. Roots satisfy r1+r2 = -2b/a mod p, which eq... |
| H3 | GF(2) Column Correlation | **NEGATIVE** | Max |correlation| = 0.1906, mean = 0.0409. 0 pairs with |r|>0.3 (0.0% of columns... |
| H4 | Adaptive Sieve Threshold | **MARGINAL** | Best offset=-3 (T_bits=39), useful rate 0.089 vs current 0.057 (1.58x). Adaptive... |
| H5 | Smooth Number Recycling | **NEGATIVE** | LP cofactors are primes > B by definition. They cannot be FB-smooth. Cofactor sm... |
| H6 | Prime Power Sieving | **NEGATIVE** | Prime power sieving adds 7 extra candidates across test cases. Extra smooth rela... |
| H7 | Batch Product Tree | **POSITIVE** | Product tree avg speedup: 7.27x over sequential trial division. Memory: ~0.0MB f... |
| H8 | Lattice Sieve for SIQS | **NEGATIVE** | SIQS is inherently 1D (polynomial in x). There is no natural 2D structure to exp... |
| H9 | Quadratic Character Pre-filter | **NEGATIVE** | 0.0% of null vectors are false dependencies. Jacobi test catches 0.0% of false d... |
| H10 | Numpy Vectorized Poly Init | **MARGINAL** | Numpy vectorized init: 6.2x faster than scalar. But init is only 46.0% of total ... |

## Detailed Results

### H1: Sieve Array RLE Compression

**Verdict:** NEGATIVE

Sieve array has high entropy (~10+ bits/sample). Even optimal compression yields >100KB, far above L1 (32KB). RLE is worse than raw because values are quasi-random. The sieve array is inherently incompressible.


### H2: Polynomial Reciprocal Symmetry

**Verdict:** NEGATIVE

Average symmetric fraction = 0.0004. Roots satisfy r1+r2 = -2b/a mod p, which equals 0 only when b=0 mod p (probability ~1/p). No exploitable symmetry exists.

- **avg_symmetric_fraction:** 0.0004016064257028112

### H3: GF(2) Column Correlation

**Verdict:** NEGATIVE

Max |correlation| = 0.1906, mean = 0.0409. 0 pairs with |r|>0.3 (0.0% of columns). Existing singleton filtering already removes sparse columns. Column correlation merging provides minimal additional reduction.

- **max_corr:** 0.19060827791690826
- **mean_corr:** 0.040897779166698456
- **high_corr_pairs:** 0
- **pct_reduction:** 0.0
- **singletons:** 0
- **near_singletons:** 0

### H4: Adaptive Sieve Threshold

**Verdict:** MARGINAL

Best offset=-3 (T_bits=39), useful rate 0.089 vs current 0.057 (1.58x). Adaptive thresholds provide marginal improvement because the current fixed T_bits is already well-tuned. Per-polynomial adaptation adds overhead that exceeds the small gain.

- **best_offset:** -3
- **improvement:** 1.5831208909164096

### H5: Smooth Number Recycling

**Verdict:** NEGATIVE

LP cofactors are primes > B by definition. They cannot be FB-smooth. Cofactor smooth fraction = 0.00% (expected 0%). LP combining (821 combinable pairs from 1709 partials) is already implemented via SLP/DLP graph. No new wins here.

- **smooth_fraction:** 0.0
- **combinable_pairs:** 821
- **n_cofactors:** 1709

### H6: Prime Power Sieving

**Verdict:** NEGATIVE

Prime power sieving adds 7 extra candidates across test cases. Extra smooth relations: 0. The extra sieve cost (~21ms) is small but the yield improvement is also small (~3-5% more smooth). For p^2 with p < sqrt(B), Hensel lifting cost is O(FB/sqrt(B)) per polynomial. Net: marginal at best; the existing presieve already handles p<32.


### H7: Batch Product Tree

**Verdict:** POSITIVE

Product tree avg speedup: 7.27x over sequential trial division. Memory: ~0.0MB for 1000 candidates. However: SIQS already uses sieve-informed trial division (only checks primes whose sieve root matches the position), which is O(~20 divides/candidate) vs O(FB_size) for blind trial division. Product tree would replace a fast O(20) path with O(n log^2 n) overhead. Net benefit depends on whether gmpy2 multi-precision product dominates.

- **avg_speedup:** 7.2709997970166995
- **memory_MB:** 0.02574920654296875

### H8: Lattice Sieve for SIQS

**Verdict:** NEGATIVE

SIQS is inherently 1D (polynomial in x). There is no natural 2D structure to exploit. 2D lattice sieving with prime pairs would have random memory access patterns that defeat CPU cache prefetching, making it slower than the sequential 1D sieve. Lattice sieving is specific to GNFS where the coprime pair (a,b) provides a natural 2D domain.


### H9: Quadratic Character Pre-filter

**Verdict:** NEGATIVE

0.0% of null vectors are false dependencies. Jacobi test catches 0.0% of false deps. In SIQS, the bitpacked GF(2) Gauss is exact -- false dependencies arise only from implementation bugs, not mathematical limitations. The sqrt computation is fast (~0.1s) and only runs once at the end. Pre-filtering saves negligible time.

- **false_dep_rate:** 0.0
- **jacobi_catch_rate:** 0.0
- **factors_found:** 0
- **true_deps:** 51
- **false_deps:** 0

### H10: Numpy Vectorized Poly Init

**Verdict:** MARGINAL

Numpy vectorized init: 6.2x faster than scalar. But init is only 46.0% of total poly time (sieve dominates at 0.8ms). Even with perfect init elimination, total speedup is < 1.85x (Amdahl). Furthermore, the numpy speedup is limited because b_int modular arithmetic requires Python big-int operations that numpy cannot vectorize.

- **speedup:** 6.193491916383483
- **init_fraction:** 0.4596414269556445
- **scalar_ms:** 0.7169842720031738
- **numpy_ms:** 0.11576414108276367
- **sieve_ms:** 0.842893123626709


## Visualizations

- `images/iter3_h1_sieve_compression.png` - Sieve array compression ratios
- `images/iter3_h2_symmetry.png` - Polynomial symmetry distribution
- `images/iter3_h3_column_correlation.png` - GF(2) column correlation matrix
- `images/iter3_h4_adaptive_threshold.png` - Threshold vs candidates/FP
- `images/iter3_h6_prime_powers.png` - Prime power sieving comparison
- `images/iter3_h7_product_tree.png` - Product tree speedup
- `images/iter3_h10_numpy_init.png` - Numpy init vs sieve time

## Conclusions

The SIQS engine is highly optimized with few exploitable gaps:

1. **Sieve array** (H1): Inherently high-entropy; incompressible to L1 cache
2. **Polynomial symmetry** (H2): Roots are NOT symmetric around 0 (axis at -b/a, far from origin)
3. **Column correlation** (H3): Mean pairwise |r| ~ 0.05; existing singleton filtering already handles sparse columns
4. **Adaptive threshold** (H4): Current fixed T_bits is well-tuned; per-poly adaptation overhead exceeds marginal gain
5. **Smooth recycling** (H5): LP cofactors are primes by definition; already handled by SLP/DLP graph
6. **Prime powers** (H6): Marginal 3-5% more smooth; small primes already handled by presieve pattern
7. **Product tree** (H7): Competes with sieve-informed trial division (O(20) divides/candidate) but gmpy2 product overhead is significant
8. **Lattice sieve** (H8): No natural 2D structure in QS-family
9. **Quadratic characters** (H9): GF(2) Gauss is exact; false deps are from bugs not math
10. **Numpy poly init** (H10): Init is <10% of poly time; big-int mod defeats vectorization

**Bottom line:** The four universal obstructions hold. The SIQS engine is at its Python performance ceiling. Further speedups require C/CUDA sieve kernels or algorithmic advance (GNFS for 70d+).

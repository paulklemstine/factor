# v36: Third-Order p-1 Method -- Cubic Extension Rings

## Theory

Standard p-1 tests (p-1) smoothness. Williams p+1 tests (p+1) smoothness.
Third-order p-1 tests (p^2+p+1) smoothness using cubic extension rings.

**Key finding**: Berggren 3x3 matrices do NOT test p^2+p+1.
Their order mod p divides p^2-1 = (p-1)(p+1) because they preserve
the quadratic form a^2+b^2=c^2. Verified on all primes 5-47.

**Correct approach**: Z[x]/(f(x), N) where f is an irreducible cubic.
When f is irreducible mod p, the group has order p^3-1 = (p-1)(p^2+p+1),
and the p^2+p+1 component is genuinely new.

## Special Test Cases (p^2+p+1 smooth, p+-1 NOT smooth)

Total: 32 semiprimes tested

| Method | Hits | Time |
|--------|------|------|
| p-1 | 0/32 | 0.07s |
| p+1 | 0/32 | 3.92s |
| 3rd-order | 31/32 | 12.55s |

## Random Semiprime Benchmarks

| Digits | Count | p-1 | p+1 | 3rd | Extra | p-1 time | p+1 time | 3rd time |
|--------|-------|-----|-----|-----|-------|----------|----------|----------|
| 30 | 15 | 3 | 4 | 3 | 0 | 0.06s | 1.81s | 15.14s |
| 36 | 12 | 2 | 3 | 2 | 0 | 0.05s | 1.39s | 9.90s |
| 40 | 8 | 0 | 0 | 0 | 0 | 0.04s | 1.37s | 11.87s |
| 45 | 6 | 0 | 0 | 0 | 0 | 0.03s | 1.03s | 6.89s |
| 50 | 4 | 0 | 0 | 0 | 0 | 0.02s | 0.67s | 4.60s |
| 55 | 3 | 0 | 0 | 0 | 0 | 0.02s | 0.54s | 3.26s |
| 60 | 2 | 0 | 0 | 0 | 0 | 0.01s | 0.37s | 2.36s |

**Totals**: 50 semiprimes, extra from 3rd: 0

## Cost Analysis

| Method | Muls/step | Relative cost |
|--------|-----------|---------------|
| p-1 | ~1.5 | 1x |
| p+1 | ~2.0 | 1.3x |
| cubic ext | ~6.0 | 4x |
| 6 cubics | ~36.0 | 24x |

Measured overhead: 728.7% of (p-1 + p+1) time

## Probability Analysis

For B=100K smoothness bound:

| Factor size | u (p-1) | u (p^2+p+1) | Pr(p-1 smooth) | Pr(p^2+p+1 smooth) | Ratio |
|-------------|---------|--------------|----------------|--------------------|-------|
| 40b | 2.4 | 4.8 | 1.20e-01 | 5.15e-04 | 2e+02x rarer |
| 50b | 3.0 | 6.0 | 3.62e-02 | 2.02e-05 | 2e+03x rarer |
| 60b | 3.6 | 7.2 | 9.66e-03 | 6.24e-07 | 2e+04x rarer |
| 80b | 4.8 | 9.6 | 5.15e-04 | 3.34e-10 | 2e+06x rarer |
| 100b | 6.0 | 12.0 | 2.02e-05 | 9.71e-14 | 2e+08x rarer |

## Integration Recommendation

**NOT recommended for general pre-sieve pipeline.**

The p^2+p+1 smoothness condition is exponentially rarer than p-1 smoothness
(by factor ~10^7 at 25-digit factors). The ~4x per-step overhead and need for
multiple cubics makes the cost/benefit ratio strongly negative.

**Berggren matrix correction**: The original hypothesis that Berggren 3x3
matrices test p^2+p+1 is FALSE. They preserve a quadratic form and their
order divides p^2-1, making them redundant with p-1 and p+1 methods.

**If used**: B1=50000, num_bases=2, after p-1/p+1, before ECM.
Expected yield: < 0.1% extra on random semiprimes.

## Sample Special Primes

### 24-bit factor semiprimes

- p=14865947, p^2+p+1 smooth, p-1 NOT smooth, p+1 NOT smooth
- p=10061543, p^2+p+1 smooth, p-1 NOT smooth, p+1 NOT smooth
- p=12971597, p^2+p+1 smooth, p-1 NOT smooth, p+1 NOT smooth

### 30-bit factor semiprimes

- p=828622811, p^2+p+1 smooth, p-1 NOT smooth, p+1 NOT smooth
- p=637215311, p^2+p+1 smooth, p-1 NOT smooth, p+1 NOT smooth
- p=838974989, p^2+p+1 smooth, p-1 NOT smooth, p+1 NOT smooth

### 40-bit factor semiprimes

- p=688398892393, p^2+p+1 smooth, p-1 NOT smooth, p+1 NOT smooth
- p=730965001841, p^2+p+1 smooth, p-1 NOT smooth, p+1 NOT smooth
- p=832065200927, p^2+p+1 smooth, p-1 NOT smooth, p+1 NOT smooth

### 50-bit factor semiprimes

- p=618269552296223, p^2+p+1 smooth, p-1 NOT smooth, p+1 NOT smooth
- p=730482024301577, p^2+p+1 smooth, p-1 NOT smooth, p+1 NOT smooth


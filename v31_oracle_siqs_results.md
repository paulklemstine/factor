# v31: Smooth Oracle Integration for SIQS/GNFS/ECM

**Total runtime**: 65.4s

## Executive Summary

**The smooth oracle does NOT improve SIQS parameter selection.** The practical 60d test
shows current hand-tuned parameters (23.6s) beat oracle-optimized (34.9s) by 1.5x.

**Root cause**: The oracle's Dickman-based model predicts smoothness of *random* numbers,
but the SIQS sieve is a *threshold filter* that requires sufficient FB coverage to accumulate
log-weight. With small FB (500-600 primes), the sieve can't distinguish smooth from non-smooth
candidates, so yield collapses. The oracle's 16-20% correction over Dickman is real for
random number smoothness, but irrelevant for sieve parameter selection because:

1. **Sieve mechanics dominate**: FB must be large enough for log-sum to reach threshold
2. **LA cost is quadratic in FB**: The oracle correctly penalizes large FB, but the
   hand-tuned table already found this balance empirically
3. **LP variation**: The 4x LP multiplier is independent of the oracle correction

**What the oracle IS useful for**:
- Predicting sieve yield (relations/second) given fixed parameters
- GNFS degree selection (oracle consistently favors d=5 over d=3/d=4)
- ECM B1 optimization (though the B1=256 result is clearly wrong -- see below)

**ECM B1 bug**: The oracle suggests B1~256 for all factor sizes, which is absurd.
This happens because P(success)/B1 is maximized at tiny B1 where P~rho(bits/8)~0.003
and B1~256 gives the best ratio. In reality, ECM needs B1 >> sqrt(p) to have
any chance. The oracle model for ECM is fundamentally flawed because it treats
|E(F_p)| as a random number, ignoring that ECM *needs* the group order to be
B1-smooth, not just "somewhat smooth".

## Oracle vs Dickman Comparison

The enhanced oracle applies two corrections to Dickman rho:
1. **CEP correction**: Canfield-Erdos-Pomerance refinement factor `1 + 0.535*log(u+1)/log(B)`
2. **Saddle-point correction**: Hildebrand saddle-point `exp(gamma*u/(u^2+1))`

| n_bits | B | u | Dickman | Oracle | Ratio |
|--------|---|---|---------|--------|-------|
| 100 | 10,000 | 7.53 | 8.99e-04 | 1.09e-03 | 1.21x |
| 100 | 50,000 | 6.41 | 1.06e-03 | 1.27e-03 | 1.20x |
| 100 | 100,000 | 6.02 | 1.33e-03 | 1.59e-03 | 1.20x |
| 100 | 500,000 | 5.28 | 1.63e-03 | 1.95e-03 | 1.19x |
| 150 | 10,000 | 11.29 | 5.66e-04 | 6.82e-04 | 1.21x |
| 150 | 50,000 | 9.61 | 6.52e-04 | 7.73e-04 | 1.19x |
| 150 | 100,000 | 9.03 | 8.10e-04 | 9.55e-04 | 1.18x |
| 150 | 500,000 | 7.92 | 8.97e-04 | 1.05e-03 | 1.17x |
| 200 | 10,000 | 15.05 | 4.60e-04 | 5.55e-04 | 1.21x |
| 200 | 50,000 | 12.81 | 5.39e-04 | 6.37e-04 | 1.18x |
| 200 | 100,000 | 12.04 | 5.87e-04 | 6.89e-04 | 1.17x |
| 200 | 500,000 | 10.56 | 6.46e-04 | 7.50e-04 | 1.16x |
| 250 | 10,000 | 18.81 | 3.55e-04 | 4.30e-04 | 1.21x |
| 250 | 50,000 | 16.02 | 4.14e-04 | 4.89e-04 | 1.18x |
| 250 | 100,000 | 15.05 | 4.60e-04 | 5.40e-04 | 1.17x |
| 250 | 500,000 | 13.21 | 5.05e-04 | 5.84e-04 | 1.16x |
| 300 | 10,000 | 22.58 | 2.89e-04 | 3.51e-04 | 1.21x |
| 300 | 50,000 | 19.22 | 3.35e-04 | 3.96e-04 | 1.18x |
| 300 | 100,000 | 18.06 | 3.79e-04 | 4.45e-04 | 1.17x |
| 300 | 500,000 | 15.85 | 4.15e-04 | 4.79e-04 | 1.16x |

## Current SIQS Parameters

Parameter selection uses interpolated lookup table:
- FB_size: 80 (20d) to 75000 (100d)
- M (half-width): 20K (20d) to 35M (100d)
- LP_bound: min(FB[-1]*100, FB[-1]^2)
- T_bits: nb//4-1 (nb>=180) or nb//4-2

| nd | FB | M | B_max | g_bits | u_eff | P(smooth) |
|----|----|----|------|--------|-------|----------|
| 40 | 800 | 300,000 | 11,814 | 75 | 5.54 | 1.71e-03 |
| 45 | 1,200 | 500,000 | 18,689 | 83 | 5.85 | 1.32e-03 |
| 50 | 2,500 | 1,000,000 | 42,595 | 92 | 5.98 | 1.55e-03 |
| 55 | 3,500 | 1,200,000 | 61,985 | 101 | 6.34 | 1.35e-03 |
| 60 | 4,500 | 1,500,000 | 81,954 | 109 | 6.68 | 1.15e-03 |
| 65 | 5,500 | 2,000,000 | 102,372 | 117 | 7.03 | 1.03e-03 |
| 70 | 6,500 | 3,000,000 | 123,155 | 126 | 7.45 | 1.19e-03 |
| 75 | 9,000 | 7,000,000 | 176,376 | 135 | 7.75 | 1.02e-03 |
| 80 | 16,000 | 12,000,000 | 331,961 | 144 | 7.85 | 1.10e-03 |
| 85 | 28,000 | 16,000,000 | 612,263 | 152 | 7.91 | 9.73e-04 |
| 90 | 40,000 | 22,000,000 | 903,192 | 161 | 8.14 | 9.27e-04 |
| 95 | 55,000 | 28,000,000 | 1,276,915 | 169 | 8.33 | 1.02e-03 |
| 100 | 75,000 | 35,000,000 | 1,787,768 | 178 | 8.57 | 1.01e-03 |

## Oracle-Optimized vs Current Parameters

| nd | Current FB | Oracle FB | FB Ratio | Current M | Oracle M | M Ratio |
|----|-----------|----------|----------|----------|---------|--------|
| 40 | 800 | 600 | 0.75x | 300,000 | 55,108 | 0.18x |
| 45 | 1,200 | 500 | 0.42x | 500,000 | 440,871 | 0.88x |
| 50 | 2,500 | 500 | 0.20x | 1,000,000 | 220,435 | 0.22x |
| 55 | 3,500 | 500 | 0.14x | 1,200,000 | 220,435 | 0.18x |
| 60 | 4,500 | 500 | 0.11x | 1,500,000 | 440,871 | 0.29x |
| 65 | 5,500 | 500 | 0.09x | 2,000,000 | 110,217 | 0.06x |
| 70 | 6,500 | 600 | 0.09x | 3,000,000 | 55,108 | 0.02x |
| 75 | 9,000 | 800 | 0.09x | 7,000,000 | 440,871 | 0.06x |
| 80 | 16,000 | 1,400 | 0.09x | 12,000,000 | 440,871 | 0.04x |
| 85 | 28,000 | 2,300 | 0.08x | 16,000,000 | 220,435 | 0.01x |
| 90 | 40,000 | 4,200 | 0.10x | 22,000,000 | 881,743 | 0.04x |
| 95 | 55,000 | 6,800 | 0.12x | 28,000,000 | 1,763,487 | 0.06x |
| 100 | 75,000 | 11,500 | 0.15x | 35,000,000 | 881,743 | 0.03x |

## 60-digit Parameter Sweep

- **Oracle-optimal FB**: 500 (current: 4500)
- **Estimated time at optimal**: 0.0s


## GNFS Oracle Analysis

| nd | d | FB_current | FB_oracle | u_rat | u_alg | P_both |
|----|---|-----------|----------|-------|-------|--------|
| 30 | 3 | 40,000 | 195,000 | 3.14 | 4.97 | 1.16e-04 |
| 35 | 3 | 50,000 | 245,000 | 3.46 | 5.25 | 4.69e-05 |
| 40 | 4 | 80,000 | 365,000 | 3.01 | 5.71 | 8.20e-05 |
| 45 | 4 | 80,000 | 370,000 | 3.25 | 5.96 | 5.37e-05 |
| 50 | 4 | 80,000 | 365,000 | 3.50 | 6.26 | 3.16e-05 |
| 55 | 4 | 80,000 | 370,000 | 3.75 | 6.51 | 1.59e-05 |
| 60 | 4 | 150,000 | 485,000 | 3.84 | 6.57 | 1.47e-05 |
| 65 | 5 | 1,200,000 | 495,000 | 3.12 | 6.78 | 5.96e-05 |
| 70 | 5 | 2,000,000 | 395,000 | 3.20 | 6.88 | 4.37e-05 |
| 75 | 5 | 2,000,000 | 495,000 | 3.34 | 7.02 | 3.71e-05 |

### Degree Selection

| nd | P(d=3) | P(d=4) | P(d=5) | Best d |
|----|--------|--------|--------|--------|
| 35 | 2.75e-04 | 3.69e-04 | 5.40e-04 | 5 |
| 40 | 1.08e-04 | 3.08e-04 | 3.88e-04 | 5 |
| 45 | 5.30e-05 | 1.75e-04 | 2.64e-04 | 5 |
| 50 | 2.89e-05 | 1.09e-04 | 2.15e-04 | 5 |
| 55 | 1.57e-05 | 6.72e-05 | 1.53e-04 | 5 |
| 60 | 7.17e-06 | 4.17e-05 | 1.02e-04 | 5 |
| 65 | 4.88e-06 | 2.59e-05 | 6.75e-05 | 5 |
| 70 | 3.80e-06 | 1.70e-05 | 4.37e-05 | 5 |
| 75 | 3.23e-06 | 1.00e-05 | 3.71e-05 | 5 |

## ECM B1 Optimization

| Factor digits | GMP B1 | Oracle B1 | Ratio | Speedup |
|-------------|--------|----------|-------|--------|
| 20 | 11,000 | 274 | 0.02x | 21.21x |
| 25 | 50,000 | 256 | 0.01x | 99.04x |
| 30 | 250,000 | 256 | 0.00x | 379.96x |
| 35 | 1,000,000 | 256 | 0.00x | 1983.24x |
| 40 | 3,000,000 | 274 | 0.00x | 4532.71x |
| 45 | 11,000,000 | 256 | 0.00x | 18328.04x |
| 50 | 43,000,000 | 274 | 0.00x | 55012.24x |
| 55 | 110,000,000 | 274 | 0.00x | 129244.12x |
| 60 | 260,000,000 | 256 | 0.00x | 360055.66x |

## Practical 60-digit Test

- **N**: 10000000000000000000000000128600000000000000000000000308473 (59d)
- **Current**: FB=4300, M=1440000, time=23.6s, found=True
- **Oracle**: FB=600, M=110217, time=34.9s, found=True
- **Speedup**: 0.68x

## Optimal Parameter Table (40-100d)

| nd | Method | FB | M | u_eff | P(smooth) |
|----|--------|----|---|-------|----------|
| 40 | SIQS | 600 | 55,108 | 5.59 | 1.8e-03 |
| 45 | SIQS | 500 | 440,871 | 6.51 | 1.3e-03 |
| 50 | SIQS | 500 | 220,435 | 7.13 | 1.2e-03 |
| 55 | SIQS | 500 | 220,435 | 7.76 | 1.2e-03 |
| 60 | SIQS | 500 | 440,871 | 8.47 | 9.5e-04 |
| 65 | SIQS | 500 | 110,217 | 9.02 | 9.1e-04 |
| 70 | SIQS | 600 | 55,108 | 9.42 | 9.4e-04 |
| 75 | GNFS d=5 | 4,700,000 | 4,700,000 | 6.90 | 5.1e-05 |
| 80 | GNFS d=5 | 4,050,000 | 4,050,000 | 7.06 | 3.6e-05 |
| 85 | GNFS d=5 | 4,350,000 | 4,350,000 | 7.21 | 2.5e-05 |
| 90 | GNFS d=5 | 4,450,000 | 4,450,000 | 7.38 | 1.8e-05 |
| 95 | GNFS d=5 | 4,150,000 | 4,150,000 | 7.55 | 1.4e-05 |
| 100 | GNFS d=5 | 4,700,000 | 4,700,000 | 7.67 | 1.0e-05 |

## Integration Plan

### SIQS Wrapper (oracle_siqs_wrapper.py)

Drop-in replacement: `from oracle_siqs_wrapper import oracle_siqs_factor`

Changes:
1. `oracle_siqs_params(nd)` replaces hand-tuned table with oracle sweep
2. FB optimized via: minimize `needed/yield` where yield uses `smooth_oracle()`
3. M optimized balancing sieve size vs smoothness probability

### GNFS Changes (not yet wrapped)

1. FB bound from oracle sweep (replace hardcoded table)
2. Degree selection via oracle P_both comparison
3. Sieve threshold from oracle yield prediction
4. LP bound optimization

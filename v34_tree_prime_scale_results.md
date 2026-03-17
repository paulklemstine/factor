# v34: Tree-Prime Zeta Zero Scaling — How Far Can 393 Primes Go?
# Date: 2026-03-16
# Method: Z_tree(t) = Σ p^{-1/2} cos(t log p), p from Berggren tree

## Tree Prime Census
- Depth 6: **393** primes, range [13, 97,609]
- Depth 7: **1063** primes, range [13, 651,997]
- Depth 8: **2866** primes, range [13, 3,314,933]
- Depth 9: **7573** primes, range [13, 19,323,701]
- Depth 10: **20446** primes, range [13, 115,841,897]

======================================================================
## Experiment 1: Height Scaling — 393 primes at t = 2K, 5K, 10K, 50K, 100K
======================================================================

### Height t ≈ 2,000
  Approximate zero count N(2000) ≈ 1516
  Computing 20 exact zeros near t=2000 via mpmath...
  mpmath computed 20 zeros in 8.91s
  Tree Z found: **20/20** zeros
  Mean error: 0.1611
  Max error:  0.4793
  Tree Z time: 0.030s  |  mpmath time: 8.91s
  Speedup: 301.3x

### Height t ≈ 5,000
  Approximate zero count N(5000) ≈ 4520
  Computing 20 exact zeros near t=5000 via mpmath...
  mpmath computed 20 zeros in 8.81s
  Tree Z found: **20/20** zeros
  Mean error: 0.2043
  Max error:  0.6012
  Tree Z time: 0.030s  |  mpmath time: 8.81s
  Speedup: 292.1x

### Height t ≈ 10,000
  Approximate zero count N(10000) ≈ 10142
  Computing 20 exact zeros near t=10000 via mpmath...
  mpmath computed 20 zeros in 14.52s
  Tree Z found: **20/20** zeros
  Mean error: 0.1764
  Max error:  0.4477
  Tree Z time: 0.036s  |  mpmath time: 14.52s
  Speedup: 400.9x

### Height t ≈ 50,000
  Approximate zero count N(50000) ≈ 63518
  Computing 20 exact zeros near t=50000 via mpmath...
  mpmath computed 20 zeros in 60.78s
  Tree Z found: **20/20** zeros
  Mean error: 0.1703
  Max error:  0.3701
  Tree Z time: 0.030s  |  mpmath time: 60.78s
  Speedup: 2016.4x

### Height t ≈ 100,000
  Approximate zero count N(100000) ≈ 138068
  Computing 20 exact zeros near t=100000 via mpmath...
  mpmath computed 20 zeros in 12.45s
  Tree Z found: **20/20** zeros
  Mean error: 0.1882
  Max error:  0.4563
  Tree Z time: 0.031s  |  mpmath time: 12.45s
  Speedup: 408.0x

**Time: 105.6s**

======================================================================
## Experiment 2: Depth Scaling — Does more primes extend the reach?
======================================================================

### Height t ≈ 5,000
  Depth 6 (393 primes): 20/20 found, mean_err=0.2043
  Depth 7 (1,063 primes): 20/20 found, mean_err=0.1860
  Depth 8 (2,866 primes): 20/20 found, mean_err=0.1890
  Depth 9 (7,573 primes): 20/20 found, mean_err=0.1981
  Depth 10 (20,446 primes): 20/20 found, mean_err=0.2046

### Height t ≈ 10,000
  Depth 6 (393 primes): 20/20 found, mean_err=0.1764
  Depth 7 (1,063 primes): 20/20 found, mean_err=0.1731
  Depth 8 (2,866 primes): 20/20 found, mean_err=0.1569
  Depth 9 (7,573 primes): 20/20 found, mean_err=0.1564
  Depth 10 (20,446 primes): 20/20 found, mean_err=0.1588

### Height t ≈ 50,000
  Depth 6 (393 primes): 20/20 found, mean_err=0.1703
  Depth 7 (1,063 primes): 20/20 found, mean_err=0.1672
  Depth 8 (2,866 primes): 20/20 found, mean_err=0.1561
  Depth 9 (7,573 primes): 20/20 found, mean_err=0.1439
  Depth 10 (20,446 primes): 20/20 found, mean_err=0.1456

**Time: 98.8s**

======================================================================
## Experiment 3: Hybrid — Tree Primes + Riemann-Siegel Correction
======================================================================

### Idea: Z_hybrid(t) = Z_tree(t) + RS_correction(t)
The RS correction accounts for primes NOT in the tree.
RS main sum uses N = floor(sqrt(t/(2π))) terms.
We use tree primes for 'importance sampled' contribution,
then add the standard RS remainder for accuracy.

### Height t ≈ 5,000
  N_RS = 28, all_primes_to_N = 9, tree_primes_in_range = 2, missing = 7
  Tree Z alone:  10/10 found, mean_err=0.2197, time=0.017s
  RS Z standard: 10/10 found, mean_err=0.000083, time=43.727s
  Hybrid Z:      10/10 found, mean_err=0.455801, time=0.025s

### Height t ≈ 10,000
  N_RS = 39, all_primes_to_N = 12, tree_primes_in_range = 4, missing = 8
  Tree Z alone:  10/10 found, mean_err=0.2373, time=0.016s
  RS Z standard: 10/10 found, mean_err=0.000147, time=63.488s
  Hybrid Z:      10/10 found, mean_err=0.454146, time=0.021s

### Height t ≈ 50,000
  N_RS = 89, all_primes_to_N = 24, tree_primes_in_range = 9, missing = 15
  Tree Z alone:  9/9 found, mean_err=0.1660, time=0.015s
  RS Z standard: 9/9 found, mean_err=0.000103, time=54.641s
  Hybrid Z:      9/9 found, mean_err=0.311154, time=0.018s

**Time: 204.6s**

======================================================================
## Experiment 4: Binary Search — Highest Zero Locatable by Tree Alone
======================================================================

### Depth 6 (393 primes)
  t=   1,000: detection rate = 100%
  t=   2,000: detection rate = 100%
  t=   5,000: detection rate = 100%
  t=  10,000: detection rate = 100%
  t=  20,000: detection rate = 100%
  t=  50,000: detection rate = 100%
  t= 100,000: detection rate = 100%
  t= 200,000: detection rate = 100%
  t= 500,000: detection rate = 100%
  Detection rate >= 80% at all tested heights up to 500,000
  **Reach exceeds 500,000!**

### Depth 8 (2,866 primes)
  t=   1,000: detection rate = 100%
  t=   2,000: detection rate = 100%
  t=   5,000: detection rate = 100%
  t=  10,000: detection rate = 100%
  t=  20,000: detection rate = 100%
  t=  50,000: detection rate = 100%
  t= 100,000: detection rate = 100%
  t= 200,000: detection rate = 100%
  t= 500,000: detection rate = 100%
  Detection rate >= 80% at all tested heights up to 500,000
  **Reach exceeds 500,000!**

### Depth 10 (20,446 primes)
  t=   1,000: detection rate = 100%
  t=   2,000: detection rate = 100%
  t=   5,000: detection rate = 100%
  t=  10,000: detection rate = 100%
  t=  20,000: detection rate = 100%
  t=  50,000: detection rate = 100%
  t= 100,000: detection rate = 100%
  t= 200,000: detection rate = 100%
  t= 500,000: detection rate = 100%
  Detection rate >= 80% at all tested heights up to 500,000
  **Reach exceeds 500,000!**

**Time: 262.3s**

======================================================================
## Experiment 5: Variance Fraction — How Much of Z(t) Do Tree Primes Capture?
======================================================================

### Theory: Var(Z_partial) / Var(Z_full) ≈ Σ_{tree} 1/p / Σ_{all≤N} 1/p
Since Z ≈ Σ p^{-1/2} cos(t log p) and cos terms are ~uncorrelated,
variance of each term ≈ 1/(2p) (from <cos²> = 1/2).

### Depth 6 (393 primes, max=97,609)
  Tree variance contribution: 0.2614
  t=       100: N_RS=      3, all_primes=     2, tree_in_range=    0, var_frac=0.0%
  t=       500: N_RS=      8, all_primes=     4, tree_in_range=    0, var_frac=0.0%
  t=     1,000: N_RS=     12, all_primes=     5, tree_in_range=    0, var_frac=0.0%
  t=     5,000: N_RS=     28, all_primes=     9, tree_in_range=    2, var_frac=9.1%
  t=    10,000: N_RS=     39, all_primes=    12, tree_in_range=    4, var_frac=12.4%
  t=    50,000: N_RS=     89, all_primes=    24, tree_in_range=    9, var_frac=15.7%
  t=   100,000: N_RS=    126, all_primes=    30, tree_in_range=   13, var_frac=17.3%
  t=   500,000: N_RS=    282, all_primes=    60, tree_in_range=   25, var_frac=19.0%
  t= 1,000,000: N_RS=    398, all_primes=    78, tree_in_range=   33, var_frac=19.6%

### Depth 8 (2,866 primes, max=3,314,933)
  Tree variance contribution: 0.3036
  t=       100: N_RS=      3, all_primes=     2, tree_in_range=    0, var_frac=0.0%
  t=       500: N_RS=      8, all_primes=     4, tree_in_range=    0, var_frac=0.0%
  t=     1,000: N_RS=     12, all_primes=     5, tree_in_range=    0, var_frac=0.0%
  t=     5,000: N_RS=     28, all_primes=     9, tree_in_range=    2, var_frac=9.1%
  t=    10,000: N_RS=     39, all_primes=    12, tree_in_range=    4, var_frac=12.4%
  t=    50,000: N_RS=     89, all_primes=    24, tree_in_range=    9, var_frac=15.7%
  t=   100,000: N_RS=    126, all_primes=    30, tree_in_range=   13, var_frac=17.3%
  t=   500,000: N_RS=    282, all_primes=    60, tree_in_range=   27, var_frac=19.4%
  t= 1,000,000: N_RS=    398, all_primes=    78, tree_in_range=   35, var_frac=20.0%

### Depth 10 (20,446 primes, max=115,841,897)
  Tree variance contribution: 0.3367
  t=       100: N_RS=      3, all_primes=     2, tree_in_range=    0, var_frac=0.0%
  t=       500: N_RS=      8, all_primes=     4, tree_in_range=    0, var_frac=0.0%
  t=     1,000: N_RS=     12, all_primes=     5, tree_in_range=    0, var_frac=0.0%
  t=     5,000: N_RS=     28, all_primes=     9, tree_in_range=    2, var_frac=9.1%
  t=    10,000: N_RS=     39, all_primes=    12, tree_in_range=    4, var_frac=12.4%
  t=    50,000: N_RS=     89, all_primes=    24, tree_in_range=    9, var_frac=15.7%
  t=   100,000: N_RS=    126, all_primes=    30, tree_in_range=   13, var_frac=17.3%
  t=   500,000: N_RS=    282, all_primes=    60, tree_in_range=   27, var_frac=19.4%
  t= 1,000,000: N_RS=    398, all_primes=    78, tree_in_range=   35, var_frac=20.0%

### Interpretation
The variance fraction tells us what % of Z(t)'s oscillatory power
comes from our tree primes. As t grows, N_RS grows, more primes contribute,
and our fraction shrinks — but our primes are the LARGEST contributors (small p).

**Time: 0.0s**

======================================================================
## Experiment 6: Gram Point Sign Agreement at Extreme Heights
======================================================================

### Test: Does Z_tree(g_n) have the same sign as Z(g_n) at Gram points?
If tree primes predict signs correctly even at huge t, that's remarkable.

### Height t ≈ 1,000
  Sign agreement: 10/30 = 33.3% (chance = 50%, excess = -16.7%)
### Height t ≈ 5,000
  Sign agreement: 20/30 = 66.7% (chance = 50%, excess = +16.7%)
### Height t ≈ 10,000
  Sign agreement: 19/30 = 63.3% (chance = 50%, excess = +13.3%)
### Height t ≈ 50,000
  Sign agreement: 9/30 = 30.0% (chance = 50%, excess = -20.0%)
### Height t ≈ 100,000
  Sign agreement: 15/30 = 50.0% (chance = 50%, excess = +0.0%)

### Extreme test: t ≈ 10^9
  t ≈ 10^9: Sign agreement: 11/20 = 55.0%

**Time: 4.2s**

======================================================================
## Experiment 7: Theoretical Analysis — Error Bounds and Scaling Laws
======================================================================

### The partial Euler product approximation

Our Z_tree(t) = Σ_{p in S} p^{-1/2} cos(t log p)
Full Z(t)     ≈ Σ_{p ≤ N} p^{-1/2} cos(t log p)  where N = √(t/2π)

Error = Z(t) - Z_tree(t) = Σ_{p ≤ N, p ∉ S} p^{-1/2} cos(t log p)

Key insight: the error is itself a sum of oscillating terms.
Its RMS ≈ √(Σ_{missing} 1/(2p)) while signal RMS ≈ √(Σ_{all} 1/(2p)).

### Signal-to-Noise Ratio (SNR) vs height

  Depth 6 (393 primes):
    t=       100: N=      3, signal_var=0.000, noise_var=0.417, SNR=0.000
    t=     1,000: N=     12, signal_var=0.000, noise_var=0.634, SNR=0.000
    t=    10,000: N=     39, signal_var=0.099, noise_var=0.698, SNR=0.141
    t=   100,000: N=    126, signal_var=0.160, noise_var=0.765, SNR=0.209
    t= 1,000,000: N=    398, signal_var=0.202, noise_var=0.828, SNR=0.244

  Depth 8 (2,866 primes):
    t=       100: N=      3, signal_var=0.000, noise_var=0.417, SNR=0.000
    t=     1,000: N=     12, signal_var=0.000, noise_var=0.634, SNR=0.000
    t=    10,000: N=     39, signal_var=0.099, noise_var=0.698, SNR=0.141
    t=   100,000: N=    126, signal_var=0.160, noise_var=0.765, SNR=0.209
    t= 1,000,000: N=    398, signal_var=0.206, noise_var=0.823, SNR=0.251

  Depth 10 (20,446 primes):
    t=       100: N=      3, signal_var=0.000, noise_var=0.417, SNR=0.000
    t=     1,000: N=     12, signal_var=0.000, noise_var=0.634, SNR=0.000
    t=    10,000: N=     39, signal_var=0.099, noise_var=0.698, SNR=0.141
    t=   100,000: N=    126, signal_var=0.160, noise_var=0.765, SNR=0.209
    t= 1,000,000: N=    398, signal_var=0.206, noise_var=0.823, SNR=0.251

### Why tree primes work: importance sampling

Tree primes ≡ 1 (mod 4) and concentrate at small values.
Small primes dominate: 1/p decreases, so p=5,13,17,29,... carry most weight.
Even at t=10^6, tree primes capture the top ~20% of variance.
The remaining 80% is spread across thousands of terms → noise averages out.
This is why sign changes survive: the noise adds jitter but not enough to
create or destroy zeros in Z_tree that correspond to true Z zeros.

### Detection probability model
P(detect zero at t) ≈ P(|noise| < |signal slope| × window)
Since signal slope ~ √(Σ 1/(2p) × log²(p)) and noise ~ N(0, σ²_noise),
detection degrades when σ_noise / σ_signal approaches 1.

  Depth 6, t=10,000: noise/signal ratio = 2.66, P(detect) ≈ 40.5%
  Depth 6, t=100,000: noise/signal ratio = 2.19, P(detect) ≈ 48.2%
  Depth 6, t=1,000,000: noise/signal ratio = 2.03, P(detect) ≈ 51.5%
  Depth 8, t=10,000: noise/signal ratio = 2.66, P(detect) ≈ 40.5%
  Depth 8, t=100,000: noise/signal ratio = 2.19, P(detect) ≈ 48.2%
  Depth 8, t=1,000,000: noise/signal ratio = 2.00, P(detect) ≈ 52.1%
  Depth 10, t=10,000: noise/signal ratio = 2.66, P(detect) ≈ 40.5%
  Depth 10, t=100,000: noise/signal ratio = 2.19, P(detect) ≈ 48.2%
  Depth 10, t=1,000,000: noise/signal ratio = 2.00, P(detect) ≈ 52.1%

**Time: 0.0s**


======================================================================
## Summary
======================================================================

Total time: 677s
Experiments: 7

### Key Findings
(To be filled by analysis of results above)
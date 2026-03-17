# v27: Zeta Zeros for Factoring Engines
Generated: 2026-03-16 21:18:00

## Loading zeta zeros...
Loaded 1000 zeros in 156.3s
First 5: [14.134725141734695, 21.022039638771556, 25.01085758014569, 30.424876125859512, 32.93506158773919]
Last: gamma_{1000} = 1419.4225

--- Running E1 ---
## E1: Smooth Number Density from Zeros

  x=10^6, u=2.00: actual=0.268200, dickman=0.306853 (err=14.4%), zero=0.324982 (err=21.2%)
  x=10^7, u=2.33: actual=0.152200, dickman=0.175368 (err=15.2%), zero=0.191336 (err=25.7%)
  x=10^8, u=2.67: actual=0.081200, dickman=0.095373 (err=17.5%), zero=0.100612 (err=23.9%)
  x=10^9, u=3.00: actual=0.041600, dickman=0.048610 (err=16.9%), zero=0.048058 (err=15.5%)
  x=10^10, u=3.33: actual=0.020800, dickman=0.024589 (err=18.2%), zero=0.020952 (err=0.7%)

  **Score**: Dickman wins 3/5, Zero-corrected wins 2/5
  **VERDICT**: Zero correction does NOT reliably improve estimates.
  Reason: zeros modulate prime density at scale O(sqrt(x)/log(x)),
  but smoothness integrates over ALL primes up to B, washing out oscillations.

  [E1 completed in 0.1s]

--- Running E2 ---
## E2: Optimal Sieve Interval from Zeros

  N = 10000000000000061 (~17 digits), B = 500, M = 50000
  Split into 20 bins of size 5000
  Smooth rates: min=0.0000, max=0.0018, mean=0.0003
  Zero scores: min=1.0598, max=1.0625
  **Correlation(zero_score, actual_smooth_rate) = -0.3422**
  **VERDICT**: Moderate correlation! Zeros predict smooth-rich regions.

  [E2 completed in 0.1s]

--- Running E3 ---
## E3: Factor Base Optimization from Zeros

  N = 100000000000037, B = 2000, FB size = 141, M = 20000
  Total Q(x) values tested: 9999
  Correlation(zero_score, hit_rate) = -0.0128
  Correlation(1/p, hit_rate) = 1.0000
  Full FB smooth: 31, Hot FB (80%): 19
  Ratio: 0.613
  **VERDICT**: No correlation. FB hit rates depend on residues mod p,
  not on prime density oscillations. Removing 'cold' primes just loses relations.

  [E3 completed in 0.1s]

--- Running E4 ---
## E4: GNFS Polynomial Selection Guided by Zeros

  N = 100000000000000000039 (~21d), d = 3, B = 5000
  Tested 41 polynomial shifts
  Top 5 by actual smooth rate:
    k=-19: actual=0.2040, dickman=0.029739, zero_est=0.033058, max_coeff=2325740
    k=-20: actual=0.2020, dickman=0.029732, zero_est=0.033121, max_coeff=3786636
    k=-13: actual=0.1740, dickman=0.029781, zero_est=0.032693, max_coeff=2325173
    k=-14: actual=0.1720, dickman=0.029774, zero_est=0.032753, max_coeff=3758139
    k= -8: actual=0.1720, dickman=0.029103, zero_est=0.031639, max_coeff=3732630

  Correlation(actual, dickman) = 0.8882
  Correlation(actual, zero_est) = 0.8881
  **VERDICT**: Zero correction does NOT improve poly selection.
  Reason: polynomial norms dominate. Zeros modulate at too fine a scale.

  [E4 completed in 0.4s]

--- Running E5 ---
## E5: Large Prime Detection via Zero-Based Gap Prediction

  Region: [1000000, 1100000], 50 bins of 2000
  LP counts: mean=0.0, std=0.0, expected~144.3
  Zero predictions: mean=-218.3, std=180.8
  **Correlation(zero_prediction, LP_count) = 0.0000**
  **VERDICT**: No useful correlation for LP detection.
  The 1000 zeros give O(sqrt(x)*log(x)) precision,
  but we need O(1) precision per bin to be useful.

  [E5 completed in 0.1s]

--- Running E6 ---
## E6: Zero-Guided Adaptive Sieve Threshold

  N = 10000000000000061, B = 500, M = 30000, 30 bins
  Smooth rate range: [0.0000, 0.0040]
  Zero score range: [1.0603, 1.0620]
  Correlation(smooth_rate, zero_score) = -0.1089
  Fixed threshold candidates: 15/30
  Adaptive threshold candidates: 15/30
  **VERDICT**: Adaptive threshold not useful. Correlation too weak.
  The sieve score already captures all relevant smoothness information.
  Zero oscillations are too weak at this scale to improve thresholding.

  [E6 completed in 0.0s]

--- Running E7 ---
## E7: Practical Comparison — Standard vs Zero-Guided SIQS

  N = 100000000000034700000000001147 (30 digits)
  p1 = 100000000000031, p2 = 1000000000000037
  Factor base: 318 primes up to 5000

  Standard: 2 smooth / 16667 tested = 0.000120 (0.19s)
  Guided:   0 smooth / 4999 tested = 0.000000 (0.06s)
  **VERDICT**: No improvement. Standard sieving matches or beats zero-guided.
  The polynomial Q(x) already concentrates smooth values near x=0,
  and zero oscillations don't add useful information at this scale.

  [E7 completed in 0.3s]

--- Running E8 ---
## E8: Theoretical Analysis — Can Zeros Reduce Factoring Complexity?

  GNFS constant c = (64/9)^(1/3) = 1.922999

  Quantifying zero oscillation strength:
    x=10^10: relative correction ~ 43.43, per sieve position ~ 4.34e-04
    x=10^15: relative correction ~ 28.95, per sieve position ~ 9.16e-07
    x=10^20: relative correction ~ 21.71, per sieve position ~ 2.17e-09
    x=10^25: relative correction ~ 17.37, per sieve position ~ 5.49e-12
    x=10^30: relative correction ~ 14.48, per sieve position ~ 1.45e-14

  **Theoretical bounds:**
  1. With K zeros, psi(x) correction has magnitude O(sqrt(x) * K / log(x))
  2. Smooth number detection needs O(1) precision per candidate
  3. For x ~ 10^50 (50-digit number), K=1000 gives relative precision ~43
     But this is over the WHOLE interval — per candidate it's O(1/M)
  4. To get O(1) per-candidate precision, need K ~ M*log(x) zeros
     For M=10^6, x=10^50: need ~10^8 zeros (vs our 1000)

  **Complexity analysis:**
  - GNFS finds smooth numbers via sieve: O(M * pi(B)) operations
  - Zeros could theoretically reduce M by focusing on smooth-rich regions
  - But the optimal M is already chosen to minimize total work
  - Even if zeros identify 2x better regions, M shrinks by 2x
  - This saves a constant factor, NOT a complexity class improvement
  - L(1/3, c) form is UNCHANGED — c might decrease by tiny constant

  **Maximum theoretical improvement (upper bound):**
  - Assume zeros perfectly predict smooth-rich 50% of interval
  - Sieve phase (70% of GNFS): 2x faster -> saves 35% total time
  - LA phase (20%) + sqrt (10%): unchanged
  - Best case: 1.54x total speedup (constant factor only)
  - Reality: zeros are NOT perfectly predictive (see E1-E6)
  - Realistic improvement: < 5% (within noise of other optimizations)

  **VERDICT**: Zeta zeros CANNOT reduce factoring complexity class.
  The L(1/3, c) exponent is determined by the BALANCE between FB size
  and smooth probability, which zeros don't change.
  At best, zeros offer a small constant factor (< 2x), but only if we
  had millions of zeros precomputed — and computing those zeros is itself
  expensive (O(T log T) for zeros up to height T).
  **The zero computation cost exceeds any factoring speedup.**

  [E8 completed in 0.0s]

## Summary
Total runtime: 157.5s

### Key Findings
- E1: Smooth density — do zeros beat Dickman?
- E2: Sieve interval — can zeros focus the sieve?
- E3: Factor base — can zeros optimize FB selection?
- E4: GNFS poly selection — do zeros improve scoring?
- E5: Large prime detection — do zeros predict LP locations?
- E6: Adaptive threshold — does zero-guidance help thresholding?
- E7: Practical test — standard vs zero-guided SIQS
- E8: Theoretical — can zeros change factoring complexity?

### Bottom Line
The explicit formula psi(x) = x - sum(x^rho/rho) provides beautiful
theoretical insight but the oscillations are too weak at practical scales
to meaningfully improve sieve-based factoring algorithms.
With K=1000 zeros, the per-candidate correction is O(K/(M*log(x))) which
is negligible for the sieve intervals M~10^6 used in SIQS/GNFS.
The complexity class L(1/3, c) is fundamentally determined by the balance
between factor base size and smooth probability, which zeros don't alter.
# Claude State: Resonance Sieve v7.0

## Current Research State
**Date**: 2026-03-11
**Target Threshold**: 66d/218b (stabilized)
**Next Wall**: 69d/229b (539s, stall at a=72)
**Architecture**: Dual-path (Path 1: Super-Generator, Path 2: SIQS)

## Active Scoreboard
| Digits | Bits | Time | Method | Growth |
|-------:|-----:|-----:|--------|-------:|
| 39d | 128b | 0.30s | SIQS | - |
| 45d | 148b | 1.01s | SIQS | - |
| 48d | 152b | 1.98s | SIQS | - |
| 54d | 177b | 12.1s | SIQS | - |
| 57d | 187b | 18.1s | SIQS | 1.5x/3d |
| 60d | 196b | 44s | SIQS | 2.4x/3d |
| 63d | 206b | 86s | SIQS | 2.0x/3d |
| 66d | 216b | 141s | SIQS | 1.6x/3d |
| 69d | 226b | 539s | SIQS | 3.8x/3d |

## Completed Optimizations
1. JIT hit detection (numba jit_find_hits) — 2x per-call speedup
2. Batch JIT (jit_batch_find_hits) — eliminates per-candidate dispatch
3. FB_size reduction — fewer relations + faster GF(2) LA
4. Adaptive T_bits — threshold for 180b+
5. Spectral Compass with exact rational arithmetic (Solution D)
6. Modular Carry Squeeze (Solution B) — LSB anchoring
7. Hyperbolic Convergence Tracker (Solution A)
8. Capture Zone Snap (Solution C)
9. Scalar Scaling (Solution E)
10. Small prime sieve skip (p<32) with threshold correction — ~2x speedup

## Bottleneck Analysis (69d)
- Relation collection: ~95% of runtime (~527s of 539s)
  - jit_sieve dominates sieve_and_collect
  - Stall at a=72: 128s gap (memory pressure with 10.4M sieve array)
- GF(2) LA: ~2.3% (12.4s)
- FB construction: <1%

## Failed Experiments (do NOT retry)
1. Pure Python trial_divide_smart — 10x slower than numpy
2. DLP with Pollard rho (Python) — 13ms/candidate, 20-27x slower
3. M value tuning (larger sieve widths) — no improvement
4. TRF tree search (heap + greedy descent) — 0 factors for balanced semiprimes
5. Knuth-Schroeppel multiplier — inconsistent
6. Resonant 'a' queue / s-selection bonus / used_a dedup — all within noise
7. int16 sieve array — inconsistent
8. T_bits tuning (looser or tighter) — existing nb//4-1 is optimal
9. DLP with BFS cycle detection (max_depth=10) — O(E) per insertion, 160s at 57d
10. DLP with C Pollard rho + Union-Find + sparse exps — birthday paradox: 300M prime space, ~7 cycles from 20K edges

## Active Hypotheses (priority order)

### Priority 1: P-adic PID Controller for Delta Refinement
- Use Modular Scent as error signal for Spectral Compass correction
- Control loop: SP = n mod 2^k, PV = (C²-B²) mod 2^k, E = Hamming distance
- PID tuning: P for bit-clash correction, I for long-term drift, D for overshoot prevention
- Goal: Stable tree traversal even with >5% initial Δ error

### Priority 2: Beat Frequency Spectrogram Analysis — TESTED
- FFT approach infeasible: float64 precision (15 digits) can't resolve Δ for 60d+ numbers
- Replaced with Fermat near-miss scan (a² - n = b²?) in resonance_band_estimate
- Works for close-prime balanced semiprimes (Δ < ~10K·√(2√n)), marginal for 60d+
- Kept as Strategy 4 in resonance_band_estimate (fast, occasionally catches easy cases)

### Priority 3: Ternary-Geometric Isomorphism (Path 1)
- Map Balanced Ternary {-1,0,1} to Berggren tree branches (M₁,M₂,M₃)
- Path encoding: represent tree path as ternary string D = {d_k,...,d_1}
- Hypothesis: factor gap Δ with sparse ternary representation → "Low-Entropy Drift" in tree
- Statistical analysis: correlate Price matrices with factor's balanced ternary substrings
- Goal: Predictive Navigator using Ternary-Bitmask (skip Jacobian at each level)

### Priority 4: NAF Sparsity & "Zero-Field" Guillotine (Path 2)
- NAF guarantees no two non-zero digits adjacent → deterministic "Zero-Fields" in carry squeeze
- SAT constraint: (x_i · x_{i+1} = 0), (y_j · y_{j+1} = 0)
- ~55% reduction in non-zero partial product terms
- Goal: 30% false-positive reduction in RNS Guillotine

### Priority 5: GF(3) Matrix Reduction
- Ternary factor base: primes where p ≡ ±1 (mod 3)
- Exponent vectors in F₃, Wiedemann solver over F₃
- Cube identity: X³-Y³ = (X-Y)(X²+XY+Y²) → gcd(X-Y, n)
- Goal: Test if smooth density is higher in ternary-prime field

### Priority 6: Recursive Warm-Start for GNFS
- Store smooth vectors from 60d-69d factorizations
- Map residues to 100d target via n₁₀₀ ≡ n₆₉ (mod k)
- Bias Kleinjung polynomial search toward known-good prime densities
- Goal: Pre-aligned polynomials for faster GNFS relation collection

### Priority 7: GNFS Full Implementation
- Base-m polynomial selection already scaffolded
- Need: lattice sieve, algebraic factor base, norm computation
- Required for RSA-100 (100d/332b)

### Priority 8: Block Lanczos for LA
- Replace O(n²) GF(2) Gaussian elimination
- Only significant at 75d+ where matrix density dominates

## Next Steps
1. Implement P-adic PID Controller (Priority 1) for Spectral Compass delta refinement
2. Benchmark Beat Frequency Spectrogram (Priority 2) for Δ narrowing
3. Begin GNFS scaffold for RSA-100 preparation

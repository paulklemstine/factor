# Claude State: Resonance Sieve v7.0

## Current Research State
**Date**: 2026-03-11
**Target Threshold**: 60d/198b (stabilized at ~57s avg)
**Next Wall**: 63d/209b (testing), 66d/219b (testing)
**Architecture**: Dual-path (Path 1: Super-Generator, Path 2: SIQS)

## Active Scoreboard
| Digits | Bits | Time | Method | Growth |
|-------:|-----:|-----:|--------|-------:|
| 39d | 128b | 0.30s | SIQS | - |
| 45d | 148b | 1.01s | SIQS | - |
| 48d | 158b | 2.67s | SIQS | 2.6x/10b |
| 51d | 168b | 6.62s | SIQS | 2.5x/10b |
| 54d | 178b | 11.3s | SIQS | 1.7x/10b |
| 57d | 188b | 25.3s | SIQS | 2.2x/10b |
| 60d | 198b | 57s | SIQS | 2.3x/3d |
| 63d | 208b | 168s | SIQS | 2.9x/3d |
| 66d | 218b | 658s | SIQS | 3.9x/3d |

## Scaling Model (updated)
Growth rate: accelerating — 2.3x→2.9x→3.9x per 3 digits
- 66d stall: a=96→99 gap of 221s (possible GC or memory pressure)
- Extrapolation: 69d ~2000s, 72d ~8000s
- RSA-100 (100d/332b): impractical with SIQS alone, GNFS mandatory
- GNFS crossover point: ~80d (QS ~100000s, GNFS ~1000s estimated)

## Completed Optimizations (this session)
1. JIT hit detection (numba jit_find_hits) — 2x per-call speedup
2. Batch JIT (jit_batch_find_hits) — eliminates per-candidate dispatch
3. FB_size reduction — fewer relations + faster GF(2) LA
4. Adaptive T_bits — tighter threshold for 180b+
5. Spectral Compass with exact rational arithmetic (Solution D)
6. Modular Carry Squeeze (Solution B) — LSB anchoring
7. Hyperbolic Convergence Tracker (Solution A)
8. Capture Zone Snap (Solution C)
9. Scalar Scaling (Solution E)

## Bottleneck Analysis (60d)
- Relation collection: ~85% of runtime (~48s of 57s)
  - trial_divide_smart: ~55% of relation collection
  - jit_sieve + jit_find_smooth: ~10%
  - process_candidate overhead: ~25%
  - polynomial switching: ~10%
- GF(2) LA: ~6% (~3.5s)
- FB construction: ~2%
- JIT warmup: ~5%

## Failed Experiments (do NOT retry)
1. Pure Python trial_divide_smart — 10x slower than numpy
2. DLP with Pollard rho (limit=5000) — overhead exceeds relation gain
3. M value tuning (larger sieve widths) — no improvement

## Active Hypotheses (priority order)
1. **GNFS scaffold for 100d+** — Must implement for RSA-100
   - Base-m polynomial selection already scaffolded
   - Need: lattice sieve, algebraic factor base, norm computation
2. **Hybrid Jump** — SIQS partials feed Super-Generator Δ estimates
   - Extract frequent small primes from SLP data → hint at factor structure
3. **Block Lanczos for LA** — Replace GF(2) Gaussian elimination
   - Current LA: O(n²) with Python big ints
   - Block Lanczos: O(n × weight) with 64-bit word operations
4. **Lattice Snapping (Coppersmith)** — LLL finishing move for Path 1
   - When C ≈ √n and Δ within n^(1/4), snap to exact factor

## Next Steps
1. Profile 63d/66d to measure growth slope
2. If growth > 3x per 3 digits, investigate LA optimization
3. Begin GNFS implementation for 100d+ target
4. Implement Hybrid Jump (SIQS→Super-Generator data bridge)

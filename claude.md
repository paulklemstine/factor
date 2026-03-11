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

## Scaling Model (updated)
Growth rate: 1.5x→2.4x→2.0x→1.6x→3.8x per 3 digits
- 69d stall: a=72 gap of 128s (GC or memory pressure, FB=6700 M=5200000)
- 66d stall was fixed by FB reduction; 69d may need same treatment
- Extrapolation: 72d ~1500-2000s, 75d ~5000-8000s
- GNFS crossover point: ~80d

## Completed Optimizations
1. JIT hit detection (numba jit_find_hits) — 2x per-call speedup
2. Batch JIT (jit_batch_find_hits) — eliminates per-candidate dispatch
3. FB_size reduction — fewer relations + faster GF(2) LA
4. Adaptive T_bits — tighter threshold for 180b+
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
2. DLP with Pollard rho (limit=5000) — overhead exceeds relation gain
3. M value tuning (larger sieve widths) — no improvement

## Active Hypotheses (priority order)
1. **FB tuning for 69d+** — Reduce FB_size/M to avoid memory stalls
2. **Block Lanczos for LA** — Replace GF(2) Gaussian elimination
   - Current LA: O(n²) with Python big ints
   - Block Lanczos: O(n × weight) with 64-bit word operations
3. **GNFS scaffold for 100d+** — Must implement for RSA-100
   - Base-m polynomial selection already scaffolded
   - Need: lattice sieve, algebraic factor base, norm computation
4. **Hybrid Jump** — SIQS partials feed Super-Generator Δ estimates
5. **Lattice Snapping (Coppersmith)** — LLL finishing move for Path 1

## Next Steps
1. Investigate 69d stall — try FB_size reduction (6700→5900)
2. Profile to confirm sieve is still the bottleneck post-optimization
3. Begin GNFS implementation for 100d+ target

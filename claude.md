# Claude State: Resonance Sieve v7.0

## Current Research State
**Date**: 2026-03-11
**Target Threshold**: 66d/218b (stabilized via SIQS)
**GNFS Status**: WORKING — algebraic sqrt solved via Hensel lifting
**Architecture**: Triple-path (Path 1: Super-Generator, Path 2: SIQS, Path 3: GNFS)

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
| 19d | 61b | 8.7s | GNFS | - |
| 21d | 67b | 9.0s | GNFS | - |
| 25d | 81b | 10.3s | GNFS | - |
| 31d | 101b | 107s | GNFS | - |

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
11. **GNFS algebraic sqrt via Hensel lifting** — solved the blocking issue

## GNFS Implementation Status
- **Phase 1**: Polynomial selection (base-m, Murphy alpha) — WORKING
- **Phase 2**: Factor base (rational + algebraic + QC) — WORKING
- **Phase 3**: Line sieve + trial division — WORKING (slow Python sieve)
- **Phase 4**: GF(2) Gaussian elimination — WORKING
- **Phase 5**: Algebraic square root (Hensel lifting) — WORKING
- **Tested**: 19d-31d successfully factored
- **Bottleneck**: Python line sieve too slow for 40d+ (need lattice sieve or C extension)
- **Key insight**: CRT with splitting primes fails (greedy sign selection picks wrong combos).
  Hensel lifting from inert prime avoids sign consistency entirely (only ±1 ambiguity).

## Bottleneck Analysis (69d SIQS)
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
11. GNFS algebraic sqrt via CRT with splitting primes — greedy min-score sign selection fails when true sqrt has large coefficients (~455 digits vs ~18 digit fake minima)

## Active Hypotheses (priority order)

### Priority 1: GNFS Lattice Sieve (Path 3 optimization)
- Current line sieve is O(A × |FB|) per b-line — too slow for 40d+
- Lattice sieve: sieve in (a, b) lattice reduced by each prime
- Expected: 10-100x speedup in relation collection
- Required for RSA-100 (100d/332b)

### Priority 2: Block Lanczos for LA
- Replace O(n²) GF(2) Gaussian elimination
- Only significant at 75d+ where matrix density dominates

### Priority 3: Ternary-Geometric Isomorphism (Path 1)
- Map Balanced Ternary {-1,0,1} to Berggren tree branches (M₁,M₂,M₃)
- Path encoding: represent tree path as ternary string D = {d_k,...,d_1}
- Hypothesis: factor gap Δ with sparse ternary representation → "Low-Entropy Drift" in tree

### Priority 4: NAF Sparsity & "Zero-Field" Guillotine (Path 2)
- NAF guarantees no two non-zero digits adjacent → deterministic "Zero-Fields"
- ~55% reduction in non-zero partial product terms

### Priority 5: GF(3) Matrix Reduction
- Ternary factor base: primes where p ≡ ±1 (mod 3)
- Cube identity: X³-Y³ = (X-Y)(X²+XY+Y²) → gcd(X-Y, n)

## Next Steps
1. Implement GNFS lattice sieve — required for 50d+ GNFS
2. Test GNFS at 40-50d with larger FB and optimized sieve
3. Try remaining hypotheses: Ternary-Geometric (P3), NAF Sparsity (P4)
4. Push toward RSA-100 via GNFS + lattice sieve

# Benchmark Results: SIQS v7.0 + JIT Hit Detection + FB Tuning

Date: 2026-03-11

## Balanced Semiprime Baseline

| Digits | Bits | Time | Status |
|-------:|-----:|-----:|-------:|
| 18 | 58 | 0.10s | PASS |
| 24 | 78 | 0.01s | PASS |
| 30 | 98 | 0.03s | PASS |
| 33 | 108 | 0.09s | PASS |
| 36 | 117 | 0.12s | PASS |
| 39 | 128 | 0.30s | PASS |
| 42 | 138 | 0.57s | PASS |
| 45 | 148 | 0.98s | PASS |
| 48 | 158 | 2.39s | PASS |
| 51 | 168 | 10.24s | PASS |
| 54 | 178 | 11.32s | PASS |
| 57 | 188 | 25.30s | PASS |
| 60 | 197 | 81.43s | PASS |

## Scaling Analysis
- 48d->51d: 4.3x (10b increase)
- 51d->54d: 1.1x (10b increase)
- 54d->57d: 2.2x (10b increase)
- 57d->60d: 3.2x (9b increase)
- Average growth: ~2.5x per 10 bits

## Key Optimizations (this session)
1. JIT hit detection (numba jit_find_hits): 2x per-call speedup in trial_divide_smart
2. Preallocated sieve array: avoids 14MB allocation per polynomial
3. FB_size reduction: smaller FB = fewer relations + faster GF(2) LA
4. Adaptive T_bits: tighter threshold for 180b+ numbers
5. Spectral Compass + Resonance Band estimation for Path 1

## Comparison with previous baseline
| Digits | Before | After | Speedup |
|-------:|-------:|------:|--------:|
| 39d | 0.68s | 0.30s | 2.3x |
| 45d | 3.81s | 0.98s | 3.9x |
| 48d | 8.37s | 2.39s | 3.5x |
| 54d | 49.18s | 11.32s | 4.3x |
| 57d | 115.16s | 25.30s | 4.6x |
| 60d | N/A | 57s avg | NEW |

## Next targets
- 63d/209b (est. ~150-200s at current scaling)
- RSA-100 (100d/332b) requires GNFS transition

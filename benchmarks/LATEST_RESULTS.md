# Benchmark Results: SIQS v7.0 + Smart Trial Division

Date: 2026-03-11

## Balanced Semiprime Baseline

| Digits | Bits | Time | Status |
|-------:|-----:|-----:|-------:|
| 18 | 59 | 0.01s | PASS |
| 24 | 79 | 0.02s | PASS |
| 30 | 99 | 0.04s | PASS |
| 33 | 109 | 0.13s | PASS |
| 36 | 119 | 0.26s | PASS |
| 39 | 129 | 0.68s | PASS |
| 42 | 139 | 1.19s | PASS |
| 45 | 149 | 3.81s | PASS |
| 48 | 159 | 8.37s | PASS |
| 51 | 169 | 14.98s | PASS |
| 54 | 179 | 49.18s | PASS |
| 57 | 189 | 115.16s | PASS |

## Scaling Analysis
- 45d->48d: 2.2x (10b increase)
- 48d->51d: 1.8x (10b increase)
- 51d->54d: 3.3x (10b increase)
- 54d->57d: 2.3x (10b increase)
- Average growth: ~2.4x per 10 bits

## Key Optimizations Applied
1. B_j reduced mod a: fixes SIQS polynomial magnitude (was 37000x too large)
2. Sieve-informed trial division: only check primes whose sieve root matches candidate position (10x speedup)

## Next target: 60d/199b (est. ~250-350s at current rate)

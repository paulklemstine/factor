# Claude State: Resonance Sieve v7.0

## Current Research State
**Date**: 2026-03-13
**Target Threshold**: 66d/218b (stabilized via SIQS)
**GNFS Status**: WORKING — algebraic sqrt solved via Hensel lifting
**ECDLP Status**: C Kangaroo with batch inversion + 2-step comb table
**Architecture**: Triple-path (Path 1: Super-Generator, Path 2: SIQS, Path 3: GNFS)

## R&D Iteration Protocol

### Workflow
1. **Brainstorm** → log ideas to `ecdlp_ideas.md` (or equivalent per-domain file)
2. **Pick highest-impact idea** with lowest risk
3. **Implement in worktree** (`isolation: worktree`) — never modify main directly
4. **Benchmark** (< 5 minutes total, use `bench_kangaroo.py` or inline benchmark)
5. **If faster**: merge to main, commit, push, update scoreboard
6. **If slower or broken**: log failure in "Failed Experiments", discard worktree
7. **Repeat**

### Benchmark Standard (ECDLP)
```
python3 -c "
from ecdlp_pythagorean import ecdlp_pythagorean_kangaroo_c, secp256k1_curve
import time, random
curve = secp256k1_curve()
G = curve.G
random.seed(42)
for bits in [20, 28, 36, 40, 44]:
    times = []
    for trial in range(3):
        k = random.randint(2**(bits-1), 2**bits-1)
        P = curve.scalar_mult(k, G)
        t0 = time.time()
        r = ecdlp_pythagorean_kangaroo_c(curve, G, P, 1<<(bits+1))
        t = time.time() - t0
        times.append(t)
        if r != k: print(f'  {bits}b FAIL')
    print(f'  {bits}b: avg {sum(times)/len(times):.3f}s')
"
```
- Seed 42 for reproducibility
- 3 trials per bit size
- Abort any single trial > 120s

## Active Scoreboard

### Factoring (SIQS/GNFS)
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
| 33d | 108b | 180s | GNFS | - |

### ECDLP (secp256k1 Kangaroo)
| Bits | Time (avg) | Version | Date |
|------|-----------|---------|------|
| 20 | 0.016s | fe_invert | 2026-03-13 |
| 28 | 0.010s | fe_invert | 2026-03-13 |
| 32 | 0.105s | fe_invert | 2026-03-13 |
| 36 | 0.329s | fe_invert | 2026-03-13 |
| 40 | 0.693s | fe_invert | 2026-03-13 |
| 44 | 4.215s | fe_invert | 2026-03-13 |

## ECDLP Improvement Ideas (prioritized)
See `ecdlp_ideas.md` for full details and analysis.

### Ready to Try
1. **uint64 position tracking** — replace mpz_add_ui with uint64_t for searches ≤64b. Expected: 5-10%. Risk: low.
2. **Robin Hood DP hash table** — open-addressing for cache-friendly DP lookups. Expected: 1.1x. Risk: low.
3. **Fermat fe_t inversion** — replace mpz_invert with a^(p-2) using optimized addition chain. Expected: uncertain. Risk: medium.

### Completed (merged)
- **Batch Montgomery inversion** — 1 mpz_invert per step for NK kangaroos. 1.4-1.8x.
- **GMP mpn_ fixed-limb hot path** — fe_t in Phases 1+3. 1.3-1.6x.
- **fe_t batch inversion product tree** — fe_mul replaces mpz_mul in Phase 2. 1.2x.
- **Multi-kangaroo (NK=4)** — adaptive 2 tame + 2 wild. ~1.3x from birthday paradox.
- **Parallel multiprocessing wrapper** — ec_kang_solve_ex with tame_start parameter.

### Failed (do NOT retry)
- **2-step comb table** — no benefit with mpn_ (original gain was mpz_mod elimination, already done by fe_t).
- **GLV 3x DP lookup** — verification overhead (6 scalar mults) negated 3x collision rate. Net: SLOWER.
- **GLV equivalence class walk** — tame/wild in different cosets, no step reduction. 2 fe_mul overhead per step.
- **Jacobian coordinates** — need affine x every step for jump index and DP check. No benefit.
- **Custom 256-bit field arithmetic (__int128)** — GMP's assembly-optimized mpn_* beats C __int128.
- **Pthreads parallelism** — GMP malloc contention + mutex overhead = 10x per-step slowdown.
- **fast_mod_p secp256k1 reduction** — only 6% gain, not worth the complexity/bug risk.
- **8-kangaroo (NK=8)** — total work increases as sqrt(NK), worse single-threaded.
- **Hybrid Kangaroo-BSGS** — reduces to standard BSGS, no algorithmic advantage.

## Completed Optimizations (Factoring)
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
12. **GNFS C sieve extension** — 100x faster sieve via gnfs_sieve_c.c
13. **GNFS batch JIT verify** — single numba call for all candidates
14. **GNFS batch JIT split QC** — vectorized quadratic character computation
15. **GNFS convergence-check Hensel** — no precomputed coeff_bound needed

## GNFS Implementation Status
- **Phase 1**: Polynomial selection (base-m, Murphy alpha) — WORKING
- **Phase 2**: Factor base (rational + algebraic + QC) — WORKING
- **Phase 3**: C sieve + batch JIT verify — WORKING
- **Phase 4**: GF(2) Gaussian elimination — WORKING
- **Phase 5**: Algebraic square root (Hensel lifting) — WORKING
- **Tested**: 21d-33d successfully factored
- **Bottleneck**: LA at 33d+; lattice sieve needed for 49d+

## Failed Experiments — Factoring (do NOT retry)
1. Pure Python trial_divide_smart — 10x slower than numpy
2. DLP with Pollard rho (Python) — 13ms/candidate, 20-27x slower
3. M value tuning (larger sieve widths) — no improvement
4. TRF tree search (heap + greedy descent) — 0 factors for balanced semiprimes
5. Knuth-Schroeppel multiplier — inconsistent
6. Resonant 'a' queue / s-selection bonus / used_a dedup — all within noise
7. int16 sieve array — inconsistent
8. T_bits tuning (looser or tighter) — existing nb//4-1 is optimal
9. DLP with BFS cycle detection — O(E) per insertion, 160s at 57d
10. DLP with C Pollard rho + Union-Find — birthday paradox: too few cycles
11. GNFS CRT with splitting primes — greedy sign selection fails

## Active Hypotheses — Factoring (priority order)

### Priority 1: GNFS Lattice Sieve
- Current line sieve is O(A × |FB|) per b-line — too slow for 40d+
- Expected: 10-100x speedup in relation collection

### Priority 2: Block Lanczos for LA
- Replace O(n²) GF(2) Gaussian elimination
- Only significant at 75d+

## Key Files
- `siqs_engine.py` — SIQS engine (Path 2)
- `gnfs_engine.py` — GNFS engine (Path 3)
- `gnfs_sieve_c.c` / `.so` — C sieve+verify extension
- `ec_kangaroo_c.c` / `.so` — C Pythagorean Kangaroo (batch inv + comb table)
- `ec_bsgs_c.c` / `.so` — C Baby-Step Giant-Step
- `ecdlp_pythagorean.py` — Python ECDLP solvers + parallel wrapper
- `test_bitcoin_search.py` — Bitcoin address key search test
- `ecdlp_ideas.md` — ECDLP improvement ideas log
- `resonance_v7.py` — Unified v7.0 driver
- `benchmark_suite.py` — Standardized benchmarks

## User Preferences
- **Benchmarks < 5 minutes** per iteration cycle
- **Use worktrees** for experimental changes
- **Autonomous R&D loop**: brainstorm → implement → benchmark → merge/discard → repeat
- **Log all ideas** to ideas file, track successes and failures
- **Commit successes immediately**, push to remote

## Environment
- WSL2 with ~7.4GB RAM + 2GB swap
- gmpy2, numba, numpy installed

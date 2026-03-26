# Claude State: Resonance Sieve v7.0

## Current Research State
**Date**: 2026-03-13
**Two active projects**:
1. **Integer Factoring** — SIQS (66d) + GNFS (33d, scaling up)
2. **ECDLP** — secp256k1 Pollard Kangaroo, CPU + CUDA GPU

## R&D Iteration Protocol

### Workflow
1. **Brainstorm** → log ideas to per-domain file (`ecdlp_ideas.md`, etc.)
2. **Pick highest-impact idea** with lowest risk
3. **Implement in worktree** (`isolation: worktree`) — never modify main directly
4. **Benchmark** (< 5 minutes total)
5. **If faster**: merge to main, commit, push, update scoreboard
6. **If slower or broken**: log failure in "Failed Experiments", discard worktree
7. **Repeat**

## User Preferences
- **Benchmarks < 5 minutes** per iteration cycle
- **Use worktrees** for experimental changes
- **Autonomous R&D loop**: brainstorm → implement → benchmark → merge/discard → repeat
- **Log all ideas** to ideas file, track successes and failures
- **Commit successes immediately**, push to remote

## Environment
- WSL2 with ~7.4GB RAM + 2GB swap
- RTX 4050 GPU (20 SMs, Ada Lovelace / sm_89)
- gmpy2, numba, numpy, CUDA installed

---

# Project 1: Integer Factoring (SIQS / GNFS)

**Target**: RSA-100 (100d/330b) milestone, RSA-260 (260d/862b) ultimate
**Architecture**: Triple-path (Path 1: Super-Generator, Path 2: SIQS, Path 3: GNFS)

## Scoreboard

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

## GNFS Implementation Status
- **Phase 1**: Polynomial selection (base-m, Murphy alpha) — WORKING
- **Phase 2**: Factor base (rational + algebraic + QC) — WORKING
- **Phase 3**: C sieve + batch JIT verify — WORKING
- **Phase 4**: GF(2) Gaussian elimination — WORKING
- **Phase 5**: Algebraic square root (Hensel lifting) — WORKING
- **Tested**: 21d-33d successfully factored
- **Bottleneck**: LA at 33d+; lattice sieve needed for 49d+

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

## Key Files (Factoring)
- `siqs_engine.py` — SIQS engine (Path 2)
- `gnfs_engine.py` — GNFS engine (Path 3)
- `gnfs_sieve_c.c` / `.so` — C sieve+verify extension
- `resonance_v7.py` — Unified v7.0 driver
- `benchmark_suite.py` — Standardized benchmarks

## Critical Bug Fixes — Factoring (MUST preserve)
1. **B_j mod a**: `B_j = t_roots[j] * A_j * A_j_inv % a` — MUST reduce mod a
2. **Sieve g(x) not Q(x)**: Sieve g(x)=a*x²+2bx+c where c=(b²-n)/a
3. **T_bits**: nb//4-1 for nb>=180, nb//4-2 otherwise. DO NOT change.
4. **Dynamic s-selection**: Use bisect to find FB range matching target prime size
5. **Do NOT reduce b mod a**: Breaks incremental offset updates in Gray code switching
6. **SGE excess buffer**: Collect 10% more relations than ncols — SGE removes rows/cols unevenly
7. **LP bound**: Use min(B*100, B²) — B² gives LP space too large for SLP combining
8. **Degree selection**: d=3 for <40d, d=4 for 40-65d, d=5 for 65-100d
9. **Poly selection**: Score by norm size at typical sieve points, NOT just skew

---

# Project 2: ECDLP (secp256k1 Discrete Log)

**Target**: Solve ECDLP on secp256k1 for progressively larger bit sizes
**Method**: Pollard's Kangaroo (Lambda) — O(√N) time, O(log N) memory
**Solvers**: CPU (C with GMP fe_t) + GPU (CUDA, RTX 4050)

## Scoreboard

| Bits | CPU (fe_invert) | GPU (CUDA) | Speedup | Date |
|------|----------------|------------|---------|------|
| 20 | 0.016s | — | — | 2026-03-13 |
| 28 | 0.010s | — | — | 2026-03-13 |
| 36 | 0.329s | — | — | 2026-03-13 |
| 40 | 0.693s | 0.13s | 5.3x | 2026-03-13 |
| 44 | 4.215s | 0.27s | 16x | 2026-03-13 |
| 48 | ~37s | 0.73s | 51x | 2026-03-13 |
| 52 | ~100s | ~3s | 33x | 2026-03-13 |
| 56 | — | ~12s | — | 2026-03-13 |
| 60 | — | ~34s | — | 2026-03-13 |
| 64 | — | ~5-10min | — | 2026-03-13 |

### Benchmark Standard (ECDLP)
**All benchmarks MUST have a timeout** (use `signal.alarm` or similar). Never run unbounded.
```
python3 -c "
import signal, time, random
signal.alarm(120)  # 2 min hard timeout
from ecdlp_pythagorean import ecdlp_pythagorean_kangaroo_c, secp256k1_curve
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

## Improvement Ideas
See `ecdlp_ideas.md` for full details and analysis.

### Completed (merged)
- **Batch Montgomery inversion** — 1 mpz_invert per step for NK kangaroos. 1.4-1.8x.
- **GMP mpn_ fixed-limb hot path** — fe_t in Phases 1+3. 1.3-1.6x.
- **fe_t batch inversion product tree** — fe_mul replaces mpz_mul in Phase 2. 1.2x.
- **Multi-kangaroo (NK=4)** — adaptive 2 tame + 2 wild. ~1.3x from birthday paradox.
- **Parallel multiprocessing wrapper** — ec_kang_solve_ex with tame_start parameter.
- **fe_invert via mpn_gcdext** — zero mpz in hot loop. 7.5%.
- **uint64 position tracking** — native uint64 replaces mpz_t for positions.
- **CUDA GPU kangaroo** — 4096 parallel walks on RTX 4050. 10-23x speedup.
- **GPU DP density tuning** — D=(bits-8)/4 reduces post-merge waste. 1.3-5x GPU.
- **GPU adaptive steps-per-launch** — 2048/4096/8192 based on problem size.
- **GPU uint64 collision fix** — unsigned subtraction for 64b+ positions.
- **GPU SM-aware NK** — query SM count, set NK=SM×256 for 100% utilization. ~20% speedup.
- **GPU Lévy spread jump table** — exponential 1-to-10M spread (10^7x). 1.2-1.45x faster at 48-56b.
- **GPU Murmur3 jump hash** — bijective mixing for uniform jump selection from Jacobian X. Reduces tail outliers.
- **GPU Bernstein-Yang divstep inversion** — replaces Fermat (255S+16M) with constant-time divsteps. 1.3-1.6x faster.
- **GPU 128-bit positions** — pos_lo/pos_hi with carry. Enables 68b+ searches. 138 regs, 0 spills.

### Failed (do NOT retry)
- **2-step comb table** — no benefit with mpn_ (already done by fe_t).
- **GLV 3x DP lookup** — verification overhead (6 scalar mults) negated 3x collision rate.
- **GLV equivalence class walk** — tame/wild in different cosets, no step reduction.
- **Jacobian coordinates (CPU)** — need affine x every step for jump index and DP check.
- **Custom 256-bit field arithmetic (__int128)** — GMP's assembly-optimized mpn_* beats C __int128.
- **Pthreads parallelism** — GMP malloc contention + mutex overhead = 10x slowdown.
- **fast_mod_p secp256k1 reduction** — only 6% gain, not worth complexity.
- **8-kangaroo (NK=8)** — total work increases as sqrt(NK), worse single-threaded.
- **Hybrid Kangaroo-BSGS** — reduces to standard BSGS, no algorithmic advantage.
- **GPU shared memory jump table** — __constant__ cache already fast on Ada Lovelace.
- **GPU negation map** — bounded search [0,2^48] in group order 2^256: useless.
- **GPU NORM_INTERVAL=16** — Jacobian X diverges from uniform after 16 steps; 2.2x slower.
- **H2 Price tree jumps** — Fibonacci-spaced hypotenuses, no improvement over baseline.
- **Near-uniform jumps (2.6x spread)** — 5x slower; weak hash needs wide spread.
- **GPU register cap (maxrregcount=96)** — 2x occupancy but spills destroy performance; timeout at 44b.
- **madd-2007-bl EC addition** — 4S+7M+12A vs 3S+8M+6A; extra adds cost more than M→S savings on GPU.
- **Klemstine function for factoring** — continuous Fermat encoding; gradient=0 at all zeros, no computational advantage.
- **H1 Berggren tree hypotenuses** — same distribution as Lévy table; specific values don't matter, only spread shape.
- **H9-H16 (endomorphism, index calculus, attractors, telescoping, etc.)** — all fail for fundamental math reasons. O(√N) is optimal for generic group DLP.

## Key Files (ECDLP)
- `ec_kangaroo_c.c` / `.so` — C Pythagorean Kangaroo (fe_invert, zero mpz hot loop)
- `ec_kangaroo_gpu.cu` / `.so` — CUDA GPU Kangaroo (Jacobian coords, SM-aware NK)
- `ec_bsgs_c.c` / `.so` — C Baby-Step Giant-Step
- `ecdlp_pythagorean.py` — Python ECDLP solvers + parallel wrapper
- `test_bitcoin_search.py` — Bitcoin address key search test
- `ecdlp_ideas.md` — ECDLP improvement ideas log

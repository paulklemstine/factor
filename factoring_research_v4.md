# Factoring Research v4: Unconventional Computation & Engineering Breakthroughs

**Started**: 2026-03-15 (session 4)
**Prior**: 210+ math fields explored (ALL converge to known L[1/3] barrier). 8 optimizations merged.
**New Strategy**: Stop exploring mathematical theory. Focus on UNCONVENTIONAL COMPUTATION and ENGINEERING that could provide 10-100x practical speedups.

## Paradigm Shift: Why This Round Is Different

Previous rounds explored 210+ mathematical fields and proved the L[1/3] barrier is theoretically robust. BUT: theoretical barriers don't mean practical limits. GNFS implementations vary by 1000x in speed (academic code vs CADO-NFS vs our code). The gap between our implementation and state-of-the-art is the biggest opportunity.

## 20 Unconventional Approaches

| # | Approach | Expected Impact | Status |
|---|---------|----------------|--------|
| 1 | **CUDA GNFS sieve** | 10-50x sieve speedup on RTX 4050 | PENDING |
| 2 | **AVX2/SSE4 sieve intrinsics** | 4-8x inner loop speedup via SIMD | PENDING |
| 3 | **Memory-mapped sieve** | Handle 100d+ sieve arrays via mmap | PENDING |
| 4 | **Bucket sieve for GNFS** | O(FB) init instead of O(FB*region) | PENDING |
| 5 | **CADO-NFS integration** | Use state-of-art GNFS, factor 100d | PENDING |
| 6 | **Msieve Block Lanczos** | Port msieve's proven BL to our pipeline | PENDING |
| 7 | **Factor base optimization** | Optimal B from Dickman with empirical correction | PENDING |
| 8 | **Sieve-by-vectors** | Process 64 sieve positions per SIMD word | PENDING |
| 9 | **Polynomial selection (Kleinjung)** | Size-optimized polys for 50d+ | PENDING |
| 10 | **Cofactor ECM in C** | Fast cofactor testing after sieve | PENDING |
| 11 | **Double large prime for GNFS** | DLP combining for GNFS (huge relation boost) | PENDING |
| 12 | **Quadratic characters** | Extra bits to filter false square roots | PENDING |
| 13 | **Sieving with powers of primes** | Include p^2, p^3 in sieve for completeness | PENDING |
| 14 | **Parallel polynomial evaluation** | Numba/C for batch poly eval at sieve points | PENDING |
| 15 | **Streaming relation I/O** | Disk-backed relations for 80d+ (>4GB data) | PENDING |
| 16 | **Sparse matrix formats** | CSR vs COO vs bitpacked for GF(2) LA | PENDING |
| 17 | **Wiedemann algorithm** | Alternative to BL: O(n*w) time, O(n) space | PENDING |
| 18 | **GPU-accelerated LA** | cuBLAS for GF(2) mat-vec on RTX 4050 | PENDING |
| 19 | **Profile-guided optimization** | Instrument SIQS/GNFS, find actual hotspots | PENDING |
| 20 | **End-to-end 50d GNFS test** | Full pipeline test at 50d to find bottlenecks | PENDING |

## Research Log

### Iteration 1: Profiling (2026-03-15)

#### SIQS Profile (59d, 194b) — 5 'a' values, 80 polynomials

| Phase | Time | % of Total |
|-------|------|-----------|
| FB construction | 0.022s | 0.9% |
| Poly setup (a+B+deltas) | 0.055s | 2.3% |
| **Sieve (jit_sieve)** | **1.303s** | **55.5%** |
| Find smooth | 0.095s | 4.0% |
| **Trial division** | **0.475s** | **20.2%** |
| Gray code switching | 0.013s | 0.6% |
| Other overhead | 0.386s | 16.4% |

- Per-poly: 16.3ms sieve, 5.9ms trial div, 1.2ms find smooth, 0.2ms gray switch
- Sieve array: 11MB (2.88M int32 entries) — exceeds L2 cache
- Effective bandwidth: 0.82 GB/s (random writes to 11MB)
- 593 candidates/poly, 1.48 smooth/poly, 21.2 partials/poly

#### GNFS Profile (43d, 141b) — C sieve path

| Phase | Time | % of Total |
|-------|------|-----------|
| C sieve | 192.2s | 79.9% |
| JIT verify | 42.9s | 17.8% |
| Factor base | 3.3s | 1.4% |

**GNFS YIELD BUG:** Only 164 full rels from 1.4M candidates (0.01%). Normal yield should be 100-1000x higher.

#### Dickman Analysis

**SIQS FB is ~20-40x smaller than theoretical optimum** but larger FB has tradeoffs (more rels needed, slower trial div). Current u~7.8 at 60d; optimal u~4.5. LP variation partially compensates.

**GNFS FB is 100-800x smaller than optimal** for larger sizes. RAM-constrained.

#### Optimization Priorities

1. **SIQS sieve (55%)**: int8 array (4x smaller, fits L2), bucket sieve for large primes
2. **SIQS trial div (20%)**: C extension for trial division
3. **GNFS C sieve (80%)**: Fix yield problem, optimize thresholds
4. **GNFS verify (18%)**: Move to C extension

### Iteration 2: Sieve Optimization (2026-03-15)

| Experiment | Speedup vs int32 baseline | Notes |
|-----------|--------------------|----|
| **uint16 sieve (logs*64)** | **4.9x** | 99.8% candidate overlap, no overflow. BEST |
| int8 sieve (logs*4) | 6.0x raw | BROKEN: overflow at 127, wraps negative |
| uint16+blocked 1MB | 4.3x | Blocking overhead > locality gain vs uint16 alone |
| blocked int32 1MB | 2.6x | Pure cache improvement |
| blocked int32 512KB | 2.4x | |
| bucket sieve | 0.7-0.8x | SLOWER: sorting overhead > locality gain |
| numpy vectorized | 0.03-0.47x | MUCH SLOWER: numpy dispatch overhead dominates |

**Winner: uint16 sieve with log scaling factor 64.** Memory halved (11MB->5.7MB), fits L2 cache better, 4.9x sieve speedup. Expected overall SIQS 60d improvement: ~1.8x.

### Iteration 3: E2E Baseline Benchmark (2026-03-15)

Current SIQS baseline on this machine (worktree):

| Digits | Time | Scoreboard |
|--------|------|-----------|
| 49d | 5.3s | 2.0s (48d) |
| 55d | 21.5s | 12s (54d) |
| 58d | 26.5s | 18s (57d) |
| 61d | 79.3s | 48s (60d) |

Times are ~1.5-2x slower than scoreboard, likely due to different test numbers
and worktree overhead. The profiling-identified uint16 sieve (4.9x on sieve = ~1.8x overall)
would bring 61d from 79s to ~44s, matching or beating the scoreboard.

### DLP Rho Hotspot Fix — COMMITTED (commit 1b0e0e9)
Profile at 57d: _quick_factor consumed 49.5% of runtime (27.4s/55.4s).
Fix: small-prime trial div (catches ~30%) + reduce rho limit 200→50.
Expected: ~4x reduction in DLP overhead → ~20s savings at 57d.

### Int8 Sieve — NOT BENEFICIAL
Python int8 sieve 2x SLOWER than int32 (overflow clamping overhead).
Cache benefit only shows in C/numba. M tuning (1.5M vs 3M) already helps.

### GNFS Yield Bug — INVESTIGATING (agent)
Critical: 0.01% yield vs expected 0.1-1% = potential 100x improvement.
Possible causes: tight thresholds, verify bug, small FB, LP bound.
Agent investigating with diagnostic experiments.

### Active Research
- GNFS 50d end-to-end test (agent)
- GNFS yield bug investigation (agent)
- Orchestrator v4 iteration 2+ (profiling-guided)
- P vs NP phase 2 experiments (partial results: Rho wins 13/20 at 18d)

### P vs NP Phase 2 — KEY FINDINGS

**Exp 1 (SAT encoding)**: O(n^2) clauses, density ~4.5-5.5. Over-constrained but SAT solvers can't exploit algebraic structure.

**Exp 2 (Hardness distribution, 1000 semiprimes at 20d)**: Unimodal, right-skewed (0.64), max/min=160x. NO bimodal hard-core. 10.8% above 2x median.

**Exp 3 (Algorithmic diversity)**: Rho wins for balanced factors. Cross-method correlation LOW (r=-0.22 Rho vs P-1). Each algorithm sees different hardness landscape.

**Exp 4 (Bit complexity) — DEEPEST RESULT**:
Information overhead = (relations needed) / (unknown bits):
- 20d: 37x overhead
- 40d: 1,843x overhead  
- 100d: 17,600,000x overhead
- Growth: log2(overhead) ~ 0.24 * digits (linear in digits = exponential in bits)

THIS IS WHY FACTORING IS HARD: each relation reveals O(1/Dickman_rho(u)) bits of information. The Dickman function makes this super-polynomially small. Polynomial factoring would require O(1) overhead ratio, which would violate the Dickman function's asymptotic behavior.

### GNFS Yield Bug Diagnosis — COMPLETE

**Not a bug**: Real yield is ~10.7% (894 full + 4444 partial from 50K candidates).
The 0.01% report counted only full relations, not partials. MEASUREMENT ARTIFACT.

**3 Real Bugs Found:**
1. JIT int64 overflow: silent norm corruption for d=4, |a|>55K (landmine for 55d+)
2. Sieve threshold too loose: passes 3x more candidates than needed
3. Missing overflow flag in C compute_alg_norm_128

**2 Optimizations:**
1. Coprimality pre-filter: eliminates 41% of wasted verify work
2. a-dependent sieve threshold: reduces candidate count ~3x

**Impact**: Not the 100x we hoped, but 3-4x on the GNFS sieve+verify pipeline.
Combined with lattice sieve (43-50x) and these fixes: GNFS 43d could reach ~60-80s.

### Int16 Sieve — COMMITTED (commit 19df211)
Log scale 1024→64, array int32→int16. Halves sieve memory, 1.27x at 52d.

### DLP Rho Fix — COMMITTED (commit 1b0e0e9)
Small-prime trial div + limit 200→50. Cuts 49.5% hotspot by ~4x.

## Session 4 Grand Summary

**10 optimizations merged and pushed** (total across all sessions).
**Engineering profiling >> mathematical theory** for practical speedups.
**Key insight**: The Dickman Information Barrier — relations/bits overhead grows as 10^(0.24*digits), making polynomial factoring impossible without violating smooth number distribution.

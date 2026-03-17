# Factoring Project Memory

## Project Goal
Factor RSA challenge numbers using custom-invented methods. No professional tools.
- Target: RSA-100 (100d/330b) as milestone, RSA-260 (260d/862b) as real target
- User password for sudo: jerusalem

## Architecture: Resonance Sieve v7.0
- **Path 1**: VSDD Sniper + Super-Generator (Pythagorean tree pathfinding + Spectral Compass)
- **Path 2**: SIQS engine (sub-exponential sieve, replaced MPQS)
- **Path 3**: GNFS engine (for 40d+, sub-exponential, now working end-to-end)
- **ECM bridge**: For medium (unbalanced) factors up to ~54 digits

## Critical Bug Fixes (MUST preserve)
1. **B_j mod a**: `B_j = t_roots[j] * A_j * A_j_inv % a` — MUST reduce mod a
2. **Sieve g(x) not Q(x)**: Sieve g(x)=a*x²+2bx+c where c=(b²-n)/a
3. **T_bits**: nb//4-1 for nb>=180, nb//4-2 otherwise. DO NOT change.
4. **Dynamic s-selection**: Use bisect to find FB range matching target prime size
5. **Do NOT reduce b mod a**: Breaks incremental offset updates in Gray code switching
6. **SGE excess buffer**: Collect 10% more relations than ncols — SGE removes rows/cols unevenly
7. **LP bound**: Use min(B*100, B²) — B² gives LP space too large for SLP combining
8. **Degree selection**: d=3 for <40d, d=4 for 40-65d, d=5 for 65-100d
9. **Poly selection**: Score by norm size at typical sieve points, NOT just skew. Low-skew polys can break Hensel sqrt.

## SIQS Performance Ceiling
- **Python SIQS is at its limit for 66d+** — sieve is 95% of runtime, DRAM bandwidth bound
- Next breakthrough: GNFS for 80d+ (now unblocked)

## Current Scoreboard
| Digits | Time | Method |
|--------|------|--------|
| 48d | 2.0s | SIQS |
| 54d | 12s | SIQS |
| 57d | 18s | SIQS |
| 60d | 48s | SIQS |
| 63d | 90s | SIQS |
| 66d | 244s | SIQS |
| 69d | 538s | SIQS |
| 43d | 352s | GNFS d=4 |
| 44d | 264s | GNFS d=4 |

## ECDLP Solvers (secp256k1) — Updated 2026-03-13
| Bits | Kangaroo (batch+comb) | Old Kangaroo | Speedup |
|------|----------------------|-------------|---------|
| 28 | 0.060s | 0.12s | 2x |
| 36 | 0.38s | 1.21s | 3.2x |
| 40 | 1.96s | 5.67s | 2.9x |
| 44 | 3.88s | ~20s | 5.2x |
| 48 | ~30s (est) | ~170s | ~5.7x |

- See [ecdlp_kangaroo_fixes.md](ecdlp_kangaroo_fixes.md) for critical bug fixes
- See [ecdlp_improvement_plan.md](ecdlp_improvement_plan.md) for optimization roadmap

## Key Files
- `siqs_engine.py` — SIQS engine (Path 2), primary workhorse
- `gnfs_engine.py` — GNFS engine (all 5 phases + SGE + DLP + SLP)
- `gnfs_sieve_c.c` / `.so` — C sieve+verify extension (__int128, Miller-Rabin)
- `b3_mpqs.py` — B3-MPQS engine (Pythagorean parabolic QS)
- `pyth_b3_sieve.py` — Original B3 sieve prototype (LA broken)
- `ec_kangaroo_c.c` / `.so` — C Pythagorean Kangaroo (Berggren hypotenuse jumps)
- `ec_bsgs_c.c` / `.so` — C Baby-Step Giant-Step with GMP hash table
- `ecdlp_pythagorean.py` — Python ECDLP solvers (FastCurve, GLV-BSGS, kangaroo)
- `resonance_v7.py` — Unified v7.0 driver
- `benchmark_suite.py` — Standardized benchmarks

## GNFS Status — WORKING END-TO-END
- **All phases**: poly selection, FB, C line sieve, SLP/DLP combining, SGE, GF(2) Gauss, Hensel sqrt
- **Polynomial selection**: Search ±1000 around m0, score by norm size at typical sieve points
- **Two-phase sieve**: Phase 1 (b=1..5000, A=2x) for high yield at small b; Phase 2 (normal A, batch 500)
- **SGE**: reduces 21K→15K matrix (~30% reduction)
- **SLP combining**: ~50% of relations. LP bound = 100*B optimal for combining rate
- **C verify optimizations**: int64 fast path for rational norms, early exit on rem < p
- **Sieve thresholds**: max(600, 1000-nd*5), max(500, 850-nd*5) — higher = fewer cands, better throughput
- **49d UNSOLVED**: FB=100-200K insufficient. Polynomial coefficients too large for smoothness.
- **Next needed**: larger FB (300K+) for 49d+, lattice sieve, Block Lanczos for O(n²) LA

## B3 Parabolic Discovery — IMPLEMENTED
- See [b3_parabolic_discovery.md](b3_parabolic_discovery.md) for research doc
- See [feedback_modinverse.md](feedback_modinverse.md) for critical bug fix
- B3 = [[1,2],[0,1]] is parabolic → arithmetic progressions → QS polynomials
- Pure B3 has perfect-square a → trivial GCD; fix: CRT square-free a
- **B3-MPQS engine**: `b3_mpqs.py`, works up to 44d (212s)
- B3-MPQS scoreboard: 20d=0.0s, 29d=0.9s, 35d=4.7s, 39d=70s, 44d=212s

## User Preferences
- **Benchmarks < 5 minutes** per iteration cycle (keep loop moving)
- **Use worktrees** for experimental changes
- **Autonomous R&D loop**: brainstorm → implement in worktree → benchmark → merge/discard → repeat
- **Log all ideas** to ideas file (ecdlp_ideas.md), track successes AND failures
- **Commit successes immediately**, push to remote
- Teams OK now (user requested team agents for parallel R&D)
- **RAM limit**: WSL2 VM will crash if >5GB RAM used — keep arrays bounded

## Pythagorean Tree Factoring Research (NEW — 2026-03-14)
- See [pyth_tree_factoring.md](pyth_tree_factoring.md) for full details
- RL agent navigates (m,n) tree, checks gcd(m²-n², N) > 1
- Best result: 87% branch prediction, generalizes beyond training size
- Wall at 24b factors — scent gradient too weak

## Environment
- WSL2 with ~7.4GB RAM + 2GB swap (may need memory increase)
- gmpy2, numba, numpy installed

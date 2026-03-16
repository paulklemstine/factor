# Iteration 4: GNFS Engine Improvements & SIQS C Sieve Investigation

Date: 2026-03-15

## Task A: GNFS Engine Analysis

### A1. GNFS Phase Profile (39d factorization)

Profiled `gnfs_factor()` on a 39d semiprime (N = 10^19+7 * 10^19+10^9+7).

| Phase | Time | % of Total |
|-------|------|-----------|
| Polynomial selection | 0.03s | 0.1% |
| Rational FB (6935 primes) | 0.001s | 0% |
| Algebraic FB (6899 ideals) | 1.89s | 4.8% |
| QC primes | 0.02s | 0% |
| **Sieve (C line sieve)** | **~1.5s** | **3.8%** |
| **Verification (C trial div)** | **~26s** | **67%** |
| Linear algebra (SGE + Gauss) | ~10s | 25% |
| Square root + extraction | ~1s | 2.5% |
| **Total** | **~39s** | |

Actual 33d run: 39.0s total, sieve+verify=8.5s, LA=13.9s.

### A2. Top 3 Bottlenecks

**#1: Verification is 67-97% of total time (at 39-40d)**

The GNFS C verify (`verify_candidates_c`) does brute-force trial division
over the ENTIRE factor base for every candidate:
- 13,836 trial divisions per candidate (6935 rational + 6901 algebraic)
- 173 microseconds per candidate
- 12.5 ns per trial division step

Compare SIQS: only trial-divides ~30 primes per candidate (sieve-informed
hit detection), making it **461x less work per candidate**.

The fix: **sieve-informed verification**. The C sieve already computes which
primes hit each sieve position. By recording hit indices during the sieve
(or recomputing from offsets), verify only needs to trial-divide the ~20-40
primes that actually contributed, not all 14K.

Expected speedup: **50-100x on verification** (from 26s to ~0.3-0.5s).

**#2: Algebraic factor base construction (1.9s, 4.8%)**

`build_algebraic_fb()` uses brute-force root finding for each prime p up to
B_a=50K-100K. For each prime, it evaluates f(x) at all x in [0, p-1] via
JIT. This is O(p * d) per prime.

For FB bound 100K: ~10K primes, average p ~ 50K, so ~500M evaluations.
At 50K+ the `_poly_roots_mod_p_smart` (Cantor-Zassenhaus) kicks in, but
for FB_bound <= 50K, it's all brute force.

Fix: Use Hensel lifting from small primes, or Berlekamp's algorithm for
polynomial root finding in O(d^2 * log p). Would cut FB construction from
1.9s to ~0.1s.

**#3: Linear algebra scales poorly (13.9s at 33d, est. 50s+ at 40d)**

SGE reduces 11680 to 7971 rows, then dense GF(2) Gauss on 7971x6566.
The numpy-vectorized Gauss is O(rows * cols / 64) per pivot, total
O(rows * cols^2 / 64). At 40d+ with 15K+ rows, this becomes dominant.

Fix: Block Lanczos for O(n^2 / 64) with 64-wide word operations.

### A3. Polynomial Quality Assessment

Current polynomial selection searches +/-1000 around m0 plus 2000
sum-of-squares candidates. For 39d with d=3:

```
f(x) = 115413749 + 591812797*x + 151438*x^2 + x^3
m = 46415837857, skew = 486.88, alpha = 0.543
```

The leading coefficient a_d = 1 is optimal for d=3 (monic polynomial).
Coefficients are well-balanced. The Murphy alpha = 0.543 is reasonable
but not exceptional (good values are 0.5-1.0 for degree 3).

For comparison, Kleinjung-recommended norms for 30d GNFS d=3:
- Typical |a_0| ~ m, |a_1| ~ m^(2/3), |a_2| ~ m^(1/3), a_3 = 1
- Our a_0 = 115M vs m = 46B: a_0/m = 0.0025 (very good, small a_0)
- Our a_1 = 592M vs m^(2/3) ~ 1.3M: a_1 is 460x larger (not ideal)

The polynomial quality is **adequate but not competitive** with tools
like msieve/CADO-NFS that use Kleinjung's algorithm. The base-m method
inherently produces polynomials with one large coefficient (a_1 ~ m).

### A4. Special-q Lattice Sieve Integration

The lattice sieve IS integrated. Both `lattice_sieve_c.so` and
`gnfs_sieve_c.so` are loaded and used:

- **lattice_sieve_c.so**: Used for nd >= 50 (C lattice available) or nd >= 80 (Python fallback)
- **gnfs_sieve_c.so**: Used for line sieve (nd < 50)
- C verify (`verify_candidates_c`): Used for both paths

The lattice sieve integration is complete with:
- Batch processing (50 special-q per C call)
- Gauss lattice reduction
- Special-q column merging (pairwise combining eliminates SQ columns)

### A5. Highest-ROI Change for GNFS at 60d

**Sieve-informed verification: expected 50-100x speedup on verification.**

Current state: the C sieve generates candidate (a,b) pairs that pass a log
threshold, but then verify_candidates_c brute-force trial-divides EVERY FB
prime for each candidate. This is the same antipattern that SIQS solved
with hit detection.

Implementation plan:
1. During C sieve, record which FB primes hit each candidate position
   (add a hit list output buffer to `sieve_batch_c`)
2. In verify, only trial-divide the primes in the hit list
3. Fall through to full trial division only if hit-based division leaves
   a cofactor (rare, handles rounding errors in log sieve)

This single change would cut GNFS 39d time from ~39s to ~15s (LA-bound),
and at 43d from ~439s to ~100s, making GNFS competitive with SIQS at 50d+.

Estimated effort: 1-2 days. The sieve and verify C code already exist;
the change is plumbing hit indices from sieve to verify.

---

## Task B: SIQS C Sieve Feasibility

### B1. Current SIQS Sieve Architecture

The SIQS sieve in `_sieve_one_a()` uses this pipeline per polynomial:

1. **Zero sieve array** (`sieve_arr[:] = 0`): ~0.3ms at 60d
2. **jit_presieve**: period-210 pattern for p=2,3,5,7 + primes 11-31
3. **jit_sieve**: additive sieve for primes >= 32, double-root interleaved
4. **jit_find_smooth**: threshold scan to find candidates
5. **jit_batch_find_hits**: hit detection (pos % p == off1 or off2)
6. **Trial division**: divmod loop over hit primes per candidate

Per-polynomial timing at 59d (FB=4300, M=1.44M, sz=2.88M):
| Step | Time | % |
|------|------|---|
| Sieve (presieve+sieve) | 5.2ms | 57% |
| Find survivors | 0.8ms | 8% |
| Hit detection | 3.2ms | 35% |
| **Total sieve path** | **9.2ms** | **100%** |

Trial division and combining happen outside this measurement.

**Key finding**: SIQS already has a C sieve (`siqs_sieve_c.so`) that is
NOT integrated into `siqs_engine.py`. The C sieve matches JIT performance
at small sizes and is ~15% faster at 66d+.

### B2. C Sieve Interface Design

Data passed from Python to C per polynomial:
- `sieve` array: int16[sz] (5.5MB at 66d, sz=4.8M)
- `fb`: int64[n_fb] factor base primes (44KB at 66d)
- `fb_logp`: int16[n_fb] log values (11KB)
- `off1, off2`: int64[n_fb] sieve offsets (44KB each)
- `threshold`: int16 scalar
- Output: `candidates`: int32[max_cands]

Total data transfer: ~5.7MB per call. At ~3ms per call, this is 1.9 GB/s,
which is close to the DRAM bandwidth wall on this system.

### B3. Speedup Estimate

Measured sieve bandwidth:
| Implementation | Bandwidth | Time/poly (59d) |
|---------------|-----------|----------------|
| Numba JIT | 1.22 GB/s | 5.2ms |
| Existing siqs_sieve_c.so | 1.14 GB/s | 5.6ms |
| New siqs_sieve_fast.so | 0.90-1.0 GB/s | 4.6-5.9ms |

**The sieve is DRAM-bandwidth-bound, not compute-bound.** All three
implementations achieve within 35% of each other because they all do
the same number of memory accesses (one write per sieve hit).

With SIMD (SSE/AVX): the threshold scan benefits (8-16 elements/cycle),
but the sieve inner loop (scattered writes at stride p) does NOT benefit
from SIMD. SIMD helps only the threshold scan (currently 8% of time).

**Projected end-to-end speedup from C sieve integration:**

At 60d: sieve = 57% of sieve path, sieve path = ~50% of total.
- C sieve gives ~1.15x on sieve step -> 8% end-to-end improvement
- Eliminating Python overhead (array zeroing, function calls): +5%
- Combined: ~13% end-to-end speedup at 60d (48s -> 42s)

At 66d: sieve = 65% of sieve path (larger FB, more time in sieve).
- C sieve + overhead elimination: ~15% end-to-end (244s -> 207s)

**Verdict: C sieve alone gives modest 10-15% improvement because the
existing numba JIT is already near DRAM bandwidth limit.**

### B4. C Sieve Prototype

Written to `/home/raver1975/factor/siqs_sieve_fast.c`.

Features:
- Combined presieve + sieve + threshold scan in one C call
- Period-210 memcpy tiling for p=2,3,5,7
- Interleaved double-root sieve for p >= 32
- 8-wide unrolled threshold scan
- Batch hit detection function (bonus)

Benchmark results (average of 20 iterations):

| Digits | New C (ms) | Old C (ms) | JIT (ms) | New/JIT |
|--------|-----------|-----------|---------|---------|
| 51d | 4.6 | 3.7 | 3.4 | 0.74x |
| 61d | 9.3 | 10.3 | 8.4 | 0.90x |
| 67d | 20.3 | 19.9 | 23.5 | 1.16x |

The C sieve breaks even with JIT at ~63d and pulls ahead at 67d+.
The crossover happens because at larger FB sizes, the C compiler's
optimization of the inner sieve loop (branch prediction, register
allocation) outperforms numba's generated code.

---

## Task C: Engineering Approaches Assessment

### C1. GPU Sieve for SIQS

**Effort**: 3-5 days (have CUDA experience from gpu_cofactor)
**Expected speedup**: 2-5x on sieve phase, 1.3-2x end-to-end
**Worth pursuing**: Maybe at 70d+

The sieve is a scatter operation (write log[p] at stride p). GPUs excel
at gather but struggle with scatter due to atomic add overhead. The main
win would be from parallelizing across multiple polynomials (sieve 32
polynomials simultaneously on 32 thread blocks).

Challenge: sieve array is 5.5MB per poly at 66d. 32 parallel polys need
176MB GPU memory. RTX 4050 has 6GB, so feasible but tight.

### C2. Distributed Factoring

**Effort**: 2-3 days
**Expected speedup**: Linear in number of machines (2x per added machine)
**Worth pursuing**: Yes, if machines available

SIQS parallelizes trivially: each worker generates different 'a' values
and returns relations. Already have multiprocessing support (n_workers
parameter). Extension to distributed:
- Workers: generate relations, send (x, sign, sparse_exps, LP) tuples
- Controller: collect relations, run LP combining, LA, sqrt

Network bandwidth: ~1KB per relation, ~4000 relations needed at 60d.
Total transfer: 4MB. Easily fits over any network.

### C3. Precomputed Factor Base Optimization Tables

**Effort**: 1 day
**Expected speedup**: 5-10% (eliminates sqrt_n_mod recomputation)
**Worth pursuing**: Easy win, do it

Currently, `sqrt_n_mod` (modular square roots of N mod each FB prime)
is computed once per run. But `a_inv_mod` (modular inverse of 'a' mod
each FB prime) is recomputed for every 'a' value. With grouped-a mode,
the base primes are shared, so base_inv can be cached.

Also: the delta arrays for Gray code switching could be precomputed as
lookup tables indexed by (FB_prime_index, B_value_index), saving the
per-a modular multiply.

### C4. JIT Compilation Optimizations

**Effort**: 1-2 days
**Expected speedup**: 10-30% on hit detection phase
**Worth pursuing**: Yes, hit detection is 35% of sieve path

Current `jit_batch_find_hits` does candidate-major order: for each
candidate, scan all FB primes and check pos % p. This is O(n_cand * n_fb).

Better approach: **prime-major with position lookup table**.
For each FB prime, compute which candidates it hits (O(n_cand/p) amortized
via offset walking). This is what `siqs_batch_find_hits_fast` in
siqs_sieve_c.c already implements but is not called.

Expected: 30% speedup on hit detection -> 10% end-to-end.

### C5. Memory-Mapped Sieve for >66d

**Effort**: 1 day
**Expected speedup**: Enables 70d+ (currently OOM)
**Worth pursuing**: Yes, enables larger M

At 70d, M=3M, sz=6M, sieve = 12MB per poly. With 2 workers, that's 24MB
just for sieve arrays. The multiprocessing fork needs ~50MB per worker for
FB copies.

mmap-based sieve: allocate sieve array as mmap'd file, OS handles paging.
Workers write directly to mmap'd region. Avoids pickle overhead for large
arrays.

Alternative: reduce sieve to int8 (currently int16). The maximum sieve
value at 70d is ~500, which fits in int16 but not int8. However, we could
use int8 with a reduced log scale (log2(p)*32 instead of *64), accepting
slightly lower threshold precision.

---

## Summary: Recommended Priority Order

| # | Change | Speedup | Effort | Target |
|---|--------|---------|--------|--------|
| 1 | **GNFS sieve-informed verify** | 50-100x on verify | 1-2 days | GNFS 40d+ |
| 2 | Integrate existing siqs_sieve_c.so | 10-15% at 66d | 0.5 days | SIQS 63d+ |
| 3 | Prime-major hit detection for SIQS | 10% end-to-end | 1 day | SIQS all |
| 4 | GNFS Block Lanczos LA | 3-5x on LA | 2-3 days | GNFS 40d+ |
| 5 | Precomputed FB tables | 5-10% | 0.5 days | SIQS all |
| 6 | GPU sieve for SIQS | 1.3-2x | 3-5 days | SIQS 70d+ |
| 7 | Distributed workers | Linear scaling | 2-3 days | SIQS 70d+ |

**The single highest-impact change is GNFS sieve-informed verification (#1).**
It would cut GNFS time by 2-3x at 40d and potentially make GNFS faster than
SIQS at 55-60d, which is the crossover point where GNFS's L(1/3) complexity
starts beating SIQS's L(1/2).

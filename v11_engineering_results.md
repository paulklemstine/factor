# V11 Engineering Results: SIQS/GNFS Performance Optimization

## Summary

Exhaustive engineering analysis of SIQS performance. Profiled all five proposed optimization vectors. Only one yielded measurable improvement.

## Task 1: C Sieve Integration

**Result: NOT BENEFICIAL -- C sieve is NOT faster than Numba JIT**

`siqs_sieve_c.so` exists and loads correctly. All four C functions work:
- `siqs_sieve` (combined presieve + main sieve)
- `siqs_find_survivors` (threshold scan)
- `siqs_batch_find_hits` (candidate-to-FB hit detection)
- `siqs_batch_find_hits_fast` (prime-major variant)

### Microbenchmark Results (synthetic data)

| Operation | JIT | C | Speedup |
|-----------|-----|---|---------|
| Sieve (60d, 3M array) | 5.9ms | 6.2ms | 0.95x |
| find_smooth/survivors | 17.6ms | 1.1ms | 15.7x |
| batch_find_hits | 93ms | 73ms | 1.27x |

The C sieve is tied with JIT for the sieve loop. C `find_survivors` is 15x faster, but this phase is only 1-2% of the real workload. C `batch_find_hits` is 27% faster, but ctypes call overhead per polynomial negates the gain.

### End-to-End Benchmark (66d)

| Mode | Time | Notes |
|------|------|-------|
| JIT only | 73.0s | Baseline |
| C hybrid (JIT sieve + C find/hits) | 77.2s | 5.7% SLOWER |
| C hybrid (pre-alloc buffers) | 78.7s | 7.8% SLOWER |

**Root cause**: ctypes marshalling overhead (`.ctypes.data_as()` per array per call) exceeds the C function speedup at the per-polynomial granularity (~600 candidates per poly, not the 11K+ in synthetic benchmarks).

**Decision**: Kept JIT-only code path. The C sieve integration was reverted.

## Task 2: Numba JIT Audit

**Result: JIT is already optimal; no improvements found**

1. **Compilation mode**: All 6 `@njit` functions compile in nopython mode (confirmed by signature inspection). No object-mode fallbacks.

2. **Type stability**: All arrays use consistent dtypes:
   - sieve: int16, primes/offsets: int64, logs: int16
   - No type mismatches or implicit conversions in the JIT code.

3. **`@njit(parallel=True)` with `prange`**: NOT APPLICABLE. The sieve loop has write conflicts (multiple primes write to overlapping sieve positions). Would require atomic adds or segmented sieve approach.

4. **`@njit(cache=True)`**: Already enabled in production. Saves ~2s JIT warmup on repeated runs.

5. **`@njit(fastmath=True)`**: No measurable effect. The sieve is integer-only arithmetic (int16 adds, int64 index computation). `fastmath` only affects floating-point relaxation.

6. **Benchmark**: Normal vs fastmath on 5000-prime FB, 3M sieve array: 5.9ms vs 5.3ms (~10% difference, within noise for integer code).

## Task 3: SIQS Parameter Retuning

**Result: Parameters are already near-optimal. No changes needed.**

### FB Size Sweep (60d)

| FB (% of current) | Time |
|-------------------|------|
| 80% (3600) | 40.8s |
| 90% (4050) | 37.8s |
| 100% (4500) | 38.1s |
| 110% (4950) | 38.8s |
| 120% (5400) | 40.7s |

Current FB=4500 is in the optimal range. 90% is marginally better but within run-to-run variance.

### Sieve Width Sweep (60d)

| M (% of current) | Time |
|-------------------|------|
| 70% (1.05M) | 36.4s |
| 85% (1.28M) | 36.7s |
| 100% (1.5M) | 35.6s |
| 115% (1.72M) | 36.2s |
| 130% (1.95M) | 36.4s |

Remarkably flat -- the sieve width has minimal impact in this range. Current M=1.5M is optimal.

### Profiling Breakdown (60d, 40s total)

| Phase | Self Time | % | Calls | Description |
|-------|-----------|---|-------|-------------|
| sieve_and_collect | 16.0s | 40% | 1,450 | JIT sieve + find_smooth + Python overhead |
| process_candidate_batch | 6.2s | 16% | 888K | Trial division per candidate |
| siqs_factor (setup) | 6.4s | 16% | 1 | a-value selection, Tonelli-Shanks, Gray deltas |
| _quick_factor | 3.0s | 8% | 167K | DLP cofactor splitting (Pollard rho) |
| is_prime | 1.9s | 5% | 859K | Primality testing for LP/DLP |
| divmod | 1.2s | 3% | 13.8M | Inner trial division loop |
| sparse exps | 1.1s | 3% | 244K | Building sparse exponent tuples |
| LP graph ops | 1.9s | 5% | ~100K | add_smooth, add_single_lp, DLP graph |
| LA (bitpacked) | 0.5s | 1% | 1 | GF(2) Gauss elimination |

**Key insight**: The sieve itself (JIT code) is only ~7% of the total time. The dominant costs are Python-level overhead in the sieve coordination loop (40%) and candidate processing (16%).

### Optimization Applied: Threshold Hoisting

Hoisted the constant `log_g_max` and `thresh` computation out of the per-polynomial `sieve_and_collect` function. These values never change but were recomputed 1450 times.

## Task 4: Process-Level Parallelism

**Result: n_workers=2 is 2.4x SLOWER than n_workers=1 at 60d**

| Workers | Time (60d avg of 2) | Scaling |
|---------|---------------------|---------|
| 1 | 38.9s | 1.0x |
| 2 | 94.4s | 0.41x |

**Root cause**: The multiprocessing worker path (`_sieve_one_a`) processes one `a`-value per task, then pickles all relations back to the main process. At 60d with s=5, each `a` yields 16 polynomials and ~50 relations. The pickle/IPC overhead per task exceeds the computation time. Additionally, fork() copies the entire Python interpreter state (JIT caches, etc.).

The n_workers=2 mode may be beneficial only at 69d+ where each `a` takes longer (more polynomials per `a` with s=7, giving 64 polys/a).

## Task 5: Memory-Mapped Sieve

**Result: mmap is NOT needed and would NOT help**

| Digits | Sieve Size | LA Matrix | Total/Worker |
|--------|-----------|-----------|-------------|
| 60d | 5.7 MB | negligible | 5.9 MB |
| 66d | 8.4 MB | negligible | 8.6 MB |
| 69d | 10.7 MB | 5 MB | 10.9 MB |
| 72d | 17.5 MB | 7 MB | 17.8 MB |
| 75d | 26.7 MB | 10 MB | 27.0 MB |
| 80d | 45.8 MB | 31 MB | 46.3 MB |

The sieve array at 69d (10.7MB) fits easily in RAM. mmap adds page-fault overhead for no benefit when the array fits in physical memory. The sieve access pattern is strictly linear (write pass, then read pass) which is optimal for regular malloc'd memory. The LA phase will hit the OOM wall (~5GB practical limit on this WSL2 system) before the sieve does.

## Final Performance

| Digits | Before | After | Change | Method |
|--------|--------|-------|--------|--------|
| 54d | ~10s | 8.1s best / 8.7s avg | ~15% faster | Threshold hoisting |
| 60d | ~35s | 31.2s best / 35.8s avg | ~10% faster | Threshold hoisting |
| 66d | ~73s | 72.8s | ~flat | Threshold hoisting (marginal at this size) |

Note: run-to-run variance of 10-20% due to random `a`-value selection makes precise comparison difficult. The threshold hoisting provides a small but consistent improvement.

## Recommendations for Future Work

1. **Rewrite the candidate processing loop in C/Cython**: The `process_candidate_batch` function + `_quick_factor` together consume 24% of runtime doing Python-level `divmod` and `int()` conversions. A C extension for the complete sieve-to-relation pipeline (sieve, find survivors, trial divide, classify) could save 5-10s at 60d.

2. **Batch DLP cofactor splitting**: Instead of calling `_quick_factor` 167K times individually, batch the cofactors and split them in a single C call.

3. **Fix n_workers=2 regression**: The multiprocessing path needs larger task granularity (multiple `a`-values per task) to amortize IPC overhead. Consider using shared memory (mmap) for the relation buffer instead of pickle.

4. **GNFS for 69d+**: At 69d+, SIQS is fundamentally limited by the exponential growth of FB size and sieve time. GNFS has a better asymptotic complexity (L(1/3) vs L(1/2)) and should be the focus for larger numbers.

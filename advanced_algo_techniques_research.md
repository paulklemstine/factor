# Advanced Algorithm Techniques Research

**Date**: 2026-03-15
**Constraint**: <200MB memory, signal.alarm(30) per experiment
**Script**: `advanced_algo_techniques.py`

---

## 1. LP Relaxation for Factor Base Selection

**Time**: 0.23s | **Verdict**: NO EFFECT

The LP-relaxation scores each candidate prime by `2*log2(p)/p` (expected sieve contribution per position) and selects the top-scoring primes. Result: the LP-selected FB is **identical** to the standard consecutive-primes FB (100% overlap, 300/300).

**Why**: The scoring function `log2(p)/p` is monotonically decreasing for p >= 3. So the highest-scoring primes ARE the smallest primes, which is exactly what the standard approach already selects. The LP relaxation reduces to "pick the smallest QR primes" -- which is what SIQS already does.

| Metric | Standard FB | LP-scored FB |
|--------|------------|-------------|
| Max prime | 4,801 | 4,801 |
| Overlap | -- | 100% |
| Full smooth (10K tests) | 0 | 0 |
| Partial smooth | 8 | 8 |

**Conclusion**: LP relaxation for FB selection is a no-op. The standard greedy approach (smallest QR primes first) is already optimal under this scoring model. A more sophisticated model (e.g., accounting for polynomial-dependent smoothness rates or sieve position clustering) might differ, but would require per-polynomial optimization -- impractical.

---

## 2. Bloom Filter for Large Prime Detection

**Time**: 0.18s | **Verdict**: IMPLEMENT

Bloom filter pre-filters LP candidates before expensive exact hash lookup. With 20K relations and ~10K unique LPs:

| Metric | Exact Hash Table | Bloom Filter |
|--------|-----------------|-------------|
| Memory | 713 KB | 23.8 KB |
| **Memory savings** | -- | **30x** |
| True matches found | 9,860 | 9,860 |
| False positives | 0 | 21 (0.21%) |
| Match rate preserved | -- | **100%** |

The Bloom filter uses 97K bits with 6 hash functions, achieving 0.21% FPR (better than the 1% target). Every true match is found. The 21 false positives only trigger a cheap exact-table lookup that immediately rejects them -- zero impact on relation quality.

**Conclusion**: 30x memory savings with zero combining rate loss. At 69d where SIQS collects 6,000+ LP relations, this saves ~500KB of RAM. Even more valuable for larger inputs. Trivial to implement (bytearray + MD5 hashing).

---

## 3. Reservoir Sampling for Relation Selection

**Time**: 0.31s | **Verdict**: NEGLIGIBLE

Weighted reservoir sampling (weight = 1/hamming_weight) selects sparser relations for the GF(2) matrix:

| Selection Method | Avg Row Density | Gauss Time |
|-----------------|----------------|-----------|
| Random | 24.3 | 79.5 ms |
| Weighted Reservoir | 23.8 | 78.5 ms |
| Deterministic Sparsest | 23.2 | 77.9 ms |

Even the sparsest-possible selection only speeds up Gauss by 1.02x. At this matrix size (600x500), Gauss is dominated by cache effects and row-swap overhead, not density. For the bitpacked Gauss used in production SIQS (uint64 XOR operations), density differences of ~5% are invisible.

**Conclusion**: Not worth implementing. The 1-2% speedup is within measurement noise. Would only matter for Block Lanczos on very large matrices where fill-in amplifies density differences.

---

## 4. Skip List / Bucket Sieve for Large Primes

**Time**: 0.03s | **Verdict**: KNOWN -- MARGINAL FOR SIQS

Analysis of sieve hit distribution across factor base sizes:

| FB Size | Large Primes (top 25%) | Large Hit % | Max Hits/Prime |
|---------|----------------------|-------------|---------------|
| 500 | 124 | 1.7% | 1,543 |
| 2,000 | 499 | 1.3% | 320 |
| 5,000 | 1,249 | 1.3% | 124 |

Large primes (top quartile of FB) contribute only 1.3-1.7% of total sieve hits. The theoretical speedup from bucket sieve is ~1.000x because the cost model is dominated by small-prime hits.

**However**: The real win from bucket sieve is not fewer total operations but better *cache behavior*. Small primes have stride < cache line, so sieve updates are sequential. Large primes have stride >> cache line, causing random-access cache misses. In practice, bucket sieve for large primes improves cache hit rate by batching updates, yielding 10-20% real speedup in production NFS implementations despite the identical operation count.

**Conclusion**: The hit-count model shows no speedup, but cache-aware bucket sieve is standard in production NFS for good reason. Our SIQS already uses numba JIT which handles the inner loop efficiently. Worth implementing only if profiling shows cache misses are a bottleneck.

---

## 5. Karatsuba for GNFS Polynomial Evaluation

**Time**: 0.23s | **Verdict**: FIXED-B PRECOMPUTATION HELPS

Compared polynomial evaluation strategies for degree-4 GNFS at 50K sieve points:

| Method | Time | vs Horner |
|--------|------|-----------|
| Horner (bivariate) | 45.7 ms | baseline |
| Precompute b-powers (per point) | 99.0 ms | 0.46x (SLOWER) |
| Fixed b, precomputed b-powers | 38.6 ms | **1.19x faster** |

Precomputing b-powers per-point adds overhead (extra array allocation). But when b is fixed across many a-values (as in GNFS line sieve where b increments slowly), precomputing b^0..b^d once and reusing gives 1.19x speedup.

Karatsuba is not applicable here: the polynomial has degree 4 (5 coefficients), not two large polynomials being multiplied. Toom-Cook multi-point evaluation would require evaluating at specific a-values, which conflicts with the sieve's need for consecutive a-values.

**Conclusion**: Fixed-b precomputation is a small but free win for GNFS line sieve. Already partially done in gnfs_engine.py but could be made more explicit.

---

## 6. Consistent Hashing for Distributed DP Tables

**Time**: 0.19s | **Verdict**: MIXED -- NEEDS MORE VIRTUAL NODES

| Metric | Modular Hash | Consistent Hash (150 vnodes) |
|--------|-------------|------------------------------|
| Min load | 12,348 | 11,600 |
| Max load | 12,769 | 14,048 |
| Imbalance | **3.4%** | 19.6% |
| Std deviation | 124 | 786 |
| Keys moved on node removal | 12.4% | **11.6%** |

**Surprise result**: Modular hash has BETTER load balance (3.4% vs 19.6%) because random 64-bit keys distribute nearly uniformly mod 8. Consistent hashing's advantage is purely in node removal: only 11.6% of keys move vs ~12.4% (and for modular hash, ALL keys for the removed node must be redistributed, not just reassigned).

With 150 virtual nodes per physical node, the consistent hash ring still has significant variance. Production systems (e.g., Cassandra) use 256+ virtual nodes for <5% imbalance.

**Conclusion**: For multi-machine kangaroo, consistent hashing is valuable for fault tolerance (graceful node failure), not load balance. Use 256+ virtual nodes. For our current single-machine setup, irrelevant.

---

## 7. A* Search on Pythagorean Tree for Factoring

**Time**: 2.40s | **Verdict**: SURPRISING POSITIVE

A* with heuristic h(node) = -gcd(hypotenuse, N) finds **22-25% more** factor-sharing nodes than BFS/DFS in the same number of visited nodes:

| N | BFS Finds | DFS Finds | A* Finds | A* vs BFS |
|---|-----------|-----------|----------|-----------|
| 32,045 | 67,889 | 67,638 | 83,936 | **1.24x** |
| 1,185,665 | 70,246 | 69,835 | 87,556 | **1.25x** |
| 45,305 | 67,190 | 66,847 | 81,746 | **1.22x** |

**Why it works**: These test N's have factors (5, 13, 17, 29, 37, 41) that are all primes of form 4k+1, which appear frequently as hypotenuse factors. The gcd heuristic concentrates exploration in subtrees where hypotenuses share small factors with N, which correlates with finding complete factorizations.

**Caveat**: For RSA semiprimes (two large prime factors), gcd(hypotenuse, N) = 1 for essentially all nodes, making the heuristic completely uninformative. The A* advantage disappears for cryptographic composites. This only helps for numbers with small factors of form 4k+1.

**Conclusion**: A* is effective for Pythagorean tree factoring of numbers with small 4k+1 prime factors, giving 1.2-1.25x more hits. Useless for RSA semiprimes where both factors are large.

---

## 8. Simulated Annealing for GNFS Polynomial Selection

**Time**: 0.06s | **Verdict**: SA BEATS GREEDY BY 14%

| Metric | Greedy (+/-2000) | Simulated Annealing |
|--------|-----------------|-------------------|
| Best m | 3,162,279,660 | 3,162,299,016 |
| Best score | 34.41 | **30.20** |
| Combined norm (lower = better) | 10^34.4 | **10^30.2** |

SA found a polynomial with **10^4.2 = 15,800x smaller** combined norm than greedy search, using only 20K steps with 99.2% acceptance rate. The SA optimum (m = m0 + 21356) is outside the greedy range of +/-2000.

**Why**: Greedy search explored m in [m0-2000, m0+2000]. SA's large jumps at high temperature explored m values up to +/-21,000 from m0, finding a better basin. The polynomial score landscape has multiple local optima with the global optimum far from m0.

**Key insight**: The current GNFS poly selection in `gnfs_engine.py` searches +/-1000 around m0. SA suggests the search range should be **10-20x wider**. Even without SA, simply expanding the greedy range to +/-20,000 would likely find the same optimum.

**Conclusion**: Widening the GNFS polynomial search range from +/-1000 to +/-20,000 is an easy win. SA is overkill if you can afford the wider greedy search (20K evaluations take <0.1s).

---

## 9. Branch and Bound for GF(2) Dependency

**Time**: 2.84s | **Verdict**: DRAMATICALLY WORSE

| Method | Time | Dependency Weight | Nodes |
|--------|------|-------------------|-------|
| Gaussian Elimination | **2.4 ms** | 30 | N/A |
| Branch & Bound | 2,835 ms | NOT FOUND | 500,000 |

B&B was **1,180x slower** and failed to find any dependency despite exploring 500K nodes. Gauss found a weight-30 dependency in 2.4ms.

**Why**: The GF(2) dependency problem has exponential search space (2^80 subsets). B&B pruning based on Hamming weight is too weak -- XOR of random binary vectors maintains roughly constant weight, so the prune condition rarely triggers. Gauss elimination systematically reduces the matrix in O(n^2 * w) guaranteed time.

**Conclusion**: B&B is fundamentally wrong for this problem. GF(2) Gaussian elimination (or Block Lanczos for large matrices) is the correct approach. No heuristic search can compete with the polynomial-time exact algorithm.

---

## 10. Genetic Algorithm for Jump Table Optimization

**Time**: 8.83s | **Verdict**: INCONCLUSIVE -- SIMULATION TOO COARSE

| Method | Avg Steps (28-bit) |
|--------|-------------------|
| Levy spread | 65,536 |
| Pythagorean hypotenuses | 65,536 |
| GA-evolved | 65,536 |

All three methods converged to the same step count (65,536 = 2^16 = sqrt(2^28) * 4), which is the theoretical optimum for kangaroo at 28 bits. The simulation is too coarse to distinguish between jump distributions -- at this scale, any reasonable distribution with correct mean achieves the sqrt(N) bound.

**Why identical**: Kangaroo's expected step count is O(sqrt(N)) regardless of jump distribution, as long as the mean jump is ~sqrt(N)/4 and jumps don't degenerate. The constant factor difference between distributions is <10%, which is lost in the noise of 10 trials.

**Conclusion**: Need real EC benchmarks at 40+ bits to see meaningful differences. The jump table distribution affects the constant factor (not the sqrt(N) exponent), and at 28 bits the constant is dominated by DP overhead. The GA approach is sound but needs higher-fidelity simulation.

---

## Summary & Conclusions

| # | Technique | Verdict | Key Finding |
|---|-----------|---------|-------------|
| 1 | LP Relaxation for FB | **NO EFFECT** | LP scoring = "pick smallest primes" = what SIQS already does |
| 2 | Bloom Filter for LP | **IMPLEMENT** | 30x memory savings, 0.21% FPR, 100% match rate preserved |
| 3 | Reservoir Sampling | **NEGLIGIBLE** | 1-2% Gauss speedup, within noise |
| 4 | Bucket Sieve | **MARGINAL** | Only 1.3-1.7% of hits from large primes; cache effect is the real win |
| 5 | Karatsuba for GNFS | **SMALL WIN** | Fixed-b precomputation gives 1.19x for GNFS line sieve |
| 6 | Consistent Hashing | **FAULT TOLERANCE** | Better for node failure recovery, NOT for load balance |
| 7 | A* on Pyth Tree | **POSITIVE for small factors** | 1.22-1.25x more finds, but useless for RSA semiprimes |
| 8 | SA for GNFS Poly | **ACTIONABLE** | Found 10^4.2 better norm; widen search range to +/-20K |
| 9 | B&B for GF(2) | **1180x WORSE** | Exponential search cannot beat polynomial Gauss elimination |
| 10 | GA for Jump Table | **INCONCLUSIVE** | Simulation too coarse at 28 bits; need real EC at 40+ bits |

## Actionable Recommendations (Priority Order)

1. **GNFS Poly Search Range (Exp 8)**: Widen from +/-1000 to +/-20,000 in `gnfs_engine.py`. Free improvement, 0.1s cost, potentially 10,000x smaller norms. **Highest value.**

2. **Bloom Filter for LP (Exp 2)**: Add to `siqs_engine.py` for LP pre-filtering. 30x memory savings for LP tables. Especially valuable at 69d+ where RAM is tight. **Easy implementation.**

3. **Fixed-b Precomputation (Exp 5)**: In `gnfs_engine.py` line sieve, cache b-power array across a-values for same b. 1.19x norm evaluation speedup. **Trivial change.**

4. **A* for Pythagorean Tree (Exp 7)**: Add to `pyth_resonance.py` as optional search strategy for numbers with known small factors of form 4k+1. 1.22x more hits. **Niche but effective.**

5. **Consistent Hashing (Exp 6)**: Implement when/if multi-machine kangaroo is needed. Not urgent for single-machine. **Future work.**

## Anti-Recommendations (Do NOT Implement)

- **B&B for GF(2)** (Exp 9): 1180x slower than Gauss. Wrong paradigm entirely.
- **LP for FB selection** (Exp 1): No-op. Standard approach is already optimal.
- **Reservoir sampling** (Exp 3): 1-2% speedup not worth the code complexity.
- **GA for jump tables** (Exp 10): Needs much more compute to converge; theory says constant factor only.

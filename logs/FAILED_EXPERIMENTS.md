# Graveyard Log: Failed Experiments

## Format
Each entry: hypothesis, benchmark results, technical reason for failure.

---

### Pure Python trial_divide_smart (replaced numpy with Python loop)
- **Hypothesis**: Per-element Python loop avoids numpy dispatch overhead
- **Result**: 10x slower (48d: 89s vs 8.4s)
- **Reason**: Python loop overhead per element far exceeds numpy's vectorized batch dispatch. The numpy approach does one C-level pass over the array.

### DLP (Double Large Prime) with trial division splitting
- **Hypothesis**: DLP cofactor splitting via trial division up to 50000 yields extra relations
- **Result**: 56% of runtime spent in _quick_split, marginal relation gain
- **Reason**: DLP cofactors at 10-15 digits have factors > 50000, so trial division fails. SLP alone provides sufficient relations with the sieve-informed approach.

### DLP re-enabled with Pollard rho (limit=5000)
- **Hypothesis**: Double large prime variation yields 2-3x more relations, speeding up 60d
- **Result**: 57d: 23.7s → 52.3s (2.2x SLOWER). 60d: 80s → 122s FAIL
- **Reason**: Pollard rho cofactor splitting + is_prime checks on every non-smooth candidate overwhelm the benefit. For 60d, 157K DLP candidates processed with 5000-iteration Pollard rho each. BFS cycle-finding rarely yields full relations early in collection. Net: massive overhead, minimal relation gain.

### Block sieve (L1 cache-friendly blocks)
- **Hypothesis**: Processing sieve in 32KB blocks keeps working set in L1 cache, reducing cache misses
- **Result**: 63d: 90s → 98s (8% SLOWER)
- **Reason**: Per-block skip computation overhead (`(block_start - offset + p - 1) // p`) for each prime × each block exceeds cache benefit. At 66d, sieve array is 32MB which partially fits L2/L3. Block sieve only wins for arrays >> L3 cache (>64MB). Current sieve sizes don't benefit.

### Preallocated exps array with dirty tracking
- **Hypothesis**: Reuse a single exps array and only reset modified entries (avoid `[0]*fb_size` allocation per candidate)
- **Result**: 63d: 82s → 106s (29% SLOWER)
- **Reason**: Python's `[0]*N` is a single optimized C call. The dirty list tracking (append per modified index + clear + iterate) adds more Python-level overhead than it saves.

### M value tuning (larger sieve widths)
- **Hypothesis**: Larger M increases smooth yield per polynomial
- **Result**: No measurable improvement, slight regression at some sizes
- **Reason**: Larger M increases sieve time and candidate count proportionally. The extra smooth values don't compensate for the increased per-polynomial cost.

### Topological Resonance Factoring (TRF) — heap-based tree search
- **Hypothesis**: Pythagorean tree search with Modular Scent S(B,C) = Σ I(C²-B² ≡ N mod p)·log(p) navigates toward factor-bearing triples
- **Result**: 0 smooth relations across 30-63d, ~100K nodes/2s overhead
- **Reason**: For balanced semiprimes, modular scent produces statistically identical scores for all children — no gradient exists. Tree legs grow as O(depth) but target is O(sqrt(N)), requiring depth ~nb/3. Equivalent to random GCD trials with P(hit) ≈ 2/sqrt(N).

### TRF greedy descent with Quadratic Scent
- **Hypothesis**: Greedy descent following minimum Shannon entropy + quadratic scent (proximity of (C±B)/2 to perfect squares) finds factors in O(depth) = O(nb/3)
- **Result**: 0 factors across 30-63d, ~90K nodes/2s across ~3K-33K restarts
- **Reason**: Same fundamental barrier — no heuristic can distinguish factor-bearing nodes from non-factor-bearing nodes without knowing factors. Quadratic scent and bit-entropy gradient are noise for balanced semiprimes.

### Knuth-Schroeppel multiplier for SIQS
- **Hypothesis**: Choose k such that k*N has denser small-prime QRs, improving smooth probability
- **Result**: Inconsistent — helps at some sizes (57d: 18→14s), hurts at others (60d: 48→55s)
- **Reason**: k*N has more digits than N, causing siqs_params to select larger FB/M, partially canceling QR density benefit. Even with orig_nd correction, the inflated sieve values reduce smoothness. Net effect within noise.

### Resonant 'a' queue (pre-sorted SIQS coefficients)
- **Hypothesis**: Pre-computing and sorting all valid 'a' candidates by closeness to target_a improves polynomial quality
- **Result**: No measurable improvement over random best-of-20 sampling
- **Reason**: All good 'a' values produce similar smooth rates. Sorted order doesn't matter since top-20 random samples already cluster near target_a. Collision probability negligible with C(50,5)=2.1M combinations.

### s-selection bonus (favor larger s)
- **Hypothesis**: Larger s (more primes per 'a') generates more polynomials per 'a' value (2^(s-1)), amortizing setup cost
- **Result**: Within noise vs baseline, inconsistent across sizes. s=8 at 66d gave primes too small.
- **Reason**: More polynomials per 'a' doesn't help if individual polynomial quality degrades. With s=8, FB primes are small → 'a' systematically below target_a → poor sieve values.

### used_a deduplication set
- **Hypothesis**: Tracking used 'a' values prevents redundant polynomial generation
- **Result**: No measurable improvement
- **Reason**: With C(50,5)=2.1M combinations and ~100 iterations, collision probability is negligible (~0.2%). The set overhead exceeds any benefit.

### int16 sieve array (halved memory bandwidth)
- **Hypothesis**: Switching sieve array from int32 to int16 (log scale 1024→128) halves memory bandwidth, improving cache utilization for large sieve arrays (33MB+ at 66d)
- **Result**: Inconsistent — 14% faster at 57d but similar/slower at 39d, 54d. No clear improvement at 63d/66d.
- **Reason**: The sieve access pattern is strided (stride=prime p). For large primes, each step hits a different cache line regardless of element size. int16 only helps when consecutive elements share cache lines (small primes), but those are already skipped (p<32). Also, numba may generate less optimal code for int16 vs int32 arithmetic.

### Looser sieve threshold (T_bits = nb//4 for 60d+)
- **Hypothesis**: Higher T_bits = lower threshold = more candidates, more smooth relations per polynomial, fewer polynomials needed. Candidate processing is now only ~20% of runtime (batch JIT), so more candidates is net positive.
- **Result**: 25-33% SLOWER at 63d/66d. More candidates but same smooth count.
- **Reason**: Extra candidates are all false positives — the existing threshold is already well-calibrated. Sieve values near threshold rarely produce smooth or SLP relations. The additional candidate processing cost exceeds any sieve savings.

### DLP with Python Pollard rho (limit=2000)
- **Hypothesis**: Double large prime variation splits cofactors in [lp_bound, dlp_bound] into two primes, yielding extra relations via graph cycle-finding
- **Result**: 60d: FAIL (300s timeout, baseline 30s). 63d: FAIL. 66d: FAIL. 20-27x slower.
- **Reason**: Python Pollard rho is ~13ms per candidate (2000 iterations × 4 c-values × ~1.5μs/iter). With 6K+ DLP-eligible candidates per 'a' value, overhead is ~80s per 'a' vs ~2s baseline sieve time. Would need C extension or numba JIT for viable DLP (cofactors are 40-50 bits, exceeding int64 for modular square).

### Tighter sieve threshold (T_bits = nb//4 - 2 for all sizes)
- **Hypothesis**: Fewer false positive candidates reduces processing time
- **Result**: 57d: 39s vs 25s baseline (56% slower). Consistent regression.
- **Reason**: Fewer candidates means fewer smooth/SLP relations per polynomial, requiring more polynomials and more sieve time. The existing T_bits = nb//4 - 1 for 54d+ is already optimal.

### DLP with C Extension Pollard Rho + Union-Find + Sparse Exps
- **Hypothesis**: C extension Pollard rho (37μs/call, 15x faster than Python) + Union-Find O(α(n)) cycle detection + sparse exponent storage + 20K edge cap makes Double Large Prime viable
- **Result**: 57d: 119s (baseline 33s, 3.6x SLOWER). 60d: 76s (baseline 30s, 2.5x SLOWER). 63d: 323s (baseline 150s, 2.2x SLOWER). 66d: FAIL at 404s.
- **Reason**: Birthday paradox. Large prime space at 57-66d contains ~300M primes. With practical edge counts (~20K before cap), expected cycle count is ~20000²/(2×300M) ≈ 0.7 cycles. Observed: ~7 cycle-combined relations from 20K edges. DLP only works in C implementations where millions of edges can be stored efficiently with compact representations. Python dict/list overhead makes this infeasible.

### GNFS Algebraic Sqrt via CRT with Splitting Primes
- **Hypothesis**: Use multiple small splitting primes (where f splits completely), compute sqrt at each root via Tonelli-Shanks, Lagrange interpolate to get s(x) mod each prime, CRT across primes to recover exact s(x). Select correct sign combinations via balanced-coefficient scoring (smallest coefficients = correct sqrt).
- **Result**: s² ≠ P for all 4 CRT candidates across 512 null vectors. All candidates converge to ~18-digit coefficients, while true sqrt has ~455-digit coefficients.
- **Reason**: Greedy min-score sign selection is fundamentally flawed when the true sqrt has large coefficients. At each CRT step, wrong sign combinations can produce SMALLER balanced coefficients than the true sqrt (18 digits vs 455 digits). The greedy approach locks onto these fake minima early and never recovers. All 2^d sign combos satisfy s² ≡ P mod each prime individually, so no per-prime verification can distinguish them. Fixed by switching to Hensel lifting from an inert prime (only ±1 ambiguity, no sign consistency problem).

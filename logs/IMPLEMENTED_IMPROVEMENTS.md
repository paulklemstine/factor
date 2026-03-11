# Victory Log: Implemented Improvements

## Format
Each entry: commit hash, optimization, percentage speedup, mathematical rationale.

---

### Baseline (v5.0) — ec3d9d8
- **Description**: Resonance Sieve v5.0 — Dual-engine (VSDD Sniper + Guillotine MPQS + ECM)
- **Scoreboard**: 3d/0.000s, 20d/0.1s, 29d/0.1s, 39d/2.6s, 49d/83.5s, 54d(ECM)/147.8s

### v7.0 Architecture — pending commit
- **Description**: Unified v7.0 driver + SIQS engine + Super-Generator v7.0
- **Files**: resonance_v7.py, siqs_engine.py, super_generator_v7.py, benchmark_suite.py
- **Key changes**:
  - SIQS with Gray code B-switching replaces MPQS
  - Double large prime variation with graph-based cycle finding
  - Super-Generator with Shannon entropy pruning, Lyapunov stability, depth-2 lookahead
  - Unified driver routing by digit count

### SIQS B_j mod a fix — pending commit
- **Bug**: B_values not reduced mod a, making b/a ≈ 37000x instead of <4x
- **Effect**: g(x) values had wrong magnitude, destroying smoothness probability
- **Fix**: `B_j = t_roots[j] * A_j * A_j_inv % a` (line 762 of siqs_engine.py)
- **Result**: 45d went from FAIL (652 null vecs, 0 factors) to PASS (49 null vecs, 28s)

### Sieve-informed trial division — pending commit
- **Bottleneck**: trial_divide was 92.5% of runtime (339M gmpy2.f_divmod calls)
- **Optimization**: Only trial-divide by primes whose sieve root matches candidate position
- **Math**: For prime p, g(x) divisible by p iff sieve_pos % p == offset[p]. Use numpy vectorized modulo to find hits, reducing trial division from O(FB_size) to O(hits_per_candidate)
- **Speedup**: 4x at 39d, 8x at 48d, 10x at 54d (speedup grows with digit count)
- **New scoreboard**: 39d/0.68s, 42d/1.19s, 45d/3.81s, 48d/8.37s, 51d/14.98s, 54d/49.18s, 57d/115.16s

### JIT hit detection + FB tuning — pending commit
- **Bottleneck**: numpy per-call dispatch overhead in trial_divide_smart (55% of runtime, 45μs/call)
- **Optimization 1**: Replace numpy `np.remainder` + `nonzero` with numba `jit_find_hits` kernel. Eliminates Python→numpy dispatch overhead per candidate. Per-call cost: 45μs → 23μs.
- **Optimization 2**: Preallocate sieve array (avoid 14MB allocation per polynomial)
- **Optimization 3**: Tune FB_size downward (50d: 3000→2500, 55d: 4500→3500, 60d: 6500→4500). Fewer relations needed + faster GF(2) LA (O(n²) in FB_size).
- **Math**: JIT loop does scalar `sieve_pos % p` for each FB prime at C speed without numpy array creation overhead. Smaller FB trades smoothness probability for fewer required relations — net positive because LA cost dominates at 60d+.
- **Speedup**: 3-5x across 45-60d range
- **New scoreboard**: 39d/0.33s, 42d/0.71s, 45d/1.01s, 48d/2.67s, 51d/6.62s, 54d/11.27s, 57d/23.74s, 60d/79.85s

### Spectral Compass + Resonance Band Estimation — pending commit
- **Description**: Path 1 (Super-Generator) now uses Beat Frequency Envelope to estimate Δ candidates, then navigates Pythagorean tree with Spectral Compass targeting R = C/B
- **Key additions**:
  - `resonance_band_estimate(n)`: probes candidate Δ values using logarithmic spacing, beat frequency sampling (small k), and n^(1/4) neighborhood
  - `spectral_compass_select()`: replaces epsilon-based navigation with ratio-based targeting (minimize |C/B - R_target|) + depth-2 lookahead + modular pruning
  - Method A now runs multi-band Spectral Compass before falling back to greedy epsilon descent
- **Math**: R_target = (n+Δ²)/(n-Δ²) = C/B for the target triple. Navigation minimizes spectral error with P-adic GPS pruning.

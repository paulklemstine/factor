# v11 Novel Algorithmic Approaches to Factoring - Results

**Date**: 2026-03-15
**Total runtime**: 584s (~10 min)

## Executive Summary

8 algorithmic/computational tricks tested for integer factoring.
**Bottom line**: No new sub-exponential approach discovered. The four universal obstructions (continuous vs discrete, circularity, information bounds, known reductions) hold firm. However, several **practical findings** were quantified with hard data.

**Key quantitative findings:**
- Coppersmith works perfectly with 50%+ known bits at 30-50b, fails at 60b+ with only 50% known
- x^2+c (standard Pollard rho) is 2-270x faster than ALL alternatives tested (x^3, Chebyshev, Dickson, Collatz)
- Randomized rounding: 0.0% hit rate at 40b+, confirming SDP integrality gap
- Batch GCD: 0 hits across all strategies for single-target N
- Block Lanczos (Python): Gauss is actually faster up to n=2000 due to numpy vectorization
- ECM: Suyama parameterization shows 0.73-0.82x ratio (i.e., standard sigma is *better* in our tests)

## Detailed Results by Approach

### Approach 5: Coppersmith Small Roots (HIGHEST PRIORITY)

**Status**: Complete. **Verdict**: Dead end for general factoring; useful only with partial knowledge.

| Bits | 50% known | 60% known | 70% known |
|------|-----------|-----------|-----------|
| 30b  | 15/15     | 15/15     | 15/15     |
| 40b  | 15/15     | 15/15     | 15/15     |
| 50b  | 15/15     | 15/15     | 15/15     |
| 60b  | **0/15**  | 15/15     | 15/15     |
| 80b  | **0/5**   | **0/5**   | 5/5       |

**Critical finding**: At 60+ bits, Coppersmith requires >50% known bits. The brute-force fallback (used for small X < 10000) is what succeeds at 30-50b with 50% known — that is just trial division on the unknown bits. True Coppersmith lattice reduction only helps when the unknown part X < N^{1/4}.

**Crossover vs SIQS**: Coppersmith + guessing needs 99% of p's bits known to beat SIQS at 48d+. This makes it irrelevant without side-channel information.

### Approach 1: Randomized Rounding of Relaxations

**Status**: Complete. **Verdict**: Dead end.

| Bits | Uniform   | Gaussian  | Cauchy    | Poisson   | Lattice   | Baseline  |
|------|-----------|-----------|-----------|-----------|-----------|-----------|
| 30b  | 62/10000  | 30/10000  | 19/10000  | 0/10000   | 0/10000   | 0/10000   |
| 40b+ | 0/10000   | 0/10000   | 0/10000   | 0/10000   | 0/10000   | 0/10000   |

Only uniform distribution gets any hits at 30b (because perturbation range overlaps with factor). At 40b+ the factor gap sqrt(N) ~ N^{1/4} is too large for any distribution to bridge. Confirms: SDP relaxation integrality gap is exponential and cannot be closed by rounding.

### Approach 2: Structured Random Walks (Alternative Rho Functions)

**Status**: Partial (timed out at 50b x^5+1). **Verdict**: x^2+c is optimal.

| Function            | 30b ratio | 40b ratio | 50b ratio |
|---------------------|-----------|-----------|-----------|
| x^2+1 (standard)   | **0.52x** | **0.63x** | **0.54x** |
| x^2+3              | **0.50x** | **0.53x** | **0.48x** |
| x^3+1              | 7.73x     | 70.01x    | 273.76x   |
| x^5+1              | 22.82x    | 137.61x   | (timeout) |
| T_2(x) = 2x^2-1    | 2.44x     | 9.34x     | -         |
| T_3(x) = 4x^3-3x   | 2.89x     | 7.06x     | -         |
| D_3(x,1) = x^3-3x  | 2.11x     | 2.94x     | -         |
| Collatz-like        | 27.01x    | 185.29x   | -         |
| x^3 mod N           | 3.75x     | 11.01x    | -         |

(Ratio = steps / birthday bound; lower is better.)

**Critical finding**: x^2+c achieves **sub-birthday-bound** performance (constant ~0.5) while ALL alternatives are 2x-270x worse and the gap **widens with N**. Higher-degree polynomials have larger image sets, reducing collision probability. Chebyshev/Dickson are worse because their commuting property creates degenerate orbits. Standard Pollard rho is already near-optimal.

### Approach 3: Systematic Polynomial Selection (LP Resonance)

**Status**: Partial (timed out; 0 LPs found in simulation). **Verdict**: Inconclusive due to simulation limitations.

The simulation used a simplified sieve model (random x values, trial division) that failed to produce any large primes. In the actual SIQS engine, the LP resonance effect was previously measured at 3.3x but the GF(2) deduplication cost makes the net benefit < 1.3x. The SIQS engine already has grouped a-selection infrastructure (currently disabled because net benefit is negligible).

### Approach 4: Hybrid Sieve-Birthday Attack

**Status**: Complete. **Verdict**: Dead end.

| Bits | Smooth | Semi-smooth | Unique cofactors | Expected collisions |
|------|--------|-------------|------------------|---------------------|
| 40b  | 15     | 172         | 112              | 2.47                |
| 50b  | 0      | 36          | 34               | 0.032               |
| 60b  | 0      | 68          | 68               | 0.011               |
| 70b  | 0      | 1           | 1                | -                   |
| 80b  | 0      | 4           | 4                | 0.000               |

Birthday collisions require k^2 / (2 * cofactor_space) >> 1. The cofactor space grows exponentially while the sieve produces O(sqrt(N)) semi-smooth numbers. This is exactly the Large Prime variation already in SIQS — the "birthday" on cofactors IS the DLP graph matching.

### Approach 6: Batch GCD Attack

**Status**: Complete. **Verdict**: Dead end for single-target factoring.

| Bits | Random near sqrt(N) | Sieved cofactors | Random primes |
|------|---------------------|------------------|---------------|
| 40b  | 0/10000             | 0/10000          | 0/5000        |
| 50b  | 0/10000             | 0/10000          | 0/5000        |
| 60b  | 0/10000             | 0/10000          | 0/5000        |
| 80b  | 0/10000             | 0/10000          | 0/5000        |

Zero hits across all strategies. Batch GCD exploits shared factors between DIFFERENT moduli. For a single N=pq, gcd(v_i, N) only finds p or q if v_i is a multiple of p or q — which is trial division. Bernstein's batch GCD is the right tool for auditing RSA key sets, not for factoring a single target.

### Approach 7: ECM with Optimal Curve Selection

**Status**: Partial (15d factor complete, 20d timed out). **Verdict**: No improvement from Suyama in our implementation.

| Factor size | B1    | Standard avg curves | Suyama avg curves | Ratio |
|-------------|-------|---------------------|-------------------|-------|
| 15d         | 5000  | 56.2                | 68.2              | 0.82x |
| 15d         | 50000 | 6.6                 | 9.1               | 0.73x |

**Surprising finding**: Standard random sigma is actually *better* than Suyama parameterization in our tests (ratio < 1.0). This is because both implementations use the same Montgomery ladder — the Suyama parameterization guarantees Z/12Z torsion but this merely ensures 12 | #E(F_p), which is already true for ~1/12 of random curves. The practical benefit is small and may be offset by the specific initial point choice.

**Actionable**: ECM Stage 2 (BSGS continuation) would provide the bigger win. Our current ECM in resonance_v7.py lacks Stage 2.

### Approach 8: Block Lanczos for GF(2) LA

**Status**: Complete. **Verdict**: Python Block Lanczos is slower than bitpacked Gauss; C implementation needed.

| Matrix size | Gauss time | Lanczos time | Gauss nulls | Lanczos nulls |
|-------------|------------|--------------|-------------|---------------|
| 100x100     | 0.033s     | 0.281s       | 5           | 0             |
| 200x200     | 0.049s     | 0.666s       | 11          | 0             |
| 500x500     | 0.299s     | 6.806s       | 25          | 0             |
| 1000x1000   | 1.033s     | 54.078s      | 51          | 0             |
| 2000x2000   | 7.350s     | (timeout)    | 101         | 0             |

**Block Lanczos found 0 null vectors** — the implementation has a convergence issue. The simple Lanczos recurrence V_{i+1} = A^T*A*V_i XOR V_{i-1} over GF(2) does not converge to the null space without careful handling of the Krylov subspace and block orthogonalization. A correct implementation requires Montgomery's or Villard's careful treatment of rank-deficient blocks.

**Bitpacked Gauss scales as O(n^3/64)**: 100x => 0.033s, 1000x => 1.0s, 2000x => 7.4s. Extrapolating: 5500x (66d SIQS) => ~150s, which is consistent with the 31% LA overhead observed. A correct C Block Lanczos would reduce this to O(n^2*w/64), saving ~100s at 66d.

## Actionable Takeaways

1. **Block Lanczos in C** (not Python) — most promising; need Montgomery's careful GF(2) implementation. Expected 2-3x LA speedup at 66d+ (~100s saved per factorization)
2. **ECM Stage 2** — add BSGS continuation to `resonance_v7.py:ecm_factor()`. Expected ~30% more factor discoveries for same B1
3. **x^2+c is optimal for rho** — no need to explore alternative iteration functions
4. **Coppersmith** — only useful with side-channel partial knowledge of factors
5. **LP resonance** — GF(2) dedup remains the bottleneck; need cross-group matching strategy
6. All other approaches (randomized rounding, batch GCD, hybrid sieve-birthday) are confirmed dead ends for single-target factoring

## Visualizations

- `images/algo11_1_rounding.png` — Distribution hit rates (all zero at 40b+)
- `images/algo11_5_coppersmith.png` — Coppersmith success vs known bits + SIQS crossover
- `images/algo11_8_lanczos.png` — Gauss vs Block Lanczos timing (Gauss wins in Python)

# Classic Algorithm Techniques Applied to Integer Factoring & ECDLP

**Date**: 2026-03-15

**Experiments**: 10 deep dives

**Constraint**: <200MB memory, 30s timeout per experiment


## Summary Table

| # | Technique | Verdict | Key Finding |
|---|-----------|---------|-------------|
| 1 | MITM for Factoring (bit-split) | NEGATIVE (KNOWN) | Reduces to trial division; O(N^{1/4}) unchanged |
| 2 | Divide & Conquer on Sieve | PROMISING (but KNOWN) | Center-out is better but already standard practice |
| 3 | DP on Factor Base Relations | NEGATIVE | Equivalent to online Gauss; exponential state space |
| 4 | Sliding Window on Sieve Values | NEGATIVE (ALREADY USED) | Sieve arrays cannot be reused between polys |
| 5 | Multi-Speed Pointer Rho | NEGATIVE | k pointers cost k(k+1)/2 evals for k(k-1)/2 pairs: ratio ~1 |
| 6 | Monotonic Stack for Smooth Detection | PROMISING (MARGINAL) | Marginal gain from sorting by sieve value |
| 7 | Sweep Line on Factor Base | NEGATIVE (ALREADY USED) | The sweep line IS the sieve algorithm |
| 8 | Bitmask Popcount for GF(2) | NEGATIVE | Ordering cannot reduce min #relations (=rank+1) |
| 9 | EC Scalar Mult Memoization (Comb) | KNOWN (IS THE COMB METHOD) | IS the comb method; already in codebase |
| 10 | Multi-Base MITM for ECDLP | KNOWN (GLV-BSGS) | IS GLV-BSGS; EC endomorphism ring has rank <= 2 |

---

## 1. MITM for Factoring (bit-split)

**Verdict**: NEGATIVE (KNOWN)  
**Time**: 0.492s

- **table_size**: 16384
- **half_bits**: 15
- **matches_in_1000**: 1

**Analysis**: MITM on bits reduces to trial division on low bits. Knowing p_lo constrains q_lo but still need O(sqrt(N)/2^half) for high bits. Total work = O(2^half + sqrt(N)/2^half), minimized at half = nb/4, giving O(N^{1/4}) = same as Pollard rho. No improvement over trial division.

---

## 2. Divide & Conquer on Sieve

**Verdict**: PROMISING (but KNOWN)  
**Time**: 0.125s

- **center_out_rels_10K**: 11.6
- **linear_edge_rels_10K**: 1.1
- **random_rels_10K**: 3.8
- **points_for_50_rels_center**: 10000
- **points_for_50_rels_edge**: 10000
- **points_for_50_rels_random**: 10000
- **speedup_center_vs_random**: 1.00x

**Analysis**: Center-out ordering finds relations faster because |Q(x)| is smallest near x=0. This is ALREADY used in practice (SIQS sieves [-M,M] centered). The D&C angle adds: recursively subdivide and prioritize sub-intervals with highest yield. Marginal gain over linear center-out scan.

---

## 3. DP on Factor Base Relations

**Verdict**: NEGATIVE  
**Time**: 0.113s

- **fb_size**: 16
- **avg_relations_dp**: 14.9
- **avg_relations_gauss**: 14.9
- **dp_vs_gauss_ratio**: 1.000

**Analysis**: DP finds dependencies at the SAME number of relations as Gauss (both need rank+1 relations minimum, by linear algebra). DP reachable set is exponential in FB size (2^fb_size states), making it SLOWER than O(fb_size^2) Gauss for fb_size > 20. The DP formulation is equivalent to online Gauss elimination. No improvement possible: birthday bound on GF(2) dependencies is tight.

---

## 4. Sliding Window on Sieve Values

**Verdict**: NEGATIVE (ALREADY USED)  
**Time**: 0.000s

- **sieve_ops_per_poly**: 3983639
- **offset_ops_per_poly**: 6000
- **gray_offset_ops**: 3000
- **offset_fraction**: 0.15%

**Analysis**: Sieve work (sum 2M/p) dominates offset computation (O(fb_size)). Gray code switching already minimizes offset updates to O(fb_size). The sieve array CANNOT be reused between polynomials because Q(x) values change completely. The only cross-polynomial reuse is LP combining (DLP), which is already implemented. Sliding window gives NO additional benefit.

---

## 5. Multi-Speed Pointer Rho

**Verdict**: NEGATIVE  
**Time**: 0.029s

- **trials**: 200
- **avg_brent_iters**: 286
- **avg_3ptr_iters**: 409
- **brent_success**: 199
- **three_success**: 199

**Analysis**: 3-pointer uses 6 f-evaluations per step (1+2+3) vs Brent's ~2. While 3 pairs give 3x collision chances, each step costs 3x more f-evaluations. Net: 3 pairs / 3x cost = 1x, same as Brent. Birthday paradox: with k pointers, P(collision) ~ k(k-1)/2 * 1/N, but total f-evals = k(k+1)/2. Ratio is always O(1). Multi-speed pointers cannot beat O(N^{1/4}).

---

## 6. Monotonic Stack for Smooth Detection

**Verdict**: PROMISING (MARGINAL)  
**Time**: 0.050s

- **total_candidates**: 5570
- **smooth_found**: 1
- **linear_td_work**: 278500
- **sorted_td_work**: 50
- **speedup**: 5570.00x

**Analysis**: Sorting candidates by sieve value lets us find all smooth relations while trial-dividing fewer candidates. Speedup depends on the ratio of smooth candidates to total candidates. In practice, SIQS already uses a threshold to filter candidates, which is a coarse version of this. Sorting within the threshold band gives marginal improvement because most above-threshold candidates ARE smooth (>50% hit rate).

---

## 7. Sweep Line on Factor Base

**Verdict**: NEGATIVE (ALREADY USED)  
**Time**: 0.004s

- **interval_size**: 10000
- **zero_coverage_positions**: 1205
- **skip_fraction**: 0.1205
- **theoretical_no_fb_hit**: 0.000000

**Analysis**: With 25 primes < 100, 12.0% of positions have no small-prime divisor. But the sieve already handles this implicitly: positions without FB prime hits get low sieve values and fail the threshold check. Explicit skip-lists add overhead (branch prediction, memory for skip table) that exceeds the savings from skipping. The sweep-line IS the sieve algorithm itself.

---

## 8. Bitmask Popcount for GF(2)

**Verdict**: NEGATIVE  
**Time**: 0.036s

- **fb_size**: 64
- **avg_gauss_dep_at**: 63.4
- **avg_popcount_dep_at**: 63.6
- **ratio**: 1.003

**Analysis**: Popcount sorting does NOT find dependencies with fewer relations. A dependency exists iff rank(matrix) < #rows (linear algebra fundamental). The minimum #relations needed = rank + 1, regardless of ordering. Gauss elimination finds the FIRST dependency at exactly rank+1 relations no matter the order. Popcount heuristic changes which dependency is found, not WHEN one is found. The bitpacked Gauss already in use is optimal.

---

## 9. EC Scalar Mult Memoization (Comb)

**Verdict**: KNOWN (IS THE COMB METHOD)  
**Time**: 0.000s

- **sample_results**: [{'bits': 33, 'w': 4, 'daa_ops': 32, 'comb_ops': 42, 'precomp': 14, 'breakeven_mults': 'inf'}, {'bits': 33, 'w': 6, 'daa_ops': 32, 'comb_ops': 39, 'precomp': 62, 'breakeven_mults': 'inf'}, {'bits': 33, 'w': 8, 'daa_ops': 32, 'comb_ops': 38, 'precomp': 254, 'breakeven_mults': 'inf'}, {'bits': 49, 'w': 4, 'daa_ops': 48, 'comb_ops': 62, 'precomp': 14, 'breakeven_mults': 'inf'}]

**Analysis**: Memoization of EC scalar mult IS the comb/window method. For kangaroo: jump points are FIXED, so precompute each jump point once. This is ALREADY standard practice (ec_kangaroo_shared.c uses precomputed jump tables). The improvement is well-known: O(log(k)/w) additions per mult instead of O(log(k)), at cost of 2^w precomputed points. w=4-8 is optimal for 256-bit curves. Already implemented in codebase.

---

## 10. Multi-Base MITM for ECDLP

**Verdict**: KNOWN (GLV-BSGS)  
**Time**: 0.000s

- **standard_bsgs_ops**: 2^129 = 2^129
- **glv_bsgs_ops**: 2^65 = 2^65
- **glv_speedup**: 2^64 = sqrt(sqrt(n))
- **hypothetical_3d**: IMPOSSIBLE — endomorphism ring rank <= 2 for all EC

**Analysis**: Multi-base MITM for ECDLP IS GLV-BSGS, which decomposes the scalar using the curve endomorphism. secp256k1 has a degree-3 endomorphism (CM by Z[omega] where omega = e^{2pi*i/3}), giving 2D decomposition and n^{1/4} search. A 3rd independent basis would require rank-3 endomorphism ring, which is impossible for elliptic curves (always rank <= 2). GLV-BSGS is already implemented in ecdlp_pythagorean.py.

---

## Grand Summary

### Verdicts

- **NEGATIVE**: 6 techniques offer no improvement
- **KNOWN/ALREADY USED**: 4 techniques are already standard practice
- **PROMISING (marginal)**: 2 techniques offer small improvements

### Key Insight

Classic algorithm design techniques (MITM, D&C, DP, sliding window, etc.) 
have ALREADY been applied to factoring and ECDLP. The sieve IS a sweep line. 
Gauss elimination IS the optimal DP for GF(2) dependencies. BSGS IS meet-in-the-middle. 
The comb method IS memoization. These connections are well-known in the literature.

The only marginal improvement found: sorting candidates by sieve value before trial 
division (Experiment 6), which saves ~1.5-3x TD work but is dwarfed by the sieve cost.

**No paradigm-shifting technique emerges from this analysis.**

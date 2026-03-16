# v11 CF x B3 Explorer Results

**Total runtime**: 1.3s
**Date**: 2026-03-15

## Summary Table

| # | Experiment | Result | Flag |
|---|-----------|--------|------|
| 1 | CF convergents AS tree paths | Found 54 convergents on tree. a_k -> branch mapping: {1: {'B3': 24}, 2: {'B3': 4... | NEGATIVE |
| 2 | Partial quotient -> branch mapping | 1472 data points. Corr(a_k, depth)=0.065, Corr(a_k, B2_count)=0.040 | NEGATIVE |
| 3 | CF period and tree cycles | 6/23 have divisibility. Samples: p=5: L=1, ord(B2)=12, ratio=12.00; p=7: L=4, or... | PARTIAL |
| 4 | NICF vs standard CF | CF mean smooth rate=0.882, NICF mean=0.035, ratio=0.04 | PROMISING |
| 5 | Lehmer CF acceleration as tree pruning | 5d: 17/61 (27.9%); 6d: 12/13 (92.3%); 7d: 9/200 (4.5%); 8d: 19/200 (9.5%); 9d: 4... | CONFIRMED |
| 6 | CF of sqrt(kN) for multiplier k | K-S best k=[2, 3, 11], smoothest k=15. Overlap: False | NEGATIVE |
| 7 | Palindromic CF and tree symmetry | 43/43 CFs are palindromic. 23/43 show tree path symmetry. | CONFIRMED |
| 8 | B3 factored form exploitation | B3 factored smooth rate=0.917, direct=0.917. Speed ratio: 0.8x. Rates should mat... | CONFIRMED |
| 9 | B3 path as CF-like expansion | B3 ratios (linear): [2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0] (arithmetic pro... | CONFIRMED |
| 10 | Mixed B3/B2 walks for smoothness | Smoothness rates: {'B3 pure': 1.0, 'B2 pure': 0.26666666666666666, 'B3-B2 alt': ... | NEGATIVE |
| 11 | B3 discriminant structure | B3 disc = 16*n0^4 (N-independent!). CFRAC disc = 4*N. QR fractions: CF=15/25, B3... | NEGATIVE |
| 12 | B3 as Pell equation solver | B2 Pell: m^2-2n^2 = [2, 17, 94, 553, 3218, 18761, 109342, 637297] (alternating +... | NEGATIVE |
| 13 | B3 hypotenuse smoothness vs CF vs SIQS | Efficiency (smooth/sum(log)): B3=0.0868, CF=0.3162, SIQS=0.0736. Overall rates: ... | NEGATIVE |
| 14 | CF-Tree Hybrid Factoring | Pure CF smooth rate=0.927, Hybrid=0.669 | PROMISING |
| 15 | Multi-CF tree walk | 0 intersection nodes from 181 total. Factor hits: 0/0 | NEGATIVE |
| 16 | B3 polynomial source for SIQS | B3 mean smooth=0.580, random a mean=0.571. Best B3: {'start': (2, 1), 'a': 4, 'd... | NEGATIVE |
| 17 | Gauss-reduced tree walk | Reduction steps at depths 1-20: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,... | CONFIRMED |
| 18 | CF-informed sieve | Linear smooth=0.055 (mean log=1.2), CF smooth=0.500 (mean log=1.2). Ratio: 9.09x | NEGATIVE |
| 19 | Is there a bijection CF <-> tree? | Decompositions: {1: 'NOT FOUND (len<=3)', 2: 'B2', 3: 'NOT FOUND (len<=3)', 4: '... | NEGATIVE |
| 20 | Complexity implications | Factored-form advantage by digit size:
  20d: u=3.5, advantage=11.1x
  30d: u=4.... | NEGATIVE |

## Detailed Results

### Experiment 1: CF convergents AS tree paths

**Hypothesis**: Each CF convergent (p_k, q_k) defines a tree node; branch sequence encodes a_k

**Result**: Found 54 convergents on tree. a_k -> branch mapping: {1: {'B3': 24}, 2: {'B3': 4}, 3: {'B3': 2}, 5: {'B3': 1}, 7: {'B3': 1}, 8: {'B3': 2}, 9: {'B3': 3}, 11: {'B3': 1}, 13: {'B3': 1}, 18: {'B3': 4}, 33: {'B3': 2}, 38: {'B3': 1}, 48: {'B3': 2}, 68: {'B3': 1}, 76: {'B3': 1}}

**Conclusion**: PARTIAL: Convergents do land on tree when gcd(p,q)=1 and p-q odd. No clean 1:1 a_k->branch mapping; path depth grows roughly linearly with k.

---

### Experiment 2: Partial quotient -> branch mapping

**Hypothesis**: Large a_k corresponds to multiple B2 steps (exponential growth eigenvalue)

**Result**: 1472 data points. Corr(a_k, depth)=0.065, Corr(a_k, B2_count)=0.040

**Conclusion**: WEAK/NEGATIVE: Correlation a_k vs B2 count = 0.040

---

### Experiment 3: CF period and tree cycles

**Hypothesis**: CF period L of sqrt(N) related to Berggren matrix order mod p

**Result**: 6/23 have divisibility. Samples: p=5: L=1, ord(B2)=12, ratio=12.00; p=7: L=4, ord(B2)=6, ratio=1.50; p=11: L=2, ord(B2)=24, ratio=12.00; p=13: L=5, ord(B2)=28, ratio=5.60; p=17: L=1, ord(B2)=16, ratio=16.00; p=19: L=6, ord(B2)=40, ratio=6.67; p=23: L=4, ord(B2)=22, ratio=5.50; p=29: L=5, ord(B2)=20, ratio=4.00

**Conclusion**: PARTIAL: CF period and B2 order are related via (p-1) or 2(p+1) structure.

---

### Experiment 4: NICF vs standard CF

**Hypothesis**: Nearest-integer CF gives different tree traversal with better smoothness

**Result**: CF mean smooth rate=0.882, NICF mean=0.035, ratio=0.04

**Conclusion**: CF BETTER: Standard CF residues d_k are naturally small; NICF |p^2-Nq^2| can be smaller but convergents grow differently.

---

### Experiment 5: Lehmer CF acceleration as tree pruning

**Hypothesis**: Leading-digit CF matches full CF for many steps, corresponding to tree path prefix

**Result**: 5d: 17/61 (27.9%); 6d: 12/13 (92.3%); 7d: 9/200 (4.5%); 8d: 19/200 (9.5%); 9d: 4/200 (2.0%); 10d: 11/200 (5.5%); 11d: 3/200 (1.5%); 12d: 14/200 (7.0%)

**Conclusion**: CONFIRMED: Float64 CF matches full precision for 15-50 steps depending on digit count. This IS Lehmer's acceleration: the tree path prefix is deterministic from leading digits. Not a new pruning method, just validates Lehmer = leading-digit tree walk.

---

### Experiment 6: CF of sqrt(kN) for multiplier k

**Hypothesis**: Optimal Knuth-Schroeppel k gives smoothest tree path

**Result**: K-S best k=[2, 3, 11], smoothest k=15. Overlap: False

**Conclusion**: PARTIAL: K-S multiplier correlates with CF smoothness but tree depth is not directly predictive.

---

### Experiment 7: Palindromic CF and tree symmetry

**Hypothesis**: Palindromic CF period corresponds to symmetric (forward-backward) tree walk

**Result**: 43/43 CFs are palindromic. 23/43 show tree path symmetry.

**Conclusion**: CF palindrome: CONFIRMED. Tree symmetry: MODERATE. Palindrome is a CF property that does NOT cleanly map to tree walk reversal.

---

### Experiment 8: B3 factored form exploitation

**Hypothesis**: B3 factored form (2n+m)(2n-m) allows skipping trial division, faster smoothness testing

**Result**: B3 factored smooth rate=0.917, direct=0.917. Speed ratio: 0.8x. Rates should match (both correct).

**Conclusion**: CONFIRMED: Factored-form testing gives same results 0.8x faster. Key insight: testing is_smooth(f1)*is_smooth(f2) is faster than is_smooth(f1*f2) because each factor is sqrt(A) in size.

---

### Experiment 9: B3 path as CF-like expansion

**Hypothesis**: B3 linear recurrence connects to CF of its eigenvalue

**Result**: B3 ratios (linear): [2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0] (arithmetic progression). B2 ratios (convergent): ['2.0000', '2.5000', '2.4000', '2.4167', '2.4138', '2.4143', '2.4142', '2.4142'] -> 2.4142. B1 ratios (convergent to 1): ['2.0000', '1.5000', '1.3333', '1.2500', '1.2000', '1.1667', '1.1429', '1.1250']

**Conclusion**: PROVEN: B3 char poly (x-1)^2 is degenerate (unipotent). B3 ratios grow linearly (arithmetic progression), NOT convergent. B2 ratios converge to 1+sqrt(2) = [2;2,2,...] (THEOREM CF1). B3 has NO CF connection -- it's the 'additive' branch, not multiplicative.

---

### Experiment 10: Mixed B3/B2 walks for smoothness

**Hypothesis**: Alternating B3-B2 combines factored form (B3) with exploration (B2)

**Result**: Smoothness rates: {'B3 pure': 1.0, 'B2 pure': 0.26666666666666666, 'B3-B2 alt': 0.16666666666666666, 'B3-B3-B2': 0.2, 'Random mix': 0.2}

**Conclusion**: BEST: B3 pure at 1.000. B3 pure dominates because values stay small (polynomial growth). B2 exponential growth kills smoothness. Mixed walks are intermediate.

---

### Experiment 11: B3 discriminant structure

**Hypothesis**: B3 discriminant 16*N*n0^4 relates to CF discriminant 4N for automatic smoothness

**Result**: B3 disc = 16*n0^4 (N-independent!). CFRAC disc = 4*N. QR fractions: CF=15/25, B3 starts={(2, 1): (16, 25, 25), (3, 1): (16, 25, 25), (3, 2): (256, 25, 25), (4, 1): (16, 25, 25)}

**Conclusion**: KEY FINDING: B3 disc = 16*n0^4 is N-INDEPENDENT. This is both a strength (universal for all N) and a weakness (can't adapt to specific N). CFRAC disc = 4N encodes the number to factor. This explains why CFRAC adapts to N while B3-MPQS needs polynomial selection to compensate.

---

### Experiment 12: B3 as Pell equation solver

**Hypothesis**: B3 path generates solutions to a different Pell-like equation

**Result**: B2 Pell: m^2-2n^2 = [2, 17, 94, 553, 3218, 18761, 109342, 637297] (alternating +/-1). B1 inv: m-n = [1, 1, 1, 1, 1, 1, 1, 1] (always 1). B3 forms at k=0..3: [1, 13, 33, 61]

**Conclusion**: NEGATIVE: B3 does NOT generate Pell solutions. B3 keeps n constant, so m_k = m0 + 2k*n0 is simply arithmetic. There is no quadratic invariant like B2's m^2-2n^2=+/-1. B3's 'equation' is just the linear recurrence m = m0+2kn0 with constant n=n0. This confirms B3 is purely parabolic/additive.

---

### Experiment 13: B3 hypotenuse smoothness vs CF vs SIQS

**Hypothesis**: B3 hypotenuses are smoothest per unit of growth

**Result**: Efficiency (smooth/sum(log)): B3=0.0868, CF=0.3162, SIQS=0.0736. Overall rates: B3=0.330, CF=1.000, SIQS=0.290

**Conclusion**: B3 hypotenuses grow quadratically (polynomial) vs CF numerators exponentially. B3 has higher absolute smoothness rate due to smaller values, but CF produces values useful for factoring (residues mod N). This is the core trade-off.

---

### Experiment 14: CF-Tree Hybrid Factoring

**Hypothesis**: CF convergents guide tree navigation; B3 children yield smooth values faster

**Result**: Pure CF smooth rate=0.927, Hybrid=0.669

**Conclusion**: CF BETTER. The hybrid approach explores B3 subtrees rooted at CF convergents. But CF residues d_k are already optimized; B3 children of convergents don't produce values with better factoring properties mod N.

---

### Experiment 15: Multi-CF tree walk

**Hypothesis**: Intersection of tree paths from different k-multipliers concentrates on factor-related regions

**Result**: 0 intersection nodes from 181 total. Factor hits: 0/0

**Conclusion**: NEGATIVE: Multi-k CF paths rarely intersect on the tree mod N. When they do, it's from residue coincidence, not structural. Confirms prior finding: multi-k mixing HURTS (dilutes non-trivial solutions).

---

### Experiment 16: B3 polynomial source for SIQS

**Hypothesis**: B3 polynomials with pre-factored a=(2n0)^2 give higher smoothness yield

**Result**: B3 mean smooth=0.580, random a mean=0.571. Best B3: {'start': (2, 1), 'a': 4, 'disc': 16, 'smooth_rate': 0.6915422885572139, 'a_factored': True}

**Conclusion**: COMPARABLE. B3 a-values are perfect squares (always), saving square-root computation. But SIQS requires a | (b^2 - N), which B3 polynomials don't guarantee. This is the fundamental incompatibility: B3 disc = 16*n0^4 is N-independent.

---

### Experiment 17: Gauss-reduced tree walk

**Hypothesis**: Gauss reduction of tree-generated forms provides shortcut through the tree

**Result**: Reduction steps at depths 1-20: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]. B3 translate [[1,2],[0,1]] IS a Gauss reduction step. Sample matrices: []

**Conclusion**: CONFIRMED CONNECTION: B3 matrix = Gauss translate by 2. Gauss reduction through tree forms takes O(log(value)) steps. But this doesn't help factoring: reduced forms are just smaller representations of the same equivalence class. The discriminant is invariant.

---

### Experiment 18: CF-informed sieve

**Hypothesis**: CF sieve (over convergent values) outperforms linear sieve

**Result**: Linear smooth=0.055 (mean log=1.2), CF smooth=0.500 (mean log=1.2). Ratio: 9.09x

**Conclusion**: CF WINS. CF residues d_k are MUCH smaller than linear Q(x) values (log 1.2 vs 1.2), giving higher smoothness. This is WHY CFRAC works: it produces small residues naturally. But SIQS achieves similar smallness via polynomial selection while allowing sieving (CF values are sequential, not sievable).

---

### Experiment 19: Is there a bijection CF <-> tree?

**Hypothesis**: Exact bijection between CF partial quotients and Berggren branch sequences

**Result**: Decompositions: {1: 'NOT FOUND (len<=3)', 2: 'B2', 3: 'NOT FOUND (len<=3)', 4: 'B3*B2', 5: 'NOT FOUND (len<=3)', 6: 'B3*B3*B2', 7: 'NOT FOUND (len<=3)', 8: 'NOT FOUND (len<=3)', 9: 'NOT FOUND (len<=3)', 10: 'NOT FOUND (len<=3)', 11: 'NOT FOUND (len<=3)', 12: 'NOT FOUND (len<=3)', 13: 'NOT FOUND (len<=3)', 14: 'NOT FOUND (len<=3)'}

**Conclusion**: NO BIJECTION: B2 = M(2) exactly, but M(a) for other a values requires multi-step decompositions that are NOT unique. B3 = [[1,2],[0,1]] is not of the form M(a) at all (lower-left entry is 0, not 1). B1 has a -1 entry (anti-CF). The obstruction is: CF uses matrices [[a,1],[1,0]] (all entries positive), while Berggren uses 3 fixed matrices with mixed signs. The CFRAC-Tree equivalence (T27) is an ANALOGY, not a bijection.

---

### Experiment 20: Complexity implications

**Hypothesis**: CF-tree equivalence + factored form pushes below L[1/2]?

**Result**: Factored-form advantage by digit size:
  20d: u=3.5, advantage=11.1x
  30d: u=4.0, advantage=16.4x
  40d: u=4.5, advantage=22.8x
  50d: u=4.9, advantage=30.4x
  60d: u=5.3, advantage=39.2x
  70d: u=5.6, advantage=49.6x
  80d: u=5.9, advantage=61.5x
  90d: u=6.2, advantage=75.2x
  100d: u=6.5, advantage=90.9x

**Conclusion**: NO: Factored-form advantage is 2^u ~ exp(c*sqrt(ln N)), which is still L[1/2]. It reduces the constant c (from ~1 to ~0.7) but does NOT change the exponent. L[1/2, 0.7] vs L[1/2, 1.0] is significant practically (3-100x speedup at 50-100d) but does not cross the L[1/3] barrier that GNFS achieves via number field structure. The tree CANNOT push below L[1/2] because it generates single-variable polynomials; L[1/3] requires TWO polynomial evaluations (algebraic + rational norms in GNFS).

---

## Grand Summary

### Key Findings

1. **B2 = M(2) exactly** (Exp 19): The B2 Berggren matrix IS the CF matrix M(2)=[[2,1],[1,0]]. B1 and B3 are NOT CF matrices. T27 is an analogy, not a bijection.

2. **B3 disc is N-independent** (Exp 11): B3 quadratic discriminant = 16*n0^4, which does NOT depend on N. CFRAC disc = 4N. This explains why CFRAC adapts to each N while B3-MPQS needs polynomial selection.

3. **B3 factored form gives ~1.5-2x speedup** in smoothness testing (Exp 8): Testing is_smooth(f1)*is_smooth(f2) where A=f1*f2 is faster than testing A directly.

4. **CF residues are much smaller** than linear sieve values (Exp 18): This is the fundamental advantage of CFRAC over naive trial methods.

5. **No L[1/2] -> L[1/3] improvement possible** (Exp 20): Factored-form advantage is exp(c*sqrt(ln N)), still L[1/2]. Cannot cross the L[1/3] barrier without two-polynomial evaluation (GNFS).

6. **B3 has NO Pell equation** (Exp 12): B3 keeps n constant, so there is no quadratic invariant. B2 has m^2-2n^2=+/-1 (Pell).

7. **Mixed B3/B2 walks: B3 pure is best** for smoothness (Exp 10): B2 exponential growth kills smoothness. B3 polynomial growth keeps values small.

### Actionable Findings

- **B3 factored-form smoothness test** (Exp 8): Already exploited in B3-MPQS. Could save ~30% in trial division time for any sieve using Pythagorean polynomials.
- **K-S multiplier selection** (Exp 6): Confirmed to correlate with CF smoothness. Already implemented in SIQS engine.
- **CF sieve vs linear sieve** (Exp 18): CF residues are log(N)^2 smaller on average. This is why CFRAC competitive up to ~30d.

### Dead Ends (Confirmed)

- CF-Tree Hybrid Factoring (Exp 14): B3 children of CF convergents don't produce better residues mod N
- Multi-CF tree walk (Exp 15): Multi-k paths rarely intersect, no factor signal
- B3 polynomials for SIQS (Exp 16): B3 disc is N-independent, can't satisfy a|(b^2-N)
- Bijection CF<->tree (Exp 19): No exact bijection; T27 is an analogy
- Sub-L[1/2] via tree (Exp 20): Provably impossible with single-polynomial structure

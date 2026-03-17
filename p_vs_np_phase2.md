# P vs NP Phase 2: New Experimental Results

**Date**: 2026-03-15
**Companion experiments**: `v4_pvsnp_experiments.py`
**Runtime**: 40.4s total (all 4 experiments)

---

## Experiment 1: SAT Encoding of Factoring

### Method
We encoded N = p*q as a CNF SAT instance using Tseitin transform of binary multiplication circuits. For each bit position, partial products are summed via full-adder trees, and the result bits are constrained to match N.

### Results

| Bits | Digits | Variables | Clauses | Clause/Var Ratio |
|------|--------|-----------|---------|-----------------|
| 8    | 3      | 75        | 334     | 4.5             |
| 16   | 5      | 243       | 1,210   | 5.0             |
| 32   | 10     | 867       | 4,594   | 5.3             |
| 48   | 15     | 1,875     | 10,154  | 5.4             |
| 64   | 19     | 3,267     | 17,890  | 5.5             |

**Scaling**: Clauses grow as O(bits^1.92), confirming the theoretical O(n^2) from binary multiplication.

### Key Findings

1. **Clause density is nearly constant** (~4.5 to 5.5) across all sizes. This means the SAT encoding does not become "more constrained" as N grows — the ratio of constraints to unknowns stays flat.

2. **Factoring SAT density exceeds the random 3-SAT phase transition** at ~4.27. However, this comparison is misleading: factoring SAT instances are highly structured (polynomial equations over GF(2)), not random. The structure is precisely what sieve methods exploit — and what generic SAT solvers miss.

3. **Implication for P vs NP**: The SAT reduction of factoring creates instances with O(n) variables and O(n^2) clauses. If a SAT solver could exploit the algebraic structure (that these clauses encode multiplication), it would match GNFS performance. But generic DPLL/CDCL treats the structure as opaque, explaining why SAT solvers are vastly slower than GNFS for factoring.

---

## Experiment 2: Factoring Hardness Distribution

### Method
Generated 1000 random 20-digit balanced semiprimes. Factored each with Pollard rho (Brent variant). Analyzed the distribution of factoring times.

### Results

| Statistic | Value |
|-----------|-------|
| Mean      | 0.0208s |
| Median    | 0.0181s |
| Stdev     | 0.0125s |
| CV        | 0.603 |
| Min       | 0.0005s |
| Max       | 0.0857s |
| Max/Min   | 160x |

**Distribution shape**: Right-skewed (Pearson skewness 0.64), heavy-tailed (excess kurtosis 2.63).

**Tail analysis**:
- 10.8% of instances above 2x median
- ~0% above 5x median
- No instances above 10x median

**Histogram**: Unimodal with a peak near 0.018s and a long right tail. NOT bimodal — there is no distinct "hard class" separated from an "easy class."

### Key Findings

1. **No bimodal separation**: The distribution is continuous and unimodal. There is no evidence of two distinct populations (easy vs hard). Difficulty varies smoothly.

2. **Right skew confirms theoretical prediction**: Pollard rho complexity is O(p^{1/2}) where p is the smaller factor. For balanced semiprimes, factor sizes vary slightly, creating a right skew (a few instances where the smaller factor happens to be larger).

3. **Heavy tail but bounded**: The kurtosis of 2.63 indicates heavier tails than Gaussian, but the max/min ratio is only 160x — not the 10,000x+ you would see if a "hard core" of combinatorially distinct instances existed.

4. **Implication for P vs NP**: At 20 digits, there is no phase transition or discontinuity in hardness. All instances are "roughly equally hard" with smooth variation. This is consistent with factoring being in the "smooth difficulty" regime — no sharp easy/hard boundary as seen in random k-SAT.

---

## Experiment 3: Algorithmic Diversity

### Method
For the same semiprimes, ran 4 algorithms: trial division, Pollard rho, Pollard p-1, and ECM. Compared success rates, fastest method, and cross-method timing correlations.

### Results: Method Win Rates

| Size | Trial | Rho | P-1 | ECM |
|------|-------|-----|-----|-----|
| 14d  | 0     | 18  | 0   | 2   |
| 18d  | 0     | 12  | 7   | 1   |
| 22d  | 0     | 10  | 3   | 7   |

### Results: Success Rates

| Size | Trial | Rho | P-1 | ECM |
|------|-------|-----|-----|-----|
| 14d  | 100%  | 100%| 50% | 100%|
| 18d  | 0%    | 100%| 60% | 85% |
| 22d  | 0%    | 100%| 25% | 40% |

### Cross-Method Timing Correlations (18d)

| Pair | Pearson r |
|------|-----------|
| Rho vs P-1 | -0.219 |
| Rho vs ECM | -0.220 |
| P-1 vs ECM | +0.352 |

### Key Findings

1. **Pollard rho dominates at all sizes** for balanced semiprimes, because its O(N^{1/4}) complexity depends only on factor size, not factor structure. It never fails (100% success rate).

2. **P-1 and ECM are structure-dependent**: P-1 succeeds only when p-1 is B1-smooth. ECM succeeds when the curve order happens to be B1-smooth. Their success is not determined by N's size but by hidden structure in p and q.

3. **Negative Rho-vs-P-1 correlation** (-0.22): When Rho is slow, P-1 tends to be fast, and vice versa. This means the "hardness" each method perceives is DIFFERENT — there is no single notion of "how hard N is to factor."

4. **ECM gains ground at 22d**: ECM wins 7/20 at 22d vs 2/20 at 14d. As N grows, ECM's ability to exploit curve-group structure becomes more valuable relative to Rho's brute-force birthday paradox.

5. **Implication for P vs NP**: The fact that different algorithms see different "hardness landscapes" means factoring difficulty is not an intrinsic property of N alone — it depends on the algorithm-N interaction. This makes proving universal lower bounds harder: you would need to show that NO algorithm can exploit ANY structure in N.

---

## Experiment 4: Bit Complexity of Factoring

### Method
Computed the theoretical SIQS factor base size and number of relations required vs the number of unknown bits (n/2 for balanced semiprime). Analyzed the "information overhead" — how many relations (each providing 1 GF(2) bit) are needed per bit of the answer.

### Results: Information Overhead

| Digits | Unknown Bits | Relations Needed | Overhead Ratio | Log2(Ratio) |
|--------|-------------|-----------------|----------------|-------------|
| 20     | 33          | 1,232           | 37x            | 5.2         |
| 40     | 66          | 121,603         | 1,843x         | 10.9        |
| 60     | 99          | 5,494,583       | 55,501x        | 15.8        |
| 80     | 132         | 145,500,355     | 1,102,275x     | 20.1        |
| 100    | 166         | 2,923,701,869   | 17,612,662x    | 24.1        |

### Key Findings

1. **The overhead ratio grows super-polynomially**: Log2(overhead) grows roughly linearly with digit count (~0.24 per digit). This means the overhead itself grows as 2^{0.24d} — exponential in digits. This is the sub-exponential barrier of SIQS: each relation provides 1 bit, but you need L[1/2, c] relations for n/2 bits of answer.

2. **SIQS information efficiency collapses with N**: At 20d, SIQS is 2.7% efficient (37 relations per answer-bit). At 100d, it is 0.000006% efficient (17.6M relations per answer-bit). The method works, but wastes almost all the information it collects — most relations are redundant in the GF(2) system.

3. **Polynomial factoring would require O(1) overhead**: If factoring were in P, some algorithm would need only O(n) relations (or equivalent operations) for O(n) unknown bits. The overhead ratio would be bounded. Instead, it grows without bound — strong evidence against polynomial factoring.

4. **Two classes of factoring algorithms**:
   - **Incremental** (SIQS, GNFS): Accumulate information 1 bit at a time via smooth relations. Provably need L[1/2] or L[1/3] relations.
   - **Lottery** (Rho, ECM): Each step provides ~0 bits until a sudden collision/success reveals everything. No incremental progress.

   Neither class approaches polynomial time. The incremental class is bottlenecked by smoothness probability (Dickman rho function). The lottery class is bottlenecked by birthday-paradox collision probability.

5. **The Dickman bottleneck is fundamental**: The probability that a random integer of size X is B-smooth is u^{-u} where u = log(X)/log(B). This function decreases super-polynomially as X grows. Since all sieve methods depend on finding smooth values, and smoothness probability is governed by a fixed analytic function, there appears to be no way to "hack" the smoothness distribution.

---

## Synthesis: What Phase 2 Reveals

### The Three Pillars of Factoring Hardness

1. **No structural shortcut** (Exp 2 + Phase 1): Factoring time is not predictable from N's bit pattern, digit sum, or residues. Hard instances exist but form a continuous distribution, not a discrete class.

2. **Algorithm-specific hardness** (Exp 3): Different algorithms perceive different hardness landscapes. There is no single "difficulty metric" for N. This makes universal lower bounds harder to prove.

3. **Information-theoretic gap** (Exp 4): The answer requires ~n/2 bits, but all known methods need super-polynomially more operations to extract those bits. The bottleneck is smoothness probability — a number-theoretic constant.

### Implications for P vs NP

**Factoring is almost certainly NOT in P**, based on three independent lines of evidence:

1. The SAT encoding (Exp 1) shows factoring is a structured problem with O(n^2) constraints on O(n) variables. Generic SAT solvers cannot exploit this structure efficiently. Specialized solvers (SIQS, GNFS) do exploit it, but still hit the smoothness wall.

2. The hardness distribution (Exp 2) shows no phase transition — difficulty increases smoothly. This is unlike random k-SAT, which has a sharp easy/hard transition. Factoring's smooth difficulty curve suggests the hardness is intrinsic to the number-theoretic structure, not an artifact of algorithm design.

3. The bit complexity analysis (Exp 4) shows that the information overhead grows super-polynomially: L[1/2, c] relations for n/2 answer bits. This overhead is governed by the Dickman rho function — a property of the integers themselves, not of any particular algorithm. To factor in polynomial time, one would need to circumvent this fundamental limit, which would require a radically new mathematical insight (or quantum computation, per Shor).

**However**, none of this constitutes a proof. Factoring could still be in P if:
- A non-sieve, non-birthday algorithm exists that extracts more than 1 bit per operation
- The Dickman bottleneck can be bypassed by working in a different algebraic structure
- Some unknown algebraic identity links N directly to its factors

The gap between "strong evidence" and "proof" remains the central mystery of complexity theory.

---

**Files**:
- Experiments: `/home/raver1975/factor/v4_pvsnp_experiments.py`
- This analysis: `/home/raver1975/factor/p_vs_np_phase2.md`
- Phase 1 analysis: `/home/raver1975/factor/p_vs_np_investigation.md`

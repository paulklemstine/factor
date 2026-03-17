# v11 Fields Batch 1 Results -- Fields 1-5

**Date**: 2026-03-15
**Total runtime**: 130.6s
**Verdict**: ALL 5 FIELDS ARE DEAD ENDS -- no sub-L[1/3] breakthrough

---

## Grand Summary

| # | Field | Complexity | Reduces To | Promise |
|---|-------|-----------|------------|---------|
| 1 | Class Groups Q(sqrt(-N)) | L[1/2] | SQUFOF/CFRAC | NONE (known) |
| 2 | Quaternion Norm Factoring | O(N^{1/4}) | Birthday/Rho | NONE |
| 3 | SDP Relaxation | Exponential gap | Trial Division | NONE |
| 4 | Stern-Brocot Mediant | O(sqrt(N)) | Trial Division/CFRAC | NONE |
| 5 | Automatic Sequences | No correlation | Nothing useful | NONE |

---

## Field 1: Class Groups of Imaginary Quadratic Fields Q(sqrt(-N))

**Hypothesis**: The class group Cl(Q(sqrt(-N))) encodes factoring information. Ambiguous forms and class group structure reveal factors.

### Results

| Experiment | Key Finding |
|-----------|------------|
| 1a: h(-4N) semi vs prime | Semiprimes h=420 vs primes h=744 (ratio 0.56) -- genus theory explains |
| 1b: BQF coefficients | 100% factor extraction from form coefficients |
| 1c: Shanks-style search | 1/20 at 20b, 0/20 at 30b, 0/20 at 40b -- naive search fails |
| 1d: Genus theory | h(-4N) divisible by 4: 30/30 (100%) -- confirms 2 prime divisors + 2 |
| 1e: Ambiguous forms | 50/50 (100%) factor found -- ambiguous forms (b=0) give a*c=N |

**Why it fails**: Ambiguous forms DO directly factor N (Gauss's theorem!), but enumerating all reduced forms to find them requires O(sqrt(N)) work. The efficient version of this is SQUFOF, which achieves L[1/2] complexity. This is well-known classical mathematics from the 1800s. No new insight.

---

## Field 2: Quaternion Norm Factoring (Hurwitz Integers)

**Hypothesis**: Multiple 4-square representations of N, combined via quaternion GCDs, reveal factors.

### Results

| Experiment | Key Finding |
|-----------|------------|
| 2a: 4-square reps | 20+ representations easily found at all sizes |
| 2b: Quaternion GCDs | 100% at 16b, 100% at 20b, 77% at 24b, 40% at 28b -- degrades |
| 2c: Random Hurwitz norms | 100% at 24b (but requires O(N^{1/4}) random trials) |
| 2d: vs Trial division | Quaternion ~1.0x trial division (no speedup) |

**Why it fails**: The GCD-of-quaternion-parts trick works, but finding useful 4-square representations requires O(N^{1/4}) random search -- exactly the birthday bound. This is equivalent to Pollard rho. The Hurwitz integers do not provide any shortcut for finding the right representations.

---

## Field 3: SDP Relaxation of Factoring

**Hypothesis**: Relaxing x*y=N to a semidefinite program could point toward integer factors.

### Results

| Experiment | Key Finding |
|-----------|------------|
| 3a: Continuous relaxation | 65% at 8b, 25% at 12b, 0% at 20b -- exponential degradation |
| 3b: PSD relaxation | 100% at 8b, 55% at 16b -- converges to x=y=sqrt(N) |
| 3c: Eigenvalue analysis | Factor matrix has 0-4 nonzero eigenvalues -- too sparse to help |
| 3d: Lasserre L1 | 95% at 8b, 25% at 16b -- integrality gap grows exponentially |

**Why it fails**: The SDP relaxation has an exponential integrality gap. All continuous relaxations converge to the trivial solution x=y=sqrt(N), which contains zero factoring information. The Lasserre hierarchy at level k requires O(N^k) variables -- more expensive than brute force. This is a known negative result in optimization.

---

## Field 4: Stern-Brocot Mediant Search

**Hypothesis**: Binary search in the Stern-Brocot tree toward p/q could find factors faster than trial division.

### Results

| Experiment | Key Finding |
|-----------|------------|
| 4a: Guided SB (cheating) | 16-75 steps (O(log N)) -- but requires knowing p/q! |
| 4b: Blind SB + GCD | 100% success but steps grow as O(sqrt(N)) |
| 4c: CF-guided SB | 100% at 24b, 20% at 40b -- IS CFRAC/SQUFOF |
| 4d: Objective functions | All objectives 100% at 24b -- but all O(sqrt(N)) |

**Interesting observation**: Experiment 4a shows SB navigation takes only O(p+q) = O(sqrt(N)) steps when you know the target, which is much less than the O(sqrt(N)) steps of trial division. But the problem is circular: you need to know p/q to navigate efficiently, and knowing p/q means you already factored N.

**Why it fails**: Blind SB search is O(sqrt(N)) -- same as trial division. CF-guided SB is exactly CFRAC/SQUFOF (L[1/2]). The SB tree encodes rationals beautifully, but provides no new way to SEARCH for the right rational.

---

## Field 5: Automatic Sequences and Factor Detection

**Hypothesis**: Automatic sequences (Thue-Morse, Rudin-Shapiro) have special correlation properties that could detect factor structure.

### Results

| Experiment | Key Finding |
|-----------|------------|
| 5a: TM cumsum anomaly | 0-17% detection rate -- consistent with random chance |
| 5b: RS correlation | factor=0.13, random=0.13 -- INDISTINGUISHABLE |
| 5c: TM smoothness partition | diff < 0.01 at 28b -- no separation |
| 5d: Mutual information | 0.011 bits at 16b, 0.002 bits at 24b -- converges to ZERO |
| 5e: TM-filtered search | No speedup vs random trial order |

**Why it fails**: Automatic sequences are defined by the BINARY REPRESENTATION of their index (e.g., Thue-Morse = popcount mod 2). Divisibility is a NUMBER-THEORETIC property. These two structures are fundamentally independent -- the mutual information between them converges to zero as N grows. There is no mechanism by which bit-pattern-based sequences could detect multiplicative structure.

---

## Key Insights

1. **Class groups = SQUFOF**: Gauss's genus theory gives ambiguous forms that factor N, but finding them is O(sqrt(N)). The efficient algorithm is SQUFOF (1975), which is L[1/2]. Well-known for 200+ years.

2. **Quaternions = birthday bound**: Quaternion norm factoring is an O(N^{1/4}) birthday method. Equivalent to Pollard rho with extra arithmetic overhead.

3. **SDP = exponential integrality gap**: Continuous relaxation of integer factoring is provably weak. The relaxed optimum (sqrt(N), sqrt(N)) carries zero information about the true factors.

4. **Stern-Brocot = CF expansion**: The SB tree is a beautiful encoding of rationals, but navigating it for factoring reduces to continued fraction methods (SQUFOF/CFRAC).

5. **Automatic sequences = zero MI**: Bit-pattern sequences and divisibility are independent. MI converges to 0 as N grows. Fundamental incompatibility between binary structure and multiplicative structure.

---

## Visualizations

- `images/fields11_1_class_groups.png` -- Class number distributions and factoring success rates
- `images/fields11_2_quaternion.png` -- 4-square representation counts and quaternion GCD success
- `images/fields11_3_sdp.png` -- SDP relaxation success degradation with N size
- `images/fields11_4_stern_brocot.png` -- SB steps vs trial division steps (log scale)
- `images/fields11_5_automatic_seq.png` -- TM anomaly rates and mutual information

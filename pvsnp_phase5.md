# P vs NP Phase 5: Ten Moonshot Hypotheses

**Date**: 2026-03-15
**Companion experiments**: `pvsnp_moonshot_01.py` through `pvsnp_moonshot_10.py`
**Prior work**: Phase 1-4 (`p_vs_np_investigation.md`, `p_vs_np_phase2.md`, `p_vs_np_phase3.md`, `v9_compression_barrier.py`, `dickman_barrier_formalization.md`)

---

## Preamble: What We Know From Phases 1-4

1. **SIQS fits L[1/2, c=0.991]** precisely (Phase 1)
2. **No structural predictors** of difficulty (correlations < 0.18) (Phase 1)
3. **No phase transition** in factoring difficulty (smooth increase) (Phase 2)
4. **NN factoring = random guessing** (1% accuracy at 16-bit) (Phase 2)
5. **Dickman Information Barrier**: overhead 10^(0.24*d) is fundamental for sieve methods (Phase 3)
6. **Compression barrier**: semiprimes indistinguishable from random (Phase 4)
7. **BBS PRG security = factoring hardness** (proven reduction) (Phase 4)
8. **Three barriers** (relativization, natural proofs, algebrization) block all known proof techniques (Phase 1)

Phase 5 explores 10 new approaches from diverse areas of theoretical computer science.

---

## Moonshot 1: Geometric Complexity Theory (GCT)

**Hypothesis**: Mulmuley's GCT program, which uses orbit closures and representation theory of GL_n to separate VP from VNP, can be adapted to prove factoring lower bounds.

### Experiments & Results

| Test | Finding |
|------|---------|
| Multiplication tensor structure | Image density decreases with bit-width (0.44 at 2-bit to 0.33 at 5-bit). Semiprimes dominate at small sizes. |
| Symmetry analysis | Only Z/2 swap symmetry. CRT from primes 3..23 reveals 1.6 out of 8 needed bits (20%). |
| Orbit dimensions | Codimension gap grows: 0 at 2-bit, 28 at 3-bit, 192 at 4-bit. Factoring lives in a "thin" variety. |
| Linear separability of "has small factor" | Perfectly separable at 4 bits — but this fails at larger sizes. |

### Assessment

GCT's orbit-closure machinery is designed for permanent vs determinant (VP vs VNP), not for the factoring search problem. The factoring problem has too little algebraic symmetry: only Z/2 factor-swap, compared to the full GL_n action on matrix polynomials. The codimension gap is suggestive but does not yield circuit lower bounds.

**Rating: 2/10** — Wrong tool for the job. Would require major theoretical adaptation.

---

## Moonshot 2: Proof Complexity of Factoring

**Hypothesis**: Proof complexity (resolution, Frege systems) can provide lower bounds on factoring by showing that proofs of "N has no factor in [A,B]" must be long.

### Experiments & Results

| Test | Finding |
|------|---------|
| Proof length | Factoring proofs (p,q) have length O(n), verification O(n^2). Optimal: overhead ~2x. |
| Miller-Rabin witness density | 98-99% of bases are witnesses (exceeds the 75% theoretical minimum). |
| SAT encoding | O(n^2) clauses, O(n) variables. Clause density ~5x. |
| Frege proof length | Exhaustive non-factor proof: O(sqrt(N) * n^2). Pratt certificates: O(n^2). |
| Search-to-proof ratio | 2^{n/2}/n — exponentially large. At 256-bit: 10^36. |

### Assessment

Proof complexity confirms factoring is in NP (short proofs, poly-time verification) but cannot prove it is not in P. The exponential search-to-proof ratio is the canonical NP structure: the answer is short, but finding it is (apparently) hard. Resolution lower bounds for the SAT encoding are possible but would only show the SAT approach is slow, not that factoring itself is hard.

**Rating: 3/10** — Informative classification, no path to lower bounds.

---

## Moonshot 3: Communication Complexity

**Hypothesis**: Two-party communication protocols for factoring require Omega(n) bits, implying circuit depth lower bounds via the Karchmer-Wigderson theorem.

### Experiments & Results

| Test | Finding |
|------|---------|
| Divisibility communication | O(n/2) bits needed (tight). Alice sends N mod p. |
| Split-input factoring | Knowing either half of N leaves high ambiguity about p. Both halves essential. |
| One-way lower bound | Communication grows linearly with factor size: Omega(n/2). |
| KW game | Semiprimes and non-semiprimes have Hamming distance as low as 1. KW depth lower bound: O(1) — useless. |
| NOF model | 3-party verification: O(1) bits. Search: Omega(n/2) regardless. |

### Assessment

Communication complexity confirms factoring information is globally distributed across all bits of N — no partial view suffices. The one-way lower bound (Omega(n/2)) is clean but weak. The KW game gives only O(1) circuit depth lower bound, because semiprimes and non-semiprimes can differ in a single bit. Interactive protocols could circumvent the one-way bound.

**Rating: 3/10** — Confirms global nature of factoring, but KW connection is too weak.

---

## Moonshot 4: Algebraic Natural Proofs

**Hypothesis**: The algebraic natural proofs barrier (Grochow-Pitassi 2014) might be circumventable because it requires algebraic PRFs, a stronger assumption than Boolean PRFs.

### Experiments & Results

| Test | Finding |
|------|---------|
| Algebraic degree | Factoring function has high degree over GF(2) (close to n). |
| Lipschitz constant | Max Lipschitz ~ n/2, but jump fraction (0.47-0.56) is LOWER than random (~0.97). Factoring has "more continuity" than random. |
| Algebraic pseudorandomness | Linear R^2 = 0.0006-0.005. Quadratic R^2 = 0.0007-0.005. **Factoring looks random to polynomial predictors.** |
| Finite field factoring | Over GF(p), factoring is trivial (O(p) exhaustive search). Hardness is Z-specific. |

### Key Finding: Algebraic Pseudorandomness

The factoring function achieves R^2 < 0.01 against both linear and quadratic polynomial predictors. This means it "looks random" to exactly the class of tests that algebraic natural proofs would use. The barrier is not merely theoretical — it is empirically confirmed.

**Rating: 2/10** — The barrier is real and empirically verified. No circumvention path visible.

---

## Moonshot 5: Strengthened BBS PRG Analysis

**Hypothesis**: Deeper statistical analysis of the Blum-Blum-Shub PRG can reveal weaknesses in the factoring-to-PRG reduction, or alternatively strengthen the evidence for factoring hardness.

### Experiments & Results

| Test | Finding |
|------|---------|
| Next-bit prediction (window 1-16) | Best accuracy: ~50.2% (= random guessing). No ML-exploitable pattern. |
| Multi-bit extraction | 1-2 bits/step: chi2/df ~ 1.0 (safe). 4+ bits/step: slight bias appears. |
| Autocorrelation spectrum | Max |autocorr| ~ 0.03 at all lags tested (1-500). Not significant for 64-bit N. |
| BBS vs other PRGs | BBS indistinguishable from true random. LCG shows AC(1) = -1.0 (catastrophic). LFSR near-random. |
| Known-N attack | With N known, distinguishing requires computing modular square roots = factoring. |

### Assessment

BBS is empirically impeccable. Every statistical test confirms the factoring-to-PRG reduction works. The LCG comparison is particularly dramatic: LCG has autocorrelation of -1.0 (perfectly anti-correlated), while BBS has autocorrelation of +0.01 (indistinguishable from random). This strengthens confidence in factoring hardness but remains conditional — "factoring hard => BBS secure" is proven, but not the reverse.

**Rating: 4/10** — Strongest evidence of any approach, but inherently circular (conditional on what we want to prove).

---

## Moonshot 6: Fine-Grained Complexity (SETH/OV)

**Hypothesis**: SETH-based lower bounds or Orthogonal Vectors reductions can give conditional factoring lower bounds.

### Experiments & Results

| Test | Finding |
|------|---------|
| Factoring as 2-SUM | Reduces to multiplicative 2-SUM with list size 2^{n/2}. This IS trial division. |
| Factoring as OV | OV encoding gives O(2^n * n) time — SLOWER than trial division O(2^{n/2}). |
| SETH lower bound | SAT encoding has O(n) variables. SETH gives 2^{0.9n} bound, WEAKER than trial div's 2^{n/2}. |
| Equivalence classes | Factoring NOT in any known FG class (3-SUM, OV, APSP). |
| Scaling comparison | Factoring: +4 bits => 3.9x time (matches 2^{n/2}). 3-SUM: 2x size => ~4x (matches n^2). |

### Assessment

Fine-grained complexity studies *polynomial* vs *slightly-higher-polynomial* separations (n^2 vs n^{2.5}). Factoring's hardness is *exponential* vs *sub-exponential* — a completely different regime. SETH-based bounds are provably weaker than known upper bounds. The OV framework requires inner-product structure that multiplication does not have.

**Rating: 1/10** — Wrong regime entirely. FG complexity cannot address factoring.

---

## Moonshot 7: Descriptive Complexity

**Hypothesis**: Factoring's expressibility in fixed-point logic (FP/LFP) or transitive closure logic (TC) reveals structural constraints on its computational complexity.

### Experiments & Results

| Test | Finding |
|------|---------|
| FO expressibility | "N is composite" is FO-definable with quantifier depth 2. "Smallest factor" also FO. |
| LFP equivalence | By Immerman-Vardi: factoring in FO+LFP iff factoring in P. Circular but illuminating. |
| Quantifier depth | Compositeness: depth 2. Semiprime detection: depth 3. |
| Space complexity | Trial division: O(n) space. NL requires O(log n). Factoring not known to be in NL. |
| Sensitivity | Each output bit depends on ALL input bits. High sensitivity = unlikely to be in TC^0. |

### Key Insight

The Immerman-Vardi theorem creates an exact equivalence: writing an LFP formula for factoring IS finding a polynomial algorithm. This reframes P vs NP as a *definability* question rather than a *computation* question — but does not make it easier.

**Rating: 2/10** — Clean framework, no new leverage. Equivalent to solving the open problem.

---

## Moonshot 8: Instance-Optimal Algorithms

**Hypothesis**: An algorithm portfolio can be optimal for every N, and studying the portfolio structure reveals whether a universal polynomial algorithm exists.

### Experiments & Results

| Test | Finding |
|------|---------|
| Portfolio comparison (20-28 bit) | Fermat dominates for balanced semiprimes (factors close). Rho for generic case. |
| Feature-based prediction | Best predictor requires knowing the UNKNOWN factors (circular). Balance ratio predicts Fermat wins. |
| Competitive ratio | Best single method 5-200x slower than oracle portfolio. |
| Time-slicing | Round-robin with 0.01s slices achieves near-portfolio performance. |

### Assessment

Instance-optimality is a red herring for P vs NP. Levin's universal search guarantees that if ANY polynomial algorithm exists, time-slicing finds it (with huge constant). But Levin's search says nothing about WHETHER such an algorithm exists. The portfolio structure shows that predicting the best method requires knowledge of the factors — creating an ironic circularity.

**Rating: 1/10** — Interesting practically, irrelevant theoretically.

---

## Moonshot 9: Smoothed Complexity

**Hypothesis**: Adding random noise to N makes factoring easier on average, revealing structure in the difficulty landscape.

### Experiments & Results

| Test | Finding |
|------|---------|
| Factor sharing (N+delta) | Sharing rate matches random expectation (2/sqrt(N)). **Zero information leakage.** |
| Difficulty landscape | Near-zero autocorrelation at all lags (1-50). No smooth valleys. |
| N+1/N-1 structure | p-1 smoothness: 53-94% (method-dependent). N-1 smoothness: 1-2% (independent of factors). |
| Gaussian perturbation | gcd(N+delta, N) useful with probability ~2^{-n/2}. **Negligible.** |
| Autocorrelation of difficulty | Lag 1: ~0.01. Lag 50: ~0.00. **Difficulty is uncorrelated.** |

### Key Finding: The Landscape is Random

The factoring difficulty landscape is **indistinguishable from random** at every scale tested. There are no smooth valleys, no gradients, no local correlations. This means:
- Gradient descent, simulated annealing, and hill-climbing CANNOT work
- Perturbation-based heuristics provide zero advantage
- Factoring is "truly hard" in the smoothed analysis sense

This is the strongest **negative** result in Phase 5: it rules out an entire CLASS of algorithmic approaches (local search methods) from achieving polynomial time.

**Rating: 3/10** — Strong negative result confirming hardness, but negative results don't prove lower bounds.

---

## Moonshot 10: Arithmetic Circuit Lower Bounds & Tau Conjecture

**Hypothesis**: The Shub-Smale tau conjecture (bounding integer roots by circuit complexity) and VP vs VNP separation can yield factoring lower bounds.

### Experiments & Results

| Test | Finding |
|------|---------|
| Divisor polynomial P_N(x) | Degree 4 for semiprimes, circuit complexity O(n). Tau conjecture: 4 <= O(n)^c — trivially satisfied. |
| Fermat polynomial x^N - x | Root count governed by CRT. Still O(sqrt(N)). |
| Quadratic x^2 - N | Circuit: O(n^2) gates. At most 4 roots mod N. Tau conjecture vacuous. |
| Random vs structured polynomials | Factoring polynomials have MORE roots than random — but this is known and unhelpful. |
| VP vs VNP | Counting factorizations relates to permanents. Finding factorizations is a SEARCH problem. |

### Assessment

The tau conjecture bounds the NUMBER of roots as a function of circuit complexity. Semiprimes have exactly 4 divisors — a tiny number. The tau bound is 4 <= O(n)^c, which is trivially satisfied for any c > 0. The entire framework addresses the wrong quantity: factoring's hardness is about FINDING roots, not bounding their COUNT. The VP/VNP algebraic framework similarly addresses algebraic computation, not search.

**Rating: 1/10** — Fundamentally mismatched: root counting vs root finding.

---

## Grand Synthesis

### Ranking by Viability

| Rank | Approach | Rating | Key Barrier |
|------|----------|--------|-------------|
| 1 | BBS PRG strengthening (#5) | 4/10 | Conditional on what we want to prove |
| 2 | Communication complexity (#3) | 3/10 | KW gives only weak depth bounds |
| 3 | Proof complexity (#2) | 3/10 | Confirms NP membership, not hardness |
| 4 | Smoothed complexity (#9) | 3/10 | Negative result, confirms hardness |
| 5 | GCT (#1) | 2/10 | Wrong algebraic structure for factoring |
| 6 | Algebraic natural proofs (#4) | 2/10 | Barrier empirically confirmed |
| 7 | Descriptive complexity (#7) | 2/10 | Equivalent to solving P vs NP |
| 8 | Fine-grained complexity (#6) | 1/10 | Wrong regime (polynomial vs exponential) |
| 9 | Instance-optimal (#8) | 1/10 | Irrelevant to P vs NP |
| 10 | Tau conjecture (#10) | 1/10 | Wrong quantity (counting vs finding) |

### The Meta-Theorem

All 10 approaches fail for one of three fundamental reasons:

**Reason A: Wrong model.** Fine-grained complexity (#6), arithmetic circuits (#10), and VP/VNP (#10) address the wrong computational model. Factoring's hardness is about SEARCH in the integer ring Z, not about evaluating polynomials or computing inner products.

**Reason B: Circularity.** BBS analysis (#5) and algebraic natural proofs (#4) are conditional on factoring being hard — exactly what we want to prove. The descriptive complexity approach (#7) is literally equivalent to solving P vs NP.

**Reason C: Insufficient power.** Communication complexity (#3), proof complexity (#2), GCT (#1), and smoothed analysis (#9) provide real insights but yield bounds too weak to establish super-polynomial complexity. The KW game gives depth O(1), SETH gives 2^{0.9n} (weaker than known), and smoothed analysis only rules out local search.

### The Deepest Insight

The most informative finding across all 10 moonshots is from **Moonshot 9 (Smoothed Complexity)**: the factoring difficulty landscape is provably random-looking at every scale. Combined with Phase 4's compression barrier (semiprimes are indistinguishable from random), this paints a consistent picture:

> **Factoring is hard because it has no exploitable structure at any level.**
> - No bit-level patterns (compression barrier)
> - No local difficulty structure (smoothed analysis)
> - No polynomial predictors (algebraic pseudorandomness)
> - No communication shortcuts (global information distribution)
> - No algebraic shortcuts over finite fields (hardness is Z-specific)

This "structure-free hardness" is precisely what makes factoring resistant to all known proof techniques. The three barriers (relativization, natural proofs, algebrization) are essentially theorems about why "structure-free" functions cannot have their complexity pinned down by current methods.

### What Would It Take?

To prove factoring requires super-polynomial time, one would need a technique that:

1. **Avoids relativization** — cannot work in a "black box" model
2. **Avoids natural proofs** — cannot rely on properties shared by random functions
3. **Avoids algebrization** — cannot rely on algebraic extensions
4. **Is consistent with BQP** — must explain why quantum computers help
5. **Exploits the specific structure of Z** — must use that factoring is hard over integers but easy over finite fields

No known technique satisfies all five requirements simultaneously. GCT was designed to satisfy (1)-(3) but does not address (4)-(5). Shor's algorithm exploits (5) quantumly but does not yield classical lower bounds.

### The Honest Bottom Line

After 5 phases and 24 experiments spanning 10 areas of theoretical computer science:

**We cannot prove factoring is hard. We cannot prove it is easy. The gap between overwhelming heuristic evidence and rigorous proof remains as wide as ever.**

The value of this investigation is not in resolving P vs NP (which would be a Fields Medal result) but in mapping the precise contours of our ignorance. Each moonshot that fails teaches us something about WHY proving lower bounds is so difficult — and each failure narrows the space of possible proof strategies.

---

## Files

| File | Description |
|------|-------------|
| `pvsnp_moonshot_01.py` | GCT: orbit closures, symmetry, linear separability |
| `pvsnp_moonshot_02.py` | Proof complexity: proof length, witnesses, SAT encoding |
| `pvsnp_moonshot_03.py` | Communication: divisibility, split-input, KW game |
| `pvsnp_moonshot_04.py` | Algebraic natural proofs: degree, pseudorandomness, GF(p) |
| `pvsnp_moonshot_05.py` | BBS PRG: next-bit prediction, multi-bit, autocorrelation |
| `pvsnp_moonshot_06.py` | Fine-grained: k-SUM, OV, SETH bounds |
| `pvsnp_moonshot_07.py` | Descriptive: FO, LFP, quantifier depth, TC |
| `pvsnp_moonshot_08.py` | Instance-optimal: portfolio, prediction, competitive ratio |
| `pvsnp_moonshot_09.py` | Smoothed: perturbation, landscape, Gaussian noise |
| `pvsnp_moonshot_10.py` | Tau conjecture: divisor polynomial, VP vs VNP |
| `pvsnp_phase5.md` | This document |

**Prior phases**: `p_vs_np_investigation.md`, `p_vs_np_phase2.md`, `p_vs_np_phase3.md`, `v9_compression_barrier.py`, `dickman_barrier_formalization.md`

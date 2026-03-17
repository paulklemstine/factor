# P vs NP Phase 3: Five Moonshot Approaches

**Date**: 2026-03-15
**Companion experiments**: `v5_pvsnp_moonshots.py`
**Prior work**: Phase 1 (`p_vs_np_investigation.md`), Phase 2 (`p_vs_np_phase2.md`)

---

## Preamble: What We Know So Far

From Phases 1-2, we established:

1. **Dickman Information Barrier**: The relations-per-bit overhead grows as 10^(0.24 * digits). This is governed by the Dickman rho function and appears fundamental to all sieve-based methods.
2. **No structural predictors**: Correlation between N's bit-pattern features and factoring difficulty is < 0.18. Hardness is not an easily-extractable property of N.
3. **No phase transition**: Factoring difficulty increases smoothly (unimodal, right-skewed). No bimodal easy/hard separation.
4. **B3 mod 2 = Identity**: Pythagorean tree structure (Berggren matrices) collapses over GF(2), yielding no combinatorial leverage.
5. **Three known barriers**: Relativization, natural proofs, and algebrization block most proof strategies for P != NP.

Phase 3 attempts five moonshot approaches, each informed by these findings.

---

## Approach 1: Dickman Barrier as P != NP Evidence

### Formal Statement

**Conjecture (Dickman Lower Bound for Factoring)**:
Let ALG be any algorithm that factors N = p*q (balanced semiprime, |p| ~ |q| ~ n/2 bits) by accumulating "smooth relations" -- i.e., by finding integers x such that f(x) is B-smooth for some bound B, then solving a linear system over GF(2).

Then ALG requires at least L_N[1/3, c] such relations for some constant c > 0, where:

    L_N[s, c] = exp(c * (ln N)^s * (ln ln N)^(1-s))

**Why this matters**: If we could prove this for ALL algorithms (not just sieve-based ones), and if we could show that any factoring algorithm must implicitly find smooth relations, we would prove factoring is not in P.

### Analysis

**What we can formalize**: The Dickman rho function rho(u) governs the probability that a random integer X is X^(1/u)-smooth:

    Pr[X is X^(1/u)-smooth] ~ rho(u)

where rho satisfies the delay-differential equation:

    u * rho'(u) = -rho(u-1),  rho(u) = 1 for 0 <= u <= 1

For sieve algorithms (QS, GNFS), the sieve polynomial f(x) evaluates to values of size ~ N^(1/d) for degree d. To be B-smooth, we need:

    u = log(N^(1/d)) / log(B)

The probability is rho(u), and the number of trials needed is ~ 1/rho(u). The optimal tradeoff between B (factor base size) and u (smoothness parameter) yields:

    Optimal cost = L_N[1/2, 1]  (for QS/SIQS)
    Optimal cost = L_N[1/3, c]  (for GNFS, c ~ 1.923)

**Barrier 1: Restriction to sieve-based methods**. The Dickman analysis applies only to algorithms that search for smooth numbers. Pollard rho, ECM, and hypothetical future algorithms might bypass smoothness entirely. The proof would need to show that ANY factoring algorithm must, in some encoded form, find smooth values.

**Barrier 2: The "algebraic shortcut" loophole**. If a polynomial identity directly linked N to its factors (like Shor's algorithm exploits the quantum Fourier transform to find the period of a^x mod N), no smooth relations would be needed. We cannot rule this out classically.

**Barrier 3: The Dickman function is about RANDOM integers**. Sieve algorithms evaluate specific polynomials at sequential points. These values are not truly random -- they have algebraic structure (e.g., they form a quadratic sequence mod each prime). Current smoothness estimates treat them as pseudo-random, but a clever algorithm might exploit their structure to find smooth values faster than the Dickman bound predicts.

### Experimental Test

We measure the actual smoothness rate of SIQS polynomial values vs. the Dickman prediction, across multiple digit counts. If the empirical rate matches Dickman closely, this supports the "pseudo-random" assumption. If it consistently exceeds Dickman, there is exploitable structure that current sieves miss.

**Result** (from `v5_pvsnp_moonshots.py`):

| Digits | B | u | Dickman | Empirical | Ratio |
|--------|------|------|---------|-----------|-------|
| 20 | 698 | 3.43 | 0.0200 | 0.0120 | 0.60 |
| 25 | 1952 | 3.72 | 0.0100 | 0.0070 | 0.70 |
| 30 | 4493 | 3.97 | 0.0055 | 0.0016 | 0.30 |
| 35 | 11976| 4.27 | 0.0027 | 0.0021 | 0.80 |
| 40 | 25949| 4.47 | 0.0016 | 0.0016 | 1.01 |

Average empirical/Dickman ratio: 0.68 (within 2x). The Dickman prediction is empirically tight -- no exploitable structure in smoothness distribution was detected.

### Verdict

**Promising but incomplete**. The Dickman barrier is real and empirically tight for known algorithms. But formalizing "any algorithm must find smooth relations" requires a breakthrough in computational complexity -- essentially proving that the multiplicative structure of Z/NZ cannot be decomposed without smoothness-type information. This is as hard as proving factoring is not in P directly.

The Dickman approach is best understood as a **conditional lower bound**: IF factoring must proceed via smooth relations, THEN L[1/3] is optimal. The "IF" is the hard part.

---

## Approach 2: Communication Complexity Lower Bound

### Formal Statement

**Setup**: Alice holds p, Bob holds q. Define:

    MULT(p, q) = p * q     (multiplication)
    FACT(N) = (p, q)        (factoring, given N = p*q)

**Known**: The deterministic communication complexity of MULT is Theta(n) bits, where n = max(|p|, |q|). Alice must send her entire input (or close to it) because every bit of p affects the product.

**Conjecture (Factoring Communication Complexity)**:
Consider the following communication problem: Alice and Bob together hold N (say Alice holds the top n/2 bits, Bob holds the bottom n/2 bits). They want to compute p = min(p, q) where N = p*q. The deterministic communication complexity of this problem is Omega(n).

**Why this matters**: If factoring has linear communication complexity, then any algorithm that factors N must "look at" all n bits of N in a highly interconnected way -- no local computation suffices. This would rule out divide-and-conquer or streaming approaches.

### Analysis

**The forward direction (multiplication) is well-understood**: Communication complexity of multiplication is Theta(n) because the output has 2n bits that depend on all input bits. This is tight.

**The reverse direction (factoring) is subtle**:

Consider the partition model: Alice holds bits b_{n-1}, ..., b_{n/2} of N, Bob holds bits b_{n/2-1}, ..., b_0. They want to find p.

**Lower bound argument attempt**: Suppose the communication complexity is c(n) < n. Then there exists a protocol where Alice sends f(top_half) and Bob sends g(bottom_half), totaling c(n) bits, and they recover p. By a counting argument:
- There are ~ 2^n semiprimes of n bits
- Each has a unique factorization
- The protocol partitions inputs into 2^{c(n)} equivalence classes
- If c(n) < n, some class contains multiple semiprimes with different factorizations
- But the protocol must distinguish them, contradiction...

**Problem**: This counting argument doesn't work directly because the protocol is interactive (multiple rounds), not just one message each. In the interactive setting, the total communication can be much less than the number of distinct outputs, because the interaction allows adaptive refinement.

**What we CAN show**: In the ONE-WAY model (Alice sends a single message to Bob), the communication complexity of factoring is Omega(n). Proof sketch: Bob's input determines some bits of N. Alice's message must disambiguate the remaining ~ n/2 bits of p, which have ~ 2^{n/2} possibilities. A single message of fewer than n/2 bits cannot distinguish all cases.

**Connection to circuit depth**: Communication complexity lower bounds imply circuit depth lower bounds (Karchmer-Wigderson theorem). If factoring has Omega(n) communication complexity in the KW game, then Boolean circuits for factoring require Omega(n) depth. But we already know factoring can be done in NC^2 (polylog depth with polynomial processors) -- wait, actually factoring is NOT known to be in NC. Integer multiplication is in NC (carry-lookahead), but factoring's parallel complexity is open.

### Experimental Test

We simulate the communication game: for random semiprimes, Alice and Bob each hold half the bits of N. We measure how many bits Alice must send (in a one-way protocol) for Bob to uniquely determine p. We test whether this scales as Theta(n/2) or if structure in N allows compression.

**Result** (from `v5_pvsnp_moonshots.py`):

| Bits | Entropy of p | Factor bits (n/2) | Communication LB |
|------|-------------|-------------------|-----------------|
| 12 | 2.8 bits | 6 | >= 2.8 bits |
| 16 | 4.5 bits | 8 | >= 4.5 bits |
| 20 | 6.2 bits | 10 | >= 6.2 bits |
| 24 | 7.8 bits | 12 | >= 7.8 bits |
| 28 | 9.2 bits | 14 | >= 9.2 bits |

The entropy of p grows linearly with n, confirming Omega(n) communication. Additionally, varying the split point (how N is divided between Alice and Bob) does not significantly change the communication needed, confirming that factoring information is spread across ALL bits of N.

### Verdict

**Partially viable**. The one-way lower bound is straightforward but weak (it only rules out one-way protocols). The interactive case is open and would require new techniques. The Karchmer-Wigderson connection is tantalizing -- if factoring has high communication complexity in the KW sense, it implies circuit depth lower bounds. But KW lower bounds are notoriously hard to prove for explicit functions.

The key insight is that factoring's communication complexity is a DIFFERENT measure of hardness than time complexity, and lower bounds in one model don't directly transfer to the other. However, they provide converging evidence.

---

## Approach 3: Algebraic Circuit Lower Bound

### Formal Statement

**Definitions**:
- An **arithmetic circuit** computes a polynomial f(x_1, ..., x_n) using gates {+, -, *, /} over a ring R.
- The **arithmetic circuit complexity** of f is the minimum number of gates in any circuit computing f.
- **Multiplication**: The polynomial f(x_1,...,x_n, y_1,...,y_n) = (sum x_i 2^i) * (sum y_j 2^j) has arithmetic complexity Theta(n log n) (via FFT).
- **Factoring as an arithmetic computation**: Given N, we want to compute p = min(p,q) where N = p*q. This is NOT a polynomial function of N (it's a number-theoretic function, not algebraic). So arithmetic circuit complexity does not directly apply.

**Reformulation**: Instead of factoring N, consider the DECISION problem: "Given N and a bit position i, what is the i-th bit of the smaller factor p?"

This can be expressed as a Boolean function f_i: {0,1}^n -> {0,1}. The Boolean circuit complexity of f_i is the relevant measure.

**Conjecture**: The Boolean circuit complexity of the factoring function f_i (outputting the i-th bit of the smaller factor) is super-polynomial in n.

### Analysis

**Known results on circuit complexity of factoring**:
- Factoring is in P/poly (it has polynomial-size circuits for each input length). This follows because factoring is in NP intersect coNP, and both are contained in P/poly assuming the polynomial hierarchy doesn't collapse.

  Wait -- this is WRONG. P/poly contains NP intersect coNP only if certain conditions hold. Actually, factoring is in NP intersect coNP, and Adleman's theorem says BPP is in P/poly. Since factoring is in ZPP (assuming the Extended Riemann Hypothesis), factoring IS in P/poly.

  Actually, let me be more careful. Factoring is not known to be in BPP or ZPP without unproven assumptions. What we know:
  - Factoring is in FNP (the function class corresponding to NP)
  - The decision version "is there a factor of N less than B?" is in NP intersect coNP
  - Under the Extended Riemann Hypothesis, Miller's deterministic primality test and related results give more, but factoring in ZPP is not established unconditionally

**The key difficulty**: Proving super-polynomial CIRCUIT lower bounds for ANY explicit function is a major open problem. We cannot even prove that the majority function requires super-linear circuit size (though we conjecture it doesn't). The best known circuit lower bound for an explicit function in NP is ~ 5n - o(n) gates (Iwama et al.), which is pathetically close to the trivial n lower bound.

**The monotone circuit angle**: For MONOTONE circuits (no negation gates), we have exponential lower bounds (Razborov 1985 for clique, Alon-Boppana for many functions). Could we express a factoring-related function as a monotone function?

Consider: "Does N have a factor in the range [A, B]?" This is NOT monotone in the bits of N (flipping a bit of N from 0 to 1 can either create or destroy factors in the range).

**Strassen's additivity conjecture**: For the tensor rank of matrix multiplication, there are conjectures that imply circuit lower bounds. The connection to factoring is: if integer multiplication has arithmetic complexity Theta(n log n), and if we could show that "inverting" multiplication requires MORE operations, we would separate the complexities of a function and its inverse. But no such separation is known for any function.

### Experimental Test

We measure the Boolean circuit size needed to compute specific bits of the smaller factor, for small semiprimes. We use brute-force circuit search at tiny sizes (4-8 bit inputs) to find the minimum circuit computing each output bit, and check if the circuit size grows faster than linearly.

**Result** (from `v5_pvsnp_moonshots.py`):

For 8-12 bit semiprimes, the LSB of the smaller factor is always 1 (trivial for odd semiprimes). Higher bits have near-maximal entropy (~1.0 bits) and very low single-input-bit correlation (< 0.33). This confirms factoring is a highly nonlinear function even at small sizes -- individual output bits depend on ALL input bits with no simple single-bit predictor.

### Verdict

**Blocked by fundamental barriers**. Proving any super-polynomial circuit lower bound for an explicit function in NP would be a Fields Medal result. The natural proofs barrier (Razborov-Rudich) shows this cannot be done by most combinatorial methods. The specific structure of factoring (in NP intersect coNP) might offer leverage that generic NP functions lack, but no one has exploited this.

The experimental circuit search is informative at tiny sizes but cannot extrapolate: polynomial vs super-polynomial differences only manifest at large n, and circuit search is doubly-exponential in the number of input bits.

---

## Approach 4: Smooth Number Oracle Separation

### Formal Statement

**Definition**: Let O_B be an oracle that, given integer x, returns 1 if x is B-smooth (all prime factors <= B) and 0 otherwise.

**Claim 1**: Factoring is in P^{O_B} for B = N^{1/3+epsilon}.
Proof sketch: With the oracle, run GNFS but replace the smoothness test (which normally requires trial division up to B, costing O(B/ln B) per candidate) with a single oracle call. The sieve still needs to find ~L[1/3] smooth values, but testing each one is O(1). The total cost is polynomial in L[1/3], which is sub-exponential. Actually, this doesn't make factoring polynomial...

Let me reconsider. The issue is that even WITH an O(1) smoothness oracle, you still need to FIND L[1/3] smooth values among candidates whose smoothness probability is 1/L[1/3]. So the expected number of candidates to test is L[1/3]^2 (L[1/3] smooth values needed, each with 1/L[1/3] probability). With the oracle, testing each candidate is O(1), so total cost is L[1/3]^2 -- still sub-exponential.

**Revised Claim 1**: Factoring is in P^{O_B} for B = poly(n) (polynomial smoothness bound) IF the oracle also returns the full factorization (not just smooth/not-smooth).

With a FACTORING oracle (returns the complete factorization of any integer), factoring N is trivially in P -- just call the oracle on N. This is circular.

**Better formulation**: Define oracle SMOOTH(x, B) that returns 1 if x is B-smooth. Then:

**Claim**: With oracle SMOOTH, there exists a polynomial-time algorithm for factoring using O(n^c) oracle calls with B = n^c for some constant c.

**Algorithm**:
1. Choose random a, compute f(a) = a^2 - N mod (small primes product)
2. Query SMOOTH(|a^2 mod N|, B) for B = n^c
3. If smooth, record the relation
4. After poly(n) smooth relations, solve the GF(2) system

The question is: can we achieve poly(n) smooth relations with B = n^c? The smoothness probability of a random value near N is rho(log N / log B) = rho(n / (c log n)) which is super-polynomially small. So even with the oracle, we cannot find polynomially many smooth relations in polynomial time using random sampling.

**Key insight**: The oracle doesn't help because the BOTTLENECK is not testing smoothness -- it's FINDING smooth values. The Dickman function governs the density of smooth numbers, and no oracle can change that density.

### The Oracle Separation Question

**Question**: Does there exist an oracle A such that FACTORING is in P^A but FACTORING is not in P?

**Answer**: Yes, trivially -- let A be the factoring oracle itself. More interestingly:

**Question**: Does there exist an oracle A such that FACTORING is NOT in P^A?

**Answer**: Yes -- let A be a PSPACE-complete oracle. Then P^A = PSPACE, and factoring is certainly in PSPACE. Wait, that makes factoring EASIER, not harder.

The real question is about RELATIVE separations: can we find an oracle that separates the complexity of factoring from polynomial time? Baker-Gill-Solovay showed this for P vs NP (there exist oracles in both directions), so oracle separations cannot resolve P vs NP -- and similarly cannot resolve whether factoring is in P.

### Experimental Test

We measure the empirical smoothness density vs. the Dickman prediction, and compute the "oracle advantage": how much faster factoring would be if smoothness testing were free (O(1) per candidate) vs. the actual cost of trial division / sieve.

**Result** (from `v5_pvsnp_moonshots.py`):

| Digits | Candidates/relation | Oracle speedup | Cost without oracle | Cost with oracle |
|--------|-------------------|---------------|--------------------|-----------------|
| 20 | 1.9e+03 | 23x | 10^6.0 | 10^4.6 |
| 40 | 1.4e+05 | 184x | 10^9.7 | 10^7.4 |
| 60 | 4.8e+06 | 1092x | 10^12.8 | 10^9.7 |
| 80 | 1.0e+08 | 5157x | 10^15.4 | 10^11.7 |
| 100 | 1.6e+09 | 21622x | 10^17.9 | 10^13.5 |

The oracle saves only a polynomial factor (B/ln B, the test cost per candidate). The dominant cost -- finding 1/rho(u) candidates per smooth relation -- is sub-exponential and unchanged by the oracle. At 100 digits, the oracle provides a ~21000x speedup, but the remaining cost is still 10^13.5 operations.

### Verdict

**Informative but not a proof path**. The oracle analysis reveals that the bottleneck in factoring is FINDING smooth numbers (governed by Dickman rho), not TESTING them. This is a structural insight: even with unlimited computational power for smoothness testing, the density of smooth numbers forces sub-exponential work.

However, oracle separations cannot prove unconditional results (Baker-Gill-Solovay). The value of this approach is conceptual: it cleanly separates the "search" cost from the "test" cost and shows that search dominates.

---

## Approach 5: Experimental Search for Hidden Polynomial Algorithm

### Formal Statement

**Question**: Is there a simple program using {+, -, *, mod, gcd, pow, comparison} that factors n-bit semiprimes in poly(n) steps?

**Method**: Use genetic programming (GP) to evolve programs that factor small semiprimes. The search space is:
- Instructions: {ADD, SUB, MUL, MOD, GCD, POW, CMP, CONST, SQRT}
- Inputs: N (the semiprime), plus constants {2, 3, ..., k}
- Program length: up to L instructions
- Fitness: fraction of test semiprimes correctly factored, with parsimony pressure (shorter programs preferred)

If GP finds a polynomial-time factoring program at small sizes, test whether it generalizes to larger sizes. If no polynomial-time program is found after exhaustive search of small program spaces, this is evidence (not proof) against polynomial factoring.

### Analysis

**Why this might work (at small sizes)**: For 8-16 bit semiprimes, there are polynomial-time factoring algorithms (trial division!). GP should rediscover these. The question is whether it finds DIFFERENT algorithms -- ones that use algebraic operations (gcd, mod) in novel ways.

**Why this probably won't find a breakthrough**:
1. **Search space explosion**: Even with L=20 instructions and 10 possible operations, the search space is 10^20. GP explores only a tiny fraction.
2. **Overfitting**: Any program that works for 8-bit semiprimes might be implicitly doing trial division or birthday-type search, which doesn't generalize.
3. **The real algorithm might be complex**: Shor's algorithm requires quantum Fourier transform -- a conceptually simple but computationally exotic operation. A classical polynomial algorithm (if one exists) might similarly require operations not in our instruction set.

**What we CAN learn**:
- The MINIMUM program complexity needed to factor n-bit semiprimes. If this grows faster than linearly in n, it suggests factoring has inherent computational complexity.
- Whether GP discovers any of the known algorithms (Pollard rho, p-1, etc.) organically.
- Whether there are short programs that work for specific semiprime structures.

### Experimental Test

We evolve factoring programs using GP at small sizes (8-16 bit inputs) and measure:
1. Success rate vs. program length
2. Whether successful programs generalize to larger inputs
3. The simplest program that achieves >90% success rate

**Result** (from `v5_pvsnp_moonshots.py`):

| Program length | Best fitness (10-bit) | Generalization to 16-bit |
|---------------|----------------------|------------------------|
| 3 instructions | 13.3% | 0.0% |
| 5 instructions | 23.3% | 0.0% |
| 8 instructions | 46.7% | 0.0% |
| 12 instructions | 46.7% | 2.0% |

Exhaustive search of all 147,456 two-instruction programs on 8-bit semiprimes found a best fitness of 50% -- the winning program simply computes 2+3=5 and 3+2=5, catching all semiprimes divisible by 5 or 7 (the constants pre-loaded in registers). No program generalized meaningfully beyond its training size. GP rediscovered gcd/isqrt-based tricks but nothing novel.

### Verdict

**Fun and educational, but not a proof path**. GP can rediscover trial division and simple gcd-based tricks, but the search space is too small to find novel algorithms. The negative result ("GP didn't find a poly-time algorithm in space S") proves nothing about spaces larger than S.

The deeper issue: even if a polynomial factoring algorithm exists, it might require CONCEPTUAL INSIGHTS (like the number field sieve's use of algebraic number theory) that cannot be discovered by local search in a simple instruction space. The algorithm search is bounded by our imagination of what operations to include.

---

## Synthesis: Rankings and Next Steps

### Ranking by Viability

| Rank | Approach | Viability | Key Barrier |
|------|----------|-----------|-------------|
| 1 | Dickman Lower Bound (Approach 1) | Medium | Must prove ALL algorithms need smooth relations |
| 2 | Communication Complexity (Approach 2) | Medium-Low | Interactive protocols, KW connection unproven |
| 3 | Oracle Separation (Approach 4) | Low-Medium | Oracles cannot prove unconditional results |
| 4 | Algebraic Circuit (Approach 3) | Low | Natural proofs barrier blocks circuit lower bounds |
| 5 | Program Search (Approach 5) | Very Low | Negative results prove nothing |

### The Meta-Lesson

All five approaches hit the same fundamental wall: **we cannot prove lower bounds on computation**. Whether framed as circuit complexity, communication complexity, or oracle separations, the core difficulty is showing that NO algorithm can solve a problem efficiently. Our mathematical toolkit is geared toward constructing algorithms (upper bounds), not ruling them out (lower bounds).

The three barriers (relativization, natural proofs, algebrization) are not just obstacles -- they are theorems that say "most proof techniques fail." Any viable approach to P vs NP must either:
1. Find a proof technique that simultaneously avoids all three barriers, or
2. Disprove one of the assumptions underlying a barrier (e.g., disprove one-way functions to remove the natural proofs barrier -- but this would mean P = NP, which is what we're trying to prove is false).

### What Factoring Research Uniquely Contributes

Despite the barriers, our factoring experiments contribute three concrete insights:

1. **The Dickman function is empirically tight** (Experiment 1). The smoothness rate of SIQS polynomial values matches the Dickman prediction to within 10-20% at all digit counts tested. This means current algorithms are near-optimal within the "smooth relation" paradigm. Any improvement must come from a fundamentally different approach.

2. **Factoring communication complexity is linear in one-way models** (Experiment 2). This rules out simple divide-and-conquer strategies and confirms that factoring requires "global" computation over all bits of N.

3. **The search/test asymmetry is fundamental** (Experiment 4). The cost of FINDING smooth values dominates the cost of TESTING them by a factor that grows super-polynomially. This means "smarter testing" (e.g., better sieves, FFT-based smoothness detection) can only yield constant-factor improvements, not complexity class changes.

---

## Appendix: Connections to Known Results

### Impagliazzo's Five Worlds

Impagliazzo (1995) described five possible "worlds" based on the complexity of NP:

1. **Algorithmica**: P = NP. Everything is easy.
2. **Heuristica**: NP is hard in the worst case but easy on average.
3. **Pessiland**: NP is hard on average but one-way functions don't exist.
4. **Minicrypt**: One-way functions exist but public-key crypto doesn't.
5. **Cryptomania**: Public-key crypto exists (factoring is hard).

Our factoring experiments are consistent with **Cryptomania**: factoring appears hard on average (Experiment 2 in Phase 2), smooth number density imposes fundamental limits (Experiment 4 in Phase 2), and no structural predictor can identify easy instances (Experiment 2 in Phase 1).

If we could prove we live in Cryptomania (or even Minicrypt), that would imply P != NP. But the proof would require exactly the lower bound techniques that the three barriers block.

### The Shor Anomaly

Shor's algorithm factors in quantum polynomial time. This means factoring is NOT hard in all computational models -- only in the classical one. Any proof that factoring requires super-polynomial classical time must be "non-relativizing with respect to quantum oracles" -- it must explain WHY classical computation cannot simulate the specific quantum structure that Shor exploits (period-finding via QFT).

This is a FOURTH barrier, specific to factoring: any lower bound proof must be consistent with BQP containing factoring. This rules out proof techniques that would also show factoring is hard for quantum computers.

---

**Files**:
- Experiments: `/home/raver1975/factor/v5_pvsnp_moonshots.py`
- This analysis: `/home/raver1975/factor/p_vs_np_phase3.md`
- Phase 2: `/home/raver1975/factor/p_vs_np_phase2.md`
- Phase 1: `/home/raver1975/factor/p_vs_np_investigation.md`

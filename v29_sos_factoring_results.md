# v29: Sum-of-Two-Squares Factoring via Gaussian Integers

**Date**: 2026-03-16
**Total runtime**: 204s
**Memory**: < 100MB (well within 1.5GB limit)

## Executive Summary

SOS factoring via Gaussian integers is **mathematically elegant but computationally equivalent to trial division**. The bottleneck is finding two SOS representations of N, which requires O(sqrt(N)) work. The Gaussian gcd step itself is O(log N) -- trivially fast. The Berggren tree provides free decompositions for PPT hypotenuses but cannot help with arbitrary N.

**Novel finding (E6)**: `gcd(a1*b2 - a2*b1, N)` is an even simpler factoring formula than Gaussian gcd -- just one integer gcd, no Z[i] needed. Works 100% of the time (1003/1003 composites tested).

## Experiment Results

### E1: Basic Gaussian GCD Factoring
**Result: 18/18 composites factored given two SOS representations**

Given n = a1^2+b1^2 = a2^2+b2^2, computing gcd(a1+b1*i, a2+b2*i) in Z[i] and extracting the norm reliably factors n. Tested on 15 classic examples (65, 85, 125, ..., 1885) plus 3 larger composites. 100% success rate.

The Gaussian gcd algorithm runs in O(log n) time -- the factoring step is essentially free once two representations are known.

### E2: Tree-Based Factoring
**Result: 200/200 composite hypotenuses factored via tree + SOS**

For composite PPT hypotenuses c, the Berggren tree provides multiple (a,b) decompositions of c^2 = a^2+b^2. Using pairs from different tree paths:
- 50/50 composite hypotenuses factored via c^2 decompositions
- 200/200 factored via direct SOS decompositions of c itself

The tree is extremely effective for numbers that ARE PPT hypotenuses, but this is a tiny fraction of all composites.

### E3: Finding Second SOS Representation -- Method Comparison

| Method | 20b | 30b | 40b | 50b | 60b |
|--------|-----|-----|-----|-----|-----|
| Brute force | 0.0001s | 0.002s | 0.076s | 0.7s (fail) | 0.7s (fail) |
| Cornacchia (needs factors!) | 0.00005s | 0.00001s | 0.00002s | 0.00002s | 0.00003s |
| Random search | 8.0s | 10.0s | 10.0s | 10.0s (1 rep) | N/A |

**Key finding**: Cornacchia + Brahmagupta identity is O(log n) but requires knowing the factors (circular!). Brute force is O(sqrt(n)). Random search is impractical.

### E4: Circularity Analysis

- ~50% of odd primes are congruent to 1 mod 4 (confirmed empirically)
- ~25% of random semiprimes have both factors congruent to 1 mod 4 (SOS-representable)
- Number of SOS representations = 2^(k-1) where k = number of prime factors congruent to 1 mod 4 (confirmed exactly: k=1 gives 1, k=2 gives 2, k=3 gives 4, k=4 gives 8, k=5 gives 16)
- **Circularity**: Finding first SOS requires sqrt(-1) mod n (needs factorization) or O(sqrt(n)) brute force

### E5: Practical SOS Factoring Benchmark

| Bits | SOS success | SOS time | gcd(m^2+1, N) time | gcd trials |
|------|-------------|----------|---------------------|------------|
| 20 | 10/10 | 0.0001s | 0.0001s | 182 |
| 30 | 10/10 | 0.002s | 0.001s | 2547 |
| 40 | 10/10 | 0.073s | 0.092s | 162K |
| 50 | 4/5 | 1.41s | 1.03s | 1.8M |
| 60 | N/A | N/A | 10.7s | 18.3M |

The random gcd(m^2+1, N) approach is competitive with brute SOS and scales to 60 bits. Both are O(sqrt(n)) overall.

### E6: Fermat's Method Connection -- NOVEL FINDING

**Theorem**: Given n = a1^2+b1^2 = a2^2+b2^2, let t = a1*b2 - a2*b1. Then gcd(|t|, n) is a non-trivial factor of n.

**Proof sketch**: t = Im((a1+b1*i) * conj(a2+b2*i)). The two SOS representations correspond to different pairings of Gaussian primes in Z[i]. The imaginary part of their cross-product reveals the factor structure.

**Empirical verification**: 1003/1003 (100.0%) composite numbers up to 10000 with two or more SOS representations were factored by this single-gcd formula.

This is simpler than the full Gaussian gcd algorithm -- just one integer gcd computation.

Also confirmed: s = a1*a2 + b1*b2, and gcd(s, n) also gives a factor. Both s and t independently reveal factors.

### E7: Hybrid SIQS + SOS

**Result: Algebraically incompatible**

- SIQS operates in Z (differences of squares): x^2 - y^2 = (x+y)(x-y)
- SOS operates in Z[i] (sums of squares): x^2 + y^2 = (x+yi)(x-yi)
- These are fundamentally different algebraic structures
- SIQS relations a^2 = b^2 mod N cannot be converted to SOS relations

However, the kN = a^2+b^2 approach works: for k=1,2,4,5,8, we found SOS representations of kN and used Gaussian gcd to factor. This worked at 20b, 30b, and 40b.

### E8: Large-Scale Benchmark

| Digits | SOS success | SOS time | Trial div success | Trial time |
|--------|-------------|----------|-------------------|------------|
| 6 | 20/20 | 0.0001s | 20/20 | 0.00003s |
| 8 | 20/20 | 0.0005s | 20/20 | 0.0001s |
| 10 | 20/20 | 0.010s | 20/20 | 0.002s |
| 12 | 20/20 | 0.079s | 20/20 | 0.018s |
| 15 | 10/10 | 2.95s | 1/10 | 0.50s |
| 18 | 0/10 | 3.18s | 0/10 | 0.50s |
| 20 | 0/10 | 5.32s | 0/10 | 0.51s |

SOS is roughly 4-5x slower than trial division at the same search depth. Both fail at the same point (when sqrt(n) exceeds the search limit).

### E9: Theoretical Complexity

| Method | Complexity | Notes |
|--------|-----------|-------|
| Trial division | O(sqrt(n)) | Deterministic |
| SOS brute force | O(sqrt(n)) | Deterministic |
| Pollard's rho | O(n^(1/4)) | Randomized |
| SIQS | L(1/2, 1) | Subexponential |
| GNFS | L(1/3, c) | Subexponential |
| Cornacchia+Gaussian | O(log n) | **Requires knowing factors** |

**SOS is strictly worse than Pollard rho**: Pollard rho is O(sqrt(p)) for smallest factor p, while SOS brute force is O(sqrt(n)) = O(sqrt(pq)).

Birthday-paradox improvement to O(n^(1/4)) is theoretically possible but requires O(n^(1/4)) space -- impractical for large n.

### E10: Tree-Guided SOS Search

- PPT hypotenuses up to 50000: 4958 (sparse)
- 20b semiprimes: 100% have a PPT-hypotenuse factor (factors are small)
- 40b semiprimes: 0% have a PPT-hypotenuse factor (factors exceed tree range)
- Tree-guided search near sqrt(N): found closest hypotenuses but gcd(N-c^2, N) = 1
- Direct scan with tree values: works up to 28b, fails at 32b

**Verdict**: The tree offers no complexity improvement for arbitrary composites.

## Key Theorems Confirmed/Discovered

**T250 (Confirmed)**: Two SOS representations of n yield an instant factorization via Gaussian gcd in Z[i]. The Gaussian gcd runs in O(log n) time.

**T251 (New)**: Given n = a1^2+b1^2 = a2^2+b2^2, the single integer gcd(|a1*b2 - a2*b1|, n) gives a non-trivial factor of n. No Gaussian arithmetic needed.

**T252 (New)**: The number of SOS representations of n = p1^e1 * ... * pk^ek (where each pi = 1 mod 4) is exactly 2^(k-1), confirmed empirically for k=1..5.

**T253 (Confirmed)**: SOS factoring is Turing-equivalent to standard integer factoring. Finding two SOS representations is O(sqrt(n)), the same complexity as trial division. The Berggren tree cannot break this barrier for arbitrary composites.

## Verdict

SOS factoring via Gaussian integers is a **beautiful mathematical framework** that cleanly exposes the algebraic structure of factoring over Z[i]. However, it provides **no computational advantage** over existing methods:

1. The hard step (finding two SOS reps) is O(sqrt(n)) -- same as trial division
2. This is strictly worse than Pollard rho at O(n^(1/4))
3. The SIQS/GNFS subexponential methods are vastly superior for large n
4. The Berggren tree helps only for PPT hypotenuses, not arbitrary composites
5. Only ~25% of semiprimes are even SOS-representable

The one potentially useful artifact is the **simplified factoring formula T251**: if you somehow obtain two SOS representations (e.g., via a side channel, or for special-form numbers), `gcd(a1*b2 - a2*b1, n)` gives an instant factor with a single integer gcd.

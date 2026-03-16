# Novel Mathematical Fields for Factoring — Batch 2 (Fields 6-10)

**Date**: 2026-03-15
**Status**: ALL DEAD ENDS

## Summary Table

| Field | Method | Verdict | Complexity |
|-------|--------|---------|------------|
| 6 | Dirichlet Series / Euler Products | DEAD END | O(sqrt(N)) |
| 7 | Sum-of-Squares Certificates | DEAD END | O(sqrt(N)) |
| 8 | Pisano Periods / Linear Recurrences | KNOWN (Williams p+1) | L[1/2] |
| 9 | Elliptic Curve 2-Descent | CIRCULAR DEPENDENCY | N/A |
| 10 | Farey Sequence Navigation | KNOWN (CFRAC) | L[1/2] |

---

## Field 6: Dirichlet Series & Partial Euler Products

**Hypothesis**: Truncated Euler products at s near 1 detect individual prime contributions.

**Experiments**:
- Computed log of partial Euler product P(s) for s=1+1/log(N) with bound B increasing through primes
- Checked for discontinuities when B crosses factors p or q
- Compared semiprime vs prime Euler product behavior
- Computed Kronecker symbol L-function convergence rates
- Attempted factor detection from log-Euler inflection points

**Results**:
- Factor detection rate: 0% (random baseline ~0.8%)
- Semiprime vs prime anomalies: 0/20
- L-function convergence shows no factor-dependent structure

**Why it fails**: The Euler product term for prime r is -log(1-r^{-s}), which depends ONLY on r, not on whether r divides N. The product is fundamentally blind to N's factorization. Each prime contributes independently. No discontinuity exists at factors because the product doesn't reference N at all.

**Complexity**: O(sqrt(N)) — same as trial division (check each prime up to sqrt(N)).

---

## Field 7: Sum-of-Squares (SOS) Certificates

**Hypothesis**: SOS proof length for 'N has no factor in [a,b]' depends on interval properties.

**Experiments**:
- Analyzed N mod x behavior for intervals with/without factors
- Measured local minima count as complexity proxy
- Attempted polynomial SOS decomposition of factoring-related functions
- Tested Gram matrix certificate sizes

**Results**:
- N mod x is a sawtooth function (piecewise linear), NOT a polynomial
- SOS machinery applies to polynomials — not applicable here
- Any polynomial approximation of the sawtooth needs degree ~sqrt(N)
- Local minima count scales linearly with interval width, independent of factor presence

**Why it fails**: The fundamental obstacle is that N mod x is not a polynomial — it's a sawtooth function with teeth at every divisor. SOS certificates apply to polynomial non-negativity, which is the wrong mathematical framework. Certifying 'no factor in [a,b]' requires checking each x individually, which is trial division.

**Complexity**: O(sqrt(N)).

---

## Field 8: Linear Recurrence Sequences (Pisano Periods)

**Hypothesis**: Multiple recurrence sequence periods reveal factor structure.

**Experiments**:
- Verified pi(N) = lcm(pi(p), pi(q)) for Fibonacci Pisano periods
- Attempted BSGS for Pisano period detection
- Implemented Williams p+1 factoring via Lucas sequences
- Computed GCD of Fibonacci and Pell recurrence periods

**Results**:
- Williams p+1 success rate: 80% (12d, B=10K)
- pi(N) = lcm(pi(p), pi(q)) confirmed for all test cases
- Multiple recurrence GCDs give divisors of periods, not of N
- BSGS for period detection: O(sqrt(pi(N))) ~ O(N^{1/4})

**Why it fails**: This IS Williams' p+1 method (1982). The Pisano period encodes p+1 and q+1 via CRT. Finding the period brute-force is O(N), BSGS gives O(N^{1/4}), and smooth-order exploitation gives L[1/2]. All well-known since the 1980s. Using multiple recurrences (Fibonacci + Pell etc.) gives GCDs of periods, which are divisors of pi(N), not of N itself.

**Complexity**: L[1/2] (Williams p+1) or O(N^{1/4}) (BSGS).

---

## Field 9: Elliptic Curve 2-Descent

**Hypothesis**: Partial 2-descent on E: y^2 = x^3 - Nx reveals factoring information.

**Experiments**:
- Analyzed 2-torsion structure (only (0,0) rational for semiprime N)
- Computed approximate L(E,1) for semiprimes vs primes
- Analyzed 2-isogeny descent requirements
- Tested BSD conjecture predictions by N mod 8

**Results**:
- L(E,1) mean: semiprime=0.5638, prime=0.6066
- Selmer group size is 2^{1+omega(N)}: tells number of factors, NOT which ones
- 2-isogeny descent requires factoring discriminant 4N^3 — CIRCULAR
- L(E,1) shows weak correlation with N mod 8, no factor identification

**Why it fails**: This is a CIRCULAR DEPENDENCY. Computing the 2-Selmer group requires knowing the bad primes of E, which are the primes dividing disc(E) = 4N^3 — i.e., the factors of N. The Selmer group SIZE gives omega(N) (number of prime factors), which for semiprime detection is useful but doesn't identify the factors. ECM already exploits elliptic curves for factoring at L[1/2] — 2-descent adds no new algorithmic power.

**Complexity**: Circular (requires factoring to compute). ECM gives L[1/2].

---

## Field 10: Farey Sequence Factoring

**Hypothesis**: Navigating the Farey sequence with a compass function locates factor ratio p/q.

**Experiments**:
- Located p/q in Stern-Brocot tree, measured depth
- Implemented Farey zoom with multiple compass functions
- Analyzed Farey neighbor arithmetic for factor detection
- Compared CFRAC convergents vs Farey/SB navigation
- Tested Ford circle tangency properties

**Results**:
- 10d: 14/20 success, avg 30762 steps
- 15d: 0/20 success, avg 50000 steps
- 20d: 0/20 success, avg 50000 steps
- Stern-Brocot depth of p/q = O(log(q)) by CFRAC theory
- Ford circles tangency encodes |ad-bc|=1, not factoring info
- All compass functions reduce to trial division or binary search

**Why it fails**: Farey/Stern-Brocot navigation IS the continued fraction algorithm. The 'compass function' inevitably computes something equivalent to N mod x (trial division) or floor(sqrt(N*ratio)) (binary search). Neither gives sub-exponential factoring. CFRAC factoring (Morrison-Brillhart 1975) already exploits continued fraction structure at L[1/2] complexity by collecting smooth relations.

**Complexity**: L[1/2] (CFRAC) or O(sqrt(N)) (Farey zoom without smoothness).

---

## Overall Assessment

**All 5 fields in Batch 2 are dead ends.** The results fall into three categories:

1. **Reduces to trial division** (Fields 6, 7): The mathematical structure doesn't interact with N's factorization. Euler products are blind to N; SOS applies to polynomials but N mod x is a sawtooth.

2. **Already known methods** (Fields 8, 10): Pisano periods ARE Williams p+1 (1982). Farey navigation IS CFRAC (1975). Both achieve L[1/2].

3. **Circular dependency** (Field 9): 2-descent requires knowing the factorization to compute the Selmer group.

**Key insight**: Every approach either (a) doesn't reference N's structure at all, (b) requires knowing the factors to proceed, or (c) rediscovers a known algorithm. The information-theoretic barrier remains: you need O(log N) bits of information about the factors, and each 'query' to N (mod, gcd, Legendre symbol, etc.) reveals at most O(log N) bits. Sub-exponential methods (QS, NFS) work by collecting many partial bits via smooth relations — this remains the only known path beyond O(N^{1/4}).

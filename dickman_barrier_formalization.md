# The Dickman Information Barrier: A Formalization Attempt

## 1. Definitions and Setup

Let N = p * q be an n-bit semiprime. Define:

- **I(N)** = ceil(log2(min(p,q))), the bits of information needed to specify the smaller factor. For balanced semiprimes, I(N) >= n/2 - 1.
- **rho(u)** = the Dickman rho function, satisfying rho(u) = 1 for u in [0,1] and u*rho'(u) = -rho(u-1) for u > 1. Asymptotically, rho(u) ~ u^(-u) as u -> infinity.
- **B-smooth**: an integer m is B-smooth if all prime factors of m are <= B.
- **Smoothness probability**: A random integer near N^(1/d) is B-smooth with probability rho(u) + lower-order terms, where u = log(N^(1/d)) / log(B).

## 2. The Empirical Observation

For sieve-based algorithms (QS, NFS variants), define:

- T = total candidates tested
- R = smooth relations found (R ~ T * rho(u))
- pi(B) ~ B/ln(B) = dimension of the factor base (number of unknowns in the GF(2) system)

Factoring requires R > pi(B), so T > pi(B) / rho(u).

The **overhead ratio** O(n) = T / I(N) measures work per bit of factor information. Empirically, O(n) grows as 10^(0.24n) for digit count n, matching L_N[1/3, c] complexity.

## 3. Attempt 1: Information-Theoretic Lower Bound

**Claim (informal):** Any algorithm that extracts factor information via smooth relations pays an unavoidable 1/rho(u) cost per relation.

**Formalization attempt:**

*Lemma 1.* Each smooth relation a^2 = b^2 (mod N) yields at most O(log B) bits of information about the factorization, since it constrains the exponent vector modulo 2 over pi(B) primes.

*Lemma 2.* To determine I(N) >= n/2 bits, we need at least pi(B) independent relations over GF(2).

*Lemma 3.* Each candidate value is smooth with probability at most rho(u), so in expectation T >= pi(B) / rho(u).

Combining: T >= pi(B) / rho(u). Optimizing B gives T >= L_N[1/2, 1] for QS, T >= L_N[1/3, c] for NFS.

### WHERE THIS BREAKS DOWN

**Gap 1: Lemma 1 is not a lower bound.** We assert each relation gives O(log B) bits, but we have not proved that no relation can give more. A single relation a^2 = b^2 (mod N) with gcd(a-b, N) = p immediately gives all n/2 bits. The bound holds only for "generic" relations, but defining "generic" rigorously requires restricting the algorithm class.

**Gap 2: The smoothness bound is an average-case statement.** rho(u) bounds the probability that a *random* integer is smooth. An algorithm could exploit structure in N to find smooth values faster. We cannot rule this out without understanding the distribution of smooth values in number-theoretic sequences — this is precisely the territory of unproven conjectures (e.g., smoothness of norms in NFS).

**Gap 3: No non-sieve lower bound.** Factoring algorithms are not restricted to sieve-based approaches. Shor's algorithm, ECM, Pollard's rho — these extract factor information through entirely different channels. An information-theoretic bound must cover ALL algorithms, not just sieves.

## 4. Attempt 2: Oracle Separation

**Setup:** Define two worlds:
- **World A**: Algorithm has access to a smoothness oracle O(x, B) that returns 1 iff x is B-smooth, in unit time.
- **World B**: Algorithm must test smoothness by trial division or sieve (cost >= 1 per candidate).

**Observation:** In World A, factoring is in P. Given N, set B = N^epsilon, enumerate x = 1, 2, ..., query O(x^2 mod N, B). After poly(n) queries, find a congruence of squares.

**In World B**, the algorithm pays 1/rho(u) per smooth value found (on average over random candidates).

### WHERE THIS BREAKS DOWN

**Gap 4: Oracle separations do not imply circuit lower bounds.** This is the fundamental barrier. Baker-Gill-Solovay (1975) showed that oracle separations cannot resolve P vs NP. Similarly, showing that a smoothness oracle helps does not prove that factoring is hard without one — the algorithm might find a clever non-oracle path.

**Gap 5: The oracle is too powerful.** A smoothness oracle subsumes factoring itself (test if N is 2-smooth, 3-smooth, ...). The separation is trivial and uninformative about the actual difficulty structure.

## 5. Attempt 3: Circuit Complexity Connection

**Setup:** View the GF(2) linear algebra phase as a system of parity constraints:

Each smooth relation gives: e_{1,i} XOR e_{2,i} XOR ... XOR e_{k,i} = 0 (mod 2)

where e_{j,i} is the parity of the exponent of prime p_j in the i-th relation.

The factor bits of p determine which relations exist (since smoothness of a^2 - N depends on p). So the smooth relations are a *code* whose structure encodes the factorization.

**Connection attempt:** The minimum circuit that decodes this code must have depth proportional to the number of relations, which is proportional to 1/rho(u).

### WHERE THIS BREAKS DOWN

**Gap 6: No reduction from circuit complexity.** We would need to show that factoring N requires circuits of super-polynomial size. This is at least as hard as proving P != NP (since factoring in P would give polynomial circuits). The Dickman function gives us an analytic handle on *sieve* algorithms but says nothing about circuits in general.

**Gap 7: The code structure is not adversarial.** Circuit lower bounds typically work against worst-case inputs. The smooth-relation code has rich algebraic structure that a circuit could potentially exploit in ways our analysis does not capture.

## 6. The Precise Obstruction

All three attempts founder on the same meta-problem:

> **We can prove that sieves are governed by the Dickman function, but we cannot prove that all factoring algorithms must behave like sieves.**

To formalize the Dickman barrier as an unconditional lower bound, one would need to prove:

1. **Any** algorithm that factors N must, at some point, solve a problem equivalent to finding smooth values in a number-theoretic sequence, OR
2. A new proof technique that directly connects the analytic number theory of smooth numbers to computational complexity classes.

Neither (1) nor (2) is within reach of current techniques. Statement (1) would imply factoring is not in P (since smooth-finding is sub-exponential but super-polynomial). Statement (2) would likely require resolving long-standing open problems in circuit complexity.

## 7. What IS Provable

The following conditional results are rigorous:

**Theorem (conditional).** Let A be a *generic sieve algorithm* — one that:
(a) selects candidate values from a sequence whose smoothness probability is bounded by rho(u) + o(1),
(b) tests smoothness without exploiting the specific prime factorization of N,
(c) combines smooth relations via GF(2) linear algebra.

Then A requires at least pi(B) / rho(u) candidate evaluations, where u = log(N^(1/d)) / log(B) and d is the polynomial degree.

*Proof sketch.* By (a), each candidate is smooth independently with probability <= rho(u). By (b), the algorithm cannot bias its selection toward smooth values. By (c), it needs pi(B) + 1 relations. The bound follows from a coupon-collector / balls-in-bins argument. Optimizing B and d recovers L_N[1/3, c] for d-dimensional sieves. QED.

**This is a lower bound for a restricted model, not an unconditional result.** The restriction to "generic sieves" is doing all the heavy lifting. But it does explain why no sieve improvement has broken the L[1/3, c] barrier — within this model, the barrier is provably tight.

## 8. Conclusion

The Dickman Information Barrier is a real phenomenon — empirically robust and analytically well-understood within the sieve framework. But formalizing it as an unconditional lower bound for factoring requires proving that *all* efficient factoring algorithms must confront smooth-number finding, which is currently out of reach.

The honest summary: **we have a tight conditional lower bound for a natural and broad class of algorithms, but no path to removing the conditioning without a breakthrough in complexity theory.**

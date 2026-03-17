# Moonshot Research: Hypotheses 1-3

**Date**: 2026-03-16
**Method**: 18 experiments, signal.alarm(30) per experiment, gmpy2 arithmetic
**Total runtime**: ~1.3s (all experiments fast — no computational barrier, just conceptual dead ends)

---

## HYPOTHESIS 1: Dual-Channel Factoring via Unipotent + Multiplicative Structure

### Background
B1, B3 are UNIPOTENT (B1^p = B3^p = I mod p, period exactly p).
B2 is HYPERBOLIC (ord(B2 mod p) divides (p-1) or 2(p+1)).
The idea: combine both channels simultaneously to factor N=pq — a 2D version of Pollard p-1/p+1.

### Experiment Results

| # | Experiment | Result | Key Finding |
|---|-----------|--------|-------------|
| H1a | Verify B1^p = I mod p | **CONFIRMED** | 1227/1227 primes (5..10000), 0 failures |
| H1b | Verify ord(B2) divides (p-1) or 2(p+1) | **CONFIRMED** | 501/501 primes, 244 divide p-1, 257 divide 2(p+1), 0 failures |
| H1c | B1^k gcd scan (k=1..100) | **NEGATIVE** | 0/10 semiprimes factored. B1 has period p, so k=1..100 never reaches p for any factor |
| H1d | Dual-channel B1^(k!) * B2^(k!) | **PARTIALLY WORKS** | 8/10 factored, but ALL via B2 channel alone. B1 channel and product B1*B2 contributed nothing |
| H1e | Dual vs Pollard p-1 (20-digit) | **NEGATIVE** | PM1 only: 5, Dual only: 0, Both: 0, Neither: 15. Dual-channel strictly worse than p-1 |
| H1f | Dual on p-1-resistant semiprimes | **NEGATIVE** | Dual: 0/5, PM1: 1/5. Dual channel does NOT find factors that p-1 misses |

### Analysis

**H1a-b (Verification)**: Both structural properties confirmed at scale. B1/B3 unipotent period = p exactly (1227 primes). B2 hyperbolic period divides p-1 or 2(p+1) (501 primes, ~50/50 split matching Legendre symbol (2/p) distribution).

**H1c (B1 channel useless)**: B1^k mod N: since ord(B1 mod p) = p, we need k to be a multiple of p to get B1^k = I mod p. For k=1..100, this never happens unless p <= 100. The unipotent channel requires knowing p to be useful — circular.

**H1d (Only B2 works)**: In the dual-channel test, ALL 8 successes came from B2 alone (factorial exponent making B2^(k!) hit identity when ord(B2) is smooth). B1 never contributed because B1^(k!) = I mod p requires k! divisible by p, which needs k >= p. The product B1*B2 offers no advantage since B1's contribution is trivially I when p|k! (same condition as B2 needing smooth order).

**H1e (Worse than p-1)**: On 20-digit semiprimes, standard Pollard p-1 found 5 factors where dual found 0. The B2 channel with factorial exponent is equivalent to Williams p+1 but with higher per-step cost (matrix multiplication vs scalar). At 20 digits, p-1 with B1=5000 outperforms because scalar powmod is ~10x faster per step.

**H1f (No complementary power)**: Even on semiprimes specifically chosen to have smooth p+1, the dual channel failed (0/5). The matrix overhead makes it non-competitive even in the best case.

### VERDICT: NEGATIVE

The dual-channel idea reduces to: B1 channel = trivially useless (needs k divisible by p), B2 channel = Williams p+1 with matrix overhead. The product B1*B2 adds nothing because the two channels are algebraically independent — hitting I mod p in one channel doesn't help the other. The "2D attack surface" is illusory: it is simply two independent 1D attacks, one of which (B1) is useless.

**Key insight**: Unipotent matrices have period equal to p itself, not a smooth function of p. This makes them fundamentally unsuitable for factorial/primorial exponent attacks. Only the hyperbolic B2 (whose period divides p-1 or 2(p+1)) responds to smooth exponents.

---

## HYPOTHESIS 2: Tree Zeta Function <-> Riemann Zeta Connection

### Background
Define a "tree zeta" via the Euler product over prime cycles of the Berggren action.
Conjecture: zeta_tree(s) relates to L(s, chi_4), and its zeros might encode factoring info.

### Experiment Results

| # | Experiment | Result | Key Finding |
|---|-----------|--------|-------------|
| H2a | Berggren orbit count mod p | **1 orbit for ALL p** | 23/23 primes (5..97): exactly 1 orbit on (Z/pZ)^2 \ {0}. Full transitivity confirmed |
| H2b | Orbit count vs chi4 correlation | **ZERO** | r(p) = 1 for all p, so correlation with chi4(p) is exactly 0 |
| H2c | Tree zeta sums by depth | **COMPUTED** | Z(s) at depth d decays as 3^d * (mean hypotenuse)^{-s}; no surprising structure |
| H2d | Compare to L(s, chi4) | **NO MATCH** | Ratios vary wildly (0.06 to 1.66); no algebraic relationship |
| H2e | Functional equation | **NONE** | Z(s)/Z(1-s) ratios span 15 orders of magnitude; no functional equation |
| H2f | Factoring connection | **TRIVIAL** | r(p)=1 for all p => zeta_tree(s) = zeta(s). No factoring information |

### Analysis

**H2a (Full transitivity kills the hypothesis)**: The entire hypothesis collapses at step 1. Since the Berggren group acts transitively on (Z/pZ)^2 \ {0} for every prime p >= 5, there is exactly 1 orbit per prime. This means r(p) = 1 for all p.

**H2b (Zero correlation)**: With r(p) = 1 constant, there is no dependence on chi4(p) or any other arithmetic function. The orbit count carries zero information about the prime.

**H2c-d (Zeta sums don't match L-functions)**: The tree's Dirichlet series (sum of c^{-s} over hypotenuses) is determined by the growth rate of hypotenuses, not by arithmetic structure. At depth d, there are 3^d nodes with hypotenuses growing as ~(1+sqrt(2))^d (B2 exponential) or ~d^2 (B1/B3 polynomial). This produces a series unrelated to L(s, chi4).

**H2e (No functional equation)**: The tree zeta is NOT an L-function. It lacks the Euler product structure (r(p)=1 gives the Riemann zeta, but the tree zeta counts weighted hypotenuses, not multiplicative units). No functional equation exists.

**H2f (Trivial reduction)**: If we define zeta_tree(s) = prod_p (1 - p^{-s})^{-r(p)} with r(p) = 1 for all p, we get exactly the Riemann zeta function. This is trivially true for ANY fully transitive group action, not specific to Berggren matrices.

### VERDICT: NEGATIVE

The tree zeta function hypothesis fails because full transitivity (Theorem E1) makes r(p) = 1 for all primes, collapsing the tree zeta to the ordinary Riemann zeta. There is no chi4 connection, no functional equation, and no factoring information. The tree's arithmetic is too "uniform" to produce interesting L-function structure.

**Key insight**: A zeta function encodes interesting information only when the orbit structure VARIES with the prime. Full transitivity means uniform behavior — the most boring possible zeta (= Riemann zeta itself).

---

## HYPOTHESIS 3: Congruent Number ECM Strategy

### Background
Every Pythagorean triple (a,b,c) maps to a rational point on E_{ab/2}: y^2=x^3-(ab/2)^2*x.
Can these curves with known rational points provide better ECM curves than random ones?

### Experiment Results

| # | Experiment | Result | Key Finding |
|---|-----------|--------|-------------|
| H3a | Generate curves | **364 curves** | Depth 0-5, areas from 6 to 279,909,630 |
| H3b | Group orders mod small primes | **100% smooth** | All orders are B50-smooth for primes 53-500. But this is expected: #E(F_p) ~ p, and p < 500 is always 500-smooth |
| H3c | Smoothness: congruent vs random | **1.00x ratio** | Congruent: 100%, Random: 99.8%. No difference — all small-prime orders are smooth |
| H3d | Mini-ECM on 10-digit N | **9/10 factored** | But curve 0 (n=6, the simplest) does most of the work |
| H3e | ECM comparison | **0.95x** | Congruent ECM: 19/20, Standard ECM: 20/20. Congruent is slightly WORSE |
| H3f | Known vs random point | **0.9x** | Known point: 9/10, Random point: 10/10. Known point slightly WORSE |

### Analysis

**H3a-b (Curve generation works)**: The tree generates abundant congruent number curves with known rational points. All have j-invariant 1728 (CM by Z[i]), meaning they are quadratic twists of y^2 = x^3 - x.

**H3c (No smoothness advantage)**: Group orders #E_n(F_p) for small primes p are ALWAYS smooth because #E(F_p) = p + 1 - a_p where |a_p| <= 2*sqrt(p), so #E(F_p) is in [p+1-2sqrt(p), p+1+2sqrt(p)] — a small range that is trivially smooth for small p. This is true for ALL elliptic curves, not just congruent number curves. The smoothness advantage is zero.

**H3d-e (ECM works but not better)**: Congruent number ECM is functional (9/10 at 10 digits) but slightly worse than standard ECM (19/20 vs 20/20 at the same B1 with the same number of curves). The j=1728 restriction limits curve diversity — all congruent curves are twists of a single curve, whereas random ECM samples from the full moduli space.

**H3f (Known point doesn't help)**: Starting from the tree's known rational point (c^2/4, c(a^2-b^2)/8) gives slightly WORSE results than a random starting point (9/10 vs 10/10). This is because the known point is "structured" (small coordinates relative to N) while a random point samples uniformly from E(Z/NZ), giving better coverage of the group.

### VERDICT: NEGATIVE

Congruent number curves are NOT better than random curves for ECM because:
1. **All j=1728**: This restricts to a single isomorphism class (quadratic twists of E_1). Standard ECM benefits from sampling diverse j-invariants, each giving an independent group order.
2. **Known point is redundant**: ECM's power comes from the GROUP ORDER being smooth, not from knowing a rational point. Any starting point works — the known point adds no information about the group order mod p.
3. **Smoothness is universal**: For small primes, ALL elliptic curve group orders are smooth. The congruent number property provides no additional smoothness.

**Key insight**: ECM's effectiveness depends on group order smoothness, which is determined by p (the unknown factor), not by the curve's arithmetic over Q. Knowing a rational point on E_n(Q) tells us nothing about #E_n(F_p). The curve's rank over Q and its group order over F_p are essentially independent.

---

## Grand Summary

| Hypothesis | Verdict | Core Reason |
|-----------|---------|-------------|
| H1: Dual-Channel | **NEGATIVE** | B1 (unipotent, period=p) is useless for smooth-exponent attacks; B2 alone = Williams p+1 with overhead |
| H2: Tree Zeta | **NEGATIVE** | Full transitivity makes r(p)=1 for all p, collapsing tree zeta to Riemann zeta (trivial) |
| H3: Congruent ECM | **NEGATIVE** | j=1728 restriction limits diversity; known point adds nothing about group order mod p |

### New Confirmed Results (not theorems, but verified at scale)

1. **B1^p = I mod p**: verified for all 1227 primes up to 10000 (extends T2-1 from 23 primes)
2. **ord(B2) | (p-1) or 2(p+1)**: verified for 501 primes (extends T2-2/G1)
3. **Full transitivity**: 1 orbit for all primes 5..97 (extends E1)
4. **Congruent ECM ~ standard ECM**: 0.95x ratio, confirming no advantage from tree structure

### Fundamental Barriers Reinforced

- **Unipotent period barrier**: B1/B3 have period exactly p, requiring knowledge of p to exploit. Cannot be made smooth by factorial/primorial exponents because p itself is the period.
- **Transitivity barrier**: Full transitivity means the orbit structure carries no prime-specific information. Any zeta-like construction reduces to the Riemann zeta.
- **j-invariant barrier**: All congruent number curves have j=1728, limiting ECM curve diversity. Standard ECM with random j-invariants is strictly better.
- **Point independence**: A known rational point on E(Q) provides zero information about the group structure mod an unknown prime p. ECM success depends on #E(F_p) being smooth, which is a function of p, not of the curve's rational points.

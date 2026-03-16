# Novel Mathematical Fields for Factoring — Batch 4 (Fields 16-20)

**Date**: 2026-03-15 21:32:04
**Total Runtime**: 69.6s
**Verdict**: ALL 5 FIELDS NEGATIVE

---

## Field 16: Hypergeometric Functions and Factoring

**Overall**: NEGATIVE. Hypergeometric functions are beautiful but CONTINUOUS — they cannot encode the discrete factoring structure. AGM mod N reduces to square roots mod composites, which IS factoring. Elliptic integrals at 1/N converge smoothly to pi/2 and carry no factor information. The only 'wins' are gcd side effects, equivalent to trial division or Pollard rho.

### Elliptic integral K(1/sqrt(N))
**Verdict**: K(1/sqrt(N)) is smooth and analytic — no factor information leaks through. The function is continuous so nearby N values give nearby K values regardless of factorization.

### AGM convergence and factor structure
**Verdict**: AGM converges quadratically (~-12.47 log10 ratio per step) REGARDLESS of factor structure. The convergence is determined by the initial gap |a-b| ~ 1/(2N), not by factorization.

### Clausen identity mod N
**Verdict**: Clausen identity holds exactly as a FORMAL identity — it cannot discriminate factor structure. Discrepancy is purely numerical precision artifact (~1e-29), independent of N's factorization.

### Ramanujan series truncation
**Verdict**: Ramanujan series terms mod N are just modular arithmetic — no factoring leverage. Any 'factors found' come from small factorial terms sharing factors with N (equivalent to trial division). The mathematical beauty of the series does not translate to factoring power.

### AGM factoring attempt
**Verdict**: The fundamental obstacle: computing sqrt(a*b) mod N requires factoring N. AGM over Z/NZ is circular — it reduces to the square root problem mod composites, which IS the factoring problem. Any 'accidental' factors come from gcd side effects (equivalent to Pollard rho type algorithms). No hypergeometric magic.

**Key Mathematical Insight**: The complete elliptic integral K(1/sqrt(N)) = (pi/2) * 2F1(1/2, 1/2; 1; 1/N) is a smooth, analytic function of N. For large N, K(1/sqrt(N)) -> pi/2 monotonically. The AGM (which computes K) converges quadratically with rate independent of whether N is prime or composite. Hypergeometric identities (Clausen, Kummer) hold as formal identities — evaluating both sides mod N gives the same result by construction. The mathematical beauty of these functions is entirely orthogonal to the discrete structure of factoring.

**Why AGM Can't Factor**: AGM(a,b) involves computing sqrt(a*b) at each step. Over Z/NZ, computing square roots is equivalent to factoring (finding two distinct square roots of the same value mod N gives a factor via gcd). So any AGM-based factoring approach reduces to... factoring. Circular.

## Field 17: Surreal Numbers and Combinatorial Game Theory

**Overall**: NEGATIVE. CGT adds a beautiful theoretical framework but provides ZERO computational advantage for factoring. Grundy values require exhaustive search (= trial division). Temperature equals the information-theoretic bound (= trivial). Nim-value encoding is arbitrary. The fundamental problem: factoring is NOT a two-player game — there is no adversary making choices. The game-theoretic model is a metaphor, not a tool.

### Grundy values
**Verdict**: Grundy values distinguish primes from composites trivially: for composites, there exists a winning move (a true divisor), so G >= 1. For primes, no divisor in the candidate set works, so the game is purely combinatorial on the removal sequence. This is CIRCULAR — knowing G(N) >= 1 requires trying all divisors (= trial division).

### Game temperature
**Verdict**: Game temperature = 1.0 always (binary search gives 1 bit per query, which is optimal for a single yes/no query). The adversarial model gives sqrt(N) worst case for sequential search, log2(sqrt(N)) for binary search. This is well-known and adds ZERO insight to factoring. The game-theoretic framing is a disguise for information-theoretic bounds.

### Nim-value factor structure
**Verdict**: Nim-value encoding is arbitrary — XOR of (factor-1) values has no mathematical significance for factoring. For semiprimes p*q, Nim=(p-1)^(q-1)=0 iff p=q (perfect square), which is trivially detectable. The Nim structure gives NO factoring advantage.

**Key Mathematical Insight**: Factoring is NOT a two-player game in any meaningful sense. The game-theoretic framing (one player picks divisors, the 'adversary' hides factors) is a metaphor. In the Sprague-Grundy framework, computing Grundy values requires exhaustively evaluating all positions — which IS trial division. Game temperature equals the Shannon information bound (1 bit per yes/no query). CGT provides an elegant language for discussing search strategies but cannot circumvent the information-theoretic lower bound of log2(sqrt(N)) binary queries.

## Field 18: Polynomial Identity Testing (PIT) and Factoring

**Overall**: NEGATIVE. PIT is fundamentally about testing whether a polynomial is identically zero — not about finding roots of non-zero polynomials. Factoring requires finding roots of xy-N, which PIT cannot help with. The Schwartz-Zippel reduction gives trial division. The Berlekamp analog gives quadratic residuosity tests (already known). The cyclotomic approach requires period finding (= Shor, not classical). All roads lead to known methods.

### Random evaluation g(x,y)=(x^2-N)(y^2-N)
**Verdict**: Random evaluation of x^2 mod N: finding gcd(x^2-y^2, N) > 1 requires x = +/-y mod p but not mod q. Probability ~ 1/2 IF we find x,y with x^2=y^2 mod N — but finding such pairs IS the hard part (= QS/NFS). Random evaluation without structure gives probability ~ 1/sqrt(N) per trial. PIT adds no leverage.

### Cyclotomic polynomial factoring
**Verdict**: Factoring Phi_N(x) mod r requires computing ord_N(r) = lcm(ord_p(r), ord_q(r)). But computing ord_N(r) WITHOUT knowing p,q requires factoring phi(N) = (p-1)(q-1), which requires knowing p and q. CIRCULAR. This is exactly why Shor's algorithm works on quantum computers (period finding = order finding) but is hard classically.

### Schwartz-Zippel on factoring
**Verdict**: Schwartz-Zippel on f(x,y)=xy-N gives probability 2/|S| per random evaluation. With S={1..sqrt(N)}, this needs sqrt(N)/2 trials — exactly trial division. PIT cannot beat this because the polynomial xy-N has degree 2 and the roots (p,q) are a single point in a huge domain. PIT is designed to test whether a polynomial is IDENTICALLY zero, not to find roots. Completely wrong tool for the job.

### Berlekamp analog
**Verdict**: The Berlekamp analog (computing x^N mod (x^2-N) over Z/NZ) is essentially computing Legendre/Jacobi symbols and quadratic residuosity — well-known territory. The gcd checks are related to quadratic sieve principles. This does NOT give a new algorithm; it's a repackaging of Euler's criterion and Fermat's method. When it works, it's because of algebraic structure that QS/NFS already exploit.

**Key Mathematical Insight**: PIT asks 'is this polynomial identically zero?' — factoring asks 'where are the roots of xy - N?' These are fundamentally different problems. Schwartz-Zippel applied to factoring gives trial division complexity. The deepest connection is through cyclotomic polynomials: factoring Phi_N(x) over Q corresponds to factoring N, but this requires order-finding (= Shor's algorithm, quantum). The Berlekamp analog over Z/NZ reduces to quadratic residuosity, which is already well-exploited by QS/NFS.

## Field 19: Etale Homotopy and Factoring

**Overall**: NEGATIVE. The étale/algebraic-geometric perspective beautifully DESCRIBES factoring but cannot SOLVE it. Key findings: (1) Nontrivial idempotents exist iff N is composite, but finding them IS factoring. (2) Random search for idempotents is WORSE than trial division (O(N) vs O(sqrt(N))). (3) Newton lifting of idempotents needs starting points within O(min(p,q)) of a fixed point — requires factor knowledge. (4) Z/NZ for RSA numbers is semisimple with trivial Jacobson radical — no nilpotent shortcuts. The abstraction is a language change, not a computational advance.

### Idempotent search
**Verdict**: Random idempotent search has probability 4/N per trial — need O(N) trials. This is WORSE than trial division (O(sqrt(N))). The étale structure tells us idempotents EXIST (there are exactly 2^k nontrivial ones for k prime factors), but finding them is as hard as factoring.

### Hensel lifting idempotents
**Verdict**: Newton iteration for idempotents converges quadratically — but only from the basin of attraction of a nontrivial fixed point. For N=pq, the basins are the sets {e : |e-e_i| < min(p,q)/4}. Random starting points hit these basins with probability ~O(1/sqrt(N)). When it works, it's essentially a variant of the p-1 or p+1 methods. No improvement over known algorithms.

### Spectral detection of components
**Verdict**: The permutation x -> ax mod N has cycle structure determined by ord_N(a), which splits as lcm(ord_p(a), ord_q(a)). The NUMBER of cycles = gcd(N, a^{ord_N(a)/gcd} - 1)... complex but ultimately: extracting factor information from cycle structure requires computing orders mod p and q separately, which requires knowing p and q. The spectral approach detects 'two components' only after factoring.

### Nilpotent/Jacobson radical
**Verdict**: For squarefree semiprimes N=pq (the RSA case), the Jacobson radical is trivial: J(Z/NZ) = {0}. There are NO nilpotent elements. The ring Z/NZ is already semisimple (product of fields). Finding the idempotent decomposition IS equivalent to factoring. The étale structure elegantly DESCRIBES the factorization but provides no computational shortcut to FIND it.

**Key Mathematical Insight**: Spec(Z/NZ) for N=pq decomposes as the disjoint union Spec(Z/pZ) + Spec(Z/qZ). The etale fundamental group detects this via connected components, which correspond to nontrivial idempotents in Z/NZ. Finding these idempotents IS factoring (gcd(e, N) gives a factor). The algebraic geometry provides a perfect DESCRIPTION of the problem but no computational shortcut. Newton iteration for idempotents (e -> 3e^2 - 2e^3) converges quadratically but only from basin of attraction ~O(min(p,q)) wide — need to already be 'close' to a factor. For RSA-type N=pq, the ring Z/NZ is semisimple (no nilpotents, trivial Jacobson radical), so no radical-based shortcuts exist.

## Field 20: Information Geometry of Factor Distributions

**Overall**: NEGATIVE, but with an interesting mathematical insight: Fisher information at a true factor of N is EXACTLY ZERO because N mod p = 0 means the score function vanishes. Information geometry cannot distinguish factors from non-factors because the relevant quantity (N mod x) is a piecewise-constant discrete function — the Riemannian structure adds overhead without information. Natural gradient descent degenerates to random walk. The framework is beautiful but fundamentally mismatched to the discrete factoring problem.

### Fisher information of factor model
**Verdict**: Fisher information peaks where N mod x changes rapidly — near divisors of N, YES, but also near any x where floor(N/x) changes (= x ~ N/k for any integer k). The peaks at true factors are NOT distinguishable from the forest of peaks at near-divisors. The 'information' about factors is drowned in the same noise that makes trial division necessary.

### Natural gradient descent
**Verdict**: Natural gradient descent on the factor loss landscape fails because: (1) (N mod x) is PIECEWISE CONSTANT (discrete), so the gradient is zero almost everywhere and infinite at jumps. (2) The Fisher information metric is degenerate at the same points. (3) 'Smoothing' the landscape destroys the factor information. (4) Both standard and natural GD behave like random walks on this landscape. No information-geometric advantage over random search.

### Curvature of factor manifold
**Verdict**: 1D statistical manifold is ALWAYS flat (Riemannian curvature = 0). The 2D manifold (x, lambda) has nontrivial curvature but it reflects the smoothing scale interaction, NOT factor structure. Fisher information at the true factor p: at p, N mod p = 0, so the score function = 0, meaning Fisher info = 0 at the exact factor! The information geometry is MAXIMALLY UNINFORMATIVE at the answer because the loss function is exactly zero there.

### Geodesic distances
**Verdict**: Geodesic distances in the Fisher metric are dominated by regions where N mod x changes rapidly (near x = N/k for small k). The true factor p does NOT sit at a geodesic extremum or saddle point — it's at a ZERO of the Fisher metric (where N mod p = 0, score = 0). The geodesic structure provides no way to distinguish factors from non-factors.

### Search comparison benchmark
**Verdict**: Information-geometric search performs COMPARABLY to random search and WORSE than sequential search for small factors. The natural gradient adds computational overhead without reducing the number of evaluations. Sequential search wins because it's deterministic and exhaustive. Random search wins by birthday paradox for balanced semiprimes. Info geometry provides a LANGUAGE for describing the problem, not a SOLUTION.

**Key Mathematical Insight (the interesting one)**: The Fisher information of the smoothed factor model P(N|x) ~ exp(-lam*(N mod x)^2) is EXACTLY ZERO at a true factor p, because N mod p = 0 means the score function d/dx log P = 0. This is a minimax saddle: factors are at the minimum of the loss landscape, where the gradient vanishes and the Fisher metric degenerates. Information geometry cannot distinguish this zero from any other local minimum of (N mod x). Natural gradient descent degenerates to random walk because the Fisher metric is degenerate at zeros. The 1D manifold of factor candidates is trivially flat (all 1D Riemannian manifolds have zero curvature). Even the 2D manifold (x, lambda) doesn't help — curvature reflects smoothing-scale interaction, not factor structure.

**Why Information Geometry Fails for Factoring**: The fundamental mismatch is that (N mod x) is PIECEWISE CONSTANT — it has no useful derivative. Smoothing it into a continuous function either (a) preserves the discreteness (lambda -> infinity, back to N mod x) or (b) destroys the factor signal (lambda -> 0, everything smooth). There is no 'Goldilocks' smoothing that makes gradient-based methods work. This is a manifestation of the broader principle that factoring is a discrete, number-theoretic problem that resists continuous optimization.

---

## Grand Summary: All 20 Fields (Batches 1-4)

| Field | Domain | Verdict | Key Obstruction |
|-------|--------|---------|-----------------|
| 16 | Hypergeometric Functions | NEGATIVE | Continuous functions can't encode discrete factors; AGM sqrt = factoring |
| 17 | Combinatorial Game Theory | NEGATIVE | Grundy values = exhaustive search; temperature = info bound |
| 18 | Polynomial Identity Testing | NEGATIVE | PIT tests identity, not roots; SZ = trial division; cyclotomic = quantum |
| 19 | Etale Homotopy | NEGATIVE | Idempotents = factors (circular); Newton basin too narrow; RSA semisimple |
| 20 | Information Geometry | NEGATIVE | Fisher info = 0 at factors; piecewise-constant landscape; GD = random walk |

### Recurring Obstruction Themes Across All 270+ Fields

1. **Continuous vs Discrete**: Most mathematical tools (analysis, geometry, topology) operate on continuous objects. Factoring is fundamentally discrete. Any continuous relaxation either loses the signal or requires solving an equally hard continuous problem.
2. **Circularity**: Many approaches reduce to 'if we knew a factor, we could...' — which is exactly what we're trying to find. Square roots mod N, idempotents, order finding, etc.
3. **Information-Theoretic Bounds**: The factoring problem contains ~log(p) bits of information. Any method that extracts < 1 bit per O(1) operation cannot beat the information-theoretic bound of O(sqrt(N)) for unstructured search (birthday bound) or L(1/3, c) for structured algebraic approaches (NFS).
4. **Known Reductions**: Every approach we tested either reduces to a KNOWN algorithm (trial division, Pollard rho, QS, NFS, Shor) or to a HARDER problem (discrete log, lattice reduction, etc.).

### The Hardness Barrier

After 270+ fields, the evidence strongly suggests that classical factoring is trapped between L(1/3) (NFS) and L(1/2) (CFRAC) complexity, with no path to polynomial time. The only known sub-L(1/3) approach is Shor's algorithm, which requires quantum computation. This is consistent with the widely-held (but unproven) conjecture that factoring is not in P.

*Generated 2026-03-15 21:32:04*
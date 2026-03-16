# Master Theorem Catalog

**Total: 101 theorems (29 high, 72 medium)**

*Compiled from 10 source files. Only HIGH and MEDIUM significance theorems included.*
*Date: 2026-03-16*

---

## High Significance

### Pythagorean Tree -- Algebraic Structure

| ID | Name | Statement | Status | Source |
|----|------|-----------|--------|--------|
| T10 | Berggren Group | The Berggren group G = <B1,B2,B3> in GL(2,F_p) has \|G\| = 2p(p^2-1), where G = {matrices with det = +/-1}. | Proven | MASTER_RESEARCH.md |
| T25 | Perfect Group | <B1,B3> mod p generates SL(2,F_p), which is perfect for p >= 5. | Proven | MASTER_RESEARCH.md |
| T28 | Unipotent Commutator | The commutators [A,B] and [B,C] are unipotent of nilpotency index 3 over Z: ([A,B]-I)^3 = 0 but ([A,B]-I)^2 != 0. Consequently, ord([A,B] mod p) = ord([B,C] mod p) = p for every prime p >= 5. [A,C] is NOT unipotent (trace=35); its order mod p divides (p-1) or 2(p+1). | Proven (algebraic + 13 primes) | pyth_theorems_v2.md |
| T66 | Unipotent Fermat Analog | B1^p = B3^p = I mod p for all primes p; B1, B3 are unipotent of exact order p. | Proven | MASTER_RESEARCH.md |
| T67 | Exact Orders | ord(B1) = ord(B3) = p; ord(B2) divides (p-1) or 2(p+1) depending on quadratic residuosity of 2 mod p. | Proven | MASTER_RESEARCH.md |

### Pythagorean Tree -- Continued Fractions and Analytic

| ID | Name | Statement | Status | Source |
|----|------|-----------|--------|--------|
| T9 | CF Generation (CF1) | B2 path ratios = convergents of 1+sqrt(2) = [2; 2, 2, ...]. | Proven | MASTER_RESEARCH.md |
| T25-v2 | Branch CF Formulas | Branch A at step k: CF(c/a) = [k+1, 1, 1, k+1] (palindromic). Branch C at step k: CF(c/a) = [n, 4n] where n=k+1. Branch B: c/a converges to sqrt(2). | Proven (A,C) / Conjecture (B) | pyth_theorems_v2.md |
| T35-v2 | Tree Zeta Function | zeta_tree(s) = sum_{PPT} c^{-s} has abscissa of convergence at s=1, with partial sums growing as C*log(X) where C ~ 1/(2*pi). Has Euler product restricted to primes p = 1 mod 4. | Proven (convergence), Conjecture (Euler product) | pyth_theorems_v2.md |
| T-v11-10 | Tree Zeta Abscissa | The Pythagorean tree zeta function zeta_T(s) has abscissa of convergence s_0 = log(3)/log(3+2*sqrt(2)) ~ 0.623239, equal to the Hausdorff dimension of the tree on the hypotenuse axis. | Proven | v11_theorem_hunter_results.md |
| TREE-ZETA-NO-FE | Tree Zeta No Functional Equation | zeta_T(s) has NO Euler product (sum-of-2-squares indicator is not multiplicative), NO functional equation (no s <-> 1-s symmetry), and NO critical line. It is an arithmetic Dirichlet series without automorphic structure. | Proven | v12_riemann_deep2_results.md |

### Pythagorean Tree -- Connections to Number Theory

| ID | Name | Statement | Status | Source |
|----|------|-----------|--------|--------|
| T34-v2 | Congruent Number Curve Map | Every PPT (a,b,c) maps to a rational point on the elliptic curve E_n: y^2 = x^3 - n^2*x where n=ab/2 (triangle area), via x=(c/2)^2, y=c(b^2-a^2)/8. The Berggren tree is an infinite generator of congruent numbers with constructive witnesses. | Proven | pyth_theorems_v2.md |
| T-v12-4 | Pythagorean Goldbach | (1) THEOREM: n = 0 mod 4 can NEVER be the sum of two hypotenuse primes (proof: 1+1 = 2 mod 4). (2) CONJECTURE: Every n = 2 mod 4 above a small threshold IS the sum of two primes = 1 mod 4. Verified up to 100,000. | Theorem + Conjecture | v11_theorem_hunter_results.md |
| T-v11-11 | Pythagorean Cassini | B2-path hypotenuses (c_k) satisfy c_{k-1}*c_{k+1} - c_k^2 = C*(3+2*sqrt(2))^(2k). The ratio of consecutive Cassini values is (3+2*sqrt(2))^2 ~ 33.97. Exponential analog of the Fibonacci identity F(n-1)F(n+1)-F(n)^2=(-1)^n. | Proven | v11_theorem_hunter_results.md |
| T-v11-7 | Index-2 Commutator | The commutator subgroup [G,G] has index EXACTLY 2 in the Berggren group G mod p. Abelianization is G/[G,G] = Z/2Z. The commutator subgroup is the kernel of the determinant map (det=+1 elements). Refines T25. | Proven | v11_theorem_hunter_results.md |
| IHARA-BERGGREN | Ihara Zeta of Berggren Graph | The Ihara zeta Z_G(u) of the Berggren Cayley graph mod p has non-trivial zeros satisfying \|u\| = 1/sqrt(2) (Ramanujan radius). All tested primes have 100% of zeros on the RH circle. The spectral gap (~0.33) confirms the graph is an expander. | Proven | v12_riemann_deep2_results.md |

### Exotic Number Systems

| ID | Name | Statement | Status | Source |
|----|------|-----------|--------|--------|
| EN-4 | Dual Shadow Linearization | The dual Pythagorean equation (a_0+a_1*eps)^2+(b_0+b_1*eps)^2=(c_0+c_1*eps)^2 decomposes into: (1) Standard: a_0^2+b_0^2=c_0^2 (nonlinear). (2) Shadow: a_0*a_1+b_0*b_1=c_0*c_1 (LINEAR). The shadow equation gives a linear congruence mod N at each tree node. Short vectors in the solution lattice can reveal factors. | Proven | v11_exotic_numbers_results.md |
| EN-5 | Z[sqrt(N)] Class Group Walk | The Berggren tree over Z[sqrt(N)] for N=pq generates a structured walk on the ideal class group of Q(sqrt(N)). Smooth norms yield factoring relations, connecting the Pythagorean tree to CFRAC/QS-type factoring. Factors found in 1-24 steps for small semiprimes. | Proven (structural) | v11_exotic_numbers_results.md |

### Complexity Theory and Barriers

| ID | Name | Statement | Status | Source |
|----|------|-----------|--------|--------|
| T61 | Dickman Information Barrier | Conditional: generic sieve algorithms require L[1/3,c] candidates. Relations/bits overhead grows as 10^(0.24*digits). | Conditional theorem | MASTER_RESEARCH.md |
| T62 | SIQS Scaling Law | SIQS fits L[1/2, c=0.991] -- matches sub-exponential theory precisely. | Verified | MASTER_RESEARCH.md |
| T73 | DLP in AM cap coAM | DLP cannot be NP-complete unless the polynomial hierarchy collapses (Boppana-Hastad-Zachos). | Proven (structural) | MASTER_RESEARCH.md |
| T75 | Two-Barrier Escape | DLP has candidate escapes for natural proofs (non-large homomorphism) AND algebrization (non-polynomial Frobenius); relativization remains unbroken. | Proven (structural) | MASTER_RESEARCH.md |
| T119 | Factoring in PPP \ PLS | Factoring belongs to PPP (Polynomial Pigeonhole Principle) but NOT to PLS (Polynomial Local Search). Evidence: cost landscape has 31% local minima (near-random ruggedness); x^2 mod N has exactly 4 fixpoints by CRT; finding nontrivial collision factors N. | Proven (structural) | v12_millennium2_results.md |
| T121 | Descriptive Complexity Bottleneck | GF(2) Gaussian elimination is P-complete under logspace reductions. SIQS/GNFS linear algebra CANNOT be parallelized to NC depth unless P = NC. Block Lanczos reduces to O(n) sequential matrix-vector products. This is a FUNDAMENTAL barrier to massively parallel factoring. | Proven | v12_millennium2_results.md |
| T117 | Millennium-Factoring Independence | Across 30 experiments connecting factoring to 5 Millennium Prize Problems (P vs NP, BSD, Riemann, Hodge, Navier-Stokes), ALL connections are either: (1) circular (computing the connection requires factoring), (2) vacuous (structure exists but no computational shortcut), or (3) barrier-blocked. | Meta-theorem | v12_millennium_results.md |

### ECDLP Barriers

| ID | Name | Statement | Status | Source |
|----|------|-----------|--------|--------|
| T82 | HoTT Transport = DLP | Univalence proves DLP path exists but computing the transport map IS solving DLP. | Proven | MASTER_RESEARCH.md |
| T81 | NCG Generator-Independence | Spectral triple for Z/nZ encodes group order n but NOT which element generates -- spectrum is generator-independent. | Proven | MASTER_RESEARCH.md |

### Riemann Zeta and Factoring

| ID | Name | Statement | Status | Source |
|----|------|-----------|--------|--------|
| HODGE-GNFS | GNFS Curve Genus | GNFS polynomial of degree d defines a curve of genus g=(d-1)(d-2)/2. Weil bound \|#C(F_p)-(p+1)\| <= 2g*sqrt(p) explains sieve yield variance. d=5 (RSA-100): g=6, fluctuation ~12*sqrt(p). Hodge-theoretic explanation of why GNFS polynomial selection matters. | Proven | v12_riemann_cf_results.md |
| EPSTEIN-FACTORING | Epstein Zeta and Factoring | Epstein zeta zeta_Q(s) for Q(m,n)=m^2+Nn^2 satisfies zeta_Q(s)=zeta(s)*L(s,chi_{-4N}). For N=pq, chi_{-4pq} factors as chi_{-4}*chi_p*chi_q. This factorization of the CHARACTER equals factorization of N, but extraction requires O(sqrt(N)) terms. Circular. | Proven (structural) | v12_riemann_deep2_results.md |

---

## Medium Significance

### Pythagorean Tree -- Ergodic/Spectral

| ID | Name | Statement | Status | Source |
|----|------|-----------|--------|--------|
| T1 | Full Transitivity | Orbit of (2,1) under {B1,B2,B3} mod p covers 100% of (Z/pZ)^2\{0} for all primes tested. | Verified | MASTER_RESEARCH.md |
| T2 | Fast Mixing | Spectral gap ~0.33, mixing in ~3 steps regardless of p. | Verified | MASTER_RESEARCH.md |
| T3 | Strong Expander | Spectral gap ~0.33, well above Ramanujan bound 0.057 for 3-regular graphs. | Verified | MASTER_RESEARCH.md |
| T4 | Height-Smoothness | All depth<=7 triples are 1000-smooth; rate decays to ~38% at depth 14. | Verified | MASTER_RESEARCH.md |
| T5 | Angular Non-uniformity | Tree angles mod p have chi^2/df ~80x uniform; ~50% residue coverage. | Verified | MASTER_RESEARCH.md |

### Pythagorean Tree -- Algebraic Structure (Medium)

| ID | Name | Statement | Status | Source |
|----|------|-----------|--------|--------|
| T6 | Symplectic Dichotomy | B1, B3 symplectic (det=1); B2 anti-symplectic (det=-1). | Proven | MASTER_RESEARCH.md |
| T7 | Galois-Period | B2 period divides (p-1) when (2/p)=1, 2(p+1) when (2/p)=-1. | Proven | MASTER_RESEARCH.md |
| T8 | Trace Invariance | B1, B3 trace=2 for all k; B2 trace follows Pell recurrence. | Proven | MASTER_RESEARCH.md |
| T11 | Swap Closure | Tree is closed under (a,b) swap -- 100% verified. | Verified | MASTER_RESEARCH.md |
| T12 | B1-B3 Disjointness | B1 and B3 generate completely disjoint A-value sets. | Verified | MASTER_RESEARCH.md |
| T68 | CRT Period Decomposition | period_N = lcm(period_p, period_q) -- proven for composite N=pq. | Proven | MASTER_RESEARCH.md |
| T69 | p-adic Period Lifting | period mod p^n ~ period_p * p^{n-1} for n >= 2; Hensel lifting of tree periods. | Proven | MASTER_RESEARCH.md |

### Pythagorean Tree -- Smoothness/Sieve

| ID | Name | Statement | Status | Source |
|----|------|-----------|--------|--------|
| T13 | Smoothness Advantage | Tree A-values 3-7x more likely B-smooth than random integers of comparable size. | Verified | MASTER_RESEARCH.md |
| T14 | B1 Conservation | On pure B1 path, m_k - n_k = 1 for all k; halves effective A-size. | Proven | MASTER_RESEARCH.md |
| T15 | Selberg Bound | Factor balance alpha=0.4 gives ~276x advantage in smoothness probability. | Verified | MASTER_RESEARCH.md |
| T16 | B3 Linear | B3 with n=1: 22.2% smooth vs 4.4% random (5x advantage) at B=100. | Verified | MASTER_RESEARCH.md |
| T17 | Matroid Low-Rank | Factored-form gives low GF(2) matroid rank; 5.7x smooth at depth 12. | Verified | MASTER_RESEARCH.md |
| T18 | Discriminant Diversity | Length-4 paths generate 18 distinct discriminants. | Verified | MASTER_RESEARCH.md |

### Pythagorean Tree -- Dynamics/Growth

| ID | Name | Statement | Status | Source |
|----|------|-----------|--------|--------|
| T19 | Lyapunov Exponents | B2: lambda=0.88 (exponential growth); B1/B3: ~0.03 (polynomial growth). | Verified | MASTER_RESEARCH.md |
| T20 | No Fixed Points | B2 has zero fixed points on (Z/pZ)^2\{0}. | Proven | MASTER_RESEARCH.md |
| T21 | Equidistribution | Tree m-values converge to equidistribution mod p. | Verified | MASTER_RESEARCH.md |
| T22 | CRT Period | period(N) = lcm(period(p), period(q)) -- exactly confirmed. | Proven | MASTER_RESEARCH.md |
| T23 | Geometric Mean Growth | Geo mean grows as c0*(3+2*sqrt(2))^d; Lyapunov = log(3+2*sqrt(2)) ~ 1.763. | Proven | MASTER_RESEARCH.md |

### Pythagorean Tree -- Structural

| ID | Name | Statement | Status | Source |
|----|------|-----------|--------|--------|
| T27 | CFRAC-Tree Equivalence | CFRAC = Pythagorean tree with adaptive step sizes M(a_k). Analogy, not bijection. | Proven (analogy) | MASTER_RESEARCH.md |
| T28-orig | Brahmagupta-Fibonacci | Two sum-of-squares representations -> 100% factor extraction (but finding reps is O(sqrt(N))). | Proven | MASTER_RESEARCH.md |
| T29 | Cross-Poly LP Resonance | 3.298x LP collision rate above random -- VERIFIED. | Verified | MASTER_RESEARCH.md |
| T30 | Discriminant Identity | disc = 16*N*n0^4 -- 100% verified (19701/19701 cases). | Verified | MASTER_RESEARCH.md |
| T31 | Hypotenuse Primes | All prime C from tree are 1 mod 4; fraction 32.4% vs expected 9.3% (3.5x enrichment). | Proven | MASTER_RESEARCH.md |
| T32 | Jacobi Two-Square | r2(C) = 4(d1(C) - d3(C)) confirmed on tree (Jacobi's classical result). | Verified | MASTER_RESEARCH.md |
| T34 | Area Divisibility | ALL areas of primitive triples are divisible by 6. | Proven | MASTER_RESEARCH.md |
| T35 | Hypotenuse Residue Bias | No hypotenuse is divisible by primes p = 3 mod 4. | Proven | MASTER_RESEARCH.md |
| T36 | Leg Ratio Golden | Mean min/max leg ratio = 0.6158, close to 1/phi = 0.618. | Verified | MASTER_RESEARCH.md |
| T37 | Twin Triples | 5749 A-twins (differ by 2), zero B-twins and C-twins in tree at depth 10. | Verified | MASTER_RESEARCH.md |
| T38 | Totient Bias | Mean phi(C)/C = 0.933, much higher than random 6/pi^2 = 0.608. | Verified | MASTER_RESEARCH.md |

### Pythagorean Tree -- v2 Theorems (Medium)

| ID | Name | Statement | Status | Source |
|----|------|-----------|--------|--------|
| T21-v2 | Parity Invariant | Every PPT in the Berggren tree has form (odd, even, odd). All three matrices preserve this parity pattern. All hypotenuses are odd. | Proven | pyth_theorems_v2.md |
| T22-v2 | Prime Hypotenuse Gap Law | (a) Every prime hypotenuse satisfies p = 1 mod 4. (b) Minimum gap between consecutive prime hypotenuses is 4. (c) Most common gaps: 12, 24, 60, 36, 48. | Proven (a), Verified (b,c) | pyth_theorems_v2.md |
| T27-v2 | Both-Legs-Prime Impossibility | In a PPT, it is IMPOSSIBLE for both legs to be prime. The even leg b=2mn >= 4 always, so b is always composite. | Proven | pyth_theorems_v2.md |
| T30-v2 | Gaussian Integer Norm Identity | Map (a,b,c) -> z=a+bi embeds each PPT into Z[i] with norm N(z)=c^2. Gaussian GCD of two embedded triples detects shared hypotenuse prime factors. | Proven | pyth_theorems_v2.md |
| T31-v2 | Mobius Super-Cancellation | Summatory Mobius function over tree hypotenuses: \|M\|/N ~ 0.00012, which is 28x smaller than expected for random integers (~1/sqrt(N)). Enhanced cancellation from all prime factors being 1 mod 4. | Conjecture (strong evidence) | pyth_theorems_v2.md |
| T36-v2 | Tree Count = r2(c)/8 | For each hypotenuse value c, the number of Berggren tree triples with that hypotenuse equals r2_prim(c)/8. | Proven | pyth_theorems_v2.md |
| T38-v2 | Fast Random Walk Convergence | Random walk on Berggren tree mod p converges to stationary distribution in O(log p) steps. Orbit size saturates at ~p^2 states. | Conjecture | pyth_theorems_v2.md |

### v11 Theorem Hunter (Medium)

| ID | Name | Statement | Status | Source |
|----|------|-----------|--------|--------|
| T-v11-2 | QR on PPTs | For all PPTs (a,b,c) with gcd(a,c)=1, the Jacobi symbol product (a/c)*(c/a) = +1. Follows from QR + c = 1 mod 4 for all PPTs. | Proven | v11_theorem_hunter_results.md |
| T-v11-3 | Twin Hypotenuse Prime Impossibility | There are NO twin primes (p, p+2) where both are hypotenuse primes (= 1 mod 4), because p = 1 mod 4 forces p+2 = 3 mod 4. Minimal gap between consecutive hypotenuse primes is 4. | Proven | v11_theorem_hunter_results.md |
| T-v11-6 | Lyapunov Universality | Random Berggren path products of depth d have \|lambda_max\| ~ exp(1.2999*d). Lyapunov exponent matches log(3+2*sqrt(2)) ~ 1.7627. Normalized eigenvalue distribution converges to a universal law. | Verified | v11_theorem_hunter_results.md |
| T-v11-14 | Cayley Graph Diameter | Berggren Cayley graph mod p has diameter ~ 1.298*log(\|G\|) = O(log p). Confirms expander graph with logarithmic diameter. | Proven | v11_theorem_hunter_results.md |
| T-v11-15 | Maximal Address Entropy | Tree address entropy per step = 1.5850 bits = log_2(3). Each branch choice is essentially uniform. | Proven | v11_theorem_hunter_results.md |

### v12 Theorem Hunter

| ID | Name | Statement | Status | Source |
|----|------|-----------|--------|--------|
| T102 | Zaremba-Berggren Dichotomy | B2 branches have bounded max partial quotient (Zaremba-like, max PQ = 5 from B2 ratio converging to 3+2*sqrt(2) = [5;1,4,1,4,...]). B1/B3 branches have unbounded max PQ (up to 19M). | Verified | v12_theorem_hunter_results.md |
| T103 | Markov-Pythagoras Gap | For PPTs, the Markov ratio (a^2+b^2+c^2)/(3abc) = 2c/(3ab) is NEVER 1. PPTs and Markov triples live in disjoint algebraic worlds. | Proven | v12_theorem_hunter_results.md |
| T107 | Pythagorean Linnik Ratio | Largest-smallest Pythagorean prime in APs is on average 1.97x the regular Linnik bound. Pythagorean constraint exactly halves AP density. | Verified | v12_theorem_hunter_results.md |
| T108 | PPT ABC Quality Bound | For PPTs, ABC quality q = log(c)/log(rad(abc)) has mean 0.38, max 0.62. 0% exceed q=1. PPTs are ABC-tame. | Verified | v12_theorem_hunter_results.md |
| T110 | Tree Zeta Rationality | zeta_T(s)/pi^s is NOT a rational number at even integers (unlike Riemann zeta). Breaks the Bernoulli number pattern. | Proven | v12_theorem_hunter_results.md |
| T111 | Apollonius-Pythagoras Incompatibility | PPTs used as curvatures in Descartes' circle theorem give integer fourth curvature 0% of the time. Pythagorean and Apollonius quadratic constraints are incompatible. | Proven | v12_theorem_hunter_results.md |
| T112 | Berggren Cayley Chromatic | Cayley graph of Berggren group has chromatic number ~5 and max clique size 4, bounded as p grows. Expander property prevents large monochromatic structures. | Verified | v12_theorem_hunter_results.md |
| T113 | Kolmogorov Address Compression | Tree addresses compress triples to 0.260 of original bits (theory: 0.208). Ratio is PROVABLY OPTIMAL. The tree IS the optimal encoding of PPTs. | Proven | v12_theorem_hunter_results.md |
| T115 | Pythagorean Scale | PPT leg ratios reduced to one octave generate a Pythagorean musical scale. (3,4,5) = exact perfect fourth (4/3). (8,15,17) = exact major seventh (15/8). | Verified | v12_theorem_hunter_results.md |
| T116 | Benford Compliance | Hypotenuse leading digits follow Benford's law with chi^2 distance 0.0000 (perfect). Follows from irrationality of log10(3+2*sqrt(2)) via Weyl equidistribution. | Proven | v12_theorem_hunter_results.md |

### Exotic Number Systems (Medium)

| ID | Name | Statement | Status | Source |
|----|------|-----------|--------|--------|
| EN-2 | Quaternion Non-Commutativity | For quaternions m,n in H, the identity (m^2-n^2)^2+(2mn)^2=(m^2+n^2)^2 holds if and only if mn=nm (m,n lie in same C subset of H). | Proven | v11_exotic_numbers_results.md |
| EN-3 | Split-Complex Decomposition | Z[j] ~ Z x Z. A split-complex Pythagorean triple decomposes into a PAIR of independent integer Pythagorean triples. A single Z[j] walk searches two paths simultaneously. | Proven | v11_exotic_numbers_results.md |

### Complexity Theory (Medium)

| ID | Name | Statement | Status | Source |
|----|------|-----------|--------|--------|
| T63 | Compression Barrier | Semiprimes indistinguishable from random (gap < 0.006 in compressibility). | Verified | MASTER_RESEARCH.md |
| T64 | Communication Lower Bound | One-way factoring communication is Omega(n) bits. | Proven | MASTER_RESEARCH.md |
| T65 | B3-SAT Debunked | B3 mod 2 = Identity; eigenvector extraction WORSE than random guessing. | Proven | MASTER_RESEARCH.md |
| T70 | DLP Non-Natural Property | DLP homomorphism property is exponentially non-large -- escapes natural proof barrier in principle. | Proven (structural) | MASTER_RESEARCH.md |
| T71 | ABP Width for EC | EC addition polynomial has ABP width Omega(10-12); scalar mult has doubly-exponential degree. | Proven | MASTER_RESEARCH.md |
| T74 | DLP-PvsNP Oracle Independence | All 4 combos of DLP-hard/easy x P=NP/P!=NP realizable by oracles -- logically independent. | Proven | MASTER_RESEARCH.md |
| T86 | Classic Algo Equivalence | Sieve IS sweep line; Gauss IS optimal DP; BSGS IS MITM; comb IS memoization -- all already applied in our engines. | Proven | MASTER_RESEARCH.md |
| T87 | Multi-Speed Rho Futility | k pointers cost k(k+1)/2 evals for k(k-1)/2 pairs -- ratio always O(1), cannot beat O(N^{1/4}). | Proven | MASTER_RESEARCH.md |
| T89 | GNFS Poly Search Range | SA found 10^4.2 better norm by searching +/-20K instead of +/-1000 around m0. | Verified | MASTER_RESEARCH.md |
| T120 | Ring vs Group Oracle | In generic group of order N=pq, order-finding requires Theta(N^{1/2}) queries. Ring Z_N zero-divisor search also requires ~N^{1/2}. Ring structure does NOT provide sub-sqrt(N) oracle advantage. | Verified | v12_millennium2_results.md |
| T122 | Smooth Detection Non-Monotonicity | 'x is B-smooth' is NOT monotone in value ordering (17% violations for B=30). IS monotone under divisibility. Razborov monotone circuit lower bounds apply to non-smooth detection but not smooth detection. | Proven | v12_millennium2_results.md |

### ECDLP Barriers (Medium)

| ID | Name | Statement | Status | Source |
|----|------|-----------|--------|--------|
| T76 | Motivic Uniformity | Near-miss distribution \|x(kG)-x(P)\| is uniform on F_p -- no exploitable structure for ECDLP. | Verified | MASTER_RESEARCH.md |
| T77 | Derived Triviality | Derived AG collapses to classical for smooth curve over finite field -- higher homotopy trivial. | Proven | MASTER_RESEARCH.md |
| T78 | Perfectoid Mismatch | Tilting is multiplicative; destroys additive EC group law. Over F_p, tilting = identity. | Proven | MASTER_RESEARCH.md |
| T79 | Condensed Discreteness | Condensed math adds structure only to infinite topological groups; E(F_p) is finite discrete. | Proven | MASTER_RESEARCH.md |
| T80 | Topos Equivalence | Etale infinity-topos gives Frobenius eigenvalues = #E(F_p) only, not DLP. | Proven | MASTER_RESEARCH.md |
| T83 | Spatial Pseudorandomness | EC multiples are spatially indistinguishable from random (Ripley's K matches Poisson). | Verified | MASTER_RESEARCH.md |
| T84 | QEC Classical Futility | Classical syndrome computation costs O(kG) per candidate -- no advantage over exhaustive search for ECDLP. | Proven | MASTER_RESEARCH.md |
| T85 | Ramsey Structure Absence | Monochromatic EC subsets have no DLP-useful structure -- Ramsey can't overcome pseudorandomness. | Verified | MASTER_RESEARCH.md |

### Riemann/Zeta Connections (Medium)

| ID | Name | Statement | Status | Source |
|----|------|-----------|--------|--------|
| DICKMAN-SIQS | Dickman-SIQS Verification | Dickman rho(u) predicts SIQS smoothness rates within 10%. SIQS u ranges from 4.0 (48d) to 4.5 (72d). The decay rho(u) ~ u^{-u} IS the information-theoretic barrier. | Verified | v12_riemann_cf_results.md |
| EXPLICIT-FB | Explicit Formula for FB | pi(x) with 100 zeta zeros achieves <1% error for x>1000. pi(B)/2 accurately predicts factor base size for SIQS. Useful for automated parameter tuning. | Verified | v12_riemann_cf_results.md |
| L-FUNC-BARRIER | L-Function Barrier | Dirichlet L-functions L(1, chi_N) encode factoring info through class number h(D), but computing L(1, chi_N) requires O(sqrt(N)) terms. No faster than trial division. Computationally circular. | Proven | v12_riemann_cf_results.md |
| PELL-FACTOR | Pell Factor Extraction | Pell equation fundamental solution factors ~50% of semiprimes via gcd(x0+/-1, N), but finding x0 requires O(sqrt(N)) CF steps. | Verified | v12_riemann_cf_results.md |
| SIEVE-NO-NS | Sieve Is Not Navier-Stokes | Sieve process is a multiplicative cascade (product of independent Bernoulli trials at each prime), NOT a PDE flow. No blow-up singularities, no turbulence. Fully described by Dickman/Mertens theory. | Proven | v12_riemann_cf_results.md |
| ZETA-N-CIRCULAR | Euler Product Circularity | For N=pq, zeta(s)/zeta_N(s) = 1/((1-p^{-s})(1-q^{-s})) uniquely determines p,q. But constructing zeta_N(s) requires knowing p,q. Detection of missing Euler factors by pair testing requires O(pi(B)^2) work. Circular. | Proven | v12_riemann_deep2_results.md |
| QUE-BERGGREN | QUE-Berggren Connection | Berggren matrices generate a Zariski-dense subgroup of SL(2,Z). Random walk equidistributes in O(log(p)/gap) steps. Finite-group analog of Lindenstrauss arithmetic QUE. Common ancestor: representation-theoretic spectral gap of automorphic forms. | Proven | v12_riemann_deep2_results.md |
| SMOOTH-POISSON | Smooth Number Poisson Process | B-smooth numbers form approximate Poisson process with rate rho(u). Maximum smooth gap grows as 1/rho(u) ~ u^u (super-polynomial). Quantifies L[1/2] barrier: sieve must cross increasingly rare smooth intervals. | Proven | v12_riemann_deep2_results.md |
| RMT-SIEVE | Sieve Matrix RMT Class | Sieve matrix eigenvalue spacing is intermediate between GOE and Poisson. Exhibits partial level repulsion. Belongs to no known RMT universality class. | Verified | v12_riemann_deep2_results.md |

### Millennium Prize Connections (Medium)

| ID | Name | Statement | Status | Source |
|----|------|-----------|--------|--------|
| T-mill-1 | Circuit Asymmetry | Multiplication requires O(n^2) gates; best known deterministic factoring circuit requires O(n^2*2^{n/2}) gates. Empirical ratio grows as ~2^n. Natural proofs barrier blocks proving super-polynomial lower bounds. | Verified | v12_millennium_results.md |
| T-mill-4 | Short Compositeness Proofs | Miller-Rabin witnesses provide O(log log N)-bit proofs of compositeness, exponentially shorter than exhibiting a factor (Theta(n/2) bits). MR witnesses are zero-knowledge for factoring. | Proven | v12_millennium_results.md |
| T-mill-5 | Factoring Uniformity | Factoring difficulty has low variance (CV=0.21) across random balanced semiprimes. Worst/avg ratio = 1.6x. Consistent with worst-case to average-case reduction existing. | Verified | v12_millennium_results.md |
| T124 | Selmer-Factoring Partial Non-Circularity | For E_N: y^2=x^3-Nx, 2-Selmer group satisfies \|Sel_2\| <= 2^(omega(N)+2). This bound is NON-CIRCULAR (computable without factoring) but only reveals omega(N), not factors. Computing exact Selmer group requires factoring. | Proven | v12_millennium2_results.md |
| T129 | Berggren Gauge Curvature | Berggren group has nonzero curvature: \|\|ABA^{-1}B^{-1}-I\|\|_F = 401.99. The connection on the tree is NOT FLAT -- parallel transport around loops picks up holonomy. This non-flatness is the geometric obstruction to global factoring shortcuts via the Berggren tree. | Proven | v12_millennium2_results.md |
| T130 | Sieve RG Flow -- No Phase Transition | Sieve yield Y(B) follows Dickman scaling. Beta function dY/d(logB) is positive and decreasing with NO zero (no fixed point/phase transition). Unlike Yang-Mills asymptotic freedom. Anomalous dimension converges to ~0.59. Absence of phase transition explains why there is no shortcut scale. | Proven | v12_millennium2_results.md |
| T131 | Prime Distribution Power Spectrum | Power spectrum of pi(x)-li(x) scales as k^{-1.70}, close to Kolmogorov K41 exponent -5/3 and RH prediction -2. Under RH, exponent should approach -2 for large x. Deviation from -2 consistent with higher zeta zeros. | Verified | v12_millennium2_results.md |
| T132 | Thermal Distribution of Smooth Relations | SIQS smooth relation 'actions' S=log\|Q(x)\|/log(B) follow approximate Boltzmann distribution with beta ~ -0.66. Smooth relations are thermal fluctuations, NOT instantons. No topological shortcuts exist. | Verified | v12_millennium2_results.md |
| T118 | PRG Structural Weakness | BBS (x^2 mod N) passes all randomness tests. Tree-mod-N has lag-3 autocorrelation 0.71 due to deterministic c_child ~ 4*c_parent. Berggren tree traversal leaks residue structure. | Verified | v12_millennium2_results.md |

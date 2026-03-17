# P vs NP Investigation Through the Lens of Integer Factoring

**Date**: 2026-03-15
**Companion experiments**: `v3_pvsnp_experiments.py`

---

## Track 1: Why Is Factoring Hard? (Evidence for P != NP)

### 1.1 The Three Barriers to P != NP Proofs

Any proof that P != NP must overcome three fundamental barriers. Each represents a class of proof techniques that provably cannot separate P from NP.

**Barrier 1: Relativization (Baker-Gill-Solovay 1975)**

A proof "relativizes" if it works unchanged when both P and NP are given access to an oracle. Baker, Gill, and Solovay showed:
- There exists an oracle A such that P^A = NP^A (oracle makes everything easy).
- There exists an oracle B such that P^B != NP^B (oracle makes things hard).

Since relativizing proofs would have to give the same answer in both worlds, no relativizing argument can resolve P vs NP. Most classical techniques in complexity theory (simulation, diagonalization) relativize. This kills all "purely structural" arguments about Turing machines.

**Barrier 2: Natural Proofs (Razborov-Rudich 1997)**

A "natural proof" of a circuit lower bound has two properties:
1. **Constructivity**: It identifies a property that can be checked in polynomial time.
2. **Largeness**: The property holds for a random function with non-negligible probability.

Razborov and Rudich proved: if one-way functions exist (a standard cryptographic assumption), then no natural proof can show super-polynomial circuit lower bounds. Since P != NP implies one-way functions exist, natural proofs are self-defeating — they require the negation of what they try to prove. Most combinatorial lower bound techniques (random restrictions, Hastad's switching lemma) produce natural proofs.

**Barrier 3: Algebrization (Aaronson-Wigderson 2009)**

An extension of relativization. A proof "algebrizes" if it holds when the oracle is replaced by a low-degree algebraic extension. Aaronson and Wigderson showed that P != NP cannot be proved by any technique that algebrizes. This kills more sophisticated approaches like arithmetization (used in IP = PSPACE) and the PCP theorem proof technique.

**What survives?** Very few proof strategies survive all three barriers simultaneously. Geometric Complexity Theory (GCT) is specifically designed to avoid them. So are certain algebraic geometry approaches. But no concrete P != NP proof candidate has yet been constructed.

### 1.2 What Makes Factoring Specifically Hard?

Factoring N = p * q into its prime factors is hard for reasons that are distinct from generic NP-hardness:

**The multiplicative structure of Z/NZ hides its additive decomposition.**

When we compute N = p * q, we destroy information about p and q individually. The ring Z/NZ is isomorphic to Z/pZ x Z/qZ (by CRT), but recovering this decomposition from Z/NZ requires finding p or q. The isomorphism exists but is computationally hidden.

**No known algebraic shortcut links N's ring structure to its factors.**

The factoring problem has deep structure:
- The group (Z/NZ)* has order phi(N) = (p-1)(q-1). If you knew phi(N), you could factor N trivially. But computing phi(N) is as hard as factoring.
- Quadratic residues mod N depend on both p and q independently (by CRT). This is why QS/GNFS work — they exploit quadratic residues. But finding smooth quadratic residues requires searching exponentially many candidates.
- The discrete log in (Z/NZ)* would give factoring, but DLP is also believed hard.

**The "information bottleneck" of factoring:**

N contains exactly log2(N) bits. The factors p, q together contain the same log2(N) bits. So factoring is NOT information-theoretically hard — the answer is fully determined by the input. The hardness is purely computational: we know the answer exists, but finding it requires (we believe) super-polynomial time.

**Why sub-exponential but not polynomial?**

The L-notation complexity L_N[1/3, c] of GNFS is rigorously understood heuristically:
- The sieve finds integers that are "smooth" (have only small prime factors).
- The probability that a random integer near N^(1/d) is B-smooth is u^(-u) where u = log(N^(1/d)) / log(B).
- Optimizing the tradeoff between sieve range and factor base size gives the L[1/3] exponent.
- There is no known way to avoid this smoothness probability bottleneck.

The key insight: **factoring is hard because smooth numbers are rare, and we have no way to generate them deterministically.** Any algorithm that finds x^2 = y^2 (mod N) must, at some point, find smooth values — and the distribution of smooth numbers is governed by analytic number theory (the Dickman rho function) in a way that appears fundamental.

### 1.3 Hard-Core Instances (Experiment 1)

See `v3_pvsnp_experiments.py`, Experiment 1. We generate many random semiprimes at each digit count and measure the distribution of factoring times. Key questions:
- Is the distribution unimodal or bimodal? (Bimodal would suggest a "hard core".)
- What is the variance? (High variance suggests instance-specific difficulty.)
- Do hard instances share structural properties?

**Hypothesis**: Factoring time variance is low for trial division (determined by smallest factor), moderate for Pollard rho (determined by sqrt of smallest factor), and high for SIQS (determined by smoothness properties of the number). The "hard core" for SIQS consists of numbers where the polynomial values are unusually non-smooth.

---

## Track 2: Could P = NP? (Devil's Advocate)

### 2.1 What Would a P = NP Proof Look Like?

If P = NP, there exists a polynomial-time algorithm for SAT (and hence all NP problems). What paradigm could achieve this?

**Candidate 1: Algebraic algorithms.** If SAT can be encoded as a system of polynomial equations over a finite field, and if there is a polynomial-time method to find solutions (beyond Grobner bases, which are exponential in the worst case), this would give P = NP.

**Candidate 2: Continuous relaxation.** Relax the Boolean constraint x_i in {0,1} to x_i in [0,1], solve the resulting convex/continuous optimization, then round. Linear programming relaxations (LP) are polynomial time, but the integrality gap for SAT is exponential. Could a cleverer relaxation (semidefinite programming? Sum-of-squares?) close the gap? The Lasserre hierarchy approaches this but requires exponential levels for hard instances.

**Candidate 3: Structural decomposition.** If every SAT instance has a polynomial-size "proof of structure" (tree decomposition, backdoor variables), and this structure can be found in polynomial time, then SAT is in P. Courcelle's theorem gives FPT algorithms for bounded treewidth, but general SAT has unbounded treewidth.

**Candidate 4: The algorithm already exists but we can't prove it terminates.** Some heuristic algorithms (e.g., DPLL with certain branching rules) might be polynomial on ALL instances, but proving this requires solving P vs NP first (a circularity). The "optimal algorithm" of Levin runs all programs in parallel — it's polynomial if a polynomial algorithm exists, but the constant is astronomical.

**Assessment**: None of these candidates is close to working. The consensus that P != NP is based on decades of failure to find polynomial algorithms for any NP-complete problem, plus the three barriers suggesting that proof of P != NP requires fundamentally new ideas.

### 2.2 The Derandomization Connection

**Fact**: Factoring is in BPP (randomized polynomial time) via the Adleman-Huang algorithm (1992) for primality, plus the Miller-Rabin test, plus the structure of the factoring problem itself.

Wait — this is imprecise. Let me be more careful:
- **Primality testing** is in P (AKS 2002).
- **Factoring** is NOT known to be in BPP. Factoring is in co-NP (the factors serve as a certificate that N is composite) and in NP (the factors serve as a certificate).
- **Factoring is in BQP** (Shor 1994) — quantum polynomial time.

The derandomization hypothesis P = BPP (widely believed, follows from strong enough circuit lower bounds) would NOT place factoring in P, because factoring is not known to be in BPP in the first place.

However, if factoring IS in BPP (which would follow from a randomized polynomial factoring algorithm), then P = BPP would imply factoring is in P, breaking RSA. No such randomized algorithm is known.

**The quantum connection**: Shor's algorithm shows factoring is in BQP. If BQP = BPP (which would mean quantum computers offer no speedup), then factoring is in BPP and hence in P (assuming derandomization). But BQP = BPP is considered very unlikely.

### 2.3 Structural Predictors of Factoring Difficulty (Experiment 2)

See `v3_pvsnp_experiments.py`, Experiment 2. We test whether factoring time correlates with:
- Bit pattern of N (Hamming weight, longest run of 0s/1s)
- Digit sum of N (mod 9, etc.)
- N mod small primes (2, 3, 5, 7, 11, 13)
- Size of smallest factor (for balanced semiprimes, this is ~sqrt(N))
- Smoothness of p-1 and q-1 (relevant for Pollard p-1 method)

**Hypothesis**: For balanced semiprimes factored by SIQS, none of these simple structural properties predict factoring time well. The difficulty is determined by the smoothness landscape of the quadratic polynomial, which depends on the interaction between N and the factor base in a way that is not predictable from N alone.

---

## Track 3: Novel Approaches to P vs NP

### 3.1 Geometric Complexity Theory (GCT)

GCT, developed by Mulmuley and Sohoni, attempts to separate P from NP (actually VP from VNP, the algebraic analogs) using:
1. The permanent vs determinant problem (Valiant's conjecture).
2. Representation theory of GL_n and the symmetric group S_n.
3. Multiplicity obstructions in Kronecker coefficients.

**The permanent-determinant connection to factoring:**

The permanent of a matrix is #P-complete to compute (Valiant 1979). The determinant is in P. If perm(A) cannot be expressed as det(B) for any polynomially-larger matrix B, this separates VP from VNP, giving strong evidence for P != NP.

Factoring is not directly related to permanent vs determinant. However, the representation-theoretic machinery of GCT could potentially be adapted to study the complexity of integer factoring specifically. The multiplicative structure of Z/NZ has natural representations that might yield orbit separation arguments.

**Current status**: GCT has not yet produced any new lower bounds. The "multiplicity obstruction" approach was shown to be insufficient by Burgisser, Ikenmeyer, and Panova (2019). GCT remains a promising framework but needs new ideas.

### 3.2 Algebraic Natural Proofs

Grochow and Pitassi (2014) extended the Razborov-Rudich barrier to the algebraic setting. They showed that "algebraic natural proofs" face similar barriers to Boolean natural proofs. However, the barrier is weaker: it requires algebraic pseudorandom functions, which are a stronger assumption than one-way functions.

**Relevance to factoring**: If factoring is hard, then certain algebraic pseudorandom constructions exist (based on the Blum-Blum-Shub generator). This creates a circular dependency similar to the Boolean case: proving factoring is hard requires avoiding algebraic natural proofs, but algebraic natural proofs are blocked by factoring being hard.

### 3.3 Factoring as a Complexity Testbed

Factoring occupies a unique position in complexity theory:
- NOT known to be NP-complete (and believed not to be, since NP-completeness of factoring would collapse the polynomial hierarchy).
- NOT known to be in P.
- IN co-NP intersection NP (factors certify both compositeness and the factorization).
- IN BQP (Shor's algorithm).
- The decision version is in UP (unique witness, since factorization is unique).

This makes factoring the ideal "canary in the coal mine" for complexity separations:
- If factoring is proved to be in P, it suggests P might equal NP (or at least that the frontier is much broader than believed).
- If factoring is proved to require super-polynomial time, it gives strong evidence for P != NP (though it wouldn't prove it, since factoring is not NP-complete).
- If someone proves NP-completeness of factoring, the polynomial hierarchy collapses to the second level (since factoring is in NP intersection co-NP).

---

## Track 4: Experimental Science

### 4.1 SAT-Factoring Reduction (Experiment 3)

We encode N = p * q as a Boolean satisfiability instance where the variables represent the bits of p and q. For an n-bit semiprime:
- Variables: 2 * (n/2) = n bits for the two factors.
- Multiplication is a circuit of AND/XOR gates, producing O(n^2) clauses when converted to CNF.
- The resulting SAT instance has O(n) variables and O(n^2) clauses.

See `v3_pvsnp_experiments.py`, Experiment 3. We construct these SAT instances and analyze their size and structure (without running a SAT solver, which would require installing one).

**Key observation**: The SAT encoding of factoring has very specific structure — it's a system of polynomial equations over GF(2), not a random SAT instance. This structure is why GNFS/SIQS outperform generic SAT solvers: they exploit the number-theoretic structure that the SAT encoding destroys.

### 4.2 Scaling Laws (Experiment 4)

We measure factoring time vs digit count for:
- Trial division: O(sqrt(N)) = O(10^(d/2)), exponential in digits.
- Pollard rho (Brent variant): O(N^(1/4)) = O(10^(d/4)), exponential but better constant.
- SIQS: L[1/2, 1] heuristically, sub-exponential.

We fit curves to the empirical data and check:
- Does trial division match the predicted exponential?
- Does Pollard rho match O(N^(1/4))?
- Does SIQS match L[1/2, c] for some constant c?
- Are there phase transitions (sudden jumps in difficulty)?

See `v3_pvsnp_experiments.py`, Experiment 4.

### 4.3 Randomness in Factoring (Experiment 5)

SIQS uses randomness in:
1. Choosing the 'a' coefficient for polynomials.
2. Choosing the starting sieve position.
3. The order of relation collection.

GNFS uses randomness in:
1. Polynomial selection (searching over leading coefficients).
2. Sieve region selection.
3. Large prime combining order.

**Question**: How much does randomness help? We test this by running SIQS with different random seeds and measuring the variance in factoring time.

See `v3_pvsnp_experiments.py`, Experiment 5.

**Theoretical connection**: If factoring can be derandomized (made fully deterministic with only polynomial overhead), this would mean factoring is in P if and only if it's in BPP. Since P = BPP is widely believed, this would mean the randomness in SIQS/GNFS is inessential — a deterministic polynomial algorithm exists if and only if a randomized one does.

---

## Synthesis: What We Learn

### The Central Mystery

Factoring sits at the nexus of three deep questions:
1. **P vs NP**: Is factoring hard because P != NP, or is it merely hard because we haven't found the right algorithm?
2. **Quantum vs Classical**: BQP contains factoring (Shor). Does BQP contain NP? Almost certainly not (relative to a random oracle). So factoring's quantum easiness does not imply NP's quantum easiness.
3. **Structure vs Hardness**: Factoring has enormous algebraic structure (ring theory, quadratic forms, algebraic number fields). SIQS and GNFS exploit this structure to achieve sub-exponential time. Could more structure exploitation reach polynomial time?

### The Experimental Evidence

Our experiments (in the companion script) test:
1. **Distribution of hardness**: Is there a "hard core" of factoring instances? (Track 1)
2. **Structural predictors**: Can we predict factoring difficulty from N's properties? (Track 2)
3. **SAT reduction size**: How large is the SAT encoding of factoring? (Track 4)
4. **Scaling laws**: Do empirical curves match theoretical predictions? (Track 4)
5. **Randomness sensitivity**: How much does randomness affect factoring time? (Track 4)

### Honest Assessment

**What factoring teaches us about P vs NP**: Not much directly, because factoring is almost certainly not NP-complete. But it teaches us about the boundary between P and NP — the twilight zone of problems that are "hard but not the hardest." If we cannot put factoring in P despite 40+ years of effort and deep algebraic structure, this is strong circumstantial evidence that NP-complete problems (which have less structure) are also not in P.

**What P vs NP teaches us about factoring**: If P != NP, factoring could still be in P (since it's not NP-complete). But the techniques that would prove P != NP (circuit lower bounds, proof complexity) might also prove factoring requires super-polynomial time. The barriers (relativization, natural proofs, algebrization) apply equally to factoring-specific lower bounds.

**The bottom line**: We have no proof that factoring is hard. We have no proof that it's easy. We have strong heuristic evidence (the L[1/3] GNFS bound, 40 years without improvement) that classical factoring requires super-polynomial time. Shor's algorithm shows this hardness is not fundamental — it's specific to the classical computational model. This makes factoring one of the most important open problems in mathematics and computer science.

---

**Files**:
- This analysis: `/home/raver1975/factor/p_vs_np_investigation.md`
- Experiments: `/home/raver1975/factor/v3_pvsnp_experiments.py`
- Prior B3-SAT analysis: `/home/raver1975/factor/b3_sat_deep_analysis.md`

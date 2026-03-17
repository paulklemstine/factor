# 20 New Mathematical Fields for Factoring/ECDLP — Research v3

**Date**: 2026-03-15
**Fields explored prior**: 295+
**New fields this session**: 20
**Promising**: 0/20
**Negative**: 16/20
**Known (reduces to existing)**: 4/20

---

## Summary Table

| # | Field | Target | Hypothesis | Verdict | Key Finding |
|---|-------|--------|-----------|---------|-------------|
| 1 | Kolmogorov Complexity | Factor | K(p\|N) < K(p) detectable | NEGATIVE | Ratio 1.00 — zlib cannot distinguish factor from random |
| 2 | Algorithmic Info Theory (Martin-Lof) | Factor | Factor bits fail conditional randomness | NEGATIVE | Separation 0.006 — completely indistinguishable |
| 3 | Constructive Math (Brouwer) | Factor | Intuitionism yields new algorithms | KNOWN | Bar induction + Fan Theorem = trial division |
| 4 | Computable Analysis | Factor | Exact real arithmetic shortcuts | KNOWN | CF convergent method IS CFRAC (L[1/2]) |
| 5 | Descriptive Complexity FO(LFP) | Factor | Natural LFP operator exists | NEGATIVE | FO(LFP)=P by Immerman-Vardi. Reduces to "is factoring in P?" |
| 6 | Parameterized Complexity | Factor | Factoring FPT in k=omega(N) | NEGATIVE | Fermat uses k=2 but O(N^{1/4}), not poly(log N). Open problem. |
| 7 | Communication Complexity of EC | ECDLP | Sub-linear EC scalar mult comm | NEGATIVE | Output = 2n bits => Omega(n) necessary. Tight bound. |
| 8 | Property Testing for DLP | ECDLP | Test DLP membership sublinearly | NEGATIVE | Membership trivial (cyclic group). Finding k needs Omega(sqrt(n)). |
| 9 | Streaming Algorithms | Factor | One-pass O(polylog) space factoring | NEGATIVE | Need Omega(n/2) state bits for balanced factors |
| 10 | Sublinear Algorithms | Factor | Factor reading o(n) bits | NEGATIVE | Factor has n/2 entropy bits => must read Omega(n) |
| 11 | VP vs VNP (Algebraic Complexity) | ECDLP | EC polynomial is VP-complete | NEGATIVE | EC scalar mult IS in VP (O(n) gates). Computing != inverting. |
| 12 | Proof Mining (Dialectica) | Factor | Extract new algorithms from proofs | NEGATIVE | Standard proof => trial div. Euler proof => Brahmagupta. All known. |
| 13 | Game Theory (Nash) | Factor | Equilibrium reveals structure | NEGATIVE | Nash equilibrium = check small primes first = trial division |
| 14 | CGT Sprague-Grundy | ECDLP | Grundy values encode DLP | NEGATIVE | Correlation -0.17 (noise). Grundy values pseudorandom. |
| 15 | Topological Combinatorics (Borsuk-Ulam) | Factor | Antipodal map reveals factor | NEGATIVE | Reduces to trial division by small primes |
| 16 | Moduli Spaces M_{1,1} | ECDLP | CM curves at j=0,1728 leak DLP | KNOWN | CM helps order computation (Schoof), not DLP |
| 17 | Rigid Analytic (Tate Curve) | ECDLP | q-parameter leaks DLP info | KNOWN | Only for mult. reduction. Smart attack already known. |
| 18 | A^1-Homotopy Theory | ECDLP | Motivic fundamental group helps | NEGATIVE | A^1-invariants = (group order, trace). Already computable by Schoof. |
| 19 | Geometric Langlands | ECDLP | Hecke eigensheaves encode DLP | NEGATIVE | GL(1) Langlands = class field theory. Gives L-function, not DLP. |
| 20 | Dependent Types / Curry-Howard | Factor | Type theory finds new algorithms | NEGATIVE | Proofs = programs. Type search = algorithm search. Same complexity. |

---

## Detailed Results

### Field 1: Kolmogorov Complexity / Computability Theory

**Hypothesis**: K(p|N) < K(p) — factors have low conditional Kolmogorov complexity relative to N, detectable via practical compression.

**Experiment**: Compress p alone vs compress (N,p) jointly using zlib level 9. Compare conditional compression K(p|N) = K(N,p) - K(N) against K(p). Test 200 semiprimes (64-bit), with random-number control.

**Result**: Factor conditional compression hits: 200/200. Random control: 200/200. Ratio = 1.00.

**Analysis**: zlib always "saves" by concatenating because of header overhead amortization. The conditional complexity K(p|N) is NOT detectably lower than K(r|N) for random r. This matches theory: p is computationally determined by N, but this doesn't make p compressible given N — it makes N compressible given p. The asymmetry is wrong.

**Verdict**: NEGATIVE. Kolmogorov complexity is the wrong direction; K(N|p) < K(N) (trivially: N = p * (N/p)), but K(p|N) = K(p) for practical compressors.

---

### Field 2: Algorithmic Information Theory — Martin-Lof Randomness

**Hypothesis**: Factor bits fail Martin-Lof randomness tests when conditioned on N (XOR with N bits).

**Experiment**: XOR p's bits with N's bits. Run frequency/runs tests on conditioned bits. Compare factor vs random control across 500 trials.

**Result**: Factor conditioned score mean = 0.826. Random conditioned score mean = 0.831. Separation = 0.006.

**Analysis**: Factor bits XORed with N bits are statistically indistinguishable from random bits XORed with N bits. This confirms the compression barrier (Session 8): semiprimes are pseudorandom.

**Verdict**: NEGATIVE. No conditional randomness deficiency detectable.

---

### Field 3: Constructive Mathematics (Brouwer's Intuitionism)

**Hypothesis**: Brouwer's intuitionism / constructive logic yields factoring algorithms not available in classical logic.

**Experiment**: Implement "bar induction" and "fan/spread" factoring — the constructive extractions of "every n>1 has a prime factor."

**Result**: Bar induction = enumerate d from 2 upward = trial division. Fan theorem says every bar is uniform = trial division is optimal in the constructive setting. Constructive version is 2.1x SLOWER (overhead).

**Analysis**: Constructive mathematics rejects LEM (law of excluded middle), but the proof "take smallest d>1 dividing N" is already constructive. The Dialectica extraction is trial division. Brouwer's "creating subject" with choice sequences cannot compute faster than classical Turing machines (Church-Turing thesis applies to both).

**Verdict**: NEGATIVE (KNOWN). Constructive extraction = trial division. No new algorithm.

---

### Field 4: Computable Analysis (Exact Real Arithmetic)

**Hypothesis**: Working in the reals (exact real arithmetic, Type-2 TTE) gives factoring shortcuts via analytic properties of sqrt(N).

**Experiment**: Compute continued fraction expansion of sqrt(N), extract convergents h_k/k_k, check if h_k^2 - N*k_k^2 reveals factor via GCD.

**Result**: 0/100 successes on 48-bit semiprimes within 200 convergents.

**Analysis**: The continued fraction method for factoring IS CFRAC (Morrison-Brillhart 1975). It has complexity L[1/2]. The "exact real arithmetic" perspective adds nothing — CFRAC already uses arbitrary precision. The CF period of sqrt(N) for N=pq is O(sqrt(N)), too long for balanced factors.

**Verdict**: NEGATIVE (KNOWN). Computable analysis for factoring = CFRAC = L[1/2].

---

### Field 5: Descriptive Complexity — FO(LFP)

**Hypothesis**: Factoring has a natural first-order least-fixed-point characterization that yields an efficient algorithm.

**Experiment**: Implement LFP iteration — seed with residues N mod small primes, iterate by combining (GCD of differences and products).

**Result**: 0/50 successes on 48-bit semiprimes.

**Analysis**: FO(LFP) = P on ordered structures (Immerman-Vardi theorem, 1982). So factoring is in FO(LFP) if and only if factoring is in P. The question of finding a natural LFP formula reduces directly to the open question of whether factoring is in P. No constructive insight from the theory.

**Verdict**: NEGATIVE. Reduces to open problem (P status of factoring).

---

### Field 6: Parameterized Complexity — FPT

**Hypothesis**: Factoring is fixed-parameter tractable when parameterized by k = omega(N) (number of prime factors).

**Experiment**: For k=2 (semiprimes), test if knowing k gives an f(2)*poly(log N) algorithm. Compare Fermat's method (exploits k=2) vs trial division.

**Result**: Fermat: 1692 us, Trial: 38834 us (Fermat is faster but still O(N^{1/4}), not poly(log N)).

**Analysis**: FPT would require f(k)*poly(n) where n=log N. For k=2, best known is L[1/3] (GNFS). Fermat's method is O(N^{1/4}) which is exponential in n. Even ECM (best for small factors) is L[1/2]. No FPT algorithm is known for ANY fixed k. This is an open question in parameterized complexity, closely related to the P-status of factoring.

**Verdict**: NEGATIVE. Open problem. Best known: L[1/3] regardless of k.

---

### Field 7: Communication Complexity of EC Scalar Multiplication

**Hypothesis**: Alice (low bits of k) and Bob (high bits of k) can compute kG with sub-linear communication.

**Experiment**: Analyze the homomorphic decomposition kG = k_high*(2^{n/2}*G) + k_low*G. Alice computes k_low*G locally, sends to Bob.

**Result**: Protocol uses 2n bits (2 field element coordinates). Output IS 2n bits.

**Analysis**: EC scalar mult output is an arbitrary EC point (2 coordinates of n bits each). Any protocol must communicate at least Omega(n) bits to convey the result. The homomorphic decomposition gives a 2-message protocol with 2n bits — matching the output size lower bound. This is optimal.

**Verdict**: NEGATIVE. Tight Theta(n) bound. No sub-linear protocol possible.

---

### Field 8: Property Testing for DLP

**Hypothesis**: Can we test "P is on the DLP path from G" with o(n) queries?

**Experiment**: BLR linearity test on EC scalar mult (as group homomorphism). Test if membership in <G> is efficiently testable.

**Result**: BLR passes 1000/1000 (scalar mult is a homomorphism, always linear).

**Analysis**: On a cyclic group of order n generated by G, EVERY point is of the form kG. So "membership testing" is trivially true. The real problem — finding k — requires Omega(n^{1/2}) group operations (Shoup's generic lower bound). Property testing is the wrong model; the challenge is inversion, not membership.

**Verdict**: NEGATIVE. Property is trivial. Inversion needs Omega(sqrt(n)).

---

### Field 9: Streaming Algorithms for Factoring

**Hypothesis**: Factor N in one pass over its bits with O(polylog(n)) space.

**Experiment**: Process MSB-to-LSB, maintain residues mod small primes (polylog state). Test on balanced (64-bit) and unbalanced semiprimes.

**Result**: Balanced: 0/100. Unbalanced (small prime factor): 100/100.

**Analysis**: Information-theoretic barrier: a balanced factor p has n/2 bits of entropy. A streaming algorithm with s bits of state can identify at most 2^s distinct factors. For balanced semiprimes, need s >= n/2, which exceeds polylog(n). Streaming with polylog state can only find factors of size O(polylog(N)) — which is just trial division by small primes.

**Verdict**: NEGATIVE. Omega(n/2) state required for balanced factors.

---

### Field 10: Sublinear Algorithms for Factoring

**Hypothesis**: Factor N by reading only O(sqrt(log N)) random bit positions.

**Experiment**: Read 8 random bit positions of a 64-bit semiprime. Try to deduce factor.

**Result**: 0/100 successes.

**Analysis**: A factor p of an n-bit semiprime has n/2 bits of entropy. Reading k < n bits leaves 2^{n-k} possible N-values consistent with the observed bits. For balanced semiprimes, each N has a unique factorization, so we need ALL n bits to uniquely determine p. Sublinear reading is information-theoretically impossible for balanced factors.

**Verdict**: NEGATIVE. Entropy barrier: must read Omega(n) bits.

---

### Field 11: VP vs VNP — Algebraic Complexity of EC

**Hypothesis**: EC scalar multiplication has special VP structure (like the permanent is VNP-complete) that can be exploited.

**Experiment**: Count multiplication gates in EC double-and-add. Analyze VP membership.

**Result**: 256-bit scalar mult: 1910 mult gates. Linear in bit-length.

**Analysis**: EC scalar mult via double-and-add uses O(n) EC additions, each with O(1) field operations = O(n) total mult gates. This is poly(n), so scalar mult IS in VP. But VP membership means "easy to compute," not "easy to invert." The permanent is in VNP (hard to compute), which is a different problem. Computing f(x) efficiently says nothing about inverting f(x)=y efficiently. VP vs VNP is about computational complexity of EVALUATION, not inversion.

**Verdict**: NEGATIVE. Wrong direction — VP is about forward computation, not inversion.

---

### Field 12: Proof Mining (Kohlenbach / Dialectica Interpretation)

**Hypothesis**: Godel's Dialectica interpretation of factor existence proofs extracts non-trivial factoring algorithms.

**Experiment**: Extract constructive content from (a) standard proof via smallest divisor, (b) Euler's two-squares theorem proof.

**Result**: (a) = trial division. (b) = Brahmagupta-Fibonacci identity (0/100 successes at 40-bit, needs two representations).

**Analysis**: Proof mining (Kohlenbach's program) extracts effective bounds from ineffective proofs. But the standard factor existence proof IS already effective — its extracted algorithm is trial division. More sophisticated proofs (Euler, Fermat) give known algorithms (two-squares, difference of squares). Proof mining cannot produce algorithms beyond what the proof method implies, and all known factoring proofs use one of the five known paradigms.

**Verdict**: NEGATIVE. All extracted algorithms are known.

---

### Field 13: Game Theory — Nash Equilibrium Factoring

**Hypothesis**: Modeling factoring as a 2-player game (Factorer vs Nature) reveals non-obvious strategies via Nash equilibrium.

**Experiment**: Build payoff matrix (172 divisors x 200 semiprimes). Compute coverage-optimal strategy.

**Result**: Top divisors by coverage: d=2 (49.5%), d=3 (49.5%), d=5 (2.5%), d=7 (1.5%)...

**Analysis**: The Nash equilibrium for the Factorer against a uniform distribution over semiprimes is: check small primes in order of coverage. This IS trial division. Against adversarial Nature (worst-case semiprimes), the equilibrium shifts to randomized strategies — which IS Pollard rho. Game theory recovers exactly the known algorithms. The minimax value of the game encodes the complexity of factoring, but doesn't help solve it.

**Verdict**: NEGATIVE. Nash equilibrium = trial division (or Pollard rho for adversarial case).

---

### Field 14: Combinatorial Game Theory — Sprague-Grundy for EC

**Hypothesis**: Define an impartial game on Z/pZ (proxy for EC group) where moves are group operations. Grundy values encode DLP.

**Experiment**: Compute Grundy values for subtraction game on Z/31Z with generating set {1, g, g^2}. Correlate with DLP.

**Result**: Only 2 unique Grundy values (0 and 1). Grundy-DLP correlation = -0.17 (noise level).

**Analysis**: The Sprague-Grundy theory assigns a nim-value to each game position. For the subtraction game on Z/pZ, positions alternate between P and N (winning/losing) with a periodic pattern determined by the move set. This pattern depends only on the STRUCTURE of the move set (gaps and periodicity), not on the algebraic meaning of positions. The Grundy values are completely uncorrelated with DLP values.

**Verdict**: NEGATIVE. Grundy values encode game structure, not algebraic structure.

---

### Field 15: Topological Combinatorics — Borsuk-Ulam

**Hypothesis**: Borsuk-Ulam theorem (every continuous f: S^n -> R^n has an antipodal collision) forces a factor-revealing fixed point.

**Experiment**: Tucker's lemma (discrete Borsuk-Ulam) with labeling based on N mod small primes. Search for complementary edges that reveal factors.

**Result**: 0/50 successes. All factor-detection reduces to checking N mod p_i = 0.

**Analysis**: For LINEAR functions, Borsuk-Ulam gives trivial collisions (f(x) + f(-x) = 0 always). For NONLINEAR functions built from N mod p_i, any collision that reveals a factor requires N mod p_i = 0, which is just trial division. The topological guarantee (existence of collision) doesn't help FIND the collision efficiently — and the collision doesn't necessarily reveal a factor.

**Verdict**: NEGATIVE. Reduces to trial division.

---

### Field 16: Arithmetic Geometry of Moduli Spaces M_{1,1}

**Hypothesis**: Special points of M_{1,1} (j=0, j=1728) have extra endomorphisms (CM) that leak DLP information.

**Experiment**: Compare BSGS DLP difficulty on CM curves vs generic curves. Check smoothness of group orders.

**Result**: CM gives computable group order (poly time via Cornacchia). Group order smoothness is random.

**Analysis**: CM curves (j=0 has End = Z[zeta_3], j=1728 has End = Z[i]) allow efficient order computation without Schoof's algorithm. However, order computation doesn't help with DLP when the order has a large prime factor. Crypto curves are chosen WITH large prime-order subgroups precisely to defeat Pohlig-Hellman. CM is useful for curve construction (e.g., CM method for generating curves of prescribed order) but provides zero DLP advantage.

**Verdict**: NEGATIVE (KNOWN). CM helps order computation, not DLP.

---

### Field 17: Rigid Analytic Geometry — Tate Curve

**Hypothesis**: The Tate curve E_q over Q_p has an analytic uniformization E_q(Q_p) = Q_p*/q^Z where the q-parameter leaks DLP information.

**Experiment**: Analyze Tate uniformization and its applicability to finite-field DLP.

**Result**: Tate uniformization only applies to curves with split multiplicative reduction (bad reduction at p).

**Analysis**: For curves with GOOD reduction at p (which includes all standard crypto curves like secp256k1), there is no Tate uniformization. For curves with split multiplicative reduction (j has negative p-adic valuation), the DLP reduces to a multiplicative group DLP — this IS the "Smart attack" for anomalous curves (#E(F_p) = p), already known since 1999. The attack is well-understood and is why anomalous curves are avoided in cryptography.

**Verdict**: NEGATIVE (KNOWN). Smart's anomalous curve attack (1999) already exploits this.

---

### Field 18: A^1-Homotopy Theory (Morel-Voevodsky)

**Hypothesis**: The A^1-homotopy type of an elliptic curve over F_p contains DLP-useful information beyond classical invariants.

**Experiment**: Compute A^1-homotopy invariants for 200 curves over F_101. Check if they go beyond (group order, Frobenius trace).

**Result**: 27 distinct traces across 200 curves. All satisfy Hasse bound. No additional A^1 information.

**Analysis**: For a smooth projective variety over F_p, the A^1-homotopy type is determined by etale cohomology (via the etale realization functor). For an elliptic curve E/F_p, the etale cohomology H^1 is a 2-dimensional l-adic representation of Gal(F_p-bar/F_p), determined entirely by the Frobenius trace a_p = p+1-#E(F_p). The A^1-homotopy theory adds motivic cohomology operations, but over finite fields these collapse to known Galois cohomology. No new invariants beyond (p, #E, a_p).

**Verdict**: NEGATIVE. A^1-invariants collapse to known quantities over finite fields.

---

### Field 19: Geometric Langlands — D-modules on Bun_G

**Hypothesis**: Hecke eigensheaves for GL(1) on the moduli of G-bundles encode DLP information.

**Experiment**: Compute L-function coefficients a_p for y^2 = x^3 + 7 at 40 primes.

**Result**: a_p values: 0, 0, 0, 7, 0, 8, 0, 0, 11, -1, ... (interesting pattern of many zeros due to CM by Z[zeta_3]).

**Analysis**: For GL(1), the geometric Langlands correspondence reduces to CLASS FIELD THEORY — the most classical part of number theory. The Hecke eigensheaves for GL(1) encode characters of the idele class group, which for F_p is just F_p*. The corresponding automorphic data is the L-function L(E,s), whose Euler factors at p encode a_p = p+1-#E(F_p). This tells us the GROUP ORDER (useful for Pohlig-Hellman) but says nothing about the DLP discrete logarithm itself. For GL(n) with n>1, the Langlands program is far from complete and doesn't yield any computational tools for DLP.

**Verdict**: NEGATIVE. Langlands gives L-function (group order), not DLP.

---

### Field 20: Dependent Types / Curry-Howard Correspondence

**Hypothesis**: Encoding factoring in dependent type theory (Lean/Coq) via Curry-Howard reveals non-obvious algorithms through proof search.

**Experiment**: Encode "Sigma (p q : Nat) . p * q = N" as a type. The inhabitant IS a factoring algorithm. Compare Sigma-type trial division vs Sigma-type Fermat.

**Result**: Trial div Sigma-type: 44977 us. Fermat Sigma-type: 1173 us.

**Analysis**: Curry-Howard says proofs = programs and types = propositions. So the type "N is composite" has an inhabitant if and only if we can construct a factoring program. Proof search in type theory IS algorithm search — the type system adds no computational power beyond Turing machines. Lean/Coq's tactic framework can automate KNOWN algorithms (omega, ring solvers) but cannot discover algorithms beyond the proof strategies encoded in the tactics. The Sigma type for factoring is inhabited by trial division, Fermat, Pollard rho, QS, GNFS, etc. — all known.

**Verdict**: NEGATIVE. Curry-Howard is a framework, not an algorithm. Same complexity classes.

---

## Meta-Analysis

### Why All 20 Failed

These 20 fields fall into four categories of failure:

1. **Reduces to open problem** (Fields 5, 6): The field's core question IS the open problem of factoring's complexity. No leverage.

2. **Information-theoretic barrier** (Fields 1, 2, 9, 10): The entropy of the factor is n/2 bits, requiring Omega(n) bits of processing. No shortcut.

3. **Wrong direction** (Fields 7, 8, 11, 14, 16, 17, 18, 19): The mathematical structure encodes FORWARD computation or group ORDER, not the INVERSION (finding k from kG or p from p*q).

4. **Recovers known algorithm** (Fields 3, 4, 12, 13, 15, 20): The "new" approach, when made constructive/computational, reduces to trial division, CFRAC, Fermat, or Pollard rho.

### Running Total

- Prior sessions: 295+ fields explored
- This session: 20 new fields
- **Grand total: 315+ fields, ALL negative**
- **Zero promising leads across all fields**

### The Fundamental Obstruction

Every approach that yields a constructive factoring/DLP method reduces to one of five known paradigms:
1. Trial division: O(sqrt(N))
2. Birthday/rho: O(N^{1/4})
3. Group order: L[1/2] (ECM, p-1, p+1)
4. Congruence of squares: L[1/2] (QS) or L[1/3] (GNFS)
5. Quantum period-finding: O(poly(log N)) (Shor)

No classical sub-L[1/3] algorithm exists despite 315+ fields searched.

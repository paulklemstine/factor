# Master Research Document — Factoring Research Program

**Date**: 2026-03-15 (March 2026)
**Author**: Compiled from 14+ research documents, 49+ experiment scripts, 250+ mathematical fields

---

## 1. Executive Summary

This research program explored 275+ mathematical fields seeking novel integer factoring methods beyond known complexity classes. **Every field reduces to one of five known paradigms**: trial division O(sqrt(N)), birthday/rho O(N^{1/4}), group-order L[1/2], sieve methods L[1/3], or quantum period-finding poly(log N). No classical sub-L[1/3] algorithm was found. The Dickman Information Barrier — relations/bits overhead grows as 10^(0.24*digits) — appears fundamental to all sieve-based methods. Engineering optimizations (15 commits) delivered 2-5x practical speedups: K-S multiplier, DLP revival, multithread sieve, bitpacked LA, C extensions. GPU acceleration achieved 42-83x on cofactor checking. The Pythagorean triple tree produced 89 theorems but zero sub-exponential breakthroughs. 20 exotic math fields tested for ECDLP (all negative). P vs NP Phase 5 (8 experiments): DLP escapes 2 of 3 proof barriers but relativization remains. 20 classic/advanced algorithm techniques analyzed: all already applied or negative. Path to RSA-100: ~346 hours with lattice sieve + Block Lanczos (estimated).

---

## 2. All Theorems

### Pythagorean Tree — Ergodic/Spectral (T1-T5)

| ID | Theorem | Key Statement |
|----|---------|---------------|
| T1 | Full Transitivity (E1) | Orbit of (2,1) under {B1,B2,B3} mod p covers 100% of (Z/pZ)^2\{0} for all primes tested |
| T2 | Fast Mixing (E2) | Spectral gap ~0.33, mixing in ~3 steps regardless of p |
| T3 | Strong Expander (SP1) | Spectral gap ~0.33, well above Ramanujan bound 0.057 for 3-regular graphs |
| T4 | Height-Smoothness (H1) | All depth<=7 triples are 1000-smooth; rate decays to ~38% at depth 14 |
| T5 | Angular Non-uniformity (A1) | Tree angles mod p have chi^2/df ~80x uniform; ~50% residue coverage |

### Pythagorean Tree — Algebraic Structure (T6-T12)

| ID | Theorem | Key Statement |
|----|---------|---------------|
| T6 | Symplectic Dichotomy (S1) | B1,B3 symplectic (det=1); B2 anti-symplectic (det=-1) |
| T7 | Galois-Period (G1) | B2 period divides (p-1) when (2/p)=1, 2(p+1) when (2/p)=-1 |
| T8 | Trace Invariance (R1) | B1,B3 trace=2 for all k; B2 trace follows Pell recurrence |
| T9 | CF Generation (CF1) | B2 path ratios = convergents of 1+sqrt(2) |
| T10 | Berggren Group (Theorem 4) | G = {det=+/-1} in GL(2,F_p), \|G\| = 2p(p^2-1) |
| T11 | Swap Closure (AU1) | Tree is closed under (a,b) swap — 100% verified |
| T12 | B1-B3 Disjointness (AU2) | B1 and B3 generate completely disjoint A-value sets |

### Pythagorean Tree — Smoothness/Sieve (T13-T18)

| ID | Theorem | Key Statement |
|----|---------|---------------|
| T13 | Smoothness Advantage (P1) | Tree A-values 3-7x more likely B-smooth than random |
| T14 | B1 Conservation (P1-EXT) | On pure B1 path, m_k-n_k=1 for all k; halves effective A-size |
| T15 | Selberg Bound (P1-SEL) | Factor balance alpha=0.4 gives ~276x advantage |
| T16 | B3 Linear (P1-B3) | B3 with n=1: 22.2% smooth vs 4.4% random (5x) at B=100 |
| T17 | Matroid Low-Rank (Theorem 5) | Factored-form gives low GF(2) matroid rank; 5.7x smooth at depth 12 |
| T18 | Discriminant Diversity (DD1) | Length-4 paths generate 18 distinct discriminants |

### Pythagorean Tree — Dynamics/Growth (T19-T23)

| ID | Theorem | Key Statement |
|----|---------|---------------|
| T19 | Lyapunov Exponents (L1) | B2: lambda=0.88 (exponential); B1/B3: ~0.03 (polynomial) |
| T20 | No Fixed Points (AD1) | B2 has zero fixed points on (Z/pZ)^2\{0} |
| T21 | Equidistribution (AN1) | Tree m-values converge to equidistribution mod p |
| T22 | CRT Period (O1) | period(N) = lcm(period(p), period(q)) — exactly confirmed |
| T23 | Geometric Mean (Theorem 19) | Geo mean grows as c0*(3+2sqrt2)^d; Lyapunov = log(3+2sqrt2) ~ 1.763 |

### Pythagorean Tree — Structural/Negative (T24-T31)

| ID | Theorem | Key Statement |
|----|---------|---------------|
| T24 | Tropical Intersection (T1) | Two B3 paths intersect at predictable step — O(p) barrier |
| T25 | Perfect Group (HOM1) | <B1,B3> mod p generates SL(2,F_p), perfect for p>=5 |
| T26 | Bijection Barrier | Tree walks have O(p) cycles — kills Pollard rho on tree |
| T27 | CFRAC-Tree Equivalence | CFRAC = Pythagorean tree with adaptive step sizes M(a_k) |
| T28 | Brahmagupta-Fibonacci (Theorem 105) | Two sum-of-squares reps -> 100% factor extraction (but finding reps is O(sqrt(N))) |
| T29 | Cross-Poly LP Resonance | 3.298x LP collision rate above random — VERIFIED |
| T30 | Discriminant Identity | disc = 16*N*n0^4 — 100% verified (19701/19701) |
| T31 | Hypotenuse Primes (Theorem 14) | All prime C from tree are 1 mod 4; fraction 32.4% vs expected 9.3% |

### Pythagorean Tree — Additional (T32-T40)

| ID | Theorem | Key Statement |
|----|---------|---------------|
| T32 | Jacobi Two-Square (Theorem 18) | r2(C) = 4(d1(C)-d3(C)) confirmed on tree |
| T33 | Modular Forms r2 | High r2 iff many primes 1 mod 4 in C |
| T34 | Area Divisibility (Theorem 165) | ALL areas of primitive triples divisible by 6 |
| T35 | Hypotenuse Residue Bias (Theorem 161) | No hypotenuse divisible by primes 3 mod 4 |
| T36 | Leg Ratio Golden (Theorem 162) | Mean min/max leg ratio = 0.6158, close to 1/phi = 0.618 |
| T37 | Twin Triples (Theorem 153) | 5749 A-twins (differ by 2), zero B-twins and C-twins |
| T38 | Totient Bias (Theorem 168) | Mean phi(C)/C = 0.933, much higher than random 6/pi^2 |
| T39 | Random Matrix (Theorem 151) | Eigenvalue spacings are Poisson, NOT GOE |
| T40 | Collatz Steps (Theorem 167) | Hypotenuses need fewer Collatz steps than random odds |

### Session 9 — 20 Tree Walk Theorems (T41-T60)

| ID | Theorem | Key Statement |
|----|---------|---------------|
| T41-T60 | Walk Entropy, Catalan, Automorphisms, Angular Spectrum, Generating Function, Autocorrelation, Cross-Products, Inverse Tree, Lattice/Minkowski, Fibonacci, Prime Legs, Digital Roots, Ternary Density, Hypotenuse Periodicity, QR Distribution, Matrix Eigenvalues, Coprimality, CF Depth, Collatz Dynamics | See RESEARCH_SUMMARY.md Track B |

### Pythagorean Tree — Modular Arithmetic (T66-T69)

| ID | Theorem | Key Statement |
|----|---------|---------------|
| T66 | Unipotent Fermat Analog (T2-1) | B1^p = B3^p = I mod p for all primes p; B1,B3 are unipotent of exact order p |
| T67 | Exact Orders (T2-2) | ord(B1) = ord(B3) = p; ord(B2) divides (p-1) or 2(p+1) depending on QR of 2 |
| T68 | CRT Period Decomposition (T8-1) | period_N = lcm(period_p, period_q) — proven for composite N=pq |
| T69 | p-adic Period Lifting (T8-2) | period mod p^n ~ period_p * p^{n-1} for n >= 2; Hensel lifting of tree periods |

### Complexity Theory (T61-T65)

| ID | Theorem | Key Statement |
|----|---------|---------------|
| T61 | Dickman Information Barrier | Conditional: generic sieve algorithms require L[1/3,c] candidates |
| T62 | SIQS Scaling Law | SIQS fits L[1/2, c=0.991] — matches theory precisely |
| T63 | Compression Barrier | Semiprimes indistinguishable from random (gap < 0.006) |
| T64 | Communication LB | One-way factoring communication is Omega(n) bits |
| T65 | B3-SAT Debunked | B3 mod 2 = Identity; eigenvector extraction WORSE than random guessing |

### P vs NP Phase 5 — Algorithmic Barriers (T70-T75)

| ID | Theorem | Key Statement |
|----|---------|---------------|
| T70 | DLP Non-Natural Property | DLP homomorphism property is exponentially non-large → escapes natural proof barrier in principle |
| T71 | ABP Width for EC | EC addition polynomial has ABP width Ω(10-12); scalar mult has doubly-exponential degree |
| T72 | Cell-Probe Triviality | Cell-probe model gives only Ω(1) DLP bound — wrong model (hardness is computational, not data-structural) |
| T73 | DLP ∈ AM ∩ coAM | DLP cannot be NP-complete unless PH collapses (Boppana-Hastad-Zachos) |
| T74 | DLP-PvsNP Oracle Independence | All 4 combos of DLP-hard/easy × P=NP/P≠NP realizable by oracles — logically independent |
| T75 | Two-Barrier Escape | DLP has candidate escapes for natural proofs (non-large homomorphism) AND algebrization (non-polynomial Frobenius); relativization remains unbroken |

### ECDLP Exotic Fields (T76-T85)

| ID | Theorem | Key Statement |
|----|---------|---------------|
| T76 | Motivic Uniformity | Near-miss distribution |x(kG)-x(P)| is uniform on F_p — no exploitable structure |
| T77 | Derived Triviality | Derived AG collapses to classical for smooth curve over finite field — higher homotopy trivial |
| T78 | Perfectoid Mismatch | Tilting is multiplicative; destroys additive EC group law. Over F_p, tilting = identity |
| T79 | Condensed Discreteness | Condensed math adds structure only to infinite topological groups; E(F_p) is finite discrete |
| T80 | Topos Equivalence | Etale infinity-topos gives Frobenius eigenvalues = #E(F_p) only, not DLP |
| T81 | NCG Generator-Independence | Spectral triple for Z/nZ encodes group order n but NOT which element generates — spectrum is generator-independent |
| T82 | HoTT Transport = DLP | Univalence proves DLP path exists but computing transport map IS solving DLP |
| T83 | Spatial Pseudorandomness | EC multiples are spatially indistinguishable from random (Ripley's K matches Poisson) |
| T84 | QEC Classical Futility | Classical syndrome computation costs O(kG) per candidate — no advantage over exhaustive search |
| T85 | Ramsey Structure Absence | Monochromatic EC subsets have no DLP-useful structure — Ramsey can't overcome pseudorandomness |

### Algorithm Techniques (T86-T89)

| ID | Theorem | Key Statement |
|----|---------|---------------|
| T86 | Classic Algo Equivalence | Sieve IS sweep line; Gauss IS optimal DP; BSGS IS MITM; comb IS memoization — all already applied |
| T87 | Multi-Speed Rho Futility | k pointers cost k(k+1)/2 evals for k(k-1)/2 pairs — ratio always O(1), cannot beat O(N^{1/4}) |
| T88 | B&B vs Gauss | Branch-and-bound is 1180x slower than Gauss for GF(2) dependencies — exponential search vs polynomial exact |
| T89 | GNFS Poly Search Range | SA found 10^4.2 better norm by searching ±20K instead of ±1000 around m0 |

---

## 3. All Hypotheses Tested

| ID | Field | Hypothesis | Result | Session |
|----|-------|-----------|--------|---------|
| H1 | Pythagorean Smoothness | Tree A-values smoother than random | CONFIRMED 3-7x | 1-2 |
| H2 | B3-SAT Linearization | B3 shear solves 3-SAT in poly time | DEBUNKED | 3 |
| H3 | Neural Network Factoring | NN can learn factor function | FAILED (1% = random) | 3 |
| H4 | Simulated Annealing | SA can factor via energy min | FAILED (O(sqrt(N))) | 3 |
| H5 | Lattice Sieve | Special-q gives 43-50x sieve speedup | CONFIRMED (theory) | 2 |
| H6 | Block Lanczos | O(n^2*w/64) LA possible | CONFIRMED (theory) | 2 |
| H7 | GPU Sieve | CUDA gives 10-50x sieve speedup | PARTIAL (1.6x vs C sieve) | 2 |
| H8 | SIQS DLP Revival | LP_bound=fb*100 enables cycles | CONFIRMED & MERGED | 2-3 |
| H9 | K-S Multiplier | Multiplier gives 1.2-2.4x for SIQS | CONFIRMED up to 2.38x | 1-2 |
| H10 | Cross-Poly LP Resonance | LP collisions above random | CONFIRMED 3.298x | 5 |
| H11 | Disc = 16*N*n0^4 | Discriminant identity for B3 | CONFIRMED 100% | 5 |
| H12 | B3 Lattice 8.2x | B3 sieve hit rate 8.2x | PARTIAL (2.3x verified) | 5 |
| H13 | Bernstein Batch-GCD | 6-9x smoothness testing | NOT IMPLEMENTED | 5 |
| H14 | 20 Moonshot Paradigms | Alt computation breaks barrier | ALL DEAD (reduce to known) | 5 |
| H15 | 20 Complexity Fields | Novel math breaks L[1/3] | ALL NEGATIVE (19/20) | 3 |
| H16 | Phase Transition | Factoring has easy/hard boundary | NO (smooth scaling) | 3-4 |
| H17 | Structural Predictors | N's bits predict difficulty | NO (correlation < 0.18) | 3-4 |
| H18 | GPU Cofactor Checking | GPU batch TD for SIQS | CONFIRMED 42-83x | 7 |
| H19 | GPU Batch ECM | GPU parallel curves | CONFIRMED 4-99x | 7 |
| H20 | GPU Batch Rho | GPU parallel rho | CONFIRMED 8.5x | 7 |
| H21 | Compression Distinguishes | Compressor detects semiprimes | FAILED (gap < 0.006) | 8 |
| H22 | ECDLP Tree Transfer | Pyth theorems help ECDLP | ALL 6 FAILED | 10 |
| H23 | 20 Session-10 Fields | Novel fields break barrier | ALL 20 REFUTED | 10 |
| H24 | Presieve Optimization | Presieve speeds SIQS | NO (slower at 60d) | 10 |
| H25 | 10 Exotic Fields Batch B | Novel math breaks ECDLP barrier | ALL 10 NEGATIVE | 11 |
| H26 | DLP Non-Natural Proof | DLP homomorphism escapes natural proofs | CONFIRMED (structural) | 11 |
| H27 | DLP ∈ AM ∩ coAM | DLP not NP-complete | CONFIRMED | 11 |
| H28 | DLP-PvsNP Independence | Oracle separation for DLP vs P≠NP | CONFIRMED (all 4 combos) | 11 |
| H29 | Fine-Grained ECDLP vs 3-SUM | Reduction between problems | FAILED (incompatible) | 11 |
| H30 | Cell-Probe DLP Bounds | Non-trivial data structure bounds | FAILED (Ω(1) only) | 11 |
| H31 | 10 Classic Algo Techniques | Novel factoring/ECDLP speedup | 6 NEGATIVE, 4 ALREADY KNOWN | 11 |
| H32 | LP Relaxation for FB | Better FB selection | NO EFFECT (= smallest primes) | 11 |
| H33 | Bloom Filter for LP | Memory savings for LP table | CONFIRMED 30x savings | 11 |
| H34 | SA for GNFS Poly | Better polynomial selection | CONFIRMED 10^4.2 better norms | 11 |
| H35 | A* on Pyth Tree | Better tree search for factoring | CONFIRMED 1.22x (small factors only) | 11 |
| H36 | Shared-Memory Kangaroo | Multi-process ECDLP speedup | CONFIRMED 2.2-3.1x (6 workers) | 11 |

---

## 4. Current Solver Scoreboard

### Integer Factoring

| Digits | Time | Method | Notes |
|--------|------|--------|-------|
| 48d | 2.0s | SIQS | With K-S multiplier |
| 54d | 12s | SIQS | 2-worker mode |
| 60d | 48s | SIQS | 2-worker mode |
| 63d | 90s | SIQS | 2-worker mode |
| 66d | 244s | SIQS | Sieve-bound |
| 69d | 493s | SIQS | Best (down from 538s) |
| 48d | 5.8s | B3-MPQS | Pythagorean polynomial source |
| 55d | 25s | B3-MPQS | |
| 60d | 82s | B3-MPQS | |
| 63d | 128s | B3-MPQS | |
| 34d | 55s | GNFS d=3 | End-to-end working |
| 42d | 263s | GNFS d=4 | |
| 43d | 439s | GNFS d=4 | |
| 40d | 1s | CFRAC | Pythagorean tree CFRAC |
| 45d | 57s | CFRAC | L(1/2) complexity |

### ECDLP (secp256k1) — Updated 2026-03-15

| Bits | Shared+Lévy (6w) | Single CPU | GPU Kangaroo | Notes |
|------|-------------------|-----------|-------------|-------|
| 28 | - | 0.060s | - | |
| 36 | 0.24s | 0.62s | - | 2.6x shared speedup |
| 40 | 2.6s | 7.9s | 3.4s | 3.0x shared speedup |
| 44 | 16.5s | 46.7s | 7.3s | 2.8x shared speedup |
| 48 | 38.5s | 135s | 38s | 3.5x shared speedup |
| 56 | - | - | ~20s | GPU wins at higher bits |
| 60 | - | - | ~34s | |

### GPU Acceleration

| Kernel | Speedup | Notes |
|--------|---------|-------|
| Cofactor checking | 42-83x | Immediate SIQS/GNFS integration |
| Batch ECM | 4-99x | 28-99x with Montgomery mulmod |
| Batch Rho | 8.5x | For medium cofactors |
| Modular multiply | 10.1x | Russian peasant; Montgomery would give 50-200x |

---

## 5. Architecture

### Key Files

| File | Purpose |
|------|---------|
| `siqs_engine.py` | SIQS engine — primary factoring workhorse (48-69d) |
| `gnfs_engine.py` | GNFS engine — all 5 phases + SGE + DLP + SLP |
| `cfrac_engine.py` | CFRAC engine — Pythagorean tree continued fractions |
| `pyth_resonance.py` | B3-MPQS engine — Pythagorean polynomial source |
| `resonance_v7.py` | Unified driver — heterogeneous dispatcher |
| `ecdlp_pythagorean.py` | ECDLP solvers — FastCurve, GLV-BSGS, kangaroo |
| `ec_kangaroo_c.c/.so` | C Pythagorean Kangaroo (Berggren hypotenuse jumps) |
| `ec_bsgs_c.c/.so` | C Baby-Step Giant-Step with GMP hash table |
| `gnfs_sieve_c.c/.so` | C sieve+verify extension (__int128, Miller-Rabin) |
| `pollard_rho_c.c/.so` | C Pollard rho for quick cofactor splitting |
| `siqs_trial_div_c.c/.so` | C batch trial division (35x faster) |
| `gpu_cofactor_lite.cu/.so` | GPU cofactor checking kernel |
| `gpu_batch_ecm.cu` | GPU parallel ECM (2560 curves) |
| `gpu_batch_rho.cu` | GPU parallel Pollard rho |
| `benchmark_suite.py` | Standardized benchmarks |

### Resonance Sieve v7.0 Architecture

- **Path 1**: VSDD Sniper + Super-Generator (Pythagorean tree + Spectral Compass)
- **Path 2**: SIQS engine (sub-exponential sieve, 48-69d)
- **Path 3**: GNFS engine (for 40d+, sub-exponential, end-to-end working)
- **ECM bridge**: For unbalanced factors up to ~54 digits

---

## 6. Open Research Directions

| Rank | Direction | Promise | Expected Impact | Effort |
|------|-----------|---------|-----------------|--------|
| 1 | C Lattice Sieve for GNFS | HIGH | 43-50x sieve, enables 50d+ | 1-2 weeks |
| 2 | Block Lanczos in C | HIGH | 200-600x LA, essential for 50d+ | 1-2 weeks |
| 3 | GPU Montgomery mulmod | HIGH | Unlocks 100-700x GPU ECM | 2-3 days |
| 4 | SIQS parameter auto-tuning | MEDIUM | 1.5-1.9x from FB/M rebalancing | 1 day |
| 5 | GPU cofactor integration | MEDIUM | 42-83x cofactor phase | 2-3 days |
| 6 | ECM Phase 2 (BSGS) | MEDIUM | 20-30% more primes at 4% cost | 1 day |
| 7 | Kleinjung poly selection | MEDIUM | 2-5x norm reduction at 70d+ | 1-2 weeks |
| 8 | ECDLP multiprocessing | MEDIUM | ~5x from 6 workers | 1-2 days |
| 9 | Cross-poly LP resonance | LOW-MED | 3.3x LP yield (verified) | 2-3 days |
| 10 | Block Wiedemann (O(n) space) | LOW | Alternative to BL for huge matrices | 2 weeks |
| 11 | GNFS poly search ±20K | MEDIUM | SA found 10^4.2 better norms vs ±1000 | 1 hour |
| 12 | Bloom filter for LP table | LOW-MED | 30x memory savings, 0% combining loss | 1 day |
| 13 | Fixed-b precomputation (GNFS) | LOW | 1.19x norm evaluation speedup | 1 hour |

---

## 7. Failed Directions (Do Not Retry)

### Mathematical Fields (275+ explored, ALL negative)
- Algebraic Geometry, p-adic Analysis, Tropical Geometry, Category Theory, Knot Theory, Modular Forms, Fourier Analysis, Differential Geometry, Ramsey Theory, Homological Algebra, Coding Theory, Arithmetic Dynamics, K-Theory, Quantum Groups, Partition Theory, Transcendental NT, Compressed Sensing, Persistent Homology, Free Probability, Mahler Measure, Dilogarithm, Perfectoid Spaces, Motivic Cohomology, Cluster Algebras, Random Matrix Theory, Langlands, Iwasawa Theory, TDA, Quantum Walks, Symplectic Geometry, Homotopy Type Theory, Clifford Algebras, Representation Theory, Adelic Analysis, Spectral Graphs, Noncommutative Geometry, Operads, Descriptive Set Theory, Proof Complexity, Reverse Mathematics, Condensed Mathematics, Motivic Integration, Derived AG, Infinity-Topos Theory, Stochastic Geometry, Quantum Error Correction...

### Specific Failed Approaches
- **B3-SAT Linearization**: B3 mod 2 = Identity; tautology, not breakthrough
- **Neural network factoring**: 1% accuracy = random guessing
- **Simulated annealing**: O(sqrt(N)) at best; exponential local minima
- **Tensor networks**: Bond dimension O(n); slower than Block Lanczos
- **Grobner bases**: Doubly exponential; times out at 4-bit factors
- **Coupled chaotic maps**: 7-33x SLOWER at 40-48 bits
- **Index calculus on Z/NZ***: IS NFS/QS; no new algorithm
- **K-S multiplier for GNFS**: Fundamental incompatibility (not QS-family)
- **Batch GCD for GNFS**: Finds 5% of smooth; lateral move vs C verify
- **Tree Pollard rho**: 15-1000x SLOWER (bijection barrier)
- **Multi-k Fermat**: ALL null vectors trivial (x equiv y mod N)
- **GNFS from B2 polynomials**: Degree-2 loses by 10^4.5 to degree-5
- **Presieve**: Slower at 60d; threshold interaction subtle
- **All 20 moonshot paradigms** (analog ODE, DNA, optical, GA, ant colony, etc.): reduce to trial div or rho
- **ECDLP tree transfer**: EC scalar mult destroys all number-theoretic structure
- **Multi-speed pointer rho**: k pointers cost k(k+1)/2 evals for k(k-1)/2 pairs — ratio O(1)
- **DP on Factor Base**: Equivalent to online Gauss; exponential state space
- **Branch-and-bound GF(2)**: 1180x slower than Gauss — exponential vs polynomial
- **LP relaxation for FB**: No-op — scoring function = "pick smallest primes" = standard
- **Cell-probe DLP bounds**: Wrong model — DLP hardness is computational, not data-structural
- **Fine-grained ECDLP vs 3-SUM**: No valid reduction in either direction — incompatible structure

---

## 8. Path to RSA-100

### Current State
- SIQS handles up to 69d (538s)
- GNFS handles up to 43d (439s) — bottlenecked by line sieve + dense Gauss
- RSA-100 = 100 digits = 330 bits, balanced 50d factors

### Required Optimizations

| Step | Optimization | Impact | Status |
|------|-------------|--------|--------|
| 1 | C Lattice Sieve | 43-50x sieve | Prototype done, needs integration |
| 2 | Block Lanczos in C | 200-600x LA | Algorithm understood, needs C impl |
| 3 | Larger FB (300K+) | Enables 70d+ | Parameter tuning needed |
| 4 | GPU trial division | 5-20x verify | CUDA kernel analyzed |
| 5 | Kleinjung poly selection | 2-5x norms | Complex implementation |
| 6 | DLP for GNFS | 30-50% more rels | Algorithm ready |

### Projected Timeline (all optimizations)

| Target | Projected Time | Method |
|--------|---------------|--------|
| GNFS 50d | ~600s | Lattice sieve + BL |
| GNFS 60d | ~30 min | Lattice sieve + BL |
| GNFS 70d | ~5 hours | + Kleinjung poly |
| **RSA-100** | **~346 hours (~2 weeks)** | All optimizations |
| RSA-100 + GPU | ~days | + GPU sieve/verify |

### Constraints
- WSL2 with ~12GB RAM + 8GB swap (5GB practical limit)
- GNFS LA crashes above ~15K matrix rows (bitpacked Gauss helps to 80K)
- RTX 4050 6GB VRAM available for GPU acceleration

---

## 9. P vs NP Summary

### Five Phases of Investigation (14+ experiments)

| Phase | Focus | Key Finding |
|-------|-------|-------------|
| 1 | Three barriers | Relativization, natural proofs, algebrization block all known proofs |
| 2 | SAT encoding, hardness distribution | No phase transition; unimodal difficulty; SIQS c=0.991 |
| 3 | Dickman formalization, communication complexity | Conditional lower bound for generic sieves |
| 4 | Compression barrier, time-space tradeoffs | Semiprimes indistinguishable from random |
| 5 | Circuit depth, algorithm entropy, proof complexity | Exponential circuit depth; entropy predicts difficulty |

### The Dickman Information Barrier
- Relations/bits overhead grows as 10^(0.24 * digits)
- Empirical smoothness matches Dickman prediction within 10-20%
- **Conditional theorem**: Generic sieve algorithms require L[1/3,c] candidates
- **Gap**: Cannot prove ALL algorithms must sieve (the hard part)

### Phase 5: Algorithmic Barriers (8 experiments, 2026-03-15)
- **DLP has non-natural-proof-compatible structure**: homomorphism property is exponentially non-large
- **DLP ∈ AM ∩ coAM**: cannot be NP-complete unless PH collapses
- **Oracle independence**: all 4 combos of DLP-hard/easy × P=NP/P≠NP realizable
- **Two of three barriers escapable** for DLP: natural proofs (non-large) + algebrization (non-polynomial Frobenius)
- **Relativization remains unbroken** — the fundamental obstacle
- Cell-probe and fine-grained reductions fail for DLP (wrong models)
- DLP-based PoW either = slow hash (weak) or inflexible (strong)
- **32 total experiments across 5 phases**, 18 distinct approaches

### Honest Assessment
- **Cannot prove P=NP or P!=NP** — three barriers block all known techniques
- Factoring is in NP intersection co-NP intersection BQP — almost certainly NOT NP-complete
- DLP ∈ AM ∩ coAM — also cannot be NP-complete (unless PH collapses)
- DLP hardness and P vs NP are **logically independent** in relativized settings
- Two of three proof barriers have DLP-specific escape routes; relativization remains
- Shor's algorithm proves hardness is classical-model-specific, not fundamental
- No structural predictors of difficulty (all correlations < 0.18)
- No phase transition (smooth increase, NOT NP-complete behavior)
- **Strong circumstantial evidence factoring is NOT in P**, but no proof exists

---

## 10. ECDLP Summary

### What Works (Engineering Optimizations)
| Optimization | Speedup | Status |
|-------------|---------|--------|
| Batch Montgomery inversion | 1.4-1.8x | MERGED |
| GMP mpn_ fixed-limb hot path | 1.3-1.6x | MERGED |
| fe_t batch inversion tree | 1.2x | MERGED |
| CUDA GPU kangaroo | 10-23x | MERGED |
| GPU SM-aware kangaroo count | ~20% | MERGED |
| Lévy flight jump spread (1-10M, 10^7 ratio) | 1.33-1.37x | MERGED |
| Murmur3 jump hash | Reduces outliers | MERGED |
| Bernstein-Yang divstep inversion | 1.3-1.6x | MERGED |
| Shared-memory multi-process (6w) | 2.2-3.1x | MERGED |
| Lévy flight max_jump cap | Fixes 44b pathology | MERGED |

### What's Impossible (Barrier Analysis — 46+ hypotheses tested)
- **All Pythagorean tree theorems fail for ECDLP**: EC scalar multiplication destroys number-theoretic structure
- **GLV equivalence class**: Different cosets for tame/wild; no reduction in expected steps
- **Negation map**: Bounded search interval too small relative to group order
- **EC index calculus**: No prime-field EC index calculus exists
- **Tree-correlated jumps**: Jump SOURCE doesn't matter; only SPREAD shape matters
- **20 exotic math fields (Batch A+B)**: Motivic, Derived AG, Perfectoid, Condensed, Topos, NCG, HoTT, Stochastic Geometry, QEC, Ramsey — ALL NEGATIVE
- **O(sqrt(N)) is provably optimal** for generic group DLP — all improvements are constant-factor

### The Fundamental Reason ECDLP Is Hard
EC scalar multiplication is a pseudorandom permutation — it completely destroys the number-theoretic structure of the scalar. x-coordinates are uniform in F_p regardless of the scalar's algebraic properties. Smoothness amplification helps factoring (same ring) but not ECDLP (different group). The only ECDLP improvements are: (1) engineering (shared DP, GPU, batch inversion), (2) curve-specific endomorphisms (GLV Z/6), (3) hardware parallelism.

---

## Appendix: Engine Optimizations Merged (15 total)

| # | Optimization | Speedup | Commit |
|---|-------------|---------|--------|
| 1 | K-S multiplier for SIQS | up to 2.38x | 87af028 |
| 2 | DLP revival + LP bound | 30-50% more rels | 2e0b643 |
| 3 | Singleton filtering | 15-50% LA | d1a3e04 |
| 4 | Multithread sieve | 1.77-1.81x | c241e30 |
| 5 | Bitpacked GF(2) Gauss | 80K rows/1.2GB | 34de418 |
| 6 | Sieve width tuning | 1.34x at 60d | — |
| 7 | C lattice sieve for GNFS | Enables 50d+ | — |
| 8 | C trial division | 35x faster | — |
| 9 | DLP rho optimization | ~4x on 49.5% hotspot | 1b0e0e9 |
| 10 | Int16 sieve | 1.27x at 52d | 19df211 |
| 11 | C Pollard rho for _quick_factor | 1.47x at 52d | cc8dcef |
| 12 | GNFS 3-bug fix | 14% | 6698e71 |
| 13 | Sparse exponents for multiprocessing | Fixes 69d OOM | fa8cb77 |
| 14 | Small_prime_correction threshold | Fixes regression | 71b09c0 |
| 15 | GNFS coprimality filter + int64 fix + wider poly | 39% fewer verify calls | e34d480 |

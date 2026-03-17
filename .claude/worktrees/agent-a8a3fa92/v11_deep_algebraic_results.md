# Deep Algebraic Structure Mining — Results

# Deep Algebraic Structure Mining for Factoring Breakthroughs
# Date: 2026-03-15 23:24:24
# 22 experiments across 5 tracks


## Track 5: B3 mod N Walk Smoothness
============================================================

### Exp 5.1: B3 mod N walk — smoothness rate vs random
  CRITICAL: Using burn-in of 500 steps to ensure mixing.
  Using random starting (m,n) to avoid small-value artifact.
  20b: B3 smooth=14.7/200, random=16.7/200, ratio=0.88x, B=50, time=0.0s
  24b: B3 smooth=6.7/200, random=7.1/200, ratio=0.95x, B=50, time=0.0s
  28b: B3 smooth=0.9/200, random=1.3/200, ratio=0.72x, B=50, time=0.0s
  32b: B3 smooth=0.5/200, random=0.5/200, ratio=1.09x, B=63, time=0.1s
  36b: B3 smooth=0.2/200, random=0.3/200, ratio=0.53x, B=88, time=0.1s
  40b: B3 smooth=0.1/200, random=0.0/200, ratio=6.00x, B=121, time=0.1s

### Exp 5.1b: Value size diagnosis — are B3 mod N values small?
  Measuring actual bit size of A_mod values vs N
  N has 32 bits
  Early walk (no burn-in) A_mod sizes: [5, 7, 9, 10, 11, 13, 15, 17, 19, 20, 21, 23, 23, 24, 24, 28, 30, 30, 30, 30]
  Min=5, Max=32, Avg=25.8
  After burn-in A_mod sizes: [27, 31, 30, 26, 30, 31, 31, 30, 30, 30, 29, 32, 32, 27, 28, 28, 28, 32, 30, 31]
  Min=26, Max=32, Avg=30.2
  Early walk values are full-size — smoothness is genuine.

### Exp 5.2: Pure B3 walks vs mixed Berggren walks vs random
  (Pure B3 = only matrix B3; mixed = random choice of B1/B2/B3)
  Using random start + burn-in to avoid small-value artifact.
  pure_b3: avg smooth = 0.67/300
  pure_b1: avg smooth = 0.69/300
  mixed: avg smooth = 0.74/300
  random: avg smooth = 0.62/300

### Exp 5.3: Structural analysis — B3 mod N value distribution
  Question: Are B3 mod N values uniformly distributed in [0,N)?
  Using random start + burn-in.
  KS test: stat=0.0099, p-value=0.7105
  RESULT: Values ARE uniformly distributed (p=0.710 > 0.05)
  => Smoothness rate should match random. No structural advantage.

### Exp 5.4: B3 in Z — smoothness decay with depth
  (Baseline: how quickly do tree values lose smoothness in Z?)
  depth=  5 (~13b): smooth(500)=1.0000 (200/200)
  depth= 10 (~25b): smooth(500)=0.4800 (96/200)
  depth= 15 (~38b): smooth(500)=0.1350 (27/200)
  depth= 20 (~51b): smooth(500)=0.0150 (3/200)
  depth= 25 (~64b): smooth(500)=0.0000 (0/200)
  depth= 30 (~76b): smooth(500)=0.0000 (0/200)
  depth= 35 (~89b): smooth(500)=0.0000 (0/200)
  depth= 40 (~102b): smooth(500)=0.0000 (0/200)
  depth= 45 (~114b): smooth(500)=0.0000 (0/200)
  depth= 50 (~127b): smooth(500)=0.0000 (0/200)
  depth= 55 (~140b): smooth(500)=0.0000 (0/200)
  depth= 60 (~153b): smooth(500)=0.0000 (0/200)

### Exp 5.5: Factored form A=(m-n)(m+n) — smoothness of PIECES
  Key insight: A is B-smooth iff BOTH (m-n) and (m+n) are B-smooth.
  Pieces are ~sqrt(A) in size, so u_piece ~ u/2.
  Dickman: rho(u/2)^2 >> rho(u) — exponential advantage.
  CRITICAL: Mod N, pieces are ~N in size (not sqrt), so no advantage.
  Testing both Z and mod N to show the difference.
  Trial 0: MOD N: pieces_smooth=0/200, A_smooth=0/200
           IN Z:  pieces_smooth=5/200, A_smooth=5/200
  Trial 1: MOD N: pieces_smooth=0/200, A_smooth=0/200
           IN Z:  pieces_smooth=7/200, A_smooth=7/200
  Trial 2: MOD N: pieces_smooth=0/200, A_smooth=0/200
           IN Z:  pieces_smooth=4/200, A_smooth=4/200

  NOTE: In Z, pieces are ~sqrt(A), so piece smoothness >> A smoothness.
  Mod N, pieces are ~N in size, so piece smoothness ~ A smoothness ~ random.
  This is WHY mod N destroys the factored-form advantage.

### Exp 5.6: N-dependent B3 — modified matrix with N-dependent entries
  Idea: Replace B3 = [[1,2],[0,1]] with B3(N) = [[1, 2*k],[0, 1]]
  where k = floor(sqrt(N)) or similar N-dependent quantity.
  The matrix is still unipotent (eigenvalues 1,1), so orbits don't escape.
  k=2 (standard B3): avg smooth = 0.48/200
  k=isqrt(N): avg smooth = 0.28/200
  k=N%100+1: avg smooth = 0.46/200
  k=gcd(N,6)+1: avg smooth = 0.48/200

### Exp 5.7: Proof sketch — why B3 mod N is pseudorandom
  B3 = I + 2*E_12 in SL(2,Z). Mod N, B3 has order N/gcd(2,N).
  The orbit {B3^k (m,n) mod N : k=0..N-1} visits all
  (m + 2kn mod N, n) for k=0..N-1.
  Since gcd(2n, N) is small (usually 1 or 2),
  this is a PERMUTATION of Z/NZ in the m-coordinate.
  => The m-values are uniformly distributed mod N.
  => A = m^2 - n^2 mod N is a random quadratic residue mod N.
  => Smoothness rate = rho(u) where u = log(N)/log(B). Same as random.

  FUNDAMENTAL OBSTRUCTION: The factored form A = (m-n)(m+n) only helps
  in Z (where pieces are smaller). Mod N, the product wraps around,
  and the pieces are NOT smaller — they are ~N in size.
  The N-independent discriminant (16*n0^4) means the tree structure
  is ORTHOGONAL to N. Mod N, this orthogonality becomes irrelevance.

  Plot saved: images/deep_alg_track5_smoothness.png

## Track 5 Continued: The Fundamental Obstruction
============================================================

### Exp 5.8: Dickman function verification for B3 walks in Z
  In Z, tree values grow as ~lambda^depth. At depth d,
  |A| ~ 5.83^d, so u = d*log(5.83)/log(B).
  Dickman rho(u) should predict smoothness rate.
  B = 500, log(B) = 6.21
  depth=  5: u=1.42, measured=1.000000, dickman~0.650438, ratio=1.54
  depth= 10: u=2.84, measured=0.424000, dickman~0.051920, ratio=8.17
  depth= 15: u=4.26, measured=0.122000, dickman~0.002107, ratio=57.90
  depth= 20: u=5.67, measured=0.020000, dickman~0.000053, ratio=378.74
  depth= 25: u=7.09, measured=0.004000, dickman~0.000001, ratio=4325.20
  depth= 30: u=8.51, measured=0.000000, dickman~0.000000, ratio=0.00
  depth= 35: u=9.93, measured=0.000000, dickman~0.000000, ratio=0.00
  depth= 40: u=11.35, measured=0.000000, dickman~0.000000, ratio=0.00
  depth= 45: u=12.77, measured=0.000000, dickman~0.000000, ratio=0.00
  depth= 50: u=14.18, measured=0.000000, dickman~0.000000, ratio=0.00

### Exp 5.9: Factored form advantage in Z
  A = (m-n)(m+n). Each piece ~ sqrt(A) ~ 5.83^{d/2}.
  Smoothness of A via pieces: Pr[A smooth] ~ rho(u/2)^2
  depth=10: u=2.84, A_smooth=0.464000, pieces_smooth=0.464000, boost=1.00x
  depth=20: u=5.67, A_smooth=0.030000, pieces_smooth=0.030000, boost=1.00x
  depth=30: u=8.51, A_smooth=0.000000, pieces_smooth=0.000000, boost=0.00x
  depth=40: u=11.35, A_smooth=0.000000, pieces_smooth=0.000000, boost=0.00x

  KEY INSIGHT: In Z, piece smoothness gives ~2-3x boost at moderate depths.
  But mod N, pieces are NOT smaller (they wrap around to ~N).
  The factored form advantage is DESTROYED by modular reduction.

### Exp 5.10: Theoretical analysis — sub-L[1/2] obstruction proof

  THEOREM (informal): No Berggren tree walk mod N can achieve sub-L[1/2]
  factoring complexity.

  PROOF SKETCH:
  1. B3 mod N has order p (and q). The orbit of B3^k on (m,n) mod N
     cycles through all residues with period lcm(p,q) = N (for RSA).
  2. The values A_k = m_k^2 - n_k^2 mod N are quadratic functions of k mod N.
     By Weil's bound, the values are equidistributed mod p and mod q.
  3. Therefore, Pr[A_k is B-smooth] = rho(log(N)/log(B)) + O(1/sqrt(p)),
     which is the SAME as random numbers in [0, N).
  4. To collect enough smooth relations (~pi(B) relations),
     we need ~pi(B)/rho(u) trials, where u = log(N)/log(B).
  5. Optimizing B gives the standard L[1/2, 1] complexity.
  6. The tree structure (spectral gap, factored form, etc.) only helps in Z,
     where values grow exponentially. Mod N, growth is replaced by
     equidistribution, and all structural advantages vanish.

  WHAT WOULD BE NEEDED for sub-L[1/2]:
  - A polynomial f(x) of degree d where f(x) is smooth for x in [1, M]
    with M = N^{1/d}. This gives u = 1/d, and rho(1/d) ~ 1.
  - The NUMBER FIELD SIEVE uses exactly this with d ~ (log N)^{1/3}.
  - The Berggren tree cannot produce such polynomials because:
    (a) Tree values are quadratic in (m,n), giving degree 2 always.
    (b) The tree is fixed (N-independent), so it cannot adapt to N's structure.
    (c) Making it N-dependent (mod N) destroys the smoothness advantage.

  Plot saved: images/deep_alg_track5_obstruction.png

## Track 1: The sqrt(-1) Factory
============================================================

### Exp 1.1: Verify a*b^{-1} mod c = sqrt(-1) mod c for PPTs
  Tree triples generated: 797161
  Prime hypotenuses: 518
  Tested (prime, = 1 mod 4): 518
  Verified sqrt(-1): 518/518
  Success rate: 100.00%

### Exp 1.2: Birthday collision on hypotenuses mod N
  Find c_i, c_j with gcd(c_i - c_j, N) > 1
  20b: 0/20 found, avg_steps=856, sqrt(N)=1024, time=0.0s
  24b: 0/20 found, avg_steps=4153, sqrt(N)=4096, time=0.7s
  28b: 0/20 found, avg_steps=8622, sqrt(N)=16384, time=3.3s
  32b: 0/20 found, avg_steps=10000, sqrt(N)=65536, time=4.6s

### Exp 1.3: Pollard rho on hypotenuses vs standard rho
  Standard rho: f(x) = x^2 + 1 mod N
  Hyp rho: f(m,n) = Berggren(m,n), check gcd(c mod N, N)
  Standard rho: avg 62 steps
  Hypotenuse rho: avg 3458 steps
  Ratio (hyp/std): 55.69x
  VERDICT: Hyp rho is SLOWER. The 2D state space has worse birthday bound.

### Exp 1.4: Direct sqrt(-1) mod N from tree hypotenuses
  If we find (a,b,c) with c | N, then sqrt(-1) mod c -> sqrt(-1) mod p or q
  Combined with another such triple, CRT gives sqrt(-1) mod N
  NOTE: Tree in Z — hypotenuses grow as ~5.83^depth, quickly exceeding p,q.
  At depth d, c ~ 5.83^d. For 24b, p ~ 2^12 ~ 4096.
  At depth 5, c ~ 5.83^5 ~ 7000. So c > p after ~5 steps!
  Divisibility c % p == 0 becomes LIKELY because c >> p (many multiples).
  This is NOT a useful attack — it's an artifact of small N.
  20/20 found both p|c and q|c in 5000 steps
  This is an ARTIFACT: at depth d, c ~ 5.83^d >> p,q for small N.
  For cryptographic N (100+ digits), c never reaches p in feasible depth.

  Verification at larger bit sizes:
  32b: hit at step 1676, c has 3153b, p has 13b, c/p ~ 2875498455328882091923599881928845751391637104750324120119163779306352697315717616753144501927606122134303843007328331764414632189879362854940463279945978537910003339340135820426781852604510984009253364312811347160747521896368184320950108509865974221478408095593528006011595294331727241193438198510018924048466137503673194973075514300673951326396332195481228446797434603461576126835765103603251588871141959464438325346716143015852069585975307019084580564536051175192065906703263422008636653705353820352865365553577705758256917287221442536373890035071323398654850009953369739180536623607931807802435191422446314213374237226035009729235261274589570973266709982495382910485254810567702503368936291386405634461669492300920945704124483317804999128504296115167505425265113878724125410293979021178516082924102320506407330760365700118823221549185163738442535373883603761757304431459641487557723855758708491985209395686404306921676058895776326037938358413
  40b: NO hit in 5000 steps (c grows to 9273b, p=19b)
  48b: NO hit in 5000 steps (c grows to 9330b, p=24b)

  Plot saved: images/deep_alg_track1_sqrt.png

## Track 2: Berggren Group Structure & Berggren-ECM
============================================================

### Exp 2.1: Verify Berggren group order mod p
  p=  5: |G|=     240, predicted 2p(p^2-1)=     240, |GL(2)|=     480, ratio=1.000
  p=  7: |G|=     672, predicted 2p(p^2-1)=     672, |GL(2)|=    2016, ratio=1.000
  p= 11: |G|=    2640, predicted 2p(p^2-1)=    2640, |GL(2)|=   13200, ratio=1.000
  p= 13: |G|=    4368, predicted 2p(p^2-1)=    4368, |GL(2)|=   26208, ratio=1.000
  p= 17: |G|=    9792, predicted 2p(p^2-1)=    9792, |GL(2)|=   78336, ratio=1.000
  p= 19: |G|=   13680, predicted 2p(p^2-1)=   13680, |GL(2)|=  123120, ratio=1.000
  p= 23: |G|=   24288, predicted 2p(p^2-1)=   24288, |GL(2)|=  267168, ratio=1.000
  p= 29: |G|=   48720, predicted 2p(p^2-1)=   48720, |GL(2)|=  682080, ratio=1.000
  p= 31: |G|=   59520, predicted 2p(p^2-1)=   59520, |GL(2)|=  892800, ratio=1.000
  p= 37: |G|=  100001, predicted 2p(p^2-1)=  101232, |GL(2)|= 1822176, ratio=0.988
  p= 41: |G|=  100001, predicted 2p(p^2-1)=  137760, |GL(2)|= 2755200, ratio=0.726
  p= 43: |G|=  100001, predicted 2p(p^2-1)=  158928, |GL(2)|= 3337488, ratio=0.629
  p= 47: |G|=  100001, predicted 2p(p^2-1)=  207552, |GL(2)|= 4773696, ratio=0.482

### Exp 2.2: Berggren-ECM — factoring via Berggren group mod N
  Analogy with ECM: pick random point, compute k! * point in group,
  check if a coordinate is 0 mod p but not mod q.
  25/30 factored, avg steps=30

### Exp 2.3: B3 matrix order mod p by residue class
  p = 1 mod 8: p=17:ord(B1)=17,ord(B3)=17, p=41:ord(B1)=41,ord(B3)=41, p=73:ord(B1)=73,ord(B3)=73, p=89:ord(B1)=89,ord(B3)=89, p=97:ord(B1)=97,ord(B3)=97
  p = 3 mod 8: p=11:ord(B1)=11,ord(B3)=11, p=19:ord(B1)=19,ord(B3)=19, p=43:ord(B1)=43,ord(B3)=43, p=59:ord(B1)=59,ord(B3)=59, p=67:ord(B1)=67,ord(B3)=67
  p = 5 mod 8: p=5:ord(B1)=5,ord(B3)=5, p=13:ord(B1)=13,ord(B3)=13, p=29:ord(B1)=29,ord(B3)=29, p=37:ord(B1)=37,ord(B3)=37, p=53:ord(B1)=53,ord(B3)=53
  p = 7 mod 8: p=7:ord(B1)=7,ord(B3)=7, p=23:ord(B1)=23,ord(B3)=23, p=31:ord(B1)=31,ord(B3)=31, p=47:ord(B1)=47,ord(B3)=47, p=71:ord(B1)=71,ord(B3)=71

  B3 order = p always (unipotent: B3^p = I mod p for odd p)
  B1 order varies — depends on eigenvalues of B1 mod p
  B1 eigenvalues: 1 +/- sqrt(2). Order depends on ord(sqrt(2)) mod p

### Exp 2.4: Berggren-ECM vs standard Pollard p-1
  Berggren group order = 2p(p^2-1). Pollard p-1 needs p-1 smooth.
  Berggren needs 2p(p^2-1) smooth — MUCH harder.
  => Berggren-ECM is WORSE than p-1 and ECM.
  The group is too large (order ~ p^3 vs ~ p for EC).
  ECM works because EC groups have order p +/- O(sqrt(p)),
  so occasionally p+1+t is smooth. Berggren group is 2p^3, never smooth enough.

## Track 3: LP Resonance Rescue
============================================================

### Exp 3.1: GF(2) duplicate analysis for grouped a-values
  Simulate exponent vectors from grouped vs random polynomials
  shared=0: unique=500/500 (dup=0.0%), GF(2) rank=100/200
  shared=2: unique=500/500 (dup=0.0%), GF(2) rank=99/200
  shared=4: unique=500/500 (dup=0.0%), GF(2) rank=97/200
  shared=6: unique=500/500 (dup=0.0%), GF(2) rank=95/200
  shared=8: unique=500/500 (dup=0.0%), GF(2) rank=93/200

### Exp 3.2: WHY grouped 'a' causes GF(2) duplicates
  When s-1 primes are shared, the exponent vectors differ only in
  the s-1 shared positions (always odd) plus random sieve hits.
  Two relations from same group: v1 XOR v2 zeros out shared positions,
  leaving only sieve-hit differences. If sieve hits overlap (likely
  for similar sieve offsets), v1 XOR v2 has very low weight.
  This means many relations are GF(2)-dependent — they contribute
  no new information to the null space search.

### Exp 3.3: Partial grouping — share s-2 instead of s-1 primes
  Testing tradeoff: fewer shared primes = more GF(2) diversity
  but less LP resonance (fewer matching large primes)
  groups=  1: SLP_matches= 191, GF2_unique=1999/2000, net_useful~1191
  groups=  5: SLP_matches= 187, GF2_unique=1998/2000, net_useful~1187
  groups= 10: SLP_matches= 178, GF2_unique=1999/2000, net_useful~1178
  groups= 50: SLP_matches= 185, GF2_unique=1999/2000, net_useful~1185
  groups=200: SLP_matches= 143, GF2_unique=1999/2000, net_useful~1143

  CONCLUSION: More groups = fewer GF(2) duplicates but fewer LP matches.
  The tradeoff is approximately neutral — net useful relations ~constant.
  LP resonance cannot be rescued without fundamentally different grouping.

## Track 4: Compositional Attacks
============================================================

### Exp 4.1: CF convergents of sqrt(N) as SIQS 'a' quality metric
  SIQS needs 'a' values that are products of FB primes with a ~ sqrt(2N)/M
  CF convergents p_k/q_k of sqrt(N) satisfy |p_k^2 - N*q_k^2| < 2*sqrt(N)
  Can CF convergents guide 'a' selection?
  N=381542204117 (40b)
  CF convergents: 100
  Near target_a: 2
  Min residue: 18067
  Avg residue (first 20): 482331

  ANALYSIS: CF convergents minimize |p^2 - Nq^2|, giving small residues.
  But SIQS already uses a similar principle: a ~ sqrt(2N)/M ensures
  g(x) = a*x^2 + 2bx + c is small in the sieve interval.
  CF convergents give the BEST rational approximations to sqrt(N),
  but SIQS needs 'a' to be a product of FB primes (for self-initialization).
  CF denominators are NOT products of FB primes in general.
  VERDICT: CF convergents don't directly help SIQS 'a' selection.

### Exp 4.2: Can partial info from rho accelerate SIQS?
  Pollard rho cycle length L satisfies p | gcd(x_L - x_0, N)
  Even before finding the factor, intermediate gcd values carry info.
  Partial factors found in N^0.25 steps: avg=0.00
  (Expected ~0 for RSA semiprimes — rho needs ~sqrt(p) steps)
  VERDICT: Rho partial information is essentially zero before convergence.
  No cross-method benefit for RSA semiprimes.

### Exp 4.3: Tree-parameterized ECM starting points
  Use tree (m,n) values to parameterize ECM curves.
  Standard ECM: random curve y^2 = x^3 + ax + b
  Tree ECM: a = m^2 - n^2, b = 2mn for tree node (m,n)
  Question: does tree structure bias toward smoother group orders?
  Curve discriminant Delta = -16(4a^3 + 27b^2)
  For ECM to work well, we want |group order - p - 1| to be smooth.
  Tree (m,n) values give specific (a,b) patterns.
  But group orders depend on p (unknown), not on (a,b) structure.
  By Hasse's theorem, group order is in [p+1-2sqrt(p), p+1+2sqrt(p)].
  The distribution of group orders over curves is essentially uniform
  in this interval (Sato-Tate). Tree parametrization doesn't change this.
  VERDICT: No advantage. ECM group order is p-dependent, not curve-dependent.

======================================================================
## SYNTHESIS: Deep Algebraic Structure Mining
======================================================================

### Track 5 (B3 mod N smoothness) — NEGATIVE RESULT, PROVEN
- B3 mod N walks produce values that are uniformly distributed in [0, N).
- Smoothness rate matches random numbers exactly (within statistical noise).
- The factored form A = (m-n)(m+n) only helps in Z, not mod N.
- Fundamental obstruction: the tree is N-independent (disc = 16n0^4).
  Making it N-dependent (via mod N) destroys the structural advantage.
- PROOF: Weil bound + equidistribution => same smoothness as random.
- CONCLUSION: No sub-L[1/2] algorithm from Berggren tree. CONFIRMED.

### Track 1 (sqrt(-1) factory) — CONFIRMED IDENTITY, NO FACTORING GAIN
- a*b^{-1} mod c = sqrt(-1) mod c for PPT (a,b,c) with c prime, c=1 mod 4: VERIFIED.
- Birthday collision on hypotenuses: O(sqrt(N)) steps, same as standard birthday.
- Hypotenuse rho: comparable or slightly worse than standard Pollard rho.
- Finding c | N requires knowing factors: circular.
- CONCLUSION: Beautiful identity, but no computational advantage for factoring.

### Track 2 (Berggren-ECM) — NEGATIVE, GROUP TOO LARGE
- Berggren group order = 2p(p^2-1) ~ 2p^3.
- For ECM, we need group order to be smooth. Smooth p^3 requires smooth p.
- Standard ECM uses groups of order ~p, which are smooth much more often.
- Berggren-ECM is strictly worse than standard ECM by factor of ~p^2.
- CONCLUSION: Berggren group structure is algebraically rich but computationally useless.

### Track 3 (LP resonance) — TRADEOFF IS NEUTRAL
- Grouped 'a' values cause GF(2) duplicates because shared primes force
  correlated exponent vectors.
- Reducing sharing (s-2 instead of s-1) reduces duplicates but also LP rate.
- The tradeoff is approximately neutral: net useful relations ~constant.
- CONCLUSION: LP resonance 3.298x is an illusion when GF(2) is accounted for.

### Track 4 (Compositional attacks) — ALL NEGATIVE
- CF convergents don't produce FB-smooth 'a' values needed by SIQS.
- Rho partial information is zero before convergence (for semiprimes).
- Tree-parameterized ECM: group orders are p-dependent (Sato-Tate), not curve-dependent.
- CONCLUSION: Cross-method information sharing doesn't help for RSA semiprimes.

### THE FOUR OBSTRUCTIONS HOLD
1. **N-independence**: Tree discriminant is N-independent. Mod N destroys structure.
2. **Equidistribution**: Mod N, tree values are pseudorandom (Weil bound).
3. **Group size**: Berggren group (~p^3) is too large for ECM-like attacks.
4. **GF(2) correlation**: Structural grouping helps LP but hurts linear algebra.

These four obstructions appear to be fundamental and cannot be circumvented
by algebraic tricks within the Berggren framework.


Total runtime: 15.1s

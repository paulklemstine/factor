# Moonshot Ideas: Pythagorean Tree Factoring

Generated 2026-03-14 by MOONSHOT agent.

Status key: each idea rated by (chance of working) x (impact if it works).

---

## 1. Pollard Rho ON the Pythagorean Tree

**Core insight**: Instead of checking gcd(derived_value, N) at every node (O(p) barrier), run a Pollard-rho-style collision search where two walks on the tree collide mod p but not mod q. This achieves O(sqrt(p)) birthday bound.

**How it works**: Launch two walks (slow/fast or multi-start). At each node, compute a single "fingerprint" f(m,n) = m^2 + n^2 mod N (the hypotenuse C). Accumulate the product of (f_slow - f_fast) mod N into a batch GCD accumulator. When two walks visit nodes where C_1 = C_2 mod p (but C_1 != C_2 mod q), the difference is divisible by p but not N. This is exactly the Pollard rho birthday trick, but the random walk happens on the Pythagorean tree instead of Z_N.

**Why it might work**: The 9-ary tree mod p has ~p nodes in each coordinate. The derived values (A, B, C, m, n, ...) give us ~12 independent hash-like quantities per node. If the walk mixes well mod p, we get birthday collisions after O(sqrt(p)) steps. With 12 derived values per node, the effective "birthday space" is 12x larger, potentially reducing steps to O(sqrt(p/12)). At 50M steps/sec in C, this would handle 32-bit factors (p ~ 2^32) in ~1 second.

**Why it might fail**: The tree walk may not mix well mod p. The 9 matrices generate a specific subgroup of GL(2, Z_p), which might be much smaller than Z_p x Z_p, creating short cycles that miss most of the space. Also, if two walks follow correlated paths (same matrix choices), their derived values are algebraically related, destroying the independence assumption.

**Key design choices**:
- Use the (m mod N, n mod N) infrastructure from `pyth_deep_mod.c` -- already done
- Fingerprint function: try C = m^2+n^2, or m*n, or m-n -- want maximum "randomness" mod p
- Walk function: deterministic from fingerprint (e.g., matrix_index = fingerprint % 9) for cycle detection
- Distinguished points: only check gcd when fingerprint has k leading zero bits

**Estimated effort**: 1-2 days. Modify `deep_random_walk` in pyth_deep_mod.c to run two parallel walks with accumulator on differences.

---

## 2. Multi-Dimensional Birthday Attack (12-value Hyperplane Intersection)

**Core insight**: Each tree node produces 12 derived values mod N. Instead of checking each individually (O(p) per value), look for two nodes where ANY of the 12 values collide mod p. This is a multi-dimensional birthday problem with collision probability ~12^2/p per pair, giving O(sqrt(p)/12) expected steps.

**How it works**: Store fingerprints of visited nodes in a hash table keyed by (derived_value_index, value mod 2^k) for some truncation k. When a new node's derived value lands in an occupied bucket, compute gcd(v_new - v_old, N). The truncation reduces memory while maintaining collision detection.

**Why it might work**: With 12 derived values, each node "occupies" 12 buckets in the hash table. Two nodes collide if ANY of their 144 value-pairs match mod p. This is a 144x speedup over single-value birthday, or equivalently sqrt(144) = 12x fewer steps needed. Combined with 50M nodes/sec throughput, this could reach 40-bit factors.

**Why it might fail**: The 12 derived values are NOT independent -- they're all polynomial functions of (m, n). So the "144 independent chances" is an overcount. In the worst case, all 12 values are determined by (m mod p, n mod p), giving only a 2D birthday (sqrt(p) regardless of derived count). However, the derived values DO live in different polynomial orbits, so partial independence should still help.

**Variant -- Cross-walk collisions**: Run K independent walks. For each new node on walk i, check all 12 values against ALL stored values from walks 1..K. With K walks, collision probability per step grows as K*12, giving O(sqrt(p)/(K*12)) steps per walk, or O(sqrt(p)*K/(K*12)) = O(sqrt(p)/12) total steps. The K walks are embarrassingly parallel.

**Estimated effort**: 2-3 days. Need a fast hash table (robin-hood or cuckoo) storing (walk_id, derived_index, truncated_value) -> full_value. Check collisions on insert.

---

## 3. Spectral Gap Amplification (Expander Walk)

**Core insight**: The 9 Berggren/Price/Firstov matrices generate a group action on (Z_p)^2. If this Cayley graph is an expander (large spectral gap), then a random walk mixes in O(log p) steps. We can exploit this by doing short walks from MANY random starting points rather than one long walk.

**How it works**:
1. Compute (or estimate) the spectral gap of the 9-generator Cayley graph on (Z_p)^2 for small test primes.
2. If the gap is large (say > 0.1), then O(log p) steps suffice to reach a nearly-uniform distribution on the orbit.
3. Strategy: do sqrt(p) independent short walks of length O(log p) each, collecting one derived value from each. Birthday among these sqrt(p) values finds a collision in O(sqrt(p)) total values but only O(sqrt(p) * log(p)) matrix multiplications.

**Why it might work**: Cayley graphs of SL(2, Z_p) with standard generators are known to be Ramanujan expanders (Lubotzky-Phillips-Sarnak). The Pythagorean matrices live in GL(2, Z) and their images mod p generate a subgroup of GL(2, Z_p). If this subgroup is all of SL(2, Z_p) (or close to it), we inherit the expander property. The mixing time would be O(log p), making short walks optimal.

**Why it might fail**: The Pythagorean matrices might generate a PROPER subgroup of SL(2, Z_p) for some primes p. The subgroup depends on p -- for some primes the orbit might be tiny (bad), for others it might be the full group (good). Need to empirically test orbit sizes for small primes first.

**Diagnostic experiment**: For p = 101, 1009, 10007, enumerate the orbit of (2,1) under all 9 matrices mod p. If orbit size ~ p^2, the group is probably SL(2, Z_p) and expander mixing applies. If orbit size << p^2, the group is a small subgroup and this approach fails.

**Estimated effort**: 1 day for diagnostic, 2-3 days for full implementation if diagnostic passes.

---

## 4. Lattice Reduction on Accumulated Coordinates

**Core insight**: After walking K steps on the tree mod N, we have K points (m_i, n_i) mod N. These points satisfy polynomial relations (from the matrix recurrences). Construct a lattice from these relations and apply LLL -- short vectors in the lattice correspond to factorizations of N.

**How it works**: Each matrix step gives a linear relation: (m_{i+1}, n_{i+1}) = M_i * (m_i, n_i) mod N. After K steps, we have the relation (m_K, n_K) = (product of matrices) * (2, 1) mod N. Let P = product of matrices (computed without mod). Then m_K = P[0][0]*2 + P[0][1]*1 and m_K mod N = (m_K mod p) because gcd preserves. Form the lattice with rows:
```
[m_K, 1, 0]
[N,   0, 0]
[0,   0, C]  (for scaling)
```
LLL finds a short vector (a, b, 0) where a = m_K mod p (small) and b is a multiplier. Then gcd(a, N) might yield p.

**Why it might work**: After D steps on the tree, the true m_D has ~2^D bits, but m_D mod N is small. The lattice encodes the constraint "m_D = x mod N" and LLL can find x if it's much smaller than N. This is essentially Coppersmith's method applied to the Pythagorean recurrence. If m_D mod p happens to be small (because the orbit mod p has short period), LLL would find it.

**Why it might fail**: m_D mod p has no reason to be small -- it's a random element of Z_p. Coppersmith-style attacks require that the target value is smaller than N^{1/d} for polynomial degree d. Here d=1 (linear relation), so we need m_D mod p < N^{1/2}, which is basically always true (p < sqrt(N) for balanced factors). But the lattice dimension is only 2, so LLL gives us nothing beyond what we could compute directly. Would need higher-dimensional lattices from multiple walks or higher-degree polynomial relations.

**Improvement**: Collect MANY short walks and form a higher-dimensional lattice. From K walks of length D, get K linear constraints modulo N. Build a K-dimensional lattice. If any walk happens to have a particularly small orbit mod p, the lattice will find it.

**Estimated effort**: 2-3 days. Need to interface with fpLLL or use gmpy2 for lattice reduction.

---

## 5. Modular Group Connection (SL(2,Z) / Hyperbolic Geometry)

**Core insight**: The Pythagorean matrices act on the upper half-plane H via Mobius transformations z -> (az+b)/(cz+d). The tree structure corresponds to a tessellation of H. Factoring N corresponds to finding a geodesic that separates the "p-world" from the "q-world."

**How it works**:
1. View (m, n) as the complex number z = m/n in the upper half-plane (or more precisely, z = (m + ni)/n for valid Pythagorean generators).
2. Each matrix M acts as a Mobius transformation on z. The orbit of z_0 = 2/1 = 2 under the group generated by the 9 matrices traces a path in H.
3. Working mod N is equivalent to working in H_p x H_q (product of two half-planes). A "factoring geodesic" is one where the p-component and q-component diverge.
4. Key idea: compute the CONTINUED FRACTION expansion of m_D/n_D mod N. The convergents of this CF give small rational approximations to m/n mod p. If p | (convergent_numerator), we win.

**Why it might work**: The connection between SL(2,Z), continued fractions, and the Stern-Brocot tree is classical. The Pythagorean tree is a subtree of the Stern-Brocot tree (roughly). Continued fraction algorithms (CFRAC) are known to be effective for factoring. This approach would naturally connect Pythagorean tree navigation to CFRAC-style factoring.

**Why it might fail**: The Pythagorean tree is NOT a subtree of the Stern-Brocot tree -- the matrices are different. The connection to continued fractions is only analogical, not exact. Also, CFRAC factoring requires smooth values, which is a different mechanism than what we're doing.

**Concrete experiment**: Compute m_D/n_D mod N for deep walks. Take the continued fraction expansion of this rational number (using the Euclidean algorithm on m_D and n_D viewed as integers mod N, i.e., m_D * n_D^{-1} mod N). Check if any convergent denominators share a factor with N.

**Estimated effort**: 1 day for the CF experiment. Full SL(2,Z) framework: 1 week.

---

## 6. Resonance Interference (Phase-Coherent Multi-Walk)

**Core insight**: Launch K walks that start at the same point but use different matrix sequences. Compute a "phase" for each walk: phi_k = (m_k^2 + n_k^2) mod N. When walks are "in phase" mod p (phi_i = phi_j mod p), their phase difference is divisible by p. This is birthday + constructive interference.

**How it works**:
1. Start K = sqrt(p) walks from (2, 1) mod N.
2. Walk k uses matrix sequence determined by a pseudorandom function seeded by k.
3. After each step, compute phase = C mod N = (m^2 + n^2) mod N for each walk.
4. Store phases in a hash table. On collision (phi_i = phi_j), compute gcd(phi_i - phi_j, N) -- wait, they're equal mod N so this gives 0.

**Fix**: Use two DIFFERENT derived values. Walk i stores (A_i mod N, B_i mod N). Walk j stores the same. If A_i = A_j mod p but A_i != A_j mod N, then gcd(A_i - A_j, N) = p. This requires that A_i != A_j mod q, which happens with probability (1 - 1/q) ~ 1.

**Alternatively -- Phase ACCUMULATION**: Each walk accumulates a running product: prod_k = product of C_step for all steps. After D steps, prod_k is a big product mod N. If walk i and walk j happen to have the same product mod p, their difference reveals p. Since each product is essentially random mod p (if walk mixes), this is birthday with O(sqrt(p)) walks.

**Why it might work**: This is essentially multi-start Pollard rho, but the "random function" is the Pythagorean tree walk. The tree structure might create correlations that HELP (similar to Pollard's p-1 exploiting smooth group order). If the tree walk has short cycles mod p for certain primes, the accumulated products will be periodic, creating extra collisions.

**Why it might fail**: Memory. Storing sqrt(p) phases requires O(sqrt(p)) memory. For p ~ 2^32, that's 64K entries (fine). For p ~ 2^64, that's 4B entries (problematic). Also, if the walks don't mix well, phases are correlated and birthdays are suppressed.

**Estimated effort**: 2 days. Implement K parallel walks in C, hash table for phase collision detection.

---

## 7. Smooth Relation Harvesting (NFS Connection)

**Core insight**: Pythagorean triples (A, B, C) naturally produce multiplicative relations. If A = m^2 - n^2 = (m-n)(m+n) is smooth, and B = 2mn is smooth, then we have a smooth relation involving m, n, m-n, m+n. Collect enough smooth relations and solve a linear system over GF(2) to find a square congruence, exactly like GNFS.

**How it works**:
1. Walk the Pythagorean tree (actual coordinates, not mod N).
2. At each node, compute A = m^2 - n^2, B = 2mn. Check if A*B mod N is smooth (all prime factors below bound B).
3. If smooth, record the factorization as a relation.
4. After collecting enough relations, solve the GF(2) exponent matrix to find a subset whose product is a perfect square.
5. Compute sqrt(product) mod N on both the "A-side" and "B-side" to get x^2 = y^2 mod N, yielding gcd(x-y, N).

**Why it might work**: This turns the Pythagorean tree into a RELATION GENERATOR for a sieve-based method. The key advantage: A = (m-n)(m+n) is ALREADY partially factored. If m-n and m+n are individually smooth, we get smoothness for free. The tree structure biases toward nodes where m and n have special forms (products of small transformations), which might favor smoothness.

**Why it might fail**: The Pythagorean tree values grow exponentially with depth. At depth D, m ~ 3^D, so A ~ 9^D. Smoothness probability for a number of size L with bound B is u^{-u} where u = log(L)/log(B). For deep tree nodes, L is enormous and smoothness probability is negligible. We'd need to stay at shallow depth, but shallow nodes are few and don't provide enough relations.

**Rescue idea**: Work mod N. The value A*B mod N is bounded by N, regardless of tree depth. Check smoothness of (A*B mod N) rather than A*B itself. This is exactly what GNFS does with its polynomial evaluation. The Pythagorean recurrence gives us a natural polynomial family to evaluate.

**Estimated effort**: 3-5 days. This is essentially building a mini-GNFS with Pythagorean polynomials. Could leverage existing GNFS infrastructure in gnfs_engine.py.

---

## 8. Deterministic Orbit Period Attack

**Core insight**: For each matrix M, the orbit of (2,1) under repeated application of M mod p has some period T_p. Similarly mod q, period T_q. The period mod N is lcm(T_p, T_q). If we can find T_N (by detecting cycles mod N) and factor it, we might recover T_p or T_q, yielding p or q.

**How it works**:
1. For each of the 9 matrices, detect the cycle length T_N of (2,1) under M^k mod N using Brent's algorithm (already implemented in `pyth_deep_mod.c`).
2. T_N = lcm(T_p, T_q). Factor T_N.
3. For each divisor d of T_N, compute M^d * (2,1) mod N. Check if the result equals (2,1) mod N. If M^d * (2,1) = (2,1) mod N but M^d != I mod N, then (M^d - I) has a kernel that factors N.
4. More precisely: compute gcd(m_d - 2, N) and gcd(n_d - 1, N) for each divisor d.

**Why it might work**: This is a generalization of the Pollard p-1 attack. If T_p | d but T_q does not divide d, then M^d * (2,1) = (2,1) mod p but != (2,1) mod q, so gcd(m_d - 2, N) = p. The current `smooth_exponent_attack` already does something similar (raising M to a smooth exponent), but it only finds factors where T_p is smooth. This approach finds factors where T_p has ANY non-trivial factorization that makes it a proper divisor of T_N.

**Why it might fail**: Finding T_N requires O(T_N) steps (Brent's algorithm). T_N = lcm(T_p, T_q) could be as large as T_p * T_q. For random matrices mod p, the orbit period is typically O(p), so T_N ~ p*q = N. Detecting a cycle of length N is infeasible. However, for SPECIFIC matrices, the period might be much shorter (related to the matrix's eigenvalues in F_p).

**Special matrices to try**: The matrix [[2,-1],[1,0]] has characteristic polynomial x^2 - 2x + 1 = (x-1)^2. Over F_p, this is nilpotent (eigenvalue 1 with multiplicity 2). The orbit period divides p (not p^2) because (M-I)^2 = 0 over F_p. So T_p | p, and T_q | q, giving T_N | lcm(p, q). If p != q, then lcm(p,q) = p*q = N, which is still too large. But for OTHER matrices with distinct eigenvalues, the period divides p-1 or p+1 (depending on whether eigenvalues are in F_p or F_{p^2}), connecting directly to Pollard p-1 and Williams p+1.

**Estimated effort**: 1 day. The Brent cycle detection is already implemented. Just need to add the divisor-testing phase.

---

## 9. Quantum-Inspired Grover Walk (Classical Amplitude Amplification)

**Core insight**: Grover's algorithm amplifies the amplitude of "marked" states quadratically. Classically, we can't do true amplitude amplification, but we can simulate it via IMPORTANCE SAMPLING: bias the walk toward states that "look promising" using a learned value function, while maintaining theoretical guarantees via rejection sampling.

**How it works**:
1. Train a fast neural network (or lookup table) V(m mod H, n mod H) that predicts "probability of finding a factor within K steps from state (m,n)."
2. Use V as a proposal distribution: at each step, compute V for all 9 children and sample proportional to exp(V/T).
3. Crucially, maintain a WEIGHT for the walk: w *= P_uniform / P_proposal. This importance weight corrects for the bias.
4. When checking gcd, weight the contribution by w. This gives an unbiased estimator of "factor found" while concentrating samples in promising regions.

**Simpler version -- Stratified sampling**: Divide the state space (Z_N)^2 into strata based on (m mod S, n mod S) for small S. Allocate more walk budget to strata that historically yield better scent values. This is a classical version of amplitude amplification: spend more time where the target is more likely.

**Why it might work**: The current beam search already uses heuristic scoring (quad_res scent). This formalizes it with proper importance weighting, ensuring we don't miss factors in "unlikely" regions while still concentrating effort in promising ones. If the value function is good (even 2x better than uniform), we get a 2x speedup for free.

**Why it might fail**: Learning V requires solving the very problem we're trying to solve. Bootstrap issue. Also, importance sampling has high variance when the proposal distribution is far from the target, which can make it worse than uniform sampling.

**Estimated effort**: 3-4 days. Need to implement importance-weighted walks + lightweight value function.

---

## 10. Eigenvalue Sieve (Spectral Fingerprinting)

**Core insight**: Each of the 9 matrices M_i has eigenvalues lambda_1, lambda_2 over F_p and over F_q. The characteristic polynomial of M_i is degree 2 with integer coefficients, so its roots mod p and mod q can be computed IF we know p and q. Flip this: the ORBIT STRUCTURE (periods, fixed points) of M_i mod N encodes information about the eigenvalues mod p and mod q, which encodes information about p and q.

**How it works**:
1. For each matrix M_i, compute: M_i^k * (2,1) mod N for k = 1, 2, ..., K.
2. Record the sequence of (m_k mod small_prime) for several small primes. This gives "spectral fingerprints."
3. The orbit of M_i mod p has period dividing p^2 - 1 (if eigenvalues are in F_{p^2}) or (p-1)^2 (if eigenvalues are in F_p). Different primes p give different periods.
4. By analyzing the fingerprints (e.g., autocorrelation of the sequence), infer constraints on p mod small_primes.
5. Use CRT to reconstruct p from enough constraints.

**Why it might work**: This is a spectral version of index calculus. The eigenvalues of 2x2 matrices over finite fields are well-understood (they involve quadratic residues). The orbit period of M mod p is closely related to the multiplicative order of the eigenvalues, which connects to discrete logarithm structure. If we can extract even partial information about the eigenvalue orders, we learn bits of p.

**Why it might fail**: We can't compute "mod p" because we don't know p. Everything is mod N. The spectral information mod p and mod q are entangled via CRT, making extraction hard. Also, autocorrelation analysis requires O(T_p) samples to detect periodicity T_p, which is back to O(p).

**Possible rescue**: Use MULTIPLE matrices simultaneously. The eigenvalues of different matrices mod p satisfy algebraic relations (they all live in the same field F_p). Cross-correlating orbits of different matrices might reveal p faster than analyzing each alone.

**Estimated effort**: 3-5 days. Significant mathematical analysis needed.

---

## 11. Fibonacci/Lucas Connection (Specific Matrix Families)

**Core insight**: The matrix [[2,1],[1,0]] generates a sequence closely related to Pell numbers (solutions to x^2 - 2y^2 = 1). The matrix [[1,1],[1,0]] generates Fibonacci numbers. Lucas-style primality/factoring tests exploit the algebraic properties of these sequences. Can we do the same with Pythagorean matrices?

**How it works**: The Berggren matrix B2 = [[2,1],[1,0]] has characteristic polynomial x^2 - 2x - 1, with roots 1 +/- sqrt(2). Over F_p:
- If 2 is a QR mod p, the roots are in F_p, and the orbit period divides p-1.
- If 2 is a QNR mod p, the roots are in F_{p^2}, and the orbit period divides p+1.

This is exactly the Williams p+1 criterion! So B2 gives us p+1 attack when 2 is QNR mod p, and p-1 attack when 2 is QR mod p. Similarly for other matrices with different discriminants.

**Enhancement**: Use ALL 9 matrices. Each has a different characteristic polynomial with different discriminant. Matrix M_i succeeds when its discriminant is a QNR mod p (giving p+1-type period) or QR mod p (giving p-1-type period). By trying all 9, we cover more cases.

**Current status**: The `smooth_exponent_attack` already does this for all 9 matrices. The `parametric_family` extends to M(t) = [[t,1],[1,0]] with discriminant t^2+4.

**New idea -- Discriminant farming**: Instead of just 9 matrices, generate HUNDREDS of matrices with carefully chosen discriminants. For each small prime q, include a matrix whose discriminant is q. Then: for any prime p, at least one matrix will have discriminant that is QNR mod p (by quadratic reciprocity), giving a p+1-style attack. With enough discriminants, the probability of ALL of them failing (i.e., p+1 and p-1 both having a large prime factor for EVERY discriminant) becomes tiny.

**Why it might work**: This is a known technique (ECM uses it implicitly by trying many curves). The question is whether the Pythagorean framework can generate enough distinct discriminants cheaply. Since each 2x2 integer matrix gives a discriminant, and we can generate millions of matrices cheaply, the discriminant coverage could be excellent.

**Why it might fail**: The smooth exponent attack already handles the smooth-p+/-1 case well (14/15 at 40b). The hard cases are where p-1 and p+1 both have large prime factors. For these, no amount of discriminant farming helps (you'd need the large prime factor to appear in SOME order, which requires factoring it).

**Estimated effort**: 1 day. Just extend `parametric_family` to try more values of t, and also try [[a,b],[c,d]] for various small (a,b,c,d).

---

## 12. Pythagorean Tree as a Pseudo-Random Function Family

**Core insight**: A walk of length D on the 9-ary tree is specified by a "path word" w in {0,1,...,8}^D. The map w -> (m_w, n_w) mod N is a pseudorandom function if the tree mixes well. Use this PRF to build a COLLISION-FINDING ENGINE: hash table of (fingerprint -> path_word), detect collisions mod p.

**How it works**:
1. Generate path words w_1, w_2, ..., w_K of fixed length D.
2. For each w_i, compute (m_i, n_i) mod N by applying the corresponding matrix product.
3. Compute fingerprint f_i = m_i mod 2^B for some bucket width B.
4. Store (f_i, i) in hash table. On collision f_i = f_j, compute gcd(m_i - m_j, N).
5. If m_i = m_j mod p (the collision is real mod p, not just truncation), then gcd gives p.

**Optimization -- Tree compression**: Don't store all path words. Use Floyd's or Brent's cycle detection on a deterministic walk defined by f: (m, n) -> apply_matrix(m mod 9, (m, n)). The walk visits O(sqrt(p)) distinct states before cycling mod p, and cycle detection finds the collision in O(sqrt(p)) time and O(1) memory.

**Why this is different from idea 1**: Idea 1 uses the derived values (A, B, C, ...) for collision. This idea uses the raw (m, n) coordinates. The advantage: (m, n) mod p is a 2D random variable with p^2 possible values. Two walks collide in m mod p with probability 1/p per step. With K walks, collision after O(p/K) steps each, or O(p) total -- no birthday improvement in m alone. BUT: if we look for collisions in m AND n simultaneously (same (m,n) mod p), we get collisions after O(p) nodes total (birthday in a p^2 space gives sqrt(p^2) = p). This is no better than direct gcd checking.

**Rescue -- Use derived value as walk function**: Make the walk function depend on a derived value, not on m directly. Then the walk's cycle structure mod p depends on the derived value's algebraic properties, and we might get lucky with short cycles.

**Estimated effort**: 1 day. Mostly a variant of the existing Brent cycle detection.

---

## 13. Matrix Commutator Attack

**Core insight**: For two matrices A, B, their commutator [A,B] = ABA^{-1}B^{-1} measures "how non-abelian" the group is. Over F_p, if [A,B] has order dividing some smooth number, the commutator orbit is short, and we can detect this.

**How it works**:
1. Pick pairs of Pythagorean matrices (M_i, M_j).
2. Compute the commutator C_{ij} = M_i * M_j * M_i^{-1} * M_j^{-1} mod N.
3. Raise C_{ij} to a smooth exponent E (product of prime powers up to bound B1).
4. Check if C_{ij}^E * (2,1) = (2,1) mod N (or more precisely, check gcd of differences).
5. If the commutator has smooth order mod p, this reveals p.

**Why it might work**: The commutator of two elements in GL(2, F_p) lies in SL(2, F_p). The order of elements in SL(2, F_p) divides p^2 - 1 (they satisfy their characteristic polynomial, whose roots are in F_{p^2}). If p^2 - 1 happens to be smooth (rare but possible), the commutator attack works. More interestingly, the commutator has TRACE = 2 + trace([A,B]-I), which might give extra algebraic structure to exploit.

**Why it might fail**: Commutator orders are no more likely to be smooth than orbit periods, so this doesn't improve on the basic smooth-exponent attack. Also, computing commutators requires matrix inverses, which are a bit more work (though cheap mod N with extended GCD on the 2x2 determinant).

**Estimated effort**: 1 day. Straightforward extension of smooth_exponent_attack.

---

## 14. Algebraic Norm Sieve on the Gaussian Integers

**Core insight**: Pythagorean triples correspond to Gaussian integer factorizations: A + Bi = (m + ni)(m - ni) * (1+i). The norm N(m+ni) = m^2 + n^2 = C (the hypotenuse). If we work in Z[i] rather than Z, the factoring problem becomes: find a Gaussian integer z such that N(z) = 0 mod p. This is equivalent to finding (m,n) such that m^2 + n^2 = 0 mod p.

**How it works**:
1. Note that m^2 + n^2 = 0 mod p iff m/n = +/- i mod p (where i = sqrt(-1) mod p, exists iff p = 1 mod 4).
2. So we need m = i*n mod p (or m = -i*n mod p), i.e., m - i*n = 0 mod p in Z[i].
3. The Pythagorean tree walk generates (m, n) mod N. Compute C = m^2 + n^2 mod N at each step.
4. If C = 0 mod p but C != 0 mod q, then gcd(C, N) = p. But C = 0 mod p happens with probability 1/p (since we need m/n = +/-i mod p), so this is O(p) expected steps.
5. Birthday improvement: collect many C values and look for C_j - C_k = 0 mod p, i.e., gcd(C_j - C_k, N) != 1. This gives O(sqrt(p)) by birthday.

**Why it might work**: The Gaussian integer viewpoint gives a CLEAN algebraic interpretation of what the Pythagorean tree walk is doing. It also suggests using algebraic number field sieve ideas: instead of Z[i], work in Z[sqrt(d)] for various d, where each quadratic field gives a different "channel" for detecting factors.

**Extension -- Multi-field sieve**: For each Pythagorean triple (A, B, C):
- Z[i]: norm = C = m^2 + n^2
- Z[sqrt(2)]: norm = A = m^2 - n^2 (since A = (m-n)(m+n))
- Z[sqrt(-2)]: norm = 2m^2 + 2n^2 (related to B = 2mn)

Collect smooth norms across multiple quadratic fields simultaneously. If a triple has smooth norms in two different fields, it provides a relation for the factor base.

**Why it might fail**: The birthday-on-C-values approach IS the same as idea 1 (Pollard rho on derived value C). The Gaussian integer viewpoint is elegant but doesn't give computational advantage. The multi-field extension is essentially GNFS with algebraic number fields, which is already the state of the art.

**Estimated effort**: 1 day for basic C-value birthday. 1 week for multi-field sieve (overlaps with GNFS work).

---

## 15. Kangaroo Method on the Pythagorean Tree

**Core insight**: Pollard's kangaroo method finds discrete logarithms by having a "tame" kangaroo (known starting point) and "wild" kangaroo (unknown starting point) take jumps of size determined by their current position. When they collide, the DLP is solved. Adapt this: the "tame" walk starts from (2,1), the "wild" walk starts from (2,1) but applies matrices IN REVERSE ORDER. When they meet, the forward and reverse paths give a factorization.

**How it works**:
1. Tame walk: from (2,1), apply random forward matrices. At step T, state is (m_T, n_T) = Product(M_{i_k}) * (2, 1) mod N.
2. Wild walk: from (2,1), apply random INVERSE matrices (going "up" the tree). At step W, state is (m_W, n_W) = Product(M^{-1}_{j_k}) * (2, 1) mod N.
3. If the tame walk at step T reaches the same (m, n) mod p as the wild walk at step W, then Product(M_{i_k}) * (2,1) = Product(M^{-1}_{j_k}) * (2,1) mod p, meaning Product(M_{i_k}) * Product(M_{j_k}) * (2,1) = (2,1) mod p. This gives us the ORDER of a group element mod p.
4. Check gcd((m_T - m_W) mod N, N).

**Why it might work**: Kangaroo methods are proven O(sqrt(p)) for 1D discrete log. The Pythagorean tree is a higher-dimensional structure, but the kangaroo principle (distinguished points + collision detection) still applies. The key advantage over plain rho: kangaroo can be parallelized with linear speedup across multiple processors.

**Why it might fail**: The inverse matrices only go "up" the tree (toward the root), so the wild walk quickly hits (2,1) and gets stuck. In the modular setting this doesn't apply (we're working mod N, so there's no "root" and inverse matrices are just more group operations). But the 3 inverse matrices generate a different (possibly smaller) subgroup than the 9 forward matrices, which could limit coverage.

**Fix**: Use all 12 matrices (9 forward + 3 inverse) for BOTH walks. The walks differ by seed/starting-point, not by matrix set.

**Estimated effort**: 2 days. Need distinguished-point infrastructure (hash table keyed on dp-mask of (m,n) mod N).

---

## Priority Ranking

| Rank | Idea | Chance | Impact | Effort |
|------|------|--------|--------|--------|
| 1 | Pollard Rho ON tree (#1) | 40% | High (O(sqrt(p))) | 1-2d |
| 2 | Multi-dim birthday (#2) | 30% | High (12x speedup) | 2-3d |
| 3 | Spectral gap / expander (#3) | 25% | Very High (O(sqrt(p)*log(p))) | 1d diag + 2-3d |
| 4 | Discriminant farming (#11) | 50% | Medium (covers more p+/-1) | 1d |
| 5 | Kangaroo method (#15) | 35% | High (parallelizable sqrt(p)) | 2d |
| 6 | Orbit period attack (#8) | 20% | Medium (handles special p) | 1d |
| 7 | Resonance interference (#6) | 20% | Medium (K-walk birthday) | 2d |
| 8 | Smooth relation harvest (#7) | 15% | Very High (sub-exponential!) | 3-5d |
| 9 | Lattice reduction (#4) | 15% | High (new approach) | 2-3d |
| 10 | Modular group / CF (#5) | 10% | High (CFRAC connection) | 1d exp + 1w full |

**Recommended first experiment**: Idea #3 diagnostic (1 day). Enumerate orbit sizes of (2,1) under all 9 matrices for p = 101, 1009, 10007, 100003. If ANY matrix generates full or near-full orbits, the expander approach is viable and ideas #1, #2, #6, #15 all benefit from good mixing.

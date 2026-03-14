# Pythagorean Tree Factoring -- Prioritized Experiment List

Generated: 2026-03-14

## Summary of Current State

**What works well (O(p) regime, balanced primes):**
- C forward beam v4: 2.5M nodes/sec, 15/15 at 28b, 9/15 at 32b
- Throughput dominates heuristic quality at 32b+

**What works well (catches unbalanced primes / Williams p+1 analog):**
- Smooth exponent (B1=1K): 14/15 at 40b, 13/15 at 48b
- Matrix power M^(2^k): 11/15 at 40b, 11/15 at 48b
- Parametric family (500 curves): 13/15 at 40b, 12/15 at 48b

**Fundamental barrier:** Each tree node hits a factor with probability ~1/p.
Even with 12 derived values and ~6x scent amplification, balanced-prime
search is O(p). Breaking through to O(sqrt(p)) is the critical challenge.

**Key infrastructure already in place:**
- Modular (m,n) tracking: unlimited depth, no bignums (pyth_deep_mod.c)
- 2x2 matrix orbit machinery: single-matrix iteration, power jump, Brent cycle
- Batch GCD accumulation (Pollard-rho style product)
- 9 forward + 3 inverse matrices (Berggren + Price + Firstov families)

---

## TIER 1 -- Highest Priority (Birthday-bound / O(sqrt(p)) approaches)

### Experiment 1: Multi-Walk Distinguished Points Collision
**Priority: 1 | Difficulty: Medium | Expected: O(sqrt(p))**

**Theory:** Run K independent random walks on the Pythagorean tree mod N.
Each walk tracks (m_i, n_i) mod N. When two walks collide mod p (but not
mod q), their difference reveals p. This is the Pollard-rho birthday
principle applied to tree walks.

**Key insight:** We do NOT need to detect collisions between specific walk
pairs. Use *distinguished points*: whenever m mod 2^d == 0 (for some d),
store (m, n, walk_id) in a hash table. Two walks that collide mod p will
eventually hit the same distinguished point mod p, producing a table match
where gcd(m1 - m2, N) yields the factor.

**Implementation:**
- Run W=32 or 64 walks in parallel (each with independent random seed)
- Each walk applies a random forward matrix at each step
- Check m for distinguished-point property every step (just a bitmask check)
- On DP hit, store (m mod N, n mod N, walk_id) in hash table
- On table collision (same m,n from different walk), compute gcd(m1-m2, N)
  where m1, m2 are the FULL modular values from the two walks
- Expected steps to collision: O(sqrt(p)) per walk, so O(sqrt(p)) total
  with K walks running in parallel

**Why this is different from current batch GCD:** Batch GCD accumulates
derived values from a SINGLE walk. It only finds factors when a derived
value is 0 mod p, which is O(p). Distinguished-point collision finds factors
when two INDEPENDENT walks reach the same (m,n) mod p, which is O(sqrt(p))
by the birthday paradox.

**Critical detail:** The walks must use a DETERMINISTIC iteration function
f(m,n) -> (m',n') that depends only on (m mod N, n mod N), so that walks
that collide mod p will STAY synchronized. Random matrix choice must be
derived from the current state: e.g., matrix_idx = hash(m, n) % 9.

**Estimated speedup:** From O(p) to O(sqrt(p)), i.e., a 32b problem becomes
as easy as a 16b problem. Could push balanced-prime factoring to 48-64b.

---

### Experiment 2: Cycle-Length GCD (Pollard-Rho on Matrix Orbits)
**Priority: 1 | Difficulty: Easy | Expected: O(sqrt(p))**

**Theory:** For a single matrix M, the orbit of (m,n) under repeated
application of M has period L mod N. Crucially, L_p = period mod p and
L_q = period mod q are typically different. By Brent/Floyd cycle detection,
we find L mod N in O(L) steps. Then gcd(M^L - I, N) reveals a factor if
L_p divides L but L_q does not (or vice versa).

**The current Brent implementation (Experiment 2 in pyth_deep_mod.c)
already does this, but it only checks gcd of coordinate DIFFERENCES between
hare and tortoise.** The missing piece: when a cycle is detected (hare ==
tortoise mod N), we should compute gcd(hare_m - tortoise_m, N). If the
cycle lengths differ mod p and mod q, this gcd will be nontrivial.

**But the real O(sqrt(p)) trick:** Instead of finding the exact cycle
length, use the Pollard-rho approach: iterate f(x) = M*x and f(f(x)) = M^2*x,
check gcd(x_fast - x_slow, N) periodically. The collision happens at
O(sqrt(L_p)) steps, and L_p is typically O(p), giving O(sqrt(p)) total.

**Enhancement over current code:** The current Brent code in pyth_deep_mod.c
checks dm = hare_m - tort_m at every step. This is correct but may be
computing gcd too frequently (expensive). Batch the differences:
accumulate product of (hare_m - tort_m) values, check gcd every 1000 steps.
This turns the inner loop into pure matrix multiply + accumulate, which
is very fast.

**Implementation:**
- For each of the 9 matrices, run Brent's algorithm with batched gcd
- Accumulate product of (hare_m - tort_m) * (hare_n - tort_n) every step
- Check gcd every 1000 steps
- Try multiple starting points: (2,1), (3,1), (4,1), (5,2), etc.
- Time budget: ~1 second per matrix, 9 matrices = 9 seconds total

---

### Experiment 3: Multi-Matrix Pollard-Rho (Composition Walk)
**Priority: 1 | Difficulty: Medium | Expected: O(sqrt(p))**

**Theory:** Instead of iterating a single matrix, define a pseudo-random
iteration function that MIXES matrices based on the current state:

    matrix_idx = hash(m mod N, n mod N) % 9
    (m', n') = FORWARD[matrix_idx] * (m, n) mod N

This creates a pseudo-random walk on (Z/NZ)^2. By the birthday paradox,
two points in this walk will collide mod p after O(sqrt(p)) steps.

**Why mixing matrices helps:** A single matrix orbit is periodic with
period dividing |GL(2, Z/pZ)|, which could be very large or could have
special structure that prevents short cycles. A pseudo-random walk breaks
any algebraic structure and guarantees birthday-bound convergence.

**Implementation:**
- Hash function: h(m,n) = ((m * 0x9E3779B97F4A7C15) ^ (n * 0x517CC1B727220A95)) >> 60
  gives 4 bits, use low bits for matrix selection (% 9)
- Brent's cycle detection: tortoise/hare with power-of-2 checkpoints
- Batch GCD: accumulate product of (hare_m - tort_m) mod N
- This is essentially Pollard-rho but on the tree's modular walk instead
  of the standard x -> x^2 + c iteration

**Expected performance:** O(sqrt(p)) steps, each step is one matrix
multiply (6 multiplications mod N) + one accumulate. At ~100M steps/sec
in C, a 48b semiprime (p ~ 2^24) needs ~sqrt(2^24) = 4096 steps = instant.
A 64b semiprime (p ~ 2^32) needs ~65K steps = instant.
A 96b semiprime (p ~ 2^48) needs ~16M steps = 0.16 seconds.

---

## TIER 2 -- High Priority (Improve existing approaches)

### Experiment 4: ECM-Style Stage 2 for Smooth Exponent
**Priority: 2 | Difficulty: Medium | Expected: Doubles success rate**

**Theory:** The current smooth_exponent_attack computes M^E where E is
the product of prime powers up to B1. This catches primes p where
ord(M) mod p is B1-smooth. Adding a Stage 2 (like ECM) handles the case
where ord(M) mod p has exactly ONE large prime factor q in (B1, B2].

**Stage 2 algorithm:**
1. After Stage 1: have M^E * (2,1) = (m_E, n_E) mod N
2. Compute baby steps: S_j = M^(j * E) * (2,1) for j = 0, 1, ..., D-1
   where D = floor(sqrt(B2 - B1))
3. Compute giant steps: G_k = M^(k*D*E) * (2,1) for k = 1, 2, ..., ceil((B2-B1)/D)
4. For each giant step G_k, accumulate product of (G_k.m - S_j.m) for all j
5. Check gcd of accumulated product with N

**Expected impact:** With B1=1000 and B2=100000, Stage 2 costs only
O(sqrt(B2)) = ~316 extra matrix multiplies but covers primes with one
factor up to 100K. This could push success rate from 13-14/15 to 15/15
at 48b and extend the approach to 56-64b.

**Implementation note:** The baby-step/giant-step structure means we need
to store O(sqrt(B2)) intermediate (m,n) pairs -- about 316 pairs = trivial
memory.

---

### Experiment 5: Smooth Exponent with Multiple Starting Points
**Priority: 2 | Difficulty: Easy | Expected: +20-30% success rate**

**Theory:** Currently smooth_exponent tries each of the 9 forward matrices
starting from (m,n) = (2,1). But if ord(M) mod p is not B1-smooth for any
of the 9 matrices, we fail. Using multiple starting points (m0, n0)
effectively gives us independent "curves" (like ECM's multiple curves).

**Implementation:**
- Try starting points: (2,1), (3,1), (4,1), (5,1), (5,2), (7,3), etc.
- For each start, try all 9 matrices with smooth exponent
- 20 starts * 9 matrices = 180 independent attempts per N
- Each attempt is cheap (B1=1000 means ~170 matrix multiplies)

---

### Experiment 6: Parametric Family with Larger B1 and Stage 2
**Priority: 2 | Difficulty: Easy | Expected: Push to 56b+**

**Theory:** The parametric family M(t) = [[t,1],[1,0]] is essentially a
Williams p+1 method. Currently it uses B1=113 (only primes up to 113) and
t_max=500. Increasing B1 to 10000 and adding Stage 2 to B2=1M should
dramatically extend its range.

**Also try:** Different matrix families:
- M(t) = [[t, 2], [1, 0]]  (related to Lucas sequences of different kind)
- M(t) = [[t, 1], [1, t]]  (symmetric -- related to Chebyshev)
- M(t) = [[t, -1], [1, 0]]  (related to p-1 method)

Each family has different group-order conditions. Trying multiple families
is like running multiple ECM curves.

---

## TIER 3 -- Medium Priority (New structural insights)

### Experiment 7: Tree-Structured Random Walk with Backtracking
**Priority: 3 | Difficulty: Medium | Expected: O(sqrt(p)) if theory holds**

**Theory:** Instead of a linear random walk, maintain a stack-based walk.
At each node, pick a random child. Periodically (every ~sqrt(budget) steps),
backtrack to a random ancestor and take a different branch. This explores
a TREE of O(B) nodes but with O(B^2) PAIRWISE comparisons (birthday
among all visited nodes).

**Key insight:** Store a distinguished-point hash table. Every node visited
goes through the DP check. With B nodes explored, we get B^2/2 pair
comparisons, so we need B = O(sqrt(p)) nodes for a birthday collision.

**This is just Experiment 1 (distinguished points) implemented differently
-- using backtracking instead of parallel walks. Both achieve O(sqrt(p)).**

---

### Experiment 8: GCD of Matrix Entries Directly
**Priority: 3 | Difficulty: Easy | Expected: Might find new factor channels**

**Theory:** Currently we compute gcd of derived values (A, B, C, m, n,
m-n, m+n, etc.) with N. But the 2x2 matrix product M^k itself has entries
that grow and could share factors with N.

For the modular walk, compute M^k mod N. The matrix entries M^k.a00,
M^k.a01, M^k.a10, M^k.a11 are all values mod N. Check:
- gcd(M^k.a00, N)
- gcd(M^k.a01, N)
- gcd(M^k.a10, N)
- gcd(M^k.a11, N)
- gcd(M^k.a00 - 1, N)  (eigenvalue condition: M^k has eigenvalue 1 mod p)
- gcd(M^k.a00 + 1, N)  (eigenvalue condition: M^k has eigenvalue -1 mod p)
- gcd(det(M^k) - 1, N)  (determinant condition)
- gcd(trace(M^k) - 2, N) (trace = sum of eigenvalues, trace=2 means identity)

**The trace check is especially promising:** trace(M^k) = 2 mod p means
M^k = I mod p (if M is in SL(2,p)), which is exactly the condition for
the smooth exponent attack. But trace is a SINGLE number, so gcd is
cheaper than checking all derived values.

---

### Experiment 9: Lattice-Based Collision Detection
**Priority: 3 | Difficulty: Hard | Expected: O(sqrt(p)) with better constants**

**Theory:** Instead of hashing (m mod N, n mod N) for collision detection,
project onto a 1D value: v = a*m + b*n mod N for random (a,b). Two walks
colliding mod p will produce the same v mod p. This reduces storage from
2 words to 1 word per entry, doubling the number of walks we can track
in the same memory.

**Better yet:** Use multiple projections. For each walk step, compute
v1 = m mod N, v2 = n mod N, v3 = (m+n) mod N. If ANY of these collide
between two walks, we get a factor. This is 3x more collision channels
per step.

---

### Experiment 10: Product Tree GCD
**Priority: 3 | Difficulty: Medium | Expected: Constant-factor speedup**

**Theory:** Currently batch GCD accumulates a running product and checks
gcd(product, N) periodically. Problem: if TWO derived values are both
0 mod p (from different steps), their product is 0 mod p^2, which is fine.
But if one value is 0 mod p and another is 0 mod q, the product is 0 mod N,
giving the trivial factor.

**Fix:** Use a product tree. Split the batch into two halves. Check
gcd(product_left, N) and gcd(product_right, N) separately. If one gives N
(trivial), recurse into that half. This recovers the non-trivial factor
in O(log(batch_size)) extra gcds.

**Also:** Interleave multiple independent accumulators. Accumulator A gets
values from steps 0,2,4,... and accumulator B gets steps 1,3,5,... When
checking, compute gcd(A, N) and gcd(B, N) separately. If either is
nontrivial, we win. If both are trivial, the original combined product
was also trivial.

---

## TIER 4 -- Speculative (Might not work but worth trying)

### Experiment 11: Algebraic Group Structure Exploitation
**Priority: 4 | Difficulty: Hard | Expected: Unknown**

**Theory:** The 2x2 matrices act on (m,n) as elements of GL(2,Z).
Modulo a prime p, the group GL(2, Z/pZ) has order p(p-1)^2(p+1).
Subgroups have orders dividing this. If we can identify which subgroup
our matrices generate mod p, we can compute the group order and use it
directly (like Pohlig-Hellman for discrete log).

**Concrete approach:** For each matrix M_i, the order of M_i in GL(2, Z/pZ)
divides p(p-1)^2(p+1). Compute M_i^E where E = lcm of smooth parts of
{p-1, p+1, p^2-1}. If ord(M_i) | E, then M_i^E = I mod p, and we can
detect this via gcd(trace(M_i^E) - 2, N).

**This is essentially what smooth_exponent already does.** The theoretical
insight is that the group order factors as p * (p-1) * (p+1) * (p-1),
so the smooth exponent approach catches primes where (p-1) or (p+1) is
smooth. This explains why it works well for unbalanced factors (small p
means p-1 is more likely smooth).

---

### Experiment 12: Projective-Line Walk (PGL(2) action)
**Priority: 4 | Difficulty: Medium | Expected: Different orbit structure**

**Theory:** Instead of tracking (m, n) as a pair, track the ratio
r = m/n mod N (i.e., m * n^(-1) mod N). The matrix action becomes a
Mobius transformation: r' = (a*r + b) / (c*r + d) mod N.

**Advantage:** The state space is now Z/NZ (one dimension) instead of
(Z/NZ)^2 (two dimensions). This means:
- Birthday collision after O(sqrt(p)) steps instead of O(p)
  (since mod p the state space is Z/pZ with only p elements)
- Standard Pollard-rho on the 1D walk should work directly

**Caveat:** When n = 0 mod p (but not mod q), the ratio is undefined mod p.
Handle by tracking (m:n) as a projective point and checking gcd(n, N)
at each step.

**This might be equivalent to Experiment 3 but with a cleaner theoretical
framework and implementation.**

---

### Experiment 13: Fibonacci/Lucas Sequence Connection
**Priority: 4 | Difficulty: Easy | Expected: Theoretical clarity**

**Theory:** The matrix [[1,1],[1,0]]^k gives Fibonacci numbers. The
parametric family M(t) = [[t,1],[1,0]] gives generalized Lucas sequences.
The Williams p+1 method is literally this: iterate the Lucas sequence
V_n(t) mod N, and if p+1 | n then V_n = 2 mod p, giving gcd(V_n - 2, N)
as a factor.

**Experiment:** Implement a direct Williams p+1 attack using the trace
of M(t)^E where E is B-smooth. Compare performance against the current
smooth_exponent_attack which checks all derived values. The trace-only
version should be faster (1 gcd instead of 12) and have identical success
probability.

**If trace-only matches smooth_exponent:** This confirms that the
Pythagorean tree smooth exponent IS Williams p+1, and all further
optimizations should focus on the known Williams p+1 literature (Stage 2,
optimal B1/B2 selection, Papadopoulos extensions).

---

### Experiment 14: Additive Combination Attack
**Priority: 4 | Difficulty: Medium | Expected: Unknown**

**Theory:** Instead of checking gcd(v, N) for individual derived values,
check gcd(a1*v1 + a2*v2 + ... + ak*vk, N) for random linear combinations.
If v_i = 0 mod p for some i, then any linear combination containing v_i
with nonzero coefficient is also 0 mod p. But additionally, if
v_i = r_i mod p, a linear combination sum(a_i * r_i) = 0 mod p with
probability 1/p for random a_i. With K values per node, we get K
independent chances instead of just 1, improving the hit rate by K.

**This is already implicitly done by batch GCD (product of values).
The additive version is different because products can overflow mod p
but sums cannot.**

---

## TIER 5 -- Infrastructure Improvements

### Experiment 15: Montgomery Multiplication for Modular Walks
**Priority: 5 | Difficulty: Medium | Expected: 2-3x throughput**

**Theory:** The inner loop of all modular walks is dominated by (u128)a*b%N
operations. Montgomery multiplication replaces the expensive division
with cheaper multiply + shift. For 64-bit N, Montgomery form gives
~2-3x speedup on the modular arithmetic.

**Implementation:** Convert (m, n) to Montgomery form at the start.
All matrix multiplies use Montgomery multiply. Convert back only when
checking gcd.

---

### Experiment 16: SIMD Parallel Walks
**Priority: 5 | Difficulty: Hard | Expected: 4-8x throughput**

**Theory:** AVX2 can do 4 parallel 64-bit multiplies. Run 4 independent
walks simultaneously using SIMD. Each walk has its own (m, n) state but
shares the same matrix sequence (for cache efficiency).

**Combined with distinguished points (Experiment 1):** 4 SIMD lanes *
8 walks per lane (interleaved) = 32 parallel walks. Distinguished point
collision detection handles the cross-walk coordination.

---

## Recommended Execution Order

1. **Experiment 3** (Multi-Matrix Pollard-Rho) -- easiest path to O(sqrt(p)),
   builds on existing pyth_deep_mod.c infrastructure
2. **Experiment 2** (Cycle-Length GCD with batching) -- quick upgrade to
   existing Brent code
3. **Experiment 1** (Distinguished Points) -- the cleanest O(sqrt(p))
   approach, but needs new hash table infrastructure
4. **Experiment 4** (Stage 2 for smooth exponent) -- easy win for the
   p+1 approach, extends to 56b+
5. **Experiment 12** (Projective-Line Walk) -- may simplify the theory
   and make the Pollard-rho connection explicit
6. **Experiment 5** (Multiple starting points) -- trivial to implement,
   moderate improvement
7. **Experiment 8** (Matrix entry GCD / trace check) -- cheap new channels

## Key Open Question

The central question is whether the Pythagorean tree walk is ERGODIC
mod p -- i.e., whether a pseudo-random walk visits all of (Z/pZ)^2
uniformly. If yes, birthday-bound methods (Experiments 1-3) will work
and give O(sqrt(p)). If the walk is confined to a subgroup, the effective
state space is smaller, which is actually BETTER for birthday collisions.

The smooth exponent results (14/15 at 40b) strongly suggest that the
matrix orbits DO have the right group-theoretic structure. The fact that
different matrices catch different primes (like different ECM curves)
further supports this.

**Bottom line:** Experiments 1-3 should be tried IMMEDIATELY. If any of
them achieves O(sqrt(p)) scaling, it would be a transformative result --
pushing Pythagorean tree factoring from a 32b toy to a 64b+ practical
method.

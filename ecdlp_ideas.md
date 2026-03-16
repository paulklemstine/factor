# ECDLP Kangaroo Improvement Ideas

## Status Key
- READY: analyzed, ready to implement
- TESTING: currently being benchmarked
- MERGED: faster, committed to main
- FAILED: slower or broken, do not retry

## Ideas

### H1. Tree-Path Correlated Jump Sequences [READY]
**Expected**: 1.1-1.4x (better walk mixing from structured jumps)
**Risk**: Medium
**Description**: Replace the flat 64-entry jump table with **dynamic jumps generated
by walking down the Pythagorean tree**. Each kangaroo carries a (m,n) state initialized
from a different tree node. At each step, the branch is selected by `x_bits & 3`
(choose Berggren matrix T1, T2, or T3), the 2×2 matrix is applied to get (m',n'),
and the jump distance is c = m'²+n'² (scaled). The kangaroo's (m,n) state advances
down the tree.
**Why**: Current flat table gives 64 possible jumps → walk period bounded by table size.
Tree-path jumps are infinite and non-repeating, with geometrically growing distances
(each tree level roughly doubles m,n). This creates walks with better coverage — the
structured growth avoids the clustering that fixed tables can produce. Two walks at
the same EC point take the same branch (same x → same branch selection) and thus stay
merged, satisfying the kangaroo determinism requirement.
**Key**: The walk function must be deterministic on x only. Branch = `x & 3` (3 branches
+ 1 "stay at current level" to prevent unbounded growth). The (m,n) state is
per-kangaroo but the branch selection is point-determined.

### H2. Fibonacci-Optimal Jump Spacing (Price Tree) [READY]
**Expected**: 1.05-1.15x (better equidistribution)
**Risk**: Low
**Description**: The Price tree's unique matrix P3=[[2,0],[1,1]] generates (m,n) pairs
whose ratios converge to the golden ratio φ. Fibonacci numbers provide the **worst-case
equidistribution** among all integer sequences (3-distance theorem / Steinhaus conjecture).
Generate all 64 jump distances by walking the Price tree to depth 6-7, extracting the
hypotenuses c = m²+n² at each node. These jumps have maximally uniform spacing in
the multiplicative sense, preventing the walk from having "blind spots."
**Why**: Standard Pythagorean hypotenuses (5, 13, 25, 29, ...) cluster at certain
residues mod small primes. Fibonacci-related hypotenuses from the Price tree are
proven to avoid this clustering. Better equidistribution → faster birthday paradox
convergence.
**Implementation**: Simple — just change the jump distance precomputation. Generate
Price tree to depth 7 (3^7 = 2187 nodes), take 64 evenly-spaced leaves, extract
hypotenuses, scale to target mean.

### H3. Lévy Flight via Multi-Scale Tree Depths [READY]
**Expected**: 1.2-1.5x (optimal search strategy for unknown target location)
**Risk**: Medium
**Description**: Lévy flights (heavy-tailed step distributions) are mathematically
proven optimal for blind search problems (Viswanathan et al., Nature 1999). Currently
all 64 jumps are scaled to similar magnitude. Instead, use the Pythagorean tree to
create a **power-law distribution** of jump sizes:
- 32 jumps from tree depth 3-4 (small, c ~ 50-200)
- 16 jumps from depth 5-6 (medium, c ~ 500-2000)
- 8 jumps from depth 7-8 (large, c ~ 5000-20000)
- 8 jumps from depth 9-12 (very large, c ~ 50000-1000000)
Jump index still uses `x & 63`. The heavy tail means most steps are local (good for
birthday paradox after merge) but occasional large leaps explore new territory fast.
**Why**: Standard kangaroo uses uniform jump sizes, which is suboptimal for the
"exploration vs exploitation" tradeoff. Lévy flights with exponent α≈2 maximize the
territory covered per step while maintaining walk merging.

### H4. Triple-Tree Diversity Jump Table [READY]
**Expected**: 1.05-1.1x (maximum jump diversity)
**Risk**: Low
**Description**: Use ALL THREE Pythagorean tree systems (Berggren, Price, Firstov)
to generate the 64 jump distances. Each tree tiles the (m,n) space differently —
Berggren by ratio, Price by parity, Firstov by leg-swapping. Taking ~21 jumps from
each tree gives maximum diversity in jump distances, since the three trees visit
completely disjoint paths through (m,n) space.
**Why**: Current jumps all come from one traversal, which may cluster at certain
residue classes. Three independent tilings provide complementary statistical properties.
More diverse jumps → more random walk → faster convergence.

### H5. 2×2 Matrix State Walk (Evolving Jumps) [READY]
**Expected**: Unknown (structural change to walk dynamics)
**Risk**: High
**Description**: Each kangaroo carries a 2×2 matrix state M (initialized to a tree
matrix). At each step: (1) compute (m,n) = M × (2,1), get jump c = m²+n²;
(2) select next matrix based on `x & 3` (T1, T2, or T3 from Berggren);
(3) update M = T_selected × M. The jump distances EVOLVE as the kangaroo walks,
growing geometrically with each step. This creates an accelerating walk.
**Why**: Standard fixed-jump kangaroo has O(√N) expected steps. An accelerating walk
covers exponentially more ground per step but risks overshooting. With proper damping
(periodically reset M to identity), this could approach O(N^{1/3}) behavior by trading
walk quality for coverage speed.
**Danger**: Evolving jumps break the "two walks at same point stay merged" property
unless the M state is also derived deterministically from the EC point. The M state
must be a function of x only, not of walk history.

### H6. Modular Group Walk via Γ(2) [READY]
**Expected**: Unknown (fundamentally different walk structure)
**Risk**: Very High (moonshot)
**Description**: The Pythagorean trees live in Γ(2), a subgroup of the modular group
PSL(2,Z). Elliptic curves are parametrized by the modular curve X₀(N) via Wiles'
modularity theorem. This means there is a **direct algebraic map** from Γ(2) actions
to the elliptic curve. Instead of walking on the EC group with random jumps, define
the walk as a sequence of Möbius transformations in Γ(2) and map each step back to
an EC point via the modular parametrization.
**Why**: Random walks on the hyperbolic plane (where Γ(2) acts) have different mixing
properties than walks on the EC group. The modular surface has constant negative
curvature → spectral gap → exponentially fast mixing (Selberg's theorem). If the
mapping preserves enough structure, this could fundamentally change the convergence
rate from O(√N) to something better.
**Reality check**: The modular parametrization is transcendental (involves q-expansions
and eta functions) — computing it is far more expensive than EC arithmetic. This is
a theoretical direction, not a practical one without major mathematical breakthrough.

### H7. Coprime-Pair Jump Generation via Stern-Brocot [READY]
**Expected**: 1.05-1.1x (optimal rational spacing)
**Risk**: Low
**Description**: The Stern-Brocot tree generates ALL positive rationals exactly once,
in "maximally spread" order. Each node m/n gives coprime (m,n) with m²+n² as a jump
distance. Walk the Stern-Brocot tree in BFS order to depth 7 (255 nodes), take 64
evenly-spaced nodes. These (m,n) pairs are guaranteed to be maximally spread among
all rationals — no two are "close" in the mediant sense.
**Why**: Stern-Brocot ordering is the unique ordering of rationals that minimizes the
maximum gap between consecutive entries at every finite truncation. This translates
directly to jump distances that optimally cover the integer range without clustering.
**Connection**: The Stern-Brocot tree IS the Farey sequence tree, which IS the
fundamental domain decomposition of PSL(2,Z) — the same group the Pythagorean trees
live in. So this is the natural way to select jump distances from the modular group.

### H8. Pythagorean Decomposition Shortcut [READY]
**Expected**: Unknown (could be transformative if it works)
**Risk**: Very High (moonshot)
**Description**: By Fermat's theorem on sums of two squares, every prime p ≡ 1 mod 4
has a unique representation p = m² + n². The scalar k we're searching for might have
a decomposition path through the Pythagorean tree that encodes its structure. If
k = c₁ · c₂ · ... · cₗ (product of Pythagorean hypotenuses), then the tree paths
to each cᵢ give a "factorization" of the walk to k·G.
**Why**: Instead of random-walking to k·G, we'd be tree-searching for the path that
decomposes k into Pythagorean hypotenuses. The tree has depth O(log k) and branching
factor 3, so exhaustive tree search is 3^(log k) = k^(log 3) ≈ k^1.58 — WORSE than
√k. BUT: if we can prune branches using information from the EC point (e.g., checking
partial products against partial scalar multiplications), we might prune to O(k^{1/3})
or better.
**Key insight**: The Pythagorean tree gives a STRUCTURED decomposition of integers,
unlike the random walk's UNSTRUCTURED search. Structure enables pruning. Pruning
enables sub-√N search.

---

### 1. GMP mpn_ Fixed-Limb Hot Path [MERGED 2026-03-13]
**Expected**: 2-2.5x speedup
**Risk**: Medium
**Description**: Replace mpz_t with mp_limb_t[4] fixed arrays in the batch-inversion
hot loop. Use mpn_mul_n (same MULX/ADX assembly) but skip all heap allocation.
Replace mpz_mod with secp256k1-specific fast reduction:
p = 2^256 - 2^32 - 977 → subtract high_limbs * (2^32 + 977), iterate.
Keep mpz_invert for the single batch inversion (convert to/from mpz there).
**Why**: GMP mpz_t overhead (alloc checks, size tracking) is ~60% of per-step cost.
mpn_ eliminates this while keeping GMP's assembly-tuned multiplication.

### 2. Multiprocessing (6 workers) [READY]
**Expected**: ~5x wall-clock speedup (6 cores, first-to-finish wins)
**Risk**: Low
**Description**: Already 80% implemented in ecdlp_pythagorean_kangaroo_c_parallel().
Each forked subprocess gets own GMP heap (no contention). Independent walks with
different tame_start positions. Exponentially distributed completion → E[wall] = E[single]/r.
**Why**: The simplest path to large speedup. 6 * 50MB = 300MB, fine for 7.4GB WSL2.

### 3. GLV Equivalence Class Walk [READY]
**Expected**: 1.6x (sqrt(3) from 6-fold equivalence)
**Risk**: Medium-High (cycle risk)
**Description**: Use phi(x,y) = (beta*x, y) where beta^3 = 1 mod p.
Canonicalize each point by min(x, beta*x, beta^2*x), combined with negation
gives 6-fold equivalence. Walk on quotient space of size N/6.
Cost: 2 field multiplications per step for canonicalization.
**Danger**: Equivalence class walks can form short cycles. Need Brent cycle
detection and perturbation jumps.

### 4. GPU Projective Coordinates [READY]
**Expected**: 2-5x GPU speedup
**Risk**: Medium
**Description**: Current GPU uses affine coords with Fermat inversion (255 squarings
+ 15 muls) EVERY step. Switch to Jacobian (X,Y,Z) coords: 11 muls + 5 squarings
per step, NO inversion. Only convert to affine at DP hits (1 in 2^dp_bits steps).
Jump index uses Z-independent hash of (X,Z) or approximation.
**Why**: Fermat inversion is ~70% of per-step GPU cost. Eliminating it for non-DP
steps should be a massive throughput improvement.

### 5. Negation Map / X-only Walk [FAILED 2026-03-13]
**Result**: No speedup for bounded kangaroo
**Risk**: Medium (2-cycle risk)
**Description**: Treat P=(x,y) and -P=(x,-y) as the same point. Walk based only on
x-coordinate. Halves the effective search space.
**Why failed**: Only works when search interval is a significant fraction of group
order. In bounded kangaroo searching [0, 2^48] on secp256k1 (order 2^256), opposite-y
collisions give k = n - t - w ≈ 2^256, far outside the search bound. Walk
canonicalization (negate to even y) also disrupts walk dynamics, causing 10x slowdown.
Same-y collisions (the only useful ones) happen at the same rate without negation.

### 6. Robin Hood / Cuckoo DP Hash Table [READY]
**Expected**: 1.1-1.2x
**Risk**: Low
**Description**: Replace chained hash (65536 buckets, linked lists) with
open-addressing Robin Hood or Cuckoo hash. Current linked lists cause cache
misses on every DP lookup. Cache-line aligned buckets would be much faster.

### 5. AES-NI Jump Index Hash [READY]
**Expected**: 1.1x
**Risk**: Low
**Description**: Replace mpz_fdiv_ui(x, 64) with reading GMP limb directly
(mpz_getlimbn) + AES-NI hash for better walk pseudorandomness. Eliminates
GMP division overhead and reduces short-cycle probability.

---

## Completed (Merged to Main)

### Batch Montgomery Inversion [MERGED 2026-03-13]
**Result**: 1.4-1.8x speedup
**Description**: Batch all NK kangaroo inversions into 1 mpz_invert per step
using Montgomery's trick: accumulate product, invert once, recover individuals.

### GMP mpn_ Fixed-Limb Hot Path [MERGED 2026-03-13]
**Result**: 1.3-1.6x speedup
**Description**: Replace mpz_t with mp_limb_t[4] (fe_t) in Phases 1+3 of hot loop.
secp256k1-specific reduction via p = 2^256 - (2^32+977). Phase 2 batch inversion
stays as mpz_t with fe↔mpz conversion at boundary.

### fe_t Batch Inversion Product Tree [MERGED 2026-03-13]
**Result**: 1.2x speedup (consistent across 36-44b)
**Description**: Replace mpz_mul+mpz_mod in batch inversion product tree with
fe_mul. Eliminates NK fe_to_mpz + NK fe_from_mpz conversions per step.
Only 1 mpz_invert call remains (via fe↔mpz conversion at the boundary).

### CUDA GPU Kangaroo [MERGED 2026-03-13]
**Result**: 10-23x speedup (44b: 10x, 48b: 23x, 52b: 20x)
**Description**: RTX 4050 GPU implementation with 4096 parallel kangaroo walks.
Jacobian coordinates with NORM_INTERVAL=8 normalization, fe_sqr optimization.
DP density tuned: D=(bits-8)/4 instead of bits/4 (reduces post-merge waste from 50% to 10%).
Incremental initialization (repeated EC addition instead of per-kangaroo scalar mult).
Adaptive steps-per-launch (2048/4096/8192 based on problem size).
56b: ~20s, 60b: ~34s. 64b+ limited by uint64 position overflow.

### GPU SM-Aware Kangaroo Count [MERGED 2026-03-13]
**Result**: ~20% speedup (48b: 1.23x, 52b: 1.32x)
**Description**: Query GPU SM count at runtime, set NK = SM_count × threads_per_block
for 100% SM utilization. Old NK=4096 gave 16 blocks / 20 SMs = 80% fill. New NK=5120
gives 20 blocks / 20 SMs = 1 block per SM. Portable across different GPU models.

### Multi-Kangaroo NK=4 [MERGED 2026-03-13]
**Result**: ~1.3x from birthday paradox with 4 walks
**Description**: Adaptive NK=2 for ≤28 bits, NK=4 for larger. 2 tame + 2 wild
with evenly-spaced starting positions.

---

## Failed (Do Not Retry)

### GLV 3x DP Lookup [FAILED 2026-03-12]
**Result**: SLOWER (44b: 39s vs 21s baseline)
**Why failed**: Verification overhead — 6 scalar multiplications per DP match
to check all 3 equivalent x-coordinates negated the 3x collision rate improvement.

### Jacobian Coordinates [FAILED 2026-03-12]
**Result**: No benefit
**Why failed**: Jump index (x mod 64) and DP check (low bits of x) both require
affine x every step. Computing x = X/Z² needs an inversion, defeating the purpose.

### Custom 256-bit Field Arithmetic (__int128) [FAILED 2026-03-12]
**Result**: SLOWER than GMP
**Why failed**: GMP's mpn_* uses assembly-optimized MULX/ADX instructions.
C compiler's __int128 generates generic mul instructions, ~30% slower for 4-limb.

### Pthreads Parallelism [FAILED 2026-03-12]
**Result**: 10x per-step overhead
**Why failed**: GMP's global malloc lock serializes all threads. Mutex contention
on DP table adds further overhead. Net result barely faster than single-threaded.

### fast_mod_p secp256k1 Reduction [FAILED 2026-03-12]
**Result**: Only 6% gain
**Why failed**: GMP's mpz_mod is already fast for 4-limb numbers. The special
reduction (p = 2^256 - 2^32 - 977) saves one division but adds complexity.
Multiple bugs encountered (negative values, double subtraction edge cases).

### 8-Kangaroo NK=8 [FAILED 2026-03-13]
**Result**: SLOWER single-threaded
**Why failed**: Total work increases as sqrt(NK). More kangaroos = more steps
total, and batch inversion already near-optimal at NK=4.

### Hybrid Kangaroo-BSGS [FAILED — analysis only, 2026-03-13]
**Result**: No algorithmic advantage
**Why failed**: Analysis showed it reduces to standard BSGS with extra overhead.
The baby-step table doesn't help the kangaroo's random walk convergence.

### GLV Equivalence Class Walk [FAILED 2026-03-13]
**Result**: No speedup (40b: 0.89x slower, 44b: 1.02x even)
**Why failed**: Tame walks from pos*G (known scalars) and wild walks from P+pos*G
(unknown scalars) occupy different cosets of the endomorphism action. Canonical x
walk makes jumps deterministic on equivalence classes, but tame/wild can only
collide when they independently reach the same class by chance — no reduction in
expected steps vs standard kangaroo. Per-step overhead of 2 fe_mul for x_canon
computation (~30-40% more per step) is not compensated.

### NORM_INTERVAL=16 [FAILED 2026-03-13]
**Result**: 2.2x slower at 48b (3.2s vs 1.2s baseline)
**Why failed**: Longer Jacobian windows (16 steps without normalization) degrade walk
pseudorandomness. The jump index cX.v[0]&63 uses Jacobian X (not affine x) between
normalizations. After many steps, Jacobian X diverges from uniform distribution,
causing biased walks and slower convergence. NORM_INTERVAL=8 is optimal.

### GPU Shared Memory Jump Table [FAILED 2026-03-13]
**Result**: No improvement (40b: 1.4x slower, 44b: 1.2x slower, 52b: within noise)
**Why failed**: __constant__ memory L1 cache on Ada Lovelace (RTX 4050) is already
fast for the 4.6KB jump table. __shared__ memory loading + __syncthreads() overhead
negates any benefit from avoiding constant cache serialization. EC arithmetic (11 field
ops per step) dominates; jump table reads are <5% of step time.

### Negation Map on GPU [FAILED 2026-03-13]
**Result**: No speedup (bounded search interval too small relative to group order)
**Why failed**: Negation map halves the search space by identifying (x,y)~(x,-y).
For bounded kangaroo searching [0, 2^48] within group order 2^256, opposite-y
collisions give k = n - pos_t - pos_w ≈ 2^256, outside [1, bound]. Only same-y
collisions are useful, and those happen at the same rate without negation.
Walk canonicalization (negate to even y at each normalization) disrupted walk dynamics.

### H1: Berggren Tree Hypotenuses [FAILED 2026-03-13]
**Result**: Same performance as Lévy table (within noise at 40-52b)
**Why failed**: Same distribution shape as exponential table. Specific number-theoretic
values don't matter for walk quality — only the spread shape matters.

### H2: Price Tree Fibonacci Jumps [FAILED 2026-03-13]
**Result**: No improvement over baseline
**Why failed**: Same class as H1. Jump value source doesn't matter; spread does.

### H3: Lévy Flight Exponential Spread [MERGED 2026-03-13]
**Result**: 1.2-1.45x faster at 48-56b
**Why it worked**: 10^7 spread (1 to 10M) compensates for weak hash `x & 63`,
ensuring correlated indices produce diverse walks.

### Murmur3 Jump Hash [MERGED 2026-03-13]
**Result**: Reduces tail outliers at 52-56b
**Why it worked**: Bijective mixing of Jacobian X produces uniform jump selection
even when X has correlated low bits within normalization intervals.

### Bernstein-Yang Divstep Inversion [MERGED 2026-03-13]
**Result**: 1.3-1.6x faster overall
**Why it worked**: Replaces Fermat inversion (255 sqr + 16 mul = 271 field ops)
with shift/add divstep algorithm. 9 batches of 62 scalar divsteps with 2x2
transition matrices. Constant-time (no warp divergence). Inversion was 75% of runtime.

### H9-H16 Analysis [ALL FAILED 2026-03-13]
**H9 Endomorphism 2D**: λ*k ≈ 2^255, outside bounded search [0, 2^48].
**H10 EC Index Calculus**: No prime-field EC index calculus exists.
**H11 Degenerate Traps**: Probability 1/2^256 per step — vanishing.
**H12 Attractor Basins**: Can't engineer attractors without losing walk diversity.
**H13 Telescoping**: No "approximate k" in discrete groups.
**H14 256 Generators**: Spread matters, not count. 64 already optimal.
**H15 Pythagorean Descent**: No algebraic map between EC (genus 1) and unit circle (genus 0).
**H16 Rainbow Table**: Just precomputed BSGS, already have that.
**Root cause**: Pollard kangaroo at O(√N) is optimal for generic group DLP.
All improvements must be constant-factor (hardware/engineering).

### __launch_bounds__ + #pragma unroll [FAILED 2026-03-13]
**Result**: 7-22% slower at 44-52b
**Why failed**: Increased register pressure caused spills to local memory,
negating any benefit from unrolling. Compiler's default was already near-optimal.

### DP Density Sweep [CONFIRMED 2026-03-13]
**Result**: D=(bits-8)/4 is optimal (tested D=8..13 at 48b and 52b)

### NORM_INTERVAL with Murmur3 [FAILED 2026-03-13]
**Result**: N=12 catastrophic (108s at 52b), N=16 worse (9.1s at 52b)
**Why failed**: Higher N = fewer merge opportunities (walks can only merge at
normalization boundaries). This is a fundamental limitation, not a hash quality issue.

### 2-Step Comb Table [FAILED 2026-03-13]
**Result**: No benefit with mpn_ code (was 1.5x with old mpz-only code)
**Why failed**: Comb doubles mean jump size but doesn't reduce EC additions to
convergence — birthday paradox depends on #points visited, not distance covered.
Original benefit was from eliminating mpz_mod for jump index, which mpn_ (fe_t)
already provides via direct limb read. Precomputation cost (~1s for 4096 ap_add)
dominates at medium bit sizes with no convergence benefit.

### Shared-Memory Multi-Process Kangaroo [MERGED 2026-03-15]
**Result**: 2.2-3.1x speedup (6 workers, scaling with problem size)
**Why it worked**: Van Oorschot-Wiener parallelism — all workers share a single
mmap'd DP table, giving near-linear speedup. Lock-free CAS inserts with two-phase
CLAIMING→READY protocol. 128-bit positions. NK=2 per worker (1T+1W) is optimal
because the shared table provides the birthday pool.
36b: 0.24s, 40b: 3.4s, 44b: 7.3s, 48b: 38s

---

## Factoring Theorem Transfer Experiments [ALL FAILED 2026-03-15]

Six hypotheses tested in parallel to determine if Pythagorean tree theorems
(spectral gap, B3 AP, Pell convergents, smoothness, multi-birthday, orbits)
can break the O(√N) barrier for ECDLP. All rejected.

### H_SPECTRAL: Berggren Expander Walk [FAILED 2026-03-15]
**Result**: 0.64x average (WORSE). Steps: 28b 67K vs 24K standard.
**Why failed**: Kangaroo convergence is a birthday problem, not a mixing problem.
Spectral gap mixes the (m,n) auxiliary state, not the EC walk. Walk quality
depends on jump SPREAD shape, not algebraic source. Confirms H1/H2 pattern.

### H_B3AP: B3 Arithmetic Progression BSGS [FAILED 2026-03-15]
**Result**: 2-3x worse than standard BSGS at all sizes (24-32b).
**Why failed**: Quadratic spacing c_k=4k²+8k+5 creates gaps exceeding giant step
range for k > M/8. Standard BSGS's dense grid (all i*M+j) has zero gaps and
achieves perfect M² coverage from 2M operations. No O(N^{1/3}) shortcut exists.

### H_PELL: Pell Number Jump Table [FAILED 2026-03-15]
**Result**: Ties Lévy table (within noise at 28-36b). No improvement.
**Why failed**: Pell numbers produce exponential spread (base 2.414), same shape
as existing Lévy table. The "worst rational approximation" property (3-distance
theorem) is irrelevant to integer jump magnitudes in random walks.

### H_SMOOTH: Smooth Coordinate Batch-GCD [FAILED 2026-03-15]
**Result**: Zero nontrivial GCDs across all trials. Zero matches.
**Why failed**: EC scalar multiplication is a pseudorandom permutation — it
completely destroys the number-theoretic structure of the scalar. x-coordinates
are uniform in F_p regardless of scalar's algebraic properties. Smoothness
amplification helps factoring (same ring) but not ECDLP (different group).
**THIS IS THE FUNDAMENTAL REASON ECDLP IS HARD.**

### H_MULTIBDAY: Multi-Dimensional Birthday [FAILED 2026-03-15]
**Result**: 2.8x worse due to per-point cost.
**Why failed**: Only ~5 unique scalars per tree node (not 12, heavy overlap).
Each scalar_mult costs 14x vs incremental EC add. The sqrt(5)=2.2x birthday
advantage cannot compensate for the 14x per-point penalty.

### H_ORBIT: Matrix Orbit Period Attack [FAILED 2026-03-15]
**Result**: Three independent barriers kill the approach.
**Why failed**: (1) B1/B3 are unipotent (order=p, not smooth). (2) B2's order
mod n has 232-bit composite cofactor. (3) No homomorphism from EC group to
GL(3,F_n) — solving matrix DLP tells nothing about EC scalar k. Matrix DLP
itself is L_p[1/3] ~ 2^100, harder than 2^128 generic EC DLP.

### Master Conclusion (2026-03-15)
All Pythagorean tree theorems (spectral gaps, smoothness amplification, B3 AP,
Pell convergents, multi-birthday, orbit structure) help factoring because
factoring operates in the SAME RING where the structure lives. ECDLP operates
in the EC group where scalar multiplication scrambles all structure. The only
ECDLP improvements are: (1) engineering (shared DP, GPU, batch inversion),
(2) curve-specific endomorphisms (GLV Z/6), (3) hardware parallelism.

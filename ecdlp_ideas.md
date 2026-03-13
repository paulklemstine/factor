# ECDLP Kangaroo Improvement Ideas

## Status Key
- READY: analyzed, ready to implement
- TESTING: currently being benchmarked
- MERGED: faster, committed to main
- FAILED: slower or broken, do not retry

## Ideas

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

### 4. Robin Hood / Cuckoo DP Hash Table [READY]
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

### 2-Step Comb Table [FAILED 2026-03-13]
**Result**: No benefit with mpn_ code (was 1.5x with old mpz-only code)
**Why failed**: Comb doubles mean jump size but doesn't reduce EC additions to
convergence — birthday paradox depends on #points visited, not distance covered.
Original benefit was from eliminating mpz_mod for jump index, which mpn_ (fe_t)
already provides via direct limb read. Precomputation cost (~1s for 4096 ap_add)
dominates at medium bit sizes with no convergence benefit.

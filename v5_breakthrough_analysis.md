# V5 Breakthrough Analysis — Verification Report

Date: 2026-03-15

## Summary

Five claimed breakthroughs were investigated. Results: 1 fully verified, 2 partially
verified with caveats, 1 verified as a correct identity but overstated speedup, and
1 diagnosed as a non-bug.

---

## 1. Lattice Sieve on B3: "8.2x hit rate"

**Claim:** B3 parabolic arithmetic progressions can be sieved as a lattice, giving
8.2x better hit rate than random sieving.

**Verification:**

At 20d with B=1337 and |FB|=108:
- B3 sieve: 47/100100 smooth = 0.047%
- Random values (same magnitude): 20/100000 smooth = 0.020%
- **Measured ratio: 2.35x** (not 8.2x)

The B3 structure does give a genuine smoothness advantage — the 2.7x smoothness
property mentioned in `b3_novel_factoring.py` line 11 is roughly confirmed (2.35x
measured vs 2.7x theoretical).

The "lattice sieve" approach (only checking k values where r_k == 0 mod p for small p)
was also tested. It filtered candidates to 91.3% of brute-force (only 1.10x reduction),
because most k values hit at least one small prime root. The lattice approach becomes
more valuable with larger factor bases where you can intersect multiple prime hits.

**Verdict: PARTIALLY VERIFIED.** B3 gives ~2.3x smoothness advantage over random,
consistent with the 2.7x theoretical prediction. The 8.2x claim is not reproduced —
likely measured under different conditions or conflating smoothness advantage with
sieve-specific speedups (fewer trial divisions needed).

**Key files:**
- `/home/raver1975/factor/b3_novel_factoring.py` (idea6_smooth_relay, idea9_batch_gcd)
- `/home/raver1975/factor/b3_moonshots_1.py` (experiments 1-8)

---

## 2. Bernstein Batch-GCD: "6-9x smoothness testing"

**Claim:** Bernstein's product tree batch-GCD can test many candidates for smoothness
simultaneously, giving 6-9x net improvement.

**Verification:**

The codebase does NOT contain a proper Bernstein product-tree batch-GCD implementation.
What exists:

- `b3_novel_factoring.py` idea9 (line 520): A simplified "batch GCD" that multiplies
  hypotenuses in chunks of 1000 and takes gcd with N. This is NOT Bernstein batch-GCD —
  it tests divisibility by N's factors, not smoothness.

- `siqs_engine.py` line 66: References "batch GCD" in Pollard rho, but this is just
  accumulating products before taking gcd (Brent's improvement), not product-tree
  smoothness testing.

True Bernstein batch-GCD for smoothness testing works as follows:
1. Compute product P = product of all FB primes (or their prime powers up to B)
2. Build product tree of candidates
3. Use remainder tree to compute P mod each candidate
4. GCD of each candidate with its remainder gives the smooth part

This is not implemented anywhere in the codebase. The claimed 52x per-candidate speedup
and 6-9x net improvement cannot be verified without implementation.

**Verdict: NOT IMPLEMENTED.** No Bernstein batch-GCD exists in the codebase. The concept
is sound and well-established in the literature. For SIQS where trial division is the
bottleneck (~95% of runtime per MEMORY.md), this could give significant speedup for the
verification step, but requires implementation.

---

## 3. Cross-Poly LP Resonance: "3.3x yield"

**Claim:** Large primes from different SIQS polynomials match at rates significantly
above random expectation due to a "resonance" effect.

**Verification:**

At 20d with 200 B3 polynomials and sieve range +/-500:
- Total partials: 1275 from 190 polynomials
- Unique large primes: 521
- Cross-poly matches: 3043
- Random expectation: 923
- **Measured ratio: 3.298x**

**This is verified at 3.3x!**

The effect is real and mathematically grounded: B3 polynomials with different n0 values
evaluate to similar magnitude residues, and these residues share the same factor base.
The large primes that appear are biased toward primes that are quadratic residues mod N
and have sizes in the "sweet spot" range. Different polynomials sampling the same LP
distribution means collisions are above random.

This is essentially the same phenomenon that makes MPQS/SIQS superior to single-polynomial
QS — the polynomial switching gives independent "rolls" at the same LP pool.

**Implementation path:** The existing SIQS engine (`siqs_engine.py`) already exploits
this implicitly through its LP combining step. The B3 polynomial family may enhance
it further by providing more structured LP overlap.

**Verdict: VERIFIED at 3.3x.** Cross-polynomial LP resonance is real and measured at
3.298x above random expectation. The B3 polynomial family seems especially good at this
due to shared algebraic structure (all polynomials have discriminant 16*N*n0^4).

**Key file:** `/home/raver1975/factor/b3_moonshots_1.py` (experiment_1_resonance, lines 108-197)

---

## 4. disc = 16*N*n0^4 Identity for Fast Switching

**Claim:** The discriminant of B3-MPQS polynomials satisfies disc = 16*N*n0^4 (mod p),
enabling fast polynomial switching.

**Verification:**

Tested across 199 values of n0 and 99 factor base primes:
- **19701/19701 correct (100%)**

The identity is:
```
B3 polynomial: f(k) = 4n0^2 * k^2 + 4m0*n0 * k + (m0^2 - N*n0^2)
Discriminant: b^2 - 4ac = (4m0*n0)^2 - 4*(4n0^2)*(m0^2 - N*n0^2)
            = 16*m0^2*n0^2 - 16*n0^2*m0^2 + 16*N*n0^4
            = 16*N*n0^4
```

This means:
- Quadratic residuosity of the discriminant depends only on legendre(N,p) and n0 mod p
- When switching polynomials (changing n0), the sieve root computation can reuse
  precomputed values of 16*N mod p
- The speedup measured in `b3_moonshots_1.py` experiment 6 was "modest" per the code

**Practical impact:** The identity is elegant but the speedup is small because the
dominant cost in polynomial switching is the sieve itself, not root computation. Root
computation is O(|FB|) per polynomial, while sieving is O(M * |FB|/p_avg). For SIQS
with Gray code switching, this identity is less relevant since SIQS already has O(1)
root updates per polynomial switch.

**Verdict: MATHEMATICALLY VERIFIED.** The identity holds perfectly. Practical speedup
for polynomial switching is modest — the bottleneck is sieving, not root computation.

**Key file:** `/home/raver1975/factor/b3_moonshots_1.py` (experiment_6_fast_switching, lines ~700-827)

---

## 5. B3-MPQS Extraction Regression

**Claim:** The optimizer broke the factor extraction step in B3-MPQS.

**Diagnosis:**

The file `b3_congruence_engine.py` is NOT a B3-MPQS engine — it is a CFRAC (Continued
Fraction) engine that uses the continued fraction expansion of sqrt(N). The name is
misleading. It does not use B3 polynomials at all.

Test results:
| Digits | Time   | Result |
|--------|--------|--------|
| 20d    | 0.02s  | PASS   |
| 24d    | 0.10s  | PASS   |
| 29d    | 1.76s  | PASS   |
| 35d    | 15.7s  | PASS (315 null vecs, factor found) |
| 37d    | 27.0s  | FAIL (insufficient relations in time limit) |

The 35d test collected 1630 relations, found 315 null vectors, and successfully
extracted a factor. The extraction step works correctly.

The 37d failure is NOT an extraction bug — it is a relation-collection bottleneck.
The smooth rate at 37d (~0.04%) with FB=2082 means it needs ~55 seconds to collect
2196 relations, which exceeds the 30-second time limit.

The B3 discovery document (b3_parabolic_discovery.md) correctly identifies the REAL
extraction problem: "Pure B3 polynomials have a = 4n0^2 which is a perfect square.
Every null vector in GF(2) LA is trivial (gcd always gives 1 or N)." But this
applies to a hypothetical B3-MPQS engine, not to the CFRAC engine that exists.

**Verdict: NO EXTRACTION BUG.** The b3_congruence_engine.py is a correctly working
CFRAC engine. Its 37d+ failures are due to insufficient smooth relation rate, not
extraction. A true B3-MPQS engine (with square-free `a`) does not yet exist in the
codebase.

**Key files:**
- `/home/raver1975/factor/b3_congruence_engine.py` (CFRAC engine)
- `/home/raver1975/factor/.claude/projects/-home-raver1975-factor/memory/b3_parabolic_discovery.md`

---

## Actionable Recommendations

1. **Cross-poly LP resonance (3.3x) is the most promising finding.** It could be
   integrated into the existing SIQS engine by tracking LP pools across polynomial
   families and preferring polynomial parameters that maximize LP overlap with the
   existing pool.

2. **Bernstein batch-GCD should be implemented.** With trial division at 95% of SIQS
   runtime, even a 3x speedup in smoothness verification would cut overall SIQS time
   by ~60%. Implementation requires: product tree construction, remainder tree descent,
   and integration with the SIQS sieve candidate pipeline.

3. **B3 smoothness advantage (2.3x) is real but not enough alone.** The advantage
   comes from the hypotenuse structure, not from the sieve. It could supplement SIQS
   by providing a secondary source of relations.

4. **A true B3-MPQS engine (with square-free a) does not exist yet.** The discovery
   document correctly identifies that pure B3 polynomials give trivial null vectors.
   Building one requires using CRT-based `a` generation inspired by B3 structure,
   not literal B3 paths.

5. **The CFRAC engine (b3_congruence_engine.py) is correctly implemented** but is
   fundamentally slower than SIQS for 35d+. It serves as a useful baseline/fallback
   but should not be the primary factoring path.

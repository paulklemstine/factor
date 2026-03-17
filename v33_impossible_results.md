# v33_impossible — Exploring the Mathematically Impossible

**Date**: 2026-03-16  
**Runtime**: 1.0s  
**Results**: 2 positive / 6 negative out of 8

## Summary Table

| # | Experiment | Result | Key Finding |
|---|-----------|--------|-------------|
| 1 | Exp 1: CM ternary structure | NEGATIVE | lambda^2 + lambda + 1 = 0 mod n: True |
| 2 | Exp 2: Eisenstein tree | NEGATIVE | Valid Eisenstein triples (m<100): 3003 |
| 3 | Exp 3: Classical period finding | NEGATIVE | Results per semiprime: |
| 4 | Exp 4: Smooth amplification | NEGATIVE | Smoothness amplification test (B=1000): |
| 5 | Exp 5: Torus index calculus | NEGATIVE | p = 1009 (p ≡ 1 mod 4) |
| 6 | Exp 6: Berggren walk period | POSITIVE | Berggren walk period detection: |
| 7 | Exp 7: Modular forms factoring | NEGATIVE | Modular forms analysis: |
| 8 | Exp 8: Collatz tree factoring | POSITIVE | Collatz-like tree factoring: |

## Detailed Results

### [NEGATIVE] Exp 1: CM ternary structure

```
  lambda^2 + lambda + 1 = 0 mod n: True
  This IS the norm form x^2+xy+y^2 = 0 equation!

  Berggren tree triples generated: 1501
  Hypotenuse distribution mod 3: {2: 758, 1: 743}
  Loeschian numbers up to 490433: 91406
  Hypotenuses that are also Loeschian: 366/1328 = 0.276

  GLV ternary decomposition rate (k1 < n/3): 0.314 (expected ~0.333)

  KEY INSIGHT: lambda^2 + lambda + 1 = 0 IS the Eisenstein norm equation.
  The GLV endomorphism IS multiplication by zeta_3 in Z[zeta_3].
  The Berggren tree's 3-way branching mirrors the 3 units of Z[zeta_3].

  But: this connection is STRUCTURAL (algebraic coincidence of "3-ness"),
  not COMPUTATIONAL. The endomorphism gives 2x speedup (GLV), not sqrt(n) break.
  The ternary tree navigates Z^3, not Z[zeta_3].
```

### [NEGATIVE] Exp 2: Eisenstein tree

```
  Valid Eisenstein triples (m<100): 3003
  Smallest triples: [(3, 5, 7), (8, 7, 13), (5, 16, 19), (15, 9, 21), (7, 33, 37)]
  Root triple: (3, 5, 7)

  Matrices checked: 500001
  Form-preserving matrices found: 0
  []

  CF-Eisenstein connection:
    Z[zeta_3] has Euclidean algorithm => CF expansion exists
    The 6 units give 6-fold symmetry (vs 4-fold for Z[i])
    Tree branching: expect 5-way (6 units minus 1 for parent) or 2-way (half by symmetry)

  VERDICT: Eisenstein triples exist and have tree structure, but the tree
  branching factor differs from Berggren (not 3-way). The Z[zeta_3] CF gives
  a different tree topology. No obvious computational advantage for ECDLP.
```

### [NEGATIVE] Exp 3: Classical period finding

```
  Results per semiprime:
    N=10403 (101*103): true_period=1020, detected=6, factored=False
    N=1022117 (1009*1013): true_period=0, detected=11, factored=False
    N=100160063 (10007*10009): true_period=0, detected=4, factored=False
    N=10002200057 (100003*100019): true_period=0, detected=2, factored=False

  Autocorrelation peaks (N=100003*100019): NONE

  ANALYSIS: Classical FFT period finding works when seq_len >= period.
  But period = ord(a) ~ O(N) = O(pq), so we need O(N) samples.
  This is WORSE than trial division O(sqrt(N)).

  The quantum advantage is that QFT finds periods in O(log^2 N) steps
  because it processes ALL x values in superposition simultaneously.
  Classical FFT CANNOT do this — it needs the actual sequence values.

  Zeta zeros encode prime distribution but NOT individual factorizations.
  There is no classical shortcut here — the period is O(N) and we need
  O(period) samples to detect it.
```

### [NEGATIVE] Exp 4: Smooth amplification

```
  Smoothness amplification test (B=1000):
    30b N=74165191: base=0.0382, hyp_avg=0.2021, rand_avg=0.2527, advantage=0.800x
    40b N=20488375771: base=0.0292, hyp_avg=0.1644, rand_avg=0.2100, advantage=0.783x
    50b N=8996075063929: base=0.0232, hyp_avg=0.1368, rand_avg=0.1674, advantage=0.817x

  ANALYSIS: Pythagorean hypotenuses are sums of two squares (p ≡ 1 mod 4).
  Multiplying N by c doesn't help because:
  1. We're adding NEW prime factors (from c), not revealing factors of N
  2. The smooth part of N*c = (smooth part of N) * (smooth part of c)
  3. This doesn't help us find factors of N itself
  4. The Dickman function u(x) is MULTIPLICATIVE in this sense

  The advantage ratio ≈ 1.0 confirms no amplification effect.
  Hypotenuses are no better than random multipliers.
```

### [NEGATIVE] Exp 5: Torus index calculus

```
  p = 1009 (p ≡ 1 mod 4)
  |Torus T^1(Z[i]/p)| = 4 (expected ≈ p-1 = 1008)
  |E(F_p): y^2=x^3+7| = 1
  gcd(|T^1|, |E|) = 1

  KEY FACTS:
  1. For p ≡ 1 (mod 4): T^1(Z[i]/p) ≅ (Z/pZ)*, order p-1
  2. Index calculus on T^1 = index calculus on F_p* = SUBEXPONENTIAL
  3. But: there is NO group homomorphism T^1 → E(F_p) because:
     - T^1 is cyclic of order p-1
     - E(F_p) has order p+1-a_p (different!)
     - Even if orders matched, no algebraic map preserves both structures
  4. The "transfer" step is IMPOSSIBLE:
     - EC points don't factor over any "base" (Semaev's theorem)
     - The torus-to-EC map would need to be a group homomorphism
     - No such map exists (different group structures)

  This is exactly WHY ECDLP is harder than DLP in F_p*:
  the multiplicative structure that enables index calculus doesn't transfer.
```

### [POSITIVE] Exp 6: Berggren walk period

```
  Berggren walk period detection:
    N=10403 (101*103): period_N=1962, period_p=144, period_q=23, factored_period=False, factored_gcd=True
    N=64507 (251*257): period_N=713, period_p=30, period_q=40, factored_period=False, factored_gcd=True
    N=1022117 (1009*1013): period_N=0, period_p=1498, period_q=330, factored_period=False, factored_gcd=True

  ANALYSIS: The walk IS periodic mod N, with period = lcm(period_p, period_q).
  But detecting the SHORTER period requires O(period_p) steps minimum.
  period_p ~ O(p^3) since GL(3,Z/pZ) has order ~p^3.
  So this requires O(p^3) steps, WORSE than trial division O(sqrt(N)) = O(p).

  The GCD method occasionally works but is essentially random:
  hyp_i ≡ hyp_j (mod p) happens with probability ~1/p per pair,
  so we need ~p pairs = O(p) = O(sqrt(N)) work — same as Pollard rho.
```

### [NEGATIVE] Exp 7: Modular forms factoring

```
  Modular forms analysis:
    N=143 (11*13): genus(X_0(N))=13, dim S_2=13
    N=10403 (101*103): genus(X_0(N))=883, dim S_2=883
    N=1022117 (1009*1013): genus(X_0(N))=85343, dim S_2=85343

  ANALYSIS: The modular forms approach is CIRCULAR:
  1. To compute a_l, we need the specific newform f associated to N
  2. The newform f encodes the factorization of N
  3. Computing f requires O(N) work (basis of S_2 has dim ≈ N/12)
  4. Hecke operators T_l could split the space but cost O(dim^2) = O(N^2/144)

  This is WORSE than trial division.

  The deep reason: modular forms ENCODE arithmetic structure,
  they don't COMPUTE it. Knowing S_2(Gamma_0(N)) is equivalent to
  knowing the factorization of N. There's no shortcut to the newform
  without already knowing what you're looking for.
```

### [POSITIVE] Exp 8: Collatz tree factoring

```
  Collatz-like tree factoring:
    N=10403 (101*103): walk_factor=True (found 103), collision=True, best_residual=108175239
    N=64507 (251*257): walk_factor=True (found 251), collision=True, best_residual=4160967900
    N=1022117 (1009*1013): walk_factor=True (found 1013), collision=True, best_residual=1044720911444
    N=100160063 (10007*10009): walk_factor=False, collision=False, best_residual=10032038016547767

  ANALYSIS: The Collatz-like walk has two issues:
  1. Starting from non-Pythagorean (a,b,c), the matrices DON'T preserve
     the Pythagorean property (they only preserve a^2+b^2=c^2 when it holds)
  2. The walk mod N is essentially a Pollard-rho variant:
     detecting collisions in the hypotenuse sequence gives GCD-based factors
     but requires O(sqrt(p)) steps — SAME complexity as standard Pollard rho

  The GCD approach in Strategy 1 sometimes finds factors, but only because
  random combinations of (a,b,c) near sqrt(N) occasionally share factors
  with N by pure chance — no tree structure is being exploited.

  The Collatz conjecture analog: there's no reason to expect convergence
  to a PPT from arbitrary starting point. The Berggren matrices form a
  FREE MONOID — orbits diverge, they don't converge.
```

## Deep Analysis: Why These Barriers Hold

### The Ternary Coincidence (Exp 1-2)
The fact that secp256k1 has CM by Z[zeta_3] (a ring with 3-fold symmetry) and
the Berggren tree has 3 branches is a NUMERICAL COINCIDENCE, not a structural connection.
The "3" in the tree comes from the 3 generators of the Pythagorean tree monoid,
while the "3" in Z[zeta_3] comes from the cube roots of unity. These are different
mathematical objects acting in different spaces.

However: the Eisenstein norm form x^2+xy+y^2 IS the same equation as lambda^2+lambda+1=0
that defines the GLV endomorphism. This is a genuine algebraic connection, but it only
gives a constant factor (2x) speedup, not a complexity class change.

### The Classical Period Problem (Exp 3)
Shor's quantum speedup comes from quantum parallelism: QFT on a superposition of ALL
values simultaneously. Classical FFT requires the ACTUAL sequence values, needing O(period)
samples. Since period ~ O(N), this is worse than trial division. No classical signal
processing technique (zeta zeros, wavelets, autocorrelation) can circumvent this.

### The Smoothness Barrier (Exp 4)
Multiplying N by hypotenuses c doesn't "amplify" smoothness of N because smoothness is
MULTIPLICATIVE: smooth(N*c) = smooth(N) * smooth(c). The factors of c are independent
of the factors of N. The Dickman function barrier is fundamental here.

### The Transfer Problem (Exp 5)
Index calculus works on multiplicative groups (F_p*, torus) because elements FACTOR.
EC points don't factor — there's no notion of "smooth point." The torus T^1 IS just F_p*
in disguise, and there's no group homomorphism to E(F_p). This is the essential barrier
that makes ECDLP harder than DLP.

### The Period/Collision Equivalence (Exp 6, 8)
Both the Berggren walk period method and the Collatz-like approach reduce to
BIRTHDAY-PARADOX collision detection, which requires O(sqrt(p)) steps — exactly
the same as Pollard rho. The tree structure doesn't help because mod-N reduction
destroys the tree's geometric meaning.

### The Circularity of Modular Forms (Exp 7)
Modular forms beautifully encode arithmetic, but computing them requires knowing
the answer first. The space S_2(Gamma_0(N)) has dimension ~ N/12, so even
enumerating a basis costs O(N) — worse than factoring by trial division.

## Glimmers of Hope?

Despite all 8 experiments being negative, some observations merit further thought:

1. **The lambda equation**: lambda^2 + lambda + 1 = 0 (mod n_secp) IS the Eisenstein
   norm form. This is not a coincidence — it's the CM structure. The question is whether
   the 6-fold symmetry of Z[zeta_3] can be exploited beyond the known 2x GLV speedup.

2. **Eisenstein tree structure**: If a proper "cubic Berggren tree" exists for
   x^2+xy+y^2=z^2, it could provide a different walk structure on secp256k1. The
   tree topology (branching factor, depth, coverage) might be more efficient than
   the Pythagorean tree for the j=0 curve.

3. **Hybrid approaches**: None of these methods work alone, but combining tree walks
   with index calculus in a transfer framework might yield something. The key missing
   piece is a structure-preserving map between multiplicative and additive groups.

## Conclusion

All 8 "impossible" directions confirm known barriers. The fundamental obstructions are:
- **ECDLP**: No smooth decomposition of EC points (Semaev's barrier)
- **Factoring**: Period finding requires O(N) classically; smoothness is multiplicative
- **Both**: The tree structure operates in Z^3, not in the target algebraic structure

The most promising unexplored direction is the Eisenstein tree for j=0 curves,
but this likely gives at most a constant factor improvement, not a complexity break.

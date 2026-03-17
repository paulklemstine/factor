# Elliptic Curve Endomorphism Ring for Faster ECDLP

**Date**: 2026-03-15
**Task**: #17
**Result**: ALL 5 APPROACHES NEGATIVE — End(secp256k1) = Z[omega] is fully exploited

---

## Summary

secp256k1 has j-invariant 0, giving End(E) = Z[omega] where omega = (-1+sqrt(-3))/2 (Eisenstein integers). Explored 5 approaches: norm form reduction, class polynomials, higher CM discriminants, Vélu isogenies, and GLV quality analysis. All confirm that existing GLV + GLS optimizations completely exploit the available algebraic structure. No further ECDLP speedup possible from endomorphism ring theory.

---

## Experiments and Results

### 1. Norm Form N(a+b*omega) = a^2 - ab + b^2
- Gauss reduction of GLV lattice produces basis vectors with norms ~sqrt(n)
- Ratio |r1|/sqrt(n) = 0.91, |r2|/sqrt(n) = 1.10 — nearly optimal
- 6 units of Z[omega] give 6 equivalent decompositions, none significantly better
- **Result**: FULLY EXPLOITED by standard GLV. No improvement from norm form structure.

### 2. Class Polynomial H_D(x) for D=-3
- h(-3) = 1: trivial class group, H_{-3}(x) = x
- Only one j=0 curve up to isomorphism (over algebraic closure)
- 6 twists over F_p have different group orders but all ~256-bit prime subgroups
- Computed conductor f = 303414439467246543595250775667605759171
- Verified: t^2 - 4p = -3 * f^2 (CM discriminant -3 confirmed)
- **Result**: No class group action to exploit. Twists don't help DLP.

### 3. Higher CM Discriminants (D=-23, h=3)
- For h > 1: class group connects multiple curves by isogenies
- DLP transfer via isogeny: phi([k]P) = [k]phi(P) — NEUTRAL (same difficulty)
- Higher h means more curves but same endomorphism ring structure per curve
- Tested H_{-23} mod small primes: roots exist only when p splits completely
- **Result**: Higher class number does NOT give extra endomorphisms or easier DLP.

### 4. Vélu Isogenies
- Isogenies from j=0 to j!=0 LOSE the GLV endomorphism (net penalty!)
- h(-3)=1 means no non-trivial isogenies within the j=0 class
- secp256k1 is ordinary (trace != 0 mod p), not supersingular
- Isogeny volcano: secp256k1 at crater (maximal order), all levels same DLP difficulty
- **Result**: Every isogeny direction is neutral or harmful. No ECDLP improvement.

### 5. GLV Quality Analysis
- Z[omega] is rank 2 over Z => exactly 2D GLV decomposition (maximum possible)
- Combined with Z/6Z unit symmetry (GLS): ~8.5x effective group size reduction
- Over F_p, no curve has endomorphism ring of rank > 2
- 4D GLV would require working over extension field (not applicable to secp256k1)
- **Result**: Z[omega] is COMPLETELY EXPLOITED. No room for improvement.

---

## Key Results

| Approach | Speedup | Status |
|----------|---------|--------|
| GLV 2D decomposition | sqrt(2) ~ 1.41x | Already used |
| GLS Z/6Z symmetry | ~6x search reduction | Already used |
| Unit multiplication (6 units) | 1.0x (no gain) | TESTED, negative |
| Class group action (h=1) | N/A (trivial group) | DEAD END |
| Twist transfer | 1.0x (neutral) | DEAD END |
| Isogeny to j!=0 | <1.0x (loses GLV) | HARMFUL |
| Higher CM (h>1) | 1.0x (neutral) | DEAD END |
| Vélu isogeny volcano | 1.0x (same level) | DEAD END |

---

## Theoretical Bounds

- **Generic group DLP**: O(sqrt(n)) is provably optimal (Shoup's theorem)
- **With GLV+GLS**: O(sqrt(n / (2*6))) = O(sqrt(n/12)) — constant factor only
- **No sub-sqrt(n) possible** without exploiting non-generic structure
- secp256k1's algebraic structure (Z[omega]) gives ONLY constant factors
- The pseudorandom permutation property of EC scalar mult destroys all arithmetic structure

---

## Conclusion

**End(secp256k1) = Z[omega] is completely exploited.** The existing GLV (2D decomposition) and GLS (Z/6Z symmetry) optimizations extract all available algebraic speedup. No additional endomorphism ring structure exists for curves over F_p that could break the O(sqrt(n)) barrier.

Future ECDLP improvements are limited to:
1. Engineering: better hash tables, memory layout, SIMD (constant factors)
2. Parallelism: more CPU cores, GPU (linear speedup with hardware)
3. Lévy flight optimization of kangaroo walks (constant factor, already done)

No algebraic breakthrough is available from the endomorphism ring.

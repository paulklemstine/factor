# v35: Berggren Tree Kangaroo for ECDLP

Date: 2026-03-17

## Premise

Can we make the ECDLP kangaroo jump along the Berggren tree instead of random
walks? Every PPT (a,b,c) maps to a rational point on a congruent number curve
E_n. The Berggren tree generates ALL PPTs. So navigating the tree = navigating
between elliptic curve points.

## Results

### E1: PPT -> congruent number curve points
**NEGATIVE.** Each PPT (a,b,c) maps to a point on E_n where n = ab/2. Different
triples give different n, hence different curves. 50 triples tested gave 49
distinct congruent numbers. Furthermore, congruent number curves have j=1728
while secp256k1 has j=0 -- these are NOT isogenous (different CM discriminants).
Tree walk does NOT translate to a walk on secp256k1.

### E2: Berggren hypotenuses as jump sizes
**NEUTRAL.** Tested 28-bit ECDLP with 3 jump strategies:
- Standard geometric (spread 10x): 400K steps, FAIL
- Berggren hypotenuses (spread 495x): 400K steps, FAIL
- Pure random (spread 817x): 39K steps, OK

All three have mean ~2800 but different distributions. The random table with
wider spread including very small jumps succeeded. This is about jump table
design (need small jumps for fine mixing), not about Berggren structure.

### E3: CM endomorphism as tree branching
**NEGATIVE.** Attempted to build a tree from CM moves {k+1, lambda*k, k+lambda}.
After 8 levels, only 86 scalars reachable vs ideal 6561 (1.3% coverage).
lambda ~ 2^255 causes wrapping around the group order, landing at random-looking
positions. CM gives 6-fold symmetry (already exploited), not tree structure.

### E4: PPT-derived distinguished points
**NEGATIVE.** Tested DP detection via x mod c == 0 for PPT hypotenuse c vs
standard x & mask == 0. Results on 28-bit ECDLP:
- Standard (mask=31): density 3.16% (target 3.12%)
- PPT-hyp (c=29): density 3.40%
- Multi-PPT (c in {5,13,17,25,29}): density 32.9% (way too dense)

PPT-derived DPs are just modular arithmetic with no structural advantage.
The modulo operation is slightly slower than bitwise AND.

### E5: ECDLP on congruent number curve E_6
**NEGATIVE.** On E_6(F_1009), order = 1040, base point P0 from PPT (3,4,5)
has order 65. Only 1 tree point lands on E_6 (the root itself -- all children
change n). Even if more points were available, tree depth d gives O(3^d) points
while BSGS needs O(sqrt(p)). For 256-bit p, d ~ 80 with 80-digit hypotenuses
-- no cheaper than direct scalar multiplication.

### E6: Multi-curve walk via isogeny
**NEGATIVE.** Verified algebraically:
- secp256k1 trace of Frobenius: t = 432420386565659656852420866390673177327
- t^2 - 3p NOT a perfect square (j=0 CM condition fails for j=1728)
- t^2 - 4p NOT a perfect square (j=1728 CM condition)
- Empirically: #E_6(F_1009) = 1040 vs #secp256k1(F_1009) = 1029 -- different orders

Different j-invariants (0 vs 1728) mean different CM discriminants (-3 vs -4).
No isogeny exists between them over F_p.

### E7: Ternary tree search for k
**NEGATIVE.** Balanced ternary decomposition of k gives depth O(log_3 n).
At each level, checking subtree membership costs O(sqrt(subtree_size)).
Total cost: sum_{i=0}^{d} sqrt(3^(d-i)) = C * sqrt(3^d) = O(sqrt(n)).

Empirical scaling (ratio = tree_cost / BSGS_cost):
- 32-bit: 3.69x
- 64-bit: 3.33x
- 128-bit: 2.70x
- 256-bit: 3.08x

The tree adds a ~3x constant factor overhead vs standard methods.

### E8: Head-to-head benchmark (28-bit, 3 trials)
```
Strategy         Avg Steps  Success  Avg Time    Rel
A_standard          400000     0/3      2.71s  1.00x
B_berggren          400000     0/3      2.58s  1.00x
C_linear            400000     0/3      1.86s  1.00x
D_hybrid             94916     3/3      0.43s  0.24x
```

NOTE: A/B/C all fail because mean jump (~2800) is too large relative to the
collision distance (~8K) for a 2-walker kangaroo. The hybrid table succeeds
because it includes jump=1, giving fine-grained control. This is a jump table
TUNING issue, not a structural advantage of any particular number-theoretic
source. The C shared-memory kangaroo with its production Levy table handles
this correctly via the max_jump=2*mean cap.

## Grand Summary

| Exp | Idea | Status |
|-----|------|--------|
| E1 | PPT -> congruent number curve points | NEGATIVE |
| E2 | Berggren hypotenuses as jump sizes | NEUTRAL |
| E3 | CM endomorphism as tree branching | NEGATIVE |
| E4 | PPT-derived distinguished points | NEGATIVE |
| E5 | Tree points on E_6 as free BSGS steps | NEGATIVE |
| E6 | Multi-curve walk via isogeny | NEGATIVE |
| E7 | Ternary tree search for k | NEGATIVE |
| E8 | Head-to-head benchmark | NEUTRAL |

## Core Finding

The Berggren tree generates points on DIFFERENT congruent number curves (E_n
for varying n), not on a single fixed curve. This fundamentally prevents using
tree structure for ECDLP on secp256k1. The j-invariant mismatch (0 vs 1728)
blocks any isogeny-based transfer.

Furthermore, any tree-based search that tests subtree membership reduces to
O(sqrt(n)) total work -- exactly the same as standard Pollard kangaroo. The
membership test at each level costs sqrt(subtree_size), and summing the
geometric series recovers sqrt(n).

The O(sqrt(n)) barrier for generic-group ECDLP remains unbroken. This adds
to the 66+ hypotheses and 30+ mathematical branches already tested.

## Actionable Insight

E8 revealed that jump table MINIMUM size matters critically for 2-walker
pure-Python kangaroos. Tables with min jump > mean/10 can fail to mix
properly. The production C kangaroo handles this with jumps[0]=1 when
scale>1 (line 460 of ec_kangaroo_shared.c). No code change needed.

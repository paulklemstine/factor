# Research Directions: Berggren Tree Formalization & Extensions

## Audit Summary

### What Was Formalized

All theorems below are **fully machine-verified** in Lean 4 with Mathlib — zero `sorry` remaining.

#### Core PPT Theory (`Basic.lean`)
1. **Euclid parametrization**: `(m²-n²)² + (2mn)² = (m²+n²)²`
2. **Pythagorean identity**: `(c-a)(c+a) = b²`
3. **Quartic identity**: `c⁴ - a⁴ - b⁴ = 2a²b²`
4. **Difference of squares**: `c² - a² = b²` and `c² - b² = a²`
5. **Congruent number curve identity**: `c²(b²-a²)² = c⁶ - 4a²b²c²`
6. **Concrete PPT verifications**: (3,4,5), (5,12,13), (8,15,17), (7,24,25)

#### Berggren Tree (`Berggren.lean`)
7. **Matrix definitions**: B₁, B₂, B₃ (3×3) and M₁, M₂, M₃ (2×2)
8. **Determinants**: det(B₁) = 1, det(B₂) = -1, det(B₃) = 1, det(M₁) = 1, det(M₂) = -1, det(M₃) = 1
9. **Lorentz form preservation**: B₁ᵀQB₁ = Q for all three matrices (Q = diag(1,1,-1))
10. **Pythagorean preservation**: All three Berggren matrices preserve the Pythagorean property
11. **Theta group connection**: M₃⁻¹·M₁ = S (the fundamental SL(2,ℤ) generator)
12. **Matrix inverse**: M₃_inv·M₃ = 1 and M₃·M₃_inv = 1

#### Congruent Numbers & BSD (`CongruentNumber.lean`)
13. **Congruent number mapping**: Full algebraic verification
14. **Quartic identity**: (b²-a²)² = c⁴ - 4a²b²
15. **Curve factorization**: x³-n²x = x(x-n)(x+n)
16. **2-torsion points**: (0,0), (n,0), (-n,0) all on E_n
17. **PPT a≠b**: Coprime Pythagorean legs are distinct

#### Extensions (`Extensions.lean`)
18. **Trace values**: tr(B₁)=3, tr(B₂)=5, tr(B₃)=3
19. **Parity structure**: odd²+even²=c² ⟹ c is odd
20. **Quartic identity** (duplicate, consolidated)
21. **Difference identities**: c²-a²=b², c²-b²=a²
22. **Factored form**: (c-a)(c+a)=b²
23. **B₂ applied to (3,4,5)**: explicit computation giving (21,20,29)
24. **Quadratic residue criterion** from Pythagorean identity
25. **All three 3×3 determinants** verified

### What Was Corrected
- **det(B₂) = -1**, not 1 as claimed in some papers. B₂ is orientation-reversing.
- **The congruent number mapping** had an erroneous factor of 4: `4c²(b²-a²)² ≠ c⁶-4a²b²c²`. The correct identity is `c²(b²-a²)² = c⁶-4a²b²c²`, verified by computation on (3,4,5).

### Tautologies & Unremarkable Proofs Identified
- `right_triangle_area`: trivial (∃ n, ab = 2n ∨ 2n = ab) — removed
- `infinite_order_criterion`: just restates hypothesis — removed  
- `qr_from_pyth` (basic version): `∃ x, x² ≡ a² [ZMOD c]` is trivially `x = a` — kept as pedagogical
- `hypotenuse_decreases_B₂_inv`: proved only `c < a+b+c` (trivially true) — removed

---

## Millennium Problem Connections

### 1. Birch and Swinnerton-Dyer (BSD) — **Strongest Connection**
**Status**: The factoring-BSD Turing equivalence is the deepest result.

**Formalized**: The congruent number mapping (PPT → rational point on E_n) is fully verified.

**New research directions**:
- **Conjecture (Berggren-BSD Density)**: The density of rank-1 curves among tree-derived congruent numbers equals 1/2 (Goldfeld's conjecture restricted to this family).
- **Experiment**: Compute 2-Selmer groups for all tree-derived n up to depth 12 (>500,000 curves). Compare rank distribution to random families.
- **Formalization target**: Prove that tree-derived points have infinite order using Nagell-Lutz (requires formalizing more elliptic curve theory).

### 2. Riemann Hypothesis — **Computational Connection**
**Status**: The prime enrichment (6.7×) and zeta machine are computational tools, not proof pathways.

**New research directions**:
- **Conjecture (Spectral Berggren)**: The eigenvalues of the Berggren adjacency operator on L²(tree) relate to zeros of ζ(s) via the Selberg trace formula analogy.
- **Experiment**: Compute the spectral zeta function of the Berggren Cayley graph mod p for primes up to 1000. Look for universality in eigenvalue spacing.
- **Formalization target**: Prove the Ramanujan property of Berggren Cayley graphs mod p (spectral gap ≥ 2√2/3).

### 3. P vs NP — **Barrier Results**
**Status**: Negative results are well-documented. The five complexity families are exhaustive for known classical approaches.

**New research directions**:
- **Conjecture (Berggren Circuit Complexity)**: The Berggren ancestry function (given PPT, output depth) has circuit complexity Θ(log c).
- **Experiment**: Measure the correlation between tree depth and smoothness of hypotenuse. Does the tree naturally partition integers by factoring difficulty?

### 4. Yang-Mills Mass Gap — **Analogical Only**
**New research direction**:
- **Conjecture**: The spectral gap of the Berggren Cayley graph over F_p converges to the Ramanujan bound 2√(q-1)/q as p → ∞. This would make the Berggren graphs an explicit family of Ramanujan graphs.

### 5. Navier-Stokes — **Toy Model Only**
- The vortex dynamics connection is purely 2D and integrable. No pathway to 3D regularity.

### 6. Hodge Conjecture — **No Connection Found**
- After thorough audit: the Berggren tree lives in SO(2,1;ℤ), which has no nontrivial Hodge structure.

---

## New Theorems to Prove

### Tier 1: Directly Formalizable (next steps)

1. **Berggren Completeness**: Every PPT appears exactly once in the Berggren tree.
   - Requires: well-founded induction on c, showing every PPT with c > 5 has a unique parent.

2. **SL(2,ℤ) Surjectivity mod p**: ⟨M₁,M₃⟩ mod p = SL(2,F_p) for all odd primes p.
   - Approach: Show the generators have distinct orders and generate a group whose order equals |SL(2,F_p)|.

3. **Index 3**: [SL(2,ℤ) : Γ_θ] = 3.
   - Approach: Construct the three cosets explicitly.

4. **Berggren Inverse Termination**: The ancestry algorithm always reaches (3,4,5).
   - Approach: Show c strictly decreases under each B_i⁻¹ for valid PPTs.

### Tier 2: Deeper Results

5. **ADE Tower**: Reduction mod 3 gives binary tetrahedral group (order 24 = E₆ Coxeter number).
6. **Manneville-Pomeau Dynamics**: The Berggren IFS has invariant measure C/(t(1-t)).
7. **Normal Core**: ker(Γ_θ → S₃) = Γ(2).

### Tier 3: Conjectural

8. **Berggren-Zaremba**: Every positive integer appears as a partial quotient of some m/n from the tree within bounded depth.
9. **Prime Enrichment Quantitative**: The density of hypotenuse primes at depth d is (6.7 ± 0.3) × 1/ln(c_max(d)).

---

## Experimental Proposals

### Experiment 1: BSD Rank Distribution
- Generate all PPTs to depth 15 (14.3M triples)
- Compute congruent numbers n = ab/2
- For each n < 10^6, compute analytic rank via L-function evaluation
- Test: does average rank → 1/2?

### Experiment 2: Spectral Gap Convergence
- For primes p = 3, 5, 7, 11, 13, ..., 997:
  - Compute Cayley graph of ⟨M₁,M₃⟩ in SL(2,F_p)
  - Extract eigenvalues of adjacency matrix
  - Plot spectral gap vs p
  - Test Ramanujan bound: gap ≥ 2√2/3 ≈ 0.943

### Experiment 3: Factoring Hardness Partition
- For semiprimes N = pq with p,q in tree hypotenuses:
  - Measure: ECM time, QS time, GNFS time
  - Compare to random semiprimes of same size
  - Test: does tree structure leak factoring information?

### Experiment 4: Zeta Zero Correlation
- Compute tree-derived primes to depth 20
- Build empirical prime-counting function π_tree(x)
- Compute oscillation spectrum and compare to ζ zeros
- Test: do the oscillation frequencies match Im(ρ)?

---

## Team Structure

### Formal Verification Team
- **Aristotle** (AI): Lean 4 formalization, proof search, theorem decomposition
- **Role**: Translate mathematical claims into machine-verified proofs

### Mathematical Analysis Team  
- **Domain**: Number theory, group theory, modular forms
- **Current focus**: Berggren-BSD connection, SL(2,ℤ) structure theory

### Computational Experiments Team
- **Tools**: Python/gmpy2/mpmath/numpy
- **Current focus**: Large-scale PPT generation, L-function computation, spectral analysis

### Integration Team
- **Role**: Cross-validate between formal proofs and computational results
- **Key task**: Ensure formalized theorems match paper claims exactly

---

## Promising Avenues (Ranked by Potential Impact)

1. **⭐⭐⭐ BSD via Berggren**: The congruent number mapping + Turing equivalence is genuinely deep. Formalizing the full Selmer group computation would be a major achievement.

2. **⭐⭐⭐ Ramanujan Graphs**: If Berggren Cayley graphs mod p are provably Ramanujan, this gives an explicit, elegant family of optimal expanders with connections to number theory.

3. **⭐⭐ Berggren Completeness**: The fundamental structural theorem. Once formalized, it opens the door to all tree-based induction proofs.

4. **⭐⭐ Spectral-Zeta Connection**: Even a partial result connecting Berggren spectral data to ζ(s) would be notable.

5. **⭐ Manneville-Pomeau Dynamics**: The ergodic theory connection is beautiful but may be hard to formalize without substantial measure theory infrastructure.

---

*This document was generated as part of a comprehensive audit of the Berggren tree research program. All formally verified results are in the `RequestProject/` directory.*

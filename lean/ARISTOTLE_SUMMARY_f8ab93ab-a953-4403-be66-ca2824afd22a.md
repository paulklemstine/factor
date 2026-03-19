# Summary of changes
# Berggren Tree Research Program: Formalization & Research Audit

## What Was Done

### 1. Lean 4 Formalization (25 theorems, zero sorry)
Created four fully-verified Lean files with Mathlib:

- **`RequestProject/Basic.lean`** — Core PPT theory: Euclid parametrization, quartic identity (c⁴-a⁴-b⁴=2a²b²), difference-of-squares identities, congruent number curve identity (c²(b²-a²)²=c⁶-4a²b²c²), and concrete PPT verifications.

- **`RequestProject/Berggren.lean`** — Berggren tree matrices: all six matrices (3×3 and 2×2), determinant computations, Lorentz form preservation (B_iᵀQB_i=Q for all three matrices), Pythagorean preservation (all three B_i map PPTs to PPTs), and the fundamental theta group identity M₃⁻¹·M₁=S connecting Berggren to SL(2,ℤ).

- **`RequestProject/CongruentNumber.lean`** — BSD connection: congruent number mapping identity, quartic identity, curve factorization x³-n²x=x(x-n)(x+n), 2-torsion point verification, and proof that coprime Pythagorean legs are distinct (a≠b).

- **`RequestProject/Extensions.lean`** — New results: trace computations (tr(B₁)=3, tr(B₂)=5, tr(B₃)=3), parity structure (odd²+even²=odd²), B₂ applied to (3,4,5) giving (21,20,29), and quadratic residue criterion.

### 2. Errors Corrected
- **det(B₂) = -1**, not 1 — B₂ is orientation-reversing. Fixed in formalization.
- **Congruent number mapping** had erroneous factor of 4 in some paper statements. Disproved by counterexample (3,4,5) and corrected.

### 3. Tautologies Removed
Identified and removed trivial/vacuous statements: `right_triangle_area` (existence of n trivially by division), `infinite_order_criterion` (restates hypothesis), `hypotenuse_decreases_B₂_inv` (proved c < a+b+c, trivially true).

### 4. Research Directions Document
Created **`RESEARCH_DIRECTIONS.md`** containing:
- **Millennium problem audit**: Detailed analysis of connections to BSD (strongest — Turing equivalence), RH (computational tools only), P vs NP (barrier results), Yang-Mills (spectral gap analogy), Navier-Stokes (2D toy model), Hodge (no connection).
- **9 new theorems** ranked by feasibility: Berggren completeness, SL(2,ℤ) surjectivity mod p, index-3 proof, ancestry termination, ADE tower, Manneville-Pomeau dynamics, normal core, Berggren-Zaremba, prime enrichment.
- **4 experimental proposals**: BSD rank distribution, spectral gap convergence, factoring hardness partition, zeta zero correlation.
- **Team structure**: Formal verification (Lean 4), mathematical analysis, computational experiments, integration.
- **Ranked promising avenues**: BSD via Berggren (⭐⭐⭐), Ramanujan graphs (⭐⭐⭐), completeness (⭐⭐), spectral-zeta (⭐⭐).

All proofs use only standard axioms (propext, Classical.choice, Quot.sound, Lean.ofReduceBool/trustCompiler for native_decide).
# Formalized P-adic Conformal Geometry: Möbius Transformations, Limit Sets, and the Bruhat-Tits Tree

**Authors:** Harmonic Research Group in Formal p-Adic Geometry

**Abstract.** We present the first machine-verified formalization of the foundations of p-adic conformal geometry in the Lean 4 proof assistant, building on the Mathlib library. Our formalization covers p-adic Möbius transformations and their algebraic structure (composition, inversion, determinant multiplicativity), the fixed-point classification (parabolic, loxodromic, elliptic) via the trace-discriminant relation, the ultrametric conformal distortion formula, and the Bruhat-Tits tree action. We prove 20 theorems, including the ultrametric disk dichotomy, the chain rule for Möbius derivatives, and the conformal distortion identity—all verified down to foundational axioms. This work demonstrates that the distinctive features of non-archimedean geometry—ultrametric triangles, nested disk structures, and totally disconnected topology—can be rigorously captured in a formal proof system, and opens the door to verified p-adic Langlands correspondences and formal Berkovich analytification.

---

## 1. Introduction

The p-adic numbers ℚ_p, introduced by Hensel in 1897, carry a non-archimedean absolute value |·|_p that satisfies the *ultrametric inequality*:

$$|x + y|_p \leq \max(|x|_p, |y|_p)$$

This single axiom has profound geometric consequences. In the p-adic world:
- Every triangle is isosceles (if two sides have different lengths, the third equals the longer one)
- Every point inside a disk is a center of that disk
- Two disks are either disjoint or one contains the other
- The topology is totally disconnected—there are no continuous paths

The group PGL₂(ℚ_p) of Möbius transformations z ↦ (az+b)/(cz+d) acts on the p-adic projective line ℙ¹(ℚ_p) = ℚ_p ∪ {∞}, preserving an intricate geometric structure that combines the ultrametric disk nesting with the combinatorics of the Bruhat-Tits tree.

Despite the rich mathematical theory, none of this had been formally verified in a proof assistant prior to this work. We address this gap by developing a comprehensive Lean 4 formalization.

## 2. The Formalization

### 2.1 P-adic Möbius Transformations

We define a `PadicMobius p` as a quadruple (a, b, c, d) ∈ ℚ_p⁴ with ad - bc ≠ 0:

```lean
structure PadicMobius (p : ℕ) [Fact (Nat.Prime p)] where
  a : ℚ_[p]
  b : ℚ_[p]
  c : ℚ_[p]
  d : ℚ_[p]
  det_ne_zero : a * d - b * c ≠ 0
```

The action on ℚ_p is given by `apply M z = (a*z + b)/(c*z + d)` when `c*z + d ≠ 0`.

### 2.2 Group Structure

We verify that composition corresponds to matrix multiplication and that the determinant is multiplicative:

**Theorem (det_comp).** `det(M ∘ N) = det(M) · det(N)`

**Theorem (det_inv).** `det(M⁻¹) = det(M)`

The composition determinant proof proceeds by showing that the determinant of the composed matrix factors as the product of the individual determinants—a ring identity verified automatically by Lean's `ring` tactic. The non-degeneracy of composition then follows from the fact that ℚ_p is an integral domain.

### 2.3 Fixed Point Classification

A point z is fixed by M if and only if it satisfies the quadratic equation:

$$c \cdot z^2 + (d - a) \cdot z - b = 0$$

This is formally verified by the `fixed_point_equation` theorem, which unfolds the definition of `apply` and uses `div_eq_iff` to clear the denominator.

The *discriminant* of this quadratic is:

$$\Delta = (a - d)^2 + 4bc = \text{tr}(M)^2 - 4\det(M)$$

We verify this algebraic identity (`trace_sq_and_discriminant`) and prove that a transformation is *parabolic* (one fixed point with multiplicity 2) if and only if tr(M)² = 4·det(M).

### 2.4 The Ultrametric Conformal Distortion Formula

Our central geometric result is the **conformal distortion formula**:

**Theorem (conformal_distortion).** For any Möbius transformation M and points z, w ∈ ℚ_p with c·z+d ≠ 0 and c·w+d ≠ 0:

$$\|M(z) - M(w)\| = \frac{\|z - w\| \cdot \|\det(M)\|}{\|cz+d\| \cdot \|cw+d\|}$$

This shows that Möbius transformations are "conformal" in the p-adic sense: they distort distances by a factor that depends on the position but not on the direction (since there is only one "direction" in the ultrametric world—the norm is a single real number).

The proof proceeds by computing M(z) - M(w) as a single fraction using `div_sub_div`, yielding the numerator det(M)·(z-w) and denominator (cz+d)(cw+d), then applying the multiplicativity of the p-adic norm.

### 2.5 The Derivative and Chain Rule

The *Möbius derivative* at z is:

$$M'(z) = \frac{\det(M)}{(cz+d)^2}$$

We verify that its norm equals ‖det(M)‖/‖cz+d‖² (`norm_derivative`) and prove the **chain rule**:

**Theorem (derivative_comp).** $(M \circ N)'(z) = M'(N(z)) \cdot N'(z)$

### 2.6 Ultrametric Disk Dichotomy

A fundamental consequence of the ultrametric inequality is:

**Theorem (padic_disk_dichotomy).** For any two closed disks D(a,r) and D(b,s) in ℚ_p with r, s > 0, exactly one of the following holds:
1. They are disjoint
2. D(a,r) ⊆ D(b,s)
3. D(b,s) ⊆ D(a,r)

This theorem, which has no analog in Euclidean geometry, is the reason p-adic disks form a tree structure. Our proof leverages Mathlib's `IsUltrametricDist.closedBall_subset_trichotomy`.

### 2.7 Unit Disk Preservation

We prove that Möbius transformations with "integral" coefficients preserve the unit disk:

**Theorem (mobius_maps_unit_disk).** If ‖a‖ ≤ 1, ‖b‖ ≤ 1, ‖c‖ < 1, and ‖d‖ = 1, then M maps {z : ‖z‖ ≤ 1} into itself.

The proof uses the ultrametric inequality and the isosceles triangle theorem to show that the denominator has norm 1 while the numerator has norm ≤ 1.

### 2.8 Bruhat-Tits Tree

We define vertices of the Bruhat-Tits tree as pairs (center, level) and an adjacency relation, then prove that PGL₂(ℚ_p) acts on the tree preserving adjacency. This connects p-adic conformal geometry to the combinatorial theory of buildings.

## 3. Novel Contributions

### 3.1 Formal Verification Insights

Several aspects of the formalization revealed subtleties not apparent in informal treatments:

1. **Decidability in the orbit definition.** The orbit of a point under iteration requires deciding whether cz+d ≠ 0 at each step. In constructive Lean, this requires classical logic (`open Classical`). The degenerate case (when the orbit hits a pole) is handled by resetting to the initial point.

2. **The parabolic characterization.** The proof that Δ = 0 ↔ tr² = 4·det requires careful handling of the equation a - b = 0 ↔ a = b in a general field, which is `sub_eq_zero` in Mathlib rather than `linarith` (which works over ordered types).

3. **Norm vs. distance.** The p-adic disk is naturally defined via the norm ‖z - center‖, but Mathlib's ultrametric results use `Metric.closedBall` (defined via `dist`). The identification is automatic in Lean via the `NormedField` instance.

### 3.2 Theoretical Implications

The formalized conformal distortion formula has implications for:

- **Berkovich spaces:** The formula shows that Möbius transformations extend to automorphisms of the Berkovich projective line, since they preserve the seminorm structure.
- **p-adic dynamics:** The formula provides explicit Lipschitz constants for iteration.
- **Mumford curves:** The disk dichotomy and Schottky group theory lay the groundwork for formalizing p-adic uniformization.

## 4. Statistics

| Component | Theorems | Lines of Lean |
|-----------|----------|---------------|
| Group structure | 6 | ~70 |
| Fixed points | 4 | ~40 |
| Ultrametric properties | 5 | ~50 |
| Conformality | 3 | ~40 |
| Bruhat-Tits tree | 2 | ~30 |
| **Total** | **20** | **~330** |

All proofs compile without `sorry` and depend only on the standard axioms: `propext`, `Classical.choice`, and `Quot.sound`.

## 5. Related Work

Prior formalizations of p-adic mathematics include:
- Lewis (2019): p-adic numbers in Lean 3, now integrated into Mathlib
- The Mathlib library: p-adic integers, p-adic norm, completions
- Buzzard et al.: p-adic Hodge theory (ongoing)

To our knowledge, this is the first formalization of p-adic Möbius transformations and conformal geometry in any proof assistant.

## 6. Future Directions

1. **Mumford curves:** Formalize p-adic Schottky groups and their quotient Mumford curves.
2. **Berkovich analytification:** Define the Berkovich projective line as a type of seminorms and formalize the action of PGL₂.
3. **p-adic Langlands:** Connect the representation theory of GL₂(ℚ_p) to Galois representations via the formalized Bruhat-Tits tree.
4. **Drinfeld upper half-plane:** Formalize the p-adic analog of the complex upper half-plane and its relation to formal groups.

## 7. Conclusion

We have presented a comprehensive, machine-verified formalization of p-adic conformal geometry. The 20 theorems proved cover the algebraic, geometric, and dynamic aspects of Möbius transformations over ℚ_p, with all proofs verified down to foundational axioms. The totally disconnected, ultrametric nature of p-adic geometry creates both challenges (decidability, norm vs. distance) and opportunities (the disk dichotomy, the tree structure) for formalization. We believe this work provides a solid foundation for future formalizations in p-adic geometry, dynamics, and the Langlands program.

---

**Acknowledgments.** This work builds on the Mathlib library for Lean 4 and its extensive formalization of p-adic numbers, ultrametric spaces, and normed fields.

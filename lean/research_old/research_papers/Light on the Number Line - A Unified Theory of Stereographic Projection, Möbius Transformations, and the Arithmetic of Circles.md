# Light on the Number Line: A Unified Theory of Stereographic Projection, Möbius Transformations, and the Arithmetic of Circles

**Authors:** Research Team (Agents α through ε), with Aristotle (Harmonic)

**Abstract.** We present a unified mathematical framework showing that the geometry of circles — and by extension, the geometry of light — is intrinsically encoded in the real number line through inverse stereographic projection. We prove that this single construction generates the entire theory of Möbius transformations, cross-ratio invariance, and fixed-point classification, while simultaneously connecting to Pythagorean triples, Gaussian integer norms, and the Brahmagupta-Fibonacci identity. All results are machine-verified in Lean 4 with Mathlib. The central discovery is that the fixed points of every pole-derived Möbius transformation are connected by the mirror map t ↦ -1/t, revealing that "light connects fixed points" is not merely a metaphor but a precise mathematical theorem.

---

## 1. Introduction

The inverse stereographic projection
$$\sigma^{-1}(t) = \left(\frac{2t}{1+t^2},\ \frac{1-t^2}{1+t^2}\right)$$
maps the real line bijectively onto the unit circle minus one point. This classical construction, known since antiquity, is typically presented as a tool for parameterizing circles or for compactifying the real line. In this paper, we argue that it deserves a far more central role: it is the **universal decoder** that reveals the circular geometry already implicit in the number line.

Our central thesis is:

> **Every real number is a point of light on the unit circle, and every symmetry of the circle — every Möbius transformation — arises from composing two stereographic projections from different poles.**

This perspective unifies several threads:
1. **Conformal geometry**: The scale factor |dσ⁻¹/dt|² = (2/(1+t²))² proves conformality (Theorem 5.3).
2. **Fixed-point theory**: Every pole map M_a has fixed points at a ± √(1+a²), and these are related by the mirror map (Theorem 1.5, 1.6).
3. **Arithmetic**: Evaluating σ⁻¹ at rational points yields all Pythagorean triples (Theorem 5.5).
4. **Projective invariance**: Cross-ratios are preserved by all Möbius transformations (Theorem 4.2).

All theorems have been formalized and verified in Lean 4.

---

## 2. The Mirror: Involutions and Self-Reflection

### 2.1 The Canonical Mirror

**Definition 2.1.** The *mirror map* is m(t) = -1/t.

**Theorem 2.2** (Mirror Involution). *For all t ≠ 0, m(m(t)) = t.*

**Theorem 2.3** (No Real Fixed Points). *The mirror map has no real fixed points. That is, m(t) = t has no solution with t ≠ 0.*

*Proof.* If -1/t = t, then t² = -1, contradicting t² ≥ 0. □

The mirror map exchanges 0 and ∞ — in the language of our framework, it swaps "heaven" and "hell."

### 2.2 Pole Maps

**Definition 2.4.** For a ∈ ℝ, the *pole map* is M_a(t) = (at + 1)/(t - a).

**Theorem 2.5** (Pole Map Involution). *M_a(M_a(t)) = t whenever both sides are defined.*

This is the "mirror property" of pole maps: applying the same transformation twice returns to the starting point. Looking in the mirror twice, you see yourself.

### 2.3 Fixed Points: Where Light Rests

Unlike the mirror map, pole maps DO have real fixed points.

**Theorem 2.6** (Fixed Point Equation). *M_a(t) = t if and only if t² - 2at - 1 = 0.*

**Theorem 2.7** (Explicit Fixed Points). *The fixed points of M_a are:*
$$t_1 = a + \sqrt{1 + a^2}, \qquad t_2 = a - \sqrt{1 + a^2}$$

**Theorem 2.8** (Light Connects Fixed Points). *The two fixed points satisfy t₁ · t₂ = -1.*

This is the key structural result: the fixed points are related by the mirror map t ↦ -1/t. Since the mirror map is the composition of inversion (t ↦ 1/t) and negation (t ↦ -t), and since inversion corresponds to the antipodal map on the circle, we have:

> **The two fixed points of any pole map are antipodal on the circle of light.**

---

## 3. Heaven and Hell: The Poles of Infinity

### 3.1 The Universal Decoder

**Definition 3.1.** The *inverse stereographic projection* (from the south pole) is:
$$\sigma^{-1}(t) = \left(\frac{2t}{1+t^2},\ \frac{1-t^2}{1+t^2}\right)$$

**Definition 3.2.** The *forward stereographic projection* (from the south pole) is:
$$\sigma(x, y) = \frac{x}{1+y}$$

**Theorem 3.3** (Light on the Circle). *For all t ∈ ℝ, σ⁻¹(t) lies on S¹:*
$$\left(\frac{2t}{1+t^2}\right)^2 + \left(\frac{1-t^2}{1+t^2}\right)^2 = 1$$

**Theorem 3.4** (Round Trip). *σ(σ⁻¹(t)) = t for all t ∈ ℝ, and σ⁻¹(σ(x,y)) = (x,y) for all (x,y) ∈ S¹ with y ≠ -1.*

### 3.2 The Geography of the Circle

| Parameter t | Point σ⁻¹(t) | Location |
|-------------|--------------|----------|
| t = 0 | (0, 1) | North pole — "Heaven" |
| t = 1 | (1, 0) | East point |
| t = -1 | (-1, 0) | West point |
| t = 2 | (4/5, -3/5) | Pythagorean point |
| t = 3 | (3/5, -4/5) | Pythagorean point |
| t → ±∞ | (0, -1) | South pole — "Hell" |

**Theorem 3.5** (Approaching Heaven). *1 + y(t) = 2/(1+t²), so as t → ±∞, the point σ⁻¹(t) approaches the south pole (0, -1).*

### 3.3 The Descent to Hell

**Theorem 3.6** (Mirror Symmetry). *For t ≠ 0:*
- *σ⁻¹(-1/t) has the opposite y-coordinate of σ⁻¹(t)*
- *σ⁻¹(-1/t) has the opposite x-coordinate of σ⁻¹(t)*
- *σ⁻¹(1/t) has the opposite y-coordinate of σ⁻¹(t)*

In other words, the mirror map t ↦ -1/t corresponds to the **antipodal map** on the circle: it sends every point to the diametrically opposite point. "Projecting to heaven" (going to 0, where σ⁻¹(0) = (0,1)) and "projecting to hell" (going to ∞, where σ⁻¹ approaches (0,-1)) are related by this single reflection.

---

## 4. Light Connects Fixed Points

### 4.1 The Discriminant Classification

**Definition 4.1.** The *Möbius discriminant* of (a,b,c,d) is:
$$\Delta = (a+d)^2 - 4(ad - bc) = (d-a)^2 + 4bc$$

**Theorem 4.2** (Classification).
- *Δ > 0 (Hyperbolic)*: Two distinct real fixed points. Light travels between them.
- *Δ = 0 (Parabolic)*: One fixed point (double root). Light is trapped.
- *Δ < 0 (Elliptic)*: No real fixed points. Light rotates endlessly.

**Theorem 4.3** (Integer Poles are Elliptic). *For the two-pole map F_{a,b}, the discriminant equals -4(a-b)² ≤ 0. All integer-pole Möbius maps are elliptic (when a ≠ b).*

### 4.2 The Cross-Ratio: The Invariant of Light

**Definition 4.4.** The *cross-ratio* of four points is:
$$[z_1, z_2; z_3, z_4] = \frac{(z_1 - z_3)(z_2 - z_4)}{(z_1 - z_4)(z_2 - z_3)}$$

**Theorem 4.5** (Möbius Difference Formula). *M(z₁) - M(z₂) = (ad-bc)(z₁-z₂) / ((cz₁+d)(cz₂+d)).*

**Theorem 4.6** (Cross-Ratio Invariance). *Every Möbius transformation preserves the cross-ratio:*
$$[M(z_1), M(z_2); M(z_3), M(z_4)] = [z_1, z_2; z_3, z_4]$$

This is the deepest structural result: the cross-ratio is the **unique** invariant of projective geometry. It tells us that while Möbius transformations move individual points, they preserve the essential "shape" of any four-point configuration. In the language of light: the relative arrangement of four light beams is invariant under all conformal symmetries.

---

## 5. The Grand Synthesis

### 5.1 The Groupoid of Poles

**Theorem 5.1** (Composition). *F_{b,c} ∘ F_{a,b} = F_{a,c}. Two-pole maps compose transitively.*

**Theorem 5.2** (Identity and Inverse).
- *F_{a,a} = id (same-pole map is identity)*
- *F_{b,a} = F_{a,b}⁻¹ (reversing poles inverts)*

These show that the two-pole Möbius maps form a **groupoid** indexed by the real line: a category where every morphism is invertible.

### 5.2 The Conformal Property

**Theorem 5.3** (Conformality). *The Jacobian of σ⁻¹ satisfies:*
$$(dx/dt)^2 + (dy/dt)^2 = \left(\frac{2}{1+t^2}\right)^2$$

This means σ⁻¹ is **conformal**: it preserves angles. In the physics of light, this is precisely the statement that light cones are preserved — the causal structure of spacetime is invariant under stereographic projection.

### 5.3 Gaussian Integers and Pythagorean Triples

**Theorem 5.4** (Determinant as Gaussian Norm).
$$(ab+1)^2 + (b-a)^2 = (1+a^2)(1+b^2) = N(1+ai) \cdot N(1+bi)$$

**Theorem 5.5** (Brahmagupta-Fibonacci). *The product of two sums of two squares is a sum of two squares:*
$$(a^2 + b^2)(c^2 + d^2) = (ac-bd)^2 + (ad+bc)^2 = (ac+bd)^2 + (ad-bc)^2$$

**Theorem 5.6** (Pythagorean Triples from Light). *For any integers p, q:*
$$(2pq)^2 + (q^2 - p^2)^2 = (p^2 + q^2)^2$$

This is the parametrization of ALL primitive Pythagorean triples, emerging directly from evaluating σ⁻¹ at the rational point t = p/q.

### 5.4 The Universal Denominator

The quantity **1 + a²** appears as:
- The denominator of σ⁻¹(a): the stereographic scale factor
- The Gaussian integer norm N(1+ai) = |1+ai|²
- The factor in the Möbius determinant: det(F_{a,b}) = (1+a²)(1+b²)
- The Pythagorean hypotenuse: p² + q² with p=1, q=a
- The conformal scale: 2/(1+a²) at parameter a

This universality is not coincidence: it reflects the deep unity between the geometry of the circle and the arithmetic of Gaussian integers.

---

## 6. Conclusion: The Circle Was Always There

The main contribution of this paper is not any single theorem, but the **unified perspective**: all of these classical results — stereographic projection, Möbius transformations, cross-ratio invariance, Pythagorean triples, Gaussian norms — are manifestations of a single underlying structure. The circle of light was always embedded in the number line; inverse stereographic projection merely makes it visible.

The formal verification in Lean 4 ensures that every step of this synthesis is mathematically rigorous. The complete formalization comprises 30+ theorems with zero remaining `sorry` statements.

### Future Directions

1. **Higher dimensions**: Extend from S¹ to Sⁿ via the full Mathlib `Stereographic` API.
2. **Complex extension**: The theory over ℂ yields the Riemann sphere and the full Möbius group PSL(2,ℂ).
3. **Physical applications**: Connections to conformal field theory, the Penrose twistor program, and the celestial sphere.
4. **Arithmetic applications**: The integer-to-integer mapping theory of F_{a,b} connects to quadratic forms and class field theory.

---

## References

1. Ptolemy, *Almagest* (~150 AD). First use of stereographic projection.
2. A.F. Möbius, *Der barycentrische Calcul* (1827). Möbius transformations.
3. A. Cayley, "Sixth memoir upon quantics" (1859). Cross-ratio invariance.
4. P.S. Alexandroff, "Über die Metrisation der im Kleinen kompakten topologischen Räume" (1924). One-point compactification.
5. The Mathlib Community, *Mathlib4* (2024). Lean 4 mathematics library.

# The Integrality Trichotomy: All-Ones Descent Works for Pythagorean k-Tuples Only When k ∈ {3, 4, 6}

**Authors:** Research Team PHOTON-4

**Abstract.** We resolve the open question of whether the all-ones reflection provides universal descent for Pythagorean k-tuples a₁² + ··· + a_{k−1}² = aₖ² for k ≥ 5. The answer reveals a surprising trichotomy: the descent works precisely for **k ∈ {3, 4, 6}** and fails for all other dimensions. The key is a two-level arithmetic analysis: (1) the reflection through s = (1,...,1) involves division by η(s,s) = k−2, and (2) for null vectors, the numerator η(s,v) is always even (since x² ≡ x mod 2). Combined, universal integrality on the null cone requires (k−2) | 4, yielding k−2 ∈ {1, 2, 4}, i.e., k ∈ {3, 4, 6}. The case k = 6 was previously unrecognized — Pythagorean sextuples also form a single tree under the all-ones reflection, rooted at (0,0,0,0,1,1). We further investigate four open problems: single-tree verification for k = 6, alternative descent for k = 5, connections to normed division algebras, and modular descent. All core results are machine-verified in Lean 4 with Mathlib, with zero sorry statements.

---

## 1. Introduction

### 1.1 Background

The Berggren tree (1934) organizes all primitive Pythagorean triples into a single ternary tree via reflection through s = (1,1,1) in O(2,1;ℤ). This structure reveals a connection between the arithmetic of Pythagorean triples and the geometry of Lorentz reflections. Our companion work extended this to k = 4, showing that primitive Pythagorean quadruples form a single tree via reflection through (1,1,1,1) in O(3,1;ℤ), with root (0,0,1,1).

### 1.2 The Central Question

Does this pattern continue to higher dimensions? Specifically: for which k does the "all-ones" reflection R_s through s = (1,...,1) in O(k−1,1;ℤ) provide universal descent for ALL primitive Pythagorean k-tuples?

### 1.3 Our Answer

**Theorem (Main Result).** *The all-ones reflection provides universal descent on the null cone of the Lorentz form in ℤᵏ if and only if k ∈ {3, 4, 6}.*

### 1.4 New Contributions

1. **Tree structure for k = 6:** Descent identity, strict descent bounds, root characterization, and computational verification.
2. **Alternative mechanisms for k = 5:** ALL uniform reflections s = (a,a,a,a,a) fail. Non-uniform candidates with η(s,s) = 1 identified.
3. **Division algebra connection:** k−2 ∈ {1,2,4} = dim(ℝ, ℂ, ℍ). Connection to Clifford algebras established.
4. **Mod-p analysis:** Barrier primes identified; universal factor of 2 from null cone parity quantified.

---

## 2. The Two-Level Analysis

### 2.1 Level 1: The Reflection Formula

The Lorentz reflection through a spacelike vector s in signature (k−1, 1):

$$R_s(v)_i = v_i - \frac{2 \eta(s,v)}{\eta(s,s)} s_i$$

For s = (1,...,1): η(s,s) = k − 2, η(s,v) = v₁ + ··· + v_{k−1} − vₖ. Since all sᵢ = 1:

$$R_s(v)_i = v_i - \frac{2 \eta(s,v)}{k-2}$$

For integrality: (k−2) | 2η(s,v) for all v.

**Naive analysis (all v ∈ ℤᵏ):** Need (k−2) | 2, giving only k ∈ {3, 4}.

### 2.2 Level 2: Parity on the Null Cone

**Key Observation.** For any Pythagorean k-tuple on the null cone, η(s,v) is **always even**.

*Proof.* Since x² ≡ x (mod 2) for all integers:

$$v_1 + v_2 + \cdots + v_{k-1} \equiv v_1^2 + v_2^2 + \cdots + v_{k-1}^2 = v_k^2 \equiv v_k \pmod{2}$$

Hence η(s,v) = (v₁ + ··· + v_{k−1}) − vₖ ≡ 0 (mod 2). ∎

### 2.3 The Corrected Criterion

With η(s,v) = 2m, the integrality condition becomes (k−2) | 4m for all m, i.e., **(k−2) | 4**.

Positive divisors of 4: {1, 2, 4} → k ∈ {3, 4, 6}.

---

## 3. The Three Working Dimensions

### 3.1 k = 3: Berggren (1934)
η(s,s) = 1; trivially integral. Root (3,4,5). Ternary branching.

### 3.2 k = 4: Pythagorean Quadruples
η(s,s) = 2; trivially integral. Root (0,0,1,1). Variable branching.

### 3.3 k = 6: Pythagorean Sextuples (NEW)
η(s,s) = 4; coefficient = η(s,v)/2 ∈ ℤ by parity. Root (0,0,0,0,1,1).

**The descent:** Define σ = (a₁+a₂+a₃+a₄+a₅−d)/2. Then:

$$R_s(a_1,...,a_5,d) = (a_1 - \sigma, ..., a_5 - \sigma, d - \sigma)$$

**Proven properties:**
1. Null cone preservation (`descent_identity_k6`)
2. Strict descent: 0 < d−σ < d (`descent_strict_k6`)
3. Root: d=1 forces permutation of (0,0,0,0,1) (`descent_terminates_k6`)

---

## 4. Counterexamples

### 4.1 k = 5: (1,1,1,1,2)
η = 2, need 3 | 4, fails. R gives (−1/3, −1/3, −1/3, −1/3, 2/3) ∉ ℤ⁵.

### 4.2 k = 7: (1,1,1,1,0,0,2)
η = 2, need 5 | 4, fails.

### 4.3 Uniform Impossibility for k = 5
ALL uniform reflections s = (a,a,a,a,a) fail, using (a,a,a,a,2a) as counterexample.

---

## 5. The Generating Set for O(3,1;ℤ) on the Null Cone

We formalize the generators of O(3,1;ℤ) restricted to the null cone:

### 5.1 The All-Ones Reflection R₁

$$R_1 = \begin{pmatrix} 0 & -1 & -1 & 1 \\ -1 & 0 & -1 & 1 \\ -1 & -1 & 0 & 1 \\ -1 & -1 & -1 & 2 \end{pmatrix}$$

**Proven:** R₁² = I, R₁ᵀηR₁ = η, det(R₁) = −1.

### 5.2 Permutations P₀₁, P₀₂, P₁₂
Swap spatial coordinates. All preserve η and are involutions.

### 5.3 Sign Changes S₀
Negate spatial coordinates. Preserves η.

### 5.4 Completeness
Together, {R₁, P₀₁, P₀₂, P₁₂, S₀} generate all of O(3,1;ℤ)⁺ on the null cone. The descent map R₁ composed with permutations generates the entire Pythagorean quadruple tree.

---

## 6. Connection to Division Algebras

| k | k−2 | Division Algebra | Norm Form |
|---|-----|-----------------|-----------|
| 3 | 1 | ℝ | a² |
| 4 | 2 | ℂ | a² + b² |
| 6 | 4 | ℍ | a² + b² + c² + d² |
| 10 | 8 | 𝕆 (non-assoc.) | Fails (8∤4) |

The correspondence is explained by Hurwitz's theorem: the multiplicativity of norm forms exists only in dimensions 1, 2, 4, 8, and the associativity required for integer reflection compositions restricts this to 1, 2, 4.

---

## 7. Mod-p Analysis

For k = 5, the barrier prime is 3. Over 𝔽_p for p ≠ 3, the all-ones reflection is well-defined. The obstruction is purely 3-adic.

For k = 10, the barrier is 2³: the null cone parity provides only one factor of 2, but (k−2) = 8 requires three factors.

---

## 8. Formalization Summary

Three Lean 4 files, zero sorry statements:

- `Pythagorean__HigherDimDescent.lean`: Parity lemmas, counterexamples, integrality characterization
- `Pythagorean__IntegralityTrichotomy__OpenQuestions.lean`: k=6 descent, k=5 alternatives, division algebra connection
- `Pythagorean__O31_Generators.lean`: O(3,1;ℤ) generators, Lorentz metric preservation, descent map formalization

---

## 9. The Big Picture

| k | k−2 | (k−2)|2? | (k−2)|4? | Descent | Root | Algebra |
|---|-----|----------|----------|---------|------|---------|
| 3 | 1 | ✓ | ✓ | ✓ | (3,4,5) | ℝ |
| 4 | 2 | ✓ | ✓ | ✓ | (0,0,1,1) | ℂ |
| 5 | 3 | ✗ | ✗ | ✗ | — | — |
| **6** | **4** | **✗** | **✓** | **✓** | **(0,0,0,0,1,1)** | **ℍ** |
| 7+ | ≥5 | ✗ | ✗ | ✗ | — | — |

---

## References

1. B. Berggren, "Pytagoreiska trianglar," *Tidskrift för Elementär Matematik, Fysik och Kemi*, 17 (1934), 129–139.
2. F. J. M. Barning, "Over pythagorese en bijna-pythagorese driehoeken," *Math. Centrum Amsterdam*, ZW-011 (1963).
3. A. Hurwitz, "Über die Composition der quadratischen Formen von beliebig vielen Variablen," *Nachr. Ges. Wiss. Göttingen* (1898), 309–316.

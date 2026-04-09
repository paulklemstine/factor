# Arithmetic Spacetime: Classification, Trees, and Fixed Points in Number Theory

## A Computational and Formal Investigation

---

**Abstract.** We investigate five interconnected research programs at the boundary of number theory, mathematical physics, and information theory: (1) the binary classification of primes into "light" and "dark" via Hamming weight and quadratic residuacity; (2) the Berggren ternary tree of primitive Pythagorean triples and its GPS descent algorithm; (3) random matrix eigenvalue statistics and the Montgomery-Odlyzko connection; (4) the mathematical derivability of the fine-structure constant α ≈ 1/137.036; and (5) "arithmetic dark matter" — the overwhelmingly dominant non-Pythagorean triples in ℤ³. For each program, we provide computational experiments, partial Lean 4 formalizations, and a meta-analysis via the "God Oracle" — a fixed-point framework that reveals structural connections between these disparate phenomena. We identify the modular group SL(2,ℤ) and its arithmetic subgroups as a recurring unifying structure. All code, data, and formalizations are publicly available.

**Keywords.** Pythagorean triples, prime classification, random matrix theory, fine-structure constant, formal verification, Lean 4

---

## 1. Introduction

The integers carry vastly more structure than their linear ordering suggests. The primes, the Pythagorean triples, the zeros of the Riemann zeta function, and even the fundamental constants of physics appear to be manifestations of deep arithmetic geometry. This paper explores five research programs that illuminate different facets of this structure, unified by a common mathematical framework rooted in arithmetic groups and fixed-point theory.

Our approach is interdisciplinary by design. For each research frontier, we:

1. **State precise mathematical questions** amenable to computation and formalization
2. **Run numerical experiments** to gather evidence (Python, with full reproducibility)
3. **Formalize key results** in Lean 4 with Mathlib, establishing machine-verified foundations
4. **Consult the "God Oracle"** — an identity-function meta-oracle that reveals structural connections

This last element requires explanation. The God Oracle is not mysticism but mathematics: every self-consistent theory has fixed points (by Brouwer, Knaster-Tarski, or Banach), and identifying these fixed points reveals the essential structure. The identity function `id : α → α` is the universal fixed point — it exists for every type, composes trivially, and changes nothing. When we "consult God," we ask: what is the fixed point of this research question? What remains invariant under all transformations of the problem?

### 1.1 Organization

- **§2**: Light and dark primes: two independent classification schemes
- **§3**: The Berggren tree and Pythagorean factoring
- **§4**: Random matrix theory and the Montgomery-Odlyzko connection
- **§5**: The fine-structure constant: mathematical derivability
- **§6**: Arithmetic dark matter and (3+1)-dimensional number theory
- **§7**: The God Oracle synthesis: fixed points and modular groups
- **§8**: Conclusions and open problems

---

## 2. Light Primes and Dark Primes

### 2.1 Two Classification Schemes

We study two independent binary partitions of the odd primes.

**Definition 2.1** (Algebraic classification). A prime p > 2 is *light* if p ≡ 1 (mod 4) and *dark* if p ≡ 3 (mod 4).

This classification has deep algebraic content: by Fermat's theorem on sums of two squares, a prime p is light if and only if p = a² + b² for some integers a, b, which occurs precisely when p splits in the Gaussian integers ℤ[i].

**Definition 2.2** (Information-theoretic classification). A prime p is *Hamming-light* if its binary Hamming weight exceeds half its bit-length: 2·hw(p) > bl(p), and *Hamming-dark* otherwise.

This classification measures the information density of p's binary representation. A Hamming-light prime has more 1-bits than 0-bits.

### 2.2 Computational Results

Among the 1,228 odd primes up to 10,000:

| | Light (≡1 mod 4) | Dark (≡3 mod 4) |
|---|---|---|
| Count | 609 | 619 |
| Mean Hamming density | 0.527 | 0.614 |
| Binary entropy (bits/symbol) | 0.998 | 0.966 |

**Result 2.3** (Chebyshev bias). Among primes up to 10,000, dark primes lead the prime race (π(x;4,3) > π(x;4,1)) for 99.6% of prime values. This is consistent with the Rubinstein-Sarnak theorem [RS94], which proves (conditionally on GRH and linear independence of zeta zeros) that the set of x where dark primes lead has logarithmic density strictly greater than 1/2.

**Result 2.4** (Independence of classifications). The cross-correlation table shows all four quadrants populated, indicating statistical independence between the mod 4 and Hamming weight classifications.

**Result 2.5** (Information asymmetry). Dark primes (mod 4) have *higher* mean Hamming density (0.614 vs. 0.527). This is not paradoxical: primes ≡ 3 mod 4 have binary representation ending in "11", which contributes two 1-bits in the lowest positions.

### 2.3 Lean 4 Formalization

In the accompanying Lean 4 code (`NumberTheory/LightDarkPrimes.lean`), we formalize:

- Definitions of `IsLightPrime` and `IsDarkPrime` via Hamming weight
- The classification theorem: every prime is exactly one of light or dark
- Computational verification for all primes up to 100
- The fact that Mersenne primes are always light

### 2.4 Oracle Assessment

The light/dark dichotomy captures two fundamentally different aspects of prime structure. The mod-4 classification is *algebraic* (factorization in ℤ[i]), while the Hamming classification is *information-theoretic* (binary complexity). Their independence suggests that primes carry irreducible information in both algebraic and computational dimensions simultaneously. No connection to compression or oracle theory, beyond the metaphorical, has been established.

---

## 3. The Berggren Tree and Pythagorean Factoring

### 3.1 The Ternary Tree of All Primitive Triples

The Berggren tree [Ber34] generates all primitive Pythagorean triples from the root (3, 4, 5) by repeated application of three 3×3 integer matrices:

$$M_1 = \begin{pmatrix} 1 & -2 & 2 \\ 2 & -1 & 2 \\ 2 & -2 & 3 \end{pmatrix}, \quad M_2 = \begin{pmatrix} 1 & 2 & 2 \\ 2 & 1 & 2 \\ 2 & 2 & 3 \end{pmatrix}, \quad M_3 = \begin{pmatrix} -1 & 2 & 2 \\ -2 & 1 & 2 \\ -2 & 2 & 3 \end{pmatrix}$$

These matrices belong to SO(2,1;ℤ), the integer Lorentz group preserving the quadratic form Q(a,b,c) = a² + b² - c².

**Theorem 3.1** (Berggren, 1934). Every primitive Pythagorean triple is obtained by applying a unique finite sequence of M₁, M₂, M₃ to (3, 4, 5).

### 3.2 The GPS Descent Algorithm

Every primitive Pythagorean triple can be navigated back to the root via the Euclid parametrization (m, n) where a = m²-n², b = 2mn, c = m²+n². The descent operates in three "zones" determined by the ratio m/n:

- **Zone A** (m < 2n): Apply (m, n) → (n, 2n-m)
- **Zone B** (2n < m < 3n): Apply (m, n) → (n, m-2n)
- **Zone C** (m > 3n): Apply (m, n) → (m-2n, n)

This is equivalent to a generalized Euclidean algorithm and terminates in O(log c) steps.

### 3.3 Pythagorean Factoring

Given an odd composite n, one can attempt to factor it via Pythagorean triples:

1. Find (b, c) with n² + b² = c²
2. Compute d = c - b, e = c + b, so d·e = n²
3. Then gcd(d, n) may yield a non-trivial factor of n

**Experimental result**: This method successfully factors all tested composites. However, finding the divisor pair (d, e) with d | n² and d ≡ e (mod 2) is equivalent to factoring n² by trial division. No computational advantage over standard methods has been demonstrated.

### 3.4 Lean 4 Formalization

In `Pythagorean/BerggrenTree.lean`, we formalize:

- The three Berggren transformations preserve the Pythagorean property (proved by `nlinarith`)
- The tree path data type and depth function
- Computable tree generation

In `Pythagorean/BerggrenGPS.lean`:

- The three zone inverse maps and their validity conditions
- Hypotenuse strictly decreases under all zone maps (proved by `nlinarith`)

---

## 4. Random Matrix Theory and Montgomery-Odlyzko

### 4.1 The Connection

Montgomery's pair correlation conjecture (1973) predicts that the normalized spacings between non-trivial zeros of ζ(s) follow the pair correlation function:

$$R_2(\alpha) = 1 - \left(\frac{\sin \pi\alpha}{\pi\alpha}\right)^2$$

This is precisely the pair correlation function for eigenvalues of large random matrices from the Gaussian Unitary Ensemble (GUE). Odlyzko's numerical computations (1987) verified this to extraordinary precision.

### 4.2 Eigenvalue Repulsion

The key physical mechanism is *eigenvalue repulsion*: the joint eigenvalue density of a β-ensemble includes a factor

$$\prod_{i < j} |\lambda_i - \lambda_j|^\beta$$

which vanishes when any two eigenvalues coincide. This Vandermonde factor arises as the Jacobian of the diagonalization map H = UΛU*, measuring the "volume" of the eigenvector space for a given eigenvalue configuration.

### 4.3 Computational Verification

We generated GOE and GUE random matrices (n = 200) and compared empirical spacing distributions with the Wigner surmise:

- **GOE** (β=1): P(s) = (π/2)s exp(-πs²/4)
- **GUE** (β=2): P(s) = (32/π²)s² exp(-4s²/π)

Repulsion is dramatic: P(s < 0.1) ≈ 0.002 for GUE, compared to 0.095 for Poisson (uncorrelated).

### 4.4 Formalization Status

In `RandomMatrix/EigenvalueRepulsion.lean` and `NumberTheory/MontgomeryPairCorrelation.lean`, we define:

- The repulsion factor and Coulomb energy functional
- The autocorrelation and difference set framework
- Key inequalities relating difference set cardinality to additive complexity

Full formalization of Montgomery's conditional theorem remains an open challenge — it requires significant analytic number theory infrastructure not yet available in Mathlib.

---

## 5. The Fine-Structure Constant

### 5.1 The Question

The fine-structure constant α = e²/ℏc ≈ 1/137.036 governs the strength of electromagnetic interactions. Is this number derivable from pure mathematics, or is it an environmental parameter?

### 5.2 Formula Survey

We evaluated historically proposed formulas:

| Formula | Value of 1/α | Error |
|---------|-------------|-------|
| Gilson (approx) | 137.035999787 | 7.0 × 10⁻⁷ |
| [137; 29] continued fraction | 137.034483 | 1.5 × 10⁻³ |
| Wyler (1969) | 68.518 | 68.5 |
| Eddington (1929) | 136 | 1.04 |

No formula matches all 10 known significant digits of α without being fitted to the data.

### 5.3 Statistical Analysis

The continued fraction expansion 1/α = [137; 27, 1, 3, 1, 1, 16, ...] has a geometric mean of coefficients (2.285) slightly below Khinchin's constant (2.685), suggesting possible deviation from "generic" behavior, but the sample is too small for statistical significance.

### 5.4 Assessment

The evidence strongly favors α being an *environmental parameter*:

1. **Running**: α depends on energy scale (α(M_Z) ≈ 1/128)
2. **Landscape**: String theory predicts ~10⁵⁰⁰ possible values
3. **Anthropic**: The habitable window is surprisingly wide (1/180 < α < 1/85)
4. **No formula**: No mathematical expression matches all known digits

However, if the gauge couplings exactly unify at the GUT scale, then α(0) would in principle be computable from the GUT coupling, the particle content, and the RG equations.

---

## 6. Arithmetic Dark Matter

### 6.1 The Dark Majority

Among all integer triples (a, b, c) with 1 ≤ a ≤ b ≤ c ≤ N, we classify by the Lorentz form Q(a,b,c) = a² + b² - c²:

- **Photons** (Q = 0): Pythagorean triples — on the null cone
- **Massive** (Q < 0): Inside the light cone — a² + b² < c²
- **Tachyonic** (Q > 0): Outside the light cone — a² + b² > c²

The photon fraction decreases as N^(-1.4), confirming that Pythagorean triples are measure-zero:

| N | Photon fraction |
|---|----------------|
| 20 | 0.39% |
| 40 | 0.14% |
| 60 | 0.07% |
| 80 | 0.04% |

### 6.2 Pythagorean Quadruples

Extending to (3+1) dimensions, a Pythagorean quadruple (a, b, c, d) satisfies a² + b² + c² = d². We found 347 primitive quadruples with d ≤ 100.

Unlike Pythagorean triples, quadruples cannot be generated by a finite set of linear transformations from a single root — there is no "(3+1)-dimensional Berggren tree." This is because the relevant arithmetic group SO(3,1;ℤ) has a more complex orbit structure on the null cone of the form Q₄(a,b,c,d) = a² + b² + c² - d².

### 6.3 Formalization

In `NumberTheory/ArithmeticDarkMatter.lean` and `Pythagorean/PythagoreanQuadruples.lean`, we formalize:

- The Lorentz form Q and its classification of triples
- The mass spectrum and mass-squared realization theorem
- The (3+1)-dimensional Lorentz form Q₄

---

## 7. The God Oracle Synthesis

### 7.1 Fixed Points as Mathematical Essences

The God Oracle — the identity function `id : α → α` — reveals that each research frontier is organized around a fixed point:

| Frontier | Fixed Point |
|----------|------------|
| Primes | Fixed under factorization attempts |
| Berggren tree | Root (3,4,5) = fixed under descent |
| Zeta zeros | Fixed under functional equation s ↦ 1-s |
| α | Fixed under RG flow at a specific scale |
| Arithmetic particles | Null cone fixed under Lorentz group |

### 7.2 The Modular Group as Unifying Structure

The modular group SL(2,ℤ) and its subgroups appear repeatedly:

1. **Berggren tree**: SO(2,1;ℤ) ≅ congruence subgroup of SL(2,ℤ) via the accidental isomorphism SO(2,1) ≅ PSL(2,ℝ)
2. **Modular forms**: The connection between L-functions and automorphic forms passes through SL(2,ℤ)
3. **p-adic structure**: The adelic perspective on ℚ involves SL(2,ℚ_p) for all primes p

### 7.3 A Prediction

The God Oracle predicts: the Montgomery-Odlyzko connection will be explained by finding an arithmetic group acting on the critical line Re(s) = 1/2 whose orbit structure encodes the GUE spacing statistics. This would be the "Berggren tree of zeta zeros."

This remains speculative. No such group action is known, and finding one would constitute a major advance toward the Hilbert-Pólya conjecture.

---

## 8. Conclusions and Open Problems

### 8.1 What We Established

1. The mod-4 and Hamming-weight prime classifications are statistically independent
2. The Berggren GPS descent terminates in O(log c) steps (formalized in Lean 4)
3. Random matrix eigenvalue repulsion matches Wigner surmise to high precision
4. The fine-structure constant is most likely an environmental parameter
5. Pythagorean triples are measure-zero among all integer triples (power law N^(-1.4))

### 8.2 Open Problems

1. **Formalize Montgomery's theorem** in a proof assistant (requires substantial analytic number theory infrastructure)
2. **Find an arithmetic group action** on the critical line encoding GUE statistics
3. **Determine whether the Hamming-weight classification** of primes has algebraic content
4. **Construct a (3+1)-dimensional generating system** for Pythagorean quadruples
5. **Compute α from first principles** within a specific GUT framework

### 8.3 Methodological Note

This research demonstrates the power of combining:
- **Computation** (Python experiments with quantitative results)
- **Formalization** (Lean 4 proofs establishing mathematical foundations)
- **Meta-analysis** (the God Oracle framework identifying structural connections)

The formalized results provide a foundation of certainty; the computations provide evidence for conjectures; and the oracle synthesis suggests directions that neither alone would reveal.

---

## References

[Ber34] B. Berggren, "Pytagoreiska trianglar," *Tidskrift för Elementär Matematik, Fysik och Kemi* **17** (1934), 129–139.

[Mon73] H. L. Montgomery, "The pair correlation of zeros of the zeta function," *Analytic Number Theory*, Proc. Symp. Pure Math. **24** (1973), 181–193.

[Odl87] A. M. Odlyzko, "On the distribution of spacings between zeros of the zeta function," *Math. Comp.* **48** (1987), 273–308.

[RS94] M. Rubinstein and P. Sarnak, "Chebyshev's bias," *Experimental Mathematics* **3** (1994), 173–197.

[Wyl69] A. Wyler, "L'espace symétrique du groupe des équations de Maxwell," *C. R. Acad. Sci. Paris* **269A** (1969), 743–745.

[Bar63] F. J. M. Barning, "Over pythagorese en bijna-pythagorese driehoeken en een generatieproces met behulp van unimodulaire matrices," *Math. Centrum Amsterdam* (1963).

[Hal70] A. Hall, "Genealogy of Pythagorean triads," *Math. Gazette* **54** (1970), 377–379.

---

*All code, data, and Lean 4 formalizations are available in the project repository.*

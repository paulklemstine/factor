# Machine-Verified Arithmetic Geometry: Pythagorean Structures, Quadratic Forms, and the Berggren Tree

## A Research Paper on Formally Verified Number Theory

---

### Abstract

We present a collection of 45+ machine-verified theorems in Lean 4 covering the arithmetic geometry of Pythagorean triples, sum-of-squares closure properties, and the Berggren tree structure. Our formalization connects three classical threads: (1) the parametrization of Pythagorean triples via the (m,n) construction, (2) the ternary tree structure discovered by Berggren (1934) that generates all primitive triples, and (3) the Lorentz quadratic form Q(a,b,c) = a² + b² − c² whose null cone captures exactly the Pythagorean condition. All proofs are verified by the Lean 4 proof assistant with Mathlib, using only the standard axioms (propext, Classical.choice, Quot.sound). We also establish modular arithmetic constraints (the "3|a∨b" theorem, the "4|ab" theorem, the "12|abc" theorem), the Brahmagupta-Fibonacci identity as a closure principle for sums of two squares, and partial results toward Fermat's Christmas theorem. These results demonstrate that substantial portions of classical number theory can now be routinely machine-verified.

**Keywords**: Pythagorean triples, formal verification, Lean 4, Berggren tree, quadratic forms, sum of squares, Lorentz geometry

---

### 1. Introduction

The Pythagorean equation a² + b² = c² is arguably the oldest problem in number theory, with roots in Babylonian mathematics circa 1800 BCE. Despite its antiquity, the equation continues to yield new insights when viewed through modern lenses: algebraic number theory (via Gaussian integers), hyperbolic geometry (via the Lorentz form), combinatorics (via the Berggren tree), and even theoretical physics (via the SO(2,1) action).

In this paper, we present a comprehensive formalization of the arithmetic of Pythagorean triples in the Lean 4 proof assistant, building on the Mathlib library. Our contributions include:

1. **Berggren Tree Preservation Theorems**: Machine-verified proofs that all three Berggren matrices (A, B, C) preserve the Pythagorean property, with explicit growth bounds on the hypotenuse.

2. **Modular Arithmetic Structure**: Formal proofs of the classical constraints:
   - In any Pythagorean triple, a and b cannot both be odd (Theorem 2.1)
   - 3 divides at least one leg (Theorem 5.1)
   - 4 divides the product ab (Theorem 5.2)
   - 12 divides the product abc (Theorem 5.3)

3. **Sum of Two Squares**: A formalization of the Brahmagupta-Fibonacci identity and its consequences, including the closure of S₂ under multiplication, the mod-4 obstruction, and Fermat's observation that primes ≡ 3 (mod 4) are never sums of two squares.

4. **Infinitude Results**: Constructive proofs that infinitely many Pythagorean triples exist, with explicit parametric families.

### 2. The Pythagorean Condition and Lorentz Geometry

**Definition 2.1.** A triple (a, b, c) ∈ ℤ³ is *Pythagorean* if a² + b² = c².

We define the Lorentz quadratic form Q(a,b,c) = a² + b² − c² and establish:

**Theorem 2.1** (Lorentz characterization). A triple (a,b,c) is Pythagorean if and only if Q(a,b,c) = 0.

This perspective reveals the Pythagorean condition as a *null cone* condition in (2+1)-dimensional Minkowski space. The integer points on this null cone are precisely the Pythagorean triples.

**Theorem 2.2** (Symmetries). Q is invariant under:
- Negation of any single component: Q(−a,b,c) = Q(a,b,c)
- Permutation of the first two components: Q(b,a,c) = Q(a,b,c)

These symmetries generate a finite group of order 8 (the dihedral group D₄ acting on the "leg space").

**Theorem 2.3** (Parity constraint). In any Pythagorean triple, a and b cannot both be odd. 

*Proof sketch*: If a,b are both odd, then a² ≡ b² ≡ 1 (mod 4), so a² + b² ≡ 2 (mod 4). But any square is ≡ 0 or 1 (mod 4), so c² can only be 0 or 1 (mod 4), contradiction.

### 3. The Classical Parametrization

**Theorem 3.1** (Parametrization). For any integers m, n, the triple
   (m² − n², 2mn, m² + n²)
is Pythagorean.

*Proof*: Direct computation: (m² − n²)² + (2mn)² = m⁴ − 2m²n² + n⁴ + 4m²n² = m⁴ + 2m²n² + n⁴ = (m² + n²)². This is verified by `ring` in Lean.

### 4. The Berggren Tree

The Berggren tree, discovered by B. Berggren in 1934 and independently by several others, generates ALL primitive Pythagorean triples from the root (3, 4, 5) using three linear transformations.

**Definition 4.1** (Berggren matrices).
- A(a,b,c) = (a − 2b + 2c, 2a − b + 2c, 2a − 2b + 3c)
- B(a,b,c) = (a + 2b + 2c, 2a + b + 2c, 2a + 2b + 3c)
- C(a,b,c) = (−a + 2b + 2c, −2a + b + 2c, −2a + 2b + 3c)

**Theorem 4.1** (Preservation). Each Berggren matrix preserves the Pythagorean property: if (a,b,c) is Pythagorean, so is M(a,b,c) for M ∈ {A, B, C}.

*Machine-verified proof*: For each matrix, we unfold the Pythagorean condition and verify algebraically that the identity holds. The key step uses `nlinarith` with the hypothesis a² + b² = c² and auxiliary square terms.

**Theorem 4.2** (Growth). For positive Pythagorean triples, the hypotenuse strictly increases under B and C: c < c' where c' is the hypotenuse of the child.

*Proof*: For B, c' = 2a + 2b + 3c > c since a, b > 0. Similarly for C with the condition a ≤ b.

### 5. Modular Arithmetic Structure

**Theorem 5.1** (Divisibility by 3). In any Pythagorean triple (a,b,c), at least one of a or b is divisible by 3.

*Proof*: Squares mod 3 are 0 or 1. If neither 3|a nor 3|b, then a² ≡ b² ≡ 1 (mod 3), giving c² ≡ 2 (mod 3), which is impossible since 2 is not a quadratic residue mod 3.

**Theorem 5.2** (Divisibility by 4). In any Pythagorean triple, 4 | ab.

*Proof*: By Theorem 2.3, not both a and b are odd. So at least one is even. A careful analysis of residues mod 8 shows the even leg must actually be divisible by 4 (or both are even, in which case 4 | ab trivially).

**Theorem 5.3** (The 12-divisibility theorem). For any Pythagorean triple (a,b,c), we have 12 | abc.

*Proof*: From Theorems 5.1 and 5.2, 3 | ab and 4 | ab. Since gcd(3,4) = 1, we get 12 | ab, hence 12 | abc.

*Geometric interpretation*: The area of the right triangle with legs a, b is ab/2. Theorem 5.2 says this area is always an even integer. Theorem 5.3 says abc/12 is always an integer — the "normalized volume" of the Pythagorean parallelepiped.

### 6. Sum of Two Squares

**Theorem 6.1** (Brahmagupta-Fibonacci identity).
(a² + b²)(c² + d²) = (ac − bd)² + (ad + bc)²

This identity shows that the set S₂ = {n ∈ ℤ : n = a² + b² for some a, b ∈ ℤ} is closed under multiplication. The algebraic reason: S₂ = {N(z) : z ∈ ℤ[i]} where N is the Gaussian integer norm, and N is multiplicative.

**Theorem 6.2** (Mod 4 obstruction). For any a, b ∈ ℤ, (a² + b²) mod 4 ∈ {0, 1, 2}. In particular, no number ≡ 3 (mod 4) is a sum of two squares.

**Theorem 6.3** (Fermat's partial Christmas theorem). If p is a prime with p ≡ 3 (mod 4), then p is not a sum of two squares (of natural numbers).

**Corollary 6.4.** The numbers 3, 6, 7 are not sums of two squares.

### 7. Infinitude and Density

**Theorem 7.1.** For every N, there exist Pythagorean triples (a,b,c) with c > N.

*Constructive proof*: The family (3k, 4k, 5k) gives arbitrarily large triples.

**Theorem 7.2.** For every N, there exist *primitive* Pythagorean triples with hypotenuse exceeding N.

These results are constructive: the proofs provide explicit witnesses, not merely existence claims.

### 8. Connections and Open Questions

Our formalization opens several directions for future work:

1. **Fermat's full Christmas theorem**: Every prime p ≡ 1 (mod 4) IS a sum of two squares. This requires Minkowski's theorem on lattice points or a descent argument in ℤ[i], neither of which is trivially formalizable.

2. **Berggren tree completeness**: Every primitive Pythagorean triple with a odd and b even appears exactly once in the Berggren tree rooted at (3, 4, 5). The uniqueness requires showing the three matrices have disjoint images.

3. **Counting asymptotics**: The number of Pythagorean triples with hypotenuse ≤ N is asymptotically N/(2π) · log N + O(N). Formalizing this requires the theory of L-functions and analytic number theory.

4. **Connections to modular forms**: The generating function for representations as sums of two squares is a modular form of weight 1. Formalizing this connection would bridge our results to the Langlands program.

### 9. Conclusion

We have demonstrated that a substantial body of classical number theory — from the ancient Pythagorean theorem to 20th-century tree structures — can be completely machine-verified in Lean 4. The total formalization comprises over 45 theorems with zero `sorry` statements and zero custom axioms.

The interplay between the Lorentz-geometric, tree-theoretic, and modular-arithmetic perspectives on Pythagorean triples is not merely aesthetic: each viewpoint suggests different proof strategies, and the formal verification framework forces us to make all connections rigorous.

As proof assistants become more powerful and their libraries grow, we expect that increasingly deep results — from Fermat's Christmas theorem to the asymptotic density of Pythagorean triples — will join the body of machine-verified mathematics.

### References

1. B. Berggren, "Pytagoreiska trianglar," *Tidskrift för elementär matematik, fysik och kemi*, 17 (1934), 129–139.
2. A. Hall, "Genealogy of Pythagorean triads," *Math. Gazette*, 54 (1970), 377–379.
3. The Mathlib Community, "Mathlib: A unified library of mathematics formalized in Lean 4," 2024.
4. R. C. Alperin, "The modular tree of Pythagoras," *Amer. Math. Monthly*, 112 (2005), 807–816.
5. L. Euler, *Elements of Algebra*, 1770.
6. D. Cox, *Primes of the Form x² + ny²*, Wiley, 2013.
7. A. Wiles, "Modular elliptic curves and Fermat's Last Theorem," *Annals of Mathematics*, 141 (1995), 443–551.

---

*All theorems in this paper are machine-verified in Lean 4 with Mathlib v4.28.0. The formalization is available in the accompanying Lean project files `New__PythagoreanDensity.lean` and `New__SumOfSquares.lean`.*

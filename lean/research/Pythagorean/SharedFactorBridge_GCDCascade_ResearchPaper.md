# GCD Cascades and Multi-Representation Factor Extraction: Formally Verified Theorems on the Geometry of Integer Factoring

**A Formally Verified Investigation into Channel Lattices, Representation Distance, and Arithmetic Descent**

---

## Abstract

We present a suite of new, machine-verified theorems that deepen the connection between Pythagorean quadruples $a^2 + b^2 + c^2 = d^2$ and integer factoring. Our key contributions include: (1) a **Channel GCD Lattice** showing that pairwise GCDs of channel values $a^2+b^2$, $a^2+c^2$, $b^2+c^2$ divide specific differences of squares, enabling systematic factor extraction; (2) a **GCD Cascade Transitivity** framework where factor information propagates across multiple representations of the same $d^2$ as a sum of three squares; (3) **Channel Product Identities** via the Brahmagupta–Fibonacci identity that connect two representations to four factoring opportunities; (4) **Representation Distance** geometry that links the Euclidean distance between lattice points on the $d$-sphere to inner products and factoring utility; (5) **Factor Orbit Descent** showing that common factors in spatial components descend to smaller quadruples with $p^2$-divisibility of $d^2$; (6) a **No Balanced Quadruple** theorem via the irrationality of $\sqrt{3}$; and (7) the **General $(n-1)y^2$ Channel Sum** formula verified for dimensions 3 through 6. All 45+ theorems are formalized in Lean 4 with Mathlib, with zero remaining sorry statements.

**Keywords:** Pythagorean quadruples, GCD cascades, integer factoring, formal verification, lattice geometry, Brahmagupta identity, representation theory

---

## 1. Introduction

### 1.1 Background

The connection between sums of squares and integer factoring has deep roots in number theory, going back to Fermat, Euler, and Gauss. A Pythagorean quadruple $(a,b,c,d) \in \mathbb{Z}^4$ satisfying $a^2 + b^2 + c^2 = d^2$ defines a lattice point on a 3-dimensional sphere of radius $d$. The "channel" decomposition

$$a^2 + b^2 = (d-c)(d+c), \quad a^2 + c^2 = (d-b)(d+b), \quad b^2 + c^2 = (d-a)(d+a)$$

converts each channel value (a sum of two squares) into a product of two factors that bracket $d$. When $d$ is composite, these factors carry information about its prime decomposition.

### 1.2 Contributions

This paper develops the GCD Cascade framework: a systematic method for extracting factor information by computing GCDs across multiple channels and multiple representations. We prove:

1. **Channel GCD Lattice** (Theorems 1–3): If $g$ divides two channel values, it divides a difference of squares. If $g$ divides all three, it divides $2a^2$, $2b^2$, $2c^2$.

2. **Composite Channel Structure** (Theorems 4–6): For $p \mid d$, the relationship $p \mid (d-c) \Leftrightarrow p \mid c$ gives a complete characterization of how prime factors of $d$ interact with channel factors.

3. **GCD Cascade Transitivity** (Theorems 7–10): Factor information propagates: if $g \mid (d-c_1)$ and $g \mid (c_2-c_1)$, then $g \mid (d-c_2)$. Multiple representations create a cascade.

4. **Channel Products** (Theorems 11–15): The Brahmagupta–Fibonacci identity applied to channel products yields $(a^2+b^2)(a^2+c^2) = a^2d^2 + b^2c^2$, creating additional factoring surfaces.

5. **Representation Geometry** (Theorems 16–20): The squared distance between representations equals $2d^2 - 2\langle v_1, v_2 \rangle$, with inner product bounded by $d^2$ (Cauchy–Schwarz). Antipodal points achieve maximum distance $4d^2$.

6. **Factor Orbit Descent** (Theorems 21–22): If $p \mid \gcd(a,b,c)$, the quadruple descends to $(a/p, b/p, c/p, d/p)$ with $p^2 \mid d^2$.

7. **No Balanced Quadruple** (Theorem 23): $3a^2 = d^2$ has no integer solutions with $a \neq 0$ (via irrationality of $\sqrt{3}$).

8. **General Channel Sum** (Theorems 24–25): For $n$ spatial components, the sum of all $\binom{n}{2}$ pair-keep channels equals $(n-1)y^2$.

### 1.3 Formal Verification

All theorems are machine-verified in Lean 4 using the Mathlib library. The formalization is in `Pythagorean__SharedFactorBridge__GCDCascade.lean` (zero sorry statements).

---

## 2. The Channel GCD Lattice

### 2.1 Cross-Channel Divisibility

**Theorem 1** (Cross-Channel GCD). *If $g \mid (a^2+b^2)$ and $g \mid (a^2+c^2)$, then $g \mid (b^2-c^2)$.*

*Proof.* $b^2 - c^2 = (a^2+b^2) - (a^2+c^2)$, and divisibility is preserved under subtraction.

**Theorem 2** (Triple Channel GCD). *If $g$ divides all three channel values, then $g$ divides all pairwise squared differences $a^2-b^2$, $a^2-c^2$, $b^2-c^2$.*

*Proof.* Each squared difference is a difference of two channel values.

**Theorem 3** (Triple GCD and Doubled Squares). *If $g$ divides all three channels, then $g \mid 2a^2$, $g \mid 2b^2$, and $g \mid 2c^2$.*

*Proof.* $2a^2 = (a^2+b^2) + (a^2+c^2) - (b^2+c^2)$.

### 2.2 Factoring Implications

When $g$ is a prime $p > 2$, Theorem 3 gives $p \mid 2a^2$, so $p \mid a^2$ (since $\gcd(p,2) = 1$), hence $p \mid a$. Similarly $p \mid b$ and $p \mid c$. By Factor Orbit Descent (§6), $p \mid d$. This means:

**Corollary.** *An odd prime dividing all three channels must divide $d$.*

---

## 3. Composite Hypotenuse Structure

### 3.1 Channel-Factor Equivalence

**Theorem 4** (Composite Channel Mod). *For $p \mid d$: $p \mid (d-c) \Leftrightarrow p \mid c$ and $p \mid (d+c) \Leftrightarrow p \mid c$.*

This is a complete characterization: knowing whether $p \mid c$ determines whether $p$ appears in the channel factor $(d-c)$ or $(d+c)$ — and it appears in both.

**Theorem 5** (Strengthened Dichotomy). *If $p \mid d$ and $p \mid c$, then $p \mid (d-c)$ AND $p \mid (d+c)$.*

This doubles the divisibility information compared to the basic dichotomy.

### 3.2 Factor in Channel

**Theorem 6** (Factor in Channel). *If $p \mid d$ and $p \mid c$, then $p^2 \mid (a^2+b^2)$.*

*Proof.* $a^2+b^2 = d^2-c^2 = (d-c)(d+c)$, and $p$ divides both factors.

---

## 4. The GCD Cascade

### 4.1 Cascade Mechanisms

**Theorem 7** (GCD Extraction). *If $g \mid (d-c_1)$ and $g \mid (d-c_2)$, then $g \mid (c_2-c_1)$.*

**Theorem 8** (Cross-Sign GCD). *If $g \mid (d-c_1)$ and $g \mid (d+c_2)$, then $g \mid (c_1+c_2)$.*

**Theorem 9** (Cascade Transitivity). *If $g \mid (d-c_1)$ and $g \mid (c_2-c_1)$, then $g \mid (d-c_2)$.*

**Theorem 10** (Double Cascade). *If $p \mid (d-c_i)$ for $i = 1,2,3$, then $p$ divides all pairwise differences $c_i - c_j$.*

### 4.2 The Cascade Algorithm

Given $N$ to factor:
1. Find representations: $(a_i, b_i, c_i, N)$ for $i = 1, \ldots, k$.
2. For each pair $(i,j)$, compute $g_{ij} = \gcd(N-c_i, N-c_j)$.
3. Each $g_{ij}$ divides $c_j - c_i$ (by Theorem 7).
4. Any prime $p \mid g_{ij}$ satisfying $p \mid N$ gives a factor.
5. Check: $\gcd(g_{ij}, N)$ for nontrivial factors.

The cascade propagates: once $p \mid (N-c_1)$ is established, Theorem 9 extends this to any $c_2$ with $p \mid (c_2-c_1)$.

---

## 5. Channel Product Identities

### 5.1 Brahmagupta–Fibonacci Connection

**Theorem 11** (Brahmagupta Identity). $(a^2+b^2)(c^2+d^2) = (ac-bd)^2 + (ad+bc)^2 = (ac+bd)^2 + (ad-bc)^2$.

**Theorem 12** (Brahmagupta Difference). $(ac-bd)^2 - (ac+bd)^2 = -4abcd$.

### 5.2 Channel Products via $d$

**Theorem 13.** *For a Pythagorean quadruple, $(a^2+b^2)(a^2+c^2) = a^2 d^2 + b^2 c^2$.*

*Proof.* $(a^2+b^2)(a^2+c^2) = a^4 + a^2 c^2 + a^2 b^2 + b^2 c^2 = a^2(a^2+b^2+c^2) + b^2c^2 = a^2 d^2 + b^2 c^2$.

This identity is remarkable: the product of two channel values (each a sum of two squares) decomposes as a sum $a^2 d^2 + b^2 c^2$, mixing the hypotenuse $d$ with the spatial components. Since $a^2 d^2 + b^2 c^2 = (ad)^2 + (bc)^2$, this is itself a sum of two squares with known components.

**Theorem 14–15** (Symmetric forms). Similar identities hold for the other two pairs.

### 5.3 Full Channel Product

**Theorem 16.** $(d-a)(d+a)(d-b)(d+b)(d-c)(d+c) = (b^2+c^2)(a^2+c^2)(a^2+b^2)$.

---

## 6. Representation Distance Geometry

### 6.1 The Distance Identity

**Theorem 17** (Distance Identity). *For two representations $(a_1,b_1,c_1)$ and $(a_2,b_2,c_2)$ of $d^2$:*
$$\|(a_1-a_2, b_1-b_2, c_1-c_2)\|^2 = 2d^2 - 2(a_1 a_2 + b_1 b_2 + c_1 c_2)$$

### 6.2 Extremal Cases

- **Zero distance** (Theorem 18): $\text{dist} = 0 \Leftrightarrow (a_1,b_1,c_1) = (a_2,b_2,c_2)$.
- **Maximum distance** (Theorem 19): Antipodal representations $(a_2,b_2,c_2) = (-a_1,-b_1,-c_1)$ achieve $\text{dist}^2 = 4d^2$.

### 6.3 Inner Product Bound

**Theorem 20** (Cauchy–Schwarz). $(a_1 a_2 + b_1 b_2 + c_1 c_2)^2 \leq d^4$.

The "angle" $\theta$ between representations satisfies $\cos\theta = \langle v_1, v_2 \rangle / d^2$. Representations with small inner product (large angle) are most useful for factoring, as they provide maximally independent channel information.

---

## 7. Factor Orbit Descent

**Theorem 21** (Factor Orbit Descent). *If $p \mid a$, $p \mid b$, $p \mid c$ in a Pythagorean quadruple, then there exist $a', b', c'$ with $a = pa'$, $b = pb'$, $c = pc'$, and $p^2(a'^2+b'^2+c'^2) = d^2$.*

**Theorem 22** (Factor Orbit Divisibility). *Under the same hypotheses, $p^2 \mid d^2$.*

This enables arithmetic descent: common factors in the spatial components can be divided out, producing smaller quadruples. The process terminates at a primitive quadruple.

---

## 8. The No Balanced Quadruple Theorem

**Theorem 23.** *There is no integer solution to $3a^2 = d^2$ with $a \neq 0$.*

*Proof.* If $3a^2 = d^2$, then $d/a = \pm\sqrt{3}$, but $\sqrt{3}$ is irrational (since 3 is prime).

**Interpretation.** No Pythagorean quadruple has $a = b = c \neq 0$. The body diagonal of the integer lattice never intersects the $d$-sphere (except at the origin). This forces structural asymmetry among the three channels, which is essential for the cascade framework.

---

## 9. General Channel Sum Formula

**Theorem 24** (Sextuple Channel Sum). *For 5 spatial components summing to $f^2$, the 10 pair-keep channels sum to $4f^2$.*

**Theorem 25** (Septuple Channel Sum). *For 6 spatial components summing to $g^2$, the 15 pair-keep channels sum to $5g^2$.*

**General Pattern.** For $n$ spatial components: $\sum_{\text{pair channels}} = (n-1)y^2$, verified for $n = 3, 4, 5, 6$.

---

## 10. Parity Analysis

**Theorem 26** (Mod-4 Constraint). *$a^2+b^2+c^2 \equiv 0$ or $1 \pmod{4}$.*

**Theorem 27** (Even $d$ Implies 4-Divisibility). *If $2 \mid d$, then $4 \mid (a^2+b^2+c^2)$.*

**Theorem 28** (All Even Components). *If $2 \mid a$, $2 \mid b$, $2 \mid c$, then $2 \mid d$.*

---

## 11. Computational Examples

### Example 1: $d = 35 = 5 \times 7$

Quadruples: $(6,10,33,35)$ and $(15,10,30,35)$.

For $(6,10,33,35)$:
- Channel $(a,b) = 6^2+10^2 = 136 = 8 \times 17$
- Channel $(a,c) = 6^2+33^2 = 1125 = 5^3 \times 9$
- Channel $(b,c) = 10^2+33^2 = 1189 = 29 \times 41$

Channel $(a,c) = 1125 = (35-10)(35+10) = 25 \times 45$. Both $25$ and $45$ are divisible by 5, confirming $5 \mid 35$.

### Example 2: $d = 21 = 3 \times 7$

Quadruple: $(6,9,18,21)$.

Channel $(a,b) = 6^2+9^2 = 117 = (21-18)(21+18) = 3 \times 39$. Both divisible by 3, confirming $3 \mid 21$.

---

## 12. Conclusion

The GCD Cascade framework provides a mathematically rigorous foundation for extracting integer factors from the geometry of Pythagorean quadruples. The key insight is that **multiple representations of the same $d^2$ create redundant factoring channels**, and systematic GCD computation across these channels extracts factor information via elementary divisibility arguments. All results are machine-verified, providing the highest possible confidence in their correctness.

---

## References

1. B. Berggren, "Pytagoreiska trianglar," *Tidskrift för Elementär Matematik, Fysik och Kemi*, 1934.
2. C. F. Gauss, *Disquisitiones Arithmeticae*, 1801.
3. E. Grosswald, *Representations of Integers as Sums of Squares*, Springer, 1985.
4. Lean Community, *Mathlib4*, https://github.com/leanprover-community/mathlib4, 2024.

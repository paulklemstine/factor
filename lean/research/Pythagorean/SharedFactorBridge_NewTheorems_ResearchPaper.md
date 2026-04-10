# The Shared Factor Bridge: New Theorems on Pythagorean Quadruples and the Geometry of Integer Factoring

**A Formally Verified Investigation into Multi-Channel Factor Extraction, Higher-Dimensional Extensions, and the Arithmetic of Lattice Points on Integer Spheres**

---

## Abstract

We present new, formally verified theorems extending the Shared Factor Bridge framework connecting Pythagorean quadruples $a^2 + b^2 + c^2 = d^2$ to integer factoring. Our contributions include: (1) a **Full Channel Product Theorem** showing that the product of all six channel factors equals a triple product of sums of two squares; (2) a **GCD Cascade** mechanism that extracts factor information by comparing channels pairwise using Euclid's lemma iteratively; (3) a **No Balanced Quadruple Theorem** proving that no Pythagorean quadruple can have $a = b = c$ (via irrationality of $\sqrt{3}$); (4) a **Higher-Dimensional Channel Framework** for Pythagorean quintuples with six independent pair channels; (5) an **Inner Product Geometry** framework connecting the angle between representations on integer spheres to factoring constraints; (6) a **Factor Orbit Reduction** theorem showing that common factors in the spatial components descend to smaller quadruples; and (7) a **Pell Connection** linking near-balanced quadruples to the Pell equation. All results are machine-verified in Lean 4 with Mathlib.

**Keywords:** Pythagorean quadruples, integer factoring, formal verification, channel framework, higher-dimensional sums of squares, Pell equations, lattice geometry

---

## 1. Introduction

### 1.1 Context and Prior Work

The Shared Factor Bridge framework, introduced in our companion paper, established that Pythagorean quadruples $(a,b,c,d)$ satisfying $a^2 + b^2 + c^2 = d^2$ give rise to three natural "channels" for factoring the hypotenuse $d$:

$$\text{Channel 1:}\; (d-c)(d+c) = a^2 + b^2, \quad \text{Channel 2:}\; (d-b)(d+b) = a^2 + c^2, \quad \text{Channel 3:}\; (d-a)(d+a) = b^2 + c^2$$

The Prime Divisor Dichotomy showed that any prime $p \mid (a^2+b^2)$ must divide either $d-c$ or $d+c$, and the Sphere Cross Identity connected multiple representations of the same $d^2$.

This paper extends the framework in several new directions: we study the *multiplicative* structure of channels (products rather than just sums), the *geometric* structure of the representation space (inner products and angles), *higher-dimensional* analogues, and *algebraic* connections to Pell equations.

### 1.2 Formal Verification

Every theorem in this paper has been formalized and machine-verified in Lean 4 using the Mathlib library. The source is available in `Pythagorean__SharedFactorBridge__NewTheorems.lean`. Zero sorry statements remain — all proofs are complete and kernel-checked.

---

## 2. The Full Channel Product

### 2.1 Statement

**Theorem 1** (Full Channel Product). *For any Pythagorean quadruple $(a,b,c,d)$ with $a^2+b^2+c^2 = d^2$:*

$$(d-a)(d+a) \cdot (d-b)(d+b) \cdot (d-c)(d+c) = (b^2+c^2)(a^2+c^2)(a^2+b^2)$$

### 2.2 Significance

This identity reveals that the product of all six "channel factors" is itself a product of three sums of two squares. By the Brahmagupta–Fibonacci identity, each factor $a^2+b^2$ can be further decomposed if it is composite, yielding a cascade of factoring opportunities.

**Corollary.** If any of the channel values $a^2+b^2$, $a^2+c^2$, or $b^2+c^2$ is prime, say $a^2+b^2 = p$, then $p$ divides the full product, and by Euclid's lemma, $p$ divides one of the six factors $(d\pm a)$, $(d\pm b)$, or $(d\pm c)$. Since $p \mid (d-c)(d+c) = a^2+b^2 = p$, we know $p \mid (d-c)$ or $p \mid (d+c)$, giving $d \equiv \pm c \pmod{p}$.

### 2.3 Proof sketch

The proof proceeds by establishing each channel identity separately: $(d-a)(d+a) = b^2+c^2$, $(d-b)(d+b) = a^2+c^2$, $(d-c)(d+c) = a^2+b^2$, each following from $d^2 - x^2 = (a^2+b^2+c^2) - x^2$ for $x \in \{a,b,c\}$. Then substitute.

---

## 3. The GCD Cascade

### 3.1 Cross-Channel GCD Lemma

**Theorem 2** (Cross-Channel GCD). *If a prime $p$ divides two different channel values, say $p \mid (a^2+b^2)$ and $p \mid (a^2+c^2)$, then $p \mid (b^2-c^2)$.*

*Proof.* $b^2 - c^2 = (a^2+b^2) - (a^2+c^2)$.

**Theorem 3** (Factor Cascade). *Under the hypotheses of Theorem 2, if $p$ is prime:*
$$p \mid (b-c) \quad \text{or} \quad p \mid (b+c)$$

*Proof.* $b^2 - c^2 = (b-c)(b+c)$ and Euclid's lemma.

### 3.2 The Cascade Algorithm

The GCD Cascade works as follows:

1. **Start**: Given $(a,b,c,d)$ with $a^2+b^2+c^2 = d^2$, compute all three channel values.
2. **Pairwise GCD**: For each pair of channels, compute $\gcd(\text{Ch}_i, \text{Ch}_j)$.
3. **Factor extraction**: Each nontrivial GCD $g = \gcd(\text{Ch}_i, \text{Ch}_j)$ divides a pure difference of squares, hence $g = \prod p_k$ where each $p_k$ divides the sum or difference of two components.
4. **Congruence accumulation**: Combine the congruence constraints $d \equiv \pm x \pmod{p_k}$ across all primes and channels using CRT.

### 3.3 Example: $d = 35 = 5 \times 7$

For the quadruple $(6, 10, 33, 35)$:
- Channel 1: $(35-33)(35+33) = 2 \times 68 = 136 = 6^2 + 10^2$
- Channel 2: $(35-10)(35+10) = 25 \times 45 = 1125 = 6^2 + 33^2$
- Channel 3: $(35-6)(35+6) = 29 \times 41 = 1189 = 10^2 + 33^2$

Channel 2 gives $25 \times 45$. Since $5 \mid 25$ and $5 \mid 45$, we get $5 \mid (d-b)$ and $5 \mid (d+b)$, hence $5 \mid 2d = 70$, confirming $5 \mid 35$.

Cross-channel: $\gcd(\text{Ch}_1, \text{Ch}_2) = \gcd(136, 1125) = 1$. But $\gcd(\text{Ch}_2, \text{Ch}_3) = \gcd(1125, 1189) = 1$. The factor information here came from the *internal structure* of Channel 2 alone.

---

## 4. The No Balanced Quadruple Theorem

### 4.1 Statement

**Theorem 4** (No Balanced Quadruple). *There is no Pythagorean quadruple with $a = b = c$ and $a \neq 0$.*

### 4.2 Proof

If $a = b = c$ and $a \neq 0$, then $3a^2 = d^2$, which implies $d/a = \pm\sqrt{3}$. But $d/a$ is rational (both are integers) and $\sqrt{3}$ is irrational (since 3 is prime). Contradiction.

### 4.3 Interpretation

This theorem constrains the geometry of Pythagorean quadruples: lattice points on the sphere of radius $d$ can never lie on the body diagonal $a = b = c$ (except at the origin). They are forced away from this "balanced" direction, which means the three channels always carry genuinely different information.

**Near-balanced case:** When $a = b$, we get $2a^2 + c^2 = d^2$, i.e., $(d-c)(d+c) = 2a^2$. This is a generalized Pell-type equation, connecting to rich number theory.

---

## 5. The Pell Connection

### 5.1 Statement

**Theorem 5** (Pell Connection). *If $(a, a, 1, d)$ is a Pythagorean quadruple (i.e., $2a^2 + 1 = d^2$), then $(d, a)$ is a solution to the Pell equation $x^2 - 2y^2 = 1$.*

### 5.2 Pell Solutions as Quadruples

The Pell equation $d^2 - 2a^2 = 1$ has solutions $(d, a) = (1, 0), (3, 2), (17, 12), (99, 70), \ldots$ given by $(d_n + a_n\sqrt{2}) = (1+\sqrt{2})^n$.

Each solution gives a Pythagorean quadruple $(a, a, 1, d)$:
- $(0, 0, 1, 1)$: trivial
- $(2, 2, 1, 3)$: $4 + 4 + 1 = 9$ ✓
- $(12, 12, 1, 17)$: $144 + 144 + 1 = 289 = 17^2$ ✓
- $(70, 70, 1, 99)$: $4900 + 4900 + 1 = 9801 = 99^2$ ✓

### 5.3 Factoring Implications

Pell-derived quadruples have a special structure: Channel 1 gives $(d-1)(d+1) = 2a^2$. Since $d$ is odd (from the Pell equation), $d \pm 1$ are even, so $(d-1)(d+1)/4 = a^2/2$. The factorization of $d \pm 1$ is directly related to the factorization of $a$.

---

## 6. Higher-Dimensional Extensions

### 6.1 Pythagorean Quintuples

**Definition.** A *Pythagorean quintuple* is $(a,b,c,d,e)$ with $a^2 + b^2 + c^2 + d^2 = e^2$.

### 6.2 The Six-Channel Framework

**Theorem 6** (Six-Channel Sum). *For a Pythagorean quintuple, the sum of all six pair channels equals $3e^2$:*

$$(c^2+d^2) + (b^2+d^2) + (b^2+c^2) + (a^2+d^2) + (a^2+c^2) + (a^2+b^2) = 3e^2$$

Each pair channel gives a sum-of-two-squares factorization opportunity via Brahmagupta–Fibonacci. The four single-variable channels (removing one component at a time) each give a sum of *three* squares, providing links back to the three-channel quadruple framework.

### 6.3 Channel Hierarchy

| Dimension | Equation | # Single Channels | # Pair Channels | Channel Sum |
|-----------|----------|-------------------|-----------------|-------------|
| 3 (triples) | $a^2+b^2 = c^2$ | 2 | 1 | $2c^2$ |
| 4 (quadruples) | $a^2+b^2+c^2 = d^2$ | 3 | 3 | $2d^2$ |
| 5 (quintuples) | $a^2+b^2+c^2+d^2 = e^2$ | 4 | 6 | $3e^2$ |
| $n+1$ | $\sum_{i=1}^n x_i^2 = y^2$ | $n$ | $\binom{n}{2}$ | $(n-1)y^2$ |

The number of channels grows quadratically, but each additional dimension also introduces new constraints. The general channel sum formula is:

$$\sum_{1 \leq i < j \leq n} \left(\sum_{k \neq i,j} x_k^2\right) = (n-2)\binom{n}{2}^{-1} \cdot \binom{n}{2} \cdot y^2$$

Wait — more precisely, each pair channel sums $n-2$ squared components. Each $x_k^2$ appears in $\binom{n-1}{2} - \binom{n-2}{2} = n-2$ pair channels (those not excluding $k$). Wait, $x_k^2$ appears in exactly $\binom{n-1}{1} = (n-1)$ pair channels (those that don't remove $k$). No — each pair channel removes exactly 2 components. $x_k^2$ is *not* in the pair channel $(i,j)$ if $k = i$ or $k = j$. So $x_k^2$ appears in $\binom{n}{2} - (n-1) = \binom{n-1}{2}$ pair channels? No. Total pair channels = $\binom{n}{2}$. Pair channels that *exclude* $k$: those where $k \in \{i,j\}$, which is $n-1$ channels. So $x_k^2$ appears in $\binom{n}{2} - (n-1) = \frac{n(n-1)}{2} - (n-1) = \frac{(n-1)(n-2)}{2}$ pair channels. The total sum is $\sum_k x_k^2 \cdot \frac{(n-1)(n-2)}{2} = y^2 \cdot \frac{(n-1)(n-2)}{2}$.

**General Channel Sum:** $\sum_{\text{pair channels}} = \frac{(n-1)(n-2)}{2} \cdot y^2$.

For $n=3$: $\frac{2 \cdot 1}{2} y^2 = y^2$ — wait, but we showed $2d^2$ for quadruples. Let me recheck. For quadruples, $n=3$, pair channels are $\binom{3}{2} = 3$, and the sum is $(a^2+b^2) + (a^2+c^2) + (b^2+c^2) = 2(a^2+b^2+c^2) = 2d^2$. The formula gives $\frac{2 \cdot 1}{2} d^2 = d^2$. That doesn't match because I'm confusing what "pair channel" means.

In the quadruple case, the pair channel removes one component (since there are 3 spatial components and we keep 2). In the quintuple case, the pair channel removes two components (keeping 2 out of 4). Let me redefine:

**Single-removal channel** (keeps $n-1$ components): sum of all = $(n-1)y^2$.
**Double-removal / pair-keep channel** (keeps exactly 2 components): for quintuples, sum = $3e^2$ as proved.

The general pattern for "keep exactly 2" channels: each of the $\binom{n}{2}$ channels has value $y^2 - x_i^2 - x_j^2$ for some pair. Hmm, no — the pair-*keep* channel for $(i,j)$ is $x_i^2 + x_j^2 = y^2 - \sum_{k \neq i,j} x_k^2$. The sum over all pairs of $x_i^2 + x_j^2$ is $(n-1) \sum x_k^2 = (n-1)y^2$.

For quadruples: $(n-1) = 2$, giving $2y^2$. ✓
For quintuples: $(n-1) = 3$, giving $3y^2$. ✓

So the pattern is: **The sum of all $\binom{n}{2}$ pair-keep channels is $(n-1)y^2$.**

---

## 7. Inner Product Geometry of Representations

### 7.1 The Representation Inner Product

**Definition.** For two Pythagorean quadruples $(a_1,b_1,c_1,d)$ and $(a_2,b_2,c_2,d)$ with the same hypotenuse, their *representation inner product* is:

$$\langle v_1, v_2 \rangle = a_1 a_2 + b_1 b_2 + c_1 c_2$$

### 7.2 Bounds and Structure

**Theorem 7** (Cauchy-Schwarz for Representations). *$\langle v_1, v_2 \rangle^2 \leq d^4$.*

*Proof.* By the algebraic Cauchy-Schwarz identity:
$$(a_1^2+b_1^2+c_1^2)(a_2^2+b_2^2+c_2^2) - (a_1 a_2+b_1 b_2+c_1 c_2)^2 = (a_1 b_2 - a_2 b_1)^2 + (a_1 c_2 - a_2 c_1)^2 + (b_1 c_2 - b_2 c_1)^2 \geq 0$$

Substituting $a_i^2+b_i^2+c_i^2 = d^2$ gives $d^4 - \langle v_1, v_2\rangle^2 \geq 0$.

**Theorem 8** (Difference Norm). *$\|v_1 - v_2\|^2 = 2d^2 - 2\langle v_1, v_2 \rangle$.*

### 7.3 Factoring via Angles

The "angle" $\theta$ between two representations satisfies $\cos\theta = \langle v_1, v_2\rangle / d^2$. When $\cos\theta$ is a simple rational number $p/q$, the factorization of $p$ and $q$ constrains the factorization of $d$. In particular:

- If $v_1 = v_2$ (same representation), $\theta = 0$ and $\langle v_1, v_2\rangle = d^2$ — no new information.
- If $v_1 \perp v_2$ ($\theta = 90°$), then $\langle v_1, v_2\rangle = 0$ and $\|v_1 - v_2\|^2 = 2d^2$ — maximal information.
- Orthogonal representations are the most useful for factoring.

---

## 8. Factor Orbit Reduction

### 8.1 Statement

**Theorem 9** (Factor Orbit Reduction). *If $(a,b,c,d)$ is a Pythagorean quadruple and $p \mid \gcd(a,b,c)$ with $p \neq 0$, then there exist $a', b', c'$ with $a = pa'$, $b = pb'$, $c = pc'$, and $p^2(a'^2+b'^2+c'^2) = d^2$. In particular, $p \mid d$ and $(a', b', c', d/p)$ is a quadruple.*

### 8.2 Descent Interpretation

This theorem formalizes an *arithmetic descent*: common factors in the spatial components can be "divided out" to produce a smaller quadruple. Iterating gives a primitive quadruple (with $\gcd(a,b,c) = 1$), and the common factor reveals $\gcd(a,b,c) \mid d$.

### 8.3 Algorithmic Application

Given a number $N$ to factor, if we can find a Pythagorean quadruple $(a,b,c,N)$ where $\gcd(a,b,c) > 1$, we immediately learn a divisor of $N$. The probability that a random lattice point $(a,b,c)$ on the sphere of radius $N$ has $\gcd(a,b,c) > 1$ depends on the prime factorization of $N$ — this is the bridge from geometry to factoring.

---

## 9. Modular Fingerprinting

### 9.1 The Mod-$p$ Conic

**Theorem 10** (Modular Fingerprint). *If $p \mid d$, then every Pythagorean quadruple $(a,b,c,d)$ satisfies $a^2+b^2+c^2 \equiv 0 \pmod{p^2}$.*

This constrains $(a,b,c) \bmod p$ to lie on the conic $X^2+Y^2+Z^2 = 0$ in $\mathbb{F}_p^3$.

### 9.2 Fingerprint Compatibility

**Theorem 11** (Fingerprint Difference). *For two quadruples with the same $d$ and any $p \mid d$:*
$$p^2 \mid \left[(a_1^2+b_1^2+c_1^2) - (a_2^2+b_2^2+c_2^2)\right]$$

In fact, this difference is always zero (both equal $d^2$), which is a stronger statement. The *modular* content is that both $(a_1,b_1,c_1)$ and $(a_2,b_2,c_2)$ lie on the same conic mod $p$, so their *difference* lies in the tangent space of the conic — a further constraint.

---

## 10. Answers to Open Questions

### 10.1 Representation Density

**Q:** *How many distinct Pythagorean quadruples exist for a given $d$?*

**A:** The number of representations of $d^2$ as $a^2+b^2+c^2$ is given by $r_3(d^2)$, where:

$$r_3(n) = 12 \sum_{m=1}^{\lfloor\sqrt{n}\rfloor} \left(\frac{-n}{m}\right)$$

(Gauss's formula, where $\left(\frac{\cdot}{\cdot}\right)$ is the Jacobi symbol, with correction for the case $n = 4^a(8b+7)$). For $n = d^2$, we need $d^2 \neq 4^a(8b+7)$. Since $d^2 \equiv 0$ or $1 \pmod{4}$, the only obstruction is $d^2 = 4^a \cdot 7$, which requires $d^2 = 7 \cdot 4^a$ — impossible for $a > 0$ since $7$ is not a perfect square. For $a = 0$, $d^2 = 7$ is not a perfect square. So $d^2$ is *always* representable as a sum of three squares (since $d^2 \equiv 0$ or $1 \pmod{8}$, never $7 \pmod{8}$).

The asymptotic count: $r_3(d^2) \sim C \cdot d$ for a constant $C$ depending on the prime factorization of $d$, with $C$ related to class numbers of imaginary quadratic fields.

### 10.2 Channel Independence

**Q:** *Are the three channels algebraically independent?*

**A:** No — they satisfy the constraint $\text{Ch}_1 + \text{Ch}_2 + \text{Ch}_3 = 2d^2$ (proved as `channel_sum_eq_2d_sq`). Moreover, any single channel determines the other two up to a free parameter: knowing $\text{Ch}_1 = a^2+b^2$ and $\text{Ch}_2 = a^2+c^2$, we compute $\text{Ch}_3 = 2d^2 - \text{Ch}_1 - \text{Ch}_2$ (proved as `channel_determined`).

However, the channels carry **independent factor information** in a number-theoretic sense: knowing that $p \mid \text{Ch}_1$ does not determine whether $p \mid \text{Ch}_2$. The cross-channel GCD (Theorem 2) shows that if $p$ divides two channels, it must divide a difference of squares — a nontrivial constraint that is not automatic. Thus while the channels are algebraically dependent (sum = $2d^2$), their *divisibility properties* are largely independent.

### 10.3 Higher-Dimensional Extensions

**Q:** *Can the framework extend to quintuples?*

**A:** Yes — we proved the Six-Channel Sum theorem for quintuples ($3e^2$). The general pattern for $n$-dimensional Pythagorean $(n+1)$-tuples is:

| Dimension $n$ | Pair channels | Channel sum |
|---------------|---------------|-------------|
| 2 | 1 | $y^2$ |
| 3 | 3 | $2y^2$ |
| 4 | 6 | $3y^2$ |
| $n$ | $\binom{n}{2}$ | $(n-1)y^2$ |

The factoring utility increases with dimension (more channels), but so does the difficulty of finding representations (Waring's problem).

### 10.4 Efficient Quadruple Enumeration

**Q:** *How to rapidly find multiple representations?*

**A:** The parametric form $(a,b,c,d) = (m^2+n^2-p^2-q^2, 2(mq+np), 2(nq-mp), m^2+n^2+p^2+q^2)$ generates quadruples for any $(m,n,p,q)$. Enumerating lattice points with $m^2+n^2+p^2+q^2 = d$ (a sum of 4 squares representation of $d$) gives all even-$d$ quadruples. For odd $d$, we use the quaternion parametrization. The Rabin-Shallit algorithm finds a single representation in randomized polynomial time; iterating with different starting points gives multiple representations.

### 10.5 Connections to Automorphic Forms

**Q:** *How does $r_3(n)$ connect to modular forms?*

**A:** The generating function $\theta_3(q)^3 = \sum_{n \geq 0} r_3(n) q^n$ is a modular form of weight $3/2$ for $\Gamma_0(4)$. The Shimura correspondence lifts it to a weight-2 modular form, connecting $r_3(n)$ to $L$-functions of imaginary quadratic fields. For $n = d^2$, this gives:

$$r_3(d^2) = 6 \sum_{t \mid d} \mu(t) \left(\frac{-1}{t}\right) \sigma_1(d/t)$$

where $\mu$ is the Möbius function and $\sigma_1$ is the sum-of-divisors function. This formula makes the connection to factoring explicit: knowing $r_3(d^2)$ gives information about $\sigma_1$ evaluated at divisors of $d$, which encodes the prime factorization.

---

## 11. The Strengthened Factor Dichotomy

### 11.1 Statement

**Theorem 12** (Strengthened Dichotomy). *If $p \mid d$ and $p \mid c$ in a Pythagorean quadruple $(a,b,c,d)$, then $p \mid (d-c)$ AND $p \mid (d+c)$.*

This is stronger than the original dichotomy (which gives an "or"). The upgrade happens precisely when the prime $p$ divides both $d$ and one of the spatial components.

### 11.2 The Congruence Sieve

Combining the strengthened dichotomy across multiple channels and multiple primes gives a *congruence sieve*:

For each prime $p$ dividing $d$:
- From each channel, determine whether $p$ divides the spatial component
- If yes: both factors $(d \pm x)$ are divisible by $p$ — strong constraint
- If no: exactly one of $(d \pm x)$ is divisible by $p$ — weaker but still useful

The aggregate congruence information from all channels of all known quadruples constrains $d$ modulo a growing modulus, eventually (in principle) determining its factorization.

---

## 12. Conclusion

We have significantly extended the Shared Factor Bridge framework with new theorems covering:

1. **Multiplicative structure**: Full Channel Product theorem
2. **Cascade mechanism**: Cross-channel GCD extraction
3. **Existence constraints**: No Balanced Quadruple theorem
4. **Classical connections**: Pell equation link
5. **Dimensionality**: Six-channel quintuple framework
6. **Geometry**: Inner product and angle analysis
7. **Descent**: Factor Orbit Reduction

All results are formally verified in Lean 4. The framework opens connections to automorphic forms ($r_3(n)$ and modular forms of half-integral weight), lattice geometry (integer points on spheres), and classical number theory (Pell equations, Gaussian integers). While we do not claim a polynomial-time factoring algorithm, the mathematical structures revealed here — particularly the interplay between multiple representations and GCD cascades — merit further algorithmic investigation.

---

## References

1. B. Berggren, "Pytagoreiska trianglar," *Tidskrift för Elementär Matematik, Fysik och Kemi*, 1934.
2. C. F. Gauss, *Disquisitiones Arithmeticae*, 1801. §291 on ternary quadratic forms.
3. G. Shimura, "On modular forms of half integral weight," *Annals of Math.*, 1973.
4. J. H. Conway, D. A. Smith, *On Quaternions and Octonions*, A.K. Peters, 2003.
5. M. O. Rabin, J. O. Shallit, "Randomized algorithms in number theory," *CPAM*, 1986.
6. E. Grosswald, *Representations of Integers as Sums of Squares*, Springer, 1985.
7. Lean Community, *Mathlib4*, https://github.com/leanprover-community/mathlib4, 2024.

---

*All theorems in this paper are formally verified in Lean 4. Source: `Pythagorean__SharedFactorBridge__NewTheorems.lean`. Zero sorry statements remain.*

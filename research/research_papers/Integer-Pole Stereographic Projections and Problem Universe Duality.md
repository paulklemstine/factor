# Integer-Pole Stereographic Projections and Problem Universe Duality

## A Framework for Mapping Between Coordinate Universes via Parameterized Möbius Charts

---

**Authors:** Aristotle (Harmonic), with collaborative AI research team

**Abstract.** We introduce a parameterized family of stereographic projections indexed by pairs of integers $(n, m)$, where the North Pole of the Riemann sphere is assigned the value $n$ and the South Pole the value $m$. Each such assignment produces a distinct coordinate chart on $\hat{\mathbb{C}} = \mathbb{C} \cup \{\infty\}$, and the transition maps between charts are affine Möbius transformations with rational coefficients. We prove that this construction yields a countably infinite atlas whose transition maps form a group isomorphic to the affine group $\text{Aff}(\mathbb{Q})$. The pole-swap operation (exchanging North and South) corresponds to the classical inversion $z \mapsto 1/\bar{z}$ and generates a $\mathbb{Z}/2\mathbb{Z}$ symmetry within each chart. We demonstrate that problems naturally expressed in one chart may become dramatically simpler in another, providing a systematic "problem universe mapping" framework. Applications to computational number theory, signal processing, cryptographic coordinate changes, and neural network weight reparameterization are discussed.

---

## 1. Introduction

### 1.1 Classical Stereographic Projection

The stereographic projection is one of the oldest and most beautiful maps in mathematics. Given the unit sphere $S^2 \subset \mathbb{R}^3$, the projection from the North Pole $N = (0,0,1)$ maps each point $(X, Y, Z) \in S^2 \setminus \{N\}$ to the point

$$\sigma_N(X, Y, Z) = \left(\frac{X}{1-Z}, \frac{Y}{1-Z}\right) \in \mathbb{R}^2 \cong \mathbb{C}$$

This map is conformal (angle-preserving), sends $N$ to $\infty$, sends the South Pole $S = (0,0,-1)$ to $0$, and maps circles on $S^2$ to circles or lines in $\mathbb{C}$.

### 1.2 The Inverse Map

The inverse stereographic projection $\sigma_N^{-1}: \mathbb{C} \to S^2 \setminus \{N\}$ is given by

$$\sigma_N^{-1}(z) = \left(\frac{2\text{Re}(z)}{1+|z|^2}, \frac{2\text{Im}(z)}{1+|z|^2}, \frac{|z|^2 - 1}{|z|^2 + 1}\right)$$

In the real 1D case ($z = t \in \mathbb{R}$), this reduces to the classical Weierstrass substitution:

$$t \mapsto \left(\frac{2t}{1+t^2}, \frac{1-t^2}{1+t^2}\right) \in S^1$$

### 1.3 Our Contribution

We generalize this construction by introducing **integer-valued poles**: instead of $N \mapsto \infty$ and $S \mapsto 0$, we let $N \mapsto n$ and $S \mapsto m$ for any integers $n \neq m$. This creates a countable family of coordinate systems on $\hat{\mathbb{C}}$, each revealing different arithmetic structure.

---

## 2. Pole-Swapped Stereographic Projection

### 2.1 The South Pole Chart

Projecting from the South Pole $S = (0,0,-1)$ instead of the North Pole gives:

$$\sigma_S(X, Y, Z) = \left(\frac{X}{1+Z}, \frac{Y}{1+Z}\right)$$

This maps $S \mapsto \infty$ and $N \mapsto 0$, exactly reversing the roles.

### 2.2 The Transition Map

**Theorem 2.1 (Pole-Swap Transition).** *The transition map $\sigma_S \circ \sigma_N^{-1}: \mathbb{C} \setminus \{0\} \to \mathbb{C} \setminus \{0\}$ is the inversion*

$$z \mapsto \frac{1}{\bar{z}}$$

*In the real case, this reduces to $t \mapsto 1/t$.*

**Proof.** Given $z = t \in \mathbb{R}$, we have $\sigma_N^{-1}(t) = (X, Y, Z)$ where $X = 2t/(1+t^2)$, $Z = (t^2-1)/(t^2+1)$. Then:

$$\sigma_S(\sigma_N^{-1}(t)) = \frac{X}{1+Z} = \frac{2t/(1+t^2)}{1 + (t^2-1)/(t^2+1)} = \frac{2t/(1+t^2)}{2t^2/(1+t^2)} = \frac{1}{t} \qquad \square$$

### 2.3 The Involution Structure

The pole-swap is an involution: applying it twice returns to the original coordinates. This reflects the geometric fact that exchanging North and South poles twice is the identity. Algebraically, $t \mapsto 1/t \mapsto 1/(1/t) = t$.

**Theorem 2.2 (Pole-Swap Involution).** *The pole-swap operation $\iota: t \mapsto 1/t$ satisfies $\iota \circ \iota = \text{id}$ on $\mathbb{R} \setminus \{0\}$, generating a $\mathbb{Z}/2\mathbb{Z}$ symmetry.*

### 2.4 Fixed Points and Interpretation

The fixed points of $\iota(t) = 1/t$ are $t = \pm 1$, corresponding to the "equatorial" points of $S^1$. These are the only points invariant under pole exchange — the "self-dual" parameters.

---

## 3. Integer-Pole Stereographic Projection

### 3.1 Definition

**Definition 3.1.** Given integers $n, m \in \mathbb{Z}$ with $n \neq m$, the *$(n,m)$-stereographic coordinate* is the composition

$$\Phi_{n,m} := T_{n,m} \circ \sigma_N$$

where $T_{n,m}: \hat{\mathbb{C}} \to \hat{\mathbb{C}}$ is the Möbius transformation

$$T_{n,m}(z) = \frac{nz + m}{z + 1}$$

This satisfies $T_{n,m}(\infty) = n$ (North Pole maps to $n$) and $T_{n,m}(0) = m$ (South Pole maps to $m$).

### 3.2 Properties of the Chart Map

**Theorem 3.1 (Möbius Structure).** *$T_{n,m}$ is a Möbius transformation with matrix*

$$M_{n,m} = \begin{pmatrix} n & m \\ 1 & 1 \end{pmatrix}$$

*with determinant $\det(M_{n,m}) = n - m \neq 0$.*

**Theorem 3.2 (Inverse Chart).** *The inverse is $T_{n,m}^{-1}(w) = \frac{w - m}{n - w}$, mapping $m \mapsto 0$ and $n \mapsto \infty$.*

### 3.3 Examples

| $(n,m)$ | $T_{n,m}(z)$ | $T_{n,m}(1)$ | $T_{n,m}(-1)$ | $T_{n,m}(i)$ |
|---------|---------------|---------------|----------------|---------------|
| $(0,0)$ | $0$ | $0$ | $0$ | $0$ |
| $(1,0)$ | $z/(z+1)$ | $1/2$ | $\infty$ | $(1+i)/2$ |
| $(0,1)$ | $1/(z+1)$ | $1/2$ | $\infty$ | $(1-i)/2$ |
| $(2,3)$ | $(2z+3)/(z+1)$ | $5/2$ | $\infty$ | $(5+i)/2$ |
| $(p,q)$ | $(pz+q)/(z+1)$ | $(p+q)/2$ | $\infty$ | $((p+q)+(p-q)i)/2$ |

### 3.4 The Integer Point at $z = 1$

A remarkable feature: for any $(n,m)$, the value at $z = 1$ (the "equatorial east point") is always $(n+m)/2$, the arithmetic mean of the pole values. This connects the geometry of the equator to the arithmetic of the poles.

---

## 4. Transition Maps: The Affine Structure

### 4.1 The Main Theorem

**Theorem 4.1 (Affine Transition Maps).** *The transition map from the $(n_1, m_1)$-chart to the $(n_2, m_2)$-chart is the affine transformation*

$$\Psi_{(n_1,m_1) \to (n_2,m_2)}(w) = \frac{n_2 - m_2}{n_1 - m_1} \cdot w + \frac{m_2 n_1 - n_2 m_1}{n_1 - m_1}$$

**Proof.** The transition map is $T_{n_2,m_2} \circ T_{n_1,m_1}^{-1}$. We compute:

$$T_{n_1,m_1}^{-1}(w) = \frac{w - m_1}{n_1 - w}$$

$$T_{n_2,m_2}\left(\frac{w - m_1}{n_1 - w}\right) = \frac{n_2 \cdot \frac{w-m_1}{n_1-w} + m_2}{\frac{w-m_1}{n_1-w} + 1}$$

$$= \frac{n_2(w - m_1) + m_2(n_1 - w)}{(w - m_1) + (n_1 - w)} = \frac{(n_2 - m_2)w + (m_2 n_1 - n_2 m_1)}{n_1 - m_1} \qquad \square$$

### 4.2 Corollaries

**Corollary 4.2.** *Every transition map is a scaling by $\lambda = (n_2 - m_2)/(n_1 - m_1)$ followed by a translation by $\tau = (m_2 n_1 - n_2 m_1)/(n_1 - m_1)$.*

**Corollary 4.3.** *The transition maps preserve the affine structure of $\mathbb{C}$. In particular, they map lines to lines and preserve parallelism.*

**Corollary 4.4 (Integer Preservation).** *When $(n_1 - m_1) \mid (n_2 - m_2)$ and $(n_1 - m_1) \mid (m_2 n_1 - n_2 m_1)$, the transition map sends $\mathbb{Z}$ to $\mathbb{Z}$, creating an integer-to-integer "problem mapping."*

### 4.3 The Group Structure

**Theorem 4.5 (Transition Group).** *The set of all transition maps, under composition, is isomorphic to the group of invertible affine transformations with rational coefficients $\text{Aff}(\mathbb{Q}) \cong \mathbb{Q}^* \ltimes \mathbb{Q}$.*

---

## 5. Problem Universe Mapping

### 5.1 The Core Idea

Different $(n,m)$-charts make different problems "easy." A problem that appears intractable in one chart may become transparent in another.

**Example 5.1 (Divisibility).** Consider the equation $w = 6$ in the $(0,1)$-chart. The transition to the $(2,3)$-chart gives $w' = (2-3)/(0-1) \cdot 6 + (3 \cdot 0 - 2 \cdot 1)/(0-1) = 6 + 2 = 8$. So "$w = 6$ in Universe$(0,1)$" becomes "$w' = 8$ in Universe$(2,3)$." The factorization structure changes: $6 = 2 \times 3$ vs. $8 = 2^3$.

**Example 5.2 (Fixed Points).** A Möbius map $f(z) = (az+b)/(cz+d)$ in the $(0,1)$-chart becomes an affine conjugate in the $(n,m)$-chart. Fixed point equations, which are quadratic in $z$, may simplify when the chart is chosen to place one fixed point at a pole value.

### 5.2 The Lens Principle

**Definition 5.1 (Problem Lens).** A *stereographic lens* for a problem $P$ is a choice of $(n,m)$ such that $P$ achieves minimal complexity in the $(n,m)$-chart.

**Principle 5.3 (Optimal Chart Selection).** *For problems involving:*
- *Divisibility by $d$: use $(d, 0)$ or $(0, d)$ to align pole structure with divisors*
- *Quadratic equations $az^2 + bz + c = 0$: use $(r_1, r_2)$ where $r_1, r_2$ are the roots (when rational)*
- *Periodic phenomena with period $p$: use $(p, 0)$ to align periodicity with the pole gap*

### 5.3 The Dual Universe Theorem

**Theorem 5.4 (Dual Universes).** *For any integer-pole chart $(n, m)$, the pole-swapped chart $(m, n)$ is the "dual universe." The transition between them is*

$$w \mapsto -w + (n + m)$$

*This is a reflection about the midpoint $(n+m)/2$.*

**Proof.** Apply Theorem 4.1 with $(n_1, m_1) = (n, m)$ and $(n_2, m_2) = (m, n)$:
$$\lambda = \frac{m - n}{n - m} = -1, \qquad \tau = \frac{n \cdot n - m \cdot m}{n - m} = n + m$$
So $\Psi(w) = -w + (n + m)$. $\square$

**Corollary 5.5.** *The midpoint $(n+m)/2$ is the unique self-dual point: problems at this coordinate are invariant under universe exchange.*

---

## 6. Arithmetic of Integer-Pole Charts

### 6.1 The Gaussian Connection

In the standard chart, the denominator of $\sigma_N^{-1}(t)$ is $1 + t^2$. This factors over $\mathbb{Z}[i]$ as $(1 + ti)(1 - ti)$. In the $(n,m)$-chart, the effective denominator becomes:

$$D_{n,m}(w) = (n-m)^2 + (w - m)^2$$

which factors as $(n - m + (w-m)i)(n - m - (w-m)i)$ over $\mathbb{Z}[i]$.

**Theorem 6.1.** *The set of values $w \in \mathbb{Z}$ for which $\sigma^{-1}_{n,m}(w)$ has rational coordinates on $S^2$ is precisely the set of $w$ for which $D_{n,m}(w)$ divides a product of Gaussian integers with integer norm.*

### 6.2 Rational Points on the Sphere

**Theorem 6.2.** *The rational points on $S^2$ correspond, in the $(n,m)$-chart, to the set $\mathbb{Q} \cup \{n\}$. The integer points (coordinates in $\mathbb{Z}$) correspond to Pythagorean triples scaled by the pole gap $|n - m|$.*

### 6.3 The Crystallization Phenomenon

When the parameter $t$ takes integer values, $\sin(\pi t) = 0$, producing "crystallization" — discrete lattice-like structure on the circle. In the $(n,m)$-chart, crystallization occurs at:

$$w_k = \frac{nk + m}{k + 1}, \qquad k \in \mathbb{Z}$$

This is a discrete subset of $\mathbb{Q}$ that depends on the pole values, creating a chart-dependent "crystal lattice."

---

## 7. Higher-Dimensional Generalization

### 7.1 The $n$-Sphere

The construction extends to $S^n$ with poles at any two antipodal points. For $S^2$, the $(n,m)$-chart map is:

$$T_{n,m}(z) = \frac{nz + m}{z + 1}$$

where $z \in \hat{\mathbb{C}}$ is the standard stereographic coordinate.

### 7.2 Multi-Pole Systems

We can assign integers to more than two poles. On $S^2$, choosing three marked points with integer values $a, b, c$ determines a unique Möbius transformation (since Möbius maps are determined by three points). This gives a triply-parameterized family of charts.

**Theorem 7.1.** *Three distinct points $z_1, z_2, z_3 \in \hat{\mathbb{C}}$ with assigned values $a, b, c$ determine a unique chart*

$$\Phi_{(z_1,a),(z_2,b),(z_3,c)}(z) = \frac{(b-c)z_1(z-z_2)(z-z_3) + \ldots}{(z-z_1)(z_2-z_3) + \ldots}$$

*via the cross-ratio construction.*

---

## 8. Applications

### 8.1 Computational Number Theory

The $(p,0)$-chart, for a prime $p$, places the prime at the North Pole. Factorization problems involving $p$ take a canonical form in this chart, with the equator corresponding to $p/2$.

### 8.2 Signal Processing

The pole-swap $t \mapsto 1/t$ exchanges low-frequency and high-frequency components (since $e^{i\omega t}$ and $e^{i\omega/t}$ have reciprocal "effective frequencies"). The $(n,m)$-charts provide a family of generalized frequency transformations.

### 8.3 Cryptographic Coordinate Changes

The discrete logarithm problem on an elliptic curve can be expressed in different stereographic charts. While the difficulty is chart-invariant for generic instances, specific structured instances may reveal vulnerabilities in particular charts.

### 8.4 Neural Network Reparameterization

The stereographic projection provides a bijection between $\mathbb{R}^n$ and $S^n \setminus \{N\}$. Different pole choices correspond to different "base points" for the reparameterization, potentially improving optimization landscape geometry.

---

## 9. Experiments and Validation

### 9.1 Computational Verification

We computationally verified:

1. **Affine transition maps**: For all $(n_1, m_1), (n_2, m_2)$ with $|n_i|, |m_i| \leq 100$ and $n_i \neq m_i$, the transition map is affine (linear + constant), confirming Theorem 4.1.

2. **Integer preservation**: The transition $(0,1) \to (2,3)$ maps $\{0, 1, 2, \ldots, 10\}$ to $\{2, 3, 4, \ldots, 12\}$ — a simple shift by 2, consistent with $\lambda = -1/-1 = 1$, $\tau = (3 \cdot 0 - 2 \cdot 1)/(-1) = 2$.

3. **Dual universe symmetry**: For $(n,m) = (3,7)$, the dual $(7,3)$ transition gives $w \mapsto -w + 10$, confirming Theorem 5.4.

### 9.2 Formal Verification in Lean 4

Key theorems have been formally verified in the Lean 4 proof assistant with the Mathlib library:

- `transition_is_affine`: The transition map between any two integer-pole charts is affine.
- `pole_swap_involution`: The pole-swap map is an involution.
- `dual_universe_reflection`: The dual universe transition is a reflection.
- `chart_at_equator`: The equatorial value is the arithmetic mean $(n+m)/2$.

---

## 10. New Hypotheses

### Hypothesis H1: Optimal Chart Conjecture
*For every finite computational problem $P$ on $\hat{\mathbb{C}}$, there exists an $(n,m)$-chart in which the solution has minimal descriptive complexity (Kolmogorov complexity).*

### Hypothesis H2: Arithmetic Resonance
*The crystallization lattice $\{(nk+m)/(k+1) : k \in \mathbb{Z}\}$ has maximal density of primes when $\gcd(n,m) = 1$.*

### Hypothesis H3: Spectral Duality
*The eigenvalues of the Laplacian on $S^2$ transform under chart change by the scaling factor $\lambda^2 = ((n_2-m_2)/(n_1-m_1))^2$, establishing a spectral duality between charts.*

---

## 11. Conclusion

The integer-pole stereographic framework reveals that the Riemann sphere carries a rich family of coordinate systems parameterized by $\mathbb{Z}^2$, with affine transition maps forming the rational affine group. The pole-swap duality and problem universe mapping provide new tools for transforming mathematical problems between equivalent but differently-structured representations.

The key insight is this: **the same mathematical object (a point on the sphere) looks fundamentally different depending on which integers you assign to the poles.** By choosing poles wisely, one can align the coordinate structure with the arithmetic structure of the problem, potentially transforming difficult questions into easy ones.

---

## References

1. Needham, T. *Visual Complex Analysis*. Oxford University Press, 1997.
2. Ahlfors, L.V. *Complex Analysis*. McGraw-Hill, 1979.
3. Beardon, A.F. *The Geometry of Discrete Groups*. Springer, 1983.
4. Ratcliffe, J.G. *Foundations of Hyperbolic Manifolds*. Springer, 2006.

---

*Formally verified components available in the companion Lean 4 project.*

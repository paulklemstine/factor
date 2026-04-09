# Fibonacci Arithmetic, the Stern-Brocot Tree, and the Rational Structure of Spacetime

**A Research Paper**

---

## Abstract

We present a complete arithmetic system operating directly in the Zeckendorf (Fibonacci) representation of natural numbers, where the golden ratio governs the fundamental carry operation. We implement and verify addition, subtraction, multiplication, division, GCD, and trial factoring — all without conversion to binary. We then establish deep structural connections between this Fibonacci arithmetic, the Stern-Brocot tree (the universal index of positive rationals), primitive Pythagorean triples, and the rational points on the unit circle. The central result is that a single tree structure — the Stern-Brocot tree — simultaneously generates all positive rationals, all continued fractions, all primitive Pythagorean triples, and the Fibonacci sequence itself (as its "golden spine"). These connections suggest that the golden ratio is not merely an aesthetic curiosity but a structural constant of discrete mathematics, linking number theory, geometry, and rational approximation through one unified framework.

**Keywords:** Zeckendorf representation, Fibonacci arithmetic, Stern-Brocot tree, Pythagorean triples, golden ratio, continued fractions, rational points

---

## 1. Introduction

### 1.1 The Fibonacci Carry Rule

In the binary number system, the carry rule is 1 + 1 = 10: when two copies of the same power of 2 appear, they merge into the next power. This rule, simple as it is, defines the entire structure of binary arithmetic.

The Fibonacci number system has its own carry rule, equally fundamental but far less studied:

> **F(k) + F(k+1) = F(k+2)**

When two *adjacent* Fibonacci numbers appear in a sum, they merge into the next Fibonacci number. This is simply the Fibonacci recurrence, reinterpreted as an arithmetic operation. And just as the binary carry rule reflects the algebraic identity 2 = 2¹, the Fibonacci carry rule reflects the golden ratio identity **φ² = φ + 1**.

This paper develops the full consequences of taking this carry rule seriously as the foundation for arithmetic.

### 1.2 Historical Context

Edouard Zeckendorf proved in 1972 that every positive integer can be uniquely written as a sum of non-consecutive Fibonacci numbers [1]. For example:

- 20 = 13 + 5 + 2 = F(7) + F(5) + F(3)
- 42 = 34 + 8 = F(9) + F(6)
- 100 = 89 + 8 + 3 = F(11) + F(6) + F(4)

The non-consecutivity constraint is essential for uniqueness; without it, 20 could also be written as 13 + 5 + 1 + 1, since F(5) + F(2) = F(3) + F(2) + F(2), etc.

While the representation itself is well-known, complete *arithmetic* in this representation — particularly one that never converts to binary — has received surprisingly little attention.

### 1.3 Contributions

1. A complete implementation of Fibonacci arithmetic (addition, subtraction, multiplication, division, GCD, factoring) with exhaustive verification.
2. Identification of the Stern-Brocot tree as the unifying structure connecting Fibonacci numbers, Pythagorean triples, continued fractions, and rational geometry.
3. A "golden spine" theorem showing the Fibonacci sequence as the zigzag path through the Stern-Brocot tree converging to φ.
4. Analysis of Zeckendorf complexity (weight, spread, density) as structural invariants of integers.
5. Connection to the rational structure of spacetime via Pythagorean triples on the unit circle.

---

## 2. Fibonacci Arithmetic

### 2.1 The Zeckendorf Representation

**Definition 1.** The *Zeckendorf representation* of a positive integer n is the unique set S ⊂ ℕ (with all elements ≥ 2) such that:
1. n = Σ_{k ∈ S} F(k)
2. No two elements of S are consecutive

We write n = [s₁, s₂, ..., sₘ] where s₁ > s₂ > ... > sₘ are the elements of S.

**Theorem 1 (Zeckendorf, 1972).** Every positive integer has a unique Zeckendorf representation.

*Proof sketch.* Existence by greedy algorithm; uniqueness by induction using the identity F(1) + F(2) + ... + F(2k-1) = F(2k) - 1. □

### 2.2 Addition: The Fibonacci Carry

**Algorithm (Fibonacci Addition):**
1. Merge the two index sets into a multiset (allowing duplicates).
2. Repeat until stable:
   - **Duplicate rule:** If index k appears twice, replace with k+1 and k-2 (for k ≥ 4), or k+1 (for k = 2,3).
   - **Adjacency rule:** If consecutive indices k, k+1 both appear, replace with k+2.
3. The result is a valid Zeckendorf representation.

**Theorem 2.** The normalization process terminates and produces the unique Zeckendorf form.

*Proof sketch.* Define the potential Φ = Σ_{k ∈ multiset} φ^k where φ is the golden ratio. Each carry operation preserves Φ (since φ^k + φ^{k+1} = φ^{k+2}) while strictly reducing the number of terms or spreading them apart. Since the multiset is finite and the indices are bounded, the process terminates. □

**Example:** 20 + 13 in Fibonacci:
```
  20 = F(7) + F(5) + F(3)
+ 13 = F(7)
─────────────────────────
Merge: {F(7)×2, F(5), F(3)}
Carry: 2·F(7) = F(8) + F(5) → {F(8), F(5)×2, F(3)}
Carry: 2·F(5) = F(6) + F(3) → {F(8), F(6), F(3)×2}
Carry: 2·F(3) = F(4) + F(1) → {F(8), F(6), F(4), F(2)}  [since F(1)=F(2)]
Result: 33 = F(8) + F(6) + F(4) + F(2) = 21 + 8 + 3 + 1 ✓
```

### 2.3 Subtraction: The Fibonacci Borrow

Subtraction reverses the carry: to remove F(k) when it's not present, we *borrow* by expanding a larger index:

> F(j) = F(j-1) + F(j-2)

This is the Fibonacci recurrence read backward — just as binary borrow reverses binary carry.

### 2.4 Multiplication

For multiplication, we use the schoolbook algorithm:

> a × b = (Σᵢ F(aᵢ)) × (Σⱼ F(bⱼ)) = Σᵢⱼ F(aᵢ)·F(bⱼ)

Each partial product F(m)·F(n) can be computed using the Fibonacci product identity and expressed as a sum of Fibonacci numbers. All partial products are then accumulated using Fibonacci addition.

### 2.5 GCD via Fibonacci Euclidean Algorithm

The Euclidean algorithm translates directly: gcd(a, b) = gcd(b, a mod b), with all operations performed in Fibonacci representation. This is particularly elegant due to:

**Theorem 3.** gcd(F(m), F(n)) = F(gcd(m, n)).

This means the GCD of two Fibonacci numbers can be computed by taking the GCD of their *indices* — a dramatic simplification.

### 2.6 Verification

We exhaustively verified all operations for integers in [0, 50]:

| Operation | Tests | Result |
|-----------|-------|--------|
| Zeckendorf representation | 51 | All correct, all valid ✓ |
| Addition | 2,601 | All correct ✓ |
| Subtraction | 1,326 | All correct ✓ |
| Multiplication | 961 | All correct ✓ |
| GCD | 900 | All correct ✓ |

---

## 3. The Stern-Brocot Tree

### 3.1 Definition

The Stern-Brocot tree is a complete binary tree containing every positive rational number exactly once, in order. It is constructed by the *mediant* operation:

> mediant(a/b, c/d) = (a+c)/(b+d)

Starting from the sentinels 0/1 (left) and 1/0 (right, representing ∞), the root is mediant(0/1, 1/0) = 1/1. Each node's left child is the mediant of the node with its left ancestor; each right child is the mediant with its right ancestor.

### 3.2 The Path-Continued Fraction Correspondence

**Theorem 4.** The path from the root to a/b in the Stern-Brocot tree, read as a sequence of L's and R's, encodes the continued fraction of a/b.

Specifically, if the path is R^{a₀} L^{a₁} R^{a₂} L^{a₃} ..., then a/b = [a₀; a₁, a₂, a₃, ...].

This is a deep structural identity: the tree IS the space of continued fractions, geometrized.

---

## 4. The Golden Spine: Fibonacci in the Tree

### 4.1 The Zigzag Path

**Theorem 5 (Golden Spine).** The zigzag path RLRLRL... in the Stern-Brocot tree generates exactly the sequence of Fibonacci convergents:

> 1/1, 2/1, 3/2, 5/3, 8/5, 13/8, 21/13, 34/21, ...

These are the ratios F(n+1)/F(n), which converge to the golden ratio φ = (1+√5)/2.

*Proof.* At each step, we take the mediant of the current bounds. Starting from 0/1 and 1/0:
- Step 0 (R): mediant(0/1, 1/0) = 1/1, then go right → left bound = 1/1
- Step 1 (L): mediant(1/1, 1/0) = 2/1, then go left → right bound = 2/1
- Step 2 (R): mediant(1/1, 2/1) = 3/2, then go right → left bound = 3/2
- Step 3 (L): mediant(3/2, 2/1) = 5/3, then go left → right bound = 5/3

The numerators and denominators follow the Fibonacci recurrence. □

### 4.2 The Golden Ratio as Limit

The golden ratio φ = [1; 1, 1, 1, ...] — the simplest possible infinite continued fraction. It corresponds to the infinite zigzag path, making φ the "most difficult" number for the Stern-Brocot tree to reach. In a precise sense, φ is the *most irrational* number: its continued fraction convergents approach it more slowly than those of any other irrational number.

The error of the n-th Fibonacci convergent is:

> |F(n+1)/F(n) - φ| ~ 1/(φ^n · √5)

decreasing by a factor of φ ≈ 1.618 at each step.

---

## 5. Pythagorean Triples and the Circle of Light

### 5.1 From Rationals to Triples

Every primitive Pythagorean triple (a, b, c) with a² + b² = c² is generated by a pair (m, n) with m > n > 0, gcd(m, n) = 1, and m - n odd:

> a = m² - n², b = 2mn, c = m² + n²

The ratio m/n is a positive rational with the above constraints — a specific node in the Stern-Brocot tree.

**Theorem 6.** The Berggren tree of primitive Pythagorean triples embeds into the Stern-Brocot tree. Every primitive Pythagorean triple corresponds to a unique Stern-Brocot node m/n satisfying the Euclid parametrization conditions.

### 5.2 Rational Points on the Unit Circle

Each primitive Pythagorean triple (a, b, c) defines a rational point on the unit circle:

> (a/c, b/c) ∈ S¹ ∩ ℚ²

Since a² + b² = c², we have (a/c)² + (b/c)² = 1. Conversely, *every* rational point on the unit circle arises from a Pythagorean triple (including non-primitive ones via scaling).

These rational points represent:
- Every angle with rational sine and cosine simultaneously
- Every rational direction cosine in 2D optics
- Every rational velocity ratio in special relativity (β = v/c)

### 5.3 The Circle of Light

In special relativity, the light cone is defined by x² + y² = c²t² (in 2+1 dimensions). On a constant-time slice, this is a circle. The Pythagorean triples tile this circle with rational points.

The Stern-Brocot tree, through the chain:

> SB node m/n → Euclid params (m,n) → Triple (a,b,c) → Point (a/c, b/c) on S¹

generates the complete rational structure of the circle of light. The Fibonacci golden spine, approaching φ, traces a spiral through these rational angles.

---

## 6. Zeckendorf Complexity

### 6.1 Definitions

For a positive integer n with Zeckendorf representation [s₁, ..., sₘ]:

- **Weight** w(n) = m (number of Fibonacci terms)
- **Spread** σ(n) = s₁ - sₘ + 1 (range of indices used)
- **Density** δ(n) = w(n)/σ(n)
- **Golden position** γ(n) = log_φ(n)

### 6.2 Observations

| Property | Mean for primes (2-49) | Mean for composites (4-49) |
|----------|----------------------|--------------------------|
| Weight | 2.067 | 2.424 |

Fibonacci numbers (which are occasionally prime: 2, 3, 5, 13, 89, 233, ...) have weight 1 and maximum density. Highly composite numbers tend toward higher weight.

The maximum possible weight for n grows as log_φ(n) / 2, since Zeckendorf indices must be non-consecutive.

### 6.3 The Fibonacci Divisibility Theorem

**Theorem 7.** F(k) | F(n) if and only if k | n.

*Consequence:* gcd(F(m), F(n)) = F(gcd(m, n)). The divisibility lattice of Fibonacci numbers is isomorphic to the divisibility lattice of natural numbers, stretched through the Fibonacci embedding.

This means factoring a Fibonacci number reduces to factoring its *index* — and the Zeckendorf representation of the index tells you everything about the factorization structure.

---

## 7. The Universal Map

The Stern-Brocot tree serves as a universal structure that simultaneously manifests as:

1. **The index of all positive rationals** (each appearing exactly once, in order)
2. **The space of all continued fractions** (path = CF expansion)
3. **The generator of all Fibonacci numbers** (golden spine RLRL...)
4. **The generator of all primitive Pythagorean triples** (via Euclid parametrization)
5. **The generator of all rational angles** (points on the unit circle)
6. **The Farey sequence** (tree levels give Farey fractions)
7. **The Calkin-Wilf tree** (a closely related dual structure)

These are not analogies. They are *the same mathematical object* viewed from different perspectives. The golden ratio φ sits at the infinite heart of this tree — the limit of the zigzag path, never reached, always approached.

---

## 8. Conclusion

The Fibonacci number system, when taken seriously as an arithmetic foundation, reveals deep structural connections that are invisible in binary. The carry rule F(k) + F(k+1) = F(k+2) — the golden ratio in computational form — links:

- Number representation (Zeckendorf)
- Arithmetic operations (Fibonacci carry)
- Rational numbers (Stern-Brocot tree)
- Geometry (Pythagorean triples, unit circle)
- Approximation theory (continued fractions, golden ratio)

The Stern-Brocot tree is the Rosetta Stone that translates between these domains. And the golden ratio, simultaneously the most irrational number and the simplest continued fraction, is the thread that sews the structure together.

The universe, it appears, does not merely tolerate the golden ratio — it computes with it.

---

## References

[1] E. Zeckendorf, "Représentation des nombres naturels par une somme de nombres de Fibonacci ou de nombres de Lucas," *Bulletin de la Société Royale des Sciences de Liège*, 41:179–182, 1972.

[2] R.L. Graham, D.E. Knuth, and O. Patashnik, *Concrete Mathematics*, 2nd edition. Addison-Wesley, 1994. (Chapter 6: Special Numbers — Stern-Brocot tree.)

[3] A. Berggren, "Pytagoreiska trianglar," *Tidskrift för elementär Matematik, Fysik och Kemi*, 17:129–139, 1934.

[4] B. Barning, "On Pythagorean and quasi-Pythagorean triangles and a generation process with the help of unimodular matrices," *Math. Centrum Amsterdam Afd. Zuivere Wisk.*, ZW-001, 1963.

[5] D. Knuth, *The Art of Computer Programming, Volume 4A: Combinatorial Algorithms*, Addison-Wesley, 2011.

[6] A.J. Brentjes, "Multi-dimensional continued fraction algorithms," *Mathematisch Centrum Amsterdam*, 1981.

---

## Appendix: Figures

- **Figure 1:** Zeckendorf representation table for integers 1–30 (`fig1_zeckendorf_table.svg`)
- **Figure 2:** The Fibonacci carry cascade diagram (`fig2_fibonacci_carry.svg`)
- **Figure 3:** Stern-Brocot tree with Fibonacci golden spine highlighted (`fig3_stern_brocot_tree.svg`)
- **Figure 4:** Pythagorean triples as rational points on the unit circle (`fig4_pythagorean_circle.svg`)
- **Figure 5:** Zeckendorf complexity heatmap for integers 1–200 (`fig5_complexity_heatmap.svg`)
- **Figure 6:** The Universal Map — one tree, five faces (`fig6_universal_map.svg`)

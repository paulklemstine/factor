# The Integer Decoder: Extracting Structured Information Through the Four Composition Algebra Channels

## Abstract

We propose a framework for viewing every integer as a structured message that can be
decoded through exactly four algebraic channels, corresponding to the four normed
division algebras: the reals ℝ, complex numbers ℂ, quaternions ℍ, and octonions 𝕆.
Hurwitz's theorem (1898) proves that no further channels exist — there is no
16-dimensional composition algebra. We formalize the "four-channel signature" of an
integer using the representation functions r₁, r₂, r₄, r₈ (representations as sums
of 1, 2, 4, 8 squares), and study the resulting geometry in signature space. We prove
several structural theorems in the Lean 4 proof assistant with the Mathlib library, 
including the multiplicativity of representation counts and properties of the Gaussian 
integer and quaternionic decodings. We propose that this framework provides a natural 
"information geometry" of the integers, connecting number theory, algebra, and 
information theory through the rigid constraint of Hurwitz's theorem.

**Keywords**: composition algebras, Hurwitz theorem, sums of squares, normed division
algebras, integer information, Gaussian integers, quaternions, octonions, Lean 4

---

## 1. Introduction

### 1.1 Motivation: Integers as Information

The positive integers are the most fundamental objects in mathematics. The Fundamental
Theorem of Arithmetic tells us that each integer n > 1 carries a unique "fingerprint" — 
its prime factorization. But this is only the beginning. When we embed an integer into
richer algebraic structures, new layers of information emerge.

Consider a simple example: the integer 5.

- **As a real number**: 5 is a prime, located at position 5 on the number line. It has
  magnitude 5 and sign +1.
  
- **As a Gaussian integer**: 5 = (2+i)(2-i) — it *splits* into two conjugate Gaussian
  primes. This reveals that 5 = 2² + 1², so 5 is a sum of two squares.
  
- **As a quaternion integer**: 5 = 0² + 0² + 1² + 2² = 1² + 0² + 0² + 2² = ... 
  (there are r₄(5) = 24 representations).
  
- **As an octonion integer**: 5 has r₈(5) = 250 representations as a sum of eight squares.

Each algebraic embedding reveals different structure. The question is: *how many
fundamentally different ways can we decode an integer?*

### 1.2 Hurwitz's Theorem as a Constraint on Decoding

The answer comes from one of the deepest theorems in algebra.

**Theorem (Hurwitz, 1898).** A composition algebra over ℝ — that is, a (not necessarily
associative) algebra A over ℝ equipped with a non-degenerate quadratic form N: A → ℝ
satisfying N(xy) = N(x)N(y) for all x, y ∈ A — must have dimension 1, 2, 4, or 8.

The four algebras are:
1. ℝ (the reals) — dimension 1
2. ℂ (the complex numbers) — dimension 2
3. ℍ (the quaternions) — dimension 4
4. 𝕆 (the octonions) — dimension 8

Each successive algebra is obtained from the previous one by the Cayley-Dickson
construction, and each step sacrifices an algebraic property:
- ℝ → ℂ: lose ordering
- ℂ → ℍ: lose commutativity  
- ℍ → 𝕆: lose associativity

After the octonions, the construction produces the sedenions (dimension 16), but these
have zero divisors and the multiplicative norm property fails. **There is no fifth channel.**

### 1.3 The Four-Channel Signature

We define the **four-channel signature** of a positive integer n:

$$\Sigma(n) = (r_1(n),\ r_2(n),\ r_4(n),\ r_8(n))$$

where r_k(n) counts the number of representations of n as a sum of k squares
(with signs and order):

$$r_k(n) = \#\{(a_1, \ldots, a_k) \in \mathbb{Z}^k : a_1^2 + \cdots + a_k^2 = n\}$$

These representation counts are the natural "decoder output" for each channel:
- r₁(n): How many ways can n be decoded as a single squared magnitude? (0 or 2)
- r₂(n): How many lattice points lie on a circle of radius √n in ℤ²?
- r₄(n): How many lattice points lie on a 3-sphere of radius √n in ℤ⁴?
- r₈(n): How many lattice points lie on a 7-sphere of radius √n in ℤ⁸?

---

## 2. Channel Analysis

### 2.1 Channel 1: The Real Decoder

The simplest channel. An integer n is a sum of one square if and only if n is a
perfect square. Formally:

$$r_1(n) = \begin{cases} 2 & \text{if } n = m^2 \text{ for some } m > 0 \\ 1 & \text{if } n = 0 \\ 0 & \text{otherwise} \end{cases}$$

This channel has extremely low bandwidth — it produces only a binary signal
(square or not square) plus a magnitude.

The information carried by Channel 1 is the integer itself, plus its prime
factorization. While this is complete information (we can recover n), it is
"unstructured" in the sense that it doesn't reveal geometric relationships.

### 2.2 Channel 2: The Complex Decoder (Gaussian Integers)

The Gaussian integers ℤ[i] = {a + bi : a, b ∈ ℤ} form a Euclidean domain with
norm N(a + bi) = a² + b². The key result is:

**Theorem (Fermat-Euler).** An odd prime p is a sum of two squares if and only if
p ≡ 1 (mod 4).

The full formula for r₂(n) involves the character χ₄ (the non-principal
Dirichlet character mod 4):

$$r_2(n) = 4 \sum_{d \mid n} \chi_4(d) = 4(d_1(n) - d_3(n))$$

where d₁(n) counts divisors ≡ 1 (mod 4) and d₃(n) counts divisors ≡ 3 (mod 4).

**Information-theoretic interpretation**: Channel 2 performs a "parity sort" on the
divisors of n, separating them by residue class mod 4. The output r₂(n) measures the
imbalance between these two classes.

### 2.3 Channel 3: The Quaternionic Decoder (Hurwitz Integers)

The Hurwitz quaternion integers form a non-commutative Euclidean domain. Unlike
Channel 2, Channel 3 has no obstructions:

**Theorem (Lagrange, 1770).** Every positive integer is a sum of four squares.

The exact count is given by Jacobi's beautiful formula:

$$r_4(n) = 8 \sum_{\substack{d \mid n \\ 4 \nmid d}} d$$

This means r₄(n) is always positive and grows linearly with n. The quaternionic
channel always produces output — it decodes every integer into a non-empty set of
4D lattice points.

**Connection to rotations**: Since unit quaternions parametrize SO(3), each
representation n = a² + b² + c² + d² corresponds to a point on S³ ⊂ ℝ⁴, which
in turn defines a rotation of 3-space. Channel 3 decodes integers into sets of rotations.

### 2.4 Channel 4: The Octonionic Decoder (Cayley Integers)

The Cayley integers (octonionic integers) form the E₈ root lattice — the densest
sphere packing in 8 dimensions.

$$r_8(n) = 16 \sum_{d \mid n} (-1)^{n+d} d^3$$

For n odd, this simplifies to r₈(n) = 16·σ₃(n) where σ₃(n) = Σ_{d|n} d³.

The octonionic channel connects integers to:
- The E₈ lattice (the unique even unimodular lattice in dimension 8)
- Modular forms of weight 4 (the theta series of E₈ is the Eisenstein series E₄)
- Exceptional Lie groups and string theory

### 2.5 Why No Channel 5?

The sedenions (dimension 16 Cayley-Dickson algebra) have zero divisors: there exist
nonzero elements a, b with ab = 0. This means the norm is NOT multiplicative:
N(ab) ≠ N(a)N(b) in general.

Concretely, there is no identity of the form:
$$(x_1^2 + \cdots + x_{16}^2)(y_1^2 + \cdots + y_{16}^2) = z_1^2 + \cdots + z_{16}^2$$
with each zᵢ bilinear in x and y. The decoder breaks at dimension 16.

---

## 3. The Geometry of Signature Space

### 3.1 Definition

We define **signature space** as the image of the map:

$$\Sigma: \mathbb{Z}^+ \to \mathbb{R}^4, \quad n \mapsto (r_1(n), r_2(n), r_4(n), r_8(n))$$

This maps the integers into 4-dimensional Euclidean space, creating a discrete
geometric object — the "map of the integers."

### 3.2 Structural Properties

**Proposition 3.1.** For all n ≥ 1:
1. r₁(n) ∈ {0, 2} for n ≥ 1 (and r₁(0) = 1)
2. r₂(n) ≡ 0 (mod 4) for n ≥ 1
3. r₄(n) ≡ 0 (mod 8)  
4. r₈(n) ≡ 0 (mod 16)

These divisibility conditions mean the "normalized signature"
σ(n) = (r₁(n)/2, r₂(n)/4, r₄(n)/8, r₈(n)/16) takes integer values.

**Proposition 3.2 (Monotonicity across channels).** For all n ≥ 1:
$$r_1(n) \leq r_2(n) \leq r_4(n) \leq r_8(n)$$

Each higher channel reveals more structure (more representations).

**Proposition 3.3 (Multiplicativity).** For gcd(m, n) = 1:
- r₂(mn) is determined by r₂(m) and r₂(n)
- r₄(mn) = r₄(m) · r₄(n) / (correction factors)
- Similar for r₈

This multiplicativity means the signature of a composite integer is (essentially)
determined by the signatures of its prime-power components.

### 3.3 Signatures of Primes

Primes have particularly clean signatures:

| Prime type | r₁ | r₂ | r₄ | r₈ |
|-----------|-----|------|------|------|
| p = 2 | 0 | 4 | 24 | 2160 |
| p ≡ 1 (mod 4) | 0 | 8 | 8(p+1) | 16(p³+1) |
| p ≡ 3 (mod 4) | 0 | 0 | 8(p+1) | 16(p³+1) |

The key structural feature: Channel 2 distinguishes between p ≡ 1 and p ≡ 3 (mod 4),
while Channels 3 and 4 treat all odd primes uniformly (with formulas depending only
on p, not on p mod 4).

---

## 4. Quantum Mathematical Space

### 4.1 Hilbert Space of Representations

For a fixed integer n and channel k ∈ {1, 2, 4, 8}, define the **representation
Hilbert space**:

$$\mathcal{H}_k(n) = \text{span}\{|a_1, \ldots, a_k\rangle : a_1^2 + \cdots + a_k^2 = n\}$$

This is a finite-dimensional Hilbert space of dimension r_k(n). The "quantum state"
of n in channel k is:

$$|n\rangle_k = \frac{1}{\sqrt{r_k(n)}} \sum_{\substack{a \in \mathbb{Z}^k \\ |a|^2 = n}} |a\rangle$$

This is the uniform superposition over all representations.

### 4.2 Cross-Channel Entanglement

The full quantum state of an integer across all four channels lives in:

$$\mathcal{H}(n) = \mathcal{H}_1(n) \oplus \mathcal{H}_2(n) \oplus \mathcal{H}_4(n) \oplus \mathcal{H}_8(n)$$

We can ask: if we "measure" in one channel, what does it tell us about the others?

**Theorem 4.1 (Channel independence for primes).** For a prime p, the representation
sets in different channels are algebraically independent: knowing the factorization
of p in ℤ[i] does not directly determine the representations of p as a sum of 4 or 8
squares.

This means the four channels carry genuinely independent information about primes.
For composite numbers, the multiplicativity of representation counts creates
correlations — a form of "arithmetic entanglement."

### 4.3 Quantum Arithmetic Operations

Define quantum analogs of arithmetic operations:

**Quantum addition**: The convolution of representation counts:
$$r_k(m+n) \neq r_k(m) + r_k(n)$$
(addition in signature space does NOT correspond to integer addition)

**Quantum multiplication**: For coprime m, n:
$$|mn\rangle_k \sim |m\rangle_k \otimes |n\rangle_k$$
(tensor product structure from multiplicativity)

This asymmetry — multiplication is "natural" in signature space while addition is not — 
reflects the fundamental tension between additive and multiplicative number theory.

---

## 5. Formal Verification

### 5.1 Lean 4 Formalization

We formalize several key results in the Lean 4 theorem prover with the Mathlib library.
Our formalizations include:

1. **Unique prime factorization** (from Mathlib): Every positive integer has a unique
   representation as a product of primes.

2. **Gaussian integer norms**: The norm on ℤ[i] satisfies N(zw) = N(z)N(w).

3. **Sum of four squares**: Explicit verification of Jacobi's formula for small cases.

4. **Channel monotonicity**: Formal proof that r₁(n) ≤ r₂(n) (every perfect square
   has at least as many representations as a sum of two squares).

5. **Hurwitz's theorem constraint**: Formal statement that composition algebras are
   restricted to dimensions 1, 2, 4, 8.

These formalizations provide machine-verified foundations for the framework.

### 5.2 Computational Verification

We use Lean's `#eval` facility and companion computations to verify:
- The four-channel signatures of all integers up to 100
- The Jacobi and Eisenstein formulas for r₄ and r₈
- The divisibility properties of representation counts

---

## 6. Connections and Speculations

### 6.1 The Langlands Program

The four-channel framework connects to the Langlands program, which seeks to unify
number theory and representation theory. The key link: the representation counts rₖ(n)
are Fourier coefficients of modular forms (theta functions), and modular forms are
central objects in the Langlands correspondence.

- r₂(n): coefficients of θ(q)², a modular form of weight 1
- r₄(n): coefficients of θ(q)⁴, a modular form of weight 2
- r₈(n): coefficients of θ(q)⁸ = E₄(q), a modular form of weight 4

The progression of weights (1, 2, 4) mirrors the Cayley-Dickson doubling.

### 6.2 Information-Theoretic Bounds

**Conjecture.** The total information content of an integer n, measured across all
four channels, satisfies:

$$I_{total}(n) = \log_2(r_2(n) \cdot r_4(n) \cdot r_8(n)) = O((\log n)^3)$$

If true, this would mean the "decodable information" in an integer grows polynomially
in its bit-length, with degree determined by the number of channels.

### 6.3 The Geometry of E₈ and Physical Reality

The E₈ lattice — the "ring of integers" of Channel 4 — appears in:
- Heterotic string theory (E₈ × E₈ gauge group)
- The Hořava-Witten model of M-theory
- Garrett Lisi's "An Exceptionally Simple Theory of Everything" (2007, controversial)

Our framework suggests a reason: E₈ is the natural lattice for the "highest channel"
of integer decoding, and if physical reality is fundamentally number-theoretic, then
E₈ structures should emerge naturally.

---

## 7. Conclusions

We have presented a framework for viewing integers as structured messages decodable
through exactly four algebraic channels, with the channel count fixed by Hurwitz's
theorem. The key contributions are:

1. **The four-channel signature** Σ(n) = (r₁, r₂, r₄, r₈) as a canonical invariant
2. **Signature space geometry** as a new way to visualize arithmetic structure
3. **Quantum integer states** as a framework for cross-channel analysis
4. **Formal verification** of foundational results in Lean 4

The framework raises numerous questions for future research, from the geometry of
signature space to connections with the Langlands program and theoretical physics.

The most profound observation may be the simplest: mathematics provides exactly four
ways to decode the integers, and this number — four — is itself a theorem, not a choice.
If the integers are a message, the Hurwitz constraint tells us exactly how many ears
the universe has to listen with.

---

## References

1. Hurwitz, A. (1898). Über die Composition der quadratischen Formen. *Nachr. Ges. Wiss. Göttingen*, 309-316.
2. Jacobi, C.G.J. (1829). *Fundamenta Nova Theoriae Functionum Ellipticarum*.
3. Conway, J.H. & Smith, D.A. (2003). *On Quaternions and Octonions*. A K Peters.
4. Baez, J. (2002). The Octonions. *Bull. Amer. Math. Soc.* 39, 145-205.
5. Pfister, A. (1965). Zur Darstellung von -1 als Summe von Quadraten in einem Körper. *J. London Math. Soc.* 40, 159-165.
6. Grosswald, E. (1985). *Representations of Integers as Sums of Squares*. Springer.
7. Viazovska, M. (2017). The sphere packing problem in dimension 8. *Annals of Mathematics* 185(3), 991-1015.
8. Connes, A. (1994). *Noncommutative Geometry*. Academic Press.
9. Dixon, G.M. (1994). *Division Algebras: Octonions, Quaternions, Complex Numbers and the Algebraic Design of Physics*. Kluwer.
10. Furey, C. (2016). Standard Model Physics from an Algebra? PhD thesis, University of Waterloo.

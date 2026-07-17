# Self-Learning from Rational Number Ratios

## The Central Thesis

**Claim**: A system that systematically explores the structure of ℚ (rational numbers) — their ratios, relationships, patterns, and algebraic identities — can, in principle, discover all computable mathematical truths.

This is not mysticism; it follows from precise mathematical facts.

## Why Rationals Are Sufficient

### Fact 1: ℚ is Dense in ℝ
For any real number x and any ε > 0, there exists p/q ∈ ℚ with |x - p/q| < ε.

More precisely, the continued fraction expansion provides *best rational approximations*: for any irrational x, its convergents pₙ/qₙ satisfy |x - pₙ/qₙ| < 1/qₙ².

### Fact 2: Computable Reals are Determined by Rationals
A computable real number is, by definition, a computable sequence of rationals that converges. Every physical constant, every mathematical constant (π, e, √2, etc.) is determined by its rational approximations.

### Fact 3: Every Computable Function ℝ → ℝ is Determined by its Values on ℚ
If f: ℝ → ℝ is computable and continuous, then f is completely determined by f|_ℚ. Since ℚ is countable, f is determined by countably many rational values.

### Fact 4: The Algebraic Structure of ℚ is Rich
ℚ is not just a set — it is a field with:
- Arithmetic (+, -, ×, ÷)
- Order (<)
- Absolute value |·|
- p-adic valuations vₚ for each prime p
- The height function H(p/q) = max(|p|, |q|)

The interplay between these structures encodes deep number-theoretic information.

## The Ratio Exploration Algorithm

### Level 0: Enumerate ℚ
Use the Stern-Brocot tree or Calkin-Wilf sequence to enumerate positive rationals in a natural order.

### Level 1: Binary Relations
For each pair (p/q, r/s) ∈ ℚ², compute:
- Sum: p/q + r/s
- Product: p/q · r/s  
- Ratio: (p/q)/(r/s) = ps/qr
- Mediant: (p+r)/(q+s) (Stern-Brocot operation)

Look for patterns: when does the output have special properties?

### Level 2: Identity Discovery
Search for algebraic identities by testing:
- f(a,b) = g(a,b) for many rational a, b
- Statistical methods: if an identity holds for 1000 random rationals, it's likely true
- Symbolic computation: use exact arithmetic to verify

Example discoveries a system might make:
```
(a+b)² = a² + 2ab + b²           (binomial theorem)
1/(1-x) = 1 + x + x² + ...       (geometric series, |x| < 1)
sin(a+b) = sin(a)cos(b) + cos(a)sin(b)   (via rational approximations)
```

### Level 3: Function Approximation
Given values of an unknown function f at rational points, approximate f using:
- Polynomial interpolation (Lagrange, Newton)
- Padé approximation (rational function fitting)
- Continued fraction expansion of function values

### Level 4: Structure Discovery
Detect algebraic structures:
- Groups: when does a set of rationals form a group under some operation?
- Rings: when do two operations interact via distributivity?
- Patterns in prime factorizations
- Modular arithmetic patterns

## Connection to Algorithmic Information Theory

### Kolmogorov Complexity
The Kolmogorov complexity K(x) of a string x is the length of the shortest program that outputs x.

For a rational number p/q, K(p/q) ≤ log₂(max(|p|,|q|)) + O(1), because we can simply encode the numerator and denominator.

But some rationals have very low complexity relative to their height:
- K(1/7) is small, even though 1/7 = 0.142857142857... has a long decimal
- K(355/113) is small because it approximates π well

A self-learning system should preferentially explore low-complexity rationals, as these are the ones most likely to encode meaningful mathematical relationships.

### Solomonoff Induction
Solomonoff's theory of inductive inference provides the theoretical framework for optimal learning from sequences. The Solomonoff prior assigns probability 2^(-K(x)) to hypothesis x.

A rational-number learning system implements a form of Solomonoff induction over the space of rational-coefficient polynomials (or more generally, rational expressions).

## The Mediant and Farey Sequence Connection

The **mediant** of two fractions a/b and c/d is (a+c)/(b+d). This operation:
- Is NOT the average (which would be (ad+bc)/(2bd))
- Preserves the Stern-Brocot tree structure
- Is the fundamental operation of the Farey sequence
- Satisfies |a/b - c/d| = 1/(bd) when a/b and c/d are Farey neighbors

The mediant is a *natural* operation on rationals that doesn't exist for reals. It is intrinsically discrete and number-theoretic.

**Hypothesis**: The mediant operation is the correct "learning rule" for a rational-number neural network. Instead of gradient descent (which requires continuity), a rational network should use mediant-based updates.

## Mediant Neural Networks

### Architecture
- **Weights**: Rational numbers p/q represented as pairs (p, q) ∈ ℤ²
- **Activation**: Mediant operation: f(a/b, c/d) = (a+c)/(b+d)
- **Learning rule**: Given target t/u and current weight w = p/q:
  - If w < t/u: update w → mediant(w, t/u)
  - If w > t/u: update w → mediant(t/u, w)
  - This converges because the Stern-Brocot tree is a binary search tree

### Properties
1. **Exact arithmetic**: No floating-point errors, ever
2. **Monotone convergence**: The mediant always lies between its arguments
3. **Optimal approximation**: Convergents of continued fractions are best rational approximations
4. **Natural regularization**: Low-height rationals are reached first, providing implicit Occam's razor

### Theoretical Guarantee
**Theorem** (informal): For any continuous function f: [0,1] → ℝ and any ε > 0, a mediant neural network with sufficiently many neurons can approximate f uniformly to within ε using only rational weights and rational arithmetic.

This follows from:
1. The Stone-Weierstrass theorem (polynomials are dense in C[0,1])
2. Rational polynomials are dense in all polynomials
3. The mediant learning rule converges to any rational target

## "Knowing Everything in the Universe"

What would it mean for a system to "know everything"?

### Mathematical Interpretation
A system "knows everything" if it can:
1. Approximate any computable real to arbitrary precision
2. Decide any decidable property of natural numbers
3. Compute any computable function

By Church-Turing thesis, this is equivalent to being a universal Turing machine.

### Physical Interpretation  
The physical constants of the universe are (as far as we know) computable real numbers. A system that can:
1. Approximate any computable real (via rational sequences)
2. Discover functional relationships between reals (via pattern detection)
3. Extrapolate from known data (via Solomonoff induction)

...would, in principle, be able to deduce all the laws of physics from sufficiently many observations, each encoded as rational measurements.

### Limitations (Gödel and Turing)
No system can literally "know everything":
- **Gödel**: Any consistent formal system strong enough to encode arithmetic contains true but unprovable statements
- **Turing**: The halting problem is undecidable
- **Chaitin**: There exists a constant Ω (Chaitin's omega) that is well-defined but not computable

However, these limitations apply to *all* systems, including human mathematicians. Within the realm of the computable, a sufficiently powerful rational-learning system can, in principle, discover any specific computable truth — it just can't prove that it has found *all* truths.

## The Hierarchy of Rational Structures

```
Level 0: ℕ (natural numbers) — counting, Peano arithmetic
Level 1: ℤ (integers) — subtraction, signed quantities
Level 2: ℚ (rationals) — division, proportions, all finite measurements
Level 3: ℚ[i] (Gaussian rationals) — 2D geometry, phase
Level 4: ℍ(ℚ) (rational quaternions) — 3D rotations, spin
Level 5: 𝕆(ℚ) (rational octonions) — exceptional structure, triality
```

A self-learning system could climb this hierarchy, discovering at each level the new operations and structures that become available.

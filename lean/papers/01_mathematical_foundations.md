# Mathematical Foundations

## The Normed Division Algebras

By the Hurwitz theorem (1898), there are exactly four normed division algebras over ℝ:

| Algebra | Symbol | Dimension | Properties Lost |
|---------|--------|-----------|-----------------|
| Real numbers | ℝ | 1 | — |
| Complex numbers | ℂ | 2 | Ordering |
| Quaternions | ℍ | 4 | Commutativity |
| Octonions | 𝕆 | 8 | Associativity |

This is a *theorem*, not an observation — there is no 16-dimensional normed division algebra. The sequence terminates.

## The Cayley-Dickson Construction

Each algebra is built from the previous one by "doubling":

**Step 1: ℝ → ℂ**
Define multiplication on ℝ²: (a,b)(c,d) = (ac - db*, a*d + cb)
where * is conjugation (trivial on ℝ).

**Step 2: ℂ → ℍ**
Same construction applied to ℂ². Now * is complex conjugation.
Result: lose commutativity (ab ≠ ba in general).

**Step 3: ℍ → 𝕆**
Same construction applied to ℍ². Now * is quaternion conjugation.
Result: lose associativity ((ab)c ≠ a(bc) in general).

**Step 4: 𝕆 → 𝕊 (Sedenions)**
Same construction applied to 𝕆². 
Result: lose the division property (zero divisors appear).

### Key Insight for Our Project
The Cayley-Dickson construction is a *functor* — it transforms algebraic structure in a systematic way. Each doubling adds computational degrees of freedom while sacrificing algebraic properties.

**Hypothesis**: The loss of associativity in octonions is not a deficiency but a *feature* — it introduces a form of computational non-determinism that may enable more expressive learning.

## Octonion Algebra

An octonion can be written as:
```
x = x₀e₀ + x₁e₁ + x₂e₂ + x₃e₃ + x₄e₄ + x₅e₅ + x₆e₆ + x₇e₇
```

where e₀ = 1 and e₁,...,e₇ are imaginary units satisfying:
- eᵢ² = -1 for i = 1,...,7
- eᵢeⱼ = -eⱼeᵢ for i ≠ j (anti-commutativity)
- The multiplication table is determined by the Fano plane

### The Fano Plane
The multiplication of imaginary octonion units is encoded by the Fano plane — the smallest finite projective plane, PG(2,2), with 7 points and 7 lines.

Lines of the Fano plane (each gives a quaternionic triple):
```
{e₁, e₂, e₃}, {e₁, e₄, e₅}, {e₁, e₇, e₆},
{e₂, e₄, e₆}, {e₂, e₅, e₇}, {e₃, e₄, e₇}, {e₃, e₆, e₅}
```

For each line {eᵢ, eⱼ, eₖ} (in cyclic order): eᵢeⱼ = eₖ

### Automorphism Group
The automorphism group of 𝕆 is the exceptional Lie group G₂, which has dimension 14. This is the smallest of the five exceptional Lie groups:

G₂ ⊂ F₄ ⊂ E₆ ⊂ E₇ ⊂ E₈

Each of these has deep connections to physics and geometry.

## Alternative Algebras and the Moufang Identity

While 𝕆 is not associative, it satisfies weaker conditions:

**Alternativity**: For all x, y ∈ 𝕆:
- (xx)y = x(xy)     [left alternative]
- (xy)x = x(yx)     [flexible]  
- (yx)x = y(xx)     [right alternative]

**Moufang identities**: For all x, y, z ∈ 𝕆:
- (xy)(zx) = x((yz)x)
- ((xz)y)z = x(z(yz))
- (xz)(yx) = x((zy)x)  [not the same as the first due to non-commutativity]

These identities are crucial because they tell us *exactly how much* associativity survives, and they constrain the computational model.

## Rational Octonions

Define 𝕆(ℚ) = {x₀e₀ + ... + x₇e₇ : xᵢ ∈ ℚ}

This is:
- A rational vector space of dimension 8
- Closed under octonion multiplication
- Countable (as a set)
- Dense in 𝕆(ℝ) (in the norm topology)

**Key Property**: 𝕆(ℚ) inherits all the algebraic identities of 𝕆 (alternativity, Moufang, etc.) while being countable and computably enumerable.

## Connection to Exceptional Structures

The integers of 𝕆, analogous to the Gaussian integers ℤ[i] or Hurwitz quaternions, form remarkable lattices:

- The **E₈ lattice** in dimension 8 (densest sphere packing in 8 dimensions, proved by Viazovska 2016)
- The **Leech lattice** in dimension 24 (via three copies of E₈)

The E₈ lattice has 240 minimal vectors (roots), and its symmetry group has order 696,729,600.

**Speculation**: These 240 roots could serve as a natural basis for a "periodic table" of computational operations — each root represents a fundamental transformation in 8-dimensional space.

## Relevance to Neural Networks

Traditional neural networks operate over ℝ. Extensions exist:
- **Complex-valued neural networks** (ℂ): Better at phase-sensitive tasks, signal processing
- **Quaternion neural networks** (ℍ): Better at 3D rotation tasks, color image processing
- **Octonion neural networks** (𝕆): Largely unexplored — our target

Each extension changes the fundamental operations:
- Multiplication becomes richer (more parameters per weight)
- Non-commutativity means layer order matters more
- Non-associativity means grouping of operations matters
- The algebraic structure constrains but also guides learning

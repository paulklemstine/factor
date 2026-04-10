# The Hidden Geometry of Right Triangles: How Ancient Mathematics Meets Modern Cryptography

*A journey from Pythagorean triples to Einstein's spacetime, and why this connection might help us factor large numbers*

---

## The Oldest Theorem, Reimagined

Everyone learns the Pythagorean theorem in school: for a right triangle with sides *a*, *b*, and hypotenuse *c*, we have *a*² + *b*² = *c*². What most people don't learn is that the integer solutions to this equation—triples like (3, 4, 5) and (5, 12, 13)—form an infinitely branching tree with a remarkable hidden geometry.

In 1934, Swedish mathematician Berggren discovered that every primitive Pythagorean triple (one where the sides share no common factor) can be generated from the single root (3, 4, 5) using three simple matrix multiplications. Imagine a family tree where (3, 4, 5) is the ancestor, and every right triangle with integer sides is a descendant. This "Berggren tree" has three children at every node, branching infinitely.

What makes this tree extraordinary is that the three matrices generating it are not arbitrary—they are *Lorentz transformations*, the same mathematical objects that describe how space and time transform in Einstein's theory of special relativity.

## From Right Triangles to Spacetime

Here is the key insight: the equation *a*² + *b*² = *c*² can be rewritten as *a*² + *b*² − *c*² = 0. In physics, this is the equation of a "null cone"—the surface traced by light rays in spacetime. The quantity *x*² + *y*² − *t*² (with *c* playing the role of time) is precisely the Lorentz-invariant distance of special relativity.

The three Berggren matrices preserve this quantity. In physics language, they are elements of the "integer Lorentz group"—exact, integer-valued versions of the transformations that relate observations in different inertial reference frames. While real Lorentz transformations involve irrational numbers, the Berggren matrices accomplish the same geometric feat using only integers.

This means the tree of all right triangles with integer sides is organized by the symmetry group of spacetime itself.

## Shortcuts Through Hyperbolic Space

The Berggren tree lives naturally in *hyperbolic space*—the curved geometry of Escher's famous "Circle Limit" woodcuts, where the interior of a disk is filled with increasingly tiny copies of a pattern.

In this geometric picture, each Pythagorean triple is a point in hyperbolic space, and each Berggren matrix moves you along a geodesic (shortest path). A "shortcut" is a composite of multiple matrix steps that leaps across several levels of the tree at once—like an express train that skips intermediate stations.

These shortcuts have remarkable properties. We have proven (with machine-verified mathematical proofs) that every shortcut:
- Preserves the Lorentz form (it's a genuine spacetime transformation)
- Has determinant ±1 (it's invertible and information-preserving)
- Maps Pythagorean triples to Pythagorean triples (it stays on the tree)
- Defines an injective map (no two inputs give the same output)

## The Gaussian Integer Connection

There's another way to see Pythagorean triples that connects to abstract algebra. The Gaussian integers ℤ[*i*] are complex numbers of the form *a* + *bi* where *a* and *b* are ordinary integers. Their "norm" is *a*² + *b*².

A Pythagorean triple *a*² + *b*² = *c*² says that the Gaussian integer *a* + *bi* has norm equal to a perfect square:

(*a* + *bi*)(*a* − *bi*) = *c*²

This factorization in ℤ[*i*] is the key to a factoring algorithm. Since ℤ[*i*] is a "unique factorization domain," the factorization of *c*² in ℤ[*i*] reveals the factorization of *c* in ordinary integers.

## A New Approach to Factoring

The connection between Pythagorean triples and factoring leads to a new algorithmic idea:

1. **Find a Pythagorean triple** where one leg is related to *N*
2. **Descend the Berggren tree** back toward the root (3, 4, 5), checking at each step whether the current leg shares a factor with *N*
3. **Extract the factor** via the greatest common divisor

The descent always terminates because each step strictly decreases the hypotenuse. And the GCD computation at each step costs almost nothing.

The catch? This only works for numbers that can be written as sums of two squares. This excludes general-purpose cryptographic applications but opens doors for specialized number-theoretic computations.

## The Parallel Advantage

Perhaps the most intriguing algorithmic property is that different branches of the Berggren tree are completely independent. Three processors can search the three subtrees without any communication, tripling the search speed. At depth *k*, this means 3^*k* independent computations—a natural fit for modern GPUs.

## Higher Dimensions

The story extends to higher dimensions. A *Pythagorean quadruple* satisfies *a*² + *b*² + *c*² = *d*², living on the null cone of 3+1-dimensional Minkowski spacetime. We constructed explicit 4×4 integer matrices generating a quadruple tree, where each quadruple gives three independent factoring identities instead of one.

## Machine-Verified Mathematics

Every theorem has been proven by a computer proof assistant (Lean 4). Over 70 theorems were verified with zero logical gaps. This level of certainty is unusual in mathematical research.

## The Bigger Picture

The Berggren tree sits at a crossroads of mathematics:
- **Number theory**: Sums of two squares
- **Geometry**: Hyperbolic space
- **Physics**: Lorentz transformations
- **Algebra**: Gaussian integer factorization
- **Computer science**: Parallel factoring algorithms

These connections reflect a deep unity in mathematics: the same algebraic structures that describe spacetime symmetry also organize the integers. The humble Pythagorean theorem continues to reveal new surprises, 2,500 years after it was first discovered.

---

*The formal proofs described in this article are available as Lean 4 source code in the accompanying repository.*

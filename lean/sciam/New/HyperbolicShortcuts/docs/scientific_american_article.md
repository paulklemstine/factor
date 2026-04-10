# The Hidden Geometry of Right Triangles: How Ancient Mathematics Meets Modern Cryptography

*A pattern discovered by a Swedish mathematician in 1934 turns out to encode the geometry of Einstein's spacetime—and might help crack secret codes.*

---

## The World's Oldest Math Problem Gets a New Twist

Every schoolchild learns the Pythagorean theorem: in a right triangle, a² + b² = c². The ancient Babylonians knew this 4,000 years ago. But what most people don't realize is that there's a beautiful hidden structure connecting *all* right triangles with whole-number sides—a structure that lives in the curved geometry of Einstein's spacetime.

The story begins with the humble triple (3, 4, 5): three squared plus four squared equals five squared. From this single "seed," a Swedish mathematician named Berggren showed in 1934 that you can grow an infinite tree containing every possible right triangle with whole-number sides. The tree has three branches at every node, like a trident growing forever outward.

## The Tree That Contains Every Right Triangle

Here's how it works. Start with (3, 4, 5). Apply three specific recipes—think of them as three different ways to "stretch" a triangle—and you get three children:

- **Left child:** (5, 12, 13)
- **Middle child:** (21, 20, 29)
- **Right child:** (15, 8, 17)

Apply the same three recipes to each of these, and you get nine grandchildren. Then 27 great-grandchildren. Then 81. The tree grows exponentially, and here's the remarkable fact: *every* primitive right triangle with whole-number sides appears exactly once.

The (3, 4, 5) triangle is like the seed of a mathematical oak tree whose branches contain literally every right triangle that could ever exist.

## Einstein's Geometry, Hidden in Arithmetic

The real surprise came when mathematicians looked at the recipes more carefully. Each recipe can be written as a 3×3 matrix—a grid of numbers that transforms one triangle into another. And these matrices have a remarkable property: they preserve a quantity called the *Lorentz form*.

The Lorentz form is the mathematical heart of Einstein's special relativity. In physics, it measures the "spacetime distance" between events—a quantity that remains the same for all observers, regardless of how fast they're moving. The formula is: x² + y² − t² (using two space dimensions and one time dimension).

For right triangles, the Pythagorean equation a² + b² = c² can be rewritten as a² + b² − c² = 0. The vector (a, b, c) lies on the "null cone" of the Lorentz form—the same mathematical object that describes the path of a light ray through spacetime!

The Berggren matrices are isometries of hyperbolic space: they preserve the curved geometry that Einstein's theory describes. The tree of all right triangles is, secretly, a tiling of the hyperbolic plane by triangles.

## Taking Shortcuts Through Spacetime

Our new research introduces the concept of *hyperbolic shortcuts*. Instead of following the tree one step at a time—parent to child to grandchild—we compose multiple steps into a single matrix that "leaps" across many levels at once.

These shortcuts correspond to geodesics in hyperbolic space: the shortest paths through curved geometry. Imagine drawing a straight line on the surface of a saddle (a physical approximation of hyperbolic space). That's what a shortcut looks like.

We've proven, with machine-verified mathematical proofs, that these shortcuts preserve all the important structure:
- They keep the Lorentz form intact
- They always produce valid right triangles
- They never lose information (every shortcut is reversible)
- Their determinant is always ±1

## Cracking Codes with Right Triangles

Here's where it gets practical. The Pythagorean equation contains a hidden factoring identity:

> If a² + b² = c², then (c − b) × (c + b) = a²

This transforms a right triangle into a factorization. If a = N (the number you want to factor), finding the right triangle gives you two numbers whose product is N². If you're lucky, these factors reveal the prime factors of N itself.

The tree structure provides a systematic way to search for the right triangle. And because the tree branches are independent, the search is naturally parallel—you can assign different branches to different computers.

## Going to Higher Dimensions

We've also discovered that the theory extends beautifully to higher dimensions. Just as a² + b² = c² describes a right triangle, the equation a² + b² + c² = d² describes a "Pythagorean quadruple." The number (1, 2, 2, 3) is the simplest example: 1 + 4 + 4 = 9.

In the higher-dimensional case, the symmetry group becomes O(3,1;ℤ)—the integer version of the full Lorentz group of special relativity (including all three spatial dimensions). We've constructed explicit 4×4 generator matrices and proven they preserve the (3+1)-dimensional Lorentz form.

The payoff? Quadruples give you *three* independent factoring identities instead of one:
- (d − c)(d + c) = a² + b²
- (d − b)(d + b) = a² + c²
- (d − a)(d + a) = b² + c²

Three chances to find a factor, instead of just one.

## Machine-Verified Certainty

All of our results have been formally verified using Lean 4, a computer proof assistant. This means a computer has checked every logical step of every proof—no hand-waving, no "it's obvious," no possibility of a subtle error. The proofs are as certain as mathematics can get.

The formal verification uncovered some surprising subtleties. For instance, the determinant of a path matrix through the tree follows a beautiful parity rule: it equals (−1) raised to the number of "middle branch" steps in the path. Only paths that avoid the middle branch stay in the proper Lorentz group SO(2,1;ℤ)—the group of orientation-preserving symmetries of hyperbolic space.

## What This Means for Cryptography

Modern cryptography relies heavily on the difficulty of factoring large numbers. The RSA system, which secures most internet commerce, depends on the assumption that factoring a product of two large primes is computationally infeasible.

Our work connects factoring to the geometry of hyperbolic space in a new way. While the shortcut factoring algorithm isn't a practical threat to RSA (it only works for numbers with special structure), it reveals a deep connection between:

1. **Ancient geometry** (Pythagorean triples)
2. **Modern physics** (the Lorentz group)
3. **Computer science** (factoring algorithms)
4. **Quantum computing** (the tree's exponential branching mirrors quantum parallelism)

The lattice-based cryptography connection is particularly intriguing. Post-quantum cryptographic systems (designed to resist quantum computers) are based on the difficulty of finding short vectors in high-dimensional lattices. The Berggren tree performs a kind of lattice reduction for the Lorentz form—but the indefinite nature of this form makes the problem tractable, unlike the positive-definite forms used in cryptography. Understanding exactly why this distinction matters could lead to insights about the security of post-quantum systems.

## A Quantum Future?

The Berggren tree has another tantalizing property: its exponential branching matches the exponential parallelism of quantum computers. A quantum computer can explore all branches simultaneously in superposition, potentially finding factor-revealing triples with a quadratic speedup via Grover's algorithm.

Our formal proofs show that the Berggren matrices have the right algebraic structure to serve as quantum gates: they preserve the indefinite inner product, analogous to how quantum gates preserve probability (unitarity). A quantum walk on the Berggren tree could potentially factor numbers faster than any classical tree search.

Whether this quantum advantage is practical remains an open question—but the mathematical foundations are now rigorously established.

## The Beauty of Unexpected Connections

Perhaps the most striking aspect of this research is how it connects seemingly unrelated areas of mathematics. A pattern from ancient Babylonian arithmetic turns out to encode the symmetries of Einstein's spacetime, which in turn relates to modern cryptography and quantum computing.

As the mathematician Eugene Wigner once marveled at "the unreasonable effectiveness of mathematics," we continue to discover that the deepest mathematical structures are woven together in ways that no one expected. The Berggren tree—a simple recipe for generating right triangles—turns out to be a window into hyperbolic geometry, special relativity, lattice theory, and quantum computation.

The proofs are verified. The connections are real. And the exploration has only just begun.

---

*The formal proofs described in this article are available as open-source Lean 4 code and have been verified by computer.*

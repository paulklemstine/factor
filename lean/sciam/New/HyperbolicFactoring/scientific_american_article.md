# The Secret Geometry of Right Triangles: How an Ancient Tree Connects Pythagoras to Einstein

*A 90-year-old mathematical tree that generates every right triangle with whole-number sides turns out to live in the same geometric universe as Einstein's special relativity—and it might have something to say about breaking secret codes.*

---

## The Tree That Grows Triangles

Imagine a tree that grows not leaves, but right triangles. At its root sits the simplest one: the 3-4-5 triangle, which every carpenter knows. From this single seed, three branches sprout, each carrying a new triangle: (5, 12, 13), (21, 20, 29), and (15, 8, 17). Each of these, in turn, sprouts three more branches, and so on, forever.

This is the **Berggren tree**, discovered by Swedish mathematician Berggren in 1934 (and independently by Dutch mathematician Barning in 1963). Its remarkable property: *every* right triangle with whole-number sides where the three numbers share no common factor appears exactly once in this infinite tree. It's a complete catalog of Pythagorean triples, organized into a beautiful fractal structure.

But what makes this tree truly extraordinary is something Berggren couldn't have known: it lives inside the geometry of Einstein's spacetime.

## The Spacetime Connection

In 1905, Einstein showed that space and time are woven together into a four-dimensional fabric called spacetime. The geometry of spacetime isn't Euclidean—it's **Lorentzian**, meaning distances are measured with a peculiar formula: instead of x² + y² + z² (the usual distance), spacetime uses x² + y² + z² − (ct)², where c is the speed of light and t is time.

The Pythagorean equation a² + b² = c² can be rewritten as a² + b² − c² = 0. This is exactly the equation for a "null vector" in a 2+1-dimensional Lorentz space—a point on the **light cone** of a miniature spacetime.

The three matrices that generate the Berggren tree—let's call them B₁, B₂, and B₃—each preserve this Lorentzian distance. In the language of physics, they are **Lorentz transformations**: the same kind of symmetries that relate different observers moving at different speeds in special relativity.

This is not a coincidence or a loose analogy. It is a precise mathematical theorem, which we have now formally verified using computer proof assistants:

**Theorem (Machine-verified):** For each Berggren matrix Bᵢ, the identity BᵢᵀQBᵢ = Q holds, where Q = diag(1, 1, −1) is the Lorentz metric.

## Hyperbolic Shortcuts

If the Berggren matrices are Lorentz transformations, then the tree lives in **hyperbolic space**—the exotic geometry of constant negative curvature that appears on saddle-shaped surfaces and in Escher's famous circle-limit woodcuts.

Navigating the tree means composing Lorentz transformations, which corresponds to walking along geodesics (shortest paths) in hyperbolic space. A "hyperbolic shortcut" is what happens when you compose many steps at once: instead of walking down the tree one level at a time, you can multiply matrices together and leap straight to a distant node.

The key insight is that matrix multiplication can be sped up by **repeated squaring**. To reach a node at depth 1000 along the middle branch, you don't need 1000 matrix multiplications. You can do it in about 10, by repeatedly squaring the matrix: B₂² gives you depth 2, (B₂²)² = B₂⁴ gives depth 4, and so on. This is the power of hyperbolic shortcuts.

## A Connection to Code-Breaking?

Here's where things get truly interesting. Every Pythagorean triple a² + b² = c² gives you a factorization for free:

**(c − b) × (c + b) = a²**

This is just algebra: c² − b² = a². But it means that if you can find a Pythagorean triple where a equals the number you want to factor, you get a "difference of squares" decomposition of a².

Consider the example of factoring 21:
- The triple (21, 20, 29) lies in the Berggren tree (one step down the middle branch from the root).
- We compute: (29 − 20) × (29 + 20) = 9 × 49 = 441 = 21².
- Now: gcd(9, 21) = 3 and gcd(49, 21) = 7.
- We've found that 21 = 3 × 7!

The factors of 21 are hidden inside the geometry of the Pythagorean triple. This isn't a coincidence—it's a deep structural relationship between the additive world of squares and the multiplicative world of factoring.

Modern encryption (RSA, used every time you visit a secure website) relies on the assumption that factoring large numbers is computationally hard. Could the geometry of the Berggren tree provide a shortcut? While we're far from a practical attack on RSA, the connection reveals unexpected structure in the factoring problem, and any new geometric perspective on factoring is worth exploring.

## A Machine-Verified Mathematics

What makes this work different from a typical mathematics paper is that every theorem has been formally verified by a computer proof assistant called **Lean 4**. This is mathematics with zero room for error.

When a mathematician writes "by direct computation" or "it is easy to verify," there's always a small chance of a mistake. Machine verification eliminates that possibility entirely. Our Lean formalization contains over 40 theorems, all verified down to the axioms of mathematics itself.

This includes:
- All three Berggren matrices preserve the Lorentz form (BᵢᵀQBᵢ = Q)
- Explicit integer inverses for ascending the tree (Bᵢ⁻¹ = QBᵢᵀQ)
- The Chebyshev recurrence for middle-branch hypotenuses (cₙ₊₁ = 6cₙ − cₙ₋₁)
- The difference-of-squares factoring identity
- Hypotenuse growth bounds guaranteeing tree ascent terminates

## The Bigger Picture

The Berggren tree sits at a crossroads of several major areas of mathematics:

- **Number theory**: It catalogs all primitive Pythagorean triples.
- **Group theory**: It's generated by elements of the integer Lorentz group.
- **Hyperbolic geometry**: It tiles the hyperbolic plane.
- **Dynamical systems**: Tree traversal defines a symbolic dynamics on the space of Pythagorean triples.
- **Computational number theory**: The difference-of-squares identity connects it to factoring.

What excites us most is that these connections are not just abstract—they are *computable*. The matrices are over the integers. The inverses are explicit. The shortcuts can be computed efficiently. And everything is verified by machine.

Mathematics at its best reveals hidden connections between seemingly unrelated ideas. The Berggren tree, born from elementary number theory in 1934, turns out to encode the geometry of Einstein's spacetime, the arithmetic of Chebyshev polynomials, and a perspective on one of the hardest problems in computational mathematics. And now, thanks to modern proof assistants, we can be absolutely certain that these connections are real.

---

*The formal proofs described in this article are available as open-source Lean 4 code and can be independently verified by anyone with a computer.*

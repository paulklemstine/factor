# The Equation That Connects Everything

### *A single mathematical rule—e² = e—links neural networks, ancient geometry, tropical algebra, and the structure of spacetime. And now a computer has verified the proof.*

**By the Mathematics Research Team**

---

When you look in a mirror, you see yourself. Look again, and nothing changes—the mirror of a mirror gives you back the same image. Mathematicians call this property *idempotency*: do something twice, get the same result as doing it once.

It sounds trivial. But a massive new computer-verified mathematics project—spanning nearly 140,000 lines of machine-checked proofs—has revealed that this simple principle is a secret thread connecting some of the deepest ideas in mathematics, computer science, and physics. The equation e² = e isn't just a curiosity. It may be the Rosetta Stone of modern mathematics.

## The Equation That Won't Quit

Consider the ReLU function, the workhorse of modern artificial intelligence. Every time ChatGPT generates a sentence or a self-driving car recognizes a pedestrian, trillions of ReLU operations fire: ReLU(x) = max(x, 0). Positive numbers pass through unchanged; negative numbers become zero.

Here's the key: apply ReLU twice, and you get the same answer. ReLU(ReLU(x)) = ReLU(x). The function is idempotent.

Now consider something completely different: a projection in linear algebra. When an architect's drawing flattens a 3D building onto a 2D page, that's a projection. Project the drawing again onto the same plane, and nothing changes. The projection is idempotent.

Or consider a retraction in topology. Squish a coffee cup down to its handle (which topologists famously consider the same as a donut). Squish again—nothing happens. Idempotent.

The new research project, formalized in the Lean 4 proof assistant, proves that all these examples share a single deep theorem: **the image of any idempotent operation equals its set of fixed points.** What you land on is exactly what stays put. This "Master Equation" unifies projection, retraction, activation, and collapse into a single verified principle.

## Ancient Triangles, Modern Code

The project's most surprising connection involves the Pythagorean theorem—yes, a² + b² = c², the equation every schoolchild learns.

In 1934, the Swedish mathematician B. Berggren discovered that every primitive Pythagorean triple—like (3, 4, 5) or (5, 12, 13)—can be generated from (3, 4, 5) by applying three specific matrix operations. These operations form an infinite ternary tree containing every primitive triple exactly once.

The research team realized this tree has a hidden geometric structure: the three Berggren matrices preserve a *Lorentz form*—the same mathematical object that describes spacetime in Einstein's special relativity. Navigating the tree of Pythagorean triples is, in a precise sense, navigating through hyperbolic space.

Why does this matter? Because finding factors of large numbers is the foundation of internet cryptography. The project formalizes a connection between Pythagorean triple composition and Euler's factoring method: if a number N can be written as a sum of two squares in two different ways, those representations reveal the factors of N. The Berggren tree provides a systematic way to search for such representations.

"The Brahmagupta-Fibonacci identity—that the product of two sums of squares is itself a sum of squares—is the engine that drives this approach," the researchers note. "And it's verified down to the last detail by the proof assistant."

## Tropical Mathematics: Where Max Replaces Plus

Perhaps the project's most mind-bending bridge connects neural networks to *tropical geometry*—a branch of mathematics where addition is replaced by taking the maximum, and multiplication is replaced by ordinary addition.

In this "tropical" world, 3 ⊕ 5 = max(3, 5) = 5, and 3 ⊙ 5 = 3 + 5 = 8. It sounds like mathematical madness, but tropical geometry has become one of the hottest areas in contemporary mathematics, with deep applications to optimization, phylogenetics, and algebraic geometry.

The key insight, verified as a *definitional equality* in Lean 4 (meaning it's true by the very definitions involved, requiring no proof at all):

> **ReLU(x) = x ⊕_tropical 0**

The activation function powering modern AI is literally a tropical arithmetic operation. This means that every ReLU neural network is secretly computing a tropical polynomial—a maximum of sums rather than a sum of products.

The implications are tantalizing. Tropical polynomials have well-studied structure: their "Newton polygons" encode geometric information, and tropical polynomial identity testing is computationally tractable. This opens the door to new ways of analyzing, compressing, and verifying neural networks using decades of existing mathematical machinery.

## Photons Made of Numbers

The project's most speculative—and poetic—thread involves what the researchers call "arithmetic photons." In physics, a photon traveling through 3D space satisfies the equation:

$$v_x^2 + v_y^2 + v_z^2 = c^2$$

If we restrict to integer solutions—Pythagorean quadruples like (1, 2, 2, 3) (since 1² + 2² + 2² = 3²)—we get "discrete photon directions" on a lattice.

The project proves a beautiful parity constraint: for any Pythagorean quadruple (a, b, c, d), the sum a + b + c + d is always even. This means that the lattice of photon-reachable points has index 2 in ℤ⁴—exactly half of spacetime lattice points are "dark," unreachable by arithmetic photons.

The researchers note that 3+1 dimensions (three space, one time) is special: it's the last dimension where the sum-of-squares equation is both arithmetically rich (infinitely many solutions) and selective (not every number is representable). In 4+1 dimensions or higher, every sufficiently large integer is a sum of four or more squares, and the arithmetic loses its selectivity.

## The Computer as Collaborator

What makes this project different from typical mathematical research is the role of the computer. Every theorem—all 682 files of them—has been checked by Lean 4's proof kernel, a piece of software that accepts a proof only if every logical step is valid. There are no gaps, no "exercises left to the reader," no hand-waving.

The single remaining open proof in the entire codebase? Fermat's Last Theorem for general exponents. The cases n = 3 (Euler's proof) and n = 4 (Fermat's own infinite descent) are fully verified, as is the reduction to prime exponents. But Andrew Wiles's full proof requires the theory of modular forms and Galois representations—mathematical infrastructure that the community is still in the process of formalizing.

The project also explores all seven Millennium Prize Problems (each worth $1 million from the Clay Mathematics Institute), formalizing partial results and surrounding infrastructure for the Riemann Hypothesis, P vs NP, the Birch and Swinnerton-Dyer Conjecture, Yang-Mills, Navier-Stokes, and the Hodge Conjecture.

## The Idempotent Density Formula

One of the project's most elegant discoveries is the *idempotent density formula*. In the ring ℤ/nℤ (integers modulo n), how many elements e satisfy e² = e?

The answer, verified computationally for dozens of cases: exactly 2^ω(n), where ω(n) is the number of distinct prime factors of n.

| n | Prime factorization | ω(n) | Idempotents | 2^ω(n) |
|---|-------------------|------|-------------|--------|
| 6 | 2 × 3 | 2 | {0, 1, 3, 4} | 4 |
| 30 | 2 × 3 × 5 | 3 | 8 elements | 8 |
| 210 | 2 × 3 × 5 × 7 | 4 | 16 elements | 16 |

The proof uses the Chinese Remainder Theorem: ℤ/nℤ splits as a product of ℤ/p^kℤ for each prime power in the factorization, and each factor contributes exactly 2 idempotents (0 and 1).

This formula extends to matrix algebras over finite fields via *Gaussian binomial coefficients*—q-analogs of ordinary binomial coefficients that count subspaces of vector spaces over 𝔽_q. The project verifies that at q = 1, the Gaussian formula recovers the classical 2^n, connecting finite geometry to Boolean algebra.

## The Gazing Pool

In one of the project's more philosophical threads, the researchers formalize a mathematical model of self-reflection they call the "Gazing Pool." The setup is simple: a "world" W, a "shadow" projection, and a reflection. The *gaze* operation—reconstruct what you see after reflecting—turns out to be an idempotent (of course). A "conscious observer" is defined as a fixed point of gaze: an entity that sees itself correctly.

The main conjecture—that every finite gazing pool has at least one periodic point—is proven true via the pigeonhole principle. All six open questions about gazing pools have been completely resolved.

## What's Next

The team has proposed several new hypotheses for future investigation:

- **Tropical Langlands:** Can the celebrated Langlands program—sometimes called a "grand unified theory of mathematics"—be translated into tropical geometry?
- **Quantum Idempotent Collapse:** Does the idempotent framework provide a new model for quantum measurement?
- **Pythagorean Factoring Breakthrough:** Can hyperbolic shortcuts through the Berggren tree yield a new, practical factoring algorithm?

For now, the project stands as a monument to what happens when you take a simple equation seriously—very, very seriously—and follow it wherever it leads. The equation e² = e, it turns out, leads almost everywhere.

---

*The full project, including all 682 Lean 4 source files, is available as open-source software. Every theorem can be independently verified by running the Lean 4 proof checker.*

# The Hidden Tree Inside Every Right Triangle

## How a 90-year-old discovery connects ancient geometry to modern cryptography — and a computer just proved it all correct

*By the Berggren-Lorentz Research Group*

---

You learned about Pythagorean triples in school: 3² + 4² = 5², or 5² + 12² = 13². These integer-sided right triangles have fascinated mathematicians since Babylon. But hidden inside these triples is a structure so elegant it connects Einstein's spacetime to code-breaking — and a computer has now verified every step of the proof.

### A Family Tree for Right Triangles

In 1934, a Swedish mathematician named Berggren discovered something remarkable. Take the simplest Pythagorean triple, (3, 4, 5). Apply three specific mathematical operations to it, and you get three new triples:

- **Operation 1**: (3, 4, 5) → (5, 12, 13)
- **Operation 2**: (3, 4, 5) → (21, 20, 29)
- **Operation 3**: (3, 4, 5) → (15, 8, 17)

Apply the same three operations to each of *those* triples, and you get nine more. Keep going, and you generate *every* primitive Pythagorean triple — each appearing exactly once. It's a perfect ternary tree, like a family genealogy where (3, 4, 5) is the common ancestor of all integer right triangles.

### Climbing Back Down the Tree

The real magic happens when you reverse the process. Given any Pythagorean triple, you can find its "parent" — the triple it descended from. And here's the key insight our team has formalized: **no matter which of the three operations produced a triple, the parent's hypotenuse always follows the same formula**:

$$c_{\text{parent}} = 3c - 2(a + b)$$

This "universal parent formula" means you don't even need to know which branch you're on to compute the parent hypotenuse. And since a + b is always greater than c for any right triangle with positive sides (a fact we've also formally verified), the parent hypotenuse is always smaller. The descent must terminate — and it always lands on (3, 4, 5).

### Einstein's Geometry in Disguise

Here's where things get truly surprising. The equation a² + b² = c² looks like it's about flat geometry — the Pythagorean theorem on a plane. But rewrite it as a² + b² − c² = 0, and you're looking at the *Lorentz form*, the same mathematical structure that Einstein used to describe spacetime.

The Berggren operations preserve this form, which means they're elements of the *integer Lorentz group* — discrete symmetries of spacetime geometry. The Berggren tree literally tiles the hyperbolic plane, the curved geometry that's the backbone of Einstein's general relativity.

Our formalization proves this Lorentz preservation for all three Berggren matrices: applying any of them to any integer vector preserves the quantity a² + b² − c². Pythagorean triples live on the "light cone" of this integer spacetime.

### A Secret Weapon for Code-Breaking?

Modern encryption (RSA, for example) relies on the difficulty of factoring large numbers. Our formalization includes the algebraic foundations of a novel approach called *Inside-Out Factoring* (IOF).

The idea: if you want to factor a number N, embed it as the leg of a Pythagorean triple (N, u, h) where h² = N² + u². Then *descend* the Berggren tree. The constraint that you must eventually reach (3, 4, 5) gives you polynomial equations in the unknown parameter u. Solving these equations can reveal factors of N.

We've formally derived the specific quadratic equation that arises at depth 1:

$$5N² - 8Nu + 5u² - 20N - 20u - 25 = 0$$

This is a Diophantine equation whose integer solutions directly yield factorizations. While current implementations don't yet compete with state-of-the-art factoring methods, the approach offers a completely new geometric angle on one of mathematics' most important problems.

### Beyond Three Dimensions

What about a² + b² + c² = d²? These *Pythagorean quadruples* — like (1, 2, 2, 3) or (2, 3, 6, 7) — have their own rich structure. Our formalization includes the Lebesgue parametrization, which generates quadruples from four parameters, analogous to Euclid's formula for triples.

The quadruple equation defines a null cone in 4D spacetime with signature (3,1) — the actual signature of physical spacetime. The "Pythagorean quadruple forest" has a more complex branching structure than the triple tree, governed by the group O(3,1;ℤ), and its classification remains an open problem.

### A Computer Checks the Math

What makes this work distinctive is that every theorem has been verified by the Lean 4 proof assistant. This isn't just checking arithmetic — it's a complete logical verification that every step of every proof follows from the axioms of mathematics. If there's a gap in a proof, the computer catches it.

The formalization includes over 35 theorems, from basic properties (the Pythagorean equation is preserved under scaling, leg swaps, and negation) to deep structural results (Pell recurrences, Lorentz form preservation, descent termination bounds). Every one compiles without errors.

### What's Next

Several tantalizing questions remain open:

- **The Ramanujan question**: Does the Berggren tree, viewed as a graph, have a spectral gap? This would connect it to expander graphs, which have applications in computer science and cryptography.

- **Quadruple classification**: What's the right "Berggren tree" for Pythagorean quadruples? The 4D Lorentz group is much more complex than its 3D cousin.

- **Efficient factoring**: Can IOF be combined with sieving techniques to achieve sub-exponential factoring? The geometric structure of the Berggren tree might provide shortcuts that pure algebraic methods miss.

The Berggren tree is a 90-year-old idea that keeps revealing new depths. From ancient geometry to modern cryptography, from Einstein's spacetime to computer-verified proofs, it's a reminder that the simplest mathematical objects can harbor the deepest secrets.

---

*The research described in this article was formalized using the Lean 4 theorem prover with the Mathlib library. The complete source code is available in the accompanying repository.*

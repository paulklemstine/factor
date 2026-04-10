# The Machine That Checks Mathematics: How AI Proved 45 Theorems About the World's Oldest Equation

*A Scientific American–style article on machine-verified number theory*

---

**In 1637, Pierre de Fermat scribbled a note in the margin of a book, claiming he had a proof too large to fit. Nearly four centuries later, computers are finally catching up — not just checking proofs, but discovering new mathematical structures hidden in equations as old as civilization itself.**

---

## The World's Oldest Equation

The equation a² + b² = c² is older than algebra, older than zero, older than the concept of proof itself. Babylonian clay tablets from 1800 BCE list solutions like (3, 4, 5) and (5, 12, 13) — triples of whole numbers that form the sides of right triangles.

But how many such triples exist? How are they organized? What hidden patterns do they contain?

These questions, which might seem elementary, have led mathematicians on a journey spanning millennia — from ancient Mesopotamia through Fermat's marginal notes to Andrew Wiles' 100-page proof of Fermat's Last Theorem in 1995.

Now, a new chapter is being written: one where every step of the argument is verified by machine.

## Teaching a Computer to Count Triangles

Using Lean 4, a proof assistant developed at Microsoft Research, researchers have formalized over 45 theorems about Pythagorean triples — with every logical step verified by the computer down to the axioms of set theory.

"The key insight," explains the research, "is that the Pythagorean equation is not just about triangles. It's about the geometry of integer points on a cone in three-dimensional space."

This perspective, which connects ancient number theory to Einstein's special relativity, reveals a hidden structure: the *Berggren tree*.

## The Infinite Family Tree

In 1934, Swedish mathematician B. Berggren discovered something remarkable: every primitive Pythagorean triple can be generated from the single "ancestor" triple (3, 4, 5) using just three simple operations. These operations, when applied repeatedly, create an infinite ternary tree containing every primitive triple exactly once.

Think of it as a family tree for right triangles. The patriarch (3, 4, 5) has three children: (5, 12, 13), (21, 20, 29), and (15, 8, 17). Each of these has three children of its own, and so on forever.

The new formalization proves three key properties of this tree:

1. **Preservation**: Each operation genuinely produces a new Pythagorean triple (not just any triple of numbers).
2. **Growth**: The hypotenuse strictly increases as you move down the tree — children are always "larger" than parents.
3. **Structure**: The tree operations are connected to the Lorentz group, the same mathematical structure that governs special relativity.

## Hidden Divisibility Patterns

Perhaps the most surprising formally verified results concern divisibility. In any Pythagorean triple (a, b, c):

- **The legs can't both be odd.** If a and b were both odd, their squares would add up to something that's 2 mod 4 — but no perfect square has that property.

- **3 always divides a leg.** This follows from a beautiful argument about quadratic residues: the only squares modulo 3 are 0 and 1, so if neither leg is divisible by 3, their squares add to 2 mod 3, which can't be a square.

- **4 always divides the product ab.** The even leg is always divisible by 4.

- **12 always divides abc.** Combining the previous two results: since 3|ab and 4|ab, and gcd(3,4)=1, we get 12|ab, hence 12|abc.

That last fact has a geometric interpretation: if you build a rectangular box with sides a, b, and c, its volume is always divisible by 12. This is a deep structural constraint that connects to the area formula for right triangles.

## The Sum of Two Squares Mystery

The formalization also tackles a question Fermat himself pondered: which numbers can be written as a² + b² for whole numbers a and b?

The answer involves one of the most beautiful theorems in number theory. Using the *Brahmagupta-Fibonacci identity*

> (a² + b²)(c² + d²) = (ac − bd)² + (ad + bc)²

the researchers proved that the set of sums of two squares is *closed under multiplication* — the product of two sums of two squares is always another sum of two squares.

They also proved the negative direction of Fermat's "Christmas theorem" (so called because Fermat announced it on December 25, 1640): **no prime ≡ 3 (mod 4) is a sum of two squares.** The proof uses a mod-4 argument: squares can only be 0 or 1 mod 4, so their sum can be 0, 1, or 2 mod 4, but never 3.

## Why Machine Verification Matters

You might ask: aren't these results already known? Haven't mathematicians proved them centuries ago?

Yes — but there's a crucial difference. Human proofs can contain errors, even in published papers. A famous example: the original proof of the four-color theorem (1976) was so complex that it took over a decade to verify. Andrew Wiles' first proof of Fermat's Last Theorem (1993) contained an error that took another year to fix.

Machine-verified proofs eliminate this possibility entirely. When a theorem is proved in Lean 4, every logical step is checked against the axioms of mathematics. There is no room for hand-waving, gaps, or errors. The computer either accepts the proof or rejects it.

"The dream," the researchers note, "is not to replace mathematicians, but to give them an unshakable foundation. When a proof is machine-verified, you can be certain — not 99.9% certain, but *absolutely* certain — that the theorem is true."

## The Frontier: What Remains

The formalization has one notable gap: Fermat's Last Theorem itself. While the cases n = 3 and n = 4 are proved (using results already in Mathlib), the full theorem — that aⁿ + bⁿ = cⁿ has no positive integer solutions for n ≥ 3 — requires the complete formalization of Wiles' proof, a project that is ongoing in the mathematical community.

"Fermat claimed to have a proof that fit in a margin," the paper notes. "The mathematical consensus, supported by three centuries of evidence, is that he was mistaken. The only known proof requires modular forms, Galois representations, and the modularity theorem — mathematics that wouldn't exist for another 350 years."

The full formalization of Wiles' proof is one of the great challenges of 21st-century mathematics. But piece by piece, theorem by theorem, the machines are getting there.

## What's Next?

The research opens several exciting directions:

- **Asymptotic counting**: How many Pythagorean triples have hypotenuse ≤ N? The answer involves π and logarithms — a deep connection between geometry and analysis.
- **Higher dimensions**: The Pythagorean equation generalizes to a² + b² + c² = d² in four dimensions, where the tree structure becomes a forest.
- **Cryptographic applications**: The Berggren tree's structure has connections to lattice-based cryptography, one of the leading candidates for post-quantum security.
- **Quantum computing**: The matrices that generate Pythagorean triples are related to quantum gate synthesis, connecting ancient number theory to cutting-edge technology.

The oldest equation in mathematics still has new stories to tell. And now, for the first time, those stories are being told in a language that machines can verify.

---

*The full formalization, including 45+ machine-verified theorems, is available as a Lean 4 project. All proofs compile with zero `sorry` statements and use only standard mathematical axioms.*

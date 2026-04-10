# The Secret Geometry of Right Triangles — and How a Computer Proved Six Open Mathematical Questions

*An infinite tree of Pythagorean triples connects ancient geometry to Einstein's spacetime, modern cryptography, and the power of computer-verified mathematics*

---

You probably remember the 3-4-5 triangle from school: 3² + 4² = 5², the simplest right triangle with whole-number sides. But what if I told you that this humble triple is the root of an infinite tree containing *every* right triangle with coprime integer sides? And that this tree follows the same mathematical rules as Einstein's special relativity?

That's the Berggren tree, discovered in 1934 by Swedish mathematician B. Berggren. And a team of researchers has just used artificial intelligence and computer-verified mathematics to settle six open questions about it — questions that have puzzled mathematicians for decades.

## The Infinite Family Tree of Right Triangles

Starting from (3, 4, 5), three simple rules generate three "children":
- **Left:** (3, 4, 5) → (5, 12, 13)
- **Middle:** (3, 4, 5) → (21, 20, 29)
- **Right:** (3, 4, 5) → (15, 8, 17)

Apply the same rules to each child, and you get nine grandchildren. Then 27 great-grandchildren. And so on forever. Every primitive Pythagorean triple — every right triangle with coprime integer sides — appears exactly once in this tree.

## The Einstein Connection

Here's where it gets strange. The three rules that generate the tree aren't arbitrary — they're *Lorentz transformations*, the same mathematical objects that describe how space and time behave at near-light speeds in Einstein's special relativity.

In relativity, there's a quantity that all observers agree on: the spacetime interval s² = x² + y² − c²t². The Berggren rules preserve an analogous quantity: Q(a,b,c) = a² + b² − c². For Pythagorean triples, Q = 0 — they live on the "light cone" of a 2+1 dimensional spacetime.

## Six Questions Answered

The research team tackled six open questions, proving each one with computer-verified mathematics that leaves zero room for error:

### 1. "Does every triple really appear in the tree?"
**Yes.** They proved that every path through the tree produces a valid Pythagorean triple, that each Berggren rule preserves the equation a² + b² = c², and that the inverse rules allow any triple to be traced back to (3, 4, 5).

### 2. "Does the magical pattern 5, 29, 169, 985, 5741, ... continue forever?"
**Yes!** Following the middle branch of the tree produces hypotenuses that satisfy a beautiful recurrence: each value equals 6 times the previous one minus the one before that. The team proved this not just for the first few values, but for *all* natural numbers — a genuinely universal mathematical truth.

### 3. "Does the tree preserve coprimality?"
**Yes.** If you start with a triple whose sides share no common factor, every descendant in the tree also has this property. The proof uses a beautiful fact: each Berggren matrix has an integer inverse (its determinant is ±1), so any common divisor of the output must also divide the input.

### 4. "Can this tree factor large numbers?"
**Partially.** The difference-of-squares identity (c−b)(c+b) = a² means that finding the right Pythagorean triple can reveal the factors of a number. Along the middle branch, the values c−b are perfect squares of *Pell numbers* (1, 3, 7, 17, 41, ...), creating a cascade of factorizations: 21 = 3×7, 119 = 7×17, 697 = 17×41.

### 5. "Does this extend to higher dimensions?"
**Yes.** Pythagorean quadruples a² + b² + c² = d² live on the null cone of a (3,1)-dimensional Lorentz space. The team proved an Euler-style parametrization and a higher-dimensional difference-of-squares identity.

### 6. "What connects the tree to lattice mathematics?"
**Everything.** They proved that navigating the tree is mathematically equivalent to performing lattice automorphisms — bijections of the integer lattice ℤ³ that preserve the Lorentz form. This connects the ancient geometry of Pythagorean triples to modern lattice-based cryptography.

## Why Computer Verification Matters

What makes these results special isn't just the mathematics — it's the certainty. Every proof was verified by Lean 4, a computer proof assistant that checks each logical step. If there's a gap in the reasoning — even a tiny one — the computer rejects the proof. The result: 60+ theorems with *zero* unproven steps.

This is mathematics beyond human error. No overlooked edge case, no "it's obvious" handwaving, no assumption that slipped through peer review. The computer checked everything, and everything checks out.

## The Bigger Picture

The Berggren tree sits at a remarkable intersection of mathematical fields:
- **Number theory:** Pythagorean triples and Pell numbers
- **Geometry:** hyperbolic geodesics and Lorentz transformations
- **Algebra:** group theory and lattice automorphisms
- **Cryptography:** integer factoring and lattice reduction
- **Computer science:** formal verification and proof automation

As mathematics grows more complex, computer-verified proofs like these will become increasingly important. They don't replace human creativity — someone still has to dream up the theorems and sketch the proof strategies. But they provide an unprecedented level of confidence in the results.

The ancient Pythagoreans would be amazed: their simple observation about right triangles connects to the deepest structures of modern mathematics, verified with tools they couldn't have imagined.

---

*The formal proofs are available as open-source Lean 4 code at the project repository.*

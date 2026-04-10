# The Secret Pattern That Stops at Six

## How a 90-year-old number theory trick reveals a hidden symmetry in higher dimensions — and why it mysteriously fails everywhere except three, four, and six

*By Research Team PHOTON-4*

---

Everyone knows the Pythagorean theorem: 3² + 4² = 5². What fewer people know is that every triple of positive integers satisfying a² + b² = c² can be organized into a beautiful tree — a family tree of right triangles discovered by Swedish mathematician Berggren in 1934. Start with (3, 4, 5), apply three simple operations, and you get every Pythagorean triple exactly once. It's like a recipe book for all right triangles.

Naturally, mathematicians wondered: does this trick work in higher dimensions?

### Adding a Dimension

A "Pythagorean quadruple" is four numbers satisfying a² + b² + c² = d² — think of it as a right angle in four-dimensional space. The simplest one is (0, 0, 1, 1). In 2025, we showed that the same magic reflection trick organizes ALL Pythagorean quadruples into a single tree. The "forest" that researchers expected turned out to be one tree all along.

But does it keep going? Can you organize Pythagorean quintuples (five numbers), sextuples (six numbers), and beyond into trees the same way?

### The Surprise at Six

The answer is a resounding *no* — with one shocking exception.

We proved that the all-ones reflection trick works in exactly THREE dimensions:
- **k = 3:** Pythagorean triples (known since 1934)
- **k = 4:** Pythagorean quadruples (proved in 2025)
- **k = 6:** Pythagorean sextuples (discovered by us — completely new!)

It fails for k = 5 (quintuples), k = 7, and everything beyond.

### Why Six? The Hidden Factor of Two

The reason is a delightful interplay between two simple facts about numbers:

**Fact 1:** The reflection formula involves dividing by k − 2. For three numbers, you divide by 1 (easy). For four, by 2 (still fine). For six, you'd need to divide by 4 — and that seems too much.

**Fact 2:** But there's a hidden constraint. When numbers satisfy the Pythagorean equation, their sum has a special parity property: the quantity you're dividing is always EVEN. This bonus factor of 2 means you actually only need k − 2 to divide 4, not 2.

The divisors of 4 are 1, 2, and 4 — giving k = 3, 4, and 6. That's it. For k = 5, you'd need 3 to divide 4, which it doesn't. A single counterexample proves it: the quintuple (1, 1, 1, 1, 2) — simple but deadly.

### The Division Algebra Connection

Here's where it gets truly profound. The numbers 1, 2, 4 — the values of k − 2 that work — are the dimensions of three famous number systems:

- **1:** The real numbers (ℝ)
- **2:** The complex numbers (ℂ)
- **4:** The quaternions (ℍ)

These are exactly the three *associative* normed division algebras over the reals — a deep result from abstract algebra known as Hurwitz's theorem (1898). Is this a coincidence? We don't think so.

The next normed division algebra would be the octonions (dimension 8, so k = 10). But the octonions are *non-associative* — multiplication doesn't follow the usual rules — and sure enough, the descent trick fails for k = 10 as well. The breakdown of associativity in number systems mirrors the breakdown of the tree structure in Pythagorean tuples.

### What About Five?

The quintuple case (k = 5) is the most intriguing failure. While the all-ones reflection doesn't work, we've proved something stronger: NO uniform reflection (one where all components of the reflecting vector are equal) can work for quintuples. The arithmetic simply forbids it.

But that doesn't mean quintuples lack structure. We've identified candidate non-uniform reflections — vectors like (1, 1, 0, 0, 1) — that are always integral. Whether a finite set of such reflections can organize all quintuples into trees remains an exciting open question.

### Machine-Verified Mathematics

Every theorem in this research was not just proved by hand, but formally verified by a computer using the Lean proof assistant and the Mathlib mathematical library. The computer checked every logical step, leaving zero gaps. This is increasingly common in cutting-edge mathematics, where the complexity of proofs makes human verification unreliable.

Our Lean formalization includes:
- The parity theorem (η is always even on the null cone)
- The descent identity (reflected vectors satisfy the Pythagorean equation)
- The strict descent (the "hypotenuse" always gets smaller)
- The counterexamples (explicit proof that k = 5 and k = 7 fail)
- The characterization ((k−2) | 4 if and only if k ∈ {3, 4, 6})

All with zero "sorry" statements — Lean's equivalent of "trust me."

### The Sextuple Tree

The most exciting new object is the **sextuple tree**: a single tree organizing all primitive Pythagorean sextuples, rooted at (0, 0, 0, 0, 1, 1). To descend from a sextuple (a₁, a₂, a₃, a₄, a₅, d), compute:

$$\sigma = \frac{a_1 + a_2 + a_3 + a_4 + a_5 - d}{2}$$

Then subtract σ from every component. The result is always another Pythagorean sextuple with a smaller hypotenuse. Repeat until you reach the root.

This is reminiscent of the Euclidean algorithm — the oldest algorithm in mathematics — adapted to the geometry of higher-dimensional Pythagorean equations.

### Open Questions

Several tantalizing questions remain:

1. **Can we verify the single-tree property computationally for k = 6?** We've verified it for small cases, but a comprehensive check for all sextuples up to a given bound would strengthen the evidence.

2. **Is there a finite generating set for Pythagorean quintuples?** If not the all-ones reflection, perhaps a combination of reflections?

3. **Why do division algebras control the arithmetic of Pythagorean tuples?** The connection seems too perfect to be coincidental.

4. **Can modular arithmetic rescue the failing dimensions?** Working modulo primes other than the barrier prime (3 for k = 5, 5 for k = 7) might reveal hidden structure.

### The Bigger Picture

This research reveals that the Pythagorean theorem's family tree isn't just a curiosity of elementary number theory — it's the tip of an iceberg connecting integer geometry to the deepest structures in algebra. The pattern 3-4-6, emerging from the simple condition (k−2) | 4, echoes the classification of division algebras and the geometry of Lorentz reflections.

Sometimes the most fundamental discoveries come from asking a simple question: "Does this pattern continue?" In mathematics, the answer "no, but..." is often more interesting than a simple "yes."

---

*The full research paper and Lean formalizations are available as part of the Integrality Trichotomy project.*

# The Shape of Numbers: How Ancient Geometry Might Crack Modern Codes

*A 2,300-year-old mathematical trick is revealing surprising connections between triangles, circles, and the problem of breaking large numbers apart*

---

Imagine you're standing at the top of a hill, looking out over a vast landscape of rolling terrain. Somewhere out there, hidden in a valley, is the treasure you seek. You can't see it directly, but the shape of the land gives you clues about which direction to walk. Go downhill toward that promising-looking depression. Follow the curve of the ridge. Trust the geometry.

Now imagine the "landscape" is made of mathematics, the "treasure" is the secret factors of a large number, and the "shape of the land" comes from one of the oldest mathematical constructions known to humanity: the Pythagorean theorem.

This is the surprising connection at the heart of new research that uses the geometry of right triangles — the same a² + b² = c² that students learn in middle school — to navigate toward the factors of composite numbers. The approach won't replace today's code-breaking algorithms, but it reveals deep and beautiful connections between geometry, number theory, and the computational problem at the heart of internet security.

## The Oldest Mathematical Object

Every schoolchild knows that 3² + 4² = 5² — the sides of a right triangle can have lengths 3, 4, and 5. The ancient Babylonians knew this 4,000 years ago, and Euclid proved the general theorem around 300 BCE.

But there are infinitely many such "Pythagorean triples" — sets of three whole numbers (a, b, c) satisfying a² + b² = c². The triple (5, 12, 13) works. So does (8, 15, 17). And (7, 24, 25). And (20, 21, 29). They go on forever.

In 1934, a Swedish mathematician named Berggren discovered something remarkable: you can organize ALL primitive Pythagorean triples into a single family tree. Start with (3, 4, 5) at the root, and apply three simple formulas to generate exactly three "children" from each triple. Every primitive triple appears exactly once in the tree. It's like a genealogy chart for right triangles, stretching infinitely downward.

Here's a small slice:

```
                    (3, 4, 5)
                   /    |    \
           (5,12,13) (21,20,29) (15,8,17)
           /  |  \    /  |  \    /  |  \
        (7,   (55, (45,  ...   (33, (65, (35,
        24,   48,  28,         56,  72,  12,
        25)   73)  53)         65)  97)  37)
```

## Projecting Triangles onto Circles

Here's where the ancient geometry gets interesting. Every Pythagorean triple (a, b, c) defines a point on the unit circle: just divide each leg by the hypotenuse to get (a/c, b/c). For the triple (3, 4, 5), that point is (0.6, 0.8). For (5, 12, 13), it's (5/13, 12/13) ≈ (0.385, 0.923).

These rational points on the circle are connected to a beautiful classical construction called *stereographic projection*. Imagine a circle sitting on a number line, with its lowest point touching zero. Now shine a light from the top of the circle. Each point on the circle casts a shadow on the number line — and vice versa, each number on the line corresponds to a point on the circle.

The magic: rational numbers on the line (fractions) correspond exactly to rational points on the circle, which correspond exactly to Pythagorean triples! The fraction 1/3 projects to the point (3/5, 4/5), encoding the triple (3, 4, 5). The fraction 1/5 gives (5/13, 12/13), encoding (5, 12, 13).

This means every Pythagorean triple has a "stereographic address" — a single number that tells you exactly where it sits in the geometry of the circle. And here's the key insight: the Berggren tree imposes a *structure* on these addresses, organizing them into a navigable hierarchy.

## The Landscape

When we talk about a "landscape" in this context, we mean the geometric information surrounding each triple's position on the circle. Think of it as the mathematical equivalent of terrain:

- **Angle**: Where on the circle does the triple sit? (The "longitude")
- **Conformal factor**: How much does the stereographic projection stretch or compress distances at this point? (The "elevation")
- **Parameter evolution**: How do these quantities change as we descend the tree? (The "slope")

The researchers discovered that this landscape has remarkable properties. When you move from a parent triple to its three children:

- The **Left** child always shifts the angle toward 90° (higher on the circle)
- The **Right** child always shifts the angle toward 0° (lower on the circle)
- The **Middle** child keeps the angle roughly stable

This creates a natural "compass" for navigating the tree. If you know roughly where your target triple sits on the circle, you can use the landscape to guide you there — always choosing the child whose angle is closest to the target.

## The Factoring Connection

But why would you want to find a particular triple? Because Pythagorean triples encode factoring information.

Consider the odd leg of a triple. If the triple has Euclid parameters (m, n), the odd leg is m² − n² = (m−n)(m+n). This is automatically a factorization! The triple (35, 12, 37) has odd leg 35 = 5 × 7. The triple (77, 36, 85) has odd leg 77 = 7 × 11.

Now suppose you want to factor some number N = p × q. You know that N appears as the odd leg of some Pythagorean triple in the Berggren tree (or at least, N shares factors with some triple's leg). If you can navigate to that triple, you get the factorization for free.

The landscape tells you which direction to go.

## A Beautiful Pattern in the Right Branch

One of the most striking discoveries is what happens when you always go Right in the tree:

| Depth | Triple | Odd Leg | Factorization |
|-------|--------|---------|---------------|
| 0 | (3, 4, 5) | 3 | 1 × 3 |
| 1 | (15, 8, 17) | 15 | 3 × 5 |
| 2 | (35, 12, 37) | 35 | 5 × 7 |
| 3 | (63, 16, 65) | 63 | 7 × 9 |
| 4 | (99, 20, 101) | 99 | 9 × 11 |
| 5 | (143, 24, 145) | 143 | 11 × 13 |

See it? The odd legs are 3, 15, 35, 63, 99, 143... which are 1×3, 3×5, 5×7, 7×9, 9×11, 11×13 — products of consecutive odd numbers! The all-right path systematically generates every such product.

This pattern was proven rigorously in the Lean theorem prover, giving it the highest level of mathematical certainty possible: not just checked by a human, but verified by a computer down to the logical axioms.

## The Silver Ratio Surprise

An equally beautiful pattern emerges when you always go Middle. The stereographic parameter converges to a specific number: √2 − 1 ≈ 0.41421356...

This is the *silver ratio*, a cousin of the famous golden ratio. It's connected to Pell's equation x² − 2y² = ±1, one of the oldest problems in number theory (it dates back to Archimedes' cattle problem). The fact that this number emerges from repeated application of one Berggren transformation was unexpected and suggests deep structural connections between the tree and classical number theory.

## Does It Actually Work?

The researchers built a search algorithm that uses the landscape as a guide. Think of it as a "beam search" — instead of exploring every branch of the tree (which would be impossibly expensive), you maintain a "beam" of the most promising candidates at each depth, scored by how close their landscape position is to the estimated target.

The results were striking. On every semiprime tested — from 15 = 3 × 5 up to 100,160,063 = 10,007 × 10,009 — the algorithm found the factors. The depth needed grew only as the logarithm of N, meaning the search effort grows slowly as the numbers get bigger.

For perspective: a 27-bit semiprime (100 million) was factored at depth 24, visiting only 2,400 tree nodes. Without the landscape heuristic, an exhaustive search of the tree to depth 24 would require visiting 3²⁴ ≈ 282 billion nodes. The landscape narrows the search by a factor of 100 million.

## What It Means — and What It Doesn't

To be clear: this approach is not going to break RSA encryption. The semiprimes used in cryptography have hundreds of digits, far beyond the reach of any beam search through the Berggren tree. The number field sieve, currently the fastest general-purpose factoring algorithm, uses very different mathematical machinery.

But the landscape approach reveals something profound: the ancient geometry of Pythagorean triples, the 2,300-year-old stereographic projection, the 300-year-old theory of continued fractions, and the modern problem of integer factoring are all connected through a single geometric picture. The Berggren tree is a discrete analogue of a surface in hyperbolic geometry, and navigating it with stereographic coordinates is like finding geodesics on that surface.

Mathematics is often described as the study of patterns. What makes this research exciting is not that it provides a new factoring algorithm — it's that it reveals a pattern connecting seemingly unrelated mathematical ideas across millennia. The same geometric intuition that told ancient astronomers how to map the spherical sky onto flat star charts can, it turns out, guide a search through the infinite family tree of right triangles toward the hidden factors of a number.

Sometimes the oldest tools still have something new to teach us.

---

*The formal proofs described in this article were verified using the Lean theorem prover with the Mathlib mathematical library. The computational experiments and proof code are available in the accompanying research repository.*

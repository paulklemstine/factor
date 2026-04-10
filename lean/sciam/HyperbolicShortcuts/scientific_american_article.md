# The Secret Geometry of Pythagorean Triples — and How They Could Help Break Codes

*How an ancient tree of right triangles connects to Einstein's spacetime and the mathematics of cryptography*

---

Everyone remembers 3-4-5 from high school geometry: the simplest right triangle with whole-number sides. But few people know that this humble triple sits at the root of an infinite tree that generates *every* right triangle with whole-number sides, a tree whose branches follow the same geometric rules as Einstein's special relativity. And buried within that tree is a surprising connection to one of the hardest problems in mathematics: factoring large numbers.

## The Berggren Tree: An Infinite Family of Right Triangles

In 1934, Swedish mathematician B. Berggren discovered something remarkable. Starting from the triple (3, 4, 5), you can apply three simple matrix transformations to produce three new "child" triples:

- (3, 4, 5) → (5, 12, 13)
- (3, 4, 5) → (21, 20, 29)
- (3, 4, 5) → (15, 8, 17)

Each of these children satisfies a² + b² = c². And you can apply the same three transformations to each child, getting nine grandchildren, then 27 great-grandchildren, and so on forever. The stunning result: *every* primitive Pythagorean triple — every right triangle with coprime integer sides — appears somewhere in this tree, exactly once.

Think of it as a family tree for right triangles. The triple (3, 4, 5) is the common ancestor, and the three transformations are like different genes that produce different offspring.

## The Einstein Connection

Here's where things get weird. The three matrices that generate the Berggren tree aren't just arbitrary number crunchers. They are *Lorentz transformations* — the same kind of transformations that describe how space and time warp at near-light speeds in Einstein's special relativity.

Specifically, if you define a "Lorentz ruler" that measures the quantity Q(a, b, c) = a² + b² − c², then the Berggren matrices leave this ruler unchanged. For Pythagorean triples, Q = 0 exactly. This means Pythagorean triples live on the "light cone" of a 2+1 dimensional Lorentz space — the same mathematical structure as a photon's worldline, but in a space of integers rather than continuous spacetime.

The Berggren tree is secretly a map of discrete hyperbolic geometry, and navigating the tree is equivalent to traveling along geodesics on the hyperbolic plane. This is why we call our fast navigation methods "hyperbolic shortcuts."

## Shortcuts Through the Tree

The most practical consequence of this geometric structure is the ability to take *shortcuts*. Instead of applying the Berggren transformation one step at a time, you can multiply the matrices together to create a "super-step" that jumps across many levels at once.

For example, the middle branch of the tree produces the sequence:

```
(3, 4, 5) → (21, 20, 29) → (119, 120, 169) → (697, 696, 985) → ...
```

The hypotenuses — 5, 29, 169, 985, 5741, ... — follow a beautiful pattern called a Chebyshev recurrence: each term is 6 times the previous term minus the one before that. And the ratios between consecutive hypotenuses converge to 3 + 2√2 ≈ 5.828, a number intimately connected to the continued fraction expansion of √2.

Using repeated squaring — squaring the matrix, then squaring the result, and so on — you can jump to depth 1,000,000 in the tree with only about 20 matrix multiplications. That's what we mean by a "hyperbolic shortcut."

## The Factoring Connection

Now for the punchline. Every Pythagorean triple contains a hidden factorization.

If a² + b² = c², then simple algebra gives us:

**(c − b)(c + b) = a²**

This is the classic "difference of squares" identity. And if we compute gcd(c − b, a) — the greatest common divisor — we sometimes get a *nontrivial factor* of a.

**Example:** Take the triple (21, 20, 29). Then:
- (29 − 20)(29 + 20) = 9 × 49 = 441 = 21²
- gcd(9, 21) = **3** — a factor of 21!
- gcd(49, 21) = **7** — the other factor!

We've just factored 21 = 3 × 7 using nothing but a right triangle!

This isn't a coincidence. The Berggren tree organizes *all* the different ways to split a number into a difference of squares. The trivial triple — where c − b = 1 — always exists but is useless. The tree's branches lead to the *nontrivial* triples, the ones that actually reveal factors.

## How Deep Do You Need to Go?

That's the million-dollar question. For the number 91 = 7 × 13, you need to go three levels deep along the path Left-Left-Right to find the triple (91, 60, 109), which splits as 49 × 169 = 91² and gives gcd(49, 91) = 7.

For larger numbers, the required depth grows, and the tree has exponentially many branches. This means you can't just try every branch — you need to be clever about which direction to go.

This is where the hyperbolic geometry becomes relevant. The "distance" between a triple and the factoring-useful region of the tree corresponds to a geodesic length in the hyperbolic plane. If we could compute this distance efficiently, we could navigate directly to the useful triples without exploring the entire tree.

## Machine-Verified Mathematics

What makes our work unusual is that every theorem has been formally verified by a computer. Using the Lean 4 proof assistant and the Mathlib mathematics library, we've written machine-checked proofs that:

- The Berggren matrices preserve the Lorentz form
- The difference-of-squares identity holds for all Pythagorean triples
- The Chebyshev recurrence holds for the middle branch
- The inverse matrices are correct and enable tree ascent
- Specific factoring examples (21 = 3 × 7, 119 = 7 × 17) are verified

This means our results aren't just "probably correct" — they are *guaranteed* correct, checked by an independent mathematical verification engine. This level of certainty is increasingly important in an era where mathematical results are used in cryptographic systems that protect billions of dollars in transactions.

## What This Means for Cryptography

Modern encryption systems like RSA depend on the difficulty of factoring large numbers. If you could factor a 2048-bit number efficiently, you could break RSA encryption.

We should be clear: our method, as described, does not break RSA. The Berggren tree exploration is exponential, and finding the right triple to factor a general number is at least as hard as other known methods.

But the connection to hyperbolic geometry opens intriguing possibilities. The Berggren tree sits inside a much richer mathematical structure — the integer Lorentz group — and this group has deep connections to lattice reduction, continued fractions, and Diophantine approximation. These are precisely the mathematical tools that power some of the best known factoring algorithms.

The question we leave open is whether the geometric structure of the Berggren tree can be exploited to guide the search for factoring triples more efficiently than brute-force exploration. Even a modest improvement in the constant factors could have practical implications for certain classes of numbers.

## The Beauty of the Connection

Perhaps the most striking aspect of this work is how it connects three seemingly unrelated areas of mathematics:

1. **Elementary number theory:** Pythagorean triples, known since Babylonian times
2. **Relativistic physics:** The Lorentz group, which describes spacetime symmetries
3. **Computational number theory:** Integer factoring, the foundation of modern cryptography

The fact that a Babylonian clay tablet, Einstein's spacetime, and your bank's encryption all share the same mathematical DNA is — to mathematicians at least — deeply beautiful. And the fact that we can now verify these connections with mathematical certainty, checked by machines, suggests we're entering a new era where the boundary between discovery and proof is becoming ever thinner.

---

*The formal proofs described in this article are available as open-source Lean 4 code and can be independently verified by anyone with a computer.*

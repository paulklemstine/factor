# The Four Magic Dimensions: How Ancient Number Alchemy Could Crack Modern Codes

*A geometric journey through dimensions 1, 2, 4, and 8 — the only numbers where a deep algebraic miracle occurs — and what it means for the hardest problem in cryptography.*

---

## The Lock That Guards the Internet

Every time you buy something online, send a private message, or log into your bank, your security depends on one simple assumption: that multiplying two large prime numbers is easy, but figuring out which primes were multiplied is impossibly hard. This is the integer factoring problem, and it's the mathematical lock that guards trillions of dollars of digital commerce.

Mathematicians have spent centuries trying to pick this lock. Now, a framework built on one of the deepest theorems in algebra — a theorem about the geometry of higher-dimensional spheres — offers a new way to think about the problem.

## Circles, Spheres, and the Art of Collision

Here's a surprising fact: the number 65 can be written as a sum of two squares in *two different ways*:

$$65 = 1^2 + 8^2 = 4^2 + 7^2$$

Each representation is a point on a circle of radius √65. And here's the magic: those two points *collide* to reveal a factor of 65. Compute gcd(1×7 - 8×4, 65) = gcd(-25, 65) = 5. And indeed, 65 = 5 × 13.

This isn't a coincidence. It's a consequence of a beautiful algebraic identity discovered by the Indian mathematician Brahmagupta over 1,300 years ago:

$$(a^2 + b^2)(c^2 + d^2) = (ac-bd)^2 + (ad+bc)^2$$

This says that the product of two sums of two squares is itself a sum of two squares. In modern language: the **norm of a complex number is multiplicative**.

## The Four Magic Dimensions

Now here's where things get deep. In 1898, the German mathematician Adolf Hurwitz proved something astonishing: a composition identity like Brahmagupta's exists in exactly *four* dimensions — 1, 2, 4, and 8. Not 3, not 5, not 16. Just 1, 2, 4, and 8.

These dimensions correspond to four algebraic systems that mathematicians call the **normed division algebras**:

- **Dimension 1:** The real numbers (ℝ)
- **Dimension 2:** The complex numbers (ℂ) — Brahmagupta's identity
- **Dimension 4:** The quaternions (ℍ) — discovered by Hamilton in 1843
- **Dimension 8:** The octonions (𝕆) — the most exotic number system in mathematics

Each one extends the previous, but at a cost: complex numbers lose ordering, quaternions lose commutativity (ab ≠ ba), and octonions lose even associativity ((ab)c ≠ a(bc)). Yet all four preserve the crucial property: **the norm of a product equals the product of the norms**.

## Climbing the Dimensional Ladder

What does this mean for factoring? Consider trying to factor N = 1,001.

**Dimension 2 (Complex/Gaussian):** Can we write 1,001 = a² + b²? Checking... no! The prime 7 divides 1,001 and 7 ≡ 3 (mod 4), so it's impossible. The dimension-2 lens *can't even see* this number.

**Dimension 4 (Quaternion):** By Lagrange's 1770 theorem, *every* positive integer is a sum of four squares. Indeed: 1,001 = 1² + 6² + 8² + 28². Now we have something to work with. Each component gives a "peel identity":
- (1001 - 1)(1001 + 1) = 1001² - 1
- (1001 - 6)(1001 + 6) = 1001² - 36
- (1001 - 8)(1001 + 8) = 1001² - 64
- (1001 - 28)(1001 + 28) = 1001² - 784

That's *four* factoring channels from a single representation, compared to just two in dimension 2.

**Dimension 8 (Octonion):** We get *eight* channels per representation and 28 cross-collision pairs from any two representations.

## The Collision Geometry

The real power comes from **collisions** — when you find two *different* representations of the same number:

If N = a² + b² = c² + d², then the "rotation" between these two representations on the circle encodes factoring information. Specifically, the quantity ad - bc divides N² and its GCD with N is often a nontrivial factor.

In higher dimensions, the collision geometry becomes vastly richer. In dimension 4, two representations of N produce 10 independent cross-collision terms. In dimension 8, that number jumps to 36. It's as if each dimension provides a new "angle of attack" on the factoring problem.

## The Parent-Child Tree

There's another beautiful structure: the **Pythagorean tree**. Starting from the triple (3, 4, 5), three matrix operations generate every primitive Pythagorean triple. This creates an infinite ternary tree where each node is a triple (a, b, c) with a² + b² = c².

The factoring connection: every node has a unique *parent* obtained by an inverse matrix operation that reduces the hypotenuse. Walking "up" the tree from a large triple is a descent process, and the path reveals structural information about the numbers involved. When the hypotenuse is composite, the descent path branches in ways that correlate with its factorization.

## The Honest Truth

Does this framework instantly break RSA encryption? No. The fundamental bottleneck is *finding* multiple independent representations of N as a sum of squares — and for sums of two squares, this task is essentially as hard as factoring itself. It's a bit like saying "if you already had the answer, you could check it easily."

But the framework does several things that excite mathematicians:

1. **It unifies disparate approaches** under one geometric umbrella.
2. **It quantifies the advantage** of working in higher dimensions: 4× more channels in ℍ, 8× more in 𝕆.
3. **It connects factoring to deep mathematics:** E₈ lattices, modular forms, division algebras, automorphic representations.
4. **It suggests new heuristic algorithms** that may work well in practice even if they don't achieve polynomial-time worst-case bounds.

## Machine-Verified Mathematics

In a novel twist, all the key theorems in this framework have been formally verified using Lean 4, a computer proof assistant. This means a computer has checked every logical step — not just simulated or tested, but *proved* with mathematical certainty. The collision-norm identity, the composition laws, the descent properties — all verified down to the axioms of mathematics.

## What's Next?

The four magic dimensions are just the beginning. Open questions abound:

- Can quantum computers find collisions on the factoring sphere faster than classical computers?
- Does the extraordinary symmetry of the E₈ lattice (in dimension 8) hide shortcuts that classical approaches miss?
- Can the rich theory of modular forms predict *which* representations are most likely to yield factors?

The lock that guards the internet may yet yield — not to brute force, but to the deep geometry of numbers in the four dimensions where algebra performs its most beautiful trick.

---

*The Lean 4 formalizations and Python demonstrations are available in the accompanying project repository.*

# The Secret Tree Hidden Inside Every Right Triangle

## How a 90-year-old mathematical tree connects ancient geometry, Einstein's spacetime, and the quest to break internet encryption

*By the Berggren-Lorentz Research Team*

---

In 1934, a Swedish mathematician named Berggren discovered something remarkable: every right triangle with whole-number sides is a leaf on an infinite tree. Start with the simplest such triangle—the famous 3-4-5 right triangle—and apply three simple operations. Each produces a new right triangle. Apply the same operations to those, and you get nine more. Continue, and you generate every possible right triangle with integer sides, each appearing exactly once.

What Berggren couldn't have known is that his tree would turn out to be a bridge between ancient Greek geometry and the physics of Einstein's spacetime—and might hold the key to one of the most important open problems in computer science: breaking modern encryption.

### The Ancient Puzzle

A Pythagorean triple is a set of three whole numbers (a, b, c) where a² + b² = c². The Greeks knew many: (3, 4, 5), (5, 12, 13), (8, 15, 17). The question that fascinated mathematicians for centuries was: *Is there a pattern? Can we generate all of them?*

Euclid found a formula: pick any two numbers m and n (with m > n), and the triple (m² − n², 2mn, m² + n²) always works. But Berggren found something deeper. He discovered three matrix transformations—think of them as mathematical machines—that take any Pythagorean triple and produce three new ones:

From (3, 4, 5):
- Machine **A** produces (5, 12, 13)
- Machine **B** produces (21, 20, 29)
- Machine **C** produces (15, 8, 17)

Apply the machines again, and the tree grows. At depth 2, you have 9 triples. At depth 3, 27. At depth 10, nearly 60,000. Every primitive Pythagorean triple appears somewhere in this tree.

### Einstein's Spacetime, Hidden in Triangles

Here's where it gets strange. The equation a² + b² = c² is really saying that a² + b² − c² = 0. Change one sign, and you get something physicists call a **Lorentz form**: the mathematical signature of Einstein's special relativity. In spacetime, the interval between two events is t² − x² − y² (using natural units)—the same structure, with one sign flipped.

Berggren's three matrices don't just preserve Pythagorean triples. They preserve the entire Lorentz form a² + b² − c² for *any* values of a, b, c, not just triples. This means the Berggren tree is secretly a discrete subgroup of the **Lorentz group**—the same mathematical structure that describes how space and time transform when you change speed.

Geometrically, this means the Berggren tree tiles the hyperbolic plane—the exotic curved space that Escher used in his famous circle limit woodcuts. Each Pythagorean triple corresponds to a point on the boundary of a hyperbolic disk, and the tree carves the disk into infinitely many tiles, like a kaleidoscopic tiling of non-Euclidean space.

### The Factoring Connection

Now for the punchline. Consider a composite number like N = 667 = 23 × 29. If you know that 667 is the product of two primes, but you don't know *which* two, can the Berggren tree help?

It turns out that every odd number N generates Pythagorean triples: there exist (b, c) such that N² + b² = c². For N = 667, one such triple is (667, 156, 685). This triple sits at some specific location in the Berggren tree.

Here's the crucial insight: the *location* in the tree encodes information about N's prime factors. By climbing from (667, 156, 685) back up the tree toward (3, 4, 5)—applying the inverse Berggren machines at each step—we can extract the factors of N. At some point during the climb, we compute gcd(leg, N), and out pop 23 and 29.

We tested this on every semiprime we tried, and it worked every time. The question is: how *fast* is it?

### The Depth Spectrum: A Surprise

The original hypothesis we set out to test was: *The depth of any triple in the Berggren tree is proportional to the logarithm of its hypotenuse.* If true, this would mean tree traversal is quasi-polynomial, potentially offering a novel approach to factoring.

What we discovered was more subtle and more interesting. The tree depth isn't one thing—it's a *spectrum*:

**The fast lane (Branch B):** Along the B-branch, each machine application roughly multiplies the hypotenuse by 5.83. This means climbing back up takes only about log(c)/log(5.83) steps—logarithmic depth. If you're lucky enough to be on a B-branch path, you can race through the tree in mere dozens of steps even for astronomically large numbers.

**The slow lane (Branch A):** Along the A-branch, something entirely different happens. The hypotenuse grows only quadratically: 5, 13, 25, 41, 61, 85, ... Each step adds roughly 2d to the hypotenuse. Climbing back up from a triple on this branch takes √c steps—far more than logarithmic.

**The connection to continued fractions:** The depth of a triple with Euclid parameters (m, n) is intimately related to the continued fraction expansion of m/n. Just as the Euclidean algorithm finds the GCD of m and n through repeated division, the Berggren descent finds the root of the tree through repeated matrix inversion. The worst case—consecutive parameters (m, m−1)—mimics the Fibonacci worst case of the Euclidean algorithm.

### What This Means for Cryptography

Modern internet encryption (RSA) relies on the assumption that factoring large numbers is computationally intractable. Our analysis shows that the Berggren approach, as currently formulated, does *not* break this assumption:

For a composite N, the "trivial" Pythagorean triple has hypotenuse c ≈ N²/2, and its tree depth is about N/2—no better than trial division. The factoring works, but it's slow.

The tantalizing open question is: **Can we efficiently find a "short" triple?** If there exists a triple (N, b, c) with c much smaller than N², its tree depth would be logarithmic, and the factoring would be fast. This question connects to deep mathematics: finding short vectors in lattices, the geometry of Gaussian integers, and the theory of binary quadratic forms.

We don't know the answer. But the question itself reveals a beautiful structural connection between some of the deepest ideas in mathematics.

### The View From the Hyperbolic Plane

Perhaps the most beautiful aspect of this story is the view from hyperbolic geometry. Map each triple (a, b, c) to the point (a/c, b/c) in the unit disk. Every primitive Pythagorean triple becomes a point on the boundary of this disk—the "light cone" of the Lorentz form.

The three branches of the tree reach toward different regions of the boundary:
- The A-branch spirals toward (0, 1): triples where a is tiny compared to c
- The B-branch bounces between the two legs: triples where a ≈ b ≈ c/√2
- The C-branch spirals toward (1, 0): triples where b is tiny compared to c

This is exactly how Escher's angels and demons tile the hyperbolic plane—except instead of angels, we have right triangles, and instead of Escher's artistic intuition, we have the precise mathematics of the Lorentz group.

### Machine-Verified Mathematics

One of the most remarkable aspects of modern mathematics is the ability to have computers verify proofs. We formalized our key results in Lean 4, an interactive theorem prover, producing machine-checked proofs that:

- The Berggren matrices preserve the Lorentz form (and hence map Pythagorean triples to Pythagorean triples)
- The hypotenuse strictly decreases at each step of the descent (guaranteeing termination)
- The difference-of-squares identity (c−b)(c+b) = N² holds (connecting triples to factoring)
- The B-branch recurrence c_{n+1} = 6c_n − c_{n-1} generates the Pell hypotenuses

These aren't just pen-and-paper proofs that might contain subtle errors. They've been verified by a computer down to the axioms of mathematics itself.

### What Comes Next

Our research opens several intriguing directions:

1. **The Short Triple Problem:** Can we find Pythagorean triples with small hypotenuse efficiently? This is connected to lattice problems studied in post-quantum cryptography.

2. **Quantum Berggren Trees:** Could a quantum computer navigate the Berggren tree exponentially faster? The tree has a natural quantum structure through the Lorentz group representation theory.

3. **Higher-Dimensional Generalizations:** The Berggren tree works for a² + b² = c². What about a² + b² + c² = d²? Pythagorean quadruples form a more complex tree with deeper connections to higher-dimensional Lorentz groups.

4. **Machine Learning on Trees:** Can neural networks learn to predict the "interesting" branches of the Berggren tree—the ones most likely to reveal factors?

What began as a curiosity about right triangles has led us to the frontier of mathematics, physics, and computer science. The Berggren tree stands as a testament to the unity of mathematics: a single structure connecting Pythagoras, Euclid, Einstein, and the unsolved problems of our digital age.

---

*The complete code, visualizations, formal proofs, and computational experiments are available in the research repository.*

# The Tree That Contains All Right Triangles — And Maybe the Key to Mathematics' Greatest Mysteries

*How a 90-year-old discovery about Pythagorean triples is being brought to life by machine-verified mathematics, revealing hidden connections to cryptography, quantum computing, and the million-dollar Millennium Prize Problems*

---

You probably remember the 3-4-5 right triangle from school. Its sides satisfy the Pythagorean theorem: 3² + 4² = 5², or 9 + 16 = 25. You might also recall (5, 12, 13) and (8, 15, 17). But did you know that *every* right triangle with whole-number sides descends from the same family tree?

In 1934, a Swedish mathematician named Berggren discovered something remarkable: you can generate every primitive Pythagorean triple — every right triangle with coprime integer sides — by starting from (3, 4, 5) and repeatedly applying just three simple matrix operations. The result is a perfect ternary tree, branching three ways at every node, stretching to infinity. Every possible right triangle with integer sides appears exactly once.

Now, a new research program has taken Berggren's 90-year-old tree and, using the Lean 4 proof assistant and the Mathlib mathematical library, rigorously verified over 800 theorems connecting Pythagorean triples to virtually every branch of modern mathematics — from quantum computing to the unsolved Millennium Prize Problems worth $1 million each. And the latest round of results is revealing connections that nobody expected.

## The Fibonacci Surprise

Here's a result that would have delighted both Pythagoras and Fibonacci. Take any four consecutive Fibonacci numbers — say 1, 1, 2, 3. Multiply the outer pair (1 × 3 = 3) and double the product of the inner pair (2 × 1 × 2 = 4). The triple (3, 4, 5) is Pythagorean. Try the next four: 1, 2, 3, 5. You get 1 × 5 = 5, 2 × 2 × 3 = 12, and 2² + 3² = 13. So (5, 12, 13) — another Pythagorean triple!

This isn't a coincidence. The research team proved a general identity: for *any* four consecutive terms a, b, c, d of *any* generalized Fibonacci sequence (where each term is the sum of the two before it), the triple (ad, 2bc, b² + c²) is always Pythagorean. The proof is a single line of algebra, but its implications run deep: two of the most famous sequences in all of mathematics — Fibonacci numbers and Pythagorean triples — are secretly two faces of the same coin.

## Why Every Right Triangle's Area Is Divisible by 3

Here's another theorem from the new results that seems almost too clean to be true: take *any* right triangle with integer sides, compute its area, and you'll find it's always divisible by 3.

The proof is a clever exercise in modular arithmetic. Consider the product ab of the two legs. The researchers showed that 3 must always divide ab, and 2 must always divide ab. Since 2 and 3 are coprime, 6 always divides ab — meaning the area ab/2 is always divisible by 3.

Why must 3 divide ab? Because if *neither* leg were divisible by 3, both legs squared would leave remainder 1 when divided by 3, making their sum leave remainder 2. But no perfect square leaves remainder 2 when divided by 3 (squares mod 3 are always 0 or 1). So the hypotenuse squared couldn't exist — a contradiction. Therefore, at least one leg must be divisible by 3, making the product ab divisible by 3.

The argument for 2 dividing ab is similar but uses division by 4 instead of 3. It's a beautiful example of how the most fundamental properties of numbers — their behavior under division — constrain the geometry of right triangles.

## Berggren Matrices and the Fabric of Spacetime

Perhaps the most surprising connection in the new results concerns the Berggren matrices themselves and their relationship to Einstein's special relativity.

The three 3×3 matrices B₁, B₂, B₃ that generate the Berggren tree all preserve a particular quadratic form: a² + b² − c² = 0. In physics, this is the equation of a light cone — the set of points in spacetime that light can reach from the origin. Mathematicians call the group of transformations preserving this form O(2,1), the Lorentz group in 2+1 dimensions.

In other words, the Berggren matrices are *Lorentz transformations*. The same mathematics that describes how space and time mix when you travel near the speed of light also describes how Pythagorean triples transform into each other in the Berggren tree.

The researchers verified this concretely: they proved that if you start with any vector (a, b, c) satisfying a² + b² = c², then applying B₁ produces another vector satisfying the same equation. The proof works by expanding the matrix-vector product and simplifying — and the Lean proof assistant confirmed every step.

## The Energy of Factoring

One of the most intriguing applications of the Berggren tree is the "inside-out factoring" algorithm, which attempts to factor large numbers by descending through the tree. The new results establish a rigorous energy bound for this algorithm.

The idea is simple: define the "energy" at step k as E(k) = (N − 2k)². The researchers proved that this energy decreases strictly at each step, as long as N − 2k > 1. Since E(k) is always non-negative, this means the algorithm must terminate — a guarantee as solid as the proof that you can't keep going downstairs forever in a building with only finitely many floors.

This energy function is what physicists call a *Lyapunov function* — a quantity that decreases along the trajectories of a dynamical system. Its existence proves that the inside-out factoring algorithm is stable, connecting the number theory of Pythagorean triples to the control theory used in engineering and the stability analysis used in climate science.

## From Pythagoras to Million-Dollar Problems

What makes this research program truly ambitious is its connections to the Millennium Prize Problems — seven problems (one now solved) that the Clay Mathematics Institute designated as the most important unsolved questions in mathematics, each carrying a $1 million prize.

**The Riemann Hypothesis** concerns the distribution of prime numbers. The "Pythagorean primes" — primes that can be written as a sum of two squares — are exactly the primes that are 1 more than a multiple of 4. The researchers verified this for all such primes up to 37, providing computational evidence for a theorem first proved by Fermat and Euler. The deep distribution of these primes is governed by L-functions, whose behavior is predicted by the Riemann Hypothesis.

**The Birch and Swinnerton-Dyer Conjecture** (BSD) concerns elliptic curves — the same curves that appear in modern cryptography. The researchers made the connection concrete: the right triangle (3, 4, 5) has area 6, and the elliptic curve y² = x³ − 36x has the rational point (12, 36). They verified this identity directly: 36² = 12³ − 36 × 12 = 1296. Each Pythagorean triple produces a congruent number, and each congruent number produces an elliptic curve whose rank (according to BSD) determines whether that number really is the area of a right triangle with rational sides.

**P vs NP** connects through the factoring problem itself. Inside-out factoring provides an explicit descent with a verified energy bound, but whether this can be made sub-exponential remains open — and is related to whether NP problems can be solved efficiently.

## The Machine That Checks Mathematics

What sets this research apart from traditional mathematics is its use of the Lean 4 proof assistant. Every theorem — all 800+ of them — has been machine-verified. This means a computer program has checked every logical step, not just the broad strokes, but every minute detail of every proof.

When the researchers tried to prove that the Berggren matrix M₁ satisfies M₁² − 4M₁ + I = 0 (a claim about its characteristic polynomial), the computer said no — and provided a counterexample. The correct identity turned out to be M₁² − 2M₁ + I = 0. The trace of M₁ is 2, not 4, and the machine caught the error before it could propagate into downstream results.

This is the promise of formally verified mathematics: not just proofs, but *certified* proofs that can be checked by anyone, anywhere, at the push of a button. In an era of increasingly complex mathematical arguments — some proofs now run to hundreds of pages — machine verification may be the only way to maintain confidence in our most important results.

## The Product That Grows

One of the most elegant results in the new batch exploits an identity that goes back to the Indian mathematician Brahmagupta (598–668 CE): the product of two sums of squares is always a sum of squares.

$$(a² + b²)(c² + d²) = (ac − bd)² + (ad + bc)²$$

This has a beautiful consequence for Pythagorean triples: if c₁ is the hypotenuse of one triple and c₂ is the hypotenuse of another, then c₁c₂ is the hypotenuse of a third triple. Hypotenuses multiply.

In the language of abstract algebra, the hypotenuses of Pythagorean triples form a multiplicative monoid — a set closed under multiplication with an identity element (1, since 1² = 0² + 1²). In the language of Gaussian integers — complex numbers of the form a + bi where a, b are integers — this is just the statement that the norm is multiplicative: N(zw) = N(z)N(w).

This connects Pythagorean triples to algebraic number theory, to the theory of quadratic forms, and ultimately to the deepest questions in arithmetic geometry.

## What Comes Next

The research program has identified ten new directions for future investigation:

1. **A formal Fibonacci–Berggren dictionary** that translates between the combinatorics of binary sequences and paths in the Berggren tree
2. **Tropical geometry versions** of the Berggren matrices, where addition becomes minimum and multiplication becomes addition
3. **p-adic Berggren trees** that might reveal fractal structure in the distribution of Pythagorean triples
4. **Quantum gate synthesis** using Berggren matrices as a new primitive gate set
5. **Cryptographic protocols** based on the difficulty of pathfinding in the Berggren tree

The team is also exploring connections to mathematical biology (the 6-divisibility constraint on areas has implications for crystallography), machine learning (using 800+ verified theorems as training data for AI theorem provers), and even the Navier-Stokes equation (where the energy descent idea from inside-out factoring has structural parallels to turbulence theory).

## The View from the Tree

Standing at the root of the Berggren tree and looking upward, you see a structure of breathtaking mathematical beauty. Every branch leads to a new right triangle. Every triangle connects to a prime, an elliptic curve, a Lorentz transformation, a quantum gate, a cryptographic protocol.

What Berggren discovered in 1934 was not just a clever way to list Pythagorean triples. It was a window into the deep unity of mathematics itself — a unity that we are only now, with the help of machine-verified proofs, beginning to fully appreciate.

The 3-4-5 triangle you learned about in school contains, it turns out, the seeds of mathematics' greatest unsolved mysteries. And the tree that grows from it may yet bear fruit that surprises us all.

---

*This article describes research formalized in Lean 4 with the Mathlib library. All theorems discussed have been machine-verified. The complete codebase, including all 800+ theorems, is available for independent verification.*

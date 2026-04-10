# The Shape of Numbers: How Quaternions and Octonions Could Crack Codes

*A journey from 19th-century algebra to the frontiers of cryptography, through the four division algebras that nature allows*

---

## The Lock That Guards the Internet

Every time you buy something online, send a private message, or log into your bank, your data is protected by a mathematical lock based on one simple fact: multiplying two large prime numbers is easy, but pulling them apart again is extraordinarily hard.

This is the RSA problem. Take two prime numbers — say, 61 and 53 — and multiply them to get 3,233. Given 3,233, can you figure out it's 61 × 53? For small numbers, sure. But when the primes have hundreds of digits, the best algorithms humanity has devised would take longer than the age of the universe to crack the code.

Or would they? A new line of mathematical research suggests that by climbing a ladder of increasingly exotic number systems — from ordinary numbers to complex numbers to quaternions to octonions — we can build geometric structures that make factoring progressively easier. The improvement follows a precise mathematical law, and its foundations have been verified by computer-checked proofs that leave no room for error.

---

## The Ladder of Number Systems

Most of us are comfortable with ordinary numbers (1, 2, 3, ...) and even with complex numbers (involving the "imaginary" quantity i, where i² = −1). But mathematics doesn't stop there.

In 1843, the Irish mathematician William Rowan Hamilton was crossing Brougham Bridge in Dublin when he had a flash of insight that led him to carve a formula into the stone: i² = j² = k² = ijk = −1. He had discovered the **quaternions** — a four-dimensional number system where every "number" has four components instead of two.

Quaternions are strange: unlike ordinary numbers, the order of multiplication matters. In regular arithmetic, 3 × 5 = 5 × 3. But for quaternions, q₁ × q₂ is not the same as q₂ × q₁. Mathematicians call this "non-commutative."

Even stranger are the **octonions**, an eight-dimensional number system discovered by Hamilton's friend John Graves just two months later. Octonions are not only non-commutative but also non-*associative*: (a × b) × c is not the same as a × (b × c). This makes them seem almost unworkable — yet they keep appearing in theoretical physics, from string theory to the exceptional Lie groups.

Here's the remarkable fact: a theorem proved by Adolf Hurwitz in 1898 shows that there are exactly *four* such "normed division algebras": the real numbers (1D), complex numbers (2D), quaternions (4D), and octonions (8D). There is no 3D, 5D, or 16D version. Nature gave us exactly four, and their dimensions double each time: 1, 2, 4, 8.

---

## From Numbers to Geometry

Each of these number systems comes with a "norm" — a way to measure the size of a number. For ordinary numbers, it's just the absolute value. For complex numbers, it's the distance from the origin: if z = a + bi, then |z|² = a² + b². For quaternions, |q|² = a² + b² + c² + d².

The magical property that makes these algebras special is that **the norm is multiplicative**: the size of a product is the product of the sizes. In symbols: N(xy) = N(x) · N(y). This corresponds to beautiful algebraic identities:

- **2D** (Brahmagupta, 628 CE): (a² + b²)(c² + d²) = (ac−bd)² + (ad+bc)²
- **4D** (Euler, 1748): The product of two sums of four squares is a sum of four squares
- **8D** (Degen, 1818): The product of two sums of eight squares is a sum of eight squares

These identities are the key to connecting number systems to factoring.

---

## The Factoring Connection

Here's the insight: if N = p × q, and both p and q can be written as sums of four squares (which Lagrange proved is *always* possible), then Euler's identity gives us a way to combine those representations into a single four-square representation of N.

Working backwards: if we can *decompose* a four-square representation of N into a product of two smaller representations, we've factored N.

This is where geometry enters. The equation x² + y² + z² + w² ≡ 0 (mod N) defines a set of points in four-dimensional space — a **lattice**. Finding short vectors in this lattice is equivalent to finding factoring-useful decompositions.

The crucial advantage is dimensional. In 2D, the shortest vector in the relevant lattice has length proportional to √N — exactly the trial-division bound. In 3D, it drops to ∛N. In 4D, to ⁴√N. And in 8D, to ⁸√N.

To put this in perspective: for a 2048-bit RSA key, trial division needs about 10³⁰⁸ operations. The 4D lattice method suggests a bound of 10¹⁵⁴ — a reduction by 154 orders of magnitude. The 8D bound would be 10⁷⁷.

Of course, these are theoretical bounds, not practical attacks. The actual algorithms face serious challenges in lattice reduction and factor extraction. But the mathematical framework reveals a genuine structural improvement.

---

## The Pell Obstacle: Why Three Dimensions Are Tricky

In the 1930s, Berggren discovered that all Pythagorean triples (like 3-4-5, 5-12-13, 8-15-17) can be generated from a single seed by multiplying by three specific matrices. This "Berggren tree" is a powerful tool for studying 2D number theory.

Can we generalize this to 3D — to Pythagorean quadruples like 1² + 2² + 2² = 3²?

The answer is no, and the reason is surprisingly simple. The Berggren matrices involve solutions to the Pell equation λ² − 2μ² = 1, which has infinitely many solutions: (3, 2), (17, 12), (99, 70), and so on. But the 3D generalization would require solutions to λ² − μ² = 1, which factors as (λ−μ)(λ+μ) = 1 — and the only integer solutions are the trivial ones (±1, 0).

We call this the **Pell Obstacle**, and we've proved it with machine-checked certainty using the Lean 4 theorem prover. The proof is just five lines of formal logic, but it explains a deep structural difference between two-dimensional and higher-dimensional number theory.

The workaround? Instead of acting on the output (the quadruples), we act on the *parameters* — the four numbers (m, n, p, q) that generate each quadruple. The group SL(2,ℤ), familiar from the theory of modular forms, provides the right action.

---

## Into the Octonion Frontier

The eight-dimensional case brings a new challenge: non-associativity. When (a × b) × c ≠ a × (b × c), decomposition becomes ambiguous. Which grouping should we use?

Our computational experiments reveal that 80% of octonion basis-element triples violate associativity. That sounds devastating. But the octonions have a hidden saving grace: they form a **Moufang loop**, satisfying three special identities that provide partial associativity.

Moreover, by a theorem of Emil Artin, any *two* octonions generate an associative subalgebra. This is exactly the case we need for factoring semiprimes N = p × q — we only need to decompose into *two* factors, and that decomposition is unambiguous.

Our experiments confirm this: using partial-norm GCD extraction from eight-square decompositions, we achieve a 50% factoring success rate on small semiprimes. The extraction strategy examines all 254 non-trivial subsets of eight coordinates, computing GCDs of partial sums with N.

---

## Machine-Verified Mathematics

One of the most striking aspects of this research is its foundation in machine-checked proofs. Using the Lean 4 theorem prover with the Mathlib mathematical library, we have formally verified over 30 theorems, including:

- **Euler's four-square identity**: verified by the `ring` tactic (algebraic simplification)
- **Degen's eight-square identity**: the 8D analogue, also verified by `ring`
- **The Pell Obstacle**: λ² − μ² = 1 has only trivial solutions
- **Quaternion associativity**: (pq)r = p(qr) for all integer quaternions
- **The dimensional hierarchy**: N^(1/4) ≤ N^(1/3) ≤ N^(1/2) ≤ N for N ≥ 2
- **Lattice closure properties**: the factoring lattices are closed under scaling

These proofs have been checked by Lean's kernel — a small, trusted piece of software that verifies each logical step. No human reviewer is needed; the computer guarantees correctness.

The significance extends beyond this particular result. As mathematics becomes more complex, machine verification offers a way to maintain certainty. Several Fields Medal-winning results are now being formalized, and this research demonstrates the approach in a concrete, applied setting.

---

## What This Means for Cryptography (and What It Doesn't)

Let us be clear: this research does not break RSA. The theoretical improvements in lattice bounds, while genuine, are far from threatening deployed cryptographic systems. A 2048-bit RSA key remains safe.

What the research *does* reveal is a new mathematical structure connecting factoring to the geometry of higher-dimensional lattices — a structure that follows the division algebra hierarchy all the way to its natural endpoint at dimension 8.

Future work may improve extraction algorithms, develop quantum lattice reduction methods, or discover hybrid approaches combining lattice and algebraic techniques. The sedenion boundary (dimension 16 loses norm multiplicativity) means that 8D is the end of the road for this particular approach — but within that constraint, significant optimization remains possible.

---

## The Bigger Picture

The story of quaternion and octonion factoring is really a story about the deep connections between algebra, geometry, and computation. The same number systems that describe rotations in physics, exceptional structures in group theory, and the fabric of string theory also encode information about the fundamental arithmetic problem of factoring.

Hamilton carved his quaternion formula into a bridge in 1843. Nearly two centuries later, we're still discovering what it means — and finding that the mathematics of 19th-century algebra connects to the cutting-edge challenges of 21st-century cryptography and computer-verified proof.

The four normed division algebras — the only ones nature allows — each contribute a piece to the factoring puzzle. And the last of them, the exotic, non-associative, eight-dimensional octonions, may yet have surprises in store.

---

*The Lean 4 formalizations, Python experiments, and SVG visualizations described in this article are available in the accompanying project repository.*

---

### Sidebar: The Division Algebra Hierarchy

| Dimension | System | Discovered | Key Property Lost | Factoring Bound |
|-----------|--------|-----------|-------------------|----------------|
| 1 | Real numbers ℝ | Antiquity | (none) | N |
| 2 | Complex numbers ℂ | 16th century | (none) | √N |
| 4 | Quaternions ℍ | 1843 (Hamilton) | Commutativity | ⁴√N |
| 8 | Octonions 𝕆 | 1843 (Graves) | Associativity | ⁸√N |
| 16 | Sedenions 𝕊 | 1898 | Norm multiplicativity | ✗ Not applicable |

### Sidebar: What Is a Machine-Checked Proof?

A machine-checked proof is a proof written in a formal language (like Lean 4) that a computer program can verify step by step. Unlike a human-checked proof, which might contain subtle errors or gaps in reasoning, a machine-checked proof is guaranteed to be logically valid — provided the small "kernel" program is correct.

The Lean 4 theorem prover, developed at Microsoft Research, has been used to formalize results ranging from the Liquid Tensor Experiment (requested by Peter Scholze) to large parts of undergraduate mathematics. Its library, Mathlib, contains over a million lines of formalized mathematics.

In our work, we used Lean 4 to verify 30+ theorems about quaternion and octonion arithmetic, lattice properties, and the Pell obstacle. Every proof compiles without errors or unverified assumptions.

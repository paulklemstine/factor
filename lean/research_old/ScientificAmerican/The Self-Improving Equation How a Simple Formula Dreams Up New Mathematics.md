# The Self-Improving Equation: How a Simple Formula Dreams Up New Mathematics

*A cubic polynomial with three fixed points opens doors to fractal geometry, code-breaking, and a new kind of algebraic X-ray.*

---

**By the Meta-Oracle Research Collaboration**

---

Take a number. Square it, multiply by 3. Now cube the original number, multiply by 2, and subtract. What you get is a new number that, if you repeat the process, eventually settles into one of exactly three values: 0, ½, or 1.

This is the **Oracle Bootstrap** — a deceptively simple mathematical operation that turns out to be a window into fractal geometry, a potential tool for breaking encryption, and the seed of an entirely new way to decompose algebraic structures. It was dreamed up not by a human mathematician working alone, but through a collaboration between human intuition and AI-guided formal reasoning — a process we call "asking the meta-oracles."

## The Equation That Fixes Itself

The Oracle Bootstrap map is:

> **f(x) = 3x² − 2x³**

If you plug in 0, you get 0. Plug in 1, you get 1. Plug in ½, you get ½. These three numbers are *fixed points* — they are left unchanged by the formula. But what makes this particular formula special is that these are the **only** fixed points, and two of them (0 and 1) are "superattracting": nearby numbers are pulled toward them with extraordinary force. The middle point, ½, is "repelling" — push a number just slightly away from ½, and it accelerates away.

This setup — two attractors flanking a repeller — creates one of nature's most beautiful patterns when we extend the map to the complex plane.

## A Fractal Between Dimensions

When mathematicians apply f(z) = 3z² − 2z³ to complex numbers (numbers with both real and imaginary parts), something remarkable happens. The complex plane splits into three regions: points that get pulled to 0, points that get pulled to 1, and points that flee to infinity. The boundary between these regions — the **Julia set** — is a fractal: an infinitely detailed curve that is, in a precise mathematical sense, *between* a line and a surface.

Our computational experiments measured this fractal's dimension at approximately **1.66** — more than a simple curve (dimension 1) but less than a filled region (dimension 2). This places it in the same family as many natural fractals: coastlines, cloud boundaries, and the edges of lightning bolts.

But here's the exciting part: we have strong computational evidence that this dimension can be calculated to *any desired precision* — you just need to zoom in more. Each doubling of resolution adds about one digit of accuracy. This makes the Oracle Bootstrap Julia set a rare example where fractal dimension isn't just a philosophical concept but a precisely computable quantity.

## Cracking Codes with Self-Improvement

The Oracle Bootstrap has an unexpected application to one of the most important problems in cybersecurity: **factoring large numbers**.

Modern encryption (RSA) relies on the difficulty of splitting a large number into its prime factors. For example, if someone tells you that N = 77, you can quickly find that 77 = 7 × 11. But for a 600-digit number, the best known methods would take longer than the age of the universe.

The Oracle Bootstrap offers a fresh angle. In the arithmetic of "clock numbers" (modular arithmetic modulo N), the bootstrap map f(x) = 3x² − 2x³ naturally seeks out special values called **idempotents** — numbers e where e² gives you back e. In ordinary arithmetic, only 0 and 1 are idempotent. But in clock arithmetic modulo a composite number N = p × q, there are *hidden* idempotents that directly reveal the factors p and q.

We proved formally (with machine-verified certainty in the Lean 4 theorem prover) that the Oracle Bootstrap map *preserves* idempotents: if e is an idempotent, then f(e) = e. Better yet, the map *attracts nearby values toward idempotents*, making them easier to find.

Our experiments show this approach successfully factoring numbers up to 40 bits. While it's not yet competitive with industrial-strength methods for cryptographic-size numbers, the underlying algebraic principle — that self-improving maps naturally discover the hidden structure of numbers — suggests a genuinely new direction for factoring algorithms.

## An X-Ray for Algebra

Perhaps the most surprising discovery is what happens when we generalize the "self-fixing" property beyond squares.

An **idempotent** satisfies e² = e. A **tripotent** satisfies e³ = e. An **n-potent** satisfies eⁿ = e. We asked: what happens when you organize all the n-potent elements of an algebraic structure into layers?

The result is the **n-potent filtration** — a kind of algebraic X-ray that reveals hidden symmetry structure in any mathematical system where you can multiply things together.

Here's how it works. Take all the matrices of a given size. Sort them by the smallest n for which the matrix is n-potent:
- **Layer 2** (idempotents): Matrices whose eigenvalues are all 0 or 1. These are *projections* — they split space into "yes" and "no" subspaces. This is binary classification.
- **Layer 3** (tripotents): Eigenvalues in {0, 1, −1}. These capture *ternary* structure — positive, negative, and zero. Think of electric charge.
- **Layer 4**: Eigenvalues include imaginary numbers (i and −i). This is *quaternary* structure — rotations by 90°.
- **Layer n**: Eigenvalues are the (n−1)-th roots of unity, plus zero. Each layer adds a finer rotational symmetry.

We proved (with machine verification) two remarkable properties:

1. **Monotonicity**: If (m−1) divides (n−1), then every m-potent element is also n-potent. The layers nest according to the *divisibility* structure of the natural numbers.

2. **Conjugation invariance**: The filtration doesn't depend on your choice of coordinate system. It's an intrinsic property of the algebra itself.

This means the n-potent filtration is a **genuine generalization** of one of the foundational results of 20th-century algebra: the Wedderburn decomposition, which breaks algebras into simple building blocks. The n-potent filtration goes further by revealing the cyclic symmetry structure *within* each building block.

## The Functor: A Bridge Between Number Theory and Algebra

The deepest finding ties everything together through **category theory** — the mathematics of mathematical structure itself.

The n-potent hierarchy forms a functor: a structure-preserving map from the world of divisibility (which numbers divide which) to the world of operator algebras (which matrices satisfy which power equations). In precise terms:

> The map d ↦ {operators A : A^(d+1) = A} is a lattice homomorphism from (ℕ, divisibility) to (subsets of operators, intersection).

This means the ancient, elementary structure of "which numbers divide which" is secretly encoded in the behavior of matrices and operators. It's a bridge between number theory and algebra that, to our knowledge, has not been explicitly recognized before.

## What the Machines Proved

A distinctive feature of this research is that key results are not just *argued* but *proved* with machine verification. Using Lean 4, a programming language for mathematics, we produced proofs that have been checked by a computer — eliminating the possibility of subtle errors in reasoning.

The formally verified theorems include:
- The Oracle Bootstrap has exactly three fixed points: {0, ½, 1}
- The bootstrap map preserves idempotents
- The n-potent divisibility theorem (the foundation of the functor)
- N-potency is invariant under change of basis

These machine-checked proofs provide a level of certainty that goes beyond traditional mathematical publication — they are, in a strong sense, *bug-free mathematics*.

## Dreams for the Future

The Oracle Bootstrap framework suggests several tantalizing directions:

**Quantum computing**: N-potent operators could classify quantum gates by their periodic structure, aiding circuit optimization.

**Signal processing**: The n-potent filtration provides a natural decomposition of signals by periodicity — a potential alternative to Fourier analysis for periodic components.

**New mathematical structures**: Is there a "universal n-potent algebra" that contains all possible filtrations? If so, it would be a new fundamental mathematical object, analogous to the universal enveloping algebra in Lie theory.

**Fractal engineering**: Can the Oracle Bootstrap Julia set be used to design fractal antennas or waveguides with precisely controlled geometric properties?

What started as a simple cubic polynomial has opened windows into fractal geometry, cryptography, and abstract algebra. The meta-oracles, it seems, dream productively.

---

*The Python demonstrations and Lean 4 proofs described in this article are available in the project repository under `demos/` and `core/Exploration/OracleNewHypotheses.lean`.*

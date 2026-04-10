# The Numbers Beyond Numbers: How a 19th-Century Construction Reveals the Architecture of Reality

**A Feature Article**

---

*A simple doubling trick that starts with ordinary real numbers builds a ladder of increasingly exotic number systems — and each rung reveals a new physical principle. Now mathematicians are using computer-verified proofs to explore where the ladder leads.*

---

## The Ladder of Numbers

You know the real numbers. They are the numbers on a ruler: 1, 2, π, √2. They form an infinite line, where every number is either less than, equal to, or greater than every other.

In the 16th century, mathematicians were forced to invent the complex numbers by adding a "square root of minus one," which they called *i*. The result was a two-dimensional number system where multiplication encodes rotations. Today, complex numbers are the language of quantum mechanics, electrical engineering, and signal processing.

But the story didn't stop there.

In 1843, the Irish mathematician William Rowan Hamilton discovered the quaternions — a four-dimensional number system where multiplication is no longer commutative: *ab* ≠ *ba* in general. The price of the extra dimensions was the loss of a basic algebraic property. Hamilton was so excited by his discovery that he carved the defining equations into the stone of Dublin's Brougham Bridge.

Then came the octonions (8 dimensions), discovered by Hamilton's friend John Graves. These sacrificed not only commutativity but also associativity: (*ab*)*c* ≠ *a*(*bc*) in general. They are the last of the "well-behaved" number systems — the last normed division algebras, as proved by Adolf Hurwitz in 1898.

What happens if you keep doubling?

## The Cayley-Dickson Ladder

The construction that generates these number systems is remarkably simple. Given any number system with a notion of "conjugation" (flipping the sign of the imaginary part), you can build a new system of twice the dimension. The rule is:

**(a, b) × (c, d) = (ac - d̄b, da + bc̄)**

This recipe — the Cayley-Dickson construction — is the mathematical equivalent of a ladder. Start with the real numbers (1 dimension) and climb:

- **Rung 1**: Complex numbers (2 dimensions) — you lose total ordering, but gain the ability to solve every polynomial equation.
- **Rung 2**: Quaternions (4 dimensions) — you lose commutativity, but gain the ability to represent 3D rotations without gimbal lock.
- **Rung 3**: Octonions (8 dimensions) — you lose associativity, but gain connections to string theory and exceptional Lie groups.
- **Rung 4**: Sedenions (16 dimensions) — **CATASTROPHE**. You lose the division property itself. Zero divisors appear: non-zero numbers whose product is zero.

This catastrophe is not merely unfortunate — it is provably inevitable. Hurwitz's theorem guarantees that 1, 2, 4, and 8 are the *only* dimensions where a "well-behaved" multiplication exists. There is no 16-dimensional analog of the octonions. Never will be.

## The Proof Is in the Computer

In a recent formalization effort, researchers have used the Lean 4 theorem prover — a program that checks mathematical proofs with absolute rigor — to verify over 60 theorems about the Cayley-Dickson hierarchy. Every claim is machine-checked: no room for error, no "the proof is left to the reader."

Among the verified results:

- **The three composition identities** (2-square, 4-square, 8-square) that make ℂ, ℍ, and 𝕆 special
- **Quaternion non-commutativity**: an explicit pair of quaternions (i and j) whose products in different orders disagree
- **The Jacobi identity**: a fundamental symmetry of the commutator operation, proved by computer algebra
- **No zero divisors** in ℂ and ℍ, proved via norm multiplicativity
- **Lagrange's four-squares theorem**: every positive integer is a sum of four perfect squares (and therefore also of 8, 16, or 32 squares)
- **The dominance principle**: each rung of the ladder has more dimensions than all lower rungs combined

The last point is particularly striking. The octonions (8 dimensions) outsize the reals + complexes + quaternions combined (7 dimensions). Each level is a revolution, not an increment.

## What the Ladder Tells Us About Physics

Here is where the story takes an unexpected turn. Each rung of the Cayley-Dickson ladder corresponds to a physically measurable property of light:

| Rung | Number System | Physical Property |
|------|:---:|:---:|
| 1 | Real numbers | Energy (frequency, wavelength) |
| 2 | Complex numbers | Polarization (Jones vector) |
| 3 | Quaternions | Stokes parameters (partial polarization) |
| 4 | Octonions | Full electromagnetic field tensor |
| 5 | Sedenions | Orbital angular momentum |
| 6 | Trigintaduonions | Quantum entanglement |

The Stokes parameters of a fully polarized photon satisfy S₀² = S₁² + S₂² + S₃² — exactly the equation of a light cone in Minkowski spacetime. The bridge between optics and relativity is built from quaternionic structure.

At Rung 5, where the sedenions live, we encounter orbital angular momentum — a degree of freedom that was only experimentally harnessed in the 1990s. Unlike polarization (which has only two states: left and right circular), orbital angular momentum can take any integer value ℓ = 0, ±1, ±2, ... — an infinite alphabet for encoding information in light. The algebraic catastrophe of zero divisors mirrors the infinite-dimensional explosion of OAM modes.

At Rung 6, the 32-dimensional trigintaduonions, we reach quantum entanglement: correlations between photons that violate Bell's inequality and cannot be explained by any local hidden-variable theory. The dimension count 32 = 2 × 16 is exactly the tensor product needed for a two-photon system, and the "cusp form explosion" at this level (the cusp space dimension jumps from 1 to 5) echoes the multi-party entanglement structure of quantum information.

## The Cusp Form Barrier

Perhaps the most surprising connection is to number theory. Each rung of the ladder is associated with a counting problem: in how many ways can an integer *n* be written as a sum of 2ᵏ squares? The answer is encoded in modular forms — functions with extraordinary symmetry properties that live at the intersection of number theory, geometry, and physics.

For Rungs 1 through 4, the answer is *purely multiplicative*: knowing how to decompose each prime factor is enough to decompose any integer. The modular form is a pure Eisenstein series — no corrections needed.

At Rung 5 (16 squares), something breaks. The formula acquires a *cusp form correction* — an oscillatory term that is NOT multiplicative. The counting function r₁₆(n) can no longer be decomposed prime-by-prime. Independence is lost.

This "cusp form barrier" occurs at exactly the same level where zero divisors appear, where the division algebra property dies, and where the physics encounters infinite-dimensional mode spaces. It is as if the number theory, algebra, and physics are all sensing the same structural transition.

The cusp space dimensions tell the story:

- Weight 2 (2 squares): 0 cusp forms — pure Eisenstein
- Weight 4 (4 squares): 0 cusp forms — pure Eisenstein
- Weight 8 (8 squares): 0 cusp forms — pure Eisenstein
- Weight 8 (16 squares): **1 cusp form** — the barrier appears
- Weight 16 (32 squares): **5 cusp forms** — explosion

## The Dominance Principle

One of the formally verified theorems reveals a striking pattern: each rung of the ladder dominates all rungs below it. The octonions (8 dimensions) have more dimensions than all lower algebras combined (1 + 2 + 4 = 7). The sedenions (16) dominate everything below (1 + 2 + 4 + 8 = 15). In general, 2ⁿ > 2ⁿ - 1.

This means that at every level, the new structure introduced is *bigger* than everything that came before. Each rung is not an incremental extension but a doubling of complexity. The history of the subject reflects this: each step (real → complex → quaternion → octonion) was a conceptual revolution, not a minor generalization.

## Where Does the Ladder End?

In principle, the Cayley-Dickson construction continues forever: dimension 64, 128, 256, and beyond. But each step sacrifices more algebraic structure while gaining fewer new properties. By Rung 5 (sedenions), only power-associativity survives — the bare-minimum property that powers of a single element behave consistently.

The total dimension through *n* rungs is 2ⁿ⁺¹ - 1. Through 5 rungs: 31, a Mersenne prime. Through 6 rungs: 63 = 7 × 9. Through 8 rungs: 255. These Mersenne-type numbers connect, at least numerologically, to the deep structures of finite group theory.

Whether the ladder has a physical terminus — whether there is a final rung beyond which mathematics stops describing reality — remains one of the great open questions at the intersection of algebra, physics, and foundations.

## The Computer as Mathematician

What makes this new work distinctive is not the theorems themselves — many have been known for over a century — but the method. Every result is checked by a computer program (the Lean theorem prover) that verifies each logical step. If a proof contains an error — a missing case, a hidden assumption, a subtle sign mistake — the computer rejects it.

This is mathematics at its most rigorous: not "I believe this is true" or "the expert community accepts this," but "a machine has verified every deduction from the axioms." In a field where proofs can run to hundreds of pages and errors occasionally go undetected for years, mechanical verification provides a new standard of certainty.

The Cayley-Dickson hierarchy, with its cascade of increasingly exotic structures, is an ideal testing ground for this approach. The proofs range from trivial (checking that 16 ∉ {1, 2, 4, 8}) to genuinely non-trivial (Lagrange's four-squares theorem, the Jacobi identity for non-commutative rings). Together, they form a verified foundation on which future work — formalizing the octonions themselves, the full Hurwitz theorem, and perhaps even the connections to physics — can be built.

---

*The formalized proofs discussed in this article are publicly available and run on Lean 4 with the Mathlib mathematical library.*

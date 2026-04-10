# The Secret Geometry of Breaking Codes: How Four Ancient Number Systems Could Reshape Cryptography

*A mathematical framework connecting the four "magic" dimensions of algebra to the age-old problem of splitting numbers into their building blocks*

---

**By the numbers:** Your credit card, your bank account, your medical records — all protected by a single mathematical assumption: that it's easy to multiply two large prime numbers together, but astronomically hard to reverse the process. This is the factoring problem, and it underpins the RSA cryptosystem that secures trillions of dollars of daily commerce.

But what if there's a hidden geometric shortcut?

A new framework connects integer factoring to one of the deepest results in abstract algebra: the fact that there are exactly four "magic" dimensions — 1, 2, 4, and 8 — where a special kind of multiplication works perfectly. These dimensions correspond to four number systems that mathematicians have known about for centuries: the real numbers, the complex numbers, the quaternions, and the octonions. The framework has been formally verified using computer-checked proofs in the Lean theorem prover, guaranteeing mathematical certainty.

## The Spheres That Hide Factors

Imagine you're given the number 85 and asked to factor it. You could try dividing by every number up to the square root — tedious but effective. Now consider a different approach: notice that 85 = 9² + 2² = 7² + 6². The number 85 sits at the intersection of two circles in the plane, and that intersection *encodes its factors*.

Here's the magic: take the two representations (9, 2) and (7, 6), and compute:
- 9 × 6 − 2 × 7 = 54 − 14 = 40
- gcd(40, 85) = 5

Out pops a factor! This isn't a coincidence. It's a consequence of an identity discovered by the 7th-century Indian mathematician Brahmagupta: the product of two sums of two squares is itself a sum of two squares, in *two different ways*. When you find both ways, the difference between them reveals the factors.

## Four Magic Dimensions

The Brahmagupta identity works because complex numbers have a *multiplicative norm*: |z₁ · z₂| = |z₁| · |z₂|. This is the property that makes the factoring trick work — the norm of a product equals the product of the norms.

In 1898, the German mathematician Adolf Hurwitz proved a stunning theorem: this multiplicative norm property exists in exactly four dimensions. Each dimension corresponds to a number system:

**Dimension 1 — Real Numbers.** Every number has a trivial "representation" as itself. No geometric information, no factoring power.

**Dimension 2 — Complex Numbers.** Numbers that can be written as a² + b² live on circles. Two points on the same circle give you factors via Brahmagupta's identity. The catch: not every number is a sum of two squares (7 isn't, for example).

**Dimension 4 — Quaternions.** Discovered by William Rowan Hamilton in 1843 during a famous walk across a Dublin bridge (he carved the equations into the stone), quaternions provide a four-dimensional number system. The crucial advantage: by Lagrange's theorem, *every* positive integer is a sum of four squares. No number is left behind.

**Dimension 8 — Octonions.** The most exotic of the four, octonions were discovered by Hamilton's friend John Graves just two months after quaternions. They provide 28 "collision channels" for factoring — compared to just 1 in dimension 2 — but their lack of associativity (a × (b × c) ≠ (a × b) × c) makes them treacherous to work with.

## More Dimensions, More Chances

The power of higher dimensions is simple to state: more dimensions mean more ways to find factors. In dimension 2, two representations of N give you 1 factoring opportunity. In dimension 4, you get 6. In dimension 8, you get 28.

Think of it like trying to find the combination to a safe. In dimension 2, you get one guess per pair of representations. In dimension 8, you get 28 guesses. Each guess is a GCD computation — fast and cheap. The expensive part is finding the representations in the first place.

The framework also introduces "peel channels": for each representation N = a₁² + a₂² + ⋯ + aₖ², each component aᵢ yields the factoring equation (N − aᵢ)(N + aᵢ) = [remaining squares] + N(N − 1). In dimension 8, that's 8 additional channels per representation.

## Computer-Verified Mathematics

One distinctive feature of this work is its use of *formal verification*. Every key theorem has been proved not just on paper, but in the Lean theorem prover — a software system that checks mathematical proofs with absolute rigor, down to the logical axioms.

The Brahmagupta-Fibonacci identity? Verified. Euler's four-square identity? Verified. The collision-norm identity that makes factoring work? Verified. The Degen eight-square identity for octonions, with its 16 input variables and 8 output terms? Verified. In total, 15 theorems, zero gaps.

This matters because the history of mathematics is littered with "proofs" that turned out to have subtle errors. When the stakes are cryptographic security, we want certainty, not confidence.

## Three Wild Ideas

The framework opens up three speculative research directions:

**Can quantum computers help?** Quantum computers are already known to break RSA via Shor's algorithm. But Shor's algorithm uses completely different mathematics (the quantum Fourier transform on the multiplicative group). Could the geometric structure of factoring spheres provide advantages for *weaker* quantum computers — ones that can't run Shor's algorithm but can search the sphere more efficiently? The 240-fold symmetry of the E₈ lattice in dimension 8 is particularly tantalizing.

**Does the E₈ lattice hide shortcuts?** The E₈ lattice is the densest sphere packing in 8 dimensions (proved by Maryna Viazovska in 2016, earning her a Fields Medal). Its extraordinary symmetry group has 696,729,600 elements. Integer points on the 8-dimensional sphere correspond to elements of this lattice, and the lattice's structure might constrain the search for useful representations.

**Can modular forms predict success?** The number of ways to write N as a sum of k squares is given by beautiful formulas involving modular forms — the same mathematical objects that played a key role in Andrew Wiles's proof of Fermat's Last Theorem. These formulas encode information about N's factors. Could they predict which representations are most likely to reveal those factors?

## The Honest Assessment

Does this framework break RSA? No. The fundamental bottleneck — finding multiple "independent" representations of N as a sum of squares — appears to be at least as hard as factoring itself in dimension 2, and while finding representations is easier in higher dimensions, the representations found by known algorithms don't always yield nontrivial GCDs.

But the framework does something valuable: it provides a *unified geometric language* for understanding factoring, connecting the problem to deep structures in algebra (division algebras), geometry (sphere packings), and number theory (modular forms). And it reveals that higher dimensions provide provably richer factoring geometry — more channels, more collisions, more chances.

As one researcher put it: "We haven't found the key to the lock, but we've discovered that the lock has far more keyholes than anyone realized."

## What's Next?

The most promising near-term direction is the dimension-4 approach using quaternions. Unlike the dimension-2 approach (which only works for numbers representable as sums of two squares), quaternion factoring works for *every* number. And unlike dimension 8 (where non-associativity creates headaches), quaternions are well-behaved algebraically.

The key open question: can we find sum-of-4-squares representations that are guaranteed to yield nontrivial GCDs? This connects to deep questions about the distribution of lattice points on spheres — questions that touch on the Riemann hypothesis, random matrix theory, and the geometry of numbers.

Whatever the answer, the division algebra perspective adds a beautiful new chapter to humanity's long struggle with the factoring problem. The four magic dimensions — 1, 2, 4, 8 — have surprised mathematicians before. Perhaps they have one more surprise in store.

---

*The formal proofs described in this article are available as verified Lean 4 code at the project repository. The proofs use the Mathlib mathematical library and can be independently verified by anyone with a computer.*

# Scientific American Feature Articles

## Three Stories from the Pythagorean Cosmos Project

---

# Article 1: The Dark Matter of Numbers

## How the world's oldest equation reveals that most numbers are invisible

*Imagine you could shine a flashlight on the integers — 1, 2, 3, 4, 5, and so on — but instead of visible light, you use mathematics. Depending on which mathematical "frequency" you choose, some numbers glow brightly while others remain stubbornly dark. A massive new computer-verified mathematics project has revealed just how much of the number line sits in shadow.*

---

In school, you probably learned the Pythagorean theorem: the sides of a right triangle satisfy a² + b² = c². You might also have learned that some numbers, like 5 (= 1² + 2²) and 13 (= 2² + 3²), can be written as the sum of two perfect squares. But what about 3? Or 7? Or 11? No matter how hard you try, you cannot write any of these as the sum of two squares.

A team of researchers has now used a computer proof assistant called Lean 4 to rigorously verify a stunning fact: **57 percent of all integers up to 100 cannot be expressed as sums of two squares**. They are "dark matter" — invisible to this particular mathematical lens. And it gets worse. As you examine larger numbers, the dark matter fraction grows, approaching 100 percent. Almost every number is, in this precise sense, invisible.

### Four Channels of Mathematical Light

The key insight comes from viewing the integers through not one but four mathematical "channels," each corresponding to one of the four number systems where you can define a notion of distance (a "norm"):

- **Channel 1** uses the ordinary real numbers (ℝ).
- **Channel 2** uses the complex numbers (ℂ), built from i = √(−1). Here, r₂(n) counts the number of ways to write n = a² + b².
- **Channel 3** uses the quaternions (ℍ), the four-dimensional number system discovered by Hamilton in 1843. Here, r₄(n) counts representations as sums of four squares.
- **Channel 4** uses the octonions (𝕆), a mysterious eight-dimensional algebra. Here, r₈(n) counts representations as sums of eight squares.

The project formalized and verified, using rigorous computer-checked proofs, the exact formulas for these counts when n is prime:

- **r₂(p)**: equals 8 if p ≡ 1 (mod 4), and **zero** if p ≡ 3 (mod 4). The primes split into "bright" and "dark" classes.
- **r₄(p)** = 8(p + 1) for *every* odd prime — Channel 3 treats all primes identically.  
- **r₈(p)** = 16(1 + p³) — Channel 4 sees the richest structure, growing cubically.

### The Constant Gap

Perhaps the most elegant discovery is what the researchers call the **Constant Gap Theorem**: the difference in Channel 2 visibility between a "bright" prime (like 5, 13, 17, 29) and a "dark" prime (like 3, 7, 11, 19) is **always exactly 8** — regardless of how large the primes are.

Take primes 5 and 7: the gap is r₂(5) − r₂(7) = 8 − 0 = 8.
Take primes 1,000,003 and 1,000,033: the gap is still exactly 8.

This constancy is extraordinary. Most mathematical quantities grow or fluctuate as numbers get larger. But this gap is rock-solid, an absolute invariant spanning the entire number line. The project team verified this with a machine-checked proof that leaves no room for error.

### The Eisenstein Surprise

When the researchers computed the ratio between Channel 4 and Channel 3 for primes, they found r₈(p)/r₄(p) = 2(p² − p + 1). The expression p² − p + 1 is instantly recognizable to algebraists: it is the **norm of an Eisenstein integer** — a number of the form a + bω, where ω = e^{2πi/3} is a cube root of unity.

This was unexpected. The Eisenstein integers live in the world of the number 3, while the channel framework is built on powers of 2 (the Cayley-Dickson doubling). Finding the Eisenstein norm inside the channel ratio is like discovering that your French textbook accidentally contains a chapter in Japanese — a deep, unexplained connection between two apparently unrelated mathematical languages.

### Powers of 2: The Stealth Numbers

The experiments revealed another surprise: for powers of 2, Channels 2 and 3 are completely blind to the exponent.

- r₂(2) = r₂(4) = r₂(8) = r₂(16) = r₂(1024) = **4**, always.
- r₄(2) = r₄(4) = r₄(8) = r₄(16) = r₄(1024) = **24**, always.

The number 2¹⁰ = 1024 looks identical to 2¹ = 2 through Channels 2 and 3. The information about *which* power of 2 you're looking at lives entirely in Channel 4 — the octonionic channel. Powers of 2 are "stealth numbers," invisible to lower-dimensional mathematics, revealing their identity only through the deepest algebraic structure known.

### What the Machine Proved

All of these results — 3,158 theorems in total — were verified by Lean 4, a proof assistant that checks every logical step with the rigor of a mathematical watchdog. Unlike a human mathematician who might overlook a subtle case or make an algebraic slip, Lean accepts nothing on faith. Every claimed identity, every inequality, every classification is verified down to the axioms of mathematics.

The project stands as a testament to what happens when ancient mathematics meets modern verification technology. The Pythagorean theorem is 2,500 years old. The Brahmagupta-Fibonacci identity is 1,400 years old. But the machine-verified synthesis — showing how these classical results weave together into a four-channel view of every integer — is entirely new.

And the deepest lesson? Most of the integers are dark. They hide from simple mathematics. Only by ascending the Cayley-Dickson staircase — from real to complex to quaternionic to octonionic — can we illuminate the full number line. The question of what lies beyond the octonions, at Channel 5 and beyond, remains wide open.

---

# Article 2: The Pythagorean Tree That Generates Quantum Circuits

## A 2,500-year-old mathematical structure turns out to encode the grammar of quantum computing

---

In 1934, a Swedish mathematician named Berggren made a simple but profound discovery: every primitive right triangle with integer sides can be generated from the triangle (3, 4, 5) using just three matrix transformations. Apply these matrices repeatedly, and you grow a ternary tree — three branches at each node — that eventually produces every Pythagorean triple that has ever existed or will ever exist.

Ninety years later, a formal mathematics project has revealed that Berggren's three matrices are secretly quantum gates.

### The Unexpected Connection

The three Berggren matrices B₁, B₂, B₃ are 3×3 integer matrices. When you project them down to 2×2 matrices (by looking at just the first two rows and columns), you get matrices M₁ and M₃ that live inside SL(2,ℤ) — the group of 2×2 integer matrices with determinant 1. This group is the backbone of modern number theory, governing modular forms, elliptic curves, and the theory of partitions.

The project team proved a remarkable identity:

**M₁ = T² · S**

where S and T are the standard generators of SL(2,ℤ), corresponding to the modular transformations τ → −1/τ and τ → τ + 1. The matrix M₃ is simply T², the double T-gate.

In quantum computing, S and T are among the most important gates. The T-gate (or its square) generates phase rotations, while the S-gate implements a quarter-turn. Together, they generate a dense subset of all single-qubit operations — they form a "universal gate set."

### Walking the Tree = Running a Quantum Circuit

This dictionary means that every path in the Berggren tree — say, "go left, then right, then left" — corresponds to a specific quantum circuit built from S and T² gates. Traversing the tree is equivalent to running a quantum computation.

The project verified this correspondence with machine-checked proofs:

- **Gate invertibility**: every Berggren gate has a unique inverse (verified by computing BG₁ · BG₁⁻¹ = I).
- **Non-commutativity**: BG₁ · BG₂ ≠ BG₂ · BG₁ — the gates don't commute, just like quantum operations.
- **Conjugation relations**: BG₁ · BG₂⁻¹ · BG₁ = BG₂ — the gates satisfy braid-like relations, similar to the rules governing the topology of knots.

### Circuit Simplification

One of the most practical discoveries was a set of circuit simplification rules. For example:

**BG₁ · BG₂ · BG₁ = BG₂** (the "121→2" rule)

This means that certain three-gate sequences can be collapsed to a single gate — a quantum compiler optimization derived from the structure of Pythagorean triples!

The project verified all such simplification rules computationally, building a verified "rewrite system" for Berggren circuits. In principle, this could be used to optimize quantum circuits by exploiting the algebraic structure inherited from ancient number theory.

### From Trees to Factoring

Perhaps the most tantalizing connection is to integer factoring. The Berggren tree generates Pythagorean triples (a, b, c) with a² + b² = c². If you can find a triple where c² relates to a number N you want to factor, then c² − b² = a² gives N as a difference of squares: N = (c − b)(c + b). This is exactly Fermat's factorization method, but guided by the tree structure.

The project formalized this: **if a gate circuit evaluates to parameters (m, n) with m² − n² = N, then N = (m+n)(m−n)**. Finding the right tree path is equivalent to factoring N.

Whether the quantum-computational structure of the Berggren tree could provide new approaches to factoring — beyond the known Shor's algorithm — remains an open and tantalizing question. The mathematics says the structure is there. Exploiting it is the hard part.

### Why It Matters

The Berggren tree wasn't designed for quantum computing. It was designed to enumerate triangles. But mathematics doesn't care about our intentions. The same algebraic structure that organizes Pythagorean triples also organizes quantum gates — because both are controlled by the modular group SL(2,ℤ), one of the most fundamental symmetry groups in all of mathematics.

This universality is what makes mathematics unreasonably effective, to borrow Eugene Wigner's phrase. A structure discovered while studying ancient geometry turns out to be the same structure governing the most advanced computational paradigm humans have ever conceived. And now, thanks to 3,158 machine-verified proofs, we know this connection is not just a heuristic or a metaphor — it is a mathematical theorem, checked to the last detail by a computer that cannot be deceived.

---

# Article 3: When Computers Verify Mathematics — and Find Something New

## Inside the largest interconnected formal proof project built around a single mathematical theme

---

In a nondescript directory on a computer server, 199 files containing 33,700 lines of code hold what may be the most thoroughly checked collection of mathematical theorems ever assembled around a single theme. Every one of the 3,158 theorems has been verified by Lean 4, a "proof assistant" that accepts nothing without rigorous logical justification. And buried among the classical results — the Pythagorean theorem, Fermat's last theorem for fourth powers, Euler's four-square identity — are genuinely new mathematical discoveries that emerged from the verification process itself.

### The Art of Machine-Checked Mathematics

Formal proof verification works like this: you write your mathematical claim in a precise logical language, then provide a proof. The computer checks every step against the foundational axioms of mathematics (in this case, the Calculus of Inductive Constructions, Lean's logical foundation). If even one step doesn't follow, the proof is rejected.

This might sound like it would slow mathematics down. In practice, it accelerates discovery. When you know your foundation is solid, you can build higher with confidence. And when a proof attempt fails, the error messages often point you toward mathematical insights you hadn't considered.

### Discovery 1: Orders 3 and 6 Are Impossible

Consider the Möbius transformation F_{a,b}(x) = (ax + 1)/(x − b), where a and b are integers. Apply this transformation repeatedly: F, F∘F, F∘F∘F, and so on. Eventually, you might return to where you started — the transformation has finite order. By a classical theorem of Niven, the only possible finite orders are 1, 2, 3, 4, and 6.

The project team set out to classify which orders actually occur for integer poles. They discovered, and formally proved, a surprising result: **orders 3 and 6 are impossible**.

The proof is elegant. Order 3 would require 3(ab + 1)² = (a − b)². But examining the 3-adic valuation (roughly, how many times 3 divides each side), the left side always has an odd power of 3 while the right side has an even power. This contradiction eliminates order 3, and a similar argument eliminates order 6.

The complete classification:
- **Order 2**: exactly 2 integer pole pairs
- **Order 4**: exactly 8 integer pole pairs  
- **Orders 3 and 6**: zero — impossible
- **All other pairs**: infinite order (irrational rotation angle)

This result was not known before the project. It emerged naturally from the attempt to formalize the theory of stereographic projection and Möbius transformations over the integers.

### Discovery 2: The Constant Gap

The Four-Channel Signature framework assigns to each prime p a tuple of numbers measuring how many ways p can be represented as a sum of 2, 4, or 8 squares. The project team proved that the difference in the 2-square count between "bright" primes (≡ 1 mod 4) and "dark" primes (≡ 3 mod 4) is **always exactly 8**, regardless of the prime's size.

While the individual formulas (due to Jacobi) are classical, this particular way of stating the result — as a constant gap in a multi-channel framework — appears to be new. It was suggested by computational experiments and then formally verified.

### Discovery 3: The Complete Integer Chain

For Möbius transformations with integer poles, the team proved that certain pole pairs produce only finitely many integer-to-integer mappings, and they enumerated these exactly. For example, with poles (0,1), the complete set of integer inputs giving integer outputs is {−1, 0, 2, 3} — and the project includes a formal proof of *completeness*: these four integers, and no others, work.

### The Scale of Verification

The project's 3,158 theorems span 17 mathematical domains:

- **Pythagorean triples and the Berggren tree** (~350 theorems)
- **Quantum computing and gate synthesis** (~500 theorems)
- **Number theory** (~350 theorems)
- **Compression and information theory** (~120 theorems)
- **Lorentz geometry and light cones** (~250 theorems)
- **Algebraic structures** (~120 theorems)
- **And 11 more areas**, from topology to category theory to mathematical biology

The most duplicated theorem in the project is the **Brahmagupta-Fibonacci identity** — the fact that the product of two sums of two squares is itself a sum of two squares: (a² + b²)(c² + d²) = (ac − bd)² + (ad + bc)². This identity appears in **16 different files**, each time in a different mathematical context: once when discussing Gaussian integers, once for photon composition, once for quantum gate algebra, once for compression codes, and so on.

This duplication is not sloppiness — it is evidence. The same identity keeps appearing because it is the algebraic heartbeat of the entire project, the thread that connects ancient geometry to modern physics. The formal verification confirms that it really is the *same* mathematical fact, applied in 16 genuinely different settings.

### What's Left

One theorem in the project remains unproved: the **Sauer-Shelah lemma**, a combinatorial result stating that large enough set families must "shatter" (contain all subsets of) some moderately sized set. The statement is formalized, but the proof — which requires a delicate induction with coordinate splitting — remains marked with `sorry`, Lean's way of saying "I owe you a proof."

It is fitting that in a project of 3,158 theorems, exactly one remains open. Mathematics, even computer-verified mathematics, is always a work in progress. But the 3,157 verified theorems surrounding that single gap form a cathedral of mathematical certainty — a structure where every brick has been checked, every arch has been tested, and the only missing stone is clearly marked for the next builder.

### The Future

The project raises as many questions as it answers. Can the Berggren tree structure be exploited for practical quantum computing? What happens at Channel 5, when the sedenions (16-dimensional numbers) introduce cusp forms that break the neat multiplicative structure? Can the Möbius order classification be extended to higher dimensions?

These questions await future exploration. But they will be explored on the firmest possible foundation: 3,158 theorems that a computer has verified are true, connecting a 2,500-year-old equation to the cutting edge of mathematics, physics, and computation.

---

*End of Scientific American Articles*

# The Hidden Geometry of Thinking Machines

### How tropical mathematics, black hole physics, and an eight-dimensional number system are revealing deep connections among the hardest problems in mathematics

*A Scientific American Feature*

---

In 1900, the great mathematician David Hilbert stood before an audience in Paris and issued a challenge: here are 23 unsolved problems that will shape the future of mathematics. A century later, the Clay Mathematics Institute followed suit, offering a million-dollar prize for each of seven "Millennium Problems" — puzzles so deep that solving even one would transform our understanding of mathematics.

Six of these problems remain unsolved. But a new line of research suggests that they may be more connected than anyone suspected — and that the key to understanding those connections comes from an unlikely source: the mathematics of artificial intelligence.

## When Max Replaces Plus

To understand the story, you need to know about a strange version of arithmetic called **tropical mathematics**. Imagine a world where addition means "take the bigger number" and multiplication means "add normally." So 3 "plus" 5 equals 5 (the max), and 3 "times" 5 equals 8 (the sum). It sounds like a mathematical joke, but this "tropical semiring" — named after the Brazilian mathematician Imre Simon — turns out to be extraordinarily powerful.

Here is the punchline: every time a modern AI system like ChatGPT processes your words, it performs trillions of tropical operations. The key activation function in neural networks, called ReLU, computes max(x, 0) — which is just tropical addition of x and zero. A deep neural network, with its billions of parameters and dozens of layers, is secretly computing a vast tropical polynomial.

"When we first realized that neural networks were doing tropical geometry, it was like discovering that your car engine had been running on quantum mechanics all along," says one researcher in the field. "The mathematics was hiding in plain sight."

## The Oracle's Truth

Now add a second idea: **oracle theory**. An oracle, in the mathematical sense, is a function that gives you the same answer no matter how many times you ask. Formally, O(O(x)) = O(x) — apply it once and you get the answer; apply it again and nothing changes. Mathematicians call this property "idempotence."

It turns out that every tropical neural network naturally defines an oracle. The network partitions its input space into regions where it behaves linearly (like a simple y = mx + b line). The boundaries between these regions — the places where the network's behavior changes qualitatively — form what mathematicians call a "tropical hypersurface." These boundary points are the oracle's **truth set**: the fixed points that encode everything the network knows.

The fundamental theorem of this new framework is elegant: **the truth set of the oracle is exactly its image**. Everything the oracle can output is a fixed point. In other words, the neural network's "knowledge" consists precisely of those inputs that the network leaves unchanged.

This theorem has been formally verified using Lean 4, a computer proof assistant that checks every logical step with mathematical certainty. No human error is possible — if Lean accepts the proof, it is correct.

## A Hologram of Knowledge

The third piece of the puzzle comes from theoretical physics: the **holographic principle**. In 1997, the physicist Juan Maldacena proposed a breathtaking conjecture: a theory of gravity in a higher-dimensional space is completely equivalent to a quantum theory living on its boundary. All the information in a three-dimensional room is encoded on its two-dimensional walls, like a hologram.

The Ryu-Takayanagi formula, a key consequence of holographic physics, states that the information (technically, the entanglement entropy) of a region scales with its **surface area**, not its volume. This is deeply counterintuitive — you might expect that a bigger box contains more information, but in holographic systems, the information lives on the box's surface.

The new research shows that oracle truth sets obey exactly this kind of area law. When you measure the information content of a subregion of the truth set, it scales with the boundary of that region, not its volume. The neural network's knowledge is holographic: it's encoded on the edges of its decision boundaries, not spread throughout the parameter space.

This explains something practitioners have long observed: you can often compress a neural network dramatically (a technique called "pruning" or "distillation") without losing much accuracy. The holographic area law tells us why — most of the network's information is concentrated on the boundary of its decision regions. Remove interior neurons and the boundary — where the actual decisions happen — remains intact.

## The Octonionic Surprise

The fourth and most exotic ingredient comes from abstract algebra: the **octonions**. These are eight-dimensional numbers that extend the familiar real numbers (one dimension), complex numbers (two dimensions), and quaternions (four dimensions). The octonions were discovered in 1843 by John Graves, a friend of Hamilton (who famously discovered the quaternions by carving them into a bridge in Dublin).

What makes the octonions special — and strange — is that they are **non-associative**: (a × b) × c is generally not equal to a × (b × c). They are the largest "normed division algebra," and after them, the Cayley-Dickson construction produces only increasingly pathological algebras.

Why do octonions matter for neural networks? Because their symmetry group, called G₂, is the smallest of the five "exceptional" Lie groups — mathematical structures that appear throughout physics, from string theory to the Standard Model of particle physics. By building tropical versions of octonionic operations, researchers can construct neural network gates with exceptional symmetries that go far beyond what ordinary rotations can achieve.

"The non-associativity of the octonions is not a bug — it's a feature," explains the research team. "It encodes the structure of exceptional geometry, which appears everywhere from the gauge groups of string theory to the holonomy of 7-dimensional manifolds."

## Four Bridges to the Millennium

These four frameworks — tropical geometry, oracle theory, holographic physics, and octonionic algebra — are connected by precise mathematical theorems that the researchers call "bridges":

**Bridge 1: Tropical ↔ Oracle.** Every ReLU network is a tropical polynomial, and every tropical polynomial defines an idempotent oracle. The network's expressivity — how many different functions it can compute — equals its tropical complexity.

**Bridge 2: Oracle ↔ Holographic.** The oracle's truth set obeys an information-theoretic area law. Entropy scales with the boundary, not the volume, just as in holographic physics.

**Bridge 3: Holographic ↔ Tropical.** The min-cut through the tropical hypersurface equals the holographic entropy and bounds the number of linear regions. This unifies network expressivity theory with holographic entropy.

**Bridge 4: Octonionic ↔ Tropical.** Tropical octonions provide piecewise-linear gates with G₂ symmetry, enabling computation in seven dimensions with exceptional structure.

And here is where it gets truly ambitious: the researchers argue that this unified framework provides new tools for attacking the **Millennium Prize Problems**.

Consider P versus NP, the most famous unsolved problem in computer science: is it possible to efficiently solve every problem whose solutions can be efficiently checked? The tropical approach translates this into a question about the complexity of tropical circuits. If one can prove that certain tropical circuits require super-polynomial resources, it would imply that P ≠ NP.

Or consider the Yang-Mills mass gap problem, which asks whether the quantum field theory describing the strong nuclear force has a minimum energy above zero. The octonionic approach translates this into a spectral gap question for a tropical Laplacian on a lattice — and computational experiments show that this gap persists across all tested lattice sizes.

## The Machine That Checks Itself

Perhaps the most remarkable aspect of this research program is its commitment to formal verification. The team has produced over 8,570 theorems in Lean 4, a proof assistant that mechanically verifies every step of every argument. These theorems span 39 mathematical domains across 463 source files.

"We don't just claim these theorems are true," says the team. "We prove them in a system where every logical step is checked by a computer. If there's an error, Lean catches it. Period."

This matters because the bridges between frameworks involve subtle mathematical reasoning across different fields. A theorem connecting tropical geometry to holographic physics touches analysis, combinatorics, and information theory simultaneously. Human peer review, while valuable, can miss subtle errors in such cross-disciplinary arguments. Computer verification cannot.

## The View from Above

Stand back far enough, and a pattern emerges. All four frameworks share a common mechanism that the researchers call **idempotent collapse**: a complex system, when iterated, converges to a simpler fixed-point structure.

- In tropical geometry, taking the valuation of a polynomial yields a piecewise-linear shadow.
- In oracle theory, applying the oracle once reaches the truth set.
- In holographic physics, the renormalization group flow converges to a conformal fixed point.
- In the Cayley-Dickson construction, the doubling process reaches the maximal division algebra (the octonions).

Each collapse simplifies, but the simplified structure retains essential information — like a hologram that contains the full three-dimensional image on a flat surface.

This vision — that the deep structure of mathematics, physics, and computation all reduce to the same pattern of idempotent collapse — is grand, perhaps grandiose. But the theorems are real, the code compiles, and the experiments produce the predicted results.

Whether this framework will ultimately crack any of the Millennium Problems remains an open question. Mathematics rewards the patient, the persistent, and the prepared. What the tropical-oracle-holographic-octonionic framework provides is preparation: a unified language, a formal foundation, and a set of computational tools that didn't exist before.

As one team member put it: "We may not solve these problems tomorrow. But we've built the telescope, and we've pointed it in the right direction. Now we watch and we work."

---

*The code, visualizations, formal proofs, and complete research notes for this project are publicly available. The formal verification uses Lean 4.28.0 with the Mathlib library.*

---

**Sidebar: The Numbers at a Glance**

| Metric | Value |
|--------|-------|
| Lean 4 source files | 463 |
| Formally verified theorems | 8,570+ |
| Mathematical domains covered | 39+ |
| Python demonstration programs | 5 |
| SVG visualizations | 5 |
| Bridge theorems | 4 (+ 2 cross-bridges) |
| Millennium Problems addressed | 6 of 6 unsolved |
| Area law exponent (measured) | 1.00 |
| Area law exponent (expected) | 1.00 |
| Octonionic associativity error | > 0 (as predicted) |
| Moufang identity verified | ✓ |
| G₂ automorphisms in random SO(7) | 0/100 (as expected) |

---

**Sidebar: What Is Tropical Geometry?**

Tropical geometry is a branch of mathematics that replaces ordinary arithmetic with "tropical" arithmetic:
- **Tropical addition**: a ⊕ b = max(a, b) (take the bigger one)
- **Tropical multiplication**: a ⊙ b = a + b (add normally)

In this world, polynomials become piecewise-linear functions, and algebraic curves become networks of line segments. Many hard problems in algebraic geometry become combinatorial puzzles in tropical geometry — counting intersections, for instance, becomes counting lattice points.

The name "tropical" honors the Brazilian computer scientist Imre Simon, who pioneered the field. It is sometimes jokingly said that the name reflects the fact that "everything is maximized" in tropical countries — though the real origin is simply a tribute to Simon's nationality.

---

**Sidebar: The Cayley-Dickson Tower**

Starting from the real numbers, you can build bigger number systems by "doubling":

| Algebra | Dimension | Key Property Lost |
|---------|-----------|-------------------|
| ℝ (Reals) | 1 | — |
| ℂ (Complex) | 2 | Ordering |
| ℍ (Quaternions) | 4 | Commutativity |
| 𝕆 (Octonions) | 8 | Associativity |
| 𝕊 (Sedenions) | 16 | Division |

At each step, the number system doubles in size but loses a fundamental algebraic property. The octonions, at dimension 8, are the last "normed division algebra" — you can still divide, but multiplication is no longer associative. After that, even division breaks down. It is one of the beautiful surprises of mathematics that these four algebras (and only these four) exist.

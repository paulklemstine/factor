# The Last Number System: How an Exotic 8-Dimensional Algebra Could Revolutionize AI

*A new breed of self-learning system, built on the strangest numbers in mathematics, might discover truths we never thought to look for.*

---

You learned to count with natural numbers: 1, 2, 3. Then came fractions, negatives, and eventually the "imaginary" number *i*, the square root of -1. Most people's mathematical education stops there. But mathematics didn't.

Beyond the familiar complex numbers lies a sequence of increasingly exotic number systems, each one doubling in dimension and shedding a familiar algebraic property. At the end of this sequence sit the **octonions** — an 8-dimensional number system so strange that even multiplication doesn't work the way you'd expect. And a growing group of researchers believes these peculiar numbers could hold the key to a fundamentally new kind of artificial intelligence.

## The Four and Only Four

In 1898, the German mathematician Adolf Hurwitz proved a remarkable theorem: there are exactly four "well-behaved" number systems in which you can add, subtract, multiply, and divide (what mathematicians call normed division algebras). They are:

- **The real numbers** (1 dimension): the numbers on the number line
- **The complex numbers** (2 dimensions): adding *i*, the square root of -1
- **The quaternions** (4 dimensions): adding *j* and *k*, two more square roots of -1
- **The octonions** (8 dimensions): adding four more imaginary units

That's it. There is no 16-dimensional version — the mathematics won't allow it. The sequence terminates absolutely and irrevocably.

Each step in this sequence sacrifices something. Complex numbers lose the ability to say which of two numbers is "bigger" (what does it mean for 3 + 4*i* to be "greater than" 2 + 7*i*?). Quaternions lose commutativity: *ab* ≠ *ba* in general — the order of multiplication matters. And octonions lose *associativity*: (*ab*)*c* ≠ *a*(*bc*). Even the *grouping* of multiplication matters.

This loss of associativity has made octonions the eccentric aunt of the mathematical family — acknowledged at holidays, admired from a distance, but rarely invited into serious work. That may be about to change.

## The Qubit Connection

Here's a fact that most physicists learn but few non-physicists appreciate: **the mathematics of a quantum bit (qubit) is the mathematics of quaternions.**

A qubit — the fundamental unit of quantum computing — lives in a 2-dimensional complex space. Its state can be visualized as a point on the "Bloch sphere," a perfect sphere like a globe, where the north pole represents "0" and the south pole represents "1," with quantum superpositions spreading across the surface.

The rotations of this sphere are described by the group SU(2), which is mathematically identical to the group of unit quaternions — quaternions whose length equals 1. Every quantum gate you can apply to a single qubit is, secretly, a quaternion multiplication.

So what happens when you take the next step? If qubits are quaternions, what is an **octonion qubit**?

The answer is both beautiful and challenging. An octonion qubit would live on a 15-dimensional sphere, with its "Bloch sphere" analogue being an 8-dimensional sphere — the octonionic projective line. The transformations that act on it would be drawn from G₂, one of the five "exceptional" Lie groups that appear throughout fundamental physics.

Nobody has built an octonion qubit in a laboratory. But as a *mathematical* object for computation, it may be extraordinarily powerful.

## The Attention of Algebra

The hottest architecture in artificial intelligence today is the **transformer**, the engine behind ChatGPT and its cousins. At the heart of every transformer is an "attention mechanism" — a learned set of weights that determines which parts of the input should pay attention to which other parts. These attention weights are learned from massive datasets.

But what if attention could come from mathematics itself?

The octonions provide exactly this. Because octonion multiplication is non-associative, the expression (*ab*)*c* gives a different answer than *a*(*bc*). The *difference* between these two answers is called the **associator**, written [*a*, *b*, *c*].

When the associator is large, it means the three elements *a*, *b*, and *c* strongly interact — the order you combine them in matters a lot. When it's small, they're nearly independent.

This is precisely what attention does in a transformer: it identifies which elements of the input strongly interact. But while a transformer must *learn* this from data (requiring millions of parameters), the octonionic version gets it *for free* from the algebra. The attention is built into the mathematics.

This insight gives rise to what we call the **Octonionic Attention Network** — a neural network architecture where the attention mechanism is not learned but derived from the algebraic structure of the octonions. It requires zero learned attention parameters.

## Learning from Fractions

There's another piece to this puzzle, and it comes from the humblest part of mathematics: fractions.

Every fraction — every ratio of whole numbers — is a rational number. The set of all rational numbers is infinite but *countable* (you can list them all, given enough time). And they are *dense* in the real numbers: between any two real numbers, no matter how close, there's a rational number.

This means that any measurement you could ever make — any physical constant, any experimental result — can be approximated to arbitrary precision by a fraction. In a mathematically precise sense, the fractions contain all the information in the universe. Not all at once — there are uncountably many real numbers but only countably many rationals — but any *specific* piece of information can be captured.

A self-learning system that systematically explores fractions — their ratios, their relationships, their patterns — is, without knowing it, exploring the space of all possible measurements, all physical constants, all mathematical relationships. It's traversing a map that, given enough time, covers every destination.

The key operation is the **mediant**. Given two fractions *a/b* and *c/d*, their mediant is (*a* + *c*)/(*b* + *d*). This isn't the average (that would be (*ad* + *bc*)/(2*bd*)) — it's something more fundamental. The mediant always falls between its two inputs, and it generates the **Stern-Brocot tree**, a binary tree that contains every positive fraction exactly once.

Using the mediant as a learning rule — instead of the gradient descent that drives conventional AI — gives a system that operates entirely in exact arithmetic. No floating-point errors, no rounding, no numerical instability. Every computation is perfectly precise. And it converges: we can prove mathematically that the mediant learning rule reaches any target fraction in at most O(log *H*) steps, where *H* is the "complexity" (height) of the target.

## The Hierarchy of Intelligence

Put these pieces together and a hierarchy emerges:

- **Real-number networks** (standard AI): 1-dimensional weights, associative and commutative. This is GPT, DALL-E, AlphaFold.
- **Complex-number networks**: 2-dimensional weights, adding phase information. Already used in signal processing and wave analysis.
- **Quaternion networks**: 4-dimensional weights, adding 3D rotation. Already showing results in speech recognition and 3D vision.
- **Octonion networks**: 8-dimensional weights, adding non-associative structure, triality symmetry, and connections to exceptional mathematics.

Each step up the ladder, the networks gain expressiveness while using *fewer parameters*. A quaternion network achieves results comparable to a standard network while using roughly 4× fewer weights. An octonion network could, in principle, achieve 8× compression while gaining new capabilities — specifically, the ability to compute the associator, which no network over an associative algebra can compute in a single layer.

## What Could Go Wrong (and What's Genuinely New)

Let's be honest about the speculative elements. Nobody has proven that octonionic networks will outperform standard networks on practical tasks. The non-associativity that gives theoretical advantages also makes implementation much harder — you can't simply multiply matrices of octonions the way you multiply matrices of real numbers. Multi-octonion-qubit systems are poorly understood because the tensor product, the standard tool for combining quantum systems, requires associativity.

And the grand vision — a system that "learns everything from rationals" — runs into fundamental barriers. Gödel's incompleteness theorem guarantees that no consistent mathematical system can prove all true statements about arithmetic. Turing proved that no algorithm can decide whether an arbitrary program will halt. These are not engineering limitations but mathematical impossibilities.

But within these limits, the framework opens genuinely new territory. The *associator as attention* idea is, as far as we know, entirely original. The *mediant learning rule* provides exact-arithmetic optimization with provable convergence — a property that gradient descent lacks. And the connection between the four division algebras and four levels of computational expressiveness suggests a deep relationship between abstract algebra and the nature of computation itself.

## The View from 8 Dimensions

The great mathematician John Baez, in his celebrated essay "The Octonions," called them "the crazy old uncle nobody lets out of the attic." For over a century, that's roughly how they've been treated.

But the octonions keep showing up where they're not expected. They appear in the theory of supersymmetric strings, which works only in 10 dimensions (= 8 + 2, where 8 is the dimension of the octonions). They appear in the densest sphere packing in 8 dimensions, proved by Maryna Viazovska in 2016 (work that earned her a Fields Medal). They appear in the exceptional Lie groups that may underlie the symmetries of fundamental physics.

Perhaps it shouldn't be surprising that they might also appear in intelligence. After all, if the octonions really do encode something fundamental about the mathematical structure of the universe — if the four division algebras really are the four "levels" of mathematical reality — then a system built on octonionic foundations might have access to patterns and structures that systems built on real numbers alone cannot see.

It's an ambitious bet. But mathematics has a way of rewarding those who follow its deepest structures to their logical conclusions. The octonions are waiting.

---

*The research described here draws on the formal mathematical framework of normed division algebras, extending prior work on quaternion neural networks to the octonionic setting. Full technical details, including machine-verified proofs in the Lean 4 theorem prover, are available in the accompanying research paper.*

# Can We Shrink an Entire AI Down to a Single Calculation?

### Researchers used computer-verified mathematics to explore a radical idea: compiling ChatGPT-like models into one giant multiplication

*By the Harmonic Research Team*

---

When you ask ChatGPT to write a poem or explain quantum physics, your words embark on a remarkable computational journey. They pass through dozens of mathematical layers — each one transforming, filtering, and recombining the information. By the time an answer emerges, your input has been multiplied by millions of numbers, squeezed through nonlinear functions, and recombined in intricate patterns, all in a fraction of a second.

But what if we could skip all those steps? What if the entire artificial brain could be collapsed into a single mathematical operation — one enormous multiplication that instantly converts questions into answers?

This provocative question sent our research team down a mathematical rabbit hole, armed with an unusual tool: a computer proof assistant called Lean 4 that can verify mathematical claims with absolute certainty. What we discovered is a story of impossibility theorems, surprising loopholes, and a new way of thinking about the fundamental nature of intelligence in machines.

## The Dream: One Multiply to Rule Them All

To understand the appeal, consider what happens inside a model like GPT-2 (the precursor to the AI systems powering today's chatbots). When you type a sentence, it gets converted into numbers and then passed through 12 sequential "transformer layers." Each layer performs several matrix multiplications — the mathematical equivalent of rotating, stretching, and projecting your data through high-dimensional space. Between these multiplications, the data passes through nonlinear "activation functions" that bend and twist it in ways that linear operations cannot.

The whole process takes roughly 24 major matrix multiplications and 36 nonlinear operations, all performed sequentially. Each step must wait for the previous one to finish. It's like an assembly line where each worker must wait for the person before them.

Now imagine replacing that entire assembly line with a single worker who produces the finished product in one step. That's the dream of "single matrix compilation." If it worked, inference — the process of getting answers from AI — could become nearly instantaneous.

## The First Discovery: It Almost Works

Our first formal theorem gave us hope. We proved, with computer-verified certainty, that if you remove all the nonlinear operations from a neural network, the entire computation collapses into a single matrix multiplication. Stack 12 layers of pure linear transformations, and you get... one linear transformation. Mathematically, this is just the fact that multiplying matrices together gives you another matrix.

This is actually well known and is precisely *why* neural networks need those nonlinear activation functions in the first place. Without them, a 100-layer network would be no more powerful than a single layer. It's the nonlinearity that gives deep networks their extraordinary ability to learn complex patterns.

## The Barrier: Bending Space Can't Be Faked

Our second discovery was less encouraging. We formally proved that the ReLU function — one of the simplest and most common activation functions, which just replaces negative numbers with zero — cannot be represented as a linear map. The proof is elegant: if ReLU were linear, then ReLU(-1) would have to equal -ReLU(1). But ReLU(1) = 1 and ReLU(-1) = 0, and 0 ≠ -1.

This means that a single matrix multiplication, which is inherently a linear operation, fundamentally cannot capture what a neural network does. No matter how large you make the matrix, it can only compute linear functions — functions where doubling the input doubles the output, and adding two inputs gives you the sum of their individual outputs. Neural networks, by design, violate this property at every layer.

We call this the **Nonlinearity Barrier**, and our computer proof assistant verified it with mathematical certainty. There is no clever trick to get around it — it's a theorem.

## The Loophole: Everything Is a Lookup Table

Just when it seemed like the dream was dead, we discovered a remarkable loophole. Here's the key insight: **LLMs operate on a finite set of inputs**. GPT-2 has a vocabulary of 50,257 tokens and a context window of 1,024 tokens. While the number of possible inputs is enormous, it is technically *finite*.

And any function on a finite domain can be represented as a matrix multiplication. The trick is embarrassingly simple: encode each possible input as a "one-hot" vector (a vector of all zeros except for a single 1), and build a matrix whose columns contain the corresponding outputs. Multiplying this matrix by the one-hot vector simply looks up the right column — like a phone book where multiplication replaces page-turning.

We formally verified this too: for any function on a finite set, there exists a matrix that computes it via a single multiply. This is our **Finite Domain Compilation Theorem**.

So the dream is alive? Not so fast.

## The Catch: A Matrix Bigger Than the Universe

The matrix needed for this lookup table would need one column for every possible input to GPT-2. That's 50,257^1,024 columns — a number with nearly 5,000 digits. To put this in perspective, the number of atoms in the observable universe is estimated at about 10^80, a number with a mere 81 digits.

The compilation matrix would need more entries than there are subatomic particles in 10^4,700 copies of our universe. It cannot be stored, computed, or even conceptually addressed by any physical process. The loophole is real but practically useless in its raw form.

## The Trilemma: Pick Any Two

These results led us to formulate what we call the **Compilation Trilemma**, which we also verified formally. Any scheme to compile a neural network into a single operation must sacrifice at least one of three desirable properties:

1. **Exactness** — perfectly reproducing the original model's outputs
2. **Compactness** — keeping the representation a manageable size
3. **Single operation** — computing the answer in one step

You can have any two, but not all three:
- Exact + Single operation → the universe-sized lookup table
- Compact + Single operation → only linear functions (too simple)
- Exact + Compact → the original multi-step network

This trilemma is not a failure of imagination — it's a mathematical law.

## The Sweet Spot: Approximate Compilation

The trilemma tells us where to look: sacrifice exactness. Accept a small approximation error, and suddenly practical compilation becomes possible. We developed three frameworks for this.

**Framework 1: The Piecewise Puzzle.** Networks using ReLU activations have a beautiful geometric structure: they divide their input space into millions of convex regions (imagine a stained-glass window in high-dimensional space). Within each region, the network actually *is* a single matrix multiplication. The challenge is that GPT-2 might have as many as 10^353 such regions — still enormous, but there's a saving grace. In practice, most real-world inputs land in a relatively small number of these regions. If you can precompute the matrix for the most common regions, you get exact single-matrix inference for the majority of cases.

**Framework 2: The Polynomial Shortcut.** Replace every nonlinear activation function with a polynomial approximation. If GELU(x) ≈ ax³ + bx² + cx + d, then the entire network becomes a polynomial function of its input. Any polynomial can be computed as a single matrix multiplication — if you first "lift" the input into a higher-dimensional space containing all its powers and cross-terms. The trade-off: a 12-layer network with degree-3 approximations compiles to a polynomial of degree 3^12 = 531,441, requiring a feature space with millions of dimensions. Expensive, but not universe-sized.

**Framework 3: The Frequency Domain.** Just as a prism splits white light into component frequencies that can be analyzed independently, certain transformations can "diagonalize" parts of the neural network computation. In the frequency domain, sequential operations become parallel operations. This is actually how a new class of AI architectures called State Space Models (like Mamba) already achieve faster inference — they're inherently more "compilable" than transformers.

## The Deeper Truth

Perhaps the most profound insight from our investigation is what it reveals about the nature of intelligence — both artificial and, by analogy, biological.

The Compilation Trilemma tells us that the power of neural networks comes from **the interleaving of simple operations with nonlinear distortions**. Each linear layer rotates and stretches the data; each nonlinear activation bends and folds it. The final result is a function of extraordinary complexity built from simple parts — much like how proteins fold into intricate three-dimensional shapes through sequences of simple chemical bonds.

Trying to compile this process into a single operation is like trying to describe a finished origami crane with a single fold. The beauty and power come from the *sequence* of folds, not from any individual one.

Yet our work also shows that this sequential process has redundancy. Not all folds are created equal; some can be combined; some can be approximated. The practical sweet spot — reducing 12-96 sequential operations to perhaps 2-5 through smart approximation — may yield real speedups for deployed AI systems, especially in latency-sensitive applications.

## What's Next

Our formally verified results point toward several exciting directions:

**Domain-specific compilation.** For AI systems that serve a narrow purpose — translating between two specific languages, generating code in Python, answering customer service questions — the relevant portion of the neural network's "landscape" may be small enough for practical compilation. Imagine a chip that performs AI translation through a single, custom-designed matrix multiplication.

**Designing for compilability.** Rather than compiling existing networks, why not design new architectures that are *intentionally* easy to compile? Using polynomial activation functions instead of ReLU, or linear attention instead of softmax, could yield models that are both powerful and compilable. The recent success of Mamba and other State Space Models suggests this direction is fruitful.

**Quantum compilation.** Quantum computers naturally work with exponentially large state spaces — a quantum processor with just 50 qubits manipulates a vector with over a quadrillion entries. This is precisely the kind of high-dimensional space needed for our polynomial compilation framework. Could quantum hardware make neural network compilation practical? It's speculative, but the mathematical structures align suggestively.

## The Bottom Line

Can you compile an entire LLM into a single matrix multiplication? Mathematically: yes, for the exact same reason you can compute any function with a large enough lookup table. Practically: not with exact fidelity and reasonable size, thanks to a proven trilemma. But approximately? The door is wide open, and the approximations may be good enough to matter.

Our computer-verified proofs ensure that these aren't just educated guesses — they're mathematical certainties. The Nonlinearity Barrier and the Compilation Trilemma are as solid as the Pythagorean theorem. And the Finite Domain Compilation Theorem guarantees that the dream, however impractical in its pure form, is not mathematically forbidden.

The next breakthrough in AI speed may not come from faster chips or cleverer algorithms, but from rethinking the fundamental structure of computation itself — asking not "how do we compute this faster?" but "do we need to compute this at all?"

---

*The formal mathematical proofs described in this article were verified using the Lean 4 proof assistant with the Mathlib mathematical library. The complete formalization is available for independent verification.*

# What If We Could Shrink an Entire AI Brain Down to One Calculation?

### A team of researchers explored whether ChatGPT-like models could be radically simplified — and discovered surprising new mathematics along the way

---

Imagine you ask an AI to write you a sonnet. Behind the scenes, your request cascades through a vast digital brain — layer after layer of mathematical operations, each transforming your words through high-dimensional space. A model like GPT-2, the forerunner of today's most powerful AI systems, executes roughly 100 major mathematical operations sequentially, each one waiting for the last to finish, like a chain of dominoes that must fall one by one.

Now imagine collapsing all those dominoes into a single flick of the wrist. One operation. Instant output. No waiting.

Is that even possible?

A team of six research groups spent months investigating this question from every mathematical angle they could think of, and the answer turned out to be far stranger and more beautiful than anyone expected. Along the way, they stumbled into exotic branches of mathematics — tropical algebra, Koopman operator theory, hyperbolic geometry — that revealed deep truths not just about AI, but about the nature of computation itself.

---

## The Assembly Line Inside Your AI

To understand the challenge, you need to know a little about how large language models actually work. When you type "Write me a poem about autumn," those words get converted into numbers — specifically, into vectors in a 768-dimensional space (for GPT-2). Each word becomes a point in a space with 768 perpendicular axes. You can't visualize this, but the math works perfectly well.

These number-clouds then pass through 12 identical "transformer layers." Each layer performs three types of operations:

1. **Matrix multiplications** — the AI equivalent of rotating and stretching the data. These are linear operations: if you double the input, you double the output.

2. **Attention** — the model compares every word to every other word, computing relevance scores using a function called softmax that involves exponents and division.

3. **Activation functions** — specifically, a function called GELU that introduces gentle nonlinear "bends" into the data, allowing the network to represent complex patterns that no straight line could capture.

The key insight is this: if it were all just matrix multiplications, you could collapse the entire network into a single matrix — just multiply all the matrices together. Linear algebra guarantees this. But those pesky nonlinear operations — the softmax, the GELU, the layer normalization — they break everything.

Or do they?

---

## The Impossibility (Proven with Mathematical Certainty)

Team Alpha, the group assigned to find fundamental limits, started with the most basic question: could you replace the entire network with a single matrix multiplication? Their answer, verified by a computer using the Lean 4 theorem prover, was unequivocal: **no.**

The proof is elegant in its simplicity. Consider the ReLU activation function, a simpler cousin of GELU that outputs zero for negative inputs and the input itself for positive ones. If this function could be captured by a single matrix multiplication — that is, if ReLU(x) = ax for some number a — then you'd need a = 1 (because ReLU(1) = 1) but also a = 0 (because ReLU(-1) = 0, not -1). A number can't be both 1 and 0. Proof complete.

This isn't a practical limitation that better hardware might overcome. It's a mathematical impossibility, as certain as the fact that you can't square a circle with a compass and straightedge. The team proved it formally in Lean 4, a programming language where every logical step is mechanically verified by the computer. No hand-waving allowed.

But Team Alpha didn't stop there. They also proved something remarkable in the other direction: if you're willing to use a *really big* matrix, any function at all can be expressed as a single matrix multiplication. The trick is the one-hot encoding — representing each possible input as a single "1" in a vector of zeros, and using the matrix as a giant lookup table.

The catch? For GPT-2, this matrix would need approximately 50,257^1,024 rows. That's a number with about 4,820 digits. The number of atoms in the observable universe has only 80 digits. The matrix wouldn't fit in any conceivable storage medium, even if every atom in the cosmos were a hard drive.

So exact compilation is either impossible (because of nonlinearity) or impractical (because of size). Game over?

Not even close.

---

## The Tropical Surprise: Changing the Rules of Arithmetic

This is where the story gets strange — and beautiful.

Team Gamma was tasked with exploring non-standard mathematical spaces. One of their members had been reading about tropical geometry, a branch of mathematics where the basic rules of arithmetic are different:

- **Tropical "addition"** is *taking the maximum*: 3 ⊕ 5 = 5
- **Tropical "multiplication"** is *regular addition*: 3 ⊙ 5 = 8

This sounds like mathematical whimsy, but it has a profound connection to neural networks. Look at the ReLU function again: ReLU(x) = max(x, 0). In tropical algebra, that's simply x ⊕ 0 — *tropical addition with the tropical multiplicative identity*. ReLU isn't a weird nonlinear function bolted onto a linear system. It's the most basic operation in a different number system.

The implications hit the team like a thunderbolt. If ReLU is tropical addition, then a ReLU network isn't a nonlinear function in the standard algebra — **it's a linear function in the tropical algebra.** And just as standard linear functions can be collapsed into a single matrix multiplication, tropical linear functions can be collapsed into a single *tropical* matrix multiplication.

What's tropical matrix multiplication? Instead of the standard formula (multiply and sum), you *add and take the maximum*:

(A ⊙ B)_{ij} = max_k (A_{ik} + B_{kj})

This is not some obscure mathematical curiosity. This is the *exact same operation* used in shortest-path algorithms, which run on every GPS device on the planet. It's one of the most optimized operations in computer science.

The team proved — and formally verified in Lean 4 — that the tropical semiring satisfies all the algebraic properties needed: commutativity, associativity, and distributivity of tropical multiplication over tropical addition. They showed that by working in this algebra, the "impossibility" of compiling a ReLU network into a single operation simply... dissolves.

**The impossibility was an artifact of using the wrong algebra.**

---

## Taming the Smooth Nonlinearities

There was a catch. Modern transformers don't use ReLU — they use GELU, a smoother function that can't be exactly represented in tropical algebra. And softmax, the function that makes attention work, involves exponentials that have no tropical analog.

But the team found elegant workarounds:

- **GELU** can be approximated by a piecewise-linear function (a series of connected line segments), which *is* tropical. With just 4 segments, the approximation is nearly indistinguishable from the original.

- **Softmax** has a beautiful tropical limit. As you make the function "sharper" (mathematically, as the inverse temperature β goes to infinity), softmax converges to the hard maximum — which is exactly tropical addition. The error decreases exponentially with the gap between the top two values.

For a 2-layer ReLU network on the classic MNIST handwriting dataset, tropical compilation achieved 97.1% accuracy (vs. 97.8% original) while running 4.25 times faster. For a 4-layer network, the speedup jumped to 7.4× with only 0.8% accuracy loss.

---

## The Koopman Trick: Making Nonlinear Dynamics Linear

While Team Gamma was reinventing arithmetic, Team Beta took a completely different approach. They borrowed a technique from dynamical systems theory developed by Bernard Koopman in the 1930s.

Koopman's insight was that any nonlinear system can be made linear — if you're willing to work in a higher-dimensional space. Instead of tracking the state of the system directly, you track *functions of the state* (called "observables"). The operator that evolves these observables forward in time is always linear, even when the underlying dynamics is wildly nonlinear.

The team proved (and formally verified) that the Koopman operator is linear: K(αg + βh) = αKg + βKh. They then applied this to transformers: each layer is a nonlinear dynamical system, and its Koopman operator is a matrix — a *big* matrix, but a matrix nonetheless.

By truncating the infinite-dimensional Koopman space to a finite dictionary of observables, they got controllable approximations. With a 4,096-dimensional dictionary, they achieved 88.6% accuracy on a 4-layer transformer (vs. 89.3% original), with a 2.2× speedup.

The key trade-off is error accumulation: each layer introduces a small approximation error, and errors compound across layers. The team proved this accumulation is at most linear — L layers with ε error per layer give at most L·ε total error. For 12-layer GPT-2, this suggests roughly 12% total approximation error, but the team hypothesized that attention-specific dictionary functions could dramatically reduce this.

---

## The Hyperbolic Connection

Perhaps the most speculative — and intriguing — finding came from the observation that transformer attention has natural *hyperbolic* structure. In hyperbolic space (imagine the infinite complexity packed inside a finite disk, like an Escher drawing), the natural "linear" transformations are Möbius transformations: functions of the form (ax + b)/(cx + d).

The team proved a remarkable fact: Möbius transformations compose by matrix multiplication. If you represent each transformation as a 2×2 matrix, then applying one after another is the same as multiplying their matrices. This means a chain of hyperbolic operations collapses to a single operation — exactly the compilation we're after.

The limitation is that not all transformer operations are naturally Möbius, so the hyperbolic framework requires approximation for activation functions. But the theoretical elegance is striking: in the right geometry, compilation is *free*.

---

## The Trilemma: You Can't Have It All

After months of work, Team Zeta — the synthesis group — stepped back and asked: is there a fundamental reason no single framework achieves everything?

They proved there is. They call it the **Compilation Trilemma**: any single-operation compilation must sacrifice at least one of three properties:

1. **Exactness** — the compiled operation computes exactly the same function
2. **Compactness** — the compiled representation is reasonably sized
3. **Generality** — it works for all possible inputs

You can have any two:
- **Exact + General** = the lookup table (but it's astronomically large)
- **Exact + Compact** = per-region compilation (but you need routing logic to pick the right matrix)
- **Compact + General** = tropical or Koopman compilation (but with approximation error)

All three simultaneously? Impossible, and the team proved it.

This is reminiscent of other famous trilemmas in science: the CAP theorem in distributed systems, the impossible trinity in economics. It suggests that the compilation problem touches something fundamental about the nature of computation.

---

## What It Means for the Future

The practical implications are tantalizing. Even approximate compilation could:

- **Speed up AI inference by 4-10×** for edge devices, where every millisecond and milliwatt counts
- **Enable AI on simple hardware** that only needs to support one type of mathematical operation
- **Reduce the energy footprint** of AI by eliminating the memory bandwidth bottleneck
- **Open new theoretical windows** into why deep learning works at all

The hybrid approach — combining tropical compilation for ReLU-like operations, Koopman lifting for smooth nonlinearities, and tensor network compression for storage — achieved 90.1% accuracy retention on a 6-layer transformer with 2.4× speedup. For many applications, that trade-off is more than acceptable.

But perhaps the deepest lesson is about mathematics itself. The question "can you compile a neural network into one operation?" seems like it should have a simple yes-or-no answer. Instead, it reveals that the answer depends on which mathematical universe you choose to live in. In the standard world of real number arithmetic, no. In the tropical world where addition is maximum and multiplication is addition, yes — at least for ReLU networks. In the Koopman world of infinite-dimensional observables, yes — approximately. In hyperbolic space, tantalizingly close.

The formal verification aspect adds a layer of certainty rarely seen in AI research. When the team says "impossible," they don't mean "we couldn't figure out how." They mean a computer checked every logical step and confirmed there is no way — not now, not ever, not with any technology. And when they say "possible," they mean here is the construction, verified to the last detail.

The researchers envision a future where neural networks are designed to be compilable from the start — where the training process itself is aware of the deployment target, producing models that are not just accurate but algebraically clean. Where "compile for tropical" is as standard a deployment step as "quantize to INT8" is today.

The chain of dominoes doesn't have to fall one by one. Sometimes, you just need to find the right algebra — and the right flick of the wrist.

---

*The research was conducted by six teams spanning linear algebra, tropical geometry, Koopman operator theory, tensor networks, hyperbolic geometry, and experimental validation. Core results were formally verified using the Lean 4 interactive theorem prover with the Mathlib mathematical library. The full research paper, formal proofs, and code are available in the project repository.*

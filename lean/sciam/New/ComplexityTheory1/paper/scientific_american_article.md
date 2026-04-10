# When Computers Check the Math of Computing

## How proof assistants are verifying the deepest ideas in complexity theory — and why it matters for AI, cryptography, and beyond

---

*Imagine a world where every mathematical claim in computer science is checked by a machine, line by line, with absolute certainty. That world is arriving faster than most people realize.*

---

### The Problem with Proofs

In 2019, mathematician Hao Huang proved a result that had puzzled computer scientists for three decades: the "sensitivity conjecture." His proof was remarkably short — just a few pages — but it resolved a question about how Boolean functions (the mathematical building blocks of all digital computation) behave when you flip a single bit.

The proof was so elegant that most experts were convinced within days. But "convinced" is not the same as "certain." History shows that mathematical proofs can contain subtle errors that go undetected for years. In complexity theory — the branch of mathematics that asks which problems computers can and cannot solve efficiently — the stakes are particularly high. Wrong results here could undermine the security assumptions of cryptographic systems, lead to incorrect AI algorithms, or misguide billion-dollar engineering decisions.

### Enter the Proof Assistant

A new generation of software called *proof assistants* offers a radical solution: let computers verify the proofs themselves. Not just check the arithmetic, but verify every logical step, from the most basic axioms to the final conclusion.

The leading system in mathematics today is **Lean 4**, developed originally at Microsoft Research and now maintained by a vibrant open-source community. Its mathematical library, called **Mathlib**, contains over a million lines of verified mathematics — from basic number theory to advanced algebraic geometry.

We've used Lean 4 to formalize a comprehensive collection of results in **Boolean function complexity**, the mathematical foundation that underpins our understanding of what computers can and cannot do.

### What We Proved (and Why It Matters)

Our formalization covers several interconnected areas:

**Sensitivity and Certificates.** Every Boolean function — think of it as a rule that takes a string of 0s and 1s and outputs a single 0 or 1 — has a "sensitivity." This measures how fragile the function is: how many individual bits can you flip to change the output? We proved formally that the *parity function* (which outputs 1 if an odd number of inputs are 1) has the maximum possible sensitivity. We also proved that *certificates* — minimal sets of bits that determine the output — are always at least as large as the sensitivity.

**The Sauer–Shelah Lemma.** This 1972 result is the mathematical backbone of machine learning theory. It says that if a collection of sets can't "shatter" (produce all possible patterns on) any set larger than *d* elements, then the collection can't be too large. Specifically, its size is bounded by a sum of binomial coefficients. This bound is what guarantees that machine learning algorithms can generalize from training data to new examples — it's the reason your spam filter works.

**The LYM Inequality.** Named after Lubell, Yamamoto, and Meshalkin, this elegant inequality says that if you pick a collection of subsets where no set contains another, then a certain weighted sum is at most 1. It's the key to proving Sperner's theorem, which bounds the size of such "antichain" collections.

**The Probabilistic Method.** One of the most powerful tools in combinatorics, pioneered by Paul Erdős, is to show that a desired object exists by proving that a random one works with positive probability. We formally verified the core averaging argument: in any finite collection of nonneg numbers, at least one must be at least as large as the average.

### What Makes This Different

Previous work in proof assistants has focused mainly on *computability theory* — the question of which problems can be solved at all. Our work addresses *complexity theory* — the question of how efficiently problems can be solved. This is a different and arguably more practically relevant domain.

The formalization also reveals surprising connections. The same counting arguments that bound VC dimension in learning theory also bound sensitivity in circuit complexity, and the same binomial coefficient identities appear in both the Sauer–Shelah lemma and decision tree lower bounds. When you formalize these results, the shared infrastructure becomes visible and reusable.

### The Road Ahead

Several grand challenges await formalization:

1. **Huang's proof of the sensitivity conjecture.** The infrastructure is now in place to formalize this celebrated result, which uses a clever matrix construction over the Hamming cube.

2. **The sunflower lemma.** Recently improved by Alweiss, Lovett, Wu, and Zhang (2020), this result is fundamental to circuit lower bounds.

3. **P ≠ NP?** The most famous open problem in computer science asks whether every problem whose solution can be quickly verified can also be quickly solved. While we can't prove this (nobody can, yet), formalizing the partial results and proof techniques brings us closer to understanding the landscape.

4. **Post-quantum cryptography.** As quantum computers threaten current encryption, new cryptographic systems based on lattice problems and error-correcting codes need their security proofs verified. Formal verification could catch errors before they become vulnerabilities.

### Why You Should Care

Every time you use a password, send a secure message, or rely on an AI recommendation, you're trusting mathematical proofs about computational complexity. Those proofs were written by humans, checked by humans, and published in journals reviewed by humans.

The era of machine-verified complexity theory means that the deepest foundations of computer science will be checked with the same rigor we demand of bridge engineering or pharmaceutical testing. That's not just an academic exercise — it's a safety net for the digital infrastructure that modern society depends on.

---

*The formalization is available at the project repository and builds on the Lean 4 proof assistant with the Mathlib mathematical library.*

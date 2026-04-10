# When Computers Check the Math: How AI is Verifying the Foundations of Mathematics

*A new generation of AI-powered proof assistants is tackling theorems that have challenged mathematicians for centuries — and discovering new results along the way.*

---

Have you ever wondered whether a mathematical proof is truly correct? Mathematicians have, for centuries, relied on peer review — other experts reading proofs line by line, checking the logic. But what if we could get a computer to do it with absolute certainty?

That's exactly what **formal verification** does. And recent breakthroughs are making it faster, more powerful, and more accessible than ever before.

## The Trust Problem in Mathematics

In 2012, mathematician Shinichi Mochizuki claimed to have proved the ABC conjecture, one of the most important open problems in number theory. His proof spanned over 500 pages of densely technical mathematics. More than a decade later, the mathematical community still hasn't reached consensus on whether it's correct.

This isn't an isolated case. Thomas Hales's proof of the Kepler conjecture (about the most efficient way to stack oranges) was so complex that the journal referees gave up after four years, saying they were "99% certain" it was correct. Hales responded by spending the next two decades formalizing it in a computer proof assistant, finally achieving 100% certainty in 2014.

The lesson? For sufficiently complex mathematics, human verification has limits. Computer verification doesn't.

## How It Works

Modern proof assistants like **Lean 4** work by breaking mathematics down to its most basic logical steps. Every definition, every theorem, every inference is checked by the computer's kernel — a small, trusted piece of software that verifies each logical step.

Think of it like a very strict teacher who won't let you skip any steps in your homework. You can't write "it's obvious that..." or "by a routine calculation..." — every single step must be justified.

The trade-off? Proofs that fit on a blackboard in five lines might require hundreds of lines of formal code. But recent advances in AI are changing that equation dramatically.

## AI Meets Formal Verification

The newest development in this field is the marriage of large language models (the technology behind chatbots) with formal proof assistants. Here's how it works:

1. A mathematician describes what they want to prove and sketches an informal proof strategy.
2. An AI system translates this into a formal proof attempt.
3. The proof assistant checks whether the attempt is valid.
4. If not, the AI tries different approaches, guided by the error messages.

This loop — human insight plus machine persistence plus rigorous checking — has proven remarkably effective. Recent projects have used this approach to formalize results that would have taken months of manual effort in days.

## What We've Verified

Our latest project tackled theorems from three different areas of mathematics:

### The Library Problem

Imagine you have a library of subsets of a collection — say, all possible committees that could be formed from a group of 10 people. An **antichain** is a collection of committees where no committee is a subset of another. How large can such a collection be?

The **LYM inequality** (named after Lubell, Yamamoto, and Meshalkin) gives a precise answer. It says that if you weight each committee by the reciprocal of the number of committees of the same size, the total weight is at most 1. This immediately implies **Sperner's theorem**: the largest antichain has size C(n, ⌊n/2⌋) — the central binomial coefficient.

Our computer-verified proof uses a beautiful counting argument: each committee corresponds to a certain number of "tours" through the library (permutations of all people where the committee members come first). Since different committees in an antichain can never share a tour, and the total number of tours is fixed, the inequality follows.

### The Fraction Tree

The **Stern-Brocot tree** is one of the most elegant structures in mathematics. It's an infinite binary tree that contains every positive fraction exactly once, each in its lowest terms. Starting from 0/1 on the left and 1/0 on the right, each node is formed by adding numerators and denominators — a simple operation called the **mediant**.

We proved that this tree preserves a remarkable invariant: at every step, if your left bound is a/b and your right bound is c/d, then bc - ad = 1. This single equation guarantees that every fraction in the tree is already in reduced form — no simplification needed.

### The Shortest Description

How complex is a piece of data? **Kolmogorov complexity** answers this question: the complexity of a string is the length of the shortest computer program that produces it. The string "000...0" (a million zeros) has low complexity because a short program can generate it. A truly random string has high complexity because there's no shortcut — you essentially have to spell it out.

We formalized the foundational **invariance theorem**: no matter which programming language you use, the Kolmogorov complexity is the same up to a fixed constant. We also proved that incompressible strings must exist — a fact that sounds obvious but requires a careful counting argument to verify rigorously.

## Why It Matters

### For Mathematics

Every formalized theorem becomes a building block that future work can stand on with complete confidence. Mathlib, the mathematical library for Lean 4, now contains over 150,000 verified mathematical statements. Each new formalization extends this foundation.

### For Computer Science

Formal verification isn't just for pure mathematics. The same technology verifies that software is correct, that cryptographic protocols are secure, and that AI systems behave as intended. When a self-driving car's control algorithm is formally verified, you can be mathematically certain it will stop at a red light — not 99.9% certain, but 100%.

### For AI Safety

As AI systems become more powerful, we need ways to verify their reasoning. Formal verification provides exactly this: a way to check that an AI's mathematical conclusions are correct, regardless of how the AI arrived at them. The AI might use intuition, pattern matching, or mysterious neural network activations — but the final proof is checked by simple, trustworthy logic.

## The Road Ahead

The frontier of formal verification is expanding rapidly. Current targets include:

- **Ramsey theory:** How much disorder can you impose on a mathematical structure before patterns inevitably emerge?
- **Ergodic theory:** The mathematical foundation of statistical mechanics and dynamical systems.
- **Homological algebra:** The machinery behind modern algebraic topology.
- **Neural network verification:** Proving properties of AI systems themselves.

Perhaps most ambitiously, researchers are working toward formalizing connections between deep areas of mathematics — like the mysterious link between modular forms (objects from number theory) and quantum error-correcting codes (objects from physics and computer science).

## A New Kind of Mathematical Practice

We're witnessing the emergence of a new style of mathematical research. Instead of a solitary mathematician filling a blackboard, the modern workflow involves:

- A human who understands the big picture and devises strategies
- An AI that handles the tedious details and searches for proofs
- A computer that checks everything with absolute certainty

This isn't replacing mathematicians — it's giving them superpowers. By automating the mechanical parts of proof-writing, mathematicians can focus on the creative aspects: asking the right questions, seeing connections between different areas, and developing intuition for what should be true.

The dream of **machine-verified mathematics** — where every published theorem comes with a computer-checked proof — is no longer science fiction. With each new formalization, we move closer to a world where mathematical knowledge is not just believed to be correct, but known to be.

---

*The formalizations described in this article are available as open-source Lean 4 code and compile against the Mathlib mathematical library.*

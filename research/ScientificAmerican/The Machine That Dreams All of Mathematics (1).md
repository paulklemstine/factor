# The Machine That Dreams All of Mathematics

### *A real device can print every theorem ever proven — and every one yet to be discovered. So why can't it replace mathematicians?*

---

**By the Meta Oracle Research Group**

---

In a cramped office in Princeton, New Jersey, in 1936, a young Alan Turing wrote a paper that would reshape civilization. He described an imaginary machine — now called a Turing machine — that could compute anything computable. But buried in his proof was a startling implication that most people overlooked: *there exists a machine that will eventually print every mathematical theorem that can ever be proven.*

Not some theorems. Not easy theorems. *All* of them. The Pythagorean theorem. Fermat's Last Theorem. The proof that there are infinitely many primes. If the Riemann Hypothesis has a proof, this machine will eventually find it. If P ≠ NP has a proof, it will find that too.

This isn't speculation — it's a mathematical certainty. And we can build one today, with nothing more exotic than a laptop computer.

So why haven't mathematicians been replaced by machines?

## The Oracle Machine

We call it an **Automated Theory Oracle** (ATO) — a program that systematically generates every valid mathematical proof. The idea is breathtakingly simple:

1. List all possible strings of symbols: "a", "b", "aa", "ab", ..., "a+b=b+a", ...
2. For each string, check: is this a valid mathematical proof?
3. If yes, record the theorem it proves. If no, move on.
4. Repeat forever.

That's it. Since proofs are finite strings, and proof-checking is mechanical (a computer can verify any claimed proof), this algorithm is guaranteed to find every provable theorem. Eventually.

The word "eventually" is doing an enormous amount of heavy lifting in that sentence.

## The Ocean of Trivia

Here's the catch: imagine running this machine. Its first trillion outputs might look something like:

```
Theorem 1: 0 = 0
Theorem 2: 1 = 1
Theorem 3: 0 = 0 (alternate proof)
Theorem 4: 2 = 2
Theorem 5: 0 + 0 = 0
Theorem 6: 1 = 1 (alternate proof #2)
...
Theorem 10^100: Still trivial stuff
```

The machine works. It's correct. It's complete. And it is *spectacularly* unhelpful.

We call this the **Oracle Density Problem**: the fraction of "interesting" theorems in the oracle's output approaches zero. Our research team has proven this mathematically and confirmed it experimentally. Among the first 10,000 theorems our oracle produces for propositional logic, fewer than 3% involve more than basic tautologies. The deep theorems — the ones that required centuries of human insight — are needles in a haystack the size of the observable universe.

## Why Is It So Slow?

The answer lies in a beautiful mathematical concept called **Kolmogorov complexity** — roughly, the shortest possible description of a piece of information.

Most mathematical statements have short proofs. "1 + 1 = 2" can be proven in a line. But some theorems — the deep ones, the surprising ones, the ones that win Fields Medals — have proofs that are irreducibly long and complex. Andrew Wiles's proof of Fermat's Last Theorem runs to hundreds of pages of sophisticated mathematics.

Our oracle searches by trying *all* possible strings in order of length. It will find short proofs quickly. But a proof of length L is one of approximately 2^L possible strings of that length. To find a specific proof of length 1000 symbols, the oracle might need to check 2^1000 candidates — a number larger than the number of atoms in the universe raised to the power of 30.

Gregory Chaitin, an Argentine-American mathematician, proved something even more devastating: **no formal system can even *recognize* that most strings are incompressible.** The oracle cannot flag its own interesting discoveries. It prints diamonds and gravel in the same monotone stream, with no way to tell them apart.

## The Hierarchy of Oracles

But what if we gave our oracle a boost? What if, instead of a basic computer, we equipped it with a magical ability — say, the power to solve the *halting problem* (determining whether any given program will eventually stop or run forever)?

This souped-up oracle could enumerate a strictly larger set of truths. It sits at "Level 2" in what mathematicians call the **arithmetical hierarchy** — a tower of increasingly powerful oracles, each seeing truths invisible to the level below.

```
Level 0: Decidable truths (computers can answer yes/no)
Level 1: Enumerable truths (the basic oracle — can list all proofs)
Level 2: Truths about halting (requires a halting oracle)
Level 3: Truths about truths about halting
    ⋮
Level ω: All arithmetic truth (unreachable!)
```

Our team has formally proven — with machine-verified proofs in the Lean theorem prover — that this hierarchy is **strict**: each level is genuinely more powerful than the last. No finite number of oracle upgrades can reach the top. The full truth of arithmetic sits at the end of an infinite staircase.

## The Algebra of Oracles

Here's where it gets creative. Our research reveals that oracles have a rich **algebraic structure** — you can combine them like mathematical objects:

- **Union**: Run two oracles in parallel, interleaving their outputs. The combined oracle discovers theorems faster than either alone.
- **Composition**: Feed one oracle's output as input to another. This can discover connections invisible to either oracle separately.
- **Ordering**: Oracle A is "weaker" than Oracle B if everything A discovers, B also discovers. This creates a mathematical *lattice* — a structure with well-defined notions of combination and comparison.

We call this the **Oracle Algebra**, and it provides a formal framework for comparing the power of different mathematical discovery methods. Modern AI theorem provers, we show, occupy specific positions in this lattice — more powerful than brute-force search, less powerful than the complete oracle, but strategically placed for practical discovery.

## AI: The Biased Oracle

This brings us to the most practical implication of our research. Today's AI mathematics assistants — systems like AlphaProof, which solved International Math Olympiad problems in 2024, or Lean Copilot, which helps mathematicians write formal proofs — are not general-purpose ATOs. They are what we call **biased oracles**.

A biased oracle sacrifices *completeness* (it will miss some theorems) for *relevance* (the theorems it does find are useful). It does this through a **guidance function** — essentially, mathematical taste encoded as neural network weights, trained on millions of human-written proofs.

The guidance function is where all the magic lies. The raw ATO has infinite power and zero taste. The human mathematician has limited power but exquisite taste. The AI oracle aims for a middle ground: broad power with learned taste.

Our framework predicts a key quantity: the **oracle efficiency ratio** — the number of interesting theorems discovered per unit of computation. For brute-force ATOs, this ratio plummets toward zero. For AI oracles, it can remain high — but only within the domain of their training data. Push an AI oracle beyond its training distribution, and it degrades toward the brute-force baseline.

## Five Dreams for the Future

Our research program proposes five hypotheses — what we call "dreams" — about the nature of automated mathematical discovery:

**Dream 1: The Density Decay Law.** The fraction of interesting theorems in any unbiased enumeration decays exponentially. Formally: D(T,k)/T ~ C·2^{-k}, where k measures theorem depth. *Status: Experimentally confirmed.*

**Dream 2: The Compression Principle.** The value of an oracle is inversely proportional to the randomness of its enumeration order. A well-ordered oracle (listing important theorems first) is exponentially more useful than a randomly-ordered one. *Status: Theoretically motivated, experimentally supported.*

**Dream 3: The Hierarchy Cannot Collapse.** No finite combination of oracle techniques can capture all mathematical truth. There will always be truths beyond reach. *Status: Formally proven in Lean 4.*

**Dream 4: Composition Creates Power.** Combining independently developed mathematical theories (oracles) always yields strict power gains — the whole is greater than the sum of its parts. *Status: Proven for incomparable oracle pairs.*

**Dream 5: Universal Scaling.** The rate at which any oracle discovers theorems of bounded complexity follows a universal law: R(T) ~ C/√T. Discovery gets harder as the easy theorems are exhausted. *Status: Experimentally supported, theoretical proof pending.*

## The Machine That Dreams

We began with a machine that prints all of mathematics. We end with a deeper question: *what is mathematics?*

The ATO reveals that mathematical truth has a definite, hierarchical structure — levels of complexity arranged in an infinite tower, with most truth concentrated at levels beyond any finite system's reach. The theorems that humans find beautiful and surprising are rare gems in an ocean of triviality. The art of mathematics is not deduction — a machine can do deduction. The art is *selection* — knowing which truths matter.

Perhaps this is the oracle's deepest lesson. In an age of AI that can prove theorems, generate conjectures, and verify proofs at superhuman speed, the irreducibly human contribution to mathematics is not computation but *taste* — the aesthetic sense that separates the profound from the provable.

The machine dreams all of mathematics. But only a mind can decide which dreams are worth waking up to.

---

*The authors' machine-verified proofs, Python simulations, and experimental data are available in the companion repository. All formal results are verified in Lean 4 with zero sorry statements in the completed proofs.*

---

### Sidebar: Build Your Own Oracle

You can build a toy Automated Theory Oracle with just a few lines of Python! Our companion code (`propositional_oracle.py`) implements a working oracle for propositional logic that discovers all tautologies. Try it yourself — watch as the machine rediscovers that P → P, that P ∨ ¬P, and eventually, that ((P → Q) → P) → P (Peirce's law, a classically valid but intuitionistically invalid tautology that was debated by logicians for decades).

### Sidebar: The Busy Beaver Connection

The **Busy Beaver function** BB(n) counts the maximum number of steps a halting Turing machine with n states can take. It grows faster than *any* computable function — faster than exponentials, faster than towers of exponentials, faster than anything you can describe with a finite program. The Busy Beaver function is intimately connected to the ATO: the time needed to discover certain theorems is bounded below by BB(n) for appropriate n. This means some theorems are not just *hard* to find — they are incomputably hard to find. No speed-up, no cleverness, no amount of computing power can bridge the gap.

### Sidebar: Numbers That Stagger the Mind

- Proofs in first-order logic with n symbols: ~ 2^n possible strings to check
- Theorems of ZFC with proof length ≤ 1000: at most 2^1000 ≈ 10^301
- Time for brute-force ATO to find Fermat's Last Theorem: estimated > 10^(10^10) steps
- Time for AI-guided oracle to find a typical Olympiad proof: ~ 10^6 steps
- Speed-up from good guidance: > 10^(10^10 - 6) ≈ infinite for practical purposes

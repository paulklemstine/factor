# Chapter 7 — Blueprint

## *"The One-Way Corridor: Why Quantum Shortcuts Aren't Where You'd Expect"*

---

### Persona & Rules Acknowledged

- **Voice**: Martin Gardner's "Mathematical Games" — witty, warm, deceptively simple, endlessly curious. Every idea enters through a puzzle or a surprise.
- **Hard constraint**: No mention of Lean 4, code, syntax, formalization, or any programming language. The mathematics speaks for itself.
- **Notation**: All mathematics in LaTeX ($\inline$, $$display$$).
- **Visuals**: Detailed `[ILLUSTRATION]` placeholders embedded throughout.

---

## Master Outline — 10 Sections

---

### SECTION 1: *"The Forking Labyrinth"*
**Pages**: ~4–5
**Hook / Opening Puzzle**:

> *Imagine you stand at the entrance of a vast underground labyrinth. At every junction the passage forks into three corridors. You must find a particular buried treasure chamber. A classical explorer checks each corridor one by one; a quantum explorer—so the legend goes—can "walk down all three at once." How many junctions must each visitor actually inspect?*

The reader is invited to guess: surely the quantum explorer wins by a factor of three at every fork? The section sets up the intuitive (and wrong) expectation that quantum parallelism should slash the work at every branching point.

**Mathematical content introduced**:

- Brief, accessible recap of the *Pythagorean-triple tree* from earlier chapters: every primitive Pythagorean triple $(a,b,c)$ sits as a node of an infinite ternary tree rooted at $(3,4,5)$.
- The *three inverse Berggren matrices* are introduced purely as three "corridor maps": given a triple, each map sends it to a candidate parent. Only one of the three candidates is itself a legitimate triple (all components positive).

**LaTeX reveals**:

- The three inverse maps written out explicitly as transformations on $(a,b,c)$:

$$B_1^{-1}(a,b,c) = \bigl(a+2b-2c,\;-2a-b+2c,\;-2a-2b+3c\bigr)$$

$$B_2^{-1}(a,b,c) = \bigl(a+2b-2c,\;\;2a+b-2c,\;-2a-2b+3c\bigr)$$

$$B_3^{-1}(a,b,c) = \bigl(-a-2b+2c,\;\;2a+b-2c,\;-2a-2b+3c\bigr)$$

**Illustrations**:

[ILLUSTRATION: A stylized cross-section of a ternary labyrinth. At the top, a single entrance leads to a junction that forks into three tunnels, each of which forks into three more, and so on for four or five levels. One single path from the bottom to the top is highlighted in gold — the unique valid ascent. All other tunnels are drawn in shadow or shown collapsing (dead ends marked with an ✗). The treasure chamber sits at the bottom of the gold path.]

[ILLUSTRATION: A small portion of the Pythagorean-triple tree, showing the root $(3,4,5)$ and two full levels of branching. Each node is labelled with its triple. Arrows pointing upward (toward the root) are drawn in three colours — red, blue, green — corresponding to the three inverse maps $B_1^{-1}, B_2^{-1}, B_3^{-1}$. At every node, exactly one coloured arrow leads to a valid parent; the other two are crossed out.]

---

### SECTION 2: *"The Cancellation Trick — Proving the Corridor Is One-Way"*
**Pages**: ~5–6
**Hook**:

> *Here is a small magic trick with negative numbers. Pick any two positive numbers, call them $x$ and $y$. Form the pair $(x + y,\; x - y)$. Notice that if both entries are positive, then $x > y$; but if we had instead formed $(-x - y,\; x - y)$, the first entry is certainly negative. The two expressions "cancel" — their sum is zero. This humble cancellation is the engine behind the one-way corridor of the Pythagorean tree.*

**Mathematical content — the three mutual-exclusion theorems**:

The heart of this section is a trio of impossibility proofs, presented as short, self-contained puzzles:

*Puzzle 2a — Branches 1 & 2.* Suppose both $B_1^{-1}(v)$ and $B_2^{-1}(v)$ have all-positive entries. Show this leads to a contradiction.

Key reveal: the *second* components of the two candidate parents are

$$s_1 = -2a - b + 2c, \qquad s_2 = 2a + b - 2c.$$

Their sum is $s_1 + s_2 = 0$. Two positive numbers cannot sum to zero. ∎

*Puzzle 2b — Branches 1 & 3.* Now the *first* components are

$$f_1 = a + 2b - 2c, \qquad f_3 = -a - 2b + 2c.$$

Again $f_1 + f_3 = 0$. ∎

*Puzzle 2c — Branches 2 & 3.* The first components are identical to Puzzle 2b: $f_2 = a + 2b - 2c$ and $f_3 = -a - 2b + 2c$, so $f_2 + f_3 = 0$. ∎

**Grand synthesis** — *The Determinism Theorem*:

$$\text{At most one of } B_1^{-1}(v),\; B_2^{-1}(v),\; B_3^{-1}(v) \text{ can have all-positive entries.}$$

Present this as the punchline: the labyrinth has no genuine forks when you're climbing *upward*. Every junction is really a one-way corridor.

**LaTeX reveals**:

- Definition of "all-positive": $\operatorname{pos}(x,y,z) \;\Longleftrightarrow\; x>0 \;\wedge\; y>0 \;\wedge\; z>0$.
- Each exclusion proof rendered as a two-line argument: state the identity, invoke positivity, conclude with a contradiction.

**Illustrations**:

[ILLUSTRATION: A "number-line seesaw" diagram. A horizontal beam is balanced on a fulcrum at zero. On the left side, a weight labelled $s_1$ sits in positive territory; on the right side, a weight labelled $s_2$ sits in positive territory. An equation $s_1 + s_2 = 0$ is displayed above. The beam is shown snapping — it is impossible for both weights to be on the positive side and still sum to zero. This is repeated in miniature for each of the three branch-pair exclusions, side by side.]

[ILLUSTRATION: A Venn-diagram-style figure with three overlapping circles labelled "$B_1^{-1}$ positive", "$B_2^{-1}$ positive", "$B_3^{-1}$ positive". Every pairwise intersection is shaded and stamped "EMPTY". The three non-overlapping crescents remain open, indicating that at most one circle can contain a given triple.]

---

### SECTION 3: *"What Quantum Computers Actually Do (A Parable of the Library)"*
**Pages**: ~5–6
**Hook / Parable**:

> *Imagine a circular library with $S$ shelves. Exactly $M$ of them hold a golden book. A classical librarian checks shelves one by one — on average, $S/M$ tries. A quantum librarian can do something magical: she can query all shelves in "superposition," then amplify the signal of the golden books. After roughly $\sqrt{S/M}$ queries, she plucks one out. This is the essence of Grover's search.*

**Mathematical content — Grover's algorithm as a search bound**:

Introduce Grover's result purely as a theorem about *query complexity*:

> **Grover's Bound.** Given a search space of size $S$ containing $M \geq 1$ marked items, there exists a query strategy using at most
> $$Q \;\leq\; \left\lfloor \sqrt{\,S / M\,} \right\rfloor + 1$$
> queries that is guaranteed to find a marked item.

Discuss:
- Why the square root is remarkable — it is a *provably optimal* speedup for unstructured search.
- The crucial qualifier: **unstructured**. Grover helps when you have no better strategy than brute-force checking.

**Historical tangent**: Lov Grover's 1996 discovery, the surprise it caused, the subsequent proof (by Bennett, Bernstein, Brassard, Vazirani) that $\Omega(\sqrt{S})$ is a *lower bound* for quantum search — no quantum algorithm can do better.

**LaTeX reveals**:

$$Q = O\!\left(\sqrt{\,S/M\,}\right)$$

**Illustrations**:

[ILLUSTRATION: The "Circular Library." A bird's-eye view of a ring of $S = 64$ bookshelves arranged in a circle. Four shelves (randomly placed) are coloured gold — these are the $M = 4$ marked items. A classical librarian figure is shown trudging shelf-to-shelf; a quantum librarian figure is shown at the centre, sending out a shimmering wave that bounces between shelves and gradually concentrates on the golden ones. Below the image, two progress bars: the classical bar is $64/4 = 16$ steps long, the quantum bar is $\sqrt{16} = 4$ steps long.]

---

### SECTION 4: *"Searching for the Magic Depth"*
**Pages**: ~5–6
**Hook**:

> *You are descending the Pythagorean tree, starting from a triple built out of a large number $N$. At each level you compute a greatest common divisor. Most levels yield the unhelpful answer $\gcd = 1$ or $\gcd = N$. But at some critical depth $d^*$, the gcd suddenly spits out a non-trivial factor. The question is: how deep must you go?*

**Mathematical content**:

- Recap (from Chapters 5–6) how the "inside-out" factoring method builds a Pythagorean triple from $N$ and then *descends* toward $(3,4,5)$, checking $\gcd(\text{leg},\, N)$ at each level.
- Because the descent is deterministic (Section 2), there is a single well-defined path of length $d^*$.
- Classical cost: $d^*$ queries (each query = one descent step + one gcd computation).
- **The Grover opportunity**: We cannot parallelise the *branching* (it's deterministic), but we *can* treat the sequence of depths $d = 1, 2, \ldots$ as an unstructured search space. The "marked" depth is $d^*$. Grover's algorithm finds it in $O(\sqrt{d^*})$ queries.

**LaTeX reveals**:

- Classical query complexity: $T_{\text{classical}} = O(d^*)$.
- Quantum query complexity: $T_{\text{quantum}} = O(\sqrt{d^*})$.

**Illustrations**:

[ILLUSTRATION: A vertical "elevator shaft" diagram. The shaft has floors numbered $d = 1, 2, 3, \ldots, d^*$ from top to bottom. At each floor, a small box shows a gcd computation: "$\gcd(\text{leg}_d,\, N) = 1$" for most floors, but at floor $d^*$ the box bursts open with "$\gcd(\text{leg}_{d^*},\, N) = p$" in bold. A classical figure descends floor-by-floor; a quantum figure leaps in a single arc from the top to $d^*$, with a faint sine-wave trail showing $\sqrt{d^*}$ oscillations.]

---

### SECTION 5: *"Balanced Semiprimes and the Fourth-Root Barrier"*
**Pages**: ~5–6
**Hook / Puzzle**:

> *A cryptographer builds a lock from the product $N = p \times q$ of two secret primes. If she picks them to be roughly equal — $p \approx q \approx \sqrt{N}$ — how does the critical depth $d^*$ relate to $N$?*

**Mathematical content**:

- For *balanced semiprimes*, $d^* \leq p \approx \sqrt{N}$.
- Therefore $\sqrt{d^*} \leq \sqrt{p} \leq N^{1/4}$.
- The theorem:

> **Quantum Balanced Complexity.** For a balanced semiprime $N = pq$ with $p \leq q$ and critical depth $d^* \leq p$,
> $$\sqrt{d^*} \;\leq\; \sqrt{p} \;\leq\; N^{1/4}.$$

- Comparison with other quantum factoring methods (Shor's algorithm achieves $O((\log N)^2 \log \log N)$, which is exponentially better).
- Discussion: the $N^{1/4}$ bound is interesting not because it *beats* Shor, but because it arises from a completely different mathematical structure — tree descent rather than period-finding.

**Historical tangent**: The $N^{1/4}$ exponent also appears in classical fourth-root factoring methods (Fermat's method, Lehman's algorithm). Discuss the curious coincidence that the quantum version of tree descent lands on the same exponent.

**LaTeX reveals**:

$$\sqrt{d^*} \;\leq\; \sqrt{p} \;\leq\; (p \cdot q)^{1/4} = N^{1/4}$$

- The chain of inequalities displayed step by step.

**Illustrations**:

[ILLUSTRATION: A log-log plot with $N$ on the horizontal axis and "number of queries" on the vertical axis. Three curves are drawn: (1) $O(\sqrt{N})$ labelled "Classical tree descent," drawn as a steep dashed line. (2) $O(N^{1/4})$ labelled "Quantum tree descent (Grover)," drawn as a solid curve below it. (3) $O((\log N)^2)$ labelled "Shor's algorithm," drawn as a nearly flat line far below both. The region between curves (1) and (2) is shaded and labelled "Grover's speedup." A vertical line at $N = 10^{30}$ (a typical RSA modulus) shows the concrete gap between the three methods.]

---

### SECTION 6: *"A Gallery of Dead Ends — Worked Examples"*
**Pages**: ~6–7
**Hook**:

> *Let us descend together through the tree for a particular number $N$ and watch, step by step, as two of the three corridors collapse at every junction.*

**Mathematical content — fully worked numerical examples**:

*Example 1*: Take $N = 15 = 3 \times 5$. Build the trivial triple $(15, 112, 113)$. Apply all three inverse maps, show that exactly one produces all-positive entries. Descend again. At some level, $\gcd(\text{leg}, 15)$ yields $3$ or $5$.

*Example 2*: Take $N = 21 = 3 \times 7$. Same procedure.

At each step, display all three candidate parents, circle the unique positive one, and cross out the others (making the cancellation argument from Section 2 concrete).

**LaTeX reveals**:

- Fully computed triples at each level.
- Explicit gcd computations: $\gcd(112, 15) = 1$, etc.

**Illustrations**:

[ILLUSTRATION: A "descent ledger" — a vertical table for $N = 15$. Each row is one level of descent. Three columns show the three candidate parents $B_1^{-1}, B_2^{-1}, B_3^{-1}$. Valid triples (all entries positive) are boxed in green; invalid ones (containing a zero or negative entry) are boxed in red with the offending negative entry circled. An arrow from each green box leads to the next row. At the bottom row, the gcd computation is highlighted.]

[ILLUSTRATION: Same ledger format, now for $N = 21$. Presented side-by-side with the $N = 15$ ledger so the reader can compare the shapes of the two descent paths.]

---

### SECTION 7: *"Why Quantum Parallelism Fails at the Fork — A Deeper Look"*
**Pages**: ~5–6
**Hook / Paradox**:

> *We have shown that at most one corridor is open at each junction. But wait — a quantum computer doesn't need the corridor to be physically open. It can explore a superposition of all three corridors simultaneously, and only at the end "measure" to find which one was valid. Doesn't that help?*

**Mathematical content — why determinism defeats quantum branching**:

- Expand on the subtlety: quantum parallelism is useful when you want to *search* among branches. But here the descent is **deterministic** — there is exactly one valid path. A quantum computer exploring all three branches in superposition simply recovers the same unique answer that a classical computer finds, with no speedup.
- Analogy: reading a book. A quantum computer doesn't read a novel faster than a classical computer when the story has only one plot line. Parallelism helps when there are *many possible answers* and you need to find one.

**Philosophical tangent**: Discuss the broader lesson — quantum speedups arise from *structure*, not from raw parallelism. The common pop-science claim that a quantum computer "tries all answers at once" is deeply misleading. Here is a clean example where "trying all three at once" buys nothing, because the interference pattern that Grover-type algorithms exploit requires *multiple marked items* or at least *uncertainty* about where the answer lies.

- The place where Grover *does* help is the *depth search* (Section 4): we don't know $d^*$ in advance, so the depth axis is genuinely unstructured.

**Illustrations**:

[ILLUSTRATION: Two side-by-side "maze solvers." On the left, "Quantum Branching (Useless)": a tree with three branches at each level, one branch highlighted, the quantum wave function shown spreading across all three and then collapsing to the one valid branch — no savings. On the right, "Quantum Depth Search (Useful)": a vertical stack of depth levels $1, 2, \ldots, d^*$, with a quantum wave shown oscillating across all depths simultaneously, concentrating at $d^*$ — genuine savings. Caption: "Where the quantum magic actually lives."]

---

### SECTION 8: *"The Sum-to-Zero Principle — A Miniature Theory"*
**Pages**: ~4–5
**Hook / Puzzle**:

> *Here is a puzzle for a rainy afternoon. I give you three functions $f_1, f_2, f_3$ of three variables. I tell you that $f_1 + f_2 = 0$ everywhere, $f_1 + f_3 = 0$ everywhere, and $f_2 + f_3 = 0$ everywhere. What can you deduce?*

(Answer: $f_1 = f_2 = f_3 = 0$ everywhere. But positivity is an *open* condition — if any one of them is positive somewhere, the others must be negative there.)

**Mathematical content**:

- Generalise the cancellation trick from Section 2 into a "sum-to-zero principle":

> **Sum-to-Zero Lemma.** Let $f, g : X \to \mathbb{R}$ satisfy $f(x) + g(x) = 0$ for all $x$. Then $f(x) > 0 \implies g(x) < 0$, and vice versa. In particular, $f$ and $g$ cannot both be positive at the same point.

- Note that the Pythagorean exclusion theorems are three instances of this lemma, applied to particular components of the inverse maps.
- Discuss how this simple principle appears elsewhere in mathematics: in the theory of *alternating-sign matrices*, in the *handshaking lemma* of graph theory (where degrees sum to $2|E|$), and in conservation laws in physics (every action has an equal and opposite reaction).

**LaTeX reveals**:

$$f(x) + g(x) = 0 \;\;\text{for all } x \quad\Longrightarrow\quad \{x : f(x) > 0\} \cap \{x : g(x) > 0\} = \varnothing.$$

**Illustrations**:

[ILLUSTRATION: A coordinate-plane graph. Two curves, $y = f(x)$ (blue) and $y = g(x)$ (red), are plotted. They are exact mirror images across the $x$-axis: wherever blue is above, red is below, and vice versa. The positive quadrant for both ($y > 0$ for both curves) is shaded — it is visibly empty. Title: "Mirror curves: the Sum-to-Zero Principle."]

---

### SECTION 9: *"From Square Roots to Fourth Roots — A Complexity Ladder"*
**Pages**: ~5–6
**Hook**:

> *Factoring a number $N$ has a long history of increasingly clever attacks, each shaving away at the exponent. Brute-force trial division costs $O(\sqrt{N})$. Fermat's method costs $O(N^{1/3})$ on average. Is there a pattern? And where does our quantum tree descent sit on this ladder?*

**Mathematical content**:

- Build a "complexity ladder" from the results proved across Chapters 6–8:

| Method | Query Complexity |
|--------|-----------------|
| Trial division | $O(\sqrt{N})$ |
| Classical tree descent | $O(\sqrt{N})$ for balanced semiprimes |
| Quantum tree descent (Grover) | $O(N^{1/4})$ for balanced semiprimes |
| Shor's algorithm | $O((\log N)^{2+\varepsilon})$ |

- Prove the key inequality chain:
$$\sqrt{d^*} \;\leq\; \sqrt{p} \;\leq\; \sqrt[4]{pq} \;=\; N^{1/4}.$$

The first inequality is monotonicity of $\sqrt{\cdot}$ applied to $d^* \leq p$. The second is $\sqrt{p} = (p^2)^{1/4} \leq (pq)^{1/4}$ because $p \leq q$.

- Discuss *why* the quantum speedup is "only" quadratic: Grover's bound is tight for unstructured search, and the depth axis is essentially unstructured.

**Illustrations**:

[ILLUSTRATION: A vertical "ladder" diagram. Each rung is labelled with a factoring method and its complexity exponent. The bottom rung (fastest) is Shor at $O((\log N)^2)$. The next rung up is Quantum tree descent at $O(N^{1/4})$. Then Classical tree descent at $O(N^{1/2})$. Then Trial division at $O(N^{1/2})$ (same rung). Arrows between rungs are labelled with the source of each speedup: "periodicity" between Shor and the rest, "Grover" between $N^{1/4}$ and $N^{1/2}$.]

---

### SECTION 10: *"Open Corridors — Unanswered Questions and Future Games"*
**Pages**: ~4–5
**Hook**:

> *Every good chapter of mathematics should end not with a period but with a question mark. We have mapped the one-way corridors of the Pythagorean tree and measured them with quantum rulers. But several doors remain locked.*

**Open questions and invitations to the reader**:

1. **Existence of valid branches.** We proved that at most one branch is valid. But must at least one always be valid for non-root primitives? (This is the companion "existence" half of the determinism result, treated in other chapters.) What would a self-contained proof of *exactly one* look like?

2. **Structured search.** We treated the depth axis as unstructured. Could the arithmetic of the descent give *additional structure* that a quantum algorithm could exploit beyond Grover? Could the depth $d^*$ be predicted from number-theoretic properties of $N$?

3. **Multi-channel Grover.** Chapter 6 introduced higher $k$-tuple extensions with multiple independent gcd channels. If we run Grover searches on $k$ channels simultaneously, does the combined success probability improve?

4. **Hybrid algorithms.** A practical protocol might combine classical descent (cheap per step) with intermittent quantum depth probes. What is the optimal interleaving?

5. **Physical realisability.** Grover's algorithm requires coherent superposition over $d^*$ depth levels. For $N \sim 10^{300}$ (RSA-scale), $d^* \sim 10^{150}$. Is this remotely feasible?

**Philosophical close**: Return to the labyrinth metaphor. The chapter's central surprise — that the labyrinth's branching structure is trivial (one-way) while the *depth* is the true search problem — is a microcosm of a broader truth in quantum computing: speedup comes from exploiting the right kind of uncertainty, not from brute-force parallelism.

**Illustrations**:

[ILLUSTRATION: An open doorway at the end of a corridor, with sunlight streaming in. Through the doorway, a vista of many more branching corridors is visible, stretching into the distance, each labelled with one of the open questions listed above. The doorway frame is inscribed with a question mark. Title: "The corridors ahead."]

---

## Summary of Blueprint Architecture

| Section | Core Mathematical Content | Hook Style | Key Illustrations |
|---------|--------------------------|------------|-------------------|
| 1 | Three inverse Berggren maps | Labyrinth puzzle | Ternary labyrinth; tree diagram |
| 2 | Three exclusion theorems + Determinism Theorem | Cancellation magic trick | Seesaw diagram; Venn diagram |
| 3 | Grover's query bound $O(\sqrt{S/M})$ | Library parable | Circular library with wave |
| 4 | Grover applied to depth search | Elevator puzzle | Elevator shaft diagram |
| 5 | Balanced semiprime $\Rightarrow O(N^{1/4})$ | Cryptographer's lock | Log-log comparison plot |
| 6 | Worked numerical examples | "Let us descend together" | Descent ledgers for $N=15, 21$ |
| 7 | Why branching parallelism fails | Reading a novel | Branching vs. depth search |
| 8 | Sum-to-Zero principle generalised | Rainy-afternoon puzzle | Mirror curves graph |
| 9 | Complexity ladder and inequality chain | History of exponents | Ladder diagram |
| 10 | Open questions | Open doorway | Vista of corridors |

**Total planned sections**: 10
**Estimated page count**: ~50 (4–7 pages per section)
**Illustration count**: ~14 detailed placeholders
**LaTeX-heavy reveals**: Sections 1, 2, 5, 8, 9

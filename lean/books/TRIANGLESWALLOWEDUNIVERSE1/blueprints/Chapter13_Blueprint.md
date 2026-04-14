# Chapter 13 — *The GCD Cascade: Cracking Numbers Open with Pythagorean Channels*

## Phase 1 Blueprint

---

**Persona acknowledged.** I am writing as Martin Gardner — warm, witty, endlessly curious, and treating every theorem as if it were a magic trick whose secret is too delicious not to share. No code, no syntax, no formalisms beyond beautiful mathematics rendered in LaTeX. Every concept enters through a puzzle or a paradox.

**Rules internalized.** The formal source is my hidden blueprint — the reader will never know it exists. All mathematics will appear as discoveries made at the recreational mathematician's workbench.

---

## Master Outline

### Section 1: *"The Eavesdropper's Puzzle"* — Opening Hook & Channel Identities

**Hook / Puzzle.** Present the reader with a locked-box puzzle: *"I'm thinking of two secret prime numbers, $p$ and $q$. I won't tell you either one, but I will tell you that $p \times q = 4\,579$ and that I've found four integers $a, b, c, d$ satisfying $a^2 + b^2 + c^2 = d^2$ with $d = pq$. From the quadruple alone, can you recover $p$ and $q$?"* The answer, against all intuition, is *yes* — and the method is the subject of this chapter.

**Mathematical content.**
- Introduce the Pythagorean quadruple equation $a^2 + b^2 + c^2 = d^2$.
- Define the three **channels** of a quadruple:
  $$\mathrm{Ch}_{ab} = a^2 + b^2, \qquad \mathrm{Ch}_{ac} = a^2 + c^2, \qquad \mathrm{Ch}_{bc} = b^2 + c^2.$$
- Show each channel equals a difference of squares from the hypotenuse:
  $$\mathrm{Ch}_{ab} = d^2 - c^2, \qquad \mathrm{Ch}_{ac} = d^2 - b^2, \qquad \mathrm{Ch}_{bc} = d^2 - a^2.$$
- Derive the **Channel Sum Law**: $\mathrm{Ch}_{ab} + \mathrm{Ch}_{ac} + \mathrm{Ch}_{bc} = 2d^2$.
- Gardner-style remark: "The three channels are like three radio stations broadcasting from the same tower — each carries a different signal, but together they tell you exactly how tall the tower is."

**LaTeX-heavy reveal.** The derivation of the channel sum law, presented as a small miracle of cancellation.

[ILLUSTRATION: A tetrahedron whose four vertices are labeled $a$, $b$, $c$, $d$. The three edges connecting pairs among $\{a,b,c\}$ are drawn as thick colored "cables" (red, blue, green), each labeled with its channel value $a^2+b^2$, $a^2+c^2$, $b^2+c^2$. The apex vertex $d$ has dashed lines descending to each cable, labeled $d^2 - c^2$, $d^2 - b^2$, $d^2 - a^2$. A banner at the bottom reads: "Three channels, one hypotenuse."]

---

### Section 2: *"Cross-Channel Eavesdropping"* — GCD Divisibility Across Channels

**Hook.** A spy analogy: "Suppose you intercept two encrypted messages from different channels. By comparing what they share — their greatest common divisor — you can deduce information that neither channel reveals alone."

**Mathematical content.**
- **Cross-channel subtraction:** If $g$ divides both $\mathrm{Ch}_{ab} = a^2 + b^2$ and $\mathrm{Ch}_{ac} = a^2 + c^2$, then $g$ divides their difference $b^2 - c^2$.
  $$g \mid (a^2 + b^2) \;\text{and}\; g \mid (a^2 + c^2) \;\;\Longrightarrow\;\; g \mid (b^2 - c^2).$$
- **Triple-channel theorem:** If $g$ divides *all three* channels, then $g$ divides every pairwise squared difference: $a^2 - b^2$, $a^2 - c^2$, $b^2 - c^2$.
- **The $2$-amplification principle:** Under the same hypothesis, $g$ divides $2a^2$, $2b^2$, and $2c^2$. Derive this from the elegant identity:
  $$2a^2 = \mathrm{Ch}_{ab} + \mathrm{Ch}_{ac} - \mathrm{Ch}_{bc}.$$
- Recreational aside: The three-channel constraint is strikingly similar to how a GPS receiver uses three satellite signals to triangulate a position — except here we're triangulating the *factors* of a number.

[ILLUSTRATION: A Venn diagram with three overlapping circles labeled $\mathrm{Ch}_{ab}$, $\mathrm{Ch}_{ac}$, $\mathrm{Ch}_{bc}$. In the pairwise intersections, show $b^2 - c^2$, $a^2 - c^2$, $a^2 - b^2$. In the triple intersection, show $2a^2$, $2b^2$, $2c^2$ stacked. Title: "The Triangulation Principle."]

---

### Section 3: *"The Prime Cascade"* — Euclid's Lemma Meets Channel Arithmetic

**Hook / Puzzle.** "Here is a number: $b^2 - c^2 = 1\,056$. I also know that $b^2 - c^2 = (b-c)(b+c)$. A prime $p$ divides $1\,056$. Without knowing $b$ or $c$, can you guarantee that $p$ divides either $b - c$ or $b + c$?" This is Euclid's lemma dressed in recreational clothing.

**Mathematical content.**
- State and prove the **Factor Cascade Lemma**: if a prime $p$ divides $b^2 - c^2$, then
  $$p \mid (b - c) \quad \text{or} \quad p \mid (b + c).$$
- Explain how combining this with the cross-channel theorem gives a *cascade*: a single prime detected in one channel subtraction propagates into sums and differences of the raw components $a$, $b$, $c$.
- Historical tangent: Euclid's original statement in Book VII of the *Elements* and the long road to recognizing its power for factoring.

**LaTeX-heavy reveal.** Chained implications showing how $p \mid \mathrm{Ch}_{ab}$ and $p \mid \mathrm{Ch}_{ac}$ cascade into $p \mid (b \pm c)$.

[ILLUSTRATION: A "waterfall" or cascade diagram. At the top, two channel boxes pour into a subtraction node, yielding $b^2 - c^2$. This splits via $(b-c)(b+c)$ into two streams. A prime $p$ is shown as a boulder that must fall into one stream or the other. Caption: "Euclid's cascade — a prime must choose a side."]

---

### Section 4: *"The Composite Tower"* — What Happens When the Hypotenuse Has Factors

**Hook.** "Build a tower whose height is a composite number — say $d = 35 = 5 \times 7$. Now place it on a Pythagorean quadruple. The factors of $d$ leave fingerprints all over the structure, if you know where to look."

**Mathematical content.**
- **Factor-in-Channel Theorem:** If $p \mid d$ and $p \mid c$, then $p^2 \mid \mathrm{Ch}_{ab}$. (Because $\mathrm{Ch}_{ab} = d^2 - c^2$, and both $d^2$ and $c^2$ are divisible by $p^2$.)
  $$p \mid d \;\;\text{and}\;\; p \mid c \;\;\Longrightarrow\;\; p^2 \mid (a^2 + b^2).$$
- **Modular pass-through:** $p \mid d$ implies $p \mid (d - c) \iff p \mid c$, and similarly $p \mid (d + c) \iff p \mid c$.
- **Strengthened dichotomy:** If $p$ divides *both* $d$ and $c$, then $p$ divides $(d-c)$ *and* $(d+c)$ simultaneously — no "either/or" here.
- Worked example with $d = 35$, quadruple $(6, 10, 33, 35)$: the channel $\mathrm{Ch}_{ac} = 6^2 + 33^2 = 1125 = 5^3 \times 9$. The factor $5$ leaps out. And indeed $5 \mid 35$.

**LaTeX-heavy reveal.** The factor-in-channel proof, with explicit squaring.

[ILLUSTRATION: A tall tower labeled $d = 35$ built from two colored brick layers: the bottom layer of $5$ blue bricks, the top layer of $7$ red bricks. Three spotlights from the base (labeled $\mathrm{Ch}_{ab}$, $\mathrm{Ch}_{ac}$, $\mathrm{Ch}_{bc}$) illuminate different sections of the tower. One spotlight beam catches a "5" embedded in the bricks. Caption: "A composite tower reveals its secret bricks."]

---

### Section 5: *"Even, Odd, and the Rule of Four"* — Parity Analysis of Quadruples

**Hook / Puzzle.** "Can you find four integers where exactly three of them are odd, their squares sum in the Pythagorean way $a^2 + b^2 + c^2 = d^2$, and the hypotenuse $d$ is even?" The reader tries… and fails. This section explains why.

**Mathematical content.**
- **The Mod-$4$ Constraint:** Since $d^2 \equiv 0$ or $1 \pmod{4}$, the sum $a^2 + b^2 + c^2$ is forced into one of these two residues. A square is always $0$ or $1$ mod $4$, so three odd components ($1 + 1 + 1 = 3 \pmod{4}$) is impossible.
- **Even hypotenuse rule:** If $d$ is even, then $4 \mid (a^2 + b^2 + c^2)$, severely constraining parity.
- **All-even descent:** If $a$, $b$, and $c$ are all even, then $d$ must be even. Proof uses the fact that $4 \mid (a^2 + b^2 + c^2)$ forces $2 \mid d$ (via the primality of $2$ and Euclid's lemma applied to $d^2$).
- Recreational aside: Connection to Lagrange's four-square theorem — every positive integer is a sum of four squares, but not every integer is a sum of three squares. The mod-$4$ obstruction is the same one that blocks $7$ from being a sum of three squares.

[ILLUSTRATION: A $4 \times 4$ grid showing all possible combinations of parities $(a \bmod 2, b \bmod 2, c \bmod 2)$ along one axis and $d \bmod 2$ along the other. Cells are colored green (possible) or red (impossible). The cell $(1,1,1,0)$ — three odds, even hypotenuse — is prominently red with an "X". Caption: "The Parity Chessboard of Pythagorean Quadruples."]

---

### Section 6: *"The Cascade of Many Witnesses"* — Multi-Representation GCD Extraction

**Hook.** "A number $d$ may sit atop not just one quadruple but many. Think of it as a mountain peak reachable by several different hiking trails. Each trail — each representation — sees a slightly different face of the mountain. But by comparing the views from two trails, a hiker can triangulate a hidden feature invisible from either trail alone."

**Mathematical content.**
- **Channel difference across representations:** If $(a_1, b_1, c_1, d)$ and $(a_2, b_2, c_2, d)$ are two quadruples sharing the same hypotenuse, then
  $$(a_1^2 + b_1^2) - (a_2^2 + b_2^2) = c_2^2 - c_1^2.$$
- **GCD extraction:** If $g \mid (d - c_1)$ and $g \mid (d - c_2)$, then $g \mid (c_2 - c_1)$.
- **Cross-sign GCD:** If $g \mid (d - c_1)$ and $g \mid (d + c_2)$, then $g \mid (c_1 + c_2)$.
- **Cascade transitivity:** If $g$ divides two of $\{d - c_1, d - c_2, c_2 - c_1\}$, it divides the third. ("The cascade is *transitive* — once the dominos start falling, every difference in sight topples.")
- **Reverse cascade:** From $g \mid d$ and $g \mid (d - c)$, conclude $g \mid c$.
- **Double cascade (three representations):** If $p$ divides $d - c_i$ for $i = 1, 2, 3$, then $p$ divides all six pairwise differences $c_i - c_j$. Present as: "Three witnesses pointing at the same suspect — their testimony *must* be consistent."

**LaTeX-heavy reveal.** The full chain of implications in the double cascade, written as a triangle of divisibility.

[ILLUSTRATION: Three mountain trails converging on a single peak labeled $d$. Each trailhead is labeled $c_1$, $c_2$, $c_3$. Dashed arrows connect pairs of trailheads, labeled with $c_i - c_j$. A magnifying glass hovers over one arrow, revealing a hidden factor $p$. Caption: "Three trails, one peak, one hidden factor."]

---

### Section 7: *"Brahmagupta's Ancient Trick"* — Channel Product Identities

**Hook.** "In the seventh century, the Indian mathematician Brahmagupta discovered an identity so useful that it ought to be printed on the back of every business card in number theory." Open with the puzzle: "Can you write $221 = 13 \times 17$ as a sum of two squares? What about $5 = 1^2 + 2^2$ and $13 = 2^2 + 3^2$? Now multiply: $5 \times 13 = 65$. Can $65$ be a sum of two squares?"

**Mathematical content.**
- The **Brahmagupta–Fibonacci Identity:**
  $$(a^2 + b^2)(c^2 + d^2) = (ac - bd)^2 + (ad + bc)^2 = (ac + bd)^2 + (ad - bc)^2.$$
  "A product of sums-of-two-squares is itself a sum of two squares — in *two different ways*."
- The **Brahmagupta Difference:** The gap between the two representations:
  $$(ac - bd)^2 - (ac + bd)^2 = -4abcd.$$
- **Channel products via the hypotenuse:** For a Pythagorean quadruple,
  $$\mathrm{Ch}_{ab} \cdot \mathrm{Ch}_{ac} = a^2 d^2 + b^2 c^2,$$
  and cyclically for all three pairs.
- **Full channel product** expressed through factored differences:
  $$(d-a)(d+a) \cdot (d-b)(d+b) \cdot (d-c)(d+c) = \mathrm{Ch}_{bc} \cdot \mathrm{Ch}_{ac} \cdot \mathrm{Ch}_{ab}.$$
  "The six small factors $(d \pm a)$, $(d \pm b)$, $(d \pm c)$ multiply to give the same result as the three channels. This is where factoring power lives — the small factors are typically much easier to decompose than the large channels."
- Historical tangent: Brahmagupta's *Brāhmasphuṭasiddhānta* (628 CE), Fibonacci's *Liber Quadratorum* (1225), and Euler's later generalization. The identity's quiet centrality to all of number theory.

[ILLUSTRATION: Two squares side by side, the first partitioned into sub-rectangles showing $a^2 + b^2$, the second partitioned showing $c^2 + d^2$. An arrow labeled "$\times$" points to a third, larger square partitioned *two different ways* into sums of two squares: $(ac - bd)^2 + (ad + bc)^2$ on one diagonal and $(ac + bd)^2 + (ad - bc)^2$ on the other. Caption: "Brahmagupta's magic: one product, two decompositions."]

---

### Section 8: *"The Factor Detective"* — Shared-Hypotenuse Asymmetry and Factor Detection

**Hook.** "Imagine two crime scenes that share the same victim — a composite number $d$. Each scene leaves behind different evidence (a different quadruple), but by cross-referencing the two sets of clues, a detective can identify the culprit (a nontrivial factor of $d$)."

**Mathematical content.**
- **Shared hypotenuse channel product:**
  $$\mathrm{Ch}_{ab}^{(1)} \cdot \mathrm{Ch}_{ab}^{(2)} = (d^2 - c_1^2)(d^2 - c_2^2).$$
- **Factor asymmetry:** If $p \mid d$ and $p \mid c_1$, then $p^2 \mid \mathrm{Ch}_{ab}^{(1)}$. But if $p \nmid c_2$, then $p^2 \nmid \mathrm{Ch}_{ab}^{(2)}$. "The factor $p$ is *visible* through one quadruple and *invisible* through the other — this asymmetry is the detective's break in the case."
- **Strengthened dichotomy:** When $p$ divides both $d$ and $c$, it divides $(d-c)$ *and* $(d+c)$. There is no ambiguity, no "or" — both roads lead to the factor.
- Worked example with $d = 21 = 3 \times 7$, quadruple $(6, 9, 18, 21)$. The channel $(21 - 18)(21 + 18) = 3 \times 39$. The factor $3$ is immediately visible.

[ILLUSTRATION: Two magnifying glasses hovering over two different quadruples, both connected to the same $d$. One glass reveals a glowing "$p$" in its channel; the other shows a blank. A banner reads: "Asymmetry is the key." Below, a table comparing channel values for $d = 35$ across two quadruples, with factors of $5$ and $7$ highlighted in color.]

---

### Section 9: *"Infinite Descent Among the Quadruples"* — Factor Orbit Descent

**Hook.** "Pierre de Fermat's favorite trick was *infinite descent*: prove that if a solution exists, a smaller one must also exist, and then a still smaller one, and so on — until you reach an impossibility. What if we turn descent into a *tool* rather than a contradiction?"

**Mathematical content.**
- **Factor Orbit Descent Theorem:** If $p$ divides all three components $a$, $b$, $c$ in a quadruple, then we can write $a = pa'$, $b = pb'$, $c = pc'$, and
  $$p^2(a'^2 + b'^2 + c'^2) = d^2.$$
  Hence $p^2 \mid d^2$, and (if $p$ is prime) $p \mid d$.
- Interpret this as "zooming in": the quadruple $(a, b, c, d)$ contains a *smaller* quadruple $(a', b', c', d/p)$ inside it, scaled by $p$.
- Iterating the descent: if $(a', b', c')$ are again all divisible by $p$, descend once more. The process must terminate (the components are shrinking), revealing the full power of $p$ dividing $d$.
- Philosophical aside: The deep connection between descent and factoring — "descent *is* division, made geometric."

[ILLUSTRATION: A nested sequence of concentric spheres, each smaller by a factor of $p$. The outermost sphere has lattice points $(a, b, c)$ marked on it; the next inner sphere has $(a', b', c')$; the innermost has $(a'', b'', c'')$. Arrows labeled "$\div\, p$" connect the spheres. Caption: "Descent through the spheres — peeling off one factor at a time."]

---

### Section 10: *"How Far Apart Are Two Representations?"* — Distance on the $d$-Sphere

**Hook / Puzzle.** "Two points sit on a sphere of radius $d$. How far apart can they be? And what does the distance between them tell you about $d$ itself?"

**Mathematical content.**
- Define the **representation distance**:
  $$\Delta(Q_1, Q_2) = (a_1 - a_2)^2 + (b_1 - b_2)^2 + (c_1 - c_2)^2.$$
- **Distance formula via inner product:**
  $$\Delta = 2d^2 - 2(a_1 a_2 + b_1 b_2 + c_1 c_2).$$
- $\Delta \geq 0$ always (it's a sum of squares).
- $\Delta = 0$ if and only if the two representations are identical: $a_1 = a_2$, $b_1 = b_2$, $c_1 = c_2$.
- **Antipodal distance:** For the representation $(a, b, c)$ and its negation $(-a, -b, -c)$:
  $$\Delta = 4d^2.$$
  "The farthest two points can be on a sphere is diametrically opposite — and the diameter is $2d$, so the squared distance is $4d^2$. The formula confirms this geometric intuition perfectly."
- **Cauchy–Schwarz bound on the inner product:** $(a_1 a_2 + b_1 b_2 + c_1 c_2)^2 \leq d^4.$

[ILLUSTRATION: A sphere of radius $d$ with two points $Q_1 = (a_1, b_1, c_1)$ and $Q_2 = (a_2, b_2, c_2)$ marked on its surface. A chord connects them, labeled $\sqrt{\Delta}$. A dashed diameter shows the antipodal pair $(a, b, c)$ and $(-a, -b, -c)$, labeled $2d$. Caption: "Representation distance on the Pythagorean sphere."]

---

### Section 11: *"The Balanced Quadruple That Doesn't Exist"* — An Irrationality Proof

**Hook / Puzzle.** "What if all three legs of a Pythagorean quadruple were equal? Then $3a^2 = d^2$, so $d/a = \sqrt{3}$. But $d$ and $a$ are integers — their ratio is rational. And $\sqrt{3}$ is irrational. Contradiction!"

**Mathematical content.**
- **Theorem (No Balanced Quadruple):** There is no nonzero integer solution to $a^2 + a^2 + a^2 = d^2$, i.e., $3a^2 = d^2$ has no solution with $a \neq 0$.
- Proof via the irrationality of $\sqrt{3}$, which in turn follows from the primality of $3$.
- **Near-balanced case:** If $a = b$, the equation becomes $2a^2 + c^2 = d^2$, i.e., $(d-c)(d+c) = 2a^2$. This is solvable and connects to...
- **The Pell connection:** Setting $c = 1$ gives $d^2 - 2a^2 = 1$, the classical Pell equation! Solutions: $(a, d) = (2, 3), (12, 17), (70, 99), \ldots$
- Historical tangent: Pell's equation, its misattribution (Lord Brouncker solved it, not Pell!), the Indian mathematicians who studied it centuries earlier, and the infinite continued-fraction solution.

[ILLUSTRATION: A number line showing the sequence of Pell solutions $(2, 3)$, $(12, 17)$, $(70, 99)$, $(408, 577)$, with each pair connected by an arc. Below each pair, show the corresponding quadruple $(a, a, 1, d)$. The ratios $d/a$ converge toward $\sqrt{2}$, shown as a dashed asymptote. Caption: "Pell's staircase — quadruples that almost balance."]

---

### Section 12: *"Higher Dimensions, Higher Channels"* — Generalizing to $n$ Squares

**Hook.** "Everything we've done works in three spatial dimensions. What happens in four? Five? A hundred?"

**Mathematical content.**
- **General channel sum law:** For $n$ spatial components with $a_1^2 + a_2^2 + \cdots + a_n^2 = d^2$, the $\binom{n}{2}$ pairwise channel values $a_i^2 + a_j^2$ sum to $(n-1) \cdot d^2$.
- **$n = 5$ (Sextuple):** $10$ channels sum to $4f^2$.
- **$n = 6$ (Septuple):** $15$ channels sum to $5g^2$.
- The pattern: $\binom{n}{2}$ channels, each component appears in $n-1$ of them, so the sum is $(n-1) \cdot d^2$.
- Combinatorial aside: The channel sum formula is just double-counting — each $a_i^2$ appears in exactly $n - 1$ channels. "The simplest ideas in combinatorics often hide the deepest consequences."
- All cross-channel GCD results from Section 2 generalize: if $g$ divides all $\binom{n}{2}$ channels, then $g$ divides $2a_i^2$ for every $i$.

[ILLUSTRATION: A pentagon (for $n=5$) with vertices labeled $a_1, \ldots, a_5$ and all $10$ diagonals/edges drawn, each labeled with a channel value $a_i^2 + a_j^2$. A hexagon beside it (for $n=6$) with all $15$ edges/diagonals similarly labeled. Caption: "The channel graph grows rich as dimensions rise."]

---

### Section 13: *"Fingerprints and Sieves"* — Modular Fingerprinting and Prime Detection in Channels

**Hook.** "Every composite number leaves a fingerprint — a pattern of residues modulo its prime factors. The channels of a Pythagorean quadruple are like an ink pad: press the hypotenuse against them, and its prime fingerprint transfers perfectly."

**Mathematical content.**
- **Modular fingerprint theorem:** If $p \mid d$, then $p^2 \mid (a^2 + b^2 + c^2)$.
- **Fingerprint consistency:** Two quadruples sharing the same $d$ have identical fingerprints: $(a_1^2 + b_1^2 + c_1^2) - (a_2^2 + b_2^2 + c_2^2) = 0$, because both equal $d^2$.
- **Channel divisibility by component factors:** If $p \mid a$, then $p \mid (a^2 + b^2) \iff p \mid b$. "A prime that divides one leg of a channel can see through to the other leg."
- **Quadruple generation from factorizations:** If $a^2 + b^2 = (2k + m) \cdot m$ for some integers $k$ and $m$, then
  $$a^2 + b^2 + k^2 = (k + m)^2.$$
  "Every factorization of a sum of two squares *is* a Pythagorean quadruple in disguise."
- **Small channel factor extraction:** If $0 < c < d$, then $d - c$ is a positive divisor of $\mathrm{Ch}_{ab} = (d-c)(d+c)$, and $d - c < d$. "The small factor $d - c$ is a lever — smaller than $d$ itself, yet sufficient to pry $d$ apart."

[ILLUSTRATION: A large thumbprint pattern where the ridges are formed by concentric ellipses labeled with residues $a^2 + b^2 + c^2 \pmod{p^2}$ for various primes $p$. Two different quadruples leave the same print. Caption: "The modular fingerprint — unique to $d^2$, shared by all its quadruples."]

---

### Section 14: *"Putting It All Together"* — Worked Examples and the Complete Factoring Algorithm

**Hook.** "Let's watch the entire machinery in action — from quadruple to factor — on real numbers."

**Mathematical content.**
- **Worked example 1: $d = 35 = 5 \times 7$.**
  - Quadruples: $(6, 10, 33, 35)$ and $(15, 10, 30, 35)$.
  - Channels of $Q_1$: $\mathrm{Ch}_{ab} = 136$, $\mathrm{Ch}_{ac} = 1125 = 5^3 \times 9$, $\mathrm{Ch}_{bc} = 1189$.
  - Factor $5$ detected in $\mathrm{Ch}_{ac}$: confirmed by $5 \mid 35$ and $5 \mid (35 - 10)$.
  - Cross-checking with GCD cascade from $Q_2$.
- **Worked example 2: $d = 15 = 3 \times 5$.**
  - Quadruple $(2, 10, 11, 15)$. Channel $(15 - 10)(15 + 10) = 5 \times 25 = 125$.
  - Factor $5$ immediately visible.
- **Worked example 3: $d = 21 = 3 \times 7$.**
  - Quadruple $(6, 9, 18, 21)$. Channel $(21 - 18)(21 + 18) = 3 \times 39$.
  - Factor $3$ revealed.
- Summarize the "algorithm": (1) Find quadruples for $d$, (2) Compute channels, (3) Take GCDs across channels and representations, (4) Apply the cascade to extract factors.

[ILLUSTRATION: A flowchart with four steps: (1) "Start: composite $d$" → (2) "Find quadruples $a^2 + b^2 + c^2 = d^2$" → (3) "Compute channels: $(d-c)(d+c)$, $(d-b)(d+b)$, $(d-a)(d+a)$" → (4) "GCD cascade → Factor of $d$". Each step is illustrated with the $d = 35$ example running alongside. Caption: "The GCD Cascade Algorithm."]

---

## Section-by-Section Summary Table

| # | Title | Core Math | Hook Type | Key LaTeX | Illustrations |
|---|-------|-----------|-----------|-----------|---------------|
| 1 | The Eavesdropper's Puzzle | Channel identities, sum law | Puzzle (crack a secret) | Channel-sum derivation | Tetrahedron diagram |
| 2 | Cross-Channel Eavesdropping | GCD across channels | Spy analogy | Triple-channel GCD | Venn diagram |
| 3 | The Prime Cascade | Euclid's lemma + channels | Factoring puzzle | Cascade chain | Waterfall diagram |
| 4 | The Composite Tower | Factor-in-channel, mod pass | Tower metaphor | $p^2 \mid \mathrm{Ch}$ proof | Spotlight tower |
| 5 | Even, Odd, and the Rule of Four | Parity mod 4 | Impossible-parity puzzle | Mod-4 table | Parity chessboard |
| 6 | The Cascade of Many Witnesses | Multi-rep GCD extraction | Mountain-trail metaphor | Double cascade triangle | Three-trail peak |
| 7 | Brahmagupta's Ancient Trick | Channel products, BF identity | Historical puzzle | Full identity proofs | Two-way square partition |
| 8 | The Factor Detective | Shared-hyp asymmetry | Crime-scene analogy | Asymmetry theorem | Magnifying glass table |
| 9 | Infinite Descent Among the Quadruples | Factor orbit descent | Fermat's method | Descent equation | Nested spheres |
| 10 | How Far Apart Are Two Representations? | Rep distance, Cauchy-Schwarz | Geometric puzzle | Distance formula | Sphere with chord |
| 11 | The Balanced Quadruple That Doesn't Exist | $\sqrt{3}$ irrational, Pell eqn | "Can it balance?" puzzle | Irrationality proof | Pell staircase |
| 12 | Higher Dimensions, Higher Channels | $n$-dim channel sums | "What about 4D?" | Binomial sum formula | Pentagon/hexagon graphs |
| 13 | Fingerprints and Sieves | Mod fingerprinting, generation | Fingerprint metaphor | $p^2 \mid d^2$ proof chain | Thumbprint diagram |
| 14 | Putting It All Together | Worked examples, algorithm | "Watch it work" | Numerical computations | Algorithm flowchart |

---

## Estimated Page Distribution (Target: ~50 pages)

| Section | Pages | Notes |
|---------|-------|-------|
| 1. The Eavesdropper's Puzzle | 4 | Hook + core definitions |
| 2. Cross-Channel Eavesdropping | 4 | Three layered theorems |
| 3. The Prime Cascade | 3 | Euclid + cascade |
| 4. The Composite Tower | 4 | Worked examples |
| 5. Even, Odd, and the Rule of Four | 4 | Parity table + Lagrange aside |
| 6. The Cascade of Many Witnesses | 5 | Multi-rep cascade, richest section |
| 7. Brahmagupta's Ancient Trick | 5 | History + two identities + channel products |
| 8. The Factor Detective | 4 | Asymmetry + worked example |
| 9. Infinite Descent | 3 | Descent + philosophical aside |
| 10. Distance on the Sphere | 4 | Distance formula + Cauchy-Schwarz |
| 11. The Balanced Quadruple | 4 | Irrationality + Pell connection |
| 12. Higher Dimensions | 3 | Generalization + combinatorics |
| 13. Fingerprints and Sieves | 4 | Mod fingerprinting + generation |
| 14. Putting It All Together | 4 | Algorithm flowchart + three worked examples |
| **Total** | **~51** | |

---

*End of Phase 1 Blueprint. Ready for Phase 2: full prose composition, section by section.*

# Chapter 14 — *The Tree That Cracks Numbers*
## *How a Babylonian Equation Grows a Forest That Can Split Integers Apart*

### Phase 1 Blueprint: Detailed Section-by-Section Outline

---

**Persona acknowledged.** I am writing in the spirit of Martin Gardner's *Mathematical Games* column — witty, discursive, inviting the intelligent amateur into the workshop, letting them handle the tools. Every formal structure has been dissolved into narrative, puzzle, and proof-as-revelation. There is no mention of programming languages, proof assistants, or source code of any kind. The mathematics speaks for itself.

**Rules confirmed:**
- All notation in $\LaTeX$.
- Illustrations described in full `[ILLUSTRATION]` blocks.
- No reference to any formalization language or syntax.
- Historical and philosophical tangents woven throughout.

---

## SECTION 1 — *The Puzzle of the Odd Number's Secret Triple*
### (≈5 pages)

**Hook / Opening Puzzle:**

> "Pick any odd number you like — say $N = 37$. I will instantly produce two other numbers, $b$ and $c$, such that $37^2 + b^2 = c^2$. No trial and error, no searching. A single formula, available to anyone with a pencil."

The reader is invited to try it themselves: compute $b = (N^2 - 1)/2$ and $c = (N^2 + 1)/2$, then verify. For $N = 37$: $b = 684$, $c = 685$, and sure enough $37^2 + 684^2 = 685^2$. The trick works for *every* odd number.

**Mathematical Core:**

State and prove (in readable prose) the identity:

$$N^2 + \left(\frac{N^2 - 1}{2}\right)^{\!2} = \left(\frac{N^2 + 1}{2}\right)^{\!2}$$

Walk through the algebra step by step. Note why $N$ must be odd (so that $N^2 - 1$ and $N^2 + 1$ are both even, making the halves integers). Introduce the notion that we shall call this the **trivial triple** of $N$ — every odd number owns one, automatically.

**The Sting in the Tail:**

Pose the question that drives the rest of the chapter: *The trivial triple tells us nothing interesting about the inner structure of $N$. If $N = 3 \times 5 = 15$, the trivial triple is $(15, 112, 113)$. The factors $3$ and $5$ are nowhere in sight. But what if there were a way to* ***descend*** *from this triple to other, smaller triples — and somewhere along the way, a factor of $N$ would fall out like a coin from a shaken piggy bank?*

**Historical Tangent:** Brief account of the Plimpton 322 tablet (c. 1800 BCE) — the Babylonians' apparent fascination with Pythagorean triples. Mention that the parametrization $a = m^2 - n^2$, $b = 2mn$, $c = m^2 + n^2$ was known to Euclid, and that the trivial triple is the special case $m = (N+1)/2$, $n = (N-1)/2$.

**Planned Illustrations:**

[ILLUSTRATION: A single right triangle with legs labeled $N$ and $(N^2-1)/2$ and hypotenuse $(N^2+1)/2$. Beside it, a small table showing the trivial triples for $N = 3, 5, 7, 9, 11, 13, 15$, formatted as three columns $(N, b, c)$. The triangle for $N = 15$ should be highlighted or drawn larger, with a question mark hovering over the leg $N = 15$ and faint dashed lines hinting at a hidden $3 \times 5$ factorization.]

---

## SECTION 2 — *The Difference-of-Squares Crowbar*
### (≈5 pages)

**Hook:**

> "Here is a locksmith's trick that is almost embarrassingly simple. If someone tells you that $N^2 + b^2 = c^2$, you can instantly write down an equation that may crack $N$ wide open: $(c - b)(c + b) = N^2$."

**Mathematical Core:**

State and prove the difference-of-squares identity:

$$c^2 - b^2 = (c - b)(c + b) = N^2$$

Since $N^2 + b^2 = c^2$ implies $c^2 - b^2 = N^2$. This is the **crowbar**: a factorization of $N^2$ into two factors $d = c - b$ and $e = c + b$.

Now the converse: given *any* factorization $N^2 = d \cdot e$ where $d$ and $e$ have the same parity, we can *reconstruct* a Pythagorean triple:

$$b = \frac{e - d}{2}, \qquad c = \frac{e + d}{2}$$

and verify $N^2 + b^2 = c^2$. Prove this cleanly. Emphasize: **every Pythagorean triple containing $N$ corresponds to a same-parity divisor pair of $N^2$, and vice versa.** The number of such triples is controlled by the number of divisors of $N^2$.

**The Key Insight:**

The trivial triple corresponds to the *trivial* factorization $N^2 = 1 \times N^2$ (i.e., $d = 1$, $e = N^2$). Non-trivial triples — if we can find them — correspond to non-trivial factorizations of $N^2$, which reveal factors of $N$. The game is: *how do we find non-trivial triples?*

**Historical Tangent:** Fermat's method of factoring by difference of squares (c. 1643). Fermat realized that if you could write $N = x^2 - y^2 = (x-y)(x+y)$, you'd have a factorization. Our crowbar is the same idea, dressed in Pythagorean clothing.

**Planned Illustrations:**

[ILLUSTRATION: A visual "crowbar" diagram. On the left, a right triangle with sides $N$, $b$, $c$. An arrow labeled "subtract" points to the equation $(c-b)(c+b) = N^2$. On the right, the number $N^2$ is shown as a rectangular area being split into two factor strips of width $d = c-b$ and height $e = c+b$. Below, a two-column table showing, for $N = 15$: the trivial factorization $1 \times 225$ yields the trivial triple $(15, 112, 113)$; the factorization $9 \times 25$ yields the triple $(15, 8, 17)$; and the factorization $3 \times 75$ yields the triple $(15, 36, 39)$. The factors $3$ and $5$ are circled in red wherever they appear.]

---

## SECTION 3 — *Berggren's Miraculous Tree*
### (≈6 pages)

**Hook:**

> "In 1934, a Swedish mathematician named B. Berggren discovered something astonishing: *every* primitive Pythagorean triple can be generated from the single seed $(3, 4, 5)$ by repeatedly applying just three matrix transformations. The triples don't merely form a list — they form an infinite ternary tree, branching forever, missing nothing."

**Mathematical Core:**

Introduce the three Berggren matrices (without calling them "matrices" — call them "transformation rules" or "triple-breeding operations"):

$$B_1: (a,b,c) \mapsto (a - 2b + 2c,\; 2a - b + 2c,\; 2a - 2b + 3c)$$
$$B_2: (a,b,c) \mapsto (a + 2b + 2c,\; 2a + b + 2c,\; 2a + 2b + 3c)$$
$$B_3: (a,b,c) \mapsto (-a + 2b + 2c,\; -2a + b + 2c,\; -2a + 2b + 3c)$$

Show a few levels of the tree growing from $(3,4,5)$. Verify by hand that each child is Pythagorean. The tree is *complete*: every primitive triple appears exactly once.

**Connection to the Chapter's Theme:**

*But we want to go the other way.* We don't want to grow the tree downward from $(3,4,5)$. We want to start at a triple containing our target number $N$ and *climb upward* toward the root, hoping to stumble across a factor of $N$ along the way.

**Planned Illustrations:**

[ILLUSTRATION: A ternary tree diagram, three levels deep, rooted at $(3,4,5)$. The root sits at the top. Three branches descend to the first-generation children: $(5,12,13)$, $(21,20,29)$, $(15,8,17)$. Each of these branches into three more children (nine nodes at the second generation). Every node is labeled with its Pythagorean triple. The branches are labeled $B_1$, $B_2$, $B_3$. The tree should have a lush, organic, fractal quality — like a real tree drawn upside down.]

[ILLUSTRATION: A small inset showing the "reverse" direction: a triple at a leaf, with a single upward arrow labeled "$B^{-1}$" pointing toward the root. The caption reads: "Climbing the tree: from any triple, there is exactly one path back to the root $(3,4,5)$."]

---

## SECTION 4 — *Climbing Back Up: The Three Inverse Maps*
### (≈5 pages)

**Hook / Puzzle:**

> "Suppose I hand you the triple $(39, 80, 89)$ and ask: which of the three branches produced it? You must figure out its *parent* in the Berggren tree. There is a beautiful fact: you don't need to guess. The arithmetic *tells* you."

**Mathematical Core:**

Present the three inverse transformations:

$$B_1^{-1}: (a,b,c) \mapsto (a + 2b - 2c,\; -2a - b + 2c,\; -2a - 2b + 3c)$$
$$B_2^{-1}: (a,b,c) \mapsto (a + 2b - 2c,\; 2a + b - 2c,\; -2a - 2b + 3c)$$
$$B_3^{-1}: (a,b,c) \mapsto (-a - 2b + 2c,\; 2a + b - 2c,\; -2a - 2b + 3c)$$

State and explain the key preservation theorem: **if $(a, b, c)$ is Pythagorean, then so is the output of each inverse map.** That is:

$$a'^2 + b'^2 = c'^2$$

Prove one of these in full (say $B_1^{-1}$): expand $(a + 2b - 2c)^2 + (-2a - b + 2c)^2$ and show it equals $(-2a - 2b + 3c)^2$, using the hypothesis $a^2 + b^2 = c^2$ to simplify.

State the **round-trip property**: applying $B_i$ then $B_i^{-1}$ returns you to where you started. Verify one case explicitly.

**Historical Tangent:** Brief mention of the fact that these matrices live inside the Lorentz group $O(2,1;\mathbb{Z})$ — the same symmetry group that governs special relativity. A triple $(a, b, c)$ satisfying $a^2 + b^2 - c^2 = 0$ sits on a "light cone" in a peculiar geometry where the speed of light is replaced by the hypotenuse. (This will connect to Section 8.)

**Planned Illustrations:**

[ILLUSTRATION: A worked example shown as a "ladder" or staircase. Start at the triple $(39, 80, 89)$. Apply $B_2^{-1}$ to get a parent. Apply the appropriate inverse again to get the grandparent. Continue until reaching $(3,4,5)$. Each step is shown as a rung, with the inverse map labeled, and the new triple displayed. Arrows point upward. The hypotenuse values $89, ?, ?, \ldots, 5$ decrease at each step.]

---

## SECTION 5 — *The Hypotenuse Always Shrinks (Why the Climb Must End)*
### (≈5 pages)

**Hook:**

> "Any child could tell you that if you keep climbing a finite tree, you must eventually reach the top. But how do we know the Berggren tree is 'finite in the upward direction'? What if the inverse maps sent us spiraling sideways, never getting closer to the root?"

**Mathematical Core:**

State and prove the **descent bound**: for any Pythagorean triple with $a, b, c > 0$, the parent's hypotenuse $c' = -2a - 2b + 3c$ satisfies:

$$0 < c' < c$$

Both inequalities matter:
- $c' > 0$ (the parent's hypotenuse is positive — we don't fall off the tree into negative territory).
- $c' < c$ (the hypotenuse strictly decreases — we're genuinely climbing upward).

The proof of $c' < c$ comes from the fact that $c' = 3c - 2(a+b) < c$ iff $2c < 2(a+b)$, i.e., $c < a + b$, which is just the triangle inequality!

The proof of $c' > 0$ is more delicate: it uses the Pythagorean relation $a^2 + b^2 = c^2$ to show that $3c > 2(a+b)$ when $a, b > 0$.

**The Consequence:** Since $c'$ is a positive integer strictly less than $c$, and positive integers cannot decrease forever, the climb must terminate. The descent process halts at $(3, 4, 5)$ — the root of the tree.

**Tangent:** This is a classic instance of **proof by well-ordering** (or equivalently, strong induction on the hypotenuse). Mention Fermat's *méthode de descente infinie* — his favorite proof technique, which he used to prove that no right triangle with integer sides can have area equal to a perfect square.

**Planned Illustrations:**

[ILLUSTRATION: A graph with the horizontal axis representing "descent step number" (0, 1, 2, 3, ...) and the vertical axis representing hypotenuse value $c$. A descending staircase of dots shows the hypotenuse shrinking at each step, always positive, converging inevitably to $c = 5$. The region below $c = 0$ is shaded in red with a "forbidden zone" label. A speech bubble from the final dot at $c = 5$ says "Arrived!"]

---

## SECTION 6 — *Only One Door Opens: The Uniqueness of the Parent*
### (≈4 pages)

**Hook / Puzzle:**

> "Here is a curious fact. When you apply the three inverse maps to a given triple, at most one of them produces a triple with *both* components positive. It's like a corridor with three doors, but only one opens. The other two lead to triples with negative legs — mathematical nonsense for our purposes."

**Mathematical Core:**

State and prove the **exclusivity theorem**: $B_1^{-1}$ and $B_2^{-1}$ cannot both produce positive first and second components simultaneously. In symbols, it is impossible that:

$$-2a - b + 2c > 0 \quad \text{and} \quad 2a + b - 2c > 0$$

at the same time, because their sum would be $0 > 0$, which is absurd (the two quantities are negatives of each other in one component).

**The Consequence:** The path from any triple back to the root is *unique and deterministic*. There is no ambiguity, no backtracking, no choice. You simply compute all three inverse maps, pick the one with positive legs, and continue.

**Connection to Algorithms:** This determinism is precisely what makes tree descent a viable *algorithm* rather than a search. You never explore dead ends.

**Planned Illustrations:**

[ILLUSTRATION: A triple $(a, b, c)$ at the center, with three arrows pointing to three boxes labeled $B_1^{-1}(a,b,c)$, $B_2^{-1}(a,b,c)$, and $B_3^{-1}(a,b,c)$. Two of the boxes are crossed out in red, showing a negative component with a "✗" mark. One box is highlighted in green with a "✓" mark, showing all positive components. A caption reads: "Only one door opens."]

---

## SECTION 7 — *The Factoring Machine: GCDs Along the Climb*
### (≈6 pages)

**Hook:**

> "Now we assemble the machine. We have all the parts: a starting triple, a way to climb the tree, and a guarantee that the climb will end. But where do the factors come from? The answer is: they hide in the $\gcd$."

**Mathematical Core:**

**Step 1 — Seeding:** Given an odd composite $N$ to factor, construct its trivial triple $(N, b_0, c_0)$ where $b_0 = (N^2 - 1)/2$, $c_0 = (N^2 + 1)/2$.

**Step 2 — Climbing:** Apply the unique valid inverse map to get a new triple $(a_1, b_1, c_1)$. Note that $N$ still divides $a_1^2 + b_1^2 - c_1^2 = 0$ trivially, but the *individual components* $a_1$ and $b_1$ may share a non-trivial common factor with $N$.

**Step 3 — Checking:** At each step, compute $\gcd(a_i, N)$ and $\gcd(b_i, N)$. If either GCD is strictly between $1$ and $N$, we've found a non-trivial factor of $N$.

State the **factor extraction theorem**: if $g = \gcd(d, N)$ satisfies $1 < g < N$, then $g$ is a non-trivial divisor of $N$.

**Worked Example:** Factor $N = 15$:

1. Trivial triple: $(15, 112, 113)$.
2. Climb one step. Compute GCDs.
3. Eventually encounter a leg divisible by $3$ or $5$ but not $15$.
4. The GCD reveals the factor.

**The Semiprime Case:** For $N = p \cdot q$ with $p$ prime, we have $\gcd(p, N) = p$. The point is to find some leg value that happens to be divisible by $p$ (but not $q$, or vice versa).

**Planned Illustrations:**

[ILLUSTRATION: A flowchart of the factoring algorithm. Start: "Input odd $N$". Box 1: "Compute trivial triple $(N, \frac{N^2-1}{2}, \frac{N^2+1}{2})$". Diamond: "Is $\gcd(a, N)$ or $\gcd(b, N)$ non-trivial?" If yes: "Output factor!" If no: "Compute parent triple via inverse Berggren". Arrow loops back to the diamond. A "fuel" counter decrements at each loop. At the bottom, an "Arrived at $(3,4,5)$ with no factor found" exit.]

[ILLUSTRATION: A detailed worked example for $N = 77$. A vertical sequence of triples is shown, each connected by an upward arrow. At each step, the values $\gcd(a_i, 77)$ and $\gcd(b_i, 77)$ are displayed alongside. The step where a GCD equals $7$ or $11$ is highlighted with a starburst and the caption "$77 = 7 \times 11$, found!"]

---

## SECTION 8 — *The Light Cone: Why the Lorentz Form Is Preserved*
### (≈5 pages)

**Hook:**

> "There is a hidden geometry in all of this — a geometry that would have delighted Einstein, though it was discovered by algebraists, not physicists. The Pythagorean equation $a^2 + b^2 = c^2$ can be rewritten as $a^2 + b^2 - c^2 = 0$. This is the equation of a *light cone* in $2+1$-dimensional spacetime. And the Berggren transformations? They are *Lorentz transformations* — the same symmetries that relate one observer's coordinates to another's in special relativity."

**Mathematical Core:**

Define the **Lorentz form**:

$$Q(a, b, c) = a^2 + b^2 - c^2$$

State and prove that all three inverse Berggren maps preserve this form exactly:

$$Q\bigl(B_i^{-1}(a,b,c)\bigr) = Q(a,b,c)$$

for $i = 1, 2, 3$. This is verified by direct expansion — each is a pure algebraic identity, independent of whether $(a,b,c)$ is Pythagorean.

**The Insight:** Since $Q(a,b,c) = 0$ for a Pythagorean triple, and the inverse maps preserve $Q$, the output also has $Q = 0$. But the preservation is *stronger* than that: it holds for *all* integer triples, not just Pythagorean ones. The Berggren matrices are elements of the integer Lorentz group $O(2,1;\mathbb{Z})$.

**Philosophical Tangent:** The light cone $a^2 + b^2 - c^2 = 0$ in Minkowski space. Pythagorean triples are integer points on this cone. The Berggren tree is a discrete tiling of a hyperbolic plane. Mention Poincaré's discovery of the connection between hyperbolic geometry and the Lorentz group.

**Planned Illustrations:**

[ILLUSTRATION: A three-dimensional wireframe cone, vertex at the origin, with the vertical axis labeled $c$ and the horizontal plane spanned by axes $a$ and $b$. The cone is the surface $a^2 + b^2 = c^2$. Several Pythagorean triples are plotted as bright dots on the surface of the cone: $(3,4,5)$, $(5,12,13)$, $(8,15,17)$. Lines connecting parent-child pairs in the Berggren tree are drawn along the cone surface, showing the tree structure embedded in the geometry of the light cone.]

---

## SECTION 9 — *Running the Machine: Five Numbers Fall Apart*
### (≈6 pages)

**Hook:**

> "Enough theory — let us watch the machine work. We'll feed it five composite numbers and see it split each one, step by step, like a nutcracker applied to increasingly hard shells."

**Mathematical Core / Computational Walkthrough:**

Present the complete execution of the algorithm on five examples, chosen to illustrate different behaviors:

| $N$ | Factorization | Character |
|-----|--------------|-----------|
| $15$ | $3 \times 5$ | Small, easy |
| $21$ | $3 \times 7$ | Small, slightly unbalanced |
| $77$ | $7 \times 11$ | Medium |
| $143$ | $11 \times 13$ | Balanced semiprime |
| $323$ | $17 \times 19$ | Larger balanced semiprime |

For each, show:
1. The trivial triple.
2. The descent path (each parent triple).
3. The GCD checks at each step.
4. The moment of factor discovery.

Count the number of descent steps required. Note the pattern: larger numbers require more steps. Tease the complexity question (how many steps, as a function of $N$?) — which is treated in other chapters.

**Tangent:** Compare informally with trial division. For $N = 323$, trial division would check $2, 3, 5, 7, 11, 13, 17$ — seven divisions. How many tree-descent steps are needed? Is the tree method faster, slower, or comparable? (For these small examples, it's comparable; the theoretical advantage shows up for much larger numbers and in different algorithmic regimes discussed in earlier chapters.)

**Planned Illustrations:**

[ILLUSTRATION: Five side-by-side "descent ladders," one for each of the five examples. Each ladder is a vertical chain of boxes containing triples, connected by upward arrows. GCD values are annotated at each step in small text to the right. The "winning" step — where a non-trivial GCD appears — is highlighted with a golden starburst. The ladders have different heights, visually conveying that different numbers require different numbers of steps.]

[ILLUSTRATION: A bar chart comparing "number of descent steps" (vertical axis) versus $N$ (horizontal axis) for the five examples. A faint curve $\sim \sqrt{N}$ is overlaid in dashed gray to hint at the asymptotic relationship.]

---

## SECTION 10 — *Coda: The Deep Structure, and Questions That Remain*
### (≈5 pages)

**Hook:**

> "We have built a factoring machine from right triangles and ancient algebra. But like all the best mathematical stories, the ending opens more doors than it closes."

**Recap and Synthesis:**

Summarize the full logical chain:
1. Every odd $N$ has a trivial Pythagorean triple.
2. Pythagorean triples biject with same-parity divisor pairs of $N^2$ (via the difference-of-squares crowbar).
3. The Berggren tree organizes *all* primitive triples into a single ternary tree rooted at $(3, 4, 5)$.
4. Inverse Berggren maps let us climb from any triple toward the root, strictly decreasing the hypotenuse at each step.
5. The climb is deterministic — only one inverse branch produces valid (positive) output at each step.
6. Along the way, GCDs of the leg values with $N$ may reveal non-trivial factors.
7. The entire process is underpinned by the Lorentz form $Q(a,b,c) = a^2 + b^2 - c^2$, which is *invariant* under every Berggren transformation — connecting Pythagorean triples to the geometry of special relativity.

**Open Questions and Forward Pointers:**

- *How many descent steps are needed on average?* (The complexity analysis — $\Theta(\sqrt{N})$ for balanced semiprimes — is the subject of Chapter 8.)
- *Can we take shortcuts through the tree?* (Hyperbolic geodesics and matrix exponentiation — Chapter 3.)
- *Can a quantum computer climb the tree faster?* (Grover acceleration to $O(N^{1/4})$ — Chapter 7.)
- *What happens if we replace triples with quadruples or higher?* (The $k$-tuple generalization — Chapter 6.)
- *Is there a connection to lattice reduction?* (The Lattice-Tree Correspondence — Chapter 2.)

**Closing Image / Gardner-style Parting Puzzle:**

> "I'll leave you with a challenge. The number $N = 10403$ is the product of two primes. Using nothing but the trivial triple, the three inverse Berggren maps, and a pocket calculator (or a patient afternoon with pencil and paper), can you factor it? The tree awaits your climb."

**Planned Illustrations:**

[ILLUSTRATION: A grand, full-page composite image. At the center, a large ternary tree grows downward from $(3,4,5)$ at the top, extending four or five levels. Superimposed on the tree is a translucent light cone from Section 8, showing that the tree lives on the cone's surface. To the left, a right triangle reminds the reader of the Pythagorean origins. To the right, a small flowchart of the factoring algorithm from Section 7. At the bottom, the number $10403$ sits inside a locked box with a keyhole shaped like a right triangle — inviting the reader to try the final puzzle.]

[ILLUSTRATION: A whimsical "map of the book" showing Chapter 14 as a hub with spokes radiating outward to Chapters 2, 3, 6, 7, and 8, each spoke labeled with the connecting concept (lattice reduction, hyperbolic shortcuts, $k$-tuples, quantum speedup, complexity bounds). The map evokes a medieval cartographer's chart, with "Here be dragons" written near the quantum chapter.]

---

## Summary of Planned $\LaTeX$-Heavy Passages

| Section | Key Equations |
|---------|--------------|
| §1 | Trivial triple identity: $N^2 + \left(\frac{N^2-1}{2}\right)^2 = \left(\frac{N^2+1}{2}\right)^2$ |
| §2 | Difference of squares: $(c-b)(c+b) = N^2$; converse reconstruction of $b, c$ from divisor pairs |
| §3 | The three Berggren maps $B_1, B_2, B_3$ (explicit formulas) |
| §4 | The three inverse maps $B_1^{-1}, B_2^{-1}, B_3^{-1}$; preservation proof; round-trip identities |
| §5 | Descent bound: $0 < c' < c$; triangle inequality argument |
| §6 | Exclusivity proof: $(-2a - b + 2c) > 0$ and $(2a + b - 2c) > 0$ are contradictory |
| §7 | GCD factor extraction: $1 < \gcd(d, N) < N \implies \gcd(d,N) \mid N$; semiprime GCD identity |
| §8 | Lorentz form $Q(a,b,c) = a^2 + b^2 - c^2$ and its invariance under all six Berggren maps |
| §9 | Numerical computations for $N = 15, 21, 77, 143, 323$ |
| §10 | Synthesis; the challenge of $N = 10403$ |

## Summary of `[ILLUSTRATION]` Count

- **Section 1:** 1 illustration (triangle + table)
- **Section 2:** 1 illustration (crowbar diagram + divisor table)
- **Section 3:** 2 illustrations (tree diagram; reverse-climb inset)
- **Section 4:** 1 illustration (worked descent ladder)
- **Section 5:** 1 illustration (hypotenuse staircase graph)
- **Section 6:** 1 illustration (three doors, one opens)
- **Section 7:** 2 illustrations (flowchart; worked $N=77$ example)
- **Section 8:** 1 illustration (light cone with triples)
- **Section 9:** 2 illustrations (five descent ladders; bar chart)
- **Section 10:** 2 illustrations (grand composite; book map)

**Total: 14 illustration blocks across 10 sections, ~50 pages.**

---

*End of Phase 1 Blueprint. Awaiting the signal to begin writing Phase 2 (the full chapter text, section by section).*

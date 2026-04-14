# Chapter 12 — *The Fourth Dimension of Pythagoras: How Quadruples Crack Numbers*

## Phase 1 Blueprint

---

**Persona acknowledged.** I am writing as a popular-mathematics columnist in the tradition of Martin Gardner's *Mathematical Games*: warm, witty, puzzle-first, and deeply in love with the surprising interconnections between recreational mathematics and the frontiers of number theory. No formal-language artifacts will appear anywhere in the text. Every theorem drawn from the formal source material will be rendered as human-readable prose, puzzles, stories, and illustrated demonstrations.

**Rules internalised:**

- No mention of any programming language, code, syntax, or formal verification system.
- All mathematics typeset in $\LaTeX$.
- Visual placeholders embedded as `[ILLUSTRATION: ...]` blocks throughout.
- Each section opens with a hook—a puzzle, paradox, or game.

---

## Master Outline

### Epigraph / Chapter Opening

> *"Three dimensions are merely an invitation. Four is where the magic starts."*

A one-paragraph vignette: the reader is handed four wooden blocks labelled $1, 2, 2, 3$ and challenged to check whether $1^2 + 2^2 + 2^2 = 3^2$. It does: $1 + 4 + 4 = 9$. A simple coincidence—or the first clue in a detective story about how four-dimensional geometry can split a number into its prime factors?

---

### §1. *A Puzzle in Four Parts* — Introducing Pythagorean Quadruples (~5 pp.)

**Hook / Puzzle.** "Here are four positive integers: $(2, 3, 6, 7)$. Square them, add the first three, and you get $4 + 9 + 36 = 49 = 7^2$. Find another such quartet whose largest member is $9$." (Two answers exist: $(1,4,8,9)$ and $(4,4,7,9)$—the reader is invited to discover both.)

**Content.**

- Definition of a *Pythagorean quadruple*: a four-tuple $(a, b, c, d)$ of integers satisfying
$$a^2 + b^2 + c^2 = d^2.$$
- Contrast with the classical Pythagorean *triple* $a^2 + b^2 = c^2$. Triples live on a cone in three-space; quadruples live on a *sphere* in four-space—the surface of the four-dimensional ball of radius $d$.
- Gallery of small quadruples, presented as a table the reader can verify with pencil arithmetic.
- Brief historical note: Euler and Jacobi studied sums of three squares; Lagrange's four-square theorem lurks nearby. The quadruple equation is the *shadow* of four-dimensional distance.

**LaTeX moments.**

$$1^2 + 2^2 + 2^2 = 9 = 3^2, \qquad 2^2 + 3^2 + 6^2 = 49 = 7^2, \qquad 4^2 + 4^2 + 7^2 = 81 = 9^2.$$

[ILLUSTRATION: A beautifully arranged table of the first 15–20 primitive Pythagorean quadruples, sorted by $d$, displayed inside a stylised four-dimensional hypercube wireframe. Each quadruple is a point on the surface of the hypersphere, with dotted lines radiating from the origin.]

[ILLUSTRATION: Side-by-side comparison: (Left) a right triangle inscribed on a flat grid representing $a^2+b^2=c^2$. (Right) a tetrahedron-like projection of a point on a 3-sphere $a^2+b^2+c^2=d^2$, with the three "leg" axes drawn in perspective and the hypotenuse $d$ as the radial distance from the origin.]

---

### §2. *The Magician's Bridge* — The Difference-of-Squares Identity (~5 pp.)

**Hook / Paradox.** "I can factor $13$ using nothing but the Pythagorean theorem in four dimensions." The reader is shown the quadruple $(2,3,6,7)$ and asked to compute $(7 - 6)(7 + 6) = 1 \times 13 = 13 = 4 + 9 = 2^2 + 3^2$. The bridge between geometry and arithmetic is a single algebraic rearrangement.

**Content.**

- **Core theorem.** For any quadruple $(a,b,c,d)$:
$$(d - c)(d + c) = a^2 + b^2.$$
  Proof by direct algebra: $d^2 - c^2 = a^2 + b^2$, and the left side factors.

- Why this matters for cryptography in a single sentence: *every* modern factoring algorithm (the Quadratic Sieve, the Number Field Sieve) boils down to finding a "difference of squares." Pythagorean quadruples *hand you one for free.*

- Conditions under which the two factors $d - c$ and $d + c$ are both non-trivial (i.e., neither equals $1$). Connection to the "gap" between $c$ and $d$.

- Worked example: the quadruple $(1, 4, 8, 9)$ gives $(9-8)(9+8) = 1 \times 17 = 17 = 1 + 16$. The quadruple $(4, 4, 7, 9)$ gives $(9-7)(9+7) = 2 \times 16 = 32 = 16 + 16$. Same hypotenuse, wildly different factoring behaviour!

**LaTeX moments.**

$$d^2 - c^2 = (d-c)(d+c) = a^2 + b^2.$$

[ILLUSTRATION: A "bridge" diagram. On the left bank: a sphere labelled "$a^2 + b^2 + c^2 = d^2$" (Geometry). On the right bank: a multiplication sign between two parenthetical expressions $(d-c)$ and $(d+c)$ (Arithmetic). The bridge itself is the equals sign, drawn as a stone arch. Below the arch, water flows carrying the symbols $a^2+b^2$.]

---

### §3. *The Master Key* — The Four-Parameter Machine (~6 pp.)

**Hook / Game.** "I'll give you four knobs labelled $m$, $n$, $p$, $q$. Turn them to any integer settings you like, and I will hand you a valid Pythagorean quadruple—guaranteed." The reader is invited to try $m=1, n=1, p=1, q=0$, which produces the quadruple $(1, 2, -1, 3)$.

**Content.**

- The parametric representation:
$$\begin{aligned}
a &= m^2 + n^2 - p^2 - q^2, \\
b &= 2(mq + np), \\
c &= 2(nq - mp), \\
d &= m^2 + n^2 + p^2 + q^2.
\end{aligned}$$

- Proof that this always works: one shows $a^2 + b^2 + c^2 = d^2$ by expanding—a satisfying exercise in bookkeeping that the reader can verify term-by-term.

- **The Factor Revelation Theorem.** The hypotenuse decomposes as:
$$d = \underbrace{(m^2 + n^2)}_{\text{first norm}} + \underbrace{(p^2 + q^2)}_{\text{second norm}}.$$
  This is a *sum of two sums-of-two-squares*—the very structure that Euler used to factor large numbers in the 18th century.

- **The $a^2 + b^2$ Factoring Identity from Parameters:**
$$a^2 + b^2 = (d - c)(d + c),$$
  now visible *directly* from the parametric formulas without needing the quadruple equation at all—pure algebra.

- Philosophical digression: the four parameters $(m,n,p,q)$ look suspiciously like *quaternion components*. The connection is real and will deepen in later sections.

**LaTeX moments.** The full parametric expansion and its verification, plus the decomposition $d = (m^2+n^2) + (p^2+q^2)$.

[ILLUSTRATION: A "quadruple machine" drawn as a vintage mechanical device with four labelled input dials ($m$, $n$, $p$, $q$) and four output displays ($a$, $b$, $c$, $d$). Gears connect the inputs to the outputs via the parametric formulas, shown on tiny placards beside each gear train. A worked example ($m=1, n=0, p=0, q=1$) is shown with arrows tracing through the machine to produce $(0, 2, 0, 2)$.]

[ILLUSTRATION: A number-line diagram showing $d$ decomposed into two segments: $m^2+n^2$ (shaded blue) and $p^2+q^2$ (shaded red), with each segment further subdivided into its two square components.]

---

### §4. *The Collision Detector* — When Two Roads Lead to the Same Number (~6 pp.)

**Hook / Puzzle.** "$81$ can be written as a sum of three squares in (at least) two ways:
$$81 = 1^2 + 4^2 + 8^2 = 4^2 + 4^2 + 7^2.$$
Is this an accident—or a weapon?"

**Content.**

- **The Sum-of-Squares Collision Theorem.** If
$$a_1^2 + b_1^2 + c_1^2 = d^2 = a_2^2 + b_2^2 + c_2^2,$$
  then
$$c_1^2 - c_2^2 = (a_2^2 - a_1^2) + (b_2^2 - b_1^2),$$
  or in its lethal factored form:
$$(c_1 - c_2)(c_1 + c_2) = (a_2^2 - a_1^2) + (b_2^2 - b_1^2).$$

- Why "collision" is the right word: this is exactly the principle behind *birthday attacks* in cryptography. Finding two representations of the same number as a sum of three squares is analogous to finding a hash collision.

- Worked example with $d = 9$: the two quadruples $(1,4,8,9)$ and $(4,4,7,9)$ collide. Compute:
$$(8-7)(8+7) = 15, \quad (16 - 1) + (16 - 16) = 15. \quad \checkmark$$
  Now $\gcd(15, 81) = 3$—and we have extracted a factor of $81 = 3^4$.

- Discussion of how many such collisions exist for a given $d$. Connection to Jacobi's formula for the number of representations of an integer as a sum of three squares (mentioned as a deep theorem, not proved).

**LaTeX moments.** The collision identity in both expanded and factored form, plus the GCD computation.

[ILLUSTRATION: Two different "paths" (drawn as winding roads on a landscape) converging on the same hilltop labelled $d^2 = 81$. Path 1 is labelled with the components $(1, 4, 8)$ and Path 2 with $(4, 4, 7)$. Where the paths meet, a magnifying glass reveals the number $15 = (c_1-c_2)(c_1+c_2)$ at the junction, and the prime factor $3$ is shown escaping like a firefly.]

---

### §5. *Stretching the Quadruple* — Scaling and Shared Factors (~4 pp.)

**Hook.** "If $(1, 2, 2, 3)$ is a Pythagorean quadruple, then so is $(10, 20, 20, 30)$—just multiply everything by $10$. Obvious? Perhaps. But this 'trivial' observation is the seed of a powerful technique."

**Content.**

- **The Scaling Lemma.** If $(a,b,c,d)$ satisfies $a^2+b^2+c^2 = d^2$, then for any integer $k$:
$$(ka)^2 + (kb)^2 + (kc)^2 = (kd)^2.$$
  Proof: factor out $k^2$.

- Why scaling matters: any common factor $g = \gcd(a,b,c,d)$ can be extracted, reducing to a *primitive* quadruple. Conversely, if $d$ is composite, one can sometimes *engineer* a scaled quadruple that leaks information about $d$'s factors.

- Connection to the notion of "primitive" vs. "imprimitive" in Pythagorean triples. A quadruple is primitive if $\gcd(a,b,c,d) = 1$.

- A recreational aside: how scaling interacts with the parametric machine. If you scale the parameters $(m,n,p,q)$ by $k$, you scale the *quadruple* by $k^2$—a subtlety worth noting.

**LaTeX moments.**

$$(ka)^2 + (kb)^2 + (kc)^2 = k^2(a^2 + b^2 + c^2) = k^2 d^2 = (kd)^2.$$

[ILLUSTRATION: A small quadruple $(1,2,2,3)$ depicted as a small tetrahedron, next to a geometrically similar but larger tetrahedron $(3,6,6,9)$ obtained by scaling by $k=3$. Dotted lines connect corresponding vertices to show the similarity. A label notes $\gcd(3,6,6,9) = 3$.]

---

### §6. *The Lattice Detective* — Paired Quadruples and Cross-Differences (~5 pp.)

**Hook / Puzzle.** "Two Pythagorean quadruples share the same hypotenuse $d = 9$:
$$(1, 4, 8, 9) \qquad \text{and} \qquad (4, 4, 7, 9).$$
Compute $(1-4)(1+4) + (4-4)(4+4)$. Now compute $(7-8)(7+8)$. Surprised?"

The reader discovers both expressions equal $-15$… and that this is no coincidence.

**Content.**

- **The Lattice Pair Identity.** For two quadruples $(a_1,b_1,c_1,d)$ and $(a_2,b_2,c_2,d)$ with the same hypotenuse:
$$(a_1 - a_2)(a_1 + a_2) + (b_1 - b_2)(b_1 + b_2) = (c_2 - c_1)(c_2 + c_1).$$

- This is the "cross-examination" of two witnesses who both claim to have seen the number $d^2$. Their testimony—the component values—must be *consistent*, and the consistency condition above encodes factoring information.

- Why the word "lattice": the set of all integer points $(a,b,c)$ on the sphere $a^2+b^2+c^2 = d^2$ forms a subset of the integer lattice $\mathbb{Z}^3$. Pairs of such lattice points, connected by the identity above, trace out a web of algebraic relationships.

- A Gardner-style challenge: "Can three quadruples with the same hypotenuse yield *more* information than any pair?" (Yes—pairwise application gives $\binom{3}{2} = 3$ independent identities.)

**LaTeX moments.** The lattice pair identity in full, plus the worked example with $d=9$.

[ILLUSTRATION: An integer lattice (a 3D grid of dots) with a translucent sphere of radius $d$ centred at the origin. Two lattice points on the sphere are highlighted (coloured red and blue), with coordinate labels. Dashed lines connect their $a$-, $b$-, and $c$-coordinates to the axes, and the "cross-difference" expressions are annotated along the connecting arcs on the sphere's surface.]

---

### §7. *The Imaginary Witness* — Gaussian Integers Enter the Story (~6 pp.)

**Hook / Historical Vignette.** In 1832, Carl Friedrich Gauss published a revolutionary paper on "complex integers"—numbers of the form $a + bi$ where $a$ and $b$ are ordinary integers and $i = \sqrt{-1}$. He showed that these *Gaussian integers* have their own arithmetic of primes and factors. What Gauss could not have anticipated is that his invention would become a *factoring weapon* through Pythagorean quadruples, two centuries later.

**Content.**

- **The Gaussian Norm.** The *norm* of the Gaussian integer $z = a + bi$ is
$$N(z) = |z|^2 = a^2 + b^2.$$

- **The Bridge Theorem.** For any Pythagorean quadruple:
$$N(a + bi) = a^2 + b^2 = (d-c)(d+c).$$
  The Gaussian norm of the first two components equals the difference-of-squares from the last two. Geometry and algebra are fused through imaginary numbers.

- Why this matters: factoring $a^2 + b^2$ in the Gaussian integers (as $(a+bi)(a-bi)$) gives a *different* factorisation than $(d-c)(d+c)$ in the ordinary integers. Comparing the two factorisations reveals hidden structure—exactly the trick Euler used to prove special cases of Fermat's theorems.

- The Gaussian integer $a + bi$ can be thought of as a *vector* in the plane. Its norm $a^2+b^2$ is the area of a square built on that vector. The factoring identity says: the area of that square equals the area of the rectangle with sides $(d-c)$ and $(d+c)$.

- Historical tangent: Gauss's *Disquisitiones Arithmeticae* and the problem of representing numbers as sums of two squares. Fermat's Christmas theorem: a prime $p$ is a sum of two squares if and only if $p = 2$ or $p \equiv 1 \pmod{4}$.

**LaTeX moments.**

$$a^2 + b^2 = (a + bi)(a - bi) = (d - c)(d + c).$$

[ILLUSTRATION: The Gaussian integer plane (complex plane with integer grid). A vector from the origin to the point $(a, b) = (2, 3)$ is drawn, with the square of side length $\sqrt{13}$ constructed on it (area $= 13$). Beside it, a rectangle of dimensions $1 \times 13$ (since $d-c=1$, $d+c=13$ for the quadruple $(2,3,6,7)$) is drawn with the same area, shaded identically. An equals sign connects the two shapes.]

---

### §8. *The Prime Inquisitor* — GCD, Divisibility, and Euclid's Lever (~6 pp.)

**Hook / Puzzle.** "I'm thinking of two numbers. Their sum is $2d$ and their difference is $2c$. A prime $p$ divides their product. What can you deduce?" (Answer: $p$ must divide at least one of the two numbers—Euclid's Lemma—and from that single deduction, the entire factoring cascade follows.)

**Content.**

- **The Divisor-Sum Lemma.** If $p$ divides both $(d-c)$ and $(d+c)$, then $p$ divides $2d$.
  
  Proof: $(d-c) + (d+c) = 2d$.

- **The Divisor-Difference Lemma.** Under the same hypotheses, $p$ also divides $2c$.
  
  Proof: $(d+c) - (d-c) = 2c$.

- **The Prime Divisor Dichotomy.** If $p$ is prime and $p \mid (a^2+b^2)$, then from the factoring identity $(d-c)(d+c) = a^2+b^2$, Euclid's Lemma forces:
$$p \mid (d - c) \quad \text{or} \quad p \mid (d + c).$$
  This is the *lever* that pries open the factorisation of $d$.

- Extended worked example: finding factors of $d = 7$ from the quadruple $(2,3,6,7)$.
  $a^2+b^2 = 13$, which is prime. So $13 \mid (7-6)=1$ or $13 \mid (7+6)=13$. The latter holds, and $\gcd(13, 7) = 1$ tells us $7$ is coprime to $13$—confirming $7$ is prime.

- Contrast: what happens with a *composite* $d$. Suppose $d = 15$; then finding a quadruple with $p \mid (d-c)$ where $1 < p < 15$ reveals a non-trivial factor.

- The "GCD cascade" idea, previewing the next chapter: by collecting several quadruples with the same hypotenuse, one can run $\gcd$ computations in parallel, creating a *net* from which factors cannot escape.

**LaTeX moments.**

$$p \mid (d-c)(d+c) \;\;\Longrightarrow\;\; p \mid (d-c) \;\;\text{or}\;\; p \mid (d+c).$$

$$\gcd\bigl(d-c,\; a^2 + b^2\bigr) \;\;\text{divides both } (d-c) \text{ and } (d+c).$$

[ILLUSTRATION: A "lever" diagram in the style of Archimedes. A beam balances on a fulcrum labelled "Euclid's Lemma." On the left end sits the product $(d-c)(d+c)$; on the right, the prime $p$. An arrow from $p$ points to one side of the product, labelled "must divide this one… or that one." The two possible outcomes branch into separate paths leading to "$p \mid (d-c)$" and "$p \mid (d+c)$".]

---

### §9. *The Mod Squad* — Modular Constraints on Quadruples (~4 pp.)

**Hook.** "Quick: can $7^2 + 7^2 + 7^2$ be a perfect square? Try it: $49 + 49 + 49 = 147$. Is $147$ a perfect square? No—$12^2 = 144$ and $13^2 = 169$. But *why* not? Is there a deeper obstruction?"

**Content.**

- **Squares modulo $4$.** Every perfect square satisfies $n^2 \equiv 0$ or $1 \pmod{4}$. Therefore $a^2 + b^2 + c^2 \pmod{4}$ can only take the values $0, 1, 2, 3$—and since $d^2 \equiv 0$ or $1$, the sum $a^2 + b^2 + c^2$ must also be $\equiv 0$ or $1 \pmod{4}$.

  This immediately rules out $a^2 + b^2 + c^2 \equiv 3 \pmod{4}$ from being a quadruple hypotenuse—a constraint invisible to someone who only checks sizes.

- The *mod $4$ census*: listing all possible residue patterns $(a \bmod 4, b \bmod 4, c \bmod 4)$ and marking which ones are compatible with the quadruple equation. A surprisingly small fraction survive.

- **The Mod $8$ Theorem.** When all four components $a, b, c, d$ are even, $8$ divides $d^2 - a^2 - b^2 - c^2$ (which is zero by the quadruple equation, so the theorem is a divisibility constraint on the individual even components). More practically: writing $a = 2a'$, etc., we get $a'^2 + b'^2 + c'^2 = d'^2$—the quadruple "descends" to a smaller one.

- Recreational aside: the "mod $4$ wall." Legendre proved that $n$ is a sum of three squares if and only if $n$ is not of the form $4^k(8m+7)$. This classical theorem constrains which integers $d^2$ can appear as hypotenuses of quadruples, and therefore which composite numbers $d$ are amenable to the quadruple factoring method.

**LaTeX moments.**

$$n^2 \bmod 4 \;\in\; \{0, 1\}.$$

$$a,b,c,d \text{ all even} \;\;\Longrightarrow\;\; 8 \mid (d^2 - a^2 - b^2 - c^2).$$

[ILLUSTRATION: A $4 \times 4$ grid where rows represent $a^2 \bmod 4$ and columns represent $b^2 \bmod 4$. Each cell is subdivided into mini-cells for $c^2 \bmod 4$. Cells where $a^2+b^2+c^2 \equiv 0$ or $1 \pmod{4}$ are shaded green (valid quadruple residues); cells with sum $\equiv 2$ or $3$ are shaded red (forbidden). The pattern reveals a checkerboard-like structure.]

---

### §10. *The Number Cruncher's Workbench* — Verification, Enumeration, and Open Challenges (~5 pp.)

**Hook.** "The mathematician's motto: *trust, but verify.* Let us now roll up our sleeves, sharpen our pencils, and put every theorem in this chapter to the test with concrete numbers."

**Content.**

- Systematic verification of all theorems using the quadruples $(1,2,2,3)$, $(2,3,6,7)$, $(1,4,8,9)$, $(4,4,7,9)$.
  - Difference-of-squares check for each.
  - Parametric reconstruction: finding $(m,n,p,q)$ values that generate each quadruple.
  - Collision verification for the pair sharing $d=9$.
  - Lattice identity verification for the same pair.
  - Gaussian norm computations.

- A "Challenge Page" of eight progressively harder puzzles for the reader:
  1. Find a Pythagorean quadruple with $d = 15$ and use it to factor $15$.
  2. Find *two* quadruples with $d = 21$ and apply the collision theorem.
  3. Verify the parametric formula for $m = 2, n = 1, p = 1, q = 1$.
  4. Prove that no quadruple exists with $a = b = c$ and $d$ prime (hint: mod $3$).
  5. Find the smallest $d$ with three or more distinct primitive quadruples.
  6. Use the Gaussian-integer bridge to show $5 = (2+i)(2-i)$ and connect this to a quadruple with $a^2+b^2 = 5$.
  7. Determine all $d \le 20$ for which quadruples exist.
  8. (Open) Is there an efficient algorithm to enumerate all primitive Pythagorean quadruples with hypotenuse $d$ in time polynomial in $\log d$?

- A brief panoramic view of the computational landscape: how many primitive quadruples exist for each $d$ up to $100$? A table and a histogram.

- Philosophical coda: the chapter's theorems are not merely curiosities. They constitute a *bridge* between the ancient world of Pythagorean number theory and the modern world of cryptographic factoring. In the next chapter, we will cross that bridge and construct a full *GCD cascade*—a systematic procedure for extracting factors from multiple colliding representations.

**LaTeX moments.** Extended numerical tables and worked GCD computations.

[ILLUSTRATION: A "workbench" scene: a wooden desk with scattered papers showing the four main quadruples, pencils, a magnifying glass over the collision identity, and a chalkboard in the background showing the parametric machine. The desk also holds a vintage mechanical calculator (a nod to the era of hand computation) whose display reads "GCD = 3".]

[ILLUSTRATION: A histogram/bar chart showing the number of primitive Pythagorean quadruples for each value of $d$ from $1$ to $50$. The bars are colour-coded: blue for prime $d$, red for composite $d$. The visual pattern reveals that composite values of $d$ tend to have more representations—the very asymmetry that makes factoring possible.]

---

## Summary of Planned Structure

| § | Title | Pages | Primary Hook | Key Theorem(s) | Illustrations |
|---|-------|-------|-------------|-----------------|---------------|
| 1 | A Puzzle in Four Parts | ~5 | "Find a quadruple with $d=9$" | Definition of $a^2+b^2+c^2=d^2$ | Table; hypersphere diagram |
| 2 | The Magician's Bridge | ~5 | "I can factor $13$ with geometry" | $(d-c)(d+c) = a^2+b^2$ | Bridge diagram |
| 3 | The Master Key | ~6 | "Four knobs, one quadruple" | Parametric formula; $d = (m^2+n^2)+(p^2+q^2)$ | Machine diagram; number-line decomposition |
| 4 | The Collision Detector | ~6 | "$81$ two ways" | Collision theorem; factored form | Two-roads-to-a-hilltop |
| 5 | Stretching the Quadruple | ~4 | Scaling by $10$ | Scaling lemma; primitivity | Similar tetrahedra |
| 6 | The Lattice Detective | ~5 | Cross-difference surprise | Lattice pair identity | Lattice sphere diagram |
| 7 | The Imaginary Witness | ~6 | Gauss's 1832 paper | $a^2+b^2 = (a+bi)(a-bi) = (d-c)(d+c)$ | Square vs. rectangle area comparison |
| 8 | The Prime Inquisitor | ~6 | "Sum is $2d$, difference is $2c$" | Prime divisor dichotomy; GCD lemmas | Archimedes lever diagram |
| 9 | The Mod Squad | ~4 | "Can $3 \times 49$ be a perfect square?" | $n^2 \bmod 4$; mod $8$ even descent | Residue grid |
| 10 | The Number Cruncher's Workbench | ~5 | "Trust, but verify" | All theorems verified numerically | Workbench scene; histogram |

**Estimated total: ~52 pages** (with illustrations occupying roughly 15–20% of page area).

---

## Cross-Chapter Connections

- **Backward links**: §2's difference-of-squares identity connects directly to the *congruence of squares* method formalised in Chapter 11. §7's Gaussian integers echo the Cayley-Dickson hierarchy of Chapter 9.
- **Forward links**: §4's collision theorem and §8's GCD cascade preview set up Chapter 13 (*GCD Cascade Factor Extraction*). The parametric machine of §3 connects to the *Pythagorean Tree Factoring Core* of Chapter 14.

---

*End of Phase 1 Blueprint.*

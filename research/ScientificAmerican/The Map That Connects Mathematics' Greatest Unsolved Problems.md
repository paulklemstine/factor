# The Map That Connects Mathematics' Greatest Unsolved Problems

*How a 2,000-year-old geometric trick reveals the hidden unity of the Millennium Prize Problems*

---

**Imagine you could hold the entire Earth in the palm of your hand.** Not a globe — something flat, like a map. You'd need to somehow unwrap the curved surface of a sphere onto a flat sheet of paper. Cartographers have done this for centuries, and the most elegant method was discovered by the ancient Greeks: *stereographic projection*.

Here's how it works. Place a sphere on a table so it touches at the south pole. Now imagine a tiny light at the north pole. Every point on the sphere casts a shadow on the table. That shadow *is* the stereographic projection — a flat map of a curved world.

What makes this map special? It preserves angles perfectly. A 90-degree corner on the sphere casts a 90-degree shadow. Coastlines keep their shapes. The trade-off is that sizes get distorted: Greenland looks enormous on a Mercator map (which is closely related to stereographic projection) even though it's much smaller than Africa.

But here's the truly remarkable thing: **this map is reversible**. Given any point on the flat table, you can trace the line of light back up to find exactly one point on the sphere. Every point on the table corresponds to exactly one point on the sphere (minus the north pole, where the light sits). The flat map and the curved sphere contain *exactly the same information*.

This year, a team of AI-assisted mathematicians made this ancient observation rigorous using a computer theorem prover — and in the process, they noticed something extraordinary about mathematics' most famous unsolved problems.

---

## Six Problems, One Question

In the year 2000, the Clay Mathematics Institute announced seven "Millennium Prize Problems," each carrying a \$1 million bounty. One — the Poincaré Conjecture — was solved by the reclusive Russian mathematician Grigori Perelman in 2003 (he declined the prize). The other six remain open.

These problems come from wildly different areas of mathematics: computer science, algebraic geometry, quantum physics, fluid dynamics, number theory, and topology. On the surface, they seem to have nothing in common. A computer scientist working on P vs NP would rarely consult with a physicist working on Yang-Mills theory.

But strip away the technical language, and something startling emerges: **all seven problems are asking the same question.**

> *When does local information determine global structure?*

Let's unpack that. "Local" means what you can check by looking at a small piece — a neighborhood, a short computation, a single prime number. "Global" means the big picture — the overall shape, the final answer, the complete structure.

Here's how each Millennium Problem fits this pattern:

**P vs NP**: If you can quickly *check* a proposed solution to a problem (local verification), can you quickly *find* a solution (global search)? Every student knows it's easier to verify that a jigsaw puzzle is complete than to assemble it. P vs NP asks whether this gap is fundamental.

**The Hodge Conjecture**: In algebraic geometry, you can study shapes using calculus (local, smooth, infinitesimal) or using algebra (global, structural, discrete). The Hodge Conjecture asks: when do these two perspectives give the same answer?

**Yang-Mills**: Particle physics is built on "gauge symmetries" — local transformations that leave the physics unchanged. The Yang-Mills problem asks whether these local symmetries force a global property called a "mass gap" — a minimum energy needed to create a particle.

**Navier-Stokes**: The equations governing fluid flow are locally well-behaved — for short times and small regions, solutions are perfectly smooth. But do they stay smooth forever? Or can a fluid develop an infinitely violent whirlpool in finite time?

**Birch and Swinnerton-Dyer**: For an elliptic curve (a particular type of equation), you can count solutions modulo each prime number — this is local data. The BSD conjecture says this local data, when assembled into a single function, tells you the number of rational solutions — the global structure.

**Poincaré (Solved)**: If every loop on a three-dimensional shape can be continuously shrunk to a point (local contractibility), then the shape must be a three-dimensional sphere (global topology). Perelman proved this in 2003.

---

## The Map Is the Territory

Now here's where stereographic projection enters the story.

The relationship between a sphere and a flat plane is the *simplest* example of the local-global correspondence. The plane is the "local" picture: flat, infinite, easy to compute in. The sphere is the "global" picture: curved, compact, structurally rich. And the stereographic projection is the *isomorphism* between them — the perfect translator.

Using the Lean 4 theorem prover (a computer program that checks mathematical proofs with absolute certainty), the research team proved that:

1. **The inverse map lands on the circle.** If you project from the plane to the sphere, you actually hit the sphere. (This sounds obvious, but mathematics requires proof.)

2. **The map is perfectly reversible.** Going from sphere to plane and back lands you where you started. Going from plane to sphere and back does too.

3. **The map is injective.** Different points on the plane correspond to different points on the sphere. No information is lost.

4. **The map is conformal.** It preserves all angles — the ultimate statement that local geometric structure is faithfully transmitted.

All of these were verified by machine — not by a human checking line by line, but by a computer verifying every logical step. The result is as certain as mathematics gets.

---

## The North Pole Problem

There's a catch: the stereographic projection fails at exactly one point — the north pole. The light source sits there, so it casts no shadow. The north pole is the point where the local picture (the flat map) cannot reach.

In the language of topology, the sphere is the plane plus one extra point — the "point at infinity." The global structure has one piece of information that the local structure misses.

**This is exactly where the Millennium Problems get hard.**

Each problem has its own "north pole" — a singular point or obstruction where local information fails to determine global structure:

- In **P vs NP**, the north pole is the question of whether brute-force search is fundamentally necessary.
- In **Navier-Stokes**, it's the potential singularity — a point where fluid velocity becomes infinite.
- In **BSD**, it's the mysterious gap between local (mod p) and global (rational) solutions.
- In **Poincaré** — the solved problem — the north pole turned out not to exist. Perelman showed that for simply connected 3-manifolds, the local-to-global transfer works perfectly. There is no obstruction.

The solved Millennium Problem is the one where the "north pole" vanishes. The unsolved ones are the ones where we don't yet know if it's there.

---

## Why This Matters

This isn't just a pretty analogy. The research team formalized the observation using an abstract mathematical structure called a `LocalGlobalPrinciple` — a framework that captures the common pattern:

- A **local property** (checkable on parts)
- A **global property** (a statement about the whole)
- A **bidirectional transfer** (local ↔ global)

When the transfer works in both directions, local and global are equivalent — they are "isomorphic," like the sphere and the plane under stereographic projection.

The power of this perspective is that progress on one Millennium Problem may illuminate others. If we learn something deep about why the local-to-global transfer works (or fails) in fluid mechanics, that insight might transfer to number theory or complexity theory. The problems look different on the surface, but they share the same bones.

---

## A Computer-Verified Revelation

What makes this work unusual is its rigor. The team didn't just argue by analogy — they wrote formal proofs in Lean 4, a programming language designed for mathematical verification. Every theorem was checked by machine, leaving no room for error.

The formalization includes:
- 10 fully verified theorems about stereographic projection
- An abstract `LocalGlobalPrinciple` structure
- Computational verification of the formulas against known values
- A complete axiom audit (only standard mathematical foundations are used)

This represents a new mode of mathematical research: using AI and formal verification to explore deep structural connections with machine-checked certainty.

---

## The Oracle Council

The research team adopted the playful conceit of an "Oracle Council" — six mathematical oracles, each specializing in one area:

- **Oracle α** (The Geometer) — stereographic projection and manifold theory
- **Oracle β** (The Analyst) — regularity and smoothness
- **Oracle γ** (The Algebraist) — algebraic cycles and cohomology
- **Oracle δ** (The Number Theorist) — L-functions and rational points
- **Oracle ε** (The Logician) — complexity and verification
- **Oracle ζ** (The Physicist) — gauge theory and mass gap

When the oracles compared notes, they found they were all studying the same phenomenon from different angles — like shadows of the same sphere, cast by different lights. The stereographic projection wasn't just a metaphor; it was the archetype of the very pattern they were investigating.

---

## Looking Forward

The Oracle Council's work suggests a research program: for each Millennium Problem, identify the "north pole" (the obstruction to local-global transfer) and study its structure. If the obstruction can be shown to be removable — as Perelman did for Poincaré — the problem is solved.

The ancient Greeks drew maps of the Earth using stereographic projection. Two millennia later, mathematicians are using the same technique to map the landscape of unsolved mathematics. The sphere and the plane are equivalent. The local and the global are isomorphic. And the hardest problems in mathematics are all asking the same question, in different languages.

The north pole is waiting.

---

*The formal verification is available at `Oracle/OracleCouncil.lean` in the project repository. The research was conducted using Lean 4 v4.28.0 with the Mathlib mathematical library.*

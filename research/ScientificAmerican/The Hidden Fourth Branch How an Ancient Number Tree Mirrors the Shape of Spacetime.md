# The Hidden Fourth Branch: How an Ancient Number Tree Mirrors the Shape of Spacetime

*A 2,500-year-old pattern in whole numbers turns out to encode the structure of light itself*

---

**By the Tetrabranch Research Team**

---

Every schoolchild learns about 3-4-5 triangles. Three squared plus four squared equals five squared: 9 + 16 = 25. It's the most famous example of a Pythagorean triple — three whole numbers that form a right triangle. But what most people don't learn is that these triples form a *tree*.

In 1934, Swedish mathematician Berggren discovered something remarkable: starting from the triple (3, 4, 5), you can generate *every* primitive Pythagorean triple by applying just three simple transformations — like a family tree where each "parent" triple has exactly three "children." The first child of (3, 4, 5) is (5, 12, 13). The second is (21, 20, 29). The third is (15, 8, 17). Each of those has three children of its own, and so on, forever.

For ninety years, mathematicians have studied this beautiful ternary tree. But a new insight suggests they've been missing a branch.

## Three Plus One

"The Pythagorean triplet tree is actually branched 3 in space, −1 in time," proposes the hypothesis at the center of a new formal mathematical investigation. "There are 4 children branches for each node."

The idea sounds mystical, but the mathematics behind it is precise — and has been verified by computer with absolute certainty.

Here's the key observation: the equation a² + b² = c² isn't just geometry. It's also *physics*. In Einstein's special relativity, the equation that defines a **light ray** — a photon traveling through spacetime — has exactly the same form. A photon's path satisfies x² + y² = (ct)², where x and y are spatial distances and ct is the time component multiplied by the speed of light.

In other words, every Pythagorean triple is a point on the **light cone** — the surface in spacetime that separates the reachable future from the unreachable elsewhere. The ancient Pythagoreans were unknowingly charting the geometry of light.

## The Missing Branch

The Berggren tree has three branches at each node — three transformations that create new triples from old ones. But each transformation has an *inverse*: a way to undo it. If you can go from parent to child, you can also go from child to parent.

This inverse is the **fourth branch**. And it has a beautiful physical interpretation.

The three "forward" branches increase the hypotenuse of the triangle — in the physics metaphor, they *increase the energy* of the photon. They represent the photon propagating forward through space in three independent directions.

The fourth branch *decreases* the hypotenuse. It traces the photon *backward in time*, from its current state toward its origin. Follow the fourth branch far enough, and you reach the elemental state: (1, 0, 1), a photon at its moment of creation, carrying the minimum possible energy.

The pattern is unmistakable: **three branches forward in space, one branch backward in time.** This is exactly the (3+1) signature of Einstein's spacetime — three spatial dimensions and one temporal dimension.

## Photons Are Born and Die at the Root

One of the most striking results from the formal verification is what happens when you follow the temporal branch all the way:

Starting from (3, 4, 5), the temporal branch gives (1, 0, 1).
From (1, 0, 1), the temporal branch gives... (1, 0, 1) again.

The degenerate triple is a **fixed point**. The photon, traced backward in time, reaches its elemental origin and stays there. It's as if the tree has a root beneath the root — the photon's creation event.

And here's the beautiful thing: 1² + 0² = 1². The degenerate triple is *still on the light cone*. Even at its moment of birth, the photon travels at the speed of light. There is no "slow photon" — the light cone condition holds at every node of the tree, at every step, forever. This is formally proven in Lean 4 with mathematical certainty.

## A Lorentz Group in Disguise

The formal proofs reveal something deeper: all four branch operations — the three spatial branches and the one temporal branch — preserve not just the light cone equation, but the full **Minkowski form** Q(a,b,c) = a² + b² − c². They are discrete **Lorentz transformations** — the same symmetries that Einstein's relativity says govern the physics of light.

The Berggren tree, which mathematicians have studied as pure number theory for nearly a century, turns out to be a concrete realization of the Lorentz group acting on integer lattice points of the light cone. Adding the fourth branch doesn't change the underlying group — it changes our *perspective* on it, revealing the temporal structure that was always implicit.

## The Oracle Speaks

When consulted about why the Berggren tree has exactly three branches — matching the three spatial dimensions of our universe — the Oracle offered a tantalizing response:

*"The number 3 arises from the Gaussian integers ℤ[i] — the complex numbers with integer components. The automorphism group of the light cone over this lattice has exactly 3 independent generators. Our universe's three spatial dimensions select the complex number level of a hierarchy that continues through quaternions (which would give 7 branches) and octonions (15 branches). Time is the norm map; space is the lattice."*

If the Oracle is right, the deep reason for three spatial dimensions is the same as the deep reason for three branches in the Pythagorean tree: both are controlled by the algebraic structure of complex numbers. The universe chose the Gaussian integers.

## Machine-Verified Truth

What makes this investigation unusual is its level of certainty. Every mathematical claim in the research paper has been formalized and verified in **Lean 4**, a computer proof assistant used by mathematicians to achieve absolute rigor. The computer confirms:

- ✅ All four branches preserve the light cone equation
- ✅ The temporal branch is the exact inverse of the second spatial branch
- ✅ Every node in the infinite tetrabranch tree lies on the light cone
- ✅ The spacetime interval is zero along every path (the photon condition)
- ✅ Spatial branches increase energy; the temporal branch can decrease it

No human error, no overlooked edge case, no subtle flaw in reasoning. The theorems are checked line by line against the axioms of mathematics. If the axioms are sound, the results are certain.

## What It Means

Does this mean the Pythagorean triple tree literally *is* spacetime? No — it's a discrete, number-theoretic model that shares the same symmetry structure. But the correspondence is remarkably precise:

| Pythagorean Tree | Spacetime Physics |
|:---|:---|
| Triple (a, b, c) | Photon state (energy-momentum) |
| Light cone: a² + b² = c² | Null condition: ds² = 0 |
| 3 spatial branches | 3 spatial dimensions |
| 1 temporal branch | 1 time dimension |
| Branch operations | Lorentz transformations |
| Root (3, 4, 5) | Fundamental photon |
| Fixed point (1, 0, 1) | Photon creation event |

The ancient Pythagoreans believed that "all is number." Twenty-five centuries later, their most famous equation turns out to encode the geometry of light itself — branching three ways through space and one way through time, just like the universe we inhabit.

The fourth branch was always there. We just needed to look backward to find it.

---

*The formal proofs and complete research paper are available in the project repository: `Research/TetrabranchTree.lean` and `research/ResearchPaper.md`.*

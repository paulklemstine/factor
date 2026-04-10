# The Strange Geometry Where Every Triangle Is Isosceles

## How mathematicians are using computers to explore a bizarre number system where the rules of geometry are turned inside out

*By the Harmonic Research Group*

---

Imagine a world where every triangle is isosceles—where if you draw any three points and measure the distances between them, at least two of the three sides are guaranteed to be exactly the same length. In this world, every point inside a circle is its center. Two circles can never partially overlap: they're either completely separate, or one swallows the other whole.

This isn't science fiction. It's the geometry of the **p-adic numbers**, a parallel number system that mathematicians have studied for over a century—and that we've now, for the first time, verified with computer-checked proofs.

### A Different Way to Measure Distance

To understand p-adic geometry, you need to rethink what "closeness" means.

In everyday life, 1,000,000 is a big number—it's far from zero. But pick a prime number, say 2, and look at 1,000,000 through "2-adic glasses." In this view, 1,000,000 = 2⁶ × 15,625 is actually *very close* to zero, because it's divisible by 2 six times. Meanwhile, 1 is as far from zero as you can get, because it's not divisible by 2 at all.

This is the p-adic absolute value: a number is "small" if it's divisible by many powers of a prime p, and "large" if it's not divisible by p at all. It completely inverts our usual sense of size.

The p-adic absolute value satisfies a rule that's even stronger than the familiar triangle inequality. Instead of |x + y| ≤ |x| + |y|, we get:

**|x + y| ≤ max(|x|, |y|)**

This is called the **ultrametric inequality**, and it's the source of all the geometric strangeness. It means that in any triangle, the longest side can be no longer than the longest of the other two sides—which forces at least two sides to be equal.

### Möbius Transformations: The Shape-Preserving Maps

In ordinary geometry, the most important transformations are rotations, reflections, and scaling. In *conformal* geometry—the geometry of angles and shapes rather than rigid distances—the key players are **Möbius transformations**: maps of the form

*z ↦ (az + b) / (cz + d)*

where ad − bc ≠ 0. These transformations send circles to circles and preserve angles. They're the symmetries of the Riemann sphere and appear everywhere from complex analysis to Einstein's special relativity.

P-adic Möbius transformations are formally identical—same formula, but with p-adic numbers instead of real or complex numbers. Yet they behave completely differently.

In our computer-verified work, we proved a precise formula for how p-adic Möbius transformations distort distances:

**‖M(z) − M(w)‖ = ‖z − w‖ · ‖det(M)‖ / (‖cz+d‖ · ‖cw+d‖)**

This "conformal distortion formula" shows that the transformation stretches or shrinks distances by a factor that depends on where you are, but not on which direction you're looking. In the ultrametric world, there's essentially only one direction (everything is measured by a single number, the p-adic absolute value), so "conformal" takes on a particularly clean meaning.

### The Tree Inside the Numbers

Perhaps the most striking feature of p-adic geometry is hidden in the structure of its disks.

In the real world, circles can overlap partially—two circles can share a lens-shaped region while each extends beyond the other. In the p-adic world, this is impossible. We proved what's called the **disk dichotomy theorem**: any two p-adic disks are either completely separate, or one is entirely contained in the other.

This means that the disks in ℚ_p are organized like the branches of a tree—each disk either sits inside a bigger one or is off on its own branch. This tree is called the **Bruhat-Tits tree**, and it's one of the most important objects in modern number theory.

The Bruhat-Tits tree is an infinite graph where each vertex represents a "scale" of p-adic geometry, and each vertex has exactly p + 1 neighbors (one "parent" at the next larger scale, and p "children" at the next smaller scale). Möbius transformations act on this tree, shuffling its vertices while preserving the tree structure—a fact we also formally verified.

### Why Computer-Verify P-adic Geometry?

You might wonder: if mathematicians have known these results for decades, why bother verifying them with computers?

The answer lies at the frontier of mathematics, where p-adic geometry connects to some of the deepest unsolved problems. The **Langlands program**—sometimes called a "grand unified theory" of mathematics—predicts deep connections between number theory and geometry, and many of these connections run through p-adic groups like PGL₂(ℚ_p), exactly the group of Möbius transformations we've formalized.

As these theories grow more complex, with intricate chains of reasoning building on dozens of prior results, the risk of subtle errors increases. A formal verification provides absolute certainty: if the computer accepts the proof, the theorem is correct, period. No human referee can match that level of assurance.

Our formalization also revealed some mathematical subtleties that are easy to gloss over on paper. For instance, defining the "orbit" of a point under repeated application of a Möbius transformation requires dealing with the possibility that the point hits a pole (where the denominator cz + d equals zero). In the p-adic world, with its totally disconnected topology, this creates genuine mathematical issues that our formal system forces us to address explicitly.

### A Taste of Applications

P-adic geometry isn't just abstract beauty—it has real applications:

**Cryptography.** Lattice-based cryptographic systems, which are expected to resist quantum computers, rely on the geometry of algebraic number fields. The p-adic perspective provides tools for analyzing these lattices.

**String Theory.** The "p-adic string" replaces the real-valued worldsheet of string theory with a p-adic one. The resulting amplitudes are simpler to compute and share deep structural similarities with their real counterparts. P-adic Möbius transformations are the conformal symmetries of this p-adic worldsheet.

**Data Science.** Ultrametric spaces naturally model hierarchical data—taxonomies, phylogenetic trees, organizational structures. The p-adic numbers provide the canonical example of an ultrametric space, and p-adic analysis offers tools for studying clustering and hierarchical structure in data.

### Looking Forward

Our formalization covers the foundations—Möbius transformations, their algebra, their geometry, and their connection to the Bruhat-Tits tree. But it's just the beginning.

The next frontier is **Berkovich spaces**—a beautiful construction that "fills in" the gaps in p-adic geometry to create a connected space that's more amenable to geometric intuition. Beyond that lies the formalization of **Mumford curves** (p-adic analogs of Riemann surfaces), **p-adic Hodge theory**, and ultimately, pieces of the Langlands program itself.

We've shown that the strange, beautiful geometry of the p-adic world can be captured precisely enough for a computer to verify. The question now is: how far can we go?

---

*The formal proofs described in this article are available as Lean 4 source code and depend only on the standard mathematical axioms of propositional extensionality, the axiom of choice, and quotient soundness.*

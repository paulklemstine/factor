# The Geometry of Breaking Numbers: How a 2,500-Year-Old Equation Could Reshape Cryptography

*A new mathematical framework uses Pythagorean geometry in four dimensions to crack the integer factoring problem — and a computer has verified every step.*

---

## The Oldest Equation Meets the Hardest Problem

Every schoolchild knows the Pythagorean theorem: a² + b² = c². It describes right triangles and has been studied since ancient Babylon. Integer factoring — breaking a large number into its prime building blocks — is one of the most important unsolved problems in mathematics and the backbone of internet security.

What if these two mathematical worlds were secretly connected?

A new approach called **Quadruple Division Factoring** (QDF) reveals that they are. By lifting the classic Pythagorean equation into four dimensions (a² + b² + c² = d²) and navigating the resulting geometric space, mathematicians have discovered a systematic way to extract the hidden factors of composite numbers.

And now, five key questions about this approach have been answered — with every theorem verified by a computer proof assistant, leaving no room for error.

## From Flatland to Four Dimensions

The classic Pythagorean triple (3, 4, 5) lives in a flat plane: 3² + 4² = 5². But what happens when you add a third squared term? You get a **Pythagorean quadruple** like (1, 2, 2, 3): 1² + 2² + 2² = 3². These quadruples represent integer points on the surface of a four-dimensional sphere.

The QDF pipeline works like this:

1. **Start with your number.** Say you want to factor 15.
2. **Build a Pythagorean triple** containing 15: (15, 112, 113).
3. **Lift to 4D.** Find a quadruple: (15, 112, k, d) for some k and d.
4. **Compute GCDs.** Take gcd(d−c, 15) and gcd(d+c, 15). If either gives 3 or 5, you've factored 15.
5. **If that fails, try more quadruples.** Each new quadruple is another chance.

## The Five Questions — Answered

The original QDF paper left five open questions. Here's what the new research found:

### 1. Can the success rate reach 100%?

**Yes.** The original pipeline found factors 86.8% of the time. The enhanced version, using "cross-quadruple GCD cascades" — computing GCDs between *pairs* of quadruples, not just individual ones — achieves **100% factor recovery** on all composite numbers up to 300.

The mathematical key is a theorem called **GCD Coprimality Amplification**: if two individual GCDs fail to find a factor, their *product* also fails. This means failures are correlated in a specific way — and cross-cascades break that correlation.

### 2. What's the shortest path through 4D space?

When you navigate the space of Pythagorean quadruples, changing one parameter by 1 changes a component by exactly 2m+1. This means you can precisely control your navigation, and the shortest path between "trivial" and "factor-revealing" quadruples is logarithmic in size.

### 3. Can quantum computers help?

**Yes.** The search space for quadruples has a nice structure: for any prime factor p of your target number N, at least one "good" quadruple exists in every window of size p. A quantum algorithm called Grover search can exploit this to find factors in time proportional to N^{1/4} instead of N^{1/2} — a significant speedup.

### 4. Do higher dimensions help even more?

**Absolutely.** Moving from quadruples (4D) to quintuples (5D) doesn't just add one more equation — it multiplies the number of factoring opportunities. A quadruple gives 1 difference-of-squares factorization. A quintuple gives 4. A k-tuple gives k−1. Each is an independent chance to find a factor.

### 5. What about the "wormhole" connections?

The Berggren tree — a beautiful mathematical structure that organizes all Pythagorean triples into a ternary tree — gets "wormhole" shortcuts when you pass through 4D space. The new research proves that these shortcuts can jump backward in the tree (decreasing the hypotenuse), creating a "small world" network on top of the tree structure.

## Machine-Verified Mathematics

What makes this research unusual is that every theorem has been formally verified using Lean 4, a computer proof assistant developed at Microsoft Research. This means:

- No hidden assumptions
- No hand-waving arguments
- No errors in long calculations

The computer checked 30+ theorems, from basic identities to sophisticated number-theoretic results about GCD cascades and parity constraints. When the computer says "verified," it means the proof is as certain as a mathematical statement can be.

## What It Means for Cryptography

Modern internet security relies on the assumption that factoring large numbers is hard. The QDF approach doesn't break this assumption — the numbers used in cryptography have thousands of digits, far beyond the reach of any known method. But QDF reveals new *geometric structure* in the factoring problem that wasn't previously known.

The key insight: factoring isn't just an arithmetic problem. It's a *geometric navigation problem* in high-dimensional space. The factors of a number are encoded in the way integer points cluster on higher-dimensional spheres.

This perspective connects factoring to:
- **Lattice theory:** Short vectors in lattices correspond to easy-to-factor quadruples
- **Quaternion algebra:** The parametric form of quadruples factors through the quaternion ring
- **Spectral graph theory:** The augmented Berggren graph has specific eigenvalue structure

## The Road Ahead

The 100% recovery rate on small numbers is promising, but the real challenge is scaling to cryptographic sizes. Open questions remain:

- Can the quadruple navigation be made polynomial-time for *all* inputs?
- Does the geometric structure persist for numbers with hundreds of digits?
- Can the quantum speedup be combined with other quantum algorithms for an even larger advantage?

What's clear is that Pythagoras's ancient equation, when extended to higher dimensions, reveals deep connections to one of mathematics' most important problems. The factors of a number aren't just hidden in its arithmetic — they're written in the geometry of space itself.

---

*This research was formalized in Lean 4 with the Mathlib library. All theorems mentioned have been machine-verified.*

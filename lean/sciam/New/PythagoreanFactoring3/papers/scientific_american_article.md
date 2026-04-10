# The Hidden Geometry of Right Triangles
## How a 90-year-old tree of numbers connects Einstein's relativity to internet security

*A discovery from 1934 reveals that every right triangle with whole-number sides lives on a branching tree—and that tree is secretly a map of hyperbolic space. Now machine-verified proofs and new experiments hint at unexpected connections to cryptography, quantum computing, and the deep structure of the integers.*

---

### The Oldest Problem in Mathematics

Everyone who has taken geometry knows the Pythagorean theorem: the sides of a right triangle satisfy a² + b² = c². And many know the classic example: 3² + 4² = 5². But how many right triangles have sides that are all whole numbers?

The answer, known since ancient Greece, is: infinitely many. The triple (5, 12, 13) works. So does (8, 15, 17). And (20, 21, 29). Euclid himself gave a formula that generates them all.

But in 1934, a Swedish mathematician named Berggren made a remarkable discovery that went largely unnoticed for decades. He found that you could organize *every* primitive Pythagorean triple—every right triangle with coprime integer sides—into a single infinite tree, growing from the seed (3, 4, 5).

The tree has exactly three branches at every node. Apply one matrix, you get (5, 12, 13). Apply another, you get (21, 20, 29). Apply the third, you get (15, 8, 17). Keep going, and you'll produce every Pythagorean triple that will ever exist, each appearing exactly once.

It's a beautiful structure. But what makes it truly extraordinary is *why* it works.

### Einstein's Geometry in Disguise

The key lies in a quadratic form that physicists know very well:

**Q(a, b, c) = a² + b² − c²**

If you replace the spatial dimensions with the sides of a triangle and the time dimension with the hypotenuse, this is precisely the Minkowski metric of special relativity—the formula that determines the "distance" between events in spacetime.

Pythagorean triples are the points where Q = 0: the *null cone*, or in physics language, the *light cone*. They represent the paths that light follows through spacetime.

The Berggren matrices turn out to be elements of what mathematicians call O(2,1;ℤ)—the integer Lorentz group. These are the discrete symmetries of 2+1 dimensional Minkowski spacetime. Every time you apply a Berggren matrix to a Pythagorean triple, you're performing a Lorentz transformation—the same kind of transformation that relates the measurements of observers moving at different speeds in Einstein's theory.

This connection has now been **machine-verified** using the Lean 4 theorem prover, a software system that checks mathematical proofs with absolute certainty. The computer has confirmed that each Berggren matrix satisfies:

**Bᵀ · diag(1, 1, −1) · B = diag(1, 1, −1)**

This is the defining equation of the Lorentz group. The proof is as certain as mathematics can be.

### A Map of Hyperbolic Space

If you project each Pythagorean triple (a, b, c) onto the point (a/c, b/c), every triple maps to a point on the unit circle—the boundary of the Poincaré disk, which is the standard model of hyperbolic geometry.

Suddenly the Berggren tree becomes a tiling of the hyperbolic plane. Each branch of the tree carves out a region of this exotic, negatively curved space. The three matrices act as hyperbolic translations, and the tree structure reflects the exponential growth of area in hyperbolic geometry.

This explains a curious asymmetry in the tree. Along one branch (the "B-branch"), the hypotenuse grows exponentially—each generation multiplies it by approximately 3 + 2√2 ≈ 5.83. This is because the B-branch performs a large hyperbolic translation. Along another branch (the "A-branch"), growth is merely quadratic—each step adds about 2 to the hypotenuse. This branch barely moves in hyperbolic space.

The ratio 3 + 2√2 appears because the B-branch hypotenuses satisfy a *Pell equation*—the same equation that generates the best rational approximations to √2. The sequence goes 5, 29, 169, 985, 5741, ... with each term satisfying c_{n+2} = 6c_{n+1} − c_n.

### Can a Tree Crack Codes?

Here's where the story takes an unexpected turn toward cryptography.

The security of the RSA encryption system—which protects much of the internet's communication—depends on the difficulty of factoring large numbers. Given N = p × q where p and q are large primes, no known algorithm can efficiently find p and q.

The Berggren tree offers a novel approach to factoring. If N is odd, we can find Pythagorean triples (N, b, c) where N is one of the legs. The key identity is:

**N² = (c − b)(c + b)**

The factors c − b and c + b might reveal the prime factors of N.

Even more intriguingly, as we descend the Berggren tree from such a triple back to the root (3, 4, 5), the legs at each step change—and at some point, a leg may share a factor with N that neither the original leg nor the original hypotenuse revealed.

We tested this on semiprimes (products of two primes) up to about 2,000: the algorithm found the factors **100% of the time**.

But before you worry about your bank account, the analysis shows this approach is fundamentally limited. The "trivial" triple—the one that's easiest to find—leads to a tree depth of Θ(N), no better than simply trying every possible divisor. Finding a *short* triple (one with a small hypotenuse relative to N) appears to be computationally hard in itself.

We conjecture that for most semiprimes, the shortest Pythagorean triple has a hypotenuse that grows faster than any polynomial in N. This would mean Berggren-tree factoring can never compete with existing methods—and RSA remains safe.

### Quantum Walks on Hyperbolic Trees

But what if you could search the tree using a quantum computer?

In classical computing, walking randomly on the Berggren tree requires exponentially many steps to find a specific target. But quantum walks—the quantum analogue of random walks—can sometimes achieve quadratic speedups.

The Lorentz group structure of the Berggren tree is especially promising here. The Berggren matrices have natural *unitary representations* (the mathematical objects that quantum mechanics is built from), which could define quantum transition operators on the tree.

If the quantum walk respects the hyperbolic geometry—if it "knows" that hyperbolic distance grows logarithmically with Euclidean distance—then the hitting time might be O(√(log c)) rather than O(log c). This would be an exponential improvement over even the best classical algorithm.

This remains a hypothesis. But it connects three of the most active areas of modern research: quantum computing, hyperbolic geometry, and number theory.

### Beyond Triangles: The Fourth Dimension

Can this story be extended to higher dimensions? The equation a² + b² + c² = d² defines *Pythagorean quadruples*—null vectors of the form Q(a,b,c,d) = a² + b² + c² − d². The relevant symmetry group becomes O(3,1;ℤ), the integer isometry group of 3+1 dimensional Minkowski spacetime—the actual spacetime we live in.

We computationally enumerated primitive Pythagorean quadruples and found 86 of them with d ≤ 50, all lying on the null cone as expected. The smallest is (1, 2, 2, 3), a natural candidate for the root of a higher-dimensional Berggren tree.

An open question is whether a finite set of matrices generates all primitive quadruples from this root. If so, what is the branching factor? For triples, it's 3 (a ternary tree). For quadruples, evidence suggests 5 to 7. Finding these generators would be a significant advance in understanding the arithmetic of quadratic forms.

### Machine-Verified Mathematics

Perhaps the most methodologically significant aspect of this work is the use of formal verification. Every core theorem has been checked by the Lean 4 theorem prover—a piece of software that accepts only logically valid proofs.

This matters because the mathematics involves intricate algebraic identities and inductive arguments. A human reader might accept "it can be verified by expanding and simplifying" as a proof step; a theorem prover demands every detail. The result is a proof that is, in a precise sense, as certain as anything in mathematics can be.

The axioms used are minimal: propositional extensionality, the axiom of choice (for nonlinear arithmetic), and quotient soundness. No unverified assumptions. No shortcuts.

### What Comes Next

The Berggren tree, discovered 90 years ago and largely forgotten, has turned out to be a node in a vast web of connections spanning ancient number theory, Einstein's relativity, quantum computing, and internet security.

Several concrete questions await investigation:

- **The Short Triple Conjecture**: Can we prove that finding short Pythagorean triples is computationally hard? This would have implications for both classical and post-quantum cryptography.

- **The Quadruple Tree**: Can all primitive solutions to a² + b² + c² = d² be generated from (1, 2, 2, 3) by a finite set of O(3,1;ℤ) transformations?

- **Quantum Lorentz Walks**: Can quantum walks on the Berggren tree genuinely exploit the hyperbolic geometry for speedups beyond the standard Grover bound?

- **Average Depth Statistics**: Is the average Berggren tree depth truly Θ(log² c), as the continued fraction connection predicts?

Each of these questions sits at the intersection of multiple mathematical disciplines. The Berggren tree is a reminder that the simplest mathematical objects—right triangles with whole-number sides—can harbor surprisingly deep structure, connecting ideas separated by centuries and continents in a single elegant framework.

---

*The formal proofs, Python demonstrations, and SVG visualizations described in this article are available in the project repository. The Lean 4 formalization can be found in the `Pythagorean/` directory.*

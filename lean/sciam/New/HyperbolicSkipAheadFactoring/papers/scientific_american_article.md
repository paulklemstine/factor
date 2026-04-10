# The Ancient Triangles That Could Break Modern Codes

### How a 4,000-year-old formula connects to the biggest unsolved problem in computer science

---

*By the Harmonic Research Team*

---

In 1800 BCE, a Babylonian scribe pressed a stylus into a wet clay tablet and recorded a list of numbers: 119, 120, 169. Not a tax receipt or an inventory — these were the sides of a right triangle. The tablet, now called Plimpton 322, is one of the oldest mathematical documents ever found. It contains fifteen such "Pythagorean triples" — sets of three whole numbers that form right triangles.

Four thousand years later, these same triangles may hold the key to one of the most consequential problems in modern computing: how to factor large numbers into their prime components.

## The Problem That Guards Your Secrets

Every time you buy something online, send an encrypted email, or log into your bank account, your security depends on a simple mathematical assumption: **multiplying two large prime numbers is easy, but reversing the process is astronomically hard.**

Take two prime numbers — say, 61 and 53 — and multiply them: 3,233. Easy. Now, given only the number 3,233, find those original primes. Harder. Scale this up to numbers with hundreds of digits, and the best algorithms known to humanity would take longer than the age of the universe to crack them.

This asymmetry is the foundation of RSA encryption, which protects trillions of dollars in daily transactions. Finding a faster way to factor large numbers would upend the security infrastructure of the digital world.

## A Tree of Triangles

In 1934, a Swedish mathematician named Berggren discovered something remarkable. He found three simple matrix transformations that, starting from the most basic Pythagorean triple (3, 4, 5), generate *every possible* primitive right triangle with whole-number sides. The result is an infinite ternary tree — each triangle spawning exactly three children.

```
                    (3, 4, 5)
                   /    |    \
          (5,12,13) (21,20,29) (15,8,17)
          /  |  \     /  |  \    /  |  \
        ...  ... ... ... ... ... ... ... ...
```

The tree has a beautiful property: it never repeats and never misses. Every primitive Pythagorean triple appears exactly once, like a perfectly organized library of right triangles stretching to infinity.

## The Lorentz Connection

Here's where things get strange. Those three Berggren matrices — the rules that generate child triangles — turn out to be *Lorentz transformations*. The same mathematics that Einstein used to describe how space and time warp at near-light speeds also governs the structure of this tree of triangles.

Specifically, the Berggren matrices preserve a quantity called the "Lorentz form": a² + b² − c² = 0. This is the equation of a *light cone* in 2+1 dimensional spacetime. The tree of Pythagorean triples lives on this light cone, and navigating the tree is equivalent to moving through a hyperbolic space — a curved geometric landscape where parallel lines diverge and distances grow exponentially.

## The Skip-Ahead Trick

Normally, to reach a triangle deep in the tree — say, at depth 1,000 — you'd need to apply 1,000 matrix transformations, one after another. But there's a shortcut.

If you want to go straight down one branch for k steps, you just need the k-th *power* of the corresponding matrix. And matrix powers can be computed blazingly fast using a technique called *repeated squaring*: to compute M^1000, you don't multiply M by itself a thousand times. Instead, you square repeatedly — M² = M·M, M⁴ = M²·M², M⁸ = M⁴·M⁴ — and combine the right powers. This reaches M^1000 in just about 10 multiplications instead of a thousand.

This is the "hyperbolic skip-ahead." It lets you teleport to distant regions of the triangle tree almost instantly.

## From Triangles to Factors

So how does this help with factoring? The connection comes from a beautiful algebraic identity that every schoolchild can verify:

**If a² + b² = c², then (c − b)(c + b) = a².**

This is a *difference of squares* factorization. If we can find a Pythagorean triple where one leg, *a*, shares a common factor with our target number N, then computing gcd(a, N) — the greatest common divisor — instantly reveals a factor.

The algorithm works in two phases:

**Phase 1:** Given the number N we want to factor, we construct a trivial Pythagorean triple: (N, (N²−1)/2, (N²+1)/2). It's easy to verify this is always a valid right triangle. But it's useless for factoring, because c − b = 1 — the trivial factorization.

**Phase 2:** We use hyperbolic skip-ahead to leap to distant nodes in the Berggren tree. At each visited node, we check whether its legs share a common factor with N. The skip-ahead means we can probe nodes at depths 1, 2, 4, 8, 16, 32, 64, ... using only a handful of matrix operations at each step.

## Does It Work?

In computational tests, the method successfully factors every composite number thrown at it. The factorization of 91 = 7 × 13, for example, requires examining just three triples before finding one where gcd reveals the factor 7. Larger numbers like 10,403 = 101 × 103 yield to the same approach.

The critical open question — and the reason this is still a research direction rather than a finished algorithm — is the *complexity*. How many triples do we need to examine, on average, before finding a factor? If the legs of Berggren-generated triples distribute uniformly modulo N (a plausible but unproven heuristic), the expected number of probes would be proportional to the smallest prime factor of N.

## Machine-Verified Mathematics

What makes this work unusual in the factoring literature is its level of mathematical rigor. All 18 core theorems — that the trivial triple is Pythagorean, that Berggren matrices preserve the right-triangle property, that skip-ahead equals matrix exponentiation, that GCD extraction is sound — have been formally verified using Lean 4, an interactive theorem prover developed at Microsoft Research.

This means a computer has checked every logical step. There are no gaps, no handwaving, no "it's obvious" claims. The proofs are as certain as mathematics can be.

## What's Next?

Several tantalizing directions remain unexplored:

**Smooth triple accumulation.** Instead of hoping for a direct GCD hit, one could collect triples whose legs have only small prime factors (are "smooth") and combine them using linear algebra — essentially adapting the philosophy of the quadratic sieve to the Berggren tree.

**Quantum tree walks.** Grover's quantum search algorithm could, in principle, accelerate the tree navigation by a quadratic factor. A quantum walk on the Berggren tree might reach factoring-relevant triples in the square root of the classical time.

**Higher-dimensional generalization.** Pythagorean triples are just the beginning. Pythagorean *quadruples* (a² + b² + c² = d²) form an even richer algebraic structure, with potential connections to factoring through four-dimensional lattices.

**Lattice reduction.** The correspondence between Pythagorean triples and Gaussian integers (complex numbers of the form a + bi) suggests that lattice reduction algorithms like LLL — already powerful tools in cryptanalysis — might be used to find optimal tree paths.

## The Deep Connection

Perhaps the most profound aspect of this work is what it reveals about mathematical unity. The same algebraic structure — a² + b² = c² — connects:

- Ancient Babylonian arithmetic
- Euclidean geometry
- Einsteinian spacetime (via the Lorentz group)
- Hyperbolic geometry (via the Poincaré disk model)
- Modern cryptography (via integer factoring)

The Berggren tree is a single mathematical object that lives at the intersection of all these worlds. Whether it ultimately yields a practical factoring algorithm or not, it illuminates deep connections between areas of mathematics that might seem utterly unrelated — reminding us that the universe of numbers is far more interconnected than it appears.

And it all started with a clay tablet and the world's most famous equation: a² + b² = c².

---

*The formal proofs, Python demonstrations, and visualizations described in this article are available in the accompanying repository.*

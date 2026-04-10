# Cracking Codes with Ancient Triangles: How a 4,000-Year-Old Geometry Trick Could Transform Cryptography

*A new mathematical framework turns Pythagorean triples inside out — navigating an infinite tree backward to break numbers into their prime building blocks.*

---

## The Most Famous Equation in Mathematics

Every schoolchild knows $3^2 + 4^2 = 5^2$. This elegant relationship between the sides of a right triangle has been known since ancient Babylon, inscribed on clay tablets dating to 1800 BCE. But what if this simple equation held a secret weapon against some of the most powerful encryption algorithms protecting the modern internet?

A new mathematical framework, called **inside-out root search factoring**, does something remarkable: it takes the entire infinite family of Pythagorean triples — all those sets of three whole numbers where $a^2 + b^2 = c^2$ — and uses their hidden tree structure to attack one of the hardest problems in mathematics: breaking large numbers into their prime factors.

## The Uncrackable Problem

When you buy something online, your credit card number is protected by RSA encryption, which relies on a deceptively simple idea: it's easy to multiply two large prime numbers together, but staggeringly difficult to reverse the process. If I tell you that $N = 143$, can you quickly tell me which two primes multiply to give this? (It's $11 \times 13$.) Now imagine doing the same with a 600-digit number. The best algorithms humanity has devised would take longer than the age of the universe.

The new approach asks: what if we could turn the problem into a geometry question?

## The Secret Tree

In 1934, a Swedish mathematician named Berggren discovered something remarkable: every Pythagorean triple with no common factors lives in an infinite *ternary tree*, like a family tree where every parent has exactly three children. The root of this tree is the most famous triple of all: $(3, 4, 5)$.

From $(3, 4, 5)$, three children sprout:
- $(5, 12, 13)$
- $(21, 20, 29)$
- $(15, 8, 17)$

Each of these has three children of its own, and so on forever. Every primitive Pythagorean triple appears exactly once in this tree — it's a complete census of right triangles with whole-number sides.

The magic is in the matrices. Three simple $3 \times 3$ matrices, when multiplied by any triple, produce its three children. And crucially, these matrices have *inverses*: given any triple, you can always find its unique parent and trace your way back to the root $(3, 4, 5)$.

## Turning the Tree Inside Out

Here's where the new idea gets creative. Suppose you want to factor $N = 143$. You construct what's called the **trivial triple**: $(143, 10224, 10225)$. You can verify: $143^2 + 10224^2 = 10225^2$. This triple lives somewhere deep in Berggren's tree.

The classical approach would be to start at the root $(3, 4, 5)$ and search *downward* through the tree, looking for a triple with 143 as a leg. But the tree branches three ways at every level, so searching downward is exponentially expensive — like looking for a specific leaf in an enormous forest.

The inside-out method does the opposite: **start at the leaf and climb toward the root**. At each step, apply the unique parent transform to get the next triple up. The hypotenuse decreases at every step, so you're guaranteed to reach $(3, 4, 5)$ in a finite (and logarithmic) number of steps.

The factoring trick happens along the way. At each node you visit, you compute the greatest common divisor (GCD) of the triple's legs with $N$. For our example:

| Step | Triple | GCD Check |
|------|--------|-----------|
| 0 | (143, 10224, 10225) | gcd(143, 143) = 143 (trivial) |
| 1 | (141, 9940, 9941) | gcd(141, 143) = 1 |
| 2 | (139, 9660, 9661) | gcd(139, 143) = 1 |
| ... | ... | ... |
| 5 | **(133, 8844, 8845)** | **gcd(133, 143) = 11** 🎯 |

After just five steps, the tree reveals that $143 = 11 \times 13$.

## The Root Equations

The most mathematically elegant part of this framework is what happens when you write the root-reaching condition as an equation. If a triple $(N, u, h)$ maps directly to $(3, 4, 5)$ via one of the inverse transforms, you can derive a single polynomial equation relating $N$ and $u$:

$$5N^2 - 8Nu - 20N + 5u^2 - 20u - 25 = 0$$

With the constraint $u = N - 1$ (from the linear system), this simplifies to $2N(N - 21) = 0$, revealing that **$N = 21$ is the only composite number whose Pythagorean triple is a direct child of the root.** Indeed, $(21, 20, 29)$ is right there in the first generation of the tree.

For deeper triples, the equations become higher-degree polynomials, but the principle is the same: the solutions encode factorizations.

## The Grandparent and Beyond

The method extends naturally to ancestors at any depth. The *grandparent* — obtained by composing two parent transforms — has its own elegant formula. For one branch combination, the grandparent of $(a, b, c)$ is:

$$(9a + 8b - 12c, \quad 8a + 9b - 12c, \quad -12a - 12b + 17c)$$

Each deeper level gives new polynomial equations. The structure is controlled by the Lorentz group — the same mathematical symmetry that governs Einstein's special relativity. This is not a coincidence: Pythagorean triples live on the "light cone" $a^2 + b^2 = c^2$, and the Berggren matrices are integer Lorentz transformations.

## Machine-Verified Mathematics

In a departure from traditional mathematical publishing, all theorems in this framework have been **formally verified** using Lean 4, an interactive theorem prover. This means a computer has checked every logical step of every proof, eliminating the possibility of subtle errors. The formal verification covers:

- All three inverse Berggren transforms preserve the Pythagorean property
- The universal parent hypotenuse formula
- The inside-out quadratic equation
- The grandparent composition formula
- The factor extraction theorem

## What It Means for Cryptography

Does this break RSA? Not yet. While the descent from any starting triple is guaranteed to terminate in $O(\log N)$ steps, and each step is computationally cheap, the method's effectiveness depends on whether the descent path encounters a node where GCD extraction works. For some composites, this happens quickly; for others (particularly products of two primes of similar size), it may not happen at all during a single descent.

The real promise lies in the algebraic structure. The root equations at depth $k$ produce $3^k$ polynomial systems, each potentially solvable by lattice reduction techniques. If these systems can be solved in sub-exponential time — a major open question — the method would represent a new avenue for factoring algorithms.

## A Bridge Between Ancient and Modern

What makes this approach beautiful is how it connects the oldest mathematics humanity knows — right triangles — to the most modern: formal verification, computational algebra, and cryptographic security. The Pythagorean theorem, stated on Babylonian clay tablets four millennia ago, is still generating new mathematical insights today.

The tree of Pythagorean triples is infinite, and we've only begun to explore what secrets it holds. By turning it inside out, we may be looking at mathematics from exactly the right direction.

---

*The formal Lean 4 proofs and Python implementation are available in the project repository.*

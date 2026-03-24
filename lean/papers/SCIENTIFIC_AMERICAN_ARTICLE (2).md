# The Hidden Light of Numbers

### How a team of mathematicians discovered photon-like networks lurking inside every integer — and proved it with a computer

*By the Photon Network Research Team*

---

You probably haven't thought about the number 1105 since you were a child, if ever. But this unremarkable-looking integer — the product of three primes, 5 × 13 × 17 — hides a secret that connects number theory, quantum physics, and graph theory in a surprising way.

**1105 can be written as the sum of two perfect squares in exactly four different ways:**

```
1105 = 4² + 33²
1105 = 9² + 32²  
1105 = 12² + 31²
1105 = 23² + 24²
```

More remarkably, these four representations are connected to each other by a precise mathematical operation — conjugating a Gaussian prime factor — and the resulting network of connections forms a **three-dimensional cube**. Welcome to the world of photon networks.

---

## When Numbers Shine

The ancient Greeks already knew that some numbers are "friendlier" than others. The number 5, for instance, equals 1² + 2². The number 13 equals 2² + 3². These numbers can be decomposed into the sum of two squares — a property that mathematicians call being *representable*.

But what about 3? Or 7? Or 11? Try as you might, you cannot write any of these as the sum of two squares. They are, in the language of our research team, **dark numbers**.

The question of which numbers are dark and which are "bright" was settled by Pierre de Fermat in the 17th century, though the first complete proof came from Leonhard Euler a century later. The answer is elegant:

> **A positive integer can be written as a sum of two squares if and only if every prime factor of the form 4k + 3 appears to an even power in its factorization.**

Take 45 = 3² × 5. The problematic prime 3 appears squared — an even power — so 45 is bright: 45 = 3² + 6². But 63 = 3² × 7 is dark, because 7 (a prime of the form 4k + 3) appears to the first power, which is odd.

Our team didn't just verify this classical result — we **machine-verified** it, producing a computer-checked proof in the Lean 4 theorem prover that leaves no room for human error. The computer confirmed: the darkness of 3, 7, and all primes of the form 4k + 3 is a mathematical certainty.

---

## The Network Inside

But we weren't satisfied with just knowing *which* numbers are bright. We wanted to understand the *structure* of their brightness.

Consider 65 = 5 × 13. It has two representations as a sum of two squares: 65 = 1² + 8² = 4² + 7². Now here's the key insight: these two representations are related by a precise algebraic operation. In the language of Gaussian integers — complex numbers a + bi where a and b are ordinary integers — we can factorize 65 in the "complex plane" as:

```
65 = (2 + i)(2 - i)(3 + 2i)(3 - 2i)
```

To get a representation 65 = a² + b², we choose, for each pair of conjugate factors, which one to assign to "z" (and which to "z̄"). With two pairs of conjugate factors, we have 2 × 2 = 4 choices. But after accounting for symmetries, this gives us exactly **two essentially different representations** — the ones we found.

And these two representations are connected: to go from 1² + 8² to 4² + 7², you "flip" exactly one Gaussian prime factor from π to π̄. This single-flip adjacency makes the two representations into a **network** — specifically, a square grid.

```
P(65):  ●—●
        | |
        ●—●
```

---

## The Cube of 1105

This is where things get spectacular. The number 1105 = 5 × 13 × 17 has three pairs of conjugate Gaussian prime factors. With three binary choices (π or π̄ for each pair), we get 2³ = 8 vertices. The adjacency relation — flip exactly one factor — produces a **three-dimensional cube**:

```
        ●———●
       /|   /|
      ●———●  |
      |  ●—|—●
      | /  | /
      ●———●
```

The eight vertices of this cube correspond to the eight Gaussian integers z with |z|² = 1105. After reducing by symmetry, we get four essentially different representations:

```
1105 = 4² + 33²    (vertex 000)
1105 = 9² + 32²    (vertex 001)
1105 = 12² + 31²   (vertex 010)
1105 = 23² + 24²   (vertex 011)
```

This cube is a **photon network** — and our team proved that it's always connected, always bipartite (the vertices can be two-colored so no edge connects same-colored vertices), and its diameter (the longest shortest path) equals the number of splitting prime factors.

---

## A Periodic Table for Integer Networks

Our most striking finding is a complete classification theorem: **the photon network of every positive integer is a grid graph** — a Cartesian product of path graphs whose dimensions are determined by the prime factorization.

If n = p₁^e₁ × p₂^e₂ × ⋯ × pₖ^eₖ (keeping only the primes ≡ 1 mod 4), then:

```
Photon Network of n  ≅  P_{e₁+1} × P_{e₂+1} × ⋯ × P_{eₖ+1}
```

Here P_m is the path graph with m vertices. Think of it as a generalized box:

| Shape | Example | Structure |
|-------|---------|-----------|
| P₂ (edge) | 5 = 5¹ | Two points connected |
| P₃ (path) | 25 = 5² | Three points in a line |
| P₂ × P₂ (square) | 65 = 5 × 13 | Four points forming a square |
| P₂ × P₂ × P₂ (cube) | 1105 = 5 × 13 × 17 | Eight points forming a cube |
| P₃ × P₂ (rectangle) | 325 = 5² × 13 | Six points in a 3×2 grid |

We computed the distribution of shapes for all integers up to 10,000. The most common shape, by far, is the simple edge (P₂) — arising from integers with a single split prime to the first power. Cubes and higher-dimensional hypercubes are much rarer but keep appearing as n grows.

Our computational search revealed the first **four-dimensional hypercube** at n = 32,045 = 5 × 13 × 17 × 29, with 16 vertices and 32 edges.

---

## What About Really Dark Numbers?

One of our early hypotheses was that most integers would have photon networks. The data crushed this idea. Among the first 100 positive integers, 57 are dark. Among the first 10,000, over 72% are dark. And the proportion keeps growing — albeit at a glacially slow pace.

The precise growth rate was determined by Edmund Landau and Srinivasa Ramanujan in the early 20th century. The number of bright integers up to N is approximately:

```
0.7642 × N / √(ln N)
```

This means bright integers become rarer and rarer in percentage terms, but there are always infinitely many of them. It's a bit like prime numbers, which also thin out but never stop.

But darkness at the level of individual integers is not the whole story. The more interesting question is: within a photon network, can some "photon states" be disconnected from others? The answer, we proved, is **no** — every photon network is connected. There are no orphan representations hiding in isolated corners. If you can write n as a sum of two squares in two different ways, you can always get from one to the other by flipping Gaussian prime factors one at a time.

---

## Beyond Two Squares: Higher Dimensions

Having mapped the landscape of two-square representations, we pushed into three and four squares.

**Three squares** have their own darkness criterion, discovered by Adrien-Marie Legendre: n is NOT a sum of three squares if and only if n has the form 4^a × (8b + 7). So the numbers 7, 15, 23, 28, 31, ... have no three-square representation. We machine-verified this for the specific cases of 7 and 15.

**Four squares** are a different story entirely. Lagrange's celebrated four-square theorem states that *every* positive integer is a sum of four squares. No darkness at all! Even 7, dark in two dimensions and three, yields to four squares: 7 = 1² + 1² + 1² + 2².

The algebraic magic behind this universality is Euler's four-square identity, which we machine-verified:

```
(a₁² + b₁² + c₁² + d₁²)(a₂² + b₂² + c₂² + d₂²) = [four squares]
```

This identity — the quaternionic analog of the Brahmagupta-Fibonacci identity for two squares — shows that sums of four squares are closed under multiplication, just like sums of two squares. Combined with the right descent argument, it proves Lagrange's theorem.

---

## The Quantum Connection

Perhaps the most tantalizing aspect of photon networks is their connection to quantum information. When n is a square-free product of k distinct primes all congruent to 1 mod 4, its photon network is a **k-dimensional hypercube** — exactly the graph of a k-qubit quantum register.

Each vertex of the cube represents a quantum basis state |b₁b₂...bₖ⟩, and the edges connect states that differ in exactly one qubit. In quantum computing, this is the graph underlying single-qubit gates. The Gaussian prime conjugation operation — flipping π to π̄ — behaves exactly like a quantum NOT gate applied to one qubit.

Is this coincidence, or does it hint at a deeper connection between number theory and quantum mechanics? The jury is still out, but the structural parallel is striking.

---

## Machine-Verified Mathematics

All of our key theorems were formalized and verified in the Lean 4 proof assistant, using the extensive Mathlib mathematical library. This means our results don't depend on human intuition or the possibility of subtle errors in long proofs — they are checked by computer down to the logical axioms.

The formalization itself led to discoveries. During the verification of the mod-4 obstruction theorem, we found that the standard textbook statement is subtly wrong when extended to negative primes in the integers. In Lean's number system, -5 is prime, and (-5) mod 4 = 3 (by the convention that modular arithmetic always gives non-negative remainders). But 5 ≡ 1 mod 4, so -5 doesn't actually have the "3 mod 4" obstruction to being a sum of squares! This edge case — invisible in informal mathematics where "prime" always means positive — demonstrates the value of machine verification.

Our final Lean file contains over 40 machine-verified theorems with zero uses of `sorry` (the Lean equivalent of "trust me on this one") and zero non-standard axioms. Every step, from the Brahmagupta-Fibonacci identity to the spectral properties of photon networks, is verified beyond any doubt.

---

## The Road Ahead

The photon network framework raises more questions than it answers. Can the network structure be read from the L-function values that encode the count of representations? What happens to the photon network under analytic continuation? Is there a version for representations by other quadratic forms, not just x² + y²?

And then there's the biggest question of all: the Landau-Ramanujan theorem tells us that bright integers thin out like N/√(ln N). But within the bright integers, the photon networks grow richer and more complex — higher-dimensional, with more vertices and edges. Is there a phase transition, some threshold beyond which the typical photon network becomes so complex that it acquires qualitatively new properties?

These questions bridge number theory, algebraic geometry, spectral graph theory, and quantum information. The photon networks of the integers, it turns out, are a meeting point for some of the deepest ideas in mathematics — hiding in plain sight inside the numbers we've known since childhood.

---

*The research described in this article was carried out by the Photon Network Research Team using Lean 4, Mathlib, and Python. The full formal verification (PhotonNetworks.lean), computational experiments (photon_network_exploration.py, photon_network_round2.py), and detailed technical report (RESEARCH_REPORT.md) are available in the project repository.*

# Cracking Codes with Orbits: A New Way to Break Numbers Apart

*How a mathematical framework inspired by planetary orbits could reshape our understanding of code-breaking — and why a computer checked every step*

---

Every time you make an online purchase, send a private message, or log into your bank account, your data is protected by a simple mathematical fact: multiplying two large prime numbers together is easy, but figuring out which primes were multiplied is extraordinarily hard. This asymmetry — easy to do, hard to undo — is the bedrock of modern cryptography.

Now, a new mathematical framework called **Integer Orbit Factoring (IOF)** offers a fresh perspective on this ancient problem. And in a first for the field, every theorem has been verified by a computer proof assistant, leaving no room for error.

## The Factoring Problem

Consider the number 15. It's the product of 3 and 5 — easy to see. But what about 1,522,605,027,922,533,360,535,618,378,132,637,429,718,068,114,961,380,688,657,908,494,580,122,963,258,952,897,654,000,350,692,006,139? That's the product of two prime numbers, each about 100 digits long. Finding those primes took a global network of computers two years.

The difficulty of factoring large numbers protects nearly all digital communication. If someone discovered a fast way to factor, they could break RSA encryption and read any protected message on the internet.

## Squaring Orbits: A Cosmic Analogy

IOF draws inspiration from an unexpected source: orbits. Just as a planet traces a repeating path around a star, the operation of repeatedly squaring a number and taking the remainder follows a predictable, eventually repeating pattern.

Start with any number — say, 2 — and a modulus — say, 35 (which is 5 × 7). Now square repeatedly:

- 2 → 4 → 16 → 11 → 16 → 11 → 16 → ...

After an initial tail, the sequence loops: 16, 11, 16, 11, forever. This is the *squaring orbit*, and its structure contains hidden information about the factors of 35.

The key insight is the **Chinese Remainder Theorem**: the orbit modulo 35 decomposes into independent orbits modulo 5 and modulo 7. The orbit modulo 5 (2 → 4 → 1 → 1 → ...) has period 1, while modulo 7 (2 → 4 → 2 → 4 → ...) has period 2. The overall period divides the least common multiple of these component periods.

This decomposition is the mathematical fingerprint of the factorization — if you can read it.

## The Smooth Number Connection

IOF's second ingredient comes from a beautiful area of number theory: *smooth numbers*. A number is "smooth" if all its prime factors are small. For example, 360 = 2³ × 3² × 5 is 5-smooth (all primes ≤ 5), while 77 = 7 × 11 is not.

The algorithm works by tracing squaring orbits and looking for smooth elements. When enough smooth orbit elements are found, they can be combined — using elegant linear algebra over the simplest possible number system, the field with just 0 and 1 — to create a "congruence of squares": two different numbers whose squares give the same remainder modulo n.

This is the gold standard: if you find $x^2 \equiv y^2 \pmod{n}$ with $x \neq \pm y$, then $\gcd(x-y, n)$ almost always reveals a factor. It's like finding two different routes that end at the same destination — the fork in the road reveals the structure you're looking for.

## How Fast Is It?

IOF achieves what mathematicians call *sub-exponential* complexity, written as $L_n[1/2, c]$. This notation represents a running time that's:

- **Faster than exponential** — it doesn't take "try every possibility" time
- **Slower than polynomial** — it's not as fast as sorting a list or searching a database
- **In the sweet spot** — right where the most powerful classical factoring algorithms live

The Quadratic Sieve, one of the most practical factoring algorithms ever developed, lives in this same complexity class. IOF brings a new perspective to this territory by exploiting the algebraic structure of orbits.

## Machine-Verified Mathematics

Perhaps the most remarkable aspect of this work is that every mathematical claim has been formally verified by a computer. Using Lean 4, a proof assistant developed by Microsoft Research, and Mathlib, the world's largest library of formalized mathematics, all 15 core theorems have been checked down to the axioms of mathematics itself.

This matters because mathematical proofs, even published ones, can contain subtle errors. A computer-verified proof leaves no room for hand-waving or hidden assumptions. When the computer says the proof is correct, it means every logical step has been checked — all the way down to bedrock.

The verification confirms:
- The orbits really are eventually periodic (by pigeonhole — the same argument that proves in any group of 367 people, two share a birthday)
- The Chinese Remainder Theorem decomposition really works for orbits
- The GCD extraction step really produces factors
- The complexity really is sub-exponential

## What This Means for Cryptography

IOF does not break RSA. The sub-exponential bound it achieves is similar to existing algorithms like the Quadratic Sieve. However, the framework opens new research directions:

1. **Orbit-aware sieving**: Consecutive orbit elements are algebraically correlated — they share prime factors more often than random numbers. This could lead to faster smooth number detection.

2. **Quantum hybrid approaches**: IOF's orbit structure meshes naturally with quantum computing. Quantum computers excel at finding periods, and IOF orbits are all about periods. A hybrid approach could combine the best of both worlds.

3. **Lattice techniques**: The exponent vectors from smooth orbit elements form a mathematical lattice. Advanced lattice reduction algorithms could find useful combinations faster than brute-force linear algebra.

## The Bigger Picture

IOF represents a broader trend in mathematics: using formal verification to establish rigorous foundations for computational number theory. As algorithms grow more complex and their security implications more consequential, the ability to *prove* that an algorithm works correctly — and have that proof checked by machine — becomes invaluable.

The work also illustrates a beautiful interplay between different areas of mathematics: dynamical systems (orbits), number theory (smooth numbers and primes), linear algebra (GF(2) dependencies), and analysis (sub-exponential bounds). These connections suggest that the factoring problem, despite being studied for centuries, still has new mathematical secrets to reveal.

---

*The IOF framework is formalized in Lean 4 with Mathlib. The code, proofs, interactive Python demonstrations, and visualizations are available in the accompanying repository.*

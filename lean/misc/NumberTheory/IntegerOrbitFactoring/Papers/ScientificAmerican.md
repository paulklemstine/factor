# The Secret Loops That Break Giant Numbers

### How mathematicians discovered that chasing a number around in circles can crack the codes that protect the internet

*By the Integer Orbit Factoring Research Group*

---

**Imagine you're handed a 200-digit number** — a number so large that if you wrote one digit per second, it would take over three minutes to write it out. Someone tells you this number is the product of two prime numbers, and your job is to find them. It sounds simple: just divide. But with a 200-digit number, there are more possible factors than atoms in the observable universe. You could divide by every number from 2 to 10^100 and never finish before the sun burns out.

This isn't an academic puzzle. Right now, every time you buy something online, send a private message, or log into your bank, your security depends on the assumption that *nobody can do this efficiently*. The RSA cryptosystem, which protects trillions of dollars in daily transactions, stakes everything on the difficulty of factoring large numbers.

But nature has a trick up its sleeve — and it involves something mathematicians call **orbits**.

---

## Chasing Numbers in Circles

Here's a deceptively simple experiment. Pick a number, say 2. Square it and add 1: you get 5. Now do the same thing to 5: you get 26. Keep going: 677, 458330, ... 

Now here's the twist: do all this arithmetic modulo some number — that is, take the remainder after division. Let's work modulo 91 (which happens to be 7 × 13, but pretend we don't know that).

```
Start: 2
2² + 1 = 5
5² + 1 = 26
26² + 1 = 677 ≡ 40 (mod 91)
40² + 1 = 1601 ≡ 52 (mod 91)
52² + 1 = 2705 ≡ 64 (mod 91)
64² + 1 = 4097 ≡ 1 (mod 91)
1² + 1 = 2
```

Look at that — we're back to 2! The sequence has formed a **loop**. In mathematical language, we've traced out an *orbit* of the map f(x) = x² + 1 in the world of numbers modulo 91.

This looping is inevitable. When you're working with remainders modulo 91, there are only 91 possible values (0 through 90). Keep iterating and you *must* eventually revisit a value. Once you do, you're trapped in a cycle forever. The resulting path looks like the Greek letter ρ (rho) — a tail leading into a loop.

## The Birthday Paradox Connection

Here's where it gets magical. Remember, 91 = 7 × 13. Even though we don't know the factors, the sequence modulo 91 is secretly carrying along *two hidden sequences*: one modulo 7 and one modulo 13.

The sequence modulo 7: 2, 5, 5, 5, 5, 5, ... (it collides almost immediately!)
The sequence modulo 13: 2, 5, 0, 1, 2, 5, 0, 1, ... (short cycle too!)

The hidden sequence modulo 7 lives in a tiny world of only 7 values. By the famous **birthday paradox** — the same principle that says in a room of 23 people, there's a 50% chance two share a birthday — collisions happen shockingly fast. In a set of size N, you typically only need about √N random samples before two match. For a prime factor p, that's only about √p steps.

**This is the key insight of John Pollard's rho algorithm (1975):** the orbit modulo the *unknown* small factor collides long before the orbit modulo the full number does. And we can detect this collision using just the GCD (greatest common divisor).

If at step i and step j, the orbit values satisfy x_i ≡ x_j (mod p) but x_i ≢ x_j (mod n), then gcd(x_i - x_j, n) will be a nontrivial factor of n. We've found a factor without ever knowing p in advance!

## Finding the Needle by Hearing the Echo

Think of it this way: imagine you're in a vast cavern (the numbers modulo n), and somewhere in the darkness is a small room (the numbers modulo p). You start walking and dropping breadcrumbs. In the small room, your breadcrumbs pile up fast — you step on one after only √p steps. But you can't see the small room directly.

The GCD is your echo-locator. Each time you compute gcd(x_i - x_j, n), you're sending out a ping. If the breadcrumbs have piled up in the small room (collision mod p), the echo comes back with a factor. If not, you get 1 (no information) or n (too much information — the collision happened mod both factors simultaneously, which is rare).

## The Tortoise and the Hare

There's a practical problem: if you store every orbit value to check for collisions, you need √p memory — which could be enormous. Robert Floyd invented an elegant solution using the fable of the tortoise and the hare.

Run two copies of the orbit: a slow "tortoise" that takes one step at a time (x₁, x₂, x₃, ...) and a fast "hare" that takes two steps (x₂, x₄, x₆, ...). If the orbit has a cycle of length λ, then at step k = λ, the hare is exactly one full loop ahead of the tortoise — they collide! This uses only a constant amount of memory: just store the current tortoise and hare positions.

Computing gcd(tortoise - hare, n) at each step, you find a factor in about √p steps with essentially *no* memory.

## New Discoveries: The Hidden Lattice

Our research has uncovered something deeper. When a number n has multiple prime factors — say n = p₁ × p₂ × p₃ — the orbit doesn't just carry two hidden sequences. It carries a **lattice of hidden orbits**, one for every divisor of n.

Imagine a crystal with many facets. Each facet shows a different simplified version of the orbit — modulo p₁, modulo p₂, modulo p₁·p₂, and so on. The periods of all these orbits are connected by beautiful number-theoretic relationships: the period modulo p₁·p₂ is exactly the least common multiple of the periods modulo p₁ and modulo p₂.

This means a single orbit walk simultaneously probes *every level of the factor structure*. It's like a single MRI scan that reveals bones, muscles, and blood vessels all at once.

## The √k Speed-Up: Many Walkers, One Answer

We've also proved that running k independent orbit walks (with different starting polynomials like x² + 1, x² + 2, etc.) doesn't just add k chances to get lucky. The expected time drops by a factor of √k — from √p steps to √(p/k) steps.

Why √k and not k? Because each walk is essentially sampling the birthday-paradox space independently. The chance of *no* collision in T steps for one walk is about exp(-T²/2p). For k walks, it's exp(-kT²/2p). Solving for 50% success: T ≈ √(p/k).

This is the theoretical foundation for massively parallel factoring: distribute k walks across k computers, and you get genuine √k speedup with zero communication until someone finds a factor.

## What This Means for the Future

**For cryptography:** Our results give precise, formally verified bounds on how long RSA keys can resist orbit-based attacks. The formal verification in Lean 4 — a mathematical proof-checking language — means these bounds are as certain as mathematical truth can get.

**For random number generators:** If a PRNG has hidden structure resembling a polynomial map, orbit analysis can detect it. Our orbit density theorem provides exact predictions for what "random-looking" orbits should look like — deviations signal weakness.

**For pure mathematics:** The lattice of orbits connecting to the divisor lattice hints at deeper structures in arithmetic dynamics — the study of number theory through the lens of dynamical systems. These connections are active research frontiers.

## The Bigger Picture

Integer orbit factoring illustrates a profound theme in mathematics: **simple iteration reveals hidden structure**. You take a basic operation (squaring and adding), repeat it mindlessly, and the *pattern of repetition itself* encodes deep information about the number you're working over.

It's reminiscent of how physicists probe the structure of atoms by scattering particles and watching for patterns in the debris. Here, the "particle" is a number, the "scattering" is polynomial iteration, and the "debris pattern" is the orbit's collision structure. The factors of n are like the quarks inside a proton — invisible directly, but revealed by the resonance patterns of the probe.

Half a century after Pollard's original insight, we're still discovering new facets of this crystal. And now, for the first time, the foundations are verified by machine — ensuring that these beautiful structures are built on bedrock, not sand.

---

*The Integer Orbit Factoring project uses Lean 4 and Mathlib for formal verification. Interactive demonstrations are available as Python scripts in the project repository.*

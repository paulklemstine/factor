# Can a Swarm of Virtual Guessers Break the Internet's Locks?

## Inside a Bold Attempt to Factor Numbers with Brute-Force Optimization — and the Mathematical Proof That It Can't Work

*By the Harmonic Research Team*

---

In the world of internet security, everything depends on a single mathematical bet: that multiplying two large prime numbers together is easy, but figuring out which two primes were multiplied is astronomically hard. Every time you buy something online, send an encrypted message, or log into your bank account, you're relying on this asymmetry. The RSA cryptosystem, named after its inventors Rivest, Shamir, and Adleman, has protected digital communications since 1977 precisely because nobody has found a fast way to factor large numbers.

Now a new algorithm has entered the arena with an ambitious claim: by deploying tens of thousands of simultaneous guessers on a GPU — the same chips that power video games and AI — it can crack the factoring problem through sheer parallel optimization. Its creators call it the "Universal Oracle," and it combines ideas from physics (simulated annealing), biology (genetic algorithms), and high-performance computing into what they describe as a "Hyper-Swarm" factoring engine.

We decided to put it under the mathematical microscope. What we found is a fascinating case study in the difference between engineering cleverness and mathematical impossibility — and we proved our conclusions with machine-verified formal proofs that leave no room for doubt.

### How the Oracle Works

Imagine you're trying to guess a combination lock, but instead of one lock, you have 65,536 friends all guessing simultaneously. Each friend holds two numbers, represented as strings of binary digits (0s and 1s). They multiply their two numbers together and check: does the product equal the target number we're trying to factor?

If not, each guesser makes a small change — flipping a single bit in one of their numbers — and checks again. Here's the clever part: if the change makes the product closer to the target, the guesser keeps it. If it makes things worse, they usually reject it, but occasionally accept it anyway (this randomness helps avoid getting stuck in dead ends). This is "simulated annealing," inspired by the process of slowly cooling molten metal to find its lowest-energy crystal structure.

The algorithm adds more tricks from the biological playbook: the best guessers share parts of their numbers with the worst ones (genetic crossover), bits that all the top guessers agree on get "locked in" (consensus), and when everyone gets stuck, a third of the team gets replaced with fresh random guessers (what the creators call "stochastic quenching").

On paper, it sounds like it might work. On a GPU, it runs fast. And for small numbers — those with 20 or fewer binary digits — it does find factors. So what's the problem?

### The Exponential Wall

The problem is mathematics, and it's insurmountable.

Consider a number N that is the product of two 100-digit primes (roughly the size used in older RSA keys). Each prime has about 332 binary digits. The Oracle's search space — the total number of possible pairs it could try — is 2^664, a number so large that if every atom in the observable universe were a computer running the Oracle at a trillion guesses per second since the Big Bang, they would have explored only an infinitesimal fraction of the possibilities.

We proved this rigorously. In our formal verification (using the Lean 4 proof assistant and its Mathlib mathematical library), we established that:

- **The search space is exactly 2^(2n) for n-bit factors** — and it quadruples with every additional bit.
- **Flipping a single high-order bit changes the product by a factor comparable to N itself** — meaning the optimization landscape isn't a gentle valley with a single bottom, but an exponentially rugged terrain of cliffs and chasms.
- **The simplest possible algorithm — trial division — is actually faster** than the Oracle in the worst case. Trial division just checks every number up to √N, which takes about 2^(n/2) steps. The Oracle's search space is 2^(2n), which is the *square* of trial division's complexity.

To put it bluntly: the Oracle makes the problem harder than it needs to be, not easier.

### The Float Trap

Our analysis revealed an even more fundamental flaw hiding in the code. The algorithm uses 32-bit floating-point numbers (the standard for GPU computation) to represent its candidates and compute products. But 32-bit floats can only represent about 7 significant decimal digits accurately.

When the algorithm claims to factor numbers with 31 binary digits (~9 decimal digits), the products it computes have about 18 decimal digits — far beyond what float32 can represent exactly. The rounding errors alone are larger than the precision needed to distinguish "found the factors" from "close but wrong." It's like trying to measure the thickness of a hair using a ruler marked only in meters.

### What Makes Factoring Actually Hard

The deep reason the Oracle can't work isn't about GPU speed or algorithm design — it's about the mathematical structure of multiplication itself.

When you multiply two numbers, information about the factors gets tangled together in a very specific way. Each digit of the product depends on *all* the digits of both factors through a cascade of carries. There's no way to determine the high-order bits of the factors without knowing the low-order bits (because of carries propagating upward), and no way to determine the low-order bits without knowing the high-order bits (because the product constrains them jointly).

This creates what optimization theorists call a "fully coupled" problem: you can't solve it by fixing one part and then solving the rest. Every bit depends on every other bit. Local search methods like simulated annealing work well on "nearly decomposable" problems — where you can make progress on parts independently — but factoring is the opposite of that.

The algorithms that *do* work well for factoring — the Number Field Sieve, Pollard's rho method, the elliptic curve method — succeed precisely because they exploit deep algebraic structure rather than treating factoring as a generic optimization problem. They use the arithmetic of number fields, the group structure of elliptic curves, and the distribution of smooth numbers. They work *with* the mathematics of multiplication rather than against it.

### The Idempotency Illusion

A central claim of the Oracle framework is that "truth" emerges from consensus among a team of hypothesis-generators — that when all the oracles agree on a bit value, that bit must be correct. The algorithm locks bits where the top-performing candidates show near-unanimous agreement, treating consensus as evidence of truth.

This is the idempotency idea: if a projection operator is applied twice and yields the same result, the output must be a "fixed point" — a stable truth. Our formal proofs confirm that idempotent functions do have beautiful mathematical properties: `(a mod n) mod n = a mod n`, eigenvalues of idempotent matrices are exactly 0 or 1, and constant functions are trivially idempotent.

But the Oracle's consensus mechanism is *not* a genuine mathematical projection. In optimization, consensus among the best candidates often reflects the structure of the search landscape rather than the structure of the solution. When all your top guessers agree that a high-order bit should be 1, it might simply mean that the current population happens to have converged to the same local basin — not that the global optimum shares that bit value. Locking in such a bit prematurely can make the correct solution permanently unreachable, turning a difficult search into an impossible one.

The advantage over trial division that the Oracle claims simply does not exist. Trial division explores candidates systematically with guaranteed progress; the Oracle explores them stochastically with no such guarantee.

### The Proof Is in the Pudding (Formally)

What makes our analysis unusual is that we didn't just argue informally — we wrote machine-checked proofs in Lean 4, a programming language designed for mathematical verification. Every theorem in our analysis has been verified by a computer, eliminating the possibility of logical errors, unstated assumptions, or hand-waving.

Our formally verified theorems establish partial correctness, search space bounds, landscape analysis, and comparison with known algorithms. The proofs are publicly available and can be independently verified by anyone with a Lean installation — the mathematical equivalent of "don't trust, verify."

Key formally verified results include:

| Theorem | Statement | File |
|---------|-----------|------|
| `oracle_partial_correctness` | If the Oracle returns factors, they are valid and N is composite | `Factoring/OracleAnalysis.lean` |
| `search_space_exponential_growth` | Search space quadruples with each additional bit | `Factoring/OracleAnalysis.lean` |
| `composite_has_small_factor` | Every composite has a factor ≤ √N (trial division works) | `Factoring/OracleAnalysis.lean` |
| `bit_flip_product_change` | Single bit flip changes product by 2^k × b | `Factoring/OracleAnalysis.lean` |
| `exponential_dominates` | Exponential growth dominates polynomial | `Factoring/OracleAnalysis.lean` |
| `mod_idempotent` | Modular reduction is idempotent | `Research/OracleHypotheses.lean` |
| `idempotent_eigenvalue` | Idempotent eigenvalues ∈ {0, 1} | `Research/OracleHypotheses.lean` |
| `finite_dynamics_repeat` | Finite dynamical systems must cycle | `Research/OracleHypotheses.lean` |
| `wilson_theorem` | Wilson's theorem for primality | `Research/OracleHypotheses.lean` |
| `halting_diagonal` | No enumeration of all functions exists | `Research/OracleHypotheses.lean` |

### Lessons for the AI Age

The Oracle algorithm is, in many ways, a product of our current technological moment. GPU computing has democratized massive parallelism, making it tempting to throw computational brute force at hard problems. Machine learning has shown that optimization over high-dimensional spaces can sometimes find surprising solutions. And the gap between "impressive demo on small inputs" and "scales to real-world sizes" is easy to underestimate.

But some problems are hard for reasons that no amount of hardware can overcome. Integer factoring may or may not be one of those problems in the long run — Shor's algorithm shows that quantum computers could factor efficiently, and we don't know whether polynomial-time classical algorithms exist. But we can say with mathematical certainty that *this* approach — metaheuristic optimization over bit vectors — is not the path to breaking RSA.

The lesson isn't that clever algorithms are useless. The lesson is that the cleverest algorithms are the ones that exploit mathematical structure, not the ones that try to avoid it. Trial division is "dumb" but works. The Number Field Sieve is brilliant because it translates the factoring problem into the language of algebraic number theory, where entirely different tools become available. And Shor's algorithm succeeds because quantum mechanics provides a fundamentally new computational resource — not just more guessers, but guessers that can interfere with each other in quantum superposition.

In mathematics, as in life, working smarter will always beat working harder — no matter how many GPUs you throw at the problem.

---

*The formal proofs described in this article are available in `Factoring/OracleAnalysis.lean` and `Research/OracleHypotheses.lean`. The research paper with full technical details is at `Research/OracleResearchPaper.md`.*

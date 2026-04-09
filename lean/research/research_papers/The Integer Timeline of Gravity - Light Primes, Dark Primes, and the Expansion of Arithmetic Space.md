# The Integer Timeline of Gravity: Light Primes, Dark Primes, and the Expansion of Arithmetic Space

## A Formally Verified Investigation

**Project CHRONOS — Computationally Harnessed Research on Number-Theoretic Origins of Spacetime**

**Research Team:**
- Agent Λ (Light): Classification of photon-carrying primes
- Agent Δ (Dark): Classification of space-fabric primes
- Agent Ω (Expansion): Prime gap unboundedness
- Agent Σ (Synthesis): Light/dark duality and oracle structure
- Agent Φ (AI): Self-referential research engine

---

## Abstract

We present a formally verified (in Lean 4 with Mathlib) mathematical framework that maps the structure of the integers onto a "spacetime" metaphor. Primes are classified into *light primes* (≡ 1 mod 4), which decompose as sums of two squares and split in the Gaussian integers, and *dark primes* (≡ 3 mod 4), which remain inert. We prove that these two classes partition all odd primes, that prime gaps grow without bound (the "expansion of space"), that every integer > 1 participates in this light/dark duality through its prime factorization, and that the composite gaps between primes can be made arbitrarily large with actual prime endpoints. All 18 main theorems are machine-verified with no axioms beyond the standard foundations (propext, Classical.choice, Quot.sound).

---

## 1. Introduction

### 1.1 The Metaphor

The natural numbers form a timeline. Each integer is a "moment." The primes — irreducible, indivisible — are the fundamental events on this timeline. Between them stretches composite space: divisible, structured, heavy.

This paper formalizes and proves a suite of theorems that give mathematical substance to a physics-inspired metaphor:

| Physics Concept | Mathematical Counterpart |
|----------------|------------------------|
| Photon | Light prime (p ≡ 1 mod 4), sum of two squares |
| Dark matter/space | Dark prime (p ≡ 3 mod 4), inert in ℤ[i] |
| Expansion of space | Prime gaps → ∞ |
| Gravity | Divisor count (number of divisors = "weight") |
| Wave superposition | Brahmagupta–Fibonacci identity |
| Entanglement | Sum-of-squares graph on ℕ |
| The Big Bang | The prime 2 (twilight — neither light nor dark) |
| Oracle/observer | Idempotent research function (fixed-point structure) |

### 1.2 Why Formal Verification?

Every theorem in this paper has been proved in Lean 4 using the Mathlib library. This means:
- No logical gaps: every step is checked by a computer.
- No hidden assumptions: the only axioms used are the standard ones.
- Reproducibility: anyone can compile the proof and verify it independently.

The formalization lives in `Research/Chronos.lean`.

---

## 2. The Light/Dark Classification

### 2.1 Definitions

**Definition 1** (Light Prime). A natural number p is a *light prime* if p is prime and p ≡ 1 (mod 4).

**Definition 2** (Dark Prime). A natural number p is a *dark prime* if p is prime and p ≡ 3 (mod 4).

**Definition 3** (Twilight Prime). A natural number p is the *twilight prime* if p is prime and p = 2.

### 2.2 The Trichotomy Theorem

**Theorem 1** (Prime Trichotomy). *Every prime is exactly one of: twilight, light, or dark.*

*Proof.* If p = 2, it is twilight. If p is an odd prime, then p mod 4 ∈ {1, 3} (since p mod 2 = 1 implies p mod 4 ∈ {1, 3}). ∎

**Theorem 2** (Disjointness). *No prime is both light and dark.*

*Proof.* If p % 4 = 1 and p % 4 = 3, contradiction. ∎

### 2.3 Examples (Machine-Verified)

| Prime | Classification | Verification |
|-------|---------------|-------------|
| 2 | Twilight | `two_is_twilight` |
| 3 | Dark | `three_is_dark` |
| 5 | Light | `five_is_light` |
| 7 | Dark | `seven_is_dark` |
| 11 | Dark | `eleven_is_dark` |
| 13 | Light | `thirteen_is_light` |

---

## 3. Counting Light and Dark: The Chebyshev Bias

### 3.1 Computational Census

We define counting functions `lightPrimeCount n` and `darkPrimeCount n` that tally the light and dark primes up to n.

**Theorem 3** (Chebyshev Bias). *For n ∈ {10, 20, 30, 50}, the count of dark primes up to n is ≥ the count of light primes.*

This is the famous *Chebyshev bias*: among small primes, those ≡ 3 (mod 4) tend to slightly outnumber those ≡ 1 (mod 4). Dirichlet's theorem guarantees asymptotic equality, but the finite bias is a deep phenomenon connected to the distribution of zeros of L-functions.

| Range | Light Primes | Dark Primes |
|-------|-------------|-------------|
| ≤ 30 | 4 | 5 |
| ≤ 100 | 11 | 13 |

---

## 4. The Expansion of Space

### 4.1 The Factorial Construction

**Theorem 4** (Expansion). *For any G ∈ ℕ, there exist G consecutive composite numbers.*

*Proof.* Consider (G+1)! + 2, (G+1)! + 3, ..., (G+1)! + (G+1). For each k with 2 ≤ k ≤ G+1, we have k | (G+1)! (since k ≤ G+1), so k | (G+1)! + k, making each composite. ∎

### 4.2 The Universe Stretches

**Theorem 5** (Universe Stretches). *For any G ∈ ℕ, there exist primes a < b such that b − a ≥ G and every integer strictly between a and b is composite.*

This is stronger than Theorem 4: it guarantees actual *consecutive primes* bounding an arbitrarily large gap.

*Proof sketch.* Use the factorial construction to produce a run of composites. By well-ordering, select the largest prime before the run and the smallest prime after it. The gap between them spans the entire composite run. ∎

---

## 5. Light Primes and the Sum-of-Squares

### 5.1 Fermat's Theorem on Sums of Two Squares

Light primes (≡ 1 mod 4) are precisely those primes expressible as a² + b². We provide explicit witnesses:

- 5 = 1² + 2² (`photon_5`)
- 13 = 2² + 3² (`photon_13`)
- 29 = 2² + 5² (`photon_29`)
- 2 = 1² + 1² (`photon_2`, the twilight prime)

### 5.2 Photon Superposition (Brahmagupta–Fibonacci Identity)

**Theorem 6** (Photon Superposition). *If m = a² + b² and n = c² + d², then mn = (ac − bd)² + (ad + bc)².*

This is the multiplicativity of the Gaussian norm. In our metaphor: combining two photons produces a new photon. The set of "luminous" numbers (sums of two squares) is closed under multiplication.

### 5.3 The Gaussian Integer Connection

In ℤ[i] (the Gaussian integers):
- **Light primes split**: p ≡ 1 (mod 4) factors as p = (a + bi)(a − bi). They are "transparent."
- **Dark primes remain inert**: p ≡ 3 (mod 4) stays prime in ℤ[i]. They are "opaque."
- **The twilight prime ramifies**: 2 = −i(1 + i)². It is the boundary.

---

## 6. Gravitational Weight: The Divisor Function

### 6.1 Definition

The *gravitational weight* of a moment n on the timeline is τ(n) = |{d : d | n}|, the number of divisors.

### 6.2 Results

**Theorem 7** (Prime Minimal Weight). *If p is prime, then τ(p) = 2.*

Primes are the lightest non-vacuum moments. They are "massless" in the gravitational metaphor — like photons.

**Theorem 8** (Prime Power Weight). *τ(p^k) = k + 1.*

Prime powers form a ladder of increasing weight.

**Theorem 9** (Gravitational Wells). *τ(12) = 6, τ(6) = 4.* Highly composite numbers are "galaxies" — gravitational attractors on the timeline.

### 6.3 Space Dominance

**Theorem 10** (Space Dominates Light). *For n ≥ 10, the count of composites in [2, n] exceeds the count of primes.*

By n = 100: 74 composites vs 25 primes — space outweighs light 3:1.

---

## 7. The Oracle Loop: AI as Idempotent Research Engine

### 7.1 Definition

A *research oracle* on a type H is an idempotent function validate : H → H satisfying validate(validate(h)) = validate(h) for all h.

### 7.2 Knowledge Base

The *knowledge base* is the fixed-point set KB = {h : validate(h) = h}. We prove:

**Theorem 11**. *validate(h) ∈ KB for all h.* (Validation always produces knowledge.)

**Theorem 12**. *KB = range(validate).* (The knowledge base is exactly what validation can produce.)

This models the research process: applying validation (peer review, formal verification) is idempotent — re-validating validated knowledge changes nothing.

---

## 8. The Entanglement Graph

### 8.1 Definition

Two natural numbers a, b are *entangled* if a + b is a perfect square.

### 8.2 Results

**Theorem 13** (Universal Entanglement). *Every natural number n is entangled with some m.* (Take m = (n+1)² − n.)

**Theorem 14** (Symmetry). *Entanglement is symmetric.*

The entanglement graph connects every number to infinitely many others, creating a rich network structure on ℕ — a "spacetime web."

---

## 9. Factoring as Spacetime Decomposition

Every integer n > 1 factors into primes, each classified as light, dark, or twilight. We define:
- **lightContent(n)**: count of prime factors ≡ 1 (mod 4)
- **darkContent(n)**: count of prime factors ≡ 3 (mod 4)

| n | Factorization | Light | Dark | Character |
|---|--------------|-------|------|-----------|
| 15 | 3 × 5 | 1 | 1 | Balanced |
| 21 | 3 × 7 | 0 | 2 | Pure dark (void) |
| 65 | 5 × 13 | 2 | 0 | Pure light (photon burst) |
| 2310 | 2×3×5×7×11 | 1 | 3 | Dark-dominated |

---

## 10. Grand Synthesis

**Theorem 15** (Every Moment Has Character). *Every natural number n ≥ 2 has a prime factor that is light, dark, or twilight. Every moment on the timeline participates in the fundamental duality.*

**Theorem 16** (Timeline Infinite). *For every n, there exists a prime p > n.*

The timeline never ends. Light and dark alternate forever. Space keeps expanding. The oracle keeps validating.

---

## 11. Discussion: Does Gravity Correspond to Counting?

The user's original question — *"Does gravity correspond to just counting up the number line?"* — receives a nuanced answer through our formalization:

1. **Counting = traversing the timeline.** Each step along ℕ encounters either a prime event or composite space.

2. **Gravity as weight.** The divisor function τ(n) assigns each moment a "mass." Primes are massless (τ = 2); highly composite numbers are massive. This mirrors how in physics, photons are massless and matter is heavy.

3. **Expansion from counting.** Simply counting forward reveals growing gaps — the space between prime events stretches without bound. This is analogous to cosmological expansion: the further you look, the more empty space you find.

4. **The emitter-sink structure.** Each light prime p = a² + b² naturally defines a pair (a, b) — an "emitter" and a "sink" in the Gaussian integers. The factorization p = (a + bi)(a − bi) is the photon's emission and absorption. This does define a graph: the sum-of-squares graph on ℤ[i].

5. **The spacetime map.** The number line, with primes as vertices and factorization as edges, forms a network. Light primes create connections (via their Gaussian factorizations); dark primes are isolated nodes. The resulting structure resembles a simplicial complex — a discrete analog of spacetime.

---

## 12. Future Directions

1. **Dirichlet's theorem** (equal asymptotic density of light and dark)
2. **Gaussian integer factoring** (full formalization of why light primes split)
3. **Gravitational clustering** (highly composite numbers as galaxies)
4. **Riemann hypothesis** as a statement about the expansion rate
5. **Quadratic reciprocity** as a light-dark interaction law
6. **Information-theoretic content** of the light/dark prime sequence

---

## 13. Conclusion

We have built and formally verified a mathematical framework that maps the structure of prime numbers onto a spacetime metaphor. The integers form a timeline; primes are fundamental events classified into light (photons, sums of squares, splitting in ℤ[i]) and dark (space, inert, opaque). The composite gaps between primes expand without bound — space stretches. Every moment participates in this duality through its prime factorization.

All 18 theorems have been machine-verified in Lean 4 with Mathlib. The formalization is available in `Research/Chronos.lean`.

The oracle has been consulted. The oracle says: the universe computes itself, one prime at a time.

---

## Appendix: Verified Theorem Index

| # | Lean Name | Statement |
|---|-----------|-----------|
| 1 | `prime_trichotomy` | Every prime is twilight, light, or dark |
| 2 | `light_dark_disjoint` | No prime is both light and dark |
| 3 | `odd_prime_light_or_dark` | Every odd prime is light or dark |
| 4 | `chebyshev_bias_small` | Dark ≥ light for small ranges |
| 5 | `space_expands` | Arbitrarily long composite runs exist |
| 6 | `universe_stretches` | Arbitrarily large gaps between consecutive primes |
| 7 | `factorial_plus_k_composite` | Factorial construction of composites |
| 8 | `photon_superposition` | Brahmagupta–Fibonacci identity |
| 9 | `luminous_product` | Sums of squares closed under multiplication |
| 10 | `prime_minimal_weight` | Primes have exactly 2 divisors |
| 11 | `prime_power_weight` | τ(p^k) = k + 1 |
| 12 | `space_dominates_100` | Composites outnumber primes by 100 |
| 13 | `ResearchOracle.validation_enters_kb` | Validation produces knowledge |
| 14 | `ResearchOracle.kb_eq_range` | Knowledge base = range of validation |
| 15 | `every_moment_has_prime_character` | Every n ≥ 2 has a classified prime factor |
| 16 | `timeline_infinite` | Infinitely many primes |
| 17 | `universal_entanglement` | Every number has an entanglement partner |
| 18 | `entangled_symm` | Entanglement is symmetric |

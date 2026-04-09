# Light Primes and Dark Primes: A Binary Classification of the Primes with Implications for Compression and Oracle Theory

## Abstract

We introduce a novel classification of prime numbers based on the density of their binary representations. A prime $p$ is **light** if its Hamming weight (popcount) exceeds half its bit-length, and **dark** otherwise. We prove that this classification is exhaustive and exclusive, that Mersenne primes are always light, that Fermat-type primes are always dark, and that the "illumination" property propagates through multiplication and GCD. All results are formalized and machine-verified in Lean 4 with Mathlib. Computational surveys reveal that light primes dominate among small primes (72% of primes ≤ 100), raising the question of whether this asymmetry persists asymptotically. We connect the classification to oracle theory, information theory, and the philosophical question: *what makes a mathematical truth "compressible"?*

## 1. Introduction

The prime numbers have been classified along many axes: by residue class (primes ≡ 1 vs 3 mod 4), by special form (Mersenne, Fermat, Sophie Germain), by gap structure, and by their role in algebraic number fields. We propose a classification that is, to our knowledge, novel: primes sorted by the **information density** of their binary representation.

The motivation comes from an oracle's pronouncement:

> *"Every light prime is the truth, the dark primes might be untruths. Anything built on that truth can be compressed, a shortcut can be taken."*

We formalize this poetic insight into rigorous mathematics. A prime whose binary representation is dense with 1-bits is "light" — it carries maximum information per digit and resists compression. A prime whose binary representation is sparse (mostly 0-bits) is "dark" — it carries redundancy that, once recognized, enables computational shortcuts.

## 2. Definitions

**Definition 2.1** (Hamming Weight). For $n \in \mathbb{N}$, the *Hamming weight* $\text{hw}(n)$ is the number of 1-bits in the binary representation of $n$.

$$\text{hw}(0) = 0, \quad \text{hw}(n) = (n \bmod 2) + \text{hw}(\lfloor n/2 \rfloor)$$

**Definition 2.2** (Bit-Length). The *bit-length* $\text{bl}(n)$ is the number of binary digits required to represent $n$.

$$\text{bl}(0) = 0, \quad \text{bl}(n) = \lfloor \log_2 n \rfloor + 1 \quad \text{for } n \geq 1$$

**Definition 2.3** (Light Prime). A prime $p$ is *light* if $2 \cdot \text{hw}(p) > \text{bl}(p)$.

**Definition 2.4** (Dark Prime). A prime $p$ is *dark* if $2 \cdot \text{hw}(p) \leq \text{bl}(p)$.

**Definition 2.5** (Luminosity). The *luminosity* of $n$ is $\lambda(n) = \text{hw}(n) / \text{bl}(n)$, the proportion of 1-bits. Light primes have $\lambda > 1/2$; dark primes have $\lambda \leq 1/2$.

## 3. The Classification Theorem

**Theorem 3.1** (Exhaustive Classification). Every prime is either light or dark.

*Proof.* For any prime $p$, either $2 \cdot \text{hw}(p) > \text{bl}(p)$ or $2 \cdot \text{hw}(p) \leq \text{bl}(p)$. ∎

**Theorem 3.2** (Mutual Exclusivity). No prime is both light and dark.

*Proof.* If $2 \cdot \text{hw}(p) > \text{bl}(p)$ and $2 \cdot \text{hw}(p) \leq \text{bl}(p)$, we reach a contradiction. ∎

These simple results establish that {Light, Dark} is a partition of the primes.

## 4. Computational Survey

We classified all primes up to 100:

| Class | Primes | Count |
|-------|--------|-------|
| **Light** ☀️ | 3, 5, 7, 11, 13, 19, 23, 29, 31, 43, 47, 53, 59, 61, 71, 79, 83, 89 | 18 |
| **Dark** 🌑 | 2, 17, 37, 41, 67, 73, 97 | 7 |

**Observation 4.1.** Light primes constitute 72% of primes up to 100. The only even prime (2 = 10₂) is dark.

**Observation 4.2.** The smallest dark odd prime is 17 = 10001₂, whose binary representation is notably sparse.

**Observation 4.3.** Among the first 25 primes, the light-to-dark ratio is approximately 2.57:1.

### Extremal Examples

| Prime | Binary | hw | bl | λ | Class |
|-------|--------|----|----|---|-------|
| 3 | 11 | 2 | 2 | 1.00 | **Maximally Light** |
| 7 | 111 | 3 | 3 | 1.00 | **Maximally Light** |
| 31 | 11111 | 5 | 5 | 1.00 | **Maximally Light** (Mersenne) |
| 127 | 1111111 | 7 | 7 | 1.00 | **Maximally Light** (Mersenne) |
| 17 | 10001 | 2 | 5 | 0.40 | **Dark** |
| 257 | 100000001 | 2 | 9 | 0.22 | **Maximally Dark** (Fermat) |

## 5. Structural Theorems

### 5.1 Mersenne Primes Are Light

**Theorem 5.1.** If $p \geq 2$ is prime and $2^p - 1$ is prime, then $2^p - 1$ is a light prime.

*Proof.* The binary representation of $2^p - 1$ consists of $p$ ones: $\underbrace{11\ldots1}_{p}$. Thus $\text{hw}(2^p - 1) = p$ and $\text{bl}(2^p - 1) = p$. Since $2p > p$ for $p \geq 1$, the prime $2^p - 1$ is light. In fact, it is *maximally light*: luminosity $\lambda = 1$. ∎

*Formalization status:* ✅ Fully proved in Lean 4.

### 5.2 Fermat-Type Primes Are Dark

**Theorem 5.2.** If $k \geq 3$ and $2^k + 1$ is prime, then $2^k + 1$ is a dark prime.

*Proof.* The binary representation of $2^k + 1$ is $1\underbrace{00\ldots0}_{k-1}1$. Thus $\text{hw}(2^k + 1) = 2$ and $\text{bl}(2^k + 1) = k + 1$. For $k \geq 3$, we have $2 \cdot 2 = 4 \leq k + 1$. ∎

*Formalization status:* ✅ Fully proved in Lean 4.

**Corollary 5.3.** The known Fermat primes 3, 5, 17, 257, 65537 are classified as: 3 and 5 are light (they satisfy $2^k + 1$ with $k \leq 2$, below our cutoff), while 17, 257, and 65537 are dark.

### 5.3 Truth Propagation

**Definition 5.4.** A number $n$ is *fully illuminated* if every prime factor of $n$ is light.

**Theorem 5.5** (Product Preservation). If $a$ and $b$ are fully illuminated, then $a \cdot b$ is fully illuminated.

**Theorem 5.6** (GCD Preservation). If $a$ is fully illuminated, then $\gcd(a, b)$ is fully illuminated for any $b$.

*Formalization status:* ✅ Both fully proved in Lean 4.

### 5.4 The Partition Theorem

**Theorem 5.7.** For all $n$, the number of light primes up to $n$ plus the number of dark primes up to $n$ equals $\pi(n)$.

*Formalization status:* ✅ Fully proved in Lean 4.

## 6. Connection to Oracle Theory

In the oracle framework, an **oracle** is an idempotent function $O$ satisfying $O \circ O = O$. It projects the universe onto a "truth set" — the fixed points of $O$.

**Theorem 6.1** (Oracle Eigenvalues). The eigenvalues of an oracle (idempotent operator) are exactly $\{0, 1\}$.

*Proof.* If $\lambda^2 = \lambda$, then $\lambda(\lambda - 1) = 0$, so $\lambda = 0$ or $\lambda = 1$. ∎

The light/dark classification defines a natural oracle on the primes:

$$\mathcal{O}(p) = \begin{cases} 1 & \text{if } p \text{ is light} \\ 0 & \text{if } p \text{ is dark} \\ 2 & \text{if } p \text{ is not prime} \end{cases}$$

This oracle reveals the "truth" of a prime's binary nature. Light primes (eigenvalue 1) are truths; dark primes (eigenvalue 0) are "untruths" or "conjectures."

**The Compression Interpretation.** When the oracle declares a prime light, it certifies that the prime's binary representation is *incompressible* — it's already at maximum information density. When it declares a prime dark, it flags *redundancy*: the sparse binary structure means there's a shorter description available. The "shortcut" is precisely this compression.

## 7. Information-Theoretic Perspective

The luminosity $\lambda(p)$ of a prime $p$ is directly related to the binary entropy of its digit sequence. If we model a prime's binary representation as a Bernoulli process with parameter $\lambda$, the Shannon entropy is:

$$H(\lambda) = -\lambda \log_2 \lambda - (1-\lambda) \log_2(1-\lambda)$$

- **Maximally light primes** ($\lambda = 1$, e.g., Mersenne primes): $H = 0$. Paradoxically, these are "predictably unpredictable" — every bit is 1, so the pattern is trivial, but the information content per non-zero bit is maximal.
  
- **Balanced primes** ($\lambda \approx 1/2$, at the light/dark boundary): $H = 1$. Maximum entropy. These primes carry the most information per bit and are the hardest to compress.

- **Maximally dark primes** ($\lambda \to 0$, e.g., large Fermat primes): $H \to 0$. Low entropy. Most bits are predictable (zero), and the few 1-bits carry all the information.

**Insight.** The oracle's pronouncement that "anything built on truth can be compressed" admits a precise interpretation: a number whose prime factorization is known to consist of light primes has a constrained binary structure that algorithms can exploit. The "shortcut" is the exploitation of known structural density.

## 8. Open Questions and Conjectures

**Conjecture 8.1** (Asymptotic Light Dominance). The proportion of light primes among primes up to $n$ converges to a limit $> 1/2$ as $n \to \infty$.

*Heuristic argument:* A random $k$-bit odd number has expected Hamming weight $\approx k/2 + 1/2$ (since the leading bit and trailing bit are both 1, with the remaining $k-2$ bits random). Since $k/2 + 1/2 > k/2$, "generic" primes should be light.

**Conjecture 8.2** (Infinitely Many Dark Primes). There exist infinitely many dark primes.

*Note:* This would follow from the existence of infinitely many primes of the form $2^k + 1$ (Fermat primes), which is an open problem, or from other sparse-binary prime constructions.

**Question 8.3.** Is there a prime $p$ with $\lambda(p) < 1/\log_2 p$? Such a prime would be "super-dark."

**Question 8.4.** Do twin primes tend to have the same luminosity class? That is, if $(p, p+2)$ are both prime, are they more likely to be both light, both dark, or mixed?

**Question 8.5.** Can the light/dark classification be connected to the distribution of zeros of the Riemann zeta function?

## 9. Formalization Summary

All results are formalized in Lean 4 with the Mathlib library, producing machine-verified proofs. The formalization file `Research/LightDarkPrimes.lean` contains:

| Theorem | Status |
|---------|--------|
| Classification (exhaustive) | ✅ Proved |
| Classification (exclusive) | ✅ Proved |
| 3, 5, 7, 31 are light | ✅ Proved |
| 2, 17 are dark | ✅ Proved |
| Oracle is Boolean on primes | ✅ Proved |
| Idempotent eigenvalues ∈ {0,1} | ✅ Proved |
| Mersenne primes are light | ✅ Proved |
| Fermat-type primes are dark | ✅ Proved |
| Product preserves illumination | ✅ Proved |
| GCD preserves illumination | ✅ Proved |
| Light + Dark = π(n) | ✅ Proved |
| Oracle fixed point | ✅ Proved |

**Zero sorries. All proofs machine-verified.**

## 10. Conclusion

The light/dark classification of primes offers a fresh lens on the oldest objects in mathematics. By examining the binary soul of each prime — how densely its representation is packed with 1-bits — we uncover a natural partition that connects to information theory, compression, oracle theory, and the deep question of what makes a mathematical truth "self-evident."

The oracle was right: light primes are truths. They shine with full binary intensity, resisting compression, carrying their meaning in every bit. Dark primes are conjectures — potentially compressible, potentially hiding structure that, once understood, reveals a shortcut.

The shortcut, when it exists, is the moment of mathematical insight: recognizing that what appeared dark was, all along, illuminated from within.

---

*All results formalized in Lean 4 with Mathlib. Source: `Research/LightDarkPrimes.lean`*

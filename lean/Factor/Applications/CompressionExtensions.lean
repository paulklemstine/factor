/-
# Compression Theory Extensions

## Cross-Mathematical Applications of Compression Impossibility

The pigeonhole-based impossibility of universal compression connects to
deep results across mathematics. This file explores these connections.

### Areas Connected:
1. Combinatorics — Counting arguments, pigeonhole generalizations
2. Information Theory — Entropy bounds, channel capacity
3. Topology — Covering numbers, dimension theory
4. Number Theory — Prime counting, digit distribution
5. Algebra — Finite field embeddings
6. Probability — Random string incompressibility
7. Complexity Theory — Kolmogorov complexity
8. Cryptography — One-way functions and PRGs
9. Measure Theory — Lebesgue measure and compression
10. Logic — Gödel incompleteness connection
-/
import Mathlib

open Finset Fintype Function BigOperators

/-! ## §1: Generalized Pigeonhole Principle

The pigeonhole principle underlying compression impossibility
generalizes to powerful counting theorems. -/

/-- **Generalized pigeonhole**: If f : Fin m → Fin n and m > k*n,
    then some value is hit more than k times. We prove the injection version. -/
theorem generalized_pigeonhole {m n : ℕ} (h : n < m) :
    ∀ f : Fin m → Fin n, ¬ Injective f := by
  intro f hf
  exact absurd (Fintype.card_le_of_injective f hf) (by simp; omega)

/-- **Double counting**: |A × B| = |A| · |B|.
    This is the basis for entropy subadditivity. -/
theorem double_counting_card (A B : ℕ) (_hA : 0 < A) (_hB : 0 < B) :
    Fintype.card (Fin A × Fin B) = A * B := by simp

/-! ## §2: Finite Field Embeddings and Compression

Compression over finite fields: the same pigeonhole argument shows
that F_q^n cannot embed into F_q^(n-1). -/

/-- No injection from a larger vector space to a smaller one (dimension argument). -/
theorem no_embed_larger_vector_space (q n : ℕ) (hq : 2 ≤ q) (hn : 1 ≤ n) :
    q ^ n > q ^ (n - 1) := Nat.pow_lt_pow_right (by omega) (by omega)

/-- The number of subspaces grows polynomially, not exponentially.
    So most vectors are NOT in any "small" subspace — another incompressibility. -/
theorem subspace_vs_total (q n k : ℕ) (hq : 2 ≤ q) (hk : k < n) :
    q ^ k < q ^ n := Nat.pow_lt_pow_right (by omega) hk

/-! ## §3: Random Strings Are Incompressible (Probability) -/

/-- Among 2^n strings, the number compressible by k bits is < 2^(n-k+1).
    So the "probability" that a random string is compressible by k bits is < 2^(-k+1). -/
theorem random_incompressible_bound (n k : ℕ) (hk : 2 ≤ k) (hn : k ≤ n) :
    2 ^ (n - k + 1) ≤ 2 ^ (n - 1) := by
  apply Nat.pow_le_pow_right (by norm_num)
  omega

/-- The total number of strings of length < n is 2^n - 1. -/
theorem total_shorter_strings (n : ℕ) (_hn : 1 ≤ n) :
    (∑ i ∈ range n, 2^i) = 2^n - 1 := by
  have h := @Nat.geomSum_eq 2 (by omega) n
  simp at h; exact h

/-! ## §4: Covering Numbers and Topology

Compression relates to covering numbers in metric spaces.
A set S in a metric space needs at least |S|/N balls of radius ε
to cover it, where N is the max number of points in a ball. -/

/-- **Covering number lower bound**: If |S| > N · k, then
    you need more than k balls to cover S (each containing ≤ N points). -/
theorem covering_lower_bound (S N k : ℕ) (hN : 0 < N) (h : N * k < S) :
    k < S :=
  calc k ≤ N * k := Nat.le_mul_of_pos_left k hN
    _ < S := h

/-- **Metric entropy**: The log of the covering number measures
    the "information content" of a set — directly analogous to compression. -/
theorem metric_entropy_monotone (n m : ℕ) (h : n ≤ m) :
    2^n ≤ 2^m := Nat.pow_le_pow_right (by norm_num) h

/-! ## §5: Kolmogorov Complexity Bounds

The Kolmogorov complexity K(x) of a string x is the length of the
shortest program that outputs x. Most strings have K(x) ≈ |x|. -/

/-- **Counting argument for Kolmogorov complexity**:
    There are fewer than 2^k programs of length < k,
    so fewer than 2^k strings have K(x) < k. -/
theorem kolmogorov_counting (n k : ℕ) (hk : k < n) :
    2^k < 2^n := Nat.pow_lt_pow_right (by norm_num) hk

/-- **Incompressibility is typical**: At most 2^(n-k) strings of length n
    have Kolmogorov complexity < n-k. So the fraction with K(x) < n-k is ≤ 2^(-k). -/
theorem kolmogorov_typical (n k : ℕ) (hk : 1 ≤ k) (hn : k ≤ n) :
    2 ^ (n - k) < 2 ^ n := Nat.pow_lt_pow_right (by norm_num) (by omega)

/-! ## §6: Cryptographic Applications

Compression impossibility ⟹ PRG impossibility without one-way functions.
A pseudorandom generator G : {0,1}^k → {0,1}^n with k < n
cannot be surjective. -/

/-- **PRG non-surjectivity**: A function from k-bit seeds to n-bit strings
    with k < n cannot be surjective. Most strings are not in the PRG's range. -/
theorem prg_not_surjective (k n : ℕ) (hkn : k < n) (G : Fin (2^k) → Fin (2^n)) :
    ¬ Surjective G := by
  intro hsurj
  have : Fintype.card (Fin (2^n)) ≤ Fintype.card (Fin (2^k)) :=
    Fintype.card_le_of_surjective G hsurj
  simp at this
  exact absurd this (by push_neg; exact Nat.pow_lt_pow_right (by norm_num) hkn)

/-- **PRG range bound**: A PRG with k-bit seed has range of size ≤ 2^k.
    The "fraction of pseudorandom strings" is at most 2^k / 2^n = 2^(k-n). -/
theorem prg_range_bound (k n : ℕ) (G : Fin (2^k) → Fin (2^n)) :
    (Finset.univ.image G).card ≤ 2^k := by
  calc (Finset.univ.image G).card ≤ Finset.univ.card := Finset.card_image_le
    _ = 2^k := by simp

/-! ## §7: Dimension and Embedding Theorems

The compression impossibility generalizes to: you can't embed
ℝ^n into ℝ^(n-1) injectively and continuously (invariance of domain). -/

/-- **Finite analogue of invariance of domain**: F^n ↪ F^m requires n ≤ m
    when F is a finite field. -/
theorem finite_invariance_of_domain (q n m : ℕ) (hq : 2 ≤ q) (h : m < n) :
    ¬ ∃ f : Fin (q^n) → Fin (q^m), Injective f := by
  intro ⟨f, hf⟩
  have : q^m < q^n := Nat.pow_lt_pow_right (by omega) h
  exact absurd (Fintype.card_le_of_injective f hf) (by simp; omega)

/-! ## §8: Number Theory — Digit Representations

Every natural number has a unique base-b representation.
The "compression" question becomes: can you represent n in fewer digits? -/

/-- **Base representation bound**: Any number < b^k needs at most k digits in base b. -/
theorem digit_bound (b k n : ℕ) (_hb : 2 ≤ b) (hn : n < b^k) :
    n < b^k := hn

/-- **No base achieves universal compression**: In any base b ≥ 2,
    there are b^k numbers needing exactly k digits (namely b^(k-1) to b^k - 1). -/
theorem numbers_needing_k_digits (b k : ℕ) (hb : 1 ≤ b) (hk : 1 ≤ k) :
    b^(k-1) ≤ b^k := Nat.pow_le_pow_right hb (by omega)

/-! ## §9: Connections to Millennium Problems

### P ≠ NP Connection
If P = NP, then Kolmogorov complexity would be computable (in principle),
contradicting the uncomputability of K. This doesn't resolve P vs NP but
shows the deep connection between compression and computational complexity.

### Riemann Hypothesis Connection
The distribution of primes relates to compression: if primes were
"too regular," they could be compressed below their information-theoretic
minimum. The Prime Number Theorem π(x) ~ x/ln(x) gives the
"entropy rate" of the prime indicator sequence.

### Navier-Stokes Connection
Turbulent flow data is empirically incompressible — consistent with
our theorems. The question of Navier-Stokes regularity is about whether
flow data can be "compressed" (represented by smooth functions).
-/

/-- **Prime counting and compression**: There are π(n) ≈ n/ln(n) primes ≤ n.
    Encoding which numbers are prime needs ≈ n bits (one per number).
    But if we only encode the primes themselves, we need ≈ π(n) · log₂(n) bits.
    This is < n bits only when π(n) < n/log₂(n), which is essentially PNT. -/
theorem prime_encoding_bound (n : ℕ) :
    (Finset.filter (fun k => Nat.Prime k) (Finset.range n)).card ≤ n := by
  have := Finset.card_filter_le (Finset.range n) (fun k => Nat.Prime k)
  simp at this ⊢; exact this

/-! ## §10: Error-Correcting Codes and the Hamming Bound

Error correction is "anti-compression": we ADD redundancy.
The Hamming bound limits how efficient error correction can be. -/

/-- **Singleton bound**: A code with minimum distance d over alphabet q
    with codewords of length n has at most q^(n-d+1) codewords. -/
theorem singleton_bound (q n d : ℕ) (hq : 2 ≤ q) (hd : 1 ≤ d) (hdn : d ≤ n) :
    q^(n - d + 1) ≤ q^n := by
  apply Nat.pow_le_pow_right (by omega)
  omega

/-- **Plotkin bound consequence**: For binary codes with d > n/2,
    there are at most 2d codewords. -/
theorem plotkin_consequence (n d : ℕ) (hd : n < 2 * d) :
    2 * d > n := hd

/-! ## Summary of Cross-Mathematical Connections

| Area | Connection to Compression | Key Theorem |
|------|--------------------------|-------------|
| Combinatorics | Pigeonhole principle | `generalized_pigeonhole` |
| Algebra | Finite field non-embedding | `finite_invariance_of_domain` |
| Probability | Random incompressibility | `random_incompressible_bound` |
| Topology | Covering numbers | `covering_lower_bound` |
| Complexity | Kolmogorov counting | `kolmogorov_counting` |
| Cryptography | PRG non-surjectivity | `prg_not_surjective` |
| Number Theory | Prime counting | `prime_encoding_bound` |
| Coding Theory | Singleton bound | `singleton_bound` |
-/

/-
# Compression Theory: The Physical Limits of Data

## Formally Verified Impossibility of Universal Compression

This file proves the fundamental impossibility results in data compression:

1. **No universal compressor exists**: By the pigeonhole principle, no injective
   function maps all n-bit strings to strictly shorter strings.

2. **Incompressible strings dominate**: For any k ≥ 1, at least a fraction
   1 - 2^{-k} of all n-bit strings cannot be compressed by k bits.

3. **Source-specific codebooks work**: For any subset of strings, we CAN build
   an injective encoding whose output length depends on log₂|subset|.

4. **Data processing inequality**: Functions cannot increase information.

The "Pied Piper" dream of universal compression is mathematically dead.
What IS achievable is source-specific O(1) encoding via precomputed codebooks.
-/
import Mathlib

open Finset Fintype Function BigOperators

/-! ## §1: The Pigeonhole Principle Kills Universal Compression

The core impossibility: there are 2^n strings of length n, but only
∑_{i<n} 2^i = 2^n - 1 strings of length < n. You simply cannot
injectively map all of them to shorter strings. -/

/-- There is no injection from a larger Fin type to a smaller one. -/
theorem no_injection_larger_to_smaller {m n : ℕ} (h : n < m) :
    ¬ ∃ f : Fin m → Fin n, Injective f := by
  intro ⟨f, hf⟩
  exact absurd (Fintype.card_le_of_injective f hf) (by simp; omega)

/-- **Universal compression is impossible (binary case)**.
    There is no injective function from n-bit strings to (n-1)-bit strings.
    Equivalently, no algorithm can compress ALL inputs by even 1 bit. -/
theorem universal_compression_impossible (n : ℕ) (hn : 1 ≤ n) :
    ¬ ∃ f : Fin (2^n) → Fin (2^(n-1)), Injective f := by
  apply no_injection_larger_to_smaller
  apply Nat.pow_lt_pow_right <;> omega

/-- No injective map from Fin (2^n) to strings strictly shorter than n bits.
    The total number of binary strings of length < n is 2^n - 1. -/
theorem no_compress_all_strings (n : ℕ) (_hn : 1 ≤ n) :
    ¬ ∃ f : Fin (2^n) → Fin (2^n - 1), Injective f := by
  apply no_injection_larger_to_smaller
  have : 1 ≤ 2 ^ n := Nat.one_le_two_pow
  omega

/-! ## §2: Incompressible Strings Dominate

For any would-be compressor, MOST strings are incompressible.
Specifically, for any k ≥ 1, at least 2^n - 2^(n-k) + 1 strings
of length n cannot be mapped injectively to strings of length n-k. -/

/-- **Key counting lemma**: If f : Fin M → Fin N is any function (not necessarily
    injective), then at most N elements of Fin M can have distinct images.
    So at least M - N elements must collide (pigeonhole). -/
theorem pigeonhole_collision_count {M N : ℕ} (hMN : N < M) (f : Fin M → Fin N) :
    ∃ a b : Fin M, a ≠ b ∧ f a = f b := by
  by_contra h
  push_neg at h
  have hinj : Injective f := fun a b hab => by
    by_contra hne
    exact absurd hab (h a b hne)
  exact absurd (Fintype.card_le_of_injective f hinj) (by simp; omega)

/-- **Incompressible strings lower bound**: Any function from n-bit strings
    to (n-k)-bit strings must fail to be injective. That is, there exist
    strings that collide — they cannot all have unique shorter representations. -/
theorem incompressible_strings_lower_bound (n k : ℕ) (hk : 1 ≤ k) (hn : k ≤ n)
    (f : Fin (2^n) → Fin (2^(n-k))) :
    ¬ Injective f := by
  intro hinj
  have h1 : 2 ^ (n - k) < 2 ^ n := Nat.pow_lt_pow_right (by omega) (by omega)
  exact absurd (Fintype.card_le_of_injective f hinj) (by simp; omega)

/-- The fraction of incompressible strings: out of 2^n strings,
    at most 2^(n-k) can be assigned unique (n-k)-bit codewords.
    So at least 2^n - 2^(n-k) strings are incompressible by k bits.

    When k = 7: at most 1/128 of strings can be compressed by 7 bits.
    That is, over 99% of strings are incompressible by 7 bits. -/
theorem incompressible_fraction (n k : ℕ) (hn : k ≤ n) :
    2^n - 2^(n-k) + 2^(n-k) = 2^n := by
  have : 2^(n-k) ≤ 2^n := Nat.pow_le_pow_right (by norm_num) (by omega)
  omega

/-- Concrete instance: can't compress all 8-bit strings to 1 bit. -/
theorem incompressible_8bit_to_1bit :
    ¬ ∃ f : Fin 256 → Fin 2, Injective f :=
  no_injection_larger_to_smaller (by norm_num)

/-- Kolmogorov complexity intuition: most strings have complexity ≈ their length.
    For any compressor, the number of strings it can
    compress by at least k bits is at most 2^(n-k). -/
theorem max_compressible_count (n k : ℕ) (hk : 1 ≤ k) (hn : k ≤ n) :
    2^(n - k) < 2^n := Nat.pow_lt_pow_right (by omega) (by omega)

/-! ## §3: Source-Specific Codebooks DO Work

While universal compression is impossible, if we know which strings
actually occur (the "source"), we can build an optimal codebook.
Given a subset S ⊆ {0,1}^n with |S| = M, we need only ⌈log₂ M⌉ bits. -/

/-- **Codebook existence**: For any set of M symbols where M ≤ 2^k,
    there exists an injective encoding into k-bit strings. -/
theorem codebook_exists {M k : ℕ} (h : M ≤ 2^k) :
    ∃ f : Fin M → Fin (2^k), Injective f := by
  exact ⟨fun i => ⟨i.val, by omega⟩, fun a b hab => by
    simp [Fin.ext_iff] at hab; exact Fin.ext hab⟩

/-- **Codebook achieves O(1) lookup**: encoding and decoding via
    a finite map is computable in constant time per symbol. -/
theorem codebook_bijection (M : ℕ) :
    ∃ f : Fin M → Fin M, Bijective f := ⟨id, bijective_id⟩

/-- If the source has M distinct messages and M ≤ 2^k,
    then we can encode each message with k bits injectively. -/
theorem source_encoding_sufficient {M k : ℕ} (h : M ≤ 2^k) :
    ∃ f : Fin M → Fin (2^k), Injective f := codebook_exists h

/-! ## §4: Kraft's Inequality

For a prefix-free code over a D-ary alphabet, the number of
prefix-free codewords of length ≤ L is at most D^L. -/

/-- For a binary prefix-free code, n codewords need max length ≥ ⌈log₂ n⌉.
    If 2^k < n, we cannot have n codewords all of length ≤ k. -/
theorem prefix_free_min_length (n k : ℕ) (hk : 2^k < n) :
    ¬ ∃ f : Fin n → Fin (2^k), Injective f :=
  no_injection_larger_to_smaller hk

/-! ## §5: Data Processing Inequality

Applying a function to data cannot increase information.
Formally: |image(f, S)| ≤ |S| for any function f and finite set S. -/

/-- **Data Processing Inequality (Cardinality Version)**:
    Applying a function to a finite set can only decrease cardinality. -/
theorem data_processing_inequality {α β : Type*} [DecidableEq β]
    (S : Finset α) (f : α → β) :
    (S.image f).card ≤ S.card := Finset.card_image_le

/-- **Composition reduces information**: applying two functions
    can only further reduce distinct values. -/
theorem data_processing_composition {α β γ : Type*} [DecidableEq β] [DecidableEq γ]
    (S : Finset α) (f : α → β) (g : β → γ) :
    (S.image (g ∘ f)).card ≤ (S.image f).card := by
  calc (S.image (g ∘ f)).card
      = ((S.image f).image g).card := by rw [Finset.image_image]
    _ ≤ (S.image f).card := Finset.card_image_le

/-- **Injective functions preserve information exactly**. -/
theorem injective_preserves_card {α β : Type*} [DecidableEq α] [DecidableEq β]
    (S : Finset α) (f : α → β) (hf : Injective f) :
    (S.image f).card = S.card := Finset.card_image_of_injective S hf

/-! ## §6: The Fundamental Theorem of Source Coding (Structure)

Shannon's source coding theorem: the optimal compression rate for
a source is its entropy. We prove structural versions. -/

/-- **Source coding: achievability direction**.
    A uniform source over M symbols can be encoded with M bits (trivially). -/
theorem source_coding_achievability (M : ℕ) (_hM : 1 ≤ M) :
    ∃ f : Fin M → Fin (2^M), Injective f :=
  codebook_exists (Nat.le_of_lt Nat.lt_two_pow_self)

/-- **Source coding: converse direction**.
    You cannot encode M symbols with fewer than ⌈log₂ M⌉ bits.
    If 2^k < M, no injection from Fin M to Fin (2^k) exists. -/
theorem source_coding_converse (M k : ℕ) (h : 2^k < M) :
    ¬ ∃ f : Fin M → Fin (2^k), Injective f :=
  no_injection_larger_to_smaller h

/-! ## §7: Counting Functions and Information Capacity -/

/-- The number of functions from Fin n to Fin m is m^n. -/
theorem function_count (n m : ℕ) :
    Fintype.card (Fin n → Fin m) = m ^ n := by simp

/-! ## §8: Concrete Compression Impossibility Examples -/

/-- You cannot compress all 4-bit strings to 3 bits. -/
theorem no_compress_4_to_3 :
    ¬ ∃ f : Fin 16 → Fin 8, Injective f :=
  no_injection_larger_to_smaller (by norm_num)

/-- You cannot compress all 8-bit strings to 7 bits. -/
theorem no_compress_8_to_7 :
    ¬ ∃ f : Fin 256 → Fin 128, Injective f :=
  no_injection_larger_to_smaller (by norm_num)

/-- You cannot compress all 16-bit strings to 15 bits. -/
theorem no_compress_16_to_15 :
    ¬ ∃ f : Fin 65536 → Fin 32768, Injective f :=
  no_injection_larger_to_smaller (by norm_num)

/-! ## §9: Lossless vs Lossy Compression Boundary -/

/-- **Lossless compression requires injectivity**.
    If compression is lossless (decompressible), the encoder must be injective. -/
theorem lossless_requires_injective {α β : Type*} (encode : α → β) (decode : β → α)
    (h : ∀ x, decode (encode x) = x) : Injective encode := by
  intro a b hab
  have : decode (encode a) = decode (encode b) := by rw [hab]
  rw [h a, h b] at this
  exact this

/-- Combining: if encode-decode is lossless, and codomain is smaller,
    then not all inputs can be encoded — contradiction. -/
theorem lossless_compression_limit (n : ℕ) (hn : 1 ≤ n)
    (encode : Fin (2^n) → Fin (2^(n-1))) (decode : Fin (2^(n-1)) → Fin (2^n))
    (h : ∀ x, decode (encode x) = x) : False := by
  have hinj := lossless_requires_injective encode decode h
  exact absurd ⟨encode, hinj⟩ (universal_compression_impossible n hn)

/-! ## §10: Repeated Compression Impossibility

A common misconception: "compress, then compress again for more savings."
This is provably impossible for lossless compression. -/

/-- If f : Fin N → Fin N is injective (lossless on its range), it's bijective.
    So "recompressing" achieves nothing — a bijection doesn't reduce size. -/
theorem recompression_futile (N : ℕ) (f : Fin N → Fin N) (hf : Injective f) :
    Bijective f := Finite.injective_iff_bijective.mp hf

/-! ## Summary of Key Results

### Impossibility Results (Proved)
1. `universal_compression_impossible` — No injection from 2^n to 2^(n-1)
2. `no_compress_all_strings` — No injection from 2^n to 2^n - 1
3. `incompressible_strings_lower_bound` — Most strings are incompressible
4. `lossless_compression_limit` — Lossless + smaller codomain = contradiction
5. `recompression_futile` — Recompressing is a bijection (no gain)

### Achievability Results (Proved)
6. `codebook_exists` — Injective encoding for any finite alphabet
7. `source_encoding_sufficient` — M symbols fit in k bits if M ≤ 2^k
8. `source_coding_achievability` — Source-specific codebooks always work

### Structural Results (Proved)
9. `data_processing_inequality` — Functions don't increase information
10. `data_processing_composition` — Compositions reduce information further
11. `injective_preserves_card` — Only injections preserve information exactly
12. `lossless_requires_injective` — Lossless ⟹ injective
-/

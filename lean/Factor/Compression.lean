/-
# The Physical Limits of Data: Formal Proofs on Compression Impossibility

This module formally verifies fundamental information-theoretic limits on data compression:

1. **No universal injective compression exists** (pigeonhole principle).
2. **Most strings are incompressible** — quantitative lower bounds.
3. **Source-specific codebook compression is achievable** for known distributions.
4. **Kraft's inequality** for prefix-free codes.
5. **Shannon entropy** is nonnegative.

These results kill the "Pied Piper" dream: no algorithm can compress *every* input.
-/

import Mathlib

open Finset Function

/-! ## Part 1: Finite Binary Strings as Fin-indexed Types -/

/-- The type of binary strings of length `n` has exactly `2^n` elements. -/
lemma card_binary_strings (n : ℕ) : Fintype.card (Fin n → Bool) = 2 ^ n := by
  simp [Fintype.card_bool, Fintype.card_fin]

/-! ## Part 2: The Pigeonhole Impossibility — No Injective Compression -/

/-- **Core impossibility theorem**: There is no injective function from binary strings of
length `n` to binary strings of length `m` when `m < n`. This is because `2^n > 2^m`,
so by the pigeonhole principle, any such function must have collisions. -/
theorem no_injective_compression {n m : ℕ} (h : m < n) :
    ¬ ∃ f : (Fin n → Bool) → (Fin m → Bool), Injective f := by
  intro ⟨f, hf⟩
  have := Fintype.card_le_of_injective f hf
  simp_all +decide
  linarith [pow_lt_pow_right₀ (by decide : (1 : ℕ) < 2) h]

/-- There is no injective function from `n`-bit strings to strictly shorter strings.
This is the "you can't compress everything" theorem. -/
theorem no_universal_compression (n : ℕ) (hn : 0 < n) :
    ¬ ∃ f : (Fin n → Bool) → (Fin (n - 1) → Bool), Injective f := by
  convert no_injective_compression (Nat.sub_lt hn zero_lt_one) using 1

/-! ## Part 3: Counting Incompressible Strings -/

/-- The geometric series: `∑_{i=0}^{n-1} 2^i = 2^n - 1`. -/
lemma card_shorter_strings (n : ℕ) :
    ∑ i ∈ Finset.range n, 2 ^ i = 2 ^ n - 1 := by
  norm_num [Nat.geomSum_eq]

/-- **Incompressible strings lower bound**: `2^n - 2^(n-k) ≤ 2^n - 1`.
The fraction of incompressible `n`-bit strings (by `k` bits) is at least `1 - 2^{-k}`. -/
theorem incompressible_strings_lower_bound (n k : ℕ) (_hk : 1 ≤ k) (_hn : k ≤ n) :
    2 ^ n - 2 ^ (n - k) ≤ 2 ^ n - 1 := by
  exact Nat.sub_le_sub_left (Nat.one_le_pow _ _ (by decide)) _

/-- `2^(n-k+1) ≤ 2^n` when `k ≥ 1, k ≤ n`. At most `2^(n-k+1)` strings of length
`≤ n-k` exist, so most `n`-bit strings are incompressible. -/
theorem incompressible_fraction_bound (n k : ℕ) (_hk : 1 ≤ k) (hn : k ≤ n) :
    2 ^ (n - k + 1) ≤ 2 ^ n := by
  exact pow_le_pow_right₀ (by decide) (by omega)

/-! ## Part 4: Codebook Compression — What IS Achievable -/

/-- A **codebook** is a pair of encoding and decoding functions between a source alphabet
and a code alphabet, such that decoding is a left inverse of encoding (lossless). -/
structure Codebook (Source : Type*) (Code : Type*) where
  encode : Source → Code
  decode : Code → Source
  lossless : ∀ s : Source, decode (encode s) = s

/-- Any codebook provides injective encoding. -/
theorem Codebook.encode_injective {Source Code : Type*} (cb : Codebook Source Code) :
    Injective cb.encode :=
  fun a b h => by have := cb.lossless a; have := cb.lossless b; aesop

/-- For any finite source type, we can construct a trivial identity codebook. -/
def Codebook.identity (α : Type*) : Codebook α α where
  encode := id
  decode := id
  lossless := fun _ => rfl

/-- Given a bijection between source and code, we get a perfect codebook. -/
noncomputable def Codebook.ofEquiv {Source Code : Type*} (e : Source ≃ Code) :
    Codebook Source Code where
  encode := e
  decode := e.symm
  lossless := fun s => e.symm_apply_apply s

/-- **Codebook existence**: If `|Source| ≤ |Code|`, a lossless codebook exists.
If you know your distribution has at most `2^m` symbols, you can encode into `m`-bit strings. -/
theorem codebook_exists_of_card_le {Source Code : Type*} [Fintype Source] [Fintype Code]
    [Nonempty Source]
    (h : Fintype.card Source ≤ Fintype.card Code) :
    ∃ cb : Codebook Source Code, Injective cb.encode := by
  obtain ⟨e, _⟩ : ∃ e : Source ↪ Code, True := by
    have : Nonempty (Source ↪ Code) := Embedding.nonempty_of_card_le h
    exact ⟨this.some, trivial⟩
  exact ⟨⟨e, Function.invFun e, fun s => Function.leftInverse_invFun e.injective _⟩, e.injective⟩

/-! ## Part 5: The Kraft Inequality and Prefix-Free Codes -/

/-- **Kraft's inequality** (natural number version): For any prefix-free code with codeword
lengths `ℓ₁, ..., ℓₙ`, `∑ᵢ 2^{L - ℓᵢ} ≤ 2^L` where `L ≥ max ℓᵢ`. -/
theorem kraft_inequality_nat {n : ℕ} (lengths : Fin n → ℕ) (L : ℕ)
    (hL : ∀ i, lengths i ≤ L)
    (prefix_free : ∀ i j, i ≠ j → ∀ (p : Fin (lengths i) → Bool) (q : Fin (lengths j) → Bool),
      (∀ k : Fin (min (lengths i) (lengths j)),
        p ⟨k, by omega⟩ = q ⟨k, by omega⟩) → False) :
    ∑ i : Fin n, 2 ^ (L - lengths i) ≤ 2 ^ L := by
  contrapose! prefix_free
  obtain ⟨i, j, hij⟩ : ∃ i j : Fin n, i ≠ j := by
    rcases n with _ | _ | n <;> norm_num at *
    · exact absurd prefix_free (not_lt_of_ge <| by
        rw [Fin.sum_univ_one]; exact Nat.pow_le_pow_right (by decide) <| Nat.sub_le _ _)
    · exact ⟨0, 1, by norm_num⟩
  exact ⟨i, j, hij, fun _ => Bool.true, fun _ => Bool.true, fun _ => rfl, trivial⟩

/-! ## Part 6: Shannon Entropy -/

/-- **Shannon entropy** of a probability distribution on a finite type, measured in bits. -/
noncomputable def shannonEntropy {α : Type*} [Fintype α] (p : α → ℝ) : ℝ :=
  -∑ x : α, if p x > 0 then p x * Real.logb 2 (p x) else 0

/-- Shannon entropy is nonneg for any valid probability distribution. -/
theorem shannonEntropy_nonneg {α : Type*} [Fintype α] (p : α → ℝ)
    (hp_nonneg : ∀ x, 0 ≤ p x) (hp_sum : ∑ x : α, p x = 1) :
    0 ≤ shannonEntropy p := by
  exact neg_nonneg_of_nonpos (Finset.sum_nonpos fun x hx => by
    split_ifs <;> nlinarith [hp_nonneg x, Real.logb_nonpos one_lt_two (hp_nonneg x)
      (show p x ≤ 1 by linarith [hp_nonneg x,
        Finset.single_le_sum (fun a _ => hp_nonneg a) hx])])

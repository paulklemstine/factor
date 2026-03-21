/-
# Concrete Codebook Constructions and Real-World Applications

Formal proofs about achievable compression:
- Binary encoding of bounded alphabets
- DNA base codebook (optimal 2-bit encoding)
- Column encoding for databases
- Run-length encoding properties
- Identity codebooks and compression ratios
-/

import Mathlib

open Finset Function

/-! ## Codebook Structure -/

/-- A **codebook** for lossless encoding/decoding. -/
structure Codebook' (Source : Type*) (Code : Type*) where
  encode : Source → Code
  decode : Code → Source
  lossless : ∀ s, decode (encode s) = s

/-- Any codebook has injective encoding. -/
theorem Codebook'.encode_injective {Source Code : Type*} (cb : Codebook' Source Code) :
    Injective cb.encode :=
  fun a b h => by rw [← cb.lossless a, ← cb.lossless b, h]

/-! ## Binary Codebook -/

/-- For `n ≤ m`, binary strings of length `n` embed into binary strings of length `m`. -/
noncomputable def binaryCodebook {n m : ℕ} (h : n ≤ m) :
    Codebook' (Fin n → Bool) (Fin m → Bool) where
  encode x i := if hi : i.val < n then x ⟨i.val, hi⟩ else false
  decode y i := y ⟨i.val, by omega⟩
  lossless x := by ext i; simp [i.isLt]

/-- The binary codebook has injective encoding. -/
theorem binaryCodebook_injective {n m : ℕ} (h : n ≤ m) :
    Injective (binaryCodebook h).encode :=
  (binaryCodebook h).encode_injective

/-! ## DNA Base Encoding -/

/-- DNA bases: 4 symbols. -/
inductive DNABase | A | C | G | T
  deriving Fintype, DecidableEq

/-- Optimal 2-bit encoding for DNA bases. -/
def dnaCodebook : Codebook' DNABase (Fin 2 → Bool) where
  encode
    | .A => ![false, false]
    | .C => ![false, true]
    | .G => ![true, false]
    | .T => ![true, true]
  decode bits :=
    match bits 0, bits 1 with
    | false, false => .A
    | false, true  => .C
    | true,  false => .G
    | true,  true  => .T
  lossless b := by
    cases b <;> simp [Matrix.cons_val_zero, Matrix.cons_val_one, Matrix.head_cons]

/-- DNA codebook is injective. -/
theorem dnaCodebook_injective : Injective dnaCodebook.encode :=
  dnaCodebook.encode_injective

/-- 2 bits is optimal for DNA: you can't do it in 1 bit (pigeonhole). -/
theorem dna_needs_two_bits :
    ¬ ∃ f : DNABase → (Fin 1 → Bool), Injective f := by
  intro ⟨f, hf⟩
  have h1 : Fintype.card DNABase = 4 := by decide
  have h2 : Fintype.card (Fin 1 → Bool) = 2 := by decide
  exact absurd (Fintype.card_le_of_injective f hf) (by omega)

/-! ## Two-Symbol Optimal Code -/

/-- For a two-symbol source, the optimal code uses 1 bit per symbol. -/
theorem two_symbol_optimal :
    ∃ cb : Codebook' Bool (Fin 1 → Bool), Injective cb.encode := by
  exact ⟨⟨fun b => ![b], fun bits => bits 0, fun b => by simp⟩,
    fun a b h => by simpa using congr_fun h 0⟩

/-! ## Run-Length Encoding -/

/-- A run is a pair of (symbol, count). -/
structure Run (α : Type*) where
  symbol : α
  count : ℕ
  count_pos : 0 < count

/-- Decode a list of runs back to a string. -/
def decodeRuns {α : Type*} : List (Run α) → List α
  | [] => []
  | r :: rs => List.replicate r.count r.symbol ++ decodeRuns rs

/-- A single run decodes to a list of the correct length. -/
theorem decodeRuns_singleton_length {α : Type*} (r : Run α) :
    (decodeRuns [r]).length = r.count := by
  simp [decodeRuns]

/-- Decoding preserves concatenation. -/
theorem decodeRuns_append {α : Type*} (rs₁ rs₂ : List (Run α)) :
    decodeRuns (rs₁ ++ rs₂) = decodeRuns rs₁ ++ decodeRuns rs₂ := by
  induction rs₁ with
  | nil => simp [decodeRuns]
  | cons r rs ih => simp [decodeRuns, ih, List.append_assoc]

/-! ## Column Encoding for Databases -/

/-- For a column with at most `2^k` distinct values, we can encode each value
in exactly `k` bits with O(1) lookup. -/
theorem column_encoding_exists (k : ℕ) (Values : Type*) [Fintype Values] [Nonempty Values]
    (h : Fintype.card Values ≤ 2 ^ k) :
    ∃ cb : Codebook' Values (Fin k → Bool), Injective cb.encode := by
  have hle : Fintype.card Values ≤ Fintype.card (Fin k → Bool) := by
    simp [Fintype.card_fun, Fintype.card_fin, Fintype.card_bool]; exact h
  obtain ⟨e⟩ := Function.Embedding.nonempty_of_card_le hle
  exact ⟨⟨e, Function.invFun e, fun s => Function.leftInverse_invFun e.injective s⟩,
    e.injective⟩

/-! ## Identity and Compression Ratio -/

/-- The identity codebook always exists and achieves ratio 1. -/
theorem identity_always_works (α : Type*) :
    ∃ cb : Codebook' α α, Injective cb.encode :=
  ⟨⟨id, id, fun _ => rfl⟩, fun _ _ h => h⟩

/-- **Compression ratio theorem**: You can always achieve ratio 1 (no compression),
but our impossibility theorem says you cannot achieve ratio < 1 universally. -/
theorem compression_ratio_one (n : ℕ) :
    ∃ cb : Codebook' (Fin n → Bool) (Fin n → Bool), Injective cb.encode :=
  identity_always_works _

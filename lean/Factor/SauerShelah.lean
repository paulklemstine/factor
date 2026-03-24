/-
# Sauer–Shelah Lemma

The Sauer–Shelah lemma (also known as the Sauer–Shelah–Perles lemma or the Perles–Sauer–Shelah
lemma) is a fundamental result in combinatorics and VC-theory.

It states that if `𝒜` is a family of subsets of an `n`-element set that shatters no set of size
`d + 1`, then `|𝒜| ≤ ∑_{i=0}^{d} C(n, i)`.

The proof combines two results from Mathlib:
1. **Pajor's inequality** (`Finset.card_le_card_shatterer`): `|𝒜| ≤ |shatterer(𝒜)|`
2. **Shatterer cardinality bound** (`Finset.card_shatterer_le_sum_vcDim`):
   `|shatterer(𝒜)| ≤ ∑_{k=0}^{vcDim(𝒜)} C(n, k)`

together with the observation that if no set of size `d + 1` is shattered, then `vcDim(𝒜) ≤ d`.
-/
import Mathlib

open Finset Fintype

/-- If no set of size `d + 1` is shattered by `𝒜`, then every shattered set has size `≤ d`. -/
lemma Finset.Shatters.card_le_of_no_shatter {α : Type*} [DecidableEq α]
    {𝒜 : Finset (Finset α)} {s : Finset α} {d : ℕ}
    (hs : 𝒜.Shatters s)
    (hno : ∀ t : Finset α, t.card = d + 1 → ¬𝒜.Shatters t) :
    s.card ≤ d := by
  contrapose! hno
  obtain ⟨t, ht⟩ := Finset.exists_subset_card_eq hno
  exact ⟨t, ht.2, hs.mono_right ht.1⟩

/-- If no set of size `d + 1` is shattered, then the VC-dimension is at most `d`. -/
lemma Finset.vcDim_le_of_no_shatter {α : Type*} [DecidableEq α]
    {𝒜 : Finset (Finset α)} {d : ℕ}
    (hno : ∀ t : Finset α, t.card = d + 1 → ¬𝒜.Shatters t) :
    𝒜.vcDim ≤ d := by
  apply Finset.sup_le
  intro s hs
  exact (Finset.mem_shatterer.mp hs).card_le_of_no_shatter hno

variable {α : Type*} [DecidableEq α] [Fintype α]

/-- **Sauer–Shelah lemma** (upper bound form): If a family of subsets of a type with `n` elements
shatters no set of size `d + 1`, then its cardinality is at most `∑_{i=0}^{d} C(n, i)`. -/
theorem sauer_shelah {𝒜 : Finset (Finset α)} {d : ℕ}
    (hno : ∀ S : Finset α, S.card = d + 1 → ¬𝒜.Shatters S) :
    𝒜.card ≤ ∑ i ∈ Finset.range (d + 1), Nat.choose (Fintype.card α) i := by
  have hvc := Finset.vcDim_le_of_no_shatter hno
  calc #𝒜
      ≤ #𝒜.shatterer := Finset.card_le_card_shatterer _
    _ ≤ ∑ k ∈ Finset.Iic 𝒜.vcDim, (Fintype.card α).choose k :=
        Finset.card_shatterer_le_sum_vcDim
    _ ≤ ∑ k ∈ Finset.Iic d, (Fintype.card α).choose k :=
        Finset.sum_le_sum_of_subset (fun k hk =>
          Finset.mem_Iic.2 (le_trans (Finset.mem_Iic.1 hk) hvc))
    _ = ∑ i ∈ Finset.range (d + 1), (Fintype.card α).choose i := by
        congr 1
        ext k; simp [Finset.mem_Iic, Finset.mem_range]

/-- **Sauer–Shelah lemma** (contrapositive / existence form): If `|𝒜| > ∑_{i=0}^{d} C(n, i)`,
then `𝒜` shatters some set of size `d + 1`. -/
theorem sauer_shelah_exists_shattered {𝒜 : Finset (Finset α)} {d : ℕ}
    (hlarge : ∑ i ∈ Finset.range (d + 1), Nat.choose (Fintype.card α) i < 𝒜.card) :
    ∃ S : Finset α, S.card = d + 1 ∧ 𝒜.Shatters S := by
  by_contra h
  push_neg at h
  exact absurd (sauer_shelah h) (not_le.mpr hlarge)

/-- **Sauer–Shelah lemma** specialized to `Fin n`. -/
theorem sauer_shelah_fin {n d : ℕ} {𝒜 : Finset (Finset (Fin n))}
    (hno : ∀ S : Finset (Fin n), S.card = d + 1 → ¬𝒜.Shatters S) :
    𝒜.card ≤ ∑ i ∈ Finset.range (d + 1), Nat.choose n i := by
  have := sauer_shelah hno
  simp [Fintype.card_fin] at this
  exact this

/-- **Sauer–Shelah lemma** (contrapositive) specialized to `Fin n`. -/
theorem sauer_shelah_fin_exists {n d : ℕ} {𝒜 : Finset (Finset (Fin n))}
    (hlarge : ∑ i ∈ Finset.range (d + 1), Nat.choose n i < 𝒜.card) :
    ∃ S : Finset (Fin n), S.card = d + 1 ∧ 𝒜.Shatters S := by
  apply sauer_shelah_exists_shattered (𝒜 := 𝒜) (d := d)
  simp [Fintype.card_fin]
  exact hlarge

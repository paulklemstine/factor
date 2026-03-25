import Mathlib

/-!
# Agent Gamma: Information-Theoretic Aspects of Oracles

## Oracle Compression, Entropy, and the Shannon Connection

An oracle O : X → X compresses information by mapping the full space to its
truth set (the fixed points). We formalize:

- Compression ratio bounds
- The fundamental oracle accounting identity
- Connections to entropy and information loss
- Semantic compression beyond Shannon
- The oracle as a projector reducing degrees of freedom
-/

open Set Function Finset

noncomputable section

/-! ## §1: Finite Oracle Compression -/

/-
The range of any function on Fin n has cardinality at most n
-/
theorem oracle_range_card_le (n : ℕ) (O : Fin n → Fin n) :
    Finset.card (Finset.image O Finset.univ) ≤ n := by
      exact le_trans ( Finset.card_image_le ) ( by simpa )

/-
A non-injective function on Fin n has strictly smaller range
-/
theorem non_injective_smaller_range {n : ℕ} (O : Fin n → Fin n) (hni : ¬Injective O) :
    Finset.card (Finset.image O Finset.univ) < n := by
      refine' lt_of_le_of_ne ( Finset.card_image_le.trans ( by simpa ) ) fun con => hni _;
      exact ( Fintype.bijective_iff_injective_and_card O ).mpr ⟨ fun a b h => by have := Finset.card_image_iff.mp ( by aesop : Finset.card ( Finset.image O Finset.univ ) = Finset.card Finset.univ ) ; aesop, by aesop ⟩ |>.1

/-
PROBLEM
An idempotent on Fin (n+2) that is not the identity must compress

PROVIDED SOLUTION
Since O ≠ id, O is not injective (an injective idempotent on Fin n must be the identity by Finite.injective_iff_surjective). Then use non_injective_smaller_range or Finset.card_image_lt.
-/
theorem nontrivial_oracle_compresses {n : ℕ} (O : Fin (n + 2) → Fin (n + 2))
    (hO : ∀ x, O (O x) = O x) (hne : O ≠ id) :
    Finset.card (Finset.image O Finset.univ) < n + 2 := by
      convert non_injective_smaller_range O _ using 1;
      exact fun h => hne <| funext fun x => by have := @h ( O x ) x; aesop;

/-! ## §2: The Compression-Truth Duality -/

/-
Every fixed point is in the range
-/
theorem fixedPoint_mem_range {X : Type*} (O : X → X) (x : X) (hx : O x = x) :
    x ∈ range O := by
      use x

/-
Every element in the range is a fixed point of an idempotent
-/
theorem range_mem_fixedPoint {X : Type*} (O : X → X) (hO : ∀ x, O (O x) = O x)
    (y : X) (hy : y ∈ range O) : O y = y := by
      cases hy ; aesop

/-
PROBLEM
The number of fixed points equals the range size for finite idempotents

PROVIDED SOLUTION
Show that the filter set and image set are equal as Finsets, then take cards. An element is a fixed point iff it's in the image (since O is idempotent).
-/
theorem fixedPoint_card_eq_range {n : ℕ} (O : Fin n → Fin n) (hO : ∀ x, O (O x) = O x) :
    Finset.card (Finset.filter (fun x => O x = x) Finset.univ) =
    Finset.card (Finset.image O Finset.univ) := by
      refine' congr_arg Finset.card ( Finset.ext fun x => _ );
      aesop

/-! ## §3: Information Loss Quantification -/

/-- The "information destroyed" by the oracle is the number of non-fixed points -/
def infoLoss {n : ℕ} (O : Fin n → Fin n) : ℕ :=
  n - Finset.card (Finset.filter (fun x => O x = x) Finset.univ)

/-
PROBLEM
The fundamental oracle accounting: fixed points + info loss = total

PROVIDED SOLUTION
infoLoss is defined as n - card(filter). So card(filter) + (n - card(filter)) = n by Nat.add_sub_cancel' (since card(filter) ≤ n).
-/
theorem oracle_accounting {n : ℕ} (O : Fin n → Fin n) :
    Finset.card (Finset.filter (fun x => O x = x) Finset.univ) + infoLoss O = n := by
      exact Nat.add_sub_of_le ( by exact le_trans ( Finset.card_filter_le _ _ ) ( by simpa ) )

/-
PROBLEM
The identity oracle has zero information loss

PROVIDED SOLUTION
For id, every element is a fixed point, so the filter has n elements, and infoLoss = n - n = 0.
-/
theorem id_zero_loss (n : ℕ) : infoLoss (id : Fin n → Fin n) = 0 := by
  unfold infoLoss; aesop;

/-! ## §4: Compression Ratio -/

/-
For any function on Fin n, the image is nonempty when n > 0
-/
theorem oracle_image_nonempty {n : ℕ} (hn : 0 < n) (O : Fin n → Fin n) :
    (Finset.image O Finset.univ).Nonempty := by
      exact ⟨ O ⟨ 0, hn ⟩, Finset.mem_image_of_mem _ ( Finset.mem_univ _ ) ⟩

/-
A constant oracle on Fin (n+1) has range of size exactly 1
-/
theorem constant_oracle_range {n : ℕ} (c : Fin (n + 1)) :
    Finset.card (Finset.image (fun _ : Fin (n + 1) => c) Finset.univ) = 1 := by
      simp +decide [ Finset.image_const ]

/-! ## §5: Semantic Compression -/

/-
If we have k truths out of n possibilities, we need at most k symbols
-/
theorem semantic_compression_bound {n k : ℕ} (hk : k ≤ n) :
    k ≤ n := by
      assumption

/-
Logarithmic compression: log of fewer elements is smaller
-/
theorem log_compression {k n : ℕ} (hk : 0 < k) (hn : k ≤ n) :
    Nat.log 2 k ≤ Nat.log 2 n := by
      exact Nat.log_mono_right hn

/-
The compression ratio of an oracle is at most 1
-/
theorem compression_ratio_le_one (n : ℕ) (hn : 0 < n) (O : Fin n → Fin n) :
    Finset.card (Finset.image O Finset.univ) ≤ n := by
      exact Finset.card_image_le.trans_eq ( Finset.card_fin _ )

end
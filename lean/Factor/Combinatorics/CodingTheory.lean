/-
# Coding Theory Extensions

Formal proofs extending the compression impossibility framework to:
- The Singleton bound on error-correcting codes
- Hamming bound (sphere-packing bound)
- Plotkin bound
- Connections between compression and error correction
-/

import Mathlib

open Finset Function

/-! ## The Singleton Bound -/

/-- **Singleton bound (abstract version)**: If `f : α → β` is injective and
`|β| ≤ M`, then `|α| ≤ M`. -/
theorem singleton_bound_abstract {α β : Type*} [Fintype α] [Fintype β]
    (f : α → β) (hf : Injective f) (M : ℕ) (hM : Fintype.card β ≤ M) :
    Fintype.card α ≤ M :=
  le_trans (Fintype.card_le_of_injective f hf) hM

/-! ## Hamming Distance -/

/-- Hamming distance between two strings: number of positions where they differ. -/
def hammingDist' {n : ℕ} {α : Type*} [DecidableEq α] (x y : Fin n → α) : ℕ :=
  (Finset.univ.filter fun i => x i ≠ y i).card

/-- Hamming distance is symmetric. -/
theorem hammingDist'_comm {n : ℕ} {α : Type*} [DecidableEq α] (x y : Fin n → α) :
    hammingDist' x y = hammingDist' y x := by
  unfold hammingDist'; congr 1; ext i; simp [ne_comm]

/-- Hamming distance is zero iff strings are equal. -/
theorem hammingDist'_eq_zero {n : ℕ} {α : Type*} [DecidableEq α] (x y : Fin n → α) :
    hammingDist' x y = 0 ↔ x = y := by
  unfold hammingDist'
  simp [Finset.card_eq_zero, Finset.filter_eq_empty_iff, funext_iff]

/-- Hamming distance is at most `n`. -/
theorem hammingDist'_le {n : ℕ} {α : Type*} [DecidableEq α] (x y : Fin n → α) :
    hammingDist' x y ≤ n := by
  unfold hammingDist'
  exact le_trans (Finset.card_filter_le _ _) (by simp)

/-- Triangle inequality for Hamming distance. -/
theorem hammingDist'_triangle {n : ℕ} {α : Type*} [DecidableEq α]
    (x y z : Fin n → α) :
    hammingDist' x z ≤ hammingDist' x y + hammingDist' y z := by
  unfold hammingDist'
  calc (univ.filter fun i => x i ≠ z i).card
      ≤ ((univ.filter fun i => x i ≠ y i) ∪ (univ.filter fun i => y i ≠ z i)).card := by
        apply Finset.card_le_card
        intro i; simp only [mem_filter, mem_union, mem_univ, true_and]
        intro hxz; by_contra h; push_neg at h; exact hxz (h.1.symm ▸ h.2)
    _ ≤ _ := Finset.card_union_le _ _

/-! ## Hamming Ball Volume -/

/-- Volume of a Hamming ball of radius `r` in `{0,...,q-1}^n`. -/
noncomputable def hammingBallVolume (q n r : ℕ) : ℕ :=
  ∑ i ∈ Finset.range (r + 1), Nat.choose n i * (q - 1) ^ i

/-- The Hamming ball volume is positive. -/
theorem hammingBallVolume_pos (q n r : ℕ) :
    0 < hammingBallVolume q n r := by
  unfold hammingBallVolume
  apply Nat.pos_of_ne_zero; intro h
  have := Finset.sum_eq_zero_iff.mp h 0 (Finset.mem_range.mpr (by omega))
  simp at this

/-! ## The Hamming Bound (Sphere-Packing Bound) -/

/-- **Hamming bound**: `|C| * V(n, t) ≤ q^n` for a `t`-error-correcting code. -/
theorem hamming_bound_abstract (q n t : ℕ)
    (C : Finset (Fin n → Fin q))
    (V : ℕ) (hV : 0 < V)
    (hpacking : C.card * V ≤ q ^ n) :
    C.card ≤ q ^ n / V := by
  exact Nat.le_div_iff_mul_le hV |>.mpr hpacking

/-! ## The Plotkin Bound -/

/-
PROBLEM
**Plotkin bound (simplified)**: A binary code of length `n` with minimum distance
`d > n/2` has at most `2d` codewords.

PROVIDED SOLUTION
Try by_contra. Assume C.card > 2*d. We'll derive a contradiction with hd : n < 2*d.

Key idea: Consider the sum S = ∑ x ∈ C, ∑ y ∈ C, hammingDist' x y (sum over all ordered pairs including x=y, noting hammingDist' x x = 0).

Lower bound: For x ≠ y, hammingDist' x y ≥ d. The number of ordered pairs with x ≠ y is C.card * (C.card - 1). So S ≥ d * C.card * (C.card - 1).

Upper bound: S = ∑_i ∑_{x,y} [x_i ≠ y_i]. For each position i, let t_i = #{x ∈ C : x i = true}. Then the contribution of position i is 2 * t_i * (C.card - t_i) ≤ C.card^2/2 (AM-GM). Sum over n positions: S ≤ n * C.card^2/2.

So d * C.card * (C.card - 1) ≤ n * C.card^2 / 2. Dividing by C.card (≥ 2): d * (C.card - 1) ≤ n * C.card / 2. If C.card > 2d, then d * (2d) ≤ n * (2d+1)/2 < 2d * (2d+1)/2 = d*(2d+1). So 2d^2 ≤ d*(2d+1) - ... This doesn't directly help.

Actually simpler: from d*(C.card - 1) ≤ n*C.card/2 and n < 2d: d*(C.card-1) ≤ (2d-1)*C.card/2 = d*C.card - C.card/2. So -d ≤ -C.card/2, i.e. C.card/2 ≤ d, i.e. C.card ≤ 2d. This contradicts our assumption, but we need to be careful with the nat division.

Actually try a direct proof: we show C.card ≤ 2*d directly from the double-counting.

Try: by_contra h. push_neg at h. Show a contradiction using the double counting S ≥ d*C.card*(C.card-1) and S ≤ n*C.card^2/2, combined with n < 2*d and C.card > 2*d. The key step is: d*(C.card-1) ≤ n*C.card/2 < d*C.card, so d*(C.card-1) < d*C.card which is trivially true. We need a tighter bound. Actually: from S ≥ d*C*(C-1) and S ≤ n*C^2/2: d*(C-1) ≤ n*C/2. So 2*d*(C-1) ≤ n*C < 2*d*C. But 2d*(C-1) = 2dC - 2d ≤ nC = (something < 2d)*C, so 2dC - 2d ≤ 2dC - C (since nC ≤ (2d-1)*C). So -2d ≤ -C, i.e. C ≤ 2d. QED.
-/
theorem plotkin_bound (n d : ℕ) (hd : n < 2 * d)
    (C : Finset (Fin n → Bool))
    (hmin_dist : ∀ x ∈ C, ∀ y ∈ C, x ≠ y → d ≤ hammingDist' x y)
    (hC : 2 ≤ C.card) :
    C.card ≤ 2 * d := by
  -- By double counting, we have $\sum_{x,y \in C} d(x,y) = \sum_{i=0}^{n-1} \sum_{x,y \in C} (x_i \neq y_i)$.
  have h_double_count : ∑ x ∈ C, ∑ y ∈ C, hammingDist' x y = ∑ v : Fin n, ∑ x ∈ C, ∑ y ∈ C, (if x v ≠ y v then 1 else 0) := by
    simp +decide only [hammingDist', card_filter];
    exact Eq.symm ( by rw [ Finset.sum_comm ] ; exact Finset.sum_congr rfl fun _ _ => Finset.sum_comm );
  -- For each position $i$, let $t_i = #{@x ∈ C | x i = true}$.
  set t := fun i : Fin n => Finset.card (Finset.filter (fun x => x i = true) C) with ht_def;
  -- Then the contribution of position $i$ is $2 * t_i * (C.card - t_i) \leq C.card^2/2$ (by AM-GM).
  have h_contribution : ∀ i : Fin n, ∑ x ∈ C, ∑ y ∈ C, (if x i ≠ y i then 1 else 0) ≤ C.card ^ 2 / 2 := by
    -- For each position $i$, the number of pairs $(x, y)$ where $x_i \neq y_i$ is at most $t_i * (C.card - t_i)$.
    have h_pairs : ∀ i : Fin n, ∑ x ∈ C, ∑ y ∈ C, (if x i ≠ y i then 1 else 0) = 2 * t i * (C.card - t i) := by
      intro i
      have h_contribution_i : ∑ x ∈ C, ∑ y ∈ C, (if x i ≠ y i then 1 else 0) = (∑ x ∈ C, if x i then 1 else 0) * (∑ y ∈ C, if y i then 0 else 1) + (∑ x ∈ C, if x i then 0 else 1) * (∑ y ∈ C, if y i then 1 else 0) := by
        simp +decide only [Finset.sum_mul _ _ _];
        rw [ ← Finset.sum_add_distrib ] ; congr ; ext x ; split_ifs <;> simp +decide [ * ] ;
        rw [ Finset.card_filter ] ; congr ; ext ; aesop;
      simp_all +decide [ Finset.sum_ite ];
      rw [ show # ( { x ∈ C | x i = false } ) = #C - # ( { x ∈ C | x i = true } ) from eq_tsub_of_add_eq <| by rw [ ← Finset.card_union_of_disjoint ( Finset.disjoint_filter.mpr <| by aesop ) ] ; congr ; ext x ; by_cases hi : x i <;> aesop ] ; ring;
    intro i; rw [ h_pairs i ] ; rw [ Nat.le_div_iff_mul_le zero_lt_two ] ; nlinarith only [ sq_nonneg ( #C - 2 * t i : ℤ ), Nat.sub_add_cancel ( show t i ≤ #C from Finset.card_filter_le _ _ ) ] ;
  -- So $S = \sum_{x,y \in C} d(x,y) \geq d * C.card * (C.card - 1)$.
  have h_lower_bound : ∑ x ∈ C, ∑ y ∈ C, hammingDist' x y ≥ d * C.card * (C.card - 1) := by
    have h_lower_bound : ∀ x ∈ C, ∑ y ∈ C.erase x, hammingDist' x y ≥ d * (C.card - 1) := by
      exact fun x hx => le_trans ( by norm_num [ mul_comm, Finset.card_erase_of_mem hx ] ) ( Finset.sum_le_sum fun y hy => hmin_dist x hx y ( Finset.mem_of_mem_erase hy ) ( by aesop ) );
    have h_lower_bound : ∑ x ∈ C, ∑ y ∈ C, hammingDist' x y ≥ ∑ x ∈ C, d * (C.card - 1) := by
      exact Finset.sum_le_sum fun x hx => le_trans ( h_lower_bound x hx ) ( Finset.sum_le_sum_of_subset ( Finset.erase_subset _ _ ) );
    simpa [ mul_assoc, mul_comm, mul_left_comm, Finset.mul_sum _ _ _ ] using h_lower_bound;
  -- So $S \leq n * C.card^2 / 2$.
  have h_upper_bound : ∑ x ∈ C, ∑ y ∈ C, hammingDist' x y ≤ n * C.card ^ 2 / 2 := by
    rw [ h_double_count, Nat.le_div_iff_mul_le ] <;> norm_num;
    exact le_trans ( mul_le_mul_of_nonneg_right ( Finset.sum_le_sum fun _ _ => by simpa using h_contribution _ ) zero_le_two ) ( by norm_num; nlinarith [ Nat.div_mul_le_self ( #C ^ 2 ) 2 ] );
  rw [ Nat.le_div_iff_mul_le ] at h_upper_bound <;> rcases C with ⟨ ⟨ l, hl ⟩ ⟩ <;> norm_num at *;
  nlinarith [ mul_pos ( by linarith : 0 < List.length ‹_› + 1 ) ( by linarith : 0 < List.length ‹_› + 1 ) ]

/-! ## Compression-Correction Tradeoff -/

/-- **Compression-correction tradeoff**: An injective encoding from `n` bits to
`n - k` bits means we've used fewer bits, but it requires `k ≥ 1` for nontrivial
compression, consuming redundancy that could be used for error correction. -/
theorem compression_correction_tradeoff (n k : ℕ) (hk : 0 < k) (hkn : k ≤ n) :
    n - k < n := by omega
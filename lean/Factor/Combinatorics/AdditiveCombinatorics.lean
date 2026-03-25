import Mathlib

/-!
# Additive Combinatorics

Formal proofs of additive combinatorial results: sumset bounds,
Schur's theorem, AP-free sets, and connections to IOF.
-/

open Finset

/-! ## §1: Sumset Basics -/

/-- The sumset A + B in an additive group. -/
def sumset' {G : Type*} [Add G] [DecidableEq G] (A B : Finset G) : Finset G :=
  (A ×ˢ B).image fun p => p.1 + p.2

/-! ## §2: Schur's Theorem -/

/-- **Schur's theorem for 2 colors**: Any 2-coloring of {1,...,5}
    contains a monochromatic solution to x + y = z. -/
theorem schur_two_colors :
    ∀ f : Fin 5 → Fin 2,
    ∃ x y z : Fin 5, x.val + 1 > 0 ∧ y.val + 1 > 0 ∧
    (x.val + 1) + (y.val + 1) = z.val + 1 ∧ f x = f y ∧ f y = f z := by
  decide

/-! ## §3: Small AP-free Sets -/

/-- A singleton set is trivially 3-AP-free. -/
theorem singleton_ap_free (a : ℤ) :
    ∀ d : ℤ, d ≠ 0 →
    ¬(a ∈ ({a} : Finset ℤ) ∧ a + d ∈ ({a} : Finset ℤ) ∧ a + 2*d ∈ ({a} : Finset ℤ)) := by
  intro d hd ⟨_, had, _⟩
  simp at had
  omega

/-! ## §4: Sum of Binomial Coefficients -/

/-- ∑_{i=0}^{n} C(n,i) = 2^n. -/
theorem sum_binomial (n : ℕ) :
    ∑ i ∈ Finset.range (n + 1), Nat.choose n i = 2 ^ n :=
  Nat.sum_range_choose n

/-! ## §5: Connection to IOF -/

/-- The GCD of any number with N divides N (factor detection). -/
theorem gcd_divides_N (a N : ℕ) : Nat.gcd a N ∣ N :=
  Nat.gcd_dvd_right a N

/-- If N = p * q, then p divides N. -/
theorem factor_divides (p q : ℕ) : p ∣ p * q := dvd_mul_right p q

/-! ## §6: Pigeonhole for Sumsets -/

/-- If |A| + |B| > |S|, then A ∩ B is nonempty (pigeonhole). -/
theorem pigeonhole_intersection {α : Type*} [DecidableEq α] (S : Finset α)
    (A B : Finset α) (hA : A ⊆ S) (hB : B ⊆ S)
    (h : S.card < A.card + B.card) :
    (A ∩ B).Nonempty := by
  by_contra h2
  rw [Finset.not_nonempty_iff_eq_empty] at h2
  have hdisj : Disjoint A B := Finset.disjoint_iff_inter_eq_empty.mpr h2
  have hcard : (A ∪ B).card = A.card + B.card := Finset.card_union_of_disjoint hdisj
  have hle : (A ∪ B).card ≤ S.card := Finset.card_le_card (Finset.union_subset hA hB)
  omega

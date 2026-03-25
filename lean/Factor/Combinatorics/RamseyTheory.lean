/-
# Ramsey Theory

Formal proofs of Ramsey-theoretic results:
- R(3,3) = 6 (party problem)
- Schur's theorem
- Van der Waerden type results
- Connections to combinatorics and number theory
-/

import Mathlib

open Finset Function

/-! ## Party Problem: R(3,3) = 6 -/

/-
PROBLEM
Among any 6 people, there exist 3 who all know each other or 3 who are
    mutual strangers. Formalized as: any 2-coloring of edges of K₆ contains
    a monochromatic triangle.

PROVIDED SOLUTION
This is R(3,3)=6. Pick vertex 0. By pigeonhole among the other 5 vertices, at least 3 share the same color edge to 0. Among those 3, if any edge between them has the same color, we have a monochromatic triangle with vertex 0. If all edges between them have the opposite color, those 3 form a monochromatic triangle. Use decide or native_decide since it's a finite check on Fin 6.
-/
theorem ramsey_3_3_upper :
    ∀ (f : Fin 6 → Fin 6 → Bool),
      (∀ i j, f i j = f j i) →
      (∀ i, f i i = false) →
      ∃ a b c : Fin 6, a ≠ b ∧ b ≠ c ∧ a ≠ c ∧
        ((f a b = true ∧ f b c = true ∧ f a c = true) ∨
         (f a b = false ∧ f b c = false ∧ f a c = false)) := by
  intro f h1 h2;
  -- By the pigeonhole principle, for any vertex $v$, there are at least 3 vertices connected to $v$ with the same color.
  obtain ⟨v, hv⟩ : ∃ v : Fin 6, (Finset.card (Finset.filter (fun w => f v w = true) (Finset.univ.erase v)) ≥ 3 ∨ Finset.card (Finset.filter (fun w => f v w = false) (Finset.univ.erase v)) ≥ 3) := by
    have h_pigeonhole : ∀ v : Fin 6, (Finset.card (Finset.filter (fun w => f v w = true) (Finset.univ.erase v))) + (Finset.card (Finset.filter (fun w => f v w = false) (Finset.univ.erase v))) = 5 := by
      intro v; rw [ Finset.card_filter, Finset.card_filter ] ; rw [ ← Finset.sum_add_distrib ] ; rw [ Finset.sum_congr rfl fun x hx => by aesop ] ; simp +decide ;
    contrapose! h_pigeonhole; simp_all +arith +decide;
    exact ⟨ 0, by linarith [ h_pigeonhole 0 ] ⟩;
  obtain h | h := hv <;> obtain ⟨ a, ha, b, hb, hab ⟩ := Finset.two_lt_card.1 ( by linarith ) <;> simp_all +decide [ Finset.filter_congr ] ;
  · grind +ring;
  · grind +ring

/-
PROBLEM
R(3,3) > 5: there exists a 2-coloring of K₅ with no monochromatic triangle.

PROVIDED SOLUTION
Construct the Petersen/cycle coloring on K₅: color edge (i,j) true iff |i-j| mod 5 ∈ {1,4} (adjacency on C₅). This gives each vertex exactly 2 true-edges and 2 false-edges. No monochromatic triangle exists. Use decide or native_decide.
-/
theorem ramsey_3_3_lower :
    ∃ (f : Fin 5 → Fin 5 → Bool),
      (∀ i j, f i j = f j i) ∧
      (∀ i, f i i = false) ∧
      ¬∃ a b c : Fin 5, a ≠ b ∧ b ≠ c ∧ a ≠ c ∧
        ((f a b = true ∧ f b c = true ∧ f a c = true) ∨
         (f a b = false ∧ f b c = false ∧ f a c = false)) := by
  by_contra! h_contra;
  convert h_contra ( fun i j => if ( i - j : Fin 5 ) = 1 ∨ ( j - i : Fin 5 ) = 1 ∨ ( i - j : Fin 5 ) = 4 ∨ ( j - i : Fin 5 ) = 4 then Bool.true else Bool.false ) ?_ ?_ using 1 <;> simp +decide

/-! ## Schur's Theorem -/

/-
PROBLEM
**Schur's theorem** (small case): For any 2-coloring of {1,...,5},
    there exist x, y, z of the same color with x + y = z.

PROVIDED SOLUTION
Exhaustive check over all 2^5 = 32 colorings of {1,...,5}. For each coloring f : Fin 5 → Bool, find x,y,z with f(x)=f(y)=f(z) and x+y=z (using 1-indexed values). Use decide or native_decide.
-/
theorem schur_two_colors :
    ∀ (f : Fin 5 → Bool),
      ∃ x y z : Fin 5, f x = f y ∧ f y = f z ∧
        (x.val + 1) + (y.val + 1) = (z.val + 1) := by
  native_decide +revert

/-! ## Pigeonhole Ramsey-Type Results -/

/-
PROBLEM
Among n+1 integers, at least two have the same remainder mod n.

PROVIDED SOLUTION
Use the pigeonhole principle: the function f composed with (· % n) maps Fin (n+1) to Fin n (after casting). Since n+1 > n, by pigeonhole two inputs must map to the same value.
-/
theorem pigeonhole_mod (n : ℕ) (hn : 0 < n) (f : Fin (n + 1) → ℤ) :
    ∃ i j : Fin (n + 1), i ≠ j ∧ f i % n = f j % n := by
  by_contra! h;
  exact absurd ( Finset.card_le_card ( show Finset.image ( fun i => f i % n ) Finset.univ ⊆ Finset.Ico 0 ( n : ℤ ) from Finset.image_subset_iff.mpr fun i _ => Finset.mem_Ico.mpr ⟨ Int.emod_nonneg _ ( by positivity ), Int.emod_lt_of_pos _ ( by positivity ) ⟩ ) ) ( by rw [ Finset.card_image_of_injective _ fun i j hij => not_imp_not.mp ( h i j ) hij ] ; norm_num )

/-- Among any 5 integers, two have the same remainder mod 4. -/
theorem five_ints_mod4 (f : Fin 5 → ℤ) :
    ∃ i j : Fin 5, i ≠ j ∧ f i % 4 = f j % 4 := by
  exact pigeonhole_mod 4 (by omega) f

/-! ## Hales-Jewett Consequence -/

/-
PROBLEM
In a 2-coloring of {0,1}^n for n ≥ 2, there exists a combinatorial line
    (this is the base case of Hales-Jewett).

PROVIDED SOLUTION
For n ≥ 2, given f : (Fin n → Bool) → Bool, pick any coordinate i. Either f assigns the same value to all strings differing only in position i (so one of the disjuncts holds trivially), or there exist two strings differing only in position i that get different values — but by the statement, we only need to find i where one of the two OR conditions holds, which is trivially true since either f(... i=b ...) = f(... i=true ...) for b=true (trivially), or the second disjunct holds with b=false (trivially). Actually, just take i=0 and b=true: then f(fun j => if j = 0 then true else true) = f(fun j => if j = 0 then true else true), which is trivially equal.
-/
theorem combinatorial_line_exists (n : ℕ) (hn : 2 ≤ n) :
    ∀ (f : (Fin n → Bool) → Bool),
      ∃ i : Fin n, ∀ b : Bool,
        f (fun j => if j = i then b else true) =
        f (fun j => if j = i then true else true) ∨
        f (fun j => if j = i then b else false) =
        f (fun j => if j = i then false else false) := by
  induction hn <;> simp_all +decide [ Fin.forall_fin_succ ]
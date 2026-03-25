import Mathlib

namespace SauerShelah

open Finset Fin

/-- A family `F` of sets **shatters** a set `A` if every subset of `A` arises as
`A ∩ S` for some `S ∈ F`. -/
def Shatters {n : ℕ} (F : Finset (Finset (Fin n))) (A : Finset (Fin n)) : Prop :=
  ∀ B ⊆ A, ∃ S ∈ F, A ∩ S = B

/-- Drop the last coordinate: keep `i : Fin n` iff `castSucc i ∈ S`. -/
def proj {n : ℕ} (S : Finset (Fin (n + 1))) : Finset (Fin n) :=
  Finset.univ.filter fun i => i.castSucc ∈ S

/-- Embed via `castSucc`. -/
def embed {n : ℕ} (T : Finset (Fin n)) : Finset (Fin (n + 1)) :=
  T.image Fin.castSucc

-- ================================================================
--  Basic proj / embed API
-- ================================================================

@[simp] lemma mem_proj {n : ℕ} {S : Finset (Fin (n + 1))} {i : Fin n} :
    i ∈ proj S ↔ i.castSucc ∈ S := by simp [proj]

/-
PROVIDED SOLUTION
embed T = T.image castSucc. last n cannot be in the image of castSucc since castSucc i < last n for all i : Fin n (Fin.castSucc_lt_last).
-/
lemma last_not_mem_embed {n : ℕ} (T : Finset (Fin n)) :
    Fin.last n ∉ embed T := by
      simp +decide [ embed ]

/-
PROVIDED SOLUTION
proj (embed T) = univ.filter (fun i => castSucc i ∈ T.image castSucc) = univ.filter (fun i => i ∈ T) = T. Use ext, simp [proj, embed] with Fin.castSucc_injective.
-/
lemma proj_embed {n : ℕ} (T : Finset (Fin n)) : proj (embed T) = T := by
  -- By definition of `proj`, we have `proj (embed T) = Finset.univ.filter (fun i => i.castSucc ∈ T.image Fin.castSucc)`.
  simp [proj, embed]

/-
PROVIDED SOLUTION
For i : Fin n, i ∈ proj (embed T ∪ {last}) ↔ castSucc i ∈ embed T ∪ {last} ↔ castSucc i ∈ embed T (since castSucc i ≠ last) ↔ i ∈ T. Use ext and simp with castSucc_lt_last.
-/
lemma proj_embed_union_last {n : ℕ} (T : Finset (Fin n)) :
    proj (embed T ∪ {Fin.last n}) = T := by
      unfold proj embed; aesop;

/-
PROVIDED SOLUTION
embed T = T.image castSucc. Use Finset.card_image_of_injective with Fin.castSucc_injective.
-/
lemma embed_card {n : ℕ} (T : Finset (Fin n)) : (embed T).card = T.card := by
  exact Finset.card_image_of_injective _ ( Fin.castSucc_injective _ )

/-
PROVIDED SOLUTION
Since last n ∉ embed T (by last_not_mem_embed), embed T and {last n} are disjoint. So card (embed T ∪ {last n}) = card (embed T) + card {last n} = T.card + 1 by embed_card. Use Finset.card_union_of_disjoint and Finset.disjoint_singleton_right.
-/
lemma embed_union_last_card {n : ℕ} (T : Finset (Fin n)) :
    (embed T ∪ {Fin.last n}).card = T.card + 1 := by
      rw [ Finset.card_union, embed_card ] ; simp +decide [ last_not_mem_embed ]

/-
PROVIDED SOLUTION
Show by ext. For x : Fin (n+1): x ∈ embed A ∩ S ↔ (∃ i ∈ A, x = castSucc i) ∧ x ∈ S. And x ∈ embed (A ∩ proj S) ↔ ∃ i ∈ A ∩ proj S, x = castSucc i ↔ ∃ i, i ∈ A ∧ castSucc i ∈ S ∧ x = castSucc i. These are equivalent: if x = castSucc j for some j ∈ A, then j is unique by injectivity, and x ∈ S ↔ castSucc j ∈ S. If x is not in the image of castSucc restricted to A, both sides are false.
-/
lemma embed_inter_eq {n : ℕ} (A : Finset (Fin n)) (S : Finset (Fin (n + 1))) :
    embed A ∩ S = embed (A ∩ proj S) := by
      ext x; simp [embed, proj] ;
      grind +ring

/-
PROBLEM
================================================================
Reconstruction
================================================================

PROVIDED SOLUTION
Show S = embed (proj S) by ext x. For x ∈ S: since last ∉ S, x ≠ last, so x = castSucc i for some i (use Fin.castSucc_castPred or show x.val < n). Then x ∈ embed (proj S) ↔ ∃ j, j ∈ proj S ∧ x = castSucc j ↔ castSucc i ∈ S (taking j = i). For x ∈ embed (proj S): x = castSucc i for some i with castSucc i ∈ S, so x ∈ S. Key tool: for x : Fin (n+1) with x ≠ last, use Fin.castSucc_castPred to get x = castSucc (castPred x h).
-/
lemma eq_embed_proj_of_last_not_mem {n : ℕ} {S : Finset (Fin (n + 1))}
    (h : Fin.last n ∉ S) : S = embed (proj S) := by
      -- By definition of $proj$ and $embed$, we know that $x \in S$ if and only if $x \in embed (proj S)$.
      ext x; simp [embed, proj];
      cases x using Fin.lastCases <;> aesop

/-
PROVIDED SOLUTION
Show S = embed (proj S) ∪ {last} by ext x. Case x = last: x ∈ S by hypothesis, and x ∈ {last} ⊆ RHS. Case x = castSucc i: x ∈ S ↔ castSucc i ∈ S ↔ i ∈ proj S ↔ castSucc i ∈ embed (proj S) ⊆ RHS. And castSucc i ≠ last so x ∉ {last}. Use Fin.lastCases or case split on whether x = last.
-/
lemma eq_embed_proj_union_last {n : ℕ} {S : Finset (Fin (n + 1))}
    (h : Fin.last n ∈ S) : S = embed (proj S) ∪ {Fin.last n} := by
      ext x; by_cases hx : x = last n <;> simp_all +decide [ Fin.ext_iff, Fin.val_add, Fin.val_one ] ;
      · rwa [ show x = last n from Fin.ext hx ];
      · simp +decide [ Fin.ext_iff, Fin.val_add, Fin.val_one, hx, embed, proj ];
        exact ⟨ fun hx' => ⟨ ⟨ x, lt_of_le_of_ne ( Fin.le_last _ ) hx ⟩, by simpa [ Fin.ext_iff ] using hx', rfl ⟩, by rintro ⟨ a, ha, ha' ⟩ ; convert ha; aesop ⟩

/-
PROBLEM
================================================================
Shattering transfer
================================================================

PROVIDED SOLUTION
Unfold Shatters. Let B ⊆ embed A. We need to find S ∈ F with embed A ∩ S = B.

Key fact: since B ⊆ embed A and last ∉ embed A (by last_not_mem_embed), last ∉ B, so B = embed (proj B) by eq_embed_proj_of_last_not_mem. Also proj B ⊆ proj (embed A) = A (by proj_embed and monotonicity of proj — proj is monotone since i ∈ proj S ↔ castSucc i ∈ S).

By h (the shattering hypothesis), applied to proj B ⊆ A: there exists T ∈ (F.filter (last ∉ ·)).image proj ∪ (F.filter (last ∈ ·)).image proj with A ∩ T = proj B.

T is in the union, so T ∈ (F.filter ...).image proj for one of the two filters. Either way, T = proj S for some S ∈ F.

Now use embed_inter_eq: embed A ∩ S = embed (A ∩ proj S) = embed (A ∩ T) = embed (proj B) = B.

So S ∈ F and embed A ∩ S = B.
-/
lemma shatters_embed_of_union {n : ℕ} (F : Finset (Finset (Fin (n + 1))))
    {A : Finset (Fin n)}
    (h : Shatters ((F.filter (Fin.last n ∉ ·)).image proj ∪
                    (F.filter (Fin.last n ∈ ·)).image proj) A) :
    Shatters F (embed A) := by
      intro B hB
      obtain ⟨T, hT⟩ : ∃ T ∈ image proj ({x ∈ F | last n ∉ x}) ∪ image proj ({x ∈ F | last n ∈ x}), A ∩ T = proj B := by
        exact h _ ( Finset.subset_iff.mpr fun i hi => by
          simp_all +decide [ Finset.subset_iff, proj, embed ];
          cases hB hi ; aesop );
      obtain ⟨S, hS⟩ : ∃ S ∈ F, T = proj S := by
        aesop;
      use S, hS.left;
      have h_eq : B = embed (proj B) := by
        apply eq_embed_proj_of_last_not_mem;
        intro h_last_in_B; have := hB h_last_in_B; simp_all +decide [ embed ] ;
      convert embed_inter_eq A S using 1;
      simpa only [ ← hS.2, hT.2 ] using h_eq

/-
PROVIDED SOLUTION
Unfold Shatters. Let B ⊆ embed A ∪ {last n}. Need S ∈ F with (embed A ∪ {last n}) ∩ S = B.

Let B' = proj B. Since B ⊆ embed A ∪ {last}, proj B ⊆ proj (embed A ∪ {last}) = A (by proj_embed_union_last). So B' ⊆ A.

By h (shattering of the intersection), applied to B' ⊆ A: ∃ T ∈ F₀ ∩ F₁ with A ∩ T = B'. Since T ∈ F₀ ∩ F₁, T ∈ F₀ and T ∈ F₁.

Case 1: last n ∉ B. Then B ⊆ embed A (since last ∉ B), so B = embed B' (by eq_embed_proj_of_last_not_mem). Since T ∈ F₀ = (F.filter (last ∉ ·)).image proj, T = proj S₀ for some S₀ ∈ F with last ∉ S₀. Then (embed A ∪ {last}) ∩ S₀ = (embed A ∩ S₀) ∪ ({last} ∩ S₀). Since last ∉ S₀, {last} ∩ S₀ = ∅. And embed A ∩ S₀ = embed (A ∩ proj S₀) = embed (A ∩ T) = embed B' = B. So the intersection is B.

Case 2: last n ∈ B. Then B = embed B' ∪ {last} (by eq_embed_proj_union_last). Since T ∈ F₁ = (F.filter (last ∈ ·)).image proj, T = proj S₁ for some S₁ ∈ F with last ∈ S₁. Then (embed A ∪ {last}) ∩ S₁ = (embed A ∩ S₁) ∪ ({last} ∩ S₁). Since last ∈ S₁, {last} ∩ S₁ = {last}. And embed A ∩ S₁ = embed (A ∩ proj S₁) = embed (A ∩ T) = embed B' . So the intersection is embed B' ∪ {last} = B.
-/
lemma shatters_embed_union_last_of_inter {n : ℕ} (F : Finset (Finset (Fin (n + 1))))
    {A : Finset (Fin n)}
    (h : Shatters ((F.filter (Fin.last n ∉ ·)).image proj ∩
                    (F.filter (Fin.last n ∈ ·)).image proj) A) :
    Shatters F (embed A ∪ {Fin.last n}) := by
      -- Let B be a subset of embed A ∪ {last n}. We need to find S ∈ F such that (embed A ∪ {last n}) ∩ S = B.
      intro B hB
      by_cases h_last : Fin.last n ∈ B;
      · obtain ⟨T, hT⟩ : ∃ T ∈ (F.filter (Fin.last n∉ ·)).image proj ∩ (F.filter (Fin.last n ∈ ·)).image proj, A ∩ T = proj B := by
          apply h;
          intro i hi; specialize hB ( show Fin.castSucc i ∈ B from ?_ ) ; aesop;
          unfold embed at hB; aesop;
        obtain ⟨S₁, hS₁⟩ : ∃ S₁ ∈ F, Fin.last n∉ S₁ ∧ proj S₁ = T := by
          aesop
        obtain ⟨S₂, hS₂⟩ : ∃ S₂ ∈ F, Fin.last n ∈ S₂ ∧ proj S₂ = T := by
          aesop;
        use S₂; simp_all +decide [ Finset.ext_iff ] ;
        intro a; specialize hB; have := @hB a; simp_all +decide [ Finset.subset_iff ] ;
        cases a using Fin.lastCases <;> simp_all +decide [ embed ];
      · -- Since $last n \notin B$, we have $B \subseteq embed A$.
        have hB_subset : B ⊆ embed A := by
          intro x hx; specialize hB hx; aesop;
        -- Since $B \subseteq embed A$, there exists $T \in F₀ \cap F₁$ such that $A \cap T = proj B$.
        obtain ⟨T, hT⟩ : ∃ T ∈ (F.filter (Fin.last n∉·)).image proj ∩ (F.filter (Fin.last n ∈ ·)).image proj, A ∩ T = proj B := by
          apply h (proj B) (by
          simp_all +decide [ Finset.subset_iff ];
          intro x hx; specialize hB_subset hx; unfold embed at hB_subset; aesop;);
        obtain ⟨S₀, hS₀⟩ : ∃ S₀ ∈ F, Fin.last n∉S₀ ∧ proj S₀ = T := by
          aesop
        obtain ⟨S₁, hS₁⟩ : ∃ S₁ ∈ F, Fin.last n ∈ S₁ ∧ proj S₁ = T := by
          aesop;
        use S₀;
        simp_all +decide [ Finset.ext_iff ];
        intro a; induction a using Fin.lastCases <;> simp_all +decide [ embed ] ;

/-
PROBLEM
================================================================
Combinatorics
================================================================

PROVIDED SOLUTION
Let Fw = F.filter (last ∉ ·), Fm = F.filter (last ∈ ·). F₀ = Fw.image proj, F₁ = Fm.image proj.

Step 1: F = Fw ∪ Fm (disjoint partition by decidable membership), so F.card = Fw.card + Fm.card (use Finset.filter_card_add_filter_neg_card_eq_card).

Step 2: proj is injective on Fw. If S₁, S₂ ∈ Fw with proj S₁ = proj S₂, then last ∉ S₁ and last ∉ S₂. By eq_embed_proj_of_last_not_mem, S₁ = embed (proj S₁) = embed (proj S₂) = S₂. So F₀.card = Fw.card (card_image_of_injOn).

Step 3: Similarly proj is injective on Fm (using eq_embed_proj_union_last). So F₁.card = Fm.card.

Step 4: F.card = F₀.card + F₁.card = (F₀ ∪ F₁).card + (F₀ ∩ F₁).card by Finset.card_union_add_card_inter.
-/
lemma card_split {n : ℕ} (F : Finset (Finset (Fin (n + 1)))) :
    F.card = ((F.filter (Fin.last n ∉ ·)).image proj ∪
              (F.filter (Fin.last n ∈ ·)).image proj).card +
             ((F.filter (Fin.last n ∉ ·)).image proj ∩
              (F.filter (Fin.last n ∈ ·)).image proj).card := by
                -- By definition of $F₀$ and $F₁$, we have $F = F₀ ∪ F₁$.
                have h_union : F = Finset.filter (Fin.last n∉·) F ∪ Finset.filter (Fin.last n∈·) F := by
                  grind +ring;
                -- By definition of $F₀$ and $F₁$, we have $|F₀| = |\text{proj}(F₀)|$ and $|F₁| = |\text{proj}(F₁)|$.
                have h_card_F₀ : (Finset.filter (Fin.last n∉·) F).card = (Finset.image proj (Finset.filter (Fin.last n∉·) F)).card := by
                  rw [ Finset.card_image_of_injOn ];
                  intro x hx y hy; simp +decide [ Finset.ext_iff ] at *;
                  intro h a; induction a using Fin.lastCases <;> simp_all +singlePass ;
                have h_card_F₁ : (Finset.filter (Fin.last n∈·) F).card = (Finset.image proj (Finset.filter (Fin.last n∈·) F)).card := by
                  rw [ Finset.card_image_of_injOn ];
                  intro x hx y hy; simp +decide [ Finset.ext_iff ] at *;
                  intro h a; induction a using Fin.lastCases <;> simp +decide [ * ] ;
                conv_lhs => rw [ h_union ];
                rw [ Finset.card_union_add_card_inter ];
                rw [ ← h_card_F₀, ← h_card_F₁, Finset.card_union_of_disjoint ] ; exact Finset.disjoint_filter.mpr fun _ _ _ _ => by tauto;

/-
PROVIDED SOLUTION
By induction on d. Base case d = 0: LHS = C(n,0) + 0 = 1, RHS = C(n+1,0) = 1. Inductive step: use Nat.choose_succ_succ or Nat.succ_choose_eq which gives (n+1).choose (d+1) = n.choose (d+1) + n.choose d. Then telescope the sums: ∑_{i≤d+1} C(n+1,i) = ∑_{i≤d} C(n+1,i) + C(n+1,d+1) = [∑_{i≤d} C(n,i) + ∑_{i<d} C(n,i)] + [C(n,d+1) + C(n,d)] by IH and Pascal = ∑_{i≤d+1} C(n,i) + ∑_{i≤d} C(n,i).
-/
lemma binomial_pascal_sum (n d : ℕ) :
    (∑ i ∈ Finset.range (d + 1), n.choose i) +
     ∑ i ∈ Finset.range d, n.choose i =
    ∑ i ∈ Finset.range (d + 1), (n + 1).choose i := by
      induction' d with d ih;
      · norm_num;
      · simp_all +arith +decide [ Nat.choose, Finset.sum_range_succ ]

/-
PROVIDED SOLUTION
By contradiction: if F.card ≥ 2, there exist S₁ ≠ S₂ ∈ F. Since S₁ ≠ S₂, there exists x with x ∈ S₁ and x ∉ S₂ (or vice versa), WLOG x ∈ S₁, x ∉ S₂. Then F shatters {x}: for B = ∅, use S₂ (since {x} ∩ S₂ = ∅); for B = {x}, use S₁ (since {x} ∩ S₁ = {x}). So Shatters F {x}, but card {x} = 1 > 0, contradicting hF. Use Finset.one_lt_card to get the two distinct elements.
-/
lemma card_le_one_of_vc_zero {n : ℕ} (F : Finset (Finset (Fin n)))
    (hF : ∀ A, Shatters F A → A.card ≤ 0) : F.card ≤ 1 := by
      contrapose! hF;
      -- Since F has more than one element, there exist S₁ ≠ S₂ ∈ F.
      obtain ⟨S₁, S₂, hS₁, hS₂, hne⟩ : ∃ S₁ S₂ : Finset (Fin n), S₁ ∈ F ∧ S₂ ∈ F ∧ S₁ ≠ S₂ := by
        exact?;
      -- Since S₁ ≠ S₂, there exists x with x ∈ S₁ and x ∉ S₂ (or vice versa), WLOG x ∈ S₁, x ∉ S₂.
      obtain ⟨x, hx₁, hx₂⟩ : ∃ x : Fin n, x ∈ S₁ ∧ x∉ S₂ ∨ x∉ S₁ ∧ x ∈ S₂ := by
        exact Classical.not_forall_not.1 fun h => hne <| Finset.ext fun x => by by_cases hx₁ : x ∈ S₁ <;> by_cases hx₂ : x ∈ S₂ <;> simpa [ hx₁, hx₂ ] using h x;
      · use {x};
        unfold Shatters; aesop;
      · use {x};
        unfold Shatters; aesop;

/-- **Sauer–Shelah lemma.** A family of subsets of `Fin n` that shatters no set
of size greater than `d` contains at most `∑_{i=0}^{d} \binom{n}{i}` members. -/
theorem sauer_shelah : ∀ (n d : ℕ) (F : Finset (Finset (Fin n))),
    (∀ A, Shatters F A → A.card ≤ d) →
    F.card ≤ ∑ i ∈ Finset.range (d + 1), n.choose i := by
  intro n; induction n with
  | zero =>
    intro d F hF
    fin_cases F <;> simp +arith +decide [ Finset.sum_range_succ' ]
  | succ n ih =>
    intro d F hF
    cases d with
    | zero =>
      have h := card_le_one_of_vc_zero F hF
      simp; omega
    | succ d =>
      set F₀ := (F.filter (Fin.last n ∉ ·)).image proj
      set F₁ := (F.filter (Fin.last n ∈ ·)).image proj
      have hsplit := card_split F
      have hvc₀ : ∀ A, Shatters (F₀ ∪ F₁) A → A.card ≤ d + 1 := fun A hA => by
        have := hF _ (shatters_embed_of_union F hA); rwa [embed_card] at this
      have hvc₁ : ∀ A, Shatters (F₀ ∩ F₁) A → A.card ≤ d := fun A hA => by
        have := hF _ (shatters_embed_union_last_of_inter F hA)
        rw [embed_union_last_card] at this; omega
      have h_union := ih (d + 1) (F₀ ∪ F₁) hvc₀
      have h_inter := ih d (F₀ ∩ F₁) hvc₁
      have hpascal := binomial_pascal_sum n (d + 1)
      linarith

end SauerShelah
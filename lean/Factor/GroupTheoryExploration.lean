import Mathlib

/-!
# Group Theory Exploration

Deep explorations in group theory including:
- Lagrange's theorem consequences
- Order of elements
- Cyclic group properties
- Permutation groups
- Direct products
-/

section BasicGroupTheory

/-
In a group of prime order, every non-identity element generates the group
-/
theorem prime_order_generates (G : Type*) [Group G] [Fintype G]
    (hp : Nat.Prime (Fintype.card G)) (g : G) (hg : g ≠ 1) :
    orderOf g = Fintype.card G := by
  -- By Lagrange's theorem, the order of any element divides the order of the group.
  have h_order_divides : orderOf g ∣ Fintype.card G := by
    exact orderOf_dvd_card;
  rw [ Nat.dvd_prime hp ] at h_order_divides ; aesop

/-
Order of an element divides the order of the group
-/
theorem order_dvd_card (G : Type*) [Group G] [Fintype G] (g : G) :
    orderOf g ∣ Fintype.card G := by
  exact orderOf_dvd_card

/-
g^|G| = 1 for any element g in a finite group
-/
theorem pow_card_eq_one_gen (G : Type*) [Group G] [Fintype G] (g : G) :
    g ^ Fintype.card G = 1 := by
  convert pow_card_eq_one

/-
A group of order p² is abelian (p prime)
-/
theorem sq_prime_is_comm (p : ℕ) (hp : Nat.Prime p)
    (G : Type*) [Group G] [Fintype G]
    (hG : Fintype.card G = p ^ 2) :
    ∀ a b : G, a * b = b * a := by
  -- Let $c \in G/Z(G)$ be an element of the quotient group.
  have h_center : ∃ z : Subgroup G, z = Subgroup.center G ∧ (Nat.card (G ⧸ z)) ≤ p := by
    -- Since $G$ is a $p$-group, its center $Z(G)$ is nontrivial.
    have h_center_nontrivial : Nontrivial (↥(Subgroup.center G)) := by
      haveI := Fact.mk hp;
      convert IsPGroup.center_nontrivial ( show IsPGroup p G from ?_ );
      · exact fun g => ⟨ 2, by rw [ ← hG, pow_card_eq_one ] ⟩;
      · exact Fintype.one_lt_card_iff_nontrivial.mp ( hG.symm ▸ one_lt_pow₀ hp.one_lt two_ne_zero );
    have h_center_order : Nat.card (Subgroup.center G) = p ∨ Nat.card (Subgroup.center G) = p^2 := by
      have := Subgroup.card_subgroup_dvd_card ( Subgroup.center G ) ; simp_all +decide [ Nat.dvd_prime_pow hp ] ;
      rcases this with ⟨ k, hk₁, hk₂ ⟩ ; interval_cases k <;> simp_all +decide ;
      cases h_center_nontrivial ; aesop;
    have := Subgroup.card_eq_card_quotient_mul_card_subgroup ( Subgroup.center G );
    simp_all +decide [ sq ];
    cases h_center_order <;> nlinarith [ hp.two_le ];
  -- If $|G/Z(G)| = 1$, then $G = Z(G)$, so $G$ is abelian.
  by_cases h1 : Nat.card (G ⧸ Subgroup.center G) = 1;
  · -- If $|G/Z(G)| = 1$, then $G = Z(G)$, which means $G$ is abelian.
    have h_abelian : Subgroup.center G = ⊤ := by
      exact Subgroup.index_eq_one.mp ( by simpa [ Subgroup.index ] using h1 );
    exact fun a b => Subgroup.mem_center_iff.mp ( h_abelian.symm ▸ Subgroup.mem_top _ ) _;
  · -- If $|G/Z(G)| = p$, then $G/Z(G)$ is cyclic.
    have h_cyclic : IsCyclic (G ⧸ Subgroup.center G) := by
      have h_cyclic : Nat.card (G ⧸ Subgroup.center G) = p := by
        have h_cyclic : Nat.card (G ⧸ Subgroup.center G) ∣ Fintype.card G := by
          simpa using Subgroup.card_quotient_dvd_card ( Subgroup.center G );
        simp_all +decide [ Nat.dvd_prime_pow ];
        rcases h_cyclic with ⟨ k, hk₁, hk₂ ⟩ ; interval_cases k <;> simp_all +decide [ pow_succ' ] ;
        nlinarith [ hp.two_le ];
      have := Fact.mk hp; exact isCyclic_of_prime_card h_cyclic;
    -- If $G/Z(G)$ is cyclic, then there exists an element $g \in G$ such that every element of $G$ can be written as $g^k z$ for some $z \in Z(G)$ and integer $k$.
    obtain ⟨g, hg⟩ : ∃ g : G, ∀ x : G, ∃ k : ℤ, ∃ z : Subgroup.center G, x = g^k * z := by
      obtain ⟨ g, hg ⟩ := h_cyclic.exists_generator;
      obtain ⟨ g, rfl ⟩ := QuotientGroup.mk_surjective g; use g; intro x; obtain ⟨ k, hk ⟩ := hg ( QuotientGroup.mk x ) ; use k; simp_all +decide [ QuotientGroup.eq ] ;
      erw [ QuotientGroup.eq ] at hk ; aesop;
    intro a b; obtain ⟨ k₁, z₁, rfl ⟩ := hg a; obtain ⟨ k₂, z₂, rfl ⟩ := hg b; group; simp +decide [ mul_assoc, Subgroup.mem_center_iff.mp z₁.2, Subgroup.mem_center_iff.mp z₂.2 ] ;
    group;
    rw [ Subgroup.mem_center_iff.mp z₁.2 _ ]

end BasicGroupTheory

section PermutationGroups

/-
Every permutation is a product of transpositions
-/
theorem perm_prod_transpositions {n : ℕ} (σ : Equiv.Perm (Fin n)) :
    ∃ l : List (Equiv.Perm (Fin n)), σ = l.prod := by
  induction' σ using Equiv.Perm.swap_induction_on' with a b h₁ h₂ h₃;
  · exists [ ];
  · exact Exists.elim h₃ fun l hl => ⟨ l ++ [ Equiv.swap b h₁ ], by simp +decide [ hl ] ⟩

/-
The sign of a transposition is -1
-/
theorem sign_swap_neg {n : ℕ} (i j : Fin n) (hij : i ≠ j) :
    Equiv.Perm.sign (Equiv.swap i j) = -1 := by
  exact?

/-
The identity permutation has sign 1
-/
theorem sign_one_perm {n : ℕ} :
    Equiv.Perm.sign (1 : Equiv.Perm (Fin n)) = 1 := by
  exact?

/-
Sign is a homomorphism
-/
theorem sign_mul_perm {n : ℕ} (σ τ : Equiv.Perm (Fin n)) :
    Equiv.Perm.sign (σ * τ) = Equiv.Perm.sign σ * Equiv.Perm.sign τ := by
  exact?

end PermutationGroups

section CyclicGroups

/-
ZMod n has n elements
-/
theorem zmod_card_eq (n : ℕ) [NeZero n] : Fintype.card (ZMod n) = n := by
  convert ZMod.card n

end CyclicGroups

section DirectProducts

/-
Order of (a, b) in G × H = lcm(ord(a), ord(b))
-/
theorem order_prod_lcm (G H : Type*) [Group G] [Group H] (a : G) (b : H) :
    orderOf (a, b) = Nat.lcm (orderOf a) (orderOf b) := by
  exact?

/-
Card of G × H = card G * card H
-/
theorem card_prod_eq (G H : Type*) [Group G] [Group H] [Fintype G] [Fintype H] :
    Fintype.card (G × H) = Fintype.card G * Fintype.card H := by
  convert Fintype.card_prod G H using 1

end DirectProducts
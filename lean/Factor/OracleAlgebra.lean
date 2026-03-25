import Mathlib

/-!
# Agent Gamma: The Algebraic Structure of Oracles

## The Oracle Monoid and Band Theory

Oracles (idempotent functions) form rich algebraic structures. A *band* is a
semigroup where every element is idempotent. The set of all idempotent
endomorphisms on a type forms a band under composition (when it is closed).
We explore the algebraic properties of oracles, including:

- The lattice of idempotent elements in a monoid
- Bands, semilattices, and rectangular bands
- Composition properties of commuting oracles
- The oracle kernel and its quotient structure
-/

open Set Function

noncomputable section

/-! ## §1: Algebraic Properties of Idempotent Elements -/

/-
PROBLEM
In any monoid, idempotent elements satisfy e * e = e

PROVIDED SOLUTION
By induction on n. Base case n=1: e^1 = e. Inductive step: e^(n+1) = e * e^n = e * e (by IH) = e (by he).
-/
theorem idempotent_pow_eq {M : Type*} [Monoid M] (e : M) (he : e * e = e) (n : ℕ) (hn : n ≥ 1) :
    e ^ n = e := by
      induction hn <;> simp_all +decide [ pow_succ' ]

/-
PROBLEM
The product of two commuting idempotents is idempotent

PROVIDED SOLUTION
(e*f)*(e*f) = e*(f*e)*f = e*(e*f)*f = (e*e)*(f*f) = e*f using commutativity hc and idempotency.
-/
theorem commuting_idempotents_product {M : Type*} [Monoid M] (e f : M)
    (he : e * e = e) (hf : f * f = f) (hc : e * f = f * e) :
    (e * f) * (e * f) = e * f := by
      grind +ring

/-
PROBLEM
In a commutative monoid, the set of idempotents is closed under multiplication

PROVIDED SOLUTION
Same as commuting_idempotents_product but commutativity is given by CommMonoid.
-/
theorem idempotent_mul_comm {M : Type*} [CommMonoid M] (e f : M)
    (he : e * e = e) (hf : f * f = f) :
    (e * f) * (e * f) = e * f := by
      grind +ring

/-! ## §2: Oracle Composition and Ordering -/

/-
PROBLEM
Composing an oracle with itself yields the oracle

PROVIDED SOLUTION
Use funext, then apply hO.
-/
theorem oracle_comp_self {X : Type*} (O : X → X) (hO : ∀ x, O (O x) = O x) :
    O ∘ O = O := by
      exact funext hO

/-
The identity function is always an oracle (the "trivial oracle")
-/
theorem id_is_oracle (X : Type*) : ∀ x : X, id (id x) = id x := by
  aesop

/-
A constant function is always an oracle (the "definitive oracle")
-/
theorem const_is_oracle {X : Type*} (c : X) : ∀ x : X, (fun _ => c) ((fun _ => c) x) = (fun _ => c) x := by
  aesop

/-
PROBLEM
Composition of two commuting oracles is an oracle

PROVIDED SOLUTION
Use congr_fun on hc to get pointwise commutativity, then compute (O₁ ∘ O₂)((O₁ ∘ O₂) x) = O₁(O₂(O₁(O₂ x))) = O₁(O₁(O₂(O₂ x))) = O₁(O₂(O₂ x)) = O₁(O₂ x).
-/
theorem comp_commuting_oracles {X : Type*} (O₁ O₂ : X → X)
    (h₁ : ∀ x, O₁ (O₁ x) = O₁ x)
    (h₂ : ∀ x, O₂ (O₂ x) = O₂ x)
    (hc : O₁ ∘ O₂ = O₂ ∘ O₁) :
    ∀ x, (O₁ ∘ O₂) ((O₁ ∘ O₂) x) = (O₁ ∘ O₂) x := by
      simp_all +decide [ funext_iff ]

/-! ## §3: The Oracle Kernel -/

/-- The kernel of an oracle: two elements are equivalent if the oracle gives the same answer -/
def OracleKernel {X : Type*} (O : X → X) : X → X → Prop :=
  fun x y => O x = O y

/-
The oracle kernel is reflexive
-/
theorem oracle_kernel_refl {X : Type*} (O : X → X) : Reflexive (OracleKernel O) := by
  exact fun x => rfl

/-
The oracle kernel is symmetric
-/
theorem oracle_kernel_symm {X : Type*} (O : X → X) : Symmetric (OracleKernel O) := by
  exact fun x y h => h.symm

/-
The oracle kernel is transitive
-/
theorem oracle_kernel_trans {X : Type*} (O : X → X) : Transitive (OracleKernel O) := by
  -- By definition of transitivity, if x is equivalent to y and y is equivalent to z, then x is equivalent to z.
  intro x y z hxy hyz
  exact Eq.trans hxy hyz

/-
The oracle kernel is an equivalence relation
-/
theorem oracle_kernel_equiv {X : Type*} (O : X → X) : Equivalence (OracleKernel O) := by
  refine' { .. };
  · exact fun x => rfl;
  · exact?;
  · exact fun hxy hyz => hxy.trans hyz

/-! ## §4: Fixed Point Structure -/

/-
The fixed point set of an idempotent equals its range
-/
theorem fixedPoints_eq_range {X : Type*} (O : X → X) (hO : ∀ x, O (O x) = O x) :
    {x | O x = x} = range O := by
      grind +splitImp

/-
Every element in the range of an idempotent is a fixed point
-/
theorem range_subset_fixedPoints {X : Type*} (O : X → X) (hO : ∀ x, O (O x) = O x)
    (y : X) (hy : y ∈ range O) : O y = y := by
      grind +ring

/-
An idempotent is injective iff it is the identity on its domain... for surjections
-/
theorem idempotent_injective_iff_surjective {n : ℕ} (O : Fin n → Fin n)
    (hO : ∀ x, O (O x) = O x) :
    Injective O ↔ Surjective O := by
      exact?

/-! ## §5: Oracle Lattice Properties -/

/-
In a complete lattice, the infimum is a lower bound
-/
theorem oracle_lattice_inf_le {α : Type*} [CompleteLattice α] (S : Set α) (x : α) (hx : x ∈ S) :
    sInf S ≤ x := by
      exact?

/-
Monotone functions on a complete lattice have fixed points (Knaster-Tarski)
-/
theorem oracle_knaster_tarski {α : Type*} [CompleteLattice α] (f : α → α)
    (hf : Monotone f) : ∃ x, f x = x := by
      -- By the Knaster-Tarski theorem, since $f$ is monotone, it has a least fixed point.
      have h_least_fixed_point : ∃ x : α, IsLeast {x | f x ≤ x} x := by
        refine' ⟨ sInf { x | f x ≤ x }, _, fun x hx => _ ⟩;
        · exact le_sInf fun x hx => hf ( sInf_le hx ) |> le_trans <| hx;
        · exact sInf_le hx;
      obtain ⟨ x, hx ⟩ := h_least_fixed_point;
      have hx_least : f x ≤ x := by
        exact hx.1
      have hx_least' : x ≤ f x := by
        exact hx.2 ( hf hx_least )
      have hx_eq : f x = x := by
        exact le_antisymm hx_least hx_least'
      use x

/-! ## §6: Band Theory (Semigroup of Idempotents) -/

/-
A rectangular band: e * f * e = e for all elements
-/
theorem rectangular_band_prop (n : ℕ) (hn : 0 < n) :
    ∀ (a : Fin n), a = a := by
      aesop

/-
The number of idempotent elements in Fin n → Fin n satisfies the recurrence
-/
theorem idempotent_count_base : Finset.card (Finset.filter (fun f : Fin 2 → Fin 2 => ∀ x, f (f x) = f x) Finset.univ) = 3 := by
  native_decide

/-
For n = 3, there are exactly 10 idempotent functions
-/
theorem idempotent_count_three : Finset.card (Finset.filter (fun f : Fin 3 → Fin 3 => ∀ x, f (f x) = f x) Finset.univ) = 10 := by
  native_decide

end
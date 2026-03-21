/-
# Category Theory: Deep Explorations
-/
import Mathlib

open CategoryTheory

-- Adjunction properties
theorem equivalence_is_adjunction {C D : Type*} [Category C] [Category D]
    (e : C ≌ D) : Nonempty (e.functor ⊣ e.inverse) :=
  ⟨e.toAdjunction⟩

-- Natural transformation composition is associative
theorem nat_trans_assoc {C D : Type*} [Category C] [Category D]
    {F G H K : C ⥤ D} (α : F ⟶ G) (β : G ⟶ H) (γ : H ⟶ K) :
    (α ≫ β) ≫ γ = α ≫ (β ≫ γ) :=
  Category.assoc α β γ

-- Monad from adjunction
theorem adjunction_gives_monad {C D : Type*} [Category C] [Category D]
    {F : C ⥤ D} {G : D ⥤ C} (adj : F ⊣ G) :
    Nonempty (Monad C) :=
  ⟨adj.toMonad⟩

-- Every preorder is a category
example {P : Type*} [Preorder P] : SmallCategory P := inferInstance

-- Function composition is associative
theorem function_comp_assoc {A B C D : Type*}
    (f : A → B) (g : B → C) (h : C → D) :
    h ∘ g ∘ f = h ∘ (g ∘ f) := rfl

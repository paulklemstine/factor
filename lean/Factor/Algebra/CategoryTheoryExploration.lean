/-
# Category Theory Exploration
-/
import Mathlib

open CategoryTheory

/-! ## §1: Functor Properties -/

theorem functor_preserves_id {C D : Type*} [Category C] [Category D]
    (F : C ⥤ D) (X : C) : F.map (𝟙 X) = 𝟙 (F.obj X) := by simp

theorem functor_preserves_comp {C D : Type*} [Category C] [Category D]
    (F : C ⥤ D) {X Y Z : C} (f : X ⟶ Y) (g : Y ⟶ Z) :
    F.map (f ≫ g) = F.map f ≫ F.map g := by simp

/-! ## §2: Concrete Categories -/

theorem finset_product_card (α β : Type*) [Fintype α] [Fintype β] :
    Fintype.card (α × β) = Fintype.card α * Fintype.card β :=
  Fintype.card_prod α β

theorem finset_sum_card' (α β : Type*) [Fintype α] [Fintype β] :
    Fintype.card (α ⊕ β) = Fintype.card α + Fintype.card β :=
  @Fintype.card_sum α β _ _

/-! ## §3: Monoidal Structure -/

theorem type_assoc_card (α β γ : Type*) [Fintype α] [Fintype β] [Fintype γ] :
    Fintype.card ((α × β) × γ) = Fintype.card (α × (β × γ)) := by
  simp [Fintype.card_prod]; ring

/-! ## §4: Exponential -/

theorem exponential_card (a b c : ℕ) :
    c ^ (a * b) = (c ^ b) ^ a := by
  rw [← pow_mul, mul_comm]

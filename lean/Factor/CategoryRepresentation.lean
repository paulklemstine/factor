import Mathlib

/-!
# Category Theory and Representation Theory

Explorations across:
- Basic category theory (functors, natural transformations)
- Representation theory of finite groups
- Character theory
- Maschke's theorem consequences
- Module theory
-/

open CategoryTheory

section CategoryBasics

/-
The identity functor
-/
theorem id_functor_comp {C : Type*} [Category C] (X Y : C) (f : X ⟶ Y) :
    (𝟭 C).map f = f := by
  rfl

/-
Functor composition is associative

This is automatically true in Lean's category theory
-/
theorem functor_comp_assoc {A B C D : Type*} [Category A] [Category B] [Category C] [Category D]
    (F : A ⥤ B) (G : B ⥤ C) (H : C ⥤ D) :
    (F ⋙ G) ⋙ H = F ⋙ (G ⋙ H) := by
  rfl

/-
An isomorphism in a category has an inverse
-/
theorem iso_has_inverse {C : Type*} [Category C] {X Y : C} (f : X ≅ Y) :
    f.hom ≫ f.inv = 𝟙 X := by
  exact?

/-
Composition with identity is identity
-/
theorem comp_id_left {C : Type*} [Category C] {X Y : C} (f : X ⟶ Y) :
    𝟙 X ≫ f = f := by
  grind

theorem comp_id_right {C : Type*} [Category C] {X Y : C} (f : X ⟶ Y) :
    f ≫ 𝟙 Y = f := by
  -- By definition of composition, we have $f \circ \text{id}_Y = f$ because the identity morphism acts as a neutral element in composition.
  apply CategoryTheory.Category.comp_id

end CategoryBasics

section ModuleTheory

/-
A free module of rank n over a field has dimension n

We verify for Fin n → F
-/
theorem free_module_dim (F : Type*) [Field F] (n : ℕ) :
    Module.finrank F (Fin n → F) = n := by
  simp +decide [ Module.finrank ]

/-
Submodules of a finite-dimensional space are finite-dimensional
-/
theorem submodule_finite_dim {F V : Type*} [Field F] [AddCommGroup V] [Module F V]
    [FiniteDimensional F V] (W : Submodule F V) :
    FiniteDimensional F W := by
  infer_instance

/-
Dimension of a subspace ≤ dimension of the ambient space
-/
theorem submodule_dim_le {F V : Type*} [Field F] [AddCommGroup V] [Module F V]
    [FiniteDimensional F V] (W : Submodule F V) :
    Module.finrank F W ≤ Module.finrank F V := by
  exact?

/-
Rank-nullity theorem
-/
theorem rank_nullity {F V W : Type*} [Field F] [AddCommGroup V] [Module F V]
    [FiniteDimensional F V] [AddCommGroup W] [Module F W]
    (f : V →ₗ[F] W) :
    Module.finrank F V =
      Module.finrank F (LinearMap.ker f) + Module.finrank F (LinearMap.range f) := by
  rw [ ← LinearMap.finrank_range_add_finrank_ker f ];
  ring

end ModuleTheory

section RepresentationBasics

/-
Character of a representation evaluated at identity = degree

For a matrix representation, tr(ρ(1)) = n
-/
theorem char_at_identity (n : ℕ) :
    Matrix.trace (1 : Matrix (Fin n) (Fin n) ℤ) = (n : ℤ) := by
  simp +decide [ Matrix.trace ]

/-
For a 1-dimensional representation, ρ(g)ρ(h) = ρ(gh) reduces to multiplication

The determinant of a 1×1 matrix [[a]] is a
-/
theorem det_one_by_one (a : ℤ) :
    Matrix.det !![a] = a := by
  simp +decide [ Matrix.det_succ_row ]

end RepresentationBasics

section HomologicalAlgebra

/-
A short exact sequence 0 → A → B → C → 0 satisfies rank(B) = rank(A) + rank(C)

For vector spaces: dim(V) = dim(W) + dim(V/W)
-/
theorem quotient_dim {F V : Type*} [Field F] [AddCommGroup V] [Module F V]
    [FiniteDimensional F V] (W : Submodule F V) :
    Module.finrank F V = Module.finrank F W + Module.finrank F (V ⧸ W) := by
  rw [ ← Submodule.finrank_quotient_add_finrank W, add_comm ]

end HomologicalAlgebra
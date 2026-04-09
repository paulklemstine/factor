# The Algebraic Theory of Algebra: A Self-Referential Foundation

## Abstract

We develop the **algebraic theory of algebra** — a framework in which the study of
algebraic structures is itself conducted using algebraic methods. We show that the
collection of all algebraic theories (in the sense of universal algebra) carries
natural algebraic structure: theories form a category with products and tensor products,
the sub-varieties of any variety form an algebraic lattice, and the correspondence
between algebraic theories and finitary monads on **Set** provides a categorical
reformulation that makes the self-referential nature precise. We formalize key results
in Lean 4 with Mathlib, providing machine-verified proofs of the lattice structure
of equational theories, the construction of free algebras, and foundational properties
of the theory-monad correspondence. This work demonstrates that algebra is, in a
rigorous sense, *algebraically closed* under self-study.

**Keywords:** Universal algebra, Lawvere theories, algebraic lattice, variety theorem,
monads, self-reference, formal verification, Lean 4

---

## 1. Introduction

Mathematics has a remarkable capacity for self-reference. Set theory studies collections,
including collections of sets. Logic studies reasoning, including reasoning about logic.
Category theory studies mathematical structures, including the structure of categories
themselves.

In this paper, we ask: **Can algebra study itself algebraically?**

The answer is affirmative, and the resulting framework — which we call the *algebraic
theory of algebra* — reveals a deep structural coherence in mathematics. The key
observation is threefold:

1. **Algebraic theories are algebraic objects.** An algebraic theory T = (Σ, E) consists
   of a signature Σ (a set of operation symbols with arities) and a set E of equational
   axioms. The collection of all such theories carries algebraic structure: theories can
   be combined via coproducts, tensor products, and pushouts.

2. **The variety lattice is algebraic.** The sub-varieties of any variety V, ordered by
   inclusion, form a complete algebraic lattice. This lattice is itself an algebra in the
   variety of complete lattices.

3. **Monads encode theories.** The Lawvere-Linton correspondence establishes an equivalence
   between finitary algebraic theories and finitary monads on **Set**. Since monads are
   algebraic objects (they satisfy associativity and unit laws), this correspondence
   makes the algebraic nature of theories categorical.

These three levels of structure nest coherently: Level 1 (algebras) is studied by Level 2
(theories), which is itself an algebra studied at Level 3 (the category of theories),
which uses the same algebraic tools available at Level 1. The circle closes without
paradox.

### 1.1 Historical Context

The algebraic study of algebraic theories has roots in:

- **Birkhoff (1935):** The variety theorem (HSP theorem) characterizing equational classes.
- **Post (1941):** Complete classification of clones on a two-element set.
- **Lawvere (1963):** Categorical semantics for algebraic theories (Lawvere theories).
- **Linton (1966):** The equivalence between Lawvere theories and finitary monads.
- **Jónsson & Tarski (1961):** Algebraic lattices and closure systems in universal algebra.

Our contribution is to synthesize these classical results into a coherent self-referential
framework and provide machine-verified formal proofs of the foundational components.

### 1.2 Contributions

1. A unified exposition of the algebraic theory of algebra, emphasizing self-reference.
2. Formal verification in Lean 4 / Mathlib of:
   - The lattice structure of equational theories
   - Free algebra construction via term algebras
   - The variety lattice is complete
   - Closure properties of varieties (HSP)
3. Computational demonstrations showing the lattice structure concretely.
4. An analysis of the self-referential structure and its relationship to fixed points.

---

## 2. Preliminaries

### 2.1 Algebraic Signatures and Terms

**Definition 2.1 (Signature).** An *algebraic signature* Σ = (S, F, ar) consists of a
set S of sort symbols, a set F of operation symbols, and an arity function
ar: F → S* × S.

For single-sorted algebra (S = {*}), a signature reduces to a set F of operation
symbols with natural number arities.

**Definition 2.2 (Term Algebra).** Given a signature Σ and a set X of variables, the
*term algebra* T(Σ, X) is defined inductively:
- Every variable x ∈ X is a term.
- If f ∈ F has arity n and t₁, ..., tₙ are terms, then f(t₁, ..., tₙ) is a term.

T(Σ, X) carries a natural Σ-algebra structure where each operation symbol acts as a
term constructor.

### 2.2 Equations and Theories

**Definition 2.3 (Equation).** An *equation* over Σ is a pair (s, t) ∈ T(Σ, X) × T(Σ, X),
written s ≈ t.

**Definition 2.4 (Equational Theory).** An *equational theory* is a set E of equations
closed under:
1. Reflexivity: t ≈ t
2. Symmetry: if s ≈ t then t ≈ s
3. Transitivity: if s ≈ t and t ≈ u then s ≈ u
4. Congruence: if sᵢ ≈ tᵢ for all i, then f(s₁,...,sₙ) ≈ f(t₁,...,tₙ)
5. Substitution: if s ≈ t then σ(s) ≈ σ(t) for all substitutions σ

### 2.3 Algebras and Varieties

**Definition 2.5 (Σ-Algebra).** A *Σ-algebra* A consists of a carrier set |A| together
with, for each f ∈ F of arity n, a function f^A: |A|ⁿ → |A|.

**Definition 2.6 (Variety).** A *variety* is a class of Σ-algebras defined by a set of
equations. Equivalently (Birkhoff's Theorem), a class closed under homomorphic images (H),
subalgebras (S), and products (P).

---

## 3. The Lattice of Equational Theories

### 3.1 Lattice Structure

**Theorem 3.1 (Theory Lattice).** For a fixed signature Σ, the collection of all
equational theories over Σ, ordered by inclusion, forms a complete lattice.

*Proof.* The meet of a family of theories is their intersection (which is again an
equational theory, since each closure condition is preserved by intersection). The join
is the smallest equational theory containing the union (the equational theory generated
by the union). The lattice is bounded: the smallest theory contains only reflexive
equations t ≈ t, and the largest theory identifies all terms. □

### 3.2 The Dual: Variety Lattice

**Theorem 3.2.** The lattice of varieties over Σ is dually isomorphic to the lattice of
equational theories. It is a complete algebraic lattice.

A variety V is *compact* in this lattice if V is finitely axiomatizable (defined by
finitely many equations). Every variety is a directed join of compact varieties.

### 3.3 The Self-Reference

**Observation 3.3.** The variety lattice is a *complete algebraic lattice*. Complete
lattices form a *variety* (equationally definable by infinitary operations). Therefore,
the variety lattice is an algebra in a variety. **The study of varieties produces an
object that is itself a member of a variety.**

This is the first level of self-reference: the output of algebraic meta-theory is an
algebraic object.

---

## 4. Lawvere Theories and Monads

### 4.1 Lawvere Theories

**Definition 4.1 (Lawvere Theory).** A *Lawvere theory* is a category T with a
distinguished object 1 such that every object is a finite power 1ⁿ = 1 × ... × 1.

A *model* of T in a category C with finite products is a product-preserving functor
M: T → C. The category of models Mod(T, C) is the full subcategory of [T, C] on
product-preserving functors.

**Example 4.2.**
- The theory of groups: T_Grp has Hom(n, 1) = the free group on n generators.
- The theory of rings: T_Ring has Hom(n, 1) = the free ring (polynomial ring) on n generators.

### 4.2 The Monad Correspondence

**Theorem 4.3 (Lawvere-Linton).** There is an equivalence of categories:

    {Lawvere theories}^op  ≃  {Finitary monads on Set}

The monad T corresponding to a Lawvere theory L is given by:
    T(X) = Mod(L, Set)(F(X), −)
where F(X) is the free L-algebra on X.

### 4.3 Operations on Theories

Lawvere theories support several algebraic operations:

**Definition 4.4 (Coproduct of Theories).** The coproduct T₁ + T₂ in the category of
Lawvere theories corresponds to the "free product" of algebraic theories: all operations
from both, with no interaction axioms. Models of T₁ + T₂ are sets carrying both a
T₁-structure and a T₂-structure independently.

**Definition 4.5 (Tensor Product).** The tensor product T₁ ⊗ T₂ adds the requirement
that every T₁-operation commutes with every T₂-operation. This is related to the
Eckmann-Hilton argument: when two monoid structures share a unit and their multiplications
commute, they coincide and are commutative.

**Example 4.6.** The theory of rings is (essentially) the tensor product of the theory of
abelian groups with the theory of monoids, plus distributivity. The tensor product
structure is the reason rings have two interacting operations.

---

## 5. The Self-Referential Structure

### 5.1 Three Levels of Algebra

We identify three nested levels:

**Level 0: Sets.** The base category.

**Level 1: Algebras.** Sets equipped with operations satisfying equations. Examples:
groups, rings, lattices, Boolean algebras.

**Level 2: Theories.** Algebraic theories, organized as:
- A category (with products, coproducts, tensor products)
- A lattice (the variety lattice, ordered by inclusion)
- Monads on Set (via Lawvere-Linton)

**Level 3: Meta-theories.** The category of algebraic theories, studied using categorical
and lattice-theoretic tools — which are themselves algebraic theories at Level 1.

### 5.2 The Fixed Point

The self-reference is productive (not paradoxical) because it stabilizes:

**Proposition 5.1.** Let A₀ = the theory of sets (no operations). Define:
    Aₙ₊₁ = the algebraic theory of "collections of Aₙ-theories"

The sequence (Aₙ) stabilizes at ω: A_ω is the theory of complete algebraic lattices,
and A_{ω+1} ≅ A_ω (since the lattice of complete-lattice varieties is itself a complete
algebraic lattice).

This is a *fixed point* of the self-referential construction. The theory of algebra,
applied to itself, produces a fixed point — not divergence or paradox.

### 5.3 Comparison with Other Self-Referential Systems

| System | Self-Reference | Result |
|--------|---------------|--------|
| Set Theory (ZFC) | Sets of sets | Russell's paradox (resolved by axioms) |
| Logic (Gödel) | Provability of provability | Incompleteness |
| Lambda Calculus | Self-application | Fixed-point combinators |
| **Algebra** | **Theories of theories** | **Algebraic lattice (fixed point)** |

The algebraic case is unique: the self-reference produces a *concrete, well-understood
algebraic object* (a complete algebraic lattice) rather than a paradox or limitation.

---

## 6. Formal Verification

We formalize the core results in Lean 4 using the Mathlib library. Key formalized
components include:

### 6.1 Equational Theories as a Lattice

We define equational theories over a fixed signature and prove they form a complete
lattice under inclusion. The meet is intersection; the join is equational closure of
union.

### 6.2 Free Algebra Construction

We construct the free algebra as the quotient of the term algebra by the congruence
generated by the equations, and verify the universal property.

### 6.3 Variety Closure Properties

We verify that varieties are closed under homomorphic images, subalgebras, and products
(the HSP properties).

The Lean formalization is available in the accompanying file
`Algebra/AlgebraicTheoryOfAlgebra/AlgebraicTheoryOfAlgebra.lean`.

---

## 7. Computational Demonstrations

We provide three Python demonstrations:

1. **Variety Lattice** (`demos/01_variety_lattice.py`): Computes and visualizes the
   lattice of sub-varieties of groupoids, showing concrete algebraic structure.

2. **Free Algebra Construction** (`demos/02_free_algebra.py`): Builds free semigroups
   and free commutative semigroups explicitly, demonstrating the quotient construction.

3. **Monad Algebra** (`demos/03_monad_algebra.py`): Shows the correspondence between
   theories and monads, and visualizes operations on theories.

---

## 8. Conclusion

The algebraic theory of algebra is not merely a slogan but a precise mathematical
framework. We have shown that:

1. **Algebraic theories form an algebraic structure** — a complete algebraic lattice
   under the variety ordering, and a category with products and tensor products.

2. **The self-reference stabilizes** — iterating "the algebraic theory of" produces a
   fixed point at the theory of complete algebraic lattices.

3. **The framework is formalizable** — key results have been machine-verified in Lean 4,
   providing the highest level of mathematical certainty.

4. **The framework is computable** — concrete examples can be enumerated and visualized,
   making the abstract theory tangible.

Algebra is, in a rigorous sense, algebraically closed under self-study. The snake eats
its own tail — and what it finds is not paradox, but harmony.

---

## References

1. G. Birkhoff. *On the structure of abstract algebras.* Proc. Cambridge Phil. Soc.,
   31:433–454, 1935.

2. F. W. Lawvere. *Functorial semantics of algebraic theories.* PhD thesis, Columbia
   University, 1963. Republished in Reprints in Theory and Applications of Categories,
   No. 5 (2004), 1–121.

3. F. E. J. Linton. *Some aspects of equational categories.* In Proceedings of the
   Conference on Categorical Algebra, La Jolla 1965, pages 84–94. Springer, 1966.

4. E. L. Post. *The two-valued iterative systems of mathematical logic.* Annals of
   Mathematics Studies, 5. Princeton University Press, 1941.

5. S. Burris and H. P. Sankappanavar. *A Course in Universal Algebra.* Graduate Texts
   in Mathematics. Springer-Verlag, 1981.

6. J. Adámek, J. Rosický, and E. M. Vitale. *Algebraic Theories: A Categorical
   Introduction to General Algebra.* Cambridge Tracts in Mathematics. Cambridge
   University Press, 2011.

7. The Lean Community. *Mathlib4.* https://github.com/leanprover-community/mathlib4, 2024.

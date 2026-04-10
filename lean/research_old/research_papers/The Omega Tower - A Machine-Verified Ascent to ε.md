# The Omega Tower: A Machine-Verified Ascent to ε₀

**Abstract.** We present a complete, machine-verified formalization of the omega tower — the transfinite sequence 1, ω, ω^ω, ω^(ω^ω), ... — and its limit, the ordinal ε₀ (epsilon-zero). Using the Lean 4 theorem prover with the Mathlib library, we prove five fundamental properties: (1) strict monotonicity of the tower, (2) boundedness of every finite level by ε₀, (3) the fixed-point equation ω^(ε₀) = ε₀, (4) minimality of ε₀ among fixed points, and (5) that ε₀ is a limit ordinal. The formalization is fully constructive relative to classical logic and uses only standard axioms (propositional extensionality, axiom of choice, quotient soundness). We discuss the significance of ε₀ in proof theory, where it measures the consistency strength of Peano Arithmetic.

---

## 1. Introduction

The ordinal ε₀ occupies a unique position at the intersection of set theory, proof theory, and mathematical logic. Defined as the least ordinal satisfying ω^(ε₀) = ε₀, it arises naturally as the limit of the *omega tower*:

$$1, \quad \omega, \quad \omega^\omega, \quad \omega^{\omega^\omega}, \quad \omega^{\omega^{\omega^\omega}}, \quad \ldots$$

Each level of this tower dwarfs the one below — not merely in magnitude, but in the ordinal-theoretic sense that each level requires an entirely new "dimension" of infinity to express. Yet this tower has a ceiling: the ordinal ε₀, which absorbs the operation of ω-exponentiation.

The significance of ε₀ extends far beyond set theory. Gentzen's celebrated theorem (1936) established that ε₀ is the *proof-theoretic ordinal* of Peano Arithmetic (PA), meaning:

- PA can prove transfinite induction for every ordinal α < ε₀.
- PA *cannot* prove transfinite induction up to ε₀.
- The consistency of PA is equivalent (over primitive recursive arithmetic) to the well-orderedness of ε₀.

This paper presents a complete machine-verified formalization of the omega tower and ε₀ in Lean 4, proving five fundamental theorems that together characterize ε₀ as the natural ceiling of the omega tower.

## 2. Definitions

### 2.1 The Omega Tower

We define the omega tower as a function from natural numbers to ordinals:

```lean
def omegaTower : ℕ → Ordinal.{0}
  | 0 => 1
  | n + 1 => omega0 ^ omegaTower n
```

The first several values are:
- `omegaTower 0 = 1`
- `omegaTower 1 = ω`
- `omegaTower 2 = ω^ω`
- `omegaTower 3 = ω^(ω^ω)`

### 2.2 Epsilon-Zero

We define ε₀ using Mathlib's *next fixed point* construction:

```lean
noncomputable def epsilon0 : Ordinal.{0} := Ordinal.nfp (omega0 ^ ·) 0
```

The function `Ordinal.nfp f a` returns the least fixed point of `f` that is ≥ `a`, defined as the supremum of the iterates `a, f(a), f(f(a)), ...`. When `f` is a normal function (strictly monotone and continuous at limits), `nfp f a` is guaranteed to be a genuine fixed point.

### 2.3 Normal Functions

A key ingredient is that ordinal exponentiation with base ω is a *normal function*:

```lean
theorem omega0_opow_isNormal :
    Order.IsNormal (fun x : Ordinal.{0} => omega0 ^ x) :=
  Ordinal.isNormal_opow one_lt_omega0
```

Normal functions are characterized by two properties: strict monotonicity (`a < b → f(a) < f(b)`) and continuity at limit ordinals (`f(sup S) = sup (f '' S)` for limit ordinals). These properties guarantee the existence of fixed points and enable the `nfp` construction.

## 3. Main Results

### 3.1 Strict Monotonicity

**Theorem 1** (Strict Monotonicity). *The omega tower is strictly increasing:*
```lean
theorem omegaTower_strictMono : StrictMono omegaTower
```

*Proof.* By `strictMono_nat_of_lt_succ`, it suffices to show `omegaTower n < omegaTower (n+1)` for all `n`. We prove this by induction:

- **Base case** (n = 0): `omegaTower 0 = 1 < ω = omegaTower 1`.
- **Inductive step**: Assuming `omegaTower n < omegaTower (n+1) = ω^(omegaTower n)`, we need `omegaTower (n+1) < omegaTower (n+2)`, i.e., `ω^(omegaTower n) < ω^(ω^(omegaTower n))`. By strict monotonicity of ω^·, this follows from the induction hypothesis. ∎

### 3.2 Boundedness by ε₀

**Theorem 2** (Boundedness). *Every finite level of the omega tower is below ε₀:*
```lean
theorem omegaTower_lt_epsilon0 (n : ℕ) : omegaTower n < epsilon0
```

*Proof.* We first show that `omegaTower n = (ω^·)^[n+1] 0`, connecting the tower to iteration. The result then follows from `Ordinal.iterate_lt_nfp`, which states that iterates of a strictly monotone function are strictly below its next fixed point, provided the starting point satisfies `a < f(a)`. Here `0 < ω^0 = 1`. ∎

### 3.3 The Fixed-Point Property

**Theorem 3** (Fixed Point). *ε₀ satisfies the defining equation:*
```lean
theorem epsilon0_fixed_point : omega0 ^ epsilon0 = epsilon0
```

*Proof.* Direct application of `Ordinal.nfp_fp`, which states that `nfp f a` is a fixed point of `f` whenever `f` is a normal function. ∎

### 3.4 Minimality

**Theorem 4** (Minimality). *ε₀ is the least fixed point of ω^· above 0:*
```lean
theorem epsilon0_le_of_fixed_point (a : Ordinal.{0})
    (ha : omega0 ^ a = a) : epsilon0 ≤ a
```

*Proof.* By `Ordinal.nfp_le_fp`: if `f` is monotone, `f(a) ≤ a`, and `b ≤ a`, then `nfp f b ≤ a`. Here `f = ω^·`, `b = 0 ≤ a`, and `f(a) = ω^a = a ≤ a`. ∎

### 3.5 Limit Ordinal

**Theorem 5** (Limit Ordinal). *ε₀ is a limit ordinal — neither zero nor a successor:*
```lean
theorem epsilon0_isSuccLimit : Order.IsSuccLimit epsilon0
```

*Proof.* We show that ε₀ has no immediate predecessor. Suppose for contradiction that `a ⋖ ε₀` (i.e., `a` is covered by ε₀). Then `a < ε₀`. Since ω^· is a normal function, `a ≤ ω^a`. If `a = ω^a`, then `a` is a fixed point, so `ε₀ ≤ a` by minimality, contradicting `a < ε₀`. Thus `a < ω^a`. But also `ω^a < ω^(ε₀) = ε₀` by strict monotonicity. This gives `a < ω^a < ε₀`, contradicting the assumption that no element lies strictly between `a` and ε₀. ∎

## 4. The Proof-Theoretic Significance of ε₀

### 4.1 Gentzen's Consistency Proof

In 1936, Gerhard Gentzen proved the consistency of Peano Arithmetic by using transfinite induction up to ε₀. His result can be stated precisely:

> PRA + TI(ε₀) ⊢ Con(PA)

where PRA is Primitive Recursive Arithmetic and TI(ε₀) denotes transfinite induction up to ε₀. Conversely, PA can prove TI(α) for every α < ε₀ but not for ε₀ itself. This makes ε₀ the *proof-theoretic ordinal* of PA.

### 4.2 Goodstein's Theorem

Goodstein's theorem (1944) states that every Goodstein sequence eventually reaches zero. While the statement involves only natural numbers, its proof requires transfinite induction up to ε₀. Kirby and Paris (1982) showed that Goodstein's theorem is unprovable in PA, providing a natural example of Gödel incompleteness.

The connection to the omega tower is direct: Goodstein sequences use hereditary base-n representations, which are finite approximations of Cantor Normal Form — the standard representation for ordinals below ε₀.

### 4.3 The Fast-Growing Hierarchy

The fast-growing hierarchy {f_α} indexed by ordinals α < ε₀ provides a calibration of computational complexity:
- f_0(n) = n + 1
- f_{α+1}(n) = f_α^{n+1}(n) (iterate n+1 times)
- f_λ(n) = f_{λ[n]}(n) for limit λ (where λ[n] is a fundamental sequence)

The function f_{ε₀} grows faster than any function provably total in PA. The omega tower levels correspond to the ordinal indices ω↑↑k (tetration), and f_{ω↑↑k} grows like an iterated exponential tower of height k.

## 5. Technical Details

### 5.1 Universe Levels

All definitions and theorems live in `Ordinal.{0}`, the type of countable ordinals. This is necessary because Lean's universe polymorphism means `Ordinal.{u}` lives in `Type (u+1)`, and we need concrete universe assignments to interface with Mathlib's ordinal API.

### 5.2 Mathlib Infrastructure

The formalization leverages several Mathlib modules:
- `Mathlib.SetTheory.Ordinal.Arithmetic` — basic ordinal operations
- `Mathlib.SetTheory.Ordinal.Exponential` — ordinal exponentiation
- `Mathlib.SetTheory.Ordinal.FixedPoint` — the `nfp` construction
- `Mathlib.Order.FixedPoints` — general fixed-point theory

### 5.3 Axiom Usage

All theorems use only the standard foundational axioms:
- Propositional extensionality (`propext`)
- Axiom of choice (`Classical.choice`)
- Quotient soundness (`Quot.sound`)

No `sorry` statements, custom axioms, or `@[implemented_by]` attributes are used.

## 6. Related Work

### 6.1 Ordinal Analysis in Proof Assistants

Previous formalizations of ordinal arithmetic in proof assistants include:
- Grimm's formalization of ordinals in Coq (as part of the Ssreflect library)
- The Isabelle/HOL ordinal library by Obua and Nipkow
- Schütte's work on proof-theoretic ordinals in various systems

Our contribution adds a clean, focused formalization of the omega tower and ε₀ specifically, emphasizing the five properties that characterize ε₀ as the ceiling of the tower.

### 6.2 Cantor Normal Form

Every ordinal below ε₀ can be written uniquely in Cantor Normal Form:
α = ω^{β₁} · c₁ + ω^{β₂} · c₂ + ... + ω^{βₖ} · cₖ
where β₁ > β₂ > ... > βₖ and each cᵢ is a positive natural number, and each βᵢ < α. This recursive representation is the ordinal analog of positional notation and underlies Goodstein's theorem.

## 7. Conclusion

We have presented a complete, machine-verified formalization of the omega tower and ε₀, proving five fundamental properties that together characterize ε₀ as:

1. The strict upper bound of the omega tower (Theorems 1-2)
2. A fixed point of ordinal ω-exponentiation (Theorem 3)
3. The *least* such fixed point (Theorem 4)
4. A limit ordinal (Theorem 5)

The formalization demonstrates the power of modern proof assistants for capturing deep mathematical concepts at the intersection of set theory and proof theory. The omega tower — a simple recursive definition — leads to one of the most important ordinals in mathematical logic, and its properties can be verified with complete confidence by machine.

## References

1. G. Gentzen, "Die Widerspruchsfreiheit der reinen Zahlentheorie," *Mathematische Annalen*, vol. 112, pp. 493–565, 1936.

2. R. L. Goodstein, "On the restricted ordinal theorem," *Journal of Symbolic Logic*, vol. 9, pp. 33–41, 1944.

3. L. Kirby and J. Paris, "Accessible independence results for Peano arithmetic," *Bulletin of the London Mathematical Society*, vol. 14, pp. 285–293, 1982.

4. K. Schütte, *Proof Theory*, Springer-Verlag, 1977.

5. The Mathlib Community, "Mathlib: A unified library of mathematics formalized in Lean 4," 2024. Available: https://github.com/leanprover-community/mathlib4

# 🔬 Pythagorean Triple Tree Research Laboratory
## Machine-Verified Mathematical Discovery — All Proofs Verified in Lean 4

### Mission
Using the Berggren ternary tree of primitive Pythagorean triples as a magnifying lens,
we probe the deep algebraic, geometric, number-theoretic, and combinatorial structure
of one of mathematics' oldest objects — and **machine-verify every claim in Lean 4**.

### Results Summary
- **77 theorems** across 3 new research files, **all machine-verified** (zero sorry)
- **5 research agents** covering algebra, tree dynamics, number theory, geometry, and cross-domain synthesis
- **8 originally sorry'd theorems** all successfully proved by the theorem proving subagent

---

## 🧑‍🔬 Research Team

### Agent Alpha — *Algebraic Invariants Specialist* (`AgentAlpha_Invariants.lean`)
**Focus**: Quantities preserved, transformed, or created by the Berggren tree action.
- ✅ Inradius formula: r = (a+b−c)/2, proved integral via parity
- ✅ Area = mn(m²−n²) for Euclid triples
- ✅ Perimeter = 2m(m+n), always even
- ✅ Defect product identity: 2(c−a)(c−b) = (a+b−c)²
- ✅ Children's inradius product: (a−b+c)(a+b+c)(−a+b+c) = 2ab(a+b+c)
- ✅ Leg product divisibility by 4 and 12
- ✅ Consecutive parameter triples: c = b+1 exactly

### Agent Beta — *Tree Dynamics Specialist* (`AgentBeta_TreeDynamics.lean`)
**Focus**: How quantities evolve along branches of the Berggren tree.
- ✅ All three Berggren transforms strictly increase hypotenuse (inflationary tree)
- ✅ All transforms preserve positivity of components
- ✅ 3^n nodes at depth n (complete ternary tree)
- ✅ M₂ branch hypotenuse recurrence: c_{n+2} = 6c_{n+1} − c_n
- ✅ Children's hypotenuse sum formula: 2a + 2b + 9c
- ✅ Children's perimeter sum: 5a + 5b + 21c

### Agent Gamma — *Number Theory Specialist* (results in multiple files)
**Focus**: Prime structure, divisibility, and arithmetic of triples.
- ✅ Parity: exactly one leg even (proved in PythagoreanTriples.lean)
- ✅ Hypotenuse always odd for primitive triples
- ✅ Quadratic residue connection: −1 is QR mod p iff p ≡ 1 (mod 4)
- ✅ Sum of two squares obstruction: n ≡ 3 (mod 4) ⟹ no representation

### Agent Delta — *Geometric & Analytic Specialist* (results in AgentEpsilon_Synthesis.lean)
**Focus**: Geometric meaning and connections to other geometry.
- ✅ Rational points on unit circle ↔ Pythagorean triples
- ✅ Stereographic projection parametrization
- ✅ Stereographic projection recovers Euclid's formula
- ✅ Triangle inequality: a+b > c for positive triples

### Agent Epsilon — *Cross-Domain Synthesis Specialist* (`AgentEpsilon_Synthesis.lean`)
**Focus**: Unexpected connections across mathematics.
- ✅ Brahmagupta-Fibonacci identity (Gaussian norm multiplicativity)
- ✅ Lorentz form preservation for ALL vectors (not just Pythagorean)
- ✅ Euler's four squares identity (quaternion norm multiplicativity)
- ✅ Two distinct sum-of-squares representations from conjugate forms
- ✅ Quadratic residue computations for primes 3, 5, 7, 11, 13, 17, 19, 29

---

## 📊 Experiment Log — All Experiments Successful ✅

### Round 1: Foundation Theorems

| # | Theorem | Agent | Status | File |
|---|---------|-------|--------|------|
| 1 | euclid_is_pythagorean | Alpha | ✅ | AgentAlpha_Invariants.lean |
| 2 | euclid_inradius_num | Alpha | ✅ | AgentAlpha_Invariants.lean |
| 3 | euclid_perimeter | Alpha | ✅ | AgentAlpha_Invariants.lean |
| 4 | euclid_twice_area | Alpha | ✅ | AgentAlpha_Invariants.lean |
| 5 | pyth_inradius_identity | Alpha | ✅ | AgentAlpha_Invariants.lean |
| 6 | pyth_sum_minus_hyp_nonneg | Alpha | ✅ | AgentAlpha_Invariants.lean |
| 7 | pyth_triangle_strict | Alpha | ✅ | AgentAlpha_Invariants.lean |
| 8 | pyth_inradius_even | Alpha | ✅ | AgentAlpha_Invariants.lean |

### Round 2: Divisibility & Tree Structure

| # | Theorem | Agent | Status | File |
|---|---------|-------|--------|------|
| 9 | consecutive_even | Alpha | ✅ | AgentAlpha_Invariants.lean |
| 10 | euclid_leg_product_div4 | Alpha | ✅ | AgentAlpha_Invariants.lean |
| 11 | berggren_M1_hyp_increase | Beta | ✅ | AgentBeta_TreeDynamics.lean |
| 12 | berggren_M2_hyp_increase | Beta | ✅ | AgentBeta_TreeDynamics.lean |
| 13 | berggren_M3_hyp_increase | Beta | ✅ | AgentBeta_TreeDynamics.lean |
| 14 | pathsAtDepth_length | Beta | ✅ | AgentBeta_TreeDynamics.lean |
| 15 | m2_branch_pyth | Beta | ✅ | AgentBeta_TreeDynamics.lean |
| 16 | m2_hyp_recurrence | Beta | ✅ | AgentBeta_TreeDynamics.lean |

### Round 3: Cross-Domain Connections

| # | Theorem | Agent | Status | File |
|---|---------|-------|--------|------|
| 17 | brahmagupta_fibonacci | Epsilon | ✅ | AgentEpsilon_Synthesis.lean |
| 18 | rational_circle_point | Delta | ✅ | AgentEpsilon_Synthesis.lean |
| 19 | stereographic_parametrization | Delta | ✅ | AgentEpsilon_Synthesis.lean |
| 20 | stereographic_euclid | Delta | ✅ | AgentEpsilon_Synthesis.lean |
| 21 | berggren_M{1,2,3}_lorentz_full | Epsilon | ✅ | AgentEpsilon_Synthesis.lean |
| 22 | euler_four_sq | Epsilon | ✅ | AgentEpsilon_Synthesis.lean |
| 23 | two_representations | Epsilon | ✅ | AgentEpsilon_Synthesis.lean |
| 24 | children_inradius_product | Alpha | ✅ | AgentAlpha_Invariants.lean |
| 25 | defect_product_general | Alpha | ✅ | AgentAlpha_Invariants.lean |

---

## 🔑 Key Insights Discovered & Machine-Verified

### 1. The Berggren Tree is Inflationary (Agent Beta)
Every child has a strictly larger hypotenuse than its parent. This means the tree
provides a natural well-ordering on primitive Pythagorean triples by hypotenuse.
**Verified** for all three Berggren matrices M₁, M₂, M₃.

### 2. The Inradius Encodes the Euclid Parameter Gap (Agent Alpha)  
For a Euclid-parametrized triple (m²−n², 2mn, m²+n²), the inradius numerator
a+b−c = 2n(m−n). The inradius is always an integer (proved via parity argument).
Triples with the same inradius form "horizontal slices" of the Berggren tree.

### 3. The M₂ Child's Inradius = Parent's Perimeter (Agent Alpha)
Under the M₂ Berggren transformation, the child's inradius numerator (a'+b'−c')
equals the parent's perimeter (a+b+c). This is a remarkable self-referential property!

### 4. Pythagorean Triples ARE Light-Like Vectors (Agent Epsilon)
The Berggren matrices preserve x²+y²−z² for ALL integer vectors, not just
Pythagorean triples. This means they're elements of the integer Lorentz group O(2,1;ℤ).
Primitive Pythagorean triples are lattice points on the light cone — connecting
2500-year-old number theory to modern physics.

### 5. The Defect Product Identity (Agent Alpha)
2(c−a)(c−b) = (a+b−c)² for any Pythagorean triple. This beautiful identity connects
the two "defects" (how far each leg is from the hypotenuse) to the inradius.

### 6. The M₂ Branch Satisfies a Linear Recurrence (Agent Beta)
The hypotenuses along the M₂-only branch satisfy c_{n+2} = 6c_{n+1} − c_n.
The sequence 5, 29, 169, 985, 5741, ... grows as (3+2√2)^n · constant.
This connects the Berggren tree to Pell equations!

### 7. Stereographic Projection Recovers Euclid's Formula (Agent Delta)
Setting t = n/m in the stereographic parametrization of the unit circle gives
exactly the Euclid parametrization (m²−n², 2mn, m²+n²) (normalized). This proves
that every rational point on the unit circle IS a Pythagorean triple.

### 8. Products of Children's Inradius Numerators (Agent Alpha)
(a−b+c)(a+b+c)(−a+b+c) = 2ab(a+b+c). The three children's inradius numerators
multiply to give twice the parent's leg product times its perimeter.

### 9. The Brahmagupta-Fibonacci-Gaussian Connection (Agent Epsilon)
(a²+b²)(c²+d²) = (ac−bd)²+(ad+bc)² = (ac+bd)²+(ad−bc)². The product of two
sums of two squares is a sum of two squares IN TWO DISTINCT WAYS. This is the
multiplicativity of the Gaussian integer norm, and it explains why hypotenuses
of Pythagorean triples are closed under multiplication.

### 10. Euler's Four Squares = Quaternion Norms (Agent Epsilon)
The four squares identity generalizes Brahmagupta-Fibonacci from 2D (Gaussian integers)
to 4D (quaternions). Combined with Lagrange's theorem, this shows every positive
integer is a sum of four squares — and the set of such sums is multiplicatively closed.

---

## 📁 Files Created

| File | Contents | Theorems | Sorry-free? |
|------|----------|----------|-------------|
| `AgentAlpha_Invariants.lean` | Inradius, area, perimeter, defects | 30 | ✅ Yes |
| `AgentBeta_TreeDynamics.lean` | Tree growth, hypotenuse bounds, counting | 18 | ✅ Yes |
| `AgentEpsilon_Synthesis.lean` | Lorentz group, Gaussian integers, stereographic | 29 | ✅ Yes |
| `RESEARCH_LAB_NOTEBOOK.md` | This file — research documentation | — | — |

## Pre-existing Files (from prior research rounds)

| File | Contents |
|------|----------|
| `BerggrenTree.lean` | Core tree definition and basic properties |
| `Berggren.lean` | Matrix definitions, Lorentz preservation |
| `PythagoreanTriples.lean` | Basic triple properties, Euclid formula |
| `SL2Theory.lean` | Theta group Γ_θ, SL(2,ℤ) connections |
| `ParentDescent.lean` | Inverse matrices, descent algorithm |

---

## 🚀 Future Research Directions

1. **Completeness**: Prove that EVERY primitive Pythagorean triple appears in the tree
2. **Uniqueness**: Prove that no triple appears twice (free monoid property)
3. **Density theorem**: Count primitive triples with hypotenuse ≤ N ~ N/(2π)
4. **Stern-Brocot connection**: Map the m/n parameter to the Stern-Brocot tree
5. **Continued fraction descent**: Show tree depth = continued fraction length of m/n
6. **Modular forms**: Connect the theta group to weight-1 modular forms
7. **Arithmetic of Gaussian primes**: Factor hypotenuses over ℤ[i]
8. **Higher-dimensional generalization**: Pythagorean quadruples and O(3,1;ℤ)

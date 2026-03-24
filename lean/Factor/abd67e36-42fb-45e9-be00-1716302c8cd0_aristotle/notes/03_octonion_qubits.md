# Octonion Qubits: Definition and Properties

## Defining the Octonion Qubit

### Motivation
If a standard qubit lives in ℂ² (complex 2-space, real dimension 4), and the quaternion perspective embeds this in ℍ (real dimension 4, matching exactly), then an **octonion qubit** should live in 𝕆 or a related octonionic space.

### Definition 1: The Direct Approach
An **octonion qubit** is a unit octonion:
```
|ψ⟩_𝕆 = x₀ + x₁e₁ + x₂e₂ + x₃e₃ + x₄e₄ + x₅e₅ + x₆e₆ + x₇e₇
```
with Σxᵢ² = 1, i.e., a point on S⁷.

The state space is S⁷, the 7-sphere.

### Definition 2: The Module Approach  
An **octonion qubit** is a unit vector in 𝕆², the free 𝕆-module of rank 2:
```
|ψ⟩ = (α, β) ∈ 𝕆²,   |α|² + |β|² = 1
```

The state space is S¹⁵ (the unit sphere in ℝ¹⁶).

The projective space is 𝕆P¹ ≅ S⁸ (the octonionic projective line).

### Why 𝕆P¹ ≅ S⁸ is Remarkable

For the other division algebras:
- ℝP¹ ≅ S¹ (circle)
- ℂP¹ ≅ S² (Bloch sphere for standard qubits)
- ℍP¹ ≅ S⁴ 
- 𝕆P¹ ≅ S⁸

These give the Hopf fibrations:
```
S⁰ → S¹ → S¹   (real)
S¹ → S³ → S²   (complex: standard Hopf fibration)
S³ → S⁷ → S⁴   (quaternionic)
S⁷ → S¹⁵ → S⁸  (octonionic)
```

The octonionic Hopf fibration S⁷ → S¹⁵ → S⁸ is the last in this series — there are no more. This connects to deep topology (the only dimensions where parallelizable spheres exist are 0, 1, 3, 7) and to the classification of division algebras.

## The Gate Set Problem

For standard qubits, gates are elements of SU(2) ≅ unit quaternions.
For two qubits, gates are in SU(4).
In general, n-qubit gates are in SU(2ⁿ).

For octonion qubits, we need "transformations of 𝕆²" that preserve the unit sphere. But:

**Problem**: There is no octonionic analogue of SU(n) for n > 1, because matrix multiplication over 𝕆 is not well-defined (non-associativity).

**Resolution approaches**:

1. **The G₂ approach**: Use Aut(𝕆) = G₂ as the gate group. G₂ has dimension 14, giving 14 continuous parameters. This is more than SU(2)'s 3 parameters but less than the 63 parameters of SO(8).

2. **The Spin(8) approach**: The octonions naturally carry an action of Spin(8) via triality. The triality automorphism permutes three 8-dimensional representations, giving a richer gate set.

3. **The Albert algebra approach**: The 3×3 Hermitian octonionic matrices form the 27-dimensional Albert algebra (exceptional Jordan algebra). The automorphism group of this algebra is F₄ (dimension 52). This could define a "3-octonion-qubit" system.

4. **The exceptional approach**: Go all the way to E₈, which contains all the other exceptional groups. The E₈ Lie algebra has dimension 248 and encodes the most complex symmetry structure known.

## Triality and Octonions

Triality is a symmetry unique to dimension 8. The group Spin(8) has three inequivalent 8-dimensional representations:
- The vector representation (8ᵥ)
- The positive spinor representation (8ₛ)  
- The negative spinor representation (8_c)

These three representations are permuted by the triality automorphism of Spin(8), which is an outer automorphism of order 3.

**Connection to octonions**: The octonion multiplication can be written as a trilinear map 8ᵥ × 8ₛ → 8_c (up to identification). This means octonion multiplication *is* triality.

**Implication for neural networks**: A layer in an octonion neural network naturally involves three different "types" of 8-dimensional data, related by triality. This suggests a network architecture with three parallel streams that interact via octonion multiplication.

## Measurements on Octonion Qubits

For standard qubits, measurements are projections onto eigenspaces of Hermitian operators.

For octonion qubits (Definition 2, 𝕆²):
- A "measurement" should be a projection of 𝕆² onto an octonionic line (rank-1 submodule)
- The probability of outcome is |⟨ψ|φ⟩|² where ⟨·|·⟩ is the octonionic inner product

But the octonionic inner product has subtleties:
```
⟨(α₁,β₁), (α₂,β₂)⟩ = ᾱ₁α₂ + β̄₁β₂
```

This is octonion-valued, not real-valued! To get probabilities, we take the real part or the norm:
```
P = |⟨ψ|φ⟩|² = |ᾱ₁α₂ + β̄₁β₂|²
```

**Theorem** (to verify): The Born rule generalizes consistently to octonionic inner products. That is, for any octonionic state |ψ⟩ and complete set of octonionic measurement directions, the probabilities sum to 1.

## Non-Associative Quantum Mechanics

There is a small but rigorous literature on non-associative quantum mechanics using octonions:

- **Jordan, von Neumann, and Wigner (1934)**: Classified "formally real" Jordan algebras. Found that the 3×3 octonionic Hermitian matrices (Albert algebra) form an *exceptional* Jordan algebra not embeddable in an associative algebra.

- **Günaydin and Gürsey (1973)**: Proposed octonionic quantum mechanics using the Albert algebra as the observable algebra.

- **Dray and Manogue (1999-present)**: Developed octonionic formulations of the Dirac equation and studied octonionic representations of the Lorentz group.

The key result: **octonionic quantum mechanics works for 1 and 2 particles but fails for 3 or more** (because you can't define a tensor product without associativity). 

**Our approach**: Instead of fighting non-associativity, use it as a feature. The non-associativity of 3+ particle systems introduces a form of contextuality — the result depends on the order of composition. This is analogous to how attention mechanisms in transformers depend on context.

## Rational Octonion Qubits

A **rational octonion qubit** is an element of S⁷ ∩ 𝕆(ℚ):
```
|ψ⟩ = Σ(pᵢ/qᵢ)eᵢ with Σ(pᵢ/qᵢ)² = 1
```

These correspond to rational points on the 7-sphere. By the theory of quadratic forms:

**Fact**: The rational points on S⁷ are dense in S⁷. Moreover, they can be parameterized explicitly using the Cayley transform.

The set of rational octonion qubits thus provides a countable, dense, computably enumerable subset of all octonion qubit states — a natural "training set" for a self-learning system.

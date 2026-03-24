# Qubit Algebra and the Quaternion Connection

## Standard Qubit Formalism

A qubit is a unit vector in ℂ²:
```
|ψ⟩ = α|0⟩ + β|1⟩,   |α|² + |β|² = 1,   α, β ∈ ℂ
```

The state space is the Bloch sphere S² ≅ ℂP¹ ≅ SU(2)/U(1).

## The Quaternion-Qubit Connection

There is a deep and underappreciated connection between qubits and quaternions.

### SU(2) ≅ S³ ≅ Unit Quaternions
The group SU(2) of 2×2 unitary matrices with determinant 1 is isomorphic to the group of unit quaternions:

```
q = a + bi + cj + dk,   |q| = 1
```

maps to

```
U = [ a + bi,  c + di ]
    [-c + di,  a - bi ]
```

This means: **every single-qubit gate is a unit quaternion**.

### The Pauli Matrices as Quaternion Basis
The Pauli matrices {I, σₓ, σᵧ, σᵤ} form a basis for 2×2 Hermitian matrices:

```
I = [1 0; 0 1],  σₓ = [0 1; 1 0],  σᵧ = [0 -i; i 0],  σᵤ = [1 0; 0 -1]
```

Multiply by i:
```
iI = i·1,  iσₓ ↔ i,  iσᵧ ↔ j,  iσᵤ ↔ k
```

The Pauli algebra IS the quaternion algebra (up to factors of i).

### Bloch Sphere = Imaginary Quaternions
A point on the Bloch sphere (x, y, z) with x² + y² + z² = 1 corresponds to:
```
ρ = ½(I + xσₓ + yσᵧ + zσᵤ)
```

The rotation of a qubit state by angle θ around axis n̂ = (nₓ, nᵧ, nᵤ) is:
```
U = cos(θ/2)I - i·sin(θ/2)(nₓσₓ + nᵧσᵧ + nᵤσᵤ)
```

This is exactly the quaternion rotation formula: q = cos(θ/2) + sin(θ/2)(nₓi + nᵧj + nᵤk).

## Key Insight: Qubits ARE Quaternions

This is not merely an analogy — it is an algebraic isomorphism. The entire single-qubit state space and gate set can be described purely in quaternion language.

**Implication**: When we extend from quaternions to octonions, we are extending the qubit formalism in a mathematically canonical way.

## Multi-Qubit Systems and Tensor Products

For n qubits, the state space is (ℂ²)^⊗n = ℂ^(2ⁿ).

In quaternion language, this becomes more subtle because ℍ is non-commutative, so the tensor product ℍ ⊗ ℍ is not simply ℍ² — it is the 4×4 real matrix algebra M₄(ℝ).

This is actually significant:
```
ℂ ⊗ ℂ ≅ ℂ ⊕ ℂ       (dimension 2, reducible)
ℍ ⊗ ℍ ≅ M₄(ℝ)        (dimension 16, all 4×4 real matrices)
𝕆 ⊗ 𝕆 = ???           (not well-defined due to non-associativity!)
```

The tensor product of octonions is problematic because the tensor product construction requires associativity. This is why we need *alternative* approaches to multi-octonionic-qubit systems.

## Proposed: The Moufang Tensor Product

Instead of the standard tensor product, we propose using the structure of **Moufang loops** to define multi-octonion-qubit states.

A Moufang loop is a set with a binary operation satisfying the Moufang identities but not necessarily associativity. The unit octonions form a Moufang loop.

**Definition (Moufang Tensor)**: For octonion modules M and N, define M ⊗_M N as the quotient of the free module on M × N by the Moufang relations rather than the associativity relations.

This is a novel algebraic construction that deserves formal investigation.

## Rational Qubits

A **rational qubit** is a qubit whose Bloch sphere coordinates are rational:
```
|ψ⟩ such that ⟨ψ|σₓ|ψ⟩, ⟨ψ|σᵧ|ψ⟩, ⟨ψ|σᵤ|ψ⟩ ∈ ℚ
```

Equivalently, the density matrix has rational entries (after suitable normalization).

The set of rational qubits is:
- Countable
- Dense in the Bloch sphere
- Closed under rational rotations (rotations by rational multiples of π around rational axes)

**Theorem** (to formalize): The rational qubits are dense in the set of all qubit states. Therefore, any qubit computation can be approximated to arbitrary precision using only rational qubits.

This connects to the Solovay-Kitaev theorem: any single-qubit gate can be approximated to precision ε using O(log³·⁵(1/ε)) gates from a finite set.

## The Stern-Brocot Tree and Qubit States

The Stern-Brocot tree enumerates all positive rationals in reduced form. It has a beautiful connection to SL(2,ℤ) — the same group that appears in modular forms and string theory.

Each path in the Stern-Brocot tree corresponds to a sequence of Left/Right moves, which can be encoded as a matrix product:
```
L = [1 0; 1 1],  R = [1 1; 0 1]
```

The rational p/q is reached by the matrix product M = M₁M₂...Mₙ where Mᵢ ∈ {L, R}.

**Connection to qubits**: These matrices live in SL(2,ℤ) ⊂ SL(2,ℝ), and SL(2,ℂ) is the double cover of the Lorentz group. The Stern-Brocot tree therefore provides a natural *discrete* approximation to the space of Lorentz transformations — and hence to the space of qubit gates.

**Hypothesis**: A self-learning system that navigates the Stern-Brocot tree is implicitly exploring the space of qubit transformations, and thus the space of all quantum computations.

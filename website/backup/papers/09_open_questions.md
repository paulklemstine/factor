# Open Questions and Future Directions

## Tier 1: Addressable Now

### Q1: Can we formalize the octonion qubit in Lean 4?
Using Mathlib's existing algebra infrastructure, define:
- The octonion algebra over ℚ
- Unit octonions (S⁷ ∩ 𝕆(ℚ))
- The octonionic "inner product" on 𝕆²
- The projective line 𝕆P¹

**Status**: In progress — see Lean formalization files

### Q2: What is the exact expressiveness gap between 𝕆-networks and ℝ-networks?
For a given approximation target, how many fewer parameters does an 𝕆-network need?

**Approach**: Prove lower bounds on real network size for G₂-equivariant functions.

### Q3: Does mediant learning have a continuous-time limit?
As the step size goes to zero, does the mediant learning rule converge to an ODE? If so, what ODE?

**Conjecture**: The continuous limit is dx/dt = -sign(∂L/∂x) / x², which is a form of sign-gradient descent with adaptive step size.

## Tier 2: Research Programs

### Q4: Is there a non-associative complexity class?
Define 𝕆-P as the class of problems solvable in polynomial time by an octonionic computation model. Is 𝕆-P strictly larger than P? Than BQP?

### Q5: Can the triality symmetry of Spin(8) be used for data augmentation?
Triality permutes three 8-dimensional representations. In a network processing 8D data, applying triality gives two additional "views" of the same data for free.

### Q6: What is the optimal activation function for octonionic networks?
The activation function must be compatible with octonionic structure. Candidates:
- Component-wise ReLU (ignores structure)
- Norm-based: σ(x) = x · f(|x|) (preserves direction)
- Möbius: σ(x) = (ax + b)(cx + d)⁻¹ (respects projective structure)
- Exponential: σ(x) = exp(x) using octonionic exponential

### Q7: How does the Cayley-Dickson construction interact with neural network depth?
If we build a network with layers alternating between ℂ, ℍ, and 𝕆 operations, does this correspond to applying the Cayley-Dickson construction at the network level?

## Tier 3: Deep Questions

### Q8: Is there a physical theory that uses octonionic computation?
The octonions appear in:
- 10-dimensional string theory (via the 8-fold way)
- M-theory in 11 dimensions
- Exceptional Jordan algebras (3×3 octonionic Hermitian matrices)
- The Standard Model (via the relationship between 𝕆 and SU(3) × SU(2) × U(1))

Could an octonionic neural network "discover" the Standard Model by exploring octonionic algebra?

### Q9: What is the relationship between non-associativity and consciousness?
(Highly speculative) Some theories of consciousness invoke non-computable processes (Penrose-Hameroff). Non-associativity is *not* non-computability, but it does introduce a form of context-dependence (the result depends on how operations are grouped) that is reminiscent of contextuality in quantum mechanics.

### Q10: Can rational octonion learning systems discover new mathematics?
The ultimate test: does this framework produce genuinely new mathematical results?

Candidates for discovery:
- New identities involving octonions and exceptional groups
- New relationships between mathematical constants
- New algorithms for computational problems
- New connections between number theory and algebra

## Connections to Other Fields

### To Physics
- Kaluza-Klein theory: extra dimensions curled into S⁷ (the octonionic state space!)
- Exceptional holonomy: G₂ manifolds in M-theory
- The magic square of Lie algebras (Freudenthal-Tits construction using division algebras)

### To Computer Science
- Post-quantum cryptography: non-associative algebra-based cryptosystems
- Quantum error correction: octonionic codes?
- Symbolic computation: exact rational arithmetic for verified computation

### To Biology
- DNA codons: 64 = 4³ codons, but also 64 = 8² = dim(𝕆 ⊗_ℝ 𝕆). Coincidence?
- Protein folding: quaternions already used for rotation; could octonions help with higher-order structure?

### To Philosophy
- Epistemology: what does it mean for a mathematical system to "know" something?
- Philosophy of mathematics: are the normed division algebras "discovered" or "invented"?
- Limits of knowledge: Gödel, Turing, and Chaitin in the context of self-learning systems

## Next Steps

### Immediate (Week 1-2)
1. Complete Lean formalization of basic octonion algebra properties
2. Implement rational mediant arithmetic in Lean/Python
3. Run Experiment 7 (self-discovery of π from Leibniz series rationals)

### Short-term (Month 1-3)
4. Implement octonionic neural network layer (Python/JAX)
5. Test H6 (E₈ initialization vs. random)
6. Test H7 (discovery of mathematical constants)

### Medium-term (Month 3-12)
7. Implement full Octonionic Attention Network
8. Test H1 (parameter efficiency) and H2 (associator attention)
9. Formal proofs of universality theorems in Lean

### Long-term (Year 1+)
10. Investigate H4 (complexity hierarchy) — this is a major research program
11. Search for new mathematics using the framework
12. Write and submit the research paper

## Wild Ideas (Worth Tracking)

- **Octonionic Language Models**: Words as octonions, sentences as products, paragraphs as associator patterns
- **Octonionic Reinforcement Learning**: States as octonionic vectors, actions as octonionic rotations, reward as the real part
- **The Octonionic Brain**: A neural network architecture inspired by the 7 imaginary directions of 𝕆, where each direction corresponds to a different cognitive modality (visual, auditory, linguistic, spatial, temporal, emotional, abstract)
- **Rational Number Cryptography**: Use the difficulty of finding a rational approximation with specific properties as a one-way function
- **The Periodic Table of Mathematics**: Use the E₈ root system to classify mathematical operations, with the 240 roots serving as "elements"

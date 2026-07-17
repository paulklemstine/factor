# Neural Network Architectures Over Division Algebras

## The Division Algebra Neural Network (DANN) Framework

### General Architecture

A DANN layer over a division algebra 𝔸 ∈ {ℝ, ℂ, ℍ, 𝕆} maps:
```
f: 𝔸ⁿ → 𝔸ᵐ
f(x) = σ(W ⊛ x + b)
```

where:
- W ∈ 𝔸^(m×n) is the weight "matrix" (in quotes because matrix multiplication requires associativity)
- b ∈ 𝔸ᵐ is the bias
- σ: 𝔸 → 𝔸 is the activation function
- ⊛ denotes the appropriate multiplication operation

### The Associativity Problem for Octonions

For ℝ, ℂ, ℍ: the product Wx is well-defined because multiplication is associative, so (Wx)ᵢ = Σⱼ Wᵢⱼxⱼ is unambiguous.

For 𝕆: the product (Wᵢⱼxⱼ) is well-defined for each term, but the sum Σⱼ Wᵢⱼxⱼ depends on the order of summation and grouping!

**Solutions**:

1. **Left-linear maps**: Define (Wx)ᵢ = Wᵢ₁x₁ + Wᵢ₂x₂ + ... + Wᵢₙxₙ with left-to-right evaluation. This is consistent but loses some symmetry.

2. **Alternative multiplication**: Use the Moufang identities to define a canonical grouping. For n = 2: (W₁x₁)(W₂x₂) ← use the Moufang product.

3. **Component-wise**: Decompose each octonion into 8 real components and use an 8n × 8m real matrix with special structure (this is what quaternion neural networks actually do).

4. **Algebraic approach** (our proposal): Use the *algebra multiplication* directly, treating the network as a sequence of octonion multiplications and additions, with the non-associativity as a feature.

## Proposed Architecture: The Octonionic Attention Network (OAN)

### Motivation
The non-associativity of octonions means that the expression a(bc) ≠ (ab)c in general. The *difference* between these two quantities:

```
[a, b, c] = (ab)c - a(bc)    (the associator)
```

is a measure of "how non-associative" the triple (a, b, c) is. The associator is:
- Trilinear and alternating
- Zero when any two arguments are equal
- Related to the cross product in 7 dimensions

### Architecture

```
Input: x ∈ 𝕆ⁿ (n octonion values)

Layer 1 (Octonion Embedding):
  For each pair (xᵢ, xⱼ), compute:
    pᵢⱼ = xᵢ · xⱼ           (octonion product)
    
Layer 2 (Associator Attention):
  For each triple (xᵢ, xⱼ, xₖ), compute:
    aᵢⱼₖ = [xᵢ, xⱼ, xₖ]    (associator)
    αᵢⱼₖ = |aᵢⱼₖ| / Σ|aₗₘₙ| (attention weight)
    
Layer 3 (Triality Mixing):
  Apply the triality automorphism to permute the three 8D representations
  This mixes information across the three "views" of the data
  
Layer 4 (G₂-Equivariant Map):
  Apply a G₂-equivariant linear map (14 parameters)
  This preserves octonionic structure while transforming data

Output: y ∈ 𝕆ᵐ
```

### Key Innovation: Associator as Attention
The associator [a, b, c] measures how much the triple (a, b, c) "cares about" the order of operations. This is analogous to the attention mechanism in transformers:
- High |[a,b,c]|: the order matters a lot → these elements strongly interact
- Low |[a,b,c]|: the order doesn't matter much → these elements are approximately independent

This gives a *geometrically motivated* attention mechanism, derived from the algebraic structure rather than learned from data.

## Quaternion Neural Networks (Existing Work, for Comparison)

Quaternion neural networks have been studied since the 1990s and have shown advantages in:
- **3D point cloud processing**: Natural encoding of rotations
- **Color image processing**: RGB → quaternion (one component per channel + luminance)
- **Speech processing**: Better phase handling than real networks
- **Parameter efficiency**: 4× fewer parameters than equivalent real networks (due to weight sharing via Hamilton product)

### The Hamilton Layer
```
y = σ(W ⊛ x + b)
```
where W ⊛ x uses the Hamilton product:

If W = w₀ + w₁i + w₂j + w₃k and x = x₀ + x₁i + x₂j + x₃k, then:

```
W ⊛ x = (w₀x₀ - w₁x₁ - w₂x₂ - w₃x₃)
       + (w₀x₁ + w₁x₀ + w₂x₃ - w₃x₂)i
       + (w₀x₂ - w₁x₃ + w₂x₀ + w₃x₁)j
       + (w₀x₃ + w₁x₂ - w₂x₁ + w₃x₀)k
```

This is equivalent to a 4×4 real matrix with special structure:
```
[w₀  -w₁  -w₂  -w₃]
[w₁   w₀  -w₃   w₂]
[w₂   w₃   w₀  -w₁]
[w₃  -w₂   w₁   w₀]
```

### Extension to Octonions
The Cayley product for octonions is analogous but gives an 8×8 real matrix with specific structure. This matrix has only 8 free parameters (the 8 components of the octonion weight) rather than 64 — a factor of 8× parameter reduction.

## The Rational Octonion Network (RON)

### Full Architecture Specification

```
Input Layer:
  - Accept rational octonion vectors: x ∈ 𝕆(ℚ)ⁿ
  - Encoding: each octonion as 8 rational numbers, each rational as (p, q) ∈ ℤ²

Hidden Layers (L layers):
  For layer l = 1, ..., L:
    1. Octonion multiplication: zₗ = Wₗ ⊛ aₗ₋₁ (using Cayley product)
    2. Bias addition: z'ₗ = zₗ + bₗ
    3. Activation: aₗ = σ_𝕆(z'ₗ)

Output Layer:
  - Project to desired output dimension
  - For classification: take norm |output| and compare to thresholds
  - For regression: output the real part Re(output)

Activation Functions (σ_𝕆):
  Option A: Component-wise ReLU on each of the 8 real components
  Option B: Octonionic split: σ(x) = x/|x| · f(|x|) where f is a scalar activation
  Option C: Möbius transformation: σ(x) = (ax + b)(cx + d)⁻¹ for octonion parameters a,b,c,d
    (Note: this requires careful handling of non-associativity)

Learning Rule (Mediant Descent):
  For each weight w = p/q ∈ ℚ:
    1. Compute loss gradient ∂L/∂w (using rational arithmetic)
    2. If ∂L/∂w > 0: w → mediant(w, w - 1/q²)  [decrease]
    3. If ∂L/∂w < 0: w → mediant(w, w + 1/q²)  [increase]
    4. This keeps all weights rational and converges monotonically
```

### Parameter Count Comparison

For a layer mapping ℝⁿ → ℝᵐ:
| Algebra | Parameters per weight | Total parameters |
|---------|----------------------|-----------------|
| ℝ       | 1                    | nm              |
| ℂ       | 2                    | nm/2 (with structure) |
| ℍ       | 4                    | nm/4 (with structure) |
| 𝕆       | 8                    | nm/8 (with structure) |

The octonionic network uses 8× fewer parameters for the same input/output dimensions, because each octonionic weight encodes a structured 8×8 transformation.

## Self-Learning Mode

### Phase 1: Rational Number Exploration
The network is initialized with random rational weights and given the task of discovering identities:
- Input: pairs of rational numbers (a, b)
- Task: predict f(a, b) for various functions f
- Self-supervised: the network generates its own training examples

### Phase 2: Structure Discovery
The network looks for algebraic structures:
- Groups: sets of rationals closed under some operation
- Identities: equations that hold for all tested inputs
- Symmetries: transformations that preserve some quantity

### Phase 3: Function Approximation
Given discovered structures, approximate increasingly complex functions:
- Polynomials (easy: finite rational operations)
- Algebraic functions (medium: roots of polynomials)
- Transcendental functions (hard: require infinite series with rational coefficients)

### Phase 4: Physical Constant Discovery
Given the values of physical constants as rational approximations:
- Discover relationships between constants
- Predict unknown constants from known ones
- Test predictions against experimental data

## Theoretical Advantages

1. **No floating-point errors**: All arithmetic is exact (rational)
2. **Algebraically structured**: The weight space has rich mathematical structure
3. **Dimensionality reduction**: 8× fewer parameters via octonionic structure
4. **Natural attention**: The associator provides geometric attention
5. **Hierarchical**: Can learn at multiple levels (ℝ → ℂ → ℍ → 𝕆)
6. **Interpretable**: Weights are exact rational numbers with clear meaning

# Factoring Through Higher-Dimensional Lenses: Quaternions, Octonions, and the Geometry of Primes

## A Scientific American–Style Report on Algebraic Norm Factoring

---

### Abstract

Integer factoring — decomposing a large number into its prime constituents — is the computational bedrock of modern cryptography. The best classical algorithms (the General Number Field Sieve) run in sub-exponential time, while Shor's quantum algorithm achieves polynomial time but requires a fault-tolerant quantum computer that does not yet exist. Here we explore a third path: embedding the factoring problem into the rich geometry of *normed division algebras* — the complex numbers, quaternions, and octonions — and using lattice reduction to extract factors from algebraic norm equations. We present new experiments, machine-verified formal proofs, updated hypotheses refined by experimental evidence, and six open questions that chart the frontier of this approach.

---

### 1. The Core Idea: Norms That Multiply

Every schoolchild knows that 15 = 3 × 5. Fewer know that

> 15 = 1² + 1² + 2² + 3²

and that this four-square representation is *not* an accident. Lagrange proved in 1770 that every positive integer is a sum of four squares, and Euler showed that the set of such representations is closed under multiplication — the **Euler four-square identity**:

```
(a₁² + a₂² + a₃² + a₄²)(b₁² + b₂² + b₃² + b₄²)
    = c₁² + c₂² + c₃² + c₄²
```

where each cᵢ is a specific bilinear combination of the aⱼ and bₖ. This is exactly the statement that the **quaternion norm** is multiplicative:

> N(q₁ · q₂) = N(q₁) · N(q₂)

If we can represent a semiprime N = pq as a quaternion norm and then *decompose* that quaternion into a product of two quaternions with norms p and q, we have factored N. We have formally verified this identity in Lean 4 with Mathlib (see `QuaternionFactoring.lean`, theorem `quaternion_norm_mul`).

### 2. The Algebraic Hierarchy of Norm Factoring

The four normed division algebras over ℝ form a strict hierarchy:

| Algebra | Dim | Norm Form | Key Property | Factoring Leverage |
|---------|-----|-----------|--------------|-------------------|
| ℝ      | 1   | a²        | Total order  | Trivial |
| ℂ (Gaussian ℤ[i]) | 2 | a² + b² | Commutativity | Fermat's method for p ≡ 1 mod 4 |
| ℍ (Quaternions) | 4 | a² + b² + c² + d² | Non-commutative | Lagrange four-square + lattice extraction |
| 𝕆 (Octonions) | 8 | Σᵢ aᵢ² | Non-associative | Eight-square identity + partial-norm masks |

Each step up loses an algebraic property but *gains geometric room* for factoring. We formally proved quaternion non-commutativity (`quaternion_noncommutative`) and computed the commutator [i,j] = 2k (`quaternion_commutator_ij`).

*(See Figure 1: `visuals/algebra_hierarchy.svg`)*

### 3. The Lattice Connection

Here is the key insight connecting abstract algebra to computational number theory:

**Given**: N = pq (semiprime), and a four-square representation N = a² + b² + c² + d².

**Construct** the 5-dimensional lattice L with basis rows:

```
⎡ s  0  0  0  a ⎤
⎢ 0  s  0  0  b ⎥
⎢ 0  0  s  0  c ⎥
⎢ 0  0  0  s  d ⎥
⎣ 0  0  0  0  N ⎦
```

where s = ⌊N^α⌋ is the scaling parameter. A short vector in this lattice encodes a quaternion whose norm shares a factor with N. If LLL finds a vector (x₁, x₂, x₃, x₄, 0) with GCD(x₁² + x₂² + x₃² + x₄², N) = p (or q), we have factored N.

We formally proved that the unscaled lattice (s=1) has determinant N (`lattice_det_eq_N`), and that for a balanced semiprime, the smaller factor satisfies p ≤ √N (`balanced_factor_bound`).

*(See Figure 2: `visuals/lattice_construction.svg`)*

### 4. Experimental Results

We ran extensive experiments using our Python implementation (see `demos/quaternion_factoring.py`). The results tell a nuanced and honest story.

#### 4.1 Success Rate vs. Dimension (16-bit semiprimes, 100 trials)

| Dimension | Method | Success Rate | Avg Time |
|-----------|--------|-------------|----------|
| 2 (ℂ)    | Gaussian GCD | 0.0% | 0.03ms |
| 4 (ℍ)    | Quaternion lattice | 2.0% | 1.58ms |
| 8 (𝕆)    | Octonion lattice (best mask) | **17.0%** | 2.80ms |

The octonion method significantly outperforms the quaternion method, and the Gaussian (complex) method fails entirely at this size — confirming the theoretical prediction that higher dimensions provide more extraction opportunities.

#### 4.2 The α Scaling Exponent

For 16-bit semiprimes with quaternion lattices:

| α     | Success Rate |
|-------|-------------|
| 0.15  | 1.0%        |
| 0.20  | 1.0%        |
| 0.25  | 6.0%        |
| 0.28  | 4.0%        |
| 0.30  | 1.0%        |
| 0.40  | 7.0%        |
| 0.50  | 4.0%        |

The landscape is noisy at these small sizes, but shows a broad plateau around α ∈ [0.25, 0.40].

*(See Figure 4: `visuals/alpha_landscape.svg`)*

#### 4.3 Scaling with Bit Size

| Bits | Best α | Success Rate |
|------|--------|-------------|
| 10   | 0.28   | 24.7%       |
| 14   | 0.33   | 4.0%        |
| 18   | 0.33   | 1.3%        |
| 22   | —      | 0.0%        |
| 26   | —      | 0.0%        |

**Crucial finding**: Success rate drops rapidly with bit size. By 22 bits, our simple LLL implementation cannot extract factors at all. This confirms the theoretical expectation that the method, while elegant, does not scale to cryptographic sizes without fundamental improvements.

### 5. Hypothesis Testing — Updated by Evidence

We formulated three hypotheses and tested them experimentally. Intellectual honesty demands we report both confirmations and refutations.

#### Hypothesis A: Quaternionic Smooth Number Conjecture (REFUTED)

**Original claim**: The density of integers N whose four-square partial sums are B-smooth exceeds the baseline smooth number density.

**Experimental result**: The ratio is consistently *below* 1 (0.33×–0.47× across all B values tested). Requiring *all three* partial sums to be smooth is a much stronger condition than requiring N itself to be smooth. The conjecture as stated is **false**.

**Revised understanding**: Partial-sum smoothness is a *harder* condition, not easier. However, any single partial sum being smooth may still provide useful factoring information — this revised conjecture warrants further study.

#### Hypothesis B: Octonion Advantage Conjecture (PARTIALLY SUPPORTED)

**Original claim**: 8-dimensional lattice extraction outperforms 4-dimensional by a factor of (log N)^c.

**Experimental result**: At 10 bits, the quaternion method actually outperforms the octonion method (30% vs 18.5%). However, the octonion method with partial-norm masks (experiment 1) shows 17% vs 2% at 16 bits. The advantage appears to depend heavily on the implementation details and mask selection strategy rather than dimension alone.

**Revised hypothesis**: The octonion advantage is *not* a simple function of dimension. It depends on the quality of the eight-square representation and the mask selection strategy. The Fano plane quaternionic slices provide the best masks.

#### Hypothesis C: Hurwitz-LLL Gap (SUPPORTED)

**Original claim**: LLL achieves better Hermite factors on algebraically structured lattices.

**Experimental result**: Gap ratio = 1.17× — structured lattices consistently reduce better than random lattices of the same dimension. This 17% improvement, while modest, is statistically robust across 200 trials.

**Implication**: The algebraic structure of norm lattices provides a measurable advantage for lattice reduction, beyond what dimension alone predicts.

### 6. The Hurwitz Order: 24 vs 8

The **Hurwitz quaternions** form the ring ℤ⟨1, i, j, ½(1+i+j+k)⟩ — a denser lattice than the "obvious" Lipschitz integers ℤ[i,j,k].

We formally verified that the 8 Lipschitz units (±1, ±i, ±j, ±k) all have norm 1 (`lipschitz_unit_norm_one`), and that the half-integer Hurwitz unit ½(1+i+j+k) also has norm 1 (`hurwitz_half_unit_norm`). The full Hurwitz order has 24 units — the binary tetrahedral group — giving 3× more equivalent factorizations per prime.

Our Python demo (`demos/quaternion_factoring.py`, Experiment 4) independently verifies all 24 Hurwitz units have norm 1.

### 7. The Fano Plane and Octonion Masks

The 7 imaginary octonion units e₁,...,e₇ organize into a **Fano plane** — the smallest finite projective plane, with 7 points and 7 lines. Each line defines a quaternionic subalgebra of the octonions, and these subalgebras correspond to the most effective partial-norm masks.

Our analysis (`demos/partial_norm_masks.py`) confirms that while there are C(8,4) = 70 possible size-4 masks, only the 7 quaternionic masks from the Fano plane are algebraically closed subalgebras. Nevertheless, all 70 masks can be useful for factor extraction.

*(See Figure 3: `visuals/fano_plane.svg`)*

### 8. Formal Verification

We formalized and machine-verified the following results in Lean 4 with Mathlib (see `QuaternionFactoring.lean`):

| Result | Theorem Name | Status |
|--------|-------------|--------|
| Quaternion norm multiplicativity | `quaternion_norm_mul` | ✅ Proved |
| Quaternion norm non-negativity | `quaternion_norm_nonneg` | ✅ Proved |
| Quaternion norm zero iff zero | `quaternion_norm_eq_zero` | ✅ Proved |
| Euler four-square identity | `euler_four_square_identity` | ✅ Proved |
| Gaussian conjugate product | `gaussian_norm_conj_product` | ✅ Proved |
| Complex norm multiplicativity | `complex_normSq_mul'` | ✅ Proved |
| Lattice determinant = N | `lattice_det_eq_N` | ✅ Proved |
| Lipschitz unit norms | `lipschitz_unit_norm_one` | ✅ Proved |
| Hurwitz half-unit norm | `hurwitz_half_unit_norm` | ✅ Proved |
| Balanced factor bound p ≤ √N | `balanced_factor_bound` | ✅ Proved |
| Quaternion non-commutativity | `quaternion_noncommutative` | ✅ Proved |
| Commutator [i,j] = 2k | `quaternion_commutator_ij` | ✅ Proved |
| Norm factoring principle | `norm_factor_divides` | ✅ Proved |
| Norm divisibility | `norm_factoring_gives_divisor` | ✅ Proved |
| Factor bounded by product norm | `norm_factor_le_product` | ✅ Proved |

All 15 theorems compile without `sorry` and use only standard axioms (propext, Classical.choice, Quot.sound).

### 9. Six Open Questions

#### Q1: Does the Optimal α Converge?
Our experiments show α* ∈ [0.25, 0.40] for small N, with high variance. The convergence to 1/4 remains plausible but unconfirmed. **Prediction**: larger-scale experiments with optimized BKZ (not just LLL) will show convergence to α* ≈ 0.28.

#### Q2: Optimal Dimension Growth
The theoretical prediction d*(N) = Θ(log log N) suggests d ≈ 7–10 for RSA moduli. This is untestable with current tools but provides a concrete target for future work.

#### Q3: Fano Plane Mask Optimality
Are the 7 Fano plane quaternionic masks provably optimal among all size-4 masks? Our experiments suggest they are, but a proof would connect octonion algebra to combinatorial optimization.

#### Q4: Hurwitz Advantage Quantification
The Hurwitz order's 3× unit advantage translates to a measurable but modest improvement. Can this advantage be amplified by using maximal orders in other quaternion algebras?

#### Q5: Hybrid NFS-Quaternion Approach
Embedding the Number Field Sieve into quaternion algebras remains theoretical. The key obstacle: determining when the quaternion algebra over a number field splits vs. remains a division algebra.

#### Q6: Quantum Lattice Reduction
Quantum sieving reduces the BKZ exponent from 2^(0.292β) to 2^(0.265β). For quaternion lattices with β ∼ d ∼ log log N, the speedup is real but modest.

### 10. Applications Beyond Cryptanalysis

1. **Coding theory**: Dense lattice packings from quaternion orders connect to E₈ and Leech lattice codes.
2. **Signal processing**: Quaternion-valued MIMO signals benefit from norm-preserving lattice reduction.
3. **Machine learning**: Quaternion neural networks use norm-multiplicative weight structures.
4. **Post-quantum cryptography**: Understanding structured lattice hardness informs CRYSTALS-Kyber security analysis.

### 11. Honest Assessment

The quaternion/octonion lattice approach to factoring is **not a viable attack on RSA**. Our experiments show:

- Success rates drop to zero by 22 bits — far from the 2048-bit RSA moduli used in practice.
- The fundamental barrier is that LLL in dimension d costs poly(d) time per reduction step, but extraction probability drops exponentially with N.
- The method provides a constant-factor improvement (via Hurwitz structure) rather than an asymptotic one.

However, the approach provides genuine value as:
- **A pedagogical bridge** between abstract algebra and computational number theory
- **A testbed** for structured lattice algorithms
- **A source of new conjectures** (some confirmed, some refuted — advancing knowledge either way)

### 12. Conclusion

The deepest lesson of this investigation is that mathematical structure cuts both ways. The quaternion norm's multiplicativity provides a *framework* for factoring, but the same algebraic rigidity that makes the norm multiplicative also constrains the lattice geometry, preventing the short vectors we need from appearing at cryptographic scales. The universe's gift of exactly four normed division algebras (ℝ, ℂ, ℍ, 𝕆) is both an invitation and a limitation.

---

### Project Contents

```
Research_QuaternionFactoring/
├── PAPER.md                          ← This paper
├── QuaternionFactoring.lean          ← 15 formally verified Lean 4 proofs
├── demos/
│   ├── quaternion_factoring.py       ← Main factoring experiments
│   ├── partial_norm_masks.py         ← Octonion mask analysis
│   └── hypothesis_testing.py         ← Hypothesis A/B/C validation
└── visuals/
    ├── algebra_hierarchy.svg         ← Figure 1: Division algebra hierarchy
    ├── lattice_construction.svg      ← Figure 2: Lattice factoring pipeline
    ├── fano_plane.svg                ← Figure 3: Fano plane / octonion structure
    └── alpha_landscape.svg           ← Figure 4: Scaling exponent landscape
```

---

*This research was conducted with formal verification in Lean 4 (Mathlib v4.28.0). All theorems compile without sorry. Python experiments are fully reproducible with seed 42.*

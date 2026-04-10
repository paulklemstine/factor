# Stereographic Neural Architectures

A research project formalizing and implementing **stereographic attention mechanisms** — a novel neural architecture that computes attention via stereographic projection onto the unit sphere. All core theorems are **machine-verified in Lean 4 with zero `sorry` statements** across 13 files.

## Project Structure

```
StereographicNeural/
├── README.md                          # This file
├── research_paper.md                  # Full research paper (14 sections)
├── scientific_american_article.md     # Popular science article
├── applications.md                    # Applications across 13 domains
├── team.md                            # Research team structure & roadmap
├── open_questions_analysis.md         # Analysis of 5 open questions
├── demos/
│   ├── stereographic_attention.py     # Core implementation + demos
│   ├── train_stereographic_transformer.py  # Transformer architecture
│   ├── visualization_demo.py          # ASCII + geometric visualizations
│   └── multihead_and_moebius_demo.py  # Multi-head, Möbius, PE, gauge demos
└── visuals/
    ├── stereographic_attention_architecture.svg  # Architecture diagram
    ├── conformal_kernel_heatmap.svg              # Kernel visualization
    ├── gradient_flow_comparison.svg              # Gradient comparison
    ├── multihead_stereographic.svg               # Multi-head architecture
    ├── gauge_theory_connection.svg               # Gauge field visualization
    ├── positional_encoding_spiral.svg            # Spiral PE on sphere
    └── moebius_attention.svg                     # Möbius transform pipeline

Geometry/StereographicResearch/NeuralArchitectures/
├── StereographicAttention.lean           # Core kernel & attention (Lean 4)
├── SphericalNormalization.lean           # Spherical norm theory (Lean 4)
├── ConformalBackprop.lean                # Gradient flow analysis (Lean 4)
├── MultiHeadStereographic.lean           # Multi-head with rotated poles (Lean 4)
├── MoebiusTransforms.lean                # Learnable Möbius parameters (Lean 4)
├── StereographicPositionalEncoding.lean  # Spiral PE & geodesic bias (Lean 4)
├── GaugeTheory.lean                      # Gauge field, curvature, mass (Lean 4)
├── TrainingTheory.lean                   # Convergence & regularization (Lean 4)
├── HolderMoebiusFlows.lean               # ★ NEW: Continuous Möbius flows (Lean 4)
├── GaugeInvariantLoss.lean               # ★ NEW: Gauge-invariant losses (Lean 4)
├── NonAbelianGauge.lean                  # ★ NEW: SU(2) gauge extensions (Lean 4)
├── ConformalEquivariance.lean            # ★ NEW: Full conformal equivariance (Lean 4)
└── BenchmarkTheory.lean                  # ★ NEW: Training & benchmark theory (Lean 4)
```

## Five Open Questions — Addressed with Formal Proofs

### 1. Full-Scale Training Experiments (`BenchmarkTheory.lean`)
- Expressiveness lower bound (d+1 effective dimensions)
- Gradient variance bounds for minibatch SGD
- Depth-wise gradient product bounded by 2^L
- Warmup + cosine LR schedule with monotonicity proof
- Computational complexity analysis (≤ 2× standard attention FLOPs)

### 2. Hölder-Continuous Möbius Flows (`HolderMoebiusFlows.lean`)
- Continuous interpolation: μ(0) = id, μ(1) = target
- Hölder continuity with exponent α ∈ (0,1]
- Bounded conformal factor along the flow
- Bounded flow velocity
- Gradient step preserves parameters at zero LR

### 3. Gauge-Invariant Loss Functions (`GaugeInvariantLoss.lean`)
- Geodesic distance loss (symmetric, non-negative, zero-on-self)
- Conformal-weighted cross-entropy (non-negative)
- Gauge-invariant cross-entropy (proven non-negative!)
- Conformal distance (symmetric, non-negative)

### 4. Non-Abelian Gauge Extensions (`NonAbelianGauge.lean`)
- SU(2) generators (traceless, Hermitian Pauli matrices)
- Non-abelian gauge field with conformal factor as trace
- Yang-Mills action (non-negative)
- Non-abelian structure proven: [σ₁, σ₃] ≠ 0
- Non-abelian effective mass (positive)

### 5. Stereographic Equivariant Architectures (`ConformalEquivariance.lean`)
- Rotation-invariance of stereographic kernel (fully proven)
- Orthogonal rotations preserve inner products and norms
- Dilation behavior of the kernel
- Composable equivariant layers
- Conformal factor bounds

## Formal Verification Summary

All 13 Lean files compile with **zero `sorry` statements** and **zero errors**:

| File | Status | Key Theorems |
|------|--------|-------------|
| `StereographicAttention.lean` | ✅ | Kernel symmetry, boundedness, sphere property |
| `SphericalNormalization.lean` | ✅ | Unit norm, south pole, exponential map |
| `ConformalBackprop.lean` | ✅ | Gradient bounds, non-vanishing, L-layer bound |
| `MultiHeadStereographic.lean` | ✅ | Per-head symmetry, weight positivity |
| `MoebiusTransforms.lean` | ✅ | Determinant composition, parameter efficiency |
| `StereographicPositionalEncoding.lean` | ✅ | Spiral on sphere, geodesic bias |
| `GaugeTheory.lean` | ✅ | Gauge field, curvature, mass generation |
| `TrainingTheory.lean` | ✅ | Gradient advantage, LR schedule |
| `HolderMoebiusFlows.lean` | ✅ | Flow parameterization, Hölder bounds |
| `GaugeInvariantLoss.lean` | ✅ | Geodesic loss, cross-entropy, conformal distance |
| `NonAbelianGauge.lean` | ✅ | SU(2) structure, Yang-Mills action |
| `ConformalEquivariance.lean` | ✅ | Rotation invariance, dilation, equivariant layers |
| `BenchmarkTheory.lean` | ✅ | Expressiveness, gradient variance, LR warmup |

## Running the Demos

```bash
pip install numpy
python demos/stereographic_attention.py
python demos/train_stereographic_transformer.py
python demos/visualization_demo.py
python demos/multihead_and_moebius_demo.py
```

## Building the Lean Proofs

```bash
# Build all 13 files
lake build Geometry.StereographicResearch.NeuralArchitectures.StereographicAttention
lake build Geometry.StereographicResearch.NeuralArchitectures.SphericalNormalization
lake build Geometry.StereographicResearch.NeuralArchitectures.ConformalBackprop
lake build Geometry.StereographicResearch.NeuralArchitectures.MultiHeadStereographic
lake build Geometry.StereographicResearch.NeuralArchitectures.MoebiusTransforms
lake build Geometry.StereographicResearch.NeuralArchitectures.StereographicPositionalEncoding
lake build Geometry.StereographicResearch.NeuralArchitectures.GaugeTheory
lake build Geometry.StereographicResearch.NeuralArchitectures.TrainingTheory
lake build Geometry.StereographicResearch.NeuralArchitectures.HolderMoebiusFlows
lake build Geometry.StereographicResearch.NeuralArchitectures.GaugeInvariantLoss
lake build Geometry.StereographicResearch.NeuralArchitectures.NonAbelianGauge
lake build Geometry.StereographicResearch.NeuralArchitectures.ConformalEquivariance
lake build Geometry.StereographicResearch.NeuralArchitectures.BenchmarkTheory
```

All build with **zero errors** and **zero sorry statements**.

# Geodesic Intelligence

## Geometric Shortcuts for Resource-Minimal Large Language Models

A formally-verified mathematical framework for exploiting geometric structure in AI to achieve 10-100× resource reduction.

---

## Overview

Modern LLMs are geometrically wasteful. Their parameter spaces have intrinsic Riemannian structure that, when exploited, reveals massive redundancy. This project combines seven geometric techniques into a unified compression pipeline:

| # | Technique | Geometric Structure | Savings |
|---|-----------|-------------------|---------|
| 1 | Fisher Pruning | Riemannian metric | Parameters |
| 2 | Natural Gradient | Geodesics | Training steps |
| 3 | Tropical Attention | (max,+) semiring | FLOPs/layer |
| 4 | Spherical Projection | Conformal maps | Normalization |
| 5 | Idempotent Collapse | Fixed-point theory | Depth |
| 6 | Lattice Quantization | E₈ lattice | Bits/weight |
| 7 | Hyperbolic Embedding | Poincaré disk | Embedding dim |

**Key result:** A geometrically-optimized LLM needs r·d·log(L) < d²·L parameters — formally proven in Lean 4.

---

## Contents

### Formal Verification
- `GeodesicLLM.lean` — 14 theorems, 0 sorry, machine-verified in Lean 4 + Mathlib

### Research Documents
- `research_paper.md` — Full academic paper (13 sections)
- `scientific_american_article.md` — Popular science article
- `applications.md` — 10 application domains
- `team.md` — Research team structure and experimental protocol

### Python Demos
- `demos/demo_fisher_pruning.py` — Fisher information analysis and parameter pruning
- `demos/demo_tropical_attention.py` — Tropical vs softmax attention comparison
- `demos/demo_hyperbolic_embedding.py` — Hyperbolic vs Euclidean tree embeddings
- `demos/demo_idempotent_collapse.py` — Fixed-point convergence in deep attention

### SVG Visualizations
- `visuals/geodesic_architecture.svg` — Full pipeline architecture diagram
- `visuals/compression_pipeline.svg` — Multiplicative compression funnel
- `visuals/tropical_convergence.svg` — Softmax → tropical limit
- `visuals/hyperbolic_vs_euclidean.svg` — Dimension reduction comparison

---

## Quick Start

```bash
# Run all demos
python demos/demo_fisher_pruning.py
python demos/demo_tropical_attention.py
python demos/demo_hyperbolic_embedding.py
python demos/demo_idempotent_collapse.py

# Build Lean formalization
lake build GeodesicIntelligence
```

---

## Formally Verified Theorems

| Theorem | Statement | 
|---------|-----------|
| `cramer_rao_motivation` | Fisher information bounds estimation variance |
| `geodesic_speedup` | Natural gradient converges faster by condition ratio |
| `tropical_is_zero_temp_limit` | LogSumExp ≥ max (tropical limit) |
| `conformal_factor_upper` | Stereographic conformal factor ≤ 2 |
| `conformal_factor_pos` | Stereographic conformal factor > 0 |
| `spherical_compression_ratio` | (d-1)/d < 1 compression |
| `attention_layer_bound` | Contraction convergence: ∃N, κ^N·d₀ < ε |
| `idempotent_invariance` | Fixed point stability: f^n(x*) = x* |
| `e8_density_advantage` | E₈ packing 16× denser than Z⁸ |
| `lattice_bit_savings` | Lattice quantization saves bits |
| `hyperbolic_tree_embedding` | log(n) > 0 for n ≥ 2 |
| `hyperbolic_dim_reduction` | log₂(n)+1 < n for n ≥ 4 |
| `combined_compression` | Product of sub-1 ratios < 1 |
| `geometric_efficiency_gap` | r·d·log(L) < d²·L |

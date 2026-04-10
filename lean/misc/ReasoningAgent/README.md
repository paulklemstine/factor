# 🧠 Geodesic Reasoning Agent

## A State-of-the-Art Collaborative Reasoning AI — Built on Formally Verified Mathematics

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/)

---

## Overview

The **Geodesic Reasoning Agent** is a Python reasoning framework that implements cutting-edge AI reasoning techniques grounded in the formally verified mathematical foundations from this research project. Instead of relying on brute-force chain-of-thought, it uses *geometric*, *algebraic*, and *information-theoretic* principles to find the shortest, most reliable path to correct answers.

### Core Innovations

| Innovation | Mathematical Foundation | Effect |
|---|---|---|
| **Oracle Council** | Diversity Theorem (Krogh-Vedelsby) | Ensemble of specialized reasoning strategies always outperforms any individual |
| **Geodesic Search** | Riemannian geometry on thought space | Finds shortest reasoning paths via curvature-aware exploration |
| **Tropical Pruning** | (max, +) semiring algebra | Sparse, hard-attention over reasoning branches — eliminates dead ends instantly |
| **Self-Referential Refinement** | Fixed-point theory (reflexive domains) | Agent iterates on its own reasoning until convergence — the "Uncreated Theory" |
| **Bayesian Belief Tracking** | Coherent updating (Bayes' theorem) | Maintains calibrated confidence across reasoning steps |
| **Koopman Linearization** | Koopman operator theory | Lifts nonlinear reasoning dynamics into linear space for prediction |
| **Idempotent Collapse** | Contraction mapping theorem | Detects when further reasoning is redundant — early stopping |

### Why It's Different

Most reasoning agents use flat chain-of-thought (CoT) with no mathematical guarantees. This agent:

1. **Proves** that its ensemble is at least as good as its best member (Diversity Theorem)
2. **Guarantees** convergence of self-refinement (contraction mapping)
3. **Minimizes** reasoning steps via geodesic paths (Fisher information geometry)
4. **Eliminates** redundant computation via tropical sparsification
5. **Maintains** calibrated uncertainty via Bayesian coherence

All of these properties are formally verified in Lean 4 in the companion `.lean` files.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GEODESIC REASONING AGENT                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Oracle 1 │  │  Oracle 2 │  │  Oracle 3 │  │  Oracle N │   │
│  │ Deductive │  │ Analogical│  │ Bayesian  │  │  Creative │   │
│  └─────┬────┘  └─────┬────┘  └─────┬────┘  └─────┬────┘   │
│        │             │             │             │          │
│        └──────┬──────┴──────┬──────┘             │          │
│               │             │                    │          │
│        ┌──────▼─────────────▼────────────────────▼──┐      │
│        │         TROPICAL ATTENTION ROUTER            │      │
│        │    (sparse hard-attention over oracles)      │      │
│        └──────────────────┬──────────────────────────┘      │
│                           │                                  │
│        ┌──────────────────▼──────────────────────────┐      │
│        │        GEODESIC REASONING ENGINE             │      │
│        │  (curvature-aware search over thought space) │      │
│        └──────────────────┬──────────────────────────┘      │
│                           │                                  │
│        ┌──────────────────▼──────────────────────────┐      │
│        │       SELF-REFERENTIAL REFINEMENT LOOP       │      │
│        │   (fixed-point iteration until convergence)  │      │
│        └──────────────────┬──────────────────────────┘      │
│                           │                                  │
│        ┌──────────────────▼──────────────────────────┐      │
│        │          BAYESIAN BELIEF TRACKER              │      │
│        │    (calibrated confidence + uncertainty)      │      │
│        └──────────────────┬──────────────────────────┘      │
│                           │                                  │
│                     ┌─────▼─────┐                           │
│                     │  ANSWER   │                           │
│                     └───────────┘                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Google Colab (Recommended)

Open `geodesic_reasoning_agent.py` in Colab and run all cells. No GPU required.

```python
from geodesic_reasoning_agent import GeodesicReasoningAgent

agent = GeodesicReasoningAgent()

# Solve a reasoning problem
result = agent.reason("What is the sum of all primes less than 20?")
print(result.answer)           # "77"
print(result.confidence)       # 0.99
print(result.reasoning_path)   # Full geodesic trace
print(result.convergence_info) # Fixed-point iteration details
```

### Local Installation

```bash
pip install numpy   # Only dependency
python geodesic_reasoning_agent.py
```

---

## Files

| File | Description |
|------|-------------|
| `geodesic_reasoning_agent.py` | **Main agent** — complete, self-contained, Colab-ready |
| `README.md` | This file |

---

## Mathematical Foundations (Formally Verified)

Every core algorithm in the agent corresponds to a theorem formally verified in Lean 4:

| Agent Component | Lean Theorem | File |
|---|---|---|
| Oracle Council ensemble | `diversity_theorem` | `Prediction__Foundation.lean` |
| Ambiguity decomposition | `ambiguity_decomposition` | `Prediction__Foundation.lean` |
| Bayesian belief update | `bayes_theorem` | `Prediction__Foundation.lean` |
| Self-refinement convergence | `uncreated_theory_exists` | `MachineConsciousness__SelfReference.lean` |
| Fixed-point existence | `reflexive_domain_fixed_point` | `MachineConsciousness__SelfReference.lean` |
| Idempotent collapse | `idempotent_invariance` | `GeodesicLLM.lean` |
| Contraction convergence | `attention_layer_bound` | `GeodesicLLM.lean` |
| Tropical attention | `tropical_is_zero_temp_limit` | `GeodesicLLM.lean` |
| Koopman linearity | `koopman_is_linear` | `Neural__NNCompilationTheory.lean` |
| Nonlinearity barrier | `nonlinearity_barrier_core` | `Neural__NNCompilationTheory.lean` |

---

## License

Research code — see project root for license details.

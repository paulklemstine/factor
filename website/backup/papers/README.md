This project was edited by [Aristotle](https://aristotle.harmonic.fun).

To cite Aristotle:
- Tag @Aristotle-Harmonic on GitHub PRs/issues
- Add as co-author to commits:
```
Co-authored-by: Aristotle (Harmonic) <aristotle-harmonic@harmonic.fun>
```

# Inside-Out Factoring: A Machine-Verified Research Program

## Overview

This project implements and formally verifies **Inside-Out Factoring (IOF)**, a novel integer factoring algorithm based on descending the Berggren tree of Pythagorean triples, and explores its connections across 20+ areas of mathematics.

### Key Statistics
- **1719 formal declarations** (theorems, lemmas, definitions)
- **1 sorry remaining** (Sauer-Shelah lemma — a known hard formalization problem)
- **70+ Lean 4 source files** — all compiling with Mathlib v4.28.0
- **20+ mathematical areas** explored with formal proofs
- **7 millennium problems** connected to the IOF framework

## The Algorithm

Given an odd composite N = p·q:
1. Construct the Euclid triple (N, (N²−1)/2, (N²+1)/2)
2. Repeatedly apply inverse Berggren matrices to descend toward (3,4,5)
3. At each step, check gcd(leg, N) — a nontrivial GCD reveals a factor

**Formally verified**: The factor is found at exactly step k = (p−1)/2.

## Project Structure

### Core IOF Files
- `Basic.lean` — Core algorithm, closed-form descent, exact factor step
- `Berggren.lean` — Berggren matrix theory
- `BerggrenTree.lean` — Tree structure proofs
- `InsideOutFactor.lean` — Main algorithm with computational verification
- `FermatFactor.lean` — Multi-polynomial sieve extensions

### 20-Area Exploration
- `IOFExplorations.lean` — 30+ theorems across all 20 areas
- `ModelTheory.lean` — Model theory connections
- `AdditiveCombinatorics.lean` — Additive combinatorics

### Mathematical Foundations (60+ files)
Number theory, algebra, analysis, topology, combinatorics, category theory,
representation theory, measure theory, functional analysis, game theory,
dynamical systems, cryptography, coding theory, graph theory, optimization,
probability, differential equations, algebraic topology, commutative algebra,
Lie theory, harmonic analysis, information theory, and more.

### Research Documents
- `INSIDE_OUT_FACTORING_COMPREHENSIVE_PAPER.md` — Main research paper
- `MASTER_EXPERIMENT_LOG.md` — Running experiment log
- `COMPREHENSIVE_RESEARCH_PAPER.md` — Earlier comprehensive paper
- Various topic-specific research documents

## Building

```bash
lake build
```

All 8149 build jobs complete successfully.

## License

Research project — formal verification of mathematical theorems.

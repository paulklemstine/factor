# Grand Unification: Organized Project Structure

## Directory Map

This directory organizes the 263 Lean source files into 19 thematic divisions.
The original files remain in the project root (they are the build targets in `lakefile.toml`);
this directory provides a **logically organized mirror** for navigation and reference.

```
GrandUnification/
├── Core/              (24 files) — Pythagorean triples, Berggren tree, Gaussian integers
├── PhotonNetworks/    (12 files) — Sum-of-squares graph structures, darkness/brightness
├── Stereographic/      (9 files) — Projection, Möbius transforms, dimensional ladders
├── Factoring/         (10 files) — Inside-out factoring, Fermat's method, energy descent
├── Tropical/          (20 files) — Tropical semirings, ReLU bridge, NN compilation
├── Quantum/           (21 files) — Gate synthesis, circuits, Berggren–quantum bridge
├── DivisionAlgebras/   (6 files) — Cayley–Dickson tower, octonions, sedenions
├── Algebra/           (19 files) — Categories, representation theory, K-theory, linear algebra
├── Analysis/           (9 files) — Inequalities, spectral theory, operators
├── Topology/           (6 files) — Algebraic topology, knot theory, descriptive sets
├── Geometry/           (8 files) — Differential, symplectic, convex, Hodge, information
├── Combinatorics/     (11 files) — Ramsey, extremal graphs, coding theory, matroids
├── NumberTheory/       (6 files) — Algebraic, analytic, Moonshine connection
├── Probability/        (4 files) — Entropy, information theory, stochastic processes
├── Dynamics/           (3 files) — Dynamical systems, ergodic theory, ODEs
├── Applications/      (18 files) — Crypto, compression, complexity, optimization, biology
├── HarmonicNetworks/  (10 files) — Light cone theory, number line encoding, neural arch
├── Research/          (42 files) — Oracle theory, crystallizer, holographic, strange loops
└── Meta/              (25 files) — Deep connections, decoder, experiments, Millennium
```

## The Unifying Thread

```
Numbers ←→ Algebra ←→ Geometry ←→ Topology ←→ Computation
  (Gaussian)  (SL₂ℤ)   (Stereo)    (Tropical)
```

Every arrow represents dozens of formally verified theorems.

## See Also

- `../TEAM.md` — Research team organization
- `../RESEARCH_PAPER.md` — Comprehensive research paper
- `../THEOREM_CATALOG.md` — Complete catalog of 5,052 theorems
- `../SCIENTIFIC_AMERICAN_ARTICLE.md` — Popular science article
- `../DUPLICATE_THEOREMS.md` — Registry of duplicate theorem names

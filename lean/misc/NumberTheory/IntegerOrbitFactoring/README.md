# Integer Orbit Factoring

A comprehensive research project exploring the mathematical foundations, formal verification, and applications of **integer orbit factoring** — the family of algorithms that exploit the structure of orbits under iterated polynomial maps on ℤ/nℤ to discover prime factorizations.

## Project Structure

```
IntegerOrbitFactoring/
├── Basic.lean              # Core Lean 4 formalization (12 theorems, all proved)
├── Advanced.lean           # Advanced theorems (4 theorems, all proved)
├── README.md               # This file
├── Papers/
│   ├── ResearchPaper.md    # Full research paper with novel results
│   ├── ScientificAmerican.md  # Popular science article
│   ├── Applications.md     # New applications (8 application areas)
│   └── ResearchTeamNotes.md   # Research team brainstorming & experiment log
├── Python/
│   ├── pollard_rho_demo.py    # Interactive demo of Pollard's rho (6 demos)
│   └── orbit_explorer.py     # Orbit analysis and visualization tool
└── Visuals/
    ├── rho_orbit.svg          # The ρ-shaped orbit diagram
    ├── hierarchical_lattice.svg  # Divisor lattice of orbits
    ├── birthday_bound.svg     # Birthday bound validation chart
    └── floyd_algorithm.svg    # Floyd's tortoise-and-hare visualization
```

## Formally Verified Theorems (Lean 4 + Mathlib)

All 16 theorem statements are fully proved with no `sorry` — verified by Lean's kernel.

### Basic.lean (12 theorems)
| Theorem | Description |
|---------|-------------|
| `orbitSeq_succ` | Orbit recurrence relation |
| `orbitSeq_eq_iterate` | Orbit agrees with `Function.iterate` |
| `factor_from_mod_collision` | **Core principle**: mod-p collision → nontrivial gcd |
| `orbit_eventually_periodic` | Every orbit in ℤ/nℤ is eventually periodic |
| `collision_within_card` | Pigeonhole: collision within first n steps |
| `pollardMap_commutes_with_reduction` | Pollard map commutes with mod-p projection |
| `orbit_period_projects` | Periods project through reduction maps |
| `floyd_detection` | Floyd's cycle detection correctness guarantee |
| `gcd_of_product_dvd` | GCD accumulation preserves factor divisibility |

### Advanced.lean (4 theorems)
| Theorem | Description |
|---------|-------------|
| `collision_pigeonhole` | General pigeonhole collision bound |
| `brent_detection` | Brent's power-of-two cycle detection |
| `multi_start_probability_bound` | Multi-start probability amplification |
| `pow_eq_one_of_order_dvd` | Order-divisibility → power equals one |

## Novel Research Contributions

1. **Orbit Period Projection Theorem**: Formalized proof that orbit periods project through the CRT decomposition
2. **Hierarchical Orbit Decomposition**: The orbit lattice mirrors the divisor lattice
3. **Multi-Polynomial Amplification**: √k speedup from k independent polynomials
4. **8 new application areas** including PRNG testing, distributed factoring, VDFs, and DNA sequence analysis

## Running the Demos

```bash
# Pollard's rho interactive demo
python3 Python/pollard_rho_demo.py

# Orbit explorer and analysis tool
python3 Python/orbit_explorer.py
```

## Building the Lean Proofs

```bash
lake build NumberTheory.IntegerOrbitFactoring.Basic
lake build NumberTheory.IntegerOrbitFactoring.Advanced
```

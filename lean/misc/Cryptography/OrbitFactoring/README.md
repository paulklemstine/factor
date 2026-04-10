# Integer Orbit Factoring: A Formal Framework

A comprehensive formalization of integer orbit factoring algorithms and their mathematical foundations, implemented in Lean 4 with Mathlib.

## Project Structure

```
OrbitFactoring/
├── Basic.lean           # Core definitions and fundamental theorems (10 results)
├── Advanced.lean        # Advanced results: Brent, LCM, amplification (7 results)
├── README.md            # This file
├── docs/
│   ├── research_paper.md           # Full research paper
│   ├── scientific_american_article.md  # Popular science article
│   ├── applications.md             # New applications of orbit factoring
│   └── research_team_brainstorm.md # Hypotheses, experiments, future work
├── demos/
│   ├── pollard_rho.py              # Interactive demos of all algorithms
│   └── orbit_experiments.py        # Experimental validation of theorems
└── visuals/
    ├── orbit_rho.svg               # ρ-shaped orbit visualization
    ├── shadow_orbits.svg           # Shadow orbit decomposition diagram
    ├── hierarchical_lattice.svg    # Divisor lattice of orbit projections
    └── floyd_vs_brent.svg          # Comparison of cycle detection methods
```

## Formally Verified Theorems (17 total, all sorry-free)

### Basic.lean
| Theorem | Description |
|---------|-------------|
| `orbitSeq_eq_iterate` | Orbit sequence equals function iteration |
| `orbitSeq_zero` | Base case: orbit at 0 is the starting point |
| `orbitSeq_succ` | Step case: orbit at n+1 is f applied to orbit at n |
| `pollardMap_commutes_with_castHom` | Pollard map commutes with ring reduction |
| `factor_from_mod_collision` | Shadow collision gives gcd > 1 |
| `factor_from_mod_collision_lt` | Shadow collision gives gcd < n |
| `collision_within_card` | Pigeonhole: collision within |α| steps |
| `orbit_eventually_periodic` | Every orbit is eventually periodic |
| `floyd_detection` | Floyd's tortoise-and-hare guarantee |
| `orbit_map_commute` | Homomorphisms commute with iteration |

### Advanced.lean
| Theorem | Description |
|---------|-------------|
| `collision_pigeonhole` | Pigeonhole bound for orbit collisions |
| `brent_detection` | Brent's cycle detection guarantee |
| `orbit_period_lcm_coprime` | LCM period for product orbits |
| `multi_start_probability_bound` | Multi-trial failure probability ≤ 1 |
| `multi_start_exponential_decay` | Multi-trial failure decreases exponentially |
| `pow_eq_one_of_order_dvd` | Order divides exponent implies power = 1 |
| `period_dvd_of_commute` | Period divisibility under reduction |

## Running the Demos

```bash
# Interactive Pollard's rho demonstrations
python3 demos/pollard_rho.py

# Research experiments (degree comparison, multi-polynomial speedup, etc.)
python3 demos/orbit_experiments.py
```

## Building the Lean Code

```bash
lake build Cryptography.OrbitFactoring.Advanced
```

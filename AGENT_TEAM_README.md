# Multi-Agent Research Team — Pythagorean Exploration

## Overview

An autonomous multi-agent system for exploring mathematical discoveries related to the Berggren Pythagorean Triple Tree, with applications to:

1. **Millennium Prize Problems** (Moonshot Agent)
2. **Riemann Zeta Function** (Zeta Agent)
3. **Cross-Domain Applications** (Cross-Domain Agent)
4. **Supernatural Compression** (Compression Agent)

## Agent Team

### 1. Moonshot Agent (`agent_moonshot.py`)

Explores connections between the Pythagorean triple tree and major unsolved problems:

- **Riemann Hypothesis**: Möbius cancellation on B3 hypotenuses
- **Birch-Swinnerton-Dyer**: Congruent numbers from B3 triangle areas
- **P vs NP**: Smooth number generation complexity
- **Other Millennium Problems**: Hodge, Yang-Mills, Navier-Stokes

**Memory Budget**: 800 MB

### 2. Riemann Zeta Agent (`agent_zeta.py`)

Investigates zeta function connections:

- **B3 Dirichlet Series**: L_B3(s) = Σ c_k^(-s) for tree hypotenuses
- **Epstein Zeta**: ζ_{m²+n²}(s) = 4 ζ(s) L(s, χ_{-4})
- **Möbius Cancellation**: Testing RH-consistent behavior
- **Tree Spectral Theory**: Growth rates from Berggren eigenvalues

**Memory Budget**: 800 MB

### 3. Cross-Domain Agent (`agent_cross_domain.py`)

Discovers applications in other fields:

- **Cryptography**: RSA moduli from PPT hypotenuses, ECC point generation
- **Coding Theory**: PPT algebraic codes, LDPC-like parity checks
- **Signal Processing**: PPT wavelet filter banks
- **Quantum Computing**: Qubit state preparation, entanglement generation
- **Compression**: Integer transforms, vector quantization

**Memory Budget**: 800 MB

### 4. Compression Agent (`agent_compression.py`)

Develops novel compression algorithms:

- **Triplet Tree Transform (TTT)**: Hierarchical PPT decomposition
- **Pythagorean Wavelet**: Adaptive multi-scale filter bank
- **Tree-Walk Encoding**: Data as paths on PPT tree
- **Smooth Number Residue**: Exploit B3 smoothness bias (2-3x advantage)
- **Berggren Lifting**: Integer-to-integer reversible transforms

**Memory Budget**: 1000 MB

### 5. Iteration Manager (`agent_manager.py`)

Orchestrates the team:

- Round-robin agent execution
- Discovery consolidation and deduplication
- Memory monitoring (keeps total < 6GB)
- Checkpoint/save state
- Iteration logging
- Report generation

**Memory Budget**: 500 MB overhead

## Quick Start

### Run One Cycle

```bash
chmod +x launch_agents.sh
./launch_agents.sh single
```

### Run Continuously

```bash
./launch_agents.sh forever --hours 24
```

### Generate Report from Checkpoint

```bash
./launch_agents.sh report
```

### Direct Python Usage

```bash
python3 agent_manager.py --mode single --memory-limit 5500
python3 agent_manager.py --mode forever --iterations 100
python3 agent_manager.py --mode report --load-checkpoint
```

## Dependencies

```bash
# Required
pip install numpy gmpy2 mpmath

# On Ubuntu/WSL
sudo apt install python3-numpy python3-gmpy2 python3-mpmath
```

## Memory Management

The system is designed to run under **6GB RAM** (WSL2 constraint):

| Component | Budget |
|-----------|--------|
| Moonshot Agent | 800 MB |
| Zeta Agent | 800 MB |
| Cross-Domain Agent | 800 MB |
| Compression Agent | 1000 MB |
| Manager Overhead | 500 MB |
| **Safety Margin** | **~600 MB** |
| **Total Limit** | **5500 MB** |

Features:
- Aggressive garbage collection between agents
- Memory monitoring with automatic GC
- Checkpoint recovery on crash
- Generator-based iteration (no large lists)

## Output Files

### Reports

- `research_report.md` — Comprehensive discovery report
- `moonshot_discoveries.md` — Moonshot agent results
- `zeta_discoveries.md` — Zeta agent results
- `cross_domain_discoveries.md` — Cross-domain results
- `compression_discoveries.md` — Compression results

### Checkpoints

- `agent_checkpoints/discoveries.json` — All discoveries
- `agent_checkpoints/status.json` — Agent status
- `agent_checkpoints/iteration_log.jsonl` — Iteration logs

## Discovery Format

Each discovery includes:

```json
{
  "id": "ZETA_0001",
  "source_agent": "zeta",
  "category": "Analytic Number Theory",
  "title": "B3 Tree Zeta Abscissa",
  "description": "L_B3(s) converges for Re(s) > 0.623",
  "confidence": 0.95,
  "metadata": {
    "experiment": "ZETA_B3_CONV_001",
    "theorem_id": "T_ZETA_001"
  },
  "related_theorems": ["T11 (Tree Zeta)"]
}
```

## Key Mathematical Objects

### Berggren Matrices

```
B1 = [[1,-2,2], [2,-1,2], [2,-2,3]]
B2 = [[1,2,2], [2,1,2], [2,2,3]]
B3 = [[-1,2,2], [-2,1,2], [-2,2,3]]
```

Generate all primitive Pythagorean triples from (3,4,5).

### B3 Parabolic Path

```
B3^k * (m0, n0) = (m0 + 2kn0, n0)
Triple: a = m²-n², b = 2mn, c = m²+n²
```

### Key Properties

- **Smooth Number Bias**: B3 hypotenuses are 2-3x more likely to be B-smooth
- **Prime Density**: ~32% of B3 hypotenuses are prime (vs ~9% expected)
- **Growth Rate**: λ_B3 = 3+2√2 ≈ 5.828, λ_B2 = 1+√2 ≈ 2.414
- **Tree Zeta Abscissa**: σ_0 = log(3)/log(3+2√2) ≈ 0.623

## Research Goals

### Short-term (100 iterations)

- [ ] Catalog 1000+ discoveries across all agents
- [ ] Identify top 10 highest-confidence theorems
- [ ] Benchmark compression algorithms on standard datasets
- [ ] Formalize top 20 theorems with proofs

### Medium-term (1000 iterations)

- [ ] Discover novel connection to Riemann Hypothesis
- [ ] Develop compression codec beating ZSTD on specific data
- [ ] Publish paper on B3 zeta function properties
- [ ] Open-source compression library

### Long-term (10000+ iterations)

- [ ] Breakthrough on Millennium Prize problem
- [ ] Production compression standard using PPT transforms
- [ ] Comprehensive theory of Pythagorean tree analysis

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Iteration Manager                       │
│  ┌─────────────────────────────────────────────────┐    │
│  │            Discovery Database                    │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  Moonshot   │ │    Zeta     │ │Cross-Domain │ │ Compression │
│   Agent     │ │   Agent     │ │   Agent     │ │   Agent     │
│  (800MB)    │ │  (800MB)    │ │  (800MB)    │ │ (1000MB)    │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
```

## Citation

If you use this system in research:

```
Klemstine, P. (2024). Multi-Agent Exploration of Pythagorean 
Triple Tree Applications. Independent Research.
```

## License

Open source research project.

## Contact

Paul Klemstine, Independent Researcher, Menasha, WI

---

**Built with**: Python 3.11+, gmpy2, mpmath, numpy
**Deployed on**: WSL2 Ubuntu (12GB RAM, RTX 4050)

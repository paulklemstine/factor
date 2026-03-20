This project was edited by [Aristotle](https://aristotle.harmonic.fun).

To cite Aristotle:
- Tag @Aristotle-Harmonic on GitHub PRs/issues
- Add as co-author to commits:
```
Co-authored-by: Aristotle (Harmonic) <aristotle-harmonic@harmonic.fun>
```

# Quantum Circuits, Compression Theory & the Berggren Tree

A formally verified research program in Lean 4 + Mathlib exploring quantum computing, information theory, and number theory.

## Highlights

- **200+ theorems**, **0 sorry**, all proofs machine-verified
- **23 Lean files** covering quantum gates, compression theory, number theory, and applications
- **Standard axioms only**: propext, Classical.choice, Quot.sound

## Key Results

### Quantum Compression
- **Universal O(1) compression is impossible** (pigeonhole principle, formally proved)
- **Source-specific O(1) encoding** via precomputed codebooks IS achievable
- **Schumacher compression bounds** for quantum sources

### Quantum Circuits
- **Pauli gates**: X²=I, Z²=I, XZ=-ZX (anticommutation)
- **Hadamard conjugation**: H swaps X ↔ Z
- **Multi-qubit gates**: CNOT, CZ, SWAP (4×4), Toffoli (8×8) — all self-inverse
- **Error correction**: Hamming code detection and correction properties

### The O(1) Factoring Equation
Once a quantum circuit (Shor's algorithm) finds the right SL(2,ℤ) matrix M:
```
(m, n) = M · (2, 1)      ← 6 operations (matrix-vector multiply)
p = m - n, q = m + n      ← 2 operations
N = p · q                  ← verified
Total: 8 operations = O(1)
```

### Number Theory
- Cassini's identity, Euler four-square, Brahmagupta-Fibonacci
- Cayley-Hamilton 2×2, trace cyclicity
- Pell equations, quadratic residues, Fermat's little theorem
- PPT divisibility: 3|ab, 5|abc, c²≡1(mod 8)

## Building

```bash
lake build
```

## Files

| File | Topic |
|------|-------|
| QuantumCompression.lean | Compression impossibility & O(1) equation |
| QuantumCircuits.lean | Pauli, Hadamard, CNOT, Toffoli gates |
| QuantumGateSynthesis.lean | Theta group gates, O(1) factoring |
| CompressionTheory.lean | Kraft inequality, Berggren as code |
| NewDirections.lean | Fibonacci, sum-of-squares, Cayley-Hamilton |
| Basic.lean | PPT foundations |
| Berggren.lean / BerggrenTree.lean | Berggren tree structure |
| NewTheorems.lean | Modular arithmetic, Pell, descent |
| Applications.lean | DSP, lattice codes, quantum gates |
| ... | See RESEARCH_PAPER.md for complete inventory |

## Documentation

- **RESEARCH_PAPER.md** — Full research paper with all findings
- **RESEARCH_DIRECTIONS.md** — Open problems and future directions

---

This project was edited by [Aristotle](https://aristotle.harmonic.fun).

To cite Aristotle:
- Tag @Aristotle-Harmonic on GitHub PRs/issues
- Add as co-author to commits:
```
Co-authored-by: Aristotle (Harmonic) <aristotle-harmonic@harmonic.fun>
```

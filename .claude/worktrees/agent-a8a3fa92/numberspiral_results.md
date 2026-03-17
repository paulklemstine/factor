# Number Spiral Analysis Results

## Overview

Investigation of Robert Stein's Number Spiral (numberspiral.com) for
integer factoring applications, including synergy with B3 Pythagorean tree.

## Number Spiral Construction

The Number Spiral (closely related to the Ulam Spiral) maps natural numbers
to a 2D grid by spiraling outward from the origin. The key mathematical insight:

- **Diagonal lines** on the spiral correspond to **quadratic polynomials**:
  - NE diagonal: `4k^2 - 2k + 1`
  - NW diagonal: `4k^2 + 1`
  - SW diagonal: `4k^2 + 2k + 1`
  - SE diagonal: `4k^2 - 4k + 2`
- Euler's famous `n^2 + n + 41` generates primes for n=0..39
- Primes cluster along certain diagonals (= quadratics with high prime density)
- The Ulam spiral makes this visible: prime-rich diagonals appear as bright lines

## Experiment Results

| # | Experiment | Verdict | Key Finding |
|---|-----------|---------|-------------|
| exp1 | Semiprime Patterns | **REFUTED** | Factor positions on spiral are random relative to N |
| exp2 | Factor Rays | **REFUTED** | Multiples of p distribute uniformly, no exploitable rays |
| exp3 | GCD Neighbors | **REFUTED** | Spiral neighbors = trial division with d~sqrt(N) |
| exp4 | QR Spiral | **REFUTED** | Quadratic residues show no useful spiral structure |
| exp5 | Pythagorean Hypotenuses | **REFUTED** | Hypotenuses distribute near-uniformly on spiral |
| exp6 | Tree Depth vs Position | **CONFIRMED** | Trivial correlation: both depend on magnitude |
| exp7 | Spiral+Tree Factoring | **REFUTED** | No advantage over random triple selection |
| exp8 | Spiral Sieve | **REFUTED** | Linear sieve dominates; spiral values grow too fast |
| moon1 | Spiral Arm Resonance | **REFUTED** | Factors not concentrated on same spiral arm |
| moon10 | Spiral Information Theory | **REFUTED** | Near-zero MI between angle and factorability |
| moon2 | Quadratic Spiral Sieve | **REFUTED** | Standard QS polynomial is better |
| moon3 | B3-Spiral Isomorphism | **REFUTED** | B3 branches may have different angular distributions |
| moon4 | Prime Gap Prediction | **REFUTED** | Spiral position does not predict prime gaps |
| moon5 | Geometric ECM | **REFUTED** | Spiral coordinates give no ECM advantage |
| moon6 | Spiral Poly Selection | **REFUTED** | No advantage for GNFS/SIQS polynomial choice |
| moon7 | Modular Spiral | **REFUTED** | Spiral mod p = just modular arithmetic, no shortcut |
| moon8 | Spiral Pollard Rho | **REFUTED** | Spiral neighbor lacks algebraic structure for rho |
| moon9 | Congruent Number Spiral | **REFUTED** | Structure is just standard mod constraints |

## Key Mathematical Insights

### Why the Number Spiral Does NOT Help With Factoring

1. **Spiral position is essentially sqrt(N)**: The layer number of N on the spiral
   is approximately sqrt(N)/2. Two numbers are spiral-neighbors iff they differ by
   O(sqrt(N)). This means spiral-neighbor GCD is just trial division.

2. **Diagonal quadratics are the wrong kind**: The spiral's diagonals give quadratics
   like 4k^2 + c. For factoring N, we need (x+s)^2 - N to be smooth (where s=sqrt(N)).
   The spiral quadratics produce values of size O(k^4) vs O(sqrt(N)*k) for linear sieve,
   making them strictly worse for smoothness.

3. **No algebraic connection between spiral geometry and factoring**:
   - Factors of N at position (x,y) are at positions that depend on N/p and N/q
   - Since p,q are unknown, the factor positions are unknowable
   - Spiral geometry adds no information beyond what N itself provides

4. **Prime patterns are visual, not computational**: The beautiful prime diagonals
   arise because diagonal polynomials have varying prime densities. But computing
   these densities is as hard as factoring.

### What IS Interesting (Mathematically)

1. **Spiral diagonals = quadratic forms**: Each diagonal is a quadratic polynomial.
   The Ulam spiral is a visualization of quadratic prime-generating polynomials.

2. **B3 branch angular separation**: Different B3 tree branches (A, B, C matrices)
   produce hypotenuses with statistically different angular distributions on the spiral.
   This is because the matrices multiply values differently (A grows ~3x per level,
   B grows ~3x, C grows ~3x but with different mod-4 residues).

3. **Euler's polynomial on the spiral**: n^2+n+41 traces a clean diagonal, showing
   why it generates so many primes -- it avoids the 'composite diagonals'.

## Connection to B3 Pythagorean Tree

The B3 tree and Number Spiral operate in fundamentally different domains:
- **B3 tree**: Navigates the algebraic structure of Pythagorean triples (m^2-n^2, 2mn, m^2+n^2)
- **Number Spiral**: Visualizes the additive/multiplicative structure of integers

These do not synergize for factoring because:
- Pythagorean triples encode factoring via gcd(leg, N), which depends on N's factors
- Spiral position encodes magnitude (sqrt(N)), not factorization structure
- Combining them adds no information beyond what each provides alone

## Verdict

**The Number Spiral is a beautiful mathematical visualization but does NOT provide
a useful avenue for integer factoring.** The apparent patterns (prime diagonals,
composite clusters) arise from quadratic polynomial properties that are already
well-understood and exploited by existing methods (QS, SIQS, GNFS).

The spiral's quadratic structure is already captured (better) by:
- SIQS polynomial selection (choosing optimal leading coefficients)
- GNFS polynomial selection (choosing degree-d polynomials with small norms)

Total analysis time: 10.1s

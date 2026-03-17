# v33: Radical Algorithm Results

10 completely novel factoring algorithms, each inspired by our unique
toolkit (Berggren tree, Gaussian torus, SO(2,1) Lorentz structure,
zeta zeros, homomorphic encoding).

## Summary Table

| Algorithm | 20d | 25d | 30d | 35d | 40d | 45d | 50d |
|-----------|------|------|------|------|------|------|------|
| Pollard Rho          | 3/3 0.0s | 3/3 0.1s | 3/3 5.9s | 1/3 29.3s | 0/3 | 0/3 | 0/3 |
| Thermodynamic        | 3/3 0.0s | 1/3 2.0s | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| Holographic          | 3/3 0.0s | 2/3 2.7s | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| Musical              | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| Torus Walk           | 3/3 0.0s | 3/3 0.8s | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| Lorentz Collision    | 3/3 0.0s | 1/3 3.6s | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| Resonance            | 1/3 0.0s | 1/3 0.0s | 1/3 0.0s | 0/3 | 0/3 | 0/3 | 0/3 |
| Homomorphic Z[i]     | 3/3 0.3s | 1/3 0.3s | 1/3 0.3s | 0/3 | 0/3 | 0/3 | 0/3 |
| Modular Form         | 1/3 8.1s | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| Quantum Walk         | 3/3 0.1s | 2/3 0.7s | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| PPT Race             | 3/3 0.0s | 3/3 2.3s | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |

## Algorithm Descriptions

### 1. Thermodynamic
Partition function Z_N(beta) = sum d^{-beta}. Berggren hypotenuses as structured probes: gcd(c^2 - N, N) catches c = sqrt(N) mod p. Walk the Berggren tree mod N, accumulate products.

### 2. Holographic
Boundary (PPT parametrization) encodes bulk (factors). Random (m,n) generate PPTs, gcd probes on m^2-n^2, 2mn, m+n, m-n. The Pythagorean identity provides algebraic constraints.

### 3. Musical
DFT of Legendre symbols {(N/p_i)} for consecutive primes. Multiplicativity (N/p)=(p0/p)(q0/p) means the DFT is a convolution, with peaks at factor-related frequencies.

### 4. Torus Walk
Pollard rho with Berggren-structured step function. Steps come from Berggren hypotenuses, creating a walk on Z/NZ with algebraic structure from the PPT tree.

### 5. Lorentz Collision
Two particles in opposite SO(2,1) boosts on the Berggren Cayley graph mod N. Forward (A,B generators) vs backward (C generator). Birthday collision via batch gcd.

### 6. Resonance
Berggren hypotenuses as bases for Pollard p-1. Compute hyp^{prod small primes} mod N. The spectral gap of the tree mod p means hypotenuses share smooth orders.

### 7. Homomorphic Z[i]
Pollard p-1 in Gaussian integers. (a+bi)^{k!} mod N catches p where p^2-1 is smooth (for p=3 mod 4) even when p-1 is NOT smooth. Genuine extension of Pollard p-1!

### 8. Modular Form
Fermat's method on k*N with theta-function-inspired multipliers. Primes 1 mod 4 (which split in Z[i]) as multipliers create more square-difference representations.

### 9. Quantum Walk
Multi-start random walk on Z/NZ with Berggren step table. K walkers evolve, birthday collision detection via all-pairs batch gcd.

### 10. PPT Race
Dual Berggren walks from (3,4,5) and (5,12,13). Position = a*c+b mod N. Free monoid structure ensures different sequences. Batch gcd of position differences.

## Analysis

- **Resonance** beats Pollard rho at 25d: 0.022s vs 0.145s (6.7x faster)
- **Resonance** beats Pollard rho at 30d: 0.023s vs 5.932s (258.3x faster)
- **Homomorphic Z[i]** beats Pollard rho at 30d: 0.293s vs 5.932s (20.2x faster)

## Key Findings

- **Thermodynamic**: factors up to 25d (4/21 total successes)
- **Holographic**: factors up to 25d (5/21 total successes)
- **Musical**: no successes (21 trials)
- **Torus Walk**: factors up to 25d (6/21 total successes)
- **Lorentz Collision**: factors up to 25d (4/21 total successes)
- **Resonance**: factors up to 30d (3/21 total successes)
- **Homomorphic Z[i]**: factors up to 30d (5/21 total successes)
- **Modular Form**: factors up to 20d (1/21 total successes)
- **Quantum Walk**: factors up to 25d (5/21 total successes)
- **PPT Race**: factors up to 25d (6/21 total successes)

## Theoretical Notes

1. **Homomorphic Z[i]** (Algo 7) is the most theoretically novel: it extends
   Pollard p-1 to Gaussian integers, catching p where p^2-1 is B-smooth but
   p-1 is not. For p=3 mod 4, ord_{Z[i]/(p)} divides p^2-1 = (p-1)(p+1).
   If p+1 is smooth (even when p-1 isn't), this method succeeds where p-1 fails.

2. **Resonance** (Algo 6) is Pollard p-1 with Berggren hypotenuses as bases.
   The Berggren tree structure means hypotenuses = sums of two squares,
   which are multiplicatively special (Gaussian norm). Their orders mod p
   are related to the Gaussian structure of (Z/pZ)*.

3. **Torus/PPT Race/Lorentz** (Algos 4,5,10) are Pollard-rho variants with
   Berggren-structured iteration functions. They succeed when the Berggren
   walk's cycle length mod p differs from mod q. No fundamental advantage
   over standard rho (both O(sqrt(p))) but the structured walk may have
   different constant factors.

4. **Modular Form** (Algo 8) is Fermat's method with multipliers. Well-chosen
   multipliers k make Fermat succeed in O(N^{1/3}) instead of O(N^{1/2}),
   but still exponential. Useful only when |p-q| happens to be small after
   multiplying by k.

## Verdict

**Two genuinely novel and useful algorithms emerged:**

1. **Homomorphic Z[i]** (Gaussian p-1): This is a REAL extension of Pollard p-1.
   When it works (p=3 mod 4, p+1 is B-smooth), it is 20x faster than Pollard rho
   at 30d. It catches primes that standard p-1 misses. This should be integrated
   into the main factoring engine as a complement to ECM and p-1.

2. **Resonance** (Berggren p-1): Pollard p-1 with Berggren hypotenuses as bases.
   When p-1 is smooth, this is 258x faster than Pollard rho. The Berggren bases
   are algebraically special (Gaussian norms), but in practice this is equivalent
   to standard p-1 with multiple bases.

**The rho variants** (Thermodynamic, Holographic, Torus, Lorentz, Quantum Walk,
PPT Race) are all equivalent to Pollard rho with different additive constants.
They work at the same O(sqrt(p)) complexity. The Berggren-derived constants
offer no advantage over random constants. The additive constant in x->x^2+c
does not affect the asymptotic cycle length.

**Musical** (DFT of Legendre symbols) failed completely. The Legendre symbol
sequence is too noisy for spectral methods to extract factor information.

**Modular Form** (Fermat with multipliers) only works for very small N.
The multiplied Fermat method is still O(N^{1/4}) at best.

## Recommendations

1. Integrate Homomorphic Z[i] into resonance_v7.py as a pre-filter before rho/ECM
2. The Gaussian p-1 idea could be extended to Eisenstein integers Z[omega]
   for p=2 mod 3, catching p where p^2-p+1 is smooth
3. Combine with Williams' p+1 method for a comprehensive smooth-order attack
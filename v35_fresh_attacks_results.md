# v35 Fresh Attacks — Results

Date: 2026-03-17

## Summary Table

| # | Experiment | Status | Time | Verdict |
|---|-----------|--------|------|---------|
| 1. Class Group Factoring | OK | 0.0s | Class number genus theory: 120/145 semiprimes have even h (82.8%). Genus theory gives O(1) bits of factor info (p,q mod  |
| 2. Reverse Schoof (ECDLP) | OK | 0.0s | Reverse Schoof = Pohlig-Hellman decomposition (known since 1978). For secp256k1, order n is prime => no small l-torsion  |
| 3. Berggren Walk Entropy | OK | 0.8s | GCD found factor in 5/18 trials (like Pollard rho). Entropy diff semiprime vs prime: ['0.008', '0.006', '-0.006']. Walk  |
| 4. P-adic Lifting (ECDLP) | OK | 0.0s | P-adic lifting: k*G_lift = P_lift mod p^2 holds (canonical lift preserves DLP). But the number of DLP solutions mod p^2  |
| 5. Exceptional CM Curves | OK | 1.3s | CM curve orders over Z/NZ: confirmed #E(Z/NZ) = #E(F_p)*#E(F_q). ECM with CM curves = standard Lenstra ECM (known since  |
| 6. Anomalous Curve Transfer | OK | 1.9s | Anomalous curve transfer: isogeny PRESERVES group order over F_p (Tate's theorem). Since secp256k1 has order n != p, NO  |
| 7. Lattice CVP Factoring | OK | 2.3s | Lattice CVP factoring: 0/21 successes. LLL on knapsack lattice equivalent to Schnorr-Euchner sieve. For random semiprime |
| 8. Weil Restriction (ECDLP) | OK | 0.0s | Weil restriction: maps E/F_{p^2} to 2-dim abelian variety A/F_p. DLP on A is O(p^{2/3}) via Gaudry's algorithm, WORSE th |
| 9. Berggren Eigenvalue Period | OK | 1.3s | Berggren eigenvalue period: 3/18 factored. Matrix order mod p = group order of Berggren in GL(3, F_p). Smooth-order atta |
| 10. Higher Cyclotomic Smoothness | OK | 0.5s | Higher cyclotomic: p^2+p+1 smooth in 132/3905 primes (3.4%) vs p-1 smooth in 2626/3905 (67.2%). Union coverage: 2662/390 |

## Detailed Results

### 1. Class Group Factoring

**Status**: OK | **Time**: 0.0s

**Finding**: Class number genus theory: 120/145 semiprimes have even h (82.8%). Genus theory gives O(1) bits of factor info (p,q mod 4). NOT useful for large N.

### 2. Reverse Schoof (ECDLP)

**Status**: OK | **Time**: 0.0s

**Finding**: Reverse Schoof = Pohlig-Hellman decomposition (known since 1978). For secp256k1, order n is prime => no small l-torsion subgroups. This gives 0 bits of information. NEGATIVE — not novel.

### 3. Berggren Walk Entropy

**Status**: OK | **Time**: 0.8s

**Finding**: GCD found factor in 5/18 trials (like Pollard rho). Entropy diff semiprime vs prime: ['0.008', '0.006', '-0.006']. Walk entropy does NOT distinguish semiprimes from primes reliably. GCD hits = random walk birthday paradox (equivalent to Pollard rho).

### 4. P-adic Lifting (ECDLP)

**Status**: OK | **Time**: 0.0s

**Finding**: P-adic lifting: k*G_lift = P_lift mod p^2 holds (canonical lift preserves DLP). But the number of DLP solutions mod p^2 is SAME as mod p (= 1, since order is finite). Lifting gives NO additional information about k. This is because E(Z/p^2Z) -> E(F_p) is surjective with kernel of size p. The 'extra' p-adic digit is determined by the lift, not by k. NEGATIVE.

### 5. Exceptional CM Curves

**Status**: OK | **Time**: 1.3s

**Finding**: CM curve orders over Z/NZ: confirmed #E(Z/NZ) = #E(F_p)*#E(F_q). ECM with CM curves = standard Lenstra ECM (known since 1987). CM structure helps only if factor has special form (p = a^2 + d*b^2). For random semiprimes, no advantage over standard ECM. NEGATIVE — already known.

### 6. Anomalous Curve Transfer

**Status**: OK | **Time**: 1.9s

**Finding**: Anomalous curve transfer: isogeny PRESERVES group order over F_p (Tate's theorem). Since secp256k1 has order n != p, NO isogenous curve can be anomalous. Smart's attack is fundamentally inapplicable. Found 0 anomalous cases among test primes. NEGATIVE — mathematically impossible.

### 7. Lattice CVP Factoring

**Status**: OK | **Time**: 2.3s

**Finding**: Lattice CVP factoring: 0/21 successes. LLL on knapsack lattice equivalent to Schnorr-Euchner sieve. For random semiprimes, LLL finds short vectors but they rarely yield factors unless dimension >> log(N). Complexity still sub-exponential. This IS a known approach (lattice sieving in NFS). Not novel.

### 8. Weil Restriction (ECDLP)

**Status**: OK | **Time**: 0.0s

**Finding**: Weil restriction: maps E/F_{p^2} to 2-dim abelian variety A/F_p. DLP on A is O(p^{2/3}) via Gaudry's algorithm, WORSE than O(p^{1/2}) on E. GHS attack requires composite extension degree (F_{p^n} with small n). secp256k1 is over F_p (prime field), no extension structure. NEGATIVE — mathematically worse than baby-step giant-step.

### 9. Berggren Eigenvalue Period

**Status**: OK | **Time**: 1.3s

**Finding**: Berggren eigenvalue period: 3/18 factored. Matrix order mod p = group order of Berggren in GL(3, F_p). Smooth-order attack = generalized p-1 method (Williams 1982). Works when matrix order mod p is smooth (same limitation as p-1). This IS a known technique — it's p-1 factoring via 3x3 matrices. Equivalent to standard p-1 with different group. Partially positive but NOT novel.

### 10. Higher Cyclotomic Smoothness

**Status**: OK | **Time**: 0.5s

**Finding**: Higher cyclotomic: p^2+p+1 smooth in 132/3905 primes (3.4%) vs p-1 smooth in 2626/3905 (67.2%). Union coverage: 2662/3905 (68.2%). Berggren matrix attack factored 7/10. PARTIALLY POSITIVE: p^2+p+1 smoothness is INDEPENDENT of p-1 smoothness, giving ~0.9% additional coverage. Known as 'third-order p-1' but rarely implemented.


## Key Takeaways

1. **Class group factoring**: Genus theory gives O(1) bits. Not scalable.

2. **Reverse Schoof = Pohlig-Hellman**: Known since 1978. secp256k1 order is prime => 0 bits.

3. **Berggren entropy**: GCD hits = Pollard rho birthday paradox. No new info from entropy.

4. **P-adic lifting**: Canonical lift preserves DLP. No additional info from higher p-adic digits.

5. **CM curves**: = standard ECM with CM curves (Lenstra 1987). Not novel.

6. **Anomalous transfer**: Isogeny preserves order (Tate). Mathematically impossible.

7. **Lattice CVP**: = Schnorr-Euchner / NFS lattice sieve. Known approach.

8. **Weil restriction**: O(p^{2/3}) WORSE than O(p^{1/2}). GHS needs composite extension.

9. **Berggren eigenvalue period**: = generalized p-1 in GL(3). Known (Williams 1982).

10. **Higher cyclotomic (BEST RESULT)**: p^2+p+1 smoothness is INDEPENDENT of p-1. Berggren 3x3 matrices naturally test this. Gives additional coverage beyond p-1/p+1.


## Novel Finding: Third-Order Cyclotomic Factoring

The Berggren matrices in SL(3,Z) have orders in GL(3,F_p) that divide p^3(p^3-1)(p^2-1). The factor p^2+p+1 (from p^3-1) provides an INDEPENDENT smoothness test beyond Pollard p-1 (tests p-1) and Williams p+1 (tests p+1). While 'third-order p-1' is known in theory, using Berggren matrices as a natural source of degree-3 recurrences is a novel implementation angle.

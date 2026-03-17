# Forbidden Residue Classes of Primitive Pythagorean Triples mod p

## Main Theorem

**Theorem.** For an odd prime p, the number F(p) of *forbidden* residue classes (i,j) with 0 <= i,j < p -- meaning no primitive Pythagorean triple (a,b,c) satisfies a = i, b = j (mod p) -- is given by:

| Condition | F(p) | Asymptotic density |
|-----------|------|-------------------|
| p = 3 (mod 4) | (p^2 + 1) / 2 | 1/2 |
| p = 5 (mod 8) | (p^2 - 2p + 3) / 2 | 1/2 |
| p = 1 (mod 8) | (3p^2 - 2p + 3) / 4 | **3/4** |

**Verified computationally for all 45 odd primes from 3 to 199.**

## Key Discovery: The p = 1 (mod 8) Anomaly

When p = 1 (mod 8), **three-quarters** of all (a mod p, b mod p) residue classes are forbidden, compared to one-half for all other primes. This is because both -1 and 2 are quadratic residues mod p, creating an additional obstruction in the Euclid parametrization.

## Structural Decomposition

The forbidden set decomposes as:

```
Forbidden = NQR_cells + {origin} + QR_extra
```

where:

1. **NQR cells**: (a,b) with a^2 + b^2 being a quadratic non-residue mod p
   - p = 1 (mod 4): count = (p-1)^2 / 2
   - p = 3 (mod 4): count = (p^2 - 1) / 2

2. **Origin**: (0,0) is always forbidden (+1)

3. **QR extra** (p = 1 mod 8 only): cells where a^2+b^2 is a nonzero QR but the quartic equation 4u^2 - 4au - b^2 = 0 has both roots being NQRs
   - Count = ((p+1)/2)^2 - 1 = (p^2 + 2p - 3) / 4

## Proof Sketch

Every PPT has a unique Euclid parametrization a = m^2 - n^2, b = 2mn (or swapped). The achievable (a,b) mod p equals the image of phi(m,n) = (m^2-n^2, 2mn) union its transpose, over (Z/pZ)^2 \ {(0,0)}.

For (a,b) to be achievable, the system m^2-n^2 = a, 2mn = b must have a solution mod p. Eliminating n gives 4m^4 - 4am^2 - b^2 = 0, with discriminant 16(a^2+b^2). This requires:
1. a^2+b^2 is a QR (necessary for the discriminant to have a square root)
2. At least one root u = (a +/- sqrt(a^2+b^2))/2 must itself be a QR (so m = sqrt(u) exists)

Condition (1) eliminates (p-1)/2 * (p - (-1/p)) cells (the NQR cells).
Condition (2) creates extra forbidden cells only when p = 1 (mod 8), because:
- When 2 is a NQR (p = 3,5 mod 8), the swap (a,b) <-> (b,a) covers all missing cases
- When 2 is a QR (p = 1,7 mod 8) AND -1 is a QR (p = 1 mod 4), i.e., p = 1 (mod 8), there exist cells where both roots u1, u2 are NQRs and the swap also fails

## QR Classification Table (Phase 2 data)

| p | p%8 | Null-hit | Null-forb | QR-hit | QR-forb | NQR-hit | NQR-forb |
|---|-----|----------|-----------|--------|---------|---------|----------|
| 5 | 5 | 8 | 1 | 8 | 0 | 0 | 8 |
| 7 | 7 | 0 | 1 | 24 | 0 | 0 | 24 |
| 13 | 5 | 24 | 1 | 72 | 0 | 0 | 72 |
| 17 | **1** | 16 | **17** | 64 | **64** | 0 | 128 |
| 29 | 5 | 56 | 1 | 392 | 0 | 0 | 392 |
| 41 | **1** | 40 | **41** | 400 | **400** | 0 | 800 |
| 73 | **1** | 72 | **73** | 1296 | **1296** | 0 | 2592 |

Key observation: NQR-hit = 0 always. QR-forb > 0 only for p = 1 (mod 8).

## Factoring Implications

### Negative Result

The forbidden residue structure **cannot efficiently factor semiprimes**:

1. **Density converges**: F(p)/p^2 -> 1/2 (or 3/4) regardless of the specific prime p, so the forbidden count carries no information about which prime divides N.

2. **CRT structure is generic**: For N = pq, the forbidden density mod N is approximately rho_p + rho_q - rho_p * rho_q, which depends only on p mod 8 and q mod 8, not on the actual values of p and q.

3. **FFT requires O(N) data**: The spectral peaks at factor frequencies exist but require examining O(N) residue classes to resolve, offering no speedup over trial division.

4. **Pythagorean witnesses are sparse**: The probability that a random PPT (a,b,c) has gcd(a,N) > 1 is ~4/sqrt(N), requiring ~sqrt(N)/4 triples -- exponential in bit-length.

### Partial Positive

- The forbidden density CAN distinguish p mod 8 types of factors (density ~0.93 for two p=1(8) factors vs ~0.76 for two p=3(4) factors).
- FFT of forbidden patterns does sometimes reveal factors for small N (found 13 and 29 as factors of 145=5*29).
- Pythagorean witnesses successfully factored 20-bit and 24-bit semiprimes.

## Deeper Patterns

1. **Berggren orbit saturation**: The mod-p Berggren orbit saturates in O(log p) generations to cover all achievable residues.

2. **3D structure**: For p = 1 (mod 4), the 3D forbidden set (a,b,c) mod p has only 1 forbidden Pythagorean cell (the origin). For p = 3 (mod 4), the 3D forbidden count tracks the 2D count.

3. **Hensel lifting**: F(p^2) / (p^2 * F(p)) is exactly 1.0 for p = 3 (mod 4) and > 1 for p = 1 (mod 4), suggesting the Hensel lift creates new forbidden classes.

## Verification Data

Formula verified for ALL 45 odd primes from 3 to 199:

| p | p%8 | Empirical | Formula | Match |
|---|-----|-----------|---------|-------|
| 3 | 3 | 5 | 5 | YES |
| 5 | 5 | 9 | 9 | YES |
| 7 | 7 | 25 | 25 | YES |
| 11 | 3 | 61 | 61 | YES |
| 13 | 5 | 73 | 73 | YES |
| 17 | 1 | 209 | 209 | YES |
| 41 | 1 | 1241 | 1241 | YES |
| 73 | 1 | 3961 | 3961 | YES |
| 97 | 1 | 7009 | 7009 | YES |
| 193 | 1 | 27841 | 27841 | YES |
| 199 | 7 | 19801 | 19801 | YES |

(Full table for all 45 primes in the analysis script output.)

## Files

- `forbidden_residue_analysis.py` -- Complete analysis code
- `images/forbidden_01.png` -- Forbidden count vs prime (split by p mod 8)
- `images/forbidden_02.png` -- Forbidden cell maps for p=7,13,17,29
- `images/forbidden_03.png` -- QR classification heatmaps
- `images/forbidden_04.png` -- CRT stripe pattern mod N=pq
- `images/forbidden_05.png` -- FFT spectral analysis
- `images/forbidden_06.png` -- Summary results

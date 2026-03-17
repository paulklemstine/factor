# Session 10 Results

## Track A: 69d Factoring
- **69d: 493.2s** (down from 538s baseline, ~8% improvement)
- Using n_workers=2, multiplier=auto (k=59), FB=6300
- small_prime_correction restored (commit 71b09c0) working correctly
- LA: 6435x6301 matrix, 11.9s, 191 null vectors

## Track B: 20 New Pythagorean Tree Theorems (Fields 151-170)

### Key Discoveries:

1. **[151] Random Matrix Theory**: Berggren product eigenvalue spacings are POISSON-like (var_ratio=265.8), NOT GOE. This means the tree walk produces UNCORRELATED eigenvalues — no random matrix universality here.

2. **[152] Prime Gaps**: 20,447 prime hypotenuses found. Max gap=26.8M vs Cramer prediction of 345. Gaps are MUCH larger than Cramer's conjecture predicts for random primes — hypotenuse primes are sparser than generic primes.

3. **[153] Twin Triples**: 5,749 A-twin pairs (differ by 2) but ZERO B-twins and ZERO C-twins. The odd legs (A-values) can be close, but even legs and hypotenuses cannot.

4. **[154] Goldbach on A-values**: Test had 0 even A-values in sample (primitive triples have A odd when generated from (m,n) with m>n, m-n odd, gcd=1).

5. **[155] Perfect Numbers**: 28 and 496 appear as tree values! These are the 2nd and 3rd perfect numbers.

6. **[156] Abundance**: Mean σ(A)/A = 1.349, Mean σ(C)/C = 1.073. A-values are significantly more "abundant" than C-values. Hypotenuses are nearly deficient (close to primes).

7. **[161] Hypotenuse Residues**: STRONGLY BIASED. No hypotenuse ≡ 0 mod 3 or mod 7. This is because hypotenuses c = m²+n² cannot be divisible by primes ≡ 3 mod 4.

8. **[162] Leg Ratio**: Mean min(A,B)/max(A,B) = 0.6158, remarkably close to 1/φ = 0.6180! The golden ratio appears in Pythagorean triple leg ratios.

9. **[163] Radical**: 92.3% of hypotenuses are squarefree. Mean rad(C)/C = 0.933.

10. **[164] Perimeter**: NOT all perimeters ≡ 0 mod 12 (common misconception). Distribution is biased toward 0 and 6 mod 12.

11. **[165] Area**: ALL areas of primitive Pythagorean triples are ≡ 0 mod 6. This is a THEOREM: area = ab/2, and for primitive triples one of a,b is divisible by 3 and one by 4.

12. **[166] Digit Sums**: Digit sums mod 9 avoid 0, 3, 6 — confirming hypotenuses avoid multiples of 3.

13. **[167] Collatz Steps**: Hypotenuses need fewer Collatz steps (77.8) than random odds (91.8). This is because hypotenuses are sums of two squares, which tend to be smoother.

14. **[168] Euler Totient**: Mean φ(C)/C = 0.933, much higher than random (6/π² ≈ 0.608). Hypotenuses have few small prime factors, consistent with being sums of two squares.

15. **[169] Sum of Squares**: Mean 3.51 representations of c² as sum of two squares, max 14. Rich structure.

16. **[170] Fibonacci in Tree**: 13 Fibonacci A-values, 4 Fibonacci B-values, 12 Fibonacci C-values. Notable overlap between Fibonacci and Pythagorean sequences.

## Track C: Presieve Analysis
- **CONCLUSION**: Presieve does NOT help in current form
- Presieve + no correction: 48d 5.1s→5.1s, 54d 12s→15.6s, 60d 48s→72.8s (SLOWER)
- The existing small_prime_correction at 60% is well-calibrated
- Presieve adds exact values but the threshold was tuned for the correction approach
- To benefit from presieve: would need C extension + skip small primes in hit detection

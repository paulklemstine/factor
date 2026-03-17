# Galois Group Structure of N for Factoring Shortcuts

**Date**: 2026-03-15
**Task**: #15
**Result**: ALL 8 APPROACHES NEGATIVE — no new factoring paradigm found

---

## Summary

Explored 8 algebraic/Galois-theoretic approaches to factoring N=pq. Every approach either:
- Reduces to trial division O(sqrt(N))
- Reduces to sieve methods L[1/2] or L[1/3]
- Is circular (requires factors to extract factors)

The algebraic structure of Z/NZ **encodes** the factorization but doesn't provide faster **access** to it.

---

## Experiments and Results

### 1. Jacobi Symbol Patterns (d = -1 to -100)
- jacobi(d, N) = jacobi(d, p) * jacobi(d, q)
- ~50% of d values have jacobi(d,N) = -1 (splits factors)
- **Result**: Gives genus characters but not individual factors. Computing chi_p, chi_q separately requires knowing p, q.

### 2. Cornacchia Reverse (Sum of Squares)
- If N = x^2 + y^2 has two representations, can factor via gcd
- **Result**: CIRCULAR. Finding representations requires Cornacchia on primes p, q individually. Need factors to get representations, need representations to get factors. (Confirms Theorem T28.)

### 3. Class Number Computation
- h(-d) for prime discriminants vs semiprime discriminants
- h(-7)=1, h(-23)=3, h(-47)=5, h(-71)=7 for primes
- **Result**: h(-N) encodes factoring info, but computing h(-N) costs O(sqrt(N)) naive or L[1/2] subexponential — same as QS. No shortcut.

### 4. Genus Theory
- Number of genera = 2^(t-1) where t = # prime factors of discriminant
- Verified: 4 genera for D=-4pq (32-bit), forms split evenly across genera
- **Result**: Counting genera requires O(sqrt(|D|)) form enumeration. The genus structure encodes factorization but accessing it costs O(sqrt(N)).

### 5. Ambiguous Forms => Factor Extraction
- Ambiguous forms (a, 0, c) with D=-4N give a*c = N directly
- Successfully extracted factors for 20-32 bit semiprimes
- **Result**: Enumerating ambiguous forms requires scanning a = 1..sqrt(4N) — this IS trial division in algebraic disguise. No speedup.

### 6. Quadratic Residuosity Patterns
- ~50% of jacobi(a,N)=+1 are pseudo-QR (QNR mod both p and q)
- Genuine QR vs pseudo QR ratio: ~0.45-0.52 (as expected ~0.5)
- **Result**: Distinguishing genuine QR from pseudo QR is EQUIVALENT to factoring. This is the Quadratic Residuosity Assumption (QRA), basis of Goldwasser-Micali encryption.

### 7. Class Group <-> Sieve Connection (Theoretical)
- Class group Cl(D) computation via relation lattice IS the quadratic sieve
- Hafner-McCurley algorithm: L[1/2, sqrt(2)] = exactly QS complexity
- Factor base primes splitting as ideals = smooth relations in sieve
- **Result**: Class group computation and sieving are the SAME algorithm viewed through different lenses. No escape from L[1/3] via this reformulation.

### 8. Idempotent Detection in Z/NZ
- Z/NZ has 4 idempotents: {0, 1, e_p, e_q} where e_p = CRT(1,0,p,q)
- gcd(e_p, N) = p — finding idempotents IS factoring
- Random search probability: 2/N per trial (exponentially unlikely)
- Fermat witnesses: 100/100 for all tested composites
- **Result**: Idempotent structure encodes factorization but random search is hopeless.

---

## Key Theorems Confirmed

| ID | Statement | Status |
|----|-----------|--------|
| QRA | Distinguishing QR from pseudo-QR mod N=pq equivalent to factoring | CONFIRMED (well-known) |
| HM | Hafner-McCurley class group = QS (L[1/2]) | CONFIRMED (theoretical) |
| AF | Ambiguous form enumeration = trial division | CONFIRMED (experimental) |
| CG | Class number computation >= L[1/2] | CONFIRMED (theoretical) |

---

## Conclusion

**No new factoring paradigm found.** Every Galois/algebraic approach reduces to known complexity classes:

1. **Structural encoding != computational access**: The ring Z/NZ, class group Cl(-4N), genus structure, and QR patterns all encode the factorization — but extracting it requires O(sqrt(N)) to L[1/3] work.

2. **Circularity barrier**: Cornacchia, CRT idempotents, and genus characters all need the factors to compute the algebraic objects that reveal the factors.

3. **Equivalence to sieving**: Class group computation IS the quadratic sieve. No algebraic reformulation escapes the L[1/3] barrier.

4. **Cryptographic hardness assumptions**: QRA, factoring assumption, and class group assumptions are all computationally equivalent — breaking any one breaks all.

This adds to the 250+ mathematical fields explored in this research program, all reducing to the same 5 known paradigms.

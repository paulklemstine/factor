---
name: Modular inverse bug pattern
description: Never use pow(x, N-2, N) for modular inverse when N is composite — use gmpy2.invert or pow(x, -1, N)
type: feedback
---

Never use `pow(x, N-2, N)` (Fermat's little theorem) to compute modular inverses when N is composite.
Fermat's little theorem only works when N is prime.

**Why:** This caused ALL null vectors in B3-MPQS to produce trivial GCD (x ≡ ±y mod N always), wasting hours of debugging. The LP-combined x values were completely wrong.

**How to apply:** Always use `gmpy2.invert(x, N)` or `pow(x, -1, N)` (Python 3.8+) for modular inverses. Only use `pow(x, p-2, p)` when the modulus p is a known prime (e.g., FB primes in CRT).

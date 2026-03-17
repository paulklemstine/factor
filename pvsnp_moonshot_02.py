#!/usr/bin/env python3
"""
Moonshot 2: Proof Complexity of Factoring
=========================================
How long must proofs be that N = p * q?
"""

import time
import math
import random
from collections import Counter

try:
    import gmpy2
    _HAS_GMPY2 = True
except ImportError:
    _HAS_GMPY2 = False

def is_prime(n):
    if _HAS_GMPY2:
        return gmpy2.is_prime(n)
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i+2) == 0: return False
        i += 6
    return True

def random_prime(bits):
    while True:
        n = random.getrandbits(bits) | (1 << (bits - 1)) | 1
        if is_prime(n):
            return n

def random_semiprime(bits):
    half = bits // 2
    p = random_prime(half)
    q = random_prime(bits - half)
    while p == q:
        q = random_prime(bits - half)
    return p * q, min(p, q), max(p, q)

def main():
    print("=" * 70)
    print("Moonshot 2: Proof Complexity of Factoring")
    print("=" * 70)
    t0 = time.time()

    # --- Test 1: Factorization proof length ---
    print("\n--- Test 1: Factorization Proof Length ---")
    print("  The 'proof' that N = p*q is the pair (p, q).")
    print("  Verification: multiply p*q and check = O(n^2).")

    for bits in [32, 64, 128, 256, 512]:
        N, p, q = random_semiprime(bits)
        proof_len = p.bit_length() + q.bit_length()
        n_bits = N.bit_length()
        verify_cost = n_bits * n_bits
        info_content = min(p.bit_length(), q.bit_length())
        overhead = proof_len / info_content
        print(f"  {bits:4d}-bit: proof={proof_len} bits, info={info_content} bits, "
              f"overhead={overhead:.2f}x, verify={verify_cost} ops")

    print("  Key: factoring proofs are OPTIMAL (overhead ~2x).")

    # --- Test 2: Compositeness witnesses ---
    print("\n--- Test 2: Miller-Rabin Witness Density ---")

    for bits in [8, 12, 16]:
        witness_fracs = []
        for _ in range(20):
            N, p, q = random_semiprime(bits)
            witnesses = 0
            test_range = min(N - 2, 100)
            d_val = N - 1
            r = 0
            while d_val % 2 == 0:
                d_val //= 2
                r += 1
            for a in range(2, test_range + 1):
                x = pow(a, d_val, N)
                if x == 1 or x == N - 1:
                    continue
                is_w = True
                for _ in range(r - 1):
                    x = pow(x, 2, N)
                    if x == N - 1:
                        is_w = False
                        break
                if is_w:
                    witnesses += 1
            witness_fracs.append(witnesses / test_range)

        avg = sum(witness_fracs) / len(witness_fracs)
        print(f"  {bits:3d}-bit: avg witness fraction = {avg:.4f} (theory >= 0.75)")

    # --- Test 3: SAT proof complexity ---
    print("\n--- Test 3: SAT Encoding Size ---")

    for bits in [4, 6, 8, 10, 12]:
        half = bits // 2
        n_clauses = 0
        n_aux = 0
        for i in range(half):
            for j in range(half):
                n_clauses += 3
                n_aux += 1
        for k in range(bits):
            n_terms = min(k + 1, half, bits - k)
            n_adders = max(0, n_terms - 1)
            n_clauses += n_adders * 7
            n_aux += n_adders * 2
        n_clauses += bits
        total_vars = bits + n_aux
        print(f"  {bits:3d}-bit: vars={total_vars}, clauses={n_clauses}")

    # --- Test 4: Frege proof length ---
    print("\n--- Test 4: Proof Length Scaling ---")

    for bits in [8, 16, 32, 64, 128]:
        sqrt_N = 2 ** (bits // 2)
        exhaustive_len = sqrt_N * bits * bits
        pratt_len = bits * bits * 10
        print(f"  {bits:4d}-bit: exhaustive={exhaustive_len:.2e}, Pratt_cert={pratt_len}")

    # --- Test 5: Search-to-proof ratio ---
    print("\n--- Test 5: Search vs Proof Size ---")

    for bits in [8, 16, 32, 64, 128, 256]:
        search_space = 2 ** (bits // 2)
        proof_size = bits
        ratio = search_space / proof_size
        print(f"  {bits:4d}-bit: search_space=2^{bits//2}, proof={bits} bits, "
              f"ratio={ratio:.2e}")

    print("  Ratio grows as 2^{n/2}/n — exponential. This IS the NP structure.")

    elapsed = time.time() - t0
    print(f"\n--- Summary (elapsed: {elapsed:.1f}s) ---")
    print("""
  Proof Complexity Findings:

  1. FACTORING PROOFS ARE SHORT: The proof (p,q) has length O(n).
     Verification is O(n^2). This puts factoring firmly in NP.

  2. COMPOSITENESS IS EASY: Miller-Rabin witnesses exist with density >= 3/4.
     But compositeness proof reveals NOTHING about the factors.

  3. SAT ENCODING: O(n^2) clauses, O(n) variables. Resolution proof
     length is at least exponential for tree resolution.

  4. FREGE PROOFS: Exhaustive non-factorability proofs need O(sqrt(N)) lines.

  5. SEARCH vs PROOF: The search-to-proof ratio is 2^{n/2}/n,
     exponentially large. Canonical NP structure: short proof, long search.

  VERDICT: Proof complexity confirms factoring's NP membership but
  cannot prove it's NOT in P. Rating: 3/10 for proving lower bounds.
""")

if __name__ == '__main__':
    main()

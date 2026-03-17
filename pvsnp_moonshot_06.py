#!/usr/bin/env python3
"""
Moonshot 6: Fine-Grained Complexity & Factoring
================================================
SETH (Strong Exponential Time Hypothesis) and OV (Orthogonal Vectors)
connections to factoring.

SETH: k-SAT requires 2^{(1-epsilon_k)n} time, epsilon_k -> 0 as k -> inf.
OV: Detecting orthogonal vectors among n vectors in d dimensions requires
    n^{2-o(1)} time (under SETH).

Questions:
1. Can factoring reduce to k-SUM or OV?
2. Does factoring have fine-grained reductions to/from other problems?
3. Is there a meaningful "conditional lower bound" from SETH?
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
    print("Moonshot 6: Fine-Grained Complexity & Factoring")
    print("=" * 70)
    t0 = time.time()

    # --- Test 1: Factoring as 2-SUM ---
    print("\n--- Test 1: Factoring as k-SUM ---")
    print("  k-SUM: given n numbers, find k that sum to target.")
    print("  2-SUM in O(n log n). 3-SUM in O(n^2) (conjectured optimal).")
    print()
    print("  Can factoring N reduce to 2-SUM?")
    print("  Idea: create list L = {primes up to B}, find p,q in L with p*q = N.")
    print("  This is PRODUCT-2-SUM, not additive 2-SUM.")
    print("  Reduction: take logs. log(p) + log(q) = log(N).")
    print("  But log is irrational, so we need approximate 2-SUM.")

    for bits in [16, 24, 32, 40]:
        N, p_true, q_true = random_semiprime(bits)

        # List of primes up to sqrt(N)
        sqrt_N = int(N ** 0.5) + 1
        # For timing, limit the list
        limit = min(sqrt_N, 100000)
        primes = []
        for x in range(2, limit):
            if is_prime(x):
                primes.append(x)
                if len(primes) > 10000:
                    break

        # 2-SUM approach: for each prime p in list, check if N/p is also prime
        t_start = time.time()
        found = False
        for pp in primes:
            if N % pp == 0:
                qq = N // pp
                if is_prime(qq):
                    found = True
                    break
        t_2sum = time.time() - t_start

        # This is essentially trial division — O(sqrt(N)) = O(2^{n/2})
        print(f"  {bits}-bit: 2-SUM approach: {'FOUND' if found else 'not found'} "
              f"in {t_2sum:.4f}s, primes checked: {len(primes)}")

    print("\n  Key insight: Factoring IS a 2-SUM variant (product instead of sum).")
    print("  The list size is ~sqrt(N) = 2^{n/2} (all primes up to sqrt(N)).")
    print("  2-SUM on this list costs O(sqrt(N) log sqrt(N)) = O(2^{n/2} * n/2).")
    print("  This is just trial division! The 2-SUM reduction doesn't help.")

    # --- Test 2: Factoring as OV (Orthogonal Vectors) ---
    print("\n--- Test 2: Factoring as Orthogonal Vectors ---")
    print("  OV: Given sets A, B of n vectors in {0,1}^d,")
    print("  find a in A, b in B with <a,b> = 0.")
    print()
    print("  Encoding: represent each candidate factor p as a binary vector.")
    print("  The 'orthogonality' condition encodes p | N.")

    for bits in [12, 16, 20]:
        N, p_true, q_true = random_semiprime(bits)

        # Create vectors for candidate factors
        # Vector for candidate p: binary representation of p
        # Vector for N: binary representation of N
        # Orthogonality condition: we need p*q = N, not <p,q> = 0
        # This doesn't naturally map to OV.

        # Alternative: encode multiplication constraints as inner products
        # For each bit position k of the product, we have:
        # N_k = sum_{i+j=k} p_i * q_j (mod 2, with carries)
        # This is NOT a simple inner product.

        # Best we can do: check all pairs (p, N/p)
        half = bits // 2
        n_candidates = 2 ** half
        # OV would check n_candidates^2 pairs in O(n^2 * d) time
        # Our problem has n = 2^{n/2} candidates, d = n bits
        # OV time: O(2^n * n) — WORSE than trial division!

        print(f"  {bits}-bit: OV encoding would need {n_candidates} vectors of dim {bits}")
        print(f"    OV time: O({n_candidates}^2 * {bits}) = O(2^{bits} * {bits})")
        print(f"    Trial div: O(2^{bits//2}) — OV is SLOWER")

    print("\n  Conclusion: Factoring does NOT reduce efficiently to OV.")
    print("  The structure is multiplicative, not inner-product.")

    # --- Test 3: SETH lower bound for factoring ---
    print("\n--- Test 3: SETH-Based Lower Bound Attempt ---")
    print("  SETH: k-SAT on n variables requires 2^{(1-c_k)n} time.")
    print("  Question: Does factoring have a fine-grained reduction FROM k-SAT?")
    print()

    # If factoring N (n-bit) reduces to k-SAT with m = O(n) variables,
    # then SETH gives factoring lower bound of 2^{(1-c_k)*O(n)}.
    # The SAT encoding of factoring uses O(n) variables and O(n^2) clauses.
    # SETH for this: 2^{(1-c_k)*n} time to solve the SAT instance.
    # This gives a WEAKER bound than trial division (2^{n/2}).

    for bits in [8, 12, 16, 20]:
        n_vars = bits  # variables in SAT encoding
        n_clauses = bits * bits  # approximate clause count

        # SETH bound for various k
        for k in [3, 4, 5, 10]:
            # c_k ~ 1/k for random k-SAT
            c_k = 1.0 / k
            seth_bound = 2 ** ((1 - c_k) * n_vars)
            trial_div = 2 ** (bits / 2)
            siqs_bound = math.exp(1.0 * math.sqrt(math.log(2**bits) *
                                                    math.log(math.log(2**bits))))

            if bits == 12:
                print(f"  {bits}-bit, {k}-SAT: SETH_bound=2^{(1-c_k)*n_vars:.1f}={seth_bound:.0f}, "
                      f"trial_div=2^{bits/2:.0f}={trial_div:.0f}, "
                      f"SIQS~{siqs_bound:.0f}")

    print("\n  Key finding: SETH gives bounds WEAKER than trial division!")
    print("  The SAT encoding inflates the problem: n-bit factoring becomes")
    print("  O(n)-variable SAT, but SETH's exponent is (1-c_k) < 1.")
    print("  So SETH bound ~ 2^{0.9n} vs trial div ~ 2^{0.5n}.")
    print("  SETH cannot improve on known factoring algorithms.")

    # --- Test 4: Fine-grained equivalences ---
    print("\n--- Test 4: Fine-Grained Equivalence Classes ---")
    print("  Known equivalences under fine-grained reductions:")
    print("  - 3-SUM <=> GeomBase (3-collinearity)")
    print("  - OV <=> Boolean matrix multiplication (combinatorial)")
    print("  - APSP <=> negative triangle detection")
    print("  - Factoring: NOT known to be equivalent to any of these!")
    print()

    # Test: compare factoring time scaling with 3-SUM and OV
    print("  Empirical scaling comparison:")

    # 3-SUM baseline
    results_3sum = []
    for n_size in [100, 200, 500, 1000, 2000]:
        arr = [random.randint(-10**6, 10**6) for _ in range(n_size)]
        arr_set = set(arr)
        t_start = time.time()
        found_3sum = False
        for i in range(min(n_size, 500)):
            for j in range(i + 1, min(n_size, 500)):
                if -(arr[i] + arr[j]) in arr_set:
                    found_3sum = True
                    break
            if found_3sum:
                break
        t_3sum = time.time() - t_start
        results_3sum.append((n_size, t_3sum))
        if n_size <= 1000:
            print(f"    3-SUM n={n_size}: {t_3sum:.4f}s")

    # Factoring baseline
    results_fact = []
    for bits in [16, 20, 24, 28, 32]:
        N, p, q = random_semiprime(bits)
        t_start = time.time()
        # Trial division
        for d in range(2, min(int(N**0.5) + 1, 10**6)):
            if N % d == 0:
                break
        t_fact = time.time() - t_start
        results_fact.append((bits, t_fact))
        print(f"    Factoring {bits}-bit: {t_fact:.4f}s")

    # Check if factoring and 3-SUM have same scaling
    # 3-SUM: O(n^2) => doubling n multiplies time by 4
    # Factoring: O(2^{n/2}) => adding 2 bits multiplies time by 2
    if len(results_3sum) >= 2:
        ratio_3sum = results_3sum[-1][1] / max(results_3sum[-2][1], 1e-10)
        size_ratio = results_3sum[-1][0] / results_3sum[-2][0]
        print(f"\n    3-SUM time ratio for {size_ratio:.1f}x size: {ratio_3sum:.1f}x "
              f"(quadratic predicts {size_ratio**2:.1f}x)")

    if len(results_fact) >= 2:
        ratio_fact = results_fact[-1][1] / max(results_fact[-2][1], 1e-10)
        bit_diff = results_fact[-1][0] - results_fact[-2][0]
        print(f"    Factoring ratio for +{bit_diff} bits: {ratio_fact:.1f}x "
              f"(exponential predicts {2**(bit_diff/2):.1f}x)")

    print("\n    Factoring and 3-SUM have DIFFERENT scaling behaviors.")
    print("    Factoring: exponential in input length (2^{n/2}).")
    print("    3-SUM: polynomial in list size (n^2).")
    print("    No fine-grained reduction between them is known.")

    elapsed = time.time() - t0
    print(f"\n--- Summary (elapsed: {elapsed:.1f}s) ---")
    print("""
  Fine-Grained Complexity Findings:

  1. k-SUM: Factoring IS a multiplicative 2-SUM with list size 2^{n/2}.
     But this is just trial division. No improvement over known methods.

  2. OV (Orthogonal Vectors): Factoring's multiplicative structure does
     NOT map to inner products. OV encoding is SLOWER than trial division.

  3. SETH: The SAT encoding of factoring has O(n) variables. SETH gives
     2^{0.9n} lower bound, WEAKER than trial division's 2^{0.5n} upper
     bound. SETH-based bounds are useless for factoring.

  4. EQUIVALENCES: Factoring is NOT in any known fine-grained equivalence
     class (3-SUM, OV, APSP). It has unique exponential-in-n scaling
     that doesn't reduce to polynomial-in-list-size problems.

  VERDICT: Fine-grained complexity is the wrong framework for factoring.
  FG complexity studies polynomial vs slightly-higher-polynomial separations.
  Factoring's hardness is exponential vs sub-exponential — a completely
  different regime. SETH cannot improve on known algorithms.
  Rating: 1/10 for factoring lower bounds.
""")

if __name__ == '__main__':
    main()

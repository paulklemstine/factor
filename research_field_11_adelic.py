"""Field 11: Adelic Analysis - Simultaneous p-adic Structure Across All Primes
Hypothesis: The adele ring A_Q = R × prod_p Q_p gives a simultaneous view of N
across all p-adic completions. The diagonal embedding Z -> A_Q maps N to its
"adelic fingerprint". If we can detect the p-adic components where N vanishes
(i.e., the primes dividing N), we factor N. Test: does partial adelic information
(small primes) give statistical signal about the large prime factors?
"""
import time, math, random
import numpy as np

def padic_expansion(n, p, precision=10):
    """Compute p-adic expansion of n: n = a_0 + a_1*p + a_2*p^2 + ..."""
    digits = []
    x = n
    for _ in range(precision):
        digits.append(x % p)
        x //= p
    return digits

def adelic_fingerprint(N, primes, precision=8):
    """Compute the adelic fingerprint: (N mod p, N mod p^2, ..., N mod p^k) for each p."""
    fingerprint = {}
    for p in primes:
        fingerprint[p] = padic_expansion(N, p, precision)
    return fingerprint

def adelic_correlation(N, p_factor, q_factor, small_primes):
    """Test: do p-adic expansions at small primes correlate with factor structure?
    Specifically: does the pattern of N mod small_prime predict anything about
    the large factors p and q?
    """
    # For each small prime r, N mod r = (p*q) mod r = (p mod r)*(q mod r) mod r
    # This gives us a system of equations: x*y = N mod r for each r
    # This is the CRT approach - it's equivalent to solving a system of
    # quadratic congruences

    residues = [(r, N % r) for r in small_primes]

    # For each small prime r, count solutions to x*y = N mod r
    solutions_per_prime = {}
    for r, nr in residues:
        sols = []
        for x in range(r):
            for y in range(r):
                if (x * y) % r == nr:
                    sols.append((x, y))
        solutions_per_prime[r] = sols

        # Check if actual factors are among solutions
        actual = (p_factor % r, q_factor % r)
        is_present = actual in sols or (actual[1], actual[0]) in sols
        # This is always true by construction

    # CRT reconstruction: try to combine solutions across primes
    # This is essentially the index calculus / sieve approach
    # Number of combinations = prod(len(sols)) ~ prod(r) = exp(sum(log r))
    total_combinations = 1
    for r in small_primes:
        total_combinations *= len(solutions_per_prime[r])

    return solutions_per_prime, total_combinations

def experiment():
    print("=== Field 11: Adelic Analysis ===\n")

    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]

    random.seed(42)
    test_cases = []
    for bits in [16, 20, 24, 28, 32]:
        while True:
            p = random.getrandbits(bits // 2) | (1 << (bits//2 - 1)) | 1
            q = random.getrandbits(bits // 2) | (1 << (bits//2 - 1)) | 1
            if p != q and p > 2 and q > 2:
                if all(p % d != 0 for d in range(2, min(int(p**0.5)+1, 300))) and \
                   all(q % d != 0 for d in range(2, min(int(q**0.5)+1, 300))):
                    break
        test_cases.append((p, q, p*q, bits))

    print("  Test 1: Adelic fingerprints")
    for p, q, N, bits in test_cases[:3]:
        fp = adelic_fingerprint(N, small_primes[:5], precision=4)
        print(f"  {bits}b: N={N} = {p}*{q}")
        for r in small_primes[:5]:
            print(f"    {r}-adic: {fp[r]} (N mod {r} = {N % r})")

    print("\n  Test 2: Adelic solution counting")
    for p, q, N, bits in test_cases:
        t0 = time.time()
        sols, total_comb = adelic_correlation(N, p, q, small_primes[:6])
        elapsed = time.time() - t0

        print(f"  {bits}b: N={N}")
        for r in small_primes[:6]:
            nsols = len(sols[r])
            print(f"    mod {r}: {nsols} solutions to xy=N (mod {r})")
        print(f"    Total CRT combinations: {total_comb}")
        print(f"    vs search space sqrt(N) = {math.isqrt(N)}")
        print(f"    Time: {elapsed:.4f}s")

    print("\n  Adelic CRT analysis:")
    print("  To factor N via adelic approach: solve xy=N mod r for many small r,")
    print("  then combine via CRT. But number of solutions per prime ~ r,")
    print("  so total combinations ~ prod(r_i) grows EXPONENTIALLY in #primes.")
    print("  This is WORSE than trial division for large factors.")
    print("  The adelic approach is essentially the sieve method in disguise:")
    print("  SIQS/GNFS use the SAME per-prime congruence information.")

    print("\nVERDICT: Adelic analysis = looking at N mod r for many small primes r.")
    print("This is exactly what sieve methods (QS, NFS) already do.")
    print("The adelic framework is a beautiful reformulation but provides NO new")
    print("algorithmic content beyond existing sieve approaches.")
    print("RESULT: REFUTED (reduces to existing sieve methods)")

experiment()

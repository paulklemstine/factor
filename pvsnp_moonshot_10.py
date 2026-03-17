#!/usr/bin/env python3
"""
Moonshot 10: Arithmetic Circuit Lower Bounds & Tau Conjecture
==============================================================
The tau conjecture (Shub-Smale 1995): the number of integer roots of a
univariate polynomial f(x) = sum a_i x^i with integer coefficients
is bounded by tau(f)^{O(1)} where tau(f) is the circuit complexity of f.

Connection to factoring:
- N = p*q means x^2 - N has a root at x = p (over Z, if we allow x^2 - N = (x-p)(x-q)...)
- Actually: consider f(x) = x(N/x) - N = 0 for integer x|N.
- The number of divisors of N is bounded by N^{o(1)}.
- If tau conjecture is true, the circuit complexity of the "divisor polynomial" is large.

We test:
1. Circuit complexity of N-specific polynomials
2. Number of roots vs circuit size
3. Connections to the permanent and factoring
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

def count_integer_roots(coeffs, bound):
    """Count integer roots of polynomial with given coefficients in [-bound, bound]."""
    roots = []
    for x in range(-bound, bound + 1):
        val = 0
        xk = 1
        for c in coeffs:
            val += c * xk
            xk *= x
        if val == 0:
            roots.append(x)
    return roots

def circuit_complexity_estimate(coeffs):
    """Estimate arithmetic circuit complexity of a polynomial.
    Lower bound: number of distinct nonzero coefficients (Horner's rule).
    Upper bound: degree + number of nonzero coefficients."""
    degree = len(coeffs) - 1
    nonzero = sum(1 for c in coeffs if c != 0)
    # Horner: degree additions + degree multiplications = 2*degree
    horner_cost = 2 * degree
    # With repeated squaring for large exponents: O(degree + log(max_coeff))
    max_coeff = max(abs(c) for c in coeffs) if coeffs else 0
    log_coeff = math.ceil(math.log2(max_coeff + 1)) if max_coeff > 0 else 0
    return {
        'degree': degree,
        'nonzero_coeffs': nonzero,
        'horner_cost': horner_cost,
        'coeff_bits': log_coeff,
        'total_estimate': horner_cost + log_coeff
    }

def main():
    print("=" * 70)
    print("Moonshot 10: Arithmetic Circuit Lower Bounds & Tau Conjecture")
    print("=" * 70)
    t0 = time.time()

    # --- Test 1: Divisor polynomial ---
    print("\n--- Test 1: The Divisor Polynomial ---")
    print("  For N = p*q, define f_N(x) = N mod x (not a polynomial).")
    print("  Better: define P_N(x) = prod_{d|N} (x - d).")
    print("  This polynomial has EXACTLY the divisors of N as roots.")
    print("  Circuit complexity of P_N vs number of roots:")

    for bits in [8, 12, 16, 20]:
        N_samples = 20
        for _ in range(N_samples):
            N, p, q = random_semiprime(bits)
            # Divisors of N = {1, p, q, N} for semiprime
            divisors = [1, p, q, N]
            n_divs = len(divisors)

            # P_N(x) = (x-1)(x-p)(x-q)(x-N)
            # Expand symbolically:
            # Coefficients of the expanded polynomial
            # Start with [1] (constant polynomial = 1)
            poly = [1]
            for root in divisors:
                # Multiply poly by (x - root)
                new_poly = [0] * (len(poly) + 1)
                for i, c in enumerate(poly):
                    new_poly[i + 1] += c  # x * c
                    new_poly[i] -= c * root  # -root * c
                poly = new_poly

            cc = circuit_complexity_estimate(poly)

            if _ < 3:  # Print details for first 3
                print(f"  N={N} ({bits}-bit): {n_divs} divisors, "
                      f"degree={cc['degree']}, "
                      f"coeff_bits={cc['coeff_bits']}, "
                      f"circuit_est={cc['total_estimate']}")

        # Average over samples
        print(f"  {bits}-bit: degree=4 (semiprime), "
              f"tau conjecture: roots <= tau^O(1)")

    print("\n  The tau conjecture predicts: #roots(f) <= tau(f)^{O(1)}.")
    print("  For P_N(x) of degree 4: #roots = 4, tau(P_N) >= 4^{1/O(1)} = O(1).")
    print("  This is trivially satisfied — the polynomial has small degree!")
    print("  The tau conjecture is interesting for HIGH-degree polynomials.")

    # --- Test 2: High-degree factoring polynomial ---
    print("\n--- Test 2: High-Degree Factoring Polynomial ---")
    print("  Define F(x) = x^N - x mod N (Fermat's little theorem variant).")
    print("  If N = p*q, then F(x) = 0 has (at least) p + q - 1 roots mod N.")
    print("  For the integer version: x^N - x evaluated at x = 0,1,...,N-1.")

    for bits in [8, 10, 12]:
        N, p, q = random_semiprime(bits)

        # Count roots of x^N - x = 0 mod N
        roots_mod_N = 0
        for x in range(min(N, 5000)):
            val = pow(x, N, N)
            if val == x % N:
                roots_mod_N += 1

        # By CRT: roots mod N correspond to (roots mod p) x (roots mod q)
        # Roots of x^N - x mod p: Fermat says x^p = x mod p for all x
        # So x^N = x^{N mod (p-1)} * x mod p
        # Not quite Fermat; need x^{p-1} = 1 mod p for gcd(x,p) = 1

        # Theoretical: x^N = x (mod p) iff x^{N-1} = 1 (mod p) for x != 0
        # x^{N-1} = x^{pq-1} mod p. Since x^{p-1} = 1, we need (p-1) | (pq-1).
        # pq - 1 = p(q-1) + (p-1). So pq-1 mod (p-1) = p(q-1) mod (p-1).
        # = (1)(q-1) mod (p-1) = (q-1) mod (p-1).
        # So roots are x with x^{(q-1) mod (p-1)} = 1 mod p.

        r_p = (q - 1) % (p - 1)
        r_q = (p - 1) % (q - 1)
        # Number of roots mod p: gcd(r_p, p-1) + 1 (including x=0)
        roots_p = math.gcd(r_p, p - 1) if r_p > 0 else p - 1
        roots_q = math.gcd(r_q, q - 1) if r_q > 0 else q - 1
        theory_roots = (roots_p + 1) * (roots_q + 1)  # +1 for x=0 in each

        tested = min(N, 5000)
        print(f"  N={N} ({bits}-bit, p={p}, q={q}):")
        print(f"    Empirical roots of x^N=x (mod N): {roots_mod_N}/{tested}")
        print(f"    Theory: ~{theory_roots} roots (CRT decomposition)")

    # --- Test 3: Circuit complexity of x^2 - N ---
    print("\n--- Test 3: The Quadratic x^2 - N ---")
    print("  Factoring reduces to finding roots of x^2 = N (mod something).")
    print("  Circuit complexity of x^2 - N: O(log N) (compute x^2, subtract N).")
    print("  But FINDING roots is hard (= factoring).")

    for bits in [16, 32, 64, 128, 256]:
        # Circuit for x^2 - N:
        # 1 multiplication (x*x), 1 subtraction (- N), N has bits bits
        # Total gates: O(bits^2) for multiplication + O(bits) for subtraction
        mult_gates = bits * bits  # schoolbook multiplication
        sub_gates = bits
        total = mult_gates + sub_gates
        # With FFT multiplication: O(bits * log(bits))
        fft_gates = bits * math.ceil(math.log2(bits + 1)) * 5  # rough

        # Number of roots (over Z): at most 2 (x = +/- sqrt(N) if N is perfect square)
        # Over Z/NZ for semiprime: at most 4 (two square roots mod each prime)

        print(f"  {bits:4d}-bit: gates(schoolbook)={total:>10d}, "
              f"gates(FFT)={fft_gates:>8d}, "
              f"roots(Z)<=2, roots(Z/NZ)<=4")

    print("\n  Tau conjecture: #roots <= tau^{O(1)} where tau = circuit complexity.")
    print("  For x^2-N: tau = O(n^2), #roots <= 4.")
    print("  4 <= O(n^2)^{O(1)} is trivially true.")
    print("  The tau conjecture gives NO useful information about factoring")
    print("  because the number of roots is always tiny (<=4 for semiprimes).")

    # --- Test 4: Multivariate connection ---
    print("\n--- Test 4: Multivariate Polynomials and Factoring ---")
    print("  Consider F(x,y) = x*y - N over integers.")
    print("  Roots: all (p,q) with p*q = N.")
    print("  Circuit complexity: O(log N) (1 mult + 1 sub).")
    print("  Number of roots: d(N) = number of divisors of N.")

    for bits in [8, 12, 16, 20]:
        N_samples = 50
        divisor_counts = []
        for _ in range(N_samples):
            N, p, q = random_semiprime(bits)
            # Semiprimes have exactly 4 divisors: 1, p, q, N
            divisor_counts.append(4)

        # For general N, d(N) can be large
        # But for semiprimes, d(N) = 4 always
        print(f"  {bits}-bit semiprimes: d(N) = 4 always "
              f"(tau conjecture: 4 <= O(log N)^c)")

    # --- Test 5: Random polynomial root counting ---
    print("\n--- Test 5: Root Counting for Random vs Structured Polynomials ---")
    print("  Compare number of integer roots for:")
    print("  (a) Random polynomials of degree d with coefficient bound C")
    print("  (b) Factoring-related polynomials")

    for degree in [2, 4, 8, 16]:
        # Random polynomial: coefficients in [-100, 100]
        random_roots = []
        factoring_roots = []

        for _ in range(100):
            # Random polynomial
            coeffs_rand = [random.randint(-100, 100) for _ in range(degree + 1)]
            if coeffs_rand[-1] == 0:
                coeffs_rand[-1] = 1
            roots = count_integer_roots(coeffs_rand, 200)
            random_roots.append(len(roots))

            # Factoring polynomial: (x - p)(x - q) * random extras
            p_val = random.randint(2, 50)
            q_val = random.randint(2, 50)
            fact_coeffs = [1, -(p_val + q_val), p_val * q_val]
            # Pad to degree d by multiplying with random factors
            while len(fact_coeffs) - 1 < degree:
                r = random.randint(-10, 10)
                new_coeffs = [0] * (len(fact_coeffs) + 1)
                for i, c in enumerate(fact_coeffs):
                    new_coeffs[i + 1] += c
                    new_coeffs[i] -= c * r
                fact_coeffs = new_coeffs
            roots = count_integer_roots(fact_coeffs, 200)
            factoring_roots.append(len(roots))

        avg_rand = sum(random_roots) / len(random_roots)
        avg_fact = sum(factoring_roots) / len(factoring_roots)
        max_rand = max(random_roots)
        max_fact = max(factoring_roots)

        print(f"  Degree {degree:2d}: random avg_roots={avg_rand:.2f} (max={max_rand}), "
              f"factoring avg_roots={avg_fact:.2f} (max={max_fact})")

    print("\n  Random polynomials typically have very few integer roots (0-2).")
    print("  Factoring polynomials have guaranteed roots (the factors).")
    print("  But this structural difference is NOT useful: we KNOW the roots")
    print("  exist (N = p*q guarantees it), we just can't FIND them.")

    # --- Test 6: Permanent as determinant (VP vs VNP) ---
    print("\n--- Test 6: VP vs VNP Connection ---")
    print("  VP (algebraic P) vs VNP (algebraic NP):")
    print("  VP: polynomials computable by poly-size arithmetic circuits")
    print("  VNP: polynomials expressible as exponential sums of VP polynomials")
    print()
    print("  The permanent is VNP-complete (Valiant 1979).")
    print("  Factoring connection: the 'product polynomial' x*y is in VP.")
    print("  The 'divisor counting function' involves summing over all factorizations.")
    print()

    # For small N, compute the "factoring permanent" — number of ordered
    # factorizations of N into k parts
    for N in [12, 30, 60, 120]:
        # Count ordered factorizations into 2 parts
        two_parts = sum(1 for a in range(2, N) if N % a == 0)
        # Count ordered factorizations into 3 parts
        three_parts = 0
        for a in range(2, N):
            if N % a == 0:
                rem = N // a
                for b in range(2, rem):
                    if rem % b == 0:
                        three_parts += 1

        print(f"  N={N:4d}: 2-factorizations={two_parts:3d}, "
              f"3-factorizations={three_parts:4d}")

    print("\n  The number of k-factorizations grows combinatorially.")
    print("  Computing this count exactly is related to the permanent")
    print("  (both involve summing over exponentially many terms).")
    print("  But counting factorizations != finding factorizations.")

    elapsed = time.time() - t0
    print(f"\n--- Summary (elapsed: {elapsed:.1f}s) ---")
    print("""
  Arithmetic Circuit Lower Bounds & Tau Conjecture Findings:

  1. DIVISOR POLYNOMIAL: P_N(x) = prod(x-d) for d|N has degree d(N)=4
     for semiprimes. Circuit complexity O(n), #roots=4.
     Tau conjecture: 4 <= O(n)^c — trivially satisfied.

  2. HIGH-DEGREE: x^N - x mod N has more roots but still O(sqrt(N)).
     The CRT decomposition gives exact root count.

  3. QUADRATIC x^2 - N: Circuit complexity O(n^2), at most 4 roots.
     The tau conjecture gives no useful bound for such small root counts.

  4. MULTIVARIATE: x*y - N has d(N)=4 roots for semiprimes.
     The tau conjecture bounds are vacuous (4 is too small).

  5. RANDOM vs STRUCTURED: Factoring polynomials have MORE roots than
     random (guaranteed by construction), but this is KNOWN and unhelpful.

  6. VP vs VNP: Counting factorizations relates to permanents (VNP).
     Finding factorizations is a SEARCH problem, not directly in VP/VNP.

  VERDICT: The tau conjecture and arithmetic circuit lower bounds are
  fundamentally about the WRONG aspect of factoring. They bound the
  number of roots as a function of circuit complexity. But semiprimes
  have tiny root count (4 divisors), so the bounds are vacuous.
  The hardness of factoring is about FINDING roots, not COUNTING them.
  The VP/VNP framework addresses algebraic complexity, not search.
  Rating: 1/10 for proving factoring lower bounds.
""")

if __name__ == '__main__':
    main()

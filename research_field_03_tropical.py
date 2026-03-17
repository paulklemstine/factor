"""Field 3: Tropical Geometry - Min-Plus Algebra for Factoring
Hypothesis: In tropical (min-plus) semiring, multiplication becomes addition and
addition becomes min. The tropical variety of xy=N (i.e., min(x+y, ...) = trop(N))
might have a simpler geometric structure than the classical variety. Tropical
Newton polygons could reveal factor-size information via vertex structure.
"""
import time, math, random

def tropical_add(a, b):
    """Tropical addition = min"""
    return min(a, b)

def tropical_mul(a, b):
    """Tropical multiplication = ordinary addition"""
    return a + b

def tropical_valuation(n, p):
    """p-adic valuation: max k such that p^k | n"""
    if n == 0:
        return float('inf')
    v = 0
    while n % p == 0:
        v += 1
        n //= p
    return v

def tropical_newton_polygon(N, primes):
    """Compute tropical Newton polygon of N with respect to given primes.
    The Newton polygon of N encodes its p-adic valuations."""
    points = []
    for i, p in enumerate(primes):
        v = tropical_valuation(N, p)
        points.append((i, v))
    return points

def tropical_factoring_test(N, p, q):
    """Test: does tropical geometry of xy=N reveal factors?
    In tropical coordinates, if N=pq then:
      v_r(N) = v_r(p) + v_r(q) for every prime r
    The tropical variety of xy=N is: for each prime r, v_r(x) + v_r(y) = v_r(N).
    """
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]

    # Tropical "fingerprint" of N
    vals_N = [tropical_valuation(N, r) for r in small_primes]
    vals_p = [tropical_valuation(p, r) for r in small_primes]
    vals_q = [tropical_valuation(q, r) for r in small_primes]

    # Verify: v(N) = v(p) + v(q) for all primes
    decomp_ok = all(vals_N[i] == vals_p[i] + vals_q[i] for i in range(len(small_primes)))

    # Key insight test: for RSA semiprimes, ALL small-prime valuations of N are 0
    # (since p,q are large primes, they have no small factors)
    all_zero = all(v == 0 for v in vals_N)

    return vals_N, decomp_ok, all_zero

def tropical_polynomial_test(N):
    """Test tropical roots of f(x) = x^2 - N in tropical semiring.
    Tropical roots correspond to slopes of Newton polygon of f.
    For f(x) = x^2 + N (tropicalized), Newton polygon has vertices
    at (0, log(N)) and (2, 0), giving tropical root = log(N)/2 = log(sqrt(N)).
    """
    # Tropical root of x^2 = N is log(N)/2
    trop_root = math.log(N) / 2 if N > 0 else 0

    # This tells us sqrt(N) is the "tropical factor"
    # For N=pq, sqrt(N) = sqrt(pq) which is between p and q
    # This is just the known bound, not new information
    return trop_root, math.exp(trop_root)

def experiment():
    print("=== Field 3: Tropical Geometry for Factoring ===\n")

    test_cases = []
    random.seed(42)
    for bits in [20, 30, 40, 50, 60]:
        while True:
            p = random.getrandbits(bits // 2) | (1 << (bits//2 - 1)) | 1
            q = random.getrandbits(bits // 2) | (1 << (bits//2 - 1)) | 1
            if p != q and p > 2 and q > 2:
                # Quick primality
                is_p = all(p % d != 0 for d in range(2, min(int(p**0.5)+1, 1000)))
                is_q = all(q % d != 0 for d in range(2, min(int(q**0.5)+1, 1000)))
                if is_p and is_q:
                    break
        test_cases.append((p, q, p*q, bits))

    for p, q, N, bits in test_cases:
        t0 = time.time()

        vals_N, decomp_ok, all_zero = tropical_factoring_test(N, p, q)
        trop_root, sqrt_est = tropical_polynomial_test(N)
        elapsed = time.time() - t0

        print(f"  {bits}b: N={N}, p={p}, q={q}")
        print(f"    Valuations v_r(N) for r=2..47: {vals_N}")
        print(f"    Decomposition v(N)=v(p)+v(q): {decomp_ok}")
        print(f"    All valuations zero (RSA-like): {all_zero}")
        print(f"    Tropical root (log-space sqrt): {sqrt_est:.1f} vs sqrt(N)={math.isqrt(N)}")
        print(f"    Time: {elapsed:.6f}s")

    # Deeper test: tropical convexity
    print("\n  Tropical convexity test:")
    print("  For N=pq, the tropical variety of xy=N in (v_2, v_3, ...) space is")
    print("  the set of all (v(x), v(y)) with v(x)+v(y)=v(N).")
    print("  For RSA semiprimes, v_r(N)=0 for all small r, so the tropical variety")
    print("  is just {(0,0)} in every coordinate. NO INFORMATION.")

    print("\nVERDICT: Tropical geometry provides zero information for RSA semiprimes.")
    print("All small-prime valuations are 0 (since factors are large primes).")
    print("Tropical root = sqrt(N) is already known. No new structure.")
    print("RESULT: REFUTED")

experiment()

"""Field 6: Category Theory - Functorial Relationships Between Factoring and Other Problems
Hypothesis: There might be a functor from the category of semiprimes (with divisibility
morphisms) to a category where factoring is easier (e.g., linear algebra over finite
fields). If such a structure-preserving map exists, we could factor by computing in the
image category. Test: Chinese Remainder Theorem as a functor Z/NZ -> Z/pZ x Z/qZ.
"""
import time, math, random

def crt_functor_test(N, p, q):
    """CRT gives an isomorphism Z/NZ ≅ Z/pZ × Z/qZ.
    This IS the factoring - knowing p,q IS the factorization.
    Test: can we detect the product structure without knowing p,q?
    """
    # The ring Z/NZ has certain categorical properties:
    # - Number of idempotents (elements e with e^2=e)
    # - Number of units (invertible elements)
    # - Number of zero divisors

    # For N=pq: idempotents = {0, 1, e_p, e_q} where e_p = 1 mod p, 0 mod q
    # Finding idempotents IS equivalent to factoring

    # Count idempotents by brute force (small N only)
    idempotents = []
    if N < 100000:
        for x in range(N):
            if (x * x) % N == x:
                idempotents.append(x)
    return idempotents

def natural_transformation_test(N):
    """Test: endomorphisms of Z/NZ as a ring.
    Ring endomorphisms f: Z/NZ -> Z/NZ must satisfy f(1)^2 = f(1).
    So endomorphisms correspond to idempotents.
    For N=pq: there are exactly 4 idempotents (and 4 ring endomorphisms).
    For N prime: only 2 ({0, 1}).
    Detecting 4 vs 2 endomorphisms distinguishes prime from semiprime.
    """
    # This is just counting idempotents, which requires factoring.
    pass

def adjunction_test(N, p, q):
    """Test: is there an adjoint functor pair that 'lifts' information?
    The inclusion Z -> Z/NZ has a right adjoint (Hensel lifting).
    Test: does Hensel lifting of sqrt(N mod p^k) converge to a factor?
    """
    # Pick a small prime r where N is a QR
    results = []
    for r in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
        if r >= N:
            continue
        # Check if N is a QR mod r
        n_mod_r = N % r
        sqrt_found = None
        for x in range(r):
            if (x * x) % r == n_mod_r:
                sqrt_found = x
                break
        if sqrt_found is not None:
            # Hensel lift: x_{k+1} = x_k - f(x_k)/f'(x_k) mod r^{k+1}
            # where f(x) = x^2 - N
            x = sqrt_found
            modulus = r
            for k in range(10):
                modulus *= r
                if modulus > N:
                    break
                # Newton step mod modulus
                fx = (x * x - N) % modulus
                fpx = (2 * x) % modulus
                # Need fpx invertible mod modulus
                g = math.gcd(fpx, modulus)
                if g > 1:
                    # fpx not invertible - this means gcd(2x, r^k) > 1
                    # which happens when r | 2x
                    factor_candidate = math.gcd(fpx, N)
                    if 1 < factor_candidate < N:
                        results.append((r, k, factor_candidate, "FACTOR from Hensel!"))
                    break
                fpx_inv = pow(fpx, -1, modulus)
                x = (x - fx * fpx_inv) % modulus

            # Check if lifted sqrt reveals factor
            g1 = math.gcd(x - int(math.isqrt(N)), N)
            g2 = math.gcd(x + int(math.isqrt(N)), N)
            if 1 < g1 < N:
                results.append((r, 10, g1, "FACTOR from sqrt lift!"))
            elif 1 < g2 < N:
                results.append((r, 10, g2, "FACTOR from sqrt lift!"))
    return results

def experiment():
    print("=== Field 6: Category Theory - Functorial Factoring ===\n")

    test_cases = [(3, 5), (7, 11), (13, 17), (23, 29), (37, 41), (101, 103),
                  (251, 257), (1009, 1013)]

    for p, q in test_cases:
        N = p * q
        t0 = time.time()

        # Test 1: Idempotents
        idem = crt_functor_test(N, p, q)
        if idem:
            nontrivial = [e for e in idem if e not in (0, 1)]
            # Nontrivial idempotents directly give factors
            factors_from_idem = [math.gcd(e, N) for e in nontrivial]
        else:
            nontrivial = []
            factors_from_idem = []

        # Test 2: Hensel lifting
        hensel_results = adjunction_test(N, p, q)

        elapsed = time.time() - t0

        print(f"  N={N} = {p}*{q}:")
        if idem:
            print(f"    Idempotents: {idem} -> factors: {factors_from_idem}")
        print(f"    Hensel lift results: {hensel_results[:3]}")
        print(f"    Time: {elapsed:.4f}s")

    print("\nVERDICT: Category theory correctly identifies that CRT is an isomorphism")
    print("and idempotents reveal factors. But FINDING idempotents requires factoring.")
    print("The functor Z/NZ -> Z/pZ x Z/qZ IS the factorization - it can't be computed")
    print("without already knowing the factors. Hensel lifting of square roots is the")
    print("basis of Tonelli-Shanks but requires knowing p. No categorical shortcut found.")
    print("RESULT: REFUTED")

experiment()

"""Field 20: Condensed Mathematics - Clausen-Scholze Framework
Hypothesis: Condensed mathematics (Clausen-Scholze) replaces topological spaces with
"condensed sets" (sheaves on profinite sets). This framework unifies p-adic and real
analysis. For factoring, the condensed structure of Z (as a condensed ring) might
provide new ways to detect the prime decomposition via the condensed cohomology
of Spec(Z/NZ). Test: does the profinite completion Z_hat = prod_p Z_p encode
factoring information more accessibly than the adelic approach?
"""
import time, math, random
import numpy as np

def profinite_approximation(N, depth=8):
    """Approximate the profinite completion of Z/NZ.
    Z_hat/NZ_hat ≅ prod_{p|N} Z_p/p^{v_p(N)} Z_p

    For N=pq (both prime): Z_hat/NZ_hat ≅ Z/pZ × Z/qZ.
    The profinite topology on this product has clopen sets corresponding
    to the two components.

    Test: can we detect the product decomposition from "local" information?
    """
    # Approximate profinite structure by looking at N mod m for increasing m
    # If N = pq, then for m divisible by p (but not q), the map Z/NZ -> Z/mZ
    # has a kernel of size q. This kernel detection = finding factors.

    small_moduli = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 16, 20, 24, 30]
    residue_data = {}
    for m in small_moduli:
        # Map Z/NZ -> Z/mZ: send x to x mod m
        # Kernel = {x in Z/NZ : x = 0 mod m} = set of multiples of m in Z/NZ
        kernel_size = N // math.gcd(N, m)  # Not quite right
        # Actually: |ker| = gcd(N, m) (number of x in [0,N) with x = 0 mod m times something)
        # No: the map Z/NZ -> Z/gcd(N,m)Z is surjective with kernel of size N/gcd(N,m)
        g = math.gcd(N, m)
        residue_data[m] = {
            "gcd(N,m)": g,
            "image_size": g,
            "kernel_size": N // g,
            "reveals_factor": 1 < g < N,
        }

    return residue_data

def condensed_sheaf_test(N, p, q):
    """In condensed mathematics, Z/NZ is a condensed abelian group.
    Its "underlying condensed set" is determined by maps from profinite sets.
    For S = Spec(Z/NZ), the sections over a profinite set T are Hom(T, Z/NZ).

    Key: the decomposition Z/NZ ≅ Z/pZ × Z/qZ is a decomposition as condensed abelian groups.
    The "condensed" structure adds nothing beyond the algebraic decomposition.

    Test: does the cohomology H^n(Spec(Z/NZ), F) for various sheaves F
    detect the product structure?
    """
    # H^0 = global sections = Z/NZ itself
    # H^1 = Ext^1 groups = extensions of Z/NZ by other modules
    # For Z/NZ ≅ Z/pZ × Z/qZ:
    # H^1(Z/NZ, Z) = Hom(Z/NZ, Q/Z) ≅ Z/NZ (Pontryagin dual)
    # This has the SAME product structure.

    # The condensed approach via "solid modules" might give:
    # RHom(Z/NZ, Z) in D(Cond(Ab))
    # But this is just the derived functor computation, same as classical.

    return {
        "H0": f"Z/NZ ≅ Z/{p}Z × Z/{q}Z",
        "H1": f"Z/NZ (Pontryagin dual, same product structure)",
        "condensed_extra": "No additional information beyond classical algebra",
    }

def analytic_condensed_test(N):
    """Condensed mathematics' main innovation: handles topological algebra.
    For Z/NZ (discrete), condensed = classical. No gain.

    Where condensed math MIGHT help: the p-adic analysis of factoring.
    Test: the "liquid vector space" completion of Q_p gives a framework
    for p-adic analysis that might simplify sieve computations.
    """
    # p-adic analysis for sieving: smoothness = having only small prime factors
    # = N being "close to 0" in EVERY p-adic metric for p in the factor base
    # This is the adelic perspective, now dressed in condensed language.

    # Test: is the "norm" ||N||_{FB} = prod_{p in FB} |N|_p a useful quantity?
    FB = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    p_adic_norms = {}
    remaining = N
    for p in FB:
        v = 0
        while remaining % p == 0:
            remaining //= p
            v += 1
        p_adic_norms[p] = p ** (-v)  # |N|_p = p^{-v_p(N)}

    # Product formula: prod_v |N|_v = 1 (including archimedean)
    product = 1
    for p in FB:
        product *= p_adic_norms[p]
    # Archimedean: |N|_inf = N (for the formula to hold, need remaining cofactor)

    return p_adic_norms, product, remaining

def experiment():
    print("=== Field 20: Condensed Mathematics ===\n")

    test_cases = [(7, 11), (13, 17), (23, 29), (37, 41), (101, 103)]

    print("  Test 1: Profinite approximation")
    for p, q in test_cases[:3]:
        N = p * q
        data = profinite_approximation(N)
        print(f"  N={N} = {p}*{q}:")
        factor_revealing = [(m, d) for m, d in data.items() if d['reveals_factor']]
        non_revealing = [(m, d) for m, d in data.items() if not d['reveals_factor']]
        if factor_revealing:
            print(f"    Factor-revealing moduli: {[(m, d['gcd(N,m)']) for m, d in factor_revealing]}")
        print(f"    Non-revealing moduli: {[m for m, _ in non_revealing[:5]]}...")

    print("\n  Test 2: Condensed sheaf cohomology")
    for p, q in test_cases[:3]:
        N = p * q
        coh = condensed_sheaf_test(N, p, q)
        print(f"  N={N}: {coh['condensed_extra']}")

    print("\n  Test 3: p-adic norm analysis")
    random.seed(42)
    for bits in [16, 20, 24, 28, 32]:
        while True:
            p = random.getrandbits(bits // 2) | (1 << (bits//2 - 1)) | 1
            q = random.getrandbits(bits // 2) | (1 << (bits//2 - 1)) | 1
            if p != q and all(p % d != 0 for d in range(2, min(int(p**0.5)+1, 300))) and \
               all(q % d != 0 for d in range(2, min(int(q**0.5)+1, 300))):
                break
        N = p * q
        norms, product, remaining = analytic_condensed_test(N)
        # For RSA semiprimes: all small-prime norms = 1 (no small factors)
        all_trivial = all(v == 1.0 for v in norms.values())
        print(f"    {bits}b: all small-prime norms trivial: {all_trivial}, remaining cofactor: {remaining}")

    print("\n  Analysis:")
    print("  Condensed mathematics provides a unified framework for topological algebra.")
    print("  For DISCRETE rings like Z/NZ, condensed = classical (no new information).")
    print("  For p-adic analysis: condensed language simplifies foundations but")
    print("  the COMPUTATIONS are identical to classical p-adic analysis.")
    print("  For RSA semiprimes: all small-prime norms are 1 (factors are large primes),")
    print("  so the condensed/p-adic perspective gives zero signal.")

    print("\nVERDICT: Condensed mathematics is a foundational framework, not an algorithm.")
    print("For discrete objects (finite rings), it adds nothing to classical algebra.")
    print("For p-adic analysis, it's a language improvement, not a computational one.")
    print("The profinite/adelic perspective on factoring is well-studied (sieve methods).")
    print("Clausen-Scholze framework is brilliant mathematics but irrelevant to factoring.")
    print("RESULT: REFUTED")

experiment()

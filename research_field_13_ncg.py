"""Field 13: Noncommutative Geometry - Connes' Approach to Primes
Hypothesis: Alain Connes' noncommutative geometry program connects primes to
the spectral realization of zeros of the Riemann zeta function. The "arithmetic
site" and its operator-theoretic formulation might provide a spectral method
for detecting prime factors. Test: the Bost-Connes system at inverse temperature
beta has partition function zeta(beta), and its KMS states at beta=1 relate to primes.
"""
import time, math, random
import numpy as np

def bost_connes_partition(N, beta_values):
    """The Bost-Connes system has partition function Z(beta) = zeta(beta).
    At beta > 1, the system has a unique KMS state.
    At beta = 1, there's a phase transition.

    For factoring: the BC system restricted to divisors of N has
    partition function Z_N(beta) = sum_{d|N} d^{-beta}.
    This is the divisor function sigma_{-beta}(N).
    """
    # For N=pq: divisors are {1, p, q, pq}
    # Z_N(beta) = 1 + p^{-beta} + q^{-beta} + (pq)^{-beta}
    #           = (1 + p^{-beta})(1 + q^{-beta})

    # The key: Z_N factors as a PRODUCT over prime powers dividing N.
    # If we could DETECT this product structure from Z_N(beta),
    # we could factor N!

    # Compute Z_N(beta) for various beta
    results = {}
    for beta in beta_values:
        # Find all divisors of N (this IS factoring for large N)
        # For the test: compute as if we DON'T know the factorization
        # Use the fact that Z_N(beta) = sum_{d|N} d^{-beta}
        # We can approximate by summing over all d up to sqrt(N)
        z = 0
        sq = int(math.isqrt(N))
        for d in range(1, sq + 1):
            if N % d == 0:
                z += d**(-beta)
                if d != N // d:
                    z += (N // d)**(-beta)
        results[beta] = z

    return results

def spectral_approach(N, num_eigenvalues=50):
    """Connes' spectral realization: the zeros of zeta correspond to eigenvalues
    of an operator. For factoring, we'd want the spectrum of the "arithmetic"
    operator restricted to Z/NZ.

    Test: the operator D on L^2(Z/NZ) defined by (Df)(x) = x*f(x)
    has eigenvalues that are the elements of Z/NZ. The trace of exp(-t*D)
    is the "heat kernel" and encodes the spectrum.
    """
    # This is just the elements of Z/NZ - no factoring information
    # What about the Hecke operators?
    # T_m on L^2(Z/NZ): (T_m f)(x) = sum_{y: my=x mod N} f(y)
    # = f(x/m mod N) if gcd(m,N)=1

    if N > 500:
        return None

    # Build Hecke operator T_2
    T = np.zeros((N, N))
    for x in range(N):
        # T_2: map x to x/2 mod N if 2|x, or (x+N)/2 mod N
        if x % 2 == 0:
            T[x // 2, x] = 1
        if (x + N) % 2 == 0:
            T[(x + N) // 2 % N, x] = 1

    eigs = np.sort(np.abs(np.linalg.eigvals(T)))[::-1]
    return eigs[:num_eigenvalues]

def experiment():
    print("=== Field 13: Noncommutative Geometry - Connes' Program ===\n")

    test_cases = [(3, 5), (7, 11), (13, 17), (23, 29), (37, 41),
                  (101, 103), (251, 257)]

    print("  Test 1: Bost-Connes partition function")
    beta_vals = [0.5, 1.0, 1.5, 2.0, 3.0]
    for p, q in test_cases[:4]:
        N = p * q
        Z = bost_connes_partition(N, beta_vals)
        print(f"  N={N} = {p}*{q}:")
        for beta in beta_vals:
            # Compare with factored form
            z_factored = (1 + p**(-beta)) * (1 + q**(-beta))
            print(f"    Z({beta:.1f}) = {Z[beta]:.6f}, factored = {z_factored:.6f}, match={abs(Z[beta]-z_factored)<1e-10}")

        # Key test: can we RECOVER p,q from Z(beta) at a few beta values?
        # Z(beta) = 1 + p^{-beta} + q^{-beta} + N^{-beta}
        # At beta=1: Z(1) = 1 + 1/p + 1/q + 1/N = (p+q+1+pq/pq) = ...
        # sigma = 1/p + 1/q = Z(1) - 1 - 1/N
        sigma = Z[1.0] - 1 - 1.0/N  # = 1/p + 1/q
        # Also: 1/p * 1/q = 1/N
        # So 1/p and 1/q are roots of t^2 - sigma*t + 1/N = 0
        disc = sigma**2 - 4.0/N
        if disc >= 0:
            root1 = (sigma + math.sqrt(disc)) / 2
            root2 = (sigma - math.sqrt(disc)) / 2
            recovered_p = round(1.0 / root1) if root1 > 0 else 0
            recovered_q = round(1.0 / root2) if root2 > 0 else 0
            print(f"    Recovered factors from Z(1): {recovered_p}, {recovered_q}")
            print(f"    Correct: {recovered_p in (p,q) and recovered_q in (p,q)}")

    print("\n  Test 2: Hecke operator spectrum")
    for p, q in test_cases[:3]:
        N = p * q
        eigs = spectral_approach(N)
        if eigs is not None:
            print(f"  N={N}: Hecke T_2 top eigenvalues: {[f'{e:.2f}' for e in eigs[:8]]}")

    print("\n  CRITICAL OBSERVATION:")
    print("  Computing Z_N(beta) = sum_{d|N} d^{-beta} REQUIRES finding all divisors of N.")
    print("  Finding all divisors IS the factoring problem!")
    print("  The Bost-Connes partition function CAN recover factors (via Vieta's formulas)")
    print("  but only after you've already computed it, which requires factoring first.")
    print("  Connes' program relates primes to zeta zeros, but doesn't give an ALGORITHM.")

    print("\nVERDICT: NCG beautifully relates primes to spectral theory.")
    print("The BC partition function Z(beta) can recover factors from its values,")
    print("but COMPUTING Z(beta) requires knowing all divisors = factoring.")
    print("Connes' framework is descriptive, not algorithmic. No speedup.")
    print("RESULT: REFUTED")

experiment()

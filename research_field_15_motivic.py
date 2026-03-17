"""Field 15: Motivic Cohomology - Motives of Varieties Defined by N
Hypothesis: The affine variety V: xy = N over Z has a motive h(V) in the category of
mixed motives. The motivic decomposition h(V) = h(Spec Z/pZ) + h(Spec Z/qZ) + ...
might be detectable via motivic cohomology groups (Chow groups, K-theory).
Specifically, the Hasse-Weil zeta function of V encodes factor information.
"""
import time, math, random
import numpy as np

def hasse_weil_local(N, r, max_power=4):
    """Compute #V(F_{r^k}) for the variety xy=N over F_r.
    V: xy = N mod r. Number of solutions = number of pairs (x,y) in F_r with xy = N mod r.
    """
    counts = []
    n_mod_r = N % r
    for k in range(1, max_power + 1):
        q = r**k
        # Count solutions to xy = N mod q in (Z/qZ)^2
        count = 0
        for x in range(q):
            if x == 0:
                if n_mod_r == 0:
                    count += q  # y can be anything
                continue
            # y = N/x mod q
            g = math.gcd(x, q)
            if (N % q) % g == 0:
                # Number of solutions = g
                count += g
            # Actually for xy = c mod q: if gcd(x,q)=1, unique y. Otherwise more complex.
        counts.append(count)
    return counts

def zeta_function_test(N, primes_to_test):
    """The Hasse-Weil zeta function of V: xy=N is
    Z(V, s) = prod_p Z_p(V, p^{-s})
    where Z_p(V, t) = exp(sum_{k>=1} #V(F_{p^k}) * t^k / k)

    For V: xy=N, the local zeta at prime r dividing N is different from
    r not dividing N. This difference IS the factoring information.
    """
    results = {}
    for r in primes_to_test:
        n_mod_r = N % r
        if n_mod_r == 0:
            # r divides N -- special fiber
            # V mod r: xy = 0, i.e., x=0 or y=0
            # #V(F_r) = 2r - 1 (union of two lines minus origin)
            count = 2 * r - 1
            fiber_type = "DEGENERATE (r | N)"
        else:
            # V mod r: xy = c for c != 0
            # #V(F_r) = r - 1 (each nonzero x gives unique y = c/x)
            count = r - 1
            fiber_type = "smooth"

        results[r] = (count, fiber_type)

    return results

def chow_group_test(N):
    """The Chow group CH^1(V) of V: xy=N classifies divisors up to rational equivalence.
    For smooth V, CH^1 is related to Pic(V).
    The structure of Pic(V) over Z depends on the singular fibers,
    which occur at primes dividing N.
    """
    # The singular fibers of xy=N -> Spec Z are at primes p|N.
    # At such primes, the fiber xy=0 has a node.
    # The component group of the Neron model at p is Z/2Z.
    # This gives: for N=pq, there are exactly 2 bad fibers (at p and q).
    # The Tamagawa number c = prod_bad c_v = 2 * 2 = 4 (each node contributes 2).

    # But to FIND which primes give bad fibers... we need to factor N.
    return "Chow group structure requires knowing singular fibers = knowing factors"

def experiment():
    print("=== Field 15: Motivic Cohomology ===\n")

    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43]

    test_cases = [(7, 11), (13, 17), (23, 29), (37, 41), (101, 103)]

    print("  Test 1: Local point counts (Hasse-Weil)")
    for p, q in test_cases[:3]:
        N = p * q
        results = zeta_function_test(N, small_primes)
        print(f"  N={N} = {p}*{q}:")
        for r in small_primes:
            count, ftype = results[r]
            marker = " <-- FACTOR" if r in (p, q) else ""
            print(f"    r={r:3d}: #V(F_r) = {count:4d}, {ftype}{marker}")

    print("\n  Test 2: Detecting degenerate fibers")
    for p, q in test_cases:
        N = p * q
        results = zeta_function_test(N, small_primes)
        degenerate = [r for r in small_primes if results[r][1] == "DEGENERATE (r | N)"]
        smooth = [r for r in small_primes if results[r][1] == "smooth"]
        print(f"  N={N}: degenerate fibers at {degenerate} (these are the factors in our test range)")

    print("\n  Critical analysis:")
    print("  The Hasse-Weil zeta function Z(V, s) has 'bad' local factors at primes r | N.")
    print("  Detecting bad fibers (#V(F_r) = 2r-1 vs r-1) is equivalent to testing r | N.")
    print("  This is EXACTLY trial division: check if N mod r = 0 for each small r.")
    print("  The motivic/cohomological language adds no new information.")
    print("  ")
    print("  For RSA semiprimes where p,q are large:")
    print("  ALL small-prime fibers are smooth (since p,q are not small primes).")
    print("  The bad fibers are at p and q, which we can't test directly.")
    print("  Motivic cohomology tells us WHERE to look (degenerate fibers)")
    print("  but finding them requires trying all primes up to sqrt(N).")

    print("\nVERDICT: Motivic cohomology and Hasse-Weil zeta functions correctly")
    print("identify factors as 'bad fibers' of the variety xy=N. But detecting")
    print("bad fibers = testing divisibility = trial division. Beautiful theory,")
    print("same algorithm. No computational advantage.")
    print("RESULT: REFUTED")

experiment()

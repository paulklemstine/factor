"""Field 14: Algebraic K-Theory - K-groups of Number Rings
Hypothesis: The K-theory groups K_0, K_1, K_2 of Z[1/N] encode arithmetic information
about N. K_0(Z[1/N]) classifies projective modules (related to ideal class group),
K_1 relates to units, K_2 to Brauer groups. The structure of these groups might
differ detectably for N=pq vs N prime, potentially revealing factors.
"""
import time, math, random

def k0_analysis(N):
    """K_0(Z/NZ) ≅ Z (rank of free modules).
    K_0(Z[1/N]) ≅ Z ⊕ Z/d_1 ⊕ ... where d_i relate to class numbers.
    For Z/NZ = Z/pZ × Z/qZ when N=pq:
      K_0(Z/NZ) ≅ K_0(Z/pZ) × K_0(Z/qZ) ≅ Z × Z
    The RANK of K_0 counts the number of prime factors!
    But computing the rank requires knowing the factorization...
    """
    # For Z/NZ as a ring: count idempotents (= number of connected components of Spec)
    # Number of minimal idempotents = number of prime factors of N
    # This is 2^k where k = number of distinct prime factors

    # We can detect this by counting solutions to e^2 = e mod N
    idem_count = 0
    if N < 50000:
        for e in range(N):
            if (e * e) % N == e:
                idem_count += 1
    else:
        # For large N, sample
        idem_count = -1  # Can't compute

    return idem_count

def k1_unit_structure(N):
    """K_1(Z/NZ) ≅ (Z/NZ)* = group of units.
    |(Z/NZ)*| = phi(N) = (p-1)(q-1) for N=pq.
    Structure: (Z/NZ)* ≅ (Z/pZ)* × (Z/qZ)* ≅ Z/(p-1) × Z/(q-1)

    The STRUCTURE of (Z/NZ)* reveals p-1 and q-1, hence p and q.
    But determining the group structure requires computing orders,
    which requires knowing phi(N), which requires factoring.
    """
    # Compute phi(N) if we know factors (for verification)
    # Without factors: we can compute the ORDER of the unit group
    # by finding the order of random elements

    # Strategy: find ord(a) for random a in (Z/NZ)*
    # ord(a) | phi(N) = (p-1)(q-1)
    # If we find several orders, lcm of orders might = phi(N) or a multiple

    orders = []
    for a in range(2, min(50, N)):
        if math.gcd(a, N) > 1:
            continue
        # Compute order of a
        x = a
        for k in range(1, N):
            if x == 1:
                orders.append(k)
                break
            x = (x * a) % N

    if orders:
        # lcm of observed orders
        from functools import reduce
        lcm_orders = reduce(lambda a, b: a * b // math.gcd(a, b), orders)
    else:
        lcm_orders = 0

    return orders, lcm_orders

def k2_tame_symbol(N, p, q):
    """K_2 of a finite field is trivial, but K_2(Z) = Z/2.
    The tame symbol K_2(Q) -> ⊕_p F_p* relates to Hilbert reciprocity.
    For factoring: the tame symbol at p maps K_2(Q) -> F_p*.
    The kernel of the tame symbol at p detects divisibility by p.

    Test: can we detect which primes have non-trivial tame symbol image?
    """
    # The tame symbol of {a, b} at prime r is:
    # (-1)^{v_r(a)*v_r(b)} * (a^{v_r(b)} / b^{v_r(a)}) mod r
    # For a,b coprime to N: tame symbol at p dividing N depends on
    # the residues of a,b mod p.

    # This reduces to knowing which primes divide N...
    # Not a useful shortcut.
    return "K_2 tame symbol requires knowing prime factorization"

def experiment():
    print("=== Field 14: Algebraic K-Theory ===\n")

    test_cases = [(3, 5), (7, 11), (13, 17), (23, 29), (37, 41),
                  (101, 103), (251, 257)]

    print("  Test 1: K_0 idempotent counting")
    for p, q in test_cases:
        N = p * q
        idem = k0_analysis(N)
        # For N=pq with p,q prime: expect 4 idempotents (0, 1, e_p, e_q)
        expected = 4  # 2^(number of prime factors)
        print(f"    N={N} = {p}*{q}: idempotents = {idem}, expected = {expected}")

    # Compare with prime
    for p_test in [7, 13, 23, 37]:
        idem = k0_analysis(p_test)
        print(f"    N={p_test} (prime): idempotents = {idem}, expected = 2")

    print("\n  Test 2: K_1 unit group structure")
    for p, q in test_cases[:4]:
        N = p * q
        orders, lcm_ord = k1_unit_structure(N)
        phi_N = (p-1) * (q-1)
        print(f"    N={N} = {p}*{q}: phi(N)={phi_N}")
        print(f"      Orders observed: {orders[:10]}...")
        print(f"      LCM of orders: {lcm_ord}")
        print(f"      LCM = phi(N)? {lcm_ord == phi_N}")

        # If lcm_orders = phi(N) = (p-1)(q-1) and we know N=pq,
        # then p + q = N + 1 - phi(N), so we can solve:
        # p + q = N + 1 - lcm_orders, p * q = N
        if lcm_ord > 0:
            s = N + 1 - lcm_ord  # = p + q
            disc = s * s - 4 * N
            if disc >= 0:
                sq_disc = math.isqrt(disc)
                if sq_disc * sq_disc == disc:
                    recovered_p = (s + sq_disc) // 2
                    recovered_q = (s - sq_disc) // 2
                    print(f"      Recovered: p={recovered_p}, q={recovered_q}, correct={set([recovered_p,recovered_q])==set([p,q])}")
                else:
                    print(f"      LCM != phi(N), recovery failed (lcm divides phi but != phi)")

    print("\n  Key insight: K_1 approach WORKS in theory!")
    print("  If we can compute phi(N) = |K_1(Z/NZ)|, we can factor N.")
    print("  But computing |K_1| = phi(N) = |(Z/NZ)*| requires factoring N!")
    print("  Computing orders of random elements gives divisors of phi(N),")
    print("  not phi(N) itself. The lcm of random orders converges to lambda(N),")
    print("  not phi(N). This is related to Shor's algorithm (period finding).")

    print("\nVERDICT: K-theory correctly identifies that K_0 (idempotents) and")
    print("K_1 (unit group) encode factoring information. But computing these")
    print("K-groups REQUIRES the factorization. K-theory provides the right")
    print("FRAMEWORK but no algorithmic shortcut.")
    print("RESULT: REFUTED")

experiment()

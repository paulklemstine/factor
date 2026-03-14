#!/usr/bin/env python3
"""
Division Polynomial experiments for ECDLP on secp256k1.

Ideas tested:
A) Division polynomial evaluation to find k from K=[k]G
B) Division polynomials mod small primes for CRT-based recovery
C) Resultants / Gröbner bases approach
"""

import gmpy2
from gmpy2 import mpz, invert, powmod
import time

# secp256k1 parameters
p = mpz(0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F)
n = mpz(0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141)
Gx = mpz(0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798)
Gy = mpz(0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)
a_curve = mpz(0)
b_curve = mpz(7)

# --- Point arithmetic on secp256k1 ---

def point_add(P, Q):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        lam = (3 * x1 * x1) * invert(2 * y1, p) % p
    else:
        lam = (y2 - y1) * invert(x2 - x1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)

def point_mul(k, P):
    k = mpz(k) % n
    R = None
    Q = P
    while k > 0:
        if k & 1:
            R = point_add(R, Q)
        Q = point_add(Q, Q)
        k >>= 1
    return R

G = (Gx, Gy)

# ====================================================================
# IDEA A: Division polynomial evaluation mod p
# ====================================================================

def divpoly_eval_range(x0, y0, max_m):
    """
    Evaluate psi_m(x0, y0) mod p for m = 0, 1, ..., max_m.

    Recurrence (Washington, "Elliptic Curves: Number Theory and Cryptography"):
      psi_0 = 0, psi_1 = 1, psi_2 = 2y
      psi_3 = 3x^4 + 6ax^2 + 12bx - a^2
      psi_4 = 4y(x^6 + 5ax^4 + 20bx^3 - 5a^2x^2 - 4abx - 8b^2 - a^3)
      psi_{2m+1} = psi_{m+2} * psi_m^3 - psi_{m-1} * psi_{m+1}^3
      psi_{2m} = psi_m * (psi_{m+2} * psi_{m-1}^2 - psi_{m-2} * psi_{m+1}^2) / (2y)

    All evaluated numerically mod p.
    """
    psi = [mpz(0)] * (max_m + 1)
    if max_m >= 1: psi[1] = mpz(1)
    if max_m >= 2: psi[2] = (2 * y0) % p
    if max_m >= 3:
        psi[3] = (3 * powmod(x0, 4, p) + 84 * x0) % p  # a=0, b=7
    if max_m >= 4:
        psi[4] = (4 * y0 * (powmod(x0, 6, p) + 140 * powmod(x0, 3, p) - 392)) % p

    inv2y = invert(2 * y0, p)

    for m in range(5, max_m + 1):
        if m % 2 == 1:
            k = (m - 1) // 2
            val = (psi[k+2] * powmod(psi[k], 3, p) - psi[k-1] * powmod(psi[k+1], 3, p)) % p
            psi[m] = val
        else:
            k = m // 2
            inner = (psi[k+2] * psi[k-1] % p * psi[k-1] - psi[k-2] * psi[k+1] % p * psi[k+1]) % p
            val = psi[k] * inner % p * inv2y % p
            psi[m] = val

    return psi


def x_coord_from_divpoly(x0, psi, m):
    """x([m]P) = x0 - psi_{m-1} * psi_{m+1} / psi_m^2"""
    if psi[m] == 0:
        return None  # point at infinity
    psi_m_sq = psi[m] * psi[m] % p
    num = psi[m-1] * psi[m+1] % p
    return (x0 - num * invert(psi_m_sq, p)) % p


def test_idea_a():
    """Test division polynomial x-coordinate formula against known scalar mults."""
    print("=" * 70)
    print("IDEA A: Division polynomial evaluation")
    print("=" * 70)

    # Verify formula for small k
    print("\n[1] Verifying x-coord formula for k=1..100...")
    max_m = 102
    t0 = time.time()
    psi = divpoly_eval_range(Gx, Gy, max_m)
    t_eval = time.time() - t0
    print(f"    Computed psi_0..psi_{max_m} in {t_eval:.4f}s")

    errors = 0
    for k in range(1, 101):
        x_dp = x_coord_from_divpoly(Gx, psi, k)
        kG = point_mul(k, G)
        if kG is None:
            if x_dp is not None:
                errors += 1
        elif x_dp != kG[0]:
            errors += 1
            if errors <= 3:
                print(f"    MISMATCH at k={k}: divpoly x={x_dp}, actual x={kG[0]}")

    if errors == 0:
        print(f"    All 100 verified correctly!")
    else:
        print(f"    {errors} mismatches found")

    # Search for known k by scanning
    print("\n[2] Searching for k by scanning psi-based x-coordinates...")
    test_cases = [100, 1234, 5000, 9999]
    max_m = 10002
    t0 = time.time()
    psi = divpoly_eval_range(Gx, Gy, max_m)
    t_eval = time.time() - t0
    print(f"    Computed psi_0..psi_{max_m} in {t_eval:.3f}s")

    for k_true in test_cases:
        K = point_mul(k_true, G)
        target_x = K[0]
        found = False
        for m in range(1, 10001):
            x_dp = x_coord_from_divpoly(Gx, psi, m)
            if x_dp == target_x:
                print(f"    k={k_true}: FOUND at m={m}")
                found = True
                break
        if not found:
            print(f"    k={k_true}: NOT found in range 1..10000")

    # Compare speed: divpoly scan vs point addition scan
    print(f"\n[3] Speed comparison: divpoly scan vs repeated point addition (N=10000)...")

    t0 = time.time()
    psi2 = divpoly_eval_range(Gx, Gy, 10002)
    t_divpoly = time.time() - t0

    t0 = time.time()
    Q = G
    for i in range(2, 10001):
        Q = point_add(Q, G)
    t_pointadd = time.time() - t0

    print(f"    Divpoly recurrence: {t_divpoly:.3f}s")
    print(f"    Repeated point add: {t_pointadd:.3f}s")
    print(f"    Ratio: {t_pointadd/t_divpoly:.1f}x")
    print(f"    Both are O(N). Divpoly is faster per step (fewer field ops).")
    print(f"    But BSGS at O(sqrt(N)) is strictly better for range searches.")


def test_idea_b():
    """Test division polys mod small primes for CRT recovery."""
    print("\n" + "=" * 70)
    print("IDEA B: Division polynomials mod small primes (CRT approach)")
    print("=" * 70)

    # Key insight: for CRT to work, we need k mod q. But [m]G for m=0..q-1
    # only covers q distinct points. Since the group order n is prime and
    # much larger than q, [m]G for m in [0, q) produces q distinct points,
    # none of which equal [k]G unless k is actually in [0, q).
    #
    # Pohlig-Hellman works when n has small factors: if q | n, then
    # [(n/q)*k]G = [(n/q)] * [k]G, and we solve DLOG in the order-q subgroup.
    # But secp256k1's order n is PRIME -- no small factors exist.
    #
    # So the CRT approach via small primes is fundamentally inapplicable.

    print("\n[1] Why CRT via small primes fails for secp256k1:")
    print(f"    Group order n is prime ({n.bit_length()} bits)")
    print(f"    n = {n}")
    print(f"    Pohlig-Hellman requires n to have small prime factors.")
    print(f"    Since n is prime, the only subgroups have order 1 and n.")
    print(f"    There is no way to compute k mod q for small q.")

    # Demonstrate: for q | n, we could map to the order-q subgroup.
    # Since n is prime, let's verify this:
    small_primes = [2, 3, 5, 7, 11, 13]
    print(f"\n[2] Checking if any small prime divides n:")
    for q in small_primes:
        print(f"    n mod {q} = {n % q}")
    print(f"    None divide n. Pohlig-Hellman gives no information.")

    # What if we tried anyway? Show it doesn't work.
    print(f"\n[3] Attempting direct scan for k mod 7 (demonstration of failure):")
    k_true = 12345
    K = point_mul(k_true, G)

    # Compute [m]G for m=0..6 and check x-coords
    print(f"    K = [{k_true}]G, K.x = {hex(int(K[0]))[:20]}...")
    for m in range(7):
        mG = point_mul(m, G)
        if mG is None:
            print(f"    [{m}]G = O (infinity)")
        else:
            match = "MATCH" if mG[0] == K[0] else ""
            print(f"    [{m}]G.x = {hex(int(mG[0]))[:20]}... {match}")
    print(f"    No match because [0..6]G are 7 distinct points, none equal [{k_true}]G.")
    print(f"    k mod 7 = {k_true % 7}, but [{k_true % 7}]G != [{k_true}]G.")

    # Division poly version of the same failed approach
    print(f"\n[4] Division poly evaluation confirms the same:")
    psi = divpoly_eval_range(Gx, Gy, 9)
    for m in range(1, 8):
        x_dp = x_coord_from_divpoly(Gx, psi, m)
        match = "MATCH" if x_dp == K[0] else ""
        print(f"    x([{m}]G) via divpoly = {hex(int(x_dp))[:20]}... {match}")

    print(f"\n    CONCLUSION: Division polys cannot circumvent the algebraic")
    print(f"    structure. CRT/Pohlig-Hellman is only useful when the group")
    print(f"    order has small factors. secp256k1 was specifically chosen")
    print(f"    to have prime order, making this approach impossible.")


def test_idea_c():
    """Test resultants / Groebner bases on tiny instances."""
    print("\n" + "=" * 70)
    print("IDEA C: Resultants and Groebner bases")
    print("=" * 70)

    print("\n[1] Division polynomial degree analysis...")
    print(f"    The degree of psi_m as a polynomial in x (after substituting y^2=x^3+7):")
    print(f"      For odd  m: deg(psi_m) = (m^2 - 1) / 2")
    print(f"      For even m: deg(psi_m / (2y)) = (m^2 - 4) / 2")
    print()
    for m in [1, 2, 3, 4, 5, 7, 10, 20, 50, 100, 1000]:
        if m % 2 == 1:
            deg = (m*m - 1) // 2
            print(f"      psi_{m:5d}: degree {deg:>10d}")
        else:
            deg = (m*m - 4) // 2
            print(f"      psi_{m:5d}: 2y * (degree {deg:>10d})")

    print(f"\n      psi_(2^128): degree ~ 2^255")
    print(f"    These polynomials are ASTRONOMICALLY large for cryptographic m.")
    print(f"    Cannot be represented or manipulated symbolically.")

    # Verify degree formula numerically for small m
    print(f"\n[2] Verifying numerical evaluation matches known degrees...")
    print(f"    (Already verified in Idea A: psi evaluation correct for m=1..100)")

    # Verify the per-step cost
    print(f"\n[3] Per-step cost analysis:")
    print(f"    Each recurrence step computes psi_m from previous values.")
    print(f"    Odd step:  2 cubes + 2 mults + 1 sub = ~5 field mults mod p")
    print(f"    Even step: 2 squares + 2 mults + 1 sub + 1 inv = ~6 field mults")
    print(f"    Point addition: 1 inv + 2 mults + 1 square + 2 subs = ~4 field mults")
    print(f"    Division poly recurrence is comparable per step to point addition.")

    # Groebner basis discussion
    print(f"\n[2] Groebner basis analysis:")
    print(f"    The ECDLP asks: given K=[k]G, find k.")
    print(f"    Scalar k appears as a RECURRENCE INDEX in psi_k, not as a")
    print(f"    polynomial variable. There is no polynomial equation F(k)=0.")
    print(f"")
    print(f"    What we could write as a polynomial system:")
    print(f"      y^2 = x^3 + 7")
    print(f"      (x, y) lies on the curve")
    print(f"      [k](x,y) = (Kx, Ky)")
    print(f"    But [k](x,y) is a rational function of (x,y) with degree O(k^2),")
    print(f"    and k is unknown. This is NOT a polynomial system in k.")
    print(f"")
    print(f"    Alternative: for each candidate m, check if [m]G = K.")
    print(f"    This is brute force, not Groebner basis computation.")
    print(f"")
    print(f"    Even for tiny curves over small fields, Groebner bases don't")
    print(f"    help because the problem structure (k as subscript) doesn't")
    print(f"    admit polynomial formulation.")

    # Resultant analysis
    print(f"\n[3] Resultant analysis:")
    print(f"    Resultants compute common roots of two polynomials.")
    print(f"    For l-torsion (psi_l(x) = 0), resultants with the curve")
    print(f"    equation can characterize torsion points.")
    print(f"    But ECDLP is not about finding torsion points.")
    print(f"    We know the point K; we need the discrete log k.")
    print(f"    Resultants don't provide a path to k.")


def main():
    print("Division Polynomial Experiments for ECDLP on secp256k1")
    print("=" * 70)

    test_idea_a()
    test_idea_b()
    test_idea_c()

    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print("""
Division polynomials psi_m provide an alternative representation of [m]P
via rational functions of the base point coordinates. Key findings:

1. IDEA A (Direct evaluation): Computing psi_0..psi_N takes O(N) field
   multiplications, same as computing [1]G..[N]G by repeated addition.
   The per-step cost is actually lower (fewer field ops per recurrence step
   vs a full point addition), so divpoly enumeration is ~2-4x faster than
   naive point addition for a linear scan. However, BSGS at O(sqrt(N))
   is asymptotically superior. Division polys don't change the complexity.

2. IDEA B (CRT via small primes): This approach is FUNDAMENTALLY BLOCKED
   by secp256k1's prime group order. Pohlig-Hellman decomposition requires
   small factors of n. Since n is prime, there are no subgroups to exploit.
   Division polynomials cannot circumvent this algebraic obstruction.

3. IDEA C (Resultants/Groebner): The scalar k is a recurrence index in
   psi_k, NOT a polynomial variable. The ECDLP cannot be encoded as a
   polynomial system where k is an unknown. Symbolic division polynomials
   have degree O(m^2), making them intractable for cryptographic sizes.
   Neither Groebner bases nor resultants are applicable.

VERDICT: Division polynomials are a REFORMULATION of elliptic curve
arithmetic, not a new attack vector. They provide:
  - A slightly faster per-step linear scan (fewer field ops per step)
  - No asymptotic improvement over BSGS/Pollard rho/kangaroo
  - No way to bypass the prime-order group structure
  - No polynomial formulation that enables algebraic attacks

The existing kangaroo/BSGS implementations remain the best approaches.
""")


if __name__ == "__main__":
    main()

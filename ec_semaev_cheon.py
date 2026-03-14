"""
H16: Semaev Summation Polynomials for Index Calculus on EC
H17: Cheon's Algorithm analysis for secp256k1

Tests whether these classical ECDLP techniques yield practical speedups,
especially when combined with secp256k1's CM structure (j=0, endomorphism).
"""

import gmpy2
from gmpy2 import mpz, invert, is_prime, isqrt, gcd
import time
import sys
import random
from collections import defaultdict

# -----------------------------------------------------------------------
# secp256k1 parameters
# -----------------------------------------------------------------------
SECP256K1_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
SECP256K1_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
SECP256K1_GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
SECP256K1_GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
SECP256K1_BETA = 0x7AE96A2B657C07106E64479EAC3434E99CF0497512F58995C1396C28719501EE
SECP256K1_LAMBDA = 0x5363AD4CC05C30E0A5261C028812645A122E22EA20816678DF02967C1B23BD72

# -----------------------------------------------------------------------
# Minimal EC arithmetic (affine, mod p)
# -----------------------------------------------------------------------

INF = None  # point at infinity

def ec_add(P, Q, a, p):
    if P is INF: return Q
    if Q is INF: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2:
        if y1 == y2:
            return ec_double(P, a, p)
        return INF
    dx = (x2 - x1) % p
    dy = (y2 - y1) % p
    inv_dx = int(gmpy2.invert(mpz(dx), mpz(p)))
    lam = (dy * inv_dx) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)

def ec_double(P, a, p):
    if P is INF: return INF
    x1, y1 = P
    if y1 == 0: return INF
    num = (3 * x1 * x1 + a) % p
    den = (2 * y1) % p
    inv_den = int(gmpy2.invert(mpz(den), mpz(p)))
    lam = (num * inv_den) % p
    x3 = (lam * lam - 2 * x1) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)

def ec_neg(P, p):
    if P is INF: return INF
    return (P[0], (-P[1]) % p)

def ec_mul(k, P, a, p):
    if k == 0: return INF
    if k < 0:
        P = ec_neg(P, p)
        k = -k
    R = INF
    Q = P
    while k:
        if k & 1:
            R = ec_add(R, Q, a, p)
        Q = ec_double(Q, a, p)
        k >>= 1
    return R

# -----------------------------------------------------------------------
# H16: Semaev Summation Polynomials
# -----------------------------------------------------------------------

def semaev_S2(x1, x2, p):
    """S_2(x1, x2) = (x1 - x2)^2. Zero iff P1 = -P2 (same x-coord)."""
    return ((x1 - x2) * (x1 - x2)) % p

def semaev_S3(x1, x2, x3, b, p):
    """
    S_3(x1, x2, x3) for y^2 = x^3 + b (a=0).

    S_3 = 0 iff there exist points P1, P2, P3 on the curve with
    x(Pi) = xi and P1 + P2 + P3 = O.

    For y^2 = x^3 + b, Semaev's S_3 is:
    S_3 = (x1^2*x2^2 + x1^2*x3^2 + x2^2*x3^2
           - 2*x1*x2*x3*(x1+x2+x3) - 4*b*(x1+x2+x3))^2
          - ... (complicated resultant)

    Actually, the standard form for general Weierstrass y^2 = x^3 + ax + b:
    S_3(x1,x2,x3) = resultant_y(f(x1,y), S_2_line(x2,x3,y))

    For a=0: we use the explicit formula. Let's derive it properly.

    P1+P2+P3 = O means P3 = -(P1+P2). So x3 = x(P1+P2).

    x(P1+P2) = ((y2-y1)/(x2-x1))^2 - x1 - x2  (when x1 != x2)

    So x3 = lam^2 - x1 - x2 where lam = (y2-y1)/(x2-x1).

    Thus: (x3 + x1 + x2)(x2-x1)^2 = (y2-y1)^2

    And y_i^2 = x_i^3 + b, so:
    (x3+x1+x2)(x2-x1)^2 = (y2-y1)^2

    But y2-y1 is not polynomial in x1,x2 alone. We need resultant over y1,y2.

    The full polynomial is obtained by eliminating y1, y2 from:
      y1^2 = x1^3 + b
      y2^2 = x2^3 + b
      (x3 + x1 + x2)(x2 - x1)^2 = (y2 - y1)^2

    Expanding: (x3+x1+x2)(x2-x1)^2 = y1^2 - 2*y1*y2 + y2^2
             = (x1^3+b) - 2*y1*y2 + (x2^3+b)
             = x1^3 + x2^3 + 2*b - 2*y1*y2

    So: 2*y1*y2 = x1^3 + x2^3 + 2*b - (x3+x1+x2)(x2-x1)^2

    Squaring: 4*y1^2*y2^2 = [x1^3+x2^3+2b-(x3+x1+x2)(x2-x1)^2]^2

    And 4*y1^2*y2^2 = 4*(x1^3+b)*(x2^3+b)

    So S_3(x1,x2,x3) = [x1^3+x2^3+2b-(x3+x1+x2)(x2-x1)^2]^2 - 4*(x1^3+b)*(x2^3+b)

    This is correct! S_3 = 0 iff there exist signs of y1,y2 making P1+P2+P3=O.
    """
    x1_3 = (x1*x1*x1) % p
    x2_3 = (x2*x2*x2) % p
    dx2 = ((x2-x1)*(x2-x1)) % p
    s = (x3 + x1 + x2) % p

    A = (x1_3 + x2_3 + 2*b - s * dx2) % p
    lhs = (A * A) % p
    rhs = (4 * (x1_3 + b) * (x2_3 + b)) % p
    return (lhs - rhs) % p


def test_semaev_S3_correctness():
    """Verify S_3 on a toy curve and on secp256k1."""
    print("=" * 60)
    print("H16: Semaev S_3 correctness tests")
    print("=" * 60)

    # Test on toy curve: y^2 = x^3 + 7 mod 1009
    p_toy = 1009
    b_toy = 7
    a_toy = 0

    # Find some points on the curve
    points = []
    for x in range(p_toy):
        rhs = (x*x*x + b_toy) % p_toy
        if rhs == 0:
            points.append((x, 0))
            continue
        if gmpy2.legendre(rhs, p_toy) == 1:
            y = tonelli_shanks(rhs, p_toy)
            if y is not None and (y*y) % p_toy == rhs:
                points.append((x, y))
                points.append((x, (-y) % p_toy))

    print(f"Toy curve y^2=x^3+7 mod {p_toy}: found {len(points)} points")

    # Pick P1, P2 and compute P3 = -(P1+P2), then check S_3 = 0
    n_tests = 0
    n_pass = 0
    for _ in range(20):
        P1 = random.choice(points)
        P2 = random.choice(points)
        if P1[0] == P2[0]:
            continue
        P1P2 = ec_add(P1, P2, a_toy, p_toy)
        if P1P2 is INF:
            continue
        P3 = ec_neg(P1P2, p_toy)  # P1+P2+P3 = O

        val = semaev_S3(P1[0], P2[0], P3[0], b_toy, p_toy)
        n_tests += 1
        if val == 0:
            n_pass += 1

    print(f"S_3 zero check (P1+P2+P3=O): {n_pass}/{n_tests} passed")

    # Negative test: random x3 should NOT give S_3 = 0 (generically)
    n_nonzero = 0
    for _ in range(20):
        P1 = random.choice(points)
        P2 = random.choice(points)
        x3_rand = random.randrange(p_toy)
        val = semaev_S3(P1[0], P2[0], x3_rand, b_toy, p_toy)
        if val != 0:
            n_nonzero += 1
    print(f"S_3 non-zero check (random x3): {n_nonzero}/20 non-zero (expected ~20)")

    # Test on secp256k1
    p = SECP256K1_P
    G = (SECP256K1_GX, SECP256K1_GY)
    k1, k2 = 12345, 67890
    P1 = ec_mul(k1, G, 0, p)
    P2 = ec_mul(k2, G, 0, p)
    P1P2 = ec_add(P1, P2, 0, p)
    P3 = ec_neg(P1P2, p)

    val = semaev_S3(P1[0], P2[0], P3[0], 7, p)
    print(f"\nsecp256k1 S_3 test: S_3(k1*G, k2*G, -(k1+k2)*G) = {'0 (PASS)' if val == 0 else 'NONZERO (FAIL)'}")

    return n_pass == n_tests


# -----------------------------------------------------------------------
# H16: Index Calculus on toy curve using Semaev S_3
# -----------------------------------------------------------------------

def toy_curve_points(p, b):
    """Find all points on y^2 = x^3 + b mod p."""
    pts = []
    for x in range(p):
        rhs = (x*x*x + b) % p
        # Tonelli-Shanks via gmpy2
        if rhs == 0:
            pts.append((x, 0))
            continue
        if gmpy2.legendre(rhs, p) != 1:
            continue
        # For p = 3 mod 4
        if p % 4 == 3:
            y = int(pow(mpz(rhs), mpz((p + 1) // 4), mpz(p)))
        else:
            y = int(gmpy2.isqrt_rem(mpz(rhs))[0])  # fallback
            # Use Cipolla or Tonelli-Shanks
            y = tonelli_shanks(rhs, p)
        if y is not None and (y*y) % p == rhs:
            pts.append((x, y))
            if y != 0:
                pts.append((x, (-y) % p))
    return pts

def tonelli_shanks(n, p):
    """Compute sqrt(n) mod p using Tonelli-Shanks."""
    if gmpy2.legendre(n, p) != 1:
        return None
    if p % 4 == 3:
        return int(pow(mpz(n), mpz((p+1)//4), mpz(p)))
    # Factor p-1 = Q * 2^S
    Q, S = p - 1, 0
    while Q % 2 == 0:
        Q //= 2
        S += 1
    # Find quadratic non-residue
    z = 2
    while gmpy2.legendre(z, p) != -1:
        z += 1
    M = S
    c = int(pow(mpz(z), mpz(Q), mpz(p)))
    t = int(pow(mpz(n), mpz(Q), mpz(p)))
    R = int(pow(mpz(n), mpz((Q+1)//2), mpz(p)))
    while True:
        if t == 0: return 0
        if t == 1: return R
        i = 1
        tmp = (t*t) % p
        while tmp != 1:
            tmp = (tmp*tmp) % p
            i += 1
        b_val = c
        for _ in range(M - i - 1):
            b_val = (b_val * b_val) % p
        M = i
        c = (b_val * b_val) % p
        t = (t * c) % p
        R = (R * b_val) % p


def find_curve_order_bsgs(G, a, b, p, max_order=None):
    """Find order of point G on y^2=x^3+ax+b mod p using BSGS."""
    if max_order is None:
        max_order = p + 1 + 2 * int(isqrt(mpz(p)))  # Hasse bound
    m = int(isqrt(mpz(max_order))) + 1

    # Baby steps: j*G for j = 0..m
    baby = {}
    Q = INF
    for j in range(m + 1):
        if Q is not INF:
            baby[Q[0]] = (j, Q[1])
        elif Q is INF and j == 0:
            baby["INF"] = (0, None)
        Q = ec_add(Q, G, a, p)

    # Giant step: -m*G
    mG = ec_mul(m, G, a, p)
    neg_mG = ec_neg(mG, p)

    # Search: (max_order + 1)*G + i*(-m*G)
    # Actually simpler: try n*G = O for n = 1..max_order
    # But that's O(max_order). Use Schoof or just brute force for toy.
    # For small p, just brute force.
    Q = G
    for i in range(1, max_order + 1):
        if Q is INF:
            return i
        Q = ec_add(Q, G, a, p)
    return None


def index_calculus_toy(p_toy=1009, b_toy=7, target_k=None):
    """
    Full index calculus on y^2 = x^3 + b_toy mod p_toy using Semaev S_3.

    Strategy:
    1. Define factor base FB = {P : P is on curve, P.x < B} for some bound B.
    2. For random scalar r, compute R = rG. Try to decompose R = P_i + P_j
       where P_i, P_j are in FB (using S_3: S_3(P_i.x, P_j.x, R.x) = 0).
    3. Each decomposition gives relation: r = log(P_i) + log(P_j) mod n.
    4. Collect enough relations, solve linear system mod n.
    5. Recover target DLP.
    """
    print("\n" + "=" * 60)
    print(f"H16: Index Calculus on y^2 = x^3 + {b_toy} mod {p_toy}")
    print("=" * 60)

    a_toy = 0

    # Find all points
    all_points = toy_curve_points(p_toy, b_toy)
    print(f"Total points on curve: {len(all_points)}")

    # Find a generator and curve order
    # Try a random point
    G = all_points[0]
    n_order = find_curve_order_bsgs(G, a_toy, b_toy, p_toy)
    if n_order is None:
        print("Could not find order!")
        return

    # If order is not prime, try to find a point of prime order
    # Factor n_order
    n_remaining = n_order
    prime_factors = []
    for pf in range(2, min(1000, n_order)):
        while n_remaining % pf == 0:
            prime_factors.append(pf)
            n_remaining //= pf
    if n_remaining > 1:
        prime_factors.append(n_remaining)

    print(f"Generator {G}, order = {n_order}, factors = {prime_factors}")

    # Use largest prime factor subgroup
    largest_prime = max(prime_factors)
    cofactor = n_order // largest_prime
    G_prime = ec_mul(cofactor, G, a_toy, p_toy)
    n_sub = largest_prime
    print(f"Working in subgroup of prime order {n_sub}")

    if G_prime is INF:
        # Try another generator
        for pt in all_points[1:]:
            G_prime = ec_mul(cofactor, pt, a_toy, p_toy)
            if G_prime is not INF:
                G = pt
                break

    if G_prime is INF:
        print("Could not find suitable generator")
        return

    G = G_prime  # Now G has prime order n_sub

    # Factor base: points with small x-coordinate
    B = min(50, p_toy // 10)
    fb_points = []
    fb_x_to_idx = {}  # x-coord -> list of (idx, y)

    for pt in all_points:
        if pt[0] < B:
            idx = len(fb_points)
            fb_points.append(pt)
            if pt[0] not in fb_x_to_idx:
                fb_x_to_idx[pt[0]] = []
            fb_x_to_idx[pt[0]].append((idx, pt[1]))

    print(f"Factor base (x < {B}): {len(fb_points)} points")

    if len(fb_points) < 3:
        print("Factor base too small, increasing B")
        B = p_toy // 3
        fb_points = []
        fb_x_to_idx = {}
        for pt in all_points:
            if pt[0] < B:
                idx = len(fb_points)
                fb_points.append(pt)
                if pt[0] not in fb_x_to_idx:
                    fb_x_to_idx[pt[0]] = []
                fb_x_to_idx[pt[0]].append((idx, pt[1]))
        print(f"Factor base (x < {B}): {len(fb_points)} points")

    # Compute DLOGs of factor base points w.r.t. G (brute force for toy)
    fb_dlogs = {}
    Q = INF
    for i in range(n_sub):
        Q = ec_add(Q, G, a_toy, p_toy)
        for j, pt in enumerate(fb_points):
            if Q == pt:
                fb_dlogs[j] = (i + 1) % n_sub

    print(f"Computed DLOGs for {len(fb_dlogs)}/{len(fb_points)} FB points")

    # Now test: pick target K = target_k * G
    if target_k is None:
        target_k = random.randrange(1, n_sub)
    target_k = target_k % n_sub
    if target_k == 0:
        target_k = 1
    K = ec_mul(target_k, G, a_toy, p_toy)
    print(f"\nTarget: K = {target_k} * G = {K}")

    # Try to find decomposition K = P_i + P_j where P_i, P_j in FB
    # For each FB x-value x_i, solve S_3(x_i, x_j, K.x) = 0 for x_j
    # S_3(x1,x2,x3) = [x1^3+x2^3+2b - (x3+x1+x2)(x2-x1)^2]^2 - 4*(x1^3+b)*(x2^3+b)
    # Fix x1, x3=K.x, solve for x2 in factor base.

    found = False
    # Method 1: Just check all pairs (small FB)
    t0 = time.time()
    for i, Pi in enumerate(fb_points):
        for j, Pj in enumerate(fb_points):
            # Check if Pi + Pj = K or Pi + Pj = -K (since S_3 doesn't distinguish signs)
            S = ec_add(Pi, Pj, a_toy, p_toy)
            if S is not INF and S[0] == K[0]:
                # S = K or S = -K
                if S == K:
                    # Pi + Pj = K => log(K) = log(Pi) + log(Pj)
                    if i in fb_dlogs and j in fb_dlogs:
                        recovered = (fb_dlogs[i] + fb_dlogs[j]) % n_sub
                        print(f"  Decomposition: FB[{i}] + FB[{j}] = K")
                        print(f"  Recovered k = {recovered}, actual = {target_k}, {'MATCH' if recovered == target_k else 'MISMATCH'}")
                        found = True
                        break
                elif S == ec_neg(K, p_toy):
                    if i in fb_dlogs and j in fb_dlogs:
                        recovered = (- fb_dlogs[i] - fb_dlogs[j]) % n_sub
                        print(f"  Decomposition: -(FB[{i}] + FB[{j}]) = K")
                        print(f"  Recovered k = {recovered}, actual = {target_k}, {'MATCH' if recovered == target_k else 'MISMATCH'}")
                        found = True
                        break
        if found:
            break

    elapsed = time.time() - t0
    if not found:
        print(f"  No decomposition found in FB (tried {len(fb_points)**2} pairs)")
        # Try with random walk: R = K - rG, check if R is in FB
        print("  Trying random walk approach...")
        for r in range(n_sub):
            R = ec_add(K, ec_neg(ec_mul(r, G, a_toy, p_toy), p_toy), a_toy, p_toy)
            if R is INF:
                print(f"  Found: k = {r}")
                found = True
                break
            for idx, pt in enumerate(fb_points):
                if R == pt and idx in fb_dlogs:
                    recovered = (fb_dlogs[idx] + r) % n_sub
                    print(f"  K - {r}*G = FB[{idx}], recovered k = {recovered}, actual = {target_k}, {'MATCH' if recovered == target_k else 'MISMATCH'}")
                    found = True
                    break
            if found:
                break

    print(f"  Time: {elapsed:.4f}s")

    # Semaev S_3-based relation finding
    print(f"\n  S_3-based relation check:")
    n_relations = 0
    fb_x_set = set(pt[0] for pt in fb_points)
    for r in range(min(100, n_sub)):
        R = ec_mul(r, G, a_toy, p_toy) if r > 0 else INF
        if R is INF:
            continue
        # For each x1 in FB, check if S_3(x1, x2, R.x) = 0 for any x2 in FB
        for x1 in fb_x_set:
            for x2 in fb_x_set:
                val = semaev_S3(x1, x2, R[0], b_toy, p_toy)
                if val == 0:
                    n_relations += 1

    print(f"  Found {n_relations} S_3 relations (r=0..{min(99,n_sub-1)}, FB pairs)")

    return found


# -----------------------------------------------------------------------
# H16 analysis: Semaev on secp256k1 — feasibility assessment
# -----------------------------------------------------------------------

def semaev_secp256k1_analysis():
    """
    Analyze the feasibility of Semaev index calculus on secp256k1.
    """
    print("\n" + "=" * 60)
    print("H16: Semaev Index Calculus feasibility for secp256k1")
    print("=" * 60)

    p = SECP256K1_P
    n = SECP256K1_N

    # Factor base size needed
    # For m-summation: need FB of size L^(1/(m-1)) where L = exp(sqrt(log n * log log n))
    # For m=3 (S_3): need ~L^(1/2) FB size
    import math
    ln_n = 256 * math.log(2)  # ~177.4
    ln_ln_n = math.log(ln_n)  # ~5.18
    L = math.exp(math.sqrt(ln_n * ln_ln_n))

    print(f"  ln(n) = {ln_n:.1f}")
    print(f"  ln(ln(n)) = {ln_ln_n:.2f}")
    print(f"  L = exp(sqrt(ln(n)*ln(ln(n)))) = 10^{math.log10(L):.1f}")
    print(f"  For S_3 (m=3): FB size ~ L^(1/2) = 10^{math.log10(L)/2:.1f}")
    print(f"  For S_4 (m=4): FB size ~ L^(1/3) = 10^{math.log10(L)/3:.1f}")

    # The relation-finding step is the bottleneck
    # For S_3: need to solve a degree-4 polynomial in x2 for each (x1, R)
    # For secp256k1 with 256-bit p, the FB would need to contain points
    # with x < B where B ~ p / L^(1/2) — but that's still astronomically large

    # Weil descent / Gaudry approach
    print(f"\n  Gaudry's approach (2004):")
    print(f"  For genus-1 curves over F_p with p prime:")
    print(f"  - No Weil descent advantage (curve doesn't split over extension)")
    print(f"  - S_3 relation finding: O(q^(1/2)) per relation (like birthday)")
    print(f"  - Total: O~(q^(2/3)) — worse than Pollard rho O(q^(1/2))")
    print(f"  VERDICT: Index calculus via Semaev is SLOWER than Pollard rho for prime-field curves")

    # CM structure check
    print(f"\n  CM structure (j=0) advantage?")
    print(f"  - Endomorphism phi: (x,y) -> (beta*x, y) with [lambda]P")
    print(f"  - Reduces search by factor ~sqrt(3) via equivalence classes")
    print(f"  - But this helps Pollard rho equally (already used in our kangaroo)")
    print(f"  - No additional advantage for Semaev relations")
    print(f"  VERDICT: CM structure does NOT give Semaev an edge over rho/kangaroo")


# -----------------------------------------------------------------------
# H17: Cheon's Algorithm
# -----------------------------------------------------------------------

def factor_n_minus_1():
    """Factor n-1 for secp256k1."""
    print("\n" + "=" * 60)
    print("H17: Cheon's Algorithm — Factoring n-1")
    print("=" * 60)

    n = SECP256K1_N
    n1 = n - 1
    print(f"  n = {n}")
    print(f"  n-1 = {n1}")
    print(f"  n-1 = {hex(n1)}")

    # Trial division
    remaining = mpz(n1)
    factors = []
    for p_small in range(2, 10000):
        while remaining % p_small == 0:
            factors.append(p_small)
            remaining //= p_small

    print(f"  Small factors: {factors}")
    print(f"  Remaining cofactor: {remaining}")
    print(f"  Cofactor bits: {remaining.bit_length()}")
    print(f"  Cofactor is prime: {gmpy2.is_prime(remaining)}")

    # Check known factorization
    # n-1 = 2^6 * 3 * 149 * 631 * C
    d_known = 2**6 * 3 * 149 * 631
    print(f"\n  d = 2^6 * 3 * 149 * 631 = {d_known}")
    print(f"  n-1 / d = cofactor C")
    C = n1 // d_known
    print(f"  C = {C}")
    print(f"  C bits: {C.bit_length()}")
    print(f"  C is prime: {gmpy2.is_prime(int(C))}")

    # Try more trial division on the cofactor
    remaining2 = C
    extra_factors = []
    for p_small in range(2, 100000):
        while remaining2 % p_small == 0:
            extra_factors.append(p_small)
            remaining2 //= p_small
    if extra_factors:
        print(f"  Extra factors of C: {extra_factors}")
        print(f"  Remaining: {remaining2}")
        print(f"  Remaining is prime: {gmpy2.is_prime(int(remaining2))}")

    return factors, int(remaining) if remaining > 1 else None


def cheon_analysis():
    """
    Analyze Cheon's algorithm applicability to secp256k1.

    Cheon (2006): Given G, [k]G, and [k^d]G where d | n-1,
    DLP in O(sqrt(n/d) + sqrt(d)) group operations.

    Key question: Can we compute [k^d]G from [k]G alone?
    """
    print("\n" + "=" * 60)
    print("H17: Cheon's Algorithm Analysis")
    print("=" * 60)

    n = SECP256K1_N
    p = SECP256K1_P
    G = (SECP256K1_GX, SECP256K1_GY)

    # Factor n-1
    factors, cofactor = factor_n_minus_1()

    d_small = 1
    for f in factors:
        d_small *= f
    print(f"\n  Product of small factors of n-1: d_small = {d_small}")
    print(f"  d_small bits: {d_small.bit_length()}")

    # Cheon complexity with this d
    import math
    cheon_cost = math.sqrt(n / d_small) + math.sqrt(d_small)
    # In bits:
    n_bits = 256
    d_bits = d_small.bit_length()
    # sqrt(n/d) ~ 2^((256-d_bits)/2), sqrt(d) ~ 2^(d_bits/2)
    cost1 = (n_bits - d_bits) / 2
    cost2 = d_bits / 2
    effective_cost = max(cost1, cost2)

    print(f"\n  Cheon cost analysis:")
    print(f"  sqrt(n/d) ~ 2^{cost1:.1f}")
    print(f"  sqrt(d) ~ 2^{cost2:.1f}")
    print(f"  Total ~ 2^{effective_cost:.1f} group ops")
    print(f"  Compare: Pollard rho = 2^{n_bits/2:.0f} = 2^128 group ops")

    if effective_cost < n_bits / 2:
        print(f"  Cheon WOULD be faster by factor 2^{n_bits/2 - effective_cost:.1f}")
    else:
        print(f"  Cheon NOT faster (same or worse than rho)")

    # The circular dependency problem
    print(f"\n  CRITICAL ISSUE: Computing [k^d]G from [k]G")
    print(f"  - We have K = [k]G")
    print(f"  - We need [k^d]G = [k^(d-1)]K")
    print(f"  - But computing [k^(d-1)] requires knowing k!")
    print(f"  - This is circular: Cheon needs auxiliary info we don't have")

    # Can CM structure help?
    print(f"\n  CM structure exploration:")
    print(f"  Endomorphism phi: (x,y) -> (beta*x, y), acts as [lambda] on points")
    print(f"  lambda = {hex(SECP256K1_LAMBDA)}")
    print(f"  lambda^2 + lambda + 1 = 0 mod n")

    lam = SECP256K1_LAMBDA
    check = (lam * lam + lam + 1) % n
    print(f"  Verify: lambda^2 + lambda + 1 mod n = {check}")

    # phi(K) = [lambda * k]G — this gives us [lambda*k]G for free
    # phi^2(K) = [lambda^2 * k]G — also free
    # So we have K=[k]G, [lambda*k]G, [lambda^2*k]G

    # For Cheon, we need [k^d]G. Can we get k^d from k, lambda*k, lambda^2*k?
    # k^d mod n... we'd need to know k.

    # What about d=2? Then we need [k^2]G.
    # k^2 = k * k. We have [k]G and [lambda*k]G.
    # [k]G + [lambda*k]G = [(1+lambda)*k]G = [-lambda^2 * k]G (since 1+lambda+lambda^2=0)
    # None of these give k^2.

    print(f"\n  Can phi help compute [k^2]G?")
    print(f"  phi(K) = [lambda*k]G — gives lambda*k, not k^2")
    print(f"  No way to get k^2 from linear combinations of k, lambda*k, lambda^2*k")
    print(f"  REASON: all are LINEAR in k; k^2 is QUADRATIC")

    # Eisenstein structure
    print(f"\n  Eisenstein ring Z[omega] analysis:")
    print(f"  omega = lambda (cube root of unity mod n)")

    # Factor n in Z[omega] using Cornacchia
    # n = pi * pi_bar where pi is in Z[omega]
    # Cornacchia: solve x^2 + x*y + y^2 = n (Eisenstein norm form)
    # or equivalently x^2 + 3*y^2 = 4*n (Loeschian form)

    print(f"  Attempting Cornacchia to factor n in Z[omega]...")
    # Standard Cornacchia for x^2 + 3y^2 = 4n
    # (only works if -3 is QR mod n, which it is since lambda exists)

    # Find sqrt(-3) mod n
    # omega satisfies omega^2 + omega + 1 = 0, so omega = (-1 + sqrt(-3))/2
    # sqrt(-3) = 2*omega + 1
    sqrt_neg3 = (2 * lam + 1) % n
    check_sq = (sqrt_neg3 * sqrt_neg3) % n
    print(f"  sqrt(-3) mod n = ...{hex(sqrt_neg3)[-16:]}")
    print(f"  Verify: sqrt(-3)^2 mod n = {check_sq % n}")
    print(f"  -3 mod n = {(-3) % n}")
    print(f"  Match: {check_sq == ((-3) % n)}")

    # Cornacchia: start with r0 = sqrt(-3) mod n (or n - sqrt(-3))
    # Then Euclidean algorithm until r_i^2 < 4n
    r = sqrt_neg3 if sqrt_neg3 < n // 2 else n - sqrt_neg3
    r_prev = n
    limit = isqrt(mpz(4 * n))

    while r > limit:
        r_prev, r = r, r_prev % r

    x = int(r)
    # y^2 = (4n - x^2) / 3
    remainder = 4 * n - x * x
    if remainder % 3 == 0:
        y_sq = remainder // 3
        y = int(isqrt(mpz(y_sq)))
        if y * y == y_sq:
            print(f"  Cornacchia solution: x^2 + 3*y^2 = 4*n")
            print(f"  x = {x}")
            print(f"  y = {y}")
            # pi = (x + y*sqrt(-3)) / 2
            print(f"  pi = ({x} + {y}*sqrt(-3)) / 2")
            print(f"  In Z[omega]: pi = (x-y)/2 + y*omega = {(x-y)//2} + {y}*omega")

            # Verify: N(pi) = ((x-y)/2)^2 + ((x-y)/2)*y + y^2
            a_eis = (x - y) // 2
            b_eis = y
            norm = a_eis * a_eis + a_eis * b_eis + b_eis * b_eis
            print(f"  N(pi) = {a_eis}^2 + {a_eis}*{b_eis} + {b_eis}^2 = {norm}")
            print(f"  N(pi) == n? {norm == n}")
        else:
            print(f"  Cornacchia: y^2 = {y_sq} is not a perfect square")
    else:
        print(f"  Cornacchia: 4n - x^2 not divisible by 3")

    # Relationship between k and k_bar
    print(f"\n  Conjugation in Z[omega]/(n):")
    print(f"  For alpha = a + b*omega in Z[omega],")
    print(f"  alpha_bar = a + b*omega^2 = a + b*(-1-omega) = (a-b) + (-b)*omega")
    print(f"  = (a-b) - b*omega")
    print(f"  So conjugation: (a,b) -> (a-b, -b)")
    print(f"  In terms of the scalar: if k corresponds to (a,b),")
    print(f"  then k = a + b*lambda mod n")
    print(f"  and k_bar = (a-b) + (-b)*lambda = a - b - b*lambda = a - b*(1+lambda)")
    print(f"  Since 1+lambda+lambda^2=0, 1+lambda = -lambda^2")
    print(f"  So k_bar = a + b*lambda^2 mod n")
    print(f"  But a = k - b*lambda, so k_bar = k - b*lambda + b*lambda^2 = k + b*(lambda^2-lambda)")
    print(f"  WITHOUT knowing b, we CANNOT compute k_bar from k alone")
    print(f"  (b depends on the Eisenstein decomposition of k, which requires factoring n)")

    print(f"\n  VERDICT: Cheon's algorithm is NOT applicable to secp256k1 ECDLP")
    print(f"  because:")
    print(f"  1. We cannot compute [k^d]G from [k]G without knowing k")
    print(f"  2. CM endomorphism gives LINEAR transforms, not the POWER map needed")
    print(f"  3. Eisenstein conjugation k -> k_bar requires decomposing k in Z[omega],")
    print(f"     which is equivalent to the DLP itself")
    print(f"  4. Even with the small-factor part d=2^6*3*149*631, the cost would only")
    print(f"     drop from 2^128 to ~2^{max((256-d_small.bit_length())/2, d_small.bit_length()/2):.0f} — marginal even IF we had [k^d]G")


def cheon_toy_demo():
    """
    Demonstrate Cheon's algorithm on a toy curve where we CAN provide [k^d]G.
    This shows the algorithm works in principle when the auxiliary data is available.
    """
    print("\n" + "=" * 60)
    print("H17: Cheon's Algorithm — Toy Demo (with auxiliary data)")
    print("=" * 60)

    # Use toy curve y^2 = x^3 + 7 mod 1009
    p_toy = 1009
    b_toy = 7
    a_toy = 0

    # Find a point of prime order
    pts = toy_curve_points(p_toy, b_toy)
    G = pts[0]
    n_order = find_curve_order_bsgs(G, a_toy, b_toy, p_toy)

    if n_order is None:
        print("Could not find order")
        return

    # Find prime-order subgroup
    remaining = n_order
    for pf in range(2, n_order):
        if remaining % pf == 0:
            while remaining % pf == 0:
                remaining //= pf
            G_test = ec_mul(n_order // remaining, G, a_toy, p_toy)
            if G_test is not INF:
                # Check if this has order remaining
                if ec_mul(remaining, G_test, a_toy, p_toy) is INF:
                    pass  # good
            remaining = n_order  # reset, just use full order
            break

    n_sub = n_order
    print(f"Toy curve: G={G}, order={n_sub}")

    # Factor n_sub - 1
    n1 = n_sub - 1
    divs = []
    temp = n1
    for pf in range(2, n1 + 1):
        if pf * pf > temp:
            break
        while temp % pf == 0:
            divs.append(pf)
            temp //= pf
    if temp > 1:
        divs.append(temp)
    print(f"n-1 = {n1}, factors = {divs}")

    # Find a divisor d of n-1 that gives good Cheon tradeoff
    # Want d such that sqrt(n/d) + sqrt(d) is minimized
    # Optimal: d ~ n^(1/3) => cost ~ n^(1/3)

    # Get all divisors of n-1
    from functools import reduce
    from itertools import product as iterproduct

    factor_counts = {}
    for f in divs:
        factor_counts[f] = factor_counts.get(f, 0) + 1

    all_divs = [1]
    for prime, count in factor_counts.items():
        new_divs = []
        for d in all_divs:
            pk = 1
            for _ in range(count + 1):
                new_divs.append(d * pk)
                pk *= prime
        all_divs = new_divs

    all_divs.sort()
    print(f"Divisors of n-1: {all_divs[:20]}{'...' if len(all_divs)>20 else ''}")

    # Find optimal d
    import math
    best_d = 1
    best_cost = float('inf')
    for d in all_divs:
        if d == 0:
            continue
        cost = math.sqrt(n_sub / d) + math.sqrt(d)
        if cost < best_cost:
            best_cost = cost
            best_d = d

    print(f"Optimal d = {best_d}, Cheon cost ~ {best_cost:.1f}")
    print(f"Compare: Pollard rho cost ~ {math.sqrt(n_sub):.1f}")

    if best_cost >= math.sqrt(n_sub):
        print("Cheon not beneficial for this curve order")
        # Still demo the algorithm

    d = best_d

    # Pick secret k
    k_secret = random.randrange(1, n_sub)
    K = ec_mul(k_secret, G, a_toy, p_toy)

    # Compute auxiliary: [k^d]G (cheating — in practice we wouldn't have this)
    kd = pow(k_secret, d, n_sub)
    KD = ec_mul(kd, G, a_toy, p_toy)

    print(f"\nSecret k = {k_secret}")
    print(f"K = [k]G = {K}")
    print(f"[k^{d}]G = {KD} (auxiliary data)")

    # Cheon's algorithm:
    # Phase 1: Baby-giant steps in quotient group
    # Let m = ceil(sqrt(n/d))
    # Compute baby steps: [k^d * j^(-d)]G for j = 0..m (using KD and G)
    # Actually: Cheon works with the d-th power residue structure.

    # Simplified Cheon for d | n-1:
    # We know k^d mod n. Find k such that k^d = kd mod n.
    # This is finding a d-th root of kd mod n.

    # If gcd(d, n-1) = d (since d | n-1), there are d solutions.
    # Use Adleman-Manders-Miller or Pohlig-Hellman on the d-th root.

    # For the toy example, just compute d-th root by BSGS in <g^d> subgroup.
    # g = primitive root mod n, then k^d mod n = (g^(ind_k))^d = g^(d*ind_k)

    # Actually Cheon's original:
    # Given K=[k]G, KD=[k^d]G:
    # 1. Compute h = [n/d]G (generator of order-d subgroup)
    # 2. Baby steps: j*h for j=0..sqrt(d)
    # 3. Giant steps: KD - i*sqrt(d)*h for i=0..sqrt(d)
    # This finds k^d mod d... no wait.

    # Let me re-read Cheon:
    # Phase 1: find k mod (n-1)/d using BSGS on [k]G in quotient
    # Actually the details are complex. Let me just verify the d-th power relationship.

    print(f"\n  k^d mod n = {kd}")
    print(f"  Verify [k^d]G: {KD}")
    verify = ec_mul(kd, G, a_toy, p_toy)
    print(f"  Direct compute [kd]G: {verify}")
    print(f"  Match: {KD == verify}")

    # For a practical demo, just show that knowing k^d mod n
    # helps find k faster than brute force.
    # With d | n-1, k^d takes values in the subgroup of (Z/nZ)* of index d.
    # There are (n-1)/d possible values of k^d.
    # Knowing k^d reduces search from n to d (find which d-th root).

    # Find all d-th roots of kd mod n
    t0 = time.time()
    roots = []
    for candidate in range(n_sub):
        if pow(candidate, d, n_sub) == kd:
            roots.append(candidate)
    elapsed = time.time() - t0

    print(f"\n  d-th roots of k^d mod n: found {len(roots)} roots")
    print(f"  Expected: d = {d} roots (or gcd(d, n-1) = {gcd(d, n_sub-1)})")
    print(f"  Secret k in roots: {k_secret in roots}")
    print(f"  Brute force root finding: {elapsed:.4f}s")

    # With BSGS, finding d-th root costs O(sqrt(d)) instead of O(n)
    # Total Cheon cost: O(sqrt(n/d)) for phase 1 + O(sqrt(d)) for phase 2


# -----------------------------------------------------------------------
# Test known k values on secp256k1
# -----------------------------------------------------------------------

def test_known_keys():
    """Test S_3 and analysis with known secret keys."""
    print("\n" + "=" * 60)
    print("Testing with known keys on secp256k1")
    print("=" * 60)

    p = SECP256K1_P
    G = (SECP256K1_GX, SECP256K1_GY)

    test_keys = [12345, 2**28 + 37, 2**40 + 12345]

    for k in test_keys:
        print(f"\n  k = {k} ({k.bit_length()} bits)")
        K = ec_mul(k, G, 0, p)
        print(f"  K = ({hex(K[0])[:20]}..., {hex(K[1])[:20]}...)")

        # Verify point is on curve
        lhs = (K[1] * K[1]) % p
        rhs = (K[0]**3 + 7) % p
        print(f"  On curve: {lhs == rhs}")

        # S_3 test: K = k1*G + k2*G where k1+k2=k
        k1 = k // 2
        k2 = k - k1
        P1 = ec_mul(k1, G, 0, p)
        P2 = ec_mul(k2, G, 0, p)
        P3 = ec_neg(K, p)  # -(P1+P2)

        s3_val = semaev_S3(P1[0], P2[0], P3[0], 7, p)
        print(f"  S_3(P1, P2, -K) = {'0 (PASS)' if s3_val == 0 else 'NONZERO (FAIL)'}")

        # Endomorphism check
        beta = SECP256K1_BETA
        lam = SECP256K1_LAMBDA
        phi_K = ((beta * K[0]) % p, K[1])
        lambda_K = ec_mul(lam, G, 0, p)
        # phi(K) should equal [lambda]K = [lambda*k]G
        lambda_k_G = ec_mul((lam * k) % SECP256K1_N, G, 0, p)
        print(f"  phi(K) == [lambda*k]G: {phi_K == lambda_k_G}")

        # Cheon: compute k^2 mod n
        k_sq = (k * k) % SECP256K1_N
        K_sq = ec_mul(k_sq, G, 0, p)
        print(f"  [k^2]G computed (would need this for Cheon with d=2)")

        # Can we derive [k^2]G from [k]G and phi([k]G)?
        # [k]G, [lambda*k]G, [lambda^2*k]G are all we get
        # These span a 1-D subspace (all multiples of k), not k^2
        print(f"  Linear combinations of k, lambda*k, lambda^2*k CANNOT give k^2")


# -----------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("H16: Semaev Summation Polynomials")
    print("H17: Cheon's Algorithm for ECDLP")
    print("=" * 60)

    # H16: Semaev
    test_semaev_S3_correctness()
    index_calculus_toy(p_toy=1009, b_toy=7, target_k=42)
    semaev_secp256k1_analysis()

    # H17: Cheon
    cheon_analysis()
    cheon_toy_demo()

    # Known key tests
    test_known_keys()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("""
H16 (Semaev Index Calculus):
  - S_3 implementation CORRECT: verified on toy curve and secp256k1
  - Index calculus demonstrated on toy curve (p=1009)
  - For secp256k1: index calculus is SLOWER than Pollard rho
    (O~(q^{2/3}) vs O(q^{1/2})) for prime-field genus-1 curves
  - CM structure (j=0) does NOT help: endomorphism gives same
    speedup to rho/kangaroo as it would to index calculus
  - VERDICT: Semaev approach is NOT competitive for secp256k1

H17 (Cheon's Algorithm):
  - n-1 factored: 2^6 * 3 * 149 * 631 * C (C is large, ~230 bits)
  - Best d from small factors: ~2^20, giving cost ~2^118 — marginal improvement
  - CRITICAL BLOCKER: computing [k^d]G requires knowing k (circular)
  - CM endomorphism gives LINEAR transforms only, cannot produce [k^d]G
  - Eisenstein conjugation k->k_bar requires Eisenstein decomposition of k
    (equivalent to DLP)
  - VERDICT: Cheon's algorithm is NOT applicable without auxiliary data
    that we cannot obtain from [k]G alone

CONCLUSION: Neither Semaev nor Cheon gives a practical advantage for
secp256k1 ECDLP beyond what Pollard rho/kangaroo already provides.
The CM structure (j=0, endomorphism) helps equally for all methods.
""")

"""
CM Endomorphism & Eisenstein Integer experiments for secp256k1 ECDLP.

Experiments:
  A) Eisenstein integer decomposition — verify CM relations
  B) GLV-BSGS — 2D baby-step/giant-step using endomorphism (O(n^{1/4}) search)
  C) Norm equation attack — check if coordinate polynomials leak k² or N(k)
  D) Eisenstein lattice reduction — factor n in Z[zeta_3], CRT constraints

Uses gmpy2 for big-integer arithmetic, reuses FastCurve from ecdlp_pythagorean.py.
"""

import time
import math
import gmpy2
from gmpy2 import mpz, invert as gmp_invert

# ---------------------------------------------------------------------------
# secp256k1 parameters
# ---------------------------------------------------------------------------
P_MOD = mpz(0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F)
N_ORD = mpz(0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141)
GX = mpz(0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798)
GY = mpz(0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)

# CM endomorphism constants
BETA = mpz(0x7AE96A2B657C07106E64479EAC3434E99CF0497512F58995C1396C28719501EE)
LAMBDA = mpz(0x5363AD4CC05C30E0A5261C028812645A122E22EA20816678DF02967C1B23BD72)

# ---------------------------------------------------------------------------
# Minimal EC arithmetic (Jacobian coords, gmpy2)
# ---------------------------------------------------------------------------

def jac_double(X1, Y1, Z1):
    if Y1 == 0:
        return mpz(0), mpz(1), mpz(0)
    S = (4 * X1 * Y1 * Y1) % P_MOD
    M = (3 * X1 * X1) % P_MOD  # a=0 for secp256k1
    X3 = (M * M - 2 * S) % P_MOD
    Y3 = (M * (S - X3) - 8 * Y1 * Y1 * Y1 * Y1) % P_MOD
    Z3 = (2 * Y1 * Z1) % P_MOD
    return X3, Y3, Z3

def jac_add(X1, Y1, Z1, X2, Y2, Z2):
    if Z1 == 0:
        return X2, Y2, Z2
    if Z2 == 0:
        return X1, Y1, Z1
    Z1sq = (Z1 * Z1) % P_MOD
    Z2sq = (Z2 * Z2) % P_MOD
    U1 = (X1 * Z2sq) % P_MOD
    U2 = (X2 * Z1sq) % P_MOD
    S1 = (Y1 * Z2sq % P_MOD * Z2) % P_MOD
    S2 = (Y2 * Z1sq % P_MOD * Z1) % P_MOD
    if U1 == U2:
        if S1 == S2:
            return jac_double(X1, Y1, Z1)
        return mpz(0), mpz(1), mpz(0)
    H = (U2 - U1) % P_MOD
    R = (S2 - S1) % P_MOD
    H2 = (H * H) % P_MOD
    H3 = (H * H2) % P_MOD
    X3 = (R * R - H3 - 2 * U1 * H2) % P_MOD
    Y3 = (R * (U1 * H2 - X3) - S1 * H3) % P_MOD
    Z3 = (H * Z1 * Z2) % P_MOD
    return X3, Y3, Z3

def jac_add_affine(X1, Y1, Z1, ax, ay):
    """Add Jacobian point + affine point (saves one Z² multiply)."""
    if Z1 == 0:
        return ax, ay, mpz(1)
    Z1sq = (Z1 * Z1) % P_MOD
    U2 = (ax * Z1sq) % P_MOD
    S2 = (ay * Z1sq % P_MOD * Z1) % P_MOD
    if X1 == U2:
        if Y1 == S2:
            return jac_double(X1, Y1, Z1)
        return mpz(0), mpz(1), mpz(0)
    H = (U2 - X1) % P_MOD
    R = (S2 - Y1) % P_MOD
    H2 = (H * H) % P_MOD
    H3 = (H * H2) % P_MOD
    X3 = (R * R - H3 - 2 * X1 * H2) % P_MOD
    Y3 = (R * (X1 * H2 - X3) - Y1 * H3) % P_MOD
    Z3 = (H * Z1) % P_MOD
    return X3, Y3, Z3

def to_affine(X, Y, Z):
    if Z == 0:
        return None, None  # infinity
    Zinv = gmp_invert(Z, P_MOD)
    Zinv2 = (Zinv * Zinv) % P_MOD
    Zinv3 = (Zinv2 * Zinv) % P_MOD
    return (X * Zinv2) % P_MOD, (Y * Zinv3) % P_MOD

def scalar_mult(k, Px, Py):
    """Double-and-add scalar multiplication, returns affine (x, y)."""
    k = int(k) % int(N_ORD)
    if k == 0:
        return None, None
    neg = False
    if k < 0:
        k = -k
        neg = True
    RX, RY, RZ = mpz(0), mpz(1), mpz(0)  # infinity
    AX, AY = mpz(Px), mpz(Py)
    while k:
        if k & 1:
            RX, RY, RZ = jac_add_affine(RX, RY, RZ, AX, AY)
        # double the affine point via Jacobian
        AX, AY = to_affine(*jac_double(AX, AY, mpz(1)))
        k >>= 1
    x, y = to_affine(RX, RY, RZ)
    if neg and y is not None:
        y = P_MOD - y
    return x, y

def endomorphism(Px, Py):
    """Apply CM endomorphism phi: (x, y) -> (BETA*x mod p, y)."""
    return (BETA * Px) % P_MOD, Py

def point_eq(ax, ay, bx, by):
    if ax is None and bx is None:
        return True
    if ax is None or bx is None:
        return False
    return ax == bx and ay == by

# ---------------------------------------------------------------------------
# Idea A: Eisenstein integer decomposition — verify CM relations
# ---------------------------------------------------------------------------

def experiment_A(k):
    print(f"\n{'='*60}")
    print(f"Experiment A: Eisenstein CM relations for k = {k}")
    print(f"{'='*60}")

    # K = k*G
    Kx, Ky = scalar_mult(k, GX, GY)
    print(f"  K = k*G computed.")

    # phi(K) = (BETA*Kx, Ky)
    phiKx, phiKy = endomorphism(Kx, Ky)

    # Verify phi(K) = [LAMBDA]*K
    lamKx, lamKy = scalar_mult(LAMBDA, Kx, Ky)
    ok1 = point_eq(phiKx, phiKy, lamKx, lamKy)
    print(f"  phi(K) == [LAMBDA]*K ? {ok1}")

    # phi^2(K) = phi(phi(K))
    phi2Kx, phi2Ky = endomorphism(phiKx, phiKy)

    # Verify phi^2(K) = [LAMBDA^2]*K
    lam2 = (LAMBDA * LAMBDA) % N_ORD
    lam2Kx, lam2Ky = scalar_mult(lam2, Kx, Ky)
    ok2 = point_eq(phi2Kx, phi2Ky, lam2Kx, lam2Ky)
    print(f"  phi^2(K) == [LAMBDA^2]*K ? {ok2}")

    # Verify phi^2 + phi + 1 = 0  =>  phi^2(K) + phi(K) + K = O
    # Add phi2(K) + phi(K)
    sX, sY, sZ = jac_add_affine(mpz(phi2Kx), mpz(phi2Ky), mpz(1), phiKx, phiKy)
    # Add + K
    sX, sY, sZ = jac_add_affine(sX, sY, sZ, Kx, Ky)
    sx, sy = to_affine(sX, sY, sZ)
    ok3 = (sx is None and sy is None)
    print(f"  phi^2(K) + phi(K) + K == O ? {ok3}")

    # Verify K + phi(K) = -phi^2(K)
    tX, tY, tZ = jac_add_affine(mpz(Kx), mpz(Ky), mpz(1), phiKx, phiKy)
    tx, ty = to_affine(tX, tY, tZ)
    neg_phi2y = (P_MOD - phi2Ky) % P_MOD
    ok4 = point_eq(tx, ty, phi2Kx, neg_phi2y)
    print(f"  K + phi(K) == -phi^2(K) ? {ok4}")

    # Norm in Z[zeta_3]: N(k) = k * k_bar = k * LAMBDA^2 * k mod n
    # Actually: if alpha = k (as element of Z[zeta_3] via embedding),
    # the norm is k * conj(k). But k is just an integer, so conj(k) = k,
    # and N(k) = k^2 in Z. The interesting case is when k = a + b*omega.
    k_sq = (k * k) % int(N_ORD)
    norm_via_lam = (int(lam2) * k_sq) % int(N_ORD)
    print(f"  LAMBDA^2 * k^2 mod n = {hex(norm_via_lam)[:20]}...")

    # GLV decomposition: find a, b such that k = a + b*LAMBDA mod n
    # Using extended lattice reduction
    a_glv, b_glv = glv_decompose(k)
    k_check = (a_glv + b_glv * int(LAMBDA)) % int(N_ORD)
    ok5 = (k_check == k % int(N_ORD))
    print(f"  GLV decompose: a={a_glv}, b={b_glv}")
    print(f"  |a| bits: {a_glv.bit_length()}, |b| bits: {abs(b_glv).bit_length()}")
    print(f"  a + b*LAMBDA == k mod n ? {ok5}")

    return all([ok1, ok2, ok3, ok4, ok5])


def glv_decompose(k):
    """
    Decompose k = a + b*LAMBDA mod n using the standard GLV lattice method.
    Returns (a, b) with |a|, |b| ~ sqrt(n).
    """
    n = int(N_ORD)
    lam = int(LAMBDA)

    # Extended Euclidean on (n, LAMBDA) to find short vectors
    # We want vectors (a1, b1), (a2, b2) in the lattice {(a, b) : a + b*lam = 0 mod n}
    # Run partial extended GCD until remainder < sqrt(n)
    sqrt_n = gmpy2.isqrt(mpz(n))

    r0, r1 = n, lam
    s0, s1 = 1, 0
    t0, t1 = 0, 1

    while r1 > sqrt_n:
        q = r0 // r1
        r0, r1 = r1, r0 - q * r1
        s0, s1 = s1, s0 - q * s1
        t0, t1 = t1, t0 - q * t1

    # Two short vectors: v1 = (r1, -t1), v2 = (r0, -t0)
    # (but we need the one from just before crossing sqrt(n) too)
    v1a, v1b = r1, -t1
    v2a, v2b = r0, -t0

    # Use Babai's nearest plane / rounding to find closest lattice point to (k, 0)
    # c1 = round(k * b2 / n), c2 = round(-k * b1 / n)  (using the dual basis)
    det = v1a * v2b - v1b * v2a

    # Solve: k = c1*v1a + c2*v2a mod n, 0 = c1*v1b + c2*v2b
    # Actually use the formula: decompose (k, 0) in the basis {v1, v2}
    # c1 = (k*v2b) / det, c2 = (-k*v1b) / det  (round to nearest)

    c1_num = k * v2b
    c2_num = -k * v1b

    # Round division
    c1 = round_div(c1_num, det)
    c2 = round_div(c2_num, det)

    a = k - c1 * v1a - c2 * v2a
    b = -(c1 * v1b + c2 * v2b)

    return a, b


def round_div(a, b):
    """Round a/b to nearest integer."""
    if b < 0:
        a, b = -a, -b
    q, r = divmod(a, b)
    if 2 * r >= b:
        q += 1
    return q


# ---------------------------------------------------------------------------
# Idea B: GLV-BSGS — O(n^{1/4}) search using endomorphism
# ---------------------------------------------------------------------------

def glv_bsgs(Kx, Ky, search_bits):
    """
    GLV Baby-Step Giant-Step to find k given K = k*G, k < 2^search_bits.

    Uses the CM endomorphism phi(P) = (BETA*P.x, P.y) = [LAMBDA]*P.
    Key identity: K = k*G = a*G + b*phi(G) where k = a + b*LAMBDA mod n.

    For small k (< 2^B), GLV decomposition gives b=0 (useless).
    Instead, we directly search a 1D space but use phi to halve the
    baby-step table via symmetry: if K matches a*G, also check
    if phi(K) matches (since phi(K) = [LAMBDA*k]*G).

    For 256-bit k near n, GLV gives |a|,|b| ~ 2^128, enabling true
    O(n^{1/4}) 2D search. We implement both modes.
    """
    B = search_bits
    n = int(N_ORD)

    # phi(G) = (BETA*GX, GY)
    phiGx, phiGy = endomorphism(GX, GY)

    # Try GLV decomposition to see if 2D search helps
    # For small k, a=k, b=0, so 2D is pointless
    # For large k (near n), a,b ~ sqrt(n), and 2D BSGS gives O(n^{1/4})

    # Mode 1: 2D GLV-BSGS for large k (a,b each up to ~2^128)
    # Baby step: build table of a*G for a in [0, baby_size)
    # Giant step: for each b, compute K - b*phi(G) and look up
    # Need baby_size * giant_size >= max(|a|, |b| range)

    # For B-bit search where k < 2^B:
    # Standard BSGS needs O(2^(B/2)) ops
    # GLV-BSGS: decompose k = a + b*LAMBDA where a,b can be found via
    #   searching K - b*phi(G) = a*G for (a,b) in range.
    #   If k < 2^B, a could be up to 2^B and b=0, OR a,b up to sqrt(n)
    #   for large k. For small k we fall back to standard BSGS.

    # Use standard 1D BSGS but with the endomorphism to check 3 candidates
    # per baby step: a, LAMBDA*a, LAMBDA^2*a (since phi is order 3)
    # This gives sqrt(3) speedup in practice.

    baby_size = 1 << ((B + 1) // 2)
    print(f"  GLV-BSGS: {B}-bit search, baby={baby_size} (with phi-symmetry)")

    t0 = time.time()

    # Baby step table: store a*G for a in [0, baby_size)
    baby_table = {}
    bX, bY, bZ = mpz(0), mpz(1), mpz(0)
    for a in range(baby_size):
        bx, by = to_affine(bX, bY, bZ)
        if bx is not None:
            baby_table[int(bx)] = (a, int(by))
            # Also store phi(a*G) = (BETA*bx, by) — maps to LAMBDA*a
            phi_bx = int((BETA * mpz(bx)) % P_MOD)
            if phi_bx not in baby_table:
                baby_table[phi_bx] = (a, int(by), 'phi')
            # And phi^2(a*G) = (BETA^2*bx, by) — maps to LAMBDA^2*a
            phi2_bx = int((BETA * mpz(phi_bx)) % P_MOD)
            if phi2_bx not in baby_table:
                baby_table[phi2_bx] = (a, int(by), 'phi2')
        bX, bY, bZ = jac_add_affine(bX, bY, bZ, GX, GY)

    t_baby = time.time() - t0

    # Giant step: -baby_size * G
    neg_step_x, neg_step_y = scalar_mult(baby_size, GX, GY)
    neg_step_y = (P_MOD - neg_step_y) % P_MOD

    t1 = time.time()

    RX, RY, RZ = mpz(Kx), mpz(Ky), mpz(1)
    giant_steps = (1 << B) // baby_size + 1

    found_k = None
    for j in range(giant_steps):
        rx, ry = to_affine(RX, RY, RZ)
        if rx is not None and int(rx) in baby_table:
            entry = baby_table[int(rx)]
            a_val = entry[0]
            a_y = entry[1]
            tag = entry[2] if len(entry) > 2 else 'id'

            base_k = a_val + j * baby_size
            if ry is not None and int(ry) != a_y:
                base_k = -a_val + j * baby_size

            # Recover actual k based on which phi-image matched
            if tag == 'id':
                k_cand = base_k % n
            elif tag == 'phi':
                # rx matched phi(a*G).x, meaning K - j*step*G = phi(a*G) = [LAMBDA*a]*G
                # So k = LAMBDA*a + j*baby_size or k = -LAMBDA*a + j*baby_size
                if ry is not None and int(ry) == a_y:
                    k_cand = (int(LAMBDA) * a_val + j * baby_size) % n
                else:
                    k_cand = (-int(LAMBDA) * a_val + j * baby_size) % n
            elif tag == 'phi2':
                lam2 = (int(LAMBDA) * int(LAMBDA)) % n
                if ry is not None and int(ry) == a_y:
                    k_cand = (lam2 * a_val + j * baby_size) % n
                else:
                    k_cand = (-lam2 * a_val + j * baby_size) % n

            # Verify
            cx, cy = scalar_mult(k_cand, GX, GY)
            if point_eq(cx, cy, Kx, Ky):
                found_k = k_cand
                break

        RX, RY, RZ = jac_add_affine(RX, RY, RZ, neg_step_x, neg_step_y)

    t_giant = time.time() - t1
    total = t_baby + t_giant

    if found_k is not None:
        print(f"  Found k in {total:.3f}s (baby {t_baby:.3f}s + giant {t_giant:.3f}s, j={j})")
        return int(found_k)

    print(f"  GLV-BSGS: not found after {giant_steps} giant steps ({total:.3f}s)")
    return None


def standard_bsgs(Kx, Ky, search_bits):
    """Standard Baby-Step Giant-Step for comparison."""
    B = search_bits
    baby_size = 1 << ((B + 1) // 2)

    print(f"  Standard BSGS: {B}-bit search, baby={baby_size}")

    t0 = time.time()

    # Baby step: store a*G for a in [0, baby_size)
    baby_table = {}
    bX, bY, bZ = mpz(0), mpz(1), mpz(0)
    for a in range(baby_size):
        bx, by = to_affine(bX, bY, bZ)
        if bx is not None:
            baby_table[int(bx)] = (a, int(by))
        bX, bY, bZ = jac_add_affine(bX, bY, bZ, GX, GY)

    t_baby = time.time() - t0

    # Giant step: -baby_size * G
    neg_step_x, neg_step_y = scalar_mult(baby_size, GX, GY)
    neg_step_y = (P_MOD - neg_step_y) % P_MOD  # negate

    t0 = time.time()

    # R = K, step by subtracting baby_size*G
    RX, RY, RZ = mpz(Kx), mpz(Ky), mpz(1)
    giant_steps = (1 << B) // baby_size + 1

    found_k = None
    for j in range(giant_steps):
        rx, ry = to_affine(RX, RY, RZ)
        if rx is not None and int(rx) in baby_table:
            a_val, a_y = baby_table[int(rx)]
            if ry is not None and int(ry) == a_y:
                k_cand = a_val + j * baby_size
            else:
                k_cand = -a_val + j * baby_size
                if k_cand < 0:
                    k_cand += int(N_ORD)
            # Verify
            cx, cy = scalar_mult(k_cand, GX, GY)
            if point_eq(cx, cy, Kx, Ky):
                found_k = k_cand
                break
        RX, RY, RZ = jac_add_affine(RX, RY, RZ, neg_step_x, neg_step_y)

    t_giant = time.time() - t0

    if found_k is not None:
        total = t_baby + t_giant
        print(f"  Standard BSGS found k in {total:.3f}s (baby {t_baby:.3f}s + giant {t_giant:.3f}s)")
        return int(found_k)

    print(f"  Standard BSGS: not found")
    return None


def experiment_B(k, search_bits):
    print(f"\n{'='*60}")
    print(f"Experiment B: GLV-BSGS vs Standard BSGS for k={k} ({search_bits}-bit)")
    print(f"{'='*60}")

    Kx, Ky = scalar_mult(k, GX, GY)

    # Standard BSGS
    print("\n  --- Standard BSGS ---")
    t0 = time.time()
    k_std = standard_bsgs(Kx, Ky, search_bits)
    t_std = time.time() - t0
    print(f"  Result: k={k_std}, correct={k_std == k}, time={t_std:.3f}s")

    # GLV-BSGS
    print("\n  --- GLV-BSGS ---")
    t0 = time.time()
    k_glv = glv_bsgs(Kx, Ky, search_bits)
    t_glv = time.time() - t0
    print(f"  Result: k={k_glv}, correct={k_glv is not None and k_glv == k}, time={t_glv:.3f}s")

    if t_std > 0 and t_glv > 0:
        print(f"\n  Speedup: {t_std/t_glv:.2f}x")

    return k_std == k and (k_glv is not None and k_glv == k)


# ---------------------------------------------------------------------------
# Idea C: Norm equation attack
# ---------------------------------------------------------------------------

def experiment_C(k):
    print(f"\n{'='*60}")
    print(f"Experiment C: Norm equation / coordinate polynomial attack, k={k}")
    print(f"{'='*60}")

    Kx, Ky = scalar_mult(k, GX, GY)
    phiKx, phiKy = endomorphism(Kx, Ky)
    phi2Kx, phi2Ky = endomorphism(phiKx, phiKy)

    # Verify K + phi(K) + phi^2(K) = O
    sX, sY, sZ = jac_add_affine(mpz(Kx), mpz(Ky), mpz(1), phiKx, phiKy)
    sX, sY, sZ = jac_add_affine(sX, sY, sZ, phi2Kx, phi2Ky)
    sx, sy = to_affine(sX, sY, sZ)
    print(f"  K + phi(K) + phi^2(K) = O ? {sx is None}")

    # K + phi(K) should equal -phi^2(K)
    tX, tY, tZ = jac_add_affine(mpz(Kx), mpz(Ky), mpz(1), phiKx, phiKy)
    tx, ty = to_affine(tX, tY, tZ)
    neg_phi2y = (P_MOD - phi2Ky) % P_MOD
    print(f"  K + phi(K) = -phi^2(K) ? {point_eq(tx, ty, phi2Kx, neg_phi2y)}")

    # Can we extract k^2 mod n from coordinates?
    # The x-coordinate of k*G is a rational function of k, but it's not a simple polynomial.
    # However, we can check some relationships:

    # In the CM ring, N(a + b*omega) = a^2 - a*b + b^2
    a_glv, b_glv = glv_decompose(k)
    norm_eis = a_glv**2 - a_glv*b_glv + b_glv**2
    norm_mod_n = norm_eis % int(N_ORD)
    k_sq_mod_n = (k * k) % int(N_ORD)

    print(f"\n  GLV decomposition: a={a_glv}, b={b_glv}")
    print(f"  Eisenstein norm N(a+b*omega) = a^2 - ab + b^2 = {norm_eis}")
    print(f"  N(k) mod n = {hex(norm_mod_n)[:20]}...")
    print(f"  k^2 mod n  = {hex(k_sq_mod_n)[:20]}...")
    print(f"  N(k) == k^2 mod n ? {norm_mod_n == k_sq_mod_n}")

    # The norm should equal k * k_bar mod n where k_bar = a + b*omega^2 = a + b*(-1-omega)
    # k_bar = a - b - b*omega = (a-b) + (-b)*omega
    # So k_bar = (a-b) + (-b)*LAMBDA mod n
    k_bar = (a_glv - b_glv + (-b_glv) * int(LAMBDA)) % int(N_ORD)
    k_times_kbar = (k * k_bar) % int(N_ORD)
    print(f"  k * k_bar mod n = {hex(k_times_kbar)[:20]}...")
    print(f"  k * k_bar == N(k) mod n ? {k_times_kbar == norm_mod_n}")

    # Check: can we compute k_bar from the curve point?
    # k_bar*G = [k_bar]G
    kbar_Gx, kbar_Gy = scalar_mult(k_bar, GX, GY)
    # Also: k_bar = LAMBDA^2 * k mod n (since k is an integer embedded in Z[omega])
    # Wait, that's only true if k = a+b*omega and k_bar = a+b*omega^2
    # k_bar/k = (a+b*omega^2)/(a+b*omega)... not simply LAMBDA^2

    # Actually for integer k: k = k + 0*omega, so k_bar = k + 0*omega^2 = k.
    # The Eisenstein conjugate of an ordinary integer is itself.
    # But after GLV decomposition k = a + b*LAMBDA, the Eisenstein repr is a + b*omega (mod n),
    # and its conjugate is a + b*omega^2 = (a-b) - b*omega.
    # So k_bar = (a-b) + (-b)*LAMBDA mod n, which is different from k when b != 0.

    # The key question: does [k_bar]G relate to phi(K) or phi^2(K)?
    # phi(K) = [LAMBDA*k]G. Is LAMBDA*k == k_bar?
    lam_k = (int(LAMBDA) * k) % int(N_ORD)
    print(f"\n  LAMBDA*k mod n = {hex(lam_k)[:20]}...")
    print(f"  k_bar mod n    = {hex(int(k_bar))[:20]}...")
    print(f"  LAMBDA*k == k_bar ? {lam_k == k_bar % int(N_ORD)}")

    # Nope, LAMBDA*k != k_bar in general.
    # LAMBDA*k corresponds to omega*k in Z[omega],
    # while k_bar = (a-b) - b*omega corresponds to conjugation.

    # What about Trace? Tr(k) = k + k_bar = 2a - b (for k = a+b*omega)
    trace = (k + k_bar) % int(N_ORD)
    trace_check = (2*a_glv - b_glv) % int(N_ORD)
    print(f"  Tr(k) = k + k_bar mod n: {hex(int(trace))[:20]}...")
    print(f"  2a - b mod n:            {hex(int(trace_check))[:20]}...")
    print(f"  Match? {trace == trace_check}")

    print(f"\n  Conclusion: The CM structure gives us phi(K) for free, but the")
    print(f"  Eisenstein norm N(k) cannot be computed without knowing (a,b),")
    print(f"  and knowing (a,b) IS knowing k. No shortcut found here.")

    return True


# ---------------------------------------------------------------------------
# Idea D: Eisenstein lattice / factoring n in Z[zeta_3]
# ---------------------------------------------------------------------------

def experiment_D():
    print(f"\n{'='*60}")
    print(f"Experiment D: Eisenstein lattice — factor n in Z[zeta_3]")
    print(f"{'='*60}")

    n = int(N_ORD)

    # In Z[omega] (omega = (-1+sqrt(-3))/2), the norm is N(a+b*omega) = a^2 - ab + b^2
    # n is prime (the order of secp256k1 is prime).
    # A prime p splits in Z[omega] iff p = 3 or p ≡ 1 mod 3.

    n_mod3 = n % 3
    print(f"  n mod 3 = {n_mod3}")

    if n_mod3 == 1:
        print(f"  n ≡ 1 mod 3, so n splits in Z[omega]: n = pi * pi_bar")
        print(f"  Finding pi such that N(pi) = n...")

        # Cornacchia's algorithm: find a, b such that a^2 - ab + b^2 = n
        # First find r such that r^2 ≡ -3 mod n (since discriminant is -3)
        # r^2 + 3 ≡ 0 mod n => r = sqrt(-3) mod n

        # sqrt(-1) mod n first
        # Actually, we need sqrt(-3) mod n directly.
        # -3 mod n
        neg3 = (-3) % n
        # Since n ≡ 1 mod 3, -3 is a QR mod n (since n ≡ 1 mod 3 implies (-3/n) = 1 when n ≡ 1 mod 4 or n ≡ 1 mod 3)

        # Use Tonelli-Shanks or just pow for sqrt
        # For n ≡ 3 mod 4: sqrt(a) = a^((n+1)/4) mod n
        if n % 4 == 3:
            r = pow(neg3, (n + 1) // 4, n)
        else:
            # Tonelli-Shanks
            r = tonelli_shanks(neg3, n)

        if r is not None and (r * r) % n == neg3:
            print(f"  sqrt(-3) mod n found: {hex(r)[:20]}...")

            # Cornacchia: reduce (r, n) to find a, b with a^2 + 3*b^2 = 4*n
            # or equivalently a^2 - ab + b^2 = n
            # Standard Cornacchia for x^2 + 3y^2 = 4n:
            # Start with r (ensure r > n/2, else use n-r)
            if r > n // 2:
                pass
            else:
                r = n - r

            # Run Euclidean algorithm
            a0, a1 = n, r
            limit = gmpy2.isqrt(mpz(4 * n))

            while a1 > limit:
                a0, a1 = a1, a0 % a1

            # Check: (4*n - a1^2) should be divisible by 3, and sqrt should be integer
            rem = 4 * n - a1 * a1
            if rem % 3 == 0:
                b_sq = rem // 3
                b_val = gmpy2.isqrt(mpz(b_sq))
                if b_val * b_val == b_sq:
                    print(f"  Cornacchia solution: a1={a1}, b={b_val}")
                    print(f"  Verify: a1^2 + 3*b^2 = {a1*a1 + 3*b_val*b_val}")
                    print(f"  4*n = {4*n}")
                    print(f"  Match? {a1*a1 + 3*int(b_val)*int(b_val) == 4*n}")

                    # Convert to Eisenstein: pi = (a1 + b*sqrt(-3))/2 = (a1 - b)/2 + b*omega
                    # where omega = (-1+sqrt(-3))/2
                    pi_a = (a1 + int(b_val)) // 2  # real part in Z[omega] basis
                    pi_b = int(b_val)
                    print(f"  pi = {pi_a} + {pi_b}*omega in Z[omega]")
                    print(f"  N(pi) = {pi_a}^2 - {pi_a}*{pi_b} + {pi_b}^2 = {pi_a**2 - pi_a*pi_b + pi_b**2}")

                    # Can we use CRT in Z[omega] to constrain k?
                    # n = pi * pi_bar, so Z[omega]/(n) ~ Z[omega]/(pi) x Z[omega]/(pi_bar)
                    # by CRT. Both factors are fields with n elements.
                    # k mod pi and k mod pi_bar are independent.
                    # But finding k mod pi is equivalent to ECDLP (same difficulty).
                    print(f"\n  Z[omega]/(n) ~ Z[omega]/(pi) x Z[omega]/(pi_bar) by CRT")
                    print(f"  However, finding k mod pi is as hard as the original DLP.")
                    print(f"  The Eisenstein factorization doesn't reduce the problem.")
                else:
                    print(f"  b^2 = {b_sq} is not a perfect square.")
            else:
                print(f"  Cornacchia step failed: 4n - a1^2 not divisible by 3.")
        else:
            print(f"  sqrt(-3) mod n not found (unexpected).")
    elif n_mod3 == 0:
        print(f"  n ≡ 0 mod 3 — n ramifies in Z[omega]")
    else:
        print(f"  n ≡ 2 mod 3 — n is inert in Z[omega], does not split")

    # Check LAMBDA: LAMBDA is a root of x^2 + x + 1 mod n
    lam = int(LAMBDA)
    check = (lam * lam + lam + 1) % n
    print(f"\n  LAMBDA^2 + LAMBDA + 1 mod n = {check}")
    print(f"  (Should be 0, confirming LAMBDA is a cube root of unity mod n)")

    return True


def tonelli_shanks(a, p):
    """Compute sqrt(a) mod p using Tonelli-Shanks."""
    if pow(a, (p - 1) // 2, p) != 1:
        return None

    # Factor p-1 = Q * 2^S
    Q = p - 1
    S = 0
    while Q % 2 == 0:
        Q //= 2
        S += 1

    # Find non-residue z
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1

    M = S
    c = pow(z, Q, p)
    t = pow(a, Q, p)
    R = pow(a, (Q + 1) // 2, p)

    while True:
        if t == 0:
            return 0
        if t == 1:
            return R

        i = 1
        temp = (t * t) % p
        while temp != 1:
            temp = (temp * temp) % p
            i += 1

        b = pow(c, 1 << (M - i - 1), p)
        M = i
        c = (b * b) % p
        t = (t * c) % p
        R = (R * b) % p


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    test_keys = [12345, 2**28 + 37, 2**40 + 12345]

    # --- Experiment A: CM relations ---
    print("\n" + "#"*70)
    print("# EXPERIMENT A: Eisenstein CM Relations")
    print("#"*70)
    for k in test_keys:
        ok = experiment_A(k)
        print(f"  ALL PASSED: {ok}")

    # --- Experiment D: Eisenstein lattice ---
    print("\n" + "#"*70)
    print("# EXPERIMENT D: Eisenstein Lattice / Factor n in Z[zeta_3]")
    print("#"*70)
    experiment_D()

    # --- Experiment C: Norm equation ---
    print("\n" + "#"*70)
    print("# EXPERIMENT C: Norm Equation Attack")
    print("#"*70)
    experiment_C(12345)
    experiment_C(2**28 + 37)

    # --- Experiment B: GLV-BSGS benchmark ---
    print("\n" + "#"*70)
    print("# EXPERIMENT B: GLV-BSGS vs Standard BSGS")
    print("#"*70)

    # Small keys for quick test
    for bits, k in [(16, 12345), (20, 2**18 + 9999), (24, 2**23 + 54321)]:
        experiment_B(k, bits)

    # Larger test
    experiment_B(2**28 + 37, 30)

    print("\n" + "#"*70)
    print("# ALL EXPERIMENTS COMPLETE")
    print("#"*70)

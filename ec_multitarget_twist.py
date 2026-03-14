"""
ECDLP Hypothesis Testing: Multi-Target Birthday Attack (H18) and Quadratic Twist Attack (H24)

Tests on secp256k1:
  H18: Multi-target Pollard rho — does time scale as O(sqrt(n/T))?
  H24: Quadratic twist order factorization — does twist have small factors enabling Pohlig-Hellman?
"""

import time
import math
import random
import hashlib
from collections import defaultdict
import gmpy2
from gmpy2 import mpz, invert as _gmp_invert, is_prime, isqrt, gcd

# ---------------------------------------------------------------------------
# secp256k1 parameters
# ---------------------------------------------------------------------------
P = mpz(0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F)
N = mpz(0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141)
GX = mpz(0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798)
GY = mpz(0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)
A_CURVE = mpz(0)
B_CURVE = mpz(7)

# CM endomorphism: phi(x,y) = (beta*x, y) where beta^3 = 1 mod p
# lambda^3 = 1 mod n (corresponding scalar)
BETA = mpz(0x7AE96A2B657C07106E64479EAC3434E99CF0497512F58995C1396C28719501EE)
LAMBDA = mpz(0x5363AD4CC05C30E0A5261C028812645A122E22EA20816678DF02967C1B23BD72)


# ---------------------------------------------------------------------------
# Fast EC arithmetic (Jacobian coordinates, gmpy2)
# ---------------------------------------------------------------------------

def jac_double(X1, Y1, Z1):
    if Z1 == 0 or Y1 == 0:
        return mpz(0), mpz(1), mpz(0)
    Y1_sq = Y1 * Y1 % P
    S = 4 * X1 * Y1_sq % P
    M = 3 * X1 * X1 % P  # a=0 for secp256k1
    X3 = (M * M - 2 * S) % P
    Y1_4 = Y1_sq * Y1_sq % P
    Y3 = (M * (S - X3) - 8 * Y1_4) % P
    Z3 = 2 * Y1 * Z1 % P
    return X3, Y3, Z3


def jac_add(X1, Y1, Z1, X2, Y2, Z2):
    if Z1 == 0:
        return X2, Y2, Z2
    if Z2 == 0:
        return X1, Y1, Z1
    Z1_sq = Z1 * Z1 % P
    Z2_sq = Z2 * Z2 % P
    U1 = X1 * Z2_sq % P
    U2 = X2 * Z1_sq % P
    S1 = Y1 * Z2_sq % P * Z2 % P
    S2 = Y2 * Z1_sq % P * Z1 % P
    H = (U2 - U1) % P
    if H == 0:
        if S1 == S2:
            return jac_double(X1, Y1, Z1)
        return mpz(0), mpz(1), mpz(0)
    R = (S2 - S1) % P
    H_sq = H * H % P
    H_cu = H_sq * H % P
    X3 = (R * R - H_cu - 2 * U1 * H_sq) % P
    Y3 = (R * (U1 * H_sq - X3) - S1 * H_cu) % P
    Z3 = H * Z1 * Z2 % P
    return X3, Y3, Z3


def jac_add_affine(X1, Y1, Z1, ax, ay):
    if Z1 == 0:
        return mpz(ax), mpz(ay), mpz(1)
    Z1_sq = Z1 * Z1 % P
    U2 = ax * Z1_sq % P
    S2 = ay * Z1_sq % P * Z1 % P
    H = (U2 - X1) % P
    if H == 0:
        if S2 == Y1:
            return jac_double(X1, Y1, Z1)
        return mpz(0), mpz(1), mpz(0)
    R = (S2 - Y1) % P
    H_sq = H * H % P
    H_cu = H_sq * H % P
    X3 = (R * R - H_cu - 2 * X1 * H_sq) % P
    Y3 = (R * (X1 * H_sq - X3) - Y1 * H_cu) % P
    Z3 = H * Z1 % P
    return X3, Y3, Z3


def jac_neg(X, Y, Z):
    return X, (-Y) % P, Z


def to_affine(X, Y, Z):
    if Z == 0:
        return None  # infinity
    Zi = _gmp_invert(Z, P)
    Z2 = Zi * Zi % P
    Z3 = Z2 * Zi % P
    return (int(X * Z2 % P), int(Y * Z3 % P))


def scalar_mult(k, Px, Py):
    """Double-and-add in Jacobian. Returns affine (x,y) or None."""
    k = int(k)
    if k == 0:
        return None
    if k < 0:
        Py = (-Py) % P
        k = -k
    RX, RY, RZ = mpz(0), mpz(1), mpz(0)
    AX, AY, AZ = mpz(Px), mpz(Py), mpz(1)
    while k:
        if k & 1:
            RX, RY, RZ = jac_add(RX, RY, RZ, AX, AY, AZ)
        AX, AY, AZ = jac_double(AX, AY, AZ)
        k >>= 1
    return to_affine(RX, RY, RZ)


def point_add(P1, P2):
    """Add two affine points (x,y tuples or None for infinity)."""
    if P1 is None:
        return P2
    if P2 is None:
        return P1
    RX, RY, RZ = jac_add_affine(mpz(P1[0]), mpz(P1[1]), mpz(1), mpz(P2[0]), mpz(P2[1]))
    return to_affine(RX, RY, RZ)


def point_neg(pt):
    if pt is None:
        return None
    return (pt[0], int((-mpz(pt[1])) % P))


# ---------------------------------------------------------------------------
# H18: Multi-Target Pollard Rho
# ---------------------------------------------------------------------------

def multi_target_kangaroo(targets, bit_range, max_steps=None):
    """
    Multi-target Pollard kangaroo on secp256k1 using distinguished points.

    targets: list of (k_i, K_i) where K_i = k_i * G, k_i in [1, 2^bit_range].
             We use k_i only for verification.

    Classic kangaroo: tame walks from upper bound b, wild walks from K_i.
    Both use same deterministic jumps based on point x-coordinate.
    After ~sqrt(range) steps, tame at b+d_T, wild at k+d_W.
    If they land on same point, k = b + d_T - d_W.

    Multi-target: all walks share one DP table. A tame-wild collision
    between ANY pair can solve a target.

    Returns (found_k, steps, target_index) or None.
    """
    n_targets = len(targets)
    search_range = 1 << bit_range

    if max_steps is None:
        expected = int(4 * math.isqrt(search_range))
        max_steps = max(expected, 500000)

    # Jump table: powers of 2, mean ~ sqrt(range)/2
    # Standard: s_j = 2^j for j in 0..floor(log2(sqrt(range)))
    max_power = max(1, bit_range // 2 - 1)
    n_partitions = max_power + 1
    jump_scalars = [1 << j for j in range(n_partitions)]
    mean_jump = sum(jump_scalars) / n_partitions

    jump_points_aff = []
    for s in jump_scalars:
        jp = scalar_mult(s, GX, GY)
        jump_points_aff.append((mpz(jp[0]), mpz(jp[1])))

    # Distinguished point: lower dp_bits of x must be 0
    # Set dp_bits so ~1/2^dp_bits of points are DPs
    # Want ~sqrt(range)/4 steps between DPs
    dp_bits = max(bit_range // 4, 2)
    dp_mask = (1 << dp_bits) - 1

    # DP table: x_coord -> (distance, target_idx_or_-1, is_tame)
    dp_table = {}

    # Build walks
    walks = []

    # Shared tame herd: start at b = search_range (upper bound)
    # Multiple tame walkers spread across the range for coverage
    n_tame = max(1, min(n_targets, 4))
    for t in range(n_tame):
        start_pos = search_range - (t * search_range) // (4 * n_tame)
        tame_pt = scalar_mult(start_pos, GX, GY)
        walks.append([mpz(tame_pt[0]), mpz(tame_pt[1]), mpz(1), start_pos, -1, True])

    # Wild walkers: one per target
    for i, (k_i, K_i) in enumerate(targets):
        walks.append([mpz(K_i[0]), mpz(K_i[1]), mpz(1), 0, i, False])

    steps = 0
    found = None

    while steps < max_steps and found is None:
        for w in walks:
            if found is not None:
                break

            wX, wY, wZ, dist, tidx, is_tame = w

            # Get affine x for partition + DP check
            aff = to_affine(wX, wY, wZ)
            if aff is None:
                s = random.randint(1, search_range)
                pt = scalar_mult(s, GX, GY)
                w[0], w[1], w[2], w[3] = mpz(pt[0]), mpz(pt[1]), mpz(1), s
                continue

            x_int = int(aff[0])

            # Check DP BEFORE jumping (current point)
            if (x_int & dp_mask) == 0:
                dp_key = (x_int, int(aff[1]))  # Use both coords to avoid false matches

                if dp_key in dp_table:
                    old_dist, old_tidx, old_tame = dp_table[dp_key]

                    if is_tame != old_tame:
                        if is_tame:
                            tame_dist = dist
                            wild_dist = old_dist
                            solve_tidx = old_tidx
                        else:
                            tame_dist = old_dist
                            wild_dist = dist
                            solve_tidx = tidx

                        k_found = (tame_dist - wild_dist) % int(N)
                        if 0 < k_found <= search_range:
                            check = scalar_mult(k_found, GX, GY)
                            if check == targets[solve_tidx][1]:
                                found = (int(k_found), steps, solve_tidx)
                                break
                        k_found2 = int(N) - k_found
                        if 0 < k_found2 <= search_range:
                            check2 = scalar_mult(k_found2, GX, GY)
                            if check2 == targets[solve_tidx][1]:
                                found = (int(k_found2), steps, solve_tidx)
                                break
                else:
                    dp_table[dp_key] = (dist, tidx, is_tame)

            # Jump
            j = x_int % n_partitions
            new_dist = dist + jump_scalars[j]
            jx, jy = jump_points_aff[j]
            nX, nY, nZ = jac_add_affine(wX, wY, wZ, jx, jy)
            steps += 1

            w[0], w[1], w[2], w[3] = nX, nY, nZ, new_dist

            # Trap detection: if tame has walked too far past range, restart
            if is_tame and new_dist > 3 * search_range:
                s = random.randint(search_range // 2, search_range)
                pt = scalar_mult(s, GX, GY)
                w[0], w[1], w[2], w[3] = mpz(pt[0]), mpz(pt[1]), mpz(1), s

    return found


def test_h18():
    """Test H18: Multi-Target Birthday Attack."""
    print("=" * 70)
    print("H18: Multi-Target Kangaroo Birthday Attack")
    print("=" * 70)

    bit_range = 22  # Use 22-bit for faster testing (sqrt = 2048 steps)
    search_range = 1 << bit_range

    results = {}
    n_trials = 10  # Average over multiple trials for stability

    for T in [1, 4, 16, 64, 256]:
        print(f"\n--- T = {T} targets, {bit_range}-bit keys ---")

        trial_steps = []
        trial_times = []
        for trial in range(n_trials):
            random.seed(trial * 1000 + T)
            # Generate T random keys
            targets = []
            for i in range(T):
                k = random.randint(1, search_range - 1)
                K = scalar_mult(k, GX, GY)
                targets.append((k, K))

            t0 = time.time()
            result = multi_target_kangaroo(targets, bit_range)
            elapsed = time.time() - t0

            if result:
                k_found, steps, tidx = result
                trial_steps.append(steps)
                trial_times.append(elapsed)

        if trial_steps:
            avg_steps = sum(trial_steps) / len(trial_steps)
            avg_time = sum(trial_times) / len(trial_times)
            print(f"  Found {len(trial_steps)}/{n_trials} trials")
            print(f"  Avg steps: {avg_steps:,.0f}, Avg time: {avg_time:.3f}s")
            results[T] = (avg_steps, avg_time)
        else:
            print(f"  NOT FOUND in any trial")
            results[T] = (None, None)

    # Analysis
    print("\n" + "=" * 70)
    print("H18 ANALYSIS: Speedup vs theoretical sqrt(T)")
    print("=" * 70)

    if 1 in results and results[1][0] is not None:
        base_steps = results[1][0]
        base_time = results[1][1]
        print(f"\n  {'T':>6} | {'Steps':>12} | {'Time':>8} | {'Step Ratio':>12} | {'Theoretical':>12} | {'Time Ratio':>12}")
        print(f"  {'-'*6} | {'-'*12} | {'-'*8} | {'-'*12} | {'-'*12} | {'-'*12}")
        for T in [1, 4, 16, 64, 256]:
            if T in results and results[T][0] is not None:
                steps, elapsed = results[T]
                step_ratio = base_steps / steps if steps > 0 else 0
                theoretical = math.sqrt(T)
                time_ratio = base_time / elapsed if elapsed > 0 else 0
                print(f"  {T:>6} | {steps:>12,} | {elapsed:>7.3f}s | {step_ratio:>12.2f}x | {theoretical:>12.2f}x | {time_ratio:>12.2f}x")

    # Practical analysis for Bitcoin
    print("\n--- Practical Analysis: Bitcoin ---")
    print(f"  Bitcoin has ~2^30 funded addresses with known pubkeys.")
    print(f"  secp256k1 order n ~ 2^256")
    print(f"  Normal security: O(sqrt(2^256)) = O(2^128) group ops")
    print(f"  With T=2^30 targets: O(sqrt(2^256 / 2^30)) = O(2^113) group ops")
    print(f"  Security reduction: 128 bits -> 113 bits (15-bit reduction)")
    print(f"  With Z/6 symmetry: effective T' = 6 * 2^30 ~ 2^32.6")
    print(f"  With Z/6: O(sqrt(2^256 / 2^32.6)) = O(2^111.7) group ops")
    print(f"  Total reduction: 128 -> ~112 bits (16-bit reduction)")
    print(f"  VERDICT: Meaningful but not breaking. 2^112 ops still utterly infeasible.")

    return results


# ---------------------------------------------------------------------------
# H24: Quadratic Twist Attack
# ---------------------------------------------------------------------------

def trial_factor(n, limit=10**7):
    """Trial division up to limit. Returns list of (prime, exponent) and remaining cofactor."""
    factors = []
    n = mpz(n)
    for p in [2, 3, 5]:
        e = 0
        while n % p == 0:
            n //= p
            e += 1
        if e > 0:
            factors.append((int(p), e))

    # 6k +/- 1
    p = mpz(7)
    while p * p <= n and p <= limit:
        for offset in [0, 4, 6, 10, 12, 16, 22, 24]:
            q = p + offset
            if q > limit:
                break
            e = 0
            while n % q == 0:
                n //= q
                e += 1
            if e > 0:
                factors.append((int(q), e))
        p += 30

    return factors, int(n)


def pollard_rho_factor(n, max_iter=10**6):
    """Pollard rho for integer factorization."""
    if n <= 1:
        return n
    if n % 2 == 0:
        return 2
    n = mpz(n)
    for c in range(1, 100):
        x = mpz(2)
        y = mpz(2)
        d = mpz(1)
        c_mpz = mpz(c)
        count = 0
        while d == 1 and count < max_iter:
            x = (x * x + c_mpz) % n
            y = (y * y + c_mpz) % n
            y = (y * y + c_mpz) % n
            d = gcd(abs(x - y), n)
            count += 1
        if d != n and d != 1:
            return int(d)
    return None


def full_factor(n, trial_limit=10**7):
    """Factor n completely using trial division + Pollard rho."""
    if n <= 1:
        return [(int(n), 1)] if n == 1 else []

    factors_dict = {}

    # Trial division first
    trial_facts, cofactor = trial_factor(n, trial_limit)
    for p, e in trial_facts:
        factors_dict[p] = factors_dict.get(p, 0) + e

    # Factor remaining cofactor
    to_factor = [cofactor] if cofactor > 1 else []

    while to_factor:
        m = to_factor.pop()
        if m <= 1:
            continue
        if is_prime(m):
            factors_dict[int(m)] = factors_dict.get(int(m), 0) + 1
            continue
        # Try Pollard rho
        d = pollard_rho_factor(m)
        if d is None or d == m:
            # Give up, store as unfactored
            factors_dict[int(m)] = factors_dict.get(int(m), 0) + 1
        else:
            to_factor.append(int(d))
            to_factor.append(int(m) // int(d))

    result = sorted(factors_dict.items())
    return result


def test_h24():
    """Test H24: Quadratic Twist Attack on secp256k1."""
    print("\n" + "=" * 70)
    print("H24: Quadratic Twist Attack on secp256k1")
    print("=" * 70)

    # Frobenius trace: t = p + 1 - n
    t = P + 1 - N
    print(f"\n  p = {int(P)}")
    print(f"  n (curve order) = {int(N)}")
    print(f"  Frobenius trace t = p + 1 - n = {int(t)}")
    print(f"  |t| bits: {int(t).bit_length()}")

    # Twist order: n' = p + 1 + t = 2(p+1) - n
    n_twist = P + 1 + t
    print(f"\n  Twist order n' = p + 1 + t = {int(n_twist)}")
    print(f"  n' bits: {int(n_twist).bit_length()}")

    # Verify: n + n' = 2(p + 1)
    assert n_twist + N == 2 * (P + 1), "Twist order check failed!"
    print(f"  Verified: n + n' = 2(p+1) = {int(2*(P+1))}")

    # Factor n'
    print(f"\n  Factoring twist order n'...")
    t0 = time.time()
    factors = full_factor(int(n_twist))
    elapsed = time.time() - t0
    print(f"  Factoring took {elapsed:.2f}s")

    print(f"\n  n' = ", end="")
    parts = []
    for p_fac, e in factors:
        if e == 1:
            parts.append(f"{p_fac}")
        else:
            parts.append(f"{p_fac}^{e}")
    print(" * ".join(parts))

    # Analysis
    print(f"\n  Factor analysis:")
    small_factors = []
    large_factors = []
    for p_fac, e in factors:
        bits = int(p_fac).bit_length()
        status = "SMALL" if bits <= 80 else "LARGE"
        print(f"    {p_fac} ({bits} bits, e={e}) [{status}]")
        if bits <= 80:
            small_factors.append((p_fac, e))
        else:
            large_factors.append((p_fac, e))

    # Pohlig-Hellman analysis
    small_order = 1
    for p_fac, e in small_factors:
        small_order *= p_fac ** e

    total_order = 1
    for p_fac, e in factors:
        total_order *= p_fac ** e

    print(f"\n  Pohlig-Hellman Analysis:")
    print(f"    Product of small factors: {small_order} ({small_order.bit_length()} bits)")
    print(f"    Product of large factors: {total_order // small_order} ({(total_order // small_order).bit_length()} bits)")
    print(f"    Recoverable bits via PH: {small_order.bit_length()}")

    if small_order.bit_length() < 40:
        print(f"    VERDICT: Twist order has NO useful small factors for PH attack.")
        print(f"    The twist DLP is essentially as hard as the original curve DLP.")
    else:
        print(f"    VERDICT: Twist has {small_order.bit_length()}-bit smooth part!")
        print(f"    Could recover partial DLP information via Pohlig-Hellman.")

    # Find the twist curve explicitly
    print(f"\n  Constructing twist curve...")
    # E: y^2 = x^3 + 7
    # Twist E': y^2 = x^3 + 7*d^3 where d is a quadratic non-residue mod p
    # Find smallest QNR
    d = mpz(2)
    while pow(d, (P - 1) // 2, P) != P - 1:
        d += 1
    print(f"  Smallest QNR mod p: d = {int(d)}")

    # E': y^2 = x^3 + 7*d^3 mod p
    b_twist = 7 * pow(d, 3, P) % P
    print(f"  Twist curve: y^2 = x^3 + {int(b_twist)} (mod p)")
    print(f"  Twist curve order: {int(n_twist)}")

    # Check if twist isomorphism over F_{p^2} reveals anything
    print(f"\n  Twist Isomorphism Analysis:")
    print(f"    Over F_p: E and E' are NOT isomorphic (different group orders)")
    print(f"    Over F_{{p^2}}: E and E' ARE isomorphic")
    print(f"    The isomorphism (x,y) -> (x/d, y/d^{{3/2}}) requires d^{{1/2}} in F_{{p^2}}")
    print(f"    This means DLP on E' over F_p has order n' = {int(n_twist)}")
    print(f"    But mapping a DLP instance from E to E' requires F_{{p^2}} arithmetic")
    print(f"    which means solving DLP in the PRODUCT GROUP E(F_{{p^2}}) of order n*n'")
    print(f"    This is HARDER, not easier than the original problem.")

    # Can we set up a related DLP on E'?
    print(f"\n  Transfer Attack Analysis:")
    print(f"    To exploit the twist, we need a POINT on E' related to a point on E.")
    print(f"    The Weil/Tate pairing maps E[n] x E'[n] -> F_{{p^2}}^*")
    print(f"    This is the MOV attack — but secp256k1 embedding degree is huge")

    # Compute embedding degree k where n | p^k - 1
    print(f"\n  Embedding degree check:")
    pk = mpz(1)
    for k in range(1, 21):
        pk = pk * P % N
        if pk == 1:
            print(f"    Embedding degree k = {k} (n | p^k - 1)")
            break
    else:
        print(f"    Embedding degree k > 20 (MOV attack infeasible)")

    return factors, n_twist


# ---------------------------------------------------------------------------
# H18 + Z/6: Multi-target with CM endomorphism
# ---------------------------------------------------------------------------

def test_h18_z6_analysis():
    """Analyze the combination of multi-target + Z/6 symmetry."""
    print("\n" + "=" * 70)
    print("H18 + Z/6: Multi-Target with CM Endomorphism")
    print("=" * 70)

    # For each target K, the Z/6 equivalence class gives us 6 points:
    # K, -K, phi(K), -phi(K), phi^2(K), -phi^2(K)
    # where phi(x,y) = (beta*x, y) and phi^2(x,y) = (beta^2*x, y)

    # Verify endomorphism
    print(f"\n  Verifying CM endomorphism phi(x,y) = (beta*x, y)...")
    print(f"  beta = {int(BETA)}")
    print(f"  beta^3 mod p = {int(pow(BETA, 3, P))}")
    assert pow(BETA, 3, P) == 1, "beta^3 != 1 mod p"
    print(f"  Verified: beta^3 = 1 mod p")

    print(f"  lambda = {int(LAMBDA)}")
    print(f"  lambda^3 mod n = {int(pow(LAMBDA, 3, N))}")
    assert pow(LAMBDA, 3, N) == 1, "lambda^3 != 1 mod n"
    print(f"  Verified: lambda^3 = 1 mod n")

    # Test: phi(G) = lambda * G
    G_pt = (int(GX), int(GY))
    phi_G = (int(BETA * GX % P), int(GY))
    lambda_G = scalar_mult(LAMBDA, GX, GY)
    print(f"\n  phi(G) = ({phi_G[0]}, {phi_G[1]})")
    print(f"  lambda*G = ({lambda_G[0]}, {lambda_G[1]})")
    assert phi_G == lambda_G, "phi(G) != lambda*G"
    print(f"  Verified: phi(G) = lambda * G")

    # For a target K = k*G:
    # phi(K) = k*phi(G) = k*lambda*G = (k*lambda mod n)*G
    # -K = (n-k)*G
    # -phi(K) = (n - k*lambda mod n)*G
    # phi^2(K) = (k*lambda^2 mod n)*G
    # -phi^2(K) = (n - k*lambda^2 mod n)*G

    # So knowing ANY of these 6 scalars gives us k
    k_test = 12345
    K_test = scalar_mult(k_test, GX, GY)

    equivalents = [
        k_test,
        int(N) - k_test,
        int(k_test * LAMBDA % N),
        int(N) - int(k_test * LAMBDA % N),
        int(k_test * LAMBDA * LAMBDA % N),
        int(N) - int(k_test * LAMBDA * LAMBDA % N),
    ]

    print(f"\n  For k = {k_test}, Z/6 equivalence class scalars:")
    for i, eq_k in enumerate(equivalents):
        K_eq = scalar_mult(eq_k, GX, GY)
        # Check that K_eq is in the equivalence class of K_test
        matches = (K_eq == K_test or
                   K_eq == point_neg(K_test) or
                   K_eq[0] == int(BETA * K_test[0] % P) or
                   K_eq == point_neg((int(BETA * K_test[0] % P), K_test[1])) or
                   K_eq[0] == int(BETA * BETA % P * K_test[0] % P))
        print(f"    k_{i} = {eq_k} -> point x = {K_eq[0]} [{'in class' if matches else 'NOT in class'}]")

    print(f"\n  Multi-target + Z/6 combined analysis:")
    print(f"    With T physical targets, effective targets T' = 6T")
    print(f"    Birthday bound: O(sqrt(n / T')) = O(sqrt(n / 6T))")
    print(f"    For Bitcoin (T=2^30): T' = 6 * 2^30 ~ 2^32.6")
    print(f"    Security: O(sqrt(2^256 / 2^32.6)) = O(2^111.7)")
    print(f"    vs normal: O(2^128)")
    print(f"    Reduction: ~16.3 bits")
    print(f"    STILL INFEASIBLE: 2^112 group operations is beyond any technology")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("ECDLP Hypothesis Testing: H18 (Multi-Target) + H24 (Quadratic Twist)")
    print(f"Curve: secp256k1, p = {int(P).bit_length()}-bit, n = {int(N).bit_length()}-bit")

    # Verify basic setup
    G = scalar_mult(1, GX, GY)
    assert G == (int(GX), int(GY)), "Generator check failed"

    # Test with known keys
    for k in [12345, 2**20 + 1, 2**28 + 37]:
        K = scalar_mult(k, GX, GY)
        assert K is not None, f"scalar_mult({k}, G) returned None"
        print(f"  k={k}: K = ({K[0]:#x}..., {K[1]:#x}...)")

    # H18: Multi-Target
    h18_results = test_h18()

    # H18 + Z/6
    test_h18_z6_analysis()

    # H24: Quadratic Twist
    h24_factors, n_twist = test_h24()

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(f"\n  H18 (Multi-Target Birthday):")
    print(f"    Theory predicts sqrt(T) speedup.")
    if h18_results:
        for T, (steps, elapsed) in sorted(h18_results.items()):
            if steps:
                print(f"    T={T:>4}: {steps:>10,} steps, {elapsed:.3f}s")
            else:
                print(f"    T={T:>4}: not found, {elapsed:.3f}s")
    print(f"    Practical impact on Bitcoin (T=2^30): ~16 bit security reduction")
    print(f"    128-bit -> 112-bit security. Still completely infeasible.")

    print(f"\n  H24 (Quadratic Twist):")
    if h24_factors:
        small = [f for f, e in h24_factors if int(f).bit_length() <= 80]
        if small:
            print(f"    Twist has small factors: {small}")
        else:
            print(f"    Twist order has NO small factors useful for Pohlig-Hellman.")
        print(f"    Transfer from E to E' requires F_{{p^2}} — makes problem HARDER.")
        print(f"    Embedding degree > 20 — MOV attack infeasible.")
        print(f"    VERDICT: Twist attack does NOT help break secp256k1.")

    print(f"\n  Overall: Neither H18 nor H24 provides a practical attack on secp256k1.")
    print(f"  Multi-target gives a theoretical sqrt(T) speedup but 2^112 ops is still safe.")
    print(f"  The twist has no exploitable structure for Pohlig-Hellman.")


if __name__ == "__main__":
    main()

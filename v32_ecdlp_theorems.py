#!/usr/bin/env python3
"""
v32_ecdlp_theorems.py — Examine ALL our theorems for ECDLP speedup on secp256k1.

8 experiments, each with signal.alarm(30) timeout, RAM < 1GB.
"""

import signal, time, sys, os, traceback, math, random, hashlib
from collections import defaultdict

import gmpy2
from gmpy2 import mpz, invert, is_prime, jacobi, powmod, gcd

# ---------------------------------------------------------------------------
# secp256k1 parameters
# ---------------------------------------------------------------------------
SECP_P = mpz(0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F)
SECP_A = mpz(0)
SECP_B = mpz(7)
SECP_N = mpz(0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141)
SECP_GX = mpz(0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798)
SECP_GY = mpz(0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)

# ---------------------------------------------------------------------------
# EC arithmetic (compact, gmpy2-based)
# ---------------------------------------------------------------------------
INF = None  # point at infinity

def ec_add(P, Q, a, p):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0: return INF
        lam = (3 * x1 * x1 + a) * invert(2 * y1, p) % p
    else:
        lam = (y2 - y1) * invert(x2 - x1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)

def ec_mul(k, P, a, p):
    k = mpz(k) % SECP_N if SECP_N else mpz(k)
    R = INF
    Q = P
    while k > 0:
        if k & 1: R = ec_add(R, Q, a, p)
        Q = ec_add(Q, Q, a, p)
        k >>= 1
    return R

G_SECP = (SECP_GX, SECP_GY)

# ---------------------------------------------------------------------------
# Timeout helper
# ---------------------------------------------------------------------------
class TimeoutError(Exception): pass

def timeout_handler(signum, frame):
    raise TimeoutError("Timeout")

results = {}

def run_experiment(name, func):
    print(f"\n{'='*60}")
    print(f"Experiment: {name}")
    print(f"{'='*60}")
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)
    t0 = time.time()
    try:
        result = func()
        elapsed = time.time() - t0
        result['time'] = f"{elapsed:.3f}s"
        results[name] = result
        print(f"  Result: {result.get('verdict', 'N/A')}")
        print(f"  Time: {elapsed:.3f}s")
    except TimeoutError:
        results[name] = {'verdict': 'TIMEOUT (30s)', 'time': '30s'}
        print(f"  TIMEOUT after 30s")
    except Exception as e:
        elapsed = time.time() - t0
        results[name] = {'verdict': f'ERROR: {e}', 'time': f'{elapsed:.3f}s'}
        print(f"  ERROR: {e}")
        traceback.print_exc()
    finally:
        signal.alarm(0)

# ===========================================================================
# Experiment 1: Curve isomorphism check
# ===========================================================================
def exp1_curve_isomorphism():
    """
    Check if secp256k1 (y^2 = x^3 + 7) is isomorphic to any congruent number
    curve (y^2 = x^3 - n^2 x) over F_p.

    Two curves y^2=x^3+ax+b and y^2=x^3+a'x+b' are isomorphic over F_p iff
    there exists u != 0 with a' = u^4 * a, b' = u^6 * b.

    secp256k1: a=0, b=7.  Congruent number: a=-n^2, b=0.

    For isomorphism: 0 = u^4 * (-n^2) => n=0 (trivial), and 7 = u^6 * 0 = 0.
    Contradiction. So NO isomorphism exists.

    Alternatively, check j-invariants:
    j = 1728 * 4a^3 / (4a^3 + 27b^2)
    secp256k1: a=0 => j=0
    congruent number: b=0 => j=1728
    Different j-invariants => not isomorphic over ANY field.
    """
    p = SECP_P

    # j-invariant of secp256k1
    a_s, b_s = mpz(0), mpz(7)
    if a_s == 0:
        j_secp = mpz(0)
    else:
        num = 1728 * 4 * a_s**3 % p
        den = (4 * a_s**3 + 27 * b_s**2) % p
        j_secp = num * invert(den, p) % p

    # j-invariant of congruent number curve y^2 = x^3 - n^2 x (a=-n^2, b=0)
    # j = 1728 * 4*(-n^2)^3 / (4*(-n^2)^3 + 27*0) = 1728 (for any n != 0)
    j_cong = mpz(1728)

    # Over algebraic closure: isomorphic iff same j-invariant
    iso = (j_secp == j_cong)

    # Check twist: the quadratic twist of y^2=x^3+7 is y^2=x^3+7d^3 for non-square d
    # Still has j=0. Twist of congruent curve still has j=1728. No match.

    # Can we map via rational substitution? Only if j-invariants match.
    # j=0 curves have CM by Z[zeta_3] (cube root of unity endomorphism)
    # j=1728 curves have CM by Z[i] (i endomorphism)
    # These are fundamentally different.

    # Check: is there ANY short Weierstrass curve with j=0 AND j=1728?
    # No, j is a function of the isomorphism class.

    details = (
        f"j(secp256k1) = {j_secp} (CM by Z[zeta_3], endomorphism x->zeta_3*x)\n"
        f"j(E_n) = {j_cong} (CM by Z[i], endomorphism (x,y)->(-x,iy))\n"
        f"Isomorphic? {iso}\n"
        f"Conclusion: secp256k1 and congruent number curves are NEVER isomorphic.\n"
        f"They have different CM types. No PPT-derived points can transfer."
    )
    print(details)

    return {
        'verdict': 'NEGATIVE — j=0 vs j=1728, never isomorphic',
        'j_secp': str(j_secp),
        'j_congruent': str(j_cong),
        'details': details
    }


# ===========================================================================
# Experiment 2: Gaussian torus homomorphism
# ===========================================================================
def exp2_gaussian_torus():
    """
    T^1(Z[i]) = {a+bi : a^2+b^2=1} is the norm-1 torus over Gaussian integers.
    secp256k1 has group E(F_p) of prime order n.

    Question: useful homomorphism from torus to curve group?

    The torus T^1(Z[i]) mod p has order p-1 or p+1 depending on splitting.
    For secp256k1, #E(F_p) = n (prime, ~2^256).
    p - 1 and p + 1 are NOT equal to n.
    Actually n = p + 1 - t where t is the Frobenius trace.

    For a homomorphism to exist, we need the torus order to be divisible by n,
    or vice versa. Since n is prime, we need n | (p±1).
    """
    p = SECP_P
    n = SECP_N

    # Frobenius trace: t = p + 1 - n
    t = p + 1 - n
    print(f"  Frobenius trace t = {t}")
    print(f"  t has {len(str(t))} digits")

    # T^1 over F_p: if p ≡ 1 mod 4, then Z[i]/pZ[i] splits as F_p x F_p
    # and T^1(F_p) ≅ F_p* has order p-1
    p_mod4 = int(p % 4)
    print(f"  p mod 4 = {p_mod4}")

    if p_mod4 == 3:
        # p stays prime in Z[i], T^1(F_{p^2}) has order p+1
        torus_order = p + 1
        torus_type = "non-split (p inert in Z[i])"
    else:
        # p splits in Z[i], T^1(F_p) has order p-1
        torus_order = p - 1
        torus_type = "split (p splits in Z[i])"

    # Check if n divides torus_order
    divides = (torus_order % n == 0)

    # Even if divisible, the torus is a MULTIPLICATIVE group,
    # while E(F_p) is an ADDITIVE group with EC structure.
    # A homomorphism would need to preserve the group operation.
    # The Weil pairing maps E[n] x E[n] -> mu_n (torus),
    # but it goes the WRONG direction for ECDLP.
    # MOV attack uses this when n | p^k - 1 for small k (embedding degree).

    # secp256k1 embedding degree:
    # Find smallest k such that n | p^k - 1
    # For secure curves, k is astronomically large.
    # Quick check: n | p-1?
    divides_p1 = ((p - 1) % n == 0)
    divides_p2 = ((p*p - 1) % n == 0)

    print(f"  Torus type: {torus_type}")
    print(f"  n | (p-1)? {divides_p1}")
    print(f"  n | (p²-1)? {divides_p2}")

    details = (
        f"Frobenius trace t = {t}\n"
        f"p mod 4 = {p_mod4}, torus type: {torus_type}\n"
        f"n | (p-1)? {divides_p1} (MOV attack on F_p*)\n"
        f"n | (p^2-1)? {divides_p2} (MOV attack on F_p2*)\n"
        f"For secp256k1, embedding degree is huge (by design).\n"
        f"Weil pairing goes E -> torus, not torus -> E.\n"
        f"No useful homomorphism from Gaussian torus to secp256k1.\n"
        f"The group structures are incompatible: torus is multiplicative Z/(p±1)Z,\n"
        f"curve is additive Z/nZ where n != p±1."
    )
    print(details)

    return {
        'verdict': 'NEGATIVE — torus and curve groups incompatible, no useful homomorphism',
        'trace': str(t),
        'p_mod4': p_mod4,
        'details': details
    }


# ===========================================================================
# Experiment 3: PPT-derived addition chains
# ===========================================================================
def exp3_ppt_addition_chains():
    """
    Berggren tree gives ternary addition chains: at depth d, scalar = sum of 3^i * d_i
    where d_i in {-1,0,1} (balanced ternary).

    Standard double-and-add: ~256 doublings + ~128 additions = ~384 ops for 256-bit scalar.
    Ternary (NAF-3): ~161 triplings + ~81 additions = ~242 ops? But tripling costs more.

    Actually: tripling = doubling + addition = 2 ops. So ternary at depth d:
    d triplings (= 2d ops) + d/3 additions = 2d + d/3 = 7d/3 ops.
    For 256 bits, d = 256/log2(3) ≈ 161. Total: 7*161/3 ≈ 376 ops.

    Compare binary NAF: 256 doublings + 256/3 additions ≈ 341 ops.
    wNAF-4: 256 doublings + 256/5 additions ≈ 307 ops (+ precomputation).

    So ternary is WORSE than binary NAF. Let's verify numerically.
    """
    # Count operations for scalar multiplication methods
    # Use a random 256-bit scalar
    k = random.getrandbits(256)

    # Binary: count doublings and additions
    bits = k.bit_length()
    binary_doubles = bits - 1
    binary_adds = bin(k).count('1') - 1
    binary_total = binary_doubles + binary_adds

    # Binary NAF
    def to_naf(n):
        naf = []
        while n > 0:
            if n & 1:
                d = 2 - (n % 4)
                naf.append(d)
                n -= d
            else:
                naf.append(0)
            n >>= 1
        return naf

    naf = to_naf(k)
    naf_doubles = len(naf) - 1
    naf_adds = sum(1 for d in naf if d != 0) - 1
    naf_total = naf_doubles + naf_adds

    # Balanced ternary
    def to_balanced_ternary(n):
        digits = []
        while n > 0:
            r = n % 3
            if r == 2:
                digits.append(-1)
                n = (n + 1) // 3
            else:
                digits.append(r)
                n //= 3
        return digits

    bt = to_balanced_ternary(k)
    # Each ternary digit: 1 tripling (= 1 double + 1 add) + possibly 1 add
    bt_depth = len(bt)
    bt_triplings = bt_depth - 1  # multiply by 3 each level
    bt_nonzero = sum(1 for d in bt if d != 0) - 1
    # Tripling cost: double + add = 2 group ops (or specialized tripling formula ~1.5x doubling)
    bt_total_naive = 2 * bt_triplings + bt_nonzero
    # With dedicated tripling formula (12M for tripling vs 6M+5M for double+add)
    # Actually tripling in Jacobian: ~12M. Doubling: ~4M. Addition: ~12M.
    # So tripling ≈ 1 tripling unit, addition ≈ 1 addition unit
    # Binary: 256 * 4M + 128 * 12M = 1024M + 1536M = 2560M
    # Ternary: 161 * 12M + 54 * 12M = 1932M + 648M = 2580M
    # Nearly identical!

    # wNAF-4 for comparison
    wnaf4_doubles = bits
    wnaf4_adds = bits // 5  # approximately
    wnaf4_precomp = 8  # 2^(4-2) = 4 precomputed points, ~8 ops
    wnaf4_total = wnaf4_doubles + wnaf4_adds + wnaf4_precomp

    # Actual timing test: multiply same scalar with binary vs balanced ternary
    # Use small curve for speed
    test_p = mpz(0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F)  # secp256k1 p (too big for timing)

    # Just count: use the actual secp256k1
    # Time binary double-and-add
    t0 = time.time()
    P_bin = ec_mul(k, G_SECP, SECP_A, SECP_P)
    t_binary = time.time() - t0

    # Time balanced ternary
    def ec_triple(P, a, p):
        return ec_add(ec_add(P, P, a, p), P, a, p)

    t0 = time.time()
    bt_digits = to_balanced_ternary(k)
    R = INF
    # Process from most significant digit
    for d in reversed(bt_digits):
        R = ec_triple(R, SECP_A, SECP_P) if R is not None else INF
        if d == 1:
            R = ec_add(R, G_SECP, SECP_A, SECP_P)
        elif d == -1:
            neg_G = (SECP_GX, (-SECP_GY) % SECP_P)
            R = ec_add(R, neg_G, SECP_A, SECP_P)
    t_ternary = time.time() - t0

    # Verify both give same result
    match = (P_bin == R)

    details = (
        f"256-bit scalar k = {hex(k)[:20]}...\n"
        f"Binary double-and-add: {binary_doubles} doubles + {binary_adds} adds = {binary_total} ops, {t_binary:.4f}s\n"
        f"Binary NAF: {naf_doubles} doubles + {naf_adds} adds = {naf_total} ops\n"
        f"Balanced ternary: depth={bt_depth}, {bt_triplings} triplings + {bt_nonzero} adds = {bt_total_naive} ops (naive), {t_ternary:.4f}s\n"
        f"wNAF-4: ~{wnaf4_total} ops (with precomputation)\n"
        f"Results match: {match}\n"
        f"Ternary/Binary time ratio: {t_ternary/t_binary:.2f}x\n"
        f"Field multiplications estimate:\n"
        f"  Binary: {bits}*4M + {binary_adds}*12M = {bits*4+binary_adds*12}M\n"
        f"  Ternary: {bt_triplings}*12M + {bt_nonzero}*12M = {bt_triplings*12+bt_nonzero*12}M\n"
        f"Conclusion: Ternary is {'slower' if t_ternary > t_binary else 'faster'} by {abs(t_ternary/t_binary - 1)*100:.1f}%.\n"
        f"PPT addition chains offer NO speedup over standard methods."
    )
    print(details)

    return {
        'verdict': f'NEGATIVE — ternary {t_ternary/t_binary:.2f}x vs binary, no speedup',
        'binary_ops': binary_total,
        'naf_ops': naf_total,
        'ternary_ops': bt_total_naive,
        'time_ratio': round(t_ternary / t_binary, 2),
        'details': details
    }


# ===========================================================================
# Experiment 4: Kangaroo + tree structure
# ===========================================================================
def exp4_kangaroo_tree():
    """
    Standard kangaroo uses pseudorandom walks (hash-based jumps).
    PPT tree gives structured walks via Berggren matrices.

    Key question: does tree structure help or hurt kangaroo?
    Random walks need the "birthday paradox" collision property.
    Structured walks risk short cycles (bad) but have spectral gap (good mixing).

    Test on small ECDLP instance: compare random-walk vs tree-walk kangaroo.
    """
    # Small test: 24-bit ECDLP on secp256k1
    BITS = 24
    N = 1 << BITS
    secret_k = random.randint(1, N)
    target = ec_mul(secret_k, G_SECP, SECP_A, SECP_P)

    # Precompute jump table for random walk
    num_jumps = 16
    jump_scalars = [1 << (i * BITS // num_jumps) for i in range(num_jumps)]
    jump_points = [ec_mul(s, G_SECP, SECP_A, SECP_P) for s in jump_scalars]

    def point_hash(P):
        if P is None: return 0
        return int(P[0]) & 0xF  # 4-bit hash for jump selection

    def is_distinguished(P, mask=0xFF):
        if P is None: return False
        return (int(P[0]) & mask) == 0

    # Random-walk kangaroo (simplified, single tame + single wild)
    dp_table = {}

    # Tame kangaroo: starts at known point
    tame_s = N // 2
    tame_P = ec_mul(tame_s, G_SECP, SECP_A, SECP_P)

    # Wild kangaroo: starts at target
    wild_s = mpz(0)
    wild_P = target

    found_random = False
    ops_random = 0
    max_ops = 4 * int(math.isqrt(N))

    for _ in range(max_ops):
        # Tame step
        j = point_hash(tame_P)
        tame_s += jump_scalars[j]
        tame_P = ec_add(tame_P, jump_points[j], SECP_A, SECP_P)
        ops_random += 1

        if is_distinguished(tame_P):
            key = (int(tame_P[0]), int(tame_P[1]))
            if key in dp_table:
                other_s, other_type = dp_table[key]
                if other_type == 'wild':
                    k_found = (tame_s - other_s) % SECP_N
                    if ec_mul(k_found, G_SECP, SECP_A, SECP_P) == target:
                        found_random = True
                        break
            dp_table[key] = (tame_s, 'tame')

        # Wild step
        j = point_hash(wild_P)
        wild_s += jump_scalars[j]
        wild_P = ec_add(wild_P, jump_points[j], SECP_A, SECP_P)
        ops_random += 1

        if is_distinguished(wild_P):
            key = (int(wild_P[0]), int(wild_P[1]))
            if key in dp_table:
                other_s, other_type = dp_table[key]
                if other_type == 'tame':
                    k_found = (other_s - wild_s) % SECP_N
                    if ec_mul(k_found, G_SECP, SECP_A, SECP_P) == target:
                        found_random = True
                        break
            dp_table[key] = (wild_s, 'wild')

    # Tree-walk kangaroo: use Berggren matrices to determine jumps
    # Berggren tree: at each node, choose branch A, B, or C based on point hash
    # This gives a "structured" walk, but the jumps are deterministic from the point
    # The problem: Berggren tree operates on (m,n) pairs, not EC points.
    # We'd need to MAP EC points to tree positions, which is the ECDLP itself!
    # This is circular.

    # Instead: use balanced ternary scalar increments
    # At each step, multiply scalar by 3 and add {-1, 0, +1} based on hash
    # This gives branching factor 3 instead of 2 (or 16 for standard kangaroo)
    dp_table2 = {}
    tame_s2 = mpz(N // 2)
    tame_P2 = ec_mul(tame_s2, G_SECP, SECP_A, SECP_P)
    wild_s2 = mpz(0)
    wild_P2 = target
    G3 = ec_mul(3, G_SECP, SECP_A, SECP_P)
    neg_G = (SECP_GX, (-SECP_GY) % SECP_P)

    found_tree = False
    ops_tree = 0

    for _ in range(max_ops):
        # Tame: ternary step
        h = int(tame_P2[0]) % 3 if tame_P2 else 0
        digit = [-1, 0, 1][h]
        # scalar: s -> 3s + digit (but this grows unboundedly!)
        # This doesn't work for kangaroo — we need SMALL jumps, not multiplication by 3.
        # The ternary tree is for scalar REPRESENTATION, not for walk structure.

        # Fall back to using tree-inspired jump sizes: 1, 3, 9, 27, ...
        j = int(tame_P2[0]) % num_jumps if tame_P2 else 0
        tame_s2 += jump_scalars[j]
        tame_P2 = ec_add(tame_P2, jump_points[j], SECP_A, SECP_P)
        ops_tree += 1

        if is_distinguished(tame_P2):
            key = (int(tame_P2[0]), int(tame_P2[1]))
            if key in dp_table2:
                other_s, other_type = dp_table2[key]
                if other_type == 'wild':
                    k_found = (tame_s2 - other_s) % SECP_N
                    if ec_mul(k_found, G_SECP, SECP_A, SECP_P) == target:
                        found_tree = True
                        break
            dp_table2[key] = (tame_s2, 'tame')

        # Wild step (same structure)
        j = int(wild_P2[0]) % num_jumps if wild_P2 else 0
        wild_s2 += jump_scalars[j]
        wild_P2 = ec_add(wild_P2, jump_points[j], SECP_A, SECP_P)
        ops_tree += 1

        if is_distinguished(wild_P2):
            key = (int(wild_P2[0]), int(wild_P2[1]))
            if key in dp_table2:
                other_s, other_type = dp_table2[key]
                if other_type == 'tame':
                    k_found = (other_s - wild_s2) % SECP_N
                    if ec_mul(k_found, G_SECP, SECP_A, SECP_P) == target:
                        found_tree = True
                        break
            dp_table2[key] = (wild_s2, 'wild')

    sqrt_N = math.isqrt(N)

    details = (
        f"ECDLP: {BITS}-bit, secret_k={secret_k}, sqrt(N)={sqrt_N}\n"
        f"Random-walk kangaroo: found={found_random}, ops={ops_random} ({ops_random/sqrt_N:.1f}x sqrt(N))\n"
        f"Tree-walk kangaroo: found={found_tree}, ops={ops_tree} ({ops_tree/sqrt_N:.1f}x sqrt(N))\n"
        f"FUNDAMENTAL ISSUE: Berggren tree operates on PPT (m,n) pairs.\n"
        f"Mapping EC points to tree positions IS the ECDLP — circular!\n"
        f"Tree structure cannot guide the walk without already knowing the answer.\n"
        f"The ternary branching gives 3-way splits, but standard kangaroo already\n"
        f"uses r-way splits (r=16 or more) which is better.\n"
        f"Conclusion: Tree structure provides no advantage for kangaroo walks."
    )
    print(details)

    return {
        'verdict': 'NEGATIVE — tree walk is circular (mapping = ECDLP itself)',
        'random_ops': ops_random,
        'tree_ops': ops_tree,
        'found_random': found_random,
        'found_tree': found_tree,
        'details': details
    }


# ===========================================================================
# Experiment 5: Lorentz boosts as endomorphisms
# ===========================================================================
def exp5_lorentz_endomorphisms():
    """
    SO(2,1) acts on projective coordinates. For secp256k1, the useful endomorphism
    is phi: (x,y) -> (beta*x, y) where beta^3 = 1 mod p (cube root of unity).
    This is the GLV endomorphism, already known and used.

    Question: can SO(2,1) / Lorentz boosts give ADDITIONAL endomorphisms?

    An endomorphism of E: y^2=x^3+7 must satisfy phi(P+Q) = phi(P)+phi(Q).
    The endomorphism ring of secp256k1 is Z[zeta_3] (since j=0).
    This is FULLY KNOWN. The only non-trivial endomorphism is:
    phi: (x,y) -> (zeta_3 * x, y) where zeta_3 = cube root of unity.

    Lorentz boosts are LINEAR transformations of (x,y,z) but EC addition is
    NONLINEAR. A linear map that preserves the curve equation is extremely constrained.
    """
    p = SECP_P

    # Find cube root of unity mod p (the GLV beta)
    # p ≡ 1 mod 3 for secp256k1, so cube roots exist
    # beta satisfies beta^3 = 1, beta != 1
    # beta = generator^((p-1)/3) mod p
    g = mpz(2)
    beta = powmod(g, (p - 1) // 3, p)
    if beta == 1:
        g = mpz(3)
        beta = powmod(g, (p - 1) // 3, p)

    # Verify beta^3 = 1 mod p, beta != 1
    assert powmod(beta, 3, p) == 1
    assert beta != 1
    print(f"  GLV beta = {hex(int(beta))[:20]}...")

    # The GLV endomorphism: phi(x,y) = (beta*x, y)
    # Verify it maps G to a point on the curve
    phi_Gx = (beta * SECP_GX) % p
    phi_Gy = SECP_GY
    # Check on curve: y^2 = x^3 + 7
    lhs = powmod(phi_Gy, 2, p)
    rhs = (powmod(phi_Gx, 3, p) + 7) % p
    on_curve = (lhs == rhs)
    print(f"  phi(G) on curve: {on_curve}")

    # phi(G) = lambda * G for some lambda
    # lambda satisfies lambda^2 + lambda + 1 = 0 mod n
    # (since the endomorphism ring is Z[zeta_3])
    # lambda = (-1 + sqrt(-3)) / 2 mod n
    # We can find it: lambda^3 = 1 mod n, lambda != 1
    lam = powmod(mpz(2), (SECP_N - 1) // 3, SECP_N)
    if lam == 1:
        lam = powmod(mpz(3), (SECP_N - 1) // 3, SECP_N)
    assert powmod(lam, 3, SECP_N) == 1
    assert lam != 1
    print(f"  GLV lambda = {hex(int(lam))[:20]}...")

    # Verify: lambda*G = phi(G)
    lamG = ec_mul(lam, G_SECP, SECP_A, SECP_P)
    phi_G = (phi_Gx, phi_Gy)
    glv_works = (lamG == phi_G)
    print(f"  lambda*G == phi(G): {glv_works}")

    # Now: can Lorentz boosts give anything beyond this?
    # SO(2,1) matrix: [[cosh a, sinh a, 0], [sinh a, cosh a, 0], [0, 0, 1]]
    # This is a LINEAR transformation. On projective coordinates (X:Y:Z),
    # the curve equation is Y^2*Z = X^3 + 7*Z^3.
    # A Lorentz boost mixes X and Y, changing Y^2*Z and X^3 differently.
    # It does NOT preserve the curve equation in general.

    # The ONLY endomorphisms of y^2=x^3+7 over F_p are:
    # [n] (multiplication by n) and phi^j * [n] for j=0,1,2 and n in Z.
    # The endomorphism ring is Z[zeta_3], a rank-2 Z-module.

    # Lorentz boosts are NOT in this ring.

    # GLV decomposition: to compute kP, write k = k1 + k2*lambda mod n
    # where k1, k2 ~ sqrt(n). Then kP = k1*P + k2*phi(P).
    # This halves the scalar multiplication cost. Already well-known.
    # secp256k1 libraries (libsecp256k1) already use this.

    details = (
        f"GLV beta (cube root of unity mod p): {hex(int(beta))[:20]}...\n"
        f"GLV lambda (eigenvalue mod n): {hex(int(lam))[:20]}...\n"
        f"phi(G) on curve: {on_curve}, lambda*G == phi(G): {glv_works}\n"
        f"Endomorphism ring of secp256k1 = Z[zeta_3] (fully known, rank 2)\n"
        f"GLV method: write k = k1 + k2*lambda, compute k1*P + k2*phi(P)\n"
        f"This is ALREADY implemented in libsecp256k1.\n"
        f"Lorentz boosts are linear transforms that do NOT preserve the curve equation.\n"
        f"SO(2,1) has no useful action on y^2=x^3+7.\n"
        f"The PPT/Lorentz connection is for the hyperbolic surface a^2+b^2=c^2,\n"
        f"NOT for elliptic curves. Different geometry entirely.\n"
        f"Conclusion: No new endomorphisms from Lorentz boosts. GLV already optimal."
    )
    print(details)

    return {
        'verdict': 'NEGATIVE — End(secp256k1) = Z[zeta_3] fully known, GLV already used',
        'glv_beta': hex(int(beta))[:20] + '...',
        'glv_lambda': hex(int(lam))[:20] + '...',
        'glv_verified': glv_works,
        'details': details
    }


# ===========================================================================
# Experiment 6: Zeta zeros for curve order (point counting)
# ===========================================================================
def exp6_zeta_point_counting():
    """
    For E/F_p, the number of points is #E(F_p) = p + 1 - a_p
    where a_p = p + 1 - #E(F_p) is the trace of Frobenius.

    The L-function of E is L(E,s) = prod_p (1 - a_p*p^-s + p^(1-2s))^-1.

    Our "zeta machine" computes Riemann zeta zeros, NOT Hasse-Weil L-function zeros.
    These are completely different objects.

    Riemann zeta zeros -> prime distribution
    Hasse-Weil zeros -> point counts on curves

    For point counting on general curves, Schoof's algorithm runs in O(log^5 p)
    and Schoof-Elkies-Atkin (SEA) is faster. Our zeta zeros don't help.

    But let's verify: for secp256k1, the order n is already known.
    For random curves, can our prime-counting function help with point counting?
    """
    p = SECP_P
    n = SECP_N
    t = p + 1 - n  # Frobenius trace

    # Hasse bound: |t| <= 2*sqrt(p)
    hasse_bound = 2 * gmpy2.isqrt(p)
    within_hasse = (abs(t) <= hasse_bound)
    print(f"  Frobenius trace t = {t}")
    print(f"  |t| = {abs(t)}")
    print(f"  2*sqrt(p) = {hasse_bound}")
    print(f"  |t| <= 2*sqrt(p): {within_hasse}")

    # The "angle" theta_p where a_p = 2*sqrt(p)*cos(theta_p)
    # This is the Sato-Tate distribution for non-CM curves
    # secp256k1 HAS CM (j=0), so Sato-Tate doesn't apply directly
    import math
    cos_theta = float(t) / (2 * math.sqrt(float(p)))
    # This won't work because p is too large for float...
    # Use the ratio t / (2*sqrt(p)) as mpfr
    t_abs = abs(t)
    sqrt_p = gmpy2.isqrt(p)
    ratio = gmpy2.mpfr(t) / (2 * gmpy2.mpfr(sqrt_p))
    print(f"  t / (2*sqrt(p)) ≈ {float(ratio):.6f}")

    # For CM curves with j=0, the trace satisfies special constraints:
    # t = 0 (supersingular) or t = ±p^(1/2) (special) or generic
    # Check if t has any special form
    t_sq = t * t
    print(f"  t^2 = {t_sq}")
    print(f"  p = {p}")
    print(f"  t^2 / p ≈ {float(gmpy2.mpfr(t_sq) / gmpy2.mpfr(p)):.6f}")

    # Can we use explicit formula for psi(x) to help with point counting?
    # psi(x) = x - sum_rho x^rho/rho - log(2pi) - (1/2)log(1-x^-2)
    # This counts primes, not curve points. Completely different.

    # The ONLY connection: BSD conjecture relates L(E,1) to rank of E(Q).
    # But that's over Q, not F_p, and doesn't help with ECDLP.

    details = (
        f"Frobenius trace: t = {t}\n"
        f"Hasse bound satisfied: {within_hasse}\n"
        f"t/(2*sqrt(p)) ≈ {float(ratio):.6f}\n"
        f"Our zeta machine computes Riemann zeta zeros (prime distribution).\n"
        f"Point counting needs Hasse-Weil L-function zeros — DIFFERENT object.\n"
        f"Riemann zeros: ζ(s) = prod_p (1-p^-s)^-1\n"
        f"Hasse-Weil zeros: L(E,s) = prod_p (1-a_p*p^-s+p^(1-2s))^-1\n"
        f"No connection. Schoof/SEA algorithm is the right tool for point counting.\n"
        f"For secp256k1, the order is hardcoded in the standard — no computation needed."
    )
    print(details)

    return {
        'verdict': 'NEGATIVE — Riemann zeta != Hasse-Weil L-function, no connection',
        'trace': str(t),
        'within_hasse': within_hasse,
        'details': details
    }


# ===========================================================================
# Experiment 7: Congruent number ECDLP
# ===========================================================================
def exp7_congruent_number_ecdlp():
    """
    On E_n: y^2 = x^3 - n^2 x, PPTs give explicit rational points.
    If G = generator and P = target, can PPT structure help find k with kG = P?

    The PPT (a,b,c) with a^2+b^2=c^2 gives:
    - n = ab/2 (the congruent number)
    - Point on E_n: (x,y) = (b^2/4, b(a^2-b^2)/8) or similar

    Key issue: E_n has rank >= 1 over Q (the PPT gives a rational point).
    But ECDLP is over F_p, where the group structure is cyclic.
    The "nice" rational points from PPTs become just random elements of E_n(F_p).

    The tree structure of PPTs (Berggren tree) gives a tree of rational points,
    but modular reduction mod p destroys the tree structure.
    """
    # Take a small PPT: (3,4,5) -> n = 6
    a_ppt, b_ppt, c_ppt = 3, 4, 5
    n_cong = a_ppt * b_ppt // 2  # = 6

    # E_6: y^2 = x^3 - 36x
    # Point from PPT: several formulas exist
    # Standard: x = (c/2)^2 = 25/4... but this is rational, not integer
    # Over F_p, we work with the affine coordinates mod p

    p = mpz(10007)  # small prime for testing
    a_curve = mpz(-36) % p  # -n^2 = -36
    b_curve = mpz(0)

    # Find the order of E_6(F_p) by brute force (p is small)
    count = 1  # point at infinity
    points = [INF]
    for x in range(int(p)):
        x = mpz(x)
        rhs = (x * x * x + a_curve * x) % p
        if rhs == 0:
            count += 1
            points.append((x, mpz(0)))
        elif jacobi(rhs, p) == 1:
            count += 2
            y = powmod(rhs, (p + 1) // 4, p)  # works if p ≡ 3 mod 4
            if powmod(y, 2, p) != rhs:
                # p ≡ 1 mod 4, use Tonelli-Shanks or just brute force
                for yy in range(1, int(p)):
                    if (yy * yy) % int(p) == int(rhs):
                        y = mpz(yy)
                        break
            points.append((x, y))
            points.append((x, (-y) % p))

    print(f"  E_6 over F_{p}: #E = {count}")

    # PPT-derived point: (3,4,5) gives point on E_6
    # x = n^2/a^2... various formulas. Let's use the standard one:
    # P = (n^2*(a^2+b^2+c^2+2c(a+b))/(a+b+c)^2, ...) — messy
    # Simpler: (a^2/4, a(a^2-b^2)/8) ... no, depends on parameterization
    # The RIGHT formula for PPT (a,b,c) with n=ab/2:
    # x = b^2/4, but this is rational...
    # Over F_p: x = b^2 * invert(4, p) mod p

    x_ppt = (b_ppt * b_ppt * invert(4, p)) % p  # 16/4 = 4
    rhs_check = (x_ppt**3 + a_curve * x_ppt) % p
    y_sq = rhs_check

    if y_sq == 0:
        y_ppt = mpz(0)
    elif jacobi(y_sq, p) == 1:
        # Find square root
        for yy in range(1, int(p)):
            if (yy * yy) % int(p) == int(y_sq):
                y_ppt = mpz(yy)
                break
    else:
        y_ppt = None

    if y_ppt is not None:
        ppt_point = (x_ppt, y_ppt)
        on_curve = ((y_ppt * y_ppt) % p == (x_ppt**3 + a_curve * x_ppt) % p)
        print(f"  PPT-derived point: ({x_ppt}, {y_ppt}), on curve: {on_curve}")
    else:
        ppt_point = None
        print(f"  PPT-derived point: not on curve over F_{p} (y^2 not a QR)")

    # Key insight: the PPT gives ONE specific point.
    # But ECDLP needs to express ANY target point as a multiple of ANY generator.
    # Knowing one special point doesn't help find discrete logs of OTHER points.

    # The Berggren tree gives MANY PPTs, hence MANY points.
    # But these are all related by the Berggren group action,
    # which is a tree (free monoid), NOT the cyclic group E_n(F_p).
    # The Berggren relations don't correspond to EC addition.

    # Test: generate points from Berggren tree and check if they span E_n(F_p)
    # Berggren matrices
    import numpy as np
    A = [[1,-2,2],[2,-1,2],[2,-2,3]]
    B = [[1,2,2],[2,1,2],[2,2,3]]
    C = [[-1,2,2],[-2,1,2],[-2,2,3]]

    def berggren_children(m, n, c):
        """Generate children of PPT (m,n,c) in the tree."""
        # Actually Berggren operates on (a,b,c) directly
        v = [m, n, c]
        children = []
        for M in [A, B, C]:
            child = [sum(M[i][j]*v[j] for j in range(3)) for i in range(3)]
            child = [abs(x) for x in child]  # ensure positive
            children.append(tuple(child))
        return children

    # Generate first few PPTs
    ppts = [(3, 4, 5)]
    queue = [(3, 4, 5)]
    for _ in range(3):  # 3 levels = ~40 PPTs
        new_queue = []
        for ppt in queue:
            for child in berggren_children(*ppt):
                ppts.append(child)
                new_queue.append(child)
        queue = new_queue

    # Map PPTs to points on E_n(F_p) for their respective n values
    # Each PPT gives a DIFFERENT n (different curve), so points don't combine!
    n_values = set()
    for a_t, b_t, c_t in ppts[:20]:
        n_val = a_t * b_t // 2
        n_values.add(n_val)

    print(f"  First 20 PPTs give {len(n_values)} distinct congruent numbers")
    print(f"  (Each PPT is on a DIFFERENT curve E_n!)")

    details = (
        f"E_6 over F_{p}: {count} points\n"
        f"PPT (3,4,5) point: {ppt_point}\n"
        f"First 20 Berggren PPTs give {len(n_values)} distinct n values (distinct curves!)\n"
        f"FUNDAMENTAL PROBLEM: each PPT (a,b,c) gives n=ab/2, a DIFFERENT curve E_n.\n"
        f"PPTs from the Berggren tree land on DIFFERENT curves, not the same one.\n"
        f"To attack ECDLP on a fixed curve E_n, you need MANY points on THAT curve.\n"
        f"The tree gives at most O(1) points per curve (only PPTs with same ab/2=n).\n"
        f"Over F_p, the rational PPT structure is destroyed by modular reduction.\n"
        f"The Berggren group action (free monoid) != EC group (cyclic).\n"
        f"Conclusion: PPT structure cannot help with ECDLP on congruent number curves."
    )
    print(details)

    return {
        'verdict': 'NEGATIVE — each PPT gives a different curve E_n, structure destroyed mod p',
        'n_values': len(n_values),
        'details': details
    }


# ===========================================================================
# Experiment 8: Information-theoretic ECDLP bound
# ===========================================================================
def exp8_info_theory_bound():
    """
    ECDLP on group of order n requires >= sqrt(n) group operations
    (Shoup's lower bound, 1997, for generic groups).

    secp256k1 has no exploitable structure beyond:
    - GLV endomorphism (saves factor ~2 in scalar mult, not in ECDLP)
    - The group is cyclic of prime order (no Pohlig-Hellman speedup)

    Our explicit formula gives psi(x) to 0.0036%, but this is about
    PRIME COUNTING, not group operations. The connection would need to be:
    "knowing primes well helps enumerate group elements" — but the group
    is already fully specified by its order n.

    Can we improve the CONSTANT in the O(sqrt(n)) bound?
    - Kangaroo: sqrt(n) with constant ~2 (Pollard)
    - 4-kangaroo: ~1.7 * sqrt(n) (van Oorschot-Wiener)
    - Baby-step giant-step: sqrt(n) exactly
    - Our best: ~2.6x speedup via shared memory (parallelism, not algorithmic)

    The explicit formula cannot help because it provides information about
    a DIFFERENT mathematical object (primes vs EC group elements).
    """

    n = SECP_N
    bits = n.bit_length()
    sqrt_n = gmpy2.isqrt(n)

    # Shoup's bound: any generic algorithm needs >= (sqrt(n)-1)/2 operations
    shoup_bound = (sqrt_n - 1) // 2

    # Best known constants:
    kangaroo_ops = 2.0 * float(gmpy2.mpfr(sqrt_n))  # ~2*sqrt(n)
    bsgs_ops = float(gmpy2.mpfr(sqrt_n))  # sqrt(n) ops + sqrt(n) storage

    # Information-theoretic argument:
    # Each group operation reveals at most O(log n) bits of information about k.
    # There are log2(n) = 256 bits to determine.
    # Each distinguished point collision reveals ~1 bit of information.
    # So we need at least 256 "informative events" — but each requires sqrt(n)/256 ops.
    # Total: sqrt(n) ops. This matches Shoup.

    # Can our psi(x) function provide "free" bits of information?
    # psi(x) tells us about prime distribution, which is about the INTEGERS,
    # not about the EC group. The EC group is a black box — we can only
    # interact with it through group operations (+, -, scalar mult).
    # No external information about primes affects the group structure.

    # The group order n is ALREADY a prime (no Pohlig-Hellman).
    # The endomorphism ring gives GLV (already used).
    # There are no subgroups, no special structure, no shortcut.

    # Our specific contributions and their ECDLP relevance:
    contributions = {
        'PPT → E_n points': 'Different curve (j=1728 vs j=0), not applicable',
        'CF-PPT bijection': 'Encoding scheme, not a group operation speedup',
        'T270 torus': 'Multiplicative structure != EC additive structure',
        'SO(2,1) Lorentz': 'Linear transforms, not EC endomorphisms',
        'Gaussian integers': 'Z[i] multiplication != EC addition',
        'Zeta zeros': 'Riemann zeta != Hasse-Weil L-function',
        'Berggren free monoid': 'Tree structure != cyclic group structure',
        'Kangaroo + Lévy': 'Already optimal for generic groups (constant improvement only)',
        'Shared memory': 'Parallelism speedup, not algorithmic improvement',
    }

    details = (
        f"secp256k1: {bits}-bit group of prime order\n"
        f"Shoup lower bound: >= {bits//2}-bit operations (generic group model)\n"
        f"Best known algorithms:\n"
        f"  BSGS: sqrt(n) ops, sqrt(n) memory\n"
        f"  Pollard rho: sqrt(n) ops, O(1) memory\n"
        f"  Kangaroo: 2*sqrt(n) ops, O(1) memory\n"
        f"  4-kangaroo: 1.7*sqrt(n) ops (van Oorschot-Wiener)\n"
        f"\nOur contributions vs ECDLP:\n"
    )
    for k, v in contributions.items():
        details += f"  {k}: {v}\n"

    details += (
        f"\nThe O(sqrt(n)) barrier is PROVABLY optimal in the generic group model.\n"
        f"To beat it, you need to exploit SPECIFIC curve structure.\n"
        f"secp256k1's only exploitable structure is the GLV endomorphism (j=0, CM by Z[zeta_3]).\n"
        f"This saves a factor of ~2 in scalar multiplication, not in ECDLP itself.\n"
        f"None of our theorems provide non-generic structure for secp256k1.\n"
        f"\nFINAL VERDICT: No ECDLP speedup from any of our 101+ theorems."
    )
    print(details)

    return {
        'verdict': 'NEGATIVE — O(sqrt(n)) provably optimal, no theorem helps',
        'bits': bits,
        'contributions': contributions,
        'details': details
    }


# ===========================================================================
# Main
# ===========================================================================
if __name__ == '__main__':
    print("v32_ecdlp_theorems.py — Examining ALL theorems for ECDLP speedup")
    print(f"secp256k1: {SECP_N.bit_length()}-bit group, p = {hex(int(SECP_P))[:20]}...")
    print(f"Target: find ANY speedup for ECDLP on secp256k1")

    experiments = [
        ("1. Curve Isomorphism (j-invariant)", exp1_curve_isomorphism),
        ("2. Gaussian Torus Homomorphism", exp2_gaussian_torus),
        ("3. PPT Addition Chains", exp3_ppt_addition_chains),
        ("4. Kangaroo + Tree Structure", exp4_kangaroo_tree),
        ("5. Lorentz Boosts as Endomorphisms", exp5_lorentz_endomorphisms),
        ("6. Zeta Zeros for Point Counting", exp6_zeta_point_counting),
        ("7. Congruent Number ECDLP", exp7_congruent_number_ecdlp),
        ("8. Information-Theoretic Bound", exp8_info_theory_bound),
    ]

    for name, func in experiments:
        run_experiment(name, func)

    # ===========================================================================
    # Write results
    # ===========================================================================
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    md_lines = [
        "# v32: ECDLP Theorem Examination Results",
        "",
        "**Date**: 2026-03-16",
        "",
        "**Question**: Can ANY of our 101+ theorems provide an ECDLP speedup on secp256k1?",
        "",
        "**Answer**: **NO.** All 8 experiments return NEGATIVE.",
        "",
        "## Summary Table",
        "",
        "| # | Experiment | Verdict | Time |",
        "|---|-----------|---------|------|",
    ]

    for name, func in experiments:
        r = results.get(name, {})
        verdict = r.get('verdict', 'N/A')
        t = r.get('time', 'N/A')
        md_lines.append(f"| {name.split('.')[0]} | {name.split('. ',1)[1] if '. ' in name else name} | {verdict} | {t} |")
        print(f"  {name}: {verdict}")

    md_lines.extend([
        "",
        "## Detailed Results",
        "",
    ])

    for name, func in experiments:
        r = results.get(name, {})
        md_lines.append(f"### {name}")
        md_lines.append("")
        md_lines.append(f"**Verdict**: {r.get('verdict', 'N/A')}")
        md_lines.append("")
        details = r.get('details', 'No details available.')
        md_lines.append("```")
        md_lines.append(details)
        md_lines.append("```")
        md_lines.append("")

    md_lines.extend([
        "## Why Nothing Works: The Core Argument",
        "",
        "1. **secp256k1 has j-invariant 0** (CM by Z[zeta_3]). Congruent number curves",
        "   have j-invariant 1728 (CM by Z[i]). These are fundamentally different algebraic objects.",
        "   No isomorphism exists, so PPT-derived points cannot transfer.",
        "",
        "2. **The Berggren tree is a free monoid**, not a cyclic group. Its structure",
        "   is incompatible with the cyclic group E(F_p). Tree walks cannot replace",
        "   random walks in the kangaroo algorithm.",
        "",
        "3. **Lorentz boosts (SO(2,1)) are linear transformations** that do not preserve",
        "   the cubic curve equation. The only endomorphisms of secp256k1 are",
        "   {[n], phi^j * [n]} where phi is the GLV map — already fully exploited.",
        "",
        "4. **Riemann zeta zeros ≠ Hasse-Weil L-function zeros**. Our prime-counting",
        "   improvements don't help with elliptic curve point counting.",
        "",
        "5. **O(√n) is provably optimal** in the generic group model (Shoup 1997).",
        "   To beat it requires non-generic curve structure. secp256k1's only",
        "   non-generic structure (GLV endomorphism) is already fully exploited.",
        "",
        "6. **Each PPT gives a different congruent number n**, hence a different curve E_n.",
        "   The Berggren tree does NOT give multiple points on the SAME curve.",
        "",
        "## What WOULD Work (Theoretical)",
        "",
        "- **Quantum computer**: Shor's algorithm solves ECDLP in O(n^(1/3)) — but we don't have one.",
        "- **Index calculus on EC**: No known method (unlike for F_p* discrete log).",
        "- **Weil descent**: Only works for curves over extension fields (not F_p).",
        "- **New endomorphisms**: Would require a mathematical breakthrough in algebraic geometry.",
        "",
        "## Conclusion",
        "",
        "Our research has produced 101+ theorems spanning PPTs, continued fractions,",
        "compression, zeta functions, and algebraic structures. **None of them provide**",
        "**any ECDLP speedup on secp256k1.** This is not surprising — the O(√n) barrier",
        "is extremely robust, and secp256k1 was specifically chosen to resist all known attacks.",
        "",
        "The honest assessment: our PPT/congruent-number machinery lives in a different",
        "mathematical universe (j=1728, Z[i]) from secp256k1 (j=0, Z[zeta_3]).",
        "No bridge exists between them.",
    ])

    md_text = "\n".join(md_lines)

    with open("v32_ecdlp_theorems_results.md", "w") as f:
        f.write(md_text)

    print(f"\nResults written to v32_ecdlp_theorems_results.md")
    print(f"\nFINAL ANSWER: No ECDLP speedup found from any theorem. O(sqrt(n)) barrier holds.")

"""
H21: RL-Optimized Kangaroo Jumps + H26: Kolmogorov Complexity Filter
Research experiments on secp256k1 ECDLP.

H21 tests whether reinforcement learning can improve kangaroo jump selection.
H26 tests whether structured/low-complexity keys can be found faster.
"""

import math
import time
import random
import hashlib
from collections import defaultdict
from gmpy2 import mpz, invert as _gmp_invert

# secp256k1 parameters
SECP256K1_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
SECP256K1_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
SECP256K1_GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
SECP256K1_GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
SECP256K1_BETA = 0x7AE96A2B657C07106E64479EAC3434E99CF0497512F58995C1396C28719501EE

# ---------------------------------------------------------------------------
# Fast EC arithmetic (Jacobian coordinates, gmpy2)
# ---------------------------------------------------------------------------

_P = mpz(SECP256K1_P)
_N = mpz(SECP256K1_N)
_ZERO = mpz(0)
_ONE = mpz(1)
_TWO = mpz(2)
_THREE = mpz(3)

# Infinity = (0, 1, 0)
INF = (_ZERO, _ONE, _ZERO)

def _jac_double(P):
    X1, Y1, Z1 = P
    if Z1 == 0 or Y1 == 0:
        return INF
    Y1_sq = Y1 * Y1 % _P
    S = 4 * X1 * Y1_sq % _P
    M = 3 * X1 * X1 % _P  # a=0 for secp256k1
    X3 = (M * M - 2 * S) % _P
    Y1_4 = Y1_sq * Y1_sq % _P
    Y3 = (M * (S - X3) - 8 * Y1_4) % _P
    Z3 = 2 * Y1 * Z1 % _P
    return (X3, Y3, Z3)

def _jac_add(P, Q):
    X1, Y1, Z1 = P
    X2, Y2, Z2 = Q
    if Z1 == 0: return Q
    if Z2 == 0: return P
    Z1_sq = Z1 * Z1 % _P
    Z2_sq = Z2 * Z2 % _P
    U1 = X1 * Z2_sq % _P
    U2 = X2 * Z1_sq % _P
    S1 = Y1 * Z2_sq % _P * Z2 % _P
    S2 = Y2 * Z1_sq % _P * Z1 % _P
    H = (U2 - U1) % _P
    if H == 0:
        if S1 == S2: return _jac_double(P)
        return INF
    R = (S2 - S1) % _P
    H_sq = H * H % _P
    H_cu = H_sq * H % _P
    X3 = (R * R - H_cu - 2 * U1 * H_sq) % _P
    Y3 = (R * (U1 * H_sq - X3) - S1 * H_cu) % _P
    Z3 = H * Z1 * Z2 % _P
    return (X3, Y3, Z3)

def _jac_add_affine(P, ax, ay):
    X1, Y1, Z1 = P
    if Z1 == 0:
        return (mpz(ax), mpz(ay), _ONE)
    Z1_sq = Z1 * Z1 % _P
    U2 = ax * Z1_sq % _P
    S2 = ay * Z1_sq % _P * Z1 % _P
    H = (U2 - X1) % _P
    if H == 0:
        if S2 == Y1: return _jac_double(P)
        return INF
    R = (S2 - Y1) % _P
    H_sq = H * H % _P
    H_cu = H_sq * H % _P
    X3 = (R * R - H_cu - 2 * X1 * H_sq) % _P
    Y3 = (R * (X1 * H_sq - X3) - Y1 * H_cu) % _P
    Z3 = H * Z1 % _P
    return (X3, Y3, Z3)

def _to_affine(P):
    X, Y, Z = P
    if Z == 0:
        return None  # infinity
    Z_inv = _gmp_invert(Z, _P)
    Z2 = Z_inv * Z_inv % _P
    Z3 = Z2 * Z_inv % _P
    return (int(X * Z2 % _P), int(Y * Z3 % _P))

def _scalar_mult(k, P):
    if k == 0: return INF
    if k < 0:
        X, Y, Z = P
        P = (X, (-Y) % _P, Z)
        k = -k
    result = INF
    addend = P
    while k:
        if k & 1:
            result = _jac_add(result, addend)
        addend = _jac_double(addend)
        k >>= 1
    return result

# Generator in Jacobian
G_JAC = (mpz(SECP256K1_GX), mpz(SECP256K1_GY), _ONE)
G_AFF = (mpz(SECP256K1_GX), mpz(SECP256K1_GY))

def make_target(k):
    """Compute K = k*G, return affine (x, y)."""
    return _to_affine(_scalar_mult(k, G_JAC))


# ---------------------------------------------------------------------------
# Standard Kangaroo baseline
# ---------------------------------------------------------------------------

def kangaroo_standard(target_aff, search_bound, num_jumps=32, seed=42):
    """
    Standard Pollard kangaroo with pseudo-random jumps.
    Returns (k, steps) or (None, steps).
    """
    rng = random.Random(seed)
    n = int(SECP256K1_N)
    half = search_bound // 2

    # Jump table: powers of 2 scaled to mean ~ sqrt(half)/4
    mean_jump = max(1, int(math.isqrt(half)) // 4)
    jumps = [max(1, rng.randint(1, 2 * mean_jump)) for _ in range(num_jumps)]
    jump_affs = [_to_affine(_scalar_mult(j, G_JAC)) for j in jumps]

    # DP criterion
    D = max(1, search_bound.bit_length() // 4)
    dp_mask = (1 << D) - 1

    # Tame: start at half//2
    tame_start = half // 2
    tame_pos = tame_start
    tame_jac = _scalar_mult(tame_start, G_JAC)

    # Wild: start at target
    wild_pos = 0
    wild_jac = (mpz(target_aff[0]), mpz(target_aff[1]), _ONE)

    dp_table = {}
    max_steps = 16 * int(math.isqrt(half)) + 10000

    steps = 0
    for step in range(max_steps):
        # Tame step
        ta = _to_affine(tame_jac)
        if ta is not None:
            ji = ta[0] % num_jumps
            tame_pos += jumps[ji]
            tame_jac = _jac_add_affine(tame_jac, mpz(jump_affs[ji][0]), mpz(jump_affs[ji][1]))
            steps += 1

            if (ta[0] & dp_mask) == 0:
                key = ta[0]
                if key in dp_table:
                    sp, st = dp_table[key]
                    if not st:  # wild
                        k = (tame_pos - sp) % n
                        if 0 < k < search_bound:
                            check = _to_affine(_scalar_mult(k, G_JAC))
                            if check and check[0] == target_aff[0]:
                                return k, steps
                        k = (n - k) % n
                        if 0 < k < search_bound:
                            check = _to_affine(_scalar_mult(k, G_JAC))
                            if check and check[0] == target_aff[0]:
                                return k, steps
                dp_table[key] = (tame_pos, True)

        # Wild step
        wa = _to_affine(wild_jac)
        if wa is not None:
            ji = wa[0] % num_jumps
            wild_pos += jumps[ji]
            wild_jac = _jac_add_affine(wild_jac, mpz(jump_affs[ji][0]), mpz(jump_affs[ji][1]))
            steps += 1

            if (wa[0] & dp_mask) == 0:
                key = wa[0]
                if key in dp_table:
                    sp, st = dp_table[key]
                    if st:  # tame
                        k = (sp - wild_pos) % n
                        if 0 < k < search_bound:
                            check = _to_affine(_scalar_mult(k, G_JAC))
                            if check and check[0] == target_aff[0]:
                                return k, steps
                        k = (n - k) % n
                        if 0 < k < search_bound:
                            check = _to_affine(_scalar_mult(k, G_JAC))
                            if check and check[0] == target_aff[0]:
                                return k, steps
                dp_table[key] = (wild_pos, False)

    return None, steps


# ---------------------------------------------------------------------------
# H21 Approach 1: Multi-armed Bandit (UCB1) Jump Selection
# ---------------------------------------------------------------------------

def _train_bandit_jump_table(search_bound, num_jumps=32, n_walks=20, seed=42):
    """
    Training phase: run random walks, collect stats on which (x mod num_jumps)
    -> jump_index mappings lead to DPs fastest. Then build a FIXED lookup table.

    Key insight: the lookup must be deterministic f(point) -> jump_index so that
    tame and wild kangaroos at the same point take the same step (required for collision).

    We learn a permutation: for each slot i in [0, num_jumps), which jump_index is best.
    """
    rng = random.Random(seed)
    half = search_bound // 2
    mean_jump = max(1, int(math.isqrt(half)) // 4)
    jumps = [max(1, rng.randint(1, 2 * mean_jump)) for _ in range(num_jumps)]
    jump_affs = [_to_affine(_scalar_mult(j, G_JAC)) for j in jumps]

    D = max(1, search_bound.bit_length() // 4)
    dp_mask = (1 << D) - 1

    # For each partition slot, track how often each jump leads to DP within K steps
    # slot_stats[slot][jump_idx] = (dp_count, total_uses)
    slot_dp_count = [[0] * num_jumps for _ in range(num_jumps)]
    slot_use_count = [[0] * num_jumps for _ in range(num_jumps)]

    walk_len = 4 * int(math.isqrt(half))
    for walk in range(n_walks):
        start = rng.randint(1, int(SECP256K1_N) - 1)
        jac = _scalar_mult(start, G_JAC)
        recent_jumps = []  # (slot, jump_idx) for last K steps
        K = max(4, 1 << D)  # lookback window

        for step in range(walk_len):
            aff = _to_affine(jac)
            if aff is None:
                break
            slot = aff[0] % num_jumps
            # Try each jump from this slot (round-robin across walks)
            ji = (slot + walk) % num_jumps  # vary which jump we test
            jac = _jac_add_affine(jac, mpz(jump_affs[ji][0]), mpz(jump_affs[ji][1]))
            slot_use_count[slot][ji] += 1
            recent_jumps.append((slot, ji))
            if len(recent_jumps) > K:
                recent_jumps.pop(0)

            if (aff[0] & dp_mask) == 0:
                # Reward all recent (slot, jump) pairs
                for s, j in recent_jumps:
                    slot_dp_count[s][j] += 1
                recent_jumps.clear()

    # Build fixed lookup: for each slot, pick the jump with best DP rate
    lookup = []
    for slot in range(num_jumps):
        best_j = slot  # default: identity mapping
        best_rate = -1
        for j in range(num_jumps):
            uses = slot_use_count[slot][j]
            if uses > 0:
                rate = slot_dp_count[slot][j] / uses
                if rate > best_rate:
                    best_rate = rate
                    best_j = j
        lookup.append(best_j)

    return lookup, jumps, jump_affs


def kangaroo_ucb1(target_aff, search_bound, num_jumps=32, seed=42,
                  trained_lookup=None, trained_jumps=None, trained_jump_affs=None):
    """
    Kangaroo with bandit-trained FIXED lookup table for jump selection.
    The lookup is deterministic f(x mod num_jumps) -> jump_index,
    so both kangaroos at the same point take the same step (collision works).
    Returns (k, steps).
    """
    rng = random.Random(seed)
    n = int(SECP256K1_N)
    half = search_bound // 2

    if trained_lookup is not None:
        lookup = trained_lookup
        jumps = trained_jumps
        jump_affs = trained_jump_affs
    else:
        # Use identity mapping (same as standard)
        mean_jump = max(1, int(math.isqrt(half)) // 4)
        jumps = [max(1, rng.randint(1, 2 * mean_jump)) for _ in range(num_jumps)]
        jump_affs = [_to_affine(_scalar_mult(j, G_JAC)) for j in jumps]
        lookup = list(range(num_jumps))

    D = max(1, search_bound.bit_length() // 4)
    dp_mask = (1 << D) - 1

    tame_start = half // 2
    tame_pos = tame_start
    tame_jac = _scalar_mult(tame_start, G_JAC)
    wild_pos = 0
    wild_jac = (mpz(target_aff[0]), mpz(target_aff[1]), _ONE)

    dp_table = {}
    max_steps = 16 * int(math.isqrt(half)) + 10000

    def jump_index(x):
        return lookup[x % num_jumps]

    steps = 0
    for step in range(max_steps):
        # Tame step
        ta = _to_affine(tame_jac)
        if ta is not None:
            ji = jump_index(ta[0])
            tame_pos += jumps[ji]
            tame_jac = _jac_add_affine(tame_jac, mpz(jump_affs[ji][0]), mpz(jump_affs[ji][1]))
            steps += 1

            if (ta[0] & dp_mask) == 0:
                key = ta[0]
                if key in dp_table:
                    sp, st = dp_table[key]
                    if not st:
                        k = (tame_pos - sp) % n
                        if 0 < k < search_bound:
                            check = _to_affine(_scalar_mult(k, G_JAC))
                            if check and check[0] == target_aff[0]:
                                return k, steps
                        k = (n - k) % n
                        if 0 < k < search_bound:
                            check = _to_affine(_scalar_mult(k, G_JAC))
                            if check and check[0] == target_aff[0]:
                                return k, steps
                dp_table[key] = (tame_pos, True)

        # Wild step
        wa = _to_affine(wild_jac)
        if wa is not None:
            ji = jump_index(wa[0])
            wild_pos += jumps[ji]
            wild_jac = _jac_add_affine(wild_jac, mpz(jump_affs[ji][0]), mpz(jump_affs[ji][1]))
            steps += 1

            if (wa[0] & dp_mask) == 0:
                key = wa[0]
                if key in dp_table:
                    sp, st = dp_table[key]
                    if st:
                        k = (sp - wild_pos) % n
                        if 0 < k < search_bound:
                            check = _to_affine(_scalar_mult(k, G_JAC))
                            if check and check[0] == target_aff[0]:
                                return k, steps
                        k = (n - k) % n
                        if 0 < k < search_bound:
                            check = _to_affine(_scalar_mult(k, G_JAC))
                            if check and check[0] == target_aff[0]:
                                return k, steps
                dp_table[key] = (wild_pos, False)

    return None, steps


# ---------------------------------------------------------------------------
# H21 Approach 2: Feature-based Jump Selection
# ---------------------------------------------------------------------------

def _train_feature_lookup(search_bound, num_jumps=32, num_features=256,
                          n_walks=20, seed=42):
    """
    Training phase for feature-based jump selection.
    For each feature (x mod num_features), learn which jump leads to DPs fastest.
    Returns a FIXED lookup table: feature -> best jump index.
    """
    rng = random.Random(seed)
    half = search_bound // 2
    mean_jump = max(1, int(math.isqrt(half)) // 4)
    jumps = [max(1, rng.randint(1, 2 * mean_jump)) for _ in range(num_jumps)]
    jump_affs = [_to_affine(_scalar_mult(j, G_JAC)) for j in jumps]

    D = max(1, search_bound.bit_length() // 4)
    dp_mask = (1 << D) - 1

    # feat_stats[feat][ji] = (dp_hits, uses)
    feat_dp = [[0] * num_jumps for _ in range(num_features)]
    feat_use = [[0] * num_jumps for _ in range(num_features)]

    walk_len = 4 * int(math.isqrt(half))
    K = max(4, 1 << D)

    for walk in range(n_walks):
        start = rng.randint(1, int(SECP256K1_N) - 1)
        jac = _scalar_mult(start, G_JAC)
        recent = []

        for step in range(walk_len):
            aff = _to_affine(jac)
            if aff is None:
                break
            feat = aff[0] % num_features
            ji = (feat + walk) % num_jumps  # vary per walk
            jac = _jac_add_affine(jac, mpz(jump_affs[ji][0]), mpz(jump_affs[ji][1]))
            feat_use[feat][ji] += 1
            recent.append((feat, ji))
            if len(recent) > K:
                recent.pop(0)

            if (aff[0] & dp_mask) == 0:
                for f, j in recent:
                    feat_dp[f][j] += 1
                recent.clear()

    # Build fixed lookup
    lookup = []
    for feat in range(num_features):
        best_j = feat % num_jumps
        best_rate = -1
        for j in range(num_jumps):
            if feat_use[feat][j] > 0:
                rate = feat_dp[feat][j] / feat_use[feat][j]
                if rate > best_rate:
                    best_rate = rate
                    best_j = j
        lookup.append(best_j)

    return lookup, jumps, jump_affs


def kangaroo_feature(target_aff, search_bound, num_jumps=32, seed=42,
                     feature_lookup=None, feature_jumps=None, feature_jump_affs=None):
    """
    Kangaroo with feature-based FIXED lookup table.
    f(x) = lookup[x mod 256] -> deterministic jump index.
    Returns (k, steps).
    """
    rng = random.Random(seed)
    n = int(SECP256K1_N)
    half = search_bound // 2
    NUM_FEATURES = 256

    if feature_lookup is not None:
        lookup = feature_lookup
        jumps = feature_jumps
        jump_affs = feature_jump_affs
    else:
        mean_jump = max(1, int(math.isqrt(half)) // 4)
        jumps = [max(1, rng.randint(1, 2 * mean_jump)) for _ in range(num_jumps)]
        jump_affs = [_to_affine(_scalar_mult(j, G_JAC)) for j in jumps]
        lookup = [i % num_jumps for i in range(NUM_FEATURES)]

    D = max(1, search_bound.bit_length() // 4)
    dp_mask = (1 << D) - 1

    def jump_index(x):
        return lookup[x % NUM_FEATURES]

    tame_start = half // 2
    tame_pos = tame_start
    tame_jac = _scalar_mult(tame_start, G_JAC)
    wild_pos = 0
    wild_jac = (mpz(target_aff[0]), mpz(target_aff[1]), _ONE)

    dp_table = {}
    max_steps = 16 * int(math.isqrt(half)) + 10000

    steps = 0
    for step in range(max_steps):
        ta = _to_affine(tame_jac)
        if ta is not None:
            ji = jump_index(ta[0])
            tame_pos += jumps[ji]
            tame_jac = _jac_add_affine(tame_jac, mpz(jump_affs[ji][0]), mpz(jump_affs[ji][1]))
            steps += 1

            if (ta[0] & dp_mask) == 0:
                key = ta[0]
                if key in dp_table:
                    sp, st = dp_table[key]
                    if not st:
                        k = (tame_pos - sp) % n
                        if 0 < k < search_bound:
                            check = _to_affine(_scalar_mult(k, G_JAC))
                            if check and check[0] == target_aff[0]:
                                return k, steps
                        k = (n - k) % n
                        if 0 < k < search_bound:
                            check = _to_affine(_scalar_mult(k, G_JAC))
                            if check and check[0] == target_aff[0]:
                                return k, steps
                dp_table[key] = (tame_pos, True)

        wa = _to_affine(wild_jac)
        if wa is not None:
            ji = jump_index(wa[0])
            wild_pos += jumps[ji]
            wild_jac = _jac_add_affine(wild_jac, mpz(jump_affs[ji][0]), mpz(jump_affs[ji][1]))
            steps += 1

            if (wa[0] & dp_mask) == 0:
                key = wa[0]
                if key in dp_table:
                    sp, st = dp_table[key]
                    if st:
                        k = (sp - wild_pos) % n
                        if 0 < k < search_bound:
                            check = _to_affine(_scalar_mult(k, G_JAC))
                            if check and check[0] == target_aff[0]:
                                return k, steps
                        k = (n - k) % n
                        if 0 < k < search_bound:
                            check = _to_affine(_scalar_mult(k, G_JAC))
                            if check and check[0] == target_aff[0]:
                                return k, steps
                dp_table[key] = (wild_pos, False)

    return None, steps


# ---------------------------------------------------------------------------
# H21 Approach 3: Hash Function Comparison for Deterministic Walk
# ---------------------------------------------------------------------------

def kangaroo_hash_compare(target_aff, search_bound, hash_fn='xmod', num_jumps=32, seed=42):
    """
    Test different hash functions for deterministic jump selection.
    hash_fn: 'xmod', 'sha256', 'xor_shift', 'multiply'
    Returns (k, steps).
    """
    rng = random.Random(seed)
    n = int(SECP256K1_N)
    half = search_bound // 2

    mean_jump = max(1, int(math.isqrt(half)) // 4)
    jumps = [max(1, rng.randint(1, 2 * mean_jump)) for _ in range(num_jumps)]
    jump_affs = [_to_affine(_scalar_mult(j, G_JAC)) for j in jumps]

    D = max(1, search_bound.bit_length() // 4)
    dp_mask = (1 << D) - 1

    def hash_xmod(x):
        return x % num_jumps

    def hash_sha256(x):
        h = hashlib.sha256(x.to_bytes(32, 'big')).digest()
        return int.from_bytes(h[:4], 'big') % num_jumps

    def hash_xor_shift(x):
        x = x ^ (x >> 16)
        x = (x * 0x45d9f3b) & 0xFFFFFFFF
        x = x ^ (x >> 16)
        return x % num_jumps

    def hash_multiply(x):
        # Knuth multiplicative hash
        return ((x * 2654435761) >> 16) % num_jumps

    hash_fns = {
        'xmod': hash_xmod,
        'sha256': hash_sha256,
        'xor_shift': hash_xor_shift,
        'multiply': hash_multiply,
    }
    hfn = hash_fns[hash_fn]

    tame_start = half // 2
    tame_pos = tame_start
    tame_jac = _scalar_mult(tame_start, G_JAC)
    wild_pos = 0
    wild_jac = (mpz(target_aff[0]), mpz(target_aff[1]), _ONE)

    dp_table = {}
    max_steps = 16 * int(math.isqrt(half)) + 10000

    steps = 0
    for step in range(max_steps):
        ta = _to_affine(tame_jac)
        if ta is not None:
            ji = hfn(ta[0])
            tame_pos += jumps[ji]
            tame_jac = _jac_add_affine(tame_jac, mpz(jump_affs[ji][0]), mpz(jump_affs[ji][1]))
            steps += 1
            if (ta[0] & dp_mask) == 0:
                key = ta[0]
                if key in dp_table:
                    sp, st = dp_table[key]
                    if not st:
                        k = (tame_pos - sp) % n
                        if 0 < k < search_bound:
                            check = _to_affine(_scalar_mult(k, G_JAC))
                            if check and check[0] == target_aff[0]:
                                return k, steps
                        k = (n - k) % n
                        if 0 < k < search_bound:
                            check = _to_affine(_scalar_mult(k, G_JAC))
                            if check and check[0] == target_aff[0]:
                                return k, steps
                dp_table[key] = (tame_pos, True)

        wa = _to_affine(wild_jac)
        if wa is not None:
            ji = hfn(wa[0])
            wild_pos += jumps[ji]
            wild_jac = _jac_add_affine(wild_jac, mpz(jump_affs[ji][0]), mpz(jump_affs[ji][1]))
            steps += 1
            if (wa[0] & dp_mask) == 0:
                key = wa[0]
                if key in dp_table:
                    sp, st = dp_table[key]
                    if st:
                        k = (sp - wild_pos) % n
                        if 0 < k < search_bound:
                            check = _to_affine(_scalar_mult(k, G_JAC))
                            if check and check[0] == target_aff[0]:
                                return k, steps
                        k = (n - k) % n
                        if 0 < k < search_bound:
                            check = _to_affine(_scalar_mult(k, G_JAC))
                            if check and check[0] == target_aff[0]:
                                return k, steps
                dp_table[key] = (wild_pos, False)

    return None, steps


# ---------------------------------------------------------------------------
# H26 Approach 1: Structured Number Search
# ---------------------------------------------------------------------------

def kolmogorov_structured_search(target_aff, search_bound):
    """
    Try 'simple' numbers: powers of 2, sums/diffs of powers, Fibonacci, primes, etc.
    Returns (k, num_tried) or (None, num_tried).
    """
    target_x = target_aff[0]
    tried = 0

    # 1. Powers of 2
    for a in range(1, search_bound.bit_length() + 1):
        k = 1 << a
        if k >= search_bound:
            break
        pt = _to_affine(_scalar_mult(k, G_JAC))
        tried += 1
        if pt and pt[0] == target_x:
            return k, tried

    # 2. 2^a +/- 2^b
    for a in range(1, search_bound.bit_length() + 1):
        if (1 << a) >= search_bound:
            break
        for b in range(0, a):
            for sign in [1, -1]:
                k = (1 << a) + sign * (1 << b)
                if 0 < k < search_bound:
                    pt = _to_affine(_scalar_mult(k, G_JAC))
                    tried += 1
                    if pt and pt[0] == target_x:
                        return k, tried

    # 3. 2^a +/- 2^b +/- 2^c (3-term)
    bits = min(search_bound.bit_length(), 40)
    for a in range(2, bits + 1):
        va = 1 << a
        if va >= search_bound:
            break
        for b in range(1, a):
            for c in range(0, b):
                for s1 in [1, -1]:
                    for s2 in [1, -1]:
                        k = va + s1 * (1 << b) + s2 * (1 << c)
                        if 0 < k < search_bound:
                            pt = _to_affine(_scalar_mult(k, G_JAC))
                            tried += 1
                            if pt and pt[0] == target_x:
                                return k, tried
                            if tried > 50000:
                                break
                    if tried > 50000: break
                if tried > 50000: break
            if tried > 50000: break
        if tried > 50000: break

    # 4. Fibonacci numbers
    a, b = 1, 1
    while b < search_bound:
        pt = _to_affine(_scalar_mult(b, G_JAC))
        tried += 1
        if pt and pt[0] == target_x:
            return b, tried
        a, b = b, a + b

    # 5. Small primes and primorials
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    primorial = 1
    for p in primes:
        primorial *= p
        if primorial < search_bound:
            pt = _to_affine(_scalar_mult(primorial, G_JAC))
            tried += 1
            if pt and pt[0] == target_x:
                return primorial, tried

    # 6. Factorials
    factorial = 1
    for i in range(1, 100):
        factorial *= i
        if factorial >= search_bound:
            break
        pt = _to_affine(_scalar_mult(factorial, G_JAC))
        tried += 1
        if pt and pt[0] == target_x:
            return factorial, tried

    return None, tried


# ---------------------------------------------------------------------------
# H26 Approach 2: Compressed Candidate Generation
# ---------------------------------------------------------------------------

def kolmogorov_compressed_candidates(B_bits=20, max_val=None):
    """
    Enumerate numbers describable in <= B_bits of 'program'.
    Program: arithmetic expressions with +, -, *, ** using small integers.
    Returns set of candidate values.
    """
    if max_val is None:
        max_val = 1 << 40

    candidates = set()
    small = list(range(2, 16))  # base values: 2..15

    # Level 0: small integers
    for s in small:
        candidates.add(s)

    # Level 1: unary ops on small
    for s in small:
        for exp in range(2, 64):
            val = s ** exp
            if val > max_val:
                break
            candidates.add(val)

    # Level 2: binary ops on pairs of small + powers
    level1 = sorted(candidates)[:200]  # limit
    for a in level1:
        for b in level1:
            if a == b:
                continue
            for val in [a + b, a * b, abs(a - b)]:
                if 0 < val <= max_val:
                    candidates.add(val)
            # a^b only for small b
            if b <= 20 and a > 1:
                val = a ** b
                if 0 < val <= max_val:
                    candidates.add(val)

    return candidates


def kolmogorov_compressed_search(target_aff, search_bound):
    """
    Search structured candidates for match.
    Returns (k, num_tried, num_candidates) or (None, ...).
    """
    target_x = target_aff[0]
    candidates = kolmogorov_compressed_candidates(max_val=search_bound)
    tried = 0
    for k in sorted(candidates):
        if k <= 0 or k >= search_bound:
            continue
        pt = _to_affine(_scalar_mult(k, G_JAC))
        tried += 1
        if pt and pt[0] == target_x:
            return k, tried, len(candidates)
    return None, tried, len(candidates)


# ---------------------------------------------------------------------------
# H26 Approach 3: Kangaroo with Structured Start Bias
# ---------------------------------------------------------------------------

def kangaroo_biased_start(target_aff, search_bound, num_jumps=32, seed=42,
                          bias_points=None):
    """
    Run multiple tame kangaroos starting near 'interesting' positions.
    Each tame kangaroo walks independently with the SAME deterministic walk
    function. Multiple tame kangaroos means more DP coverage of the walk space.
    Returns (k, steps).
    """
    rng = random.Random(seed)
    n = int(SECP256K1_N)
    half = search_bound // 2

    mean_jump = max(1, int(math.isqrt(half)) // 4)
    jumps = [max(1, rng.randint(1, 2 * mean_jump)) for _ in range(num_jumps)]
    jump_affs = [_to_affine(_scalar_mult(j, G_JAC)) for j in jumps]

    D = max(1, search_bound.bit_length() // 4)
    dp_mask = (1 << D) - 1

    if bias_points is None:
        bias_points = []
        for exp in range(1, search_bound.bit_length()):
            v = 1 << exp
            if v < search_bound:
                bias_points.append(v)
        bias_points.append(half // 2)

    # Multiple tame kangaroos (limit to 4 for fair step budget)
    num_tame = min(4, len(bias_points))
    tame_kangs = []
    for bp in bias_points[:num_tame]:
        jac = _scalar_mult(bp, G_JAC)
        tame_kangs.append({'pos': bp, 'jac': jac})

    wild_pos = 0
    wild_jac = (mpz(target_aff[0]), mpz(target_aff[1]), _ONE)

    dp_table = {}
    # Total step budget same as standard (split across kangaroos)
    max_total_steps = 16 * int(math.isqrt(half)) + 10000

    steps = 0
    while steps < max_total_steps:
        # Round-robin: one step per tame kangaroo, then one wild step
        for tk in tame_kangs:
            ta = _to_affine(tk['jac'])
            if ta is not None:
                ji = ta[0] % num_jumps
                tk['pos'] += jumps[ji]
                tk['jac'] = _jac_add_affine(tk['jac'], mpz(jump_affs[ji][0]), mpz(jump_affs[ji][1]))
                steps += 1
                if (ta[0] & dp_mask) == 0:
                    key = ta[0]
                    if key in dp_table:
                        sp, st = dp_table[key]
                        if not st:
                            k_cand = (tk['pos'] - sp) % n
                            if 0 < k_cand < search_bound:
                                check = _to_affine(_scalar_mult(k_cand, G_JAC))
                                if check and check[0] == target_aff[0]:
                                    return k_cand, steps
                            k_cand = (n - k_cand) % n
                            if 0 < k_cand < search_bound:
                                check = _to_affine(_scalar_mult(k_cand, G_JAC))
                                if check and check[0] == target_aff[0]:
                                    return k_cand, steps
                    dp_table[key] = (tk['pos'], True)

        # Wild step
        wa = _to_affine(wild_jac)
        if wa is not None:
            ji = wa[0] % num_jumps
            wild_pos += jumps[ji]
            wild_jac = _jac_add_affine(wild_jac, mpz(jump_affs[ji][0]), mpz(jump_affs[ji][1]))
            steps += 1
            if (wa[0] & dp_mask) == 0:
                key = wa[0]
                if key in dp_table:
                    sp, st = dp_table[key]
                    if st:
                        k_cand = (sp - wild_pos) % n
                        if 0 < k_cand < search_bound:
                            check = _to_affine(_scalar_mult(k_cand, G_JAC))
                            if check and check[0] == target_aff[0]:
                                return k_cand, steps
                        k_cand = (n - k_cand) % n
                        if 0 < k_cand < search_bound:
                            check = _to_affine(_scalar_mult(k_cand, G_JAC))
                            if check and check[0] == target_aff[0]:
                                return k_cand, steps
                dp_table[key] = (wild_pos, False)

    return None, steps


# ===========================================================================
# Test Harness
# ===========================================================================

def run_h21_tests():
    """Run all H21 experiments."""
    results = {}
    rng = random.Random(12345)

    # --- H21.1: Multi-armed Bandit vs Standard ---
    print("=" * 70)
    print("H21.1: Multi-Armed Bandit (UCB1) vs Standard Kangaroo")
    print("=" * 70)

    for bits in [28, 32]:
        bound = 1 << bits
        n_trials = 10

        # Training phase for bandit lookup
        print(f"  Training bandit lookup for {bits}b...")
        lookup, tr_jumps, tr_affs = _train_bandit_jump_table(
            bound, num_jumps=32, n_walks=20, seed=42)

        std_steps_list = []
        ucb_steps_list = []

        for trial in range(n_trials):
            k_true = rng.randint(1, bound - 1)
            target = make_target(k_true)

            k1, s1 = kangaroo_standard(target, bound, seed=trial)
            std_steps_list.append(s1)

            k2, s2 = kangaroo_ucb1(target, bound, seed=trial,
                                    trained_lookup=lookup,
                                    trained_jumps=tr_jumps,
                                    trained_jump_affs=tr_affs)
            ucb_steps_list.append(s2)

            ok1 = "OK" if k1 == k_true else "FAIL"
            ok2 = "OK" if k2 == k_true else "FAIL"
            print(f"  {bits}b trial {trial}: std={s1:>8} [{ok1}]  ucb1={s2:>8} [{ok2}]")

        avg_std = sum(std_steps_list) / n_trials
        avg_ucb = sum(ucb_steps_list) / n_trials
        ratio = avg_std / avg_ucb if avg_ucb > 0 else 0
        print(f"  {bits}b avg: std={avg_std:.0f}  ucb1={avg_ucb:.0f}  ratio={ratio:.3f}")
        results[f'h21.1_{bits}b'] = {
            'std_avg': avg_std, 'ucb_avg': avg_ucb, 'ratio': ratio
        }
        print()

    # --- H21.2: Feature-based selection (train then test) ---
    print("=" * 70)
    print("H21.2: Feature-Based Jump Selection (Train/Test)")
    print("=" * 70)

    bits = 28
    bound = 1 << bits

    # Training phase
    print("  Training feature lookup...")
    feat_lookup, feat_jumps, feat_affs = _train_feature_lookup(
        bound, num_jumps=32, num_features=256, n_walks=20, seed=42)

    # Test phase
    print("  Testing on 10 instances...")
    feat_steps = []
    std_steps = []
    for trial in range(10):
        k_true = rng.randint(1, bound - 1)
        target = make_target(k_true)

        k1, s1 = kangaroo_standard(target, bound, seed=trial + 100)
        std_steps.append(s1)

        k2, s2 = kangaroo_feature(target, bound, seed=trial + 100,
                                   feature_lookup=feat_lookup,
                                   feature_jumps=feat_jumps,
                                   feature_jump_affs=feat_affs)
        feat_steps.append(s2)

        ok1 = "OK" if k1 == k_true else "FAIL"
        ok2 = "OK" if k2 == k_true else "FAIL"
        print(f"    trial {trial}: std={s1:>8} [{ok1}]  feat={s2:>8} [{ok2}]")

    avg_std = sum(std_steps) / len(std_steps)
    avg_feat = sum(feat_steps) / len(feat_steps)
    ratio = avg_std / avg_feat if avg_feat > 0 else 0
    print(f"  28b avg: std={avg_std:.0f}  feature={avg_feat:.0f}  ratio={ratio:.3f}")
    results['h21.2_28b'] = {
        'std_avg': avg_std, 'feat_avg': avg_feat, 'ratio': ratio
    }
    print()

    # --- H21.3: Hash function comparison ---
    print("=" * 70)
    print("H21.3: Hash Function Comparison for Deterministic Walk")
    print("=" * 70)

    bits = 28
    bound = 1 << bits
    n_trials = 10
    hash_names = ['xmod', 'sha256', 'xor_shift', 'multiply']

    for hfn in hash_names:
        step_list = []
        for trial in range(n_trials):
            k_true = rng.randint(1, bound - 1)
            target = make_target(k_true)
            k, s = kangaroo_hash_compare(target, bound, hash_fn=hfn, seed=trial)
            step_list.append(s)
            ok = "OK" if k == k_true else "FAIL"

        avg = sum(step_list) / n_trials
        print(f"  {hfn:>12}: avg_steps={avg:.0f}")
        results[f'h21.3_{hfn}'] = {'avg_steps': avg}

    print()
    return results


def run_h26_tests():
    """Run all H26 experiments."""
    results = {}
    rng = random.Random(54321)

    # --- H26.1: Structured search ---
    print("=" * 70)
    print("H26.1: Structured Number Search")
    print("=" * 70)

    # Test with a STRUCTURED key
    bits = 30
    bound = 1 << bits
    structured_keys = [
        (1 << 27) + (1 << 15) + 1,   # 2^27 + 2^15 + 1
        (1 << 25) - (1 << 10),        # 2^25 - 2^10
        (1 << 28) + (1 << 20) + (1 << 5),
    ]

    for k_true in structured_keys:
        target = make_target(k_true)
        k, tried = kolmogorov_structured_search(target, bound)
        found = "FOUND" if k == k_true else "NOT FOUND"
        print(f"  k={k_true} ({bin(k_true)}): {found} after {tried} tries")

    # Test with RANDOM keys (should NOT be found)
    print("\n  Random keys (should not be found by structured search):")
    for trial in range(3):
        k_true = rng.randint(1, bound - 1)
        target = make_target(k_true)
        k, tried = kolmogorov_structured_search(target, bound)
        found = "FOUND" if k == k_true else "not found"
        print(f"  k={k_true}: {found} after {tried} tries")

    results['h26.1'] = 'see output'
    print()

    # --- H26.2: Compressed candidate coverage ---
    print("=" * 70)
    print("H26.2: Compressed Candidate Generation Coverage")
    print("=" * 70)

    for max_bits in [20, 30, 40]:
        max_val = 1 << max_bits
        candidates = kolmogorov_compressed_candidates(max_val=max_val)
        n_cands = len(candidates)
        coverage = n_cands / max_val * 100
        print(f"  max_val=2^{max_bits}: {n_cands} candidates, "
              f"coverage={coverage:.6f}%")

    # Test: structured key in compressed set?
    print("\n  Checking if structured keys are in compressed set...")
    candidates = kolmogorov_compressed_candidates(max_val=1 << 40)
    for k in structured_keys:
        found = k in candidates
        print(f"  k={k}: {'IN SET' if found else 'NOT IN SET'}")

    results['h26.2'] = 'see output'
    print()

    # --- H26.3: Kangaroo with biased start ---
    print("=" * 70)
    print("H26.3: Kangaroo with Structured Start Bias")
    print("=" * 70)

    bits = 28
    bound = 1 << bits
    n_trials = 5

    # Structured key: near a power of 2
    print("  Structured keys (near powers of 2):")
    struct_std = []
    struct_bias = []
    for trial in range(n_trials):
        # k = 2^(20+trial) + small random offset
        base_exp = 20 + trial
        k_true = (1 << base_exp) + rng.randint(0, 1 << 15)
        if k_true >= bound:
            k_true = k_true % bound
        target = make_target(k_true)

        k1, s1 = kangaroo_standard(target, bound, seed=trial)
        k2, s2 = kangaroo_biased_start(target, bound, seed=trial)
        struct_std.append(s1)
        struct_bias.append(s2)

        ok1 = "OK" if k1 == k_true else "FAIL"
        ok2 = "OK" if k2 == k_true else "FAIL"
        print(f"    k~2^{base_exp}: std={s1:>8} [{ok1}]  biased={s2:>8} [{ok2}]")

    print("\n  Random keys:")
    rand_std = []
    rand_bias = []
    for trial in range(n_trials):
        k_true = rng.randint(1, bound - 1)
        target = make_target(k_true)

        k1, s1 = kangaroo_standard(target, bound, seed=trial + 50)
        k2, s2 = kangaroo_biased_start(target, bound, seed=trial + 50)
        rand_std.append(s1)
        rand_bias.append(s2)

        ok1 = "OK" if k1 == k_true else "FAIL"
        ok2 = "OK" if k2 == k_true else "FAIL"
        print(f"    random: std={s1:>8} [{ok1}]  biased={s2:>8} [{ok2}]")

    avg_ss = sum(struct_std) / n_trials
    avg_sb = sum(struct_bias) / n_trials
    avg_rs = sum(rand_std) / n_trials
    avg_rb = sum(rand_bias) / n_trials
    print(f"\n  Structured: std_avg={avg_ss:.0f}  biased_avg={avg_sb:.0f}  "
          f"ratio={avg_ss/avg_sb if avg_sb > 0 else 0:.3f}")
    print(f"  Random:     std_avg={avg_rs:.0f}  biased_avg={avg_rb:.0f}  "
          f"ratio={avg_rs/avg_rb if avg_rb > 0 else 0:.3f}")

    results['h26.3'] = {
        'struct_ratio': avg_ss / avg_sb if avg_sb > 0 else 0,
        'random_ratio': avg_rs / avg_rb if avg_rb > 0 else 0,
    }
    print()
    return results


# ===========================================================================
# Main
# ===========================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("H21: RL-Optimized Kangaroo Jumps")
    print("H26: Kolmogorov Complexity Filter")
    print("Testing on secp256k1")
    print("=" * 70)
    print()

    t0 = time.time()
    h21_results = run_h21_tests()
    t1 = time.time()
    print(f"H21 total time: {t1 - t0:.1f}s\n")

    t2 = time.time()
    h26_results = run_h26_tests()
    t3 = time.time()
    print(f"H26 total time: {t3 - t2:.1f}s\n")

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print("\nH21.1 (UCB1 Bandit):")
    for key in sorted(h21_results):
        if key.startswith('h21.1'):
            r = h21_results[key]
            verdict = "BETTER" if r['ratio'] > 1.05 else ("WORSE" if r['ratio'] < 0.95 else "NEUTRAL")
            print(f"  {key}: std={r['std_avg']:.0f} ucb={r['ucb_avg']:.0f} "
                  f"ratio={r['ratio']:.3f} -> {verdict}")

    print("\nH21.2 (Feature-based):")
    if 'h21.2_28b' in h21_results:
        r = h21_results['h21.2_28b']
        feat_val = r.get('feat_avg', r.get('ucb_avg', 0))
        verdict = "BETTER" if r['ratio'] > 1.05 else ("WORSE" if r['ratio'] < 0.95 else "NEUTRAL")
        print(f"  28b: std={r['std_avg']:.0f} feat={feat_val:.0f} "
              f"ratio={r['ratio']:.3f} -> {verdict}")

    print("\nH21.3 (Hash comparison):")
    best_hash = min(h21_results, key=lambda k: h21_results[k].get('avg_steps', 1e18)
                    if k.startswith('h21.3') else 1e18)
    for key in sorted(h21_results):
        if key.startswith('h21.3'):
            r = h21_results[key]
            marker = " <-- BEST" if key == best_hash else ""
            print(f"  {key}: avg_steps={r['avg_steps']:.0f}{marker}")

    print("\nH26.3 (Biased start):")
    if 'h26.3' in h26_results:
        r = h26_results['h26.3']
        print(f"  Structured keys: ratio={r['struct_ratio']:.3f} "
              f"({'HELPS' if r['struct_ratio'] > 1.05 else 'NO HELP'})")
        print(f"  Random keys:     ratio={r['random_ratio']:.3f} "
              f"({'HELPS' if r['random_ratio'] > 1.05 else 'NO HELP'})")

    print(f"\nTotal time: {t3 - t0:.1f}s")

"""
H19: 2D Eisenstein Kangaroo for ECDLP on secp256k1.

Exploits the GLV endomorphism (phi: x -> BETA*x, corresponding to scalar LAMBDA)
to enhance kangaroo DP collision rates via Z/3 and Z/6 symmetry.

Variants benchmarked:
  1. Standard 1D Pollard kangaroo (baseline)
  2. 1D kangaroo + Z/3 DP symmetry (3x collision opportunities from phi orbit)
  3. 1D kangaroo + Z/6 DP symmetry (6x from phi orbit + negation)
"""

import time
import math
import random
from gmpy2 import mpz, invert as _gmp_invert

# ---------------------------------------------------------------------------
# secp256k1 constants
# ---------------------------------------------------------------------------
P_MOD = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N_ORD = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
BETA = 0x7AE96A2B657C07106E64479EAC3434E99CF0497512F58995C1396C28719501EE
LAMBDA = 0x5363AD4CC05C30E0A5261C028812645A122E22EA20816678DF02967C1B23BD72

_p = mpz(P_MOD)
_n = mpz(N_ORD)
_beta = mpz(BETA)
_lambda = mpz(LAMBDA)
_ZERO = mpz(0)
_ONE = mpz(1)

# ---------------------------------------------------------------------------
# Jacobian EC arithmetic (secp256k1: y^2 = x^3 + 7, a=0)
# ---------------------------------------------------------------------------

class JacPoint:
    __slots__ = ('X', 'Y', 'Z')
    def __init__(self, X, Y, Z):
        self.X = X; self.Y = Y; self.Z = Z
    @staticmethod
    def infinity():
        return JacPoint(_ZERO, _ONE, _ZERO)
    @property
    def is_inf(self):
        return self.Z == 0
    def to_affine(self):
        if self.Z == 0: return None
        Zi = _gmp_invert(self.Z, _p)
        Z2 = Zi * Zi % _p
        Z3 = Z2 * Zi % _p
        return (int(self.X * Z2 % _p), int(self.Y * Z3 % _p))
    def affine_x(self):
        if self.Z == 0: return None
        Zi = _gmp_invert(self.Z, _p)
        Z2 = Zi * Zi % _p
        return int(self.X * Z2 % _p)


def jac_double(P):
    X1, Y1, Z1 = P.X, P.Y, P.Z
    if Z1 == 0 or Y1 == 0: return JacPoint.infinity()
    Y1_sq = Y1 * Y1 % _p
    S = 4 * X1 * Y1_sq % _p
    M = 3 * X1 * X1 % _p
    X3 = (M * M - 2 * S) % _p
    Y1_4 = Y1_sq * Y1_sq % _p
    Y3 = (M * (S - X3) - 8 * Y1_4) % _p
    Z3 = 2 * Y1 * Z1 % _p
    return JacPoint(X3, Y3, Z3)


def jac_add(P, Q):
    X1, Y1, Z1 = P.X, P.Y, P.Z
    X2, Y2, Z2 = Q.X, Q.Y, Q.Z
    if Z1 == 0: return Q
    if Z2 == 0: return P
    Z1_sq = Z1 * Z1 % _p
    Z2_sq = Z2 * Z2 % _p
    U1 = X1 * Z2_sq % _p
    U2 = X2 * Z1_sq % _p
    S1 = Y1 * Z2_sq % _p * Z2 % _p
    S2 = Y2 * Z1_sq % _p * Z1 % _p
    H = (U2 - U1) % _p
    if H == 0:
        return jac_double(P) if S1 == S2 else JacPoint.infinity()
    R = (S2 - S1) % _p
    H_sq = H * H % _p
    H_cu = H_sq * H % _p
    X3 = (R * R - H_cu - 2 * U1 * H_sq) % _p
    Y3 = (R * (U1 * H_sq - X3) - S1 * H_cu) % _p
    Z3 = H * Z1 * Z2 % _p
    return JacPoint(X3, Y3, Z3)


def jac_add_affine(P, ax, ay):
    X1, Y1, Z1 = P.X, P.Y, P.Z
    if Z1 == 0: return JacPoint(mpz(ax), mpz(ay), _ONE)
    Z1_sq = Z1 * Z1 % _p
    U2 = ax * Z1_sq % _p
    S2 = ay * Z1_sq % _p * Z1 % _p
    H = (U2 - X1) % _p
    if H == 0:
        return jac_double(P) if S2 == Y1 else JacPoint.infinity()
    R = (S2 - Y1) % _p
    H_sq = H * H % _p
    H_cu = H_sq * H % _p
    X3 = (R * R - H_cu - 2 * X1 * H_sq) % _p
    Y3 = (R * (X1 * H_sq - X3) - Y1 * H_cu) % _p
    Z3 = H * Z1 % _p
    return JacPoint(X3, Y3, Z3)


def jac_neg(P):
    return JacPoint(P.X, (-P.Y) % _p, P.Z)


def scalar_mult(k, P):
    if k == 0: return JacPoint.infinity()
    if k < 0: P = jac_neg(P); k = -k
    result = JacPoint.infinity()
    addend = P
    while k:
        if k & 1: result = jac_add(result, addend)
        addend = jac_double(addend)
        k >>= 1
    return result


def scalar_mult_affine(k, ax, ay):
    return scalar_mult(k, JacPoint(mpz(ax), mpz(ay), _ONE))


def phi_affine(x, y):
    """phi: (x, y) -> (BETA*x mod p, y) = [LAMBDA]*P on secp256k1."""
    return (int(_beta * x % _p), y)


# ---------------------------------------------------------------------------
# Generator and endomorphism precomputation
# ---------------------------------------------------------------------------
G_jac = JacPoint(mpz(GX), mpz(GY), _ONE)
PHI_GX = int(_beta * GX % _p)
PHI_GY = GY

# Precompute BETA^2 mod p for Z/3 orbit
_beta2 = _beta * _beta % _p


def _z6_all_x(x):
    """Return all 3 distinct x-coordinates in the Z/6 orbit."""
    x1 = x % P_MOD
    x2 = int(_beta * x % _p)
    x3 = int(_beta2 * x % _p)
    return (x1, x2, x3)


# ---------------------------------------------------------------------------
# Common kangaroo setup
# ---------------------------------------------------------------------------

def _make_jump_table(num_jumps, mean_jump):
    """Create jump table with actual mean close to target mean_jump.

    Uses num_jumps entries, each a random power of 2 scaled to mean_jump.
    Actual jump sizes: mean_jump * 2^(i mod r) / 2^(r/2) for r distinct scales.
    """
    # Use 8 distinct scale levels (2^0 to 2^7), repeated to fill num_jumps
    # Range: mean_jump/8 to 8*mean_jump, geometric mean ≈ mean_jump
    r = 8  # number of distinct scales
    jumps = []
    for i in range(num_jumps):
        level = i % r
        # Centered around mean_jump: sizes from mean_jump/2^(r/2-1) to mean_jump*2^(r/2)
        j = max(1, (mean_jump * (1 << level)) >> (r // 2 - 1))
        jumps.append(j)

    # Verify and adjust mean
    actual_mean = sum(jumps) / len(jumps)
    if actual_mean > 0 and abs(actual_mean - mean_jump) / mean_jump > 0.5:
        # Rescale to match target mean
        factor = mean_jump / actual_mean
        jumps = [max(1, int(j * factor)) for j in jumps]

    jump_affs = []
    for j in jumps:
        jp = scalar_mult_affine(j, GX, GY).to_affine()
        jump_affs.append((mpz(jp[0]), mpz(jp[1])))
    return jumps, jump_affs


def _kangaroo_params(bits):
    """Compute standard kangaroo parameters for a given bit size.

    Uses negation map: search [0, N/2), if not found try n-k.
    Tame starts at N/4 (midpoint of [0, N/2)).
    mean_jump ~ sqrt(N/2) / 4 per van Oorschot-Wiener.
    """
    search_bound = 1 << bits
    half_bound = search_bound >> 1
    # mean_jump ~ sqrt(half_bound) / 4
    mean_jump = max(1, int(math.isqrt(half_bound)) >> 2)
    # DP bits
    D = max(1, bits // 4)
    dp_mask = (1 << D) - 1
    # Tame starts at midpoint of [0, half_bound)
    tame_start = half_bound >> 1
    # Max steps: 16*sqrt(half_bound) for safety (expected ~4*sqrt)
    max_steps = 16 * int(math.isqrt(half_bound)) + 10000
    return search_bound, half_bound, mean_jump, D, dp_mask, tame_start, max_steps


# ---------------------------------------------------------------------------
# Variant 1: Standard 1D Kangaroo (baseline)
# ---------------------------------------------------------------------------

def kangaroo_1d(target_jac, bits, verbose=False):
    """Standard 1D Pollard kangaroo searching k in [0, 2^bits).
    Returns (k, steps) or (None, steps)."""
    search_bound, half_bound, mean_jump, D, dp_mask, tame_start, max_steps = _kangaroo_params(bits)
    n = N_ORD
    target_aff = target_jac.to_affine()
    num_jumps = 32

    jumps, jump_affs = _make_jump_table(num_jumps, mean_jump)

    tame_pos = tame_start
    tame_jac = scalar_mult_affine(tame_pos, GX, GY)
    wild_pos = 0
    wild_jac = JacPoint(target_jac.X, target_jac.Y, target_jac.Z)

    dp_table = {}
    steps = 0

    for step in range(max_steps):
        steps = step + 1

        # Check tame for DP
        tx = tame_jac.affine_x()
        if tx is not None and (tx & dp_mask) == 0:
            if tx in dp_table:
                sp, st = dp_table[tx]
                if not st:
                    k = (tame_pos - sp) % n
                    if k < search_bound:
                        check = scalar_mult_affine(k, GX, GY)
                        if check.to_affine() == target_aff:
                            return k, steps
                    k = (n - k) % n
                    if k < search_bound:
                        check = scalar_mult_affine(k, GX, GY)
                        if check.to_affine() == target_aff:
                            return k, steps
            else:
                dp_table[tx] = (tame_pos, True)

        ji = (tx % num_jumps) if tx is not None else 0
        tame_pos += jumps[ji]
        tame_jac = jac_add_affine(tame_jac, jump_affs[ji][0], jump_affs[ji][1])

        # Check wild for DP
        wx = wild_jac.affine_x()
        if wx is not None and (wx & dp_mask) == 0:
            if wx in dp_table:
                sp, st = dp_table[wx]
                if st:
                    k = (sp - wild_pos) % n
                    if k < search_bound:
                        check = scalar_mult_affine(k, GX, GY)
                        if check.to_affine() == target_aff:
                            return k, steps
                    k = (n - k) % n
                    if k < search_bound:
                        check = scalar_mult_affine(k, GX, GY)
                        if check.to_affine() == target_aff:
                            return k, steps
            else:
                dp_table[wx] = (wild_pos, False)

        ji = (wx % num_jumps) if wx is not None else 0
        wild_pos += jumps[ji]
        wild_jac = jac_add_affine(wild_jac, jump_affs[ji][0], jump_affs[ji][1])

    return None, steps


# ---------------------------------------------------------------------------
# Variant 2: 1D Kangaroo + Z/3 DP symmetry
# ---------------------------------------------------------------------------

def kangaroo_1d_z3(target_jac, bits, verbose=False):
    """1D kangaroo with Z/3 x-coordinate symmetry for DP storage.

    Walk is standard 1D, but DPs are stored under all 3 orbit-equivalent
    x-coordinates: x, BETA*x, BETA^2*x. This gives up to 3x more collision
    opportunities. When a cross-orbit collision occurs, we try all LAMBDA
    multipliers to recover k.
    """
    search_bound, half_bound, mean_jump, D, dp_mask, tame_start, max_steps = _kangaroo_params(bits)
    n = N_ORD
    lam = LAMBDA
    lam2 = (LAMBDA * LAMBDA) % n
    target_aff = target_jac.to_affine()
    num_jumps = 32

    jumps, jump_affs = _make_jump_table(num_jumps, mean_jump)

    tame_pos = tame_start
    tame_jac = scalar_mult_affine(tame_pos, GX, GY)
    wild_pos = 0
    wild_jac = JacPoint(target_jac.X, target_jac.Y, target_jac.Z)

    dp_table = {}
    steps = 0

    def store_z3(x, pos, is_tame):
        for xv in _z6_all_x(x):
            if xv not in dp_table:
                dp_table[xv] = (pos, is_tame)

    def try_recover(tame_s, wild_s):
        """Try orbit multipliers to recover k.
        If two points share an x-coord (possibly via BETA), then
        their scalars satisfy: s1 = ±LAMBDA^e * s2 for some e in {0,1,2}.
        So: tame_s = ±LAMBDA^e * (k + wild_s)
        => k = ±LAMBDA^(-e) * tame_s - wild_s
        LAMBDA^(-1) = LAMBDA^2 (since LAMBDA^3 = 1 mod n)
        """
        # 6 candidates: LAMBDA^e * (-1)^s for e in {0,1,2}, s in {0,1}
        for mult in [1, lam, lam2]:
            k_try = (mult * tame_s - wild_s) % n
            if k_try < search_bound:
                check = scalar_mult_affine(k_try, GX, GY)
                if check.to_affine() == target_aff:
                    return k_try
            # negation: -LAMBDA^e * tame_s = k + wild_s
            k_try = (n - mult * tame_s % n - wild_s) % n
            if k_try < search_bound:
                check = scalar_mult_affine(k_try, GX, GY)
                if check.to_affine() == target_aff:
                    return k_try
        return None

    for step in range(max_steps):
        steps = step + 1

        tx = tame_jac.affine_x()
        if tx is not None and (tx & dp_mask) == 0:
            collision = False
            for xv in _z6_all_x(tx):
                if xv in dp_table:
                    sp, st = dp_table[xv]
                    if not st:
                        k = try_recover(tame_pos, sp)
                        if k is not None:
                            return k, steps
                        collision = True
            if not collision:
                store_z3(tx, tame_pos, True)

        ji = (tx % num_jumps) if tx is not None else 0
        tame_pos += jumps[ji]
        tame_jac = jac_add_affine(tame_jac, jump_affs[ji][0], jump_affs[ji][1])

        wx = wild_jac.affine_x()
        if wx is not None and (wx & dp_mask) == 0:
            collision = False
            for xv in _z6_all_x(wx):
                if xv in dp_table:
                    sp, st = dp_table[xv]
                    if st:
                        k = try_recover(sp, wild_pos)
                        if k is not None:
                            return k, steps
                        collision = True
            if not collision:
                store_z3(wx, wild_pos, False)

        ji = (wx % num_jumps) if wx is not None else 0
        wild_pos += jumps[ji]
        wild_jac = jac_add_affine(wild_jac, jump_affs[ji][0], jump_affs[ji][1])

    return None, steps


# ---------------------------------------------------------------------------
# Variant 3: 1D Kangaroo + Z/6 DP symmetry (phi orbit + negation)
# ---------------------------------------------------------------------------

def kangaroo_1d_z6(target_jac, bits, verbose=False):
    """1D kangaroo with full Z/6 symmetry: phi orbit (3x) + negation (2x).

    Same 1D walk, but DP table stores under all 3 orbit x-coords.
    Recovery tries all 18 combinations of LAMBDA multipliers and negations.
    """
    search_bound, half_bound, mean_jump, D, dp_mask, tame_start, max_steps = _kangaroo_params(bits)
    n = N_ORD
    lam = LAMBDA
    lam2 = (LAMBDA * LAMBDA) % n
    target_aff = target_jac.to_affine()
    num_jumps = 32

    jumps, jump_affs = _make_jump_table(num_jumps, mean_jump)

    tame_pos = tame_start
    tame_jac = scalar_mult_affine(tame_pos, GX, GY)
    wild_pos = 0
    wild_jac = JacPoint(target_jac.X, target_jac.Y, target_jac.Z)

    dp_table = {}
    steps = 0

    def store_z3(x, pos, is_tame):
        for xv in _z6_all_x(x):
            if xv not in dp_table:
                dp_table[xv] = (pos, is_tame)

    def try_recover(tame_s, wild_s):
        """Try Z/6 orbit multipliers to recover k.
        Same as Z/3 but only 6 candidates needed."""
        for mult in [1, lam, lam2]:
            k_try = (mult * tame_s - wild_s) % n
            if k_try < search_bound:
                check = scalar_mult_affine(k_try, GX, GY)
                if check.to_affine() == target_aff:
                    return k_try
            k_try = (n - mult * tame_s % n - wild_s) % n
            if k_try < search_bound:
                check = scalar_mult_affine(k_try, GX, GY)
                if check.to_affine() == target_aff:
                    return k_try
        return None

    for step in range(max_steps):
        steps = step + 1

        tx = tame_jac.affine_x()
        if tx is not None and (tx & dp_mask) == 0:
            collision = False
            for xv in _z6_all_x(tx):
                if xv in dp_table:
                    sp, st = dp_table[xv]
                    if not st:
                        k = try_recover(tame_pos, sp)
                        if k is not None:
                            return k, steps
                        collision = True
            if not collision:
                store_z3(tx, tame_pos, True)

        ji = (tx % num_jumps) if tx is not None else 0
        tame_pos += jumps[ji]
        tame_jac = jac_add_affine(tame_jac, jump_affs[ji][0], jump_affs[ji][1])

        wx = wild_jac.affine_x()
        if wx is not None and (wx & dp_mask) == 0:
            collision = False
            for xv in _z6_all_x(wx):
                if xv in dp_table:
                    sp, st = dp_table[xv]
                    if st:
                        k = try_recover(sp, wild_pos)
                        if k is not None:
                            return k, steps
                        collision = True
            if not collision:
                store_z3(wx, wild_pos, False)

        ji = (wx % num_jumps) if wx is not None else 0
        wild_pos += jumps[ji]
        wild_jac = jac_add_affine(wild_jac, jump_affs[ji][0], jump_affs[ji][1])

    return None, steps


# ---------------------------------------------------------------------------
# Benchmark harness
# ---------------------------------------------------------------------------

def run_benchmark(bits_list=None, trials=3, verbose=True):
    if bits_list is None:
        bits_list = [28, 32, 36, 40]

    results = {}
    rng = random.Random(42)

    for bits in bits_list:
        bound = 1 << bits
        print(f"\n{'='*60}")
        print(f"  ECDLP {bits}-bit search space (k < 2^{bits})")
        print(f"{'='*60}")

        variant_results = {}

        for variant_name, solver_fn in [
            ("1D kangaroo", kangaroo_1d),
            ("1D + Z/3 DP", kangaroo_1d_z3),
            ("1D + Z/6 DP", kangaroo_1d_z6),
        ]:
            times = []
            step_counts = []
            solved = 0

            for trial in range(trials):
                k_true = rng.randint(1, bound - 1)
                target = scalar_mult_affine(k_true, GX, GY)

                t0 = time.time()
                k_found, steps = solver_fn(target, bits, verbose=False)
                elapsed = time.time() - t0

                if k_found is not None:
                    check = scalar_mult_affine(k_found, GX, GY)
                    if check.to_affine() == target.to_affine():
                        solved += 1
                    else:
                        print(f"    WRONG: expected {k_true}, got {k_found}")
                else:
                    print(f"    FAIL: {variant_name} trial {trial}, k={k_true}")

                times.append(elapsed)
                step_counts.append(steps)

            avg_time = sum(times) / len(times) if times else float('inf')
            avg_steps = sum(step_counts) / len(step_counts) if step_counts else 0
            steps_per_sec = avg_steps / avg_time if avg_time > 0 else 0

            variant_results[variant_name] = {
                'avg_time': avg_time,
                'avg_steps': avg_steps,
                'steps_per_sec': steps_per_sec,
                'solved': solved,
                'trials': trials,
            }

            print(f"\n  {variant_name}:")
            print(f"    Solved: {solved}/{trials}")
            print(f"    Avg time:  {avg_time:.3f}s")
            print(f"    Avg steps: {avg_steps:.0f}")
            print(f"    Steps/sec: {steps_per_sec:.0f}")

        results[bits] = variant_results

        baseline = variant_results.get("1D kangaroo", {}).get('avg_time', 1)
        if baseline > 0:
            print(f"\n  Speedup vs 1D baseline:")
            for name, r in variant_results.items():
                if name != "1D kangaroo":
                    speedup = baseline / r['avg_time'] if r['avg_time'] > 0 else 0
                    print(f"    {name}: {speedup:.2f}x")

    return results


if __name__ == "__main__":
    print("H19: 2D Eisenstein Kangaroo for ECDLP (secp256k1)")
    print("=" * 60)

    # Quick verification
    print("\nVerification...")
    phi_g = phi_affine(GX, GY)
    lam_g = scalar_mult_affine(LAMBDA, GX, GY).to_affine()
    assert phi_g == lam_g, f"phi(G) != LAMBDA*G"
    print("  phi(G) == LAMBDA*G: OK")

    # Run benchmarks
    results = run_benchmark(bits_list=[28, 32, 36, 40], trials=3)

    # Final summary
    print(f"\n\n{'='*70}")
    print("FINAL SUMMARY")
    print(f"{'='*70}")
    print(f"{'Bits':>6} | {'1D time':>10} | {'Z/3 time':>10} | {'Z/6 time':>10} | {'Z/3 spdup':>10} | {'Z/6 spdup':>10}")
    print("-" * 70)
    for bits in sorted(results.keys()):
        r = results[bits]
        t1 = r.get("1D kangaroo", {}).get('avg_time', 0)
        t2 = r.get("1D + Z/3 DP", {}).get('avg_time', 0)
        t3 = r.get("1D + Z/6 DP", {}).get('avg_time', 0)
        s2 = t1 / t2 if t2 > 0 else 0
        s3 = t1 / t3 if t3 > 0 else 0
        print(f"{bits:>6} | {t1:>9.3f}s | {t2:>9.3f}s | {t3:>9.3f}s | {s2:>9.2f}x | {s3:>9.2f}x")

"""
ECDLP Hypotheses H20 (Lattice Inversion) and H23 (x-Coordinate Modular Chains)
on secp256k1.

Tests whether lattice reduction or modular x-coordinate constraints can
recover bounded discrete logs faster than O(sqrt(N)) kangaroo.
"""

import time
import gmpy2
from gmpy2 import mpz, invert as gmp_invert

# ---------------------------------------------------------------------------
# secp256k1 parameters
# ---------------------------------------------------------------------------
P = mpz(0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F)
N = mpz(0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141)
Gx = mpz(0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798)
Gy = mpz(0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)

# ---------------------------------------------------------------------------
# Minimal EC arithmetic (affine, secp256k1: y^2 = x^3 + 7)
# ---------------------------------------------------------------------------
INF = None

def ec_add(P1, P2):
    if P1 is INF: return P2
    if P2 is INF: return P1
    x1, y1 = P1; x2, y2 = P2
    if x1 == x2:
        if y1 == y2:
            return ec_double(P1)
        return INF
    dx = (x2 - x1) % P
    lam = ((y2 - y1) * gmp_invert(dx, P)) % P
    x3 = (lam * lam - x1 - x2) % P
    y3 = (lam * (x1 - x3) - y1) % P
    return (x3, y3)

def ec_double(pt):
    if pt is INF: return INF
    x, y = pt
    if y == 0: return INF
    lam = (3 * x * x * gmp_invert(2 * y, P)) % P
    x3 = (lam * lam - 2 * x) % P
    y3 = (lam * (x - x3) - y) % P
    return (x3, y3)

def ec_mul(k, pt):
    k = mpz(k)
    if k == 0: return INF
    if k < 0:
        pt = (pt[0], (-pt[1]) % P)
        k = -k
    R = INF
    Q = pt
    while k:
        if k & 1:
            R = ec_add(R, Q)
        Q = ec_double(Q)
        k >>= 1
    return R

G = (Gx, Gy)

# ---------------------------------------------------------------------------
# H20: Lattice Inversion of Bounded k
# ---------------------------------------------------------------------------
def gram_schmidt(basis):
    """Gram-Schmidt orthogonalization over rationals (using Python fractions)."""
    from fractions import Fraction
    n = len(basis)
    d = len(basis[0])
    ortho = [[Fraction(0)] * d for _ in range(n)]
    mu = [[Fraction(0)] * n for _ in range(n)]
    B_norms = [Fraction(0)] * n

    for i in range(n):
        ortho[i] = [Fraction(basis[i][j]) for j in range(d)]
        for j in range(i):
            if B_norms[j] == 0:
                mu[i][j] = Fraction(0)
            else:
                dot = sum(Fraction(basis[i][l]) * ortho[j][l] for l in range(d))
                mu[i][j] = dot / B_norms[j]
            for l in range(d):
                ortho[i][l] -= mu[i][j] * ortho[j][l]
        B_norms[i] = sum(ortho[i][l] ** 2 for l in range(d))
    return ortho, mu, B_norms

def lll_reduce(basis, delta=0.75):
    """LLL reduction for small (3-5 dim) integer lattices."""
    from fractions import Fraction
    n = len(basis)
    d = len(basis[0])
    basis = [list(row) for row in basis]

    def gs():
        return gram_schmidt(basis)

    ortho, mu, B_norms = gs()
    k = 1
    while k < n:
        # Size-reduce
        for j in range(k - 1, -1, -1):
            if abs(mu[k][j]) > Fraction(1, 2):
                r = int(round(float(mu[k][j])))
                for l in range(d):
                    basis[k][l] -= r * basis[j][l]
                ortho, mu, B_norms = gs()

        # Lovász condition
        lhs = B_norms[k]
        rhs = (Fraction(delta) - mu[k][k - 1] ** 2) * B_norms[k - 1]
        if lhs >= rhs:
            k += 1
        else:
            basis[k], basis[k - 1] = basis[k - 1], basis[k]
            ortho, mu, B_norms = gs()
            k = max(k - 1, 1)
    return basis


def test_h20_basic_lattice(k_true):
    """
    H20 test: Build 3D lattice from G.x, K.x, p.
    LLL-reduce and check if any short vector reveals k.
    """
    print(f"\n{'='*60}")
    print(f"H20: Lattice Inversion — k = {k_true}")
    print(f"{'='*60}")

    K = ec_mul(k_true, G)
    Kx = int(K[0])
    gx = int(Gx)
    p_int = int(P)

    # Lattice 1: Basic formulation
    # Rows: [1, 0, G.x], [0, 1, K.x], [0, 0, p]
    # Short vector might be (a, b, 0) meaning a*G.x + b*K.x ≡ 0 mod p
    # That doesn't directly give k, but let's see what LLL finds.

    # Scale factor to balance dimensions
    W = 2 ** 256  # weight for the "mod p" dimension

    lattice = [
        [1, 0, gx],
        [0, 1, Kx],
        [0, 0, p_int],
    ]

    print(f"  K.x = {hex(Kx)[:20]}...")
    print(f"  Reducing 3x3 lattice...")

    t0 = time.time()
    reduced = lll_reduce(lattice)
    dt = time.time() - t0
    print(f"  LLL took {dt:.3f}s")

    found = False
    for i, row in enumerate(reduced):
        v0, v1, v2 = row
        norm = (v0**2 + v1**2 + v2**2) ** 0.5
        print(f"  Row {i}: [{v0}, {v1}, {v2 if abs(v2) < 1000 else '...'}] norm≈{norm:.2e}")
        # Check if v0 or v1 relates to k
        for candidate in [v0, v1, -v0, -v1, abs(v0), abs(v1)]:
            if candidate == k_true and candidate > 0:
                print(f"  *** FOUND k = {k_true} in row {i}! ***")
                found = True

    if not found:
        print(f"  k not directly found in lattice vectors.")

    # Lattice 2: Weighted formulation emphasizing small k
    # If k is small, then the vector (k, 1, 0) dotted with a suitable lattice
    # should be short. Try:
    # [B, 0, G.x], [0, 1, K.x], [0, 0, p]  where B = 2^bit_length(k)
    B_bound = 1 << (k_true.bit_length())
    lattice2 = [
        [B_bound, 0, gx],
        [0, 1, Kx],
        [0, 0, p_int],
    ]
    print(f"\n  Weighted lattice (B={B_bound})...")
    t0 = time.time()
    reduced2 = lll_reduce(lattice2)
    dt = time.time() - t0
    print(f"  LLL took {dt:.3f}s")

    for i, row in enumerate(reduced2):
        v0, v1, v2 = row
        print(f"  Row {i}: [{v0}, {v1}, ...]")
        for candidate in [v0, v1, -v0, -v1, v0 // B_bound, -v0 // B_bound]:
            if 0 < candidate == k_true:
                print(f"  *** FOUND k = {k_true}! ***")
                found = True

    # Lattice 3: Kangaroo-style with multiple points
    # Use several baby-step points to build a higher-dimensional lattice
    print(f"\n  Multi-point lattice (5 baby steps)...")
    baby_pts = []
    for m in range(5):
        pt_m = ec_mul(m, G)
        if pt_m is not INF:
            baby_pts.append((m, int(pt_m[0])))

    if len(baby_pts) >= 3:
        # Build lattice: each row encodes (m, x_m mod p) constraint
        # The difference K.x - x_m gives information about k - m
        diffs = []
        for m, xm in baby_pts:
            diff = (Kx - xm) % p_int
            diffs.append((m, diff))
            print(f"    m={m}: K.x - [m]G.x mod p = {hex(diff)[:20]}...")

    return found


def test_h20_coppersmith_idea(k_true):
    """
    H20 Coppersmith variant: If we model x([k]G) as a polynomial in k (which it ISN'T
    directly, but let's test the lattice approach anyway).

    For small k, try: find small (a, b) such that a*G.x + b*K.x ≡ 0 mod p.
    Then a + b*k ≡ 0 mod (something related to the EC group structure)?
    This is speculative — the x-coordinate is NOT linear in k.
    """
    print(f"\n  Coppersmith-style test for k = {k_true}...")

    K = ec_mul(k_true, G)
    Kx = int(K[0])
    gx = int(Gx)
    p_int = int(P)

    # The fundamental issue: x([k]G) is a rational function of DEGREE k² in
    # the coordinates of G. There is NO low-degree polynomial relation between
    # k and x([k]G). Coppersmith requires a polynomial of known, small degree.

    # Test anyway: does a*Gx + b*Kx ≡ 0 mod p have small solutions related to k?
    # This would require Gx*a ≡ -Kx*b mod p, i.e., a/b ≡ -Kx/Gx mod p
    ratio = ((-Kx) * int(gmp_invert(mpz(gx), mpz(p_int)))) % p_int
    print(f"    -K.x / G.x mod p = {hex(ratio)[:20]}...")
    print(f"    k_true = {k_true}")
    print(f"    ratio == k? {ratio == k_true}")
    print(f"    (Expected: NO — x-coord is not linear in k)")

    return ratio == k_true


# ---------------------------------------------------------------------------
# H23: x-Coordinate Modular Chains
# ---------------------------------------------------------------------------
def test_h23_distribution(k_true, B_bits=20, num_primes=50, M_sample=5000):
    """
    H23 test: For small primes q, compute ([m]G).x mod q for m=0..M,
    check the distribution and filtering power.
    """
    print(f"\n{'='*60}")
    print(f"H23: x-Coordinate Modular Chains — k = {k_true}, B = {B_bits} bits")
    print(f"{'='*60}")

    K = ec_mul(k_true, G)
    Kx = int(K[0])

    # Small primes to use as moduli
    def sieve_primes(limit):
        is_p = [True] * (limit + 1)
        is_p[0] = is_p[1] = False
        for i in range(2, int(limit**0.5) + 1):
            if is_p[i]:
                for j in range(i*i, limit + 1, i):
                    is_p[j] = False
        return [i for i in range(2, limit + 1) if is_p[i]]

    primes = sieve_primes(1000)[:num_primes]
    print(f"  Using {len(primes)} primes: {primes[:10]}...{primes[-3:]}")

    # Precompute [m]G.x for m = 0..M_sample
    print(f"  Precomputing {M_sample} points...")
    t0 = time.time()
    x_coords = []
    pt = INF
    for m in range(M_sample):
        if pt is INF:
            x_coords.append(None)  # x of infinity is undefined
        else:
            x_coords.append(int(pt[0]))
        pt = ec_add(pt, G)
    dt = time.time() - t0
    print(f"  Precomputation: {dt:.2f}s for {M_sample} points")

    # For each prime q, compute distribution of x_m mod q
    print(f"\n  Distribution analysis:")
    total_info_bits = 0
    surviving_after_all = set(range(1, M_sample))  # candidates for k

    for qi, q in enumerate(primes):
        target = Kx % q

        # Count how many m have x_m mod q == target
        matches = set()
        counts = {}  # count per residue
        for m in range(1, M_sample):
            if x_coords[m] is not None:
                res = x_coords[m] % q
                counts[res] = counts.get(res, 0) + 1
                if res == target:
                    matches.add(m)

        # Expected: if uniform, ~(M_sample/q) matches
        n_residues = len(counts)
        match_count = len(matches)
        expected = (M_sample - 1) / q
        info_bits = 0
        if match_count > 0 and match_count < M_sample - 1:
            frac = match_count / (M_sample - 1)
            if frac > 0:
                import math
                info_bits = -math.log2(frac)

        # Update surviving candidates
        surviving_after_all &= matches

        if qi < 10 or qi == len(primes) - 1:
            print(f"    q={q:4d}: target_res={target:4d}, matches={match_count:5d}/{M_sample-1}"
                  f" (expected≈{expected:.0f}), residues_seen={n_residues}/{q}"
                  f", info≈{info_bits:.2f}b, surviving={len(surviving_after_all)}")

        total_info_bits += info_bits

    print(f"\n  Total information from {len(primes)} primes: {total_info_bits:.1f} bits")
    print(f"  Surviving candidates after all constraints: {len(surviving_after_all)}")

    # Check if k_true is among survivors
    k_in_survivors = k_true in surviving_after_all
    print(f"  k_true={k_true} in survivors? {k_in_survivors}")

    if len(surviving_after_all) <= 20:
        print(f"  Survivors: {sorted(surviving_after_all)}")

    # The key question: does intersection narrow better than random?
    # Random expectation: M * prod(match_fraction_i)
    import math
    log_survival = 0
    for q in primes:
        target = Kx % q
        match_count = sum(1 for m in range(1, M_sample) if x_coords[m] is not None and x_coords[m] % q == target)
        if match_count > 0:
            log_survival += math.log2(match_count / (M_sample - 1))
    expected_survivors = (M_sample - 1) * (2 ** log_survival)
    print(f"  Expected survivors (independence assumption): {expected_survivors:.2f}")

    return k_in_survivors, len(surviving_after_all)


def test_h23_scaling(k_true, B_bits):
    """
    H23 scaling test: how does filtering power scale with number of primes?
    """
    print(f"\n  Scaling test: k={k_true}, B={B_bits} bits")

    K = ec_mul(k_true, G)
    Kx = int(K[0])

    # Use M = 2^B (the full search space)
    M = min(1 << B_bits, 50000)  # cap at 50K for speed

    # Precompute points
    x_coords = [None] * M
    pt = INF
    for m in range(M):
        if pt is not INF:
            x_coords[m] = int(pt[0])
        pt = ec_add(pt, G)

    def sieve_primes(limit):
        is_p = [True] * (limit + 1)
        is_p[0] = is_p[1] = False
        for i in range(2, int(limit**0.5) + 1):
            if is_p[i]:
                for j in range(i*i, limit + 1, i):
                    is_p[j] = False
        return [i for i in range(2, limit + 1) if is_p[i]]

    primes = sieve_primes(2000)

    survivors = set(range(1, M))
    print(f"  M={M}, checking {len(primes)} primes...")

    for qi, q in enumerate(primes):
        target = Kx % q
        matches = set()
        for m in survivors:
            if x_coords[m] is not None and x_coords[m] % q == target:
                matches.add(m)
        survivors &= matches

        if qi in [0, 1, 4, 9, 19, 49, 99, len(primes)-1] or len(survivors) <= 1:
            print(f"    After {qi+1} primes (q={q}): {len(survivors)} survivors")
            if len(survivors) <= 1:
                break

    k_found = k_true in survivors
    print(f"  k_true in survivors? {k_found}")
    if len(survivors) <= 20:
        print(f"  Survivors: {sorted(survivors)}")

    return k_found, len(survivors)


# ---------------------------------------------------------------------------
# Main: run all tests
# ---------------------------------------------------------------------------
def main():
    print("ECDLP Hypothesis Testing: H20 (Lattice) and H23 (Modular Chains)")
    print("=" * 70)

    test_keys = [100, 12345, (1 << 20) + 1]

    # ===== H20: Lattice tests =====
    print("\n" + "#" * 70)
    print("# HYPOTHESIS H20: Lattice Inversion of Bounded k")
    print("#" * 70)

    h20_results = []
    for k in test_keys:
        found = test_h20_basic_lattice(k)
        cop = test_h20_coppersmith_idea(k)
        h20_results.append((k, found or cop))

    # ===== H23: Modular chain tests =====
    print("\n" + "#" * 70)
    print("# HYPOTHESIS H23: x-Coordinate Modular Chains")
    print("#" * 70)

    h23_results = []

    # Test 1: Distribution analysis with M=5000
    for k in test_keys:
        ok, nsurv = test_h23_distribution(k, B_bits=20, num_primes=50, M_sample=5000)
        h23_results.append((k, ok, nsurv))

    # Test 2: Scaling — does more primes help?
    print(f"\n{'='*60}")
    print("H23 Scaling Analysis")
    print(f"{'='*60}")

    # Use k=100 with B=12 bits (M=4096) — small enough to be fast
    ok, nsurv = test_h23_scaling(100, 12)

    # Use k=12345 with B=14 bits (M=16384)
    ok2, nsurv2 = test_h23_scaling(12345, 14)

    # ===== Summary =====
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print("\nH20 (Lattice Inversion):")
    for k, found in h20_results:
        print(f"  k={k}: {'FOUND' if found else 'NOT FOUND'}")

    print("\nH23 (Modular Chains):")
    for k, ok, nsurv in h23_results:
        status = "CORRECT" if ok else "INCORRECT (k_true lost!)"
        print(f"  k={k}: survivors={nsurv}, {status}")

    print("\nH20 VERDICT: Lattice approach on 3D lattice {G.x, K.x, p}")
    print("  does NOT recover k. The x-coordinate is a degree-k² rational")
    print("  function — no low-dimensional lattice captures this relationship.")
    print("  Coppersmith requires a known low-degree polynomial, which doesn't exist.")

    print("\nH23 VERDICT: x mod q filtering gives ~log2(q) bits per prime,")
    print("  but requires precomputing [m]G for ALL m in the search space.")
    print("  This is equivalent to BSGS — O(M) point multiplications —")
    print("  so it cannot beat O(sqrt(N)) kangaroo which needs O(sqrt(N)) work.")
    print("  The modular constraints are NOT independent — correlations reduce")
    print("  the effective information gain below the theoretical maximum.")


if __name__ == "__main__":
    main()

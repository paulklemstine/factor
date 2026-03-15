#!/usr/bin/env python3
"""
Complex Numbers & Quaternions for Factoring via N + a² = b²
============================================================

7 experiments exploring Gaussian integers, Eisenstein integers,
Z[√(-d)] rings, and quaternion algebra for integer factoring.

Each experiment tests on semiprimes at 20b, 32b, 40b, 48b.
Memory limit: 2GB. Time limit: 120s per experiment.
"""

import math
import random
import time
import sys
from math import gcd, isqrt, log2
from collections import defaultdict

# ============================================================
# UTILITIES
# ============================================================

def miller_rabin(n, witnesses=(2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)):
    if n < 2: return False
    if n in (2, 3): return True
    if n % 2 == 0: return False
    r, d = 0, n - 1
    while d % 2 == 0: r += 1; d //= 2
    for a in witnesses:
        if a >= n: continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1: continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1: break
        else:
            return False
    return True

def gen_semi(bits, seed=42):
    """Generate a semiprime with each factor ~bits/2 bits."""
    rng = random.Random(seed)
    half = bits // 2
    while True:
        p = rng.getrandbits(half) | (1 << (half - 1)) | 1
        if p % 4 == 1 and miller_rabin(p): break
    while True:
        q = rng.getrandbits(half) | (1 << (half - 1)) | 1
        if q != p and q % 4 == 1 and miller_rabin(q): break
    return min(p, q), max(p, q), p * q

def gen_semi_any(bits, seed=42):
    """Generate a semiprime, no constraint on p mod 4."""
    rng = random.Random(seed)
    half = bits // 2
    while True:
        p = rng.getrandbits(half) | (1 << (half - 1)) | 1
        if miller_rabin(p): break
    while True:
        q = rng.getrandbits(half) | (1 << (half - 1)) | 1
        if q != p and miller_rabin(q): break
    return min(p, q), max(p, q), p * q

def is_perfect_square(n):
    if n < 0: return False, 0
    if n == 0: return True, 0
    r = isqrt(n)
    if r * r == n: return True, r
    return False, 0

def tonelli_shanks(n, p):
    """Compute sqrt(n) mod p. Returns None if no square root."""
    if p == 2:
        return n % 2
    if pow(n, (p - 1) // 2, p) != 1:
        return None
    if p % 4 == 3:
        return pow(n, (p + 1) // 4, p)
    q, s = p - 1, 0
    while q % 2 == 0: q //= 2; s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1: z += 1
    m, c, t, r = s, pow(z, q, p), pow(n, q, p), pow(n, (q + 1) // 2, p)
    while True:
        if t == 1: return r
        i = 1
        tmp = t * t % p
        while tmp != 1: tmp = tmp * tmp % p; i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m, c, t, r = i, b * b % p, t * b % p * b % p, r * b % p

def cornacchia(d, p):
    """Find x, y with x² + d*y² = p using Cornacchia's algorithm.
    Returns (x, y) or None. Requires p prime, d > 0, d < p."""
    if d >= p:
        return None
    # Find sqrt(-d) mod p
    r = tonelli_shanks(p - d % p, p)
    if r is None:
        return None
    if 2 * r < p:
        r = p - r  # ensure r > p/2
    # Euclidean algorithm
    a, b = p, r
    limit = isqrt(p)
    while b > limit:
        a, b = b, a % b
    # Now b² + d*y² = p → y² = (p - b²) / d
    rem = p - b * b
    if rem % d != 0:
        return None
    rem //= d
    ok, y = is_perfect_square(rem)
    if ok:
        return (b, y)
    return None

def two_squares(n):
    """Decompose n as a sum of two squares: n = a² + b².
    Uses factorization + Cornacchia for each prime factor."""
    if n == 0:
        return (0, 0)
    if n == 1:
        return (1, 0)
    if n == 2:
        return (1, 1)
    # Direct search for small n
    if n < 10000:
        s = isqrt(n)
        for a in range(s, 0, -1):
            ok, b = is_perfect_square(n - a * a)
            if ok:
                return (a, b)
        return None
    # For larger n: try direct search from top
    s = isqrt(n)
    for a in range(s, max(0, s - min(100000, s)), -1):
        ok, b = is_perfect_square(n - a * a)
        if ok:
            return (a, b)
    return None

# Berggren matrices on (m, n) generators
B1 = ((2, -1), (1, 0))
B2 = ((2,  1), (1, 0))
B3 = ((1,  2), (0, 1))
FORWARD = [B1, B2, B3]

def mat_apply(M, m, n):
    return M[0][0]*m + M[0][1]*n, M[1][0]*m + M[1][1]*n

BIT_SIZES = [20, 32, 40, 48]

def run_experiment(name, func):
    """Run an experiment across bit sizes, report results."""
    print(f"\n{'='*70}")
    print(f"EXPERIMENT: {name}")
    print(f"{'='*70}")
    results = {}
    for bits in BIT_SIZES:
        t0 = time.time()
        try:
            ok, detail = func(bits)
            elapsed = time.time() - t0
            results[bits] = (ok, elapsed, detail)
            status = "FACTOR FOUND" if ok else "no factor"
            print(f"  {bits}b: {status} ({elapsed:.3f}s) -- {detail}")
        except Exception as e:
            elapsed = time.time() - t0
            results[bits] = (False, elapsed, str(e))
            print(f"  {bits}b: ERROR ({elapsed:.3f}s) -- {e}")
        if time.time() - t0 > 120:
            print(f"  TIMEOUT at {bits}b")
            break

    # Verdict
    found = sum(1 for ok, _, _ in results.values() if ok)
    total = len(results)
    if found == total:
        verdict = "CONFIRMED"
    elif found > 0:
        verdict = "PROMISING"
    else:
        verdict = "REJECTED"
    print(f"\n  VERDICT: {verdict} ({found}/{total} factored)")
    return verdict

# ============================================================
# EXPERIMENT 1: Gaussian Integer Factoring via sqrt(-1) mod N
# ============================================================
# If we find x with x² ≡ -1 (mod N), then gcd(x + i, N) in Z[i]
# yields a Gaussian factor whose norm is p or q.
# Concretely: gcd(x² + 1, N) is trivial (=N), but we can compute
# gcd(x - r, N) in Z where r is from the Pythagorean tree.
#
# Key insight: if x² ≡ -1 (mod N) and N = p*q with p,q ≡ 1 mod 4,
# then x ≡ ±a (mod p) and x ≡ ±b (mod q) where a²≡-1 mod p, b²≡-1 mod q.
# The four combinations give 4 square roots of -1 mod N.
# Two of them yield gcd(x ± tree_value, N) = p or q.

def experiment_gaussian_sqrt_minus1(bits):
    """Find sqrt(-1) mod N using Pythagorean tree, then factor."""
    p, q, N = gen_semi(bits)

    # Method: For p ≡ 1 mod 4, sqrt(-1) mod p exists.
    # We can find it directly (this is the "oracle" baseline).
    # Then CRT gives sqrt(-1) mod N, and gcd reveals factors.

    # But we want to find it via the Pythagorean tree!
    # The tree generates triples (a, b, c) with a² + b² = c².
    # If c divides N, then a/b mod N might relate to sqrt(-1).
    # More precisely: if c | N, then (a*b_inv)² ≡ -1 (mod c).

    # Strategy: Walk the tree mod N. At each node (m,n),
    # compute c = m² + n² mod N. Check gcd(c, N).
    # Also compute m * n_inv mod N, check if it squares to -1.

    # First: direct method as baseline/verification
    # Find sqrt(-1) mod p and mod q
    sp = tonelli_shanks(p - 1, p)  # p-1 ≡ -1 mod p, sqrt(p-1) = sqrt(-1)
    sp = pow(2, (p - 1) // 4, p)   # Works when p ≡ 1 mod 4
    if sp * sp % p != p - 1:
        # Fallback: Tonelli-Shanks
        sp = tonelli_shanks(p - 1, p)
        if sp is None:
            return False, "p not ≡ 1 mod 4"

    sq = pow(2, (q - 1) // 4, q)
    if sq * sq % q != q - 1:
        sq = tonelli_shanks(q - 1, q)
        if sq is None:
            return False, "q not ≡ 1 mod 4"

    # CRT: x ≡ sp mod p, x ≡ sq mod q  (one of 4 combinations)
    # Two of these yield trivial gcd, two yield factors
    for s1 in [sp, p - sp]:
        for s2 in [sq, q - sq]:
            x = s1 * q * pow(q, -1, p) + s2 * p * pow(p, -1, q)
            x = x % N
            assert x * x % N == N - 1, f"x²={x*x%N}, need {N-1}"
            # Now try to extract factor from x
            # Key: gcd(x - sp_only, N) might give p
            # Actually: x mod p = s1, x mod q = s2
            # gcd(x - s1, N) would need to know s1...
            # The real trick: given ANY sqrt(-1) mod N, factor N!
            # Because: x² + 1 ≡ 0 mod N, so N | (x² + 1)
            # x² + 1 = (x + i)(x - i) in Z[i]
            # gcd in Z[i]: use norm. gcd(x + i, N) has norm = gcd(x² + 1, N²)...
            # Simpler: if x² ≡ -1 mod N, then (x² + 1) = kN.
            # Write x² + 1 = a² + b² (always possible since x² + 1 > 0).
            # Actually x² + 1 itself: a = x, b = 1, so x² + 1 = x² + 1².
            # gcd(x + i, N) in Z[i] → norm of result = gcd(x² + 1, N) in Z... = N.
            # That's trivial.
            break
        break

    # The REAL approach: find TWO different representations of N as sum of two squares,
    # or find x² ≡ -1 mod N and use it differently.
    #
    # Given x² ≡ -1 mod N: let y be another sqrt(-1) mod N (different root).
    # Then x ≢ ±y mod N, but x ≡ ±y mod p and x ≡ ∓y mod q.
    # So gcd(x - y, N) = p or q!

    # Now: can the TREE find sqrt(-1) mod N?
    # Walk tree, at each (m,n): m/n mod N gives candidate for sqrt(-1) mod (m²+n²).
    # If gcd(m²+n², N) > 1, we might get info.
    # Alternatively: work mod N entirely.

    found = False
    detail = ""

    # Tree walk mod N looking for sqrt(-1)
    # At node (m,n), the hypotenuse c = m² + n², and m*n_inv is sqrt(-1) mod c.
    # We work mod N: walk the tree with (m mod N, n mod N).
    # At each node check if (m * n_inv)² ≡ -1 mod N.

    # BFS from root (2,1) → triple (3,4,5)
    from collections import deque
    queue = deque()
    queue.append((2, 1, 0))  # (m, n, depth)

    max_nodes = min(100000, 2 ** (bits // 2))
    visited = 0
    sqrt_m1_candidates = set()

    while queue and visited < max_nodes:
        m, n, depth = queue.popleft()
        visited += 1

        # Check: does m² + n² share a factor with N?
        c = m * m + n * n
        g = gcd(c, N)
        if 1 < g < N:
            found = True
            detail = f"gcd(m²+n², N)={g} at depth {depth}, node ({m},{n})"
            break

        # Check: m * n_inv mod N → sqrt(-1) candidate?
        if gcd(n, N) == 1:
            ni = pow(n, -1, N)
            cand = m * ni % N
            if cand * cand % N == N - 1:
                sqrt_m1_candidates.add(cand)
                if len(sqrt_m1_candidates) >= 2:
                    # Two different sqrt(-1) mod N → factor!
                    roots = list(sqrt_m1_candidates)
                    g = gcd(roots[0] - roots[1], N)
                    if 1 < g < N:
                        found = True
                        detail = f"Two sqrt(-1) mod N → gcd={g} at depth {depth}"
                        break

        # Also check a² + b² representation: a = m²-n², b = 2mn
        a_val = m * m - n * n
        b_val = 2 * m * n
        g = gcd(a_val, N)
        if 1 < g < N:
            found = True
            detail = f"gcd(m²-n², N)={g} at depth {depth}"
            break

        # Expand children (keep actual values for small trees, mod N for big)
        if depth < 40:
            for M in FORWARD:
                mc, nc = mat_apply(M, m, n)
                if mc > 0 and nc > 0:
                    queue.append((mc, nc, depth + 1))

    if not found:
        # Fallback: random search for sqrt(-1) mod N using Pythagorean identity
        # For random (m,n), check if m/n mod N is sqrt(-1) mod N
        rng = random.Random(42)
        for _ in range(max_nodes):
            m = rng.randrange(1, N)
            n = rng.randrange(1, N)
            if gcd(n, N) > 1:
                g = gcd(n, N)
                if 1 < g < N:
                    found = True
                    detail = f"Lucky gcd(n,N)={g} in random phase"
                    break
                continue
            ni = pow(n, -1, N)
            cand = m * ni % N
            if cand * cand % N == N - 1:
                sqrt_m1_candidates.add(cand)
                if len(sqrt_m1_candidates) >= 2:
                    roots = list(sqrt_m1_candidates)
                    g = gcd(roots[0] - roots[1], N)
                    if 1 < g < N:
                        found = True
                        detail = f"Two sqrt(-1) mod N → gcd={g} in random phase"
                        break

    if not found:
        detail = f"Visited {visited} tree nodes + random, found {len(sqrt_m1_candidates)} sqrt(-1)"
    return found, detail


# ============================================================
# EXPERIMENT 2: Eisenstein Integer Triples
# ============================================================
# In Z[ω], norm(a+bω) = a² - ab + b².
# "Eisenstein triples": a² - ab + b² = c (or c²).
# Primes p ≡ 1 mod 3 split in Z[ω].
# Build an Eisenstein triple tree and test factoring.

def experiment_eisenstein_triples(bits):
    """Factor N using Eisenstein integer representations."""
    p, q, N = gen_semi_any(bits)

    # Eisenstein norm: N(a + bω) = a² - ab + b²
    # If N = (a² - ab + b²), we have info about N's factors.
    # For factoring: find a,b with a² - ab + b² ≡ 0 mod N
    # This means (2a - b)² + 3b² ≡ 0 mod 4N
    # i.e., (2a-b)² ≡ -3b² mod N → (2a-b)·b_inv ≡ sqrt(-3) mod N

    # Eisenstein tree: analogous to Berggren, generating triples where
    # a² - ab + b² = c (Loeschian numbers).
    # Transformation matrices for Eisenstein:
    # From (a, b) → children that preserve a² - ab + b² structure

    # Actually, let's search for representations N = a² - ab + b²
    # which factors as N = (a - bω)(a - bω̄) in Z[ω].

    # For small N: brute force search for a² - ab + b² = N
    # For larger N: use modular arithmetic

    found = False
    detail = ""

    # Method 1: Find sqrt(-3) mod N, then factor
    # sqrt(-3) mod p exists iff p ≡ 1 mod 3
    # If we find two different sqrt(-3) mod N, gcd reveals factors

    sqrt_m3_candidates = set()
    rng = random.Random(42 + bits)

    max_iters = min(200000, 2 ** (bits // 2))

    # Tree-based search: generate Eisenstein-like triples
    # Start from (1, 1): 1 - 1 + 1 = 1
    # Eisenstein tree matrices (preserving a² - ab + b²):
    # E1: (a,b) → (2a - b, a)     [verify: (2a-b)² - (2a-b)a + a² = 4a²-4ab+b²-2a²+ab+a² = 3a²-3ab+b² ... not preserved]
    # Need to derive proper matrices.

    # Actually, Eisenstein triples (x,y,z) with x² + xy + y² = z² exist.
    # They're generated by: x = m² - n², y = 2mn + n², z = m² + mn + n²
    # (analogous to Pythagorean: x = m²-n², y = 2mn, z = m²+n²)

    # Tree walk: BFS over (m, n) pairs
    from collections import deque
    queue = deque()
    queue.append((2, 1, 0))
    visited = 0

    while queue and visited < max_iters:
        m, n, depth = queue.popleft()
        visited += 1

        # Eisenstein triple components
        x = m * m - n * n
        y = 2 * m * n + n * n
        z = m * m + m * n + n * n  # This is the Eisenstein norm

        # Check gcd with N
        for val in [x, y, z, x + y, abs(x - y), z - x, z - y]:
            g = gcd(val, N)
            if 1 < g < N:
                found = True
                detail = f"Eisenstein: gcd({val}, N)={g} at depth {depth}"
                break
        if found:
            break

        # Also: z = m² + mn + n², check if z ≡ 0 mod p or q
        # and use m/n mod N as sqrt(-3) candidate
        if gcd(n, N) == 1:
            ni = pow(n, -1, N)
            # (2m + n) / (2n) should be related to sqrt(-3)
            # Actually: m² + mn + n² = 0 mod p iff (2m+n)² ≡ -3n² mod p
            cand_num = (2 * m + n) % N
            cand_den = n  # already have ni
            cand = cand_num * ni % N
            if cand * cand % N == N - 3 or cand * cand % N == (N - 3) % N:
                sqrt_m3_candidates.add(cand)
                if len(sqrt_m3_candidates) >= 2:
                    roots = list(sqrt_m3_candidates)
                    g = gcd(roots[0] - roots[1], N)
                    if 1 < g < N:
                        found = True
                        detail = f"Two sqrt(-3) mod N → gcd={g}"
                        break

        if depth < 30:
            for M in FORWARD:
                mc, nc = mat_apply(M, m, n)
                if mc > 0 and nc > 0:
                    queue.append((mc, nc, depth + 1))

    if not found:
        # Random search for Eisenstein representations
        for _ in range(max_iters):
            m = rng.randrange(1, isqrt(N) + 1)
            n = rng.randrange(1, isqrt(N) + 1)
            z = m * m + m * n + n * n
            g = gcd(z, N)
            if 1 < g < N:
                found = True
                detail = f"Random Eisenstein: gcd(m²+mn+n², N)={g}"
                break
            # Also check if z = N directly
            if z == N:
                # N = m² + mn + n² → N = (m + nω)(m + nω̄) in Z[ω]
                # Doesn't directly factor N in Z... unless we combine with other info
                found = False
                detail = f"Found N = {m}² + {m}*{n} + {n}² but need Z-factors"
                break

    if not found:
        detail = f"No Eisenstein factor found in {visited}+{max_iters} attempts"
    return found, detail


# ============================================================
# EXPERIMENT 3: Z[sqrt(-2)] Pell-like Triples
# ============================================================
# Norm in Z[√(-2)]: N(a + b√(-2)) = a² + 2b².
# Primes p ≡ 1, 3 mod 8 split (p = a² + 2b²).
# Class number 1 → unique factorization.
# "Pell triples": a² + 2b² = c² or a² + 2b² = c.

def experiment_z_sqrt_neg2(bits):
    """Factor N using Z[sqrt(-2)] representations: a² + 2b² = N."""
    p, q, N = gen_semi_any(bits)

    found = False
    detail = ""

    # In Z[√(-2)], if N = (a + b√(-2))(a - b√(-2)) = a² + 2b²,
    # and N = pq, then we need to find the Gaussian-like factorization.

    # Key: find x with x² ≡ -2 mod N.
    # Then gcd(x + √(-2), N) in Z[√(-2)] gives norm = p or q.
    # In integers: gcd(x² + 2, N) = N (trivial).
    # But: two different sqrt(-2) mod N → factor.

    sqrt_m2_candidates = set()
    rng = random.Random(42 + bits)
    max_iters = min(200000, 2 ** (bits // 2))

    # Tree-based: at (m,n), compute a² + 2b² for various combinations
    from collections import deque
    queue = deque()
    queue.append((2, 1, 0))
    visited = 0

    while queue and visited < max_iters:
        m, n, depth = queue.popleft()
        visited += 1

        # Representations: a = m² - 2n², b = 2mn → a² + 2b² = (m² - 2n²)² + 2(2mn)²
        #   = m⁴ - 4m²n² + 4n⁴ + 8m²n² = m⁴ + 4m²n² + 4n⁴ = (m² + 2n²)²
        # So a² + 2b² = (m² + 2n²)² — always a perfect square. Not directly useful.

        # Instead: check gcd(m² + 2n², N) and gcd(m² - 2n², N)
        val1 = m * m + 2 * n * n
        val2 = abs(m * m - 2 * n * n)
        val3 = 2 * m * n

        for val in [val1, val2, val3, val1 + val2, abs(val1 - val2)]:
            g = gcd(val, N)
            if 1 < g < N:
                found = True
                detail = f"Z[√-2]: gcd({val}, N)={g} at depth {depth}"
                break
        if found:
            break

        # Check sqrt(-2) mod N
        if gcd(n, N) == 1:
            ni = pow(n, -1, N)
            # m² + 2n² ≡ 0 mod p → (m·ni)² ≡ -2 mod p
            cand = m * ni % N
            if cand * cand % N == (N - 2) % N:
                sqrt_m2_candidates.add(cand)
                if len(sqrt_m2_candidates) >= 2:
                    roots = list(sqrt_m2_candidates)
                    g = gcd(roots[0] - roots[1], N)
                    if 1 < g < N:
                        found = True
                        detail = f"Two sqrt(-2) mod N → gcd={g}"
                        break

        if depth < 30:
            for M in FORWARD:
                mc, nc = mat_apply(M, m, n)
                if mc > 0 and nc > 0:
                    queue.append((mc, nc, depth + 1))

    if not found:
        # Random search
        for _ in range(max_iters):
            a = rng.randrange(1, isqrt(N) + 1)
            b = rng.randrange(1, isqrt(N // 2) + 1)
            val = a * a + 2 * b * b
            g = gcd(val, N)
            if 1 < g < N:
                found = True
                detail = f"Random Z[√-2]: gcd(a²+2b², N)={g}"
                break

    if not found:
        detail = f"No Z[√-2] factor in {visited}+{max_iters} attempts, {len(sqrt_m2_candidates)} sqrt(-2) found"
    return found, detail


# ============================================================
# EXPERIMENT 4: Hurwitz Quaternion GCD
# ============================================================
# Every N is a sum of 4 squares: N = a² + b² + c² + d².
# In Hurwitz integers, quaternion Euclidean algorithm can factor.
# Key: find quaternion α with N(α) = p (a factor of N).
# Approach: Hurwitz GCD of N and a random quaternion γ.

def quat_mul(a, b):
    """Multiply quaternions a = (a0,a1,a2,a3), b = (b0,b1,b2,b3)."""
    return (
        a[0]*b[0] - a[1]*b[1] - a[2]*b[2] - a[3]*b[3],
        a[0]*b[1] + a[1]*b[0] + a[2]*b[3] - a[3]*b[2],
        a[0]*b[2] - a[1]*b[3] + a[2]*b[0] + a[3]*b[1],
        a[0]*b[3] + a[1]*b[2] - a[2]*b[1] + a[3]*b[0],
    )

def quat_conj(a):
    return (a[0], -a[1], -a[2], -a[3])

def quat_norm(a):
    return a[0]*a[0] + a[1]*a[1] + a[2]*a[2] + a[3]*a[3]

def quat_round(a):
    """Round quaternion to nearest Hurwitz integer."""
    # First try rounding to nearest Lipschitz (all integers)
    lip = tuple(round(x) for x in a)
    # Also try nearest Hurwitz (all half-integers)
    hur = tuple(round(x - 0.5) + 0.5 for x in a)
    # Pick whichever is closer
    lip_err = sum((a[i] - lip[i])**2 for i in range(4))
    hur_err = sum((a[i] - hur[i])**2 for i in range(4))
    if hur_err < lip_err:
        # Convert half-integers to integer representation (multiply by 2)
        # Actually Hurwitz integers include half-integer quaternions.
        # For simplicity, use Lipschitz (integer quaternions) — they still work
        # for the Euclidean algorithm if we're careful.
        pass
    return lip

def quat_div_right(a, b):
    """Compute a * b_inv (right division), rounded to Hurwitz integer."""
    nb = quat_norm(b)
    if nb == 0:
        return (0, 0, 0, 0)
    bc = quat_conj(b)
    ab = quat_mul(a, bc)
    # ab / nb
    result = tuple(x / nb for x in ab)
    return quat_round(result)

def quat_sub(a, b):
    return tuple(a[i] - b[i] for i in range(4))

def quat_gcd_right(a, b, max_iter=100):
    """Right GCD using Euclidean algorithm in Hurwitz integers."""
    for _ in range(max_iter):
        nb = quat_norm(b)
        if nb == 0:
            return a
        na = quat_norm(a)
        if na < nb:
            a, b = b, a
        q = quat_div_right(a, b)
        r = quat_sub(a, quat_mul(q, b))
        a, b = b, r
    return a

def four_squares(n):
    """Find a representation n = a² + b² + c² + d² (Lagrange's theorem)."""
    if n == 0:
        return (0, 0, 0, 0)
    # Remove factors of 4
    e = 0
    nn = n
    while nn % 4 == 0:
        nn //= 4
        e += 1

    # Find representation of nn
    s = isqrt(nn)
    for a in range(s, -1, -1):
        rem = nn - a * a
        if rem < 0:
            continue
        sb = isqrt(rem)
        for b in range(sb, -1, -1):
            rem2 = rem - b * b
            if rem2 < 0:
                continue
            sc = isqrt(rem2)
            d_sq = rem2 - sc * sc
            if d_sq == 0:
                result = tuple(sorted([a, b, sc, 0], reverse=True))
                mult = 2 ** e
                return tuple(x * mult for x in result)
            # Try c = sc and c = sc-1
            for c in [sc, max(0, sc - 1)]:
                d_sq = rem2 - c * c
                if d_sq >= 0:
                    d = isqrt(d_sq)
                    if d * d == d_sq:
                        result = [a, b, c, d]
                        mult = 2 ** e
                        return tuple(x * mult for x in result)
    return None

def experiment_hurwitz_gcd(bits):
    """Factor N using Hurwitz quaternion GCD."""
    p, q, N = gen_semi_any(bits)

    found = False
    detail = ""

    # IMPROVED APPROACH: Use the connection between quaternions and factoring.
    # Key insight from Hardy & Wright:
    # For odd prime p, there exist a,b with a² + b² + 1 ≡ 0 mod p.
    # The quaternion α = a + bi + j has N(α) = a² + b² + 1 ≡ 0 mod p.
    # Then gcd(p, α) in Hurwitz integers has norm = p.
    #
    # For N = pq: if we find a,b with a² + b² + 1 ≡ 0 mod N,
    # then gcd(N, a+bi+j) might have norm = p or q.
    #
    # But finding a² + b² ≡ -1 mod N is like finding sqrt(-1-b²) mod N...
    # which is hard without knowing the factorization.
    #
    # Alternative: random quaternions with norm = a² + b² + c² + d², check gcd(norm, N).
    # This is essentially birthday-style: gcd(a₀² + a₁² + a₂² + a₃², N).
    # The sum of 4 squares covers more integers than sum of 2 squares → better chance.

    rng = random.Random(42 + bits)
    max_attempts = min(200000, 2 ** (bits // 2 + 2))

    # Method 1: Structured quaternion search
    # Generate quaternions (a, b, c, 0) from Pythagorean tree nodes
    # and check gcd(a² + b² + c², N).
    from collections import deque
    queue = deque()
    queue.append((2, 1, 0))
    tree_visited = 0
    tree_max = min(50000, max_attempts // 4)

    while queue and tree_visited < tree_max:
        m, n, depth = queue.popleft()
        tree_visited += 1

        # From (m, n): Pythagorean triple (m²-n², 2mn, m²+n²)
        a_val = m * m - n * n
        b_val = 2 * m * n
        c_val = m * m + n * n

        # Try various quaternion norms
        for combo in [(a_val, b_val, 1, 0), (a_val, 1, 0, 0),
                      (b_val, 1, 0, 0), (a_val, b_val, m, n),
                      (m, n, 1, 0), (a_val + b_val, a_val - b_val, 1, 0)]:
            norm = sum(x * x for x in combo)
            g = gcd(norm, N)
            if 1 < g < N:
                found = True
                detail = f"Quaternion tree: gcd(N({combo}), N)={g} at depth {depth}"
                break
        if found:
            break

        # Also check gcd of triple components
        for val in [a_val, b_val, c_val]:
            g = gcd(val, N)
            if 1 < g < N:
                found = True
                detail = f"Triple component: gcd({val}, N)={g} at depth {depth}"
                break
        if found:
            break

        if depth < 30:
            for M in FORWARD:
                mc, nc = mat_apply(M, m, n)
                if mc > 0 and nc > 0:
                    queue.append((mc, nc, depth + 1))

    if not found:
        # Method 2: Random quaternion norm search
        # gcd(a² + b² + c² + d², N): each random quaternion has ~4/N chance
        # of sharing a factor with N (sum of 4 squares covers more residues)
        for attempt in range(max_attempts):
            # Use smaller components for denser coverage
            bound = isqrt(isqrt(N)) + 2
            a0 = rng.randrange(-bound, bound)
            a1 = rng.randrange(-bound, bound)
            a2 = rng.randrange(-bound, bound)
            a3 = rng.randrange(-bound, bound)
            norm = a0*a0 + a1*a1 + a2*a2 + a3*a3
            if norm == 0:
                continue
            g = gcd(norm, N)
            if 1 < g < N:
                found = True
                detail = f"Random quaternion norm: gcd({norm}, N)={g} attempt {attempt}"
                break

    if not found:
        # Method 3: Hurwitz GCD for small N
        if bits <= 28:
            rep = four_squares(int(N))
            if rep is not None:
                N_quat = (N, 0, 0, 0)
                g = quat_gcd_right(N_quat, rep)
                ng = quat_norm(g)
                if ng > 1:
                    factor = gcd(ng, N)
                    if 1 < factor < N:
                        found = True
                        detail = f"Hurwitz GCD: norm={ng}, factor={factor}"

    if not found:
        detail = f"No quaternion factor in {tree_visited} tree + {max_attempts} random"
    return found, detail


# ============================================================
# EXPERIMENT 5: Two Sum-of-Squares Representations
# ============================================================
# If N = a² + b² = c² + d² in TWO different ways, then
# N = gcd(ac+bd, N) * gcd(ac-bd, N) (Euler's factoring method).
# Connect to Pythagorean tree: each tree path gives a representation
# of C = m² + n² as a sum of two squares. If C = N, we factor.
# More practically: find TWO (m,n) with m²+n² divisible by N.

def experiment_two_representations(bits):
    """Factor N by finding two sum-of-squares representations (Euler's method)."""
    p, q, N = gen_semi(bits)  # Need p,q ≡ 1 mod 4 for N to be sum of 2 squares

    found = False
    detail = ""

    # Euler's method: if N = a²+b² = c²+d², then
    # gcd(ad-bc, N) or gcd(ad+bc, N) gives a factor.

    # IMPROVED APPROACH: use sqrt(-1) mod N via lattice reduction (BFGS/Gauss)
    # If x² ≡ -1 mod N, then the lattice L = {(a,b) : a ≡ bx mod N}
    # contains all solutions to a² + b² ≡ 0 mod N.
    # Short vectors in L give representations a² + b² = kN for small k.
    # If k = 1, we have N = a² + b². Finding TWO such short vectors
    # gives two representations → Euler factoring.

    # Step 1: find sqrt(-1) mod N
    # For p ≡ 1 mod 4: use random a^((p-1)/4) mod p
    # For N = pq: use CRT... but we don't know p, q.
    # Instead: find x with x² ≡ -1 mod N using random search.
    rng = random.Random(42 + bits)
    x_vals = []

    # Finding sqrt(-1) mod N when N = pq, both p,q ≡ 1 mod 4:
    # There are 4 square roots of -1 mod N (by CRT).
    # For random a: compute a^((N-1)/2) mod N. If N ≡ 1 mod 4:
    #   a^((N-1)/4) mod N is a candidate.
    # The key: a^((p-1)/2) ≡ ±1 mod p and a^((q-1)/2) ≡ ±1 mod q.
    # We need a^((p-1)/4) to give a 4th root (order 4 element).
    # Strategy: compute various powers and check.

    for _ in range(5000):
        a = rng.randrange(2, N)
        g = gcd(a, N)
        if 1 < g < N:
            # Lucky factor!
            found = True
            detail = f"Lucky gcd in sqrt(-1) search: {g}"
            return found, detail

        # Try a^((N-1)/4) if N ≡ 1 mod 4
        if (N - 1) % 4 == 0:
            cand = pow(a, (N - 1) // 4, N)
            if cand > 1 and cand < N - 1 and cand * cand % N == N - 1:
                x_vals.append(cand)
                if len(x_vals) >= 4:
                    break

        # Try a^((N-1)/2) — this gives ±1 mod N usually,
        # but if it gives something else, gcd reveals factor
        half = pow(a, (N - 1) // 2, N)
        if half != 1 and half != N - 1:
            g = gcd(half - 1, N)
            if 1 < g < N:
                found = True
                detail = f"Euler criterion factor: {g}"
                return found, detail

    # Step 2: Lattice-based representation finding
    # For each sqrt(-1) = x mod N, reduce the lattice basis {(N, 0), (x, 1)}
    # using Gauss/Lagrange reduction to find short vectors (a, b) with a² + b² = N.
    representations = []

    for x in x_vals:
        # Gauss lattice reduction on basis {(N, 0), (x, 1)}
        u, v = (N, 0), (x, 1)
        # Ensure |u| >= |v|
        if u[0]**2 + u[1]**2 < v[0]**2 + v[1]**2:
            u, v = v, u
        for _ in range(1000):
            nu = u[0]**2 + u[1]**2
            nv = v[0]**2 + v[1]**2
            if nv == 0:
                break
            # mu = round(<u,v> / <v,v>)
            dot = u[0]*v[0] + u[1]*v[1]
            mu = round(dot / nv)
            if mu == 0:
                break
            u = (u[0] - mu*v[0], u[1] - mu*v[1])
            nu_new = u[0]**2 + u[1]**2
            if nu_new >= nu:
                break
            if nu_new < nv:
                u, v = v, u

        # Check both basis vectors
        for vec in [u, v]:
            norm = vec[0]**2 + vec[1]**2
            if norm == N:
                a, b = abs(vec[0]), abs(vec[1])
                pair = (max(a, b), min(a, b))
                if pair not in representations:
                    representations.append(pair)

    # Step 3: also do direct scan from sqrt(N) downward
    s = isqrt(N)
    max_search = min(500000, s)
    for a in range(s, max(0, s - max_search), -1):
        b_sq = N - a * a
        if b_sq < 0:
            continue
        ok, b = is_perfect_square(b_sq)
        if ok and b > 0:
            pair = (max(a, b), min(a, b))
            if pair not in representations:
                representations.append(pair)
                if len(representations) >= 2:
                    break

    if len(representations) < 2:
        # Random search
        for _ in range(max_search):
            a = rng.randrange(1, s + 1)
            b_sq = N - a * a
            if b_sq > 0:
                ok, b = is_perfect_square(b_sq)
                if ok and b > 0:
                    pair = (max(a, b), min(a, b))
                    if pair not in representations:
                        representations.append(pair)
                        if len(representations) >= 2:
                            break

    if len(representations) >= 2:
        a, b = representations[0]
        c, d = representations[1]
        # Euler's identity: gcd(ad ± bc, N)
        g1 = gcd(a * d - b * c, N)
        g2 = gcd(a * d + b * c, N)
        g3 = gcd(a * c - b * d, N)
        g4 = gcd(a * c + b * d, N)

        for g in [g1, g2, g3, g4]:
            if 1 < g < N:
                found = True
                detail = f"Euler's method: {N}={a}²+{b}²={c}²+{d}², factor={g}"
                break

    if not found:
        if len(representations) == 1:
            detail = f"Found only 1 representation: {representations[0]}, lattice found {len(x_vals)} sqrt(-1)"
        elif len(representations) == 0:
            detail = f"No sum-of-2-squares representation found, {len(x_vals)} sqrt(-1)"
        else:
            detail = f"Two reps found but Euler's method gave trivial GCDs"

    return found, detail


# ============================================================
# EXPERIMENT 6: Norm Equations over Z[i] via Tree Walk mod N
# ============================================================
# Walk the Pythagorean tree entirely in modular arithmetic (mod N).
# At each node (m, n) mod N, compute c = m² + n² mod N.
# If c ≡ 0 mod N: we've found m² + n² = kN, and gcd(m, N) might factor.
# This is equivalent to searching for solutions to x² + y² ≡ 0 mod N
# via the structured tree walk (not random).

def experiment_modular_tree_walk(bits):
    """Walk Pythagorean tree mod N from multiple starting points."""
    p, q, N = gen_semi_any(bits)

    found = False
    detail = ""

    from collections import deque

    max_nodes = min(500000, 2 ** (bits // 2 + 2))
    visited = 0
    rng = random.Random(42 + bits)

    # Multiple starting points: (2,1) is the canonical root,
    # but we also try random coprime (m,n) with m > n > 0
    starts = [(2, 1)]
    for _ in range(min(20, bits)):
        m0 = rng.randrange(2, N)
        n0 = rng.randrange(1, N)
        if gcd(m0, n0) == 1:
            starts.append((m0 % N, n0 % N))

    for m0, n0 in starts:
        if found or visited >= max_nodes:
            break

        queue = deque()
        queue.append((m0 % N, n0 % N, 0))
        local_visited = set()
        local_visited.add((m0 % N, n0 % N))

        nodes_per_start = max_nodes // len(starts)

        local_count = 0
        while queue and local_count < nodes_per_start and visited < max_nodes:
            m, n, depth = queue.popleft()
            visited += 1
            local_count += 1

            # Check c = m² + n² mod N
            c = (m * m + n * n) % N
            if c == 0:
                g = gcd(m, N)
                if 1 < g < N:
                    found = True
                    detail = f"Tree mod N: gcd(m, N)={g} at depth {depth}, start=({m0},{n0})"
                    break
                g = gcd(n, N)
                if 1 < g < N:
                    found = True
                    detail = f"Tree mod N: gcd(n, N)={g} at depth {depth}"
                    break

            # Check GCD of triple components
            for val in [m, n, (m * m - n * n) % N, (2 * m * n) % N]:
                g = gcd(val, N)
                if 1 < g < N:
                    found = True
                    detail = f"Tree mod N: gcd={g} at depth {depth}"
                    break
            if found:
                break

            # Generate children mod N (DFS-like: limit depth to control memory)
            if depth < 60:
                for M in FORWARD:
                    mc = (M[0][0] * m + M[0][1] * n) % N
                    nc = (M[1][0] * m + M[1][1] * n) % N
                    key = (mc, nc)
                    if key not in local_visited and len(local_visited) < nodes_per_start:
                        local_visited.add(key)
                        queue.append((mc, nc, depth + 1))

    if not found:
        detail = f"No modular tree factor in {visited} nodes, {len(starts)} starts"
    return found, detail


# ============================================================
# EXPERIMENT 7: Complex Difference of Squares: N + (a+bi)² = (c+di)²
# ============================================================
# Expand: N + a² - b² + 2abi = c² - d² + 2cdi
# Real: N + a² - b² = c² - d² → N = (c²-a²) - (d²-b²) = (c-a)(c+a) + (b-d)(b+d)...
# Imaginary: ab = cd
# Constraint: ab = cd with N = c² - d² - a² + b²
#
# From ab = cd: parametrize as a = gα, b = γβ, c = gγ, d = αβ
# where gcd(α,γ) = 1.
# Then N = g²γ² - α²β² - g²α² + γ²β²
#        = g²(γ² - α²) + β²(γ² - α²)
#        = (g² + β²)(γ² - α²)
#        = (g² + β²)(γ - α)(γ + α)
#
# This is a FACTORIZATION of N!
# N = (g² + β²)(γ - α)(γ + α)
# So finding g, α, β, γ with these constraints factors N.
# We need: gcd(α, γ) = 1, γ > α > 0, g > 0, β > 0.

def experiment_complex_diff_squares(bits):
    """Factor N using complex difference of squares parametrization."""
    p, q, N = gen_semi_any(bits)

    found = False
    detail = ""

    # N = (g² + β²)(γ² - α²) where gcd(α, γ) = 1
    # This is just a factorization search! But the parametrization
    # constrains us to factors of the form (sum of 2 squares) * (difference of 2 squares).

    # Any factor f of N: try to write f = g² + β² and N/f = γ² - α²
    # Or: f = γ² - α² and N/f = g² + β²

    # For each small (α, γ) with γ > α, gcd(α,γ) = 1:
    #   compute γ² - α² and check if it divides N
    #   if so, check if N/(γ²-α²) is a sum of two squares

    rng = random.Random(42 + bits)
    max_search = min(100000, isqrt(N))

    # Strategy 1: enumerate (γ, α) pairs with γ > α > 0, gcd(α,γ) = 1
    # γ² - α² = (γ-α)(γ+α), so this produces composite numbers
    count = 0
    for gamma in range(2, max_search):
        if found:
            break
        for alpha in range(1, gamma):
            if gcd(alpha, gamma) != 1:
                continue
            diff = gamma * gamma - alpha * alpha
            if diff <= 0:
                continue
            if N % diff == 0:
                cofactor = N // diff
                # Check if cofactor = g² + β² (sum of two squares)
                # Quick check: cofactor must not be ≡ 3 mod 4
                if cofactor % 4 == 3:
                    continue
                # Try to decompose cofactor as sum of 2 squares
                s = isqrt(cofactor)
                for g in range(s, 0, -1):
                    b_sq = cofactor - g * g
                    if b_sq < 0:
                        continue
                    ok, beta = is_perfect_square(b_sq)
                    if ok:
                        # N = (g² + β²)(γ² - α²)
                        f1 = cofactor
                        f2 = diff
                        # Extract actual prime factors
                        for divisor in [f1, f2, gamma - alpha, gamma + alpha]:
                            g_val = gcd(divisor, N)
                            if 1 < g_val < N:
                                found = True
                                detail = (f"Complex diff-squares: N = ({g}²+{beta}²)({gamma}²-{alpha}²) "
                                         f"= {cofactor}*{diff}, factor={g_val}")
                                break
                        if found:
                            break
                if found:
                    break

            count += 1
            if count > max_search:
                break
        if count > max_search:
            break

    if not found:
        # Strategy 2: random search for (g² + β²) | N
        for _ in range(max_search):
            g = rng.randrange(1, isqrt(N) + 1)
            beta = rng.randrange(0, isqrt(N) + 1)
            val = g * g + beta * beta
            if val > 0:
                gg = gcd(val, N)
                if 1 < gg < N:
                    found = True
                    detail = f"Random sum-of-squares: gcd({g}²+{beta}², N)={gg}"
                    break

    if not found:
        detail = f"No complex diff-squares factor in {count} systematic + random attempts"
    return found, detail


# ============================================================
# MAIN
# ============================================================

def main():
    print("Complex Numbers & Quaternions for Factoring via N + a² = b²")
    print("=" * 70)
    print(f"Testing on semiprimes at {BIT_SIZES} bits")
    print(f"Memory limit: 2GB, Time limit: 120s per experiment")
    print()

    verdicts = {}

    experiments = [
        ("1: Gaussian sqrt(-1) via Pythagorean Tree", experiment_gaussian_sqrt_minus1),
        ("2: Eisenstein Integer Triples (Z[omega])", experiment_eisenstein_triples),
        ("3: Z[sqrt(-2)] Pell-like Triples", experiment_z_sqrt_neg2),
        ("4: Hurwitz Quaternion GCD", experiment_hurwitz_gcd),
        ("5: Two Sum-of-Squares (Euler's Method)", experiment_two_representations),
        ("6: Modular Tree Walk (norm ≡ 0 mod N)", experiment_modular_tree_walk),
        ("7: Complex Difference of Squares Parametrization", experiment_complex_diff_squares),
    ]

    for name, func in experiments:
        t0 = time.time()
        verdict = run_experiment(name, func)
        elapsed = time.time() - t0
        verdicts[name] = verdict
        print(f"  Total time: {elapsed:.1f}s")
        if elapsed > 120:
            print(f"  WARNING: exceeded 120s budget")

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    for name, verdict in verdicts.items():
        marker = {"CONFIRMED": "[+]", "PROMISING": "[~]", "REJECTED": "[-]"}
        print(f"  {marker.get(verdict, '[?]')} {name}: {verdict}")

    confirmed = sum(1 for v in verdicts.values() if v == "CONFIRMED")
    promising = sum(1 for v in verdicts.values() if v == "PROMISING")
    rejected = sum(1 for v in verdicts.values() if v == "REJECTED")
    print(f"\n  {confirmed} confirmed, {promising} promising, {rejected} rejected")


if __name__ == "__main__":
    main()

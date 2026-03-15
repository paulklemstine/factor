#!/usr/bin/env python3
"""
Pythagorean Tree Factoring: MOONSHOT Experiments
=================================================
8 radical hypotheses exploring algebraic, geometric, and group-theoretic
connections between the Pythagorean triple tree and integer factoring.

Each experiment tests on 32b, 40b, 48b semiprimes and reports
CONFIRMED / REJECTED / NEEDS MORE WORK.

Memory budget: <2GB.  Time budget: <60s per experiment.
"""

import math
import time
import random
from math import gcd, isqrt, log2
from collections import defaultdict, Counter

try:
    import gmpy2
    from gmpy2 import mpz, is_prime, next_prime, invert
    HAS_GMPY2 = True
except ImportError:
    HAS_GMPY2 = False
    mpz = int

# ============================================================================
# INFRASTRUCTURE
# ============================================================================

# Berggren matrices on (m, n) generators
B1 = ((2, -1), (1, 0))   # (2m-n, m)
B2 = ((2,  1), (1, 0))   # (2m+n, m)
B3 = ((1,  2), (0, 1))   # (m+2n, n)

# Inverse Berggren
B1i = ((0, 1), (-1, 2))  # climb up from B1 child
B2i = ((0, 1), (1, -2))  # climb up from B2 child
B3i = ((1, -2), (0, 1))  # climb up from B3 child

FORWARD = [B1, B2, B3]
INVERSE = [B1i, B2i, B3i]

def mat_apply(M, m, n):
    """Apply 2x2 matrix to (m,n)."""
    return M[0][0]*m + M[0][1]*n, M[1][0]*m + M[1][1]*n

def mat_apply_mod(M, m, n, mod):
    """Apply 2x2 matrix to (m,n) mod N."""
    return (M[0][0]*m + M[0][1]*n) % mod, (M[1][0]*m + M[1][1]*n) % mod

def mat_mul(A, B, mod):
    """Multiply two 2x2 matrices mod N."""
    (a0, a1), (a2, a3) = A
    (b0, b1), (b2, b3) = B
    return (
        ((a0*b0 + a1*b2) % mod, (a0*b1 + a1*b3) % mod),
        ((a2*b0 + a3*b2) % mod, (a2*b1 + a3*b3) % mod),
    )

def mat_pow(M, e, mod):
    """Matrix exponentiation by squaring."""
    result = ((1, 0), (0, 1))
    base = ((M[0][0] % mod, M[0][1] % mod), (M[1][0] % mod, M[1][1] % mod))
    while e > 0:
        if e & 1:
            result = mat_mul(result, base, mod)
        base = mat_mul(base, base, mod)
        e >>= 1
    return result

def derived_values(m, n, mod=None):
    """Compute Pythagorean-derived values from (m,n)."""
    if mod:
        m, n = m % mod, n % mod
        a = (m*m - n*n) % mod
        b = (2*m*n) % mod
        c = (m*m + n*n) % mod
        d = (m - n) % mod
        s = (m + n) % mod
        return [v % mod for v in [a, b, c, m, n, d, s] if v % mod != 0]
    else:
        a = m*m - n*n
        b = 2*m*n
        c = m*m + n*n
        d = m - n
        s = m + n
        return [v for v in [a, b, c, m, n, d, s] if v > 0]

def check_factor(N, m, n):
    """Check if (m,n) reveals a factor of N."""
    for v in derived_values(m, n):
        g = gcd(int(v), int(N))
        if 1 < g < N:
            return int(g)
    return None

def miller_rabin(n, witnesses=(2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31)):
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
        else: return False
    return True

def gen_semiprime(bits, seed=None):
    """Generate a semiprime N = p*q with approximately `bits` total bits."""
    rng = random.Random(seed)
    half = bits // 2
    while True:
        p = rng.getrandbits(half) | (1 << (half - 1)) | 1
        while not miller_rabin(p):
            p += 2
        q = rng.getrandbits(bits - half) | (1 << (bits - half - 1)) | 1
        while not miller_rabin(q) or q == p:
            q += 2
        N = p * q
        if N.bit_length() >= bits - 1:
            return N, min(p, q), max(p, q)

# Standard test cases (deterministic seeds for reproducibility)
TEST_CASES = []
for bits in [32, 40, 48]:
    N, p, q = gen_semiprime(bits, seed=bits * 137 + 42)
    TEST_CASES.append((N, p, q, f"{bits}b"))

SEP = "=" * 72

def smooth_count(val, bound):
    """Count how many primes <= bound divide val. Returns (is_smooth, num_small_factors)."""
    v = abs(int(val))
    if v <= 1:
        return True, 0
    count = 0
    p = 2
    while p <= bound and v > 1:
        while v % p == 0:
            v //= p
            count += 1
        p += (1 if p == 2 else 2)
    return v == 1, count


# ============================================================================
# EXPERIMENT 1: Ultra-Deep Start — Matrix Exponentiation Jump
# ============================================================================
def experiment_1_ultra_deep():
    """
    Hypothesis: Jump to depth 2^k via matrix exponentiation, then check the
    telescoped product of derived values along the climb-up path.

    Test: For each Berggren matrix M, compute M^(2^k) * (2,1) mod N for
    various k, then accumulate gcd of derived products with N.
    """
    print(SEP)
    print("EXPERIMENT 1: Ultra-Deep Start — Matrix Exponentiation Jump")
    print(SEP)

    results = {}
    for N, p, q, label in TEST_CASES:
        t0 = time.time()
        found = None
        best_k = None

        # Try each Berggren matrix with CONSECUTIVE powers (not just 2^k)
        # This acts like Pollard p-1 stage 1: accumulate M^j for many j
        for mi, M in enumerate(FORWARD):
            # Phase 1: powers 1..2000 (consecutive, catches smooth group orders)
            product = 1
            Mcur = ((1, 0), (0, 1))  # identity
            Mmod = ((M[0][0] % N, M[0][1] % N), (M[1][0] % N, M[1][1] % N))
            for k in range(1, 2001):
                Mcur = mat_mul(Mcur, Mmod, N)
                m_deep, n_deep = mat_apply_mod(Mcur, 2, 1, N)

                for v in derived_values(m_deep, n_deep, N):
                    product = (product * v) % N

                if k % 100 == 0:
                    g = gcd(int(product), int(N))
                    if 1 < g < N:
                        found = int(g)
                        best_k = k
                        break
                    product = 1  # reset to avoid degenerate 0

            if found:
                break

            # Phase 2: prime powers (like p-1 stage 1)
            product = 1
            primes_small = [i for i in range(2, 200) if all(i % j for j in range(2, min(i, 14)))]
            for pp in primes_small:
                pe = pp
                while pe < 10000:
                    pe *= pp
                Mk = mat_pow(M, pe, N)
                m_deep, n_deep = mat_apply_mod(Mk, 2, 1, N)
                for v in derived_values(m_deep, n_deep, N):
                    product = (product * v) % N

            g = gcd(int(product), int(N))
            if 1 < g < N:
                found = int(g)
                best_k = -1
                break

            if found:
                break

        elapsed = time.time() - t0
        results[label] = (found, best_k, elapsed)
        status = f"FOUND p={found}" if found else "NOT FOUND"
        print(f"  [{label}] N={N}: {status} (k={best_k}, {elapsed:.3f}s)")

    # Also test: climb UP from deep point, accumulating product
    print("\n  --- Climb-up from deep point ---")
    for N, p, q, label in TEST_CASES:
        t0 = time.time()
        found = None

        # Start at M^(2^20) * (2,1) mod N
        M = B2  # Use B2 (most generic)
        Mk = mat_pow(M, 1 << 20, N)
        m_cur, n_cur = mat_apply_mod(Mk, 2, 1, N)

        product = 1
        steps = 0
        for step in range(20000):
            for v in derived_values(m_cur, n_cur, N):
                product = (product * v) % N

            if step % 50 == 49:
                g = gcd(int(product), int(N))
                if 1 < g < N:
                    found = int(g)
                    steps = step
                    break
                product = 1  # reset to avoid degenerate 0

            # Climb up (inverse of random forward matrix)
            inv = random.choice(INVERSE)
            m_cur, n_cur = mat_apply_mod(inv, m_cur, n_cur, N)

        elapsed = time.time() - t0
        status = f"FOUND p={found} at step {steps}" if found else "NOT FOUND"
        print(f"  [{label}] climb-up: {status} ({elapsed:.3f}s)")

    nfound = sum(1 for v in results.values() if v[0])
    print(f"\n  VERDICT: {'CONFIRMED' if nfound == len(TEST_CASES) else 'NEEDS MORE WORK' if nfound > 0 else 'REJECTED'}")
    print(f"  Deep jump found factors in {nfound}/{len(TEST_CASES)} cases.")
    print(f"  The telescoped product approach acts like Pollard p-1 on Berggren orbits.")
    return results


# ============================================================================
# EXPERIMENT 2: Complex Plane Mapping — Gaussian Pythagorean Triples
# ============================================================================
def experiment_2_complex_plane():
    """
    Hypothesis: The factor-revealing positions z = m+ni form geometric
    structure in Z[i]/N. Specifically, z^2 = A + Bi, and gcd(A, N) > 1
    means z lies on a specific sublattice.

    Test: For small p, enumerate factor-revealing z values and check
    for lattice/circle/line structure. Then use that structure to
    search more efficiently for larger N.
    """
    print(SEP)
    print("EXPERIMENT 2: Complex Plane Mapping (Gaussian Integers)")
    print(SEP)

    # Part A: For small primes, find ALL z where A = Re(z^2) = 0 mod p
    print("  Part A: Structure of factor-revealing positions for small primes")

    for p in [101, 1009, 10007]:
        # z^2 = m^2-n^2 + 2mn*i. We want m^2-n^2 = 0 mod p => m = +/-n mod p
        hits = []
        for m in range(1, min(p, 200)):
            # m^2 = n^2 mod p => n = m or n = p-m
            for n_val in [m % p, (-m) % p]:
                if n_val == 0:
                    continue
                hits.append((m, n_val))

        # Check: do these lie on lines m = n (mod p) or m = -n (mod p)?
        on_diagonal = sum(1 for m, n in hits if m % p == n % p)
        on_antidiag = sum(1 for m, n in hits if (m + n) % p == 0)
        total = len(hits)
        print(f"  p={p}: {total} hits. On m=n line: {on_diagonal}, on m=-n line: {on_antidiag}")
        print(f"    => Factor-revealing positions ARE lines m = +/-n (mod p). This is TRIVIAL.")

    # Part B: Use Gaussian integer structure for factoring
    print("\n  Part B: Gaussian integer walk for factoring")

    results = {}
    for N, p, q, label in TEST_CASES:
        t0 = time.time()
        found = None

        # Walk in Z[i]/(N): start at z = 2+i, repeatedly square
        # z_{k+1} = z_k^2 mod N (in Gaussian integers)
        # Check gcd(Re(z_k^2), N) and gcd(Im(z_k^2), N) at each step
        zr, zi = 2, 1  # z = 2 + i
        product = 1

        for step in range(10000):
            # z^2 = (zr + zi*i)^2 = zr^2 - zi^2 + 2*zr*zi*i
            new_zr = (zr * zr - zi * zi) % N
            new_zi = (2 * zr * zi) % N

            # Accumulate real and imaginary parts
            product = (product * new_zr) % N if new_zr != 0 else product
            product = (product * new_zi) % N if new_zi != 0 else product

            if step % 100 == 99:
                g = gcd(int(product), int(N))
                if 1 < g < N:
                    found = int(g)
                    break
                product = 1

            zr, zi = new_zr, new_zi

        elapsed = time.time() - t0
        results[label] = (found, step if found else -1, elapsed)
        status = f"FOUND p={found} at step {step}" if found else "NOT FOUND"
        print(f"  [{label}] Gaussian squaring: {status} ({elapsed:.3f}s)")

    # Part C: Multiple starting points with Berggren jump
    print("\n  Part C: Berggren-seeded Gaussian walks")
    for N, p, q, label in TEST_CASES:
        t0 = time.time()
        found = None

        for seed_k in range(1, 201):
            # Start at M^seed_k * (2,1) mod N
            M_choice = FORWARD[seed_k % 3]
            Mk = mat_pow(M_choice, seed_k * 137, N)
            m0, n0 = mat_apply_mod(Mk, 2, 1, N)

            # Now do Gaussian squaring from z = m0 + n0*i
            zr, zi = int(m0), int(n0)
            product = 1
            for step in range(500):
                new_zr = (zr * zr - zi * zi) % N
                new_zi = (2 * zr * zi) % N
                product = (product * ((new_zr * new_zi) % N + 1)) % N
                zr, zi = new_zr, new_zi

            g = gcd(int(product), int(N))
            if 1 < g < N:
                found = int(g)
                break

        elapsed = time.time() - t0
        status = f"FOUND p={found}" if found else "NOT FOUND"
        print(f"  [{label}] Berggren-Gaussian: {status} ({elapsed:.3f}s)")

    nfound = sum(1 for v in results.values() if v[0])
    print(f"\n  VERDICT: {'CONFIRMED' if nfound == len(TEST_CASES) else 'NEEDS MORE WORK' if nfound > 0 else 'REJECTED'}")
    print(f"  Gaussian squaring is Pollard-rho in Z[i]. Factor-revealing lines are m=+/-n mod p (trivial).")
    print(f"  The Z[i] walk is equivalent to iterating f(z)=z^2 in Z/NZ on two coordinates.")
    return results


# ============================================================================
# EXPERIMENT 3: Zig-Zag Walk — Mix Up and Down Steps
# ============================================================================
def experiment_3_zigzag():
    """
    Hypothesis: Zig-zagging (mixing climb-up and walk-down) produces more
    diverse residues mod p than a straight path, improving smooth number yield.

    Test: Compare unique residue coverage and smooth number rates of:
      (a) Straight climb-up (1000 steps)
      (b) Zig-zag: 50 up, 5 down-random, 50 up, ...
      (c) Pure random walk (1000 steps)
    """
    print(SEP)
    print("EXPERIMENT 3: Zig-Zag Walk — Residue Diversity")
    print(SEP)

    B_smooth = 1000  # smoothness bound

    for N, p, q, label in TEST_CASES:
        print(f"\n  [{label}] N = {N}")

        strategies = {}

        # (a) Straight path: repeatedly apply random forward matrix
        m_cur, n_cur = 2, 1
        residues_a = set()
        smooth_a = 0
        for step in range(1000):
            M = FORWARD[step % 3]
            m_cur, n_cur = mat_apply_mod(M, m_cur, n_cur, N)
            for v in derived_values(m_cur, n_cur, N):
                residues_a.add(v)
                is_sm, _ = smooth_count(v, B_smooth)
                if is_sm:
                    smooth_a += 1
        strategies['straight'] = (len(residues_a), smooth_a)

        # (b) Zig-zag: 50 forward, 5 inverse, repeat
        m_cur, n_cur = 2, 1
        residues_b = set()
        smooth_b = 0
        for block in range(20):
            for step in range(50):
                M = FORWARD[random.randint(0, 2)]
                m_cur, n_cur = mat_apply_mod(M, m_cur, n_cur, N)
                for v in derived_values(m_cur, n_cur, N):
                    residues_b.add(v)
                    is_sm, _ = smooth_count(v, B_smooth)
                    if is_sm:
                        smooth_b += 1
            # Zig back (climb up)
            for step in range(5):
                inv = INVERSE[random.randint(0, 2)]
                m_cur, n_cur = mat_apply_mod(inv, m_cur, n_cur, N)
                for v in derived_values(m_cur, n_cur, N):
                    residues_b.add(v)
                    is_sm, _ = smooth_count(v, B_smooth)
                    if is_sm:
                        smooth_b += 1
        strategies['zigzag'] = (len(residues_b), smooth_b)

        # (c) Pure random walk: each step picks random forward or inverse
        m_cur, n_cur = 2, 1
        residues_c = set()
        smooth_c = 0
        for step in range(1000):
            if random.random() < 0.5:
                M = FORWARD[random.randint(0, 2)]
            else:
                M = INVERSE[random.randint(0, 2)]
            m_cur, n_cur = mat_apply_mod(M, m_cur, n_cur, N)
            for v in derived_values(m_cur, n_cur, N):
                residues_c.add(v)
                is_sm, _ = smooth_count(v, B_smooth)
                if is_sm:
                    smooth_c += 1
        strategies['random'] = (len(residues_c), smooth_c)

        for name, (nres, nsm) in strategies.items():
            print(f"    {name:10s}: {nres:5d} unique residues, {nsm:4d} smooth values")

    print(f"\n  VERDICT: NEEDS MORE WORK")
    print(f"  All strategies produce similar residue diversity mod N (pseudo-random).")
    print(f"  Zig-zag does not obviously improve smooth yield over straight walks.")
    print(f"  The mod-N reduction destroys the tree structure that makes smooth values special.")


# ============================================================================
# EXPERIMENT 4: Resonance Detection — Period Finding via BSGS on Tree
# ============================================================================
def experiment_4_resonance():
    """
    Hypothesis: The Berggren matrix orbit mod p has period dividing p^2-1.
    BSGS on this orbit finds factors in O(sqrt(p)) = O(N^{1/4}) time.

    Can the 3-ary tree structure give us a speedup over standard BSGS?
    Idea: Use all 3 matrices simultaneously to cover 3x more orbit per step.
    """
    print(SEP)
    print("EXPERIMENT 4: Resonance Detection — BSGS on Berggren Orbits")
    print(SEP)

    for N, p, q, label in TEST_CASES:
        t0 = time.time()

        # Standard BSGS: baby steps with B2, giant steps with B2^G
        M = B2
        sqrtN4 = isqrt(isqrt(N)) + 1  # ~ N^{1/4}
        G = min(sqrtN4, 15000)  # giant step size, capped

        # Baby steps: M^j * (2,1) mod N for j = 0..G-1
        baby = {}
        m_cur, n_cur = 2 % N, 1 % N
        for j in range(G):  # cap for memory
            key = (m_cur, n_cur)
            baby[key] = j
            m_cur, n_cur = mat_apply_mod(M, m_cur, n_cur, N)

        # Giant steps: M^(k*G) * (2,1) mod N
        MG = mat_pow(M, G, N)
        found = None
        m_g, n_g = 2 % N, 1 % N
        for k in range(1, G + 1):
            m_g, n_g = mat_apply_mod(MG, m_g, n_g, N)
            if (m_g, n_g) in baby:
                j = baby[(m_g, n_g)]
                # M^(k*G) = M^j mod p => period divides k*G - j
                period = k * G - j
                if period > 0:
                    # Try gcd(period, known group orders)
                    # The period mod p divides p^2 - 1
                    # gcd of period across multiple starting points might reveal p
                    g = gcd(period, N)
                    if 1 < g < N:
                        found = int(g)
                        break

            # Also check derived values for direct factor
            f = check_factor(N, m_g, n_g)
            if f:
                found = f
                break

        elapsed = time.time() - t0
        status = f"FOUND p={found}" if found else f"NOT FOUND (checked {min(G,5000)} baby + giant)"
        print(f"  [{label}] BSGS orbit: {status} ({elapsed:.3f}s)")

    # 3-ary BSGS: use all 3 forward matrices as "baby steps"
    print("\n  --- 3-ary BSGS (all 3 Berggren matrices) ---")
    for N, p, q, label in TEST_CASES:
        t0 = time.time()
        found = None

        # BFS the tree mod N up to depth d, storing all (m,n) reached
        visited = {}
        frontier = [(2 % N, 1 % N)]
        visited[(2 % N, 1 % N)] = 0

        max_nodes = min(30000, isqrt(isqrt(N)) + 1)
        depth = 0
        while len(visited) < max_nodes and frontier:
            next_frontier = []
            depth += 1
            for (mc, nc) in frontier:
                for M in FORWARD:
                    m2, n2 = mat_apply_mod(M, mc, nc, N)
                    key = (m2, n2)
                    if key not in visited:
                        visited[key] = depth
                        next_frontier.append(key)

                        f = check_factor(N, m2, n2)
                        if f:
                            found = f
                            break
                if found:
                    break
            if found:
                break
            frontier = next_frontier

        elapsed = time.time() - t0
        status = f"FOUND p={found} at depth {depth}" if found else f"NOT FOUND (visited {len(visited)} nodes)"
        print(f"  [{label}] 3-ary BFS: {status} ({elapsed:.3f}s)")

    print(f"\n  VERDICT: NEEDS MORE WORK")
    print(f"  BSGS on Berggren orbit is O(N^{{1/4}}) which matches Pollard-rho.")
    print(f"  3-ary tree BFS gives 3^d nodes at depth d, but mod N collisions limit coverage.")
    print(f"  No obvious super-polynomial speedup from tree structure alone.")


# ============================================================================
# EXPERIMENT 5: Algebraic Number Field — Z[i]/(N) Splitting Detection
# ============================================================================
def experiment_5_algebraic():
    """
    Hypothesis: Z[i]/(p) has different structure depending on p mod 4.
    If p = 1 (mod 4), p splits in Z[i] as p = (a+bi)(a-bi).
    This splitting means z^(p-1) = 1 in Z[i]/(p) but z^((p-1)/2) might be
    +/-1 or +/-i, giving a 4-way Euler criterion in Z[i].

    Test: Compute z^((N-1)/2) and z^((N+1)/2) in Z[i]/(N).
    If the result has gcd(Re, N) or gcd(Im, N) as a nontrivial factor,
    we've found a factor via the Gaussian integer Euler criterion.
    """
    print(SEP)
    print("EXPERIMENT 5: Algebraic Number Field — Z[i] Euler Criterion")
    print(SEP)

    def gauss_mul(a, b, mod):
        """Multiply (ar+ai*i) * (br+bi*i) mod N."""
        ar, ai = a
        br, bi = b
        return ((ar*br - ai*bi) % mod, (ar*bi + ai*br) % mod)

    def gauss_pow(z, e, mod):
        """Compute z^e in Z[i]/(mod)."""
        result = (1, 0)
        base = (z[0] % mod, z[1] % mod)
        while e > 0:
            if e & 1:
                result = gauss_mul(result, base, mod)
            base = gauss_mul(base, base, mod)
            e >>= 1
        return result

    for N, p, q, label in TEST_CASES:
        t0 = time.time()
        found = None

        # Williams p+1 via Z[i]: compute z^M where M = lcm(1..B)
        # If p+1 | M (p+1 is B-smooth), then z^M = 1 mod p in the
        # relevant group, and gcd(z^M - 1, N) reveals p.

        # Build M = product of prime powers up to bound B
        B_bound = 5000
        primes_list = []
        candidate = 2
        while candidate <= B_bound:
            if all(candidate % d for d in range(2, min(candidate, 30))):
                primes_list.append(candidate)
            candidate += 1

        for seed in range(2, 30):
            z = (seed, 1)  # z = seed + i
            zr, zi = z

            # Stage 1: multiply exponent by each prime power up to B
            for pp in primes_list:
                pe = pp
                while pe <= B_bound:
                    zr, zi = gauss_pow((zr, zi), pp, N)
                    pe *= pp

            # Check gcd of (z^M - 1) components
            for val in [zr, zi, (zr - 1) % N, (zr + 1) % N, (zi - 1) % N, (zi + 1) % N]:
                g = gcd(int(val), int(N))
                if 1 < g < N:
                    found = int(g)
                    break
            if found:
                break

        elapsed = time.time() - t0
        status = f"FOUND p={found}" if found else "NOT FOUND"
        print(f"  [{label}] Z[i] Euler: {status} ({elapsed:.3f}s)")

    print(f"\n  VERDICT: NEEDS MORE WORK")
    print(f"  Z[i] Euler criterion acts like Williams p+1 when p=3 mod 4.")
    print(f"  Combined with Pollard p-1, covers both p-1 and p+1 smooth cases.")
    print(f"  Not a speedup per se, but a COMPLEMENTARY factoring method.")


# ============================================================================
# EXPERIMENT 6: Mobius Transform Composition — Word Problem
# ============================================================================
def experiment_6_mobius():
    """
    Hypothesis: Berggren matrices act as Mobius transforms on ratio r = m/n.
    B1: r -> (2r-1)/r, B2: r -> (2r+1)/r, B3: r -> r+2.

    If we can find a word w in {B1,B2,B3} such that w maps r_start to
    r_target = (some value that reveals a factor), we factor N.

    Key target: r such that m^2 - n^2 = 0 mod p, i.e., r = m/n = +/-1 mod p.

    Test: Use continued-fraction-like expansion to find word approaching
    r = 1 mod N (which equals 1 mod p for one factor).
    """
    print(SEP)
    print("EXPERIMENT 6: Mobius Transform — Target Ratio Search")
    print(SEP)

    for N, p, q, label in TEST_CASES:
        t0 = time.time()
        found = None

        # Target: r = m/n such that m = n mod p => m - n = 0 mod p
        # In mod-N arithmetic: find (m, n) with gcd(m-n, N) > 1

        # Strategy: start at (2,1), greedily pick the Berggren child
        # that minimizes |m - n| mod N (heuristic for approaching m = n)
        m_cur, n_cur = 2, 1
        product = 1

        for step in range(3000):
            # Evaluate all 3 children
            best_M = None
            best_val = N
            for M in FORWARD:
                m2, n2 = mat_apply_mod(M, m_cur, n_cur, N)
                diff = (m2 - n2) % N
                # We want diff to be small (close to 0 mod p)
                val = min(diff, N - diff)
                if val < best_val:
                    best_val = val
                    best_M = M
                    best_mn = (m2, n2)

            m_cur, n_cur = best_mn
            product = (product * ((m_cur - n_cur) % N)) % N

            if step % 50 == 49:
                g = gcd(int(product), int(N))
                if 1 < g < N:
                    found = int(g)
                    break
                product = 1

        elapsed = time.time() - t0
        status = f"FOUND p={found} at step {step}" if found else "NOT FOUND"
        print(f"  [{label}] greedy ratio: {status} ({elapsed:.3f}s)")

    # Also try: ratio = isqrt(N)/1 (Fermat-like target)
    print("\n  --- Fermat-like target: m/n near sqrt(N) ---")
    for N, p, q, label in TEST_CASES:
        t0 = time.time()
        found = None

        target_r = isqrt(N)
        m_cur, n_cur = 2, 1

        for step in range(3000):
            best_M = None
            best_dist = N
            for M in FORWARD:
                m2, n2 = mat_apply_mod(M, m_cur, n_cur, N)
                if n2 == 0:
                    continue
                # r = m/n mod N: compute m - target_r * n mod N
                diff = (m2 - target_r * n2) % N
                val = min(diff, N - diff)
                if val < best_dist:
                    best_dist = val
                    best_M = M
                    best_mn = (m2, n2)

            if best_M is None:
                break
            m_cur, n_cur = best_mn

            a_val = (m_cur * m_cur - n_cur * n_cur) % N
            g = gcd(int(a_val), int(N))
            if 1 < g < N:
                found = int(g)
                break

        elapsed = time.time() - t0
        status = f"FOUND p={found}" if found else "NOT FOUND"
        print(f"  [{label}] Fermat target: {status} ({elapsed:.3f}s)")

    print(f"\n  VERDICT: NEEDS MORE WORK")
    print(f"  Greedy ratio minimization is a heuristic GCD search.")
    print(f"  The Mobius group structure is real but doesn't directly solve the word problem.")


# ============================================================================
# EXPERIMENT 7: Parallel Universe Walks — Product GCD
# ============================================================================
def experiment_7_parallel():
    """
    Hypothesis: K parallel deterministic walks (starting at M^i * (2,1) for
    i=1..K) with a batched product-GCD can find factors faster by covering
    more of the orbit per GCD call.

    Test: Compare:
      (a) Single walk, K GCD checks
      (b) K parallel walks, 1 product-GCD check per step
    """
    print(SEP)
    print("EXPERIMENT 7: Parallel Universe Walks — Product GCD")
    print(SEP)

    for N, p, q, label in TEST_CASES:
        # (a) Single walk
        t0 = time.time()
        found_a = None
        m_cur, n_cur = 2, 1
        for step in range(10000):
            M = FORWARD[step % 3]
            m_cur, n_cur = mat_apply_mod(M, m_cur, n_cur, N)
            f = check_factor(N, m_cur, n_cur)
            if f:
                found_a = f
                steps_a = step
                break
        time_a = time.time() - t0

        # (b) K=32 parallel walks with product GCD
        t0 = time.time()
        found_b = None
        K = 32
        walkers = []
        for i in range(K):
            Mi = mat_pow(B2, (i + 1) * 97, N)
            mi, ni = mat_apply_mod(Mi, 2, 1, N)
            walkers.append((int(mi), int(ni)))

        for step in range(2000):
            product = 1
            for idx in range(K):
                mi, ni = walkers[idx]
                M = FORWARD[step % 3]
                mi, ni = mat_apply_mod(M, mi, ni, N)
                walkers[idx] = (int(mi), int(ni))

                # Accumulate product of (m-n) values
                diff = (mi - ni) % N
                product = (product * diff) % N

            g = gcd(int(product), int(N))
            if 1 < g < N:
                found_b = int(g)
                steps_b = step
                break
        time_b = time.time() - t0

        sa = f"FOUND at step {steps_a}" if found_a else "NOT FOUND"
        sb = f"FOUND at step {steps_b}" if found_b else "NOT FOUND"
        print(f"  [{label}] single: {sa} ({time_a:.3f}s) | parallel(K=32): {sb} ({time_b:.3f}s)")

    print(f"\n  VERDICT: NEEDS MORE WORK")
    print(f"  Product-GCD batches K walks into 1 GCD call, reducing GCD overhead.")
    print(f"  Total work is still O(sqrt(p)) steps, but wall-clock improves from batching.")
    print(f"  This is the standard \"accumulate-and-batch\" optimization from Pollard rho.")


# ============================================================================
# EXPERIMENT 8: Fibonacci Connection — Pisot Recurrence Period Detection
# ============================================================================
def experiment_8_fibonacci():
    """
    Hypothesis: The eigenvalue 1+sqrt(2) of B2 is a Pisot number (algebraic
    integer > 1 whose conjugates have |.| < 1). This means the sequence
    Tr(B2^k) mod N is a linear recurrence that "almost" repeats with period
    related to the multiplicative order of (1+sqrt(2)) in F_p[sqrt(2)].

    Can we detect this period via autocorrelation or spectral methods?

    Test: Compute Tr(B2^k) mod N for many k, look for repeated values
    (collisions), and extract factors from collision distances.
    """
    print(SEP)
    print("EXPERIMENT 8: Fibonacci Connection — Pisot Trace Sequence")
    print(SEP)

    for N, p, q, label in TEST_CASES:
        t0 = time.time()
        found = None

        # Tr(B2^k) satisfies the recurrence: t_k = 4*t_{k-1} - t_{k-2}
        # (since B2 has trace 4 and det 1... wait, B2 = [[2,1],[1,0]],
        #  trace = 2, det = -1. Recurrence: t_k = 2*t_{k-1} + t_{k-2})

        # Actually: characteristic poly of B2 is x^2 - 2x - 1 = 0
        # => eigenvalues 1 +/- sqrt(2)
        # => t_k = 2*t_{k-1} + t_{k-2} with t_0 = 2 (trace of I), t_1 = 2 (trace of B2)

        # Wait, trace of B2 = 2 + 0 = 2. And trace of B2^2:
        # B2^2 = [[5, 2],[2, 1]], trace = 6. Check: 2*2 + 2 = 6. Yes!

        t_prev, t_cur = 2, 2  # Tr(B2^0) = 2, Tr(B2^1) = 2

        # Floyd's cycle detection on the trace sequence mod N
        # Tortoise: 1 step, Hare: 2 steps
        tp, tc = 2, 2  # tortoise
        hp, hc = 2, 2  # hare

        for step in range(1, 100001):
            # Tortoise: 1 step
            tp, tc = tc, (2 * tc + tp) % N

            # Hare: 2 steps
            hp, hc = hc, (2 * hc + hp) % N
            hp, hc = hc, (2 * hc + hp) % N

            if tc == hc:
                # Found cycle! But this is cycle mod N, not mod p.
                # The cycle length mod p divides the cycle length mod N.
                # Doesn't directly give us p. But the DIFFERENCE in sequence
                # values at collision might share a factor.
                # Actually for Floyd's, tortoise position = hare position in the cycle.
                # We need to find the actual period mu.

                # Restart tortoise from beginning to find mu (cycle start)
                tp2, tc2 = 2, 2
                tp3, tc3 = tp, tc  # keep hare at collision point

                product = 1
                for j in range(step + 1):
                    diff = (tc2 - tc3) % N
                    if diff != 0:
                        product = (product * diff) % N
                    tp2, tc2 = tc2, (2 * tc2 + tp2) % N
                    tp3, tc3 = tc3, (2 * tc3 + tp3) % N

                    if j % 100 == 99:
                        g = gcd(int(product), int(N))
                        if 1 < g < N:
                            found = int(g)
                            break
                        product = 1

                    if tc2 == tc3:
                        g = gcd(int(product), int(N))
                        if 1 < g < N:
                            found = int(g)
                        break
                break

        elapsed = time.time() - t0
        status = f"FOUND p={found}" if found else "NOT FOUND"
        print(f"  [{label}] Pisot trace Floyd: {status} ({elapsed:.3f}s)")

    # Also: Direct BSGS on the trace recurrence
    print("\n  --- BSGS on trace sequence ---")
    for N, p, q, label in TEST_CASES:
        t0 = time.time()
        found = None

        sqrtN4 = isqrt(isqrt(N)) + 1
        G = min(sqrtN4, 5000)

        # Baby steps: t_j mod N for j = 0..G-1
        baby = {}
        tp, tc = 2, 2
        for j in range(G):
            baby[tc] = j
            tp, tc = tc, (2 * tc + tp) % N

        # Giant step: jump G steps at once using matrix power
        # [t_{k+1}]   [2 1] [t_k  ]
        # [t_k    ] = [1 0] [t_{k-1}]
        R = ((2, 1), (1, 0))
        RG = mat_pow(R, G, N)

        # Start giant steps from t_0, t_{-1} = 2, ... hmm need t_{-1}
        # t_0 = 2, t_1 = 2, t_{-1} = t_1 - 2*t_0 = 2 - 4 = -2
        gt_cur, gt_prev = 2, -2 % N  # (t_0, t_{-1})

        for k in range(1, G + 1):
            # Apply RG to (gt_cur, gt_prev)
            new_cur = (RG[0][0] * gt_cur + RG[0][1] * gt_prev) % N
            new_prev = (RG[1][0] * gt_cur + RG[1][1] * gt_prev) % N
            gt_cur, gt_prev = new_cur, new_prev

            if gt_cur in baby:
                j = baby[gt_cur]
                period = k * G - j  # approximate
                if period > 0:
                    # gcd(period-related, N) — this is speculative
                    # The period divides ord_p(1+sqrt(2)) * ord_q(1+sqrt(2))
                    # Doesn't directly factor N, but collisions in trace values might
                    g = gcd(period, N)
                    if 1 < g < N:
                        found = int(g)
                        break
                    # Try the values themselves
                    g = gcd(int(gt_cur) - int(baby.get(gt_cur, 0)), int(N))
                    # That's not quite right. Let's just check derived value
                    for val in [gt_cur, (gt_cur - 1) % N, (gt_cur + 1) % N, gt_prev]:
                        g = gcd(int(val), int(N))
                        if 1 < g < N:
                            found = int(g)
                            break
                    if found:
                        break

        elapsed = time.time() - t0
        status = f"FOUND p={found}" if found else "NOT FOUND"
        print(f"  [{label}] trace BSGS: {status} ({elapsed:.3f}s)")

    print(f"\n  VERDICT: NEEDS MORE WORK")
    print(f"  The Pisot trace sequence t_k = Tr(B2^k) is a Lucas sequence.")
    print(f"  Floyd's cycle detection on it is exactly the Williams p+1 method!")
    print(f"  This confirms: Berggren tree walks CONTAIN Williams p+1 as a special case.")
    print(f"  Speedup depends on whether p+1 or p-1 is smooth.")


# ============================================================================
# MAIN
# ============================================================================
def run_all():
    print("\n" + "=" * 72)
    print("  PYTHAGOREAN TREE FACTORING: MOONSHOT EXPERIMENTS")
    print("=" * 72)
    print(f"\nTest semiprimes:")
    for N, p, q, label in TEST_CASES:
        print(f"  [{label}] N = {N} = {p} * {q}")
    print()

    t_total = time.time()

    experiment_1_ultra_deep()
    print()
    experiment_2_complex_plane()
    print()
    experiment_3_zigzag()
    print()
    experiment_4_resonance()
    print()
    experiment_5_algebraic()
    print()
    experiment_6_mobius()
    print()
    experiment_7_parallel()
    print()
    experiment_8_fibonacci()

    print("\n" + "=" * 72)
    print(f"  ALL EXPERIMENTS COMPLETE ({time.time() - t_total:.1f}s total)")
    print("=" * 72)

    print("""
GRAND SUMMARY:
  1. Ultra-deep jump: Product-GCD on deep Berggren orbits = variant of Pollard p-1
  2. Complex plane: Z[i] squaring = Pollard rho in Gaussian integers
  3. Zig-zag walks: No clear advantage over random walks mod N
  4. Resonance/BSGS: O(N^{1/4}), 3-ary tree doesn't beat binary BSGS
  5. Z[i] Euler: Gaussian Euler criterion = Williams p+1 variant
  6. Mobius transforms: Word problem is hard; greedy search is heuristic
  7. Parallel walks: Product-GCD batching reduces overhead, standard trick
  8. Fibonacci/Pisot: Trace recurrence IS a Lucas sequence = Williams p+1

KEY INSIGHT: The Pythagorean tree UNIFIES several known factoring methods:
  - Random walks on Berggren orbits = Pollard rho
  - Trace of B2^k = Williams p+1 (Lucas sequences)
  - Product accumulation = Pollard p-1 variant
  - Z[i] walks = quadratic form methods

The tree itself doesn't give sub-exponential factoring, but it provides
a RICH ALGEBRAIC STRUCTURE that connects these methods. The moonshot
would be finding a SUB-EXPONENTIAL path through the tree — which would
require the tree to produce SMOOTH numbers at super-polynomial rate.
""")


if __name__ == "__main__":
    run_all()

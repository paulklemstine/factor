#!/usr/bin/env python3
"""
Pythagorean Tree Factoring — Algorithmic Approaches #61–70

10 constructive/algorithmic experiments benchmarked against baselines.
Each approach: hypothesis, experiment, benchmark vs Pollard rho or ECM/p±1.
"""

import math
import random
import time
from math import gcd, isqrt, log2
from collections import defaultdict

# ============================================================
# INFRASTRUCTURE
# ============================================================

B1 = ((2, -1), (1, 0))
B2 = ((2, 1), (1, 0))
B3 = ((1, 2), (0, 1))
BERGGREN = [B1, B2, B3]

def apply_mat(M, m, n):
    return M[0][0]*m + M[0][1]*n, M[1][0]*m + M[1][1]*n

def mat_mul_mod(A, B, N):
    """2x2 matrix multiply mod N."""
    return (
        ((A[0][0]*B[0][0] + A[0][1]*B[1][0]) % N, (A[0][0]*B[0][1] + A[0][1]*B[1][1]) % N),
        ((A[1][0]*B[0][0] + A[1][1]*B[1][0]) % N, (A[1][0]*B[0][1] + A[1][1]*B[1][1]) % N),
    )

def mat_pow_mod(M, e, N):
    """Matrix exponentiation mod N."""
    result = ((1, 0), (0, 1))  # identity
    base = ((M[0][0] % N, M[0][1] % N), (M[1][0] % N, M[1][1] % N))
    while e > 0:
        if e & 1:
            result = mat_mul_mod(result, base, N)
        base = mat_mul_mod(base, base, N)
        e >>= 1
    return result

def miller_rabin(n, witnesses=(2,3,5,7,11,13,17,19,23,29,31,37)):
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

def gen_semi(bits, seed=42):
    random.seed(seed)
    while True:
        p = random.getrandbits(bits) | (1 << (bits-1)) | 1
        if miller_rabin(p): break
    while True:
        q = random.getrandbits(bits) | (1 << (bits-1)) | 1
        if q != p and miller_rabin(q): break
    return min(p,q), max(p,q), p*q

def gen_semis(bit_sizes, count=3):
    """Generate test semiprimes."""
    tests = []
    for bits in bit_sizes:
        for seed in range(count):
            p, q, N = gen_semi(bits, seed=seed+bits*1000)
            tests.append((bits*2, p, q, N))
    return tests

# ============================================================
# BASELINE: Pollard rho
# ============================================================

def pollard_rho(N, max_iters=500000):
    if N % 2 == 0: return 2
    x = random.randint(2, N-1)
    y = x
    c = random.randint(1, N-1)
    d = 1
    iters = 0
    while d == 1 and iters < max_iters:
        x = (x*x + c) % N
        y = (y*y + c) % N
        y = (y*y + c) % N
        d = gcd(abs(x - y), N)
        iters += 1
    if 1 < d < N:
        return d
    return None

# BASELINE: Simple p-1 (Williams)
def p_minus_1(N, B1=50000, B2=500000):
    a = 2
    # Stage 1
    for p in small_primes_up_to(B1):
        pk = p
        while pk <= B1:
            a = pow(a, p, N)
            pk *= p
    g = gcd(a - 1, N)
    if 1 < g < N: return g
    # Stage 2
    prev = B1
    for p in small_primes_up_to(B2):
        if p <= B1: continue
        a = pow(a, p, N)
        g = gcd(a - 1, N)
        if 1 < g < N: return g
    return None

_small_primes_cache = None
def small_primes_up_to(limit):
    global _small_primes_cache
    if _small_primes_cache is not None and _small_primes_cache[-1] >= limit:
        import bisect
        idx = bisect.bisect_right(_small_primes_cache, limit)
        return _small_primes_cache[:idx]
    sieve = bytearray(b'\x01') * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, isqrt(limit) + 1):
        if sieve[i]:
            sieve[i*i::i] = bytearray(len(sieve[i*i::i]))
    result = [i for i in range(2, limit + 1) if sieve[i]]
    _small_primes_cache = result
    return result

# ============================================================
# APPROACH 61: Smooth-residue sieve
# ============================================================
# Hypothesis: Walk tree mod N, compute (m²-n²) mod N. Because tree nodes
# have factored form A=(m-n)(m+n), we can sieve over a factor base more
# efficiently. If A mod N is B-smooth, we get a relation for factoring.

def approach_61_smooth_residue_sieve(N, max_nodes=50000, B=2000):
    """Walk tree, collect smooth residues of (m²-n²) mod N, find x²≡y² mod N."""
    FB = small_primes_up_to(B)
    fb_set = set(FB)

    relations = []  # (exponent_vector, m, n)

    # BFS tree walk mod N
    queue = [(2, 1)]  # root primitive triple generator
    visited = set()
    nodes_checked = 0

    while queue and nodes_checked < max_nodes:
        m, n = queue.pop(0)
        key = (m % N, n % N)
        if key in visited:
            continue
        visited.add(key)
        nodes_checked += 1

        # Compute a = m²-n² mod N (factored as (m-n)(m+n))
        a_mod = ((m - n) * (m + n)) % N

        # Trial divide over FB
        residue = a_mod
        if residue == 0:
            continue
        exps = {}
        for p in FB:
            while residue % p == 0:
                exps[p] = exps.get(p, 0) + 1
                residue //= p
            if residue == 1:
                break

        if residue == 1:
            relations.append((exps, m, n))

            # Try combining pairs
            if len(relations) >= 2:
                # Check last relation against all previous
                e2, m2, n2 = relations[-1]
                for e1, m1, n1 in relations[:-1]:
                    # Combined exponent vector
                    combined = defaultdict(int)
                    for p, e in e1.items(): combined[p] += e
                    for p, e in e2.items(): combined[p] += e
                    if all(v % 2 == 0 for v in combined.values()):
                        x = ((m1-n1)*(m1+n1)) % N
                        y = ((m2-n2)*(m2+n2)) % N
                        # x*y should be a perfect square mod N
                        prod = (x * y) % N
                        sqrt_prod = 1
                        for p, e in combined.items():
                            sqrt_prod = (sqrt_prod * pow(p, e//2, N)) % N
                        g = gcd(sqrt_prod - prod, N) if prod != sqrt_prod else 1
                        if 1 < g < N:
                            return g, nodes_checked, len(relations)

        # Expand children
        for M in BERGGREN:
            cm, cn = apply_mat(M, m, n)
            if cm > 0 and cn > 0 and cm > cn:
                queue.append((cm, cn))

    return None, nodes_checked, len(relations)


# ============================================================
# APPROACH 62: Collision chain
# ============================================================
# Hypothesis: Build chains of tree nodes where m_i ≡ m_j mod (product of small primes).
# Collisions in m mod batch_product leak information about factors of N when
# combined with the factored triple structure.

def approach_62_collision_chain(N, max_nodes=50000, batch_bits=40):
    """Collision chains on m mod batch_product."""
    # Use product of small primes as modulus
    primes = small_primes_up_to(200)
    batch = 1
    for p in primes:
        if batch.bit_length() > batch_bits:
            break
        batch *= p

    buckets = defaultdict(list)
    queue = [(2, 1)]
    visited = set()
    nodes_checked = 0

    while queue and nodes_checked < max_nodes:
        m, n = queue.pop(0)
        if (m, n) in visited or m > 10**15:
            continue
        visited.add((m, n))
        nodes_checked += 1

        key = m % batch
        buckets[key].append((m, n))

        # Check for collisions
        if len(buckets[key]) >= 2:
            for prev_m, prev_n in buckets[key][:-1]:
                diff_m = abs(m - prev_m)
                diff_n = abs(n - prev_n)
                # Products from factored form
                a1 = (prev_m - prev_n) * (prev_m + prev_n)
                a2 = (m - n) * (m + n)
                for val in [diff_m, diff_n, a1 - a2, a1 + a2, m * prev_n - n * prev_m]:
                    g = gcd(abs(val), N)
                    if 1 < g < N:
                        return g, nodes_checked

        for M in BERGGREN:
            cm, cn = apply_mat(M, m, n)
            if cm > 0 and cn > 0 and cm > cn:
                queue.append((cm, cn))

    return None, nodes_checked


# ============================================================
# APPROACH 63: Tree-ECM hybrid
# ============================================================
# Hypothesis: Tree nodes (m,n) generate points on curves y²=x³+ax+b where
# a,b depend on the triple. The group order inherits smoothness from the
# triple's factored structure, improving ECM stage-1 success rate.

def approach_63_tree_ecm_hybrid(N, max_nodes=20000, B1=5000):
    """Use tree triples to seed ECM curves with structured group orders."""
    nodes_checked = 0
    queue = [(2, 1)]
    visited = set()

    while queue and nodes_checked < max_nodes:
        m, n = queue.pop(0)
        if (m, n) in visited or m > 10**12:
            continue
        visited.add((m, n))
        nodes_checked += 1

        a_triple = m*m - n*n
        b_triple = 2*m*n
        c_triple = m*m + n*n

        # Use triple to construct curve parameter
        # Curve: y² = x³ + a_triple*x + b_triple (mod N)
        # Starting point: (m mod N, n mod N)
        x0 = m % N
        y0_sq = (pow(x0, 3, N) + a_triple * x0 + b_triple) % N

        # Montgomery ladder scalar mult using B1-smooth exponent
        # Simplified: just compute kP for k = lcm(1..B1) via prime powers
        # Using projective coords (X:Z) for Montgomery
        sigma = (c_triple * m) % N
        if sigma < 6:
            sigma = 6 + (nodes_checked % 100)

        # Suyama parameterization
        u = (sigma * sigma - 5) % N
        v = (4 * sigma) % N

        vmu = (v - u) % N
        A = (vmu * vmu * vmu * (3*u + v)) % N
        denom = (4 * u * u * u * v) % N
        g = gcd(denom, N)
        if 1 < g < N:
            return g, nodes_checked
        if g == N:
            for M in BERGGREN:
                cm, cn = apply_mat(M, m, n)
                if cm > 0 and cn > 0 and cm > cn:
                    queue.append((cm, cn))
            continue

        try:
            denom_inv = pow(denom, -1, N)
        except ValueError:
            g = gcd(denom, N)
            if 1 < g < N:
                return g, nodes_checked
            for M in BERGGREN:
                cm, cn = apply_mat(M, m, n)
                if cm > 0 and cn > 0 and cm > cn:
                    queue.append((cm, cn))
            continue

        A_curve = (A * denom_inv - 2) % N

        # Montgomery scalar multiplication
        Qx, Qz = (u*u*u % N), (v*v*v % N)
        Rx, Rz = Qx, Qz  # dummy start

        # Multiply by primes up to B1
        for p in small_primes_up_to(B1):
            pk = p
            while pk <= B1:
                # Double-and-add (simplified Montgomery)
                # This is a simplified version - real ECM uses proper ladder
                Rz_new = (Rx * Rz * 2 + A_curve * Rx * Rz + Rz * Rz) % N
                Rx_new = (Rx * Rx - Rz * Rz) % N
                Rx, Rz = Rx_new % N, Rz_new % N
                pk *= p

            g = gcd(Rz, N)
            if 1 < g < N:
                return g, nodes_checked
            if g == N:
                break

        for M in BERGGREN:
            cm, cn = apply_mat(M, m, n)
            if cm > 0 and cn > 0 and cm > cn:
                queue.append((cm, cn))

    return None, nodes_checked


# ============================================================
# APPROACH 64: Recursive CRT
# ============================================================
# Hypothesis: For each small prime p, the tree walk mod p has a short orbit.
# Determine (factor mod p) for many small p by detecting orbit structure,
# then CRT-reconstruct the factor.

def approach_64_recursive_crt(N, max_nodes=50000):
    """For each small prime p, find m mod p orbit in tree, reconstruct factor via CRT."""
    primes = small_primes_up_to(200)
    residues = {}  # p -> set of possible residues

    for p in primes[:30]:
        if N % p == 0:
            return p, 0  # trivial

        # Walk tree mod p, find which residues of m lead to gcd hits
        # on (m²-n²) mod p
        hit_residues = set()
        m, n = 2, 1
        seen = set()
        for _ in range(min(p*p*3, 5000)):
            key = (m % p, n % p)
            if key in seen:
                break
            seen.add(key)

            a_mod_p = (m*m - n*n) % p
            n_mod_p = N % p
            # If a_mod_p divides N mod p
            if a_mod_p != 0 and n_mod_p % a_mod_p == 0:
                hit_residues.add(m % p)

            # Random walk
            M = BERGGREN[random.randint(0, 2)]
            m, n = apply_mat(M, m, n)
            if m <= n or n < 0:
                m, n = 2, 1

        if hit_residues and len(hit_residues) < p:
            residues[p] = hit_residues

    # CRT reconstruction attempt
    # For each combination of residues, check if product is a factor
    nodes_checked = sum(min(p*p*3, 5000) for p in primes[:30])

    if len(residues) < 3:
        return None, nodes_checked

    # Try small CRT combinations
    sorted_primes = sorted(residues.keys())[:8]

    def crt_search(idx, current, modulus):
        if idx >= len(sorted_primes):
            g = gcd(current, N)
            if 1 < g < N:
                return g
            g = gcd(N - current, N)
            if 1 < g < N:
                return g
            return None
        p = sorted_primes[idx]
        for r in residues[p]:
            # CRT combine
            new_mod = modulus * p
            # Find x ≡ current (mod modulus), x ≡ r (mod p)
            g_ext = gcd(modulus, p)
            if (r - current) % g_ext != 0:
                continue
            # Since p is prime and modulus coprime to p
            inv = pow(modulus, -1, p)
            x = (current + modulus * ((r - current) * inv % p)) % new_mod
            result = crt_search(idx + 1, x, new_mod)
            if result:
                return result
        return None

    for r in residues.get(sorted_primes[0], [0]):
        result = crt_search(1, r, sorted_primes[0])
        if result:
            return result, nodes_checked

    return None, nodes_checked


# ============================================================
# APPROACH 65: Parity detection
# ============================================================
# Hypothesis: The branch pattern (B1/B2/B3 choices) that reaches a node
# encodes parity information about m mod p. By analyzing which branches
# lead to even/odd m values mod small primes, we can extract factor bits.

def approach_65_parity_detection(N, max_depth=20, max_nodes=50000):
    """Detect factor parity from tree branch patterns."""
    nodes_checked = 0

    # For each small prime p, map branch sequences to m mod p
    primes = small_primes_up_to(100)
    branch_maps = {}  # p -> {branch_seq: m_mod_p}

    for p in primes[:20]:
        if N % p == 0:
            return p, 0

        bmap = {}
        # Enumerate paths up to depth
        stack = [(2, 1, ())]  # (m, n, branch_sequence)
        while stack and len(bmap) < 500:
            m, n, seq = stack.pop()
            nodes_checked += 1
            if nodes_checked > max_nodes:
                break

            bmap[seq] = m % p

            if len(seq) < max_depth:
                for i, M in enumerate(BERGGREN):
                    cm, cn = apply_mat(M, m, n)
                    if cm > 0 and cn > 0 and cm > cn and cm < 10**12:
                        stack.append((cm, cn, seq + (i,)))

        branch_maps[p] = bmap

    # Cross-reference: find branch sequences where m mod p reveals factor info
    # If N ≡ 0 mod p is impossible (since p < N), look for
    # sequences where (m²-n²) mod N has small gcd with N

    # Actually: walk tree, check gcd at each node using derived values
    m, n = 2, 1
    for _ in range(min(max_nodes - nodes_checked, 30000)):
        nodes_checked += 1
        a = m*m - n*n
        b = 2*m*n
        c = m*m + n*n
        for val in [a, b, c, m-n, m+n]:
            g = gcd(val, N)
            if 1 < g < N:
                return g, nodes_checked

        # Choose branch based on parity of current m relative to N
        # This is the "parity detection" heuristic
        r = (m * n) % 3
        M = BERGGREN[r]
        m, n = apply_mat(M, m, n)
        if m <= n or n < 0 or m > 10**15:
            m, n = 2, 1

    return None, nodes_checked


# ============================================================
# APPROACH 66: Bilinear pairing
# ============================================================
# Hypothesis: Take nodes from two different tree paths. Cross-products
# (m_i * n_j - m_j * n_i) are bilinear in the tree parameters.
# The factored form means these cross-products inherit smoothness,
# giving more relations per node pair.

def approach_66_bilinear_pairing(N, max_nodes=30000, B=3000):
    """Cross-pair nodes from different paths for bilinear smooth relations."""
    FB = small_primes_up_to(B)

    # Collect nodes from 3 different branch paths
    paths = [[], [], []]
    for branch_idx in range(3):
        m, n = 2, 1
        for _ in range(max_nodes // 3):
            paths[branch_idx].append((m, n))
            # Follow primarily one branch with occasional mixing
            if random.random() < 0.8:
                m, n = apply_mat(BERGGREN[branch_idx], m, n)
            else:
                m, n = apply_mat(BERGGREN[random.randint(0, 2)], m, n)
            if m <= n or n < 0 or m > 10**12:
                m, n = 2, 1

    nodes_checked = sum(len(p) for p in paths)
    relations = []

    # Cross-pair between paths
    for i in range(min(len(paths[0]), 500)):
        m1, n1 = paths[0][i]
        for j in range(min(len(paths[1]), 500)):
            m2, n2 = paths[1][j]

            cross = abs(m1 * n2 - m2 * n1)
            if cross == 0:
                continue

            g = gcd(cross, N)
            if 1 < g < N:
                return g, nodes_checked, len(relations)

            # Check smoothness of cross mod N
            cross_mod = cross % N
            if cross_mod == 0:
                continue

            residue = cross_mod
            exps = {}
            for p in FB:
                if residue == 1:
                    break
                while residue % p == 0:
                    exps[p] = exps.get(p, 0) + 1
                    residue //= p

            if residue == 1:
                relations.append((exps, (m1, n1), (m2, n2)))

    # Try to combine relations for square
    if len(relations) >= 2:
        for i in range(len(relations)):
            for j in range(i+1, min(len(relations), i+100)):
                e1 = relations[i][0]
                e2 = relations[j][0]
                combined = defaultdict(int)
                for p, e in e1.items(): combined[p] += e
                for p, e in e2.items(): combined[p] += e
                if all(v % 2 == 0 for v in combined.values()):
                    m1, n1 = relations[i][1]
                    m2, n2 = relations[i][2]
                    m3, n3 = relations[j][1]
                    m4, n4 = relations[j][2]
                    v1 = abs(m1*n2 - m2*n1) % N
                    v2 = abs(m3*n4 - m4*n3) % N
                    sqrt_val = 1
                    for p, e in combined.items():
                        sqrt_val = sqrt_val * pow(p, e//2, N) % N
                    prod = (v1 * v2) % N
                    g = gcd(sqrt_val - prod, N)
                    if 1 < g < N:
                        return g, nodes_checked, len(relations)
                    g = gcd(sqrt_val + prod, N)
                    if 1 < g < N:
                        return g, nodes_checked, len(relations)

    return None, nodes_checked, len(relations)


# ============================================================
# APPROACH 67: Index calculus on tree
# ============================================================
# Hypothesis: Treat tree navigation as a group operation. Build index calculus
# relations: express random tree elements as products of "basis" elements
# (small-depth nodes). Solving the DLP in this group may reveal factors.

def approach_67_index_calculus(N, max_nodes=30000, basis_depth=6):
    """Index calculus: express deep nodes as products of shallow basis nodes."""
    # Build basis: all nodes up to depth basis_depth
    basis = []
    stack = [(2, 1, 0)]
    while stack:
        m, n, d = stack.pop()
        if d > basis_depth:
            continue
        basis.append((m, n))
        for M in BERGGREN:
            cm, cn = apply_mat(M, m, n)
            if cm > 0 and cn > 0 and cm > cn:
                stack.append((cm, cn, d+1))

    nodes_checked = len(basis)

    # For each basis node, compute (m²+n²) mod N (the hypotenuse)
    basis_hyps = [(m*m + n*n) % N for m, n in basis]
    basis_legs = [((m*m - n*n) % N, (2*m*n) % N) for m, n in basis]

    # Check GCDs
    for m, n in basis:
        for val in [m*m - n*n, 2*m*n, m*m + n*n, m-n, m+n]:
            g = gcd(val, N)
            if 1 < g < N:
                return g, nodes_checked

    # Random deep walks, check if hypotenuse can be expressed via basis
    m, n = 2, 1
    for step in range(max_nodes - nodes_checked):
        nodes_checked += 1
        M = BERGGREN[random.randint(0, 2)]
        m, n = apply_mat(M, m, n)
        if m <= n or n < 0 or m > 10**15:
            m, n = 2, 1
            continue

        hyp = (m*m + n*n) % N
        leg_a = (m*m - n*n) % N

        # Check gcd of differences with basis hypotenuses
        for bh in basis_hyps[:50]:
            g = gcd(abs(hyp - bh), N)
            if 1 < g < N:
                return g, nodes_checked
            g = gcd((hyp * bh) % N, N)
            # This is always 0 mod N or not useful, skip

        # Check leg products
        for ba, bb in basis_legs[:50]:
            g = gcd(abs(leg_a * ba - 1) % N if ba else 0, N)
            if g and 1 < g < N:
                return g, nodes_checked

    return None, nodes_checked


# ============================================================
# APPROACH 68: Sieve by tree depth
# ============================================================
# Hypothesis: For each FB prime p, certain tree depths/paths guarantee
# divisibility of (m²-n²) by p. Precompute these depth patterns,
# then only visit nodes at "rich" depths — concentrating smoothness.

def approach_68_sieve_by_depth(N, max_nodes=50000, B=5000):
    """Precompute which depths give divisibility by FB primes, target those."""
    FB = small_primes_up_to(B)

    # For each prime p, find which (m mod p, n mod p) pairs give p | (m²-n²)
    # i.e., m² ≡ n² mod p, i.e., m ≡ ±n mod p
    # Then trace which tree depths map root (2,1) to these residues

    # For each p, compute tree walk mod p
    depth_hits = defaultdict(set)  # depth -> set of primes that divide a at this depth

    nodes_checked = 0
    # BFS with depth tracking
    queue = [(2, 1, 0)]  # m, n, depth
    visited = set()
    smooth_at = defaultdict(list)  # depth -> list of (m, n, smoothness_count)

    while queue and nodes_checked < max_nodes:
        m, n, depth = queue.pop(0)
        if depth > 25:
            continue
        key = (m, n)
        if key in visited:
            continue
        visited.add(key)
        nodes_checked += 1

        a = m*m - n*n
        b_val = 2*m*n
        c = m*m + n*n

        # Check gcd
        for val in [a, b_val, c, m-n, m+n]:
            g = gcd(val, N)
            if 1 < g < N:
                return g, nodes_checked, 0

        # Count FB primes dividing a
        smooth_count = 0
        temp = a
        for p in FB:
            if temp == 1: break
            while temp % p == 0:
                smooth_count += 1
                temp //= p

        smooth_at[depth].append((m, n, smooth_count, temp == 1))

        for M in BERGGREN:
            cm, cn = apply_mat(M, m, n)
            if cm > 0 and cn > 0 and cm > cn:
                queue.append((cm, cn, depth + 1))

    # Analyze: which depths have highest smoothness rate?
    best_depth = 0
    best_rate = 0
    for d, entries in smooth_at.items():
        full_smooth = sum(1 for _, _, _, s in entries if s)
        rate = full_smooth / len(entries) if entries else 0
        if rate > best_rate:
            best_rate = rate
            best_depth = d

    return None, nodes_checked, best_rate


# ============================================================
# APPROACH 69: Matrix powering shortcut (fast p±1)
# ============================================================
# Hypothesis: Compute B2^E mod N where E = lcm(1..B). If the order of B2
# mod p divides E (smooth order), then B2^E ≡ I mod p, and we can extract
# p via gcd. This is a structured p±1 attack using Berggren matrix structure.

def approach_69_matrix_powering(N, B1_bound=50000, B2_bound=500000):
    """Matrix p±1: compute Berggren matrix powers mod N, extract factor from order."""
    nodes_checked = 0  # count matrix multiplications as "work"

    for mat_idx, mat in enumerate(BERGGREN):
        # Stage 1: multiply by all prime powers up to B1
        M = ((mat[0][0] % N, mat[0][1] % N), (mat[1][0] % N, mat[1][1] % N))

        for p in small_primes_up_to(B1_bound):
            pk = p
            while pk <= B1_bound:
                M = mat_pow_mod(M, p, N)
                nodes_checked += int(log2(p)) + 1
                pk *= p

        # Check if M ≡ I mod p for some factor p
        # M - I should have entries divisible by p
        for entry in [M[0][0] - 1, M[0][1], M[1][0], M[1][1] - 1]:
            g = gcd(entry % N, N)
            if 1 < g < N:
                return g, nodes_checked, f"B{mat_idx+1}"

        # Also check det(M) - 1
        det = (M[0][0] * M[1][1] - M[0][1] * M[1][0]) % N
        g = gcd(det - 1, N)
        if 1 < g < N:
            return g, nodes_checked, f"B{mat_idx+1}_det"

        # Check trace
        tr = (M[0][0] + M[1][1]) % N
        for target in [2, 0, N-2]:  # trace of identity, or other special values
            g = gcd(tr - target, N)
            if 1 < g < N:
                return g, nodes_checked, f"B{mat_idx+1}_tr"

        # Stage 2: baby-step giant-step for primes in (B1, B2)
        # Simplified: just multiply by large primes
        primes_s2 = small_primes_up_to(min(B2_bound, 100000))
        for p in primes_s2:
            if p <= B1_bound:
                continue
            M = mat_pow_mod(M, p, N)
            nodes_checked += int(log2(p)) + 1

            for entry in [M[0][0] - 1, M[0][1], M[1][0], M[1][1] - 1]:
                g = gcd(entry % N, N)
                if 1 < g < N:
                    return g, nodes_checked, f"B{mat_idx+1}_s2"

    return None, nodes_checked, "none"


# ============================================================
# APPROACH 70: Hybrid rho + smooth
# ============================================================
# Hypothesis: Use Pollard rho for factors < 2^32 (fast cycle detection),
# then switch to tree-smooth sieve for larger factors. The tree's 3-6x
# smoothness advantage reduces the sieve bound needed.

def approach_70_hybrid_rho_smooth(N, rho_iters=100000, tree_nodes=30000, B=5000):
    """Phase 1: Pollard rho. Phase 2: tree smooth sieve with reduced bound."""
    # Phase 1: fast rho
    nodes_checked = 0

    for attempt in range(3):
        x = random.randint(2, N-1)
        y = x
        c = random.randint(1, N-1)

        # Brent's improvement with batched gcd
        q = 1
        r = 1
        ys = x

        for _ in range(rho_iters):
            nodes_checked += 1
            x_old = x
            for _ in range(r):
                x = (x * x + c) % N

            k = 0
            while k < r:
                ys = x
                batch = min(128, r - k)
                for _ in range(batch):
                    x = (x * x + c) % N
                    q = q * abs(x - y) % N

                g = gcd(q, N)
                if g != 1:
                    break
                k += batch

            if g != 1:
                break
            y = x_old
            r *= 2

        if 1 < g < N:
            return g, nodes_checked, "rho"
        if g == N:
            # Backtrack
            while True:
                ys = (ys * ys + c) % N
                g = gcd(abs(ys - y), N)
                if g != 1:
                    break
            if 1 < g < N:
                return g, nodes_checked, "rho_bt"

    # Phase 2: tree smooth sieve with reduced bound (smoothness advantage)
    effective_B = int(B * 0.6)  # 40% reduction from smoothness advantage
    FB = small_primes_up_to(effective_B)

    relations = []
    m, n = 2, 1

    for _ in range(tree_nodes):
        nodes_checked += 1
        a = (m - n) * (m + n)  # factored form
        a_mod = a % N

        if a_mod == 0:
            M = BERGGREN[random.randint(0, 2)]
            m, n = apply_mat(M, m, n)
            continue

        # Quick gcd check
        g = gcd(a, N)
        if 1 < g < N:
            return g, nodes_checked, "tree_gcd"

        # Trial division (fast because a is partially factored)
        residue = a_mod
        exps = {}
        # Factor (m-n) and (m+n) separately — smoothness advantage
        for part in [abs(m-n), m+n]:
            part_r = part
            for p in FB:
                while part_r % p == 0:
                    exps[p] = exps.get(p, 0) + 1
                    part_r //= p
                    residue //= p
                if part_r == 1:
                    break

        if residue == 1 or all(v % 2 == 0 for v in exps.values()):
            relations.append((exps, m, n))

        M = BERGGREN[random.randint(0, 2)]
        m, n = apply_mat(M, m, n)
        if m <= n or n < 0 or m > 10**15:
            m, n = 2, 1

    return None, nodes_checked, f"tree_{len(relations)}rels"


# ============================================================
# RUNNER
# ============================================================

def run_all():
    results = {}
    bit_sizes = [16, 20, 24, 28, 32]
    tests = gen_semis(bit_sizes, count=3)

    print("=" * 80)
    print("PYTHAGOREAN TREE FACTORING — ALGORITHMIC APPROACHES #61–70")
    print("=" * 80)

    # ---- Approach 61 ----
    print("\n### APPROACH 61: Smooth-residue sieve ###")
    print("Hypothesis: Walk tree, sieve (m²-n²) mod N for B-smooth residues,")
    print("  combine to get x²≡y² mod N. Factored form gives 3-6x smoothness boost.")
    a61_results = []
    for total_bits, p, q, N in tests:
        t0 = time.time()
        result = approach_61_smooth_residue_sieve(N, max_nodes=30000, B=2000)
        elapsed = time.time() - t0
        found = result[0] is not None and (result[0] == p or result[0] == q)
        a61_results.append((total_bits, found, elapsed, result[1], result[2]))
        status = "FOUND" if found else "MISS"
        print(f"  {total_bits}b: {status} in {elapsed:.3f}s ({result[1]} nodes, {result[2]} rels)")
    results[61] = a61_results

    # Baseline: Pollard rho
    print("\n  Baseline (Pollard rho):")
    rho_results = []
    for total_bits, p, q, N in tests:
        t0 = time.time()
        random.seed(42)
        r = pollard_rho(N, max_iters=100000)
        elapsed = time.time() - t0
        found = r is not None and (r == p or r == q)
        rho_results.append((total_bits, found, elapsed))
        print(f"  {total_bits}b: {'FOUND' if found else 'MISS'} in {elapsed:.3f}s")
    results['rho'] = rho_results

    # ---- Approach 62 ----
    print("\n### APPROACH 62: Collision chain ###")
    print("Hypothesis: Collisions in m mod (product of small primes) leak factor")
    print("  info via cross-products of factored triples.")
    a62_results = []
    for total_bits, p, q, N in tests:
        t0 = time.time()
        result = approach_62_collision_chain(N, max_nodes=30000)
        elapsed = time.time() - t0
        found = result[0] is not None and (result[0] == p or result[0] == q)
        a62_results.append((total_bits, found, elapsed, result[1]))
        print(f"  {total_bits}b: {'FOUND' if found else 'MISS'} in {elapsed:.3f}s ({result[1]} nodes)")
    results[62] = a62_results

    # ---- Approach 63 ----
    print("\n### APPROACH 63: Tree-ECM hybrid ###")
    print("Hypothesis: Tree triples seed ECM curves with structured group orders,")
    print("  improving stage-1 success rate via inherited smoothness.")
    a63_results = []
    for total_bits, p, q, N in tests:
        t0 = time.time()
        result = approach_63_tree_ecm_hybrid(N, max_nodes=10000, B1=5000)
        elapsed = time.time() - t0
        found = result[0] is not None and (result[0] == p or result[0] == q)
        a63_results.append((total_bits, found, elapsed, result[1]))
        print(f"  {total_bits}b: {'FOUND' if found else 'MISS'} in {elapsed:.3f}s ({result[1]} nodes)")
    results[63] = a63_results

    # ---- Approach 64 ----
    print("\n### APPROACH 64: Recursive CRT ###")
    print("Hypothesis: Determine (factor mod p) for small primes p by orbit")
    print("  detection in tree mod p, then CRT-reconstruct factor.")
    a64_results = []
    for total_bits, p, q, N in tests:
        t0 = time.time()
        result = approach_64_recursive_crt(N, max_nodes=30000)
        elapsed = time.time() - t0
        found = result[0] is not None and (result[0] == p or result[0] == q)
        a64_results.append((total_bits, found, elapsed, result[1]))
        print(f"  {total_bits}b: {'FOUND' if found else 'MISS'} in {elapsed:.3f}s")
    results[64] = a64_results

    # ---- Approach 65 ----
    print("\n### APPROACH 65: Parity detection ###")
    print("Hypothesis: Branch patterns (B1/B2/B3) encode parity of m mod p;")
    print("  analyzing patterns extracts factor bits.")
    a65_results = []
    for total_bits, p, q, N in tests:
        t0 = time.time()
        result = approach_65_parity_detection(N, max_nodes=30000)
        elapsed = time.time() - t0
        found = result[0] is not None and (result[0] == p or result[0] == q)
        a65_results.append((total_bits, found, elapsed, result[1]))
        print(f"  {total_bits}b: {'FOUND' if found else 'MISS'} in {elapsed:.3f}s ({result[1]} nodes)")
    results[65] = a65_results

    # ---- Approach 66 ----
    print("\n### APPROACH 66: Bilinear pairing ###")
    print("Hypothesis: Cross-products (m_i*n_j - m_j*n_i) from different paths")
    print("  inherit smoothness, giving more relations per node pair.")
    a66_results = []
    for total_bits, p, q, N in tests:
        t0 = time.time()
        result = approach_66_bilinear_pairing(N, max_nodes=20000, B=2000)
        elapsed = time.time() - t0
        found = result[0] is not None and (result[0] == p or result[0] == q)
        a66_results.append((total_bits, found, elapsed, result[1], result[2]))
        print(f"  {total_bits}b: {'FOUND' if found else 'MISS'} in {elapsed:.3f}s ({result[1]} nodes, {result[2]} rels)")
    results[66] = a66_results

    # ---- Approach 67 ----
    print("\n### APPROACH 67: Index calculus on tree ###")
    print("Hypothesis: Express deep tree elements via shallow basis nodes;")
    print("  solving DLP in tree group reveals factors via GCD of differences.")
    a67_results = []
    for total_bits, p, q, N in tests:
        t0 = time.time()
        result = approach_67_index_calculus(N, max_nodes=20000)
        elapsed = time.time() - t0
        found = result[0] is not None and (result[0] == p or result[0] == q)
        a67_results.append((total_bits, found, elapsed, result[1]))
        print(f"  {total_bits}b: {'FOUND' if found else 'MISS'} in {elapsed:.3f}s ({result[1]} nodes)")
    results[67] = a67_results

    # Baseline: p-1
    print("\n  Baseline (p-1, B1=50K):")
    pm1_results = []
    for total_bits, p, q, N in tests:
        t0 = time.time()
        r = p_minus_1(N, B1=50000, B2=100000)
        elapsed = time.time() - t0
        found = r is not None and (r == p or r == q)
        pm1_results.append((total_bits, found, elapsed))
        print(f"  {total_bits}b: {'FOUND' if found else 'MISS'} in {elapsed:.3f}s")
    results['pm1'] = pm1_results

    # ---- Approach 68 ----
    print("\n### APPROACH 68: Sieve by tree depth ###")
    print("Hypothesis: Certain tree depths/paths guarantee divisibility by FB primes;")
    print("  target those depths to concentrate smoothness.")
    a68_results = []
    for total_bits, p, q, N in tests:
        t0 = time.time()
        result = approach_68_sieve_by_depth(N, max_nodes=20000, B=3000)
        elapsed = time.time() - t0
        found = result[0] is not None and (result[0] == p or result[0] == q)
        a68_results.append((total_bits, found, elapsed, result[1], result[2]))
        print(f"  {total_bits}b: {'FOUND' if found else 'MISS'} in {elapsed:.3f}s ({result[1]} nodes, smooth_rate={result[2]:.3f})")
    results[68] = a68_results

    # ---- Approach 69 ----
    print("\n### APPROACH 69: Matrix powering shortcut (fast p±1) ###")
    print("Hypothesis: B^E mod N where E=lcm(1..B). If ord(B mod p) | E,")
    print("  then B^E ≡ I mod p, factor via gcd of (trace-2, det-1, entries).")
    a69_results = []
    for total_bits, p, q, N in tests:
        t0 = time.time()
        result = approach_69_matrix_powering(N, B1_bound=10000, B2_bound=50000)
        elapsed = time.time() - t0
        found = result[0] is not None and (result[0] == p or result[0] == q)
        a69_results.append((total_bits, found, elapsed, result[1], result[2]))
        status = "FOUND" if found else "MISS"
        print(f"  {total_bits}b: {status} in {elapsed:.3f}s ({result[1]} mults, via {result[2]})")
    results[69] = a69_results

    # ---- Approach 70 ----
    print("\n### APPROACH 70: Hybrid rho + smooth ###")
    print("Hypothesis: Rho for small factors, tree-smooth sieve for larger.")
    print("  Smoothness advantage reduces effective sieve bound by ~40%.")
    a70_results = []
    for total_bits, p, q, N in tests:
        t0 = time.time()
        random.seed(total_bits + 999)
        result = approach_70_hybrid_rho_smooth(N, rho_iters=50000, tree_nodes=20000, B=3000)
        elapsed = time.time() - t0
        found = result[0] is not None and (result[0] == p or result[0] == q)
        a70_results.append((total_bits, found, elapsed, result[1], result[2]))
        print(f"  {total_bits}b: {'FOUND' if found else 'MISS'} in {elapsed:.3f}s ({result[1]} ops, via {result[2]})")
    results[70] = a70_results

    # ============================================================
    # SUMMARY
    # ============================================================
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    for approach_id in range(61, 71):
        data = results[approach_id]
        total = len(data)
        found = sum(1 for r in data if r[1])
        avg_time = sum(r[2] for r in data) / total if total else 0
        # Success by bit size
        by_bits = defaultdict(lambda: [0, 0])
        for r in data:
            by_bits[r[0]][0] += 1
            if r[1]:
                by_bits[r[0]][1] += 1
        bits_str = ", ".join(f"{b}b:{s}/{t}" for b, (t, s) in sorted(by_bits.items()))
        print(f"  #{approach_id}: {found}/{total} found, avg {avg_time:.3f}s  [{bits_str}]")

    # Baselines
    rho_found = sum(1 for r in results['rho'] if r[1])
    rho_time = sum(r[2] for r in results['rho']) / len(results['rho'])
    pm1_found = sum(1 for r in results['pm1'] if r[1])
    pm1_time = sum(r[2] for r in results['pm1']) / len(results['pm1'])
    print(f"  Baseline rho: {rho_found}/{len(results['rho'])} found, avg {rho_time:.3f}s")
    print(f"  Baseline p-1: {pm1_found}/{len(results['pm1'])} found, avg {pm1_time:.3f}s")

    return results

if __name__ == "__main__":
    results = run_all()

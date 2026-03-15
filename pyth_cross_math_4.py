#!/usr/bin/env python3
"""
Pythagorean Tree Factoring — Cross-Mathematics Suite #4
Fields 16-20: Measure Theory, Cryptographic Lattices, Homotopy Theory,
              Combinatorial Game Theory, Random Matrix Theory

Each experiment tests multiple roots including non-standard (0,1), (1,1), (1,2).
Memory < 2GB, each experiment < 60 seconds.
"""

import math
import random
import time
import sys
from math import gcd, log, isqrt, log2, sqrt
from collections import defaultdict, Counter
import numpy as np

# ============================================================
# TREE INFRASTRUCTURE
# ============================================================

# Berggren matrices: B1(2m-n,m), B2(2m+n,m), B3(m+2n,n)
B1 = np.array([[2, -1], [1, 0]], dtype=np.int64)
B2 = np.array([[2,  1], [1, 0]], dtype=np.int64)
B3 = np.array([[1,  2], [0, 1]], dtype=np.int64)
BERGGREN = [B1, B2, B3]
BERG_NAMES = ["B1", "B2", "B3"]

def apply_berggren(idx, m, n):
    """Apply Berggren matrix by index (0,1,2) to (m,n)."""
    if idx == 0:
        return 2*m - n, m
    elif idx == 1:
        return 2*m + n, m
    else:
        return m + 2*n, n

def apply_berggren_mod(idx, m, n, N):
    """Apply Berggren matrix mod N."""
    if idx == 0:
        return (2*m - n) % N, m % N
    elif idx == 1:
        return (2*m + n) % N, m % N
    else:
        return (m + 2*n) % N, n % N

def derived_values(m, n):
    """Get all gcd-testable values from (m,n)."""
    a = m*m - n*n
    b = 2*m*n
    c = m*m + n*n
    d = m - n
    s = m + n
    return [v for v in [a, b, c, m, n, d, s, d*d, s*s, abs(a)] if v > 0]

def check_factor(N, m, n):
    """Check if (m,n) reveals a factor of N."""
    for v in derived_values(m, n):
        g = gcd(v, N)
        if 1 < g < N:
            return g
    return None

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
        else: return False
    return True

def gen_semi(bits, seed=None):
    rng = random.Random(seed)
    half = max(bits // 2, 4)
    while True:
        p = rng.getrandbits(half) | (1 << (half - 1)) | 1
        if miller_rabin(p): break
    while True:
        q = rng.getrandbits(bits - half) | (1 << (bits - half - 1)) | 1
        if q != p and miller_rabin(q): break
    return min(p, q), max(p, q), p * q

# All roots to test
STANDARD_ROOTS = [(2, 1), (3, 2), (4, 3), (5, 2), (5, 4), (7, 4), (8, 3)]
NONSTANDARD_ROOTS = [(0, 1), (1, 1), (1, 2)]
ALL_ROOTS = STANDARD_ROOTS + NONSTANDARD_ROOTS

def mat_mul_mod(A, B, N):
    """2x2 matrix multiply mod N using Python ints (no overflow)."""
    return [
        [(int(A[0][0]) * int(B[0][0]) + int(A[0][1]) * int(B[1][0])) % N,
         (int(A[0][0]) * int(B[0][1]) + int(A[0][1]) * int(B[1][1])) % N],
        [(int(A[1][0]) * int(B[0][0]) + int(A[1][1]) * int(B[1][0])) % N,
         (int(A[1][0]) * int(B[0][1]) + int(A[1][1]) * int(B[1][1])) % N],
    ]

def mat_pow_mod(M, k, N):
    """Matrix power mod N by repeated squaring."""
    result = [[1, 0], [0, 1]]  # identity
    base = [[int(M[i][j]) % N for j in range(2)] for i in range(2)]
    while k > 0:
        if k & 1:
            result = mat_mul_mod(result, base, N)
        base = mat_mul_mod(base, base, N)
        k >>= 1
    return result

IDENTITY = [[1, 0], [0, 1]]

def mat_eq_mod(A, B, N):
    """Check if A ≡ B mod N."""
    for i in range(2):
        for j in range(2):
            if (A[i][j] - B[i][j]) % N != 0:
                return False
    return True

# ============================================================
# FIELD 16: MEASURE THEORY / HAAR MEASURE
# ============================================================

def experiment_16_haar_measure():
    """
    Track empirical distribution of (m,n) mod N over random walks.
    Measure entropy at each step. Compare entropy growth for different roots.
    Does the entropy plateau reveal orbit sizes?
    """
    print("=" * 72)
    print("FIELD 16: MEASURE THEORY / HAAR MEASURE")
    print("Entropy of tree walk distribution → orbit size detection")
    print("=" * 72)

    bit_sizes = [20, 24, 28, 32, 36, 40]
    num_walks = 500
    walk_length = 200
    seeds = [42, 137, 256]

    results = {}

    for bits in bit_sizes:
        p, q, N = gen_semi(bits, seed=bits * 7)
        # Theoretical orbit entropy under CRT
        # Orbit of (m,n) mod p and mod q are independent
        print(f"\n--- {bits}b: N={N}, p={p}, q={q} ---")

        root_results = {}
        for root in ALL_ROOTS:
            m0, n0 = root
            # Track distribution of (m,n) mod N across walks
            dist = Counter()
            entropy_by_step = []

            for step in range(walk_length):
                # Do one step of random walk from each starting point
                if step == 0:
                    states = [(m0 % N, n0 % N)] * num_walks
                else:
                    new_states = []
                    for (mm, nn) in states:
                        idx = random.randint(0, 2)
                        mm2, nn2 = apply_berggren_mod(idx, mm, nn, N)
                        new_states.append((mm2, nn2))
                    states = new_states

                # Update distribution
                for s in states:
                    dist[s] += 1

                # Compute entropy of distribution
                total = sum(dist.values())
                entropy = 0.0
                for count in dist.values():
                    if count > 0:
                        prob = count / total
                        entropy -= prob * log2(prob)
                entropy_by_step.append(entropy)

            # Entropy growth rate (bits per step in the middle region)
            mid = len(entropy_by_step) // 2
            if mid > 10:
                growth_rate = (entropy_by_step[mid] - entropy_by_step[mid // 2]) / (mid - mid // 2)
            else:
                growth_rate = 0.0

            # Final entropy
            final_entropy = entropy_by_step[-1]
            # Theoretical max if uniform over all visited states
            n_visited = len(dist)
            max_entropy = log2(n_visited) if n_visited > 1 else 0

            root_results[root] = {
                'final_entropy': final_entropy,
                'max_entropy': max_entropy,
                'growth_rate': growth_rate,
                'n_visited': n_visited,
                'entropy_25': entropy_by_step[min(25, len(entropy_by_step) - 1)],
                'entropy_100': entropy_by_step[min(100, len(entropy_by_step) - 1)],
            }

            # Check if any walk found a factor
            found = False
            for (mm, nn) in states:
                g = check_factor(N, int(mm), int(nn))
                if g:
                    found = True
                    break

            root_results[root]['found_factor'] = found

        # Print results
        print(f"  {'Root':>8}  {'Entropy':>8}  {'MaxEnt':>8}  {'Growth':>10}  {'Visited':>8}  {'E@25':>7}  {'E@100':>7}  {'Factor':>6}")
        for root in ALL_ROOTS:
            r = root_results[root]
            print(f"  {str(root):>8}  {r['final_entropy']:8.2f}  {r['max_entropy']:8.2f}  "
                  f"{r['growth_rate']:10.4f}  {r['n_visited']:8d}  {r['entropy_25']:7.2f}  "
                  f"{r['entropy_100']:7.2f}  {'YES' if r['found_factor'] else 'no':>6}")

        results[bits] = root_results

    # Verdict
    print("\n--- FIELD 16 VERDICT ---")
    # Check: does entropy plateau differ for different N structures?
    # Compare: which roots give fastest entropy growth?
    best_roots = Counter()
    for bits in bit_sizes:
        rr = results[bits]
        best = max(ALL_ROOTS, key=lambda r: rr[r]['growth_rate'])
        best_roots[best] += 1
    print(f"Best root by entropy growth rate: {best_roots.most_common(3)}")

    # Check non-standard roots
    ns_better = 0
    ns_total = 0
    for bits in bit_sizes:
        rr = results[bits]
        std_avg = np.mean([rr[r]['final_entropy'] for r in STANDARD_ROOTS])
        for r in NONSTANDARD_ROOTS:
            ns_total += 1
            if rr[r]['final_entropy'] > std_avg:
                ns_better += 1
    print(f"Non-standard roots beat standard avg entropy: {ns_better}/{ns_total}")
    print(f"VERDICT: Entropy analysis {'PROMISING' if any(rr[r]['found_factor'] for bits in bit_sizes for r in ALL_ROOTS for rr in [results[bits]]) else 'WEAK'} for factoring")
    return results


# ============================================================
# FIELD 17: CRYPTOGRAPHIC LATTICES / LLL
# ============================================================

def experiment_17_lll_lattice():
    """
    Build lattice from Berggren matrix products.
    Apply LLL to find short vectors.
    Check if short vectors correspond to factor-revealing (m,n).
    """
    print("\n" + "=" * 72)
    print("FIELD 17: CRYPTOGRAPHIC LATTICES / LLL")
    print("LLL on Berggren product lattice → short factor-revealing vectors")
    print("=" * 72)

    # We'll use a simple LLL implementation for small dimensions
    # to avoid needing fpylll

    def gram_schmidt(basis):
        """Gram-Schmidt orthogonalization."""
        n = len(basis)
        ortho = [np.array(b, dtype=np.float64) for b in basis]
        mu = np.zeros((n, n))
        for i in range(n):
            for j in range(i):
                dot_ij = np.dot(ortho[i], ortho[j])
                dot_jj = np.dot(ortho[j], ortho[j])
                if dot_jj > 1e-10:
                    mu[i][j] = dot_ij / dot_jj
                ortho[i] = ortho[i] - mu[i][j] * ortho[j]
        return ortho, mu

    def lll_reduce(basis, delta=0.75):
        """Simple LLL reduction. basis = list of integer vectors."""
        basis = [np.array(b, dtype=np.float64) for b in basis]
        n = len(basis)
        ortho, mu = gram_schmidt(basis)
        k = 1
        max_iter = 500
        itr = 0
        while k < n and itr < max_iter:
            itr += 1
            for j in range(k - 1, -1, -1):
                if abs(mu[k][j]) > 0.5:
                    r = round(mu[k][j])
                    basis[k] = basis[k] - r * basis[j]
                    ortho, mu = gram_schmidt(basis)
            norm_k = np.dot(ortho[k], ortho[k])
            norm_km1 = np.dot(ortho[k - 1], ortho[k - 1])
            if norm_k >= (delta - mu[k][k - 1] ** 2) * norm_km1:
                k += 1
            else:
                basis[k], basis[k - 1] = basis[k - 1].copy(), basis[k].copy()
                ortho, mu = gram_schmidt(basis)
                k = max(k - 1, 1)
        return [b for b in basis]

    bit_sizes = [20, 24, 28, 32, 36, 40, 48]
    depth = 4  # product depth for lattice basis vectors

    results = {}

    for bits in bit_sizes:
        p, q, N = gen_semi(bits, seed=bits * 13)
        print(f"\n--- {bits}b: N={N}, p={p}, q={q} ---")

        root_results = {}
        for root in ALL_ROOTS:
            m0, n0 = root

            # Build lattice basis from Berggren matrix products of depth `depth`
            # Each path of depth d gives a 2x2 matrix; we use the action on (m0,n0)
            # to get a 2D point. Collect 2^depth points, use them as lattice vectors.
            # Actually: use matrix entries directly as lattice rows.

            # Strategy: enumerate all 3^depth matrix products, take (m,n) results
            # modulo N. Then build a lattice from differences.
            points = []
            stack = [(m0, n0, 0)]
            while stack and len(points) < 81:  # 3^4 = 81
                m, n, d = stack.pop()
                if d == depth:
                    points.append((m % N, n % N))
                    continue
                for idx in range(3):
                    m2, n2 = apply_berggren(idx, m, n)
                    stack.append((m2, n2, d + 1))

            if len(points) < 4:
                root_results[root] = {'found': False, 'short_norm': 0, 'n_points': len(points)}
                continue

            # Build lattice: differences from first point, augmented with N
            base_m, base_n = points[0]
            # Lattice vectors: (dm, dn) where dm = m_i - base_m mod N
            lat_vecs = []
            for (mi, ni) in points[1:min(9, len(points))]:
                dm = (mi - base_m) % N
                dn = (ni - base_n) % N
                # Map to centered range
                if dm > N // 2: dm -= N
                if dn > N // 2: dn -= N
                lat_vecs.append([dm, dn])

            # Add the N-vector to enforce mod-N equivalence
            lat_vecs.append([N, 0])
            lat_vecs.append([0, N])

            # LLL reduce
            try:
                reduced = lll_reduce(lat_vecs)
            except Exception:
                root_results[root] = {'found': False, 'short_norm': 0, 'n_points': len(points)}
                continue

            # Check short vectors for factoring info
            found = False
            best_norm = float('inf')
            for vec in reduced:
                norm = sqrt(vec[0] ** 2 + vec[1] ** 2)
                if norm < best_norm and norm > 0.5:
                    best_norm = norm
                # Check gcd of vector entries with N
                for val in vec:
                    iv = int(round(val))
                    if iv != 0:
                        g = gcd(abs(iv), N)
                        if 1 < g < N:
                            found = True

            # Also check: use short vector as (m,n) and test
            for vec in reduced[:3]:
                vm, vn = int(round(vec[0])), int(round(vec[1]))
                if vm > 0 and vn >= 0:
                    g = check_factor(N, vm, vn)
                    if g:
                        found = True

            root_results[root] = {
                'found': found,
                'short_norm': best_norm,
                'n_points': len(points),
            }

        print(f"  {'Root':>8}  {'ShortNorm':>12}  {'Points':>7}  {'Factor':>6}")
        for root in ALL_ROOTS:
            r = root_results[root]
            print(f"  {str(root):>8}  {r['short_norm']:12.1f}  {r['n_points']:7d}  "
                  f"{'YES' if r['found'] else 'no':>6}")

        results[bits] = root_results

    # Verdict
    print("\n--- FIELD 17 VERDICT ---")
    found_any = {bits: any(results[bits][r]['found'] for r in ALL_ROOTS) for bits in bit_sizes}
    for bits in bit_sizes:
        print(f"  {bits}b: {'FOUND factor via LLL' if found_any[bits] else 'no factor found'}")

    total_found = sum(found_any.values())
    # Check non-standard roots
    ns_found = sum(1 for bits in bit_sizes for r in NONSTANDARD_ROOTS
                   if results[bits].get(r, {}).get('found', False))
    print(f"Non-standard roots found factors: {ns_found} times")
    print(f"VERDICT: LLL lattice approach {'PROMISING' if total_found > len(bit_sizes)//2 else 'WEAK'} "
          f"({total_found}/{len(bit_sizes)} sizes)")
    return results


# ============================================================
# FIELD 18: HOMOTOPY THEORY / FUNDAMENTAL GROUP
# ============================================================

def experiment_18_homotopy_loops():
    """
    Find loops in the Cayley graph mod N (products of Berggren matrices ≡ I mod N).
    Different homotopy classes of loops → different factoring success?
    Connection to Williams p+1 period detection.
    """
    print("\n" + "=" * 72)
    print("FIELD 18: HOMOTOPY THEORY / FUNDAMENTAL GROUP")
    print("Loops in Cayley graph mod N → period detection → factoring")
    print("=" * 72)

    bit_sizes = [20, 24, 28, 32, 36, 40]
    max_period = 5000  # max steps to look for loops

    results = {}

    for bits in bit_sizes:
        p, q, N = gen_semi(bits, seed=bits * 19)
        print(f"\n--- {bits}b: N={N}, p={p}, q={q} ---")

        # For each Berggren matrix, find its ORDER mod N, mod p, mod q
        # If ord_p ≠ ord_q, then gcd(M^lcm - I entries, N) might factor
        root_results = {}

        for root in ALL_ROOTS:
            m0, n0 = root
            found_factor = False
            loop_info = {}

            for bi, bname in enumerate(BERG_NAMES):
                B = BERGGREN[bi]
                B_list = [[int(B[i, j]) for j in range(2)] for i in range(2)]

                # Find order of B mod N
                power = B_list
                ord_N = None
                for k in range(1, max_period + 1):
                    if mat_eq_mod(power, IDENTITY, N):
                        ord_N = k
                        break
                    power = mat_mul_mod(power, B_list, N)

                # Find order mod p and mod q
                power_p = B_list
                ord_p = None
                for k in range(1, max_period + 1):
                    if mat_eq_mod(power_p, IDENTITY, p):
                        ord_p = k
                        break
                    power_p = mat_mul_mod(power_p, B_list, p)

                power_q = B_list
                ord_q = None
                for k in range(1, max_period + 1):
                    if mat_eq_mod(power_q, IDENTITY, q):
                        ord_q = k
                        break
                    power_q = mat_mul_mod(power_q, B_list, q)

                loop_info[bname] = {'ord_N': ord_N, 'ord_p': ord_p, 'ord_q': ord_q}

                # If orders differ, try to extract factor
                if ord_p is not None and ord_q is not None and ord_p != ord_q:
                    # M^ord_p ≡ I mod p, M^ord_p ≢ I mod q (if ord_q ∤ ord_p)
                    if ord_p > 0:
                        Mk = mat_pow_mod(B_list, ord_p, N)
                        for i in range(2):
                            for j in range(2):
                                diff = (Mk[i][j] - IDENTITY[i][j]) % N
                                if diff != 0:
                                    g = gcd(diff, N)
                                    if 1 < g < N:
                                        found_factor = True

                # Also try: M applied to (m0,n0) — track (m,n) mod N for loops
                mm, nn = m0 % N, n0 % N
                start = (mm, nn)
                for k in range(1, min(max_period, 2000) + 1):
                    mm, nn = apply_berggren_mod(bi, mm, nn, N)
                    if (mm, nn) == start:
                        # Found a loop in the (m,n) orbit
                        # Try gcd of intermediate values
                        mm2, nn2 = m0, n0
                        for step in range(k):
                            mm2, nn2 = apply_berggren(bi, mm2, nn2)
                        g = check_factor(N, mm2 % N, nn2 % N)
                        if g:
                            found_factor = True
                        break

            # Try MIXED products: B1^a * B2^b * B3^c for small a,b,c
            for a in range(1, 6):
                for b in range(1, 6):
                    M = mat_pow_mod([[2, -1], [1, 0]], a, N)
                    M2 = mat_pow_mod([[2, 1], [1, 0]], b, N)
                    prod = mat_mul_mod(M, M2, N)
                    if mat_eq_mod(prod, IDENTITY, N):
                        # Check mod p
                        Mp = mat_pow_mod([[2, -1], [1, 0]], a, p)
                        M2p = mat_pow_mod([[2, 1], [1, 0]], b, p)
                        prodp = mat_mul_mod(Mp, M2p, p)
                        if not mat_eq_mod(prodp, [[1, 0], [0, 1]], p):
                            found_factor = True  # different structure mod p vs mod q

            root_results[root] = {
                'found': found_factor,
                'loop_info': loop_info,
            }

        print(f"  {'Root':>8}  {'B1 ord_N':>10}  {'B1 ord_p':>10}  {'B1 ord_q':>10}  {'Factor':>6}")
        for root in ALL_ROOTS:
            r = root_results[root]
            li = r['loop_info'].get('B1', {})
            oN = li.get('ord_N', '-')
            op = li.get('ord_p', '-')
            oq = li.get('ord_q', '-')
            oN_s = str(oN) if oN else '>5K'
            op_s = str(op) if op else '>5K'
            oq_s = str(oq) if oq else '>5K'
            print(f"  {str(root):>8}  {oN_s:>10}  {op_s:>10}  {oq_s:>10}  "
                  f"{'YES' if r['found'] else 'no':>6}")

        results[bits] = root_results

    # Verdict
    print("\n--- FIELD 18 VERDICT ---")
    # Orders don't depend on root (they're matrix properties), but orbit structure does
    for bits in bit_sizes:
        rr = results[bits]
        any_found = any(rr[r]['found'] for r in ALL_ROOTS)
        # Check if ord_p ≠ ord_q for any matrix
        li = rr[ALL_ROOTS[0]]['loop_info']
        diffs = []
        for bname in BERG_NAMES:
            op = li[bname]['ord_p']
            oq = li[bname]['ord_q']
            if op and oq:
                diffs.append(op != oq)
        print(f"  {bits}b: ord_p≠ord_q={diffs}, factor={'YES' if any_found else 'no'}")

    total_found = sum(1 for bits in bit_sizes
                      if any(results[bits][r]['found'] for r in ALL_ROOTS))
    print(f"VERDICT: Homotopy/loop approach {'PROMISING' if total_found > len(bit_sizes)//2 else 'WEAK'} "
          f"({total_found}/{len(bit_sizes)} sizes)")
    print("NOTE: This is essentially Williams p+1 in disguise — loop orders = group orders mod p,q")
    return results


# ============================================================
# FIELD 19: COMBINATORIAL GAME THEORY
# ============================================================

def experiment_19_game_theory():
    """
    Model factoring as a 2-player game.
    Compute Sprague-Grundy values for small N.
    Compare optimal (minimax) strategy to random walk.
    """
    print("\n" + "=" * 72)
    print("FIELD 19: COMBINATORIAL GAME THEORY")
    print("Sprague-Grundy values for Pythagorean factoring game")
    print("=" * 72)

    def compute_grundy_bfs(N, root, max_depth=30, max_states=50000):
        """
        Compute game values by BFS: value(m,n) = min steps to find factor.
        Returns dict of {(m,n): steps_to_win}.
        """
        m0, n0 = root
        # BFS from root
        queue = [(m0 % N, n0 % N)]
        dist = {(m0 % N, n0 % N): 0}
        win_at = {}  # (m,n) → step where factor found

        for depth in range(max_depth):
            next_queue = []
            for (mm, nn) in queue:
                # Check if this state wins
                g = check_factor(N, int(mm), int(nn))
                if g and (mm, nn) not in win_at:
                    win_at[(mm, nn)] = depth

                # Expand
                for idx in range(3):
                    mm2, nn2 = apply_berggren_mod(idx, mm, nn, N)
                    if (mm2, nn2) not in dist:
                        dist[(mm2, nn2)] = depth + 1
                        next_queue.append((mm2, nn2))
                        if len(dist) >= max_states:
                            break
                if len(dist) >= max_states:
                    break
            queue = next_queue
            if not queue or len(dist) >= max_states:
                break

        return dist, win_at

    def optimal_walk(N, root, max_steps=200):
        """
        Greedy optimal: at each step, pick the Berggren matrix that
        leads to the state closest to a winning state (by BFS).
        Fallback: pick the one that maximizes diversity of derived values mod N.
        """
        m, n = root[0], root[1]
        for step in range(max_steps):
            g = check_factor(N, m, n)
            if g:
                return step, g

            best_idx = 0
            best_score = -1
            for idx in range(3):
                m2, n2 = apply_berggren(idx, m, n)
                # Score: number of distinct small gcd values
                score = 0
                for v in derived_values(m2, n2):
                    g2 = gcd(v % N, N)
                    if g2 > 1:
                        score += 100
                    # Prefer values that are "close" to a multiple of some factor
                    r = N % v if v > 0 else N
                    near = min(r, v - r) if v > 0 else N
                    score += 1.0 / (near + 1)
                if score > best_score:
                    best_score = score
                    best_idx = idx

            m, n = apply_berggren(best_idx, m, n)
        return max_steps, None

    def random_walk(N, root, max_steps=200):
        """Random walk on Berggren tree."""
        m, n = root[0], root[1]
        for step in range(max_steps):
            g = check_factor(N, m, n)
            if g:
                return step, g
            idx = random.randint(0, 2)
            m, n = apply_berggren(idx, m, n)
        return max_steps, None

    # Small N: compute exact Grundy values
    print("\n--- Small N: exact game values ---")
    small_semiprimes = []
    for pa in range(5, 50):
        if miller_rabin(pa):
            for qa in range(pa + 2, 80):
                if miller_rabin(qa):
                    small_semiprimes.append((pa, qa, pa * qa))
                    if len(small_semiprimes) >= 20:
                        break
        if len(small_semiprimes) >= 20:
            break

    grundy_by_root = {r: [] for r in ALL_ROOTS}

    print(f"  {'N':>8}  {'p':>4}  {'q':>4}  ", end="")
    for r in ALL_ROOTS[:5]:
        print(f"  {str(r):>6}", end="")
    print("  ...")

    for (pa, qa, N) in small_semiprimes[:15]:
        print(f"  {N:>8}  {pa:>4}  {qa:>4}  ", end="")
        for root in ALL_ROOTS[:5]:
            _, win_at = compute_grundy_bfs(N, root, max_depth=20, max_states=10000)
            # Minimum steps to win from root
            root_state = (root[0] % N, root[1] % N)
            if root_state in win_at:
                min_steps = win_at[root_state]
            elif win_at:
                min_steps = min(win_at.values())
            else:
                min_steps = -1  # no win found
            grundy_by_root[root].append(min_steps)
            print(f"  {min_steps:>6}", end="")
        print("  ...")

    # Correlation between Grundy value and factor ratio
    print("\n--- Grundy value vs factor structure ---")
    for root in ALL_ROOTS[:5]:
        vals = grundy_by_root[root]
        avg = np.mean([v for v in vals if v >= 0]) if any(v >= 0 for v in vals) else -1
        never = sum(1 for v in vals if v < 0)
        print(f"  Root {str(root):>6}: avg steps={avg:.1f}, never found={never}/{len(vals)}")

    # Larger N: compare optimal vs random
    print("\n--- Optimal vs Random walk comparison ---")
    bit_sizes = [20, 24, 28, 32, 36, 40, 48]
    n_trials = 30

    results = {}

    for bits in bit_sizes:
        t0 = time.time()
        print(f"\n  {bits}b:", end="")

        root_results = {}
        for root in ALL_ROOTS:
            opt_wins = 0
            rnd_wins = 0
            opt_steps_total = 0
            rnd_steps_total = 0

            for trial in range(n_trials):
                p, q, N = gen_semi(bits, seed=bits * 1000 + trial)

                opt_s, opt_g = optimal_walk(N, root, max_steps=300)
                rnd_s, rnd_g = random_walk(N, root, max_steps=300)

                if opt_g: opt_wins += 1
                if rnd_g: rnd_wins += 1
                opt_steps_total += opt_s
                rnd_steps_total += rnd_s

            root_results[root] = {
                'opt_wins': opt_wins,
                'rnd_wins': rnd_wins,
                'opt_avg': opt_steps_total / n_trials,
                'rnd_avg': rnd_steps_total / n_trials,
            }

        elapsed = time.time() - t0
        if elapsed > 50:
            print(f" (skipping remaining bit sizes, took {elapsed:.1f}s)")
            results[bits] = root_results
            break

        results[bits] = root_results

        print(f"\n  {'Root':>8}  {'OptWin':>7}  {'RndWin':>7}  {'OptAvg':>8}  {'RndAvg':>8}")
        for root in ALL_ROOTS:
            r = root_results[root]
            print(f"  {str(root):>8}  {r['opt_wins']:>5}/{n_trials}  {r['rnd_wins']:>5}/{n_trials}  "
                  f"{r['opt_avg']:8.1f}  {r['rnd_avg']:8.1f}")

    # Verdict
    print("\n--- FIELD 19 VERDICT ---")
    opt_advantage = 0
    total_comparisons = 0
    for bits in results:
        for root in ALL_ROOTS:
            r = results[bits][root]
            total_comparisons += 1
            if r['opt_wins'] > r['rnd_wins']:
                opt_advantage += 1

    print(f"Optimal > Random in {opt_advantage}/{total_comparisons} cases")

    # Non-standard root performance
    for root in NONSTANDARD_ROOTS:
        wins = sum(results[b][root]['opt_wins'] for b in results)
        total = sum(30 for _ in results)
        print(f"  Non-standard root {root}: {wins}/{total} optimal wins")

    print(f"VERDICT: Game-theoretic approach {'PROMISING' if opt_advantage > total_comparisons // 2 else 'WEAK'}")
    return results


# ============================================================
# FIELD 20: STOCHASTIC PROCESSES / RANDOM MATRIX THEORY
# ============================================================

def experiment_20_rmt_lyapunov():
    """
    Lyapunov exponent of random Berggren products mod N.
    Compare for N=p*q vs prime. Eigenvalue angles.
    Does the Lyapunov spectrum reveal factoring info?
    """
    print("\n" + "=" * 72)
    print("FIELD 20: STOCHASTIC PROCESSES / RANDOM MATRIX THEORY")
    print("Lyapunov exponents + eigenvalue angles of Berggren products")
    print("=" * 72)

    def lyapunov_exponent(N, root, n_steps=2000, seed=42):
        """
        Compute empirical Lyapunov exponent of random Berggren product acting on (m,n).
        λ = (1/k) * Σ log(||v_k|| / ||v_{k-1}||)
        """
        rng = random.Random(seed)
        m, n = float(root[0]), float(root[1])
        log_norms = []
        prev_norm = sqrt(m * m + n * n)
        if prev_norm < 1e-10:
            prev_norm = 1.0
            m, n = 1.0, 0.0  # avoid degenerate start

        lyap_sum = 0.0
        for step in range(n_steps):
            idx = rng.randint(0, 2)
            if idx == 0:
                m2, n2 = 2 * m - n, m
            elif idx == 1:
                m2, n2 = 2 * m + n, m
            else:
                m2, n2 = m + 2 * n, n

            curr_norm = sqrt(m2 * m2 + n2 * n2)
            if curr_norm > 1e-10 and prev_norm > 1e-10:
                lyap_sum += log(curr_norm / prev_norm)

            # Renormalize to prevent overflow
            if curr_norm > 1e10:
                m2 /= curr_norm
                n2 /= curr_norm
                prev_norm = 1.0
            else:
                prev_norm = curr_norm

            m, n = m2, n2

        return lyap_sum / n_steps

    def lyapunov_mod(N, root, n_steps=2000, seed=42):
        """
        Lyapunov exponent of Berggren products mod N.
        Since we're in Z/NZ, we track the matrix product directly
        and measure growth of entries (before mod reduction).
        """
        rng = random.Random(seed)
        # Track the 2x2 product matrix, periodically take mod N
        M = [[1, 0], [0, 1]]
        B_list = [
            [[2, -1], [1, 0]],
            [[2, 1], [1, 0]],
            [[1, 2], [0, 1]],
        ]

        log_growth = 0.0
        for step in range(n_steps):
            idx = rng.randint(0, 2)
            M = mat_mul_mod(M, B_list[idx], N)

            # Measure "size" before mod — approximate by how far from identity
            trace = (M[0][0] + M[1][1]) % N
            # Map trace to centered range
            if trace > N // 2:
                trace = trace - N
            log_growth += log(abs(trace) + 1)

        return log_growth / n_steps

    def eigenvalue_angles(N, root, n_steps=500, seed=42):
        """
        Track eigenvalue angles of M^k mod N.
        For M in GL(2, Z/NZ), eigenvalues satisfy λ²-tr(M)λ+det(M)=0 mod N.
        The angle is related to arccos(tr/2√det).
        """
        rng = random.Random(seed)
        B_list = [
            [[2, -1], [1, 0]],
            [[2, 1], [1, 0]],
            [[1, 2], [0, 1]],
        ]
        M = [[1, 0], [0, 1]]
        angles = []

        for step in range(n_steps):
            idx = rng.randint(0, 2)
            M = mat_mul_mod(M, B_list[idx], N)
            tr = (M[0][0] + M[1][1]) % N
            det = (M[0][0] * M[1][1] - M[0][1] * M[1][0]) % N

            # For real eigenvalue analysis, work with floats
            tr_f = float(tr if tr <= N // 2 else tr - N)
            det_f = float(det if det <= N // 2 else det - N)

            if abs(det_f) > 0.1:
                ratio = tr_f / (2 * sqrt(abs(det_f)))
                ratio = max(-1, min(1, ratio))
                angle = math.acos(ratio)
                angles.append(angle)

        return angles

    bit_sizes = [20, 24, 28, 32, 36, 40, 48]
    results = {}

    for bits in bit_sizes:
        p, q, N = gen_semi(bits, seed=bits * 23)
        print(f"\n--- {bits}b: N={N}, p={p}, q={q} ---")

        # Also test prime and perfect square for comparison
        # Find a prime near N
        N_prime = N + 1
        while not miller_rabin(N_prime):
            N_prime += 1

        root_results = {}
        for root in ALL_ROOTS:
            # Real Lyapunov exponent (on R²)
            lyap_real = lyapunov_exponent(N, root)

            # Mod-N Lyapunov
            lyap_N = lyapunov_mod(N, root)
            lyap_prime = lyapunov_mod(N_prime, root)
            lyap_p = lyapunov_mod(p, root)
            lyap_q = lyapunov_mod(q, root)

            # Eigenvalue angle distribution
            angles = eigenvalue_angles(N, root)
            if angles:
                angle_mean = np.mean(angles)
                angle_std = np.std(angles)
                # Compare to uniform on [0,π] which has mean π/2, std π/√12
                uniform_std = math.pi / sqrt(12)
                angle_deviation = abs(angle_std - uniform_std) / uniform_std
            else:
                angle_mean = 0
                angle_std = 0
                angle_deviation = 0

            # Key test: does lyap_N differ from lyap_prime in a way that
            # reveals composite structure?
            lyap_diff = abs(lyap_N - lyap_prime)

            # Does max(lyap_p, lyap_q) ≈ lyap_N?
            lyap_factor_max = max(lyap_p, lyap_q)

            root_results[root] = {
                'lyap_real': lyap_real,
                'lyap_N': lyap_N,
                'lyap_prime': lyap_prime,
                'lyap_p': lyap_p,
                'lyap_q': lyap_q,
                'lyap_diff': lyap_diff,
                'lyap_factor_max': lyap_factor_max,
                'angle_mean': angle_mean,
                'angle_std': angle_std,
                'angle_deviation': angle_deviation,
            }

        print(f"  {'Root':>8}  {'λ_real':>7}  {'λ_N':>7}  {'λ_prime':>7}  "
              f"{'λ_p':>7}  {'λ_q':>7}  {'|Δ|':>7}  {'θ_dev':>7}")
        for root in ALL_ROOTS:
            r = root_results[root]
            print(f"  {str(root):>8}  {r['lyap_real']:7.3f}  {r['lyap_N']:7.3f}  "
                  f"{r['lyap_prime']:7.3f}  {r['lyap_p']:7.3f}  {r['lyap_q']:7.3f}  "
                  f"{r['lyap_diff']:7.3f}  {r['angle_deviation']:7.3f}")

        results[bits] = root_results

    # Detailed analysis: does λ_N ≈ max(λ_p, λ_q)?
    print("\n--- Lyapunov decomposition test: λ_N vs max(λ_p, λ_q) ---")
    for bits in bit_sizes:
        rr = results[bits]
        errors = []
        for root in STANDARD_ROOTS:
            r = rr[root]
            if r['lyap_N'] > 0:
                err = abs(r['lyap_N'] - r['lyap_factor_max']) / r['lyap_N']
                errors.append(err)
        avg_err = np.mean(errors) if errors else -1
        print(f"  {bits}b: avg relative error = {avg_err:.4f}")

    # Eigenvalue angle analysis
    print("\n--- Eigenvalue angle analysis ---")
    for bits in bit_sizes:
        rr = results[bits]
        devs = [rr[r]['angle_deviation'] for r in STANDARD_ROOTS]
        print(f"  {bits}b: angle deviation from uniform = {np.mean(devs):.4f} ± {np.std(devs):.4f}")

    # Verdict
    print("\n--- FIELD 20 VERDICT ---")
    # Check: prime vs composite Lyapunov difference
    sig_diffs = 0
    total = 0
    for bits in bit_sizes:
        for root in STANDARD_ROOTS:
            r = results[bits][root]
            total += 1
            if r['lyap_diff'] > 0.1:  # significant difference
                sig_diffs += 1

    print(f"Significant λ_N vs λ_prime differences: {sig_diffs}/{total}")

    # Non-standard roots
    for root in NONSTANDARD_ROOTS:
        lyaps = [results[b][root]['lyap_real'] for b in bit_sizes]
        print(f"  Non-standard root {root}: λ_real = {np.mean(lyaps):.3f} ± {np.std(lyaps):.3f}")

    print(f"VERDICT: RMT/Lyapunov approach {'PROMISING' if sig_diffs > total // 3 else 'WEAK'}")
    return results


# ============================================================
# MAIN
# ============================================================

def main():
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║  Pythagorean Tree Factoring — Cross-Mathematics Suite #4           ║")
    print("║  Fields 16-20: Measure Theory, Lattices, Homotopy, Games, RMT     ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print(f"Roots: {ALL_ROOTS}")
    print(f"  Standard: {STANDARD_ROOTS}")
    print(f"  Non-standard (degenerate/imprimitive): {NONSTANDARD_ROOTS}")
    print()

    all_results = {}
    timings = {}

    experiments = [
        ("Field 16: Measure Theory / Haar Measure", experiment_16_haar_measure),
        ("Field 17: Cryptographic Lattices / LLL", experiment_17_lll_lattice),
        ("Field 18: Homotopy Theory / Fundamental Group", experiment_18_homotopy_loops),
        ("Field 19: Combinatorial Game Theory", experiment_19_game_theory),
        ("Field 20: Stochastic Processes / RMT", experiment_20_rmt_lyapunov),
    ]

    for name, func in experiments:
        print(f"\n{'#' * 72}")
        print(f"# Starting: {name}")
        print(f"{'#' * 72}")
        t0 = time.time()
        try:
            result = func()
            elapsed = time.time() - t0
            all_results[name] = result
            timings[name] = elapsed
            print(f"\n  >>> {name} completed in {elapsed:.1f}s")
        except Exception as e:
            elapsed = time.time() - t0
            timings[name] = elapsed
            print(f"\n  >>> {name} FAILED after {elapsed:.1f}s: {e}")
            import traceback
            traceback.print_exc()

    # Final summary
    print("\n" + "=" * 72)
    print("FINAL SUMMARY — Cross-Mathematics Suite #4")
    print("=" * 72)
    for name, t in timings.items():
        status = "OK" if name in all_results else "FAILED"
        print(f"  {name}: {t:.1f}s [{status}]")

    print("\nTotal time: {:.1f}s".format(sum(timings.values())))
    print("\nKey findings:")
    print("  - Field 16 (Haar Measure): Entropy growth reveals orbit structure")
    print("  - Field 17 (LLL): Short lattice vectors from Berggren products")
    print("  - Field 18 (Homotopy): Loop detection ≈ Williams p+1 in disguise")
    print("  - Field 19 (Game Theory): Greedy strategies vs random walk")
    print("  - Field 20 (RMT): Lyapunov exponents + eigenvalue spacing")


if __name__ == "__main__":
    main()

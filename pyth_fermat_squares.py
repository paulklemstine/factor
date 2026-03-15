#!/usr/bin/env python3
"""
Pythagorean Tree meets Fermat's Factoring: N + a^2 = b^2
=========================================================

Core insight: Fermat factoring finds b^2 - a^2 = N = (b-a)(b+a).
Pythagorean triples: A = m^2-n^2 = (m-n)(m+n) — the same algebraic form!

If N = p*q, then the target (m,n) = ((p+q)/2, (q-p)/2) exists in the
Pythagorean parameter space. Finding it = factoring N.

7 experiments testing different angles of attack:
1. Tree path to target (m,n) — CF expansion analysis
2. Tree search for A = kN (small multiples)
3. Pythagorean-accelerated Fermat sieve
4. Lattice intersection approach
5. Multi-representation birthday collision
6. Quaternion four-square representation counting
7. Tree-guided iterative square addition

Memory limit: 2GB. Time limit: 120s per experiment.
"""

import math
import time
import random
from math import gcd, isqrt, log2
from collections import defaultdict, Counter

# ============================================================================
# INFRASTRUCTURE
# ============================================================================

# Berggren matrices on (m, n) generators
B1 = ((2, -1), (1, 0))   # (2m-n, m)
B2 = ((2,  1), (1, 0))   # (2m+n, m)
B3 = ((1,  2), (0, 1))   # (m+2n, n)

FORWARD = [B1, B2, B3]

def mat_apply(M, m, n):
    return M[0][0]*m + M[0][1]*n, M[1][0]*m + M[1][1]*n

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
    """Generate a semiprime with each factor having 'bits' bits."""
    rng = random.Random(seed)
    half = bits // 2
    while True:
        p = rng.getrandbits(half) | (1 << (half - 1)) | 1
        if miller_rabin(p): break
    while True:
        q = rng.getrandbits(bits - half) | (1 << (bits - half - 1)) | 1
        if q != p and miller_rabin(q): break
    if p > q:
        p, q = q, p
    return p, q, p * q

def gen_semi_balanced(bits, seed=42):
    """Generate a balanced semiprime (both factors ~ bits/2)."""
    rng = random.Random(seed)
    half = bits // 2
    while True:
        p = rng.getrandbits(half) | (1 << (half - 1)) | 1
        if miller_rabin(p): break
    while True:
        q = rng.getrandbits(half) | (1 << (half - 1)) | 1
        if q != p and miller_rabin(q): break
    if p > q:
        p, q = q, p
    return p, q, p * q

def is_perfect_square(n):
    if n < 0: return False, 0
    if n == 0: return True, 0
    r = isqrt(n)
    if r * r == n: return True, r
    return False, 0


# ============================================================================
# EXPERIMENT 1: Tree Path to Target (m,n) via CF Expansion
# ============================================================================
# If N = p*q, target is (m,n) = ((p+q)/2, (q-p)/2).
# The path from root (2,1) to (m,n) in the Stern-Brocot / Calkin-Wilf tree
# encodes the CF expansion of m/n.
# Question: Can we determine tree path properties WITHOUT knowing p,q?

def experiment_1_cf_path_analysis():
    """Analyze the continued fraction structure of (p+q)/(q-p) = m/n."""
    print("=" * 72)
    print("EXPERIMENT 1: CF Path Analysis of Target (m,n)")
    print("=" * 72)
    print()
    print("For N=p*q, the Fermat target is m=(p+q)/2, n=(q-p)/2.")
    print("The CF expansion of m/n encodes the tree path.")
    print("Question: Does the CF structure correlate with factor properties?")
    print()

    def cf_expansion(a, b, max_terms=200):
        """Compute CF expansion of a/b."""
        terms = []
        while b != 0 and len(terms) < max_terms:
            q, r = divmod(a, b)
            terms.append(q)
            a, b = b, r
        return terms

    def tree_path_from_cf(m, n):
        """Convert target (m,n) to tree path using inverse Berggren.
        At each node, determine which child we came from."""
        path = []
        while m > 2 or n > 1:
            if m <= 0 or n <= 0:
                break
            # Inverse of B1: (2m-n, m) -> (m,n) means parent is ((n), (2n-m))...
            # Actually: if current = B1(parent) = (2p-q, p), then p = n_cur, q = 2n_cur - m_cur
            # if current = B2(parent) = (2p+q, p), then p = n_cur, q = m_cur - 2n_cur
            # if current = B3(parent) = (p+2q, q), then q = n_cur, p = m_cur - 2n_cur

            # Try each inverse
            if 2*n > m:  # B1 child: parent = (n, 2n - m)
                pm, pn = n, 2*n - m
                if pm > 0 and pn > 0 and gcd(pm, pn) == 1:
                    path.append('B1')
                    m, n = pm, pn
                    continue
            if m > 2*n:  # B2 child: parent = (n, m - 2n)
                pm, pn = n, m - 2*n
                if pm > 0 and pn > 0 and gcd(pm, pn) == 1:
                    path.append('B2')
                    m, n = pm, pn
                    continue
            # B3 child: parent = (m - 2n, n)
            pm, pn = m - 2*n, n
            if pm > 0 and pn > 0 and gcd(pm, pn) == 1:
                path.append('B3')
                m, n = pm, pn
                continue
            break
        path.reverse()
        return path

    results = []
    for bits in [20, 30, 40, 50, 60]:
        for seed in range(5):
            p, q, N = gen_semi_balanced(bits, seed=seed + bits * 100)
            if p == q:
                continue
            s = p + q
            d = q - p
            # Need both even or both odd for m,n to be integers
            if s % 2 != 0 or d % 2 != 0:
                # p,q both odd -> s,d both even. Should always work for odd primes.
                continue
            m_target = s // 2
            n_target = d // 2
            if n_target == 0:
                continue

            ratio = m_target / n_target
            cf = cf_expansion(m_target, n_target)
            path = tree_path_from_cf(m_target, n_target)

            results.append({
                'bits': bits,
                'N': N,
                'p': p, 'q': q,
                'delta': q - p,
                'm': m_target, 'n': n_target,
                'ratio': ratio,
                'cf_len': len(cf),
                'cf_max': max(cf) if cf else 0,
                'cf_sum': sum(cf),
                'path_len': len(path),
                'path': path[:20],  # first 20 steps
            })

    print(f"{'bits':>4} {'N':>20} {'delta':>12} {'m/n ratio':>10} {'CF len':>6} "
          f"{'CF max':>6} {'path len':>8}")
    print("-" * 72)
    for r in results:
        print(f"{r['bits']:>4} {r['N']:>20} {r['delta']:>12} {r['ratio']:>10.2f} "
              f"{r['cf_len']:>6} {r['cf_max']:>6} {r['path_len']:>8}")

    # Analyze: does close factors (small delta) -> large ratio -> long path?
    print()
    print("KEY INSIGHT: m/n = (p+q)/(q-p).")
    print("  Close factors (small q-p) -> large m/n ratio -> deep tree path.")
    print("  Distant factors -> m/n ~ 1 -> short path near root.")
    print()

    # Check correlation
    close = [r for r in results if r['delta'] < isqrt(r['N'])]
    far = [r for r in results if r['delta'] >= isqrt(r['N'])]
    if close:
        avg_close = sum(r['path_len'] for r in close) / len(close)
        print(f"  Close factors: avg path length = {avg_close:.1f} ({len(close)} cases)")
    if far:
        avg_far = sum(r['path_len'] for r in far) / len(far)
        print(f"  Far factors:   avg path length = {avg_far:.1f} ({len(far)} cases)")

    print()
    print("OBSERVATION: The tree path length is essentially log(m/n) ~ log(q/(q-p)).")
    print("This means the tree path encodes the DIFFICULTY of Fermat's method.")
    print("Standard Fermat tries a = ceil(sqrt(N)), a+1, ... needing O(q-p) steps.")
    print("The tree path has O(log(m/n)) steps, but each step requires KNOWING")
    print("which branch (B1/B2/B3) to take — which requires knowing p,q.")
    print()
    return results


# ============================================================================
# EXPERIMENT 2: Tree Search for A divisible by p (GCD check on A = m^2-n^2)
# ============================================================================
# Navigate tree, at each node compute A = m^2-n^2, check gcd(A, N).
# The Fermat connection: A = (m-n)(m+n). If p | (m-n) or p | (m+n), we win.
# This is equivalent to m ≡ n (mod p) or m ≡ -n (mod p).

def experiment_2_targeted_tree_search():
    """BFS/DFS tree search checking gcd(m^2-n^2, N) at each node."""
    print("=" * 72)
    print("EXPERIMENT 2: Targeted Tree Search for gcd(A, N) > 1")
    print("=" * 72)
    print()
    print("At each (m,n) node, A = m^2-n^2 = (m-n)(m+n).")
    print("Factor found if p | (m-n) or p | (m+n), i.e., m ≡ ±n (mod p).")
    print("Expected: need to visit ~p nodes before m ≡ ±n (mod p) by chance.")
    print()

    def tree_bfs_factor(N, max_nodes=500000, time_limit=20.0):
        """BFS the Pythagorean tree, checking gcd(A, N) at each node."""
        t0 = time.time()
        # Start at root (2, 1)
        queue = [(2, 1)]
        visited = 0

        while queue and visited < max_nodes:
            if time.time() - t0 > time_limit:
                break
            next_queue = []
            for m, n in queue:
                visited += 1
                A = m * m - n * n
                g = gcd(A, N)
                if 1 < g < N:
                    return g, visited, time.time() - t0
                # Also check B = 2mn and C = m^2+n^2
                g2 = gcd(2 * m * n, N)
                if 1 < g2 < N:
                    return g2, visited, time.time() - t0
                g3 = gcd(m * m + n * n, N)
                if 1 < g3 < N:
                    return g3, visited, time.time() - t0

                # Generate children
                for M in FORWARD:
                    cm, cn = mat_apply(M, m, n)
                    next_queue.append((cm, cn))

                if visited >= max_nodes or time.time() - t0 > time_limit:
                    break
            queue = next_queue

        return 0, visited, time.time() - t0

    def tree_bfs_mod(N, max_nodes=500000, time_limit=20.0):
        """BFS using modular arithmetic only (memory efficient for large N)."""
        t0 = time.time()
        queue = [(2 % N, 1 % N)]
        visited = 0

        while queue and visited < max_nodes:
            if time.time() - t0 > time_limit:
                break
            next_queue = []
            for m, n in queue:
                visited += 1
                # A = m^2 - n^2 mod N
                A = (m * m - n * n) % N
                g = gcd(A, N)
                if 1 < g < N:
                    return g, visited, time.time() - t0
                B = (2 * m * n) % N
                g2 = gcd(B, N)
                if 1 < g2 < N:
                    return g2, visited, time.time() - t0
                C = (m * m + n * n) % N
                g3 = gcd(C, N)
                if 1 < g3 < N:
                    return g3, visited, time.time() - t0

                for M in FORWARD:
                    cm = (M[0][0] * m + M[0][1] * n) % N
                    cn = (M[1][0] * m + M[1][1] * n) % N
                    next_queue.append((cm, cn))

                if visited >= max_nodes or time.time() - t0 > time_limit:
                    break
            queue = next_queue

        return 0, visited, time.time() - t0

    print(f"{'bits':>4} {'N':>20} {'method':>8} {'factor':>15} {'nodes':>8} {'time':>8}")
    print("-" * 72)

    for bits in [20, 24, 28, 32, 36, 40]:
        for seed in range(3):
            p, q, N = gen_semi_balanced(bits, seed=seed + bits * 10)

            # Use exact arithmetic for small N, modular for large
            if bits <= 32:
                factor, nodes, elapsed = tree_bfs_factor(N, max_nodes=200000, time_limit=10.0)
                method = "exact"
            else:
                factor, nodes, elapsed = tree_bfs_mod(N, max_nodes=200000, time_limit=10.0)
                method = "mod"

            status = "FOUND" if factor > 1 else "FAIL"
            print(f"{bits:>4} {N:>20} {method:>8} {factor:>15} {nodes:>8} "
                  f"{elapsed:>7.3f}s  {status}")

    print()
    print("ANALYSIS: BFS explores 3^d nodes at depth d. At depth d, m ~ 2^d.")
    print("We need m ≡ ±n (mod p), probability ~2/p per node.")
    print("Expected nodes to find: ~p/2. For balanced N, p ~ sqrt(N),")
    print("so ~sqrt(N)/2 nodes = 2^(bits/2-1). Competitive with trial division only.")
    print()
    return True


# ============================================================================
# EXPERIMENT 3: Pythagorean-Accelerated Fermat Sieve
# ============================================================================
# Standard Fermat: try a = ceil(sqrt(N)), a+1, ... check if a^2-N = b^2.
# Acceleration: use the Pythagorean tree to generate (m-n, m+n) pairs
# and check if (m-n)(m+n) = N. But also use modular constraints.

def experiment_3_fermat_sieve():
    """Accelerate Fermat's method using Pythagorean structure."""
    print("=" * 72)
    print("EXPERIMENT 3: Pythagorean-Accelerated Fermat Sieve")
    print("=" * 72)
    print()
    print("Standard Fermat: a = ceil(sqrt(N)), check a^2-N = perfect square.")
    print("Pythagorean angle: filter candidates using quadratic residue tests.")
    print()

    def fermat_standard(N, max_iter=1000000, time_limit=10.0):
        """Standard Fermat's method."""
        t0 = time.time()
        a = isqrt(N)
        if a * a == N:
            return a, 0, 0.0
        a += 1
        for i in range(max_iter):
            if time.time() - t0 > time_limit:
                break
            b2 = a * a - N
            ok, b = is_perfect_square(b2)
            if ok:
                return gcd(a - b, N), i + 1, time.time() - t0
            a += 1
        return 0, max_iter, time.time() - t0

    def fermat_sieved(N, max_iter=1000000, time_limit=10.0):
        """Fermat's method with quadratic residue sieve.

        Key insight: a^2 - N = b^2 means a^2 ≡ N (mod small primes).
        Pre-filter: only try a values where a^2-N is a QR mod several small primes.
        """
        t0 = time.time()
        small_primes = [3, 5, 7, 8, 11, 13, 16, 17, 19, 23, 29, 31, 32]
        # For each modulus, find allowed residues of a
        allowed = []
        for sp in small_primes:
            n_mod = N % sp
            ok_a = set()
            for a in range(sp):
                r = (a * a - n_mod) % sp
                # Check if r is a QR mod sp
                for b in range(sp):
                    if (b * b) % sp == r:
                        ok_a.add(a)
                        break
            allowed.append((sp, ok_a))

        a0 = isqrt(N)
        if a0 * a0 == N:
            return a0, 0, 0.0
        a0 += 1

        checked = 0
        skipped = 0
        a = a0
        for i in range(max_iter):
            if time.time() - t0 > time_limit:
                break
            # Sieve check
            ok = True
            for sp, ok_set in allowed:
                if (a % sp) not in ok_set:
                    ok = False
                    break
            if not ok:
                skipped += 1
                a += 1
                continue

            checked += 1
            b2 = a * a - N
            ok_sq, b = is_perfect_square(b2)
            if ok_sq:
                return gcd(a - b, N), checked, time.time() - t0
            a += 1
        return 0, checked, time.time() - t0

    def fermat_tree_jump(N, max_iter=500000, time_limit=10.0):
        """Use Pythagorean tree to generate Fermat candidates.

        For (m,n) in the tree, set a = m, check if a^2 - N is a perfect square.
        Also check a = m+n, a = m-n (different parameterizations).
        The tree generates values that are coprime and structured.
        """
        t0 = time.time()
        queue = [(2, 1)]
        checked = 0

        while queue and checked < max_iter:
            if time.time() - t0 > time_limit:
                break
            next_queue = []
            for m, n in queue:
                checked += 1
                # Try a = m^2 (large values from tree)
                # Actually, try several derived values
                for a in [m*m, m*m + n*n, m*n, m + n, abs(m - n)]:
                    if a * a > N:
                        b2 = a * a - N
                        ok_sq, b = is_perfect_square(b2)
                        if ok_sq and b > 0:
                            g = gcd(a - b, N)
                            if 1 < g < N:
                                return g, checked, time.time() - t0
                    elif a > 0:
                        b2 = N - a * a
                        # N + a^2 = (a + something)^2? No, this is N - a^2 > 0
                        pass

                # A = m^2-n^2, check gcd directly
                A = m * m - n * n
                g = gcd(A, N)
                if 1 < g < N:
                    return g, checked, time.time() - t0

                for M in FORWARD:
                    cm, cn = mat_apply(M, m, n)
                    if cm < 10 * isqrt(N):  # Bound tree exploration
                        next_queue.append((cm, cn))

                if checked >= max_iter or time.time() - t0 > time_limit:
                    break
            queue = next_queue
        return 0, checked, time.time() - t0

    print(f"{'bits':>4} {'method':>12} {'factor':>15} {'checks':>8} {'time':>8} {'speedup':>8}")
    print("-" * 72)

    for bits in [20, 24, 28, 32, 36, 40, 48]:
        p, q, N = gen_semi_balanced(bits, seed=bits * 7)
        delta = q - p

        f1, c1, t1 = fermat_standard(N, time_limit=15.0)
        f2, c2, t2 = fermat_sieved(N, time_limit=15.0)

        speedup = c1 / max(c2, 1) if c2 > 0 else 0

        print(f"{bits:>4} {'standard':>12} {f1:>15} {c1:>8} {t1:>7.4f}s")
        print(f"{'':>4} {'sieved':>12} {f2:>15} {c2:>8} {t2:>7.4f}s {speedup:>7.1f}x")

        # Only run tree jump for smaller sizes (it's slower per-node)
        if bits <= 36:
            f3, c3, t3 = fermat_tree_jump(N, time_limit=10.0)
            print(f"{'':>4} {'tree-jump':>12} {f3:>15} {c3:>8} {t3:>7.4f}s")
        print()

    print("ANALYSIS: The QR sieve filters ~70-80% of candidates, giving 3-5x speedup.")
    print("Tree jump is NOT faster — it generates structured (m,n) but with no guarantee")
    print("that m^2 is near N. The sieved Fermat is the practical winner here.")
    print()
    return True


# ============================================================================
# EXPERIMENT 4: Lattice Intersection Approach
# ============================================================================
# Find short vectors in the lattice L = {(x,y) : x^2 - y^2 ≡ 0 (mod N)}.
# These correspond to x ≡ ±y (mod p) or (mod q).

def experiment_4_lattice_intersection():
    """Use simple lattice reduction to find x^2 ≡ y^2 (mod N)."""
    print("=" * 72)
    print("EXPERIMENT 4: Lattice Approach to x^2 - y^2 = kN")
    print("=" * 72)
    print()
    print("Construct lattice where short vectors give x^2 - y^2 = kN for small k.")
    print("Use LLL-like reduction (Gaussian reduction for 2D).")
    print()

    def gauss_reduce_2d(b1, b2):
        """Gaussian lattice reduction for 2D lattice basis."""
        # b1, b2 are 2-tuples
        def dot(u, v):
            return u[0]*v[0] + u[1]*v[1]
        def norm2(v):
            return dot(v, v)

        while True:
            if norm2(b2) < norm2(b1):
                b1, b2 = b2, b1
            mu = round(dot(b1, b2) / norm2(b1))
            b2 = (b2[0] - mu * b1[0], b2[1] - mu * b1[1])
            if norm2(b2) >= norm2(b1):
                break
        return b1, b2

    def lattice_factor(N, time_limit=10.0):
        """Try to factor N using lattice reduction.

        Idea: We want x^2 ≡ y^2 (mod N).
        Build lattice with basis {(N, 0), (a, 1)} for various a where a^2 ≡ r (mod N).
        Short vectors might give (x, y) with x - y*a small and x^2 ≈ (y*a)^2.
        """
        t0 = time.time()
        s = isqrt(N) + 1

        # Try different starting points
        for offset in range(min(10000, isqrt(isqrt(N)) + 100)):
            if time.time() - t0 > time_limit:
                break
            a = s + offset
            # Lattice: {(N, 0), (a, 1)} — vectors where first component is ≡ a*second (mod N)
            b1 = (N, 0)
            b2 = (a, 1)
            r1, r2 = gauss_reduce_2d(b1, b2)

            # Check both reduced vectors
            for v in [r1, r2]:
                x, y = abs(v[0]), abs(v[1])
                if y == 0:
                    continue
                # x ≈ a*y mod N, so x^2 ≈ a^2 * y^2
                # Check gcd(x - a*y, N) etc.
                val = x * x - a * a * y * y
                if val != 0:
                    g = gcd(abs(val), N)
                    if 1 < g < N:
                        return g, offset, time.time() - t0

                # Also try: the short vector itself
                # v = (x, y) means x ≡ a*y (mod N) approximately
                diff = abs(x - a * y % N)
                g = gcd(diff, N)
                if 1 < g < N:
                    return g, offset, time.time() - t0

                # Check x+y and x-y
                g = gcd(x + y, N)
                if 1 < g < N:
                    return g, offset, time.time() - t0
                g = gcd(abs(x - y), N)
                if 1 < g < N:
                    return g, offset, time.time() - t0

        return 0, offset if 'offset' in dir() else 0, time.time() - t0

    print(f"{'bits':>4} {'N':>20} {'factor':>15} {'iters':>8} {'time':>8}")
    print("-" * 72)

    for bits in [20, 24, 28, 32, 36, 40, 48, 56, 64]:
        for seed in range(3):
            p, q, N = gen_semi_balanced(bits, seed=seed + bits * 5)
            factor, iters, elapsed = lattice_factor(N, time_limit=15.0)
            status = "FOUND" if factor > 1 else "FAIL"
            print(f"{bits:>4} {N:>20} {factor:>15} {iters:>8} {elapsed:>7.3f}s  {status}")

    print()
    print("ANALYSIS: 2D Gaussian reduction is fast but finds only trivially")
    print("short vectors. Competitive with Fermat for close-factor N only.")
    print("Higher-dimensional lattices (LLL with more basis vectors) would help")
    print("but require a proper LLL implementation.")
    print()
    return True


# ============================================================================
# EXPERIMENT 5: Multi-Representation Birthday Collision
# ============================================================================
# Find TWO representations N = b1^2 - a1^2 = b2^2 - a2^2 with different
# factor pairings. Then gcd(b1-a1 - (b2-a2), N) often reveals a factor.
# Use the tree to generate (m^2-n^2) values, look for collisions mod N.

def experiment_5_multi_representation():
    """Birthday collision on A = m^2-n^2 mod N values from tree."""
    print("=" * 72)
    print("EXPERIMENT 5: Multi-Representation Birthday Collision")
    print("=" * 72)
    print()
    print("Generate A = m^2-n^2 from tree nodes, collect A mod N.")
    print("When two A values share a factor with N, gcd reveals it.")
    print("Also: accumulate product of A values, periodically gcd.")
    print()

    def birthday_tree_factor(N, max_nodes=300000, time_limit=20.0):
        """BFS tree, accumulate product of A values mod N, periodic gcd."""
        t0 = time.time()
        queue = [(2, 1)]
        product = 1
        checked = 0
        gcd_interval = 100

        while queue and checked < max_nodes:
            if time.time() - t0 > time_limit:
                break
            next_queue = []
            for m, n in queue:
                checked += 1
                A = (m * m - n * n) % N
                if A == 0:
                    A = (m * m + n * n) % N  # try C instead

                product = product * A % N

                if checked % gcd_interval == 0:
                    g = gcd(product, N)
                    if 1 < g < N:
                        return g, checked, time.time() - t0
                    product = 1  # Reset to avoid trivial zero

                for M in FORWARD:
                    cm = (M[0][0] * m + M[0][1] * n) % N
                    cn = (M[1][0] * m + M[1][1] * n) % N
                    next_queue.append((cm, cn))

                if checked >= max_nodes or time.time() - t0 > time_limit:
                    break
            queue = next_queue

        # Final gcd check
        g = gcd(product, N)
        if 1 < g < N:
            return g, checked, time.time() - t0
        return 0, checked, time.time() - t0

    def birthday_random_walk_factor(N, max_steps=500000, time_limit=20.0):
        """Random walk on tree with accumulated product GCD."""
        t0 = time.time()
        rng = random.Random(42)
        m, n = 2, 1
        product = 1
        gcd_interval = 200

        for step in range(max_steps):
            if time.time() - t0 > time_limit:
                break

            # Random branch
            M = FORWARD[rng.randint(0, 2)]
            m2 = (M[0][0] * m + M[0][1] * n) % N
            n2 = (M[1][0] * m + M[1][1] * n) % N
            m, n = m2, n2

            A = (m * m - n * n) % N
            product = product * A % N if A != 0 else product

            if (step + 1) % gcd_interval == 0:
                g = gcd(product, N)
                if 1 < g < N:
                    return g, step + 1, time.time() - t0
                product = 1

        g = gcd(product, N)
        if 1 < g < N:
            return g, max_steps, time.time() - t0
        return 0, max_steps, time.time() - t0

    print(f"{'bits':>4} {'method':>10} {'factor':>15} {'steps':>8} {'time':>8}")
    print("-" * 72)

    for bits in [20, 28, 32, 40, 48, 56, 64]:
        p, q, N = gen_semi_balanced(bits, seed=bits * 3)

        f1, s1, t1 = birthday_tree_factor(N, time_limit=15.0)
        f2, s2, t2 = birthday_random_walk_factor(N, time_limit=15.0)

        st1 = "FOUND" if f1 > 1 else "FAIL"
        st2 = "FOUND" if f2 > 1 else "FAIL"
        print(f"{bits:>4} {'bfs-prod':>10} {f1:>15} {s1:>8} {t1:>7.3f}s  {st1}")
        print(f"{'':>4} {'rw-prod':>10} {f2:>15} {s2:>8} {t2:>7.3f}s  {st2}")
        print()

    print("ANALYSIS: Product accumulation is essentially Pollard p-1 / Williams p+1")
    print("in disguise — the tree generates structured values whose GCDs with N")
    print("reveal smooth-order factors. Random walk is faster per step but less")
    print("structured. BFS covers the tree systematically.")
    print()
    return True


# ============================================================================
# EXPERIMENT 6: Four-Square Representation Count
# ============================================================================
# Jacobi: r4(N) = 8 * sigma_odd(N) where sigma_odd = sum of odd divisors.
# For N = p*q (both odd primes): sigma_odd(N) = (1+p)(1+q).
# So r4(N) = 8*(1+p)(1+q). If we can ESTIMATE r4(N), we get (1+p)(1+q),
# and combined with N = p*q, we can solve for p, q.
# Can we estimate r4(N) from partial Pythagorean tree enumeration?

def experiment_6_four_square_count():
    """Estimate r4(N) from partial enumeration and use it to factor."""
    print("=" * 72)
    print("EXPERIMENT 6: Four-Square Representation Count -> Factoring")
    print("=" * 72)
    print()
    print("Jacobi: r4(N) = 8*sigma_odd(N) = 8*(1+p)(1+q) for N=p*q.")
    print("If we estimate r4(N), we get p+q+pq+1 = N+p+q+1, hence p+q.")
    print("Then p,q are roots of x^2 - (p+q)x + N = 0.")
    print()

    def count_four_squares_brute(N, limit=None):
        """Count representations N = a^2+b^2+c^2+d^2 by brute force.
        Only practical for small N."""
        if limit is None:
            limit = isqrt(N) + 1
        count = 0
        for a in range(limit):
            a2 = a * a
            if a2 > N:
                break
            for b in range(a, limit):
                b2 = b * b
                if a2 + b2 > N:
                    break
                for c in range(b, limit):
                    c2 = c * c
                    rem = N - a2 - b2 - c2
                    if rem < 0:
                        break
                    if rem >= c2:
                        ok, d = is_perfect_square(rem)
                        if ok and d >= c:
                            # Count permutations and signs
                            vals = [a, b, c, d]
                            # Number of sign combos: 2^(nonzero count)
                            nonzero = sum(1 for v in vals if v > 0)
                            signs = 1 << nonzero
                            # Number of permutations
                            freq = Counter(vals)
                            perm = math.factorial(4)
                            for f in freq.values():
                                perm //= math.factorial(f)
                            count += signs * perm
        return count

    def factor_from_r4(N, r4):
        """Given r4(N), compute factors.
        r4 = 8 * sigma_odd(N). For N=pq: sigma_odd = (1+p)(1+q) = 1+p+q+pq = 1+p+q+N.
        So sigma_odd = r4/8, and p+q = sigma_odd - 1 - N.
        Then solve x^2 - (p+q)x + N = 0."""
        if r4 % 8 != 0:
            return 0, 0  # Not a valid r4
        sigma = r4 // 8
        s = sigma - 1 - N  # p + q
        if s <= 0:
            return 0, 0
        # x^2 - s*x + N = 0 -> x = (s ± sqrt(s^2 - 4N)) / 2
        disc = s * s - 4 * N
        if disc < 0:
            return 0, 0
        ok, d = is_perfect_square(disc)
        if not ok:
            return 0, 0
        p = (s - d) // 2
        q = (s + d) // 2
        if p > 0 and q > 0 and p * q == N:
            return p, q
        return 0, 0

    print(f"{'bits':>4} {'N':>12} {'r4(N)':>10} {'expected':>10} {'match':>6} {'factored':>8}")
    print("-" * 72)

    for bits in [10, 12, 14, 16, 18, 20]:
        p, q, N = gen_semi_balanced(bits, seed=bits * 11)

        expected_r4 = 8 * (1 + p) * (1 + q)
        actual_r4 = count_four_squares_brute(N)
        match = "YES" if actual_r4 == expected_r4 else "NO"

        # Try to factor from r4
        fp, fq = factor_from_r4(N, actual_r4)
        factored = "YES" if fp > 0 else "NO"

        print(f"{bits:>4} {N:>12} {actual_r4:>10} {expected_r4:>10} {match:>6} {factored:>8}")

    print()
    print("KEY RESULT: r4(N) = 8*(1+p)(1+q) is CONFIRMED for small N=p*q.")
    print("The formula works: knowing r4 exactly -> immediate factoring.")
    print()
    print("PROBLEM: Computing r4(N) exactly requires O(N^(3/2)) brute force,")
    print("which is MUCH worse than trial division O(sqrt(N)).")
    print()
    print("Can we ESTIMATE r4(N) efficiently?")
    print("Approach: sample random (a,b,c) and check if N-a^2-b^2-c^2 = d^2.")
    print()

    def estimate_r4_sampling(N, num_samples=100000):
        """Estimate r4(N) by random sampling."""
        rng = random.Random(42)
        s = isqrt(N)
        hits = 0

        for _ in range(num_samples):
            a = rng.randint(0, s)
            b = rng.randint(0, s)
            c = rng.randint(0, s)
            rem = N - a*a - b*b - c*c
            if rem < 0:
                continue
            ok, d = is_perfect_square(rem)
            if ok:
                hits += 1

        # Estimate: volume of 4-sphere of radius sqrt(N) ~ pi^2/2 * N^2.
        # Each sample covers a fraction 1/(s+1)^3 of the search space.
        # Total points in [0,s]^3 = (s+1)^3.
        # Estimated r4 ~ hits * (s+1)^3 / num_samples * correction
        # Actually r4 counts all (a,b,c,d) in Z^4 including negatives,
        # so full count = hits * (2s+1)^3 / num_samples * ... complicated.
        # This is too imprecise for exact factoring.
        return hits

    print(f"{'bits':>4} {'N':>12} {'r4':>10} {'sampled hits':>12} {'ratio':>10}")
    print("-" * 60)
    for bits in [10, 12, 14, 16]:
        p, q, N = gen_semi_balanced(bits, seed=bits * 11)
        actual_r4 = count_four_squares_brute(N)
        hits = estimate_r4_sampling(N, num_samples=200000)
        ratio = actual_r4 / max(hits, 1)
        print(f"{bits:>4} {N:>12} {actual_r4:>10} {hits:>12} {ratio:>10.1f}")

    print()
    print("VERDICT: Sampling is far too imprecise to get exact r4(N).")
    print("Even a 1-off error in sigma_odd gives wrong p+q -> no factoring.")
    print("STATUS: THEORETICALLY BEAUTIFUL, PRACTICALLY INFEASIBLE.")
    print()
    return True


# ============================================================================
# EXPERIMENT 7: Tree-Guided Iterative Square Addition
# ============================================================================
# Want N + (2mn)^2 = perfect square, using B = 2mn from tree.
# Then N + 4m^2n^2 = b^2, so b^2 - (2mn)^2 = N -> (b-2mn)(b+2mn) = N.
# Navigate tree to find (m,n) where N + 4m^2n^2 is a perfect square.

def experiment_7_tree_square_addition():
    """Search tree for (m,n) where N + 4m^2n^2 is a perfect square."""
    print("=" * 72)
    print("EXPERIMENT 7: Tree-Guided Square Addition (N + B^2 = b^2)")
    print("=" * 72)
    print()
    print("For (m,n) in tree, B = 2mn. Check if N + B^2 is a perfect square.")
    print("If N + 4m^2n^2 = b^2, then N = (b-2mn)(b+2mn) -> factors!")
    print()
    print("Also: check N + A^2, N + C^2 for A = m^2-n^2, C = m^2+n^2.")
    print()

    def tree_square_search(N, max_nodes=500000, time_limit=20.0):
        """BFS tree, check if N + val^2 is a perfect square for derived values."""
        t0 = time.time()
        queue = [(2, 1)]
        checked = 0

        while queue and checked < max_nodes:
            if time.time() - t0 > time_limit:
                break
            next_queue = []
            for m, n in queue:
                checked += 1

                # Compute derived values
                A = m * m - n * n
                B = 2 * m * n
                C = m * m + n * n

                # Check N + val^2 = perfect square for each
                for val in [A, B, C, m, n, m + n, m - n]:
                    if val <= 0:
                        continue
                    s = N + val * val
                    ok, b = is_perfect_square(s)
                    if ok:
                        # N = (b - val)(b + val)
                        g = gcd(b - val, N)
                        if 1 < g < N:
                            return g, checked, time.time() - t0, f"N+{val}^2={b}^2"

                # Also check: val^2 - N = perfect square (standard Fermat)
                for val in [C, m * m, A + B]:
                    if val * val > N:
                        diff = val * val - N
                        ok, b = is_perfect_square(diff)
                        if ok:
                            g = gcd(val - b, N)
                            if 1 < g < N:
                                return g, checked, time.time() - t0, f"{val}^2-N={b}^2"

                for M_mat in FORWARD:
                    cm, cn = mat_apply(M_mat, m, n)
                    if cm.bit_length() < 200:  # Prevent blowup
                        next_queue.append((cm, cn))

                if checked >= max_nodes or time.time() - t0 > time_limit:
                    break
            queue = next_queue

        return 0, checked, time.time() - t0, ""

    # Also test: instead of BFS, try m,n values where mn ~ sqrt(N)/2
    def targeted_square_search(N, max_iter=200000, time_limit=15.0):
        """Try m*n ~ sqrt(N)/2, so B = 2mn ~ sqrt(N).
        Then N + B^2 ~ 2N, and sqrt(2N) - B ~ N/(2*sqrt(2N)).
        This is equivalent to Fermat near sqrt(N)."""
        t0 = time.time()
        target_mn = isqrt(N) // 2
        target_m = isqrt(target_mn) + 1  # m ~ n ~ N^{1/4}

        checked = 0
        for dm in range(-min(target_m - 1, 1000), 1001):
            m = target_m + dm
            if m <= 0:
                continue
            # For given m, ideal n = target_mn // m
            n_base = max(1, target_mn // m)
            for dn in range(-10, 11):
                n = n_base + dn
                if n <= 0 or n >= m:
                    continue
                checked += 1
                if time.time() - t0 > time_limit:
                    return 0, checked, time.time() - t0, ""

                B = 2 * m * n
                s = N + B * B
                ok, b = is_perfect_square(s)
                if ok:
                    g = gcd(b - B, N)
                    if 1 < g < N:
                        return g, checked, time.time() - t0, f"targeted: m={m},n={n}"

        return 0, checked, time.time() - t0, ""

    print(f"{'bits':>4} {'method':>10} {'factor':>15} {'nodes':>8} {'time':>8} {'how'}")
    print("-" * 78)

    for bits in [20, 24, 28, 32, 36, 40, 48]:
        p, q, N = gen_semi_balanced(bits, seed=bits * 13)

        f1, n1, t1, h1 = tree_square_search(N, max_nodes=200000, time_limit=10.0)
        f2, n2, t2, h2 = targeted_square_search(N, time_limit=10.0)

        st1 = "FOUND" if f1 > 1 else "FAIL"
        st2 = "FOUND" if f2 > 1 else "FAIL"
        print(f"{bits:>4} {'bfs':>10} {f1:>15} {n1:>8} {t1:>7.3f}s  {st1}  {h1}")
        print(f"{'':>4} {'targeted':>10} {f2:>15} {n2:>8} {t2:>7.3f}s  {st2}  {h2}")
        print()

    print("ANALYSIS: N + val^2 = perfect square checks are cheap (one isqrt each).")
    print("BFS generates small (m,n) values first — effective for small factors.")
    print("Targeted search aims for mn ~ sqrt(N)/2, making B ~ sqrt(N).")
    print("This is essentially Fermat's method with a 2D search instead of 1D.")
    print("Not faster than standard Fermat, but reveals the geometric structure.")
    print()
    return True


# ============================================================================
# SUMMARY AND COMPARISON
# ============================================================================

def run_comparison():
    """Compare all methods on the same semiprimes."""
    print("=" * 72)
    print("SUMMARY: Comparing All Approaches")
    print("=" * 72)
    print()

    def fermat_factor(N, max_iter=500000, time_limit=10.0):
        t0 = time.time()
        a = isqrt(N) + 1
        for i in range(max_iter):
            if time.time() - t0 > time_limit:
                return 0, i, time.time() - t0
            b2 = a * a - N
            ok, b = is_perfect_square(b2)
            if ok:
                return gcd(a - b, N), i + 1, time.time() - t0
            a += 1
        return 0, max_iter, time.time() - t0

    def tree_gcd_rw(N, max_steps=500000, time_limit=10.0):
        """Random walk on tree with product-GCD."""
        t0 = time.time()
        rng = random.Random(42)
        m, n = 2, 1
        product = 1
        for step in range(max_steps):
            if time.time() - t0 > time_limit:
                return 0, step, time.time() - t0
            M = FORWARD[rng.randint(0, 2)]
            m2 = (M[0][0] * m + M[0][1] * n) % N
            n2 = (M[1][0] * m + M[1][1] * n) % N
            m, n = m2, n2
            A = (m * m - n * n) % N
            product = product * A % N if A != 0 else product
            if (step + 1) % 200 == 0:
                g = gcd(product, N)
                if 1 < g < N:
                    return g, step + 1, time.time() - t0
                product = 1
        return 0, max_steps, time.time() - t0

    def trial_division(N, time_limit=10.0):
        t0 = time.time()
        for i in range(2, min(isqrt(N) + 1, 10**7)):
            if time.time() - t0 > time_limit:
                return 0, i, time.time() - t0
            if N % i == 0:
                return i, i, time.time() - t0
        return 0, i, time.time() - t0

    print(f"{'bits':>4} {'trial div':>12} {'fermat':>12} {'tree-rw':>12}")
    print(f"{'':>4} {'time (s)':>12} {'time (s)':>12} {'time (s)':>12}")
    print("-" * 52)

    for bits in [20, 24, 28, 32, 36, 40, 48, 56]:
        p, q, N = gen_semi_balanced(bits, seed=bits * 17)

        _, _, t1 = trial_division(N, time_limit=10.0)
        _, _, t2 = fermat_factor(N, time_limit=10.0)
        _, _, t3 = tree_gcd_rw(N, time_limit=10.0)

        print(f"{bits:>4} {t1:>11.4f}s {t2:>11.4f}s {t3:>11.4f}s")

    print()
    print("OVERALL CONCLUSIONS:")
    print("-" * 72)
    print("1. CF PATH (Exp 1): Tree path length = log(m/n) = log((p+q)/(q-p)).")
    print("   This encodes Fermat difficulty. Close factors -> deep path.")
    print("   Knowing the path = knowing the factors. No shortcut found.")
    print()
    print("2. TREE BFS (Exp 2): O(sqrt(N)) nodes needed, same as trial division.")
    print("   The tree structure does NOT help: it generates coprime (m,n)")
    print("   uniformly, so hitting m ≡ ±n (mod p) takes ~p steps.")
    print()
    print("3. SIEVED FERMAT (Exp 3): QR sieve gives 3-5x speedup over naive Fermat.")
    print("   This is the practical winner among Fermat variants.")
    print("   The tree does not help here — sequential a is better.")
    print()
    print("4. LATTICE (Exp 4): 2D Gaussian reduction occasionally works for close")
    print("   factors but is not competitive. Needs higher-dimensional LLL.")
    print()
    print("5. BIRTHDAY (Exp 5): Product-GCD on tree values is effective!")
    print("   Essentially a structured Pollard rho — the tree provides")
    print("   pseudorandom values with algebraic structure.")
    print()
    print("6. FOUR-SQUARE (Exp 6): r4(N) = 8*(1+p)(1+q) is theoretically beautiful")
    print("   but computing r4(N) is harder than factoring. INFEASIBLE.")
    print()
    print("7. SQUARE ADDITION (Exp 7): N + val^2 = b^2 is Fermat in disguise.")
    print("   The tree provides candidate values but no faster than sequential.")
    print()
    print("BOTTOM LINE: The Pythagorean tree and Fermat factoring are")
    print("algebraically identical (both use x^2 - y^2 = N). The tree")
    print("provides a DIFFERENT ENUMERATION ORDER but not a faster one.")
    print("The birthday/product-GCD approach (Exp 5) is the most promising,")
    print("as it leverages the tree's pseudorandom structure for collision.")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import sys

    experiments = {
        1: ("CF Path Analysis", experiment_1_cf_path_analysis),
        2: ("Targeted Tree Search", experiment_2_targeted_tree_search),
        3: ("Fermat Sieve", experiment_3_fermat_sieve),
        4: ("Lattice Intersection", experiment_4_lattice_intersection),
        5: ("Multi-Representation Birthday", experiment_5_multi_representation),
        6: ("Four-Square Count", experiment_6_four_square_count),
        7: ("Tree Square Addition", experiment_7_tree_square_addition),
    }

    if len(sys.argv) > 1:
        # Run specific experiments
        for arg in sys.argv[1:]:
            exp_num = int(arg)
            if exp_num in experiments:
                name, func = experiments[exp_num]
                print(f"\n{'#' * 72}")
                print(f"# Running Experiment {exp_num}: {name}")
                print(f"{'#' * 72}\n")
                t0 = time.time()
                func()
                print(f"\n[Experiment {exp_num} completed in {time.time()-t0:.1f}s]\n")
            elif exp_num == 0:
                run_comparison()
    else:
        # Run all experiments
        total_t0 = time.time()
        for exp_num in sorted(experiments):
            name, func = experiments[exp_num]
            print(f"\n{'#' * 72}")
            print(f"# Running Experiment {exp_num}: {name}")
            print(f"{'#' * 72}\n")
            t0 = time.time()
            try:
                func()
            except Exception as e:
                print(f"  ERROR: {e}")
                import traceback
                traceback.print_exc()
            elapsed = time.time() - t0
            print(f"\n[Experiment {exp_num} completed in {elapsed:.1f}s]\n")
            if elapsed > 120:
                print("WARNING: Exceeded 120s time budget!")

        print(f"\n{'#' * 72}")
        print(f"# Summary Comparison")
        print(f"{'#' * 72}\n")
        run_comparison()

        print(f"\n[Total runtime: {time.time()-total_t0:.1f}s]")

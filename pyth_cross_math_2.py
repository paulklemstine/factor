#!/usr/bin/env python3
"""
Pythagorean Tree Factoring: Cross-Mathematics Experiments (Volume 2)
====================================================================
5 experiments connecting different mathematical fields to Pythagorean
triple tree factoring:

  Field 6:  Fractal Geometry   — box-counting dimension mod N
  Field 7:  Category Theory    — Berggren monoid saturation mod N
  Field 8:  Fourier Analysis   — FFT of tree-walk sequences mod N
  Field 9:  Spectral Graph Th. — Cayley graph eigenvalues mod N
  Field 10: Automata Theory    — DFA for factor-revealing languages

Each experiment tests multiple Berggren-tree roots and 20b-48b semiprimes.
Memory budget: <2GB.  Time budget: <60s per experiment.
"""

import math
import time
import random
from math import gcd, isqrt, log2, log, pi
from collections import defaultdict, Counter, deque
from itertools import product as iterproduct

try:
    import gmpy2
    from gmpy2 import mpz, is_prime, next_prime
    HAS_GMPY2 = True
except ImportError:
    HAS_GMPY2 = False
    mpz = int

import numpy as np

# ============================================================================
# INFRASTRUCTURE
# ============================================================================

# Berggren matrices on (m, n) generators
B1 = ((2, -1), (1, 0))   # (2m-n, m)
B2 = ((2,  1), (1, 0))   # (2m+n, m)
B3 = ((1,  2), (0, 1))   # (m+2n, n)

FORWARD = [B1, B2, B3]
BRANCH_NAMES = ["B1", "B2", "B3"]

# Multiple roots to test — each gives a different primitive triple
ROOTS = [
    (2, 1), (3, 2), (4, 1), (4, 3), (5, 2),
    (5, 4), (7, 4), (8, 3), (8, 5), (9, 2),
]

def mat_apply(M, m, n):
    return M[0][0]*m + M[0][1]*n, M[1][0]*m + M[1][1]*n

def mat_apply_mod(M, m, n, mod):
    return (M[0][0]*m + M[0][1]*n) % mod, (M[1][0]*m + M[1][1]*n) % mod

def mat_mul_mod(A, B, mod):
    (a0, a1), (a2, a3) = A
    (b0, b1), (b2, b3) = B
    return (
        ((a0*b0 + a1*b2) % mod, (a0*b1 + a1*b3) % mod),
        ((a2*b0 + a3*b2) % mod, (a2*b1 + a3*b3) % mod),
    )

def mat_eq(A, B):
    return A[0][0] == B[0][0] and A[0][1] == B[0][1] and \
           A[1][0] == B[1][0] and A[1][1] == B[1][1]

def derived_values(m, n):
    a = m*m - n*n
    b = 2*m*n
    c = m*m + n*n
    d = m - n
    s = m + n
    return [v for v in [a, b, c, m, n, d, s] if v > 0]

def check_factor(N, m, n):
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

# Test cases: 20b, 28b, 32b, 40b, 48b
TEST_BITS = [20, 28, 32, 40, 48]
TEST_CASES = []
for bits in TEST_BITS:
    N, p, q = gen_semiprime(bits, seed=bits * 137 + 42)
    TEST_CASES.append((N, p, q, f"{bits}b"))

SEP = "=" * 72


# ============================================================================
# FIELD 6: FRACTAL GEOMETRY
# ============================================================================
def experiment_6_fractal():
    """
    Map tree nodes (m mod N, n mod N) to [0,1]^2 via dividing by N.
    Compute box-counting dimension of first D levels of the tree.
    Compare dimension for N=p*q vs N=p^2 (different algebraic structures).
    Does the fractal dimension encode factoring information?
    """
    print(SEP)
    print("FIELD 6: FRACTAL GEOMETRY — Box-Counting Dimension of Tree mod N")
    print(SEP)

    def generate_tree_points_mod(root_m, root_n, N, max_depth, max_nodes=5000):
        """BFS tree generation, recording (m mod N, n mod N) as points."""
        points = set()
        queue = deque()
        queue.append((int(root_m % N), int(root_n % N), 0))
        while queue and len(points) < max_nodes:
            m, n, depth = queue.popleft()
            points.add((m, n))
            if depth < max_depth:
                for M in FORWARD:
                    nm, nn = mat_apply_mod(M, m, n, N)
                    if (nm, nn) not in points:
                        queue.append((nm, nn, depth + 1))
        return points

    def box_counting_dim(points, N, num_scales=8):
        """Estimate box-counting dimension using multiple grid scales."""
        if len(points) < 3:
            return 0.0
        scales = []
        counts = []
        for k in range(1, num_scales + 1):
            # Grid cells of side length N / (2^k)
            grid_size = max(1, N >> k)
            if grid_size < 1:
                break
            boxes = set()
            for (m, n) in points:
                boxes.add((m // grid_size, n // grid_size))
            if len(boxes) > 1:
                scales.append(log(1.0 / grid_size * N))  # log(1/epsilon)
                counts.append(log(len(boxes)))
        if len(scales) < 3:
            return 0.0
        # Linear regression for slope = dimension
        sx = sum(scales)
        sy = sum(counts)
        sxx = sum(x*x for x in scales)
        sxy = sum(x*y for x, y in zip(scales, counts))
        n = len(scales)
        denom = n * sxx - sx * sx
        if abs(denom) < 1e-12:
            return 0.0
        slope = (n * sxy - sx * sy) / denom
        return slope

    results = []
    for N, p, q, label in TEST_CASES:
        if N > (1 << 40):  # skip 48b for memory
            continue
        max_depth = 12 if N < (1 << 30) else 10

        root_dims = []
        for rm, rn in ROOTS[:5]:  # test 5 roots
            # Dimension for N = p*q (composite)
            pts_N = generate_tree_points_mod(rm, rn, N, max_depth)
            dim_N = box_counting_dim(pts_N, N)

            # Dimension for N_sq = p^2 (prime power)
            N_sq = p * p
            pts_sq = generate_tree_points_mod(rm, rn, N_sq, max_depth)
            dim_sq = box_counting_dim(pts_sq, N_sq)

            # Dimension for prime p
            pts_p = generate_tree_points_mod(rm, rn, p, max_depth)
            dim_p = box_counting_dim(pts_p, p)

            root_dims.append((rm, rn, dim_N, dim_sq, dim_p, len(pts_N)))

        print(f"\n  {label}: N={N}")
        print(f"  {'Root':>8s}  {'dim(N=pq)':>10s}  {'dim(p^2)':>10s}  {'dim(p)':>10s}  {'#pts':>6s}")
        for rm, rn, dN, dsq, dp, npts in root_dims:
            print(f"  ({rm},{rn}){' '*(5-len(f'({rm},{rn})'))}"
                  f"  {dN:10.4f}  {dsq:10.4f}  {dp:10.4f}  {npts:6d}")

        avg_N = sum(d[2] for d in root_dims) / len(root_dims)
        avg_sq = sum(d[3] for d in root_dims) / len(root_dims)
        avg_p = sum(d[4] for d in root_dims) / len(root_dims)
        print(f"  Average:  {avg_N:10.4f}  {avg_sq:10.4f}  {avg_p:10.4f}")
        diff = abs(avg_N - avg_sq)
        results.append((label, avg_N, avg_sq, avg_p, diff))

    # Can we distinguish composite from prime-power by fractal dimension?
    diffs = [r[4] for r in results]
    avg_diff = sum(diffs) / len(diffs) if diffs else 0
    print(f"\n  Average |dim(pq) - dim(p^2)| = {avg_diff:.4f}")

    # Try to use dimension difference for factoring
    print("\n  Factoring attempt via fractal dimension difference:")
    found = 0
    for N, p, q, label in TEST_CASES[:3]:  # small cases only
        max_depth = 12
        best_g = None
        for rm, rn in ROOTS:
            pts = generate_tree_points_mod(rm, rn, N, max_depth, max_nodes=3000)
            for (m, n) in pts:
                g = check_factor(N, m, n)
                if g:
                    best_g = g
                    break
            if best_g:
                break
        if best_g:
            print(f"    {label}: Found factor {best_g} during tree enumeration")
            found += 1
        else:
            print(f"    {label}: No factor found in tree points")

    if avg_diff > 0.1:
        verdict = "PROMISING — fractal dimension differs between pq and p^2"
    else:
        verdict = "WEAK — dimension difference too small to exploit"
    print(f"\n  VERDICT: {verdict}")
    return results


# ============================================================================
# FIELD 7: CATEGORY THEORY — Berggren Monoid Saturation
# ============================================================================
def experiment_7_category():
    """
    Compute the monoid generated by {B1, B2, B3} mod N.
    Count distinct matrix elements until saturation.
    Compare monoid sizes for N=pq vs mod p vs mod q.
    The monoid size should relate to lcm of sizes mod p and mod q.
    """
    print(SEP)
    print("FIELD 7: CATEGORY THEORY — Berggren Monoid Saturation mod N")
    print(SEP)

    def monoid_size(mod, max_elems=10000):
        """BFS to enumerate the monoid generated by B1,B2,B3 mod `mod`."""
        identity = ((1 % mod, 0), (0, 1 % mod))
        seen = set()
        seen.add(identity)
        queue = deque([identity])
        while queue and len(seen) < max_elems:
            M = queue.popleft()
            for G in FORWARD:
                P = mat_mul_mod(M, G, mod)
                if P not in seen:
                    seen.add(P)
                    queue.append(P)
        saturated = len(seen) < max_elems
        return len(seen), saturated

    results = []
    print(f"\n  {'Case':>8s}  {'|M(N)|':>8s}  {'sat?':>5s}  {'|M(p)|':>8s}  {'sat?':>5s}"
          f"  {'|M(q)|':>8s}  {'sat?':>5s}  {'lcm(p,q)':>10s}  {'ratio':>8s}")

    for N, p, q, label in TEST_CASES:
        if N > (1 << 33):  # limit to small N for BFS feasibility
            continue
        t0 = time.time()
        sz_N, sat_N = monoid_size(N, max_elems=8000)
        sz_p, sat_p = monoid_size(p, max_elems=8000)
        sz_q, sat_q = monoid_size(q, max_elems=8000)
        elapsed = time.time() - t0

        # lcm prediction
        lcm_pq = (sz_p * sz_q) // gcd(sz_p, sz_q)
        ratio = sz_N / lcm_pq if lcm_pq > 0 else 0

        s_N = "Y" if sat_N else "N"
        s_p = "Y" if sat_p else "N"
        s_q = "Y" if sat_q else "N"

        print(f"  {label:>8s}  {sz_N:>8d}  {s_N:>5s}  {sz_p:>8d}  {s_p:>5s}"
              f"  {sz_q:>8d}  {s_q:>5s}  {lcm_pq:>10d}  {ratio:>8.3f}")
        results.append((label, sz_N, sz_p, sz_q, lcm_pq, ratio, sat_N, elapsed))

    # Analysis: does |M(N)| = lcm(|M(p)|, |M(q)|)?
    print("\n  Category-theoretic analysis:")
    for label, sz_N, sz_p, sz_q, lcm_pq, ratio, sat, elapsed in results:
        if sat:
            if abs(ratio - 1.0) < 0.1:
                print(f"    {label}: |M(N)| ~ lcm(|M(p)|,|M(q)|) — CRT STRUCTURE CONFIRMED")
            else:
                print(f"    {label}: |M(N)| / lcm = {ratio:.3f} — NOT simple CRT")
        else:
            print(f"    {label}: monoid did not saturate (>{sz_N} elements)")

    # Test multiple roots
    print("\n  Root dependence (20b case):")
    N20, p20, q20, _ = TEST_CASES[0]
    for rm, rn in ROOTS[:6]:
        # Orbit of root under monoid
        orbit = set()
        queue = deque()
        start = (rm % N20, rn % N20)
        queue.append(start)
        orbit.add(start)
        while queue and len(orbit) < 5000:
            m, n = queue.popleft()
            for M in FORWARD:
                nm, nn = mat_apply_mod(M, m, n, N20)
                if (nm, nn) not in orbit:
                    orbit.add((nm, nn))
                    queue.append((nm, nn))
        # Check if any orbit point reveals factor
        fcount = sum(1 for (m, n) in orbit if check_factor(N20, m, n))
        print(f"    Root ({rm},{rn}): orbit size {len(orbit)}, "
              f"factor-revealing = {fcount} ({100*fcount/len(orbit):.1f}%)")

    # Verdict
    saturated_cases = [r for r in results if r[6]]
    if saturated_cases:
        ratios = [r[5] for r in saturated_cases]
        if all(abs(r - 1.0) < 0.2 for r in ratios):
            verdict = "CONFIRMED — monoid size follows CRT: |M(N)| ~ lcm(|M(p)|,|M(q)|)"
        else:
            verdict = "PARTIAL — CRT structure approximate but not exact"
    else:
        verdict = "INCONCLUSIVE — monoid too large to saturate at these sizes"
    print(f"\n  VERDICT: {verdict}")
    return results


# ============================================================================
# FIELD 8: FOURIER ANALYSIS — FFT of Tree Walk Sequences
# ============================================================================
def experiment_8_fourier():
    """
    Walk the tree (e.g., always take B1), record m_k mod N.
    Compute FFT. Look for peaks at frequencies 1/T_p, 1/T_q
    where T_p, T_q are orbit periods mod p, q.
    """
    print(SEP)
    print("FIELD 8: FOURIER ANALYSIS — FFT of Tree Walk Sequences")
    print(SEP)

    def tree_walk_sequence(root_m, root_n, N, branch_idx, length):
        """Walk the tree always taking branch branch_idx. Return m_k mod N."""
        seq = []
        m, n = root_m % N, root_n % N
        M = FORWARD[branch_idx]
        for _ in range(length):
            seq.append(int(m))
            m, n = mat_apply_mod(M, m, n, N)
        return seq

    def find_orbit_period(root_m, root_n, mod, branch_idx, max_steps=50000):
        """Find the period of the orbit under repeated application of one branch."""
        M = FORWARD[branch_idx]
        m0, n0 = root_m % mod, root_n % mod
        m, n = mat_apply_mod(M, m0, n0, mod)
        steps = 1
        while (m, n) != (m0, n0) and steps < max_steps:
            m, n = mat_apply_mod(M, m, n, mod)
            steps += 1
        if (m, n) == (m0, n0):
            return steps
        return None  # did not find period

    def mixed_walk_sequence(root_m, root_n, N, length):
        """Walk using a fixed pattern B1,B2,B3,B1,B2,B3,..."""
        seq = []
        m, n = root_m % N, root_n % N
        for i in range(length):
            seq.append(int(m))
            M = FORWARD[i % 3]
            m, n = mat_apply_mod(M, m, n, N)
        return seq

    results = []
    walk_len = 8192  # power of 2 for FFT

    for N, p, q, label in TEST_CASES:
        print(f"\n  {label}: N={N}, p={p}, q={q}")

        for root_m, root_n in ROOTS[:3]:  # test 3 roots
            print(f"    Root ({root_m},{root_n}):")

            for bi, bname in enumerate(BRANCH_NAMES):
                # Compute true orbit periods
                T_p = find_orbit_period(root_m, root_n, p, bi, max_steps=20000)
                T_q = find_orbit_period(root_m, root_n, q, bi, max_steps=20000)

                # Walk and FFT
                seq = tree_walk_sequence(root_m, root_n, N, bi, walk_len)
                arr = np.array(seq, dtype=np.float64)
                arr = arr - arr.mean()  # remove DC
                spectrum = np.abs(np.fft.rfft(arr))
                freqs = np.fft.rfftfreq(walk_len)

                # Find top 5 peaks (skip DC at index 0)
                top_idx = np.argsort(spectrum[1:])[-5:][::-1] + 1
                top_freqs = freqs[top_idx]
                top_powers = spectrum[top_idx]

                # Check if any peak frequency matches 1/T_p or 1/T_q
                match_p = False
                match_q = False
                if T_p and T_p > 1:
                    target_p = 1.0 / T_p
                    for f in top_freqs:
                        if abs(f - target_p) < 1.0 / walk_len:
                            match_p = True
                if T_q and T_q > 1:
                    target_q = 1.0 / T_q
                    for f in top_freqs:
                        if abs(f - target_q) < 1.0 / walk_len:
                            match_q = True

                T_p_str = str(T_p) if T_p else ">20K"
                T_q_str = str(T_q) if T_q else ">20K"
                print(f"      {bname}: T_p={T_p_str}, T_q={T_q_str}, "
                      f"match_p={match_p}, match_q={match_q}, "
                      f"top_freq={top_freqs[0]:.6f}")

                results.append((label, root_m, root_n, bname,
                                T_p, T_q, match_p, match_q))

    # Factoring attempt: find peaks, convert to period, try gcd
    print(f"\n  Factoring attempt via FFT peak periods:")
    factored = 0
    for N, p, q, label in TEST_CASES:
        best_g = None
        for rm, rn in ROOTS[:3]:
            for bi in range(3):
                seq = tree_walk_sequence(rm, rn, N, bi, walk_len)
                arr = np.array(seq, dtype=np.float64)
                arr -= arr.mean()
                spectrum = np.abs(np.fft.rfft(arr))
                top_idx = np.argsort(spectrum[1:])[-10:][::-1] + 1
                freqs = np.fft.rfftfreq(walk_len)
                for idx in top_idx:
                    f = freqs[idx]
                    if f > 0:
                        period = int(round(1.0 / f))
                        if period > 1:
                            # The period mod N might relate to p or q
                            # Try gcd of various matrix-power results
                            M = FORWARD[bi]
                            m, n = rm % N, rn % N
                            # Apply M^period and check
                            mp, np_ = m, n
                            for _ in range(min(period, 10000)):
                                mp, np_ = mat_apply_mod(M, mp, np_, N)
                            # gcd of (m^T - m, N)
                            diff_m = (mp - m) % N
                            g = gcd(int(diff_m), int(N))
                            if 1 < g < N:
                                best_g = g
                                break
                    if best_g:
                        break
                if best_g:
                    break
            if best_g:
                break
        if best_g:
            print(f"    {label}: FACTORED! gcd(m_T - m_0, N) = {best_g}")
            factored += 1
        else:
            print(f"    {label}: No factor from FFT peaks")

    # Check how many had matching periods
    matches = sum(1 for r in results if r[6] or r[7])
    total = len(results)
    print(f"\n  Period matches: {matches}/{total} "
          f"({100*matches/total:.1f}% had at least one match)")

    if matches > total * 0.3:
        verdict = "PROMISING — FFT peaks correlate with orbit periods mod p,q"
    elif factored > 0:
        verdict = "PARTIAL — FFT-based factoring works for some cases"
    else:
        verdict = "WEAK — FFT peaks do not clearly reveal factor structure"
    print(f"\n  VERDICT: {verdict}")
    return results


# ============================================================================
# FIELD 9: SPECTRAL GRAPH THEORY — Cayley Graph Eigenvalues
# ============================================================================
def experiment_9_spectral():
    """
    Build the Cayley graph of (Z/NZ)^2 under action of {B1,B2,B3}.
    Compute eigenvalues of its adjacency matrix.
    Compare spectral gap for N=pq vs N=r (prime).
    """
    print(SEP)
    print("FIELD 9: SPECTRAL GRAPH THEORY — Cayley Graph Eigenvalues")
    print(SEP)

    def build_cayley_graph(N, roots_to_use, max_nodes=2000):
        """
        Build adjacency structure for Cayley graph of tree mod N.
        Start from given roots, BFS expand.
        Returns adjacency matrix as dense numpy array.
        """
        node_map = {}
        edges = []
        queue = deque()

        for rm, rn in roots_to_use:
            start = (rm % N, rn % N)
            if start not in node_map:
                node_map[start] = len(node_map)
                queue.append(start)

        while queue and len(node_map) < max_nodes:
            m, n = queue.popleft()
            i = node_map[(m, n)]
            for M in FORWARD:
                nm, nn = mat_apply_mod(M, m, n, N)
                if (nm, nn) not in node_map:
                    if len(node_map) >= max_nodes:
                        break
                    node_map[(nm, nn)] = len(node_map)
                    queue.append((nm, nn))
                j = node_map[(nm, nn)]
                edges.append((i, j))

        sz = len(node_map)
        adj = np.zeros((sz, sz), dtype=np.float64)
        for (i, j) in edges:
            adj[i][j] = 1.0
            adj[j][i] = 1.0  # undirected
        return adj, node_map

    def spectral_gap(adj):
        """Compute spectral gap = lambda_1 - lambda_2 of adjacency matrix."""
        if adj.shape[0] < 3:
            return 0.0, []
        # Use symmetric eigenvalue solver (real symmetric matrix)
        try:
            eigs = np.linalg.eigvalsh(adj)
            eigs = sorted(eigs, reverse=True)
            gap = eigs[0] - eigs[1] if len(eigs) > 1 else 0.0
            return gap, eigs[:5]
        except Exception:
            return 0.0, []

    results = []
    # Use small moduli only — adjacency matrix is N^2 x N^2 worst case
    small_cases = [(N, p, q, label) for N, p, q, label in TEST_CASES
                   if N < (1 << 30)]

    for N, p, q, label in small_cases:
        print(f"\n  {label}: N={N}, p={p}, q={q}")
        max_n = min(1500, N * N)  # cap graph size

        for rm, rn in ROOTS[:3]:
            # Graph mod N (composite)
            adj_N, nmap_N = build_cayley_graph(N, [(rm, rn)], max_nodes=max_n)
            gap_N, eigs_N = spectral_gap(adj_N)

            # Graph mod p (prime)
            adj_p, nmap_p = build_cayley_graph(p, [(rm, rn)], max_nodes=max_n)
            gap_p, eigs_p = spectral_gap(adj_p)

            # Graph mod q (prime)
            adj_q, nmap_q = build_cayley_graph(q, [(rm, rn)], max_nodes=max_n)
            gap_q, eigs_q = spectral_gap(adj_q)

            eN_str = ", ".join(f"{e:.2f}" for e in eigs_N[:3])
            ep_str = ", ".join(f"{e:.2f}" for e in eigs_p[:3])
            eq_str = ", ".join(f"{e:.2f}" for e in eigs_q[:3])

            print(f"    Root ({rm},{rn}):")
            print(f"      mod N: {len(nmap_N)} nodes, gap={gap_N:.4f}, top eigs=[{eN_str}]")
            print(f"      mod p: {len(nmap_p)} nodes, gap={gap_p:.4f}, top eigs=[{ep_str}]")
            print(f"      mod q: {len(nmap_q)} nodes, gap={gap_q:.4f}, top eigs=[{eq_str}]")

            results.append((label, rm, rn, gap_N, gap_p, gap_q,
                            len(nmap_N), len(nmap_p), len(nmap_q)))

    # Analysis: is gap(N) related to gap(p), gap(q)?
    print("\n  Spectral gap analysis:")
    for label, rm, rn, gN, gp, gq, szN, szp, szq in results:
        diff = abs(gN - min(gp, gq))
        print(f"    {label} root({rm},{rn}): "
              f"gap(N)={gN:.4f}, gap(p)={gp:.4f}, gap(q)={gq:.4f}, "
              f"|gap(N)-min|={diff:.4f}")

    if results:
        # Check if gap(N) is consistently close to min(gap(p), gap(q))
        close = sum(1 for r in results
                    if abs(r[3] - min(r[4], r[5])) < 0.5 * max(r[4], r[5], 0.01))
        total = len(results)
        print(f"\n  gap(N) ~ min(gap(p),gap(q)) in {close}/{total} cases "
              f"({100*close/total:.0f}%)")

        if close > total * 0.5:
            verdict = "PROMISING — spectral gap of composite reflects prime structure"
        else:
            verdict = "WEAK — spectral gap relationship unclear"
    else:
        verdict = "SKIPPED — no cases small enough"
    print(f"\n  VERDICT: {verdict}")
    return results


# ============================================================================
# FIELD 10: AUTOMATA THEORY — Factor-Revealing Language
# ============================================================================
def experiment_10_automata():
    """
    Enumerate all tree paths (words over {B1,B2,B3}) up to depth D.
    Identify which paths lead to factor-revealing nodes.
    Attempt to build a DFA that recognizes the factor-revealing language.
    Test if the DFA generalizes to other N.
    """
    print(SEP)
    print("FIELD 10: AUTOMATA THEORY — Factor-Revealing Language DFA")
    print(SEP)

    def enumerate_paths(root_m, root_n, N, max_depth):
        """
        Enumerate all paths up to max_depth.
        Returns list of (path_word, m, n, is_factor_revealing).
        """
        results = []
        # BFS: (m, n, word)
        queue = deque()
        queue.append((root_m, root_n, ()))
        while queue:
            m, n, word = queue.popleft()
            is_fr = check_factor(N, m, n) is not None
            results.append((word, m, n, is_fr))
            if len(word) < max_depth:
                for i, M in enumerate(FORWARD):
                    nm, nn = mat_apply(M, m, n)
                    queue.append((nm, nn, word + (i,)))
        return results

    def build_dfa_from_examples(positive_words, negative_words, alphabet_size=3):
        """
        Attempt to build a simple DFA using suffix-based state heuristic.
        State = last k symbols of the word (k-suffix automaton).
        Try k=1,2,3 and pick best.
        """
        best_k = 0
        best_acc = 0
        best_states = {}

        for k in range(1, 4):
            # Build state map: suffix -> {accept_count, reject_count}
            state_map = defaultdict(lambda: [0, 0])
            for w in positive_words:
                suffix = w[-k:] if len(w) >= k else w
                state_map[suffix][0] += 1
            for w in negative_words:
                suffix = w[-k:] if len(w) >= k else w
                state_map[suffix][1] += 1

            # Decision: accept if accept_count > reject_count
            decisions = {}
            for suffix, (acc, rej) in state_map.items():
                decisions[suffix] = acc > rej

            # Evaluate accuracy
            correct = 0
            total = 0
            for w in positive_words:
                suffix = w[-k:] if len(w) >= k else w
                if decisions.get(suffix, False):
                    correct += 1
                total += 1
            for w in negative_words:
                suffix = w[-k:] if len(w) >= k else w
                if not decisions.get(suffix, False):
                    correct += 1
                total += 1

            acc = correct / total if total > 0 else 0
            if acc > best_acc:
                best_acc = acc
                best_k = k
                best_states = dict(decisions)

        return best_k, best_acc, best_states

    def growth_rate(counts_by_depth):
        """Compute average growth rate of factor-revealing words per level."""
        rates = []
        depths = sorted(counts_by_depth.keys())
        for i in range(1, len(depths)):
            d0, d1 = depths[i-1], depths[i]
            c0, c1 = counts_by_depth[d0], counts_by_depth[d1]
            if c0 > 0:
                rates.append(c1 / c0)
        return sum(rates) / len(rates) if rates else 0

    results = []
    # Limit to small N where enumeration is tractable
    small_cases = [(N, p, q, label) for N, p, q, label in TEST_CASES
                   if N < (1 << 35)]

    for N, p, q, label in small_cases:
        max_depth = 10 if N < (1 << 25) else 8
        print(f"\n  {label}: N={N}, p={p}, q={q}, max_depth={max_depth}")

        for rm, rn in ROOTS[:4]:
            paths = enumerate_paths(rm, rn, N, max_depth)
            positive = [w for w, m, n, fr in paths if fr and len(w) > 0]
            negative = [w for w, m, n, fr in paths if not fr and len(w) > 0]
            total = len(positive) + len(negative)

            # Count by depth
            fr_by_depth = defaultdict(int)
            total_by_depth = defaultdict(int)
            for w, m, n, fr in paths:
                d = len(w)
                total_by_depth[d] += 1
                if fr:
                    fr_by_depth[d] += 1

            density = len(positive) / total if total > 0 else 0
            gr = growth_rate(fr_by_depth)

            # Build DFA
            k, acc, states = build_dfa_from_examples(positive, negative)

            print(f"    Root ({rm},{rn}): {len(positive)}/{total} factor-revealing "
                  f"({100*density:.2f}%), growth_rate={gr:.2f}")
            print(f"      Best DFA: k={k}-suffix, accuracy={100*acc:.1f}%")

            # Depth breakdown
            for d in sorted(total_by_depth.keys())[:6]:
                fr_d = fr_by_depth.get(d, 0)
                tot_d = total_by_depth[d]
                pct = 100 * fr_d / tot_d if tot_d > 0 else 0
                print(f"        depth {d}: {fr_d}/{tot_d} ({pct:.1f}%)")

            results.append((label, rm, rn, density, gr, k, acc))

    # Generalization test: train DFA on one N, test on another
    print("\n  Generalization test (train on 20b, test on 28b):")
    if len(small_cases) >= 2:
        N_train, p_train, q_train, _ = small_cases[0]
        N_test, p_test, q_test, _ = small_cases[1]

        for rm, rn in ROOTS[:2]:
            # Train
            paths_train = enumerate_paths(rm, rn, N_train, 8)
            pos_train = [w for w, m, n, fr in paths_train if fr and len(w) > 0]
            neg_train = [w for w, m, n, fr in paths_train if not fr and len(w) > 0]
            k, acc_train, states = build_dfa_from_examples(pos_train, neg_train)

            # Test
            paths_test = enumerate_paths(rm, rn, N_test, 8)
            correct = 0
            total = 0
            for w, m, n, fr in paths_test:
                if len(w) == 0:
                    continue
                suffix = w[-k:] if len(w) >= k else w
                prediction = states.get(suffix, False)
                if prediction == fr:
                    correct += 1
                total += 1
            acc_test = correct / total if total > 0 else 0
            print(f"    Root ({rm},{rn}): train_acc={100*acc_train:.1f}%, "
                  f"test_acc={100*acc_test:.1f}% "
                  f"({'GENERALIZES' if acc_test > 0.6 else 'DOES NOT GENERALIZE'})")

    # Language regularity analysis
    print("\n  Language regularity analysis:")
    # If factor-revealing density is constant across depths -> likely regular
    # If it decays -> context-free or context-sensitive
    for label, rm, rn, density, gr, k, acc in results[:4]:
        if abs(gr - 1.0) < 0.3:
            reg = "REGULAR-like (constant density)"
        elif gr > 1.0:
            reg = "SUPER-LINEAR growth (not regular)"
        else:
            reg = "SUB-LINEAR growth (density decays)"
        print(f"    {label} root({rm},{rn}): {reg}, DFA acc={100*acc:.1f}%")

    # Verdict
    accuracies = [r[6] for r in results]
    avg_acc = sum(accuracies) / len(accuracies) if accuracies else 0
    if avg_acc > 0.85:
        verdict = "CONFIRMED — factor-revealing language is approximately regular (DFA works)"
    elif avg_acc > 0.7:
        verdict = "PARTIAL — k-suffix DFA captures some structure but not all"
    else:
        verdict = "REJECTED — factor-revealing language is NOT regular"
    print(f"\n  VERDICT: {verdict}")
    return results


# ============================================================================
# MAIN
# ============================================================================
def main():
    print("=" * 72)
    print("PYTHAGOREAN TREE FACTORING: CROSS-MATHEMATICS VOL. 2")
    print("Fields 6-10: Fractal, Category, Fourier, Spectral, Automata")
    print("=" * 72)
    print(f"\nRoots tested: {ROOTS}")
    print(f"Test cases:")
    for N, p, q, label in TEST_CASES:
        print(f"  {label}: N={N} = {p} * {q}")
    print()

    all_results = {}
    experiments = [
        ("Field 6: Fractal Geometry", experiment_6_fractal),
        ("Field 7: Category Theory", experiment_7_category),
        ("Field 8: Fourier Analysis", experiment_8_fourier),
        ("Field 9: Spectral Graph Theory", experiment_9_spectral),
        ("Field 10: Automata Theory", experiment_10_automata),
    ]

    for name, func in experiments:
        t0 = time.time()
        try:
            result = func()
            elapsed = time.time() - t0
            all_results[name] = result
            print(f"\n  [{name}] completed in {elapsed:.1f}s")
        except Exception as e:
            elapsed = time.time() - t0
            print(f"\n  [{name}] FAILED after {elapsed:.1f}s: {e}")
            import traceback
            traceback.print_exc()
        print()

    # Final summary
    print(SEP)
    print("FINAL SUMMARY")
    print(SEP)
    print(f"  Experiments completed: {len(all_results)}/{len(experiments)}")
    print(f"  Roots tested: {len(ROOTS)}")
    print(f"  Semiprime sizes: {TEST_BITS}")
    print()
    print("  Key questions answered:")
    print("    6. Does fractal dimension mod N differ for pq vs p^2?")
    print("    7. Does Berggren monoid size follow CRT (lcm of mod-p, mod-q sizes)?")
    print("    8. Does FFT of tree walks reveal orbit periods related to p, q?")
    print("    9. Does spectral gap of Cayley graph encode factoring info?")
    print("   10. Is the factor-revealing language regular (DFA-recognizable)?")


if __name__ == "__main__":
    main()

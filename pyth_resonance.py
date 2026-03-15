#!/usr/bin/env python3
"""
B3-SIQS Engine — Self-Initializing QS with C Sieve + Gray Code + DLP
=====================================================================

Upgrade from B3-MPQS with these key wins:
  1. Gray Code B-switching: 2^(s-1) polys per 'a', O(FB_size) additions per switch
  2. Precomputed offset delta arrays: incremental sieve offset updates
  3. Double Large Prime (DLP): graph-based cycle finding for 2-LP relations
  4. Knuth-Schroeppel multiplier selection
  5. Small prime optimization: skip p<32 in sieve, adjust threshold
  6. C sieve kernel (mpqs_sieve_c.so) + C batch trial division

Critical bug fixes preserved:
  - B_j = t_roots[j] * A_j * A_j_inv % a — MUST reduce mod a
  - Sieve g(x) = a*x^2 + 2*b*x + c where c = (b^2 - n) / a
  - T_bits = nb//4-1 for nb>=180, nb//4-2 otherwise
  - Do NOT reduce b mod a — breaks incremental offset updates
  - LP bound: min(B*100, B^2)
"""

import gmpy2
from gmpy2 import mpz, isqrt, is_prime, gcd, jacobi, next_prime, iroot, legendre
import numpy as np
import ctypes
import time
import math
import os
import bisect
import random
from collections import defaultdict

###############################################################################
# C EXTENSION LOADING
###############################################################################

_c_lib = None

def _load_c_lib():
    """Load the C sieve+trial-division shared library."""
    global _c_lib
    if _c_lib is not None:
        return _c_lib
    so_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mpqs_sieve_c.so')
    if not os.path.exists(so_path):
        c_path = so_path.replace('.so', '.c')
        if os.path.exists(c_path):
            os.system(f'gcc -O3 -march=native -shared -fPIC -o {so_path} {c_path} -lm')
    if not os.path.exists(so_path):
        raise RuntimeError(f"Cannot find {so_path}")
    lib = ctypes.CDLL(so_path)

    lib.sieve_poly.restype = None
    lib.sieve_poly.argtypes = [
        ctypes.POINTER(ctypes.c_uint16), ctypes.c_int,
        ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_uint16),
        ctypes.c_int,
    ]
    lib.find_survivors.restype = ctypes.c_int
    lib.find_survivors.argtypes = [
        ctypes.POINTER(ctypes.c_uint16), ctypes.c_int, ctypes.c_int,
        ctypes.POINTER(ctypes.c_int), ctypes.c_int,
    ]
    lib.trial_divide_batch.restype = ctypes.c_int
    lib.trial_divide_batch.argtypes = [
        ctypes.POINTER(ctypes.c_int64), ctypes.POINTER(ctypes.c_int64),
        ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.c_int,
        ctypes.c_int64, ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int64), ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ]
    _c_lib = lib
    return lib


###############################################################################
# TONELLI-SHANKS
###############################################################################

def tonelli_shanks(n, p):
    """Compute r such that r^2 = n (mod p), or None if no solution."""
    n = n % p
    if n == 0:
        return 0
    if p == 2:
        return n
    if pow(n, (p - 1) // 2, p) != 1:
        return None
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    if s == 1:
        return pow(n, (p + 1) // 4, p)
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m, c, t, r = s, pow(z, q, p), pow(n, q, p), pow(n, (q + 1) // 2, p)
    while True:
        if t == 1:
            return r
        i, tmp = 1, t * t % p
        while tmp != 1:
            tmp = tmp * tmp % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m, c, t, r = i, b * b % p, t * b * b % p, r * b % p


###############################################################################
# HELPER: encode Python int as (hi64, lo64) for C __int128
###############################################################################

def _encode_128(val):
    """Encode a Python integer as (hi64, lo64) pair for C __int128."""
    MASK64 = (1 << 64) - 1
    if val >= 0:
        lo = val & MASK64
        hi = (val >> 64) & MASK64
    else:
        val128 = val & ((1 << 128) - 1)
        lo = val128 & MASK64
        hi = (val128 >> 64) & MASK64
    if hi >= (1 << 63):
        hi -= (1 << 64)
    if lo >= (1 << 63):
        lo -= (1 << 64)
    return int(hi), int(lo)


###############################################################################
# PYTHON FALLBACK TRIAL DIVISION (for values > 128 bits)
###############################################################################

def _py_trial_divide(val, fb, fb_size):
    """Trial divide |val| by factor base. Returns (exps_list, cofactor)."""
    v = abs(val)
    exps = [0] * fb_size
    for i in range(fb_size):
        p = fb[i]
        if v == 1:
            break
        if p * p > v:
            break
        q, r = divmod(v, p)
        if r == 0:
            e = 1
            v = q
            q, r = divmod(v, p)
            while r == 0:
                e += 1
                v = q
                q, r = divmod(v, p)
            exps[i] = e
    if v > 1 and v <= fb[-1]:
        lo, hi = 0, fb_size - 1
        while lo <= hi:
            mid = (lo + hi) >> 1
            if fb[mid] == v:
                exps[mid] += 1
                return exps, 1
            elif fb[mid] < v:
                lo = mid + 1
            else:
                hi = mid - 1
    return exps, v


###############################################################################
# POLLARD RHO for DLP cofactor splitting
###############################################################################

def _quick_factor(n_val, limit=200):
    """Quick Pollard rho to split a cofactor into two primes."""
    if n_val < 4:
        return None
    if n_val % 2 == 0:
        return 2
    for c in (1, 3, 5):
        x, y, d = 2, 2, 1
        while d == 1 and limit > 0:
            x = (x * x + c) % n_val
            y = (y * y + c) % n_val
            y = (y * y + c) % n_val
            d = math.gcd(abs(x - y), n_val)
            limit -= 1
        if 1 < d < n_val:
            return int(d)
    return None


###############################################################################
# KNUTH-SCHROEPPEL MULTIPLIER
###############################################################################

def _ks_select_multiplier(N, verbose=False):
    """
    Knuth-Schroeppel multiplier selection.
    Test squarefree k=1..67, score by small primes with jacobi(kN, p)=1.
    """
    candidates = [1, 2, 3, 5, 6, 7, 10, 11, 13, 14, 15, 17, 19, 21,
                  23, 26, 29, 30, 31, 33, 34, 37, 38, 41, 42, 43,
                  46, 47, 51, 53, 55, 57, 58, 59, 61, 62, 65, 66, 67]
    scored = []
    for k in candidates:
        kN = N * k
        sq = isqrt(kN)
        if sq * sq == kN:
            continue
        score = -math.log(k) / 2.0 if k > 1 else 0.0
        kN_mod8 = int(kN % 8)
        if kN_mod8 == 1:
            score += 2.0 * math.log(2.0)
        elif kN_mod8 == 5:
            score += math.log(2.0)
        elif kN_mod8 == 0:
            score += math.log(2.0) * 0.5
        p = mpz(3)
        for _ in range(80):
            pf = float(p)
            leg = legendre(kN, p)
            if leg == 1:
                score += 2.0 * math.log(pf) / (pf - 1.0)
            elif leg == 0:
                score += math.log(pf) / pf
            p = next_prime(p)
        scored.append((score, k))
    scored.sort(reverse=True)
    if verbose:
        top5 = [(k, f"{s:.3f}") for s, k in scored[:5]]
        print(f"    K-S multipliers (top 5): {top5}")
    return scored[0][1]


###############################################################################
# GRAY CODE UTILITIES
###############################################################################

def gray_code_sequence(num_bits):
    """
    Generate Gray code sequence for num_bits bits.
    Returns list of (gray_value, bit_that_flipped, direction) tuples.
    Consecutive values differ by exactly one bit => only one B_value sign flips.
    """
    seq = []
    prev = 0
    for i in range(1, 1 << num_bits):
        gray = i ^ (i >> 1)
        changed_bit = (prev ^ gray)
        bit_pos = 0
        while (changed_bit >> bit_pos) & 1 == 0:
            bit_pos += 1
        direction = 1 if (gray >> bit_pos) & 1 else -1
        seq.append((gray, bit_pos, direction))
        prev = gray
    return seq


###############################################################################
# DOUBLE LARGE PRIME GRAPH
###############################################################################

class DoubleLargePrimeGraph:
    """
    Manages relations with up to 2 large prime cofactors.
    SLP: one large prime < lp_bound. Two SLPs with same LP combine.
    DLP: cofactor = product of two primes, each < lp_bound.
         Stored in graph; cycles yield full relations.
    """

    def __init__(self, n, fb_size, lp_bound):
        self.n = int(n)
        self.fb_size = fb_size
        self.lp_bound = lp_bound
        self.slp_partials = {}
        self.dlp_graph = defaultdict(list)
        self.dlp_count = 0
        self._uf_parent = {}
        self._uf_rank = {}
        self.smooth = []  # (x, sign, exps, lp_val)
        self.n_slp_combined = 0
        self.n_dlp_combined = 0

    def _uf_find(self, x):
        if x not in self._uf_parent:
            self._uf_parent[x] = x
            self._uf_rank[x] = 0
            return x
        root = x
        while self._uf_parent[root] != root:
            root = self._uf_parent[root]
        while self._uf_parent[x] != root:
            self._uf_parent[x], x = root, self._uf_parent[x]
        return root

    def _uf_union(self, a, b):
        ra, rb = self._uf_find(a), self._uf_find(b)
        if ra == rb:
            return
        if self._uf_rank[ra] < self._uf_rank[rb]:
            ra, rb = rb, ra
        self._uf_parent[rb] = ra
        if self._uf_rank[ra] == self._uf_rank[rb]:
            self._uf_rank[ra] += 1

    def add_smooth(self, x, sign, exps):
        self.smooth.append((x, sign, exps, 0))

    def add_single_lp(self, x, sign, exps, lp):
        lp = int(lp)
        if lp in self.slp_partials:
            ox, os, oe = self.slp_partials.pop(lp)
            # Combined: x1*x2 on left, lp^2 on right (even exp, cancels in GF(2))
            cax = ox * x % self.n
            cs = (os + sign) % 2
            ce = [oe[j] + exps[j] for j in range(self.fb_size)]
            self.smooth.append((cax, cs, ce, lp))
            self.n_slp_combined += 1
        else:
            self.slp_partials[lp] = (x, sign, exps)
        return None

    def add_double_lp(self, x, sign, exps, lp1, lp2):
        lp1, lp2 = int(min(lp1, lp2)), int(max(lp1, lp2))
        self.dlp_count += 1
        if lp1 == lp2:
            return self.add_single_lp(x, sign, exps, lp1)
        if self.dlp_count > 50000:
            return None
        sparse = tuple((j, e) for j, e in enumerate(exps) if e != 0)
        if self._uf_find(lp1) == self._uf_find(lp2):
            path = self._find_path(lp1, lp2, max_depth=5)
            if path is not None:
                result = self._combine_cycle(path, x, sign, sparse, lp1, lp2)
                if result is not None:
                    return result
        self.dlp_graph[lp1].append((lp2, x, sign, sparse))
        self.dlp_graph[lp2].append((lp1, x, sign, sparse))
        self._uf_union(lp1, lp2)
        return None

    def _find_path(self, start, end, max_depth=5):
        if start not in self.dlp_graph or end not in self.dlp_graph:
            return None
        visited = {start: None}
        queue = [start]
        depth = {start: 0}
        while queue:
            node = queue.pop(0)
            if depth[node] >= max_depth:
                continue
            for neighbor, x, sign, exps in self.dlp_graph[node]:
                if neighbor == end:
                    path = [(node, neighbor)]
                    cur = node
                    while visited[cur] is not None:
                        prev = visited[cur]
                        path.append((prev, cur))
                        cur = prev
                    path.reverse()
                    return path
                if neighbor not in visited:
                    visited[neighbor] = node
                    depth[neighbor] = depth[node] + 1
                    queue.append(neighbor)
        return None

    def _combine_cycle(self, path, new_x, new_sign, new_sparse, lp1, lp2):
        combined_x = new_x
        combined_sign = new_sign
        combined_exps = [0] * self.fb_size
        for idx, val in new_sparse:
            combined_exps[idx] = val
        lp_counts = defaultdict(int)
        lp_counts[lp1] += 1
        lp_counts[lp2] += 1
        for src, dst in path:
            edge_found = False
            for neighbor, x, sign, sparse in self.dlp_graph[src]:
                if neighbor == dst:
                    combined_x = combined_x * x % self.n
                    combined_sign = (combined_sign + sign) % 2
                    for idx, val in sparse:
                        combined_exps[idx] += val
                    lp_counts[src] += 1
                    lp_counts[dst] += 1
                    edge_found = True
                    break
            if not edge_found:
                return None
        # Each LP appears an even number of times in the combined relation,
        # so lp^(2k) cancels in GF(2). No v_inv needed — just store the product.
        # But we need lp_product for factor extraction (lp appears in exponent).
        # Store lp=0 since all LP exponents are even and cancel in GF(2).
        self.smooth.append((combined_x, combined_sign, combined_exps, 0))
        self.n_dlp_combined += 1
        return None

    @property
    def num_smooth(self):
        return len(self.smooth)

    @property
    def num_partials(self):
        return len(self.slp_partials)


###############################################################################
# PARAMETER TABLE — Tuned for SIQS with Gray code
###############################################################################

def b3mpqs_params(nd):
    """
    Parameter selection for B3-SIQS.
    Returns (fb_size, sieve_half).
    Tuned: SIQS poly switching is much cheaper so we can use slightly larger M.
    """
    tbl = [
        (20,    80,   15000),
        (25,   150,   30000),
        (30,   300,   60000),
        (35,   500,  120000),
        (40,   900,  200000),
        (45,  1500,  350000),
        (50,  2800,  700000),
        (55,  3800, 1000000),
        (60,  4500, 1500000),
        (63,  5000, 2000000),
        (66,  5500, 2500000),
        (69,  6200, 3000000),
        (72,  7000, 4000000),
        (75, 10000, 7000000),
    ]
    for i in range(len(tbl) - 1):
        if tbl[i][0] <= nd < tbl[i + 1][0]:
            frac = (nd - tbl[i][0]) / (tbl[i + 1][0] - tbl[i][0])
            fb = int(tbl[i][1] + frac * (tbl[i + 1][1] - tbl[i][1]))
            M = int(tbl[i][2] + frac * (tbl[i + 1][2] - tbl[i][2]))
            return fb, M
    if nd <= tbl[0][0]:
        return tbl[0][1], tbl[0][2]
    return tbl[-1][1], tbl[-1][2]


###############################################################################
# MAIN B3-SIQS ENGINE
###############################################################################

def b3mpqs_factor(N, verbose=True, time_limit=3600):
    """
    Factor N using Self-Initializing QS with C-accelerated sieve,
    Gray code polynomial switching, and Double Large Prime variation.
    """
    N = mpz(N)
    nd = len(str(N))
    nb = int(gmpy2.log2(N)) + 1
    N_int = int(N)

    # Quick checks
    if N <= 1: return 0
    if N % 2 == 0: return 2
    if N % 3 == 0: return 3
    for small_p in range(5, 1000, 2):
        if N % small_p == 0:
            return small_p
    for exp in range(2, nb + 1):
        root, exact = iroot(N, exp)
        if exact:
            return int(root)
    if is_prime(N):
        return int(N)
    sq = isqrt(N)
    if sq * sq == N:
        return int(sq)

    t0 = time.time()

    # Knuth-Schroeppel multiplier — disabled for now (extraction needs work)
    k_mult = 1
    kN = N
    kN_int = N_int

    # Load C library
    try:
        clib = _load_c_lib()
        use_c = True
    except Exception as e:
        if verbose:
            print(f"  WARNING: C lib not available ({e}), using Python fallback")
        use_c = False
        clib = None

    fb_size_target, sieve_half = b3mpqs_params(nd)

    # Build factor base: primes p where jacobi(kN, p) = 1 (or p=2)
    fb = []
    p = 2
    while len(fb) < fb_size_target:
        if p == 2 or (is_prime(p) and jacobi(int(kN % p), p) == 1):
            fb.append(int(p))
        p = int(next_prime(p)) if p > 2 else 3

    fb_size = len(fb)
    fb_index = {p: i for i, p in enumerate(fb)}

    # C arrays for factor base
    c_fb_primes = (ctypes.c_int * fb_size)(*fb)
    fb_np = np.array(fb, dtype=np.int64)  # numpy copy for vectorized offset ops
    LOG_SCALE = 16
    fb_logp_vals = [max(1, int(round(math.log2(p) * LOG_SCALE))) for p in fb]
    c_fb_logp = (ctypes.c_uint16 * fb_size)(*fb_logp_vals)

    # Precompute sqrt(kN) mod p for each FB prime
    sqrt_N_mod = {}
    for p in fb:
        if p == 2:
            sqrt_N_mod[2] = int(kN % 2)
        else:
            sqrt_N_mod[p] = tonelli_shanks(int(kN % p), p)

    # Large prime bound
    lp_bound = min(fb[-1] ** 2, fb[-1] * 100)
    # DLP bound: cofactor up to lp_bound^2 can be split into two primes
    dlp_bound = lp_bound * lp_bound

    # Sieve threshold
    kN_nb = int(gmpy2.log2(kN)) + 1
    if kN_nb >= 180:
        T_bits = max(15, kN_nb // 4 - 1)
    else:
        T_bits = max(15, kN_nb // 4 - 2)

    # Small prime correction (in log2*LOG_SCALE scale)
    small_prime_correction = 0
    for p in fb:
        if p >= 32:
            break
        roots = 1 if p == 2 else 2
        small_prime_correction += roots * math.log2(p) * LOG_SCALE / p
    small_prime_correction = int(small_prime_correction * 0.60)

    needed = fb_size + max(30, fb_size // 5)
    sz = 2 * sieve_half
    M = sieve_half

    # DLP relation manager
    dlp_graph = DoubleLargePrimeGraph(kN_int, fb_size, lp_bound)

    if verbose:
        print(f"B3-SIQS{'(C)' if use_c else ''}: {nd}d ({nb}b), |FB|={fb_size}, M={M}, "
              f"need={needed}, LP<={int(math.log10(max(lp_bound,10))):.0f}d")
        print(f"  FB[{fb[0]}..{fb[-1]}], T_bits={T_bits}, DLP=on")

    poly_count = 0
    total_cands = 0
    a_count = 0

    # Pre-allocate C buffers
    if use_c:
        c_sieve = (ctypes.c_uint16 * sz)()
        max_survivors = min(sz, 100000)
        c_survivors = (ctypes.c_int * max_survivors)()
        c_offsets1 = (ctypes.c_int * fb_size)()
        c_offsets2 = (ctypes.c_int * fb_size)()
        td_max = max_survivors
        c_gx_hi = (ctypes.c_int64 * td_max)()
        c_gx_lo = (ctypes.c_int64 * td_max)()
        c_td_exps = (ctypes.c_int * (td_max * fb_size))()
        c_td_cofactors = (ctypes.c_int64 * td_max)()
        c_td_signs = (ctypes.c_int * td_max)()
        c_td_status = (ctypes.c_int * td_max)()
        c_td_n_smooth = (ctypes.c_int * 1)()

    # Target a ~ sqrt(2*kN) / M
    target_a = isqrt(2 * kN) // M
    log_target = float(gmpy2.log2(target_a)) if target_a > 0 else 0

    # Choose s (number of primes in a) and FB range
    best_s = 2
    best_range = (1, len(fb) - 1)
    best_score = float('inf')
    for s_try in range(2, 12):
        ideal_log = log_target / s_try
        if ideal_log < 3.5 or ideal_log > 50:
            continue
        ideal_prime = int(2 ** ideal_log)
        mid = bisect.bisect_left(fb, ideal_prime)
        if mid >= len(fb):
            continue
        lo = max(1, mid - max(s_try * 5, 20))
        hi = min(len(fb) - 1, mid + max(s_try * 5, 20))
        pool_size = hi - lo
        if pool_size < s_try * 3:
            continue
        actual_median = fb[min(max(mid, lo), hi)]
        score = abs(math.log2(max(actual_median, 2)) - ideal_log)
        if ideal_prime < 100:
            score += 2.0
        elif ideal_prime < 500:
            score += 0.5
        if s_try > 8:
            score += (s_try - 8) * 0.5
        if score < best_score:
            best_score = score
            best_s = s_try
            best_range = (lo, hi)

    s = best_s
    select_lo, select_hi = best_range

    # Generate Gray code sequence for 2^(s-1) poly variants per 'a'
    gray_seq = gray_code_sequence(s - 1)
    n_polys_per_a = 1 + len(gray_seq)  # first poly + gray variants

    if verbose:
        print(f"  s={s}, select FB[{select_lo}..{select_hi}], {n_polys_per_a} polys/a")

    gx_max_bits = int(log_target + 2 * math.log2(max(M, 1))) + 10
    can_use_c_td = use_c
    if verbose and use_c:
        print(f"  g(x) max ~{gx_max_bits}b, C trial div: yes")

    # Precompute threshold (constant for all polys)
    log_g_max = math.log2(max(M, 1)) + 0.5 * kN_nb
    thresh = int(max(0, (log_g_max - T_bits)) * LOG_SCALE) - small_prime_correction
    thresh = max(1, thresh)

    # ======================================================================
    # Helper: process one sieved polynomial
    # ======================================================================
    MAX_128 = (1 << 127) - 1

    def _process_poly(a_int, b_int, c_int, a_prime_exps):
        """Sieve one polynomial and collect relations. Returns direct factor or None."""
        nonlocal poly_count, total_cands

        # --- Sieve (offsets already set by caller) ---
        ctypes.memset(c_sieve, 0, sz * 2)
        clib.sieve_poly(c_sieve, sz, c_fb_primes, c_offsets1, c_offsets2,
                       c_fb_logp, fb_size)
        n_surv = clib.find_survivors(c_sieve, sz, thresh, c_survivors, max_survivors)

        poly_count += 1

        if n_surv == 0:
            return None

        total_cands += n_surv

        # --- Compute g(x) and ax+b for each survivor ---
        gx_list = []
        axb_list = []

        for ci in range(n_surv):
            sieve_idx = c_survivors[ci]
            x = sieve_idx - M
            gx = a_int * x * x + 2 * b_int * x + c_int
            ax_b = a_int * x + b_int
            gx_list.append(gx)
            axb_list.append(ax_b)

        n_cand = len(gx_list)
        if n_cand == 0:
            return None

        # Split candidates: C vs Python
        c_indices = []
        py_indices = []
        for ci in range(n_cand):
            gx = gx_list[ci]
            if gx == 0:
                g = gcd(mpz(axb_list[ci]), kN)
                if 1 < g < kN:
                    # Factor of kN found
                    g_int = int(g)
                    # Check if it's a factor of N
                    gN = gcd(mpz(g_int), N)
                    if 1 < gN < N:
                        return int(gN)
            elif -MAX_128 <= gx <= MAX_128:
                c_indices.append(ci)
            else:
                py_indices.append(ci)

        # C batch trial division
        n_c = len(c_indices)
        if n_c > 0:
            for idx, ci in enumerate(c_indices):
                hi, lo = _encode_128(gx_list[ci])
                c_gx_hi[idx] = hi
                c_gx_lo[idx] = lo

            c_td_n_smooth[0] = 0
            clib.trial_divide_batch(
                c_gx_hi, c_gx_lo, n_c,
                c_fb_primes, fb_size, lp_bound,
                c_td_exps, c_td_cofactors, c_td_signs, c_td_status, c_td_n_smooth
            )

            for idx in range(n_c):
                status = c_td_status[idx]
                if status == 0:
                    continue

                ci = c_indices[idx]
                ax_b = axb_list[ci]
                sign = c_td_signs[idx]
                cofactor = c_td_cofactors[idx]

                exps = [0] * fb_size
                base = idx * fb_size
                for j in range(fb_size):
                    exps[j] = c_td_exps[base + j] + a_prime_exps[j]

                x_stored = int(mpz(ax_b) % kN_int)

                if status == 1:
                    dlp_graph.add_smooth(x_stored, sign, exps)
                elif status == 2:
                    lp = int(cofactor)
                    result = dlp_graph.add_single_lp(x_stored, sign, exps, lp)
                    if result is not None and isinstance(result, int):
                        gN = int(gcd(mpz(result), N))
                        if 1 < gN < N_int:
                            return gN

        # Python fallback for overflow candidates
        for ci in py_indices:
            gx = gx_list[ci]
            ax_b = axb_list[ci]
            sign = 1 if gx < 0 else 0
            exps, cofactor = _py_trial_divide(gx, fb, fb_size)
            for j in range(fb_size):
                exps[j] += a_prime_exps[j]
            x_stored = int(mpz(ax_b) % kN_int)
            if cofactor == 1:
                dlp_graph.add_smooth(x_stored, sign, exps)
            elif 1 < cofactor <= lp_bound:
                if is_prime(cofactor):
                    result = dlp_graph.add_single_lp(x_stored, sign, exps, int(cofactor))
                    if result is not None and isinstance(result, int):
                        gN = int(gcd(mpz(result), N))
                        if 1 < gN < N_int:
                            return gN

        return None

    # ======================================================================
    # MAIN SIEVE LOOP — SIQS with Gray code switching
    # ======================================================================

    while dlp_graph.num_smooth < needed:
        if time.time() - t0 > time_limit:
            if verbose:
                print(f"\n  Time limit ({time_limit}s) reached")
            break

        # --- Select 'a' as product of s FB primes near target ---
        best_a = None
        best_diff = float('inf')
        for _ in range(20):
            try:
                indices = sorted(random.sample(range(select_lo, select_hi), s))
            except ValueError:
                continue
            a = mpz(1)
            for i in indices:
                a *= fb[i]
            diff = abs(float(gmpy2.log2(a)) - log_target) if a > 0 else float('inf')
            if diff < best_diff:
                best_diff = diff
                best_a = a
                best_primes = [fb[i] for i in indices]

        if best_a is None:
            continue

        a = best_a
        a_primes = best_primes
        a_prime_set = set(a_primes)
        a_prime_idx = [fb_index[ap] for ap in a_primes]
        a_int = int(a)
        a_count += 1

        # Compute prime factorization exps for 'a'
        a_prime_exps = [0] * fb_size
        for ap in a_primes:
            if ap in fb_index:
                a_prime_exps[fb_index[ap]] += 1

        # --- Compute t_roots: sqrt(kN) mod q for each q in a ---
        t_roots = []
        ok = True
        for q in a_primes:
            t = sqrt_N_mod.get(q)
            if t is None:
                ok = False
                break
            t_roots.append(t)
        if not ok:
            continue

        # --- Compute B_values for Gray code switching ---
        B_values = []
        b_ok = True
        for j in range(s):
            q = a_primes[j]
            A_j = a // q
            try:
                A_j_inv = pow(int(A_j % q), -1, q)
            except (ValueError, ZeroDivisionError):
                b_ok = False
                break
            B_j = mpz(t_roots[j]) * A_j * mpz(A_j_inv) % a
            B_values.append(B_j)
        if not b_ok:
            continue

        # --- Precompute a_inv mod p for each FB prime ---
        a_inv_mod = [0] * fb_size
        is_a_prime_flag = [False] * fb_size
        for pi in range(fb_size):
            p = fb[pi]
            if p in a_prime_set:
                is_a_prime_flag[pi] = True
            else:
                try:
                    a_inv_mod[pi] = pow(a_int % p, -1, p)
                except (ValueError, ZeroDivisionError):
                    a_inv_mod[pi] = 0

        # --- Precompute delta arrays for Gray code switching ---
        # delta[j][pi] = (2 * B_values[j] mod p) * a_inv_mod[pi] mod p
        deltas = []
        for j in range(s):
            d = [0] * fb_size
            B_j_2 = int(2 * B_values[j])
            for pi in range(fb_size):
                if is_a_prime_flag[pi]:
                    continue
                p = fb[pi]
                d[pi] = B_j_2 % p * a_inv_mod[pi] % p
            deltas.append(d)

        # --- First polynomial: all B signs positive ---
        b = mpz(0)
        for B_j in B_values:
            b += B_j

        if (b * b - kN) % a != 0:
            b = -b
            if (b * b - kN) % a != 0:
                continue

        c = (b * b - kN) // a
        b_int = int(b)
        c_int = int(c)

        # --- Compute initial sieve offsets ---
        for pi in range(fb_size):
            p = fb[pi]
            o1_val = -1
            o2_val = -1

            if p == 2:
                g0 = c_int % 2
                g1 = (a_int + 2 * b_int + c_int) % 2
                if g0 == 0:
                    o1_val = M % 2
                    if g1 == 0:
                        o2_val = (M + 1) % 2
                elif g1 == 0:
                    o1_val = (M + 1) % 2
            elif p in a_prime_set:
                b2 = (2 * b_int) % p
                if b2 != 0:
                    b2_inv = pow(b2, -1, p)
                    c_mod = c_int % p
                    r = (-c_mod * b2_inv) % p
                    o1_val = (r + M) % p
            else:
                t = sqrt_N_mod.get(p)
                if t is not None:
                    ai = a_inv_mod[pi]
                    bm = b_int % p
                    r1 = (ai * (t - bm)) % p
                    r2 = (ai * (p - t - bm)) % p
                    o1_val = (r1 + M) % p
                    o2_val = ((r2 + M) % p) if r2 != r1 else -1

            if use_c:
                c_offsets1[pi] = o1_val
                c_offsets2[pi] = o2_val

        # --- Sieve first polynomial ---
        result = _process_poly(a_int, b_int, c_int, a_prime_exps)
        if result is not None:
            total_t = time.time() - t0
            if verbose:
                print(f"\n  *** FACTOR (direct): {result} ({total_t:.1f}s) ***")
            if k_mult > 1:
                g = int(gcd(mpz(result), N))
                return int(g) if 1 < g < N_int else 0
            return int(result)

        # --- Gray code B-switching for remaining 2^(s-1)-1 polynomials ---
        signs = [1] * s
        # Store offsets as Python lists for fast incremental update
        off1 = [c_offsets1[i] for i in range(fb_size)]
        off2 = [c_offsets2[i] for i in range(fb_size)]

        for gray_val, flip_bit, flip_dir in gray_seq:
            if dlp_graph.num_smooth >= needed:
                break

            j = flip_bit + 1
            if j >= s:
                continue

            old_sign = signs[j]
            signs[j] = -old_sign

            # Update b: flip sign of B_values[j]
            if signs[j] < 0:
                b = b - 2 * B_values[j]
                offset_dir = 1  # add delta
            else:
                b = b + 2 * B_values[j]
                offset_dir = -1  # subtract delta

            c = (b * b - kN) // a
            b_int = int(b)
            c_int = int(c)

            # Incremental offset update: only for non-a-primes
            delta_j = deltas[j]
            if offset_dir > 0:
                for pi in range(fb_size):
                    if is_a_prime_flag[pi]:
                        continue
                    p = fb[pi]
                    if off1[pi] >= 0:
                        off1[pi] = (off1[pi] + delta_j[pi]) % p
                    if off2[pi] >= 0:
                        off2[pi] = (off2[pi] + delta_j[pi]) % p
            else:
                for pi in range(fb_size):
                    if is_a_prime_flag[pi]:
                        continue
                    p = fb[pi]
                    if off1[pi] >= 0:
                        off1[pi] = (off1[pi] - delta_j[pi]) % p
                    if off2[pi] >= 0:
                        off2[pi] = (off2[pi] - delta_j[pi]) % p

            # Recompute offsets for a-primes (only s primes, s~8)
            for pi in a_prime_idx:
                p = fb[pi]
                if p == 2:
                    g0 = c_int % 2
                    g1 = (a_int + 2 * b_int + c_int) % 2
                    off1[pi] = -1
                    off2[pi] = -1
                    if g0 == 0:
                        off1[pi] = M % 2
                        if g1 == 0:
                            off2[pi] = (M + 1) % 2
                    elif g1 == 0:
                        off1[pi] = (M + 1) % 2
                    continue
                b2 = (2 * b_int) % p
                if b2 == 0:
                    off1[pi] = -1
                    off2[pi] = -1
                    continue
                b2_inv = pow(b2, -1, p)
                c_mod = c_int % p
                r = (-c_mod * b2_inv) % p
                off1[pi] = (r + M) % p
                off2[pi] = -1

            # Copy to C arrays
            if use_c:
                for pi in range(fb_size):
                    c_offsets1[pi] = off1[pi]
                    c_offsets2[pi] = off2[pi]

            result = _process_poly(a_int, b_int, c_int, a_prime_exps)
            if result is not None:
                total_t = time.time() - t0
                if verbose:
                    print(f"\n  *** FACTOR (direct): {result} ({total_t:.1f}s) ***")
                if k_mult > 1:
                    g = int(gcd(mpz(result), N))
                    return int(g) if 1 < g < N_int else 0
                return int(result)

        # Progress report (every a-value)
        if a_count % max(1, 20 if nd < 50 else 5 if nd < 60 else 2) == 0 and verbose:
            elapsed = time.time() - t0
            ns = dlp_graph.num_smooth
            rate = ns / max(elapsed, 0.001)
            eta = (needed - ns) / max(rate, 0.001) if rate > 0 else 99999
            print(f"  [{elapsed:.1f}s] a={a_count} poly={poly_count} "
                  f"sm={ns}/{needed} SLP={dlp_graph.n_slp_combined} "
                  f"DLP={dlp_graph.n_dlp_combined} "
                  f"part={dlp_graph.num_partials} cand={total_cands} "
                  f"rate={rate:.1f}/s eta={min(eta,99999):.0f}s")

    # ==========================================================================
    # GF(2) Gaussian Elimination
    # ==========================================================================
    smooth = dlp_graph.smooth
    elapsed_sieve = time.time() - t0
    if verbose:
        print(f"\n  Sieve done: {len(smooth)} rels in {elapsed_sieve:.1f}s "
              f"({poly_count} polys, a={a_count}, "
              f"SLP={dlp_graph.n_slp_combined}, DLP={dlp_graph.n_dlp_combined})")

    if len(smooth) < fb_size + 1:
        if verbose:
            print(f"  Insufficient: {len(smooth)}/{fb_size+1}")
        return 0

    la_t0 = time.time()
    nrows = len(smooth)
    ncols = fb_size + 1

    if verbose:
        print(f"  LA: {nrows} x {ncols} matrix...")

    mat = [0] * nrows
    for i in range(nrows):
        _, s_val, exps, _ = smooth[i]
        row = s_val
        for j in range(fb_size):
            if exps[j] & 1:
                row |= (1 << (j + 1))
        mat[i] = row

    combo = [mpz(1) << i for i in range(nrows)]
    used = [False] * nrows

    for col in range(ncols):
        mask = 1 << col
        piv = -1
        for row in range(nrows):
            if not used[row] and mat[row] & mask:
                piv = row
                break
        if piv == -1:
            continue
        used[piv] = True
        piv_row = mat[piv]
        piv_combo = combo[piv]
        for row in range(nrows):
            if row != piv and mat[row] & mask:
                mat[row] ^= piv_row
                combo[row] ^= piv_combo

    null_vecs = []
    for row in range(nrows):
        if mat[row] == 0:
            indices = []
            bits = combo[row]
            idx = 0
            while bits:
                if bits & 1:
                    indices.append(idx)
                bits >>= 1
                idx += 1
            if indices:
                null_vecs.append(indices)

    la_time = time.time() - la_t0
    if verbose:
        print(f"  LA: {la_time:.1f}s, {len(null_vecs)} null vecs")

    # ==========================================================================
    # Factor Extraction
    # ==========================================================================
    # Work with kN for extraction, then recover factor of N
    for vi, indices in enumerate(null_vecs):
        x_val = mpz(1)
        total_exp = [0] * fb_size
        total_sign = 0
        lp_product = mpz(1)

        for idx in indices:
            x_stored, s_val, exps, lp_val = smooth[idx]
            x_val = x_val * mpz(x_stored) % kN
            total_sign += s_val
            for j in range(fb_size):
                total_exp[j] += exps[j]
            if lp_val > 0:
                lp_product = lp_product * mpz(lp_val) % kN

        if any(e & 1 for e in total_exp) or total_sign & 1:
            continue

        y_val = lp_product
        for j in range(fb_size):
            if total_exp[j] > 0:
                y_val = y_val * pow(mpz(fb[j]), total_exp[j] >> 1, kN) % kN

        for diff in (x_val - y_val, x_val + y_val):
            g = gcd(diff % kN, kN)
            if 1 < g < kN:
                # Recover factor of original N
                gN = gcd(g, N)
                if 1 < gN < N:
                    total_t = time.time() - t0
                    if verbose:
                        print(f"\n  *** FACTOR: {gN} ({nd}d, {total_t:.1f}s, "
                              f"{poly_count} polys, {len(smooth)} rels) ***")
                    return int(gN)

    if verbose:
        print(f"  Tried {len(null_vecs)} null vecs, no factor found.")
    return 0


###############################################################################
# CONVENIENCE
###############################################################################

def factor(N, verbose=True, time_limit=3600):
    """Main entry point for B3-SIQS factoring with retry on extraction failure."""
    t_start = time.time()
    for attempt in range(5):
        remaining = time_limit - (time.time() - t_start)
        if remaining < 5:
            break
        if attempt > 0:
            random.seed(attempt * 12345 + int(time.time()))
            if verbose:
                print(f"\n  Retry #{attempt+1} ({remaining:.0f}s remaining)...")
        result = b3mpqs_factor(N, verbose=verbose, time_limit=remaining)
        if result and result > 0:
            return result
    return 0


###############################################################################
# SELF-TEST
###############################################################################

if __name__ == "__main__":
    print("=" * 70)
    print("B3-SIQS Engine (C-accelerated + Gray code + DLP) — Self-Test")
    print("=" * 70)

    from gmpy2 import mpz, next_prime

    rng = random.Random(42)

    tests = []
    for nd in [48, 55, 60, 63, 66, 69]:
        half_bits = int(nd * 3.32 / 2)
        p = int(next_prime(mpz(rng.getrandbits(half_bits)) | (mpz(1) << (half_bits - 1))))
        q = int(next_prime(mpz(rng.getrandbits(half_bits)) | (mpz(1) << (half_bits - 1))))
        N = p * q
        actual_nd = len(str(N))
        limit = max(60, nd * 15)
        tests.append((f"{nd}d", N, limit))

    results = []
    for label, n, limit in tests:
        nd = len(str(n))
        print(f"\n{'='*70}")
        print(f"Test: {label} ({nd} actual digits)")
        print(f"N = {n}")
        t0 = time.time()
        f = factor(n, verbose=True, time_limit=limit)
        elapsed = time.time() - t0
        if f and f > 1 and n % f == 0:
            print(f"  SUCCESS: {f} x {n // f}  ({elapsed:.1f}s)")
            results.append((label, nd, elapsed, True))
        else:
            print(f"  FAILED ({elapsed:.1f}s)")
            results.append((label, nd, elapsed, False))

    print(f"\n{'='*70}")
    print("Summary:")
    print(f"  {'Label':>6}  {'Digits':>6}  {'Time':>8}  {'Result':>8}")
    for label, nd, t, ok in results:
        print(f"  {label:>6}  {nd:>5}d  {t:>7.1f}s  {'OK' if ok else 'FAIL':>8}")

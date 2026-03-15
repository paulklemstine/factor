#!/usr/bin/env python3
"""
SIQS ENGINE v1.0 — Self-Initializing Quadratic Sieve + GNFS Scaffold
=====================================================================

Upgrade from Guillotine MPQS (resonance_v5.py) with these key wins:

1. Gray Code B-switching: O(FB_size) additions per poly instead of inversions
2. Precomputed offset delta arrays: incremental sieve offset updates
3. Batch polynomial generation: 2^(s-1) polys per 'a' value
4. Double Large Prime variation: graph-based cycle finding for 2-LP relations

Plus GNFS polynomial selection scaffold for future use on 100+ digit numbers.

Critical bug fixes preserved from v5.0:
  - Sieve g(x) = a*x^2 + 2*b*x + c where c = (b^2 - n) / a
  - Partial combining uses v_inv: cax = ax1 * ax2 * pow(v, -1, n) % n
  - T_bits = nb // 4 for sieve threshold
  - Trial divide with gmpy2.f_divmod and early exit when p^2 > v
"""

import gmpy2
from gmpy2 import mpz, isqrt, is_prime, gcd, jacobi, next_prime, legendre
import numpy as np
from numba import njit
import ctypes
import time
import math
import random
import bisect
import os
import multiprocessing
from collections import defaultdict

###############################################################################
# C EXTENSION: Fast Pollard rho for DLP cofactor splitting
###############################################################################

_c_rho_lib = None
_c_rho_fn = None

def _load_c_rho():
    """Load the C Pollard rho shared library (lazy init)."""
    global _c_rho_lib, _c_rho_fn
    if _c_rho_fn is not None:
        return _c_rho_fn
    so_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pollard_rho_c.so')
    if not os.path.exists(so_path):
        return None
    try:
        _c_rho_lib = ctypes.CDLL(so_path)
        _c_rho_lib.pollard_rho_split.argtypes = [ctypes.c_uint64, ctypes.c_int]
        _c_rho_lib.pollard_rho_split.restype = ctypes.c_uint64
        _c_rho_fn = _c_rho_lib.pollard_rho_split
        return _c_rho_fn
    except OSError:
        return None


###############################################################################
# FAST POLLARD RHO for DLP cofactor splitting
###############################################################################

def _pollard_rho_split(n_val, limit=2000):
    """
    Brent's improvement of Pollard rho with batch GCD.
    Split a composite n_val into a non-trivial factor.
    Returns a factor, or None if limit exceeded.
    """
    if n_val <= 1:
        return None
    if n_val % 2 == 0:
        return 2
    # Try a few small c values
    for c in (1, 3, 5, 7):
        y, r, q = 1, 1, 1
        x = y
        g = 1
        iters = 0
        while g == 1 and iters < limit:
            x = y
            for _ in range(r):
                y = (y * y + c) % n_val
                iters += 1
            k = 0
            while k < r and g == 1:
                ys = y
                batch = min(128, r - k)
                q = 1
                for _ in range(batch):
                    y = (y * y + c) % n_val
                    q = q * abs(x - y) % n_val
                    iters += 1
                g = math.gcd(q, n_val)
                k += batch
            r *= 2
        if g == n_val:
            # Backtrack
            while True:
                ys = (ys * ys + c) % n_val
                g = math.gcd(abs(x - ys), n_val)
                if g > 1:
                    break
        if 1 < g < n_val:
            return int(g)
    return None


###############################################################################
# TONELLI-SHANKS: modular square root
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
# NUMBA JIT KERNELS
###############################################################################

@njit(cache=True)
def jit_presieve(sieve_arr, primes, logs, offsets1, offsets2, sz):
    """
    Presieve: build period-210 pattern for primes 2,3,5,7 and tile into array.
    Then sieve remaining small primes (11-31) directly.
    This adds ~4.5 bits of log that were previously skipped, giving more
    accurate sieve values and fewer false positives in trial division.
    """
    # Build period-210 pattern (lcm(2,3,5,7) = 210)
    PERIOD = 210
    pattern = np.zeros(PERIOD, dtype=sieve_arr.dtype)
    for i in range(len(primes)):
        p = primes[i]
        if p > 7:
            break
        lp = logs[i]
        o1 = offsets1[i]
        o2 = offsets2[i]
        if o1 >= 0:
            j = o1 % p
            while j < PERIOD:
                pattern[j] += lp
                j += p
        if o2 >= 0 and o2 != o1:
            j = o2 % p
            while j < PERIOD:
                pattern[j] += lp
                j += p

    # Tile pattern into sieve array
    full_copies = sz // PERIOD
    remainder = sz % PERIOD
    pos = 0
    for _ in range(full_copies):
        for k in range(PERIOD):
            sieve_arr[pos + k] = pattern[k]
        pos += PERIOD
    for k in range(remainder):
        sieve_arr[pos + k] = pattern[k]

    # Sieve primes 11-31 directly (small enough to skip pattern but worth sieving)
    for i in range(len(primes)):
        p = primes[i]
        if p <= 7:
            continue
        if p >= 32:
            break
        lp = logs[i]
        o1 = offsets1[i]
        o2 = offsets2[i]
        if o1 >= 0:
            j = o1
            while j < sz:
                sieve_arr[j] += lp
                j += p
        if o2 >= 0 and o2 != o1:
            j = o2
            while j < sz:
                sieve_arr[j] += lp
                j += p


@njit(cache=True)
def jit_sieve(sieve_arr, primes, logs, offsets1, offsets2, sz):
    """
    Inner sieve loop: add log contributions at arithmetic progressions.
    Only processes primes >= 32 (small primes handled by jit_presieve).
    """
    for i in range(len(primes)):
        p = primes[i]
        if p < 32:
            continue  # Handled by presieve
        lp = logs[i]
        o1 = offsets1[i]
        o2 = offsets2[i]
        if o1 >= 0:
            j = o1
            while j < sz:
                sieve_arr[j] += lp
                j += p
        if o2 >= 0 and o2 != o1:
            j = o2
            while j < sz:
                sieve_arr[j] += lp
                j += p


@njit(cache=True)
def jit_find_smooth(sieve_arr, threshold):
    """Find indices where sieve value meets threshold."""
    count = 0
    for i in range(len(sieve_arr)):
        if sieve_arr[i] >= threshold:
            count += 1
    result = np.empty(count, dtype=np.int64)
    idx = 0
    for i in range(len(sieve_arr)):
        if sieve_arr[i] >= threshold:
            result[idx] = i
            idx += 1
    return result


@njit(cache=True)
def jit_find_hits(sieve_pos, fb, off1, off2, fb_size):
    """
    JIT hit detection for sieve-informed trial division.
    For a candidate at sieve_pos, find which FB primes have a sieve root
    matching this position (i.e., sieve_pos % p == off1[i] or off2[i]).

    Returns array of FB indices that are hits.
    Much faster than numpy per-call dispatch for individual candidates.
    """
    hits = np.empty(fb_size, dtype=np.int32)
    n_hits = 0
    for i in range(fb_size):
        p = fb[i]
        o1 = off1[i]
        if o1 < 0:
            continue
        r = sieve_pos % p
        if r == o1:
            hits[n_hits] = i
            n_hits += 1
        elif off2[i] >= 0 and r == off2[i]:
            hits[n_hits] = i
            n_hits += 1
    return hits[:n_hits]


@njit(cache=True)
def jit_batch_find_hits(candidates, n_cand, fb, off1, off2, fb_size):
    """
    Batch JIT hit detection for ALL candidates in a polynomial at once.
    Eliminates Python→numba transition overhead per candidate.

    Returns flat arrays:
      hit_starts[ci] = index into hit_fb where candidate ci's hits begin
      hit_fb[j] = FB index of j-th hit across all candidates
      hit_count = total number of hits
    """
    # First pass: count hits per candidate to compute offsets
    max_total = n_cand * 80  # ~80 hits per candidate upper bound
    hit_fb = np.empty(max_total, dtype=np.int32)
    hit_starts = np.empty(n_cand + 1, dtype=np.int32)
    total = 0

    for ci in range(n_cand):
        hit_starts[ci] = total
        pos = candidates[ci]
        for i in range(fb_size):
            p = fb[i]
            o1 = off1[i]
            if o1 < 0:
                continue
            r = pos % p
            if r == o1 or (off2[i] >= 0 and r == off2[i]):
                if total < max_total:
                    hit_fb[total] = i
                    total += 1
    hit_starts[n_cand] = total
    return hit_starts, hit_fb[:total]
    # because we need the prime values for modular arithmetic.


###############################################################################
# KNUTH-SCHROEPPEL MULTIPLIER SELECTION
###############################################################################

def _ks_select_multiplier(N, verbose=False):
    """
    Knuth-Schroeppel multiplier selection for QS-family sieves.

    Test squarefree k=1..67, score by how many small primes have
    jacobi(kN, p) = 1 (i.e., kN is a QR mod p), weighted by 2*log(p)/(p-1).
    Penalize large k by -log(k)/2.

    Returns the best multiplier k (int).
    """
    candidates = [1, 2, 3, 5, 6, 7, 10, 11, 13, 14, 15, 17, 19, 21,
                  23, 26, 29, 30, 31, 33, 34, 37, 38, 41, 42, 43,
                  46, 47, 51, 53, 55, 57, 58, 59, 61, 62, 65, 66, 67]
    scored = []
    for k in candidates:
        kN = N * k
        sq = isqrt(kN)
        if sq * sq == kN:
            continue  # kN is a perfect square — useless
        score = -math.log(k) / 2.0 if k > 1 else 0.0

        # Special handling for p=2 based on kN mod 8
        kN_mod8 = int(kN % 8)
        if kN_mod8 == 1:
            score += 2.0 * math.log(2.0)
        elif kN_mod8 == 5:
            score += math.log(2.0)
        elif kN_mod8 == 0:
            score += math.log(2.0) * 0.5

        # Score over first 80 odd primes
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
# SIQS PARAMETER TABLE
###############################################################################

def siqs_params(nd):
    """
    Parameter selection for SIQS. Slightly more aggressive than MPQS
    because Gray code switching generates polynomials faster.
    """
    tbl = [
        # (digits, FB_size, sieve_half_width_M)
        # Tuned to match/exceed v5 MPQS performance.
        # M values slightly larger than MPQS since SIQS poly switching is cheaper.
        # FB_size tuned: smaller FB = fewer relations needed + faster LA,
        # but lower smoothness probability per candidate.
        (20,    80,    20000),
        (25,   150,    40000),
        (30,   250,    80000),
        (35,   450,   150000),
        (40,   800,   300000),
        (45,  1200,   500000),
        (50,  2500,  1000000),
        (55,  3500,  1200000),
        (60,  4500,  1500000),
        (65,  5500,  2000000),
        (70,  6500,  3000000),
        (75,  9000,  7000000),
        (80, 16000, 12000000),
        (85, 28000, 16000000),
        (90, 40000, 22000000),
        (95, 55000, 28000000),
        (100, 75000, 35000000),
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
# GRAY CODE UTILITIES
###############################################################################

def gray_code_sequence(num_bits):
    """
    Generate the Gray code sequence for num_bits bits.
    Returns list of (gray_value, bit_that_flipped) pairs.

    Gray code property: consecutive values differ by exactly one bit.
    This means when iterating polynomials, we only flip one B_value sign
    at a time, enabling incremental offset updates.

    For s factor-base primes in 'a', we have s B_values and 2^(s-1)
    sign combinations (fixing first sign positive to avoid duplicates).
    The bit_that_flipped tells us which B_value's sign to flip.
    """
    seq = []
    prev = 0
    for i in range(1, 1 << num_bits):
        gray = i ^ (i >> 1)
        changed_bit = (prev ^ gray)
        # Find which bit changed
        bit_pos = 0
        while (changed_bit >> bit_pos) & 1 == 0:
            bit_pos += 1
        # Direction: +1 if bit went 0->1, -1 if 1->0
        direction = 1 if (gray >> bit_pos) & 1 else -1
        seq.append((gray, bit_pos, direction))
        prev = gray
    return seq


def _quick_factor(n, limit=50):
    """Quick split of cofactor into two primes. Returns a factor or None."""
    if n < 4:
        return None
    # Quick trial division by small primes (catches ~30% of cases in <1µs)
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53):
        if n % p == 0:
            return p
    # Use C Pollard rho if available (10-50x faster than Python)
    c_rho = _load_c_rho()
    if c_rho is not None and n < (1 << 64):
        f = c_rho(n, limit * 4)  # C is faster, can afford more iters
        if f > 1:
            return int(f)
        return None
    # Python fallback: Pollard rho with reduced iteration limit
    x, y, c, d = 2, 2, 1, 1
    while d == 1 and limit > 0:
        x = (x * x + c) % n
        y = (y * y + c) % n
        y = (y * y + c) % n
        d = math.gcd(abs(x - y), n)
        limit -= 1
    if 1 < d < n:
        return int(d)
    return None


###############################################################################
# DOUBLE LARGE PRIME GRAPH
###############################################################################

class DoubleLargePrimeGraph:
    """
    Manages relations with up to 2 large prime cofactors.

    Single large prime (SLP): cofactor is one prime < lp_bound
        Stored in partials dict; two SLPs with same large prime combine.

    Double large prime (DLP): cofactor is product of two primes, each < lp_bound
        Stored in a graph where vertices = large primes, edges = relations.
        A cycle in this graph yields a full relation (the product of relations
        around the cycle cancels all large primes).

    The DLP variation typically yields 2-3x more relations for the same
    sieve effort, which is critical for 60+ digit numbers.
    """

    def __init__(self, n, fb_size, lp_bound):
        self.n = n
        self.fb_size = fb_size
        self.lp_bound = lp_bound

        # Single large prime partials: lp -> (x, sign, exps)
        self.slp_partials = {}

        # Double large prime graph: adjacency list
        # Key: large prime, Value: list of (other_lp, x, sign, exps)
        self.dlp_graph = defaultdict(list)
        self.dlp_count = 0

        # Union-Find for O(α(n)) cycle detection
        self._uf_parent = {}
        self._uf_rank = {}

        # Full relations (smooth + combined)
        self.smooth = []
        # GF(2) signature dedup: track unique exponent vector signatures
        self._gf2_sigs = set()
        self.num_dupes = 0

    def _gf2_sig(self, sign, exps):
        """Compute GF(2) signature of a relation's exponent vector."""
        return (sign % 2,) + tuple(e % 2 for e in exps)

    def _uf_find(self, x):
        """Find with path compression."""
        if x not in self._uf_parent:
            self._uf_parent[x] = x
            self._uf_rank[x] = 0
            return x
        root = x
        while self._uf_parent[root] != root:
            root = self._uf_parent[root]
        # Path compression
        while self._uf_parent[x] != root:
            self._uf_parent[x], x = root, self._uf_parent[x]
        return root

    def _uf_union(self, a, b):
        """Union by rank."""
        ra, rb = self._uf_find(a), self._uf_find(b)
        if ra == rb:
            return  # Already same component
        if self._uf_rank[ra] < self._uf_rank[rb]:
            ra, rb = rb, ra
        self._uf_parent[rb] = ra
        if self._uf_rank[ra] == self._uf_rank[rb]:
            self._uf_rank[ra] += 1

    def add_smooth(self, x, sign, exps):
        """Add a fully smooth relation (dedup by GF(2) signature)."""
        sig = self._gf2_sig(sign, exps)
        if sig in self._gf2_sigs:
            self.num_dupes += 1
            return  # skip duplicate
        self._gf2_sigs.add(sig)
        self.smooth.append((x, sign, exps))

    def add_single_lp(self, x, sign, exps, lp):
        """
        Add a relation with one large prime cofactor.
        If we already have a partial with the same lp, combine them.

        Combining: if Q1 = prod(fb^e1) * v and Q2 = prod(fb^e2) * v, then
        Q1*Q2/v^2 = prod(fb^(e1+e2)) is fully smooth.
        On the x side: x_combined = x1 * x2 * v^(-1) mod n.
        """
        lp = int(lp)
        if lp in self.slp_partials:
            ox, os, oe = self.slp_partials[lp]
            try:
                v_inv = pow(lp, -1, int(self.n))
            except (ValueError, ZeroDivisionError):
                g = gcd(mpz(lp), self.n)
                if 1 < g < self.n:
                    return int(g)
                return None
            # Critical bug fix from v5.0: use v_inv in combining
            cax = ox * x * v_inv % int(self.n)
            cs = (os + sign) % 2
            ce = [oe[j] + exps[j] for j in range(self.fb_size)]
            sig = self._gf2_sig(cs, ce)
            if sig not in self._gf2_sigs:
                self._gf2_sigs.add(sig)
                self.smooth.append((cax, cs, ce))
            else:
                self.num_dupes += 1
        else:
            self.slp_partials[lp] = (x, sign, exps)
        return None

    def add_double_lp(self, x, sign, exps, lp1, lp2):
        """
        Add a relation with two large prime cofactors.

        Store as an edge in the large prime graph: vertex lp1 -- vertex lp2.
        When a cycle forms, the product of relations around the cycle
        cancels all large primes, yielding a full relation.

        For efficiency, we do simple cycle detection: when adding edge (lp1, lp2),
        check if lp1 and lp2 are already connected via BFS/DFS. If so, extract
        the path and combine all relations along it.
        """
        lp1, lp2 = int(min(lp1, lp2)), int(max(lp1, lp2))
        self.dlp_count += 1

        # Check for immediate cycle: if lp1 == lp2, this is effectively SLP
        if lp1 == lp2:
            return self.add_single_lp(x, sign, exps, lp1)

        # Cap DLP graph to prevent memory explosion
        # Each edge stores sparse exps (~20 entries vs fb_size=5000+)
        if self.dlp_count > 20000:
            return None

        # Sparse exps: only store non-zero entries as tuple of (idx, val) pairs
        sparse = tuple((j, e) for j, e in enumerate(exps) if e != 0)

        # Union-Find: O(α(n)) check if lp1 and lp2 are already connected
        if self._uf_find(lp1) == self._uf_find(lp2):
            # Cycle exists! Use BFS to find the path (only runs when cycle found)
            path = self._find_path(lp1, lp2, max_depth=5)
            if path is not None:
                result = self._combine_cycle(path, x, sign, sparse, lp1, lp2)
                if result is not None:
                    return result

        # Store edge with sparse exps and union the components
        self.dlp_graph[lp1].append((lp2, x, sign, sparse))
        self.dlp_graph[lp2].append((lp1, x, sign, sparse))
        self._uf_union(lp1, lp2)
        return None

    def _find_path(self, start, end, max_depth=10):
        """BFS to find path from start to end in the large prime graph."""
        if start not in self.dlp_graph or end not in self.dlp_graph:
            return None

        visited = {start: None}  # node -> parent
        queue = [start]
        depth = {start: 0}

        while queue:
            node = queue.pop(0)
            if depth[node] >= max_depth:
                continue
            for neighbor, x, sign, exps in self.dlp_graph[node]:
                if neighbor == end:
                    # Found it — reconstruct path
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

    def _sparse_to_dense(self, sparse, size):
        """Convert sparse exps tuple ((idx,val),...) to dense list."""
        dense = [0] * size
        for idx, val in sparse:
            dense[idx] = val
        return dense

    def _add_sparse(self, combined, sparse):
        """Add sparse exps into combined dense list in-place."""
        for idx, val in sparse:
            combined[idx] += val

    def _combine_cycle(self, path, new_x, new_sign, new_sparse, lp1, lp2):
        """
        Combine relations along a cycle to produce a full relation.
        Exps stored as sparse tuples; converted to dense only here.
        """
        combined_x = new_x
        combined_sign = new_sign
        combined_exps = self._sparse_to_dense(new_sparse, self.fb_size)

        lp_counts = defaultdict(int)
        lp_counts[lp1] += 1
        lp_counts[lp2] += 1

        for src, dst in path:
            edge_found = False
            for neighbor, x, sign, sparse in self.dlp_graph[src]:
                if neighbor == dst:
                    combined_x = combined_x * x % int(self.n)
                    combined_sign = (combined_sign + sign) % 2
                    self._add_sparse(combined_exps, sparse)
                    lp_counts[src] += 1
                    lp_counts[dst] += 1
                    edge_found = True
                    break
            if not edge_found:
                return None

        for lp, count in lp_counts.items():
            pairs = count // 2
            for _ in range(pairs):
                try:
                    lp_inv = pow(int(lp), -1, int(self.n))
                    combined_x = combined_x * lp_inv % int(self.n)
                except (ValueError, ZeroDivisionError):
                    g = gcd(mpz(lp), self.n)
                    if 1 < g < self.n:
                        return int(g)
                    return None

        sig = self._gf2_sig(combined_sign, combined_exps)
        if sig not in self._gf2_sigs:
            self._gf2_sigs.add(sig)
            self.smooth.append((combined_x, combined_sign, combined_exps))
        else:
            self.num_dupes += 1
        return None

    @property
    def num_smooth(self):
        return len(self.smooth)

    @property
    def num_partials(self):
        return len(self.slp_partials)


###############################################################################
# MULTIPROCESSING WORKER FOR SIQS SIEVE
###############################################################################

# Relation types returned by workers
_REL_SMOOTH = 0
_REL_SINGLE_LP = 1
_REL_DOUBLE_LP = 2
_REL_DIRECT_FACTOR = 3


def _sieve_one_a(args):
    """
    Top-level worker function for multiprocessing: sieve all polynomials
    for one 'a' value and return raw relations.

    Must be top-level (not nested) for pickling.

    Args: single tuple (unpacked inside) containing all data needed.
    Returns: list of (rel_type, data) tuples.
    """
    (n_int, fb, fb_np_list, fb_log_list, fb_size, M, sz,
     sqrt_n_mod_list, T_bits, nb, lp_bound,
     s, gray_seq_data, select_lo, select_hi, log_target,
     small_prime_correction, seed, base_indices) = args

    # Reconstruct numpy arrays (can't pickle numpy arrays reliably across processes)
    fb_np = np.array(fb_np_list, dtype=np.int64)
    fb_log = np.array(fb_log_list, dtype=np.int16)
    sqrt_n_mod = dict(sqrt_n_mod_list)

    n = mpz(n_int)
    rng = random.Random(seed)

    fb_index = {p: i for i, p in enumerate(fb)}

    # Select 'a' as product of s FB primes near target
    best_a = None
    best_diff = float('inf')

    if base_indices is not None and len(base_indices) < s:
        # GROUPED mode: base of n_shared primes is fixed, pick remaining randomly
        base_set = set(base_indices)
        base_product = mpz(1)
        for i in base_indices:
            base_product *= fb[i]
        n_extra = s - len(base_indices)  # how many more primes to pick
        for _ in range(20):
            # Pick n_extra more primes not in the base
            extras = []
            extra_set = set(base_set)
            for _e in range(n_extra):
                for _try in range(10):
                    idx = rng.randint(select_lo, select_hi - 1)
                    if idx not in extra_set:
                        extras.append(idx)
                        extra_set.add(idx)
                        break
            if len(extras) < n_extra:
                continue
            indices = sorted(list(base_indices) + extras)
            a = base_product
            for idx in extras:
                a *= fb[idx]
            diff = abs(float(gmpy2.log2(a)) - log_target) if a > 0 else float('inf')
            if diff < best_diff:
                best_diff = diff
                best_a = a
                best_primes = [fb[i] for i in indices]
    else:
        # RANDOM mode: fully random a-selection (original behavior)
        for _ in range(20):
            try:
                indices = sorted(rng.sample(range(select_lo, select_hi), s))
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
        return []

    a = best_a
    a_primes = best_primes
    a_prime_idx = [fb_index[ap] for ap in a_primes]
    a_prime_set = set(a_primes)
    a_int = int(a)

    # Compute t_roots: sqrt(n) mod q_j for each q_j in a
    t_roots = []
    for q in a_primes:
        t = sqrt_n_mod.get(q)
        if t is None:
            return []
        t_roots.append(t)

    # Compute B_values for Gray code switching
    B_values = []
    for j in range(s):
        q = a_primes[j]
        A_j = a // q
        try:
            A_j_inv = pow(int(A_j % q), -1, q)
        except (ValueError, ZeroDivisionError):
            return []
        B_j = mpz(t_roots[j]) * A_j * mpz(A_j_inv) % a
        B_values.append(B_j)

    # Precompute a_inv mod p for each FB prime
    a_inv_mod = np.zeros(fb_size, dtype=np.int64)
    is_a_prime = np.zeros(fb_size, dtype=np.bool_)
    for pi in range(fb_size):
        p = fb[pi]
        if p in a_prime_set:
            a_inv_mod[pi] = 0
            is_a_prime[pi] = True
        else:
            try:
                a_inv_mod[pi] = pow(a_int % p, -1, p)
            except (ValueError, ZeroDivisionError):
                a_inv_mod[pi] = 0

    regular_idx = np.where(~is_a_prime)[0]

    # Precompute delta arrays for Gray code switching
    deltas = []
    for j in range(s):
        d = np.zeros(fb_size, dtype=np.int64)
        B_j_2 = 2 * B_values[j]
        for pi in range(fb_size):
            p = fb[pi]
            if p in a_prime_set:
                d[pi] = 0
            else:
                d[pi] = int(B_j_2 % p) * a_inv_mod[pi] % p
        deltas.append(d)

    # First polynomial: all signs positive
    b = mpz(0)
    for B_j in B_values:
        b += B_j
    if (b * b - n) % a != 0:
        b = -b
        if (b * b - n) % a != 0:
            return []

    c = (b * b - n) // a
    b_int = int(b)

    # Compute initial sieve offsets
    o1 = np.full(fb_size, -1, dtype=np.int64)
    o2 = np.full(fb_size, -1, dtype=np.int64)

    for pi in range(fb_size):
        p = fb[pi]
        if p == 2:
            g0 = int(c % 2)
            g1 = int((a_int + 2 * b_int + int(c)) % 2)
            if g0 == 0:
                o1[pi] = M % 2
                if g1 == 0:
                    o2[pi] = (M + 1) % 2
            elif g1 == 0:
                o1[pi] = (M + 1) % 2
            continue
        if p in a_prime_set:
            b2 = (2 * b_int) % p
            if b2 == 0:
                continue
            b2_inv = pow(b2, -1, p)
            c_mod = int(c % p)
            r = (-c_mod * b2_inv) % p
            o1[pi] = (r + M) % p
            continue
        t = sqrt_n_mod.get(p)
        if t is None:
            continue
        ai = int(a_inv_mod[pi])
        bm = b_int % p
        r1 = (ai * (t - bm)) % p
        r2 = (ai * (p - t - bm)) % p
        o1[pi] = (r1 + M) % p
        o2[pi] = ((r2 + M) % p) if r2 != r1 else -1

    # Collect relations from all polynomials for this 'a'
    relations = []
    _sieve_buf = np.zeros(sz, dtype=np.int16)

    def _worker_sieve_poly(b_val, c_val, off1, off2):
        """Sieve one polynomial, collect raw relations."""
        b_v = int(b_val)
        c_v = int(c_val)

        _sieve_buf[:] = 0
        jit_sieve(_sieve_buf, fb_np, fb_log, off1, off2, sz)

        log_g_max = math.log2(max(M, 1)) + 0.5 * nb
        thresh = int(max(0, (log_g_max - T_bits)) * 64)

        candidates = jit_find_smooth(_sieve_buf, thresh)
        n_cand = len(candidates)
        if n_cand == 0:
            return

        hit_starts, hit_fb = jit_batch_find_hits(
            candidates, n_cand, fb_np, off1, off2, fb_size)

        for ci in range(n_cand):
            sieve_pos = int(candidates[ci])
            x = sieve_pos - M
            ax_b = int(a * x + b_val)
            gx = a_int * x * x + 2 * b_v * x + c_v

            if gx == 0:
                g = gcd(mpz(ax_b), n)
                if 1 < g < n:
                    relations.append((_REL_DIRECT_FACTOR, int(g)))
                continue

            sign = 1 if gx < 0 else 0
            v = abs(gx)
            exps = [0] * fb_size

            h_start = hit_starts[ci]
            h_end = hit_starts[ci + 1]
            for h in range(h_start, h_end):
                idx = hit_fb[h]
                p = fb[idx]
                if v == 1:
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
                    exps[idx] = e

            for idx in a_prime_idx:
                exps[idx] += 1
            x_stored = int(mpz(ax_b) % n)

            # Use sparse exps to reduce pickle size (~100x smaller)
            sparse_exps = tuple((j, e) for j, e in enumerate(exps) if e != 0)

            if v == 1:
                relations.append((_REL_SMOOTH, (x_stored, sign, sparse_exps)))
            elif v < lp_bound and is_prime(v):
                relations.append((_REL_SINGLE_LP, (x_stored, sign, sparse_exps, int(v))))
            elif v < lp_bound * lp_bound and v > 1:
                sq = gmpy2.isqrt(mpz(v))
                if sq * sq == v and is_prime(sq):
                    lp1 = lp2 = int(sq)
                else:
                    lp1 = _quick_factor(v)
                    if lp1 and lp1 > 1 and v // lp1 > 1:
                        lp2 = v // lp1
                    else:
                        continue
                if lp1 < lp_bound and lp2 < lp_bound and is_prime(mpz(lp1)) and is_prime(mpz(lp2)):
                    relations.append((_REL_DOUBLE_LP, (x_stored, sign, sparse_exps, lp1, lp2)))

    # Sieve first polynomial
    _worker_sieve_poly(b, c, o1, o2)

    # Gray code B-switching for remaining polynomials
    signs = [1] * s
    for gray_val, flip_bit, flip_dir in gray_seq_data:
        j = flip_bit + 1
        if j >= s:
            continue
        old_sign = signs[j]
        signs[j] = -old_sign

        if signs[j] < 0:
            b = b - 2 * B_values[j]
            offset_dir = 1
        else:
            b = b + 2 * B_values[j]
            offset_dir = -1

        c = (b * b - n) // a
        b_int = int(b)

        delta_j = deltas[j]
        ri = regular_idx
        valid1 = o1[ri] >= 0
        ri_v1 = ri[valid1]
        valid2 = o2[ri] >= 0
        ri_v2 = ri[valid2]

        if offset_dir > 0:
            o1[ri_v1] = (o1[ri_v1] + delta_j[ri_v1]) % fb_np[ri_v1]
            o2[ri_v2] = (o2[ri_v2] + delta_j[ri_v2]) % fb_np[ri_v2]
        else:
            o1[ri_v1] = (o1[ri_v1] - delta_j[ri_v1]) % fb_np[ri_v1]
            o2[ri_v2] = (o2[ri_v2] - delta_j[ri_v2]) % fb_np[ri_v2]

        for pi in a_prime_idx:
            p = fb[pi]
            if p == 2:
                g0 = int(c % 2)
                g1 = int((a_int + 2 * b_int + int(c)) % 2)
                o1[pi] = -1
                o2[pi] = -1
                if g0 == 0:
                    o1[pi] = M % 2
                    if g1 == 0:
                        o2[pi] = (M + 1) % 2
                elif g1 == 0:
                    o1[pi] = (M + 1) % 2
                continue
            b2 = (2 * b_int) % p
            if b2 == 0:
                o1[pi] = -1
                o2[pi] = -1
                continue
            b2_inv = pow(b2, -1, p)
            c_mod = int(c % p)
            r = (-c_mod * b2_inv) % p
            o1[pi] = (r + M) % p
            o2[pi] = -1

        _worker_sieve_poly(b, c, o1, o2)

    return relations


###############################################################################
# SIQS CORE
###############################################################################


def _fallback_gauss(sparse_rows, ncols, nrows):
    """Fallback mpz-based GF(2) Gauss when block_lanczos not available."""
    mat = [0] * nrows
    for i, cols in enumerate(sparse_rows):
        for c in cols:
            mat[i] |= (1 << c)
    combo = [mpz(1) << i for i in range(nrows)]
    used = [False] * nrows
    for col in range(ncols):
        mask = 1 << col
        piv = -1
        for row in range(nrows):
            if not used[row] and mat[row] & mask:
                piv = row; break
        if piv == -1: continue
        used[piv] = True
        for row in range(nrows):
            if row != piv and mat[row] & mask:
                mat[row] ^= mat[piv]; combo[row] ^= combo[piv]
    vecs = []
    for row in range(nrows):
        if mat[row] == 0:
            indices = []; bits = combo[row]; idx = 0
            while bits:
                if bits & 1: indices.append(idx)
                bits >>= 1; idx += 1
            if indices: vecs.append(indices)
    return vecs


def siqs_factor(n, verbose=True, time_limit=3600, multiplier=1, n_workers=1, grouped_a=True):
    """
    Self-Initializing Quadratic Sieve (SIQS).

    Core relation: (a*x + b)^2 = a * g(x) (mod n)
    where g(x) = a*x^2 + 2*b*x + c, c = (b^2 - n) / a

    Key improvements over MPQS:
    1. Gray code enumeration of b-values for O(1) poly switching
    2. Precomputed offset deltas for incremental sieve updates
    3. Double large prime variation for ~2x more relations
    4. Batch generation of 2^(s-1) polynomials per 'a' value

    Args:
        multiplier: Knuth-Schroeppel multiplier.
            1 = no multiplier (default, backward compatible)
            'auto' = auto-select optimal multiplier via K-S scoring
            int > 1 = use that specific multiplier
        n_workers: Number of parallel sieve workers (default=1, single-threaded).
            Use 2 for ~1.7x speedup on multi-core systems.
            Each worker needs ~3MB RAM (sieve array + FB copy).

    Returns a non-trivial factor of n, or None if time_limit exceeded.
    """
    n = mpz(n)
    nd = len(str(n))
    nb = int(gmpy2.log2(n)) + 1

    # Quick checks
    if n <= 1:
        return None
    if n % 2 == 0:
        return 2
    if is_prime(n):
        return int(n)
    sr = isqrt(n)
    if sr * sr == n:
        return int(sr)

    # Knuth-Schroeppel multiplier selection
    original_n = n  # preserve for factor extraction
    if multiplier == 'auto':
        k = _ks_select_multiplier(n, verbose=verbose)
    else:
        k = int(multiplier)

    # Parameters based on ORIGINAL n size (multiplier doesn't change difficulty)
    fb_size, M = siqs_params(nd)

    if k > 1:
        n = mpz(k) * n  # sieve with kN
        # Update bit-size for sieve threshold math (kN is the sieve target)
        nb = int(gmpy2.log2(n)) + 1

    if verbose:
        k_str = f", k={k}" if k > 1 else ""
        print(f"  SIQS: {len(str(original_n))}d ({int(gmpy2.log2(original_n))+1}b){k_str}, FB={fb_size}, M={M}")

    def _extract_factor(g):
        """Extract a non-trivial factor of original_n from a factor of kN."""
        g = gcd(mpz(g), original_n)
        if 1 < g < original_n:
            return int(g)
        return None

    t0 = time.time()

    # ======================================================================
    # Stage 1: Build Factor Base
    # ======================================================================
    # FB = {p prime : Legendre(n, p) = 1} union {2}
    # These are the primes for which n is a quadratic residue mod p,
    # meaning we can find sqrt(n) mod p and thus sieve positions.
    fb = []
    p = 2
    while len(fb) < fb_size:
        if p == 2 or (is_prime(p) and jacobi(int(n % p), p) == 1):
            fb.append(int(p))
        p = int(next_prime(p)) if p > 2 else 3

    fb_np = np.array(fb, dtype=np.int64)
    # Scale factor 64 (not 1024): halves sieve array to int16, fits L2 cache better
    fb_log = np.array([int(round(math.log2(p) * 64)) for p in fb], dtype=np.int16)
    fb_index = {p: i for i, p in enumerate(fb)}

    # Expected sieve contribution from small primes skipped in jit_sieve.
    # Presieve handles primes 2-31 directly, threshold adjusted accordingly.
    small_prime_correction = 0

    if verbose:
        print(f"    FB[{fb[0]}..{fb[-1]}] built ({time.time()-t0:.1f}s)")

    # Precompute sqrt(n) mod p for each FB prime (Tonelli-Shanks)
    sqrt_n_mod = {}
    for p in fb:
        if p == 2:
            sqrt_n_mod[2] = int(n % 2)
        else:
            sqrt_n_mod[p] = tonelli_shanks(int(n % p), p)

    sqrt_n = isqrt(n)
    if sqrt_n * sqrt_n < n:
        sqrt_n += 1

    # ======================================================================
    # Stage 2: Relation Collection with SIQS
    # ======================================================================

    # Large prime bound: min(B*100, B^2) — B^2 gives LP space too large for DLP combining
    lp_bound = min(fb[-1] * 100, fb[-1] ** 2)

    # T_bits controls sieve threshold: thresh = (log_g_max - T_bits) * 64.
    # Higher T_bits = lower threshold = more candidates (looser).
    # For 54d+, slightly looser works because sieve is the bottleneck.
    if nb >= 180:
        T_bits = max(15, nb // 4 - 1)
    else:
        T_bits = max(15, nb // 4 - 2)
    needed = fb_size + 30

    dlp_graph = DoubleLargePrimeGraph(n, fb_size, lp_bound)

    if verbose:
        print(f"    Need {needed} rels, T_bits={T_bits}, LP_bound={int(math.log10(lp_bound)):.0f}d")

    # JIT warmup
    dummy = np.zeros(100, dtype=np.int32)
    jit_sieve(dummy, np.array([2, 3], dtype=np.int64),
              np.array([10, 15], dtype=np.int32),
              np.array([0, 0], dtype=np.int64),
              np.array([1, 1], dtype=np.int64), 100)
    jit_find_smooth(dummy, 1)

    poly_count = 0
    total_cands = 0
    a_count = 0

    def trial_divide(val):
        """
        Trial divide val over FB using gmpy2 for speed.
        Critical v5.0 fix: use gmpy2.f_divmod and early exit when p^2 > v.
        """
        v = mpz(abs(val))
        exps = [0] * fb_size
        for i in range(fb_size):
            p = fb[i]
            if v == 1:
                break
            if p * p > v:
                break
            q, r = gmpy2.f_divmod(v, p)
            if r == 0:
                e = 1
                v = q
                q, r = gmpy2.f_divmod(v, p)
                while r == 0:
                    e += 1
                    v = q
                    q, r = gmpy2.f_divmod(v, p)
                exps[i] = e
        return exps, int(v)

    # JIT warmup for hit detection
    _warmup_fb = np.array([2, 3], dtype=np.int64)
    _warmup_o = np.array([0, 1], dtype=np.int64)
    jit_find_hits(0, _warmup_fb, _warmup_o, _warmup_o, 2)

    def trial_divide_smart(val, sieve_pos, off1, off2):
        """
        Sieve-informed trial division: only check primes whose sieve root
        matches the candidate position. Uses numba JIT for hit detection
        (avoids numpy per-call dispatch overhead), then gmpy2 only on hits.
        """
        v = mpz(abs(val))
        exps = [0] * fb_size

        # JIT hit detection (numba loop, no numpy dispatch overhead)
        hits = jit_find_hits(sieve_pos, fb_np, off1, off2, fb_size)

        for i in range(len(hits)):
            idx = hits[i]
            p = fb[idx]
            if v == 1:
                break
            q, r = gmpy2.f_divmod(v, p)
            if r == 0:
                e = 1
                v = q
                q, r = gmpy2.f_divmod(v, p)
                while r == 0:
                    e += 1
                    v = q
                    q, r = gmpy2.f_divmod(v, p)
                exps[idx] = e

        return exps, int(v)

    def process_candidate_batch(ax_b_val, gx_val, a_prime_indices,
                                hit_fb_arr, h_start, h_end):
        """
        Process a candidate using precomputed hit indices from batch JIT.
        Uses native Python int division (faster than gmpy2 for values < 2^128).
        """
        if gx_val == 0:
            g = gcd(mpz(ax_b_val), n)
            if 1 < g < n:
                return int(g)
            return None

        sign = 1 if gx_val < 0 else 0
        v = abs(gx_val)  # Native Python int — avoid mpz overhead
        exps = [0] * fb_size

        # Trial divide using precomputed hit indices (native int divmod)
        for h in range(h_start, h_end):
            idx = hit_fb_arr[h]
            p = fb[idx]
            if v == 1:
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
                exps[idx] = e

        if v == 1:
            # Smooth relation
            for idx in a_prime_indices:
                exps[idx] += 1
            x_stored = int(mpz(ax_b_val) % n)
            dlp_graph.add_smooth(x_stored, sign, exps)
        elif v < lp_bound and is_prime(v):
            # Single large prime relation
            for idx in a_prime_indices:
                exps[idx] += 1
            x_stored = int(mpz(ax_b_val) % n)
            result = dlp_graph.add_single_lp(x_stored, sign, exps, int(v))
            if result:
                return result
        # DLP: try to split cofactor into two large primes
        elif v < lp_bound * lp_bound and v > 1:
            # Quick divisibility check by small primes first
            sq = gmpy2.isqrt(mpz(v))
            if sq * sq == v and is_prime(sq):
                lp1 = lp2 = int(sq)
            else:
                # Try Pollard rho for quick split (limit iterations)
                lp1 = _quick_factor(v)
                if lp1 and lp1 > 1 and v // lp1 > 1:
                    lp2 = v // lp1
                else:
                    return None
            if lp1 < lp_bound and lp2 < lp_bound and is_prime(mpz(lp1)) and is_prime(mpz(lp2)):
                for idx in a_prime_indices:
                    exps[idx] += 1
                x_stored = int(mpz(ax_b_val) % n)
                result = dlp_graph.add_double_lp(x_stored, sign, exps, lp1, lp2)
                if result:
                    return result
        return None

    def process_candidate(ax_b_val, gx_val, a_prime_indices,
                          sieve_pos=None, off1=None, off2=None):
        """
        Process a sieve candidate: trial divide g(x), classify relation.

        Relation: (a*x + b)^2 = a * g(x) (mod n)
        We factor a * g(x) over FB. The 'a' contribution is known (a_prime_indices),
        so we only trial-divide g(x).

        If sieve_pos/off1/off2 are provided, uses sieve-informed smart trial
        division (only checks primes whose sieve root matches the position).
        """
        if gx_val == 0:
            g = gcd(mpz(ax_b_val), n)
            if 1 < g < n:
                return int(g)
            return None

        sign = 1 if gx_val < 0 else 0
        if sieve_pos is not None and off1 is not None and off2 is not None:
            exps, remainder = trial_divide_smart(gx_val, sieve_pos, off1, off2)
        else:
            exps, remainder = trial_divide(gx_val)

        # Add a's prime contributions to the exponent vector
        for idx in a_prime_indices:
            exps[idx] += 1

        x_stored = int(mpz(ax_b_val) % n)

        if remainder == 1:
            # Fully smooth
            dlp_graph.add_smooth(x_stored, sign, exps)
        elif remainder < lp_bound and gmpy2.is_prime(remainder):
            # Single large prime
            result = dlp_graph.add_single_lp(x_stored, sign, exps, remainder)
            if result:
                return result
        # DLP: try to split remainder into two large primes
        elif remainder < lp_bound * lp_bound and remainder > 1:
            sq = gmpy2.isqrt(mpz(remainder))
            if sq * sq == remainder and gmpy2.is_prime(sq):
                lp1 = lp2 = int(sq)
            else:
                lp1 = _quick_factor(remainder)
                if lp1 and lp1 > 1 and remainder // lp1 > 1:
                    lp2 = remainder // lp1
                else:
                    return None
            if lp1 < lp_bound and lp2 < lp_bound and gmpy2.is_prime(mpz(lp1)) and gmpy2.is_prime(mpz(lp2)):
                result = dlp_graph.add_double_lp(x_stored, sign, exps, lp1, lp2)
                if result:
                    return result
        return None

    def _quick_split(n_val):
        """Split a small composite into two factors via trial division.
        Much faster than Pollard rho for DLP cofactors (typically < 16 digits)."""
        if n_val % 2 == 0:
            return 2
        # Trial divide by odd numbers up to min(sqrt(n_val), 50000)
        limit = min(int(n_val**0.5) + 1, 50000)
        for d in range(3, limit, 2):
            if n_val % d == 0:
                return d
        return None

    def _pollard_rho_quick(n_val, limit=1000):
        """Quick Pollard rho for splitting DLP cofactors."""
        if n_val % 2 == 0:
            return 2
        x = mpz(2)
        y = mpz(2)
        d = mpz(1)
        c = mpz(1)
        for _ in range(limit):
            x = (x * x + c) % n_val
            y = (y * y + c) % n_val
            y = (y * y + c) % n_val
            d = gcd(abs(x - y), n_val)
            if d != 1 and d != n_val:
                return int(d)
        return None

    # ------------------------------------------------------------------
    # SIQS Polynomial Generation with Gray Code B-switching
    # ------------------------------------------------------------------
    # For each 'a' value (product of s FB primes), we generate 2^(s-1)
    # polynomials by varying the signs of the B_values in b = sum(+/- B_j).
    #
    # Gray code ensures consecutive polynomials differ by exactly one
    # sign flip, so sieve offsets can be updated incrementally.
    #
    # Mathematical setup:
    #   a = q_1 * q_2 * ... * q_s  (product of s FB primes)
    #   For each q_j, compute t_j = sqrt(n) mod q_j
    #   B_j = t_j * (a/q_j) * (a/q_j)^(-1) mod q_j
    #   b = sum(+/- B_j) mod a  (2^(s-1) choices, fixing first sign)
    #   c = (b^2 - n) / a  (exact integer division)
    #
    #   Sieve roots for prime p (not dividing a):
    #     r1 = a^(-1) * (sqrt_n_mod_p - b) mod p
    #     r2 = a^(-1) * (-sqrt_n_mod_p - b) mod p
    #
    #   When flipping sign of B_j (b -> b +/- 2*B_j):
    #     new_r1 = r1 -/+ 2 * B_j * a^(-1) mod p
    #     new_r2 = r2 -/+ 2 * B_j * a^(-1) mod p
    #
    #   So we precompute delta_j[i] = 2 * B_j * a_inv mod p_i for each
    #   (j, p_i) pair. Then switching costs O(FB_size) additions.
    # ------------------------------------------------------------------

    # Choose s (number of primes in a) and the FB range to select from
    target_a = isqrt(2 * n) // M
    log_target = float(gmpy2.log2(target_a)) if target_a > 0 else 0

    # Select s and FB range for 'a' construction.
    # Key tradeoff: larger s => more polys per 'a' (2^(s-1)) but each prime
    # is smaller, giving worse polynomial quality. For SIQS, s should give
    # primes in the range ~1000-50000 for best results.
    # We want: ideal_prime = target_a^(1/s) to fall within the FB, with
    # enough primes nearby to sample from (at least 3*s candidates).
    best_s = 2
    best_range = (1, len(fb) - 1)
    best_score = float('inf')
    for s_try in range(2, 12):
        ideal_log = log_target / s_try
        if ideal_log < 3.5 or ideal_log > 50:
            # Primes below ~12 or above ~10^15 are not useful for 'a'
            continue
        ideal_prime = int(2 ** ideal_log)
        mid = bisect.bisect_left(fb, ideal_prime)
        if mid >= len(fb):
            continue
        # Selection range: enough primes around the ideal
        lo = max(1, mid - max(s_try * 5, 20))
        hi = min(len(fb) - 1, mid + max(s_try * 5, 20))
        pool_size = hi - lo
        if pool_size < s_try * 3:
            continue
        actual_median = fb[min(max(mid, lo), hi)]
        # Primary score: how close is the median FB prime to the ideal?
        score = abs(math.log2(max(actual_median, 2)) - ideal_log)
        # Penalty for too-small primes (< 100): they degrade poly quality
        if ideal_prime < 100:
            score += 2.0
        elif ideal_prime < 500:
            score += 0.5
        # Penalty for very large s: diminishing returns on poly count
        if s_try > 8:
            score += (s_try - 8) * 0.5
        if score < best_score:
            best_score = score
            best_s = s_try
            best_range = (lo, hi)

    s = best_s
    select_lo, select_hi = best_range
    num_b_polys = 1 << (s - 1)  # 2^(s-1) polynomials per 'a'

    if verbose:
        print(f"    s={s}, {num_b_polys} polys/a, select FB[{select_lo}..{select_hi}]")

    # Pre-generate Gray code sequence for b-switching
    gray_seq = gray_code_sequence(s - 1)  # s-1 bits (first sign always +)

    # ------------------------------------------------------------------
    # Main sieve loop
    # ------------------------------------------------------------------
    sz = 2 * M  # Sieve array size: x in [-M, M) mapped to [0, 2M)

    # Serialize data needed by workers (convert numpy arrays to lists for pickling)
    _worker_fb_np_list = fb_np.tolist()
    _worker_fb_log_list = fb_log.tolist()
    _worker_sqrt_n_mod_list = list(sqrt_n_mod.items())
    _worker_gray_seq = gray_seq

    def _make_worker_args(seed, base_indices=None):
        """Build the argument tuple for _sieve_one_a worker."""
        return (int(n), fb, _worker_fb_np_list, _worker_fb_log_list, fb_size, M, sz,
                _worker_sqrt_n_mod_list, T_bits, nb, lp_bound,
                s, _worker_gray_seq, select_lo, select_hi, log_target,
                small_prime_correction, seed, base_indices)

    def _feed_relations(relations):
        """Feed raw relations from a worker into the DLP graph.
        Returns a direct factor if one was found, else None.
        Workers send sparse exps: tuple of (index, value) pairs.
        We reconstruct full exps list here to save pickle/IPC memory."""
        for rel_type, data in relations:
            if rel_type == _REL_DIRECT_FACTOR:
                return data
            elif rel_type == _REL_SMOOTH:
                x_stored, sign, sparse_exps = data
                exps = [0] * fb_size
                for j, e in sparse_exps:
                    exps[j] = e
                dlp_graph.add_smooth(x_stored, sign, exps)
            elif rel_type == _REL_SINGLE_LP:
                x_stored, sign, sparse_exps, lp = data
                exps = [0] * fb_size
                for j, e in sparse_exps:
                    exps[j] = e
                result = dlp_graph.add_single_lp(x_stored, sign, exps, lp)
                if result:
                    return result
            elif rel_type == _REL_DOUBLE_LP:
                x_stored, sign, sparse_exps, lp1, lp2 = data
                exps = [0] * fb_size
                for j, e in sparse_exps:
                    exps[j] = e
                result = dlp_graph.add_double_lp(x_stored, sign, exps, lp1, lp2)
                if result:
                    return result
        return None

    # Grouped a-selection: generate bases of s-1 primes for LP resonance
    # Cross-poly LP resonance: polynomials sharing s-1 of s primes in 'a' produce
    # large primes that collide ~3.3x more often than random, boosting DLP combines.
    # We use grouped selection for ~60% of 'a' values and random for ~40% to
    # maintain relation independence for LA while getting the LP collision benefit.
    group_size = 10  # number of variants per base group
    grouped_ratio = 0.5  # fraction of 'a' values using grouped selection
    # LP resonance with s-1 shared primes produces 3.3x more LP collisions,
    # but the resulting DLP-combined relations are GF(2)-duplicate (~90% waste).
    # s//2 sharing reduces dupes but also eliminates the resonance benefit.
    # Net effect: grouped a-selection provides no speedup with current DLP graph.
    # Keep the infrastructure for future improvements (e.g., cross-group LP matching).
    n_shared = max(2, s // 2)  # number of primes shared in base
    # Disabled by default: no measurable benefit with inline GF(2) dedup
    use_grouped = False  # grouped_a and s >= 5 and (select_hi - select_lo) >= s * 4

    def _gen_base(rng_local):
        """Generate a random base of n_shared FB prime indices for grouped a-selection."""
        try:
            return tuple(sorted(rng_local.sample(range(select_lo, select_hi), n_shared)))
        except ValueError:
            return None

    if n_workers > 1:
        # ============================================================
        # MULTI-PROCESS SIEVE MODE
        # ============================================================
        if verbose:
            mode_str = "grouped" if use_grouped else "random"
            print(f"    Parallel sieve: {n_workers} workers ({mode_str} a-selection)")

        # Use 'fork' context for fastest startup + shared numba JIT cache
        # (spawn would re-JIT in each worker, wasting ~2s each)
        mp_ctx = multiprocessing.get_context('fork')
        pool = mp_ctx.Pool(processes=n_workers)

        try:
            # Submit batches of 'a' values to the pool
            batch_size = n_workers * 2  # Keep workers fed with 2x pipeline depth
            seed_counter = random.randint(0, 2**31)

            for batch_start in range(0, 200000, batch_size):
                if dlp_graph.num_smooth >= needed or time.time() - t0 > time_limit:
                    break

                # Build batch of worker args
                batch_args = []
                if use_grouped:
                    # Mix grouped and random a-selection for LP resonance
                    # without sacrificing relation independence for LA
                    if not hasattr(_gen_base, '_base_pool'):
                        _gen_base._base_pool = []
                        _gen_base._base_usage = []
                    for i in range(batch_size):
                        seed_counter += 1
                        if random.random() < grouped_ratio:
                            # Grouped: pick from base pool
                            if not _gen_base._base_pool:
                                b = _gen_base(random.Random(seed_counter))
                                if b is not None:
                                    _gen_base._base_pool.append(b)
                                    _gen_base._base_usage.append(0)
                            if _gen_base._base_pool:
                                bi = random.randint(0, len(_gen_base._base_pool) - 1)
                                base = _gen_base._base_pool[bi]
                                _gen_base._base_usage[bi] += 1
                                if _gen_base._base_usage[bi] >= group_size:
                                    _gen_base._base_pool.pop(bi)
                                    _gen_base._base_usage.pop(bi)
                                batch_args.append(_make_worker_args(seed_counter, base))
                            else:
                                batch_args.append(_make_worker_args(seed_counter))
                        else:
                            # Random: original fully random selection
                            batch_args.append(_make_worker_args(seed_counter))
                else:
                    for i in range(batch_size):
                        seed_counter += 1
                        batch_args.append(_make_worker_args(seed_counter))

                # imap_unordered for dynamic load balancing
                for relations in pool.imap_unordered(_sieve_one_a, batch_args):
                    a_count += 1
                    poly_count += num_b_polys  # Each 'a' produces num_b_polys polynomials

                    if relations:
                        result = _feed_relations(relations)
                        if result:
                            if k > 1:
                                f = _extract_factor(result)
                                if f:
                                    pool.terminate()
                                    return f
                            else:
                                pool.terminate()
                                return result

                    if dlp_graph.num_smooth >= needed:
                        break

                # Progress report
                if verbose:
                    elapsed = time.time() - t0
                    ns = dlp_graph.num_smooth
                    rate = ns / max(elapsed, 0.001)
                    eta = (needed - ns) / max(rate, 0.001) if rate > 0 else 99999
                    print(f"      [{elapsed:.0f}s] a={a_count} poly={poly_count} "
                          f"sm={ns}/{needed} part={dlp_graph.num_partials} "
                          f"dlp={dlp_graph.dlp_count} "
                          f"rate={rate:.1f}/s eta={min(eta,99999):.0f}s")
        finally:
            pool.terminate()
            pool.join()

    else:
        # ============================================================
        # SINGLE-THREADED SIEVE MODE (original code path)
        # ============================================================
        # Preallocate sieve array (avoid 14MB+ allocation per polynomial)
        _sieve_buf = np.zeros(sz, dtype=np.int16)

        # Grouped a-selection state for single-thread mode
        _st_base_pool = []  # list of [base_indices, usage_count, base_product]

        for a_iter in range(200000):
            if dlp_graph.num_smooth >= needed or time.time() - t0 > time_limit:
                break

            # --- Select 'a' as product of s FB primes near target ---
            best_a = None
            best_diff = float('inf')

            if use_grouped and random.random() < grouped_ratio:
                # Grouped: use a base from pool
                if not _st_base_pool:
                    b = _gen_base(random)
                    if b is not None:
                        bp = mpz(1)
                        for i in b:
                            bp *= fb[i]
                        _st_base_pool.append([b, 0, bp])
                if _st_base_pool:
                    bi = random.randint(0, len(_st_base_pool) - 1)
                    cur_base, cur_usage, base_product = _st_base_pool[bi]
                    base_set = set(cur_base)
                    n_extra = s - len(cur_base)
                    for _ in range(20):
                        extras = []
                        extra_set = set(base_set)
                        for _e in range(n_extra):
                            for _try in range(10):
                                idx = random.randint(select_lo, select_hi - 1)
                                if idx not in extra_set:
                                    extras.append(idx)
                                    extra_set.add(idx)
                                    break
                        if len(extras) < n_extra:
                            continue
                        indices = sorted(list(cur_base) + extras)
                        a = base_product
                        for idx in extras:
                            a *= fb[idx]
                        diff = abs(float(gmpy2.log2(a)) - log_target) if a > 0 else float('inf')
                        if diff < best_diff:
                            best_diff = diff
                            best_a = a
                            best_primes = [fb[i] for i in indices]
                    _st_base_pool[bi][1] += 1
                    if _st_base_pool[bi][1] >= group_size:
                        _st_base_pool.pop(bi)

            if best_a is None:
                # Fallback to random (also used when grouped_a=False)
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
            a_prime_idx = [fb_index[ap] for ap in a_primes]
            a_prime_set = set(a_primes)
            a_int = int(a)
            a_count += 1

            # --- Compute t_roots: sqrt(n) mod q_j for each q_j in a ---
            t_roots = []
            ok = True
            for q in a_primes:
                t = sqrt_n_mod.get(q)
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
            a_inv_mod = np.zeros(fb_size, dtype=np.int64)
            is_a_prime = np.zeros(fb_size, dtype=np.bool_)
            for pi in range(fb_size):
                p = fb[pi]
                if p in a_prime_set:
                    a_inv_mod[pi] = 0
                    is_a_prime[pi] = True
                else:
                    try:
                        a_inv_mod[pi] = pow(a_int % p, -1, p)
                    except (ValueError, ZeroDivisionError):
                        a_inv_mod[pi] = 0

            regular_idx = np.where(~is_a_prime)[0]

            # --- Precompute delta arrays for Gray code switching ---
            deltas = []
            for j in range(s):
                d = np.zeros(fb_size, dtype=np.int64)
                B_j_2 = 2 * B_values[j]
                for pi in range(fb_size):
                    p = fb[pi]
                    if p in a_prime_set:
                        d[pi] = 0
                    else:
                        d[pi] = int(B_j_2 % p) * a_inv_mod[pi] % p
                deltas.append(d)

            # --- First polynomial: all signs positive ---
            b = mpz(0)
            for B_j in B_values:
                b += B_j
            if (b * b - n) % a != 0:
                b = -b
                if (b * b - n) % a != 0:
                    continue

            c = (b * b - n) // a
            b_int = int(b)

            # --- Compute initial sieve offsets for first polynomial ---
            o1 = np.full(fb_size, -1, dtype=np.int64)
            o2 = np.full(fb_size, -1, dtype=np.int64)

            for pi in range(fb_size):
                p = fb[pi]
                if p == 2:
                    g0 = int(c % 2)
                    g1 = int((a_int + 2 * b_int + int(c)) % 2)
                    if g0 == 0:
                        o1[pi] = M % 2
                        if g1 == 0:
                            o2[pi] = (M + 1) % 2
                    elif g1 == 0:
                        o1[pi] = (M + 1) % 2
                    continue

                if p in a_prime_set:
                    b2 = (2 * b_int) % p
                    if b2 == 0:
                        continue
                    b2_inv = pow(b2, -1, p)
                    c_mod = int(c % p)
                    r = (-c_mod * b2_inv) % p
                    o1[pi] = (r + M) % p
                    continue

                t = sqrt_n_mod.get(p)
                if t is None:
                    continue
                ai = int(a_inv_mod[pi])
                bm = b_int % p
                r1 = (ai * (t - bm)) % p
                r2 = (ai * (p - t - bm)) % p
                o1[pi] = (r1 + M) % p
                o2[pi] = ((r2 + M) % p) if r2 != r1 else -1

            # --- Sieve first polynomial ---
            def sieve_and_collect(b_val, c_val, off1, off2):
                """Sieve one polynomial and collect relations using batch hit detection."""
                nonlocal poly_count, total_cands
                b_v = int(b_val)
                c_v = int(c_val)

                _sieve_buf[:] = 0
                sieve_arr = _sieve_buf
                jit_sieve(sieve_arr, fb_np, fb_log, off1, off2, sz)

                log_g_max = math.log2(max(M, 1)) + 0.5 * nb
                thresh = int(max(0, (log_g_max - T_bits)) * 64)

                candidates = jit_find_smooth(sieve_arr, thresh)
                n_cand = len(candidates)
                total_cands += n_cand

                if n_cand == 0:
                    poly_count += 1
                    return None

                hit_starts, hit_fb = jit_batch_find_hits(
                    candidates, n_cand, fb_np, off1, off2, fb_size)

                for ci in range(n_cand):
                    sieve_pos = int(candidates[ci])
                    x = sieve_pos - M
                    ax_b = int(a * x + b_val)
                    gx = a_int * x * x + 2 * b_v * x + c_v

                    h_start = hit_starts[ci]
                    h_end = hit_starts[ci + 1]

                    result = process_candidate_batch(
                        ax_b, gx, a_prime_idx, hit_fb, h_start, h_end)
                    if result:
                        return result

                poly_count += 1
                return None

            result = sieve_and_collect(b, c, o1, o2)
            if result:
                if k > 1:
                    f = _extract_factor(result)
                    if f:
                        return f
                else:
                    return result

            # --- Gray code B-switching ---
            signs = [1] * s

            for gray_val, flip_bit, flip_dir in gray_seq:
                if dlp_graph.num_smooth >= needed or time.time() - t0 > time_limit:
                    break

                j = flip_bit + 1
                if j >= s:
                    continue

                old_sign = signs[j]
                signs[j] = -old_sign

                if signs[j] < 0:
                    b = b - 2 * B_values[j]
                    offset_dir = 1
                else:
                    b = b + 2 * B_values[j]
                    offset_dir = -1

                c = (b * b - n) // a
                b_int = int(b)

                delta_j = deltas[j]
                ri = regular_idx
                valid1 = o1[ri] >= 0
                ri_v1 = ri[valid1]
                valid2 = o2[ri] >= 0
                ri_v2 = ri[valid2]

                if offset_dir > 0:
                    o1[ri_v1] = (o1[ri_v1] + delta_j[ri_v1]) % fb_np[ri_v1]
                    o2[ri_v2] = (o2[ri_v2] + delta_j[ri_v2]) % fb_np[ri_v2]
                else:
                    o1[ri_v1] = (o1[ri_v1] - delta_j[ri_v1]) % fb_np[ri_v1]
                    o2[ri_v2] = (o2[ri_v2] - delta_j[ri_v2]) % fb_np[ri_v2]

                for pi in a_prime_idx:
                    p = fb[pi]
                    if p == 2:
                        g0 = int(c % 2)
                        g1 = int((a_int + 2 * b_int + int(c)) % 2)
                        o1[pi] = -1
                        o2[pi] = -1
                        if g0 == 0:
                            o1[pi] = M % 2
                            if g1 == 0:
                                o2[pi] = (M + 1) % 2
                        elif g1 == 0:
                            o1[pi] = (M + 1) % 2
                        continue
                    b2 = (2 * b_int) % p
                    if b2 == 0:
                        o1[pi] = -1
                        o2[pi] = -1
                        continue
                    b2_inv = pow(b2, -1, p)
                    c_mod = int(c % p)
                    r = (-c_mod * b2_inv) % p
                    o1[pi] = (r + M) % p
                    o2[pi] = -1

                result = sieve_and_collect(b, c, o1, o2)
                if result:
                    if k > 1:
                        f = _extract_factor(result)
                        if f:
                            return f
                    else:
                        return result

            # Progress report
            if a_count % max(1, 10 if nd < 60 else 3) == 0 and verbose:
                elapsed = time.time() - t0
                ns = dlp_graph.num_smooth
                rate = ns / max(elapsed, 0.001)
                eta = (needed - ns) / max(rate, 0.001) if rate > 0 else 99999
                print(f"      [{elapsed:.0f}s] a={a_count} poly={poly_count} "
                      f"sm={ns}/{needed} part={dlp_graph.num_partials} "
                      f"dlp={dlp_graph.dlp_count} cand={total_cands} "
                      f"rate={rate:.1f}/s eta={min(eta,99999):.0f}s")

    # ======================================================================
    # Stage 3: GF(2) Gaussian Elimination
    # ======================================================================
    smooth = dlp_graph.smooth
    elapsed = time.time() - t0

    if len(smooth) < fb_size + 1:
        if verbose:
            print(f"\n    Insufficient: {len(smooth)}/{needed} ({elapsed:.1f}s)")
        return None


    if verbose:
        print(f"\n    LA: {len(smooth)} x {fb_size + 1}")

    la_t0 = time.time()

    # Singleton filtering: remove columns appearing in only 1 relation (iteratively)
    # This reduces matrix size by 15-50%, speeding up Gaussian elimination.
    active_rows = list(range(len(smooth)))
    for _filt_pass in range(10):  # iterate until stable
        # Count column occurrences across active rows
        col_count = {}
        for ri in active_rows:
            _, sign, exps = smooth[ri]
            if sign % 2:
                col_count[0] = col_count.get(0, 0) + 1
            for j, e in enumerate(exps):
                if e % 2:
                    col_count[j + 1] = col_count.get(j + 1, 0) + 1
        # Find singleton columns (count == 1)
        singletons = {c for c, cnt in col_count.items() if cnt == 1}
        if not singletons:
            break
        # Remove rows that contain a singleton column
        new_active = []
        for ri in active_rows:
            _, sign, exps = smooth[ri]
            has_singleton = False
            if sign % 2 and 0 in singletons:
                has_singleton = True
            if not has_singleton:
                for j, e in enumerate(exps):
                    if e % 2 and (j + 1) in singletons:
                        has_singleton = True
                        break
            if not has_singleton:
                new_active.append(ri)
        if len(new_active) == len(active_rows):
            break
        active_rows = new_active

    if verbose and len(active_rows) < len(smooth):
        print(f"    Filtering: {len(smooth)} -> {len(active_rows)} rows "
              f"({100 - len(active_rows) * 100 // len(smooth)}% removed)")

    # Remap to filtered set
    filtered_smooth = [smooth[i] for i in active_rows]
    row_map = active_rows  # maps filtered index -> original index

    nrows = len(filtered_smooth)
    ncols = fb_size + 1  # +1 for the sign column

    # Build sparse rows for bitpacked Gauss (list of sets of odd-exponent columns)
    sparse_rows = []
    for _, sign, exps in filtered_smooth:
        cols = set()
        if sign % 2:
            cols.add(0)
        for j, e in enumerate(exps):
            if e % 2 == 1:
                cols.add(j + 1)
        sparse_rows.append(cols)

    try:
        from block_lanczos import bitpacked_gauss
        raw_vecs = bitpacked_gauss(sparse_rows, ncols)
    except (ImportError, MemoryError):
        raw_vecs = _fallback_gauss(sparse_rows, ncols, nrows)

    # Map filtered indices back to original smooth[] indices
    null_vecs = [[row_map[i] for i in vec] for vec in raw_vecs]

    if verbose:
        print(f"    LA: {time.time()-la_t0:.1f}s, {len(null_vecs)} null vecs")

    # Try each null vector to find a factor
    for vi, indices in enumerate(null_vecs):
        x_val = mpz(1)
        total_exp = [0] * fb_size
        total_sign = 0
        for idx in indices:
            ax, sign, exps = smooth[idx]
            x_val = x_val * mpz(ax) % n
            total_sign += sign
            for j in range(fb_size):
                total_exp[j] += exps[j]

        if any(e % 2 != 0 for e in total_exp) or total_sign % 2 != 0:
            continue

        y_val = mpz(1)
        for j, e in enumerate(total_exp):
            if e > 0:
                y_val = y_val * pow(mpz(fb[j]), e // 2, n) % n

        for diff in [x_val - y_val, x_val + y_val]:
            g = gcd(diff % n, n)
            if 1 < g < n:
                if k > 1:
                    f = _extract_factor(int(g))
                    if f is None:
                        continue
                    total = time.time() - t0
                    if verbose:
                        print(f"\n    *** FACTOR: {f} ({total:.1f}s, k={k}) ***")
                    return f
                else:
                    total = time.time() - t0
                    if verbose:
                        print(f"\n    *** FACTOR: {g} ({total:.1f}s) ***")
                    return int(g)

    if verbose:
        print(f"    {len(null_vecs)} null vecs, no factor found.")
    return None


###############################################################################
# GNFS POLYNOMIAL SELECTION (Scaffold)
###############################################################################

def gnfs_polynomial_select(n, degree=5):
    """
    Basic base-m polynomial selection for the General Number Field Sieve.

    Given n, find m = floor(n^(1/d)) for degree d, then express n in base m:
        n = c_d * m^d + c_{d-1} * m^{d-1} + ... + c_1 * m + c_0

    This gives:
        f(x) = c_d * x^d + c_{d-1} * x^{d-1} + ... + c_0
        g(x) = x - m

    Properties:
        - f(m) = n (by construction)
        - g(m) = 0
        - The algebraic factor base uses f(x); the rational factor base uses g(x)
        - Both share the common root m modulo n: f(m) = 0 (mod n), g(m) = 0 (mod n)

    For actual GNFS, you'd want to optimize the polynomial to minimize
    the size of norms (Kleinjung's method), but base-m is the starting point.

    Parameters:
        n: number to factor (should be > 10^100 for GNFS to beat QS)
        degree: polynomial degree (typically 5 for 100-150 digits, 6 for 150+)

    Returns:
        (f_coeffs, m) where f_coeffs = [c_0, c_1, ..., c_d] (low-to-high)
    """
    n = mpz(n)
    d = degree

    # Compute m = floor(n^(1/d))
    # Use gmpy2.iroot for exact integer root
    m, exact = gmpy2.iroot(n, d)

    # If m^d > n, decrease m by 1
    while pow(m, d) > n:
        m -= 1
    # If (m+1)^d <= n, increase m
    while pow(m + 1, d) <= n:
        m += 1

    # Express n in base m: n = c_d * m^d + ... + c_0
    coeffs = []
    remainder = n
    for i in range(d + 1):
        q, r = divmod(remainder, m)
        coeffs.append(int(r))
        remainder = q

    # Verify: f(m) should equal n
    check = mpz(0)
    m_power = mpz(1)
    for c in coeffs:
        check += mpz(c) * m_power
        m_power *= m

    assert check == n, f"Polynomial check failed: f(m)={check} != n={n}"

    # Verify leading coefficient
    # coeffs[-1] should be > 0 (it's c_d)
    # Trim any leading zeros
    while len(coeffs) > 1 and coeffs[-1] == 0:
        coeffs.pop()

    return coeffs, int(m)


def gnfs_compute_norms(f_coeffs, m, a, b):
    """
    Compute algebraic and rational norms for a coprime pair (a, b).

    Algebraic norm: N(a + b*alpha) = (-b)^d * f(-a/b)
        = sum_{i=0}^{d} f_coeffs[i] * (-a)^i * (-b)^(d-i)  [homogenized]
        = resultant of (a + b*x) and f(x)

    Rational norm: a + b*m

    These norms must both be smooth over their respective factor bases
    for (a, b) to yield a useful relation in GNFS.

    Parameters:
        f_coeffs: polynomial coefficients [c_0, c_1, ..., c_d] (low-to-high)
        m: the base-m value
        a, b: coprime integers

    Returns:
        (algebraic_norm, rational_norm)
    """
    d = len(f_coeffs) - 1

    # Algebraic norm via homogeneous evaluation:
    # N = sum_{i=0}^{d} c_i * a^i * b^(d-i)  [with alternating sign pattern]
    # More precisely: N = (-b)^d * f(-a/b)
    # = sum_{i=0}^{d} c_i * (-a/b)^i * (-b)^d
    # = sum_{i=0}^{d} c_i * (-a)^i * (-b)^(d-i)
    # = sum_{i=0}^{d} c_i * (-1)^i * a^i * (-1)^(d-i) * b^(d-i)
    # = (-1)^d * sum_{i=0}^{d} c_i * a^i * (-b)^(d-i)  ... let's just compute directly

    a_mpz = mpz(a)
    b_mpz = mpz(b)
    neg_a = -a_mpz
    neg_b = -b_mpz

    alg_norm = mpz(0)
    neg_a_power = mpz(1)   # (-a)^i
    for i in range(d + 1):
        neg_b_power = pow(neg_b, d - i)  # (-b)^(d-i)
        alg_norm += mpz(f_coeffs[i]) * neg_a_power * neg_b_power
        neg_a_power *= neg_a

    # Rational norm: a + b*m
    rat_norm = int(a_mpz + b_mpz * mpz(m))

    return int(alg_norm), rat_norm


###############################################################################
# TEST SUITE
###############################################################################

if __name__ == "__main__":
    random.seed(42)

    print("=" * 70)
    print("SIQS ENGINE v1.0")
    print("Self-Initializing Quadratic Sieve + GNFS Scaffold")
    print("=" * 70)

    # ------------------------------------------------------------------
    # Test 1: GNFS polynomial selection
    # ------------------------------------------------------------------
    print("\n--- GNFS Polynomial Selection Test ---")
    # Use RSA-100 as example
    RSA_100 = 1522605027922533360535618378132637429718068114961380688657908494580122963258952897654000350692006139
    coeffs, m = gnfs_polynomial_select(RSA_100, degree=5)
    print(f"  n = RSA-100 ({len(str(RSA_100))}d)")
    print(f"  degree = 5")
    print(f"  m = {m}")
    print(f"  f(x) = ", end="")
    terms = []
    for i in range(len(coeffs) - 1, -1, -1):
        if coeffs[i] != 0:
            if i == 0:
                terms.append(f"{coeffs[i]}")
            elif i == 1:
                terms.append(f"{coeffs[i]}*x")
            else:
                terms.append(f"{coeffs[i]}*x^{i}")
    print(" + ".join(terms))

    # Test algebraic/rational norms
    alg_norm, rat_norm = gnfs_compute_norms(coeffs, m, 1, 1)
    print(f"  Algebraic norm N(1+alpha) = {alg_norm}")
    print(f"  Rational norm 1+m = {rat_norm}")
    alg_norm2, rat_norm2 = gnfs_compute_norms(coeffs, m, 3, 7)
    print(f"  Algebraic norm N(3+7*alpha) = {alg_norm2}")
    print(f"  Rational norm 3+7*m = {rat_norm2}")

    # ------------------------------------------------------------------
    # Test 2: SIQS factoring at various sizes
    # ------------------------------------------------------------------
    print(f"\n{'=' * 70}")
    print("SIQS Factoring Tests")
    print(f"{'=' * 70}")

    # Generate test semiprimes
    tests = []

    # 20 digits
    tests.append(("20d", 1000000009 * 1000000087))

    # 30 digits
    tests.append(("30d", 100000000000067 * 100000000000097))

    # 40 digits
    p40 = int(next_prime(mpz(10) ** 19 + 7))
    q40 = int(next_prime(mpz(10) ** 19 + 231))
    tests.append(("40d", p40 * q40))

    # 50 digits
    p50 = int(next_prime(mpz(random.getrandbits(83))))
    q50 = int(next_prime(mpz(random.getrandbits(83))))
    tests.append(("50d", p50 * q50))

    # 60 digits
    p60 = int(next_prime(mpz(random.getrandbits(100))))
    q60 = int(next_prime(mpz(random.getrandbits(100))))
    tests.append(("60d", p60 * q60))

    results = []
    for name, n_val in tests:
        nd = len(str(n_val))
        nb = int(gmpy2.log2(mpz(n_val))) + 1
        print(f"\n{'_' * 70}")
        print(f"### {name}: {nd}d ({nb}b) ###")
        print(f"  n = {n_val}")
        t0 = time.time()
        f = siqs_factor(n_val, verbose=True, time_limit=600)
        elapsed = time.time() - t0
        ok = f is not None and 1 < f < n_val and n_val % f == 0
        if ok:
            print(f"  PASS: {f} x {n_val // f} ({elapsed:.1f}s)")
        else:
            print(f"  FAIL ({elapsed:.1f}s)")
        results.append((name, nd, elapsed, ok))

    # Summary
    print(f"\n{'=' * 70}")
    print("RESULTS SUMMARY")
    print(f"{'=' * 70}")
    for name, nd, t, ok in results:
        status = "PASS" if ok else "FAIL"
        print(f"  {name:10s} ({nd:3d}d) {t:8.1f}s  {status}")

    passes = sum(1 for _, _, _, ok in results if ok)
    print(f"\n  {passes}/{len(results)} passed")

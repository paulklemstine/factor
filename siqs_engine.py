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
from gmpy2 import mpz, isqrt, is_prime, gcd, jacobi, next_prime
import numpy as np
from numba import njit
import time
import math
import random
import bisect
from collections import defaultdict


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
def jit_sieve(sieve_arr, primes, logs, offsets1, offsets2, sz):
    """Inner sieve loop: add log contributions at arithmetic progressions."""
    for i in range(len(primes)):
        p = primes[i]
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
def jit_update_offsets_gray(offsets1, offsets2, deltas1, deltas2, sz, num_primes, flip_sign):
    """
    Gray code B-switching: update sieve offsets by adding or subtracting
    precomputed deltas. This is the core SIQS speedup.

    When switching from b to b' = b +/- 2*B_values[j], the sieve roots
    shift by +/- delta[i] for each prime p_i, where:
        delta[i] = 2 * B_values[j] * a_inv[i] mod p_i

    flip_sign: +1 or -1 (whether to add or subtract the delta)
    """
    for i in range(num_primes):
        if offsets1[i] >= 0:
            if flip_sign > 0:
                offsets1[i] = (offsets1[i] + deltas1[i]) % (deltas1[i] + deltas2[i] + 1)
            else:
                offsets1[i] = (offsets1[i] - deltas1[i])
            # Wrap into [0, sz)
            # Actually we need mod p, but p isn't passed here.
            # We'll handle this in Python instead.
            pass
    # This kernel is a placeholder — the real update is done in Python
    # because we need the prime values for modular arithmetic.


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
        (20,    80,    20000),
        (25,   150,    40000),
        (30,   250,    80000),
        (35,   450,   150000),
        (40,   800,   300000),
        (45,  1200,   500000),
        (50,  3000,  1000000),
        (55,  4500,  1500000),
        (60,  6500,  2500000),
        (65,  7000,  4000000),
        (70, 10000,  6000000),
        (75, 15000,  8000000),
        (80, 22000, 12000000),
        (85, 32000, 16000000),
        (90, 45000, 22000000),
        (95, 60000, 28000000),
        (100, 80000, 35000000),
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

        # Full relations (smooth + combined)
        self.smooth = []

    def add_smooth(self, x, sign, exps):
        """Add a fully smooth relation."""
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
            self.smooth.append((cax, cs, ce))
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

        # Try to find path from lp1 to lp2 in existing graph (BFS, limited depth)
        path = self._find_path(lp1, lp2, max_depth=10)
        if path is not None:
            # Found a cycle! Combine all relations along the path + this new edge
            result = self._combine_cycle(path, x, sign, exps, lp1, lp2)
            if result is not None:
                return result

        # No cycle found — just store the edge
        self.dlp_graph[lp1].append((lp2, x, sign, exps))
        self.dlp_graph[lp2].append((lp1, x, sign, exps))
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

    def _combine_cycle(self, path, new_x, new_sign, new_exps, lp1, lp2):
        """
        Combine relations along a cycle to produce a full relation.

        Each edge contributes: x_i^2 = (-1)^s_i * prod(fb^e_i) * lp_a * lp_b (mod n)
        Around the cycle, each large prime appears exactly twice (entering and leaving
        a vertex), so they cancel in pairs.

        Combined x = product of all x_i mod n
        Combined exps = sum of all exps_i
        For the large primes: each appears twice, so add 2 to their "exponent"
        which is even and vanishes in GF(2).
        """
        combined_x = new_x
        combined_sign = new_sign
        combined_exps = list(new_exps)

        # Collect all large primes that appear (each should appear exactly twice)
        lp_counts = defaultdict(int)
        lp_counts[lp1] += 1
        lp_counts[lp2] += 1

        for src, dst in path:
            # Find the edge data
            edge_found = False
            for neighbor, x, sign, exps in self.dlp_graph[src]:
                if neighbor == dst:
                    combined_x = combined_x * x % int(self.n)
                    combined_sign = (combined_sign + sign) % 2
                    for j in range(len(combined_exps)):
                        combined_exps[j] += exps[j]
                    lp_counts[src] += 1
                    lp_counts[dst] += 1
                    edge_found = True
                    break
            if not edge_found:
                return None  # Shouldn't happen

        # Each large prime should appear exactly twice — cancel them
        # by multiplying x by lp^(-1) for each pair
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

        self.smooth.append((combined_x, combined_sign, combined_exps))
        return None

    @property
    def num_smooth(self):
        return len(self.smooth)

    @property
    def num_partials(self):
        return len(self.slp_partials)


###############################################################################
# SIQS CORE
###############################################################################

def siqs_factor(n, verbose=True, time_limit=3600):
    """
    Self-Initializing Quadratic Sieve (SIQS).

    Core relation: (a*x + b)^2 = a * g(x) (mod n)
    where g(x) = a*x^2 + 2*b*x + c, c = (b^2 - n) / a

    Key improvements over MPQS:
    1. Gray code enumeration of b-values for O(1) poly switching
    2. Precomputed offset deltas for incremental sieve updates
    3. Double large prime variation for ~2x more relations
    4. Batch generation of 2^(s-1) polynomials per 'a' value

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

    fb_size, M = siqs_params(nd)

    if verbose:
        print(f"  SIQS: {nd}d ({nb}b), FB={fb_size}, M={M}")

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
    fb_log = np.array([int(round(math.log2(p) * 1024)) for p in fb], dtype=np.int32)
    fb_index = {p: i for i, p in enumerate(fb)}

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

    # Double large prime setup
    lp_bound = fb[-1] ** 2  # Single LP bound: cofactor < FB_max^2
    dlp_bound = fb[-1] ** 3  # Double LP bound: cofactor < FB_max^3

    # T_bits = nb // 4 — critical threshold from v5.0
    T_bits = max(15, nb // 4)
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

    def trial_divide_smart(val, sieve_pos, off1, off2):
        """
        Sieve-informed trial division: only check primes whose sieve root
        matches the candidate position. Reduces from O(FB_size) to O(hits).

        For each prime p, g(x) is divisible by p iff sieve_pos % p == off1[p]
        or sieve_pos % p == off2[p]. Use numpy vectorized modulo to find hits.
        """
        v = mpz(abs(val))
        exps = [0] * fb_size

        # Vectorized: find which primes have a sieve root at this position
        pos_mod = sieve_pos % fb_np  # numpy broadcast: scalar % array
        hit_mask = (pos_mod == off1) | ((off2 >= 0) & (pos_mod == off2))
        hit_indices = np.flatnonzero(hit_mask)

        # Trial-divide only by primes that hit this position
        for i in hit_indices:
            p = fb[i]
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
                exps[i] = e

        return exps, int(v)

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
        elif remainder < dlp_bound:
            # Potential double large prime: try to factor remainder into 2 primes
            # Each prime must be < lp_bound^(1/2) = fb[-1]... no, each < sqrt(dlp_bound)
            # Actually: remainder = p1 * p2 where both < lp_bound
            rem_mpz = mpz(remainder)
            if not is_prime(rem_mpz):
                sr = isqrt(rem_mpz)
                if sr * sr == rem_mpz and sr < lp_bound:
                    # Perfect square of a large prime
                    result = dlp_graph.add_single_lp(x_stored, sign, exps, int(sr))
                    if result:
                        return result
                    # Actually this means remainder = sr^2, add sr twice
                    # Treat as smooth with sr appearing with exponent 2 (even, so vanishes)
                    dlp_graph.add_smooth(x_stored, sign, exps)
                else:
                    # Try small primes to split remainder
                    # Quick trial: if remainder has a small factor, one of the two
                    # large primes is small enough to find quickly
                    found_split = False
                    rem_int = int(remainder)

                    # Check if remainder is divisible by any FB prime we missed
                    # (shouldn't happen if trial_divide is correct, but the
                    #  early-exit on p^2 > v means we may have stopped early)
                    # Actually the early exit is fine — remainder IS the cofactor.
                    # For DLP, we need to factor it into exactly 2 primes.

                    # Use Pollard rho or just check if it's a semiprime
                    # For speed, try a quick Fermat/Pollard check
                    lp1 = _pollard_rho_quick(rem_mpz, limit=1000)
                    if lp1 is not None and lp1 > 1 and lp1 < rem_int:
                        lp2 = rem_int // lp1
                        if is_prime(mpz(lp1)) and is_prime(mpz(lp2)):
                            if lp1 < lp_bound and lp2 < lp_bound:
                                result = dlp_graph.add_double_lp(
                                    x_stored, sign, exps, lp1, lp2)
                                if result:
                                    return result
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

    for a_iter in range(200000):
        if dlp_graph.num_smooth >= needed or time.time() - t0 > time_limit:
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
        # B_j = t_j * (a/q_j) * inv(a/q_j, q_j)
        # These are the building blocks for b = sum(+/- B_j)
        B_values = []
        b_ok = True
        for j in range(s):
            q = a_primes[j]
            A_j = a // q  # a / q_j
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
        # Also build mask of "regular" primes (not dividing a) for fast updates
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

        # Indices of primes NOT in a (the vast majority) — for vectorized updates
        regular_idx = np.where(~is_a_prime)[0]

        # --- Precompute delta arrays for Gray code switching ---
        # delta_j[pi] = 2 * B_values[j] * a_inv mod p  for each (j, pi)
        # When flipping sign of B_values[j], offsets change by +/- delta_j[pi]
        deltas = []  # deltas[j] is numpy array of shape (fb_size,)
        for j in range(s):
            d = np.zeros(fb_size, dtype=np.int64)
            B_j_2 = 2 * B_values[j]  # 2 * B_j (mpz)
            for pi in range(fb_size):
                p = fb[pi]
                if p in a_prime_set:
                    d[pi] = 0
                else:
                    d[pi] = int(B_j_2 % p) * a_inv_mod[pi] % p
            deltas.append(d)

        # --- First polynomial: all signs positive ---
        # b = sum(B_j); DO NOT reduce mod a — this preserves b mod p
        # for all FB primes p, which is essential for incremental offset updates.
        # The CRT construction guarantees b^2 = n (mod a) without reduction.
        b = mpz(0)
        for B_j in B_values:
            b += B_j
        # Verify b^2 = n (mod a)
        if (b * b - n) % a != 0:
            # Try negating b
            b = -b
            if (b * b - n) % a != 0:
                continue

        c = (b * b - n) // a
        b_int = int(b)

        # --- Compute initial sieve offsets for first polynomial ---
        # g(x) = a*x^2 + 2*b*x + c
        # Roots: x = a^(-1) * (+/- sqrt(n) - b) mod p
        o1 = np.full(fb_size, -1, dtype=np.int64)
        o2 = np.full(fb_size, -1, dtype=np.int64)

        for pi in range(fb_size):
            p = fb[pi]
            if p == 2:
                # Handle p=2 specially
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
                # For primes dividing a: single root x = -c/(2b) mod p
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
            """Sieve one polynomial and collect relations."""
            nonlocal poly_count, total_cands
            b_v = int(b_val)
            c_v = int(c_val)

            sieve_arr = np.zeros(sz, dtype=np.int32)
            jit_sieve(sieve_arr, fb_np, fb_log, off1, off2, sz)

            # Threshold: log2(max|g(x)|) - T_bits
            # max|g(x)| ~ a*M^2 for large M, but more precisely:
            # |g(x)| = |a*x^2 + 2*b*x + c| <= a*M^2 + 2*b*M + |c|
            log_g_max = math.log2(max(M, 1)) + 0.5 * nb
            thresh = int(max(0, (log_g_max - T_bits)) * 1024)

            candidates = jit_find_smooth(sieve_arr, thresh)
            total_cands += len(candidates)

            for ci in range(len(candidates)):
                sieve_pos = int(candidates[ci])
                x = sieve_pos - M
                ax_b = int(a * x + b_val)
                # g(x) = a*x^2 + 2*b*x + c  (sieve g(x), NOT Q(x) = ax^2 - n)
                gx = a_int * x * x + 2 * b_v * x + c_v
                result = process_candidate(ax_b, gx, a_prime_idx,
                                           sieve_pos=sieve_pos, off1=off1, off2=off2)
                if result:
                    return result

            poly_count += 1
            return None

        result = sieve_and_collect(b, c, o1, o2)
        if result:
            return result

        # --- Gray code B-switching: generate remaining 2^(s-1) - 1 polynomials ---
        # Track current sign state: signs[j] = +1 or -1
        signs = [1] * s  # Start: all positive

        for gray_val, flip_bit, flip_dir in gray_seq:
            if dlp_graph.num_smooth >= needed or time.time() - t0 > time_limit:
                break

            # Flip sign of B_values[flip_bit + 1] (bit 0 in gray = B_values[1])
            # (B_values[0] sign is always fixed positive)
            j = flip_bit + 1  # Index into B_values (skip index 0)
            if j >= s:
                continue

            old_sign = signs[j]
            signs[j] = -old_sign

            # Update b: b_new = b_old + 2 * (new_sign - old_sign)/2 * B_values[j]
            #         = b_old +/- 2 * B_values[j]
            # If sign flipped from +1 to -1: subtract 2*B_j
            # If sign flipped from -1 to +1: add 2*B_j
            if signs[j] < 0:
                b = b - 2 * B_values[j]
                offset_dir = 1   # Add delta to offsets (root increases)
            else:
                b = b + 2 * B_values[j]
                offset_dir = -1  # Subtract delta from offsets (root decreases)

            # DO NOT reduce b mod a — this would break incremental offset updates
            # because (b % a) mod p != b mod p in general.
            c = (b * b - n) // a
            b_int = int(b)

            # --- Incremental offset update (the SIQS key win) ---
            # For regular primes (not dividing a): vectorized add/sub delta
            # For a-primes (only s of them): recompute from scratch (cheap)
            #
            # Math: when b -> b' = b +/- 2*B_j, the sieve roots change:
            #   r_new = a_inv * (t - b') mod p = r_old -/+ 2*B_j*a_inv mod p
            #   offset_new = (r_new + M) mod p = offset_old -/+ delta_j mod p
            #
            # When sign flips +1 -> -1: b decreases by 2*B_j, so root INCREASES by delta
            # When sign flips -1 -> +1: b increases by 2*B_j, so root DECREASES by delta
            delta_j = deltas[j]

            # Vectorized update for regular primes (the fast path)
            # CRITICAL: only update primes that have valid offsets (o1 >= 0)
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

            # Recompute for the few a-primes (at most s primes)
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
    nrows = len(smooth)
    ncols = fb_size + 1  # +1 for the sign column

    # Build GF(2) matrix using Python big ints as bit vectors
    mat = []
    for _, sign, exps in smooth:
        row = sign  # Bit 0 = sign
        for j, e in enumerate(exps):
            if e % 2 == 1:
                row |= (1 << (j + 1))
        mat.append(row)

    # Gaussian elimination with combination tracking
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
        for row in range(nrows):
            if row != piv and mat[row] & mask:
                mat[row] ^= mat[piv]
                combo[row] ^= combo[piv]

    # Extract null space vectors
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

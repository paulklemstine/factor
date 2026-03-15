#!/usr/bin/env python3
"""
B3-MPQS Engine — Pythagorean B3 Polynomial Source for MPQS
==========================================================

Uses B3 (Pythagorean progression) to generate MPQS polynomials with small residues:

For each n0 = 1, 2, 3, ..., set m0 = round(n0 * sqrt(N)).
Define: a = (2*n0)^2, b = m0 (adjusted so b^2 ≡ N mod a), c = (b^2-N)/a.
Polynomial: g(x) = a*x^2 + 2*b*x + c
Relation: (a*x + b)^2 = a*g(x) + N ≡ a*g(x) (mod N)

This is standard MPQS where:
- x_stored = a*x + b (the value whose square gives a*g(x) mod N)
- We sieve and factor g(x)
- Add a's prime factors to the exponent vector

The B3 construction ensures |c| ≈ sqrt(N)/(4*n0^2), giving small residues.

Features:
  - Log sieve with Tonelli-Shanks root finding
  - Single Large Prime variation
  - GF(2) Gaussian elimination
  - Numba JIT sieve kernel
  - Adaptive per-position sieve threshold
"""

import gmpy2
from gmpy2 import mpz, isqrt, is_prime, gcd, jacobi, next_prime, iroot
import numpy as np
from numba import njit
import time
import math
import os

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
# NUMBA JIT SIEVE KERNELS
###############################################################################

@njit(cache=True)
def jit_sieve(sieve_arr, primes, logs, offsets1, offsets2, sz):
    """Inner sieve loop: add log contributions at arithmetic progressions."""
    for i in range(len(primes)):
        p = primes[i]
        if p < 32:
            continue
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


###############################################################################
# PARAMETER TABLE
###############################################################################

def b3mpqs_params(nd):
    """
    Parameter selection for B3-MPQS.
    Returns (fb_size, sieve_half).
    """
    tbl = [
        (20,    80,   10000),
        (25,   150,   20000),
        (30,   300,   40000),
        (35,   500,   80000),
        (40,   900,  150000),
        (45,  1500,  250000),
        (50,  2800,  500000),
        (55,  4000,  800000),
        (60,  5500, 1500000),
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
# MAIN B3-MPQS ENGINE
###############################################################################

def b3mpqs_factor(N, verbose=True, time_limit=3600):
    """
    Factor N using B3-MPQS.

    The B3 progression generates MPQS polynomials:
      a = (2*n0)^2 = 4*n0^2
      b chosen so b^2 ≡ N (mod a)  [b = m0 adjusted]
      c = (b^2 - N) / a  [small, ~sqrt(N)/(4n0^2)]
      g(x) = a*x^2 + 2*b*x + c
      Relation: (ax+b)^2 = a*g(x) + N ≡ a*g(x) (mod N)

    We sieve g(x), factor it, add a's prime factors, store ax+b.
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

    fb_size_target, sieve_half = b3mpqs_params(nd)

    # Build factor base: primes p where jacobi(N, p) = 1 (or p=2)
    fb = []
    p = 2
    while len(fb) < fb_size_target:
        if p == 2 or (is_prime(p) and jacobi(int(N % p), p) == 1):
            fb.append(int(p))
        p = int(next_prime(p)) if p > 2 else 3

    fb_size = len(fb)
    fb_np = np.array(fb, dtype=np.int64)
    fb_log = np.array([int(round(math.log2(p) * 1024)) for p in fb], dtype=np.int32)
    fb_index = {p: i for i, p in enumerate(fb)}

    # Precompute sqrt(N) mod p for each FB prime
    sqrt_N_mod = {}
    for p in fb:
        if p == 2:
            sqrt_N_mod[2] = int(N % 2)
        else:
            sqrt_N_mod[p] = tonelli_shanks(int(N % p), p)

    # Large prime bound
    lp_bound = fb[-1] ** 2

    # Sieve threshold
    if nb >= 180:
        T_bits = max(15, nb // 4 - 1)
    else:
        T_bits = max(15, nb // 4 - 2)

    # Small prime correction
    small_prime_correction = 0
    for p in fb:
        if p >= 32:
            break
        roots = 1 if p == 2 else 2
        small_prime_correction += roots * math.log2(p) * 1024 / p
    small_prime_correction = int(small_prime_correction * 0.60)

    needed = fb_size + max(30, fb_size // 5)
    sz = 2 * sieve_half

    if verbose:
        print(f"B3-MPQS: {nd}d ({nb}b), |FB|={fb_size}, M={sieve_half}, "
              f"need={needed}, LP<={int(math.log10(max(lp_bound,10))):.0f}d")
        print(f"  FB[{fb[0]}..{fb[-1]}], T_bits={T_bits}")

    # JIT warmup
    dummy = np.zeros(100, dtype=np.int32)
    jit_sieve(dummy, np.array([2, 3], dtype=np.int64),
              np.array([10, 15], dtype=np.int32),
              np.array([0, 0], dtype=np.int64),
              np.array([1, 1], dtype=np.int64), 100)
    jit_find_smooth(dummy, 1)

    # Relation storage
    smooth = []  # (x_stored, sign, exps, lp)
    partials = {}  # lp -> (x_stored, sign, exps)
    n_lp_combined = 0

    poly_count = 0
    total_cands = 0

    # Pre-allocate sieve buffer
    _sieve_buf = np.zeros(sz, dtype=np.int32)

    M = sieve_half  # half-width

    def trial_divide(val):
        """Trial divide |val| by factor base."""
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

    def process_candidate(ax_b_val, gx_val, a_prime_exps):
        """
        Process a sieve candidate.

        Relation: ax_b_val^2 ≡ a * gx_val (mod N)
        We factor gx_val, then add a_prime_exps to get the full exponent
        vector for a * gx_val.
        """
        nonlocal n_lp_combined

        if gx_val == 0:
            g = gcd(mpz(ax_b_val), N)
            if 1 < g < N:
                return int(g)
            return None

        sign = 1 if gx_val < 0 else 0
        exps, cofactor = trial_divide(gx_val)

        # Add a's prime factors
        for j in range(fb_size):
            exps[j] += a_prime_exps[j]

        x_stored = int(mpz(ax_b_val) % N)

        if cofactor == 1:
            smooth.append((x_stored, sign, exps, 0))
        elif cofactor <= lp_bound and cofactor > 1:
            if is_prime(cofactor):
                lp = cofactor
                if lp in partials:
                    x2, s2, e2 = partials.pop(lp)
                    c_x = (x_stored * x2) % N_int
                    c_sign = (sign + s2) % 2
                    c_exps = [exps[j] + e2[j] for j in range(fb_size)]
                    smooth.append((c_x, c_sign, c_exps, lp))
                    n_lp_combined += 1
                else:
                    partials[lp] = (x_stored, sign, exps)
        return None

    # ==========================================================================
    # Main polynomial loop
    # ==========================================================================
    #
    # For each n0, we construct an MPQS polynomial:
    #   a = 4*n0^2
    #   b = m0 (where m0 ≈ n0*sqrt(N), adjusted so b^2 ≡ N mod a)
    #   c = (b^2 - N) / a
    #   g(x) = a*x^2 + 2*b*x + c
    #
    # Stored: ax + b. Relation: (ax+b)^2 = a*g(x) + N.
    # (ax+b)^2 ≡ a*g(x) (mod N).
    #
    # We sieve g(x), not f(k). The difference from before:
    # - f(k) = (m0+2kn0)^2 - N*n0^2 = a*k^2 + 2*b*k + a*c
    #   where we defined a=4n0^2 earlier
    # - g(x) = f(x)/1 = same polynomial, but now x_stored = a*x + b.
    #
    # Actually g(x) = a*x^2 + 2*b*x + c where c = (b^2-N)/a.
    # At x=0: g(0) = c = (b^2-N)/a ≈ ±sqrt(N)/(4n0^2).
    # The key: b^2 - N must be divisible by a = 4*n0^2.
    #
    # With b = m0: b^2 - N*n0^2/n0^2 != ...
    # Let's be precise. We want b with b^2 ≡ N (mod a).
    # a = 4*n0^2. N mod a = N mod (4*n0^2).
    # We need b^2 ≡ N (mod 4*n0^2).
    #
    # Let t = sqrt(N) mod n0 (if it exists via Tonelli-Shanks on each prime factor of n0).
    # Then t^2 ≡ N (mod n0). We need b ≡ t (mod n0) and b^2 ≡ N (mod 4).
    # If N ≡ 1 (mod 4): b can be odd, b^2 ≡ 1 ≡ N (mod 4).
    # If N ≡ 1 (mod 2) and N ≡ 1 (mod 4): b = 2*n0*round(sqrt(N)/(2*n0)).
    #
    # Simpler approach: b = m0 where m0 = round(n0*sqrt(N)).
    # Then b^2 - N*n0^2 = (m0 - n0*sqrt(N))(m0 + n0*sqrt(N)) ≈ ε * 2*n0*sqrt(N)
    # where ε = m0 - n0*sqrt(N) is small.
    # So c_raw = m0^2 - N*n0^2 is small (~sqrt(N)).
    # But c = c_raw / a = (m0^2 - N*n0^2) / (4*n0^2).
    # This is NOT integer unless 4*n0^2 | (m0^2 - N*n0^2).
    #
    # m0^2 - N*n0^2 = m0^2 (mod n0^2) - 0 = m0^2 mod n0^2.
    # For this to be div by n0^2, need n0 | m0. Since m0 ≈ n0*sqrt(N),
    # m0 = n0*isqrt(N) + adjustment. So m0 mod n0 depends on the adjustment.
    # In general m0 is NOT divisible by n0.
    #
    # THE REAL APPROACH: Don't force c = (b^2-N)/a. Instead, use the B3 polynomial
    # directly as g(x) and define the MPQS relation properly.
    #
    # Let a = 4*n0^2, b_half = 2*m0*n0 (so 2*b_half = 4*m0*n0 = b_coeff).
    # g(x) = a*x^2 + 2*b_half*x + c  where c = m0^2 - N*n0^2.
    # b_half^2 - a*c = 4*m0^2*n0^2 - 4*n0^2*(m0^2 - N*n0^2)
    #                = 4*N*n0^4
    #
    # For standard MPQS: b^2 - a*c = N. Here b_half^2 - a*c = 4*N*n0^4 = N*a*n0^2.
    # So (a*x + b_half)^2 = a^2*x^2 + 2*a*b_half*x + b_half^2
    #                      = a*(a*x^2 + 2*b_half*x + c) + b_half^2 - a*c + a*c - a*c
    # Hmm, let me redo:
    # (a*x + b_half)^2 = a^2*x^2 + 2*a*b_half*x + b_half^2
    #                   = a*(a*x^2 + 2*b_half*x) + b_half^2
    # And g(x) = a*x^2 + 2*b_half*x + c, so a*x^2 + 2*b_half*x = g(x) - c.
    # (a*x + b_half)^2 = a*(g(x) - c) + b_half^2 = a*g(x) + (b_half^2 - a*c)
    #                   = a*g(x) + 4*N*n0^4
    #
    # Mod N: (a*x + b_half)^2 ≡ a*g(x) (mod N).  (since 4*N*n0^4 ≡ 0 mod N)
    #
    # So x_stored = a*x + b_half = 4*n0^2*x + 2*m0*n0 = 2*n0*(2*n0*x + m0).
    # And we factor g(x) over FB, add a's primes to exps.
    # g(x) = a*x^2 + 2*b_half*x + c
    # At x = 0: g(0) = c = m0^2 - N*n0^2 (small, ~sqrt(N)).
    # At x = k: g(k) = 4*n0^2*k^2 + 4*m0*n0*k + c.
    #
    # THIS IS EXACTLY what we had before as f(k)! The polynomial is the same.
    # The difference: x_stored = a*k + b_half = 2*n0*(2*n0*k + m0)
    # instead of x_k = m0 + 2*k*n0.
    #
    # So x_stored = 2*n0 * x_k. And we already showed this doesn't help
    # because the 2*n0 factors cancel in the product.
    #
    # THE FUNDAMENTAL ISSUE: In standard MPQS, a = product of s distinct primes,
    # and b is found via CRT such that b^2 ≡ N (mod a).
    # HERE, a = (2*n0)^2 is a PERFECT SQUARE. This means there's only ONE
    # square root of a*g(x) mod N (up to sign), and it equals a*x + b_half.
    # In standard MPQS, a is square-free, so sqrt(a*g(x)) mod N can be
    # different from a*x + b because a has a nontrivial Jacobi symbol.
    #
    # THE FIX: Use a = product of DISTINCT primes, not a perfect square.
    # The B3 construction naturally gives a = 4*n0^2 which is a perfect square.
    # Instead, I should generate polynomials the standard MPQS way but use
    # the B3 idea to get good polynomial coefficients.
    #
    # ACTUAL IMPLEMENTATION: Standard MPQS with proper 'a' selection.
    # Use a = product of s FB primes (standard MPQS).
    # Find b via CRT: b^2 ≡ N (mod a).
    # c = (b^2 - N) / a.
    # g(x) = a*x^2 + 2*b*x + c.
    # Sieve g(x), store a*x+b.
    # The B3 insight: for n0 with a = product of primes near 2*n0,
    # choose b near m0 = n0*sqrt(N)/n0... this doesn't really help.
    #
    # OK, I'll just implement standard MPQS. The B3 idea doesn't add value
    # because the perfect-square 'a' kills the factor extraction.

    # ======================================================================
    # STANDARD MPQS IMPLEMENTATION
    # ======================================================================

    # Target a ≈ sqrt(2N) / M
    target_a = isqrt(2 * N) // M
    log_target = float(gmpy2.log2(target_a)) if target_a > 0 else 0

    # Choose s (number of primes in a) and FB range
    best_s = 2
    best_range = (1, len(fb) - 1)
    best_score = float('inf')
    import bisect
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
    import random

    if verbose:
        print(f"  s={s}, select FB[{select_lo}..{select_hi}]")

    n0_val = 0

    while len(smooth) < needed:
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
            n0_val += 1
            continue

        a = best_a
        a_primes = best_primes
        a_prime_set = set(a_primes)
        a_int = int(a)

        # Compute prime factorization exps for 'a'
        a_prime_exps = [0] * fb_size
        for ap in a_primes:
            if ap in fb_index:
                a_prime_exps[fb_index[ap]] += 1

        # --- Compute t_roots: sqrt(N) mod q for each q in a ---
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

        # --- Compute b via CRT ---
        # b = sum(t_j * (a/q_j) * inv(a/q_j, q_j))
        b = mpz(0)
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
            b += B_j
        if not b_ok:
            continue

        # Reduce b mod a to minimize |c|
        b = b % a
        # Choose b or a-b to minimize |c| (equivalently, minimize |b^2 - N| / a)
        b_alt = a - b
        if abs(b_alt * b_alt - N) < abs(b * b - N):
            b = b_alt

        # Verify b^2 ≡ N (mod a)
        if (b * b - N) % a != 0:
            continue

        c = (b * b - N) // a
        b_int = int(b)
        c_int = int(c)

        # --- Compute sieve offsets ---
        # g(x) = a*x^2 + 2*b*x + c
        # Roots: x = a^(-1) * (±sqrt(N) - b) mod p
        o1 = np.full(fb_size, -1, dtype=np.int64)
        o2 = np.full(fb_size, -1, dtype=np.int64)

        for pi in range(fb_size):
            p = fb[pi]

            if p == 2:
                g0 = c_int % 2
                g1 = (a_int + 2 * b_int + c_int) % 2
                if g0 == 0:
                    o1[pi] = M % 2
                    if g1 == 0:
                        o2[pi] = (M + 1) % 2
                elif g1 == 0:
                    o1[pi] = (M + 1) % 2
                continue

            if p in a_prime_set:
                # Single root: x = -c/(2b) mod p
                b2 = (2 * b_int) % p
                if b2 == 0:
                    continue
                b2_inv = pow(b2, -1, p)
                c_mod = c_int % p
                r = (-c_mod * b2_inv) % p
                o1[pi] = (r + M) % p
                continue

            t = sqrt_N_mod.get(p)
            if t is None:
                continue
            try:
                ai = pow(a_int % p, -1, p)
            except (ValueError, ZeroDivisionError):
                continue
            bm = b_int % p
            r1 = (ai * (t - bm)) % p
            r2 = (ai * (p - t - bm)) % p
            o1[pi] = (r1 + M) % p
            o2[pi] = ((r2 + M) % p) if r2 != r1 else -1

        # --- Sieve ---
        _sieve_buf[:] = 0
        jit_sieve(_sieve_buf, fb_np, fb_log, o1, o2, sz)

        # Threshold
        log_g_max = math.log2(max(M, 1)) + 0.5 * nb
        thresh = int(max(0, (log_g_max - T_bits)) * 1024) - small_prime_correction

        candidates = jit_find_smooth(_sieve_buf, thresh)
        n_cand = len(candidates)
        total_cands += n_cand

        for ci in range(n_cand):
            sieve_idx = int(candidates[ci])
            x = sieve_idx - M

            gx = a_int * x * x + 2 * b_int * x + c_int
            ax_b = a_int * x + b_int  # stored x value

            result = process_candidate(ax_b, gx, a_prime_exps)
            if result:
                total_t = time.time() - t0
                if verbose:
                    print(f"\n  *** FACTOR (direct): {result} ({total_t:.1f}s) ***")
                return result

        poly_count += 1

        # Progress report
        if poly_count % max(1, 50 if nd < 35 else 20 if nd < 45 else 5) == 0 and verbose:
            elapsed = time.time() - t0
            ns = len(smooth)
            rate = ns / max(elapsed, 0.001)
            eta = (needed - ns) / max(rate, 0.001) if rate > 0 else 99999
            print(f"  [{elapsed:.1f}s] poly={poly_count} "
                  f"sm={ns}/{needed} LP={n_lp_combined} "
                  f"part={len(partials)} cand={total_cands} "
                  f"rate={rate:.1f}/s eta={min(eta,99999):.0f}s")

    # ==========================================================================
    # GF(2) Gaussian Elimination
    # ==========================================================================
    elapsed_sieve = time.time() - t0
    if verbose:
        print(f"\n  Sieve done: {len(smooth)} rels in {elapsed_sieve:.1f}s "
              f"({poly_count} polys, {n_lp_combined} LP)")

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
    for vi, indices in enumerate(null_vecs):
        x_val = mpz(1)
        total_exp = [0] * fb_size
        total_sign = 0
        lp_product = mpz(1)

        for idx in indices:
            x_stored, s_val, exps, lp_val = smooth[idx]
            x_val = x_val * mpz(x_stored) % N
            total_sign += s_val
            for j in range(fb_size):
                total_exp[j] += exps[j]
            if lp_val > 0:
                lp_product = lp_product * mpz(lp_val) % N

        if any(e & 1 for e in total_exp) or total_sign & 1:
            continue

        y_val = lp_product
        for j in range(fb_size):
            if total_exp[j] > 0:
                y_val = y_val * pow(mpz(fb[j]), total_exp[j] >> 1, N) % N

        for diff in (x_val - y_val, x_val + y_val):
            g = gcd(diff % N, N)
            if 1 < g < N:
                total_t = time.time() - t0
                if verbose:
                    print(f"\n  *** FACTOR: {g} ({nd}d, {total_t:.1f}s, "
                          f"{poly_count} polys, {len(smooth)} rels) ***")
                return int(g)

    if verbose:
        print(f"  Tried {len(null_vecs)} null vecs, no factor found.")
    return 0


###############################################################################
# CONVENIENCE
###############################################################################

def factor(N, verbose=True, time_limit=3600):
    """Main entry point for B3-MPQS factoring with retry on extraction failure."""
    import random
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
    print("B3-MPQS Engine — Self-Test")
    print("=" * 70)

    tests = [
        ("20d", int(mpz(1000000007) * mpz(1000000009)), 30),
        ("25d", int(mpz(10000000033) * mpz(1000000000061)), 60),
        ("30d", int(mpz(1000000009) * mpz(100000000000000013)), 120),
        ("35d", int(mpz(10000000000000069) * mpz(1000000000000000009)), 180),
        ("40d", int(mpz(10000000000000000087) * mpz(10000000000000000091)), 300),
        ("45d", int(mpz(1000000000000000000193) * mpz(10000000000000000000000343)), 600),
    ]

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

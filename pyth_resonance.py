#!/usr/bin/env python3
"""
B3-MPQS Engine — C-Accelerated MPQS with Sieve + Trial Division in C
=====================================================================

Standard MPQS with:
  - C sieve kernel (mpqs_sieve_c.so)
  - C batch trial division with __int128 support
  - Single Large Prime variation
  - GF(2) Gaussian elimination

The C extension handles the two hottest loops:
  1. Sieve: add log(p) contributions at arithmetic progressions
  2. Trial division: divide all candidates by all FB primes

For residues up to 128 bits (~38 digits), C handles everything.
For larger residues (55d+ semiprimes), Python pre-reduces by small primes,
then C handles the rest.
"""

import gmpy2
from gmpy2 import mpz, isqrt, is_prime, gcd, jacobi, next_prime, iroot
import numpy as np
import ctypes
import time
import math
import os
import bisect
import random

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
        # Try to compile
        c_path = so_path.replace('.so', '.c')
        if os.path.exists(c_path):
            os.system(f'gcc -O3 -march=native -shared -fPIC -o {so_path} {c_path} -lm')
    if not os.path.exists(so_path):
        raise RuntimeError(f"Cannot find {so_path}")
    lib = ctypes.CDLL(so_path)

    # sieve_poly
    lib.sieve_poly.restype = None
    lib.sieve_poly.argtypes = [
        ctypes.POINTER(ctypes.c_uint16),   # sieve
        ctypes.c_int,                      # sz
        ctypes.POINTER(ctypes.c_int),      # fb_primes
        ctypes.POINTER(ctypes.c_int),      # fb_offsets1
        ctypes.POINTER(ctypes.c_int),      # fb_offsets2
        ctypes.POINTER(ctypes.c_uint16),   # fb_logp
        ctypes.c_int,                      # n_fb
    ]

    # find_survivors
    lib.find_survivors.restype = ctypes.c_int
    lib.find_survivors.argtypes = [
        ctypes.POINTER(ctypes.c_uint16),   # sieve
        ctypes.c_int,                      # sz
        ctypes.c_int,                      # threshold
        ctypes.POINTER(ctypes.c_int),      # out_indices
        ctypes.c_int,                      # max_out
    ]

    # trial_divide_batch
    lib.trial_divide_batch.restype = ctypes.c_int
    lib.trial_divide_batch.argtypes = [
        ctypes.POINTER(ctypes.c_int64),    # gx_hi
        ctypes.POINTER(ctypes.c_int64),    # gx_lo
        ctypes.c_int,                      # n_cand
        ctypes.POINTER(ctypes.c_int),      # fb_primes
        ctypes.c_int,                      # n_fb
        ctypes.c_int64,                    # lp_bound
        ctypes.POINTER(ctypes.c_int),      # out_exponents (flat n_cand*n_fb)
        ctypes.POINTER(ctypes.c_int64),    # out_cofactors
        ctypes.POINTER(ctypes.c_int),      # out_signs
        ctypes.POINTER(ctypes.c_int),      # out_status
        ctypes.POINTER(ctypes.c_int),      # out_n_smooth
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
    # C reconstructs as: (i128)hi << 64 | (u128)(uint64_t)lo
    # For negative values, we use two's complement 128-bit representation
    MASK64 = (1 << 64) - 1
    if val >= 0:
        lo = val & MASK64
        hi = (val >> 64) & MASK64
    else:
        # Two's complement: treat as unsigned 128-bit, then split
        val128 = val & ((1 << 128) - 1)  # 128-bit two's complement
        lo = val128 & MASK64
        hi = (val128 >> 64) & MASK64
    # Convert to signed int64 range for ctypes
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
        (60,  4500, 1500000),
        (65,  5500, 3000000),
        (70,  7000, 5000000),
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
# MAIN B3-MPQS ENGINE
###############################################################################

def b3mpqs_factor(N, verbose=True, time_limit=3600):
    """
    Factor N using standard MPQS with C-accelerated sieve and trial division.
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

    # Build factor base: primes p where jacobi(N, p) = 1 (or p=2)
    fb = []
    p = 2
    while len(fb) < fb_size_target:
        if p == 2 or (is_prime(p) and jacobi(int(N % p), p) == 1):
            fb.append(int(p))
        p = int(next_prime(p)) if p > 2 else 3

    fb_size = len(fb)
    fb_index = {p: i for i, p in enumerate(fb)}

    # C arrays for factor base
    c_fb_primes = (ctypes.c_int * fb_size)(*fb)
    # Log scale: log2(p) * 16, fits in uint16 comfortably
    LOG_SCALE = 16
    fb_logp_vals = [max(1, int(round(math.log2(p) * LOG_SCALE))) for p in fb]
    c_fb_logp = (ctypes.c_uint16 * fb_size)(*fb_logp_vals)

    # Precompute sqrt(N) mod p for each FB prime
    sqrt_N_mod = {}
    for p in fb:
        if p == 2:
            sqrt_N_mod[2] = int(N % 2)
        else:
            sqrt_N_mod[p] = tonelli_shanks(int(N % p), p)

    # Large prime bound: fb[-1]^2 gives huge LP space; cap reasonably
    lp_bound = min(fb[-1] ** 2, fb[-1] * 100)

    # Sieve threshold
    if nb >= 180:
        T_bits = max(15, nb // 4 - 1)
    else:
        T_bits = max(15, nb // 4 - 2)

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

    if verbose:
        print(f"B3-MPQS{'(C)' if use_c else ''}: {nd}d ({nb}b), |FB|={fb_size}, M={M}, "
              f"need={needed}, LP<={int(math.log10(max(lp_bound,10))):.0f}d")
        print(f"  FB[{fb[0]}..{fb[-1]}], T_bits={T_bits}")

    # Relation storage
    smooth = []  # (x_stored, sign, exps, lp)
    partials = {}  # lp -> (x_stored, sign, exps)
    n_lp_combined = 0

    poly_count = 0
    total_cands = 0

    # Pre-allocate C buffers
    if use_c:
        c_sieve = (ctypes.c_uint16 * sz)()
        max_survivors = min(sz, 100000)
        c_survivors = (ctypes.c_int * max_survivors)()
        c_offsets1 = (ctypes.c_int * fb_size)()
        c_offsets2 = (ctypes.c_int * fb_size)()
        # Trial division output buffers (reusable, sized for max batch)
        td_max = max_survivors
        c_gx_hi = (ctypes.c_int64 * td_max)()
        c_gx_lo = (ctypes.c_int64 * td_max)()
        c_td_exps = (ctypes.c_int * (td_max * fb_size))()
        c_td_cofactors = (ctypes.c_int64 * td_max)()
        c_td_signs = (ctypes.c_int * td_max)()
        c_td_status = (ctypes.c_int * td_max)()
        c_td_n_smooth = (ctypes.c_int * 1)()

    # ======================================================================
    # STANDARD MPQS IMPLEMENTATION
    # ======================================================================

    # Target a ~ sqrt(2N) / M
    target_a = isqrt(2 * N) // M
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

    if verbose:
        print(f"  s={s}, select FB[{select_lo}..{select_hi}]")

    # g(x) values: max |g(x)| ~ a*M^2 + 2*b*M + |c|
    # Most candidates are near center where |g(x)| is much smaller.
    # We always try C trial division; for individual values > 127 bits,
    # we fall back to Python per-candidate.
    gx_max_bits = int(log_target + 2 * math.log2(max(M, 1))) + 10
    can_use_c_td = use_c  # Always try C; Python fallback per-candidate if overflow
    if verbose and use_c:
        print(f"  g(x) max ~{gx_max_bits}b, C trial div: yes")

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

        b = b % a
        b_alt = a - b
        if abs(b_alt * b_alt - N) < abs(b * b - N):
            b = b_alt

        if (b * b - N) % a != 0:
            continue

        c = (b * b - N) // a
        b_int = int(b)
        c_int = int(c)

        # --- Compute sieve offsets ---
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
                    try:
                        ai = pow(a_int % p, -1, p)
                    except (ValueError, ZeroDivisionError):
                        pass
                    else:
                        bm = b_int % p
                        r1 = (ai * (t - bm)) % p
                        r2 = (ai * (p - t - bm)) % p
                        o1_val = (r1 + M) % p
                        o2_val = ((r2 + M) % p) if r2 != r1 else -1

            if use_c:
                c_offsets1[pi] = o1_val
                c_offsets2[pi] = o2_val

        # --- Sieve (C or Python fallback) ---
        if use_c:
            ctypes.memset(c_sieve, 0, sz * 2)  # uint16 = 2 bytes each
            clib.sieve_poly(c_sieve, sz, c_fb_primes, c_offsets1, c_offsets2,
                           c_fb_logp, fb_size)

            # Threshold (in log2*LOG_SCALE scale)
            log_g_max = math.log2(max(M, 1)) + 0.5 * nb
            thresh = int(max(0, (log_g_max - T_bits)) * LOG_SCALE) - small_prime_correction
            thresh = max(1, thresh)

            n_surv = clib.find_survivors(c_sieve, sz, thresh, c_survivors, max_survivors)
        else:
            # Python fallback (shouldn't happen normally)
            n_surv = 0

        if n_surv == 0:
            poly_count += 1
            continue

        total_cands += n_surv

        # --- Compute g(x) and ax+b for each survivor ---
        # Batch: compute all g(x) values, encode for C trial division
        gx_list = []
        axb_list = []
        surv_indices = []

        for ci in range(n_surv):
            sieve_idx = c_survivors[ci] if use_c else 0
            x = sieve_idx - M
            gx = a_int * x * x + 2 * b_int * x + c_int
            ax_b = a_int * x + b_int
            gx_list.append(gx)
            axb_list.append(ax_b)
            surv_indices.append(sieve_idx)

        # --- Batch trial division ---
        n_cand = len(gx_list)

        if can_use_c_td and n_cand > 0:
            # Split candidates: those fitting in 127 bits go to C, rest to Python
            c_indices = []
            py_indices = []
            MAX_128 = (1 << 127) - 1
            for ci in range(n_cand):
                gx = gx_list[ci]
                if gx == 0:
                    g = gcd(mpz(axb_list[ci]), N)
                    if 1 < g < N:
                        total_t = time.time() - t0
                        if verbose:
                            print(f"\n  *** FACTOR (direct): {g} ({total_t:.1f}s) ***")
                        return int(g)
                elif -MAX_128 <= gx <= MAX_128:
                    c_indices.append(ci)
                else:
                    py_indices.append(ci)

            # C batch trial division for candidates that fit in 128 bits
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

                    x_stored = int(mpz(ax_b) % N)

                    if status == 1:
                        smooth.append((x_stored, sign, exps, 0))
                    elif status == 2:
                        lp = int(cofactor)
                        if lp in partials:
                            x2, s2, e2 = partials.pop(lp)
                            c_x = (x_stored * x2) % N_int
                            c_sign = (sign + s2) % 2
                            c_exps = [exps[j] + e2[j] for j in range(fb_size)]
                            smooth.append((c_x, c_sign, c_exps, lp))
                            n_lp_combined += 1
                        else:
                            partials[lp] = (x_stored, sign, exps)

            # Python fallback for overflow candidates
            for ci in py_indices:
                gx = gx_list[ci]
                ax_b = axb_list[ci]
                sign = 1 if gx < 0 else 0
                exps, cofactor = _py_trial_divide(gx, fb, fb_size)
                for j in range(fb_size):
                    exps[j] += a_prime_exps[j]
                x_stored = int(mpz(ax_b) % N)
                if cofactor == 1:
                    smooth.append((x_stored, sign, exps, 0))
                elif 1 < cofactor <= lp_bound:
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

        else:
            # Python fallback for large g(x) or no C lib
            for ci in range(n_cand):
                gx = gx_list[ci]
                ax_b = axb_list[ci]

                if gx == 0:
                    g = gcd(mpz(ax_b), N)
                    if 1 < g < N:
                        total_t = time.time() - t0
                        if verbose:
                            print(f"\n  *** FACTOR (direct): {g} ({total_t:.1f}s) ***")
                        return int(g)
                    continue

                sign = 1 if gx < 0 else 0
                exps, cofactor = _py_trial_divide(gx, fb, fb_size)

                for j in range(fb_size):
                    exps[j] += a_prime_exps[j]

                x_stored = int(mpz(ax_b) % N)

                if cofactor == 1:
                    smooth.append((x_stored, sign, exps, 0))
                elif 1 < cofactor <= lp_bound:
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
    print("B3-MPQS Engine (C-accelerated) — Self-Test")
    print("=" * 70)

    from gmpy2 import mpz, next_prime

    rng = random.Random(42)

    tests = []
    for nd in [48, 50, 53, 55, 58, 60, 63, 66]:
        half_bits = int(nd * 3.32 / 2)
        p = int(next_prime(mpz(rng.getrandbits(half_bits)) | (mpz(1) << (half_bits - 1))))
        q = int(next_prime(mpz(rng.getrandbits(half_bits)) | (mpz(1) << (half_bits - 1))))
        N = p * q
        actual_nd = len(str(N))
        limit = max(30, nd * 10)
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

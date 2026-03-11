#!/usr/bin/env python3
"""
THE RESONANCE SIEVE v7.0
==========================
Unified Geometric Engine: VSDD Sniper + Super-Generator + SIQS/GNFS + ECM

Routing strategy by digit count:
  < 20d:   Trial division / VSDD
  20-45d:  ECM (good for unbalanced) + VSDD Sniper
  45-100d: SIQS (primary) with ECM fallback
  > 100d:  GNFS scaffold (placeholder), falls back to SIQS

Budget allocation:
  Path 1 (VSDD + Super-Generator): 10% of time
  ECM:                              20% of time
  Path 2 (SIQS):                    70% of time
"""

import gmpy2
from gmpy2 import mpz, isqrt, is_prime, gcd, jacobi, next_prime
import numpy as np
import time
import math
import random

from rsa_targets import *

# ---------------------------------------------------------------------------
# Optional imports: SIQS engine, Super-Generator v7
# Fall back to inline MPQS / VSDD if not available yet.
# ---------------------------------------------------------------------------
_have_siqs = False
_have_supergen = False

try:
    from siqs_engine import siqs_factor
    _have_siqs = True
except ImportError:
    pass

try:
    from super_generator_v7 import super_generator_search
    _have_supergen = True
except ImportError:
    pass

# We always need numba for the inline MPQS fallback
try:
    from numba import njit
    _have_numba = True
except ImportError:
    _have_numba = False


###############################################################################
# PATH 1: THE VSDD FERMAT SNIPER  (inline, copied from v5.0)
###############################################################################

def vsdd_sniper(n, verbose=True, time_limit=60):
    """
    VSDD Fermat Sniper: For each delta, check if B = (n - delta^2)/(2*delta)
    is integer. If yes: factors are delta and (2B + delta).

    Uses resonance bands (beat frequency envelope) to jump to
    high-probability delta values instead of scanning linearly.
    """
    n = mpz(n)
    nb = int(gmpy2.log2(n)) + 1
    sqrt_n = isqrt(n)

    if verbose:
        print(f"  VSDD Sniper: {len(str(int(n)))}d ({nb}b)")

    t0 = time.time()
    checked = 0

    # Modular pre-filter
    filter_primes = [3, 5, 7, 8, 9, 11, 13, 16, 17, 19, 23, 29, 31]
    n_residues = {p: int(n % p) for p in filter_primes}

    # Phase A: Small factor trial (odd numbers up to 10^6)
    if n % 2 == 0:
        return 2

    delta = mpz(3)
    while delta * delta <= n and delta < 1000000:
        if time.time() - t0 > time_limit:
            break
        if n % delta == 0:
            if verbose:
                print(f"    Trial: delta={delta} ({time.time()-t0:.3f}s)")
            return int(delta)
        delta += 2
        checked += 1

    if verbose:
        print(f"    Trial phase: checked {checked} ({time.time()-t0:.1f}s)")

    # Phase B: Resonance gradient jumping
    for k in range(1, min(100000, int(sqrt_n) + 1)):
        if time.time() - t0 > time_limit:
            break

        delta_center = isqrt(n // k) if k > 0 else sqrt_n
        window = max(1, min(100, int(delta_center) // (2 * k + 1)))

        for offset in range(-window, window + 1):
            delta = delta_center + offset
            if delta < 2 or delta * delta > n:
                continue
            checked += 1

            numerator = n - delta * delta
            denominator = 2 * delta

            if numerator > 0 and numerator % denominator == 0:
                B = numerator // denominator
                factor1 = delta
                factor2 = 2 * B + delta
                if factor1 * factor2 == n:
                    elapsed = time.time() - t0
                    if verbose:
                        print(f"    HIT: delta={factor1}, (2B+delta)={factor2} ({elapsed:.3f}s)")
                    return int(min(factor1, factor2))

    elapsed = time.time() - t0
    if verbose:
        print(f"    No hit after {checked} checks ({elapsed:.1f}s)")
    return None


###############################################################################
# PATH 2: GUILLOTINE MPQS  (inline fallback when siqs_engine unavailable)
###############################################################################

def tonelli_shanks(n, p):
    n = n % p
    if n == 0: return 0
    if p == 2: return n
    if pow(n, (p - 1) // 2, p) != 1: return None
    q, s = p - 1, 0
    while q % 2 == 0: q //= 2; s += 1
    if s == 1: return pow(n, (p + 1) // 4, p)
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1: z += 1
    m, c, t, r = s, pow(z, q, p), pow(n, q, p), pow(n, (q + 1) // 2, p)
    while True:
        if t == 1: return r
        i, tmp = 1, t * t % p
        while tmp != 1: tmp = tmp * tmp % p; i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m, c, t, r = i, b * b % p, t * b * b % p, r * b % p


if _have_numba:
    @njit(cache=True)
    def jit_sieve(sieve_arr, primes, logs, offsets1, offsets2, sz):
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
else:
    def jit_sieve(sieve_arr, primes, logs, offsets1, offsets2, sz):
        for i in range(len(primes)):
            p = int(primes[i])
            lp = int(logs[i])
            o1 = int(offsets1[i])
            o2 = int(offsets2[i])
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

    def jit_find_smooth(sieve_arr, threshold):
        return np.where(sieve_arr >= threshold)[0].astype(np.int64)


def mpqs_params(nd):
    tbl = [
        (20,   80,    20000),
        (25,  150,    40000),
        (30,  250,    80000),
        (35,  450,   150000),
        (40,  800,   300000),
        (45, 1200,   500000),
        (50, 3000,  1000000),
        (55, 4500,  1500000),
        (60, 6500,  2500000),
        (65, 7000,  4000000),
        (70,10000,  6000000),
        (75,15000,  8000000),
        (80,22000, 12000000),
        (85,32000, 16000000),
        (90,45000, 22000000),
        (95,60000, 28000000),
        (100,80000, 35000000),
    ]
    for i in range(len(tbl) - 1):
        if tbl[i][0] <= nd < tbl[i + 1][0]:
            frac = (nd - tbl[i][0]) / (tbl[i + 1][0] - tbl[i][0])
            fb = int(tbl[i][1] + frac * (tbl[i + 1][1] - tbl[i][1]))
            M = int(tbl[i][2] + frac * (tbl[i + 1][2] - tbl[i][2]))
            return fb, M
    if nd <= tbl[0][0]: return tbl[0][1], tbl[0][2]
    return tbl[-1][1], tbl[-1][2]


def guillotine_mpqs(n, verbose=True, time_limit=3600):
    """
    Guillotine MPQS: Multiple Polynomial Quadratic Sieve with RNS pre-filter.
    Core: sieve g(x) = a*x^2 + 2*b*x + c  where c = (b^2 - n) / a
    Relation: (ax+b)^2 === a*g(x) (mod n)
    """
    import bisect

    n = mpz(n)
    nd = len(str(n))
    nb = int(gmpy2.log2(n)) + 1

    fb_size, M = mpqs_params(nd)

    if verbose:
        print(f"  MPQS: {nd}d ({nb}b), FB={fb_size}, M={M}")

    t0 = time.time()

    # Factor Base
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
        print(f"    FB[{fb[0]}..{fb[-1]}] ({time.time()-t0:.1f}s)")

    sqrt_n_mod = {}
    for p in fb:
        if p == 2:
            sqrt_n_mod[2] = int(n % 2)
        else:
            sqrt_n_mod[p] = tonelli_shanks(int(n % p), p)

    sqrt_n = isqrt(n)
    if sqrt_n * sqrt_n < n:
        sqrt_n += 1
    if sqrt_n * sqrt_n == n:
        return int(sqrt_n)

    smooth = []
    partials = {}
    needed = fb_size + 20
    lp_bound = fb[-1] ** 2
    # T_bits = nb//4 — critical parameter, do NOT change
    T_bits = max(15, nb // 4)

    if verbose:
        print(f"    Need {needed} rels, T_bits={T_bits}")

    # JIT warmup
    dummy = np.zeros(100, dtype=np.int32)
    jit_sieve(dummy, np.array([2, 3], dtype=np.int64),
              np.array([10, 15], dtype=np.int32),
              np.array([0, 0], dtype=np.int64),
              np.array([1, 1], dtype=np.int64), 100)
    jit_find_smooth(dummy, 1)

    poly_count = 0
    total_cands = 0

    def trial_divide(val):
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

    def store_relation(ax_b_val, gx_val, a_prime_indices):
        if gx_val == 0:
            g = gcd(mpz(ax_b_val), n)
            if 1 < g < n:
                return int(g)
            return None

        sign = 1 if gx_val < 0 else 0
        exps, remainder = trial_divide(gx_val)

        for idx in a_prime_indices:
            exps[idx] += 1

        x_stored = int(mpz(ax_b_val) % n)

        if remainder == 1:
            smooth.append((x_stored, sign, exps))
        elif remainder < lp_bound and gmpy2.is_prime(remainder):
            remainder = int(remainder)
            if remainder in partials:
                ox, os, oe = partials[remainder]
                # v_inv partial combining: cax = ax1*ax2*pow(v,-1,n) % n
                try:
                    v_inv = pow(remainder, -1, int(n))
                except (ValueError, ZeroDivisionError):
                    g = gcd(mpz(remainder), n)
                    if 1 < g < n:
                        return int(g)
                    return None
                cax = ox * x_stored % int(n)
                cax = cax * v_inv % int(n)
                cs = (os + sign) % 2
                ce = [oe[j] + exps[j] for j in range(fb_size)]
                smooth.append((cax, cs, ce))
            else:
                partials[remainder] = (x_stored, sign, exps)
        return None

    # Phase 1: Simple QS near sqrt(n)
    if verbose:
        print(f"\n    Phase 1: Simple QS")

    simple_M = min(M, 200000) if nd > 45 else M

    off1 = np.full(fb_size, -1, dtype=np.int64)
    off2 = np.full(fb_size, -1, dtype=np.int64)
    for pi, p in enumerate(fb):
        if p == 2:
            off1[pi] = (1 - int(sqrt_n % 2)) % 2
            continue
        t = sqrt_n_mod.get(p)
        if t is None: continue
        sn_p = int(sqrt_n % p)
        r1 = (t - sn_p) % p
        r2 = (p - t - sn_p) % p
        off1[pi] = r1
        off2[pi] = r2 if r2 != r1 else -1

    sieve = np.zeros(simple_M, dtype=np.int32)
    jit_sieve(sieve, fb_np, fb_log, off1, off2, simple_M)
    log_q = math.log2(float(2 * sqrt_n)) + math.log2(max(simple_M, 1))
    thresh = int(max(0, (log_q - T_bits)) * 1024)
    candidates = jit_find_smooth(sieve, thresh)
    total_cands += len(candidates)

    for ci in range(len(candidates)):
        x = int(candidates[ci])
        ax = sqrt_n + x
        Q = int(ax * ax - n)
        result = store_relation(int(ax), Q, [])
        if result: return result

    # Negative side
    off1n = np.full(fb_size, -1, dtype=np.int64)
    off2n = np.full(fb_size, -1, dtype=np.int64)
    for pi, p in enumerate(fb):
        if p == 2:
            off1n[pi] = int(sqrt_n % 2)
            continue
        t = sqrt_n_mod.get(p)
        if t is None: continue
        sn_p = int(sqrt_n % p)
        r1 = (t - sn_p) % p
        r2 = (p - t - sn_p) % p
        off1n[pi] = (-r1 - 1) % p
        off2n[pi] = ((-r2 - 1) % p) if r2 != r1 else -1

    sieve_neg = np.zeros(simple_M, dtype=np.int32)
    jit_sieve(sieve_neg, fb_np, fb_log, off1n, off2n, simple_M)
    candidates_neg = jit_find_smooth(sieve_neg, thresh)
    total_cands += len(candidates_neg)

    for ci in range(len(candidates_neg)):
        j = int(candidates_neg[ci])
        x = -(j + 1)
        ax = sqrt_n + x
        Q = int(ax * ax - n)
        result = store_relation(int(ax), Q, [])
        if result: return result

    poly_count += 1

    if verbose:
        print(f"      {len(smooth)} smooth, {len(partials)} partial ({time.time()-t0:.1f}s)")

    # Phase 2: MPQS with multiple polynomials
    if len(smooth) < needed:
        if verbose:
            print(f"\n    Phase 2: MPQS")

        target_a = isqrt(2 * n) // M
        log_target = float(gmpy2.log2(target_a)) if target_a > 0 else 0

        # Dynamic s-selection using bisect
        best_s = 2
        best_range = (1, len(fb) - 1)
        best_score = float('inf')
        for s_try in range(2, 16):
            ideal_log = log_target / s_try
            ideal_prime = int(2 ** ideal_log)
            mid = bisect.bisect_left(fb, ideal_prime)
            lo = max(1, mid - s_try * 5)
            hi = min(len(fb) - 1, mid + s_try * 5)
            if hi - lo < s_try + 2:
                continue
            actual_median = fb[min(max(mid, lo), hi)]
            score = abs(math.log2(actual_median) - ideal_log)
            if score < best_score:
                best_score = score
                best_s = s_try
                best_range = (lo, hi)

        s = best_s
        select_lo, select_hi = best_range

        if verbose:
            print(f"      target_a ~ 10^{len(str(int(target_a)))}, s={s}")

        for poly_iter in range(200000):
            if len(smooth) >= needed or time.time() - t0 > time_limit:
                break

            best_a = None
            best_diff = float('inf')
            for _ in range(20):
                indices = sorted(random.sample(range(select_lo, select_hi), s))
                a = mpz(1)
                for i in indices:
                    a *= fb[i]
                diff = abs(float(gmpy2.log2(a) - log_target))
                if diff < best_diff:
                    best_diff = diff
                    best_a = a
                    best_primes = [fb[i] for i in indices]

            a = best_a
            a_primes = best_primes
            a_prime_idx = [fb_index[ap] for ap in a_primes]
            a_prime_set = set(a_primes)

            t_roots = []
            ok = True
            for q in a_primes:
                t = sqrt_n_mod.get(q)
                if t is None: ok = False; break
                t_roots.append(t)
            if not ok: continue

            for sign_combo in range(1 << (s - 1)):
                if len(smooth) >= needed or time.time() - t0 > time_limit:
                    break

                signs = [1]
                for bit in range(s - 1):
                    signs.append(-1 if (sign_combo >> bit) & 1 else 1)

                b = mpz(0)
                bad = False
                for i in range(s):
                    q = a_primes[i]
                    t = (t_roots[i] * signs[i]) % q
                    Ai = a // q
                    try:
                        Ai_inv = pow(int(Ai % q), -1, q)
                    except (ValueError, ZeroDivisionError):
                        bad = True; break
                    b = (b + mpz(t) * Ai * mpz(Ai_inv)) % a

                if bad or (b * b - n) % a != 0:
                    continue

                c = (b * b - n) // a
                a_int = int(a)
                b_int = int(b)

                sz = 2 * M
                o1 = np.full(fb_size, -1, dtype=np.int64)
                o2 = np.full(fb_size, -1, dtype=np.int64)

                for pi in range(fb_size):
                    p = fb[pi]
                    if p == 2:
                        g0 = int(c % 2)
                        g1 = int((a + 2 * b + c) % 2)
                        if g0 == 0:
                            o1[pi] = M % 2
                            if g1 == 0: o2[pi] = (M + 1) % 2
                        elif g1 == 0:
                            o1[pi] = (M + 1) % 2
                        continue

                    if p in a_prime_set:
                        b2 = (2 * b_int) % p
                        if b2 == 0: continue
                        b2_inv = pow(b2, -1, p)
                        c_mod = int(c % p)
                        r = (-c_mod * b2_inv) % p
                        o1[pi] = (r + M) % p
                        continue

                    t = sqrt_n_mod.get(p)
                    if t is None: continue
                    a_inv = pow(a_int % p, -1, p)
                    b_mod = b_int % p
                    r1 = (a_inv * (t - b_mod)) % p
                    r2 = (a_inv * (p - t - b_mod)) % p
                    o1[pi] = (r1 + M) % p
                    o2[pi] = ((r2 + M) % p) if r2 != r1 else -1

                sieve = np.zeros(sz, dtype=np.int32)
                jit_sieve(sieve, fb_np, fb_log, o1, o2, sz)

                log_g_max = math.log2(max(M, 1)) + 0.5 * nb
                thresh = int(max(0, (log_g_max - T_bits)) * 1024)
                candidates = jit_find_smooth(sieve, thresh)
                total_cands += len(candidates)

                for ci in range(len(candidates)):
                    x = int(candidates[ci]) - M
                    ax_b = int(a * x + b)
                    gx = a_int * x * x + 2 * b_int * x + int(c)
                    result = store_relation(ax_b, gx, a_prime_idx)
                    if result: return result

                poly_count += 1

            if poly_count > 0 and poly_count % max(1, 20 if nd < 60 else 5) == 0 and verbose:
                elapsed = time.time() - t0
                rate = len(smooth) / max(elapsed, 0.001)
                eta = (needed - len(smooth)) / max(rate, 0.001) if rate > 0 else 99999
                print(f"      [{elapsed:.0f}s] poly={poly_count} sm={len(smooth)}/{needed} "
                      f"part={len(partials)} cand={total_cands} "
                      f"rate={rate:.1f}/s eta={min(eta,99999):.0f}s")

    elapsed = time.time() - t0
    if len(smooth) < fb_size + 1:
        if verbose:
            print(f"\n    Insufficient: {len(smooth)}/{needed} ({elapsed:.1f}s)")
        return None

    # GF(2) Gaussian Elimination
    if verbose:
        print(f"\n    LA: {len(smooth)} x {fb_size+1}")

    la_t0 = time.time()
    nrows = len(smooth)
    ncols = fb_size + 1

    mat = []
    for _, sign, exps in smooth:
        row = sign
        for j, e in enumerate(exps):
            if e % 2 == 1:
                row |= (1 << (j + 1))
        mat.append(row)

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
                mat[row] ^= mat[piv]
                combo[row] ^= combo[piv]

    null_vecs = []
    for row in range(nrows):
        if mat[row] == 0:
            indices = []
            bits = combo[row]; idx = 0
            while bits:
                if bits & 1: indices.append(idx)
                bits >>= 1; idx += 1
            if indices: null_vecs.append(indices)

    if verbose:
        print(f"    LA: {time.time()-la_t0:.1f}s, {len(null_vecs)} null vecs")

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
        print(f"    {len(null_vecs)} null vecs, no factor.")
    return None


###############################################################################
# ECM  (inline, copied from v5.0 — proven workhorse up to 54 digits)
###############################################################################

def ecm_factor(n, B1=1000000, curves=100, verbose=True):
    n = mpz(n)
    for c in range(curves):
        sigma = mpz(random.randint(6, 10**9))
        u = (sigma * sigma - 5) % n
        v = (4 * sigma) % n
        x = pow(u, 3, n); z = pow(v, 3, n)
        diff = (v - u) % n
        a24n = pow(diff, 3, n) * ((3*u+v) % n) % n
        a24d = 16 * x * v % n
        try:
            a24i = pow(int(a24d), -1, int(n))
        except Exception:
            g = gcd(a24d, n)
            if 1 < g < n:
                return int(g)
            continue
        a24 = a24n * a24i % n

        def md(px, pz):
            s = (px + pz) % n; d = (px - pz) % n
            ss = s * s % n; dd = d * d % n; dl = (ss - dd) % n
            return ss * dd % n, dl * (dd + a24 * dl % n) % n

        def ma(px, pz, qx, qz, dx, dz):
            u1 = (px + pz) * (qx - qz) % n
            v1 = (px - pz) * (qx + qz) % n
            return (u1 + v1) * (u1 + v1) % n * dz % n, (u1 - v1) * (u1 - v1) % n * dx % n

        def mm(k, px, pz):
            if k <= 1:
                return (px, pz) if k == 1 else (mpz(0), mpz(1))
            r0x, r0z = px, pz
            r1x, r1z = md(px, pz)
            for bit in bin(k)[3:]:
                if bit == '1':
                    r0x, r0z = ma(r0x, r0z, r1x, r1z, px, pz)
                    r1x, r1z = md(r1x, r1z)
                else:
                    r1x, r1z = ma(r0x, r0z, r1x, r1z, px, pz)
                    r0x, r0z = md(r0x, r0z)
            return r0x, r0z

        p = 2
        while p <= B1:
            pp = p
            while pp * p <= B1:
                pp *= p
            x, z = mm(pp, x, z)
            p = int(next_prime(p))
        g = gcd(z, n)
        if 1 < g < n:
            if verbose:
                print(f"  ECM curve {c}: {g}")
            return int(g)
        if verbose and c % 50 == 0 and c > 0:
            print(f"  ECM {c}/{curves}...")
    return None


###############################################################################
# MASTER DRIVER v7.0
###############################################################################

def factor(n, verbose=True, time_limit=3600):
    """
    Resonance Sieve v7.0 Master Driver.

    Routing by digit count:
      < 20d:   Trial division / VSDD
      20-45d:  ECM (unbalanced) + VSDD Sniper
      45-100d: SIQS (primary) with ECM fallback
      > 100d:  GNFS scaffold -> falls back to SIQS

    Budget: Path 1 = 10%, ECM = 20%, Path 2 (SIQS/MPQS) = 70%
    """
    n_val = int(n)
    nd = len(str(n_val))
    nb = int(gmpy2.log2(mpz(n_val))) + 1

    if verbose:
        print(f"Resonance Sieve v7.0: {nd}d ({nb}b)")
        engines = []
        if _have_siqs:
            engines.append("SIQS")
        else:
            engines.append("MPQS(fallback)")
        if _have_supergen:
            engines.append("SuperGen")
        engines.extend(["ECM", "VSDD"])
        print(f"  Engines: {', '.join(engines)}")

    t0 = time.time()

    # Trivial checks
    if n_val < 2:
        return None
    if gmpy2.is_prime(n_val):
        if verbose:
            print(f"  Input is prime.")
        return n_val
    if n_val % 2 == 0:
        return 2

    # Budget allocation
    path1_budget = max(5, time_limit * 0.10)   # 10%
    ecm_budget   = max(10, time_limit * 0.20)  # 20%
    path2_budget = max(30, time_limit * 0.70)   # 70%

    # ====================================================================
    # ROUTE: < 20 digits  --  Trial division / VSDD only
    # ====================================================================
    if nd < 20:
        if verbose:
            print(f"\n[Route] < 20d: Trial / VSDD")
        f = vsdd_sniper(n_val, verbose=verbose, time_limit=time_limit)
        if f and f != n_val:
            if verbose:
                print(f"  Total: {time.time()-t0:.3f}s")
            return f
        # Fallback: small MPQS
        if verbose:
            print(f"\n[Fallback] MPQS for small number")
        f = guillotine_mpqs(n_val, verbose=verbose, time_limit=time_limit - (time.time() - t0))
        if f:
            if verbose:
                print(f"  Total: {time.time()-t0:.3f}s")
            return f
        return None

    # ====================================================================
    # ROUTE: 20-45 digits  --  ECM + VSDD Sniper
    # ====================================================================
    if nd <= 45:
        if verbose:
            print(f"\n[Route] 20-45d: ECM + VSDD Sniper")

        # Path 1: VSDD Sniper (10% budget)
        if verbose:
            print(f"\n[Path 1] VSDD Sniper (budget={path1_budget:.0f}s)")
        f = vsdd_sniper(n_val, verbose=verbose, time_limit=path1_budget)
        if f and f != n_val:
            if verbose:
                print(f"  Total: {time.time()-t0:.3f}s")
            return f

        # Super-Generator (if available, shares Path 1 budget)
        if _have_supergen:
            remaining_p1 = max(1, path1_budget - (time.time() - t0))
            if verbose:
                print(f"\n[Path 1b] Super-Generator (budget={remaining_p1:.0f}s)")
            try:
                f = super_generator_search(n_val, verbose=verbose, time_limit=remaining_p1)
                if f and f != n_val:
                    if verbose:
                        print(f"  Total: {time.time()-t0:.3f}s")
                    return f
            except Exception as e:
                if verbose:
                    print(f"  Super-Generator error: {e}")

        # ECM (20% budget)
        ecm_B1 = min(1000000, max(10000, 10 ** (nd // 5)))
        ecm_curves = min(200, max(30, nd * 2))
        if verbose:
            print(f"\n[ECM] B1={ecm_B1}, curves={ecm_curves}, budget={ecm_budget:.0f}s")
        f = ecm_factor(n_val, B1=ecm_B1, curves=ecm_curves, verbose=verbose)
        if f and f != n_val:
            if verbose:
                print(f"  Total: {time.time()-t0:.1f}s")
            return f

        # Path 2: MPQS / SIQS (70% budget)
        remaining = max(30, time_limit - (time.time() - t0))
        if _have_siqs:
            if verbose:
                print(f"\n[Path 2] SIQS (budget={remaining:.0f}s)")
            try:
                f = siqs_factor(n_val, verbose=verbose, time_limit=remaining)
                if f and f != n_val:
                    if verbose:
                        print(f"  Total: {time.time()-t0:.1f}s")
                    return f
            except Exception as e:
                if verbose:
                    print(f"  SIQS error: {e}, falling back to MPQS")

        if verbose:
            print(f"\n[Path 2] Guillotine MPQS (budget={remaining:.0f}s)")
        f = guillotine_mpqs(n_val, verbose=verbose, time_limit=remaining)
        if f:
            if verbose:
                print(f"  Total: {time.time()-t0:.1f}s")
            return f
        return None

    # ====================================================================
    # ROUTE: 45-100 digits  --  SIQS primary, ECM fallback
    # ====================================================================
    if nd <= 100:
        if verbose:
            print(f"\n[Route] 45-100d: SIQS primary + ECM")

        # Path 1: VSDD Sniper (10% budget — unlikely to hit but cheap)
        if verbose:
            print(f"\n[Path 1] VSDD Sniper (budget={path1_budget:.0f}s)")
        f = vsdd_sniper(n_val, verbose=verbose, time_limit=path1_budget)
        if f and f != n_val:
            if verbose:
                print(f"  Total: {time.time()-t0:.3f}s")
            return f

        # Super-Generator (if available)
        if _have_supergen:
            remaining_p1 = max(1, path1_budget - (time.time() - t0))
            if verbose:
                print(f"\n[Path 1b] Super-Generator (budget={remaining_p1:.0f}s)")
            try:
                f = super_generator_search(n_val, verbose=verbose, time_limit=remaining_p1)
                if f and f != n_val:
                    if verbose:
                        print(f"  Total: {time.time()-t0:.3f}s")
                    return f
            except Exception as e:
                if verbose:
                    print(f"  Super-Generator error: {e}")

        # ECM (20% budget — catches unbalanced factors)
        ecm_B1 = min(5000000, max(100000, 10 ** (nd // 4)))
        ecm_curves = min(500, max(50, nd * 3))
        if verbose:
            print(f"\n[ECM] B1={ecm_B1}, curves={ecm_curves}, budget={ecm_budget:.0f}s")
        ecm_t0 = time.time()
        f = ecm_factor(n_val, B1=ecm_B1, curves=ecm_curves, verbose=verbose)
        if f and f != n_val:
            if verbose:
                print(f"  Total: {time.time()-t0:.1f}s")
            return f

        # Path 2: SIQS (primary, 70% budget)
        remaining = max(60, time_limit - (time.time() - t0))
        if _have_siqs:
            if verbose:
                print(f"\n[Path 2] SIQS (budget={remaining:.0f}s)")
            try:
                f = siqs_factor(n_val, verbose=verbose, time_limit=remaining)
                if f and f != n_val:
                    if verbose:
                        print(f"  Total: {time.time()-t0:.1f}s")
                    return f
            except Exception as e:
                if verbose:
                    print(f"  SIQS error: {e}, falling back to MPQS")

        # Fallback: inline MPQS
        remaining = max(60, time_limit - (time.time() - t0))
        if verbose:
            print(f"\n[Path 2 fallback] Guillotine MPQS (budget={remaining:.0f}s)")
        f = guillotine_mpqs(n_val, verbose=verbose, time_limit=remaining)
        if f:
            if verbose:
                print(f"  Total: {time.time()-t0:.1f}s")
            return f
        return None

    # ====================================================================
    # ROUTE: > 100 digits  --  GNFS scaffold (placeholder)
    # ====================================================================
    if verbose:
        print(f"\n[Route] > 100d: GNFS scaffold")
        print(f"  GNFS not yet implemented, using SIQS")

    # Path 1 (quick check)
    if verbose:
        print(f"\n[Path 1] VSDD Sniper (budget={path1_budget:.0f}s)")
    f = vsdd_sniper(n_val, verbose=verbose, time_limit=path1_budget)
    if f and f != n_val:
        return f

    # ECM (20%)
    ecm_B1 = min(10000000, max(1000000, 10 ** (min(nd, 80) // 4)))
    ecm_curves = min(1000, max(100, nd * 3))
    if verbose:
        print(f"\n[ECM] B1={ecm_B1}, curves={ecm_curves}, budget={ecm_budget:.0f}s")
    f = ecm_factor(n_val, B1=ecm_B1, curves=ecm_curves, verbose=verbose)
    if f and f != n_val:
        if verbose:
            print(f"  Total: {time.time()-t0:.1f}s")
        return f

    # SIQS / MPQS (70%)
    remaining = max(60, time_limit - (time.time() - t0))
    if _have_siqs:
        if verbose:
            print(f"\n[Path 2] SIQS (budget={remaining:.0f}s)")
        try:
            f = siqs_factor(n_val, verbose=verbose, time_limit=remaining)
            if f and f != n_val:
                if verbose:
                    print(f"  Total: {time.time()-t0:.1f}s")
                return f
        except Exception as e:
            if verbose:
                print(f"  SIQS error: {e}, falling back to MPQS")

    remaining = max(60, time_limit - (time.time() - t0))
    if verbose:
        print(f"\n[Path 2 fallback] Guillotine MPQS (budget={remaining:.0f}s)")
    f = guillotine_mpqs(n_val, verbose=verbose, time_limit=remaining)
    if f:
        if verbose:
            print(f"  Total: {time.time()-t0:.1f}s")
        return f

    if verbose:
        print(f"  FAILED after {time.time()-t0:.1f}s")
    return None


###############################################################################
# TEST SUITE
###############################################################################

if __name__ == "__main__":
    random.seed(42)
    print("=" * 72)
    print("THE RESONANCE SIEVE v7.0")
    print("Unified Geometric Engine: VSDD Sniper + Super-Generator + SIQS + ECM")
    print("=" * 72)

    # Verify with n=901 from the spec
    print("\n--- Spec Verification: n=901 ---")
    f = factor(901, verbose=True, time_limit=10)
    assert f == 17 or f == 53, f"Expected 17 or 53, got {f}"
    print(f"  901 = {f} x {901 // f}")

    results = []

    # Test suite: increasing difficulty
    tests = [
        ("20d", 1000000009 * 1000000087),
        ("30d", 100000000000067 * 100000000000097),
    ]

    for bits in [110, 130, 150, 170, 190, 200, 220]:
        half = bits // 2
        p = int(next_prime(mpz(random.getrandbits(half))))
        q = int(next_prime(mpz(random.getrandbits(half))))
        n_val = p * q
        nd = len(str(n_val))
        nb = int(gmpy2.log2(mpz(n_val))) + 1
        tests.append((f"{nd}d/{nb}b", n_val))

    for name, n_val in tests:
        nd = len(str(n_val))
        nb = int(gmpy2.log2(mpz(n_val))) + 1
        print(f"\n{'='*72}")
        print(f"### {name}: {nd}d ({nb}b) ###")
        t0 = time.time()
        f = factor(n_val, verbose=True, time_limit=600)
        elapsed = time.time() - t0
        ok = f is not None and f != n_val
        if ok:
            print(f"  PASS: {f} x {n_val // f} ({elapsed:.1f}s)")
        else:
            print(f"  FAIL ({elapsed:.1f}s)")
        results.append((name, elapsed, ok))

    # Summary
    print(f"\n{'='*72}")
    print("RESULTS SUMMARY v7.0")
    print(f"{'='*72}")
    for name, t, ok in results:
        print(f"  {name:15s} {t:8.1f}s  {'PASS' if ok else 'FAIL'}")

    passes = sum(1 for _, _, ok in results if ok)
    print(f"\n  {passes}/{len(results)} passed")

    # RSA-100 attempt if enough pass
    if passes >= len(results) - 2:
        print(f"\n{'='*72}")
        print("RSA-100 ATTEMPT (100 digits, 330 bits)")
        print(f"{'='*72}")
        t0 = time.time()
        f = factor(RSA_100, verbose=True, time_limit=14400)
        elapsed = time.time() - t0
        if f:
            print(f"\n*** RSA-100 FACTORED: {f} x {RSA_100 // f} ***")
        else:
            print(f"\nRSA-100 FAILED ({elapsed:.1f}s)")

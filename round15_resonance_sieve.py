#!/usr/bin/env python3
"""
Round 15: The Resonance Sieve v2.0 — Corrected MPQS
=====================================================
Key fix: sieve g(x) = a*x^2 + 2*b*x + c where c=(b^2-n)/a
NOT Q(x) = (ax+b)^2 - n which is a*g(x) and ~n in magnitude.

Pipeline:
  Stage 1: Factor base + modular pre-filter
  Stage 2: MPQS with proper polynomial generation
  Stage 3: JIT-accelerated sieve of g(x) + large prime variation
  Stage 4: GF(2) Gaussian elimination → factor extraction
"""

import gmpy2
from gmpy2 import mpz, isqrt, is_prime, gcd, jacobi, next_prime
import numpy as np
from numba import njit
import time
import math
import random
import sys

from rsa_targets import *


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


def mpqs_params(nd):
    # Tuned based on L(n) heuristics and empirical testing.
    # Key: FB must be small enough that g(x) values (~nb/2 bits) have
    # reasonable probability of being smooth over the FB.
    # Smoothness prob ≈ u^(-u) where u = log(g_max)/log(B), B = max FB prime.
    tbl = [
        (20,   80,    20000),
        (25,  150,    40000),
        (30,  250,    80000),
        (35,  450,   150000),
        (40,  800,   300000),
        (45, 1200,   500000),
        (50, 2000,   800000),
        (55, 3000,  1200000),
        (60, 4500,  2000000),
        (65, 7000,  3000000),
        (70,10000,  4500000),
        (75,15000,  6000000),
        (80,22000,  8000000),
        (85,32000, 11000000),
        (90,45000, 15000000),
        (95,60000, 20000000),
        (100,80000, 28000000),
    ]
    for i in range(len(tbl) - 1):
        if tbl[i][0] <= nd < tbl[i + 1][0]:
            frac = (nd - tbl[i][0]) / (tbl[i + 1][0] - tbl[i][0])
            fb = int(tbl[i][1] + frac * (tbl[i + 1][1] - tbl[i][1]))
            M = int(tbl[i][2] + frac * (tbl[i + 1][2] - tbl[i][2]))
            return fb, M
    if nd <= tbl[0][0]: return tbl[0][1], tbl[0][2]
    return tbl[-1][1], tbl[-1][2]


def mpqs_factor(n, verbose=True, time_limit=3600):
    """
    Multiple Polynomial Quadratic Sieve.

    Core identity: (ax+b)^2 ≡ a * g(x) (mod n)
    where g(x) = a*x^2 + 2*b*x + c, c = (b^2-n)/a

    We sieve g(x) which has max magnitude ≈ M*sqrt(n/2),
    much smaller than (ax+b)^2 - n ≈ n.
    """
    n = mpz(n)
    nd = len(str(n))
    nb = int(gmpy2.log2(n)) + 1

    fb_size, M = mpqs_params(nd)

    if verbose:
        print(f"MPQS: {nd} digits ({nb} bits)")
        print(f"  Factor base: {fb_size}, Sieve width: 2×{M}")

    t0 = time.time()

    # ── Stage 1: Factor Base ──
    fb = []
    p = 2
    while len(fb) < fb_size:
        if p == 2 or (is_prime(p) and jacobi(int(n % p), p) == 1):
            fb.append(int(p))
        p = int(next_prime(p)) if p > 2 else 3

    fb_np = np.array(fb, dtype=np.int64)
    fb_log = np.array([int(round(math.log2(p) * 1024)) for p in fb], dtype=np.int32)

    if verbose:
        print(f"  FB: [{fb[0]}..{fb[-1]}], built {time.time() - t0:.1f}s")

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

    # Threshold tolerance in bits
    T_bits = max(20, nb // 3)

    if verbose:
        print(f"  Need: {needed} relations, T_bits={T_bits}")

    # JIT warmup
    dummy = np.zeros(100, dtype=np.int32)
    jit_sieve(dummy, np.array([2, 3], dtype=np.int64),
              np.array([10, 15], dtype=np.int32),
              np.array([0, 0], dtype=np.int64),
              np.array([1, 1], dtype=np.int64), 100)
    jit_find_smooth(dummy, 1)

    poly_count = 0
    total_cands = 0
    total_smooth_full = 0
    total_smooth_partial = 0

    def sieve_poly_mpqs(a_val, b_val, a_primes_used):
        """
        Sieve g(x) = a*x^2 + 2*b*x + c where c=(b^2-n)/a.

        The relation: (ax+b)^2 = a*g(x) + n, so (ax+b)^2 ≡ a*g(x) (mod n).
        Since a is a product of FB primes, if g(x) is smooth over FB,
        then a*g(x) is smooth and we have a valid relation.

        The x-value stored for LA is (ax+b) mod n.
        The exponent vector includes contributions from both a and g(x).
        """
        nonlocal total_cands, total_smooth_full, total_smooth_partial

        a_int = int(a_val)
        b_int = int(b_val)
        c_val = (b_val * b_val - n) // a_val  # Exact since a | (b^2-n)
        sz = 2 * M

        # Sieve offsets: g(x) ≡ 0 (mod p)
        # g(x) = a*x^2 + 2*b*x + c
        # For p not dividing a: g(x) ≡ 0 (mod p) iff (ax+b)^2 ≡ n (mod p)
        #   ax+b ≡ ±t (mod p) where t = sqrt(n mod p)
        #   x ≡ (±t - b) * a^{-1} (mod p)
        # For p | a: g(x) = a*x^2 + 2*b*x + c, and a≡0 mod p
        #   g(x) ≡ 2*b*x + c (mod p), so x ≡ -c/(2b) (mod p) — one root

        offsets1 = np.full(fb_size, -1, dtype=np.int64)
        offsets2 = np.full(fb_size, -1, dtype=np.int64)

        a_prime_set = set(a_primes_used) if a_primes_used else set()
        # Pre-compute indices for a_primes in fb (avoid fb.index() in hot loop)
        a_prime_indices = [fb_index[ap] for ap in a_primes_used] if a_primes_used else []

        for pi in range(fb_size):
            p = fb[pi]
            if p == 2:
                # Check parity: g(x) for x=0 and x=1
                g0 = int(c_val % 2)
                g1 = int((a_val + 2 * b_val + c_val) % 2)
                if g0 == 0:
                    offsets1[pi] = M % 2  # x=0 maps to index M
                    if g1 == 0:
                        offsets2[pi] = (M + 1) % 2
                elif g1 == 0:
                    offsets1[pi] = (M + 1) % 2
                continue

            if p in a_prime_set:
                # p | a: g(x) ≡ 2*b*x + c (mod p)
                # x ≡ -c * (2b)^{-1} (mod p)
                b2 = (2 * b_int) % p
                if b2 == 0:
                    continue
                b2_inv = pow(b2, -1, p)
                c_mod = int(c_val % p)
                r = (-c_mod * b2_inv) % p
                off = (r + M) % p
                offsets1[pi] = off
                # Only one root when p | a
                continue

            t = sqrt_n_mod.get(p)
            if t is None:
                continue

            a_inv = pow(a_int % p, -1, p)
            b_mod = b_int % p

            r1 = (a_inv * (t - b_mod)) % p
            r2 = (a_inv * (p - t - b_mod)) % p

            off1 = (r1 + M) % p
            off2 = (r2 + M) % p

            offsets1[pi] = off1
            offsets2[pi] = off2 if off2 != off1 else -1

        # JIT sieve
        sieve = np.zeros(sz, dtype=np.int32)
        jit_sieve(sieve, fb_np, fb_log, offsets1, offsets2, sz)

        # Threshold based on log2(max|g(x)|)
        # g(x) at edges: |g(±M)| ≈ a*M^2 ≈ sqrt(2n)/M * M^2 = M*sqrt(2n)
        # But also c = (b^2-n)/a ≈ -n/a ≈ -M*sqrt(n/2), so |g(0)| ≈ M*sqrt(n/2)
        log_g_max = math.log2(max(M, 1)) + 0.5 * nb
        thresh = int(max(0, (log_g_max - T_bits)) * 1024)

        candidates = jit_find_smooth(sieve, thresh)
        total_cands += len(candidates)

        # Trial divide g(x) for each candidate
        for ci in range(len(candidates)):
            x = int(candidates[ci]) - M
            ax_b = a_val * x + b_val

            # Compute g(x) = a*x^2 + 2*b*x + c
            gx = int(a_val * x * x + 2 * b_val * x + c_val)

            if gx == 0:
                g = gcd(ax_b, n)
                if 1 < g < n:
                    return int(g)
                continue

            v = abs(gx)
            sign = 1 if gx < 0 else 0
            exps = []
            for p in fb:
                e = 0
                while v % p == 0:
                    v //= p
                    e += 1
                exps.append(e)

            if v == 1:
                # g(x) is smooth! Add exponents from a as well.
                for idx in a_prime_indices:
                    exps[idx] += 1

                smooth.append((int(ax_b % n), sign, exps))
                total_smooth_full += 1
            elif v < lp_bound and gmpy2.is_prime(v):
                v = int(v)
                if v in partials:
                    ox, os, oe = partials[v]
                    # Combine: multiply x-values, add exponent vectors
                    cax = ox * int(ax_b) % int(n)
                    cs = (os + sign) % 2
                    for idx in a_prime_indices:
                        exps[idx] += 1
                    ce = [oe[j] + exps[j] for j in range(fb_size)]
                    smooth.append((cax, cs, ce))
                    total_smooth_partial += 1
                else:
                    # Store with a's contribution included
                    for idx in a_prime_indices:
                        exps[idx] += 1
                    partials[v] = (int(ax_b % n), sign, exps)

        return None

    def sieve_poly_simple(x_start, x_end):
        """Simple QS: Q(x) = (sqrt_n + x)^2 - n, sieve x in [x_start, x_end)."""
        nonlocal total_cands, total_smooth_full, total_smooth_partial

        sz = x_end - x_start
        if sz <= 0:
            return None

        offsets1 = np.full(fb_size, -1, dtype=np.int64)
        offsets2 = np.full(fb_size, -1, dtype=np.int64)

        for pi, p in enumerate(fb):
            if p == 2:
                sn2 = int(sqrt_n % 2)
                r = (1 - sn2) % 2
                off = (r - x_start % 2 + 2) % 2
                offsets1[pi] = off
                continue
            t = sqrt_n_mod.get(p)
            if t is None:
                continue
            sn_p = int(sqrt_n % p)
            r1 = (t - sn_p) % p
            r2 = (p - t - sn_p) % p
            offsets1[pi] = (r1 - x_start % p + p) % p
            offsets2[pi] = ((r2 - x_start % p + p) % p) if r2 != r1 else -1

        sieve = np.zeros(sz, dtype=np.int32)
        jit_sieve(sieve, fb_np, fb_log, offsets1, offsets2, sz)

        log_q = math.log2(float(2 * sqrt_n)) + math.log2(max(abs(x_end), abs(x_start), 1))
        thresh = int(max(0, (log_q - T_bits)) * 1024)

        candidates = jit_find_smooth(sieve, thresh)
        total_cands += len(candidates)

        for ci in range(len(candidates)):
            x = int(candidates[ci]) + x_start
            ax = sqrt_n + x
            Q = int(ax * ax - n)
            if Q == 0:
                g = gcd(ax, n)
                if 1 < g < n:
                    return int(g)
                continue

            v = abs(Q)
            sign = 1 if Q < 0 else 0
            exps = []
            for p in fb:
                e = 0
                while v % p == 0:
                    v //= p
                    e += 1
                exps.append(e)

            if v == 1:
                smooth.append((int(ax % n), sign, exps))
                total_smooth_full += 1
            elif v < lp_bound and gmpy2.is_prime(v):
                v = int(v)
                if v in partials:
                    ox, os, oe = partials[v]
                    cax = ox * int(ax) % int(n)
                    cs = (os + sign) % 2
                    ce = [oe[j] + exps[j] for j in range(fb_size)]
                    smooth.append((cax, cs, ce))
                    total_smooth_partial += 1
                else:
                    partials[v] = (int(ax % n), sign, exps)

        return None

    # ── Phase 1: Simple QS (quick scan near sqrt_n) ──
    if verbose:
        print(f"\n  Phase 1: Simple QS scan")

    simple_range = min(M, 100000) if nd > 45 else min(M, 500000)

    result = sieve_poly_simple(1, simple_range)
    if result:
        return result
    result = sieve_poly_simple(-simple_range, 0)
    if result:
        return result
    poly_count += 1

    if verbose:
        print(f"    Simple QS: {len(smooth)} smooth ({total_smooth_full}+{total_smooth_partial}), "
              f"{len(partials)} partial ({time.time()-t0:.1f}s)")

    # ── Phase 2: MPQS ──
    if len(smooth) < needed:
        if verbose:
            print(f"\n  Phase 2: MPQS — targeting {needed} relations")

        target_a = isqrt(2 * n) // M
        log_target = float(gmpy2.log2(target_a)) if target_a > 0 else 0

        # Pick primes from upper portion of FB
        select_lo = max(1, len(fb) // 3)
        select_hi = len(fb) - 1
        median_prime = fb[(select_lo + select_hi) // 2]
        s = max(2, min(15, round(log_target / math.log2(median_prime))))

        if verbose:
            print(f"    target_a ≈ 10^{len(str(int(target_a)))}, s={s} primes/poly")

        # Pre-build index lookup for a_primes
        fb_index = {p: i for i, p in enumerate(fb)}

        for poly_iter in range(100000):
            if len(smooth) >= needed or time.time() - t0 > time_limit:
                break

            # Select a
            best_a = None
            best_diff = float('inf')
            best_primes = None

            for _ in range(30):
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

            # Compute all valid b values via CRT with sign combos
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

            # 2^(s-1) sign combos (fix first sign to +)
            n_b_values = 1 << (s - 1)

            for sign_combo in range(n_b_values):
                if len(smooth) >= needed or time.time() - t0 > time_limit:
                    break

                signs = [1]
                for bit in range(s - 1):
                    signs.append(1 if not (sign_combo & (1 << bit)) else -1)

                b = mpz(0)
                bad = False
                for i in range(s):
                    q = a_primes[i]
                    t = (t_roots[i] * signs[i]) % q
                    Ai = a // q
                    try:
                        Ai_inv = pow(int(Ai % q), -1, q)
                    except (ValueError, ZeroDivisionError):
                        bad = True
                        break
                    b = (b + mpz(t) * Ai * mpz(Ai_inv)) % a

                if bad:
                    continue

                if (b * b - n) % a != 0:
                    continue

                result = sieve_poly_mpqs(a, b, a_primes)
                if result:
                    return result

                poly_count += 1

            if poly_count > 0 and poly_count % max(1, 20 if nd < 60 else 5) == 0 and verbose:
                elapsed = time.time() - t0
                rate = len(smooth) / max(elapsed, 0.001)
                eta = (needed - len(smooth)) / max(rate, 0.001) if rate > 0 else float('inf')
                print(f"    [{elapsed:.0f}s] poly={poly_count}, smooth={len(smooth)}/{needed} "
                      f"({total_smooth_full}+{total_smooth_partial}), "
                      f"partial={len(partials)}, cands={total_cands}, "
                      f"rate={rate:.1f}/s, eta={min(eta, 999999):.0f}s")

    elapsed = time.time() - t0

    if len(smooth) < fb_size + 1:
        if verbose:
            print(f"\n  Insufficient: {len(smooth)}/{needed} ({elapsed:.1f}s)")
        return None

    # ── Stage 4: Linear Algebra over GF(2) ──
    if verbose:
        print(f"\n  Stage 4: LA on {len(smooth)} relations × {fb_size + 1} columns")

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
                piv = row
                break
        if piv == -1:
            continue
        used[piv] = True
        for row in range(nrows):
            if row != piv and mat[row] & mask:
                mat[row] ^= mat[piv]
                combo[row] ^= combo[piv]

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
            if len(indices) >= 1:
                null_vecs.append(indices)

    if verbose:
        print(f"  LA: {time.time() - la_t0:.1f}s, {len(null_vecs)} null vectors")

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
                    print(f"\n  *** FACTOR: {g} ({total:.1f}s) ***")
                    print(f"  Cofactor: {n // g}")
                return int(g)

    if verbose:
        print(f"  All {len(null_vecs)} null vectors tried, no factor.")
    return None


###############################################################################
# ECM with Stage 2
###############################################################################

def ecm_factor(n, B1=1000000, curves=100, verbose=True):
    n = mpz(n)
    for c in range(curves):
        sigma = mpz(random.randint(6, 10**9))
        u = (sigma * sigma - 5) % n
        v = (4 * sigma) % n
        x = pow(u, 3, n)
        z = pow(v, 3, n)

        diff = (v - u) % n
        a24_num = pow(diff, 3, n) * ((3 * u + v) % n) % n
        a24_den = 16 * x * v % n

        try:
            a24_inv = pow(int(a24_den), -1, int(n))
        except (ValueError, ZeroDivisionError):
            g = gcd(a24_den, n)
            if 1 < g < n: return int(g)
            continue

        a24 = a24_num * a24_inv % n

        def mont_double(px, pz):
            s = (px + pz) % n; d = (px - pz) % n
            ss, dd = s * s % n, d * d % n
            delta = (ss - dd) % n
            return ss * dd % n, delta * (dd + a24 * delta % n) % n

        def mont_add(px, pz, qx, qz, dx, dz):
            u1 = (px + pz) * (qx - qz) % n
            v1 = (px - pz) * (qx + qz) % n
            return (u1 + v1) * (u1 + v1) % n * dz % n, (u1 - v1) * (u1 - v1) % n * dx % n

        def mont_mul(k, px, pz):
            if k <= 1: return (px, pz) if k == 1 else (mpz(0), mpz(1))
            r0x, r0z = px, pz
            r1x, r1z = mont_double(px, pz)
            for bit in bin(k)[3:]:
                if bit == '1':
                    r0x, r0z = mont_add(r0x, r0z, r1x, r1z, px, pz)
                    r1x, r1z = mont_double(r1x, r1z)
                else:
                    r1x, r1z = mont_add(r0x, r0z, r1x, r1z, px, pz)
                    r0x, r0z = mont_double(r0x, r0z)
            return r0x, r0z

        p = 2
        while p <= B1:
            pp = p
            while pp * p <= B1: pp *= p
            x, z = mont_mul(pp, x, z)
            p = int(next_prime(p))

        g = gcd(z, n)
        if 1 < g < n:
            if verbose: print(f"  ECM S1 curve {c}: {g}")
            return int(g)

        if verbose and c % 50 == 0 and c > 0:
            print(f"  ECM: {c}/{curves} curves...")

    return None


###############################################################################
# Driver
###############################################################################

def factor(n, verbose=True, time_limit=3600):
    n_val = int(n)
    nd = len(str(n_val))

    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
        if n_val % p == 0:
            return p

    p = 37
    while p < 1000000 and p * p <= n_val:
        if n_val % p == 0:
            return p
        p += 2

    if gmpy2.is_prime(n_val):
        if verbose: print(f"  {n_val} is prime")
        return n_val

    ecm_B1 = min(1000000, max(10000, 10 ** (nd // 5)))
    ecm_curves = min(200, max(30, nd * 2))

    if verbose:
        print(f"  Trying ECM (B1={ecm_B1}, curves={ecm_curves})...")

    t0 = time.time()
    f = ecm_factor(n_val, B1=ecm_B1, curves=ecm_curves, verbose=verbose)
    if f:
        if verbose: print(f"  ECM: {time.time()-t0:.1f}s")
        return f

    if verbose:
        print(f"  ECM failed ({time.time()-t0:.1f}s), trying MPQS...")

    remaining = time_limit - (time.time() - t0)
    return mpqs_factor(n_val, verbose=verbose, time_limit=max(60, remaining))


###############################################################################
# Test
###############################################################################

if __name__ == "__main__":
    random.seed(42)
    print("=" * 70)
    print("Round 15: Resonance Sieve v2.0 — Corrected MPQS")
    print("=" * 70)

    results = []

    tests = [
        ("20d", 1000000009 * 1000000087),
        ("30d", 100000000000067 * 100000000000097),
    ]

    for target_bits in [110, 130, 150, 170, 190, 200, 220]:
        half = target_bits // 2
        p = int(next_prime(mpz(random.getrandbits(half))))
        q = int(next_prime(mpz(random.getrandbits(half))))
        n_val = p * q
        nd = len(str(n_val))
        nb = int(gmpy2.log2(mpz(n_val))) + 1
        tests.append((f"{nd}d/{nb}b", n_val))

    for name, n_val in tests:
        nd = len(str(n_val))
        nb = int(gmpy2.log2(mpz(n_val))) + 1
        print(f"\n{'─'*70}")
        print(f"### {name}: {nd} digits ({nb} bits) ###")
        t0 = time.time()

        f = factor(n_val, verbose=True, time_limit=600)
        elapsed = time.time() - t0

        if f and f != n_val:
            print(f"  Result: {f} × {n_val // f}")
            print(f"  Time: {elapsed:.1f}s")
            results.append((name, elapsed, True))
        else:
            print(f"  FAIL ({elapsed:.1f}s)")
            results.append((name, elapsed, False))

    print(f"\n{'='*70}")
    print("RESULTS SUMMARY")
    print(f"{'='*70}")
    for name, t, ok in results:
        status = "PASS" if ok else "FAIL"
        print(f"  {name:15s} {t:8.1f}s  {status}")

    passes = sum(1 for _, _, ok in results if ok)
    if passes >= len(results) - 2:
        print(f"\n{'='*70}")
        print("RSA-100 ATTEMPT (100 digits, 330 bits)")
        print(f"{'='*70}")
        t0 = time.time()
        f = mpqs_factor(RSA_100, verbose=True, time_limit=14400)
        elapsed = time.time() - t0
        if f:
            print(f"\n*** RSA-100 FACTORED: {f} ***")
        else:
            print(f"\nRSA-100 FAILED ({elapsed:.1f}s)")

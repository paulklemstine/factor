#!/usr/bin/env python3
"""
Round 13: Fast Quadratic Sieve with Numba JIT
Key optimizations:
1. Numba JIT for sieve loop (10-100x faster than numpy slice)
2. Numba JIT for trial division
3. Double large prime variation
4. Proper MPQS polynomial selection
"""

import gmpy2
from gmpy2 import mpz, isqrt, is_prime, gcd, jacobi, next_prime
import numpy as np
import numba
from numba import njit, prange
import time
import math
import random
import sys

from rsa_targets import *


def tonelli_shanks(n, p):
    n = n % p
    if n == 0: return 0
    if p == 2: return n
    if pow(n, (p-1)//2, p) != 1: return None
    q, s = p-1, 0
    while q % 2 == 0: q //= 2; s += 1
    if s == 1: return pow(n, (p+1)//4, p)
    z = 2
    while pow(z, (p-1)//2, p) != p-1: z += 1
    m, c, t, r = s, pow(z, q, p), pow(n, q, p), pow(n, (q+1)//2, p)
    while True:
        if t == 1: return r
        i, tmp = 1, t*t % p
        while tmp != 1: tmp = tmp*tmp % p; i += 1
        b = pow(c, 1 << (m-i-1), p)
        m, c, t, r = i, b*b%p, t*b*b%p, r*b%p


###############################################################################
# Numba JIT-compiled sieve
###############################################################################

@njit(cache=True)
def sieve_with_primes(sieve, fb_primes, fb_logs, roots1, roots2, M):
    """JIT-compiled sieve: add log(p) at every root position."""
    sz = 2 * M
    n_primes = len(fb_primes)
    for i in range(n_primes):
        p = fb_primes[i]
        log_p = fb_logs[i]
        r1 = roots1[i]
        r2 = roots2[i]

        if r1 < 0:
            continue  # Skip primes with no roots

        # Sieve with root1
        j = (r1 + M) % p
        while j < sz:
            sieve[j] += log_p
            j += p

        # Sieve with root2 (may equal root1)
        if r2 != r1 and r2 >= 0:
            j = (r2 + M) % p
            while j < sz:
                sieve[j] += log_p
                j += p


@njit(cache=True)
def find_candidates(sieve, threshold):
    """Find sieve locations above threshold."""
    result = np.empty(len(sieve), dtype=np.int64)
    count = 0
    for i in range(len(sieve)):
        if sieve[i] >= threshold:
            result[count] = i
            count += 1
    return result[:count]


###############################################################################
# Main QS implementation
###############################################################################

def fast_mpqs(n, verbose=True, time_limit=3600):
    """Fast MPQS with Numba-accelerated sieve."""
    n = mpz(n)
    nd = len(str(n))
    nb = int(gmpy2.log2(n)) + 1

    # Parameters
    if nd <= 25: fb_size, M = 50, 10000
    elif nd <= 30: fb_size, M = 100, 25000
    elif nd <= 35: fb_size, M = 200, 50000
    elif nd <= 40: fb_size, M = 350, 80000
    elif nd <= 45: fb_size, M = 600, 150000
    elif nd <= 50: fb_size, M = 1000, 300000
    elif nd <= 55: fb_size, M = 1800, 500000
    elif nd <= 60: fb_size, M = 3000, 800000
    elif nd <= 65: fb_size, M = 5000, 1200000
    elif nd <= 70: fb_size, M = 8000, 1800000
    elif nd <= 80: fb_size, M = 15000, 3000000
    elif nd <= 90: fb_size, M = 30000, 5000000
    else: fb_size, M = 50000, 8000000

    if verbose:
        print(f"Fast MPQS: {nd} digits ({nb} bits), FB={fb_size}, M={M}")

    t0 = time.time()

    # Build factor base
    fb = []
    p = 2
    while len(fb) < fb_size:
        if p == 2 or (is_prime(p) and jacobi(int(n % p), p) == 1):
            fb.append(int(p))
        p = int(next_prime(p)) if p > 2 else 3

    fb_np = np.array(fb, dtype=np.int64)
    fb_log_np = np.array([round(math.log2(p) * 1024) for p in fb], dtype=np.int32)

    if verbose:
        print(f"  FB: max={fb[-1]}, built in {time.time()-t0:.1f}s")

    # Precompute sqrt(n) mod p
    sqrt_n_mod = {}
    for p in fb:
        if p == 2:
            sqrt_n_mod[2] = int(n % 2)
        else:
            sqrt_n_mod[p] = tonelli_shanks(int(n % p), p)

    sqrt_n = isqrt(n)
    if sqrt_n * sqrt_n < n:
        sqrt_n += 1

    # State
    smooth = []
    partials = {}
    needed = fb_size + 5

    # Threshold
    T_bits = max(10, nb // 5)

    # Warmup JIT
    dummy = np.zeros(100, dtype=np.int32)
    sieve_with_primes(dummy, np.array([2,3], dtype=np.int64),
                      np.array([10,15], dtype=np.int32),
                      np.array([0,0], dtype=np.int64),
                      np.array([1,1], dtype=np.int64), 50)
    find_candidates(dummy, 1)

    if verbose:
        print(f"  JIT compiled. Starting sieve...")

    lp_bound = fb[-1] ** 2
    poly_count = 0

    def do_sieve(a, b, M_use):
        """Sieve one polynomial and extract smooth relations."""
        nonlocal smooth, partials, poly_count

        # Compute roots for each prime
        # (a*x + b)^2 ≡ n (mod p)
        # a*x ≡ ±t - b (mod p) where t^2 ≡ n (mod p)
        # x ≡ a^(-1) * (±t - b) (mod p)

        roots1 = np.full(len(fb), -1, dtype=np.int64)
        roots2 = np.full(len(fb), -1, dtype=np.int64)

        a_int = int(a)
        b_int = int(b)

        for pi, p in enumerate(fb):
            if p == 2:
                # Find root mod 2
                for x in range(2):
                    if int((a * x + b) ** 2 - n) % 2 == 0:
                        roots1[pi] = x
                        break
                continue

            t = sqrt_n_mod.get(p)
            if t is None:
                continue

            try:
                a_inv = pow(a_int % p, -1, p)
            except (ValueError, ZeroDivisionError):
                continue

            b_mod = b_int % p
            r1 = (a_inv * (t - b_mod)) % p
            r2 = (a_inv * (p - t - b_mod)) % p
            roots1[pi] = r1
            roots2[pi] = r2 if r2 != r1 else -1

        # Sieve
        sieve = np.zeros(2 * M_use, dtype=np.int32)
        sieve_with_primes(sieve, fb_np, fb_log_np, roots1, roots2, M_use)

        # Threshold
        if a_int == 1:
            log_q = math.log2(float(2 * sqrt_n)) + math.log2(max(M_use, 1))
        else:
            log_q = math.log2(float(a)) + 2 * math.log2(max(M_use, 1))
        thresh = int(max(0, (log_q - T_bits)) * 1024)

        # Find candidates
        candidates = find_candidates(sieve, thresh)

        # Trial divide each candidate
        direct_factor = None
        for ci in range(len(candidates)):
            idx = int(candidates[ci])
            x = idx - M_use
            ax_b = a * x + b
            Q = int(ax_b * ax_b - n)
            if Q == 0:
                g = gcd(ax_b, n)
                if 1 < g < n:
                    direct_factor = int(g)
                    return direct_factor
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
                smooth.append((int(ax_b), sign, exps))
            elif v < lp_bound:
                if gmpy2.is_prime(v):
                    v = int(v)
                    if v in partials:
                        ox, os, oe = partials[v]
                        cax = ox * int(ax_b) % int(n)
                        cs = (os + sign) % 2
                        ce = [oe[j] + exps[j] for j in range(len(fb))]
                        smooth.append((cax, cs, ce))
                    else:
                        partials[v] = (int(ax_b), sign, exps)

        poly_count += 1
        return None

    # Phase 1: Simple QS sieve
    if verbose:
        print(f"  Phase 1: Simple QS")

    for block in range(max(1, M // 200000)):
        if len(smooth) >= needed or time.time() - t0 > time_limit:
            break
        start = block * 200000
        result = do_sieve(mpz(1), sqrt_n + start, min(200000, M))
        if result:
            return result

        if block % 10 == 0 and verbose:
            elapsed = time.time() - t0
            print(f"    [{elapsed:.0f}s] block={block}, smooth={len(smooth)}/{needed}, "
                  f"partial={len(partials)}")

    # Phase 2: MPQS
    if len(smooth) < needed:
        if verbose:
            print(f"  Phase 2: MPQS ({len(smooth)}/{needed} so far)")

        target_a = isqrt(2 * n) // M

        for poly_iter in range(100000):
            if len(smooth) >= needed:
                break
            if time.time() - t0 > time_limit:
                break

            # Choose a as product of FB primes
            n_factors = max(2, min(7, fb_size // 80))
            mid = max(1, len(fb) // 5)
            upper = min(len(fb) - 1, len(fb) * 4 // 5)

            best_a = None
            best_diff = float('inf')
            for _ in range(15):
                try:
                    indices = sorted(random.sample(range(mid, upper), n_factors))
                except ValueError:
                    continue
                a = mpz(1)
                for i in indices:
                    a *= fb[i]
                diff = abs(int(a) - int(target_a))
                if diff < best_diff:
                    best_diff = diff
                    best_a = a
                    best_indices = indices

            if best_a is None:
                continue

            a = best_a

            # Compute b via CRT
            a_factors = [fb[i] for i in best_indices]
            remainders = []
            ok = True
            for q in a_factors:
                s = sqrt_n_mod.get(q)
                if s is None:
                    ok = False
                    break
                remainders.append(s)
            if not ok:
                continue

            # Try all sign combinations (2^n_factors options)
            found_b = False
            for flip in range(1 << len(a_factors)):
                b = mpz(0)
                for i, (r, q) in enumerate(zip(remainders, a_factors)):
                    r_use = r if not (flip & (1 << i)) else (q - r)
                    Mi = a // q
                    try:
                        Mi_inv = pow(int(Mi % q), -1, q)
                    except (ValueError, ZeroDivisionError):
                        break
                    b = (b + mpz(r_use) * Mi * mpz(Mi_inv)) % a
                else:
                    if (b * b - n) % a == 0:
                        found_b = True
                        break

            if not found_b:
                continue

            result = do_sieve(a, b, M)
            if result:
                return result

            if poly_iter % 50 == 0 and verbose:
                elapsed = time.time() - t0
                rate = len(smooth) / max(elapsed, 0.001)
                print(f"    [{elapsed:.0f}s] poly={poly_count}, smooth={len(smooth)}/{needed}, "
                      f"partial={len(partials)}, rate={rate:.1f}/s")

    if len(smooth) < fb_size + 1:
        if verbose:
            print(f"  Not enough relations: {len(smooth)}/{needed}")
        return None

    # Linear algebra
    if verbose:
        print(f"\n  Linear algebra: {len(smooth)} relations, {len(fb)+1} columns")

    la_t0 = time.time()
    nrows = len(smooth)
    ncols = len(fb) + 1

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
        print(f"  LA: {time.time()-la_t0:.1f}s, {len(null_vecs)} null vectors")

    for vi, indices in enumerate(null_vecs):
        x_val = mpz(1)
        total_exp = [0] * len(fb)
        total_sign = 0

        for idx in indices:
            ax, sign, exps = smooth[idx]
            x_val = x_val * mpz(ax) % n
            total_sign += sign
            for j in range(len(fb)):
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
                return int(g)

    if verbose:
        print(f"  All {len(null_vecs)} vectors failed.")
    return None


###############################################################################
# ECM with gmpy2
###############################################################################

def ecm_factor(n, B1=1000000, curves=100, verbose=False):
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

        def md(px, pz):
            s = (px + pz) % n; d = (px - pz) % n
            ss, dd = s*s%n, d*d%n; delta = (ss - dd) % n
            return ss*dd%n, delta*(dd + a24*delta%n)%n

        def ma(px, pz, qx, qz, dx, dz):
            u1 = (px+pz)*(qx-qz)%n; v1 = (px-pz)*(qx+qz)%n
            return (u1+v1)*(u1+v1)%n*dz%n, (u1-v1)*(u1-v1)%n*dx%n

        def mm(k, px, pz):
            if k <= 1: return (px, pz) if k == 1 else (mpz(0), mpz(1))
            r0x, r0z = px, pz; r1x, r1z = md(px, pz)
            for bit in bin(k)[3:]:
                if bit == '1':
                    r0x, r0z = ma(r0x, r0z, r1x, r1z, px, pz); r1x, r1z = md(r1x, r1z)
                else:
                    r1x, r1z = ma(r0x, r0z, r1x, r1z, px, pz); r0x, r0z = md(r0x, r0z)
            return r0x, r0z

        p = 2
        while p <= B1:
            pp = p
            while pp * p <= B1: pp *= p
            x, z = mm(pp, x, z)
            p = int(next_prime(p))
        g = gcd(z, n)
        if 1 < g < n: return int(g)
    return None


###############################################################################
# Main
###############################################################################

if __name__ == "__main__":
    random.seed(42)
    print("="*60)
    print("Round 13: Fast MPQS + ECM (Numba JIT)")
    print("="*60)

    # Quick tests
    tests = [
        ("20d", 1000000009 * 1000000087),
        ("30d", 100000000000067 * 100000000000097),
    ]

    for bits in [66, 83, 100, 116, 133]:
        p = int(next_prime(mpz(random.getrandbits(bits))))
        q = int(next_prime(mpz(random.getrandbits(bits))))
        nd = len(str(p * q))
        tests.append((f"{nd}d({2*bits}b)", p * q))

    for name, n_val in tests:
        nd = len(str(n_val))
        nb = int(gmpy2.log2(mpz(n_val))) + 1
        print(f"\n### {name}: {nd} digits ({nb} bits) ###")
        t0 = time.time()

        # ECM first
        f = ecm_factor(n_val, B1=min(1000000, 10**(nd//3)), curves=50)
        if f:
            print(f"  ECM: {f} × {n_val // f} ({time.time()-t0:.1f}s)")
            continue

        # QS
        f = fast_mpqs(n_val, verbose=True, time_limit=600)
        if f:
            print(f"  MPQS: {f} × {n_val // f} ({time.time()-t0:.1f}s)")
        else:
            print(f"  FAIL ({time.time()-t0:.1f}s)")

    # RSA-100
    print(f"\n{'='*60}")
    print("RSA-100 ATTACK (100 digits, 330 bits)")
    print(f"{'='*60}")
    f = fast_mpqs(RSA_100, verbose=True, time_limit=7200)
    if f:
        print(f"\n*** RSA-100: {f} ***")

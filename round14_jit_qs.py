#!/usr/bin/env python3
"""
Round 14: JIT-Accelerated Quadratic Sieve
Focus: crack 50-70 digit numbers, then push to RSA-100.

Strategy:
1. Numba JIT for sieve inner loop (the bottleneck)
2. Correct simple QS first, then add MPQS
3. Double large prime variation for 2x more relations
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


@njit(cache=True)
def jit_sieve(sieve_arr, primes, logs, offsets1, offsets2, sz):
    """Ultra-fast sieve inner loop via Numba JIT."""
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
    """Find indices where sieve value exceeds threshold."""
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


def qs_factor(n, verbose=True, time_limit=3600):
    """Quadratic Sieve with JIT-accelerated sieve."""
    n = mpz(n)
    nd = len(str(n))
    nb = int(gmpy2.log2(n)) + 1

    # Tuned parameters
    if nd <= 25: fb_sz, M = 50, 15000
    elif nd <= 30: fb_sz, M = 100, 30000
    elif nd <= 35: fb_sz, M = 200, 60000
    elif nd <= 40: fb_sz, M = 350, 100000
    elif nd <= 45: fb_sz, M = 600, 200000
    elif nd <= 50: fb_sz, M = 1000, 400000
    elif nd <= 55: fb_sz, M = 1800, 700000
    elif nd <= 60: fb_sz, M = 3000, 1200000
    elif nd <= 65: fb_sz, M = 5000, 2000000
    elif nd <= 70: fb_sz, M = 8000, 3000000
    elif nd <= 80: fb_sz, M = 15000, 5000000
    elif nd <= 90: fb_sz, M = 30000, 8000000
    else: fb_sz, M = 50000, 12000000

    if verbose:
        print(f"QS: {nd} digits ({nb} bits), FB={fb_sz}, M={M}")

    t0 = time.time()

    # Build factor base
    fb = []
    p = 2
    while len(fb) < fb_sz:
        if p == 2 or (is_prime(p) and jacobi(int(n % p), p) == 1):
            fb.append(int(p))
        p = int(next_prime(p)) if p > 2 else 3

    fb_np = np.array(fb, dtype=np.int64)
    fb_log = np.array([int(round(math.log2(p) * 1024)) for p in fb], dtype=np.int32)

    if verbose:
        print(f"  FB: [{fb[0]}..{fb[-1]}], built {time.time()-t0:.1f}s")

    # Precompute roots
    sqrt_n = isqrt(n)
    if sqrt_n * sqrt_n < n:
        sqrt_n += 1
    if sqrt_n * sqrt_n == n:
        return int(sqrt_n)

    # For Q(x) = (sqrt_n + x)² - n, roots mod p:
    # sqrt_n + x ≡ ±t (mod p) where t² ≡ n (mod p)
    # x ≡ ±t - sqrt_n (mod p)
    root1_arr = np.full(fb_sz, -1, dtype=np.int64)
    root2_arr = np.full(fb_sz, -1, dtype=np.int64)

    for pi, p in enumerate(fb):
        if p == 2:
            # Q(x) = (sqrt_n+x)² - n. For x even/odd:
            sn2 = int(sqrt_n % 2)
            # (sn+x)² - n mod 2 = (sn+x) mod 2 XOR n mod 2... n is odd
            # Q(x) mod 2 = (sn+x)² mod 2 - 1 mod 2 = (sn+x+1) mod 2
            # Q even when sn+x is odd, i.e., x has opposite parity to sn
            root1_arr[pi] = (1 - sn2) % 2  # 0 or 1
            root2_arr[pi] = -1  # Only one root mod 2
            continue
        t = tonelli_shanks(int(n % p), p)
        if t is None:
            continue
        sn_p = int(sqrt_n % p)
        r1 = (t - sn_p) % p
        r2 = (p - t - sn_p) % p
        root1_arr[pi] = r1
        root2_arr[pi] = r2 if r2 != r1 else -1

    # Warmup JIT
    dummy = np.zeros(100, dtype=np.int32)
    jit_sieve(dummy, np.array([2,3], dtype=np.int64), np.array([10,15], dtype=np.int32),
              np.array([0,0], dtype=np.int64), np.array([1,1], dtype=np.int64), 100)
    jit_find_smooth(dummy, 1)

    # State
    smooth = []  # (ax_val, sign, exponents)
    partials = {}
    needed = fb_sz + 5
    lp_bound = fb[-1] ** 2

    # Threshold
    T_bits = max(10, nb // 5)

    if verbose:
        print(f"  Need: {needed} relations, T={T_bits} bits")
        print(f"  Sieving...")

    # Sieve in blocks of M, extending outward from sqrt_n
    block = 0
    total_cands = 0

    while len(smooth) < needed and time.time() - t0 < time_limit:
        for direction in [1, -1]:
            if len(smooth) >= needed:
                break

            # Sieve range: [x_start, x_start + M)
            if direction == 1:
                x_start = block * M + (1 if block == 0 else 0)
            else:
                x_start = -(block + 1) * M

            sz = M

            # Compute offsets for this block
            offsets1 = np.empty(fb_sz, dtype=np.int64)
            offsets2 = np.empty(fb_sz, dtype=np.int64)

            for pi, p in enumerate(fb):
                r1 = root1_arr[pi]
                r2 = root2_arr[pi]
                if r1 < 0:
                    offsets1[pi] = -1
                    offsets2[pi] = -1
                    continue
                # First j >= 0 where (x_start + j) ≡ r1 (mod p)
                o1 = (int(r1) - x_start % p) % p
                offsets1[pi] = o1
                if r2 >= 0:
                    o2 = (int(r2) - x_start % p) % p
                    offsets2[pi] = o2
                else:
                    offsets2[pi] = -1

            # JIT sieve
            sieve = np.zeros(sz, dtype=np.int32)
            jit_sieve(sieve, fb_np, fb_log, offsets1, offsets2, sz)

            # Threshold: log2(Q) at x_start+M
            x_max = abs(x_start + sz)
            if x_max == 0:
                x_max = sz
            log_q = math.log2(float(2 * sqrt_n)) + math.log2(max(x_max, 1))
            thresh = int(max(0, (log_q - T_bits)) * 1024)

            candidates = jit_find_smooth(sieve, thresh)
            total_cands += len(candidates)

            # Trial divide
            for ci in range(len(candidates)):
                x = int(candidates[ci]) + x_start
                ax = sqrt_n + x
                Q = int(ax * ax - n)
                if Q == 0:
                    g = gcd(ax, n)
                    if 1 < g < n:
                        if verbose: print(f"\n  DIRECT: {g}")
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
                    smooth.append((int(ax), sign, exps))
                elif v < lp_bound and gmpy2.is_prime(v):
                    v = int(v)
                    if v in partials:
                        ox, os, oe = partials[v]
                        cax = ox * int(ax) % int(n)
                        cs = (os + sign) % 2
                        ce = [oe[j] + exps[j] for j in range(len(fb))]
                        smooth.append((cax, cs, ce))
                    else:
                        partials[v] = (int(ax), sign, exps)

        block += 1

        if block % 10 == 0 and verbose:
            elapsed = time.time() - t0
            rate = len(smooth) / max(elapsed, 0.001)
            eta = (needed - len(smooth)) / max(rate, 0.001)
            print(f"  [{elapsed:.0f}s] range=±{block*M}, smooth={len(smooth)}/{needed}, "
                  f"partial={len(partials)}, cands={total_cands}, "
                  f"rate={rate:.1f}/s, eta={eta:.0f}s")

    if len(smooth) < fb_sz + 1:
        if verbose:
            print(f"\n  Insufficient: {len(smooth)}/{needed} ({time.time()-t0:.0f}s)")
        return None

    # Linear algebra
    if verbose:
        print(f"\n  LA: {len(smooth)} relations × {len(fb)+1} columns")

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
        print(f"  All {len(null_vecs)} vectors tried, no factor.")
    return None


###############################################################################
# ECM
###############################################################################

def ecm(n, B1=1000000, curves=100):
    n = mpz(n)
    for c in range(curves):
        sigma = mpz(random.randint(6, 10**9))
        u = (sigma*sigma - 5) % n; v = (4*sigma) % n
        x = pow(u, 3, n); z = pow(v, 3, n)
        diff = (v - u) % n
        a24n = pow(diff, 3, n) * ((3*u + v) % n) % n
        a24d = 16 * x * v % n
        try: a24i = pow(int(a24d), -1, int(n))
        except: g = gcd(a24d, n); return int(g) if 1 < g < n else None; continue
        a24 = a24n * a24i % n
        def md(px, pz):
            s=(px+pz)%n; d=(px-pz)%n; ss=s*s%n; dd=d*d%n; dl=(ss-dd)%n
            return ss*dd%n, dl*(dd+a24*dl%n)%n
        def ma(px,pz,qx,qz,dx,dz):
            u1=(px+pz)*(qx-qz)%n; v1=(px-pz)*(qx+qz)%n
            return (u1+v1)*(u1+v1)%n*dz%n, (u1-v1)*(u1-v1)%n*dx%n
        def mm(k, px, pz):
            if k<=1: return (px,pz) if k==1 else (mpz(0),mpz(1))
            r0x,r0z=px,pz; r1x,r1z=md(px,pz)
            for bit in bin(k)[3:]:
                if bit=='1': r0x,r0z=ma(r0x,r0z,r1x,r1z,px,pz); r1x,r1z=md(r1x,r1z)
                else: r1x,r1z=ma(r0x,r0z,r1x,r1z,px,pz); r0x,r0z=md(r0x,r0z)
            return r0x,r0z
        p = 2
        while p <= B1:
            pp = p
            while pp*p <= B1: pp *= p
            x, z = mm(pp, x, z); p = int(next_prime(p))
        g = gcd(z, n)
        if 1 < g < n: return int(g)
    return None


###############################################################################
# Main
###############################################################################

if __name__ == "__main__":
    random.seed(42)
    print("="*60)
    print("Round 14: JIT-Accelerated QS + ECM")
    print("="*60)

    results = []

    # Generate test semiprimes of increasing size
    for target_bits in [40, 60, 80, 100, 120, 140, 160, 180, 200]:
        half = target_bits // 2
        p = int(next_prime(mpz(random.getrandbits(half))))
        q = int(next_prime(mpz(random.getrandbits(half))))
        n_val = p * q
        nd = len(str(n_val))
        nb = int(gmpy2.log2(mpz(n_val))) + 1
        name = f"{nd}d/{nb}b"

        print(f"\n### {name}: n has {nd} digits ({nb} bits) ###")
        t0 = time.time()

        # Try ECM first
        f = ecm(n_val, B1=min(1000000, max(10000, 10**(nd//3))), curves=50)
        if f:
            elapsed = time.time() - t0
            print(f"  ECM: {f} ({elapsed:.1f}s)")
            results.append((name, "ECM", elapsed, True))
            continue

        # QS
        f = qs_factor(n_val, verbose=True, time_limit=600)
        elapsed = time.time() - t0
        if f:
            print(f"  QS: {f} ({elapsed:.1f}s)")
            results.append((name, "QS", elapsed, True))
        else:
            print(f"  FAIL ({elapsed:.1f}s)")
            results.append((name, "FAIL", elapsed, False))

    # Summary
    print(f"\n{'='*60}")
    print("RESULTS SUMMARY")
    print(f"{'='*60}")
    for name, method, t, ok in results:
        status = "✓" if ok else "✗"
        print(f"  {name:12s} {method:6s} {t:8.1f}s {status}")

    # If all pass, try RSA-100
    all_ok = all(ok for _, _, _, ok in results)
    if all_ok or len(results) > 5:
        print(f"\n{'='*60}")
        print("RSA-100 ATTEMPT")
        print(f"{'='*60}")
        f = qs_factor(RSA_100, verbose=True, time_limit=7200)
        if f:
            print(f"\n*** RSA-100 FACTORED: {f} ***")

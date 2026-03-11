#!/usr/bin/env python3
"""
Round 13 FINAL: Quadratic Sieve + MPQS
Verified correct on small examples. Now push to RSA-100.
"""

import gmpy2
from gmpy2 import mpz, isqrt, is_prime, gcd, jacobi, next_prime
import numpy as np
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


def qs_params(nd):
    """Conservative, tested parameters."""
    tbl = [(20,40,10000), (25,60,15000), (30,100,30000), (35,200,60000),
           (40,400,120000), (45,700,250000), (50,1200,500000),
           (55,2000,1000000), (60,3500,2000000), (65,5500,3000000),
           (70,9000,5000000), (75,14000,8000000), (80,20000,12000000),
           (85,30000,18000000), (90,45000,25000000), (95,60000,35000000),
           (100,80000,50000000)]
    for i in range(len(tbl)-1):
        if tbl[i][0] <= nd < tbl[i+1][0]:
            frac = (nd - tbl[i][0]) / (tbl[i+1][0] - tbl[i][0])
            fb = int(tbl[i][1] + frac * (tbl[i+1][1] - tbl[i][1]))
            M = int(tbl[i][2] + frac * (tbl[i+1][2] - tbl[i][2]))
            return fb, M
    if nd <= tbl[0][0]: return tbl[0][1], tbl[0][2]
    return tbl[-1][1], tbl[-1][2]


def mpqs_factor(n, verbose=True, time_limit=3600):
    """Multiple Polynomial Quadratic Sieve."""
    n = mpz(n)
    nd = len(str(n))
    nb = int(gmpy2.log2(n)) + 1

    fb_size, M = qs_params(nd)

    if verbose:
        print(f"MPQS: {nd} digits ({nb} bits)")
        print(f"  Factor base: {fb_size}, Sieve half-width: {M}")

    t0 = time.time()

    # Build factor base
    fb = []
    p = 2
    while len(fb) < fb_size:
        if p == 2 or (is_prime(p) and jacobi(int(n % p), p) == 1):
            fb.append(int(p))
        p = int(next_prime(p)) if p > 2 else 3

    fb_log = [round(math.log2(p) * 1024) for p in fb]

    if verbose:
        print(f"  FB built: max={fb[-1]}, {time.time()-t0:.1f}s")

    # Precompute sqrt(n) mod p for each prime
    sqrt_n_mod = {}
    for p in fb:
        if p == 2:
            sqrt_n_mod[2] = int(n % 2)
        else:
            sqrt_n_mod[p] = tonelli_shanks(int(n % p), p)

    sqrt_n = isqrt(n)
    if sqrt_n * sqrt_n < n:
        sqrt_n += 1

    # Relations
    smooth = []
    partials = {}
    needed = fb_size + 5  # Minimal padding

    # Threshold for sieve
    T_bits = max(10, nb // 6)

    # MPQS: use multiple polynomials Q(x) = (ax+b)^2 - n
    # Simple QS: a=1, b=sqrt_n
    # MPQS: choose a ≈ sqrt(2n)/M, then Q(x) values are smaller

    poly_count = 0
    total_candidates = 0

    def sieve_one_poly(a, b, M_use):
        """Sieve polynomial Q(x) = (ax+b)^2 - n with x in [-M_use, M_use)."""
        nonlocal smooth, partials, total_candidates

        sz = 2 * M_use
        sieve = np.zeros(sz, dtype=np.int32)

        a_int = int(a)

        for pi, p in enumerate(fb):
            if p == 2:
                # (a*x+b)^2 - n ≡ 0 (mod 2)
                # Check x=0 and x=1 to find the valid parity
                for test_x in [0, 1]:
                    val = int((a * test_x + b) ** 2 - n) % 2
                    if val == 0:
                        offset = (test_x + M_use) % 2
                        sieve[offset::2] += fb_log[0]
                        break
                continue

            t = sqrt_n_mod.get(p)
            if t is None:
                continue

            # (a*x + b)^2 ≡ n (mod p)
            # a*x + b ≡ ±t (mod p)
            # x ≡ (±t - b) * a^(-1) (mod p)
            try:
                a_inv = pow(a_int % p, -1, p)
            except (ValueError, ZeroDivisionError):
                g = gcd(mpz(a_int), mpz(p))
                continue

            b_mod = int(b % p)
            r1 = (a_inv * (t - b_mod)) % p
            r2 = (a_inv * (p - t - b_mod)) % p

            log_p = fb_log[pi]

            # Sieve: index j corresponds to x = j - M_use
            # We want j such that (j - M_use) ≡ r (mod p)
            # j ≡ r + M_use (mod p)
            off1 = (r1 + M_use) % p
            off2 = (r2 + M_use) % p

            sieve[off1::p] += log_p
            if off1 != off2:
                sieve[off2::p] += log_p

        # Threshold
        # Q(x) ≈ a*M^2 for MPQS at edges
        if a == 1:
            log_q = math.log2(float(2 * sqrt_n)) + math.log2(max(M_use, 1))
        else:
            log_q = math.log2(float(a)) + 2 * math.log2(max(M_use, 1))
        thresh = int(max(0, (log_q - T_bits)) * 1024)

        candidates = np.where(sieve >= thresh)[0]
        total_candidates += len(candidates)

        for idx in candidates:
            x = int(idx) - M_use
            ax_b = a * x + b
            Q = int(ax_b * ax_b - n)
            if Q == 0:
                g = gcd(ax_b, n)
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
                smooth.append((int(ax_b), sign, exps))
            elif v < fb[-1] ** 2 and gmpy2.is_prime(v):
                v = int(v)
                if v in partials:
                    ox, os, oe = partials[v]
                    cax = ox * int(ax_b) % int(n)
                    cs = (os + sign) % 2
                    ce = [oe[j] + exps[j] for j in range(len(fb))]
                    smooth.append((cax, cs, ce))
                else:
                    partials[v] = (int(ax_b), sign, exps)
        return None

    # Phase 1: Simple QS (a=1, b=sqrt_n)
    if verbose:
        print(f"\n  Phase 1: Simple QS polynomial")

    # Sieve in chunks
    chunk = min(M, 2000000)  # Max 4M entries per sieve array
    for start in range(0, M, chunk):
        if len(smooth) >= needed:
            break
        if time.time() - t0 > time_limit:
            break

        # Sieve [start, start+chunk) and [-start-chunk, -start)
        for sign_dir in [1, -1]:
            if sign_dir == 1:
                b_val = sqrt_n + start
            else:
                b_val = sqrt_n - start - chunk

            result = sieve_one_poly(mpz(1), b_val, chunk)
            if result:
                return result

        poly_count += 1
        if poly_count % 5 == 0 and verbose:
            elapsed = time.time() - t0
            rate = len(smooth) / max(elapsed, 0.001)
            print(f"    [{elapsed:.0f}s] range=±{start+chunk}, smooth={len(smooth)}/{needed}, "
                  f"partial={len(partials)}, cands={total_candidates}, "
                  f"rate={rate:.1f}/s")

    # Phase 2: MPQS - multiple polynomials with smaller Q(x)
    if len(smooth) < needed:
        if verbose:
            print(f"\n  Phase 2: MPQS with multiple polynomials")

        # Target a ≈ sqrt(2n)/M
        target_a = isqrt(2 * n) // M

        for poly_iter in range(10000):
            if len(smooth) >= needed:
                break
            if time.time() - t0 > time_limit:
                break

            # Choose a as a product of primes from factor base
            # Pick ~3-5 primes from middle of FB
            n_primes = max(2, min(6, fb_size // 50))
            mid = len(fb) // 4
            upper = len(fb) * 3 // 4

            best_a = None
            best_diff = float('inf')
            for _ in range(20):
                indices = sorted(random.sample(range(mid, upper), n_primes))
                a = mpz(1)
                for i in indices:
                    a *= fb[i]
                diff = abs(int(a - target_a))
                if diff < best_diff:
                    best_diff = diff
                    best_a = a
                    best_indices = indices

            a = best_a

            # Compute b: b^2 ≡ n (mod a)
            # Use CRT: for each prime factor q of a, find sqrt(n) mod q
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

            # CRT
            b = mpz(0)
            for i, (r, q) in enumerate(zip(remainders, a_factors)):
                Mi = a // q
                Mi_inv = pow(int(Mi % q), -1, q)
                b = (b + mpz(r) * Mi * mpz(Mi_inv)) % a

            # Verify b^2 ≡ n (mod a)
            if (b * b - n) % a != 0:
                # Try flipping signs
                found = False
                for flip in range(1, 1 << len(a_factors)):
                    b2 = mpz(0)
                    for i, (r, q) in enumerate(zip(remainders, a_factors)):
                        r_use = r if not (flip & (1 << i)) else (q - r)
                        Mi = a // q
                        Mi_inv = pow(int(Mi % q), -1, q)
                        b2 = (b2 + mpz(r_use) * Mi * mpz(Mi_inv)) % a
                    if (b2 * b2 - n) % a == 0:
                        b = b2
                        found = True
                        break
                if not found:
                    continue

            result = sieve_one_poly(a, b, M)
            if result:
                return result

            poly_count += 1
            if poly_count % 20 == 0 and verbose:
                elapsed = time.time() - t0
                rate = len(smooth) / max(elapsed, 0.001)
                print(f"    [{elapsed:.0f}s] poly={poly_count}, smooth={len(smooth)}/{needed}, "
                      f"partial={len(partials)}, rate={rate:.1f}/s")

    if len(smooth) < fb_size + 1:
        if verbose:
            print(f"\n  Not enough: {len(smooth)}/{needed}")
        return None

    # Linear algebra
    if verbose:
        print(f"\n  Linear algebra on {len(smooth)} relations...")
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
        print(f"  LA done: {time.time()-la_t0:.1f}s, {len(null_vecs)} null vectors")

    # Extract factor
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
                    print(f"\n  *** FACTOR: {g} (vec {vi}, {total:.1f}s) ***")
                    print(f"  Cofactor: {n // g}")
                return int(g)

    if verbose:
        print(f"  All {len(null_vecs)} vectors failed.")
    return None


###############################################################################
# ECM with gmpy2
###############################################################################

def ecm_factor(n, B1=1000000, curves=100, verbose=True):
    """ECM using gmpy2."""
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
            s = (px + pz) % n
            d = (px - pz) % n
            ss, dd = s*s%n, d*d%n
            delta = (ss - dd) % n
            return ss*dd%n, delta*(dd + a24*delta%n)%n

        def mont_add(px, pz, qx, qz, dx, dz):
            u1 = (px+pz)*(qx-qz)%n
            v1 = (px-pz)*(qx+qz)%n
            return (u1+v1)*(u1+v1)%n*dz%n, (u1-v1)*(u1-v1)%n*dx%n

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
            if verbose: print(f"  ECM curve {c}: {g}")
            return int(g)
        if verbose and c % 50 == 0 and c > 0:
            print(f"  ECM: {c}/{curves} curves...")
    return None


###############################################################################
# Main
###############################################################################

if __name__ == "__main__":
    random.seed(42)
    print("="*60)
    print("Round 13 FINAL: MPQS + ECM")
    print("="*60)

    # Test suite
    tests = [
        ("20-digit", 1000000009 * 1000000087),
        ("30-digit", 100000000000067 * 100000000000097),
    ]

    # Generate test semiprimes
    def make_test(bits):
        while True:
            p = int(next_prime(mpz(random.getrandbits(bits))))
            q = int(next_prime(mpz(random.getrandbits(bits))))
            if p != q:
                return p * q

    tests.append(("40-digit", make_test(66)))
    tests.append(("50-digit", make_test(83)))
    tests.append(("60-digit", make_test(100)))
    tests.append(("70-digit", make_test(116)))

    for name, n_val in tests:
        nd = len(str(n_val))
        nb = int(gmpy2.log2(mpz(n_val))) + 1
        print(f"\n### {name} ({nd} digits, {nb} bits) ###")
        t0 = time.time()

        # Try ECM first for speed
        f = ecm_factor(n_val, B1=100000, curves=50, verbose=False)
        if f:
            elapsed = time.time() - t0
            print(f"  ECM: {f} × {n_val // f} ({elapsed:.1f}s)")
            continue

        f = mpqs_factor(n_val, verbose=True, time_limit=300)
        elapsed = time.time() - t0
        if f:
            print(f"  PASS: {f} × {n_val // f} ({elapsed:.1f}s)")
        else:
            print(f"  FAIL ({elapsed:.1f}s)")

    # RSA-100
    print(f"\n{'='*60}")
    print("RSA-100 ATTACK")
    print(f"{'='*60}")

    # ECM won't work (factors are 50 digits, need B1 ~ 10^25)
    # MPQS is our only shot
    f = mpqs_factor(RSA_100, verbose=True, time_limit=7200)
    if f:
        print(f"\n*** RSA-100 FACTORED: {f} ***")

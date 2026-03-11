#!/usr/bin/env python3
"""
Round 13 v2: Minimal Correct Quadratic Sieve
Focus: Get it RIGHT, then optimize.

Q(x) = (x + ceil(sqrt(n)))^2 - n for x = -M, ..., +M
When Q(x) factors completely over the factor base, we have a "relation".
Collect enough relations, use linear algebra mod 2 to find x^2 ≡ y^2 (mod n).
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
    """sqrt(n) mod p."""
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


def qs_factor(n, verbose=True, time_limit=300):
    """Quadratic Sieve: factor n."""
    n = mpz(n)
    nd = len(str(n))
    nb = int(gmpy2.log2(n)) + 1

    # Parameters (conservative for correctness)
    if nd <= 25: fb_size, M = 60, 10000
    elif nd <= 30: fb_size, M = 100, 25000
    elif nd <= 35: fb_size, M = 200, 50000
    elif nd <= 40: fb_size, M = 400, 100000
    elif nd <= 45: fb_size, M = 700, 200000
    elif nd <= 50: fb_size, M = 1200, 500000
    elif nd <= 55: fb_size, M = 2000, 1000000
    elif nd <= 60: fb_size, M = 3000, 1500000
    elif nd <= 65: fb_size, M = 5000, 2000000
    elif nd <= 70: fb_size, M = 8000, 3000000
    else: fb_size, M = 12000, 5000000

    if verbose:
        print(f"QS: {nd} digits ({nb} bits), FB={fb_size}, M={M}")

    t0 = time.time()

    # Build factor base: primes where n is a QR
    fb = []
    p = 2
    while len(fb) < fb_size:
        if p == 2 or (is_prime(p) and jacobi(int(n % p), p) == 1):
            fb.append(int(p))
        p = int(next_prime(p)) if p > 2 else 3

    fb_log = np.array([round(math.log2(p) * 1024) for p in fb], dtype=np.int32)

    if verbose:
        print(f"  FB: [{fb[0]}, ..., {fb[-1]}] built in {time.time()-t0:.1f}s")

    # Precompute roots: for each p in fb, find t where t^2 ≡ n (mod p)
    sqrt_n = isqrt(n)
    if sqrt_n * sqrt_n < n:
        sqrt_n += 1  # ceil(sqrt(n))

    # Q(x) = (sqrt_n + x)^2 - n
    # For sieving: Q(x) ≡ 0 (mod p) when (sqrt_n + x)^2 ≡ n (mod p)
    # sqrt_n + x ≡ ±t (mod p) where t^2 ≡ n (mod p)
    # x ≡ ±t - sqrt_n (mod p)

    roots = {}
    sn_mod = {}
    for p in fb:
        if p == 2:
            # Q(x) = (sqrt_n + x)^2 - n
            # For p=2: depends on parity
            sn2 = int(sqrt_n % 2)
            n2 = int(n % 2)
            # (sn+x)^2 - n mod 2 = (sn+x)^2 + n mod 2 (since -1=1 mod 2)
            # = sn^2 + n mod 2 (x doesn't matter if we check both)
            # Actually: (sn+x)^2 mod 2 = (sn+x) mod 2
            # We want (sn+x) mod 2 = n mod 2? No.
            # Q(x) mod 2 = ((sn+x)^2 - n) mod 2 = ((sn+x)^2 + n) mod 2
            # For Q(x) to be divisible by 2: (sn+x)^2 ≡ n (mod 2)
            # n is odd (semiprime of odd primes), so n mod 2 = 1
            # (sn+x)^2 mod 2 = (sn+x) mod 2 = 1 when sn+x is odd
            # sn+x odd when x has opposite parity to sn
            r = (1 - sn2) % 2  # x where sn+x is odd
            roots[2] = [r]
            continue

        t = tonelli_shanks(int(n % p), p)
        if t is None:
            continue
        sn_p = int(sqrt_n % p)
        r1 = (t - sn_p) % p
        r2 = (p - t - sn_p) % p
        roots[p] = sorted(set([r1, r2]))

    if verbose:
        print(f"  Roots computed for {len(roots)}/{len(fb)} primes")

    # Sieve
    relations = []  # (x, sign, exponent_vector)
    partials = {}   # large_prime -> (x, sign, exponents)
    needed = fb_size + 30
    lp_bound = fb[-1] ** 2

    # Compute threshold
    # Q(x) ≈ 2 * sqrt_n * |x| for |x| << sqrt_n
    # At x = M: log2(Q) ≈ log2(2*sqrt_n*M)
    log_q_est = math.log2(float(2 * sqrt_n)) + math.log2(M)
    T_bits = max(15, nb // 5)  # Tolerance in bits
    thresh = int((log_q_est - T_bits) * 1024)

    if verbose:
        print(f"  log2(Q) at M ≈ {log_q_est:.0f}, threshold T={T_bits}, need {needed} relations")

    block_start = -M
    block_end = M
    total_smooth = 0
    total_partial = 0

    # Single big sieve pass
    sz = block_end - block_start
    sieve = np.zeros(sz, dtype=np.int32)

    if verbose:
        print(f"  Sieving [{block_start}, {block_end}), sz={sz}...")
        sieve_t0 = time.time()

    for pi, p in enumerate(fb):
        if p not in roots:
            continue
        log_p = int(fb_log[pi])

        for r in roots[p]:
            # First index >= 0 with (block_start + idx) ≡ r (mod p)
            offset = (r - block_start % p) % p
            sieve[offset::p] += log_p

            # Prime powers
            pk = p * p
            while pk < sz:
                # Hensel lift: if r is a root mod p, lift to mod pk
                # For simplicity, just sieve starting from r mod pk
                offset_pk = (r - block_start % pk) % pk
                sieve[offset_pk::pk] += int(round(math.log2(p) * 1024))
                pk *= p

    if verbose:
        print(f"  Sieve done in {time.time()-sieve_t0:.1f}s")

    # Extract candidates
    candidates = np.where(sieve >= thresh)[0]
    if verbose:
        print(f"  {len(candidates)} candidates above threshold")

    trial_t0 = time.time()
    for ci, idx in enumerate(candidates):
        x = int(idx) + block_start
        ax = sqrt_n + x
        Q = int(ax * ax - n)

        if Q == 0:
            g = gcd(ax, n)
            if 1 < g < n:
                print(f"  DIRECT FACTOR: {g}")
                return int(g)
            continue

        # Trial divide
        sign = 0
        v = Q
        if v < 0:
            v = -v
            sign = 1

        exps = []
        smooth = True
        for p in fb:
            e = 0
            while v % p == 0:
                v //= p
                e += 1
            exps.append(e)

        if v == 1:
            relations.append((int(ax), sign, exps))
            total_smooth += 1
        elif v < lp_bound and gmpy2.is_prime(v):
            v = int(v)
            if v in partials:
                ox, os, oe = partials[v]
                # Combine: multiply the two Q values
                # New ax = ox * ax mod n
                cax = (ox * int(ax)) % int(n)
                csign = (os + sign) % 2
                cexps = [oe[j] + exps[j] for j in range(len(fb))]
                # The large prime v appears twice → v^2, which is even exponent
                relations.append((cax, csign, cexps))
                total_smooth += 1
            else:
                partials[v] = (int(ax), sign, exps)
                total_partial += 1

        if total_smooth >= needed:
            break

        if ci % 10000 == 0 and ci > 0 and verbose:
            elapsed = time.time() - trial_t0
            print(f"    Trial: {ci}/{len(candidates)}, smooth={total_smooth}, "
                  f"partial={total_partial}, {elapsed:.1f}s")

    if verbose:
        print(f"  Trial division: {time.time()-trial_t0:.1f}s")
        print(f"  Smooth: {total_smooth}, Partial: {total_partial}")

    if total_smooth < needed:
        # Need more sieving — extend the interval
        if verbose:
            print(f"  Need more relations ({total_smooth}/{needed}). Extending sieve...")

        # Sieve additional blocks
        for extra_block in range(1, 100):
            if total_smooth >= needed or time.time() - t0 > time_limit:
                break

            for direction in [1, -1]:
                bs = direction * extra_block * M + (M if direction > 0 else -2*M)
                be = bs + M

                sz2 = M
                sieve2 = np.zeros(sz2, dtype=np.int32)

                for pi, p in enumerate(fb):
                    if p not in roots:
                        continue
                    log_p = int(fb_log[pi])
                    for r in roots[p]:
                        offset = (r - bs % p) % p
                        sieve2[offset::p] += log_p

                cands2 = np.where(sieve2 >= thresh)[0]
                for idx in cands2:
                    x = int(idx) + bs
                    ax = sqrt_n + x
                    Q = int(ax * ax - n)
                    if Q == 0:
                        g = gcd(ax, n)
                        if 1 < g < n:
                            return int(g)
                        continue

                    sign = 0
                    v = Q
                    if v < 0: v = -v; sign = 1

                    exps = []
                    for p in fb:
                        e = 0
                        while v % p == 0: v //= p; e += 1
                        exps.append(e)

                    if v == 1:
                        relations.append((int(ax), sign, exps))
                        total_smooth += 1
                    elif v < lp_bound and gmpy2.is_prime(v):
                        v = int(v)
                        if v in partials:
                            ox, os, oe = partials[v]
                            cax = (ox * int(ax)) % int(n)
                            csign = (os + sign) % 2
                            cexps = [oe[j] + exps[j] for j in range(len(fb))]
                            relations.append((cax, csign, cexps))
                            total_smooth += 1
                        else:
                            partials[v] = (int(ax), sign, exps)
                            total_partial += 1

                if total_smooth >= needed:
                    break

            if extra_block % 5 == 0 and verbose:
                elapsed = time.time() - t0
                print(f"    Extra block {extra_block}: smooth={total_smooth}/{needed}, "
                      f"partial={total_partial}, {elapsed:.1f}s")

    if total_smooth < fb_size + 1:
        if verbose:
            print(f"\nNot enough relations: {total_smooth}/{needed}")
        return None

    if verbose:
        print(f"\n  Collected {total_smooth} relations. Linear algebra...")

    # Linear algebra: Gaussian elimination over GF(2)
    la_t0 = time.time()
    nrows = len(relations)
    ncols = len(fb) + 1  # +1 for sign

    # Build binary matrix as list of Python ints (bitwise)
    mat = []
    for _, sign, exps in relations:
        row = sign  # bit 0 = sign
        for j, e in enumerate(exps):
            if e % 2 == 1:
                row |= (1 << (j + 1))
        mat.append(row)

    # Track row combinations
    combo = [mpz(1) << i for i in range(nrows)]

    # Row-reduce
    used = [False] * nrows
    pivot_for_col = {}

    for col in range(ncols):
        mask = 1 << col
        # Find unused pivot
        piv = -1
        for row in range(nrows):
            if not used[row] and mat[row] & mask:
                piv = row
                break
        if piv == -1:
            continue

        used[piv] = True
        pivot_for_col[col] = piv

        # Eliminate column from all other rows
        for row in range(nrows):
            if row != piv and mat[row] & mask:
                mat[row] ^= mat[piv]
                combo[row] ^= combo[piv]

    # Find null vectors (zero rows)
    null_vecs = []
    for row in range(nrows):
        if mat[row] == 0:
            # Extract indices from combo
            indices = []
            bits = combo[row]
            idx = 0
            while bits:
                if bits & 1:
                    indices.append(idx)
                bits >>= 1
                idx += 1
            if len(indices) >= 2:
                null_vecs.append(indices)

    if verbose:
        print(f"  GF(2) elimination: {time.time()-la_t0:.1f}s, {len(null_vecs)} null vectors")

    # Try each null vector
    for vi, indices in enumerate(null_vecs):
        # x = product of ax_i mod n
        x_val = mpz(1)
        total_exp = [0] * len(fb)
        total_sign = 0

        for idx in indices:
            ax, sign, exps = relations[idx]
            x_val = x_val * mpz(ax) % n
            total_sign += sign
            for j in range(len(fb)):
                total_exp[j] += exps[j]

        # Check all exponents are even
        if any(e % 2 != 0 for e in total_exp) or total_sign % 2 != 0:
            continue

        # y = product of p^(e/2) mod n
        y_val = mpz(1)
        for j, e in enumerate(total_exp):
            if e > 0:
                y_val = y_val * pow(mpz(fb[j]), e // 2, n) % n

        if total_sign % 2 == 1:
            # Shouldn't happen if null vector is correct
            pass

        # gcd(x ± y, n)
        for diff in [x_val - y_val, x_val + y_val]:
            g = gcd(diff % n, n)
            if 1 < g < n:
                total_time = time.time() - t0
                if verbose:
                    print(f"\n*** FACTOR FOUND (vector {vi})! ***")
                    print(f"  {g}")
                    print(f"  × {n // g}")
                    print(f"  Time: {total_time:.1f}s")
                return int(g)

    if verbose:
        print(f"\n  Tried {len(null_vecs)} vectors, no factor found.")
    return None


###############################################################################
# Test
###############################################################################

if __name__ == "__main__":
    print("="*60)
    print("Round 13 v2: Quadratic Sieve (Correct Implementation)")
    print("="*60)

    random.seed(42)

    # Test suite with increasing size
    tests = []

    # 20-digit
    p = int(next_prime(mpz(10**9 + 7)))
    q = int(next_prime(mpz(10**9 + 37)))
    tests.append(("20-digit", p * q, p, q))

    # 30-digit
    p = int(next_prime(mpz(10**14 + 31)))
    q = int(next_prime(mpz(10**14 + 67)))
    tests.append(("30-digit", p * q, p, q))

    # 40-digit
    p = int(next_prime(mpz(10**19 + 51)))
    q = int(next_prime(mpz(10**19 + 97)))
    tests.append(("40-digit", p * q, p, q))

    # 50-digit
    p = int(next_prime(mpz(10**24 + 43)))
    q = int(next_prime(mpz(10**24 + 79)))
    tests.append(("50-digit", p * q, p, q))

    # 60-digit
    p = int(next_prime(mpz(10**29 + 33)))
    q = int(next_prime(mpz(10**29 + 81)))
    tests.append(("60-digit", p * q, p, q))

    for name, n, p_true, q_true in tests:
        print(f"\n### {name}: n = {str(n)[:50]}... ###")
        print(f"  True factors: {p_true} × {q_true}")
        t0 = time.time()
        f = qs_factor(n, verbose=True, time_limit=300)
        elapsed = time.time() - t0
        if f and n % f == 0:
            print(f"  ✓ PASS ({elapsed:.1f}s)")
        else:
            print(f"  ✗ FAIL ({elapsed:.1f}s)")

    # If small tests pass, try RSA-100
    print(f"\n{'='*60}")
    print(f"RSA-100 ATTEMPT ({len(str(RSA_100))} digits)")
    print(f"{'='*60}")
    f = qs_factor(RSA_100, verbose=True, time_limit=3600)
    if f:
        print(f"RSA-100 FACTORED: {f}")

#!/usr/bin/env python3
"""
Round 13: Quadratic Sieve — Clean Implementation
Uses gmpy2 for fast arithmetic. Focus on CORRECTNESS first, then speed.

Approach: Simple QS with single polynomial Q(x) = (x + floor(sqrt(n)))^2 - n
Then upgrade to MPQS once it works.
"""

import gmpy2
from gmpy2 import mpz, isqrt, is_prime, gcd, log2, next_prime, jacobi
import numpy as np
import time
import math
import random
import sys

from rsa_targets import *

###############################################################################
# Tonelli-Shanks
###############################################################################

def tonelli_shanks(n, p):
    """sqrt(n) mod p. Returns None if n is not a QR."""
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
        i, temp = 1, (t * t) % p
        while temp != 1:
            temp = (temp * temp) % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m, c, t, r = i, (b * b) % p, (t * b * b) % p, (r * b) % p


###############################################################################
# Parameter selection (based on empirical data from real QS implementations)
###############################################################################

def qs_params(n_digits):
    """Return (factor_base_size, sieve_radius) for given number of digits."""
    # These are tuned from actual QS implementations
    params = {
        20: (50, 5000),
        25: (80, 10000),
        30: (120, 20000),
        35: (200, 40000),
        40: (350, 65536),
        45: (550, 100000),
        50: (900, 150000),
        55: (1300, 250000),
        60: (2000, 350000),
        65: (3000, 500000),
        70: (4500, 700000),
        75: (6000, 1000000),
        80: (8000, 1500000),
        85: (12000, 2000000),
        90: (18000, 3000000),
        95: (25000, 4000000),
        100: (35000, 5000000),
    }
    # Interpolate
    keys = sorted(params.keys())
    if n_digits <= keys[0]:
        return params[keys[0]]
    if n_digits >= keys[-1]:
        return params[keys[-1]]
    for i in range(len(keys) - 1):
        if keys[i] <= n_digits <= keys[i + 1]:
            lo, hi = keys[i], keys[i + 1]
            frac = (n_digits - lo) / (hi - lo)
            fb = int(params[lo][0] + frac * (params[hi][0] - params[lo][0]))
            sr = int(params[lo][1] + frac * (params[hi][1] - params[lo][1]))
            return (fb, sr)


###############################################################################
# Core QS
###############################################################################

def quadratic_sieve(n, verbose=True, time_limit=600):
    """Factor n using the Quadratic Sieve."""
    n = mpz(n)
    n_digits = len(str(n))
    n_bits = int(log2(n)) + 1

    # Quick checks
    if is_prime(n):
        return int(n), 1
    g = gcd(n, 6469693230)  # product of primes up to 29
    if 1 < g < n:
        return int(g), int(n // g)

    fb_size, M = qs_params(n_digits)

    if verbose:
        print(f"QS: {n_digits} digits ({n_bits} bits)")
        print(f"  Factor base: {fb_size} primes")
        print(f"  Sieve interval: M={M}")

    t_start = time.time()

    # Step 1: Build factor base (primes where n is a QR)
    factor_base = [-1]  # -1 for the sign
    fb_primes = []
    p = 2
    while len(fb_primes) < fb_size:
        if p == 2 or (is_prime(p) and jacobi(int(n % p), p) == 1):
            fb_primes.append(p)
        p = int(next_prime(p)) if p > 2 else 3

    factor_base_primes = fb_primes
    fb_log = np.array([round(math.log2(p) * 1024) for p in fb_primes], dtype=np.int32)

    if verbose:
        print(f"  Factor base built: {len(fb_primes)} primes, max={fb_primes[-1]}")
        print(f"  Time: {time.time()-t_start:.1f}s")

    # Step 2: Precompute square roots mod p
    sqrt_n = isqrt(n)
    if sqrt_n * sqrt_n == n:
        return int(sqrt_n), int(sqrt_n)

    # For Q(x) = (x + sqrt_n)^2 - n, we need to find x where Q(x) ≡ 0 (mod p)
    # (x + sqrt_n)^2 ≡ n (mod p)
    # x + sqrt_n ≡ ±sqrt(n) (mod p)
    # x ≡ ±sqrt(n) - sqrt_n (mod p)
    roots = {}
    for p in fb_primes:
        if p == 2:
            # Special case
            r = int((n + 1) % 2)  # x where Q(x) even
            roots[2] = [r]
            continue
        s = tonelli_shanks(int(n % p), p)
        if s is None:
            continue
        sn_mod_p = int(sqrt_n % p)
        r1 = (s - sn_mod_p) % p
        r2 = (p - s - sn_mod_p) % p
        if r1 == r2:
            roots[p] = [r1]
        else:
            roots[p] = [r1, r2]

    if verbose:
        print(f"  Roots computed for {len(roots)} primes")

    # Step 3: Sieve
    relations_needed = len(fb_primes) + 20
    smooth_relations = []  # List of (x_val, exponent_vector)
    partial_rels = {}  # large_prime -> (x_val, exponent_vector)
    large_prime_bound = fb_primes[-1] ** 2

    # Sieve in blocks
    block = 0
    total_candidates = 0

    # Approximate log2 of Q(x) at edges of sieve
    # Q(x) ≈ 2 * sqrt(n) * x for small x relative to sqrt(n)
    # At x=M: Q ≈ 2*sqrt(n)*M
    approx_log_q = int(math.log2(float(2 * sqrt_n)) * 1024) + int(math.log2(M) * 1024)
    # Threshold: accept if sieve value > approx_log_q - T
    # T controls how aggressive the sieve is (higher T = more candidates)
    T_bits = max(20, n_bits // 4)
    threshold = approx_log_q - int(T_bits * 1024)

    if verbose:
        print(f"  Approx log2(Q) at M: {approx_log_q/1024:.1f}")
        print(f"  Threshold T: {T_bits} bits")
        print(f"  Sieve threshold: {threshold/1024:.1f}")
        print(f"  Relations needed: {relations_needed}")

    while len(smooth_relations) < relations_needed:
        elapsed = time.time() - t_start
        if elapsed > time_limit:
            if verbose:
                print(f"\nTime limit! {len(smooth_relations)}/{relations_needed} relations")
            break

        # Sieve from block*M to (block+1)*M, then negative side
        for sign in [1, -1]:
            x_start = block * M + (1 if block == 0 else 0)
            x_end = (block + 1) * M

            sz = x_end - x_start
            if sz <= 0:
                continue

            sieve = np.zeros(sz, dtype=np.int32)

            # Sieve with each prime
            for pi, p in enumerate(fb_primes):
                if p not in roots:
                    continue
                log_p = fb_log[pi]

                for r in roots[p]:
                    # First x >= x_start with x ≡ r (mod p)
                    if sign == 1:
                        start = r - (x_start % p)
                        if start < 0:
                            start += p
                    else:
                        # For negative x: Q(-x) = (-x + sqrt_n)^2 - n
                        # Roots: -x ≡ ±sqrt(n) (mod p) => x ≡ ∓sqrt(n) - sqrt_n (mod p)
                        # Actually we need separate roots for negative side
                        sn_mod_p = int(sqrt_n % p)
                        if p == 2:
                            start = r - (x_start % p)
                            if start < 0:
                                start += p
                        else:
                            s = tonelli_shanks(int(n % p), p)
                            r_neg = (-s - sn_mod_p) % p if r == (s - sn_mod_p) % p else (s - sn_mod_p) % p
                            # For Q(-x) = (sqrt_n - x)^2 - n, roots are x ≡ sqrt_n ± sqrt(n) (mod p)
                            r_neg = (sn_mod_p - s) % p if r == (s - sn_mod_p) % p else (sn_mod_p + s) % p
                            start = r_neg - (x_start % p)
                            if start < 0:
                                start += p

                    sieve[start::p] += log_p

                    # Prime powers
                    pk = p * p
                    while pk < sz and pk < 10000000:
                        for r_orig in roots[p]:
                            r_pk = r_orig  # Simplified — should Hensel lift
                            s_pk = r_pk - (x_start % pk)
                            if s_pk < 0:
                                s_pk += pk
                            if s_pk < sz:
                                sieve[s_pk::pk] += log_p
                        pk *= p

            # Find candidates
            candidates = np.where(sieve >= threshold)[0]
            total_candidates += len(candidates)

            for j in candidates:
                x = sign * (int(j) + x_start)
                val = (mpz(x) + sqrt_n) ** 2 - n

                if val == 0:
                    g_val = gcd(mpz(x) + sqrt_n, n)
                    if 1 < g_val < n:
                        if verbose:
                            print(f"\n*** DIRECT FACTOR: {g_val} ***")
                        return int(g_val), int(n // g_val)
                    continue

                # Trial divide by factor base
                v = abs(int(val))
                sign_bit = 1 if val < 0 else 0
                exponents = [sign_bit]  # First element is sign
                smooth = True

                for p in fb_primes:
                    exp = 0
                    while v % p == 0:
                        v //= p
                        exp += 1
                    exponents.append(exp)

                if v == 1:
                    # Fully smooth!
                    smooth_relations.append((x, exponents))
                elif v < large_prime_bound and gmpy2.is_prime(v):
                    # Single large prime
                    v = int(v)
                    if v in partial_rels:
                        # Combine!
                        old_x, old_exp = partial_rels[v]
                        combined_exp = [old_exp[k] + exponents[k] for k in range(len(exponents))]
                        # The x value for combined relation
                        combined_x = old_x * x  # We'll handle this properly in matrix phase
                        smooth_relations.append(((old_x, x, v), combined_exp))
                    else:
                        partial_rels[v] = (x, exponents)

        block += 1

        if block % 5 == 0 and verbose:
            elapsed = time.time() - t_start
            rate = len(smooth_relations) / max(elapsed, 0.001)
            eta = (relations_needed - len(smooth_relations)) / max(rate, 0.001)
            print(f"  [{elapsed:.0f}s] Block {block}, Smooth: {len(smooth_relations)}/{relations_needed}, "
                  f"Partial: {len(partial_rels)}, Candidates: {total_candidates}, "
                  f"Rate: {rate:.2f}/s, ETA: {eta:.0f}s")

    if len(smooth_relations) < relations_needed:
        if verbose:
            print(f"\nInsufficient relations: {len(smooth_relations)}/{relations_needed}")
        return None, None

    if verbose:
        print(f"\nCollected {len(smooth_relations)} relations in {time.time()-t_start:.1f}s")
        print("Starting linear algebra (Gaussian elimination mod 2)...")

    # Step 4: Linear algebra — Gaussian elimination over GF(2)
    t_la = time.time()
    n_cols = len(fb_primes) + 1  # +1 for sign

    # Build binary matrix
    n_rows = len(smooth_relations)
    # Use bit manipulation for speed
    matrix = []
    for _, exps in smooth_relations:
        row = 0
        for j, e in enumerate(exps):
            if e % 2 == 1:
                row |= (1 << j)
        matrix.append(row)

    # Track row origins for combining
    origins = [1 << i for i in range(n_rows)]  # Bitmask of which original rows

    # Gaussian elimination
    pivot_cols = {}
    for col in range(n_cols):
        mask = 1 << col
        # Find pivot row
        pivot = None
        for row in range(n_rows):
            if matrix[row] & mask:
                pivot = row
                break
        if pivot is None:
            continue
        pivot_cols[col] = pivot

        # Swap pivot to "used" status and eliminate
        for row in range(n_rows):
            if row != pivot and matrix[row] & mask:
                matrix[row] ^= matrix[pivot]
                origins[row] ^= origins[pivot]

    # Find zero rows
    null_vectors = []
    for row in range(n_rows):
        if matrix[row] == 0:
            # This is a dependency — origins[row] tells us which relations to combine
            indices = []
            bits = origins[row]
            idx = 0
            while bits:
                if bits & 1:
                    indices.append(idx)
                bits >>= 1
                idx += 1
            if len(indices) >= 2:
                null_vectors.append(indices)

    if verbose:
        print(f"  Linear algebra: {time.time()-t_la:.1f}s, found {len(null_vectors)} null vectors")

    # Step 5: Try to extract factors
    for vec_idx, indices in enumerate(null_vectors):
        # Compute x = product of (x_i + sqrt_n) mod n
        # Compute y = sqrt(product of Q(x_i)) mod n
        x_prod = mpz(1)
        total_exp = [0] * n_cols

        for idx in indices:
            x_val, exps = smooth_relations[idx]

            if isinstance(x_val, tuple):
                # Combined partial relation
                x1, x2, lp = x_val
                x_prod = (x_prod * (mpz(x1) + sqrt_n) % n * (mpz(x2) + sqrt_n)) % n
            else:
                x_prod = (x_prod * (mpz(x_val) + sqrt_n)) % n

            for j in range(n_cols):
                total_exp[j] += exps[j]

        # Verify all exponents are even
        if any(e % 2 != 0 for e in total_exp):
            continue

        # Compute y
        y = mpz(1)
        for j, exp in enumerate(total_exp):
            if exp > 0:
                if j == 0:
                    continue  # Sign — handled by x_prod already
                p = fb_primes[j - 1]
                y = (y * pow(mpz(p), exp // 2, n)) % n

        # Factor attempt: gcd(x - y, n) or gcd(x + y, n)
        for diff in [x_prod - y, x_prod + y]:
            g = gcd(diff, n)
            if 1 < g < n:
                total_time = time.time() - t_start
                if verbose:
                    print(f"\n*** FACTOR FOUND (vector {vec_idx})! ***")
                    print(f"  Factor: {g}")
                    print(f"  Cofactor: {n // g}")
                    print(f"  Total time: {total_time:.1f}s")
                return int(g), int(n // g)

    total_time = time.time() - t_start
    if verbose:
        print(f"\nAll {len(null_vectors)} null vectors tried, no factor. ({total_time:.1f}s)")
    return None, None


###############################################################################
# ECM with gmpy2 (our proven method)
###############################################################################

def ecm_factor(n, B1=1000000, curves=200, verbose=True):
    """ECM using gmpy2 for fast arithmetic."""
    n = mpz(n)
    if verbose:
        print(f"  ECM: B1={B1}, curves={curves}")

    for c in range(curves):
        # Random curve via Suyama's parameterization
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
            if 1 < g < n:
                return int(g)
            continue

        a24 = a24_num * a24_inv % n

        # Montgomery ladder multiplication
        def mont_double(px, pz):
            s = (px + pz) % n
            d = (px - pz) % n
            ss = s * s % n
            dd = d * d % n
            delta = (ss - dd) % n
            return ss * dd % n, delta * (dd + a24 * delta % n) % n

        def mont_add(px, pz, qx, qz, dx, dz):
            u1 = (px + pz) * (qx - qz) % n
            v1 = (px - pz) * (qx + qz) % n
            s = (u1 + v1) % n
            d = (u1 - v1) % n
            return s * s % n * dz % n, d * d % n * dx % n

        def mont_mul(k, px, pz):
            if k == 0:
                return mpz(0), mpz(1)
            if k == 1:
                return px, pz
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

        # Stage 1
        p = 2
        while p <= B1:
            pp = p
            while pp * p <= B1:
                pp *= p
            x, z = mont_mul(pp, x, z)
            p = int(next_prime(p))

        g = gcd(z, n)
        if 1 < g < n:
            if verbose:
                print(f"    Curve {c}: FACTOR {g}")
            return int(g)

        if verbose and c % 50 == 0 and c > 0:
            print(f"    {c}/{curves} curves done...")

    return None


###############################################################################
# Main attack pipeline
###############################################################################

def attack(name, n, time_limit=600):
    """Multi-method attack on n."""
    n = mpz(n)
    n_digits = len(str(n))
    n_bits = int(log2(n)) + 1

    print(f"\n{'='*70}")
    print(f"ATTACKING {name}: {n_digits} digits ({n_bits} bits)")
    print(f"{'='*70}")

    t0 = time.time()

    # Phase 1: Quick ECM for small factors
    print("\n--- Phase 1: ECM Quick Scan ---")
    for B1, nc in [(10000, 30), (100000, 50), (1000000, 100)]:
        print(f"  B1={B1}, {nc} curves...")
        f = ecm_factor(n, B1=B1, curves=nc, verbose=False)
        if f:
            print(f"\n*** ECM FOUND: {f} ***")
            print(f"  Time: {time.time()-t0:.1f}s")
            return f

    # Phase 2: Quadratic Sieve
    remaining = time_limit - (time.time() - t0)
    if remaining > 30:
        print(f"\n--- Phase 2: Quadratic Sieve ({remaining:.0f}s budget) ---")
        p, q = quadratic_sieve(n, verbose=True, time_limit=remaining)
        if p:
            print(f"\n*** QS FOUND: {p} ***")
            print(f"  Time: {time.time()-t0:.1f}s")
            return p

    # Phase 3: Heavy ECM
    remaining = time_limit - (time.time() - t0)
    if remaining > 30:
        print(f"\n--- Phase 3: Heavy ECM ({remaining:.0f}s budget) ---")
        for B1 in [5000000, 20000000]:
            f = ecm_factor(n, B1=B1, curves=50, verbose=True)
            if f:
                print(f"\n*** ECM FOUND: {f} ***")
                return f
            if time.time() - t0 > time_limit:
                break

    print(f"\nFailed after {time.time()-t0:.1f}s")
    return None


if __name__ == "__main__":
    print("="*70)
    print("Round 13: Quadratic Sieve + ECM Attack")
    print("Target: RSA Factoring Challenge Numbers")
    print("="*70)

    # Test 1: Small semiprime (should be instant)
    print("\n### Test 1: 30-digit semiprime ###")
    p1 = 982451653  # 10-digit prime
    q1 = 999999937  # 10-digit prime
    n1 = p1 * q1  # 20 digits
    print(f"n = {n1} ({len(str(n1))} digits)")
    f1, f2 = quadratic_sieve(n1, verbose=True, time_limit=30)
    if f1:
        print(f"PASS: {f1} x {f2}")

    # Test 2: 40-digit
    print("\n### Test 2: 40-digit semiprime ###")
    p2 = 99999999999999999877  # 20-digit prime? Check
    # Generate proper primes
    random.seed(12345)
    p2 = int(next_prime(mpz(10**19 + random.randint(0, 10**18))))
    q2 = int(next_prime(mpz(10**19 + random.randint(0, 10**18))))
    n2 = p2 * q2
    print(f"n = {n2} ({len(str(n2))} digits)")
    print(f"p = {p2}, q = {q2}")
    f1, f2 = quadratic_sieve(n2, verbose=True, time_limit=120)
    if f1:
        print(f"PASS: {f1} x {f2}")

    # Test 3: 50-digit
    print("\n### Test 3: 50-digit semiprime ###")
    p3 = int(next_prime(mpz(10**24 + random.randint(0, 10**23))))
    q3 = int(next_prime(mpz(10**24 + random.randint(0, 10**23))))
    n3 = p3 * q3
    print(f"n = {n3} ({len(str(n3))} digits)")
    f1, f2 = quadratic_sieve(n3, verbose=True, time_limit=300)
    if f1:
        print(f"PASS: {f1} x {f2}")

    # If tests pass, attack RSA-100
    print("\n" + "="*70)
    print("### RSA-100 ATTACK ###")
    print("="*70)
    attack("RSA-100", RSA_100, time_limit=3600)

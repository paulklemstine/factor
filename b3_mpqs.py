#!/usr/bin/env python3
"""
B3-MPQS: Pythagorean Parabolic Multiple Polynomial Quadratic Sieve
===================================================================

Key insight from the B3 Parabolic Discovery:
    Berggren B3 = [[1,2],[0,1]] is parabolic → B3^k creates arithmetic
    progressions in m, giving quadratic polynomials sievable by QS.

    The catch: pure B3 has a = 4n₀² (perfect square) → trivial GCD.
    Fix: use CRT-based square-free a from FB primes, which is standard
    MPQS but inspired by the B3 polynomial structure.

Implementation: MPQS with CRT polynomial generation.
    Q(x) = a·x² + 2b·x + c, where:
        a = product of s FB primes (square-free)
        b² ≡ N (mod a) via CRT
        c = (b² - N) / a
    Sieve Q(x) for smooth values. Relation: (ax+b)² ≡ Q(x) (mod N).

Memory-safe: all arrays bounded, <2GB total.
"""

import time
import math
import sys
import numpy as np
import gmpy2
from gmpy2 import mpz, isqrt, gcd, is_prime, next_prime, legendre


def _build_factor_base(N, B):
    """Primes p <= B where N is a QR mod p (or p divides N)."""
    fb = [2]
    p = mpz(3)
    while p <= B:
        if legendre(N, p) >= 0:
            fb.append(int(p))
        p = next_prime(p)
    return fb


def _tonelli_shanks(n, p):
    """Compute sqrt(n) mod p."""
    n = n % p
    if n == 0:
        return 0
    if p == 2:
        return n
    if pow(n, (p - 1) // 2, p) != 1:
        return None
    if p % 4 == 3:
        return pow(n, (p + 1) // 4, p)
    Q, S = p - 1, 0
    while Q % 2 == 0:
        Q //= 2
        S += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    M, c, t, R = S, pow(z, Q, p), pow(n, Q, p), pow(n, (Q + 1) // 2, p)
    while True:
        if t == 1:
            return R
        i, tmp = 1, t * t % p
        while tmp != 1:
            tmp = tmp * tmp % p
            i += 1
        b = pow(c, 1 << (M - i - 1), p)
        M, c, t, R = i, b * b % p, t * b * b % p, R * b % p


def b3_mpqs_factor(N, verbose=True, time_limit=600):
    """
    Factor N using B3-inspired MPQS with CRT square-free a.
    """
    N = mpz(N)
    nd = len(str(N))
    nb = int(gmpy2.log2(N)) + 1

    # Quick checks
    if N <= 1:
        return 0
    if N % 2 == 0:
        return 2
    for p in [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
        if N % p == 0:
            return int(p)
    if is_prime(N):
        return int(N)
    sq = isqrt(N)
    if sq * sq == N:
        return int(sq)

    t0 = time.time()
    N_int = int(N)

    # Parameter selection
    ln_n = float(gmpy2.log(N))
    ln_ln_n = math.log(max(ln_n, 2.0))
    L_exp = math.sqrt(ln_n * ln_ln_n)

    alpha = 0.5
    B = int(math.exp(alpha * L_exp))
    B = max(B, 200)
    B = min(B, 300_000)

    fb = _build_factor_base(N, B)
    fb_size = len(fb)
    needed = int(fb_size * 1.10) + 10

    lp_bound = min(B * 100, B * B)

    # Sieve half-interval
    sieve_M = min(200_000, max(20_000, B * 4))

    # Precompute Tonelli-Shanks roots for N mod each FB prime
    # t_roots[i] = sqrt(N) mod fb[i], or -1 if N is not QR
    t_roots = []
    for p in fb:
        if p == 2:
            t_roots.append(int(N % 2))
        else:
            r = _tonelli_shanks(int(N % p), p)
            t_roots.append(r if r is not None else -1)

    # Log table
    LOG_SCALE = 256
    fb_logs = [int(round(math.log2(p) * LOG_SCALE)) for p in fb]

    # Number of primes per 'a' value
    # Target: a ≈ sqrt(2N) / M for optimal residue size
    target_a = isqrt(2 * N) // sieve_M
    if target_a < 2:
        target_a = mpz(2)
    log_target = float(gmpy2.log(target_a))

    # Pick s primes whose product ≈ target_a
    # Use primes from the middle of the FB for balanced size
    # Skip primes that are too small or too large
    import bisect
    fb_sorted = sorted(fb[1:])  # skip 2
    target_prime_size = int(math.exp(log_target / max(1, nb // 20)))
    target_prime_size = max(7, min(target_prime_size, B // 2))

    # Find the range of primes to use for 'a' construction
    a_prime_start = bisect.bisect_left(fb_sorted, target_prime_size // 2)
    a_prime_end = bisect.bisect_right(fb_sorted, target_prime_size * 3)
    a_prime_start = max(0, a_prime_start)
    a_prime_end = min(len(fb_sorted), a_prime_end)
    if a_prime_end - a_prime_start < 5:
        a_prime_start = max(0, len(fb_sorted) // 4)
        a_prime_end = min(len(fb_sorted), 3 * len(fb_sorted) // 4)
    a_primes_pool = fb_sorted[a_prime_start:a_prime_end]

    # Determine s (number of primes per a)
    if len(a_primes_pool) > 0:
        avg_log = sum(math.log(p) for p in a_primes_pool) / len(a_primes_pool)
        s = max(1, round(log_target / avg_log))
        s = min(s, len(a_primes_pool), 10)
    else:
        s = 1
        a_primes_pool = fb_sorted[:max(10, len(fb_sorted))]

    # T_bits for sieve threshold
    T_bits = nb // 4 - 1 if nb >= 180 else nb // 4 - 2
    T_bits = max(T_bits, 5)
    threshold = int((float(gmpy2.log2(sieve_M * target_a)) - T_bits) * LOG_SCALE)
    threshold = max(threshold, 1)

    if verbose:
        print(f"B3-MPQS: {nd}d ({nb}b), B={B:,}, |FB|={fb_size:,}, "
              f"need={needed:,}, M={sieve_M:,}")
        print(f"  s={s}, |a_pool|={len(a_primes_pool)}, "
              f"target_a≈{target_a}, T_bits={T_bits}")

    # ===== Relation collection =====
    smooth = []
    partials = {}
    n_lp = 0
    n_polys = 0
    n_full = 0
    rng = __import__('random').Random(42)

    while len(smooth) < needed:
        if time.time() - t0 > time_limit * 0.9:
            break

        # Select s primes for a (square-free)
        if s >= len(a_primes_pool):
            a_indices = list(range(len(a_primes_pool)))
        else:
            a_indices = sorted(rng.sample(range(len(a_primes_pool)), s))
        a_factors = [a_primes_pool[i] for i in a_indices]
        a_val = 1
        for p in a_factors:
            a_val *= p

        # Find which FB indices these a-primes correspond to
        a_fb_indices = []
        for p in a_factors:
            try:
                a_fb_indices.append(fb.index(p))
            except ValueError:
                pass

        # Compute b via CRT: b² ≡ N (mod a)
        # For each a-prime q, find t where t² ≡ N (mod q)
        b_parts = []
        valid = True
        for q in a_factors:
            idx = fb.index(q) if q in fb else -1
            if idx < 0 or t_roots[idx] < 0:
                valid = False
                break
            b_parts.append((t_roots[idx], q))
        if not valid:
            continue

        # CRT to combine
        b_val = 0
        for t_i, q_i in b_parts:
            # b ≡ t_i (mod q_i)
            M_i = a_val // q_i
            M_i_inv = pow(M_i, q_i - 2, q_i)  # M_i^(-1) mod q_i
            b_val += t_i * M_i * M_i_inv
        b_val = b_val % a_val

        # Ensure b² ≡ N (mod a)
        if (b_val * b_val - int(N)) % a_val != 0:
            # Try the other root
            b_val = a_val - b_val
            if (b_val * b_val - int(N)) % a_val != 0:
                continue

        c_val = (b_val * b_val - int(N)) // a_val

        n_polys += 1

        # Precompute sieve offsets for each FB prime
        # Q(x) = a*x² + 2*b*x + c
        # Q(x) ≡ 0 (mod p) when a*x² + 2*b*x + c ≡ 0 (mod p)
        # Roots: x ≡ (-b ± t) * a^(-1) (mod p) where t² ≡ N (mod p)
        offsets1 = [-1] * fb_size
        offsets2 = [-1] * fb_size

        for i in range(fb_size):
            p = fb[i]
            if a_val % p == 0:
                # p divides a: single root
                # Q(x)/p: need special handling
                if p == 2:
                    continue
                a_inv_p = pow(a_val // p % p, p - 2, p)
                # Q(x) = a*x² + 2*b*x + c, and p | a
                # 2*b*x + c ≡ 0 (mod p)
                if (2 * b_val) % p == 0:
                    continue
                inv_2b = pow(2 * b_val % p, p - 2, p)
                root = (-c_val % p * inv_2b) % p
                offsets1[i] = (root + sieve_M) % p
                continue

            t = t_roots[i]
            if t < 0:
                continue

            a_inv = pow(a_val % p, p - 2, p)

            r1 = ((-b_val + t) * a_inv) % p
            r2 = ((-b_val - t) * a_inv) % p

            # Shift to [0, sieve_M) range: position = root + sieve_M
            offsets1[i] = (int(r1) + sieve_M) % p
            offsets2[i] = (int(r2) + sieve_M) % p

        # Sieve over [-sieve_M, sieve_M)
        sieve_len = 2 * sieve_M
        sieve = np.zeros(sieve_len, dtype=np.int32)

        for i in range(fb_size):
            p = fb[i]
            if p < 16:
                continue
            lp_val = fb_logs[i]
            o1 = offsets1[i]
            if o1 >= 0:
                pos = o1
                while pos < sieve_len:
                    sieve[pos] += lp_val
                    pos += p
            o2 = offsets2[i]
            if o2 >= 0 and o2 != o1:
                pos = o2
                while pos < sieve_len:
                    sieve[pos] += lp_val
                    pos += p

        # Find candidates above threshold
        hits = np.where(sieve >= threshold)[0]

        for pos_idx in range(len(hits)):
            if len(smooth) >= needed:
                break
            pos = int(hits[pos_idx])
            x = pos - sieve_M  # actual x value in [-M, M)

            # Compute Q(x) = a*x² + 2*b*x + c
            Q_val = a_val * x * x + 2 * b_val * x + c_val

            if Q_val == 0:
                continue

            # The relation: (a*x + b)² ≡ a*Q(x) (mod N)
            # So we sieve Q(x), but the actual smooth value is Q(x)
            # and ax_val = (a*x + b) mod N

            ax_val = (a_val * x + b_val) % N_int

            # Direct GCD check
            g = int(gcd(mpz(ax_val), N))
            if 1 < g < N_int:
                if verbose:
                    print(f"\n  *** DIRECT FACTOR: {g} ({time.time()-t0:.1f}s) ***")
                return g

            # Trial divide |Q(x)| over FB
            sign = 0
            cof = abs(Q_val)
            if Q_val < 0:
                sign = 1

            exps = [0] * fb_size
            for i in range(fb_size):
                p = fb[i]
                if p * p > cof:
                    break
                if cof % p == 0:
                    e = 0
                    while cof % p == 0:
                        cof //= p
                        e += 1
                    exps[i] = e
                    if cof == 1:
                        break

            if cof == 1:
                # Fully smooth: (ax+b)² ≡ a·Q(x) (mod N)
                # But we need: ax² ≡ Q(x) (mod N)? No.
                # (a*x + b)² = a²x² + 2abx + b² = a(ax² + 2bx) + b²
                #             = a(ax² + 2bx + c) + b² - ac = aQ(x) + N
                # So (ax+b)² ≡ aQ(x) (mod N)
                # We need (ax+b)² ≡ aQ(x) (mod N) and aQ(x) to be a
                # perfect square for the combining step.
                # Since a is square-free, we track a's prime factors in exps.
                for fi in a_fb_indices:
                    exps[fi] += 1  # a contributes one factor of each a-prime
                smooth.append((ax_val, sign, exps))
                n_full += 1
            elif 1 < cof <= lp_bound and is_prime(mpz(cof)):
                lp = cof
                # Add a's contribution
                a_exps = exps[:]
                for fi in a_fb_indices:
                    a_exps[fi] += 1
                if lp in partials:
                    x2, s2, e2 = partials.pop(lp)
                    cs = (sign + s2) % 2
                    ce = [a_exps[j] + e2[j] for j in range(fb_size)]
                    lp_inv = int(gmpy2.invert(mpz(lp), N))
                    cx = (ax_val * x2 % N_int) * lp_inv % N_int
                    smooth.append((cx, cs, ce))
                    n_lp += 1
                else:
                    partials[lp] = (ax_val, sign, a_exps)

        # Progress
        if verbose and n_polys % 200 == 0:
            elapsed = time.time() - t0
            rate = len(smooth) / max(elapsed, 0.01)
            eta = (needed - len(smooth)) / max(rate, 0.001)
            print(f"  poly #{n_polys}: {len(smooth)}/{needed} "
                  f"({n_full} full + {n_lp} LP), "
                  f"rate={rate:.1f}/s eta={min(eta,99999):.0f}s")

    elapsed_sieve = time.time() - t0
    if verbose:
        print(f"\n  Sieve: {len(smooth):,} rels ({n_full} full + {n_lp} LP) "
              f"in {elapsed_sieve:.1f}s, {n_polys} polys")

    if len(smooth) < fb_size + 2:
        if verbose:
            print(f"  Insufficient: {len(smooth)}/{fb_size+2}")
        return 0

    # ===== GF(2) Gaussian Elimination =====
    nrows = len(smooth)
    ncols = fb_size + 1

    if verbose:
        print(f"  LA: {nrows} x {ncols}")

    la_t0 = time.time()
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
            if indices:
                null_vecs.append(indices)

    if verbose:
        print(f"  LA: {time.time()-la_t0:.1f}s, {len(null_vecs)} null vecs")

    # ===== Factor Extraction =====
    # (ax+b)² ≡ a·Q(x) (mod N). When product of a·Q(x) = s²:
    # product(ax+b)² ≡ s² (mod N), gcd(product(ax+b) ± s, N) → factor
    n_tried = 0
    for indices in null_vecs:
        x_val = mpz(1)
        total_exp = [0] * fb_size
        total_sign = 0

        for idx in indices:
            xk, sign, exps = smooth[idx]
            x_val = x_val * mpz(xk) % N
            total_sign += sign
            for j in range(fb_size):
                total_exp[j] += exps[j]

        if any(e % 2 != 0 for e in total_exp) or total_sign % 2 != 0:
            continue

        y_val = mpz(1)
        for j, e in enumerate(total_exp):
            if e > 0:
                y_val = y_val * pow(mpz(fb[j]), e // 2, N) % N

        n_tried += 1
        for diff in [x_val - y_val, x_val + y_val]:
            g = int(gcd(diff % N, N))
            if 1 < g < N_int:
                total_t = time.time() - t0
                if verbose:
                    print(f"\n  *** FACTOR: {g} ({nd}d, {total_t:.1f}s, "
                          f"{len(smooth)} rels [{n_full}+{n_lp} LP], "
                          f"{n_tried}/{len(null_vecs)} vecs) ***")
                return g

    if verbose:
        print(f"  {len(null_vecs)} null vecs tried, no non-trivial factor.")
    return 0


# ===== CLI =====
if __name__ == "__main__":
    import random

    def _gen_semiprime(nd_target, rng):
        half_bits = int(nd_target * 3.32 / 2)
        while True:
            p = int(next_prime(mpz(rng.getrandbits(half_bits))))
            q = int(next_prime(mpz(rng.getrandbits(half_bits))))
            if p != q:
                N = p * q
                if len(str(N)) >= nd_target - 1:
                    return N, p, q

    if len(sys.argv) > 1 and sys.argv[1] == "bench":
        print("=" * 70)
        print("B3-MPQS Benchmark")
        print("=" * 70)

        rng = random.Random(42)
        results = []
        for nd_target in [20, 25, 30, 35, 40, 45, 50, 55]:
            N, p, q = _gen_semiprime(nd_target, rng)
            nd = len(str(N))
            print(f"\n{'='*50}")
            print(f"Target: {nd}d ({int(gmpy2.log2(mpz(N)))+1}b)")
            print(f"{'='*50}")
            t0 = time.time()
            f = b3_mpqs_factor(N, verbose=True, time_limit=300)
            elapsed = time.time() - t0
            if f and f > 1 and N % f == 0:
                print(f"  PASS: {f} x {N//f} in {elapsed:.1f}s")
                results.append((nd, elapsed, "PASS"))
            else:
                print(f"  FAIL in {elapsed:.1f}s")
                results.append((nd, elapsed, "FAIL"))

        print(f"\n{'='*70}")
        print(f"{'Digits':>6} {'Time':>8} {'Result':>8}")
        print(f"{'-'*6:>6} {'-'*8:>8} {'-'*8:>8}")
        for nd, t, r in results:
            print(f"{nd:>6} {t:>7.1f}s {r:>8}")

    elif len(sys.argv) > 1 and sys.argv[1] == "test":
        print("B3-MPQS Quick Test")
        print("=" * 40)
        rng = random.Random(123)
        passes = 0
        fails = 0
        for nd in [15, 20, 25, 30, 35]:
            N, p, q = _gen_semiprime(nd, rng)
            print(f"\n  {len(str(N))}d: N={N}")
            t0 = time.time()
            f = b3_mpqs_factor(N, verbose=True, time_limit=120)
            elapsed = time.time() - t0
            if f and f > 1 and N % f == 0:
                print(f"    PASS: {f} in {elapsed:.1f}s")
                passes += 1
            else:
                print(f"    FAIL in {elapsed:.1f}s")
                fails += 1
        print(f"\n{passes} passed, {fails} failed")

    elif len(sys.argv) > 1:
        N = int(sys.argv[1])
        tl = int(sys.argv[2]) if len(sys.argv) > 2 else 300
        f = b3_mpqs_factor(N, verbose=True, time_limit=tl)
        if f and f > 1:
            print(f"\nResult: {N} = {f} * {N // f}")
        else:
            print(f"\nFailed to factor {N}")

    else:
        print("Usage:")
        print("  b3_mpqs.py test          — quick test on small semiprimes")
        print("  b3_mpqs.py bench         — benchmark 20d-55d")
        print("  b3_mpqs.py <N> [timeout] — factor a specific number")

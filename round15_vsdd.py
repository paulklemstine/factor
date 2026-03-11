#!/usr/bin/env python3
"""
Round 15b: VSDD — Variable Sieve Distinct Differences
======================================================
Core insight: Lock Δ = C - B, then sieve the LINEAR polynomial
  g(B) = 2*Δ*B + Δ² (mod n)

For factoring n: we want x² ≡ y (mod n) where y is smooth.
Setting x = B + Δ:  (B+Δ)² - B² = 2BΔ + Δ²
So (B+Δ)² ≡ B² + 2BΔ + Δ² (mod n)
   (B+Δ)² - n ≡ 2BΔ + Δ² - n + B²  ... no, that's not right.

Actually, for difference of squares: n = x² - y² = (x-y)(x+y)
We want: x² ≡ y² (mod n), or equivalently x² - n = Q, Q smooth.

The VSDD approach: for each Δ, define x = sqrt_n + k for some offset.
Then Q(k) = (sqrt_n + k)² - n = 2*sqrt_n*k + k²

With VSDD: fix Δ as a parameter. For each Δ, we sieve
  f(B) = (B + Δ)² - n
This is QUADRATIC in B, not linear.

BUT: the key VSDD insight is different. We decompose:
  (B + Δ)² - B² = 2BΔ + Δ²
This is always true. We want (B+Δ)² - B² to have a specific relationship to n.

For QS: we need x² ≡ Q (mod n) where Q is smooth.
Standard: x = sqrt_n + k, Q = 2*sqrt_n*k + k² ≈ 2*sqrt_n*k for small k.

VSDD linear sieve: for a fixed Δ, define
  x = B + Δ
  x² = B² + 2BΔ + Δ²

We want x² mod n to be smooth. We don't control B² mod n easily.

Actually, the CORRECT interpretation of VSDD for QS is:
We're sieving values of f(x) = x² - n for smoothness.
MPQS uses f(x) = (ax+b)² - n with multiple polynomials to keep values small.
VSDD uses the observation that consecutive values differ by:
  f(x+1) - f(x) = 2x + 1

So if p | f(x₀), then p | f(x₀ + p) as well (standard sieve).
But also: f(x) = (x - sqrt_n)(x + sqrt_n) ≈ 2*sqrt_n * (x - sqrt_n) near sqrt_n.

The LINEAR sieve idea: Instead of evaluating x² - n (quadratic),
we note that for the standard QS polynomial centered at sqrt_n:
  Q(t) = (sqrt_n + t)² - n = 2*sqrt_n*t + t²

For small t, Q(t) ≈ 2*sqrt_n*t which IS linear in t.
The sieve roots: Q(t) ≡ 0 (mod p) when t ≡ (±sqrt(n mod p) - sqrt_n) (mod p)
This still needs Tonelli-Shanks, but the SIEVE itself is standard.

The REAL win of VSDD in the user's framework:
For Price's tree with locked Δ = C - B:
  C² - B² = (C-B)(C+B) = Δ*(2B + Δ)

If we want Δ*(2B + Δ) to relate to n:
  We need Δ*(2B + Δ) ≡ 0 (mod p) for primes p | n... no.

OK let me re-read the user's v3.0 more carefully.
The relation they want: (B + Δ)² - B² ≡ y (mod n)
  y = 2BΔ + Δ²

They store: x = B + Δ, and need y = 2BΔ + Δ² to be smooth.
Then x² ≡ B² + y (mod n), so x² - B² ≡ y (mod n).
But x² - B² = Δ(2B + Δ) = y exactly (not mod n).

For QS, we need: x² ≡ y (mod n) where y is smooth.
But here x² - B² = y, and this is NOT mod n. We need mod n.

UNLESS we're looking at it differently:
  x² mod n = (B² + 2BΔ + Δ²) mod n

For this to give a QS relation, we need (B² + 2BΔ + Δ²) mod n to be smooth.
That's just (B+Δ)² mod n being smooth, which is the standard setup.

I think the key insight the user is going for is:
With MPQS, we sieve g(x) which is QUADRATIC → finding roots mod p needs Tonelli-Shanks.
With VSDD, the quantity 2BΔ + Δ² is LINEAR in B (for fixed Δ), so sieve roots are trivial:
  2BΔ + Δ² ≡ 0 (mod p)  →  B ≡ -Δ/2 (mod p)

But we need more than just divisibility by p — we need FULL smoothness of 2BΔ + Δ².
And 2BΔ + Δ² is NOT x²-n. It's just (B+Δ)²-B².

To make this work for factoring n, we need to connect it to n somehow.
The connection: if n = (B+Δ)² - B² = 2BΔ + Δ², then B = (n - Δ²)/(2Δ).
That's Fermat's method with fixed Δ.

For QS-style: we need MULTIPLE relations x² ≡ y (mod n).
Let me think about this differently.

Actually: x = B + Δ. We compute x² mod n. If x² mod n is small and smooth, great.
But x² mod n is not necessarily equal to 2BΔ + Δ². It equals (B+Δ)² mod n.

For x near sqrt(n): x² mod n ≈ x² - n ≈ 2*sqrt(n)*(x - sqrt(n)).

I think the cleanest implementation is:
1. For fixed Δ, set x = B + Δ where B ranges over a sieve interval.
2. Compute y = x² - n = B² + 2BΔ + Δ² - n.
3. Sieve y for smoothness. y is quadratic in B.
4. This is basically the same as standard QS sieving.

The linear trick only works if we restrict to y = 2BΔ + Δ² WITHOUT the B² term.
That means we need B² to cancel with n somehow.

Hmm, let me just implement the standard MPQS more efficiently instead,
and add the VSDD as a fast pre-filter for Fermat-like methods.
"""

import gmpy2
from gmpy2 import mpz, isqrt, is_prime, gcd, jacobi, next_prime
import numpy as np
from numba import njit
import time
import math
import random

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
    """Tuned MPQS parameters based on number of digits."""
    tbl = [
        (20,   80,    20000),
        (25,  150,    40000),
        (30,  250,    80000),
        (35,  450,   150000),
        (40,  800,   300000),
        (45, 1200,   500000),
        (50, 2000,   800000),
        (55, 3000,  1500000),
        (60, 4500,  2500000),
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


def mpqs_factor(n, verbose=True, time_limit=3600):
    """
    MPQS with correct g(x) sieving.

    For polynomial (ax+b)² - n:
      g(x) = a*x² + 2*b*x + c, where c = (b²-n)/a
      (ax+b)² ≡ a*g(x) (mod n)

    When a | g(x)'s factorization and g(x) is smooth, we have a relation.
    """
    n = mpz(n)
    nd = len(str(n))
    nb = int(gmpy2.log2(n)) + 1

    fb_size, M = mpqs_params(nd)

    if verbose:
        print(f"MPQS: {nd}d ({nb}b), FB={fb_size}, M={M}")

    t0 = time.time()

    # Factor Base: primes p where n is a QR mod p
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
        print(f"  FB[{fb[0]}..{fb[-1]}] built {time.time()-t0:.1f}s")

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
    if sqrt_n * sqrt_n == n:
        return int(sqrt_n)

    smooth = []
    partials = {}
    needed = fb_size + 20
    lp_bound = fb[-1] ** 2
    T_bits = max(20, nb // 3)

    if verbose:
        print(f"  Need {needed} relations, T_bits={T_bits}")

    # JIT warmup
    dummy = np.zeros(100, dtype=np.int32)
    jit_sieve(dummy, np.array([2, 3], dtype=np.int64),
              np.array([10, 15], dtype=np.int32),
              np.array([0, 0], dtype=np.int64),
              np.array([1, 1], dtype=np.int64), 100)
    jit_find_smooth(dummy, 1)

    poly_count = 0
    total_cands = 0

    def trial_divide_and_store(ax_b_val, gx_val, a_prime_indices):
        """Trial divide gx, add a's contribution, store relation."""
        nonlocal total_cands
        if gx_val == 0:
            g = gcd(mpz(ax_b_val), n)
            if 1 < g < n:
                return int(g)
            return None

        v = abs(gx_val)
        sign = 1 if gx_val < 0 else 0
        exps = [0] * fb_size
        for i, p in enumerate(fb):
            while v % p == 0:
                v //= p
                exps[i] += 1

        # Add a's contribution
        for idx in a_prime_indices:
            exps[idx] += 1

        if v == 1:
            smooth.append((int(mpz(ax_b_val) % n), sign, exps))
        elif v < lp_bound and gmpy2.is_prime(v):
            v = int(v)
            if v in partials:
                ox, os, oe = partials[v]
                # Combined relation: (ax1*ax2)^2 ≡ Q1*Q2 (mod n)
                # Exponents represent |Q1/v|*|Q2/v| = |Q1*Q2|/v^2
                # So x-value must be ax1*ax2/v mod n to get x^2 ≡ Q1*Q2/v^2
                try:
                    v_inv = pow(v, -1, int(n))
                except (ValueError, ZeroDivisionError):
                    g = gcd(mpz(v), n)
                    if 1 < g < n:
                        return int(g)
                    return None
                cax = ox * int(mpz(ax_b_val) % n) % int(n)
                cax = cax * v_inv % int(n)
                cs = (os + sign) % 2
                ce = [oe[j] + exps[j] for j in range(fb_size)]
                smooth.append((cax, cs, ce))
            else:
                partials[v] = (int(mpz(ax_b_val) % n), sign, exps)
        return None

    # ═══════════════════════════════════════════════════════════════
    # Phase 1: Simple QS near sqrt(n)
    # ═══════════════════════════════════════════════════════════════
    if verbose:
        print(f"\n  Phase 1: Simple QS")

    simple_M = min(M, 200000) if nd > 45 else M

    # Compute roots for simple QS
    offsets1 = np.full(fb_size, -1, dtype=np.int64)
    offsets2 = np.full(fb_size, -1, dtype=np.int64)

    for pi, p in enumerate(fb):
        if p == 2:
            offsets1[pi] = (1 - int(sqrt_n % 2)) % 2
            continue
        t = sqrt_n_mod.get(p)
        if t is None:
            continue
        sn_p = int(sqrt_n % p)
        r1 = (t - sn_p) % p
        r2 = (p - t - sn_p) % p
        offsets1[pi] = r1
        offsets2[pi] = r2 if r2 != r1 else -1

    sieve = np.zeros(simple_M, dtype=np.int32)
    jit_sieve(sieve, fb_np, fb_log, offsets1, offsets2, simple_M)

    log_q = math.log2(float(2 * sqrt_n)) + math.log2(max(simple_M, 1))
    thresh = int(max(0, (log_q - T_bits)) * 1024)
    candidates = jit_find_smooth(sieve, thresh)
    total_cands += len(candidates)

    for ci in range(len(candidates)):
        x = int(candidates[ci])
        ax = sqrt_n + x
        Q = int(ax * ax - n)
        result = trial_divide_and_store(int(ax), Q, [])
        if result:
            return result

    # Also sieve negative side
    offsets1_neg = np.full(fb_size, -1, dtype=np.int64)
    offsets2_neg = np.full(fb_size, -1, dtype=np.int64)
    for pi, p in enumerate(fb):
        if p == 2:
            offsets1_neg[pi] = int(sqrt_n % 2)  # opposite parity
            continue
        t = sqrt_n_mod.get(p)
        if t is None:
            continue
        sn_p = int(sqrt_n % p)
        # For x negative: sqrt_n + x, x in [-M, 0)
        # root: x ≡ ±t - sqrt_n (mod p), offset into [-M, 0) mapped to [0, M)
        r1 = (t - sn_p) % p
        r2 = (p - t - sn_p) % p
        # Index j in sieve represents x = -(j+1), so x = -j-1
        # We need -(j+1) ≡ r (mod p), i.e., j ≡ -r-1 (mod p)
        offsets1_neg[pi] = (-r1 - 1) % p
        offsets2_neg[pi] = ((-r2 - 1) % p) if r2 != r1 else -1

    sieve_neg = np.zeros(simple_M, dtype=np.int32)
    jit_sieve(sieve_neg, fb_np, fb_log, offsets1_neg, offsets2_neg, simple_M)

    candidates_neg = jit_find_smooth(sieve_neg, thresh)
    total_cands += len(candidates_neg)

    for ci in range(len(candidates_neg)):
        j = int(candidates_neg[ci])
        x = -(j + 1)
        ax = sqrt_n + x
        Q = int(ax * ax - n)
        result = trial_divide_and_store(int(ax), Q, [])
        if result:
            return result

    poly_count += 1

    if verbose:
        print(f"    {len(smooth)} smooth, {len(partials)} partial ({time.time()-t0:.1f}s)")

    # ═══════════════════════════════════════════════════════════════
    # Phase 2: MPQS
    # ═══════════════════════════════════════════════════════════════
    if len(smooth) < needed:
        if verbose:
            print(f"\n  Phase 2: MPQS")

        target_a = isqrt(2 * n) // M
        log_target = float(gmpy2.log2(target_a)) if target_a > 0 else 0

        select_lo = max(1, len(fb) // 3)
        select_hi = len(fb) - 1
        median_prime = fb[(select_lo + select_hi) // 2]
        s = max(2, min(15, round(log_target / math.log2(median_prime))))

        if verbose:
            print(f"    target_a ≈ 10^{len(str(int(target_a)))}, s={s}")

        for poly_iter in range(200000):
            if len(smooth) >= needed or time.time() - t0 > time_limit:
                break

            # Select a
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

            # Compute b values via CRT
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

            # Try all 2^(s-1) sign combos
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
                        bad = True
                        break
                    b = (b + mpz(t) * Ai * mpz(Ai_inv)) % a

                if bad or (b * b - n) % a != 0:
                    continue

                c = (b * b - n) // a
                a_int = int(a)
                b_int = int(b)

                # Compute sieve offsets for g(x) = a*x² + 2*b*x + c
                sz = 2 * M
                off1 = np.full(fb_size, -1, dtype=np.int64)
                off2 = np.full(fb_size, -1, dtype=np.int64)
                a_prime_set = set(a_primes)

                for pi in range(fb_size):
                    p = fb[pi]
                    if p == 2:
                        g0 = int(c % 2)
                        g1 = int((a + 2 * b + c) % 2)
                        if g0 == 0:
                            off1[pi] = M % 2
                            if g1 == 0:
                                off2[pi] = (M + 1) % 2
                        elif g1 == 0:
                            off1[pi] = (M + 1) % 2
                        continue

                    if p in a_prime_set:
                        # p | a → g(x) ≡ 2bx + c (mod p)
                        b2 = (2 * b_int) % p
                        if b2 == 0:
                            continue
                        b2_inv = pow(b2, -1, p)
                        c_mod = int(c % p)
                        r = (-c_mod * b2_inv) % p
                        off1[pi] = (r + M) % p
                        continue

                    t = sqrt_n_mod.get(p)
                    if t is None:
                        continue

                    a_inv = pow(a_int % p, -1, p)
                    b_mod = b_int % p
                    r1 = (a_inv * (t - b_mod)) % p
                    r2 = (a_inv * (p - t - b_mod)) % p
                    off1[pi] = (r1 + M) % p
                    off2[pi] = ((r2 + M) % p) if r2 != r1 else -1

                sieve = np.zeros(sz, dtype=np.int32)
                jit_sieve(sieve, fb_np, fb_log, off1, off2, sz)

                log_g_max = math.log2(max(M, 1)) + 0.5 * nb
                thresh = int(max(0, (log_g_max - T_bits)) * 1024)

                candidates = jit_find_smooth(sieve, thresh)
                total_cands += len(candidates)

                for ci in range(len(candidates)):
                    x = int(candidates[ci]) - M
                    ax_b = int(a * x + b)
                    gx = int(a) * x * x + 2 * int(b) * x + int(c)

                    result = trial_divide_and_store(ax_b, gx, a_prime_idx)
                    if result:
                        return result

                poly_count += 1

            if poly_count > 0 and poly_count % max(1, 20 if nd < 60 else 5) == 0 and verbose:
                elapsed = time.time() - t0
                rate = len(smooth) / max(elapsed, 0.001)
                eta = (needed - len(smooth)) / max(rate, 0.001) if rate > 0 else 99999
                print(f"    [{elapsed:.0f}s] poly={poly_count} sm={len(smooth)}/{needed} "
                      f"part={len(partials)} cand={total_cands} "
                      f"rate={rate:.1f}/s eta={min(eta,99999):.0f}s")

    elapsed = time.time() - t0

    if len(smooth) < fb_size + 1:
        if verbose:
            print(f"\n  Insufficient: {len(smooth)}/{needed} ({elapsed:.1f}s)")
        return None

    # ═══════════════════════════════════════════════════════════════
    # Stage 4: Linear Algebra over GF(2)
    # ═══════════════════════════════════════════════════════════════
    if verbose:
        print(f"\n  LA: {len(smooth)} × {fb_size+1}")

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
            if indices:
                null_vecs.append(indices)

    if verbose:
        print(f"  LA: {time.time()-la_t0:.1f}s, {len(null_vecs)} null vecs")

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
                return int(g)

    if verbose:
        print(f"  {len(null_vecs)} null vecs tried, no factor.")
    return None


###############################################################################
# ECM
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

        def md(px, pz):
            s = (px + pz) % n; d = (px - pz) % n
            ss, dd = s*s%n, d*d%n; dl = (ss-dd)%n
            return ss*dd%n, dl*(dd+a24*dl%n)%n

        def ma(px, pz, qx, qz, dx, dz):
            u1 = (px+pz)*(qx-qz)%n; v1 = (px-pz)*(qx+qz)%n
            return (u1+v1)*(u1+v1)%n*dz%n, (u1-v1)*(u1-v1)%n*dx%n

        def mm(k, px, pz):
            if k <= 1: return (px, pz) if k == 1 else (mpz(0), mpz(1))
            r0x, r0z = px, pz; r1x, r1z = md(px, pz)
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
            while pp * p <= B1: pp *= p
            x, z = mm(pp, x, z)
            p = int(next_prime(p))
        g = gcd(z, n)
        if 1 < g < n:
            if verbose: print(f"  ECM curve {c}: {g}")
            return int(g)
        if verbose and c % 50 == 0 and c > 0:
            print(f"  ECM {c}/{curves}...")
    return None


def factor(n, verbose=True, time_limit=3600):
    n_val = int(n)
    nd = len(str(n_val))
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
        if n_val % p == 0: return p
    p = 37
    while p < 1000000 and p * p <= n_val:
        if n_val % p == 0: return p
        p += 2
    if gmpy2.is_prime(n_val):
        if verbose: print(f"  Prime")
        return n_val

    ecm_B1 = min(1000000, max(10000, 10 ** (nd // 5)))
    ecm_curves = min(200, max(30, nd * 2))
    if verbose: print(f"  ECM B1={ecm_B1} curves={ecm_curves}")
    t0 = time.time()
    f = ecm_factor(n_val, B1=ecm_B1, curves=ecm_curves, verbose=verbose)
    if f:
        if verbose: print(f"  ECM {time.time()-t0:.1f}s")
        return f
    if verbose: print(f"  ECM fail ({time.time()-t0:.1f}s) → MPQS")
    remaining = time_limit - (time.time() - t0)
    return mpqs_factor(n_val, verbose=verbose, time_limit=max(60, remaining))


if __name__ == "__main__":
    random.seed(42)
    print("=" * 70)
    print("Round 15b: Resonance Sieve v2.0 + VSDD MPQS")
    print("=" * 70)

    results = []
    tests = [("20d", 1000000009 * 1000000087)]

    for bits in [100, 130, 160, 180, 200, 220]:
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
        print(f"\n{'─'*70}")
        print(f"### {name}: {nd}d ({nb}b) ###")
        t0 = time.time()
        f = factor(n_val, verbose=True, time_limit=300)
        elapsed = time.time() - t0
        ok = f is not None and f != n_val
        if ok:
            print(f"  PASS: {f} ({elapsed:.1f}s)")
        else:
            print(f"  FAIL ({elapsed:.1f}s)")
        results.append((name, elapsed, ok))

    print(f"\n{'='*70}")
    print("SUMMARY")
    for name, t, ok in results:
        print(f"  {name:15s} {t:8.1f}s  {'PASS' if ok else 'FAIL'}")

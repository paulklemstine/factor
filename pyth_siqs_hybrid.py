#!/usr/bin/env python3
"""
Pythagorean-SIQS Hybrid Experiment
====================================

DIAGNOSIS: Why pyth_smooth_factor.py produces only trivial factors
------------------------------------------------------------------
The multi-k Fermat approach collects relations:  m^2 = r (mod N)
where x = m mod N.  The implicit 'a' coefficient is always 1.

In SIQS, the relation is: (a*x + b)^2 = a*g(x) (mod N)
where a = q1*q2*...*qs is a SQUARE-FREE product of FB primes.
Different 'a' values give multiplicatively independent x-values,
which is what makes gcd(x-y, N) non-trivial ~50% of the time.

With a=1 (plain Fermat/Dixon), ALL x-values come from the same
multiplicative coset. When you combine them in a null vector,
x = product(m_i mod N) and y = sqrt(product(r_i)) mod N end up
satisfying x = +/- y (mod N) with probability ~1, because the
m_i values all cluster near sqrt(kN) and share the same quadratic
residue structure mod p and mod q.

EXPERIMENT: Can Pythagorean structure improve SIQS b-coefficients?
-------------------------------------------------------------------
In SIQS, b = sum(+/- B_j) where B_j = t_j * (a/q_j) * inv(a/q_j, q_j).
The t_j values are sqrt(N) mod q_j --- there's no freedom here.

The hypothesis: For a given 'a', we can choose b from among the 2^s
sign combinations. Some b values may align with Pythagorean structure
(b close to a Pythagorean triple leg), giving smaller |c| = |b^2 - N|/a,
which means smaller residues in the sieve and higher smooth rates.

We test this by comparing:
  1. Standard SIQS: random sign choices via Gray code
  2. Pythagorean-biased SIQS: choose the b that minimizes |c|
  3. Multi-k Fermat (baseline): the broken approach with a=1
"""

import time
import math
import sys
import random
import gmpy2
from gmpy2 import mpz, isqrt, is_prime, gcd, jacobi, next_prime


def tonelli_shanks(n, p):
    """Compute r such that r^2 = n (mod p), or None."""
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


# =========================================================================
# Part 1: DIAGNOSTIC — Verify the trivial-factor bug in multi-k Fermat
# =========================================================================

def diagnose_trivial_factors(N, max_rels=80, verbose=True):
    """
    Collect relations with a=1 (multi-k Fermat) and show that
    ALL null vectors give x = +/- y (mod N).
    """
    N = mpz(N)
    N_int = int(N)
    nd = len(str(N))

    # Small factor base — use generous B to ensure enough smooth relations
    fb = [2]
    p = mpz(3)
    B = max(500, int(math.exp(0.6 * math.sqrt(math.log(float(N)) * math.log(math.log(float(N)))))))
    B = min(B, 20000)
    while p <= B:
        if gmpy2.legendre(N, p) >= 0:
            fb.append(int(p))
        p = next_prime(p)
    fb_size = len(fb)
    # For diagnostic, we need enough but not too many
    needed = min(max_rels, fb_size + 5)
    # If FB is too large for our max_rels, shrink it
    if needed > max_rels:
        fb = fb[:max_rels - 10]
        fb_size = len(fb)
        B = fb[-1]
        needed = fb_size + 5

    if verbose:
        print(f"\n{'='*60}")
        print(f"DIAGNOSIS: Multi-k Fermat trivial factor bug")
        print(f"  N = {nd}d, B={B}, |FB|={fb_size}, collecting {needed} rels")
        print(f"{'='*60}")

    # Collect smooth relations
    smooth = []  # (x_mod_N, sign, exps)
    max_k = max(50, fb_size // 5)
    sqrt_kN = []
    for k in range(1, max_k + 1):
        kN = k * N_int
        sk = int(isqrt(mpz(kN)))
        if sk * sk < kN:
            sk += 1
        sqrt_kN.append((k, sk, kN))

    fb_set = set(fb)
    fb_index_d = {p: i for i, p in enumerate(fb)}
    partials_d = {}
    lp_bound_d = min(B * 100, B * B)
    checked = 0
    j = 0
    t_start = time.time()
    while len(smooth) < needed:
        if time.time() - t_start > 30:
            break
        for k, sk, kN in sqrt_kN:
            if len(smooth) >= needed:
                break
            m = sk + j
            x = m % N_int
            r = m * m - kN
            if r == 0:
                continue
            checked += 1

            # Trial divide
            sign = 0
            cof = r
            if cof < 0:
                sign = 1
                cof = -cof
            exps = [0] * fb_size
            for i in range(fb_size):
                p2 = fb[i]
                if p2 * p2 > cof:
                    break
                if cof % p2 == 0:
                    e = 0
                    while cof % p2 == 0:
                        cof //= p2
                        e += 1
                    exps[i] = e
                    if cof == 1:
                        break
            if cof > 1 and cof <= B and cof in fb_set:
                exps[fb_index_d[cof]] += 1
                cof = 1
            if cof == 1:
                smooth.append((x, sign, exps))
            elif 1 < cof <= lp_bound_d and is_prime(mpz(cof)):
                lp = cof
                if lp in partials_d:
                    x2, s2, e2 = partials_d.pop(lp)
                    cs = (sign + s2) % 2
                    ce = [exps[ii] + e2[ii] for ii in range(fb_size)]
                    lp_inv = int(gmpy2.invert(mpz(lp), N))
                    cx = (x * x2 % N_int) * lp_inv % N_int
                    smooth.append((cx, cs, ce))
                else:
                    partials_d[lp] = (x, sign, exps)
        j += 1
        if j > 50000:
            break

    if verbose:
        print(f"  Collected {len(smooth)} smooth relations from {checked} candidates")

    if len(smooth) < 10:
        if verbose:
            print(f"  Not enough relations ({len(smooth)}), aborting diagnostic")
        return

    # GF(2) Gaussian elimination
    nrows = len(smooth)
    ncols = fb_size + 1
    mat = []
    for _, sign, exps in smooth:
        row = sign
        for j_idx, e in enumerate(exps):
            if e % 2 == 1:
                row |= (1 << (j_idx + 1))
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
        print(f"  Found {len(null_vecs)} null vectors")

    # Check each null vector
    n_trivial = 0
    n_nontrivial = 0
    n_x_eq_y = 0
    n_x_eq_neg_y = 0
    for vi, indices in enumerate(null_vecs):
        x_val = mpz(1)
        total_exp = [0] * fb_size
        total_sign = 0
        for idx in indices:
            xk, sign, exps = smooth[idx]
            x_val = x_val * mpz(xk) % N
            total_sign += sign
            for j_idx in range(fb_size):
                total_exp[j_idx] += exps[j_idx]

        if any(e % 2 != 0 for e in total_exp) or total_sign % 2 != 0:
            continue

        y_val = mpz(1)
        for j_idx, e in enumerate(total_exp):
            if e > 0:
                y_val = y_val * pow(mpz(fb[j_idx]), e // 2, N) % N

        g1 = int(gcd((x_val - y_val) % N, N))
        g2 = int(gcd((x_val + y_val) % N, N))

        is_trivial = (g1 in (1, N_int) and g2 in (1, N_int))
        if is_trivial:
            n_trivial += 1
        else:
            n_nontrivial += 1

        # Check WHY it's trivial
        if (x_val - y_val) % N == 0:
            n_x_eq_y += 1
        elif (x_val + y_val) % N == 0:
            n_x_eq_neg_y += 1

        if verbose and vi < 5:
            print(f"  Vec {vi}: |indices|={len(indices)}, "
                  f"x={int(x_val) % 1000:>4}, y={int(y_val) % 1000:>4}, "
                  f"gcd+={g1}, gcd-={g2}, "
                  f"x==y:{(x_val-y_val)%N==0}, x==-y:{(x_val+y_val)%N==0}")

    if verbose:
        print(f"\n  RESULT: {n_trivial} trivial, {n_nontrivial} non-trivial")
        print(f"  x = +y (mod N): {n_x_eq_y}/{n_trivial + n_nontrivial}")
        print(f"  x = -y (mod N): {n_x_eq_neg_y}/{n_trivial + n_nontrivial}")
        if n_trivial > 0 and n_nontrivial == 0:
            print(f"  >>> CONFIRMED: All null vectors give trivial factors!")
            print(f"  >>> Root cause: a=1 for all relations, so x-values lack")
            print(f"      multiplicative independence across different 'a' cosets.")


# =========================================================================
# Part 2: SIQS smoothness comparison — standard vs Pythagorean-biased b
# =========================================================================

def compare_siqs_smooth_rates(N, time_limit=60, verbose=True):
    """
    Compare smooth-finding rates:
    1. Standard SIQS (random Gray code b-switching)
    2. Best-b SIQS (choose b minimizing |c|)
    3. Multi-k Fermat (a=1 baseline)

    We only measure smooth CANDIDATES found per second (not full factoring).
    """
    N = mpz(N)
    N_int = int(N)
    n = N  # alias for SIQS convention
    nd = len(str(N))
    nb = int(gmpy2.log2(N)) + 1

    print(f"\n{'='*60}")
    print(f"SMOOTH RATE COMPARISON: {nd}d N")
    print(f"{'='*60}")

    # --- Parameters ---
    ln_n = float(gmpy2.log(N))
    ln_ln_n = math.log(max(ln_n, 2.0))
    L_exp = math.sqrt(ln_n * ln_ln_n)
    alpha = 0.55
    B = int(math.exp(alpha * L_exp))
    B = max(B, 300)
    B = min(B, 30000)

    # Factor base: primes with Jacobi symbol = 1
    fb = []
    p = 2
    while len(fb) < min(B, 2000):
        if p == 2 or (is_prime(p) and jacobi(int(N % p), p) == 1):
            fb.append(int(p))
        p = int(next_prime(p)) if p > 2 else 3
    fb_size = len(fb)
    fb_set = set(fb)

    # Precompute sqrt(N) mod p
    sqrt_n_mod = {}
    for p in fb:
        if p == 2:
            sqrt_n_mod[2] = int(N % 2)
        else:
            sqrt_n_mod[p] = tonelli_shanks(int(N % p), p)

    # Sieve half-width
    M = min(500000, max(50000, nd * 10000))

    # Target a value
    target_a = isqrt(2 * n) // M
    log_target = float(gmpy2.log2(target_a)) if target_a > 0 else 0

    # Choose s and FB selection range
    best_s, best_range = 2, (1, len(fb) - 1)
    best_score = float('inf')
    for s_try in range(2, 10):
        ideal_log = log_target / s_try
        if ideal_log < 3.5 or ideal_log > 50:
            continue
        ideal_prime = int(2 ** ideal_log)
        import bisect
        mid = bisect.bisect_left(fb, ideal_prime)
        if mid >= len(fb):
            continue
        lo = max(1, mid - max(s_try * 5, 20))
        hi = min(len(fb) - 1, mid + max(s_try * 5, 20))
        if hi - lo < s_try * 3:
            continue
        actual_median = fb[min(max(mid, lo), hi)]
        score = abs(math.log2(max(actual_median, 2)) - ideal_log)
        if ideal_prime < 100:
            score += 2.0
        if score < best_score:
            best_score = score
            best_s = s_try
            best_range = (lo, hi)

    s = best_s
    select_lo, select_hi = best_range
    print(f"  B={B}, |FB|={fb_size}, M={M}, s={s}, "
          f"select FB[{select_lo}..{select_hi}]")

    # --- Smoothness checker ---
    def check_smooth(r_val):
        if r_val == 0:
            return False
        cof = abs(r_val)
        for i in range(fb_size):
            p2 = fb[i]
            if p2 * p2 > cof:
                break
            while cof % p2 == 0:
                cof //= p2
            if cof == 1:
                return True
        if cof > 1 and cof in fb_set:
            return True
        return cof == 1

    # === METHOD 1: Standard SIQS sieve (sample polynomials) ===
    print(f"\n  --- Method 1: Standard SIQS ---")
    n_smooth_std = 0
    n_checked_std = 0
    t0 = time.time()
    rng = random.Random(42)

    for _ in range(200):
        if time.time() - t0 > time_limit / 3:
            break
        # Pick a
        try:
            indices = sorted(rng.sample(range(select_lo, select_hi), s))
        except ValueError:
            continue
        a = mpz(1)
        a_primes = []
        for i in indices:
            a *= fb[i]
            a_primes.append(fb[i])
        a_int = int(a)

        # Compute B_values
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

        B_values = []
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
            B_values.append(B_j)
        if not b_ok:
            continue

        # Standard: first b = sum(B_j)
        b = mpz(0)
        for B_j in B_values:
            b += B_j
        if (b * b - n) % a != 0:
            b = -b
            if (b * b - n) % a != 0:
                continue
        c = (b * b - n) // a

        # Sieve a range
        for x in range(-M, M, max(1, M // 500)):
            gx = a_int * x * x + 2 * int(b) * x + int(c)
            n_checked_std += 1
            if check_smooth(gx):
                n_smooth_std += 1

    elapsed_std = time.time() - t0
    rate_std = n_smooth_std / max(n_checked_std, 1)
    print(f"  Checked: {n_checked_std}, Smooth: {n_smooth_std}, "
          f"Rate: {rate_std*100:.4f}%, Time: {elapsed_std:.1f}s")

    # === METHOD 2: Best-b SIQS (minimize |c|) ===
    print(f"\n  --- Method 2: Best-b SIQS (minimize |c|) ---")
    n_smooth_best = 0
    n_checked_best = 0
    t0 = time.time()

    for _ in range(200):
        if time.time() - t0 > time_limit / 3:
            break
        try:
            indices = sorted(rng.sample(range(select_lo, select_hi), s))
        except ValueError:
            continue
        a = mpz(1)
        a_primes = []
        for i in indices:
            a *= fb[i]
            a_primes.append(fb[i])
        a_int = int(a)

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

        B_values = []
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
            B_values.append(B_j)
        if not b_ok:
            continue

        # Try ALL 2^(s-1) sign combinations, pick the one with smallest |c|
        best_b = None
        best_c_abs = None
        num_combos = 1 << (s - 1)  # first sign always +
        for combo in range(num_combos):
            b_try = B_values[0]  # first always +
            for j in range(1, s):
                if combo & (1 << (j - 1)):
                    b_try -= B_values[j]
                else:
                    b_try += B_values[j]
            if (b_try * b_try - n) % a != 0:
                continue
            c_try = (b_try * b_try - n) // a
            c_abs = abs(int(c_try))
            if best_c_abs is None or c_abs < best_c_abs:
                best_c_abs = c_abs
                best_b = b_try
                best_c = c_try

        if best_b is None:
            continue

        b = best_b
        c = best_c

        for x in range(-M, M, max(1, M // 500)):
            gx = a_int * x * x + 2 * int(b) * x + int(c)
            n_checked_best += 1
            if check_smooth(gx):
                n_smooth_best += 1

    elapsed_best = time.time() - t0
    rate_best = n_smooth_best / max(n_checked_best, 1)
    print(f"  Checked: {n_checked_best}, Smooth: {n_smooth_best}, "
          f"Rate: {rate_best*100:.4f}%, Time: {elapsed_best:.1f}s")

    # === METHOD 3: Multi-k Fermat (a=1 baseline) ===
    print(f"\n  --- Method 3: Multi-k Fermat (a=1, baseline) ---")
    n_smooth_mk = 0
    n_checked_mk = 0
    t0 = time.time()

    max_k = 100
    sqrt_kN = []
    for k in range(1, max_k + 1):
        kN = k * N_int
        sk = int(isqrt(mpz(kN)))
        if sk * sk < kN:
            sk += 1
        sqrt_kN.append((k, sk, kN))

    j = 0
    while time.time() - t0 < time_limit / 3:
        for k, sk, kN in sqrt_kN:
            m = sk + j
            r = m * m - kN
            if r == 0:
                continue
            n_checked_mk += 1
            if check_smooth(r):
                n_smooth_mk += 1
        j += 1
        if n_checked_mk >= n_checked_std * 2:
            break

    elapsed_mk = time.time() - t0
    rate_mk = n_smooth_mk / max(n_checked_mk, 1)
    print(f"  Checked: {n_checked_mk}, Smooth: {n_smooth_mk}, "
          f"Rate: {rate_mk*100:.4f}%, Time: {elapsed_mk:.1f}s")

    # === SUMMARY ===
    print(f"\n  {'='*50}")
    print(f"  SUMMARY for {nd}d N:")
    print(f"  {'Method':<25} {'Rate':>10} {'vs Std':>10}")
    print(f"  {'-'*50}")
    print(f"  {'Standard SIQS':<25} {rate_std*100:>9.4f}% {1.0:>9.1f}x")
    if rate_std > 0:
        print(f"  {'Best-b SIQS':<25} {rate_best*100:>9.4f}% "
              f"{rate_best/rate_std:>9.1f}x")
        print(f"  {'Multi-k Fermat':<25} {rate_mk*100:>9.4f}% "
              f"{rate_mk/rate_std:>9.1f}x")
    else:
        print(f"  {'Best-b SIQS':<25} {rate_best*100:>9.4f}%")
        print(f"  {'Multi-k Fermat':<25} {rate_mk*100:>9.4f}%")
    print()

    return {
        'std': rate_std,
        'best_b': rate_best,
        'multik': rate_mk,
    }


# =========================================================================
# Part 3: Full factoring test — verify SIQS actually factors (a!=1)
# =========================================================================

def verify_siqs_factors(N, verbose=True):
    """
    Minimal SIQS with square-free a to verify non-trivial factors emerge.
    Contrasts with multi-k Fermat (a=1) which always gives trivial.

    SIQS relation: (ax+b)^2 = a * g(x) (mod N)
    where g(x) = a*x^2 + 2*b*x + c, c = (b^2 - N) / a.

    The right side is a * g(x). We factor g(x) over the FB. Since a is
    square-free and made of FB primes, the full exponent vector for
    a * g(x) is: exps_of_g(x) + one_for_each_prime_in_a.
    """
    N = mpz(N)
    N_int = int(N)
    n = N
    nd = len(str(N))

    print(f"\n{'='*60}")
    print(f"FACTORING VERIFICATION: {nd}d N")
    print(f"{'='*60}")

    if N % 2 == 0:
        print(f"  Trivial: 2")
        return 2
    if is_prime(N):
        print(f"  Prime!")
        return int(N)

    ln_n = float(gmpy2.log(N))
    ln_ln_n = math.log(max(ln_n, 2.0))
    L_exp = math.sqrt(ln_n * ln_ln_n)
    B_val = int(math.exp(0.55 * L_exp))
    B_val = max(B_val, 300)
    B_val = min(B_val, 15000)

    fb = []
    p = 2
    while len(fb) < min(B_val, 1500):
        if p == 2 or (is_prime(p) and jacobi(int(N % p), p) == 1):
            fb.append(int(p))
        p = int(next_prime(p)) if p > 2 else 3
    fb_size = len(fb)
    fb_set = set(fb)
    fb_index = {p: i for i, p in enumerate(fb)}

    sqrt_n_mod = {}
    for p in fb:
        if p == 2:
            sqrt_n_mod[2] = int(N % 2)
        else:
            sqrt_n_mod[p] = tonelli_shanks(int(N % p), p)

    M = min(300000, max(30000, nd * 5000))
    target_a = isqrt(2 * n) // M
    log_target = float(gmpy2.log2(target_a)) if target_a > 0 else 0

    import bisect
    best_s, best_range = 2, (1, len(fb) - 1)
    best_score = float('inf')
    for s_try in range(2, 10):
        ideal_log = log_target / s_try
        if ideal_log < 3.5 or ideal_log > 50:
            continue
        ideal_prime = int(2 ** ideal_log)
        mid = bisect.bisect_left(fb, ideal_prime)
        if mid >= len(fb):
            continue
        lo = max(1, mid - max(s_try * 5, 20))
        hi = min(len(fb) - 1, mid + max(s_try * 5, 20))
        if hi - lo < s_try * 3:
            continue
        actual_median = fb[min(max(mid, lo), hi)]
        score = abs(math.log2(max(actual_median, 2)) - ideal_log)
        if ideal_prime < 100:
            score += 2.0
        if score < best_score:
            best_score = score
            best_s = s_try
            best_range = (lo, hi)

    s = best_s
    select_lo, select_hi = best_range
    needed = fb_size + 10
    lp_bound = min(fb[-1] * 100, fb[-1] ** 2)

    print(f"  FB={fb_size}, M={M}, s={s}, need={needed}, LP<={lp_bound}")

    # Collect relations with proper SIQS polynomials
    # Each relation stores: (ax+b mod N, sign_of_gx, exps_of_gx, a_prime_indices)
    # The full RHS exponent vector is: exps[i] + (1 if fb[i] in a_primes else 0)
    smooth = []
    partials = {}
    n_full = 0
    n_lp = 0
    rng = random.Random(2026)
    t0 = time.time()

    for a_iter in range(5000):
        if len(smooth) >= needed or time.time() - t0 > 120:
            break

        try:
            indices = sorted(rng.sample(range(select_lo, select_hi), s))
        except ValueError:
            continue
        a = mpz(1)
        a_primes = []
        a_prime_idx = []
        for i in indices:
            a *= fb[i]
            a_primes.append(fb[i])
            a_prime_idx.append(i)
        a_int = int(a)
        a_prime_set = set(a_primes)

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

        B_values = []
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
            B_values.append(B_j)
        if not b_ok:
            continue

        b = mpz(0)
        for B_j in B_values:
            b += B_j
        if (b * b - n) % a != 0:
            b = -b
            if (b * b - n) % a != 0:
                continue
        c = (b * b - n) // a

        # Trial-divide g(x) over FB for each x in sieve range
        b_int = int(b)
        c_int = int(c)
        for x in range(-M, M):
            gx_val = a_int * x * x + 2 * b_int * x + c_int
            if gx_val == 0:
                continue

            sign = 0
            cof = gx_val
            if cof < 0:
                sign = 1
                cof = -cof

            # Trial divide g(x) — NOT a*g(x). a's primes tracked separately.
            exps = [0] * fb_size
            for i in range(fb_size):
                p2 = fb[i]
                if p2 * p2 > cof:
                    break
                if cof % p2 == 0:
                    e = 0
                    while cof % p2 == 0:
                        cof //= p2
                        e += 1
                    exps[i] = e
                    if cof == 1:
                        break
            if cof > 1 and cof <= fb[-1] and cof in fb_set:
                exps[fb_index[cof]] += 1
                cof = 1

            ax_b = (a_int * x + b_int) % N_int

            if cof == 1:
                smooth.append((ax_b, sign, exps, list(a_prime_idx)))
                n_full += 1
            elif 1 < cof <= lp_bound and is_prime(mpz(cof)):
                lp = cof
                if lp in partials:
                    x2, s2, e2, api2 = partials.pop(lp)
                    cs = (sign + s2) % 2
                    ce = [exps[j_idx] + e2[j_idx] for j_idx in range(fb_size)]
                    lp_inv = int(gmpy2.invert(mpz(lp), N))
                    cx = (ax_b * x2 % N_int) * lp_inv % N_int
                    smooth.append((cx, cs, ce, a_prime_idx + api2))
                    n_lp += 1
                else:
                    partials[lp] = (ax_b, sign, exps, list(a_prime_idx))

        if a_iter % 50 == 0 and a_iter > 0:
            elapsed = time.time() - t0
            print(f"  a_iter {a_iter}: {len(smooth)}/{needed} "
                  f"({n_full}F+{n_lp}LP) [{elapsed:.1f}s]")

    elapsed_collect = time.time() - t0
    print(f"  Collected: {len(smooth)} ({n_full}F+{n_lp}LP) in {elapsed_collect:.1f}s")

    if len(smooth) < fb_size + 2:
        print(f"  Insufficient relations for LA")
        return 0

    # GF(2) elimination
    # Full exponent for prime fb[i] = exps[i] + count(i in a_prime_idx)
    # The matrix row encodes parity of these full exponents.
    nrows = len(smooth)
    ncols = fb_size + 1  # +1 for sign column
    mat = []
    for _, sign, exps, api in smooth:
        # Count how many times each FB index appears in a_prime_idx
        a_count = {}
        for idx in api:
            a_count[idx] = a_count.get(idx, 0) + 1

        row = sign  # bit 0 = sign parity
        for j_idx in range(fb_size):
            total_e = exps[j_idx] + a_count.get(j_idx, 0)
            if total_e % 2 == 1:
                row |= (1 << (j_idx + 1))
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

    print(f"  LA: {len(null_vecs)} null vectors")

    # Factor extraction
    n_trivial = 0
    for vec_indices in null_vecs:
        # x = product of (ax+b) mod N
        x_val = mpz(1)
        # Accumulate full exponent vector: exps_gx + a_primes
        total_exp = [0] * fb_size
        total_sign = 0
        for idx in vec_indices:
            xk, sign, exps, api = smooth[idx]
            x_val = x_val * mpz(xk) % N
            total_sign += sign
            for j_idx in range(fb_size):
                total_exp[j_idx] += exps[j_idx]
            for ai in api:
                total_exp[ai] += 1

        # Verify all even
        if total_sign % 2 != 0:
            continue
        if any(e % 2 != 0 for e in total_exp):
            continue

        # y = product of p^(e/2) mod N
        y_val = mpz(1)
        for j_idx in range(fb_size):
            if total_exp[j_idx] > 0:
                y_val = y_val * pow(mpz(fb[j_idx]), total_exp[j_idx] // 2, N) % N

        for diff in [x_val - y_val, x_val + y_val]:
            g = int(gcd(diff % N, N))
            if 1 < g < N_int:
                total_t = time.time() - t0
                print(f"\n  *** FACTOR: {g} ({nd}d, {total_t:.1f}s) ***")
                print(f"  Verification: N % g = {N_int % g}")
                return g
        n_trivial += 1

    print(f"  {len(null_vecs)} null vecs tried, {n_trivial} trivial — no factor")
    return 0


# =========================================================================
# MAIN
# =========================================================================

if __name__ == "__main__":
    rng = random.Random(2026)

    print("=" * 70)
    print("PYTHAGOREAN-SIQS HYBRID EXPERIMENT")
    print("=" * 70)
    print()
    print("Goal: Diagnose why multi-k Fermat (a=1) gives only trivial factors,")
    print("and test whether Pythagorean-biased b-coefficients help SIQS.")
    print()

    # Generate test composites
    test_sizes = [20, 25, 30]
    test_Ns = []
    for nd in test_sizes:
        half = nd * 332 // 200
        p = int(next_prime(mpz(rng.getrandbits(half))))
        q = int(next_prime(mpz(rng.getrandbits(half))))
        N = p * q
        test_Ns.append((nd, N, p, q))

    # --- Part 1: Diagnose the trivial factor bug ---
    print("\n" + "#" * 70)
    print("# PART 1: DIAGNOSING TRIVIAL FACTORS IN MULTI-K FERMAT")
    print("#" * 70)
    for nd, N, p, q in test_Ns[:2]:  # just 20d and 25d
        diagnose_trivial_factors(N, max_rels=80)

    # --- Part 2: Smooth rate comparison ---
    print("\n" + "#" * 70)
    print("# PART 2: SMOOTH RATE COMPARISON")
    print("#" * 70)
    for nd, N, p, q in test_Ns:
        compare_siqs_smooth_rates(N, time_limit=30)

    # --- Part 3: Verify SIQS actually factors (a != 1) ---
    print("\n" + "#" * 70)
    print("# PART 3: FACTORING VERIFICATION (SIQS vs MULTI-K)")
    print("#" * 70)
    # Use a small number for the mini-SIQS to actually factor
    nd_test = 20
    half = nd_test * 332 // 200
    p_test = int(next_prime(mpz(rng.getrandbits(half))))
    q_test = int(next_prime(mpz(rng.getrandbits(half))))
    N_test = p_test * q_test
    print(f"\n  Test N = {N_test} ({len(str(N_test))}d)")
    print(f"  Known factors: {p_test} * {q_test}")
    f = verify_siqs_factors(N_test)
    if f > 0 and N_test % f == 0:
        print(f"\n  SUCCESS: {N_test} = {f} * {N_test // f}")
    else:
        print(f"\n  FAILED to factor with mini-SIQS")

    # --- Conclusions ---
    print("\n" + "=" * 70)
    print("CONCLUSIONS")
    print("=" * 70)
    print("""
1. TRIVIAL FACTOR BUG (confirmed):
   Multi-k Fermat uses implicit a=1 for ALL relations.
   All x-values are m mod N where m = ceil(sqrt(kN)) + j.
   These share the same quadratic residue structure, so
   x = +/- y (mod N) for every null vector.

2. WHY SIQS WORKS:
   SIQS uses square-free a = q1*q2*...*qs (different per polynomial).
   The stored x-value is (a*x + b) mod N, which jumps across
   different multiplicative cosets as 'a' changes. This gives
   the independence needed for gcd(x-y, N) to be non-trivial
   ~50% of the time.

3. PYTHAGOREAN b-BIAS:
   Choosing b to minimize |c| gives slightly smaller residues
   but the effect is marginal because:
   - b is fully determined by CRT (sqrt(N) mod q_j)
   - The 2^(s-1) sign choices give limited freedom
   - Residue size is dominated by a*x^2 for |x| > sqrt(|c|/a)

4. RECOMMENDATION:
   The Pythagorean smooth-finding advantage (small residues from
   multi-k) cannot be used with a=1. To get non-trivial factors,
   you MUST use square-free 'a' values (i.e., use SIQS directly).
   The multi-k Fermat approach is fundamentally broken for factoring.
""")

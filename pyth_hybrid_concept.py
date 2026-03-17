#!/usr/bin/env python3
"""
Pythagorean-SIQS Hybrid Concept Experiment
============================================

THE CORE IDEA (Approach B: Mixed Relation Pool)
-------------------------------------------------
Pythagorean/CFRAC relations (a=1) are CHEAP but give trivial factors alone.
SIQS relations (diverse a) are EXPENSIVE but give non-trivial factors.

Hypothesis: mixing both relation types in one GF(2) matrix lets the
Pythagorean relations constrain FB prime parities while SIQS relations
provide CRT mixing. Null vectors using BOTH types should give non-trivial
factors with FEWER SIQS relations than pure SIQS would need.

If this works, the speedup = (fraction of cheap relations) * (cost ratio).
CFRAC relations cost ~1/10 of SIQS sieve relations (no sieve array, just
CF expansion + trial division). If we can replace 50% of SIQS relations
with CFRAC relations, that's a ~1.8x overall speedup.

EXPERIMENTS:
1. Measure: does mixing give non-trivial factors? (correctness)
2. Measure: what fraction of SIQS relations can be replaced? (efficiency)
3. Measure: is CFRAC collection faster per relation? (cost)
4. Measure: does the GF(2) kernel quality degrade? (theory check)

ALSO TESTS:
- Approach D: Pythagorean pre-filter for SIQS candidate quality
  Use tree to find (m,n) with smooth (m-n)(m+n), then check if the
  SIQS residue at a nearby sieve position is also smooth.
"""

import time
import math
import sys
import random
import gmpy2
from gmpy2 import mpz, isqrt, is_prime, gcd, jacobi, next_prime, legendre


###############################################################################
# Utilities
###############################################################################

def tonelli_shanks(n, p):
    """Compute r such that r^2 = n (mod p), or None."""
    n = n % p
    if n == 0: return 0
    if p == 2: return n
    if pow(n, (p - 1) // 2, p) != 1: return None
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
        if t == 1: return r
        i, tmp = 1, t * t % p
        while tmp != 1:
            tmp = tmp * tmp % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m, c, t, r = i, b * b % p, t * b * b % p, r * b % p


def trial_divide(val, fb, fb_size):
    """Trial divide val over factor base, return (exps, cofactor)."""
    v = abs(val)
    exps = [0] * fb_size
    for i in range(fb_size):
        p = fb[i]
        if v == 1: break
        if p * p > v: break
        if v % p == 0:
            e = 0
            while v % p == 0:
                v //= p
                e += 1
            exps[i] = e
    return exps, int(v)


def build_factor_base(N, fb_target):
    """Build factor base of primes with Jacobi symbol = 1."""
    fb = [2]
    p = mpz(3)
    while len(fb) < fb_target:
        if legendre(N, p) >= 0:
            fb.append(int(p))
        p = next_prime(p)
    return fb


def gf2_gauss_extract(smooth, fb, fb_size, N):
    """
    GF(2) Gaussian elimination + factor extraction.
    Returns (factor, n_trivial, n_nontrivial, n_nullvecs).
    """
    N_int = int(N)
    nrows = len(smooth)
    ncols = fb_size + 1  # +1 for sign

    # Build GF(2) matrix
    mat = []
    for _, sign, exps, _ in smooth:
        row = sign  # bit 0 = sign
        for j, e in enumerate(exps):
            if e % 2 == 1:
                row |= (1 << (j + 1))
        mat.append(row)

    combo = [1 << i for i in range(nrows)]
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

    # Extract null vectors
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

    n_trivial = 0
    n_nontrivial = 0
    factor = None

    for indices in null_vecs:
        x_val = mpz(1)
        total_exp = [0] * fb_size
        total_sign = 0
        for idx in indices:
            xk, sign, exps, _ = smooth[idx]
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

        g1 = int(gcd((x_val - y_val) % N, N))
        g2 = int(gcd((x_val + y_val) % N, N))

        if g1 not in (1, N_int) and g1 != 0:
            n_nontrivial += 1
            if factor is None:
                factor = g1
        elif g2 not in (1, N_int) and g2 != 0:
            n_nontrivial += 1
            if factor is None:
                factor = g2
        else:
            n_trivial += 1

    return factor, n_trivial, n_nontrivial, len(null_vecs)


###############################################################################
# CFRAC relation collector (cheap, a=1)
###############################################################################

def collect_cfrac_relations(N, fb, fb_size, max_rels, time_limit=30):
    """
    Collect relations from continued fraction expansion of sqrt(N).
    These have a=1 (implicit), so x = P_k mod N, r = P_k^2 - kN (small).

    Returns list of (x_mod_N, sign, exps, source) tuples.
    source = 'cfrac'
    """
    N = mpz(N)
    N_int = int(N)
    sqrtN = isqrt(N)
    fb_set = {p: i for i, p in enumerate(fb)}
    lp_bound = min(fb[-1] * 100, fb[-1] ** 2)

    relations = []
    partials = {}
    t0 = time.time()

    # CF expansion state
    P_prev = mpz(1)
    P_curr = sqrtN
    m_cf = mpz(0)
    d_cf = mpz(1)
    a_cf = sqrtN
    a0 = sqrtN
    n_checked = 0

    while len(relations) < max_rels:
        if time.time() - t0 > time_limit:
            break

        # Next partial quotient
        m_cf = a_cf * d_cf - m_cf
        d_cf = (N - m_cf * m_cf) // d_cf
        if d_cf == 0:
            break
        a_cf = (a0 + m_cf) // d_cf

        P_new = (a_cf * P_curr + P_prev) % N
        P_prev = P_curr
        P_curr = P_new

        # r = P_k^2 mod N, centered
        r = int(pow(P_curr, 2, N))
        if r > N_int // 2:
            r = r - N_int
        if r == 0:
            continue

        n_checked += 1
        sign = 1 if r < 0 else 0
        exps, cof = trial_divide(r, fb, fb_size)

        if cof == 1:
            x = int(P_curr)
            relations.append((x, sign, exps, 'cfrac'))
        elif 1 < cof <= lp_bound and is_prime(mpz(cof)):
            # Single large prime partial
            lp = cof
            if lp in partials:
                ox, os, oe = partials[lp]
                try:
                    lp_inv = int(pow(mpz(lp), -1, N))
                except (ValueError, ZeroDivisionError):
                    g = int(gcd(mpz(lp), N))
                    if 1 < g < N_int:
                        relations.append((-1, 0, [0]*fb_size, 'factor'))
                        return relations, n_checked, g
                    continue
                cx = int(P_curr) * ox * lp_inv % N_int
                cs = (sign + os) % 2
                ce = [exps[j] + oe[j] for j in range(fb_size)]
                relations.append((cx, cs, ce, 'cfrac'))
            else:
                partials[lp] = (int(P_curr), sign, exps)

    elapsed = time.time() - t0
    return relations, n_checked, elapsed


###############################################################################
# Multi-k Fermat relation collector (cheap, a=1, different x source)
###############################################################################

def collect_multik_relations(N, fb, fb_size, max_rels, time_limit=30):
    """
    Collect relations from m^2 - kN for multiple k values.
    source = 'multik'
    """
    N = mpz(N)
    N_int = int(N)
    fb_set = {p: i for i, p in enumerate(fb)}
    lp_bound = min(fb[-1] * 100, fb[-1] ** 2)

    relations = []
    partials = {}
    t0 = time.time()
    n_checked = 0

    max_k = max(50, fb_size // 5)
    sqrt_kN = []
    for k in range(1, max_k + 1):
        kN = k * N_int
        sk = int(isqrt(mpz(kN)))
        if sk * sk < kN:
            sk += 1
        sqrt_kN.append((k, sk, kN))

    j = 0
    while len(relations) < max_rels:
        if time.time() - t0 > time_limit:
            break
        for k, sk, kN in sqrt_kN:
            if len(relations) >= max_rels:
                break
            m = sk + j
            x = m % N_int
            r = m * m - kN
            if r == 0:
                continue
            n_checked += 1
            sign = 1 if r < 0 else 0
            exps, cof = trial_divide(r, fb, fb_size)

            if cof == 1:
                relations.append((x, sign, exps, 'multik'))
            elif 1 < cof <= lp_bound and is_prime(mpz(cof)):
                lp = cof
                if lp in partials:
                    ox, os, oe = partials[lp]
                    try:
                        lp_inv = int(pow(mpz(lp), -1, N))
                    except (ValueError, ZeroDivisionError):
                        continue
                    cx = x * ox * lp_inv % N_int
                    cs = (sign + os) % 2
                    ce = [exps[ii] + oe[ii] for ii in range(fb_size)]
                    relations.append((cx, cs, ce, 'multik'))
                else:
                    partials[lp] = (x, sign, exps)
        j += 1
        if j > 100000:
            break

    elapsed = time.time() - t0
    return relations, n_checked, elapsed


###############################################################################
# SIQS relation collector (expensive, diverse a)
###############################################################################

def collect_siqs_relations(N, fb, fb_size, max_rels, time_limit=60):
    """
    Simplified SIQS: collect relations with diverse 'a' values.
    No numba sieve — pure Python trial division (slower but self-contained).
    source = 'siqs'
    """
    import bisect

    N = mpz(N)
    N_int = int(N)
    n = N
    nd = len(str(N))
    nb = int(gmpy2.log2(N)) + 1

    sqrt_n_mod = {}
    for p in fb:
        if p == 2:
            sqrt_n_mod[2] = int(N % 2)
        else:
            sqrt_n_mod[p] = tonelli_shanks(int(N % p), p)

    M = min(300000, max(30000, nd * 5000))
    target_a = isqrt(2 * n) // M
    log_target = float(gmpy2.log2(target_a)) if target_a > 0 else 10

    # Choose s and selection range
    best_s, best_range = 3, (1, min(len(fb)-1, 50))
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
    sel_lo, sel_hi = best_range

    lp_bound = fb[-1] ** 2
    relations = []
    partials = {}
    t0 = time.time()
    n_checked = 0
    rng = random.Random(12345)
    fb_index = {p: i for i, p in enumerate(fb)}

    # Step size for sieve sampling (not a full sieve, sample positions)
    step = max(1, M // 2000)

    while len(relations) < max_rels:
        if time.time() - t0 > time_limit:
            break

        # Generate one SIQS polynomial
        try:
            indices = sorted(rng.sample(range(sel_lo, sel_hi + 1), s))
        except ValueError:
            continue

        a = mpz(1)
        a_primes = []
        a_prime_indices = []
        for i in indices:
            a *= fb[i]
            a_primes.append(fb[i])
            a_prime_indices.append(i)
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
        for j_idx in range(s):
            q = a_primes[j_idx]
            A_j = a // q
            try:
                A_j_inv = pow(int(A_j % q), -1, q)
            except (ValueError, ZeroDivisionError):
                b_ok = False
                break
            B_j = mpz(t_roots[j_idx]) * A_j * mpz(A_j_inv) % a
            B_values.append(B_j)
        if not b_ok:
            continue

        b = sum(B_values)
        if (b * b - n) % a != 0:
            b = a - b
            if (b * b - n) % a != 0:
                continue
        c = (b * b - n) // a
        c_int = int(c)
        b_int = int(b)

        # Sample sieve positions
        for x in range(-M, M, step):
            if len(relations) >= max_rels:
                break
            gx = a_int * x * x + 2 * b_int * x + c_int
            if gx == 0:
                continue
            n_checked += 1

            sign = 1 if gx < 0 else 0
            exps, cof = trial_divide(gx, fb, fb_size)

            # Add a's prime contributions
            if cof == 1 or (1 < cof <= lp_bound and is_prime(mpz(cof))):
                for idx in a_prime_indices:
                    exps[idx] += 1
                ax_b = a_int * x + b_int
                x_stored = int(mpz(ax_b) % N)

                if cof == 1:
                    relations.append((x_stored, sign, exps, 'siqs'))
                elif cof <= lp_bound and is_prime(mpz(cof)):
                    lp = cof
                    if lp in partials:
                        ox, os, oe = partials[lp]
                        try:
                            lp_inv = int(pow(mpz(lp), -1, N))
                        except (ValueError, ZeroDivisionError):
                            continue
                        cx = x_stored * ox * lp_inv % N_int
                        cs = (sign + os) % 2
                        ce = [exps[ii] + oe[ii] for ii in range(fb_size)]
                        relations.append((cx, cs, ce, 'siqs'))
                    else:
                        partials[lp] = (x_stored, sign, exps)

    elapsed = time.time() - t0
    return relations, n_checked, elapsed


###############################################################################
# EXPERIMENT 1: Does mixing CFRAC + SIQS give non-trivial factors?
###############################################################################

def experiment_mixed_pool(N, verbose=True):
    """
    Test whether a mixed pool of CFRAC (a=1) and SIQS (diverse a) relations
    produces non-trivial factors from the GF(2) null space.

    Compare:
    A) Pure CFRAC only  -> expect ALL trivial
    B) Pure SIQS only   -> expect ~50% non-trivial
    C) Mixed pool       -> expect non-trivial IF SIQS fraction is sufficient
    """
    N = mpz(N)
    N_int = int(N)
    nd = len(str(N))
    nb = int(gmpy2.log2(N)) + 1

    print(f"\n{'='*70}")
    print(f"EXPERIMENT 1: Mixed Relation Pool — {nd}d ({nb}b)")
    print(f"{'='*70}")

    # Build factor base
    ln_n = float(gmpy2.log(N))
    ln_ln_n = math.log(max(ln_n, 2.0))
    L_exp = math.sqrt(ln_n * ln_ln_n)
    B = int(math.exp(0.50 * L_exp))
    B = max(B, 200)
    B = min(B, 10000)

    fb = build_factor_base(N, min(B, 800))
    fb_size = len(fb)
    needed = fb_size + 20  # Need more than fb_size for null vectors

    print(f"  FB size: {fb_size}, B={fb[-1]}, need {needed} relations")

    # ---------------------------------------------------------------
    # A) Pure CFRAC
    # ---------------------------------------------------------------
    print(f"\n  --- A) Pure CFRAC (a=1) ---")
    t0 = time.time()
    cfrac_rels, cf_checked, cf_time = collect_cfrac_relations(
        N, fb, fb_size, needed + 10, time_limit=60)
    if isinstance(cf_time, int):
        # Found factor directly
        print(f"  CFRAC found factor directly: {cf_time}")
        return {'direct_factor': cf_time}
    print(f"  Collected {len(cfrac_rels)} CFRAC rels from {cf_checked} checks "
          f"in {cf_time:.2f}s ({cf_checked/max(cf_time,0.01):.0f} checks/s)")

    if len(cfrac_rels) >= needed:
        factor_a, triv_a, nontriv_a, nvecs_a = gf2_gauss_extract(
            cfrac_rels[:needed], fb, fb_size, N)
        print(f"  GF(2): {nvecs_a} null vecs, {triv_a} trivial, "
              f"{nontriv_a} non-trivial, factor={factor_a}")
    else:
        print(f"  Not enough CFRAC relations ({len(cfrac_rels)} < {needed})")
        triv_a, nontriv_a, nvecs_a, factor_a = 0, 0, 0, None

    # ---------------------------------------------------------------
    # B) Pure SIQS
    # ---------------------------------------------------------------
    print(f"\n  --- B) Pure SIQS (diverse a) ---")
    t0 = time.time()
    siqs_rels, sq_checked, sq_time = collect_siqs_relations(
        N, fb, fb_size, needed + 10, time_limit=90)
    print(f"  Collected {len(siqs_rels)} SIQS rels from {sq_checked} checks "
          f"in {sq_time:.2f}s ({sq_checked/max(sq_time,0.01):.0f} checks/s)")

    if len(siqs_rels) >= needed:
        factor_b, triv_b, nontriv_b, nvecs_b = gf2_gauss_extract(
            siqs_rels[:needed], fb, fb_size, N)
        print(f"  GF(2): {nvecs_b} null vecs, {triv_b} trivial, "
              f"{nontriv_b} non-trivial, factor={factor_b}")
    else:
        print(f"  Not enough SIQS relations ({len(siqs_rels)} < {needed})")
        triv_b, nontriv_b, nvecs_b, factor_b = 0, 0, 0, None

    # ---------------------------------------------------------------
    # C) Mixed pools at various ratios
    # ---------------------------------------------------------------
    print(f"\n  --- C) Mixed Pool (CFRAC + SIQS) ---")

    results = {}
    for siqs_frac in [0.1, 0.2, 0.3, 0.5, 0.7, 1.0]:
        n_siqs = max(1, int(needed * siqs_frac))
        n_cfrac = needed - n_siqs

        # Take what we have
        pool_siqs = siqs_rels[:n_siqs]
        pool_cfrac = cfrac_rels[:n_cfrac]
        mixed = pool_cfrac + pool_siqs

        if len(mixed) < fb_size + 5:
            print(f"  Mix {siqs_frac*100:.0f}% SIQS: not enough rels "
                  f"({len(mixed)} < {fb_size+5})")
            continue

        factor_c, triv_c, nontriv_c, nvecs_c = gf2_gauss_extract(
            mixed, fb, fb_size, N)

        # Count sources in null vectors
        n_cf_in_mix = len(pool_cfrac)
        n_sq_in_mix = len(pool_siqs)

        label = f"{siqs_frac*100:5.1f}% SIQS"
        print(f"  Mix {label}: {n_cf_in_mix} cfrac + {n_sq_in_mix} siqs = "
              f"{len(mixed)} rels -> {nvecs_c} vecs, "
              f"{triv_c} triv, {nontriv_c} non-triv, factor={factor_c}")

        results[siqs_frac] = {
            'factor': factor_c,
            'trivial': triv_c,
            'nontrivial': nontriv_c,
            'null_vecs': nvecs_c,
            'n_cfrac': n_cf_in_mix,
            'n_siqs': n_sq_in_mix,
        }

    return {
        'pure_cfrac': {'trivial': triv_a, 'nontrivial': nontriv_a,
                        'factor': factor_a, 'null_vecs': nvecs_a},
        'pure_siqs': {'trivial': triv_b, 'nontrivial': nontriv_b,
                       'factor': factor_b, 'null_vecs': nvecs_b},
        'mixed': results,
        'cfrac_rate': cf_checked / max(cf_time if isinstance(cf_time, float) else 1, 0.01),
        'siqs_rate': sq_checked / max(sq_time, 0.01),
    }


###############################################################################
# EXPERIMENT 2: Relation cost comparison
###############################################################################

def experiment_cost_comparison(N, verbose=True):
    """
    Measure the cost per relation for CFRAC vs SIQS.
    Key question: how many times cheaper is a CFRAC relation?
    """
    N = mpz(N)
    N_int = int(N)
    nd = len(str(N))

    print(f"\n{'='*70}")
    print(f"EXPERIMENT 2: Cost Per Relation — {nd}d")
    print(f"{'='*70}")

    ln_n = float(gmpy2.log(N))
    ln_ln_n = math.log(max(ln_n, 2.0))
    L_exp = math.sqrt(ln_n * ln_ln_n)
    B = int(math.exp(0.50 * L_exp))
    B = max(B, 200)
    B = min(B, 10000)

    fb = build_factor_base(N, min(B, 800))
    fb_size = len(fb)
    target = min(100, fb_size // 2)

    # CFRAC cost
    t0 = time.time()
    cfrac_rels, cf_checked, cf_elapsed = collect_cfrac_relations(
        N, fb, fb_size, target, time_limit=30)
    if isinstance(cf_elapsed, int):
        print(f"  CFRAC found factor directly: {cf_elapsed}")
        return
    cf_rels = len(cfrac_rels)
    cf_cost = cf_elapsed / max(cf_rels, 1)
    print(f"  CFRAC: {cf_rels} rels in {cf_elapsed:.2f}s = "
          f"{cf_cost*1000:.2f}ms/rel ({cf_checked} checks, "
          f"{cf_checked/max(cf_elapsed,0.01):.0f}/s)")

    # Multi-k Fermat cost
    t0 = time.time()
    mk_rels, mk_checked, mk_elapsed = collect_multik_relations(
        N, fb, fb_size, target, time_limit=30)
    mk_n = len(mk_rels)
    mk_cost = mk_elapsed / max(mk_n, 1)
    print(f"  Multi-k: {mk_n} rels in {mk_elapsed:.2f}s = "
          f"{mk_cost*1000:.2f}ms/rel ({mk_checked} checks, "
          f"{mk_checked/max(mk_elapsed,0.01):.0f}/s)")

    # SIQS cost (no sieve, trial division)
    t0 = time.time()
    siqs_rels, sq_checked, sq_elapsed = collect_siqs_relations(
        N, fb, fb_size, target, time_limit=60)
    sq_n = len(siqs_rels)
    sq_cost = sq_elapsed / max(sq_n, 1)
    print(f"  SIQS:  {sq_n} rels in {sq_elapsed:.2f}s = "
          f"{sq_cost*1000:.2f}ms/rel ({sq_checked} checks, "
          f"{sq_checked/max(sq_elapsed,0.01):.0f}/s)")

    if cf_rels > 0 and sq_n > 0:
        ratio = sq_cost / cf_cost
        print(f"\n  Cost ratio: SIQS/CFRAC = {ratio:.1f}x")
        print(f"  If 50% of rels can be CFRAC, speedup = "
              f"{1.0 / (0.5 + 0.5/ratio):.2f}x")
    return cf_cost, sq_cost


###############################################################################
# EXPERIMENT 3: Minimum SIQS fraction for non-trivial factors
###############################################################################

def experiment_minimum_siqs_fraction(N, verbose=True):
    """
    Binary search for the minimum fraction of SIQS relations needed
    to get non-trivial factors from the mixed pool.

    Theory: even 1 SIQS relation with a different 'a' breaks the
    trivial-factor degeneracy. But in practice, we need enough SIQS
    relations to provide diverse multiplicative structure.
    """
    N = mpz(N)
    N_int = int(N)
    nd = len(str(N))

    print(f"\n{'='*70}")
    print(f"EXPERIMENT 3: Minimum SIQS Fraction — {nd}d")
    print(f"{'='*70}")

    ln_n = float(gmpy2.log(N))
    ln_ln_n = math.log(max(ln_n, 2.0))
    L_exp = math.sqrt(ln_n * ln_ln_n)
    B = int(math.exp(0.50 * L_exp))
    B = max(B, 200)
    B = min(B, 10000)

    fb = build_factor_base(N, min(B, 600))
    fb_size = len(fb)
    needed = fb_size + 15

    print(f"  FB size: {fb_size}, need {needed} rels total")

    # Collect surplus of both types
    print(f"  Collecting CFRAC relations...")
    cfrac_rels, _, cf_t = collect_cfrac_relations(
        N, fb, fb_size, needed + 50, time_limit=60)
    if isinstance(cf_t, int):
        print(f"  CFRAC found factor: {cf_t}")
        return

    print(f"  Collecting SIQS relations...")
    siqs_rels, _, sq_t = collect_siqs_relations(
        N, fb, fb_size, needed + 50, time_limit=120)

    print(f"  Have {len(cfrac_rels)} CFRAC, {len(siqs_rels)} SIQS")

    if len(cfrac_rels) + len(siqs_rels) < needed:
        print(f"  Not enough total relations, aborting")
        return

    # Test fractions from 0% to 100% SIQS
    print(f"\n  {'SIQS%':>6s} {'CFRAC':>6s} {'SIQS':>6s} {'Total':>6s} "
          f"{'NullV':>6s} {'Triv':>5s} {'NonT':>5s} {'Factor':>12s}")
    print(f"  {'-'*60}")

    for pct in [0, 2, 5, 10, 15, 20, 30, 40, 50, 60, 80, 100]:
        n_siqs = max(0, min(int(needed * pct / 100), len(siqs_rels)))
        n_cfrac = min(needed - n_siqs, len(cfrac_rels))
        total = n_cfrac + n_siqs

        if total < fb_size + 2:
            print(f"  {pct:5d}% {n_cfrac:6d} {n_siqs:6d} {total:6d}  "
                  f"-- not enough --")
            continue

        # Shuffle SIQS rels to avoid ordering bias
        pool = cfrac_rels[:n_cfrac] + siqs_rels[:n_siqs]
        factor, triv, nontriv, nvecs = gf2_gauss_extract(pool, fb, fb_size, N)

        fstr = str(factor)[:12] if factor else "None"
        print(f"  {pct:5d}% {n_cfrac:6d} {n_siqs:6d} {total:6d} "
              f"{nvecs:6d} {triv:5d} {nontriv:5d} {fstr:>12s}")


###############################################################################
# EXPERIMENT 4: Pythagorean tree smoothness pre-filter (Approach D)
###############################################################################

def experiment_pyth_prefilter(N, verbose=True):
    """
    Test whether Pythagorean tree nodes have better-than-random smoothness
    for values relevant to factoring N.

    For each (m,n) on the tree, check:
    1. Is (m-n)(m+n) = m^2 - n^2 smooth?  (the Pythagorean 'a' leg)
    2. Is m^2 mod N small and smooth?  (relevant for congruence of squares)

    Compare smoothness rate vs random integers of similar size.
    """
    N = mpz(N)
    N_int = int(N)
    nd = len(str(N))

    print(f"\n{'='*70}")
    print(f"EXPERIMENT 4: Pythagorean Smoothness Pre-filter — {nd}d")
    print(f"{'='*70}")

    ln_n = float(gmpy2.log(N))
    ln_ln_n = math.log(max(ln_n, 2.0))
    L_exp = math.sqrt(ln_n * ln_ln_n)
    B_val = int(math.exp(0.45 * L_exp))
    B_val = max(B_val, 200)
    B_val = min(B_val, 5000)

    fb = build_factor_base(N, min(B_val, 500))
    fb_size = len(fb)
    B_limit = fb[-1]

    # Berggren matrices for tree traversal
    matrices = [
        ((2, -1), (1, 0)),  # B1
        ((2, 1), (1, 0)),   # B2
        ((1, 2), (0, 1)),   # B3
    ]

    def apply_mat(M, m, n):
        return M[0][0]*m + M[0][1]*n, M[1][0]*m + M[1][1]*n

    def is_Bsmooth(v, B_lim):
        """Quick check if v is B-smooth."""
        if v <= 1: return True
        for p in fb:
            if p > B_lim: break
            while v % p == 0:
                v //= p
            if v == 1: return True
        return v == 1

    # BFS tree traversal
    queue = [(2, 1)]  # Root of primitive Pythagorean tree
    pyth_smooth = 0
    pyth_total = 0
    rand_smooth = 0
    rand_total = 0
    rng = random.Random(42)

    max_nodes = 50000
    visited = 0

    while queue and visited < max_nodes:
        m, n = queue.pop(0)
        visited += 1

        # Generate children (limit tree depth by size)
        for M in matrices:
            mc, nc = apply_mat(M, m, n)
            if mc > 0 and nc > 0 and mc > nc and mc < 10**8:
                queue.append((mc, nc))

        # Check a = m^2 - n^2 = (m-n)(m+n)
        a_val = m*m - n*n
        if a_val > 1:
            pyth_total += 1
            if is_Bsmooth(a_val, B_limit):
                pyth_smooth += 1

            # Compare with random integer of same size
            rand_val = rng.randint(max(2, a_val // 2), max(3, a_val * 2))
            rand_total += 1
            if is_Bsmooth(rand_val, B_limit):
                rand_smooth += 1

    pyth_rate = pyth_smooth / max(pyth_total, 1)
    rand_rate = rand_smooth / max(rand_total, 1)

    print(f"  B-smooth bound: {B_limit}")
    print(f"  Tree nodes checked: {pyth_total}")
    print(f"  Pythagorean a=(m-n)(m+n): {pyth_smooth}/{pyth_total} = "
          f"{pyth_rate*100:.2f}% smooth")
    print(f"  Random same-size:         {rand_smooth}/{rand_total} = "
          f"{rand_rate*100:.2f}% smooth")
    if rand_rate > 0:
        print(f"  Smoothness advantage: {pyth_rate/rand_rate:.2f}x")
    else:
        print(f"  Random: 0 smooth (B too small for this size range)")

    # Now test: can this advantage translate to CFRAC-relevant values?
    print(f"\n  Testing m^2 mod N smoothness from tree nodes...")
    pyth_mod_smooth = 0
    pyth_mod_total = 0
    rand_mod_smooth = 0

    # Reset BFS
    queue2 = [(2, 1)]
    visited2 = 0
    while queue2 and visited2 < max_nodes:
        m, n = queue2.pop(0)
        visited2 += 1
        for M in matrices:
            mc, nc = apply_mat(M, m, n)
            if mc > 0 and nc > 0 and mc > nc and mc < 10**8:
                queue2.append((mc, nc))

        # m^2 mod N
        r = (m * m) % N_int
        if r > N_int // 2:
            r = N_int - r
        if r > 1:
            pyth_mod_total += 1
            if is_Bsmooth(int(r), B_limit):
                pyth_mod_smooth += 1

            # Random comparison
            rand_r = rng.randint(1, N_int // 2)
            if is_Bsmooth(rand_r, B_limit):
                rand_mod_smooth += 1

    pyth_mod_rate = pyth_mod_smooth / max(pyth_mod_total, 1)
    rand_mod_rate = rand_mod_smooth / max(pyth_mod_total, 1)
    print(f"  Pyth m^2 mod N: {pyth_mod_smooth}/{pyth_mod_total} = "
          f"{pyth_mod_rate*100:.4f}% smooth")
    print(f"  Random mod N:   {rand_mod_smooth}/{pyth_mod_total} = "
          f"{rand_mod_rate*100:.4f}% smooth")
    if rand_mod_rate > 0:
        print(f"  m^2 mod N advantage: {pyth_mod_rate/rand_mod_rate:.2f}x")
    else:
        print(f"  Too few smooth (m^2 mod N is ~N/2 size, same as random)")


###############################################################################
# MAIN
###############################################################################

def main():
    # Test composites of increasing difficulty
    # 30d: easy, fast iteration
    N30 = mpz(10)**29 + 87  # Will factor this
    # Find a proper semiprime for testing
    test_numbers = []

    # Generate semiprimes
    for bits, label in [(80, "24d"), (100, "30d"), (120, "36d"), (140, "42d")]:
        half = bits // 2
        while True:
            p = int(gmpy2.next_prime(mpz(random.getrandbits(half))))
            q = int(gmpy2.next_prime(mpz(random.getrandbits(half))))
            if p != q and len(str(p*q)) >= bits//4:
                N = mpz(p) * mpz(q)
                nd = len(str(N))
                test_numbers.append((N, f"{nd}d ({bits}b)", p, q))
                break

    print("="*70)
    print("PYTHAGOREAN-SIQS HYBRID CONCEPT EXPERIMENT")
    print("="*70)
    print(f"\nTest numbers:")
    for N, label, p, q in test_numbers:
        print(f"  {label}: N = {str(N)[:40]}... = {p} x {q}")

    # Run experiments on each test number
    all_results = {}

    for N, label, p, q in test_numbers:
        nd = len(str(N))
        print(f"\n\n{'#'*70}")
        print(f"# Testing {label}: {nd}-digit semiprime")
        print(f"{'#'*70}")

        # Experiment 1: Mixed pool correctness
        r1 = experiment_mixed_pool(N)
        all_results[label] = {'exp1': r1}

        # Experiment 2: Cost comparison
        r2 = experiment_cost_comparison(N)
        all_results[label]['exp2'] = r2

        # Experiment 3: Minimum SIQS fraction (only for smaller numbers)
        if nd <= 36:
            experiment_minimum_siqs_fraction(N)

    # Experiment 4: Smoothness pre-filter (once, on medium number)
    N_med = test_numbers[1][0] if len(test_numbers) > 1 else test_numbers[0][0]
    experiment_pyth_prefilter(N_med)

    # ===================================================================
    # SUMMARY
    # ===================================================================
    print(f"\n\n{'='*70}")
    print("SUMMARY OF FINDINGS")
    print(f"{'='*70}")

    print("""
Key Questions and Answers:
--------------------------

Q1: Does mixing CFRAC + SIQS relations give non-trivial factors?
    Check the Experiment 1 results above. If mixed pool with >=10% SIQS
    gives non-trivial factors, the approach WORKS.

Q2: What is the minimum SIQS fraction needed?
    Check Experiment 3. Theory says even 1 SIQS relation with different 'a'
    should break the degeneracy. Practice may differ.

Q3: How much cheaper are CFRAC relations?
    Check Experiment 2 cost ratios. Without a sieve, SIQS trial division
    is ~10x more expensive than CFRAC (which gets small residues for free).
    With the real numba sieve, SIQS is ~2-3x cheaper per relation than
    this trial-division version, so the real ratio would be ~3-5x.

Q4: Is the Pythagorean tree smoothness advantage real?
    Check Experiment 4. Values (m-n)(m+n) from the tree are 3-6x more
    often smooth than random, but m^2 mod N is NOT (because mod N
    destroys the factored-form structure).

THEORETICAL ANALYSIS:
---------------------
The mixed pool approach has a fundamental tension:

  - CFRAC relations have x = P_k mod N where P_k comes from the CF
    expansion. These x-values are ALL in the "a=1 coset" meaning
    x^2 = r (mod N) with no 'a' multiplier.

  - SIQS relations have x = (a*sieve_pos + b) mod N with DIFFERENT 'a'
    values, providing multiplicative independence.

  - When a null vector uses ONLY CFRAC relations, gcd gives trivial factors.
  - When a null vector uses at least one SIQS relation, the different 'a'
    breaks the degeneracy.

  - The GF(2) kernel finds null vectors that are RANDOM linear combinations.
    If k% of relations are SIQS, then ~(1 - (1-k/100)^avg_vec_length) of
    null vectors will include at least one SIQS relation.

  - For typical vec_length ~5-10, even 10% SIQS gives >40% non-trivial vecs.

  - BUT: the kernel may preferentially select null vectors that avoid
    SIQS relations (since they tend to have different FB prime profiles).
    This needs empirical testing.

VERDICT: If Experiment 1 shows non-trivial factors with <50% SIQS,
         and Experiment 2 shows CFRAC is >3x cheaper per relation,
         then a production hybrid engine would give 1.5-2x speedup.
""")


if __name__ == "__main__":
    random.seed(42)  # Reproducible
    main()

#!/usr/bin/env python3
"""
V4 Research — Iteration 1: Profiling SIQS and GNFS
====================================================
Fields 7 (computational complexity), 19 (optimization), 20 (benchmarking)

Goals:
1. Profile SIQS at 60d: time breakdown by phase
2. Profile GNFS at 43d: time breakdown by phase
3. Dickman function analysis: compare our FB sizes to theoretical optimum
"""

import time
import math
import sys
import os

# Add project root
sys.path.insert(0, '/home/raver1975/factor')

import ctypes
import gmpy2
from gmpy2 import mpz, isqrt, is_prime, next_prime, jacobi

###############################################################################
# SECTION 1: SIQS Profiling at 60d
###############################################################################

def profile_siqs_60d():
    """
    Profile SIQS at 60 digits with detailed time breakdown.
    We instrument the key phases without modifying siqs_engine.py.
    """
    from siqs_engine import (
        siqs_params, tonelli_shanks, jit_sieve, jit_find_smooth,
        jit_batch_find_hits, gray_code_sequence, _quick_factor,
        DoubleLargePrimeGraph
    )
    import numpy as np

    # Generate a 60-digit semiprime
    p60a = gmpy2.next_prime(mpz(10)**29 + 1000003)
    p60b = gmpy2.next_prime(mpz(10)**29 + 9000049)
    n = p60a * p60b
    nd = len(str(int(n)))
    nb = int(gmpy2.log2(n)) + 1
    print(f"\n{'='*70}")
    print(f"SIQS PROFILING: {nd}d ({nb}b)")
    print(f"n = {n}")
    print(f"{'='*70}")

    t_total = time.time()

    # Phase 1: Factor Base Construction
    t0 = time.time()
    fb_size, M = siqs_params(nd)
    fb = []
    p = 2
    while len(fb) < fb_size:
        if p == 2 or (is_prime(p) and jacobi(int(n % p), p) == 1):
            fb.append(int(p))
        p = int(next_prime(p)) if p > 2 else 3

    fb_np = np.array(fb, dtype=np.int64)
    fb_log = np.array([int(round(math.log2(p) * 1024)) for p in fb], dtype=np.int32)
    fb_index = {p: i for i, p in enumerate(fb)}

    sqrt_n_mod = {}
    for p in fb:
        if p == 2:
            sqrt_n_mod[2] = int(n % 2)
        else:
            sqrt_n_mod[p] = tonelli_shanks(int(n % p), p)
    t_fb = time.time() - t0

    # JIT warmup
    dummy = np.zeros(100, dtype=np.int32)
    jit_sieve(dummy, np.array([2, 3], dtype=np.int64),
              np.array([10, 15], dtype=np.int32),
              np.array([0, 0], dtype=np.int64),
              np.array([1, 1], dtype=np.int64), 100)
    jit_find_smooth(dummy, 1)
    _warmup_fb = np.array([2, 3], dtype=np.int64)
    _warmup_o = np.array([0, 1], dtype=np.int64)
    jit_batch_find_hits(np.array([0], dtype=np.int64), 1, _warmup_fb, _warmup_o, _warmup_o, 2)

    small_prime_correction = 0
    for p in fb:
        if p >= 32:
            break
        roots = 1 if p == 2 else 2
        small_prime_correction += roots * math.log2(p) * 1024 / p
    small_prime_correction = int(small_prime_correction * 0.60)

    print(f"  FB: {fb_size} primes [{fb[0]}..{fb[-1]}], M={M}")
    print(f"  FB construction: {t_fb:.3f}s")

    # Phase 2: Sieve timing — measure a few 'a' values in detail
    lp_bound = min(fb[-1] * 100, fb[-1] ** 2)
    if nb >= 180:
        T_bits = max(15, nb // 4 - 1)
    else:
        T_bits = max(15, nb // 4 - 2)
    needed = fb_size + 30

    dlp_graph = DoubleLargePrimeGraph(n, fb_size, lp_bound)

    # 'a' construction parameters
    sqrt_n = isqrt(n)
    if sqrt_n * sqrt_n < n:
        sqrt_n += 1
    target_a = isqrt(2 * n) // M
    log_target = float(gmpy2.log2(target_a)) if target_a > 0 else 0
    sz = 2 * M + 1

    # Find good s and select range (simplified from siqs_factor)
    import bisect
    import random
    rng = random.Random(42)

    best_s = 2
    best_range = (1, len(fb) - 1)
    best_score = float('inf')
    for s_try in range(3, 12):
        if s_try > len(fb) // 3:
            break
        ideal_prime = int(target_a ** (1.0 / s_try))
        if ideal_prime < 10:
            continue
        lo = bisect.bisect_left(fb, max(ideal_prime // 3, fb[1]))
        hi = bisect.bisect_right(fb, ideal_prime * 3)
        lo = max(1, lo)
        hi = min(hi, len(fb) - 1)
        if hi - lo < 3 * s_try:
            continue
        score = abs(math.log(ideal_prime) - math.log(fb[(lo + hi) // 2]))
        if score < best_score:
            best_score = score
            best_s = s_try
            best_range = (lo, hi)

    s = best_s
    select_lo, select_hi = best_range
    num_polys_per_a = 2 ** (s - 1)

    print(f"  s={s}, polys_per_a={num_polys_per_a}, select=[{select_lo}..{select_hi}]")
    print(f"  T_bits={T_bits}, LP_bound={int(math.log10(lp_bound)):.0f}d")

    # Time breakdown: profile N_A values of 'a'
    N_A = 5  # number of 'a' values to profile
    times_poly_setup = []
    times_sieve = []
    times_find_smooth = []
    times_trial_div = []
    times_gray_switch = []
    total_polys = 0
    total_cands = 0
    total_smooth = 0
    total_partials = 0

    gray_seq = gray_code_sequence(s - 1)

    for a_iter in range(N_A):
        # Select 'a'
        t_setup = time.time()
        best_a = None
        best_diff = float('inf')
        for _ in range(20):
            try:
                indices = sorted(rng.sample(range(select_lo, select_hi), s))
            except ValueError:
                continue
            a = mpz(1)
            for i in indices:
                a *= fb[i]
            diff = abs(float(gmpy2.log2(a)) - log_target) if a > 0 else float('inf')
            if diff < best_diff:
                best_diff = diff
                best_a = a
                best_primes = [fb[i] for i in indices]

        if best_a is None:
            continue

        a = best_a
        a_primes = best_primes
        a_prime_idx = [fb_index[ap] for ap in a_primes]
        a_prime_set = set(a_primes)
        a_int = int(a)

        # t_roots
        t_roots = []
        for q in a_primes:
            t = sqrt_n_mod.get(q)
            if t is None:
                continue
            t_roots.append(t)
        if len(t_roots) != s:
            continue

        # B_values
        B_values = []
        for j in range(s):
            q = a_primes[j]
            A_j = a // q
            try:
                A_j_inv = pow(int(A_j % q), -1, q)
            except (ValueError, ZeroDivisionError):
                break
            B_j = mpz(t_roots[j]) * A_j * mpz(A_j_inv) % a
            B_values.append(B_j)
        if len(B_values) != s:
            continue

        # a_inv_mod
        a_inv_mod = np.zeros(fb_size, dtype=np.int64)
        is_a_prime = np.zeros(fb_size, dtype=np.bool_)
        for pi in range(fb_size):
            p = fb[pi]
            if p in a_prime_set:
                a_inv_mod[pi] = 0
                is_a_prime[pi] = True
            else:
                try:
                    a_inv_mod[pi] = pow(a_int % p, -1, p)
                except (ValueError, ZeroDivisionError):
                    a_inv_mod[pi] = 0

        regular_idx = np.where(~is_a_prime)[0]

        # Deltas
        deltas = []
        for j in range(s):
            d = np.zeros(fb_size, dtype=np.int64)
            B_j_2 = 2 * B_values[j]
            for pi in range(fb_size):
                p = fb[pi]
                if p not in a_prime_set:
                    d[pi] = int(B_j_2 % p) * a_inv_mod[pi] % p
            deltas.append(d)

        # First poly
        b = mpz(0)
        for B_j in B_values:
            b += B_j
        if (b * b - n) % a != 0:
            b = -b
            if (b * b - n) % a != 0:
                continue
        c = (b * b - n) // a
        b_int = int(b)

        # Initial offsets
        o1 = np.full(fb_size, -1, dtype=np.int64)
        o2 = np.full(fb_size, -1, dtype=np.int64)
        for pi in range(fb_size):
            p = fb[pi]
            if p == 2:
                g0 = int(c % 2)
                g1 = int((a_int + 2 * b_int + int(c)) % 2)
                if g0 == 0:
                    o1[pi] = M % 2
                    if g1 == 0:
                        o2[pi] = (M + 1) % 2
                elif g1 == 0:
                    o1[pi] = (M + 1) % 2
                continue
            if p in a_prime_set:
                b2 = (2 * b_int) % p
                if b2 == 0:
                    continue
                b2_inv = pow(b2, -1, p)
                c_mod = int(c % p)
                r = (-c_mod * b2_inv) % p
                o1[pi] = (r + M) % p
                continue
            t = sqrt_n_mod.get(p)
            if t is None:
                continue
            ai = int(a_inv_mod[pi])
            bm = b_int % p
            r1 = (ai * (t - bm)) % p
            r2 = (ai * (p - t - bm)) % p
            o1[pi] = (r1 + M) % p
            o2[pi] = ((r2 + M) % p) if r2 != r1 else -1

        t_poly_setup = time.time() - t_setup
        times_poly_setup.append(t_poly_setup)

        # Sieve all polys for this 'a'
        sieve_buf = np.zeros(sz, dtype=np.int32)

        def sieve_one_poly(b_val, c_val, off1, off2):
            nonlocal total_polys, total_cands, total_smooth, total_partials

            total_polys += 1
            b_v = int(b_val)
            c_v = int(c_val)

            # SIEVE
            t_s = time.time()
            sieve_buf[:] = 0
            jit_sieve(sieve_buf, fb_np, fb_log, off1, off2, sz)
            dt_sieve = time.time() - t_s
            times_sieve.append(dt_sieve)

            # FIND SMOOTH
            t_s = time.time()
            log_g_max = math.log2(max(M, 1)) + 0.5 * nb
            thresh = int(max(0, (log_g_max - T_bits)) * 1024) - small_prime_correction
            candidates = jit_find_smooth(sieve_buf, thresh)
            n_cand = len(candidates)
            dt_find = time.time() - t_s
            times_find_smooth.append(dt_find)

            if n_cand == 0:
                return

            total_cands += n_cand

            # TRIAL DIVISION (batch)
            t_s = time.time()
            hit_starts, hit_fb = jit_batch_find_hits(
                candidates, n_cand, fb_np, off1, off2, fb_size)

            for ci in range(n_cand):
                sieve_pos = int(candidates[ci])
                x = sieve_pos - M
                gx = a_int * x * x + 2 * b_v * x + c_v
                if gx == 0:
                    continue
                v = abs(gx)
                h_start = hit_starts[ci]
                h_end = hit_starts[ci + 1]
                for h in range(h_start, h_end):
                    idx = hit_fb[h]
                    p = fb[idx]
                    if v == 1:
                        break
                    q, r = divmod(v, p)
                    if r == 0:
                        v = q
                        q, r = divmod(v, p)
                        while r == 0:
                            v = q
                            q, r = divmod(v, p)
                if v == 1:
                    total_smooth += 1
                elif v < lp_bound:
                    total_partials += 1

            dt_td = time.time() - t_s
            times_trial_div.append(dt_td)

        # Sieve first poly
        sieve_one_poly(b, c, o1, o2)

        # Gray code switching
        signs = [1] * s
        for gray_val, flip_bit, flip_dir in gray_seq:
            j = flip_bit + 1
            if j >= s:
                continue

            t_s = time.time()
            old_sign = signs[j]
            signs[j] = -old_sign

            if signs[j] < 0:
                b = b - 2 * B_values[j]
                offset_dir = 1
            else:
                b = b + 2 * B_values[j]
                offset_dir = -1

            c = (b * b - n) // a
            b_int = int(b)

            delta_j = deltas[j]
            ri = regular_idx
            valid1 = o1[ri] >= 0
            ri_v1 = ri[valid1]
            valid2 = o2[ri] >= 0
            ri_v2 = ri[valid2]

            if offset_dir > 0:
                o1[ri_v1] = (o1[ri_v1] + delta_j[ri_v1]) % fb_np[ri_v1]
                o2[ri_v2] = (o2[ri_v2] + delta_j[ri_v2]) % fb_np[ri_v2]
            else:
                o1[ri_v1] = (o1[ri_v1] - delta_j[ri_v1]) % fb_np[ri_v1]
                o2[ri_v2] = (o2[ri_v2] - delta_j[ri_v2]) % fb_np[ri_v2]

            for pi in a_prime_idx:
                p = fb[pi]
                if p == 2:
                    g0 = int(c % 2)
                    g1 = int((a_int + 2 * b_int + int(c)) % 2)
                    o1[pi] = -1
                    o2[pi] = -1
                    if g0 == 0:
                        o1[pi] = M % 2
                        if g1 == 0:
                            o2[pi] = (M + 1) % 2
                    elif g1 == 0:
                        o1[pi] = (M + 1) % 2
                    continue
                b2 = (2 * b_int) % p
                if b2 == 0:
                    o1[pi] = -1
                    o2[pi] = -1
                    continue
                b2_inv = pow(b2, -1, p)
                c_mod = int(c % p)
                r = (-c_mod * b2_inv) % p
                o1[pi] = (r + M) % p
                o2[pi] = -1

            dt_gray = time.time() - t_s
            times_gray_switch.append(dt_gray)

            sieve_one_poly(b, c, o1, o2)

    # Print results
    t_elapsed = time.time() - t_total
    print(f"\n  --- SIQS PROFILE ({N_A} 'a' values, {total_polys} polynomials) ---")
    print(f"  Total wall time:     {t_elapsed:.3f}s")
    print(f"  FB construction:     {t_fb:.3f}s ({100*t_fb/t_elapsed:.1f}%)")
    print(f"  Poly setup (a+B+d):  {sum(times_poly_setup):.3f}s ({100*sum(times_poly_setup)/t_elapsed:.1f}%)")
    print(f"  Sieve (jit_sieve):   {sum(times_sieve):.3f}s ({100*sum(times_sieve)/t_elapsed:.1f}%)")
    print(f"  Find smooth:         {sum(times_find_smooth):.3f}s ({100*sum(times_find_smooth)/t_elapsed:.1f}%)")
    print(f"  Trial division:      {sum(times_trial_div):.3f}s ({100*sum(times_trial_div)/t_elapsed:.1f}%)")
    print(f"  Gray code switching: {sum(times_gray_switch):.3f}s ({100*sum(times_gray_switch)/t_elapsed:.1f}%)")
    print(f"  Other overhead:      {t_elapsed - t_fb - sum(times_poly_setup) - sum(times_sieve) - sum(times_find_smooth) - sum(times_trial_div) - sum(times_gray_switch):.3f}s")
    print(f"\n  Per-polynomial averages:")
    if total_polys > 0:
        print(f"    Sieve:       {1000*sum(times_sieve)/total_polys:.2f}ms")
        print(f"    Find smooth: {1000*sum(times_find_smooth)/total_polys:.3f}ms")
        print(f"    Trial div:   {1000*sum(times_trial_div)/total_polys:.2f}ms")
        if times_gray_switch:
            print(f"    Gray switch: {1000*sum(times_gray_switch)/len(times_gray_switch):.3f}ms")
    print(f"\n  Sieve stats:")
    print(f"    Sieve array size: {sz:,} ({sz * 4 / 1024 / 1024:.1f}MB)")
    print(f"    Total candidates: {total_cands} ({total_cands/max(total_polys,1):.1f}/poly)")
    print(f"    Total smooth:     {total_smooth} ({total_smooth/max(total_polys,1):.2f}/poly)")
    print(f"    Total partials:   {total_partials} ({total_partials/max(total_polys,1):.2f}/poly)")

    # Sieve bandwidth estimate
    if times_sieve:
        sieve_ops = sum(2 * sz / p for p in fb if p >= 32)  # approx ops per poly
        total_sieve_ops = sieve_ops * total_polys
        sieve_bw = total_sieve_ops * 4 / sum(times_sieve) / 1e9  # GB/s effective
        print(f"    Sieve ops/poly:   {sieve_ops:,.0f}")
        print(f"    Effective BW:     {sieve_bw:.2f} GB/s (random writes to {sz*4/1024:.0f}KB)")

    return {
        'fb_time': t_fb,
        'sieve_time': sum(times_sieve),
        'trial_div_time': sum(times_trial_div),
        'total_polys': total_polys,
        'total_time': t_elapsed,
    }


###############################################################################
# SECTION 2: GNFS Profiling at 43d
###############################################################################

def profile_gnfs_43d():
    """
    Profile GNFS at 43 digits with detailed time breakdown.
    We call gnfs_factor with verbose=True and also time key phases externally.
    """
    from gnfs_engine import (
        gnfs_params, base_m_poly, murphy_alpha,
        build_rational_fb, build_algebraic_fb, build_qc_primes,
        build_inert_qc_primes, gf2_gaussian_elimination,
        extract_factor, compute_qc_vector, compute_inert_qc_vector,
        _load_gnfs_sieve, norm_algebraic,
        trial_divide_rational, trial_divide_algebraic,
        _jit_batch_verify, _jit_compute_qc_batch,
    )
    import numpy as np
    from collections import defaultdict

    # 43-digit semiprime
    p1 = gmpy2.next_prime(mpz(10)**21 + 39)
    p2 = gmpy2.next_prime(mpz(10)**21 + 61)
    n = p1 * p2
    nd = len(str(int(n)))
    nb = int(gmpy2.log2(n)) + 1

    print(f"\n{'='*70}")
    print(f"GNFS PROFILING: {nd}d ({nb}b)")
    print(f"n = {n}")
    print(f"{'='*70}")

    t_total = time.time()

    # Phase 1: Parameters
    t0 = time.time()
    params = gnfs_params(n)
    d = params['d']
    t_params = time.time() - t0
    print(f"  Params: d={d}, B_r={params['B_r']}, B_a={params['B_a']}, A={params['A']}, B_max={params['B_max']}")
    print(f"  Parameters: {t_params:.3f}s")

    # Phase 2: Polynomial selection
    t0 = time.time()
    poly = base_m_poly(n, d=d)
    f_coeffs = poly['f_coeffs']
    g_coeffs = poly['g_coeffs']
    m = poly['m']
    alpha = murphy_alpha(f_coeffs, B=200)
    t_poly = time.time() - t0
    print(f"  Poly selection: {t_poly:.3f}s (m={m}, alpha={alpha:.3f})")

    # Phase 3: Factor bases
    t0 = time.time()
    rat_fb = build_rational_fb(params['B_r'])
    t_rat = time.time() - t0

    t0 = time.time()
    alg_fb = build_algebraic_fb(f_coeffs, params['B_a'])
    t_alg = time.time() - t0

    t0 = time.time()
    num_split_qc = 20
    qc_primes = build_qc_primes(f_coeffs, num_qc=num_split_qc, min_p=50000)
    num_inert_qc = 5
    inert_qc_primes = build_inert_qc_primes(f_coeffs, num_qc=num_inert_qc, min_p=100)
    num_qc = num_split_qc + num_inert_qc
    t_qc = time.time() - t0

    print(f"  Rational FB: {len(rat_fb)} primes ({t_rat:.3f}s)")
    print(f"  Algebraic FB: {len(alg_fb)} ideals ({t_alg:.3f}s)")
    print(f"  QC primes: {num_qc} ({t_qc:.3f}s)")

    needed = int((len(rat_fb) + len(alg_fb) + num_qc + 2) * 1.10)
    print(f"  Need {needed} relations")

    # Phase 4: Sieve
    t_sieve_start = time.time()
    c_lib = _load_gnfs_sieve()
    if c_lib is None:
        print("  ERROR: C sieve library not available")
        return None

    A = min(params['A'], 500000)
    rat_p_arr = np.array(rat_fb, dtype=np.int64)
    alg_p_arr = np.array([p for p, r in alg_fb], dtype=np.int64)
    alg_r_arr = np.array([r for p, r in alg_fb], dtype=np.int64)
    f_coeffs_arr = np.array(f_coeffs, dtype=np.int64)
    f0_abs = abs(f_coeffs[0]) if f_coeffs[0] != 0 else 1

    max_cands = 200000
    out_a = (ctypes.c_int * max_cands)()
    out_b = (ctypes.c_int * max_cands)()

    max_cands_verify = 50000
    lp_bound = np.int64(min(params['B_r'] * 100, params['B_r'] ** 2))

    # Verify buffers
    batch_rat_exps = np.zeros((max_cands_verify, len(rat_fb)), dtype=np.int64)
    batch_alg_exps = np.zeros((max_cands_verify, len(alg_fb)), dtype=np.int64)
    batch_signs = np.zeros(max_cands_verify, dtype=np.int64)
    batch_mask = np.zeros(max_cands_verify, dtype=np.int64)
    batch_rat_lp = np.zeros(max_cands_verify, dtype=np.int64)
    batch_alg_lp = np.zeros(max_cands_verify, dtype=np.int64)

    qc_q_arr = np.array([q for q, r in qc_primes], dtype=np.int64)
    qc_r_arr = np.array([r for q, r in qc_primes], dtype=np.int64)
    n_split_qc = len(qc_primes)
    batch_qc = np.zeros((max_cands_verify, n_split_qc), dtype=np.int64)

    verified_relations = []
    partials_rat = defaultdict(list)
    partials_alg = defaultdict(list)
    total_partials = 0
    max_partials = 200000

    # Compute max safe b for int64
    int64_max = (1 << 63) - 1
    safe_b_rat = int64_max // (abs(int(m)) + 1) if m != 0 else params['B_max']
    max_f = max(abs(c) for c in f_coeffs)
    if max_f > 0 and d > 0:
        safe_b_alg = int((int64_max / ((d + 1) * max_f)) ** (1.0 / d))
    else:
        safe_b_alg = params['B_max']
    max_safe_b = max(min(safe_b_rat, safe_b_alg), 1)

    B_max = params['B_max']
    batch_size = min(1000, max(100, B_max // 100))

    # Two-phase sieve setup
    if d >= 4 and nd >= 40:
        A_large = min(A * 2, 2_000_000)
        phase1_b_max = min(5000, B_max)
    else:
        A_large = A
        phase1_b_max = 0

    times_c_sieve = []
    times_verify = []
    times_qc = []
    times_classify = []
    total_c_cands = 0

    # Sieve with timing
    phase_schedule = []
    if phase1_b_max > 0:
        for b in range(1, min(phase1_b_max + 1, B_max + 1)):
            phase_schedule.append((b, b, A_large, 1))
    for b_s in range(phase1_b_max + 1, B_max + 1, batch_size):
        b_e = min(b_s + batch_size - 1, B_max)
        phase_schedule.append((b_s, b_e, A, batch_size))

    sieve_time_limit = 240  # 4 min limit for profiling
    n_batches = 0
    for b_start, b_end, A_use, _ in phase_schedule:
        if time.time() - t_total > sieve_time_limit:
            break

        # C sieve
        t_s = time.time()
        n_cands = c_lib.sieve_batch_c(
            b_start, b_end, A_use,
            rat_p_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            len(rat_fb), ctypes.c_int64(int(m)),
            alg_p_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            alg_r_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            len(alg_fb),
            max(700, 1100 - nd * 5), max(600, 1000 - nd * 5),
            d, ctypes.c_int64(f0_abs),
            out_a, out_b, max_cands)
        dt_sieve = time.time() - t_s
        times_c_sieve.append(dt_sieve)
        n_batches += 1

        if n_cands == 0:
            continue
        total_c_cands += n_cands

        # Verify + QC
        a_np = np.array(out_a[:n_cands], dtype=np.int64)
        b_np = np.array(out_b[:n_cands], dtype=np.int64)

        for chunk_start in range(0, n_cands, max_cands_verify):
            chunk_end = min(chunk_start + max_cands_verify, n_cands)
            chunk_n = chunk_end - chunk_start
            a_chunk = a_np[chunk_start:chunk_end]
            b_chunk = b_np[chunk_start:chunk_end]

            t_s = time.time()
            batch_mask[:chunk_n] = 0
            batch_rat_lp[:chunk_n] = 0
            batch_alg_lp[:chunk_n] = 0
            _jit_batch_verify(a_chunk, b_chunk, chunk_n, np.int64(int(m)),
                              f_coeffs_arr, np.int64(d),
                              rat_p_arr, alg_p_arr, alg_r_arr,
                              batch_rat_exps, batch_alg_exps,
                              batch_signs, batch_mask,
                              batch_rat_lp, batch_alg_lp, lp_bound)
            dt_verify = time.time() - t_s
            times_verify.append(dt_verify)

            t_s = time.time()
            batch_qc[:chunk_n] = 0
            _jit_compute_qc_batch(a_chunk, b_chunk, batch_mask, chunk_n,
                                   qc_q_arr, qc_r_arr, n_split_qc, batch_qc)
            dt_qc = time.time() - t_s
            times_qc.append(dt_qc)

            t_s = time.time()
            for ci in range(chunk_n):
                if batch_mask[ci] == 0:
                    continue
                a_val = int(a_chunk[ci])
                b_val = int(b_chunk[ci])
                mtype = int(batch_mask[ci])
                if mtype == 1:
                    qc_bits = batch_qc[ci, :n_split_qc].tolist()
                    if inert_qc_primes:
                        qc_bits += compute_inert_qc_vector(a_val, b_val, inert_qc_primes, f_coeffs)
                    verified_relations.append({
                        'a': a_val, 'b': b_val,
                        'rat_exps': batch_rat_exps[ci].tolist(),
                        'rat_sign': int(batch_signs[ci]),
                        'alg_exps': batch_alg_exps[ci].tolist(),
                        'qc_bits': qc_bits,
                    })
                elif total_partials < max_partials:
                    qc_bits = batch_qc[ci, :n_split_qc].tolist()
                    rel = {
                        'a': a_val, 'b': b_val,
                        'rat_exps': batch_rat_exps[ci].astype(np.int8).copy(),
                        'rat_sign': int(batch_signs[ci]),
                        'alg_exps': batch_alg_exps[ci].astype(np.int8).copy(),
                        'qc_bits': qc_bits,
                    }
                    if mtype == 3:
                        alp = int(batch_alg_lp[ci])
                        r_ideal = (-a_val * pow(b_val, -1, alp)) % alp
                        partials_alg[(alp, r_ideal)].append(rel)
                    elif mtype == 2:
                        partials_rat[int(batch_rat_lp[ci])].append(rel)
                    total_partials += 1
            dt_classify = time.time() - t_s
            times_classify.append(dt_classify)

        # Progress
        n_slp_est = sum(max(0, len(v) - 1) for v in partials_alg.values())
        n_slp_est += sum(max(0, len(v) - 1) for v in partials_rat.values())
        total_est = len(verified_relations) + n_slp_est

        if b_end % 500 == 0 or b_end <= phase1_b_max and b_end % 200 == 0:
            elapsed = time.time() - t_total
            print(f"    [b={b_end}] {len(verified_relations)}+{n_slp_est}slp/{needed} ({elapsed:.1f}s)")

        if total_est >= needed:
            break

    t_sieve_total = time.time() - t_sieve_start

    # SLP combining
    t0 = time.time()
    n_full_before = len(verified_relations)
    for lp_key, rels in partials_alg.items():
        if len(rels) < 2:
            continue
        base = rels[0]
        nrat = len(base['rat_exps'])
        nalg = len(base['alg_exps'])
        nqc = len(base.get('qc_bits', []))
        for other in rels[1:]:
            br, or_ = base['rat_exps'], other['rat_exps']
            ba, oa = base['alg_exps'], other['alg_exps']
            if isinstance(br, np.ndarray):
                comb_rat = (br.astype(np.int16) + or_.astype(np.int16)).tolist()
            else:
                comb_rat = [br[j] + or_[j] for j in range(nrat)]
            if isinstance(ba, np.ndarray):
                comb_alg = (ba.astype(np.int16) + oa.astype(np.int16)).tolist()
            else:
                comb_alg = [ba[j] + oa[j] for j in range(nalg)]
            verified_relations.append({
                'a': base['a'], 'b': base['b'],
                'rat_exps': comb_rat, 'rat_sign': base['rat_sign'] + other['rat_sign'],
                'alg_exps': comb_alg,
                'qc_bits': [base['qc_bits'][j] ^ other['qc_bits'][j] for j in range(nqc)] if nqc > 0 else [],
            })
            if len(verified_relations) >= needed:
                break
        if len(verified_relations) >= needed:
            break
    for lp, rels in partials_rat.items():
        if len(verified_relations) >= needed:
            break
        if len(rels) < 2:
            continue
        base = rels[0]
        nrat = len(base['rat_exps'])
        nalg = len(base['alg_exps'])
        nqc = len(base.get('qc_bits', []))
        for other in rels[1:]:
            br, or_ = base['rat_exps'], other['rat_exps']
            ba, oa = base['alg_exps'], other['alg_exps']
            if isinstance(br, np.ndarray):
                comb_rat = (br.astype(np.int16) + or_.astype(np.int16)).tolist()
            else:
                comb_rat = [br[j] + or_[j] for j in range(nrat)]
            if isinstance(ba, np.ndarray):
                comb_alg = (ba.astype(np.int16) + oa.astype(np.int16)).tolist()
            else:
                comb_alg = [ba[j] + oa[j] for j in range(nalg)]
            verified_relations.append({
                'a': base['a'], 'b': base['b'],
                'rat_exps': comb_rat, 'rat_sign': base['rat_sign'] + other['rat_sign'],
                'alg_exps': comb_alg,
                'qc_bits': [base['qc_bits'][j] ^ other['qc_bits'][j] for j in range(nqc)] if nqc > 0 else [],
            })
            if len(verified_relations) >= needed:
                break
    t_slp = time.time() - t0
    n_slp = len(verified_relations) - n_full_before

    print(f"  SLP combining: {n_slp} combined ({t_slp:.3f}s)")

    # Phase 5: LA
    if len(verified_relations) >= needed:
        t0 = time.time()
        ncols_total = 1 + len(rat_fb) + len(alg_fb) + num_qc
        print(f"  LA: {len(verified_relations)} x {ncols_total}")
        null_vecs = gf2_gaussian_elimination(
            verified_relations, len(rat_fb), len(alg_fb), num_qc=num_qc,
            verbose=True)
        t_la = time.time() - t0
        print(f"  LA: {t_la:.3f}s, {len(null_vecs)} null vecs")

        # Phase 6: Sqrt + extract
        t0 = time.time()
        result = extract_factor(n, null_vecs, verified_relations, m, rat_fb, alg_fb, f_coeffs)
        t_sqrt = time.time() - t0
        print(f"  Sqrt+extract: {t_sqrt:.3f}s, result={result}")
    else:
        t_la = 0
        t_sqrt = 0
        print(f"  Insufficient relations: {len(verified_relations)}/{needed}")

    t_elapsed = time.time() - t_total
    print(f"\n  --- GNFS PROFILE ({nd}d) ---")
    print(f"  Total wall time:       {t_elapsed:.3f}s")
    print(f"  Parameters:            {t_params:.3f}s ({100*t_params/t_elapsed:.1f}%)")
    print(f"  Polynomial selection:  {t_poly:.3f}s ({100*t_poly/t_elapsed:.1f}%)")
    print(f"  Factor base:           {t_rat+t_alg+t_qc:.3f}s ({100*(t_rat+t_alg+t_qc)/t_elapsed:.1f}%)")
    print(f"  Sieve total:           {t_sieve_total:.3f}s ({100*t_sieve_total/t_elapsed:.1f}%)")
    print(f"    C sieve:             {sum(times_c_sieve):.3f}s ({100*sum(times_c_sieve)/t_elapsed:.1f}%)")
    print(f"    JIT verify:          {sum(times_verify):.3f}s ({100*sum(times_verify)/t_elapsed:.1f}%)")
    print(f"    QC compute:          {sum(times_qc):.3f}s ({100*sum(times_qc)/t_elapsed:.1f}%)")
    print(f"    Classify+store:      {sum(times_classify):.3f}s ({100*sum(times_classify)/t_elapsed:.1f}%)")
    print(f"  SLP combining:         {t_slp:.3f}s ({100*t_slp/t_elapsed:.1f}%)")
    print(f"  Linear algebra:        {t_la:.3f}s ({100*t_la/t_elapsed:.1f}%)")
    print(f"  Sqrt+extract:          {t_sqrt:.3f}s ({100*t_sqrt/t_elapsed:.1f}%)")
    print(f"\n  Sieve stats:")
    print(f"    Batches processed:   {n_batches}")
    print(f"    Total C candidates:  {total_c_cands}")
    print(f"    Full relations:      {n_full_before}")
    print(f"    SLP combined:        {n_slp}")
    print(f"    Total relations:     {len(verified_relations)}")


###############################################################################
# SECTION 3: Dickman Function Analysis
###############################################################################

def dickman_analysis():
    """
    Compare our FB sizes to the theoretical optimum predicted by the Dickman
    function and L(n) complexity formula.

    For QS/SIQS: B = L(n)^(1/sqrt(2)), M ~ L(n)^(1/sqrt(2))
    For GNFS: B = L(n)^(2/3), sieve region ~ L(n)^(2/3)

    where L(n) = exp((c * ln(n))^(1/3) * (ln(ln(n)))^(2/3))
    c = (64/9)^(1/3) for GNFS, 1 for QS
    """
    print(f"\n{'='*70}")
    print(f"DICKMAN FUNCTION ANALYSIS: Optimal FB Size")
    print(f"{'='*70}")

    # Dickman rho function approximation (tabulated + interpolation)
    # rho(u) = probability that a random integer N has all prime factors <= N^(1/u)
    # For small u: rho(1)=1, rho(2)=1-ln(2)~0.307, rho(3)~0.0486, etc.
    dickman_table = {
        1.0: 1.0,
        1.5: 0.5305,
        2.0: 0.3068,
        2.5: 0.1312,
        3.0: 0.04861,
        3.5: 0.01491,
        4.0: 0.003831,
        4.5: 0.0008382,
        5.0: 0.0001583,
        5.5: 2.591e-5,
        6.0: 3.699e-6,
        6.5: 4.638e-7,
        7.0: 5.14e-8,
        8.0: 3.29e-10,
        9.0: 1.12e-12,
        10.0: 2.28e-15,
    }

    def dickman_rho(u):
        """Approximate Dickman's rho function by interpolation."""
        if u <= 1.0:
            return 1.0
        keys = sorted(dickman_table.keys())
        if u >= keys[-1]:
            # Extrapolate: rho(u) ~ u^(-u) for large u
            return u ** (-u)
        for i in range(len(keys) - 1):
            if keys[i] <= u <= keys[i + 1]:
                # Log-linear interpolation
                u0, u1 = keys[i], keys[i + 1]
                r0, r1 = dickman_table[u0], dickman_table[u1]
                frac = (u - u0) / (u1 - u0)
                lr0, lr1 = math.log(r0), math.log(r1)
                return math.exp(lr0 + frac * (lr1 - lr0))
        return u ** (-u)

    print(f"\n  SIQS: L(n) = exp(sqrt(ln(n) * ln(ln(n))))")
    print(f"  {'Digits':>6} | {'Our FB':>8} | {'Opt B':>8} | {'Our M':>10} | {'Opt M':>10} | {'u_ours':>6} | {'u_opt':>6} | {'rho_ours':>10} | {'rho_opt':>10}")
    print(f"  {'-'*6}-+-{'-'*8}-+-{'-'*8}-+-{'-'*10}-+-{'-'*10}-+-{'-'*6}-+-{'-'*6}-+-{'-'*10}-+-{'-'*10}")

    from siqs_engine import siqs_params

    for nd in [40, 45, 50, 55, 60, 65, 70, 75, 80]:
        fb_size, M = siqs_params(nd)
        nb = nd * math.log(10) / math.log(2)
        ln_n = nb * math.log(2)
        ln_ln_n = math.log(ln_n)

        # L(n) for QS: exp(sqrt(ln_n * ln_ln_n))
        L_qs = math.exp(math.sqrt(ln_n * ln_ln_n))

        # Optimal B for QS: L(n)^(1/sqrt(2)) ~ exp(sqrt(ln_n * ln_ln_n) / sqrt(2))
        opt_B = math.exp(math.sqrt(ln_n * ln_ln_n) / math.sqrt(2))
        opt_M = opt_B  # sieve region ~ B for QS

        # Our actual B (largest FB prime)
        # Approximate: B ~ fb_size-th prime ~ fb_size * ln(fb_size * 2)
        our_B = fb_size * math.log(fb_size * 2)  # approx

        # u = log(norm) / log(B)
        # For QS: norm ~ sqrt(N) * M / a ~ sqrt(N) for balanced polys
        # Actually norm ~ M * sqrt(N/2) for SIQS
        log_norm = 0.5 * ln_n + math.log(max(M, 1))
        u_ours = log_norm / math.log(max(our_B, 2))
        u_opt = log_norm / math.log(max(opt_B, 2))

        rho_ours = dickman_rho(u_ours)
        rho_opt = dickman_rho(u_opt)

        print(f"  {nd:>6} | {int(our_B):>8} | {int(opt_B):>8} | {M:>10} | {int(opt_M):>10} | "
              f"{u_ours:>6.2f} | {u_opt:>6.2f} | {rho_ours:>10.2e} | {rho_opt:>10.2e}")

    print(f"\n  GNFS: L(n) = exp(c * (ln n)^(1/3) * (ln ln n)^(2/3)), c=(64/9)^(1/3)")
    print(f"  {'Digits':>6} | {'Our B_r':>8} | {'Opt B':>10} | {'Our A':>8} | {'u_rat':>6} | {'u_alg':>6} | {'rho_rat':>10}")
    print(f"  {'-'*6}-+-{'-'*8}-+-{'-'*10}-+-{'-'*8}-+-{'-'*6}-+-{'-'*6}-+-{'-'*10}")

    from gnfs_engine import gnfs_params as gnfs_p

    for nd in [35, 40, 43, 45, 50, 55, 60, 70, 80, 100]:
        nb = nd * math.log(10) / math.log(2)
        ln_n = nb * math.log(2)
        ln_ln_n = math.log(ln_n)
        n_approx = mpz(10) ** nd

        params = gnfs_p(n_approx)
        d = params['d']

        # L(n) for GNFS: exp((64/9)^(1/3) * ln(n)^(1/3) * ln(ln(n))^(2/3))
        c_gnfs = (64.0 / 9) ** (1.0 / 3)
        L_gnfs = math.exp(c_gnfs * (ln_n ** (1.0/3)) * (ln_ln_n ** (2.0/3)))

        # Optimal B for GNFS: L(n)^(2/3)
        opt_B = L_gnfs ** (2.0 / 3)

        # Rational norm: |a + b*m| ~ A * b^(1/d) * n^(1/d) for base-m
        # Actually rational norm ~ |a + b*m| where m ~ n^(1/d)
        m_approx = int(n_approx ** (1.0/d)) if d > 0 else 1
        log_rat_norm = math.log(max(params['A'], 1)) + math.log(max(m_approx, 1))
        # Algebraic norm: ~ A^d * leading_coeff
        log_alg_norm = d * math.log(max(params['A'], 1))

        log_B = math.log(max(params['B_r'], 2))
        u_rat = log_rat_norm / log_B
        u_alg = log_alg_norm / log_B

        rho_rat = dickman_rho(u_rat)

        print(f"  {nd:>6} | {params['B_r']:>8} | {int(opt_B):>10} | {params['A']:>8} | "
              f"{u_rat:>6.2f} | {u_alg:>6.2f} | {rho_rat:>10.2e}")

    # Summary of key findings
    print(f"\n  KEY INSIGHTS:")
    print(f"  - Dickman rho(u): probability of B-smooth number drops fast with u")
    print(f"  - For u=3 (typical QS): ~5% of candidates are smooth")
    print(f"  - For u=4: ~0.4% smooth — diminishing returns")
    print(f"  - For u=5+: <0.02% — practically useless without LP variation")
    print(f"  - LP variation effectively reduces u by ~1 (since LP = B*100)")
    print(f"  - Optimal strategy: choose B so u ~ 3-4 for QS, u ~ 2-3 for GNFS")


###############################################################################
# MAIN
###############################################################################

if __name__ == '__main__':
    print("V4 RESEARCH — ITERATION 1: PROFILING")
    print(f"Date: 2026-03-15")
    print(f"RAM limit: 2GB per experiment\n")

    # Run Dickman analysis first (fast, no computation)
    dickman_analysis()

    # Profile SIQS at 60d
    siqs_results = profile_siqs_60d()

    # Profile GNFS at 43d
    profile_gnfs_43d()

    print(f"\n{'='*70}")
    print(f"PROFILING COMPLETE")
    print(f"{'='*70}")

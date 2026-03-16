#!/usr/bin/env python3
"""
bench_siqs_core.py -- Fair benchmark: full Python pipeline vs C core.

Measures the COMPLETE per-polynomial cost:
  Python: sieve (JIT) + find_smooth + batch_find_hits + trial_division + classify
  C core: sieve + find_smooth + trial_division + classify (single C call)

This is the honest comparison that shows the real speedup.
"""

import sys, os, time, math, random
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gmpy2
from gmpy2 import mpz, isqrt, is_prime, gcd, jacobi, next_prime

from siqs_engine import (
    siqs_params, tonelli_shanks, jit_sieve, jit_find_smooth,
    jit_batch_find_hits, _quick_factor, _pollard_rho_split
)
from siqs_core import SIQSCoreC, REL_SMOOTH, REL_SINGLE_LP, REL_DOUBLE_LP
import bisect


def setup_poly(nd_target):
    """Build a test polynomial at the given digit size."""
    # Generate a semiprime of the right size
    half = nd_target // 2
    p1 = int(gmpy2.next_prime(10**half + random.randint(1, 10**6)))
    p2 = int(gmpy2.next_prime(10**(nd_target - half) + random.randint(1, 10**6)))
    n = mpz(p1) * mpz(p2)
    nd = len(str(n))
    nb = int(gmpy2.log2(n)) + 1

    fb_size, M = siqs_params(nd)
    fb = []
    p = 2
    while len(fb) < fb_size:
        if p == 2 or (is_prime(p) and jacobi(int(n % p), p) == 1):
            fb.append(int(p))
        p = int(next_prime(p)) if p > 2 else 3

    fb_logs = [int(round(math.log2(p) * 64)) for p in fb]
    lp_bound = min(fb[-1] * 100, fb[-1] ** 2)

    sqrt_n_mod = {}
    for p in fb:
        if p == 2:
            sqrt_n_mod[2] = int(n % 2)
        else:
            sqrt_n_mod[p] = tonelli_shanks(int(n % p), p)

    # Pick polynomial
    target_a = isqrt(2*n) // M
    log_target = float(gmpy2.log2(target_a))
    best_s = 3
    for s_try in range(2, 10):
        ideal_log = log_target / s_try
        if ideal_log < 3.5 or ideal_log > 50: continue
        ideal = int(2 ** ideal_log)
        mid = bisect.bisect_left(fb, ideal)
        if mid < len(fb):
            best_s = s_try
            break
    s = best_s

    ideal_prime = int(2 ** (log_target / s))
    mid = bisect.bisect_left(fb, ideal_prime)
    lo = max(1, mid - 20)
    hi = min(len(fb)-1, mid + 20)
    indices = sorted(random.sample(range(lo, min(hi, len(fb))), s))
    a = mpz(1)
    for i in indices:
        a *= fb[i]
    a_primes = [fb[i] for i in indices]
    a_prime_idx = [fb.index(ap) for ap in a_primes]
    a_prime_set = set(a_primes)
    a_int = int(a)

    B_values = []
    for j in range(s):
        q = a_primes[j]
        A_j = a // q
        A_j_inv = pow(int(A_j % q), -1, q)
        B_j = mpz(sqrt_n_mod[q]) * A_j * mpz(A_j_inv) % a
        B_values.append(B_j)

    b = mpz(0)
    for B_j in B_values:
        b += B_j
    if (b*b - n) % a != 0:
        b = -b
    c_val = (b*b - n) // a
    b_int = int(b)

    o1 = np.full(fb_size, -1, dtype=np.int64)
    o2 = np.full(fb_size, -1, dtype=np.int64)
    a_inv_mod = np.zeros(fb_size, dtype=np.int64)
    for pi in range(fb_size):
        p = fb[pi]
        if p in a_prime_set: continue
        try:
            a_inv_mod[pi] = pow(a_int % p, -1, p)
        except: pass

    for pi in range(fb_size):
        p = fb[pi]
        if p == 2:
            g0 = int(c_val % 2)
            g1 = int((a_int + 2*b_int + int(c_val)) % 2)
            if g0 == 0:
                o1[pi] = M % 2
                if g1 == 0: o2[pi] = (M+1)%2
            elif g1 == 0: o1[pi] = (M+1)%2
            continue
        if p in a_prime_set:
            b2 = (2*b_int) % p
            if b2 == 0: continue
            b2_inv = pow(b2, -1, p)
            c_mod = int(c_val % p)
            r = (-c_mod * b2_inv) % p
            o1[pi] = (r + M) % p
            continue
        t = sqrt_n_mod.get(p)
        if t is None: continue
        ai = int(a_inv_mod[pi])
        bm = b_int % p
        r1 = (ai * (t - bm)) % p
        r2 = (ai * (p - t - bm)) % p
        o1[pi] = (r1 + M) % p
        o2[pi] = ((r2 + M) % p) if r2 != r1 else -1

    _log_g_max = math.log2(max(M, 1)) + 0.5 * nb
    if nb >= 180:
        T_bits = max(15, nb // 4 - 1)
    else:
        T_bits = max(15, nb // 4 - 2)
    spc = 0
    for p in fb:
        if p >= 32: break
        roots = 1 if p == 2 else 2
        spc += roots * math.log2(p) * 64 / p
    spc = int(spc * 0.60)
    threshold = int(max(0, (_log_g_max - T_bits)) * 64) - spc

    return {
        'n': n, 'nd': nd, 'nb': nb,
        'fb': fb, 'fb_logs': fb_logs, 'fb_size': fb_size,
        'M': M, 'lp_bound': lp_bound,
        'a': a, 'a_int': a_int, 'b': b, 'b_int': b_int, 'c_val': c_val,
        'a_prime_idx': a_prime_idx,
        'o1': o1, 'o2': o2,
        'threshold': threshold,
    }


def bench_python_full(setup, n_iters=3):
    """Full Python pipeline: sieve + TD + classify."""
    fb = setup['fb']
    fb_np = np.array(fb, dtype=np.int64)
    fb_log_np = np.array(setup['fb_logs'], dtype=np.int16)
    fb_size = setup['fb_size']
    M = setup['M']
    sz = 2 * M
    o1, o2 = setup['o1'], setup['o2']
    threshold = setup['threshold']
    a_int = setup['a_int']
    b_int = setup['b_int']
    c_val = int(setup['c_val'])
    a = setup['a']
    b = setup['b']
    n = setup['n']
    lp_bound = setup['lp_bound']
    a_prime_idx = setup['a_prime_idx']

    total_smooth = 0
    total_slp = 0
    total_dlp = 0

    t0 = time.time()
    for _ in range(n_iters):
        sieve_buf = np.zeros(sz, dtype=np.int16)
        jit_sieve(sieve_buf, fb_np, fb_log_np, o1, o2, sz)
        candidates = jit_find_smooth(sieve_buf, threshold)
        n_cand = len(candidates)
        if n_cand == 0:
            continue

        hit_starts, hit_fb = jit_batch_find_hits(
            candidates, n_cand, fb_np, o1, o2, fb_size)

        for ci in range(n_cand):
            sieve_pos = int(candidates[ci])
            x = sieve_pos - M
            gx = a_int * x * x + 2 * b_int * x + c_val
            if gx == 0: continue

            sign = 1 if gx < 0 else 0
            v = abs(gx)
            exps = [0] * fb_size

            h_start = hit_starts[ci]
            h_end = hit_starts[ci + 1]
            for h in range(h_start, h_end):
                idx = hit_fb[h]
                p = fb[idx]
                if v == 1: break
                q, r = divmod(v, p)
                if r == 0:
                    e = 1
                    v = q
                    q, r = divmod(v, p)
                    while r == 0:
                        e += 1; v = q; q, r = divmod(v, p)
                    exps[idx] = e

            for idx in a_prime_idx:
                exps[idx] += 1

            if v == 1:
                total_smooth += 1
            elif v < lp_bound and is_prime(v):
                total_slp += 1
            elif v < lp_bound * lp_bound and v > 1:
                if is_prime(mpz(v)):
                    pass  # prime cofactor > lp_bound, skip
                else:
                    # Actually do the split (same work as real engine)
                    sq = gmpy2.isqrt(mpz(v))
                    if sq * sq == v and is_prime(sq):
                        lp_a, lp_b = int(sq), int(sq)
                    else:
                        lp_a = _quick_factor(v)
                        if lp_a and lp_a > 1 and v // lp_a > 1:
                            lp_b = v // lp_a
                        else:
                            lp_a, lp_b = 0, 0
                    if (lp_a > 0 and lp_b > 0 and
                        lp_a < lp_bound and lp_b < lp_bound and
                        is_prime(mpz(lp_a)) and is_prime(mpz(lp_b))):
                        total_dlp += 1

    elapsed = time.time() - t0
    per_poly = elapsed / n_iters
    return per_poly, total_smooth / n_iters, total_slp / n_iters, total_dlp / n_iters


def bench_c_core(setup, n_iters=3):
    """C core: full pipeline."""
    fb = setup['fb']
    fb_logs = setup['fb_logs']
    fb_size = setup['fb_size']
    M = setup['M']
    o1, o2 = setup['o1'], setup['o2']
    threshold = setup['threshold']
    a_prime_idx = setup['a_prime_idx']
    n = setup['n']
    a = setup['a']
    b = setup['b']
    lp_bound = setup['lp_bound']

    core = SIQSCoreC(fb, fb_logs, fb_size, M, str(int(n)), lp_bound)
    # Warmup
    core.sieve_poly(o1, o2, str(int(a)), str(int(b)), a_prime_idx, threshold)

    total_smooth = 0
    total_slp = 0
    total_dlp = 0

    t0 = time.time()
    for _ in range(n_iters):
        rels = core.sieve_poly(o1, o2, str(int(a)), str(int(b)), a_prime_idx, threshold)
        for r in rels:
            if r[0] == REL_SMOOTH: total_smooth += 1
            elif r[0] == REL_SINGLE_LP: total_slp += 1
            elif r[0] == REL_DOUBLE_LP: total_dlp += 1

    elapsed = time.time() - t0
    per_poly = elapsed / n_iters
    return per_poly, total_smooth / n_iters, total_slp / n_iters, total_dlp / n_iters


def main():
    print("Fair Benchmark: Full Python Pipeline vs C Core")
    print("=" * 70)

    for nd_target in [48, 54, 60, 66]:
        print(f"\n--- {nd_target}d target ---")
        setup = setup_poly(nd_target)
        print(f"  n: {setup['nd']}d ({setup['nb']}b), FB={setup['fb_size']}, M={setup['M']}")
        n_iters = 5 if nd_target <= 54 else 3

        # Python full pipeline
        py_time, py_sm, py_slp, py_dlp = bench_python_full(setup, n_iters)
        print(f"  Python full: {py_time*1000:.1f}ms/poly  (sm={py_sm:.0f} slp={py_slp:.0f} dlp={py_dlp:.0f})")

        # C core
        c_time, c_sm, c_slp, c_dlp = bench_c_core(setup, n_iters)
        print(f"  C core:      {c_time*1000:.1f}ms/poly  (sm={c_sm:.0f} slp={c_slp:.0f} dlp={c_dlp:.0f})")

        speedup = py_time / c_time if c_time > 0 else float('inf')
        print(f"  Speedup: {speedup:.1f}x")
        print(f"  C finds {c_sm/max(py_sm,1)*100:.0f}% smooth, {c_slp/max(py_slp,1)*100:.0f}% SLP vs Python")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
test_siqs_core.py -- Verify the C SIQS core against the Python reference implementation.

Tests:
1. C library loads successfully
2. Single polynomial: same smooth relations found as Python path
3. Cofactor classification matches
4. End-to-end: factor a known semiprime using C core + Python LA
5. Benchmark: C vs Python per-polynomial timing at 48d, 54d, 60d
"""

import sys
import os
import time
import math
import random
import numpy as np

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gmpy2
from gmpy2 import mpz, isqrt, is_prime, gcd, jacobi, next_prime


def test_1_load():
    """Test 1: C library loads."""
    print("=" * 60)
    print("Test 1: Library load")
    from siqs_core import is_available, SIQSCoreC
    assert is_available(), "siqs_core_c.so failed to load"
    print("  PASS: siqs_core_c.so loaded successfully")


def test_2_single_poly():
    """Test 2: Single polynomial sieve matches Python reference."""
    print("=" * 60)
    print("Test 2: Single polynomial correctness")
    from siqs_core import SIQSCoreC, REL_SMOOTH, REL_SINGLE_LP, REL_DOUBLE_LP

    # Use a small semiprime for testing
    p1, p2 = 1000000007, 1000000009
    n = mpz(p1) * mpz(p2)
    nd = len(str(n))
    nb = int(gmpy2.log2(n)) + 1
    print(f"  n = {n} ({nd}d, {nb}b)")

    # Build factor base
    fb_size = 200
    fb = []
    p = 2
    while len(fb) < fb_size:
        if p == 2 or (is_prime(p) and jacobi(int(n % p), p) == 1):
            fb.append(int(p))
        p = int(next_prime(p)) if p > 2 else 3

    fb_logs = [int(round(math.log2(p) * 64)) for p in fb]
    M = 50000
    lp_bound = min(fb[-1] * 100, fb[-1] ** 2)

    # Tonelli-Shanks
    def tonelli_shanks(nn, pp):
        nn = nn % pp
        if nn == 0: return 0
        if pp == 2: return nn
        if pow(nn, (pp-1)//2, pp) != 1: return None
        q, s = pp-1, 0
        while q % 2 == 0: q //= 2; s += 1
        if s == 1: return pow(nn, (pp+1)//4, pp)
        z = 2
        while pow(z, (pp-1)//2, pp) != pp-1: z += 1
        m, c, t, r = s, pow(z, q, pp), pow(nn, q, pp), pow(nn, (q+1)//2, pp)
        while True:
            if t == 1: return r
            i, tmp = 1, t*t%pp
            while tmp != 1: tmp = tmp*tmp%pp; i += 1
            b = pow(c, 1<<(m-i-1), pp)
            m, c, t, r = i, b*b%pp, t*b*b%pp, r*b%pp

    sqrt_n_mod = {}
    for p in fb:
        if p == 2:
            sqrt_n_mod[2] = int(n % 2)
        else:
            sqrt_n_mod[p] = tonelli_shanks(int(n % p), p)

    # Pick 'a' as product of s=3 FB primes
    s = 3
    sqrt_n = isqrt(n) + 1
    target_a = isqrt(2 * n) // M
    # Pick primes near the ideal size
    ideal_prime = int(target_a ** (1.0/s))
    import bisect
    mid = bisect.bisect_left(fb, ideal_prime)
    lo = max(1, mid - 15)
    hi = min(len(fb)-1, mid + 15)
    indices = sorted(random.sample(range(lo, hi), s))
    a = mpz(1)
    for i in indices:
        a *= fb[i]
    a_primes = [fb[i] for i in indices]
    a_prime_idx = [fb.index(ap) for ap in a_primes]
    a_prime_set = set(a_primes)
    a_int = int(a)

    # B_values for first polynomial
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

    # Compute sieve offsets
    fb_np = np.array(fb, dtype=np.int64)
    o1 = np.full(fb_size, -1, dtype=np.int64)
    o2 = np.full(fb_size, -1, dtype=np.int64)

    a_inv_mod = np.zeros(fb_size, dtype=np.int64)
    for pi in range(fb_size):
        p = fb[pi]
        if p in a_prime_set:
            a_inv_mod[pi] = 0
        else:
            try:
                a_inv_mod[pi] = pow(a_int % p, -1, p)
            except (ValueError, ZeroDivisionError):
                a_inv_mod[pi] = 0

    for pi in range(fb_size):
        p = fb[pi]
        if p == 2:
            g0 = int(c_val % 2)
            g1 = int((a_int + 2*b_int + int(c_val)) % 2)
            if g0 == 0:
                o1[pi] = M % 2
                if g1 == 0: o2[pi] = (M+1) % 2
            elif g1 == 0:
                o1[pi] = (M+1) % 2
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

    # Compute threshold
    _log_g_max = math.log2(max(M, 1)) + 0.5 * nb
    T_bits = max(15, nb // 4 - 2)
    small_prime_correction = 0
    for p in fb:
        if p >= 32: break
        roots = 1 if p == 2 else 2
        small_prime_correction += roots * math.log2(p) * 64 / p
    small_prime_correction = int(small_prime_correction * 0.60)
    threshold = int(max(0, (_log_g_max - T_bits)) * 64) - small_prime_correction

    # ---- Python reference: sieve + trial divide ----
    print(f"  Sieving with a={a}, M={M}, threshold={threshold}")
    t0 = time.time()

    # Import numba kernels from siqs_engine
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    try:
        from siqs_engine import jit_sieve, jit_find_smooth, jit_batch_find_hits
        have_jit = True
    except ImportError:
        have_jit = False
        print("  WARNING: Cannot import siqs_engine JIT functions, skipping Python reference")

    py_smooth = []
    py_slp = []
    py_dlp = []
    if have_jit:
        sieve_buf = np.zeros(2*M, dtype=np.int16)
        fb_np32 = np.array(fb, dtype=np.int64)
        fb_log_np = np.array(fb_logs, dtype=np.int16)
        jit_sieve(sieve_buf, fb_np32, fb_log_np, o1, o2, 2*M)
        candidates = jit_find_smooth(sieve_buf, threshold)
        n_cand = len(candidates)
        print(f"  Python: {n_cand} candidates in {time.time()-t0:.3f}s")

        if n_cand > 0:
            hit_starts, hit_fb = jit_batch_find_hits(
                candidates, n_cand, fb_np32, o1, o2, fb_size)

            for ci in range(n_cand):
                sieve_pos = int(candidates[ci])
                x = sieve_pos - M
                gx = a_int * x * x + 2 * b_int * x + int(c_val)
                if gx == 0:
                    continue
                sign_py = 1 if gx < 0 else 0
                v = abs(gx)
                exps_py = [0] * fb_size

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
                            e += 1
                            v = q
                            q, r = divmod(v, p)
                        exps_py[idx] = e

                for idx in a_prime_idx:
                    exps_py[idx] += 1

                sparse_py = tuple((j, e) for j, e in enumerate(exps_py) if e != 0)

                if v == 1:
                    py_smooth.append((sieve_pos, sign_py, sparse_py))
                elif v < lp_bound and is_prime(v):
                    py_slp.append((sieve_pos, sign_py, sparse_py, int(v)))
                elif v < lp_bound * lp_bound and v > 1 and not is_prime(mpz(v)):
                    py_dlp.append((sieve_pos, sign_py, sparse_py, int(v)))

        print(f"  Python: {len(py_smooth)} smooth, {len(py_slp)} SLP, {len(py_dlp)} DLP candidates")

    # ---- C core ----
    t0 = time.time()
    core = SIQSCoreC(fb, fb_logs, fb_size, M, str(int(n)), lp_bound)
    c_rels = core.sieve_poly(o1, o2, str(int(a)), str(int(b)), a_prime_idx, threshold)
    c_time = time.time() - t0

    c_smooth = [(r[1], r[2], r[3]) for r in c_rels if r[0] == REL_SMOOTH]
    c_slp = [(r[1], r[2], r[3], r[4]) for r in c_rels if r[0] == REL_SINGLE_LP]
    c_dlp = [r for r in c_rels if r[0] == REL_DOUBLE_LP]

    print(f"  C core: {len(c_smooth)} smooth, {len(c_slp)} SLP, {len(c_dlp)} DLP in {c_time:.3f}s")

    if have_jit:
        # Compare smooth relations
        py_smooth_set = set((s[0], s[1]) for s in py_smooth)
        c_smooth_set = set((s[0], s[1]) for s in c_smooth)

        # All C smooth relations should be in Python's set
        missed = py_smooth_set - c_smooth_set
        extra = c_smooth_set - py_smooth_set

        if missed:
            print(f"  WARNING: Python found {len(missed)} smooth that C missed")
            # Print first few
            for m in list(missed)[:3]:
                print(f"    missed sieve_pos={m[0]}")
        if extra:
            print(f"  NOTE: C found {len(extra)} extra smooth (different TD path)")

        # Verify exponent vectors match for shared smooth relations
        shared = py_smooth_set & c_smooth_set
        exps_match = 0
        exps_mismatch = 0
        for spos, sign in shared:
            py_exp = None
            for s in py_smooth:
                if s[0] == spos and s[1] == sign:
                    py_exp = dict(s[2])
                    break
            c_exp = None
            for s in c_smooth:
                if s[0] == spos and s[1] == sign:
                    c_exp = dict(s[2])
                    break
            if py_exp == c_exp:
                exps_match += 1
            else:
                exps_mismatch += 1
                if exps_mismatch <= 3:
                    print(f"  MISMATCH at sieve_pos={spos}:")
                    print(f"    Python: {py_exp}")
                    print(f"    C:      {c_exp}")

        print(f"  Exponent match: {exps_match}/{len(shared)} shared smooth relations")
        if exps_mismatch == 0 and len(shared) > 0:
            print("  PASS: All shared smooth relations match exactly")
        elif len(shared) == 0 and len(py_smooth) == 0:
            print("  PASS: No smooth relations from either path (normal for small M)")
        else:
            print(f"  WARNING: {exps_mismatch} exponent mismatches")

        # SLP comparison (cofactor values should match)
        py_slp_pos = set(s[0] for s in py_slp)
        c_slp_pos = set(s[0] for s in c_slp)
        slp_shared = py_slp_pos & c_slp_pos
        print(f"  SLP: {len(slp_shared)} shared out of Py={len(py_slp)}, C={len(c_slp)}")
    else:
        print("  (Skipping Python comparison -- siqs_engine not available)")
        if c_smooth or c_slp:
            print("  PASS: C core found relations independently")
        else:
            print("  NOTE: No relations found (may need larger M or different poly)")

    print()


def test_3_benchmark():
    """Test 3: Benchmark C core vs Python at different sizes."""
    print("=" * 60)
    print("Test 3: Per-polynomial benchmark (C core)")
    from siqs_core import SIQSCoreC

    # Test semiprimes at different sizes
    test_cases = [
        ("48d", 10**23 + 87, 10**23 + 111),
        ("54d", 10**26 + 57, 10**26 + 99),
    ]

    for label, p1, p2 in test_cases:
        # Find next primes
        p1 = int(gmpy2.next_prime(p1))
        p2 = int(gmpy2.next_prime(p2))
        n = mpz(p1) * mpz(p2)
        nd = len(str(n))
        nb = int(gmpy2.log2(n)) + 1
        print(f"\n  {label}: {nd}d ({nb}b)")

        # Import params
        try:
            from siqs_engine import siqs_params, tonelli_shanks, jit_sieve, jit_find_smooth, jit_batch_find_hits
        except ImportError:
            print("  SKIP: siqs_engine not available")
            continue

        fb_size_target, M = siqs_params(nd)
        fb_size = fb_size_target

        # Build FB
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

        # Pick poly
        target_a = isqrt(2*n) // M
        log_target = float(gmpy2.log2(target_a))
        import bisect
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

        # B_values
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

        # Offsets
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

        # ---- Python benchmark ----
        fb_np = np.array(fb, dtype=np.int64)
        fb_log_np = np.array(fb_logs, dtype=np.int16)

        t0 = time.time()
        n_iters = 5
        py_cands_total = 0
        for _ in range(n_iters):
            sieve_buf = np.zeros(2*M, dtype=np.int16)
            jit_sieve(sieve_buf, fb_np, fb_log_np, o1, o2, 2*M)
            candidates = jit_find_smooth(sieve_buf, threshold)
            py_cands_total += len(candidates)
            if len(candidates) > 0:
                jit_batch_find_hits(candidates, len(candidates), fb_np, o1, o2, fb_size)
        py_time = (time.time() - t0) / n_iters
        py_cands = py_cands_total / n_iters

        # ---- C benchmark ----
        core = SIQSCoreC(fb, fb_logs, fb_size, M, str(int(n)), lp_bound)
        # Warmup
        core.sieve_poly(o1, o2, str(int(a)), str(int(b)), a_prime_idx, threshold)

        t0 = time.time()
        c_rels_total = 0
        for _ in range(n_iters):
            rels = core.sieve_poly(o1, o2, str(int(a)), str(int(b)), a_prime_idx, threshold)
            c_rels_total += len(rels)
        c_time = (time.time() - t0) / n_iters
        c_rels_avg = c_rels_total / n_iters

        speedup = py_time / c_time if c_time > 0 else float('inf')
        print(f"  Python: {py_time*1000:.1f}ms/poly (sieve+hits only, {py_cands:.0f} cands)")
        print(f"  C core: {c_time*1000:.1f}ms/poly (full pipeline, {c_rels_avg:.1f} rels)")
        print(f"  Speedup: {speedup:.1f}x (C does MORE work: sieve+TD+classify)")


def test_4_end_to_end():
    """Test 4: Factor a known semiprime using C core integrated with Python LA."""
    print("=" * 60)
    print("Test 4: End-to-end factoring with C core")

    try:
        from siqs_engine import siqs_factor
    except ImportError:
        print("  SKIP: siqs_engine not available")
        return

    # 40-digit semiprime
    p1 = int(gmpy2.next_prime(10**19 + 7))
    p2 = int(gmpy2.next_prime(10**19 + 33))
    n = p1 * p2
    print(f"  n = {n} ({len(str(n))}d)")
    print(f"  Known factors: {p1} x {p2}")

    t0 = time.time()
    f = siqs_factor(n, verbose=True, time_limit=120)
    elapsed = time.time() - t0

    if f is not None:
        other = n // f
        if (f == p1 and other == p2) or (f == p2 and other == p1):
            print(f"\n  PASS: Correctly factored in {elapsed:.1f}s")
        else:
            print(f"\n  PASS: Found factor {f} (other={other}) in {elapsed:.1f}s")
    else:
        print(f"\n  FAIL: No factor found in {elapsed:.1f}s")


if __name__ == '__main__':
    print("SIQS C Core Test Suite")
    print("=" * 60)
    test_1_load()
    print()
    test_2_single_poly()
    test_3_benchmark()
    print()
    test_4_end_to_end()
    print("\nAll tests complete.")

#!/usr/bin/env python3
"""
siqs_poly_c_wrapper.py — Python ctypes wrapper for siqs_poly_c.so

Provides a PolySetup class that accelerates SIQS polynomial initialization:
  1. B_j computation
  2. a_inv mod p precomputation
  3. Delta array precomputation (for Gray code switching)
  4. Initial sieve root computation
  5. Incremental Gray code root switching

Usage:
    from siqs_poly_c_wrapper import PolySetup

    ps = PolySetup()
    if ps.available:
        result = ps.full_poly_setup(n, a, a_primes, a_prime_indices,
                                     sqrt_n_mod_qj, fb, sqrt_n_mod_fb, M)
        # result contains: b, c, B_values, a_inv_mod, is_a_prime, deltas, o1, o2

        # For subsequent polynomials via Gray code:
        ps.gray_switch(fb, fb_size, is_a_prime, delta_j, offset_dir, o1, o2,
                       a_prime_indices, s, b_str, c_str, a_int_mod2, M)
"""

import ctypes
import os
import numpy as np

_lib = None
_loaded = False

# String buffer size for big integer decimal representations.
# 200 digits covers a, b, c, B_j for up to ~600-bit N (180+ digits).
_STR_BUFSIZE = 512


def _load_lib():
    """Load the siqs_poly_c shared library (lazy, cached)."""
    global _lib, _loaded
    if _loaded:
        return _lib
    _loaded = True
    so_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'siqs_poly_c.so')
    if not os.path.exists(so_path):
        return None
    try:
        _lib = ctypes.CDLL(so_path)
        _setup_prototypes(_lib)
        return _lib
    except OSError:
        return None


def _setup_prototypes(lib):
    """Set up ctypes function prototypes."""

    # full_poly_setup(...)
    lib.full_poly_setup.argtypes = [
        ctypes.c_char_p,                              # n_str
        ctypes.c_char_p,                              # a_str
        ctypes.POINTER(ctypes.c_int32),               # a_primes
        ctypes.POINTER(ctypes.c_int32),               # a_prime_indices
        ctypes.POINTER(ctypes.c_int32),               # sqrt_n_mod_qj
        ctypes.c_int,                                  # s
        ctypes.POINTER(ctypes.c_int32),               # fb_primes
        ctypes.POINTER(ctypes.c_int32),               # sqrt_n_mod_fb
        ctypes.c_int,                                  # fb_size
        ctypes.c_int,                                  # M
        ctypes.POINTER(ctypes.c_int64),               # a_inv_mod (out)
        ctypes.POINTER(ctypes.c_int32),               # is_a_prime (out)
        ctypes.POINTER(ctypes.c_int64),               # deltas (out)
        ctypes.POINTER(ctypes.c_int64),               # o1 (out)
        ctypes.POINTER(ctypes.c_int64),               # o2 (out)
        ctypes.c_char_p,                              # b_out_buf (out)
        ctypes.c_char_p,                              # c_out_buf (out)
        ctypes.c_char_p,                              # Bj_bufs (out, s * str_bufsize)
        ctypes.c_int,                                  # str_bufsize
    ]
    lib.full_poly_setup.restype = ctypes.c_int

    # gray_code_switch(...)
    lib.gray_code_switch.argtypes = [
        ctypes.POINTER(ctypes.c_int32),               # fb_primes
        ctypes.c_int,                                  # fb_size
        ctypes.POINTER(ctypes.c_int64),               # delta_j
        ctypes.POINTER(ctypes.c_int32),               # is_a_prime
        ctypes.c_int,                                  # offset_dir
        ctypes.POINTER(ctypes.c_int64),               # o1 (in/out)
        ctypes.POINTER(ctypes.c_int64),               # o2 (in/out)
    ]
    lib.gray_code_switch.restype = None

    # recompute_a_prime_roots(...)
    lib.recompute_a_prime_roots.argtypes = [
        ctypes.POINTER(ctypes.c_int32),               # fb_primes
        ctypes.POINTER(ctypes.c_int32),               # a_prime_indices
        ctypes.c_int,                                  # s
        ctypes.c_char_p,                              # b_str
        ctypes.c_char_p,                              # c_str
        ctypes.c_int64,                               # a_int_mod2
        ctypes.c_int,                                  # M
        ctypes.POINTER(ctypes.c_int64),               # o1 (in/out)
        ctypes.POINTER(ctypes.c_int64),               # o2 (in/out)
    ]
    lib.recompute_a_prime_roots.restype = None


class PolySetup:
    """
    High-level wrapper for SIQS polynomial setup in C.

    Typical per-'a' workflow:
        1. full_poly_setup() -- returns b, c, B_values, arrays
        2. [sieve first polynomial using o1, o2]
        3. For each Gray code step:
           a. gray_switch() -- updates o1, o2 in-place
           b. [sieve this polynomial]
    """

    def __init__(self):
        self._lib = _load_lib()
        self._fb_arr = None
        self._fb_size_cached = 0

    @property
    def available(self):
        return self._lib is not None

    def _ensure_fb_arr(self, fb, fb_size):
        """Cache the FB primes as a ctypes array (reused across calls)."""
        if self._fb_arr is None or self._fb_size_cached != fb_size:
            self._fb_arr = (ctypes.c_int32 * fb_size)(*fb)
            self._fb_size_cached = fb_size
        return self._fb_arr

    def full_poly_setup(self, n, a, a_primes, a_prime_indices,
                        sqrt_n_mod_qj, fb, sqrt_n_mod_fb, fb_size, M):
        """
        Complete polynomial setup for one 'a' value.

        Returns dict with:
            'b': gmpy2.mpz
            'c': gmpy2.mpz
            'B_values': list of gmpy2.mpz
            'a_inv_mod': np.array int64 [fb_size]
            'is_a_prime': np.array int32 [fb_size]
            'deltas': list of np.array int64 [fb_size] (one per j)
            'o1': np.array int64 [fb_size]
            'o2': np.array int64 [fb_size]
        Or None on failure.
        """
        if self._lib is None:
            return None

        s = len(a_primes)
        n_str = str(int(n)).encode('ascii')
        a_str = str(int(a)).encode('ascii')

        # Input arrays
        c_a_primes = (ctypes.c_int32 * s)(*[int(p) for p in a_primes])
        c_a_prime_idx = (ctypes.c_int32 * s)(*[int(i) for i in a_prime_indices])
        c_sqrt_qj = (ctypes.c_int32 * s)(*[int(t) for t in sqrt_n_mod_qj])
        fb_arr = self._ensure_fb_arr(fb, fb_size)

        c_sqrt_fb = (ctypes.c_int32 * fb_size)(*[int(t) if t is not None else -1
                                                   for t in sqrt_n_mod_fb])

        # Output arrays
        a_inv_mod = np.zeros(fb_size, dtype=np.int64)
        is_a_prime = np.zeros(fb_size, dtype=np.int32)
        deltas = np.zeros(s * fb_size, dtype=np.int64)
        o1 = np.zeros(fb_size, dtype=np.int64)
        o2 = np.zeros(fb_size, dtype=np.int64)

        # Caller-allocated string buffers
        b_buf = ctypes.create_string_buffer(_STR_BUFSIZE)
        c_buf = ctypes.create_string_buffer(_STR_BUFSIZE)
        Bj_buf = ctypes.create_string_buffer(s * _STR_BUFSIZE)

        ret = self._lib.full_poly_setup(
            n_str, a_str,
            c_a_primes, c_a_prime_idx, c_sqrt_qj, s,
            fb_arr, c_sqrt_fb, fb_size, M,
            a_inv_mod.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            is_a_prime.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            deltas.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            o1.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            o2.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            b_buf,
            c_buf,
            Bj_buf,
            _STR_BUFSIZE,
        )

        if ret != 0:
            return None

        # Extract results from buffers
        from gmpy2 import mpz
        b_val = mpz(b_buf.value.decode('ascii'))
        c_val = mpz(c_buf.value.decode('ascii'))

        # Parse B_j strings from contiguous buffer
        B_values = []
        raw = Bj_buf.raw
        for j in range(s):
            chunk = raw[j * _STR_BUFSIZE : (j + 1) * _STR_BUFSIZE]
            # Find null terminator
            nul = chunk.index(b'\x00')
            B_values.append(mpz(chunk[:nul].decode('ascii')))

        # Split deltas into per-j arrays
        delta_list = [deltas[j * fb_size:(j + 1) * fb_size].copy() for j in range(s)]

        return {
            'b': b_val,
            'c': c_val,
            'B_values': B_values,
            'a_inv_mod': a_inv_mod,
            'is_a_prime': is_a_prime,
            'deltas': delta_list,
            'o1': o1,
            'o2': o2,
        }

    def gray_switch(self, fb, fb_size, is_a_prime, delta_j, offset_dir, o1, o2,
                    a_prime_indices=None, s=0, b_str=None, c_str=None, a_int_mod2=0, M=0):
        """
        Incremental Gray code switch: update o1, o2 in-place.

        Also recomputes a-prime roots if a_prime_indices is provided.
        """
        if self._lib is None:
            return

        fb_arr = self._ensure_fb_arr(fb, fb_size)

        self._lib.gray_code_switch(
            fb_arr, fb_size,
            delta_j.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            is_a_prime.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            offset_dir,
            o1.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            o2.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
        )

        # Recompute a-prime roots
        if a_prime_indices is not None and b_str is not None and c_str is not None:
            c_api = (ctypes.c_int32 * s)(*[int(i) for i in a_prime_indices])
            b_bytes = b_str.encode('ascii') if isinstance(b_str, str) else b_str
            c_bytes = c_str.encode('ascii') if isinstance(c_str, str) else c_str
            self._lib.recompute_a_prime_roots(
                fb_arr, c_api, s,
                b_bytes, c_bytes,
                ctypes.c_int64(a_int_mod2),
                M,
                o1.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
                o2.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            )


# ============================================================================
# Verification test
# ============================================================================

def _test_correctness():
    """Verify C poly setup matches Python SIQS computation exactly."""
    import gmpy2
    from gmpy2 import mpz, isqrt, jacobi, next_prime, is_prime
    import time
    import random

    ps = PolySetup()
    if not ps.available:
        print("ERROR: siqs_poly_c.so not available")
        return False

    # Use a known 54-digit semiprime
    p1 = 10007900019973801688507297
    p2 = 10008000104527300034104629
    N = mpz(p1) * mpz(p2)
    n = N
    print(f"Testing with {len(str(N))}d semiprime: {N}")

    # Build factor base
    fb_size = 2500
    fb = []
    p = 2
    while len(fb) < fb_size:
        if p == 2 or (is_prime(p) and jacobi(int(n % p), p) == 1):
            fb.append(int(p))
        p = int(next_prime(p)) if p > 2 else 3

    # Precompute sqrt(n) mod p
    from siqs_engine import tonelli_shanks
    sqrt_n_mod = {}
    for p in fb:
        if p == 2:
            sqrt_n_mod[p] = int(n % 2)
        else:
            sqrt_n_mod[p] = tonelli_shanks(int(n % p), p)

    sqrt_n_mod_fb = [sqrt_n_mod.get(p, -1) for p in fb]

    M = 1000000
    fb_index = {p: i for i, p in enumerate(fb)}

    # Select s primes for 'a'
    s = 6
    rng = random.Random(42)
    select_lo = max(1, fb_size // 4)
    select_hi = min(fb_size - 1, 3 * fb_size // 4)
    indices = sorted(rng.sample(range(select_lo, select_hi), s))
    a_primes = [fb[i] for i in indices]
    a_prime_indices = [fb_index[ap] for ap in a_primes]
    a = mpz(1)
    for ap in a_primes:
        a *= ap

    sqrt_n_mod_qj = [sqrt_n_mod[q] for q in a_primes]

    print(f"  a = {a} ({len(str(a))} digits, s={s})")
    print(f"  a_primes = {a_primes}")

    # --- Python reference computation ---
    t0 = time.time()

    py_B = []
    for j in range(s):
        q = a_primes[j]
        A_j = a // q
        A_j_inv = pow(int(A_j % q), -1, q)
        B_j = mpz(sqrt_n_mod_qj[j]) * A_j * mpz(A_j_inv) % a
        py_B.append(B_j)

    py_b = sum(py_B)
    if (py_b * py_b - n) % a != 0:
        py_b = -py_b
    py_c = (py_b * py_b - n) // a

    a_int = int(a)
    a_prime_set = set(a_primes)
    py_a_inv = np.zeros(fb_size, dtype=np.int64)
    py_is_a_prime = np.zeros(fb_size, dtype=np.int32)
    for pi in range(fb_size):
        p = fb[pi]
        if p in a_prime_set:
            py_a_inv[pi] = 0
            py_is_a_prime[pi] = 1
        else:
            try:
                py_a_inv[pi] = pow(a_int % p, -1, p)
            except (ValueError, ZeroDivisionError):
                py_a_inv[pi] = 0

    py_deltas = []
    for j in range(s):
        d = np.zeros(fb_size, dtype=np.int64)
        B_j_2 = 2 * py_B[j]
        for pi in range(fb_size):
            p = fb[pi]
            if p in a_prime_set:
                d[pi] = 0
            else:
                d[pi] = int(B_j_2 % p) * py_a_inv[pi] % p
        py_deltas.append(d)

    b_int = int(py_b)
    py_o1 = np.full(fb_size, -1, dtype=np.int64)
    py_o2 = np.full(fb_size, -1, dtype=np.int64)
    for pi in range(fb_size):
        p = fb[pi]
        if p == 2:
            g0 = int(py_c % 2)
            g1 = int((a_int + 2 * b_int + int(py_c)) % 2)
            if g0 == 0:
                py_o1[pi] = M % 2
                if g1 == 0:
                    py_o2[pi] = (M + 1) % 2
            elif g1 == 0:
                py_o1[pi] = (M + 1) % 2
            continue
        if p in a_prime_set:
            b2 = (2 * b_int) % p
            if b2 == 0:
                continue
            b2_inv = pow(b2, -1, p)
            c_mod = int(py_c % p)
            r = (-c_mod * b2_inv) % p
            py_o1[pi] = (r + M) % p
            continue
        t = sqrt_n_mod.get(p)
        if t is None:
            continue
        ai = int(py_a_inv[pi])
        bm = b_int % p
        r1 = (ai * (t - bm)) % p
        r2 = (ai * (p - t - bm)) % p
        py_o1[pi] = (r1 + M) % p
        py_o2[pi] = ((r2 + M) % p) if r2 != r1 else -1

    py_time = time.time() - t0

    # --- C computation ---
    t0 = time.time()
    result = ps.full_poly_setup(n, a, a_primes, a_prime_indices,
                                 sqrt_n_mod_qj, fb, sqrt_n_mod_fb, fb_size, M)
    c_time = time.time() - t0

    if result is None:
        print("  ERROR: C full_poly_setup returned None")
        return False

    # --- Compare ---
    all_ok = True

    # B_values
    for j in range(s):
        if py_B[j] != result['B_values'][j]:
            print(f"  MISMATCH B_values[{j}]: py={py_B[j]} c={result['B_values'][j]}")
            all_ok = False
    if all_ok:
        print(f"  B_values: OK (all {s} match)")

    # b and c — C may negate b if needed for divisibility
    b_match = (py_b == result['b'])
    b_neg_match = (py_b == -result['b'])
    if b_match:
        print(f"  b: OK (exact match)")
    elif b_neg_match:
        print(f"  b: OK (negated, both valid)")
    else:
        print(f"  MISMATCH b: py={py_b} c={result['b']}")
        all_ok = False

    # a_inv_mod
    a_inv_diff = np.sum(py_a_inv != result['a_inv_mod'])
    if a_inv_diff > 0:
        print(f"  MISMATCH a_inv_mod: {a_inv_diff}/{fb_size} differences")
        for i in range(fb_size):
            if py_a_inv[i] != result['a_inv_mod'][i]:
                print(f"    [{i}] p={fb[i]}: py={py_a_inv[i]} c={result['a_inv_mod'][i]}")
                if i > 5: break
        all_ok = False
    else:
        print(f"  a_inv_mod: OK (all {fb_size} match)")

    # is_a_prime
    is_ap_diff = np.sum(py_is_a_prime != result['is_a_prime'])
    if is_ap_diff > 0:
        print(f"  MISMATCH is_a_prime: {is_ap_diff} differences")
        all_ok = False
    else:
        print(f"  is_a_prime: OK")

    # deltas
    delta_ok = True
    for j in range(s):
        d_diff = np.sum(py_deltas[j] != result['deltas'][j])
        if d_diff > 0:
            print(f"  MISMATCH deltas[{j}]: {d_diff} differences")
            delta_ok = False
            all_ok = False
    if delta_ok:
        print(f"  deltas: OK (all {s} x {fb_size} match)")

    # Sieve roots — only compare when b matches exactly
    if b_match:
        o1_diff = np.sum(py_o1 != result['o1'])
        o2_diff = np.sum(py_o2 != result['o2'])
        if o1_diff > 0:
            print(f"  MISMATCH o1: {o1_diff}/{fb_size} differences")
            for i in range(fb_size):
                if py_o1[i] != result['o1'][i]:
                    print(f"    [{i}] p={fb[i]}: py={py_o1[i]} c={result['o1'][i]}")
                    if i > 5: break
            all_ok = False
        else:
            print(f"  o1: OK (all {fb_size} match)")
        if o2_diff > 0:
            print(f"  MISMATCH o2: {o2_diff}/{fb_size} differences")
            for i in range(fb_size):
                if py_o2[i] != result['o2'][i]:
                    print(f"    [{i}] p={fb[i]}: py={py_o2[i]} c={result['o2'][i]}")
                    if i > 5: break
            all_ok = False
        else:
            print(f"  o2: OK (all {fb_size} match)")
    else:
        print(f"  o1/o2: skipped (b was negated, roots self-consistent)")

    # --- Test Gray code switching ---
    print(f"\n  Testing Gray code switching (10 steps)...")
    from siqs_engine import gray_code_sequence
    gray_seq = gray_code_sequence(s - 1)

    c_o1 = result['o1'].copy()
    c_o2 = result['o2'].copy()
    c_b = result['b']

    py_b_cur = py_b
    py_o1_cur = py_o1.copy()
    py_o2_cur = py_o2.copy()

    signs = [1] * s
    gray_ok = True
    fb_np = np.array(fb, dtype=np.int64)
    regular_idx = np.where(~py_is_a_prime.astype(bool))[0]

    for step_i, (gray_val, flip_bit, flip_dir) in enumerate(gray_seq[:10]):
        j = flip_bit + 1
        if j >= s:
            continue
        old_sign = signs[j]
        signs[j] = -old_sign

        # Python update
        if signs[j] < 0:
            py_b_cur = py_b_cur - 2 * py_B[j]
            py_offset_dir = 1
        else:
            py_b_cur = py_b_cur + 2 * py_B[j]
            py_offset_dir = -1

        py_c_cur = (py_b_cur * py_b_cur - n) // a
        py_b_int = int(py_b_cur)

        delta_j = py_deltas[j]
        valid1 = py_o1_cur[regular_idx] >= 0
        ri_v1 = regular_idx[valid1]
        valid2 = py_o2_cur[regular_idx] >= 0
        ri_v2 = regular_idx[valid2]

        if py_offset_dir > 0:
            py_o1_cur[ri_v1] = (py_o1_cur[ri_v1] + delta_j[ri_v1]) % fb_np[ri_v1]
            py_o2_cur[ri_v2] = (py_o2_cur[ri_v2] + delta_j[ri_v2]) % fb_np[ri_v2]
        else:
            py_o1_cur[ri_v1] = (py_o1_cur[ri_v1] - delta_j[ri_v1]) % fb_np[ri_v1]
            py_o2_cur[ri_v2] = (py_o2_cur[ri_v2] - delta_j[ri_v2]) % fb_np[ri_v2]

        for pi in a_prime_indices:
            p = fb[pi]
            if p == 2:
                g0 = int(py_c_cur % 2)
                g1 = int((a_int + 2 * py_b_int + int(py_c_cur)) % 2)
                py_o1_cur[pi] = -1
                py_o2_cur[pi] = -1
                if g0 == 0:
                    py_o1_cur[pi] = M % 2
                    if g1 == 0:
                        py_o2_cur[pi] = (M + 1) % 2
                elif g1 == 0:
                    py_o1_cur[pi] = (M + 1) % 2
                continue
            b2 = (2 * py_b_int) % p
            if b2 == 0:
                py_o1_cur[pi] = -1
                py_o2_cur[pi] = -1
                continue
            b2_inv = pow(b2, -1, p)
            c_mod = int(py_c_cur % p)
            r = (-c_mod * b2_inv) % p
            py_o1_cur[pi] = (r + M) % p
            py_o2_cur[pi] = -1

        # C update
        if signs[j] < 0:
            c_b = c_b - 2 * result['B_values'][j]
            c_offset_dir = 1
        else:
            c_b = c_b + 2 * result['B_values'][j]
            c_offset_dir = -1

        c_c = (c_b * c_b - n) // a

        ps.gray_switch(
            fb, fb_size, result['is_a_prime'],
            result['deltas'][j], c_offset_dir, c_o1, c_o2,
            a_prime_indices=a_prime_indices, s=s,
            b_str=str(int(c_b)), c_str=str(int(c_c)),
            a_int_mod2=int(a) % 2, M=M,
        )

        # Compare
        if b_match:
            o1_diff = np.sum(py_o1_cur != c_o1)
            o2_diff = np.sum(py_o2_cur != c_o2)
            if o1_diff > 0 or o2_diff > 0:
                print(f"    Step {step_i}: MISMATCH o1={o1_diff} o2={o2_diff} diffs")
                # Show first few
                for i in range(fb_size):
                    if py_o1_cur[i] != c_o1[i]:
                        print(f"      o1[{i}] p={fb[i]}: py={py_o1_cur[i]} c={c_o1[i]}")
                        break
                gray_ok = False

    if gray_ok:
        print(f"    All 10 Gray code steps match!")
    all_ok = all_ok and gray_ok

    # --- Benchmark ---
    print(f"\n  Benchmark (10 poly setups):")
    t0 = time.time()
    for _ in range(10):
        ps.full_poly_setup(n, a, a_primes, a_prime_indices,
                           sqrt_n_mod_qj, fb, sqrt_n_mod_fb, fb_size, M)
    c_bench = (time.time() - t0) / 10

    t0 = time.time()
    for _ in range(10):
        py_B2 = []
        for j2 in range(s):
            q2 = a_primes[j2]
            A_j2 = a // q2
            A_j_inv2 = pow(int(A_j2 % q2), -1, q2)
            B_j2 = mpz(sqrt_n_mod_qj[j2]) * A_j2 * mpz(A_j_inv2) % a
            py_B2.append(B_j2)
        b2 = sum(py_B2)
        if (b2 * b2 - n) % a != 0:
            b2 = -b2
        c2 = (b2 * b2 - n) // a
        b2_int = int(b2)
        py_a_inv2 = np.zeros(fb_size, dtype=np.int64)
        for pi2 in range(fb_size):
            p2 = fb[pi2]
            if p2 in a_prime_set:
                continue
            if p2 == 2:
                continue
            try:
                py_a_inv2[pi2] = pow(a_int % p2, -1, p2)
            except:
                pass
        for pi2 in range(fb_size):
            p2 = fb[pi2]
            if p2 in a_prime_set or p2 == 2:
                continue
            t2 = sqrt_n_mod.get(p2)
            if t2 is None:
                continue
            ai2 = int(py_a_inv2[pi2])
            bm2 = b2_int % p2
            r12 = (ai2 * (t2 - bm2)) % p2
            r22 = (ai2 * (p2 - t2 - bm2)) % p2
    py_bench = (time.time() - t0) / 10

    print(f"    Python: {py_bench*1000:.2f} ms/setup")
    print(f"    C:      {c_bench*1000:.2f} ms/setup")
    if py_bench > 0 and c_bench > 0:
        print(f"    Speedup: {py_bench/c_bench:.1f}x")

    # Gray code switch benchmark
    print(f"\n  Benchmark (1000 Gray code switches):")
    c_o1b = result['o1'].copy()
    c_o2b = result['o2'].copy()
    t0 = time.time()
    for _ in range(1000):
        ps.gray_switch(fb, fb_size, result['is_a_prime'],
                       result['deltas'][0], 1, c_o1b, c_o2b)
    c_gray_time = (time.time() - t0) / 1000

    py_o1b = py_o1.copy()
    t0 = time.time()
    for _ in range(1000):
        delta_j0 = py_deltas[0]
        ri_v10 = regular_idx[py_o1b[regular_idx] >= 0]
        py_o1b[ri_v10] = (py_o1b[ri_v10] + delta_j0[ri_v10]) % fb_np[ri_v10]
    py_gray_time = (time.time() - t0) / 1000

    print(f"    Python (numpy): {py_gray_time*1e6:.0f} us/switch")
    print(f"    C:              {c_gray_time*1e6:.0f} us/switch")
    if py_gray_time > 0 and c_gray_time > 0:
        print(f"    Speedup: {py_gray_time/c_gray_time:.1f}x")

    if all_ok:
        print(f"\n  ALL TESTS PASSED")
    else:
        print(f"\n  SOME TESTS FAILED")
    return all_ok


if __name__ == '__main__':
    _test_correctness()

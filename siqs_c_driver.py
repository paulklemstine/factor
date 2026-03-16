#!/usr/bin/env python3
"""
SIQS C Driver — Unified integration layer for C-accelerated SIQS
=================================================================

Drop-in replacement for siqs_engine.siqs_factor with automatic fallback:
  - siqs_core_c.so  -> C sieve + TD + relation extraction (when available)
  - siqs_poly_c.so  -> C polynomial setup + Gray code switching (when available)
  - siqs_sieve_fast.so -> C sieve + threshold scan (existing, always available)
  - siqs_sieve_c.so -> C sieve kernel (existing, always available)
  - siqs_trial_div_c.so -> C trial division (existing, always available)
  - block_lanczos_c.so -> C GF(2) Gauss / Block Lanczos (existing, always available)

Fallback: if any C .so is missing, falls back to the Python implementation
from siqs_engine.py. The user experience is "it just works, faster if C libs
are compiled".

Usage:
    from siqs_c_driver import siqs_factor_c
    factor = siqs_factor_c(n, verbose=True)
"""

import gmpy2
from gmpy2 import mpz, isqrt, is_prime, gcd, jacobi, next_prime, legendre
import numpy as np
from numba import njit
import ctypes
import time
import math
import random
import bisect
import os
import multiprocessing
from collections import defaultdict

# Import the base engine for fallback and shared utilities
import siqs_engine

###############################################################################
# C LIBRARY LOADING — Graceful fallback for each component
###############################################################################

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_c_lib(name):
    """Load a C shared library by name, returning (lib, True) or (None, False)."""
    path = os.path.join(_SCRIPT_DIR, name)
    if not os.path.exists(path):
        return None, False
    try:
        lib = ctypes.CDLL(path)
        return lib, True
    except OSError:
        return None, False


# --- siqs_core_c.so: full sieve + TD + relation extraction ---
_core_lib, _HAS_CORE_C = _load_c_lib("siqs_core_c.so")
if _HAS_CORE_C:
    _core_lib.siqs_sieve_and_extract.restype = ctypes.c_int
    _core_lib.siqs_sieve_and_extract.argtypes = [
        ctypes.POINTER(ctypes.c_int32),    # fb_primes [fb_size]
        ctypes.POINTER(ctypes.c_int16),    # fb_logs [fb_size]
        ctypes.POINTER(ctypes.c_int32),    # roots1 [fb_size]
        ctypes.POINTER(ctypes.c_int32),    # roots2 [fb_size]
        ctypes.c_int,                      # fb_size
        ctypes.c_int,                      # M
        ctypes.c_int16,                    # threshold
        ctypes.c_char_p,                   # a_str
        ctypes.c_char_p,                   # b_str
        ctypes.c_char_p,                   # n_str
        ctypes.c_int64,                    # lp_bound
        ctypes.POINTER(ctypes.c_int32),    # a_prime_indices [n_a_primes]
        ctypes.c_int,                      # n_a_primes
        ctypes.POINTER(ctypes.c_int32),    # rel_x [max_rels]
        ctypes.POINTER(ctypes.c_int8),     # rel_type [max_rels]
        ctypes.POINTER(ctypes.c_int8),     # rel_sign [max_rels]
        ctypes.POINTER(ctypes.c_int16),    # rel_exps [max_rels * fb_size]
        ctypes.POINTER(ctypes.c_int64),    # rel_cofactor [max_rels]
        ctypes.POINTER(ctypes.c_int64),    # rel_cofactor2 [max_rels]
        ctypes.c_int,                      # max_rels
        ctypes.POINTER(ctypes.c_int16),    # sieve_buf [2*M]
        ctypes.POINTER(ctypes.c_int32),    # cand_buf [max_rels*20 or 2*M]
    ]

# --- siqs_poly_c.so: polynomial setup + Gray code ---
_poly_lib, _HAS_POLY_C = _load_c_lib("siqs_poly_c.so")
_poly_free_str = None  # default; set below if poly lib is available
if _HAS_POLY_C:
    # gray_code_switch: incremental root update when flipping B_j sign
    _poly_lib.gray_code_switch.restype = None
    _poly_lib.gray_code_switch.argtypes = [
        ctypes.POINTER(ctypes.c_int32),    # fb_primes
        ctypes.c_int,                      # fb_size
        ctypes.POINTER(ctypes.c_int64),    # delta_j
        ctypes.POINTER(ctypes.c_int32),    # is_a_prime
        ctypes.c_int,                      # offset_dir (+1 or -1)
        ctypes.POINTER(ctypes.c_int64),    # o1 (in/out)
        ctypes.POINTER(ctypes.c_int64),    # o2 (in/out)
    ]
    # recompute_a_prime_roots: fix up a-prime roots after gray switch
    _poly_lib.recompute_a_prime_roots.restype = None
    _poly_lib.recompute_a_prime_roots.argtypes = [
        ctypes.POINTER(ctypes.c_int32),    # fb_primes
        ctypes.POINTER(ctypes.c_int32),    # a_prime_indices
        ctypes.c_int,                      # s
        ctypes.c_char_p,                   # b_str
        ctypes.c_char_p,                   # c_str
        ctypes.c_int64,                    # a_int_mod2
        ctypes.c_int,                      # M
        ctypes.POINTER(ctypes.c_int64),    # o1
        ctypes.POINTER(ctypes.c_int64),    # o2
    ]
    # free_gmp_str: free strings allocated by GMP
    # May not be exported if compiled without it; use libc free as fallback
    try:
        _poly_lib.free_gmp_str.restype = None
        _poly_lib.free_gmp_str.argtypes = [ctypes.c_char_p]
        _poly_free_str = _poly_lib.free_gmp_str
    except AttributeError:
        _libc = ctypes.CDLL(None)  # loads libc
        _libc.free.restype = None
        _libc.free.argtypes = [ctypes.c_void_p]
        _poly_free_str = _libc.free
    # full_poly_setup: do all polynomial initialization in one C call
    _poly_lib.full_poly_setup.restype = ctypes.c_int
    _poly_lib.full_poly_setup.argtypes = [
        ctypes.c_char_p,                   # n_str
        ctypes.c_char_p,                   # a_str
        ctypes.POINTER(ctypes.c_int32),    # a_primes [s]
        ctypes.POINTER(ctypes.c_int32),    # a_prime_indices [s]
        ctypes.POINTER(ctypes.c_int32),    # sqrt_n_mod_qj [s]
        ctypes.c_int,                      # s
        ctypes.POINTER(ctypes.c_int32),    # fb_primes [fb_size]
        ctypes.POINTER(ctypes.c_int32),    # sqrt_n_mod_fb [fb_size]
        ctypes.c_int,                      # fb_size
        ctypes.c_int,                      # M
        ctypes.POINTER(ctypes.c_int64),    # a_inv_mod [fb_size] (out)
        ctypes.POINTER(ctypes.c_int32),    # is_a_prime [fb_size] (out)
        ctypes.POINTER(ctypes.c_int64),    # deltas [s*fb_size] (out)
        ctypes.POINTER(ctypes.c_int64),    # o1 [fb_size] (out)
        ctypes.POINTER(ctypes.c_int64),    # o2 [fb_size] (out)
        ctypes.POINTER(ctypes.c_char_p),   # b_out_str (out)
        ctypes.POINTER(ctypes.c_char_p),   # c_out_str (out)
        ctypes.POINTER(ctypes.c_char_p),   # Bj_strs [s] (out)
    ]

# --- siqs_sieve_fast.so: existing combined sieve + threshold scan ---
_sieve_fast_lib, _HAS_SIEVE_FAST = _load_c_lib("siqs_sieve_fast.so")
if _HAS_SIEVE_FAST:
    _sieve_fast_lib.siqs_sieve_fast.restype = ctypes.c_int
    _sieve_fast_lib.siqs_sieve_fast.argtypes = [
        ctypes.POINTER(ctypes.c_int16),   # sieve
        ctypes.c_int,                      # sz
        ctypes.POINTER(ctypes.c_int64),    # fb
        ctypes.POINTER(ctypes.c_int16),    # fb_logp
        ctypes.POINTER(ctypes.c_int64),    # off1
        ctypes.POINTER(ctypes.c_int64),    # off2
        ctypes.c_int,                      # n_fb
        ctypes.c_int16,                    # threshold
        ctypes.POINTER(ctypes.c_int32),    # out_cands
        ctypes.c_int,                      # max_cands
    ]
    _sieve_fast_lib.siqs_batch_hits.restype = ctypes.c_int
    _sieve_fast_lib.siqs_batch_hits.argtypes = [
        ctypes.POINTER(ctypes.c_int32),    # candidates
        ctypes.c_int,                      # n_cand
        ctypes.POINTER(ctypes.c_int64),    # fb
        ctypes.POINTER(ctypes.c_int64),    # off1
        ctypes.POINTER(ctypes.c_int64),    # off2
        ctypes.c_int,                      # n_fb
        ctypes.POINTER(ctypes.c_int32),    # hit_starts
        ctypes.POINTER(ctypes.c_int32),    # hit_fb
        ctypes.c_int,                      # max_total
    ]

# --- siqs_sieve_c.so: existing sieve kernel ---
_sieve_lib, _HAS_SIEVE_C = _load_c_lib("siqs_sieve_c.so")
if _HAS_SIEVE_C:
    _sieve_lib.siqs_sieve.restype = None
    _sieve_lib.siqs_sieve.argtypes = [
        ctypes.POINTER(ctypes.c_int16),
        ctypes.c_int,
        ctypes.POINTER(ctypes.c_int64),
        ctypes.POINTER(ctypes.c_int16),
        ctypes.POINTER(ctypes.c_int64),
        ctypes.POINTER(ctypes.c_int64),
        ctypes.c_int,
    ]
    _sieve_lib.siqs_find_survivors.restype = ctypes.c_int
    _sieve_lib.siqs_find_survivors.argtypes = [
        ctypes.POINTER(ctypes.c_int16),
        ctypes.c_int,
        ctypes.c_int16,
        ctypes.POINTER(ctypes.c_int32),
        ctypes.c_int,
    ]

# --- siqs_trial_div_c.so: existing batch trial division ---
_td_lib, _HAS_TD_C = _load_c_lib("siqs_trial_div_c.so")
if _HAS_TD_C:
    _td_lib.trial_divide_one.restype = None
    _td_lib.trial_divide_one.argtypes = [
        ctypes.POINTER(ctypes.c_int64),    # fb
        ctypes.POINTER(ctypes.c_int32),    # hits
        ctypes.c_int,                      # n_hits
        ctypes.c_uint64,                   # val_lo
        ctypes.c_uint64,                   # val_hi
        ctypes.POINTER(ctypes.c_int64),    # out_exps
        ctypes.POINTER(ctypes.c_int64),    # out_cofactor
    ]
    _td_lib.trial_divide_batch.restype = None
    _td_lib.trial_divide_batch.argtypes = [
        ctypes.POINTER(ctypes.c_int64),    # fb
        ctypes.POINTER(ctypes.c_int32),    # all_hits
        ctypes.POINTER(ctypes.c_int32),    # hit_starts
        ctypes.POINTER(ctypes.c_uint64),   # vals_lo
        ctypes.POINTER(ctypes.c_uint64),   # vals_hi
        ctypes.c_int,                      # n_cands
        ctypes.POINTER(ctypes.c_int64),    # all_exps (flat)
        ctypes.POINTER(ctypes.c_int64),    # cofactors
        ctypes.c_int,                      # max_hits
    ]

# --- block_lanczos_c.so: GF(2) linear algebra ---
_bl_lib, _HAS_BL_C = _load_c_lib("block_lanczos_c.so")


###############################################################################
# CAPABILITY REPORT
###############################################################################

def get_capabilities():
    """Return a dict describing which C accelerations are available."""
    return {
        "siqs_core_c": _HAS_CORE_C,
        "siqs_poly_c": _HAS_POLY_C,
        "siqs_sieve_fast": _HAS_SIEVE_FAST,
        "siqs_sieve_c": _HAS_SIEVE_C,
        "siqs_trial_div_c": _HAS_TD_C,
        "block_lanczos_c": _HAS_BL_C,
    }


def print_capabilities():
    """Print which C accelerations are available."""
    caps = get_capabilities()
    print("SIQS C Driver — Capability Report")
    print("-" * 40)
    for name, available in caps.items():
        status = "AVAILABLE" if available else "missing (Python fallback)"
        print(f"  {name:20s}: {status}")
    print()


###############################################################################
# C-ACCELERATED SIEVE FUNCTIONS
###############################################################################

def c_sieve_and_find(sieve_buf, sz, fb_np, fb_log, off1, off2, fb_size, threshold):
    """
    Run C sieve + candidate detection. Returns candidate positions as numpy array.

    Uses siqs_sieve_fast.so (combined sieve+scan) if available,
    else siqs_sieve_c.so (separate sieve+scan),
    else falls back to numba JIT.

    Timing info returned as (candidates, sieve_time).
    """
    t0 = time.time()

    if _HAS_SIEVE_FAST:
        # Combined sieve + threshold scan in single C call
        max_cands = min(sz // 4, 200000)
        out_cands = np.zeros(max_cands, dtype=np.int32)

        sieve_c = sieve_buf.ctypes.data_as(ctypes.POINTER(ctypes.c_int16))
        fb_c = fb_np.ctypes.data_as(ctypes.POINTER(ctypes.c_int64))
        log_c = fb_log.ctypes.data_as(ctypes.POINTER(ctypes.c_int16))
        o1_c = off1.ctypes.data_as(ctypes.POINTER(ctypes.c_int64))
        o2_c = off2.ctypes.data_as(ctypes.POINTER(ctypes.c_int64))
        out_c = out_cands.ctypes.data_as(ctypes.POINTER(ctypes.c_int32))

        n_cand = _sieve_fast_lib.siqs_sieve_fast(
            sieve_c, sz, fb_c, log_c, o1_c, o2_c,
            fb_size, ctypes.c_int16(threshold), out_c, max_cands
        )
        elapsed = time.time() - t0
        if n_cand > 0:
            return out_cands[:n_cand].astype(np.int64), elapsed
        return np.empty(0, dtype=np.int64), elapsed

    elif _HAS_SIEVE_C:
        # Separate sieve + scan
        sieve_buf[:] = 0
        sieve_c = sieve_buf.ctypes.data_as(ctypes.POINTER(ctypes.c_int16))
        fb_c = fb_np.ctypes.data_as(ctypes.POINTER(ctypes.c_int64))
        log_c = fb_log.ctypes.data_as(ctypes.POINTER(ctypes.c_int16))
        o1_c = off1.ctypes.data_as(ctypes.POINTER(ctypes.c_int64))
        o2_c = off2.ctypes.data_as(ctypes.POINTER(ctypes.c_int64))

        _sieve_lib.siqs_sieve(sieve_c, sz, fb_c, log_c, o1_c, o2_c, fb_size)

        max_cands = min(sz // 4, 200000)
        out_cands = np.zeros(max_cands, dtype=np.int32)
        out_c = out_cands.ctypes.data_as(ctypes.POINTER(ctypes.c_int32))

        n_cand = _sieve_lib.siqs_find_survivors(
            sieve_c, sz, ctypes.c_int16(threshold), out_c, max_cands
        )
        elapsed = time.time() - t0
        if n_cand > 0:
            return out_cands[:n_cand].astype(np.int64), elapsed
        return np.empty(0, dtype=np.int64), elapsed

    else:
        # Numba JIT fallback
        sieve_buf[:] = 0
        siqs_engine.jit_sieve(sieve_buf, fb_np, fb_log, off1, off2, sz)
        candidates = siqs_engine.jit_find_smooth(sieve_buf, threshold)
        elapsed = time.time() - t0
        return candidates, elapsed


def c_batch_find_hits(candidates, n_cand, fb_np, off1, off2, fb_size):
    """
    Batch hit detection: for each candidate, find which FB primes divide it.

    Uses siqs_sieve_fast.so batch_hits if available,
    else falls back to numba JIT.

    Returns (hit_starts, hit_fb, elapsed_time).
    """
    t0 = time.time()

    if _HAS_SIEVE_FAST:
        max_total = n_cand * 80
        hit_starts = np.zeros(n_cand + 1, dtype=np.int32)
        hit_fb = np.zeros(max_total, dtype=np.int32)

        cand_c = candidates.astype(np.int32).ctypes.data_as(ctypes.POINTER(ctypes.c_int32))
        fb_c = fb_np.ctypes.data_as(ctypes.POINTER(ctypes.c_int64))
        o1_c = off1.ctypes.data_as(ctypes.POINTER(ctypes.c_int64))
        o2_c = off2.ctypes.data_as(ctypes.POINTER(ctypes.c_int64))
        hs_c = hit_starts.ctypes.data_as(ctypes.POINTER(ctypes.c_int32))
        hf_c = hit_fb.ctypes.data_as(ctypes.POINTER(ctypes.c_int32))

        total = _sieve_fast_lib.siqs_batch_hits(
            cand_c, n_cand, fb_c, o1_c, o2_c, fb_size,
            hs_c, hf_c, max_total
        )
        elapsed = time.time() - t0
        return hit_starts, hit_fb[:total], elapsed

    else:
        # Numba JIT fallback
        hit_starts, hit_fb = siqs_engine.jit_batch_find_hits(
            candidates, n_cand, fb_np, off1, off2, fb_size
        )
        elapsed = time.time() - t0
        return hit_starts, hit_fb, elapsed


def c_trial_divide_one(fb_np, hits, n_hits, val):
    """
    Trial divide one candidate value against its hit primes using C.

    Falls back to Python divmod if C not available.

    Returns (exps_dict, cofactor).
    exps_dict maps FB index -> exponent (only nonzero entries).
    """
    if _HAS_TD_C and val < (1 << 128):
        val_abs = abs(val)
        val_lo = ctypes.c_uint64(val_abs & 0xFFFFFFFFFFFFFFFF)
        val_hi = ctypes.c_uint64((val_abs >> 64) & 0xFFFFFFFFFFFFFFFF)

        out_exps = (ctypes.c_int64 * n_hits)()
        out_cofactor = ctypes.c_int64(0)

        hits_c = hits[:n_hits].ctypes.data_as(ctypes.POINTER(ctypes.c_int32))
        fb_c = fb_np.ctypes.data_as(ctypes.POINTER(ctypes.c_int64))

        _td_lib.trial_divide_one(
            fb_c, hits_c, n_hits,
            val_lo, val_hi,
            ctypes.cast(out_exps, ctypes.POINTER(ctypes.c_int64)),
            ctypes.byref(out_cofactor)
        )

        exps_dict = {}
        for i in range(n_hits):
            if out_exps[i] > 0:
                exps_dict[int(hits[i])] = int(out_exps[i])
        return exps_dict, int(out_cofactor.value)

    else:
        # Python fallback: divmod loop
        v = abs(val)
        fb = fb_np
        exps_dict = {}
        for i in range(n_hits):
            idx = int(hits[i])
            p = int(fb[idx])
            if v <= 1:
                break
            q, r = divmod(v, p)
            if r == 0:
                e = 1
                v = q
                q, r = divmod(v, p)
                while r == 0:
                    e += 1
                    v = q
                    q, r = divmod(v, p)
                exps_dict[idx] = e
        return exps_dict, int(v)


###############################################################################
# C POLY SETUP + GRAY CODE SWITCH HELPERS
###############################################################################

def c_full_poly_setup(n, a, a_primes, a_prime_idx, sqrt_n_mod, fb, fb_size, M, s):
    """
    Full polynomial initialization in one C call (siqs_poly_c.so).
    Returns (B_values, b, c, a_inv_mod, is_a_prime_arr, deltas, o1, o2) or None.
    """
    if not _HAS_POLY_C:
        return None

    n_str = str(int(n)).encode('ascii')
    a_str = str(int(a)).encode('ascii')

    a_primes_c = (ctypes.c_int32 * s)(*[int(p) for p in a_primes])
    a_prime_idx_c = (ctypes.c_int32 * s)(*[int(i) for i in a_prime_idx])

    sqrt_n_mod_qj = (ctypes.c_int32 * s)()
    for j, q in enumerate(a_primes):
        t = sqrt_n_mod.get(int(q))
        if t is None:
            return None
        sqrt_n_mod_qj[j] = int(t)

    fb_primes_c = (ctypes.c_int32 * fb_size)(*[int(p) for p in fb])
    sqrt_n_mod_fb_c = (ctypes.c_int32 * fb_size)()
    for i in range(fb_size):
        t = sqrt_n_mod.get(int(fb[i]))
        sqrt_n_mod_fb_c[i] = int(t) if t is not None else -1

    # Output buffers
    a_inv_mod_out = np.zeros(fb_size, dtype=np.int64)
    is_a_prime_out = np.zeros(fb_size, dtype=np.int32)
    deltas_out = np.zeros(s * fb_size, dtype=np.int64)
    o1_out = np.full(fb_size, -1, dtype=np.int64)
    o2_out = np.full(fb_size, -1, dtype=np.int64)

    b_out = ctypes.c_char_p()
    c_out = ctypes.c_char_p()
    Bj_strs_out = (ctypes.c_char_p * s)()

    ret = _poly_lib.full_poly_setup(
        n_str, a_str,
        a_primes_c, a_prime_idx_c, sqrt_n_mod_qj, s,
        fb_primes_c, sqrt_n_mod_fb_c, fb_size, M,
        a_inv_mod_out.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
        is_a_prime_out.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
        deltas_out.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
        o1_out.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
        o2_out.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
        ctypes.byref(b_out),
        ctypes.byref(c_out),
        Bj_strs_out,
    )

    if ret != 0:
        return None

    # Parse output strings
    b_val = mpz(b_out.value.decode('ascii'))
    c_val = mpz(c_out.value.decode('ascii'))
    B_values = []
    for j in range(s):
        B_values.append(mpz(Bj_strs_out[j].decode('ascii')))

    # Free GMP-allocated strings
    _poly_free_str(b_out)
    _poly_free_str(c_out)
    for j in range(s):
        _poly_free_str(Bj_strs_out[j])

    # Reshape deltas: s arrays of fb_size
    deltas_list = []
    for j in range(s):
        deltas_list.append(deltas_out[j * fb_size:(j + 1) * fb_size].copy())

    return B_values, b_val, c_val, a_inv_mod_out, is_a_prime_out, deltas_list, o1_out, o2_out


def c_gray_code_switch(fb, fb_size, delta_j, is_a_prime_arr, offset_dir,
                       o1, o2, b, c, a_prime_idx, a_int, n, a, B_values, j_flip, signs, s, M):
    """
    Perform Gray code polynomial switch using C acceleration.

    Updates o1, o2 in-place for regular primes via C gray_code_switch,
    then recomputes a-prime roots via C recompute_a_prime_roots.

    Returns (new_b, new_c).
    """
    if not _HAS_POLY_C:
        return None

    # Update b
    if signs[j_flip] < 0:
        b = b - 2 * B_values[j_flip]
    else:
        b = b + 2 * B_values[j_flip]

    c = (b * b - n) // a

    fb_primes_c = np.array(fb, dtype=np.int32)
    fb_c = fb_primes_c.ctypes.data_as(ctypes.POINTER(ctypes.c_int32))
    delta_c = delta_j.ctypes.data_as(ctypes.POINTER(ctypes.c_int64))
    iap_c = is_a_prime_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int32))
    o1_c = o1.ctypes.data_as(ctypes.POINTER(ctypes.c_int64))
    o2_c = o2.ctypes.data_as(ctypes.POINTER(ctypes.c_int64))

    _poly_lib.gray_code_switch(fb_c, fb_size, delta_c, iap_c,
                               offset_dir, o1_c, o2_c)

    # Recompute a-prime roots
    a_prime_idx_c = (ctypes.c_int32 * s)(*[int(i) for i in a_prime_idx])
    b_str = str(int(b)).encode('ascii')
    c_str = str(int(c)).encode('ascii')
    a_mod2 = int(a) % 2

    _poly_lib.recompute_a_prime_roots(
        fb_c, a_prime_idx_c, s,
        b_str, c_str, ctypes.c_int64(a_mod2), M,
        o1_c, o2_c
    )

    return b, c


###############################################################################
# C FULL PIPELINE: sieve + TD + relation extraction in one call
###############################################################################

# Preallocated buffers for the C core pipeline (reused across calls)
_core_bufs = {}

def _get_core_bufs(fb_size, M, max_rels=500):
    """Get or allocate reusable buffers for siqs_sieve_and_extract."""
    key = (fb_size, M)
    if key in _core_bufs:
        return _core_bufs[key]
    sz = 2 * M
    bufs = {
        'sieve_buf': np.zeros(sz, dtype=np.int16),
        'cand_buf': np.zeros(min(max_rels * 20, sz), dtype=np.int32),
        'rel_x': np.zeros(max_rels, dtype=np.int32),
        'rel_type': np.zeros(max_rels, dtype=np.int8),
        'rel_sign': np.zeros(max_rels, dtype=np.int8),
        'rel_exps': np.zeros(max_rels * fb_size, dtype=np.int16),
        'rel_cofactor': np.zeros(max_rels, dtype=np.int64),
        'rel_cofactor2': np.zeros(max_rels, dtype=np.int64),
        'max_rels': max_rels,
    }
    _core_bufs[key] = bufs
    return bufs


def c_sieve_and_extract(fb_i32, fb_log, o1, o2, fb_size, M, threshold,
                        a, b, n, lp_bound, a_prime_idx):
    """
    Full C pipeline: sieve + TD + cofactor classification in one call.
    Returns list of (rel_type, sieve_pos, sign, exps_sparse, cofactor, cofactor2).

    rel_type: 0=smooth, 1=SLP, 2=DLP, 3=direct factor
    """
    if not _HAS_CORE_C:
        return None

    bufs = _get_core_bufs(fb_size, M)
    max_rels = bufs['max_rels']

    # Convert offsets to int32 roots for C (C core uses int32 roots not int64 offsets)
    roots1 = o1.astype(np.int32)
    roots2 = o2.astype(np.int32)

    a_str = str(int(a)).encode('ascii')
    b_str = str(int(b)).encode('ascii')
    n_str = str(int(n)).encode('ascii')

    s = len(a_prime_idx)
    api_c = (ctypes.c_int32 * s)(*[int(i) for i in a_prime_idx])

    n_rels = _core_lib.siqs_sieve_and_extract(
        fb_i32.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
        fb_log.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
        roots1.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
        roots2.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
        fb_size, M, ctypes.c_int16(threshold),
        a_str, b_str, n_str,
        ctypes.c_int64(int(lp_bound)),
        api_c, s,
        bufs['rel_x'].ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
        bufs['rel_type'].ctypes.data_as(ctypes.POINTER(ctypes.c_int8)),
        bufs['rel_sign'].ctypes.data_as(ctypes.POINTER(ctypes.c_int8)),
        bufs['rel_exps'].ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
        bufs['rel_cofactor'].ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
        bufs['rel_cofactor2'].ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
        max_rels,
        bufs['sieve_buf'].ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
        bufs['cand_buf'].ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
    )

    if n_rels <= 0:
        return []

    # Parse results into Python tuples
    results = []
    for ri in range(n_rels):
        rtype = int(bufs['rel_type'][ri])
        sieve_pos = int(bufs['rel_x'][ri])
        sign = int(bufs['rel_sign'][ri])
        cofactor = int(bufs['rel_cofactor'][ri])
        cofactor2 = int(bufs['rel_cofactor2'][ri])

        # Extract sparse exponents from the flat array
        base = ri * fb_size
        exps_raw = bufs['rel_exps'][base:base + fb_size]
        sparse = tuple((j, int(exps_raw[j])) for j in range(fb_size) if exps_raw[j] != 0)

        results.append((rtype, sieve_pos, sign, sparse, cofactor, cofactor2))

    return results


###############################################################################
# PHASE TIMING TRACKER
###############################################################################

class PhaseTimer:
    """Accumulate per-phase timing for benchmarking."""
    __slots__ = ('sieve', 'hits', 'td', 'poly_setup', 'la', 'sqrt',
                 'total', '_t0')

    def __init__(self):
        self.sieve = 0.0
        self.hits = 0.0
        self.td = 0.0
        self.poly_setup = 0.0
        self.la = 0.0
        self.sqrt = 0.0
        self.total = 0.0
        self._t0 = time.time()

    def finalize(self):
        self.total = time.time() - self._t0

    def summary(self):
        return {
            'sieve': self.sieve,
            'hits': self.hits,
            'td': self.td,
            'poly_setup': self.poly_setup,
            'la': self.la,
            'sqrt': self.sqrt,
            'total': self.total,
        }


###############################################################################
# MAIN C-ACCELERATED SIQS FACTOR FUNCTION
###############################################################################

def siqs_factor_c(n, verbose=True, time_limit=3600, multiplier=1,
                  n_workers=1, grouped_a=True, phase_timer=None):
    """
    Self-Initializing Quadratic Sieve with C acceleration.

    Drop-in replacement for siqs_engine.siqs_factor() with automatic
    fallback to Python for any missing C components.

    Flow:
        for each a_value:
            B_values, deltas = setup_poly(N, a, a_primes)     # C or Python
            for each gray_code_poly:
                gray_switch(offsets, delta_j, sign)             # C or Python
                candidates = c_sieve_and_find(...)              # C sieve
                hits = c_batch_find_hits(...)                   # C hits
                for each candidate:
                    exps, cofactor = trial_divide(...)           # C or Python TD
                    classify_relation(exps, cofactor)            # Python LP graph
        matrix = build_gf2_matrix(relations)                    # Python
        deps = gauss_or_lanczos(matrix)                         # C (block_lanczos_c.so)
        factor = sqrt_and_gcd(deps, relations, N)               # Python

    Args:
        n: number to factor
        verbose: print progress
        time_limit: max seconds
        multiplier: Knuth-Schroeppel multiplier (1, 'auto', or int)
        n_workers: parallel sieve workers
        grouped_a: use grouped a-selection for LP resonance
        phase_timer: PhaseTimer instance for benchmark timing (optional)

    Returns: a non-trivial factor of n, or None
    """
    if phase_timer is None:
        phase_timer = PhaseTimer()

    n = mpz(n)
    nd = len(str(n))
    nb = int(gmpy2.log2(n)) + 1

    # Quick checks
    if n <= 1:
        return None
    if n % 2 == 0:
        return 2
    if is_prime(n):
        return int(n)
    sr = isqrt(n)
    if sr * sr == n:
        return int(sr)

    # Knuth-Schroeppel multiplier selection
    original_n = n
    if multiplier == 'auto':
        k = siqs_engine._ks_select_multiplier(n, verbose=verbose)
    else:
        k = int(multiplier)

    fb_size, M = siqs_engine.siqs_params(nd)

    if k > 1:
        n = mpz(k) * n
        nb = int(gmpy2.log2(n)) + 1

    if verbose:
        caps = get_capabilities()
        accel_parts = [name for name, avail in caps.items() if avail]
        k_str = f", k={k}" if k > 1 else ""
        print(f"  SIQS-C: {len(str(original_n))}d ({int(gmpy2.log2(original_n))+1}b)"
              f"{k_str}, FB={fb_size}, M={M}")
        print(f"    C accel: {', '.join(accel_parts) if accel_parts else 'none (pure Python)'}")

    def _extract_factor(g):
        g = gcd(mpz(g), original_n)
        if 1 < g < original_n:
            return int(g)
        return None

    t0 = time.time()

    # ======================================================================
    # Stage 1: Build Factor Base
    # ======================================================================
    fb = []
    p = 2
    while len(fb) < fb_size:
        if p == 2 or (is_prime(p) and jacobi(int(n % p), p) == 1):
            fb.append(int(p))
        p = int(next_prime(p)) if p > 2 else 3

    fb_np = np.array(fb, dtype=np.int64)
    fb_i32 = np.array(fb, dtype=np.int32)  # int32 version for C core
    fb_log = np.array([int(round(math.log2(p) * 64)) for p in fb], dtype=np.int16)
    fb_index = {p: i for i, p in enumerate(fb)}

    # Small prime correction for sieve threshold
    small_prime_correction = 0
    for p in fb:
        if p >= 32:
            break
        roots = 1 if p == 2 else 2
        small_prime_correction += roots * math.log2(p) * 64 / p
    small_prime_correction = int(small_prime_correction * 0.60)

    if verbose:
        print(f"    FB[{fb[0]}..{fb[-1]}] built ({time.time()-t0:.1f}s)")

    # Precompute sqrt(n) mod p
    sqrt_n_mod = {}
    for p in fb:
        if p == 2:
            sqrt_n_mod[2] = int(n % 2)
        else:
            sqrt_n_mod[p] = siqs_engine.tonelli_shanks(int(n % p), p)

    sqrt_n = isqrt(n)
    if sqrt_n * sqrt_n < n:
        sqrt_n += 1

    # ======================================================================
    # Stage 2: Relation Collection
    # ======================================================================
    lp_bound = min(fb[-1] * 100, fb[-1] ** 2)
    if nb >= 180:
        T_bits = max(15, nb // 4 - 1)
    else:
        T_bits = max(15, nb // 4 - 2)
    needed = fb_size + 100

    dlp_graph = siqs_engine.DoubleLargePrimeGraph(n, fb_size, lp_bound)

    if verbose:
        print(f"    Need {needed} rels, T_bits={T_bits}, "
              f"LP_bound={int(math.log10(lp_bound)):.0f}d")

    # JIT warmup
    dummy = np.zeros(100, dtype=np.int16)
    _wp = np.array([2, 3], dtype=np.int64)
    _wl = np.array([10, 15], dtype=np.int16)
    _wo = np.array([0, 1], dtype=np.int64)
    siqs_engine.jit_presieve(dummy, _wp, _wl, _wo, _wo, 100)
    siqs_engine.jit_sieve(dummy, _wp, _wl, _wo, _wo, 100)
    siqs_engine.jit_find_smooth(dummy, 1)
    siqs_engine.jit_find_hits(0, _wp, _wo, _wo, 2)

    poly_count = 0
    total_cands = 0
    a_count = 0

    # Polynomial parameter selection
    target_a = isqrt(2 * n) // M
    log_target = float(gmpy2.log2(target_a)) if target_a > 0 else 0

    best_s = 2
    best_range = (1, len(fb) - 1)
    best_score = float('inf')
    for s_try in range(2, 12):
        ideal_log = log_target / s_try
        if ideal_log < 3.5 or ideal_log > 50:
            continue
        ideal_prime = int(2 ** ideal_log)
        mid = bisect.bisect_left(fb, ideal_prime)
        if mid >= len(fb):
            continue
        lo = max(1, mid - max(s_try * 5, 20))
        hi = min(len(fb) - 1, mid + max(s_try * 5, 20))
        pool_size = hi - lo
        if pool_size < s_try * 3:
            continue
        actual_median = fb[min(max(mid, lo), hi)]
        score = abs(math.log2(max(actual_median, 2)) - ideal_log)
        if ideal_prime < 100:
            score += 2.0
        elif ideal_prime < 500:
            score += 0.5
        if s_try > 8:
            score += (s_try - 8) * 0.5
        if score < best_score:
            best_score = score
            best_s = s_try
            best_range = (lo, hi)

    s = best_s
    select_lo, select_hi = best_range
    num_b_polys = 1 << (s - 1)

    if verbose:
        print(f"    s={s}, {num_b_polys} polys/a, select FB[{select_lo}..{select_hi}]")

    gray_seq = siqs_engine.gray_code_sequence(s - 1)

    sz = 2 * M
    _sieve_buf = np.zeros(sz, dtype=np.int16)

    # ======================================================================
    # Main Sieve Loop (single-threaded, C-accelerated)
    # ======================================================================
    # For n_workers > 1, delegate to the existing multiprocessing path
    # in siqs_engine since it handles fork/pickle correctly.
    if n_workers > 1:
        if verbose:
            print(f"    Multi-worker mode: delegating to siqs_engine ({n_workers} workers)")
        result = siqs_engine.siqs_factor(
            int(original_n), verbose=verbose, time_limit=time_limit,
            multiplier=multiplier, n_workers=n_workers, grouped_a=grouped_a
        )
        phase_timer.finalize()
        return result

    for a_iter in range(200000):
        if dlp_graph.num_smooth >= needed or time.time() - t0 > time_limit:
            break

        # --- Select 'a' as product of s FB primes near target ---
        t_poly = time.time()
        best_a = None
        best_diff = float('inf')

        for _ in range(20):
            try:
                indices = sorted(random.sample(range(select_lo, select_hi), s))
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
        a_count += 1

        # === POLYNOMIAL SETUP: C path or Python fallback ===
        c_poly_result = c_full_poly_setup(
            n, a, a_primes, a_prime_idx, sqrt_n_mod, fb, fb_size, M, s)

        if c_poly_result is not None:
            # C poly setup succeeded
            (B_values, b, c, a_inv_mod, is_a_prime_i32,
             deltas, o1, o2) = c_poly_result
            b_int = int(b)
            # Convert is_a_prime to bool for numpy where()
            is_a_prime = is_a_prime_i32.astype(np.bool_)
            regular_idx = np.where(~is_a_prime)[0]
        else:
            # Python fallback: compute t_roots, B_values, etc.
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

            a_inv_mod = np.zeros(fb_size, dtype=np.int64)
            is_a_prime = np.zeros(fb_size, dtype=np.bool_)
            is_a_prime_i32 = np.zeros(fb_size, dtype=np.int32)
            for pi in range(fb_size):
                p = fb[pi]
                if p in a_prime_set:
                    a_inv_mod[pi] = 0
                    is_a_prime[pi] = True
                    is_a_prime_i32[pi] = 1
                else:
                    try:
                        a_inv_mod[pi] = pow(a_int % p, -1, p)
                    except (ValueError, ZeroDivisionError):
                        a_inv_mod[pi] = 0

            regular_idx = np.where(~is_a_prime)[0]

            deltas = []
            for j in range(s):
                d = np.zeros(fb_size, dtype=np.int64)
                B_j_2 = 2 * B_values[j]
                for pi in range(fb_size):
                    p = fb[pi]
                    if p in a_prime_set:
                        d[pi] = 0
                    else:
                        d[pi] = int(B_j_2 % p) * a_inv_mod[pi] % p
                deltas.append(d)

            b = mpz(0)
            for B_j in B_values:
                b += B_j
            if (b * b - n) % a != 0:
                b = -b
                if (b * b - n) % a != 0:
                    continue

            c = (b * b - n) // a
            b_int = int(b)

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

        phase_timer.poly_setup += time.time() - t_poly

        # Sieve threshold
        _log_g_max = math.log2(max(M, 1)) + 0.5 * nb
        _thresh = int(max(0, (_log_g_max - T_bits)) * 64) - small_prime_correction

        def sieve_and_collect(b_val, c_val, off1, off2):
            """Sieve one polynomial using C acceleration and collect relations."""
            nonlocal poly_count, total_cands

            # ============================================================
            # FAST PATH: Full C pipeline (sieve + TD + classify in one call)
            # Currently disabled: ctypes marshalling overhead makes the C core
            # slower than numba JIT for single-threaded operation. The C core
            # will be enabled when a full C multiprocessing worker is built
            # (eliminating Python-side per-relation marshalling).
            # Set _USE_CORE_C = True to force-enable for testing.
            # ============================================================
            _USE_CORE_C = False
            if _USE_CORE_C and _HAS_CORE_C:
                t_all = time.time()
                rels = c_sieve_and_extract(
                    fb_i32, fb_log, off1, off2, fb_size, M, _thresh,
                    a, b_val, n, lp_bound, a_prime_idx)
                elapsed = time.time() - t_all
                phase_timer.sieve += elapsed * 0.4  # approximate split
                phase_timer.td += elapsed * 0.6
                poly_count += 1

                if rels is None or len(rels) == 0:
                    return None

                for rtype, sieve_pos, sign, sparse, cofactor, cofactor2 in rels:
                    total_cands += 1

                    if rtype == 3:
                        # Direct factor: recompute ax+b and check gcd
                        x = sieve_pos - M
                        ax_b = int(a * x + b_val)
                        g = gcd(mpz(ax_b), n)
                        if 1 < g < n:
                            return int(g)
                        continue

                    # Build dense exps from sparse
                    exps = [0] * fb_size
                    nz_indices = []
                    for idx, e in sparse:
                        exps[idx] = int(e)
                        nz_indices.append(idx)

                    # Compute x_stored = (a*x + b) mod n
                    x = sieve_pos - M
                    ax_b = int(a * x + b_val)
                    x_stored = int(mpz(ax_b) % n)

                    if rtype == 0:
                        # Smooth
                        dlp_graph.add_smooth(x_stored, sign, exps)
                    elif rtype == 1:
                        # Single large prime
                        result = dlp_graph.add_single_lp(
                            x_stored, sign, exps, int(cofactor))
                        if result:
                            return result
                    elif rtype == 2:
                        # Double large prime
                        sparse_t = tuple((j, exps[j]) for j in nz_indices)
                        result = dlp_graph.add_double_lp_sparse(
                            x_stored, sign, exps, sparse_t,
                            int(cofactor), int(cofactor2))
                        if result:
                            return result
                return None

            # ============================================================
            # FALLBACK: Separate C sieve + Python TD
            # ============================================================
            b_v = int(b_val)
            c_v = int(c_val)

            # === C-ACCELERATED SIEVE ===
            candidates, sieve_time = c_sieve_and_find(
                _sieve_buf, sz, fb_np, fb_log, off1, off2, fb_size, _thresh)
            phase_timer.sieve += sieve_time

            n_cand = len(candidates)
            total_cands += n_cand

            if n_cand == 0:
                poly_count += 1
                return None

            # === HIT DETECTION: numba JIT ===
            t_hits = time.time()
            hit_starts, hit_fb = siqs_engine.jit_batch_find_hits(
                candidates, n_cand, fb_np, off1, off2, fb_size)
            phase_timer.hits += time.time() - t_hits

            # === TRIAL DIVISION + RELATION CLASSIFICATION ===
            t_td = time.time()
            for ci in range(n_cand):
                sieve_pos = int(candidates[ci])
                x = sieve_pos - M
                ax_b = int(a * x + b_val)
                gx = a_int * x * x + 2 * b_v * x + c_v

                if gx == 0:
                    g = gcd(mpz(ax_b), n)
                    if 1 < g < n:
                        phase_timer.td += time.time() - t_td
                        return int(g)
                    continue

                sign = 1 if gx < 0 else 0
                v = abs(gx)

                h_start = int(hit_starts[ci])
                h_end = int(hit_starts[ci + 1])

                exps_dict = {}
                cofactor = v
                for h in range(h_start, h_end):
                    idx = int(hit_fb[h])
                    p = fb[idx]
                    if cofactor <= 1:
                        break
                    q, r = divmod(cofactor, p)
                    if r == 0:
                        e = 1
                        cofactor = q
                        q, r = divmod(cofactor, p)
                        while r == 0:
                            e += 1
                            cofactor = q
                            q, r = divmod(cofactor, p)
                        exps_dict[idx] = e

                # Build full exponent vector
                exps = [0] * fb_size
                nz_indices = []
                for idx, e in exps_dict.items():
                    exps[idx] = e
                    nz_indices.append(idx)
                for idx in a_prime_idx:
                    if exps[idx] == 0:
                        nz_indices.append(idx)
                    exps[idx] += 1

                x_stored = int(mpz(ax_b) % n)

                if cofactor == 1:
                    dlp_graph.add_smooth(x_stored, sign, exps)
                elif cofactor < lp_bound and is_prime(cofactor):
                    result = dlp_graph.add_single_lp(x_stored, sign, exps, int(cofactor))
                    if result:
                        phase_timer.td += time.time() - t_td
                        return result
                elif cofactor < lp_bound * lp_bound and cofactor > 1:
                    if is_prime(mpz(cofactor)):
                        continue
                    sq = gmpy2.isqrt(mpz(cofactor))
                    if sq * sq == cofactor and is_prime(sq):
                        lp1 = lp2 = int(sq)
                    else:
                        lp1 = siqs_engine._quick_factor(cofactor)
                        if lp1 and lp1 > 1 and cofactor // lp1 > 1:
                            lp2 = cofactor // lp1
                        else:
                            continue
                    if (lp1 < lp_bound and lp2 < lp_bound
                            and is_prime(mpz(lp1)) and is_prime(mpz(lp2))):
                        sparse = tuple((j, exps[j]) for j in nz_indices)
                        result = dlp_graph.add_double_lp_sparse(
                            x_stored, sign, exps, sparse, lp1, lp2)
                        if result:
                            phase_timer.td += time.time() - t_td
                            return result

            phase_timer.td += time.time() - t_td
            poly_count += 1
            return None

        # Sieve first polynomial
        result = sieve_and_collect(b, c, o1, o2)
        if result:
            if k > 1:
                f = _extract_factor(result)
                if f:
                    phase_timer.finalize()
                    return f
            else:
                phase_timer.finalize()
                return result

        # Gray code B-switching
        signs = [1] * s
        for gray_val, flip_bit, flip_dir in gray_seq:
            if dlp_graph.num_smooth >= needed or time.time() - t0 > time_limit:
                break

            t_gs = time.time()
            j = flip_bit + 1
            if j >= s:
                continue

            old_sign = signs[j]
            signs[j] = -old_sign

            if signs[j] < 0:
                offset_dir = 1
            else:
                offset_dir = -1

            # === C GRAY CODE SWITCH (or Python fallback) ===
            c_result = c_gray_code_switch(
                fb, fb_size, deltas[j], is_a_prime_i32, offset_dir,
                o1, o2, b, c, a_prime_idx, a_int, n, a,
                B_values, j, signs, s, M)

            if c_result is not None:
                b, c = c_result
                b_int = int(b)
            else:
                # Python fallback
                if signs[j] < 0:
                    b = b - 2 * B_values[j]
                else:
                    b = b + 2 * B_values[j]

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

            phase_timer.poly_setup += time.time() - t_gs

            result = sieve_and_collect(b, c, o1, o2)
            if result:
                if k > 1:
                    f = _extract_factor(result)
                    if f:
                        phase_timer.finalize()
                        return f
                else:
                    phase_timer.finalize()
                    return result

        # Progress report
        if a_count % max(1, 10 if nd < 60 else 3) == 0 and verbose:
            elapsed = time.time() - t0
            ns = dlp_graph.num_smooth
            rate = ns / max(elapsed, 0.001)
            eta = (needed - ns) / max(rate, 0.001) if rate > 0 else 99999
            print(f"      [{elapsed:.0f}s] a={a_count} poly={poly_count} "
                  f"sm={ns}/{needed} part={dlp_graph.num_partials} "
                  f"dlp={dlp_graph.dlp_count} cand={total_cands} "
                  f"rate={rate:.1f}/s eta={min(eta,99999):.0f}s"
                  f" | sieve={phase_timer.sieve:.1f}s "
                  f"hits={phase_timer.hits:.1f}s td={phase_timer.td:.1f}s")

    # ======================================================================
    # Stage 3: GF(2) Gaussian Elimination
    # ======================================================================
    smooth = dlp_graph.smooth
    elapsed = time.time() - t0

    if len(smooth) < fb_size + 1:
        if verbose:
            print(f"\n    Insufficient: {len(smooth)}/{needed} ({elapsed:.1f}s)")
        phase_timer.finalize()
        return None

    if verbose:
        print(f"\n    LA: {len(smooth)} x {fb_size + 1}")

    la_t0 = time.time()

    # Singleton filtering
    active_rows = list(range(len(smooth)))
    for _filt_pass in range(10):
        col_count = {}
        for ri in active_rows:
            _, sign, exps = smooth[ri]
            if sign % 2:
                col_count[0] = col_count.get(0, 0) + 1
            for j, e in enumerate(exps):
                if e % 2:
                    col_count[j + 1] = col_count.get(j + 1, 0) + 1
        singletons = {c for c, cnt in col_count.items() if cnt == 1}
        if not singletons:
            break
        new_active = []
        for ri in active_rows:
            _, sign, exps = smooth[ri]
            has_singleton = False
            if sign % 2 and 0 in singletons:
                has_singleton = True
            if not has_singleton:
                for j, e in enumerate(exps):
                    if e % 2 and (j + 1) in singletons:
                        has_singleton = True
                        break
            if not has_singleton:
                new_active.append(ri)
        if len(new_active) == len(active_rows):
            break
        active_rows = new_active

    if verbose and len(active_rows) < len(smooth):
        print(f"    Filtering: {len(smooth)} -> {len(active_rows)} rows "
              f"({100 - len(active_rows) * 100 // len(smooth)}% removed)")

    filtered_smooth = [smooth[i] for i in active_rows]
    row_map = active_rows
    nrows = len(filtered_smooth)
    ncols = fb_size + 1

    sparse_rows = []
    for _, sign, exps in filtered_smooth:
        cols = set()
        if sign % 2:
            cols.add(0)
        for j, e in enumerate(exps):
            if e % 2 == 1:
                cols.add(j + 1)
        sparse_rows.append(cols)

    try:
        from block_lanczos import bitpacked_gauss
        raw_vecs = bitpacked_gauss(sparse_rows, ncols)
    except (ImportError, MemoryError):
        raw_vecs = siqs_engine._fallback_gauss(sparse_rows, ncols, nrows)

    null_vecs = [[row_map[i] for i in vec] for vec in raw_vecs]
    phase_timer.la = time.time() - la_t0

    if verbose:
        print(f"    LA: {phase_timer.la:.1f}s, {len(null_vecs)} null vecs")

    # ======================================================================
    # Stage 4: Square Root + GCD
    # ======================================================================
    sqrt_t0 = time.time()
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
                if k > 1:
                    f = _extract_factor(int(g))
                    if f is None:
                        continue
                    phase_timer.sqrt = time.time() - sqrt_t0
                    phase_timer.finalize()
                    total = time.time() - t0
                    if verbose:
                        print(f"\n    *** FACTOR: {f} ({total:.1f}s, k={k}) ***")
                    return f
                else:
                    phase_timer.sqrt = time.time() - sqrt_t0
                    phase_timer.finalize()
                    total = time.time() - t0
                    if verbose:
                        print(f"\n    *** FACTOR: {g} ({total:.1f}s) ***")
                    return int(g)

    phase_timer.sqrt = time.time() - sqrt_t0
    phase_timer.finalize()

    if verbose:
        print(f"    {len(null_vecs)} null vecs, no factor found.")
    return None


###############################################################################
# SELF-TEST
###############################################################################

if __name__ == "__main__":
    random.seed(42)
    print_capabilities()

    print("=" * 70)
    print("SIQS C Driver — Correctness Tests")
    print("=" * 70)

    tests = [
        ("30d", 100000000000067 * 100000000000097),
        ("40d", int(next_prime(mpz(10)**19 + 7)) * int(next_prime(mpz(10)**19 + 231))),
    ]

    for name, n_val in tests:
        nd = len(str(n_val))
        print(f"\n### {name}: {nd}d ###")
        pt = PhaseTimer()
        f = siqs_factor_c(n_val, verbose=True, phase_timer=pt)
        ok = f is not None and 1 < f < n_val and n_val % f == 0
        status = "PASS" if ok else "FAIL"
        print(f"  {status}: {f} x {n_val // f}" if ok else f"  {status}")
        s = pt.summary()
        print(f"  Phases: sieve={s['sieve']:.2f}s hits={s['hits']:.2f}s "
              f"td={s['td']:.2f}s poly={s['poly_setup']:.2f}s "
              f"la={s['la']:.2f}s sqrt={s['sqrt']:.2f}s total={s['total']:.2f}s")

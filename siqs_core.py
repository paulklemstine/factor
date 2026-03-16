#!/usr/bin/env python3
"""
siqs_core.py -- Python ctypes wrapper for siqs_core_c.so

Provides a drop-in replacement for the per-polynomial hot path in siqs_engine.py.
The C code handles: sieve + candidate extraction + trial division + cofactor classification.

Usage in siqs_engine.py:
    from siqs_core import SIQSCoreC
    core = SIQSCoreC(fb_primes, fb_logs, fb_size, M, n_str, lp_bound)
    rels = core.sieve_poly(roots1, roots2, a_str, b_str, a_prime_indices, threshold)
    # rels = list of (rel_type, sieve_pos, sign, exps_sparse, cofactor, cofactor2)
"""

import ctypes
import os
import numpy as np
from numpy.ctypeslib import ndpointer
from ctypes import (
    c_int, c_int8, c_int16, c_int32, c_int64,
    POINTER
)

# Relation types (must match C defines)
REL_SMOOTH = 0
REL_SINGLE_LP = 1
REL_DOUBLE_LP = 2
REL_DIRECT_FACTOR = 3

_lib = None
_lib_loaded = False


def _load_lib():
    """Load the C shared library (lazy, cached)."""
    global _lib, _lib_loaded
    if _lib_loaded:
        return _lib
    _lib_loaded = True
    so_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'siqs_core_c.so')
    if not os.path.exists(so_path):
        return None
    try:
        _lib = ctypes.CDLL(so_path)
        # Set up function signature using ndpointer for numpy arrays
        _lib.siqs_sieve_and_extract.argtypes = [
            ndpointer(dtype=np.int32, flags='C_CONTIGUOUS'),  # fb_primes
            ndpointer(dtype=np.int16, flags='C_CONTIGUOUS'),  # fb_logs
            ndpointer(dtype=np.int32, flags='C_CONTIGUOUS'),  # roots1
            ndpointer(dtype=np.int32, flags='C_CONTIGUOUS'),  # roots2
            c_int,              # fb_size
            c_int,              # M
            c_int16,            # threshold
            ctypes.c_char_p,    # a_str
            ctypes.c_char_p,    # b_str
            ctypes.c_char_p,    # n_str
            c_int64,            # lp_bound
            ndpointer(dtype=np.int32, flags='C_CONTIGUOUS'),  # a_prime_indices
            c_int,              # n_a_primes
            ndpointer(dtype=np.int32, flags='C_CONTIGUOUS'),  # rel_x
            ndpointer(dtype=np.int8, flags='C_CONTIGUOUS'),   # rel_type
            ndpointer(dtype=np.int8, flags='C_CONTIGUOUS'),   # rel_sign
            ndpointer(dtype=np.int16, flags='C_CONTIGUOUS'),  # rel_exps
            ndpointer(dtype=np.int64, flags='C_CONTIGUOUS'),  # rel_cofactor
            ndpointer(dtype=np.int64, flags='C_CONTIGUOUS'),  # rel_cofactor2
            c_int,              # max_rels
            ndpointer(dtype=np.int16, flags='C_CONTIGUOUS'),  # sieve_buf
            ndpointer(dtype=np.int32, flags='C_CONTIGUOUS'),  # cand_buf
        ]
        _lib.siqs_sieve_and_extract.restype = c_int
        return _lib
    except OSError as e:
        print(f"WARNING: Failed to load siqs_core_c.so: {e}")
        _lib = None
        return None


class SIQSCoreC:
    """
    Wrapper around the C SIQS core sieve-to-relation pipeline.

    Pre-allocates all numpy buffers once, reuses them across polynomial calls.
    Uses numpy arrays directly (zero-copy to C via ndpointer).
    """

    def __init__(self, fb_primes_list, fb_logs_list, fb_size, M, n_str, lp_bound):
        """
        Initialize the C core with factor base and sieve parameters.

        Args:
            fb_primes_list: list/array of int32 factor base primes
            fb_logs_list: list/array of int16 log approximations (log2(p)*64)
            fb_size: number of primes in factor base
            M: sieve half-width
            n_str: number to factor as decimal string
            lp_bound: large prime bound
        """
        self.lib = _load_lib()
        if self.lib is None:
            raise RuntimeError("siqs_core_c.so not found or failed to load")

        self.fb_size = fb_size
        self.M = M
        self.sz = 2 * M
        self.n_bytes = n_str.encode() if isinstance(n_str, str) else n_str
        self.lp_bound = int(lp_bound)

        # Convert factor base to contiguous numpy arrays (persistent)
        self.fb_primes = np.array(fb_primes_list, dtype=np.int32)
        self.fb_logs = np.array(fb_logs_list, dtype=np.int16)

        # Pre-allocate per-poly input buffers (numpy, contiguous)
        self._roots1 = np.empty(fb_size, dtype=np.int32)
        self._roots2 = np.empty(fb_size, dtype=np.int32)

        # Pre-allocate output buffers
        self.max_rels = 20000  # generous: 48d can have ~8K candidates
        self._rel_x = np.empty(self.max_rels, dtype=np.int32)
        self._rel_type = np.empty(self.max_rels, dtype=np.int8)
        self._rel_sign = np.empty(self.max_rels, dtype=np.int8)
        self._rel_exps = np.empty(self.max_rels * fb_size, dtype=np.int16)
        self._rel_cofactor = np.empty(self.max_rels, dtype=np.int64)
        self._rel_cofactor2 = np.empty(self.max_rels, dtype=np.int64)

        # Workspace buffers
        self._sieve_buf = np.empty(self.sz, dtype=np.int16)
        max_cands = min(self.max_rels * 10, self.sz)
        self._cand_buf = np.empty(max_cands, dtype=np.int32)

    def sieve_poly(self, off1_np, off2_np, a_str, b_str, a_prime_idx_list, threshold):
        """
        Sieve one polynomial and extract all relations.

        Args:
            off1_np: numpy int64 array of sieve offsets (root 1), -1 = skip
            off2_np: numpy int64 array of sieve offsets (root 2), -1 = skip
            a_str: 'a' coefficient as decimal string
            b_str: 'b' coefficient as decimal string
            a_prime_idx_list: list of FB indices that are 'a' primes
            threshold: int16 sieve threshold

        Returns:
            list of (rel_type, sieve_pos, sign, sparse_exps, cofactor, cofactor2)
            where sparse_exps = tuple of (fb_index, exponent) for non-zero entries
        """
        fb_size = self.fb_size

        # Bulk copy offsets: numpy int64 -> int32 (vectorized, no Python loop)
        # Clamp values: anything < 0 becomes -1 for the C side
        np.clip(off1_np, -1, 2147483647, out=self._roots1.view(np.int64)[:fb_size] if False else None)
        # Direct cast is fastest -- values are always in int32 range
        self._roots1[:] = off1_np[:fb_size].astype(np.int32)
        self._roots2[:] = off2_np[:fb_size].astype(np.int32)

        # a_prime_indices as contiguous numpy
        a_idx = np.array(a_prime_idx_list, dtype=np.int32)

        # Encode strings
        a_bytes = a_str.encode() if isinstance(a_str, str) else a_str
        b_bytes = b_str.encode() if isinstance(b_str, str) else b_str

        # Call C
        n_rels = self.lib.siqs_sieve_and_extract(
            self.fb_primes, self.fb_logs,
            self._roots1, self._roots2,
            fb_size,
            self.M, c_int16(int(threshold)),
            a_bytes, b_bytes, self.n_bytes,
            c_int64(self.lp_bound),
            a_idx, len(a_idx),
            self._rel_x, self._rel_type, self._rel_sign,
            self._rel_exps, self._rel_cofactor, self._rel_cofactor2,
            self.max_rels,
            self._sieve_buf, self._cand_buf
        )

        if n_rels == 0:
            return []

        # Extract results using numpy vectorized operations
        # Reshape exponents to [n_rels, fb_size] for row access
        exps_2d = self._rel_exps[:n_rels * fb_size].reshape(n_rels, fb_size)

        results = []
        for ri in range(n_rels):
            rtype = int(self._rel_type[ri])
            spos = int(self._rel_x[ri])
            sign = int(self._rel_sign[ri])
            cof = int(self._rel_cofactor[ri])
            cof2 = int(self._rel_cofactor2[ri])

            # Extract sparse exponents using numpy nonzero (much faster than Python loop)
            row = exps_2d[ri]
            nz_idx = np.nonzero(row)[0]
            sparse = tuple((int(j), int(row[j])) for j in nz_idx)

            results.append((rtype, spos, sign, sparse, cof, cof2))

        return results

    def sieve_poly_raw(self, off1_np, off2_np, a_str, b_str, a_prime_idx_list, threshold):
        """
        Like sieve_poly() but returns numpy arrays instead of Python lists.
        Avoids per-relation Python object creation overhead.

        Returns: (n_rels, rel_type, rel_x, rel_sign, rel_exps_2d, rel_cofactor, rel_cofactor2)
        All are numpy arrays/views. Caller must copy before next sieve_poly call.
        """
        fb_size = self.fb_size

        # Bulk copy offsets
        self._roots1[:] = off1_np[:fb_size].astype(np.int32)
        self._roots2[:] = off2_np[:fb_size].astype(np.int32)

        a_idx = np.array(a_prime_idx_list, dtype=np.int32)
        a_bytes = a_str.encode() if isinstance(a_str, str) else a_str
        b_bytes = b_str.encode() if isinstance(b_str, str) else b_str

        n_rels = self.lib.siqs_sieve_and_extract(
            self.fb_primes, self.fb_logs,
            self._roots1, self._roots2,
            fb_size,
            self.M, c_int16(int(threshold)),
            a_bytes, b_bytes, self.n_bytes,
            c_int64(self.lp_bound),
            a_idx, len(a_idx),
            self._rel_x, self._rel_type, self._rel_sign,
            self._rel_exps, self._rel_cofactor, self._rel_cofactor2,
            self.max_rels,
            self._sieve_buf, self._cand_buf
        )

        if n_rels == 0:
            return 0, None, None, None, None, None, None

        # Return views (zero-copy, but caller must consume before next call)
        exps_2d = self._rel_exps[:n_rels * fb_size].reshape(n_rels, fb_size)
        return (n_rels,
                self._rel_type[:n_rels],
                self._rel_x[:n_rels],
                self._rel_sign[:n_rels],
                exps_2d,
                self._rel_cofactor[:n_rels],
                self._rel_cofactor2[:n_rels])


def is_available():
    """Check if the C core is available."""
    return _load_lib() is not None

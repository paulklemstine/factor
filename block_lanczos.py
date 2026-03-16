"""
GF(2) Linear Algebra: C Block Lanczos + C Gauss + Python Gauss fallback.

Three backends, tried in order by bitpacked_gauss():
  1. C Gauss   (block_lanczos_c.so:gauss_gf2_c) — O(n^3/64), reliable
  2. numpy Gauss — O(n^3/64), pure Python fallback

Block Lanczos (block_lanczos_c.so:block_lanczos) is available separately
via block_lanczos_solve(). It is O(n^2*w/64) and faster for large matrices
(5000+) but probabilistic — it finds fewer null vectors per run.

Drop-in: bitpacked_gauss(sparse_rows, ncols) has the same API as before.
"""

import numpy as np
import ctypes
import os
import time

# ---------------------------------------------------------------------------
# Load C shared library
# ---------------------------------------------------------------------------
_lib = None
_lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "block_lanczos_c.so")


def _load_lib():
    global _lib
    if _lib is not None:
        return _lib
    if not os.path.exists(_lib_path):
        return None
    try:
        _lib = ctypes.CDLL(_lib_path)

        _lib.gauss_gf2_c.restype = ctypes.c_int
        _lib.gauss_gf2_c.argtypes = [
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int),
            ctypes.c_int, ctypes.c_int,
            ctypes.POINTER(ctypes.c_uint64), ctypes.c_int,
        ]

        # Wiedemann null-space finder (renamed from block_lanczos)
        _lib.block_lanczos_v2.restype = ctypes.c_int
        _lib.block_lanczos_v2.argtypes = [
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int),
            ctypes.c_int, ctypes.c_int,
            ctypes.POINTER(ctypes.c_uint64), ctypes.c_int,
        ]

        # Block Wiedemann (64x parallel)
        try:
            _lib.block_wiedemann.restype = ctypes.c_int
            _lib.block_wiedemann.argtypes = [
                ctypes.POINTER(ctypes.c_int),
                ctypes.POINTER(ctypes.c_int),
                ctypes.c_int, ctypes.c_int,
                ctypes.POINTER(ctypes.c_uint64), ctypes.c_int,
            ]
        except AttributeError:
            pass

        # Legacy name compatibility
        try:
            _lib.block_lanczos.restype = ctypes.c_int
            _lib.block_lanczos.argtypes = [
                ctypes.POINTER(ctypes.c_int),
                ctypes.POINTER(ctypes.c_int),
                ctypes.c_int, ctypes.c_int,
                ctypes.POINTER(ctypes.c_uint64), ctypes.c_int,
            ]
        except AttributeError:
            pass

        return _lib
    except OSError:
        return None


# ---------------------------------------------------------------------------
# Sparse rows (set-of-ints) -> CSR arrays
# ---------------------------------------------------------------------------
def _sparse_to_csr(sparse_rows):
    """Convert list-of-sets to CSR (row_ptr, col_idx) as ctypes arrays."""
    nrows = len(sparse_rows)
    nnz = sum(len(r) for r in sparse_rows)

    row_ptr = (ctypes.c_int * (nrows + 1))()
    col_idx = (ctypes.c_int * max(nnz, 1))()

    idx = 0
    for i, row in enumerate(sparse_rows):
        row_ptr[i] = idx
        for c in sorted(row):
            col_idx[idx] = c
            idx += 1
    row_ptr[nrows] = idx
    return row_ptr, col_idx, nnz


# ---------------------------------------------------------------------------
# Decode bitpacked dependency vectors from C
# ---------------------------------------------------------------------------
def _decode_deps(deps_buf, ndeps, nrows):
    """Convert bitpacked deps to list of sorted row-index lists."""
    nwords = (nrows + 63) // 64
    result = []
    for d in range(ndeps):
        indices = []
        off = d * nwords
        for w in range(nwords):
            bits = deps_buf[off + w]
            base = w * 64
            while bits:
                lsb = bits & (-bits)
                idx = base + lsb.bit_length() - 1
                if idx < nrows:
                    indices.append(idx)
                bits ^= lsb
        if indices:
            result.append(sorted(indices))
    return result


# ---------------------------------------------------------------------------
# C Gauss elimination
# ---------------------------------------------------------------------------
def _c_gauss(sparse_rows, ncols, verbose=False):
    """GF(2) Gauss via C. Returns list of null vecs or None."""
    lib = _load_lib()
    if lib is None:
        return None

    nrows = len(sparse_rows)
    row_ptr, col_idx, nnz = _sparse_to_csr(sparse_rows)
    max_deps = nrows
    nwords_dep = (nrows + 63) // 64
    deps_buf = (ctypes.c_uint64 * (max_deps * nwords_dep))()

    if verbose:
        print(f"    C Gauss: {nrows}x{ncols}, nnz={nnz}")

    t0 = time.time()
    ndeps = lib.gauss_gf2_c(row_ptr, col_idx, nrows, ncols, deps_buf, max_deps)
    dt = time.time() - t0

    if ndeps < 0:
        if verbose:
            print(f"    C Gauss failed (code {ndeps})")
        return None

    vecs = _decode_deps(deps_buf, ndeps, nrows)
    if verbose:
        print(f"    C Gauss: {len(vecs)} null vecs, {dt:.3f}s")
    return vecs


# ---------------------------------------------------------------------------
# C Block Lanczos
# ---------------------------------------------------------------------------
def block_lanczos_solve(sparse_rows, ncols, verbose=False):
    """
    Wiedemann null-space finder over GF(2) via C shared library.

    Finds vectors x in the left null space of A (i.e., A^T * x = 0)
    using the Wiedemann algorithm with Berlekamp-Massey and block extraction.
    Each dependency is an nrows-bit vector indicating which rows XOR to zero.

    O(n * w * rank / 64) where w = average row weight.
    Faster than Gauss for matrices above ~15000 rows.

    Returns list of null vectors (sorted row-index lists), or None.
    """
    lib = _load_lib()
    if lib is None:
        return None

    nrows = len(sparse_rows)
    row_ptr, col_idx, nnz = _sparse_to_csr(sparse_rows)

    max_deps = min(256, nrows)
    nwords_dep = (nrows + 63) // 64
    deps_buf = (ctypes.c_uint64 * (max_deps * nwords_dep))()

    if verbose:
        print(f"    Wiedemann: {nrows}x{ncols}, nnz={nnz}")

    t0 = time.time()
    ndeps = lib.block_lanczos_v2(row_ptr, col_idx, nrows, ncols,
                                 deps_buf, max_deps)
    dt = time.time() - t0

    if ndeps < 0:
        if verbose:
            print(f"    Wiedemann failed (code {ndeps})")
        return None

    vecs = _decode_deps(deps_buf, ndeps, nrows)
    if verbose:
        print(f"    Wiedemann: {len(vecs)} null vecs, {dt:.3f}s")
    return vecs


# ---------------------------------------------------------------------------
# C Block Wiedemann (64x parallel)
# ---------------------------------------------------------------------------
def block_wiedemann_solve(sparse_rows, ncols, verbose=False):
    """
    Block Wiedemann null-space finder over GF(2) via C shared library.

    Uses 64 parallel Krylov sequences in a single block mat-vec pass,
    then 64 independent Berlekamp-Massey instances, then polynomial
    evaluation for null vector extraction.

    64x more null vectors per Phase 1 pass than scalar Wiedemann.
    Same mat-vec cost as scalar for Phase 1, but far fewer rounds needed.

    Returns list of null vectors (sorted row-index lists), or None.
    """
    lib = _load_lib()
    if lib is None:
        return None

    if not hasattr(lib, 'block_wiedemann'):
        if verbose:
            print("    block_wiedemann not found in .so, falling back to scalar")
        return None

    nrows = len(sparse_rows)
    row_ptr, col_idx, nnz = _sparse_to_csr(sparse_rows)

    max_deps = min(256, nrows)
    nwords_dep = (nrows + 63) // 64
    deps_buf = (ctypes.c_uint64 * (max_deps * nwords_dep))()

    if verbose:
        print(f"    Block Wiedemann: {nrows}x{ncols}, nnz={nnz}")

    t0 = time.time()
    ndeps = lib.block_wiedemann(row_ptr, col_idx, nrows, ncols,
                                deps_buf, max_deps)
    dt = time.time() - t0

    if ndeps < 0:
        if verbose:
            print(f"    Block Wiedemann failed (code {ndeps})")
        return None

    vecs = _decode_deps(deps_buf, ndeps, nrows)
    if verbose:
        print(f"    Block Wiedemann: {len(vecs)} null vecs, {dt:.3f}s")
    return vecs


# ---------------------------------------------------------------------------
# numpy Gauss (pure Python fallback)
# ---------------------------------------------------------------------------
def _numpy_gauss(sparse_rows, ncols, verbose=False):
    """numpy-based Gauss elimination. Always works."""
    nrows = len(sparse_rows)
    nwords_mat = (ncols + 63) // 64
    nwords_combo = (nrows + 63) // 64

    mem_mb = nrows * (nwords_mat + nwords_combo) * 8 / 1e6
    if verbose:
        print(f"    numpy Gauss: {nrows}x{ncols}, {mem_mb:.0f} MB")
    if mem_mb > 1800:
        raise MemoryError(f"GF(2) Gauss needs {mem_mb:.0f} MB (limit 1800 MB)")

    mat = np.zeros((nrows, nwords_mat), dtype=np.uint64)
    for i, row in enumerate(sparse_rows):
        for c in row:
            mat[i, c // 64] |= np.uint64(1) << np.uint64(c % 64)

    combo = np.zeros((nrows, nwords_combo), dtype=np.uint64)
    for i in range(nrows):
        combo[i, i // 64] = np.uint64(1) << np.uint64(i % 64)

    used = np.zeros(nrows, dtype=np.bool_)
    t0 = time.time()
    rank = 0

    for col in range(ncols):
        w = col // 64
        bit = np.uint64(1) << np.uint64(col % 64)
        col_bits = mat[:, w] & bit
        has_bit = col_bits.astype(np.bool_) & ~used
        all_set = np.where(has_bit)[0]
        if len(all_set) == 0:
            continue
        piv = int(all_set[0])
        used[piv] = True
        rank += 1
        rows_to_xor = all_set[1:]
        if len(rows_to_xor) > 0:
            mat[rows_to_xor] ^= mat[piv]
            combo[rows_to_xor] ^= combo[piv]
        if verbose and (col + 1) % 5000 == 0:
            print(f"      col {col+1}/{ncols}, rank={rank}, {time.time()-t0:.1f}s")

    null_vecs = []
    zero_rows = np.all(mat == 0, axis=1)
    for row_idx in np.where(zero_rows)[0]:
        indices = []
        for ww in range(nwords_combo):
            bits = int(combo[row_idx, ww])
            base = ww * 64
            while bits:
                lsb = bits & (-bits)
                indices.append(base + lsb.bit_length() - 1)
                bits ^= lsb
        indices = [i for i in indices if i < nrows]
        if indices:
            null_vecs.append(sorted(indices))

    if verbose:
        print(f"    numpy Gauss: {len(null_vecs)} null vecs, {time.time()-t0:.1f}s")
    return null_vecs


# ---------------------------------------------------------------------------
# Main entry point (drop-in compatible)
# ---------------------------------------------------------------------------
def bitpacked_gauss(sparse_rows, ncols, verbose=False):
    """
    GF(2) null-space computation. Tries C Gauss, falls back to numpy.

    Args:
        sparse_rows: list of sets of column indices (one per row)
        ncols: number of columns

    Returns:
        list of null vectors, each a sorted list of row indices whose XOR is zero
    """
    try:
        result = _c_gauss(sparse_rows, ncols, verbose=verbose)
        if result is not None:
            return result
    except Exception as e:
        if verbose:
            print(f"    C Gauss exception: {e}")

    if verbose:
        print("    Falling back to numpy Gauss")
    return _numpy_gauss(sparse_rows, ncols, verbose=verbose)


###############################################################################
# GNFS drop-in replacement
###############################################################################

def gf2_block_lanczos(relations, ncols_rat, ncols_alg, num_qc=0, num_sq=0,
                       num_lp=0, verbose=False):
    """
    Drop-in replacement for gf2_gaussian_elimination in gnfs_engine.py.
    """
    from gnfs_engine import _sge_reduce

    ncols = 1 + ncols_rat + ncols_alg + num_qc + num_sq + num_lp

    sparse_rows = []
    for rel in relations:
        cols = set()
        if rel['rat_sign'] % 2:
            cols.add(0)
        for j, e in enumerate(rel['rat_exps']):
            if e % 2 == 1:
                cols.add(j + 1)
        for j, e in enumerate(rel['alg_exps']):
            if e % 2 == 1:
                cols.add(j + 1 + ncols_rat)
        qc_bits = rel.get('qc_bits', [])
        for j, bit in enumerate(qc_bits):
            if bit:
                cols.add(j + 1 + ncols_rat + ncols_alg)
        sq_col = rel.get('sq_col', -1)
        sq_exp = rel.get('sq_exp', 0)
        if sq_col >= 0 and sq_exp % 2 == 1:
            cols.add(1 + ncols_rat + ncols_alg + num_qc + sq_col)
        for lp_col in rel.get('lp_cols', []):
            cols.add(1 + ncols_rat + ncols_alg + num_qc + num_sq + lp_col)
        sparse_rows.append(cols)

    reduced_rows, compositions, sge_null_vecs = _sge_reduce(sparse_rows, verbose=verbose)
    null_vecs = list(sge_null_vecs)

    if not reduced_rows:
        return null_vecs

    all_cols = set()
    for row in reduced_rows:
        all_cols.update(row)
    col_list = sorted(all_cols)
    col_map = {c: i for i, c in enumerate(col_list)}
    n_reduced_cols = len(col_list)

    if verbose:
        print(f"    LA post-SGE: {len(reduced_rows)} x {n_reduced_cols}")

    remapped = [{col_map[c] for c in row} for row in reduced_rows]
    raw_vecs = bitpacked_gauss(remapped, n_reduced_cols, verbose=verbose)

    for indices in raw_vecs:
        original = set()
        for ri in indices:
            if ri < len(compositions):
                original.symmetric_difference_update(compositions[ri])
        if original:
            null_vecs.append(sorted(original))

    return null_vecs


###############################################################################
# Verification and test utilities
###############################################################################

def _verify(sparse_rows, vecs):
    """Check how many kernel vectors actually XOR to zero."""
    good = 0
    for vec in vecs:
        combined = set()
        for idx in vec:
            if idx < len(sparse_rows):
                combined.symmetric_difference_update(sparse_rows[idx])
        if not combined:
            good += 1
    return good


def _rand_sparse(nrows, ncols, avg_w, seed=42):
    """Generate random sparse GF(2) matrix for testing."""
    rng = np.random.RandomState(seed)
    rows = []
    for _ in range(nrows):
        w = max(1, rng.poisson(avg_w))
        rows.append(set(rng.choice(ncols, size=min(w, ncols), replace=False).tolist()))
    return rows


###############################################################################
# Main: tests and benchmarks
###############################################################################

if __name__ == "__main__":
    print("=" * 60)
    print("GF(2) Linear Algebra — C Gauss + Block Lanczos + numpy Gauss")
    print("=" * 60)

    has_c = _load_lib() is not None
    print(f"C library: {_lib_path}")
    print(f"C library loaded: {has_c}")

    # Test 1: Known null vector (4x3)
    print("\n--- Test 1: 4x3 known null ---")
    rows = [{0, 2}, {1, 2}, {0, 1}, {0, 1, 2}]
    for name, fn in [("C Gauss", _c_gauss), ("Block Lanczos", block_lanczos_solve),
                     ("numpy Gauss", _numpy_gauss)]:
        if not has_c and fn is not _numpy_gauss:
            continue
        vecs = fn(rows, 3, verbose=False)
        if vecs is None:
            print(f"  {name}: None"); continue
        good = _verify(rows, vecs)
        print(f"  {name}: {len(vecs)} vecs, {good} verified -> {vecs}")

    # Benchmarks
    sizes = [
        (200,  180,  10, 10),
        (500,  480,  15, 11),
        (1000, 950,  15, 20),
        (2000, 1900, 20, 25),
        (5000, 4900, 20, 30),
    ]

    for nr, nc, w, seed in sizes:
        print(f"\n--- {nr}x{nc}, w={w} ---")
        rows = _rand_sparse(nr, nc, w, seed=seed)
        for name, fn in [("C Gauss", _c_gauss),
                         ("Block Lanczos", block_lanczos_solve),
                         ("numpy Gauss", _numpy_gauss)]:
            if not has_c and fn is not _numpy_gauss:
                continue
            try:
                t0 = time.time()
                vecs = fn(rows, nc, verbose=False)
                dt = time.time() - t0
                if vecs is None:
                    print(f"  {name}: None"); continue
                good = _verify(rows, vecs)
                status = "OK" if good == len(vecs) else f"FAIL({good}/{len(vecs)})"
                print(f"  {name:15s}: {len(vecs):4d} vecs, {good:4d} good [{status}], {dt:.3f}s")
            except Exception as e:
                print(f"  {name}: ERROR {e}")

    # Final: unified entry point
    print(f"\n--- bitpacked_gauss (unified) 5000x4900 ---")
    rows = _rand_sparse(5000, 4900, 20, seed=30)
    t0 = time.time()
    vecs = bitpacked_gauss(rows, 4900, verbose=True)
    dt = time.time() - t0
    good = _verify(rows, vecs)
    print(f"  Result: {len(vecs)} vecs, {good} verified, {dt:.3f}s")

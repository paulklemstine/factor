"""
GF(2) Linear Algebra for GNFS: bit-packed Gaussian elimination.

Drop-in replacement for gf2_gaussian_elimination in gnfs_engine.py.
Uses numpy-vectorized XOR on bit-packed uint64 rows for the matrix AND
the combination-tracking matrix.

Complexity: O(ncols * nrows * max(ncols, nrows) / 64) time.
Memory:     O(nrows * (ncols + nrows) / 8) bytes.

At 15K rows: ~55 MB RAM, ~30s. At 80K rows: ~1.2 GB RAM, ~15 min.
"""

import numpy as np
import time


def bitpacked_gauss(sparse_rows, ncols, verbose=False):
    """
    GF(2) Gaussian elimination with fully bit-packed matrix and combo tracking.

    The matrix and combination-tracking matrix are stored as numpy uint64 arrays.
    Elimination is vectorized via numpy array XOR on entire row slices.

    Args:
        sparse_rows: list of sets of column indices (one per row)
        ncols: number of columns

    Returns:
        list of null vectors, each a sorted list of row indices whose XOR is zero
    """
    nrows = len(sparse_rows)
    nwords_mat = (ncols + 63) // 64
    nwords_combo = (nrows + 63) // 64

    mem_mb = nrows * (nwords_mat + nwords_combo) * 8 / 1e6
    if verbose:
        print(f"    Gauss: {nrows}x{ncols}, {mem_mb:.0f} MB")

    if mem_mb > 1800:
        raise MemoryError(f"GF(2) Gauss needs {mem_mb:.0f} MB (limit 1800 MB). "
                          f"Reduce matrix with more aggressive SGE or increase RAM.")

    # Build bit-packed matrix
    mat = np.zeros((nrows, nwords_mat), dtype=np.uint64)
    for i, row in enumerate(sparse_rows):
        for c in row:
            mat[i, c // 64] |= np.uint64(1) << np.uint64(c % 64)

    # Bit-packed combination tracking (identity)
    combo = np.zeros((nrows, nwords_combo), dtype=np.uint64)
    for i in range(nrows):
        combo[i, i // 64] = np.uint64(1) << np.uint64(i % 64)

    used = np.zeros(nrows, dtype=np.bool_)
    pivot_row = np.full(ncols, -1, dtype=np.int32)  # pivot_row[col] = row index
    t0 = time.time()
    rank = 0

    for col in range(ncols):
        w = col // 64
        bit = np.uint64(1) << np.uint64(col % 64)

        # Find all rows with this column bit set
        col_bits = mat[:, w] & bit
        has_bit = col_bits.astype(np.bool_)
        all_set = np.where(has_bit)[0]
        if len(all_set) == 0:
            continue

        # Pick first unused row as pivot
        piv = -1
        for r in all_set:
            if not used[r]:
                piv = int(r)
                break
        if piv == -1:
            continue

        used[piv] = True
        pivot_row[col] = piv
        rank += 1

        # Eliminate from all other rows that have this bit
        rows_to_xor = all_set[all_set != piv]

        if len(rows_to_xor) > 0:
            mat[rows_to_xor] ^= mat[piv]
            combo[rows_to_xor] ^= combo[piv]

        if verbose and (col + 1) % 5000 == 0:
            print(f"      col {col+1}/{ncols}, rank={rank}, {time.time()-t0:.1f}s")

    # Extract null vectors (rows that are now all-zero)
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
        print(f"    Gauss: {len(null_vecs)} null vecs, {time.time()-t0:.1f}s")

    return null_vecs


###############################################################################
# GNFS drop-in replacement
###############################################################################

def gf2_block_lanczos(relations, ncols_rat, ncols_alg, num_qc=0, num_sq=0,
                       num_lp=0, verbose=False):
    """
    Drop-in replacement for gf2_gaussian_elimination in gnfs_engine.py.

    Uses SGE preprocessing then bit-packed Gaussian elimination.
    Handles matrices up to ~100K rows within 2GB RAM.

    Args:
        relations: list of GNFS relation dicts
        ncols_rat, ncols_alg: factor base sizes
        num_qc, num_sq, num_lp: extra column counts

    Returns:
        list of null vectors (each a sorted list of relation indices)
    """
    from gnfs_engine import _sge_reduce

    ncols = 1 + ncols_rat + ncols_alg + num_qc + num_sq + num_lp

    # Build sparse representation (identical to gnfs_engine)
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

    # SGE preprocessing
    reduced_rows, compositions, sge_null_vecs = _sge_reduce(sparse_rows, verbose=verbose)
    null_vecs = list(sge_null_vecs)

    if not reduced_rows:
        return null_vecs

    # Renumber columns for dense addressing
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

    # Map through SGE compositions to original relation indices
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
    print("GF(2) Bit-Packed Gauss — Tests & Benchmarks")
    print("=" * 60)

    # Test 1: Known null vector
    print("\n--- Test 1: 4x3 known null ---")
    rows = [{0, 2}, {1, 2}, {0, 1}, {0, 1, 2}]
    vecs = bitpacked_gauss(rows, 3, verbose=True)
    good = _verify(rows, vecs)
    print(f"  {len(vecs)} vectors, {good} verified")
    for v in vecs:
        print(f"    {v}")

    # Test 2: 200x180
    print("\n--- Test 2: 200x180, w=10 ---")
    rows = _rand_sparse(200, 180, 10, seed=10)
    t0 = time.time()
    vecs = bitpacked_gauss(rows, 180, verbose=True)
    dt = time.time() - t0
    good = _verify(rows, vecs)
    print(f"  {len(vecs)} vectors, {good} verified, {dt:.3f}s")

    # Test 3: 1000x950
    print("\n--- Test 3: 1000x950, w=15 ---")
    rows = _rand_sparse(1000, 950, 15, seed=20)
    t0 = time.time()
    vecs = bitpacked_gauss(rows, 950, verbose=True)
    dt = time.time() - t0
    good = _verify(rows, vecs)
    print(f"  {len(vecs)} vectors, {good} verified, {dt:.3f}s")

    # Test 4: 5000x4900
    print("\n--- Test 4: 5000x4900, w=20 ---")
    rows = _rand_sparse(5000, 4900, 20, seed=30)
    t0 = time.time()
    vecs = bitpacked_gauss(rows, 4900, verbose=True)
    dt = time.time() - t0
    good = _verify(rows, vecs)
    print(f"  {len(vecs)} vectors, {good} verified, {dt:.1f}s")

    # Test 5: 15000x14500
    print("\n--- Test 5: 15000x14500, w=25 ---")
    rows = _rand_sparse(15000, 14500, 25, seed=40)
    t0 = time.time()
    vecs = bitpacked_gauss(rows, 14500, verbose=True)
    dt = time.time() - t0
    good = _verify(rows, vecs)
    print(f"  {len(vecs)} vectors, {good} verified, {dt:.1f}s")

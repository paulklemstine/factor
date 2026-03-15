"""
Block Lanczos over GF(2) for GNFS linear algebra.

Two implementations:
1. block_lanczos() — Montgomery's Block Lanczos with 64-column blocks.
   O(n * n/64 * w) time, O(n * 8 * 3) bytes RAM. For matrices > 20K rows.
2. sparse_gauss() — Bit-packed Gauss with sparse combination tracking.
   O(n^2 * w / 64) time, O(n * w_mat / 8 + n * k * 4) bytes RAM.
   Better for < 80K rows due to lower constant factor in pure Python.

Both find row dependencies: subsets of rows whose XOR is the zero vector.
Interface matches gnfs_engine.py.
"""

import numpy as np
import time
from collections import defaultdict


###############################################################################
# Implementation 1: Bit-packed Gauss with sparse combo tracking
###############################################################################

def sparse_gauss(sparse_rows, ncols, verbose=False):
    """
    GF(2) Gaussian elimination with bit-packed matrix rows and sparse combos.

    The matrix is stored as bit-packed uint64 arrays (dense, O(n * ncols/64)).
    Combination tracking uses sparse sets of original row indices.
    This avoids the O(n^2) combo matrix that kills the dense approach.

    Time: O(ncols * nrows * ncols/64) — same as dense Gauss.
    RAM: O(nrows * ncols/8) for matrix + O(nrows * avg_combo) for combos.
    """
    nrows = len(sparse_rows)
    nwords = (ncols + 63) // 64

    if verbose:
        print(f"    SG: {nrows}x{ncols} ({nwords} words/row, "
              f"{nrows * nwords * 8 / 1e6:.1f} MB matrix)")

    # Build bit-packed matrix
    mat = np.zeros((nrows, nwords), dtype=np.uint64)
    for i, row in enumerate(sparse_rows):
        for c in row:
            mat[i, c // 64] |= np.uint64(1) << np.uint64(c % 64)

    # Sparse combination tracking: combo[i] = set of original row indices
    combos = [set([i]) for i in range(nrows)]

    used = np.zeros(nrows, dtype=np.bool_)
    t0 = time.time()

    for col in range(ncols):
        w = col // 64
        bit = np.uint64(1) << np.uint64(col % 64)

        # Find pivot
        piv = -1
        for row in range(nrows):
            if not used[row] and (mat[row, w] & bit):
                piv = row
                break
        if piv == -1:
            continue

        used[piv] = True

        # Vectorized: find all rows with this bit set
        has_bit = (mat[:, w] & bit).astype(np.bool_)
        has_bit[piv] = False
        rows_to_xor = np.where(has_bit)[0]

        if len(rows_to_xor) > 0:
            # Vectorized XOR for matrix rows
            mat[rows_to_xor] ^= mat[piv]

            # Sparse XOR for combos
            piv_combo = combos[piv]
            for r in rows_to_xor:
                combos[r].symmetric_difference_update(piv_combo)

        if verbose and (col + 1) % 5000 == 0:
            elapsed = time.time() - t0
            print(f"      col {col+1}/{ncols}, {elapsed:.1f}s")

    # Extract null vectors
    null_vecs = []
    zero_rows = np.all(mat == 0, axis=1)
    for row in np.where(zero_rows)[0]:
        if combos[row]:
            null_vecs.append(sorted(combos[row]))

    if verbose:
        elapsed = time.time() - t0
        print(f"    SG: {len(null_vecs)} null vecs, {elapsed:.1f}s")

    return null_vecs


###############################################################################
# Implementation 2: Montgomery's Block Lanczos
###############################################################################

def _build_csr(sparse_rows, ncols):
    nrows = len(sparse_rows)
    nnz = sum(len(r) for r in sparse_rows)
    rp = np.zeros(nrows + 1, dtype=np.int64)
    ci = np.empty(nnz, dtype=np.int32)
    pos = 0
    for i, cols in enumerate(sparse_rows):
        sc = sorted(cols)
        ci[pos:pos + len(sc)] = sc
        pos += len(sc)
        rp[i + 1] = pos
    return rp, ci


def _spmv(rp, ci, nr, nc, x):
    """B * x (nr x nc sparse) * (nc,) -> (nr,)."""
    y = np.zeros(nr, dtype=np.uint64)
    for i in range(nr):
        s, e = int(rp[i]), int(rp[i + 1])
        acc = np.uint64(0)
        for k in range(s, e):
            acc ^= x[ci[k]]
        y[i] = acc
    return y


def _spmvT(rp, ci, nr, nc, x):
    """B^T * x."""
    y = np.zeros(nc, dtype=np.uint64)
    for i in range(nr):
        xi = x[i]
        if xi == 0:
            continue
        s, e = int(rp[i]), int(rp[i + 1])
        for k in range(s, e):
            y[ci[k]] ^= xi
    return y


def _BBt(rp, ci, nr, nc, x):
    """A*x = B * B^T * x."""
    return _spmv(rp, ci, nr, nc, _spmvT(rp, ci, nr, nc, x))


def _inner(x, y, n):
    """X^T Y -> 64x64 GF(2) matrix."""
    M = np.zeros(64, dtype=np.uint64)
    for k in range(n):
        xk = int(x[k])
        if xk == 0:
            continue
        yk = y[k]
        bits = xk
        while bits:
            j = (bits & -bits).bit_length() - 1
            M[j] ^= yk
            bits &= bits - 1
    return M


def _mul64(A, B):
    """64x64 * 64x64 GF(2)."""
    C = np.zeros(64, dtype=np.uint64)
    for i in range(64):
        ai = int(A[i])
        bits = ai
        while bits:
            j = (bits & -bits).bit_length() - 1
            C[i] ^= B[j]
            bits &= bits - 1
    return C


def _apply(V, M, n):
    """V * M: (n,) uint64 block * 64x64 -> (n,) uint64."""
    out = np.zeros(n, dtype=np.uint64)
    for i in range(n):
        vi = int(V[i])
        if vi == 0:
            continue
        acc = np.uint64(0)
        bits = vi
        while bits:
            j = (bits & -bits).bit_length() - 1
            acc ^= M[j]
            bits &= bits - 1
        out[i] = acc
    return out


def _inv64(M):
    """Invert 64x64 GF(2) matrix. Returns (inv, rank)."""
    A = M.copy()
    I = np.zeros(64, dtype=np.uint64)
    for i in range(64):
        I[i] = np.uint64(1 << i)
    rank = 0
    for col in range(64):
        mask = np.uint64(1 << col)
        piv = -1
        for row in range(rank, 64):
            if A[row] & mask:
                piv = row
                break
        if piv == -1:
            continue
        if piv != rank:
            A[piv], A[rank] = A[rank].copy(), A[piv].copy()
            I[piv], I[rank] = I[rank].copy(), I[piv].copy()
        for row in range(64):
            if row != rank and (A[row] & mask):
                A[row] ^= A[rank]
                I[row] ^= I[rank]
        rank += 1
    return I, rank


def _find_Si(VtV):
    """Column subspace selector. Returns (S, rank)."""
    A = VtV.copy()
    rank = 0
    pivots = []
    for col in range(64):
        mask = np.uint64(1 << col)
        piv = -1
        for row in range(rank, 64):
            if A[row] & mask:
                piv = row
                break
        if piv == -1:
            continue
        pivots.append(col)
        if piv != rank:
            A[piv], A[rank] = A[rank].copy(), A[piv].copy()
        for row in range(64):
            if row != rank and (A[row] & mask):
                A[row] ^= A[rank]
        rank += 1
    S = np.zeros(64, dtype=np.uint64)
    for c in pivots:
        S[c] = np.uint64(1 << c)
    return S, rank


def _winv(VtV, S):
    """
    Compute W-inverse: the pseudo-inverse of VtV restricted to S subspace.
    Since VtV is symmetric over GF(2) and S selects the non-degenerate part,
    we compute (S * VtV * S)^{-1} projected through S.
    """
    # Restrict: form S * VtV * S
    SVS = _mul64(S, _mul64(VtV, S))
    inv, _ = _inv64(SVS)
    # Project: S * inv * S
    return _mul64(S, _mul64(inv, S))


def block_lanczos(sparse_rows, ncols, verbose=False):
    """
    Montgomery's Block Lanczos over GF(2).

    Finds row dependencies of sparse GF(2) matrix B (nrows x ncols).
    Works on A = B * B^T (symmetric, nrows x nrows).

    The key identity: if A*x = 0 then ||B^T x||^2 = x^T A x = 0,
    so B^T x = 0 (over GF(2), since x^T A x = (B^T x)^T (B^T x)).

    Returns list of kernel vectors (sorted lists of row indices).
    """
    nrows = len(sparse_rows)
    rp, ci = _build_csr(sparse_rows, ncols)

    if verbose:
        nnz = int(rp[-1])
        print(f"    BL: {nrows}x{ncols}, nnz={nnz}, w={nnz/max(nrows,1):.1f}")

    max_iter = nrows // 64 + 128

    # Random start
    rng = np.random.RandomState(12345)
    Y = np.zeros(nrows, dtype=np.uint64)
    for i in range(nrows):
        Y[i] = np.uint64(int(rng.randint(0, 2**32)) | (int(rng.randint(0, 2**32)) << 32))

    # V_0 = A * Y
    Vi = _BBt(rp, ci, nrows, ncols, Y)
    V0 = Vi.copy()

    # We need to track the FULL linear combination that produces the answer.
    # x_acc will accumulate contributions so that A * x_acc = V_0 projected
    # onto the Krylov subspace. At convergence, any bit-column where the
    # residual A*x_acc XOR V0 projected is zero gives a kernel vector.
    #
    # Actually, the correct formula from Montgomery:
    # Let W_i = V_i^T * V_i, D_i = S_i * W_i^{-1} (pseudo).
    # x = SUM_i  V_i * D_i * V_i^T * V_0
    # Then A*x = V_0 (projected).
    # The KERNEL vectors come from bit-columns of x where V_0's
    # corresponding column is zero (i.e., the projection killed it).
    #
    # More precisely: define z = x XOR Y. Then A*z should be zero
    # for the columns where the Krylov subspace captured everything.
    # But this is still tricky.
    #
    # Simpler correct approach (Villard 1997):
    # Track S = SUM_i V_i * D_i * V_i^T as a linear map from nrows -> nrows.
    # Then S * A * S = S (idempotent on Krylov subspace).
    # Kernel = {y : A*y = 0} = {S*v : A*S*v = 0 for random v}.
    #
    # In practice: accumulate x = SUM V_i D_i VitV0, then check A*x vs V0.
    # The zero bit-columns of (A*x XOR V0) give kernel directions.
    # Then x restricted to those bit-columns are kernel vectors.

    x_acc = np.zeros(nrows, dtype=np.uint64)
    Vi_prev = np.zeros(nrows, dtype=np.uint64)
    prev_Winv = None

    for it in range(max_iter):
        VtV = _inner(Vi, Vi, nrows)
        S, s_rank = _find_Si(VtV)

        if s_rank == 0:
            if verbose:
                print(f"    BL: converged at iter {it}")
            break

        Winv = _winv(VtV, S)

        # Accumulate: x += Vi * D * Vi^T * V0 where D = Winv
        VtV0 = _inner(Vi, V0, nrows)
        coeff = _mul64(Winv, VtV0)
        x_acc ^= _apply(Vi, coeff, nrows)

        # Next iterate: V_{i+1} = A*Vi*S - Vi*Ei - V_{i-1}*Fi
        AViS = _BBt(rp, ci, nrows, ncols, _apply(Vi, S, nrows))

        # Ei = Winv * Vi^T * A*Vi*S
        VtAVS = _inner(Vi, AViS, nrows)
        Ei = _mul64(Winv, VtAVS)
        Vi_next = AViS ^ _apply(Vi, Ei, nrows)

        # Fi correction from previous
        if it > 0 and prev_Winv is not None:
            VptAVS = _inner(Vi_prev, AViS, nrows)
            Fi = _mul64(prev_Winv, VptAVS)
            Vi_next ^= _apply(Vi_prev, Fi, nrows)

        prev_Winv = Winv
        Vi_prev = Vi.copy()
        Vi = Vi_next

        if verbose and (it + 1) % 50 == 0:
            print(f"    BL: iter {it+1}/{max_iter}, rank={s_rank}")

    # Check residual: r = A*x XOR V0. Bit-columns where r=0 give kernel directions.
    # But actually we want kernel of A, not A*x=V0.
    # The correct extraction: compute A * x_acc. For any bit-column b where
    # (A * x_acc)[i] == V0[i] for all i, that column is "solved".
    # The kernel comes from: (x_acc XOR Y) for those columns where
    # the entire V0 column was in the Krylov subspace.
    # If V0 column b was entirely spanned, then A*(x_acc col b) = V0 col b = A*Y col b,
    # so A*(x_acc XOR Y) col b = 0.

    Ax = _BBt(rp, ci, nrows, ncols, x_acc)
    residual = Ax ^ V0

    # Find zero bit-columns of residual
    res_or = np.uint64(0)
    for i in range(nrows):
        res_or |= residual[i]
    res_or_int = int(res_or)

    # z = x_acc XOR Y — kernel vector candidates
    z = x_acc ^ Y

    kernel_vecs = []
    for bit in range(64):
        if res_or_int & (1 << bit):
            continue  # residual nonzero in this column
        mask = 1 << bit
        indices = [i for i in range(nrows) if int(z[i]) & mask]
        if not indices:
            continue
        # Verify
        combined = set()
        for idx in indices:
            combined.symmetric_difference_update(sparse_rows[idx])
        if not combined:
            kernel_vecs.append(sorted(indices))

    if verbose:
        zero_cols = 64 - bin(res_or_int).count('1')
        print(f"    BL: {zero_cols} zero residual cols, {len(kernel_vecs)} verified kernel vecs")

    return kernel_vecs


###############################################################################
# Unified interface for GNFS
###############################################################################

def gf2_block_lanczos(relations, ncols_rat, ncols_alg, num_qc=0, num_sq=0,
                       num_lp=0, verbose=False):
    """
    Drop-in replacement for gf2_gaussian_elimination in gnfs_engine.py.
    Uses sparse_gauss for matrices up to ~50K rows, block_lanczos above that.
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

    # Renumber columns
    all_cols = set()
    for row in reduced_rows:
        all_cols.update(row)
    col_list = sorted(all_cols)
    col_map = {c: i for i, c in enumerate(col_list)}
    n_reduced_cols = len(col_list)
    n_reduced_rows = len(reduced_rows)

    if verbose:
        print(f"    LA post-SGE: {n_reduced_rows} x {n_reduced_cols}")

    remapped = [{col_map[c] for c in row} for row in reduced_rows]

    # Choose method based on matrix size
    if n_reduced_rows < 50000:
        raw_vecs = sparse_gauss(remapped, n_reduced_cols, verbose=verbose)
    else:
        raw_vecs = block_lanczos(remapped, n_reduced_cols, verbose=verbose)

    # Map through SGE compositions
    for indices in raw_vecs:
        original = set()
        for ri in indices:
            if ri < len(compositions):
                original.symmetric_difference_update(compositions[ri])
        if original:
            null_vecs.append(sorted(original))

    return null_vecs


###############################################################################
# Test utilities
###############################################################################

def _verify(sparse_rows, vecs):
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
    rng = np.random.RandomState(seed)
    rows = []
    for _ in range(nrows):
        w = max(1, rng.poisson(avg_w))
        rows.append(set(rng.choice(ncols, size=min(w, ncols), replace=False).tolist()))
    return rows


###############################################################################
# Main: correctness tests and benchmarks
###############################################################################

if __name__ == "__main__":
    print("=" * 60)
    print("Block Lanczos / Sparse Gauss over GF(2) — Tests")
    print("=" * 60)

    # --- sparse_gauss correctness ---

    print("\n=== sparse_gauss tests ===")

    # Test 1: Known null vector
    print("\n--- SG Test 1: 4x3 ---")
    rows = [{0, 2}, {1, 2}, {0, 1}, {0, 1, 2}]
    vecs = sparse_gauss(rows, 3, verbose=True)
    good = _verify(rows, vecs)
    print(f"  {len(vecs)} vectors, {good} verified")
    for v in vecs:
        print(f"    {v}")

    # Test 2: 200x180
    print("\n--- SG Test 2: 200x180, w=10 ---")
    rows = _rand_sparse(200, 180, 10, seed=10)
    t0 = time.time()
    vecs = sparse_gauss(rows, 180, verbose=True)
    dt = time.time() - t0
    good = _verify(rows, vecs)
    print(f"  {len(vecs)} vectors, {good} verified, {dt:.2f}s")

    # Test 3: 1000x950
    print("\n--- SG Test 3: 1000x950, w=15 ---")
    rows = _rand_sparse(1000, 950, 15, seed=20)
    t0 = time.time()
    vecs = sparse_gauss(rows, 950, verbose=True)
    dt = time.time() - t0
    good = _verify(rows, vecs)
    print(f"  {len(vecs)} vectors, {good} verified, {dt:.2f}s")

    # Test 4: 5000x4900
    print("\n--- SG Test 4: 5000x4900, w=20 ---")
    rows = _rand_sparse(5000, 4900, 20, seed=30)
    t0 = time.time()
    vecs = sparse_gauss(rows, 4900, verbose=True)
    dt = time.time() - t0
    good = _verify(rows, vecs)
    print(f"  {len(vecs)} vectors, {good} verified, {dt:.2f}s")

    # --- block_lanczos correctness ---

    print("\n=== block_lanczos tests ===")

    # BL Test 1: 200x180
    print("\n--- BL Test 1: 200x180, w=10 ---")
    rows = _rand_sparse(200, 180, 10, seed=10)
    t0 = time.time()
    vecs = block_lanczos(rows, 180, verbose=True)
    dt = time.time() - t0
    good = _verify(rows, vecs)
    print(f"  {len(vecs)} vectors, {good} verified, {dt:.2f}s")

    # BL Test 2: 1000x950
    print("\n--- BL Test 2: 1000x950, w=15 ---")
    rows = _rand_sparse(1000, 950, 15, seed=20)
    t0 = time.time()
    vecs = block_lanczos(rows, 950, verbose=True)
    dt = time.time() - t0
    good = _verify(rows, vecs)
    print(f"  {len(vecs)} vectors, {good} verified, {dt:.2f}s")

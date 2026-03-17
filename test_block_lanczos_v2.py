#!/usr/bin/env python3
"""Test Block Lanczos v2 against C Gauss for correctness and performance."""

import numpy as np
import ctypes
import os
import time
import sys

# Load both libraries
_dir = os.path.dirname(os.path.abspath(__file__))

def _load(name):
    path = os.path.join(_dir, name)
    if not os.path.exists(path):
        print(f"  {path} not found!")
        return None
    lib = ctypes.CDLL(path)
    return lib

lib_v1 = _load("block_lanczos_c.so")
lib_v2 = _load("block_lanczos_v2.so")

def sparse_to_csr(sparse_rows):
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

def decode_deps(deps_buf, ndeps, nrows):
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

def verify(sparse_rows, vecs):
    good = 0
    for vec in vecs:
        combined = set()
        for idx in vec:
            if idx < len(sparse_rows):
                combined.symmetric_difference_update(sparse_rows[idx])
        if not combined:
            good += 1
    return good

def run_gauss(lib, sparse_rows, ncols):
    nrows = len(sparse_rows)
    row_ptr, col_idx, nnz = sparse_to_csr(sparse_rows)
    max_deps = nrows
    nwords_dep = (nrows + 63) // 64
    deps_buf = (ctypes.c_uint64 * (max_deps * nwords_dep))()
    t0 = time.time()
    ndeps = lib.gauss_gf2_c(row_ptr, col_idx, nrows, ncols, deps_buf, max_deps)
    dt = time.time() - t0
    if ndeps < 0:
        return None, dt
    return decode_deps(deps_buf, ndeps, nrows), dt

def run_bl_v1(lib, sparse_rows, ncols):
    nrows = len(sparse_rows)
    row_ptr, col_idx, nnz = sparse_to_csr(sparse_rows)
    max_deps = min(256, nrows)
    nwords_dep = (nrows + 63) // 64
    deps_buf = (ctypes.c_uint64 * (max_deps * nwords_dep))()
    t0 = time.time()
    ndeps = lib.block_lanczos(row_ptr, col_idx, nrows, ncols, deps_buf, max_deps)
    dt = time.time() - t0
    if ndeps < 0:
        return None, dt
    return decode_deps(deps_buf, ndeps, nrows), dt

def run_bl_v2(lib, sparse_rows, ncols):
    nrows = len(sparse_rows)
    row_ptr, col_idx, nnz = sparse_to_csr(sparse_rows)
    max_deps = min(256, nrows)
    nwords_dep = (nrows + 63) // 64
    deps_buf = (ctypes.c_uint64 * (max_deps * nwords_dep))()
    t0 = time.time()
    ndeps = lib.block_lanczos_v2(row_ptr, col_idx, nrows, ncols, deps_buf, max_deps)
    dt = time.time() - t0
    if ndeps < 0:
        return None, dt
    return decode_deps(deps_buf, ndeps, nrows), dt

def rand_sparse(nrows, ncols, avg_w, seed=42):
    rng = np.random.RandomState(seed)
    rows = []
    for _ in range(nrows):
        w = max(1, rng.poisson(avg_w))
        rows.append(set(rng.choice(ncols, size=min(w, ncols), replace=False).tolist()))
    return rows

def make_known_null(nrows, ncols, avg_w, seed=42):
    """Create a matrix with a guaranteed null space by making some rows XOR-dependent."""
    rng = np.random.RandomState(seed)
    rows = []
    # First make independent rows
    for _ in range(nrows - 5):
        w = max(1, rng.poisson(avg_w))
        rows.append(set(rng.choice(ncols, size=min(w, ncols), replace=False).tolist()))
    # Now add 5 rows that are XOR combos of earlier rows
    for i in range(5):
        src = rng.choice(len(rows), size=rng.randint(2, 5), replace=False)
        combined = set()
        for s in src:
            combined.symmetric_difference_update(rows[s])
        rows.append(combined)
    return rows

# ======================================================================
print("=" * 70)
print("Block Lanczos v2 — Correctness and Performance Tests")
print("=" * 70)

# --- Test 1: Tiny known null space ---
print("\n--- Test 1: 4x3 known null space ---")
rows = [{0, 2}, {1, 2}, {0, 1}, {0, 1, 2}]
# Rows 0+1+2 = {0,2}^{1,2}^{0,1} = {} (null vec)
# Rows 0+1+3 = {0,2}^{1,2}^{0,1,2} = {0,1,2}^{0,1,2} ... let me check
# Actually row3 = row0 ^ row1 ^ row2: {0,2}^{1,2}^{0,1} = {0,1,2}^{0,1} = {2}. No.
# Let's just test what Gauss finds.

if lib_v1:
    vecs, dt = run_gauss(lib_v1, rows, 3)
    if vecs is not None:
        good = verify(rows, vecs)
        print(f"  Gauss:     {len(vecs)} vecs, {good} verified, {dt:.6f}s")

if lib_v2:
    vecs, dt = run_bl_v2(lib_v2, rows, 3)
    if vecs is not None:
        good = verify(rows, vecs)
        print(f"  BL v2:     {len(vecs)} vecs, {good} verified, {dt:.6f}s")
    else:
        print(f"  BL v2:     None (failed)")

# --- Test 2: Matrices with guaranteed null space ---
print("\n--- Test 2: Matrices with guaranteed null space ---")
for nr, nc, w, seed in [(50, 40, 8, 100), (100, 80, 10, 101), (200, 180, 12, 102)]:
    rows = make_known_null(nr, nc, w, seed=seed)
    print(f"\n  {nr}x{nc}, w~{w}:")

    if lib_v1:
        vecs_g, dt_g = run_gauss(lib_v1, rows, nc)
        good_g = verify(rows, vecs_g) if vecs_g else 0
        n_g = len(vecs_g) if vecs_g else 0
        print(f"    Gauss:     {n_g:3d} vecs, {good_g:3d} verified, {dt_g:.4f}s")

    if lib_v2:
        vecs_bl, dt_bl = run_bl_v2(lib_v2, rows, nc)
        good_bl = verify(rows, vecs_bl) if vecs_bl else 0
        n_bl = len(vecs_bl) if vecs_bl else 0
        print(f"    BL v2:     {n_bl:3d} vecs, {good_bl:3d} verified, {dt_bl:.4f}s")

# --- Test 3: Scaling benchmark ---
print("\n--- Test 3: Scaling benchmark ---")
sizes = [
    (200,  180,  10, 10),
    (500,  480,  15, 11),
    (1000, 950,  15, 20),
    (2000, 1900, 20, 25),
    (5000, 4900, 20, 30),
    (10000, 9800, 25, 40),
]

for nr, nc, w, seed in sizes:
    rows = rand_sparse(nr, nc, w, seed=seed)
    print(f"\n  {nr}x{nc}, w~{w}:")

    # Gauss (skip if too large)
    if lib_v1 and nr <= 10000:
        vecs_g, dt_g = run_gauss(lib_v1, rows, nc)
        good_g = verify(rows, vecs_g) if vecs_g else 0
        n_g = len(vecs_g) if vecs_g else 0
        tag_g = "OK" if good_g == n_g else f"FAIL({good_g}/{n_g})"
        print(f"    Gauss:     {n_g:4d} vecs, {good_g:4d} good [{tag_g}], {dt_g:.3f}s")

    if lib_v1:
        vecs_bl1, dt_bl1 = run_bl_v1(lib_v1, rows, nc)
        good_bl1 = verify(rows, vecs_bl1) if vecs_bl1 else 0
        n_bl1 = len(vecs_bl1) if vecs_bl1 else 0
        tag_bl1 = "OK" if good_bl1 == n_bl1 else f"FAIL({good_bl1}/{n_bl1})"
        print(f"    BL v1:     {n_bl1:4d} vecs, {good_bl1:4d} good [{tag_bl1}], {dt_bl1:.3f}s")

    if lib_v2:
        vecs_bl2, dt_bl2 = run_bl_v2(lib_v2, rows, nc)
        good_bl2 = verify(rows, vecs_bl2) if vecs_bl2 else 0
        n_bl2 = len(vecs_bl2) if vecs_bl2 else 0
        tag_bl2 = "OK" if good_bl2 == n_bl2 else f"FAIL({good_bl2}/{n_bl2})"
        print(f"    BL v2:     {n_bl2:4d} vecs, {good_bl2:4d} good [{tag_bl2}], {dt_bl2:.3f}s")

# --- Test 4: Large matrices (BL only) ---
print("\n--- Test 4: Large matrix test (BL v2 only) ---")
for nr, nc, w, seed in [(20000, 19800, 25, 50), (50000, 49800, 30, 60)]:
    rows = rand_sparse(nr, nc, w, seed=seed)
    print(f"\n  {nr}x{nc}, w~{w}:")

    if lib_v2:
        vecs_bl2, dt_bl2 = run_bl_v2(lib_v2, rows, nc)
        good_bl2 = verify(rows, vecs_bl2) if vecs_bl2 else 0
        n_bl2 = len(vecs_bl2) if vecs_bl2 else 0
        tag_bl2 = "OK" if good_bl2 == n_bl2 else f"FAIL({good_bl2}/{n_bl2})"
        print(f"    BL v2:     {n_bl2:4d} vecs, {good_bl2:4d} good [{tag_bl2}], {dt_bl2:.3f}s")

print("\n" + "=" * 70)
print("Done.")

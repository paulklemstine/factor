#!/usr/bin/env python3
"""Test Block Wiedemann (64-parallel) vs scalar Wiedemann for correctness and speed."""

import numpy as np
import ctypes
import os
import time
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from block_lanczos import (
    _load_lib, _sparse_to_csr, _decode_deps, _verify, _rand_sparse,
    block_lanczos_solve, block_wiedemann_solve, _c_gauss
)


def run_fn(fn_name, sparse_rows, ncols):
    lib = _load_lib()
    nrows = len(sparse_rows)
    row_ptr, col_idx, nnz = _sparse_to_csr(sparse_rows)
    max_deps = min(256, nrows)
    nwords_dep = (nrows + 63) // 64
    deps_buf = (ctypes.c_uint64 * (max_deps * nwords_dep))()
    fn = getattr(lib, fn_name)
    t0 = time.time()
    ndeps = fn(row_ptr, col_idx, nrows, ncols, deps_buf, max_deps)
    dt = time.time() - t0
    if ndeps < 0:
        return None, dt
    return _decode_deps(deps_buf, ndeps, nrows), dt


print("=" * 70)
print("Block Wiedemann (64-parallel) vs Scalar Wiedemann -- Test Suite")
print("=" * 70)

lib = _load_lib()
has_bw = lib is not None and hasattr(lib, 'block_wiedemann')
print(f"Library loaded: {lib is not None}")
print(f"block_wiedemann available: {has_bw}")

if not has_bw:
    print("FATAL: block_wiedemann not found in .so")
    sys.exit(1)

# ---- Test 1: Tiny known null space ----
print("\n--- Test 1: 4x3 known null space ---")
rows = [{0, 2}, {1, 2}, {0, 1}, {0, 1, 2}]
for name in ["gauss_gf2_c", "block_lanczos_v2", "block_wiedemann"]:
    vecs, dt = run_fn(name, rows, 3)
    if vecs is None:
        print(f"  {name:20s}: None")
        continue
    good = _verify(rows, vecs)
    print(f"  {name:20s}: {len(vecs)} vecs, {good} verified")

# ---- Test 2: Correctness across multiple seeds ----
print("\n--- Test 2: Correctness (multiple seeds) ---")
all_ok = True
for nr, nc, w in [(100, 80, 10), (500, 480, 15), (1000, 950, 15)]:
    for seed in range(42, 52):
        rows = _rand_sparse(nr, nc, w, seed=seed)
        vecs, dt = run_fn("block_wiedemann", rows, nc)
        good = _verify(rows, vecs) if vecs else 0
        n = len(vecs) if vecs else 0
        if good != n or n == 0:
            print(f"  FAIL: {nr}x{nc} seed={seed}: {n} vecs, {good} good")
            all_ok = False
if all_ok:
    print("  All correctness tests passed (100x80, 500x480, 1000x950 x 10 seeds each)")

# ---- Test 3: Scaling benchmark ----
print("\n--- Test 3: Scaling benchmark ---")
print(f"{'Size':>12s} | {'Scalar':>8s} | {'Block':>8s} | {'Spd':>5s} | B-vecs")
print("-" * 55)

sizes = [
    (1000, 950, 15, 20),
    (2000, 1900, 20, 25),
    (5000, 4900, 20, 30),
]

for nr, nc, w, seed in sizes:
    rows = _rand_sparse(nr, nc, w, seed=seed)

    vs, dts = run_fn("block_lanczos_v2", rows, nc)
    ns = len(vs) if vs else 0

    vb, dtb = run_fn("block_wiedemann", rows, nc)
    nb = len(vb) if vb else 0
    gb = _verify(rows, vb) if vb else 0

    spd = dts / dtb if dtb > 0 else 0
    ok = "OK" if gb == nb and nb > 0 else f"FAIL({gb}/{nb})"
    print(f"{nr:5d}x{nc:<5d} | {dts:6.2f}s | {dtb:6.2f}s | {spd:4.1f}x | {nb:3d} [{ok}]")
    sys.stdout.flush()

# 10K: block only (scalar too slow for test suite)
print("\n--- Block Wiedemann only (10K) ---")
rows = _rand_sparse(10000, 9800, 25, seed=40)
vb, dtb = run_fn("block_wiedemann", rows, 9800)
nb = len(vb) if vb else 0
gb = _verify(rows, vb) if vb else 0
ok = "OK" if gb == nb and nb > 0 else f"FAIL({gb}/{nb})"
print(f"10000x9800  | {dtb:6.2f}s | {nb:3d} vecs [{ok}]")

print("\n" + "=" * 70)
print("Done.")

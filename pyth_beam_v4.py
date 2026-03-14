#!/usr/bin/env python3
"""
Pythagorean Tree Factoring — v4 with full C beam search

Entire beam search loop runs in C (pyth_beam_c.so):
  - Hash-table dedup
  - Matrix multiply + scent + GCD
  - Diversified selection + restarts
"""

import ctypes
import random
import time
import os
from math import gcd

# === Load C extension ===
_dir = os.path.dirname(os.path.abspath(__file__))
_lib = ctypes.CDLL(os.path.join(_dir, "pyth_beam_c.so"))

_lib.beam_search_full.restype = ctypes.c_uint64
_lib.beam_search_full.argtypes = [
    ctypes.c_uint64,                   # N
    ctypes.POINTER(ctypes.c_int),      # matrices
    ctypes.c_int,                      # n_mat
    ctypes.c_int,                      # beam_width
    ctypes.c_int,                      # max_steps
    ctypes.c_int,                      # time_limit_ms
    ctypes.c_int,                      # n_clusters
    ctypes.c_int,                      # diversity_frac (percent)
    ctypes.c_int,                      # restart_patience
    ctypes.c_uint64,                   # seed
    ctypes.POINTER(ctypes.c_int),      # steps_out
    ctypes.POINTER(ctypes.c_int),      # nodes_out
]

# === Matrices ===
BERGGREN = [
    [( 1,-2, 2), ( 2,-1, 2), ( 2,-2, 3)],
    [( 1, 2, 2), ( 2, 1, 2), ( 2, 2, 3)],
    [(-1, 2, 2), (-2, 1, 2), (-2, 2, 3)],
]
PRICE = [
    [( 1, 0, 0), ( 2, 1, 0), ( 2, 0, 1)],
    [(-1, 0, 2), (-2, 1, 2), (-2, 0, 3)],
    [( 1, 0, 2), ( 2, 1, 2), ( 2, 0, 3)],
]
UNIQUE_MATRICES = BERGGREN + PRICE

def mat_inverse_3x3(M):
    a, b, c = M[0]; d, e, f = M[1]; g, h, i_ = M[2]
    det = a*(e*i_ - f*h) - b*(d*i_ - f*g) + c*(d*h - e*g)
    if abs(det) != 1: return None
    return [
        [det*(e*i_ - f*h), det*(c*h - b*i_), det*(b*f - c*e)],
        [det*(f*g - d*i_), det*(a*i_ - c*g), det*(c*d - a*f)],
        [det*(d*h - e*g), det*(b*g - a*h), det*(a*e - b*d)],
    ]

INVERSE_MATRICES = [mat_inverse_3x3(M) for M in UNIQUE_MATRICES]
ALL_MATRICES = UNIQUE_MATRICES + INVERSE_MATRICES[:3]
N_MATRICES = len(ALL_MATRICES)

def _matrices_to_c():
    flat = []
    for M in ALL_MATRICES:
        for row in M:
            for val in row:
                flat.append(int(val))
    return (ctypes.c_int * len(flat))(*flat)

C_MATRICES = _matrices_to_c()

# === Primality ===
def miller_rabin(n, witnesses=(2,3,5,7,11,13,17,19,23,29,31,37)):
    if n < 2: return False
    if n in (2, 3): return True
    if n % 2 == 0: return False
    r, d = 0, n - 1
    while d % 2 == 0: r += 1; d //= 2
    for a in witnesses:
        if a >= n: continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1: continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1: break
        else: return False
    return True

def generate_semiprime(bits_per_factor, seed=None):
    if seed is not None: random.seed(seed)
    while True:
        p = random.getrandbits(bits_per_factor) | (1 << (bits_per_factor - 1)) | 1
        if miller_rabin(p): break
    while True:
        q = random.getrandbits(bits_per_factor) | (1 << (bits_per_factor - 1)) | 1
        if q != p and miller_rabin(q): break
    return min(p, q), max(p, q), p * q


def beam_search_c(N, beam_width=500, max_steps=20000, time_limit=60.0,
                  n_clusters=12, diversity_pct=25, restart_patience=8, seed=None):
    """Full C beam search. N must fit in uint64."""
    if N >= (1 << 64):
        raise ValueError("N too large for C uint64 path")

    if seed is None:
        seed = random.getrandbits(64)

    steps_out = ctypes.c_int(0)
    nodes_out = ctypes.c_int(0)

    factor = _lib.beam_search_full(
        ctypes.c_uint64(N),
        C_MATRICES,
        ctypes.c_int(N_MATRICES),
        ctypes.c_int(beam_width),
        ctypes.c_int(max_steps),
        ctypes.c_int(int(time_limit * 1000)),
        ctypes.c_int(n_clusters),
        ctypes.c_int(diversity_pct),
        ctypes.c_int(restart_patience),
        ctypes.c_uint64(seed),
        ctypes.byref(steps_out),
        ctypes.byref(nodes_out),
    )

    return int(factor) if factor > 0 else None, steps_out.value, nodes_out.value


_lib.beam_search_forward.restype = ctypes.c_uint64
_lib.beam_search_forward.argtypes = [
    ctypes.c_uint64, ctypes.POINTER(ctypes.c_int), ctypes.c_int,
    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
    ctypes.c_int, ctypes.c_int, ctypes.c_uint64,
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
]

# Forward-only matrices (no inverses)
def _forward_matrices_to_c():
    flat = []
    for M in UNIQUE_MATRICES:  # 6 forward matrices only
        for row in M:
            for val in row:
                flat.append(int(val))
    return (ctypes.c_int * len(flat))(*flat)

C_FORWARD_MATRICES = _forward_matrices_to_c()
N_FORWARD = len(UNIQUE_MATRICES)  # 6


def beam_search_forward(N, beam_width=500, max_steps=50000, time_limit=120.0,
                        n_clusters=12, diversity_pct=25, restart_patience=8, seed=None):
    """Forward-only beam search. No dedup, no memory limit."""
    if N >= (1 << 64):
        raise ValueError("N too large for uint64")
    if seed is None:
        seed = random.getrandbits(64)

    steps_out = ctypes.c_int(0)
    nodes_out = ctypes.c_int(0)

    factor = _lib.beam_search_forward(
        ctypes.c_uint64(N),
        C_FORWARD_MATRICES, ctypes.c_int(N_FORWARD),
        ctypes.c_int(beam_width), ctypes.c_int(max_steps),
        ctypes.c_int(int(time_limit * 1000)),
        ctypes.c_int(n_clusters), ctypes.c_int(diversity_pct),
        ctypes.c_int(restart_patience), ctypes.c_uint64(seed),
        ctypes.byref(steps_out), ctypes.byref(nodes_out),
    )
    return int(factor) if factor > 0 else None, steps_out.value, nodes_out.value


def run_test(bits_list, n_trials=15, beam_width=500, max_steps=20000,
             time_limit=60.0, label="v4_C"):
    print(f"{'Bits':>5} | {label:>16} | {'nodes/trial':>12} | {'time/trial':>10}")
    print("-" * 60)

    results = {}
    for bits in bits_list:
        solved = 0
        total_nodes = 0
        total_time = 0.0

        for trial in range(n_trials):
            p, q, N = generate_semiprime(bits, seed=42 + trial)
            t0 = time.time()
            f, steps, nodes = beam_search_c(
                N, beam_width=beam_width, max_steps=max_steps,
                time_limit=time_limit, seed=42 + trial
            )
            elapsed = time.time() - t0
            total_time += elapsed
            total_nodes += nodes
            if f and 1 < f < N: solved += 1

        avg_nodes = total_nodes // n_trials
        avg_time = total_time / n_trials
        throughput = total_nodes / total_time if total_time > 0 else 0
        results[bits] = solved
        print(f"{bits:>5} | {solved:>7}/{n_trials:<8} | {avg_nodes:>10,} | {avg_time:>8.2f}s  ({throughput:,.0f} n/s)")

    return results


def factor_pythagorean(N, time_limit=60.0, beam_width=500, seed=None):
    """
    Factor N using Pythagorean tree beam search.
    Best method: forward-only diversified beam with C acceleration.
    Returns factor or None.
    """
    if seed is None:
        seed = random.getrandbits(64)
    max_steps = int(time_limit * 3000)  # ~3K steps/sec
    f, _, _ = beam_search_forward(N, beam_width=beam_width,
                                   max_steps=max_steps, time_limit=time_limit,
                                   seed=seed)
    return f


if __name__ == "__main__":
    import sys
    print("Pythagorean Tree Factoring — v4 (C-accelerated forward beam)")
    print("=" * 60)

    # Throughput
    print("\n--- Throughput ---")
    for bits in [24, 28, 32]:
        _, _, N = generate_semiprime(bits, seed=999)
        t0 = time.time()
        f, steps, nodes = beam_search_forward(N, beam_width=500,
                                               max_steps=10000, time_limit=15.0, seed=999)
        elapsed = time.time() - t0
        print(f"  {bits}b: {nodes:,} nodes in {elapsed:.2f}s = {nodes/elapsed:,.0f} n/s"
              f"  {'FOUND' if f else 'miss'}", flush=True)

    # Main benchmark
    for bits, tlimit in [(20, 10), (24, 30), (28, 60), (32, 180)]:
        n_trials = 15
        solved = 0
        total_nodes = 0
        total_time = 0.0
        print(f"\n--- {bits}b (beam=500, {tlimit}s) ---", flush=True)
        for trial in range(n_trials):
            p, q, N = generate_semiprime(bits, seed=42 + trial)
            t0 = time.time()
            f, steps, nodes = beam_search_forward(
                N, beam_width=500, max_steps=200000,
                time_limit=float(tlimit), seed=42 + trial
            )
            elapsed = time.time() - t0
            total_time += elapsed
            total_nodes += nodes
            ok = f and 1 < f < N
            if ok: solved += 1
            print(f"  t{trial:>2}: {'Y' if ok else 'n'}  {nodes:>12,}n  {elapsed:>6.1f}s", flush=True)
        avg_tput = total_nodes / total_time if total_time > 0 else 0
        print(f"  {bits}b: {solved}/{n_trials}  ({avg_tput:,.0f} nodes/sec avg)", flush=True)

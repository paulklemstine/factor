#!/usr/bin/env python3
"""Test the C-accelerated Pythagorean heuristic search."""

import ctypes
import random
import time
import os

_dir = os.path.dirname(os.path.abspath(__file__))
_lib = ctypes.CDLL(os.path.join(_dir, "pyth_heuristic_c.so"))

# beam_restart
_lib.pyth_beam_restart.restype = ctypes.c_uint64
_lib.pyth_beam_restart.argtypes = [
    ctypes.c_uint64,  # N
    ctypes.c_int,     # beam_width
    ctypes.c_int,     # max_steps
    ctypes.c_int,     # time_limit_ms
    ctypes.c_int,     # restart_patience
    ctypes.c_uint64,  # seed
    ctypes.POINTER(ctypes.c_int),  # nodes_out
    ctypes.POINTER(ctypes.c_int),  # restarts_out
]

# greedy_restart
_lib.pyth_greedy_restart.restype = ctypes.c_uint64
_lib.pyth_greedy_restart.argtypes = [
    ctypes.c_uint64,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_uint64,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
]


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

def gen_semi(bits, seed=None):
    if seed is not None: random.seed(seed)
    while True:
        p = random.getrandbits(bits) | (1 << (bits-1)) | 1
        if miller_rabin(p): break
    while True:
        q = random.getrandbits(bits) | (1 << (bits-1)) | 1
        if q != p and miller_rabin(q): break
    return min(p,q), max(p,q), p*q


def beam_restart(N, beam_width=50, max_steps=500000, time_limit=60.0,
                 restart_patience=300, seed=None):
    if seed is None: seed = random.getrandbits(64)
    nodes_out = ctypes.c_int(0)
    restarts_out = ctypes.c_int(0)
    f = _lib.pyth_beam_restart(
        ctypes.c_uint64(N), ctypes.c_int(beam_width),
        ctypes.c_int(max_steps), ctypes.c_int(int(time_limit * 1000)),
        ctypes.c_int(restart_patience), ctypes.c_uint64(seed),
        ctypes.byref(nodes_out), ctypes.byref(restarts_out)
    )
    return int(f) if f > 0 else None, nodes_out.value, restarts_out.value


def greedy_restart(N, max_steps=2000000, time_limit=60.0,
                   restart_patience=200, seed=None):
    if seed is None: seed = random.getrandbits(64)
    nodes_out = ctypes.c_int(0)
    restarts_out = ctypes.c_int(0)
    f = _lib.pyth_greedy_restart(
        ctypes.c_uint64(N), ctypes.c_int(max_steps),
        ctypes.c_int(int(time_limit * 1000)),
        ctypes.c_int(restart_patience), ctypes.c_uint64(seed),
        ctypes.byref(nodes_out), ctypes.byref(restarts_out)
    )
    return int(f) if f > 0 else None, nodes_out.value, restarts_out.value


if __name__ == "__main__":
    print("Pythagorean Heuristic Search — C Engine Benchmark")
    print("=" * 60)

    # Throughput test
    print("\n--- Throughput ---")
    for bits in [20, 24, 28]:
        _, _, N = gen_semi(bits, seed=999)
        t0 = time.time()
        f, nodes, restarts = beam_restart(N, beam_width=50, max_steps=100000,
                                           time_limit=5.0, seed=999)
        elapsed = time.time() - t0
        tput = nodes / elapsed if elapsed > 0 else 0
        print(f"  {bits}b: {nodes:>10,} nodes in {elapsed:.2f}s = {tput:>12,.0f} n/s  "
              f"{'FOUND' if f else 'miss'}  ({restarts} restarts)")

    # Main benchmark
    for bits, tlimit, bw in [(20, 10, 50), (24, 30, 50), (28, 60, 80), (32, 180, 100)]:
        n_trials = 15
        print(f"\n--- {bits}b beam_restart (bw={bw}, {tlimit}s) ---")

        solved = 0
        total_nodes = 0
        total_time = 0.0
        for trial in range(n_trials):
            p, q, N = gen_semi(bits, seed=42 + trial)
            t0 = time.time()
            f, nodes, restarts = beam_restart(N, beam_width=bw,
                                               max_steps=5000000,
                                               time_limit=float(tlimit),
                                               seed=42 + trial)
            elapsed = time.time() - t0
            total_time += elapsed
            total_nodes += nodes
            ok = f and 1 < f < N
            if ok: solved += 1
            print(f"  t{trial:>2}: {'Y' if ok else 'n'}  {nodes:>12,}n  {elapsed:>6.1f}s  "
                  f"{restarts}r", flush=True)

        tput = total_nodes / total_time if total_time > 0 else 0
        print(f"  {bits}b: {solved}/{n_trials}  ({tput:,.0f} n/s avg)")

    # Greedy comparison at 24b
    print(f"\n--- 24b greedy_restart (30s) ---")
    solved = 0
    total_nodes = 0
    total_time = 0.0
    for trial in range(15):
        p, q, N = gen_semi(24, seed=42 + trial)
        t0 = time.time()
        f, nodes, restarts = greedy_restart(N, max_steps=5000000,
                                             time_limit=30.0, seed=42+trial)
        elapsed = time.time() - t0
        total_time += elapsed
        total_nodes += nodes
        ok = f and 1 < f < N
        if ok: solved += 1
        print(f"  t{trial:>2}: {'Y' if ok else 'n'}  {nodes:>12,}n  {elapsed:>6.1f}s  "
              f"{restarts}r", flush=True)
    tput = total_nodes / total_time if total_time > 0 else 0
    print(f"  24b greedy: {solved}/15  ({tput:,.0f} n/s avg)")

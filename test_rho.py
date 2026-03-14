#!/usr/bin/env python3
"""Test projective Pollard-rho on Pythagorean tree."""

import ctypes, random, time, os, math

_dir = os.path.dirname(os.path.abspath(__file__))
_lib = ctypes.CDLL(os.path.join(_dir, "pyth_rho_c.so"))

# Projective rho (1D walk, expected O(sqrt(p)))
_lib.projective_rho.restype = ctypes.c_uint64
_lib.projective_rho.argtypes = [
    ctypes.c_uint64, ctypes.c_uint64, ctypes.c_int, ctypes.c_int,
    ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint64)
]

# Multi-start projective rho
_lib.multi_projective_rho.restype = ctypes.c_uint64
_lib.multi_projective_rho.argtypes = [
    ctypes.c_uint64, ctypes.c_int, ctypes.c_uint64, ctypes.c_int, ctypes.c_int,
    ctypes.POINTER(ctypes.c_uint64)
]

# 2D rho (expected O(p), for comparison)
_lib.twod_rho.restype = ctypes.c_uint64
_lib.twod_rho.argtypes = [
    ctypes.c_uint64, ctypes.c_uint64, ctypes.c_int, ctypes.c_int,
    ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint64)
]

# Projective rho + derived values
_lib.projective_rho_plus.restype = ctypes.c_uint64
_lib.projective_rho_plus.argtypes = [
    ctypes.c_uint64, ctypes.c_uint64, ctypes.c_int, ctypes.c_int,
    ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint64)
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


if __name__ == "__main__":
    print("=" * 75)
    print("Pythagorean Tree — Projective Pollard-Rho Factoring")
    print("=" * 75)

    TRIALS = 15
    TIME_MS = 30000  # 30s per trial

    # ---- Scaling test: how do steps scale with factor size? ----
    print("\n--- SCALING TEST: Steps vs factor size ---")
    print(f"{'bits':>5s} {'method':>14s} {'solved':>7s} {'avg_steps':>12s} {'sqrt(p)':>10s} {'ratio':>8s} {'time':>8s}")
    print("-" * 75)

    for bits in [10, 12, 14, 16, 18, 20, 24, 28, 32]:
        sqrtp = int(math.isqrt(2**bits))
        max_steps = min(500_000_000, 200 * (2**bits))

        for method_name, method_fn in [
            ("proj_rho", lambda N, seed: _lib.projective_rho(
                ctypes.c_uint64(N), ctypes.c_uint64(max_steps),
                ctypes.c_int(TIME_MS), ctypes.c_int(200),
                ctypes.c_uint64(seed), ctypes.byref(steps))),
            ("2d_rho", lambda N, seed: _lib.twod_rho(
                ctypes.c_uint64(N), ctypes.c_uint64(max_steps),
                ctypes.c_int(TIME_MS), ctypes.c_int(200),
                ctypes.c_uint64(seed), ctypes.byref(steps))),
            ("proj_plus", lambda N, seed: _lib.projective_rho_plus(
                ctypes.c_uint64(N), ctypes.c_uint64(max_steps),
                ctypes.c_int(TIME_MS), ctypes.c_int(200),
                ctypes.c_uint64(seed), ctypes.byref(steps))),
        ]:
            solved = 0
            total_steps = 0
            total_time = 0.0
            steps = ctypes.c_uint64(0)

            for trial in range(TRIALS):
                p, q, N = gen_semi(bits, seed=42+trial)
                t0 = time.time()
                f = int(method_fn(N, 42 + trial))
                elapsed = time.time() - t0
                total_time += elapsed
                s = int(steps.value)
                total_steps += s
                if f > 1 and f < N:
                    solved += 1

            avg_s = total_steps // TRIALS
            ratio = avg_s / sqrtp if sqrtp > 0 else 0
            avg_t = total_time / TRIALS
            print(f"{2*bits:>5d} {method_name:>14s} {solved:>3d}/{TRIALS:<3d} {avg_s:>12,} {sqrtp:>10,} {ratio:>8.1f} {avg_t:>7.3f}s")

    # ---- Multi-start test ----
    print("\n--- MULTI-START PROJECTIVE RHO ---")
    for bits in [16, 20, 24, 28, 32]:
        solved = 0
        total_steps = 0
        steps = ctypes.c_uint64(0)
        for trial in range(TRIALS):
            p, q, N = gen_semi(bits, seed=42+trial)
            t0 = time.time()
            f = int(_lib.multi_projective_rho(
                ctypes.c_uint64(N), ctypes.c_int(100),
                ctypes.c_uint64(min(10_000_000, 100*(2**bits))),
                ctypes.c_int(TIME_MS), ctypes.c_int(200),
                ctypes.byref(steps)))
            elapsed = time.time() - t0
            s = int(steps.value)
            total_steps += s
            if f > 1 and f < N:
                solved += 1
        avg_s = total_steps // TRIALS
        sqrtp = int(math.isqrt(2**bits))
        print(f"  {2*bits}b: {solved}/{TRIALS}  avg_steps={avg_s:>12,}  sqrt(p)={sqrtp:>8,}  ratio={avg_s/sqrtp:.1f}")

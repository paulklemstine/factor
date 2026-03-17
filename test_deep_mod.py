#!/usr/bin/env python3
"""Test deep modular Pythagorean tree experiments."""

import ctypes, random, time, os

_dir = os.path.dirname(os.path.abspath(__file__))
_lib = ctypes.CDLL(os.path.join(_dir, "pyth_deep_mod.so"))

# Experiment 1: Deep random walk
_lib.deep_random_walk.restype = ctypes.c_uint64
_lib.deep_random_walk.argtypes = [
    ctypes.c_uint64, ctypes.c_uint64, ctypes.c_int, ctypes.c_int,
    ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint64)
]

# Experiment 2: Brent cycle detection
_lib.brent_cycle_detect.restype = ctypes.c_uint64
_lib.brent_cycle_detect.argtypes = [
    ctypes.c_uint64, ctypes.c_int, ctypes.c_uint64, ctypes.c_int,
    ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64)
]

# Experiment 3: Matrix power jump
_lib.matrix_power_jump.restype = ctypes.c_uint64
_lib.matrix_power_jump.argtypes = [
    ctypes.c_uint64, ctypes.c_int, ctypes.POINTER(ctypes.c_uint64)
]

# Experiment 4: Smooth exponent attack
_lib.smooth_exponent_attack.restype = ctypes.c_uint64
_lib.smooth_exponent_attack.argtypes = [
    ctypes.c_uint64, ctypes.c_int, ctypes.POINTER(ctypes.c_uint64)
]

# Experiment 5: Parametric family
_lib.parametric_family.restype = ctypes.c_uint64
_lib.parametric_family.argtypes = [
    ctypes.c_uint64, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_uint64)
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
    print("Pythagorean Tree — Deep Modular Experiments")
    print("=" * 60)

    # ---- Experiment 3: Matrix Power Jump (instant, try first) ----
    print("\n--- EXP 3: Matrix Power Jump M^(2^k), k=0..50 ---")
    for bits in [20, 24, 28, 32, 40, 48]:
        solved = 0
        for trial in range(15):
            p, q, N = gen_semi(bits, seed=42+trial)
            steps = ctypes.c_uint64(0)
            f = _lib.matrix_power_jump(ctypes.c_uint64(N), ctypes.c_int(50),
                                        ctypes.byref(steps))
            f = int(f)
            if f > 1 and f < N: solved += 1
        print(f"  {bits}b: {solved}/15  ({int(steps.value)} total steps)", flush=True)

    # ---- Experiment 4: Smooth Exponent Attack (Williams p+1 style) ----
    print("\n--- EXP 4: Smooth Exponent (9 matrices, B1=1000) ---")
    for bits in [20, 24, 28, 32, 40, 48]:
        solved = 0
        for trial in range(15):
            p, q, N = gen_semi(bits, seed=42+trial)
            steps = ctypes.c_uint64(0)
            f = _lib.smooth_exponent_attack(ctypes.c_uint64(N), ctypes.c_int(1000),
                                             ctypes.byref(steps))
            f = int(f)
            if f > 1 and f < N: solved += 1
        print(f"  {bits}b: {solved}/15  (~{int(steps.value)} steps)", flush=True)

    # With larger bound
    print("\n--- EXP 4b: Smooth Exponent (B1=10000) ---")
    for bits in [20, 24, 28, 32, 40, 48]:
        solved = 0
        for trial in range(15):
            p, q, N = gen_semi(bits, seed=42+trial)
            steps = ctypes.c_uint64(0)
            f = _lib.smooth_exponent_attack(ctypes.c_uint64(N), ctypes.c_int(10000),
                                             ctypes.byref(steps))
            f = int(f)
            if f > 1 and f < N: solved += 1
        print(f"  {bits}b: {solved}/15  (~{int(steps.value)} steps)", flush=True)

    # ---- Experiment 5: Parametric Family ----
    print("\n--- EXP 5: Parametric M(t)=[[t,1],[1,0]], t=1..500, B1=1000 ---")
    for bits in [20, 24, 28, 32, 40, 48]:
        solved = 0
        for trial in range(15):
            p, q, N = gen_semi(bits, seed=42+trial)
            steps = ctypes.c_uint64(0)
            f = _lib.parametric_family(ctypes.c_uint64(N), ctypes.c_int(500),
                                        ctypes.c_int(1000), ctypes.byref(steps))
            f = int(f)
            if f > 1 and f < N: solved += 1
        print(f"  {bits}b: {solved}/15  (~{int(steps.value)} steps)", flush=True)

    # ---- Experiment 1: Deep Random Walk (throughput king) ----
    print("\n--- EXP 1: Deep Random Walk + Batched GCD ---")
    for bits, tlimit in [(20, 5), (24, 10), (28, 30), (32, 60)]:
        solved = 0
        total_steps = 0
        total_time = 0.0
        for trial in range(15):
            p, q, N = gen_semi(bits, seed=42+trial)
            steps = ctypes.c_uint64(0)
            t0 = time.time()
            f = _lib.deep_random_walk(
                ctypes.c_uint64(N), ctypes.c_uint64(500000000),
                ctypes.c_int(tlimit * 1000), ctypes.c_int(500),
                ctypes.c_uint64(42 + trial), ctypes.byref(steps)
            )
            elapsed = time.time() - t0
            f = int(f)
            total_steps += int(steps.value)
            total_time += elapsed
            ok = f > 1 and f < N
            if ok: solved += 1
            print(f"  t{trial:>2}: {'Y' if ok else 'n'}  {int(steps.value):>12,} steps  "
                  f"{elapsed:>5.1f}s", flush=True)
        tput = total_steps / total_time if total_time > 0 else 0
        print(f"  {bits}b: {solved}/15  ({tput:,.0f} steps/s avg)")

    # ---- Experiment 2: Brent Cycle Detection ----
    print("\n--- EXP 2: Brent Cycle Detection (per matrix, 30s each) ---")
    for bits in [24, 28, 32]:
        solved = 0
        for trial in range(5):
            p, q, N = gen_semi(bits, seed=42+trial)
            for mi in range(9):
                steps = ctypes.c_uint64(0)
                period = ctypes.c_uint64(0)
                f = _lib.brent_cycle_detect(
                    ctypes.c_uint64(N), ctypes.c_int(mi),
                    ctypes.c_uint64(100000000), ctypes.c_int(5000),
                    ctypes.c_uint64(42), ctypes.byref(steps), ctypes.byref(period)
                )
                f = int(f)
                if f > 1 and f < N:
                    solved += 1
                    print(f"  {bits}b t{trial} M{mi}: FOUND at step {int(steps.value):,} "
                          f"period~{int(period.value):,}", flush=True)
                    break
            else:
                print(f"  {bits}b t{trial}: no factor (9 matrices tried)", flush=True)
        print(f"  {bits}b: {solved}/5")

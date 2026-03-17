#!/usr/bin/env python3
"""
Benchmark suite for Pythagorean tree hybrid factoring approaches.

Tests 4 approaches at 20b, 24b, 28b, 32b, 40b, 48b:
  1. smooth_stage2   — Stage 1 + ECM-style Stage 2
  2. multi_curve     — Many random matrices + smooth exponent + batch GCD
  3. smooth_walk     — Smooth warm-start + random walk continuation
  4. combined_attack — All-in-one (Stage1 + Stage2 + walk on many curves)

Also compares with the baseline smooth_exponent_attack and parametric_family
from pyth_deep_mod.c.
"""

import ctypes
import os
import random
import time
from math import gcd

# --- Load shared libraries ---
HERE = os.path.dirname(os.path.abspath(__file__))

lib_hybrid = ctypes.CDLL(os.path.join(HERE, "pyth_hybrid_c.so"))

# Try to load baseline for comparison
try:
    lib_baseline = ctypes.CDLL(os.path.join(HERE, "pyth_deep_mod.so"))
    HAS_BASELINE = True
except OSError:
    # Try to compile it
    base_c = os.path.join(HERE, "pyth_deep_mod.c")
    base_so = os.path.join(HERE, "pyth_deep_mod.so")
    if os.path.exists(base_c):
        os.system(f"gcc -O3 -march=native -shared -fPIC -o {base_so} {base_c} -lm")
        try:
            lib_baseline = ctypes.CDLL(base_so)
            HAS_BASELINE = True
        except OSError:
            HAS_BASELINE = False
    else:
        HAS_BASELINE = False

# --- C function signatures ---
# smooth_stage2(N, B1, B2, t_max, *steps) -> factor
lib_hybrid.smooth_stage2.argtypes = [
    ctypes.c_uint64, ctypes.c_int, ctypes.c_int, ctypes.c_int,
    ctypes.POINTER(ctypes.c_uint64)
]
lib_hybrid.smooth_stage2.restype = ctypes.c_uint64

# multi_curve_smooth(N, num_curves, B1, seed, *steps) -> factor
lib_hybrid.multi_curve_smooth.argtypes = [
    ctypes.c_uint64, ctypes.c_int, ctypes.c_int, ctypes.c_uint64,
    ctypes.POINTER(ctypes.c_uint64)
]
lib_hybrid.multi_curve_smooth.restype = ctypes.c_uint64

# smooth_then_walk(N, B1, walk_steps, num_starts, seed, *steps) -> factor
lib_hybrid.smooth_then_walk.argtypes = [
    ctypes.c_uint64, ctypes.c_int, ctypes.c_uint64, ctypes.c_int, ctypes.c_uint64,
    ctypes.POINTER(ctypes.c_uint64)
]
lib_hybrid.smooth_then_walk.restype = ctypes.c_uint64

# combined_attack(N, B1, B2, num_random, walk_steps, seed, *steps) -> factor
lib_hybrid.combined_attack.argtypes = [
    ctypes.c_uint64, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint64,
    ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint64)
]
lib_hybrid.combined_attack.restype = ctypes.c_uint64

# combined_timed(N, B1, B2, t_max, num_random, walk_steps, time_limit_ms, seed, *steps)
lib_hybrid.combined_timed.argtypes = [
    ctypes.c_uint64, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
    ctypes.c_uint64, ctypes.c_int, ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint64)
]
lib_hybrid.combined_timed.restype = ctypes.c_uint64

if HAS_BASELINE:
    lib_baseline.smooth_exponent_attack.argtypes = [
        ctypes.c_uint64, ctypes.c_int, ctypes.POINTER(ctypes.c_uint64)
    ]
    lib_baseline.smooth_exponent_attack.restype = ctypes.c_uint64

    lib_baseline.parametric_family.argtypes = [
        ctypes.c_uint64, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_uint64)
    ]
    lib_baseline.parametric_family.restype = ctypes.c_uint64


# --- Helpers ---

def miller_rabin(n, witnesses=(2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)):
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
        else:
            return False
    return True


def gen_semi(bits, seed=None):
    """Generate a semiprime with two balanced primes of 'bits' bits each."""
    rng = random.Random(seed)
    while True:
        p = rng.getrandbits(bits) | (1 << (bits - 1)) | 1
        if miller_rabin(p): break
    while True:
        q = rng.getrandbits(bits) | (1 << (bits - 1)) | 1
        if q != p and miller_rabin(q): break
    return min(p, q), max(p, q), p * q


def verify_factor(N, f, p, q):
    """Check if f is a valid nontrivial factor of N."""
    if f == 0:
        return False
    return f > 1 and f < N and N % f == 0


# --- Parameters per bit-size ---
def get_params(bits):
    """Return tuned parameters per size.
    Key insight: at small sizes the walk component dominates, at larger sizes
    we need more curves and higher B1/B2 to catch smooth-period orbits."""
    if bits <= 20:
        return dict(B1=100, B2=500, num_curves=100, walk_steps=5000,
                    num_starts=50, t_max=100, time_ms=2000)
    elif bits <= 24:
        return dict(B1=200, B2=2000, num_curves=200, walk_steps=20000,
                    num_starts=100, t_max=200, time_ms=5000)
    elif bits <= 28:
        return dict(B1=500, B2=5000, num_curves=500, walk_steps=100000,
                    num_starts=200, t_max=300, time_ms=10000)
    elif bits <= 32:
        return dict(B1=1000, B2=20000, num_curves=1000, walk_steps=500000,
                    num_starts=500, t_max=500, time_ms=20000)
    elif bits <= 40:
        return dict(B1=5000, B2=50000, num_curves=2000, walk_steps=1000000,
                    num_starts=800, t_max=1000, time_ms=30000)
    else:  # 48b
        return dict(B1=10000, B2=100000, num_curves=3000, walk_steps=2000000,
                    num_starts=1000, t_max=1000, time_ms=60000)


# --- Run one approach on a set of semiprimes ---
def bench_approach(name, func, semiprimes, bits):
    """Run func on each semiprime, return (solved, total, avg_time, avg_steps)."""
    solved = 0
    total = len(semiprimes)
    times = []
    all_steps = []

    for i, (p, q, N) in enumerate(semiprimes):
        steps = ctypes.c_uint64(0)
        t0 = time.time()
        f = func(N, steps)
        elapsed = time.time() - t0
        times.append(elapsed)
        all_steps.append(steps.value)

        ok = verify_factor(N, f, p, q)
        if ok:
            solved += 1

    avg_t = sum(times) / total if total > 0 else 0
    avg_s = sum(all_steps) / total if total > 0 else 0
    return solved, total, avg_t, avg_s


def run_benchmark(bits_list, n_trials=15):
    """Run all approaches at each bit size."""
    print("=" * 90)
    print(f"  Pythagorean Hybrid Factoring Benchmark — {n_trials} trials per bit-size")
    print("=" * 90)

    # Collect results for summary table
    all_results = {}

    for bits in bits_list:
        print(f"\n{'─' * 90}")
        print(f"  {bits}b semiprimes (each prime ~{bits}b, product ~{2*bits}b)")
        print(f"{'─' * 90}")

        # Generate semiprimes
        semiprimes = [gen_semi(bits, seed=42 + i) for i in range(n_trials)]

        params = get_params(bits)
        B1 = params['B1']
        B2 = params['B2']
        num_curves = params['num_curves']
        walk_steps = params['walk_steps']
        num_starts = params['num_starts']
        t_max = params['t_max']
        time_ms = params['time_ms']

        print(f"  Params: B1={B1}, B2={B2}, curves={num_curves}, "
              f"walk={walk_steps}, starts={num_starts}, t_max={t_max}, time={time_ms}ms")

        results = {}

        # --- Baseline: smooth_exponent_attack (Stage 1 only, 9 matrices) ---
        if HAS_BASELINE:
            def run_baseline(N, steps):
                return lib_baseline.smooth_exponent_attack(N, B1, ctypes.byref(steps))
            s, t, at, ast = bench_approach("baseline_smooth", run_baseline, semiprimes, bits)
            results["Baseline smooth(9 mat)"] = (s, t, at, ast)
            print(f"  {'Baseline smooth(9 mat)':<30}  {s:>2}/{t}  avg {at:.4f}s  {ast:.0f} steps")

        # --- Baseline: parametric family ---
        if HAS_BASELINE:
            def run_parametric(N, steps):
                return lib_baseline.parametric_family(N, t_max, B1, ctypes.byref(steps))
            s, t, at, ast = bench_approach("baseline_param", run_parametric, semiprimes, bits)
            results["Baseline param(t_max)"] = (s, t, at, ast)
            print(f"  {'Baseline param(t_max)':<30}  {s:>2}/{t}  avg {at:.4f}s  {ast:.0f} steps")

        # --- Approach 1: Smooth + Stage 2 ---
        def run_stage2(N, steps):
            return lib_hybrid.smooth_stage2(N, B1, B2, t_max, ctypes.byref(steps))
        s, t, at, ast = bench_approach("smooth_stage2", run_stage2, semiprimes, bits)
        results["1. Smooth + Stage2"] = (s, t, at, ast)
        print(f"  {'1. Smooth + Stage2':<30}  {s:>2}/{t}  avg {at:.4f}s  {ast:.0f} steps")

        # --- Approach 2: Multi-curve smooth ---
        def run_multi(N, steps):
            return lib_hybrid.multi_curve_smooth(N, num_curves, B1, 12345, ctypes.byref(steps))
        s, t, at, ast = bench_approach("multi_curve", run_multi, semiprimes, bits)
        results["2. Multi-curve smooth"] = (s, t, at, ast)
        print(f"  {'2. Multi-curve smooth':<30}  {s:>2}/{t}  avg {at:.4f}s  {ast:.0f} steps")

        # --- Approach 3: Smooth + walk ---
        def run_walk(N, steps):
            return lib_hybrid.smooth_then_walk(N, B1, walk_steps, num_starts, 67890, ctypes.byref(steps))
        s, t, at, ast = bench_approach("smooth_walk", run_walk, semiprimes, bits)
        results["3. Smooth + walk"] = (s, t, at, ast)
        print(f"  {'3. Smooth + walk':<30}  {s:>2}/{t}  avg {at:.4f}s  {ast:.0f} steps")

        # --- Approach 4: Combined (no time limit) ---
        def run_combined(N, steps):
            return lib_hybrid.combined_attack(
                N, B1, B2, max(50, num_curves // 4),
                min(walk_steps, 50000), 11111, ctypes.byref(steps)
            )
        s, t, at, ast = bench_approach("combined", run_combined, semiprimes, bits)
        results["4. Combined attack"] = (s, t, at, ast)
        print(f"  {'4. Combined attack':<30}  {s:>2}/{t}  avg {at:.4f}s  {ast:.0f} steps")

        # --- Approach 5: Combined timed (best effort within time budget) ---
        def run_timed(N, steps):
            return lib_hybrid.combined_timed(
                N, B1, B2, t_max, num_curves, walk_steps,
                time_ms, 11111, ctypes.byref(steps)
            )
        s, t, at, ast = bench_approach("combined_timed", run_timed, semiprimes, bits)
        results["5. Combined timed"] = (s, t, at, ast)
        print(f"  {'5. Combined timed':<30}  {s:>2}/{t}  avg {at:.4f}s  {ast:.0f} steps")

        all_results[bits] = results

    # --- Summary table ---
    print(f"\n{'=' * 90}")
    print("  SUMMARY: Solved / Total")
    print(f"{'=' * 90}")

    approaches = []
    if HAS_BASELINE:
        approaches += ["Baseline smooth(9 mat)", "Baseline param(t_max)"]
    approaches += ["1. Smooth + Stage2", "2. Multi-curve smooth",
                    "3. Smooth + walk", "4. Combined attack", "5. Combined timed"]

    header = f"  {'Approach':<30}"
    for b in bits_list:
        header += f"  {b:>4}b"
    print(header)
    print("  " + "-" * (30 + 7 * len(bits_list)))

    for approach in approaches:
        row = f"  {approach:<30}"
        for b in bits_list:
            if b in all_results and approach in all_results[b]:
                s, t, _, _ = all_results[b][approach]
                row += f"  {s:>2}/{t}"
            else:
                row += f"  {'--':>5}"
        print(row)

    # --- Timing table ---
    print(f"\n  Average time (seconds):")
    header = f"  {'Approach':<30}"
    for b in bits_list:
        header += f"  {b:>6}b"
    print(header)
    print("  " + "-" * (30 + 9 * len(bits_list)))

    for approach in approaches:
        row = f"  {approach:<30}"
        for b in bits_list:
            if b in all_results and approach in all_results[b]:
                _, _, at, _ = all_results[b][approach]
                row += f"  {at:>6.3f}s"
            else:
                row += f"  {'--':>7}"
        print(row)

    print()


if __name__ == "__main__":
    import sys
    # Default: 20b, 24b, 28b, 32b, 40b, 48b
    bits_list = [20, 24, 28, 32, 40, 48]
    n_trials = 15

    if len(sys.argv) > 1:
        bits_list = [int(b) for b in sys.argv[1].split(",")]
    if len(sys.argv) > 2:
        n_trials = int(sys.argv[2])

    run_benchmark(bits_list, n_trials)

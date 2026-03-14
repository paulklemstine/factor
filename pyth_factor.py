#!/usr/bin/env python3
"""
Unified Pythagorean Tree Factoring Driver.

Strategy:
  1. Smooth exponent attack (free, catches p±1 smooth factors) — B1=1000
  2. Multi-GCD birthday collision (K parallel walks, pairwise GCD) — main workhorse
"""

import ctypes, os, time, random, math, sys

_dir = os.path.dirname(os.path.abspath(__file__))

# Load C libraries
_birthday = ctypes.CDLL(os.path.join(_dir, "pyth_birthday_c.so"))
_deep = ctypes.CDLL(os.path.join(_dir, "pyth_deep_mod.so"))

# Bind smooth_exponent_attack(N, B1, steps_out) -> u64
_deep.smooth_exponent_attack.restype = ctypes.c_uint64
_deep.smooth_exponent_attack.argtypes = [
    ctypes.c_uint64, ctypes.c_int, ctypes.POINTER(ctypes.c_uint64)
]

# Bind birthday_multi_gcd(N, num_walks, max_steps, seed, time_limit_ms, total_steps) -> u64
_birthday.birthday_multi_gcd.restype = ctypes.c_uint64
_birthday.birthday_multi_gcd.argtypes = [
    ctypes.c_uint64, ctypes.c_int, ctypes.c_uint64,
    ctypes.c_uint64, ctypes.c_int, ctypes.POINTER(ctypes.c_uint64)
]

# 128-bit extension (Montgomery-accelerated)
_birthday128 = ctypes.CDLL(os.path.join(_dir, "pyth_birthday128.so"))
_birthday128.birthday_multi_gcd_128.restype = ctypes.c_int
_birthday128.birthday_multi_gcd_128.argtypes = [
    ctypes.c_uint64, ctypes.c_uint64,  # N_hi, N_lo
    ctypes.c_int, ctypes.c_uint64, ctypes.c_uint64, ctypes.c_int,
    ctypes.POINTER(ctypes.c_uint64),   # total_steps
    ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64),  # factor_hi, factor_lo
]


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
        else: return False
    return True


def pyth_factor(N, time_limit_s=60, K=1024, B1=1000, verbose=True):
    """Factor N using Pythagorean tree methods.

    Returns (factor, method, elapsed) or (0, None, elapsed) if not found.
    """
    if N < 4:
        return 0, None, 0.0

    if N.bit_length() > 128:
        if verbose:
            print(f"  ERROR: N is {N.bit_length()} bits, exceeds 128-bit limit")
        return 0, "overflow", 0.0

    use_128 = N.bit_length() > 64

    # Trivial division
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31):
        if N % p == 0 and N // p > 1:
            return p, "trivial", 0.0

    # Check if prime
    if miller_rabin(N):
        return 0, "prime", 0.0

    t0 = time.time()

    # Phase 1: Smooth exponent (u64 only — skip for >64b N)
    if not use_128:
        steps = ctypes.c_uint64(0)
        f = int(_deep.smooth_exponent_attack(ctypes.c_uint64(N), ctypes.c_int(B1),
                                              ctypes.byref(steps)))
        elapsed = time.time() - t0
        if f > 1 and f < N:
            if verbose:
                print(f"  [smooth B1={B1}] Found {f} in {elapsed:.3f}s ({steps.value} steps)")
            return f, "smooth", elapsed
        if verbose:
            print(f"  [smooth B1={B1}] No factor ({elapsed:.3f}s)")

    elapsed = time.time() - t0

    # Phase 2: Multi-GCD birthday collision
    remaining_ms = int((time_limit_s - elapsed) * 1000)
    if remaining_ms < 100:
        return 0, None, time.time() - t0

    nb = N.bit_length()
    seed = random.getrandbits(64)
    total_steps = ctypes.c_uint64(0)

    if use_128:
        # 128-bit Montgomery path
        max_rounds = max(100_000, 2 ** (nb // 4))
        N_hi = (N >> 64) & ((1 << 64) - 1)
        N_lo = N & ((1 << 64) - 1)
        fac_hi = ctypes.c_uint64(0)
        fac_lo = ctypes.c_uint64(0)

        ok = _birthday128.birthday_multi_gcd_128(
            ctypes.c_uint64(N_hi), ctypes.c_uint64(N_lo),
            ctypes.c_int(K), ctypes.c_uint64(max_rounds),
            ctypes.c_uint64(seed), ctypes.c_int(remaining_ms),
            ctypes.byref(total_steps),
            ctypes.byref(fac_hi), ctypes.byref(fac_lo))

        f = (fac_hi.value << 64) | fac_lo.value
        elapsed = time.time() - t0
        if ok and f > 1 and f < N:
            if verbose:
                print(f"  [multi-GCD-128 K={K}] Found {f} in {elapsed:.3f}s "
                      f"({total_steps.value:,} steps)")
            return f, "multi-gcd-128", elapsed
    else:
        # 64-bit native path
        max_steps = max(10_000_000, K * (2 ** (nb // 4)))
        f = int(_birthday.birthday_multi_gcd(
            ctypes.c_uint64(N), ctypes.c_int(K), ctypes.c_uint64(max_steps),
            ctypes.c_uint64(seed), ctypes.c_int(remaining_ms),
            ctypes.byref(total_steps)))

        elapsed = time.time() - t0
        if f > 1 and f < N:
            if verbose:
                print(f"  [multi-GCD K={K}] Found {f} in {elapsed:.3f}s "
                      f"({total_steps.value:,} steps)")
            return f, "multi-gcd", elapsed

    if verbose:
        print(f"  [multi-GCD{'128' if use_128 else ''} K={K}] No factor ({elapsed:.3f}s, "
              f"{total_steps.value:,} steps)")
    return 0, None, elapsed


def gen_semi(bits, seed=None):
    """Generate balanced semiprime with given total bit length."""
    if seed is not None:
        random.seed(seed)
    half = bits // 2
    while True:
        p = random.getrandbits(half) | (1 << (half - 1)) | 1
        if not miller_rabin(p): continue
        q = random.getrandbits(bits - half) | (1 << (bits - half - 1)) | 1
        if q != p and miller_rabin(q):
            return min(p, q), max(p, q), p * q


# ---- CLI ----
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "bench":
        # Benchmark mode
        TRIALS = 15
        time_limit = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        bit_sizes = [32, 48, 56, 64, 72, 80]

        print("=" * 75)
        print("Pythagorean Tree Unified Factoring — Benchmark")
        print(f"Trials={TRIALS}, time_limit={time_limit}s per trial")
        print("=" * 75)
        print(f"{'bits':>5} {'solved':>7} {'smooth':>7} {'mgcd':>7} "
              f"{'avg_time':>10} {'med_time':>10}")
        print("-" * 60)

        for bits in bit_sizes:
            solved = 0
            smooth_count = 0
            mgcd_count = 0
            times = []

            K = min(2048, max(512, 2 ** (bits // 8 + 5)))

            for trial in range(TRIALS):
                p, q, N = gen_semi(bits, seed=42 + trial)
                f, method, elapsed = pyth_factor(
                    N, time_limit_s=time_limit, K=K, verbose=False)

                if f > 1 and f < N:
                    solved += 1
                    times.append(elapsed)
                    if method == "smooth":
                        smooth_count += 1
                    elif method == "multi-gcd":
                        mgcd_count += 1
                else:
                    times.append(time_limit)

            avg_t = sum(times) / len(times)
            med_t = sorted(times)[len(times) // 2]

            print(f"{bits:5d} {solved:3d}/{TRIALS:<3d} {smooth_count:3d}/{TRIALS:<3d} "
                  f"{mgcd_count:3d}/{TRIALS:<3d} {avg_t:9.2f}s {med_t:9.2f}s")

            sys.stdout.flush()

    elif len(sys.argv) > 1:
        # Factor a specific number
        N = int(sys.argv[1])
        tl = int(sys.argv[2]) if len(sys.argv) > 2 else 120
        print(f"Factoring N = {N} ({N.bit_length()}b)")
        f, method, elapsed = pyth_factor(N, time_limit_s=tl, K=2048)
        if f > 1:
            print(f"Result: {N} = {f} * {N // f}  [{method}, {elapsed:.3f}s]")
        else:
            print(f"No factor found in {elapsed:.1f}s")

    else:
        print("Usage:")
        print("  pyth_factor.py <N> [time_limit_s]  — factor a specific number")
        print("  pyth_factor.py bench [time_limit_s] — run scaling benchmark")

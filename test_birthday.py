"""
Test suite for Pythagorean tree multi-walk birthday collision factoring.

Benchmarks at 20b, 24b, 28b, 32b, 40b to measure scaling exponent.
If truly O(sqrt(p)), doubling bit size should ~2x the steps needed.
"""

import ctypes
import os
import time
import random
import math
import sys

# Load the C library
SO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pyth_birthday_c.so")
lib = ctypes.CDLL(SO_PATH)

# ---- Bind birthday_collision_factor ----
lib.birthday_collision_factor.restype = ctypes.c_uint64
lib.birthday_collision_factor.argtypes = [
    ctypes.c_uint64,    # N
    ctypes.c_int,       # num_walks
    ctypes.c_uint64,    # steps_per_walk
    ctypes.c_int,       # dp_bits
    ctypes.c_uint64,    # seed
    ctypes.c_int,       # time_limit_ms
    ctypes.POINTER(ctypes.c_uint64),  # total_steps
    ctypes.POINTER(ctypes.c_int),     # dp_count
    ctypes.POINTER(ctypes.c_int),     # collision_count
]

# ---- Bind birthday_rho_factor ----
lib.birthday_rho_factor.restype = ctypes.c_uint64
lib.birthday_rho_factor.argtypes = [
    ctypes.c_uint64,    # N
    ctypes.c_int,       # num_walks
    ctypes.c_uint64,    # max_steps
    ctypes.c_uint64,    # seed
    ctypes.c_int,       # time_limit_ms
    ctypes.POINTER(ctypes.c_uint64),  # total_steps
]

# ---- Bind birthday_multi_gcd ----
lib.birthday_multi_gcd.restype = ctypes.c_uint64
lib.birthday_multi_gcd.argtypes = [
    ctypes.c_uint64,    # N
    ctypes.c_int,       # num_walks
    ctypes.c_uint64,    # max_steps
    ctypes.c_uint64,    # seed
    ctypes.c_int,       # time_limit_ms
    ctypes.POINTER(ctypes.c_uint64),  # total_steps
]


def gen_semiprime(bits):
    """Generate a semiprime N = p * q where p, q are ~bits/2 each."""
    half = bits // 2
    while True:
        p = random.getrandbits(half) | (1 << (half - 1)) | 1
        q = random.getrandbits(bits - half) | (1 << (bits - half - 1)) | 1
        if p == q:
            continue
        # Check primality (probabilistic)
        if is_probably_prime(p) and is_probably_prime(q):
            N = p * q
            if N.bit_length() == bits or N.bit_length() == bits - 1:
                return N, min(p, q), max(p, q)


def is_probably_prime(n, k=20):
    """Miller-Rabin primality test."""
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    # Write n-1 as 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def test_method1_dp(N, p, q, bits, num_walks=64, steps=500000, dp_bits=8,
                     seed=12345, time_limit_ms=30000):
    """Test distinguished-point multi-walk birthday collision."""
    total_steps = ctypes.c_uint64(0)
    dp_count = ctypes.c_int(0)
    collision_count = ctypes.c_int(0)

    t0 = time.time()
    result = lib.birthday_collision_factor(
        ctypes.c_uint64(N),
        ctypes.c_int(num_walks),
        ctypes.c_uint64(steps),
        ctypes.c_int(dp_bits),
        ctypes.c_uint64(seed),
        ctypes.c_int(time_limit_ms),
        ctypes.byref(total_steps),
        ctypes.byref(dp_count),
        ctypes.byref(collision_count),
    )
    elapsed = time.time() - t0

    found = result > 0 and result < N and (N % result == 0)
    return {
        "method": "DP-birthday",
        "bits": bits,
        "found": found,
        "factor": result,
        "steps": total_steps.value,
        "time": elapsed,
        "dp_stored": dp_count.value,
        "collisions": collision_count.value,
        "steps_per_sec": total_steps.value / elapsed if elapsed > 0 else 0,
    }


def test_method2_rho(N, p, q, bits, num_walks=16, steps=2000000,
                      seed=12345, time_limit_ms=30000):
    """Test Pollard-rho style with Brent cycle detection on Pyth tree."""
    total_steps = ctypes.c_uint64(0)

    t0 = time.time()
    result = lib.birthday_rho_factor(
        ctypes.c_uint64(N),
        ctypes.c_int(num_walks),
        ctypes.c_uint64(steps),
        ctypes.c_uint64(seed),
        ctypes.c_int(time_limit_ms),
        ctypes.byref(total_steps),
    )
    elapsed = time.time() - t0

    found = result > 0 and result < N and (N % result == 0)
    return {
        "method": "Rho-birthday",
        "bits": bits,
        "found": found,
        "factor": result,
        "steps": total_steps.value,
        "time": elapsed,
        "steps_per_sec": total_steps.value / elapsed if elapsed > 0 else 0,
    }


def test_method3_multi_gcd(N, p, q, bits, num_walks=128, steps=2000000,
                            seed=12345, time_limit_ms=30000):
    """Test multi-walk pairwise GCD birthday."""
    total_steps = ctypes.c_uint64(0)

    t0 = time.time()
    result = lib.birthday_multi_gcd(
        ctypes.c_uint64(N),
        ctypes.c_int(num_walks),
        ctypes.c_uint64(steps),
        ctypes.c_uint64(seed),
        ctypes.c_int(time_limit_ms),
        ctypes.byref(total_steps),
    )
    elapsed = time.time() - t0

    found = result > 0 and result < N and (N % result == 0)
    return {
        "method": "Multi-GCD",
        "bits": bits,
        "found": found,
        "factor": result,
        "steps": total_steps.value,
        "time": elapsed,
        "steps_per_sec": total_steps.value / elapsed if elapsed > 0 else 0,
    }


def run_scaling_benchmark():
    """Run all three methods at multiple bit sizes and analyze scaling."""
    random.seed(42)

    bit_sizes = [20, 24, 28, 32, 40, 48, 52, 56]
    trials_per_size = 10
    time_limit = 60000  # 60s per trial max

    print("=" * 80)
    print("Pythagorean Tree Birthday Collision Factoring — Scaling Benchmark")
    print("=" * 80)
    print()

    all_results = {}

    # Scale parameters with bit size
    def dp_kwargs(bits):
        # More walks + steps for larger sizes; dp_bits scales with problem
        nw = max(32, bits * 4)
        steps = max(100000, 2 ** (bits // 2 + 6))
        dpb = max(4, bits // 4)
        return {"num_walks": nw, "steps": steps, "dp_bits": dpb,
                "time_limit_ms": time_limit}

    def rho_kwargs(bits):
        nw = max(8, bits)
        steps = max(100000, 2 ** (bits // 2 + 8))
        return {"num_walks": nw, "steps": steps, "time_limit_ms": time_limit}

    def multi_kwargs(bits):
        # Scale walks with sqrt of expected effort for birthday balance
        nw = max(32, min(1024, 2 ** (bits // 4 + 2)))
        steps = max(100000, 2 ** (bits // 2 + 8))
        return {"num_walks": nw, "steps": steps, "time_limit_ms": time_limit}

    for method_name, method_fn, kwfn in [
        ("DP-birthday", test_method1_dp, dp_kwargs),
        ("Rho-birthday", test_method2_rho, rho_kwargs),
        ("Multi-GCD", test_method3_multi_gcd, multi_kwargs),
    ]:
        kwargs = None  # will be set per bit size
        print(f"\n--- Method: {method_name} ---")
        print(f"{'Bits':>5} | {'Found':>5} | {'Steps':>12} | {'Time(s)':>8} | "
              f"{'Steps/sec':>12} | {'Extra'}")
        print("-" * 80)

        method_results = []
        for bits in bit_sizes:
            found_count = 0
            total_time = 0
            total_steps_sum = 0
            details = []

            for trial in range(trials_per_size):
                N, p, q = gen_semiprime(bits)
                seed = random.randint(1, 2**32)
                r = method_fn(N, p, q, bits, seed=seed, **kwfn(bits))
                if r["found"]:
                    found_count += 1
                total_time += r["time"]
                total_steps_sum += r["steps"]
                details.append(r)

            avg_steps = total_steps_sum / trials_per_size
            avg_time = total_time / trials_per_size
            avg_sps = avg_steps / avg_time if avg_time > 0 else 0

            extra = ""
            if method_name == "DP-birthday":
                avg_dp = sum(d.get("dp_stored", 0) for d in details) / trials_per_size
                avg_coll = sum(d.get("collisions", 0) for d in details) / trials_per_size
                extra = f"DPs={avg_dp:.0f} Colls={avg_coll:.1f}"

            print(f"{bits:5d} | {found_count:3d}/{trials_per_size} | "
                  f"{avg_steps:12.0f} | {avg_time:8.3f} | "
                  f"{avg_sps:12.0f} | {extra}")

            method_results.append({
                "bits": bits,
                "found_rate": found_count / trials_per_size,
                "avg_steps": avg_steps,
                "avg_time": avg_time,
            })

        all_results[method_name] = method_results

    # Scaling analysis
    print("\n" + "=" * 80)
    print("SCALING ANALYSIS")
    print("=" * 80)
    print()
    print("If O(sqrt(p)) ~ O(2^(bits/4)), then doubling bits should 4x steps.")
    print("If O(p) ~ O(2^(bits/2)), then doubling bits should sqrt(N)-scale steps.")
    print()

    for method_name, results in all_results.items():
        print(f"--- {method_name} ---")
        prev = None
        for r in results:
            if r["found_rate"] == 0:
                ratio = "N/A (no solutions)"
            elif prev and prev["found_rate"] > 0 and prev["avg_steps"] > 0:
                ratio = f"{r['avg_steps'] / prev['avg_steps']:.2f}x"
            else:
                ratio = "-"
            print(f"  {r['bits']:3d}b: avg {r['avg_steps']:12.0f} steps, "
                  f"{r['avg_time']:.3f}s, "
                  f"found {r['found_rate']*100:.0f}%, "
                  f"ratio vs prev: {ratio}")
            prev = r

        # Fit log-log scaling for successful runs
        successful = [(r["bits"], r["avg_steps"]) for r in results
                      if r["found_rate"] > 0 and r["avg_steps"] > 0]
        if len(successful) >= 2:
            # log(steps) = a * bits + b
            xs = [s[0] for s in successful]
            ys = [math.log2(s[1]) for s in successful]
            n = len(xs)
            sx = sum(xs)
            sy = sum(ys)
            sxy = sum(x * y for x, y in zip(xs, ys))
            sx2 = sum(x * x for x in xs)
            denom = n * sx2 - sx * sx
            if denom != 0:
                a = (n * sxy - sx * sy) / denom
                print(f"  Scaling exponent: steps ~ 2^({a:.3f} * bits)")
                print(f"  O(sqrt(p)) would be 0.25, O(p) would be 0.50")
        print()


def run_quick_test():
    """Quick sanity check that the methods work on small inputs."""
    print("Quick sanity tests...")
    random.seed(123)

    test_cases = [
        (3 * 5, 3, 5, 4),
        (7 * 11, 7, 11, 7),
        (101 * 103, 101, 103, 14),
        (1009 * 1013, 1009, 1013, 20),
        (10007 * 10009, 10007, 10009, 27),
    ]

    for N, p, q, bits in test_cases:
        for seed in range(1, 4):
            r1 = test_method1_dp(N, p, q, bits, num_walks=32, steps=500000,
                                  dp_bits=4, seed=seed, time_limit_ms=5000)
            r2 = test_method2_rho(N, p, q, bits, num_walks=8, steps=500000,
                                   seed=seed, time_limit_ms=5000)
            r3 = test_method3_multi_gcd(N, p, q, bits, num_walks=64,
                                         steps=500000, seed=seed,
                                         time_limit_ms=5000)

            found_any = r1["found"] or r2["found"] or r3["found"]
            methods = []
            if r1["found"]: methods.append(f"DP({r1['steps']})")
            if r2["found"]: methods.append(f"Rho({r2['steps']})")
            if r3["found"]: methods.append(f"Multi({r3['steps']})")

            status = "OK" if found_any else "MISS"
            print(f"  N={N:>12d} ({bits:2d}b) seed={seed}: "
                  f"{status:4s} {', '.join(methods) if methods else 'no method found factor'}")

    print()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        run_quick_test()
    elif len(sys.argv) > 1 and sys.argv[1] == "bench":
        run_scaling_benchmark()
    else:
        run_quick_test()
        run_scaling_benchmark()

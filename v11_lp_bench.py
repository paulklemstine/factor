#!/usr/bin/env python3
"""
v11 LP Resonance Benchmark
===========================
Tests SIQS with grouped a-selection (LP resonance) vs random a-selection.

Approach: Temporarily patch the grouped-mode constants in siqs_engine
before each run, then restore them. This avoids permanent changes until
we confirm improvement.

Runs are interleaved (baseline-grouped-baseline-grouped...) to reduce
bias from system load variation or thermal throttling.
"""

import time
import random
import sys
import os
import importlib

# Unbuffered output
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)
sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', buffering=1)

# Ensure we import from the right place
sys.path.insert(0, '/home/raver1975/factor')

from gmpy2 import next_prime, mpz

SRC_PATH = '/home/raver1975/factor/siqs_engine.py'

# Generate reproducible test semiprimes
def gen_semiprime(digits, seed):
    """Generate a semiprime with approximately `digits` total digits."""
    rng = random.Random(seed)
    half = digits // 2
    lo = mpz(10) ** (half - 1)
    hi = mpz(10) ** half
    p = next_prime(lo + mpz(rng.randint(0, int(hi - lo))))
    q = next_prime(lo + mpz(rng.randint(0, int(hi - lo))))
    while p == q:
        q = next_prime(q + 1)
    return int(p * q)


def patch_engine_grouped(grouped_ratio=0.6, group_size=15):
    """Patch siqs_engine.py to enable grouped a-selection with LP resonance."""
    with open(SRC_PATH, 'r') as f:
        src = f.read()

    src = src.replace(
        'use_grouped = False  # grouped_a and s >= 5 and (select_hi - select_lo) >= s * 4',
        'use_grouped = grouped_a and s >= 5 and (select_hi - select_lo) >= s * 4'
    )
    src = src.replace(
        'n_shared = max(2, s // 2)  # number of primes shared in base',
        'n_shared = s - 1  # number of primes shared in base (LP resonance)'
    )
    src = src.replace(
        "grouped_ratio = 0.5  # fraction of 'a' values using grouped selection",
        f"grouped_ratio = {grouped_ratio}  # fraction of 'a' values using grouped selection"
    )
    src = src.replace(
        'group_size = 10  # number of variants per base group',
        f'group_size = {group_size}  # number of variants per base group'
    )

    with open(SRC_PATH, 'w') as f:
        f.write(src)


def restore_engine(original_src):
    """Restore siqs_engine.py to original source."""
    with open(SRC_PATH, 'w') as f:
        f.write(original_src)


def run_siqs(n, verbose=False):
    """Run SIQS on n with whatever is currently in siqs_engine.py."""
    import siqs_engine
    importlib.reload(siqs_engine)

    t0 = time.time()
    result = siqs_engine.siqs_factor(n, verbose=verbose, n_workers=1, grouped_a=True)
    elapsed = time.time() - t0

    return {
        'time': elapsed,
        'factor': result,
        'success': result is not None and result > 1 and n % result == 0,
    }


def main():
    print("=" * 70)
    print("v11 LP Resonance Benchmark: Grouped vs Random a-selection")
    print("=" * 70)

    # Save original source
    with open(SRC_PATH, 'r') as f:
        original_src = f.read()

    # Test configs: use 51d, 54d, 57d for speed (2 each = 12 total runs)
    # 51d ~5s, 54d ~12s, 57d ~25s => baseline ~84s, grouped ~84s, total ~168s < 5min
    test_configs = [
        (51, 2),
        (54, 2),
        (57, 2),
        (60, 2),
    ]

    # Generate test numbers
    tests = []
    for digits, count in test_configs:
        for i in range(count):
            seed = digits * 1000 + i * 137 + 42
            n = gen_semiprime(digits, seed)
            nd = len(str(n))
            tests.append((nd, n, seed))

    print(f"\nTest semiprimes: {len(tests)} total")
    for nd, n, seed in tests:
        print(f"  {nd}d: {str(n)[:40]}...")

    # --- INTERLEAVED RUNS ---
    print("\n" + "=" * 70)
    print("INTERLEAVED RUNS (baseline then grouped for each number)")
    print("=" * 70)

    baseline_results = {}
    grouped_results = {}

    try:
        for nd, n, seed in tests:
            key = (nd, seed)
            print(f"\n--- {nd}d (seed={seed}) ---")

            # BASELINE
            restore_engine(original_src)
            print(f"  BASELINE: ", end="", flush=True)
            result_b = run_siqs(n, verbose=False)
            baseline_results[key] = result_b
            status = "OK" if result_b['success'] else "FAIL"
            print(f"{status} in {result_b['time']:.1f}s")

            # GROUPED
            patch_engine_grouped(grouped_ratio=0.6, group_size=15)
            print(f"  GROUPED:  ", end="", flush=True)
            result_g = run_siqs(n, verbose=False)
            grouped_results[key] = result_g
            status = "OK" if result_g['success'] else "FAIL"
            speedup = result_b['time'] / result_g['time'] if result_g['time'] > 0 else float('inf')
            print(f"{status} in {result_g['time']:.1f}s  (speedup: {speedup:.2f}x)")

    finally:
        # ALWAYS restore original source
        restore_engine(original_src)
        importlib.reload(importlib.import_module('siqs_engine'))
        print("\n[Source restored to original]")

    # --- COMPARISON ---
    print("\n" + "=" * 70)
    print("COMPARISON")
    print("=" * 70)

    print(f"\n{'Digits':>6} {'Seed':>6} {'Baseline':>10} {'Grouped':>10} {'Speedup':>10} {'Result':>8}")
    print("-" * 60)

    by_digits = {}
    total_baseline_time = 0
    total_grouped_time = 0

    for nd, n, seed in tests:
        key = (nd, seed)
        bt = baseline_results[key]['time']
        gt = grouped_results[key]['time']
        total_baseline_time += bt
        total_grouped_time += gt
        speedup = bt / gt if gt > 0 else float('inf')
        b_ok = baseline_results[key]['success']
        g_ok = grouped_results[key]['success']
        result_str = "OK" if (b_ok and g_ok) else "FAIL"
        print(f"{nd:>6} {seed:>6} {bt:>10.1f}s {gt:>10.1f}s {speedup:>9.2f}x {result_str:>8}")

        if nd not in by_digits:
            by_digits[nd] = {'baseline': [], 'grouped': []}
        by_digits[nd]['baseline'].append(bt)
        by_digits[nd]['grouped'].append(gt)

    print(f"\n{'Digits':>6} {'Avg Baseline':>12} {'Avg Grouped':>12} {'Avg Speedup':>12}")
    print("-" * 50)

    any_improved = False
    any_regressed = False
    for nd in sorted(by_digits.keys()):
        avg_b = sum(by_digits[nd]['baseline']) / len(by_digits[nd]['baseline'])
        avg_g = sum(by_digits[nd]['grouped']) / len(by_digits[nd]['grouped'])
        speedup = avg_b / avg_g if avg_g > 0 else float('inf')
        if speedup > 1.10:
            marker = " <-- IMPROVED"
            any_improved = True
        elif speedup < 0.90:
            marker = " <-- REGRESSED"
            any_regressed = True
        else:
            marker = ""
        print(f"{nd:>6} {avg_b:>12.1f}s {avg_g:>12.1f}s {speedup:>11.2f}x{marker}")

    total_speedup = total_baseline_time / total_grouped_time if total_grouped_time > 0 else float('inf')
    print(f"\n  Overall: {total_baseline_time:.1f}s -> {total_grouped_time:.1f}s ({total_speedup:.2f}x)")

    if any_improved and not any_regressed and total_speedup > 1.10:
        print("\n  VERDICT: Grouped a-selection shows >10% improvement.")
        print("  Recommendation: Enable in siqs_engine.py")
    elif any_regressed:
        print("\n  VERDICT: Grouped a-selection shows REGRESSION at some digit sizes.")
        print("  Recommendation: Keep disabled (current behavior)")
    else:
        print("\n  VERDICT: Grouped a-selection does NOT show consistent >10% improvement.")
        print("  Recommendation: Keep disabled (current behavior)")

    return any_improved and not any_regressed and total_speedup > 1.10


if __name__ == '__main__':
    improved = main()
    sys.exit(0 if improved else 1)

#!/usr/bin/env python3
"""
Resonance Sieve Benchmark Suite
=================================
Standardized benchmark for factoring engines.

- Deterministic test generation (random.seed(42))
- Balanced semiprimes at 66, 100, 110, 130, 150, 165, 180, 190 bits
- Configurable per-test time limit (default 300s)
- Optional cProfile profiling of a specified bit-length
- Clean results table + saved to benchmarks/LATEST_RESULTS.md
"""

import gmpy2
from gmpy2 import mpz, next_prime
import random
import time
import os
import sys
import argparse
import cProfile
import pstats
import io
from datetime import datetime

# ---------------------------------------------------------------------------
# Import factoring engine: prefer v7, fall back to v5
# ---------------------------------------------------------------------------
_engine_name = None
_factor_fn = None

try:
    from resonance_v7 import factor as _factor_v7
    _factor_fn = _factor_v7
    _engine_name = "Resonance Sieve v7.0"
except ImportError:
    try:
        from resonance_v5 import factor as _factor_v5
        _factor_fn = _factor_v5
        _engine_name = "Resonance Sieve v5.0"
    except ImportError:
        print("ERROR: Could not import resonance_v7 or resonance_v5.")
        print("       Make sure one of these files is in the Python path.")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Test generation
# ---------------------------------------------------------------------------

# Bit-lengths for balanced semiprimes
DEFAULT_BIT_LENGTHS = [66, 100, 110, 130, 150, 165, 180, 190]

def generate_tests(bit_lengths=None, seed=42):
    """
    Generate balanced semiprimes at the given bit-lengths.

    Each semiprime n = p * q where p and q are primes of approximately
    half the target bit-length. Uses a seeded RNG for reproducibility.
    """
    if bit_lengths is None:
        bit_lengths = DEFAULT_BIT_LENGTHS

    rng = random.Random(seed)
    tests = []

    for bits in bit_lengths:
        half = bits // 2
        # Generate two random primes of ~half bits (high bit set to ensure size)
        p_candidate = rng.getrandbits(half) | (1 << (half - 1)) | 1
        q_candidate = rng.getrandbits(half) | (1 << (half - 1)) | 1
        p = int(next_prime(mpz(p_candidate)))
        q = int(next_prime(mpz(q_candidate)))
        # Ensure p != q
        while q == p:
            q_candidate = rng.getrandbits(half) | (1 << (half - 1)) | 1
            q = int(next_prime(mpz(q_candidate)))
        n = p * q
        nd = len(str(n))
        nb = int(gmpy2.log2(mpz(n))) + 1
        tests.append({
            "bits_target": bits,
            "bits_actual": nb,
            "digits": nd,
            "n": n,
            "p": min(p, q),
            "q": max(p, q),
        })

    return tests


# ---------------------------------------------------------------------------
# Benchmark runner
# ---------------------------------------------------------------------------

def run_benchmark(tests, time_limit=300, verbose_tests=True):
    """
    Run the factoring engine on each test case.

    Returns a list of result dicts with keys:
      bits_target, bits_actual, digits, n, p, q, factor_found, correct, elapsed, status
    """
    results = []

    for i, test in enumerate(tests):
        bits = test["bits_target"]
        nb = test["bits_actual"]
        nd = test["digits"]
        n = test["n"]
        expected_p = test["p"]
        expected_q = test["q"]

        print(f"\n{'='*72}")
        print(f"[{i+1}/{len(tests)}] {nd}d ({nb}b, target {bits}b)")
        print(f"{'='*72}")

        t0 = time.time()
        try:
            f = _factor_fn(n, verbose=verbose_tests, time_limit=time_limit)
        except Exception as e:
            f = None
            print(f"  ERROR: {e}")

        elapsed = time.time() - t0

        if f is not None and f != n and f > 1 and n % f == 0:
            other = n // f
            correct = ({min(f, other), max(f, other)} == {expected_p, expected_q})
            status = "PASS" if correct else "PASS*"
            print(f"  {status}: {f} x {n // f} ({elapsed:.2f}s)")
        elif f is None:
            correct = False
            status = "FAIL"
            print(f"  FAIL: no factor found ({elapsed:.2f}s)")
        else:
            correct = False
            status = "FAIL"
            print(f"  FAIL: trivial result ({elapsed:.2f}s)")

        results.append({
            "bits_target": bits,
            "bits_actual": nb,
            "digits": nd,
            "n": n,
            "p": expected_p,
            "q": expected_q,
            "factor_found": f,
            "correct": correct,
            "elapsed": elapsed,
            "status": status,
        })

    return results


# ---------------------------------------------------------------------------
# Profiling
# ---------------------------------------------------------------------------

def profile_test(test, time_limit=300):
    """
    Run cProfile on a single test case and print the top functions by
    cumulative time.
    """
    bits = test["bits_target"]
    nb = test["bits_actual"]
    nd = test["digits"]
    n = test["n"]

    print(f"\n{'='*72}")
    print(f"PROFILING: {nd}d ({nb}b, target {bits}b)")
    print(f"{'='*72}")

    pr = cProfile.Profile()
    pr.enable()

    t0 = time.time()
    try:
        f = _factor_fn(n, verbose=False, time_limit=time_limit)
    except Exception as e:
        f = None
        print(f"  ERROR during profiling: {e}")

    elapsed = time.time() - t0
    pr.disable()

    if f and f != n and f > 1 and n % f == 0:
        print(f"  Factored: {f} x {n // f} ({elapsed:.2f}s)")
    else:
        print(f"  No factor ({elapsed:.2f}s)")

    # Print stats
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
    ps.print_stats(30)
    print(s.getvalue())

    return elapsed


# ---------------------------------------------------------------------------
# Results table and saving
# ---------------------------------------------------------------------------

def print_results_table(results):
    """Print a clean ASCII results table."""
    print(f"\n{'='*72}")
    print(f"BENCHMARK RESULTS  --  {_engine_name}")
    print(f"{'='*72}")
    header = f"{'Bits':>6s}  {'Digits':>6s}  {'Status':>6s}  {'Time':>10s}"
    print(header)
    print("-" * len(header))

    for r in results:
        time_str = f"{r['elapsed']:.2f}s" if r["elapsed"] < 1000 else f"{r['elapsed']:.0f}s"
        print(f"{r['bits_target']:>6d}  {r['digits']:>6d}  {r['status']:>6s}  {time_str:>10s}")

    passes = sum(1 for r in results if r["status"].startswith("PASS"))
    total = len(results)
    print(f"\n  {passes}/{total} passed")


def save_results(results, output_path):
    """Save results to a Markdown file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    lines = []
    lines.append(f"# Benchmark Results: {_engine_name}")
    lines.append(f"")
    lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"")
    lines.append(f"| Bits | Digits | Status | Time |")
    lines.append(f"|-----:|-------:|-------:|-----:|")

    for r in results:
        time_str = f"{r['elapsed']:.2f}s" if r["elapsed"] < 1000 else f"{r['elapsed']:.0f}s"
        lines.append(f"| {r['bits_target']} | {r['digits']} | {r['status']} | {time_str} |")

    passes = sum(1 for r in results if r["status"].startswith("PASS"))
    total = len(results)
    lines.append(f"")
    lines.append(f"**{passes}/{total} passed**")
    lines.append(f"")

    with open(output_path, "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"\nResults saved to {output_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Resonance Sieve Benchmark Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--time-limit", type=int, default=300,
        help="Time limit per test in seconds (default: 300)",
    )
    parser.add_argument(
        "--bits", type=str, default=None,
        help="Comma-separated bit-lengths to test (default: 66,100,110,130,150,165,180,190)",
    )
    parser.add_argument(
        "--profile", type=int, default=None, nargs="?", const=165,
        help="Profile a specific bit-length test (default: 165 if flag given)",
    )
    parser.add_argument(
        "--output", type=str,
        default="/home/raver1975/factor/benchmarks/LATEST_RESULTS.md",
        help="Path to save results markdown",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for test generation (default: 42)",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Suppress per-test verbose output from the factoring engine",
    )

    args = parser.parse_args()

    # Parse bit-lengths
    if args.bits:
        bit_lengths = [int(b.strip()) for b in args.bits.split(",")]
    else:
        bit_lengths = DEFAULT_BIT_LENGTHS

    print(f"{'='*72}")
    print(f"RESONANCE SIEVE BENCHMARK SUITE")
    print(f"Engine: {_engine_name}")
    print(f"Bit-lengths: {bit_lengths}")
    print(f"Time limit: {args.time_limit}s per test")
    print(f"Seed: {args.seed}")
    print(f"{'='*72}")

    # Generate tests
    tests = generate_tests(bit_lengths=bit_lengths, seed=args.seed)

    print(f"\nGenerated {len(tests)} test cases:")
    for t in tests:
        print(f"  {t['bits_target']:>4d}b -> {t['digits']}d ({t['bits_actual']}b actual)")

    # Run profiling if requested
    if args.profile is not None:
        profile_bits = args.profile
        profile_test_case = None
        for t in tests:
            if t["bits_target"] == profile_bits:
                profile_test_case = t
                break
        if profile_test_case is None:
            # Generate the profiling test on-the-fly if not in the main list
            profile_tests = generate_tests(bit_lengths=[profile_bits], seed=args.seed)
            profile_test_case = profile_tests[0]
        profile_test(profile_test_case, time_limit=args.time_limit)

    # Run benchmark
    results = run_benchmark(tests, time_limit=args.time_limit, verbose_tests=not args.quiet)

    # Print and save
    print_results_table(results)
    save_results(results, args.output)


if __name__ == "__main__":
    main()

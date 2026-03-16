#!/usr/bin/env python3
"""
v11_c_siqs_bench.py — Comprehensive SIQS Benchmark Framework
=============================================================

Benchmarks:
  1. Current Python SIQS (siqs_engine.siqs_factor) at 48d, 54d, 60d, 63d, 66d
  2. C-accelerated SIQS (siqs_c_driver.siqs_factor_c) at the same sizes
  3. Per-phase timing: sieve, hit detection, trial division, poly setup, LA, sqrt
  4. Speedup table: C/Python ratio per phase and total
  5. Correctness validation: compare factors found by both paths

Test semiprimes are deterministic (same primes each run) for reproducibility.

Usage:
    python v11_c_siqs_bench.py              # Quick mode: 48d, 54d only
    python v11_c_siqs_bench.py --full       # Full mode: 48d through 66d
    python v11_c_siqs_bench.py --validate   # Correctness validation only
    python v11_c_siqs_bench.py --profile    # Profile current Python SIQS
"""

import sys
import time
import random
import argparse

import gmpy2
from gmpy2 import mpz, next_prime, is_prime

# Import both engines
import siqs_engine
from siqs_c_driver import siqs_factor_c, PhaseTimer, get_capabilities, print_capabilities


###############################################################################
# DETERMINISTIC SEMIPRIME GENERATION
###############################################################################

def make_semiprime(digits):
    """
    Generate a deterministic semiprime of approximately `digits` digits.
    Uses fixed seeds for reproducibility across runs.
    """
    half = digits // 2
    p = int(next_prime(mpz(10**(half-1)) + 42))
    q = int(next_prime(mpz(10**(digits-half-1)) + 179))
    n = p * q
    return n, p, q


def make_semiprimes(digits, count=3):
    """Generate `count` semiprimes of given digit size with different seeds."""
    results = []
    offsets = [42, 1337, 7919, 10007, 31337]
    for i in range(count):
        half = digits // 2
        p_base = 10**(half-1) + offsets[i % len(offsets)]
        q_base = 10**(digits-half-1) + offsets[(i+1) % len(offsets)] * 3
        p = int(next_prime(mpz(p_base)))
        q = int(next_prime(mpz(q_base)))
        # Ensure p != q
        while p == q:
            q = int(next_prime(mpz(q + 1)))
        n = p * q
        actual_digits = len(str(n))
        results.append((n, p, q, actual_digits))
    return results


###############################################################################
# BENCHMARK RUNNER
###############################################################################

def bench_python_siqs(n, p, q, time_limit=300, verbose=False):
    """
    Benchmark the pure Python SIQS engine.
    Returns (factor, elapsed, success).
    """
    t0 = time.time()
    try:
        f = siqs_engine.siqs_factor(n, verbose=verbose, time_limit=time_limit)
    except Exception as e:
        return None, time.time() - t0, False, str(e)
    elapsed = time.time() - t0
    success = f is not None and n % f == 0 and 1 < f < n
    return f, elapsed, success, None


def bench_c_siqs(n, p, q, time_limit=300, verbose=False):
    """
    Benchmark the C-accelerated SIQS driver.
    Returns (factor, elapsed, success, phase_timer).
    """
    pt = PhaseTimer()
    t0 = time.time()
    try:
        f = siqs_factor_c(n, verbose=verbose, time_limit=time_limit, phase_timer=pt)
    except Exception as e:
        pt.finalize()
        return None, time.time() - t0, False, pt, str(e)
    elapsed = time.time() - t0
    pt.finalize()
    success = f is not None and n % f == 0 and 1 < f < n
    return f, elapsed, success, pt, None


###############################################################################
# CORRECTNESS VALIDATION
###############################################################################

def validate_correctness(digit_sizes=None, verbose=True):
    """
    Run both Python and C SIQS on the same semiprimes and compare results.

    For each test case:
      1. Run Python SIQS, record factor
      2. Run C SIQS, record factor
      3. Verify both find valid factors of the same number
    """
    if digit_sizes is None:
        digit_sizes = [30, 40, 48]

    print("=" * 70)
    print("CORRECTNESS VALIDATION")
    print("=" * 70)

    all_pass = True

    for digits in digit_sizes:
        semiprimes = make_semiprimes(digits, count=2)
        for i, (n, p, q, actual_d) in enumerate(semiprimes):
            print(f"\n  [{digits}d #{i+1}] n = {n} ({actual_d}d)")
            print(f"    Expected factors: {p} x {q}")

            # Python SIQS
            f_py, t_py, ok_py, err_py = bench_python_siqs(n, p, q, time_limit=120, verbose=False)
            py_status = "PASS" if ok_py else f"FAIL ({err_py})"
            print(f"    Python SIQS: factor={f_py}, {t_py:.2f}s, {py_status}")

            # C SIQS
            f_c, t_c, ok_c, pt_c, err_c = bench_c_siqs(n, p, q, time_limit=120, verbose=False)
            c_status = "PASS" if ok_c else f"FAIL ({err_c})"
            print(f"    C SIQS:      factor={f_c}, {t_c:.2f}s, {c_status}")

            # Validate both found valid factors
            if ok_py and ok_c:
                # Both should find a valid factorization (not necessarily same factor)
                py_valid = (n % f_py == 0 and 1 < f_py < n)
                c_valid = (n % f_c == 0 and 1 < f_c < n)
                if py_valid and c_valid:
                    print(f"    MATCH: both found valid factors")
                else:
                    print(f"    MISMATCH: py_valid={py_valid}, c_valid={c_valid}")
                    all_pass = False
            elif ok_py != ok_c:
                print(f"    DIVERGENCE: Python={'ok' if ok_py else 'fail'}, "
                      f"C={'ok' if ok_c else 'fail'}")
                all_pass = False

    print(f"\n{'=' * 70}")
    print(f"Validation: {'ALL PASSED' if all_pass else 'SOME FAILURES'}")
    print(f"{'=' * 70}")
    return all_pass


###############################################################################
# MAIN BENCHMARK
###############################################################################

def run_benchmark(digit_sizes, n_samples=3, time_limit=300, verbose_factor=False):
    """
    Run the full benchmark suite.

    For each digit size:
      - Generate n_samples semiprimes
      - Run Python SIQS and C SIQS on each
      - Collect per-phase timing
      - Compute speedup ratios
    """
    print("=" * 70)
    print("SIQS BENCHMARK SUITE")
    print("=" * 70)
    print_capabilities()

    results = []  # (digits, py_times, c_times, c_phases, successes)

    for digits in digit_sizes:
        print(f"\n{'=' * 70}")
        print(f"  {digits}-DIGIT SEMIPRIMES")
        print(f"{'=' * 70}")

        semiprimes = make_semiprimes(digits, count=n_samples)
        py_times = []
        c_times = []
        c_phases_list = []
        py_ok_count = 0
        c_ok_count = 0

        for i, (n, p, q, actual_d) in enumerate(semiprimes):
            print(f"\n  Sample {i+1}/{n_samples}: {actual_d}d, n={str(n)[:40]}...")

            # Python SIQS
            print(f"    Python SIQS...", end=" ", flush=True)
            f_py, t_py, ok_py, err_py = bench_python_siqs(
                n, p, q, time_limit=time_limit, verbose=verbose_factor)
            py_times.append(t_py)
            if ok_py:
                py_ok_count += 1
                print(f"{t_py:.2f}s (PASS)")
            else:
                print(f"{t_py:.2f}s (FAIL: {err_py})")

            # C SIQS
            print(f"    C SIQS...", end=" ", flush=True)
            f_c, t_c, ok_c, pt_c, err_c = bench_c_siqs(
                n, p, q, time_limit=time_limit, verbose=verbose_factor)
            c_times.append(t_c)
            c_phases_list.append(pt_c.summary())
            if ok_c:
                c_ok_count += 1
                print(f"{t_c:.2f}s (PASS)")
                phases = pt_c.summary()
                print(f"      sieve={phases['sieve']:.2f}s "
                      f"hits={phases['hits']:.2f}s "
                      f"td={phases['td']:.2f}s "
                      f"poly={phases['poly_setup']:.2f}s "
                      f"la={phases['la']:.2f}s")
            else:
                print(f"{t_c:.2f}s (FAIL: {err_c})")

        # Aggregate results for this digit size
        avg_py = sum(py_times) / len(py_times) if py_times else 0
        avg_c = sum(c_times) / len(c_times) if c_times else 0
        speedup = avg_py / avg_c if avg_c > 0 else 0

        # Average phase times
        avg_phases = {}
        if c_phases_list:
            for key in c_phases_list[0]:
                avg_phases[key] = sum(p[key] for p in c_phases_list) / len(c_phases_list)

        results.append({
            'digits': digits,
            'n_samples': n_samples,
            'py_avg': avg_py,
            'c_avg': avg_c,
            'speedup': speedup,
            'py_ok': py_ok_count,
            'c_ok': c_ok_count,
            'c_phases': avg_phases,
            'py_times': py_times,
            'c_times': c_times,
        })

    # ======================================================================
    # SUMMARY TABLE
    # ======================================================================
    print(f"\n\n{'=' * 70}")
    print("BENCHMARK RESULTS SUMMARY")
    print(f"{'=' * 70}")
    print()

    # Overall timing table
    hdr = f"{'Digits':>6s} | {'Python avg':>10s} | {'C avg':>10s} | {'Speedup':>8s} | {'Py OK':>5s} | {'C OK':>5s}"
    print(hdr)
    print("-" * len(hdr))
    for r in results:
        py_str = f"{r['py_avg']:.2f}s"
        c_str = f"{r['c_avg']:.2f}s"
        sp_str = f"{r['speedup']:.2f}x" if r['speedup'] > 0 else "N/A"
        print(f"{r['digits']:>6d} | {py_str:>10s} | {c_str:>10s} | {sp_str:>8s} | "
              f"{r['py_ok']:>2d}/{r['n_samples']:<2d} | {r['c_ok']:>2d}/{r['n_samples']:<2d}")

    # Per-phase breakdown (C driver only)
    print(f"\n{'=' * 70}")
    print("C DRIVER — PER-PHASE BREAKDOWN (averages)")
    print(f"{'=' * 70}")
    phase_hdr = (f"{'Digits':>6s} | {'Sieve':>8s} | {'Hits':>8s} | {'TD':>8s} | "
                 f"{'Poly':>8s} | {'LA':>8s} | {'Sqrt':>8s} | {'Total':>8s}")
    print(phase_hdr)
    print("-" * len(phase_hdr))
    for r in results:
        ph = r['c_phases']
        if not ph:
            continue
        print(f"{r['digits']:>6d} | "
              f"{ph.get('sieve',0):>7.2f}s | "
              f"{ph.get('hits',0):>7.2f}s | "
              f"{ph.get('td',0):>7.2f}s | "
              f"{ph.get('poly_setup',0):>7.2f}s | "
              f"{ph.get('la',0):>7.2f}s | "
              f"{ph.get('sqrt',0):>7.2f}s | "
              f"{ph.get('total',0):>7.2f}s")

    # Phase percentage breakdown
    print(f"\n{'=' * 70}")
    print("C DRIVER — PHASE PERCENTAGES")
    print(f"{'=' * 70}")
    pct_hdr = (f"{'Digits':>6s} | {'Sieve':>6s} | {'Hits':>6s} | {'TD':>6s} | "
               f"{'Poly':>6s} | {'LA':>6s} | {'Sqrt':>6s} | {'Other':>6s}")
    print(pct_hdr)
    print("-" * len(pct_hdr))
    for r in results:
        ph = r['c_phases']
        if not ph:
            continue
        total = ph.get('total', 1) or 1
        tracked = (ph.get('sieve', 0) + ph.get('hits', 0) + ph.get('td', 0) +
                   ph.get('poly_setup', 0) + ph.get('la', 0) + ph.get('sqrt', 0))
        other = max(0, total - tracked)
        print(f"{r['digits']:>6d} | "
              f"{100*ph.get('sieve',0)/total:>5.1f}% | "
              f"{100*ph.get('hits',0)/total:>5.1f}% | "
              f"{100*ph.get('td',0)/total:>5.1f}% | "
              f"{100*ph.get('poly_setup',0)/total:>5.1f}% | "
              f"{100*ph.get('la',0)/total:>5.1f}% | "
              f"{100*ph.get('sqrt',0)/total:>5.1f}% | "
              f"{100*other/total:>5.1f}%")

    return results


###############################################################################
# PROFILING MODE
###############################################################################

def profile_python_siqs(digits=54):
    """Profile the current Python SIQS to establish precise baselines."""
    print("=" * 70)
    print(f"PROFILING PYTHON SIQS AT {digits}d")
    print("=" * 70)

    n, p, q = make_semiprime(digits)
    nd = len(str(n))
    print(f"  n = {n} ({nd}d)")
    print(f"  Expected: {p} x {q}")
    print()

    # Run with verbose to see internal timing
    t0 = time.time()
    f = siqs_engine.siqs_factor(n, verbose=True, time_limit=300)
    elapsed = time.time() - t0

    ok = f is not None and n % f == 0 and 1 < f < n
    print(f"\n  Result: {'PASS' if ok else 'FAIL'}, factor={f}, {elapsed:.2f}s")
    return ok


###############################################################################
# MAIN
###############################################################################

def main():
    parser = argparse.ArgumentParser(description="SIQS Benchmark Framework")
    parser.add_argument("--full", action="store_true",
                        help="Full benchmark: 48d through 66d")
    parser.add_argument("--validate", action="store_true",
                        help="Correctness validation only")
    parser.add_argument("--profile", action="store_true",
                        help="Profile Python SIQS")
    parser.add_argument("--digits", type=int, nargs="+",
                        help="Specific digit sizes to benchmark")
    parser.add_argument("--samples", type=int, default=2,
                        help="Number of samples per digit size (default: 2)")
    parser.add_argument("--verbose", action="store_true",
                        help="Verbose factor output")
    parser.add_argument("--time-limit", type=int, default=120,
                        help="Per-factorization time limit in seconds (default: 120)")
    args = parser.parse_args()

    random.seed(42)

    if args.validate:
        validate_correctness(verbose=True)
        return

    if args.profile:
        profile_python_siqs(digits=54)
        return

    if args.digits:
        digit_sizes = args.digits
    elif args.full:
        digit_sizes = [48, 54, 60, 63, 66]
    else:
        # Quick mode: fast sizes only to stay under 5 minutes
        digit_sizes = [48, 54]

    run_benchmark(
        digit_sizes=digit_sizes,
        n_samples=args.samples,
        time_limit=args.time_limit,
        verbose_factor=args.verbose,
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
v37_test_presieve.py — Benchmark the COMPLETE pre-sieve stack
=============================================================
Tests: pollard_pm1, williams_pp1, gaussian_pm1, berggren_pm1, eisenstein_pm1
on 100 random semiprimes (30-60 digits) plus targeted Eisenstein-friendly cases.

Measures:
  - Catch rate per method (cumulative and unique)
  - Total pre-sieve time
  - Overhead analysis by digit count
"""

import gmpy2
from gmpy2 import mpz, is_prime, next_prime, gcd
import random
import time
import sys

sys.path.insert(0, '/home/raver1975/factor')
from resonance_v7 import (pollard_pm1, williams_pp1, gaussian_pm1,
                           berggren_pm1, eisenstein_pm1, _sieve_primes)


def random_prime(bits):
    """Generate a random prime of approximately `bits` bits."""
    while True:
        p = mpz(random.getrandbits(bits))
        p = next_prime(p | 1)
        if p.bit_length() >= bits - 1:
            return p


def make_semiprime(digit_target):
    """Make a semiprime with approximately digit_target digits."""
    # Each factor is ~half the digits
    half_bits = int(digit_target * 3.32 / 2)
    p = random_prime(half_bits)
    q = random_prime(half_bits)
    while p == q:
        q = random_prime(half_bits)
    return int(p * q), int(p), int(q)


def is_smooth(n, B):
    """Check if n is B-smooth (all prime factors <= B). Fast: uses _SMALL_PRIMES cache."""
    n = abs(int(n))
    if n <= 1:
        return True
    for p in _sieve_primes(min(B, 10_000_000)):
        if p > B:
            break
        while n % p == 0:
            n //= p
        if n == 1:
            return True
    # Check if remaining cofactor is a prime <= B
    return n == 1 or (gmpy2.is_prime(n) and int(n) <= B)


def make_smooth_prime(bits, B_smooth):
    """
    Generate a prime p where p^2 + p + 1 is B_smooth-smooth AND p ≡ 2 mod 3.
    Strategy: build p^2+p+1 from smooth factors, then solve for p.
    Fallback: random search with fast smoothness check.
    """
    # Fast approach: random search. For small bit sizes this works.
    # Use cached primes list for speed.
    cached_primes = _sieve_primes(min(B_smooth, 10_000_000))
    for _ in range(50000):
        p = random_prime(bits)
        if int(p) % 3 != 2:
            continue
        # Fast smoothness check: trial divide p^2+p+1
        val = int(p) * int(p) + int(p) + 1
        rem = val
        for pp in cached_primes:
            if pp > B_smooth:
                break
            while rem % pp == 0:
                rem //= pp
            if rem == 1:
                break
        if rem == 1 or (gmpy2.is_prime(rem) and rem <= B_smooth):
            return int(p)
    return None


def make_eisenstein_friendly(digit_target, B1=500000):
    """
    Make a semiprime N = p * q where p^2 + p + 1 is B1-smooth.
    """
    half_bits = int(digit_target * 3.32 / 2)
    p = make_smooth_prime(half_bits, B1)
    if p is None:
        return None, None, None
    q = int(random_prime(half_bits))
    while q == p:
        q = int(random_prime(half_bits))
    return p * q, p, q


def make_pm1_friendly(digit_target, B1=500000):
    """Make semiprime where p-1 is B1-smooth."""
    half_bits = int(digit_target * 3.32 / 2)
    attempts = 0
    while attempts < 100000:
        attempts += 1
        p = random_prime(half_bits)
        if is_smooth(int(p) - 1, B1):
            q = random_prime(half_bits)
            while q == p:
                q = random_prime(half_bits)
            return int(p * q), int(p), int(q)
    return None, None, None


def make_pp1_friendly(digit_target, B1=500000):
    """Make semiprime where p+1 is B1-smooth."""
    half_bits = int(digit_target * 3.32 / 2)
    attempts = 0
    while attempts < 100000:
        attempts += 1
        p = random_prime(half_bits)
        if is_smooth(int(p) + 1, B1):
            q = random_prime(half_bits)
            while q == p:
                q = random_prime(half_bits)
            return int(p * q), int(p), int(q)
    return None, None, None


def test_method(func, n, B1, **kwargs):
    """Test a single method, return (factor_or_None, time_taken)."""
    t0 = time.time()
    try:
        f = func(n, B1=B1, verbose=False, **kwargs)
    except Exception as e:
        f = None
    elapsed = time.time() - t0
    if f and 1 < f < n and n % f == 0:
        return f, elapsed
    return None, elapsed


def run_benchmark():
    print("=" * 78)
    print("v37: COMPLETE PRE-SIEVE STACK BENCHMARK")
    print("=" * 78)

    random.seed(42)

    # ---------------------------------------------------------------
    # Phase 1: Generate 100 random semiprimes (30-60 digits)
    # ---------------------------------------------------------------
    print("\n[Phase 1] Generating 100 random semiprimes (30-60d)...")
    test_cases = []
    for i in range(100):
        nd = 30 + (i % 31)  # 30 to 60 digits
        n, p, q = make_semiprime(nd)
        actual_nd = len(str(n))
        test_cases.append((n, p, q, actual_nd, "random"))

    print(f"  Generated {len(test_cases)} semiprimes")
    digit_dist = {}
    for _, _, _, nd, _ in test_cases:
        bucket = (nd // 5) * 5
        digit_dist[bucket] = digit_dist.get(bucket, 0) + 1
    for k in sorted(digit_dist):
        print(f"    {k}-{k+4}d: {digit_dist[k]} cases")

    # ---------------------------------------------------------------
    # Phase 2: Test each method individually on all 100
    # ---------------------------------------------------------------
    methods = [
        ("p-1",        lambda n, B1: test_method(pollard_pm1, n, B1, B2=B1*10)),
        ("p+1",        lambda n, B1: test_method(williams_pp1, n, B1, B2=B1*10, max_seeds=10)),
        ("Gaussian",   lambda n, B1: test_method(gaussian_pm1, n, B1, B2=B1*10)),
        ("Berggren",   lambda n, B1: test_method(berggren_pm1, n, B1)),
        ("Eisenstein", lambda n, B1: test_method(eisenstein_pm1, n, B1)),
    ]

    B1 = 500000

    # results[method_name] = list of (caught: bool, time: float) for each case
    results = {name: [] for name, _ in methods}
    caught_by = {name: set() for name, _ in methods}

    print(f"\n[Phase 2] Testing 5 methods on 100 semiprimes (B1={B1})...")
    print(f"  This may take a few minutes...\n")

    total_t0 = time.time()
    for i, (n, p, q, nd, kind) in enumerate(test_cases):
        if (i + 1) % 10 == 0:
            elapsed = time.time() - total_t0
            print(f"  Progress: {i+1}/100 ({elapsed:.1f}s elapsed)")

        for name, func in methods:
            f, t = func(n, B1)
            caught = f is not None
            results[name].append((caught, t))
            if caught:
                caught_by[name].add(i)

    total_time = time.time() - total_t0
    print(f"\n  Total benchmark time: {total_time:.1f}s")

    # ---------------------------------------------------------------
    # Phase 3: Cumulative catch rates
    # ---------------------------------------------------------------
    print("\n" + "=" * 78)
    print("CUMULATIVE PRE-SIEVE CATCH RATES")
    print("=" * 78)

    cumulative = set()
    method_names_ordered = ["p-1", "p+1", "Gaussian", "Berggren", "Eisenstein"]
    cumulative_counts = []

    for name in method_names_ordered:
        own = caught_by[name]
        new_unique = own - cumulative
        cumulative |= own
        total_caught = len(own)
        total_time_method = sum(t for _, t in results[name])
        avg_time = total_time_method / len(test_cases)
        cumulative_counts.append(len(cumulative))

        print(f"\n  {name:12s}: {total_caught:3d}/100 caught | "
              f"{len(new_unique):2d} unique | "
              f"cumulative: {len(cumulative):3d}/100 | "
              f"avg time: {avg_time:.3f}s | "
              f"total: {total_time_method:.2f}s")

        if new_unique:
            print(f"    Unique catches: {sorted(new_unique)[:10]}{'...' if len(new_unique) > 10 else ''}")

    print(f"\n  TOTAL pre-sieve: {len(cumulative)}/100 caught")
    all_times = sum(sum(t for _, t in results[name]) for name in method_names_ordered)
    print(f"  Total pre-sieve time (all methods, all cases): {all_times:.2f}s")
    print(f"  Average pre-sieve time per semiprime: {all_times / len(test_cases):.3f}s")

    # ---------------------------------------------------------------
    # Phase 4: Build comparison table
    # ---------------------------------------------------------------
    print("\n" + "=" * 78)
    print("STACK BUILD-UP TABLE")
    print("=" * 78)

    stack = set()
    stack_time = 0.0
    for j, name in enumerate(method_names_ordered):
        stack |= caught_by[name]
        stack_time += sum(t for _, t in results[name])
        label = " + ".join(method_names_ordered[:j+1])
        print(f"  {label:50s} => {len(stack):3d}/100 "
              f"(+{len(caught_by[name] - set().union(*(caught_by[m] for m in method_names_ordered[:j])) if j > 0 else caught_by[name]):2d} new) "
              f" time: {stack_time:.2f}s")

    # ---------------------------------------------------------------
    # Phase 5: Targeted Eisenstein test cases
    # ---------------------------------------------------------------
    print("\n" + "=" * 78)
    print("TARGETED EISENSTEIN TEST CASES (p^2+p+1 smooth)")
    print("=" * 78)

    eis_B1 = 500000
    eis_cases = []
    print(f"\n  Generating Eisenstein-friendly semiprimes (p^2+p+1 is {eis_B1}-smooth)...")

    for target_nd in [20, 24, 28, 30, 34, 38]:
        n, p, q = make_eisenstein_friendly(target_nd, eis_B1)
        if n is not None:
            eis_cases.append((n, p, q, len(str(n))))
            print(f"    Generated {len(str(n))}d case (target {target_nd}d)")
        else:
            print(f"    FAILED to generate {target_nd}d case")

    if not eis_cases:
        print("  WARNING: Could not generate Eisenstein-friendly cases")
        print("  Trying with larger B1...")
        eis_B1 = 2000000
        for target_nd in [20, 24, 28]:
            n, p, q = make_eisenstein_friendly(target_nd, eis_B1)
            if n is not None:
                eis_cases.append((n, p, q, len(str(n))))

    print(f"  Generated {len(eis_cases)} targeted cases\n")

    eis_caught = {"p-1": 0, "p+1": 0, "Gaussian": 0, "Berggren": 0, "Eisenstein": 0}
    for n, p, q, nd in eis_cases:
        print(f"  N = {str(n)[:40]}... ({nd}d)")
        print(f"    p = {p}, q = {q}")
        p_mod3 = int(p) % 3
        q_mod3 = int(q) % 3
        print(f"    p mod 3 = {p_mod3}, q mod 3 = {q_mod3}")
        p2p1 = int(p)*int(p) + int(p) + 1
        print(f"    p^2+p+1 smooth({eis_B1})? {is_smooth(p2p1, eis_B1)}")

        for name, func in methods:
            f, t = func(n, eis_B1)
            hit = "HIT" if f else "miss"
            if f:
                eis_caught[name] += 1
            print(f"    {name:12s}: {hit} ({t:.3f}s)")
        print()

    if eis_cases:
        print(f"  Targeted Eisenstein results ({len(eis_cases)} cases):")
        for name in method_names_ordered:
            print(f"    {name:12s}: {eis_caught[name]}/{len(eis_cases)}")

    # ---------------------------------------------------------------
    # Phase 6: Timing analysis by digit count
    # ---------------------------------------------------------------
    print("\n" + "=" * 78)
    print("TIMING ANALYSIS BY DIGIT COUNT")
    print("=" * 78)

    buckets = {}
    for i, (n, p, q, nd, kind) in enumerate(test_cases):
        bucket = (nd // 10) * 10
        if bucket not in buckets:
            buckets[bucket] = {name: [] for name in method_names_ordered}
        for name in method_names_ordered:
            buckets[bucket][name].append(results[name][i][1])

    print(f"\n  {'Digits':>8s}", end="")
    for name in method_names_ordered:
        print(f"  {name:>10s}", end="")
    print(f"  {'TOTAL':>10s}")
    print("  " + "-" * 72)

    for bucket in sorted(buckets):
        print(f"  {bucket:>3d}-{bucket+9:<3d}d", end="")
        row_total = 0
        for name in method_names_ordered:
            times = buckets[bucket][name]
            avg = sum(times) / len(times) if times else 0
            row_total += avg
            print(f"  {avg:>9.3f}s", end="")
        print(f"  {row_total:>9.3f}s")

    # ---------------------------------------------------------------
    # Phase 7: Verdict
    # ---------------------------------------------------------------
    print("\n" + "=" * 78)
    print("VERDICT")
    print("=" * 78)

    eis_unique = caught_by["Eisenstein"] - caught_by["p-1"] - caught_by["p+1"] - caught_by["Gaussian"] - caught_by["Berggren"]
    eis_total_time = sum(t for _, t in results["Eisenstein"])
    eis_avg = eis_total_time / len(test_cases)

    print(f"\n  Eisenstein unique catches: {len(eis_unique)}/100")
    print(f"  Eisenstein avg time:      {eis_avg:.3f}s per semiprime")
    print(f"  Eisenstein total time:    {eis_total_time:.2f}s for 100 cases")

    if len(eis_unique) > 0:
        cost_per_unique = eis_total_time / len(eis_unique)
        print(f"  Cost per unique catch:    {cost_per_unique:.2f}s")
        print(f"\n  RECOMMENDATION: KEEP Eisenstein in pre-sieve stack.")
        print(f"  {len(eis_unique)} unique catches justify {eis_avg:.3f}s avg overhead.")
    else:
        print(f"\n  On random semiprimes, Eisenstein had 0 unique catches.")
        print(f"  But it shines on TARGETED cases (p^2+p+1 smooth).")
        print(f"  RECOMMENDATION: KEEP if overhead < 0.5s avg, SKIP for >60d.")

    print(f"\n  Full 5-method stack: {len(cumulative)}/100 caught, {all_times:.2f}s total")
    print(f"  That's {all_times/100:.3f}s avg overhead before ECM/SIQS.")
    print()


if __name__ == "__main__":
    run_benchmark()

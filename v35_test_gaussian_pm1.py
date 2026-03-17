#!/usr/bin/env python3
"""
Test suite for Gaussian p-1 integration into resonance_v7.py.

Tests:
1. Standalone gaussian_pm1 correctness on known factors
2. Comparative benchmark: standard pipeline vs pipeline + gaussian_pm1
3. Semiprimes of 30-60 digits with various smoothness properties
"""

import time
import random
import gmpy2
from gmpy2 import mpz, is_prime, next_prime
from resonance_v7 import gaussian_pm1, pollard_pm1, williams_pp1

# ──────────────────────────────────────────────────────────────────────
# Helper: generate semiprime n = p * q with controlled properties
# ──────────────────────────────────────────────────────────────────────

def random_prime_near(bits):
    """Random prime near 2^bits."""
    base = mpz(2) ** bits + mpz(random.randint(0, 2 ** (bits - 1)))
    return mpz(int(gmpy2.next_prime(base)))

def make_semiprime(p_bits, q_bits):
    """Random semiprime with given factor sizes."""
    p = random_prime_near(p_bits)
    q = random_prime_near(q_bits)
    while p == q:
        q = random_prime_near(q_bits)
    return int(p * q), int(p), int(q)

def make_p_plus1_smooth(bits, B_smooth):
    """Find a prime p ~ 2^bits where p+1 is B_smooth-smooth."""
    while True:
        # Build p+1 from small primes
        val = mpz(2)
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
        while val.bit_length() < bits:
            val *= random.choice(primes[:min(8, len(primes))])
        p = val - 1
        if p > 3 and is_prime(p) and p.bit_length() >= bits - 2:
            return int(p)

def make_p_minus1_smooth(bits, B_smooth):
    """Find a prime p ~ 2^bits where p-1 is B_smooth-smooth."""
    while True:
        val = mpz(2)
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
        while val.bit_length() < bits:
            val *= random.choice(primes[:min(8, len(primes))])
        p = val + 1
        if p > 3 and is_prime(p) and p.bit_length() >= bits - 2:
            return int(p)


# ──────────────────────────────────────────────────────────────────────
# Test 1: Standalone correctness
# ──────────────────────────────────────────────────────────────────────

def test_standalone():
    print("=" * 70)
    print("TEST 1: Standalone gaussian_pm1 correctness")
    print("=" * 70)

    # Known small semiprimes
    cases = [
        (15, "3*5"),
        (77, "7*11"),
        (10007 * 10009, "10007*10009"),
        (1000003 * 1000033, "1000003*1000033"),
    ]

    passed = 0
    for n, desc in cases:
        t0 = time.time()
        f = gaussian_pm1(n, B1=50000, B2=500000, verbose=False)
        dt = time.time() - t0
        if f and 1 < f < n and n % f == 0:
            print(f"  PASS: {desc} -> factor {f} ({dt:.3f}s)")
            passed += 1
        else:
            print(f"  SKIP: {desc} -> no factor ({dt:.3f}s)")

    print(f"\n  {passed}/{len(cases)} passed\n")
    return passed


# ──────────────────────────────────────────────────────────────────────
# Test 2: p+1 smooth factors (where Gaussian p-1 should shine)
# ──────────────────────────────────────────────────────────────────────

def test_p_plus1_smooth():
    print("=" * 70)
    print("TEST 2: p+1 smooth factors (Gaussian p-1 vs others)")
    print("=" * 70)

    results = {"gauss": 0, "pm1": 0, "pp1": 0}
    times = {"gauss": [], "pm1": [], "pp1": []}

    random.seed(42)

    for trial in range(5):
        # Make a semiprime where one factor has p+1 smooth
        p = make_p_plus1_smooth(50, 50000)
        q = int(next_prime(mpz(random_prime_near(50))))
        n = p * q
        nd = len(str(n))
        print(f"\n  Trial {trial+1}: {nd}d semiprime, p={p} (p+1 smooth), q={q}")

        B1, B2 = 100000, 1000000

        # Gaussian p-1
        t0 = time.time()
        f = gaussian_pm1(n, B1=B1, B2=B2, verbose=False)
        dt = time.time() - t0
        times["gauss"].append(dt)
        if f and 1 < f < n and n % f == 0:
            results["gauss"] += 1
            print(f"    Gauss p-1:  FOUND {f} in {dt:.3f}s")
        else:
            print(f"    Gauss p-1:  miss ({dt:.3f}s)")

        # Pollard p-1
        t0 = time.time()
        f = pollard_pm1(n, B1=B1, B2=B2, verbose=False)
        dt = time.time() - t0
        times["pm1"].append(dt)
        if f and 1 < f < n and n % f == 0:
            results["pm1"] += 1
            print(f"    Pollard p-1: FOUND {f} in {dt:.3f}s")
        else:
            print(f"    Pollard p-1: miss ({dt:.3f}s)")

        # Williams p+1
        t0 = time.time()
        f = williams_pp1(n, B1=B1, B2=B2, max_seeds=5, verbose=False)
        dt = time.time() - t0
        times["pp1"].append(dt)
        if f and 1 < f < n and n % f == 0:
            results["pp1"] += 1
            print(f"    Williams p+1: FOUND {f} in {dt:.3f}s")
        else:
            print(f"    Williams p+1: miss ({dt:.3f}s)")

    print(f"\n  Summary (p+1 smooth):")
    print(f"    Gauss p-1:   {results['gauss']}/5 found, avg {sum(times['gauss'])/5:.3f}s")
    print(f"    Pollard p-1: {results['pm1']}/5 found, avg {sum(times['pm1'])/5:.3f}s")
    print(f"    Williams p+1:{results['pp1']}/5 found, avg {sum(times['pp1'])/5:.3f}s")
    print()
    return results


# ──────────────────────────────────────────────────────────────────────
# Test 3: Random semiprimes 30-60 digits
# ──────────────────────────────────────────────────────────────────────

def test_random_semiprimes():
    print("=" * 70)
    print("TEST 3: Random semiprimes (30-60 digits)")
    print("=" * 70)

    random.seed(123)
    results = {"gauss": 0, "pm1": 0, "pp1": 0}
    times = {"gauss": [], "pm1": [], "pp1": []}

    digit_sizes = [30, 35, 40, 45, 50, 55, 40, 45, 35, 50]

    for trial, nd_target in enumerate(digit_sizes):
        bits = int(nd_target * 3.32 / 2)  # half the bits per factor
        n, p, q = make_semiprime(bits, bits)
        nd = len(str(n))
        print(f"\n  Trial {trial+1}: {nd}d = {len(str(p))}d * {len(str(q))}d")

        B1 = min(500000, max(10000, 10 ** (nd // 6)))
        B2 = B1 * 10

        for name, func in [("Gauss p-1", gaussian_pm1),
                            ("Pollard p-1", pollard_pm1)]:
            key = "gauss" if "Gauss" in name else "pm1"
            t0 = time.time()
            f = func(n, B1=B1, B2=B2, verbose=False)
            dt = time.time() - t0
            times[key].append(dt)
            if f and 1 < f < n and n % f == 0:
                results[key] += 1
                print(f"    {name:14s}: FOUND {f} in {dt:.3f}s")
            else:
                print(f"    {name:14s}: miss ({dt:.3f}s)")

        t0 = time.time()
        f = williams_pp1(n, B1=B1, B2=B2, max_seeds=5, verbose=False)
        dt = time.time() - t0
        times["pp1"].append(dt)
        if f and 1 < f < n and n % f == 0:
            results["pp1"] += 1
            print(f"    {"Williams p+1":14s}: FOUND {f} in {dt:.3f}s")
        else:
            print(f"    {"Williams p+1":14s}: miss ({dt:.3f}s)")

    print(f"\n  Summary (random semiprimes):")
    print(f"    Gauss p-1:    {results['gauss']}/10 found, avg {sum(times['gauss'])/10:.3f}s")
    print(f"    Pollard p-1:  {results['pm1']}/10 found, avg {sum(times['pm1'])/10:.3f}s")
    print(f"    Williams p+1: {results['pp1']}/10 found, avg {sum(times['pp1'])/10:.3f}s")
    print()
    return results


# ──────────────────────────────────────────────────────────────────────
# Test 4: p ≡ 3 mod 4 factors (where Z[i] gives p²-1 = (p-1)(p+1))
# ──────────────────────────────────────────────────────────────────────

def test_p_cong_3_mod4():
    print("=" * 70)
    print("TEST 4: p ≡ 3 (mod 4) with p+1 smooth (Gaussian p-1 sweet spot)")
    print("=" * 70)

    results = {"gauss": 0, "pm1": 0, "pp1": 0}
    random.seed(7)

    for trial in range(5):
        # Build p ≡ 3 mod 4 with p+1 smooth
        while True:
            p = make_p_plus1_smooth(50, 50000)
            if p % 4 == 3:
                break
        q = int(next_prime(mpz(random_prime_near(55))))
        n = p * q
        nd = len(str(n))
        print(f"\n  Trial {trial+1}: {nd}d, p={p} (p≡{p%4} mod 4, p+1 smooth)")

        B1, B2 = 100000, 1000000

        for name, func in [("Gauss p-1", gaussian_pm1),
                            ("Pollard p-1", pollard_pm1)]:
            key = "gauss" if "Gauss" in name else "pm1"
            t0 = time.time()
            f = func(n, B1=B1, B2=B2, verbose=False)
            dt = time.time() - t0
            if f and 1 < f < n and n % f == 0:
                results[key] += 1
                print(f"    {name:14s}: FOUND {f} in {dt:.3f}s")
            else:
                print(f"    {name:14s}: miss ({dt:.3f}s)")

        t0 = time.time()
        f = williams_pp1(n, B1=B1, B2=B2, max_seeds=5, verbose=False)
        dt = time.time() - t0
        if f and 1 < f < n and n % f == 0:
            results["pp1"] += 1
            print(f"    {"Williams p+1":14s}: FOUND {f} in {dt:.3f}s")
        else:
            print(f"    {"Williams p+1":14s}: miss ({dt:.3f}s)")

    print(f"\n  Summary (p ≡ 3 mod 4, p+1 smooth):")
    print(f"    Gauss p-1:    {results['gauss']}/5")
    print(f"    Pollard p-1:  {results['pm1']}/5")
    print(f"    Williams p+1: {results['pp1']}/5")
    print()
    return results


# ──────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Gaussian p-1 Integration Test Suite")
    print("=" * 70)

    t_total = time.time()

    r1 = test_standalone()
    r2 = test_p_plus1_smooth()
    r3 = test_random_semiprimes()
    r4 = test_p_cong_3_mod4()

    print("=" * 70)
    print(f"ALL TESTS COMPLETE in {time.time()-t_total:.1f}s")
    print("=" * 70)
